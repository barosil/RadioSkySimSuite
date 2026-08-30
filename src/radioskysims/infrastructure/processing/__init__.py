"""
Módulo: src/radioskysims/infrastructure/processing/__init__.py

Componentes de processamento consciente de recursos.

Copyright BINGO Collaboration
Last modified: 2026-07-28
"""

from __future__ import annotations

from radioskysims_simulation.infrastructure.processing.resource_processor import (
    MemoryEstimator,
    ProcessingResources,
    ResourceAwareProcessor,
    ResourceLimitError,
    SourceBatch,
)

__all__ = [
    "MemoryEstimator",
    "ProcessingResources",
    "ResourceAwareProcessor",
    "ResourceLimitError",
    "SourceBatch",
]
