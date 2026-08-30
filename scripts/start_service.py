from __future__ import annotations

import sys
from pathlib import Path

import panel as pn

from radioskysims_simulation.application.tod_panel import TODPanel
from radioskysims_simulation.bootstrap.composition import create_sim_orchestrator

# Garante que o diretório raiz do projeto esteja no sys.path quando executado direto
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # pragma: no cover - apenas conveniência CLI
    sys.path.append(str(ROOT))


def main() -> None:
    """Entry point para iniciar uma simulação simples e abrir o visualizador TOD.

    Fluxo:
    1. Cria um :class:`SimOrchestrator` usando o ``settings.toml`` (telescope="default");
    2. Executa uma simulação para as constelações definidas em ``satellites.constellations``;
    3. Abre um painel interativo com o resultado (TOD).
    """

    orchestrator = create_sim_orchestrator(telescope="default")

    # Roda simulação usando defaults (constellations/time_range do settings)
    result = orchestrator.run()

    # Cria painel de visualização
    tod_panel = TODPanel(result)

    pn.serve(tod_panel, title="RadioSkySim - TOD Viewer", show=True)


if __name__ == "__main__":  # pragma: no cover
    main()
