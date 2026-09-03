from __future__ import annotations

from collections.abc import Sequence

from radioskysims_skymap.application.skymap.dto import (
    GenerateSkyMapInputDTO,
)
from radioskysims_skymap.application.skymap.generate import (
    GenerateSkyMapUseCase,
)

from radioskysims.interfaces.cli.formatters import (
    OutputFormat,
    format_generate_result,
)


def execute_generate_command(
    *,
    use_case: GenerateSkyMapUseCase,
    frequency_ghz: float,
    nside: int,
    components: Sequence[str],
    output_format: OutputFormat = "text",
) -> str:
    """Executa o comando de geração de SkyMap.

    A função pertence à Presentation e somente:

    1. cria o DTO de entrada;
    2. chama o caso de uso;
    3. formata o resultado.
    """

    input_dto = GenerateSkyMapInputDTO(
        frequency_ghz=frequency_ghz,
        nside=nside,
        components=tuple(components),
    )

    output_dto = use_case.execute(input_dto)

    return format_generate_result(
        output=output_dto,
        frequency_ghz=frequency_ghz,
        components=components,
        output_format=output_format,
    )
