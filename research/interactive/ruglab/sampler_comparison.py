"""Complete finite-base unions and alternative color assignments for comparison."""

from dataclasses import dataclass
from functools import lru_cache, wraps
from itertools import product
from math import factorial
from random import Random

import numpy as np

from ._orders.combinatorics import pick
from ._orders.coordinates import image, twist_space
from ._orders.core import Basic, nu
from ._orders.sampler import stirling
from .indexed import IndexedValues
from .order_classes import ORDER_COMBINERS, _interpolated_targets, _map_structure, _model, head_powers, tail_power

STRATEGIES = {
    "polynomial_orders": "Polynomial order union (minimum M)",
    "equality_iid": "Uniform raw equalities / IID levels",
    "order_iid": "Uniform nonmerging orders / IID levels",
    "equality_equal": "Uniform raw equalities / equal spacing",
    "order_equal": "Uniform nonmerging orders / equal spacing",
    "equality_dirichlet": "Uniform raw equalities / Dirichlet gaps",
    "order_dirichlet": "Uniform nonmerging orders / Dirichlet gaps",
    "isometric_equalities": "Isometric equality union / identity spacing",
    "isometric_orders": "Isometric order union (all post-precisions)",
    "isometric_window": "Isometric orders / finite precision window",
    "cell_mass": "Uniform raw equalities / cell-mass spacing",
    "polynomial_all_orders": "Polynomial order union / all precisions",
    "polynomial_equalities": "Polynomial equality union / all precisions",
}


class ComparisonUnavailable(ValueError):
    """An exact comparison exceeds the configured finite-work limits."""


def retain_signature(collection, key, value):
    if key not in collection:
        if (len(collection) + 1) * len(key) > 64 << 20:
            raise ComparisonUnavailable(
                "Complete isometric union exceeds the 64 MiB spatial-signature budget; no partial union was sampled."
            )
        collection[key] = value


def bounded_cache(size):
    """Cache exact results and feasibility failures across gallery draws."""

    def decorate(function):
        @lru_cache(maxsize=size)
        def cached(*args):
            try:
                return function(*args)
            except ComparisonUnavailable as error:
                return str(error)

        @wraps(function)
        def call(*args):
            result = cached(*args)
            if isinstance(result, str):
                raise ComparisonUnavailable(result)
            return result

        return call

    return decorate


@dataclass(frozen=True)
class PowerGroup:
    powers: tuple[int, ...]
    tail: bool = False

    def __str__(self):
        return "Tail" if self.tail else "Pre " + " & ".join(map(str, self.powers))


def power_groups(size):
    if size < 8 or size > 4096 or size & (size - 1):
        raise ComparisonUnavailable("Comparison requires a power-of-two side from 8 to 4096.")
    depths = {}
    for q in head_powers(size):
        d = q - (q & -q).bit_length() - 1
        depths.setdefault(d, []).append(q)
    return (*(PowerGroup(tuple(qs)) for _, qs in sorted(depths.items())), PowerGroup((tail_power(size),), True))


def canonical_partition(indices):
    flat = np.asarray(indices).ravel()
    _, first, inverse = np.unique(flat, return_index=True, return_inverse=True)
    remap = np.empty(len(first), dtype=np.uint32)
    remap[np.argsort(first)] = np.arange(len(first), dtype=np.uint32)
    return remap[inverse].reshape(indices.shape)


@dataclass
class Entry:
    basic: Basic
    partition: np.ndarray
    first: np.ndarray


def entry(basic):
    partition = canonical_partition(basic.indices)
    _, first = np.unique(partition, return_index=True)
    return Entry(basic, partition, first)


