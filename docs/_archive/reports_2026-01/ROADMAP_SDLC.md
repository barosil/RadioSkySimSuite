# 🛣️ ROADMAP SDLC - RADIOSKYSIM

**Documento de Planejamento Técnico & Engenharia de Software**  
**Data:** 29 de janeiro de 2026  
**Versão:** 1.0  
**Status:** Recomendações de Próximas Fases

---

## 📋 Índice Executivo

| Fase | Duração | Foco | Impacto |
|------|---------|------|--------|
| **1: Consolidação** | 2 semanas | Arquitetura DDD | 🔴 Crítico |
| **2: Robustez** | 2 semanas | Testing & Logging | 🟠 Alto |
| **3: Expansão** | 2-3 semanas | Domínios Incompletos | 🟡 Médio |
| **4: Production** | 1-2 semanas | Polish & CI/CD | 🟢 Finalização |
| **Total Estimado** | **8-10 semanas** | **MVP → Production** | ✅ |

---

## Fase 1️⃣: CONSOLIDAÇÃO (Semanas 1-2)

### Objetivo
Consolidar arquitetura DDD, criar abstrações explícitas (Ports), reorganizar código.

### 1.1 Reorganizar Estrutura de Diretórios ⏱️ 6h

**Problema Atual:**
```
domain/skymap/
  ├── models.py
  ├── value_objects.py
  ├── factory.py
  ├── analyzer.py          ← Deveria ser infrastructure
  ├── download.py          ← Deveria ser infrastructure
  ├── analysis.py          ← Duplicado com infrastructure/
  └── visualization.py     ← Deveria ser infrastructure

infrastructure/skymap/
  ├── healpy_provider.py   ✓ Correto
  ├── pysm_generator.py    ✓ Correto
  ├── healpy_analysis.py   ← Duplicado
  ├── visualization.py     ← Duplicado
```

**Ação:**
```bash
# Estrutura alvo
domain/skymap/
  ├── __init__.py
  ├── models.py              (SkyMap entity)
  ├── value_objects.py       (NSide, SkyMapDataset)
  ├── factory.py             (SkyMapFactory)
  ├── operations.py          (Operações puras)
  └── exceptions.py

infrastructure/skymap/
  ├── __init__.py
  ├── providers/
  │   ├── __init__.py
  │   ├── healpy.py
  │   └── pysm.py
  ├── adapters/
  │   ├── __init__.py
  │   ├── analysis.py        (HealpySkyMapAnalyzer)
  │   └── visualization.py   (HealpyVisualizer)
  ├── io/
  │   ├── __init__.py
  │   ├── download.py
  │   └── cache.py
  └── __init__.py (exports)
```

**Checklist:**
- [ ] Mover `domain/skymap/analyzer.py` → `infrastructure/skymap/adapters/`
- [ ] Mover `domain/skymap/download.py` → `infrastructure/skymap/io/`
- [ ] Mover `domain/skymap/visualization.py` → `infrastructure/skymap/adapters/`
- [ ] Remover duplicatas
- [ ] Atualizar imports em todos os arquivos
- [ ] Rodar testes para validar

**Impacto:** ✅ Clareza arquitetural +30%

---

### 1.2 Criar Camada de Ports (Interfaces Explícitas) ⏱️ 4h
**PULAR**

**Problema:** Sem abstrações, implementações estão acopladas.

