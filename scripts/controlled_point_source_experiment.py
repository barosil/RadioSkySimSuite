"""Experimento controlado: fonte pontual transitando no boresight.

Gera TOD sem ruído, reconstrói mapas HEALPix e imprime métricas
pedidas na tarefa do revisor.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import healpy as hp
import numpy as np
import xarray as xr
from scipy.constants import k as k_B

from radioskysims_beam.domain.beam.models import Beam
from radioskysims_core.domain.common.models import Observer, TimeRange
from radioskysims_core.domain.geometry.pointing import compute_pointing_track
from radioskysims_sources.domain.signal_source import compute_theta_boresight
from radioskysims_simulation.domain.tod.simulator import TODSimulator
from radioskysims_simulation.infrastructure.mapmaking.healpy_binned import HealpyBinnedMapMakerAdapter


@dataclass
class SimplePointSource:
    ra_deg: float
    dec_deg: float
    time_grid: np.ndarray
    flux_w_m2_hz: float = 1e-26

    def psd(self) -> xr.DataArray:
        freq = np.array([1.0e9], dtype=float)
        da = xr.DataArray(
            np.array([self.flux_w_m2_hz], dtype=float),
            dims=("frequency",),
            coords={"frequency": freq},
        )
        da.attrs["units"] = "W/m²/Hz"
        return da

    def tracks(self) -> xr.Dataset:
        n = len(self.time_grid)
        return xr.Dataset(
            data_vars={
                "ra": ("time", np.full(n, np.deg2rad(self.ra_deg))),
                "dec": ("time", np.full(n, np.deg2rad(self.dec_deg))),
            },
            coords={"time": self.time_grid},
        )

    # API compat for TODSimulator
    def angle(self) -> xr.DataArray:
        # placeholder; we will pass explicit angle to simulate_from_source
        return xr.DataArray(
            np.zeros(len(self.time_grid)), dims=("time",), coords={"time": self.time_grid}
        )

    def range(self) -> xr.DataArray:
        return xr.DataArray(
            np.full(len(self.time_grid), 1e20), dims=("time",), coords={"time": self.time_grid}
        )


def build_gaussian_beam(fwhm_deg: float = 0.6) -> Beam:
    sigma = fwhm_deg / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    angles = np.linspace(-5.0, 5.0, 2001)
    amp = np.exp(-0.5 * (angles / sigma) ** 2)
    ds = xr.Dataset(
        {"amplitude": (("angle", "frequency"), amp[:, None])},
        coords={"angle": angles, "frequency": np.array([1.0e9])},
    )
    ds["angle"].attrs["units"] = "deg"
    ds["frequency"].attrs["units"] = "Hz"
    return Beam(ds)


def run_experiment():
    # Parâmetros fornecidos
    observer = Observer(
        lat="-7d13m",
        lon="-35d52m",
        height=550.0,
        timeframe=TimeRange.from_iso("2026-07-26T00:00:00", "2026-07-26T00:10:00", resolution=5.0),
    )

    # Build time grid as numpy datetime64 array
    time_grid = np.array(
        [np.datetime64(t) for t in observer.timeframe.to_astropy().iso], dtype="datetime64[ns]"
    )

    # Compute pointing RA/Dec temporal for fixed alt/az
    pointing_track = compute_pointing_track(observer, time_grid, alt_deg=60.0, az_deg=180.0)

    # select central instant t0
    n = len(time_grid)
    idx_center = n // 2
    ra_t0 = float(pointing_track["ra"].values[idx_center])
    dec_t0 = float(pointing_track["dec"].values[idx_center])

    # Build source positioned to transit boresight at t0
    src = SimplePointSource(ra_deg=ra_t0, dec_deg=dec_t0, time_grid=time_grid)

    # compute angular separation time series
    tracks_ds = src.tracks()
    theta = compute_theta_boresight(
        tracks_ds,
        pointing_track_ra=pointing_track["ra"].values,
        pointing_track_dec=pointing_track["dec"].values,
    )

    # Build beam and TOD simulator
    beam = build_gaussian_beam(fwhm_deg=0.6)
    tod = TODSimulator(beam=beam, gain=1.0, effective_area_m2=1.0)

    # Run sim: pass angle explicitly
    ds = tod.simulate_from_source(sat=src, angle=theta)

    # Select channel frequency
    freq_hz = float(ds["frequency"].values[0])

    t_vals = np.asarray(ds["T_antenna"].sel(frequency=freq_hz).squeeze().values, dtype=float)

    # A) Geometry
    idx_max = int(np.nanargmax(t_vals))
    t_max = np.datetime_as_string(time_grid[idx_max], unit="s")
    theta_min_rad = float(theta.min().values)
    theta_min_deg = math.degrees(theta_min_rad)
    theta_min_arcsec = theta_min_deg * 3600.0

    # B) Radiometry
    T_A_max = float(t_vals[idx_max])
    # Beam response at theta_peak
    # Build angle DataArray with single time entry to match xarray dims
    angle_da = xr.DataArray(
        np.array([theta[idx_max].values]),
        dims=("time",),
        coords={"time": np.array([time_grid[idx_max]])},
    )
    beam_resp = beam.evaluate(
        frequency=xr.DataArray([freq_hz], dims=("frequency",), coords={"frequency": [freq_hz]}),
        angle=angle_da,
    )
    # beam.evaluate returns DataArray possibly with shape (frequency,)
    B_theta_peak = float(beam_resp.squeeze().values)

    T_expected = (1.0 * B_theta_peak * 1.0 * 1e-26) / (2.0 * k_B)
    rel_err = (T_A_max - T_expected) / T_expected if T_expected != 0 else float("nan")
    T_onaxis = (1.0 * 1e-26) / (2.0 * k_B)

    # C) Angular profile: FWHM along scan
    # Build a signed scan coordinate relative to the peak sample using pointing RA/Dec
    ra_pt = np.asarray(pointing_track["ra"].values, dtype=float)
    dec_pt = np.asarray(pointing_track["dec"].values, dtype=float)

    ra_peak = float(ra_pt[idx_max])
    dec_peak = float(dec_pt[idx_max])

    # Convert pointing to radians for trigonometric functions (pointing_track uses degrees)
    ra_pt_rad = np.deg2rad(ra_pt)
    dec_pt_rad = np.deg2rad(dec_pt)
    ra_peak_rad = math.radians(ra_peak)
    dec_peak_rad = math.radians(dec_peak)

    # angular distance to peak for each sample (always positive)
    cos_gamma = np.sin(dec_pt_rad) * math.sin(dec_peak_rad) + np.cos(dec_pt_rad) * math.cos(
        dec_peak_rad
    ) * np.cos(ra_pt_rad - ra_peak_rad)
    cos_gamma = np.clip(cos_gamma, -1.0, 1.0)
    ang_dist_rad = np.arccos(cos_gamma)
    ang_dist_deg = np.degrees(ang_dist_rad)

    # assign sign: negative for samples before peak, positive after
    idxs = np.arange(len(ang_dist_deg))
    sign = np.where(idxs < idx_max, -1.0, np.where(idxs > idx_max, 1.0, 0.0))
    scan_coord_deg = sign * ang_dist_deg

    half = T_A_max / 2.0

    # find left crossing: search backward from peak to find interval crossing half
    left_cross = float("nan")
    for i in range(idx_max - 1, -1, -1):
        y0 = t_vals[i]
        y1 = t_vals[i + 1]
        if (y0 - half) <= 0.0 <= (y1 - half) or (y0 - half) >= 0.0 >= (y1 - half):
            x0 = scan_coord_deg[i]
            x1 = scan_coord_deg[i + 1]
            if y1 == y0:
                left_cross = x0
            else:
                left_cross = x0 + (half - y0) * (x1 - x0) / (y1 - y0)
            break

    # find right crossing: search forward from peak to find interval crossing half
    right_cross = float("nan")
    for i in range(idx_max, len(t_vals) - 1):
        y0 = t_vals[i]
        y1 = t_vals[i + 1]
        if (y0 - half) <= 0.0 <= (y1 - half) or (y0 - half) >= 0.0 >= (y1 - half):
            x0 = scan_coord_deg[i]
            x1 = scan_coord_deg[i + 1]
            if y1 == y0:
                right_cross = x1
            else:
                right_cross = x0 + (half - y0) * (x1 - x0) / (y1 - y0)
            break

    if not (math.isnan(left_cross) or math.isnan(right_cross)):
        fwhm_recovered = right_cross - left_cross
    else:
        fwhm_recovered = float("nan")

    fwhm_error_pct = (
        100.0 * (fwhm_recovered - 0.6) / 0.6 if not math.isnan(fwhm_recovered) else float("nan")
    )

    # D) Flux recovery
    S_recovered_w = 2.0 * k_B * T_A_max / (1.0 * B_theta_peak * 1.0)
    S_recovered_jy = S_recovered_w / 1e-26
    flux_err_rel = (S_recovered_jy - 1.0) / 1.0

    # E) Mapmaking
    map_maker = HealpyBinnedMapMakerAdapter()
    nsides = [256, 512, 1024, 2048]
    map_results = {}
    for nside in nsides:
        res = map_maker.make_map(
            tod=ds, pointing_track=pointing_track, frequency_hz=freq_hz, nside=nside
        )
        map_data = res.skymap.data
        hit_map = res.hit_map
        pix_max = int(np.argmax(map_data))
        hp.nside2npix(nside)
        # pixel area (sr)
        area_sr = hp.nside2pixarea(nside)
        area_deg2 = area_sr * (180.0 / math.pi) ** 2
        pixel_scale_deg = math.degrees(math.sqrt(area_sr))
        # pixel center coords
        theta_pix, phi_pix = hp.pix2ang(nside, pix_max, nest=False)
        ra_pix_deg = math.degrees(phi_pix)
        dec_pix_deg = 90.0 - math.degrees(theta_pix)
        # separation to true source
        # convert to radians
        ra1 = math.radians(ra_pix_deg)
        dec1 = math.radians(dec_pix_deg)
        ra2 = math.radians(ra_t0)
        dec2 = math.radians(dec_t0)
        cos_gamma = math.sin(dec1) * math.sin(dec2) + math.cos(dec1) * math.cos(dec2) * math.cos(
            ra1 - ra2
        )
        cos_gamma = max(-1.0, min(1.0, cos_gamma))
        sep_deg = math.degrees(math.acos(cos_gamma))

        map_results[nside] = {
            "nside": nside,
            "pixel_area_deg2": area_deg2,
            "pixel_scale_deg": pixel_scale_deg,
            "sep_deg": sep_deg,
            "sep_over_scale": sep_deg / pixel_scale_deg if pixel_scale_deg > 0 else float("nan"),
            "T_map_max_over_T_tod_max": float(map_data[pix_max] / T_A_max)
            if T_A_max != 0
            else float("nan"),
            "hits_max_pixel": int(hit_map[pix_max]),
        }

    # F) nside=512 details
    r512 = map_results[512]
    res512_full = map_maker.make_map(
        tod=ds, pointing_track=pointing_track, frequency_hz=freq_hz, nside=512
    )
    hits = res512_full.hit_map
    total_pixels = hp.nside2npix(512)
    observed_pixels = int(np.sum(hits > 0))
    total_hits = int(np.sum(hits))
    hits_max = int(hits.max())
    area_deg2_512 = r512["pixel_area_deg2"]
    pixel_scale_deg_512 = r512["pixel_scale_deg"]
    sep_deg_512 = r512["sep_deg"]
    sep_in_pixel_scale = (
        sep_deg_512 / pixel_scale_deg_512 if pixel_scale_deg_512 > 0 else float("nan")
    )

    # Assemble report
    report = {
        "A_geometry": {
            "idx_max": idx_max,
            "t_max": t_max,
            "sep_min_deg": theta_min_deg,
            "sep_min_arcsec": theta_min_arcsec,
        },
        "B_radiometry": {
            "T_A_max_K": T_A_max,
            "B_theta_peak": B_theta_peak,
            "T_expected_K": T_expected,
            "rel_error": rel_err,
            "T_onaxis_K": T_onaxis,
        },
        "C_profile": {
            "half_max": half,
            "left_cross_deg": left_cross,
            "right_cross_deg": right_cross,
            "fwhm_recovered_deg": fwhm_recovered,
            "fwhm_error_pct": fwhm_error_pct,
        },
        "D_flux_recovery": {
            "S_recovered_Jy": S_recovered_jy,
            "flux_rel_error": flux_err_rel,
        },
        "E_healpix": map_results,
        "F_nside512": {
            "total_pixels": total_pixels,
            "observed_pixels": observed_pixels,
            "total_hits": total_hits,
            "hits_max": hits_max,
            "pixel_area_deg2": area_deg2_512,
            "pixel_scale_deg": pixel_scale_deg_512,
            "sep_deg": sep_deg_512,
            "sep_in_pixel_scale": sep_in_pixel_scale,
            "T_map_max_over_T_tod_max": r512["T_map_max_over_T_tod_max"],
        },
    }

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    run_experiment()
