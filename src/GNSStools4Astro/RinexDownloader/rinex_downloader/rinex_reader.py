import xarray as xr
import georinex as gr

def read_rinex_files(file_list):
    """
    Reads multiple RINEX files and concatenates them in time
    """
    datasets = []

    for f in file_list:
        ds = gr.load(f)
        datasets.append(ds)

    return xr.concat(datasets, dim="time")