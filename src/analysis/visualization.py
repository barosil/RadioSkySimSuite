"""Visualização dos dados de análise — waterfall e séries temporais.

Usa HoloViews + Datashader (rasterize) com zoom/pan linkados entre painéis:

- ``waterfall_plot``      — waterfall (time × frequency) lado a lado, com tira
                            opcional da média/mediana por tempo;
- ``temporal_median_plot``— série temporal da mediana espectral por amostra de
                            tempo, lado a lado (ou sobreposta);
- ``calibration_plot``    — painéis da calibração (a, g, T_sys, R²) por canal.
"""

from __future__ import annotations

import numpy as np

from ._utils import _as_2d, _time_seconds

__all__ = ["calibration_plot", "dt_profile_plot", "temporal_median_plot", "waterfall_plot"]


def waterfall_plot(
    xarray_list,
    titles=None,
    ncols: int = 2,
    cmap: str = "viridis",
    width: int = 550,
    height: int = 350,
    strip_height: int = 140,
    add_mean_line: bool = False,
    strip_stat: str = "mean",
    abs_time: bool = False,
):
    """Plota waterfall (time × frequency) dos xarrays lado a lado.

    Cada painel é um ``hv.QuadMesh`` rasterizado com Datashader (cmap comum,
    barra de cores e zoom/pan linkados entre os painéis — tempo e frequência).
    Cada waterfall tem **colorbar/limites de cor independentes** (``clim`` por
    painel) — importante quando os painéis têm escalas/unidades muito
    diferentes (ex.: simulação em K vs observação em potência, antes de
    calibração).

    Opcionalmente (``add_mean_line=True``), cada painel vira uma pilha vertical
    com uma tira da média do sinal por tempo **acima** do waterfall (elemento
    separado, compartilhando o eixo de tempo).

    O eixo de tempo de cada painel é **relativo ao próprio início (0 h)** por
    padrão (uma simulação/observação de 24 h começa em 0 h). Com
    ``abs_time=True``, o eixo mostra o **tempo absoluto (UTC)** — as séries
    começam onde os dados começam (ex.: sim às 12:00 e obs às 12:12 UTC).

    Parameters
    ----------
    xarray_list:
        Lista de DataArray/Dataset (ou ``ObservationData``) com dims
        ``time × frequency``.
    titles:
        Rótulos por painel (na ordem de ``xarray_list``).
    ncols:
        Nº de painéis por linha.
    cmap:
        Colormap dos waterfalls.
    width / height:
        Largura e altura dos waterfalls.
    strip_height:
        Altura da tira de média (usada quando ``add_mean_line=True``).
    add_mean_line:
        Se ``True``, inclui a tira de média acima de cada waterfall.
    strip_stat:
        Estatística da tira temporal: ``"mean"`` (padrão) ou ``"median"``
        (mediana espectral por tempo).
    abs_time:
        Se ``True``, usa o tempo absoluto (UTC) no eixo temporal; se ``False``
        (padrão), usa horas desde o início de cada dataset.

    Returns
    -------
    holoviews.Layout
        Layout ``.cols(ncols)`` com os waterfalls.
    """
    import holoviews as hv
    from holoviews.operation.datashader import rasterize

    # Garante backend bokeh carregado (idempotente) para aplicar .opts() mesmo
    # quando chamado fora de um notebook que já fez hv.extension("bokeh").
    hv.extension("bokeh")

    # Eixo de tempo: relativo ao PRÓPRIO início (0 h) por padrão; absoluto (UTC)
    # com abs_time=True (sim começa ~12:00, obs ~12:12 — o eixo reflete isso).
    elements: list = []
    for i, x in enumerate(xarray_list):
        if hasattr(x, "_target"):
            x = x._target()  # ObservationData → DataArray
        da = _as_2d(x)
        if abs_time:
            t = np.asarray(da["time"].values).astype("datetime64[ns]")
            time_kdim = "time (UTC)"
        else:
            t = _time_seconds(da) / 3600.0  # horas desde o início
            time_kdim = "time [h]"
        freq = np.asarray(da["frequency"].values, dtype=float)
        z = np.nan_to_num(np.asarray(da.values, dtype=float), nan=0.0)

        # ── Waterfall: cmap comum, mas clim INDEPENDENTE por painel ──
        # (percentis 1–99 para não deixar outliers dominarem a escala de cor).
        vmin, vmax = (float(v) for v in np.percentile(z, (1, 99)))
        if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
            vmin, vmax = float(z.min()), float(z.max())

        img = hv.QuadMesh(
            (t, freq, z.T),
            kdims=[time_kdim, "frequency [MHz]"],
        )
        # Nota: o cmap/clim devem ser definidos via .opts no elemento
        # rasterizado (passar ao rasterize() não é aplicado sem sombreamento).
        img = rasterize(img, dynamic=False).opts(
            cmap=cmap,
            width=width,
            height=height,
            clim=(vmin, vmax),
            colorbar=True,
            tools=["hover"],
        )

        if add_mean_line:
            # ── Tira (média/mediana) ACIMA do waterfall (elemento separado) ──
            if str(strip_stat).lower() == "median":
                mean = np.asarray(da.median("frequency").values, dtype=float)
            else:
                mean = np.asarray(da.mean("frequency").values, dtype=float)
            vdim = str(da.name) if da.name else f"mean_{i}"
            strip = hv.Curve(
                (t, mean),
                kdims=[time_kdim],
                vdims=[vdim],
            ).opts(
                width=width,
                height=strip_height,
                color="black",
                line_width=1.2,
                xlabel=time_kdim,
            )
            if titles and i < len(titles):
                strip = strip.opts(title=str(titles[i]))
            elements.append(strip)
            elements.append(img)  # waterfall abaixo da tira de média
        else:
            if titles and i < len(titles):
                img = img.opts(title=str(titles[i]))
            elements.append(img)

    layout = hv.Layout(elements).cols(ncols)
    # shared_axes linka eixos de mesma dimensão: tempo em todos; frequência
    # entre os waterfalls; a tira de cada painel tem vdim próprio (não linkada).
    layout.opts(shared_axes=True)
    return layout


