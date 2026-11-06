> **Atualização completa do snapshot de setembro/2026** — substitui/complementa
> `docs/architecture/relatorio_set_2026.md`, cuja principal limitação era a
> ausência dos submódulos `packages/*` no clone auditado.
> **As-of:** 2026-09-01.

# Relatório Atualizado (completo) — RadioSkySimSuite (Setembro/2026)

**Branch analisada:** `feature/sims-notebook`
**Commit de referência:** `a5f4423`
**Escopo efetivamente auditado:** meta-repo em `src/`, `scripts/`, `tests/` e os
**9 pacotes** em `packages/*` (submódulos git **inicializados** neste clone),
mais a documentação em `docs/`.

## 1. Resumo executivo

Diferente da rodada anterior, os submódulos de `packages/*` estavam
**totalmente inicializados** (`git submodule status` sem prefixo `-`), o que
permite auditar o workspace `uv` completo — não apenas o umbrella. O quadro que
emerge é mais rico e mais preciso do que os dois relatórios anteriores
(agosto e setembro/v1), que só enxergavam o pacote raiz.

Leitura curta:

- **Volume real do código de produção**: **58.374 linhas** em **437 arquivos**
  Python, distribuídas em 9 pacotes + umbrella (`src/radioskysims`) — quase
  **6× maior** do que o que os relatórios anteriores conseguiram medir
  (10.667 linhas, só o umbrella).
- **Testes**: **31.064 linhas** em **217 arquivos**, com pelo menos **1.388**
  funções `test_*` (contagem estática; execução completa via `pytest`
  não foi realizada nesta rodada — ambiente `uv` local não estava sincronizado
  com todos os pacotes no momento da auditoria). Razão teste/produção de
  **53%**, saudável para um projeto científico.
- **Lint com o ruleset do projeto (`pyproject.toml`)**: **0 erros** em todo o
  código de produção. Isso é um resultado forte, mas precisa ser lido com
  cautela: o ruleset ativo hoje é enxuto (`ARG, B, C4, EM, EXE, G` +
  regras default do Ruff) e a **dívida de legado** (`src/analysis`, `src/bingo`,
  `src/arpls`, `src/GNSStools4Astro`) está **explicitamente excluída** do lint
  via `extend-exclude`.
- **Lint com ruleset máximo (`--select=ALL`, informativo)**: **5.108**
  ocorrências — majoritariamente docstrings ausentes (D1xx), anotação de tipo
  incompleta (ANN0xx/ANN401) e complexidade (`C901`, `PLR0913`). Serve como
  mapa de dívida técnica "ideal", não como meta de curto prazo.
- **Formatação**: **154 de 413 arquivos** (37%) ainda divergem de
  `ruff format`. Esse número não aparecia nos relatórios anteriores porque o
  código dos pacotes não era visível.
- **Arquitetura**: adesão estratégica alta (bounded contexts claros, um
  pacote por contexto, composition root explícito); adesão tática ainda
  parcial, com módulos de orquestração muito grandes
  (`sim_orchestrator.py`, `simulation.py`, `resource_processor.py`) que
  concentram lógica de aplicação, domínio e infraestrutura.
- **Científico/performance**: confirma a leitura anterior — a base é desenhada
  para **processamento local com Dask, controle de memória e datasets lazy**;
  GPU/HPC permanece aspiracional.

## 2. Método e limitações desta atualização

Fontes usadas:

- inspeção estática de todo `src/`, `scripts/` e `packages/*/src` (81 + 356
  arquivos Python de produção);
- `ruff check` (ruleset do projeto e `--select=ALL`) e `ruff format --check`
  sobre `src` e `packages/*/src`;
- contagem estática de testes (`grep -R "def test_"`) sobre `tests/` e
  `packages/*/tests`;
- `pyproject.toml` (raiz e dos 9 pacotes), `settings.toml`, `AGENTS.md`;
- documentos canônicos existentes: `docs/architecture/architecture.md`,
  `bounded_contexts.md`, `entrypoints.md`, `module_dependencies.md`,
  `technical_debt.md`, `docs/source/*.md`, `docs/audits/*`;
