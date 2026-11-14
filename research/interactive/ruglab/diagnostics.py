"""Exact signatures; period measurements describe the supplied window only."""

import math

import numpy as np


def anchored(result):
    if result.modulus is None:
        raise ValueError("Declare an integer modulus for exact diagnostics")
    return (result.values - int(result.values.flat[0])) % result.modulus


def ranks(result, *, anchor=None):
    if anchor is None:
        a = anchored(result)
    else:
        if result.modulus is None:
            raise ValueError("Declare an integer modulus for exact diagnostics")
        a = (result.values - anchor) % result.modulus
    lookup = {v: i for i, v in enumerate(sorted(set(a.flat)))}
    return np.asarray(np.frompyfunc(lookup.__getitem__, 1, 1)(a), dtype=int)


def signature(result, kind="shift"):
    if kind == "order":
        return (result.values.shape, tuple(ranks(result).flat))
    if kind != "shift":
        raise ValueError(kind)
    a = anchored(result)
    g = math.gcd(result.modulus, *map(int, a.flat))
    return (a.shape, result.modulus // g, tuple(int(x) // g for x in a.flat))


def summary(result):
    a = result.values
    return {
        "shape": a.shape,
        "M": result.modulus,
        "distinct_values": len(set(a.flat)),
        "zero_fraction": sum(x == 0 for x in a.flat) / a.size,
        "scope": "supplied window; certify a full torus before claiming global periods",
    }


def periods(result, *, certified_torus=False):
    if not certified_torus:
        raise ValueError("Pass a known complete periodic torus, not a crop")
    a = result.values
    return tuple(
        next(
            h
            for h in range(1, a.shape[axis] + 1)
            if a.shape[axis] % h == 0 and np.array_equal(a, np.roll(a, h, axis=axis))
        )
        for axis in (1, 0)
    )


def symmetries(result):
    a = result.values
    return {
        "scope": "reflections about the supplied window center",
        "horizontal": np.array_equal(a, a[:, ::-1]),
        "vertical": np.array_equal(a, a[::-1, :]),
        "transpose": np.array_equal(a, a.T),
        "anti_transpose": np.array_equal(a, a[::-1, ::-1].T),
        "quarter_turn": np.array_equal(a, np.rot90(a)),
    }


def duplicates(items, kind="order"):
    groups = {}
    for name, r in items:
        groups.setdefault(signature(r, kind), []).append(name)
    return list(groups.values())
