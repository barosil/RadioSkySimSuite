from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_PREFIXES = (
    "radioskysims.infrastructure",
    "pysm3",
    "healpy",
    "reproject",
    "astropy.io.fits",
)


def test_gui_has_no_forbidden_imports() -> None:
    base = Path("src/radioskysims/interfaces/gui/skymap")
    violations: list[str] = []

    for file_path in sorted(base.glob("*.py")):
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module_name = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    for forbidden in FORBIDDEN_PREFIXES:
                        if module_name == forbidden or module_name.startswith(f"{forbidden}."):
                            violations.append(f"{file_path}: {module_name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
                for forbidden in FORBIDDEN_PREFIXES:
                    if module_name == forbidden or module_name.startswith(f"{forbidden}."):
                        violations.append(f"{file_path}: {module_name}")

    assert not violations, "Imports proibidos encontrados:\n" + "\n".join(violations)