# Pontos de Entrada do Projeto - RadioSkySim

Data: 2026-07-16
Escopo: src/radioskysims e scripts/

## Classificacao de estado
- Oficial: ponto de entrada recomendado para uso corrente.
- Experimental: util para desenvolvimento/prototipo, sem compromisso forte de estabilidade.
- Legado: ainda presente por compatibilidade, mas nao recomendado para novos fluxos.
- Obsoleto: inconsistente com a arquitetura atual ou com alto risco de falha.

## Entrypoints identificados

| Localizacao | Finalidade | Estado | Recomendacao |
|---|---|---|---|
| src/radioskysims/main.py | Inicializa simulacao e abre visualizador Panel com fluxo satellite manager antigo | Obsoleto | Nao usar como referencia de bootstrap. Substituir por composition root unico em interfaces na Fase 2. |
| scripts/start_service.py | Inicia simulacao via SimOrchestrator e abre TODPanel | Oficial | Manter como entrypoint operacional atual de GUI/TOD de baixo atrito. |
| src/radioskysims/application/tod_panel.py (bloco main) | Servidor Panel minimo para uso manual do TODPanel | Experimental | Manter apenas como modo de desenvolvimento local; evitar uso como bootstrap principal. |
| src/radioskysims/application/beam_panel.py (bloco main) | Painel interativo de beam para exploracao manual | Experimental | Tratar como ferramenta de exploracao, sem garantia de API estavel. |
| src/radioskysims/application/gain_panel.py (bloco main) | Painel de ganho sintetico para visualizacao | Experimental | Manter para estudo/manual; nao usar como entrypoint produtivo. |
| src/radioskysims/application/radiotelescope_panel.py (bloco main) | Painel de configuracao de radiotelescopio via Panel | Experimental | Manter para prototipacao; consolidar com composition root em Interfaces depois. |
| src/radioskysims/interfaces/cli/generate.py (funcao main) | CLI para gerar sky map via argparse | Experimental | Tornar executavel explicito por modulo/script dedicado e documentar parametros oficiais. |
| src/radioskysims/domain/satellite/main.py | Tentativa de app FastAPI no pacote de dominio | Obsoleto | Nao utilizar. Mover/remover na Fase 3 por violar separacao de camadas. |
| src/radioskysims/infrastructure/db/init_db.py (bloco main) | Inicializacao de schema de banco via SQLModel async | Oficial | Manter como utilitario de infraestrutura para setup de ambiente. |
| src/radioskysims/infrastructure/config/config_loader.py (bloco main) | Exemplo manual de carga de configuracao | Legado | Tratar como exemplo interno; evitar divulgar como entrypoint de execucao. |
| scripts/check_docs.py | Verificador de docstrings e type hints no codigo | Oficial | Manter como ferramenta de qualidade para dev e CI local. |

## Observacoes de estabilizacao para Fase 2

1. O projeto possui multiplos entrypoints de desenvolvimento, mas poucos com status operacional claro.
2. O entrypoint mais seguro para uso corrente e scripts/start_service.py.
3. O caminho em domain/satellite/main.py deve ser explicitamente marcado como obsoleto por violar a fronteira de camadas.
4. Durante a Fase 2, manter compatibilidade e apenas documentar status, sem alterar regras de negocio.
