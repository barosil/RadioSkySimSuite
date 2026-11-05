"""\
Módulo: src/radioskysims/interfaces/cli/commands/export_tod.py

Descrição:
    Comando CLI ``tod export`` (ticket TOD-003): roda uma simulação TOD curta
    em foreground usando o ``SimOrchestrator``, grava o dataset
    (HDF5/NetCDF/Zarr) e imprime um resumo.

    O ``--config`` deve apontar para um arquivo de settings completo do
    RadioSkySim (schema com ``[radiotelescopes.<name>]`` e ``[simulations]``),
    como o ``settings.toml`` da raiz. Use ``--telescope`` para escolher o
    perfil.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, TextIO, cast

from radioskysims_core.config.config_loader import resolve_settings_path
from radioskysims_core.db.job_repository import JobRepository, default_jobs_db


def _project_data_dir() -> Path:
    """Diretório ``data`` do projeto (raiz detectada), independente do CWD."""
    from radioskysims_core.paths import get_project_root

    return get_project_root() / "data"  # type: ignore[no-any-return]


DEFAULT_OUTDIR = _project_data_dir() / "TOD"


def _default_output_path() -> Path:
    """Caminho padrão do dataset exportado (raiz do projeto, timestamp UTC)."""
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return DEFAULT_OUTDIR / f"tod_{ts}.nc"


def _resolve_config(config_path: str | Path | None) -> Path | None:
    """Resolve o arquivo de settings, se fornecido."""
    if config_path is None:
        return None
    return cast(Path, resolve_settings_path(config_path))


def format_export_result(output: Path, sidecar: str) -> str:
    """Formata o resultado do comando ``tod export``."""
    return "\n".join(
        [
            "TOD exportado com sucesso",
            f"Dataset: {output}",
            f"Sidecar (JSON): {sidecar}",
        ]
    )


@dataclass(frozen=True)
class ExportResult:
    """Resultado estruturado de ``tod export`` (foreground).

    Substitui o retorno puramente textual por um objeto com os artefatos
    gerados (UX L2); ``str()``/``__repr__`` reproduzem o resumo amigável
    exibido pela CLI.
    """

    output: Path
    sidecar: str
    message: str = "TOD exportado com sucesso"

    def to_text(self) -> str:
        return format_export_result(self.output, self.sidecar)

    def __str__(self) -> str:
        return self.to_text()

    def __repr__(self) -> str:
        return f"ExportResult(output={self.output!s}, message={self.message!r})"


def execute_export_tod_command(
    *,
    config_path: str | Path | None,
    telescope: str,
    constellations: list[str] | None,
    include_local_sources: bool,
    use_processor: bool,
    output: str | Path | None,
    stderr: TextIO,
    orchestrator_factory: Callable[..., Any] | None = None,
) -> ExportResult:
    """Executa ``tod export`` em foreground e retorna o resumo formatado.

    Se ``orchestrator_factory`` for informado (testes/injeção), é usado no
    lugar de ``SimOrchestrator.from_settings``.
    """
    from radioskysims_simulation.application.services.sim_orchestrator import (
        SimOrchestrator,
    )

    cfg = _resolve_config(config_path)

    factory = orchestrator_factory or SimOrchestrator.from_settings
    orchestrator = factory(
        telescope=telescope,
        settings_file=str(cfg) if cfg is not None else None,
    )

    consts = list(constellations) if constellations else []
    
    # T3.2: Se nenhuma fonte é selecionada, usar GPS como padrão
    if not consts and not include_local_sources:
        consts = ["GPS"]
        include_satellites = True
        print(
            "Nenhuma fonte selecionada; usando padrão: GPS (satélites).",
            file=stderr,
        )
    else:
        include_satellites = bool(consts)

    print("Iniciando simulação TOD...", file=stderr)

    result = orchestrator.run(
        constellations=consts,
        include_satellites=include_satellites,
        include_local_sources=include_local_sources,
        use_processor=use_processor,
    )

    out_path = Path(output) if output else _default_output_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar = result.save_result(str(out_path))

    print(f"TOD gravado em: {out_path}", file=stderr)
    return ExportResult(output=out_path, sidecar=sidecar)


def _resolve_jobs_db_url(jobs_db: str | None) -> str:
    """Resolve a URL do banco de jobs, criando o diretório se for SQLite em arquivo."""
    url = jobs_db or default_jobs_db()
    if url.startswith("sqlite:///"):
        Path(url[len("sqlite:///") :]).parent.mkdir(parents=True, exist_ok=True)
    return url


def launch_background_export(
    *,
    config_path: str | Path | None,
    telescope: str,
    constellations: list[str] | None,
    include_local_sources: bool,
    use_processor: bool,
    output: str | Path | None,
    jobs_db: str | None = None,
    stderr: TextIO,
    repository_factory: Callable[..., JobRepository] | None = None,
    popen_factory: Callable[..., Any] | None = None,
) -> int:
    """Cria um job e spawna o worker em background; retorna o id do job.

    O worker (``export_worker``) roda a mesma exportação em foreground e
    atualiza o banco (RUNNING → SUCCESS/FAILED) além de gravar o arquivo de
    progresso. O log do subprocesso vai para ``<output>.log``.
    """
    url = _resolve_jobs_db_url(jobs_db)
    repo = (repository_factory or JobRepository)(url)
    try:
        cfg = _resolve_config(config_path)
        out_path = Path(output) if output else _default_output_path()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        job = repo.create(name="tod export", config_path=cfg)
        log_path = out_path.with_suffix(out_path.suffix + ".log")

        cmd = [
            sys.executable,
            "-m",
            "radioskysims.interfaces.cli.commands.export_worker",
            "--job-id",
            str(job.id),
            "--jobs-db",
            url,
            "--telescope",
            telescope,
            "--output",
            str(out_path),
        ]
        if cfg is not None:
            cmd += ["--config", str(cfg)]
        if constellations:
            cmd += ["--constellations", *constellations]
        if include_local_sources:
            cmd += ["--local-sources"]
        if use_processor:
            cmd += ["--use-processor"]

        with open(log_path, "wb") as log:
            popen = (popen_factory or subprocess.Popen)(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        repo.set_pid(job.id, popen.pid)

        print(
            f"Job {job.id} iniciado em background (pid={popen.pid}).",
            file=stderr,
        )
        return int(job.id)
    finally:
        repo.close()


__all__ = [
    "DEFAULT_OUTDIR",
    "ExportResult",
    "execute_export_tod_command",
    "format_export_result",
    "launch_background_export",
]
