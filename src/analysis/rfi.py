"""Baseline adaptativa e flagging de RFI com ArPLS.

Item 6 do roteiro do notebook ``02_BINGO_ANALYSIS.ipynb`` (Método 2 — melhoria
com calibração local) pede:

- aplicar o algoritmo de RFI com ArPLS (``src/arpls/baseline``);
- construir uma *baseline adaptativa* (que varia no tempo e/ou na frequência)
  e discutir as features encontradas (deriva instrumental, RFI, transitos).

Este módulo encapsula a função ``ArPLS`` (Baek et al. 2015,
:cite:`Baek2015`) de ``src/arpls/baseline.py`` num wrapper 2D: a baseline é
ajustada ao longo de um eixo escolhido (``time`` ou ``frequency``) para cada
fatia do outro eixo, retornando uma baseline com as **mesmas dims** do dado de
entrada.

A baseline adaptativa serve para separar o sinal de interesse (transitos de
Sol/satélites/radiosources, que são *features* aditivas de banda estreita e
temporalmente localizadas) da componente instrumental lisa (banda do receptor,
deriva lenta, RFI de banda larga que varia suavemente).

Exemplos
--------
>>> bl = adaptive_baseline(obs, axis="time", lam=1e5)   # por canal, no tempo
>>> resid = obs - bl                                     # features → resíduo
>>> mask = mask_rfi(resid, n_sigma=5)                    # outliers → RFI
"""

from __future__ import annotations

import numpy as np
import xarray as xr
from concurrent.futures import ThreadPoolExecutor
from scipy.ndimage import median_filter

from ._utils import _as_2d

__all__ = [
    "adaptive_baseline",
    "arpls_baseline",
    "effective_band",
    "flag_rfi_sed",
    "mad_filter",
    "mask_rfi",
    "mask_rfi_channels",
    "spectral_normalization",
]


def arpls_baseline(y, lam: float = 1e5, ratio: float = 0.05, itermax: int = 20) -> np.ndarray:
    """Baseline ArPLS 1D (Baek et al. 2015) a partir de ``src/arpls/baseline``.

    Envolve a implementação de referência do projeto
    (``src/arpls/baseline.ArPLS``) com conversão explícita para ``float``.

    Parameters
    ----------
    y:
        Série 1D a ajustar (a baseline é a componente lisa de ``y``).
    lam:
        Suavidade da baseline (maior ⇒ mais lisa).
    ratio:
        Critério de convergência (menor ⇒ mais iterações).
    itermax:
        Nº máximo de iterações.

    Returns
    -------
    np.ndarray
        Baseline 1D (mesmo comprimento de ``y``).
    """
    from arpls.baseline import ArPLS  # import tardio (módulo de RFI do projeto)

    return np.asarray(ArPLS(np.asarray(y, dtype=float), lam=lam, ratio=ratio, itermax=itermax))


def _fill_nan(y: np.ndarray) -> np.ndarray:
    """Interpola NaNs de uma série 1D (ArPLS não aceita NaN)."""
    y = np.asarray(y, dtype=float)
    if not np.isfinite(y).all():
        idx = np.arange(y.size)
        good = np.isfinite(y)
        if good.sum() == 0:
            return np.zeros_like(y)
        y = np.interp(idx, idx[good], y[good])
    return y


def _run_arpls_axis(work: np.ndarray, axis: int, lam, ratio, itermax) -> np.ndarray:
    """Aplica ArPLS ao longo de ``axis`` para cada fatia do outro eixo.

    ``work`` é 2D. Retorna a baseline 2D (mesma forma): para cada índice da
    outra dimensão, ``ArPLS`` é aplicado sobre a fatia ao longo de ``axis``.
    """
    n_slices = work.shape[1 - axis]
    out = np.full_like(work, np.nan, dtype=float)
    for k in range(n_slices):
        y = _fill_nan(work[:, k]) if axis == 0 else _fill_nan(work[k, :])
        z = arpls_baseline(y, lam=lam, ratio=ratio, itermax=itermax)
        if axis == 0:
            out[:, k] = z
        else:
            out[k, :] = z
    return out


