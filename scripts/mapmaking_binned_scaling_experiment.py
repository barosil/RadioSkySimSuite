#!/usr/bin/env python3
"""
Experimento para caracterizar numericamente o `HealpyBinnedMapMakerAdapter`.

Gera um TOD sintético a partir de um campo analítico S(ra,dec), reconstrói mapas
para vários NSIDE e diferentes números de amostras, e reporta métricas.

Saída: JSON estruturado impresso no stdout e tabela legível.

Não altera o algoritmo do mapmaker. Determinístico.
"""

from __future__ import annotations

import json
import math
import sys
import threading
import time
from collections.abc import Callable
from statistics import median

import numpy as np
import xarray as xr

try:
    import healpy as hp
except Exception:
    print("healpy is required to run this script.", file=sys.stderr)
    raise

from radioskysims_simulation.infrastructure.mapmaking.healpy_binned import (
    HealpyBinnedMapMakerAdapter,
)


def sky_function(ra: np.ndarray, dec: np.ndarray) -> np.ndarray:
    """Campo analítico: combinação suave de harmônicos simples.

    ra, dec em radianos.
    """
    return np.sin(dec) + 0.5 * np.cos(2.0 * ra)


def build_tod_and_pointing(nt: int) -> tuple[xr.Dataset, xr.Dataset]:
    """Constrói um TOD e track de pointing determinísticos.

    - RA varre 0..2π uniformemente em `nt` pontos.
    - Dec fixo em 0 (equador) para simplificar cobertura previsível.
    - Frequência única 1 GHz.
    - T_antenna é exatamente `sky_function(ra,dec)` avaliado nos pontos.
    """
    times = np.arange(nt).astype("datetime64[s]")

    ra = np.linspace(0.0, 2.0 * np.pi, num=nt, endpoint=False)
    dec = np.zeros_like(ra)

    temperature = xr.DataArray(
        np.asarray(sky_function(ra, dec), dtype=float).reshape((nt, 1)),
        dims=("time", "frequency"),
        coords={"time": times, "frequency": np.array([1.0e9])},
        attrs={"units": "K"},
    )

    tod = xr.Dataset(data_vars={"T_antenna": temperature})

    pointing = xr.Dataset(
        data_vars={
            "ra": xr.DataArray(ra, dims=("time",), coords={"time": times}, attrs={"units": "rad"}),
            "dec": xr.DataArray(
                dec, dims=("time",), coords={"time": times}, attrs={"units": "rad"}
            ),
        }
    )

    return tod, pointing


def compute_reference_map(
    nside: int, sky_fn: Callable[[np.ndarray, np.ndarray], np.ndarray]
) -> np.ndarray:
    """Avalia a função de céu nos centros dos pixels HEALPix para `nside`."""
    npix = hp.nside2npix(nside)
    theta, phi = hp.pix2ang(nside, np.arange(npix), nest=False)
    # theta = colatitude, phi = longitude; convert to RA/Dec
    dec = np.pi / 2.0 - theta
    ra = phi
    return np.asarray(sky_fn(ra, dec), dtype=np.float64)


class PeakRSSMonitor:
    def __init__(self, interval: float = 0.01) -> None:
        self.interval = interval
        self._running = False
        self._peak: int = 0
        self._thread: threading.Thread | None = None

        try:
            import psutil

            self._psutil = psutil
        except Exception:
            self._psutil = None

    def _sample(self) -> None:
        proc = self._psutil.Process() if self._psutil is not None else None
        while self._running:
            if proc is not None:
                rss = int(proc.memory_info().rss / (1024 * 1024))
                self._peak = max(self._peak, rss)
            time.sleep(self.interval)

    def __enter__(self):
        if self._psutil is None:
            return self
        self._running = True
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._psutil is None:
            return
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    @property
    def peak_mb(self) -> int | None:
        return self._peak if self._psutil is not None else None


def pixel_scale_deg(nside: int) -> float:
    npix = hp.nside2npix(nside)
    area_sr = 4.0 * math.pi / float(npix)
    ang_rad = math.sqrt(area_sr)
    return math.degrees(ang_rad)


def run_nside_sweep(nsides: list[int], nt: int, runs_per_setting: int = 5) -> list[dict]:
    adapter = HealpyBinnedMapMakerAdapter()
    tod, pointing = build_tod_and_pointing(nt)

    results: list[dict] = []

    for nside in nsides:
        npix = hp.nside2npix(nside)
        ref = compute_reference_map(nside, sky_function)

        # warm-up
        adapter.make_map(tod=tod, pointing_track=pointing, frequency_hz=1.0e9, nside=nside)

        times: list[float] = []
        peaks: list[int | None] = []
        reconstructions: list[np.ndarray] = []

        for _ in range(runs_per_setting):
            monitor = PeakRSSMonitor()
            start = time.perf_counter()
            with monitor:
                result = adapter.make_map(
                    tod=tod, pointing_track=pointing, frequency_hz=1.0e9, nside=nside
                )
            end = time.perf_counter()

            times.append(end - start)
            peaks.append(monitor.peak_mb)
            reconstructions.append(result.skymap.data)

        # choose median time and peak
        time_median = float(median(times))
        # pick max peak across runs if available
        peak_values = [p for p in peaks if p is not None]
        memory_peak = int(max(peak_values)) if peak_values else None

        # use last reconstruction for per-pixel comparison
        recon = reconstructions[-1]

        hit_map = result.hit_map
        observed = result.observed_mask
        observed_pixels = int(np.count_nonzero(observed))
        coverage_fraction = float(observed_pixels) / float(npix)
        mean_hits = float(hit_map[observed].mean()) if observed_pixels > 0 else 0.0
        max_hits = int(hit_map.max())

        # compute residual only on observed pixels
        diff = recon[observed] - ref[observed]
        rms_error = (
            float(math.sqrt(float(np.mean(np.square(diff)))))
            if observed_pixels > 0
            else float("nan")
        )
        bias = float(np.mean(diff)) if observed_pixels > 0 else float("nan")

        results.append(
            {
                "nside": int(nside),
                "npix": int(npix),
                "pixel_scale_deg": float(pixel_scale_deg(nside)),
                "observed_pixels": observed_pixels,
                "coverage_fraction": coverage_fraction,
                "mean_hits_observed": mean_hits,
                "max_hits": max_hits,
                "rms_error_K": rms_error,
                "bias_K": bias,
                "time_median_s": time_median,
                "memory_peak_MB": memory_peak,
            }
        )

    return results