@bounded_cache(6)
def base_pool(size, group, max_bases, tail_twists=False):
    if group not in power_groups(size):
        raise ComparisonUnavailable("This power group is absent at the selected size.")
    reduced_tail = group.tail and not tail_twists
    spaces = [(group.powers[0], [], [])] if reduced_tail else [(q, *twist_space(size, q)) for q in group.powers]
    combiners = ("or",) if reduced_tail else ORDER_COMBINERS
    descriptions = sum(len(combiners) * (1 << sum(bits)) for _, bits, _ in spaces)
    if descriptions > max_bases:
        raise ComparisonUnavailable(
            f"Exact all-twist union needs {descriptions:,} bases; limit is {max_bases:,}. No restricted subset was sampled."
        )
    if descriptions * size * size > 16_000_000:
        raise ComparisonUnavailable(
            "Exact union exceeds the 16 million retained grid-cell work budget; choose a smaller field or a higher power group."
        )
    all_bases, partitions = [], {}
    for q, bits, transform in spaces:
        for coordinate in product(*(range(1 << b) for b in bits)):
            Q = tuple(sum(a * transform[j][i] for i, a in enumerate(coordinate)) for j in range(len(transform)))
            for c in combiners:
                basic = Basic(size, q, Q, c)
                current = entry(basic)
                all_bases.append(basic)
                partitions.setdefault(current.partition.tobytes(), current)
    return tuple(partitions.values()), tuple(all_bases)


def component_model(basic):
    components = sorted(basic.components, key=lambda g: (len(g), g))
    nodes = tuple(node for component in components for node in component)
    return _model(tuple(map(len, components))), nodes


def draw_union(entries, rng):
    weights = [component_model(e.basic)[0].total for e in entries]
    while True:
        i = pick(rng, list(enumerate(weights)))
        source = entries[i]
        basic = source.basic
        model, nodes = component_model(basic)
        rank, structure = model.draw(rng, anchor=nodes.index(basic.anchor))
        original = np.empty(len(nodes), dtype=np.int64)
        original[list(nodes)] = rank
        field = original[basic.indices].ravel()
        multiplicity = sum(np.array_equal(field, field[e.first][e.partition.ravel()]) for e in entries)
        if rng.randrange(multiplicity) == 0:
            values, modulus = _interpolated_targets(basic, _map_structure(structure, nodes))
            return basic, values, modulus, multiplicity


def partition_count(n, ordered):
    return sum(stirling(n)[n][k] * (factorial(k - 1) if ordered else 1) for k in range(1, n + 1))


def partition_draw(n, rng, ordered):
    S = stirling(n)
    k = pick(rng, [(k, S[n][k] * (factorial(k - 1) if ordered else 1)) for k in range(1, n + 1)])
    decisions = []
    for remaining in range(n, 0, -1):
        singleton = S[remaining - 1][k - 1]
        together = k * (S[remaining - 1][k] if k < remaining else 0)
        alone = rng.randrange(singleton + together) < singleton
        decisions.append((remaining - 1, alone))
        k -= alone
    groups = []
    for node, alone in reversed(decisions):
        if alone:
            groups.append([node])
        else:
            groups[rng.randrange(len(groups))].append(node)
    if ordered:
        rng.shuffle(groups)
    rank = np.empty(n, dtype=np.int64)
    for i, nodes in enumerate(groups):
        rank[nodes] = i
    return rank


def draw_all_precision(entries, rng, ordered):
    weights = [
        partition_count(len(e.basic.nodes), ordered) - partition_count(len(e.basic.components), ordered)
        for e in entries
    ]
    while True:
        basic = entries[pick(rng, list(enumerate(weights)))].basic
        # Rejection conditions the uniform partition draw on full period.
        while True:
            rank = partition_draw(len(basic.nodes), rng, ordered)
            if basic.full(rank):
                break
        rank = (rank - rank[basic.anchor]) % (int(rank.max()) + 1)
        field = rank[basic.indices].ravel()
        multiplicity = sum(np.array_equal(field, field[e.first][e.partition.ravel()]) for e in entries)
        if rng.randrange(multiplicity) == 0:
            if not ordered:
                order = list(range(int(rank.max()) + 1))
                rng.shuffle(order)
                rank = np.array(order)[rank]
                rank = (rank - rank[basic.anchor]) % len(order)
            depth = max(
                sum(int(nu(t - u)) for j, u in enumerate(basic.nodes) if i != j) for i, t in enumerate(basic.nodes)
            )
            levels = 1 << int(rank.max()).bit_length()
            return basic, rank.astype(object) << depth, levels << depth, multiplicity


