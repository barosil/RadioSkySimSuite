"""\
Módulo: src/radioskysims/interfaces/cli/commands/export_worker.py

Descrição:
    Entry point (subprocess) do comando ``tod export --background``
    (ticket TOD-004). Roda a exportação em foreground dentro do worker,
    atualiza o job no banco (SQLite) e grava um arquivo de progresso JSON
    (formato preliminar do TOD-006: ``{status, percent, step}``).

    Invocado via ``python -m radioskysims.interfaces.cli.commands.export_worker``
    pelo launcher ``launch_background_export``.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from radioskysims_core.db.job_repository import JobRepository, default_jobs_db
from radioskysims_core.db.jobs import JobStatus

from radioskysims.interfaces.cli.commands.export_tod import (
    _default_output_path,
    execute_export_tod_command,
)
from radioskysims.interfaces.cli.commands.progress import (
    progress_file_path,
    write_progress,
)


def build_worker_parser() -> argparse.ArgumentParser:
    """Parser de argumentos do worker (espelho do ``tod export``)."""
    parser = argparse.ArgumentParser(prog="radioskysims-export-worker")
    parser.add_argument("--job-id", type=int, required=True)
    parser.add_argument("--jobs-db", default=None, help="URL do banco de jobs.")
    parser.add_argument("--config", default=None, help="Arquivo de settings.")
    parser.add_argument("--telescope", default="default")
    parser.add_argument("--constellations", nargs="*", default=None)
    parser.add_argument("--local-sources", action="store_true")
    parser.add_argument("--use-processor", action="store_true")
    parser.add_argument("--output", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Executa o worker e atualiza o job (RUNNING → SUCCESS/FAILED)."""
    args = build_worker_parser().parse_args(argv)
    repo = JobRepository(args.jobs_db or default_jobs_db())
    out_path = Path(args.output) if args.output else _default_output_path()
    started_at = time.monotonic()
    try:
        repo.update_status(
            args.job_id,
            JobStatus.RUNNING,
            output_path=str(out_path),
        )
        progress_path = progress_file_path(out_path)
        write_progress(
            progress_path,
            status="RUNNING",
            percent=0.0,
            step="starting",
            started_at=started_at,
        )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_progress(
            progress_path,
            status="RUNNING",
            percent=5.0,
            step="simulação iniciada",
            started_at=started_at,
        )
        repo.update_progress(
            args.job_id,
            percent=5.0,
            step="simulação iniciada",
        )

        execute_export_tod_command(
            config_path=args.config,
            telescope=args.telescope,
            constellations=args.constellations,
            include_local_sources=args.local_sources,
            use_processor=args.use_processor,
            output=out_path,
            stderr=sys.stderr,
        )

        repo.update_status(
            args.job_id,
            JobStatus.SUCCESS,
            output_path=str(out_path),
        )
        write_progress(
            progress_path,
            status="SUCCESS",
            percent=100.0,
            step="done",
            started_at=started_at,
        )
        return 0
    except Exception as exc:
        msg = f"{type(exc).__name__}: {exc}"
        repo.update_status(args.job_id, JobStatus.FAILED, error=msg)
        write_progress(
            progress_file_path(out_path),
            status="FAILED",
            percent=100.0,
            step="failed",
            started_at=started_at,
            error=msg,
        )
        print(msg, file=sys.stderr)
        return 1
    finally:
        repo.close()


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "build_worker_parser",
    "main",
    "progress_file_path",
]
