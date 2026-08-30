# Auditoria Técnica — Funcionalidade Física 3: Construção de Mapas a partir da TOD

## 1. Objetivo

Esta funcionalidade implementa o processo de reconstrução de mapas HEALPix a partir de dados temporais do tipo Time-Ordered Data (TOD), completando o fluxo observacional inverso já existente no RadioSkySim.

Enquanto as funcionalidades anteriores produzem TOD a partir de fontes discretas e mapas de céu, esta funcionalidade realiza a operação complementar:

```text
TOD
→ pointing
→ pixelização HEALPix
→ acumulação por pixel
→ mapa reconstruído
```

O objetivo definido para esta etapa foi atender aos seguintes requisitos:

* criação de modelo de domínio;
* criação de modelo de banco de dados;
* criação de modelo de repositório;
* criação de modelo de serviço;
* reconstrução de mapas a partir de TOD multi-frequência;
* registro da quantidade de observações por pixel;
* persistência eficiente dos mapas reconstruídos;
* associação entre mapa reconstruído e simulação de origem;
* recuperação posterior dos resultados persistidos.

A implementação foi desenvolvida de forma compatível com a arquitetura em camadas já utilizada pelo RadioSkySim.

---

# 2. Visão geral da arquitetura

O fluxo implementado segue a separação de responsabilidades:

```text
TOD / SimulationResult
        |
        v
GenerateSkyMapsFromTODUseCase
        |
        v
MapMakerPort
        |
        v
HealpyBinnedMapMakerAdapter
        |
        v
MapMakingResult
        |
        v
MapMakingService
        |
        v
MapMakingRepositoryPort
        |
        v
MapMakingRepository
        |
        +----------------------+
        |                      |
        v                      v
   PostgreSQL                HDF5
   metadados          pixels + hit_map
```

A arquitetura foi organizada de maneira que:

* o domínio não dependa de banco de dados;
* a camada de aplicação não dependa diretamente de SQLModel ou HDF5;
* a implementação concreta de mapmaking permaneça na infraestrutura;
* a persistência seja acessada através de ports;
* os arrays científicos sejam mantidos fora do banco relacional.

Essa organização preserva a direção arquitetural desejada:

```text
interfaces
    ↓
application
    ↓
domain
    ↑
infrastructure
```

---

# 3. Modelo de domínio

## 3.1 MapMakingResult

Foi criada a entidade:

```text
src/radioskysims/domain/mapmaking/models.py
```

com o modelo:

```text
MapMakingResult
```

O objeto representa o resultado científico da reconstrução de um canal de frequência.

Sua estrutura conceitual é:

```text
MapMakingResult
├── skymap
├── hit_map
├── observed_mask
└── n_samples
```

### skymap

O mapa científico reconstruído utiliza a entidade já existente:

```text
SkyMap
```

Essa decisão evita a duplicação de conceitos já presentes no domínio.

A entidade `SkyMap` continua sendo responsável por:

* dados HEALPix;
* `nside`;
* número de pixels;
* unidade;
* sistema de coordenadas;
* frequência;
* campo Stokes.

O mapmaking apenas adiciona informações específicas do processo de reconstrução.

### hit_map

`hit_map` registra quantas amostras temporais contribuíram para cada pixel HEALPix.

Formalmente:

```text
hit_map[p] = número de amostras observando o pixel p
```

Esse mapa é importante para:

* análise de cobertura;
* identificação de pixels nunca observados;
* avaliação da estratégia de varredura;
* desenvolvimento futuro de mapmaking ponderado.

### observed_mask

A máscara observada é definida por:

```text
observed_mask = hit_map > 0
```

O modelo valida explicitamente que essa relação seja satisfeita.

### n_samples

Representa o número total de amostras temporais processadas para o canal de frequência.

---

# 4. Propriedades derivadas

O `MapMakingResult` também fornece métricas derivadas.

## 4.1 Número de pixels observados

```text
n_observed_pixels
```

é calculado como:

```text
count_nonzero(observed_mask)
```

