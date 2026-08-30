"""
Módulo: src/radioskysims/main.py

Descrição:
    Ponto de entrada principal da aplicação RadioSkySim.
    Inicializa serviços, conexões de banco de dados e interface gráfica.
"""

# main.py
from __future__ import annotations

from sqlmodel import Session, create_engine

from radioskysims_sources.application.services.satellite_manager import SatelliteManager
from radioskysims_sources.domain.satellite.factory import SatelliteFactory
from radioskysims_sources.infrastructure.db.satellite import SatelliteRepository
from radioskysims_sources.infrastructure.external.satellite_downloader import (
    SpaceTrackClient,
)
from radioskysims_sources.interfaces.gui.satellite_panel import SatellitePanel


def main() -> None:
    """
    Inicializa e executa a aplicação RadioSkySim.

    Configura:
    - Conexão com banco de dados (SQLite ou PostgreSQL)
    - Repositórios de dados
    - Clientes de serviços externos (SpaceTrack)
    - Fábricas e gerenciadores de domínio
    - Interface gráfica (Panel)

    Raises:
        ConnectionError: Se não conseguir conectar ao banco de dados.
        AuthenticationError: Se credenciais do SpaceTrack forem inválidas.
    """
    engine = create_engine("sqlite:///db.db")  # ou PostgreSQL
    session = Session(engine)

    repo = SatelliteRepository(session)
    spacetrack = SpaceTrackClient()
    factory = SatelliteFactory(repository=repo, spacetrack_client=spacetrack)
    SatelliteManager(factory=factory)

    panel_app = SatellitePanel(factory)
    panel_app.show().servable()


if __name__ == "__main__":
    main()
