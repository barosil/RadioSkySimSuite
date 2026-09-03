# Auditoria de UX dos Entrypoints e Plano de Implantação — RadioSkySimSuite

**Auditoria:** 2026-09-02 · **Plano de implantação:** 2026-09-03
**Escopo:** `src/radioskysims` (umbrella) + CLIs de pacote (`radioskysim-sources`,
`gnss4astro`) + fachada de notebook + GUI. Análise de **experiência do usuário**
(facilidade de uso, consistência, feedback, pré-condições de primeiro uso).

> Complementa o inventário de entrypoints em `docs/architecture/entrypoints.md`
> (2026-09-01). A partir de 2026-09-03 este documento é também o **plano de
> implantação consolidado** dos comentários desta auditoria e das demais em
> `docs/audits/`. O status foi verificado sobre o código **pós-desacoplamento**
> (Fases 0–7 concluídas; domínio/application/infra em `packages/*`, meta-pacote
> `src/radioskysims` com CLI/GUI + legado). As referências de linha do
> diagnóstico apontam o monólito; no plano valem os caminhos atuais.

---

## 0. Resumo executivo do plano

O desacoplamento (Fases 0–7) **moveu e encapsulou** o código, mas **transportou
junto** a maior parte da dívida de UX e de engenharia — ela segue ativa nos
pacotes e no meta-pacote. Itens superados são os que dependiam de estruturas
removidas (shims, `domain/satellite/main.py`, duplicação de beam loaders,
exemplo `run_simulation` do README).

**Legenda de status**
- `[ ]` pendente · `[~]` em andamento · `[x]` concluído
- `[>]` fora de escopo — repo próprio `gnsstools4astro`
- `[v]` superado — o desacoplamento resolveu

**Três frentes de trabalho**
- **F1 — UX dos entrypoints** (seção 4): ondas 1–3, itens R1–R6/M1–M5/L1–L3.
- **F2 — Dívida de engenharia/DDD herdada** (seção 5.1; fontes
  `docs/audits/engineering_audit_report.md` e
  `docs/architecture/technical_debt.md`).
- **F3 — Evoluções científicas e validações** (seção 5.2; auditorias de
  funcionalidade física, mapmaking, HI e TOD-performance).

**Decisões de escopo registradas**
- **`gnss4astro` fora de escopo** — desenvolvimento próprio; não deve ter
  entrypoints adicionais no umbrella. R4, L3 e a parte de R5 relativa ao
  `gnss4astro` pertencem ao repositório `barosil/gnsstools4astro` (ferramentas
  GNSS já são pacotes próprios consumidos por sources via ports — decisão do
  plano de decoupling).

---

## 1. O que o usuário vê ao rodar cada entrypoint

### `radioskysims` (umbrella) — `bootstrap/skymap_cli.py` → `interfaces/cli/main.py`

Antes do help, o usuário já vê ruído:

```
asyncpg não disponível no ambiente; async_engine não foi criado: No module named 'asyncpg'
```

```
usage: radioskysims [-h] [--debug] {skymap,tod} ...
positional arguments:
  {skymap,tod}
    skymap    Operações relacionadas a mapas do céu.
    tod       Operações de simulação TOD.
options:
  --debug    Exibe traceback completo em caso de falha.
```

Árvore aninhada: `skymap {generate, survey, analyze}`, `tod {export, jobs}`
e `tod jobs {list, status, cancel, monitor}`.

### `radioskysim-sources`

```
usage: radioskysim-sources [-h] {radio,sun} ...
  radio      comandos de fontes de rádio
  sun        informações/plots do Sol
```

Saída real de `radio list --n 3` (tabela limpa, sem rede/banco):

```
RadioSourcesManager — 3 fontes
      id     ra_deg    dec_deg  nu0_mhz    s0_jy    alpha  flux_1400mhz_jy
SIM-0000 278.624177  23.684163   1400.0 0.358798 0.358782         0.358798
```

### `gnss4astro`

```
usage: gnss4astro [-h] [--log-level LOG_LEVEL] {download,tracks,signal,sync-signals} ...
```

Subcomandos planos (verbos). A execução despeja log estruturado JSON no stdout
misturado ao resultado humano.

---

## 2. Pontos de atrito de UX

1. **Ruído no startup do umbrella** — todo `radioskysims ...` (inclusive `--help`
   e comandos que não usam banco) imprime `asyncpg não disponível...`. Causa:
   efeito colateral de nível de módulo criando engine async no import
   (`packages/radioskysims-core/src/radioskysims_core/db/aengine.py:75-81`,
   importado por `db/__init__.py`). No `tod export` soma-se um `UserWarning` do
   pydantic (`<built-in function allocate_lock> is not a Python type`).

2. **Default `--telescope` quebrado no 1º uso** — `main.py:276` define
   `default="default"`, mas o `settings.toml` raiz só define
   `[radiotelescopes.uirapuru]`. `uv run radioskysims tod export` sem args falha
   com `Erro de entrada: settings.toml: radiotelescopes.default not found`
   (`config_loader.py:272-275`). A documentação compensa hardcodando
   `--telescope uirapuru` em todos os exemplos (`docs/source/quickstart.md`).
   `scripts/start_service.py` também usa `telescope="default"`.

3. **"Sem satélites" silencioso** — `main.py:283`: `--constellations` default
   `None` e o help diz *"Se omitido, sem satélites"*. Um usuário que roda
   `tod export` sem conhecer a flag produz silenciosamente uma simulação
   vazia/sem GNSS. Idem na fachada de notebook (`notebook.py`).

4. **Fallback silencioso para catálogo simulado** — `radioskysim-sources radio
   list --source db` engole qualquer exceção e devolve `simulated()` sem
   mensagem (`radio_sources_manager.py:132`). Com banco fora do ar o usuário vê
   fontes "reais" que na verdade são simuladas.

