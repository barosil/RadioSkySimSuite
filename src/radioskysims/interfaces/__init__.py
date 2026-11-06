"""
Interfaces de usuário para RadioSkySim.

Inclui CLI, API REST (notebook_api) e GUI.

E11 (TD-013): este pacote não reexporta adapters concretos — apenas
subpacotes de interface (cli/, notebook_api/, etc.). Contratos/fachadas
públicos vivem nos próprios pacotes (radioskysims_* ) e no hub
``radioskysims.__init__``.
"""
