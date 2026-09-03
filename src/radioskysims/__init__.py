"""
Módulo: src/radioskysims/__init__.py

Descrição:
    Pacote principal do projeto RadioSkySim (composition root).
    Sistema de simulação de radiotelescópios com modelagem de sinais,
    trajetórias de satélites, feixes de antena e interferências RFI.

    Expõe uma interface simples de configuração via :class:`Config` e uma
    fábrica de alto nível :func:`create_radiotelescope`.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

# Re-export dos tipos centrais do kernel no hub (UX Onda 3/R6):
#    from radioskysims import FrequencyRange, TimeRange, Observer
from radioskysims_core.domain.common import FrequencyRange, Observer, TimeRange
from radioskysims_core.paths import get_project_root

__version__ = "0.1.0"
__author__ = "RadioSkySim Team"


def create_radiotelescope(
    name: str = "default",
    *,
    settings_file: str | Path | None = None,
    **kwargs: Any,
) -> Any:
    """Cria um ``RadiotelescopeSpec`` de forma simples.

    Dois modos de uso:

    - **A partir do settings.toml** (perfil)::

          uirapuru = radioskysims.create_radiotelescope("uirapuru")
          uirapuru = radioskysims.create_radiotelescope(
              settings_file="data/settings/settings_fast.toml"
          )

    - **Direto por kwargs** (dict com as chaves necessárias de
      ``RadiotelescopeSpec``: ``name``, ``observer`` e ``antennas``)::

          from radioskysims_core.domain.common import Observer, TimeRange
          spec = radioskysims.create_radiotelescope(
              name="demo",
              observer=Observer(...),
              antennas=[...],
          )

    Args:
        name: Nome do perfil em ``[radiotelescopes.<name>]`` do settings.
        settings_file: Caminho alternativo de ``settings.toml``.
        **kwargs: Quando fornecidos, constrói o ``RadiotelescopeSpec``
            diretamente (ignora ``name``/``settings_file`` para o settings).

    Returns:
        ``RadiotelescopeSpec`` (radioskysims-radiotelescope).
    """
    if kwargs:
        from radioskysims_radiotelescope.domain.radiotelescope.specs import (
            RadiotelescopeSpec,
        )

        data = dict(kwargs)
        data.setdefault("name", name)
        return RadiotelescopeSpec(**data)

    from radioskysims_core.config.config_loader import (
        build_radiotelescope_from_settings,
    )

    return build_radiotelescope_from_settings(name, settings_file=settings_file)


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


__all__ = [
    "Config",
    "FrequencyRange",
    "Observer",
    "TimeRange",
    "create_radiotelescope",
]
