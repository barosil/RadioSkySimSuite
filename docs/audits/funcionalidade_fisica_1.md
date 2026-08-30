Auditoria Técnica — Funcionalidade Física 1

Projeto: RadioSkySimBranch: feat/tod-notebooksEscopo: contribuição difusa da Via Láctea na geração de Time-Ordered Data (TOD)Data: 10/08/2026

1. Objetivo

A Funcionalidade Física 1 amplia o RadioSkySim para permitir a geração de TOD não apenas a partir de fontes discretas, fluxos e tracks, mas também a partir de mapas difusos do céu.

O caso físico implementado é a emissão difusa da Via Láctea, modelada com PySM3 e representada por mapas HEALPix.

Fluxo principal:

Galaxy
  ↓
PySM3
(synchrotron + dust + free-free)
  ↓
SkyMap / HEALPix
  ↓
pointing BINGO + beam
  ↓
TODSimulator
  ↓
TODOrchestrator
  ↓
SimOrchestrator
  ↓
SimulationResult

Também foi implementado o fluxo persistente:

SkyMap → HDF5 → Repository.load() → SkyMap → pointing + beam → TOD

2. Requisitos atendidos

A implementação cobre os seguintes requisitos solicitados:

criação da representação ContinuumSource → Galaxy;

geração da Via Láctea com PySM3;

componentes synchrotron, dust e free-free;

geração de um mapa por bin de FrequencyRange;

construção de TOD a partir de mapas HEALPix;

uso do apontamento do radiotelescópio;

inclusão da resposta do beam;

separação entre TOD de fontes/tracks e TOD de mapas;

serviço de orquestração para combinar contribuições;

persistência opcional de mapas HEALPix;

repository HDF5 para salvar/carregar mapas;

uso de mapas carregados para reconstrução do TOD;

integração ao SimOrchestrator;

demonstração no 50_TOD_SIMULATION.ipynb.

3. Arquivos criados

src/radioskysims/domain/radiosources/continuum.py

Introduz os conceitos físicos de ContinuumSource e Galaxy.

A Galaxy representa a Via Láctea e define as componentes galácticas aceitas. A validação de componentes permanece no Domain, sem dependência de PySM3 ou HDF5.

src/radioskysims/application/skymap/generate_continuum.py

Implementa:

GalaxyMapSet;

GenerateGalaxyMapsUseCase.

Responsabilidades:

percorrer FrequencyRange.value;

converter MHz → GHz para o generator;

gerar um SkyMap por frequência;

garantir correspondência entre número de mapas e bins espectrais;

persistir opcionalmente através de SkyMapRepositoryPort;

propagar a política overwrite.

src/radioskysims/application/ports/skymap_repository.py

Define o contrato de persistência dos SkyMaps, com operações equivalentes a:

save / load / exists / delete

A Application não depende diretamente de HDF5.

src/radioskysims/domain/tod/map_projector.py

Define a abstração SkyMapTODProjector, usada pelo TOD para transformar mapas do céu em séries temporais observadas pelo telescópio.

src/radioskysims/application/services/tod_orchestrator.py

Novo serviço de Application que explicita os dois caminhos físicos do TOD:

run_sources() — fontes discretas;

run_maps() — mapas difusos;

combine() — combinação das contribuições;

run() — orquestração de alto nível.

src/radioskysims/infrastructure/skymap/repository/hdf5.py

Implementação concreta de SkyMapRepositoryPort usando HDF5.

Cada mapa é salvo individualmente, por exemplo:

galaxy_980mhz_nside64.h5
...
galaxy_1360mhz_nside64.h5

São preservados:

pixels;

NSide;

Npix;

unidade;

frame;

campo de Stokes;

frequência.

O repository impede sobrescrita acidental quando overwrite=False.

src/radioskysims/infrastructure/skymap/repository/__init__.py

Exporta a implementação HDF5 do repository.

src/radioskysims/infrastructure/skymap/tod_projector.py

Implementa HealpySkyMapTODProjector.

Responsabilidades:

receber mapa e pointing temporal;

trabalhar com coordenadas RA/Dec;

