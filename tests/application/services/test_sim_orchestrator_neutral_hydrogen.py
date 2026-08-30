from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import xarray as xr

from radioskysims_simulation.application.services.sim_orchestrator import (
    SimOrchestrator,
)
from radioskysims_simulation.application.services.tod_orchestrator import (
    TODOrchestrator,
)
from radioskysims_core.domain.common import TimeRange


class _FakeEmptySatelliteService:
    def get_by_constellations(
        self,
        constellations: list[str],
    ) -> list[object]:
        _ = constellations
        return []


def _dataset(
    *,
    temperature_k: float,
) -> xr.Dataset:
    time = np.array(
        [
            "2026-07-28T00:00:00",
            "2026-07-28T00:01:00",
        ],
        dtype="datetime64[ns]",
    )

    frequency = np.array(
        [
            1.0e9,
            1.1e9,
        ],
        dtype=float,
    )

    temperature = xr.DataArray(
        np.full(
            (
                len(time),
                len(frequency),
            ),
            temperature_k,
        ),
        dims=(
            "time",
            "frequency",
        ),
        coords={
            "time": time,
            "frequency": frequency,
        },
    )

    power = temperature * 1.380649e-23

    return xr.Dataset(
        {
            "T_antenna": temperature,
            "power": power,
        }
    )


def test_sim_orchestrator_runs_neutral_hydrogen_without_satellites(
    monkeypatch,
) -> None:
    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeEmptySatelliteService(),
        simulation_service=SimpleNamespace(),
        tod_orchestrator=TODOrchestrator(
            simulator=object(),
        ),
        galaxy_map_generator=None,
        neutral_hydrogen_map_generator=object(),
        cosmology_parameters=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(context)

    fake_rt = SimpleNamespace(
        antennas=[
            object(),
        ],
    )

    monkeypatch.setattr(
        ("radioskysims_core.config.config_loader.build_radiotelescope_from_settings"),
        lambda _telescope_name: fake_rt,
    )

    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: (
            None,
            None,
            2,
            None,
            None,
            67.0,
            0.0,
        ),
    )

    hi_calls: list[dict] = []

    def _fake_hi(
        **kwargs,
    ) -> xr.Dataset:
        hi_calls.append(kwargs)

        return _dataset(
            temperature_k=0.5,
        )

    monkeypatch.setattr(
        orchestrator,
        "_run_neutral_hydrogen_for_antenna",
        _fake_hi,
    )

    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    result = orchestrator.run(
        constellations=[],
        time_range=time_range,
        include_galaxy=False,
        include_neutral_hydrogen=True,
        neutral_hydrogen_nside=32,
        neutral_hydrogen_seed=42,
        use_processor=False,
    )

    dataset = result.simulation_result.dataset

    np.testing.assert_allclose(
        dataset["T_antenna"].values,
        0.5,
    )

    assert len(hi_calls) == 1

    assert hi_calls[0]["nside"] == 32
    assert hi_calls[0]["seed"] == 42

    assert result.config["include_neutral_hydrogen"] is True

    assert result.config["neutral_hydrogen_nside"] == 32

    assert result.config["neutral_hydrogen_seed"] == 42

    assert result.simulation_result.satellites == []


def test_sim_orchestrator_combines_discrete_and_neutral_hydrogen_tod(
    monkeypatch,
) -> None:
    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    source_dataset = _dataset(
        temperature_k=1.0,
    )

    class _FakeSatelliteService:
        def get_by_constellations(
            self,
            constellations: list[str],
        ) -> list[object]:
            _ = constellations

            return [
                SimpleNamespace(
                    id="GPS-1",
                ),
            ]

    class _FakeSimulationService:
        def run_multi_source(
            self,
            **kwargs,
        ):
            from radioskysims_simulation.domain.simulation import (
                SimulationResult,
            )

            return SimulationResult(
                dataset=source_dataset.copy(deep=True),
                sources=[
                    SimpleNamespace(
                        name="GPS-1",
                    ),
                ],
                satellites=[
                    SimpleNamespace(
                        id="GPS-1",
                    ),
                ],
                time_range=kwargs["time_range"],
            )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeSatelliteService(),
        simulation_service=_FakeSimulationService(),
        tod_orchestrator=TODOrchestrator(
            simulator=object(),
        ),
        galaxy_map_generator=None,
        neutral_hydrogen_map_generator=object(),
        cosmology_parameters=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(context)

    fake_rt = SimpleNamespace(
        antennas=[
            object(),
        ],
    )

    monkeypatch.setattr(
        ("radioskysims_core.config.config_loader.build_radiotelescope_from_settings"),
        lambda _telescope_name: fake_rt,
    )

    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: (
            None,
            None,
            2,
            None,
            None,
            67.0,
            0.0,
        ),
    )

    monkeypatch.setattr(
        orchestrator,
        "_run_neutral_hydrogen_for_antenna",
        lambda **_kwargs: _dataset(
            temperature_k=0.5,
        ),
    )

    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    result = orchestrator.run(
        constellations=[
            "GPS",
        ],
        time_range=time_range,
        include_neutral_hydrogen=True,
        neutral_hydrogen_nside=32,
        neutral_hydrogen_seed=42,
        use_processor=False,
    )

    np.testing.assert_allclose(
        result.simulation_result.dataset["T_antenna"].values,
        1.5,
    )

    np.testing.assert_allclose(
        result.simulation_result.dataset["power"].values,
        1.5 * 1.380649e-23,
    )

    assert result.simulation_result.dataset.attrs["contributions"] == [
        "source",
        "skymap",
    ]


