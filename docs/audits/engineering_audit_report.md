# RadioSkySim — Relatório de Auditoria de Engenharia

**Data:** 2026-08-14
**Branch:** `perf/tod-performance-audit`
**Escopo:** arquitetura, qualidade de código, pontos de entrada, casos de uso, stack técnica, performance, governança documental, roadmap e riscos de engenharia.

## 1. Resumo Executivo

O RadioSkySim é uma plataforma científica de simulação do céu em rádio observado por radiotelescópios de prato único em modo de trânsito, com aplicação direta a instrumentos do tipo BINGO. A base atual integra contribuições de satélites, fontes locais, catálogos de rádio fontes, foregrounds Galácticos, hidrogênio neutro, resposta de feixe, geração de Time Ordered Data (TOD), mapas HEALPix e mapmaking.

O projeto se encontra em um estágio de desenvolvimento científico tecnicamente maduro, com ampla suíte automatizada de testes, casos de uso explícitos na camada de aplicação, persistência, processamento com Dask e instrumentação específica para análise de performance. A base auditada possui aproximadamente **36.950 linhas de código Python distribuídas em 254 arquivos**, além de **137 arquivos Python de teste**.

A arquitetura declarada segue princípios de Domain-Driven Design e Arquitetura Hexagonal, com separação entre `domain`, `application`, `infrastructure`, `interfaces` e `bootstrap`. Essa organização é visível no código, mas a aderência ainda é **parcial**: permanecem dependências diretas de Domain para Application/Infrastructure e de Application para implementações concretas de Infrastructure.

A suíte de testes encontra-se funcional e estável. Na execução auditada foram observados **1.060 testes aprovados, 9 ignorados e 1 falha esperada**, com **64% de cobertura global por statements**. Alguns fluxos desenvolvidos mais recentemente, como hidrogênio neutro, mapmaking e orquestração de TOD, apresentam cobertura elevada, enquanto módulos legados ou fortemente integrados com infraestrutura ainda possuem cobertura significativamente menor.

As ferramentas de qualidade estão configuradas, mas a base ainda não atende integralmente às regras declaradas. O Ruff encontrou **1.062 violações de lint** entre código-fonte e testes, e o formatter indicou **133 arquivos que ainda precisariam ser reformatados**. O projeto também possui configuração estrita de `mypy`, mas o executável não estava instalado no ambiente auditado. O verificador próprio de documentação encontrou **520 problemas de docstrings ou type hints básicos em 168 dos 254 arquivos de código-fonte**.

A parte de performance do pipeline TOD avançou significativamente no escopo atual. Foram realizados benchmarks de curta duração e de uma hora, otimizações importantes no fluxo de rádio fontes, correções para preservação de laziness com Dask, persistência por tipo de fonte e instrumentação de diagnóstico no processor. Experimentos que degradaram memória ou tempo de execução foram explicitamente rejeitados com base em medições. A validação integrada de 24 horas permanece pendente para execução em hardware universitário com maior capacidade de memória.

No estado atual, os principais desafios de engenharia não estão mais ligados à ausência das funcionalidades científicas centrais, mas à consolidação da base: reduzir violações de fronteira arquitetural, decompor módulos excessivamente grandes, ampliar cobertura em caminhos críticos de infraestrutura, alinhar dependências declaradas com a stack científica realmente utilizada, reduzir dívida de lint/documentação/typing e manter uma documentação canônica atualizada.

## 2. Descrição do Projeto

O RadioSkySim modela o céu em rádio observado por um radiotelescópio single dish em modo de trânsito. O objetivo principal é produzir dados simulados que incorporem efeitos físicos, instrumentais e observacionais relevantes para análise científica e etapas posteriores de reconstrução de mapas.

As principais capacidades atualmente presentes incluem:

- carregamento, modelagem e avaliação de beams;
- propagação orbital de satélites e cálculo de sua contribuição em rádio;
- modelagem de fontes locais;
- ingestão e simulação de catálogos de rádio fontes;
- geração de foregrounds Galácticos em mapas HEALPix;
- geração de campos cosmológicos de hidrogênio neutro;
- síntese de Time Ordered Data;
- processamento em batches com suporte a Dask;
- extração de eventos e RFI;
- geração e análise de mapas HEALPix;
- reconstrução de mapas a partir de TOD;
- persistência de simulações, mapas e produtos de mapmaking;
- interfaces CLI e GUI baseadas em Panel.

A base de código está organizada principalmente nas seguintes camadas:

- `domain`: modelos científicos, entidades, value objects e serviços de domínio;
- `application`: casos de uso, orquestração e ports da aplicação;
- `infrastructure`: banco de dados, providers externos, adapters concretos, processamento e IO;
- `interfaces`: CLI, GUI e interfaces voltadas ao usuário;
- `bootstrap`: construção e injeção de dependências;
- `visualization`: visualização científica e plots interativos.

O pacote instalado expõe atualmente a CLI de SkyMap através do comando `radioskysims`, enquanto o fluxo operacional de TOD/GUI pode ser iniciado por `scripts/start_service.py`. Também existem módulos executáveis auxiliares, experimentais e legados, que não devem ser tratados como pontos de entrada canônicos do projeto.

## 3. Avaliação de DDD e Arquitetura

### 3.1 Arquitetura declarada

O RadioSkySim declara uma arquitetura baseada em Domain-Driven Design e Arquitetura Hexagonal (Ports and Adapters). A documentação arquitetural define explicitamente as responsabilidades das camadas e a direção desejada das dependências:

- `domain` deve conter entidades, value objects, regras de negócio e serviços de domínio;
- `application` deve orquestrar casos de uso e depender de contratos;
- `infrastructure` deve implementar adapters concretos para banco de dados, arquivos, rede e providers externos;
- `interfaces` deve concentrar CLI, GUI e API;
- `bootstrap` deve funcionar como composition root responsável pela construção das dependências concretas.

A regra-alvo mais importante é que `domain` não dependa de `application`, `infrastructure` ou `interfaces`, enquanto `application` não deve depender diretamente de implementações concretas de `infrastructure`.

### 3.2 Aderência observada

A aderência atual é parcial. A organização dos pacotes representa claramente a arquitetura pretendida, e vários fluxos mais recentes utilizam ports e casos de uso pequenos e explícitos. Entretanto, ainda existem violações reais de direção de dependência.

Foram identificadas dependências de `domain` para camadas externas, incluindo:

- `domain/simulation/simulation.py` importando `application.services.simulation_service`;
- `domain/geometry/pointing.py` importando `infrastructure.external.skyfield_loader`;
- `domain/geometry/interface.py` e `domain/geometry/skyfield_provider.py` dependendo de ports definidos em `application`;
- `domain/skymap/factory.py` e `domain/beam/services.py` utilizando diretamente infraestrutura de logging;
- `domain/satellite/selector.py` dependendo de modelo definido na camada de infraestrutura.

Também existem dependências diretas de `application` para `infrastructure`, incluindo:

- `SimOrchestrator` dependendo diretamente de `ResourceAwareProcessor`;
- resolução direta de beam loaders concretos dentro de `SimOrchestrator`;
- `SimulationService` resolvendo loaders concretos de beam;
- `RadioSourceCatalogService` dependendo de provider concreto de radio sources.

Esses casos enfraquecem a inversão de dependência e reduzem a independência das camadas internas.

### 3.3 Composition Root

O projeto possui uma direção arquitetural adequada para centralizar wiring em `bootstrap`. O arquivo `bootstrap/skymap_cli.py`, por exemplo, instancia adapters concretos e injeta os casos de uso da camada `application`, sendo um bom exemplo de composition root.

Entretanto, o wiring ainda não está completamente centralizado. Alguns serviços e orquestradores continuam resolvendo dependências concretas localmente, o que cria múltiplos pontos de composição e aumenta o acoplamento.

### 3.4 Ports e Adapters

A camada `application/ports` está bem estabelecida e contém contratos para beam, cosmologia, geometria, fontes locais, mapmaking, radio sources, satélites, simulações e sky maps.

Os fluxos mais recentes mostram melhoria clara nesse aspecto. Mapmaking, HI e SkyMap possuem contratos relativamente pequenos e explícitos, favorecendo substituição de adapters e testes isolados.

