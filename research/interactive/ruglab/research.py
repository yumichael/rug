"""Exact period rules and samplers for the workbench."""

import math
import random

from .engine import evaluate
from .specs import resolve


def family_pre_modulus(q, R, combiner):
    if q < 2 or q % 2 or R < 8 or R & (R - 1):
        raise ValueError("Use even q>=2 and dyadic R>=8")
    w = (q & -q).bit_length() - 1
    r = R.bit_length() - 1
    if combiner in ("or", "xor", "add", "absdiff"):
        k = r + w
    elif combiner in ("mult", "clmul"):
        k = max(r + w, q + 1)
    elif combiner == "and":
        threshold = r + w - 1
        j = max(4, threshold) if q == 2 else q if threshold <= q else max(q + w + 2, threshold)
        k = j + 1
    else:
        raise ValueError("No proved family rule for this combiner")
    return 1 << k


def _valuation(n):
    return (abs(n) & -abs(n)).bit_length() - 1 if n else math.inf


def _power_depth(a, b, p):
    """Return the 2-adic valuation of a**p - b**p without building either power."""
    if a == b:
        return math.inf
    if not a or not b:
        return p * _valuation(a or b)
    ta, tb = _valuation(a), _valuation(b)
    if ta != tb:
        return p * min(ta, tb)
    a0, b0 = a >> ta, b >> tb
    depth = p * ta + _valuation(a0 - b0)
    if p % 2 == 0:
        depth += _valuation(a0 + b0) + _valuation(p) - 1
    return depth


def _shift_depth(table, shift, axis, power):
    size = len(table)
    if axis == 0:
        pairs = {(table[i][j], table[(i + shift) % size][j]) for i in range(size) for j in range(size)}
    else:
        pairs = {(table[i][j], table[i][(j + shift) % size]) for i in range(size) for j in range(size)}
    return min(_power_depth(a, b, power) for a, b in pairs)


def minimum_post_modulus(spec, target, power=1, max_cells=262144):
    s = resolve(spec)
    K = s["K"]
    if max_cells < K * K:
        raise ValueError("Full-torus check exceeds max_cells; use an analytical rule or explicitly raise the limit")
    if isinstance(s["combine"], list) or "expression" in s:
        raise ValueError("This helper handles one basic combiner and one post-power")
    if power < 1:
        raise ValueError("power must be positive")
    targets = (target, target) if isinstance(target, int) else tuple(target)
    if any(R < 1 or R & (R - 1) for R in targets):
        raise ValueError("Targets must be positive powers of two")
    r = evaluate({**s, "shape": [K, K], "post": [], "M": 1})
    # Targets are in x, y order. Transpose the row-major grid to match.
    table = r.stages["z0"].T.tolist()
    lower, upper = 1, math.inf
    for axis, period in enumerate(targets):
        # The target shift must vanish, while its half-shift must stay visible.
        upper = min(upper, _shift_depth(table, period, axis, power))
        if period > 1:
            lower = max(lower, 1 + _shift_depth(table, period // 2, axis, power))
    return 1 << lower if lower <= upper and lower != math.inf else None


def uniform_xor(C=64, seed=0, parity="both", sampling="checkerboard_same"):
    if C < 32 or C & (C - 1):
        raise ValueError("C must be a power of two >=32")
    if sampling not in ("full", "checkerboard_same", "checkerboard_opposite"):
        raise ValueError("Sampler theorem covers full grid and checkerboard sampling")
    rng = random.Random(seed)
    if parity == "both":
        parity = "odd" if rng.randrange(9) < 8 else "even"
    if parity not in ("odd", "even"):
        raise ValueError("parity must be odd, even, or both")
    p = 2 * rng.randrange(C // 8) + 1 if parity == "odd" else 2 * (1 + rng.randrange(C // 32))
    v = (p & -p).bit_length() - 1
    M = C << v
    Q = C // (2 if parity == "odd" else 4)
    a = 2 * rng.randrange(Q // 2) + 1
    return {
        "n": C,
        "shape": [C // 2, C // 2],
        "K": C,
        "M": M,
        "coordinates": "historical",
        "sampling": sampling,
        "pre": [],
        "combine": "xor",
        "post": [["pow", p], ["mult", a], ["add", -a]],
        "seed": seed,
    }