def adaptive_baseline(
    data,
    *,
    axis: str = "time",
    lam: float = 1e5,
    ratio: float = 0.05,
    itermax: int = 20,
    channels=None,
    n_jobs: int = 1,
) -> xr.DataArray:
    """Baseline adaptativa ArPLS de um dado 2D ``(time, frequency)``.

    Ajusta uma baseline *por fatia* ao longo do eixo escolhido:

    - ``axis="time"`` (padrão): para **cada canal de frequência**, ajusta a
      baseline no tempo — captura a deriva instrumental por canal e deixa as
      features *temporalmente localizadas* (transitos, RFI pulsada) no resíduo.
    - ``axis="frequency"``: para **cada amostra de tempo**, ajusta a baseline
      espectral — captura a forma da banda (Tsys·G + D₀) e deixa as features
      *espectralmente localizadas* (linhas RFI, transitos de banda estreita)
      no resíduo.

    O resultado é uma baseline com as MESMAS dims/coords de ``data``
    (sem interpolação temporal/espectral — apenas o ajuste ArPLS por fatia).

    Parameters
    ----------
    data:
        ``ObservationData`` ou DataArray 2D ``(time, frequency)``.
    axis:
        ``"time"`` (baseline temporal por canal) ou ``"frequency"`` (baseline
        espectral por tempo).
    lam / ratio / itermax:
        Parâmetros do ArPLS (ver ``arpls_baseline``).
    channels:
        Opcional; iterável de índices a processar (para inspeção rápida em um
        subconjunto). As fatias não processadas ficam NaN.
    n_jobs:
        Nº de threads para paralelizar as fatias (padrão 1 = serial).

    Returns
    -------
    xr.DataArray
        Baseline 2D (mesmas dims/coords de ``data``), materializada.
    """
    da = data._target() if hasattr(data, "_target") else _as_2d(data)
    z = np.asarray(da.values, dtype=float)
    if z.ndim != 2:
        msg = f"adaptive_baseline exige dados 2D (time, frequency); got {z.ndim}D"
        raise ValueError(msg)

    ax = str(axis).lower()
    if ax in ("time", "t"):
        work = z.T  # (nf, nt): eixo 0 = frequência, eixo 1 = tempo
        work_axis = 1
        n = work.shape[0]
    elif ax in ("frequency", "freq", "f"):
        work = z  # (nt, nf): eixo 0 = tempo, eixo 1 = frequência
        work_axis = 0
        n = work.shape[0]
    else:
        msg = f"axis desconhecido: {axis!r} (use 'time' | 'frequency')"
        raise ValueError(msg)

    indices = list(range(n)) if channels is None else [int(c) for c in channels]
    bl = np.full_like(work, np.nan, dtype=float)

    def _one(k: int) -> tuple[int, np.ndarray]:
        y = _fill_nan(work[k, :]) if ax in ("time", "t") else _fill_nan(work[k, :])
        return k, arpls_baseline(y, lam=lam, ratio=ratio, itermax=itermax)

    if n_jobs and n_jobs > 1:
        with ThreadPoolExecutor(max_workers=int(n_jobs)) as ex:
            for k, zz in ex.map(_one, indices):
                bl[k, :] = zz
    else:
        for k in indices:
            bl[k, :] = _one(k)[1]

    # desfaz a transposição → baseline com a MESMA forma do dado de entrada
    if ax in ("time", "t"):
        baseline = bl.T
    else:
        baseline = bl

    out = da.copy(data=baseline)
    out.attrs.update({"baseline": f"arpls_{axis}", "lam": lam, "itermax": itermax})
    return out


