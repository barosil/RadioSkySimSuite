from __future__ import annotations

from pathlib import Path

import healpy as hp
import numpy as np
import xarray as xr

from radioskysims_simulation.application.services.tod_orchestrator import (
    TODOrchestrator,
)
from radioskysims_skymap.domain.skymap import (
    NSide,
    SkyMap,
)
from radioskysims_simulation.domain.tod import (
    TODSimulator,
)
from radioskysims_skymap.infrastructure.skymap.repository.hdf5 import (
    HDF5SkyMapRepository,
)
from radioskysims_simulation.infrastructure.skymap.tod_projector import (
    HealpySkyMapTODProjector,
)


def _pointing() -> xr.Dataset:
    return xr.Dataset(
        data_vars={
            "ra": (
                "time",
                np.array(
                    [
                        0.0,
                        0.1,
                        0.2,
                    ],
                    dtype=float,
                ),
            ),
            "dec": (
                "time",
                np.array(
                    [
                        0.0,
                        0.05,
                        0.1,
                    ],
                    dtype=float,
                ),
            ),
        },
        coords={
            "time": np.array(
                [
                    0.0,
                    1.0,
                    2.0,
                ],
                dtype=float,
            ),
        },
    )


def _constant_skymap(
    *,
    value_uk: float,
    freq_ghz: float,
) -> SkyMap:
    nside = 8

    return SkyMap(
        dataset=np.full(
            hp.nside2npix(nside),
            value_uk,
            dtype=np.float64,
        ),
        nside=NSide(nside),
        unit="uK_CMB",
        frame="galactic",
        freq_ghz=freq_ghz,
        field="I",
    )


def test_persisted_hdf5_map_can_generate_tod(
    tmp_path: Path,
):
    # --------------------------------------------------
    # 1. Cria repository HDF5
    # --------------------------------------------------
    repository = HDF5SkyMapRepository(tmp_path)

    original_map = _constant_skymap(
        value_uk=1_000_000.0,
        freq_ghz=1.0,
    )

    # --------------------------------------------------
    # 2. Persiste mapa
    # --------------------------------------------------
    repository.save(
        "galaxy_1000mhz_nside8",
        original_map,
    )

    assert repository.exists("galaxy_1000mhz_nside8")

    # --------------------------------------------------
    # 3. Carrega novamente
    # --------------------------------------------------
    loaded_map = repository.load("galaxy_1000mhz_nside8")

    assert loaded_map is not None

    np.testing.assert_array_equal(
        loaded_map.data,
        original_map.data,
    )

    assert loaded_map.freq_ghz == 1.0
    assert loaded_map.frame == "galactic"
    assert loaded_map.unit == "uK_CMB"

    # --------------------------------------------------
    # 4. Configura TOD
    # --------------------------------------------------
    simulator = TODSimulator(
        beam=None,
        gain=1.0,
    )

    projector = HealpySkyMapTODProjector()

    orchestrator = TODOrchestrator(
        simulator=simulator,
    )

    # --------------------------------------------------
    # 5. Usa MAPA CARREGADO para gerar TOD
    # --------------------------------------------------
    result = orchestrator.run(
        maps=[
            loaded_map,
        ],
        pointing_track=_pointing(),
        projector=projector,
        use_beam=False,
    )

    # --------------------------------------------------
    # 6. Valida estrutura
    # --------------------------------------------------
    assert "T_antenna" in result
    assert "power" in result

    assert result["T_antenna"].dims == (
        "time",
        "frequency",
    )

    assert result["T_antenna"].shape == (
        3,
        1,
    )

    # --------------------------------------------------
    # 7. 1_000_000 uK = 1 K
    #
    # Mapa constante => TOD constante.
    # --------------------------------------------------
    np.testing.assert_allclose(
        result["T_antenna"].values,
        1.0,
    )

    # --------------------------------------------------
    # 8. Frequência preservada
    # --------------------------------------------------
    np.testing.assert_allclose(
        result.coords["frequency"].values,
        [
            1.0e9,
        ],
    )

    assert result.attrs["contributions"] == [
        "skymap",
    ]
