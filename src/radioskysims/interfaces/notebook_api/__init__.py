"""\
Módulo: src/radioskysims/interfaces/notebook_api/__init__.py

Descrição:
    API pública para notebooks: execução de simulações TOD (foreground/
    background) via ``run_simulation``/``JobHandle`` e widget de progresso
    (ticket TOD-007).

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from radioskysims.interfaces.notebook_api.notebook import (
    ExportResult,
    JobHandle,
    run_simulation,
)
from radioskysims.interfaces.notebook_api.widget import progress_widget

__all__ = ["ExportResult", "JobHandle", "progress_widget", "run_simulation"]
