# Auditoria de código e roadmap de dívida técnica — 2026-11-06

## 1. Escopo, método e limites

Esta revisão coteja a avaliação fornecida pelo usuário com o código disponível,
o workflow de CI e as auditorias anteriores. O meta-repositório foi examinado em
`3bb119e5ba5e42e059f4e660c9ea004fb0efbca0` (`main`), não na branch `dev`
citada nos relatórios de 5/11. Foram inspecionados exemplos de código e
contratos, não todas as linhas de todos os pacotes. As constatações abaixo não
são uma certificação de correção científica ou de ausência de outros problemas.

Tentou-se obter os nove gitlinks com `git submodule update --init`; os seis
primeiros da tabela abaixo puderam ser examinados nos commits fixados. Para
beam, core e skymap, o servidor respondeu `upload-pack: not our ref` aos
fetches diretos dos commits fixados. Foram examinados os HEADs de `main`
clonados no momento da auditoria, **não** os commits registrados; não é possível
concluir que os gitlinks sejam irrecuperáveis de todos os remotos ou backups.

| Submódulo | Gitlink fixado | HEAD inspecionado | Relação |
|---|---|---|---|
| gnsstools4astro | `06bc929` | `06bc929` | coincide |
| radioskysims-radiotelescope | `18d2a5b` | `18d2a5b` | coincide |
| radioskysims-simulation | `a362921` | `a362921` | coincide |
| radioskysims-sources | `5f3b99a` | `5f3b99a` | coincide |
| radioskysims-viz | `4246724` | `4246724` | coincide |
| radioskysims-waterfall | `3d01d7e` | `3d01d7e` | coincide |
| radioskysims-beam | `50b3f08` | `a9341d5` | divergente; gitlink indisponível no fetch |
| radioskysims-core | `c73431e` | `fbec29a` | divergente; gitlink indisponível no fetch |
| radioskysims-skymap | `656905d` | `52e60e2` | divergente; gitlink indisponível no fetch |

Método: leitura direcionada de código, manifests, CI e documentos; buscas
estáticas por imports e funções de teste; `wc -l` para tamanho de módulos. A
busca não prova ausência de imports dinâmicos ou relativos e não constitui
verificação completa de dependências. Não foram executados pytest, Ruff,
mypy, benchmarks ou build: o ambiente não tinha `.venv` nem pytest, Ruff,
xarray ou Dask instalados, e o snapshot fixado está incompleto. Resultados
históricos de outras execuções são identificados como tais.

## 2. Cotejo da avaliação

| Afirmação | Resultado e qualificação |
|---|---|
| Boa base modular, com dívida técnica e relatórios divergentes | **Confirmado por amostragem.** Há ports, adapters e composição, mas também acoplamentos e inconsistências documentais detalhados adiante. Qualidade global não foi medida. |
| Dask/xarray e controle de recursos favorecem escala | **Confirmado como desenho, não como garantia de desempenho.** `simulation/application/ports/processing.py`, `simulation/infrastructure/processing/resource_processor.py` e a auditoria TOD mostram caminhos e medições específicos. O fluxo medido pode ser eager e um experimento full-lazy foi pior; Dask por si só não comprova escalabilidade. |
| Orquestradores extensos prejudicam manutenção/SRP | **Confirmado como risco.** `sim_orchestrator.py` tem 1.745 linhas e `domain/simulation/simulation.py` 1.551, incluindo comentários e código desativado. Tamanho não mede complexidade isoladamente; o primeiro reúne composição, processador, fontes, mapas, persistência e execução. |
| Escalabilidade de ponta a ponta ainda não comprovada | **Compatível com as evidências consultadas.** Os experimentos publicados não demonstram todos os fluxos/cargas. Não foi reproduzido aqui um cenário completo de 24 h. |
| Features abrangentes para single dish | **Escopo declarado e parcialmente corroborado**, por README, código e auditorias temáticas de mapas, TOD e HI. A existência de implementações/testes não implica que todos os fluxos sejam executáveis ou cientificamente validados neste snapshot. |
| Há Repository, Factory, providers e composition root | **Confirmado por exemplos:** `simulation/application/ports/mapmaking.py`, `mapmaking_repository.py`, `simulation/bootstrap/builders.py` e `simulation/bootstrap/composition.py`. São sinais de DDD/hexagonal, não prova de aderência integral. |
| Application importa infraestrutura; domain importa application | **Confirmado nos exemplos da seção 3**, inclusive imports locais e facades de compatibilidade. Beam e core são apenas HEADs substitutos. O rótulo “adapter” sob `application` não elimina a inversão quando importado pelo domínio. |
| Liskov e Interface Segregation não foram avaliados integralmente | **Confirmado.** Não foram realizados testes sistemáticos de substituibilidade nem revisão de todos os contratos e consumidores. |
| Aproximadamente 1.740 funções `test_*` | **Compatível com esta amostra mista: 1.746 declarações** (253 em `tests/`; 65 GNSS, 56 beam, 117 core, 14 radiotelescope, 308 simulation, 278 skymap, 472 sources, 49 viz, 134 waterfall). Contagem por `rg '^\s*(async\s+)?def test_'` em `tests/` e `packages/*/tests/`, arquivos `*.py`; não é coleta do pytest, número de casos parametrizados, cobertura ou resultado de execução. Os três HEADs substitutos tornam o número não representativo do snapshot fixado. |
| CI principal executa meta e core, não todos os pacotes | **Confirmado para `.github/workflows/ci.yml`**: checkout recursivo, `uv sync`, Ruff, `pytest tests/` e `pytest packages/radioskysims-core/tests`; nenhum passo explícito para os outros oito pacotes. Não foram auditadas as CIs próprias dos submódulos. |
| README e métricas divergem; três HEADs diferem | **Confirmado para este checkout.** O README lista, por exemplo, `src/radioskysims/domain/beam/` e `docker/postgresql/`, ausentes. Os três gitlinks acima falharam no fetch, mais que o “ao menos um” citado. Não atualizar ponteiros automaticamente sem recuperar ou aprovar substitutos. |