**Solução:**
```python
# infrastructure/ports/__init__.py

from abc import ABC, abstractmethod
from pathlib import Path
from radioskysims.domain.skymap.models import SkyMap
from radioskysims.domain.skymap.value_objects import NSide

class SkyMapProviderPort(ABC):
    """Interface para operações de SkyMap."""
    
    @abstractmethod
    def read_map(
        self,
        path: str | Path,
        *,
        nside: NSide | None = None,
        unit: str = "unknown",
        frame: str = "galactic",
        field: str = "I",
    ) -> SkyMap:
        """Ler mapa do céu de arquivo."""
        pass
    
    @abstractmethod
    def write_map(
        self,
        skymap: SkyMap,
        path: str | Path,
        *,
        overwrite: bool = False,
    ) -> Path:
        """Escrever mapa do céu em arquivo."""
        pass
    
    @abstractmethod
    def smooth(self, skymap: SkyMap, fwhm_rad: float) -> SkyMap:
        """Suavizar mapa com Gaussiana."""
        pass
    
    @abstractmethod
    def rotate(self, skymap: SkyMap, rot_matrix: np.ndarray) -> SkyMap:
        """Rotacionar mapa no céu."""
        pass
    
    @abstractmethod
    def downgrade(self, skymap: SkyMap, nside_out: NSide) -> SkyMap:
        """Downgrade para menor resolução."""
        pass


class GeometryProviderPort(ABC):
    """Interface para cálculos geométricos."""
    
    @abstractmethod
    def calculate_position(
        self,
        satellite,
        time: np.ndarray,
        observer_lat: float,
        observer_lon: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Retorna (theta, phi, range) em radianos e metros."""
        pass
    
    @abstractmethod
    def calculate_range(
        self,
        satellite,
        time: np.ndarray,
    ) -> np.ndarray:
        """Distância satélite-telescópio."""
        pass


class BeamProviderPort(ABC):
    """Interface para operações com feixes."""
    
    @abstractmethod
    def create_beam(self, **kwargs):
        """Criar feixe normalizado."""
        pass
    
    @abstractmethod
    def evaluate_beam(
        self,
        beam,
        frequency: float,
        angle: np.ndarray,
    ) -> np.ndarray:
        """Avaliar padrão de radiação."""
        pass
```

**Implementações:**
```python
# infrastructure/skymap/providers/healpy.py

from radioskysims.infrastructure.ports import SkyMapProviderPort

class HealpySkyMapProvider(SkyMapProviderPort):
    """Implementação usando HEALPy."""
    
    def read_map(self, path, *, nside=None, ...):
        # Implementação
        pass
    
    # ... outros métodos
```

**Impacto:** ✅ Testabilidade +40%, Desacoplamento +35%

---

### 1.3 Criar Hierarquia de Exceções ⏱️ 2h
**fazer**
**Arquivo:** `domain/exceptions.py`

```python
"""
Exceções de domínio do RadioSkySim.

Hierarquia:
    RadioSkySkyException (base)
    ├── SkyMapException
    │   ├── InvalidNSideError
    │   ├── InvalidMapDataError
    │   └── MapFormatError
    ├── SatelliteException
    │   ├── SatelliteNotFoundError
    │   ├── InvalidOrbitalElementError
    │   └── EphemerisError
    ├── SimulationException
    │   ├── SimulationFailedError
    │   ├── TimeRangeError
    │   └── ConvergenceError
    └── BeamException
        ├── InvalidBeamError
        └── InterpolationError
"""

class RadioSkySkyException(Exception):
    """Base exception para RadioSkySim."""
    pass


# SkyMap Exceptions
class SkyMapException(RadioSkySkyException):
    """Base para exceções de mapa do céu."""
    pass


class InvalidNSideError(SkyMapException):
    """NSide inválido (não é potência de 2 ou fora dos limites)."""
    
    def __init__(self, nside: int):
        super().__init__(
            f"NSide {nside} inválido. Deve ser potência de 2 entre 1 e 8192."
        )


class InvalidMapDataError(SkyMapException):
    """Dados de mapa inconsistentes."""
    pass


class MapFormatError(SkyMapException):
    """Formato de arquivo de mapa não suportado."""
    pass


# Satellite Exceptions
class SatelliteException(RadioSkySkyException):
    """Base para exceções de satélites."""
    pass


class SatelliteNotFoundError(SatelliteException):
    """Satélite não encontrado no repositório."""
    
    def __init__(self, norad_id: int):
        super().__init__(f"Satélite NORAD {norad_id} não encontrado.")


class InvalidOrbitalElementError(SatelliteException):
    """Elementos orbitais inválidos ou inconsistentes."""
    pass


# Simulation Exceptions
class SimulationException(RadioSkySkyException):
    """Base para exceções de simulação."""
    pass


class SimulationFailedError(SimulationException):
    """Simulação falhou durante execução."""
    pass


class TimeRangeError(SimulationException):
    """Time range inválido ou inconsistente."""
    pass


# Beam Exceptions
class BeamException(RadioSkySkyException):
    """Base para exceções de feixe."""
    pass


class InvalidBeamError(BeamException):
    """Padrão de feixe inválido."""
    pass
```