Ainda assim, parte do código legado ou central continua dependendo diretamente de implementações concretas. A recomendação é continuar a migração de forma incremental, evitando grandes refatorações simultâneas nos módulos centrais de simulação.

### 3.5 Avaliação geral de aderência

A classificação recomendada para o estado atual é:

**DDD / Arquitetura Hexagonal: aderência parcial e em consolidação.**

Pontos positivos:

- separação de diretórios coerente com as camadas;
- presença de ports explícitos;
- uso de composition roots em `bootstrap`;
- novos fluxos científicos estruturados como casos de uso;
- dívida arquitetural documentada.

Pontos que impedem classificação como aderência completa:

- dependências `Domain -> Application`;
- dependências `Domain -> Infrastructure`;
- dependências `Application -> Infrastructure`;
- wiring concreto ainda presente fora do composition root;
- módulos centrais com responsabilidades excessivamente amplas.

### 3.6 Recomendações arquiteturais

As correções devem ser feitas de forma incremental e orientadas por risco.

Prioridades recomendadas:

1. remover dependências diretas de `Domain` para `Infrastructure`;
2. eliminar o import de `Application` dentro de `domain/simulation/simulation.py`;
3. substituir dependências concretas de `SimOrchestrator` e `SimulationService` por ports;
4. manter todo novo wiring concreto exclusivamente no `bootstrap`;
5. evitar refatoração simultânea dos grandes módulos de simulação enquanto o pipeline científico estiver estável;
6. atualizar periodicamente `technical_debt.md` com status e evidência atual, evitando itens históricos tratados como dívida ativa.

## 4. Stack Técnica e Gestão de Dependências

### 4.1 Stack principal

A stack técnica do RadioSkySim é coerente com um projeto científico de simulação e processamento de dados multidimensionais.

Os principais componentes observados são:

- **Python 3.11+** como linguagem base;
- **xarray** para representação de datasets multidimensionais;
- **Dask / Distributed** para processamento lazy, chunking, execução paralela e controle de memória;
- **Astropy** para unidades e utilidades astronômicas;
- **Astroquery** para acesso a catálogos e serviços astronômicos;
- **Skyfield** para propagação orbital, efemérides e geometria;
- **Healpy** para operações sobre mapas HEALPix;
- **PySM3** para geração de foregrounds Galácticos;
- **PyCCL** para cálculos cosmológicos e espectros angulares;
- **SQLModel / SQLAlchemy** para persistência relacional;
- **Panel / HoloViews / Bokeh** para GUI e visualização interativa;
- **HTTPX** para comunicação HTTP;
- **Pytest / pytest-cov** para testes e cobertura;
- **Ruff** para lint e formatação;
- **mypy** para análise estática de tipos;
- **Pylint** como ferramenta adicional de análise estática;
- **Sphinx + MyST** para documentação técnica.

### 4.2 Papel das principais bibliotecas

`xarray` é o formato central de intercâmbio de dados dentro dos fluxos de simulação. Essa escolha é adequada ao domínio, pois permite representar explicitamente dimensões como tempo, frequência, fonte e outras coordenadas científicas.

Dask complementa esse modelo permitindo arrays lazy e processamento em chunks. No pipeline TOD, seu uso é especialmente importante para reduzir materialização prematura e permitir que datasets maiores que a memória imediata sejam manipulados de forma controlada.

Astropy, Skyfield, Healpy, PySM3 e PyCCL formam o núcleo científico externo do projeto. Essas bibliotecas cobrem unidades físicas, coordenadas e efemérides, mapas esféricos, emissão Galáctica e cosmologia, evitando reimplementação de algoritmos científicos complexos.

SQLModel e SQLAlchemy fornecem a camada relacional de persistência. O projeto também utiliza persistência em formatos científicos, como HDF5 e Zarr, para resultados multidimensionais que não se encaixam naturalmente em tabelas relacionais.

Panel, HoloViews e Bokeh são usados principalmente na camada de interfaces e visualização e não deveriam vazar para regras científicas do Domain.

### 4.3 Estado do ambiente auditado

No ambiente utilizado durante esta auditoria foram confirmadas, entre outras, as seguintes bibliotecas:

- xarray 2025.6.1;
- Dask / Distributed 2025.12.0;
- Astropy 7.2.0;
- Astroquery 0.4.11;
- Skyfield 1.54;
- Healpy 1.19.0;
- PySM3 3.4.2;
- PyCCL 3.3.6;
- SQLModel 0.0.24;
- SQLAlchemy 2.0.51;
- Panel 1.8.5;
- HoloViews 1.22.1;
- Bokeh 3.8.2;
- HTTPX 0.28.1.

### 4.4 Gestão de dependências

A gestão de dependências está atualmente fragmentada entre `pyproject.toml`, `requirements.txt` e `requirements_extra.txt`.

O `pyproject.toml` contém apenas parte das dependências necessárias para os fluxos científicos atuais. Bibliotecas importantes como Astropy, Astroquery, Healpy, PySM3, PyCCL, SQLModel, SQLAlchemy e HTTPX não aparecem integralmente na lista principal de `[project].dependencies`, embora estejam instaladas e sejam utilizadas pelo projeto.

Grande parte dessas dependências aparece em `requirements.txt`, que funciona hoje como descrição mais ampla do ambiente científico.

Isso cria três riscos principais:

1. uma instalação baseada apenas em `pip install -e .` pode não reproduzir o ambiente científico completo;
2. versões podem divergir entre `pyproject.toml`, `requirements.txt` e o ambiente efetivamente utilizado;
3. fica menos claro quais dependências são obrigatórias e quais são opcionais por funcionalidade.

### 4.5 Recomendações para dependências

A recomendação é consolidar progressivamente a definição de dependências no `pyproject.toml`.

Uma estrutura desejável seria separar:

- dependências mínimas de runtime;
- dependências científicas opcionais por feature;
- dependências de GUI;
- dependências de banco de dados;
- dependências de desenvolvimento e qualidade;
- dependências de documentação.

Os arquivos `requirements*.txt` podem continuar existindo como ambientes pinados ou lockfiles auxiliares, mas não deveriam ser a única fonte de verdade para dependências funcionais do pacote.

Também é recomendável documentar explicitamente quais features exigem bibliotecas opcionais como PySM3, Healpy, PyCCL, Astroquery ou interfaces gráficas.

## 5. Pontos de Entrada e Casos de Uso

### 5.1 Pontos de entrada identificados

O projeto possui mais de um ponto executável, mas eles têm finalidades diferentes e não devem ser tratados como equivalentes.

O entrypoint empacotado oficialmente é definido em `pyproject.toml`:

`radioskysims = radioskysims.bootstrap.skymap_cli:main`

Esse fluxo corresponde à CLI de SkyMap e utiliza `bootstrap/skymap_cli.py` como composition root, construindo adapters concretos e injetando casos de uso da camada `application`.

Para o fluxo operacional de simulação/TOD com interface gráfica, o projeto também possui:

`scripts/start_service.py`

Esse script utiliza `create_sim_orchestrator()` definido em `bootstrap`, executa uma simulação com os defaults configurados e inicia o `TODPanel`.

Além desses dois fluxos principais, existem pontos executáveis auxiliares ou experimentais em módulos como:

- `application/tod_panel.py`;
- `application/radiotelescope_panel.py`;
- `application/gain_panel.py`;
- `bootstrap/skymap_gui.py`;
- `interfaces/cli/generate.py`;
- `interfaces/gui/beam_panel.py`;
- `infrastructure/db/init_db.py`;
- `infrastructure/config/config_loader.py`.

Também permanece `src/radioskysims/main.py`, que representa um fluxo antigo de inicialização de satélites e GUI. Esse módulo faz wiring direto de infraestrutura e utiliza APIs que não representam o caminho arquitetural atual, devendo ser tratado como legado/obsoleto.

### 5.2 Classificação recomendada dos entrypoints

A classificação recomendada é:

