"""
Módulo: src/radioskysims/__init__.py

Descrição:
    Pacote principal do projeto RadioSkySim.
    Sistema de simulação de radiotelescópios com modelagem de sinais,
    trajetórias de satélites, feixes de antena e interferências RFI.

    Também expõe uma interface simples de configuração via :class:`Config`,
    que lê o arquivo ``settings.toml`` na raiz do repositório.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from radioskysims_core.paths import get_project_root

__version__ = "0.1.0"
__author__ = "RadioSkySim Team"


class Config(dict):
    """Carrega configurações a partir de um arquivo TOML.

    Exemplos
    --------
    >>> from radioskysims import Config
    >>> cfg = Config()  # usa ``settings.toml`` na raiz do projeto
    >>> paths = cfg.get("paths", {})

    Também é possível indicar um caminho explícito::

        cfg = Config(file="settings.toml")

    O caminho informado é resolvido em relação à raiz do projeto,
    detectada por :func:`get_project_root`.
    """

    def __init__(self, file: str | Path | None = None) -> None:
        root = get_project_root()
        if file is None:
            path = root / "settings.toml"
        else:
            p = Path(file)
            path = p if p.is_absolute() else root / p

        if not path.exists():  # falha rápida com mensagem clara
            msg = f"Arquivo de configuração não encontrado: {path}"
            raise FileNotFoundError(msg)

        with path.open("rb") as f:
            data: dict[str, Any] = tomllib.load(f)

        super().__init__(data)
        self._path = path

    @property
    def path(self) -> Path:
        """Retorna o caminho absoluto do arquivo de configuração carregado."""

        return self._path