## 4.2 Fração de cobertura

A cobertura espacial é calculada por:

```text
coverage_fraction =
    n_observed_pixels / npix
```

Essa métrica fornece uma estimativa direta da fração do céu HEALPix visitada pelo pointing.

---

# 5. Validações do domínio

O modelo verifica:

* dimensionalidade 1D do `hit_map`;
* dimensionalidade 1D da máscara;
* compatibilidade entre número de pixels do mapa e do `hit_map`;
* compatibilidade entre número de pixels e máscara;
* impossibilidade de contagens negativas;
* número de amostras positivo;
* consistência entre `observed_mask` e `hit_map > 0`.

Essas validações mantêm invariantes científicos no domínio e evitam que resultados inconsistentes sejam propagados para persistência ou análise.

---

# 6. Port de mapmaking

Foi criado:

```text
src/radioskysims/application/ports/mapmaking.py
```

com o contrato:

```text
MapMakerPort
```

O método principal é:

```text
make_map(...)
```

que recebe:

```text
TOD
pointing_track
frequency_hz
nside
frame
```

e retorna:

```text
MapMakingResult
```

Esse port desacopla o caso de uso da implementação concreta de pixelização.

Assim, futuramente podem ser implementados diferentes mapmakers sem alterar a camada de aplicação, por exemplo:

```text
NaiveBinnedMapMaker
WeightedMapMaker
DestripingMapMaker
GLSMapMaker
```

---

# 7. Adapter HEALPix

Foi implementado:

```text
src/radioskysims/infrastructure/mapmaking/healpy_binned.py
```

com:

```text
HealpyBinnedMapMakerAdapter
```

Esse adapter implementa o primeiro algoritmo de reconstrução disponível no RadioSkySim.

---

# 8. Algoritmo de naive binning

O método implementado corresponde ao mapmaking por binning simples.

Para cada amostra temporal:

```text
pointing(t)
    ↓
coordenadas angulares
    ↓
pixel HEALPix p
```

O valor do TOD é acumulado naquele pixel.

Para cada pixel observado:

```text
m[p] =
    soma dos valores TOD observados no pixel
    /
    número de observações no pixel
```

ou matematicamente:

[
m_p =
\frac{\sum_{t \in p} d_t}
{N_p}
]

onde:

* (m_p) é a temperatura reconstruída do pixel;
* (d_t) é o valor do TOD na amostra temporal;
* (N_p) é o número de observações do pixel.

No código:

```text
temperature_sum[p]
hit_map[p]
```

e:

```text
map[p] =
temperature_sum[p] / hit_map[p]
```

para:

```text
hit_map[p] > 0
```

Pixels não observados recebem zero nesta primeira implementação.

---

# 9. Conversão do pointing para HEALPix

A reconstrução utiliza os campos:

```text
ra
dec
```

do `pointing_track`.

O sistema trabalha inicialmente no frame:

```text
equatorial
```

As coordenadas são convertidas para a convenção angular do HEALPix:

```text
theta = π/2 - dec
phi   = ra mod 2π
```

Em seguida:

```text
healpy.ang2pix(...)
```

é utilizado para determinar o pixel associado a cada amostra temporal.

---

# 10. Processamento por canal de frequência

O TOD utilizado pelo RadioSkySim possui estrutura típica:

```text
time × frequency
```

A entidade `SkyMap`, por outro lado, representa um mapa associado a uma frequência individual.

Por isso, a reconstrução foi organizada como:

```text
TOD(time, frequency)
        |
        +--> frequência 1 → SkyMap
        |
        +--> frequência 2 → SkyMap
        |
        +--> frequência 3 → SkyMap
        |
        ...
```

Essa decisão também mantém coerência com as funcionalidades de mapas de Galáxia e Hidrogênio Neutro.

---

# 11. Caso de uso multi-frequência

Foi criado:

```text
src/radioskysims/application/mapmaking/generate_from_tod.py
```

com:

```text
GenerateSkyMapsFromTODUseCase
```

O caso de uso:

