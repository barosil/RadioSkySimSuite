> **Atualização do snapshot de agosto/2026** — complementar a
> `docs/relatorio_ago_2026.md`.
> **As-of:** 2026-09-01.

# Relatório Atualizado — RadioSkySimSuite (Setembro/2026)

**Branch analisada:** `copilot/update-relatorio-ago-2026`  
**Commit de referência:** `40606e3`  
**Escopo efetivamente auditado:** meta-repo em `/src`, `tests`, `scripts` e
documentação em `docs/`.

## 1) Resumo executivo

O projeto evoluiu para um **meta-repo orientado a workspace `uv`**, com
arquitetura hexagonal e separação explícita entre pacote umbrella
(`radioskysim`) e 9 subpacotes versionados como submódulos. No clone auditado,
os submódulos aparecem apenas como ponteiros Git, então a análise direta do
código ficou concentrada no umbrella, nos testes e na documentação.

Leitura curta:

- **Arquitetura:** boa direção estratégica, especialmente em bootstrap, CLI e
  contratos; o desenho DDD/Hexagonal continua coerente.
- **Engenharia:** documentação forte, lint bem menor que no snapshot de agosto,
  mas ainda com passivo de formatação e cobertura parcial de docstrings.
- **Científico/performance:** a base está claramente desenhada para
  **processamento local com Dask, controle de memória e datasets lazy**; o
  caminho GPU/HPC ainda é aspiracional, não operacional, no estado visível.
- **Dívida técnica principal:** módulos grandes no umbrella, resíduos legados em
  `src/analysis`, `src/arpls`, `src/bingo`, documentação histórica dispersa e
  dependência operacional dos submódulos para auditoria completa.

## 2) Método e limitações da atualização

Fontes usadas:

- `docs/architecture.md`
- `docs/architecture/entrypoints.md`
- `docs/code_quality.md`
- `docs/performance/PROFILING_GUIDE.md`
- `docs/source/performance.md`
- `docs/audits/tod_performance_audit_report.md`
- `README.md`
- `pyproject.toml`
- varredura estática do código em `src/`, `tests/` e `scripts/`

Limitação importante desta atualização:

- os diretórios `packages/*` estão registrados em `.gitmodules`, mas aparecem no
  clone atual apenas como **submódulos não inicializados**;
- por isso, as métricas quantitativas abaixo representam o **código visível no
  meta-repo**, não a soma integral dos 9 pacotes desacoplados.

Isso não invalida o relatório, mas muda seu foco: ele avalia com alta confiança
o umbrella, a superfície de integração e a documentação, e com confiança
moderada os domínios desacoplados descritos apenas pelos documentos canônicos.

## 3) Descrição resumida do projeto

O **RadioSkySimSuite** é uma suíte Python para simulação e análise do céu em
rádio, voltada ao contexto BINGO e a workloads de radioastronomia/cosmologia.
Os principais fluxos cobertos pela documentação e pelos entrypoints atuais são:

- geração e análise de **SkyMaps** HEALPix;
- síntese de **TOD** (*Time Ordered Data*);
- integração de fontes locais, satélites e rádio-fontes;
- persistência de resultados em disco e banco;
- visualização interativa via CLI/GUI.

O desenho atual privilegia:

- execução em **nó único**;
- uso de **xarray + Dask** para arrays lazy;
- particionamento por memória via `ResourceAwareProcessor`;
- persistência em HDF5/Zarr + PostgreSQL;
- separação entre composição (`bootstrap`), casos de uso e adapters.

## 4) Adesão à arquitetura DDD / Hexagonal

### Avaliação

**Adesão estratégica: alta.**

Há sinais fortes de DDD/Hexagonal no nível de arquitetura:

- contexts bem definidos em `docs/architecture.md`:
  Beam, Satellite, LocalSources, RadioSources, TOD, SkyMap, Simulation e
  Waterfall;
- composition root explícito em `src/radioskysims/bootstrap/`;
- CLI montada por injeção de dependências em
  `src/radioskysims/bootstrap/skymap_cli.py`;
- uso de ports/contratos e testes de contrato em
  `tests/infrastructure/ports/test_port_contracts.py`.

**Adesão tática: parcial, mas melhor delimitada.**

