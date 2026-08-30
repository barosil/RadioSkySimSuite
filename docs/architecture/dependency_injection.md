# Dependency Injection - Sprint 2.4

Data: 2026-07-16
Escopo: consolidar Composition Root + DI sem alterar comportamento funcional.

Status do documento: **snapshot histórico da Sprint 2.4**.
Revalidação mais recente: **2026-08-05** (cotejamento docs × código).

## 1. Objetivo

Centralizar criacao concreta de dependencias no bootstrap e manter Application dependente apenas de Domain e Application Ports.

## 2. Fluxo arquitetural consolidado

```text
Interfaces
  -> Bootstrap
    -> Application
      -> Domain
        -> Ports
          -> Infrastructure
```

Observacao:
- Os Ports pertencem a Application e definem contratos.
- A Infrastructure implementa esses contratos.
- O bootstrap conecta implementacoes concretas aos contratos.

## 3. Fluxo de criacao das dependencias

```text
create_sim_orchestrator()
  -> create_simulation_context()
    -> build_simulation_context_dependencies()
      -> build_configuration()
      -> build_logging()
      -> build_database()
      -> build_repositories()
      -> build_domain_components()
      -> build_services()
      -> build_local_sources_service()
```

## 4. Estado before/after (snapshot da sprint)

Before (baseline da auditoria Sprint 2.3):
- 11 imports diretos de Infrastructure dentro de Application.
- Arquivos impactados: simulation_service.py, sim_orchestrator.py, satellite_service.py.

After:
- reducao relevante de imports diretos de Infrastructure dentro de
  src/radioskysims/application (na sprint).

## 4.1 Revalidação 2026-08-05 (delta pós-sprint)

No estado atual do código, **ainda existem imports diretos** de
`radioskysims.infrastructure` dentro de `application`:

- `application/services/catalog_services.py`
- `application/services/sim_orchestrator.py`
- `application/services/simulation_service.py`

Leitura correta para governança arquitetural:
- a Sprint 2.4 consolidou DI/Composition Root e reduziu acoplamentos;
- o objetivo de “zero imports diretos” ainda está **parcialmente pendente**.

## 5. Mudancas aplicadas

1. satellite_service.py
- Logger concreto removido da Infrastructure.
- Logger passou a ser dependencia injetavel no construtor.
- Fallback local no-op para preservar compatibilidade de API sem construcao concreta.

2. simulation_service.py
- Removidos imports concretos de config loader, beam loader e logger da Infrastructure.
- Adicionadas dependencias injetaveis:
  - telescope_loader
  - beam_loader_factory
  - logger
- Fluxos run_by_*_from_settings preservados, agora via dependencias recebidas no construtor.

3. sim_orchestrator.py
- Removida criacao concreta de LocalSourcesService e adapters de Infrastructure.
- LocalSourcesService passou a ser recebido via SimulationContext.
- default_constellations passou a usar config_loader injetado no context.
- Tipagens de repositorio/DB substituidas para evitar acoplamento a classes concretas de Infrastructure.

4. bootstrap/builders.py
- Consolidado wiring em builders por responsabilidade unica:
  - build_configuration
  - build_logging
  - build_database
  - build_repositories
  - build_domain_components
  - build_services
  - build_local_sources_service
- Adicionada via oficial de criacao de casos de uso RadioSources:
  - build_radiosources_use_cases
- build_simulation_context_dependencies preservado como orquestrador unico.

5. infrastructure/ports
- Wrappers padronizados para reexport puro de application.ports.*.

## 6. Regras reforcadas

- Application nao pode importar radioskysims.infrastructure.*.
- Bootstrap e o unico local autorizado para montagem de objetos concretos.
- Ports continuam de ownership da Application (Sprint 2.2).

## 7. Validacao executada

- compileall em src/radioskysims: OK
- import smoke de pacotes principais: OK
- test_port_contracts.py: OK
- test_sim_orchestrator_local_sources.py: OK

Observacao de ambiente:
- Em revalidação posterior (2026-08-05), a coleta ampla na raiz encontrou
  erro de permissão em `data/DB/conftest.py` (ambiente/volume), sem relação
  direta com o refactor de DI.
