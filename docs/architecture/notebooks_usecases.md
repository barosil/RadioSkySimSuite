# Casos de Uso dos Notebooks — Sequence Diagrams

**Data:** 2026-09-01

Este documento mapeia explicitamente cada notebook de exemplo
(`notebooks/`) para diagramas de sequência (Mermaid) que refletem as
chamadas reais de API observadas no código das células. Complementa
[`architecture.md §8`](architecture.md) e os diagramas legados em
`docs/diagrams/usecase_*.mmd` (que descrevem os *casos de uso* em nível de
domínio, não a sequência de chamadas do notebook).

| Notebook | Seção | Diagrama |
|---|---|---|
| `00_examples.ipynb` | §2 Radiotelescope & Beam | [§1](#1-radiotelescope--beam-00_examplesipynb-2) |
| `00_examples.ipynb` | §3 Satélites via TLE | [§2](#2-satélites-via-tle-00_examplesipynb-3) |
| `00_examples.ipynb` | §3 Satélites via RINEX | [§3](#3-satélites-via-rinex-00_examplesipynb-3) |
| `00_examples.ipynb` | §4 Local Sources (Sun) | [§4](#4-local-sources-sol-00_examplesipynb-4) |
| `00_examples.ipynb` | §5 Radio Sources (NVSS) | [§5](#5-radio-sources-nvss-00_examplesipynb-5) |
| `01_maps.ipynb` | §7 `SkyMapManager` (fluxo unificado) | [§6](#6-skymap-fluxo-unificado-01_mapsipynb-7) |
| `02_sims.ipynb` (vazio — gap documentado) | Fluxo `SimOrchestrator` (via `quickstart.md`) | [§7](#7-simulaçãotod-simorchestrator-02_simsipynb--gap) |

> **Nota sobre o gap**: `02_sims.ipynb` está vazio na branch
> `feature/sims-notebook` — o diagrama §7 é derivado do fluxo documentado em
> `docs/source/quickstart.md` e serve como especificação para o notebook
> ainda a ser escrito (ver `relatorio_set_2026_v2.md §11`, sugestão de nova
> feature).

## 1. Radiotelescope & Beam (`00_examples.ipynb` §2)

```mermaid
sequenceDiagram
    actor User
    participant NB as Notebook
    participant Fac as create_radiotelescope()
    participant RT as RadiotelescopeConfig
    participant Obs as Observer (holoviews)

    User->>NB: create_radiotelescope("uirapuru")
    NB->>Fac: create_radiotelescope(profile)
    Fac->>RT: build_configuration("uirapuru")\n(radioskysims-radiotelescope, via settings.toml)
    RT-->>Fac: RadiotelescopeSpec (antennas, observer)
    Fac-->>NB: uirapuru
    NB->>RT: print(uirapuru) / print(uirapuru.antennas)
    NB->>Obs: uirapuru.observer.view()
    Obs-->>User: mapa interativo (tiles OSM)
```

## 2. Satélites via TLE (`00_examples.ipynb` §3)

```mermaid
sequenceDiagram
    actor User
    participant NB as Notebook
    participant DB as Database (radioskysims-core)
    participant Build as build_repositories()
    participant Mgr as SatelliteManager
    participant Repo as SatelliteRepository (Postgres)

    User->>NB: db = Database()
    NB->>DB: __init__() (engine PostgreSQL)
    User->>NB: repos = build_repositories(db)
    NB->>Build: build_repositories(db)
    Build-->>NB: {satellite_repository, signal_repository}
    User->>NB: mgr = SatelliteManager(repository, signal_repository, epoch=REF_DATE)
    User->>Mgr: sats = mgr.create_from_constellations(["GPS", "GALILEO"])
    Mgr->>Repo: query TLEs (constellations, epoch)
    Repo-->>Mgr: TLEs deduplicados por NORAD ID
    Mgr-->>NB: sats
    User->>Mgr: assembled = mgr.build(TR, FR)
    Mgr-->>NB: SatelliteAssembled (tracks + signals)
    NB->>NB: assembled.plot_tracks(by="constellation", contours=True)
    NB->>NB: assembled.plot_signals()
    NB->>NB: assembled.select_Constellation("GPS")\nassembled.select_Satellite(noradID=...)
```

## 3. Satélites via RINEX (`00_examples.ipynb` §3)

```mermaid
sequenceDiagram
    actor User
    participant NB as Notebook
    participant RMgr as RinexSatelliteManager (gnsstools4astro)
    participant RBMC as Estação RBMC (pbcg)
    participant LB as EstimateLinkBudgetUseCase

    User->>RMgr: RinexSatelliteManager.for_station("pbcg", ref_date, cache_dir)
    User->>RMgr: nav_path = rmgr.download_nav()
    RMgr->>RBMC: download NAV (cache local ou online)
    RBMC-->>RMgr: arquivo NAV
    User->>RMgr: obs_path = rmgr.download_obs()
    RMgr->>RBMC: download OBS (cache local ou online)
    RBMC-->>RMgr: arquivo OBS (ou indisponível)
    User->>RMgr: rinex_assembled = rmgr.build(TR, FR)
    RMgr-->>NB: RinexAssembled (tracks + signals PSD analítica)
    NB->>NB: rinex_assembled.plot_tracks() / plot_signals()
    alt OBS disponível
        User->>RMgr: estimates = rmgr.estimate_link_budget(obs_path)
        User->>LB: lb = EstimateLinkBudgetUseCase(get_constellation_signals())
        User->>LB: lb.summarize(estimates)
        LB-->>NB: EIRP estimada por banda (C/N0 obs + range nav)
        NB->>NB: lb.to_signals_reference(estimates, base=...) → signals.json
    end
```

## 4. Local Sources / Sol (`00_examples.ipynb` §4)

```mermaid
sequenceDiagram
    actor User
    participant NB as Notebook
    participant Cache as cache local (data/solar_flux)
    participant Dl as SolarFluxDownloader
    participant Sun as Sun (application/services)

    User->>NB: load_or_download(name="fluxo solar (SRD/SRS)", local, download)
    NB->>Cache: verifica solar_<data>.nc
    alt cache existe
        Cache-->>NB: SolarFlux (dataset em cache)
    else cache ausente
        NB->>Dl: SolarFluxDownloader(timeout_sec=60).fetch(center_utc, window_hours=24)
        Dl-->>NB: SolarFlux (download real SRD/SRS)
        NB->>Cache: solar_flux.dataset.to_netcdf(cache_path)
    end
    User->>Sun: sun = Sun.simulated(observer=OBSERVER, time_range=TR, flux=solar_flux)
    Sun-->>NB: sun (track via Skyfield + fluxo real)
    NB->>NB: sun.view_skychart() / sun.view_mollweide() / sun.flux_density().view()
```

## 5. Radio Sources / NVSS (`00_examples.ipynb` §5)

```mermaid
sequenceDiagram
    actor User
    participant NB as Notebook
    participant Mgr as RadioSourcesManager
    participant DB as banco radio_sources (Postgres)
    participant TAP as TAP VizieR (NVSS + SPECFIND)

    User->>Mgr: radiosources = RadioSourcesManager.get_radio_sources()
    Mgr->>DB: query catálogo (323 fontes NVSS reais)
    DB-->>Mgr: fontes com α (índice espectral)
    Mgr-->>NB: radiosources
    NB->>NB: view_mollweide() / view_flux_density()
    User->>Mgr: bright = radiosources.select(min_flux_jy=1.0)
    Mgr-->>NB: bright (subset)
    User->>Mgr: tap = RadioSourcesManager.from_tap(ra/dec range, smin_jy=0.1)
    Mgr->>TAP: query ADQL (NVSS + SPECFIND, prior de α quando ausente)
    TAP-->>Mgr: fontes reais na janela do céu
    Mgr-->>NB: tap
```

## 6. SkyMap — fluxo unificado (`01_maps.ipynb` §7)

O `SkyMapManager` (pacote `radioskysims-skymap`) encadeia geração →
suavização → máscara → análise → I/O em uma única fachada, substituindo o
uso direto de `SkyMapFactory` + `SkyMapOperations` + `SkyMask` +
`SkyMapAnalysis` + `HealpySkyMapProvider` (seções 2–6 do mesmo notebook).

```mermaid
sequenceDiagram
    actor User
    participant NB as Notebook
    participant SMM as SkyMapManager
    participant Fac as SkyMapFactory (domain)
    participant Ops as SkyMapOperations (domain)
    participant Mask as SkyMask (domain)
    participant Ana as SkyMapAnalysis (domain)
    participant IO as HealpySkyMapProvider (infrastructure)

    User->>SMM: handle = SkyMapManager.create_map_from_coefficients(\ncls_input, nside, lmax, seed, unit, freq_ghz)
    SMM->>Fac: create(dataset=hp.synfast(cls_input, ...), nside, freq_ghz)
    Fac-->>SMM: SkyMap
    SMM-->>NB: handle (fachada sobre SkyMap)
    User->>SMM: handle.smooth(fwhm_deg=...)
    SMM->>Ops: SkyMapOperations.smooth(data, fwhm_rad)
    Ops-->>SMM: dados suavizados
    User->>SMM: handle.mask(mask_half_sky)
    SMM->>Mask: SkyMask.apply(data, mask)
    Mask-->>SMM: dados mascarados
    User->>SMM: handle.stats() / handle.cls()
    SMM->>Ana: mean()/rms()/min_max()/angular_spectrum()
    Ana-->>SMM: estatísticas + Cℓ
    User->>SMM: handle.save(path)
    SMM->>IO: write_map(skymap, path, overwrite=True)
    IO-->>SMM: path (FITS)
    User->>SMM: handle.plot()
    SMM-->>NB: figura (SkyMapVisualizer)
```

## 7. Simulação/TOD — `SimOrchestrator` (`02_sims.ipynb` — gap)

Baseado em `docs/source/quickstart.md` (não há notebook correspondente
ainda — ver observação no topo deste documento).

```mermaid
sequenceDiagram
    actor User
    participant Orch as SimOrchestrator
    participant Boot as bootstrap (from_settings)
    participant Proc as ResourceAwareProcessor
    participant Result as SimulationOrchestratorResult
    participant FS as HDF5/Zarr (data/TOD)

    User->>Orch: orch = SimOrchestrator.from_settings(telescope="uirapuru")
    Orch->>Boot: monta contexto a partir de settings.toml\n(radiotelescope + beam + fontes)
    Boot-->>Orch: SimulationContext
    User->>Orch: result = orch.run(constellations=["GPS"],\ninclude_satellites=True, use_processor=True)
    Orch->>Proc: particiona fontes em batches (max_batch_mb)
    Proc-->>Orch: dataset lazy (dask)
    Orch-->>User: SimulationOrchestratorResult (lazy)
    User->>Result: ds = result.compute()
    Result-->>User: xr.Dataset materializado
    User->>Result: print(result.format_summary())
    User->>Result: sidecar_path = result.save_result("data/TOD/gps_tod.nc")
    Result->>FS: to_hdf5(...) / to_zarr(...) + sidecar JSON
    FS-->>Result: gps_tod.nc + gps_tod.nc.json
    Note over User,Result: Reload posterior sem reexecutar:\nSimulationOrchestratorResult.load_result(path)
```

## Recomendações

1. Escrever `notebooks/02_sims.ipynb` seguindo exatamente o diagrama §7 —
   fecha o gap identificado em `relatorio_set_2026_v2.md §11` (Simulation é
   o maior pacote do monorepo e o único bounded context sem notebook).
2. Ao evoluir os notebooks, manter este documento sincronizado — cada nova
   seção relevante de `00_examples.ipynb`/`01_maps.ipynb`/`02_sims.ipynb`
   deve ganhar (ou atualizar) o sequence diagram correspondente aqui.
