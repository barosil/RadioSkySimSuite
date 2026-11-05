"""\
Módulo: src/radioskysims/interfaces/cli/commands/progress.py

Descrição:
    Padronização do progresso de jobs (ticket TOD-006). Formato JSON do
    arquivo ``<output>.progress.json``: ``{status, percent, step, eta,
    updated_at}`` (+ ``error`` em falha). Inclui escrita/leitura e cálculo
    de ETA linear aproximada.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


def progress_file_path(output: Path) -> Path:
    """Caminho do arquivo de progresso associado a um dataset."""
    return output.with_suffix(output.suffix + ".progress.json")


def estimate_eta(started_at: float, percent: float) -> str | None:
    """ETA linear (formato H:MM:SS) baseada no percentual concluído.

    Retorna ``None`` se o progresso ainda não começou (percent <= 0).
    """
    if percent <= 0.0:
        return None
    elapsed = max(0.0, time.monotonic() - started_at)
    total = elapsed * (100.0 / percent)
    remaining = max(0.0, total - elapsed)
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    seconds = int(remaining % 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def write_progress(
    path: Path,
    *,
    status: str,
    percent: float,
    step: str,
    started_at: float,
    error: str | None = None,
) -> None:
    """Grava o estado atual do job em um arquivo JSON de progresso."""
    payload: dict[str, object] = {
        "status": status,
        "percent": max(0.0, min(100.0, float(percent))),
        "step": step,
        "eta": estimate_eta(started_at, float(percent)),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    if error is not None:
        payload["error"] = error
    path.write_text(json.dumps(payload))


def read_progress(path: Path) -> dict[str, Any]:
    """Lê o arquivo de progresso; retorna {} se ausente ou corrompido."""
    if not path.exists():
        return {}
    try:
        return cast(dict[str, Any], json.loads(path.read_text()))
    except (json.JSONDecodeError, OSError):
        return {}


__all__ = [
    "estimate_eta",
    "progress_file_path",
    "read_progress",
    "write_progress",
]