## 3. Achados priorizados

As linhas referem-se aos commits identificados na seção 1. Prioridade expressa
risco e urgência de investigação, não probabilidade comprovada de falha.

### A1 — Reprodução do workspace e CI bloqueadas por gitlinks (P0)

`.github/workflows/ci.yml` usa checkout recursivo antes de sincronizar o
workspace. O fetch direto dos gitlinks de beam, core e skymap falhou como
descrito acima; um clone limpo com acesso equivalente pode falhar antes dos
testes. Não se demonstrou uma execução real do GitHub Actions. A escolha de
novos commits pode alterar APIs e resultados científicos; restaurar os objetos
originais ou revisar e aprovar substituições em cada submódulo antes do bump.

### A2 — Falha silenciosa na construção de pointing (P0/P1)

`packages/radioskysims-simulation/src/radioskysims_simulation/domain/simulation/simulation.py:1082-1106`
captura `Exception` na construção do pointing e executa `pass`.
Em `:1390-1440`, `_compute_boresight` tenta outros caminhos; o adapter em
`:1454-1469` pode usar `source.tracks["theta"]` se não houver boresight.
Assim, uma falha pode mudar o caminho de cálculo sem diagnóstico. **Risco
científico potencial**, não foi demonstrado erro numérico nesta revisão.
Precisam-se testes que injetem erro, validem o comportamento e comparem os
resultados físicos; decidir explicitamente quando um fallback é aceitável.

### A3 — Método sobrescrito na definição da classe (P1)

`packages/radioskysims-simulation/src/radioskysims_simulation/application/services/sim_orchestrator.py:259-339`
define duas vezes `_run_galaxy_maps_for_antenna`. Em Python, a segunda definição
substitui a primeira; o corpo anterior, incluindo seu evento de log, não é
executado por essa chamada. O método substituto delega ao caminho genérico
em `:1609`. Não se infere regressão física sem comparar os caminhos. Remover a
duplicação após caracterização de erros, logging e resultados.

### A4 — Inversões de dependência (P1)

- Simulation: `application/services/sim_orchestrator.py:403-446` aceita
  `ProcessorPort` injetado, mas cria `ResourceAwareProcessor` concreto no
  fallback; `:630-670` instancia loaders de beam de outro pacote. A facade
  `application/orchestrators/mapmaking_orchestrator.py:58-73` cria adapter
  concreto no `default()`. Há DI real, porém não cobre todos os caminhos.
- Sources: `application/services/radio_sources_manager.py:158-200` constrói
  repositório concreto em `from_db`, enquanto `from_repository` aceita uma
  dependência fornecida. Outros exemplos incluem
  `application/orchestrators/continuum_source_orchestrator.py:78-83` e
  `application/services/local_sources_manager.py:187`.
- Waterfall: `domain/models.py:510-543` chama pipeline, storage e plot; também
  `domain/lightcurve.py:95` e `domain/sed.py:95` chamam visualização. São
  métodos de conveniência públicos, portanto sua remoção pode quebrar usuários.
