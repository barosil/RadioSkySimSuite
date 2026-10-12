#!/usr/bin/env python3
"""\
Módulo: notebooks/00_uirapuru_first_run/run_first_run.py

Descrição:
    Execução "primeira luz" do UIRAPURU — simulação de TOD instrumentada com
    os parâmetros do experimento:

    - LO do DDC em 1120 MHz (notch DC esperado), 4096 canais, integração 30 s;
    - constelações GPS/GALILEO/GLONASS/BEIDOU (satélites) + fontes locais (Sol);
    - padrão de feixe ``beampattern_horn01.csv``;
    - apontamento FIXO alt=80°, az=9°;
    - EIRP dos satélites recalculado em ``signals.json`` (deste diretório);
    - fluxo solar do novo provider NoRP/NRO (XDR).

    Janela: **24 h** (passo de 120 s → 721 instantes), configurável em
    ``[simulations].time_range`` do ``settings_first_run.toml``.

    Executa em duas fases: (1) **estimativa** do tempo por extrapolação linear
    de execuções curtas; (2) **run** completa (com ``use_processor=True``,
    streaming a disco automático quando a saída excede a memória).

Copyright BINGO Collaboration
Last modified: 2026-10-12
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# ── Âncora de diretório: raiz do projeto (CWD-independente) ──────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

try:  # credenciais (SpaceTrack/CIRADA) — opcional
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / "credentials.env", override=False)
except Exception:  # pragma: no cover
    pass

import numpy as np  # noqa: E402
from radioskysims_core.domain.common import TimeRange  # noqa: E402
from radioskysims_simulation import SimOrchestrator  # noqa: E402

from radioskysims import create_radiotelescope  # noqa: E402

# ═══════════════════════════════════════════════════════════════════════
# Parâmetros do experimento (explícitos, espelhando a instrumentação)
# ═══════════════════════════════════════════════════════════════════════
HERE = PROJECT_ROOT / "notebooks" / "00_uirapuru_first_run"
SETTINGS_FILE = HERE / "settings_first_run.toml"
TELESCOPE = "uirapuru_first_run"
OUTDIR = HERE / "output"

CENTRE_FREQUENCY_MHZ = 1120.0  # LO do DDC; notch esperado
NUMBER_OF_CHANNELS = 4096
REQUESTED_INTEGRATION_TIME_S = 30.0
CONSTELLATIONS = ["GPS", "GALILEO", "GLONASS", "BEIDOU"]
INCLUDE_SATELLITES = True
INCLUDE_LOCAL_SOURCES = True
BEAM_PATTERN_PATH = Path("src/radioskysims/resources/beams/beampattern_horn01.csv")
POINTING_ALT_DEG = 80.0
POINTING_AZ_DEG = 9.0

ESTIMATE_SAMPLES = (3, 6)  # pontos da extrapolação linear


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def build_orchestrator() -> SimOrchestrator:
    _log(f"Compondo orquestrador (settings={SETTINGS_FILE.name}, telescope={TELESCOPE})")
    return SimOrchestrator.from_settings(telescope=TELESCOPE, settings_file=str(SETTINGS_FILE))


def _slice(tr: TimeRange, n: int) -> TimeRange:
    """Recorta os primeiros ``n`` instantes do TimeRange."""
    dt = tr.to_datetime64()[:n]
    start = dt[0].astype("datetime64[us]").tolist()
    end = dt[-1].astype("datetime64[us]").tolist()
    step = float((dt[1] - dt[0]) / np.timedelta64(1, "s")) if len(dt) > 1 else 30.0
    return TimeRange.from_iso(start.isoformat(), end.isoformat(), step)


def _run_once(orch: SimOrchestrator, tr: TimeRange, *, use_processor: bool):
    t0 = time.monotonic()
    result = orch.run(
        constellations=CONSTELLATIONS,
        time_range=tr,
        include_satellites=INCLUDE_SATELLITES,
        include_local_sources=INCLUDE_LOCAL_SOURCES,
        include_radio_sources=False,
        use_processor=use_processor,
    )
    return result, time.monotonic() - t0


def estimate_runtime(orch: SimOrchestrator, full: TimeRange) -> dict:
    """Estima o tempo total e o tamanho de saída (2 execuções curtas)."""
    n_total = full.to_datetime64().shape[0]
    _log(f"Estimativa: {n_total} instantes; benchmark com {ESTIMATE_SAMPLES} amostras")

    samples, timings, sizes = [], [], {}
    for n in ESTIMATE_SAMPLES:
        tr_n = _slice(full, n)
        result, dt = _run_once(orch, tr_n, use_processor=False)
        sizes = dict(result.simulation_result.dataset.sizes)
        samples.append(n)
        timings.append(dt)
        _log(f"  benchmark n={n}: {dt:.1f}s | dims {sizes}")

    # Ajuste linear t(n) = a*n + b (b ≈ overhead fixo de montagem)
    a, b = np.polyfit(samples, timings, 1)
    est = a * n_total + b

    # Tamanho projetado da saída: n_time × n_freq × n_pol × n_src × 8 bytes × 2 vars
    n_freq = int(sizes.get("frequency", 0))
    n_pol = int(sizes.get("polarization", 1))
    n_src = int(sizes.get("source", 1))
    projected_gb = (n_total * n_freq * n_pol * n_src * 8 * 2) / 1e9

    info = {
        "n_total_samples": int(n_total),
        "bench_samples": samples,
        "bench_seconds": [round(t, 2) for t in timings],
        "per_sample_s": round(float(a), 4),
        "fixed_overhead_s": round(float(b), 2),
        "estimated_total_s": round(float(est), 1),
        "estimated_total_min": round(float(est) / 60.0, 2),
        "dataset_dims": sizes,
        "projected_output_gb": round(float(projected_gb), 1),
    }
    _log(
        f"Estimativa: ~{info['estimated_total_min']} min "
        f"({info['per_sample_s']}s/amostra, overhead ~{info['fixed_overhead_s']}s)"
    )
    _log(
        f"Saída projetada: ~{info['projected_output_gb']} GB "
        f"({n_total}×{n_freq}×{n_pol}×{n_src} × 2 vars)"
    )
    return info


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Primeira execução do UIRAPURU")
    ap.add_argument("--skip-estimate", action="store_true", help="pula a fase de estimativa")
    ap.add_argument("--no-processor", action="store_true", help="roda sem ResourceAwareProcessor")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    _log("===== UIRAPURU first run =====")
    _log(
        f"LO={CENTRE_FREQUENCY_MHZ} MHz | {NUMBER_OF_CHANNELS} canais | "
        f"int={REQUESTED_INTEGRATION_TIME_S}s | const={CONSTELLATIONS}"
    )

    # Sanidade: arquivo de beam e telescópio acessíveis
    if not (PROJECT_ROOT / BEAM_PATTERN_PATH).exists():
        _log(f"ERRO: beam não encontrado: {BEAM_PATTERN_PATH}")
        return 2

    rt = create_radiotelescope(TELESCOPE, settings_file=str(SETTINGS_FILE))
    _log(f"Telescópio: {rt.name} | observer lat={rt.observer.lat}, lon={rt.observer.lon}")

    orch = build_orchestrator()
    full = orch.default_time_range()
    _log(
        f"Janela: {full.to_datetime64()[0]} → {full.to_datetime64()[-1]} "
        f"({full.to_datetime64().shape[0]} instantes)"
    )

    estimate = None
    if not args.skip_estimate:
        estimate = estimate_runtime(orch, full)
        import shutil

        free_gb = shutil.disk_usage(str(PROJECT_ROOT)).free / 1e9
        need_gb = float(estimate["projected_output_gb"])
        _log(f"Disco livre: {free_gb:.1f} GB | saída projetada ~{need_gb:.1f} GB")
        if need_gb > 0.6 * free_gb:
            _log(
                f"ABORTADO: saída projetada ({need_gb:.1f} GB) excede 60% do disco "
                f"livre ({free_gb:.1f} GB). Aumente o passo em [simulations].time_range."
            )
            return 3

    _log("===== RUN (completa) =====")
    result, dt = _run_once(orch, full, use_processor=not args.no_processor)
    _log(f"⏱ run() completou em {dt:.1f}s")

    ds = result.simulation_result.dataset
    _log(f"dims: {dict(ds.sizes)}")
    _log(f"variáveis: {list(ds.data_vars)}")

    outfile = OUTDIR / "uirapuru_first_run.nc"
    sidecar = result.save_result(str(outfile))
    _log(f"dataset salvo em {outfile}")
    _log(f"resumo (sidecar) em {sidecar}")

    if estimate is not None:
        import json

        (OUTDIR / "estimate.json").write_text(json.dumps(estimate, indent=2), encoding="utf-8")

    _log("===== CONCLUÍDO =====")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