**Impacto:** ✅ Error handling +50%, Debugging +40%

---

### 1.4 Documentar Bounded Contexts ⏱️ 3h
**pular**
**Arquivo:** `docs/architecture/bounded_contexts.md`

```markdown
# Bounded Contexts do RadioSkySim

## 1. SkyMap Context
**Responsabilidade:** Representação e manipulação de mapas do céu em HEALPix.

**Entidades:**
- `SkyMap`: Mapa do céu principal

**Value Objects:**
- `NSide`: Resolução HEALPix
- `SkyMapDataset`: Abstração de dados (numpy/xarray/dask)

**Serviços:**
- `SkyMapFactory`: Criação de SkyMaps
- `HealpySkyMapProvider`: Operações HEALPix
- `PySMSkyMapProvider`: Geração com PySM3

**Eventos:**
- `SkyMapCreated`
- `SkyMapTransformed` (smooth, rotate, etc)

**Agregado Root:** `SkyMap`

**Anti-Corruption Layer:** Não necessário (HEALPy é estável)

---

## 2. Satellite Context
**Responsabilidade:** Modelos orbitais e trajetórias de satélites.

**Entidades:**
- `Satellite`: Satélite com parâmetros orbitais
- `SatelliteAssembled`: Satélite + tracks + signals

**Value Objects:**
- `OrbitalElement`: Parâmetros orbitais TLE
- `TimeRange`: Intervalo temporal

**Serviços:**
- `SatelliteFactory`: Criação de satélites
- `SkyFieldGeometryProvider`: Cálculos de órbita
- `SatelliteService`: Busca e seleção

**Agregado Root:** `Satellite`

**Anti-Corruption Layer:** SpaceTrack API → `SatelliteRepository`

---

## 3. Beam Context
**Responsabilidade:** Padrão de radiação do radiotelescópio.

**Entidades:**
- `Beam`: Padrão de radiação 3D

**Value Objects:**
- `BeamParamsDomain`: Propriedades físicas do feixe

**Serviços:**
- `BeamFactory`: Criação de feixes
- `BeamInterpolator`: Interpolação em (freq, angle)

**Agregado Root:** `Beam`

---

## 4. Simulation Context
**Responsabilidade:** Orquestração da simulação completa.

**Entidades:**
- `Simulation`: Executor da simulação
- `SimulationResult`: Resultado imutável

**Value Objects:**
- `TimeRange`: Intervalo temporal
- `SimulationConfig`: Configuração

**Serviços:**
- `SimulationService`: Orquestrador
- `TODSimulator`: Gerador de Time-Ordered Data

**Eventos:**
- `SimulationStarted`
- `SimulationCompleted`
- `SimulationFailed`

**Agregado Root:** `Simulation`

---

## Relações entre Contexts

```
┌─────────────────────────────────────────┐
│         SIMULATION CONTEXT              │
│  ┌──────────────────────────────────┐   │
│  │  SimulationService               │   │
│  │  - Orquestra execução            │   │
│  │  - Seleciona satélites           │   │
│  │  - Prepara dados                 │   │
│  └──────────────────────────────────┘   │
│            ↓         ↓          ↓        │
├────────────┼─────────┼──────────┼────────┤
│   BEAM     │ SATELLITE │  SKYMAP │       │
│  CONTEXT   │ CONTEXT   │ CONTEXT │ TOD   │
│            │           │         │CONTEXT│
└────────────┴───────────┴─────────┴───────┘
```

**Padrão de Comunicação:** Publicação de Eventos (Event-Driven Architecture)

**Exemplo:**
```
SkyMapContext.SkyMapCreated
    ↓
