from __future__ import annotations

import numpy as np
import xarray as xr
from radioskysims_core.domain.common import (
    FrequencyRange,
)
from radioskysims_simulation.application.services.tod_orchestrator import (
    TODOrchestrator,
)
from radioskysims_simulation.domain.tod import TODSimulator
from radioskysims_simulation.infrastructure.skymap.tod_projector import (
    HealpySkyMapTODProjector,
)
from radioskysims_skymap.infrastructure.skymap.repository.hdf5 import (
    HDF5SkyMapRepository,
)
from radioskysims_sources.application.cosmology import (
    GenerateNeutralHydrogenMapsUseCase,
    GenerateNeutralHydrogenMapUseCase,
)
from radioskysims_sources.domain.cosmology import CosmologyParameters
from radioskysims_sources.domain.radiosources import NeutralHydrogen
from radioskysims_sources.infrastructure.cosmology import (
    HealpyGaussianMatterFieldAdapter,
    PyCCLCosmologyAdapter,
)


def _build_pointing_track() -> xr.Dataset:
    time = np.array(
        [
            "2026-07-26T00:00:00",
            "2026-07-26T00:01:00",
            "2026-07-26T00:02:00",
            "2026-07-26T00:03:00",
        ],
        dtype="datetime64[ns]",
    )

    ra = xr.DataArray(
        np.deg2rad([0.0, 5.0, 10.0, 15.0]),
        dims=("time",),
        coords={"time": time},
        attrs={"units": "rad"},
    )

    dec = xr.DataArray(
        np.deg2rad([-15.0, -15.0, -15.0, -15.0]),
        dims=("time",),
        coords={"time": time},
        attrs={"units": "rad"},
    )

    return xr.Dataset(
        data_vars={
            "ra": ra,
            "dec": dec,
        },
        coords={
            "time": time,
        },
    )


def test_neutral_hydrogen_maps_generate_tod() -> None:
    cosmology = CosmologyParameters(
        omega_c=0.25,
        omega_b=0.05,
        h=0.67,
        sigma8=0.81,
        n_s=0.965,
    )

    frequency_range = FrequencyRange(
        min_mhz=1000.0,
        max_mhz=1020.0,
        resolution_mhz=10.0,
    )

    channel_generator = GenerateNeutralHydrogenMapUseCase(
        angular_power=PyCCLCosmologyAdapter(),
        gaussian_field=HealpyGaussianMatterFieldAdapter(),
    )

    map_generator = GenerateNeutralHydrogenMapsUseCase(
        channel_generator=channel_generator,
    )

    map_set = map_generator.execute(
        source=NeutralHydrogen(),
        cosmology=cosmology,
        frequency_range=frequency_range,
        nside=8,
        ell_max=16,
        seed=42,
    )

    simulator = TODSimulator(
        beam=None,
        gain=1.0,
    )

    tod_orchestrator = TODOrchestrator(
        simulator=simulator,
    )

    tod = tod_orchestrator.run_maps(
        maps=map_set.maps,
        pointing_track=_build_pointing_track(),
        projector=HealpySkyMapTODProjector(),
        use_beam=False,
    )

    assert set(tod.data_vars) >= {
        "T_antenna",
        "power",
    }

    assert tod["T_antenna"].dims == (
        "time",
        "frequency",
    )

    assert tod["power"].dims == (
        "time",
        "frequency",
    )

    assert tod.sizes["time"] == 4
    assert tod.sizes["frequency"] == len(frequency_range.value)

    expected_frequency_hz = frequency_range.value * 1.0e6

    np.testing.assert_allclose(
        tod.coords["frequency"].values,
        expected_frequency_hz,
    )

    assert tod["T_antenna"].attrs["units"] == "K"
    assert tod["power"].attrs["units"] == "W/Hz"

    temperature = np.asarray(
        tod["T_antenna"].values,
        dtype=float,
    )

    power = np.asarray(
        tod["power"].values,
        dtype=float,
    )

    assert np.all(np.isfinite(temperature))
    assert np.all(np.isfinite(power))

    assert np.any(temperature < 0)
    assert np.any(temperature > 0)

    assert not np.allclose(
        temperature,
        0.0,
        rtol=0.0,
        atol=0.0,
    )

    assert tod.attrs["contributions"] == ["skymap"]

    assert tod.attrs["sky_model"] == "diffuse"
    assert tod.attrs["beam_model"] == "none"


