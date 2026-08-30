"""
Módulo: src/radioskysims/visualization/waterfall.py

Visualizador Waterfall (tempo × frequência × T_antenna) usando
HoloViews + Datashader para renderização eficiente de grandes volumes
de dados.

Inclui suporte a eventos (``SimulationEvents``): overlay de retângulos
translúcidos no eixo do tempo com tooltip do objeto em trânsito e
concatenação de datasets de eventos (intervalos ausentes preenchidos
com 0).

Copyright BINGO Collaboration
Last modified: 2026-08-04
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import numpy as np
import xarray as xr

if TYPE_CHECKING:
    from radioskysims_core.domain.common import TimeRange

# Ferramentas Bokeh: zoom/pano POR EIXO (x/y), sem zoom global (box_zoom/wheel_zoom).
_AXIS_TOOLS = [
    "hover",
    "xpan",
    "ypan",
    "xwheel_zoom",
    "ywheel_zoom",
    "xzoom_in",
    "xzoom_out",
    "yzoom_in",
    "yzoom_out",
    "reset",
]


def _check_holoviews_available() -> None:
    """Verifica se HoloViews e Datashader estão instalados."""
    missing = []
    try:
        import holoviews as hv  # noqa: F401
    except ImportError:
        missing.append("holoviews")
    try:
        import datashader as ds  # noqa: F401
    except ImportError:
        missing.append("datashader")
    if missing:
        msg = (
            f"Pacotes necessários não encontrados: {', '.join(missing)}. "
            "Instale com: pip install holoviews datashader"
        )
        raise ImportError(msg)


def _clock_base_hours(t0: Any, time_mode: str = "UTC") -> float:
    """Fração da hora do dia (0–24) de ``t0`` na referência UTC ou local.

    ``t0`` é tipicamente ``time_vals[0]`` (datetime64). O eixo temporal passa a
    exibir a HORA DO DIA real — alternar UTC/Local desloca o eixo pelo offset
    do fuso, implementando uma mudança efetiva no eixo.
    """
    dt = datetime.fromisoformat(str(t0).replace(" ", "T"))
    if time_mode.lower() == "local":
        try:
            import zoneinfo

            dt = dt.astimezone(zoneinfo.ZoneInfo())
        except Exception:
            pass
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.hour + dt.minute / 60.0 + dt.second / 3600.0


def _seconds_to_axis(seconds: np.ndarray | float, time_unit: str, clock_base: float) -> Any:
    """Converte segundos desde o início para o valor do eixo (hora do dia)."""
    if time_unit == "hours":
        return seconds / 3600.0 + clock_base
    if time_unit == "minutes":
        return seconds / 60.0 + clock_base * 60.0
    return seconds + clock_base * 3600.0


def _time_axis_label(time_unit: str, time_mode: str = "UTC") -> str:
    """Rótulo do eixo temporal (hora do dia na referência UTC ou local)."""
    unit_label = {"hours": "h", "minutes": "min"}.get(time_unit, "s")
    ref = "local" if time_mode.lower() == "local" else "UTC"
    return f"Hora do dia [{unit_label}] ({ref})"


def _time_label(t0: Any, time_unit: str, time_mode: str = "UTC") -> str:
    """Rótulo do eixo temporal com referência UTC ou local.

    Mantido por compatibilidade: descreve a hora do dia na referência escolhida.
    """
    _ = t0  # mantido por compatibilidade (ignorado)
    return _time_axis_label(time_unit, time_mode)


def _reindex_events_to_grid(
    dataset: xr.Dataset,
    time_range: TimeRange,
) -> xr.Dataset:
    """Reindexa um dataset de eventos (tempo esparso) para o grid completo.

    Preenche os intervalos temporais ausentes com 0 (T_antenna e power),
    produzindo um waterfall contínuo a partir de um dataset de eventos.
    """
    T = dataset.get("T_antenna")
    if T is None or "time" not in T.coords:
        return dataset
    time_vals = T.coords["time"].values
    if not np.issubdtype(time_vals.dtype, np.datetime64):
        return dataset

    if np.issubdtype(time_vals.dtype, np.datetime64):
        full = time_range.to_datetime64()
    else:
        from astropy.time import Time as AstroTime

        t0 = np.datetime64(AstroTime(time_range.start_jd, format="jd").datetime64, "ns")
        t1 = np.datetime64(AstroTime(time_range.end_jd, format="jd").datetime64, "ns")
        step_ns = int(round(time_range.resolution_sec * 1e9))
        n = int(round(float((t1 - t0) / np.timedelta64(step_ns, "ns")))) + 1
        full = t0 + np.arange(n) * np.timedelta64(step_ns, "ns")

    # Já cobre o grid completo? Evita reindex desnecessário em datasets full.
    if np.isin(full, time_vals).all():
        return dataset

    # Reindexa todo o dataset (Dataset.reindex) para que a coordenada ``time``
    # seja substituída pelo grid completo — atribuir apenas o array realinharia
    # de volta à coordenada esparsa existente.
    return dataset.reindex(time=full, fill_value=0.0)


def events_spans(
    events: Any,
    time_range: TimeRange | None = None,
    time_unit: str = "hours",
    time_mode: str = "UTC",
) -> list[dict[str, Any]]:
    """Deriva spans por EVENTO (fonte × janela contígua), não global.

    Para cada fonte ativa (T_antenna > 0) produz um span ``{start, end,
    label}`` por intervalo contíguo em que ela está no feixe. Fontes
    sobrepostas geram retângulos SEPARADOS (translúcidos), cada um com seu
    próprio início/fim — em vez de um único retângulo global "A + B".

    Parameters
    ----------
    events:
        ``SimulationEvents`` (ou dataset com ``beam_events``).
    time_range:
        Se fornecido, reindexa os eventos ao grid completo, garantindo
        que lacunas entre eventos apareçam como spans separados.
    time_unit:
        Unidade do eixo temporal.
    time_mode:
        ``"UTC"`` ou ``"local"`` — referência do eixo (hora do dia).

    Returns
    -------
    list[dict]
        ``[{"start": float, "end": float, "label": str}, ...]``
    """
    beam_events = getattr(events, "beam_events", None)
    if beam_events is None:
        return []

    ds = beam_events
    if "T_antenna" not in ds or "time" not in ds.coords:
        return []
    if "source" not in ds.dims:
        return []

    # Grid completo para detectar lacunas entre eventos
    if time_range is not None:
        ds = _reindex_events_to_grid(ds, time_range)

    T = ds["T_antenna"]
    try:
        per_source = T.max(dim=["frequency", "polarization", "pointing"], skipna=True) > 0.0
    except Exception:
        per_source = T > 0.0
    if per_source.ndim == 1:
        per_source = per_source.expand_dims(source=[str(ds.coords["source"].values[0])])
    active = np.asarray(per_source.values, dtype=bool)  # (time, source)

    time_vals = ds.coords["time"].values
    t0 = time_vals[0]
    if np.issubdtype(time_vals.dtype, np.datetime64):
        secs = (time_vals - t0).astype("timedelta64[ns]").astype(float) / 1e9
    elif np.issubdtype(time_vals.dtype, np.floating):
        secs = (time_vals - time_vals[0]) * 86400.0
    else:
        secs = np.arange(len(time_vals), dtype=float)

    clock_base = _clock_base_hours(t0, time_mode)
    src_names = [str(s) for s in ds.coords["source"].values]

    spans: list[dict[str, Any]] = []
    for j in range(active.shape[1]):
        col = active[:, j]
        start_i: int | None = None
        for i, on in enumerate(col):
            if on and start_i is None:
                start_i = i
            elif not on and start_i is not None:
                spans.append(
                    {
                        "start": _seconds_to_axis(secs[start_i], time_unit, clock_base),
                        "end": _seconds_to_axis(secs[i], time_unit, clock_base),
                        "label": src_names[j],
                    }
                )
                start_i = None
        if start_i is not None:
            spans.append(
                {
                    "start": _seconds_to_axis(secs[start_i], time_unit, clock_base),
                    "end": _seconds_to_axis(secs[-1], time_unit, clock_base),
                    "label": src_names[j],
                }
            )
    return spans


def events_overlay(
    spans: list[dict[str, Any]],
    y_range: tuple[float, float] = (0.0, 1.0),
) -> Any:
    """Retorna overlay de retângulos translúcidos para os eventos.

    Cada retângulo cobre o intervalo ``[start, end]`` no eixo do tempo e
    toda a extensão ``y_range``, com tooltip indicando o objeto em trânsito.

    Parameters
    ----------
    spans:
        Saída de :func:`events_spans`.
    y_range:
        Extensão vertical dos retângulos (ex.: faixa de frequência).

    Returns
    -------
    holoviews.Overlay | None
        Overlay de ``hv.Rectangles`` ou ``None`` se não houver spans.
    """
    if not spans:
        return None

    import holoviews as hv

    hv.extension("bokeh")

    y0, y1 = y_range
    data = [(sp["start"], y0, sp["end"], y1, sp["label"]) for sp in spans]
    rects = hv.Rectangles(data, vdims=["label"]).opts(
        fill_color="cyan",
        fill_alpha=0.0,
        line_color="cyan",
        line_alpha=0.7,
        line_width=1.5,
        hover_fill_color="cyan",
        hover_fill_alpha=0.2,
        tools=_AXIS_TOOLS,
    )
    return rects


def waterfall_plot(
    dataset: xr.Dataset,
    *,
    source_name: str | None = None,
    source_type: str | list[str] | None = None,
    polarization: str | None = None,
    pointing: int = 0,
    time_unit: str = "hours",
    freq_unit: str = "MHz",
    title: str | None = None,
    width: int = 900,
    height: int = 400,
    cmap: str = "inferno",
    log_color: bool = False,
    use_datashader: bool = True,
    clim: tuple[float | None, float | None] | None = None,
    time_range: TimeRange | None = None,
    events: Any | None = None,
    fill_missing: bool = False,
    time_mode: str = "UTC",
    ylim: tuple[float, float] | None = None,
    show_title: bool = True,
) -> Any:
    """Gera um gráfico waterfall (tempo × frequência × T_antenna).

    Parameters
    ----------
    dataset:
        Dataset com T_antenna e coordenadas time, frequency, source.
    source_name:
        Nome da fonte a visualizar. Se ``None``, soma todas as fontes.
    source_type:
        Tipo(s) de fonte a filtrar (ex.: ``"satellite"``, ``"localsource"``,
        ``"radiosource"``) — aceita uma string ou uma lista de tipos
        (que são somados). Se ``None``, usa todas.
    polarization:
        Polarização a visualizar. Se ``None``, usa a primeira.
    pointing:
        Índice do pointing.
    time_unit:
        Unidade temporal: ``"hours"``, ``"minutes"``, ``"seconds"``.
    freq_unit:
        Unidade de frequência: ``"MHz"``, ``"GHz"``, ``"Hz"``.
    title:
        Título do gráfico. Se ``None``, gera automaticamente.
    width:
        Largura do gráfico em pixels.
    height:
        Altura do gráfico em pixels.
    cmap:
        Mapa de cores matplotlib.
    log_color:
        Se ``True``, usa escala logarítmica para a cor.
    use_datashader:
        Se ``True``, usa Datashader para rasterização (recomendado para
        datasets grandes). Se ``False``, usa rasterização nativa do
        HoloViews (mais rápido para datasets pequenos).
    clim:
        Limites de cor (vmin, vmax). Se ``None``, calcula automaticamente.
    time_range:
        Se fornecido, fatia o dataset apenas para este intervalo temporal
        antes de processar, evitando computar dados fora da janela.
    events:
        ``SimulationEvents`` (ou dataset de eventos). Se fornecido, o
        waterfall usa ``beam_events`` (concatenação dos eventos).
    fill_missing:
        Se ``True`` (e ``time_range`` fornecido), reindexa o dataset para o
        grid temporal completo, preenchendo os intervalos ausentes com 0
        (comportamento para datasets de eventos com tempo esparso).
    time_mode:
        ``"UTC"`` ou ``"local"`` — controla o rótulo do eixo temporal
        (tempo de referência exibido).
    ylim:
        Limites do eixo de frequência ``(y_min, y_max)``. Se ``None``,
        usa o padrão ``(0.8 * f_min, 1.2 * f_max)``.
    show_title:
        Se ``False``, remove o título (útil ao empilhar com a série
        temporal com eixos x compartilhados).

    Returns
    -------
    holoviews.Layout or holoviews.Image
        Objeto HoloViews para exibição no notebook.
    """
    _check_holoviews_available()

    import datashader as ds
    import holoviews as hv
    import holoviews.operation.datashader as hd

    hv.extension("bokeh")

    # ── Usa beam_events se events foi fornecido ──────────────
    if events is not None:
        be = getattr(events, "beam_events", None)
        if be is not None:
            dataset = be

    # ── Reindexa eventos para o grid completo (preenche com 0) ──
    if fill_missing and time_range is not None:
        dataset = _reindex_events_to_grid(dataset, time_range)

    # ── Fatia o dataset pelo time_range se fornecido ──────────
    if time_range is not None:
        # Converte time_range (JD) para datetime64 para isel
        t_start = time_range.start_jd
        t_end = time_range.end_jd
        time_coord = dataset.coords["time"].values
        if np.issubdtype(time_coord.dtype, np.datetime64):
            from astropy.time import Time as AstroTime

            t_start_dt = AstroTime(t_start, format="jd").datetime64
            t_end_dt = AstroTime(t_end, format="jd").datetime64
            dataset = dataset.sel(time=slice(t_start_dt, t_end_dt))
        else:
            # Coordenada em JD — slice direto
            dataset = dataset.sel(time=slice(t_start, t_end))

    T = dataset["T_antenna"]

    # ── Seleciona fonte ────────────────────────────────────────
    if source_name is not None:
        T_src = T.sel(source=source_name, method=None)
    elif source_type is not None and "source_type" in dataset.coords:
        if isinstance(source_type, str):
            source_types = [source_type]
        else:
            source_types = list(source_type)
        mask = dataset.coords["source_type"].isin(source_types).values
        src_names = dataset.coords["source"].values[mask]
        if len(src_names) == 0:
            msg = f"Nenhuma fonte dos tipos {source_types} encontrada."
            raise ValueError(msg)
        T_src = T.sel(source=list(src_names)).sum(dim="source")
    else:
        T_src = T.sum(dim="source")

    # ── Polarização ────────────────────────────────────────────
    if polarization is not None and "polarization" in T_src.dims:
        T_src = T_src.sel(polarization=polarization, method=None)
    elif "polarization" in T_src.dims:
        T_src = T_src.isel(polarization=0)

    # ── Pointing ───────────────────────────────────────────────
    if "pointing" in T_src.dims:
        T_src = T_src.isel(pointing=pointing)

    # ── Converte tempo ─────────────────────────────────────────
    time_vals = T_src.coords["time"].values
    if np.issubdtype(time_vals.dtype, np.datetime64):
        t0 = time_vals[0]
        # Arredonda para o segundo mais próximo: a conversão JD → datetime64[ns]
        # no pipeline do TOD pode gerar degraus de 599 s (truncamento), deixando
        # o grid irregular e disparando o warning "Image dimension time is not
        # evenly sampled" no HoloViews/Datashader.
        time_seconds = np.round((time_vals - t0).astype("timedelta64[ns]").astype(float) / 1e9)
    elif np.issubdtype(time_vals.dtype, np.floating):
        # JD → horas desde o primeiro ponto
        time_seconds = (time_vals - time_vals[0]) * 86400.0
    else:
        time_seconds = np.arange(len(time_vals), dtype=float)

    if time_unit == "hours" or time_unit == "minutes":
        clock_base = _clock_base_hours(time_vals[0], time_mode)
        time_data = _seconds_to_axis(time_seconds, time_unit, clock_base)
        time_label = _time_axis_label(time_unit, time_mode)
    else:
        clock_base = _clock_base_hours(time_vals[0], time_mode)
        time_data = _seconds_to_axis(time_seconds, time_unit, clock_base)
        time_label = _time_axis_label(time_unit, time_mode)

    # ── Converte frequência ────────────────────────────────────
    freq_vals = T_src.coords["frequency"].values
    if freq_unit == "GHz":
        freq_data = freq_vals / 1e9
    elif freq_unit == "MHz":
        freq_data = freq_vals / 1e6
    else:
        freq_data = freq_vals

    freq_label = f"Frequência [{freq_unit}]"

    # ── Range padrão do eixo de frequência ───────────────────
    # Padrão: 0.8 * freq_minima até 1.2 * freq_maxima.
    if ylim is None and freq_data.size:
        _fmin = float(np.nanmin(freq_data))
        _fmax = float(np.nanmax(freq_data))
        ylim = (0.8 * _fmin, 1.2 * _fmax)

    # ── Prepara dados 2D ──────────────────────────────────────
    T_vals = T_src.values  # (time, frequency)

    if log_color:
        T_plot = np.log10(np.maximum(T_vals, 1e-30))
    else:
        T_plot = T_vals

    # ── Amostragem se o grid for muito grande (> 1M pontos) ──
    n_time, n_freq = T_plot.shape
    total_points = n_time * n_freq

    if total_points > 5_000_000 and use_datashader:
        max_points = 2_000_000
        step = max(1, int(np.sqrt(total_points / max_points)))
        T_plot = T_plot[::step, ::step]
        time_data = time_data[::step]
        freq_data = freq_data[::step]

    # ── Constrói gráfico ──────────────────────────────────────
    if use_datashader:
        # hv.Image + hd.rasterize: trata dados como grid regular,
        # evitando listras brancas do hv.Points + hd.datashade.
        #
        # IMPORTANTE: construir o Image a partir de uma DataArray NOMEADA.
        # Com datashader>=0.19 / holoviews>=1.19, o `rasterize`/`regrid`
        # reconstrói a DataArray internamente e valida que `name` == coluna
        # da redução (`mean('T_antenna')`). Um Image criado de tupla produz
        # uma DataArray sem nome → `ValueError: DataArray name None does not
        # match supplied reduction mean('T_antenna')`.
        data_array = xr.DataArray(
            T_plot.T,
            dims=["frequency", "time"],
            coords={
                "time": ("time", time_data),
                "frequency": ("frequency", freq_data),
            },
            name="T_antenna",
        ).rename({"time": time_label})
        img = hv.Image(
            data_array,
            kdims=[time_label, "frequency"],
            vdims=["T_antenna"],
        )
        img = hd.rasterize(img, aggregator=ds.reductions.mean("T_antenna")).opts(
            cmap=cmap,
            colorbar=True,
            width=width,
            height=height,
            xlabel=time_label,
            ylabel=freq_label,
            title=(title or "Waterfall TOD") if show_title else "",
            ylim=ylim,
            tools=_AXIS_TOOLS,
            clim=clim if clim else (None, None),
        )
    else:
        img = hv.Image(
            (time_data, freq_data, T_plot.T),
            [time_label, "frequency"],
            "T_antenna",
        ).opts(
            cmap=cmap,
            colorbar=True,
            width=width,
            height=height,
            xlabel=time_label,
            ylabel=freq_label,
            title=(title or "Waterfall TOD") if show_title else "",
            ylim=ylim,
            tools=_AXIS_TOOLS,
            clim=clim if clim else (None, None),
        )

    # ── Overlay de eventos (retângulos translúcidos com tooltip) ──
    if events is not None:
        spans = events_spans(
            events,
            time_range=time_range,
            time_unit=time_unit,
            time_mode=time_mode,
        )
        if spans:
            if freq_data.size:
                min_freq = float(np.nanmin(freq_data))
                max_freq = float(np.nanmax(freq_data))
                freq_height = (max_freq - min_freq) / 10.0 if max_freq > min_freq else 1.0
                y_range = (min_freq - freq_height, min_freq)
            else:
                y_range = (0.0, 0.1)
            overlay = events_overlay(spans, y_range=y_range)
            if overlay is not None:
                return img * overlay

    return img


def available_source_types(dataset: xr.Dataset) -> list[str]:
    """Lista ordenada dos tipos de fonte presentes no dataset.

    Parameters
    ----------
    dataset:
        Dataset com a coordenada ``source_type``.

    Returns
    -------
    list[str]
        Tipos ordenados (ex.: ``["localsource", "radiosource", "satellite"]``).
        Se o dataset não tiver ``source_type``, retorna ``["all"]``.
    """
    if "source_type" not in dataset.coords:
        return ["all"]
    values = dataset.coords["source_type"].values
    if hasattr(values, "compute"):  # dask
        values = values.compute()
    return sorted(str(t) for t in np.unique(values))


def interactive_waterfall(
    dataset: xr.Dataset,
    *,
    time_range: TimeRange | None = None,
    title: str = "Waterfall TOD",
    width: int = 900,
    height: int = 350,
    cmap: str = "inferno",
    use_datashader: bool = True,
    **kwargs: Any,
) -> Any:
    """Waterfall interativo com seleção múltipla de ``source_type``.

    Constrói um layout Panel com um ``CheckboxGroup`` (seleção múltipla dos
    tipos de fonte) e o waterfall que se atualiza conforme a seleção.

    Parameters
    ----------
    dataset:
        Dataset com ``T_antenna`` e a coordenada ``source_type``.
    time_range:
        Se fornecido, fatia o dataset para este intervalo temporal.
    title:
        Título base do gráfico.
    width, height:
        Dimensões do gráfico em pixels.
    cmap:
        Mapa de cores.
    use_datashader:
        Se ``True``, usa Datashader para rasterização.
    **kwargs:
        Repassados para ``waterfall_plot``.

    Returns
    -------
    panel.Column
        Layout com a caixa de seleção e o gráfico dinâmico.
    """
    _check_holoviews_available()

    import holoviews as hv
    import panel as pn

    pn.extension()

    types = available_source_types(dataset)
    selector = pn.widgets.CheckBoxGroup(
        name="Tipos de fonte",
        options=types,
        value=list(types),
        inline=False,
    )

    def _make_plot(selection: list[str] | None) -> Any:
        selection = list(selection or [])
        if not selection:
            return pn.pane.Markdown("⚠️ Selecione ao menos um tipo de fonte.")
        # Sem coordenada source_type → mostra todas as fontes
        source_type: str | list[str] | None = None if types == ["all"] else selection
        plot = waterfall_plot(
            dataset,
            source_type=source_type,
            title=f"{title} — {' + '.join(selection)}",
            width=width,
            height=height,
            cmap=cmap,
            use_datashader=use_datashader,
            time_range=time_range,
            **kwargs,
        )
        # Com datashader, waterfall_plot retorna um hv.DynamicMap (operação
        # rasterize). DynamicMaps dentro de widgets Panel não são avaliados no
        # render estático de notebooks VS Code, deixando o gráfico vazio.
        # Avaliamos aqui para um elemento estático (hv.Image), que renderiza
        # de forma confiável no notebook.
        if isinstance(plot, hv.DynamicMap):
            try:
                plot = plot[()]
            except Exception:
                if plot.data:
                    plot = list(plot.data.values())[0]
        return plot

    plot_pane = pn.bind(_make_plot, selection=selector)
    return pn.Column(
        pn.pane.Markdown(f"### {title}"),
        selector,
        plot_pane,
    )


def tod_panel(
    dataset: xr.Dataset,
    *,
    events: Any | None = None,
    time_range: TimeRange | None = None,
    title: str = "Waterfall TOD",
    width: int = 900,
    height: int = 350,
    cmap: str = "inferno",
    use_datashader: bool = True,
    **kwargs: Any,
) -> Any:
    """Painel interativo de TOD com seletores no topo.

    Layout (Panel):
      - Seletores no topo: Antenna (pointing), Polarização, Tempo (UTC/Local)
        e switch "Mostrar eventos".
      - Seleção múltipla de ``source_type``.
      - Waterfall (tempo × frequência) com overlay de eventos (retângulos
        translúcidos com tooltip do objeto em trânsito).
      - Painel com T_antenna integrado em frequência.

    Parameters
    ----------
    dataset:
        Dataset com ``T_antenna``.
    events:
        ``SimulationEvents`` opcional — habilita o switch de eventos e o
        overlay/concateção com intervalos ausentes preenchidos com 0.
    time_range:
        Se fornecido, fatia o dataset e reindexa eventos ao grid completo.
    title, width, height, cmap, use_datashader:
        Opções de plotagem (repassadas ao ``waterfall_plot``).

    Returns
    -------
    panel.Column
        Layout com controles e gráficos (servir via ``serve_tod_panel``).
    """
    _check_holoviews_available()

    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")
    pn.extension()

    T = dataset["T_antenna"]
    pointing_opts = list(range(T.sizes.get("pointing", 1)))
    pol_vals = list(T.polarization.values) if "polarization" in T.dims else ["UNDEFINED"]
    types = available_source_types(dataset)

    pointing_sel = pn.widgets.Select(
        name="Antenna (pointing)",
        options={f"antenna {i}": i for i in pointing_opts},
        value=0,
    )
    pol_sel = pn.widgets.Select(
        name="Polarização",
        options={str(p): p for p in pol_vals},
        value=pol_vals[0],
    )
    type_sel = pn.widgets.CheckBoxGroup(
        name="Tipos de fonte",
        options=types,
        value=list(types),
        inline=False,
    )
    time_mode = pn.widgets.RadioButtonGroup(
        name="Tempo",
        options=["UTC", "Local"],
        value="UTC",
        button_type="primary",
    )
    show_events = pn.widgets.Switch(
        name="Mostrar eventos",
        value=events is not None,
    )
    if events is None:
        show_events.disabled = True

    # ── Controle dos limites da colorbar do waterfall ─────────
    clim_auto = pn.widgets.Switch(name="Colorbar automática", value=True)
    clim_min = pn.widgets.FloatInput(name="Colorbar min", value=0.0)
    clim_max = pn.widgets.FloatInput(name="Colorbar max", value=1.0)

    def _toggle_clim(enabled: bool) -> None:
        clim_min.disabled = not enabled
        clim_max.disabled = not enabled

    clim_auto.param.watch(lambda e: _toggle_clim(e.new), "value")
    _toggle_clim(clim_auto.value)

    def _make_plot(
        pnt: int,
        pol: str,
        selection: list[str] | None,
        tmode: str,
        ev: bool,
        clim_on: bool,
        cmin: float,
        cmax: float,
    ) -> Any:
        selection = list(selection or [])
        if not selection:
            return pn.pane.Markdown("⚠️ Selecione ao menos um tipo de fonte.")
        st: str | list[str] | None = None if types == ["all"] else selection
        clim = None if clim_on else (cmin, cmax)

        # Waterfall: quando habilitado no switch, exibe também os eventos
        # (retângulos + reindexação do dataset de eventos).
        wf = waterfall_plot(
            dataset,
            source_type=st,
            polarization=pol,
            pointing=pnt,
            show_title=False,
            width=width,
            height=height,
            cmap=cmap,
            use_datashader=use_datashader,
            time_range=time_range,
            events=events if ev else None,
            fill_missing=True,
            time_mode=tmode,
            clim=clim,
            **kwargs,
        )
        # Série temporal: recebe os eventos (retângulos + reindexação).
        ts = time_series_plot(
            dataset,
            source_type=st,
            polarization=pol,
            pointing=pnt,
            width=width,
            height=160,
            time_range=time_range,
            time_mode=tmode,
            events=events if ev else None,
            fill_missing=True,
            show_title=False,
            show_xlabel=False,
        )
        # Mantém o DynamicMap: o Datashader re-rasteriza no zoom preservando a
        # resolução (NÃO colapsar para elemento estático — o painel roda via
        # pn.serve no navegador, onde o DynamicMap atualiza no zoom/pan).
        # Série temporal ACIMA do waterfall, com eixos x compartilhados
        # (sem rótulo de x na série e sem título no waterfall → eixos colados).
        try:
            layout = hv.Layout([ts, wf]).opts(shared_axes=True, merge_tools=False).cols(1)
        except Exception:
            layout = pn.Column(ts, wf)
        return pn.Column(layout)

    plot_pane = pn.bind(
        _make_plot,
        pnt=pointing_sel,
        pol=pol_sel,
        selection=type_sel,
        tmode=time_mode,
        ev=show_events,
        clim_on=clim_auto,
        cmin=clim_min,
        cmax=clim_max,
    )

    controls = pn.Row(pointing_sel, pol_sel, time_mode, show_events)
    color_controls = pn.Row(clim_auto, clim_min, clim_max)
    return pn.Column(
        pn.pane.Markdown(f"### {title}"),
        controls,
        type_sel,
        color_controls,
        plot_pane,
    )


def _port_free(prt: int) -> bool:
    """Retorna True se a porta está livre para bind."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", prt)) != 0


