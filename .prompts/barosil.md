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

## Snapshot — 2026-09-08

- `dev` (186e2c2): UX Ondas 1–3 (F1) + série E (F2, E1–E14) + notebooks 00/01/02
  migrados p/ API de alto nível. `main` = baseline (release dev→main pendente).
- HEAD local: `feat/orchestrator-processor-dask` = dev + finalização 02_sims +
  showcase 03_waterfall; **WIP** no submódulo simulation (expor
  `ResourceAwareProcessor` na API pública + testes de processor/dask movidos p/
  dentro do pacote).
- Submódulos: todos em `main` atualizados, exceto `radioskysims-simulation` em
  `feat/orchestrator-processor-dask` (com WIP).
- Detalhes/pendências por frente: ver `notebooks/ux_entrypoints_audit.md`
  (plano F1/F2/F3, com status `[x]`/`[~]`/`[ ]`).

## Plano corrente — Consolidação de documentação e higiene (2026-09-08)

Objetivo: deixar só **trabalho corrente** na árvore, com rastreio único e
localizações corretas de artefatos.

| # | Tarefa | Detalhe | Status |
|---|--------|---------|--------|
| C1 | **Todo único com breakdown + indicadores** | Este arquivo (`.prompts/barosil.md`) é o todo-mestre; itemizado com indicador `[x]/[~]/[ ]` + data. | `[x]` criado 2026-09-08 |
| C2 | **Remover `docs/TODO_DOCS.md` e unificar** | Conteúdo (33 l.) já realizado → superado pela doc atual (`docs/architecture/*`). Removido; sem perda. | `[x]` removido 2026-09-08 |
| C3 | **Remover decoupling documentando o que passou/falta** | Fases 0–7 + planos movidos para **`docs/archive/decoupling/`** (histórico preservado); referências atualizadas (AGENTS.md, docs/source). Trabalho corrente vive em `.prompts/barosil.md` + `notebooks/ux_entrypoints_audit.md` (F1/F2/F3). | `[x]` arquivado 2026-09-08 |
| C4 | **Auditar `docs/audits/` (manter só corrente)** | Mantidos os 6 relatórios `.md` que alimentam F2/F3; removidos dumps `.txt` exploratórios (rastreados no git → recuperáveis). | `[x]` 2026-09-08 |
| C5 | **Corrigir localizações plots/dados** | Parar de gravar em `plots/` (raiz) e `notebooks/data/`; padronizar saída em `data/` (raiz) e `notebooks/plots/` — **independência de CWD no código** (viz/PathManager/notebooks) + reconciliar duplicatas. | `[ ]` (próximo branch) |
| C6 | **Release dev→main** (fase seguinte, após C1–C5) | PR dev→main com dev limpo; release inicial. | `[ ]` (fora desta rodada) |

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
