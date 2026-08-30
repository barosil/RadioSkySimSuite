from datetime import datetime, timedelta
import xarray as xr
from rinex_downloader import run

timestamp = datetime(2024, 6, 10, 12, 0)
station = "braz"

run(timestamp, station, "rinex_full_day.nc")

# recorte de 1h
ds = xr.open_dataset("rinex_full_day.nc")

ds_1h = ds.sel(time=slice(timestamp, timestamp + timedelta(hours=1)))
ds_1h.to_netcdf("rinex_1hour.nc")

print("Done!")

'''
from datetime import datetime
from rinex_downloader import run

timestamp = datetime(2024, 6, 10, 12, 0)
station = "brft"
out_nc = "rinex_15min.nc"

run(timestamp, station, out_nc)
'''