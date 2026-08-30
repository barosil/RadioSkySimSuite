Relatório Técnico — Auditoria de Desempenho do Pipeline TOD

Projeto: RadioSkySimBranch: perf/tod-performance-auditData: 2026-08-12Escopo principal: desempenho do pipeline de geração de Time-Ordered Data (TOD), com foco em radio sources, uso de CPU, uso de memória, comportamento do ResourceAwareProcessor, Dask, xarray e regressão funcional.

1. Objetivo

Esta auditoria teve como objetivo identificar e reduzir gargalos de desempenho no pipeline TOD do RadioSkySim, preservando o comportamento científico e a compatibilidade arquitetural existente.

Os objetivos específicos foram:

estabelecer benchmarks reprodutíveis;

medir tempo de execução e uso de memória;

avaliar o comportamento do ResourceAwareProcessor;

verificar equivalência entre os caminhos processor OFF e processor ON;

identificar gargalos em Beam, TODSimulator, Simulation e concatenação xarray;

reduzir custo de CPU e pico de RAM;

preservar resultados científicos;

adicionar testes de regressão para otimizações críticas;

produzir evidências quantitativas para futuras decisões de arquitetura e paralelização.

2. Cenário de referência

O principal cenário utilizado para comparar as otimizações foi:

Parâmetro

Valor

Instrumento/configuração

BINGO

Intervalo

10 min

Resolução temporal

60 s

Amostras temporais

11

Canais de frequência

2048

Radio sources

161

Polarizações

4

Pointings

1

Satélites

desabilitados

Local sources

desabilitados

Galaxy

desabilitada

Neutral Hydrogen

desabilitado

Processor

OFF, salvo quando explicitamente testado

Scheduler

threads

Dataset final

~221.42 MB

Backend final

NumPy/eager

Chunks finais

None

O dataset final possui dimensões:

pointing      = 1
frequency     = 2048
source        = 161
time          = 11
polarization  = 4

3. Infraestrutura de benchmark

Foi criado/expandido o script:

benchmarks/benchmark_tod.py

O benchmark passou a registrar:

duração da simulação;

resolução temporal;

ativação/desativação do processor;

scheduler;

inclusão de radio/local sources;

build_time_s;

compute_time_s;

total_time_s;

RSS antes da execução;

RSS após build;

RSS após compute;

pico de RSS amostrado com psutil;

crescimento de memória no pico;

dimensões;

chunks;

tamanho lógico do dataset;

resumo do processor.

Também foi criada uma comparação de equivalência entre caminhos de execução para validar numericamente o resultado científico.

4. Estado inicial

Antes das principais otimizações, o cenário de 10 min / 161 radio sources / 2048 canais apresentava aproximadamente:

tempo total ≈ 121.1 s

O pipeline também apresentava elevado uso transitório de memória e diferenças de comportamento entre os caminhos normal e use_processor=True.

A análise mostrou que o problema de desempenho não estava concentrado apenas em Dask ou no número de fontes. Existiam operações xarray de alto custo dentro de loops críticos.

5. Achados e correções funcionais

PERF-A01 — Chave de cosmologia obsoleta no Composition Root

Foi removida uma dependência/chave obsoleta relacionada a:

cosmology_field_model

A alteração eliminou inconsistência de injeção de dependência sem modificar a física do pipeline.

PERF-A02 — Fluxo source-only dependia indevidamente de satélites

A orquestração assumia que a simulação necessitava de satélites mesmo quando havia outras contribuições físicas válidas.

Foi corrigida a lógica para considerar como contribuições válidas:

satélites;

local sources;

radio sources;

Galaxy;

Neutral Hydrogen.

O caminho legado explicitamente satellite-only permaneceu compatível.

PERF-A03 — pointing_track utilizado antes da definição

Foi corrigida a ordem de construção/uso do pointing_track, evitando dependência de uma variável ainda não estabelecida durante a montagem de radio sources.

PERF-A04 — Processor aplicava filtro angular adicional

