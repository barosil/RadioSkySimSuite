"""
Módulo: tests/e2e/test_multi_source_workflow.py

Teste end-to-end do workflow multi-fonte (satélites + locais + rádio).

Valida as propriedades descritas no TODO.md:
1. Cada fonte tem tracks (theta, az, el, range) no referencial do observador
2. Cada fonte tem PSD em W/Hz
3. Theta_boresight calculado com pointing temporal (Skyfield)
4. Filtro N×FWHM descarta fontes fora do feixe
5. Resultado consolidado com dims (time, frequency, polarization, source, pointing)
6. Múltiplas antenas/beams
"""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from radioskysims_beam.domain.beam import Beam
from radioskysims_core.domain.common import Observer, TimeRange
from radioskysims_sources.domain.signal_source import (
    compute_theta_boresight,
)
from radioskysims_simulation.domain.simulation.simulation import Simulation
from radioskysims_simulation.domain.tod import TODSimulator

# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def time_grid() -> np.ndarray:
    """Grade temporal de 10 minutos, resolução 60s (endpoint inclusivo, igual a TimeRange)."""
    return np.arange(
        np.datetime64("2026-07-28T00:00:00"),
        np.datetime64("2026-07-28T00:10:01"),  # +1s inclui 00:10:00 → 11 pontos
        np.timedelta64(60, "s"),
        dtype="datetime64[ns]",
    )


@pytest.fixture
def observer() -> Observer:
    """Observador no equador, greenwich."""
    return Observer(
        lat=0.0,
        lon=0.0,
        height=0.0,
        timeframe=TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:10:00", resolution=60),
    )


@pytest.fixture
def beam_gaussian() -> Beam:
    """Beam gaussiano analítico (FWHM ~ 23.5°)."""
    theta = np.linspace(-90, 90, 181)
    amp = np.exp(-0.5 * (theta / 10) ** 2)
    amp_3d = amp[:, None, None]  # (angle, freq, pol)
    ds = xr.Dataset(
        {"amplitude": (("angle", "frequency", "polarization"), amp_3d)},
        coords={
            "angle": theta,
            "frequency": [1.0e9],
            "polarization": ["H"],
        },
    )
    return Beam(ds)


# ═══════════════════════════════════════════════════════════════════
# Mock SignalSources
# ═══════════════════════════════════════════════════════════════════


def _make_track(
    time_grid: np.ndarray,
    theta_mean_deg: float = 5.0,
    range_km: float = 20000.0,
) -> xr.Dataset:
    """Cria tracks mock com theta variando sinusoidalmente."""
    n = len(time_grid)
    t = np.linspace(0, 2 * np.pi, n)
    theta_rad = np.deg2rad(theta_mean_deg) * (1 + 0.1 * np.sin(t))
    return xr.Dataset(
        data_vars={
            "theta": ("time", theta_rad),
            "az": ("time", np.deg2rad(np.full(n, 45.0))),
            "el": ("time", np.pi / 2 - theta_rad),
            "range": ("time", np.full(n, range_km * 1e3, dtype=float)),
        },
        coords={"time": time_grid},
    )


class MockSatelliteSource:
    """Mock de SignalSource para satélite."""

    def __init__(self, name: str, time_grid: np.ndarray):
        self._name = name
        self._tracks = _make_track(time_grid, theta_mean_deg=2.0)

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_type(self) -> str:
        return "satellite"

    @property
    def tracks(self) -> xr.Dataset:
        return self._tracks

    def psd(self) -> xr.DataArray:
        freq = np.array([1.0e9], dtype=float)
        return xr.DataArray(
            np.ones_like(freq) * 1e-12,  # W/Hz
            dims="frequency",
            coords={"frequency": freq},
            attrs={"units": "W/Hz"},
        )


class MockLocalSource:
    """Mock de SignalSource para fonte local (Sol)."""

    def __init__(self, name: str, time_grid: np.ndarray):
        self._name = name
        self._tracks = _make_track(time_grid, theta_mean_deg=10.0, range_km=1.5e8)

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_type(self) -> str:
        return "localsource"

    @property
    def tracks(self) -> xr.Dataset:
        return self._tracks

    def psd(self) -> xr.DataArray:
        freq = np.array([1.0e9], dtype=float)
        # Fluxo solar típico ~ 10⁵ Jy → 10⁵ × 1e-26 = 1e-21 W/m²/Hz
        # Assume A_eff nominal → PSD ~ 1e-15 W/Hz
        return xr.DataArray(
            np.array([1e-15], dtype=float),
            dims="frequency",
            coords={"frequency": freq},
            attrs={"units": "W/Hz"},
        )


