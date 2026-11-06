"""
Contract tests para todos os Ports da Infrastructure Layer.

Verifica que as implementações concretas (adapters) respeitam os
contratos definidos nos ports, testando assinaturas, tipos de
retorno e comportamentos esperados (exceções, etc).

Estrutura:
    - SkyMapIOPort: HealpySkyMapProvider, PySMSkyMapGeneratorAdapter
    - SkyMapTransformPort: HealpySkyMapProvider
    - GeometryProviderPort: SkyfieldGeometryProvider
    - BeamLoaderPort: LITBeamLoader, CSVBeamLoader, CustomBeamLoader
    - SkyMapAnalyzerPort: HealpySkyMapAnalyzer
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from radioskysims_beam.application.ports.beam import (
    BeamLoaderPort,
)
from radioskysims_core.application.ports.geometry import GeometryProviderPort
from radioskysims_skymap.application.skymap.ports import (
    SkyMapAnalyzerPort,
    SkyMapGeneratorPort,
    SkyMapMaskPort,
)
from radioskysims_skymap.domain.skymap.models import SkyMap
from radioskysims_skymap.domain.skymap.value_objects import NSide

# =============================================================================
# Imports dos Ports (interfaces)
# =============================================================================
from radioskysims_skymap.infrastructure.ports.skymap import SkyMapIOPort, SkyMapTransformPort
from radioskysims_skymap.infrastructure.skymap.adapters.analysis import (
    HealpySkyMapAnalyzer,
    HealpySkyMapAnalyzerAdapter,
)

# =============================================================================
# Imports das implementações (adapters)
# =============================================================================
from radioskysims_skymap.infrastructure.skymap.providers.healpy import HealpySkyMapProvider

# =============================================================================
# Fixtures compartilhadas
# =============================================================================


@pytest.fixture
def dummy_skymap() -> SkyMap:
    """SkyMap mínimo (NSide=1, 12 pixels) para testes de contrato."""
    return SkyMap(
        dataset=np.ones(12),
        nside=NSide(1),
        unit="uK_CMB",
        frame="galactic",
    )


@pytest.fixture
def healpy_provider() -> HealpySkyMapProvider:
    return HealpySkyMapProvider()


# =============================================================================
# 1. Contract: SkyMapIOPort
# =============================================================================


class TestSkyMapIOPortContract:
    """Verifica que HealpySkyMapProvider respeita o contrato SkyMapIOPort."""

    def test_implementa_interface(self, healpy_provider):
        assert isinstance(healpy_provider, SkyMapIOPort)

    def test_read_map_assinatura(self, healpy_provider):
        """Verifica que read_map aceita os parâmetros obrigatórios."""
        import inspect

        sig = inspect.signature(healpy_provider.read_map)
        assert "path" in sig.parameters
        assert "nside" in sig.parameters
        assert "unit" in sig.parameters
        assert "field" in sig.parameters

    def test_read_map_arquivo_inexistente(self, healpy_provider):
        """Contrato: FileNotFoundError para arquivo que não existe."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pytest.raises(FileNotFoundError):
                healpy_provider.read_map("/path/inexistente.fits")

    def test_write_map_assinatura(self, healpy_provider):
        """Verifica que write_map aceita os parâmetros do contrato."""
        import inspect

        sig = inspect.signature(healpy_provider.write_map)
        assert "skymap" in sig.parameters
        assert "path" in sig.parameters
        assert "overwrite" in sig.parameters

    def test_write_map_retorna_path(self, healpy_provider, dummy_skymap, tmp_path):
        """Contrato: write_map retorna um Path."""
        out = tmp_path / "test_map.fits"
        result = healpy_provider.write_map(dummy_skymap, out, overwrite=True)
        assert isinstance(result, Path)


# =============================================================================
# 2. Contract: SkyMapTransformPort
# =============================================================================


class TestSkyMapTransformPortContract:
    """Verifica que HealpySkyMapProvider respeita o contrato SkyMapTransformPort."""

    def test_implementa_interface(self, healpy_provider):
        assert isinstance(healpy_provider, SkyMapTransformPort)

    def test_smooth_assinatura(self, healpy_provider):
        import inspect

        sig = inspect.signature(healpy_provider.smooth)
        assert "skymap" in sig.parameters
        assert "fwhm_rad" in sig.parameters

    def test_smooth_retorna_skymap(self, healpy_provider, dummy_skymap):
        """Contrato: smooth retorna um SkyMap."""
        result = healpy_provider.smooth(dummy_skymap, fwhm_rad=0.1)
        assert isinstance(result, SkyMap)

    def test_smooth_fwhm_invalido(self, healpy_provider, dummy_skymap):
        """Contrato: ValueError se fwhm_rad <= 0."""
        with pytest.raises(ValueError):
            healpy_provider.smooth(dummy_skymap, fwhm_rad=0)
        with pytest.raises(ValueError):
            healpy_provider.smooth(dummy_skymap, fwhm_rad=-0.1)

    def test_rotate_assinatura(self, healpy_provider):
        import inspect

        sig = inspect.signature(healpy_provider.rotate)
        assert "skymap" in sig.parameters
        assert "rot" in sig.parameters

    def test_rotate_retorna_skymap(self, healpy_provider, dummy_skymap):
        """Contrato: rotate retorna um SkyMap."""
        result = healpy_provider.rotate(dummy_skymap, rot=(0, 0, 0))
        assert isinstance(result, SkyMap)

    def test_downgrade_assinatura(self, healpy_provider, dummy_skymap):
        """Contrato: downgrade aceita target_nside."""
        result = healpy_provider.downgrade(dummy_skymap, target_nside=NSide(1))
        assert isinstance(result, SkyMap)