def test_sim_orchestrator_combines_galaxy_and_neutral_hydrogen_tod(
    monkeypatch,
) -> None:
    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeEmptySatelliteService(),
        simulation_service=SimpleNamespace(),
        tod_orchestrator=TODOrchestrator(
            simulator=object(),
        ),
        galaxy_map_generator=object(),
        neutral_hydrogen_map_generator=object(),
        cosmology_parameters=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(context)

    fake_rt = SimpleNamespace(
        antennas=[
            object(),
        ],
    )

    monkeypatch.setattr(
        ("radioskysims_core.config.config_loader.build_radiotelescope_from_settings"),
        lambda _telescope_name: fake_rt,
    )

    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: (
            None,
            None,
            2,
            None,
            None,
            67.0,
            0.0,
        ),
    )

    monkeypatch.setattr(
        orchestrator,
        "_run_galaxy_for_antenna",
        lambda **_kwargs: _dataset(
            temperature_k=2.0,
        ),
    )

    monkeypatch.setattr(
        orchestrator,
        "_run_neutral_hydrogen_for_antenna",
        lambda **_kwargs: _dataset(
            temperature_k=0.5,
        ),
    )

    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    result = orchestrator.run(
        constellations=[],
        time_range=time_range,
        include_galaxy=True,
        galaxy_nside=64,
        include_neutral_hydrogen=True,
        neutral_hydrogen_nside=32,
        neutral_hydrogen_seed=42,
        use_processor=False,
    )

    dataset = result.simulation_result.dataset

    np.testing.assert_allclose(
        dataset["T_antenna"].values,
        2.5,
    )

    np.testing.assert_allclose(
        dataset["power"].values,
        2.5 * 1.380649e-23,
    )

    assert dataset.attrs["n_map_components"] == 2

    assert result.config["include_galaxy"] is True

    assert result.config["include_neutral_hydrogen"] is True


def test_neutral_hydrogen_persistence_flags_are_propagated(
    monkeypatch,
) -> None:
    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeEmptySatelliteService(),
        simulation_service=SimpleNamespace(),
        tod_orchestrator=TODOrchestrator(
            simulator=object(),
        ),
        galaxy_map_generator=None,
        neutral_hydrogen_map_generator=object(),
        cosmology_parameters=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(context)

    fake_rt = SimpleNamespace(
        antennas=[object()],
    )

    monkeypatch.setattr(
        ("radioskysims_core.config.config_loader.build_radiotelescope_from_settings"),
        lambda _telescope_name: fake_rt,
    )

    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: (
            None,
            None,
            2,
            None,
            None,
            67.0,
            0.0,
        ),
    )

    received: dict[str, object] = {}

    def _fake_hi_for_antenna(
        **kwargs,
    ) -> xr.Dataset:
        received.update(kwargs)

        return _dataset(
            temperature_k=0.5,
        )

    monkeypatch.setattr(
        orchestrator,
        "_run_neutral_hydrogen_for_antenna",
        _fake_hi_for_antenna,
    )

    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    orchestrator.run(
        constellations=[],
        time_range=time_range,
        include_neutral_hydrogen=True,
        neutral_hydrogen_nside=8,
        neutral_hydrogen_seed=42,
        persist_skymaps=True,
        skymap_overwrite=True,
        use_processor=False,
    )

    assert received["persist_skymaps"] is True

    assert received["skymap_overwrite"] is True

    assert received["nside"] == 8

    assert received["seed"] == 42
