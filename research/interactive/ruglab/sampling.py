"""Explicit original-grid phases and array sampling."""

import numpy as np

from .specs import SAMPLINGS


def coordinates(shape, sampling="full", origin=(0, 0)):
    if sampling not in SAMPLINGS:
        raise ValueError(sampling)
    # Rows represent y; columns represent x.
    j, i = np.indices(shape, dtype=object)
    i, j = i + origin[0], j + origin[1]
    if sampling == "full":
        return i, j
    if sampling.startswith("checkerboard"):
        return i + j + (sampling == "checkerboard_opposite"), i - j
    ex, ey = {"even_even": (0, 0), "even_odd": (0, 1), "odd_even": (1, 0), "odd_odd": (1, 1)}[sampling]
    return 2 * i + ex, 2 * j + ey


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
