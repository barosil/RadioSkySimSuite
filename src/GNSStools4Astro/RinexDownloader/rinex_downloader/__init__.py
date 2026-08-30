from datetime import datetime, timedelta
from .downloader import build_rinex_url, download_file
from .rinex_reader import read_rinex_files
from .config import CDDIS_BASE_URL
import os

def run(timestamp, station, out_nc):

    url = build_rinex_url(timestamp, station, "obs")

    output_dir = f"data/{station}_{timestamp:%Y%m%d}"

    rinex_files = download_file(url, output_dir)

    print("Arquivos encontrados:")
    for f in rinex_files:
        print(" -", f)

    ds = read_rinex_files(rinex_files)

    ds.to_netcdf(out_nc)

'''
def run(timestamp: datetime, station: str, out_nc: str):
    """
    Complete pipeline:
    - download obs and nav
    - concatenate
    - save in NetCDF
    """

    local_files_obs = []
    local_files_nav = []

    for minute in range(15):
        t = timestamp + timedelta(minutes=minute)

        obs_url = build_rinex_url(CDDIS_BASE_URL, t, station, "obs")
        nav_url = build_rinex_url(CDDIS_BASE_URL, t, station, "nav")

        obs_file = f"data/obs/{station}_{t:%Y%m%d_%H%M}.rnx"
        nav_file = f"data/nav/{station}_{t:%Y%m%d_%H%M}.nav"

        download_file(obs_url, obs_file)
        download_file(nav_url, nav_file)

        local_files_obs.append(obs_file)
        local_files_nav.append(nav_file)

    ds_obs = read_rinex_files(local_files_obs)
    ds_nav = read_rinex_files(local_files_nav)

    ds_obs.to_netcdf(out_nc.replace(".nc", "_obs.nc"))
    ds_nav.to_netcdf(out_nc.replace(".nc", "_nav.nc"))
    '''