SimulationContext.handle_skymap_created()

SatelliteContext.SatelliteSelected
    ↓
SimulationContext.handle_satellite_selected()

SimulationContext.SimulationCompleted
    ↓
(Log, Persist, Notify User)
```
```

**Impacto:** ✅ Clareza de responsabilidades +40%, Manutenibilidade +30%

---

## 📊 Resumo Fase 1

| Tarefa | Duração | Impacto |
|--------|---------|--------|
| Reorganizar estrutura | 6h | ⭐⭐⭐⭐⭐ |
| Criar Ports | 4h | ⭐⭐⭐⭐⭐ |
| Exceções | 2h | ⭐⭐⭐⭐ |
| Documentar BCs | 3h | ⭐⭐⭐⭐ |
| **TOTAL** | **15h** | **Alto** |

---

## Fase 2️⃣: ROBUSTEZ (Semanas 3-4)

### Objetivo
Melhorar confiabilidade via logging, testes de integração, persistência tipada.

### 2.1 Logging Estruturado ⏱️ 4h
**fazer importante**
**Objetivo:** Usar `structlog` para logs estruturados em JSON.

```python
# infrastructure/logging_config.py

import structlog
from pythonjsonlogger import jsonlogger

def configure_logging():
    """Configurar logging estruturado com JSON."""
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger(__name__)

# Uso em ServiÇos

class SimulationService:
    def run_by_constellations(self, constellations, time_range):
        logger.info(
            "simulation_started",
            constellations=constellations,
            time_range=str(time_range),
            timestamp=datetime.now().isoformat(),
        )
        
        try:
            satellites = self._satellite_service.get_by_constellations(constellations)
            logger.info("satellites_loaded", count=len(satellites))
            
            result = self._run(satellites, time_range)
            
            logger.info(
                "simulation_completed",
                satellites=len(result.satellites),
                time_range=str(result.time_range),
                duration_seconds=0,  # Calcular
            )
            
            return result
            
        except Exception as e:
            logger.exception(
                "simulation_failed",
                constellations=constellations,
                error=str(e),
            )
            raise
```

**Impacto:** ✅ Observability +60%, Debugging +50%

---

### 2.2 Integration Tests ⏱️ 8h
**pular**
**Arquivo:** `tests/integration/test_complete_pipeline.py`

```python
import pytest
import numpy as np
from datetime import datetime, timedelta

def test_complete_simulation_pipeline():
    """
    Test: SkyMap → Satellite → Geometry → Signal → TOD → Dataset
    
    Verifica:
    - Carregamento de mapa
    - Criação de satélite
    - Cálculo de órbita
    - Geração de TOD
    - Validação de resultado
    """
    
    # 1️⃣ Setup
    from radioskysims.infrastructure.skymap.healpy_provider import HealpySkyMapProvider
    from radioskysims.domain.skymap.factory import SkyMapFactory
    from radioskysims.domain.satellite.factory import SatelliteFactory
    from radioskysims.application.services import SimulationService
    
    # 2️⃣ Criar SkyMap de teste
    skymap = SkyMapFactory.create(
        dataset=np.random.randn(hp.nside2npix(128)),
        nside=NSide(128),
        unit="K",
    )
    assert skymap.npix == hp.nside2npix(128)
    
    # 3️⃣ Criar Satélite de teste
    sat = SatelliteFactory.create(
        norad_id=25544,  # ISS
        constellation="ISS",
        epoch=datetime.now(),
    )
    assert sat.norad_id == 25544
    
    # 4️⃣ Executar Simulação
    time_range = TimeRange(
        start=datetime.now(),
        end=datetime.now() + timedelta(hours=1),
    )
    
    service = SimulationService(...)
    result = service.run([sat], time_range)
    
    # 5️⃣ Validar Resultado
    assert result.dataset is not None
    assert result.dataset.dims["time"] > 0
    assert result.dataset.dims["frequency"] > 0
    assert "data" in result.dataset.data_vars
    assert result.dataset["data"].units == "K"
    
    # 6️⃣ Verificar Integridade Física
    assert np.all(np.isfinite(result.dataset["data"].values))  # Sem NaNs
    assert np.all(result.dataset["data"].values >= 0)  # Temp positiva


def test_skymap_persistence():
    """Test: SkyMap → DB → SkyMap"""
    
    from radioskysims.infrastructure.db.skymap_models import SkyMapRecord
    
    # Criar mapa
    skymap = SkyMapFactory.create(...)
    
    # Persistir
    record = SkyMapRecord.from_skymap(skymap)
    # Simular save
    
    # Recuperar
    recovered = record.to_skymap()
    
    # Validar
    assert np.allclose(skymap.data, recovered.data)
    assert skymap.nside == recovered.nside
```

