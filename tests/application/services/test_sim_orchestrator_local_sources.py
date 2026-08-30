"""\
Módulo: tests/application/services/test_sim_orchestrator_local_sources.py

Descrição:
    Testes unitários para integração de LocalSources no SimOrchestrator.

Copyright BINGO Collaboration
Last modified: 2026-03-03
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import xarray as xr

from radioskysims_sources.application.services.source_assembler import SourceAssembler
from radioskysims_core.domain.common import Observer, TimeRange
from radioskysims_sources.domain.localsources.models import (
    LocalSource,
    LocalSources,
    LocalSourceTrack,
    SolarFlux,
)


class _FakeLocalSourcesService:
    def __init__(self, time_range: TimeRange) -> None:
        self._time_range = time_range

    def build_local_sources(self) -> LocalSources:
        return LocalSources(
            sources=[
                LocalSource(name="Sun", kind="sun", has_track=True, has_signal=True),
            ]
        )

    def get_solar_flux(self, center_utc: datetime, window_hours: int | None = None) -> SolarFlux:
        _ = window_hours
        center_naive_utc = center_utc.astimezone(UTC).replace(tzinfo=None)
        times = np.array(center_naive_utc, dtype="datetime64[ns]") + np.arange(
            -1, 2
        ) * np.timedelta64(30, "m")
        freqs = np.array([1000.0, 1100.0], dtype=float)
        values = np.array(
            [
                [100.0, 120.0],
                [140.0, 160.0],
                [180.0, 200.0],
            ],
            dtype=float,
        )
        ds = xr.Dataset(
            data_vars={"flux_jy": (("time", "frequency_mhz"), values)},
            coords={"time": times, "frequency_mhz": freqs},
        )
        return SolarFlux(
            start_utc=center_utc,
            end_utc=center_utc,
            dataset=ds,
            source_url="fake://solar",
        )

    def get_local_source_track(
        self,
        source_name: str,
        observer: Observer,
        time_range: TimeRange,
    ) -> LocalSourceTrack:
        _ = observer
        times = np.asarray(time_range.to_astropy().datetime64).astype("datetime64[ns]")
        n = len(times)
        ds = xr.Dataset(
            data_vars={
                "theta_rad": ("time", np.linspace(0.1, 0.3, n)),
                "az_rad": ("time", np.linspace(0.2, 0.4, n)),
                "el_rad": ("time", np.linspace(0.5, 0.7, n)),
                "range_m": ("time", np.linspace(1.0e11, 1.1e11, n)),
            },
            coords={"time": times},
        )
        return LocalSourceTrack(source_name=source_name, dataset=ds)


def test_source_assembler_builds_local_source_signal() -> None:
    """Verifica que SourceAssembler produz SignalSource para fonte local (Sun)."""
    tr = TimeRange.from_iso(
        start="2025-02-03T12:00:00",
        end="2025-02-03T12:20:00",
        resolution=600,
    )

    fake_local = _FakeLocalSourcesService(time_range=tr)

    assembler = SourceAssembler(
        local_sources_service=fake_local,
    )

    observer = Observer(
        lat=-22.0,
        lon=-45.0,
        height=800.0,
        timeframe=tr,
    )

    # Gera grade temporal no formato esperado
    time_grid = np.asarray(tr.to_astropy().datetime64).astype("datetime64[ns]")

    freq_mhz = np.array([1000.0, 1100.0], dtype=float)

    sources = assembler.assemble_local_sources(
        observer=observer,
        time_range=tr,
        time_grid=time_grid,
        freq_mhz=freq_mhz,
    )

    # Deve ter gerado 1 SignalSource (Sun)
    assert len(sources) == 1
    src = sources[0]
    assert src.name == "Sun"
    assert src.source_type == "localsource"

    # Verifica tracks
    tracks = src.tracks
    for var in ("theta", "az", "el", "range"):
        assert var in tracks.data_vars, f"Variável '{var}' ausente nos tracks"
        assert "time" in tracks[var].dims

    # Verifica PSD (densidade de fluxo: W/m²/Hz, sem fator 1/r²)
    psd = src.psd()
    assert "frequency" in psd.dims
    assert psd.attrs.get("units") == "W/m²/Hz"
