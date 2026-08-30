# Roadmap — Próximos Passos (RadioSkySim)

**Data:** 2026-08-04
**Base:** `docs/architecture/refactoring_roadmap.md` (refatoração arquitetural),
`docs/code_quality.md` (qualidade), `docs/architecture/technical_debt.md`.

O roadmap organiza o trabalho em **4 trilhas**: Segurança & Infra, Qualidade,
Arquitetura, e Ciência/Produto.

---

## Trilha A — Segurança & Infra (P0)

> Objetivo: eliminar riscos imediatos e estabilizar o ambiente de desenvolvimento.

| # | Item | Detalhe |
|---|---|---|
| A1 | **Rotacionar credencial SpaceTrack** | `settings.toml [SPACETRACK]` contém senha real. Rotacionar e mover para `credentials.env`/env vars; atualizar `.gitignore`. |
| A2 | **Tratar vulnerabilidades** | Triar as 226 (1 critical, 88 high) do Dependabot — issue **#52**. |
| A3 | **CI básica** | GitHub Actions: `ruff check` + `pytest` + badge de coverage. |
| A4 | **Dependabot** | Habilitar auto-merge para atualizações de patch/segurança. |
| A5 | **Permissões do volume** | `data/DB` inacessível para leitura em alguns comandos — revisar ownership do volume Postgres. |

**Saída:** nenhuma credencial versionada; critical/high zeradas; CI verde.

## Trilha B — Qualidade de código (P1)

> Objetivo: reduzir dívida de lint e fechar lacunas de teste.

| # | Item | Detalhe |
|---|---|---|
| B1 | **Lint auto-fix** | `ruff check --fix` (130 fixes) + revisão manual. |
| B2 | **EM101 / PLC0415** | Tratar `raw-string-in-exception` (140) e imports fora do topo (127) em lotes por camada. |
| B3 | **Cobertura** | `pytest --cov=radioskysims` e fechar lacunas: `domain/rfi`, `domain/noise`, `interfaces/api`. |
| B4 | **Logging** | Substituir f-strings em logging (G004) por args estruturados. |
| B5 | **Notebooks** | Manter auditoria: promover notebooks de `_archive` de volta quando corrigidos. |

**Saída:** ruff ≤ 100 erros; cobertura ≥ 60% nas camadas principais.

## Trilha C — Arquitetura (P2, seguir `refactoring_roadmap.md`)

> Objetivo: restaurar a separação hexagonal de forma segura (baixo risco primeiro).

| # | Item | Fase |
|---|---|---|
| C1 | Contenção imediata (compila + entrypoint oficial) | F0 |
| C2 | Higiene de API pública (controllers, `interfaces/__init__`) | F1 |
| C3 | Ports + composition root (application sem infrastructure) | F2 |
| C4 | Blindagem do domínio (domain sem infra/application) | F3 |
| C5 | Consolidar adapters/namespaces de beam | F4 |
| C6 | Fatiar módulos grandes (simulation_service, domain/common) | F5 |

**Saída:** dependências de camada validadas por ferramenta (ex.: `dependency-cruiser`
/ arquitetura-check no CI).

## Trilha D — Ciência / Produto (contínua)

> Objetivo: avançar nos casos de uso científicos já suportados.

| # | Item | Contexto |
|---|---|---|
| D1 | **TOD end-to-end** | Consolidar pipeline 50_TOD: processamento batch, persistência (HDF5/Zarr + Postgres), `shutdown()` do dask distribuído. |
| D2 | **SkyMap** | Expandir `skymap_howto`: integração HiPS/PySM3, survey contínuo, CLI. |
| D3 | **Satélites** | Curar TLEs (SpaceTrack), validação de tracks contra ephemeris. |
| D4 | **Beam** | Unificar loaders; validar `BeamFactory` end-to-end com dados reais do BINGO. |
| D5 | **RFI / Noise** | Modelos de RFI e ruído (pysm3) — fechar testes. |
| D6 | **Catálogos** | Automatizar ingestão NVSS/Specfind via TAP; cache em `data/catalog`. |
| D7 | **GUI/API** | TodPanel + FastAPI: expor resumos persistidos (`SimulationRepository`). |

## Indicadores de sucesso (mensuráveis)

- [ ] 0 credenciais versionadas; 0 vulns critical/high.
- [ ] CI verde (lint + testes) em todo PR para `dev`.
- [ ] `ruff check` < 100 erros.
- [ ] Cobertura de testes ≥ 60%.
- [ ] `domain` sem imports de `application`/`infrastructure` (gate automatizado).
- [ ] Notebooks oficiais executam de ponta a ponta sem erros.

## Ordem recomendada

1. **Trilha A** (P0) → base segura.
2. **Trilha B + C1** (qualidade + contenção) → higiene rápida.
3. **Trilha C (C2–C6)** → arquitetura, em paralelo com a **Trilha D** científica.
4. Revisitar este documento a cada sprint.

---

Referências: `docs/code_quality.md`, `docs/architecture/refactoring_roadmap.md`,
`docs/architecture/technical_debt.md`, `notebooks/_archive/README.md`, issue #52.
