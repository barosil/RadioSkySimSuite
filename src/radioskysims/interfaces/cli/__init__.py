from __future__ import annotations

from radioskysims_skymap.application.skymap.generate import (
    ContinuumSurveyMapUseCase,
)
from radioskysims.interfaces.cli.formatters import (
    OutputFormat,
    format_survey_result,
)


def execute_survey_command(
    *,
    use_case: ContinuumSurveyMapUseCase,
    survey_id: str,
    ra_deg: float,
    dec_deg: float,
    fov_deg: float,
    nside: int,
    frequency_ghz: float | None,
    field: str,
    output_format: OutputFormat = "text",
) -> str:
    """Obtém um mapa de survey e formata o resultado."""

    sky_map = use_case.execute(
        survey_id=survey_id,
        ra_deg=ra_deg,
        dec_deg=dec_deg,
        fov_deg=fov_deg,
        nside=nside,
        freq_ghz=frequency_ghz,
        field=field,
    )

    return format_survey_result(
        sky_map=sky_map,
        survey_id=survey_id,
        ra_deg=ra_deg,
        dec_deg=dec_deg,
        fov_deg=fov_deg,
        frequency_ghz=frequency_ghz,
        output_format=output_format,
    )