**Impacto:** ✅ Confiabilidade +50%, Regressão -70%

---

### 2.3 TypedDict para Tipos Complexos ⏱️ 2h
**pula**
```python
# application/types.py

from typing import TypedDict
import numpy as np

class FITSHeader(TypedDict, total=False):
    """Header de arquivo FITS HEALPix."""
    NSIDE: int
    COORDSYS: str
    ORDERING: str
    EXTNAME: str
    FREQ_GHZ: float
    UNIT: str


class GeometryData(TypedDict):
    """Dados de geometria orbital."""
    time: np.ndarray  # [Nt]
    theta: np.ndarray  # [Nt] radianos
    phi: np.ndarray    # [Nt] radianos
    range: np.ndarray  # [Nt] metros
    elevation: np.ndarray  # [Nt] radianos
    azimuth: np.ndarray    # [Nt] radianos


class TODData(TypedDict):
    """Time-Ordered Data."""
    time: np.ndarray        # [Nt]
    frequency: np.ndarray  # [Nf]
    data: np.ndarray        # [Nt, Nf] em Kelvin
    units: str
```

**Impacto:** ✅ Type Safety +40%

---

## 📊 Resumo Fase 2

| Tarefa | Duração | Impacto |
|--------|---------|--------|
| Logging | 4h | ⭐⭐⭐⭐ |
| Integration Tests | 8h | ⭐⭐⭐⭐⭐ |
| TypedDict | 2h | ⭐⭐⭐ |
| **TOTAL** | **14h** | **Alto** |

---

## Fase 3️⃣: EXPANSÃO - Domínios Incompletos (Semanas 5-6)

### 3.1 Completar RFI Context ⏱️ 8h

```python
# domain/rfi/models.py

class RFI:
    """Interferência de Radiofrequência."""
    
    def __init__(self, frequency_ranges: list[tuple[float, float]]):
        """
        Args:
            frequency_ranges: [(f_min, f_max), ...] em GHz
        """
        self.frequency_ranges = frequency_ranges
    
    def is_contaminated(self, frequency: float) -> bool:
        """Verifica se frequência está contaminada."""
        return any(
            f_min <= frequency <= f_max
            for f_min, f_max in self.frequency_ranges
        )
    
    def create_mask(self, frequencies: np.ndarray) -> np.ndarray:
        """Máscara booleana: True = RFI, False = Clean."""
        return np.array([self.is_contaminated(f) for f in frequencies])
    
    def apply_rfi_filter(self, tod: xr.Dataset) -> xr.Dataset:
        """Remove canais RFI do TOD."""
        mask = self.create_mask(tod["frequency"].values)
        
        # Zero out RFI channels
        tod_filtered = tod.copy()
        tod_filtered["data"].values[:, mask] = 0.0
        
        return tod_filtered
```

---

### 3.2 Completar Noise Context ⏱️ 10h

