"""Adapters for proved modulus rules; no automatic execution of research reports."""

import importlib.util
import random
import sys
from functools import lru_cache
from pathlib import Path

from .engine import evaluate


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


@lru_cache(maxsize=1)
def _theory():
    theory_dir = Path(__file__).resolve().parents[2] / "theory"
    path = theory_dir / "2026-11-03-combiners-and-order-classes/combiners_order_classes.py"
    spec = importlib.util.spec_from_file_location("_rug_theory", path)
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


def minimum_post_modulus(spec, target, power=1, max_cells=262144):
    from .specs import resolve

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
    # The research helper indexes x first; native arrays index rows/y first.
    table = r.stages["z0"].T.tolist()
    m = _theory().minimum_post_exponent(table, targets, power)
    return None if m is None else 1 << m


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