class MockRadioSource:
    """Mock de SignalSource para fonte de rádio (NVSS)."""

    def __init__(self, name: str, time_grid: np.ndarray):
        self._name = name
        # Fonte de rádio com RA/Dec nos tracks
        n = len(time_grid)
        self._tracks = xr.Dataset(
            data_vars={
                "ra": ("time", np.deg2rad(np.full(n, 180.0))),
                "dec": ("time", np.deg2rad(np.full(n, 0.0))),
                "theta": ("time", np.deg2rad(np.full(n, 15.0))),
                "az": ("time", np.deg2rad(np.full(n, 90.0))),
                "el": ("time", np.deg2rad(np.full(n, 75.0))),
                "range": ("time", np.full(n, 1e20, dtype=float)),  # distância cosmológica
            },
            coords={"time": time_grid},
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_type(self) -> str:
        return "radiosource"

    @property
    def tracks(self) -> xr.Dataset:
        return self._tracks

    def psd(self) -> xr.DataArray:
        freq = np.array([1.0e9], dtype=float)
        # Fonte fraca: 1 Jy → 1e-26 W/m²/Hz
        return xr.DataArray(
            np.array([1e-26], dtype=float),
            dims="frequency",
            coords={"frequency": freq},
            attrs={"units": "W/Hz"},
        )


# ═══════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════


class TestComputePointingTrack:
    """Step 1: compute_pointing_track() com Skyfield."""

    def test_ra_dec_variation(self, observer, time_grid):
        """Pointing fixo alt-az produz RA variante no tempo."""
        from radioskysims_core.domain.geometry import compute_pointing_track

        pt = compute_pointing_track(observer, time_grid, alt_deg=67.0, az_deg=0.0)
        assert "ra" in pt
        assert "dec" in pt
        assert "time" in pt.dims
        assert len(pt.time) == len(time_grid)

        # RA deve variar (rotação da Terra)
        ra_range = float(pt.ra.max().values - pt.ra.min().values)
        assert ra_range > 0, f"RA não variou: range={ra_range}"

    def test_ra_variation_rate(self, observer):
        """10 minutos → RA varia ~2.5° (15°/h)."""
        from radioskysims_core.domain.geometry import compute_pointing_track

        grid = np.arange(
            np.datetime64("2026-07-28T00:00:00"),
            np.datetime64("2026-07-28T00:10:00"),
            np.timedelta64(60, "s"),
            dtype="datetime64[ns]",
        )
        pt = compute_pointing_track(observer, grid, alt_deg=67.0, az_deg=0.0)
        ra_range = float(pt.ra.max().values - pt.ra.min().values)
        # 10 min = 1/6 h → 15/6 = 2.5°
        assert 2.0 < ra_range < 3.0, f"RA variation {ra_range:.2f}° != ~2.5°"


class TestComputeThetaBoresight:
    """Step 2: compute_theta_boresight com pointing temporal."""

    def test_fixed_pointing(self):
        """Compatibilidade retroativa: pointing fixo funciona."""
        n = 5
        tracks = xr.Dataset(
            {
                "ra": ("time", np.deg2rad(np.linspace(100, 110, n))),
                "dec": ("time", np.deg2rad(np.linspace(10, 12, n))),
            },
            coords={"time": np.arange(n).astype("datetime64[ns]")},
        )
        gamma = compute_theta_boresight(tracks, pointing_ra_deg=105.0, pointing_dec_deg=11.0)
        assert gamma.name == "angle_boresight"
        assert gamma.attrs["units"] == "rad"
        assert gamma.shape == (n,)

    def test_temporal_pointing(self):
        """Pointing temporal (DataArray) funciona."""
        n = 5
        time = np.arange(n).astype("datetime64[ns]")
        tracks = xr.Dataset(
            {
                "ra": ("time", np.deg2rad(np.linspace(100, 110, n))),
                "dec": ("time", np.deg2rad(np.linspace(10, 12, n))),
            },
            coords={"time": time},
        )
        pt_ra = xr.DataArray(np.full(n, 105.0), dims="time", coords={"time": time})
        pt_dec = xr.DataArray(np.full(n, 11.0), dims="time", coords={"time": time})
        gamma = compute_theta_boresight(tracks, pointing_track_ra=pt_ra, pointing_track_dec=pt_dec)
        assert gamma.shape == (n,)
        assert gamma.attrs["units"] == "rad"

    def test_temporal_matches_fixed(self):
        """Pointing temporal uniforme produz mesmo resultado que fixo."""
        n = 5
        time = np.arange(n).astype("datetime64[ns]")
        tracks = xr.Dataset(
            {
                "ra": ("time", np.deg2rad(np.linspace(100, 110, n))),
                "dec": ("time", np.deg2rad(np.linspace(10, 12, n))),
            },
            coords={"time": time},
        )
        pt_ra = xr.DataArray(np.full(n, 105.0), dims="time", coords={"time": time})
        pt_dec = xr.DataArray(np.full(n, 11.0), dims="time", coords={"time": time})

        gamma_fixed = compute_theta_boresight(tracks, pointing_ra_deg=105.0, pointing_dec_deg=11.0)
        gamma_temporal = compute_theta_boresight(
            tracks, pointing_track_ra=pt_ra, pointing_track_dec=pt_dec
        )
        assert np.allclose(gamma_fixed, gamma_temporal)

    def test_altaz_fallback(self):
        """Fallback alt-az funciona quando não há RA/Dec nos tracks."""
        n = 5
        tracks = xr.Dataset(
            {
                "el": ("time", np.deg2rad(np.linspace(10, 20, n))),
                "az": ("time", np.deg2rad(np.linspace(0, 10, n))),
            },
            coords={"time": np.arange(n).astype("datetime64[ns]")},
        )
        gamma = compute_theta_boresight(tracks, pointing_alt_deg=15.0, pointing_az_deg=5.0)
        assert gamma.shape == (n,)

    def test_no_pointing_raises(self):
        """Erro se nem RA/Dec nem alt-az forem fornecidos."""
        tracks = xr.Dataset(
            {"el": ("time", np.zeros(3))},
            coords={"time": np.arange(3).astype("datetime64[ns]")},
        )
        with pytest.raises(ValueError, match="requer RA/Dec ou alt-az"):
            compute_theta_boresight(tracks)


class TestSimulationMultiSource:
    """Simulation com múltiplos tipos de fonte."""

    def test_single_source_satellite(self, time_grid, beam_gaussian):
        """Simulação com 1 satélite produz resultado com dims esperadas."""
        tod = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )
        src = MockSatelliteSource("GPS-1", time_grid)

        sim = Simulation(
            sources=[src],
            time_range=TimeRange.from_iso(
                "2026-07-28T00:00:00", "2026-07-28T00:10:00", resolution=60
            ),
            tod_simulator=tod,
            pointing_alt_deg=67.0,
            pointing_az_deg=0.0,
            beam_fwhm_deg=23.5,
        )
        result = sim.run()
        ds = result.dataset

        # Dims esperadas
        assert "time" in ds.dims
        assert "frequency" in ds.dims
        assert "source" in ds.dims
        assert "pointing" in ds.dims
        assert "source_type" in ds.coords
        assert ds.coords["source_type"].values[0] == "satellite"

        # Data vars
        assert "T_antenna" in ds
        assert "power" in ds

    def test_three_source_types(self, time_grid, beam_gaussian):
        """Três tipos de fonte produzem source_type distintos."""
        tod = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )

        srcs = [
            MockSatelliteSource("GPS-1", time_grid),
            MockLocalSource("Sun", time_grid),
            MockRadioSource("NVSS-1", time_grid),
        ]

        sim = Simulation(
            sources=srcs,
            time_range=TimeRange.from_iso(
                "2026-07-28T00:00:00", "2026-07-28T00:10:00", resolution=60
            ),
            tod_simulator=tod,
            pointing_alt_deg=67.0,
            pointing_az_deg=0.0,
            beam_fwhm_deg=23.5,
        )
        result = sim.run()
        ds = result.dataset

        assert ds.dims["source"] == 3
        types = list(ds.coords["source_type"].values)
        assert "satellite" in types
        assert "localsource" in types
        assert "radiosource" in types

    def test_fwhm_filter(self, time_grid, beam_gaussian):
        """Fontes fora do limiar N×FWHM são descartadas."""
        tod = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )

        # Fonte muito distante do pointing (el=5°, az=180° → separação ~75° >> 3×10°)
        far_source = MockSatelliteSource("Far", time_grid)
        n = len(time_grid)
        far_source._tracks = xr.Dataset(
            data_vars={
                "theta": ("time", np.deg2rad(np.full(n, 85.0))),
                "az": ("time", np.deg2rad(np.full(n, 180.0))),
                "el": ("time", np.deg2rad(np.full(n, 5.0))),
                "range": ("time", np.full(n, 20000e3, dtype=float)),
            },
            coords={"time": far_source._tracks.coords["time"]},
        )

        sim = Simulation(
            sources=[far_source],
            time_range=TimeRange.from_iso(
                "2026-07-28T00:00:00", "2026-07-28T00:10:00", resolution=60
            ),
            tod_simulator=tod,
            pointing_alt_deg=67.0,
            pointing_az_deg=0.0,
            beam_fwhm_deg=10.0,
            fwhm_factor=3.0,
        )

        with pytest.raises(ValueError, match="Nenhuma fonte dentro do limiar"):
            sim.run()

    def test_pointing_track_integration(self, time_grid, beam_gaussian):
        """Simulation aceita pointing_track e calcula boresight."""
        tod = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )

        pointing_track = xr.Dataset(
            data_vars={
                "ra": ("time", np.full(len(time_grid), 180.0)),
                "dec": ("time", np.full(len(time_grid), 0.0)),
            },
            coords={"time": time_grid},
        )

        src = MockRadioSource("Src", time_grid)

        sim = Simulation(
            sources=[src],
            time_range=TimeRange.from_iso(
                "2026-07-28T00:00:00", "2026-07-28T00:10:00", resolution=60
            ),
            tod_simulator=tod,
            pointing_track=pointing_track,
            beam_fwhm_deg=23.5,
        )
        result = sim.run()
        assert result.dataset.dims["source"] == 1
        assert "T_antenna" in result.dataset

    def test_angle_boresight_preserves_values_with_small_time_offset(
        self,
        time_grid,
        beam_gaussian,
    ):
        """Regressão: pequeno offset temporal não deve gerar angle_boresight NaN."""
        tod = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )

        src = MockSatelliteSource("GPS-1", time_grid)

        shifted_time = src._tracks.coords["time"].values + np.timedelta64(14, "us")

        src._tracks = src._tracks.assign_coords(time=shifted_time)

        sim = Simulation(
            sources=[src],
            time_range=TimeRange.from_iso(
                "2026-07-28T00:00:00",
                "2026-07-28T00:10:00",
                resolution=60,
            ),
            tod_simulator=tod,
            pointing_alt_deg=67.0,
            pointing_az_deg=0.0,
            beam_fwhm_deg=23.5,
        )

        result = sim.run()
        ds = result.dataset

        angle = ds.coords["angle_boresight"]

        assert angle.sizes["time"] == ds.sizes["time"]
        assert np.all(np.isfinite(angle.values))
        np.testing.assert_array_equal(
            angle.coords["time"].values,
            ds.coords["time"].values,
        )


