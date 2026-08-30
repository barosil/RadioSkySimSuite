from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    import tomllib as _toml_load
except Exception:  # pragma: no cover - fallback for older Pythons
    try:
        import tomli as _toml_load
    except Exception:  # pragma: no cover
        _toml_load = None


DEFAULT_FILENAMES = ["settings.toml", "settings_01.toml"]


def resolve_settings(path_or_name: Optional[str] = None) -> Path:
    """Resolve o arquivo de settings a usar.

    Ordem de resolução (primeira que existir):
      1. argumento `path_or_name` se for um caminho de arquivo existente
      2. variável de ambiente `RADIOSKYSIM_SETTINGS` (path)
      3. se `path_or_name` dado e não existir como arquivo, tenta resolver
         como nome "named toml" em `config/` (ex: `config/name.toml`).
      4. procura no diretório da workspace por `settings.toml` e `settings_01.toml`.

    Levanta FileNotFoundError se nada for encontrado.
    """
    # 1) argumento explícito como caminho
    if path_or_name:
        p = Path(path_or_name)
        if p.exists() and p.is_file():
            return p

    # 2) variável de ambiente
    env_path = os.environ.get("RADIOSKYSIM_SETTINGS")
    if env_path:
        p = Path(env_path)
        if p.exists() and p.is_file():
            return p

    # 3) named toml in config/
    if path_or_name:
        candidate = Path("config") / f"{path_or_name}.toml"
        if candidate.exists() and candidate.is_file():
            return candidate

    # 4) default filenames in repo root
    repo_root = Path.cwd()
    for name in DEFAULT_FILENAMES:
        candidate = repo_root / name
        if candidate.exists() and candidate.is_file():
            return candidate

    msg = "Could not resolve settings.toml. Provide a path or set RADIOSKYSIM_SETTINGS."
    raise FileNotFoundError(
        msg
    )


def load_settings(path: Optional[str] = None) -> dict:
    """Load and parse TOML settings returning a dict.

    If `path` is None, resolve with `resolve_settings`.
    """
    if _toml_load is None:
        msg = "No TOML parser available: install tomli (for Python<3.11) or use Python 3.11+."
        raise RuntimeError(
            msg
        )

    p = resolve_settings(path)
    with p.open("rb") as fh:
        data = _toml_load.load(fh)
    return data


def validate_settings(settings: dict) -> None:
    """Quick validation of minimal required sections for TOD runs.

    Levanta ValueError em caso de inválido. Mantém escopo pequeno — validar campos
    essenciais: `time_range`, `frequency_range` e `output`.
    """
    if not isinstance(settings, dict):
        msg = "settings must be a mapping"
        raise ValueError(msg)

    if "time_range" not in settings:
        msg = "missing 'time_range' in settings"
        raise ValueError(msg)
    tr = settings["time_range"]
    if not all(k in tr for k in ("start", "end", "cadence")):
        msg = "time_range must include start, end and cadence"
        raise ValueError(msg)

    if "frequency_range" not in settings:
        msg = "missing 'frequency_range' in settings"
        raise ValueError(msg)

    if "output" not in settings:
        msg = "missing 'output' section (e.g. outdir, format)"
        raise ValueError(msg)


__all__ = ["resolve_settings", "load_settings", "validate_settings"]