No clone visível, o umbrella já está bem mais fino do que no relatório de
agosto: `application`, `infrastructure` e `domain` residuais quase desapareceram
do pacote raiz, enquanto `interfaces` e `visualization` concentram a maior parte
do código restante. Isso é um sinal positivo do desacoplamento.

### Comentário crítico

O projeto hoje parece estar em um estágio de **DDD estratégico maduro** e
**DDD tático em transição**, porque:

- o mapa de bounded contexts está claro;
- a composição e os entrypoints já respeitam bem a fronteira entre interface e
  aplicação;
- porém a auditoria completa do domínio desacoplado depende do checkout real dos
  submódulos.

Em termos práticos: a arquitetura está mais convincente que o snapshot de
agosto, mas a governança do meta-repo ainda depende de garantir observabilidade
dos pacotes desacoplados no CI e nas auditorias.

## 5) Tech stack comentado

### Base principal

- **Python 3.11–3.14**: escolha adequada para ecossistema científico atual.
- **uv workspace**: excelente para meta-repo com múltiplas distribuições, mas
  exige disciplina de bootstrap e CI.
- **Pydantic / SQLModel / SQLAlchemy**: boa combinação para DTOs, settings e
  persistência.
- **NumPy / xarray / Dask**: stack correta para simulação científica com arrays
  grandes e restrição de memória.
- **Astropy / Skyfield / Healpy / PySM3 / astroquery / pyvo**: stack alinhada à
  radioastronomia e cosmologia aplicada.
- **Panel / HoloViews / Bokeh**: adequados para exploração interativa e
  visualização técnica.
- **pytest / ruff / Sphinx + MyST**: base de engenharia sólida.

### Comentário especializado

- O projeto está bem posicionado para **workloads CPU-bound com arrays lazy**.
- A estratégia Dask favorece **máquinas não distribuídas**, com opção de
  `LocalCluster` quando necessário.
- **Não há evidência de backend GPU operacional** no código auditado; GPU/HPC
  aparece mais como direção futura do que como capacidade pronta.
- Há uso pontual de **Numba** em `src/arpls`, mas fora do fluxo principal de TOD.

## 6) Entrypoints atuais

### Oficiais / recomendados

1. `radioskysims` → `src/radioskysims/bootstrap/skymap_cli.py`
   - console script principal do pacote umbrella;
   - monta casos de uso de SkyMap e delega para a CLI.

2. `gnss4astro` → `gnsstools4astro.bootstrap.gnss4astro_cli:main`
   - declarado no `pyproject.toml`;
   - dependente do submódulo correspondente.

3. `scripts/start_service.py`
   - entrypoint operacional de GUI/TOD;
   - chama `create_sim_orchestrator()` e sobe `TODPanel`.

4. `scripts/check_db.py`
   - utilitário operacional de diagnóstico do banco.

5. `scripts/check_docs.py`
   - verificador local de docstrings e type hints do umbrella.

### Secundários / residuais

- `src/radioskysims/main.py`
- `src/radioskysims/interfaces/cli/commands/export_worker.py`
- `src/radioskysims/bootstrap/skymap_gui.py`

Leitura de engenharia: hoje o projeto já tem um **entrypoint principal claro
para SkyMap** e um **entrypoint pragmático para TOD/GUI**, o que é melhor que o
estado descrito no documento histórico de julho.

## 7) Casos de uso observáveis

Os casos de uso mais concretos no estado auditado são:

- **SkyMap / generate**: geração de mapas sintéticos;
- **SkyMap / survey**: aquisição de survey contínuo por coordenadas e campo;
- **SkyMap / analyze**: cálculo de espectro angular e inspeção de mapas;
- **TOD export / jobs**: exportação e monitoramento por CLI;
- **TOD viewer**: abertura de painel a partir do orquestrador;
- **integrações E2E**: testes cobrindo pipeline completo, multi-source workflow,
  mapas persistidos para TOD e fluxos cosmológicos.

Do ponto de vista funcional, o projeto já oferece uma boa superfície para:

- exploração científica;
- automação via CLI;
- integração com notebooks;
- evolução para workflows reproduzíveis.

## 8) Qualidade de código

## 8.1) Tamanho do código visível neste clone

### Totais

- **`src/`**: 81 arquivos Python / **10.667 linhas**
- **`tests/`**: 53 arquivos Python / **9.724 linhas**
- **`scripts/`**: 7 arquivos Python / **1.294 linhas**
- **Total auditado (código + testes + scripts)**: **21.685 linhas**

