"""Builders de componentes — composition root (Fase 5).

Este módulo passou a ser fino: delega os builders para os pacotes
(strategy pattern). Importe diretamente dos pacotes quando possível.
"""

from __future__ import annotations

from radioskysims_beam.bootstrap.builders import _load_beam_from_csv  # noqa: F401
from radioskysims_core.bootstrap.builders import (  # noqa: F401
    build_database,
    build_logging,
)
from radioskysims_radiotelescope.bootstrap.builders import build_configuration  # noqa: F401
from radioskysims_simulation.bootstrap.builders import (  # noqa: F401
    build_domain_components,
    build_services,
    build_simulation_context_dependencies,
    build_skymap_components,
)
from radioskysims_sources.bootstrap.builders import (  # noqa: F401
    build_cosmology_components,
    build_local_sources_service,
    build_radiosources_use_cases,
    build_repositories,
)
