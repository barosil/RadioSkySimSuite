# Resumo: Simplificação de Imports e Revisão de Relações de Classes

## Data: 24 de janeiro de 2026

## Objetivo
Simplificar os imports internos utilizando os arquivos `__init__.py` e revisar as relações de classes para gerar um satélite com tracks e signals.

## Alterações Realizadas

### 1. Configuração dos Arquivos `__init__.py`

Foram criados/atualizados os seguintes arquivos `__init__.py` para exportar as classes principais:

#### `domain/satellite/__init__.py`
```python
from .models import Satellite, OrbitalElement, SatelliteAssembled
from .factory import SatelliteFactory
from .selector import TLESelector
from .assembler import SatelliteAssembler
```

#### `domain/tracks/__init__.py`
```python
from .models import Tracks
from .factory import TracksFactory
from .types import SatelliteBlocks
```

#### `domain/signal/__init__.py`
```python
from .models import TOD
from .factory import SignalFactory
```

#### `domain/tod/__init__.py`
```python
from .simulator import TODSimulator
```

#### `domain/beam/__init__.py`
(Já existia configurado)
```python
from .models import Beam
from .operations import BeamOps
from .properties import BeamProperties
```

#### `domain/geometry/__init__.py`
```python
from .interface import GeometryProvider
from .skyfield_provider import SkyfieldGeometryProvider
```

#### `domain/simulation/__init__.py`
```python
from .simulation import Simulation, SimulationResult
```

### 2. Atualização dos Imports

Os imports foram simplificados em diversos arquivos:

#### Antes:
```python
from radioskysims.domain.satellite.models import Satellite
from radioskysims.domain.common.models import TimeRange
from radioskysims.domain.signal.factory import SignalFactory
from radioskysims.domain.tod.simulator import TODSimulator
```

#### Depois:
```python
from radioskysims.domain.satellite import Satellite
from radioskysims.domain.common import TimeRange
from radioskysims.domain.signal import SignalFactory
from radioskysims.domain.tod import TODSimulator
```

### Arquivos Atualizados:

1. **Application Layer:**
   - `application/services/simulation_service.py`
   - `application/services/satellite_service.py`
   - `application/services/tod_services.py`

2. **Domain Layer:**
   - `domain/simulation/simulation.py`
   - `domain/satellite/factory.py`
   - `domain/satellite/assembler.py`
   - `domain/satellite/selector.py`
   - `domain/signal/factory.py`
   - `domain/tracks/factory.py`

3. **Infrastructure Layer:**
   - `infrastructure/beams/loaders/base.py`
   - `infrastructure/beams/loaders/csv.py`
   - `infrastructure/beams/loaders/lit.py`
   - `infrastructure/beams/loaders/custom.py`
   - `infrastructure/db/satellite/satelliterepository.py`

### 3. Diagrama de Classes

Foi criado um diagrama Mermaid completo mostrando as relações entre as classes principais:

**Localização:** `sandbox/diagrams/satellite_tracks_signals_relations.mermaid`

O diagrama ilustra:

- **Entidades principais:** Satellite, OrbitalElement, SatelliteAssembled, Tracks, TOD
- **Factories:** SatelliteFactory, TracksFactory, SignalFactory, SatelliteAssembler
- **Simulação:** Simulation, SimulationResult, TODSimulator
- **Value Objects:** TimeRange, FrequencyRange
- **Interfaces:** GeometryProvider

#### Tipos de Relações:

- **Composição (`*--`):** Componentes que pertencem exclusivamente ao todo
  - Satellite contém OrbitalElement
  - SatelliteAssembled possui Tracks e TOD
  
- **Agregação (`o--`):** Componentes compartilhados
  - Simulation agrega múltiplos Satellites
  - Tracks rastreia múltiplos Satellites

- **Dependência (`..>`):** Uma classe usa/cria outra
  - Factories criam suas respectivas entidades
  - Simulation gera TOD e SimulationResult

- **Associação (`-->`):** Relacionamento de uso
  - Simulation usa GeometryProvider, SignalFactory, TODSimulator

## Fluxo de Geração de Satélite com Tracks e Signals

```
1. SatelliteFactory.build()
   └─> cria Satellite (com OrbitalElement)

2. TracksFactory.create_tracks()
   └─> usa dados de Satellite
   └─> gera Tracks (xr.Dataset com posições)

3. SignalFactory.create_signal()
   └─> usa FrequencyRange
   └─> gera signals (xr.Dataset com PSD)

4. SatelliteAssembler.assemble()
   └─> combina name, Tracks, signals
   └─> produz SatelliteAssembled

5. Simulation.run()
   └─> usa GeometryProvider para cálculos geométricos
   └─> usa SignalFactory para gerar sinais
   └─> usa TODSimulator para simular TOD
   └─> produz SimulationResult
```

## Benefícios da Simplificação

1. **Imports mais limpos e legíveis:** Reduz a verbosidade do código
2. **Menor acoplamento:** Desacopla a estrutura interna dos módulos
3. **Manutenção facilitada:** Mudanças internas não afetam imports externos
4. **API pública clara:** Os `__init__.py` definem explicitamente o que é público
5. **Melhor organização:** Imports relativos dentro dos módulos

## Próximos Passos Sugeridos

1. Atualizar testes para usar os novos imports simplificados
2. Verificar notebooks que possam estar usando os imports antigos
3. Atualizar documentação com exemplos dos novos imports
4. Considerar adicionar type hints nos `__init__.py` para melhor IDE support

## Observações

- O módulo `common` já estava bem configurado
- O módulo `beam` já possuía `__init__.py` completo
- Alguns módulos internos agora usam imports relativos (`.models`, `.factory`)
- Todos os imports foram testados e estão funcionais
