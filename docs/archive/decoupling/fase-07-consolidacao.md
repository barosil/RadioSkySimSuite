# Fase 7 — Consolidação / meta-pacote / limpeza de shims

## Objetivo

Consolidar o ecossistema de pacotes no meta-pacote `radioskysim`, remover os
**shims de compatibilidade** (imports antigos `radioskysims.* → pacote novo`),
atualizar documentação e rodar o gate final de regressão/cobertura.

## O que foi feito

| Item | Descrição |
|---|---|
| **Integração `radioskysims-waterfall`** | Repo criado (`github.com/barosil/radioskysims-waterfall`), registrado como submódulo, adicionado ao `[project.dependencies]`, extras `waterfall` e `all`, `[tool.uv.sources]` e `[tool.coverage.run].source`. Pyproject alinhado ao padrão do workspace (hatch-vcs, `requires-python` com limite superior, `[project.urls]`). |
| **Remoção de shims** | 207 arquivos `src/radioskysims/**` com docstring "Shim de compatibilidade" removidos via `git rm`. O meta-pacote passou de ~251 para **44 arquivos**. |
| **Migração de imports** | Script de migração (`/tmp/migrate_shims.py`) reescreveu imports absolutos; correção manual de imports relativos em `application/ports/__init__.py`, `infrastructure/db/{models,init_db}.py`, `infrastructure/processing/__init__.py`, `src/radioskysims/__init__.py` (`get_project_root` → `radioskysims_core.paths`), `packages/radioskysims-core/domain/tracks/factory.py` e `tests/test_logging_integration.py`. |
| **Teste realocado** | `TestSimulationContext::test_sort_sources_by_ra` (importava `radioskysims.domain.simulation` — shim) movido de `packages/radioskysims-sources/tests/domain/source/test_source.py` para `packages/radioskysims-simulation/tests/domain/simulation/test_simulation_context.py` (a classe pertence ao domínio de simulation, que já depende de sources). |
| **Configs de qualidade** | `[tool.coverage.run].source` ganhou `radioskysims_simulation` e `radioskysims_waterfall`. Mypy (`files = ["src","tests","packages"]`) e ruff já cobrem os pacotes. |
| **Documentação** | `docs/architecture.md` atualizado: seção 1.1 "Ecossistema de pacotes (uv workspace)" com diagrama Mermaid de dependências entre os 9 pacotes + umbrella, `Waterfall` nos bounded contexts, seção de diagramas. `AGENTS.md` criado na raiz com a convenção de layout. |
| **Docs de decoupling** | `fase-06-radioskysims-waterfall.md` (Fase 6) e `fase-07-consolidacao.md` (esta); `README.md` atualizado (status ✅ e tabela de submódulos). |

## Shims: o que foi preservado no meta-pacote

Após a remoção, `src/radioskysims/` mantém apenas código real:

- `bootstrap/` (composition root: `builders.py` fino, `composition.py`, CLI/GUI)
- `interfaces/` (CLI de skymap, GUI de skymap)
- `main.py`, `visualization/waterfall.py`, `application/gain_panel.py`
- `infrastructure/db/{models,init_db}.py`, `infrastructure/ports/*`,
  `infrastructure/processing/__init__.py`, `infrastructure/utils/lazy.py`
- `domain/map/` (stub fora de escopo — designado a outro colaborador)
- `src/GNSStools4Astro`, `src/analysis`, `src/bingo`, `src/arpls` (vendorizados)

## Verificação (gate da fase)

```bash
uv run pytest tests -q --ignore=tests/performance          # → 207 passed, 3 skipped
uv run --package radioskysims-core pytest ...              # → 88 passed
uv run --package radioskysims-viz pytest ...               # → 5 passed
uv run --package radioskysims-beam pytest ...              # → 55 passed
uv run --package radioskysims-skymap pytest ...            # → 325 passed
uv run --package radioskysims-sources pytest ...           # → 164 passed, 1 xfailed
uv run --package radioskysims-simulation pytest ...        # → 283 passed
uv run --package radioskysims-waterfall pytest ...         # → 133 passed
uv run --package gnsstools4astro pytest ...                # → 21 passed, 9 skipped
```

- `import radioskysims` OK (meta-pacote fino).
- Diagrama Mermaid do ecossistema validado (`mermaid-diagram-validator`) e
  pré-visualizado (`mermaid-diagram-preview`).

## Observações / pendências pós-Fase 7

- `radioskysims-radiotelescope` **não tem testes dedicados** (estado herdado da
  Fase 4; cobertura via orchestrators na raiz). Criar `packages/radioskysims-radiotelescope/tests/`
  fica como melhoria futura.
- Notebooks (`notebooks/`) podem ainda referenciar caminhos antigos; não fazem
  parte do gate pytest. Migração fica como tarefa de manutenção.
- `ruff` apresenta erros **pré-existentes** no código real do meta-pacote
  (`visualization/waterfall.py`, `interfaces/*`); não foram introduzidos nesta
  fase e ficam como dívida técnica.
- Shims **removidos definitivamente** (sem ciclo de depreciação adicional) —
  decisão do usuário em 2026-08-29.
