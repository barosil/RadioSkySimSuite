from __future__ import annotations

import json
from collections.abc import Sequence
from io import StringIO

import numpy as np

from radioskysims_skymap.application.skymap.generate import (
    GenerateSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.ports import (
    SkyMapGeneratorPort,
)
from radioskysims_skymap.domain.skymap import NSide, SkyMap
from radioskysims.interfaces.cli.main import (
    SkyMapCLIUseCases,
    run,
)


class FakeGenerator(
    SkyMapGeneratorPort
):
    def generate(
        self,
        *,
        nside: NSide,
        freq_ghz: float,
        components: Sequence[str] | None = None,
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


def make_dependencies() -> SkyMapCLIUseCases:
    return SkyMapCLIUseCases(
        generate_skymap=GenerateSkyMapUseCase(
            generator=FakeGenerator(),
        )
    )


def test_run_generate_text_success() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "generate",
            "--frequency-ghz",
            "30",
            "--nside",
            "1",
            "--components",
            "synchrotron",
            "dust",
        ],
        use_cases=make_dependencies(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert "SkyMap gerado com sucesso" in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_run_generate_json_success() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "generate",
            "--frequency-ghz",
            "1.4",
            "--nside",
            "1",
            "--components",
            "synchrotron",
            "--output-format",
            "json",
        ],
        use_cases=make_dependencies(),
        stdout=stdout,
        stderr=stderr,
    )

    payload = json.loads(
        stdout.getvalue()
    )

    assert exit_code == 0
    assert payload["status"] == "success"
    assert payload["nside"] == 1
    assert payload["npix"] == 12
    assert stderr.getvalue() == ""


def test_run_returns_code_2_for_invalid_frequency() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "generate",
            "--frequency-ghz",
            "0",
            "--nside",
            "1",
            "--components",
            "synchrotron",
        ],
        use_cases=make_dependencies(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert (
        "frequency_ghz deve ser positiva"
        in stderr.getvalue()
    )


def test_run_returns_code_2_for_invalid_nside() -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "generate",
            "--frequency-ghz",
            "30",
            "--nside",
            "3",
            "--components",
            "dust",
        ],
        use_cases=make_dependencies(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "NSide" in stderr.getvalue()