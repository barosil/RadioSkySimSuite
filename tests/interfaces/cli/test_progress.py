"""Testes do módulo de progresso JSON (ticket TOD-006)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from radioskysims.interfaces.cli.commands.progress import (
    estimate_eta,
    progress_file_path,
    read_progress,
    write_progress,
)


def test_estimate_eta_zero() -> None:
    assert estimate_eta(100.0, 0.0) is None


def test_estimate_eta_linear() -> None:
    started = time.monotonic() - 60.0  # 60s decorridos
    eta = estimate_eta(started, 10.0)
    assert eta == "0:09:00"  # total 600s - 60s = 540s


def test_estimate_eta_done() -> None:
    started = time.monotonic() - 30.0
    assert estimate_eta(started, 100.0) == "0:00:00"


def test_write_read_progress(tmp_path: Path) -> None:
    path = tmp_path / "x.progress.json"
    write_progress(
        path,
        status="RUNNING",
        percent=50.0,
        step="tracks",
        started_at=time.monotonic(),
    )

    data = json.loads(path.read_text())
    assert data["status"] == "RUNNING"
    assert data["percent"] == 50.0
    assert data["step"] == "tracks"
    assert "eta" in data
    assert "updated_at" in data
    assert read_progress(path) == data


def test_write_progress_clamps_percent(tmp_path: Path) -> None:
    path = tmp_path / "y.progress.json"
    write_progress(
        path,
        status="RUNNING",
        percent=150.0,
        step="tracks",
        started_at=time.monotonic(),
    )
    data = json.loads(path.read_text())
    assert data["percent"] == 100.0


def test_write_progress_error(tmp_path: Path) -> None:
    path = tmp_path / "z.progress.json"
    write_progress(
        path,
        status="FAILED",
        percent=100.0,
        step="failed",
        started_at=time.monotonic(),
        error="boom",
    )
    data = json.loads(path.read_text())
    assert data["error"] == "boom"


def test_read_progress_missing(tmp_path: Path) -> None:
    assert read_progress(tmp_path / "nope.json") == {}


def test_read_progress_corrupt(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json")
    assert read_progress(path) == {}


def test_progress_file_path() -> None:
    assert progress_file_path(Path("a.nc")) == Path("a.nc.progress.json")
    assert progress_file_path(Path("/x/y.tod.nc")) == Path("/x/y.tod.nc.progress.json")