def mask_rfi(
    residual, n_sigma: float = 5.0, axis: str | None = None, min_frac: float = 0.0
) -> np.ndarray:
    """Máscara booleana de RFI a partir de um resíduo (outliers por MAD).

    Um ponto é marcado como RFI se estiver a mais de ``n_sigma`` desvios (MAD
    escalada) da mediana de referência. A referência é:

    - ``axis=None``: estatísticas globais do resíduo inteiro;
    - ``axis="time"``: estatísticas por **canal de frequência** (RFI que afeta
      um canal ao longo de todo o tempo);
    - ``axis="frequency"``: estatísticas por **amostra de tempo**.

    ``min_frac`` (0–1) remove canais/tempos com fração de RFI acima do limite
    (útil para descartar canais permanentemente poluídos antes do fit).

    Parameters
    ----------
    residual:
        Array/DataArray 2D ``(time, frequency)`` do sinal após subtrair a
        baseline adaptativa (as features — transitos e RFI — ficam aqui).
    n_sigma:
        Limiar de detecção em unidades de MAD.
    axis:
        Eixo da estatística de referência (``None`` | ``"time"`` | ``"frequency"``).
    min_frac:
        Fração máxima de RFI tolerada; acima disso a linha/coluna é toda mascarada.

    Returns
    -------
    np.ndarray
        Array booleano 2D com a mesma forma de ``residual`` (``True`` = RFI).
    """
    if hasattr(residual, "values"):
        r = np.asarray(residual.values, dtype=float)
    else:
        r = np.asarray(residual, dtype=float)
    if r.ndim != 2:
        msg = "mask_rfi exige dados 2D (time, frequency)."
        raise ValueError(msg)

    def _mad_mask(a: np.ndarray, sigma: float) -> np.ndarray:
        m = np.nanmedian(a)
        s = 1.4826 * np.nanmedian(np.abs(a - m))
        if not np.isfinite(s) or s <= 0:
            return np.zeros(a.shape, dtype=bool)
        return np.abs(a - m) > sigma * s

    ax = str(axis).lower() if axis else "none"
    if ax == "time":  # por canal de frequência (cada coluna)
        mask = np.stack([_mad_mask(r[:, k], n_sigma) for k in range(r.shape[1])], axis=1)
    elif ax == "frequency":  # por amostra de tempo (cada linha)
        mask = np.stack([_mad_mask(r[i, :], n_sigma) for i in range(r.shape[0])], axis=0)
    else:
        mask = _mad_mask(r, n_sigma)

    if min_frac and min_frac > 0:
        # descarta canais (colunas) com RFI demais ao longo do tempo
        frac = mask.mean(axis=0)
        mask = mask | (frac > min_frac)[None, :]
    return mask


