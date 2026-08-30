# Waterfall Visualization

The `radioskysims-waterfall` package (import `radioskysims_waterfall`) manages
**time × frequency** datasets ("waterfalls") for radio astronomy, with a
chainable processing pipeline and interactive HoloViews/Datashader plots.

## Domain

```python
from radioskysims_waterfall import Waterfall, WaterfallMetadata
from radioskysims_waterfall.domain.sed import SED
from radioskysims_waterfall.domain.lightcurve import LightCurve

wf = Waterfall(data, meta=WaterfallMetadata(...), mask=mask,
               events=events, time=time, freq=freq)
```

- `Waterfall` — canonical `("time", "freq")` DataArray with chainable,
  immutable operations.
- `WaterfallMetadata` — associated metadata.
- `SED` — spectral energy distribution; `LightCurve` — light curve (has a
  `.plot()`); `Event` — transient/event annotations.
- Module-level operation helpers: `bandpass.py`, `baseline.py`, `filters.py`,
  `masks.py`, `normalize.py`, `units.py`.

## Pipeline

`WaterfallPipeline` lets you chain processing steps:

```python
from radioskysims_waterfall.application.services.pipeline import WaterfallPipeline

pipeline = WaterfallPipeline()
pipeline.add(step_1).add(step_2)
print(pipeline.describe())
result = pipeline.run(waterfall, monitor=None)
```

Ports (`application/ports/`) define `WaterfallLoaderPort` and
`WaterfallStoragePort`.

## Plotting

```python
from radioskysims_waterfall.application.visualization.waterfall_plot import (
    plot_waterfall,
    plot_sed,
    plot_lightcurve,
)

plot_waterfall(waterfall, ...)   # interactive HoloViews/Datashader
plot_sed(...)
plot_lightcurve(...)
```

Color limits, interactivity and widget-based exploration are the focus of the
visualization examples (task `VIZ-001`).

## Persistence & loading

`FileStorage` (adapter for `WaterfallStoragePort`) saves in
**netcdf / zarr / hdf5 / fits** with versioning:

```python
from radioskysims_waterfall.adapters.storage.file_storage import FileStorage

storage = FileStorage()
path = storage.save(waterfall, "data/waterfalls/obs.nc", fmt="netcdf")
```

Loaders live in `adapters/loaders/` (`fits_loader`, `hdf5_loader`,
`netcdf_loader`, `xarray_loader`, `zarr_loader`), with `create_loader` and
`load_waterfall` exported from `adapters/__init__.py`.

## Legacy visualization (meta-package)

`src/radioskysims/visualization/waterfall.py` still exposes the pre-decoupling
helpers: `waterfall_plot`, `interactive_waterfall`, `tod_panel`,
`serve_tod_panel`, `multi_source_waterfall`, `time_series_plot`,
`events_spans`, `events_overlay`.

```{note}
Prefer the `radioskysims-waterfall` API above for new work; the legacy module
is kept for compatibility and traceability.
```

## Related notebooks

- `notebooks/50_TOD_Visualization.ipynb` — loads the latest simulation and
  shows an interactive waterfall + time series (run after
  `50_TOD_SIMULATION.ipynb`).
- `notebooks/00_RADIOSKYSIM_COMPLETE_DEMO.ipynb` — full pipeline including
  waterfall.