- notebooks (`notebooks/00_examples.ipynb`, `01_maps.ipynb`) para casos de uso
  observáveis.

Limitações explícitas:

- **não foi executada a suíte completa de testes** (`pytest`) nesta rodada —
  o ambiente `uv` do clone auditado não estava sincronizado com os pacotes do
  workspace (`ModuleNotFoundError` ao coletar `packages/*/tests`). Os números
  de teste aqui são contagens **estáticas** (arquivos, linhas, funções
  `def test_`), não resultados de execução/cobertura. Recomenda-se `uv sync`
  seguido de `uv run pytest tests packages/*/tests` antes da próxima
  auditoria para obter cobertura real.
- `radioskysim_orig/` (~46.400 linhas) existe no disco local mas está listado em
  `.gitignore` e não é rastreado pelo git — não entra nas métricas, é citado
  apenas como observação de higiene de working tree.
- `02_sims.ipynb` está vazio (branch `feature/sims-notebook` em andamento) —
  não há ainda um notebook de ponta a ponta para o contexto de `Simulation`.

## 3. Descrição resumida do projeto

O **RadioSkySimSuite** é uma suíte Python para simulação e análise do céu em
rádio, voltada ao contexto BINGO (radiotelescópio *single dish* em modo de
trânsito) e a workloads de radioastronomia/cosmologia aplicada. Principais
capacidades:

- carregamento e avaliação de padrões de **beam** (`radioskysims-beam`);
- modelagem de **radiotelescópio** e backend de espectrômetro
  (`radioskysims-radiotelescope`);
- geração/análise de **mapas HEALPix** (`radioskysims-skymap`): sintéticos,
  PySM3, HiPS, operações (smooth/mask), estatística e espectro angular;
- catálogos de **satélites** (TLE/SpaceTrack, RINEX/GNSS) e **rádio-fontes**
  (TAP/NVSS) via `radioskysims-sources` e `gnsstools4astro`;
- orquestração de ponta a ponta e síntese de **TOD** (Time Ordered Data) via
  `radioskysims-simulation`, com processamento *resource-aware* em Dask;
- visualização de **waterfall**/espectrogramas (`radioskysims-waterfall`);
- kernel compartilhado (`radioskysims-core`): config, DB, logging, paths,
  monitor de recursos, progresso e domínio comum (`geometry`, `tracks`);
- visualização reutilizável (`radioskysims-viz`): `PanelApplication`,
  `VisualizerPort`.

O meta-pacote `radioskysim` (raiz) é hoje um **meta-pacote fino**: concentra
composition root (`bootstrap/`), CLI/GUI (`interfaces/`), visualização de
waterfall e resíduos legados fora de escopo (`src/analysis`, `src/bingo`,
`src/arpls`, `src/GNSStools4Astro`, `src/domain/map`).

## 4. Adesão à arquitetura DDD / Hexagonal

**Adesão estratégica: alta.**

- 9 bounded contexts mapeados 1:1 em pacotes próprios (submódulos git), cada um
  com `domain/ application/ ports/ adapters/ infrastructure/` internos.
- Composition root explícito: `src/radioskysims/bootstrap/composition.py`
  **delega** para `radioskysims_simulation.bootstrap.composition` (quebra de
  ciclo lazy `sim_orchestrator ↔ composition` feita na Fase 5 do
  desacoplamento) — bom exemplo de bootstrap fino e sem lógica própria.
- CLIs próprias por pacote via `project.scripts`: `radioskysims` (umbrella,
  SkyMap CLI), `radioskysim-sources` (`radioskysims_sources.interfaces.cli.
  sources_cli:main`), `gnss4astro` (`gnsstools4astro.bootstrap.
  gnss4astro_cli:main`) — sinal de que os pacotes já são "aplicações"
  independentes, não apenas bibliotecas internas.

**Adesão tática: parcial.**

Nos pacotes com maior volume (`radioskysims-simulation`, `radioskysims-sources`,
`radioskysims-skymap`), a camada de `application/services` concentra módulos
muito grandes que fazem orquestração, regra de negócio e wiring de
infraestrutura no mesmo arquivo:

