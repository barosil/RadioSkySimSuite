"""Modelos de infraestrutura de banco de dados - alias para fácil importação.

Este módulo expõe os principais modelos SQLModel usados na camada de
infraestrutura, permitindo imports mais concisos em outras partes do
projeto.
"""

from __future__ import annotations

from radioskysims_beam.infrastructure.db.beam_db_model import BeamParamsDB
from radioskysims_simulation.infrastructure.db.simulation_db_model import SimulationRecord
from radioskysims_sources.infrastructure.db.radiosources_db_model import RadioSourceDB
from radioskysims_sources.infrastructure.db.satellite.models import OrbitalElement, SatID

__all__ = [
    "BeamParamsDB",
    "OrbitalElement",
    "RadioSourceDB",
    "SatID",
    "SimulationRecord",
]