O caminho use_processor=True aplicava um filtro de FWHM adicional que não era aplicado pelo caminho normal.

Esse comportamento fazia os dois caminhos divergirem.

O filtro extra foi removido do processor, mantendo o FWHM onde ele ainda é necessário para outras responsabilidades.

PERF-A05 — Grade de frequência divergente no Processor

O caminho processor produzia uma grade de frequência diferente da grade normal da simulação.

Foi feita a normalização para espelhar o fluxo padrão:

normalização da FrequencyRange;

interpolação do beam na grade do backend;

normalização do beam.

Após a correção, o processor voltou a produzir 2048 canais no cenário de referência.

PERF-A09 — Centro de radio sources hardcoded

O caminho processor utilizava:

RA = 190°
Dec = 0°

como centro fixo para radio sources.

Esse valor foi substituído pela posição derivada do pointing real da observação, mantendo fallback apenas quando necessário.

PERF-A12 — MemoryEstimator assumia 24 horas

O estimador de memória calculava n_time usando uma duração fixa de 24 h.

Foi corrigido para derivar o número de amostras diretamente do TimeRange:

10 min  -> 11 amostras
60 min  -> 61 amostras
24 h    -> 1441 amostras

Isso tornou a estimativa coerente com o workload real.

6. Equivalência entre Processor OFF e ON

Após as correções, foi executado um teste de equivalência numérica para:

10 min
161 radio sources
2048 canais

Resultado:

allclose      = True
same_nan_mask = True
max_abs_diff  = 0

Portanto, para esse cenário, os caminhos processor OFF e processor ON passaram a produzir resultados numericamente equivalentes.

7. Avaliação do ResourceAwareProcessor

A auditoria mostrou que a presença de Dask e a configuração de um scheduler não significam, por si só, que o loop principal das fontes está paralelizado.

O fluxo principal continua conceitualmente semelhante a:

for source in sources:
    simulate(source)

Além disso, o ResourceAwareProcessor percorre batches sequencialmente.

Após a correção do MemoryEstimator, as 161 radio sources cabem em um único batch no cenário de referência.

Resumo observado:

batches     = 1
succeeded   = 1
failed      = 0
cpu_count   = 8
scheduler   = threads

Execuções recentes mostraram:

processor OFF
~7.8 s
ΔRSS ~558 MB

processor ON
~9–10.7 s
ΔRSS ~695–707 MB

Conclusão:

Para o workload analisado, em que todas as fontes cabem em um único batch, o processor introduz overhead sem paralelizar o loop de fontes e sem reduzir o uso de memória.

Essa conclusão é específica ao cenário medido e não implica que o processor seja desnecessário para workloads maiores ou outros tipos de fonte.

8. Principal gargalo de CPU — Beam

8.1 Diagnóstico inicial

O profiling mostrou forte concentração de tempo em:

Beam.evaluate()
xarray.sortby()
indexação xarray
deepcopy NumPy

No cenário com 161 fontes e 4 polarizações, eram realizadas aproximadamente:

644 chamadas de Beam.evaluate()

O profile mostrava cerca de:

Beam.evaluate             ~151.8 s acumulados
sortby/indexação xarray   ~145 s acumulados

8.2 PERF-A25 — Ordenação repetida do beam

O método Beam.evaluate() executava repetidamente:

ds = ds.sortby("angle")

A ordenação foi movida para o construtor do Beam, sendo executada uma única vez.

Resultado aproximado:

antes  ≈ 121.11 s
depois ≈ 43.90 s

Ganho:

~2.76× mais rápido
~63.8% de redução no tempo

8.3 PERF-A27 — Vetorização de polarizações rejeitada

Foi testada uma alternativa para processar as quatro polarizações em uma única chamada de Beam.evaluate().

Apesar de reduzir o número de chamadas de 644 para 161, o benchmark piorou:

antes  ≈ 43.90 s
depois ≈ 50.28 s

O custo de indexação interna do xarray aumentou.

