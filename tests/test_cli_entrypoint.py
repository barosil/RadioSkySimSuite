from __future__ import annotations

import importlib
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_project_script_uses_generic_cli_bootstrap() -> None:
    """O console script principal deve apontar para o bootstrap genérico."""

    with (ROOT / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    scripts = pyproject["project"]["scripts"]

    assert scripts["radioskysims"] == "radioskysims.bootstrap.cli:main"


def test_generic_cli_bootstrap_is_importable() -> None:
    """O composition root oficial da CLI deve existir."""

    module = importlib.import_module("radioskysims.bootstrap.cli")

    assert callable(module.main)


def test_legacy_skymap_cli_remains_compatible() -> None:
    """O bootstrap antigo deve continuar disponível durante a transição."""

    legacy = importlib.import_module(
        "radioskysims.bootstrap.skymap_cli"
    )

    assert callable(legacy.main)


def test_python_module_cli_uses_generic_bootstrap() -> None:
    """python -m radioskysims.interfaces.cli deve usar o bootstrap oficial."""

    path = (
        ROOT
        / "src"
        / "radioskysims"
        / "interfaces"
        / "cli"
        / "__main__.py"
    )

    source = path.read_text(encoding="utf-8")

    assert (
        "from radioskysims.bootstrap.cli import main"
        in source
    )
