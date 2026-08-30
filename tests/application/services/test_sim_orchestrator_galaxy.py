from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest
import xarray as xr

from radioskysims_simulation.application.services.sim_orchestrator import (
    SimOrchestrator,
)
from radioskysims_simulation.application.services.tod_orchestrator import (
    TODOrchestrator,
)
from radioskysims_core.domain.common import TimeRange
from radioskysims_simulation.domain.simulation import SimulationResult


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
    def __init__(
        self,
        dataset: xr.Dataset,
    ) -> None:
        self._dataset = dataset
        self.calls: list[dict] = []

    def run_multi_source(
        self,
        **kwargs,
    ) -> SimulationResult:
        self.calls.append(kwargs)

        return SimulationResult(
            dataset=self._dataset.copy(deep=True),
            sources=[
                SimpleNamespace(name="GPS-1"),
            ],
            satellites=[
                SimpleNamespace(id="GPS-1"),
            ],
            time_range=kwargs["time_range"],
        )


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
            dtype=float,
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
        data_vars={
            "T_antenna": temperature,
            "power": power,
        },
        attrs={
            "contributions": [
                "source",
            ],
        },
    )


def test_sim_orchestrator_combines_discrete_and_galaxy_tod(
    monkeypatch,
) -> None:
    """
    Verifica o fluxo de alto nível:

    fontes discretas
        +
    Galaxy
        ->
    TOD combinado.
    """

    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    source_dataset = _dataset(temperature_k=1.0)

    galaxy_dataset = _dataset(temperature_k=2.0)

    simulation_service = _FakeSimulationService(source_dataset)

    tod_orchestrator = TODOrchestrator(
        simulator=object(),
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=(_FakeSatelliteService()),
        simulation_service=(simulation_service),
        tod_orchestrator=(tod_orchestrator),
        galaxy_map_generator=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(context)

    # Evita carregar o radiotelescópio real de settings.toml.
    fake_antenna = object()

    fake_rt = SimpleNamespace(
        antennas=[
            fake_antenna,
        ],
    )

    monkeypatch.setattr(
        ("radioskysims_core.config.config_loader.build_radiotelescope_from_settings"),
        lambda _telescope_name: fake_rt,
    )

    # Evita depender da configuração real do beam/antenna.
    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: (
            None,  # beam
            None,  # backend
            2,  # num_channels
            None,  # ra_deg
            None,  # dec_deg
            67.0,  # alt_deg
            0.0,  # az_deg
        ),
    )

    galaxy_calls: list[dict] = []

    def _fake_run_galaxy_for_antenna(
        **kwargs,
    ) -> xr.Dataset:
        galaxy_calls.append(kwargs)

        return galaxy_dataset.copy(deep=True)

    monkeypatch.setattr(
        orchestrator,
        "_run_galaxy_for_antenna",
        _fake_run_galaxy_for_antenna,
    )

    # O resumo não faz parte do objetivo deste teste.
    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    result = orchestrator.run(
        constellations=[
            "GPS",
        ],
        time_range=time_range,
        include_galaxy=True,
        galaxy_nside=64,
        persist_skymaps=True,
        skymap_overwrite=True,
        use_processor=False,
    )

    dataset = result.simulation_result.dataset

    # 1 K das fontes + 2 K da Galaxy.
    np.testing.assert_allclose(
        dataset["T_antenna"].values,
        3.0,
    )

    expected_power = 3.0 * 1.380649e-23

    np.testing.assert_allclose(
        dataset["power"].values,
        expected_power,
    )

    # Confirma que o caminho discreto foi executado.
    assert len(simulation_service.calls) == 1

    # Confirma que o caminho Galaxy foi executado.
    assert len(galaxy_calls) == 1

    galaxy_call = galaxy_calls[0]

    assert galaxy_call["nside"] == 64

    assert galaxy_call["persist_skymaps"] is True

    assert galaxy_call["skymap_overwrite"] is True

    assert galaxy_call["alt_deg"] == 67.0

    assert galaxy_call["az_deg"] == 0.0

    # Confirma metadados adicionados pelo SimOrchestrator.
    assert result.config["include_galaxy"] is True

    assert result.config["galaxy_nside"] == 64

    assert result.config["persist_skymaps"] is True


