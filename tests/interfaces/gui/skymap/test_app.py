import pytest
from bokeh.models import Div

pn = pytest.importorskip("panel")

from importlib import reload  # noqa: E402

import radioskysims.interfaces.gui.skymap.app as skymap_app_module  # noqa: E402
from radioskysims.interfaces.gui.skymap.app import build_skymap_app  # noqa: E402
from radioskysims.interfaces.gui.skymap.controller import SkyMapGUIController  # noqa: E402
from radioskysims.interfaces.gui.skymap.state import SkyMapGuiState  # noqa: E402


class FakeGenerateUseCase:
    def execute(self, dto):
        return {
            "frequency_ghz": getattr(dto, "frequency_ghz", 1.4),
            "nside": getattr(dto, "nside", 64),
            "components": getattr(dto, "components", ["synchrotron"]),
            "map_data": [1.0, 2.0, 3.0, 4.0],
            "unit": "K_RJ",
            "frame": "galactic",
            "field": "I",
        }


class FakeSurveyUseCase:
    def execute(self, **kwargs):
        return {
            "survey_id": kwargs.get("survey_id", "NVSS"),
            "ra_deg": kwargs.get("ra_deg", 180.0),
            "dec_deg": kwargs.get("dec_deg", 0.0),
            "fov_deg": kwargs.get("fov_deg", 2.0),
            "frequency_ghz": kwargs.get("freq_ghz", 1.4),
            "source_path": "data/hips",
            "skymap": {
                "nside": kwargs.get("nside", 64),
                "npix": 8,
                "unit": "K_RJ",
                "frame": "equatorial",
                "field": kwargs.get("field", "I"),
                "map_data": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, float("nan"), 7.0],
            },
        }


class FakeReader:
    def read_map(self, path, *, unit="unknown", frame="galactic", field="I"):
        return {
            "nside": 64,
            "npix": 8,
            "unit": unit,
            "frame": frame,
            "field": field,
            "map_data": [1.0, 2.0, 3.0, 4.0, float("nan"), 6.0, 7.0, 8.0],
            "path": str(path),
        }


class FakeAnalyzeUseCase:
    def execute(self, dto):
        return {
            "nside": 64,
            "lmax": getattr(dto, "lmax", 4),
            "cls": [1.0, 0.5, 0.25, 0.125, 0.0625],
        }


def test_build_app_does_not_serve(monkeypatch):
    called = {"serve": False}

    def fake_serve(*_args, **_kwargs):
        called["serve"] = True

    monkeypatch.setattr(pn, "serve", fake_serve)

    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        generate_use_case=FakeGenerateUseCase(),
        survey_use_case=FakeSurveyUseCase(),
        analyze_use_case=FakeAnalyzeUseCase(),
        skymap_reader=FakeReader(),
    )
    app = build_skymap_app(controller, state)
    assert app is not None
    assert called["serve"] is False


def test_app_module_import_does_not_serve(monkeypatch):
    called = {"serve": False}

    def fake_serve(*_args, **_kwargs):
        called["serve"] = True

    monkeypatch.setattr(pn, "serve", fake_serve)

    reload(skymap_app_module)

    assert called["serve"] is False


def test_generate_and_reset_callbacks():
    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        generate_use_case=FakeGenerateUseCase(),
        survey_use_case=FakeSurveyUseCase(),
        analyze_use_case=FakeAnalyzeUseCase(),
        skymap_reader=FakeReader(),
    )
    app = build_skymap_app(controller, state)

    handles = app._skymap_gui_handles
    widgets = handles["widgets"]
    map_pane = handles["map_pane"]
    hist_pane = handles["hist_pane"]
    metadata_pane = handles["metadata_pane"]
    messages_pane = handles["messages_pane"]

    assert isinstance(map_pane.object, Div)
    assert "SkyMap ainda não gerado" in map_pane.object.text
    assert isinstance(hist_pane.object, Div)
    assert "Histograma ainda não disponível" in hist_pane.object.text
    assert "nenhum mapa gerado" in metadata_pane.object

    widgets.frequency_ghz.value = 1.6
    widgets.nside.value = 32
    widgets.components.value = ["synchrotron", "dust"]

    before_success_count = len([m for m in state.messages if m.level == "success"])
    handles["on_generate"](None)

    assert state.current_map is not None
    assert state.map_origin == "generated"
    assert "nside" in metadata_pane.object
    assert "32" in metadata_pane.object
    assert "npix" in metadata_pane.object
    assert not isinstance(map_pane.object, Div)
    assert not isinstance(hist_pane.object, Div)

    after_success_count = len([m for m in state.messages if m.level == "success"])
    assert after_success_count == before_success_count + 1
    assert messages_pane.object.count("Mapa gerado com sucesso.") == 1

    handles["on_reset"](None)

    assert state.current_map is None
    assert state.map_origin == "unknown"
    assert isinstance(map_pane.object, Div)
    assert "SkyMap ainda não gerado" in map_pane.object.text
    assert isinstance(hist_pane.object, Div)
    assert "Histograma ainda não disponível" in hist_pane.object.text
    assert "nenhum mapa gerado" in metadata_pane.object
    assert "sem mensagens" in messages_pane.object


