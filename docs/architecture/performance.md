# Performance — Análise de Eficiência e Gargalos (RadioSkySimSuite)

**Data:** 2026-09-01

> Este documento é **complementar** a [`docs/source/performance.md`](../source/performance.md)
> (guia de uso do `ResourceAwareProcessor`/`SystemMonitor`/tuning de Dask) e a
> [`docs/audits/tod_performance_audit_report.md`](../audits/tod_performance_audit_report.md)
> (benchmark detalhado de agosto/2026). Aqui o foco é **análise de
> engenharia**: onde estão os gargalos, por que, e o que fazer a respeito —
> sintetizando a seção 10 de [`relatorio_set_2026_v2.md`](relatorio_set_2026_v2.md).

## 1. Desenho geral

A suíte é desenhada para **processamento em nó único com controle de
memória**, não para escala distribuída/HPC:

- `xarray` + `dask` para arrays lazy por padrão;
- `ResourceAwareProcessor` (`radioskysims_simulation.infrastructure.processing.
  resource_processor`, 1.235 linhas) particiona fontes em batches por
  `max_batch_mb`, faz streaming para disco quando a saída estimada excede a
  RAM disponível, e nunca materializa o dataset completo em memória;
- `SystemMonitor` (`radioskysims_core.monitor.system_monitor`) fornece
  `snapshot()`/`check_resources()` para detectar recursos disponíveis antes
  de rodar;
- `dask_scheduler` configurável (`threads` | `synchronous` | `distributed`),
  com `LocalCluster` + dashboard quando `distributed` é usado.

Esse desenho é **coerente com o hardware alvo** (estações de trabalho/
servidores universitários com RAM limitada), não com clusters HPC — o que é
uma decisão de engenharia correta para o estágio atual do projeto.

## 2. Hotspots conhecidos (evidenciados por auditoria de performance)

Com base em `docs/audits/tod_performance_audit_report.md` (benchmark de
10 min e de 1h, cenário BINGO/GPS):

1. **Consolidação final de batches** (`xr.concat` no
   `ResourceAwareProcessor`) — ponto natural de pico de RAM, pois reúne
   resultados de todos os batches antes de retornar/persistir.
2. **Rádio-fontes** — caminho historicamente mais *eager* que satélites/
   fontes locais; um experimento para tornar o fluxo "full-lazy" **piorou**
   tempo e memória e foi explicitamente rejeitado com base em medição — é um
   contraexemplo importante: nem toda materialização tardia é uma melhoria.
3. **Transformadas Healpy** (`map2alm` e correlatas) — hotspot esperado por
   natureza (transformada esférica O(N^{3/2}) a O(N²) dependendo do `lmax`),
   não específico deste código.
4. **Materializações acidentais fora do processor** — `visualization/
   waterfall.py` (1.250 linhas) e os presenters da GUI (`interfaces/gui/
   skymap/presenters.py`, 885 linhas) são candidatos a computar `xarray`
   lazy sem necessidade ao construir plots.

## 3. Por que os hotspots são difíceis de otimizar com segurança hoje

Os módulos que fazem a orquestração onde os hotspots vivem são exatamente os
módulos maiores e mais complexos do monorepo (ver `code_quality.md §4`):

- `sim_orchestrator.py` (1.623 linhas, `C901` concentrado) mistura wiring de
  4 famílias de fonte + processor + persistência;
- `resource_processor.py` (1.235 linhas) é relativamente coeso, mas grande o
  suficiente para dificultar profiling função-a-função;
- `satelliterepository.py` (834 linhas) mistura persistência, curadoria e
  ingestão externa — qualquer otimização de I/O ali precisa navegar três
  responsabilidades diferentes.

**Implicação prática**: otimizar performance com segurança exige primeiro
reduzir o tamanho/acoplamento desses módulos (ver `module_dependencies.md`),
não o contrário. Profiling e refatoração devem andar juntos aqui.

## 4. GPU / HPC

- Não há evidência de backend GPU operacional no código auditado.
- Uso pontual de **Numba** existe em `src/arpls` (legado, fora do fluxo
  principal de TOD — excluído do lint por `AGENTS.md`).
- **Recomendação mantida das auditorias anteriores**: não tratar GPU como
  prioridade de curto prazo. O retorno maior no momento vem de:
  1. isolar materializações acidentais fora do processor;
  2. reduzir o tamanho dos módulos de orquestração para permitir profiling
     seguro;
  3. instrumentar benchmark de regressão contínuo.
- GPU só tende a compensar depois que os hotspots estiverem isolados e os
  contratos de dados estáveis (mesma leitura do relatório de agosto,
  confirmada nesta rodada).

## 5. Recomendações de engenharia

1. **Separar compute de apresentação** — impedir materialização acidental em
   módulos de GUI/visualização (`waterfall.py`, `presenters.py`).
2. **Telemetria operacional padrão** — expor diagnósticos do
   `ResourceAwareProcessor` (`processor_diagnostics=True`) de forma mais
   acessível em notebook/CLI, incluindo a URL do dashboard Dask sempre que
   `dask_scheduler="distributed"`.
3. **Materialização seletiva por tipo de fonte** — permitir persistir/exportar
   subconjuntos por `source_type` (satélite/local/rádio/galáxia)
   reduz custo de depuração e de re-execução.
4. **Política de chunks mais explícita** — recomendar automaticamente ao
   usuário um `max_batch_mb`/chunking quando o dataset estimado se aproxima
   do limite de RAM detectado por `SystemMonitor`.
5. **Benchmark de regressão contínuo** (task `PERF-003`, ainda planejada) —
   preservar os limites aceitos de tempo/memória para TOD, Healpy e
   interpolação de beam, evitando reincidência de regressões já corrigidas.
6. **Cautela com "full-lazy" indiscriminado** — o caso de rádio-fontes mostra
   que mover tudo para lazy nem sempre ajuda; decisões de laziness devem ser
   guiadas por medição, não por princípio geral.

## 6. Relação com a suíte de testes de performance

`docs/source/testing_qa.md` define o nível **Performance** (marker
`performance`, não executado por padrão) em `tests/performance`. Este
documento não substitui aquela matriz — recomenda-se que os itens do §5
(especialmente o benchmark de regressão contínuo) sejam implementados como
testes marcados `performance`, executados sob demanda ou em pipeline
dedicado.
