from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import numpy as np
import pytest

from radioskysims_skymap.application.skymap.generate import (
    ContinuumSurveyMapUseCase,
    GenerateSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.ports import (
    ContinuumSurveyMapPort,
    SkyMapGeneratorPort,
)
from radioskysims_skymap.domain.skymap import NSide, SkyMap
from radioskysims.interfaces.cli.commands.fetch_survey import (
    execute_survey_command,
)
from radioskysims.interfaces.cli.main import (
    SkyMapCLIUseCases,
    run,
)


class FakeContinuumSurveyProvider(
    ContinuumSurveyMapPort
):
    """Provider fake para os testes da CLI."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def fetch_cutout(
        self,
        *,
        survey_id: str,
        ra_deg: float,
        dec_deg: float,
        fov_deg: float,
        nside: NSide,
        freq_ghz: float | None = None,
        field: str = "I",
    ) -> SkyMap:
        self.calls.append(
            {
                "survey_id": survey_id,
                "ra_deg": ra_deg,
                "dec_deg": dec_deg,
                "fov_deg": fov_deg,
                "nside": nside,
                "freq_ghz": freq_ghz,
                "field": field,
            }
        )

        return SkyMap(
            dataset=np.ones(
                nside.npix,
                dtype=np.float64,
            ),
            nside=nside,
            unit="Jy/beam",
            frame="galactic",
            freq_ghz=freq_ghz,
            field=field,
        )


class FakeGenerator(
    SkyMapGeneratorPort
):
    """Gerador mínimo para preencher as dependências da CLI."""

    def generate(
        self,
        *,
        nside: NSide,
        freq_ghz: float,
        components: tuple[str, ...] | list[str] | None = None,
    ) -> SkyMap:
        _ = (components)  # assinala uso (interface/reservado)
        return SkyMap(
            dataset=np.ones(
                nside.npix,
                dtype=np.float64,
            ),
            nside=nside,
            unit="uK_CMB",
            frame="galactic",
            freq_ghz=freq_ghz,
            field="I",
        )


def make_survey_use_case() -> tuple[
    ContinuumSurveyMapUseCase,
    FakeContinuumSurveyProvider,
]:
    provider = FakeContinuumSurveyProvider()

    return (
        ContinuumSurveyMapUseCase(
            provider=provider,
        ),
        provider,
    )


def make_cli_dependencies(
    provider: FakeContinuumSurveyProvider,
) -> SkyMapCLIUseCases:
    def survey_factory(
        base_path: Path,
    ) -> ContinuumSurveyMapUseCase:
        # A factory recebe o caminho, mas o teste não acessa disco.
        assert isinstance(base_path, Path)

        return ContinuumSurveyMapUseCase(
            provider=provider,
        )

    return SkyMapCLIUseCases(
        generate_skymap=GenerateSkyMapUseCase(
            generator=FakeGenerator(),
        ),
        continuum_survey_factory=survey_factory,
    )


def test_execute_survey_command_text() -> None:
    use_case, provider = make_survey_use_case()

    result = execute_survey_command(
        use_case=use_case,
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=8,
        frequency_ghz=1.4,
        field="I",
        output_format="text",
    )

    assert "Mapa de survey obtido com sucesso" in result
    assert "Survey: NVSS" in result
    assert "NSide: 8" in result
    assert "Número de pixels: 768" in result
    assert "Unidade: Jy/beam" in result
    assert "Frequência: 1.4 GHz" in result

    assert provider.calls == [
        {
            "survey_id": "NVSS",
            "ra_deg": 180.0,
            "dec_deg": 0.0,
            "fov_deg": 2.0,
            "nside": NSide(8),
            "freq_ghz": 1.4,
            "field": "I",
        }
    ]


def test_execute_survey_command_json() -> None:
    use_case, _ = make_survey_use_case()

    result = execute_survey_command(
        use_case=use_case,
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=8,
        frequency_ghz=1.4,
        field="I",
        output_format="json",
    )

    payload = json.loads(result)

    assert payload == {
        "status": "success",
        "command": "skymap.survey",
        "survey_id": "NVSS",
        "ra_deg": 180.0,
        "dec_deg": 0.0,
        "fov_deg": 2.0,
        "nside": 8,
        "npix": 768,
        "unit": "Jy/beam",
        "frame": "galactic",
        "frequency_ghz": 1.4,
        "field": "I",
        "dtype": "float64",
    }


def test_run_survey_text_success() -> None:
    provider = FakeContinuumSurveyProvider()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "survey",
            "--survey-id",
            "NVSS",
            "--ra-deg",
            "180",
            "--dec-deg",
            "0",
            "--fov-deg",
            "2",
            "--nside",
            "8",
            "--frequency-ghz",
            "1.4",
            "--field",
            "I",
            "--base-path",
            "outputs/skymap",
        ],
        use_cases=make_cli_dependencies(provider),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert "Mapa de survey obtido com sucesso" in stdout.getvalue()
    assert "Survey: NVSS" in stdout.getvalue()
    assert stderr.getvalue() == ""
    assert len(provider.calls) == 1


def test_run_survey_json_success() -> None:
    provider = FakeContinuumSurveyProvider()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "survey",
            "--survey-id",
            "NVSS",
            "--ra-deg",
            "180",
            "--dec-deg",
            "0",
            "--fov-deg",
            "2",
            "--nside",
            "8",
            "--frequency-ghz",
            "1.4",
            "--field",
            "I",
            "--base-path",
            "outputs/skymap",
            "--output-format",
            "json",
        ],
        use_cases=make_cli_dependencies(provider),
        stdout=stdout,
        stderr=stderr,
    )

    payload = json.loads(
        stdout.getvalue()
    )

    assert exit_code == 0
    assert payload["status"] == "success"
    assert payload["command"] == "skymap.survey"
    assert payload["survey_id"] == "NVSS"
    assert payload["nside"] == 8
    assert payload["npix"] == 768
    assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    ("argument", "value", "expected_message"),
    [
        (
            "--ra-deg",
            "360",
            "ra_deg deve estar entre 0 e 360 graus",
        ),
        (
            "--dec-deg",
            "91",
            "dec_deg deve estar entre -90 e 90 graus",
        ),
        (
            "--fov-deg",
            "0",
            "fov_deg deve ser positivo",
        ),
        (
            "--nside",
            "3",
            "NSide",
        ),
        (
            "--frequency-ghz",
            "0",
            "freq_ghz deve ser positiva",
        ),
    ],
)
def test_run_survey_returns_code_2_for_invalid_input(
    argument: str,
    value: str,
    expected_message: str,
) -> None:
    provider = FakeContinuumSurveyProvider()
    stdout = StringIO()
    stderr = StringIO()

    arguments = [
        "skymap",
        "survey",
        "--survey-id",
        "NVSS",
        "--ra-deg",
        "180",
        "--dec-deg",
        "0",
        "--fov-deg",
        "2",
        "--nside",
        "8",
        "--frequency-ghz",
        "1.4",
        "--field",
        "I",
        "--base-path",
        "outputs/skymap",
    ]

    argument_index = arguments.index(argument)
    arguments[argument_index + 1] = value

    exit_code = run(
        arguments,
        use_cases=make_cli_dependencies(provider),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert expected_message in stderr.getvalue()
    assert provider.calls == []


def test_run_survey_returns_code_3_for_missing_file() -> None:
    stdout = StringIO()
    stderr = StringIO()

    def failing_factory(
        base_path: Path,
    ) -> ContinuumSurveyMapUseCase:
        raise FileNotFoundError(
            base_path / "NVSS.fits"
        )

    dependencies = SkyMapCLIUseCases(
        generate_skymap=GenerateSkyMapUseCase(
            generator=FakeGenerator(),
        ),
        continuum_survey_factory=failing_factory,
    )

    exit_code = run(
        [
            "skymap",
            "survey",
            "--survey-id",
            "NVSS",
            "--ra-deg",
            "180",
            "--dec-deg",
            "0",
            "--fov-deg",
            "2",
            "--nside",
            "8",
            "--base-path",
            "diretorio/inexistente",
        ],
        use_cases=dependencies,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 3
    assert stdout.getvalue() == ""
    assert "Arquivo não encontrado" in stderr.getvalue()