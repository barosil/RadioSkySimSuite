from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = PROJECT_ROOT / "src" / "radioskysims"


def test_legacy_beam_namespace_does_not_exist() -> None:
    legacy_package = SOURCE_ROOT / "beam"

    assert not legacy_package.exists(), (
        "O namespace legado src/radioskysims/beam não deve existir. "
        "Use radioskysims_beam.domain.beam."
    )


def test_source_code_does_not_import_legacy_beam_namespace() -> None:
    violations: list[str] = []

    for path in SOURCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "radioskysims.beam" or alias.name.startswith(
                        "radioskysims.beam."
                    ):
                        violations.append(f"{path}:{node.lineno}: import {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                if module == "radioskysims.beam" or module.startswith(
                    "radioskysims.beam."
                ):
                    violations.append(
                        f"{path}:{node.lineno}: from {module} import ..."
                    )

    assert not violations, (
        "Foram encontrados imports do namespace legado Beam:\n"
        + "\n".join(violations)
    )


def test_legacy_beam_visualizer_does_not_exist() -> None:
    legacy_visualizer = (
        PROJECT_ROOT
        / "src"
        / "radioskysims"
        / "interfaces"
        / "gui"
        / "beam_visualizer.py"
    )

    assert not legacy_visualizer.exists(), (
        "O visualizador Beam legado não deve ser recriado. "
        "Use beam_panel ou a futura GUI modular do Beam."
    )
