from __future__ import annotations

import json
from collections.abc import Sequence
from io import StringIO
from pathlib import Path

import numpy as np

from radioskysims_skymap.application.skymap.analyze import (
    AnalyzeSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.generate import (
    GenerateSkyMapUseCase,
)
from radioskysims_skymap.application.skymap.ports import (
    SkyMapAnalyzerPort,
    SkyMapGeneratorPort,
)
from radioskysims_skymap.domain.skymap import NSide, SkyMap
from radioskysims_skymap.domain.skymap.exceptions import (
    AnalysisError,
)
from radioskysims.interfaces.cli.commands.analyze_skymap import (
    execute_analyze_command,
)
from radioskysims.interfaces.cli.main import (
    SkyMapCLIUseCases,
    run,
)


class FakeSkyMapReader:
    """Leitor fake que não acessa arquivos reais."""

    def __init__(
        self,
        *,
        result: SkyMap | None = None,
        error: Exception | None = None,
    ) -> None:
        self._result = result or make_skymap()
        self._error = error
        self.calls: list[dict[str, object]] = []

    def read_map(
        self,
        path: str | Path,
        *,
        nside: NSide | None = None,
        unit: str = "unknown",
        frame: str = "galactic",
        field: str = "I",
    ) -> SkyMap:
        self.calls.append(
            {
                "path": Path(path),
                "nside": nside,
                "unit": unit,
                "frame": frame,
                "field": field,
            }
        )

        if self._error is not None:
            raise self._error

        source = self._result

        return SkyMap(
            dataset=source.data,
            nside=source.nside,
            unit=unit,
            frame=frame,
            freq_ghz=source.freq_ghz,
            field=field,
        )


class FakeSkyMapAnalyzer(SkyMapAnalyzerPort):
    """Analyzer fake com resultado determinístico."""

    def __init__(
        self,
        *,
        result: np.ndarray | None = None,
        error: Exception | None = None,
    ) -> None:
        self._result = (
            result
            if result is not None
            else np.array(
                [1.0, 2.0, 3.0, 4.0, 5.0],
                dtype=np.float64,
            )
        )
        self._error = error
        self.calls: list[dict[str, object]] = []

    def compute_cls(
        self,
        *,
        skymap: SkyMap,
        lmax: int | None = None,
    ) -> np.ndarray:
        self.calls.append(
            {
                "skymap": skymap,
                "lmax": lmax,
            }
        )

        if self._error is not None:
            raise self._error

        return self._result.copy()


class FakeGenerator(SkyMapGeneratorPort):
    """Dependência mínima exigida pela estrutura atual da CLI."""

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


def make_skymap() -> SkyMap:
    return SkyMap(
        dataset=np.arange(
            12,
            dtype=np.float64,
        ),
        nside=NSide(1),
        unit="uK_CMB",
        frame="galactic",
        field="I",
    )


def make_dependencies(
    *,
    reader: FakeSkyMapReader | None = None,
    analyzer: FakeSkyMapAnalyzer | None = None,
) -> SkyMapCLIUseCases:
    resolved_reader = reader or FakeSkyMapReader()
    resolved_analyzer = analyzer or FakeSkyMapAnalyzer()

    return SkyMapCLIUseCases(
        generate_skymap=GenerateSkyMapUseCase(
            generator=FakeGenerator(),
        ),
        analyze_skymap=AnalyzeSkyMapUseCase(
            analyzer=resolved_analyzer,
        ),
        skymap_reader=resolved_reader,
    )


def test_execute_analyze_command_text() -> None:
    reader = FakeSkyMapReader()
    analyzer = FakeSkyMapAnalyzer()

    result = execute_analyze_command(
        use_case=AnalyzeSkyMapUseCase(
            analyzer=analyzer,
        ),
        reader=reader,
        input_path=Path("map.fits"),
        lmax=4,
        unit="uK_CMB",
        frame="galactic",
        field="I",
        output_format="text",
    )

    assert "Análise espectral concluída" in result
    assert "Arquivo: map.fits" in result
    assert "NSide: 1" in result
    assert "Número de pixels: 12" in result
    assert "lmax: 4" in result
    assert "Quantidade de coeficientes Cℓ: 5" in result
    assert "Cℓ mínimo: 1.0" in result
    assert "Cℓ máximo: 5.0" in result
    assert "Cℓ médio: 3.0" in result

    assert len(reader.calls) == 1
    assert len(analyzer.calls) == 1
    assert analyzer.calls[0]["lmax"] == 4


def test_execute_analyze_command_json() -> None:
    reader = FakeSkyMapReader()
    analyzer = FakeSkyMapAnalyzer()

    result = execute_analyze_command(
        use_case=AnalyzeSkyMapUseCase(
            analyzer=analyzer,
        ),
        reader=reader,
        input_path=Path("map.fits"),
        lmax=4,
        unit="uK_CMB",
        frame="galactic",
        field="I",
        output_format="json",
    )

    payload = json.loads(result)

    assert payload == {
        "status": "success",
        "command": "skymap.analyze",
        "input": "map.fits",
        "nside": 1,
        "npix": 12,
        "unit": "uK_CMB",
        "frame": "galactic",
        "field": "I",
        "lmax": 4,
        "cls_length": 5,
        "cls_min": 1.0,
        "cls_max": 5.0,
        "cls_mean": 3.0,
        "dtype": "float64",
    }


def test_run_analyze_text_success() -> None:
    reader = FakeSkyMapReader()
    analyzer = FakeSkyMapAnalyzer()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "analyze",
            "--input",
            "map.fits",
            "--lmax",
            "4",
            "--unit",
            "uK_CMB",
            "--frame",
            "galactic",
            "--field",
            "I",
        ],
        use_cases=make_dependencies(
            reader=reader,
            analyzer=analyzer,
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert "Análise espectral concluída" in stdout.getvalue()
    assert "Quantidade de coeficientes Cℓ: 5" in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_run_analyze_json_success() -> None:
    reader = FakeSkyMapReader()
    analyzer = FakeSkyMapAnalyzer()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "analyze",
            "--input",
            "map.fits",
            "--lmax",
            "4",
            "--unit",
            "uK_CMB",
            "--frame",
            "galactic",
            "--field",
            "I",
            "--output-format",
            "json",
        ],
        use_cases=make_dependencies(
            reader=reader,
            analyzer=analyzer,
        ),
        stdout=stdout,
        stderr=stderr,
    )

    payload = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert payload["status"] == "success"
    assert payload["command"] == "skymap.analyze"
    assert payload["nside"] == 1
    assert payload["npix"] == 12
    assert payload["lmax"] == 4
    assert payload["cls_length"] == 5
    assert stderr.getvalue() == ""


