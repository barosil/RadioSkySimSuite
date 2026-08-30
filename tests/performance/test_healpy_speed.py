import cProfile
import pstats
import sys
import time

import numpy as np
import pytest


@pytest.mark.performance
def test_healpy_speed():
    """Gera um SkyMap com NSide=512, executa smooth e downgrade, mede tempo total."""

    hp = pytest.importorskip("healpy")

    np.random.seed(0)
    nside = 512
    npix = hp.nside2npix(nside)

    # mapa simples (padrão) - valores constantes para evitar variações
    m = np.ones(npix, dtype=float)

    prof = cProfile.Profile()
    prof.enable()
    start = time.perf_counter()

    # smoothing e downgrade
    # Removido verbose=False (deprecado em healpy >= 1.15)
    smoothed = hp.smoothing(m, fwhm=np.radians(1.0))
    hp.ud_grade(smoothed, nside_out=128)

    elapsed = time.perf_counter() - start
    prof.disable()

    ps = pstats.Stats(prof, stream=sys.stdout)
    ps.strip_dirs().sort_stats("cumtime").print_stats(20)

    # Limite ajustado: map2alm (transformada harmônica esférica) é O(nside^2 log nside)
    # nside=512 com SHT em CPU leva ~1.4s (sem aceleração GPU/OpenMP)
    assert elapsed < 2.0

