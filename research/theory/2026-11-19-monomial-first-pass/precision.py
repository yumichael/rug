"""Exact single-power modulus selectors and complete finite twist coordinates."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import comb

from ruglab._orders.coordinates import diagonalize, twist_space
from study import CHECKERBOARD, Base, valuation


@dataclass(frozen=True)
class Moduli:
    minimum_period: int
    distinct_outputs: int
    catalogue: int


def distinct_bits(values):
    """Least bit width at which the given distinct residues stay distinct."""
    low, high = 0, values[-1].bit_length()
    while low < high:
        middle = (low + high) // 2
        mask = (1 << middle) - 1
        if len({value & mask for value in values}) < len(values):
            low = middle + 1
        else:
            high = middle
    return high


def moduli(base: Base, p):
    w, v = valuation(base.q), valuation(p)
    K = base.K
    if base.sampling == CHECKERBOARD:
        head = base.q < valuation(K)
        balanced = K << v
        if base.combiner == "absdiff" and head and p % 2:
            return Moduli(4, K, K)
        keep = 2 * balanced if head and base.combiner in ("add", "absdiff") else balanced
        return Moduli(balanced, keep, keep)

    s, t = w + 2, valuation(base.size) - 1
    if base.combiner == "add":
        minimum = K << (p - 1 + v)
        keep = 2 * minimum
    elif base.combiner in ("and", "or"):
        minimum = keep = K << v
    elif base.combiner == "mult" and s >= t + 1:
        minimum = K << v
        keep = (K * K // 4) << v
    elif base.combiner == "clmul" and s >= t:
        minimum = K << v
        keep = (K * K // 2) << v
    elif base.combiner in ("mult", "clmul"):
        minimum = K << v
        keep = 1 << (distinct_bits(base.labels[0]) + v)
    else:
        min_bits = 2 if base.combiner == "absdiff" and p % 2 else t + v
        minimum = 1 << (s * p + min_bits)
        keep = 1 << (s * p + p * (t - 1) + 1 + int(p == 2))
    return Moduli(minimum, keep, keep)


def coefficient_vectors(bits, generators):
    columns = tuple(zip(*generators, strict=True))
    for coords in product(*(range(1 << width) for width in bits)):
        yield tuple(sum(a * b for a, b in zip(coords, column, strict=True)) for column in columns)


@lru_cache(maxsize=32)
def odd_twists(N, q):
    """One Q per distinct action on the complete odd pre-value coset."""
    s = valuation(q) + 2
    K = 2 * N * (q & -q)
    k = valuation(K)
    count = max(0, (k - 2) // s)
    values = tuple(range(1, K, 1 << s))
    if not count:
        return ((),)
    columns = [tuple(2 * z * (z - 1) ** (j + 1) % K for z in values) for j in range(count)]
    # Track the corresponding coefficients in the (z-1)^j basis.
    bits, transform = diagonalize(columns, K)
    generators = [tuple(row[j] for row in transform) for j in range(len(bits))]
    result = []
    for coefficients in coefficient_vectors(bits, generators):
        Q = tuple(
            sum(c * comb(j, i) * (-1) ** (j - i) for j, c in enumerate(coefficients) if j >= i) for i in range(count)
        )
        result.append(Q if any(Q) else ())
    return tuple(result)


@lru_cache(maxsize=32)
def checkerboard_twists(N, q):
    """Reuse the complete shared-family coordinates on the opposite checkerboard."""
    bits, transform = twist_space(N, q)
    generators = [tuple(row[j] for row in transform) for j in range(len(bits))]
    return tuple(Q if any(Q) else () for Q in coefficient_vectors(bits, generators))


def preserving_unit_powers(base):
    """All power representatives at Distinct outputs for the unit-coset cases."""
    w = valuation(base.q)
    d = valuation(moduli(base, 1).distinct_outputs)
    even_start = 0
    odds = ()
    if base.sampling == CHECKERBOARD:
        s = min(base.q, w + 2)
        if base.combiner == "absdiff" and base.q < valuation(base.K):
            odds = tuple(range(1, 1 << max(1, d - 2), 2))
            even_start = 1
            d = valuation(moduli(base, 2).distinct_outputs) - 1
    elif base.combiner == "add":
        d -= 1
        s = w + 1
    elif base.combiner in ("and", "or", "mult", "clmul"):
        s = w + 2
    else:
        raise ValueError("The distinction-preserving unit-coset reduction does not apply.")
    t = d - s
    return odds + tuple(
        (1 << v) * u for v in range(even_start, max(even_start, t - s + 1) + 1) for u in range(1, 1 << t, 2)
    )