### Módulos principais por área

| Área | Arquivos | Linhas |
|---|---:|---:|
| `src/radioskysims/interfaces` | 25 | 4.071 |
| `src/analysis` | 7 | 2.848 |
| `src/radioskysims/visualization` | 2 | 1.288 |
| `scripts` | 7 | 1.294 |
| `src/bingo` | 6 | 550 |
| `src/arpls` | 4 | 511 |
| `src/radioskysims/bootstrap` | 5 | 231 |
| `src/radioskysims/infrastructure` | 9 | 123 |
| `src/radioskysims/application` | 4 | 96 |
| `src/radioskysims/domain` | 3 | 2 |

### Leitura arquitetural das métricas

- O umbrella virou de fato um **pacote de integração/apresentação**.
- A maior parte do código restante está em **interfaces** e
  **visualização**, o que é coerente com um meta-pacote fino.
- A permanência de `analysis`, `bingo`, `arpls` e `GNSStools4Astro` no `src/`
  indica **resíduo legado/vendorizado** que ainda pesa na manutenção.

## 8.2) Linting, formatação, docstrings, type annotations, documentação

### Linting

Execução local de `ruff check src tests scripts`:

- **98 erros**
- **64 fixáveis automaticamente**

Regras mais frequentes:

- `I001` (`unsorted-imports`): 39
- `BLE001` (`blind-except`): 16
- `RUF100` (`unused-noqa`): 9
- `DTZ001` (`datetime` sem timezone): 6

Arquivos com mais ocorrências:

1. `src/radioskysims/visualization/waterfall.py` — 12
2. `src/radioskysims/utils/settings.py` — 6
3. `tests/application/services/test_sim_orchestrator_radio_params.py` — 5
4. `tests/domain/test_satellite_factory.py` — 5
5. `tests/interfaces/gui/skymap/test_app.py` — 5

### Formatação

Execução local de `ruff format --check src tests scripts`:

- **41 arquivos seriam reformatados**
- **76 arquivos já estão formatados**

### Docstrings e type annotations

`python scripts/check_docs.py` no umbrella:

- **51 arquivos verificados**
- **27 arquivos com problemas**
- **57 issues** reportadas

Métrica AST no código Python visível (`src/`, `tests/`, `scripts/`):

- módulos com docstring: **48,2%**
- classes com docstring: **59,4%**
- funções com anotação de retorno: **75,4%**
- argumentos anotados: **64,7%**

### Documentação

Pontos fortes:

- `docs/architecture.md` está claro e atualizado como documento canônico;
- `docs/source/performance.md` e os relatórios de auditoria trazem conteúdo
  técnico útil para tuning de memória;
- a documentação cobre arquitetura, performance, uso, configuração e testes.

Pontos fracos:

- ainda há muitos snapshots históricos convivendo com documentos ativos;
- a distinção entre documento canônico, histórico e backlog nem sempre é óbvia;
- o meta-repo depende fortemente da documentação para representar pacotes cujo
  código não está presente no clone.

## 8.3) Módulos grandes que merecem refatoração

Maiores arquivos do código visível:

1. `src/radioskysims/visualization/waterfall.py` — **1.250 linhas**
2. `src/radioskysims/interfaces/gui/skymap/presenters.py` — **885 linhas**
3. `src/analysis/observation.py` — **730 linhas**
4. `src/analysis/rfi.py` — **660 linhas**
5. `src/radioskysims/interfaces/cli/main.py` — **603 linhas**

### Prioridade de refatoração

- **`visualization/waterfall.py`**: prioridade mais alta. Mistura volume,
  rendering, materialização e heurísticas de uso de dados; também concentra o
  maior passivo de lint.
- **`interfaces/gui/skymap/presenters.py`**: forte candidato a dividir em
  presenters por caso de uso (`generate`, `survey`, `analyze`) e por widget.
- **`interfaces/cli/main.py`**: parser robusto, mas já grande o suficiente para
  migrar para composição por subcomandos.
- **`analysis/observation.py` / `analysis/rfi.py`**: úteis cientificamente, mas
  devem ser tratados como biblioteca analítica separada ou absorvidos por pacote
  dedicado, para não continuar acoplando o umbrella.

## 8.4) Comentário sobre os melhores módulos

Os melhores módulos no estado atual são os que mais claramente respeitam
fronteiras arquiteturais:

