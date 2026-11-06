# RadioSkySimSuite — Status Consolidado de Frentes (Novembro 2026)

**Data de atualização:** 2026-11-05  
**Documento-mestre:** `.prompts/barosil.md` (principal rastreador)  
**Complementos:** `notebooks/ux_entrypoints_audit.md` (detalhe F1/F2/F3)

---

## Resumo Executivo — 3 Frentes em Paralelo

| Frente | Objetivo | Progresso | Próximas ações |
|--------|----------|-----------|----------------|
| **F1 — UX Entrypoints** | Eliminar ruído, feedback consistente | 50% (R1–R3 done, R4–R6 pending) | Logging JSON/humanizado; progress bars |
| **F2 — Dívida Técnica** | Refactoring DDD, lint, type-hints | 65% (DDD+DI+LSP+SRP concluídos) | SRP residual: decompor run() do orquestrador |
| **F3 — Validações Científicas** | HI, mapmaking, TOD 24h, satélites | 60% (HI/mapmaking validated) | TOD 24h em hardware real; resolver NVSS/PySM3 |

---

## F1 — Experiência de Usuário (UX) dos Entrypoints

### Ondas de implantação

#### Onda 1: Eliminar Ruído no Startup — `[x]` Concluído (setembro)

| Item | Status | Data | Notas |
|------|--------|------|-------|
| **R1** — `asyncpg` missing no umbrella | `[x]` | 2026-09-15 | Fallback graceful; db ativado só se config |
| **R2** — `--help` falha sem PostgreSQL | `[x]` | 2026-09-15 | Mesmo fallback |
| **R3** — CLI de subpacotes funcional | `[x]` | 2026-09-20 | Testado: `radioskysim-sources radio list` |

#### Onda 2: Logging e Feedback — `[~]` Em andamento

| Item | Status | Descrição | Prioritário |
|------|--------|-----------|------------|
| **R4** — Entrypoint `radioskysim-gnss` no umbrella | `[>]` Fora de escopo | Pertence ao repo `barosil/gnsstools4astro` | Não |
| **R5** — Logging estruturado (JSON) vs humanizado | `[ ]` Pendente | CLI mistura JSON estruturado + output humano | **Sim** |
| **R6** — Progress bars em operações longas | `[ ]` Pendente | TOD simulation, export: sem feedback de progresso | **Sim** |

#### Onda 3: Documentação de Uso — `[ ]` Pendente

| Item | Status | Descrição | Estimativa |
|------|--------|-----------|-----------|
| **L1** — README atualizado com fluxo mínimo viável | `[ ]` | Getting started; remover exemplo legado `run_simulation` | 2 dias |
| **L2** — Docstring de CLI commands | `[ ]` | `typer` help strings claras em todo umbrella | 3 dias |
| **L3** — Documentação de `gnss4astro` | `[>]` | Fora de escopo (repo próprio) | — |

### Indicadores de sucesso F1

- [ ] CLI umbrella não produz warnings/erros no startup
- [ ] Cada subcomando tem help claro (`--help`)
- [ ] Progress em operações > 5 segundos
- [ ] Logging estruturado separado do output do usuário
- [ ] README com fluxo mínimo (2–3 exemplos)

---

## F2 — Dívida de Engenharia e Aderência DDD

### Categorias mapeadas (fonte: `engineering_audit_report.md` + `technical_debt.md`)

#### Violações de Limite Arquitetural

| Violação | Localização | Tipo | Prioridade | Fix |
|----------|------------|------|-----------|-----|
| Logging direto em domain | `domain/*/services.py` | Design | Alta | ✅ Removido (B2 — domínio puro) |
| Providers externos em value objects | `domain/geometry/skyfield_provider.py` | Design | Alta | ✅ Movido p/ `infrastructure/external_geometry.py` |
| Dependência de domain para application | `domain/simulation/simulation.py` → application | Import | Média | ✅ Resolvida (DI no composition root) |

#### Complexidade de Módulo (candidates para refactoring)

| Módulo | Linhas | Funções | Complexidade | Status | Ação |
|--------|--------|---------|--------------|--------|------|
| `simulation/sim_orchestrator.py` | 1419 | 20+ | Alta | `[~]` | DiffuseTODRunner extraído; run() residual |
| `simulation/simulation.py` | ~600 | 15+ | Alta | `[ ]` | Mover lógica para domain/application |
| `domain/beam/services.py` | ~400 | 12+ | Média | `[~]` | Revisão em progresso |

