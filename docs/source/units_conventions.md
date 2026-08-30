# Units & Conventions

This page is the canonical reference for units and conventions across the
project. Keeping these consistent is required for correct physics and for
interoperability between packages.

## Canonical units

| Quantity | Unit | Notes |
|---|---|---|
| Frequency | **MHz** | User-facing (settings, `FrequencyRange`) |
| Angles | **degrees** (user) / **radians** (internal) | Pointing, beam widths, tracks |
| Time | **MJD / UTC** internally; **ISO 8601 strings** as input | `TimeRange` boundaries are ISO strings |
| Time intervals / cadence | **seconds** | `cadence`, `integration_time_s` |
| Flux density | **Jy** | Solar flux, radio catalogs |
| Antenna temperature | **Kelvin** | `T_antenna`, `T_sys_K` |
| Map amplitude | **µK_CMB** (default) | `SkyMap.unit` |

## Per-component conventions

| Component | Convention |
|---|---|
| `FrequencyRange` (`radioskysims-core`) | `min_mhz`, `max_mhz`, `resolution_mhz` |
| TOD dataset `frequency` coordinate | **Hz** (converted from MHz at the boundary; `SimulationResult` derives its `FrequencyRange` from it) |
| `SkyMap.freq_ghz` | GHz (e.g. PySM3 components) |
| `TODSimulator` units | `"W/Hz"` (total power, 1/r² applied) or `"W/m²/Hz"` (flux density) |
| Map-making `frequency_hz` | Hz |
| Beam | amplitude vs angle, normalized in **dB** for plots; FWHM in degrees; gain in dBi |
| Waterfall | canonical dims `("time", "freq")`; frequency coordinate in Hz |

## Frames & pointing

- Sky maps default to the **galactic** frame (`SkyMap.frame="galactic"`);
  equatorial is supported via rotation.
- `Pointing` mode `"transit"` with `alt_deg`/`az_deg` (or `ra_deg`/`dec_deg`
  for equatorial pointing).
- Tracks/geometry computed with Skyfield in MJD/UTC.

## Settings input

All time inputs in `settings.toml` are ISO 8601 strings, e.g.
`time_range = ["2025-02-27T00:00:00", "2025-02-28T00:00:00", 120]` where the
third element is the cadence in **seconds**.

## Validation

When in doubt, the `FrequencyRange`, `TimeRange`, `Observer` and `AngularRange`
value objects in `radioskysims-core.domain.common` enforce these units at
construction time.
