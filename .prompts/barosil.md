# barosil.md — Documento-mestre de trabalho (RadioSkySimSuite)

> Este arquivo é o **registro único e corrente** do trabalho do agente `barosil`
> no meta-repo. Todo trabalho novo parte daqui. Atualizar **status/data** ao
> concluir itens. Documentos históricos de outras fases são referenciados, não
> duplicados.

## Como trabalhamos (regras de ouro)

- Branch de trabalho: **`dev`** (mantido limpo). Mudanças sempre em **branch
  própria** → PR → merge (submódulos primeiro, depois o meta com o bump do
  ponteiro).
- **Nada quebra**: suíte verde + lint antes de merge. Submódulos são repos
  próprios (`barosil/<pacote>`); cada mudança lá tem seu próprio branch/PR.
- Lançamento: PR `dev → main` (release). `main` ainda = baseline inicial.
- Código: hexagonal; docstrings; sem dataclass no domínio; xarray+dask lazy;
  pydantic/sqlmodel; PostgreSQL + HDF5/Zarr.
- Contexto técnico detalhado e atualizado em `/memories/repo/*` (importante
  consultar — contém pitfalls reais e APIs validadas).

## Snapshot — 2026-11-05

- `dev` (97b18d3): Base consolidada; 3 frentes ativas (F1 50%, F2 30%, F3 60%).
  Workspace `uv` funcional com 9 pacotes + umbrella; 91.340 LOC de produção;
  253 testes; lint limpo.
- Branches WIP: `feat/orchestrator-processor-dask` (simulation — notebooks 02/03),
  `feat/tod-map-notebooks`, `feat/waterfall-notebook`.
- Submódulos: todos em `main`, exceto `radioskysims-simulation` em
  `feat/orchestrator-processor-dask`.
- **Relatórios atualizados** (nov 5): `november_2026_audit_report.md`,
  `frentes_status_consolidado.md`, `metricas_tecnicas_2026.md`.
- Detalhes por frente: documentos de auditoria em `docs/audits/`.
- Próxima ação crítica: validação TOD 24h; merge de formatação/logging.

---

### Cronologia recente

| Data | Evento | Status |
|------|--------|--------|
| 2026-09-08 | Consolidação pós-desacoplamento; C1–C5 iniciados | Ref histórica |
| 2026-09-20 | C1–C4 concluídos; dev em bom estado | ✓ |
| 2026-10-15 | UIRAPURU 24h executado (primeiro teste); resultados em processamento | ✓ |
| 2026-10-30 | Bump de submódulos; preparação para release | 🟡 |
| 2026-11-02 | Teste de UIRAPURU com janela 24h (logs em `logs/`) | 🟡 |
| 2026-11-05 | **Auditoria consolidada e atualização de relatórios** | ← **Aqui agora** |

## Plano corrente — Consolidação F1/F2/F3 + Release (2026-11-05)

Objetivo: completar frentes de trabalho paralelas, atualizar documentação,
preparar release `dev → main` em dezembro.

| # | Tarefa | Detalhe | Status | Deadline |
|---|--------|---------|--------|----------|
| D1 | **Atualizar relatórios de auditoria** | Criar `november_2026_audit_report.md`, `frentes_status_consolidado.md`, `metricas_tecnicas_2026.md`. | `[x]` 2026-11-05 | — |
| F1a | **Consolidar UX — Logging JSON/humanizado** | R5: Separar logging estruturado (JSON) de output humano em CLI. Usar stderr para JSON, stdout para user. | `[ ]` | Nov 17 |
| F1b | **Consolidar UX — Progress bars** | R6: Adicionar `tqdm` ou similar em operações > 5s (TOD gen, export, mapmaking). | `[ ]` | Nov 17 |
| F1c | **Consolidar UX — README** | L1: "Getting started" com 3 exemplos mínimos. | `[ ]` | Nov 24 |
| F2a | **DDD — Mover logging de domain** | Move logger imports de `domain/*/services.py` para application. | `[ ]` | Nov 17 |
| F2b | **DDD — Refactoring orquestração** | Esquema DESIGN.md para decompor `sim_orchestrator.py` e `simulation.py`. | `[ ]` | Nov 24 |
| F2c | **Lint — Ruff format** | Branch `chore/formatting`; `ruff format src packages`. | `[ ]` | Nov 17 |
| F3a | **Ciência — TOD 24h** | Executar validação TOD 24h em hardware real. | `[ ]` | Nov 20 |
| F3b | **Ciência — Satélites auditoria** | Auditoria formal de propagação TLE e contribuição em rádio. | `[ ]` | Nov 30 |
| C6 | **Release dev→main** | PR com changelog F1/F2/F3; merge após aprovação. | `[ ]` | Dez 5 |

## Frentes de trabalho vigentes (referência)

- **F1 — UX entrypoints** · **F2 — dívida DDD/eng** · **F3 — evoluções
  científicas** → detalhamento e status em `notebooks/ux_entrypoints_audit.md`
  (O1.x/O2.x/O3.x, E1–E15, C1–C15, V1–V3). Este arquivo aponta para lá; não
  duplicar o conteúdo.
- Resíduos conhecidos fora desta rodada: waterfall com eventos; TLE vs RINEX;
  NVSS; banda completa PySM3.

## Indicadores de acompanhamento (definição)

- `[x]` entregue (com data) · `[~]` em andamento · `[ ]` pendente.
- Todo item vira **branch**; PRs fechados atualizam o marcador neste arquivo e o
  snapshot de status no topo.
