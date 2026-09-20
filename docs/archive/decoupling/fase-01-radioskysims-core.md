# Fase 1 — Kernel compartilhado: `radioskysims-core`

## Objetivo

Extrair do monólito o kernel compartilhado em `packages/radioskysims-core/`
(distribuição `radioskysims-core`, import `radioskysims_core`), mantendo
**shims de compatibilidade** nos caminhos antigos e a suite **verde** em cada
etapa.

## O que foi movido

| Módulo original (`src/radioskysims/`) | Pacote core |
|---|---|
| `paths.py` | `radioskysims_core.paths` (generalizado: `PathManager`, detecção por marcadores) |
| `infrastructure/config/config_loader.py` | `radioskysims_core.config.config_loader` |
| `infrastructure/config/settings.py` | `radioskysims_core.config.settings` |
| `infrastructure/config/settings.toml` | `radioskysims_core.config/settings.toml` |
| `infrastructure/logging_config.py` | `radioskysims_core.logging_config` |
| `infrastructure/db/engine.py` | `radioskysims_core.db.engine` |
| `infrastructure/db/aengine.py` | `radioskysims_core.db.aengine` |
| `domain/common/*` | `radioskysims_core.domain.common` |
| `domain/geometry/*` | `radioskysims_core.domain.geometry` |
| `domain/tracks/*` | `radioskysims_core.domain.tracks` |
| `application/ports/geometry.py` | `radioskysims_core.application.ports.geometry` |
| `infrastructure/external/skyfield_loader.py` | `radioskysims_core.skyfield_loader` (loader genérico de efemérides) |

**Novos** (requisitos do plano):
- `radioskysims_core.config.ports.ConfigPort` (ABC) + `config.adapters.TomlConfigAdapter`.
- `radioskysims_core.db.models` — registro de schema SQLModel **plugável**
  (`register_model_module` / `load_registered_models`); cada pacote de domínio
  registra suas tabelas.
- `radioskysims_core.monitor.SystemMonitor` — detecção de CPU/memória/disco
  extraída do `ResourceAwareProcessor` (a parte de chunking/dask fica na
  simulação, Fase 5).
- `radioskysims_core.progress` — indicador de progresso uniforme (requisito
  "Messages" do `.prompts/decoupling.md`).

## Decisões de isolação (auditoria)

- **`config_loader`**: os imports de `domain.radiotelescope.*` viraram **lazy**
  (dentro de `build_radiotelescope_from_settings`) — o núcleo é importável sem
  radiotelescope. A função em si migra para o pacote radiotelescope na Fase 4.
- **`resource_processor.py`** ficou no monólito (vai para `radioskysims-simulation`
  na Fase 5) — importa `domain.signal_source`/`domain.simulation` em runtime.
- **`infrastructure/db/models.py`/`init_db.py`** ficaram no monólito (agregam
  tabelas de beam/sources/simulation); o core expõe a base plugável.
- **`application/ports/__init__.py`** (agregador global) permanece no monólito;
  o port de geometry passa a vir do core.
- **`domain/common/exceptions.SkyMapError`** usa fallback local (núcleo não
  depende de skymap); reconciliação na Fase 3.
- **`paths.get_project_root()`** agora detecta a raiz por marcadores
  (`pyproject.toml`/`.git`) — independe da localização física do módulo.

## Shims de compatibilidade (mantidos até a Fase 7)

Todos os caminhos antigos reexportam do core, marcados deprecated:
`radioskysims.paths`, `radioskysims.infrastructure.config.*`,
`radioskysims.infrastructure.logging_config`,
`radioskysims.infrastructure.db.engine`/`aengine`,
`radioskysims.domain.{common,geometry,tracks}.*`,
`radioskysims.application.ports.geometry`,
`radioskysims.infrastructure.external.skyfield_loader`.

Imports dos consumidores do monólito (67 arquivos) reescritos para
`radioskysims_core.*`.

## Testes movidos (junto com o código)

`packages/radioskysims-core/tests/`:
- `domain/common/*` (AngularRange, FrequencyRange, ScienceValidator, TimeRange)
- `domain/test_tracks.py` + `track_fixtures.py`
- `domain/tracks/{conftest,test_track_factory}.py` (fixtures `numpy_ds`/`dask_ds`)
- `test_logging_integration.py`
- `core/` — novos testes das abstrações (ConfigPort, SystemMonitor, progress,
  PathManager, registro de modelos DB)

## Verificação (gate da fase)

```bash
uv run --package radioskysims-core pytest packages/radioskysims-core/tests
# → 88 passed, 3 skipped (skips = API legada do TrackFactory, igual ao original)

uv run pytest tests -q -m "not integration" --ignore=tests/performance
# → 1037 passed, 12 skipped, 1 xfailed

uv tree --package radioskysims-core   # SEM panel/healpy/pyccl/camb/astroquery ✔
```

- `uv sync --package radioskysims-core` (instalável isolado).
- Import lazy do `gnsstools4astro` (`radioskysims.infrastructure.db.engine`)
  continua funcionando via shim.

## Nota de decisão

O plano citava core "sem dask", mas `domain/geometry` e `domain/tracks`
(que o próprio plano aloca ao core) usam `dask`/`xarray` — mantivemos `dask`
como dependência leve do core (sem binários pesados) e documentamos a decisão.

## Commit

`1992940` — "Fase 1: radioskysims-core — kernel compartilhado extraído do monólito"