1. lê as frequências disponíveis no TOD;
2. percorre cada canal;
3. chama o `MapMakerPort`;
4. gera um `MapMakingResult` por frequência;
5. retorna um conjunto ordenado de resultados.

O container utilizado é:

```text
MapMakingResultSet
```

que fornece:

```text
results
maps
frequencies_ghz
```

O fluxo passa a ser:

```text
TOD
   ↓
GenerateSkyMapsFromTODUseCase
   ↓
MapMakingResultSet
   ├── MapMakingResult ν1
   ├── MapMakingResult ν2
   └── MapMakingResult νN
```

---

# 12. Serviço de aplicação

Foi criado:

```text
src/radioskysims/application/services/mapmaking_service.py
```

com:

```text
MapMakingService
```

O serviço coordena:

```text
geração
+
persistência opcional
```

Sua responsabilidade é de alto nível.

O serviço recebe:

* TOD;
* pointing;
* `nside`;
* frame;
* flag de persistência;
* `simulation_id`;
* prefixo de chave;
* flag de overwrite.

O fluxo é:

```text
MapMakingService.run()
        |
        v
GenerateSkyMapsFromTODUseCase
        |
        v
MapMakingResultSet
        |
        +--> persist=False
        |
        └--> persist=True
                |
                v
        MapMakingRepositoryPort
```

O retorno é:

```text
MapMakingServiceResult
```

contendo:

```text
mapmaking
record_ids
```

---

# 13. Modelo de banco de dados

Foi criado:

```text
src/radioskysims/infrastructure/db/mapmaking_db_model.py
```

com:

```text
MapMakingRecord
```

O modelo representa os metadados do resultado de mapmaking.

Os principais campos são:

```text
id
simulation_id
created_at
frequency_hz
nside
npix
unit
frame
field
n_samples
n_observed_pixels
coverage_fraction
filepath
mapmaker
```

---

# 14. Estratégia de persistência

Foi tomada a decisão de não armazenar diretamente todos os pixels HEALPix no PostgreSQL.

O desenho adotado foi:

```text
PostgreSQL
    ↓
metadados

HDF5
    ↓
arrays científicos
```

Essa estratégia é mais adequada para dados científicos potencialmente grandes.

---

# 15. Conteúdo armazenado no PostgreSQL

O banco mantém informações leves e consultáveis:

```text
simulation_id
frequency_hz
nside
npix
unit
frame
field
n_samples
n_observed_pixels
coverage_fraction
filepath
mapmaker
```

Isso permite consultas como:

```text
quais mapas pertencem à simulação X?

qual frequência foi reconstruída?

qual foi a cobertura do mapa?

qual resolução HEALPix foi utilizada?

onde está armazenado o arquivo correspondente?
```

sem carregar os arrays na memória.

---

# 16. Conteúdo armazenado em HDF5

Cada resultado persistido armazena:

```text
/pixels
/hit_map
```

Além dos atributos necessários para reconstrução do objeto.

O arquivo HDF5 contém:

```text
pixels
hit_map
nside
unit
frame
field
freq_ghz
n_samples
```

O uso de HDF5 permite:

* compressão;
* armazenamento eficiente de arrays;
* interoperabilidade com ferramentas científicas;
* separação entre metadata relacional e dados numéricos.

---

# 17. Repository Port

Foi criado:

```text
src/radioskysims/application/ports/mapmaking_repository.py
```

com:

```text
MapMakingRepositoryPort
```

O contrato define:

```text
save
load
get_metadata
delete
```

A Application não conhece SQLModel, HDF5 ou PostgreSQL.

---

# 18. Repository concreto

Foi criado:

```text
src/radioskysims/infrastructure/db/mapmaking_repository.py
```

com:

```text
MapMakingRepository
```

Esse adapter implementa um repositório híbrido.

O método:

```text
save()
```

realiza:

```text
MapMakingResult
        |
        +--> grava pixels no HDF5
        |
        +--> grava hit_map no HDF5
        |
        └--> registra metadados no banco
```