- `radioskysims_simulation/application/services/sim_orchestrator.py` — 1.623
  linhas;
- `radioskysims_simulation/domain/simulation/simulation.py` — 1.573 linhas
  (domínio "gordo": mistura entidade + lógica de composição);
- `radioskysims_simulation/infrastructure/processing/resource_processor.py` —
  1.235 linhas;
- `radioskysims_sources/infrastructure/db/satellite/satelliterepository.py` —
  834 linhas (persistência + curadoria + ingestão externa no mesmo módulo,
  problema já apontado no `module_dependencies.md` histórico e ainda presente).

Isso reforça o diagnóstico dos relatórios anteriores: a fronteira entre
pacotes está bem resolvida (isolamento por submódulo/distribuição), mas a
fronteira **dentro** de cada pacote (domain vs application vs infrastructure)
ainda tem módulos "canhão" que concentram responsabilidades demais.

## 5. Tech stack comentado

| Camada | Bibliotecas | Comentário |
|---|---|---|
| Runtime | Python 3.11–3.14, `uv` workspace | Boa escolha para meta-repo multi-pacote; exige disciplina de `uv sync`/CI. |
| Domínio/DTOs | `pydantic>=2`, `sqlmodel`, `SQLAlchemy>=2.0` | Consistente com `AGENTS.md` ("sem `dataclass` no domínio"). |
| Arrays/computação | `numpy`, `xarray`, `dask[distributed]`, `scipy`, `scikit-learn` | Stack correta para lazy arrays e controle de memória em nó único. |
| Astronomia/cosmologia | `astropy`, `skyfield`, `sgp4`, `healpy`, `pysm3`, `astroquery`, `pyvo`, `reproject`, `pyccl`, `camb` | Alinhada ao domínio (BINGO/HI/cosmologia). |
| GNSS | `georinex`, `gnsstools4astro` (pacote próprio) | Cobre RINEX NAV/OBS além do catálogo TLE. |
| Persistência | PostgreSQL via `psycopg2-binary`/SQLModel; `h5py`/`h5netcdf`; `zarr`/`numcodecs` | Split correto: metadados relacionais vs. arrays científicos em HDF5/Zarr. |
| Visualização | `panel`, `holoviews`, `hvplot`, `datashader`, `jupyter-bokeh`, `matplotlib`, `cartopy` | Adequado para exploração interativa e notebooks. |
| Qualidade | `pytest`, `pytest-cov`, `ruff>=0.9` (`0.12.0` instalado) | Configuração enxuta hoje; ver §7 sobre lacunas. |
| Docs | `sphinx`, `myst-parser`, `myst-nb`, `pydata_sphinx_theme` | Livro Sphinx completo em `docs/source/` (24 páginas .md). |

Comentário especializado:

- Não há evidência de backend GPU operacional; `dask[distributed]` com
  `LocalCluster` é o caminho de escala hoje. GPU continua "capacidade futura",
  não implementada.
- `constraint-dependencies` no `pyproject.toml` raiz fixa ~30 pacotes de
  terceiros para reprodutibilidade — boa prática, mas precisa de processo
  claro de atualização (quem/quando revisa essas pins).

## 6. Entrypoints