- `src/radioskysims/bootstrap/skymap_cli.py`
  - pequeno, tipado, com composição explícita;
  - excelente exemplo de composition root enxuto.

- `src/radioskysims/interfaces/cli/commands/generate_skymap.py`
  - função fina, focada em DTO → use case → formatter;
  - boa separação entre apresentação e aplicação.

- `src/radioskysims/interfaces/cli/commands/analyze_skymap.py`
  - usa `Protocol` para dependência mínima;
  - preserva baixo acoplamento na superfície da CLI.

- `tests/infrastructure/ports/test_port_contracts.py`
  - bom uso de testes de contrato;
  - reforça a disciplina arquitetural entre ports e adapters.

## 9) Dívida técnica

Principais dívidas identificadas:

1. **Submódulos não observáveis no clone**
   - o meta-repo depende de pacotes externos para auditoria completa;
   - CI e auditorias precisam garantir checkout consistente dos submódulos.

2. **Resíduo legado no umbrella**
   - `analysis`, `bingo`, `arpls` e `GNSStools4Astro` ainda ampliam a superfície
     de manutenção do pacote raiz.

3. **Documentação histórica excessiva em `docs/`**
   - há material canônico, histórico e auditorias no mesmo nível;
   - isso dificulta navegação e aumenta risco de uso de diagnóstico vencido.

4. **Módulos monolíticos em visualização e apresentação**
   - `waterfall.py`, `presenters.py` e `interfaces/cli/main.py`.

5. **Cobertura incompleta de docstrings e padronização**
   - especialmente em módulos utilitários, widgets e scripts.

6. **Tooling de bootstrap frágil**
   - o workspace depende de `uv`, mas o ambiente precisa garantir isso de forma
     mais explícita em onboarding e CI.

## 10) Detalhamento da simulação TOD

Com base na documentação canônica e nos relatórios de performance:

1. o entrypoint/interface chama o composition root;
2. o composition root monta serviços, adapters, config e repositórios;
3. o orquestrador recebe parâmetros de execução;
4. com `use_processor=True`, o fluxo entra no `ResourceAwareProcessor`;
5. o processor estima recursos, particiona fontes em batches e coordena Dask;
6. o resultado principal permanece em **`xarray.Dataset` lazy**;
7. produtos derivados como `events` são materializados **por chunks temporais**;
8. persistência ocorre em **HDF5/Zarr** e metadados vão para PostgreSQL.

### Pontos fortes do desenho

- foco explícito em **controle de memória**;
- preferência por **materialização tardia**;
- suporte a `dask_scheduler="threads" | "synchronous" | "distributed"`;
- `LocalCluster` documentado para inspeção e dashboard.

### Pontos de atenção

- o fluxo de radio sources ainda é apontado na auditoria como relativamente
  **eager** em trechos de consolidação;
- o merge final por `xr.concat()` segue como candidato natural a pico de RAM;
- a documentação recomenda evitar `compute()` global e manter extrações
  derivadas por chunks, o que está conceitualmente correto.

### Leitura especializada

Para observações de 24h em cadência de minuto, com satélites, rádio-fontes e
fontes locais, a decisão de engenharia mais importante não é “maximizar Dask”,
mas **limitar conscientemente onde o grafo lazy cresce**. A própria auditoria de
performance mostra que “full-lazy” indiscriminado para radio sources piorou
tempo e memória, o que é coerente com workloads científicos de concatenação e
redução heterogênea.

## 11) Eficiência de código, gargalos e melhorias

### Gargalos já evidenciados

- **consolidação final de batches** no `ResourceAwareProcessor`;
- **radio sources** com caminho parcialmente eager;
- **transformadas Healpy** (`map2alm`) como hotspot esperado;
- materializações em pontos de visualização, como
  `visualization/waterfall.py` e presenters GUI;
- parser/CLI grande demais, o que impacta manutenibilidade mais do que CPU.

### Melhorias recomendadas

1. **separar claramente compute de apresentação**
   - impedir materialização acidental em módulos de GUI.

2. **telemetria operacional padrão**
   - tornar diagnósticos do processor mais fáceis de ativar e registrar em
     notebook/CLI.

3. **materialização seletiva por tipo de fonte**
   - persistir ou exportar subconjuntos por source type reduziria custo de
     depuração e análise.

