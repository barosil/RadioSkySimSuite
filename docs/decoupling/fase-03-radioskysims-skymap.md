# Fase 3 — `radioskysims-skymap`

## Objetivo

Extrair o domínio de SkyMap (e sua infraestrutura) para um **pacote dedicado**
`radioskysims-skymap` (import `radioskysims_skymap`), dependendo apenas do
`radioskysims-core`. Evita inflar o core com `healpy` e evita que `simulation`
dependa de `sources` só para usar o tipo `SkyMap`.

## O que foi movido

| Módulo | Pacote skymap |
|---|---|
| `domain/skymap/*` (SkyMap, NSide, SkyMapDataset, mask, operations, analysis, factory, exceptions) | `radioskysims_skymap.domain.skymap` |
| `application/skymap/{__init__,analyze,generate,dto,ports}.py` | `radioskysims_skymap.application.skymap` |
| `application/ports/skymap.py` + `skymap_repository.py` | `radioskysims_skymap.application.ports.*` |
| `infrastructure/skymap/*` (healpy_*, providers, adapters, io, repository, telemetry, utils, visualization) | `radioskysims_skymap.infrastructure.skymap` |
| `infrastructure/db/skymap_models.py` | `radioskysims_skymap.infrastructure.db.skymap_models` |

**Não movidos (permanecem na raiz):**
- `application/skymap/generate_continuum.py` — usa `domain.radiosources.continuum`
  (→ Fase 4, `radioskysims-sources`).
- `infrastructure/skymap/tod_projector.py` — usa `domain.tod.map_projector`
  (→ Fase 5, `radioskysims-simulation`).

## Ajustes

- Import de `SkyMapRecord` no `radioskysims.infrastructure.db.__init__` aponta
  para o pacote skymap.
- `init_db.py` importa `skymap_models` do pacote skymap.
- Shims de compatibilidade: `radioskysims.domain.skymap.*`,
  `radioskysims.application.skymap.*` (exceto `generate_continuum`), etc.
- As referências a `tod_projector` foram **protegidas** na reescrita (ficam na raiz).

## Dependências

`numpy`, `astropy`, `xarray`, `healpy`, `h5py`, `pysm3`, `radioskysims-core`.
**Sem** `astroquery`, `pyccl`, `camb`, `dask`, `panel`.

## Testes movidos (junto com o código)

`packages/radioskysims-skymap/tests/`:
- `skymap/*` (16 arquivos)
- `infrastructure/skymap/{io,repository,test_telemetry}.py`
- `application/services/skymap/{test_dto,test_generate,test_ports}.py`
- Ficaram na raiz: `test_tod_projector.py`, `test_generate_continuum.py`

## Verificação (gate da fase)

```bash
uv run --package radioskysims-skymap pytest packages/radioskysims-skymap/tests
# → 325 passed

uv run pytest tests -q -m "not integration" --ignore=tests/performance
# → 658 passed, 12 skipped, 1 xfailed
```

- Isolamento (uv.lock): astropy, h5py, healpy, numpy, pysm3, core, xarray —
  sem astroquery/pyccl/camb/dask/panel.

## Commit

`9c4d84c` — "Fase 3: radioskysims-skymap — pacote dedicado de SkyMap"
