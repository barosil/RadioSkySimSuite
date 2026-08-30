# Configuration

Runtime configuration is driven by a **TOML file** — by default
`settings.toml` at the project root. The configuration layer lives in
`radioskysims-core` (`radioskysims_core.config`) and follows the **Ports and
Adapters** pattern: `ConfigPort` (port) + `TomlConfigAdapter` (adapter).

## Resolution order

```{note}
The legacy utility in `src/radioskysims/utils/settings.py` resolves the file
as: explicit path → `RADIOSKYSIM_SETTINGS` env var → `config/<name>.toml` →
`settings.toml`/`settings_01.toml` in the current working directory.
```
The current `radioskysims-core` loaders resolve relative to the **project
root** (`get_project_root() / "settings.toml"`), or accept an explicit
`settings_file`.

## `settings.toml` schema

Below is the schema used by the current decoupled code (repository ships a
working file at the root).

| Section | Purpose | Key fields |
|---|---|---|
| `[paths]` | Data folders | `raw_data_folder`, `auxiliary_data_folder`, `log_folder`, `skyfield_folder` |
| `[ports]` | Service ports | `db_port` (5432), `panel_port` (8080) |
| `[radiotelescopes.<name>]` | Telescope profile | `name`, `observer` (lat/lon/height), `antennas[]` |
| `[radiotelescopes.<name>.antennas]` | Antenna spec | `name`, `frequency_range` `[min,max,res]`, `pointing` (mode/alt_deg/az_deg), `beam` (name/polarizations/beam_width_deg/pattern_file), `backend` (spectrometer) |
| `[...antennas.backend]` | Spectrometer | `bandwidth_mhz`, `sampling_rate_mhz`, `integration_time_s`, `num_channels`, `T_sys_K` |
| `[simulations]` | Default time grid | `time_range` = `["<start ISO>", "<end ISO>", cadence_s]` |
| `[processing]` | Dask / batching | `max_batch_mb`, `cpu_count`, `dask_scheduler` (`threads`/`synchronous`/`distributed`), `dask_processes` |
| `[beams]` | Default beam | `name`, `file_path` |
| `[catalogs.radiosources]` / `[catalogs.spectral_indexes]` | Default catalogs | `name`, `url` |
| `[radiosources]` | Query filter | `query_str` (SQL used to filter the radio catalog) |
| `[noisemodels]` | Diffuse noise | `pysm3_component` (e.g. `["synchrotron"]`) |
| `[satellites]` | GNSS selection | `constellations` (e.g. `["GPS","GALILEO","BEIDOU","GLONASS"]`), `satellites` |
| `[signals]` | Signal metadata | `sat_signals` (path to `sat_signals.json`) |
| `[DB]` | PostgreSQL | `POSTGRES_USER/PASSWORD/HOST/PORT/DB` |
| `[cosmology]` | Cosmological params | `field_model`, `omega_c`, `omega_b`, `h`, `sigma8`, `n_s` |
| `[SPACETRACK]` | SpaceTrack credentials | `ST_USER`, `ST_PWD` (prefer env/`credentials.env`) |

## Using the configuration API

```python
from radioskysims_core.config.config_loader import (
    load_config,
    resolve_settings_path,
    set_settings_file,
    build_observer_from_settings,
    build_radiotelescope_from_settings,
)

# Dot-separated key lookup (returns dict):
sim_cfg = load_config("simulations")            # {"time_range": [...]}
proc_cfg = load_config("processing")            # {"dask_scheduler": "threads", ...}

# Resolve the settings file path:
path = resolve_settings_path()                  # -> Path(settings.toml)

# Switch the active file for the whole context:
set_settings_file("settings_planning.toml")

# Typed builders used by the composition root:
observer = build_observer_from_settings()
telescope = build_radiotelescope_from_settings("uirapuru")
```

### Pydantic Settings

A typed subset is also available via Pydantic `BaseSettings`
(`radioskysims_core.config.settings`):

```python
from radioskysims_core.config.settings import Settings

s = Settings.load()            # reads <project_root>/settings.toml
print(s.paths.sat_signals)     # Path | None
```

Environment variables (`.env`, nested delimiter `__`) take precedence over
the TOML file.

## Minimal example (planned CLI schema)

A minimal TOD-oriented example ships at
`config/examples/tod_settings_example.toml`. It uses a **flatter schema** that
targets the planned `tod export` CLI:

```toml
[time_range]
start = "2026-08-01T00:00:00Z"
end = "2026-08-01T00:10:00Z"
cadence = 1.0          # seconds

[frequency_range]
start_mhz = 980.0
end_mhz = 1260.0
nchan = 4

[radiotelescope]
name = "example_rt"
latitude = -7.0
longitude = -38.0
altitude = 100.0

[sources.sun]
enabled = true

[output]
outdir = "data/TOD/"
format = "netcdf"      # or 'zarr'
filename_template = "tod_result_{timestamp}.nc"
```

```{warning}
This minimal schema is **planned** for the future CLI; the current
`SimOrchestrator.from_settings()` reads the full schema described in the table
above (telescope profiles under `[radiotelescopes.<name>]`).
```

## Best practices

- Keep `settings.toml` as the **primary source of configuration**.
- Use named profile files (e.g. `settings_planning.toml`) and switch with
  `set_settings_file()` — never hard-code paths in code.
- Keep secrets (SpaceTrack, DB passwords) out of version control; use
  environment variables or a git-ignored `credentials.env`.
