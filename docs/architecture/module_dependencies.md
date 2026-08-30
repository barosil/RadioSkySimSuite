# Dependencias entre Modulos e Camadas - RadioSkySim

Data da auditoria: 2026-07-16
Escopo: src/radioskysims
Base: analise AST de imports internos + inspeção manual dos hotspots.

Status do documento: **baseline historica** (2026-07-16).
Revalidacao mais recente: **2026-08-05**.

## Revalidacao 2026-08-05 (delta)

Contagem atual de imports internos por origem -> destino (recálculo AST):

| Origem | Destino | Quantidade | Leitura arquitetural |
|---|---:|---:|---|
| application | domain | 49 | esperado |
| application | infrastructure | 6 | violacao residual |
| domain | domain | 39 | esperado |
| domain | infrastructure | 4 | violacao residual |
| domain | application | 3 | violacao residual |
| interfaces | application | 13 | esperado |
| interfaces | infrastructure | 2 | acoplamento direto |
| infrastructure | domain | 40 | esperado em adapters |
| infrastructure | application | 12 | alto por wrappers/compat |

Exemplos atuais de acoplamento residual:
- `application/services/catalog_services.py`
- `application/services/sim_orchestrator.py`
- `application/services/simulation_service.py`
- `domain/geometry/interface.py`
- `domain/geometry/skyfield_provider.py`
- `domain/simulation/simulation.py`

### Ajustes de diagnóstico (itens históricos superados)

- A menção a `domain/satellite/main.py` como risco ativo está desatualizada
  (arquivo ausente no estado atual).
- O risco operacional de `IndentationError` em `application/tod_panel.py` não foi
  observado na revalidação sintática atual.
- A seção de duplicação `infrastructure/files/*` vs
  `infrastructure/beams/loaders/*` deve ser tratada como histórica: não há
  `src/radioskysims/infrastructure/files/**/*.py` na base atual.

## 1. Dependencias entre camadas

Contagem de imports internos por origem -> destino:

| Origem | Destino | Quantidade | Leitura arquitetural |
|---|---:|---:|---|
| application | domain | 26 | esperado |
| application | infrastructure | 13 | violacao de camada |
| domain | domain | 91 | esperado |
| domain | infrastructure | 9 | violacao de camada |
| domain | application | 1 | violacao de camada |
| interfaces | application | 2 | esperado |
| interfaces | infrastructure | 2 | acoplamento direto |
| infrastructure | domain | 45 | esperado em adapters |
| infrastructure | application | 4 | atencao (possivel inversao) |

## 2. Dependencias entre modulos (evidencias principais)

### 2.1 Violacoes Application -> Infrastructure

- application/radiosources_use_cases.py:27
  - importa infrastructure/ports/radiosources
- application/services/sim_orchestrator.py:21,25,26,29,30,31,34
  - importa config loader, engine DB, repositories e providers externos
- application/services/simulation_service.py:23,24,27
  - importa loader de beam, config loader e logging da infraestrutura
- application/services/local_sources_service.py:22
  - importa ports definidos em infrastructure/ports

### 2.2 Violacoes Domain -> Infrastructure/Application

- domain/tracks/factory.py:12,13
  - importa config/logging de infrastructure
- domain/geometry/skyfield_provider.py:8
  - importa GeometryProviderPort de infrastructure
- domain/satellite/factory.py:9
  - importa repository concreto de infrastructure
- domain/satellite/selector.py:8
  - importa modelo SatID do DB (infrastructure)
- domain/satellite/repositories.py:11
  - importa port de application
- domain/satellite/main.py:9
  - importa repository inexistente de infrastructure e mistura concerns de API
- domain/signal/factory.py:20
  - importa logging de infrastructure
- domain/skymap/factory.py:9 e domain/beam/services.py:8
  - importam logging de infrastructure

### 2.3 Interfaces acopladas a Infrastructure

- interfaces/__init__.py:9
  - exporta diretamente adapter PySM de infrastructure
- interfaces/cli/generate.py:9
  - faz wiring direto com provider concreto (esperavel em composition, mas reforca acoplamento de API)

## 3. Modulos mais acoplados

### 3.1 Maior acoplamento de saida (outgoing)

| Modulo | Dependencias internas distintas |
|---|---:|
| application/services/sim_orchestrator.py | 16 |
| application/services/simulation_service.py | 12 |
| infrastructure/db/satellite/satelliterepository.py | 6 |
| main.py | 5 |
| domain/simulation/simulation.py | 5 |

Leitura:
- sim_orchestrator e simulation_service concentram orchestration + wiring de infraestrutura.
- satelliterepository concentra persistencia, curadoria e ingestao externa no mesmo modulo.

### 3.2 Modulos mais dependidos (inbound por import)

| Modulo alvo | Numero de referencias |
|---|---:|
| domain/common | 15 |
| domain/beam/models | 13 |
| infrastructure/logging_config | 10 |
| domain/skymap | 9 |
| domain/satellite/models | 9 |
| infrastructure/config/config_loader | 7 |
| infrastructure/db/satellite/models | 7 |

Leitura:
- domain/common e um hub grande e com risco de tornar-se modulo "god/common".
- logging/config de infrastructure estao muito difundidos, inclusive em domain.

## 4. Dependencias com indicio de duplicacao arquitetural

### 4.1 Dois caminhos para loaders de beam

- infrastructure/files/csv_loader.py e infrastructure/beams/loaders/csv.py
- infrastructure/files/lit_loader.py e infrastructure/beams/loaders/lit.py
- infrastructure/files/custom_loader.py e infrastructure/beams/loaders/custom.py

Efeito:
- sobreposicao de responsabilidade e comportamento divergente para mesma finalidade.

### 4.2 Dois namespaces de beam

- radioskysims/beam/* (compat legado)
- domain/beam/* (modelo de dominio atual)

Efeito:
- API publica ambigua (dois tipos Beam com contratos distintos).

## 5. Sintese de risco de dependencias

Risco alto:
- acoplamento de application/domain a infraestrutura concreta.
- modulo domain com responsabilidade de interface web.

Risco medio:
- duplicacao de adapters e namespaces de beam.
- interfaces expondo componentes de infraestrutura no __init__.

Risco operacional imediato:
- erro de sintaxe em application/tod_panel.py (indentacao) interrompe compileall do pacote.
