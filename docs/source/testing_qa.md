# Tests & QA

This page defines the **test matrix** and quality gates. The goal is a clear
separation between fast unit tests, slower integration tests and end-to-end
notebook checks.

## Test matrix

| Level | Scope | Speed | Where |
|---|---|---|---|
| **Unit** | Domain entities, value objects, pure logic (no IO) | fast | `packages/<pkg>/tests/unit` and `tests/domain` |
| **Integration** | Adapters, DB, providers (Skyfield, Healpy, TAP), settings | medium | `packages/<pkg>/tests/integration`, `tests/integration` |
| **E2E (notebooks)** | Full pipelines (TOD, map-making round-trip, satellite tracks) | slow | `tests/e2e` + executable `notebooks/` |
| **Performance** | Benchmark / profiling (`PERF-003`) | very slow | `tests/performance` (marker `performance`, not run by default) |

## Markers

Defined in `pytest.ini`:

- `integration` — tests depending on external libraries or heavy IO.
- `performance` — performance/profiling tests, **not run by default**.

```bash
# default (unit + fast integration):
uv run pytest tests

# integration only:
uv run pytest tests -m integration

# skip slow markers:
uv run pytest tests -m "not performance and not integration"

# single package in isolation:
uv run --package radioskysims-simulation \
  pytest packages/radioskysims-simulation/tests
```

## What each level must cover

- **Unit** — beam math (FWHM/gain), `FrequencyRange`/`TimeRange` bounds,
  satellite track filtering, waterfall operations (mask/baseline/filter),
  TODSimulator source combination.
- **Integration** — the **TOD → map-making round-trip** (reconstruct a map
  from a simulated TOD and assert coverage, task `MAP-002`), settings
  loaders/validators, TAP/astroquery ingest (mocked or live), HDF5/Zarr
  save/load round-trips.
- **E2E** — the Quickstart flow: `SimOrchestrator.from_settings()` →
  `run(constellations=["GPS"])` → `compute()` → `save_result()`, and the
  notebook-based demos.

## Lint & formatting

```bash
uv run ruff check src packages/*/src tests
uv run ruff format --check src packages/*/src tests
```

## CI (planned)

```{note}
A CI pipeline running the fast tests on pull requests (task `QA-002`) is
**planned but not yet implemented** — there is no `.github/workflows` yet.
When added, the pipeline should:
```

1. `uv sync` on the PR branch.
2. Run lint (`ruff check`).
3. Run fast tests: `uv run pytest tests -m "not performance"` (smoke).
4. Run integration tests (with PostgreSQL service) on a nightly schedule.
5. Validate that `make docs` builds without warnings.

## Smoke test

A minimal smoke check is just the Quickstart:

```bash
uv run python - <<'PY'
from radioskysims_simulation.application.services.sim_orchestrator import SimOrchestrator
orch = SimOrchestrator.from_settings(telescope="uirapuru")
r = orch.run(constellations=["GPS"], include_satellites=True, use_processor=True)
print(r.format_summary())
PY
```

See {doc}`quickstart` for the full flow.
