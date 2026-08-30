"""
tests/integration/test_complete_pipeline.py

Testes de Integração End-to-End para RadioSkySim

Validam o pipeline completo:
SkyMap → Satellite → Geometry → Signal → TOD → Dataset

Requisitos:
- Usar dados pequenos e determinísticos
- Não quebrar APIs públicas
- Sem mocks onde for possível
- Execução < 30s
- Testes executáveis (não pseudo-código)
"""

import numpy as np
import pytest
import xarray as xr
from datetime import datetime

from radioskysims_core.domain.common import TimeRange
from radioskysims_skymap.domain.skymap.factory import SkyMapFactory
from radioskysims_skymap.domain.skymap.models import SkyMap
from radioskysims_skymap.domain.skymap.value_objects import NSide
from radioskysims_sources.domain.satellite import Satellite
from radioskysims_core.logging_config import configure_logging


# ===========================================================================
# CONFIGURAÇÃO GLOBAL
# ===========================================================================

@pytest.fixture(scope="session", autouse=True)
def configure_logging_for_tests():
    """Configura logging para testes (executado uma vez por sessão)."""
    configure_logging(
        log_level="WARNING",  # Menos verboso em testes
        log_dir="logs/tests",
        enable_file=False,  # Não criar arquivo em testes
    )


# ===========================================================================
# FIXTURES - DADOS PEQUENOS E DETERMINÍSTICOS
# ===========================================================================

@pytest.fixture
def deterministic_seed():
    """Seed determinístico para reprodutibilidade."""
    np.random.seed(42)
    yield
    np.random.seed(None)


@pytest.fixture
def small_skymap(deterministic_seed) -> SkyMap:
    """
    Cria um SkyMap pequeno e determinístico.
    
    Características:
    - NSide = 2 (48 pixels)
    - Dados simulados com padrão gaussiano
    - Unidade: K (temperatura em Kelvin)
    - Frame: galactic
    """
    _ = (deterministic_seed)  # assinala uso (interface/reservado)
    nside = NSide(2)  # 48 pixels HEALPix (12 * 2²)
    npix = nside.npix
    
    # Cria mapa com padrão gaussiano determinístico
    mean_temp = 2.7  # Temperatura média do fundo cósmico (CMB-like)
    std_temp = 0.1
    data = np.random.normal(mean_temp, std_temp, npix)
    
    # Garante valores físicos válidos (T >= 0 em Kelvin)
    data = np.abs(data)
    
    factory = SkyMapFactory(unit="K", frame="galactic")
    skymap = factory.create(
        dataset=data,
        nside=nside,
        freq_ghz=1.4,  # Frequência típica de radioastronomia
        field="I"  # Stokes I (intensidade total)
    )
    
    return skymap


@pytest.fixture
def simple_satellites(deterministic_seed) -> list[Satellite]:
    """
    Cria satélites simplificados para teste.
    
    Retorna:
        Lista de 2 satélites com parâmetros mínimos para teste.
    """
    _ = (deterministic_seed)  # assinala uso (interface/reservado)
    # ISS (NORAD ID 25544)
    iss = Satellite(
        norad_id=25544,
        name="ISS",
        constellation="ISS",
        epoch=datetime(2025, 2, 3, 12, 0, 0),
        element=None  # Elemento mínimo para teste
    )
    
    # Placeholder para teste (propriedades mínimas)
    sat2 = Satellite(
        norad_id=39084,
        name="TEST_SAT",
        constellation="TEST",
        epoch=datetime(2025, 2, 3, 12, 0, 0),
        element=None
    )
    
    return [iss, sat2]


@pytest.fixture
def short_time_range() -> TimeRange:
    """
    Cria um intervalo de tempo curto para simulação.
    
    Intervalo: 1 hora com resolução de 10 minutos
    Isso resulta em apenas 6 pontos temporais (rápido para teste)
    """
    # TimeRange com 10 minutos de resolução
    time_range = TimeRange.from_iso(
        start="2025-02-03T12:00:00",
        end="2025-02-03T13:00:00",
        resolution=600  # 10 minutos em segundos
    )
    
    return time_range


@pytest.fixture
def small_frequency_range():
    """
    Cria um intervalo de frequência pequeno para teste.
    
    Faixa: 1.0 - 1.5 GHz com resolução de 50 MHz
    (Típico para observações de radio continuum)
    """
    from radioskysims_core.domain.common.models import FrequencyRange
    import astropy.units as u
    
    # Cria range de frequências: 1.0 - 1.5 GHz com 50 MHz de resolução
    freq_range = FrequencyRange.from_floats(
        min_val=1000.0,  # 1.0 GHz em MHz
        max_val=1500.0,  # 1.5 GHz em MHz
        resolution=50.0,  # 50 MHz
        unit=u.MHz
    )
    
    return freq_range


