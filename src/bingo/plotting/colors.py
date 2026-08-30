"""Colour and line conventions for scientific figures.

The palette follows the Okabe-Ito colour-blind-safe scheme (8 colours)
plus a neutral ``gray60``, reordered so that the automatic cycle starts
with orange. Named styles pair a colour with a linestyle so that curves
remain distinguishable even when printed in grayscale.
"""

from __future__ import annotations

from cycler import cycler

# ----------------------------------------------------------------------
# Okabe-Ito palette (9 colours, starting with orange)
# ----------------------------------------------------------------------

ORANGE = "#E69F00"  # primary data
SKY_BLUE = "#56B4E9"
BLUISH_GREEN = "#009E73"
YELLOW = "#F0E442"
BLUE = "#0072B2"
VERMILLION = "#D55E00"
REDDISH_PURPLE = "#CC79A7"
BLACK = "#000000"
GRAY60 = "#999999"  # neutral

# Canonical Okabe-Ito order (reference only).
OKABE_ITO = (
    BLACK,
    ORANGE,
    SKY_BLUE,
    BLUISH_GREEN,
    YELLOW,
    BLUE,
    VERMILLION,
    REDDISH_PURPLE,
)

# Publication cycle order: starts with orange.
COLORS = (
    ORANGE,
    SKY_BLUE,
    BLUISH_GREEN,
    YELLOW,
    BLUE,
    VERMILLION,
    REDDISH_PURPLE,
    BLACK,
    GRAY60,
)

# Linestyles paired 1:1 with COLORS.
LINESTYLES = (
    "-",
    "--",
    "-.",
    ":",
    "-",
    "--",
    "-.",
    ":",
    "-",
)

DEFAULT_CYCLE = cycler(color=COLORS) + cycler(linestyle=LINESTYLES)


# ----------------------------------------------------------------------
# Named styles (colour paired with linestyle)
# ----------------------------------------------------------------------


def _style(color: str, linestyle: str) -> dict[str, str]:
    """Build a named style dict pairing ``color`` with ``linestyle``."""
    return {"color": color, "linestyle": linestyle}


# Canonical pairings, consistent with ``DEFAULT_CYCLE``.
STYLES = {
    "orange": _style(ORANGE, "-"),
    "sky_blue": _style(SKY_BLUE, "--"),
    "green": _style(BLUISH_GREEN, "-."),
    "yellow": _style(YELLOW, ":"),
    "blue": _style(BLUE, "-"),
    "vermillion": _style(VERMILLION, "--"),
    "purple": _style(REDDISH_PURPLE, "-."),
    "black": _style(BLACK, ":"),
    "gray60": _style(GRAY60, "-"),
}


def get_style(name: str) -> dict[str, str]:
    """
    Return a copy of the named style ``name``.

    Parameters
    ----------
    name : str
        One of the keys of :data:`STYLES`.

    Raises
    ------
    KeyError
        If ``name`` is not a registered style.
    """
    return dict(STYLES[name])


# ----------------------------------------------------------------------
# Semantic conventions
#
# Each semantic style pairs a colour with a distinct linestyle so that
# curves remain distinguishable when printed in grayscale.
# ----------------------------------------------------------------------

MEASUREMENT = {"color": ORANGE, "linestyle": "-"}
MODEL = {"color": BLUE, "linestyle": "--"}
SIMULATION = {"color": BLUISH_GREEN, "linestyle": "-."}
REFERENCE = {"color": GRAY60, "linestyle": ":"}

# Semantic aliases registered for lookup via ``get_style``.
STYLES.update(
    {
        "measurement": MEASUREMENT,
        "model": MODEL,
        "simulation": SIMULATION,
        "reference": REFERENCE,
    }
)


__all__ = [
    "BLACK",
    "BLUE",
    "BLUISH_GREEN",
    "COLORS",
    "DEFAULT_CYCLE",
    "GRAY60",
    "LINESTYLES",
    "MEASUREMENT",
    "MODEL",
    "OKABE_ITO",
    "ORANGE",
    "REDDISH_PURPLE",
    "REFERENCE",
    "SIMULATION",
    "SKY_BLUE",
    "STYLES",
    "VERMILLION",
    "YELLOW",
    "get_style",
]