5. **Sem cores/formatadores em nenhum CLI** — nenhum usa `rich`/`click`/`typer`/
   `colorama`. Saídas em plain `print`; barra de progresso ASCII em
   `jobs_cmd.py`. Sem hierarquia visual para aviso/erro/sucesso.

6. **Help ausente em flags obrigatórias** — em `generate`/`survey`
   (`main.py:110-190`) quase nenhuma flag tem `help=` (ex.: `--frequency-ghz`,
   `--nside`, `--survey-id`, `--base-path`). Contraste com `analyze`/`export`.

7. **Unidades embaralhadas** — `--frequency-ghz` (umbrella/PySM),
   `--bandwidth-mhz`/`--min-alt` (gnss4astro), colunas `nu0_mhz` (sources),
   enquanto o padrão documentado (AGENTS.md) é **MHz**.

8. **Três mecanismos diferentes de saída "máquina"** — umbrella
   `--output-format {text,json}`; sources nenhum; gnss4astro flag `--json`.

9. **gnss4astro: log ruidoso no stdout + falha parcial como sucesso** —
   `configure_logging("INFO")` envia JSON estruturado para stdout. Num download
   com 1 arquivo falhando (WARNING) o comando ainda imprime `Baixados: 3
   arquivos...` e retorna `0` (`main.py:115,175`). Caminho duplicado
   `data/rinex/data/rinex/...` no erro de salvamento de `.crx.gz`.

10. **Inconsistência de tratamento de erro entre os 3 CLIs** — o umbrella captura
    exceções tipadas com mensagem amigável e exit codes distintos (2–5, 1
    inesperado) + `--debug`. `radioskysim-sources` e `gnss4astro` não têm
    try/except: qualquer falha vira traceback cru.

11. **Gramática/estrutura divergente** — umbrella: 2 níveis de substantivo com
    verbos nas folhas (`skymap generate`, `tod jobs list`); sources:
    1 substantivo → verbo (`radio list`); gnss4astro: verbos planos
    (`download`, `sync-signals`). `sun` é substantivo-folha. Capitalização das
    descrições difere. São 3 modelos mentais distintos.

12. **Muitas pré-condições de 1º uso, implícitas e de fontes duplicadas** —
    para a primeira execução bem-sucedida um usuário novo precisa, sem que
    nenhuma CLI anuncie: (a) `settings.toml` raiz com perfil de radiotelescópio
    compatível com `--telescope`; (b) seção `[simulations] time_range`;
    (c) PostgreSQL no ar com tabela `radio_sources` populada (para `--source db`
    e fluxos que consultam catálogo); (d) `credentials.env` para SpaceTrack
    (ST_USER/ST_PWD, CIRADA) — só lido pelo `SpaceTrackClient`, não pela engine;
    (e) diretórios de dados (`data/rinex`, `data/TOD`, `data/aux/skyfield`).
    Agravante: **duas fontes conflitantes de config de banco** —
    `credentials.env.example` oferece `DATABASE_URL` que a engine **ignora**
    (ela usa `[DB]` do `settings.toml`).

13. **Caminhos relativos ao CWD misturados com raiz do projeto** — settings
    resolve relativo à raiz (`config_loader.py:40-60`), mas outputs default são
    relativos ao CWD: `data/TOD/tod_<ts>.nc`, `sqlite:///data/jobs.db` (umbrella),
    `plots/` (sources), `tracks.nc`/`data/rinex` (gnss4astro).

14. **Fachada de notebook com retorno misto** — `run_simulation` retorna
    `JobHandle | str` dependendo de `background` (`notebook.py`): no foreground
    devolve uma string formatada (não dados estruturados). O diretório
    `interfaces/api/` sugere REST mas não é.

15. **GUI sem entrypoint de 1 comando** — não há `radioskysims gui`; o usuário
    precisa conhecer `scripts/start_service.py` (que ainda usa `telescope=
    "default"` → falha — item 2). Complexidade de manutenção alta:
    `presenters.py` 885 linhas, `controller.py` 384, `views.py` 408.

---

## 3. Pontos fortes de UX

- Umbrella com tratamento de erro exemplar: mensagens pt-BR, classes de erro
  mapeadas a exit codes (2–5) e `--debug` opcional — padrão a replicar.
- Separação limpa DTO → caso de uso → formatador em `generate_skymap.py` /
  `analyze_skymap.py`, com saída `text`/`json` (`ensure_ascii=False`).
- Lifecycle de jobs completo: `tod jobs list/status/cancel/monitor` com barra
  ASCII + etapa + ETA, worker em background com sidecar JSON e cancelamento
  idempotente; mensagens com próximo passo acionável.
- Fachada de notebook documentada (`JobHandle`, `progress_widget`) com
  `ImportError` instrutivo.
- Defaults sensatos no `radioskysim-sources` (catálogo simulado sem rede/banco)
  e saída em tabela clara.
- `gnss4astro` documenta defaults no help e usa parser de data leniente
  (naive → UTC).
- Idioma consistente (pt-BR) e documentação com exemplos funcionais.

---

## 4. Plano de implantação — F1: UX dos entrypoints

> Reorganiza as recomendações R1–R6/M1–M5/L1–L3 em **ondas** de implantação,
> incorporando as decisões anotadas no documento. Caminhos refletem o código
> **atual** (pós-desacoplamento). O alvo de API (bloco "UX Changes") com status
> por símbolo está no **Anexo A**.

### Onda 1 — Primeiro minuto (alto impacto: R1–R3)

Itens que um usuário novo encontra nos primeiros segundos. Gate: `--help`
limpo, `tod export` sem args funcionando, nenhuma simulação vazia silenciosa.

