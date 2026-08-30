"""src/radioskysims/interfaces/gui/skymap/app.py
App Panel para SkyMap GUI.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

import panel as pn

from .controller import SkyMapGUIController
from .state import SkyMapGuiState
from .views import (
    build_analyze_placeholder_spectrum,
    build_analyze_placeholder_table,
    build_generate_placeholder_hist,
    build_generate_placeholder_map,
    build_spectrum_plot,
    build_survey_placeholder_hist,
    build_survey_placeholder_map,
    build_histogram_plot,
    build_map_plot,
    build_messages_panel,
    build_metadata_panel,
    render_cls_table_markdown,
    render_messages_markdown,
    render_metadata_markdown,
)
from .widgets import (
    build_analyze_widgets,
    build_generate_widgets,
    build_survey_widgets,
)


def build_skymap_app(controller: SkyMapGUIController, state: SkyMapGuiState) -> pn.viewable.Viewable:
    """Monta aplicação Panel sem iniciar servidor."""
    generate_w = build_generate_widgets()
    survey_w = build_survey_widgets()
    analyze_w = build_analyze_widgets()

    messages_pane = build_messages_panel(state)
    metadata_pane = build_metadata_panel()
    map_pane = pn.pane.Bokeh(build_generate_placeholder_map(), sizing_mode="stretch_width")
    hist_pane = pn.pane.Bokeh(build_generate_placeholder_hist(), sizing_mode="stretch_width")
    spectrum_pane = pn.pane.Bokeh(build_analyze_placeholder_spectrum(), sizing_mode="stretch_width")
    cls_table_pane = build_analyze_placeholder_table()

    def _refresh_messages() -> None:
        messages_pane.object = render_messages_markdown(state)

    def _set_generate_placeholders() -> None:
        map_placeholder = build_generate_placeholder_map()
        hist_placeholder = build_generate_placeholder_hist()
        map_pane.object = map_placeholder
        hist_pane.object = hist_placeholder
        spectrum_pane.object = build_analyze_placeholder_spectrum()
        cls_table_pane.object = render_cls_table_markdown(None)
        metadata_pane.object = render_metadata_markdown(None)

    def _set_survey_placeholders() -> None:
        map_pane.object = build_survey_placeholder_map()
        hist_pane.object = build_survey_placeholder_hist()
        spectrum_pane.object = build_analyze_placeholder_spectrum()
        cls_table_pane.object = render_cls_table_markdown(None)
        metadata_pane.object = render_metadata_markdown(None)

    def _set_analyze_placeholders() -> None:
        map_pane.object = build_generate_placeholder_map()
        hist_pane.object = build_generate_placeholder_hist()
        spectrum_pane.object = build_analyze_placeholder_spectrum()
        cls_table_pane.object = render_cls_table_markdown(None)
        metadata_pane.object = render_metadata_markdown(None)

    def _on_generate(_event: object) -> None:
        generate_w.generate.disabled = True
        try:
            vm = controller.generate(
                frequency_ghz=float(generate_w.frequency_ghz.value),
                nside=int(generate_w.nside.value),
                components=list(generate_w.components.value),
                unit=str(generate_w.unit.value),
                frame=str(generate_w.frame.value),
                field=str(generate_w.field.value),
            )
            if vm is not None:
                metadata_pane.object = render_metadata_markdown(vm)
                hist_plot = build_histogram_plot(vm)
                map_plot = build_map_plot(vm)
                hist_pane.object = hist_plot
                map_pane.object = map_plot
                spectrum_pane.object = build_analyze_placeholder_spectrum()
                cls_table_pane.object = render_cls_table_markdown(None)
            _refresh_messages()
        finally:
            generate_w.generate.disabled = False

    def _on_reset(_event: object) -> None:
        state.reset()
        generate_w.frequency_ghz.value = 1.4
        generate_w.nside.value = 64
        generate_w.components.value = ["synchrotron"]
        generate_w.unit.value = "K_RJ"
        generate_w.frame.value = "galactic"
        generate_w.field.value = "I"
        _set_generate_placeholders()
        _refresh_messages()

    def _on_survey_load(_event: object) -> None:
        survey_w.load_survey.disabled = True
        try:
            vm = controller.survey(
                survey_id=str(survey_w.survey_id.value),
                ra_deg=float(survey_w.ra_deg.value),
                dec_deg=float(survey_w.dec_deg.value),
                fov_deg=float(survey_w.fov_deg.value),
                nside=int(survey_w.nside.value),
                frequency_ghz=float(survey_w.frequency_ghz.value),
                unit=str(survey_w.unit.value),
                frame=str(survey_w.frame.value),
                field=str(survey_w.field.value),
                base_path=str(survey_w.base_path.value),
            )

            if vm is not None:
                metadata_pane.object = render_metadata_markdown(vm)
                hist_pane.object = build_histogram_plot(vm)
                map_pane.object = build_map_plot(vm)
                spectrum_pane.object = build_analyze_placeholder_spectrum()
                cls_table_pane.object = render_cls_table_markdown(None)

            _refresh_messages()
        finally:
            survey_w.load_survey.disabled = False

    def _on_survey_reset(_event: object) -> None:
        state.reset()
        survey_w.survey_id.value = "NVSS"
        survey_w.ra_deg.value = 180.0
        survey_w.dec_deg.value = 0.0
        survey_w.fov_deg.value = 2.0
        survey_w.nside.value = 64
        survey_w.frequency_ghz.value = 1.4
        survey_w.unit.value = "K_RJ"
        survey_w.frame.value = "equatorial"
        survey_w.field.value = "I"
        survey_w.base_path.value = "data/hips"
        _set_survey_placeholders()
        _refresh_messages()

    def _on_analyze(_event: object) -> None:
        analyze_w.analyze.disabled = True
        try:
            vm = controller.analyze(
                input_path=str(analyze_w.input_path.value),
                lmax=int(analyze_w.lmax.value),
                unit=str(analyze_w.unit.value),
                frame=str(analyze_w.frame.value),
                field=str(analyze_w.field.value),
            )

            if vm is not None:
                metadata_pane.object = render_metadata_markdown(vm)
                map_pane.object = build_map_plot(vm)
                hist_pane.object = build_histogram_plot(vm)
                spectrum_pane.object = build_spectrum_plot(vm)
                cls_table_pane.object = render_cls_table_markdown(vm)

            _refresh_messages()
        finally:
            analyze_w.analyze.disabled = False

    def _on_analyze_reset(_event: object) -> None:
        state.reset()
        analyze_w.input_path.value = ""
        analyze_w.lmax.value = 16
        analyze_w.unit.value = "uK_CMB"
        analyze_w.frame.value = "galactic"
        analyze_w.field.value = "I"
        _set_analyze_placeholders()
        _refresh_messages()

    generate_w.generate.on_click(_on_generate)
    generate_w.reset.on_click(_on_reset)
    survey_w.load_survey.on_click(_on_survey_load)
    survey_w.reset.on_click(_on_survey_reset)
    analyze_w.analyze.on_click(_on_analyze)
    analyze_w.reset.on_click(_on_analyze_reset)

    generate_tab = pn.Column(
        "## Generate",
        generate_w.frequency_ghz,
        generate_w.nside,
        generate_w.components,
        generate_w.unit,
        generate_w.frame,
        generate_w.field,
        pn.Row(generate_w.generate, generate_w.reset),
    )

    survey_tab = pn.Column(
        "## Survey",
        survey_w.survey_id,
        pn.Row(survey_w.ra_deg, survey_w.dec_deg),
        pn.Row(survey_w.fov_deg, survey_w.nside),
        pn.Row(survey_w.frequency_ghz, survey_w.field),
        pn.Row(survey_w.unit, survey_w.frame),
        survey_w.base_path,
        pn.Row(survey_w.load_survey, survey_w.reset),
    )

    analyze_tab = pn.Column(
        "## Analyze",
        analyze_w.input_path,
        pn.Row(analyze_w.lmax, analyze_w.field),
        pn.Row(analyze_w.unit, analyze_w.frame),
        pn.Row(analyze_w.analyze, analyze_w.reset),
    )

    tabs = pn.Tabs(("Generate", generate_tab), ("Survey", survey_tab), ("Analyze", analyze_tab), dynamic=False)

    template = pn.template.FastListTemplate(
        title="RadioSkySim - SkyMap GUI",
        sidebar=[messages_pane],
        main=[tabs, metadata_pane, map_pane, hist_pane, spectrum_pane, cls_table_pane],
    )

    # Ganchos para testes de callbacks sem browser automation.
    template._skymap_gui_handles = {"widgets": generate_w, "survey_widgets": survey_w, "analyze_widgets": analyze_w, "on_generate": _on_generate, "on_reset": _on_reset, "on_survey_load": _on_survey_load, "on_survey_reset": _on_survey_reset, "on_analyze": _on_analyze, "on_analyze_reset": _on_analyze_reset, "messages_pane": messages_pane, "metadata_pane": metadata_pane, "map_pane": map_pane, "hist_pane": hist_pane, "spectrum_pane": spectrum_pane, "cls_table_pane": cls_table_pane}
    return template