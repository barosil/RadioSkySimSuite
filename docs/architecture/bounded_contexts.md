# Bounded Contexts e Contratos do RadioSkySim

**Data:** 3 de março de 2026  
**Status:** ativo  
**Arquitetura:** Hexagonal (Ports and Adapters)

Este documento consolida os bounded contexts principais e seus contratos de integração.
A versão detalhada e histórica permanece em `docs/architecture/_bounded_contexts.md`.

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

- Ports de Satellite, Beam, SkyMap, RadioSources e TOD
- Resultado agregado: `SimulationResult`

## Regras transversais de integração

- Persistência principal em PostgreSQL (SQLModel)
- Cache de execução em `data/temp`
- Downloads externos preferencialmente por `httpx` assíncrono
- Logs estruturados JSON com eventos categorizados (`http`, `io`, `db`)
