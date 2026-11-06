"""Compatibilidade para o antigo entrypoint da CLI de SkyMap.

O composition root oficial da CLI umbrella do RadioSkySim vive em
``radioskysims.bootstrap.cli``.

Este módulo permanece como alias temporário para não quebrar imports
existentes.
"""

from __future__ import annotations

from collections.abc import Sequence

from radioskysims.bootstrap.cli import (
    build_continuum_survey_use_case,
    build_skymap_cli_use_cases,
    main as _main,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a CLI umbrella mantendo compatibilidade com o import legado."""
    return _main(argv)


__all__ = [
    "build_continuum_survey_use_case",
    "build_skymap_cli_use_cases",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
