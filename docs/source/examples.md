# Examples & Notebooks

Executable examples demonstrate the main end-to-end flows. The notebooks below
are rendered from the versions under `docs/source/examples/` (curated copies),
showing their **cached outputs** from the last run. The canonical sources live
in `notebooks/` at the repository root.

```{note}
The notebooks are rendered with their stored outputs
(`nb_execution_mode = "off"`). To re-execute and cache fresh outputs, set
`nb_execution_mode = "cache"` in `docs/source/conf.py` (requires
`jupyter-cache` and a kernel that can reach the DB / network services).
```

```{toctree}
:maxdepth: 1
:caption: Rendered examples

examples/01_domain_common
examples/02_beam_end_to_end
examples/03_satellite_signal_tracks_demo
examples/04_generate_satellite_tracks
examples/05_radiosource_catalog_end2end
examples/50_TOD_SIMULATION
examples/50_TOD_Visualization
examples/tod_background_job
```

## Additional notebooks

The following larger notebooks are not copied into the docs tree (to keep the
build lean) but are available in the repository:

| Notebook | Flow | Link |
|---|---|---|
| `00_RADIOSKYSIM_COMPLETE_DEMO.ipynb` | Full DDD/hexagonal overview: SkyMap, Beam, RFI, Noise, Satellite, TOD, Simulation | {download}`notebook <../../notebooks/00_RADIOSKYSIM_COMPLETE_DEMO.ipynb>` |
| `00_ALL_IN_ONE.ipynb` | All main features (DB, PSD panels, tracks, SkyChart, pointing, full TOD + waterfall) | {download}`notebook <../../notebooks/00_ALL_IN_ONE.ipynb>` |
| `skymap_howto.ipynb` | SkyMap end-to-end (NSide, masks, transforms, analysis, providers) | {download}`notebook <../../notebooks/skymap_howto.ipynb>` |
| `99_uirapuru.ipynb` | Uirapuru calibration study (Sun + GNSS in-beam) | {download}`notebook <../../notebooks/99_uirapuru.ipynb>` |
| `51_signal_chain_verification.ipynb` | Physics verification of $T_A$ / $S$ vs. reference radiometry | {download}`notebook <../../notebooks/51_signal_chain_verification.ipynb>` |

## Keeping the examples in sync

When a notebook under `notebooks/` is updated, refresh the copy used by the
docs:

```bash
cp notebooks/<name>.ipynb docs/source/examples/<name>.ipynb
```

Each example states its prerequisites (database running, network access for
TLE/catalogs) in its first markdown cell — see {doc}`contributing`.
