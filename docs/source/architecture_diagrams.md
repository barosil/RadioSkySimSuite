# Architecture, Diagrams & Sequence Flows

The canonical, continuously maintained architecture document is
{download}`architecture.md <../architecture.md>`. This page collects the
diagrams and sequence flows for the main use cases, matching the current
decoupled package layout.

## Layered architecture

RadioSkySim follows **Hexagonal (Ports & Adapters)**:

```mermaid
flowchart LR
    subgraph Interfaces["Interfaces (CLI / GUI / API)"]
        CLI[radioskysims · gnss4astro]
        GUI[Panel apps]
    end
    subgraph App["Application (use cases + ports)"]
        ORCH[SimOrchestrator / Services]
        PORTS[Ports / contracts]
    end
    subgraph Domain["Domain (entities + value objects)"]
        CORE[radioskysims-core]
        BEAM[radioskysims-beam]
        SKY[radioskysims-skymap]
        SRC[radioskysims-sources]
        SIM[radioskysims-simulation]
        WF[radioskysims-waterfall]
    end
    subgraph Infra["Infrastructure (adapters)"]
        DB[(PostgreSQL / SQLModel)]
        FILES[(HDF5 · Zarr · NetCDF · FITS)]
        SKYF[Skyfield · Healpy · PySM3 · HiPS]
        TAP[astroquery/TAP · SpaceTrack · Celestrak]
    end
    Interfaces --> App
    App --> Domain
    Domain --> Infra
    Infra -.implements.-> PORTS
    UMB[radioskysim - umbrella / composition root] --> Interfaces
```

## Package dependency graph

```mermaid
flowchart LR
    subgraph Kernel["Kernel compartilhado"]
        CORE[radioskysims-core]
        VIZ[radioskysims-viz]
    end
    subgraph Dominios["Radio domains"]
        BEAM[radioskysims-beam]
        SKYMAP[radioskysims-skymap]
        RT[radioskysims-radiotelescope]
        SRC[radioskysims-sources]
        SIM[radioskysims-simulation]
        WF[radioskysims-waterfall]
    end
    subgraph Infra["Infraestrutura"]
        GNSS[gnsstools4astro]
    end
    UMB[radioskysim - umbrella]

    BEAM --> CORE
    BEAM --> VIZ
    SKYMAP --> CORE
    RT --> CORE
    RT --> VIZ
    SRC --> CORE
    SRC --> SKYMAP
    SIM --> CORE
    SIM --> VIZ
    SIM --> BEAM
    SIM --> SKYMAP
    SIM --> SRC
    SIM --> RT
    UMB --> CORE & VIZ & BEAM & SKYMAP & RT & SRC & SIM & WF & GNSS
```

## Sequence: TOD simulation (main use case)

```mermaid
sequenceDiagram
    participant User as User / CLI / Notebook
    participant Orch as SimOrchestrator<br/>(Application)
    participant SatSvc as SatelliteService<br/>(radioskysims-sources)
    participant Track as TrackFactory<br/>(radioskysims-core)
    participant Signal as SignalFactory<br/>(radioskysims-sources)
    participant TOD as TODSimulator<br/>(radioskysims-simulation)
    participant Proc as ResourceAwareProcessor<br/>(Infrastructure)

    User->>Orch: from_settings(telescope="uirapuru")
    Orch->>Orch: build context (observer, time range,<br/>frequency range, antennas)
    User->>Orch: run(constellations=["GPS"], use_processor=True)

    alt satellites enabled
        Orch->>SatSvc: get_by_constellations(["GPS"])
        SatSvc-->>Orch: list[Satellite]
        Orch->>Track: build tracks (Skyfield)
        Orch->>Signal: build PSD signals
    end

    Orch->>Proc: process sources in memory-safe batches
    Proc->>TOD: simulate_from_source(source, beam, ...)
    TOD-->>Proc: xr.Dataset (T_antenna)
    Proc-->>Orch: consolidated lazy dataset (dask)

    Orch-->>User: SimulationOrchestratorResult
    User->>Orch: compute() / format_summary() / save_result(path)
```

## Sequence: background job execution (planned)

```{note}
The background job runner (`tod export --background`, `jobs list/status/
cancel`) and the notebook `JobHandle`/widget are **planned** — see
`docs/tasks/tod_cli_background_tickets.md`. The diagram below captures the
target flow.
```

```mermaid
sequenceDiagram
    participant User as User
    participant CLI as radioskysims tod export
    participant DB as Jobs DB (SQLite/Postgres)
    participant Worker as Worker subprocess
    participant Out as Output (NetCDF/Zarr)

    User->>CLI: tod export --config settings.toml --background
    CLI->>DB: create job (status=RUNNING)
    CLI-->>User: job id
    Worker->>Worker: load settings, run TOD pipeline
    Worker->>DB: update progress (percent/step/eta)
    Worker->>Out: write dataset
    Worker->>DB: update status=SUCCESS + output_path
    User->>CLI: tod jobs status <id>
    CLI-->>User: RUNNING/SUCCESS + progress + output_path
```

## Diagram assets

Existing diagram sources (editable, Mermaid/draw.io):

| File | Content |
|---|---|
| `docs/source/diagrams/radioskysim_ddd_architecture.mmd` | DDD class map (domain / application / infrastructure / external) |
| `docs/source/diagrams/radioskysim_sequence_diagram.mmd` | Simulation sequence (setup, satellites, signals) |
| `docs/source/diagrams/simulation_sequence_detailed.mmd` | Detailed TOD sequence |
| `docs/source/diagrams/skymap_domain_class.mmd`, `map_domain_class.mmd`, `map_domain_package.mmd` | SkyMap / domain maps |
| `docs/source/diagrams/radioskysim_architecture_uml.mmd` / `.drawio.svg` | Architecture UML |
| `docs/diagrams/architecture.mmd`, `uml_*.mmd`, `classes_and_sequence_*.mmd`, `usecase_*.mmd` | Historical UML + use-case diagrams |
| `docs/architecture.md` | Canonical architecture doc (Mermaid) |

## Class / ER diagrams (DB)

The persistence schema (tables, models and relationships) is documented in
{doc}`database`. Class-level diagrams for the beam, satellite and skymap
domains are in the assets listed above.

## How to update

1. Edit the `.mmd` source (Mermaid) or `.drawio` file.
2. Re-export static images (`.svg`/`.png`) if the build relies on them.
3. Validate the Mermaid syntax before committing (use the Mermaid validator
   and preview in the editor).
4. Keep `docs/architecture.md` in sync — it is the canonical reference.