def _serve_app(
    app: Any,
    *,
    port: int,
    title: str,
    open_browser: bool = False,
) -> tuple[str, Any]:
    """Sobe um app Panel via ``pn.serve`` em thread, gerenciando a porta."""
    import time

    import panel as pn

    pn.extension()

    # Encerra servidor anterior na mesma porta (shutdown do Bokeh é assíncrono)
    prev = _ACTIVE_SERVERS.get(port)
    if prev is not None:
        try:
            prev.stop()
        except Exception:
            pass
        for _ in range(25):  # até ~5s
            if _port_free(port):
                break
            time.sleep(0.2)

    server = pn.serve(
        app,
        port=port,
        show=open_browser,
        threaded=True,
        title=title,
    )
    _ACTIVE_SERVERS[port] = server
    return f"http://localhost:{port}", server


def serve_tod_panel(
    dataset: xr.Dataset,
    *,
    events: Any | None = None,
    port: int = 5007,
    open_browser: bool = False,
    title: str = "Waterfall TOD interativo",
    **kwargs: Any,
) -> tuple[str, Any]:
    """Serve o painel interativo TOD via ``pn.serve`` (funciona no navegador).

    Contorna a limitação de render de widgets Panel no notebook VS Code: o app
    roda num servidor Bokeh em thread; abra a URL retornada no navegador.

    Parameters
    ----------
    dataset:
        Dataset com ``T_antenna``.
    events:
        ``SimulationEvents`` opcional (habilita overlay de eventos).
    port:
        Porta do servidor (padrão 5007).
    open_browser:
        Se ``True``, abre o navegador automaticamente.
    title:
        Título do app.
    **kwargs:
        Repassados para ``tod_panel``.

    Returns
    -------
    tuple[str, Any]
        (url, server).
    """
    _check_holoviews_available()

    app = tod_panel(dataset, events=events, **kwargs)
    url, server = _serve_app(
        app,
        port=port,
        title=title,
        open_browser=open_browser,
    )
    print(f"🌐 Waterfall TOD interativo em: {url}   (para encerrar: stop_waterfall_servers())")
    return url, server


