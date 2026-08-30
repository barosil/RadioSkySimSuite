# File Formats & IO

This page documents the file formats used for persistence and interchange, and
how the API reference docs are generated.

## Formats

| Format | Where it is used |
|---|---|
| **HDF5** (NetCDF4-compatible via `h5netcdf`) | Default output of `SimulationResult.save()`; `Tracks.to_hdf5()`; `HDF5SkyMapRepository`; `MapMakingRecord` arrays (referenced by filepath); waterfall storage; `SolarFluxRepository` cache |
| **Zarr** | `SimulationResult.to_zarr()` / `SimulationResult.save(..., fmt="zarr")`; `Tracks.to_zarr()`; waterfall storage |
| **NetCDF** | `Tracks.to_hdf5(engine="h5netcdf")`; `gnss4astro tracks --out tracks.nc`; waterfall netcdf loader/storage |
| **FITS** | Sky maps (`HealpySkyMapProvider.read_map/write_map`), HiPS cutouts, CLI `skymap analyze --input <fits>`, waterfall fits loader/storage |
| **CSV / XLSX** | Beam pattern files (`CSVBeamLoader`, `BeamFactory.create_beam_from_file`; xlsx in `radioskysims/resources/beams/`), radio catalogs (`catalogs.radiosources`) |
| **JSON** | `sat_signals.json` (signal metadata), simulation sidecar summaries (`save_result` → `<file>.json`), `SignalRepository` |

### Choosing a format

- `SimulationResult.save(path, fmt=None)` infers the format from the file
  extension: `.nc` / `.h5` / `.hdf5` → HDF5; `.zarr` → Zarr. Pass
  `fmt="hdf5"|"nc"|"zarr"` to override.
- Waterfall `FileStorage.save(waterfall, path, fmt=...)` supports
  netcdf / zarr / hdf5 / fits with versioning.

## Dataset layout

- **TOD dataset** — dims `(time, frequency, ...)` with a `pointing` dimension
  for multi-antenna runs; `T_antenna` in Kelvin; `frequency` coordinate in Hz;
  provenance stored in `dataset.attrs` (see {doc}`units_conventions`).
- **Tracks** — time series of satellite positions/geometry (xarray), with
  `to_hdf5` / `to_zarr` and chunk helpers.

## API reference generation (IO-002)

The API reference is generated with **sphinx-autodoc2** (`docs/source/conf.py`).
The configuration for the **decoupled packages** is already in place
(`autodoc2_packages` scans the 9 `packages/*/src` trees), but the `autodoc2`
extension is currently commented out — see the `IO-002` banner in `conf.py`.

### Enabling the auto-generated API reference

Run these steps in an environment that has access to PyPI (the `autodoc2`
package is **not** part of the `docs` extra on purpose — it is not available in
all registries/mirrors, and keeping it out of the extras avoids breaking
`uv sync`):

1. **Install `autodoc2`** (e.g. `uv pip install autodoc2` or
   `pip install autodoc2`).
2. **Enable the extension** — in `docs/source/conf.py`, uncomment
   `"autodoc2"` in the `extensions` list.
3. **Include the generated pages** — remove `"apidocs/**"` from
   `exclude_patterns` in `conf.py`.
4. **Delete the stale monolith output** so autodoc2 starts fresh:

   ```bash
   rm -rf docs/source/apidocs
   ```

5. **Rebuild**:

   ```bash
   make docs
   ```

autodoc2 regenerates `docs/source/apidocs/` from the packages
(`radioskysims_core`, `radioskysims_beam`, `radioskysims_skymap`,
`radioskysims_radiotelescope`, `radioskysims_sources`,
`radioskysims_simulation`, `radioskysims_waterfall`, `radioskysims_viz`,
`gnsstools4astro`) and `api.md` includes them via toctree.

### Tuning

- The config uses `auto_mode="all"` with `module_mode="module"` (one page per
  module). If the output is too verbose, restrict with `include_patterns` /
  `exclude_patterns` per package entry in `autodoc2_packages`.
- `autodoc2_output_dir = "apidocs"` controls the output location.
- Docstrings follow the NumPy/Google styles; autodoc2 parses both with its
  default `docstring_parser`.

## Related notebooks

- `notebooks/50_TOD_SIMULATION.ipynb` — TOD generation and HDF5 persistence.
- `notebooks/skymap_howto.ipynb` — FITS read/write, cache and download.
- `notebooks/localsources_solar_flux_real_test.ipynb` — NetCDF caching.
