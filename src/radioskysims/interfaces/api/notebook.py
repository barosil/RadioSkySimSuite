"""\
Módulo: src/radioskysims/interfaces/api/notebook.py

Descrição:
    API de notebook para execução de simulações TOD (ticket TOD-007).
    ``run_simulation`` roda em foreground (retorna resumo) ou em background
    (retorna um ``JobHandle`` para acompanhar/cancelar).

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable

from radioskysims_core.db.job_repository import DEFAULT_JOBS_DB, JobRepository
from radioskysims_core.db.jobs import JobStatus

from radioskysims.interfaces.cli.commands.export_tod import (
    execute_export_tod_command,
    launch_background_export,
)
from radioskysims.interfaces.cli.commands.jobs_cmd import execute_jobs_cancel
from radioskysims.interfaces.cli.commands.progress import (
    progress_file_path,
    read_progress,
)

_FINAL_STATUSES = {
    JobStatus.SUCCESS.value,
    JobStatus.FAILED.value,
    JobStatus.CANCELLED.value,
}


class JobHandle:
    """Handle de um job em background, para uso em notebooks.

    Faz polling do banco de jobs (SQLite) e do arquivo de progresso JSON
    associado ao output para expor status/percentual/ETA.
    """

    def __init__(
        self,
        job_id: int,
        *,
        jobs_db: str | None = None,
        repository_factory: Callable[..., JobRepository] | None = None,
    ) -> None:
        self.job_id = job_id
        self._jobs_db = jobs_db
        self._repository_factory = repository_factory

    def _repo(self) -> JobRepository:
        url = self._jobs_db or DEFAULT_JOBS_DB
        return (self._repository_factory or JobRepository)(url)

    def refresh(self) -> dict[str, Any]:
        """Snapshot atual do job (lê DB + arquivo de progresso)."""
        repo = self._repo()
        try:
            job = repo.get(self.job_id)
            if job is None:
                return {
                    "job_id": self.job_id,
                    "status": None,
                    "percent": 0.0,
                    "step": "",
                    "eta": None,
                    "output_path": None,
                    "error": None,
                }
            prog: dict[str, Any] = {}
            if job.output_path:
                prog = read_progress(progress_file_path(Path(job.output_path)))
            return {
                "job_id": self.job_id,
                "status": prog.get("status") or job.status,
                "percent": float(prog.get("percent", job.progress_percent or 0.0)),
                "step": str(prog.get("step") or job.progress_step or ""),
                "eta": prog.get("eta"),
                "output_path": job.output_path,
                "error": prog.get("error") or job.error,
            }
        finally:
            repo.close()

    @property
    def status(self) -> str | None:
        return self.refresh()["status"]

    @property
    def percent(self) -> float:
        return self.refresh()["percent"]

    def wait(
        self,
        *,
        timeout: float | None = None,
        interval: float = 1.0,
    ) -> dict[str, Any]:
        """Aguarda o job terminar (SUCCESS/FAILED/CANCELLED) e retorna o snapshot."""
        elapsed = 0.0
        while True:
            snap = self.refresh()
            if snap["status"] in _FINAL_STATUSES:
                return snap
            if timeout is not None and elapsed >= timeout:
                return snap
            time.sleep(max(0.1, float(interval)))
            elapsed += float(interval)

    def cancel(self) -> str:
        """Cancela o job (SIGTERM ao worker + status CANCELLED)."""
        return execute_jobs_cancel(
            self.job_id,
            jobs_db=self._jobs_db,
            repository_factory=self._repository_factory,
        )

    def __repr__(self) -> str:
        return f"JobHandle(job_id={self.job_id}, status={self.status!r})"


def run_simulation(
    settings: str | Path | None = None,
    *,
    telescope: str = "default",
    constellations: list[str] | None = None,
    include_local_sources: bool = False,
    use_processor: bool = False,
    output: str | Path | None = None,
    background: bool = False,
    jobs_db: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobHandle | str:
    """Executa uma simulação TOD.

    - ``background=False`` (default): roda em foreground e retorna o resumo
      formatado; ``progress_callback`` é chamado com snapshots iniciais/finais.
    - ``background=True``: cria o job, spawna o worker e retorna um
      ``JobHandle`` imediatamente.
    """
    if background:
        job_id = launch_background_export(
            config_path=settings,
            telescope=telescope,
            constellations=constellations,
            include_local_sources=include_local_sources,
            use_processor=use_processor,
            output=output,
            jobs_db=jobs_db,
            stderr=sys.stderr,
        )
        return JobHandle(job_id, jobs_db=jobs_db)

    if progress_callback is not None:
        progress_callback(
            {
                "status": "RUNNING",
                "percent": 0.0,
                "step": "starting",
                "eta": None,
            }
        )
    result = execute_export_tod_command(
        config_path=settings,
        telescope=telescope,
        constellations=constellations,
        include_local_sources=include_local_sources,
        use_processor=use_processor,
        output=output,
        stderr=sys.stderr,
    )
    if progress_callback is not None:
        progress_callback(
            {
                "status": "SUCCESS",
                "percent": 100.0,
                "step": "done",
                "eta": None,
            }
        )
    return result


__all__ = ["JobHandle", "run_simulation"]
