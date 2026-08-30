"""Exemplo completo do pipeline GNSStools4Astro (download → tracks → sinal).

Uso:
    .venv/bin/python src/GNSStools4Astro/examples/run_pipeline.py \\
        --station braz --start 2024-06-10T00:00 --end 2024-06-10T12:00 \\
        --lat -7.5 --lon -35.0 --height 10 --outdir /tmp/gnss_demo

O passo de estimativa de sinal usa as amostras C/N0 do arquivo de
observação; se o arquivo não contiver SNR (RINEX 2.11 da RBMC), usa
amostras sintéticas de demonstração.
"""

# ruff: noqa: T201

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from gnsstools4astro.bootstrap.composition import (
    build_download_use_case,
    build_signal_use_case,
    build_tracks_use_case,
)
from gnsstools4astro.domain.rinex import RinexFileType, RinexRequest, RinexSource
from gnsstools4astro.domain.station import (
    DEFAULT_STATION,
    DEFAULT_STATION_POSITION,
    GNSSStation,
)
from gnsstools4astro.infrastructure.logging_config import configure_logging
from gnsstools4astro.infrastructure.rinex.reader import RinexReader


def _parse_dt(value: str) -> datetime:
    """Interpreta datas ``naive`` como UTC (sem deslocamento de fuso local)."""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline GNSStools4Astro")
    parser.add_argument("--station", default=DEFAULT_STATION)
    parser.add_argument("--start", default="2024-06-10T00:00")
    parser.add_argument("--end", default="2024-06-10T12:00")
    parser.add_argument("--lat", type=float, default=DEFAULT_STATION_POSITION.lat_deg)
    parser.add_argument("--lon", type=float, default=DEFAULT_STATION_POSITION.lon_deg)
    parser.add_argument("--height", type=float, default=DEFAULT_STATION_POSITION.height_m)
    parser.add_argument("--outdir", default="/tmp/gnss_demo")
    args = parser.parse_args()

    configure_logging("INFO")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    request = RinexRequest(
        station=args.station,
        start=_parse_dt(args.start),
        end=_parse_dt(args.end),
        source=RinexSource.RBMC,
    )
    station = GNSSStation(
        name=args.station,
        lat_deg=args.lat,
        lon_deg=args.lon,
        height_m=args.height,
    )

    # 1) Download
    print("\n=== 1. Download RINEX (RBMC) ===")
    downloaded = build_download_use_case(outdir).run(request, outdir)
    for path in downloaded.all_files():
        print("  -", path.name)

    # 2) Tracks
    print("\n=== 2. Tracks de satélites ===")
    nav_files = downloaded.files.get(RinexFileType.NAV, [])
    if not nav_files:
        print("  Sem arquivos NAV; pulando tracks.")
    else:
        tracks = build_tracks_use_case().run(
            nav_files,
            station,
            start=request.start,
            end=request.end,
            step_s=3600,
            min_alt_deg=5,
        )
        tracks_out = outdir / "tracks.nc"
        tracks.to_netcdf(tracks_out)
        print(f"  {len(tracks.satellites)} satélites salvos em {tracks_out}")

    # 3) Sinal (PSD/EIRP)
    print("\n=== 3. Estimativa de sinal (PSD/EIRP) ===")
    obs_files = downloaded.files.get(RinexFileType.OBS, [])
    reader = RinexReader()
    sv_means: list[tuple[str, float]] = []
    for obs_path in obs_files:
        sv_means.extend(reader.mean_cn0_per_sv(reader.load_obs(obs_path), signal="S1C"))

    if not sv_means:
        print("  Observação sem C/N0 — usando amostras sintéticas.")
        sv_means = [
            ("G01", 45.0),
            ("E11", 42.0),
            ("R05", 39.0),
            ("C19", 41.0),
        ]

    use_case = build_signal_use_case()
    summaries = use_case.summarize_cn0(sv_means)

    print(f"{'sv':<5} {'const':<9} {'C/N0':>7} {'P_rec(W)':>12} {'PSD(W/Hz)':>14} {'EIRP(dBW)':>10}")
    for s in summaries:
        print(
            f"{s.sv:<5} {s.constellation.value:<9} {s.cn0_mean_dbhz:>7.1f} "
            f"{s.received_power_mean_w:>12.2e} {s.psd_mean_w_hz:>14.2e} "
            f"{s.eirp_dbw if s.eirp_dbw is not None else '-':>10}"
        )

    print("\nPipeline concluído.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
