# Logging — RadioSkySimSuite

**Data:** 2026-09-01

## 1. Padrão adotado

O projeto usa **logging estruturado em JSON** sobre a `stdlib logging`,
implementado em `radioskysims_core.logging_config`:

- `JSONFormatter` — formata cada `LogRecord` como um objeto JSON
  (`timestamp` ISO em UTC, `level`, `logger`, `event`, contexto extra);
  aceita tanto mensagens string simples quanto `dict` estruturado.
- `StructuredLogger` — wrapper fino sobre `logging.Logger` com métodos
  `debug/info/warning/error/critical/exception(event: str, **kwargs)`, que
  serializam `event` + kwargs como JSON.
- `configure_logging(log_level="INFO", log_dir="logs", enable_file=True)` —
  ponto único de configuração: define o `root_logger`, adiciona
  `StreamHandler` (stdout) e opcionalmente `FileHandler`
  (`logs/radioskysim_<timestamp>.json`), e silencia loggers verbosos de
  terceiros (`sqlalchemy.engine`, `matplotlib`, `skyfield`, `scipy`).
- `get_logger(name) -> StructuredLogger` — fábrica usada nos módulos que
  adotam o padrão estruturado.

Exemplo de uso (do docstring de `logging_config.py`):

```python
from radioskysims_core.logging_config import get_logger

logger = get_logger("radioskysims.beam")
logger.info("beam_created", beam_id="BEAM001", frequency_ghz=10.5)
logger.warning("beam_interpolation_slow", duration_ms=2500)
logger.error("beam_load_failed", path="/path/to/beam", reason="file_not_found")
```

`configure_logging()` deve ser chamado **uma única vez** no início da
aplicação (`main.py`, `conftest.py`, composition root) — nunca em módulos de
biblioteca.

## 2. Onde a configuração é montada

`build_logging` (builder de composition root) existe em **três lugares**:

- `radioskysims_core/bootstrap/builders.py` — implementação real
  (`configure_logging` + wiring de contexto);
- `radioskysims_simulation/bootstrap/builders.py` — re-exporta/usa o builder
  do core no fluxo de simulação;
- `src/radioskysims/bootstrap/builders.py` — re-exporta
  `build_logging` do `radioskysims-core` (Fase 5, ver `architecture.md §6`).

Não há, portanto, configuração de logging duplicada no caminho principal —
apenas re-exportação através da cadeia de composition roots.

## 3. Categorização de eventos

`bounded_contexts.md` declara como regra transversal: *"Logs estruturados
JSON com eventos categorizados (`http`, `io`, `db`)"*. Na prática, isso
aparece hoje principalmente em `radioskysims_core.db.engine`, que importa
`log_db_event` de `logging_config` para eventos de banco (ex.: criação de
engine, inspeção de tabelas). Eventos `http`/`io` equivalentes (para
downloads via `httpx`, leitura/escrita de HDF5/Zarr) **não foram
confirmados de forma consistente** nesta auditoria — recomenda-se auditar
se `infrastructure/external/*` (downloaders TAP/SpaceTrack/HiPS) usa
`get_logger`/eventos categorizados ou `print`/`logging` puro.

## 4. Adoção real — inconsistência a corrigir

Varredura estática (`grep`) sobre `src` + `packages/*/src`:

| Padrão | Módulos (arquivos únicos) |
|---|---:|
| `get_logger(...)` (estruturado, padrão do projeto) | 15 |
| `logging.getLogger(__name__)` (stdlib puro) | 31 |

**Leitura**: a maioria dos módulos que fazem logging ainda usa
`logging.getLogger(__name__)` puro em vez do `StructuredLogger` — os logs
desses módulos não seguem o padrão JSON estruturado com `event`/kwargs
declarado como convenção do projeto. Isso não quebra nada (ambos escrevem
via o mesmo `root_logger` e herdam o `JSONFormatter` configurado
globalmente — o formatter trata `record.msg` string como `{"event": msg}`),
mas perde a estruturação de campos extras (kwargs) que `StructuredLogger`
oferece.

`ruff` já sinaliza parte do problema: `G` (`flake8-logging-format`) está
habilitado em `extend-select`, mas não impõe o uso de `get_logger` — apenas
o formato de string de interpolação em chamadas de logging padrão.

## 5. Duplicação intencional em `gnsstools4astro`

`gnsstools4astro/infrastructure/logging_config.py` é uma **cópia
autocontida** do mesmo desenho (`JSONFormatter` + `StructuredLogger`),
com o comentário explícito *"padrão radioskysims, autocontido"*. Isso não é
acidental: `gnsstools4astro` **não depende de `radioskysims-core`** em seu
`pyproject.toml` (é utilizável como ferramenta standalone fora da suíte),
então duplicar o módulo de logging evita puxar o kernel inteiro como
dependência.

**Trade-off documentado**: duplicação de ~2 módulos pequenos (formatter +
logger) em troca de um pacote GNSS verdadeiramente standalone. Aceitável,
desde que as duas cópias não divirjam silenciosamente — recomenda-se um
teste de contrato simples que compare a saída JSON de ambas as
implementações para o mesmo input.

## 6. Segurança

- `radioskysims_core.db.engine.Database.__repr__` sanitiza a URL de conexão
  antes de expor/logar (`remove credenciais` via `url.split("@")[-1]`) — boa
  prática, evita vazar senha em log de erro/debug.
- `configure_logging` silencia `sqlalchemy.engine` para `WARNING` por
  padrão — reduz risco de logar SQL com parâmetros sensíveis em `INFO`/
  `DEBUG` acidentalmente, mas **não impede** um `logger.debug(query)`
  explícito em código de aplicação.
- **Achado (corrigido nesta rodada)**: `Database._create_engine()` logava a
  URI de conexão completa (com senha em texto plano) em nível `DEBUG` —
  como `enable_file=True` é o padrão de `configure_logging`, isso persistia
  a credencial em `logs/*.json` quando o nível DEBUG estava ativo. O log
  agora usa apenas `self.db` (host:port, sem credenciais). Detalhamento em
  [`persistence.md §2.1`](persistence.md#21-achado-de-segurança--uri-completa-em-log-debug-corrigido).

## 7. Recomendações

1. Migrar os 31 módulos que usam `logging.getLogger(__name__)` puro para
   `get_logger(__name__)` nos pontos de log realmente estruturados
   (eventos de negócio), mantendo `logging` puro apenas para mensagens de
   biblioteca genéricas (ex.: warnings de terceiros).
2. Confirmar/uniformizar a categorização `http`/`io`/`db` de eventos nos
   adapters de `infrastructure/external/*` de cada pacote.
3. Adicionar teste de contrato comparando a saída de
   `radioskysims_core.logging_config.JSONFormatter` e
   `gnsstools4astro.infrastructure.logging_config.JSONFormatter` para o
   mesmo `LogRecord`, evitando divergência silenciosa entre as duas cópias.
4. Documentar explicitamente em `AGENTS.md`/`architecture.md` que
   `gnsstools4astro` é o único pacote com módulo de logging duplicado
   (por design), para não ser confundido com dívida técnica acidental em
   futuras auditorias.
5. ~~Corrigir o vazamento de credencial em log DEBUG~~ — **corrigido**
   nesta rodada (ver §6 e `persistence.md §2.1`).