def test_survey_load_and_reset_callbacks() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        generate_use_case=FakeGenerateUseCase(),
        survey_use_case=FakeSurveyUseCase(),
        analyze_use_case=FakeAnalyzeUseCase(),
        skymap_reader=FakeReader(),
    )
    app = build_skymap_app(controller, state)

    handles = app._skymap_gui_handles
    survey_widgets = handles["survey_widgets"]
    map_pane = handles["map_pane"]
    hist_pane = handles["hist_pane"]
    metadata_pane = handles["metadata_pane"]
    messages_pane = handles["messages_pane"]

    # Placeholder inicial
    assert isinstance(map_pane.object, Div)
    assert "SkyMap ainda não gerado" in map_pane.object.text

    survey_widgets.survey_id.value = "NVSS"
    survey_widgets.ra_deg.value = 180.0
    survey_widgets.dec_deg.value = 0.0
    survey_widgets.fov_deg.value = 2.0
    survey_widgets.nside.value = 64
    survey_widgets.frequency_ghz.value = 1.4
    survey_widgets.field.value = "I"
    survey_widgets.base_path.value = "data/hips"

    before_success_count = len([m for m in state.messages if m.level == "success"])
    handles["on_survey_load"](None)

    assert state.current_map is not None
    assert state.map_origin == "survey"
    assert "survey_id" in metadata_pane.object
    assert "NVSS" in metadata_pane.object
    assert "valid_fraction" in metadata_pane.object
    assert not isinstance(map_pane.object, Div)
    assert not isinstance(hist_pane.object, Div)

    after_success_count = len([m for m in state.messages if m.level == "success"])
    assert after_success_count == before_success_count + 1
    assert messages_pane.object.count("Mapa de survey carregado com sucesso.") == 1

    handles["on_survey_reset"](None)

    assert state.current_map is None
    assert state.map_origin == "unknown"
    assert isinstance(map_pane.object, Div)
    assert "Survey ainda não carregado" in map_pane.object.text
    assert isinstance(hist_pane.object, Div)
    assert "Histograma de survey indisponível" in hist_pane.object.text
    assert "nenhum mapa gerado" in metadata_pane.object
    assert "sem mensagens" in messages_pane.object


def test_analyze_and_reset_callbacks() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        generate_use_case=FakeGenerateUseCase(),
        survey_use_case=FakeSurveyUseCase(),
        analyze_use_case=FakeAnalyzeUseCase(),
        skymap_reader=FakeReader(),
    )
    app = build_skymap_app(controller, state)

    handles = app._skymap_gui_handles
    analyze_widgets = handles["analyze_widgets"]
    spectrum_pane = handles["spectrum_pane"]
    cls_table_pane = handles["cls_table_pane"]
    metadata_pane = handles["metadata_pane"]
    messages_pane = handles["messages_pane"]

    assert isinstance(spectrum_pane.object, Div)
    assert "Espectro C_l indisponível" in spectrum_pane.object.text
    assert "nenhum dado disponível" in cls_table_pane.object

    analyze_widgets.input_path.value = "data/map.fits"
    analyze_widgets.lmax.value = 8
    analyze_widgets.unit.value = "uK_CMB"
    analyze_widgets.frame.value = "galactic"
    analyze_widgets.field.value = "I"

    before_success_count = len([m for m in state.messages if m.level == "success"])
    handles["on_analyze"](None)

    assert state.current_map is not None
    assert state.map_origin == "fits"
    assert "cls_length" in metadata_pane.object
    assert not isinstance(spectrum_pane.object, Div)
    assert "Tabela C_l" in cls_table_pane.object

    after_success_count = len([m for m in state.messages if m.level == "success"])
    assert after_success_count == before_success_count + 1
    assert messages_pane.object.count("Análise concluída com sucesso.") == 1

    handles["on_analyze_reset"](None)

    assert state.current_map is None
    assert state.map_origin == "unknown"
    assert isinstance(spectrum_pane.object, Div)
    assert "Espectro C_l indisponível" in spectrum_pane.object.text
    assert "nenhum dado disponível" in cls_table_pane.object
    assert "sem mensagens" in messages_pane.object
