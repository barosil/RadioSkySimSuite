> **Documento histórico** — auditoria com ``as-of: 2026-07-16``.
> Superado pelo plano faseado em `docs/decoupling/` (ver `docs/architecture.md`).

# Roadmap de Refatoracao Arquitetural - RadioSkySim

Data da auditoria: 2026-07-16
Objetivo: reduzir risco primeiro, preservar comportamento e empurrar mudancas estruturais maiores para o final.

## Principios do plano
- Baixo risco primeiro.
- Mudancas comportamentais minimas nas fases iniciais.
- Compatibilidade retroativa temporaria com deprecacao explicita.
- Gates por testes e validacoes arquiteturais em cada fase.

## Fase 0 - Contencao imediata (baixo risco, alto retorno)

Objetivo:
- remover bloqueios de build/execucao e alinhar pontos de entrada mais quebrados.

Acoes:
1. Corrigir integridade sintatica de application/tod_panel.py.
2. Definir oficialmente o ponto de entrada suportado (CLI/API/GUI), marcando outros como legados.
3. Adicionar cheque automatizado de compilacao do pacote no CI (compileall ou equivalente).

Risco:
- baixo.

Criterio de saida:
- pacote compila integralmente; entrypoint oficial documentado.

## Fase 1 - Higiene de API publica (baixo risco)

Objetivo:
- reduzir ambiguidades de uso sem alterar motor de dominio.

Acoes:
1. Alinhar interfaces/api/satellite_controller.py com contrato real de SatelliteService.
2. Remover/exportar com cuidado o re-export de adapter concreto em interfaces/__init__.py.
3. Documentar APIs legadas beam e definir status (supported/deprecated).

Risco:
- baixo a medio.

Criterio de saida:
- API HTTP e servicos com contrato consistente; import paths publicos estabilizados.

## Fase 2 - Ports e injecao de dependencias (medio risco, alto valor)

Objetivo:
- restaurar separacao entre application e infrastructure.

Acoes:
1. Mover ports de radiosources/localsources para application/ports.
2. Ajustar application/services para depender somente de ports.
3. Introduzir composition root explicito em interfaces (wiring de adapters concretos).

Risco:
- medio.

Criterio de saida:
- nenhum import de infrastructure dentro de application (exceto composition root).

## Fase 3 - Blindagem do dominio (medio-alto)

Objetivo:
- tornar domain independente de application/infrastructure.

Acoes:
1. Remover imports de infrastructure em domain/* (logging/config/modelos DB).
2. Substituir tipos de infraestrutura (ex.: SatID) por tipos de dominio/DTOs internos.
3. Mover/remover domain/satellite/main.py para camada correta de interfaces.
4. Eliminar dependencia domain -> application (alias de repositories).

Risco:
- medio-alto.

Criterio de saida:
- domain sem dependencias para application, infrastructure e interfaces.

## Fase 4 - Consolidacao de adapters e modulos duplicados (alto risco controlado)

Objetivo:
- reduzir custo de manutencao e ambiguidade arquitetural.

Acoes:
1. Unificar loaders de beam em um unico pacote canonico.
2. Manter wrappers temporarios para legado com avisos de deprecacao.
3. Consolidar namespace Beam (dominio como fonte de verdade).

Risco:
- alto (pode afetar integracoes existentes).

Criterio de saida:
- um unico caminho canonico para Beam e loaders; wrappers mapeados e testados.

## Fase 5 - Fatiamento de modulos grandes e coesao (alto risco, por ultimo)

Objetivo:
- atacar divida estrutural profunda apos estabilizacao de fronteiras.

Acoes:
1. Dividir infrastructure/db/satellite/satelliterepository.py por responsabilidade:
   - query/read
   - curadoria/sincronizacao
   - associacao de sinais
2. Dividir application/services/simulation_service.py em use cases menores.
3. Dividir domain/common/models.py em submodulos coesos.

Risco:
- alto.

Criterio de saida:
- reducao de tamanho/ciclomaticidade por modulo e maior coesao por pacote.

## Ordem recomendada (resumo)
1. Fase 0
2. Fase 1
3. Fase 2
4. Fase 3
5. Fase 4
6. Fase 5

## Indicadores de progresso
- KPI-1: quantidade de violacoes de camada (AST import rules) ate zerar domain->infrastructure/application.
- KPI-2: quantidade de modulos com >300 linhas e >10 funcoes.
- KPI-3: quantidade de caminhos publicos duplicados para o mesmo conceito (beam/loaders).
- KPI-4: cobertura de testes dos casos de uso apos separacao de ports/adapters.
