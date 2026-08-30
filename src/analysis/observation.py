"""Classe ``ObservationData`` — encapsula dados ``(time × frequency)``.

Fornece métodos de manipulação implementados como *sufixos de xarray*: cada
transformação retorna uma **nova** instância (padrão imutável), permitindo
encadeamento, ex.::

    obs = ObservationData(obs_data)
    obs.resample(interval_s=60, n_bins=1024).remove_baseline("median")

Cobre observações (``power``) e simulações (``T_antenna``), com os métodos:

- ``resample``           — binning temporal (interval_s) e espectral (n_bins),
                           retornando média **e** desvio padrão.
- ``remove_baseline``    — median / savitsky_golay / MAD, ou remoção da
                           assinatura quiet (``quiet_signature=True``).
- ``get_quiet_signature``— janela de ``window_min`` (padrão 30 min) com a
                           menor mediana → espectro quiet de referência.
- ``align_time``         — alinha temporalmente com um dataset de referência
                           (cross-correlação).
- ``get_event``          — slice temporal (nomenclatura de simulação).
- ``to_power_spectrum``  — converte temperatura de brilho (K) → potência (W/Hz).

Nota de memória: os métodos operam de forma lazy sempre que os dados forem
dask; materialize (``.load()``/``.compute()``) apenas o resultado reduzido.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr
from scipy import signal as sp_signal

from ._utils import _as_2d, _time_seconds
from .loading import K_B

# Métodos de baseline aceitos (normalizados: minúsculas, sem acento/_/-)
_BASELINE_METHODS = ("median", "savitsky_golay", "mad")


def _norm_method(method: str) -> str:
    """Normaliza o nome do método (ex.: 'Savitsky-Golay' → 'savitsky_golay')."""
    m = str(method).lower().replace("-", "_").replace(" ", "_")
    return m.replace("savgol", "savitsky_golay").replace("savitzky", "savitsky")


def estimate_time_lag(
    obs,
    sim,
    *,
    window=None,
    lag_range=(-60, 60),
    robust: bool = True,
) -> tuple[int, np.ndarray]:
    """Estima o atraso temporal (em amostras) entre obs e sim.

    Método robusto a RFI: em vez de correlacionar a série média sobre a banda
    (dominada por RFI/deriva), faz um **scan** de deslocamentos e, para cada um,
    calcula a correlação de Pearson **por canal** (vetorizada) entre os dois
    espectros no intervalo comum; o lag escolhido é o que maximiza a mediana
    das correlações por canal.

    Parameters
    ----------
    obs, sim:
        ``ObservationData`` ou xarray com dims ``time x frequency`` (mesma
        dimensão de frequência; grids podem ser ligeiramente diferentes, desde
        que alinháveis por índice).
    window:
        Opcional, ``(start, end)`` — restringe o scan a uma janela temporal
        (ex.: janela do transito do Sol), onde o sinal comum é relativamente
        maior frente a RFI.
    lag_range:
        Intervalo de lags a testar, em amostras.
    robust:
        Se ``True``, remove a baseline por canal (mediana temporal) de ambos
        antes de correlacionar.

    Returns
    -------
    tuple[int, np.ndarray]
        ``(lag, perfil)`` onde ``lag`` é o deslocamento a **somar** à coordenada
        ``time`` de ``obs`` para alinhá-la a ``sim`` (em amostras) e ``perfil``
        é a mediana da correlação por canal para cada lag testado.
    """
    obs_da = obs._target() if isinstance(obs, ObservationData) else _as_2d(obs)
    sim_da = sim._target() if isinstance(sim, ObservationData) else _as_2d(sim)
    if window is not None:
        start, end = window
        obs_da = obs_da.sel(time=slice(start, end))
        sim_da = sim_da.sel(time=slice(start, end))
    if robust:
        obs_da = obs_da - obs_da.median("time")
        sim_da = sim_da - sim_da.median("time")
    o = np.asarray(obs_da.values, dtype=float)
    s = np.asarray(sim_da.values, dtype=float)
    n = min(o.shape[0], s.shape[0])
    lo, hi = int(lag_range[0]), int(lag_range[1])

    def _medcorr(shift: int) -> float:
        if shift >= 0:
            a, b = o[shift : shift + n], s[:n]
        else:
            a, b = o[:n], s[-shift : -shift + n]
        m = min(a.shape[0], b.shape[0])
        a, b = a[:m], b[:m]
        a = a - a.mean(axis=0)
        b = b - b.mean(axis=0)
        den = np.sqrt((a * a).sum(axis=0) * (b * b).sum(axis=0))
        with np.errstate(divide="ignore", invalid="ignore"):
            cc = np.where(den > 0, (a * b).sum(axis=0) / np.where(den > 0, den, 1), np.nan)
        return float(np.nanmedian(cc))

    profile = np.array([_medcorr(sft) for sft in range(lo, hi + 1)])
    best = int(lo + int(np.nanargmax(profile)))
    return best, profile


class ObservationData:
    """Dados ``(time × frequency)`` com transformações encadeáveis.

    Parameters
    ----------
    data:
        ``xr.DataArray`` ou ``xr.Dataset`` com dims ``time`` e ``frequency``.
    name:
        Variável alvo quando ``data`` é Dataset (default: ``T_antenna`` se
        existir, senão a primeira data_var).
    kind:
        ``"obs"`` (observação) ou ``"sim"`` (simulação) — usado em rótulos.
    """

    def __init__(
        self, data, *, name: str | None = None, kind: str = "obs", meta: dict | None = None
    ) -> None:
        if isinstance(data, xr.Dataset):
            # Mantém o Dataset como está (pode ter <name> e <name>_std do
            # resample); as transformações usam _target() para pegar a variável.
            if name is None:
                name = "T_antenna" if "T_antenna" in data else list(data.data_vars)[0]
            self.data = data
        else:
            self.data = data
            if name is None:
                name = str(self.data.name) if self.data.name else "power"
        self.name = name
        self.kind = kind
        self.meta = dict(meta or {})

    # ──────────────────────────────────────────────────────────────
    # Acesso
    # ──────────────────────────────────────────────────────────────
    @property
    def time(self) -> np.ndarray:
        return np.asarray(self.data["time"].values)

    @property
    def frequency(self) -> np.ndarray:
        return np.asarray(self.data["frequency"].values, dtype=float)

    @property
    def time_seconds(self) -> np.ndarray:
        return _time_seconds(self.data)

    @property
    def shape(self):
        return self.data.shape

    def __repr__(self) -> str:
        dims = ", ".join(f"{d}={s}" for d, s in self.data.sizes.items())
        return f"<ObservationData kind={self.kind!r} name={self.name!r} ({dims})>"

    def _like(self, da: xr.DataArray, **kw) -> ObservationData:
        """Nova instância preservando nome/kind/meta.

        Se ``self.data`` for um Dataset (ex.: resultado do ``resample`` com
        média + desvio padrão), o Dataset é preservado e a variável alvo é
        atualizada — outras variáveis (ex.: ``<name>_std``) são mantidas.
        """
        name = kw.pop("name", da.name or self.name)
        if isinstance(self.data, xr.Dataset):
            ds = xr.Dataset({name: da})
            if name == self.name:  # preserva variáveis irmãs (ex.: _std)
                for v in self.data.data_vars:
                    if v != self.name:
                        ds[v] = self.data[v]
            return ObservationData(ds, name=name, kind=self.kind, meta=self.meta, **kw)
        return ObservationData(da, name=name, kind=self.kind, meta=self.meta, **kw)

    def _target(self) -> xr.DataArray:
        """Retorna o DataArray alvo (seleciona ``self.name`` em Dataset)."""
        if isinstance(self.data, xr.Dataset):
            return self.data[self.name]
        return self.data

    # ──────────────────────────────────────────────────────────────
    # resample — binning temporal + espectral (média e desvio padrão)
    # ──────────────────────────────────────────────────────────────
    def resample(
        self, interval_s: float = 60, n_bins: int = 1024, stat: str = "mean", with_std: bool = True
    ) -> ObservationData:
        """Resample por binning (integração) em tempo e frequência.

        O eixo temporal é agrupado em janelas de ``interval_s`` segundos e o
        eixo de frequência em ``n_bins`` bins. **Não** usa interpolação: cada
        bin de saída é a agregação dos pontos originais que caem nele
        (``xarray.coarsen``). A estatística do bin é controlada por ``stat``:

        - ``"mean"`` — média (preserva a densidade de potência; padrão);
        - ``"sum"``  — **integração** (soma os counts/potência no bin);
        - ``"median"`` — mediana (robusta a outliers/RFI).

        Retorna um Dataset com a variável agregada (``self.name``) e o desvio
        padrão (``self.name + '_std'``), com dims ``(time, frequency)``.

        Parameters
        ----------
        interval_s:
            Largura do bin temporal (segundos).
        n_bins:
            Nº de bins de frequência na saída.
        stat:
            Estatística do bin: ``"mean"`` | ``"sum"`` | ``"median"``.
        with_std:
            Incluir a variável ``<name>_std`` (desvio padrão por bin).

        Returns
        -------
        ObservationData
            Novo objeto com ``.data`` = Dataset {name: <stat>, name_std: std}.
        """
        da = self._target()
        stat = str(stat).lower()
        if stat not in ("mean", "sum", "median"):
            msg = f"stat desconhecido: {stat!r} (use 'mean' | 'sum' | 'median')"
            raise ValueError(msg)

        # 1) binning temporal (coarsen por fator inteiro) — sem interpolação
        dt_s = float(np.median(np.diff(self.time_seconds)))
        time_factor = max(1, int(round(interval_s / dt_s)))
        tmean = da.coarsen(time=time_factor, boundary="trim", coord_func="mean").mean()

        # 2) rebin espectral EXATO para n_bins (integração sobre o grid)
        f = np.asarray(da["frequency"].values, dtype=float)
        target_freq = np.linspace(float(f[0]), float(f[-1]), int(n_bins))
        agg = _rebin_to_grid(tmean, target_freq, stat).rename(self.name)

        out: dict[str, xr.DataArray] = {self.name: agg}
        if with_std:
            # desvio padrão temporal dentro de cada bin, rebinado p/ o grid
            std_t = da.coarsen(time=time_factor, boundary="trim", coord_func="mean").std()
            out[f"{self.name}_std"] = _rebin_to_grid(std_t, target_freq, "mean").rename(
                f"{self.name}_std"
            )

        ds = xr.Dataset(out)
        ds[self.name].attrs = da.attrs
        return ObservationData(ds, name=self.name, kind=self.kind, meta=self.meta)

    # ──────────────────────────────────────────────────────────────
    # rebin_frequency — integração num grid de frequência alvo
    # ──────────────────────────────────────────────────────────────
    def rebin_frequency(self, target_freq, stat: str = "mean") -> ObservationData:
        """Rebin (integra) a frequência num grid alvo — **sem interpolação**.

        Cada bin do grid alvo recebe a agregação (média ou **integração** =
        soma) de todos os canais originais cujo centro cai dentro dele. O grid
        de saída é exatamente ``target_freq`` (canais sem cobertura → NaN).

        Parâmetros
        ----------
        target_freq:
            Centros dos bins de saída (array, em MHz).
        stat:
            ``"mean"`` (padrão) ou ``"sum"`` (integração) por bin.

        Returns
        -------
        ObservationData
            Mesma dimensão temporal, frequência = ``target_freq``.
        """
        tf = np.asarray(target_freq, dtype=float)
        if tf.ndim != 1 or tf.size < 2:
            msg = "target_freq deve ser um array 1D com >= 2 bins."
            raise ValueError(msg)
        res = _rebin_to_grid(self._target(), tf, stat)
        return self._like(res.rename(self.name))

    # ──────────────────────────────────────────────────────────────
    # get_quiet_signature — janela de 30 min com a menor mediana
    # ──────────────────────────────────────────────────────────────
    def get_quiet_signature(self, window_min: float = 30) -> xr.DataArray:
        """Espectro quiet de referência (média da janela de menor mediana).

        Encontra a janela contígua de ``window_min`` minutos (padrão 30) com a
        menor mediana da série temporal (média espectral por tempo) e retorna o
        espectro médio dessa janela: baseline por frequência ``(frequency,)``.

        Nota: para dados observacionais de alta cadência, chame **antes** em
        dados ``resample``-ados (ex.: interval_s=60), senão a busca na série
        completa fica cara.

        Returns
        -------
        xr.DataArray
            Espectro quiet ``(frequency,)``.
        """
        da = self._target()
        tsec = self.time_seconds
        dt_s = float(np.median(np.diff(tsec)))
        win_n = max(3, int(round(window_min * 60.0 / dt_s)))

        series = np.asarray(da.mean("frequency").values, dtype=float)
        roll = pd.Series(series).rolling(win_n, min_periods=win_n).median()
        argmin = int(np.nanargmin(roll.values))
        start = max(0, argmin - win_n + 1)
        return da.isel(time=slice(start, start + win_n)).mean("time")

    # ──────────────────────────────────────────────────────────────
    # slice — recorte temporal e/ou espectral (sem interpolação)
    # ──────────────────────────────────────────────────────────────
    def slice(
        self, start=None, end=None, *, center=None, window_min=None, fmin=None, fmax=None
    ) -> ObservationData:
        """Recorta tempo e/ou frequência do dataset (sem interpolação).

        O recorte temporal aceita ``start``/``end`` (datetime64, ISO str ou
        Timestamp) ou ``center`` + ``window_min`` (meia-janela em minutos). O
        recorte espectral aceita ``fmin``/``fmax`` (em MHz — a frequência é
        normalizada para MHz no carregamento).

        Parameters
        ----------
        start, end:
            Limites do intervalo temporal.
        center:
            Centro do intervalo temporal (com ``window_min``).
        window_min:
            Meia-janela em minutos em torno de ``center``.
        fmin, fmax:
            Limites do intervalo espectral (MHz).

        Returns
        -------
        ObservationData
            Slice (dims reduzidas em ``time`` e/ou ``frequency``).
        """
        if center is not None and window_min is not None:
            start = pd.Timestamp(center) - pd.Timedelta(minutes=window_min)
            end = pd.Timestamp(center) + pd.Timedelta(minutes=window_min)
        da = self._target()
        if start is not None or end is not None:
            if start is None or end is None:
                msg = "slice temporal requer start E end (ou center + window_min)."
                raise ValueError(msg)
            da = da.sel(time=slice(start, end))
        if fmin is not None or fmax is not None:
            if fmin is None or fmax is None:
                msg = "slice espectral requer fmin E fmax."
                raise ValueError(msg)
            da = da.sel(frequency=slice(fmin, fmax))
        return self._like(da)

    # ──────────────────────────────────────────────────────────────
    # temporal_median — mediana espectral por amostra de tempo
    # ──────────────────────────────────────────────────────────────
    def temporal_median(self) -> np.ndarray:
        """Mediana sobre a frequência **em cada tempo** (série temporal).

        Reduz o espectro a um escalar por amostra de tempo — útil para
        inspecionar a evolução temporal (transitos, RFI, quiet zone) e para o
        alinhamento temporal por cross-correlação.

        Returns
        -------
        np.ndarray
            Série ``(time,)`` com a mediana espectral por tempo.
        """
        da = self._target()
        return np.asarray(da.median("frequency").values, dtype=float)

    # ──────────────────────────────────────────────────────────────
    # normalize — normalização por mediana (ex.: quiet signal)
    # ──────────────────────────────────────────────────────────────
    def normalize(
        self, *, baseline=None, quiet: bool = False, window_min: float = 30
    ) -> ObservationData:
        """Normaliza pela mediana do espectro: ``(D − M) / M``.

        Implementa a normalização *bandpass* do roteiro:
        :math:`\\delta D(t,\\nu) = \\big(D(t,\\nu) - M(\\nu)\\big) / M(\\nu)`,
        onde :math:`M(\\nu)` é a mediana por canal usada como referência:

        - ``quiet=True`` → ``M`` = assinatura quiet
          (``get_quiet_signature`` — janela de menor mediana);
        - ``baseline=<espectro>`` → usa um espectro ``(frequency,)`` explícito;
        - padrão (nenhum) → ``M`` = mediana temporal do próprio dado.

        Parameters
        ----------
        baseline:
            Espectro de referência ``(frequency,)`` (DataArray ou array).
        quiet:
            Se ``True``, deriva ``M`` da assinatura quiet.
        window_min:
            Janela (min) para ``get_quiet_signature`` quando ``quiet=True``.

        Returns
        -------
        ObservationData
            Dados normalizados (mesmas dims/coords).
        """
        da = self._target()
        if baseline is None:
            baseline = (
                self.get_quiet_signature(window_min=window_min) if quiet else da.median("time")
            )
        if isinstance(baseline, xr.DataArray):
            M = baseline.interp(frequency=da["frequency"].values).assign_coords(
                frequency=da["frequency"].values
            )
        else:
            b = np.asarray(baseline, dtype=float)
            if b.ndim == 1 and b.size == da.sizes["frequency"]:
                M = da.isel(time=0).copy(data=b).rename(da.name or "M")
            else:
                M = da * 0.0 + b  # broadcast simples (escalar)
        out = (da - M) / M
        out.attrs.update({"normalization": "quiet_median" if quiet else "median"})
        return self._like(out)

    # ──────────────────────────────────────────────────────────────
    # remove_baseline — median / savitsky_golay / MAD (ou assinatura quiet)
    # ──────────────────────────────────────────────────────────────
    def remove_baseline(
        self, method: str = "median", quiet_signature: bool = False, **kwargs
    ) -> ObservationData:
        """Remove a baseline do sinal, preservando as dimensões.

        Parameters
        ----------
        method:
            ``"median"`` (mediana ao longo do tempo por canal),
            ``"savitsky_golay"`` (filtro Savitzky-Golay ao longo do tempo),
            ``"mad"`` (mediana + desvio absoluto mediano ao longo do tempo).
        quiet_signature:
            Se ``True``, usa a assinatura quiet (``get_quiet_signature``) como
            baseline a remover — ignorando ``method``. Se ``False`` (padrão),
            usa a baseline derivada de ``method``.
        **kwargs:
            Repassados à baseline:
            - ``window``/``polyorder`` (savitsky_golay);
            - ``sigma_clip`` (mad);
            - ``window_min`` (get_quiet_signature quando ``quiet_signature=True``).

        Returns
        -------
        ObservationData
            Dados com a baseline subtraída (mesmas dims/coords).
        """
        da = self._target()
        if quiet_signature:
            sig = self.get_quiet_signature(window_min=kwargs.get("window_min", 30))
            baseline = sig.interp(frequency=da["frequency"].values)
        else:
            baseline = _baseline_kernel(da, method, **kwargs)
        return self._like(da - baseline)

    # ──────────────────────────────────────────────────────────────
    # adaptive_baseline / remove_adaptive_baseline — ArPLS (item 6)
    # ──────────────────────────────────────────────────────────────
    def adaptive_baseline(
        self, *, axis: str = "time", lam: float = 1e5, ratio: float = 0.05,
        itermax: int = 20, channels=None, n_jobs: int = 1,
    ) -> xr.DataArray:
        """Baseline adaptativa (ArPLS) com as mesmas dims deste dado.

        Método 2 do roteiro (item 6): separa a componente instrumental lisa
        (baseline) das *features* (transitos do Sol/satélites, RFI). A baseline
        é ajustada por fatia ao longo do eixo escolhido:

        - ``axis="time"`` — por canal de frequência ao longo do tempo (deriva
          instrumental por canal; features temporais ficam no resíduo);
        - ``axis="frequency"`` — por amostra de tempo ao longo da frequência
          (forma da banda; linhas RFI/transitos de banda estreita no resíduo).

        Envolve ``src.analysis.rfi.adaptive_baseline``. O dado é materializado
        para o ajuste (ArPLS é numpy); use em dados já reduzidos (ex.: 120s/2048).

        Returns
        -------
        xr.DataArray
            Baseline 2D (mesmas dims/coords), materializada.
        """
        from .rfi import adaptive_baseline as _ab

        return _ab(
            self._target(), axis=axis, lam=lam, ratio=ratio, itermax=itermax,
            channels=channels, n_jobs=n_jobs,
        )

    def remove_adaptive_baseline(
        self, *, axis: str = "time", lam: float = 1e5, ratio: float = 0.05,
        itermax: int = 20, channels=None, n_jobs: int = 1,
    ) -> ObservationData:
        """Retorna ``dado − baseline_adaptativa(ArPLS)`` (resíduo/features).

        O resíduo contém as features de interesse (transitos, RFI) com a
        componente instrumental lisa removida — base para o flagging de RFI e
        para a calibração local do item 6.

        Returns
        -------
        ObservationData
            Mesmas dims/coords, com a baseline ArPLS subtraída.
        """
        bl = self.adaptive_baseline(
            axis=axis, lam=lam, ratio=ratio, itermax=itermax,
            channels=channels, n_jobs=n_jobs,
        )
        return self._like(self._target() - bl)

    # ──────────────────────────────────────────────────────────────
    # align_time — alinhamento temporal com dataset de referência
    # ──────────────────────────────────────────────────────────────
    def align_time(
        self,
        reference,
        method: str = "cross-correlation",
        robust: bool = True,
        window=None,
    ) -> ObservationData:
        """Alinha o tempo deste dataset a um ``reference``.

        A série temporal (média sobre frequência) é cross-correlacionada com a
        do ``reference`` para estimar o atraso (em amostras); a coordenada
        ``time`` deste objeto é deslocada por esse atraso.

        Parameters
        ----------
        reference:
            ``ObservationData`` ou xarray com dims ``time x frequency``.
        method:
            ``"cross-correlation"`` (padrão, rápido) ou ``"lag_scan"``
            (scan de correlação por canal via ``estimate_time_lag`` — mais
            robusto a RFI; use quando o sinal comum é fraco).
        robust:
            Se ``True`` (padrão), remove a baseline por canal (mediana
            temporal de cada frequência) de **ambas** as séries antes de
            correlacionar. Necessário quando a observação tem uma baseline
            instrumental dominante (ex.: ~10^4 ADU) que mascararia o sinal de
            interesse (transito do Sol ~0,6 %) na correlação.
        window:
            Opcional, ``(start, end)`` — restringe ambas as séries a essa janela
            temporal **antes** de correlacionar. Recomendado quando o sinal
            comum (ex.: transito do Sol) é fraco frente a RFI/satélites: ancorar
            a correlação na janela do transito evita que features não-comuns
            (RFI, transitos de satélites diferentes) dominem o pico.

        Returns
        -------
        ObservationData
            Cópia com ``time`` deslocado para alinhar com ``reference``.
        """
        ref = reference.data if isinstance(reference, ObservationData) else _as_2d(reference)
        if str(method).lower() == "lag_scan":
            lag, _ = estimate_time_lag(self._target(), ref, window=window, robust=robust)
        else:
            s_self = self._target()
            s_ref = ref
            if window is not None:
                start, end = window
                s_self = s_self.sel(time=slice(start, end))
                s_ref = s_ref.sel(time=slice(start, end))
            if robust:
                s_self = s_self - s_self.median("time")
                s_ref = s_ref - s_ref.median("time")
            s_self = np.asarray(s_self.mean("frequency").values, dtype=float)
            s_ref = np.asarray(s_ref.mean("frequency").values, dtype=float)

            corr = sp_signal.correlate(s_ref - s_ref.mean(), s_self - s_self.mean(), mode="full")
            lag = len(s_ref) - 1 - int(np.argmax(corr))
        dt_s = float(np.median(np.diff(self.time_seconds)))

        t = self.time
        if np.issubdtype(np.asarray(t).dtype, np.datetime64):
            shift = np.timedelta64(int(round(lag * dt_s * 1e9)), "ns")
            t_new = t + shift
        else:
            t_new = t + lag * dt_s

        shifted = self._target().assign_coords(time=t_new)
        return self._like(shifted)

    # ──────────────────────────────────────────────────────────────
    # get_event — slice temporal (nomenclatura de simulação)
    # ──────────────────────────────────────────────────────────────
    def get_event(
        self, start=None, end=None, *, center=None, window_min: float | None = None
    ) -> ObservationData:
        """Recorta um evento (intervalo temporal) do dataset.

        Compatível com a nomenclatura de simulação (transitos/fontes no feixe
        são descritos por intervalos temporais): forneça ``start``/``end`` ou
        ``center`` + ``window_min`` (meia-janela em minutos).

        Parameters
        ----------
        start, end:
            Limites do intervalo (datetime64, ISO str ou Timestamp).
        center:
            Centro do evento (com ``window_min`` = meia-janela em minutos).
        window_min:
            Meia-janela em minutos em torno de ``center``.

        Returns
        -------
        ObservationData
            Slice temporal do dataset (dims reduzidas em ``time``).
        """
        if center is not None and window_min is not None:
            start = pd.Timestamp(center) - pd.Timedelta(minutes=window_min)
            end = pd.Timestamp(center) + pd.Timedelta(minutes=window_min)
        if start is None or end is None:
            msg = "get_event requer start/end ou center + window_min."
            raise ValueError(msg)
        da = self._target().sel(time=slice(start, end))
        return self._like(da)

    # ──────────────────────────────────────────────────────────────
    # to_power_spectrum — temperatura de brilho → potência
    # ──────────────────────────────────────────────────────────────
    def to_power_spectrum(self) -> ObservationData:
        """Converte temperatura de brilho (K) → densidade de potência (W/Hz).

        Usa ``P_nu = k_B * T_A`` (W/Hz), a mesma relação do arquivo de
        simulação (``T_antenna`` em K e ``power`` em W/Hz). Se a variável não
        estiver em Kelvin, retorna uma cópia sem conversão (apenas renomeada).

        Returns
        -------
        ObservationData
            Dados em potência (W/Hz).
        """
        da = self._target()
        units = str(da.attrs.get("units", ""))
        if "K" in units:
            out = (da * K_B).rename("power")
            out.attrs["units"] = "W/Hz"
        else:
            out = da.rename("power")
        return self._like(out, name="power")


# ──────────────────────────────────────────────────────────────────
# Rebin espectral por integração (usado por resample/rebin_frequency)
# ──────────────────────────────────────────────────────────────────
def _rebin_to_grid(da: xr.DataArray, target_freq: np.ndarray, stat: str = "mean") -> xr.DataArray:
    """Agrega (integra) ``da`` nos bins do grid ``target_freq`` (sem interpolação).

    Cada bin alvo recebe a média (``stat="mean"``), soma (``stat="sum"``) ou
    mediana (``stat="median"``) dos canais originais cujo centro cai nele.
    O resultado é reindexado para ``target_freq`` exatamente (bins vazios → NaN).
    """
    f = np.asarray(da["frequency"].values, dtype=float)
    tf = np.asarray(target_freq, dtype=float)

    half = np.diff(tf) / 2.0
    edges = np.concatenate([[tf[0] - half[0]], tf[:-1] + half, [tf[-1] + half[-1]]])
    idx = np.digitize(f, edges) - 1  # bin alvo de cada canal original

    grouped = da.assign_coords(_bin=("frequency", idx)).groupby("_bin")
    if stat == "sum":
        res = grouped.sum("frequency")
    elif stat == "median":
        res = grouped.median("frequency")
    else:
        res = grouped.mean("frequency")

    present = np.asarray(res["_bin"].values)
    valid = (present >= 0) & (present < tf.size)
    res = res.sel(_bin=present[valid])
    res = res.assign_coords(_bin=tf[present[valid]].astype(float))
    res = res.reindex(_bin=tf)  # garante exatamente len(target_freq) bins
    return res.rename(_bin="frequency")


# ──────────────────────────────────────────────────────────────────
# Kernels de baseline (funções de módulo)
# ──────────────────────────────────────────────────────────────────
def _baseline_kernel(
    da: xr.DataArray,
    method: str = "median",
    *,
    window: int = 601,
    polyorder: int = 3,
    sigma_clip: float = 3.0,
) -> xr.DataArray:
    """Deriva a baseline de ``da`` pelo método indicado.

    - ``median``: mediana ao longo do tempo (por canal).
    - ``savitsky_golay``: filtro Savitzky-Golay ao longo do tempo
      (``window``/``polyorder``; o filtro usa a série temporal de cada canal).
    - ``mad``: mediana dos pontos dentro de ``sigma_clip`` MADs em torno da
      mediana (baseline robusta).

    Returns
    -------
    xr.DataArray
        Baseline com as mesmas dims de ``da``.
    """
    m = _norm_method(method)
    if m == "median":
        return da.median("time")
    if m == "savitsky_golay":
        arr = np.asarray(da.values, dtype=float)
        win = max(3, min(int(window), arr.shape[0] - (1 - arr.shape[0] % 2)))
        if win % 2 == 0:
            win -= 1
        win = max(3, win)
        poly = min(polyorder, win - 1)
        filt = sp_signal.savgol_filter(arr, window_length=win, polyorder=poly, axis=0)
        return da.copy(data=filt)
    if m == "mad":
        med = da.median("time")
        mad = np.abs(da - med).median("time")
        mask = np.abs(da - med) <= sigma_clip * mad
        return xr.where(mask, da, med).mean("time")
    msg = f"método de baseline desconhecido: {method!r} (use {_BASELINE_METHODS})"
    raise ValueError(msg)
