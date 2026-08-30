"""Publication-quality plotting utilities for BINGO.

The default configuration follows the visual conventions adopted for
astronomy journal figures:

* Helvetica / Arial sans-serif fonts;
* Okabe-Ito colour-blind-safe palette (9 colours, starting with orange);
* named styles that pair a colour with a linestyle.

The high-level interface (:func:`jai.style`, :func:`jai.subplots`,
:func:`jai.savefig`, ...) is available through the :mod:`jai` submodule.

Example
-------
>>> from bingo.plotting import jai
>>> from bingo.plotting.colors import MEASUREMENT, MODEL
>>> with jai.style():
...     fig, ax = jai.subplots(width="single", kind="default")
...     ax.plot(x, y_obs, **MEASUREMENT, label="dados")
...     ax.plot(x, y_model, **MODEL, label="modelo")
...     ax.legend()
"""

from __future__ import annotations

from . import colors, dimensions, helpers, jai
from .colors import (
    MEASUREMENT,
    MODEL,
    REFERENCE,
    SIMULATION,
    STYLES,
    get_style,
)

__all__ = [
    "MEASUREMENT",
    "MODEL",
    "REFERENCE",
    "SIMULATION",
    "STYLES",
    "colors",
    "dimensions",
    "get_style",
    "helpers",
    "jai",
]
