"""
Módulo: tests/infrastructure/ports/test_port_contracts.py

Descrição:
    Testes de contrato para os ports de infraestrutura.
    Verifica que as abstrações (ABC) estão corretamente definidas e que
    implementações concretas respeitam os contratos estabelecidos.

Copyright BINGO Collaboration
Last modified: 2026-02-26
"""

from __future__ import annotations

import inspect
from abc import ABC
from typing import Any

import numpy as np
import pytest
import xarray as xr
from radioskysims_beam.application.ports.beam import (
    BeamLoaderPort,
)
from radioskysims_beam.domain.beam.models import Beam
from radioskysims_core.application.ports.geometry import GeometryProviderPort

# SkyMap ports require healpy → astropy; skip if not available in this env.
try:
    from radioskysims_skymap.infrastructure.ports.skymap import (
        SkyMapIOPort,
        SkyMapTransformPort,
    )

    _skymap_ports_available = True
except (ImportError, AttributeError):
    _skymap_ports_available = False
    SkyMapIOPort = None  # type: ignore[assignment,misc]
    SkyMapTransformPort = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _abstract_methods(cls: type) -> set[str]:
    """Return names of all abstract methods defined on *cls*."""
    return {
        name
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction)
        if getattr(method, "__isabstractmethod__", False)
    }


def _make_minimal_beam() -> Beam:
    """Create a minimal valid Beam for testing."""
    angles = np.linspace(0, np.pi / 2, 10)
    frequencies = [1.0e8, 2.0e8]
    polarizations = ["H"]
    amp = np.ones((len(polarizations), len(frequencies), len(angles)))
    ds = xr.Dataset(
        {"amplitude": (["polarization", "frequency", "angle"], amp)},
        coords={
            "polarization": polarizations,
            "frequency": frequencies,
            "angle": angles,
        },
    )
    return Beam(ds)


# ---------------------------------------------------------------------------
# BeamLoaderPort contract
# ---------------------------------------------------------------------------


class TestBeamLoaderPortContract:
    """Verifica que BeamLoaderPort define o contrato correto."""

    def test_is_abstract(self) -> None:
        assert issubclass(BeamLoaderPort, ABC)

    def test_has_load_method(self) -> None:
        assert "load" in _abstract_methods(BeamLoaderPort)

    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            BeamLoaderPort()  # type: ignore[abstract]

    def test_concrete_subclass_must_implement_load(self) -> None:
        class IncompleteLoader(BeamLoaderPort):
            pass

        with pytest.raises(TypeError):
            IncompleteLoader()  # type: ignore[abstract]

    def test_concrete_subclass_with_load_instantiates(self) -> None:
        class MinimalLoader(BeamLoaderPort):
            def load(self) -> Beam:
                return _make_minimal_beam()

        loader = MinimalLoader()
        result = loader.load()
        assert isinstance(result, Beam)


# ---------------------------------------------------------------------------
# GeometryProviderPort contract
# ---------------------------------------------------------------------------


class TestGeometryProviderPortContract:
    """Verifica que GeometryProviderPort define o contrato correto."""

    def test_is_abstract(self) -> None:
        assert issubclass(GeometryProviderPort, ABC)

    def test_has_required_abstract_methods(self) -> None:
        abstracts = _abstract_methods(GeometryProviderPort)
        assert "compute" in abstracts
        assert "calculate_position" in abstracts
        assert "calculate_range" in abstracts

    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            GeometryProviderPort()  # type: ignore[abstract]

    def test_concrete_subclass_must_implement_all_methods(self) -> None:
        class PartialGeometry(GeometryProviderPort):
            def compute(self, tracks: Any, observer: Any, sat_block: Any = None) -> xr.Dataset:
                _ = (observer, sat_block, tracks)  # assinala uso (interface/reservado)
                return xr.Dataset()

        # Missing calculate_position and calculate_range → should fail
        with pytest.raises(TypeError):
            PartialGeometry()  # type: ignore[abstract]

    def test_full_concrete_subclass_instantiates(self) -> None:
        class MinimalGeometry(GeometryProviderPort):
            def compute(self, tracks: Any, observer: Any, sat_block: Any = None) -> xr.Dataset:
                _ = (observer, sat_block, tracks)  # assinala uso (interface/reservado)
                return xr.Dataset()

            def calculate_position(
                self,
                satellite: Any,
                time: Any,
                observer_lat: float,
                observer_lon: float,
            ) -> tuple[Any, Any, Any]:
                _ = (
                    observer_lat,
                    observer_lon,
                    satellite,
                    time,
                )  # assinala uso (interface/reservado)
                return (0.0, 0.0, 0.0)

            def calculate_range(
                self,
                satellite: Any,
                time: Any,
                observer_lat: float | None = None,
                observer_lon: float | None = None,
            ) -> Any:
                _ = (
                    observer_lat,
                    observer_lon,
                    satellite,
                    time,
                )  # assinala uso (interface/reservado)
                return 0.0

        geo = MinimalGeometry()
        result = geo.compute({}, {})
        assert isinstance(result, xr.Dataset)


# ---------------------------------------------------------------------------
# SkyMapIOPort contract (requires healpy/astropy)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _skymap_ports_available, reason="healpy/astropy not available in test env")
class TestSkyMapIOPortContract:
    """Verifica que SkyMapIOPort define o contrato correto."""

    def test_is_abstract(self) -> None:
        assert issubclass(SkyMapIOPort, ABC)  # type: ignore[arg-type]

    def test_has_required_abstract_methods(self) -> None:
        abstracts = _abstract_methods(SkyMapIOPort)  # type: ignore[arg-type]
        assert "read_map" in abstracts
        assert "write_map" in abstracts


@pytest.mark.skipif(not _skymap_ports_available, reason="healpy/astropy not available in test env")
class TestSkyMapTransformPortContract:
    """Verifica que SkyMapTransformPort define o contrato correto."""

    def test_is_abstract(self) -> None:
        assert issubclass(SkyMapTransformPort, ABC)  # type: ignore[arg-type]

    def test_has_required_abstract_methods(self) -> None:
        abstracts = _abstract_methods(SkyMapTransformPort)  # type: ignore[arg-type]
        assert "smooth" in abstracts
        assert "rotate" in abstracts
        assert "downgrade" in abstracts