transformar coordenadas equatoriais ↔ galácticas quando necessário;

interpolar o mapa HEALPix nas posições observadas;

aplicar suavização correspondente ao beam;

produzir temperatura do céu ao longo do tempo.

4. Arquivos modificados

src/radioskysims/domain/tod/simulator.py

O simulador passou a oferecer caminhos explícitos:

simulate_from_source();

simulate_from_maps().

O método legado simulate() foi preservado como compatibilidade.

simulate_from_maps() constrói T_antenna e power, organiza as dimensões time e frequency, aplica ganho e utiliza o projector para obter a temperatura observada.

src/radioskysims/application/services/sim_orchestrator.py

Integra a contribuição galáctica à pipeline principal.

Novas opções incluem:

include_galaxy
galaxy_nside
persist_skymaps
skymap_overwrite

Também foram integrados ao contexto:

TODOrchestrator;

gerador de mapas galácticos;

SkyMap repository;

SkyMap generator;

SkyMap TOD projector.

Foi implementado suporte a Galaxy-only, permitindo a simulação da emissão difusa mesmo sem satélites disponíveis.

Quando fontes e Galaxy estão habilitadas, as contribuições são combinadas pelo TODOrchestrator.

Também foi criado cache dos mapas galácticos para reutilização entre múltiplas antenas. Assim, PySM3 não é executado novamente para cada antena.

src/radioskysims/bootstrap/builders.py

O Composition Root passou a construir e injetar:

PySMSkyMapGeneratorAdapter
HDF5SkyMapRepository
GenerateGalaxyMapsUseCase
HealpySkyMapTODProjector
TODOrchestrator

Também foi corrigido o caminho do repository para ser resolvido a partir da raiz do projeto, evitando que notebooks criem acidentalmente notebooks/data/aux/skymaps.

Destino padrão final:

<RadioSkySim>/data/aux/skymaps

notebooks/50_TOD_SIMULATION.ipynb

O notebook foi reorganizado para demonstrar a funcionalidade de modo didático.

Estrutura principal:

Setup;

emissão difusa da Via Láctea;

geração/reutilização dos mapas;

carregamento HDF5;

mapas persistidos → TOD;

validação do round-trip;

TOD de fontes discretas;

persistência do SimulationResult;

repository de simulações opcional;

eventos e trânsitos.

Foram adicionadas flags de execução:

GENERATE_GALAXY_MAPS = False
RUN_DISCRETE_SOURCES = False

Isso permite Run All sem regenerar PySM3 e sem depender de Space-Track/Celestrak.

5. Grade espectral validada

A configuração BINGO utilizada possui:

frequency_range = [980, 1360, 1]

Logo, a pipeline utiliza:

980, 981, 982, ..., 1360 MHz

Total:

381 bins

com resolução de 1 MHz.

A execução real confirmou:

frequency size = 381
Δν = 1 MHz

O num_channels=2048 pertence ao backend/espectrômetro e não substitui FrequencyRange.value no fluxo atual da simulação.

6. Persistência HDF5 validada

Foram gerados e persistidos 381 mapas para NSide=64.

Para esse NSide:

Npix = 12 × 64² = 49152

Um arquivo real apresentou:

dataset: pixels
field: I
frame: galactic
freq_ghz: 1.0
npix: 49152
nside: 64
unit: uK_CMB
pixels shape: (49152,)
pixels dtype: float64

7. Round-trip validado

Foi executado o caminho:

PySM3
  ↓
SkyMap
  ↓
HDF5
  ↓
Repository.load()
  ↓
SkyMap
  ↓
pointing + beam
  ↓
TOD

Os 381 mapas foram carregados novamente e utilizados para gerar TOD.

Resultado observado:

time = 11
frequency = 381
variáveis = T_antenna, power

A comparação numérica com numpy.testing.assert_allclose passou para T_antenna e power.

8. Testes criados

Domain

tests/domain/radiosources/

tests/domain/tod/test_map_simulation.py

tests/domain/tod/test_source_simulation_api.py

Application

tests/application/services/skymap/test_generate_continuum.py

tests/application/services/test_tod_orchestrator.py

