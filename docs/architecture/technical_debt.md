# Divida Tecnica Arquitetural - RadioSkySim

Data da auditoria: 2026-07-16
Escopo: src/radioskysims

Status do documento: **baseline histórica da auditoria de 2026-07-16**.
Revalidação complementar: **2026-08-05**.

## Revalidação 2026-08-05 (delta sobre a baseline)

Esta seção atualiza apenas o que mudou com evidência direta no código;
o inventário original abaixo é mantido para rastreabilidade histórica.

### Itens reclassificados

- **TD-004 (domain/satellite/main.py com FastAPI)**
  - Status atual: **resolvido**.
  - Evidência: `src/radioskysims/domain/satellite/main.py` não existe no estado atual.

- **TD-007 (IndentationError em application/tod_panel.py)**
  - Status atual: **resolvido**.
  - Evidência: varredura sintática (AST parse) em `src/radioskysims` sem erros.

- **TD-008 (duplicação infrastructure/files vs infrastructure/beams/loaders)**
  - Status atual: **revalidar escopo**.
  - Evidência: não há `src/radioskysims/infrastructure/files/**/*.py`; caminho
    observado atualmente é `infrastructure/beams/loaders/*`.

### Itens que permanecem em aberto (confirmados)

- **TD-001**: ainda há imports `application -> infrastructure`.
- **TD-003**: ainda há dependências `domain -> application`.
- **TD-011/TD-012**: módulos grandes e baixa coesão continuam relevantes.

### Ação recomendada para governança

Adicionar status por item (`ativo`, `resolvido`, `revalidar`) com data da última
checagem para evitar backlog “zumbi”.

## Classificacao de impacto
- Critico: quebra de execucao, risco alto de regressao, bloqueia evolucao arquitetural.
- Alto: degrada testabilidade/evolucao, aumenta custo de manutencao.
- Medio: inconsistencia e complexidade local relevante.
- Baixo: melhoria de higiene arquitetural.

## Lista completa de divida tecnica

### TD-001 - Violacao de camada em Application (imports diretos de Infrastructure)
- Evidencia:
  - application/services/sim_orchestrator.py:21,25,26,29,30,31,34
  - application/services/simulation_service.py:23,24,27
  - application/radiosources_use_cases.py:27
  - application/services/local_sources_service.py:22
- Causa:
  - ausencia de composition root claro e ports definidos no lugar correto.
- Impacto:
  - baixa testabilidade, dificuldade de mock/substituicao de adapters.
- Risco:
  - alto risco de regressao ao trocar infraestrutura.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - mover contratos para application/ports e injetar adapters no bootstrap.

### TD-002 - Violacao de camada em Domain (dependencia de Infrastructure)
- Evidencia:
  - domain/tracks/factory.py:12,13
  - domain/geometry/skyfield_provider.py:8
  - domain/satellite/factory.py:9
  - domain/satellite/selector.py:8
  - domain/signal/factory.py:20
  - domain/skymap/factory.py:9
  - domain/beam/services.py:8
- Causa:
  - fronteiras de dominio e infraestrutura nao estabilizadas.
- Impacto:
  - dominio deixa de ser nucleo independente.
- Risco:
  - alto risco de acoplamento circular e dificuldade de reutilizacao.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - substituir tipos/servicos concretos por interfaces de dominio/application.

### TD-003 - Domain dependendo de Application
- Evidencia:
  - domain/satellite/repositories.py:11
- Causa:
  - compatibilidade retroativa implementada no lado errado da fronteira.
- Impacto:
  - inversao de dependencia arquitetural.
- Risco:
  - alto para manutencao de contratos e versionamento interno.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - mover alias de compatibilidade para application ou infrastructure adapters.

### TD-004 - Modulo de Domain com responsabilidade de Interface Web
- Evidencia:
  - domain/satellite/main.py usa FastAPI e tenta wiring de controller/repository.
- Causa:
  - codigo legado mantido em pacote de dominio.
- Impacto:
  - quebra de separacao de responsabilidade e confusao de ponto de entrada.
- Risco:
  - critico para evolucao e onboarding (modulo sugere arquitetura incorreta).
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - realocar/remover modulo; entrada web deve viver em interfaces/api.

### TD-005 - API publica inconsistente entre controller e service
- Evidencia:
  - interfaces/api/satellite_controller.py chama get_all_satellites/get_satellite_by_id/add/update/delete
  - application/services/satellite_service.py expoe get_all/get_by_ids/get_by_constellations/update_*
- Causa:
  - contratos de API e servico evoluiram de forma independente.
- Impacto:
  - risco de endpoint quebrado e manutencao duplicada.
- Risco:
  - critico em runtime da interface HTTP.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - definir DTO/contrato de facade de API unico e alinhar controller/service.

### TD-006 - Ponto de entrada principal inconsistente com APIs atuais
- Evidencia:
  - main.py instancia SatelliteFactory(repository=..., spacetrack_client=...) mas a factory atual nao aceita esse parametro.
