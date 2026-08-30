"""\
Módulo: src/radioskysims/interfaces/api/__init__.py

Descrição:
    API pública para notebooks: execução de simulações TOD (foreground/
    background) via ``run_simulation``/``JobHandle`` e widget de progresso
    (ticket TOD-007).

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from radioskysims.interfaces.api.notebook import JobHandle, run_simulation
from radioskysims.interfaces.api.widget import progress_widget

__all__ = ["JobHandle", "progress_widget", "run_simulation"]