- **Oficial — CLI SkyMap:** `radioskysims.bootstrap.skymap_cli:main`;
- **Operacional — TOD/GUI:** `scripts/start_service.py`;
- **Auxiliares/experimentais:** módulos Panel, GUI e CLIs locais usados para desenvolvimento;
- **Utilitários de infraestrutura:** inicialização de banco e ferramentas de configuração;
- **Legado/obsoleto:** `src/radioskysims/main.py` e outros fluxos que não seguem o composition root atual.

A documentação deve evitar apresentar todos esses módulos como pontos de entrada igualmente suportados.

> **Atualização — 2026-09-11:** após a auditoria de entrypoints/UX, o console script oficial `radioskysims` passou a apontar para `radioskysims.bootstrap.cli:main`, que atua como composition root da CLI umbrella. O módulo `radioskysims.bootstrap.skymap_cli` foi mantido como wrapper de compatibilidade para imports legados.

### 5.3 Casos de uso da camada Application

A camada `application` expõe atualmente casos de uso e serviços que podem ser agrupados em quatro grandes áreas.

#### Simulação e TOD

- `SimOrchestrator`;
- `SimulationService`;
- `TODOrchestrator`;
- `TODService`;
- `SourceAssembler`.

Esse grupo coordena a montagem das fontes, execução das simulações, integração com beam, processamento em batches e produção de TOD.

#### Fontes e foregrounds

- `BuildRadioSourcesCatalogUseCase`;
- `BuildNvssSpecfindCatalogUseCase`;
- `ComputeRadioSourcesForegroundUseCase`;
- `RadioSourceCatalogService`;
- `LocalSourcesService`;
- `SatelliteService`.

Esses componentes tratam aquisição, seleção, preparação e simulação de fontes que contribuem para o sinal observado.

#### SkyMap, Galaxy e Hidrogênio Neutro

- `GenerateSkyMapUseCase`;
- `ContinuumSurveyMapUseCase`;
- `AnalyzeSkyMapUseCase`;
- `GenerateGalaxyMapsUseCase`;
- `GenerateNeutralHydrogenMapUseCase`;
- `GenerateNeutralHydrogenMapsUseCase`.

Esse grupo cobre geração e análise de mapas, foreground Galáctico e campos cosmológicos de HI.

#### Mapmaking

- `GenerateSkyMapsFromTODUseCase`;
- `MapMakingService`.

Esses componentes implementam a transformação de Time Ordered Data em mapas reconstruídos.

### 5.4 Avaliação dos casos de uso

Os fluxos científicos mais recentes apresentam boa separação de responsabilidades.

Como exemplos positivos:

- `GenerateSkyMapsFromTODUseCase` possui cerca de 90 linhas;
- `GenerateNeutralHydrogenMapUseCase` possui cerca de 141 linhas;
- `GenerateNeutralHydrogenMapsUseCase` possui cerca de 127 linhas;
- `GenerateGalaxyMapsUseCase` possui cerca de 130 linhas;
- os ports de Mapmaking possuem contratos pequenos e específicos.

Esses módulos são exemplos de organização desejável: casos de uso relativamente pequenos, dependências explícitas e responsabilidade bem delimitada.

Em contraste, parte significativa da orquestração histórica está concentrada em poucos módulos muito grandes, principalmente `SimOrchestrator`, `SimulationService` e `domain/simulation/simulation.py`.

### 5.5 Inconsistência identificada no README

O README auditado contém um exemplo que chama:

`orchestrator.run_simulation(...)`

Entretanto, a implementação atual de `SimOrchestrator` expõe `run(...)` e não possui `run_simulation(...)`.

Esse exemplo deve ser atualizado para evitar que a documentação pública apresente uma API inexistente.

## 6. Qualidade de Código

### 6.1 Dimensão da base

A base auditada contém aproximadamente **36.950 linhas de código Python** distribuídas em **254 arquivos** dentro de `src/radioskysims`.

Distribuição aproximada por camada:

- `domain`: 14.141 LOC;
- `infrastructure`: 10.556 LOC;
- `application`: 6.542 LOC;
- `interfaces`: 3.227 LOC;
- `visualization`: 1.289 LOC;
- `bootstrap`: 762 LOC.

Também foram identificados **137 arquivos Python de teste**.

Essa distribuição mostra que a maior parte da complexidade está concentrada em Domain e Infrastructure, o que é coerente com o caráter científico e orientado a adapters do projeto, mas aumenta a importância de manter fronteiras arquiteturais claras.

### 6.2 Maiores módulos

Os maiores arquivos identificados foram:

- `domain/simulation/simulation.py`: 1.558 linhas;
- `application/services/sim_orchestrator.py`: 1.552 linhas;
- `visualization/waterfall.py`: 1.251 linhas;
- `infrastructure/processing/resource_processor.py`: 1.093 linhas;
- `application/services/simulation_service.py`: 1.006 linhas;
- `interfaces/gui/skymap/presenters.py`: 919 linhas;
- `domain/tod/simulator.py`: 849 linhas;
- `infrastructure/db/satellite/satelliterepository.py`: 803 linhas.

Esses módulos devem ser considerados hotspots de manutenção.

Tamanho por si só não implica necessariamente baixa qualidade, mas os arquivos centrais de simulação combinam grande volume com múltiplas responsabilidades, tornando-os candidatos prioritários para decomposição incremental.

### 6.3 Principais candidatos a refatoração

Os principais candidatos são:

- `domain/simulation/simulation.py`;
- `application/services/sim_orchestrator.py`;
- `application/services/simulation_service.py`;
- `domain/tod/simulator.py`;
- `infrastructure/processing/resource_processor.py`;
- `visualization/waterfall.py`.

A recomendação não é executar uma grande refatoração imediata desses módulos. Como eles estão ligados a fluxos científicos sensíveis e hoje possuem uma suíte estável de testes, o risco de regressão deve ser reduzido por extrações pequenas e progressivas.

Possíveis linhas de decomposição incluem:

- separar resolução de configuração de execução;
- separar composição de fontes;
- separar persistência e serialização;
- separar política de processamento e batching;
- separar geração de dataset de operações auxiliares;
- extrair lógica de visualização independente do estado de GUI.

### 6.4 Módulos com boa organização

Alguns módulos mais recentes apresentam melhor equilíbrio entre tamanho, responsabilidade e testabilidade.

Entre os exemplos positivos estão:

- `application/mapmaking/generate_from_tod.py`;
- `application/cosmology/generate_hi_map.py`;
- `application/cosmology/generate_hi_maps.py`;
- `application/skymap/generate_continuum.py`;
- `application/ports/mapmaking.py`;
- `application/ports/mapmaking_repository.py`.

Esses componentes seguem melhor o padrão de casos de uso pequenos, contratos explícitos e baixa quantidade de responsabilidades.

### 6.5 Lint e formatação

O projeto possui Ruff configurado para lint e formatação.

Na auditoria, a execução:

`ruff check src tests`

encontrou **1.062 violações**.

A distribuição foi:

- **667 violações em `src`**;
- **395 violações em `tests`**.

No código de produção, as categorias mais frequentes incluem:

- `EM101`: strings literais diretamente em exceções;
- `PLC0415`: imports fora do topo do módulo;
- `EM102`: f-strings usadas diretamente em exceções;
- `G004`: f-strings em logging;
- `I001`: imports não ordenados;
- `I002`: ausência do import obrigatório `from __future__ import annotations`.

Nos testes, predominam:

- imports fora do topo;
- argumentos não utilizados;
- ausência do import obrigatório de annotations;
- `pytest.raises` excessivamente amplo;
- imports não ordenados;
- uso da API legada de random do NumPy.

A execução de:

`ruff format --check src tests`

indicou:

- **133 arquivos que seriam reformatados**;
- **259 arquivos já formatados**.

Isso demonstra que a configuração de qualidade existe, mas ainda não está aplicada de forma consistente em toda a base.

### 6.6 Typing

O `pyproject.toml` configura `mypy` em modo `strict` para `src` e `tests`, com regras adicionais para o pacote `radioskysims`.

Entretanto, no ambiente auditado o executável `mypy` não estava instalado.

Portanto, a situação atual deve ser descrita como:

**typing estrito configurado, mas não validado no ambiente auditado.**