def mask_rfi_channels(
    data,
    *,
    n_sigma: float = 6.0,
    smooth: int = 41,
    min_dev: float = 0.01,
    mask_positive: bool = True,
    mask_negative: bool = True,
) -> np.ndarray:
    """Mascara canais de frequência com RFI **persistente** (picos ou dips).

    O flagging temporal (`mask_rfi(..., axis="time")`) só vê excursões que
    variam no tempo — uma RFI de banda estreita **constante** (linha fixa, ou
    um canal morto/em absorção) não é outlier no tempo dentro do próprio canal
    e passa despercebida. Esta função detecta esses canais pelo **perfil
    espectral** (mediana temporal por canal) comparado a uma tendência local
    suavizada (mediana móvel de ``smooth`` canais):

    .. math::

        \\delta(\\nu) = \\frac{M(\\nu) - \\bar M(\\nu)}{\\bar M(\\nu)},
        \\qquad
        \\text{canal RFI se } |\\delta(\\nu) - \\mathrm{med}\\,\\delta|
        > \\max(n_\\sigma\\cdot\\mathrm{MAD}\\,\\delta,\\; \\text{min\\_dev})

    Canais anômalos são mascarados em **todas** as amostras de tempo (colunas
    inteiras). ``mask_positive``/``mask_negative`` controlam se picos (RFI de
    emissão, ``δ>0``) e dips (canais mortos/absorção, ``δ<0``) são flagados —
    desative um deles para um flagging ainda menos agressivo.

    O limiar combina um critério estatístico (``n_sigma``·MAD — robusto quando
    há muitos canais anômalos) com um mínimo absoluto (``min_dev``) para não
    explodir quando o MAD do desvio é ~0 (banda lisa com poucos anômalos).

    Parameters
    ----------
    data:
        ``ObservationData`` ou DataArray 2D ``(time, frequency)`` — use a
        **observação original** (counts) para capturar também dips na baseline.
    n_sigma:
        Limiar estatístico (unidades de MAD do desvio relativo).
    smooth:
        Janela (ímpar) da mediana móvel espectral (tendência local).
    min_dev:
        Desvio relativo mínimo aceito (ex.: ``0.01`` = 1 %) — evita flagar
        canais com desvios minúsculos quando o MAD é ~0.
    mask_positive / mask_negative:
        Flagar picos (``δ>0``) e/ou dips (``δ<0``).

    Returns
    -------
    np.ndarray
        Máscara booleana 2D com a mesma forma de ``data`` (colunas inteiras
        ``True`` nos canais RFI).
    """
    da = data._target() if hasattr(data, "_target") else _as_2d(data)
    z = np.asarray(da.values, dtype=float)
    if z.ndim != 2:
        msg = "mask_rfi_channels exige dados 2D (time, frequency)."
        raise ValueError(msg)

    omed = np.nanmedian(z, axis=0)
    smooth = int(smooth)
    if smooth % 2 == 0:
        smooth += 1
    osm = median_filter(omed, size=smooth, mode="nearest")
    denom = np.where(osm > 0, osm, float(np.nanmedian(osm)))
    delta_rel = (omed - osm) / denom

    med = float(np.nanmedian(delta_rel))
    s = 1.4826 * np.nanmedian(np.abs(delta_rel - med))
    if not np.isfinite(s):
        s = 0.0
    thr = max(n_sigma * s, float(min_dev))

    dev = delta_rel - med
    chan = np.abs(dev) > thr
    if not mask_positive:
        chan &= dev < 0
    if not mask_negative:
        chan &= dev > 0

    return np.broadcast_to(chan, z.shape).copy()


