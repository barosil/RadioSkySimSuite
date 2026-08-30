from radioskysims.interfaces.gui.skymap.controller import SkyMapGUIController
from radioskysims.interfaces.gui.skymap.state import SkyMapGuiState


class FakeGenerateUseCase:
    def __init__(self) -> None:
        self.received = None

    def execute(self, dto):
        self.received = dto
        return {
            "frequency_ghz": getattr(dto, "frequency_ghz", 1.4),
            "nside": getattr(dto, "nside", 64),
            "unit": getattr(dto, "unit", "K_RJ"),
            "frame": getattr(dto, "frame", "galactic"),
            "field": getattr(dto, "field", "I"),
            "components": getattr(dto, "components", ["synchrotron"]),
            "map_data": [0.1, 0.2, 0.3, 0.4],
        }


class FakeSurveyUseCase:
    def __init__(self) -> None:
        self.received_kwargs = None

    def execute(self, **kwargs):
        self.received_kwargs = kwargs
        return {
            "nside": kwargs.get("nside", 64),
            "npix": 4,
            "map_data": [1.0, 2.0, 3.0, 4.0],
            "unit": "K_RJ",
            "frame": "equatorial",
            "field": kwargs.get("field", "I"),
        }


class FakeReader:
    def read_map(self, path, *, unit="unknown", frame="galactic", field="I"):
        return {
            "nside": 64,
            "npix": 4,
            "unit": unit,
            "frame": frame,
            "field": field,
            "map_data": [1.0, 2.0, 3.0, 4.0],
            "path": str(path),
        }


class FakeAnalyzeUseCase:
    def execute(self, dto):
        return {
            "nside": 64,
            "lmax": getattr(dto, "lmax", 8),
            "cls": [1.0, 0.5, 0.25],
        }


def test_generate_success_and_state_updates() -> None:
    state = SkyMapGuiState()
    use_case = FakeGenerateUseCase()
    controller = SkyMapGUIController(state, generate_use_case=use_case)

    vm = controller.generate(
        frequency_ghz=1.4,
        nside=64,
        components=["synchrotron"],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )

    assert vm is not None
    assert state.current_map is not None
    assert state.map_origin == "generated"
    assert state.is_processing is False
    assert any(m.level == "success" for m in state.messages)
    assert use_case.received is not None


def test_generate_empty_components() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, generate_use_case=FakeGenerateUseCase())

    vm = controller.generate(
        frequency_ghz=1.4,
        nside=64,
        components=[],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )

    assert vm is None
    assert any("componente" in m.text.lower() for m in state.messages)


def test_generate_invalid_frequency_and_nside() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, generate_use_case=FakeGenerateUseCase())

    vm1 = controller.generate(
        frequency_ghz=0.0,
        nside=64,
        components=["synchrotron"],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )
    assert vm1 is None

    vm2 = controller.generate(
        frequency_ghz=1.4,
        nside=0,
        components=["synchrotron"],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )
    assert vm2 is None


def test_generate_use_case_error() -> None:
    class BrokenUC:
        def execute(self, _dto):
            msg = "boom"
            raise RuntimeError(msg)

    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, generate_use_case=BrokenUC())
    vm = controller.generate(
        frequency_ghz=1.4,
        nside=64,
        components=["synchrotron"],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )
    assert vm is None
    assert any("Falha inesperada" in m.text for m in state.messages)


def test_generate_adds_single_success_message_per_execution() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, generate_use_case=FakeGenerateUseCase())

    vm1 = controller.generate(
        frequency_ghz=1.4,
        nside=64,
        components=["synchrotron"],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )
    assert vm1 is not None

    vm2 = controller.generate(
        frequency_ghz=2.4,
        nside=32,
        components=["dust"],
        unit="K_RJ",
        frame="galactic",
        field="I",
    )
    assert vm2 is not None

    success_messages = [m.text for m in state.messages if m.level == "success"]
    assert success_messages == [
        "Mapa gerado com sucesso.",
        "Mapa gerado com sucesso.",
    ]


