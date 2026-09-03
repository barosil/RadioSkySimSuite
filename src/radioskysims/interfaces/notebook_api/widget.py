"""\
Módulo: src/radioskysims/interfaces/notebook_api/widget.py

Descrição:
    Widget de progresso para notebooks (ticket TOD-007): um VBox ipywidgets
    que acompanha um ``JobHandle`` (barra de progresso, etapa, ETA e botão
    de cancelar) via polling em thread.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import threading
import time
from typing import Any

from radioskysims.interfaces.notebook_api.notebook import JobHandle

_FINAL_STATUSES = {"SUCCESS", "FAILED", "CANCELLED"}


def progress_widget(
    handle: JobHandle,
    *,
    interval: float = 2.0,
    title: str | None = None,
) -> Any:
    """Retorna um ipywidgets VBox que acompanha o progresso de um job.

    Requer ``ipywidgets`` instalado (levanta ImportError informativo caso
    contrário). O polling roda em uma thread daemon e para quando o job
    atinge um estado final.
    """
    try:
        import ipywidgets as widgets
    except ImportError:
        msg = (
            "ipywidgets não está instalado. Instale com "
            "`uv pip install ipywidgets` e reinicie o kernel."
        )
        raise ImportError(msg) from None

    title = title or f"TOD export (job {handle.job_id})"
    status_label = widgets.HTML(f"<b>{title}</b>")
    bar = widgets.FloatProgress(
        value=0,
        min=0,
        max=100,
        description="Progresso:",
        layout=widgets.Layout(width="100%"),
    )
    step_label = widgets.Label("Etapa: -")
    eta_label = widgets.Label("ETA: -")
    cancel_button = widgets.Button(
        description="Cancelar",
        disabled=False,
        button_style="danger",
    )
    stop = threading.Event()

    def _on_cancel(_btn: Any) -> None:
        handle.cancel()
        cancel_button.disabled = True
        status_label.value = f"<b>{title}</b> — cancelando..."

    cancel_button.on_click(_on_cancel)

    def _poll() -> None:
        while not stop.is_set():
            snap = handle.refresh()
            status = snap["status"]
            bar.value = float(snap["percent"])
            step_label.value = f"Etapa: {snap['step'] or '-'}"
            eta_label.value = f"ETA: {snap['eta'] or '-'}"
            status_label.value = f"<b>{title}</b> — {status}" if status else f"<b>{title}</b>"
            if status in _FINAL_STATUSES:
                cancel_button.disabled = True
                if status == "FAILED":
                    step_label.value = f"Etapa: falhou — {snap['error'] or 'erro'}"
                stop.set()
                return
            time.sleep(max(0.1, float(interval)))

    threading.Thread(target=_poll, daemon=True).start()
    return widgets.VBox([status_label, bar, step_label, eta_label, cancel_button])


__all__ = ["progress_widget"]
