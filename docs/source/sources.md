# Sources (Local & Radio)

The `radioskysims-sources` package (import `radioskysims_sources`) provides the
**signal sources** used in TOD simulations: the **Sun / local sources** and
**radio source catalogs** (NVSS via TAP). The common protocol is
`SignalSource` (`domain/signal_source.py`) with concrete implementations
`SatelliteSignalSource`, `LocalSourceSignalSource` and
`RadioSourceSignalSource`.

## Sun & local sources

```python
from radioskysims_sources.infrastructure.external.solar_flux_downloader import (
    SolarFluxDownloader,
)

# Real solar flux from Learmonth SRD/SRS (Jy), centered on a UTC time
flux = SolarFluxDownloader(timeout_sec=30).fetch(
    center_utc="2026-08-01T12:00:00", window_hours=2,
)

# Evaluate the flux model at a given UTC time / frequency (MHz)
value_jy = flux.evaluate(t_utc, freq_mhz=1000.0)
grid = flux.evaluate_grid(times, freqs_mhz)
```

The domain model (`domain/localsources/models.py`) provides `SolarFlux`,
`LocalSourceTrack`, `LocalSource` and `LocalSources`. Track computation uses
`SkyfieldLocalSourceTrackProvider().compute_track(...)`.

The service layer (`application/services/local_sources_service.py`) exposes
`build_local_sources()`, `get_solar_flux(...)` and `get_local_source_track(...)`.

```{seealso}
`notebooks/localsources_solar_flux_real_test.ipynb` — real `SolarFlux` test
with `SolarFluxRepository` NetCDF caching (canonical unit: **Jy**).
```

## Radio sources (NVSS / TAP)

### Domain

`domain/radiosources/`:

| Class | Role |
|---|---|
| `RadioSource` | Catalog entry (name, RA/Dec, flux, spectral index) |
| `SpectralModel` | Spectral index / flux model |
| `RadioSourceFluxSample` | Flux sample at a frequency |
| `RadioSourceSignalEvaluator` | `evaluate_flux`, `evaluate_flux_batch`, `evaluate_flux_grid` |
| `RadioSourceTrack` | `evaluate`, `filter_by_source`, `filter_by_flux` |
| `ContinuumSource`, `Galaxy`, `NeutralHydrogen` | Extended/diffuse continuum sources |

### Ingest (TAP / astroquery)

```python
from radioskysims_sources.infrastructure.external.radiosources_ingest import (
    VizierTapIngestAdapter,
)

adapter = VizierTapIngestAdapter(tap_url="...")
records = adapter.ingest_from_tap(survey="NVSS", adql_query="SELECT ...")
# or from a local file:
records = adapter.ingest_from_file("catalog.csv", format="csv")
```

### Service & use cases

`RadioSourceCatalogService` (`application/services/catalog_services.py`):
`ingest_nvss_specfind(...)`, `list_sources_in_region(...)`,
`compute_tracks(...)`, `evaluate_flux(...)`, `get_brightest_sources(...)`.

Use cases in `application/radiosources_use_cases.py`:

- `BuildRadioSourcesCatalogUseCase`
- `BuildNvssSpecfindCatalogUseCase` — NVSS + SPECFIND ADQL query
- `ComputeRadioSourcesForegroundUseCase`

Cosmology / diffuse maps:

- `GenerateNeutralHydrogenMapUseCase`, `GenerateNeutralHydrogenMapsUseCase`
  (`application/cosmology/`)
- `GalaxyMapSet`, `GenerateGalaxyMapsUseCase`
  (`application/skymap/generate_continuum.py`)

```{note}
The default radio query filter comes from `[radiosources] query_str` in
`settings.toml` (exposed as `radio_min_flux_jy`), and the default catalogs are
declared under `[catalogs.radiosources]` / `[catalogs.spectral_indexes]`.
```

## Using sources in a simulation

Pass the corresponding flags to `SimOrchestrator.run`:

```python
orch.run(include_satellites=False, include_local_sources=True,  use_processor=True)  # Sun
orch.run(include_satellites=False, include_radio_sources=True,  use_processor=True)  # NVSS
orch.run(include_satellites=False, include_galaxy=True,         use_processor=True)  # Galactic diffuse
```

## Related notebooks

- `notebooks/05_radiosource_catalog_end2end.ipynb` — NVSS+SPECFIND TAP ingest,
  filtering, persistence, tracks and flux evaluation.
- `notebooks/00_ALL_IN_ONE.ipynb` — radio/local tracks and TOD.