A alteração foi revertida.

Essa decisão foi baseada em medição, não em expectativa teórica.

8.4 PERF-A28 — assume_sorted=True

Depois de garantir a ordenação das coordenadas angle e frequency no construtor do Beam, a interpolação passou a usar:

result = ds["amplitude"].interp(
    frequency=frequency,
    angle=angle,
    assume_sorted=True,
    kwargs={"fill_value": 0.0},
)

Resultado:

~43.90 s -> ~7.68 s

Comparado ao baseline original:

~121.11 s -> ~7.7 s

Ganho total aproximado:

~15.6× mais rápido
~93.6% de redução no tempo

O profiling após essa mudança mostrou:

_oindex_get
~28.8 s -> ~0.88 s

deepcopy NumPy
~6.46 s -> ~0.29 s

A interpolação do beam deixou de ser o gargalo dominante.

9. Teste de regressão do Beam

Foi adicionado um teste para garantir que um Beam criado a partir de coordenadas desordenadas:

ordene internamente angle;

ordene internamente frequency;

preserve o resultado da interpolação;

continue compatível com assume_sorted=True.

Isso protege diretamente a premissa usada pela otimização PERF-A28.

10. Diagnóstico de memória

10.1 Problema da métrica inicial

O benchmark registrava inicialmente apenas RSS antes e depois do build.

Isso não capturava objetos temporários criados durante concatenações, ordenações e materializações intermediárias.

Foi adicionado um monitor de pico de memória utilizando psutil e uma thread de amostragem.

10.2 Pico real observado

Primeira medição confiável:

rss_before_mb        = 336.58 MB
rss_after_build_mb   = 894.66 MB
peak_rss_mb          = 1595.13 MB
peak_rss_growth_mb   = 1258.54 MB
dataset_nbytes_mb    = 221.42 MB

Isso mostrou que um dataset final de ~221 MB fazia o processo chegar temporariamente a aproximadamente 1.6 GB de RSS.

11. PERF-A30 — Remoção da lista intermediária tod_list

O fluxo originalmente mantinha uma lista tod_list e posteriormente criava _cleaned_tod.

Foi feito um experimento para limpar cada ds_src imediatamente e manter apenas _cleaned_tod.

A alteração preservou o funcionamento, mas não reduziu consistentemente o pico de memória.

Conclusão:

A sobrecarga principal não estava nas listas Python em si, mas nos buffers NumPy/xarray que permaneciam vivos durante a consolidação.

A simplificação de código foi mantida por ser funcionalmente segura.

12. PERF-A32 — Diagnóstico do xr.concat()

O xr.concat() foi instrumentado temporariamente.

Resultado:

n datasets        = 161
rss before concat = 932.55 MB
rss after concat  = 1154.97 MB
delta concat      = 222.42 MB
concat time       = 0.1267 s

Comparação:

dataset final ≈ 221.42 MB
delta concat  ≈ 222.42 MB

Conclusão:

A concatenação cria aproximadamente uma cópia adicional do tamanho lógico do TOD consolidado.

Porém, isso ainda não explicava sozinho o pico de ~1.6 GB.

13. PERF-A33 — sortby("time") redundante

Foi instrumentado o trecho:

dataset = dataset.sortby("time")

Resultado:

time monotonic   = True

rss before sort  = 1154.72 MB
rss after sort   = 1376.11 MB
delta sort       = 221.38 MB
sort time        = 0.2627 s
peak global      = 1590.90 MB

A coordenada temporal já estava ordenada, mas o xarray reorganizava o dataset mesmo assim.

O aumento de RSS após o sort era praticamente igual ao tamanho lógico do dataset final.

14. Correção do sort temporal

A ordenação incondicional:

try:
    dataset = dataset.sortby("time")
except Exception:
    pass

foi substituída por uma verificação condicional:

if "time" in dataset.coords:
    try:
        time_values = dataset.coords["time"].values

        if (
            time_values.size > 1
            and not np.all(time_values[1:] >= time_values[:-1])
        ):
            dataset = dataset.sortby("time")

    except Exception:
        dataset = dataset.sortby("time")

Com isso:

tempo já ordenado
    -> não executa sortby

tempo desordenado
    -> mantém comportamento anterior

15. Resultado da otimização de memória

Antes

peak_rss_mb        = 1590.90 MB
peak_rss_growth_mb = 1254.73 MB

Depois

peak_rss_mb        = 1154.76 MB
peak_rss_growth_mb = 818.57 MB

Ganho

redução absoluta do pico ≈ 436 MB
redução do pico absoluto ≈ 27.4%
redução da memória incremental ≈ 34.8%

O benchmark final da etapa foi:

build_time_s        = 6.8782 s
compute_time_s      = 0.0006 s
total_time_s        = 6.8787 s

rss_before_mb       = 336.19 MB
rss_after_build_mb  = 893.83 MB
rss_after_compute   = 893.83 MB

peak_rss_mb         = 1154.76 MB
peak_rss_growth_mb  = 818.57 MB

dataset_nbytes_mb   = 221.42 MB
chunks              = None

16. Comparação consolidada

Métrica

Estado inicial

Estado atual

Resultado

Tempo radio TOD 10 min

~121.1 s

~6.9–7.8 s

~15.6×

Redução de tempo

—

—

~93.6%

Pico RSS medido

~1590.9 MB*

~1154.8 MB

-436 MB

Redução do pico absoluto

—

—

~27.4%

Crescimento do RSS

~1254.7 MB

~818.6 MB

~34.8% menor

Dataset final

~221.4 MB

~221.4 MB

preservado

Chunks finais

None

None

eager

Compute posterior

~0 s

~0 s

eager

* O monitor de pico foi introduzido durante a auditoria; portanto esse valor representa o baseline da fase de memória, não necessariamente o pico correspondente ao primeiro benchmark de ~121 s.

17. Estado de regressão

A última regressão completa registrada após a remoção dos experimentos
full-lazy rejeitados apresentou:

1060 passed
9 skipped
1 xfailed

Após a introdução da instrumentação opcional do ResourceAwareProcessor, os
testes focados relacionados ao processor e ao SimOrchestrator apresentaram:

21 passed
1049 deselected

Não foram observadas regressões funcionais associadas à instrumentação.

18. Gargalo atual de memória

Após a remoção do sortby("time") redundante, o pico de memória do cenário
radio-only de 10 min ficou próximo ao RSS observado após xr.concat():

RSS pós-concat anterior ≈ 1154.71 MB
pico observado          ≈ 1154.76 MB

Isso localiza o principal custo de RAM restante na coexistência de:

datasets individuais das fontes
+
resultado consolidado produzido por xr.concat()

O pipeline de radio sources permanece predominantemente eager nesse caminho.

19. Experimentos estruturais posteriores

19.1 Merge incremental no ResourceAwareProcessor

Foi avaliada uma estratégia em que o processor deixava de acumular todos os
datasets parciais em uma lista e realizava a consolidação incrementalmente a
cada batch.

Em um benchmark integrado de 1 h com limite fixo de batch de 800 MB, foram
observados aproximadamente:

baseline com lista de parciais
build ≈ 26.82 s
peak RSS ≈ 3015 MB

merge incremental
build ≈ 16.5–19.2 s
peak RSS ≈ 2982–3130 MB

Embora algumas execuções tenham apresentado redução no tempo de build, não
houve redução consistente do pico de memória.

Conclusão:

a estratégia de merge incremental foi rejeitada para esta entrega, pois não
resolveu o objetivo principal de redução de RAM e aumentaria a complexidade do
fluxo de consolidação.

O ResourceAwareProcessor foi mantido com o comportamento original:

acumulação de partials
+
_merge_results() ao final

19.2 Full-lazy para radio sources

Também foi avaliada a conversão do fluxo de radio sources para Dask desde o
track, passando pelo PSD, até T_antenna e power.

