# Qualidade de Código — RadioSkySimSuite

**Data:** 2026-09-01
**Escopo:** `src/radioskysims` (umbrella) + 9 pacotes em `packages/*`.
**Fonte primária:** `ruff check`/`ruff format --check` (Ruff 0.12.0),
contagem estática (`wc -l`, `grep`) — sem execução de `mypy` (não instalado
no ambiente auditado) nem cobertura real de testes (ver §5).

Este documento detalha a seção 8 de
[`relatorio_set_2026_v2.md`](relatorio_set_2026_v2.md) e serve como
referência viva para acompanhar a evolução da dívida de qualidade.

## 1. Volume de código

| Escopo | Arquivos | Linhas |
|---|---:|---:|
| Produção (`src` + `packages/*/src`) | 437 | 58.374 |
| Testes (`tests` + `packages/*/tests`) | 217 | 31.064 |
| `scripts/` | 7 | 1.294 |
| Legado vendorizado (excluído de lint) | 24 | 4.193 |

Razão teste/produção: **53,2%**.

### Por pacote (produção)

| Pacote | Arquivos | Linhas |
|---|---:|---:|
| `radioskysims-simulation` | 59 | 13.083 |
| `radioskysims-sources` | 90 | 11.109 |
| `src/radioskysims` (umbrella) | 81 | 10.697 |
| `radioskysims-skymap` | 46 | 5.429 |
| `gnsstools4astro` | 36 | 4.853 |
| `radioskysims-waterfall` | 32 | 4.259 |
| `radioskysims-core` | 40 | 4.339 |
| `radioskysims-beam` | 26 | 2.154 |
| `radioskysims-viz` | 9 | 1.780 |
| `radioskysims-radiotelescope` | 18 | 671 |

### Por pacote (testes)

| Pacote | Arquivos | Linhas |
|---|---:|---:|
| `tests` (umbrella) | 53 | 9.716 |
| `radioskysims-simulation` | 42 | 6.089 |
| `radioskysims-skymap` | 24 | 5.528 |
| `radioskysims-sources` | 41 | 3.729 |
| `radioskysims-core` | 17 | 1.515 |
| `radioskysims-beam` | 10 | 1.505 |
| `radioskysims-waterfall` | 13 | 1.187 |
| `gnsstools4astro` | 10 | 979 |
| `radioskysims-viz` | 6 | 691 |
| `radioskysims-radiotelescope` | 1 | 125 |

## 2. Linting

### 2.1 Ruleset configurado no projeto

`pyproject.toml` (raiz):

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
extend-exclude = [
  "src/arpls/**", "src/bingo/**", "src/GNSStools4Astro/**",
  "src/analysis/**", "src/domain/map/**",
]

