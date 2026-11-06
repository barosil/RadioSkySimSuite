# Bounded Contexts e Contratos do RadioSkySimSuite

**Data:** 2026-09-01 (atualizado — mapeamento para pacotes pós-desacoplamento)
**Status:** ativo
**Arquitetura:** Hexagonal (Ports and Adapters)

Este documento consolida os bounded contexts principais e seus contratos de
integração. A versão detalhada e histórica permanece em
`docs/architecture/_bounded_contexts.md`.

## Mapeamento context → pacote (uv workspace)

Desde o desacoplamento (Fases 1–7, ver `docs/decoupling/`), cada bounded
context abaixo corresponde a um pacote próprio em `packages/*` (submódulo
git), exceto onde indicado:

| Bounded context | Pacote | CLI própria |
|---|---|---|
| SkyMap | `radioskysims-skymap` | via `radioskysims` (umbrella) |
| Satellite + LocalSources + RadioSources | `radioskysims-sources` | `radioskysim-sources` |
| Beam | `radioskysims-beam` | — |
| RadioTelescope | `radioskysims-radiotelescope` | — |
| TOD + Simulation | `radioskysims-simulation` | via `radioskysims tod export` |
| Waterfall | `radioskysims-waterfall` | — |
| GNSS/RINEX (satélites via efemérides broadcast) | `gnsstools4astro` | `gnss4astro` |
| Kernel compartilhado (config/db/logging/paths/geometry/tracks comuns) | `radioskysims-core` | — |
| Visualização reutilizável (`PanelApplication`, `VisualizerPort`) | `radioskysims-viz` | — |

Nota: `Satellite`, `LocalSources` e `RadioSources` — tratados como três
contexts separados nas seções abaixo por clareza de contrato — vivem hoje no
**mesmo pacote** (`radioskysims-sources`), cada um em seu próprio submódulo de
`domain/application/infrastructure` interno.

## SkyMap Context

Responsável por geração, transformação e análise de mapas HEALPix.

### Contratos do SkyMap

- `SkyMapGeneratorPort.generate(nside, freq_ghz, components) -> SkyMap`
- `SkyMapAnalyzerPort.compute_cls(skymap, lmax) -> ndarray`
- `SkyMapIOPort.read_map(path, nside, unit, frame, field) -> SkyMap`
- `SkyMapIOPort.write_map(skymap, path, overwrite) -> Path`

### Unidades e regras do SkyMap

- Frequência de entrada/saída: MHz (usuário)
- Manipulação angular interna: radianos

## Satellite Context

Responsável por elementos orbitais, seleção e tracks de satélites.

### Contratos do Satellite

- `GeometryProviderPort.compute(tracks, observer, sat_block) -> xr.Dataset`
- `GeometryProviderPort.calculate_position(...) -> (theta, phi, range)`
- `GeometryProviderPort.calculate_range(...) -> Distance`

### Unidades e regras do Satellite

- Tempo interno: MJD/JD (UTC)
- Entrada temporal: ISO (convertida internamente)
- Ângulos para usuário: graus; interno: radianos

## Beam Context

Responsável por carregamento e avaliação de padrões de feixe.

### Contratos do Beam

- `BeamLoaderPort.load(source) -> Beam`
- `BeamEvaluatorPort.evaluate(beam, frequency, angle, polarization) -> xr.DataArray`
- `BeamEvaluatorPort.compute_properties(beam) -> dict`

### Unidades e regras do Beam

- Frequência: MHz
- Ângulo interno: radianos

## RadioSources Context

Responsável por ingestão de catálogos e avaliação de fluxo espectral.

### Contratos do RadioSources

- `RadioSourcesCatalogPort.query_sources(...) -> list[RadioSource]`
- `RadioSourcesFluxPort.evaluate_flux(sources, freqs_ghz) -> list[RadioSourceFluxSample]`
- `CatalogIngestPort.ingest_from_tap(survey, adql_query) -> DataFrame`
- `RadioSourcesRepositoryPort.save_sources(sources) -> None`

### Unidades e regras do RadioSources

- Fluxo: Jy
- Frequência de referência: GHz no modelo espectral; conversão explícita quando necessário

## LocalSources Context

Responsável por fontes locais (Sol) com fluxo solar real e track via Skyfield.
Vive no mesmo pacote de `RadioSources`/`Satellite` (`radioskysims-sources`),
em submódulo `domain/application` próprios.

### Contratos do LocalSources

- `LocalSourcesPort.get_flux(date_range) -> LocalSourceFlux`
- `LocalSourcesPort.get_track(observer, date_range) -> xr.Dataset`

### Unidades e regras do LocalSources

- Fluxo solar: SFU (download SRD/SRS, com cache local em `data/solar_flux/`)
- Tempo interno: UTC/MJD

## RadioTelescope Context

Responsável pela modelagem do radiotelescópio (antena, backend de
espectrômetro, perfis de configuração via `settings.toml`). Pacote:
`radioskysims-radiotelescope`.

### Contratos do RadioTelescope

- `build_configuration(telescope: str) -> RadiotelescopeConfig`

### Unidades e regras do RadioTelescope

- Frequência: MHz
- Temperatura de sistema: Kelvin

## TOD Context

Responsável pela síntese de Time Ordered Data a partir de geometria, beam e sinais.

### Contrato do TOD

- `TODSimulator.simulate(sat, beam, geometry, gain) -> xr.Dataset`

### Unidades e regras do TOD

- Temperatura de antena: Kelvin
- Tempo interno: UTC/MJD

## Simulation Context

Responsável pela orquestração end-to-end entre os contexts.

### Contratos consumidos pelo Simulation

- Ports de Satellite, Beam, SkyMap, RadioSources, LocalSources, RadioTelescope e TOD
- Resultado agregado: `SimulationResult` / `SimulationOrchestratorResult`
- Persistência via `SimulationRepositoryPort` (HDF5/Zarr + metadados PostgreSQL)
- Processamento resource-aware via `ResourceAwareProcessor` (batches + Dask)

## Waterfall Context

Responsável por ferramentas de análise de waterfall (tempo × frequência):
máscara, baseline, filtros, SED e light curves. Pacote:
`radioskysims-waterfall` (autônomo — não depende de `core`/`viz`;
integração com `Simulation` via porta, sem dependência rígida).

### Contratos do Waterfall

- `WaterfallLoaderPort.load(source) -> WaterfallDataset`
- `WaterfallStoragePort.save(dataset, path) -> Path`

### Unidades e regras do Waterfall

- Tempo/frequência na mesma convenção dos demais contexts (segundos/MHz)

## Regras transversais de integração

- Persistência principal em PostgreSQL (SQLModel)
- Cache de execução em `data/temp`
- Downloads externos preferencialmente por `httpx` assíncrono
- Logs estruturados JSON com eventos categorizados (`http`, `io`, `db`)
