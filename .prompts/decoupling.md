# Plano de Desenvolvimento RadioSkySim

## Requisitos

### Tech Stack

- Xarray
- Dask
- Astropy
- Skyfield
- h5py
- Pydantic
- SQLModel

### Persistencia

- Aplicações devem ter um DB engine e scheme comum
- Settings.toml para as configurações pode ser comum para todas as aplicações ou cada uma delas ter seu próprio arquivo de configurações
- credenciais de acesso em credentials.env
- Cama aplicação interage com o DB postgres e cria as tabelas necessárias ou utiliza as existentes.

### Instalações

- Cada aplicação tem o seu proprio pyproject.toml e requirements.txt
- A aplicação principal tem um pyproject que instala todos os componentes e expõe linhas de comando necessárias.

### Logging

- Cada aplicação tem o seu proprio logger
- Logs são salvos em um arquivo de log usando ferramentas do sistema syslog para rotação e leitura
- Flags para logs mais verbosos se propagam até o root logger da aplicação

### Monitor

- As aplicações tem acesso a um modulo de monitoramento comum para acessar informações de disco, memória e cpu.
- A aplicação deve verificar recursos da máquina para realizar operações de maneira segura e consistente, evitando travamento.

### Messages

- Operações de download devem ser informadas no início e no fim da operação.
- Operação de ingestão de dados grandes devem ser informadas.
- Operações de escrita de dados devem ser informadas.
- Registros no banco de dados devem ser informados
- Operações cpu-bound time consuming devem ser informadas
- Prover indicador de progresso para operações, uniforme em todo o pacote.

## Aplicações

- RadioSkySim
    - DBapp
    - ConfigLoader
    - SystemMonitor
    - PathManager
    - RadioBeam
        - Beam
            - creation
            - visualization
            - export
            - load
        - BeamOperations
    - SkyCoordsProcessor
    - Satellites
        - GNSSSatellitesTLE
        - GNSSatellitesRINEX
        - GNSSatellitesSignals
        - GNSSSatelliteInfo
    - LocalSources
        - SunFlux&Track
        - TrackMaker
        - FluxMaker
        - LearmonthDataProvider
    - RadioSources
        - RadioSourceFlux&Track
        - TrackMaker
        - FluxMaker
        - CatalogProvider
    - ContinuumSources
        - SkyMap
        - HIPSProvider
    - CosmologicalSource
    - Noise
    - RFI
    - Radiotelescope
       - Pointing
       - Antenna
       - Backend
       - Observer
    - MapAnalyzer
        - load
        - visualize
        - manipulate
        - filter
        - mask
        - rotate