[tool.ruff.lint]
extend-select = ["ARG", "B", "C4", "EM", "EXE", "G"]
```

Ou seja, além do default do Ruff (`E`, `F` essencialmente), o projeto liga:
`ARG` (argumentos não usados), `B` (bugbear), `C4` (comprehensions), `EM`
(mensagens de exceção), `EXE` (permissões de executável), `G` (formato de
logging).

**Resultado:** `ruff check src packages/*/src` → **0 erros**. O código de
produção *vivo* (excluído o legado) está limpo sob este ruleset.

### 2.2 Ruleset máximo (`--select=ALL`) — informativo

Executar `ruff check --select=ALL` habilita ~800 regras (incluindo
`pydocstyle`, `flake8-annotations`, `pylint`, `flake8-bandit` etc.). Não é
meta de curto prazo — serve para mapear a dívida "ideal":

**Resultado:** **5.108 ocorrências**. Top categorias:

| Grupo | Regras principais (contagem) | Leitura |
|---|---|---|
| Docstrings ausentes | `D102`=192, `D100`=88, `D107`=91, `D105`=70, `D103`=15, `D101`=26 | ≈482 itens públicos (métodos, módulos, `__init__`, funções, classes, magic methods) sem docstring. |
| Tipagem incompleta | `ANN401`=398 (`Any`), `ANN001`=127, `ANN201`=63, `ANN202`=48 | Uso extenso de `Any` e assinaturas parcialmente anotadas. |
| Complexidade | `C901`=42, `PLR0913`=101 | Concentrada nos módulos "canhão" (`sim_orchestrator.py`, `simulation.py`, `satelliterepository.py`). |
| Estilo/import (auto-fixável) | `D212`+`D413`=888, `COM812`=426, `I001`=61 | Baixo risco; `ruff check --fix` resolve a maior parte. |
| Práticas de exceção | `BLE001`=109 (`except Exception`), `TRY400`=18, `S110`=28 (`try/except/pass`) | Tratamento de exceção genérico; risco de mascarar falhas. |
| Segurança pontual | `S608`=2 (SQL hardcoded), `S324`=1 (hash inseguro), `S101`=4 (`assert` em produção) | Baixo volume, mas vale revisão pontual (ver `logging.md`/`persistence.md`). |

### 2.3 Formatação

`ruff format --check src packages/*/src`:

- **154 de 413 arquivos (37%)** divergem do formatter padrão.
- Correção é mecânica (`ruff format`), mas recomenda-se aplicar por pacote
  em PRs pequenos para não gerar diffs ruidosos em revisões em andamento.

## 3. Docstrings e type annotations

Sem `mypy` disponível no ambiente auditado, a métrica de tipagem usada aqui é
a cobertura de anotações reportada pelo Ruff (`ANN0xx`, ver §2.2). Como
proxy adicional, `scripts/check_docs.py` (verificador local de docstrings e
type hints) cobre **apenas o umbrella** — recomenda-se estendê-lo para
`packages/*/src` (ver §6).

Leitura qualitativa por pacote (a partir da distribuição de `D1xx`/`ANN0xx`
por diretório):

- **Melhor cobertura**: `radioskysims-core` (módulos pequenos e centrais como
  `logging_config.py` e `db/engine.py` têm docstrings completas com
  `Args`/`Returns`/exemplos).
- **Maior lacuna**: `radioskysims-simulation` e `radioskysims-sources`,
  onde os módulos maiores concentram a maior parte dos itens sem docstring —
  coerente com o achado de que os módulos "canhão" também são os menos
  documentados.

## 4. Módulos muito grandes (candidatos a refatoração)

| Módulo | Linhas | Prioridade |
|---|---:|---|
| `radioskysims_simulation/application/services/sim_orchestrator.py` | 1.623 | Alta |
| `radioskysims_simulation/domain/simulation/simulation.py` | 1.573 | Alta |
| `src/radioskysims/visualization/waterfall.py` | 1.250 | Alta |
| `radioskysims_simulation/infrastructure/processing/resource_processor.py` | 1.235 | Média-Alta |
| `radioskysims_simulation/application/services/simulation_service.py` | 1.023 | Média |
| `radioskysims_simulation/domain/tod/simulator.py` | 889 | Média |
| `src/radioskysims/interfaces/gui/skymap/presenters.py` | 885 | Média |
| `radioskysims_sources/infrastructure/db/satellite/satelliterepository.py` | 834 | Alta |
| `radioskysims_core/domain/common/models.py` | 654 | Média |
| `src/radioskysims/interfaces/cli/main.py` | 603 | Média |

Critério de priorização: tamanho **combinado** com violação de camada
(`module_dependencies.md`) e centralidade de uso (quantos outros módulos
dependem dele). Ver racional completo em `relatorio_set_2026_v2.md §8.4`.

## 5. Testes

- **1.388 funções `def test_`** (contagem estática via `grep`), em 217
  arquivos / 31.064 linhas.
- **Execução completa não realizada nesta rodada**: `uv run pytest
  packages/*/tests` falhou por `ModuleNotFoundError` (ambiente `uv` não
  sincronizado com todos os pacotes do workspace no clone auditado).
  Recomenda-se `uv sync` antes de qualquer nova auditoria para obter números
  reais de aprovação/cobertura (o relatório de agosto/2026 media 64% de
  cobertura por statements apenas no umbrella).
- `docs/source/testing_qa.md` já define a matriz de testes (unit/integration/
  e2e/performance) e os comandos corretos por nível/pacote — este documento
  não a duplica, apenas referencia.

## 6. Recomendações

1. Aplicar `ruff format` por pacote (PRs pequenos e revisáveis).
2. Priorizar docstrings públicas em `radioskysims-core` (kernel compartilhado,
   maior superfície reutilizada) antes de expandir para os pacotes maiores.
3. Estender `scripts/check_docs.py` para `packages/*/src`.
4. Configurar `uv sync` + `pytest tests packages/*/tests` em CI para garantir
   que a métrica de teste seja sempre de execução real, não estática.
5. Tratar os módulos do §4 como backlog de refatoração formal (ver sprints em
   `relatorio_set_2026_v2.md §13`).
