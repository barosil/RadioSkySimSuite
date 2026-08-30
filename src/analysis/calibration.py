"""Calibração por canal de frequência: ``D = a + g·T_sim``.

Modelo físico (ver roteiro do notebook ``02_BINGO_ANALYSIS.ipynb``):

.. math::

    D(t,\\nu) = a(\\nu) + g(\\nu)\\, T_{A,\\odot}^{\\rm sim}(t,\\nu) + n(t,\\nu)

- :math:`a(\\nu)` — baseline instrumental (counts; inclui ``G·T_sys + D_0``);
- :math:`g(\\nu)` — ganho em counts/K;
- :math:`T_{A,\\odot}^{\\rm sim}` — temperatura de antena da simulação (K).

O ajuste é OLS por canal (fórmula fechada, vetorizada sobre a frequência):

.. math::

    g = \\frac{n\\,S_{xy} - S_x S_y}{n\\,S_{xx} - S_x^2}, \\qquad
    a = \\frac{S_y - g\\,S_x}{n}, \\qquad
    T_{\\rm sys} = \\frac{a}{g}

Aplicação da calibração:

.. math::

    T_A^{\\rm cal}(t,\\nu) = \\frac{D(t,\\nu) - \\hat a(\\nu)}{\\hat g(\\nu)}
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from ._utils import _as_2d
from .observation import ObservationData

__all__ = [
    "apply_calibration",
    "dt_to_dtheta",
    "fit_calibration",
    "fit_calibration_dt",
]


def _to_2d(obj) -> xr.DataArray:
    """Normaliza a entrada (ObservationData ou xarray) para DataArray 2D."""
    if isinstance(obj, ObservationData):
        obj = obj._target()
    return _as_2d(obj)


def fit_calibration(obs, sim, *, fit_frequency=None, fit_window=None) -> xr.Dataset:
    """Ajusta ``D = a + g·T_sim`` por canal de frequência (OLS).

    Usa a fórmula fechada da regressão linear simples, vetorizada sobre a
    dimensão de frequência — rápida mesmo com ~10³ canais. Ajusta **apenas o
    intervalo temporal comum** (interseção das coordenadas ``time``; se os
    grids forem ligeiramente diferentes, alinhe antes com
    ``ObservationData.align_time`` + ``.sel``/``.interp``).

    Parameters
    ----------
    obs:
        Observação em counts (ADU) — ``ObservationData`` ou xarray
        ``(time, frequency)``.
    sim:
        Simulação em temperatura de brilho (K) — ``ObservationData`` ou xarray
        ``(time, frequency)``.
    fit_frequency:
        Opcional. Se dado (array), interpola ``obs`` e ``sim`` para esse grid
        antes do ajuste (ex.: grid comum de calibração). Se ``None``, exige que
        os grids de frequência coincidam.
    fit_window:
        Opcional, ``(start, end)`` — restringe o ajuste a uma janela temporal
        (ex.: a janela do transito do Sol, onde o sinal correlacionado é
        relativamente maior frente a RFI/deriva de baseline). Recomendado para
        dados com muita RFI, em que o ajuste global fica dominado por ruído.

    Returns
    -------
    xr.Dataset
        Coordenada ``frequency`` e variáveis:
        ``a`` (baseline, counts), ``g`` (ganho, counts/K), ``T_sys`` (K),
        ``r2`` (coef. de determinação), ``n`` (pontos válidos por canal).
    """
    D = _to_2d(obs)
    T = _to_2d(sim)

    if fit_frequency is not None:
        ffit = np.asarray(fit_frequency, dtype=float)
        D = D.interp(frequency=ffit)
        T = T.interp(frequency=ffit)
    elif D.sizes["frequency"] != T.sizes["frequency"]:
        msg = (
            "obs e sim têm grids de frequência diferentes "
            f"({D.sizes['frequency']} vs {T.sizes['frequency']}). "
            "Passe fit_frequency (grid comum) ou rebina antes."
        )
        raise ValueError(msg)

    # ── interseção temporal (por rótulo) ──
    t_common = np.intersect1d(D["time"].values, T["time"].values)
    if t_common.size < 3:
        msg = (
            "obs e sim não compartilham o grid temporal — alinhe antes "
            "(ObservationData.align_time) e interpole para um grid comum."
        )
        raise ValueError(msg)
    D = D.sel(time=t_common)
    T = T.sel(time=t_common)
    if fit_window is not None:
        start, end = fit_window
        D = D.sel(time=slice(start, end))
        T = T.sel(time=slice(start, end))
        if D.sizes["time"] < 3:
            msg = "fit_window resultou em poucos pontos temporais."
            raise ValueError(msg)

    d = np.asarray(D.values, dtype=float)
    t = np.asarray(T.values, dtype=float)
    n_f = d.shape[1]

    # máscara de pontos válidos (NaN fora)
    valid = np.isfinite(d) & np.isfinite(t)
    n = valid.sum(axis=0).astype(float)
    d = np.where(valid, d, 0.0)
    t = np.where(valid, t, 0.0)

    Sx = t.sum(axis=0)
    Sy = d.sum(axis=0)
    Sxx = (t * t).sum(axis=0)
    Sxy = (t * d).sum(axis=0)

    denom = n * Sxx - Sx * Sx
    g = np.full(n_f, np.nan)
    a = np.full(n_f, np.nan)
    ok = (denom != 0) & (n > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(ok, (n * Sxy - Sx * Sy) / np.where(ok, denom, 1), np.nan)
        a = np.where(ok, (Sy - g * Sx) / np.where(ok, n, 1), np.nan)

    # ── R² por canal ──
    yhat = a[None, :] + g[None, :] * t
    ss_res = np.where(valid, (d - yhat) ** 2, 0.0).sum(axis=0)
    ss_tot = np.where(valid, (d - d.mean(axis=0)) ** 2, 0.0).sum(axis=0)
    r2 = np.where(ss_tot > 0, 1.0 - ss_res / np.where(ss_tot > 0, ss_tot, 1), np.nan)

    with np.errstate(divide="ignore", invalid="ignore"):
        t_sys = a / g

    coords = {"frequency": D["frequency"].values}
    cal = xr.Dataset(
        {
            "a": (("frequency",), a),
            "g": (("frequency",), g),
            "T_sys": (("frequency",), t_sys),
            "r2": (("frequency",), r2),
            "n": (("frequency",), n),
        },
        coords=coords,
    )
    for v, units in (("a", "counts"), ("g", "counts/K"), ("T_sys", "K")):
        cal[v].attrs["units"] = units
    cal.attrs["model"] = "D = a + g * T_sim  (OLS por canal)"
    return cal


def apply_calibration(obs, cal) -> xr.DataArray:
    """Aplica a calibração: ``T_A^cal = (D − a) / g``.

    Parameters
    ----------
    obs:
        Observação em counts (ADU) — ``ObservationData`` ou xarray.
    cal:
        Resultado de ``fit_calibration`` (Dataset com ``a`` e ``g``).

    Returns
    -------
    xr.DataArray
        Temperatura de brilho calibrada ``(time, frequency)`` em K.
    """
    D = _to_2d(obs)
    a = (
        cal["a"]
        .interp(frequency=D["frequency"].values)
        .assign_coords(frequency=D["frequency"].values)
    )
    g = (
        cal["g"]
        .interp(frequency=D["frequency"].values)
        .assign_coords(frequency=D["frequency"].values)
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (D - a) / g
    out = out.rename("T_antenna_cal")
    out.attrs["units"] = "K"
    out.attrs["calibration"] = "linear (a, g) por canal"
    return out


# ──────────────────────────────────────────────────────────────────
# Método 2 (item 6 do roteiro): calibração com três parâmetros
# a(ν), g(ν) e δt — ver roteiro do notebook 02_BINGO_ANALYSIS
# ──────────────────────────────────────────────────────────────────
# Taxa aparente do Sol no céu (rotação da Terra): 360°/24 h = 15°/h
# = 0.25°/min = 0.0041667°/s. Usada na conversão δt → δθ (apontamento).
SOLAR_RATE_DEG_PER_S = 15.0 / 3600.0


def dt_to_dtheta(dt_s: float) -> float:
    """Converte um atraso temporal ``δt`` (s) em deslocamento de apontamento
    ``δθ`` (graus), usando a taxa aparente do Sol no céu (~15°/h).

    O roteiro associa o ``δt`` da calibração local a um erro de apontamento
    ``δθ``: se o Sol está ``δt`` adiantado/atrasado no modelo, isso equivale a
    um desvio angular de ``δθ = δt · (15/3600)`` graus.
    """
    return float(dt_s) * SOLAR_RATE_DEG_PER_S


def _ols_by_channel(d: np.ndarray, t: np.ndarray) -> tuple[np.ndarray, ...]:
    """OLS por canal (vetorizado sobre a frequência) — retorna (a, g, r2, n).

    ``d`` e ``t`` são arrays ``(time, frequency)`` já alinhados e com o mesmo
    grid temporal. Pontos não finitos são mascarados por canal.
    """
    d = np.asarray(d, dtype=float)
    t = np.asarray(t, dtype=float)
    valid = np.isfinite(d) & np.isfinite(t)
    n = valid.sum(axis=0).astype(float)
    d = np.where(valid, d, 0.0)
    t = np.where(valid, t, 0.0)

    Sx = t.sum(axis=0)
    Sy = d.sum(axis=0)
    Sxx = (t * t).sum(axis=0)
    Sxy = (t * d).sum(axis=0)

    denom = n * Sxx - Sx * Sx
    ok = (denom != 0) & (n > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(ok, (n * Sxy - Sx * Sy) / np.where(ok, denom, 1), np.nan)
        a = np.where(ok, (Sy - g * Sx) / np.where(ok, n, 1), np.nan)

    yhat = a[None, :] + g[None, :] * t
    ss_res = np.where(valid, (d - yhat) ** 2, 0.0).sum(axis=0)
    ss_tot = np.where(valid, (d - d.mean(axis=0)) ** 2, 0.0).sum(axis=0)
    r2 = np.where(ss_tot > 0, 1.0 - ss_res / np.where(ss_tot > 0, ss_tot, 1), np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        t_sys = a / g
    return a, g, t_sys, r2, n, ss_res


def fit_calibration_dt(
    obs,
    sim,
    *,
    fit_window=None,
    dt_range_s=(-1800, 1800),
    dt_step_s: float = 30.0,
    dt_refine: bool = True,
    refine_iters: int = 3,
    return_profile: bool = True,
    dt_fixed: float | None = None,
):
    """Calibração local com três parâmetros: ``a(ν)``, ``g(ν)`` e ``δt``.

    Item 6 do roteiro (Método 2): além da baseline e do ganho por canal, o
    ajuste incorpora um **atraso temporal global** ``δt`` (associado a um erro
    de apontamento ``δθ`` — o Sol se move ~0.25°/min no céu):

    .. math::

        D(t,\\nu) = a(\\nu) + g(\\nu)\\, T_{\\rm sim}(t - \\delta t, \\nu) + n

    O ``δt`` é estimado por **varredura em um grid temporal**: para cada
    candidato, a simulação é deslocada no tempo (interpolação no grid comum) e
    o OLS por canal ``(a, g)`` é refeito; o ``δt`` vencedor é o que minimiza a
    soma dos quadrados dos resíduos sobre todos os canais. Um refinamento
    parabólico (opcional) interpola o mínimo entre os pontos do grid.

    Parameters
    ----------
    obs:
        Observação em counts (ADU) — ``ObservationData`` ou xarray
        ``(time, frequency)``. Deve compartilhar o grid temporal com ``sim``
        (alinhe antes com ``ObservationData.align_time`` + ``.interp``).
    sim:
        Simulação em temperatura (K) — mesmo grid de tempo e de frequência
        de ``obs`` (use ``rebin_frequency``/``fit_frequency`` para alinhar).
    fit_window:
        Opcional, ``(start, end)`` — janela temporal do ajuste (recomendado:
        a janela do trânsito do Sol, onde o sinal correlacionado domina).
    dt_range_s:
        Intervalo de busca do ``δt`` em segundos ``(min, max)``.
    dt_step_s:
        Passo do grid de busca (s). Ex.: 30 s com obs binada a 120 s.
    dt_refine:
        Se ``True`` (padrão), refina o ``δt`` com interpolação parabólica.
    refine_iters:
        Nº de iterações do refinamento.
    return_profile:
        Se ``True`` (padrão), inclui o perfil ``(δt, SSE)`` no resultado.
    dt_fixed:
        Opcional. Se fornecido (ex.: ``0.0``), **força** o ``δt`` (sem varredura)
        e ajusta apenas ``a(ν)`` e ``g(ν)`` na janela — útil quando o ``δt``
        não é identificável (sinal fraco) e se quer a calibração com o
        desalinhamento já conhecido/assumido. Nesse caso ``at_boundary=False``
        e o perfil ``ss`` fica vazio (``[nan]``).

    Returns
    -------
    tuple[xr.Dataset, float, dict]
        ``(cal, dt_best_s, res)`` onde:
        - ``cal`` — Dataset idêntico ao de ``fit_calibration`` (a, g, T_sys,
          r2, n) avaliado no ``δt`` ótimo;
        - ``dt_best_s`` — atraso temporal ótimo (s); ``δt > 0`` ⇒ a simulação
          está atrasada em relação à observação (obs lidera por ``δt``);
        - ``res`` — dict com ``dt_grid_s``, ``ss`` (perfil de SSE vs δt),
          ``dt_best_s``, ``dtheta_deg`` (δt convertido em apontamento) e
          ``r2_best`` (R² por canal no δt ótimo).
    """
    D = _to_2d(obs)
    T = _to_2d(sim)
    if D.sizes["frequency"] != T.sizes["frequency"]:
        msg = (
            "obs e sim têm grids de frequência diferentes — rebina antes "
            "(ObservationData.rebin_frequency) ou use fit_frequency."
        )
        raise ValueError(msg)

    # ── interseção temporal (por rótulo) + janela de ajuste ──
    t_common = np.intersect1d(D["time"].values, T["time"].values)
    if t_common.size < 3:
        msg = (
            "obs e sim não compartilham o grid temporal — alinhe antes e "
            "interpole para um grid comum (ex.: obs_on_sim do passo 9)."
        )
        raise ValueError(msg)
    D = D.sel(time=t_common)
    T = T.sel(time=t_common)
    if fit_window is not None:
        start, end = fit_window
        D = D.sel(time=slice(start, end))
        T = T.sel(time=slice(start, end))
        if D.sizes["time"] < 3:
            msg = "fit_window resultou em poucos pontos temporais."
            raise ValueError(msg)

    # normaliza o grid temporal para ns (o interp do xarray falha se a coord
    # for datetime64[s] e o shift produzir datetime64[ns])
    t_ns = np.asarray(T["time"].values, dtype="datetime64[ns]")
    D = D.assign_coords(time=np.asarray(D["time"].values, dtype="datetime64[ns]"))
    T = T.assign_coords(time=t_ns)
    t_grid = t_ns
    d_arr = np.asarray(D.values, dtype=float)
    t_arr = np.asarray(T.values, dtype=float)

    def _shifted(dt_s: float) -> np.ndarray:
        """T_sim avaliado em (t − δt): desloca a simulação no tempo."""
        if abs(dt_s) < 1e-9:
            return t_arr
        shift = np.timedelta64(int(round(dt_s * 1e9)), "ns")
        t_sh = T.interp(time=t_grid - shift)
        return np.asarray(t_sh.values, dtype=float)

    # ── determinação de δt: forçado (dt_fixed) ou varredura ──
    if dt_fixed is not None:
        # δt forçado (ex.: 0) — sem varredura; apenas OLS com a(ν), g(ν)
        dt_best = float(dt_fixed)
        at_boundary = False
        dt_grid = np.array([dt_best], dtype=float)
        ss = np.array([np.nan], dtype=float)
        n_valid = np.array([np.nan], dtype=float)
    else:
        # varredura de δt
        dt_grid = np.arange(dt_range_s[0], dt_range_s[1] + dt_step_s / 2.0, dt_step_s, dtype=float)
        ss = np.full(dt_grid.size, np.inf)
        n_valid = np.full(dt_grid.size, np.nan)
        for i, dt in enumerate(dt_grid):
            t_sh = _shifted(dt)
            *_, n_, ss_res = _ols_by_channel(d_arr, t_sh)
            nv = float(np.nansum(n_))
            n_valid[i] = nv
            # SSE MÉDIA por ponto válido: deslocamentos grandes empurram a
            # simulação para fora do domínio temporal (interp → NaN); pontos
            # inválidos não devem contar como resíduo zero (isso favorecia os
            # extremos do grid).
            ss[i] = float(np.nansum(ss_res) / nv) if nv > 0 else np.inf

        best_idx = int(np.nanargmin(ss))
        dt_best = float(dt_grid[best_idx])
        at_boundary = bool(best_idx == 0 or best_idx == dt_grid.size - 1)

        # ── refinamento parabólico do mínimo ──
        if dt_refine and 0 < best_idx < dt_grid.size - 1:
            dt_best = _refine_parabola(dt_grid, ss, best_idx, refine_iters)
            at_boundary = False

    # ── re-ajuste final no δt escolhido ──
    t_sh_best = _shifted(dt_best)
    a, g, t_sys, r2, n, ss_res = _ols_by_channel(d_arr, t_sh_best)

    coords = {"frequency": D["frequency"].values}
    cal = xr.Dataset(
        {
            "a": (("frequency",), a),
            "g": (("frequency",), g),
            "T_sys": (("frequency",), t_sys),
            "r2": (("frequency",), r2),
            "n": (("frequency",), n),
        },
        coords=coords,
    )
    for v, units in (("a", "counts"), ("g", "counts/K"), ("T_sys", "K")):
        cal[v].attrs["units"] = units
    cal.attrs["model"] = "D = a + g * T_sim(t - dt)  (OLS por canal + scan de dt)"

    res = {
        "dt_grid_s": dt_grid,
        "ss": ss,
        "n_valid": n_valid,
        "dt_best_s": dt_best,
        "dtheta_deg": dt_to_dtheta(dt_best),
        "r2_best": r2,
        "at_boundary": at_boundary,
    }
    if not return_profile:
        res.pop("dt_grid_s", None)
        res.pop("ss", None)
        res.pop("n_valid", None)
    return cal, dt_best, res


def _refine_parabola(dt_grid: np.ndarray, ss: np.ndarray, i: int, iters: int) -> float:
    """Refina o mínimo de ``ss`` perto do índice ``i`` por vértice de parábola.

    Usa os três pontos vizinhos do mínimo do grid. As coordenadas são
    **centradas** no ponto central antes de interpolar o vértice — a fórmula
    clássica é numericamente instável quando ``δt`` é da ordem de centenas de
    segundos e o espalhamento do grid é pequeno (cancelação de termos ~x²).
    Para um grid uniforme de passo ``h``, o vértice é:

    .. math::

        u^* = \\frac{h\\,(y_0 - y_2)}{2\\,(y_0 - 2y_1 + y_2)},
        \\qquad \\delta t_{\\rm best} = x_1 + u^*

    ``iters`` é mantido por compatibilidade (a interpolação parabólica já
    fornece o mínimo em uma passada; iterações adicionais re-avaliam o perfil
    por interpolação linear ao redor do vértice).
    """
    x0, x1, x2 = dt_grid[i - 1], dt_grid[i], dt_grid[i + 1]
    y0, y1, y2 = ss[i - 1], ss[i], ss[i + 1]

    h = (x2 - x0) / 2.0  # passo do grid (uniforme)
    denom = y0 - 2.0 * y1 + y2
    if abs(denom) < 1e-15 or not np.isfinite(denom):
        return float(x1)

    u_star = h * (y0 - y2) / (2.0 * denom)
    x_best = float(x1 + u_star)
    x_best = min(max(x_best, x0), x2)

    # passadas extras: re-amostra o perfil (interp linear) em torno do vértice
    step = h
    for _ in range(int(iters)):
        step = step * 0.5
        xa, xb = x_best - step, x_best + step
        ya = float(np.interp(xa, dt_grid, ss))
        yb = float(np.interp(xb, dt_grid, ss))
        yc = float(np.interp(x_best, dt_grid, ss))
        dd = ya - 2.0 * yc + yb
        if abs(dd) < 1e-15 or not np.isfinite(dd):
            break
        u = step * (ya - yb) / (2.0 * dd)
        xn = x_best + u
        if not np.isfinite(xn):
            break
        x_best = float(min(max(xn, xa), xb))
    return float(x_best)