- [x] **O1.1 · R1 — Remover ruído de startup do umbrella** *(implementado 2026-09-03)*
  - **Status:** engine async **lazy** (`aengine._ensure_async_engine`); `db/__init__.py`
    sem import de `AsyncDatabase` (inexistente); extra `asyncpg` no pyproject do core;
    campos `lock`/`async_lock`/`log` do `Tracks` → `PrivateAttr` (fim do `UserWarning`
    do pydantic no import). `--help` e import `db` limpos; tests core 104 passed.
  - Causa atual: engine async criada no import (nível de módulo) em
    `packages/radioskysims-core/src/radioskysims_core/db/aengine.py` (try/except
    do módulo) + `try: from .aengine import …` em `db/__init__.py`. `asyncpg`
    não está em `requirements*.txt`.
  - Decisão anotada: *"instalar asyncpg no ambiente e deixar padrão de uso do db
    como settings"*; **decidido 2026-09-03: `asyncpg` como extra opcional** (não
    no ambiente padrão) → (a) engine **lazy** (factory sob demanda) para `--help`
    e comandos sem banco rodarem limpos; (b) `asyncpg` em extra de DB (ex.:
    extra `db`/`postgres` documentado), não nos `requirements*.txt` padrão.
  - Verificação: `uv run radioskysims --help` sem stderr extra; notebooks sem a
    linha "asyncpg não disponível" no 1º run; `UserWarning` do pydantic
    silenciado na entrada de `tod export`.

- [~] **O1.2 · R2 — Alinhar default de `--telescope` ao settings distribuído**
  - **Status (2026-09-03):** `[radiotelescopes.default]` criado (cópia do `uirapuru`)
    em `settings.toml`, `config/examples/settings.toml` e `settings_fast.toml`; CLI
    `tod export` sem args resolve `default`. Pendente: migrar notebooks
    (`00_examples`/`02_sims`) do rótulo `uirapuru` → `default` (cosmético; perfil é
    cópia idêntica).
  - Causa atual: `--telescope default="default"` em
    `src/radioskysims/interfaces/cli/main.py`; `scripts/start_service.py` e
    `src/radioskysims/__init__.py::create_radiotelescope` com default `"default"`;
    `settings.toml` (raiz) e `config/examples/settings*.toml` só definem
    `[radiotelescopes.uirapuru]` (sem `default`).
  - **Decidido 2026-09-03**: criar `[radiotelescopes.default]` no `settings.toml`
    (raiz) e em `config/examples/settings*.toml` **copiando as informações do
    `uirapuru`**; a aplicação (CLI e notebook) **continua usando `default`** —
    não mudar o default do CLI para `uirapuru`. Conferir notebooks que chamam
    `create_radiotelescope("uirapuru")` → passar a usar `default` (ou sem args).
  - Verificação: `uv run radioskysims tod export` sem args passa no 1º uso.