def test_neutral_hydrogen_skymap_microkelvin_is_converted_to_kelvin() -> None:
    cosmology = CosmologyParameters(
        omega_c=0.25,
        omega_b=0.05,
        h=0.67,
        sigma8=0.81,
        n_s=0.965,
    )

    channel_generator = GenerateNeutralHydrogenMapUseCase(
        angular_power=PyCCLCosmologyAdapter(),
        gaussian_field=HealpyGaussianMatterFieldAdapter(),
    )

    result = channel_generator.execute(
        source=NeutralHydrogen(),
        cosmology=cosmology,
        frequency_mhz=1100.0,
        nside=8,
        ell_max=16,
        seed=42,
    )

    pointing = _build_pointing_track()

    projector = HealpySkyMapTODProjector()

    projected_uk = projector.project(
        skymap=result.skymap,
        pointing_track=pointing,
        fwhm_rad=None,
    )

    simulator = TODSimulator(
        beam=None,
        gain=1.0,
    )

    tod = simulator.simulate_from_maps(
        maps=[result.skymap],
        pointing_track=pointing,
        projector=projector,
        use_beam=False,
    )

    np.testing.assert_allclose(
        tod["T_antenna"].isel(frequency=0).values,
        projected_uk.values * 1.0e-6,
    )


def test_neutral_hydrogen_maps_generate_beam_convolved_tod() -> None:
    cosmology = CosmologyParameters(
        omega_c=0.25,
        omega_b=0.05,
        h=0.67,
        sigma8=0.81,
        n_s=0.965,
    )

    channel_generator = GenerateNeutralHydrogenMapUseCase(
        angular_power=PyCCLCosmologyAdapter(),
        gaussian_field=HealpyGaussianMatterFieldAdapter(),
    )

    result = channel_generator.execute(
        source=NeutralHydrogen(),
        cosmology=cosmology,
        frequency_mhz=1100.0,
        nside=16,
        ell_max=32,
        seed=42,
    )

    pointing = _build_pointing_track()

    projector = HealpySkyMapTODProjector()

    simulator = TODSimulator(
        beam=None,
        gain=1.0,
    )

    without_beam = simulator.simulate_from_maps(
        maps=[result.skymap],
        pointing_track=pointing,
        projector=projector,
        use_beam=False,
    )

    with_beam = simulator.simulate_from_maps(
        maps=[result.skymap],
        pointing_track=pointing,
        projector=projector,
        fwhm_deg=1.0,
        use_beam=True,
    )

    raw_temperature = np.asarray(
        without_beam["T_antenna"].values,
        dtype=float,
    )

    convolved_temperature = np.asarray(
        with_beam["T_antenna"].values,
        dtype=float,
    )

    assert np.all(np.isfinite(raw_temperature))
    assert np.all(np.isfinite(convolved_temperature))

    assert raw_temperature.shape == convolved_temperature.shape

    assert not np.allclose(
        raw_temperature,
        convolved_temperature,
        rtol=0.0,
        atol=0.0,
    )

    assert without_beam.attrs["beam_model"] == "none"

    assert with_beam.attrs["beam_model"] == ("gaussian_equivalent")

    assert with_beam.attrs["beam_fwhm_source"] == ("explicit")