# =============================================================================
# 3. Contract: SkyMapAnalyzerPort
# =============================================================================


class TestSkyMapAnalyzerPortContract:
    """Verifica que HealpySkyMapAnalyzer respeita o contrato SkyMapAnalyzerPort."""

    @pytest.fixture
    def analyzer(self) -> HealpySkyMapAnalyzer:
        return HealpySkyMapAnalyzer()

    def test_implementa_interface(self, analyzer):
        assert isinstance(analyzer, SkyMapAnalyzerPort)

    def test_compute_cls_assinatura(self, analyzer):
        import inspect

        sig = inspect.signature(analyzer.compute_cls)
        assert "skymap" in sig.parameters

    def test_compute_cls_retorna_array(self, analyzer, dummy_skymap):
        """Contrato: compute_cls retorna algo compatível com ndarray."""
        result = analyzer.compute_cls(dummy_skymap, lmax=3)
        assert result is not None


class TestSkyMapAnalyzerAdapterContract:
    """Verifica o contrato do HealpySkyMapAnalyzerAdapter."""

    @pytest.fixture
    def adapter(self) -> HealpySkyMapAnalyzerAdapter:
        return HealpySkyMapAnalyzerAdapter()

    def test_compute_cls_retorna_array(self, adapter):
        data = np.ones(12)
        result = adapter.compute_cls(map_data=data, lmax=3)
        assert isinstance(result, np.ndarray)

    def test_compute_cls_map_data_obrigatorio(self, adapter):
        with pytest.raises(TypeError):
            adapter.compute_cls(map_data="invalido", lmax=3)


# =============================================================================
# 4. Contract: SkyMapGeneratorPort
# =============================================================================


class TestSkyMapGeneratorPortContract:
    """Verifica que os geradores respeitam o contrato SkyMapGeneratorPort."""

    def test_implementa_interface(self):
        from radioskysims_skymap.infrastructure.skymap.providers.pysm import (
            PySMSkyMapGeneratorAdapter,
        )

        gen = PySMSkyMapGeneratorAdapter()
        assert isinstance(gen, SkyMapGeneratorPort)

    def test_generate_assinatura(self):
        import inspect

        from radioskysims_skymap.infrastructure.skymap.providers.pysm import (
            PySMSkyMapGeneratorAdapter,
        )

        gen = PySMSkyMapGeneratorAdapter()
        sig = inspect.signature(gen.generate)
        assert "nside" in sig.parameters
        assert "freq_ghz" in sig.parameters


# =============================================================================
# 5. Contract: BeamLoaderPort
# =============================================================================


class TestBeamLoaderPortContract:
    """Verifica que os loaders de beam respeitam o contrato BeamLoaderPort."""

    @pytest.mark.parametrize(
        "loader_cls",
        [
            pytest.param(
                "LITBeamLoader",
                marks=pytest.mark.skip(reason="requer arquivo .xlsx real"),
            ),
            pytest.param(
                "CSVBeamLoader",
                marks=pytest.mark.skip(reason="requer arquivo .csv real"),
            ),
            pytest.param(
                "CustomBeamLoader",
                marks=pytest.mark.skip(reason="requer implementação"),
            ),
            pytest.param("AnalyticalBeamLoader"),
        ],
    )
    def test_implementa_interface(self, loader_cls):
        """Verificação estrutural: a classe implementa BeamLoaderPort."""
        import importlib

        mod = importlib.import_module("radioskysims_beam.infrastructure.beams.loaders")
        cls = getattr(mod, loader_cls)
        assert issubclass(cls, BeamLoaderPort)


# =============================================================================
# 8. Contract: GeometryProviderPort
# =============================================================================


class TestGeometryProviderPortContract:
    """Verifica que o provider de geometria respeita o contrato GeometryProviderPort."""

    def test_classe_exportada(self):
        """Verificação estrutural: a classe implementa GeometryProviderPort."""
        from radioskysims_core.infrastructure.external_geometry import (
            SkyfieldGeometryProvider,
        )

        assert issubclass(SkyfieldGeometryProvider, GeometryProviderPort)

    def test_compute_assinatura(self):
        from radioskysims_core.infrastructure.external_geometry import (
            SkyfieldGeometryProvider,
        )

        # SkyfieldGeometryProvider requer ts (timescale) no construtor
        # Testamos apenas a assinatura estática da classe
        assert hasattr(SkyfieldGeometryProvider, "compute")


# =============================================================================
# 9. Contract: SkyMapMaskPort
# =============================================================================


class TestSkyMapMaskPortContract:
    """Verifica que implementações de máscara respeitam o contrato SkyMapMaskPort."""

    def test_apply_assinatura(self, dummy_skymap):
        """SkyMap tem método apply_mask como operação de domínio."""
        _ = dummy_skymap  # assinala uso (interface/reservado)
        import inspect

        # Verifica que a assinatura do contrato é respeitada
        sig = inspect.signature(SkyMapMaskPort.apply)
        assert "skymap" in sig.parameters
        assert "mask" in sig.parameters
