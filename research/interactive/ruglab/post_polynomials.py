"""Stratified polynomial draws for the odd inputs of identity-pre XOR."""

from functools import lru_cache
from random import Random

# Interleave the strata so a small scan includes both parities and several precisions.
POST_STRATA = (
    ("odd power", 0),
    ("even power", 1),
    ("odd sum", 0),
    ("even sum", 1),
    ("even only", 1),
    ("any powers", 0),
    ("even sum", 2),
    ("even only", 2),
    ("any powers", 1),
    ("even sum", 3),
    ("any powers", 2),
    ("even sum", 4),
    ("even only", 4),
    ("any powers", 4),
    ("even sum tail", 5),
)


@lru_cache(maxsize=64)
def _newton_basis(domain, modulus, family, valuation):
    """Return (polynomial, coefficient width) columns on the odd input set."""
    width = modulus.bit_length() - 1
    if family in ("odd sum", "even sum", "even sum tail"):
        power = 1 << valuation
        degree, spacing = 2 * power, 1 << (valuation + 3)
        polynomial = (0,) * power + (1,)
    else:
        degree, spacing = (2, 8) if family == "even only" else (1, 2)
        polynomial = (1,)
    columns = []
    depth = 0
    spacing_depth = spacing.bit_length() - 1
    for k in range(domain // 2):
        if depth >= width:
            break
        # All nonconstant Newton columns vanish at input 1. The initial
        # monomial in a same-valuation sum is anchored by subtracting one.
        if k or len(polynomial) > 1:
            anchored = polynomial if k else (-1, *polynomial[1:])
            columns.append((anchored, width - depth))
        node = 1 + spacing * k
        extended = [0] * (len(polynomial) + degree)
        for j, coefficient in enumerate(polynomial):
            extended[j] -= node * coefficient
            extended[j + degree] += coefficient
        polynomial = tuple(extended)
        low_bit = (k + 1) & -(k + 1)
        depth += spacing_depth + low_bit.bit_length() - 1
    return columns


def _value(coefficients, z, mask):
    value = 0
    for coefficient in reversed(coefficients):
        value = (z * value + coefficient) & mask
    return value


def _full_period(coefficients, domain, modulus):
    half, quarter = domain // 2, domain // 4
    mask = modulus - 1
    return all(
        any(_value(coefficients, z, mask) != _value(coefficients, z + half, mask) for z in inputs)
        for inputs in (range(1, quarter, 2), range(quarter + 1, half, 2))
    )


def _cyclic_index(count, seed, family, valuation, draw):
    """Walk a power-of-two catalogue with a seeded start and odd stride."""
    rng = Random(f"post-catalogue:{seed}:{family}:{valuation}")
    start = rng.randrange(count)
    stride = 2 * rng.randrange(max(1, count // 2)) + 1
    return (start + draw * stride) % count


def _anchored_power(power, multiplier):
    return (-multiplier,) + (0,) * (power - 1) + (multiplier,)


@lru_cache(maxsize=256)
def draw_post_polynomial(domain, family, valuation, seed, draw):
    """Return anchored coefficients and modulus for one draw within a stratum."""
    if family in ("odd power", "even power"):
        even = family == "even power"
        powers = max(1, domain // (32 if even else 8))
        multipliers = domain // (8 if even else 4)
        index = _cyclic_index(powers * multipliers, seed, family, valuation, draw)
        exponent_index, multiplier_index = divmod(index, multipliers)
        power = 2 * exponent_index + (2 if even else 1)
        return _anchored_power(power, 2 * multiplier_index + 1), domain * (power & -power)

    if family == "even sum tail":
        valuation = max(5, domain.bit_length() - 6)
    modulus = domain << valuation
    if family in ("even sum", "even sum tail") and valuation >= max(1, domain.bit_length() - 6):
        # At stabilization the whole anchored space has one cyclic generator.
        index = _cyclic_index(domain // 8, seed, family, valuation, draw)
        return _anchored_power(1 << valuation, 2 * index + 1), modulus

    rng = Random(f"post-polynomial:{seed}:{draw}:{family}:{valuation}")
    columns = _newton_basis(domain, modulus, family, valuation)
    same_valuation = family in ("odd sum", "even sum", "even sum tail")
    # Uniform coefficients map uniformly onto their image, even when a
    # spanning list has relations. For sums the first coefficient sets the
    # period bit. For other polynomials condition on both half-shift tests.
    while True:
        coefficients = [0] * len(columns[-1][0])
        for index, (generator, width) in enumerate(columns):
            coefficient = rng.randrange(1, 1 << width, 2) if same_valuation and index == 0 else rng.getrandbits(width)
            for degree, term in enumerate(generator):
                coefficients[degree] = (coefficients[degree] + coefficient * term) % modulus
        if same_valuation or _full_period(coefficients, domain, modulus):
            while coefficients[-1] == 0:
                coefficients.pop()
            return tuple(coefficients), modulus