4. **refinar política de chunks**
   - expor recomendações automáticas ao usuário final quando o dataset estimado
     se aproxima do limite de RAM.

5. **explorar kernels compilados apenas nos hotspots corretos**
   - Numba/Cython valem mais para transformações numéricas estáveis do que para
     mover indiscriminadamente o pipeline para full-lazy/GPU.

6. **dashboard Dask mais visível em notebooks**
   - o endereço do dashboard deve aparecer sempre que `LocalCluster` for criado.

7. **CI de benchmark**
   - preservar os limites aceitos de TOD, Healpy e interpolação de beam.

### Comentário sobre GPU

Hoje eu não trataria GPU como prioridade de curto prazo. Antes disso, o projeto
ganha mais com:

- redução de picos de RAM na consolidação;
- isolamento de materializações;
- melhor instrumentação;
- benchmark contínuo.

GPU só tende a compensar depois que os hotspots estiverem claramente isolados e
os contratos de dados estiverem estáveis.

## 12) Novas features — sugestões

1. **Suite formal de benchmark do TOD**
   - smoke, stress e regressão com cenários padrão.

2. **Observations repository mais rico**
   - consultas mais abrangentes, serialização consistente e filtros temporais.

3. **Persistência opcional por source type**
   - satélite, rádio-fontes, locais, foregrounds cosmológicos.

4. **Domínio explícito de cosmology / HI**
   - separar melhor fluxo de neutral hydrogen do restante da simulação.

5. **Modo notebook-first para Dask local**
   - mensagem padronizada com URL do dashboard e resumo de recursos.

6. **Reorganização assistida de `docs/`**
   - mover snapshots vencidos para `_archive` com índice e banner de validade.

7. **Health-check de submódulos no CI**
   - validar se ponteiros Git, versões e imports do workspace estão coerentes.

## 13) Roadmap de evolução

### Horizonte sugerido

**Curto prazo**

- reduzir dívida de lint/formatação;
- reorganizar documentação ativa vs histórica;
- estabilizar observabilidade dos submódulos no CI;
- fatiar `waterfall.py` e `presenters.py`.

**Médio prazo**

- reforçar benchmark e telemetria do pipeline TOD;
- ampliar recursos de persistência e consulta;
- consolidar cosmology / HI / mapmaking como domínios mais explícitos.

**Longo prazo**

- preparar trilha HPC real (`dask-mpi`, multi-node, eventualmente GPU);
- revisar fronteiras definitivas entre umbrella, pacotes científicos e legados.

## 14) Proposta de sprints para melhoria de engenharia

### Sprint 1 — Higiene e governança do meta-repo

- reduzir `ruff` com foco em `I001`, `BLE001`, `RUF100`, `DTZ001`;
- zerar backlog de formatação automática;
- classificar `docs/` em canônico, auditoria e histórico;
- adicionar verificação de submódulos no pipeline.

### Sprint 2 — Refatoração de superfície

- quebrar `visualization/waterfall.py`;
- modularizar `interfaces/gui/skymap/presenters.py`;
- decompor `interfaces/cli/main.py` por subcomando/contexto;
- elevar cobertura de docstrings nos módulos públicos.

### Sprint 3 — Observabilidade e performance

- padronizar diagnósticos do `ResourceAwareProcessor`;
- publicar dashboard Dask em notebook/CLI;
- adicionar benchmark contínuo para TOD / Healpy / beam;
- medir picos de RAM por cenário de referência.

### Sprint 4 — Produto científico e persistência

- enriquecer modelo de observações e consultas;
- suportar persistência/export por tipo de fonte;
- consolidar fluxo cosmology/neutral hydrogen;
- revisar contratos de mapmaking e reaproveitamento de mapas persistidos.

## 15) Conclusão

Comparado ao snapshot de agosto, o projeto agora transmite melhor a ideia de um
**meta-repo desacoplado**, com umbrella enxuto e arquitetura mais nítida. O
desafio central deixou de ser “provar a arquitetura” e passou a ser
**operacionalizar a engenharia**: observabilidade dos submódulos, redução de
superfície residual no umbrella, benchmark contínuo e governança da
documentação.

Em termos científicos, a base está bem orientada para **simulação em máquina
única com restrição de memória**, usando Dask de forma pragmática. Em termos de
engenharia, a próxima maturidade virá menos de novas abstrações e mais de
**instrumentação, refatoração de superfície e disciplina de release do
workspace**.
