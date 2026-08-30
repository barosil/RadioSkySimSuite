# Regras Arquiteturais da Fase 2 - RadioSkySim

Data: 2026-07-16
Escopo: Fase 2 (Estabilizacao Arquitetural)
Objetivo: preservar comportamento funcional enquanto reduz risco arquitetural.

## 1. Regras gerais da Fase 2

1. Nao alterar regras de negocio, modelos fisicos ou APIs publicas sem RFC explicita.
2. Mudancas devem ser de baixo risco e reversiveis.
3. Priorizar estabilizacao de fronteiras entre camadas antes de grandes refatoracoes.
4. Todo ajuste estrutural deve manter compatibilidade com o estado atual do projeto.

## 2. Responsabilidades por camada

### Domain
- Conter entidades, value objects, regras de negocio e servicos de dominio.
- Nao conter wiring de infraestrutura, IO externo, framework web/UI ou bootstrap de aplicacao.

### Application
- Orquestrar casos de uso e coordenar fluxo entre Domain e Ports.
- Depender de contratos (Ports), nunca de adapters concretos.

### Infrastructure
- Implementar adapters concretos para DB, arquivos, rede, telemetria e provedores externos.
- Nao conter regra de negocio central de dominio.

### Interfaces
- Expor CLI, GUI e API.
- Concentrar composition root e wiring de dependencias concretas para casos de uso.

## 3. Dependencias permitidas entre camadas

Matriz alvo para a Fase 2:

| Origem | Dependencias permitidas |
|---|---|
| Domain | Domain |
| Application | Domain, Application |
| Infrastructure | Domain, Application, Infrastructure |
| Interfaces | Application, Domain, Infrastructure, Interfaces |

Regras obrigatorias:
1. Domain nao deve depender de Application, Infrastructure ou Interfaces.
2. Application nao deve depender de implementacoes concretas de Infrastructure.
3. Interfaces podem fazer wiring, mas devem evitar espalhar adapters concretos em re-exports de pacote.
4. Infrastructure nunca deve ser importada diretamente pela Application.

## 4. Ports e Adapters

1. Ports devem representar contratos estaveis para casos de uso.
2. Application e proprietaria dos Ports (application/ports).
3. Infrastructure implementa Ports e nao e proprietaria dos contratos.
4. Domain nunca deve depender de Ports definidos em Infrastructure.
5. Ports representam contratos estaveis de casos de uso e devem ser versionados com cuidado.
6. Adapters concretos devem implementar esses contratos sem vazar detalhes para Domain.
7. Mudancas de assinatura em ports exigem validacao de impacto em todos os adapters.
8. Wrappers de compatibilidade legado sao permitidos, desde que documentados com status e plano de deprecacao.

## 5. Composition Root

Definicao:
- Composition root e o ponto unico onde objetos concretos sao montados e injetados.

Regras:
1. Bootstrap e o unico Composition Root oficial do projeto.
2. Wiring de infraestrutura deve ocorrer em Interfaces ou scripts de bootstrap.
3. Domain e Application nao devem criar diretamente dependencias concretas.
4. Application nunca instancia adapters concretos.
5. Toda criacao concreta ocorre no Bootstrap.
6. Cada fluxo oficial (CLI, GUI, API) deve apontar para composition root documentado.

## 6. Regras de qualidade minima para Fase 2

1. O pacote deve compilar integralmente com compileall.
2. Importacao basica deve funcionar para:
   - radioskysims
   - radioskysims.domain
   - radioskysims.application
   - radioskysims.infrastructure
   - radioskysims.interfaces
3. CI deve validar compileall e import smoke em toda execucao de push/PR.

## 7. Controle de mudancas

1. Alteracoes de arquitetura devem atualizar os documentos em docs/architecture.
2. Toda excecao temporaria de regra deve ser registrada com justificativa, risco e prazo de remocao.
3. Refatoracoes grandes devem seguir o roadmap faseado e priorizar baixo risco primeiro.