- Causa:
  - drift entre codigo legado de bootstrap e implementacao corrente.
- Impacto:
  - ponto de entrada potencialmente nao executavel.
- Risco:
  - alto (falha imediata de runtime).
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - consolidar um unico composition root suportado e remover bootstrap obsoleto.

### TD-007 - Erro de sintaxe em modulo de Application
- Evidencia:
  - application/tod_panel.py (IndentationError na linha 36) detectado por compileall.
- Causa:
  - merge/edicao parcial com bloco corrompido.
- Impacto:
  - pacote nao compila integralmente.
- Risco:
  - critico para distribuicao e confiabilidade do build.
- Prioridade:
  - Critica.
- Recomendacao de refatoracao:
  - corrigir integridade sintatica e cobrir com teste de import/compile.

### TD-008 - Duplicacao de adapters de Beam Loader
- Evidencia:
  - infrastructure/files/* e infrastructure/beams/loaders/* implementam CSV/LIT/Custom com sobreposicao.
- Causa:
  - migracao incompleta entre estruturas de infraestrutura.
- Impacto:
  - manutencao dobrada, comportamento divergente, ambiguidade de uso.
- Risco:
  - alto para bugs silenciosos por caminho de import.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - eleger um caminho canonico e manter wrappers minimos para legado.

### TD-009 - Duplicacao de API Beam (namespace legado vs dominio)
- Evidencia:
  - radioskysims/beam/models.py define Beam legado
  - domain/beam/models.py define Beam de dominio com contrato diferente
- Causa:
  - compatibilidade legado sem fronteira explicita de deprecacao.
- Impacto:
  - API publica inconsistente e potencial erro de tipo em runtime.
- Risco:
  - alto em integracoes e testes.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - padronizar Beam canonico e manter alias apenas de migracao controlada.

### TD-010 - Ports de aplicacao alocados na camada Infrastructure
- Evidencia:
  - infrastructure/ports/radiosources.py
  - infrastructure/ports/localsources.py
  - usage direto em application/*
- Causa:
  - modelagem de ports invertida por contexto.
- Impacto:
  - enfraquece DIP e torna application dependente de infraestrutura.
- Risco:
  - alto para extensibilidade.
- Prioridade:
  - Alta.
- Recomendacao de refatoracao:
  - mover contratos para application/ports e deixar em infrastructure apenas adapters.

### TD-011 - Modulos excessivamente grandes e multifuncionais
- Evidencia:
  - infrastructure/db/satellite/satelliterepository.py (~774 linhas)
  - domain/common/models.py (~635 linhas)
  - application/services/simulation_service.py (~599 linhas)
  - application/services/sim_orchestrator.py (~465 linhas)
- Causa:
  - acumulacao de responsabilidades sem fatiamento por subdominio/caso de uso.
- Impacto:
  - baixa legibilidade, alto custo de mudanca, baixa coesao.
- Risco:
  - medio-alto para regressao.
- Prioridade:
  - Media-Alta.
- Recomendacao de refatoracao:
  - extrair servicos/objetos menores por responsabilidade.

### TD-012 - Baixa coesao em domain/common
- Evidencia:
  - domain/common/models.py concentra ranges, observer/time, lazy imports e utilitarios diversos.
- Causa:
  - modulo comum tornou-se agregador generico.
- Impacto:
  - acoplamento elevado; modulo vira ponto unico de impacto.
- Risco:
  - medio.
- Prioridade:
  - Media.
- Recomendacao de refatoracao:
  - quebrar em submodulos orientados a conceito (time, frequency, angles, observer).

### TD-013 - Inconsistencia de API publica em __init__ de interfaces
- Evidencia:
  - interfaces/__init__.py exporta diretamente PySMSkyMapGeneratorAdapter (infraestrutura).
- Causa:
  - re-export de adapter concreto no nivel de pacote de interface.
- Impacto:
  - acoplamento de import path publico a implementacao concreta.
- Risco:
  - medio.
- Prioridade:
  - Media.
- Recomendacao de refatoracao:
  - expor apenas contratos/facades de interface, nao adapters concretos.

### TD-014 - Artefatos de codigo legado/obsoleto coexistindo com caminho atual
- Evidencia:
  - domain/satellite/main.py referencia modulos inexistentes (satellite_controller/service no domain, infrastructure/satellite_repository.py)
  - coexistencia de wrappers e aliases de compatibilidade sem politica unica.
- Causa:
  - limpeza incompleta apos refactors anteriores.
- Impacto:
  - confusao no fluxo principal e aumento de custo cognitivo.
- Risco:
  - medio.
- Prioridade:
  - Media.
- Recomendacao de refatoracao:
  - marcar deprecado, remover dead paths e documentar trilha canonica.

## Resumo por impacto
- Critico: TD-005, TD-007
- Alto: TD-001, TD-002, TD-003, TD-004, TD-006, TD-008, TD-009, TD-010
- Medio/Medio-Alto: TD-011, TD-012, TD-013, TD-014
