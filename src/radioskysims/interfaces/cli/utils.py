# src/radioskysims/interfaces/cli/utils.py

import healpy as hp
import numpy as np


def save_map_fits(
    map_data: np.ndarray,
    filename: str,
    overwrite: bool = True,
) -> None:
    """
    Save a HEALPix map to a FITS file.
    """
    hp.write_map(
        filename,
        map_data,
        overwrite=overwrite,
    )
