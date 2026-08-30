"""Testes do worker de background do ``tod export`` (ticket TOD-004)."""

from __future__ import annotations

import json
from pathlib import Path

import radioskysims.interfaces.cli.commands.export_worker as worker


class FakeRepo:
    """Repositório fake que registra as chamadas de update."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.calls: list[tuple[object, ...]] = []

    def update_status(self, job_id: int, status: object, **kwargs: object) -> None:
        self.calls.append(("status", job_id, status, kwargs))

    def update_progress(self, job_id: int, **kwargs: object) -> None:
        self.calls.append(("progress", job_id, kwargs))

    def close(self) -> None:
        pass


def test_worker_success(
    monkeypatch,
    tmp_path: Path,
) -> None:
    repo = FakeRepo("sqlite://")
    monkeypatch.setattr(worker, "JobRepository", lambda _url: repo)

    executed: dict[str, object] = {}

    def fake_execute(**kwargs: object) -> str:
        executed.update(kwargs)
        return "ok"

    monkeypatch.setattr(worker, "execute_export_tod_command", fake_execute)

    out = tmp_path / "w.nc"
    code = worker.main(["--job-id", "5", "--output", str(out)])

    assert code == 0
    assert (
        "status",
        5,
        worker.JobStatus.RUNNING,
        {"output_path": str(out)},
    ) in repo.calls
    assert any(
        c == ("status", 5, worker.JobStatus.SUCCESS, {"output_path": str(out)}) for c in repo.calls
    )
    assert ("progress", 5, {"percent": 5.0, "step": "simulação iniciada"}) in repo.calls
    assert executed["output"] == out

    prog = json.loads(worker.progress_file_path(out).read_text())
    assert prog["status"] == "SUCCESS"
    assert prog["percent"] == 100.0
    assert prog["step"] == "done"


def test_worker_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    repo = FakeRepo("sqlite://")
    monkeypatch.setattr(worker, "JobRepository", lambda _url: repo)

    def boom(*args: object, **kwargs: object) -> None:
        _ = (args, kwargs)
        msg = "boom"
        raise RuntimeError(msg)

    monkeypatch.setattr(worker, "execute_export_tod_command", boom)

    out = tmp_path / "w2.nc"
    code = worker.main(["--job-id", "6", "--output", str(out)])

    assert code == 1
    assert any(
        c[0] == "status" and c[2] == worker.JobStatus.FAILED and "boom" in c[3]["error"]  # type: ignore[operator]
        for c in repo.calls
    )

    prog = json.loads(worker.progress_file_path(out).read_text())
    assert prog["status"] == "FAILED"
    assert "boom" in prog["error"]


def test_worker_default_output(
    monkeypatch,
    tmp_path: Path,
) -> None:
    repo = FakeRepo("sqlite://")
    monkeypatch.setattr(worker, "JobRepository", lambda _url: repo)
    monkeypatch.setattr(
        worker,
        "_default_output_path",
        lambda: tmp_path / "auto.nc",
    )

    def fake_execute(**kwargs: object) -> str:
        _ = (kwargs,)
        return "ok"

    monkeypatch.setattr(worker, "execute_export_tod_command", fake_execute)

    code = worker.main(["--job-id", "9"])

    assert code == 0
    assert any(
        c
        == (
            "status",
            9,
            worker.JobStatus.SUCCESS,
            {"output_path": str(tmp_path / "auto.nc")},
        )
        for c in repo.calls
    )