| Entrypoint | Pacote | Estado | Observação |
|---|---|---|---|
| `radioskysims` (console script) | `radioskysim` (raiz) → `radioskysims.bootstrap.skymap_cli:main` | Oficial | CLI de SkyMap; composition root delega para o pacote de simulação quando aplicável. |
| `radioskysim-sources` (console script) | `radioskysims-sources` → `radioskysims_sources.interfaces.cli.sources_cli:main` | Oficial | CLI própria do pacote de fontes/satélites — **novo** desde o desacoplamento, não existia nos relatórios anteriores. |
| `gnss4astro` (console script) | `gnsstools4astro` → `gnsstools4astro.bootstrap.gnss4astro_cli:main` | Oficial | CLI de ferramentas GNSS/RINEX. |
| `scripts/start_service.py` | raiz | Oficial | Sobe `SimOrchestrator` + `TODPanel` (GUI). |
| `scripts/check_db.py` | raiz | Oficial | Diagnóstico de banco. |
| `scripts/check_docs.py` | raiz | Oficial | Verificador local de docstrings/type hints (não migrado para os pacotes). |
| `scripts/regenerate_beam_csv.py`, `controlled_point_source_experiment.py`, `mapmaking_binned_scaling_experiment.py`, `plot_mapmaking_binned_scaling.py` | raiz | Experimental | Scripts de experimento pontual, úteis para reprodutibilidade científica mas fora do fluxo operacional principal. |
| `src/radioskysims/interfaces/{cli,api,gui}` | raiz | Misto | `cli/main.py` (603 linhas) é o parser Typer/argparse do umbrella; `gui/skymap/*` monta o Panel app; `api/` existe mas não está exposto por nenhum `project.scripts` (ver `entrypoints.md` atualizado). |
| `notebooks/00_examples.ipynb`, `01_maps.ipynb` | raiz | Oficial (documentação executável) | Cobrem radiotelescópio/beam, satélites (TLE e RINEX), fontes locais (Sol), rádio-fontes (NVSS) e o contexto SkyMap completo via `SkyMapManager`. |
| `notebooks/02_sims.ipynb` | raiz | **Vazio** | Placeholder da branch atual; nenhum fluxo de `Simulation` ponta a ponta documentado via notebook ainda. |

Detalhamento completo (por estado/recomendação) em
[`entrypoints.md`](entrypoints.md).

## 7. Casos de uso

Observáveis diretamente nos notebooks e nas CLIs:

- **Radiotelescópio & Beam** — criar `Radiotelescope`, avaliar FWHM×frequência,
  propriedades de beam (`00_examples.ipynb §2`).
- **Satélites** — `SatelliteManager` por constelação + TLE numa janela de 24h;
  variante a partir de **RINEX** (NAV/OBS, `gnsstools4astro`) com o mesmo
  `build(TR, FR)` (`00_examples.ipynb §3`).
- **Fontes locais (Sol)** — fluxo solar real (SRD/SRS) com cache local e track
  via Skyfield (`00_examples.ipynb §4`).
- **Rádio-fontes** — catálogo real (`radio_sources`), re-ingestão via TAP/NVSS
  (`00_examples.ipynb §5`).
- **SkyMap** — geração sintética offline, geração física via PySM3,
  operações (suavização/máscara), análise (média/RMS/`Cℓ`), I/O FITS, e a API
  unificada `SkyMapManager` que compõe os passos acima
  (`01_maps.ipynb §§1–7`).
- **TOD / Simulation** — via `SimOrchestrator.from_settings(...).run(...)`
  (documentado em `docs/source/quickstart.md`), combinando satélites, fontes
  locais, rádio-fontes e Galáxia (PySM3), com `use_processor=True` acionando o
  `ResourceAwareProcessor`; persistência via `save_result()`/`load_result()`
  em HDF5/NetCDF ou Zarr + sidecar JSON. **Ainda sem notebook próprio**
  (`02_sims.ipynb` vazio) — ver sugestão de feature no §12.
- **CLI de exportação/monitoramento de TOD** — `radioskysims tod export`,
  jobs em background (mencionado em `docs/source/quickstart.md`, seção
  `quickstart-cli`).

## 8. Qualidade de código

### 8.1 Total de linhas de código

| Escopo | Arquivos | Linhas |
|---|---:|---:|
| Produção (`src` + `packages/*/src`) | 437 | 58.374 |
| Testes (`tests` + `packages/*/tests`) | 217 | 31.064 |
| `scripts/` | 7 | 1.294 |
| Legado vendorizado, excluído de lint (`src/analysis`, `bingo`, `arpls`, `GNSStools4Astro`) | 24 | 4.193 |
| **Total rastreado pelo git (aprox.)** | **685** | **94.925** |

Razão teste/produção: **53,2%** (31.064 / 58.374) — patamar saudável.

### 8.2 Módulos (linhas de produção por pacote)

