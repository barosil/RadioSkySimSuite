from __future__ import annotations

import healpy as hp
import numpy as np
import xarray as xr

from radioskysims_simulation.infrastructure.mapmaking.healpy_binned import HealpyBinnedMapMakerAdapter


def _tod_and_pointing_small():
    time = np.array(
        [
            "2026-07-26T00:00:00",
            "2026-07-26T00:01:00",
            "2026-07-26T00:02:00",
            "2026-07-26T00:03:00",
        ],
        dtype="datetime64[ns]",
    )

    frequency = np.array([1.0e9], dtype=float)

    temperature = xr.DataArray(
        np.array([[1.0], [2.0], [3.0], [4.0]], dtype=float),
        dims=("time", "frequency"),
        coords={"time": time, "frequency": frequency},
        attrs={"units": "K"},
    )

    tod = xr.Dataset(data_vars={"T_antenna": temperature})

    ra = np.deg2rad([0.0, 0.0, 90.0, 90.0])
    dec = np.deg2rad([0.0, 0.0, 0.0, 0.0])

    pointing = xr.Dataset(
        data_vars={
            "ra": xr.DataArray(ra, dims=("time",), coords={"time": time}, attrs={"units": "rad"}),
            "dec": xr.DataArray(dec, dims=("time",), coords={"time": time}, attrs={"units": "rad"}),
        }
    )

    return tod, pointing


def test_basic_properties_and_consistency():
    adapter = HealpyBinnedMapMakerAdapter()

    tod, pointing = _tod_and_pointing_small()

    nside = 8
    result = adapter.make_map(tod=tod, pointing_track=pointing, frequency_hz=1.0e9, nside=nside)

    # deterministic invariants
    assert int(result.hit_map.sum()) == 4
    assert result.n_samples == 4

    npix = hp.nside2npix(nside)
    assert npix == 12 * nside * nside

    observed_pixels = int(np.count_nonzero(result.observed_mask))
    assert observed_pixels > 0

    cover = observed_pixels / float(npix)
    assert 0.0 <= cover <= 1.0

    # RMS of residual must be finite and non-negative
    # Build a simple reference evaluated at pixel centers
    ref = _build_reference_simple(nside)

    observed = result.observed_mask
    diff = result.skymap.data[observed] - ref[observed]
    rms = float(np.sqrt(float(np.mean(np.square(diff)))))
    assert np.isfinite(rms) and rms >= 0.0

    # bias finite
    bias = float(np.mean(diff))
    assert np.isfinite(bias)

    # pixel scale decreases when nside increases
    scale_n8 = _pixel_scale_deg(8)
    scale_n16 = _pixel_scale_deg(16)
    assert scale_n16 < scale_n8


def _pixel_scale_deg(nside: int) -> float:
    area_sr = 4.0 * np.pi / float(hp.nside2npix(nside))
    return np.degrees(np.sqrt(area_sr))


def _build_reference_simple(nside: int) -> np.ndarray:
    # reference uses the same analytical function as the experiment script
    npix = hp.nside2npix(nside)
    theta, phi = hp.pix2ang(nside, np.arange(npix), nest=False)
    dec = np.pi / 2.0 - theta
    ra = phi
    return np.sin(dec) + 0.5 * np.cos(2.0 * ra)
