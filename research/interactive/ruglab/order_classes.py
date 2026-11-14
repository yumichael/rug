"""Seeded conditional order draws with the existing interpolation's value spacing.

The sampler and interpolation are from the November 12 checkerboard head/tail
research. Previewing its target table avoids eagerly expanding polynomial
coefficients, without changing any normalized output value.
"""

from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from random import Random

import numpy as np

from ._orders.core import Basic, nu
from ._orders.realize import pre_polynomial, realize
from ._orders.sampler import OrderSampler
from .indexed import IndexedValues, byte_lru

ORDER_COMBINERS = ("or", "xor", "add", "absdiff")


class OrderSampleUnavailable(ValueError):
    """The selected base does not belong to the requested family."""


def tail_power(size):
    """First even exponent after which the even branch stays erased."""
    r = size.bit_length() - 1
    return next(q for q in range(2, 66, 2) if all(p >= r + int(nu(p)) for p in range(q, 66, 2)))


def head_powers(size):
    return tuple(range(2, tail_power(size), 2))


@dataclass(frozen=True)
class OrderClassRecipe:
    family: str
    seed: int
    draw: int
    pre_power: int = 2
    twist: tuple[int, ...] = ()
    combiner: str = "or"


@lru_cache(maxsize=8)
def _basic(size, power, twist, combiner):
    return Basic(size, power, twist, combiner)


@lru_cache(maxsize=8)
def _model(sizes):
    start = 0
    groups = []
    for size in sizes:
        groups.append(tuple(range(start, start + size)))
        start += size
    return OrderSampler(groups)


def _map_structure(structure, nodes):
    def group(values):
        return tuple(nodes[i] for i in values)

    return [(group(a), group(b), [group(g) for g in p], [group(g) for g in q]) for a, b, p, q in structure]


def _interpolated_targets(basic, structure):
    # These are the label placements and common denominator scale used by
    # realize.py, with no spacing optimization or rank-color substitution.
    need = sum(1 + max(len(p), len(q)) for _, _, p, q in structure)
    half = 1 << (need - 1).bit_length()
    labels = [0] * len(basic.nodes)
    position = 0
    for a, b, p, q in structure:
        for node in a:
            labels[node] = position
        for node in b:
            labels[node] = position + half
        for groups, start in ((p, position), (q, position + half)):
            for offset, group in enumerate(groups, 1):
                for node in group:
                    labels[node] = start + offset
        position += 1 + max(len(p), len(q))
    labels = [(v - labels[basic.anchor]) % (2 * half) for v in labels]
    # Valuation of each Lagrange denominator is the sum of its factor depths.
    # This equals realize.py's depth without constructing the huge products.
    depth = max(sum(int(nu(t - u)) for j, u in enumerate(basic.nodes) if i != j) for i, t in enumerate(basic.nodes))
    return np.array([v << depth for v in labels], dtype=object), (2 * half) << depth


@byte_lru(8, 64 << 20, lambda result: result.nbytes)
def _indices(size, power, twist, combiner):
    basic = _basic(size, power, twist, combiner)
    indices = basic.indices.astype(np.min_scalar_type(len(basic.nodes) - 1))
    # Retain only the compact tile in this byte-limited cache.
    basic.__dict__.pop("indices", None)
    indices.flags.writeable = False
    return indices


def order_sample(recipe, size):
    if size < 8 or size > 4096 or size & (size - 1):
        raise OrderSampleUnavailable("Order sampling requires a power-of-two side from 8 to 4096.")
    if recipe.family not in ("head", "tail") or recipe.combiner not in ORDER_COMBINERS:
        raise ValueError("Choose head or tail and OR, XOR, ADD, or ABSDIFF")
    if recipe.draw < 0:
        raise ValueError("Draw index must be nonnegative")
    power = tail_power(size) if recipe.family == "tail" else recipe.pre_power
    twist = () if recipe.family == "tail" else recipe.twist
    if power < 2 or power % 2:
        raise ValueError("Pre-power must be positive and even")
    if recipe.family == "head" and power >= size.bit_length() - 1 + int(nu(power)):
        raise OrderSampleUnavailable(f"Pre-power {power} belongs to the tail at side {size}; choose a head power.")
    basic = _basic(size, power, twist, recipe.combiner)
    components = sorted(basic.components, key=lambda g: (len(g), g))
    nodes = tuple(node for group in components for node in group)
    model = _model(tuple(map(len, components)))
    inverse = {node: i for i, node in enumerate(nodes)}
    draw_seed = f"order-classes:{recipe.seed}:{recipe.draw}"
    _, structure = model.draw(Random(draw_seed), anchor=inverse[basic.anchor])
    structure = _map_structure(structure, nodes)
    outputs, modulus = _interpolated_targets(basic, structure)
    indices = _indices(size, power, twist, recipe.combiner)
    groups = np.unique(outputs)
    gaps = [int(b - a) for a, b in zip(groups, [*groups[1:], int(groups[0]) + modulus], strict=True)]
    cell_counts = np.bincount(indices.ravel(), minlength=len(outputs))
    bins = [0] * 16
    for value, count in zip(outputs, cell_counts, strict=True):
        bins[int(value) * 16 // modulus] += int(count)
    metadata = {
        "family": recipe.family,
        "seed": recipe.seed,
        "draw": recipe.draw,
        "draw_seed": draw_seed,
        "pre_power": power,
        "twist": list(twist),
        "structure": structure,
        "class_count_hex": hex(model.total),
        "class_count_bits": model.total.bit_length(),
        "groups": len(groups),
        "min_gap_ratio": min(gaps) * len(groups) / modulus,
        "max_gap_ratio": max(gaps) * len(groups) / modulus,
        "cell_bins": bins,
        "largest_bin_fraction": max(bins) / indices.size,
    }
    spec = {
        "n": size,
        "K": basic.K,
        "M": modulus,
        "sampling": "checkerboard_opposite",
        "checkerboard_axis": "vertical",
        "combine": recipe.combiner,
        "pre": [["pow", power], ["poly", pre_polynomial(twist)]],
        "post": [["lookup", {str(node): hex(int(value)) for node, value in zip(basic.nodes, outputs, strict=True)}]],
        "color": "cmr.emergency",
        "order_sample": metadata,
    }
    return IndexedValues(np.array(basic.nodes, dtype=object), indices), outputs, spec


def realize_order_polynomial(spec):
    """Expand the existing interpolating polynomial when coefficients are needed."""
    result = deepcopy(spec)
    info = result["order_sample"]
    basic = _basic(result["n"], info["pre_power"], tuple(info["twist"]), result["combine"])
    coefficients, modulus, _ = realize(basic, info["structure"])
    if modulus != result["M"]:
        raise ValueError("Realize the sampled modulus before changing M")
    result["post"] = [["poly", coefficients]]
    return result
