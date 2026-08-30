from __future__ import annotations

import numpy as np
import xarray as xr
from sqlalchemy import create_engine
from sqlmodel import Session

from radioskysims_simulation.application.mapmaking import (
    GenerateSkyMapsFromTODUseCase,
)
from radioskysims_simulation.application.services.mapmaking_service import (
    MapMakingService,
)
from radioskysims_simulation.infrastructure.db.mapmaking_db_model import (
    MapMakingRecord,
)
from radioskysims_simulation.infrastructure.db.mapmaking_repository import (
    MapMakingRepository,
)
from radioskysims_simulation.infrastructure.mapmaking import (
    HealpyBinnedMapMakerAdapter,
)


def _tod() -> xr.Dataset:
    time = np.array(
        [
            "2026-07-26T00:00:00",
            "2026-07-26T00:01:00",
            "2026-07-26T00:02:00",
            "2026-07-26T00:03:00",
        ],
        dtype="datetime64[ns]",
    )

    frequencies = np.array(
        [
            1.0e9,
            1.001e9,
            1.002e9,
        ],
        dtype=np.float64,
    )

    temperature = np.array(
        [
            [1.0, 10.0, 100.0],
            [2.0, 20.0, 200.0],
            [3.0, 30.0, 300.0],
            [4.0, 40.0, 400.0],
        ],
        dtype=np.float64,
    )

    return xr.Dataset(
        data_vars={
            "T_antenna": (
                (
                    "time",
                    "frequency",
                ),
                temperature,
            ),
        },
        coords={
            "time": time,
            "frequency": frequencies,
        },
    )


def _pointing() -> xr.Dataset:
    time = np.array(
        [
            "2026-07-26T00:00:00",
            "2026-07-26T00:01:00",
            "2026-07-26T00:02:00",
            "2026-07-26T00:03:00",
        ],
        dtype="datetime64[ns]",
    )

    return xr.Dataset(
        data_vars={
            "ra": (
                "time",
                np.deg2rad(
                    [
                        0.0,
                        0.0,
                        90.0,
                        90.0,
                    ]
                ),
            ),
            "dec": (
                "time",
                np.deg2rad(
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ]
                ),
            ),
        },
        coords={
            "time": time,
        },
    )


def _repository(tmp_path) -> MapMakingRepository:
    engine = create_engine(
        "sqlite://",
    )

    MapMakingRecord.metadata.create_all(engine)

    return MapMakingRepository(
        root=tmp_path,
        session_factory=lambda: Session(engine),
    )


def test_tod_to_persisted_maps_round_trip(
    tmp_path,
) -> None:
    repository = _repository(tmp_path)

    service = MapMakingService(
        generator=GenerateSkyMapsFromTODUseCase(
            mapmaker=HealpyBinnedMapMakerAdapter(),
        ),
        repository=repository,
    )

    service_result = service.run(
        tod=_tod(),
        pointing_track=_pointing(),
        nside=8,
        frame="equatorial",
        persist=True,
        simulation_id=123,
        key_prefix="integration",
    )

    assert len(service_result.mapmaking.results) == 3

    assert len(service_result.record_ids) == 3

    for original, record_id in zip(
        service_result.mapmaking.results,
        service_result.record_ids,
        strict=True,
    ):
        loaded = repository.load(record_id)

        assert loaded is not None

        assert loaded.skymap.nside_value == original.skymap.nside_value

        assert loaded.skymap.frame == original.skymap.frame

        assert loaded.skymap.unit == original.skymap.unit

        assert loaded.skymap.freq_ghz == original.skymap.freq_ghz

        np.testing.assert_allclose(
            loaded.skymap.data,
            original.skymap.data,
        )

        np.testing.assert_array_equal(
            loaded.hit_map,
            original.hit_map,
        )

        np.testing.assert_array_equal(
            loaded.observed_mask,
            original.observed_mask,
        )

        assert loaded.n_samples == original.n_samples

        assert loaded.n_observed_pixels == original.n_observed_pixels


def test_persisted_metadata_links_to_simulation(
    tmp_path,
) -> None:
    repository = _repository(tmp_path)

    service = MapMakingService(
        generator=GenerateSkyMapsFromTODUseCase(
            mapmaker=HealpyBinnedMapMakerAdapter(),
        ),
        repository=repository,
    )

    result = service.run(
        tod=_tod(),
        pointing_track=_pointing(),
        nside=8,
        persist=True,
        simulation_id=456,
        key_prefix="metadata",
    )

    for record_id in result.record_ids:
        metadata = repository.get_metadata(record_id)

        assert metadata is not None

        assert metadata["simulation_id"] == 456

        assert metadata["n_samples"] == 4

        assert metadata["n_observed_pixels"] == 2


def test_reconstructed_channel_values_are_correct(
    tmp_path,
) -> None:
    repository = _repository(tmp_path)

    service = MapMakingService(
        generator=GenerateSkyMapsFromTODUseCase(
            mapmaker=HealpyBinnedMapMakerAdapter(),
        ),
        repository=repository,
    )

    result = service.run(
        tod=_tod(),
        pointing_track=_pointing(),
        nside=8,
    )

    expected = (
        [1.5, 3.5],
        [15.0, 35.0],
        [150.0, 350.0],
    )

    for channel, expected_values in zip(
        result.mapmaking.results,
        expected,
        strict=True,
    ):
        observed_values = np.sort(channel.skymap.data[channel.observed_mask])

        np.testing.assert_allclose(
            observed_values,
            expected_values,
        )