| Pacote | Arquivos | Linhas | % do total |
|---|---:|---:|---:|
| `radioskysims-simulation` | 59 | 13.083 | 22,4% |
| `radioskysims-sources` | 90 | 11.109 | 19,0% |
| `src/radioskysims` (umbrella) | 81 | 10.697 | 18,3% |
| `radioskysims-skymap` | 46 | 5.429 | 9,3% |
| `gnsstools4astro` | 36 | 4.853 | 8,3% |
| `radioskysims-waterfall` | 32 | 4.259 | 7,3% |
| `radioskysims-core` | 40 | 4.339 | 7,4% |
| `radioskysims-beam` | 26 | 2.154 | 3,7% |
| `radioskysims-viz` | 9 | 1.780 | 3,0% |
| `radioskysims-radiotelescope` | 18 | 671 | 1,1% |
| **Total** | **437** | **58.374** | **100%** |

Leitura: `simulation` + `sources` + umbrella somam **~60%** do código de
produção — são os três pontos de maior risco de manutenção e também os de
maior densidade de casos de uso reais (orquestração, persistência de
satélites/rádio-fontes, CLI/GUI).

### 8.3 Linting, formatação, docstrings, type annotations

**Lint com o ruleset do projeto** (`ruff check src packages/*/src`):
**0 erros**. O `pyproject.toml` raiz habilita apenas
`extend-select = ["ARG", "B", "C4", "EM", "EXE", "G"]` além do default do
Ruff, e exclui explicitamente o legado
(`extend-exclude = ["src/arpls/**", "src/bingo/**", "src/GNSStools4Astro/**",
"src/analysis/**", "src/domain/map/**"]`). Ou seja: **o código vivo passa
limpo no ruleset atual**, mas esse ruleset é propositalmente conservador.

**Lint com `--select=ALL`** (informativo, não é meta de curto prazo):
**5.108 ocorrências**. Categorias mais relevantes:

| Categoria | Regras (contagem) | Leitura |
|---|---|---|
| Docstrings ausentes | D102=192, D100=88, D107=91, D105=70, D103=15, D101=26 (≈482 itens públicos) | Cobertura de docstring incompleta em métodos/módulos/`__init__`, mais forte que o indicado no relatório de agosto. |
| Tipagem incompleta | ANN401=398 (`Any`), ANN001=127 (arg sem tipo), ANN201=63 / ANN202=48 (retorno sem tipo) | Uso extenso de `Any` e assinaturas parcialmente tipadas, mesmo em código novo pós-desacoplamento. |
| Complexidade | C901=42 (função complexa), PLR0913=101 (excesso de argumentos) | Concentra-se nos módulos grandes do §8.4. |
| Estilo/import | D212/D413=512+376, COM812=426, I001=61 | Majoritariamente auto-fixável (`ruff --fix`), baixo risco. |
| Práticas de exceção | TRY400=18, BLE001=109, S110=28 (`try/except/pass`) | Tratamento de exceção genérico ainda comum; risco de mascarar falhas silenciosamente. |

**Formatação** (`ruff format --check src packages/*/src`): **154 de 413
arquivos (37%)** divergem do formatter — dado que os relatórios anteriores não
conseguiam medir (código dos pacotes ausente do clone).

**Documentação estrutural**: o "livro" Sphinx em `docs/source/` tem 24 páginas
cobrindo instalação, quickstart, configuração, testes/QA, performance, banco de
dados, satélites, mapas, waterfall, radiotelescópio, simulação e histórico —
volume de documentação de uso é bom; o que falta é o material de
**auditoria/arquitetura por pacote** que este relatório e os documentos
irmãos (`code_quality.md`, `logging.md`, `persistence.md`, `performance.md`,
novos) endereçam.

### 8.4 Módulos muito grandes (candidatos a refatoração)

