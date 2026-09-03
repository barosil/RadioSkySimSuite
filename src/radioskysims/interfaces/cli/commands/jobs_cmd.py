"""\
Módulo: src/radioskysims/interfaces/cli/commands/jobs_cmd.py

Descrição:
    Comandos de gerenciamento de jobs (ticket TOD-005):
    ``radioskysims tod jobs list|status|cancel``. Operam sobre o banco
    SQLite de jobs (``JobRepository``); ``cancel`` sinaliza o worker
    (SIGTERM via process group) e grava o status CANCELLED.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import os
import signal
import time
from pathlib import Path
from typing import Any, Callable, TextIO

from radioskysims_core.db.job_repository import JobRepository, default_jobs_db
from radioskysims_core.db.jobs import Job, JobStatus

from radioskysims.interfaces.cli.commands.progress import (
    progress_file_path,
    read_progress,
)

_FINAL_STATUSES = {
    JobStatus.SUCCESS.value,
    JobStatus.FAILED.value,
    JobStatus.CANCELLED.value,
}


def _repo_for(
    jobs_db: str | None,
    repository_factory: Callable[..., JobRepository] | None,
) -> JobRepository:
    """Instancia o repositório (injetável em testes)."""
    url = jobs_db or default_jobs_db()
    return (repository_factory or JobRepository)(url)


def _format_job_row(job: Job) -> str:
    """Formata uma linha da listagem de jobs."""
    ts = job.updated_at.strftime("%Y-%m-%d %H:%M:%S") if job.updated_at else "-"
    return f"{job.id}\t{job.status}\t{job.progress_percent:.0f}%\t{job.name}\t{ts}"


def execute_jobs_list(
    *,
    jobs_db: str | None = None,
    repository_factory: Callable[..., JobRepository] | None = None,
) -> str:
    """Lista os jobs (mais recentes primeiro)."""
    repo = _repo_for(jobs_db, repository_factory)
    try:
        jobs = repo.list()
        if not jobs:
            return "Nenhum job encontrado."
        lines = ["ID\tSTATUS\tPROG\tNOME\tATUALIZADO"]
        lines.extend(_format_job_row(job) for job in jobs)
        return "\n".join(lines)
    finally:
        repo.close()


def execute_jobs_status(
    job_id: int,
    *,
    jobs_db: str | None = None,
    repository_factory: Callable[..., JobRepository] | None = None,
) -> str:
    """Exibe o detalhe de um job."""
    repo = _repo_for(jobs_db, repository_factory)
    try:
        job = repo.get(job_id)
        if job is None:
            return f"Job {job_id} não encontrado."
        return "\n".join(
            [
                f"ID: {job.id}",
                f"Nome: {job.name}",
                f"Status: {job.status}",
                f"Progresso: {job.progress_percent:.0f}% ({job.progress_step})",
                f"Output: {job.output_path or '-'}",
                f"PID: {job.pid or '-'}",
                f"Criado: {job.created_at}",
                f"Atualizado: {job.updated_at}",
                f"Erro: {job.error or '-'}",
            ]
        )
    finally:
        repo.close()


def execute_jobs_cancel(
    job_id: int,
    *,
    jobs_db: str | None = None,
    repository_factory: Callable[..., JobRepository] | None = None,
) -> str:
    """Cancela um job em PENDING/RUNNING (SIGTERM ao worker) e grava CANCELLED."""
    repo = _repo_for(jobs_db, repository_factory)
    try:
        job = repo.get(job_id)
        if job is None:
            return f"Job {job_id} não encontrado."
        if job.status in _FINAL_STATUSES:
            return f"Job {job_id} já está em {job.status}; cancelamento ignorado."

        repo.update_status(job_id, JobStatus.CANCELLED)

        pid = job.pid
        if pid is not None:
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                return f"Job {job_id} marcado como CANCELLED (worker já encerrado)."
            return f"Job {job_id} cancelado (SIGTERM enviado ao pid {pid})."
        return f"Job {job_id} marcado como CANCELLED (sem worker ativo)."
    finally:
        repo.close()


def _render_progress(job: Job, prog: dict[str, Any]) -> str:
    """Renderiza a barra de progresso de um job (arquivo + DB)."""
    percent = float(prog.get("percent", job.progress_percent or 0.0))
    step = str(prog.get("step") or job.progress_step or "-")
    eta = str(prog.get("eta") or "-")
    status = str(prog.get("status") or job.status)

    width = 30
    filled = int(round(max(0.0, min(100.0, percent)) / 100.0 * width))
    bar = "#" * filled + "-" * (width - filled)

    lines = [
        f"Job {job.id} [{status}]",
        f"|{bar}| {percent:.0f}%",
        f"Etapa: {step}",
        f"ETA: {eta}",
    ]
    if job.error:
        lines.append(f"Erro: {job.error}")
    return "\n".join(lines)


def execute_jobs_monitor(
    job_id: int,
    *,
    jobs_db: str | None = None,
    repository_factory: Callable[..., JobRepository] | None = None,
    watch: bool = False,
    interval: float = 2.0,
    stdout: TextIO,
) -> int:
    """Exibe o progresso de um job; com ``watch``, segue até concluir."""
    repo = _repo_for(jobs_db, repository_factory)
    try:
        while True:
            job = repo.get(job_id)
            if job is None:
                print(f"Job {job_id} não encontrado.", file=stdout)
                return 1
            if not job.output_path:
                print(
                    f"Job {job_id} sem output definido ainda (aguarde o worker).",
                    file=stdout,
                )
                return 1

            print(
                _render_progress(
                    job,
                    read_progress(progress_file_path(Path(job.output_path))),
                ),
                file=stdout,
            )
            if not watch or job.status in _FINAL_STATUSES:
                return 0
            time.sleep(max(0.1, float(interval)))
    finally:
        repo.close()


__all__ = [
    "execute_jobs_cancel",
    "execute_jobs_list",
    "execute_jobs_monitor",
    "execute_jobs_status",
]