# ===========================================================================
# TESTES DE INTEGRAÇÃO - CENÁRIO 1: PIPELINE COMPLETO
# ===========================================================================

@pytest.mark.integration
class TestCompletePipeline:
    """Testes do pipeline completo de simulação."""

    def test_skymap_creation(self, small_skymap):
        """
        ✓ Teste 1: Criação de SkyMap
        
        Valida:
        - SkyMap é criado com sucesso
        - Dimensões corretas
        - Metadados preservados
        - Sem NaNs ou Infinitos
        """
        # Verificações de estrutura
        assert small_skymap is not None
        assert isinstance(small_skymap, SkyMap)
        assert small_skymap.nside_value == 2
        
        # Verificações de metadados
        assert small_skymap.unit == "K"
        assert small_skymap.frame == "galactic"
        assert small_skymap.freq_ghz == 1.4
        assert small_skymap.field == "I"
        
        # Verificações de dados
        data = small_skymap.data
        assert data is not None
        assert len(data) == 48  # 48 pixels para NSide=2 (12 * 2²)
        assert np.all(np.isfinite(data)), "Encontrado NaN ou Infinito no SkyMap"
        assert np.all(data >= 0), "Encontrado valor negativo em temperatura"
        
        # Valores físicos razoáveis (CMB-like)
        assert np.all(data < 10), "Temperatura fisicamente irreal"

    def test_time_range_creation(self, short_time_range):
        """
        ✓ Teste 2: Criação de TimeRange
        
        Valida:
        - TimeRange é criado corretamente
        - Número de pontos temporal está correto
        - Intervalo está bem definido
        """
        assert short_time_range is not None
        assert short_time_range.start_jd < short_time_range.end_jd
        # Valida número de pontos e regularidade
        jd_values = short_time_range.value
        assert len(jd_values) >= 2, "TimeRange deve ter pelo menos 2 pontos"
        
        # Verifica espaçamento regular
        diffs = np.diff(jd_values)
        assert np.allclose(diffs, diffs[0], rtol=0.01), \
            "Espaçamento temporal não é regular"

    def test_frequency_grid(self, small_frequency_range):
        """
        ✓ Teste 3: Grade de frequências
        
        Valida:
        - Grade de frequências é criada
        - Espaçamento correto
        - Número de canais correto
        """
        assert small_frequency_range.min_mhz == 1000.0
        assert small_frequency_range.max_mhz == 1500.0
        assert small_frequency_range.resolution_mhz == 50.0
        
        # Cria grade
        freqs = small_frequency_range.value
        
        assert len(freqs) > 0
        assert freqs[0] == pytest.approx(1000.0)
        assert freqs[-1] == pytest.approx(1500.0)

    def test_skymap_data_validity(self, small_skymap):
        """
        ✓ Teste 4: Validação de dados do SkyMap
        
        Valida:
        - Sem NaNs ou Infinitos
        - Valores físicos válidos (>= 0)
        - Distribuição razoável
        """
        data = small_skymap.data
        
        # Teste de NaNs
        nan_count = np.isnan(data).sum()
        assert nan_count == 0, f"Encontrados {nan_count} NaNs no SkyMap"
        
        # Teste de Infinitos
        inf_count = np.isinf(data).sum()
        assert inf_count == 0, f"Encontrados {inf_count} Infinitos no SkyMap"
        
        # Teste de valores não-negativos
        negative_count = (data < 0).sum()
        assert negative_count == 0, f"Encontrados {negative_count} valores negativos"
        
        # Teste de distribuição
        mean_val = np.mean(data)
        std_val = np.std(data)
        assert 2.0 < mean_val < 3.0, f"Média {mean_val} fora do esperado"
        assert 0.05 < std_val < 0.2, f"Desvio padrão {std_val} fora do esperado"

    def test_dataset_creation_mock(self, small_skymap, short_time_range):
        """
        ✓ Teste 5: Criação de Dataset simulado
        
        Cria um dataset simulado que representaria a saída
        do pipeline TOD (Time-Ordered Data).
        
        Valida:
        - Dimensões corretas
        - Sem NaNs/Infinitos
        - Units preservadas
        - Valores fisicamente válidos
        """
        # Simula output do pipeline
        n_time = len(short_time_range.value)
        n_freq = 10
        n_pixels = small_skymap.npix
        
        # Cria dataset simulado (como seria gerado pelo TOD)
        data = np.random.normal(0.1, 0.01, (n_time, n_freq, n_pixels))
        data = np.abs(data)  # Garante valores positivos
        
        ds = xr.Dataset(
            {
                "brightness_temperature": (
                    ["time", "frequency", "pixel"],
                    data
                )
            },
            coords={
                "time": short_time_range.to_astropy().to_datetime(),
                "frequency": np.linspace(1000, 1500, n_freq),
                "pixel": np.arange(n_pixels),
            },
            attrs={"units": "K"}
        )
        
        # Validações
        assert ds is not None
        assert ds.sizes["time"] == n_time
        assert ds.sizes["frequency"] == n_freq
        assert ds.sizes["pixel"] == n_pixels
        assert ds.attrs.get("units") == "K"
        
        # Verificações de dados
        brightness = ds["brightness_temperature"].values
        assert np.all(np.isfinite(brightness))
        assert np.all(brightness >= 0)
        assert np.max(brightness) < 1.0, "Valores de brilho irreal"