def run_nt_sweep(nt_values: list[int], nside: int, runs_per_setting: int = 5) -> list[dict]:
    adapter = HealpyBinnedMapMakerAdapter()
    results: list[dict] = []

    for nt in nt_values:
        tod, pointing = build_tod_and_pointing(nt)

        # warm-up
        adapter.make_map(tod=tod, pointing_track=pointing, frequency_hz=1.0e9, nside=nside)

        times: list[float] = []
        peaks: list[int | None] = []
        reconstructions: list[np.ndarray] = []

        for _ in range(runs_per_setting):
            monitor = PeakRSSMonitor()
            start = time.perf_counter()
            with monitor:
                result = adapter.make_map(
                    tod=tod, pointing_track=pointing, frequency_hz=1.0e9, nside=nside
                )
            end = time.perf_counter()

            times.append(end - start)
            peaks.append(monitor.peak_mb)
            reconstructions.append(result.skymap.data)

        time_median = float(median(times))
        peak_values = [p for p in peaks if p is not None]
        memory_peak = int(max(peak_values)) if peak_values else None

        recon = reconstructions[-1]
        npix = hp.nside2npix(nside)
        observed = result.observed_mask
        observed_pixels = int(np.count_nonzero(observed))
        coverage_fraction = float(observed_pixels) / float(npix)
        mean_hits = float(result.hit_map[observed].mean()) if observed_pixels > 0 else 0.0
        max_hits = int(result.hit_map.max())

        # reference at same nside
        ref = compute_reference_map(nside, sky_function)
        diff = recon[observed] - ref[observed]
        rms_error = (
            float(math.sqrt(float(np.mean(np.square(diff)))))
            if observed_pixels > 0
            else float("nan")
        )
        bias = float(np.mean(diff)) if observed_pixels > 0 else float("nan")

        results.append(
            {
                "nt": int(nt),
                "nside": int(nside),
                "npix": int(npix),
                "pixel_scale_deg": float(pixel_scale_deg(nside)),
                "observed_pixels": observed_pixels,
                "coverage_fraction": coverage_fraction,
                "mean_hits_observed": mean_hits,
                "max_hits": max_hits,
                "rms_error_K": rms_error,
                "bias_K": bias,
                "time_median_s": time_median,
                "memory_peak_MB": memory_peak,
            }
        )

    return results


def main() -> None:
    nsides = [64, 128, 256, 512, 1024]
    nt_default = 5000
    nt_values = [121, 500, 1000, 5000, 10000]

    print("Running NSIDE sweep (this may take time).")
    nside_results = []
    try:
        nside_results = run_nside_sweep(nsides, nt=nt_default, runs_per_setting=3)
    except MemoryError:
        print("MemoryError during NSIDE sweep; consider reducing max NSIDE.", file=sys.stderr)

    print("Running Nt sweep at nside=512")
    try:
        nt_results = run_nt_sweep(nt_values, nside=512, runs_per_setting=3)
    except MemoryError:
        print("MemoryError during Nt sweep; reduce Nt values.", file=sys.stderr)
        nt_results = []

    output = {
        "metadata": {
            "description": "Binned HEALPix mapmaker scaling experiment",
            "field_function": "sin(dec) + 0.5*cos(2*ra)",
            "frequency_hz": 1.0e9,
            "deterministic": True,
        },
        "nside_sweep": nside_results,
        "nt_sweep": nt_results,
    }

    print(json.dumps(output, indent=2))

    # human-readable table summary (compact)
    print("\nNSIDE sweep summary:")
    for row in nside_results:
        print(
            f"nside={row['nside']:4d} npix={row['npix']:7d} obs={row['observed_pixels']:6d} "
            f"cov={row['coverage_fraction']:.4f} mean_hits={row['mean_hits_observed']:.2f} "
            f"rms={row['rms_error_K']:.6g} time_s={row['time_median_s']:.4f} mem_MB={row['memory_peak_MB']}"
        )

    print("\nNt sweep summary:")
    for row in nt_results:
        print(
            f"nt={row['nt']:6d} nside={row['nside']:4d} obs={row['observed_pixels']:6d} "
            f"cov={row['coverage_fraction']:.4f} mean_hits={row['mean_hits_observed']:.2f} "
            f"rms={row['rms_error_K']:.6g} time_s={row['time_median_s']:.4f} mem_MB={row['memory_peak_MB']}"
        )


if __name__ == "__main__":
    main()