def temporal_median_plot(
    xarray_list,
    titles=None,
    overlay: bool = False,
    width: int = 550,
    height: int = 300,
    colors=None,
):
    """Série temporal da mediana espectral por amostra de tempo, lado a lado.

    Para cada dataset, reduz o espectro à **mediana sobre a frequência** em cada
    tempo (``ObservationData.temporal_median``) e plota a série no eixo de
    **tempo absoluto (UTC)**. Ajuda a comparar transitos/quiet zone entre
    simulação e observação e a inspecionar o alinhamento temporal (as séries
    sobrepostas devem coincidir após ``align_time``).

    Parameters
    ----------
    xarray_list:
        Lista de ``ObservationData``/DataArray com dims ``time × frequency``.
    titles:
        Rótulos por painel.
    overlay:
        Se ``False`` (padrão), retorna um Layout lado a lado. Se ``True``,
        retorna um ``hv.Overlay`` com todas as séries no mesmo eixo (para
        verificar o alinhamento temporal).
    width / height:
        Tamanho de cada curva.
    colors:
        Cores por série (lista; opcional).

    Returns
    -------
    holoviews.Layout | holoviews.Overlay
    """
    import holoviews as hv

    hv.extension("bokeh")

    curves: list = []
    for i, x in enumerate(xarray_list):
        if hasattr(x, "temporal_median"):
            y = x.temporal_median()
            da = x._target()
        else:
            da = _as_2d(x)
            y = np.asarray(da.median("frequency").values, dtype=float)
        t = np.asarray(da["time"].values)
        if np.issubdtype(t.dtype, np.datetime64):
            t = t.astype("datetime64[ns]")
        vdim = str(da.name) if da.name else f"median_{i}"
        c = hv.Curve((t, y), kdims=["time (UTC)"], vdims=[vdim]).opts(
            width=width,
            height=height,
            line_width=1.5,
            xlabel="time (UTC)",
            ylabel=f"median({vdim})",
        )
        if colors and i < len(colors) and colors[i]:
            c = c.opts(color=colors[i])
        if titles and i < len(titles):
            c = c.opts(title=str(titles[i]))
        curves.append(c)

    if overlay:
        return hv.Overlay(curves).opts(legend_position="top_right")
    return hv.Layout(curves).cols(max(1, len(curves)))


def calibration_plot(cal, width: int = 520, height: int = 300):
    """Painéis da calibração por canal: ``a(ν)``, ``g(ν)``, ``T_sys(ν)``, ``R²``.

    Parameters
    ----------
    cal:
        Dataset retornado por ``fit_calibration``.
    width / height:
        Tamanho de cada painel.

    Returns
    -------
    holoviews.Layout
        Layout 2×2 com as curvas por frequência.
    """
    import holoviews as hv

    hv.extension("bokeh")
    f = np.asarray(cal["frequency"].values, dtype=float)
    specs = (
        ("a", "a(nu) [counts]"),
        ("g", "g(nu) [counts/K]"),
        ("T_sys", "T_sys(nu) [K]"),
        ("r2", "R2(nu)"),
    )
    panels = []
    for var, ylab in specs:
        y = np.asarray(cal[var].values, dtype=float)
        panels.append(
            hv.Curve((f, y), kdims=["frequency [MHz]"], vdims=[ylab]).opts(
                width=width,
                height=height,
                title=var,
                xlabel="frequency [MHz]",
            )
        )
    return hv.Layout(panels).cols(2)


def dt_profile_plot(res, width: int = 550, height: int = 300, title="Perfil SSE vs δt"):
    """Curva do perfil da soma de quadrados dos resíduos vs ``δt``.

    Item 6 (calibração local com três parâmetros): o ``δt`` ótimo é o mínimo
    do perfil ``SSE(δt)`` da varredura de ``fit_calibration_dt``. A linha
    tracejada marca o ``δt`` vencedor (em minutos).

    Parameters
    ----------
    res:
        Dict retornado por ``fit_calibration_dt`` (chaves ``dt_grid_s``/``ss``
        quando ``return_profile=True``, e ``dt_best_s``).
    width / height:
        Tamanho do painel.

    Returns
    -------
    holoviews.Overlay
        Curva do perfil + linha vertical no ``δt`` ótimo.
    """
    import holoviews as hv

    hv.extension("bokeh")
    dt_min = np.asarray(res["dt_grid_s"]) / 60.0
    ss = np.asarray(res["ss"], dtype=float)
    best_min = float(res["dt_best_s"]) / 60.0
    curve = hv.Curve((dt_min, ss), kdims=["δt [min]"], vdims=["SSE"]).opts(
        width=width,
        height=height,
        title=title,
        tools=["hover"],
    )
    vline = hv.VLine(best_min).opts(color="red", line_dash="dashed")
    return curve * vline