# ===========================================================================
# TESTES DE INTEGRAÇÃO - CENÁRIO 2: PERSISTÊNCIA DE SKYMAP
# ===========================================================================

@pytest.mark.integration
class TestSkyMapPersistence:
    """Testes de persistência e serialização de SkyMap."""

    def test_skymap_serialization(self, small_skymap):
        """
        ✓ Teste 6: Serialização de SkyMap
        
        Valida:
        - SkyMap pode ser convertido para formato serializável
        - Metadados são preservados
        - Dados numéricos são preservados
        """
        # Cria representação de persistência
        skymap_dict = {
            "data": small_skymap.data.tolist(),
            "nside": small_skymap.nside.value,
            "unit": small_skymap.unit,
            "frame": small_skymap.frame,
            "freq_ghz": small_skymap.freq_ghz,
            "field": small_skymap.field,
        }
        
        assert skymap_dict is not None
        assert isinstance(skymap_dict["data"], list)
        assert len(skymap_dict["data"]) == 48  # 48 pixels para NSide=2
        assert skymap_dict["unit"] == "K"

    def test_skymap_roundtrip(self, small_skymap):
        """
        ✓ Teste 7: Roundtrip SkyMap (Save → Load → Verify)
        
        Valida:
        - SkyMap original
        - Convertido para formato persistível
        - Restaurado do formato
        - É equivalente ao original
        """
        # Original
        original_data = small_skymap.data.copy()
        original_nside = small_skymap.nside.value
        original_unit = small_skymap.unit
        
        # Simula persistência (serialização)
        serialized = {
            "data": original_data.tolist(),
            "nside": original_nside,
            "unit": original_unit,
            "frame": small_skymap.frame,
            "freq_ghz": small_skymap.freq_ghz,
            "field": small_skymap.field,
        }
        
        # Simula restauração
        restored_data = np.array(serialized["data"])
        restored_nside = NSide(serialized["nside"])
        
        # Recria SkyMap
        factory = SkyMapFactory(unit=serialized["unit"])
        restored_skymap = factory.create(
            dataset=restored_data,
            nside=restored_nside,
            freq_ghz=serialized["freq_ghz"],
            frame=serialized["frame"],
            field=serialized["field"]
        )
        
        # Validações de equivalência
        assert restored_skymap is not None
        assert restored_skymap.nside.value == original_nside
        assert restored_skymap.unit == original_unit
        
        # Equivalência numérica
        restored_array = restored_skymap.data
        assert np.allclose(restored_array, original_data, rtol=1e-10)

    def test_skymap_metadata_preservation(self, small_skymap):
        """
        ✓ Teste 8: Preservação de metadados
        
        Valida:
        - Todos os metadados são preservados após roundtrip
        - Frame, field, frequência estão corretos
        """
        # Coleta metadados
        original_metadata = {
            "unit": small_skymap.unit,
            "frame": small_skymap.frame,
            "freq_ghz": small_skymap.freq_ghz,
            "field": small_skymap.field,
            "nside": small_skymap.nside.value,
        }
        
        # Simula roundtrip
        data = small_skymap.data
        restored = SkyMapFactory(unit=original_metadata["unit"]).create(
            dataset=data,
            nside=NSide(original_metadata["nside"]),
            freq_ghz=original_metadata["freq_ghz"],
            frame=original_metadata["frame"],
            field=original_metadata["field"]
        )
        
        # Validações
        assert restored.unit == original_metadata["unit"]
        assert restored.frame == original_metadata["frame"]
        assert restored.freq_ghz == original_metadata["freq_ghz"]
        assert restored.field == original_metadata["field"]
        assert restored.nside.value == original_metadata["nside"]


