"""Helpers compartilhados do pacote ``analysis``.

Funções pequenas de normalização usadas pelos módulos de carga, análise e
visualização: conversão de coordenadas, extração de DataArray 2D e vetores
temporais em segundos.
"""

from __future__ import annotations

import numpy as np
import xarray as xr


def _freq_to_mhz(obj):
    """Normaliza a coordenada ``frequency`` para MHz se estiver em Hz.

    Detecta Hz pela magnitude dos valores (mediana |f| ≥ 1e6) — um espectro em
    Hz tem valores ~1e9; em MHz, ~1e3. Não usa o espaçamento para não falhar
    com passos pequenos (ex.: 25 kHz).
    """
    f = obj["frequency"].values
    if np.nanmedian(np.abs(f)) >= 1e6:
        return obj.assign_coords(frequency=f / 1e6)
    return obj


def _as_2d(x):
    """Converte entrada para DataArray 2D (time, frequency).

    - Se for Dataset, usa ``T_antenna`` (ou a primeira data_var).
    - Dimensões extras (polarization, source, pointing) são agregadas pela
      média.
    - Frequência é normalizada para MHz e deduplicada (agregando canais
      repetidos pela média).
    - Preserva lazy (dask) quando os dados vierem assim.
    """
    if isinstance(x, xr.Dataset):
        var = "T_antenna" if "T_antenna" in x else list(x.data_vars)[0]
        x = x[var]
    reduce_dims = [d for d in x.dims if d not in ("time", "frequency")]
    if reduce_dims:
        x = x.mean(dim=reduce_dims)
    x = _dedup_frequency(x)
    if x.dims[0] != "time":
        x = x.transpose("time", ...)
    return x


def _dedup_frequency(obj):
    """Remove frequências duplicadas (ex.: FITS Callisto repete o último bin).

    Canais com o mesmo valor de frequência são agregados pela média. Necessário
    para interpolação, que exige índice com valores únicos.
    """
    da = _freq_to_mhz(obj)
    f = np.asarray(da["frequency"].values, dtype=float)
    if len(np.unique(f)) == len(f):
        return da
    return (
        da.assign_coords(_freq=("frequency", f))
        .groupby("_freq")
        .mean()
        .rename({"_freq": "frequency"})
    )


def _time_seconds(da) -> np.ndarray:
    """Converte a coordenada ``time`` para segundos (float) desde o início."""
    t = da["time"].values
    if np.issubdtype(np.asarray(t).dtype, np.datetime64):
        return (t - t[0]).astype("timedelta64[ns]").astype(float) / 1e9
    return np.asarray(t, dtype=float)


def scale_window(window, factor: float = 1.0, unit: str = "min"):
    """Expande/contrai uma janela temporal ``(start, end)`` em torno do centro.

    Mantém o centro da janela fixo e multiplica a meia-duração pelo ``factor``:

    .. math::

        \\text{centro} = \\tfrac{start + end}{2},
        \\qquad
        start' = \\text{centro} - f\\,\\tfrac{end - start}{2},
        \\qquad
        end' = \\text{centro} + f\\,\\tfrac{end - start}{2}

    Útil para **crescer a janela do fit** de calibração (ex.: trânsito do Sol de
    ``sim.events``) quando se quer incluir mais amostras em torno do evento.

    Parameters
    ----------
    window:
        ``(start, end)`` — strings ISO, ``np.datetime64`` ou ``Timestamp``.
    factor:
        Fator de escala (``1.0`` mantém a janela; ``2.0`` dobra a duração).
    unit:
        Unidade do ``factor`` (``"min"`` ou ``"s"``) — usado para converter a
        meia-duração. Padrão ``"min"``.

    Returns
    -------
    tuple[str, str]
        Nova janela ``(start, end)`` em strings ISO (segundos).
    """
    import pandas as pd

    start = pd.Timestamp(window[0])
    end = pd.Timestamp(window[1])
    center = start + (end - start) / 2
    half = (end - start) / 2
    if unit == "s":
        half = pd.Timedelta(seconds=half.total_seconds() * factor)
    else:
        half = pd.Timedelta(minutes=half.total_seconds() / 60 * factor)
    new_start = (center - half).strftime("%Y-%m-%dT%H:%M:%S")
    new_end = (center + half).strftime("%Y-%m-%dT%H:%M:%S")
    return new_start, new_end
