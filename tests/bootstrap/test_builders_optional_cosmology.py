from __future__ import annotations

from types import SimpleNamespace

import pytest
from radioskysims_simulation.bootstrap import builders as sim_builders

from radioskysims.bootstrap import builders


def _patch_minimal_bootstrap_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    # A partir da Fase 5 os builders vivem nos pacotes; `build_simulation_context_dependencies`
    # resolve os nomes no módulo `radioskysims_simulation.bootstrap.builders`.
    monkeypatch.setattr(
        sim_builders,
        "build_configuration",
        lambda telescope="default", settings_file=None: {  # noqa: ARG005 (param nomeado exigido pela interface mockada)
            "telescope_name": telescope,
            "frequency_range": SimpleNamespace(
                min_mhz=980.0,
                max_mhz=1360.0,
                resolution_mhz=1.0,
            ),
        },
    )
    monkeypatch.setattr(
        sim_builders,
        "build_logging",
        lambda: {
            "satellite_logger": object(),
            "simulation_logger": object(),
            "orchestrator_logger": object(),
        },
    )
    monkeypatch.setattr(sim_builders, "build_database", lambda: SimpleNamespace(session=object()))
    monkeypatch.setattr(
        sim_builders,
        "build_repositories",
        lambda _db: {
            "satellite_repository": object(),
            "signal_repository": object(),
        },
    )
    monkeypatch.setattr(
        sim_builders,
        "build_domain_components",
        lambda **_kwargs: {
            "geometry": object(),
            "signal_factory": object(),
            "tod_simulator": object(),
        },
    )
    monkeypatch.setattr(
        sim_builders,
        "build_skymap_components",
        lambda: {"skymap_repository": object()},
    )
    monkeypatch.setattr(
        sim_builders,
        "build_local_sources_service",
        lambda _db: object(),
    )
    monkeypatch.setattr(
        sim_builders,
        "build_services",
        lambda **_kwargs: {
            "satellite_service": object(),
            "simulation_service": object(),
            "tod_orchestrator": object(),
        },
    )


def test_build_simulation_context_dependencies_falls_back_when_pyccl_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_minimal_bootstrap_dependencies(monkeypatch)

    def _raise_pyccl(*args, **kwargs):
        _ = (args, kwargs)  # assinala uso (interface/reservado)
        msg = "No module named 'pyccl'"
        raise ModuleNotFoundError(msg, name="pyccl")

    monkeypatch.setattr(sim_builders, "build_cosmology_components", _raise_pyccl)

    deps = builders.build_simulation_context_dependencies(telescope="bingo")

    assert deps["cosmology_parameters"] is None
    assert deps["neutral_hydrogen_map_generator"] is None


def test_build_simulation_context_dependencies_propagates_other_missing_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_minimal_bootstrap_dependencies(monkeypatch)

    def _raise_other(*args, **kwargs):
        _ = (args, kwargs)  # assinala uso (interface/reservado)
        msg = "No module named 'some_other_module'"
        raise ModuleNotFoundError(
            msg,
            name="some_other_module",
        )

    monkeypatch.setattr(sim_builders, "build_cosmology_components", _raise_other)

    with pytest.raises(ModuleNotFoundError, match="some_other_module"):
        builders.build_simulation_context_dependencies(telescope="bingo")
