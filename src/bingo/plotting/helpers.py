"""Small helpers for publication figures."""

from __future__ import annotations


def panel_label(
    ax,
    label,
    x=0.03,
    y=0.95,
    **kwargs,
):
    """
    Add a panel identifier such as ``(a)`` or ``(b)``.
    """
    defaults = {
        "transform": ax.transAxes,
        "ha": "left",
        "va": "top",
        "fontweight": "bold",
        "fontsize": 8,
    }

    defaults.update(kwargs)

    return ax.text(
        x,
        y,
        label,
        **defaults,
    )


def enable_minor_ticks(ax):
    """Enable minor ticks using the current publication style."""
    ax.minorticks_on()


def outward_colorbar_ticks(colorbar):
    """
    Normalize colorbar tick appearance.

    Useful for image-like figures where the main axes use inward ticks
    but the colorbar benefits from conventional outward ticks.
    """
    colorbar.ax.tick_params(direction="out")