def flag_rfi_sed(
    data,
    *,
    lam: float = 1e5,
    line_nsigma: float = 5.0,
    blob_chi: float | None = None,
    sed_stat: str = "mean",
    sm_kwargs: dict | None = None,
    di_kwargs: dict | None = None,
):
    """Procedimento ArPLS-ST (SED + baseline + SumThreshold) p/ medidas lineares.

    Roteiro do pré-processamento (item 6) aplicado a um dado 2D
    ``S(t, freq)`` (ex.: observação em ADU — medidas **lineares**):

    1. **SED** — espectro médio por canal: ``SED(freq) = ⟨S⟩_t``
       (``mean`` — como no roteiro ``sum_s/n_t`` — ou ``median``, mais robusto);
    2. **Baseline** — ``ArPLS(SED)`` modela a forma da banda (componente lisa);
    3. **Linhas RFI** — ``diff = SED − baseline``; canais com desvio > ``n_sigma``
       MAD são mascarados em **todas** as amostras de tempo (RFI persistente,
       ex.: o dip em ~1125 MHz);
    4. **Baseline removal na imagem** — ``resid = S(t,f) − baseline(f)``;
    5. **Blobs RFI** — ``SumThreshold`` (``arpls.st_mask``) no resíduo: detecta
       RFI localizada (transitória/2D);
    6. **Máscara final** — ``linhas | blobs``.

    Ao contrário de ``arpls.arpls_mask`` (que usa ``ksigma`` por ajuste
    gaussiano e assume dados já de banda plana), esta versão usa estatísticas
    **robustas (MAD)** e remove a baseline espectral antes do SumThreshold,
    adequada ao caso em que a forma da banda domina o espectro.

    Parameters
    ----------
    data:
        ``ObservationData`` ou DataArray 2D ``(time, frequency)``.
    lam:
        Suavidade do ArPLS da SED (maior ⇒ baseline mais lisa).
    line_nsigma:
        Limiar (em MAD) para canais de RFI persistentes no resíduo da SED.
    blob_chi:
        Threshold inicial do SumThreshold (unidades do dado). Se ``None``,
        estimado como ``5·MAD(resíduo)``.
    sed_stat:
        ``"mean"`` (roteiro) ou ``"median"`` (robusto a RFI na SED).
    sm_kwargs / di_kwargs:
        Suavização/dilatação do SumThreshold (ver ``arpls.get_sm_kwargs``).

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        ``(mask, baseline, sed)`` — máscara booleana 2D (mesma forma de
        ``data``), baseline espectral ``(frequency,)`` e SED ``(frequency,)``.
    """
    from arpls import (
        ArPLS,
        get_di_kwargs,
        get_sm_kwargs,
        st_mask,
    )

    da = data._target() if hasattr(data, "_target") else _as_2d(data)
    Z = np.asarray(da.values, dtype=float)  # (time, frequency)
    if Z.ndim != 2:
        msg = "flag_rfi_sed exige dados 2D (time, frequency)."
        raise ValueError(msg)

    # 1) SED — espectro médio por canal
    if str(sed_stat).lower() in ("median", "med"):
        sed = np.nanmedian(Z, axis=0)
    else:
        sed = np.nanmean(Z, axis=0)

    # 2) baseline espectral via ArPLS
    bl = np.asarray(ArPLS(sed, lam=lam, ratio=0.05, itermax=20), dtype=float)

    # 3) linhas RFI (canais persistentes) por MAD no resíduo da SED
    diff = sed - bl
    med_d = float(np.nanmedian(diff))
    mad_d = 1.4826 * np.nanmedian(np.abs(diff - med_d))
    thr_line = max(float(line_nsigma) * mad_d, 1e-9)
    line_mask = np.abs(diff - med_d) > thr_line

    # 4) baseline removal na imagem (medidas lineares)
    resid = Z - bl[None, :]

    # 5) blobs RFI via SumThreshold no resíduo
    r = np.nan_to_num(resid, nan=0.0)
    if blob_chi is None:
        blob_chi = 5.0 * (1.4826 * np.median(np.abs(r - np.median(r))))
    sm = sm_kwargs or get_sm_kwargs(40, 20, 7.5, 15)
    di = di_kwargs or get_di_kwargs(3, 3)
    blob = st_mask(r.T, chi_1=float(blob_chi), sm_kwargs=sm, di_kwargs=di).T

    mask = line_mask[None, :] | blob.astype(bool)
    return mask, bl, sed


# ──────────────────────────────────────────────────────────────────
# Normalização espectral e filtro MAD (Buch et al. 2016) — TODO
# ──────────────────────────────────────────────────────────────────
def effective_band(
    data,
    *,
    frac: float = 0.9,
    lam: float = 1e7,
    ratio: float = 0.01,
    itermax: int = 50,
) -> np.ndarray:
    """Máscara booleana 1D (sobre ``frequency``) da banda efetiva.

    Determinação da banda efetiva (TODO de normalização espectral):

    1. **SED** — espectro mediano por canal (``M_m = mediana_t S(m, t)``);
    2. **Baseline ao longo da frequência** com **ArPLS agressivo**
       (``lam`` alto / ``ratio`` baixo) — modela a componente lisa (piso
       instrumental); usada como diagnóstico visual;
    3. **Clipping** — canais cujo sinal está abaixo de ``frac`` × **mediana do
       espectro** (SED) são excluídos (bordas da banda / canais mortos),
       restando a banda efetiva onde a resposta do receptor é alta.

    Parameters
    ----------
    data:
        ``ObservationData`` ou DataArray 2D ``(time, frequency)`` (use a
        observação original — a forma da banda está nela).
    frac:
        Fração da mediana da baseline abaixo da qual o canal é excluído
        (ex.: ``0.9`` = 90 %).
    lam / ratio / itermax:
        Parâmetros do ArPLS agressivo (ver ``arpls_baseline``).

    Returns
    -------
    np.ndarray
        Array booleano 1D de comprimento = nº de canais (``True`` = na banda
        efetiva).
    """
    da = data._target() if hasattr(data, "_target") else _as_2d(data)
    z = np.asarray(da.values, dtype=float)
    if z.ndim != 2:
        msg = "effective_band exige dados 2D (time, frequency)."
        raise ValueError(msg)

    sed = np.nanmedian(z, axis=0)  # (nf,) — espectro mediano por canal
    # baseline ArPLS agressiva ao longo da frequência — modela a componente
    # lisa (piso instrumental); usada como diagnóstico visual.
    baseline = arpls_baseline(sed, lam=lam, ratio=ratio, itermax=itermax)
    # referência de clipping: mediana do espectro (nível central da banda).
    # Canais cujo sinal cai abaixo de ``frac`` × essa mediana (bordas da banda,
    # canais mortos/em absorção) são excluídos da banda efetiva.
    ref = float(np.nanmedian(sed))
    if not np.isfinite(ref) or ref <= 0:
        return np.ones(z.shape[1], dtype=bool)
    return sed >= frac * ref


