#!/usr/bin/env python3
"""\
Módulo: notebooks/00_uirapuru_first_run/run_sun_only.py

Descrição:
    Simulação de TOD **só-Sol** do UIRAPURU (calibração solar):

    - janela de **3 h**, passo de **10 s** (configurável em
      ``settings_sun_3h.toml`` → ``[simulations].time_range``);
    - **4096 canais** (995–1245 MHz, LO 1120 MHz);
    - **DUAS polarizações** (H_COPOL/V_COPOL) — vem de
      ``beampattern_horn01_copol.csv`` (o número de pols é definido pelo CSV do
      beam, não pelo TOML);
    - fluxo solar do provider **NoRP/NRO** (XDR) via ``[solar_flux] source = "nro"``;
    - **sem satélites** e sem radiofontes.

Copyright BINGO Collaboration
Last modified: 2026-10-12
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

try:  # credenciais opcionais (SpaceTrack/CIRADA)
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / "credentials.env", override=False)
except Exception:  # pragma: no cover
    pass

from radioskysims_core.logging_config import configure_logging  # noqa: E402
from radioskysims_simulation import SimOrchestrator  # noqa: E402

HERE = PROJECT_ROOT / "notebooks" / "00_uirapuru_first_run"
SETTINGS_FILE = HERE / "settings_sun_3h.toml"
TELESCOPE = "uirapuru_sun"
OUTDIR = HERE / "output"

# Fluxo solar esperado: 1 SFU = 1e4 Jy. Se o sidecar trouxer ~1,5e6 Jy (150 SFU)
# o provider do NRO falhou e caiu no fallback de Sol calmo.
QUIET_SUN_FALLBACK_JY = 150.0 * 1.0e4


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Simulação só-Sol do UIRAPURU")
    ap.add_argument("--out", default=str(OUTDIR / "uirapuru_sun_3h.nc"))
    ap.add_argument(
        "--processor", action="store_true", help="usa o ResourceAwareProcessor"
    )
    ap.add_argument("--batch-output-dir", default=None)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    configure_logging()
    _log("===== UIRAPURU SÓ-SOL (3 h) =====")
    _log(f"settings: {SETTINGS_FILE.name} | telescópio: {TELESCOPE}")

    orch = SimOrchestrator.from_settings(
        telescope=TELESCOPE, settings_file=str(SETTINGS_FILE)
    )
    full = orch.default_time_range()
    grid = full.to_datetime64()
    _log(f"janela: {grid[0]} → {grid[-1]} ({grid.shape[0]} instantes)")

    t0 = time.time()
    result = orch.run(
        time_range=full,
        include_satellites=False,
        include_local_sources=True,
        include_radio_sources=False,
        use_processor=args.processor,
        batch_output_dir=args.batch_output_dir,
    )
    _log(f"run() concluiu em {time.time() - t0:.1f}s")

    ds = result.simulation_result.dataset
    _log(f"dims: {dict(ds.sizes)}")
    _log(f"pols: {list(ds.polarization.values)}")
    _log(f"fontes: {list(ds.source.values)}")

    sidecar = result.save_result(args.out)
    _log(f"dataset: {args.out}")
    _log(f"sidecar: {sidecar}")

    summary = json.loads(Path(sidecar).read_text(encoding="utf-8"))
    sun = (
        summary.get("simulation", {})
        .get("sky", {})
        .get("localsources", {})
        .get("Sun", {})
    )
    _log(f"Sol no sidecar: {json.dumps(sun, default=str)}")
    flux = sun.get("flux_jy")
    value = flux.get("value_jy") if isinstance(flux, dict) else flux
    if value is None:
        _log("AVISO: flux_jy ausente no sidecar.")
    else:
        sfu = float(value) / 1.0e4
        origin = (
            "FALLBACK Sol calmo (150 SFU)"
            if abs(float(value) - QUIET_SUN_FALLBACK_JY) < 1.0e4
            else "dados do provider NoRP/NRO"
        )
        _log(
            f"fluxo no canal central: {float(value):.4g} Jy = {sfu:.2f} SFU → {origin}"
        )
    _log("===== CONCLUÍDO =====")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