tests/application/services/test_sim_orchestrator_galaxy.py

Infrastructure

tests/infrastructure/skymap/repository/test_hdf5_repository.py

tests/infrastructure/skymap/test_tod_projector.py

Integration

tests/integration/skymap/test_persisted_map_to_tod.py

A regressão focada final apresentou:

54 passed

no ambiente radiosky, Python 3.11.14.

9. Validação com componentes reais

O fluxo real foi executado com:

SimOrchestrator.from_settings("bingo")
        ↓
Galaxy
        ↓
PySM3
        ↓
HEALPix NSide=64
        ↓
pointing BINGO
        ↓
beam
        ↓
TOD

Resultado:

time = 11
frequency = 381
T_antenna
power
contribution = skymap

Portanto, a validação não ficou restrita a mocks ou fakes.

10. Conformidade arquitetural

A implementação preserva a separação em camadas:

Domain
  Galaxy
  ContinuumSource
  SkyMapTODProjector
  TODSimulator

Application
  GenerateGalaxyMapsUseCase
  TODOrchestrator
  SimOrchestrator
  SkyMapRepositoryPort

Infrastructure
  PySMSkyMapGeneratorAdapter
  HealpySkyMapTODProjector
  HDF5SkyMapRepository

Bootstrap
  builders.py

A lógica física permanece separada das tecnologias de geração, projeção e persistência.

11. Decisões de compatibilidade

simulate() foi preservado;

simulate_from_source() explicita o fluxo legado;

simulate_from_maps() adiciona o novo fluxo;

include_galaxy=False mantém o comportamento anterior;

Galaxy-only não depende de satélites;

o comportamento legado de ausência de satélites continua preservado quando Galaxy não está habilitada.

12. Melhorias de desempenho

Cache multi-antena

Os mapas PySM3 são gerados uma única vez por execução e reutilizados para cada antena.

Reuso por HDF5

Depois da primeira geração, o notebook pode executar com:

GENERATE_GALAXY_MAPS = False

reutilizando os mapas já persistidos.

13. Limitações conhecidas

Beam

A rota de mapas utiliza atualmente uma aproximação gaussiana equivalente baseada em FWHM. Uma evolução futura poderá utilizar convolução completa com padrões de beam medidos/tabulados ou representação harmônica.

Conversão uK_CMB → K

A conversão atual é escalar (× 1e-6). Uma evolução futura poderá implementar conversão termodinâmica/Rayleigh-Jeans dependente da frequência.

Custo PySM3

A geração dos 381 mapas em NSide=64 possui custo computacional significativo. A persistência e o cache reduzem esse impacto em execuções posteriores.

Canais instrumentais x bins de simulação

O backend possui num_channels=2048, enquanto a grade atual de FrequencyRange possui 381 bins. O fluxo implementado segue explicitamente FrequencyRange.value, conforme o contrato atual da simulação.

14. Resultado da auditoria

Critério

Avaliação

Requisitos funcionais

Concluídos

Integração ao SimOrchestrator

Concluída

Persistência de SkyMaps

Concluída

Load HDF5 → TOD

Validado

Separação sources/maps

Concluída

Compatibilidade legado

Preservada

Testes focados

54 passed

Execução real BINGO/PySM3

Validada

Notebook demonstrativo

Run All validado

Arquitetura Ports & Adapters

Preservada

15. Conclusão

A Funcionalidade Física 1 adiciona ao RadioSkySim um segundo mecanismo físico de formação de TOD.

Antes desta implementação, o caminho principal estava centrado em fontes discretas, fluxos e tracks. Agora o sistema também representa campos difusos do céu por mapas HEALPix.

A arquitetura permite expressar conceitualmente:

TOD total = TOD de fontes discretas + TOD de mapas difusos

A emissão da Via Láctea é a primeira implementação concreta desse novo caminho.

A solução está integrada ao SimOrchestrator, possui persistência e reutilização HDF5, preserva o fluxo legado, apresenta cobertura automatizada em múltiplas camadas e foi validada com componentes reais.

Status da Funcionalidade Física 1: concluída e adequada para versionamento/revisão antes do commit.