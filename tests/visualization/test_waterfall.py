"""\
Módulo: tests/visualization/test_waterfall.py

Testes do visualizador waterfall: spans de eventos por fonte (início/fim
por evento, não global), eixo temporal UTC/local (hora do dia) e ferramentas
de zoom por eixo (sem zoom global).

Copyright BINGO Collaboration
Last modified: 2026-08-03
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
import xarray as xr
from radioskysims_core.domain.common import TimeRange

from radioskysims.visualization.waterfall import (
    _AXIS_TOOLS,
    _clock_base_hours,
    _seconds_to_axis,
    events_overlay,
    events_spans,
    time_series_plot,
    tod_panel,
    waterfall_plot,
)


def _events_dataset() -> xr.Dataset:
    n_time, n_freq, n_src = 24, 4, 3
    time = np.arange(
        np.datetime64("2026-07-26T00:00:00", "ns"),
        np.datetime64("2026-07-26T00:00:00", "ns") + n_time * np.timedelta64(600, "s"),
        np.timedelta64(600, "s"),
    )
    freq = np.linspace(980e6, 1360e6, n_freq)
    T = np.zeros((n_time, n_freq, n_src, 1, 1))
    T[2:6, :, 0, 0, 0] = 10.0  # SAT-A janela 1
    T[10:13, :, 0, 0, 0] = 8.0  # SAT-A janela 2
    T[3:5, :, 1, 0, 0] = 5.0  # SAT-B (sobreposta parcialmente)
    return xr.Dataset(
        {"T_antenna": (("time", "frequency", "source", "polarization", "pointing"), T)},
        coords={
            "time": time,
            "frequency": freq,
            "source": ["SAT-A", "SAT-B", "Sun"],
            "source_type": ("source", ["satellite", "satellite", "localsource"]),
            "polarization": ["V"],
            "pointing": [0],
        },
    )


class _Ev:
    beam_events = _events_dataset()


def _time_range() -> TimeRange:
    return TimeRange.from_iso("2026-07-26T00:00:00", "2026-07-26T04:00:00", resolution=600)


# ── Spans por evento (início/fim por evento, não global) ─────


def test_events_spans_per_source() -> None:
    spans = events_spans(_Ev(), time_range=_time_range(), time_unit="hours", time_mode="UTC")
    labels = [sp["label"] for sp in spans]
    # SAT-A tem 2 janelas contíguas → 2 retângulos separados
    assert labels.count("SAT-A") == 2
    assert labels.count("SAT-B") == 1
    assert "Sun" not in labels  # inativa
    for sp in spans:
        assert sp["start"] < sp["end"]
        assert isinstance(sp["start"], (int, float, np.floating))
        assert isinstance(sp["end"], (int, float, np.floating))


def test_events_spans_gaps_create_separate_spans() -> None:
    spans = events_spans(_Ev(), time_range=_time_range(), time_unit="hours", time_mode="UTC")
    a_spans = [sp for sp in spans if sp["label"] == "SAT-A"]
    # As duas janelas de SAT-A devem ter início/fim distintos (lacuna entre elas)
    assert len(a_spans) == 2
    assert a_spans[0]["end"] < a_spans[1]["start"]


def test_events_spans_time_mode_shifts_axis() -> None:
    spans_utc = events_spans(_Ev(), time_range=_time_range(), time_unit="hours", time_mode="UTC")
    # Simula fuso -3 (clock base 21) — os valores do eixo deslocam
    spans_local = events_spans(
        _Ev(), time_range=_time_range(), time_unit="hours", time_mode="local"
    )
    # O mecanismo é o deslocamento de clock base; se o sistema for UTC, local==UTC
    base = _clock_base_hours(np.datetime64("2026-07-26T00:00:00", "ns"), "local")
    shifted = _seconds_to_axis(7200.0, "hours", 21.0)
    assert shifted == pytest.approx(23.0)
    assert shifted != pytest.approx(2.0)  # ≠ eixo UTC (2h)
    # UTC e local (com base diferente) produzem spans com valores diferentes
    if base != 0.0:
        assert spans_utc[0]["start"] != spans_local[0]["start"]


def test_events_overlay_rectangles() -> None:
    spans = events_spans(_Ev(), time_range=_time_range(), time_unit="hours", time_mode="UTC")
    ov = events_overlay(spans, y_range=(980.0, 1360.0))
    assert ov is not None
    # Cada retângulo tem início/fim próprios no eixo x
    x0 = ov.dimension_values("x0")
    x1 = ov.dimension_values("x1")
    assert len(x0) == len(spans) == len(x1)
    assert all(s < e for s, e in zip(x0, x1, strict=False))


def test_events_overlay_draws_outline_below_min_frequency() -> None:
    spans = events_spans(_Ev(), time_range=_time_range(), time_unit="hours", time_mode="UTC")
    min_freq = np.nanmin(_events_dataset().coords["frequency"].values) / 1e6
    max_freq = np.nanmax(_events_dataset().coords["frequency"].values) / 1e6
    y_lo = min_freq - (max_freq - min_freq) / 10.0
    y_hi = min_freq
    ov = events_overlay(spans, y_range=(y_lo, y_hi))
    assert ov is not None
    opts_repr = repr(ov.opts)
    assert "fill_alpha=0.0" in opts_repr
    assert "line_alpha=0.7" in opts_repr
    assert "line_width=1.5" in opts_repr


def test_waterfall_plot_default_ylim_frequency_range() -> None:
    import holoviews as hv

    hv.extension("bokeh")
    img = waterfall_plot(
        _events_dataset(),
        use_datashader=False,
        time_range=_time_range(),
        show_title=False,
        time_mode="UTC",
    )
    freq = _events_dataset().coords["frequency"].values / 1e6
    ylim = img.opts["ylim"]
    assert ylim[0] == pytest.approx(0.8 * freq.min())
    assert ylim[1] == pytest.approx(1.2 * freq.max())
    # show_title=False esconde o título (string vazia → barra oculta no Bokeh,
    # eixos x colados com a série temporal)
    assert img.opts["title"] == ""


def test_time_series_plot_default_ylim_and_hidden_xlabel() -> None:
    import holoviews as hv

    hv.extension("bokeh")
    curve = time_series_plot(
        _events_dataset(),
        time_range=_time_range(),
        time_mode="UTC",
        show_title=False,
        show_xlabel=False,
    )
    ds = _events_dataset()
    T_series = (
        ds["T_antenna"].sum(dim="source").isel(polarization=0, pointing=0).mean(dim="frequency")
    )
    vals = T_series.values
    tmin = float(np.nanmin(vals))
    tmax = float(np.nanmax(vals))
    ylim = curve.opts["ylim"]
    assert ylim[0] == pytest.approx(0.9 * tmin)
    assert ylim[1] == pytest.approx(1.1 * tmax)
    # show_xlabel=False remove o rótulo do eixo x
    assert curve.opts["xlabel"] == ""


def test_waterfall_and_timeseries_share_x_kdim() -> None:
    """Série temporal e waterfall usam o mesmo kdim x → zoom/pan sincronizado.

    O HoloViews só vincula os ranges entre subplots de um Layout (via
    ``shared_axes=True``) quando os nomes dos kdims coincidem. Como a série
    usa ``Hora do dia [h] (UTC)``, o waterfall precisa usar o mesmo nome
    (em vez de ``time``) para o zoom em um painel refletir no outro.
    """
    import holoviews as hv

    hv.extension("bokeh")
    ts = time_series_plot(
        _events_dataset(),
        time_range=_time_range(),
        time_mode="UTC",
        show_title=False,
        show_xlabel=False,
    )
    wf = waterfall_plot(
        _events_dataset(),
        use_datashader=False,
        time_range=_time_range(),
        show_title=False,
        time_mode="UTC",
    )
    assert str(ts.kdims[0]) == str(wf.kdims[0])

    # Verificação direta no Bokeh: os dois figures compartilham o mesmo x_range.
    layout = hv.Layout([ts, wf]).opts(shared_axes=True, merge_tools=False).cols(1)
    doc = hv.render(layout)
    ids: list[int] = []
    seen: set[int] = set()

    def _walk(m: Any) -> None:
        if id(m) in seen:
            return
        seen.add(id(m))
        if hasattr(m, "x_range"):
            ids.append(id(m.x_range))
        for child in getattr(m, "children", []):
            if isinstance(child, (list, tuple)):
                for c in child:
                    _walk(c)
            else:
                _walk(child)

    _walk(doc)
    assert len(ids) == 2
    assert len(set(ids)) == 1


# ── Eixo temporal (hora do dia UTC/local) ────────────────────


def test_clock_base_and_seconds_to_axis() -> None:
    t0 = np.datetime64("2026-07-26T00:00:00", "ns")
    base_utc = _clock_base_hours(t0, "UTC")
    assert base_utc == pytest.approx(0.0)
    # fuso simulado -3 (21h do dia anterior)
    assert _seconds_to_axis(7200.0, "hours", 21.0) == pytest.approx(23.0)
    assert _seconds_to_axis(3600.0, "minutes", 0.0) == pytest.approx(60.0)


# ── Plotagem + ferramentas de zoom por eixo ──────────────────


def test_waterfall_plot_datashader_is_dynamicmap() -> None:
    import holoviews as hv

    hv.extension("bokeh")
    wf = waterfall_plot(
        _events_dataset(),
        use_datashader=True,
        time_range=_time_range(),
        events=_Ev(),
        fill_missing=True,
        time_mode="UTC",
    )
    # DynamicMap (datashader) → re-rasteriza no zoom preservando a resolução
    assert isinstance(wf, hv.DynamicMap)


def test_waterfall_plot_tools_per_axis() -> None:
    assert "xwheel_zoom" in _AXIS_TOOLS
    assert "ywheel_zoom" in _AXIS_TOOLS
    assert "box_zoom" not in _AXIS_TOOLS
    assert "wheel_zoom" not in _AXIS_TOOLS


def _has_title(element) -> bool:
    try:
        return bool(element.opts["title"])
    except KeyError:
        return False


def test_time_series_plot_no_title() -> None:
    import holoviews as hv

    hv.extension("bokeh")
    ts = time_series_plot(
        _events_dataset(),
        time_range=_time_range(),
        time_mode="UTC",
        show_title=False,
    )
    assert _has_title(ts) is False

    ts_default = time_series_plot(
        _events_dataset(),
        time_range=_time_range(),
        time_mode="UTC",
    )
    assert _has_title(ts_default) is True


def test_tod_panel_show_events_switch_controls_waterfall_overlay(monkeypatch) -> None:
    import holoviews as hv

    hv.extension("bokeh")

    calls: list[object | None] = []

    def _fake_waterfall_plot(*args, **kwargs):
        _ = (args)  # assinala uso (interface/reservado)
        calls.append(kwargs.get("events"))
        return hv.Curve(([0.0, 1.0], [0.0, 1.0]))

    def _fake_time_series_plot(*args, **kwargs):
        _ = (args, kwargs)  # assinala uso (interface/reservado)
        return hv.Curve(([0.0, 1.0], [0.0, 1.0]))

    monkeypatch.setattr(
        "radioskysims.visualization.waterfall.waterfall_plot",
        _fake_waterfall_plot,
    )
    monkeypatch.setattr(
        "radioskysims.visualization.waterfall.time_series_plot",
        _fake_time_series_plot,
    )

    ev = _Ev()
    panel = tod_panel(_events_dataset(), events=ev, time_range=_time_range())

    controls = panel[1]
    show_events = controls[3]
    bound_plot = panel[4].object

    show_events.value = False
    _ = bound_plot()
    show_events.value = True
    _ = bound_plot()

    # Com switch desligado, não deve enviar eventos ao waterfall.
    assert any(call is None for call in calls)
    # Com switch ligado, deve enviar o objeto de eventos.
    assert any(call is ev for call in calls)