def multi_source_waterfall(
    dataset: xr.Dataset,
    *,
    source_types: list[str] | None = None,
    time_range: TimeRange | None = None,
    **kwargs: Any,
) -> Any:
    """Gera múltiplos waterfalls, um por tipo de fonte.

    Parameters
    ----------
    dataset:
        Dataset com T_antenna.
    source_types:
        Lista de tipos de fonte. Se ``None``, usa todos os tipos
        disponíveis em ``source_type``.
    **kwargs:
        Repassados para ``waterfall_plot``.

    Returns
    -------
    holoviews.Layout
        Layout com um subplot por tipo de fonte.
    """
    _check_holoviews_available()

    import holoviews as hv

    hv.extension("bokeh")

    if source_types is None and "source_type" in dataset.coords:
        source_types = list(set(dataset.coords["source_type"].values))
    elif source_types is None:
        source_types = ["all"]

    plots = []
    for stype in source_types:
        if stype == "all":
            title = kwargs.pop("title", "Waterfall — Todas as fontes")
            p = waterfall_plot(
                dataset, source_type=None, title=title, time_range=time_range, **kwargs
            )
        else:
            title = kwargs.pop("title", f"Waterfall — {stype}")
            p = waterfall_plot(
                dataset, source_type=stype, title=title, time_range=time_range, **kwargs
            )
        plots.append(p)

    return hv.Layout(plots).cols(1)


