"""src/radioskysims/interfaces/gui/skymap/views.py
Views e renderização da aba Generate.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

import panel as pn
from bokeh.models import ColumnDataSource, Div
from bokeh.plotting import figure

from .presenters import AnalyzeViewModel, GenerateViewModel, SurveyViewModel
from .state import SkyMapGuiState


def render_messages_markdown(state: SkyMapGuiState) -> str:
    """Converte as mensagens do estado para Markdown."""
    if not state.messages:
        return "**Mensagens:** _(sem mensagens)_"

    lines = [f"- **{message.level.upper()}**: {message.text}" for message in state.messages]
    return "**Mensagens:**\n" + "\n".join(lines)


def render_metadata_markdown(
    vm: GenerateViewModel | SurveyViewModel | AnalyzeViewModel | None,
) -> str:
    """Converte os metadados do resultado para Markdown."""
    if vm is None:
        return "**Metadados:** _(nenhum mapa gerado)_"

    lines = [f"- `{key}`: {value}" for key, value in vm.metadata.items() if value != ""]

    content = "\n".join(lines) if lines else "_vazio_"

    if isinstance(vm, SurveyViewModel):
        if vm.valid_fraction is None:
            coverage = "_cobertura indisponível_"
        else:
            coverage = f"- `valid_fraction`: {vm.valid_fraction:.6f} ({vm.valid_pixels}/{vm.npix})"

        content = "\n".join([content, coverage])

    if isinstance(vm, AnalyzeViewModel):
        lines = [content]

        lines.append(f"- `cls_length`: {vm.cls_length}")

        if vm.cls_min is not None:
            lines.append(f"- `cls_min`: {vm.cls_min:.6g}")
        if vm.cls_max is not None:
            lines.append(f"- `cls_max`: {vm.cls_max:.6g}")
        if vm.cls_mean is not None:
            lines.append(f"- `cls_mean`: {vm.cls_mean:.6g}")

        content = "\n".join(lines)

    return "**Metadados:**\n" + (content)


def build_messages_panel(
    state: SkyMapGuiState,
) -> pn.pane.Markdown:
    """Cria o painel de mensagens da interface."""
    return pn.pane.Markdown(
        render_messages_markdown(state),
        sizing_mode="stretch_width",
    )


def build_metadata_panel(
    vm: GenerateViewModel | SurveyViewModel | None = None,
) -> pn.pane.Markdown:
    """Cria o painel de metadados da interface."""
    return pn.pane.Markdown(
        render_metadata_markdown(vm),
        sizing_mode="stretch_width",
    )


def build_generate_placeholder_map() -> Div:
    """Cria o placeholder inicial da visualização do mapa."""
    return Div(
        text="""
        <div style="
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px dashed #9e9e9e;
            border-radius: 6px;
            padding: 10px;
            box-sizing: border-box;
        ">
            <div>
                <strong>SkyMap ainda não gerado</strong><br>
                Configure os parâmetros e clique em Gerar mapa.
            </div>
        </div>
        """,
        height=240,
        sizing_mode="stretch_width",
    )


def build_survey_placeholder_map() -> Div:
    """Cria o placeholder inicial da visualização do survey."""
    return Div(
        text="""
        <div style="
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px dashed #9e9e9e;
            border-radius: 6px;
            padding: 10px;
            box-sizing: border-box;
        ">
            <div>
                <strong>Survey ainda não carregado</strong><br>
                Configure os parâmetros e clique em Load Survey.
            </div>
        </div>
        """,
        height=240,
        sizing_mode="stretch_width",
    )


def build_generate_placeholder_hist() -> Div:
    """Cria o placeholder inicial da visualização do histograma."""
    return Div(
        text="""
        <div style="
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px dashed #9e9e9e;
            border-radius: 6px;
            padding: 10px;
            box-sizing: border-box;
        ">
            <div>
                <strong>Histograma ainda não disponível</strong><br>
                Gere um mapa para visualizar a distribuição dos pixels.
            </div>
        </div>
        """,
        height=220,
        sizing_mode="stretch_width",
    )


def build_survey_placeholder_hist() -> Div:
    """Cria o placeholder inicial do histograma de survey."""
    return Div(
        text="""
        <div style="
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px dashed #9e9e9e;
            border-radius: 6px;
            padding: 10px;
            box-sizing: border-box;
        ">
            <div>
                <strong>Histograma de survey indisponível</strong><br>
                Carregue um survey com pixels válidos para visualizar a distribuição.
            </div>
        </div>
        """,
        height=220,
        sizing_mode="stretch_width",
    )


def build_analyze_placeholder_spectrum() -> Div:
    """Cria o placeholder inicial para o espectro C_l."""
    return Div(
        text="""
        <div style="
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px dashed #9e9e9e;
            border-radius: 6px;
            padding: 10px;
            box-sizing: border-box;
        ">
            <div>
                <strong>Espectro C_l indisponível</strong><br>
                Execute Analyze para visualizar o espectro angular.
            </div>
        </div>
        """,
        height=240,
        sizing_mode="stretch_width",
    )


def build_analyze_placeholder_table() -> pn.pane.Markdown:
    """Cria o placeholder inicial da tabela de C_l."""
    return pn.pane.Markdown(
        "**Tabela C_l:** _(nenhum dado disponível)_",
        sizing_mode="stretch_width",
    )


def build_histogram_plot(
    vm: GenerateViewModel | SurveyViewModel | AnalyzeViewModel | None,
):
    """Cria o gráfico de histograma dos valores dos pixels."""
    if vm is None or vm.histogram is None:
        if isinstance(vm, SurveyViewModel):
            return build_survey_placeholder_hist()
        if isinstance(vm, AnalyzeViewModel):
            return build_generate_placeholder_hist()
        return build_generate_placeholder_hist()

    histogram = vm.histogram

    if hasattr(histogram, "bins") and hasattr(histogram, "counts"):
        bins = histogram.bins
        counts = histogram.counts
    elif isinstance(histogram, tuple) and len(histogram) == 2:
        counts, bins = histogram
    else:
        if isinstance(vm, SurveyViewModel):
            return build_survey_placeholder_hist()
        if isinstance(vm, AnalyzeViewModel):
            return build_generate_placeholder_hist()
        return build_generate_placeholder_hist()

    if len(bins) < 2 or len(counts) == 0:
        if isinstance(vm, SurveyViewModel):
            return build_survey_placeholder_hist()
        if isinstance(vm, AnalyzeViewModel):
            return build_generate_placeholder_hist()
        return build_generate_placeholder_hist()

    source = ColumnDataSource(
        data={
            "left": bins[:-1],
            "right": bins[1:],
            "top": counts,
        }
    )

    plot = figure(
        height=220,
        title="Histograma de pixels",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        sizing_mode="stretch_width",
    )

    plot.quad(
        top="top",
        bottom=0,
        left="left",
        right="right",
        source=source,
        alpha=0.7,
    )

    plot.xaxis.axis_label = "Valor"
    plot.yaxis.axis_label = "Contagem"

    return plot


def build_map_plot(
    vm: GenerateViewModel | SurveyViewModel | AnalyzeViewModel | None,
):
    """Cria o gráfico amostrado dos valores do mapa."""
    if vm is None or vm.map_preview is None:
        if isinstance(vm, SurveyViewModel):
            return build_survey_placeholder_map()
        if isinstance(vm, AnalyzeViewModel):
            return build_generate_placeholder_map()
        return build_generate_placeholder_map()

    map_preview = vm.map_preview

    if hasattr(map_preview, "pixel_index") and hasattr(map_preview, "pixel_value"):
        pixel_index = map_preview.pixel_index
        pixel_value = map_preview.pixel_value
    elif isinstance(map_preview, tuple) and len(map_preview) == 2:
        pixel_index, pixel_value = map_preview
    else:
        if isinstance(vm, SurveyViewModel):
            return build_survey_placeholder_map()
        if isinstance(vm, AnalyzeViewModel):
            return build_generate_placeholder_map()
        return build_generate_placeholder_map()

    if len(pixel_index) == 0 or len(pixel_value) == 0:
        if isinstance(vm, SurveyViewModel):
            return build_survey_placeholder_map()
        if isinstance(vm, AnalyzeViewModel):
            return build_generate_placeholder_map()
        return build_generate_placeholder_map()

    source = ColumnDataSource(
        data={
            "pixel_index": pixel_index,
            "pixel_value": pixel_value,
        }
    )

    plot = figure(
        height=240,
        title="Preview do mapa (amostrado)",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        sizing_mode="stretch_width",
    )

    plot.line(
        "pixel_index",
        "pixel_value",
        source=source,
        line_width=2,
    )

    plot.xaxis.axis_label = "Pixel index"
    plot.yaxis.axis_label = "Valor"

    return plot


def build_spectrum_plot(vm: AnalyzeViewModel | None):
    """Cria gráfico de espectro angular C_l."""

    if vm is None or not vm.spectrum:
        return build_analyze_placeholder_spectrum()

    ell = [item[0] for item in vm.spectrum]
    cl = [item[1] for item in vm.spectrum]

    if not ell or not cl:
        return build_analyze_placeholder_spectrum()

    source = ColumnDataSource(
        data={
            "ell": ell,
            "cl": cl,
        }
    )

    plot = figure(
        height=240,
        title="Espectro angular C_l",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        sizing_mode="stretch_width",
    )

    plot.line("ell", "cl", source=source, line_width=2)
    plot.scatter("ell", "cl", source=source, size=4, alpha=0.6)

    plot.xaxis.axis_label = "Multipolo l"
    plot.yaxis.axis_label = "C_l"

    return plot


def render_cls_table_markdown(vm: AnalyzeViewModel | None) -> str:
    """Renderiza tabela resumida de C_l em Markdown."""

    if vm is None or not vm.cls_table:
        return "**Tabela C_l:** _(nenhum dado disponível)_"

    lines = ["**Tabela C_l (primeiros 25):**", "", "| l | C_l |", "|---:|---:|"]
    for row in vm.cls_table:
        ell = row.get("ell")
        cl = row.get("cl")
        if isinstance(cl, float):
            lines.append(f"| {ell} | {cl:.6g} |")
        else:
            lines.append(f"| {ell} | {cl} |")

    return "\n".join(lines)