O experimento conseguiu produzir batches puramente radio source com backend
Dask, mas apresentou forte crescimento do grafo e piora de desempenho.

Benchmark integrado de 1 h:

implementação eager anterior
build ≈ 17.3 s
peak RSS ≈ 3.16 GB

experimento full-lazy
build ≈ 135.7 s
peak RSS ≈ 5.46 GB

O build ficou aproximadamente 7.8 vezes mais lento e o consumo de memória
aumentou em cerca de 2.3 GB.

Além disso, foram observados milhares de tasks Dask por variável e crescimento
substancial do grafo após a consolidação dos batches.

Conclusão:

tornar todo o caminho de radio sources lazy indiscriminadamente não é uma
otimização adequada para o workload atual.

As alterações específicas desse experimento foram revertidas.

Foi mantida apenas a correção independente no Beam que permite preservar
laziness quando ângulos Dask precisam ser convertidos entre radianos e graus.

20. Instrumentação do ResourceAwareProcessor

Foi adicionada instrumentação opcional, desabilitada por padrão, através de:

processor_diagnostics=True

A instrumentação registra, quando habilitada:

RSS antes dos batches;

RSS antes de cada batch e após Simulation.run();

contagem de fontes por source_type;

contagem de source_type observada no dataset parcial;

tamanho lógico de datasets parciais e do dataset consolidado;

backend de T_antenna e power;

número aproximado de tasks Dask;

RSS após o merge final;

backend e tamanho aproximado do grafo do resultado consolidado.

O benchmark TOD expõe a opção:

--processor-diagnostics

e inclui a telemetria no resultado estruturado.

A instrumentação não altera o algoritmo de consolidação e não executa quando
não é solicitada.

21. Escala de 24 horas

O cenário científico desejado para validação final é aproximadamente:

24 h de observação
resolução temporal de 1 min
satélites
radio sources
local sources
2048 canais, conforme configuração utilizada

A máquina local utilizada durante a auditoria possui aproximadamente 7.5 GiB
de RAM.

Os benchmarks de 1 h já produziram picos da ordem de 3 GB no caminho normal,
enquanto o experimento full-lazy ultrapassou 5 GB.

O dataset lógico cresce significativamente com a duração da observação. Uma
extrapolação linear simples do dataset integrado de 1 h coloca o cenário de
24 h em uma ordem de grandeza de dezenas de gigabytes de dados lógicos.

Essa extrapolação é apenas indicativa e não substitui medição real.

Por esse motivo, o benchmark integrado completo de 24 h não deve ser forçado
na máquina local.

Decisão operacional:

o benchmark de 24 h fica reservado para execução em máquina com mais RAM e
CPU, como infraestrutura disponível na universidade.

Os benchmarks de 10 min e 1 h permanecem como validações de engenharia e
regressão de desempenho no ambiente local.

Portanto:

PERF-05 não é considerado concluído localmente;

a implementação está pronta para a validação de escala;

a execução de 24 h permanece como validação externa de hardware.

22. Outros requisitos de performance concluídos

Persistência por source type

SimulationResult permite selecionar e persistir separadamente:

satellite
localsource
radiosource

mantendo metadados de proveniência e sem forçar materialização global do
dataset antes da seleção.

Parâmetros de busca de radio sources

SimOrchestrator e SimulationService passaram a aceitar:

radio_search_radius_deg
radio_min_flux_jy

com precedência:

argumento explícito
>
default histórico

Os valores efetivamente utilizados também são registrados no resumo da query
de radio sources.

Eventos

O dataset principal da simulação permanece lazy quando seu backend é Dask.

A extração de eventos/transits possui contrato explícito de materialização por
chunks temporais, em vez de executar compute() sobre todo o dataset.

Os eventos são calculados sob demanda e armazenados em cache após o primeiro
acesso.

Dask Client/dashboard

O processor suporta scheduler distributed com LocalCluster e Client locais e
expõe o endereço do dashboard quando disponível.

