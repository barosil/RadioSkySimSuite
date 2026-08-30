# Application Ports - RadioSkySim (Sprint 2.2)

Data: 2026-07-16
Escopo: reorganizacao arquitetural de baixo risco na Fase 2.

## 1. Objetivo dos Ports

Application Ports definem contratos estaveis para os casos de uso da camada Application.
Esses contratos descrevem o que a aplicacao precisa de IO/persistencia/integracoes,
sem acoplar os casos de uso a implementacoes concretas.

Nesta sprint, os contratos foram movidos para Application, preservando compatibilidade
com caminhos antigos via wrappers em Infrastructure.

## 2. Responsabilidade da camada Application

A camada Application passa a ser proprietaria de seus Ports.
Isso significa:
- contratos usados pelos casos de uso vivem em application/ports;
- casos de uso importam contratos de application/ports;
- Application descreve necessidades, mas nao implementa infraestrutura concreta.

## 3. Diferenca entre Port e Adapter

- Port:
  - interface/contrato estavel;
  - orientado a caso de uso;
  - sem detalhes de framework/DB/rede.

- Adapter:
  - implementacao concreta de um Port;
  - vive em Infrastructure;
  - pode usar DB, arquivos, APIs externas, libs especificas.

## 4. Fluxo correto de dependencias

Fluxo desejado (Fase 2):

```text
Interfaces/Bootstrap -> Application (use cases) -> Application Ports
Infrastructure (adapters) ----------------------> Application Ports
Domain sem dependencia de adapters concretos
```

Reforco:
- Application nao deve depender de infrastructure.ports.
- Infrastructure implementa contratos definidos por Application.

## 5. Politica de compatibilidade temporaria

Para evitar quebra de import legado:
- modulos em infrastructure/ports permanecem disponiveis;
- esses modulos atuam como wrappers de compatibilidade;
- wrappers reexportam simbolos de application/ports;
- nesta sprint nao ha DeprecationWarning em runtime.

Exemplo de wrapper:
- infrastructure/ports/radiosources.py -> from radioskysims.application.ports.radiosources import *

## 6. Estrategia de migracao para proximas sprints

1. Sprint 2.2 (esta sprint):
- mover contratos para application/ports;
- manter wrappers em infrastructure/ports;
- atualizar imports da camada Application.

2. Sprint seguinte (planejada):
- ajustar gradualmente adapters de Infrastructure para importar diretamente application/ports;
- ampliar verificacoes arquiteturais automatizadas.

3. Sprint de consolidacao:
- descontinuar wrappers de compatibility com plano de remocao controlado;
- manter apenas caminho canonico em application/ports.

## 7. Ports migrados nesta sprint

- radiosources
- localsources
- beam
- geometry
- skymap

Todos preservando nomes, assinaturas e semantica original dos contratos.
