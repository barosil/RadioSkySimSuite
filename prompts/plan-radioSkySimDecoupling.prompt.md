# Plan: Desacoplamento do RadioSkySim em ecossistema de pacotes


## Revisão

Vamos verificar o plano de desacoplamento, com vistas a sua implantação não destrutiva da situação atual.
- Nomenclatura de pacotes aceita 
- Build tooling: uv workspace (não Poetry) — decidido com usuário.
- Ignorar `bingo`, `analysis`, `arpls` (vendorizados, baixo acoplamento, sem uso crítico) — decidido com usuário. (serão integrados a waterfall posteriormente, mas não agora
- Waterfall criado apenas com ferramentas básicas: slice, resampling, viz.
- Ferramentas de infrastructure para GNSS, com uso de celestrak, space_track transformam-se em pacote próprio utilizado pelos serviços de radioskysims com port adapters específicos.
- Ferramentas de infrastructure para GNSS usando RINEX (georinex) transformam-se em pacote próprio utilizado pelos serviços de radioskysims com port adapters específicos.
- Incluir no plano de criação uma verificação de qualidade de código existente (mypy, ruff, coverage) e manter a suite de testes existente (pytest) verde em cada fase.
- Incluir no plano de criação de cada pacote uma lista compreensiva das funcionalidades que serão movidas para cada pacote, com a devida referência aos arquivos originais.
- **Revisão 2026-08-29**: auditoria de `src/radioskysims/domain/` revelou 10 módulos não mapeados nas fases originais (`common`, `geometry`, `tracks`, `signal`, `signal_source(.py)`, `signal_source_group.py`, `noise`, `rfi`, `catalog`, `skymap`, `map`). Mapeamento resolvido e confirmado com o usuário — ver "Mapeamento de domínio → pacote" abaixo.
- Nomenclatura de imports confirmada: **nomes próprios por pacote** (`radioskysims_core`, `radioskysims_beam`, ...), não namespace único `radioskysims.*`.
- `domain/geometry` (skyfield_provider) e `domain/tracks` (TrackFactory) confirmados no **core** (dependem só de `skyfield`, usados por sources/radiotelescope/simulation igualmente).
- `domain/skymap` (usa healpy) vira **pacote dedicado `radioskysims-skymap`** em vez de ser dobrado dentro de `radioskysims-sources` — decidido com usuário.


## TL;DR
Viável e de risco técnico BAIXO (arquitetura hexagonal já limpa, portos já definidos, precedente funcionando em GNSStools4Astro), mas de esforço ALTO (130 arquivos fonte + 148 de teste, ~5.300 linhas, 65+ usos de config/logging/paths). Recomendação: migrar para **uv workspace**, consolidar os 18 módulos do documento em **9 pacotes por grafo de acoplamento real** (`core`, `skymap`, `viz`, `beam`, `sources`, `radiotelescope`, `simulation`, `waterfall`, `gnsstools4astro`), rodar em fases com portão de regressão (suite de testes) entre cada uma, começando pelo par `radioskysims-core` + `radioskysims-beam`/`radioskysims-viz` como piloto.

## Mapeamento de domínio → pacote (resolvido em 2026-08-29)
| Módulo `domain/` | Pacote destino | Motivo |
|---|---|---|
| `common` (Observer, TimeRange, FrequencyRange, exceptions, science_validator) | `radioskysims-core` | usado por praticamente todos os outros domínios |
| `geometry` (skyfield_provider, pointing) | `radioskysims-core` | só depende de `skyfield`; usado por sources, radiotelescope e simulation |
| `tracks` (TrackFactory) | `radioskysims-core` | acoplado a `geometry`; mesmo padrão de reuso amplo |
| `skymap` (SkyMap, NSide, mask, operations) + `application/skymap/{analyze,generate,dto,ports}.py` | `radioskysims-skymap` (novo) | usa healpy; consumido por cosmologia (sources) e mapmaking (simulation) — pacote dedicado evita dependência invertida |
| `signal` (SignalDefinition, SatSignal — sinal GNSS) | `radioskysims-sources` | usado só pelo domínio de satélite |
| `signal_source.py` / `signal_source_group.py` (protocolo unificado satellite/local/radio) | `radioskysims-sources` | é o contrato exportado por sources; simulation consome, não o contrário |
| `catalog` (CatalogIngestion, CatalogQuery) | `radioskysims-sources` | usado só por `catalog_services` |
| `cosmology` + `application/cosmology/*` + `application/skymap/generate_continuum.py` | `radioskysims-sources` | usa `domain.radiosources.continuum` (Galaxy/HI) junto com `radioskysims-skymap` |
| `noise`, `rfi` | `radioskysims-simulation` | só aparecem em `sim_orchestrator`/`simulation_service`/TOD |
| `map` (stub, `models.py` com TODO, sem nenhum uso) | **fora de escopo** | não implementado ainda (designado a outro colaborador); revisitar quando a implementação começar |

Decisões já validadas com o usuário:
- Workspace: **uv workspace** (migrar de Poetry).
- Granularidade: **consolidar por acoplamento real**, não os 18 itens literais.
- Piloto: **core + RadioBeam + PanelApplication comum**.
- WaterfallTools: **incluir implementação básica** (não existe hoje).

## Decisão de nomenclatura/import (não perguntada ainda — assumida, revisar com usuário)
Cada pacote vira uma distribuição Python com **nome de top-level próprio** (`radioskysims_core`, `radioskysims_beam`, `radioskysims_sources`, `radioskysims_radiotelescope`, `radioskysims_simulation`, `radioskysims_viz`, `radioskysims_waterfall`), em vez de manter tudo sob o namespace único `radioskysims` via PEP 420. Motivo: evita fragilidade de namespace packages (múltiplos `__init__.py` faltando em vários níveis), alinha com o precedente já existente (`gnsstools4astro` é top-level próprio), e deixa claro no `pip install` o que cada pacote é. Custo: exige rename de imports em todo o repo (mecânico, mas grande). Pacote guarda-chuva `radioskysims` (raiz do repo) vira meta-pacote fino: composition root + CLI/GUI + extras de instalação seletiva.

## Fases

### Fase 0 — Fundação de workspace (bloqueia todas as demais)
- Migrar build-system de Poetry (`poetry-core` + `poetry-dynamic-versioning`) para **uv workspace** (`[tool.uv.workspace] members = ["packages/*"]`), com backend `hatchling` (ou setuptools) por pacote; substituir `poetry-dynamic-versioning` por equivalente compatível com uv/hatch (ex.: `hatch-vcs`).
- Criar diretório `packages/` na raiz; decidir contrato de layout: `packages/<nome>/pyproject.toml` + `packages/<nome>/src/<nome_import>/...` + `packages/<nome>/tests/...`.
- Root `pyproject.toml` continua sendo a distribuição guarda-chuva `radioskysim`, mas passa a referenciar os membros do workspace como path-dependencies, com extras (`[project.optional-dependencies]`) por pacote: `beam`, `sources`, `radiotelescope`, `simulation`, `viz`, `waterfall`, `gnss`, `all`.
- Sem mover código ainda — só tooling. Verificação: `uv sync` funciona, suite atual (`pytest`) continua verde sem nenhuma mudança funcional.
- Criar `packages/<nome>/tests/` como contrato de layout desde já (mesmo vazio), já que os testes serão movidos junto com o código a cada fase (decisão confirmada — ver `## Decisions`).

### Fase 1 — Kernel compartilhado: `radioskysims-core` (depende da Fase 0)
Extrair para `packages/radioskysims-core/src/radioskysims_core/`:
- `config/`: generalizar [config_loader.py](src/radioskysims/infrastructure/config/config_loader.py) em `ConfigPort` (ABC) + `TomlConfigAdapter` (implementação atual).
- `db/`: [engine.py](src/radioskysims/infrastructure/db/engine.py) (classe `Database`) + [models.py](src/radioskysims/infrastructure/db/models.py) base, com registro de schema plugável (cada pacote de domínio registra suas próprias tabelas SQLModel).
- `logging_config.py`: mover [logging_config.py](src/radioskysims/infrastructure/logging_config.py) (`configure_logging`, `get_logger`) praticamente sem mudança — é o menos acoplado.
- `paths.py`: generalizar [paths.py](src/radioskysims/paths.py) (`PathManager`), parametrizando a raiz do projeto.
- `monitor/` (NOVO): extrair a parte de detecção de CPU/memória do [resource_processor.py](src/radioskysims/infrastructure/processing/resource_processor.py) (`ResourceAwareProcessor`) em um `SystemMonitor` genérico, standalone, usável por qualquer app antes de qualquer operação pesada. A parte de *chunking/scheduler dask* específica de simulação fica para a Fase 5 (`radioskysims-simulation`).
- `progress.py` (NOVO): utilitário de indicador de progresso uniforme (requisito "Messages" do `.prompts/decoupling.md`) para downloads, ingestão, escrita em DB, operações CPU-bound.
- `domain/common/*` (Observer, TimeRange, FrequencyRange, exceptions, science_validator) — kernel de domínio compartilhado, sem mudança de comportamento.
- `domain/geometry/*` (`SkyfieldGeometryProvider`, `compute_pointing_track`) e `domain/tracks/*` (`TrackFactory`) — só dependem de `skyfield`; usados igualmente por sources, radiotelescope e simulation, evitando dependência cruzada entre esses três.
- Atualizar (mecanicamente) todos os 65+/65+/69+ usos de config/logging/paths/domain-comum no restante do repo para importar de `radioskysims_core.*`; deixar *shims* de compatibilidade temporários nos caminhos antigos (`radioskysims.infrastructure.config.config_loader` reexporta de `radioskysims_core.config`), marcados como deprecated, removidos na Fase 7.
- Verificação: `uv sync --package radioskysims-core` instala com deps mínimas (pydantic, sqlmodel, tomli, psutil, skyfield) sem panel/dask/pyccl/healpy; suite completa (`pytest tests/`) continua verde.

### Fase 2 — Piloto: `radioskysims-viz` + `radioskysims-beam` (depende da Fase 1; valida o padrão antes de generalizar)
- `radioskysims-viz`: nova abstração `PanelApplication` (classe base) sintetizada a partir dos padrões comuns de [beam_panel.py](src/radioskysims/application/beam_panel.py), `gain_panel.py`, `radiotelescope_panel.py`, `tod_panel.py` e do dashboard MVC em `interfaces/gui/skymap/` (`app.py`, `controller.py`, `views.py`, `widgets.py`, `presenters.py`, `state.py`): template/layout padrão (sidebar+main), ciclo de vida `build_sidebar()`/`build_main()`/`serve()`. Também criar `VisualizerPort` (ABC) + `PanelVisualizer` (adapter concreto) para resolver o acoplamento "Panel hardcoded em application" identificado na auditoria.
- `radioskysims-beam`: mover `domain/beam/*`, `infrastructure/beams/loaders/*`, `infrastructure/db/beam_repository.py`+`beam_db_model.py`, `application/ports/beam.py`, `application/beam_panel.py` (refatorado para herdar `PanelApplication`) para `packages/radioskysims-beam/src/radioskysims_beam/{domain,application,infrastructure}/`.
- Verificação: `radioskysims-beam` pyproject declara apenas deps leves (numpy, xarray, panel, holoviews) — **não** deve puxar dask/pyccl/camb/psycopg2 transitivamente, provando que "instalar só um subconjunto" funciona. Testes de `tests/domain/beam/*` e de beam_panel passam isolados via `uv run --package radioskysims-beam pytest`.

### Fase 3 — `radioskysims-skymap` (novo pacote dedicado; depende só da Fase 1; pode rodar em paralelo com a Fase 2)
- Mover `domain/skymap/*` (`SkyMap`, `NSide`, `mask.py`, `operations.py`, `analysis.py`, `value_objects.py`, `factory.py`) e a parte pura de `application/skymap/{analyze.py,generate.py,dto.py,ports.py}` (sem dependência de `domain.radiosources`) para `packages/radioskysims-skymap/src/radioskysims_skymap/`.
- Motivo do pacote dedicado (em vez de dobrar em `sources`): `domain/skymap` usa `healpy` e é consumido tanto por cosmologia (`radioskysims-sources`, Fase 4) quanto por mapmaking (`radioskysims-simulation`, Fase 5) — um pacote separado evita que `simulation` dependa de `sources` só para pegar o tipo `SkyMap`, e evita inflar `core` com `healpy`.
- `application/skymap/generate_continuum.py` (usa `domain.radiosources.continuum.Galaxy`) **não** entra aqui — vai para a Fase 4 junto com `radioskysims-sources`, que depende de `radioskysims-skymap`.
- Verificação: `uv sync --package radioskysims-skymap` instala com core + healpy, sem astroquery/pyccl/camb/dask; testes de `tests/domain/skymap/*` e `tests/application/skymap/*` (parte pura) passam isolados.

### Fase 4 — `radioskysims-sources` + `radioskysims-radiotelescope` + `gnsstools4astro` (depende das Fases 1 e 3; pode rodar em paralelo com a Fase 2)
- `radioskysims-sources`: consolidar `domain/satellite/*`, `domain/localsources/*`, `domain/radiosources/*` (inclui `continuum.py` = ContinuumSources + CosmologicalSource), `domain/cosmology/*`, `domain/catalog/*` (CatalogIngestion, CatalogQuery), `domain/signal/*` (SignalDefinition/SatSignal — sinal GNSS), `domain/signal_source.py` + `domain/signal_source_group.py` (protocolo unificado `SignalSource` e adapters — é o contrato que `radioskysims-simulation` consome, não o contrário), seus serviços (`satellite_service.py`, `local_sources_service.py`, `catalog_services.py`, `source_assembler.py`), infraestrutura (repositórios de satélite/radiosources, `solar_flux_repository.py`+downloader, adapters de cosmologia pyccl/healpy), use cases (`radiosources_use_cases.py`, `cosmology/generate_hi_map*.py`, `application/skymap/generate_continuum.py`) e `interfaces/gui/satellite_panel.py` (refatorado sobre `PanelApplication`). Depende de `radioskysims-core` + `radioskysims-skymap`.
- `radioskysims-radiotelescope`: `domain/radiotelescope/*`, `application/radiotelescope_panel.py`, lógica de `build_radiotelescope_from_settings` (usa `ConfigPort` genérico do core).
- Mover `src/GNSStools4Astro/gnsstools4astro` para `packages/gnsstools4astro/` como membro do workspace (sem mudança de código — auditoria já confirmou zero imports cruzados `radioskysims → gnsstools4astro` fora de testes/exemplos). `bingo`, `analysis`, `arpls` permanecem vendorizados como estão — fora de escopo, anotar como limpeza futura. `domain/map` (stub vazio, sem uso, designado a outro colaborador) também fica fora de escopo — não migrar até ter implementação real.
- Verificação: suites de sources/radiotelescope passam isoladas; `radioskysims-sources` declara deps pesadas (pyccl, camb, healpy, astroquery, georinex) para não vazarem para pacotes leves.

### Fase 5 — `radioskysims-simulation` (mais acoplado; depende das Fases 1, 3 e 4, é o integrador)
- Mover `domain/tod/*`, `domain/simulation/*`, `domain/noise/*`, `domain/rfi/*`, `infrastructure/mapmaking/*`, `application/services/{simulation_service,tod_orchestrator,sim_orchestrator}.py` (com o dataclass `SimulationContext`), `application/mapmaking/generate_from_tod.py`, `application/tod_panel.py` (→ `PanelApplication`), e a parte de chunking/scheduler dask do `resource_processor.py`.
- Refatorar [bootstrap/builders.py](src/radioskysims/bootstrap/builders.py) (hoje 450 linhas monolíticas) em builders por pacote (`radioskysims_beam.bootstrap.build_beam_components()`, `radioskysims_sources.bootstrap.build_sources_components()`, etc.), com o `bootstrap/builders.py` do pacote guarda-chuva reduzido a compor essas chamadas (strategy pattern) — resolve o acoplamento crítico #4 do relatório de auditoria.
- Verificação: suite completa de `tests/e2e/` e `tests/integration/` verde; `create_sim_orchestrator()` produz `SimulationContext` funcionalmente idêntico (sem mudança de comportamento esperada).

### Fase 6 — `radioskysims-waterfall` (novo; pode rodar em paralelo com Fases 4/5, sem legado)
- Criar `packages/radioskysims-waterfall/` do zero seguindo o padrão hexagonal: `domain/waterfall/models.py` (value object Waterfall: array 2D freq×tempo + metadados), `application/ports/waterfall.py` (`WaterfallLoaderPort`, `SpectrumAnalysisPort`), `application/waterfall_panel.py` (subclasse de `PanelApplication`, usando holoviews+**datashader** — natural aqui dado o volume de dados de TOD/waterfall), utilitários básicos de SED/spectrum como funções puras no domínio, infraestrutura mínima (loader simples, netcdf ou in-memory).
- Escopo: implementação básica/MVP (conforme decidido), não feature-completa. Testes próprios desde o início.
- Depende de `radioskysims-core` + `radioskysims-viz`; integração opcional com `radioskysims-simulation` via porta (sem dependência rígida).

### Fase 7 — Consolidação final / meta-pacote / limpeza (depende de todas as anteriores)
- Root `pyproject.toml` (distribuição guarda-chuva `radioskysim`) declara dependência de todos os sub-pacotes por padrão, com extras seletivos (`radioskysim[beam]`, `radioskysim[simulation]`, `radioskysim[all]`, etc.).
- Remover shims de compatibilidade das Fases 1-6 (ou manter por um ciclo de depreciação — decisão a confirmar com usuário).
- Atualizar `docs/architecture.md` com diagrama de módulos refletindo os novos limites de pacote (usar workflow Mermaid do repo: validar com `mermaid-diagram-validator`, prévia com `mermaid-diagram-preview`, seguindo `.github/instructions/mermaid.instructions.md`).
- Atualizar `AGENTS.md` com a nova convenção de layout (`packages/<nome>/src/<nome_import>/{domain,application,ports,adapters}`).
- Atualizar `[tool.coverage.run].source` e config de mypy/ruff para incluir os novos nomes de pacote.
- Rodar suite completa + checagem de cobertura como gate final.

## Relevant files
- `pyproject.toml` — build-system, workspace, extras, entry points, coverage/mypy source lists.
- `src/radioskysims/bootstrap/builders.py`, `composition.py` — composition root a ser fatiado em strategy pattern.
- `src/radioskysims/infrastructure/config/config_loader.py`, `infrastructure/db/engine.py`+`models.py`, `infrastructure/logging_config.py`, `paths.py`, `infrastructure/processing/resource_processor.py` — candidatos ao `radioskysims-core`.
- `src/radioskysims/application/beam_panel.py`, `gain_panel.py`, `radiotelescope_panel.py`, `tod_panel.py`, `interfaces/gui/skymap/{app,controller,views,widgets,presenters,state}.py`, `interfaces/gui/satellite_panel.py` — fonte de padrões para `PanelApplication` comum.
- `src/radioskysims/domain/{beam,satellite,localsources,radiosources,radiotelescope,tod,simulation}/*` — código de domínio a mover por pacote (ver tabela "Mapeamento de domínio → pacote" para os módulos menores).
- `src/radioskysims/domain/{common,geometry,tracks}/*` — kernel de domínio compartilhado, candidatos ao `radioskysims-core` (Fase 1).
- `src/radioskysims/domain/skymap/*` + `application/skymap/{analyze,generate,dto,ports}.py` — candidatos ao `radioskysims-skymap` (Fase 3).
- `src/radioskysims/domain/{signal,catalog}.py`, `signal_source.py`, `signal_source_group.py`, `domain/cosmology/*`, `application/cosmology/*`, `application/skymap/generate_continuum.py` — candidatos ao `radioskysims-sources` (Fase 4).
- `src/radioskysims/domain/{noise,rfi}/*` — candidatos ao `radioskysims-simulation` (Fase 5).
- `src/radioskysims/domain/map/*` — stub sem implementação, fora de escopo por ora.
- `src/GNSStools4Astro/RinexDownloader/pyproject.toml` — template de pyproject standalone já existente (precedente).
- `src/GNSStools4Astro/gnsstools4astro/` — mover para `packages/gnsstools4astro/`.
- `.prompts/decoupling.md` — documento de contexto/especificação original do usuário.
- `tests/` (148 arquivos, espelha `src/radioskysims/`) — mover junto com o código por fase para `packages/<nome>/tests/`.
- `docs/architecture.md`, `AGENTS.md` — atualizar na Fase 7.

## Verification
1. Após cada fase: `pytest tests/` (ou `uv run --package <nome> pytest` para o pacote isolado) deve permanecer verde — nenhuma mudança de comportamento esperada, apenas reorganização.
2. Testar instalação seletiva: `uv sync --package radioskysims-beam` não deve instalar dask/pyccl/camb/psycopg2 (prova de que o objetivo de "instalar só algumas partes" foi atingido). Idem `radioskysims-skymap` não deve instalar astroquery/pyccl/camb/dask.
3. `uv sync` (workspace completo) reproduz o ambiente atual sem regressão de versões de dependências.
4. Ao final da Fase 5: `tests/e2e/` e `tests/integration/` continuam verdes com comportamento idêntico do `SimOrchestrator`.
5. Ao final da Fase 7: diagrama Mermaid de arquitetura validado (`mermaid-diagram-validator`) e visualizado (`mermaid-diagram-preview`) antes de commitar.

## Decisions
- uv workspace (não Poetry) — decidido com usuário.
- Consolidar 18 módulos do `.prompts/decoupling.md` em **9 pacotes** por acoplamento real (`core`, `skymap`, `viz`, `beam`, `sources`, `radiotelescope`, `simulation`, `waterfall`, `gnsstools4astro`) — decidido com usuário em 2026-08-29 (revisão da estimativa inicial de ~8).
- Piloto: `radioskysims-core` + `radioskysims-beam` + `radioskysims-viz` — decidido com usuário.
- WaterfallTools: incluir implementação básica (MVP) — decidido com usuário.
- Nomenclatura própria por pacote (`radioskysims_beam`, etc.) em vez de namespace PEP 420 único — **confirmado com usuário em 2026-08-29**.
- `domain/geometry` + `domain/tracks` no `radioskysims-core` — **confirmado com usuário em 2026-08-29**.
- `domain/skymap` em pacote dedicado `radioskysims-skymap` (Fase 3), não dobrado em `sources` — **confirmado com usuário em 2026-08-29**.
- `bingo`, `analysis`, `arpls` ficam fora de escopo (vendorizados, baixo acoplamento, sem uso crítico). `domain/map` (stub sem implementação) também fora de escopo por ora.
- **Testes movem junto com o código de cada fase** para `packages/<nome>/tests/` (não ficam centralizados em `tests/` na raiz) — **confirmado com usuário em 2026-08-29**. Cada pacote testável isoladamente via `uv run --package <nome> pytest`.
- **Shims de compatibilidade mantidos até a Fase 7** (ciclo de depreciação completo; cada fase deixa o import antigo reexportando do novo caminho, marcado deprecated) — **confirmado com usuário em 2026-08-29**. Remoção só acontece na Fase 7.

## Further Considerations
1. **`radioskysims_signal_source` como fronteira sources↔simulation**: o protocolo `SignalSource` (e adapters) fica em `sources`, mas é o único ponto de acoplamento onde `simulation` importa tipos de `sources` diretamente (`SatelliteSignalSource`, `LocalSourceSignalSource`, `RadioSourceSignalSource`). Se no futuro for necessário desacoplar ainda mais, considerar extrair esse protocolo para `core` como uma `Port` genérica — não necessário agora.

### Anotações de revisão técnica (arquivo separado)
Anotações e recomendações detalhadas foram extraídas para:
`.github/prompts/plan-radioSkySimDecoupling.review.md`
Por favor, consulte esse arquivo para leitura aprofundada e checklist de implementação.
