# Fase 6 — `radioskysims-waterfall`

## Objetivo

Criar do zero `packages/radioskysims-waterfall/` — ferramentas de gerenciamento
de **waterfalls** (tempo × frequência) para radioastronomia, com arquitetura
hexagonal e foco em processamento seguro de grandes volumes de dados
(xarray + dask) e visualização preservando memória (holoviews + datashader).

Escopo **MVP** (decidido com o usuário): slice, resampling, filtros, SED,
lightcurve, baseline/bandpass e visualização básica. Não é feature-completa.

## O que foi criado

Estrutura hexagonal em `packages/radioskysims-waterfall/src/radioskysims_waterfall/`:

| Camada | Conteúdo |
|---|---|
| `domain/` | `models.py` (value object `Waterfall` + `WaterfallMetadata`), `operations.py` (slice/resample/decimation/interpolação/rebinning), `units.py`, `sed.py` (SED), `lightcurve.py`, `bandpass.py`, `baseline.py`, `filters.py` (mean/median/MAD/ArPLS), `masks.py`, `events.py`, `normalize.py` |
| `application/` | `ports/{loader,storage}.py` (`WaterfallLoaderPort`, `WaterfallStoragePort`), `services/pipeline.py` (`WaterfallPipeline` — declarativo e chainable), `visualization/waterfall_plot.py` (holoviews + datashader) |
| `adapters/` | `loaders/` (fits, hdf5, netcdf, xarray, zarr), `storage/file_storage.py` (persistência com versionamento) |
| `infrastructure/` | `monitor.py` (`SystemMonitor` — checagem segura de CPU/memória antes de operações pesadas) |

API pública de alto nível em `radioskysims_waterfall/__init__.py`: `Waterfall`,
`WaterfallMetadata`, `SED`, `LightCurve`, `WaterfallPipeline`, `SystemMonitor`,
`create_loader`, `load_waterfall`.

## Decisões de escopo

- O waterfall nasceu **autônomo**: não importa `radioskysims_core` nem
  `radioskysims_viz` (o plano previa dependência de `core`+`viz`, mas a
  implementação não precisou deles — mantém o pacote leve). Integração opcional
  com `radioskysims-simulation` fica via porta, sem dependência rígida.
- Extras seletivos: `hdf5`, `zarr`, `fits`, `plot`, `test`, `all`.
- `SystemMonitor` replica a detecção de CPU/memória do
  `ResourceAwareProcessor` do monólito, mas standalone e genérico (padrão da
  Fase 1 para o `radioskysims-core`).

## Dependências

`numpy`, `scipy`, `xarray`, `dask[array]`, `astropy>=7`, `psutil` + extras
opcionais (`h5py`/`h5netcdf`/`netCDF4`, `zarr`, `holoviews`/`datashader`/`panel`).

## Testes

`packages/radioskysims-waterfall/tests/` (12 arquivos): models, operations,
units, SED/lightcurve, bandpass/baseline, filters, masks/events,
loaders/storage, pipeline, monitor, visualization.

## Verificação (gate da fase)

```bash
uv run --package radioskysims-waterfall pytest packages/radioskysims-waterfall/tests
# → 133 passed
```

- `uv sync` do workspace resolve e instala `radioskysims-waterfall==0.1.0` sem
  regressão nos demais pacotes.
- `radioskysims-waterfall` registrado no umbrella: `[project.dependencies]`,
  extras `waterfall` e `all`, `[tool.uv.sources]` e `[tool.coverage.run].source`.

## Submódulo

`packages/radioskysims-waterfall` → `github.com/barosil/radioskysims-waterfall`
(commit `1350893161` — repo criado; ver `.gitmodules`).
