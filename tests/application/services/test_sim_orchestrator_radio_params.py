from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import xarray as xr

from radioskysims_simulation.application.services.sim_orchestrator import SimOrchestrator
from radioskysims_core.domain.common import TimeRange
from radioskysims_simulation.domain.simulation import SimulationResult


class _FakeSatelliteService:
    def get_by_constellations(self, constellations: list[str]) -> list[object]:
        _ = constellations
        return [SimpleNamespace(id="GPS-1")]


class _FakeSimulationService:
    def __init__(self, dataset: xr.Dataset) -> None:
        self._dataset = dataset
        self.calls: list[dict] = []

    def run_multi_source(self, **kwargs) -> SimulationResult:
        self.calls.append(kwargs)
        return SimulationResult(
            dataset=self._dataset.copy(deep=True),
            sources=[],
            satellites=[],
            time_range=kwargs["time_range"],
        )


def _dataset() -> xr.Dataset:
    time = np.array(["2026-07-28T00:00:00", "2026-07-28T00:01:00"], dtype="datetime64[ns]")
    frequency = np.array([1.0e9, 1.1e9], dtype=float)
    temperature = xr.DataArray(
        np.full((len(time), len(frequency)), 1.0, dtype=float),
        dims=("time", "frequency"),
        coords={"time": time, "frequency": frequency},
    )
    power = temperature * 1.380649e-23
    return xr.Dataset(
        data_vars={"T_antenna": temperature, "power": power},
        attrs={"contributions": ["source"]},
    )


def _orchestrator(*, config_loader=None) -> tuple[SimOrchestrator, _FakeSimulationService]:
    simulation_service = _FakeSimulationService(_dataset())
    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeSatelliteService(),
        simulation_service=simulation_service,
        tod_orchestrator=SimpleNamespace(),
        galaxy_map_generator=None,
        skymap_repository=None,
        skymap_tod_projector=None,
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=config_loader,
        logger=None,
        simulation_repository=None,
    )
    orchestrator = SimOrchestrator(context)
    return orchestrator, simulation_service


def _patch_radiotelescope(monkeypatch, orchestrator: SimOrchestrator) -> None:
    fake_antenna = object()
    fake_rt = SimpleNamespace(antennas=[fake_antenna])

    monkeypatch.setattr(
        "radioskysims_core.config.config_loader.build_radiotelescope_from_settings",
        lambda _telescope_name: fake_rt,
    )
    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: (None, None, 2, None, None, 67.0, 0.0),
    )
    monkeypatch.setattr(
        "radioskysims_simulation.domain.simulation.summary.assemble_config",
        lambda **kwargs: kwargs,
    )


def test_radio_query_defaults_preserved(monkeypatch) -> None:
    orchestrator, simulation_service = _orchestrator()
    _patch_radiotelescope(monkeypatch, orchestrator)

    tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:01:00", resolution=60)
    result = orchestrator.run(
        constellations=["GPS"],
        time_range=tr,
        include_radio_sources=True,
        use_processor=False,
    )

    call = simulation_service.calls[0]
    assert call["radio_search_radius_deg"] == 20.0
    assert call["radio_min_flux_jy"] == 1.0
    assert result.config["radio_query"]["search_radius_deg"] == 20.0
    assert result.config["radio_query"]["min_flux_jy"] == 1.0


def test_radio_query_explicit_search_radius_overrides_default(monkeypatch) -> None:
    orchestrator, simulation_service = _orchestrator()
    _patch_radiotelescope(monkeypatch, orchestrator)

    tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:01:00", resolution=60)
    orchestrator.run(
        constellations=["GPS"],
        time_range=tr,
        include_radio_sources=True,
        radio_search_radius_deg=42.5,
        use_processor=False,
    )

    call = simulation_service.calls[0]
    assert call["radio_search_radius_deg"] == 42.5
    assert call["radio_min_flux_jy"] == 1.0


def test_radio_query_explicit_min_flux_overrides_default(monkeypatch) -> None:
    orchestrator, simulation_service = _orchestrator()
    _patch_radiotelescope(monkeypatch, orchestrator)

    tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:01:00", resolution=60)
    orchestrator.run(
        constellations=["GPS"],
        time_range=tr,
        include_radio_sources=True,
        radio_min_flux_jy=3.25,
        use_processor=False,
    )

    call = simulation_service.calls[0]
    assert call["radio_search_radius_deg"] == 20.0
    assert call["radio_min_flux_jy"] == 3.25


def test_radio_query_params_are_independent(monkeypatch) -> None:
    orchestrator, simulation_service = _orchestrator()
    _patch_radiotelescope(monkeypatch, orchestrator)

    tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:01:00", resolution=60)
    orchestrator.run(
        constellations=["GPS"],
        time_range=tr,
        include_radio_sources=True,
        radio_search_radius_deg=12.0,
        radio_min_flux_jy=0.75,
        use_processor=False,
    )

    call = simulation_service.calls[0]
    assert call["radio_search_radius_deg"] == 12.0
    assert call["radio_min_flux_jy"] == 0.75