23. Dívidas técnicas identificadas

A auditoria também registrou pontos que permanecem fora do escopo desta etapa.

Arquitetura

SimOrchestrator depende diretamente do ResourceAwareProcessor da Infrastructure;

SimulationService resolve implementações concretas de beam da Infrastructure;

Simulation.run() importa _compute_time_grid da Application, introduzindo
dependência Domain -> Application.

Paralelização

Simulation.run() percorre fontes serialmente;

ResourceAwareProcessor percorre batches sequencialmente;

o scheduler Dask não paraleliza automaticamente esses loops;

o caminho atual pode manter datasets parciais vivos até a consolidação final.

Radio sources

o pipeline depende de catálogo previamente ingerido;

ausência de fontes ainda pode produzir uma falha pouco específica em alguns
caminhos.

Metadados TOD

O TODSimulator possui dívida semântica histórica relacionada ao atributo
contributions, que pode indicar satellite mesmo em caminhos envolvendo outros
tipos de fonte.

Esses pontos devem ser tratados como dívida arquitetural ou semântica futura,
e não como bloqueadores da auditoria de performance atual.

24. Estado das tarefas PERF

PERF-01
Auditoria do fluxo TOD
Concluído

PERF-02
Auditoria Processor/Dask/lazy
Concluído no escopo atual

PERF-03
Benchmark reprodutível
Concluído

PERF-04
Baseline reduzido
Concluído

PERF-05
Benchmark integrado 24 h
Validação externa pendente — requer hardware com mais memória

PERF-06
RAM / tempo / chunks
Concluído para benchmarks locais de 10 min e 1 h

PERF-07
Gargalos por componente
Concluído

PERF-08
Processor/materialização
Concluído no escopo atual; instrumentação por batch adicionada

PERF-09
Radio sources
Concluído no escopo atual; parâmetros configuráveis e experimentos lazy avaliados

PERF-10
Dask Client/dashboard
Concluído

PERF-11
Testes de regressão
Ativo / validado

PERF-12
Relatório técnico
Atualizado

25. Conclusão

A auditoria mostrou que os maiores ganhos no pipeline TOD não vieram de
simplesmente ativar Dask ou aumentar paralelismo.

O principal gargalo inicial de CPU estava em operações xarray repetidas dentro
do Beam.evaluate(), especialmente ordenação e interpolação.

A combinação de ordenação única do Beam e assume_sorted=True reduziu o cenário
radio-only de referência aproximadamente de:

121.1 s
para
~7 s

sem diferença numérica detectável no teste de equivalência.

Na memória, a remoção do sort temporal redundante reduziu o pico observado de
aproximadamente:

1591 MB
para
1155 MB

Os experimentos posteriores mostraram duas conclusões importantes:

merge incremental entre batches
-> não reduziu RAM de forma consistente

full-lazy indiscriminado para radio sources
-> aumentou fortemente tempo, memória e tamanho do grafo Dask

Esses experimentos foram tratados como resultados da auditoria e não como
falhas: ambos evitam introduzir otimizações estruturalmente mais complexas sem
evidência quantitativa de benefício.

O ResourceAwareProcessor mantém seu algoritmo original de consolidação e agora
possui telemetria opcional para medir memória, composição dos batches e
comportamento Dask.

O benchmark de 24 h foi separado da validação de engenharia local. O ambiente
local é suficiente para benchmarks curtos e intermediários, mas a validação
integrada de 24 h será executada em hardware com maior capacidade de memória.

Assim, o pipeline TOD encontra-se em um estado significativamente mais rápido,
melhor instrumentado e com decisões de arquitetura fundamentadas por
benchmarks reproduzíveis.

Os principais itens restantes deixam de ser otimizações locais especulativas e
passam a ser:

validação integrada de 24 h em hardware adequado;

monitoramento de regressão dos benchmarks;

evoluções estruturais futuras apenas quando novos workloads demonstrarem
necessidade mensurável.