def minimum_bits(basic):
    return 1 + min(int(nu(basic.nodes[a] - basic.nodes[b])) for a, b in basic.edges if a != b)


@lru_cache(maxsize=8)
def isometric_bases(size, group, max_bases):
    if not group.tail:
        return base_pool(size, group, max_bases)[1]
    # At low (merging) precision all twists and odd exponent parts are
    # absorbed by global post-isometries. Valuations stabilize at r-4.
    r = size.bit_length() - 1
    powers = []
    for w in range(1, max(1, r - 4) + 1):
        u = 1
        while (1 << w) * u < r + w:
            u += 2
        powers.append((1 << w) * u)
    return tuple(Basic(size, q, (), "or") for q in powers)


@bounded_cache(8)
def isometric_equalities(size, group, max_bases):
    bases = isometric_bases(size, group, max_bases)
    result = {}
    for basic in bases:
        nodes = np.array(basic.nodes, dtype=np.int64)
        for bits in range(minimum_bits(basic), max(basic.nodes).bit_length() + 1):
            modulus = 1 << bits
            values = nodes % modulus
            field = canonical_partition(values[basic.indices])
            retain_signature(result, field.tobytes(), (basic, values, modulus))
    return tuple(result.values())


@lru_cache(maxsize=128)
def isometric_coordinates(nodes, modulus):
    # Rivest parity conditions: a1 odd; even-degree coefficient sum even;
    # odd-degree sum above degree one even. Null falling factorials of
    # degree >=4 preserve these conditions, so this degree bound is complete.
    m = modulus.bit_length() - 1
    degree = 4
    while int(nu(factorial(degree))) < m:
        degree += 1
    columns = []
    anchor = nodes[0]
    for j in range(1, degree):
        if j <= 3:
            column = tuple(2 * (pow(z, j, modulus) - pow(anchor, j, modulus)) % modulus for z in nodes)
        else:
            base_degree = 2 if j % 2 == 0 else 3
            column = tuple(
                (
                    pow(z, j, modulus)
                    - pow(z, base_degree, modulus)
                    - pow(anchor, j, modulus)
                    + pow(anchor, base_degree, modulus)
                )
                % modulus
                for z in nodes
            )
        columns.append(column)
    bits, generators = image(columns, modulus)
    return bits, generators


@bounded_cache(8)
def isometric_window_orders(size, group, max_bases, offsets, limit):
    _, bases = base_pool(size, group, max_bases, True)
    jobs, work = [], 0
    seen_jobs = set()
    for basic in bases:
        for offset in offsets:
            modulus = 1 << (minimum_bits(basic) + offset)
            signature = (basic.nodes, basic.indices.tobytes(), modulus)
            if signature in seen_jobs:
                continue
            seen_jobs.add(signature)
            bits, generators = isometric_coordinates(basic.nodes, modulus)
            work += 1 << sum(bits)
            if work > limit:
                raise ComparisonUnavailable(
                    f"Exact isometric order enumeration exceeds {limit:,} tables for this precision window. No truncated union was sampled."
                )
            jobs.append((basic, modulus, bits, generators))
    orders = {}
    for basic, modulus, bits, generators in jobs:
        base = np.array([(z - basic.nodes[0]) % modulus for z in basic.nodes], dtype=np.int64)
        for coefficients in product(*(range(1 << b) for b in bits)):
            values = (
                base
                + sum(
                    (a * np.array(g) for a, g in zip(coefficients, generators, strict=True)),
                    np.zeros(len(base), dtype=np.int64),
                )
            ) % modulus
            _, ranks = np.unique(values, return_inverse=True)
            ranks = (ranks - ranks[basic.anchor]) % (int(ranks.max()) + 1)
            retain_signature(orders, ranks[basic.indices].astype(np.uint32).tobytes(), (basic, values, modulus))
    return tuple(orders.values())