def time_series_plot(
    dataset: xr.Dataset,
    *,
    source_name: str | None = None,
    source_type: str | list[str] | None = None,
    polarization: str | None = None,
    pointing: int = 0,
    integrate_freq: bool = True,
    time_unit: str = "hours",
    title: str | None = None,
    show_title: bool = True,
    width: int = 900,
    height: int = 300,
    time_range: TimeRange | None = None,
    time_mode: str = "UTC",
    events: Any | None = None,
    fill_missing: bool = False,
    ylim: tuple[float, float] | None = None,
    show_xlabel: bool = True,
) -> Any:
    """Gera série temporal de T_antenna.

    Parameters
    ----------
    dataset:
        Dataset com T_antenna.
    source_name:
        Nome da fonte. Se None, soma todas.
    source_type:
        Filtro por tipo de fonte.
    polarization:
        Polarização.
    pointing:
        Índice do pointing.
    integrate_freq:
        Se True, integra (média) sobre a dimensão de frequência.
    time_unit:
        Unidade temporal.
    title:
        Título.
    width, height:
        Dimensões do gráfico.
    time_range:
        Se fornecido, fatia o dataset para este intervalo.
    time_mode:
        ``"UTC"`` ou ``"local"`` — referência exibida no eixo temporal.
    events:
        ``SimulationEvents`` — usado para reindexar (fill_missing) e para
        overlay de eventos na série.
    fill_missing:
        Se ``True`` (e ``time_range``), preenche intervalos ausentes com 0.
    ylim:
        Limites do eixo y ``(T_min, T_max)``. Se ``None``, usa o padrão
        ``(0.9 * T_min, 1.1 * T_max)``.
    show_xlabel:
        Se ``False``, remove o rótulo do eixo x (para empilhar com o
        waterfall com eixos x compartilhados).

    Returns
    -------
    holoviews.Curve or holoviews.Overlay
    """
    _check_holoviews_available()

    import holoviews as hv

    hv.extension("bokeh")

    if events is not None:
        be = getattr(events, "beam_events", None)
        if be is not None:
            dataset = be

    if fill_missing and time_range is not None:
        dataset = _reindex_events_to_grid(dataset, time_range)

    # ── Fatia o dataset pelo time_range se fornecido ──────────
    if time_range is not None:
        t_start = time_range.start_jd
        t_end = time_range.end_jd
        time_coord = dataset.coords["time"].values
        if np.issubdtype(time_coord.dtype, np.datetime64):
            from astropy.time import Time as AstroTime

            t_start_dt = AstroTime(t_start, format="jd").datetime64
            t_end_dt = AstroTime(t_end, format="jd").datetime64
            dataset = dataset.sel(time=slice(t_start_dt, t_end_dt))
        else:
            dataset = dataset.sel(time=slice(t_start, t_end))

    T = dataset["T_antenna"]

    # Seleciona fontes
    if source_name is not None:
        T_src = T.sel(source=source_name, method=None)
    elif source_type is not None and "source_type" in dataset.coords:
        if isinstance(source_type, str):
            source_types = [source_type]
        else:
            source_types = list(source_type)
        mask = dataset.coords["source_type"].isin(source_types).values
        src_names = dataset.coords["source"].values[mask]
        if len(src_names) == 0:
            msg = f"Nenhuma fonte dos tipos {source_types} encontrada."
            raise ValueError(msg)
        T_src = T.sel(source=list(src_names)).sum(dim="source")
    else:
        T_src = T.sum(dim="source")

    # Polarização e pointing
    if polarization is not None and "polarization" in T_src.dims:
        T_src = T_src.sel(polarization=polarization, method=None)
    elif "polarization" in T_src.dims:
        T_src = T_src.isel(polarization=0)

    if "pointing" in T_src.dims:
        T_src = T_src.isel(pointing=pointing)

    # Integra em frequência
    if integrate_freq and "frequency" in T_src.dims:
        T_series = T_src.mean(dim="frequency")
    else:
        T_series = T_src

    # Converte tempo
    time_vals = T_series.coords["time"].values
    if np.issubdtype(time_vals.dtype, np.datetime64):
        t0 = time_vals[0]
        # Arredonda para o segundo mais próximo (evita grid irregular
        # por truncamento JD → datetime64[ns]).
        time_seconds = np.round((time_vals - t0).astype("timedelta64[ns]").astype(float) / 1e9)
    elif np.issubdtype(time_vals.dtype, np.floating):
        time_seconds = (time_vals - time_vals[0]) * 86400.0
    else:
        time_seconds = np.arange(len(time_vals), dtype=float)

    clock_base = _clock_base_hours(time_vals[0], time_mode)
    t_plot = _seconds_to_axis(time_seconds, time_unit, clock_base)
    t_label = _time_axis_label(time_unit, time_mode)

    T_plot = T_series.values

    # ── Range inicial do eixo y (0.9*T_min, 1.1*T_max) ────────
    if ylim is None:
        _finite = T_plot[np.isfinite(T_plot)]
        _tmin = float(_finite.min()) if _finite.size else 0.0
        _tmax = float(_finite.max()) if _finite.size else 1.0
        if _tmax <= _tmin:
            _tmax = _tmin + 1.0
        ylim = (0.9 * _tmin, 1.1 * _tmax)

    curve = hv.Curve(
        (t_plot, T_plot),
        kdims=[t_label],
        vdims=["T_antenna [K]"],
    ).opts(
        width=width,
        height=height,
        ylim=ylim,
        xlabel=t_label if show_xlabel else "",
        tools=_AXIS_TOOLS,
    )
    if show_title:
        if title is None:
            title = "Série Temporal T_antenna"
        curve = curve.opts(title=title)
    else:
        curve = curve.opts(title="")

    # ── Overlay de eventos (retângulos contorno) ──────────────
    if events is not None:
        spans = events_spans(
            events,
            time_range=time_range,
            time_unit=time_unit,
            time_mode=time_mode,
        )
        if spans:
            overlay = events_overlay(spans, y_range=ylim)
            if overlay is not None:
                return curve * overlay

    return curve


