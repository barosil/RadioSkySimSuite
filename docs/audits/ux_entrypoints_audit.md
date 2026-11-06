# Auditoria de UX dos Entrypoints — RadioSkySimSuite

**Data:** 2026-09-02
**Escopo:** `src/radioskysims` (umbrella) + CLIs de pacote (`radioskysim-sources`,
`gnss4astro`) + fachada de notebook + GUI. Análise de **experiência do usuário**
(facilidade de uso, consistência, feedback, pré-condições de primeiro uso).

> Complementa o inventário de entrypoints em `docs/architecture/entrypoints.md`
> (2026-09-01). Aqui o foco é *como o usuário vê/opera* cada ponto de entrada e
> o que gera atrito. Baseado em execução real dos comandos e leitura do código.

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

## 4. Recomendações priorizadas

### Alto impacto
- **R1 — Remover ruído de startup do umbrella**: engine async *lazy* (ou
  protegida por env) e silenciar o `UserWarning` do pydantic na entrada, para
  que `--help` e comandos sem banco rodem limpos (`aengine.py:75-81`,
  `db/__init__.py`).
- **R2 — Alinhar o default de `--telescope` ao settings distribuído**: mudar o
  default para o perfil presente (`uirapuru`) ou adicionar
  `[radiotelescopes.default]` (alias) no `settings.toml` raiz; corrigir
  `scripts/start_service.py` na mesma linha. Hoje `tod export` sem args e a GUI
  falham no primeiro uso.
- **R3 — Nunca simular "em silêncio"**: aviso explícito quando não houver
  satélites/fontes (`tod export`/`run_simulation`) e quando `--source db` cair
  no catálogo simulado (`radio_sources_manager.py:132`); oferecer um único
  mecanismo de saída JSON (unificar `--output-format json` e `--json`).
- **R4 — Sanear o `gnss4astro` para humanos**: `--log-level WARNING` default (ou
  logs estruturados para stderr e resultado humano para stdout), retornar
  exit ≠ 0 em falha parcial de download e corrigir o caminho duplicado do
  `outdir`.
- **R5 — Tratamento de erro padrão nos 3 CLIs**: replicar o padrão do umbrella
  (mensagem amigável + `--debug`) em `radioskysim-sources` e `gnss4astro`.

### Médio impacto
- **M1** — Preencher `help=` nas flags obrigatórias de `generate`/`survey`.
- **M2** — Expor a GUI pelo umbrella (`radioskysims gui`) e documentar 1
  comando; reduzir `presenters.py` por caso de uso.
- **M3** — Renomear `interfaces/api/` → `interfaces/notebook_api/` (eliminar
  ambiguidade REST).
- **M4** — Unificar resolução de caminhos (outputs/jobs-db default relativos à
  raiz, como settings) ou documentar claramente a regra CWD.
- **M5** — Definir uma única fonte de config de banco (`settings.toml [DB]` vs
  `DATABASE_URL`) e listar pré-requisitos por comando no `--help`.

### Baixo impacto
- **L1** — Padronizar gramática/estilo entre as 3 CLIs (e avaliar `rich`).
- **L2** — Fachada de notebook: retornar dataclass de resultado (não
  `JobHandle | str`) e default explícito de satélites com aviso.
- **L3** — `gnss4astro download`: validar data no parser com erro amigável e
  oferecer `--dry-run`/contagem antes de baixar.

---

## 5. Resumo executivo

O projeto tem ótima base (erros tipados no umbrella, lifecycle de jobs, docs com
exemplos), mas o atrito concentra-se em (a) ruído de startup, (b) default de
telescope que não casa com o settings distribuído, (c) silêncios que mascaram
simulação vazia/fallback de banco e (d) 3 padrões de CLI diferentes sem
tratamento de erro uniforme. Os itens **R1–R3** atacam exatamente o que um
usuário novo encontra no primeiro minuto.
