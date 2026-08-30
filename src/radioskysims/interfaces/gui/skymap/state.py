"""src/radioskysims/interfaces/gui/skymap/state.py
Estado da GUI SkyMap.
Copyright BINGO Collaboration
Last modified: 2026-07-23
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


MapOrigin = Literal["generated", "survey", "fits", "unknown"]
MessageLevel = Literal["success", "error", "info"]


@dataclass(slots=True)
class GuiMessage:
    """Mensagem para feedback na interface."""

    level: MessageLevel
    text: str


@dataclass(slots=True)
class SkyMapGuiState:
    """Estado mínimo da GUI SkyMap."""

    current_map: Any | None = None
    map_origin: MapOrigin = "unknown"
    input_params: dict[str, Any] = field(default_factory=dict)
    analysis_result: Any | None = None
    messages: list[GuiMessage] = field(default_factory=list)
    is_processing: bool = False

    def begin_processing(self, input_params: dict[str, Any] | None = None) -> None:
        self.is_processing = True
        if input_params is not None:
            self.input_params = dict(input_params)

    def finish_processing(self) -> None:
        self.is_processing = False

    def add_success(self, message: str) -> None:
        self.messages.append(GuiMessage(level="success", text=message))

    def add_error(self, message: str) -> None:
        self.messages.append(GuiMessage(level="error", text=message))

    def clear_messages(self) -> None:
        self.messages.clear()

    def reset(self) -> None:
        self.current_map = None
        self.map_origin = "unknown"
        self.input_params = {}
        self.analysis_result = None
        self.messages = []
        self.is_processing = False