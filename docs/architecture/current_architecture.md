# Auditoria Arquitetural Atual - RadioSkySim

Data da auditoria: 2026-07-16
Escopo analisado: src/radioskysims (185 arquivos Python)
Metodo: analise estatica de imports (AST), leitura de modulos criticos e validacao de compilacao Python.

Status do documento: **baseline historica** (2026-07-16).
Revalidacao mais recente: **2026-08-05**.

## Revalidacao 2026-08-05 (delta)

O projeto manteve a direcao arquitetural, mas com pendencias residuais de
acoplamento entre camadas. No estado atual:

- `application -> infrastructure`: **6** imports internos.
- `domain -> infrastructure`: **4** imports internos.
- `domain -> application`: **3** imports internos.
- `interfaces -> infrastructure`: **2** imports internos.
- `infrastructure -> application`: **12** imports internos
   (majoritariamente wrappers/compat em `infrastructure/ports/*`).

Exemplos confirmados (2026-08-05):
- `application/services/catalog_services.py`
- `application/services/sim_orchestrator.py`
- `application/services/simulation_service.py`
- `domain/geometry/interface.py`
- `domain/geometry/skyfield_provider.py`
- `domain/simulation/simulation.py`

Itens resolvidos em relacao ao texto original:
- `domain/satellite/main.py` nao existe na base atual.
- varredura sintatica em `src/radioskysims` sem erros de compilacao.

Leitura recomendada:
- usar este documento como foto historica + delta acima;
- para planejamento corrente, priorizar `docs/relatorio_ago_2026.md` e
   `docs/relatorio_ago_2026_diff_docs_vs_code.md`.

## 1. Visao geral da arquitetura atual

O projeto declara arquitetura Hexagonal e possui pacotes explicitos para:
- domain
- application
- infrastructure
- interfaces
- common (materializado principalmente em domain/common)

Na pratica, a estrutura de diretorios existe, mas ha vazamentos entre camadas e mistura de responsabilidades em pontos centrais:
- domain depende de infrastructure e ate de application em alguns modulos.
- application importa infraestrutura concreta diretamente em casos de uso/servicos.
- interfaces contem wiring de infraestrutura no nivel de pacote.
- existem caminhos legados paralelos (ex.: radioskysims/beam e domain/beam) com sobreposicao funcional.

Resumo quantitativo de dependencias internas por camada (imports internos):
- application -> infrastructure: 13
- domain -> infrastructure: 9
- domain -> application: 1
- interfaces -> infrastructure: 2
- infrastructure -> domain: 45 (esperado em ports/adapters)
- infrastructure -> application: 4 (nao esperado na maioria dos casos)

## 2. Diagrama textual das camadas

Estado alvo de uma arquitetura em camadas/hexagonal:

```text
interfaces -> application -> domain
infrastructure -> application (via ports) e domain (implementacoes)
domain sem dependencia de application/infrastructure/interfaces
```

Estado observado no codigo:

```text
interfaces --> application
interfaces --> infrastructure            [ocorre]

application --> domain                   [ocorre]
application --> infrastructure           [ocorre em servicos-chave]

domain --> domain                        [ocorre]
domain --> infrastructure                [ocorre em modulos centrais]
domain --> application                   [ocorre]

infrastructure --> domain                [ocorre, esperado]
infrastructure --> application           [ocorre em parte]
```

## 3. Fluxo principal atual do sistema

Fluxo principal identificado (pipeline de simulacao):
1. Entrada por orchestrator em application:
   - application/services/sim_orchestrator.py
2. Carregamento de configuracao e construcao de dependencias concretas:
   - infrastructure/config/config_loader.py
   - infrastructure/db/*
   - infrastructure/external/*
3. Orquestracao de simulacao:
   - application/services/simulation_service.py
4. Execucao de regras e modelos de dominio:
   - domain/simulation/simulation.py
   - domain/satellite/*
   - domain/signal/*
   - domain/tod/*
5. Persistencia e IO em infraestrutura:
   - infrastructure/db/*
   - infrastructure/beams/loaders/*
   - infrastructure/skymap/*

### Observacao critica

O passo 2 ocorre dentro da camada application (sim_orchestrator), nao no composition root de interfaces/app bootstrap. Isso reduz testabilidade e aumenta acoplamento direto entre caso de uso e infraestrutura concreta.

## 4. Estado de separacao por camada

### Domain
Pontos positivos:
- boa concentracao de entidades/value objects em varios subdominios.

Problemas estruturais:
- imports para infrastructure em modulos de dominio (logging, config, modelos DB).
- um modulo de dominio atuando como app web (domain/satellite/main.py com FastAPI).
- dependencia de domain para application (domain/satellite/repositories.py).

### Application
Pontos positivos:
- servicos de orquestracao de casos de uso estao presentes.

Problemas estruturais:
- imports diretos de repositories, loaders e config de infrastructure.
- parte dos ports de aplicacao esta fora da camada application (ports em infrastructure/ports).

### Infrastructure
Pontos positivos:
- ampla cobertura de adapters para DB, arquivos e provedores externos.

Problemas estruturais:
- coexistencia de adapters com sobreposicao (files/* e beams/loaders/*).
- em alguns pontos depende de contratos definidos fora da camada application.

### Interfaces
Pontos positivos:
- separacao de API/CLI/GUI por subpacotes.

Problemas estruturais:
- pacote interfaces exporta adapter de infrastructure no __init__.
- controller API usa contrato de servico diferente do servico real disponivel.

### Shared/Common
- Nao existe um pacote shared/common transversal independente.
- O papel de comum esta concentrado em domain/common, mas com escopo muito amplo (modelos fisicos, utilitarios e lazy imports), indicando baixa coesao.

## 5. Principais conclusoes

1. A separacao de camadas esta parcialmente presente no layout, mas nao esta aplicada de forma consistente nas dependencias reais.
2. O maior risco arquitetural esta nos cruzamentos domain/application com infrastructure concreta.
3. Existe divida de evolucao (camadas legadas coexistindo) que impacta clareza de API publica e manutencao.
4. O sistema tem um fluxo principal funcional, porem com composicao de dependencias em local inadequado (application em vez de composition root dedicado).