def test_processing_params_precedence_remains_unchanged(monkeypatch) -> None:
    def _cfg(section: str):
        if section == "processing":
            return {
                "max_batch_mb": 111.0,
                "cpu_count": 7,
                "dask_scheduler": "synchronous",
                "dask_processes": True,
            }
        return {}

    orchestrator, _ = _orchestrator(config_loader=_cfg)
    _patch_radiotelescope(monkeypatch, orchestrator)

    captured: dict = {}

    def _fake_run_with_processor(**kwargs):
        captured.update(kwargs)
        return SimulationResult(
            dataset=_dataset(),
            sources=[],
            satellites=[],
            time_range=kwargs["time_range"],
        )

    monkeypatch.setattr(orchestrator, "_run_with_processor", _fake_run_with_processor)

    tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:01:00", resolution=60)
    orchestrator.run(
        constellations=["GPS"],
        time_range=tr,
        include_radio_sources=True,
        use_processor=True,
        max_batch_mb=222.0,
        cpu_count=3,
        dask_scheduler="threads",
        dask_processes=False,
    )

    assert captured["max_batch_mb"] == 222.0
    assert captured["cpu_count"] == 3
    assert captured["dask_scheduler"] == "threads"
    assert captured["dask_processes"] is False


def test_run_with_processor_passes_radio_query_values_to_assembler(monkeypatch) -> None:
    orchestrator, _ = _orchestrator()

    class _FakeSignalFactory:
        def __init__(self) -> None:
            self.fr = None

    class _FakeTODSim:
        def __init__(self) -> None:
            self.beam = None

    class _FakeSvc:
        def __init__(self) -> None:
            self._signal_factory = _FakeSignalFactory()
            self._tod_simulator = _FakeTODSim()
            self._source_assembler = SimpleNamespace()

        @staticmethod
        def _frequency_range_from_beam(beam):
            _ = (beam)  # assinala uso (interface/reservado)
            return None

        @staticmethod
        def _normalize_frequency_range(frequency_range, num_channels):
            _ = (num_channels)  # assinala uso (interface/reservado)
            return frequency_range

        @staticmethod
        def _beam_frequency_grid(frequency_range, num_channels):
            _ = (frequency_range, num_channels)  # assinala uso (interface/reservado)
            return None

        @staticmethod
        def _interpolate_beam_frequency(beam, freq_grid):
            _ = (freq_grid)  # assinala uso (interface/reservado)
            return beam

        @staticmethod
        def _satellites_are_assembled(satellites):
            _ = (satellites)  # assinala uso (interface/reservado)
            return True

    fake_svc = _FakeSvc()
    orchestrator._ctx.simulation_service = fake_svc

    radio_call: dict = {}

    def _assemble_radio_sources(**kwargs):
        radio_call.update(kwargs)
        return []

    fake_svc._source_assembler = SimpleNamespace(assemble_radio_sources=_assemble_radio_sources)

    monkeypatch.setattr(
        "radioskysims_simulation.application.services.sim_orchestrator._compute_time_grid",
        lambda _tr: np.array([np.datetime64("2026-07-28T00:00:00")], dtype="datetime64[ns]"),
    )
    monkeypatch.setattr(
        "radioskysims_simulation.application.services.sim_orchestrator._compute_freq_mhz",
        lambda _fr: np.array([1000.0], dtype=float),
    )

    class _FakeResources:
        cpu_count = 1
        memory_mb = 256.0
        usable_memory_mb = 256.0

    class _NoOpLogger:
        """Fake logger that accepts all log methods."""
        def debug(self, *args, **kwargs):
            pass
        def info(self, *args, **kwargs):
            pass
        def warning(self, *args, **kwargs):
            pass
        def error(self, *args, **kwargs):
            pass
        def exception(self, *args, **kwargs):
            pass

    class _FakeProcessor:
        def __init__(self, **kwargs):
            # Contrato de ResourceAwareProcessor: expõe os recursos detectados
            # (o orquestrador lê processor.resources após a construção).
            self.resources = kwargs["resources"]
            self.summary = {}
            self._log = kwargs.get("logger", _NoOpLogger())

        @staticmethod
        def partition_sources(**kwargs):
            _ = (kwargs)  # assinala uso (interface/reservado)
            return []

        @staticmethod
        def run_batches(**kwargs):
            _ = kwargs
            return _dataset()

    monkeypatch.setattr(
        "radioskysims_simulation.infrastructure.processing.resource_processor.ResourceAwareProcessor",
        _FakeProcessor,
    )

    tr = TimeRange.from_iso("2026-07-28T00:00:00", "2026-07-28T00:01:00", resolution=60)
    orchestrator._run_with_processor(
        satellites=[SimpleNamespace(id="GPS-1")],
        time_range=tr,
        observer=SimpleNamespace(),
        frequency_range=None,
        num_channels=None,
        beam=None,
        pointing_ra_deg=None,
        pointing_dec_deg=None,
        pointing_alt_deg=None,
        pointing_az_deg=None,
        mueller=None,
        combine_polarization="sum",
        include_local_sources=False,
        include_radio_sources=True,
        radio_search_radius_deg=33.0,
        radio_min_flux_jy=2.2,
        sun_flux_mean_window_s=None,
        max_batch_mb=None,
        cpu_count=None,
        memory_mb=None,
        dask_scheduler=None,
        dask_processes=None,
        processor_diagnostics=False,
    )

    assert radio_call["search_radius_deg"] == 33.0
    assert radio_call["min_flux_jy"] == 2.2
