# Fase 2 — Piloto: `radioskysims-viz` + `radioskysims-beam`

## Objetivo

Validar o padrão de extração antes de generalizar: criar a base de
visualização (`radioskysims-viz`) e o pacote de feixes (`radioskysims-beam`)
como piloto, refatorando o painel de beam para herdar `PanelApplication`.

## `radioskysims-viz` (novo)

- `panel_application.PanelApplication` — classe base (`pn.viewable.Viewer`)
  com ciclo de vida `build_sidebar()` / `build_main()` / `serve()`, layout
  padrão sidebar+main.
- `ports.VisualizerPort` (ABC) — contrato de visualização.
- `panel_visualizer.PanelVisualizer` — adapter concreto baseado em Panel
  (resolve o acoplamento "Panel hardcoded em application" da auditoria).

Dependências: `panel`, `holoviews`, `hvplot` (leves).

## `radioskysims-beam`

Movido para `packages/radioskysims-beam/`:
- `domain/beam/*` — `Beam`, `BeamOps`, `BeamProperties`, factory, value objects
- `infrastructure/beams/loaders/*` — analytical, base, csv, custom, lit
- `infrastructure/db/beam_repository.py` + `beam_db_model.py`
- `application/ports/beam.py` — `BeamLoaderPort`/`BeamEvaluatorPort`/`BeamCreatorPort`
- `application/beam_panel.py` — **refatorado**: `BeamPanel(PanelApplication)`
  com `build_sidebar()`/`build_main()`

Ajustes de isolação:
- `loaders/csv.py`: `radioskysims.__path__[0]` → `radioskysims_core.paths.get_project_root()`
  (resolução da raiz do projeto sem depender do pacote legado).

## Shims de compatibilidade (mantidos até Fase 7)

`radioskysims.domain.beam.*`, `radioskysims.infrastructure.beams.*`,
`radioskysims.infrastructure.db.beam_repository`/`beam_db_model`,
`radioskysims.application.ports.beam`, `radioskysims.application.beam_panel`.

## Testes movidos (junto com o código)

- `tests/domain/beam/{test_beam_operations,test_beam_properties}.py`
- `tests/infrastructure/{test_beam_repository,test_beams_loaders,test_csv_loader,test_custom_loader}.py`
- `tests/beam_panel_test.py`, `tests/test_beam_pipeline.py`
- `tests/performance/test_beam_interpolation_speed.py`
- `test_no_legacy_namespace.py` **ficou na raiz** (testa a estrutura do monólito)
- Novos: `packages/radioskysims-beam/tests/conftest.py` (filtros de warning),
  `packages/radioskysims-viz/tests/test_panel_application.py`

## Verificação (gate da fase)

```bash
uv run --package radioskysims-beam pytest packages/radioskysims-beam/tests  # → 55 passed
uv run --package radioskysims-viz pytest packages/radioskysims-viz/tests    # → 5 passed
uv run pytest tests -q -m "not integration" --ignore=tests/performance       # → 983 passed
```

- Isolamento: deps runtime do beam (uv.lock) = holoviews, hvplot, numpy, pandas,
  panel, sqlmodel, xarray, core, viz — **sem** dask/pyccl/camb/psycopg2/healpy/astroquery.
- `dask` mantido em `[dependency-groups] dev` do beam (usado por testes).
- `BeamPanel` refatorado herda `PanelApplication` e constrói layout sidebar+main.

## Commit

`f54bfc8` — "Fase 2: piloto radioskysims-viz + radioskysims-beam"