| Módulo | Linhas | Prioridade | Racional |
|---|---:|---|---|
| `radioskysims_simulation/application/services/sim_orchestrator.py` | 1.623 | Alta | Orquestra 4 tipos de fonte + processor + persistência num único arquivo; maior módulo do monorepo. |
| `radioskysims_simulation/domain/simulation/simulation.py` | 1.573 | Alta | Entidade de domínio "gorda"; mistura modelo de dados com lógica de composição/summary. |
| `src/radioskysims/visualization/waterfall.py` | 1.250 | Alta | Já apontado nos relatórios anteriores; mistura render, materialização e heurística de dados. |
| `radioskysims_simulation/infrastructure/processing/resource_processor.py` | 1.235 | Média-Alta | Núcleo do `ResourceAwareProcessor`; grande mas relativamente coeso (batching + Dask). |
| `radioskysims_simulation/application/services/simulation_service.py` | 1.023 | Média | Sobreposição de responsabilidade com `sim_orchestrator.py` — vale avaliar fusão/redistribuição. |
| `radioskysims_simulation/domain/tod/simulator.py` | 889 | Média | Core científico do TOD; grande mas domínio genuinamente complexo. |
| `src/radioskysims/interfaces/gui/skymap/presenters.py` | 885 | Média | Já apontado antes; bom candidato a dividir por caso de uso (`generate`/`survey`/`analyze`). |
| `radioskysims_sources/infrastructure/db/satellite/satelliterepository.py` | 834 | Alta | Persistência + curadoria + ingestão externa no mesmo módulo — viola separação adapter única responsabilidade. |
| `radioskysims_core/domain/common/models.py` | 654 | Média | Hub de tipos comuns (`FrequencyRange`, `TimeRange`, `Observer`); risco de virar módulo "god" à medida que mais pacotes dependem dele. |
| `src/radioskysims/interfaces/cli/main.py` | 603 | Média | Parser grande; já recomendado migrar para subcomandos em relatórios anteriores. |

### 8.5 Comentário sobre os melhores módulos

- `src/radioskysims/bootstrap/composition.py` — 15 linhas, delega
  integralmente para o pacote de simulação; exemplo de composition root fino
  e sem lógica própria (evolução real desde o relatório de agosto, que ainda
  via um composition root monolítico no umbrella).
- `radioskysims_core/logging_config.py` — logging estruturado em JSON,
  singleton de formatter, contexto global via `set_context`/`clear_context`,
  bem documentado (docstrings completas, `Args`/`Returns`/exemplo de uso).
  Bom modelo a ser replicado nos módulos de infraestrutura de outros pacotes.
- `radioskysims_core/db/engine.py` — `Database.__repr__` sanitiza credenciais
  antes de logar/mostrar URL; inspeciona tabelas via `sqlalchemy.inspect`;
  boa prática de segurança (não vaza segredo em repr/log).
- pacote `radioskysims-radiotelescope` — o menor pacote (671 linhas, 18
  arquivos), mas com estrutura hexagonal limpa e coesa; bom candidato a
  "referência de tamanho ideal" para revisar os pacotes maiores.
- CLIs finas por comando (`radioskysims_sources.interfaces.cli.sources_cli`,
  `gnsstools4astro.bootstrap.gnss4astro_cli`) — seguem o padrão
  DTO → caso de uso → formatter já elogiado no relatório anterior, agora
  replicado em pacotes próprios.

## 9. Dívida técnica

1. **Módulos "canhão" de orquestração** (`sim_orchestrator.py`,
   `simulation.py`, `resource_processor.py`, `satelliterepository.py`) —
   maior risco de manutenção do monorepo; concentram lógica de múltiplas
   camadas.
2. **Cobertura de docstring/tipagem abaixo do ideal em código novo** — os 482
   itens públicos sem docstring e ~640 ocorrências de tipagem incompleta
   mostram que o desacoplamento não veio acompanhado de reforço de
   documentação/tipagem no código migrado.
3. **37% dos arquivos fora do padrão de formatação** — risco de diffs
   ruidosos em PRs futuros; fácil de corrigir (`ruff format`), mas precisa de
   decisão de time (aplicar de uma vez vs. gradualmente por pacote).
4. **Legado vendorizado ainda presente no umbrella** (`src/analysis`,
   `src/bingo`, `src/arpls`, `src/GNSStools4Astro`, `src/domain/map`) — 4.193
   linhas fora do lint/format, sem dono claro de manutenção.
5. **Ambiente de auditoria/CI não valida o workspace completo por padrão** —
   nesta rodada, `uv run pytest` falhou por módulos não sincronizados; se o CI
   tiver o mesmo problema, testes de pacotes podem não estar rodando
   continuamente.