def spectral_normalization(
    data,
    *,
    kernel: int = 51,
    stat: str = "median",
) -> tuple[xr.DataArray, np.ndarray, np.ndarray]:
    """Normalização espectral Buch2016: ``S_norm = S / M_S``.

    Procedimento do TODO (refs/buch2016.pdf):

    1. **Espectro mediano** ``M_m = mediana_t S(m, t)`` por canal
       (``stat="median"``; ``"mean"`` também disponível);
    2. **Running median filter ao longo da frequência** do espectro mediano →
       espectro suavizado ``M_S`` (janela ímpar ``kernel``);
    3. **Normalização** por canal e por tempo: ``S_norm(i,t) = S(i,t) / M_S(i)``.

    O espectro suavizado ``M_S`` modela a forma da banda (envelope do
    receptor); a divisão por ele remove essa forma e deixa o sinal
    ~1 (unidade) fora das features — base para o ``mad_filter``.

    Parameters
    ----------
    data:
        ``ObservationData`` ou DataArray 2D ``(time, frequency)``.
    kernel:
        Janela (ímpar) do running median filter espectral.
    stat:
        Estatística temporal do espectro mediano: ``"median"`` (padrão,
        robusto) ou ``"mean"``.

    Returns
    -------
    tuple[xr.DataArray, np.ndarray, np.ndarray]
        ``(normalized, med_spectrum, smoothed_spectrum)`` — espectro
        normalizado (mesmas dims/coords de ``data``), espectro mediano
        ``(frequency,)`` e espectro suavizado ``(frequency,)``.
    """
    da = data._target() if hasattr(data, "_target") else _as_2d(data)
    z = np.asarray(da.values, dtype=float)
    if z.ndim != 2:
        msg = "spectral_normalization exige dados 2D (time, frequency)."
        raise ValueError(msg)

    if str(stat).lower() in ("mean", "avg"):
        med = np.nanmean(z, axis=0)
    else:
        med = np.nanmedian(z, axis=0)

    k = int(kernel)
    if k % 2 == 0:
        k += 1
    m_s = median_filter(med, size=k, mode="nearest")
    denom = np.where(m_s > 0, m_s, np.nan)  # evita divisão por zero
    norm = z / denom[None, :]

    out = da.copy(data=norm)
    out.attrs.update(
        {
            "normalization": "spectral_mad",
            "kernel": int(k),
            "stat": str(stat),
        }
    )
    return out, med, m_s


