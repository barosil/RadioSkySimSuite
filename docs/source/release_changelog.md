# Release, Changelog & Migration

This page defines the release workflow and the migration path for users coming
from the pre-decoupling (monolithic) versions.

## Release checklist

1. **Freeze the workspace** — `uv sync` from a clean clone and run the full
   suite:
   ```bash
   uv sync
   uv run pytest tests -m "not performance"
   uv run ruff check src tests scripts packages/*/src
   ```
2. **Bump versions** — each package in `packages/*/pyproject.toml` uses a
   static version (`hatch-vcs`); update the changed packages and the umbrella
   `radioskysim`.
3. **Update `constraints.txt` / `requirements.txt`** if dependencies changed.
4. **Write the changelog** (template below) and the migration notes.
5. **Build the docs** and confirm no warnings:
   ```bash
   make docs
   ```
6. **Tag & publish** — create a GitHub release with the changelog
   (the `Changelog` URL in `pyproject.toml` points to GitHub releases).
7. **Update submodule pointers** — commit package changes in each affected
   submodule and bump the pointers in the meta-repo.

## Changelog template

```markdown
## [Unreleased]

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Deprecated
- ...

### Removed
- ...

## [0.x.y] - YYYY-MM-DD

### Added
- ...
```

## Unreleased — TOD export CLI + Job Runner (tickets TOD-003 → TOD-009)

### Added

- **CLI `radioskysims tod export`** — runs a short TOD simulation in
  foreground via `SimOrchestrator` and writes the dataset (HDF5/NetCDF/Zarr)
  plus a JSON sidecar. Options: `--config`, `--telescope`, `--constellations`,
  `--local-sources`, `--use-processor`, `--output`.
- **Background runner** — `radioskysims tod export --background` creates a
  job in the jobs database (SQLite, default `data/jobs.db`), spawns a worker
  subprocess and returns the job id immediately. The worker updates status
  (`PENDING → RUNNING → SUCCESS/FAILED/CANCELLED`) and writes a JSON progress
  file (`<output>.progress.json`) plus a log (`<output>.log`).
- **Jobs management** — `radioskysims tod jobs list`, `tod jobs status <id>`,
  `tod jobs cancel <id>` (SIGTERM to the worker) and `tod jobs monitor <id>
  [--watch]` (progress bar + step + ETA).
- **Notebook API** — `radioskysims.interfaces.api` exposes
  `run_simulation(..., background=...)`, `JobHandle` (`.refresh()`, `.wait()`,
  `.cancel()`, `.status`) and `progress_widget(handle)` (ipywidgets: bar,
  step, ETA, cancel button). See the executable example
  `notebooks/tod_background_job.ipynb`.
- **Job model + repository** — `Job` (table `jobs`) and `JobRepository`
  (SQLite) in `radioskysims_core.db` (`create`/`update_status`/
  `update_progress`/`set_pid`/`get`/`list`).
- **CI workflow** — `.github/workflows/ci.yml` (lint + meta tests + core
  tests) with submodules checkout.

### Changed

- The quickstart now documents the CLI and notebook workflows
  ({doc}`quickstart`).
- `tests/e2e/test_skymap_cli_e2e.py` skips when `asyncpg` is not installed
  (it is not a declared dependency).

### Notes

- The new commands are part of the umbrella `radioskysim` package; package
  versions are unchanged so far (changelog consolidated at the next release
  bump).

## Migration guide (monolithic → decoupled)

Users of the pre-decoupling `radioskysim` package must adapt their imports and
configuration:

### Imports

| Old (monolith) | New (decoupled) |
|---|---|
| `from radioskysims.domain.satellite import ...` | `from radioskysims_sources.domain.satellite import ...` |
| `from radioskysims.domain.tod import TODSimulator` | `from radioskysims_simulation.domain.tod import TODSimulator` |
| `from radioskysims.domain.skymap import SkyMap` | `from radioskysims_skymap.domain.skymap import SkyMap` |
| `from radioskysims.domain.common import TimeRange, Observer` | `from radioskysims_core.domain.common import TimeRange, Observer` |
| `from radioskysims.bootstrap.composition import create_sim_orchestrator` | `from radioskysims_simulation.application.services.sim_orchestrator import SimOrchestrator` |
| `from radioskysims.infrastructure.config.settings import settings` | `from radioskysims_core.config.settings import Settings` |

```{note}
Legacy `radioskysims.* → package` compatibility shims were **removed** in
Fase 7 of the decoupling plan. Do not re-create them.
```

### Configuration

- The runtime now resolves `settings.toml` from the **project root**, or an
  explicit `settings_file` argument. Old `config/<name>.toml` resolution via
  `RADIOSKYSIM_SETTINGS` is still supported by the legacy utility in
  `src/radioskysims/utils/settings.py` (see {doc}`configuration`).
- Telescope profiles live under `[radiotelescopes.<name>]`; the `[simulations]
  time_range` grid and `[processing]` knobs are read by `SimOrchestrator`.

### Notebooks

- The demo notebooks in `notebooks/` were updated to the decoupled imports;
  use them as reference for migrating your own notebooks.

### TOD CLI (new)

The `tod export` / `tod jobs` commands and the notebook API replace the
Python-only interactive flow for running simulations:

| Old (Python API only) | New (CLI / notebook API) |
|---|---|
| `orch = SimOrchestrator.from_settings(...)`; `orch.run(...)` in a notebook | `radioskysims tod export --config settings.toml --telescope uirapuru` |
| Blocking `run()` in the notebook cell | `run_simulation(..., background=True)` → `JobHandle` (non-blocking) |
| Manually tracking runs | `radioskysims tod jobs status <id>` / `monitor <id>` |

No changes to the underlying `SimOrchestrator` API are required — the CLI and
notebook helpers are thin adapters over the same pipeline.

### Data

- Persisted data (HDF5/Zarr/NetCDF) is forward-compatible — coordinates and
  attrs are unchanged. Re-run `init_db` to create any new tables
  (see {doc}`database`).

## Versioning

- Each package and the umbrella follow **SemVer**.
- Breaking API changes bump the major (or minor, per project policy) of the
  affected package; the umbrella `radioskysim` depends on explicit ranges.