@bounded_cache(8)
def isometric_order_extras(size, group, max_bases, limit):
    """Coarse orders outside the symbolic nonmerging-order union."""
    entries, _ = base_pool(size, group, max_bases)
    bases = isometric_bases(size, group, max_bases)
    raw_keys = {e.partition.tobytes() for e in entries}
    extras, seen, work = {}, set(), 0
    for basic in bases:
        upper = max(int(nu(a - b)) for i, a in enumerate(basic.nodes) for b in basic.nodes[:i])
        for m in range(minimum_bits(basic), upper + 1):
            modulus = 1 << m
            signature = (basic.nodes, basic.indices.tobytes(), modulus)
            if signature in seen:
                continue
            seen.add(signature)
            if canonical_partition((np.array(basic.nodes) % modulus)[basic.indices]).tobytes() in raw_keys:
                continue
            bits, generators = isometric_coordinates(basic.nodes, modulus)
            work += 1 << sum(bits)
            if work > limit:
                raise ComparisonUnavailable(
                    f"Complete isometric coarse-order union exceeds {limit:,} tables; no partial union was sampled. The finite-window strategy is separate."
                )
            base = np.array([(z - basic.nodes[0]) % modulus for z in basic.nodes], dtype=np.int64)
            for coefficients in product(*(range(1 << b) for b in bits)):
                values = (
                    base
                    + sum(
                        (a * np.array(g) for a, g in zip(coefficients, generators, strict=True)),
                        np.zeros(len(base), dtype=np.int64),
                    )
                ) % modulus
                _, ranks = np.unique(values, return_inverse=True)
                ranks = (ranks - ranks[basic.anchor]) % (int(ranks.max()) + 1)
                retain_signature(extras, ranks[basic.indices].astype(np.uint32).tobytes(), (basic, values, modulus))
    return tuple(extras.values())


def draw_isometric_union(entries, size, recipe, rng):
    extras = isometric_order_extras(size, recipe.group, recipe.max_bases, recipe.max_isometry_tables)
    weights = [factorial(len(e.first) - 1) for e in entries]
    choice = pick(rng, [*enumerate(weights), (len(entries), len(extras))])
    if choice == len(entries):
        return extras[rng.randrange(len(extras))]
    basic = entries[choice].basic
    ranks = list(range(len(basic.nodes)))
    rng.shuffle(ranks)
    ranks = [(v - ranks[basic.anchor]) % len(ranks) for v in ranks]
    depth = max(sum(int(nu(t - u)) for j, u in enumerate(basic.nodes) if i != j) for i, t in enumerate(basic.nodes))
    stride = 1 << max(depth + 2, max(basic.nodes).bit_length() + 1)
    modulus = 1 << (stride * (len(ranks) + 1)).bit_length()
    values = np.array([z + stride * r for z, r in zip(basic.nodes, ranks, strict=True)], dtype=object)
    return basic, values, modulus


@dataclass(frozen=True)
class ComparisonRecipe:
    group: PowerGroup
    strategy: str
    draw: int
    seed: int
    concentration: float = 1.0
    max_bases: int = 4096
    isometry_offsets: tuple[int, ...] = (0, 1, 2)
    max_isometry_tables: int = 50000
    combiner: str = "or"


def group_levels(strategy, counts, rng, concentration):
    k = len(counts)
    modulus = 1 << 53
    if strategy.endswith("_equal"):
        modulus = k
        values = list(range(k))
        rng.shuffle(values)
    elif strategy.endswith("_dirichlet"):
        gaps = [rng.gammavariate(concentration, 1) for _ in range(k)]
        total = sum(gaps)
        if not total or not np.isfinite(total):
            raise ComparisonUnavailable("Dirichlet concentration is below useful numerical precision.")
        gaps = [max(1, int(g / total * (modulus - k))) for g in gaps]
        # Integer positive gaps retain every group despite finite precision.
        modulus = sum(gaps)
        values = np.cumsum([0, *gaps[:-1]]).tolist()
        rng.shuffle(values)
    elif strategy == "cell_mass":
        order = list(range(k))
        rng.shuffle(order)
        values = [0] * k
        position = 0
        modulus = 2 * int(counts.sum())
        for i in order:
            values[i] = 2 * position + int(counts[i])
            position += int(counts[i])
    else:
        values = rng.sample(range(modulus), k)
    return np.array(values, dtype=np.int64), modulus