---

# 19. Persistência atômica

Para reduzir o risco de arquivos incompletos, o HDF5 é inicialmente escrito como arquivo temporário:

```text
<key>.h5.tmp
```

e somente após uma escrita bem-sucedida é renomeado para:

```text
<key>.h5
```

Em caso de exceção, o arquivo temporário é removido.

---

# 20. Recuperação de resultados

O método:

```text
load(record_id)
```

realiza o processo inverso:

```text
PostgreSQL
    ↓
metadados
    +
filepath
    ↓
HDF5
    ↓
pixels + hit_map
    ↓
SkyMap
    ↓
MapMakingResult
```

A máscara observada é reconstruída como:

```text
hit_map > 0
```

---

# 21. Consulta somente de metadados

O método:

```text
get_metadata(record_id)
```

permite consultar dados sem materializar os arrays.

Essa característica é especialmente importante para:

* catálogos de simulações;
* interfaces gráficas;
* relatórios;
* pipelines de seleção;
* execução sob restrições de memória.

---

# 22. Exclusão

O método:

```text
delete(record_id)
```

remove:

```text
registro SQL
+
arquivo HDF5
```

mantendo consistência entre os dois níveis de persistência.

---

# 23. Associação com Simulation

O modelo possui:

```text
simulation_id
```

Isso permite associar cada mapa reconstruído à simulação TOD que lhe deu origem.

Conceitualmente:

```text
SimulationRecord
      |
      +------ MapMakingRecord ν1
      |
      +------ MapMakingRecord ν2
      |
      +------ MapMakingRecord ν3
```

Essa associação estabelece provenance entre o dado temporal e o produto científico reconstruído.

---

# 24. Testes de domínio

Foram implementados testes para:

```text
MapMakingResult válido
hit_map incompatível
observed_mask inconsistente
```

Esses testes verificam os invariantes fundamentais do modelo.

---

# 25. Testes do MapMaker

O adapter HEALPix possui testes verificando:

* conformidade com `MapMakerPort`;
* criação correta do resultado;
* número de amostras;
* contagem do hit map;
* média de amostras que atingem o mesmo pixel;
* rejeição de TOD sem `T_antenna`.

Um caso sintético utiliza amostras:

```text
1, 2
```

em um pixel e:

```text
3, 4
```

em outro.

Os valores esperados são:

```text
1.5
3.5
```

confirmando o funcionamento do binning.

---

# 26. Testes multi-frequência

O caso de uso foi validado com TOD contendo múltiplos canais.

Por exemplo:

```text
1 GHz
1.1 GHz
```

gerando dois mapas independentes.

Também foi verificado que as escalas de temperatura são preservadas individualmente por canal.

---

# 27. Testes do serviço

O `MapMakingService` foi testado em dois modos.

## Sem persistência

```text
TOD
→ mapas
```

sem acesso ao repository.

## Com persistência

```text
TOD
→ mapas
→ repository
```

Foi verificado que:

* cada canal é persistido;
* são retornados IDs independentes;
* `simulation_id` é propagado;
* as chaves incluem frequência e `nside`.

Exemplo:

```text
bingo_1000mhz_nside8
bingo_1100mhz_nside8
```

---

# 28. Testes do modelo DB

O `MapMakingRecord` foi validado para garantir armazenamento correto de:

* simulation ID;
* frequência;
* `nside`;
* quantidade de pixels;
* número de amostras;
* número de pixels observados;
* caminho HDF5;
* identificador do algoritmo.

---

# 29. Testes do repository

Foram validados:

```text
save
load
get_metadata
delete
```

O round-trip garante:

```text
original
→ HDF5 + DB
→ load
→ reconstruído
```

e verifica igualdade entre:

```text
pixels
hit_map
n_samples
n_observed_pixels
```

---

# 30. Teste de integração ponta a ponta

Foi criado:

```text
tests/integration/mapmaking/test_tod_to_persisted_map.py
```

O teste executa:

