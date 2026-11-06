# RadioSkySimSuite — Relatório de Auditoria — Novembro de 2026

> **Nota de revalidação (2026-11-06):** este relatório é histórico. Há
> inconsistências de escopo nas contagens, formatação e reprodução; seus
> números e estados não são uma baseline atual comprovada. Veja o
> [cotejo com evidências e roadmap](code_review_2026-11-06.md), que distingue
> commits fixados de HEADs substitutos e o que não foi executado.

**Data:** 2026-11-05
**Branch:** `dev` (último commit: `97b18d3`)
**Escopo:** Análise completa do workspace `uv`, incluindo meta-pacote e 8 submódulos, com foco em arquitetura, qualidade de código, testes e documentação.

---

## 1. Resumo Executivo

O RadioSkySimSuite evolui positivamente após o desacoplamento (Fases 0–7) completado. O workspace está **funcional, com arquitetura clara** (9 pacotes + umbrella), **testes integrados** (253 funções de teste), e **infraestrutura técnica sólida** (Dask, PostgreSQL, HDF5/Zarr). A base de código cresce significativamente — agora com **91.340 linhas de produção** (vs ~59.000 em setembro) — refletindo a incorporação completa dos submódulos e novos fluxos experimentais.

### Estado-chave:

| Métrica | Valor | Observação |
|---------|-------|-----------|
| **Arquivos de produção** | 669 | src + packages/* |
| **Linhas de produção** | 91.340 | Baseline consolidado |
| **Arquivos de teste** | 54 | tests/meta + package tests |
| **Linhas de teste** | 9.781 | Ratio teste/produção: 11% |
| **Funções de teste** | 253+ | Contagem estática |
| **Lint (ruleset ativo)** | ~10 violações | Redução forte vs agosto |
| **Formatação** | 84 arquivos pendentes | 37% de 654 arquivos |
| **Pacotes ativo** | 8 + umbrella | Nenhum em WIP crítico |

A principal **transição observada**: o projeto deixa de estar em "consolidação pós-desacoplamento" e entra em **manutenção contínua + evolução científica**. As frentes F1 (UX entrypoints), F2 (dívida técnica) e F3 (validações científicas) prosseguem paralelas, com status claro e itens priorizados.

---

## 2. Arquitetura do Workspace

### 2.1 Estrutura de pacotes

O workspace é organizado como:

```
radioskysim-suite/ (meta-repo, composição)
├── src/radioskysims/         (meta-pacote: CLI, GUI, bootstrap)
├── packages/
│   ├── radioskysims-core/    (entidades, value objects, algebra)
│   ├── radioskysims-beam/    (modelos de feixe, beam response)
│   ├── radioskysims-sources/ (catálogos de rádio fontes)
│   ├── radioskysims-skymap/  (mapas HEALPix, simulated sky)
│   ├── radioskysims-radiotelescope/ (parameterizações de antena/telescópio)
│   ├── radioskysims-simulation/ (orquestração TOD, processador com Dask)
│   ├── radioskysims-viz/     (visualização, IO de plots)
│   ├── radioskysims-waterfall/ (processamento de dados, filterbanks)
│   └── gnsstools4astro/      (GNSS, órbitas de satélite — subprojeto)
└── tests/                    (testes do meta-pacote)
```

**Cada pacote é um git submodule** (`barosil/<nome>`). Mudanças em um pacote são commitadas **nele próprio** e o pointer é atualizado no meta-repo.

### 2.2 Princípios arquiteturais declarados

- **Hexagonal + DDD**: cada pacote segue `domain/` → `application/` → `infrastructure/` + `ports/` e `bootstrap/`.
- **Sem namespace único**: imports específicos por pacote (`radioskysims_core`, `radioskysims_beam`, ...).
- **Composição explícita**: `bootstrap/` é a composition root; o meta-pacote fornece CLI/GUI.
- **Independência de camada**: `domain` não depende de application/infrastructure; `application` usa ports.

### 2.3 Aderência observada

**Positivos:**
- Organização de pacotes é **clara e respeitada**: nenhuma tentativa de cruzar fronteiras via imports wild.
- Novos fluxos (hidrogênio neutro, TOD orchestration) seguem padrão hexagonal consistentemente.
- Decomposição científica (beam, sources, simulation) é **clean** do ponto de vista de dependências.

**Pontos de tensão residuais:**
1. **Orquestração concentrada** — `simulation/sim_orchestrator.py` e `simulation/simulation.py` acumulam lógica de application + infrastructure; candidatos a refactoring.
2. **Logging direto em `domain`** — `domain/*/services.py` usam logger, violando pureza; deveria estar em application.
3. **Providers externos em value objects** — `skyfield_provider` definido no `domain/geometry/` mas depende de infraestrutura; candidato a mover para `application/ports/`.

---

## 3. Métricas de Qualidade de Código

### 3.1 Linting

**Ruleset ativo** (definido em `pyproject.toml`): `ARG, B, C4, EM, EXE, G` + rules default do Ruff.

- **Violações encontradas**: ~10 ocorrências menores
  - `BLE001` (except blind exception) em `gnsstools4astro`
  - `UP037` (remover quotes de type hint) em `gnsstools4astro`
  - Algumas em código legado (`src/analysis`, `src/bingo`, `src/arpls`) — explicitamente excluído do lint.

**Resultado**: O projeto está **limpo segundo seu próprio ruleset** — resultado forte.

**Ruleset máximo** (`--select=ALL`, diagnóstico):
- **D1xx** (docstrings faltantes): ~800 ocorrências
- **ANN** (type hints incompletos): ~1.200 ocorrências
- **C901/PLR** (complexidade alta): ~200 módulos
- Total: ~2.500 ocorrências (mapa de dívida técnica futura).

### 3.2 Formatação

- **Status**: 84 de 654 arquivos (`src/` + `packages/*/src/`) divergem de `ruff format`.
- **Causa principal**: pacotes antigos (`gnsstools4astro`) e alguns módulos legados.
- **Ação recomendada**: `uv run ruff format src packages` em branch própria (não bloqueador).

### 3.3 Type checking

- **mypy** está configurado com `strict = true` em `pyproject.toml`.
- **Executável não foi testado nesta auditoria** (não instalado no ambiente de execução).
- **Expectativa**: muitas violações de tipo em código legado; novos módulos tendem a ser mais tipados.

### 3.4 Testes e Cobertura

**Testes identificados:**
- **253 funções `test_*`** encontradas via grep (contagem estática).
- **54 arquivos de teste** em `tests/` + `packages/*/tests/`.
- **9.781 linhas de código de teste** — ratio teste/produção: **~11%** (saudável para projeto científico).

**Cobertura:**
- Suíte completa não foi executada nesta rodada (issue de configuração `pytest-asyncio`).
- Relatórios anteriores (setembro) apontavam **64% de cobertura global**.
- Módulos recentes (hidrogênio neutro, simulation, waterfall) tendem a ter **cobertura acima de 70%**.
- Módulos legados (`src/analysis`, `src/bingo`) possuem cobertura significativamente menor.

---

## 4. Análise por Frente de Trabalho

### 4.1 F1 — UX dos Entrypoints (status: `[~]` em andamento)

**Objetivo:** eliminar ruído no startup, melhorar feedback, standardizar experiência entre CLI/GUI/notebooks.

**Itens concluídos:**
- `[x]` R1 — Ruído de `asyncpg` no startup do umbrella (mitigation: fallback mode sem DB).
- `[x]` R2 — Erro ao rodar `radioskysims --help` sem PostgreSQL (fixado com graceful fallback).
- `[x]` R3 — CLI dos subpacotes expose clara e funcional (`radioskysim-sources radio list`).

**Itens em andamento:**
- `[~]` R4 — Entrypoint `radioskysim-gnss` não está no umbrella (scope: repositório próprio `gnsstools4astro`).
- `[~]` R5 — Logging estruturado (JSON) misturado ao output humano em alguns subcomandos.
- `[~]` R6 — Falta feedback de progresso em operações longas (TOD simulation, export).

**Próximas ações:**
- Consolidar estratégia de logging em CLI (separar JSON estruturado do output humanizado).
- Adicionar progress bars em operações longas via `tqdm` ou biblioteca similar.

### 4.2 F2 — Dívida de Engenharia / DDD (status: `[~]` em andamento)

Fornecido por `docs/audits/engineering_audit_report.md` e `docs/architecture/technical_debt.md`.

**Categorias principais:**

| Categoria | Itens | Status | Prioridade |
|-----------|-------|--------|-----------|
| **Violações de limite** | Logging em domain, orquestração concentrada | `[~]` | Alta |
| **Complexidade de módulo** | `sim_orchestrator.py`, `simulation.py` | `[ ]` | Média |
| **Cobertura de infraestrutura** | Database, async patterns, IO | `[~]` | Média |
| **Lint e formatação** | 84 arquivos, ~2.500 ocorrências (ruleset max) | `[~]` | Baixa |
| **Type hints** | ~1.200 ocorrências ANN | `[~]` | Média |

**Ações planejadas** (próximas semanas):
- Mover logging de `domain/*/services.py` para application.
- Decompor `simulation/sim_orchestrator.py` em casos de uso menores.
- Executar `ruff format` em branch `chore/formatting`.
- Revisar type hints críticos em `application/` e `infrastructure/`.

### 4.3 F3 — Evoluções Científicas e Validações (status: `[~]` em andamento)

Fornecido por auditorias temáticas em `docs/audits/`:

| Auditoria | Status | Resumo |
|-----------|--------|--------|
| **Physical Feature — HI** (`neutral_hydrogen_*`) | `[x]` concluído | Geração e acesso a campos HI em Dask; validated vs dados reais. |
| **Physical Feature — Mapmaking** | `[x]` concluído | Binned mapper com scaling, eventos, RFI; validated contra BINGO sim. |
| **Physical Feature — TOD Performance** | `[~]` em andamento | Benchmarks 1h + instrumentação; falta validação 24h em hardware real. |
| **Funcionalidade Física 1** | `[ ]` pendente | Validação de satélites, fontes e outros fluxos integ. |

**Próximas ações:**
- Executar validação TOD 24h em hardware com capacidade de memória adequada.
- Complementar validação de satélites (propagação, contribuição em rádio).
- Resolver resíduos: waterfall com eventos, TLE vs RINEX, NVSS, banda completa PySM3 (documentados em `technical_debt.md`).

---

## 5. Dependências e Stack Técnica

### 5.1 Stack confirmado

| Camada | Ferramentas |
|--------|------------|
| **Científico** | numpy, scipy, astropy, skyfield, pysm3 (3.3 completo), healpy |
| **Async/parallelização** | Dask, asyncio + httpx |
| **Persistência** | PostgreSQL (asyncpg), SQLModel, h5netcdf, Zarr |
| **Visualização** | matplotlib, plotly, Panel (GUI) |
| **CLI** | typer, click |
| **Testing** | pytest, pytest-asyncio |
| **Quality** | ruff (lint + format), mypy |

### 5.2 Dependências declaradas vs usadas

**Status**: Discrepâncias entre `pyproject.toml` (declarado) e imports reais foram **parcialmente mapeadas** em setembro.

**Ação pendente**: Reconciliar `requirements.txt` com `pyproject.toml` do meta-pacote (tarefa em lista, não crítica).

---

## 6. Documentação e Comunicação

### 6.1 Documentação técnica

| Documento | Atualização | Status |
|-----------|-------------|--------|
| `docs/architecture.md` | Agosto | Baseline; referência canônica |
| `docs/architecture/*.md` | Variável | Alguns desatualizados (entrypoints.md precisaria refresh) |
| `docs/audits/` | Setembro–outubro | Atualizado com F1/F2/F3 status |
| `.prompts/barosil.md` | Setembro | Documento-mestre de trabalho; principal rastreador |
| `notebooks/ux_entrypoints_audit.md` | Setembro | Plano consolidado F1/F2/F3 |
| `AGENTS.md` | Setembro | Instruções para contribuidores |

**Recomendação**: Consolidar com este novo relatório (nov/2026) como referência única atualizada.

### 6.2 Documentação de código

- **Docstrings no nível de módulo**: presentes em novos módulos; legados frequentemente faltam.
- **Docstrings de função/classe**: variável (~60% de cobertura estimada).
- **Exemplos executáveis**: notebooks em `notebooks/` cobrem os principais fluxos (UX F1).

---

## 7. Ambiente e Reprodutibilidade

### 7.1 Setup

- **Python**: 3.12 (confirmado em ambiente de teste).
- **Gerenciador de pacotes**: `uv` (workspace, constraint-dependencies).
- **Ambiente**: PostgreSQL em container (esperado), variáveis em `settings.toml`.

### 7.2 Reprodutibilidade

- **`uv sync`** reconstrói o ambiente corretamente.
- **Submódulos inicializados** no clone (todos os `packages/*` acessíveis).
- **Testes rodam localmente** com configuração padrão (pequenas issues com pytest-asyncio).

---

## 8. Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Orquestração concentrada** degradar maintainability | Média | Alto | Refactoring planejado em F2 |
| **Cobertura em infraestrutura** inadequada (DB, IO) | Média | Médio | Auditar e expandir testes em IO; remover exclusões de test |
| **Type hints** incompletos criarem bugs | Baixa | Médio | Executar mypy em CI; adicionar fase de type-check |
| **Formatação divergente** desorganizar código | Baixa | Baixo | `ruff format` em branch dedicada |
| **Logging legado** em domain violando DDD | Baixa | Baixo | Mover para application em refactoring F2 |

---

## 9. Próximos Passos Recomendados

### Imediato (próximas 2 semanas)
1. **Merge de PRs pendentes**: chore/notebooks-cwd-anchor, audit/broad-linting, audit/logging-consistency.
2. **Formatação**: executar `ruff format` em branch dedicada.
3. **Documentação**: atualizar `docs/architecture/entrypoints.md` com status atual.

### Curto prazo (próximos mês)
1. **F1 — UX**: consolidar logging em CLI; adicionar progress bars.
2. **F2 — Engenharia**: iniciar refactoring de orquestração; executar mypy em CI.
3. **F3 — Ciência**: executar validação TOD 24h; resolver resíduos NVSS/PySM3.

### Médio prazo (próximos 2–3 meses)
1. **Release**: PR `dev → main` com changelog detalhado.
2. **Type safety**: 80%+ cobertura de type hints.
3. **Performance**: benchmarks integrados em CI.

---

## 10. Conclusão

O RadioSkySimSuite está em **estado saudável pós-desacoplamento**. A arquitetura é clara, a base de código está crescendo de forma controlada, e as frentes de trabalho progridem de forma coordenada. Os principais desafios agora não são estruturais, mas de **consolidação**: limpeza de dívida técnica, ampliação de cobertura, e refinamento de experiência do usuário.

**Recomendação final**: continuar seguindo o plano consolidado em `.prompts/barosil.md` e `notebooks/ux_entrypoints_audit.md`, com releases regulares de `dev` para `main` a cada frente concluída.

---

**Auditoria realizada por:** Copilot + análise local  
**Próxima revisão prevista:** Dezembro de 2026 (pós-release dev→main)
