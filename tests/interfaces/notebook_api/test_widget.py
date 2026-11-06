"""Testes do widget de progresso para notebooks (ticket TOD-007)."""

from __future__ import annotations

import sys
from typing import Any

import pytest
from ipywidgets import Button, FloatProgress, VBox

from radioskysims.interfaces.notebook_api.widget import progress_widget


class FakeHandle:
    """Handle fake usado nos testes do widget."""

    job_id = 1

    def __init__(self, snap: dict[str, Any]) -> None:
        self._snap = snap

    def refresh(self) -> dict[str, Any]:
        return self._snap

    def cancel(self) -> str:
        return "ok"


def test_progress_widget_import_error(
    monkeypatch,
) -> None:
    monkeypatch.setitem(sys.modules, "ipywidgets", None)
    handle = FakeHandle(
        {
            "status": "RUNNING",
            "percent": 0.0,
            "step": "starting",
            "eta": None,
            "error": None,
        }
    )
    with pytest.raises(ImportError):
        progress_widget(handle)


def test_progress_widget_returns_box() -> None:
    handle = FakeHandle(
        {
            "status": "SUCCESS",
            "percent": 100.0,
            "step": "done",
            "eta": "0:00:00",
            "error": None,
        }
    )
    box = progress_widget(handle, interval=0.05)
    assert isinstance(box, VBox)
    kinds = [type(child) for child in box.children]
    assert any(issubclass(kind, FloatProgress) for kind in kinds)
    assert any(issubclass(kind, Button) for kind in kinds)
