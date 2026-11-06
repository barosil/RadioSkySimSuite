# Dependências entre Módulos e Camadas — RadioSkySimSuite

**Data da auditoria:** 2026-09-01
**Escopo:** `src/radioskysims` (umbrella) + 9 pacotes em `packages/*`
(submódulos git inicializados neste clone).
**Base:** varredura estática de imports internos (`grep` por
`from <pacote>.<camada>`) + inspeção manual dos hotspots.

> **Status do documento:** substitui integralmente a baseline de 2026-07-16 e
> a revalidação de 2026-08-05, que descreviam o **monólito pré-desacoplamento**
> (`src/radioskysims/domain|application|infrastructure`). Desde a Fase 7 do
> plano de desacoplamento, cada bounded context vive em seu próprio pacote
> (`packages/<nome>/src/<nome_import>/{domain,application,infrastructure,
> bootstrap}`), e o umbrella ficou reduzido a composition root + interfaces +
> visualização + resíduo legado.

## 1. Nova unidade de análise: dependências entre pacotes

A pergunta arquitetural relevante deixou de ser só "domain importa
infrastructure?" (ainda vale, ver §2) e passou a incluir "quem importa quem
entre pacotes?". Do `architecture.md` (grafo de `pyproject.toml`):

| Pacote | Depende de |
|---|---|
| `radioskysims-core` | — (kernel; não depende de domínios de rádio) |
| `radioskysims-viz` | — (kernel de visualização) |
| `radioskysims-beam` | `core`, `viz` |
| `radioskysims-skymap` | `core` |
| `radioskysims-radiotelescope` | `core`, `viz` |
| `radioskysims-sources` | `core`, `skymap` |
| `gnsstools4astro` | `core`, `skymap` |
| `radioskysims-simulation` | `core`, `viz`, `beam`, `skymap`, `sources`, `radiotelescope` |
| `radioskysims-waterfall` | (independente; consumido pelo umbrella) |
| `radioskysim` (umbrella) | todos os 9 pacotes |

Leitura: o grafo entre pacotes é **acíclico e coerente** com a hierarquia
kernel → domínios → orquestração → umbrella. Não há violação de dependência
circular entre pacotes. O risco de acoplamento hoje está **dentro** de cada
pacote, não entre eles — ver §2.

## 2. Violações de camada dentro de cada pacote

Contagem de arquivos com import direto entre camadas (varredura
`grep -rlE "from <pkg>\.(infrastructure|application)"`):

| Pacote | Domain → Infra/App | Application → Infra | Leitura |
|---|---:|---:|---|
| `radioskysims-simulation` | 1 arquivo | 1 arquivo | Concentrado nos dois maiores módulos do monorepo (ver abaixo). |
| `radioskysims-sources` | 2 arquivos | 3 arquivos | Maior número de violações; reflete acoplamento histórico de satélite/rádio-fonte com persistência. |
| `radioskysims-beam` | 1 arquivo | 0 | Violação pontual e antiga (loader analítico). |
| `radioskysims-core` | 2 arquivos | 0 | Ports definidos em `application.ports.geometry`, implementados por provider em `domain` — ver nota abaixo. |
| `radioskysims-waterfall` | 3 arquivos | 1 arquivo | Modelos de domínio (`models.py`, `sed.py`, `lightcurve.py`) com import de infraestrutura. |
| `radioskysims-skymap` | 0 | 0 | **Limpo.** Melhor pacote sob este critério. |
| `radioskysims-radiotelescope` | 0 | 0 | **Limpo.** Pacote pequeno (671 linhas) e coeso. |

### 2.1 Detalhe das violações

**`radioskysims-simulation`**
- `domain/simulation/simulation.py` — importa de `application`/`infrastructure`
  (entidade "gorda" que também compõe/orquestra, ver `relatorio_set_2026_v2.md §8.4`).
- `application/services/sim_orchestrator.py:53` — importa
  `infrastructure.processing.resource_processor.ResourceAwareProcessor`
  diretamente (esperado em orquestração, mas reforça o tamanho do módulo).

**`radioskysims-sources`**
- `domain/signal/factory.py`, `domain/satellite/selector.py:8` — o segundo
  importa `SatID` de `infrastructure.db.satellite.models` (modelo de
  persistência vazando para o domínio — mesmo padrão já apontado no
  documento histórico de 2026-07-16).
- `application/services/catalog_services.py:35`,
  `local_sources_manager.py`, `radio_sources_manager.py` — importam
  providers/adapters concretos de `infrastructure.external.*` diretamente nos
  serviços de aplicação.

**`radioskysims-beam`**
- `domain/beam/factory.py:23` — importa
  `infrastructure.beams.loaders.analytical` (loader concreto usado como
  fallback dentro da factory de domínio).

