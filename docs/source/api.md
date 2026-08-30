# API Reference

This section indexes the main public components of the **decoupled packages**.
Each scientific domain has a dedicated page with the public classes/functions,
their locations and usage examples.

## Domain pages

- {doc}`radiotelescope` — telescope / antenna / backend specifications.
- {doc}`satellites` — TLE/RINEX pipeline, tracks, signals and PSDs.
- {doc}`sources` — Sun / local sources and radio source catalogs (NVSS/TAP).
- {doc}`skymaps` — HEALPix sky maps, generation, analysis and map-making.
- {doc}`simulation` — TOD synthesis, `SimOrchestrator`, result objects.
- {doc}`waterfall` — time × frequency datasets, pipeline and plotting.
- {doc}`file_formats` — HDF5 / Zarr / NetCDF / FITS / JSON usage.

## Core (kernel) modules

- `radioskysims_core.domain.common` — `Observer`, `TimeRange`,
  `FrequencyRange`, `AngularRange`.
- `radioskysims_core.domain.geometry` — `SkyfieldGeometryProvider`,
  `compute_pointing_track`.
- `radioskysims_core.domain.tracks` — `TrackFactory`, `Tracks`.
- `radioskysims_core.config` — `load_config`, `Settings`, `ConfigPort`,
  `TomlConfigAdapter`.
- `radioskysims_core.db` — `Database`, `aengine`, model registration.
- `radioskysims_core.monitor` — `SystemMonitor`, `check_resources`.

```{note}
Auto-generated API pages (sphinx **autodoc2**) for the decoupled packages are
**prepared but not yet enabled** (task `IO-002`): the `autodoc2_packages`
configuration in `docs/source/conf.py` already scans the 9 `packages/*/src`
trees, but the extension is commented out pending an environment with
`autodoc2` installed. Follow the runbook in {doc}`file_formats` →
*API reference generation (IO-002)* to enable it. The previous autodoc output
in `apidocs/` and the module pages in `modules/` document the old monolithic
`radioskysims.*` API and are currently excluded from the build — see
{doc}`history_cleanup`.
```
