"""
Interfaces de usuário para RadioSkySim.

Inclui CLI, API REST, e GUI.
"""

from __future__ import annotations

from radioskysims_skymap.infrastructure.skymap.providers.pysm import (
    PySMSkyMapGeneratorAdapter,
)

__all__ = [
    "PySMSkyMapGeneratorAdapter",
]