#### Cobertura de Testes em Infraestrutura

| Componente | Cobertura | Status | Meta |
|-----------|-----------|--------|------|
| **Database/SQLModel** | ~40% | Baixa | 70% |
| **Async patterns (httpx)** | ~35% | Baixa | 60% |
| **IO (h5netcdf, Zarr)** | ~50% | Média | 75% |
| **Processor/Dask** | ~65% | Média | 80% |

#### Lint e Formatação

| Aspecto | Status | Meta | Ação |
|---------|--------|------|------|
| **Ruleset ativo** | ~10 erros | 0 erros | Fix em próxima PR |
| **Formatação** | 84/654 arquivos | 100% | Branch `chore/formatting` |
| **Type hints (ANN)** | ~1.200 ocorrências | 80% cobertura | Faseado ao longo do Q4 |

### Plano de execução F2

**Semana 1–2 (nov 5–17):**
- [ ] Mover logging de `domain/*/services.py` para application → nova PR
- [ ] Esquematizar refactoring de orquestração (DESIGN.md)

**Semana 3–4 (nov 18–24):**
- [ ] Executar `ruff format` em branch `chore/formatting` + merge
- [ ] Primeira iteração de type hints críticos em application/

**Dezembro:**
- [ ] Refactoring de orquestração (iteration 1 de N)
- [ ] Executar mypy em CI
- [ ] Resolver issues de import em infrastructure

### Indicadores de sucesso F2

- [ ] 0 violações de design no ruleset ativo
- [ ] 85%+ arquivos formatados
- [ ] 75%+ cobertura de type hints em application/
- [ ] Testes de infraestrutura com 65%+ cobertura
- [ ] mypy rodando sem falhas críticas

---

## F3 — Evoluções e Validações Científicas

### Auditorias e validações por componente

#### Componente: Hidrogênio Neutro (HI)

| Status | Data | Validação | Resultado |
|--------|------|-----------|-----------|
| **Geração em Dask** | `[x]` | Set/2026 | Ok; lazy evaluation preservada |
| **Acesso/slicing** | `[x]` | Set/2026 | Ok; indexing em chunks |
| **Validação vs dados reais** | `[x]` | Out/2026 | Ok; comparação com SKAO simulado |

**Artefatos:** `docs/audits/neutral_hydrogen_physical_feature_audit.md`

**Status:** ✅ **CONCLUÍDO** — Pronto para produção

---

#### Componente: Mapmaking (Binned Sky Maps)

| Status | Data | Validação | Resultado |
|--------|------|-----------|-----------|
| **Binned mapper** | `[x]` | Ago/2026 | Ok; scale factor implementado |
| **Eventos (RFI, outliers)** | `[x]` | Set/2026 | Ok; flagging integrado |
| **Validação vs BINGO sim** | `[x]` | Out/2026 | Ok; fluxos batem dentro de tolerância |

**Artefatos:** `docs/audits/mapmaking_physical_feature_audit.md`, `mapmaking_binned_scaling.md`

**Status:** ✅ **CONCLUÍDO** — Pronto para produção

---

#### Componente: TOD Performance e Processamento

| Etapa | Status | Data | Resultado | Próximas ações |
|-------|--------|------|-----------|----------------|
| **Benchmarks 1h** | `[x]` | Set/2026 | Ok; performance aceitável | — |
| **Instrumentação Dask** | `[x]` | Out/2026 | Ok; diagnóstico implementado | — |
| **Validação TOD 24h** | `[ ]` | Pendente | — | **Executar em hardware real** |
| **Otimizações seguintes** | `[~]` | Em andamento | Candidatos mapeados | Avaliar após 24h |

**Artefatos:** `docs/audits/tod_performance_audit_report.md`

**Bloqueador crítico:** Hardware com capacidade de memória > 32GB para validação 24h.

**Status:** 🟡 **EM ANDAMENTO** — Faltando validação 24h

---

#### Componente: Satélites (Propagação, Contribuição Rádio)

| Etapa | Status | Data | Resultado |
|-------|--------|------|-----------|
| **Propagação TLE** | `[~]` | Em andamento | Parcialmente validado |
| **Contribuição em rádio (S-band)** | `[ ]` | Pendente | — |
| **Validação integrada** | `[ ]` | Pendente | — |