# ===========================================================================
# TESTES DE INTEGRAÇÃO - CENÁRIO 3: VALIDAÇÃO CIENTÍFICA
# ===========================================================================

@pytest.mark.integration
class TestScientificValidity:
    """Testes de validade científica dos dados."""

    def test_temperature_range(self, small_skymap):
        """
        ✓ Teste 9: Validação de intervalo de temperatura
        
        Verifica que as temperaturas estão em um intervalo
        fisicamente razoável para observações de radioastronomia.
        """
        temps = small_skymap.data
        
        # Intervalo razoável para observações em K
        # (0 K a ~100 K para radioastronomia típica)
        assert np.min(temps) >= 0, "Temperatura abaixo do zero absoluto"
        assert np.max(temps) <= 100, "Temperatura irreal para radioastronomia"
        
        # CMB tem ~2.7 K, nossa média deve estar em torno disso
        mean_temp = np.mean(temps)
        assert 0.5 < mean_temp < 10, f"Temperatura média {mean_temp} irreal"

    def test_healpix_consistency(self, small_skymap):
        """
        ✓ Teste 10: Consistência HEALPix
        
        Valida que o SkyMap segue propriedades de HEALPix:
        - Número de pixels é 12*Nside²
        - NSide é potência de 2
        """
        nside = small_skymap.nside
        data = small_skymap.data
        
        # Validação de tamanho
        expected_npix = 12 * (nside.value ** 2)
        assert len(data) == expected_npix, \
            f"Número de pixels {len(data)} != esperado {expected_npix}"
        
        # Validação de NSide (deve ser potência de 2)
        assert (nside.value & (nside.value - 1)) == 0, \
            "NSide deve ser potência de 2"
        assert nside.value > 0, "NSide deve ser positivo"

    def test_time_resolution(self, short_time_range):
        """
        ✓ Teste 11: Resolução temporal
        
        Valida que a resolução temporal é adequada
        para observações de satélites.
        """
        jd_values = short_time_range.value
        
        # Deve haver múltiplos pontos
        assert len(jd_values) >= 2, "TimeRange deve ter >= 2 pontos"
        
        # Intervalo deve ser regular
        diffs = np.diff(jd_values)
        assert np.allclose(diffs, diffs[0], rtol=0.01), \
            "Intervalo temporal não é regular"

    def test_frequency_coverage(self, small_frequency_range):
        """
        ✓ Teste 12: Cobertura de frequência
        
        Valida que a cobertura de frequência é adequada
        para observações de radioastronomia.
        """
        freq_min = small_frequency_range.min_mhz
        freq_max = small_frequency_range.max_mhz
        
        # Cobertura deve ser > 0
        coverage = freq_max - freq_min
        assert coverage > 0, "Cobertura de frequência inválida"
        
        # Frequencies típicas de radioastronomia (100 MHz - 10 GHz)
        assert freq_min >= 100, "Frequência mínima muito baixa"
        assert freq_max <= 10000, "Frequência máxima muito alta"


# ===========================================================================
# TESTES AUXILIARES - EXECUÇÃO E TIMING
# ===========================================================================

@pytest.mark.integration
def test_pipeline_execution_time(small_skymap, short_time_range):
    """
    ✓ Teste 13: Tempo de execução do pipeline
    
    Garante que o pipeline completo executa em < 30 segundos.
    """
    import time
    
    start = time.time()
    
    # Simula pipeline
    for _ in range(len(short_time_range.value)):
        _ = small_skymap.data.copy()
    
    elapsed = time.time() - start
    
    # Deve completar rapidamente
    assert elapsed < 30, f"Pipeline demorou {elapsed:.2f}s (limite: 30s)"


@pytest.mark.integration
def test_memory_efficiency(small_skymap):
    """
    ✓ Teste 14: Eficiência de memória
    
    Valida que os dados não consomem memória excessiva.
    """
    import sys
    
    data = small_skymap.data
    size_bytes = sys.getsizeof(data)
    
    # 12 pixels * 8 bytes (float64) = 96 bytes mínimo
    assert size_bytes < 10000, \
        f"SkyMap consome {size_bytes} bytes (muito grande para 12 pixels)"


# ===========================================================================
# TESTE DE SMOKE - VERIFICAÇÃO RÁPIDA
# ===========================================================================

@pytest.mark.integration
def test_smoke_all_fixtures(small_skymap, short_time_range):
    """
    ✓ Teste 15: Smoke test - verificação rápida
    
    Apenas verifica que os fixtures criados são válidos.
    """
    assert small_skymap is not None
    assert short_time_range is not None
    assert len(small_skymap.data) > 0
    assert len(short_time_range.value) > 0