**`radioskysims-core`**
- `domain/geometry/interface.py:18` e `domain/geometry/skyfield_provider.py:7`
  — importam `GeometryProviderPort` de `application.ports.geometry`. Isso é
  uma inversão de dependência aceitável em alguns desenhos hexagonais (port
  definido em application, implementado por um provider "de domínio"), mas
  destoa da regra estrita "domain não depende de application" declarada em
  `architecture.md`. Recomenda-se mover `GeometryProviderPort` para
  `domain.geometry` (contrato) e deixar `application` apenas consumir.

**`radioskysims-waterfall`**
- `domain/models.py`, `domain/sed.py`, `domain/lightcurve.py` — importam de
  `infrastructure`; `application/services/pipeline.py` também importa
  infraestrutura diretamente. É o pacote com a violação proporcionalmente
  mais espalhada (3 de poucos módulos de domínio).

## 3. Pacotes sem violação de camada detectada

- `radioskysims-skymap` — ausência de import cruzado entre `domain` e
  `application`/`infrastructure` nesta varredura. Estrutura de referência
  para os demais pacotes.
- `radioskysims-radiotelescope` — mesmo resultado; também o menor pacote
  (671 linhas), o que facilita manter a disciplina.

## 4. Módulos com maior acoplamento de saída (imports internos distintos)

| Módulo | Pacote | Observação |
|---|---|---|
| `application/services/sim_orchestrator.py` | `radioskysims-simulation` | Maior módulo do monorepo (1.623 linhas); concentra wiring de satélite, local, rádio-fonte, galáxia e processor. |
| `domain/simulation/simulation.py` | `radioskysims-simulation` | Entidade + composição + summary no mesmo módulo (1.573 linhas). |
| `infrastructure/db/satellite/satelliterepository.py` | `radioskysims-sources` | Persistência + curadoria + ingestão externa (834 linhas). |
| `infrastructure/processing/resource_processor.py` | `radioskysims-simulation` | Núcleo do processamento resource-aware (1.235 linhas); coeso, mas grande. |
| `domain/common/models.py` | `radioskysims-core` | Hub de tipos comuns (`FrequencyRange`, `TimeRange`, `Observer`); 13+ pacotes/módulos dependem dele — risco de módulo "god" à medida que a suíte cresce. |

## 5. Resíduos do umbrella (`src/radioskysims`)

O umbrella ainda mantém pastas `domain/`, `application/`, `infrastructure/`
com conteúdo residual (não removido na Fase 7 por serem usados por
`interfaces`/`bootstrap` locais):

- `domain/map/models.py` — modelo legado de mapa, fora de escopo (`AGENTS.md`).
- `application/gain_panel.py`, `application/ports/__init__.py` — sobras de
  painel Panel antigo; `gain_panel.py` já era classificado como
  "Experimental" no `entrypoints.md` histórico.
- `infrastructure/ports/{skymap,geometry}.py`, `infrastructure/db/init_db.py`,
  `infrastructure/utils/lazy.py` — utilitários finos, sem violação relevante
  de camada detectada.

Esses resíduos são pequenos (1 + 96 + 123 linhas — ver
`relatorio_set_2026_v2.md §8.2`) e não representam risco arquitetural
comparável aos módulos canhão dos pacotes de domínio.

## 6. Síntese de risco

**Risco alto**
- `sim_orchestrator.py` / `simulation.py` (`radioskysims-simulation`):
  tamanho + violação de camada + maior densidade de casos de uso reais.
- `satelliterepository.py` (`radioskysims-sources`): persistência,
  curadoria e ingestão externa misturadas.

**Risco médio**
- Inversão de dependência de `GeometryProviderPort` (`radioskysims-core`):
  não é crítico, mas destoa da regra declarada e é fácil de corrigir
  (mover o contrato para `domain`).
- `domain/satellite/selector.py` importando modelo de infraestrutura
  (`radioskysims-sources`): mesmo padrão já sinalizado em 2026-07-16 e ainda
  presente após o desacoplamento.
- Módulos de domínio de `radioskysims-waterfall` acoplados a infraestrutura.

**Risco baixo**
- `radioskysims-beam`: violação pontual e isolada em `factory.py`.
- Resíduos do umbrella: pequenos, sem sinal de crescimento.

**Sem risco detectado**
- `radioskysims-skymap` e `radioskysims-radiotelescope`: nenhuma violação de
  camada encontrada nesta varredura.

## 7. Recomendações

1. Tratar `sim_orchestrator.py` e `simulation.py` como prioridade nº1 de
   refatoração (ver sprints em `relatorio_set_2026_v2.md §13`).
2. Mover `GeometryProviderPort` para `radioskysims_core.domain.geometry` e
   deixar `application.ports` apenas re-exportar, eliminando a inversão.
3. Extrair curadoria/ingestão de `satelliterepository.py` para um serviço de
   aplicação dedicado, deixando o repository só com CRUD/consulta.
4. Revisar `radioskysims_core.domain.common.models` como candidato a módulo
   "god": considerar particionar por sub-tema (`common.time`,
   `common.frequency`, `common.observer`) se continuar crescendo.
5. Usar `radioskysims-skymap` e `radioskysims-radiotelescope` como referência
   de estrutura ao revisar os demais pacotes.