def test_sim_orchestrator_does_not_run_galaxy_when_disabled(
    monkeypatch,
) -> None:
    """
    Garante backward compatibility:

    include_galaxy=False
        -> caminho Galaxy não é executado.
    """

    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    source_dataset = _dataset(
        temperature_k=1.0,
    )

    simulation_service = _FakeSimulationService(
        source_dataset,
    )

    tod_orchestrator = TODOrchestrator(
        simulator=object(),
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeSatelliteService(),
        simulation_service=simulation_service,
        tod_orchestrator=tod_orchestrator,
        galaxy_map_generator=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(
        context,
    )

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

    def _galaxy_must_not_run(
        **kwargs,
    ):
        _ = (kwargs)  # assinala uso (interface/reservado)
        msg = "Galaxy path must not run when include_galaxy=False."
        raise AssertionError(msg)

    monkeypatch.setattr(
        orchestrator,
        "_run_galaxy_for_antenna",
        _galaxy_must_not_run,
    )

    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    result = orchestrator.run(
        constellations=["GPS"],
        time_range=time_range,
        include_galaxy=False,
        use_processor=False,
    )

    np.testing.assert_allclose(
        result.simulation_result["T_antenna"].values
        if hasattr(
            result.simulation_result,
            "__getitem__",
        )
        else result.simulation_result.dataset["T_antenna"].values,
        1.0,
    )

    assert result.config["include_galaxy"] is False

    assert result.config["galaxy_nside"] is None

    assert result.config["persist_skymaps"] is False


def test_sim_orchestrator_propagates_galaxy_options(
    monkeypatch,
) -> None:
    """Verifica parâmetros de geração/persistência Galaxy."""

    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    simulation_service = _FakeSimulationService(
        _dataset(
            temperature_k=1.0,
        )
    )

    tod_orchestrator = TODOrchestrator(
        simulator=object(),
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeSatelliteService(),
        simulation_service=simulation_service,
        tod_orchestrator=tod_orchestrator,
        galaxy_map_generator=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(
        context,
    )

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
            50.0,
            15.0,
        ),
    )

    captured: dict = {}

    def _fake_galaxy(
        **kwargs,
    ) -> xr.Dataset:
        captured.update(
            kwargs,
        )

        return _dataset(
            temperature_k=2.0,
        )

    monkeypatch.setattr(
        orchestrator,
        "_run_galaxy_for_antenna",
        _fake_galaxy,
    )

    monkeypatch.setattr(
        ("radioskysims_simulation.domain.simulation.summary.assemble_config"),
        lambda **_kwargs: {},
    )

    orchestrator.run(
        constellations=["GPS"],
        time_range=time_range,
        include_galaxy=True,
        galaxy_nside=128,
        persist_skymaps=True,
        skymap_overwrite=True,
        use_processor=False,
    )

    assert captured["nside"] == 128
    assert captured["persist_skymaps"] is True
    assert captured["skymap_overwrite"] is True
    assert captured["alt_deg"] == 50.0
    assert captured["az_deg"] == 15.0


class _FakeEmptySatelliteService:
    def get_by_constellations(
        self,
        constellations: list[str],
    ) -> list[object]:
        _ = constellations
        return []


def test_sim_orchestrator_runs_galaxy_without_satellites(
    monkeypatch,
) -> None:
    """
    Galaxy-only deve funcionar mesmo quando não existem satélites.

    O caminho de fontes discretas não deve ser executado.
    """

    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    simulation_service = _FakeSimulationService(
        _dataset(
            temperature_k=1.0,
        )
    )

    tod_orchestrator = TODOrchestrator(
        simulator=object(),
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeEmptySatelliteService(),
        simulation_service=simulation_service,
        tod_orchestrator=tod_orchestrator,
        galaxy_map_generator=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(
        context,
    )

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
            None,  # beam
            None,  # backend
            2,  # num_channels
            None,  # ra_deg
            None,  # dec_deg
            67.0,  # alt_deg
            0.0,  # az_deg
        ),
    )

    galaxy_calls: list[dict] = []

    def _fake_galaxy(
        **kwargs,
    ) -> xr.Dataset:
        galaxy_calls.append(
            kwargs,
        )

        return _dataset(
            temperature_k=2.0,
        )

    monkeypatch.setattr(
        orchestrator,
        "_run_galaxy_for_antenna",
        _fake_galaxy,
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
        persist_skymaps=False,
        use_processor=False,
    )

    dataset = result.simulation_result.dataset

    # Galaxy = 2 K.
    np.testing.assert_allclose(
        dataset["T_antenna"].values,
        2.0,
    )

    np.testing.assert_allclose(
        dataset["power"].values,
        2.0 * 1.380649e-23,
    )

    # SimulationService não deve ter sido executado,
    # pois não existem fontes discretas.
    assert len(simulation_service.calls) == 0

    # Galaxy deve ter sido executada.
    assert len(galaxy_calls) == 1

    assert result.config["include_galaxy"] is True

    assert result.config["n_satellites"] == 0

    assert result.simulation_result.satellites == []


