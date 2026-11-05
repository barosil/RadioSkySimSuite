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

## Plano corrente — Execução Intensiva 2 Semanas (2026-11-05 a 2026-11-17)

**Documento principal:** [`PLANO_EXECUCAO_NOV_2026.md`](./PLANO_EXECUCAO_NOV_2026.md)

Objetivo: 9 branches paralelas atacando dívida técnica (T1), qualidade (T2) e F1 UX completo (T3).
Timeline: 2 semanas intensivas (nov 5–17). Saída: dev 100% verde + 1 release-ready.

**Branches:**

| # | Branch | Foco | Esforço | Deps | Status |
|---|--------|------|---------|------|--------|
| B1 | `fix/td-001-application-infrastructure-ports` | Ports + DI (application→infrastructure) | 30h | — | 🟡 Ativo |
| B2 | `fix/td-002-domain-infrastructure-boundaries` | Domain puro (infraestrutura fora) | 18h | B1 | 🟡 Ativo |
| B3 | `fix/td-003-domain-application-inversion` | Aliases compatibilidade | 4h | — | 🟡 Ativo |
| B4 | `chore/ruff-format-complete` | 100% formatação ruff | 2.5h | — | 🟡 Ativo |
| B5 | `chore/type-hints-coverage-expansion` | Type hints 75%+ + mypy CI | 17h | B4 | 🟡 Ativo |
| B6 | `fix/f1-startup-noise-and-defaults` | Ruído startup + defaults | 3h | — | 🟡 Ativo |
| B7 | `fix/f1-silent-failures-and-consistency` | Erros claros, exit codes, unidades | 9h | — | 🟡 Ativo |
| B8 | `feat/f1-output-formatting-and-progress` | Cores, tabelas, progress bars, logging | 16h | B7 | 🟡 Ativo |
| B9 | `docs/f1-getting-started-and-reference` | README, docstrings, FAQ | 7h | — | 🟡 Ativo |

**Sequência de merge:** B4 → B6 → B1 → B7 → B2 → B8 → B5 → B3 → B9 (respeitar deps)

**Critério de sucesso:** Todas 9 branches em dev; 100% testes verde; 0 lint; type hints 75%+; CLI 100% F1.

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