Além disso, o pacote declara o classifier `Typing :: Typed`, o que torna importante validar periodicamente essa afirmação em CI.

### 6.7 Docstrings e documentação no código

O projeto possui `scripts/check_docs.py`, que verifica:

- docstrings de módulo;
- docstrings de classes;
- docstrings de funções públicas;
- type hints de retorno.

Na execução auditada:

- 254 arquivos foram verificados;
- 168 arquivos apresentaram pelo menos um problema;
- foram encontrados **520 issues**.

Esse script não substitui mypy e não mede typing completo, mas oferece uma boa métrica de cobertura documental básica.

### 6.8 Testes e cobertura

A suíte completa auditada terminou com:

- **1.060 testes aprovados**;
- **9 testes ignorados**;
- **1 xfail esperado**.

A cobertura global por statements foi de **64%**, com:

- 12.514 statements;
- 4.446 statements não cobertos;
- 100 arquivos com cobertura completa.

A cobertura é heterogênea.

Exemplos de boa cobertura:

- geração de mapa HI: aproximadamente 90%;
- geração multifrequência de HI: aproximadamente 95%;
- mapmaking application: aproximadamente 87–93%;
- `TODOrchestrator`: aproximadamente 98%;
- diversos modelos e operações de SkyMap: acima de 90%;
- `SimulationRepository`: aproximadamente 83%.

Hotspots com cobertura baixa:

- `SimulationService`: aproximadamente 17%;
- `SatelliteRepository`: aproximadamente 11%;
- `ResourceAwareProcessor`: aproximadamente 53%;
- vários entrypoints e módulos de GUI: 0%;
- alguns adapters externos e módulos legados: abaixo de 40%.

A prioridade de novos testes deve ser orientada por risco, e não apenas por aumento do percentual global.

### 6.9 Avaliação geral de qualidade

A base apresenta uma combinação de sinais positivos e dívida técnica clara.

Pontos fortes:

- suíte ampla e estável;
- cobertura elevada em diversos módulos científicos recentes;
- ferramentas de qualidade já configuradas;
- testes de integração, performance e arquitetura;
- documentação técnica extensa;
- uso consistente de type hints em partes relevantes da base.

Pontos de atenção:

- lint elevado;
- formatação não uniforme;
- mypy não validado no ambiente;
- cobertura baixa em alguns módulos críticos;
- documentação no código incompleta;
- módulos centrais excessivamente grandes;
- coexistência de código legado com fluxos atuais.

A recomendação é tratar qualidade como um processo incremental de hardening, evitando uma campanha ampla de correções automáticas que altere centenas de arquivos sem relação direta com funcionalidades em desenvolvimento.

## 7. Fluxo de Simulação TOD, Processor, Dask e Memória

### 7.1 Visão geral do fluxo

O fluxo de Time Ordered Data é um dos caminhos mais complexos e críticos do RadioSkySim.

Em alto nível, a execução parte da camada de aplicação, normalmente por meio do `SimOrchestrator`, que:

1. resolve parâmetros de execução e configuração;
2. monta ou consulta as fontes a serem simuladas;
3. prepara telescope, beam e intervalos de tempo/frequência;
4. decide entre execução direta e execução com processor;
5. delega a geração das contribuições;
6. combina os resultados em um `xarray.Dataset`;
7. retorna um objeto de resultado de simulação;
8. opcionalmente persiste ou apresenta o dataset.

A simulação pode envolver diferentes tipos de fonte, incluindo satélites, fontes locais e radio sources.

### 7.2 Papel do SimOrchestrator

`SimOrchestrator` atua como principal coordenador de alto nível do pipeline atual.

Suas responsabilidades incluem, entre outras:

- interpretar argumentos explícitos e defaults;
- coordenar configuração de telescope e beam;
- consultar e montar fontes;
- selecionar o fluxo de execução;
- integrar o `ResourceAwareProcessor`;
- construir metadados de execução;
- controlar persistência;
- gerenciar recursos Dask quando utilizados.

Essa concentração explica seu tamanho atual de aproximadamente 1.552 linhas e o torna um dos principais candidatos a decomposição futura.

Ao mesmo tempo, ele é um ponto sensível para regressões, portanto a recomendação é reduzir responsabilidades de forma incremental, preservando os contratos públicos atuais.

### 7.3 Precedência de parâmetros

A auditoria consolidou a regra de precedência para parâmetros de busca de radio sources:

**argumento explícito do construtor/chamada > valor padrão histórico.**

Foram expostos parâmetros como:

- raio de busca de radio sources;
- fluxo mínimo em Jy.

Essa abordagem permite que o chamador sobrescreva comportamento sem depender exclusivamente de configuração global.

A recomendação para novos parâmetros é manter a mesma regra de precedência sempre que o valor fizer sentido como decisão de execução.

### 7.4 ResourceAwareProcessor

O `ResourceAwareProcessor` implementa processamento em batches com foco em controle de memória.

Em vez de processar obrigatoriamente todas as fontes em uma única operação, o processor divide o trabalho em lotes e executa cada lote separadamente.

O fluxo atual é conceitualmente:

1. receber coleção de fontes;
2. estimar ou respeitar tamanho máximo de batch;
3. dividir as fontes em lotes;
4. executar `Simulation.run()` para cada lote;
5. armazenar os datasets parciais;
6. combinar os resultados ao final;
7. devolver o dataset consolidado.

A execução dos batches é atualmente serial no nível Python. Portanto, a existência de um scheduler Dask não implica automaticamente paralelização desse loop.

### 7.5 Consolidação dos datasets

O algoritmo atual mantém datasets parciais e realiza uma consolidação final.

Durante a auditoria foi avaliada uma alternativa de merge incremental, na qual o resultado acumulado seria combinado após cada batch.

Essa alternativa reduziu tempo de construção em algumas execuções, mas não apresentou redução consistente de memória. Em diferentes medições, o pico de memória permaneceu semelhante ou chegou a aumentar.

Por esse motivo, o merge incremental foi rejeitado e o comportamento original foi preservado.

Essa decisão é importante: otimizações futuras devem ser mantidas apenas quando houver benefício mensurável e repetível, e não apenas redução aparente de complexidade do código.

### 7.6 Dask e laziness

Dask é utilizado principalmente para preservar avaliação lazy de arrays grandes e permitir execução chunked.

Um princípio adotado na auditoria foi evitar chamadas desnecessárias a:

- `.compute()`;
- `.values`;
- `np.asarray(...)`;

quando essas operações causariam materialização prematura de arrays Dask.

Foi corrigido um caso no fluxo de beam em que conversões angulares poderiam destruir laziness. A solução adotada utiliza operações escalares nativas do xarray, preservando o backend Dask.

Entretanto, a auditoria também mostrou que tornar uma operação lazy não é automaticamente uma otimização.

### 7.7 Experimento de radio sources totalmente lazy

Foi avaliada uma versão experimental na qual tracks e PSD de radio sources permaneciam lazy durante uma parte maior do fluxo.

O resultado foi negativo.

No benchmark integrado de aproximadamente uma hora, a versão totalmente lazy:

- aumentou significativamente o tempo de construção;
- aumentou o pico de memória;
- gerou um grafo Dask muito maior;
- introduziu milhares de tasks adicionais.

Comparativamente, a implementação normal apresentou construção da ordem de dezenas de segundos e pico de memória na faixa de aproximadamente 3,16 GB, enquanto o experimento lazy elevou o tempo para mais de dois minutos e o pico para aproximadamente 5,46 GB.

A versão experimental foi rejeitada.

A conclusão é que laziness deve ser aplicada de forma seletiva. Grafos Dask excessivamente grandes podem custar mais memória e tempo do que uma materialização controlada.

### 7.8 Materialização controlada

A política desejada para o pipeline não é “nunca materializar”, mas:

**materializar apenas em fronteiras explícitas e em unidades controladas.**

Isso é especialmente relevante para:

- eventos;
- persistência;
- visualização;
- métricas de diagnóstico;
- operações incompatíveis com backends lazy.

O dataset principal de simulação deve permanecer lazy sempre que possível, enquanto produtos derivados podem ser materializados de forma limitada.

### 7.9 Eventos

A extração de eventos foi validada com uma política específica:

