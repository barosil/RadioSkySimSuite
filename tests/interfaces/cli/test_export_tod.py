"""Testes do comando CLI ``tod export`` (ticket TOD-003)."""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from radioskysims.interfaces.cli.main import (
    SkyMapCLIUseCases,
    build_parser,
    run,
)


class FakeResult:
    """Resultado fake com ``save_result`` que cria o arquivo."""

    def __init__(self) -> None:
        self.saved_path: str | None = None

    def save_result(
        self,
        filepath: str,
        *,
        fmt: str | None = None,
        **kwargs: object,
    ) -> str:
        _ = (fmt, kwargs)
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        self.saved_path = str(path)
        return str(path) + ".json"


class FakeOrchestrator:
    """Orquestrador fake que registra os kwargs de ``run``."""

    def __init__(self) -> None:
        self.run_kwargs: dict[str, object] | None = None

    def run(self, **kwargs: object) -> FakeResult:
        self.run_kwargs = kwargs
        return FakeResult()


def _factory_with(orch: FakeOrchestrator) -> object:
    """Factory fake com a assinatura de ``SimOrchestrator.from_settings``."""

    def factory(
        *,
        telescope: str,
        settings_file: str | None = None,
    ) -> FakeOrchestrator:
        _ = (telescope, settings_file)
        return orch

    return factory


def test_build_parser_export() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "tod",
            "export",
            "--telescope",
            "uirapuru",
            "--constellations",
            "GPS",
            "GALILEO",
            "--local-sources",
            "--output",
            "out.nc",
            "--use-processor",
        ]
    )
    assert args.context == "tod"
    assert args.tod_command == "export"
    assert args.telescope == "uirapuru"
    assert args.constellations == ["GPS", "GALILEO"]
    assert args.local_sources is True
    assert args.use_processor is True
    assert args.output == Path("out.nc")


def test_build_parser_export_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["tod", "export"])
    assert args.config is None
    assert args.telescope == "default"
    assert args.constellations is None
    assert args.local_sources is False
    assert args.output is None
    assert args.use_processor is False


def test_execute_export_tod_command(
    tmp_path,
) -> None:
    from radioskysims.interfaces.cli.commands.export_tod import (
        ExportResult,
        execute_export_tod_command,
    )

    orch = FakeOrchestrator()
    out = tmp_path / "tod_out.nc"
    stderr = StringIO()

    result = execute_export_tod_command(
        config_path=None,
        telescope="uirapuru",
        constellations=["GPS"],
        include_local_sources=True,
        use_processor=True,
        output=out,
        stderr=stderr,
        orchestrator_factory=_factory_with(orch),
    )

    assert orch.run_kwargs is not None
    assert orch.run_kwargs["constellations"] == ["GPS"]
    assert orch.run_kwargs["include_satellites"] is True
    assert orch.run_kwargs["include_local_sources"] is True
    assert orch.run_kwargs["use_processor"] is True

    assert out.exists()
    assert isinstance(result, ExportResult)
    assert result.output == out
    assert "TOD exportado com sucesso" in str(result)
    assert str(out) in str(result)
    assert "TOD gravado em" in stderr.getvalue()


def test_execute_export_no_satellites_when_no_constellations(
    tmp_path,
) -> None:
    from radioskysims.interfaces.cli.commands.export_tod import (
        execute_export_tod_command,
    )

    orch = FakeOrchestrator()
    out = tmp_path / "tod_local.nc"

    execute_export_tod_command(
        config_path=None,
        telescope="uirapuru",
        constellations=None,
        include_local_sources=True,
        use_processor=False,
        output=out,
        stderr=StringIO(),
        orchestrator_factory=_factory_with(orch),
    )

    assert orch.run_kwargs is not None
    assert orch.run_kwargs["constellations"] == []
    assert orch.run_kwargs["include_satellites"] is False


