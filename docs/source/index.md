# 📡 RadioSkySim

Simulation and analysis of the radio sky as seen by a **single-dish radio
telescope in transit mode**, developed by the **BINGO collaboration**.

RadioSkySim models antenna beams, GNSS satellites, local sources (Sun), radio
source catalogs (NVSS/TAP), and synthesizes **Time Ordered Data (TOD)** and
**HEALPix sky maps**. It follows a **Hexagonal (Ports & Adapters)** architecture
and is organized as a **uv workspace** of decoupled packages, with a thin
umbrella package (`radioskysim`) acting as the composition root (CLI/GUI).

```{toctree}
:maxdepth: 1
:caption: Getting Started

installation
quickstart
configuration
```

```{toctree}
:maxdepth: 1
:caption: Scientific Domains

radiotelescope
satellites
sources
skymaps
simulation
waterfall
```

```{toctree}
:maxdepth: 1
:caption: Examples

examples
```

```{toctree}
:maxdepth: 1
:caption: Core Concepts

architecture_diagrams
units_conventions
file_formats
database
performance
```

```{toctree}
:maxdepth: 1
:caption: Engineering & Project

testing_qa
release_changelog
history_cleanup
contributing
```

```{toctree}
:maxdepth: 1
:caption: Appendix

legacy_notes
barosi_docs
vanderson_docs
```

```{toctree}
:maxdepth: 1
:caption: API Reference

api
```

## Highlights

- **TOD synthesis** with memory-aware batching (`ResourceAwareProcessor` +
  Dask) — discrete sources (satellites, Sun, radio sources) and diffuse
  Galactic/HEALPix maps.
- **Satellite pipeline** — TLE (Celestrak/SpaceTrack) → tracks (Skyfield) →
  PSD (BPSK/QPSK/BOC/CBOC) → `signals.json`.
- **Sky maps** — generation and analysis of HEALPix maps via Healpy, PySM3 and
  HiPS providers.
- **Waterfall** — time × frequency datasets with a chainable pipeline
  (masking, baseline, filtering) and interactive HoloViews/Datashader plots.
- **Radiotelescope** — telescope/antenna/backend specifications driven by
  `settings.toml`, with an interactive Panel UI.

## Package ecosystem

| Package (import name) | Purpose |
|---|---|
| `radioskysims-core` | Shared kernel: config, DB, logging, paths, geometry, tracks, common domain |
| `radioskysims-beam` | Beam domain, loaders (CSV/analytical), repository, panel |
| `radioskysims-skymap` | HEALPix sky maps, generation, analysis, HiPS |
| `radioskysims-radiotelescope` | Telescope, antenna and backend specifications |
| `radioskysims-sources` | Signal sources: satellites, Sun/local, radio catalogs |
| `radioskysims-simulation` | TOD, simulation, noise/RFI, mapmaking, orchestration |
| `radioskysims-waterfall` | Waterfall (time×freq) management and visualization |
| `radioskysims-viz` | Base visualization (Panel) ports and application |
| `gnsstools4astro` | GNSS/RINEX tools for astronomy |

## Architecture reference

The canonical architecture document (kept continuously updated) lives at
{download}`architecture.md <../architecture.md>`. See also
{doc}`architecture_diagrams` for C4/sequence and class/ER diagrams.

## Project notes (legacy)

Historical working notes from the early project phase are preserved under
{doc}`legacy_notes`, {doc}`barosi_docs` and {doc}`vanderson_docs`; they document
the pre-decoupling monolithic layout and are kept for traceability.