```text
TOD sintético multi-frequência
        ↓
MapMakingService
        ↓
HealpyBinnedMapMakerAdapter
        ↓
SkyMaps
        ↓
MapMakingRepository
        ↓
HDF5 + banco
        ↓
load
        ↓
comparação com original
```

O teste valida três frequências:

```text
1000 MHz
1001 MHz
1002 MHz
```

e confirma que cada canal é reconstruído e persistido independentemente.

---

# 31. Validação da provenance

A integração também verifica que:

```text
simulation_id
```

é preservado nos metadados.

Isso permite rastrear o produto reconstruído até sua simulação de origem.

---

# 32. Validação científica dos valores

Um teste específico verifica o valor reconstruído dos pixels.

Para TOD:

```text
1, 2, 3, 4
```

e dois pixels visitados duas vezes cada:

```text
pixel A → (1 + 2) / 2 = 1.5
pixel B → (3 + 4) / 2 = 3.5
```

O mesmo comportamento é validado em múltiplos canais de frequência.

---

# 33. Resultado dos testes da funcionalidade

O conjunto específico de mapmaking alcançou:

```text
15 testes passando
```

incluindo:

* domínio;
* aplicação;
* ports;
* infraestrutura;
* banco;
* repository;
* integração.

---

# 34. Regressão das funcionalidades físicas

Também foi executada uma suíte incluindo:

* mapmaking;
* Neutral Hydrogen;
* SkyMap persistido → TOD.

Resultado:

```text
26 passed
```

Isso indicou que a nova funcionalidade não introduziu regressões nos fluxos físicos anteriores.

---

# 35. Regressão global

Após o alinhamento do ambiente de dependências e correção das inconsistências de Zarr/xarray, foi executada:

```bash
pytest tests -q
```

Resultado final:

```text
1024 passed
9 skipped
1 xfailed
0 failed
```

Isso fornece uma evidência forte de ausência de regressões funcionais na suíte atualmente disponível.

---

# 36. Observação sobre dependências xarray/Zarr

Durante a regressão global foi identificada uma inconsistência no ambiente local.

O ambiente inicialmente possuía:

```text
xarray 2023.12.0
zarr   3.1.5
```

enquanto o `requirements.txt` do projeto especificava:

```text
xarray==2025.6.1
zarr==3.0.8
```

O ambiente foi alinhado às versões declaradas pelo projeto.

Após o alinhamento, os testes relacionados à persistência Zarr voltaram a passar.

Essa ocorrência não estava relacionada ao mapmaking, mas foi detectada durante sua validação global.

---

# 37. Integração com as funcionalidades físicas anteriores

Após esta implementação, o projeto passa a suportar um ciclo conceitual mais completo.

## Céu para TOD

```text
Galaxy
      \
       \
Neutral Hydrogen
         \
          v
       SkyMap
          |
          v
       map → TOD
```

## TOD para mapa

```text
TOD
 |
 v
MapMaking
 |
 v
SkyMap reconstruído
```

O fluxo geral passa a ser:

```text
modelo físico do céu
        ↓
SkyMap
        ↓
beam + pointing
        ↓
TOD
        ↓
mapmaking
        ↓
SkyMap reconstruído
```

Essa capacidade é importante para estudar efeitos instrumentais e qualidade de reconstrução.

---

# 38. Estado atual das funcionalidades físicas

No estado atual do branch, as três funcionalidades físicas solicitadas foram implementadas.

## Funcionalidade Física 1 — Galáxia

Status:

```text
CONCLUÍDA
```

Inclui:

* emissão difusa;
* PySM3;
* componentes galácticos;
* mapas por frequência;
* geração de TOD;
* persistência/reload.

## Funcionalidade Física 2 — Hidrogênio Neutro

Status:

```text
CONCLUÍDA
```

Inclui:

* domínio cosmológico;
* conversão frequência/redshift;
* PyCCL;
* matéria angular;
* temperatura HI;
* campos Gaussianos;
* campos lognormais;
* HEALPix;
* TOD;
* persistência.