**Artefatos:** (falta auditoria formal)

**Status:** 🟡 **PENDENTE** — Requer auditoria e validação

---

### Resíduos conhecidos (fora desta rodada)

| Residual | Descrição | Impacto | Prioridade |
|----------|-----------|---------|-----------|
| **Waterfall com eventos** | Integração de flagging (RFI) no pipeline | Médio | Baixa |
| **TLE vs RINEX** | Ambiguidade de fonte de órbita | Baixo | Baixa |
| **NVSS** | Catálogo não incluído | Médio | Média |
| **PySM3 banda completa** | Interpolação além de 23 GHz | Baixo | Baixa |

---

## 4. Timeline Consolidada — Roadmap Nov–Dez 2026

### Semana Nov 5–10

- `[ ]` Merge: chore/notebooks-cwd-anchor, audit/broad-linting, audit/logging-consistency
- `[ ]` Revisar e consolidar este relatório de auditoria
- `[ ]` Iniciar F2: mover logging de domain

### Semana Nov 11–17

- `[ ]` Executar ruff format; criar branch `chore/formatting`
- `[ ]` F3: setup para TOD 24h (hardware, dados)
- `[ ]` F1: prototipo de progress bars em CLI

### Semana Nov 18–24

- `[ ]` Merge: chore/formatting
- `[ ]` Merge: F2 logging refactor
- `[ ]` F3: executar validação TOD 24h
- `[ ]` Revisar PRs, consolidar

### Semana Nov 25–Dez 1

- `[ ]` F3: análise resultados TOD 24h
- `[ ]` F2: esquema de refactoring de orquestração
- `[ ]` Documentação (README, docstrings)

### Dezembro (pós-Thanksgiving)

- `[ ]` Iteração 2 F2: refactoring de orquestração
- `[ ]` F1: merge progress bars
- `[ ]` Preparar release dev→main
- `[ ]` Type hints + mypy CI

---

## 5. Definições de Pronto (DoD por frente)

### F1 — UX Entrypoints

- [ ] Sem warnings no startup (todos os entrypoints)
- [ ] `--help` sempre funciona
- [ ] Progress em operações > 5s
- [ ] Logging estruturado (JSON) separado do output
- [ ] README com 3 exemplos de "getting started"
- [ ] Todas as PRs merged para `dev`

### F2 — Dívida Técnica

- [ ] 0 violações de limite arquitetural no ruleset ativo
- [ ] 100% formatação (ruff format)
- [ ] Refactoring de orquestração iniciado com DESIGN.md
- [ ] Testes de infraestrutura com 65%+ cobertura
- [ ] mypy configurado e rodando em CI (sem falhas críticas)

### F3 — Validações Científicas

- [ ] TOD 24h validado (vs dados reais ou tolerância científica)
- [ ] Satélites auditados e validados
- [ ] Mapmaking pronto para uso científico
- [ ] HI campo validated (já concluído)
- [ ] Resíduos (NVSS, PySM3) documentados e priorizados

---

## 6. Indicadores de Saúde do Projeto

| Indicador | Status | Meta | Trend |
|-----------|--------|------|-------|
| **Branches em WIP** | 6 (simulation, tod-map, waterfall) | < 4 | → (mantido) |
| **PRs abertas** | 3–5 | < 5 | ✓ Ok |
| **Testes passando** | 95%+ | 100% | ✓ Bom |
| **CI verde** | Sim | Sim | ✓ Ok |
| **Lint (ativo)** | ~10 | 0 | ↑ Melhorando |
| **Documentação atualizada** | 70% | 100% | ↑ Melhorando |

---

## 7. Referências Cruzadas

- **Documento-mestre:** `.prompts/barosil.md`
- **Detalhe técnico:** `notebooks/ux_entrypoints_audit.md`
- **Arquitetura:** `docs/architecture.md`
- **Dívida técnica:** `docs/architecture/technical_debt.md`
- **Engenharia:** `docs/audits/engineering_audit_report.md`
- **Auditorias científicas:** `docs/audits/{neutral_hydrogen,mapmaking,tod_performance}*.md`

---

**Próxima atualização:** 2026-12-05 (após Thanksgiving)  
**Preparado por:** Copilot + análise de código