def test_run_analyze_returns_code_2_for_invalid_lmax() -> None:
    reader = FakeSkyMapReader()
    analyzer = FakeSkyMapAnalyzer()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "analyze",
            "--input",
            "map.fits",
            "--lmax",
            "0",
        ],
        use_cases=make_dependencies(
            reader=reader,
            analyzer=analyzer,
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 2
    assert stdout.getvalue() == ""
    assert "lmax deve ser positivo" in stderr.getvalue()
    assert analyzer.calls == []


def test_run_analyze_returns_code_3_for_missing_file() -> None:
    reader = FakeSkyMapReader(
        error=FileNotFoundError("map.fits"),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "analyze",
            "--input",
            "map.fits",
        ],
        use_cases=make_dependencies(
            reader=reader,
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 3
    assert stdout.getvalue() == ""
    assert "Arquivo não encontrado" in stderr.getvalue()


def test_run_analyze_returns_code_5_for_analysis_error() -> None:
    analyzer = FakeSkyMapAnalyzer(
        error=AnalysisError(
            "falha no cálculo do espectro"
        ),
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        [
            "skymap",
            "analyze",
            "--input",
            "map.fits",
            "--lmax",
            "4",
        ],
        use_cases=make_dependencies(
            analyzer=analyzer,
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 5
    assert stdout.getvalue() == ""
    assert "Falha de análise" in stderr.getvalue()
    assert (
        "falha no cálculo do espectro"
        in stderr.getvalue()
    )
    