```python
# domain/noise/models.py

class Noise:
    """Modelo de ruído do sistema."""
    
    def __init__(
        self,
        t_sys: float,  # Temperatura de sistema [K]
        efficiency: float = 0.8,
    ):
        self.t_sys = t_sys
        self.efficiency = efficiency
    
    def thermal_noise_power(
        self,
        frequency: np.ndarray,  # [Nf] Hz
        bandwidth: float,        # Hz
        integration_time: float, # s
    ) -> np.ndarray:
        """
        Ruído térmico via radiometer equation:
        σ_T = k_B · T_sys / √(B · τ)
        
        Returns:
            [Nf] temperatura de ruído equivalente em Kelvin
        """
        from scipy.constants import k as k_B
        
        return k_B * self.t_sys / np.sqrt(bandwidth * integration_time)
    
    def atmospheric_noise(
        self,
        elevation: np.ndarray,  # [Nt] radianos
        frequency: float,       # Hz
    ) -> np.ndarray:
        """
        Ruído atmosférico via model de opacidade.
        
        τ(el) = τ_0 / sin(el)
        T_atm = T_0 · (1 - exp(-τ(el)))
        """
        el_deg = np.degrees(elevation)
        
        # Model atmosphere (simplificado)
        tau_0 = 0.05 + 0.01 * (frequency / 1e9)  # ópacidade zenital
        tau = tau_0 / np.sin(np.radians(np.clip(el_deg, 1, 90)))
        
        T_0 = 280  # Temperatura atmosférica [K]
        T_atm = T_0 * (1 - np.exp(-tau))
        
        return T_atm
    
    def generate_noise_time_series(
        self,
        frequencies: np.ndarray,  # [Nf] Hz
        times: np.ndarray,         # [Nt] datetime
        elevation: np.ndarray,     # [Nt] radianos
    ) -> np.ndarray:
        """Gerar série temporal de ruído [Nt, Nf]."""
        Nt = len(times)
        Nf = len(frequencies)
        
        noise = np.zeros((Nt, Nf))
        
        for i, (t, el) in enumerate(zip(times, elevation)):
            # Ruído térmico
            t_thermal = self.thermal_noise_power(
                frequencies,
                bandwidth=1e6,  # 1 MHz
                integration_time=1.0,  # 1 segundo
            )
            
            # Ruído atmosférico
            t_atm = self.atmospheric_noise(np.array([el]), frequencies[0])
            
            # Ruído total
            noise[i, :] = t_thermal + t_atm
        
        return noise
```

---

## 📊 Resumo Fase 3

| Tarefa | Duração | Impacto |
|--------|---------|--------|
| RFI Context | 8h | ⭐⭐⭐⭐ |
| Noise Context | 10h | ⭐⭐⭐⭐⭐ |
| Catalog Context (TODO @Jonas) | 12h | ⭐⭐⭐⭐⭐ |
| Map Context (TODO @rafaela) | 8h | ⭐⭐⭐ |
| **TOTAL** | **38h** | **Muito Alto** |

---

## Fase 4️⃣: PRODUCTION-READY (Semanas 7-8)

### 4.1 Performance Profiling ⏱️ 6h

```python
# tests/performance/test_tod_simulation_speed.py

import cProfile
import pstats
from io import StringIO

def test_tod_simulator_performance():
    """Profile TOD simulator com 1M amostras."""
    
    profiler = cProfile.Profile()
    
    # Setup
    sat = create_test_satellite()
    tod_sim = TODSimulator(beam=..., gain=1.0)
    
    # Profile
    profiler.enable()
    
    result = tod_sim.simulate(sat, sky=None, noise=None)
    
    profiler.disable()
    
    # Análise
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)  # Top 20 functions
    
    print(s.getvalue())
    
    # Esperado: < 5s para 1M amostras
    assert result.dataset["data"].size == 1_000_000
```

**Targets:**
- TODSimulator: < 5s para 1M amostras
- HEALPy operations: < 1s para NSide=512
- Interpolação de Beam: < 100ms para 10k avaliações

---

### 4.2 E2E Tests com Dados Reais ⏱️ 10h

