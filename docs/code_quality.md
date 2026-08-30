# Relatório de Qualidade de Código — RadioSkySim

**Data:** 2026-08-04
**Revalidação (as-of):** 2026-08-05
**Escopo:** `src/`, `tests/`, `scripts/`, notebooks
**Método:** análise estática (ruff), coleta de testes (pytest), auditoria de
arquitetura (`docs/architecture/`), inspeção manual.

---

## 1. Resumo executivo

O projeto está **saudável e em evolução ativa**: 860 testes coletados (com
`--ignore=data/DB`), arquitetura hexagonal em consolidação e documentação
recentemente expandida. Os principais pontos de atenção são: (1) **811 avisos
de lint** (maioria de estilo, 128
corrigíveis automaticamente), (2) **violações de camada** entre domain/application
e infrastructure, e (3) gestão contínua de segurança/dependências.

| Dimensão | Estado | Nota |
|---|---|---|
| Testes | 🟢 | 860 coletados (com `--ignore=data/DB`) em 80 arquivos de teste |
| Lint (ruff) | 🟡 | 811 erros (128 auto-fix) |
| Arquitetura | 🟡 | Hexagonal em consolidação; violações conhecidas |
| Segurança | 🟡 | Credenciais em `settings.toml` estão vazias; manter enforcement por env vars |
| Dependências | 🔴 | 226 vulnerabilidades no Dependabot |
| Documentação | 🟢 | README, architecture.md, diagramas, notebooks |

## 2. Métricas gerais

### Tamanho do código (`src/radioskysims`)

| Camada | Arquivos | Linhas |
|---|---:|---:|
| domain | 87 | 12 541 |
| application | 31 | 4 497 |
| infrastructure | 68 | 8 948 |
| interfaces | 24 | 3 240 |
| bootstrap | 5 | 484 |
| visualization | 2 | 1 289 |
| **Total** | **217** | **30 999** |

> Observação: `domain` é a camada mais volumosa (~39% do código), o que é
> coerente com um projeto de simulação científica rica em modelos de domínio.

### Testes

- **860 testes** coletados com `--ignore=data/DB` (coleta ampla na raiz encontra
  erro de permissão em `data/DB/conftest.py`).
- **80 arquivos de teste** identificados em `tests/`.
- Cobertura por área: unit (domain/application), infrastructure/db, integration,
  e2e, performance, skymap, visualization.
- O Makefile expõe `make test` para execução.

> Recomendação: executar `pytest --cov=radioskysims --cov-report=term-missing`
> para medir cobertura por módulo e priorizar áreas sem testes (ex.:
> `domain/rfi`, `domain/noise`, `interfaces/api`).

## 3. Lint (ruff 0.12.0)

`ruff check src/ tests/ scripts/` → **811 erros** (128 auto-fix; 304 com
`--unsafe-fixes`).

### Principais categorias

| Regra | Qtd | Descrição |
|---|---:|---|
| PLC0415 | 129 | `import-outside-top-level` (imports lazy) |
| EM101 | 122 | `raw-string-in-exception` |
| ARG002 | 53 | `unused-method-argument` |
| I001 / I002 | 84 | imports fora de ordem / `__init__` faltando |
| G004 | 38 | `logging-f-string` (f-string em logging) |
| T201 | 38 | `print` em produção |
| NPY002 | 27 | `numpy-legacy-random` |
| F401 / F841 / F821 | 37 | imports/variáveis não usados, nomes indefinidos |

### Arquivos com mais problemas

| Arquivo | Erros |
|---|---:|
| `src/radioskysims/visualization/waterfall.py` | 39 |
| `src/radioskysims/domain/simulation/simulation.py` | 34 |
| `src/radioskysims/infrastructure/db/beam_repository.py` | 25 |
| `scripts/check_db.py` | 24 |
| `src/radioskysims/application/services/simulation_service.py` | 21 |

> Recomendação: rodar `ruff check --fix` (128 fixes automáticos) e, em seguida,
> tratar EM101/PLC0415 (mais invasivos) em batches por camada.

## 4. Arquitetura e dívidas técnicas

Base: `docs/architecture/current_architecture.md`, `module_dependencies.md`,
`target_architecture.md`.

### Positivos
- Layout hexagonal com ports em `application/ports/` (7 ports) e composition
  root em `bootstrap/`.
- Módulos recentes seguem a separação (ex.: `SimulationRepositoryPort` +
  `SimulationRepository`).
- DI consolidada via builders.

### Violações de camada conhecidas (dívida)

> Nota de revalidação (2026-08-05): os valores abaixo são da baseline
> arquitetural; manter como referência histórica e recontar automaticamente no CI.

| Origem → Destino | Qtd | Exemplo |
|---|---|---|
| application → infrastructure | 13 | `sim_orchestrator.py` (config/DB/loaders) |
| domain → infrastructure | 9 | `domain/tracks`, `domain/signal`, `domain/skymap` (logging/config) |
| domain → application | 1 | `domain/satellite/repositories.py` |
| interfaces → infrastructure | 2 | `interfaces/__init__.py` |

### Outros pontos
- Há namespace legado de beam (`radioskysims/beam`) coexistindo com `domain/beam`
  em relatórios históricos; requer revalidação contínua de caminho canônico.
- `domain/satellite/main.py` não está presente na base atual (item histórico).
- `domain/common` concentrado (risco de "god/common").

Detalhes: `docs/architecture/technical_debt.md` e `refactoring_roadmap.md`.

## 5. Segurança 🟡

- Em `settings.toml` atual (seção `[SPACETRACK]`), `ST_USER`/`ST_PWD` estão
  vazios e comentados para uso via ambiente.
  - **Ação imediata**: manter enforcement para não reintroduzir credenciais
    reais no versionamento.
- **226 vulnerabilidades de dependências** no branch default (1 critical, 88
  high, 97 moderate, 40 low) — acompanhado no **issue #52**.

## 6. Notebooks (auditoria 2026-08-04)

- **10 notebooks mantidos** em `notebooks/` (funcionais, sem erros salvos).
- **10 movidos para `notebooks/_archive/`** (erros, vazios ou rascunhos) — ver
  `notebooks/_archive/README.md`.
- Removidos: `notebooks/data/` (duplicata de `data/` criada por execução) e 2
  `.code-workspace` versionados.

## 7. Infra / higiene

- `__pycache__` do projeto removido (72 diretórios).
- Makefile criado (`make setup|install|test|lint|postgres-up|docs|clean`).
- `data/DB` não acessível por permissão em alguns comandos — revisar permissões
  do volume Postgres.

## 8. Recomendações priorizadas

### P0 (segurança)
1. Manter enforcement para impedir reintrodução de credenciais reais em
  `settings.toml`.
2. Tratar vulnerabilidades critical/high (issue #52).

### P1 (qualidade)
3. `ruff check --fix` + tratar EM101/PLC0415 em lotes por camada.
4. Rodar coverage e fechar lacunas (rfi, noise, interfaces/api).

### P2 (arquitetura)
5. Remover imports `domain → infrastructure` (logging/config) — injetar logger.
6. Unificar loaders/namespaces de beam e atualizar documentação histórica de
  caminhos legados.
7. Revisar política de configuração para manter `settings.toml` sem segredos e
  com validação no CI.

### P3 (processo)
8. Adicionar CI (lint + testes) e badge de cobertura.
9. Habilitar Dependabot com auto-merge para atualizações seguras.
