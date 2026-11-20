"""First-pass catalogues at the smallest post-modulus retaining both axis periods."""

from dataclasses import dataclass
from functools import cached_property, lru_cache
from math import inf
from random import Random

import numpy as np
from ruglab.engine import evaluate
from ruglab.exploration import _study_twist
from ruglab.research import _power_depth, _valuation
from ruglab.sampler_comparison import power_groups

CHECKERBOARD = "checkerboard_opposite"
ODD_ODD = "odd_odd"
CHECKER_COMBINERS = ("or", "xor", "add", "absdiff")
ODD_COMBINERS = ("and", "or", "xor", "add", "absdiff", "mult", "clmul")
ODD_COSETS = ("and", "or", "add", "mult", "clmul")


def valuation(n):
    return (n & -n).bit_length() - 1


@dataclass(frozen=True)
class Base:
    size: int
    sampling: str
    combiner: str
    q: int
    twist: tuple[int, ...] = ()

    @property
    def K(self):
        return self.size << (valuation(self.q) + (self.sampling == ODD_ODD))

    def spec(self, p=1, a=1, M=1, phase=0):
        pre = [["pow", self.q]]
        if self.twist:
            pre.append(["poly", list(_study_twist(self.twist))])
        return {
            "n": self.size,
            "K": self.K,
            "M": M,
            "checkerboard_axis": "vertical",
            "sampling": self.sampling,
            "combine": self.combiner,
            "pre": pre,
            "post": [["pow", p], ["mult", a], ["add", phase]],
        }

    @cached_property
    def field(self):
        return evaluate(self.spec()).stages["z0"]

    @cached_property
    def labels(self):
        values, indices = np.unique(self.field, return_inverse=True)
        return tuple(map(int, values)), indices.reshape(self.field.shape)

    @cached_property
    def half_edges(self):
        _, indices = self.labels
        return tuple(
            {
                (int(a), int(b))
                for a, b in zip(indices.ravel(), np.roll(indices, self.size // 2, axis=axis).ravel(), strict=True)
                if a != b
            }
            for axis in (0, 1)
        )

    def minimum(self, p):
        """Reuse the period valuation test on the actual sampled half-period edges."""
        values, _ = self.labels
        depth = max(
            min((_power_depth(values[a], values[b], p) for a, b in edges), default=inf) for edges in self.half_edges
        )
        if depth == inf:
            raise ValueError("One axis is already periodic at half the target side.")
        return 1 << (1 + int(depth))

    def effective_values(self, p, M=None):
        if M is None:
            M = self.minimum(p)
        values, indices = self.labels
        anchor = pow(values[indices[0, 0]], p, M)
        anchored = tuple((pow(z, p, M) - anchor) % M for z in values)
        shift = min(_valuation(n) for n in anchored)
        return tuple(z >> shift for z in anchored), M >> shift


@dataclass(frozen=True)
class Witness:
    base: Base
    p: int
    a: int
    modulus: int

    def spec(self, phase=0):
        return self.base.spec(self.p, self.a, self.modulus, phase)


def odd_odd_tail(size, combiner):
    return valuation(size) - (1 if combiner == "add" else 2)


def odd_odd_prepowers(size, combiner):
    """All pre-power motifs up to the proved valuation tail and odd-part cycle."""
    t = valuation(size) - 1
    return tuple(
        (w, tuple((1 << w) * u for u in range(1, 1 << t, 2))) for w in range(1, odd_odd_tail(size, combiner) + 1)
    )


def checkerboard_tail_prepowers(size):
    """Choose an erased-branch power in every relevant pre-valuation and odd-part row."""
    r = valuation(size)
    width = size // 4
    powers = []
    for w in range(1, max(1, r - 3) + 1):
        for u in range(1, width, 2):
            q = u << w
            while q < r + w:
                q += width << w
            powers.append(q)
    return tuple(powers)


@lru_cache(maxsize=16)
def postpowers(base):
    """Complete representatives for the unit-coset cases at minimum precision."""
    if base.sampling == ODD_ODD and base.combiner in ODD_COSETS:
        s = valuation(base.q) + (1 if base.combiner == "add" else 2)
        t = valuation(base.size) - 1
    elif base.sampling == CHECKERBOARD:
        w = valuation(base.q)
        s = min(base.q, w + 2)
        t = valuation(base.K) - s
    else:
        raise ValueError("A unit-coset base is required.")
    split_absdiff = base.sampling == CHECKERBOARD and base.combiner == "absdiff" and base.q < valuation(base.K)
    start = int(split_absdiff)
    return ((1,) if split_absdiff else ()) + tuple(
        (1 << v) * u for v in range(start, max(start, t - s + 1) + 1) for u in range(1, 1 << t, 2)
    )


@lru_cache(maxsize=16)
def nonunit_order_powers(base):
    """All order/equality representatives for odd-odd XOR and ABSDIFF."""
    t = valuation(base.size) - 1
    representatives = {1 << t}
    for v in range(t):
        m = 2 if v == 0 and base.combiner == "absdiff" else t + v
        cycle = 1 << max(1, m - 2 - v)
        for u in range(1, cycle, 2):
            p = u << v
            while p < m:
                representatives.add(p)
                p += cycle << v
            representatives.add(p)
    return tuple(sorted(representatives))


def joint_positions(bases):
    """One cell per joint raw equality group preserves exact cross-base comparisons."""
    table = np.column_stack([base.labels[1].ravel() for base in bases])
    _, positions = np.unique(table, axis=0, return_index=True)
    # Preserve spatial order, including the origin at index zero.
    return np.sort(positions)


def partition(values):
    _, first, indices = np.unique(values, return_index=True, return_inverse=True)
    labels = np.empty(len(first), dtype=np.int64)
    labels[np.argsort(first)] = np.arange(len(first))
    return labels[indices]


def catalogues(bases, powers, *, retain_shifts=True, modulus=Base.minimum):
    """Deduplicate the supplied powers and every effective odd multiplier.

    A uniform index in a returned dictionary samples its discrete classes exactly.
    """
    positions = joint_positions(bases)
    equality, order, shift = {}, {}, {}
    for base in bases:
        indices = base.labels[1].ravel()[positions]
        for p in powers(base):
            M = modulus(base, p)
            outputs, effective_modulus = base.effective_values(p, M)
            if effective_modulus > 1 << 31:
                raise ValueError("This finite enumeration needs at most 31 effective bits.")
            values = np.asarray(outputs, dtype=np.int64)
            equality.setdefault(partition(values[indices]).astype(np.uint32).tobytes(), Witness(base, p, 1, M))
            for a in range(1, effective_modulus, 2):
                residues = (a * values) % effective_modulus
                witness = Witness(base, p, a, M)
                ranks = np.unique(residues, return_inverse=True)[1]
                order.setdefault(ranks[indices].astype(np.uint32).tobytes(), witness)
                if retain_shifts:
                    shift.setdefault((effective_modulus, residues[indices].astype(np.uint32).tobytes()), witness)
    return {"equality": equality, "order": order, "shift": shift}


def draw(classes, rng: Random):
    """Choose one distinct class and then an independent uniform modular phase."""
    witness = tuple(classes.values())[rng.randrange(len(classes))]
    return witness.spec(rng.randrange(witness.modulus))


def checkerboard_groups(size):
    return tuple((str(group), group.powers) for group in power_groups(size))
