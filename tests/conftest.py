# tests/conftest.py
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
GNSS_SRC = SRC_PATH / "GNSStools4Astro"

for _p in (SRC_PATH, GNSS_SRC):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

_SAMPLE = GNSS_SRC / "RinexDownloader" / "data" / "braz_20240610"


@pytest.fixture(scope="session")
def sample_dir() -> Path:
    """Diretório com os arquivos RINEX de exemplo (estação braz, 2024-06-10)."""
    if not _SAMPLE.exists():
        pytest.skip("dados de exemplo não encontrados")
    return _SAMPLE


@pytest.fixture(scope="session")
def gps_nav(sample_dir: Path) -> Path:
    return sample_dir / "braz1621.24n"


@pytest.fixture(scope="session")
def galileo_nav(sample_dir: Path) -> Path:
    return sample_dir / "braz1621.24l"


@pytest.fixture(scope="session")
def glonass_nav(sample_dir: Path) -> Path:
    return sample_dir / "braz1621.24g"


@pytest.fixture(scope="session")
def obs_file(sample_dir: Path) -> Path:
    return sample_dir / "braz1621.24d"


def pytest_configure(config):
    _ = (config)  # assinala uso (interface/reservado)
    # Ignora apenas DeprecationWarning originado do PySM3
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module=r"pysm3.*",
    )
    # Ignora DeprecationWarning do numpy.core (renomeado para numpy._core no NumPy 2.x)
    # causado por xarray e healpy em ambientes com NumPy >= 2.0
    warnings.filterwarnings(
        "ignore",
        message=r"numpy\.core\.",
        category=DeprecationWarning,
    )
    # Recursos não fechados de libs de terceiros (Skyfield .bsp, openpyxl) geram
    # ResourceWarning no __del__ — promovidos a erro por filterwarnings=error.
    warnings.filterwarnings(
        "ignore",
        category=pytest.PytestUnraisableExceptionWarning,
    )


def pytest_collection_modifyitems(config, items):
    # Testes de performance não rodam por padrão (rode com: -m performance)
    expr = (config.getoption("-m") or "").strip()
    for item in items:
        if item.get_closest_marker("performance") and expr != "performance":
            item.add_marker(
                pytest.mark.skip(reason="teste de performance (rode com -m performance)")
            )