def test_persisted_hi_maps_can_be_loaded_and_used_for_tod(
    tmp_path,
) -> None:
    repository = HDF5SkyMapRepository(
        root=tmp_path,
    )

    cosmology = CosmologyParameters(
        omega_c=0.25,
        omega_b=0.05,
        h=0.67,
        sigma8=0.81,
        n_s=0.965,
    )

    frequency_range = FrequencyRange(
        min_mhz=1000.0,
        max_mhz=1002.0,
        resolution_mhz=1.0,
    )

    channel_generator = GenerateNeutralHydrogenMapUseCase(
        angular_power=PyCCLCosmologyAdapter(),
        gaussian_field=HealpyGaussianMatterFieldAdapter(),
    )

    map_generator = GenerateNeutralHydrogenMapsUseCase(
        channel_generator=channel_generator,
        repository=repository,
    )

    generated = map_generator.execute(
        source=NeutralHydrogen(),
        cosmology=cosmology,
        frequency_range=frequency_range,
        nside=8,
        ell_max=16,
        seed=42,
        persist=True,
    )

    loaded_maps = []

    for frequency_mhz in frequency_range.value:
        key = map_generator.repository_key(
            frequency_mhz=float(frequency_mhz),
            nside=8,
        )

        assert repository.exists(key)

        loaded = repository.load(key)

        assert loaded is not None

        loaded_maps.append(loaded)

    assert len(loaded_maps) == len(generated.maps)

    for original, loaded in zip(
        generated.maps,
        loaded_maps,
        strict=False,
    ):
        np.testing.assert_allclose(
            original.dataset.to_numpy(),
            loaded.dataset.to_numpy(),
        )

        assert loaded.nside_value == original.nside_value

        assert loaded.unit == original.unit
        assert loaded.frame == original.frame
        assert loaded.field == original.field

        assert loaded.freq_ghz == original.freq_ghz

    simulator = TODSimulator(
        beam=None,
        gain=1.0,
    )

    tod_orchestrator = TODOrchestrator(
        simulator=simulator,
    )

    tod = tod_orchestrator.run_maps(
        maps=tuple(loaded_maps),
        pointing_track=_build_pointing_track(),
        projector=HealpySkyMapTODProjector(),
        use_beam=False,
    )

    assert tod["T_antenna"].dims == (
        "time",
        "frequency",
    )

    assert tod["power"].dims == (
        "time",
        "frequency",
    )

    assert tod.sizes["time"] == 4

    assert tod.sizes["frequency"] == len(frequency_range.value)

    expected_frequency_hz = frequency_range.value * 1.0e6

    np.testing.assert_allclose(
        tod.coords["frequency"].values,
        expected_frequency_hz,
    )

    temperature = np.asarray(
        tod["T_antenna"].values,
        dtype=float,
    )

    power = np.asarray(
        tod["power"].values,
        dtype=float,
    )

    assert np.all(np.isfinite(temperature))

    assert np.all(np.isfinite(power))

    assert not np.allclose(
        temperature,
        0.0,
        rtol=0.0,
        atol=0.0,
    )

    assert tod["T_antenna"].attrs["units"] == "K"

    assert tod["power"].attrs["units"] == "W/Hz"

    assert tod.attrs["contributions"] == ["skymap"]

    assert tod.attrs["sky_model"] == "diffuse"

    assert tod.attrs["beam_model"] == "none"


def test_lognormal_neutral_hydrogen_maps_generate_tod() -> None:
    from radioskysims_sources.infrastructure.cosmology import (
        HealpyLognormalMatterFieldAdapter,
    )

    cosmology = CosmologyParameters(
        omega_c=0.25,
        omega_b=0.05,
        h=0.67,
        sigma8=0.81,
        n_s=0.965,
    )

    frequency_range = FrequencyRange(
        min_mhz=1000.0,
        max_mhz=1002.0,
        resolution_mhz=1.0,
    )

    channel_generator = GenerateNeutralHydrogenMapUseCase(
        angular_power=PyCCLCosmologyAdapter(),
        gaussian_field=HealpyLognormalMatterFieldAdapter(),
    )

    map_generator = GenerateNeutralHydrogenMapsUseCase(
        channel_generator=channel_generator,
    )

    result = map_generator.execute(
        source=NeutralHydrogen(),
        cosmology=cosmology,
        frequency_range=frequency_range,
        nside=8,
        ell_max=16,
        seed=42,
    )

    simulator = TODSimulator(
        beam=None,
        gain=1.0,
    )

    tod_orchestrator = TODOrchestrator(
        simulator=simulator,
    )

    tod = tod_orchestrator.run_maps(
        maps=result.maps,
        pointing_track=_build_pointing_track(),
        projector=HealpySkyMapTODProjector(),
        use_beam=False,
    )

    assert tod["T_antenna"].dims == (
        "time",
        "frequency",
    )

    assert tod["power"].dims == (
        "time",
        "frequency",
    )

    assert tod.sizes["time"] == 4
    assert tod.sizes["frequency"] == 3

    np.testing.assert_allclose(
        tod.coords["frequency"].values,
        frequency_range.value * 1e6,
    )

    temperature = np.asarray(
        tod["T_antenna"].values,
        dtype=float,
    )

    power = np.asarray(
        tod["power"].values,
        dtype=float,
    )

    assert np.all(np.isfinite(temperature))

    assert np.all(np.isfinite(power))

    assert not np.allclose(
        temperature,
        0.0,
        rtol=0.0,
        atol=0.0,
    )

    assert tod["T_antenna"].attrs["units"] == "K"

    assert tod["power"].attrs["units"] == "W/Hz"

    assert tod.attrs["contributions"] == ["skymap"]

    assert tod.attrs["sky_model"] == "diffuse"

    assert tod.attrs["beam_model"] == "none"
