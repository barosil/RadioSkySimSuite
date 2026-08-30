# Bounded Contexts do RadioSkySim

**Data:** 3 de fevereiro de 2026  
**Versão:** 1.0  
**Padrão:** Domain-Driven Design (DDD)  
**Arquitetura:** Ports & Adapters + Event-Driven

---

## 📋 Índice

1. [SkyMap Context](#1-skymap-context)
2. [Satellite Context](#2-satellite-context)
3. [Beam Context](#3-beam-context)
4. [RadioSources Context](#4-radiosources-context)
5. [TOD Context](#5-tod-context)
6. [Simulation Context](#6-simulation-context)
7. [Relações entre Contexts](#7-relações-entre-contexts)
8. [Fluxos de Eventos](#8-fluxos-de-eventos)
9. [Anti-Corruption Layers](#9-anti-corruption-layers)
10. [Resumo Visual e Padrões](#10-resumo-visual-e-padrões)

---

## 1. SkyMap Context

### Responsabilidade

Representação, manipulação e análise de mapas do céu em formato HEALPix. Define o contrato para operações de I/O, transformações geométricas e análise espectral de mapas.

### Entidades

- **`SkyMap`** (Aggregate Root)
  - Mapa do céu HEALPix imutável
  - Propriedades: `nside`, `unit`, `frame`, `freq_ghz`, `field`
  - Operações: `copy()`, `apply_mask()`, `alm()` (transformada esférica)
  - Encapsula dados via `SkyMapDataset` (abstração numpy/xarray/dask)

### Value Objects

- **`NSide`**
  - Resolução HEALPix (potência de 2)
  - Imutável, hashable
  - Calcula automaticamente `npix` (número de pixels)

- **`SkyMapDataset`**
  - Abstração de dados (suporta numpy, xarray, dask)
  - Conversão transparente para numpy
  - Propriedades: `shape`, `ndim`, `size`

### Serviços de Domínio

- **`SkyMapFactory`**
  - Criação segura de SkyMaps com validação
  - Métodos: `create()`, `from_array()`, `from_file()`

- **`MapAnalysis`** (futura expansão)
  - Operações espectrais: `mean()`, `statistics()`
  - Cálculo de C_l (espectro angular)

### Serviços de Aplicação

- **`GenerateSkyMapUseCase`**
  - Orquestra `SkyMapGeneratorPort` (injeção de dependência)
  - Suporta múltiplos geradores (PySM3, WebSky, etc)

### Ports (Interfaces)

```python
# Application Layer
SkyMapGeneratorPort:
    - generate(nside, freq_ghz, components) -> SkyMap

SkyMapAnalyzerPort:
    - compute_cls(skymap, lmax) -> ndarray

SkyMapMaskPort:
    - apply(skymap, mask) -> SkyMap

# Infrastructure Layer
SkyMapIOPort:
    - read_map(path, nside, unit, frame, field) -> SkyMap
    - write_map(skymap, path, overwrite) -> Path

SkyMapTransformPort:
    - smooth(skymap, fwhm_rad) -> SkyMap
    - rotate(skymap, rot) -> SkyMap
    - downgrade(skymap, target_nside) -> SkyMap
```

### Adapters

- **`HealpySkyMapProvider`** → `SkyMapIOPort`, `SkyMapTransformPort`
  - Implementa I/O e transformações usando HEALPy
  - Telemetria integrada

- **`PySMSkyMapGeneratorAdapter`** → `SkyMapGeneratorPort`
  - Geração sintética com componentes PySM3
  - Suporta: synchrotron, dust, freefree, ame, cmb

- **`HealpySkyMapAnalyzer`** → `SkyMapAnalyzerPort`
  - Cálculo de C_l via HEALPy's `anafast()`

### Agregado Root

**`SkyMap`** é o Aggregate Root. Garante consistência dos dados internos:
- Imutabilidade externa (dados via `data` property)
- Validação em construção
- Operações retornam novos SkyMaps (padrão funcional)

### Anti-Corruption Layer

**Não necessário** — HEALPy é estável e bem documentado. O `HealpySkyMapProvider` atua como adapter técnico.

### Eventos de Domínio

- `SkyMapCreated` (futuro)
- `SkyMapAnalyzed` (futuro)
- `SkyMapTransformed` (futuro)

### Dependências (Entrantes)

- ← **Simulation Context**: orquestra geração de SkyMap
- ← **TOD Context**: lê dados do SkyMap

---

## 2. Satellite Context

### Responsabilidade

Modelos orbitais, trajetórias de satélites e suas propriedades físicas. Define contrato para cálculos de posição e geometria observacional.

### Entidades

- **`Satellite`** (Aggregate Root)
  - NORAD ID, nome, constelação
  - `OrbitalElement`: parâmetros TLE (época, a, e, i, etc)
  - Validação: intervalo válido de época
  - Imutável após criação

- **`SatelliteAssembled`**
  - Satélite com dados derivados
  - `tracks`: Dataset xr (theta, range, az, el)
  - `signals`: Dataset xr (frequência, modulação, PSD)

### Value Objects

- **`OrbitalElement`**
  - Encapsula parâmetros TLE
  - Propriedades: `epoch`, `semi_major_axis`, `eccentricity`, `inclination`, `raan`, `arg_perigee`, `mean_anomaly`

- **`TimeRange`** (compartilhado)
  - Intervalo temporal (ISO strings ou JD)
  - Conversão para Skyfield, numpy, astropy

### Serviços de Domínio

- **`SatelliteFactory`**
  - Criação a partir de NORAD IDs ou constelações
  - Busca em `SatelliteRepository` (SpaceTrack)
  - Validação de épocas

- **`SatelliteAssembler`**
  - Agrega dados de órbita + sinais
  - Usa `TrackFactory` + `SignalFactory`

### Ports (Interfaces)

```python
# Infrastructure Layer
GeometryProviderPort:
    - compute(tracks, observer, sat_block) -> xr.Dataset
    - calculate_position(satellite, time, lat, lon) -> (theta, phi, range)
    - calculate_range(satellite, time, lat, lon) -> Distance
```

### Adapters

- **`SkyfieldGeometryProvider`** → `GeometryProviderPort`
  - Cálculos orbitais via Skyfield
  - Retorna theta (ângulo zenital), range, az, el

### Agregado Root

**`Satellite`** é o Aggregate Root. Garants:
- Identidade única (NORAD ID)
- Validação de época orbital
- Imutabilidade após criação

`SatelliteAssembled` é uma entidade derivada (composition).

### Anti-Corruption Layer

**`SatelliteRepository`** → SpaceTrack API
- Traduz JSON SpaceTrack → `Satellite`
- Cache local via SQLite/PostgreSQL

### Eventos de Domínio

- `SatelliteCreated` (futuro)
- `SatelliteTracksCalculated` (futuro)

### Dependências (Entrantes)

- ← **Simulation Context**: seleciona satélites
- ← **TOD Context**: lê trajetórias (theta, range, PSD)

---

## 3. Beam Context

### Responsabilidade

Padrão de radiação do radiotelescópio em função de frequência e ângulo. Define contrato para carregamento, avaliação e propriedades de feixes.

### Entidades

- **`Beam`** (Aggregate Root)
  - Padrão de radiação 3D: B(freq, angle)
  - Armazenado como xr.Dataset
  - Dimensões: `frequency`, `angle`, `polarization` (opcional)
  - Operações: `evaluate()`, `params()`

### Value Objects

- **`BeamParamsDomain`**
  - Propriedades calculadas do feixe
  - `polarizations`, `frequencies`, `fwhm`, `directivity`, `directivity_db`, `main_lobe_efficiency`
  - Imutável, para relatórios

### Serviços de Domínio

- **`BeamFactory`**
  - Criação de Beams a partir de diferentes fontes
  - Métodos: `create()`, `from_hdf5()`, `from_csv()`

- **`BeamProperties`**
  - Cálculo de propriedades físicas (FWHM, directividade)
  - Extrai características do dataset

### Ports (Interfaces)

```python
# Infrastructure Layer
BeamLoaderPort:
    - load(source) -> Beam

BeamEvaluatorPort:
    - evaluate(beam, frequency, angle, polarization) -> xr.DataArray
    - compute_properties(beam) -> dict

BeamCreatorPort:
    - create(frequency, angle, amplitudes, polarizations) -> Beam
```

### Adapters

- **`BeamLoader`** (abstract) → `BeamLoaderPort`
  - Implementações: `CSVBeamLoader`, `LITBeamLoader`, `CustomBeamLoader`
  - Carregam dados de diferentes formatos

### Agregado Root

**`Beam`** é o Aggregate Root. Garante:
- Integridade dos dados (dimensões consistentes)
- Avaliação segura (interpolação com bounds checking)

### Anti-Corruption Layer

**`BeamLoaderPort`** abstraem formatos específicos (CSV, HDF5, LIT).

### Eventos de Domínio

- `BeamLoaded` (futuro)
- `BeamPropertiesComputed` (futuro)

### Dependências (Entrantes)

- ← **TOD Context**: solicita avaliação de beam
- ← **Simulation Context**: orquestra carregamento

---

## 4. RadioSources Context

### Responsabilidade

Fornecer uma visão consistente de **fontes de rádio contínuas** (catálogos + mapas), permitindo estimar fluxo em frequência (e, no futuro, polarização e variabilidade) para consumo principalmente pelos contexts **TOD** e **Simulation**.

### Entidades

- **`RadioSource`** (Aggregate Root)
  - Identidade da fonte (ex.: nome NVSS, ID interno)
  - Propriedades principais: `ra_deg`, `dec_deg`, `reference_freq_ghz`, `flux_ref_jy`, `spectral_index`, `spectral_model`
  - Invariantes: `0 ≤ ra_deg < 360`, `-90 ≤ dec_deg ≤ 90`, `flux_ref_jy > 0`

- **`SpectralModel`** (Value Object)
  - MVP: lei de potência $S(\nu) = S_0 (\nu/\nu_0)^{-\alpha}$
  - Parâmetros: `nu0_ghz`, `s0_jy`, `alpha`
  - Operações: `evaluate(freq_ghz)` → fluxo em Jy

- **`RadioSourceFluxSample`** (Value Object)
  - Amostra de fluxo de uma fonte em uma dada frequência
  - Campos: `source_id`, `freq_ghz`, `flux_jy`

### Serviços de Domínio

- **`RadioSourcesFluxService`**
  - Dado um conjunto de `RadioSource` + frequências, retorna lista de `RadioSourceFluxSample`.
  - Encapsula uso de `SpectralModel`.

### Ports (Interfaces de Saída)

Esses são os contratos que outros bounded contexts utilizam.

```python
class RadioSourcesCatalogPort(Protocol):
    def query_sources(
        self,
        ra_deg: float,
        dec_deg: float,
        radius_deg: float,
        min_flux_jy: float | None = None,
        freq_ghz: float | None = None,
        limit: int | None = None,
    ) -> list[RadioSource]:
        ...


class RadioSourcesFluxPort(Protocol):
    def evaluate_flux(
        self,
        sources: list[RadioSource],
        freqs_ghz: list[float],
    ) -> list[RadioSourceFluxSample]:
        ...


class RadioSourcesSkyFluxPort(Protocol):
    def evaluate_sky_contribution(
        self,
        theta_rad: float,
        phi_rad: float,
        freqs_ghz: list[float],
        radius_deg: float,
        min_flux_jy: float | None = None,
    ) -> list[RadioSourceFluxSample]:
        ...
```

- **Consumidores típicos**:
  - **TOD Context**: cálculo de contribuição de fontes brilhantes por linha de visada.
  - **Simulation Context**: seleção de populações de fontes para cenários específicos.

### Ports (Interfaces de Entrada / Infraestrutura)

Abstraem ingestão de catálogos e persistência.

```python
class CatalogIngestPort(Protocol):
    def ingest_from_tap(self, survey: str, adql_query: str) -> "DataFrame":
        ...

    def ingest_from_file(self, path: Path, format: str) -> "DataFrame":
        ...


class RadioSourcesRepositoryPort(Protocol):
    def save_sources(self, sources: list[RadioSource]) -> None:
        ...

    def list_sources_in_region(
        self,
        ra_deg: float,
        dec_deg: float,
        radius_deg: float,
        min_flux_jy: float | None = None,
    ) -> list[RadioSource]:
        ...
```

- Implementações candidatas:
  - `VizierTapIngestAdapter` (TAP/ADQL seguro para NVSS, SPECFIND, etc.).
  - `FitsContinuumMapIngestAdapter` (RACS, HiPS, HDF5).
  - `SqlRadioSourcesRepository` (Postgres, via SQLAlchemy/SQLModel).

### Serviços de Aplicação

- **`BuildRadioSourcesCatalogUseCase`**
  - Usa `CatalogIngestPort` + `RadioSourcesRepositoryPort` para criar/atualizar o catálogo normalizado.

- **`QueryRadioSourcesUseCase`**
  - Fachada application‑level sobre `RadioSourcesRepositoryPort` com validação extra de parâmetros.

- **`ComputeRadioSourcesForegroundUseCase`**
  - Entrada típica: posição ($\theta,\phi$), beam FWHM, lista de frequências, `min_flux_jy`.
  - Usa `RadioSourcesCatalogPort` + `RadioSourcesFluxPort` para produzir contribuição de foreground discreto.

### Adapters

- **`VizierTapIngestAdapter`** → `CatalogIngestPort`
  - Implementa queries assíncronas/robustas NVSS + SPECFIND via TAP.

- **`PostgresRadioSourcesRepository`** → `RadioSourcesRepositoryPort`
  - Normaliza catálogo em tabelas SQL (schema dedicado `radiosources`).

- **`ContinuumMapSlicer`** → (futuro) integração com SkyMap/Beam para mapas contínuos.

### Agregado Root

**`RadioSource`** é o Aggregate Root:

- Garante consistência de coordenadas e parâmetros espectrais.
- Exposição de API de alto nível (`to_spectral_model()`, etc.).

### Anti-Corruption Layer

- **TAP/ADQL ↔ Domínio**: adapters de ingestão convertem tabelas NVSS/SPECFIND/RACS em `RadioSource` + `SpectralModel`.
- **FITS/HiPS ↔ Domínio**: adapters de mapas contínuos convertem arquivos em estruturas xarray/SkyMap sem vazar detalhes para o domínio.

### Dependências (Entrantes)

- ← **TOD Context**: consulta fontes dentro do beam e fluxo por canal de frequência.
- ← **Simulation Context**: monta catálogos e cenários de foreground discreto.

---

## 5. TOD Context

### Responsabilidade

Simulação de Time-Ordered Data (dados ordenados no tempo) da observação. Integra Beam, Satellite e Geometry para produzir TOD.

### Entidades

- **`TODSimulator`** (Domain Service, não Aggregate)
  - Calcula sinal observado: T_ant(t, ν)
  - Fórmula física: `T_ant = G · B(θ(t), ν) · PSD(ν) · c² / [4π r(t)² ν² k_B]`
  - Entrada: satélite, beam, geometria
  - Saída: xr.Dataset(time, frequency)

### Value Objects

- **`TODResult`** (futuro)
  - Dataset com TOD + metadados
  - Dimensões: `time`, `frequency`
  - Variáveis: amplitude, fase (opcional), SNR

### Serviços de Aplicação

- **`TODService`**
  - Orquestra `TODSimulator` com dependências injetadas
  - Validação de inputs

### Dependências (Entrantes)

- ← **Simulation Context**: solicita cálculo de TOD
- ← **Beam Context**: carrega beam
- ← **Satellite Context**: obtém trajetória + PSD

### Acoplamento com Otros Contexts

```
TODSimulator.simulate(
    sat: SatelliteAssembled,     # do Satellite Context
    beam: Beam,                   # do Beam Context
    geometry: GeometryProvider,   # do Satellite Context
    gain: float
) -> xr.Dataset
```

---

## 6. Simulation Context

### Responsabilidade

Orquestração e composição da simulação completa. Coordena os demais contexts e compõe o resultado final.

### Entidades

- **`Simulation`** (Aggregate Root)
  - Satélites selecionados
  - Intervalo temporal
  - Estado: selected, ready, running, completed

- **`SimulationResult`** (Value Object)
  - Dataset xr com resultados
  - Lista de satélites
  - TimeRange utilizado

### Serviços de Domínio

- **`SimulationService`** (Application Layer)
  - Orquestra workflow completo
  - Sequência:
    1. Seleciona satélites (`Satellite Context`)
    2. Carrega beam (`Beam Context`)
    3. Calcula geometria (`Satellite Context`)
    4. Simula TOD (`TOD Context`)
    5. Agrega resultados

### Fluxo Workflow

```
SimulationService.execute()
├─ select_satellites() → List[Satellite]
├─ for satellite in satellites:
│  ├─ geometry = compute_geometry(satellite) → (theta, range, az, el)
│  ├─ tod = simulate_tod(satellite, beam, geometry) → xr.Dataset
│  └─ aggregate_results()
└─ return SimulationResult(dataset, satellites, time_range)
```

### Eventos de Domínio

- `SimulationStarted` (futuro)
- `SatelliteSelected` (futuro)
- `TODSimulated` (futuro)
- `SimulationCompleted` (futuro)

### Dependências (Saintes)

```
Simulation Context
├─→ SkyMap Context (carrega background)
├─→ Satellite Context (seleciona + geometria)
├─→ Beam Context (carrega padrão)
└─→ TOD Context (simula dados)
```

---

## 7. Relações entre Contexts

### Mapa de Dependências

```
┌─────────────────────────────────────────────────────────────────┐
│                   SIMULATION CONTEXT                            │
│                  (Orquestrador Central)                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SimulationService                                       │   │
│  │  - select_satellites()                                  │   │
│  │  - compute_geometry()                                   │   │
│  │  - simulate_tod()                                       │   │
│  │  - execute()                                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────┬──────────────┬────────────────┬────────────────────┘
           │              │                │
           ▼              ▼                ▼
    ┌──────────────┐ ┌───────────┐  ┌──────────────┐
    │   SATELLITE  │ │  BEAM     │  │   SKYMAP     │
    │   CONTEXT    │ │ CONTEXT   │  │   CONTEXT    │
    ├──────────────┤ ├───────────┤  ├──────────────┤
    │ Satellite    │ │ Beam      │  │ SkyMap       │
    │ GeometryProvider│ BeamLoader│  │ SkyMapFactory│
    │ SatelliteFactory│ BeamEvaluat│  │ Analyzer     │
    └──────────────┘ └───────────┘  └──────────────┘
           ▲              ▲                ▲
           │              │                │
           └──────────────┼────────────────┘
                          ▼
              ┌────────────────────────┐
              │   TOD CONTEXT          │
              │  (Integrador Físico)   │
              ├────────────────────────┤
              │ TODSimulator           │
              │  T_ant = G·B·PSD·c²/.. │
              └────────────────────────┘
```

### Comunicação Entre Contexts

#### Satellite Context → Simulation Context

```
SatelliteFactory.create()
  ↓
List[Satellite]
  ↓
(SatelliteAssembler.assemble() → SatelliteAssembled)
```

**Interface:** `SatelliteFactory`, `GeometryProviderPort`

#### Beam Context → TOD Context

```
BeamLoader.load()
  ↓
Beam
  ↓
TODSimulator.evaluate(beam, frequency, angle)
```

**Interface:** `BeamLoaderPort`, `BeamEvaluatorPort`

#### Satellite Context → TOD Context

```
SatelliteAssembled.psd()  → PSD(freq)
SatelliteAssembled.angle()  → theta(time)
SatelliteAssembled.range()  → r(time)
```

**Interface:** Properties do Aggregate `SatelliteAssembled`

#### SkyMap Context → Simulation Context

```
SkyMapGenerator.generate()
  ↓
SkyMap
  ↓
(futuro: contribuição para TOD)
```

**Interface:** `SkyMapGeneratorPort`

### Padrão de Comunicação

- **Direção:** Simulation Context → Others (inbound only)
- **Tipo:** Dependency Injection via Ports/Interfaces
- **Acoplamento:** Baixo (apenas via abstrações)

---

## 8. Fluxos de Eventos

### Fluxo Principal: Simulação Completa

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INICIAÇÃO                                                │
│    User input: select_by_ids([25544, 23002, ...])          │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SELEÇÃO (Satellite Context)                              │
│    SatelliteFactory.create_from_norad_ids(ids)              │
│    ↓                                                        │
│    → Satellite[] (com OrbitalElement)                       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ASSEMBLAGEM (Satellite Context)                          │
│    SatelliteAssembler.assemble(satellites, time_range)      │
│    ↓                                                        │
│    → SatelliteAssembled[] (com tracks, signals)             │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CARREGAMENTO (Beam Context)                              │
│    BeamLoader.load("beam_definition")                       │
│    ↓                                                        │
│    → Beam (xr.Dataset)                                      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. COMPUTAÇÃO DE TOD (TOD Context)                          │
│    FOR cada satellite:                                      │
│      geometry = GeometryProvider.compute(tracks, observer)  │
│      ↓                                                      │
│      tod = TODSimulator.simulate(                           │
│        sat,          # SatelliteAssembled                   │
│        beam,         # Beam                                 │
│        geometry,     # xr.Dataset (theta, range, az, el)   │
│        gain=G        # float                                │
│      )                                                      │
│      ↓                                                      │
│      → TOD (xr.Dataset, dims: time × frequency)            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. AGREGAÇÃO (Simulation Context)                           │
│    Combina TOD[] em resultado final                         │
│    ↓                                                        │
│    → SimulationResult(dataset, satellites, time_range)      │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados por Context

#### SkyMap Context
```
Input: nside, freq_ghz, components
  ↓
[SkyMapGeneratorPort]
  ↓
Output: SkyMap
  ├─ nside: NSide
  ├─ data: ndarray
  ├─ unit: str
  └─ frame: str
```

#### Satellite Context
```
Input: NORAD IDs, TimeRange
  ↓
[SatelliteFactory, GeometryProvider]
  ↓
Output: SatelliteAssembled[]
  ├─ tracks: xr.Dataset (time, satellite)
  │   ├─ theta(time)    : zenital angle
  │   ├─ range(time)    : distance
  │   ├─ az(time)       : azimuth
  │   └─ el(time)       : elevation
  └─ signals: xr.Dataset (freq, satellite)
      ├─ psd(freq)      : power spectral density [W/Hz]
      ├─ modulation     : type of signal
      └─ center_freq    : central frequency
```

#### Beam Context
```
Input: Beam definition (file/database)
  ↓
[BeamLoader]
  ↓
Output: Beam
  └─ dataset: xr.Dataset
      ├─ amplitude(frequency, angle)
      ├─ frequency (GHz)
      └─ angle (rad)
```

#### TOD Context
```
Input: SatelliteAssembled, Beam, Geometry
  ↓
[TODSimulator]
  ↓
Formula: T_ant(t,ν) = G · B(θ(t),ν) · PSD(ν) · c²/[4π r(t)² ν² k_B]
  ↓
Output: xr.Dataset
  └─ antenna_temperature(time, frequency)
      └─ Units: Kelvin [K]
```

---

## 9. Anti-Corruption Layers

### Definição

Camada (Adapter) que traduz linguagem/modelos externos para linguagem do domínio.

### Implementações

#### Satellite Context ↔ SpaceTrack API

**Responsabilidade:** Traduzir JSON SpaceTrack → `Satellite` domain entity

```python
# adapter/satellite_downloader.py
class SatelliteRepository:
    """Anti-Corruption Layer para SpaceTrack API"""
    
    def get_by_norad_id(self, norad_id: int) -> Satellite:
        # 1. Busca em SpaceTrack (JSON)
        tle_json = self._fetch_from_spacetrack(norad_id)
        
        # 2. Traduz para OrbitalElement (domínio)
        orbital_element = OrbitalElement(
            epoch=datetime.fromisoformat(tle_json['epoch']),
            semi_major_axis=tle_json['a'],
            # ...
        )
        
        # 3. Cria Satellite (domínio)
        return Satellite(
            norad_id=norad_id,
            name=tle_json['satname'],
            element=orbital_element,
            # ...
        )
```

#### Beam Context ↔ File Formats

**Responsabilidade:** Traduzir CSV/HDF5/LIT → `Beam` domain entity

```python
# adapters/beam_loader.py
class BeamLoaderCSV(BeamLoader):
    """Anti-Corruption Layer para CSV"""
    
    def load(self, path: str) -> Beam:
        # 1. Lê CSV
        df = pd.read_csv(path)
        
        # 2. Valida estrutura
        required_cols = ['frequency', 'angle', 'amplitude']
        # ...
        
        # 3. Cria Dataset (xr.Dataset)
        ds = xr.Dataset(...)
        
        # 4. Retorna Beam (domínio)
        return Beam(dataset=ds)
```

#### SkyMap Context ↔ File I/O

**Responsabilidade:** Traduzir FITS/HDF5 → `SkyMap`

```python
# infrastructure/skymap/providers/healpy.py
class HealpySkyMapProvider(SkyMapIOPort):
    """Anti-Corruption Layer para HEALPy"""
    
    def read_map(self, path, **kwargs) -> SkyMap:
        # 1. Lê com HEALPy (lib específica)
        data = healpy.read_map(path)
        
        # 2. Cria SkyMapDataset (abstração)
        dataset = SkyMapDataset(data)
        
        # 3. Retorna SkyMap (domínio)
        return SkyMap(
            dataset=dataset,
            nside=NSide(healpy.get_nside(data)),
            **kwargs
        )
```

### Localização

- `infrastructure/db/satellite/repository.py` — Satellite ↔ SpaceTrack
- `infrastructure/beams/loaders/*.py` — Beam ↔ File formats
- `infrastructure/skymap/providers/*.py` — SkyMap ↔ File I/O

---

## 10. Resumo Visual e Padrões

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║               RADIOSKYSIM BOUNDED CONTEXTS                     ║
║                                                                ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │                 SIMULATION CONTEXT                       │ ║
║  │              (Orquestrador Executivo)                    │ ║
║  │                                                          │ ║
║  │  Agreg Root: Simulation                                 │ ║
║  │  Services: SimulationService, Simulation                │ ║
║  │  Responsabilidade: Coordenar contextos                  │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║         ▲         ▲              ▲           ▲                 ║
║         └─────────┼──────────────┼───────────┘                 ║
║                   │              │                             ║
║  ┌────────────────┴──┐ ┌────────┴──────┐ ┌─────────────────┐  ║
║  │ SATELLITE       │ │  BEAM      │ │ SKYMAP          │  ║
║  │ CONTEXT         │ │ CONTEXT     │ │ CONTEXT         │  ║
║  ├────────────────┤ ├──────────────┤ ├─────────────────┤  ║
║  │Root: Satellite │ │Root: Beam    │ │Root: SkyMap     │  ║
║  │Services:       │ │Services:     │ │Services:        │  ║
║  │ -Factory       │ │ -Factory     │ │ -Factory        │  ║
║  │ -Assembler     │ │ -Loader      │ │ -Analyzer       │  ║
║  │ -GeometryProv  │ │ -Evaluator   │ │ -Generator      │  ║
║  └────────────────┘ └──────────────┘ └─────────────────┘  ║
║         │                │                  │                 ║
║         └────────────────┼──────────────────┘                 ║
║                          │                                    ║
║                   ┌──────▼──────┐                             ║
║                   │ TOD CONTEXT  │                             ║
║                   ├──────────────┤                             ║
║                   │Service:      │                             ║
║                   │ -Simulator   │                             ║
║                   │Formula:      │                             ║
║                   │ T_ant = G·B·…│                             ║
║                   └──────────────┘                             ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

### Por Bounded Context

| Context | Aggregate Root | Factory | Services | Ports |
|---------|---|---|---|---|
| **SkyMap** | SkyMap | SkyMapFactory | SkyMapFactory, MapAnalysis | GeneratorPort, AnalyzerPort, IOPort |
| **Satellite** | Satellite | SatelliteFactory | Factory, Assembler | GeometryProviderPort |
| **Beam** | Beam | BeamFactory | Factory, Properties | LoaderPort, EvaluatorPort |
| **TOD** | — | — | TODSimulator (Domain Service) | — |
| **Simulation** | Simulation | — | SimulationService | — |
| **RadioSources** | RadioSource | — | RadioSourcesFluxService, *UseCases* | CatalogPort, FluxPort, SkyFluxPort, RepositoryPort |

### Princípios SOLID Aplicados

1. **Single Responsibility Principle (SRP)**
   - Cada context tem responsabilidade clara e bem delimitada

2. **Open/Closed Principle (OCP)**
   - Ports permitem adicionar novos adapters sem alterar domínio

3. **Liskov Substitution Principle (LSP)**
   - Todos os adapters respeitam contrato do Port

4. **Interface Segregation Principle (ISP)**
   - Ports separados por responsabilidade (IOPort, TransformPort, etc)

5. **Dependency Inversion Principle (DIP)**
   - Domínio não depende de infraestrutura (injeção via Ports)

---

## Referências

- **Estrutura DDD:** `src/radioskysims/domain/`
- **Application Services:** `src/radioskysims/application/`
- **Adapters/Ports:** `src/radioskysims/infrastructure/`
- **Documentação Detalhada:** `docs/architecture/`
- **Diagramas:** `docs/source/diagrams/radioskysim_ddd_architecture.mmd`

---

**Versão:** 1.0 | **Atualizado:** 3 de fevereiro de 2026