def test_run_tod_export(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.cli.main as main

    captured: dict[str, object] = {}

    def fake_command(**kwargs: object) -> str:
        captured.update(kwargs)
        return "OK TOD"

    monkeypatch.setattr(
        main,
        "execute_export_tod_command",
        fake_command,
    )

    stdout = StringIO()
    stderr = StringIO()

    exit_code = run(
        ["tod", "export", "--telescope", "uirapuru"],
        use_cases=SkyMapCLIUseCases(generate_skymap=object()),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert captured["telescope"] == "uirapuru"
    assert captured["include_local_sources"] is False
    assert "OK TOD" in stdout.getvalue()


def test_run_tod_export_unknown_context(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.cli.main as main

    monkeypatch.setattr(
        main,
        "execute_export_tod_command",
        lambda **_kwargs: "never",
    )

    stdout = StringIO()
    stderr = StringIO()

    with pytest.raises(SystemExit):
        run(
            ["tod", "unknown"],
            use_cases=SkyMapCLIUseCases(generate_skymap=object()),
            stdout=stdout,
            stderr=stderr,
        )


class FakeJobRepo:
    """Repositório fake para o launcher de background."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.created: tuple[str, str | None] | None = None

    def create(self, *, name: str, config_path: str | None = None) -> SimpleNamespace:
        self.created = (name, str(config_path) if config_path else None)
        return SimpleNamespace(id=7)

    def set_pid(self, job_id: int, pid: int | None) -> None:
        self.pid_set = (job_id, pid)

    def close(self) -> None:
        pass


def test_build_parser_export_background() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "tod",
            "export",
            "--background",
            "--jobs-db",
            "sqlite:///tmp/x.db",
        ]
    )
    assert args.background is True
    assert args.jobs_db == "sqlite:///tmp/x.db"


def test_launch_background_export(
    tmp_path,
) -> None:
    from radioskysims.interfaces.cli.commands import export_tod

    db = tmp_path / "jobs.db"
    out = tmp_path / "bg" / "tod_bg.nc"
    repo = FakeJobRepo(f"sqlite:///{db}")
    launched: dict[str, object] = {}

    def fake_popen(cmd: list[str], **kwargs: object) -> SimpleNamespace:
        _ = (kwargs,)
        launched["cmd"] = cmd
        return SimpleNamespace(pid=4242)

    stderr = StringIO()
    job_id = export_tod.launch_background_export(
        config_path=None,
        telescope="uirapuru",
        constellations=["GPS"],
        include_local_sources=True,
        use_processor=True,
        output=out,
        jobs_db=f"sqlite:///{db}",
        stderr=stderr,
        repository_factory=lambda _url: repo,
        popen_factory=fake_popen,
    )

    assert job_id == 7
    assert repo.created == ("tod export", None)
    assert repo.pid_set == (7, 4242)
    assert db.parent.exists()
    assert out.parent.exists()
    assert "Job 7 iniciado em background" in stderr.getvalue()

    cmd = launched["cmd"]
    assert cmd[0] == sys.executable
    assert "-m" in cmd
    assert "radioskysims.interfaces.cli.commands.export_worker" in cmd
    assert "--job-id" in cmd and "7" in cmd
    assert "--telescope" in cmd and "uirapuru" in cmd
    assert "--constellations" in cmd and "GPS" in cmd
    assert "--local-sources" in cmd
    assert "--use-processor" in cmd
    assert str(out) in cmd


def test_launch_background_export_with_config(
    tmp_path,
) -> None:
    from radioskysims.interfaces.cli.commands import export_tod

    cfg = tmp_path / "settings.toml"
    cfg.write_text("[radiotelescopes]\n")
    db = tmp_path / "jobs.db"
    repo = FakeJobRepo(f"sqlite:///{db}")
    launched: dict[str, object] = {}

    def fake_popen(cmd: list[str], **kwargs: object) -> SimpleNamespace:
        _ = (kwargs,)
        launched["cmd"] = cmd
        return SimpleNamespace(pid=1)

    job_id = export_tod.launch_background_export(
        config_path=cfg,
        telescope="default",
        constellations=None,
        include_local_sources=False,
        use_processor=False,
        output=None,
        jobs_db=f"sqlite:///{db}",
        stderr=StringIO(),
        repository_factory=lambda _url: repo,
        popen_factory=fake_popen,
    )

    assert job_id == 7
    assert repo.created == ("tod export", str(cfg))
    cmd = launched["cmd"]
    assert "--config" in cmd and str(cfg) in cmd
    assert "--constellations" not in cmd
    assert "--local-sources" not in cmd
    assert "--use-processor" not in cmd


def test_run_tod_export_background(
    monkeypatch,
) -> None:
    import radioskysims.interfaces.cli.main as main

    captured: dict[str, object] = {}

    def fake_launch(**kwargs: object) -> int:
        captured.update(kwargs)
        return 99

    monkeypatch.setattr(main, "launch_background_export", fake_launch)

    stdout = StringIO()
    stderr = StringIO()
    exit_code = run(
        [
            "tod",
            "export",
            "--background",
            "--telescope",
            "uirapuru",
            "--jobs-db",
            "sqlite://",
        ],
        use_cases=SkyMapCLIUseCases(generate_skymap=object()),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert captured["telescope"] == "uirapuru"
    assert captured["jobs_db"] == "sqlite://"
    assert "Job 99 criado" in stdout.getvalue()
