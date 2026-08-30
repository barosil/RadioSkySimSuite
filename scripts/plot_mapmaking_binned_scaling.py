from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

OUTDIR = Path("outputs/mapmaking_scaling/figures")
OUTDIR.mkdir(parents=True, exist_ok=True)

nside = [64, 128, 256, 512, 1024]
rms_nside = [
    0.0006634508158969311,
    0.00028862666973426213,
    0.0002279487230242968,
    0.00013397159035080167,
    0.00017872731683139226,
]
memory_nside = [205, 216, 259, 433, 1041]
time_nside = [
    0.011266927000178839,
    0.011429738000060752,
    0.010868497000046773,
    0.03184308599998076,
    0.5662664270000732,
]

nt = [121, 500, 1000, 5000, 10000]
rms_nt = [
    0.0006362916400075972,
    0.0006288515711584137,
    0.0006276370552794984,
    0.00013397159035080167,
    0.00011030975290975148,
]


def save_plot(x, y, xlabel, ylabel, filename, logx=False, logy=False):
    plt.figure(figsize=(7, 5))
    plt.plot(x, y, marker="o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)

    if logx:
        plt.xscale("log")

    if logy:
        plt.yscale("log")

    plt.tight_layout()
    plt.savefig(OUTDIR / filename, dpi=200)
    plt.close()


save_plot(
    nside,
    rms_nside,
    "NSIDE",
    "Erro RMS [K]",
    "rms_vs_nside.png",
    logx=True,
)

save_plot(
    nside,
    memory_nside,
    "NSIDE",
    "Pico de memória RSS [MB]",
    "memory_vs_nside.png",
    logx=True,
)

save_plot(
    nside,
    time_nside,
    "NSIDE",
    "Tempo mediano [s]",
    "time_vs_nside.png",
    logx=True,
    logy=True,
)

save_plot(
    nt,
    rms_nt,
    "Número de amostras Nt",
    "Erro RMS [K]",
    "rms_vs_nt.png",
    logx=True,
)

print(f"Figuras salvas em: {OUTDIR.resolve()}")