6. **`radioskysim_orig/` como cópia local não rastreada** (~46,4k linhas) —
   não é dívida de repositório, mas é dívida de *working tree*/onboarding:
   claro candidato a remoção ou arquivamento fora do diretório de trabalho
   ativo.
7. **`docs/` com múltiplos relatórios de auditoria acumulando-se** (agora um
   terceiro relatório de setembro) — reforça a recomendação já feita em
   rodadas anteriores de mover snapshots vencidos para `_archive/` com
   banner de validade.
8. **`notebooks/02_sims.ipynb` vazio** — o contexto `Simulation`, apesar de
   ser o maior pacote do monorepo, é o único bounded context sem notebook de
   demonstração ponta a ponta.
9. **[Segurança — CORRIGIDO nesta rodada] Credencial de banco em log DEBUG**
   — `radioskysims_core.db.engine.Database._create_engine()` logava a URI de
   conexão completa (senha em texto plano) em nível `DEBUG`; como
   `configure_logging(enable_file=True)` é o default, isso persistia a
   credencial em `logs/*.json`. Achado novo desta rodada, corrigido no mesmo
   commit — o log agora usa apenas `self.db` (host:port). Detalhado em
   [`persistence.md §2.1`](persistence.md#21-achado-de-segurança--uri-completa-em-log-debug-corrigido)
   e [`logging.md §6`](logging.md#6-segurança).
10. **Inconsistência de adoção do logging estruturado** — 31 módulos usam
    `logging.getLogger(__name__)` puro contra 15 que usam o
    `StructuredLogger`/`get_logger` do padrão do projeto. Ver
    [`logging.md §4`](logging.md#4-adoção-real--inconsistência-a-corrigir).

Detalhamento tático (violação de camada por módulo) permanece em
[`module_dependencies.md`](module_dependencies.md), agora reescrito para a
estrutura pós-desacoplamento.

## 10. Análise de eficiência de código e gargalos

Com base em `docs/source/performance.md`, `docs/audits/tod_performance_audit_report.md`
e inspeção do `ResourceAwareProcessor`:

- **Desenho geral correto**: lazy por padrão (`xarray` + `dask`), batching por
  memória via `ResourceAwareProcessor.max_batch_mb`, streaming para disco
  quando a saída estimada excede a RAM disponível.
- **Hotspots conhecidos e já instrumentados**: consolidação final de batches
  (`xr.concat`), transformadas Healpy (`map2alm`), e o caminho de rádio-fontes
  historicamente mais eager que o restante do pipeline (confirmado pela
  auditoria de performance de agosto).
- **Risco não resolvido**: os módulos que fazem essa orquestração
  (`sim_orchestrator.py`, `resource_processor.py`) são exatamente os módulos
  maiores e mais complexos (`C901` concentra-se ali) — dificultando otimizar
  com segurança sem uma bateria de benchmark de regressão.
- **GPU/HPC**: continuam aspiracionais. Antes de investir em GPU, o retorno
  maior vem de (a) isolar pontos de materialização acidental fora do processor,
  (b) benchmark de regressão contínuo, e (c) reduzir o tamanho/acoplamento dos
  módulos de orquestração para permitir profiling seguro por função.
- **Nada nesta rodada contradiz a recomendação anterior**: não tratar GPU como
  prioridade de curto prazo.

Ver detalhamento e exemplos de código em
[`performance.md`](performance.md) (novo).

## 11. Novas features — sugestões

1. **Notebook `02_sims.ipynb`** cobrindo o fluxo `SimOrchestrator` ponta a
   ponta (mesmo exemplo do `quickstart.md`), com dashboard Dask visível e
   `save_result`/`load_result` — fecha a lacuna do maior bounded context sem
   demonstração executável.
2. **Benchmark de regressão contínuo** para TOD/Healpy/beam, com limites
   aceitos versionados (complementa `docs/audits/tod_performance_audit_report.md`).
3. **Persistência seletiva por tipo de fonte** (satélite/rádio-fonte/local/
   galáxia) no `SimulationOrchestratorResult`, reduzindo custo de depuração.
4. **CI que roda `uv sync` + `pytest` no workspace completo** antes de
   qualquer auditoria/relatório futuro — a limitação metodológica do §2 não
   deveria se repetir num quarto relatório.
5. **Script de verificação de docstring/tipagem por pacote** (equivalente a
   `scripts/check_docs.py`, hoje só cobre o umbrella) integrado ao `Makefile`.
6. **Dashboard/CLI padronizados para expor URL do `LocalCluster` Dask** sempre
   que `dask_scheduler="distributed"` for usado — já recomendado no relatório
   de agosto, ainda não confirmado como implementado.

## 12. Roadmap de evolução

**Curto prazo (1 sprint)**
- corrigir ambiente de auditoria/CI (`uv sync` cobrindo todo o workspace);
- aplicar `ruff format` nos 154 arquivos pendentes, por pacote;
- fechar lacunas de docstring nos módulos públicos de maior visibilidade
  (`radioskysims-core`, `radioskysims-simulation`);
- ~~corrigir o log de credencial em texto plano em
  `Database._create_engine()`~~ — **corrigido** nesta rodada (ver
  `persistence.md §2.1`).

**Médio prazo (2–3 sprints)**
- decompor `sim_orchestrator.py`, `simulation.py` e `satelliterepository.py`
  em módulos menores por responsabilidade;
- criar `02_sims.ipynb` seguindo o sequence diagram em
  [`notebooks_usecases.md §7`](notebooks_usecases.md#7-simulaçãotod-simorchestrator-02_simsipynb--gap)
  e alinhar com `docs/source/quickstart.md`;
- instrumentar benchmark de regressão contínuo (TOD/Healpy/beam);
- uniformizar adoção do `StructuredLogger`/`get_logger` (`logging.md §4`).

**Longo prazo**
- avaliar necessidade real de GPU/HPC somente após consolidar os pontos
  acima;
- revisar se o legado vendorizado (`analysis`, `bingo`, `arpls`,
  `GNSStools4Astro` em `src/`) deve virar pacote próprio, ser arquivado ou
  removido.

## 13. Sprints propostas para melhoria de engenharia

### Sprint 1 — Fechar a lacuna de observabilidade do workspace
- `uv sync` reprodutível documentado e validado em CI para todo `packages/*`;
- `pytest tests packages/*/tests` rodando de fato (coleta + execução) em CI;
- medir cobertura real (hoje só temos contagem estática de `def test_`).

### Sprint 2 — Higiene de formatação e docstring
- `ruff format` aplicado por pacote (PRs pequenos, revisáveis);
- reduzir os 482 itens públicos sem docstring, priorizando `radioskysims-core`
  (kernel compartilhado, maior "superfície pública" reutilizada).

### Sprint 3 — Refatoração dos módulos canhão
- quebrar `sim_orchestrator.py` por família de fonte (satélite/local/rádio/
  galáxia);
- separar `simulation.py` (entidade) de lógica de composição/summary;
- extrair curadoria/ingestão de `satelliterepository.py` para serviços de
  aplicação dedicados.

### Sprint 4 — Performance e produto científico
- benchmark contínuo + telemetria padronizada do `ResourceAwareProcessor`;
- `02_sims.ipynb` + persistência seletiva por tipo de fonte;
- revisão de `radioskysims_core/domain/common/models.py` como possível módulo
  "god" à medida que mais pacotes crescem em torno dele.

## 14. Conclusão

Com os submódulos populados, o quadro muda de escala mas não de direção: a
suíte é **~6× maior** do que os relatórios anteriores conseguiam medir, e a
arquitetura hexagonal por pacote se confirma bem resolvida na fronteira entre
pacotes. O trabalho que falta está **dentro** de cada pacote — reduzir o
tamanho e o acoplamento dos módulos de orquestração, fechar a lacuna de
docstring/tipagem que acompanhou o desacoplamento, e garantir que auditorias
futuras rodem sobre o workspace completo (não apenas o umbrella). Cientificamente
a base continua bem orientada para simulação em nó único com Dask; a próxima
onda de maturidade de engenharia deve vir de refatoração de superfície e
observabilidade de CI, não de novas abstrações.
