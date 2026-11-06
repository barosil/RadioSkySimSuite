# Fase 4 — `radioskysims-sources` + `radioskysims-radiotelescope` + `gnsstools4astro`

## Objetivo

Extrair as fontes de sinal, o radiotelescópio e o pacote GNSS como membros do
workspace, dependendo de `radioskysims-core` (+ `radioskysims-skymap` para
sources). Os pacotes leves continuam sem vazar dependências pesadas.

## `radioskysims-sources`

Movido para `packages/radioskysims-sources/`:
- `domain/{satellite,localsources,radiosources,cosmology,catalog,signal,source}`
- `domain/signal_source.py` + `domain/signal_source_group.py` (protocolo
  unificado `SignalSource` — fronteira sources↔simulation)
- `application/services/{satellite_service,catalog_services,local_sources_service,source_assembler,satellite_manager}.py`
- `application/radiosources_use_cases.py`, `application/cosmology/`,
  `application/skymap/generate_continuum.py`
- `application/ports/{radiosources,localsources,satellite,cosmology}.py`
- `infrastructure/external/*` (SpaceTrack, Solar Flux, catálogos), `infrastructure/cosmology/`,
  `infrastructure/db/{radiosources,solar_flux,satellite,signal}*`,
  `infrastructure/ports/{radiosources,localsources}.py`
- `interfaces/{gui/satellite_panel,api/satellite_controller,cli/satellite_cli}.py`

Dependências (pesadas, declaradas corretamente): `pyccl`, `camb`, `healpy`,
`astroquery`, `pyvo`, `georinex`, `h5py`, `dask`, `sgp4`, `httpx`, + `core` + `skymap`.

## `radioskysims-radiotelescope`

Movido para `packages/radioskysims-radiotelescope/`:
- `domain/radiotelescope/*` (pointing, antena, backend/spectrometer, specs)
- `application/radiotelescope_panel.py` — **refatorado**: `RadiotelescopePanel(PanelApplication)`
- `application/services/radiotelescope_services.py`

Dependências: `numpy`, `pydantic`, `panel`, `radioskysims-core`, `radioskysims-viz` (leve).

Nota: `build_radiotelescope_from_settings` permanece no core (`config.config_loader`)
com imports lazy apontando para `radioskysims_radiotelescope` (a migração completa
do corpo da função para o pacote radiotelescope fica para a Fase 7, junto com o
refactor do `ConfigPort`).

## `gnsstools4astro`

Movido de `src/gnsstools4astro/` para `packages/gnsstools4astro/` como membro do
workspace (com pyproject próprio). As strings de integração lazy
(`tle_tracks.py`) atualizadas para `radioskysims_core` / `radioskysims_sources`.

## Shims de compatibilidade (mantidos até Fase 7)

Todos os caminhos antigos (`radioskysims.domain.satellite`, `domain.radiotelescope`,
`application.services.satellite_service`, `infrastructure.external.*`,
`application.skymap.generate_continuum`, `interfaces.gui.satellite_panel`, etc.)
reesportam dos novos pacotes. 39 arquivos de consumidores reescritos (sources) +
4 (radiotelescope).

## Testes movidos (junto com o código)

- sources (27): `tests/domain/{satellite,radiosources,cosmology,signal,source}/*`,
  `tests/infrastructure/cosmology/*`, `tests/application/cosmology/*`,
  `tests/application/ports/test_cosmology.py`,
  `tests/application/services/skymap/test_generate_continuum.py`,
  `tests/test_satellite.py`, `tests/test_space_track_client.py`
- gnss (6): `tests/test_gnss_*.py` + `tests/conftest.py` (fixtures RINEX)
- radiotelescope: sem testes diretos (coberto via simulation nas fases seguintes)

Ajustes:
- sources tests usam árvore de pacote com `__init__.py` (modo de import padrão —
  resolve colisão de nomes e o problema de backend anyio).
- gnsstools4astro tests ganharam conftest próprio com as fixtures de amostra RINEX.

## Verificação (gate da fase)

```bash
uv run --package radioskysims-sources pytest packages/radioskysims-sources/tests   # → 165 passed, 1 xfailed
uv run --package gnsstools4astro pytest packages/gnsstools4astro/tests              # → 21 passed, 9 skipped (dados RINEX ausentes)
uv run pytest tests -q -m "not integration" --ignore=tests/performance              # → 472 passed
```

- Isolamento (uv.lock): sources declara as pesadas; radiotelescope e gnss leves.
- Todos os pacotes (core/viz/beam/skymap) permanecem verdes.

## Commit

`09d78a6` — "Fase 4: radioskysims-sources + radioskysims-radiotelescope + gnsstools4astro"

## Submódulos

Registrados no commit `b5373d2` — cada pacote virou submódulo apontando para o
repo próprio no GitHub (`barosil/<pacote>`).

> **Nota pós-montagem**: o disco foi remontado (I/O errors no caminho antigo).
> O workspace passou a `/media/lbarosi/barosi_portable1/RadioSkySimSuite` e o
> venv foi recriado para regenerar shebangs/caminhos.