# Registro de servidores pn.serve ativos (por porta) para permitir re-execução
# sem conflito de porta.
_ACTIVE_SERVERS: dict[int, Any] = {}


def serve_interactive_waterfall(
    dataset: xr.Dataset,
    *,
    port: int = 5006,
    open_browser: bool = False,
    title: str = "Waterfall TOD interativo",
    **kwargs: Any,
) -> tuple[str, Any]:
    """Serve o waterfall interativo como um app Panel via ``pn.serve``.

    Widgets Panel (com ``pn.bind``/DynamicMap) costumam falhar com erro de
    JavaScript no render de notebooks VS Code. Rodar o app num servidor Bokeh
    separado (em thread) contorna isso: abra a URL retornada no navegador, onde
    o waterfall datashader interativo funciona normalmente.

    Parameters
    ----------
    dataset:
        Dataset com ``T_antenna``.
    port:
        Porta do servidor (padrão 5006). Se já houver um servidor ativo nessa
        porta, ele é encerrado antes de subir o novo.
    open_browser:
        Se ``True``, abre o navegador automaticamente.
    title:
        Título do app.
    **kwargs:
        Repassados para ``tod_panel`` (inclui ``events``).

    Returns
    -------
    tuple[str, Any]
        (url, server) — URL para abrir no navegador e a thread do servidor
        (use ``server.stop()`` para encerrar).
    """
    _check_holoviews_available()

    app = tod_panel(dataset, **kwargs)
    url, server = _serve_app(
        app,
        port=port,
        title=title,
        open_browser=open_browser,
    )
    print(f"🌐 Waterfall interativo em: {url}   (para encerrar: server.stop())")
    return url, server


def stop_waterfall_servers() -> None:
    """Encerra todos os servidores pn.serve de waterfall ativos."""
    for port, server in list(_ACTIVE_SERVERS.items()):
        try:
            server.stop()
        except Exception:
            pass
        _ACTIVE_SERVERS.pop(port, None)
    if _ACTIVE_SERVERS:
        _ACTIVE_SERVERS.clear()


# Alias público para reindexação de eventos ao grid completo.
reindex_events_to_grid = _reindex_events_to_grid