- o dataset principal permanece lazy;
- a extração de eventos pode materializar chunks de tempo;
- não deve ocorrer `Dataset.compute()` sobre o dataset completo;
- o acesso aos eventos é feito sob demanda;
- o resultado pode ser armazenado em cache após o primeiro acesso.

Essa estratégia permite produzir uma representação tabular/event-based sem obrigar a materialização integral do TOD.

### 7.10 Persistência por tipo de fonte

O resultado de simulação permite selecionar dados por tipo de fonte antes da persistência.

O fluxo suporta seleção de:

- `satellite`;
- `localsource`;
- `radiosource`.

Essa funcionalidade pode ser utilizada em persistência HDF5/Zarr para armazenar subconjuntos relevantes sem necessidade de duplicar toda a lógica de simulação.

A seleção preserva metadados e procura manter laziness até a fronteira de escrita.

### 7.11 Diagnósticos do processor

Foi adicionada instrumentação opcional ao `ResourceAwareProcessor`.

Quando habilitada, ela registra informações como:

- RSS antes dos batches;
- RSS antes de cada batch;
- RSS após `Simulation.run()`;
- RSS após o merge final;
- contagem de fontes por tipo;
- tamanho lógico dos datasets parciais;
- tamanho lógico do dataset consolidado;
- backend das principais variáveis;
- quantidade aproximada de tasks Dask.

A instrumentação é desabilitada por padrão para não alterar o custo do caminho normal.

Ela deve ser tratada como ferramenta de diagnóstico e benchmarking, não como parte obrigatória da execução científica.

### 7.12 Dask Distributed

O fluxo foi validado com `dask.distributed.Client` local.

Esse modo permite:

- acompanhamento do scheduler;
- visualização do dashboard;
- inspeção de tasks e workers;
- execução controlada de grafos lazy.

Entretanto, é importante distinguir duas formas de paralelismo:

- paralelismo dentro de grafos Dask;
- paralelismo do loop Python de fontes/batches.

Atualmente, o loop de fontes e o loop de batches permanecem essencialmente seriais. O scheduler Dask paraleliza apenas tarefas representadas no grafo.

### 7.13 Perfil de memória

Os benchmarks mostraram que a principal pressão de memória não está associada a um único ponto isolado.

Os principais fatores incluem:

- datasets parciais simultaneamente vivos;
- criação do dataset final durante concatenação/merge;
- cópias temporárias geradas por operações xarray;
- materialização de arrays em caminhos específicos;
- tamanho dos grafos Dask;
- estruturas de tracks e beam para muitas fontes.

A operação final de concatenação pode temporariamente coexistir com os datasets de entrada, criando aproximadamente uma cópia adicional do tamanho do dataset final.

Esse comportamento deve ser considerado em qualquer estimativa de memória para execuções longas.

### 7.14 Escala de 24 horas

O cenário-alvo solicitado para validação é uma observação de aproximadamente 24 horas com resolução temporal de um minuto e múltiplos tipos de fonte.

A máquina local utilizada na auditoria possui aproximadamente 7,5 GiB de RAM.

Os benchmarks de uma hora mostraram consumo de memória suficiente para indicar que uma extrapolação ingênua para 24 horas não é segura nesse hardware.

Por esse motivo, foi tomada a decisão de não continuar forçando a execução completa de 24 horas na máquina local.

A validação final de escala será realizada em hardware universitário com maior capacidade de RAM e CPU.

Essa pendência deve ser classificada como:

**validação externa de escala**, e não como bloqueio funcional ou falha do pipeline atual.

### 7.15 Estado atual do pipeline TOD

No escopo auditado, o pipeline TOD pode ser considerado funcional e substancialmente otimizado.

Estão concluídos:

- processamento em batches;
- integração com Dask;
- preservação de laziness em caminhos importantes;
- otimizações relevantes para radio sources;
- persistência por tipo de fonte;
- eventos com materialização chunk-wise;
- diagnósticos opcionais de memória/backend;
- suporte a Dask Distributed;
- benchmarks de curta duração e uma hora.

Permanece pendente principalmente:

- validação integrada de 24 horas em hardware adequado;
- redução futura da memória do merge final;
- possível paralelização controlada do loop de batches/fontes;
- decomposição arquitetural dos módulos centrais sem regressão científica.

## 8. Eficiência, Gargalos e Melhorias Prioritárias

### 8.1 Ganhos já obtidos

A auditoria de performance mostrou que parte relevante do custo do pipeline TOD estava concentrada em operações evitáveis ou em caminhos pouco eficientes de radio sources.

Entre os ganhos já consolidados estão:

- redução significativa do tempo de processamento de radio sources após otimizações de ordenação e avaliação de beam;
- remoção de ordenações redundantes em `time`;
- preservação de laziness em conversões angulares do beam;
- uso de batches com tamanho controlado;
- instrumentação de memória e backend no processor;
- persistência seletiva por tipo de fonte;
- extração de eventos sem materialização integral do dataset;
- suporte a `dask.distributed.Client` para inspeção e execução local.

Em benchmarks curtos, o fluxo de radio sources apresentou redução de tempo de aproximadamente dois minutos para poucos segundos em cenários comparáveis após as otimizações de beam e ordenação.

### 8.2 Gargalo de memória no merge final

O principal gargalo estrutural ainda observado é a consolidação dos datasets parciais.

Durante o merge ou concatenação final, os datasets de entrada podem permanecer vivos enquanto o dataset consolidado é criado. Isso produz um pico de memória superior ao tamanho lógico do resultado final.

Portanto, o consumo máximo de memória não pode ser estimado apenas pelo `nbytes` do dataset produzido.

Esse ponto é particularmente relevante para observações longas e para execuções com grande quantidade de fontes.

### 8.3 Loops seriais

Dois loops importantes permanecem seriais no nível Python:

- processamento de fontes dentro da simulação;
- processamento de batches dentro do `ResourceAwareProcessor`.

Isso significa que a presença de Dask não garante paralelização total do pipeline.

Uma futura otimização pode explorar paralelização controlada desses loops, mas deve considerar:

- competição por memória;
- custo de serialização;
- segurança de acesso a banco e providers;
- crescimento do grafo Dask;
- impacto sobre reproducibilidade;
- possibilidade de múltiplas materializações simultâneas.

A prioridade deve ser throughput com limite de memória, e não simplesmente maximizar o número de tarefas concorrentes.

### 8.4 Grafos Dask excessivamente grandes

A tentativa de tornar uma parte maior do fluxo de radio sources totalmente lazy produziu um grafo Dask muito maior e piorou tanto tempo quanto memória.

Esse resultado mostra que o número de tasks e a profundidade do grafo devem ser tratados como métricas de performance.

A recomendação é evitar:

- criação de milhares de pequenas tasks;
- encadeamento excessivo de operações elementares;
- laziness aplicada a estruturas pequenas ou baratas de materializar;
- construção de grafos complexos antes de operações inevitavelmente eager.

### 8.5 Materialização como decisão arquitetural

Chamadas a `.compute()`, `.values` ou conversões NumPy não devem ser proibidas de forma absoluta.

Elas devem ocorrer em fronteiras identificáveis, por exemplo:

- persistência;
- visualização;
- exportação;
- estatísticas finais;
- eventos por chunk;
- bibliotecas externas que não aceitam arrays Dask.

O problema arquitetural é a materialização implícita e não controlada dentro de funções intermediárias.

Por isso, a recomendação é documentar nos métodos relevantes se eles:

- preservam laziness;
- materializam apenas uma variável;
- materializam um chunk;
- materializam o dataset completo.

### 8.6 Tamanho de batch

O tamanho de batch é uma das principais alavancas para equilibrar memória e throughput.

Um batch pequeno reduz pico de memória, mas aumenta:

- número de chamadas;
- overhead de concatenação;
- overhead de setup;
- quantidade de datasets intermediários.

Um batch grande reduz overhead, mas aumenta o working set e pode aproximar a execução do limite físico de RAM.

A política ideal deve continuar baseada em medição real e, quando possível, em estimativas de memória por tipo de fonte.

### 8.7 Radio sources

Radio sources foram um dos maiores focos de otimização.

