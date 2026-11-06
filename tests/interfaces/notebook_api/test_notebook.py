"""Testes da API de notebook (ticket TOD-007): JobHandle + run_simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from radioskysims_core.db.jobs import Job, JobStatus

from radioskysims.interfaces.notebook_api.notebook import JobHandle, run_simulation


class FakeRepo:
    """Repositório fake com jobs em memória."""

    def __init__(self, jobs: dict[int, Job]) -> None:
        self.jobs = jobs

    def get(self, job_id: int) -> Job | None:
        return self.jobs.get(job_id)

    def close(self) -> None:
        pass


def test_jobhandle_refresh(tmp_path: Path) -> None:
    out = tmp_path / "h.nc"
    prog = out.with_suffix(out.suffix + ".progress.json")
    prog.write_text(
        json.dumps(
            {
                "status": "RUNNING",
                "percent": 40.0,
                "step": "tracks",
                "eta": "0:03:00",
            }
        )
    )
    job = Job(
        id=5,
        name="tod export",
        status=JobStatus.RUNNING.value,
        output_path=str(out),
        progress_percent=10.0,
    )
    repo = FakeRepo({5: job})
    handle = JobHandle(5, jobs_db="sqlite://", repository_factory=lambda _url: repo)

    snap = handle.refresh()
    assert snap["status"] == "RUNNING"
    assert snap["percent"] == 40.0  # arquivo sobrepõe o valor do DB
    assert snap["step"] == "tracks"
    assert snap["eta"] == "0:03:00"
    assert snap["output_path"] == str(out)


def test_jobhandle_refresh_not_found() -> None:
    repo = FakeRepo({})
    handle = JobHandle(9, jobs_db="sqlite://", repository_factory=lambda _url: repo)
    snap = handle.refresh()
    assert snap["status"] is None
    assert snap["percent"] == 0.0


def test_jobhandle_status_property() -> None:
    job = Job(id=7, name="tod export", status=JobStatus.SUCCESS.value, output_path=None)
    repo = FakeRepo({7: job})
    handle = JobHandle(7, jobs_db="sqlite://", repository_factory=lambda _url: repo)
    assert handle.status == "SUCCESS"


def test_jobhandle_wait_final_immediately() -> None:
    job = Job(id=8, name="tod export", status=JobStatus.SUCCESS.value, output_path=None)
    repo = FakeRepo({8: job})
    handle = JobHandle(8, jobs_db="sqlite://", repository_factory=lambda _url: repo)
    snap = handle.wait(interval=0.01)
    assert snap["status"] == "SUCCESS"


def test_jobhandle_cancel(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.notebook_api.notebook as nb

    called: dict[str, object] = {}

    def fake_cancel(
        job_id: int,
        *,
        jobs_db: str | None = None,
        repository_factory: object = None,
    ) -> str:
        _ = (repository_factory,)
        called["job_id"] = job_id
        called["jobs_db"] = jobs_db
        return "cancelado"

    monkeypatch.setattr(nb, "execute_jobs_cancel", fake_cancel)

    handle = JobHandle(3, jobs_db="sqlite://")
    result = handle.cancel()

    assert called == {"job_id": 3, "jobs_db": "sqlite://"}
    assert result == "cancelado"


def test_run_simulation_foreground(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.notebook_api.notebook as nb

    executed: dict[str, object] = {}

    def fake_execute(**kwargs: object) -> str:
        executed.update(kwargs)
        return "resumo"

    monkeypatch.setattr(nb, "execute_export_tod_command", fake_execute)

    callbacks: list[dict[str, Any]] = []
    result = run_simulation(
        "settings.toml",
        telescope="uirapuru",
        background=False,
        progress_callback=callbacks.append,
    )

    assert result == "resumo"
    assert executed["telescope"] == "uirapuru"
    assert [c["status"] for c in callbacks] == ["RUNNING", "SUCCESS"]


def test_run_simulation_background(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.notebook_api.notebook as nb

    launched: dict[str, object] = {}

    def fake_launch(**kwargs: object) -> int:
        launched.update(kwargs)
        return 42

    monkeypatch.setattr(nb, "launch_background_export", fake_launch)

    result = run_simulation(
        "settings.toml",
        telescope="uirapuru",
        background=True,
        jobs_db="sqlite://",
    )

    assert isinstance(result, JobHandle)
    assert result.job_id == 42
    assert launched["telescope"] == "uirapuru"
