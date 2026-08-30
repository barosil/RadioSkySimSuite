# Performance, Dask & Tuning

Simulations can produce very large TOD datasets. This page explains the
memory-aware machinery (`ResourceAwareProcessor`, `SystemMonitor`) and how to
tune Dask execution.

## `ResourceAwareProcessor`

Located in `radioskysims-simulation`:
`radioskysims_simulation.infrastructure.processing.resource_processor`.

It splits sources into **memory-safe batches** and merges the resulting TODs,
streaming to disk when the estimated output exceeds available memory (the full
dataset is never materialized in RAM).

```python
from radioskysims_simulation.infrastructure.processing.resource_processor import (
    ResourceAwareProcessor,
)

proc = ResourceAwareProcessor(
    resources=None,                # auto-detect
    max_batch_mb=2048,
    dask_scheduler="threads",      # "threads" | "synchronous" | "distributed"
    dask_processes=True,
    diagnostics_enabled=False,
)
```

Companion types:

- `ProcessingResources.detect()`, `usable_memory_mb()`, `usable_cpu_count()`
- `MemoryEstimator.estimate_source_mb(...)`, `estimate_total_output_mb(...)`
- `SourceBatch`, `BatchResult`, `ResourceLimitError`

With `dask_scheduler="distributed"` a **`LocalCluster` + `Client`** is started
and the dashboard URL is logged.

## Using it from `SimOrchestrator`

Pass the processor flags directly to `run(...)`:

```python
result = orch.run(
    constellations=["GPS"],
    use_processor=True,
    max_batch_mb=2048,
    cpu_count=4,
    memory_mb=16384,
    dask_scheduler="distributed",
    dask_processes=True,
    batch_output_dir="data/TOD/batches",
    processor_diagnostics=False,
)
```

## `SystemMonitor`

`radioskysims_core.monitor.system_monitor` provides runtime resource checks:

```python
from radioskysims_core.monitor.system_monitor import (
    SystemMonitor,
    check_resources,
)

snap = SystemMonitor().snapshot(disk_path="data")
print(snap.available_memory_mb, snap.cpu_count)

# raises if the estimated footprint does not fit:
check_resources(estimated_mb=..., ...)
```

## Settings knobs (`[processing]`)

| Key | Default | Meaning |
|---|---|---|
| `max_batch_mb` | auto | Memory limit per batch (MB) |
| `cpu_count` | auto | Number of CPUs to use |
| `dask_scheduler` | `"threads"` | `threads` / `synchronous` / `distributed` |
| `dask_processes` | `true` | Separate processes for distributed workers (isolation); `false` → 1 worker with threads |

## Chunking

- `Tracks.get_chunks()` / `get_chunks_info()` (`radioskysims-core`) and
  `set_chunks` (`radioskysims-sources.domain.satellite.chunks`) control dataset
  chunking.
- `SimulationEvents` are extracted **chunk-wise by time** — materialize only the
  slices you need instead of the whole dataset.
- `SimulationResult.to_zarr(..., chunk_s=..., target_mb=64.0)` re-chunks
  uniformly before writing.

## Tuning guide

1. **Start small** — run `use_processor=True` with default (auto) limits on a
   short `time_range`.
2. **Inspect the summary** — `result.format_summary()` reports dataset
   dimensions, chunks and size (MB) in the `computation` block.
3. **Raise `max_batch_mb`** gradually if batches are too small and memory
   allows; keep it below `SystemMonitor` available memory.
4. **Prefer `dask_scheduler="threads"`** for single-node runs; switch to
   `"distributed"` when you need process isolation or the dashboard.
5. **Watch disk** for streaming batches (`batch_output_dir`); ensure free
   space for the expected output.

```{note}
**HPC path (planned):** the MVP targets a single node with `LocalCluster`.
The roadmap documents moving to `dask-mpi`/multi-node for HPC; this is not yet
implemented.
```

## Benchmarks (planned)

A reproducible **mini-bench** (task `PERF-003` in the planning docs) is
planned. Until then, `notebooks/99_uirapuru.ipynb` and the
`scripts/*experiment*.py` scripts provide representative runtimes and scaling
observations.
