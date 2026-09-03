from __future__ import annotations

from pathlib import Path
from typing import Protocol

from radioskysims_skymap.application.skymap.analyze import (
    AnalyzeSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.dto import (
    AnalyzeSkyMapInputDTO,
)
from radioskysims_skymap.domain.skymap import NSide, SkyMap
from radioskysims.interfaces.cli.formatters import (
    OutputFormat,
    format_analyze_result,
)


class SkyMapReader(Protocol):
    """Contrato mínimo necessário pela CLI para carregar mapas."""

    def read_map(
        self,
        path: str | Path,
        *,
        nside: NSide | None = None,
        unit: str = "unknown",
        frame: str = "galactic",
        field: str = "I",
    ) -> SkyMap:
        """Carrega um SkyMap."""
        ...


def execute_analyze_command(
    *,
    use_case: AnalyzeSkyMapUseCase,
    reader: SkyMapReader,
    input_path: Path,
    lmax: int | None,
    unit: str,
    frame: str,
    field: str,
    output_format: OutputFormat = "text",
) -> str:
    """Carrega um mapa HEALPix, executa a análise e formata o resultado."""

    sky_map = reader.read_map(
        input_path,
        unit=unit,
        frame=frame,
        field=field,
    )

    input_dto = AnalyzeSkyMapInputDTO(
        sky_map=sky_map,
        lmax=lmax,
    )

    output_dto = use_case.execute(input_dto)

    return format_analyze_result(
        output=output_dto,
        sky_map=sky_map,
        input_path=input_path,
        output_format=output_format,
    )
