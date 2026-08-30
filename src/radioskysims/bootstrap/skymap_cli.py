from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from radioskysims_skymap.application.skymap.analyze import (
    AnalyzeSkyMapUseCase,
)
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
from radioskysims_skymap.infrastructure.skymap.providers.pysm import (
    PySMSkyMapGeneratorAdapter,
)
from radioskysims.interfaces.cli.main import (
    SkyMapCLIUseCases,
    run,
)


def build_continuum_survey_use_case(
    base_path: Path,
) -> ContinuumSurveyMapUseCase:
    """Constrói o caso de uso de survey sob demanda."""

    from radioskysims_skymap.infrastructure.skymap.providers.hips import (
        HiPSSkyMapProvider,
    )

    provider = HiPSSkyMapProvider(
        base_path=base_path,
    )

    return ContinuumSurveyMapUseCase(
        provider=provider,
    )


def build_skymap_cli_use_cases() -> SkyMapCLIUseCases:
    """Constrói as dependências da CLI de SkyMap."""

    generator = PySMSkyMapGeneratorAdapter(
        unit="uK_CMB",
        field="I",
    )

    analyzer = HealpySkyMapAnalyzer()
    reader = HealpySkyMapProvider()

    return SkyMapCLIUseCases(
        generate_skymap=GenerateSkyMapUseCase(
            generator=generator,
        ),
        continuum_survey_factory=(
            build_continuum_survey_use_case
        ),
        analyze_skymap=AnalyzeSkyMapUseCase(
            analyzer=analyzer,
        ),
        skymap_reader=reader,
    )


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """Executa a CLI de SkyMap."""

    return run(
        argv,
        use_cases=build_skymap_cli_use_cases(),
    )


if __name__ == "__main__":
    raise SystemExit(main())