"""Colour and line conventions for scientific figures."""

from __future__ import annotations

from cycler import cycler

# ----------------------------------------------------------------------
# Colour palette
# ----------------------------------------------------------------------

# Okabe-Ito inspired palette.
# Designed to remain reasonably accessible under common forms of
# colour-vision deficiency.

BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
RED = "#D55E00"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
YELLOW = "#F0E442"
BLACK = "#000000"
GREY = "#777777"


COLORS = (
    BLUE,
    ORANGE,
    GREEN,
    RED,
    PURPLE,
    SKY,
)


# ----------------------------------------------------------------------
# Default plotting cycle
# ----------------------------------------------------------------------

# Colour and linestyle are both varied so that curves remain
# distinguishable when printed in grayscale.

LINESTYLES = (
    "-",
    "--",
    "-.",
    ":",
    "-",
    "--",
)


DEFAULT_CYCLE = cycler(color=COLORS) + cycler(linestyle=LINESTYLES)


# ----------------------------------------------------------------------
# Semantic conventions
# ----------------------------------------------------------------------

MEASUREMENT = {
    "color": BLUE,
    "linestyle": "-",
}

MODEL = {
    "color": ORANGE,
    "linestyle": "--",
}

SIMULATION = {
    "color": GREEN,
    "linestyle": "-.",
}

REFERENCE = {
    "color": GREY,
    "linestyle": ":",
}