## Funcionalidade Física 3 — Mapmaking

Status:

```text
CONCLUÍDA
```

Inclui:

* modelo de domínio;
* modelo DB;
* repository;
* service;
* mapmaker HEALPix;
* TOD multi-frequência;
* hit maps;
* persistência;
* provenance;
* round-trip.

---

# 39. Limitações atuais

A implementação atual representa um primeiro mapmaker funcional e arquiteturalmente extensível.

Entretanto, existem limitações científicas importantes.

---

# 40. Naive binning

O algoritmo atual assume pesos iguais para todas as amostras:

```text
m[p] = média simples das observações
```

Ele não considera:

* variância temporal do ruído;
* correlação temporal;
* ruído 1/f;
* pesos por detector;
* flagging;
* gaps no TOD;
* covariância instrumental.

---

# 41. Pixels não observados

Pixels sem hits recebem:

```text
0
```

Nesta primeira versão.

Para análise científica futura pode ser mais apropriado utilizar:

```text
NaN
```

ou uma máscara explicitamente propagada nas etapas seguintes.

O `observed_mask` já fornece a informação necessária para essa evolução.

---

# 42. Beam

O mapmaking atual não realiza deconvolução do beam.

O mapa reconstruído representa aproximadamente o céu já observado através da resposta instrumental aplicada durante a geração do TOD.

Uma reconstrução mais avançada poderá considerar o beam explicitamente.

---

# 43. Polarização

A implementação atual produz mapas:

```text
field = I
```

O suporte a:

```text
Q
U
```

poderá ser adicionado posteriormente mediante a definição da matriz de pointing/polarização apropriada.

---

# 44. Frequências

Cada canal é reconstruído individualmente.

Isso é apropriado para a estrutura atual do `SkyMap`, mas o custo cresce linearmente com o número de canais.

Para o BINGO, com centenas ou milhares de canais, será importante considerar:

* execução lazy;
* chunking;
* Dask;
* paralelização por canal;
* processamento em blocos de frequência.

---

# 45. Uso de memória

O adapter atual utiliza:

```text
np.asarray(temperature.values)
```

para um canal de frequência.

Isso evita materializar todos os canais simultaneamente, mas ainda materializa todo o eixo temporal daquele canal.

Para simulações de 24 horas ou superiores, futuras versões podem processar:

```text
time chunks
```

e acumular:

```text
temperature_sum
hit_map
```

incrementalmente.

---

# 46. Weighted binning

A próxima evolução natural é:

[
m_p =
\frac{\sum_t w_t d_t}
{\sum_t w_t}
]

com:

```text
w_t = 1 / σ_t²
```

quando existir uma estimativa de variância instrumental por amostra.

O atual `hit_map` poderia ser complementado por:

```text
weight_map
```

---

# 47. Destriping

Para TOD com ruído correlacionado, uma evolução importante seria um mapmaker por destriping.

O modelo conceitual seria:

```text
TOD =
sky signal
+
baseline noise
+
white noise
```

e o algoritmo buscaria estimar e remover offsets temporais antes do binning.

---

# 48. Generalized Least Squares

Uma evolução de maior fidelidade científica é o método GLS.

O modelo geral é:

[
d = Pm + n
]

onde:

* (d) é o TOD;
* (P) é a matriz de pointing;
* (m) é o mapa;
* (n) é o ruído.

A solução de máxima verossimilhança é:

[
\hat{m} =
(P^T N^{-1} P)^{-1}
P^T N^{-1} d
]

Essa implementação exige:

* modelo de covariância de ruído;
* operadores lineares;
* técnicas iterativas;
* processamento distribuído;
* controle rigoroso de memória.

A criação do `MapMakerPort` permite incorporar esse tipo de algoritmo futuramente sem modificar os casos de uso.

---

# 49. Roadmap recomendado

## MM-FUTURE-01 — Weighted binning

Adicionar suporte a pesos por amostra.

## MM-FUTURE-02 — Flagging

Permitir excluir amostras inválidas do TOD.