- Core (`fbec29a`, não gitlink): `domain/geometry/skyfield_provider.py:24-26`
  reexporta um adapter de application para compatibilidade; o problema está
  na direção do import, não simplesmente na presença da biblioteca Skyfield.
  Beam (`a9341d5`, não gitlink):
  `application/services/beam_factory.py:24-26` usa loader concreto legado.

Estes exemplos contradizem uma leitura de zero violações, sem provar que todo
import de infraestrutura seja indevido: composition roots e adapters devem
conhecer implementações concretas. Classificar facades e compatibilidade,
estabelecer política de migração e testar APIs antes de aplicar uma regra.
Logging no domínio não é, isoladamente, uma violação de DIP; avaliar efeitos,
contratos e observabilidade, não removê-lo mecanicamente.

### A5 — Cobertura de CI e qualidade desconhecidas (P1)

O workflow do meta-repositório não executa explicitamente as suítes dos outros
oito pacotes, `ruff format --check` ou mypy. `pyproject.toml:429-450` configura
mypy com `strict = true`, mas desabilita duas opções globalmente e as reativa
para `radioskysims.*`; configuração não comprova execução ou cobertura de
tipagem. Os dados de lint, cobertura e percentual de testes passando nos
relatórios históricos não têm resultado reproduzido neste snapshot.

### A6 — Complexidade e fronteiras de responsabilidade (P2)

Além dos arquivos citados na seção 2, `simulation_service.py` tem 1.020 linhas
e `resource_processor.py` 1.155. A presença de DI e componentes menores é
positiva, mas configuração, gestão do ciclo de vida, projeção, persistência e
montagem ainda coexistem no orquestrador. Fatiar por contratos e fluxos
observáveis, não por uma meta arbitrária de linhas, preservando API, dimensões,
unidades e equivalência numérica.

### A7 — Evidência de desempenho é contextual (P2)

`tod_performance_audit_report.md:650-712` descreve benchmark de 1 h: merge
incremental sem redução consistente de pico RSS e full-lazy de aproximadamente
135,7 s/5,46 GB contra eager de 17,3 s/3,16 GB, naquele experimento.
`:753-786` reserva 24 h para máquina mais capaz; extrapolação não é medição.
`mapmaking_binned_scaling.md` descreve um experimento analítico com variação
de NSIDE e amostras, não o pipeline completo. O relatório TOD aponta
`benchmarks/benchmark_tod.py`, ausente neste checkout; localizar o script e
versão exatos é pré-requisito para reprodução. Os números de 15,6 min/6 GB
no índice e na tabela de métricas não foram reconciliados com artefatos brutos.

### A8 — Drift documental e métricas incompatíveis (P2)

`november_2026_audit_report.md` atribui 253 testes ao meta + pacotes, enquanto
`metricas_tecnicas_2026.md` diz que 253 são apenas do meta; a coleta desta
revisão encontra 253 no meta e 1.746 no checkout misto. 84/654 arquivos
correspondem a 12,8% divergentes, não 37%. O relatório declara `uv sync`
reproduzido e todos os submódulos acessíveis, algo não verificado aqui e
contradito no checkout atual. `PLANO_EXECUCAO_NOV_2026.md` relata B4/B5
concluídos, mas a CI atual não contém os checks de formato/mypy descritos em
seus critérios; diferenças de branch/commit podem explicar parte do desvio.
Não extrapolar progresso, cobertura ou status a partir desses documentos.

## 4. Roadmap para redução e eliminação da dívida identificada

O backlog abaixo complementa, não substitui, F1/F2/F3 e o plano B1–B9 em
`.prompts/barosil.md`. IDs são deste diagnóstico; nenhum item é marcado como
concluído pela existência de um plano. Prioridades e sequência são propostas,
sem estimativas de prazo ou promessas de “dívida zero” para todo o projeto.
Alterações de código nos pacotes exigem PR/commit no submódulo e depois bump
do gitlink no meta-repositório.

