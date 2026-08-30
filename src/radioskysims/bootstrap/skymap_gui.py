"""src/radioskysims/bootstrap/skymap_gui.py
Composition root da GUI SkyMap.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from radioskysims_skymap.application.skymap.analyze import AnalyzeSkyMapUseCase
from radioskysims_skymap.application.skymap.generate import (
    ContinuumSurveyMapUseCase,
    GenerateSkyMapUseCase,
)
from radioskysims_skymap.infrastructure.skymap.adapters.analysis import (
    HealpySkyMapAnalyzer,
)
from radioskysims_skymap.infrastructure.skymap.providers.healpy import (
    HealpySkyMapProvider,
)
from radioskysims_skymap.infrastructure.skymap.providers.hips import HiPSSkyMapProvider
from radioskysims_skymap.infrastructure.skymap.providers.pysm import PySMSkyMapGeneratorAdapter
from radioskysims.interfaces.gui.skymap import SkyMapGUIController, SkyMapGuiState, build_skymap_app


@dataclass(slots=True)
class SkyMapGuiDependencies:
    state: SkyMapGuiState
    controller: SkyMapGUIController


def _build_generate_use_case() -> GenerateSkyMapUseCase:
    adapter = PySMSkyMapGeneratorAdapter()
    signature = inspect.signature(GenerateSkyMapUseCase)

    kwargs: dict[str, Any] = {}
    for param_name in signature.parameters:
        if param_name in {"self"}:
            continue
        if "generator" in param_name or "provider" in param_name or "port" in param_name:
            kwargs[param_name] = adapter

    if kwargs:
        return GenerateSkyMapUseCase(**kwargs)

    # fallback para assinatura posicional única
    return GenerateSkyMapUseCase(adapter)


def _build_survey_use_case(
    base_path: Path,
) -> ContinuumSurveyMapUseCase:
    provider = HiPSSkyMapProvider(
        base_path=base_path,
    )

    return ContinuumSurveyMapUseCase(
        provider=provider,
    )


def build_skymap_gui_dependencies() -> SkyMapGuiDependencies:
    state = SkyMapGuiState()
    generate_use_case = _build_generate_use_case()
    skymap_reader = HealpySkyMapProvider()
    analyze_use_case = AnalyzeSkyMapUseCase(
        analyzer=HealpySkyMapAnalyzer(),
    )
    controller = SkyMapGUIController(
        state,
        generate_use_case=generate_use_case,
        survey_use_case=_build_survey_use_case,
        analyze_use_case=analyze_use_case,
        skymap_reader=skymap_reader,
    )
    return SkyMapGuiDependencies(state=state, controller=controller)


def build_skymap_gui():
    deps = build_skymap_gui_dependencies()
    return build_skymap_app(deps.controller, deps.state)


def main() -> None:
    import panel as pn

    app = build_skymap_gui()
    pn.serve(app)


if __name__ == "__main__":
    main()