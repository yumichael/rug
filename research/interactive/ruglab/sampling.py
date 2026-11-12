"""Explicit original-grid phases and array sampling."""

import numpy as np

from .specs import ADDITIONAL_SAMPLINGS, SAMPLINGS

CARTESIAN_PHASES = {"even_even": (0, 0), "even_odd": (0, 1), "odd_even": (1, 0), "odd_odd": (1, 1)}


def checkerboard_indices(x, y, sampling, *, axis="horizontal"):
    phase = int(sampling == "checkerboard_opposite")
    if axis == "vertical":
        # The opposite-parity tile starts with the preceding row of its period.
        x, y = y - phase, x
    elif axis != "horizontal":
        raise ValueError("Checkerboard axis must be horizontal or vertical")
    return x + y + phase, x - y


def coordinates(shape, sampling="full", origin=(0, 0), *, checkerboard_axis="horizontal"):
    """Map displayed columns and rows to unsampled operand indices."""
    if sampling not in SAMPLINGS:
        raise ValueError(sampling)
    # Rows represent y; columns represent x.
    j, i = np.indices(shape, dtype=object)
    i, j = i + origin[0], j + origin[1]
    if sampling == "full":
        return i, j
    if sampling == "doubled_checkerboard_opposite":
        return i + ((i + j) % 2 == 0), j
    if sampling.startswith("checkerboard"):
        return checkerboard_indices(i, j, sampling, axis=checkerboard_axis)
    ex, ey = CARTESIAN_PHASES[sampling]
    return 2 * i + ex, 2 * j + ey


def resample_view(values, sampling="full"):
    """Resample a finished view, using its top left as the parity origin."""
    if sampling == "full":
        return values
    if sampling in CARTESIAN_PHASES:
        x, y = CARTESIAN_PHASES[sampling]
        return values[y::2, x::2]
    if sampling not in ADDITIONAL_SAMPLINGS:
        raise ValueError("Unknown sampling: " + sampling)
    n = values.shape[0]
    if values.shape[1] != n or n < 2 or n % 2:
        raise ValueError("Additional checkerboard sampling requires an even square")
    if sampling == "doubled_checkerboard_opposite":
        # Copy opposite-parity cells into their left neighbours, wrapping
        # the first column into the last column on odd rows.
        doubled = values.copy()
        doubled[0::2, 0::2] = values[0::2, 1::2]
        doubled[1::2, 1::2] = np.roll(values[1::2, 0::2], -1, axis=1)
        return doubled
    # Walk down the x=y direction and across the other diagonal. A half-size
    # grid fits inside the source; offset one cell to select the other parity.
    half = n // 2
    row = np.arange(half)[:, None]
    col = np.arange(half)[None, :]
    phase = int(sampling == "checkerboard_opposite")
    offset = half - 1 + (phase ^ ((half - 1) % 2))
    return values[row - col + offset, row + col]


def legacy_sample(z, name):
    n = z.shape[0]
    if z.shape != (n, n) or n % 2:
        raise ValueError("Legacy sampling requires an even square")
    if name == "skip":
        return z[1::2, 1::2].copy()
    i, j = np.indices((n // 2, n // 2))
    if name in ("diag1m", "diag1m_1"):
        i, j = i + n // 4, j + n // 4
    if name in ("diag0", "ddiag0"):
        out = z[(n // 2 + i - j) % n, (-n // 2 + i + j) % n].T
    elif name == "diag1m_1":
        out = z[(n // 2 + i - j) % n, (-n // 2 + 1 + i + j) % n]
    else:
        out = z[(n // 2 - 1 + i - j) % n, (-n // 2 + i + j) % n]
    if name.startswith("ddiag"):
        i, j = np.indices((n, n))
        out = z[(n // 2 - (name == "ddiag1") + i - j) % n, (-n // 2 + i + j) % n]
        if name == "ddiag0":
            out = out.T
    return out