- [x] **O1.3 · R3 — Nunca simular "em silêncio"** *(implementado 2026-09-03)*
  - **Status:** avisos em `execute_export_tod_command` (foreground/worker) quando a
    simulação fica sem satélites/fontes; `RadioSourcesManager.from_db` emite warning
    ao cair no fallback simulado; `sources_cli` com `logging.basicConfig(WARNING)`;
    teste de fallback adicionado (10 passed).
  - Causa atual: `--constellations` default `None` em `main.py` (help: *"Se
    omitido, sem satélites"*); fallback com `except Exception: pass` em
    `packages/radioskysims-sources/.../application/services/radio_sources_manager.py`
    (`from_db`); idem na fachada `src/radioskysims/interfaces/api/notebook.py`.
  - Decisão anotada: *"implementar warning quando não houver fontes/satélites"*;
    unificar saída máquina (`--output-format json` do umbrella vs `--json`).
  - Verificação: aviso em stderr quando a simulação for vazia e quando o
    fallback simulado for usado; um único mecanismo de saída JSON.

### Onda 2 — Consistência de CLIs, erros e entrypoints (M1–M5, R5, L1/L2)

- [x] **O2.1 · M1 — `help=` nas flags obrigatórias de `generate`/`survey`** *(implementado 2026-09-03)*
  - Anotado: *"implementar"*. Em `main.py` (`generate`, `survey`) flags sem
    `help=` (`--frequency-ghz`, `--nside`, `--survey-id`, `--base-path`, …).
  - Verificação: `radioskysims skymap generate --help` descreve todas as flags.

- [~] **O2.2 · M2 — GUI por um comando (`radioskysims gui`)**
  - **Status (2026-09-03):** subcomando `radioskysims gui` criado no parser do
    umbrella, delegando ao composition root `radioskysims.bootstrap.skymap_gui`
    (dashboard SkyMap) — 1 comando, help documentado. Pendente (trabalho
    contínuo): reduzir `presenters.py`/`controller.py`/`views.py` por caso de uso.
  - Anotado: *"implementar"*. Hoje só via `scripts/start_service.py` (usa
    `telescope="default"` → depende de O1.2). Expor `radioskysims gui` no
    umbrella (composition root do pacote simulation); documentar 1 comando;
    reduzir `presenters.py`/`controller.py`/`views.py` por caso de uso.
  - Verificação: `radioskysims gui` sobe o painel; `--help` indica o comando.

- [x] **O2.3 · M3 — Renomear `interfaces/api/` → `interfaces/notebook_api/`** *(implementado 2026-09-03)*
  - **Status:** diretório movido (`git mv` src+tests); imports/docstrings atualizados
    (código, testes, docs ativos); nota `nest_asyncio` na docstring da fachada; 9
    testes passando. Faltam apidocs `.rst` legados (regenerar na Fase de docs).
  - Anotado: *"implementar"* e *"notebook api deve mencionar necessidade de
    nest_asyncio"*. Renomear diretório/imports e ajustar docstrings e
    `docs/architecture/entrypoints.md`.
  - Verificação: imports atualizados; doc da fachada cita `nest_asyncio`.

- [x] **O2.4 · M4 — Unificar resolução de caminhos** *(implementado 2026-09-03)*
  - **Status:** helper `default_jobs_db()` no core resolve o banco de jobs na raiz
    do projeto (`get_project_root`); `DEFAULT_OUTDIR`/`_default_output_path` de
    `tod export` também resolvem na raiz. Aplicado em `export_tod`, `export_worker`,
    `jobs_cmd` e `JobHandle`. Validado rodando de subpasta (caminhos estáveis).
  - Anotado: *"introjetar resolução de caminhos e uniformizar"*. Outputs/jobs-db
    default relativos ao CWD (`data/TOD/…`, `sqlite:///data/jobs.db`, `plots/`)
    vs settings resolvidos pela raiz. Decidir regra única (raiz, como settings)
    e aplicar nos defaults; documentar exceções.
  - Verificação: rodar de qualquer diretório produz os mesmos caminhos.

- [x] **O2.5 · M5 — Fonte única de config de banco + pré-requisitos no `--help`**
  - **Status (2026-09-03):** `[DB]` do `settings.toml` como fonte única documentada;
    `DATABASE_URL` marcada como legado/ignorada em `credentials.env.example`;
    epílogo de pré-requisitos no `--help` de `tod export`.
  - Anotado: *"implementar"*. Conflito: `credentials.env.example` oferece
    `DATABASE_URL` que a engine **ignora** (usa `[DB]` do `settings.toml` em
    `aengine.py`/`engine.py`). Eleger `[DB]` como canônica e documentar
    `DATABASE_URL` como obsoleta; listar pré-requisitos por comando no `--help`
    (item 12 do diagnóstico).
  - Verificação: `--help` de cada comando lista pré-requisitos; uma fonte
    documentada.

- [>] **O2.6 · R4/L3 — Sanear `gnss4astro` (fora de escopo)**
  - Anotado: *"gnss4astro está com desenvolvimento próprio, não deve ter
    entrypoints próprios"*; L3 *"dev próprio"*. Log ruidoso no stdout, falha
    parcial como sucesso, caminho duplicado `data/rinex/data/rinex`, validação
    de data e `--dry-run` → mover para `barosil/gnsstools4astro`.

- [x] **O2.7 · R5 — Tratamento de erro padrão nos CLIs de pacote** *(implementado 2026-09-03)*
  - **Status:** `radioskysim-sources` com `--debug` e erro amigável em stderr
    (padrão do umbrella); exit code 1. gnss4astro segue fora de escopo (O2.6).
  - Anotado: *"uniformizar o tratamento de erro em todos os CLIs"*. Replicar o
    padrão do umbrella (mensagem amigável + `--debug` + exit codes 2–5) no
    `radioskysim-sources` (`packages/radioskysims-sources/.../interfaces/cli/
    sources_cli.py`, hoje sem try/except).
  - Verificação: falha de CLI de pacote não gera traceback cru.

- [x] **O2.8 · L1 — Avaliação de gramática/estilo entre CLIs (rich/click/typer)**
  - **Avaliação (2026-09-03):** manter **argparse** (subparsers aninhados do
    umbrella + tratamento de erro já padronizado na Onda 2). **Rich** pode entrar
    incrementalmente para saída colorida/tabelas/progresso (piloto: umbrella).
    **click/typer**: refactor de superfície nas 3 CLIs sem ganho funcional imediato
    → registrar como opção futura, não migrar agora.
  - Anotado: *"rich + click/typer"*. Avaliar adoção num piloto (umbrella) antes
    de generalizar; padronizar subcomandos e descrições.

- [x] **O2.9 · L2 — Fachada de notebook: retorno estruturado + aviso de satélites**
  - **Status (2026-09-03):** `run_simulation` foreground retorna `ExportResult`
    (dataclass `output`/`sidecar`); aviso de simulação vazia vem do R3 (O1.3).
    Testes export_tod + notebook_api: 19 passed.
  - Anotado: *"implementar uniformização dos outputs"*. `run_simulation`
    retorna `JobHandle | str` (foreground → string formatada). Retornar dataclass
    de resultado com metadados; default explícito de satélites com aviso (O1.3).
  - Verificação: notebooks consomem o retorno estruturado sem parse de string.

### Onda 3 — API pública de alto nível (R6 + "UX Changes")

- [ ] **O3.1 · R6 — Uniformização semântica e fachadas de pacote**
  - **Status (2026-09-03):** criados e expostos na raiz — `SatelliteOrchestrator`
    (sources; TLE via banco — smoke 32 GPS), `LocalSourcesOrchestrator` (sources;
    `create_sun`), `RadioSourcesOrchestrator` (sources; simulated/db/tap),
    `ContinuumSourceOrchestrator` (sources; injetável e `default()` com PySM3),
    `MapMakingOrchestrator` (simulation; injetável e `default()` com
    `HealpyBinnedMapMakerAdapter`), `SkyMapOrchestrator`+`Mask` (skymap),
    `SimOrchestrator` exposto na raiz (simulation), e tipos do kernel no
    `radioskysims_core`/hub (`FrequencyRange`/`TimeRange`/`Observer`).
    **Processor no core**: recomendação — migração incremental em F2/E5
    (`ResourceAwareProcessor` é módulo central com testes sensíveis; evitar
    refactor amplo na Onda 3). RINEX e conveniências (`SkyMap.from_sources`/
    `to_tod`, `Sim.to_map`) seguem pendentes.
  - Anotado: *"facilitar interface de usuário e uso de orchestrators e
    processors; processor implícito (dask localcluster) vs explícito
    (distributed/mpi/gpu); habilitar MPI para pysm3 e healpy"*.
  - **Avaliação 2026-09-03:** o bloco "UX Changes" é majoritariamente **não
    implementado** — é o desenho de uma API pública nova. Só `SimOrchestrator`
    existe. **Não existem** `SkyMapOrchestrator`, `SatelliteOrchestrator`,
    `LocalSourcesOrchestrator`, `RadioSourcesOrchestrator`,
    `ContinuumSourceOrchestrator`, `MapMakingOrchestrator` nem `Mask` exposto.
    Os `__init__.py` não exportam a API alvo (`radioskysims_sources` só exporta
    `SignalSource`; `radioskysims_core` só `__version__`; `radioskysims_skymap`
    exporta `SkyMap`/`NSide`/`SkyMapManager`; `radioskysims_simulation` exporta
    `Simulation`/`SimulationResult`/`TODSimulator`).
  - Ação em sub-etapas: (1) expor símbolos existentes por fachada de pacote;
    (2) criar orchestrators finos embrulhando os managers atuais
    (`RadioSourcesManager`, `Sun`, `SatelliteManager`, …); (3) definir a
    gerência de processador; (4) avaliar MPI para pysm3/healpy. Ver Anexo A.
  - **Decidido 2026-09-03 — ordem dos orchestrators:** Satellite → LocalSource →
    RadioSource → Continuum → MapMaking (fontes primeiro; skymap/waterfall
    depois, a definir).
  - **Decidido 2026-09-03 — Processor:** abstração (domínio/ports + services) no
    `radioskysims_core` com **implementações concretas em `infrastructure`** do
    core; `radioskysims-simulation` consome via porta (mover/refatorar o
    `ResourceAwareProcessor` hoje em `radioskysims-simulation/infrastructure`).
  - Verificação: os imports do Anexo A funcionam; notebooks/exemplos usam só a
    API pública; suite completa verde.

### Resumo executivo da auditoria (referência)

O projeto tem ótima base (erros tipados no umbrella, lifecycle de jobs, docs com
exemplos), mas o atrito concentra-se em (a) ruído de startup, (b) default de
telescope que não casa com o settings distribuído, (c) silêncios que mascaram
simulação vazia/fallback de banco e (d) 3 padrões de CLI diferentes sem
tratamento de erro uniforme. **O1.1–O1.3** atacam exatamente o que um usuário
novo encontra no primeiro minuto.

---

## 5. Plano — F2/F3: demais auditorias (`docs/audits/`)

### 5.1 F2 — Engenharia e dívida técnica herdada

Fontes: `docs/audits/engineering_audit_report.md` (2026-08-14) e
`docs/architecture/technical_debt.md` (baseline 07-16, revalidação 08-05). O
desacoplamento **moveu** o código e **superou** TD-004/007/008/009/010 (e o
exemplo `run_simulation` do README); os demais itens foram **transportados**
para os pacotes e seguem ativos.

**Fronteiras DDD (TD-001/002/003)**
- [x] **E1 — Domain → Application** (2026-09-03): `_compute_time_grid` → domínio
  (`simulation/domain/simulation/grids.py`); `GeometryProviderPort` canônico
  movido p/ `core/domain/geometry/interface.py` (`application/ports/geometry.py`
  reexporta por compat).
- [x] **E2 — Domain → Infrastructure** (2026-09-03): `BeamFactory` movido p/
  `beam/application/services/beam_factory.py` (sem uso de produção);
  `sources/domain/satellite/selector.py` opera por Protocol
  (`SatelliteElementsView`); `SignalFactory` (sources) recebe `psd_provider` por
  DI — composition roots injetam `GnsstoolsAnalyticPsdProvider`.
- [ ] **E3 — Application → Infrastructure** (2026-09-03, PARCIAL):
  `catalog_services.py` (sources) movido a ports + bootstrap — novo port
  `RadioSourceTrackProviderPort`; builders do simulation injeta o adapter
  `SkyfieldRadioSourceTrackProvider`. Processor/beam resolvers concretos de
  `sim_orchestrator.py`/`simulation_service.py` → consolidadas no E5 (migração
  do processor para o port do core + extração de resolvers de beam).
- [x] **E4 — Leak novo pós-decoupling** (2026-09-03): `radioskysims_sources`
  importava `radioskysims.application.ports`; agora usa
  `radioskysims_sources.application.ports.satellite` (contrato local). Meta
  reexporta por compat.

**Módulos grandes (TD-011/012, hotspots)**
- [ ] **E5 — Decompor hotspots de simulação** (2026-09-03, INÍCIO):
  `domain/simulation/{simulation.py, simulator, ...}` — helpers de grid
  (`_compute_time_grid`/`_compute_freq_mhz`/`_beam_fwhm_deg`) extraídos p/
  `domain/simulation/grids.py` (funções puras). Hotspots maiores
  (`sim_orchestrator.py` ~1620 l., `simulation.py` ~1570 l.,
  `simulation_service.py` ~1020 l., `domain/tod/simulator.py` ~890 l.,
  `infrastructure/processing/resource_processor.py` ~1230 l.) seguem como
  decomposição incremental (processor → port do core).
- [ ] **E6 — `src/radioskysims/visualization/waterfall.py`** (~1250 l.) fora das
  fases do decoupling — integrar ao `radioskysims-waterfall` (decisão do plano
  de decoupling) e decompor.
- [x] **E7 — `radioskysims_core/domain/common/models.py`** (2026-09-03): ~654 l.
  quebrado por conceito — `frequency.py` (FrequencyRange), `angles.py`
  (AngularRange/parse_angle), `time.py` (TimeRange), `observer.py` (Observer) e
  `_lazy.py` (helpers lazy); `models.py` virou shim reexport (TD-012).
- [ ] **E8 — `radioskysims_sources/infrastructure/db/satellite/
  satelliterepository.py`** (~896 l.) — TD-011.

**Drifts de API e legado no meta-pacote**
- [x] **E9 — TD-005** (2026-09-03): API HTTP legada removida
  (`interfaces/api/satellite_controller.py` — sem uso, chamava métodos
  inexistentes do `SatelliteService`, que expõe `get_all`/`get_by_ids`).
- [ ] **E10 — TD-006/TD-014**: `src/radioskysims/main.py` legado chama
  `SatelliteFactory(repository=…, spacetrack_client=…)` que a factory atual
  (só `repository`) não aceita → TypeError; remover/consolidar junto com
  `src/radioskysims/application/gain_panel.py`, shims
  `src/radioskysims/infrastructure/ports/{geometry,skymap}.py` e placeholder
  `domain/map/models.py`.
- [x] **E11 — TD-013** (2026-09-03): `src/radioskysims/interfaces/__init__.py`
  não reexporta mais o adapter concreto (`PySMSkyMapGeneratorAdapter`); fica só
  a docstring do pacote (consumidores importam do próprio pacote skymap).

**Qualidade estática (Sprint 1/2 da auditoria de engenharia)**
- [ ] **E12 — mypy**: `[tool.mypy]` strict configurado (cobre src/tests/packages), mas
  o executável está ausente no ambiente/CI → instalar e rodar (gate real).
- [ ] **E13 — ruff format**: ~153 arquivos a reformatar (`uv run ruff format
  --check src packages/*/src`) — aplicar de forma controlada por pacote.
- [x] **E14 — check_docs** (2026-09-03): `scripts/check_docs.py` agora varre o
  meta-pacote E também `packages/*/src` (423 arquivos; 650 issues — redução
  contínua).
- [ ] **E15 — Cobertura de hotspots**: `SimulationService` ~17%; entrypoints/GUI
  ~0% — orientar novos testes por risco.

**Superados (referência)** — TD-004, TD-007, TD-008, TD-009, TD-010; README
`run_simulation` → `run()`; afirmação "hexagonal" no README agora coerente;
consolidação de dependências em `pyproject.toml` (uv workspace + extras +
constraints).

#### Status de encerramento F2 (2026-09-03)

F2 **concluída nesta etapa** com os itens estruturais/fronteiras entregues;
os itens restantes ficam **registrados como pendentes/deferidos** (trabalho
contínuo pós-push — não bloqueiam o push).

- **Entregues ✅** — E1 (Domain→Application), E2 (Domain→Infrastructure),
  E4 (leak sources→meta), E7 (TD-012 split models core), E9 (TD-005), E11
  (TD-013), E14 (check_docs), E5-início (grids no domínio) e
  E3-catalog_services (port + bootstrap).
- **Pendentes/deferidos** — E3-simulation (processor/beam resolvers,
  consolidado com E5); E5 restante (hotspots grandes: `sim_orchestrator`,
  `simulation.py`, `simulator`, `resource_processor`); E6 (waterfall →
  `radioskysims-waterfall`); E8 (`satelliterepository` ~896 l.); E10
  (TD-006/014: `main.py` legado, `gain_panel`, shims, `domain/map`); E12 (mypy
  gate); E13 (ruff format ~153 arquivos); E15 (cobertura de hotspots).

### 5.2 F3 — Evoluções científicas e validações

Fontes: `docs/audits/funcionalidade_fisica_1.md`, `mapmaking_binned_scaling.md`,
`mapmaking_physical_feature_audit.md`, `neutral_hydrogen_physical_feature_audit.md`,
`tod_performance_audit_report.md`. Tipos: **CÓDIGO** (roadmap futuro) e
**VALIDAÇÃO** (requer execução/hardware).

**Mapmaking (não iniciado — roadmap futuro)**
- [ ] **C1 · Weighted binning / flagging / noise model** (`healpy_binned.py` hoje
  pesos iguais, sem flagging) — MM-FUTURE 01–03.
- [ ] **C2 · Destriping** (remoção de baselines temporais) — MM-FUTURE-04.
- [ ] **C3 · GLS (maximum-likelihood)** via `MapMakerPort` — MM-FUTURE-05.
- [ ] **C4 · Chunking temporal / paralelização por canal** (adapter materializa
  o eixo temporal com `np.asarray`) — MM-FUTURE 06–07.
- [ ] **C5 · Polarização Q/U** (hoje fixo `field="I"`) — MM-FUTURE-08.
- [ ] **C6 · Beam-aware / deconvolução** — MM-FUTURE-09.
- [ ] **C7 · Métricas de comparação mapa→reconstruído** (RMS/bias/espectro) —
  MM-FUTURE-10.
- [ ] **C8 · Pixels não observados**: propagar máscara/NaN em vez de preencher 0.

**Hidrogênio neutro**
- [ ] **C9 · Expor seleção do modelo HI (`lognormal`) em `SimOrchestrator.run()`**
  (hoje via settings/builders).
- [ ] **C10 · Correlação física entre canais de frequência/redshift (tomografia
  21 cm)** — hoje canais independentes com seed por canal.
- [ ] **C11 · Adapter FLASK/nbodykit** para campo de matéria.
- [ ] **C12 · Documentação científica do modelo HI** (hipóteses/equações).
- [ ] **C13 · Duplicidade de `SimulationContext`** (`application/services/
  sim_orchestrator.py` vs `domain/simulation/context.py`) — consolidar.

**Funcionalidade física**
- [ ] **C14 · Beam na rota de mapas** é só gaussiana (FWHM) via `hp.smoothing`;
  avaliar convolução com beam tabulado/medido.
- [ ] **C15 · Conversão de temperatura `uK_CMB → K`**: hoje fator escalar ×1e-6;
  avaliar conversão termodinâmica/RJ por frequência.
- [v] **C16 · Custo PySM3** — mitigado (cache multi-antena + persistência HDF5).
- [v] **C17 · Canais backend vs bins de `FrequencyRange`** — contrato documentado.

**Performance / validação**
- [ ] **V1 · Benchmark integrado 24 h** (satélites + radio/local sources, 2048
  canais) — VALIDAÇÃO externa; requer hardware com mais memória (PERF-05).
- [ ] **V2 · Mapmaking binned em configuração BINGO realista** (ruído,
  multi-frequência, varredura real) — VALIDAÇÃO (`mapmaking_binned_scaling` §13).
- [ ] **V3 · Monitorar benchmarks de regressão** (PERF-11) — localizar/criar
  `benchmarks/` pós-decoupling.
- [v] **V4 · Regressões de beam e fix de memória** (`sort`/`assume_sorted`,
  `sortby` redundante) — preservados nos pacotes com testes.

### 5.3 Governança das auditorias

- [x] **G1 — `docs/audits/modules/`**: **removido em 2026-09-03** (todos os 10
  arquivos). Decisão: remover — 9 eram placeholders vazios (0 bytes) e
  `beam_audit.md` (BEAM-001, já RESOLVIDO) iniciava com artefato de shell
  (`cat >> … <<'EOF'`). A auditoria por domínio passa a ser conduzida e
  atualizada pelo trabalho de consolidação deste documento (seções 5.1/5.2 por
  pacote), em vez de relatórios estáticos separados.
- [x] **G2 — `docs/audits/technical_debt_overview.md`** — **removido**
  (2026-09-03); o canônico é `docs/architecture/technical_debt.md`.
- [ ] **G3 — Atualizar `docs/architecture/entrypoints.md`** ao longo das ondas 1–2
  (caminhos pós-desacoplamento + pré-requisitos por comando).

---

## 6. Ordenação, gates e riscos

### 6.1 Ordem de implantação sugerida
1. **Onda 1 (UX)** — baixo risco, alto impacto no 1º uso.
2. **Onda 2 (UX)** + limpezas rápidas de F2 (E10/E11/E14) em paralelo.
3. **E9–E15** (drifts/qualidade) após ondas 1–2, por pacote, com testes verdes.
4. **Onda 3 (R6/API)** depois que a Onda 2 estabilizar a superfície dos pacotes.
5. **Fronteiras DDD (E1–E4)** incrementalmente junto a refactors de simulação
   (não como campanha isolada).
6. **F3 (C1–C15)** é roadmap futuro/científico (agendar por prioridade de
   física); **V1/V2** dependem de hardware.

### 6.2 Gates por onda
- **Onda 1**: `--help` limpo; `tod export` sem args OK; warnings de simulação
  vazia/fallback visíveis (stderr).
- **Onda 2**: `--help` completo; `radioskysims gui` funciona; imports sem
  `interfaces/api`; caminhos determinísticos; uma fonte de DB; CLIs de pacote
  sem traceback cru.
- **Onda 3**: imports do Anexo A funcionam; notebooks/exemplos usam só a API
  pública; suite completa verde.
- **Geral**: `uv run pytest tests` verde a cada etapa (sem mudança de
  comportamento científico); `uv run ruff check src packages/*/src` verde.

### 6.3 Riscos
- Refatorações em `sim_orchestrator`/`simulation.py`/`mapmaking` têm alto risco
  de regressão → extrações pequenas cobertas por teste (recomendação da
  auditoria).
- Mudar default de `--telescope` ou de caminhos pode quebrar exemplos existentes
  → revisar `docs/source/quickstart.md` e notebooks juntos.
- Onda 3 cria API pública nova → requer depreciação da API interna e atualização
  de exemplos; decidir se o re-export é no meta-pacote `radioskysims` (hub) ou
  por pacote.

---

## 7. Decisões (registro) e pendências

**Decididas em 2026-09-03**
1. **Default de telescope (R2)** — criar `[radiotelescopes.default]` copiando as
   informações do `uirapuru` (settings raiz + `config/examples`); a aplicação
   (CLI e notebook) usa `default`.
2. **asyncpg (R1)** — em **extra opcional** (não no ambiente padrão); engine
   async *lazy* no core.
3. **Ordem dos orchestrators (Onda 3/R6)** — Satellite → LocalSource →
   RadioSource → Continuum → MapMaking.
4. **Processor** — contrato (domínio/ports + services) no `radioskysims_core`;
   implementações em `infrastructure` do core; simulation consome via porta.
5. **`docs/audits/modules/`** — **removido** (todos os arquivos); a auditoria
   por domínio passa a ser conduzida por este plano de consolidação (G1).

**Ainda pendentes**
- Re-export da fachada de API: no meta-pacote `radioskysims` (hub) ou por
  pacote? (Onda 3)
- `visualization/waterfall.py`: integrar ao `radioskysims-waterfall` já ou
  manter no meta-pacote (E6)?
- C14/C15 (funcionalidade física): incluir no ciclo atual ou registrar como
  backlog científico?

---

## Anexo A — API alvo ("UX Changes") com status por símbolo (2026-09-03)

Legenda: ✅ importável hoje · 🟡 existe mas não exposto na fachada pública ·
❌ não existe (criar) · ➡️ decisão de design preservada do original.

```python
# ── Meta-pacote (radioskysims / src/radioskysims/__init__.py) ──────────────
from radioskysims import create_radiotelescope   # ✅ existe
from radioskysims import FrequencyRange, TimeRange  # ✅ reexportados (hub) 2026-09-03
from radioskysims import Observer                    # ✅ reexportado (hub) 2026-09-03
from radioskysims import Config                      # ✅ existe

# ── radioskysims_core ─────────────────────────────────────────────────────
from radioskysims_core import FrequencyRange, TimeRange, Observer  # ✅ expostos 2026-09-03
# (Exceptions/NSide etc. continuam em radioskysims_core.domain.common)

# ── radioskysims_sources ──────────────────────────────────────────────────
from radioskysims_sources import SignalSource        # ✅ existe
# SatelliteOrchestrator / LocalSourcesOrchestrator / RadioSourcesOrchestrator /
#   ContinuumSourceOrchestrator  → ✅ criados 2026-09-03 (embrulham managers);
#      integração RINEX do SatelliteOrchestrator pendente (via gnsstools4astro)
# ➡️ RINEX/TLE devem vir do orchestrator:
#    SatelliteOrchestrator.create_from_constellation(method="RINEX")  (ou from_RINEX)
# ➡️ sun = LocalSourcesOrchestrator.create_sun(); sun.track(timerange).view(); sun.flux()
# ➡️ usuário não deve conhecer build_repositories / bootstrap.builders

# ── radioskysims_skymap ───────────────────────────────────────────────────
from radioskysims_skymap import SkyMap, NSide, SkyMapManager  # ✅ existe
from radioskysims_skymap import SkyMapOrchestrator, Mask  # ✅ criados 2026-09-03
#   SkyMapOrchestrator: from_noise/from_coefficients/load/download/apply/
#   smooth/rotate/save/view/statistics (encadeável). Pendentes: from_sources
#   (composição com sources) e to_tod (projeção no simulation).
# ➡️ usuário não deve conhecer factory/providers (pysm|healpy)/visualizer

# ── radioskysims_simulation ───────────────────────────────────────────────
from radioskysims_simulation import Simulation, SimulationResult, TODSimulator  # ✅ existe
from radioskysims_simulation import MapMakingOrchestrator  # ✅ criado 2026-09-03 (injetável)
from radioskysims_simulation import SimOrchestrator  # ✅ exposto na raiz (lazy) 2026-09-03
# ➡️ simplificar chamada: SimOrchestrator(...).to_map() (pendente)

# ── radioskysims_waterfall ────────────────────────────────────────────────
from radioskysims_waterfall import (   # ✅ existe (raiz do pacote)
    Waterfall, SED, WaterfallPipeline, load_waterfall,
)
# Waterfall.load()/view()/apply()/save()/properties() → conferir cobertura da API

# ── radioskysims_viz ──────────────────────────────────────────────────────
from radioskysims_viz import save_figure, save_plot   # ✅ existe
# ➡️ avaliar se os dois métodos são necessários (decisão do original)

# ── gnsstools4astro ───────────────────────────────────────────────────────
# ➡️ FORA DE ESCOPO (repo próprio). RINEX/TLE entram via SatelliteOrchestrator.
```

Notas do alvo original preservadas: *"O usuário não deve saber como construir
repositórios"*; *"avaliar se é necessário dois métodos"* (viz); *"RINEX ou TLE
devem vir do orchestrator"*; *"User should not know about this"* (factory,
providers, paths, dotenv, db engine); *"Podemos simplificar a chamada"*
(`SimOrchestrator` → `to_map()`).

