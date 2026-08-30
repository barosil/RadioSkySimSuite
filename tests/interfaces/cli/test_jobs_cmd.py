"""Testes dos comandos de gerenciamento de jobs (ticket TOD-005)."""

from __future__ import annotations

import json
import os
import signal
from io import StringIO
from pathlib import Path
from typing import Any

from radioskysims_core.db.jobs import Job, JobStatus

from radioskysims.interfaces.cli.commands.jobs_cmd import (
    execute_jobs_cancel,
    execute_jobs_list,
    execute_jobs_monitor,
    execute_jobs_status,
)
from radioskysims.interfaces.cli.main import (
    SkyMapCLIUseCases,
    run,
)


class FakeRepo:
    """Repositório fake que registra chamadas e devolve jobs em memória."""

    def __init__(self, url: str, jobs: dict[int, Job]) -> None:
        self.url = url
        self.jobs = jobs
        self.status_updates: list[tuple[int, object, dict[str, object]]] = []

    def list(self, *, status: object = None, limit: int = 100) -> list[Job]:
        _ = (status, limit)
        return list(self.jobs.values())

    def get(self, job_id: int) -> Job | None:
        return self.jobs.get(job_id)

    def update_status(
        self,
        job_id: int,
        status: object,
        **kwargs: object,
    ) -> None:
        self.status_updates.append((job_id, status, kwargs))

    def close(self) -> None:
        pass


def _factory(repo: FakeRepo) -> Any:
    return lambda _url: repo


def test_jobs_list_empty() -> None:
    repo = FakeRepo("sqlite://", {})
    result = execute_jobs_list(
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )
    assert result == "Nenhum job encontrado."


def test_jobs_list_rows() -> None:
    job = Job(
        id=1,
        name="tod export",
        status=JobStatus.RUNNING.value,
        progress_percent=50.0,
    )
    repo = FakeRepo("sqlite://", {1: job})
    result = execute_jobs_list(
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )
    assert "ID\tSTATUS\tPROG\tNOME" in result
    assert "1\tRUNNING\t50%" in result


def test_jobs_status_found() -> None:
    job = Job(
        id=3,
        name="tod export",
        status=JobStatus.SUCCESS.value,
        output_path="/tmp/x.nc",
    )
    repo = FakeRepo("sqlite://", {3: job})
    result = execute_jobs_status(
        3,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )
    assert "Status: SUCCESS" in result
    assert "/tmp/x.nc" in result


def test_jobs_status_not_found() -> None:
    repo = FakeRepo("sqlite://", {})
    result = execute_jobs_status(
        9,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )
    assert "não encontrado" in result


def test_jobs_cancel_running_with_pid(
    monkeypatch,
) -> None:
    killed: dict[str, int] = {}
    monkeypatch.setattr(os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(
        os,
        "killpg",
        lambda pgid, sig: killed.update(pgid=pgid, sig=sig),
    )

    job = Job(
        id=5,
        name="tod export",
        status=JobStatus.RUNNING.value,
        pid=4242,
    )
    repo = FakeRepo("sqlite://", {5: job})
    result = execute_jobs_cancel(
        5,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )

    assert repo.status_updates == [(5, JobStatus.CANCELLED, {})]
    assert killed == {"pgid": 4242, "sig": signal.SIGTERM}
    assert "cancelado" in result


def test_jobs_cancel_no_pid() -> None:
    job = Job(
        id=6,
        name="tod export",
        status=JobStatus.PENDING.value,
        pid=None,
    )
    repo = FakeRepo("sqlite://", {6: job})
    result = execute_jobs_cancel(
        6,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )

    assert repo.status_updates == [(6, JobStatus.CANCELLED, {})]
    assert "sem worker ativo" in result


def test_jobs_cancel_final_status_ignored() -> None:
    job = Job(
        id=7,
        name="tod export",
        status=JobStatus.SUCCESS.value,
        pid=123,
    )
    repo = FakeRepo("sqlite://", {7: job})
    result = execute_jobs_cancel(
        7,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )

    assert "já está em SUCCESS" in result
    assert repo.status_updates == []


def test_jobs_cancel_not_found() -> None:
    repo = FakeRepo("sqlite://", {})
    result = execute_jobs_cancel(
        11,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
    )
    assert "não encontrado" in result
    assert repo.status_updates == []


def test_run_jobs_status_dispatch(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.cli.main as main

    captured: dict[str, object] = {}

    def fake_status(
        job_id: int,
        *,
        jobs_db: str | None = None,
        repository_factory: object = None,
    ) -> str:
        _ = (repository_factory,)
        captured["job_id"] = job_id
        captured["jobs_db"] = jobs_db
        return "STATUS OK"

    monkeypatch.setattr(main, "execute_jobs_status", fake_status)

    stdout = StringIO()
    exit_code = run(
        ["tod", "jobs", "status", "42", "--jobs-db", "sqlite://"],
        use_cases=SkyMapCLIUseCases(generate_skymap=object()),
        stdout=stdout,
        stderr=StringIO(),
    )

    assert exit_code == 0
    assert captured == {"job_id": 42, "jobs_db": "sqlite://"}
    assert "STATUS OK" in stdout.getvalue()


def test_jobs_monitor_renders(
    tmp_path: Path,
) -> None:
    out = tmp_path / "m.nc"
    prog_path = out.with_suffix(out.suffix + ".progress.json")
    prog_path.write_text(
        json.dumps(
            {
                "status": "RUNNING",
                "percent": 50.0,
                "step": "tracks",
                "eta": "0:05:00",
            }
        )
    )

    job = Job(
        id=20,
        name="tod export",
        status=JobStatus.RUNNING.value,
        output_path=str(out),
    )
    repo = FakeRepo("sqlite://", {20: job})
    stdout = StringIO()

    code = execute_jobs_monitor(
        20,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
        stdout=stdout,
    )

    assert code == 0
    text = stdout.getvalue()
    assert "Job 20 [RUNNING]" in text
    assert "50%" in text
    assert "tracks" in text
    assert "0:05:00" in text


def test_jobs_monitor_not_found() -> None:
    repo = FakeRepo("sqlite://", {})
    stdout = StringIO()
    code = execute_jobs_monitor(
        3,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
        stdout=stdout,
    )
    assert code == 1
    assert "não encontrado" in stdout.getvalue()


def test_jobs_monitor_no_output() -> None:
    job = Job(
        id=4,
        name="tod export",
        status=JobStatus.RUNNING.value,
        output_path=None,
    )
    repo = FakeRepo("sqlite://", {4: job})
    stdout = StringIO()
    code = execute_jobs_monitor(
        4,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
        stdout=stdout,
    )
    assert code == 1
    assert "sem output" in stdout.getvalue()


def test_jobs_monitor_watch_stops_on_final(
    tmp_path: Path,
) -> None:
    out = tmp_path / "w.nc"
    prog_path = out.with_suffix(out.suffix + ".progress.json")
    prog_path.write_text(json.dumps({"status": "SUCCESS", "percent": 100.0, "step": "done"}))

    job = Job(
        id=21,
        name="tod export",
        status=JobStatus.SUCCESS.value,
        output_path=str(out),
    )
    repo = FakeRepo("sqlite://", {21: job})
    stdout = StringIO()

    code = execute_jobs_monitor(
        21,
        jobs_db="sqlite://",
        repository_factory=_factory(repo),
        watch=True,
        interval=0.1,
        stdout=stdout,
    )

    assert code == 0
    assert "SUCCESS" in stdout.getvalue()