Os principais custos observados estavam associados a:

- tracks;
- ordenação temporal;
- avaliação de beam;
- propagação de arrays multidimensionais;
- construção de datasets intermediários.

As otimizações atuais já produziram ganhos relevantes. Novas alterações nesse fluxo devem ser justificadas por benchmarks, porque a tentativa de ampliar laziness mostrou que modificações conceitualmente atraentes podem piorar significativamente o desempenho real.

### 8.8 Persistência

A persistência por tipo de fonte reduz a necessidade de salvar datasets completos quando o usuário deseja apenas um subconjunto científico.

Essa funcionalidade também permite organizar pipelines posteriores de análise por contribuição física.

Como melhoria futura, pode ser avaliada uma estratégia de escrita incremental/chunked diretamente durante o processamento, reduzindo a necessidade de manter todo o resultado consolidado em memória.

Essa abordagem, porém, alteraria o contrato atual de produção do dataset e deve ser tratada como evolução arquitetural, não como otimização local.

### 8.9 Cobertura dos hotspots

Alguns módulos críticos de performance ainda possuem cobertura moderada ou baixa.

Em especial:

- `ResourceAwareProcessor` possui cobertura próxima de 53%;
- `SimulationService` possui cobertura próxima de 17%.

Antes de refatorações estruturais nesses componentes, é recomendável aumentar cobertura sobre:

- batching;
- merge;
- exceções;
- diferentes tipos de fonte;
- comportamento com datasets lazy;
- comportamento com datasets materializados;
- limites e falhas de memória simuladas;
- configuração do processor.

### 8.10 Observabilidade

A telemetria opcional adicionada ao processor é uma base importante para evolução futura.

Como extensão, pode ser útil registrar de forma estruturada:

- duração por batch;
- duração por tipo de fonte;
- número de fontes por batch;
- tamanho lógico de cada variável;
- número de tasks do grafo;
- RSS máximo observado;
- tempo de merge;
- tempo de persistência;
- versão das principais dependências científicas.

Esses dados permitiriam comparar benchmarks ao longo do tempo e identificar regressões automaticamente.

### 8.11 Melhorias prioritárias

As melhorias de performance recomendadas, em ordem aproximada de valor e risco, são:

1. manter e ampliar benchmarks reproduzíveis;
2. aumentar testes do `ResourceAwareProcessor`;
3. medir explicitamente tempo e memória do merge final;
4. estudar escrita incremental/chunked como alternativa para execuções muito longas;
5. avaliar paralelismo limitado de batches apenas em hardware com memória suficiente;
6. reduzir materializações implícitas identificadas por profiling;
7. monitorar tamanho dos grafos Dask como métrica de regressão;
8. executar a validação completa de 24 horas em hardware universitário;
9. evitar novas estratégias full-lazy sem benchmark integrado;
10. tratar otimizações como mudanças experimentais reversíveis até que apresentem ganho mensurável.

### 8.12 Critério para aceitar otimizações

Uma otimização deve ser considerada válida somente quando houver evidência de melhoria em pelo menos uma métrica relevante sem regressão inaceitável nas demais.

As métricas mínimas recomendadas são:

- tempo de construção;
- tempo total de execução;
- pico de RSS;
- tamanho lógico do dataset;
- número de tasks Dask;
- número de fontes;
- número de batches;
- correção científica do resultado.

Esse critério já se mostrou útil durante a auditoria, permitindo rejeitar alterações que pareciam arquiteturalmente elegantes, mas degradavam a execução real.

## 9. Novas Funcionalidades Científicas e de Engenharia

### 9.1 Foregrounds Galácticos

O projeto passou a possuir um fluxo explícito para geração de foregrounds Galácticos em mapas HEALPix.

Esse fluxo utiliza PySM3 para representar componentes como:

- synchrotron;
- emissão térmica de poeira;
- free-free.

A geração pode ser realizada por frequência ou em múltiplos canais, permitindo produzir mapas compatíveis com o pipeline de simulação.

Também existe integração com o fluxo de TOD, no qual mapas de céu podem ser projetados ao longo do apontamento do radiotelescópio e combinados com a resposta do beam.

Uma decisão arquitetural importante foi manter separados os fluxos baseados em:

- tracks de fontes discretas;
- mapas do céu.

Essa separação reduz a necessidade de tratar estruturas físicas diferentes através de uma única abstração excessivamente genérica.

### 9.2 Persistência e reutilização de SkyMaps

Mapas HEALPix podem ser persistidos e reutilizados posteriormente.

O fluxo permite:

- geração do mapa;
- persistência em formato científico;
- recarga do produto armazenado;
- uso do mapa persistido em etapas posteriores de TOD.

Essa capacidade evita recomputar modelos físicos caros quando o mesmo sky map será utilizado em múltiplas simulações.

### 9.3 Hidrogênio Neutro

Foi implementado um fluxo específico para simulação cosmológica de hidrogênio neutro.

Os principais componentes incluem:

- parâmetros cosmológicos de domínio;
- conversão entre frequência observada e redshift;
- cálculo de espectros angulares com PyCCL;
- geração de campos Gaussianos sobre HEALPix;
- geração de campo lognormal;
- cálculo de temperatura de brilho;
- geração de mapas por canal;
- geração multifrequência;
- projeção de mapas para TOD;
- persistência dos mapas produzidos.

O fluxo de HI está representado por casos de uso explícitos na camada Application, evitando concentrar toda a lógica física dentro do `SimOrchestrator`.

### 9.4 Campo lognormal de HI

Foi adicionada uma implementação lognormal baseada em Healpy como baseline de baixo custo.

A transformação utilizada segue a forma:

`delta_LN = exp(g - sigma_g^2 / 2) - 1`

onde `g` representa o campo Gaussiano subjacente.

Foram adicionados testes estatísticos para verificar propriedades básicas do campo produzido, incluindo:

- média de ensemble aproximadamente nula;
- limite físico superior a `-1`;
- espectro angular finito;
- potência angular não trivial.

A implementação local não pretende preservar exatamente o espectro de entrada após a transformação não linear. Esse comportamento é documentado como uma limitação conhecida.

### 9.5 Avaliação de FLASK e nbodykit

Também foram avaliadas alternativas externas para geração de campos cosmológicos mais sofisticados.

FLASK foi identificado como opção potencial para campos lognormais correlacionados e aplicações tomográficas.

nbodykit foi considerado como uma alternativa mais ampla para fluxos de Large Scale Structure.

Essas ferramentas não foram incorporadas como dependências obrigatórias no escopo atual devido ao custo adicional de integração e dependências.

Uma evolução futura pode implementá-las como adapters opcionais de um port de geração de campo de matéria.

### 9.6 Mapmaking

Foi adicionado um fluxo explícito de mapmaking a partir de TOD.

A arquitetura inclui:

- modelos de domínio para resultado de mapmaking;
- port de aplicação;
- implementação baseada em binning Healpy;
- geração multifrequência;
- serviço de aplicação;
- repositório;
- persistência HDF5.

O caso de uso `GenerateSkyMapsFromTODUseCase` é um dos exemplos mais claros de aplicação pequena e orientada a um objetivo específico.

### 9.7 Persistência por tipo de fonte

`SimulationResult` passou a permitir seleção por tipo de fonte antes da persistência.

Os tipos suportados no escopo atual incluem:

- `satellite`;
- `localsource`;
- `radiosource`.

Essa funcionalidade é útil para análises separadas das contribuições físicas e também reduz a necessidade de persistir dados que não serão utilizados.

### 9.8 Busca de resultados de simulação

O repositório de simulações passou a oferecer busca por metadados sem exigir carregamento dos datasets armazenados.

Os filtros disponíveis incluem:

- intervalo de data de criação;
- interseção com intervalo de observação;
- telescope;
- faixa de frequência;
- estado de persistência;
- estado de registro;
- paginação por `limit` e `offset`.

Os resultados possuem ordenação determinística por data de criação e identificador.

Essa abordagem é especialmente importante porque permite localizar simulações grandes apenas através de metadados relacionais.

### 9.9 Busca por tipo de fonte no repositório

A busca por `source_type` não foi incorporada ao filtro relacional atual.