| ID / prioridade | Trabalho e dependências | Critério de aceite verificável |
|---|---|---|
| **R0 / P0** | Reproduzir gitlinks de beam, core e skymap (A1); recuperar objetos em fonte autorizada ou revisar commits substitutos, suas diferenças e compatibilidade; só então atualizar ponteiros. | Clone limpo com `git submodule update --init --recursive` sem falhas; `git submodule status --recursive` sem `-`, `+` ou `U`; lock/constraints e instalação reproduzidos, evidências com SHAs. |
| **R1 / P0–P1** | Caracterizar pointing e erros (A2); independente de R2, mas merge/reprodução integrada dependem de R0. Não alterar fallback sem especificação científica. | Testes injetam falhas e verificam erro explícito ou fallback deliberado e observável; testes de regressão com coordenadas e unidades de referência documentam tolerâncias e resultados. |
| **R2 / P1** | Reproduzir baseline de testes/lint por pacote após R0; definir dependências, serviços externos, skips e tempos. | Registro por SHA, ambiente e comando, incluindo coletados/passados/falhados/skips; resultados reais de todos os nove pacotes e meta, sem confundir contagem estática com execução. |
| **R3 / P1** | Após R0/R2, ampliar CI do meta: matriz das nove suítes, integração e regras de lint; separar testes que exigem serviços/recursos e explicitar políticas de skips. | Checkout limpo e jobs obrigatórios verdes para meta + nove pacotes; falha de qualquer suíte não é mascarada; execução integrada nos gitlinks propostos. Verificar também CI própria sem presumir sua inexistência. |
| **R4 / P1** | Caracterizar e remover duplicação A3; coordenar com R1 antes de refatorar o fluxo e manter observabilidade intencional. | Uma única definição; testes verificam entradas inválidas, delegação, logging escolhido e equivalência numérica dos cenários Galaxy representativos. |
| **R5 / P1** | Inventariar imports reais por camada, inclusive relativos e dinâmicos; em seguida migrar os exemplos A4 por ports, DI e composition root. Preservar métodos/facades públicos com migração explícita; compatibilidade só nos locais permitidos. R2 precede mudanças; R3 dá proteção contínua. | Regra automatizada por pacote e exceções explícitas com motivo e prazo, cobrindo `domain → application/adapters/infrastructure` e `application → infrastructure` fora de composition roots aprovados; nenhuma violação nova, exceções existentes eliminadas ou deliberadamente aprovadas; testes de contrato, import público e bootstrap. |
| **R6 / P2** | Decompor `SimOrchestrator`, `Simulation` e serviços relacionados após caracterização R1/R4 e contratos R5. Priorizar processamento, mapas, configuração e persistência por responsabilidade. | Testes de contrato e regressão comprovam API, dimensões, coordenadas, unidades, persistência e equivalência numérica dentro de tolerâncias justificadas; sem duplicação de caminhos de cálculo e com ciclo de vida do processor testado. |
| **R7 / P2** | Medir e controlar formato, tipos e cobertura após R2/R3: fixar versão/escopo do Ruff, iniciar mypy incremental em módulos de fronteira, medir cobertura por pacote com denominadores e exclusões explícitos. | `ruff format --check` e mypy nos escopos adotados em CI; relatório versionado por SHA/comando; metas de cobertura definidas por risco após baseline, sem declarar 75% ou 100% sem medição. |
| **R8 / P2** | Recuperar/versionar scripts e artefatos de benchmark; medir tempo de build/compute, RSS e grafo, comparando processor on/off e configurações representativas. Depende de R0/R2; para 24 h, planejar hardware e controle de custos. | Resultados reproduzíveis com SHAs, hardware, dados, dimensões, parâmetros, repetições, unidades e tolerâncias; comparar com baseline em execução curta na CI e 24 h em infraestrutura adequada; não extrapolar números de outros cenários. |
| **R9 / P2** | Reconciliar README, auditorias, diagramas e plano mestre após R0–R3; manter histórico separado de fatos correntes. | Links/caminhos e exemplos conferidos; toda métrica atual tem comando, escopo, data e SHA; status B1–B9 reconciliado com commits reais, sem inventar progresso. Atualizar `docs/architecture.md` e validar Mermaid se a arquitetura mudar. |
| **R10 / P2** | Revalidar ciência por fluxo (F3): HI, mapmaking, satélites e TOD, incluindo modos/fallbacks alterados em R1/R5/R6. | Casos e dados de referência versionados ou identificados, unidades e tolerâncias explícitas, resultados registrados por SHA; distinção entre validação numérica e benchmark de desempenho. |

**Sequência sugerida:** R0 → R2 → R3; R1 e R4 podem ser caracterizados em
paralelo, com integração após R0; R5 antes de R6; R7/R8/R9 após suas baselines;
R10 acompanha mudanças que alterem caminhos científicos. Governança: cada
entrega registra evidência e status no documento-mestre e no repositório
correspondente; nenhum número histórico vira critério de aceite sem medição.
