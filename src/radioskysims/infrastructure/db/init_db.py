"""
Módulo: src/radioskysims/infrastructure/db/init_db.py

Descrição:
    Inicializa o banco de dados criando todas as tabelas dos modelos SQLModel
    do projeto (schema). Importa explicitamente todos os modelos para que eles
    sejam registrados no ``SQLModel.metadata`` — sem esses imports o
    ``create_all`` criaria um banco vazio.

    Usa o engine síncrono (``Database``/psycopg2), driver que é dependência do
    projeto. O driver assíncrono (asyncpg) não é instalado neste ambiente.

Copyright BINGO Collaboration
Last modified: 2026-08-15

Uso:
    .venv/bin/python -m radioskysims.infrastructure.db.init_db
"""

from __future__ import annotations

import logging

from radioskysims_core.db import jobs as _jobs  # noqa: F401  (tabela ``jobs``, TOD-002)
from radioskysims_core.db.engine import Database
from radioskysims_skymap.infrastructure.db import skymap_models  # noqa: F401
from radioskysims_sources.infrastructure.db import solar_flux_db_model  # noqa: F401
from radioskysims_sources.infrastructure.db.satellite import (
    models as satellite_models,  # noqa: F401
)
from sqlmodel import SQLModel

# Importa TODOS os modelos SQLModel (registra no SQLModel.metadata).
# O `models` agrega beam, radiosources, satellite (SatID/OrbitalElement) e
# simulação; os demais módulos são importados explicitamente.
from . import models  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Cria todas as tabelas dos modelos SQLModel no banco (engine síncrono)."""
    db = Database()
    SQLModel.metadata.create_all(db.engine)
    tables = sorted(SQLModel.metadata.tables)
    logger.info("Tabelas criadas com sucesso: %s", tables)
    print(f"✅ Tabelas criadas ({len(tables)}): {tables}")


if __name__ == "__main__":
    init_db()