## MM-FUTURE-03 — Noise model

Integrar estimativas de ruído instrumental.

## MM-FUTURE-04 — Destriping

Implementar remoção de baselines temporais.

## MM-FUTURE-05 — GLS

Criar adapter de maximum-likelihood mapmaking.

## MM-FUTURE-06 — Dask

Processar TOD por chunks temporais.

## MM-FUTURE-07 — Parallel frequency reconstruction

Distribuir canais entre workers.

## MM-FUTURE-08 — Polarization

Reconstruir mapas I/Q/U.

## MM-FUTURE-09 — Beam-aware mapmaking

Incorporar resposta instrumental no operador de reconstrução.

## MM-FUTURE-10 — Map comparison

Adicionar métricas:

```text
input map
vs
reconstructed map
```

como:

```text
RMS
bias
residual map
angular power spectrum
correlation
```

---

# 50. Avaliação arquitetural

A implementação segue adequadamente a arquitetura pretendida.

## Domain

Contém:

```text
MapMakingResult
```

e não depende de persistência.

## Application

Contém:

```text
MapMakerPort
MapMakingRepositoryPort
GenerateSkyMapsFromTODUseCase
MapMakingService
```

## Infrastructure

Contém:

```text
HealpyBinnedMapMakerAdapter
MapMakingRecord
MapMakingRepository
```

Essa separação mantém:

```text
regra científica
≠
orquestração
≠
persistência
```

---

# 51. Avaliação científica

O naive binning implementado é adequado como primeiro mapmaker porque:

* possui interpretação física direta;
* é determinístico;
* permite validação simples;
* fornece hit maps;
* cria baseline para comparação com algoritmos futuros;
* possui custo computacional relativamente baixo;
* permite verificar o ciclo map → TOD → map.

Ele não deve ser considerado o método final para análise instrumental realista com ruído correlacionado, mas constitui uma base correta para evolução.

---

# 52. Avaliação de persistência

A estratégia:

```text
PostgreSQL → metadados
HDF5       → arrays
```

é preferível ao armazenamento de grandes mapas diretamente em blobs SQL.

As principais vantagens são:

* escalabilidade;
* menor pressão sobre o banco;
* facilidade para análise externa;
* interoperabilidade científica;
* possibilidade futura de lazy loading;
* melhor separação entre catálogo e armazenamento de dados.

---

# 53. Critérios de conclusão

A funcionalidade é considerada concluída no escopo definido porque os seguintes critérios foram atendidos:

```text
[x] modelo de domínio
[x] modelo de DB
[x] modelo de repositório
[x] modelo de serviço
[x] port de mapmaking
[x] implementação HEALPix
[x] reconstrução por canal
[x] hit map
[x] máscara observada
[x] persistência
[x] provenance
[x] load
[x] round-trip
[x] testes de integração
[x] regressão das funcionalidades físicas
[x] regressão global sem falhas
```

---

# 54. Resultado final

A Funcionalidade Física 3 adiciona ao RadioSkySim a capacidade de transformar dados temporais simulados em produtos cartográficos HEALPix.

Antes:

```text
Sky model
→ TOD
```

Agora:

```text
Sky model
→ TOD
→ reconstructed SkyMap
```

Com isso, o projeto passa a representar uma parcela mais completa da cadeia de simulação radioastronômica:

```text
céu
→ instrumento
→ observação temporal
→ reconstrução de mapa
```

Esse fluxo cria uma base adequada para estudos futuros de:

* desempenho instrumental;
* estratégias de scanning;
* ruído;
* mapmaking;
* reconstrução cosmológica;
* comparação entre céu simulado e céu recuperado.

---

# 55. Status

```text
Funcionalidade Física 3 — Construção de mapas a partir da TOD

STATUS: CONCLUÍDA
```

Validação final da suíte:

```text
1024 passed
9 skipped
1 xfailed
0 failed
```

A implementação encontra-se integrada às funcionalidades físicas anteriores e preparada arquiteturalmente para futuras técnicas de mapmaking mais avançadas.