## Histórico do documento

- 2026-09-02 — Auditoria de UX dos entrypoints (diagnóstico e recomendações).
- 2026-09-03 — Revisão dos comentários + consolidação em plano de implantação
  (F1/F2/F3), status verificados pós-desacoplamento; gnss4astro fora de escopo.
- 2026-09-03 (b) — Decisões registradas: default de telescope copia `uirapuru`;
  `asyncpg` em extra; ordem de orquestradores Satellite→LocalSource→RadioSource→
  Continuum→MapMaking; processor no core (infrastructure no core); remoção de
  `docs/audits/modules/` (auditoria por domínio segue neste plano).
- 2026-09-03 (c) — **Onda 1 implementada**: O1.1 (engine async lazy + `Tracks`
  `PrivateAttr` + extra `asyncpg`), O1.2 (perfil `default` nos settings; notebooks
  pendente), O1.3 (avisos de simulação vazia/fallback + teste). Removidos arquivos
  vazios de `docs/audits/` (G2 e evidência).
- 2026-09-03 (d) — **Onda 2 (parte 1)**: notebooks uniformizados para o perfil
  `default`; O2.1 (help flags), O2.3 (rename `interfaces/api` → `notebook_api`),
  O2.5 (fonte única de DB + pré-requisitos no help), O2.7 (erro padrão no
  `sources_cli`), O2.9 (`ExportResult` na fachada). Pendentes: O2.2 (GUI), O2.4
  (caminhos), O2.8 (rich/typer).