def test_survey_success_and_state_updates() -> None:
    state = SkyMapGuiState()
    survey_use_case = FakeSurveyUseCase()
    controller = SkyMapGUIController(state, survey_use_case=survey_use_case)

    vm = controller.survey(
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=64,
        frequency_ghz=1.4,
        unit="K_RJ",
        frame="equatorial",
        field="I",
        base_path="data/hips",
    )

    assert vm is not None
    assert state.current_map is not None
    assert state.map_origin == "survey"
    assert state.is_processing is False
    success_messages = [m.text for m in state.messages if m.level == "success"]
    assert success_messages == ["Mapa de survey carregado com sucesso."]
    assert survey_use_case.received_kwargs == {
        "survey_id": "NVSS",
        "ra_deg": 180.0,
        "dec_deg": 0.0,
        "fov_deg": 2.0,
        "nside": 64,
        "freq_ghz": 1.4,
        "field": "I",
    }


def test_survey_empty_survey_id() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, survey_use_case=FakeSurveyUseCase())

    vm = controller.survey(
        survey_id=" ",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=64,
        frequency_ghz=1.4,
        unit="K_RJ",
        frame="equatorial",
        field="I",
        base_path="data/hips",
    )

    assert vm is None
    assert any("survey_id" in m.text.lower() for m in state.messages)


def test_survey_invalid_frequency() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, survey_use_case=FakeSurveyUseCase())

    vm = controller.survey(
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=64,
        frequency_ghz=0.0,
        unit="K_RJ",
        frame="equatorial",
        field="I",
        base_path="data/hips",
    )

    assert vm is None
    assert any("frequency_ghz" in m.text for m in state.messages)


def test_survey_invalid_nside() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, survey_use_case=FakeSurveyUseCase())

    vm = controller.survey(
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=0,
        frequency_ghz=1.4,
        unit="K_RJ",
        frame="equatorial",
        field="I",
        base_path="data/hips",
    )

    assert vm is None
    assert any("nside" in m.text.lower() for m in state.messages)


def test_survey_file_not_found_error() -> None:
    class BrokenSurveyUC:
        def execute(self, **_kwargs):
            msg = "arquivo ausente"
            raise FileNotFoundError(msg)

    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, survey_use_case=BrokenSurveyUC())

    vm = controller.survey(
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=64,
        frequency_ghz=1.4,
        unit="K_RJ",
        frame="equatorial",
        field="I",
        base_path="data/hips",
    )

    assert vm is None
    assert any("arquivo" in m.text.lower() for m in state.messages)


def test_survey_unexpected_error() -> None:
    class BrokenSurveyUC:
        def execute(self, **_kwargs):
            msg = "boom"
            raise RuntimeError(msg)

    state = SkyMapGuiState()
    controller = SkyMapGUIController(state, survey_use_case=BrokenSurveyUC())

    vm = controller.survey(
        survey_id="NVSS",
        ra_deg=180.0,
        dec_deg=0.0,
        fov_deg=2.0,
        nside=64,
        frequency_ghz=1.4,
        unit="K_RJ",
        frame="equatorial",
        field="I",
        base_path="data/hips",
    )

    assert vm is None
    assert any("Falha inesperada ao carregar survey" in m.text for m in state.messages)
    assert state.is_processing is False


def test_analyze_success_and_state_updates() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        analyze_use_case=FakeAnalyzeUseCase(),
        skymap_reader=FakeReader(),
    )

    vm = controller.analyze(
        input_path="data/map.fits",
        lmax=8,
        unit="uK_CMB",
        frame="galactic",
        field="I",
    )

    assert vm is not None
    assert state.current_map is not None
    assert state.map_origin == "fits"
    assert state.analysis_result is not None
    assert state.is_processing is False
    success_messages = [m.text for m in state.messages if m.level == "success"]
    assert success_messages == ["Análise concluída com sucesso."]


def test_analyze_invalid_lmax() -> None:
    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        analyze_use_case=FakeAnalyzeUseCase(),
        skymap_reader=FakeReader(),
    )

    vm = controller.analyze(
        input_path="data/map.fits",
        lmax=0,
        unit="uK_CMB",
        frame="galactic",
        field="I",
    )

    assert vm is None
    assert any("lmax" in m.text.lower() for m in state.messages)


def test_analyze_unexpected_error() -> None:
    class BrokenAnalyzeUC:
        def execute(self, _dto):
            msg = "boom"
            raise RuntimeError(msg)

    state = SkyMapGuiState()
    controller = SkyMapGUIController(
        state,
        analyze_use_case=BrokenAnalyzeUC(),
        skymap_reader=FakeReader(),
    )

    vm = controller.analyze(
        input_path="data/map.fits",
        lmax=8,
        unit="uK_CMB",
        frame="galactic",
        field="I",
    )

    assert vm is None
    assert any("Falha inesperada ao analisar mapa" in m.text for m in state.messages)
    assert state.is_processing is False