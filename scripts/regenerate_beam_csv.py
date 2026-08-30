"""
Módulo: scripts/regenerate_beam_csv.py

Descrição:
    Regenera o CSV de padrão de feixe (beampattern_horn01.csv) a partir do
    arquivo base LIT (beampattern_horn01.xlsx).

    Procedimento:
      1. Lê o xlsx via LITBeamLoader — amplitude em dB (formato pt-br nas
         frequências), ângulos em graus.
      2. Normalização: desloca o pico de cada banda (frequência) para 0 dB,
         agrupando todas as polarizações — preserva a relação cross/co-polar.
      3. As folhas Cruzada têm grade de frequência menor (7 vs 17 bandas);
         interpola linearmente (em dB) as frequências ausentes.
      4. Converte amplitude de dB para potência linear: A = 10^(dB/10).
      5. Grava CSV com colunas: polarization, frequency (MHz), angle (°),
         amplitude (linear), phase (°).

    Saída: src/radioskysims/resources/beams/beampattern_horn01.csv

Copyright BINGO Collaboration
Last modified: 2026-08-14
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from radioskysims_beam.infrastructure.beams.loaders.lit import LITBeamLoader

XLSX_PATH = (
    Path(__file__).resolve().parent.parent
    / "src/radioskysims/resources/beams/beampattern_horn01.xlsx"
)
CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "src/radioskysims/resources/beams/beampattern_horn01.csv"
)


def main() -> None:
    if not XLSX_PATH.exists():
        raise FileNotFoundError(XLSX_PATH)

    beam = LITBeamLoader(XLSX_PATH).load()
    ds = beam.dataset

    print("Dataset LIT (dB, normalizado pico→0 dB):")
    print(f"  dims: {dict(ds.sizes)}")
    print(f"  polarizações: {list(ds.polarization.values)}")

    freqs_full = ds["frequency"].values
    nan_before = int(np.isnan(ds["amplitude"].values).sum())
    print(f"  NaN em amplitude antes da interpolação: {nan_before}")

    # Interpola (linearmente, em dB) as frequências ausentes — principalmente
    # as folhas Cruzada, que têm grade menor que as Copolar. Usa pandas
    # (pivot + interpolate) porque xr.interp propaga NaN quando há lacunas.
    df = ds.to_dataframe().reset_index()
    parts: list[pd.DataFrame] = []
    for pol in df["polarization"].unique():
        sub = df[df["polarization"] == pol]
        for var in ("amplitude", "phase"):
            piv = sub.pivot(index="frequency", columns="angle", values=var)
            piv = piv.reindex(freqs_full)
            piv = piv.interpolate(method="linear", axis=0, limit_direction="both")
            piv = piv.reset_index().melt(id_vars="frequency", var_name="angle", value_name=var)
            if var == "amplitude":
                acc = piv.copy()
                acc["polarization"] = pol
            else:
                acc = acc.merge(piv, on=["frequency", "angle"])
        parts.append(acc)

    df = pd.concat(parts, ignore_index=True)
    df["polarization"] = df["polarization"].astype(str)

    nan_after = int(df["amplitude"].isna().sum())
    print(f"  NaN em amplitude após interpolação: {nan_after}")
    if nan_after:
        msg = f"Há {nan_after} NaN residuais após interpolação."
        raise ValueError(msg)

    # dB (pico 0) -> potência linear
    df["amplitude"] = 10.0 ** (df["amplitude"] / 10.0)
    df = df.sort_values(["polarization", "frequency", "angle"]).reset_index(drop=True)
    df = df[["polarization", "frequency", "angle", "amplitude", "phase"]]

    # Validações
    peak = df.groupby(["polarization", "frequency"])["amplitude"].max()
    print("\nPico (linear) por banda (máx. deve ser 1.0 na pol. dominante):")
    print(peak.unstack().round(4).to_string())
    assert np.isclose(df["amplitude"].max(), 1.0), "Pico global deve ser 1.0"
    assert np.all(df["amplitude"] <= 1.0 + 1e-9), "Amplitude não pode exceder 1.0"
    assert df["amplitude"].notna().all() and df["phase"].notna().all()

    df.to_csv(CSV_PATH, index=False)
    print(f"\nCSV gerado: {CSV_PATH} ({len(df)} linhas)")


if __name__ == "__main__":
    main()