- 2026-09-03 (e) — **Onda 2 (parte 2)**: O2.4 (M4 — caminhos default de output
  TOD/jobs-db resolvidos na raiz do projeto via `default_jobs_db()`/`get_project_root`).
  Pendentes: O2.2 (GUI), O2.8 (rich/typer).
- 2026-09-03 (f) — **Onda 2 (parte 3)**: O2.2 — entrypoint `radioskysims gui`
  (delega ao `bootstrap.skymap_gui`; decomposição dos módulos de GUI fica como
  trabalho contínuo). O2.8 — avaliação rich/typer registrada (manter argparse;
  rich incremental opcional). Onda 2 fechada (O2.1–O2.9).
- 2026-09-03 (g) — **Onda 3 (fachadas, parte 1)**: criados e expostos na raiz
  `SatelliteOrchestrator`, `LocalSourcesOrchestrator`, `RadioSourcesOrchestrator`,
  `ContinuumSourceOrchestrator` (sources) e `MapMakingOrchestrator` (simulation).
  Testes: sources 13 passed, simulation 3 passed. Pendente: fachadas de
  core/skymap, hub no meta, montagens default e integração RINEX.
- 2026-09-03 (h) — **Onda 3 (fachadas, parte 2)**: `SkyMapOrchestrator`+`Mask`
  (skymap), `SimOrchestrator` exposto (simulation), `FrequencyRange`/`TimeRange`/
  `Observer` no `radioskysims_core` e reexportados no hub `radioskysims`. Testes:
  core 104, skymap 6. API pública do Anexo A quase completa (faltam montagens
  default, RINEX e conveniências de integração).
- 2026-09-03 (i) — **Onda 3 (fachadas, parte 3)**: fábricas `default()` em
  `ContinuumSourceOrchestrator` (PySM3) e `MapMakingOrchestrator`
  (`HealpyBinnedMapMakerAdapter`). Processor no core → migração incremental em
  F2/E5 (módulo central). RINEX e conveniências pendentes.