def level_statistics(values, counts, modulus, offset):
    levels = sorted(set(map(int, values)))
    gaps = [b - a for a, b in zip(levels, [*levels[1:], levels[0] + modulus], strict=True)]
    bins = [0] * 16
    for value, count in zip(values, counts, strict=True):
        bins[int(((int(value) / modulus + offset) % 1) * 16)] += int(count)
    return {
        "min_gap_ratio": min(gaps) * len(levels) / modulus,
        "max_gap_ratio": max(gaps) * len(levels) / modulus,
        "largest_bin_fraction": max(bins) / int(counts.sum()),
    }


def comparison_sample(recipe, size):
    entries, _ = base_pool(size, recipe.group, recipe.max_bases)
    rng = Random(f"comparison:{recipe.seed}:{size}:{recipe.group}:{recipe.strategy}:{recipe.draw}")
    multiplicity = 1
    strategy = recipe.strategy
    if strategy == "polynomial_orders":
        basic, values, modulus, multiplicity = draw_union(entries, rng)
    elif strategy in ("polynomial_all_orders", "polynomial_equalities"):
        basic, values, modulus, multiplicity = draw_all_precision(entries, rng, strategy == "polynomial_all_orders")
    elif strategy == "isometric_orders":
        basic, values, modulus = draw_isometric_union(entries, size, recipe, rng)
    elif strategy.startswith("isometric_"):
        choices = (
            isometric_equalities(size, recipe.group, recipe.max_bases)
            if strategy == "isometric_equalities"
            else isometric_window_orders(
                size, recipe.group, recipe.max_bases, recipe.isometry_offsets, recipe.max_isometry_tables
            )
        )
        basic, values, modulus = choices[rng.randrange(len(choices))]
    else:
        order_weighted = strategy.startswith("order_")
        weights = [factorial(len(e.first) - 1) if order_weighted else 1 for e in entries]
        source = entries[pick(rng, list(enumerate(weights)))]
        basic = source.basic
        counts = np.bincount(basic.indices.ravel(), minlength=len(basic.nodes))
        values, modulus = group_levels(strategy, counts, rng, recipe.concentration)
    values = np.asarray(values, dtype=object)
    values = (values - values[basic.anchor]) % modulus
    offset = Random(f"comparison-rotation:{recipe.seed}:{size}:{recipe.group}:{recipe.draw}").random()
    counts = np.bincount(basic.indices.ravel(), minlength=len(values))
    spec = {
        "n": size,
        "K": basic.K,
        "M": int(modulus),
        "pre": [["pow", basic.q], ["poly", _pre_polynomial(basic.Q)]],
        "combine": basic.combiner,
        "sampling": "checkerboard_opposite",
        "checkerboard_axis": "vertical",
        "post": [["lookup", {str(z): hex(int(value)) for z, value in zip(basic.nodes, values, strict=True)}]],
        "color": "cmr.emergency",
        "color_offset": offset,
        "comparison_sample": {
            "strategy": STRATEGIES[strategy],
            "group": str(recipe.group),
            "draw": recipe.draw,
            "raw_partitions": len(entries),
            **level_statistics(values, counts, modulus, offset),
            "multiplicity": multiplicity,
            "pre_power": basic.q,
            "twist": list(basic.Q),
            "concentration": recipe.concentration,
            "isometry_offsets": list(recipe.isometry_offsets),
        },
    }
    return IndexedValues(np.array(basic.nodes, dtype=object), basic.indices), values, spec


def _pre_polynomial(Q):
    coefficients = [0, 1] + [0] * len(Q)
    for j, c in enumerate(Q):
        coefficients[j + 1] -= 2 * c
        coefficients[j + 2] += 2 * c
    return coefficients
