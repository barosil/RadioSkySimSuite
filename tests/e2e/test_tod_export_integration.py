"""\
Teste: tests/e2e/test_tod_export_integration.py

Descrição:
    Integração curta do fluxo ``tod export`` (ticket TOD-008): executa a CLI
    real (parser → dispatch → execute_export_tod_command → save_result),
    substituindo apenas o orquestrador (dependência externa) por um fake.
    Não depende de Postgres/rede.

Copyright BINGO Collaboration
Last modified: 2026-08-30
"""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from radioskysims_simulation.application.services import sim_orchestrator

from radioskysims.interfaces.cli.main import SkyMapCLIUseCases, run


class FakeResult:
    """Resultado fake que cria o dataset no save_result."""

    def save_result(self, filepath: str, *args: object, **kwargs: object) -> str:
        _ = (args, kwargs)
        out = Path(filepath)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.touch()
        return str(out) + ".json"


@pytest.mark.integration
def test_tod_export_foreground_integration(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Pipeline real do ``tod export`` com orquestrador fake."""
    captured: dict[str, object] = {}

    class FakeOrchestrator:
        def __init__(
            self,
            *,
            telescope: str,
            settings_file: str | None = None,
        ) -> None:
            captured["telescope"] = telescope
            captured["settings_file"] = settings_file

        def run(self, **kwargs: object) -> FakeResult:
            captured["run_kwargs"] = kwargs
            return FakeResult()

    monkeypatch.setattr(
        sim_orchestrator.SimOrchestrator,
        "from_settings",
        FakeOrchestrator,
    )

    out = tmp_path / "int" / "tod.nc"
    stdout = StringIO()
    stderr = StringIO()

    code = run(
        [
            "tod",
            "export",
            "--config",
            "settings.toml",
            "--telescope",
            "uirapuru",
            "--local-sources",
            "--output",
            str(out),
        ],
        use_cases=SkyMapCLIUseCases(generate_skymap=object()),
        stdout=stdout,
        stderr=stderr,
    )

    assert code == 0
    assert captured["telescope"] == "uirapuru"
    assert captured["settings_file"] is not None
    run_kwargs = captured["run_kwargs"]
    assert isinstance(run_kwargs, dict)
    assert run_kwargs["include_local_sources"] is True
    assert run_kwargs["include_satellites"] is False
    assert out.exists()
    assert "TOD exportado com sucesso" in stdout.getvalue()
