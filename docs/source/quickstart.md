# Quickstart

This guide reproduces a **minimal Time Ordered Data (TOD)** simulation end to
end. It uses the current decoupled API (`radioskysims_simulation`), driven by
`settings.toml`. Two entry points are available: the **Python API** (below)
and the **CLI** (`radioskysims tod export`, see {ref}`quickstart-cli`).

```{note}
The CLI runs the same pipeline as the Python API. Use the CLI for one-shot
runs and background jobs; use the Python API (or the notebook helpers in
{ref}`quickstart-notebook`) for interactive work.
```

## 1. Install and prepare

Follow {doc}`installation` first. The quickstart assumes the project is
installed (editable) and that a `settings.toml` exists at the project root
(it does, in the repository).

## 2. Run a minimal TOD

```python
from radioskysims_simulation.application.services.sim_orchestrator import (
    SimOrchestrator,
)

# Create an orchestrator from the telescope profile in settings.toml.
# The repository ships a "uirapuru" profile (see settings.toml).
orch = SimOrchestrator.from_settings(telescope="uirapuru")

# Run a satellite-only TOD (constellations from settings.toml by default).
result = orch.run(
    constellations=["GPS"],
    include_satellites=True,
    use_processor=True,   # memory-aware batching (ResourceAwareProcessor)
)

# Materialize the lazy (dask) dataset into memory.
ds = result.compute()

# Human-readable summary of the run (config + sky statistics).
print(result.format_summary())
```

`run()` returns a `SimulationOrchestratorResult`. The `.dataset` inside
`result.simulation_result` stays **lazy (dask)** until you call
`compute()` — useful for large TODs.

## 3. Persist the result

The result can be saved as **HDF5/NetCDF** or **Zarr**, plus a JSON sidecar
with the full run summary:

```python
from radioskysims_simulation.domain.simulation import (
    SimulationOrchestratorResult,
)

# Format inferred from the extension: .nc/.h5/.hdf5 → HDF5, .zarr → Zarr.
sidecar_path = result.save_result("data/TOD/gps_tod.nc")
print("Saved dataset + summary:", sidecar_path)  # -> gps_tod.nc + gps_tod.nc.json

# Reload later without re-running the simulation:
loaded = SimulationOrchestratorResult.load_result("data/TOD/gps_tod.nc")
print(loaded.format_summary())
```

## 4. Run other source types

The three source families are independent — combine them as needed:

```python
# Sun / local sources only:
orch.run(
    include_satellites=False,
    include_local_sources=True,
    use_processor=True,
)

# Radio sources (NVSS) only:
orch.run(
    include_satellites=False,
    include_radio_sources=True,
    use_processor=True,
)

# Diffuse Galactic emission (PySM3 HEALPix maps):
orch.run(
    include_satellites=False,
    include_galaxy=True,
    galaxy_nside=64,
    use_processor=True,
)
```

```{seealso}
{doc}`simulation` describes each option of `SimOrchestrator.run` in detail,
and {doc}`configuration` explains how `settings.toml` drives the run.
```

## 5. CLI entry points

Two console scripts are installed:

```bash
radioskysims --help     # TOD export + sky-map generation/analysis (argparse)
gnss4astro --help       # GNSS/RINEX download, tracks, signal estimation
```

(quickstart-cli)=
### 5.1. `radioskysims tod export` — run a TOD

The CLI drives the same `SimOrchestrator` pipeline as the Python API. It needs
a complete settings file (schema with `[radiotelescopes.<name>]` and
`[simulations]`), like the `settings.toml` at the project root.

```bash
# Foreground: short run, writes data/TOD/tod_<ts>.nc + JSON sidecar
radioskysims tod export --config settings.toml --telescope uirapuru

# With GNSS constellations and local sources (Sun)
radioskysims tod export --config settings.toml --telescope uirapuru \
    --constellations GPS GALILEO --local-sources

# Memory-aware processor (ResourceAwareProcessor batching)
radioskysims tod export --config settings.toml --telescope uirapuru \
    --use-processor

# Custom output path
radioskysims tod export --config settings.toml --telescope uirapuru \
    --output data/TOD/my_run.nc
```

### 5.2. `--background` — background jobs

`--background` creates a job in the jobs database (SQLite by default at
`data/jobs.db`), spawns a worker subprocess and returns immediately with the
job id. The worker writes a JSON progress file (`<output>.progress.json`) and
updates the database as it runs.

```bash
# Creates job, returns job id right away
radioskysims tod export --config settings.toml --telescope uirapuru --background

# Manage jobs
radioskysims tod jobs list
radioskysims tod jobs status 1
radioskysims tod jobs monitor 1 --watch          # bar + step + ETA, até concluir
radioskysims tod jobs cancel 1                   # SIGTERM ao worker + CANCELLED

# Point at a custom jobs database
radioskysims tod jobs status 1 --jobs-db sqlite:///data/jobs.db
```

```{seealso}
{doc}`simulation` describes each option of `SimOrchestrator.run` in detail,
and {doc}`configuration` explains how `settings.toml` drives the run.
```

(quickstart-notebook)=
### 5.3. Notebook API — non-blocking runs + widget

`radioskysims.interfaces.api` exposes `run_simulation` (foreground or
background), a `JobHandle` to track/cancel a job, and an ipywidgets progress
widget:

```python
from radioskysims.interfaces.api import progress_widget, run_simulation

# Background: returns a JobHandle immediately (no blocking)
handle = run_simulation(
    "settings.toml",
    telescope="uirapuru",
    background=True,
)

# Track it
print(handle.status)      # -> PENDING / RUNNING / ...
snap = handle.wait(timeout=120)   # blocks until SUCCESS/FAILED/CANCELLED
print(snap["status"], snap["percent"], snap["eta"])

# Live widget (in a notebook cell): bar + step + ETA + cancel button
progress_widget(handle)

# Foreground with a progress callback
run_simulation(
    "settings.toml",
    telescope="uirapuru",
    progress_callback=lambda snap: print(snap["status"], snap["percent"]),
)
```

```{seealso}
The executable example `notebooks/tod_background_job.ipynb` walks through a
full background run with the widget.
```

## Troubleshooting

- **"No satellites available"** — the satellite repository needs orbital
  elements. Run the ingestion notebook
  (`notebooks/04_generate_satellite_tracks.ipynb`) or update elements via the
  `SatelliteService` before simulating.
- **Job stuck as `RUNNING`** — check the worker log next to the output
  (`<output>.log`) and the JSON progress file; the job may have failed before
  updating the database.
- **"Connection refused" / asyncpg warnings** — the TOD pipeline initializes
  the PostgreSQL engine for persistence. Start the database container with
  `make postgres-up` (see {doc}`database`) or check the environment.
- **Postgres not running** — satellite/simulation persistence uses the DB
  configured in `[DB]` of `settings.toml`. Start it with `make postgres-up`
  (see {doc}`database`).
- **Memory** — for large runs always pass `use_processor=True`; see
  {doc}`performance` for tuning.