def test_sim_orchestrator_requires_satellites_when_galaxy_disabled(
    monkeypatch,
) -> None:
    """
    Garante backward compatibility:

    sem satélites
    +
    include_galaxy=False
        ->
    RuntimeError.
    """
    _ = (monkeypatch)  # assinala uso (interface/reservado)

    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    simulation_service = _FakeSimulationService(
        _dataset(
            temperature_k=1.0,
        )
    )

    tod_orchestrator = TODOrchestrator(
        simulator=object(),
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeEmptySatelliteService(),
        simulation_service=simulation_service,
        tod_orchestrator=tod_orchestrator,
        galaxy_map_generator=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(
        context,
    )

    with pytest.raises(
        RuntimeError,
        match="Nenhum satélite disponível",
    ):
        orchestrator.run(
            constellations=[],
            time_range=time_range,
            include_galaxy=False,
            use_processor=False,
        )

    # Nenhum TOD discreto deve ter sido iniciado.
    assert len(simulation_service.calls) == 0


def test_sim_orchestrator_reuses_galaxy_maps_for_multiple_antennas(
    monkeypatch,
) -> None:
    """
    Os mapas físicos da Galaxy devem ser gerados uma única vez
    e reutilizados por todas as antenas.
    """

    time_range = TimeRange.from_iso(
        start="2026-07-28T00:00:00",
        end="2026-07-28T00:01:00",
        resolution=60,
    )

    simulation_service = _FakeSimulationService(
        _dataset(
            temperature_k=1.0,
        )
    )

    tod_orchestrator = TODOrchestrator(
        simulator=object(),
    )

    context = SimpleNamespace(
        telescope_name="bingo",
        observer=SimpleNamespace(),
        frequency_range=SimpleNamespace(),
        satellite_repository=SimpleNamespace(),
        satellite_service=_FakeEmptySatelliteService(),
        simulation_service=simulation_service,
        tod_orchestrator=tod_orchestrator,
        galaxy_map_generator=object(),
        skymap_repository=object(),
        skymap_tod_projector=object(),
        local_sources_service=None,
        radio_source_catalog_service=None,
        config_loader=None,
        logger=None,
        simulation_repository=None,
    )

    orchestrator = SimOrchestrator(
        context,
    )

    # Duas antenas.
    fake_rt = SimpleNamespace(
        antennas=[
            object(),
            object(),
        ],
    )

    monkeypatch.setattr(
        ("radioskysims_core.config.config_loader.build_radiotelescope_from_settings"),
        lambda _telescope_name: fake_rt,
    )

    pointings = iter(
        [
            (
                None,
                None,
                2,
                None,
                None,
                67.0,
                0.0,
            ),
            (
                None,
                None,
                2,
                None,
                None,
                50.0,
                15.0,
            ),
        ]
    )

    monkeypatch.setattr(
        orchestrator,
        "_resolve_antenna_config",
        lambda _antenna: next(pointings),
    )

    galaxy_generation_calls = 0
    galaxy_projection_calls = 0

    fake_maps = (
        SimpleNamespace(
            freq_ghz=1.0,
        ),
    )

    def _fake_generate_galaxy_maps(
        **kwargs,
    ):
        _ = (kwargs)  # assinala uso (interface/reservado)
        nonlocal galaxy_generation_calls

        galaxy_generation_calls += 1

        return fake_maps

    def _fake_project_galaxy_for_antenna(
        *,
        maps,
        **kwargs,
    ) -> xr.Dataset:
        _ = (kwargs)  # assinala uso (interface/reservado)
        nonlocal galaxy_projection_calls

        galaxy_projection_calls += 1

        assert maps is fake_maps

        return _dataset(
            temperature_k=2.0,
        )

    monkeypatch.setattr(
        orchestrator,
        "_generate_galaxy_maps",
        _fake_generate_galaxy_maps,
    )

    monkeypatch.setattr(
        orchestrator,
        "_run_galaxy_maps_for_antenna",
        _fake_project_galaxy_for_antenna,
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
        persist_skymaps=True,
        skymap_overwrite=False,
        use_processor=False,
    )

    # O céu físico é gerado apenas uma vez.
    assert galaxy_generation_calls == 1

    # Cada antena observa o mesmo céu.
    assert galaxy_projection_calls == 2

    # Resultado consolidado nas duas antenas.
    assert result.simulation_result.dataset.sizes["pointing"] == 2
