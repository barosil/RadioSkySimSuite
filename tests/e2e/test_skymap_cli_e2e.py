from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import healpy as hp
import numpy as np
import pytest

# O fluxo e2e assume stderr vazio; sem asyncpg o bootstrap emite warning no
# stderr (DB async não é criado). asyncpg NÃO é dependência declarada do
# projeto — o teste integra apenas quando o driver está disponível.
pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("asyncpg") is None,
    reason="asyncpg não disponível; DB async engine não é criado (warning no stderr).",
)


@pytest.mark.integration
def test_skymap_analyze_cli_end_to_end(
    tmp_path: Path,
) -> None:
    """Valida o fluxo completo de análise pela CLI instalada.

    O teste:

    1. cria um mapa HEALPix determinístico;
    2. grava o mapa em FITS;
    3. executa o comando real ``radioskysims``;
    4. interpreta a saída JSON;
    5. valida os principais resultados científicos e estruturais.
    """

    # Prioriza o script da MESMA env do teste (evita script stale de outra env,
    # ex.: /opt/miniforge/bin/radioskysims apontando para outro ambiente).
    # Usa sys.prefix (raiz do venv, sem seguir symlink de bin/python → base).
    candidates = [
        Path(sys.prefix) / "bin" / "radioskysims",
        Path(shutil.which("radioskysims") or ""),
    ]
    executable = next((str(p) for p in candidates if p.is_file()), None)

    assert executable is not None, (
        "O executável 'radioskysims' não foi encontrado. "
        "Instale o projeto com 'python -m pip install -e .'."
    )

    nside = 8
    npix = hp.nside2npix(nside)
    lmax = 8

    pixel_indices = np.arange(
        npix,
        dtype=np.int64,
    )

    theta, phi = hp.pix2ang(
        nside,
        pixel_indices,
    )

    map_data = (2.0 + np.cos(theta) + 0.25 * np.sin(theta) * np.cos(phi)).astype(
        np.float64,
    )

    input_path = tmp_path / "e2e_skymap.fits"

    hp.write_map(
        input_path,
        map_data,
        overwrite=True,
        dtype=np.float64,
        coord="G",
        column_units="uK_CMB",
    )

    assert input_path.is_file()
    assert input_path.stat().st_size > 0

    process = subprocess.run(
        [
            executable,
            "skymap",
            "analyze",
            "--input",
            str(input_path),
            "--lmax",
            str(lmax),
            "--unit",
            "uK_CMB",
            "--frame",
            "galactic",
            "--field",
            "I",
            "--output-format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert process.returncode == 0, (
        f"A CLI retornou erro.\nstdout:\n{process.stdout}\nstderr:\n{process.stderr}"
    )

    assert process.stderr == ""

    payload = json.loads(process.stdout)

    assert payload["status"] == "success"
    assert payload["command"] == "skymap.analyze"

    assert payload["input"] == str(input_path)
    assert payload["nside"] == nside
    assert payload["npix"] == npix

    assert payload["unit"] == "uK_CMB"
    assert payload["frame"] == "galactic"
    assert payload["field"] == "I"

    assert payload["lmax"] == lmax
    assert payload["cls_length"] == lmax + 1
    assert payload["dtype"] == "float64"

    assert payload["cls_min"] is not None
    assert payload["cls_max"] is not None
    assert payload["cls_mean"] is not None

    assert np.isfinite(payload["cls_min"])
    assert np.isfinite(payload["cls_max"])
    assert np.isfinite(payload["cls_mean"])

    assert payload["cls_min"] >= 0.0
    assert payload["cls_max"] >= payload["cls_min"]
