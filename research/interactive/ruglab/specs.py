"""Serializable specifications; all numerical choices are explicit."""

from copy import deepcopy

SAMPLINGS = (
    "full",
    "checkerboard_same",
    "doubled_checkerboard_opposite",
    "checkerboard_opposite",
    "even_even",
    "even_odd",
    "odd_even",
    "odd_odd",
)
ADDITIONAL_SAMPLINGS = SAMPLINGS
COMBINERS = (
    "and",
    "or",
    "xor",
    "add",
    "mult",
    "clmul",
    "absdiff",
    "gcd",
    "min",
    "max",
    "subtract",
    "xor0",
)


def resolve(spec):
    s = deepcopy(spec)
    n = s.setdefault("n", 64)
    s.setdefault("shape", [n, n])
    s.setdefault("origin", [0, 0])
    s.setdefault("sampling", "full")
    s.setdefault("K", n)
    s.setdefault("M", n)
    s.setdefault("pre", [])
    s.setdefault("post", [])
    s.setdefault("combine", "xor")
    if s["sampling"] not in SAMPLINGS:
        raise ValueError("Unknown sampling: " + s["sampling"])
    if s.get("checkerboard_axis", "horizontal") not in ("horizontal", "vertical"):
        raise ValueError("Checkerboard axis must be horizontal or vertical")
    if len(s["shape"]) != 2 or any(not isinstance(v, int) or v < 1 for v in s["shape"]):
        raise ValueError("shape must contain two positive integers")
    for key in ("K", "M"):
        if not isinstance(s[key], int) or s[key] < 1:
            raise ValueError(key + " must be a positive integer")
    return s
