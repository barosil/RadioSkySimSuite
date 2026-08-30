> **Documento histórico** — snapshot da Fase 2 (``as-of: 2026-07-16``).
> Superado pelo plano faseado de desacoplamento em `docs/decoupling/` e pelo
> documento canônico `docs/architecture.md`.

# Arquitetura Alvo da Fase 2 - RadioSkySim

Data: 2026-07-16
Escopo: estabelecer base arquitetural para refatoracoes futuras sem alterar comportamento funcional atual.

Atualizacao Sprint 2.4 (2026-07-16): consolidacao de Composition Root + Dependency Injection.

## 1. Objetivo da arquitetura

O objetivo da Fase 2 e explicitar a montagem de dependencias em um Composition Root oficial, preservando:
- regras de negocio;
- modelos fisicos;
- APIs publicas;
- comportamento operacional dos fluxos existentes.

Esta fase prepara o terreno para futuras evolucoes de Ports, DI e limpeza arquitetural.
Com a Sprint 2.4, a direcao arquitetural de DI esta consolidada:
- Application depende de Domain e Application Ports.
- Criacao concreta de adapters de Infrastructure ficou centralizada no bootstrap.
- Builders do bootstrap foram organizados por responsabilidade unica.

## 2. Diagrama textual das camadas

```text
Interfaces -> Bootstrap -> Application -> Domain
                      \-> Infrastructure
Infrastructure -------> Application (via ports) / Domain (tipos de dominio)
```

Leitura:
- Interfaces disparam casos de uso.
- Bootstrap monta os objetos concretos.
- Application orquestra sem criar adapters concretos de Infrastructure.
- Domain concentra regras de negocio e modelos.
- Infrastructure fornece implementacoes concretas (DB, IO, providers).

## 3. Papel do Composition Root

O Composition Root:
1. centraliza a criacao de objetos concretos;
2. reduz wiring espalhado em entrypoints e servicos;
3. preserva assinaturas publicas atuais;
4. evita introduzir regras de negocio no bootstrap.

Pacote oficial:
- src/radioskysims/bootstrap/
  - __init__.py
  - builders.py
  - composition.py

## 4. Fluxo das dependencias

Fluxo atual apos a Sprint 2.4:
1. Interfaces/scripts chamam bootstrap.composition.
2. bootstrap.builders monta dependencias concretas:
  - build_configuration
  - build_logging
  - build_database
  - build_repositories
  - build_domain_components
  - build_services
  - build_local_sources_service
3. bootstrap.composition devolve objetos compostos (ex.: SimOrchestrator).
4. Application executa os casos de uso com as dependencias montadas.

## 5. Fluxo de inicializacao da aplicacao

Fluxo oficial (TOD viewer):
1. scripts/start_service.py chama create_sim_orchestrator(telescope="default").
2. create_sim_orchestrator usa create_simulation_context.
3. create_simulation_context usa builders para montar dependencias concretas.
4. SimOrchestrator.run() executa simulacao.
5. TODPanel recebe o resultado e a interface e servida por Panel.

## 6. Responsabilidades por camada

### Interfaces
- iniciar fluxos CLI/GUI/API;
- chamar o Composition Root para obter objetos montados;
- nao concentrar regra de negocio.

### Bootstrap
- montar e conectar dependencias concretas;
- manter wiring explicito e rastreavel;
- manter um unico caminho oficial de criacao para services e orquestradores;
- nao conter regra de negocio ou calculo fisico.

### Application
- orquestrar casos de uso;
- coordenar chamadas de dominio e ports;
- manter assinatura publica estavel nesta fase.

### Domain
- concentrar entidades, value objects e regras de negocio;
- permanecer independente de detalhes de inicializacao.

### Infrastructure
- prover implementacoes concretas de repositores, loaders e providers;
- manter comportamento tecnico atual sem mudancas funcionais nesta sprint.

## 7. Entrypoints oficiais

Com base em docs/architecture/entrypoints.md:
- scripts/start_service.py (oficial de execucao da aplicacao)
- src/radioskysims/infrastructure/db/init_db.py (utilitario oficial de setup de banco)
- scripts/check_docs.py (utilitario oficial de qualidade)

Nesta sprint, o composition root foi consolidado com builders especializados e sem duplicacao de wiring.