def mad_filter(
    data,
    *,
    n_sigma: float = 3.0,
    axis: str | None = "frequency",
    mode: str = "clip",
    fill_value: float | None = None,
) -> tuple[xr.DataArray, np.ndarray]:
    """Filtro MAD (Buch et al. 2016) — detecta e substitui outliers.

    Para cada janela de referência calcula a mediana ``M`` e o desvio robusto
    ``sigma_R = 1.4826 · MAD`` (MAD = mediana de ``|x − M|``), com limiares
    ``U = M + n_sigma·sigma_R`` e ``L = M − n_sigma·sigma_R``. Pontos fora de
    ``[L, U]`` são outliers e substituídos conforme ``mode``:

    - ``"clip"``: substitui pelo limiar (``U`` se acima, ``L`` se abaixo);
    - ``"median"``: substitui pela mediana de referência;
    - ``"constant"``/``"replace"``: substitui por ``fill_value`` (padrão:
      mediana global dos dados).

    ``axis`` define a janela de referência:

    - ``"frequency"`` (padrão): por amostra de tempo (cada linha) — remove
      outliers **espectrais** (linhas RFI de banda estreita);
    - ``"time"``: por canal de frequência (cada coluna) — remove outliers
      **temporais** (RFI impulsiva/pulsada);
    - ``None``: estatísticas globais.

    Parameters
    ----------
    data:
        ``ObservationData`` ou DataArray 2D ``(time, frequency)`` — ex.: o
        espectro normalizado de ``spectral_normalization``.
    n_sigma:
        Limiar de detecção em unidades de desvio robusto (``~3`` ótimo).
    axis:
        Eixo da estatística de referência (``"frequency"`` | ``"time"`` |
        ``None``).
    mode:
        Estratégia de substituição: ``"clip"`` | ``"median"`` |
        ``"constant"``.
    fill_value:
        Valor de substituição em ``mode="constant"`` (padrão: mediana
        global dos dados).

    Returns
    -------
    tuple[xr.DataArray, np.ndarray]
        ``(filtered, mask)`` — dado filtrado (mesmas dims/coords de ``data``)
        e máscara booleana 2D dos pontos detectados como RFI (``True``).
    """
    da = data._target() if hasattr(data, "_target") else _as_2d(data)
    r = np.asarray(da.values, dtype=float)
    if r.ndim != 2:
        msg = "mad_filter exige dados 2D (time, frequency)."
        raise ValueError(msg)

    def _stats(a: np.ndarray) -> tuple[float, float]:
        m = float(np.nanmedian(a))
        s = 1.4826 * float(np.nanmedian(np.abs(a - m)))
        if not np.isfinite(s) or s <= 0:
            s = float("nan")  # sem dispersão → sem filtragem
        return m, s

    ax = str(axis).lower() if axis else "none"
    if ax in ("time", "t"):  # por coluna (canal de frequência)
        med = np.array([_stats(r[:, k])[0] for k in range(r.shape[1])])[None, :]
        sig = np.array([_stats(r[:, k])[1] for k in range(r.shape[1])])[None, :]
    elif ax in ("frequency", "freq", "f"):  # por linha (amostra de tempo)
        med = np.array([_stats(r[k, :])[0] for k in range(r.shape[0])])[:, None]
        sig = np.array([_stats(r[k, :])[1] for k in range(r.shape[0])])[:, None]
    else:
        med, sig = _stats(r)
        med = np.asarray(med)
        sig = np.asarray(sig)

    thr = n_sigma * sig
    mask = np.abs(r - med) > thr  # comparação com NaN → False (sem filtragem)

    out = r.copy()
    if mask.any():
        if mode == "clip":
            up = med + thr
            lo = med - thr
            repl = np.where(r > med, up, lo)  # (nt, nf) por broadcasting
            out[mask] = repl[mask]
        elif mode == "median":
            out[mask] = np.broadcast_to(med, r.shape)[mask]
        else:  # constant / replace
            fv = float(fill_value) if fill_value is not None else float(np.nanmedian(r))
            out[mask] = fv

    filtered = da.copy(data=out)
    filtered.attrs.update({"mad_filter": True, "n_sigma": n_sigma, "axis": axis, "mode": mode})
    return filtered, mask
