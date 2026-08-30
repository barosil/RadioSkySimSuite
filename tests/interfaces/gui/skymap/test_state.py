from radioskysims.interfaces.gui.skymap.state import SkyMapGuiState


def test_state_transitions() -> None:
    state = SkyMapGuiState()
    state.begin_processing({"frequency_ghz": 1.4})
    assert state.is_processing is True
    assert state.input_params["frequency_ghz"] == 1.4

    state.add_success("ok")
    state.add_error("erro")
    assert len(state.messages) == 2

    state.finish_processing()
    assert state.is_processing is False

    state.clear_messages()
    assert state.messages == []

    state.reset()
    assert state.current_map is None
    assert state.map_origin == "unknown"