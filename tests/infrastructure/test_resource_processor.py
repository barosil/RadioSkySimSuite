"""\
Módulo: tests/infrastructure/test_resource_processor.py

Testes do ``ResourceAwareProcessor.run_batches``: a consolidação deve
preservar os nomes REAIS das fontes que sobreviveram ao filtro do feixe,
em vez de fatiar a lista completa por posição (que renomeava o Sol para
'localsource' e associava nomes errados às fontes).

Copyright BINGO Collaboration
Last modified: 2026-08-03
"""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from radioskysims_core.domain.common import TimeRange
from radioskysims_simulation.domain.simulation import SimulationResult
from radioskysims_simulation.infrastructure.processing.resource_processor import (
    ProcessingResources,
    ResourceAwareProcessor,
    SourceBatch,
)


class _FakeSource:
    """Fonte mínima com name/source_type (sem tracks)."""

    def __init__(self, name: str, source_type: str = "satellite") -> None:
        self.name = name
        self.source_type = source_type


def _mk_ds(names: list[str], types: list[str] | None = None) -> xr.Dataset:
    n_t, n_src = 3, len(names)
    time = np.arange(
        np.datetime64("2026-07-26T00:00:00", "ns"),
        np.datetime64("2026-07-26T00:00:00", "ns") + n_t * np.timedelta64(600, "s"),
        np.timedelta64(600, "s"),
    )
    T = np.zeros((n_t, n_src, 1, 1))
    types = types or ["satellite"] * n_src
    return xr.Dataset(
        {"T_antenna": (("time", "source", "polarization", "pointing"), T)},
        coords={
            "time": time,
            "source": names,
            "source_type": ("source", types),
            "polarization": ["V"],
            "pointing": [0],
        },
    )


class _FakeSim:
    """Envolve um SimulationResult com a interface esperada (método ``run``)."""

    def __init__(self, result: SimulationResult) -> None:
        self._result = result

    def run(self) -> SimulationResult:
        return self._result


def _factory(simulate_beam_filter: bool):
    """Fábrica que retorna um dataset com uma SUBSET das fontes do batch.

    Simula o filtro N×FWHM do ``Simulation.run()``: apenas a primeira fonte
    do batch "sobrevive" ao feixe.
    """

    def _make(batch_sources: list) -> _FakeSim:
        names = [s.name for s in batch_sources]
        types = [getattr(s, "source_type", "satellite") for s in batch_sources]
        kept_n = names[:1] if simulate_beam_filter else names
        kept_t = types[:1] if simulate_beam_filter else types
        return _FakeSim(
            SimulationResult(
                dataset=_mk_ds(kept_n, kept_t),
                sources=batch_sources,
                satellites=[],
                time_range=TimeRange.from_iso(
                    "2026-07-26T00:00:00", "2026-07-26T00:30:00", resolution=600
                ),
            )
        )

    return _make


def _processor() -> ResourceAwareProcessor:
    return ResourceAwareProcessor(
        resources=ProcessingResources(
            cpu_count=1,
            available_memory_mb=512.0,
        ),
        dask_scheduler="synchronous",
    )


def test_run_batches_keeps_real_source_names_after_beam_filter() -> None:
    proc = _processor()
    batches = [
        SourceBatch(
            sources=[_FakeSource("GPS-A"), _FakeSource("GPS-B"), _FakeSource("Sun", "localsource")],
            estimated_mb=1.0,
            batch_index=0,
        ),
        SourceBatch(
            sources=[_FakeSource("GPS-C")],
            estimated_mb=1.0,
            batch_index=1,
        ),
    ]
    # Simula que apenas a 1ª fonte de cada batch sobrevive ao feixe:
    # batch0 → [GPS-A], batch1 → [GPS-C]
    ds = proc.run_batches(batches=batches, simulation_factory=_factory(simulate_beam_filter=True))
    names = list(ds.coords["source"].values)
    assert names == ["GPS-A", "GPS-C"], f"Nomes reais das fontes: {names}"


def test_run_batches_no_filter_keeps_all_names() -> None:
    proc = _processor()
    batches = [
        SourceBatch(
            sources=[_FakeSource("GPS-A"), _FakeSource("GPS-B"), _FakeSource("Sun", "localsource")],
            estimated_mb=1.0,
            batch_index=0,
        ),
    ]
    ds = proc.run_batches(batches=batches, simulation_factory=_factory(simulate_beam_filter=False))
    names = list(ds.coords["source"].values)
    assert names == ["GPS-A", "GPS-B", "Sun"]
    assert list(ds.coords["source_type"].values) == ["satellite", "satellite", "localsource"]


def test_distributed_scheduler_starts_dashboard_and_shutdown() -> None:
    """dask_scheduler='distributed' sobe um LocalCluster e loga o dashboard."""
    pytest.importorskip("distributed")
    import dask

    proc = ResourceAwareProcessor(
        resources=ProcessingResources(cpu_count=2, available_memory_mb=512.0),
        dask_scheduler="distributed",
        dask_processes=False,  # 1 worker com threads (rápido p/ teste)
    )
    try:
        proc._configure_dask()
        assert proc.dashboard_url is not None
        assert proc.dashboard_url.startswith("http")
        assert proc.summary["dask_scheduler"] == "distributed"
        assert proc.summary["dashboard_url"] == proc.dashboard_url
        assert dask.config.get("scheduler", None) == "dask.distributed"
    finally:
        proc.shutdown()

    assert proc.dashboard_url is None
    # shutdown restaura threads como scheduler padrão
    assert dask.config.get("scheduler", None) == "threads"


def test_distributed_with_processes_true() -> None:
    """dask_processes=True (padrão) cria workers em processos separados."""
    pytest.importorskip("distributed")

    proc = ResourceAwareProcessor(
        resources=ProcessingResources(cpu_count=2, available_memory_mb=512.0),
        dask_scheduler="distributed",
        dask_processes=True,
    )
    try:
        proc._configure_dask()
        assert proc.dashboard_url is not None
        assert proc.summary["dashboard_url"] == proc.dashboard_url
        n_workers = len(proc._client.scheduler_info()["workers"])
        assert n_workers == 2
    finally:
        proc.shutdown()
