"""High-level interface for BINGO publication figures."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from .colors import DEFAULT_CYCLE
from .dimensions import figsize
from .helpers import panel_label

STYLE_FILE = Path(__file__).with_name("jai.mplstyle")


# ----------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------


def use_style():
    """
    Apply the publication style globally.

    Prefer ``style()`` when the plotting configuration should remain
    local to a specific figure or block of code.
    """
    plt.style.use(STYLE_FILE)

    mpl.rcParams["axes.prop_cycle"] = DEFAULT_CYCLE


@contextmanager
def style():
    """
    Context manager for publication plotting.

    Examples
    --------
    >>> with style():
    ...     fig, ax = subplots()
    """
    with plt.style.context(STYLE_FILE):
        old_cycle = mpl.rcParams["axes.prop_cycle"]

        mpl.rcParams["axes.prop_cycle"] = DEFAULT_CYCLE

        try:
            yield
        finally:
            mpl.rcParams["axes.prop_cycle"] = old_cycle


# ----------------------------------------------------------------------
# Figure creation
# ----------------------------------------------------------------------


def figure(
    width="single",
    kind="default",
    aspect=None,
    **kwargs,
):
    """
    Create a publication-sized Matplotlib figure.
    """
    size = figsize(
        width_spec=width,
        kind=kind,
        aspect=aspect,
    )

    return plt.figure(
        figsize=size,
        **kwargs,
    )


def subplots(
    nrows=1,
    ncols=1,
    width="single",
    kind="default",
    aspect=None,
    **kwargs,
):
    """
    Create publication-sized Matplotlib subplots.
    """
    size = figsize(
        width_spec=width,
        kind=kind,
        aspect=aspect,
    )

    return plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=size,
        **kwargs,
    )


# ----------------------------------------------------------------------
# Specialized figures
# ----------------------------------------------------------------------


def map_figure(
    width="double",
    **kwargs,
):
    """Create a figure appropriate for sky maps."""
    return figure(
        width=width,
        kind="map",
        **kwargs,
    )


def waterfall_figure(
    width="double",
    **kwargs,
):
    """Create a figure appropriate for waterfall plots."""
    return figure(
        width=width,
        kind="waterfall",
        **kwargs,
    )


# ----------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------


def savefig(
    fig,
    filename,
    formats=("pdf", "eps"),
    dpi=600,
    close=False,
    **kwargs,
):
    """
    Export a figure in publication formats.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    filename : str or Path
        Output filename without extension.
    formats : sequence of str
        Output formats.
    dpi : int
        Resolution used for rasterized components.
    close : bool
        Close the figure after export.
    """
    path = Path(filename)

    if path.suffix:
        path = path.with_suffix("")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    defaults = {
        "bbox_inches": "tight",
        "pad_inches": 0.02,
        "dpi": dpi,
    }

    defaults.update(kwargs)

    outputs = []

    for fmt in formats:
        output = path.with_suffix(f".{fmt}")

        fig.savefig(
            output,
            format=fmt,
            **defaults,
        )

        outputs.append(output)

    if close:
        plt.close(fig)

    return outputs


__all__ = [
    "figure",
    "map_figure",
    "panel_label",
    "savefig",
    "style",
    "subplots",
    "use_style",
    "waterfall_figure",
]