A informação está representada em metadados JSON e não como coluna escalar adequada para esse tipo de consulta.

Adicionar esse filtro exigiria decisão de schema e possível migração de banco.

Por esse motivo, a ausência foi documentada em vez de introduzir uma mudança de persistência apenas para atender uma busca isolada.

### 9.10 Representação concisa de SimulationResult

Foi adicionada uma representação textual simples para resultados de simulação.

O `repr` evita imprimir ou materializar o dataset completo e apresenta apenas informações resumidas, como:

- dimensões;
- backend;
- quantidade de fontes;
- intervalo temporal;
- faixa de frequência;
- data de criação.

Essa melhoria facilita uso interativo em notebooks e debugging sem produzir grandes dumps de dados.

### 9.11 Eventos lazy e materialização chunk-wise

O contrato de eventos foi formalizado para evitar materialização integral do TOD.

O dataset principal permanece lazy e os eventos são extraídos de forma controlada por chunks.

O accessor é avaliado sob demanda e pode manter o resultado em cache após o primeiro acesso.

Esse comportamento foi acompanhado por testes que garantem que a extração não executa um `compute()` global sobre o dataset completo.

### 9.12 Diagnósticos de processamento

O `ResourceAwareProcessor` recebeu suporte opcional a diagnósticos detalhados.

Esse recurso permite registrar:

- memória RSS;
- backend NumPy/Dask;
- tamanho lógico dos datasets;
- contagem de fontes;
- quantidade aproximada de tasks;
- estado antes e depois das principais etapas.

O recurso é opt-in e permanece desabilitado no caminho normal.

### 9.13 Parâmetros explícitos para radio sources

O orquestrador passou a aceitar parâmetros explícitos para busca de radio sources, incluindo:

- raio angular de pesquisa;
- fluxo mínimo em Jy.

Isso reduz dependência de defaults internos e torna execuções científicas mais reproduzíveis.

A precedência adotada é:

`argumento explícito > default histórico`

enquanto não existirem campos equivalentes consolidados na configuração global.

### 9.14 Estado das novas funcionalidades

No escopo atual da entrega, podem ser considerados implementados:

- foreground Galáctico por mapas;
- persistência/reuso de SkyMaps;
- cosmologia de HI;
- campo Gaussiano de HI;
- baseline lognormal de HI;
- validação estatística do lognormal;
- avaliação arquitetural de FLASK/nbodykit;
- TOD a partir de mapas;
- Mapmaking;
- persistência por tipo de fonte;
- buscas expandidas no repositório;
- representação concisa de resultados;
- eventos com materialização controlada;
- diagnósticos do processor;
- parâmetros explícitos de busca de radio sources.

A evolução futura dessas funcionalidades deve priorizar integração, robustez e escalabilidade, em vez de adicionar novos caminhos paralelos sem necessidade científica clara.

## 10. Governança da Documentação

### 10.1 Situação encontrada

A documentação do RadioSkySim é extensa e cobre arquitetura, relatórios técnicos, diagramas, API, performance, qualidade de código e planejamento.

Entretanto, parte importante dessa documentação foi produzida em momentos diferentes da evolução do projeto e passou a coexistir sem uma separação clara entre:

- documentação canônica;
- snapshots históricos;
- relatórios de auditoria;
- roadmaps antigos;
- documentação gerada automaticamente.

Essa sobreposição aumentava o risco de leitura de métricas antigas como se fossem estado atual.

### 10.2 Arquivamento de relatórios históricos

Durante esta auditoria, o conjunto histórico localizado em:

`docs/source/reports/`

foi movido para:

`docs/_archive/reports_2026-01/`

O conjunto arquivado contém:

- `ANALISE_RADIOSKYSIM.md`;
- `DOCUMENTATION_STATUS.md`;
- `INDICE_ANALISE.md`;
- `ROADMAP_SDLC.md`;
- `SIMPLIFICACAO_IMPORTS_2026-01-24.md`;
- `STATUS_PROJETO.txt`;
- `SUMARIO_EXECUTIVO.md`.

Esses documentos continuam preservados para rastreabilidade histórica, mas deixam de ocupar o mesmo espaço editorial da documentação corrente.

As referências externas existentes foram atualizadas para o novo caminho.

### 10.3 Documentação atual

Os documentos mais recentes de auditoria e arquitetura devem ser tratados como fontes principais para o estado atual.

Entre eles:

- `docs/audits/engineering_audit_report.md`;
- `docs/audits/tod_performance_audit_report.md`;
- `docs/audits/neutral_hydrogen_physical_feature_audit.md`;
- `docs/audits/mapmaking_physical_feature_audit.md`;
- `docs/architecture/architecture_rules.md`;
- `docs/architecture/technical_debt.md`;
- `docs/architecture/current_architecture.md`;
- `docs/architecture/entrypoints.md`;
- `docs/roadmap.md`.

Os relatórios de agosto anteriores continuam úteis como snapshots intermediários, mas devem ser interpretados pela data de referência.

### 10.4 Princípio recomendado

Todo documento de estado, auditoria ou roadmap deve conter explicitamente:

- data da análise;
- branch ou commit de referência;
- escopo;
- status editorial;
- indicação se representa estado atual ou snapshot histórico.

Métricas como número de testes, LOC, lint e cobertura devem sempre possuir data de coleta.

### 10.5 API docs

A árvore `docs/source/apidocs/` contém grande quantidade de documentação gerada ou semiautomática.

Ela deve ser tratada separadamente dos relatórios de engenharia.

A documentação gerada não deve ser usada como fonte canônica de arquitetura, porque ela descreve estrutura de código e não necessariamente intenção arquitetural.

### 10.6 README

O README funciona adequadamente como apresentação inicial do projeto, mas precisa acompanhar mudanças de API e arquitetura.

Foi identificada pelo menos uma inconsistência atual:

- o exemplo utiliza `SimOrchestrator.run_simulation(...)`;
- a API atual expõe `SimOrchestrator.run(...)`.

Também é recomendável ajustar a afirmação de que o projeto "segue arquitetura hexagonal" para deixar claro que essa é a arquitetura adotada/alvo e que ainda existem débitos de aderência.

## 11. Roadmap de Engenharia

### 11.1 Objetivo do roadmap

O roadmap atual deve priorizar consolidação e redução de risco, não expansão indiscriminada de funcionalidades.

A maior parte dos fluxos científicos solicitados já possui implementação funcional. Os próximos ciclos devem aumentar previsibilidade, testabilidade, reprodutibilidade e capacidade de execução em escala.

### 11.2 Prioridade 1 — Hardening de qualidade

Objetivos:

- reduzir violações Ruff progressivamente;
- aplicar formatação de forma controlada;
- instalar e executar mypy no ambiente/CI;
- aumentar documentação de APIs públicas;
- corrigir inconsistências do README;
- elevar cobertura de módulos críticos.

A estratégia recomendada é corrigir arquivos tocados por feature/refactor em vez de reformar toda a base em um único commit.

### 11.3 Prioridade 2 — Fronteiras arquiteturais

Objetivos:

- reduzir dependências `Domain -> Infrastructure`;
- reduzir dependências `Domain -> Application`;
- remover dependências concretas `Application -> Infrastructure`;
- consolidar wiring no `bootstrap`;
- transformar dependências concretas em ports onde houver valor real.

A evolução deve ocorrer por pequenas extrações cobertas por testes.

### 11.4 Prioridade 3 — Decomposição dos hotspots

Priorizar os maiores módulos:

- `domain/simulation/simulation.py`;
- `application/services/sim_orchestrator.py`;
- `application/services/simulation_service.py`;
- `domain/tod/simulator.py`;
- `infrastructure/processing/resource_processor.py`;
- `visualization/waterfall.py`.

A decomposição deve ser feita por responsabilidade funcional e não apenas por número de linhas.

### 11.5 Prioridade 4 — Performance e escala

Objetivos:

- executar benchmark integrado de 24 horas em hardware adequado;
- registrar pico de memória e tempo por etapa;
- medir custo do merge final;
- avaliar escrita incremental;
- estudar paralelismo controlado de batches;
- monitorar tamanho do grafo Dask;
- manter benchmarks de regressão.

