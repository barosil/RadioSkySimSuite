"""Composition Root oficial para montagem da aplicacao.

A partir da Fase 5, delega para ``radioskysims_simulation.bootstrap.composition``
(o ciclo lazy ``sim_orchestrator ↔ composition`` foi quebrado movendo o
composition root de simulação para o pacote).
"""

from __future__ import annotations

from radioskysims_simulation.bootstrap.composition import (
    create_sim_orchestrator,
    create_simulation_context,
)

__all__ = ["create_sim_orchestrator", "create_simulation_context"]
