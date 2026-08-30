# Simulation (TOD & Maps)

This page documents the **simulation API** — the entry points to synthesize
Time Ordered Data (TOD) from discrete sources (satellites, Sun, radio sources)
and diffuse maps (Galactic emission, neutral hydrogen).

All objects live in `radioskysims-simulation` (import `radioskysims_simulation`).

## Public entry point: `SimOrchestrator`

The recommended high-level API:

```python
from radioskysims_simulation.application.services.sim_orchestrator import (
    SimOrchestrator,
)

orch = SimOrchestrator.from_settings(telescope="uirapuru")

result = orch.run(
    constellations=["GPS"],        # or None → settings.toml default
    include_satellites=True,
    include_local_sources=False,   # Sun
    include_radio_sources=False,   # NVSS
    include_galaxy=False,          # diffuse PySM3 maps
    use_processor=True,            # memory-aware batching (Dask)
)

ds = result.compute()               # -> xr.Dataset (materialized)
print(result.format_summary())      # human-readable run summary
sidecar = result.save_result("data/TOD/run.nc")   # dataset + JSON sidecar
```

### `from_settings`

`SimOrchestrator.from_settings(telescope="default", *, settings_file=None)`
creates an orchestrator from a telescope profile in `settings.toml`. An
optional named settings file (e.g. `settings_planning.toml`) becomes the
active file for the whole simulation context.

### `run(...)` — key parameters

| Parameter | Default | Meaning |
|---|---|---|
| `constellations` | `None` (settings) | GNSS constellations, e.g. `["GPS","GALILEO"]` |
| `time_range` | observer default | `TimeRange` to simulate |
| `include_satellites` | `True` | Include GNSS satellite sources |
| `include_local_sources` | `False` | Include Sun / local sources |
| `include_radio_sources` | `False` | Include NVSS radio sources |
| `radio_search_radius_deg` / `radio_min_flux_jy` | 20.0 / settings | Radio catalog filter |
| `include_galaxy` | `False` | Diffuse Galactic maps (PySM3, `galaxy_nside` default 64) |
| `include_neutral_hydrogen` | `False` | Neutral-hydrogen (HI) contribution |
| `use_processor` | `False` | Batch sources with `ResourceAwareProcessor` |
| `max_batch_mb` / `cpu_count` / `memory_mb` | auto | Memory/cpu knobs for the processor |
| `dask_scheduler` | `"threads"` | `"threads"` \| `"synchronous"` \| `"distributed"` |
| `dask_processes` | settings | Spawn separate processes for distributed workers |
| `mueller` / `combine_polarization` | `None` / `"sum"` | Polarization handling |
| `persist_skymaps` / `skymap_overwrite` | `False` | Persist generated Galactic maps to HDF5 |

`run()` returns a **`SimulationOrchestratorResult`** with:

- `.simulation_result` — the underlying `SimulationResult` (lazy dataset);
- `.compute()` → `xr.Dataset`;
- `.summary()`, `.format_summary()`, `.to_json()` — run summary (config +
  sky statistics; stats filled after materialization);
- `.events` — `SimulationEvents` (transits) extracted chunk-wise, computed on
  demand;
- `.save_result(filepath, fmt=...)` → writes dataset + `<file>.json` sidecar,
  returns the sidecar path;
- `.load_result(filepath)` — reconstructs a persisted result.

```{note}
`run()` supports **multiple antennas/beams**: it iterates over
`rt.antennas`, runs a simulation for each and consolidates the results along a
`pointing` dimension.
```

## Lower-level API

For fine-grained control you can use the components directly:

| Component | Location | Role |
|---|---|---|
| `TODSimulator` | `domain/tod/simulator.py` | `simulate_from_source(...)` for discrete sources; `simulate_from_maps(...)` for diffuse maps (requires a `SkyMapTODProjector`) |
| `TODOrchestrator` | `application/services/tod_orchestrator.py` | `run_sources(...)`, `run_maps(...)`, `run(...)` |
| `TODService` | `application/services/tod_services.py` | Convenience `run(*, satellites, mueller, combine_polarization)` |
| `SimulationService` | `application/services/simulation_service.py` | `run_by_constellations_from_settings(...)`, `run_by_ids(...)`, ... |
| `Simulation` | `domain/simulation/simulation.py` | Domain executor producing `SimulationResult` |
| `SimulationResult` | `domain/simulation/simulation.py` | Lazy result: `.dataset`, `.compute()`, `.save()`, `.to_zarr()`, `.to_hdf5()`, `.load()`, `.select_source_type()` |

### `TODSimulator` details

```python
from radioskysims_simulation.domain.tod import TODSimulator

sim = TODSimulator(beam=beam, gain=gain, effective_area_m2=area_m2)

# Discrete sources (SatelliteSignalSource / LocalSourceSignalSource /
# RadioSourceSignalSource):
tod = sim.simulate_from_source(
    sat=source, combine_polarization="sum", units="W/Hz",
)

# Diffuse maps:
tod = sim.simulate_from_maps(
    maps=maps, pointing_track=track, projector=projector,
    fwhm_deg=fwhm, use_beam=True,
)
```

Units accepted: `"W/Hz"` (total power, applies 1/r²) or `"W/m²/Hz"` (flux
density).

## Map-making (TOD → map)

`radioskysims-simulation` provides `HealpyBinnedMapMakerAdapter.make_map(...)`
→ `MapMakingResult` (`skymap`, `hit_map`, `observed_mask`, `n_samples`,
`n_observed_pixels`, `coverage_fraction`), orchestrated by
`MapMakingService.run(...)`. See {doc}`skymaps`.

## Non-blocking / notebook helpers (planned)

```{warning}
The planned `run_simulation(..., background=True)` helper returning a
`JobHandle` and the progress widget (tickets `SIM-003`/`TOD-007`) are **not
implemented yet**. The roadmap is tracked in
`docs/tasks/tod_cli_background_tickets.md` and
`docs/tasks/use_case_full_breakdown.md`.
```

Until then, large runs in notebooks should use `use_processor=True` (which
streams batches to disk when the estimated output exceeds available memory) and
materialize only the slices you need via `SimulationEvents` / chunk-wise access.

## Persisting results

`SimulationResult.save(path, fmt=None)` infers the format from the extension
(`.nc`/`.h5`/`.hdf5` → HDF5 via h5netcdf; `.zarr` → Zarr) or an explicit
`fmt="hdf5"|"nc"|"zarr"`. See {doc}`file_formats`.
