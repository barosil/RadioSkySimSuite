from __future__ import annotations

import json
from collections.abc import Sequence

import numpy as np

from radioskysims_skymap.application.skymap.generate import (
    GenerateSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.ports import (
    SkyMapGeneratorPort,
)
from radioskysims_skymap.domain.skymap import NSide, SkyMap
from radioskysims.interfaces.cli.commands.generate_skymap import (
    execute_generate_command,
)


class FakeSkyMapGenerator(
    SkyMapGeneratorPort
):
    """Gerador fake sem dependências científicas externas."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        *,
        nside: NSide,
        freq_ghz: float,
        components: Sequence[str] | None = None,
    ) -> SkyMap:
        self.calls.append(
            {
                "nside": nside,
                "freq_ghz": freq_ghz,
                "components": tuple(
                    components or ()
                ),
            }
        )

        data = np.arange(
            nside.npix,
            dtype=np.float64,
        )

        return SkyMap(
            dataset=data,
            nside=nside,
            unit="uK_CMB",
            frame="galactic",
            freq_ghz=freq_ghz,
            field="I",
        )


def make_use_case() -> tuple[
    GenerateSkyMapUseCase,
    FakeSkyMapGenerator,
]:
    generator = FakeSkyMapGenerator()

    return (
        GenerateSkyMapUseCase(
            generator=generator,
        ),
        generator,
    )


def test_execute_generate_command_text() -> None:
    use_case, generator = make_use_case()

    result = execute_generate_command(
        use_case=use_case,
        frequency_ghz=30.0,
        nside=1,
        components=(
            "synchrotron",
            "dust",
        ),
        output_format="text",
    )

    assert "SkyMap gerado com sucesso" in result
    assert "NSide: 1" in result
    assert "Número de pixels: 12" in result
    assert "Frequência: 30.0 GHz" in result
    assert "synchrotron, dust" in result

    assert generator.calls == [
        {
            "nside": NSide(1),
            "freq_ghz": 30.0,
            "components": (
                "synchrotron",
                "dust",
            ),
        }
    ]


def test_execute_generate_command_json() -> None:
    use_case, _ = make_use_case()

    result = execute_generate_command(
        use_case=use_case,
        frequency_ghz=1.4,
        nside=1,
        components=("synchrotron",),
        output_format="json",
    )

    payload = json.loads(result)

    assert payload == {
        "status": "success",
        "command": "skymap.generate",
        "nside": 1,
        "npix": 12,
        "frequency_ghz": 1.4,
        "components": ["synchrotron"],
        "dtype": "float64",
    }