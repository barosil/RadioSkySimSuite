# Database & Persistence

Persistence uses **SQLModel** (SQLAlchemy + Pydantic) on **PostgreSQL** for
metadata and sidecar records, while the heavy arrays (datasets, HEALPix maps)
live on **HDF5/Zarr/NetCDF** files referenced from the database.

```{note}
The `jobs` and `persisted_maps` tables described in the planning docs
(`docs/tasks/use_case_full_breakdown.md`) are **planned but not yet
implemented**. This page documents the schema that exists today.
```

## Engine

The core engine lives in `radioskysims_core.db` and is configured from the
`[DB]` section of `settings.toml`.

- **Sync engine** — `Database` (psycopg2; also works with SQLite for tests):
  `session`, `create_table(model)`, `drop_table`, `clear_db`,
  `test_connection()`.
- **Async engine** — `aengine` (asyncpg): `build_async_uri()`, `async_engine`,
  `AsyncSessionLocal`, `get_session()`, `init_db()`, `test_connection()`.

The connection URI is built from `POSTGRES_USER/PASSWORD/HOST/PORT/DB`
(defaults `radio`/`radio`/`localhost`/`5432`/`radioskysims`).

```python
from radioskysims_core.db.engine import Database

db = Database()
print(db.test_connection())
with db.session() as s:
    ...
```

## Creating the schema

`SQLModel.metadata.create_all` is used (no Alembic migrations yet — those are
**planned**). The initialization script imports every model module so that all
tables are registered:

```bash
.venv/bin/python -m radioskysims.infrastructure.db.init_db
```

```{note}
Repositories also call `create_all` defensively before use, so the schema is
usually created on first access even without running `init_db`.
```

## Tables (current schema)

### Sources — `radioskysims-sources`

| Table | Model | Purpose |
|---|---|---|
| `satid` | `SatID` | Satellite catalog entries (NORAD ID, names, constellation) |
| `orbital_elements` | `OrbitalElement` | TLE/OMM orbital elements (epoch, mean motion, inclination, ...) |
| `signal` | `Signal` | Signal definitions (PSD metadata per modulation) |
| `sat_signal_link` | `SatSignalLink` | Association satellite ↔ signal |
| `radiosources` | `RadioSourceDB` | Radio source catalog rows (RA/Dec, flux, spectral index) |
| `solar_flux` | `SolarFluxDB` | Cached solar flux measurements (Jy) |

### Beam — `radioskysims-beam`

| Table | Model | Purpose |
|---|---|---|
| `beamparamsdb` | `BeamParamsDB` | Beam parameters (pattern file path, FWHM, polarizations) |

### Radiotelescope — `radioskysims-radiotelescope`

| Table | Model | Purpose |
|---|---|---|
| `radiotelescopes` | `Radiotelescope` | Telescope value object (EarthLocation, frequency range, beam id) |

### Simulation — `radioskysims-simulation`

| Table | Model | Purpose |
|---|---|---|
| `simulations` | `SimulationRecord` | Full run summary (observer, frequency grid, sky stats, computation state) as JSON + scalar columns |
| `mapmaking_results` | `MapMakingRecord` | Map-making run metadata + reference to the HDF5 file (arrays are **not** stored in Postgres) |

### Skymap — `radioskysims-skymap`

| Table | Model | Purpose |
|---|---|---|
| `skymaprecord` | `SkyMapRecord` | Persisted HEALPix sky-map metadata |

## Model registration

The schema is pluggable: `radioskysims_core.db.models` exposes
`register_model_module(module_name)` and `load_registered_models()`. The
umbrella `src/radioskysims/infrastructure/db/models.py` aggregates the models
for convenient imports.

## Repositories

- `SimulationRepository` / `MapMakingRepository` (`radioskysims-simulation`) —
  create/read `SimulationRecord` and `MapMakingRecord`, calling `create_all`
  defensively.
- `SatelliteRepository` / `SignalRepository` / `RadioSourceRepository`
  (`radioskysims-sources`) — satellite catalog, signals and radio sources.
- `HDF5SkyMapRepository` (`radioskysims-skymap`) — persisted sky maps on HDF5.

## Roadmap (planned)

- `jobs` table — background job lifecycle (`RUNNING` → `SUCCESS`/`CANCELLED`).
- `persisted_maps` table — registry of persisted sky maps / datasets.
- Alembic migrations instead of bare `create_all`.
