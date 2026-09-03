"""\
Módulo: src/radioskysims/interfaces/cli/commands/gui_cmd.py

Descrição:
    Comando ``radioskysims gui`` — abre a interface gráfica (Panel) do
    RadioSkySim (dashboard SkyMap) no navegador, via composition root
    ``radioskysims.bootstrap.skymap_gui``.

    Atende UX M2: expõe a GUI pelo umbrella com **um único comando**, sem o
    usuário precisar conhecer ``scripts/start_service.py``.

Copyright BINGO Collaboration
Last modified: 2026-09-03
"""

from __future__ import annotations


def execute_gui_command(*, show: bool = True) -> int:
    """Serve a GUI (Panel SkyMap) e retorna 0 quando o servidor encerra.

    Args:
        show: Abre o navegador automaticamente (repassado a ``pn.serve``
            pelo composition root; mantido para futuros controles).
    """
    _ = show  # o composition root abre o navegador por padrão (pn.serve show=True)
    from radioskysims.bootstrap.skymap_gui import main as skymap_gui_main

    skymap_gui_main()
    return 0


__all__ = ["execute_gui_command"]
