"""
Módulo: src/radioskysims/visualization/__init__.py

Interface de visualização para resultados de simulação TOD.

Copyright BINGO Collaboration
Last modified: 2026-08-03
"""

from __future__ import annotations

from .waterfall import (
    events_overlay,
    events_spans,
    interactive_waterfall,
    multi_source_waterfall,
    reindex_events_to_grid,
    serve_interactive_waterfall,
    serve_tod_panel,
    stop_waterfall_servers,
    time_series_plot,
    tod_panel,
    waterfall_plot,
)

__all__ = [
    "events_overlay",
    "events_spans",
    "interactive_waterfall",
    "multi_source_waterfall",
    "reindex_events_to_grid",
    "serve_interactive_waterfall",
    "serve_tod_panel",
    "stop_waterfall_servers",
    "time_series_plot",
    "tod_panel",
    "waterfall_plot",
]