class TestMultiAntenna:
    """Step 6: Consolidação de múltiplas antenas."""

    def test_multi_pointing_concat(self, time_grid, beam_gaussian):
        """Duas simulações com pointings diferentes são concatenáveis."""
        tod1 = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )

        tod2 = TODSimulator(
            beam=beam_gaussian,
            gain=1.0,
            effective_area_m2=1.0,
        )
        src = MockSatelliteSource("GPS-1", time_grid)
        tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:10:00", resolution=60)

        sim1 = Simulation(
            sources=[src],
            time_range=tr,
            tod_simulator=tod1,
            pointing_alt_deg=67.0,
            pointing_az_deg=0.0,
        )
        sim2 = Simulation(
            sources=[src],
            time_range=tr,
            tod_simulator=tod2,
            pointing_alt_deg=45.0,
            pointing_az_deg=90.0,
        )

        r1 = sim1.run()
        r2 = sim2.run()

        # Concatena como SimOrchestrator faria
        ds1 = r1.dataset.assign_coords(pointing=[0])
        ds2 = r2.dataset.assign_coords(pointing=[1])
        merged = xr.concat(
            [ds1, ds2],
            dim="pointing",
            compat="override",
            coords="minimal",
            combine_attrs="drop_conflicts",
        )

        assert merged.dims["pointing"] == 2
        assert "T_antenna" in merged
        assert merged["T_antenna"].dims == (
            "time",
            "frequency",
            "polarization",
            "source",
            "pointing",
        )