### 11.6 Prioridade 5 — Dependências e reprodutibilidade

Objetivos:

- consolidar dependências funcionais no `pyproject.toml`;
- separar extras científicos e GUI;
- reduzir divergência entre `requirements.txt` e `pyproject.toml`;
- documentar dependências opcionais por feature;
- garantir ambiente reproduzível para CI e notebooks científicos.

### 11.7 Prioridade 6 — Persistência e consulta científica

Possíveis evoluções:

- avaliar modelagem relacional explícita para metadados consultados frequentemente;
- considerar `source_type` como campo indexável caso a necessidade de busca se torne recorrente;
- evoluir escrita chunked/incremental para grandes simulações;
- manter separação entre metadata query e carregamento de datasets pesados.

## 12. Proposta de Sprints de Engenharia

### Sprint 1 — Baseline de qualidade e documentação

Objetivo: tornar as métricas de engenharia reproduzíveis.

Entregas:

- corrigir README;
- documentar comandos oficiais de lint, teste, cobertura e typing;
- instalar/validar mypy;
- registrar baseline de Ruff;
- atualizar `technical_debt.md`;
- consolidar documentação canônica.

Critério de saída:

- comandos de qualidade executáveis em ambiente limpo;
- métricas documentadas com data;
- ausência de documentação concorrente tratada como estado atual.

### Sprint 2 — Cobertura dos hotspots

Objetivo: reduzir risco antes de refatorações.

Foco:

- `SimulationService`;
- `ResourceAwareProcessor`;
- caminhos de repository;
- casos de erro em batching e merge.

Critério de saída:

- testes cobrindo principais decisões de execução;
- comportamento lazy/eager explicitamente testado;
- cobertura maior nos módulos escolhidos.

### Sprint 3 — Fronteiras DDD

Objetivo: reduzir violações arquiteturais de maior impacto.

Possíveis entregas:

- remover dependência Domain -> Application em Simulation;
- mover resolução concreta de beam para composition root;
- abstrair processor por port quando fizer sentido;
- revisar dependências de geometry e satellite selector.

Critério de saída:

- redução objetiva do número de imports proibidos;
- testes preservados;
- documentação arquitetural atualizada.

### Sprint 4 — Decomposição da orquestração

Objetivo: reduzir responsabilidades de `SimOrchestrator` e `SimulationService`.

Possíveis extrações:

- resolução de configuração;
- preparação de fontes;
- preparação de beam/telescope;
- persistência;
- montagem de metadados;
- lifecycle de Dask.

Critério de saída:

- redução de tamanho e responsabilidades sem alterar API pública;
- manutenção ou aumento da cobertura;
- ausência de regressão nos benchmarks.

### Sprint 5 — Performance de escala

Objetivo: validar execução longa e preparar operação em hardware maior.

Entregas:

- benchmark de 24 horas;
- perfil de memória;
- perfil por batch;
- comparação entre scheduler local e distributed;
- avaliação de merge/escrita incremental.

Critério de saída:

- relatório reproduzível com hardware, parâmetros, tempo e memória;
- decisão documentada sobre próximos gargalos.

### Sprint 6 — Reprodutibilidade do ambiente

Objetivo: tornar instalação e execução científicas previsíveis.

Entregas:

- revisão do `pyproject.toml`;
- definição de extras;
- alinhamento com requirements;
- smoke test de instalação;
- documentação das dependências opcionais.

Critério de saída:

- instalação do pacote com conjunto de extras explicitamente documentado;
- ambiente capaz de executar os fluxos científicos correspondentes.

## 13. Status Consolidado

### Concluído no escopo atual

- pipeline TOD funcional;
- batching e processamento consciente de recursos;
- otimizações relevantes de radio sources;
- suporte a Dask e Dask Distributed;
- eventos com materialização chunk-wise;
- persistência por tipo de fonte;
- consultas ampliadas no repositório;
- foreground Galáctico;
- geração de HI;
- campo lognormal e validação estatística;
- Mapmaking;
- persistência de mapas;
- diagnósticos do processor;
- reorganização da documentação histórica;
- auditoria de qualidade e arquitetura.

### Parcial / em consolidação

- aderência completa a DDD/Hexagonal;
- lint e formatação;
- documentação de APIs;
- typing estrito;
- cobertura de módulos críticos;
- centralização completa do composition root;
- decomposição dos módulos grandes;
- consolidação das dependências.

### Pendente por validação externa

- benchmark integrado de 24 horas com todos os tipos de fonte em hardware com memória suficiente.

## 14. Matriz de Rastreabilidade do Pedido de Auditoria

| Item solicitado | Estado | Evidência / seção |
|---|---|---|
| Descrição do projeto | Concluído | Seção 2 |
| Avaliação de aderência a DDD | Concluído | Seção 3 |
| Stack técnica comentada | Concluído | Seção 4 |
| Pontos de entrada | Concluído | Seção 5 |
| Casos de uso | Concluído | Seção 5 |
| LOC total e por camada | Concluído | Seção 6 |
| Maiores módulos e candidatos a refatoração | Concluído | Seção 6 |
| Lint e formatação | Concluído | Seção 6 |
| Docstrings e type hints | Parcial | Baseline medido; mypy ainda não executado |
| Cobertura de testes | Concluído | Seção 6 |
| Melhores exemplos de módulos | Concluído | Seções 5 e 6 |
| Fluxo detalhado de TOD | Concluído | Seção 7 |
| Processor e política de batches | Concluído | Seção 7 |
| Dask e materialização lazy | Concluído | Seções 7 e 8 |
| Diagnóstico de memória | Concluído | Seções 7 e 8 |
| Otimização de radio sources | Concluído | Seções 7 e 8 |
| Dataset/persistência por tipo de fonte | Concluído | Seções 7 e 9 |
| Parâmetros explícitos no orquestrador | Concluído | Seções 7 e 9 |
| Busca ampliada no repositório | Concluído | Seção 9 |
| `repr` simples para resultados | Concluído | Seção 9 |
| Eventos com dataset principal lazy | Concluído | Seções 7 e 9 |
| Dask Local Client / Distributed | Concluído | Seção 7 |
| Benchmark TOD | Concluído para 10 min/1 h | Relatório específico de performance |
| Benchmark integrado de 24 h | Validação externa | Hardware universitário |
| Foregrounds Galácticos / PySM3 | Concluído | Seção 9 |
| TOD a partir de mapas | Concluído | Seção 9 |
| Persistência/reuso de mapas | Concluído | Seção 9 |
| Cosmologia de HI / PyCCL | Concluído | Seção 9 |
| Campo Gaussiano de HI | Concluído | Seção 9 |
| Campo lognormal de HI | Concluído | Seção 9 |
| Avaliação FLASK / nbodykit | Concluído no escopo de avaliação | Seção 9 |
| Mapmaking | Concluído | Seção 9 |
| Reorganização de `docs/` | Concluído | Seção 10 |
| Arquivamento de documentação histórica | Concluído | Seção 10 |
| Roadmap de engenharia | Concluído | Seção 11 |
| Sprints de engenharia | Concluído | Seção 12 |

## 15. Conclusão

O RadioSkySim apresenta uma base científica ampla e funcional, com evolução significativa em simulação TOD, sky maps, foregrounds, cosmologia de hidrogênio neutro e mapmaking.

A arquitetura possui uma direção clara e está melhor estruturada nos fluxos desenvolvidos mais recentemente, mas ainda carrega acoplamentos históricos importantes nos módulos centrais.

A suíte de testes fornece uma base segura para evolução, embora a cobertura ainda seja desigual. A principal dívida de engenharia está hoje em consolidação: qualidade estática, fronteiras arquiteturais, módulos grandes, dependências fragmentadas e escalabilidade de execuções longas.

A estratégia recomendada é preservar a estabilidade científica atual e avançar por sprints pequenos, mensuráveis e reversíveis. Refatorações devem ser acompanhadas por testes e benchmarks, especialmente nos caminhos de TOD e processamento.

A execução de 24 horas deve ser tratada como validação final de escala em hardware apropriado, e não como justificativa para introduzir otimizações agressivas sem evidência.
