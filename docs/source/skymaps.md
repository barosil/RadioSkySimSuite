# Healpix Sky Maps & Map-making

This page covers **HEALPix sky maps** (`radioskysims-skymap`, import
`radioskysims_skymap`) and the **TOD ↔ map** round-trip (projection and
map-making, in `radioskysims-simulation`).

## Domain

```python
from radioskysims_skymap.domain.skymap import (
    SkyMap,
    SkyMapFactory,
    SkyMapOperations,
    NSide,
)

sm = SkyMap(dataset=ds, nside=NSide(64), unit="uK_CMB",
            frame="galactic", freq_ghz=30.0, field="I")

sm2 = SkyMapOperations.smooth(sm, fwhm_deg=1.0)
sm3 = SkyMapOperations.rotate(sm, frame="equatorial")
sm4 = SkyMapOperations.downgrade(sm, nside=32)
```

- `SkyMap` — the entity (`dataset`, `nside`, `unit`, `frame`, `freq_ghz`,
  `field`).
- `NSide`, `SkyMapDataset` — value objects.
- `SkyMapOperations` — `smooth`, `rotate`, `downgrade`.
- `SkyMapFactory.create(...)`, plus `mask` and `analysis` helpers.

## Application / use cases

| Use case | Signature | Purpose |
|---|---|---|
| `GenerateSkyMapUseCase` | `execute(frequency_ghz, nside, components, ...)` | Generate a map from diffuse components (PySM3) |
| `ContinuumSurveyMapUseCase` | `execute(survey_id, ra_deg, dec_deg, fov_deg, nside, ...)` | Fetch a survey cutout |
| `AnalyzeSkyMapUseCase` | `execute(input, lmax, unit, frame, field)` | Power-spectrum / harmonic analysis |

## Infrastructure providers

| Provider | Capabilities |
|---|---|
| `HealpySkyMapProvider` | `read_map`, `read_header`, `write_map` (FITS), `smooth`, `rotate`, `downgrade` |
| `PySMSkyMapGeneratorAdapter` | `generate(freq_ghz, nside, components)` — `unit="uK_CMB"`, `field="I"` |
| `HiPSSkyMapProvider` | `fetch_cutout(...)` — local HiPS FITS cutouts |
| `HealpySkyMapAnalyzer` | `compute_cls(...)` — angular power spectrum |
| `HDF5SkyMapRepository` | Persist/load maps on HDF5 |

## CLI

```bash
# Generate a sky map (PySM3 components)
radioskysims skymap generate --frequency-ghz 30 --nside 64 \
    --components cmb synchrotron dust --output-format text

# Survey cutout
radioskysims skymap survey --survey-id <id> --ra-deg 0 --dec-deg 0 \
    --fov-deg 20 --nside 64

# Analyze a FITS map
radioskysims skymap analyze --input map.fits --lmax 512 --frame galactic
```

## TOD from maps (projection)

The diffuse Galactic contribution is projected onto the TOD by
`HealpySkyMapTODProjector` (in `radioskysims-simulation`), exposed through
`TODSimulator.simulate_from_maps(...)`:

```python
from radioskysims_simulation.infrastructure.skymap.tod_projector import (
    HealpySkyMapTODProjector,
)

proj = HealpySkyMapTODProjector()
pixels = proj.project(skymap, pointing_track, fwhm_rad=None)  # -> xr.DataArray
```

The projector protocol (`SkyMapTODProjector`) allows plugging alternative
implementations.

## Map-making (TOD → map)

`HealpyBinnedMapMakerAdapter.make_map(...)` bins the TOD back into a HEALPix
map:

```python
from radioskysims_simulation.infrastructure.mapmaking.healpy_binned import (
    HealpyBinnedMapMakerAdapter,
)

maker = HealpyBinnedMapMakerAdapter()
res = maker.make_map(
    tod=tod,
    pointing_track=tracks,
    frequency_hz=1.0e9,
    nside=64,
    frame="equatorial",
)
print(res.coverage_fraction)   # fraction of observed pixels
print(res.n_observed_pixels)
```

`MapMakingResult` (`domain/mapmaking/models.py`) carries `skymap`, `hit_map`,
`observed_mask`, `n_samples`, `n_observed_pixels` and `coverage_fraction`.
Use `MapMakingService.run(...)` (`application/services/mapmaking_service.py`)
for orchestration; results can be registered in the `mapmaking_results` table
(see {doc}`database`).

## Round-trip test

The acceptance criterion for this area is an integration test that
reconstructs a map from a simulated TOD (`TOD → mapmaking`). See
{doc}`testing_qa`.

## Related notebooks

- `notebooks/skymap_howto.ipynb` — NSide, SkyMap entity, masks, transforms,
  analysis, use cases, Healpy/PySM3/HiPS adapters, FITS, telemetry.
- `notebooks/50_TOD_SIMULATION.ipynb` — diffuse maps + HEALPix maps in the TOD
  pipeline.
