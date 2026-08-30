"""Análise da montagem do BINGO.

Pacote que concentra a lógica de análise (antes espalhada no notebook) para
manter o ``02_BINGO_ANALYSIS.ipynb`` limpo e organizado:

- ``loading``        : carga lazy (sim/obs), análise de chunks, redução de
                       polarização e criação de ``sim_data_reduced``.
- ``observation``    : classe ``ObservationData`` com métodos de manipulação
                       encadeáveis (sufixos de xarray): resample (integração),
                       slice, quiet signal, normalização, alinhamento temporal.
- ``calibration``    : fit por canal ``D = a + g·T_sim`` e aplicação.
- ``visualization``  : waterfall, medianas temporais e calibração com
                       HoloViews + Datashader.
"""

from __future__ import annotations

from ._utils import scale_window
from .calibration import (
    apply_calibration,
    dt_to_dtheta,
    fit_calibration,
    fit_calibration_dt,
)
from .loading import (
    CO_POLARIZATIONS,
    K_B,
    analyze_chunks,
    build_obs_cache,
    list_sources,
    load_obs_lazy,
    load_sim_data_reduced,
    load_sim_lazy,
    load_sim_sources,
    reduce_polarization,
)
from .observation import ObservationData, estimate_time_lag
from .rfi import (
    adaptive_baseline,
    arpls_baseline,
    effective_band,
    flag_rfi_sed,
    mad_filter,
    mask_rfi,
    mask_rfi_channels,
    spectral_normalization,
)
from .visualization import (
    calibration_plot,
    dt_profile_plot,
    temporal_median_plot,
    waterfall_plot,
)

__all__ = [
    "CO_POLARIZATIONS",
    "K_B",
    "ObservationData",
    "adaptive_baseline",
    "analyze_chunks",
    "apply_calibration",
    "arpls_baseline",
    "build_obs_cache",
    "calibration_plot",
    "dt_profile_plot",
    "dt_to_dtheta",
    "effective_band",
    "estimate_time_lag",
    "fit_calibration",
    "fit_calibration_dt",
    "flag_rfi_sed",
    "list_sources",
    "load_obs_lazy",
    "load_sim_data_reduced",
    "load_sim_lazy",
    "load_sim_sources",
    "mad_filter",
    "mask_rfi",
    "mask_rfi_channels",
    "reduce_polarization",
    "scale_window",
    "spectral_normalization",
    "temporal_median_plot",
    "waterfall_plot",
]