```python
# tests/e2e/test_with_real_data.py

def test_e2e_gps_satellite_simulation():
    """
    E2E: ISS real → Órbita → TOD → Comparação externa
    """
    
    # 1️⃣ Usar dados públicos reais
    sat = SatelliteService.get_by_norad_id(25544)  # ISS
    
    # 2️⃣ Executar simulação
    time_range = TimeRange(
        start=datetime(2024, 1, 1, 0, 0, 0),
        end=datetime(2024, 1, 1, 1, 0, 0),
    )
    
    result = SimulationService.run([sat], time_range)
    
    # 3️⃣ Validar contra dados externos
    # (e.g., comparar com software de órbita conhecido)
    assert result.dataset is not None
    assert result.dataset["data"].shape[0] > 0
```

---

### 4.3 CI/CD Pipeline ⏱️ 4h

**GitHub Actions (.github/workflows/test.yml):**

```yaml
name: Tests & Type Checking

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -e ".[dev]"
    
    - name: Run pytest
      run: pytest tests/ --cov=src/radioskysims --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
    
    - name: Type checking with mypy
      run: mypy src/radioskysims --strict
    
    - name: Linting with ruff
      run: ruff check src/
    
    - name: Format check
      run: black --check src/
```

**Impacto:** ✅ Qualidade +60%, Regressão -80%

---

## 📊 Resumo Fase 4

| Tarefa | Duração | Impacto |
|--------|---------|--------|
| Performance | 6h | ⭐⭐⭐ |
| E2E Tests | 10h | ⭐⭐⭐⭐⭐ |
| CI/CD | 4h | ⭐⭐⭐⭐ |
| Documentação | 8h | ⭐⭐⭐⭐ |
| **TOTAL** | **28h** | **Finalização** |

---

## 📅 Timeline Consolidada

```
SEMANA 1-2: Consolidação (Arquitetura)
├─ Reorganizar estrutura
├─ Criar Ports
├─ Exceções
└─ Documentar BCs
   → Objetivo: Clareza arquitetural

SEMANA 3-4: Robustez (Testing & Logging)
├─ Logging estruturado
├─ Integration tests
└─ TypedDict
   → Objetivo: Confiabilidade

SEMANA 5-6: Expansão (Novos Domínios)
├─ RFI Context
├─ Noise Context
└─ Catalog & Map (paralelo com @Jonas/@rafaela)
   → Objetivo: Features científicas

SEMANA 7-8: Production (Polish)
├─ Performance profiling
├─ E2E tests
├─ CI/CD
└─ Documentação final
   → Objetivo: Release-ready
```

---

## ✅ Critérios de Sucesso

### Fase 1 ✓
- [ ] Reorganização sem quebra de testes
- [ ] 100% de Ports implementadas
- [ ] Documentação de Bounded Contexts

### Fase 2 ✓
- [ ] 10+ integration tests passando
- [ ] Coverage ≥ 80%
- [ ] Logs estruturados em JSON

### Fase 3 ✓
- [ ] RFI Context completo e testado
- [ ] Noise Context completo e testado
- [ ] Catalog & Map em andamento

### Fase 4 ✓
- [ ] Testes E2E com dados reais
- [ ] CI/CD pipeline verde
- [ ] Documentação 90%+
- [ ] Score Maturidade: 4.8/5

---

## 🎯 Recomendações Finais (Como Especialista)

### 1. **Priorize Ports/Interfaces** (CRÍTICO)
Sem abstrações explícitas, refatorações futuras serão difíceis.

### 2. **Logging Estruturado** (ALTA)
Em produção, logs em JSON são essenciais para observability.

### 3. **Domínios Científicos** (MUITO ALTA)
RFI e Noise são críticos para simulações realistas.

### 4. **E2E Tests** (ALTA)
Validação com dados reais contra software estabelecido.

### 5. **Documentação de Decisões** (MÉDIA)
ADRs (Architecture Decision Records) para decisões futuras.

---

**Documento Preparado por:** GitHub Copilot (Claude Haiku 4.5)  
**Data:** 29 de janeiro de 2026  
**Status:** ✅ Roadmap Completo
