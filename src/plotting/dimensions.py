"""Physical dimensions for publication figures."""

from __future__ import annotations

MM = 1.0 / 25.4

# ----------------------------------------------------------------------
# Journal dimensions
# ----------------------------------------------------------------------

# Physical widths in millimetres.
#
# These values are intentionally centralized. If the journal template
# requires different dimensions, only these constants need to change.

SINGLE_COLUMN_MM = 85.0
DOUBLE_COLUMN_MM = 175.0

SINGLE_COLUMN = SINGLE_COLUMN_MM * MM
DOUBLE_COLUMN = DOUBLE_COLUMN_MM * MM


# ----------------------------------------------------------------------
# Aspect ratios
# ----------------------------------------------------------------------

GOLDEN_RATIO = (5**0.5 - 1.0) / 2.0

ASPECT_RATIOS = {
    "default": GOLDEN_RATIO,
    "wide": 0.50,
    "square": 1.00,
    "map": 0.55,
    "waterfall": 0.65,
}


def width(value="single"):
    """
    Convert a width specification to inches.

    Parameters
    ----------
    value : {"single", "double"} or float
        Named journal width or explicit width in millimetres.

    Returns
    -------
    float
        Width in inches.
    """
    if value == "single":
        return SINGLE_COLUMN

    if value == "double":
        return DOUBLE_COLUMN

    if isinstance(value, (int, float)):
        return float(value) * MM

    msg = "width must be 'single', 'double', or a number in millimetres"
    raise ValueError(msg)


def figsize(width_spec="single", kind="default", aspect=None):
    """
    Return a Matplotlib figsize tuple.

    Parameters
    ----------
    width_spec : {"single", "double"} or float
        Figure width.
    kind : str
        Named aspect-ratio preset.
    aspect : float, optional
        Explicit height / width ratio. Overrides ``kind``.
    """
    w = width(width_spec)

    if aspect is None:
        try:
            aspect = ASPECT_RATIOS[kind]
        except KeyError:
            msg = f"unknown figure kind: {kind!r}"
            raise ValueError(msg) from None

    return w, w * aspect
