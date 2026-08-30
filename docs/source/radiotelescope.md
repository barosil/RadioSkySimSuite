# Radiotelescope

The `radioskysims-radiotelescope` package (import `radioskysims_radiotelescope`)
defines the **telescope, antenna and backend** specifications used by
simulations, plus an interactive Panel UI.

## Domain model

| Class | Location | Role |
|---|---|---|
| `Radiotelescope` | `domain/radiotelescope/models.py` | SQLModel value object (table `radiotelescopes`) — `earth_location_lat/lon/alt`, `frequency_min/max`, `beam_id`; property `frequency_range` |
| `RadiotelescopeSpec` | `domain/radiotelescope/specs.py` | Named spec: `name`, `observer` (`Observer` from core), `antennas: list[Antenna]` |
| `Antenna` | `domain/radiotelescope/antenna/models.py` | `name`, `effective_area_m2`, `frequency_range`, `pointing`, `beam`, `backend` |
| `Pointing` | `antenna/models.py` | `mode` (`"transit"`), `alt_deg`, `az_deg`, `params` |
| `BeamSpec` | `antenna/models.py` | file-based (`beam_pattern_file`) or analytical (`profile` + `beam_width_deg`) |
| `SpectrometerBackend` | `domain/radiotelescope/backend/spectrometer/models.py` | `kind`, `bandwidth_mhz`, `sampling_rate_mhz`, `integration_time_s`, `num_channels`, `system_temperature_k`; `as_dict()` |

## Instantiating a telescope

### Inline (programmatic)

```python
from radioskysims_radiotelescope.domain.radiotelescope.factory import (
    RadiotelescopeFactory,
)

rt = RadiotelescopeFactory.create(
    lat=-7.211637,
    lon=-35.90813,
    alt=530.0,
    freq_min=1000.0,   # MHz
    freq_max=1250.0,   # MHz
    beam_id=None,
)
print(rt.frequency_range)
```

### From `settings.toml`

The recommended path is to declare a **telescope profile** in `settings.toml`
under `[radiotelescopes.<name>]` and build it from configuration:

```python
from radioskysims_core.config.config_loader import build_radiotelescope_from_settings

spec = build_radiotelescope_from_settings("uirapuru")
```

`SimOrchestrator.from_settings(telescope="uirapuru")` does exactly this when
setting up a simulation (see {doc}`simulation`). The package also exposes
`bootstrap/builders.py::build_configuration(telescope="default", settings_file=None)`
which returns `observer`, `time_range`, `frequency_range` and the antenna spec.

### Settings example

```toml
[radiotelescopes.uirapuru]
name = "UIRAPURU Telescope"

[radiotelescopes.uirapuru.observer]
lat = -7.211637
lon = -35.90813
height = 530.0

[[radiotelescopes.uirapuru.antennas]]
name = "BINGO Horn"
frequency_range = [1000, 1250, 0.05]

[radiotelescopes.uirapuru.antennas.pointing]
mode = "transit"
alt_deg = 65
az_deg = 0

[radiotelescopes.uirapuru.antennas.beam]
name = "BINGO Horn LIT"
polarizations = ["H_COPOL"]
beam_width_deg = 15.0
pattern_file = "radioskysims/resources/beams/beampattern_horn01.csv"

[radiotelescopes.uirapuru.antennas.backend]
type = "spectrometer"
frequency_range = [1000, 1250, 0.05]
name = "UIRAPURU Backend"
bandwidth_mhz = 250
sampling_rate_mhz = 250
integration_time_s = 1
num_channels = 5000
T_sys_K = 50
```

## Interactive panel

`application/radiotelescope_panel.py` provides a Panel-based UI that lets you
pick the observer location, frequency range and beam, and builds the
`Radiotelescope` object through the factory — the same widget stack used in
the legacy GUI (`src/radioskysims/main.py` serves a Panel app).

## Visualization (planned)

```{warning}
The OSM/beam plotting utility (task `RT-002` in the planning docs) is
**planned but not implemented**. Today, beam pattern plots come from
`radioskysims-beam` visualization helpers and the interactive beam panels in
`radioskysims-viz` (HoloViews/Panel). See {doc}`waterfall` for the generic
visualization stack.
```
