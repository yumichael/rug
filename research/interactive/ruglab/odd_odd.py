"""Exact spatial-class samplers for the Cartesian odd-odd domain."""

from dataclasses import dataclass
from functools import lru_cache
from math import factorial
from random import Random

import numpy as np

from . import sampler_comparison
from ._orders.combinatorics import pick
from ._orders.core import poly
from ._orders.odd_pre import OddPreSpace
from .indexed import IndexedValues, byte_lru, combination_table
from .order_classes import _map_structure, _model, component_levels
from .sampler_comparison import (
    STRATEGIES,
    _pre_polynomial,
    canonical_partition,
    group_levels,
    level_statistics,
    partition_count,
    partition_draw,
)

ODD_COMBINERS = ("and", "or", "xor", "add", "absdiff", "mult", "clmul")
ODD_STRATEGIES = {
    **{key: STRATEGIES[key] for key in STRATEGIES if key.startswith(("equality_", "order_")) or key == "cell_mass"},
    **{
        key: STRATEGIES[key]
        for key in ("isometric_equalities", "polynomial_equalities", "polynomial_all_orders", "polynomial_orders")
    },
    "residue_orders": "Residue partitions / uniform circular orders",
}
_PRODUCTS = ("mult", "clmul")
_DIRECT_RAW = ("and", "or", "add", "absdiff")
_COARSENINGS = ("polynomial_equalities", "polynomial_all_orders", "polynomial_orders")
_MAX_COARSENING_GROUPS = 768


@dataclass(frozen=True)
class OddOddRecipe:
    combiners: tuple[str, ...]
    strategy: str
    draw: int
    seed: int
    concentration: float
    max_cells: int


@dataclass(frozen=True)
class Witness:
    q: int
    twist: tuple[int, ...]
    combiner: str
    modulus: int | None = None

    def pre_modulus(self, period):
        return 4 * period * (self.q & -self.q)

    def codes(self, period):
        K = self.pre_modulus(period)
        shift = K // period
        values = [pow(x, self.q, K) for x in range(1, 2 * period, 2)]
        if self.twist:
            values = [(z + 2 * z * (z - 1) * poly(self.twist, z, K)) % K for z in values]
        return np.array([(z - 1) // shift for z in values], dtype=np.intp)

    def tile(self, period):
        shift = self.pre_modulus(period) // period
        table = code_table(period, shift, self.combiner)
        codes = self.codes(period)
        return IndexedValues(table.labels, table.indices[codes[:, None], codes])


@dataclass(frozen=True)
class Partition:
    witness: Witness
    groups: int


@lru_cache(maxsize=32)
def pre_spaces(period, *, product_tail=False):
    t = period.bit_length() - 1
    final_w = max(1, t - 2 + product_tail)
    return tuple(OddPreSpace(t, w, True) for w in range(1, final_w + 1))


@byte_lru(48, 24 << 20, lambda table: table.nbytes)
def code_table(period, shift, combiner):
    values = 1 + shift * np.arange(period, dtype=np.int64)
    return combination_table(values, values, combiner)


def full_period(field):
    """An axis half-shift reverses the independent odd operand positions."""
    return not np.array_equal(field, field[::-1])


def projections(table, residue):
    """Visit distinct full-period equality relations in increasing precision."""
    groups = len(table.labels)
    if residue:
        previous = 0
        for bits in range(1, int(table.labels[-1]).bit_length() + 1):
            modulus = 1 << bits
            distinct, indices = np.unique(table.labels & (modulus - 1), return_inverse=True)
            count = len(distinct)
            # The partitions are nested, so equal counts give identical classes.
            if count == previous:
                continue
            previous = count
            field = indices[table.indices]
            half = len(field) // 2
            # In code order the same shift toggles the top bit.
            if not np.array_equal(field[:half], field[half:]):
                yield field, count, modulus
            if count == groups:
                return
    else:
        yield table.indices, groups, None


def _pool_bytes(pool):
    return len(pool) if isinstance(pool, str) else sum(len(key) + 256 for key in pool)


@byte_lru(16, 48 << 20, _pool_bytes)
def _partition_pool(period, combiners, residue, max_cells):
    spaces = pre_spaces(period, product_tail=True)
    rows, cols = np.triu_indices(period)
    width = len(rows)
    result = {}
    work = 0
    for combiner in combiners:
        active = spaces if combiner in _PRODUCTS else pre_spaces(period)
        for space in active:
            table = code_table(period, 1 << space.s, combiner)
            for field, count, modulus in projections(table, residue):
                # Every injective unordered-pair table yields the same spatial partition.
                candidates = 1 if count == width else space.count
                work += candidates * width
                if work > max_cells:
                    return f"Exact odd-odd union exceeds the {max_cells:,}-cell work limit. Choose a smaller field."
                dtype = np.min_scalar_type(count - 1)
                for rank in range(candidates):
                    q, twist = space.unrank(rank)
                    witness = Witness(q, twist, combiner, modulus)
                    codes = witness.codes(period)
                    entries = field[codes[rows], codes[cols]]
                    key = canonical_partition(entries).astype(dtype).tobytes()
                    result.setdefault(key, Partition(witness, count))
    return result


def partition_pool(period, combiners, residue, max_cells):
    """Deduplicate the exact finite range on one triangular fundamental tile."""
    pool = _partition_pool(period, combiners, residue, max_cells)
    if isinstance(pool, str):
        raise sampler_comparison.ComparisonUnavailable(pool)
    return pool


@lru_cache(maxsize=8)
def raw_weights(group_counts):
    """Cache factorials by distinct group counts, rather than by witnesses."""
    return {count: factorial(count - 1) for count in group_counts}


def raw_draw(period, recipe, rng):
    residue = recipe.strategy in ("isometric_equalities", "residue_orders")
    combiners = recipe.combiners
    if not residue and len(combiners) == 1 and combiners[0] in _DIRECT_RAW:
        # All maps in this scope have the same number of groups, so use their direct rank.
        spaces = pre_spaces(period)
        count = sum(space.count for space in spaces)
        space = pick(rng, [(space, space.count) for space in spaces])
        q, twist = space.unrank(rng.randrange(space.count))
        return Witness(q, twist, combiners[0]), count
    pool = tuple(partition_pool(period, combiners, residue, recipe.max_cells).values())
    if recipe.strategy.startswith("order_") or recipe.strategy == "residue_orders":
        weights = raw_weights(tuple(sorted({item.groups for item in pool})))
        entry = pick(rng, [(item, weights[item.groups]) for item in pool])
    else:
        entry = pool[rng.randrange(len(pool))]
    return entry.witness, len(pool)


def _components(indices, groups):
    """Contract the label pairs identified by an axis half-period."""
    parents = list(range(groups))

    def root(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    half = indices.shape[0] // 2
    edges = np.unique(indices[:half].astype(np.int64) * groups + indices[::-1][:half])
    for edge in edges.tolist():
        a, b = divmod(edge, groups)
        parents[root(a)] = root(b)
    components = {}
    for i in range(groups):
        components.setdefault(root(i), []).append(i)
    return sorted(components.values(), key=len)


@lru_cache(maxsize=8)
def _coarsening_plans(period, combiners, max_cells, strategy):
    rows, cols = np.triu_indices(period)
    plans = []
    for key, item in partition_pool(period, combiners, False, max_cells).items():
        groups = item.groups
        labels = np.frombuffer(key, dtype=np.min_scalar_type(groups - 1))
        # First-occurrence positions let us check membership in a source partition.
        first = np.unique(labels, return_index=True)[1]
        indices = np.empty((period, period), dtype=labels.dtype)
        indices[rows, cols] = indices[cols, rows] = labels
        components = _components(indices, groups)
        if strategy == "polynomial_orders":
            weight = _model(tuple(map(len, components))).total
        else:
            ordered = strategy == "polynomial_all_orders"
            weight = partition_count(groups, ordered) - partition_count(len(components), ordered)
        plans.append((item.witness, labels, first, weight))
    return tuple(plans)


def _coarsening_levels(table, strategy, rng):
    count = len(table.labels)
    if strategy == "polynomial_orders":
        components = _components(table.indices, count)
        nodes = tuple(node for group in components for node in group)
        anchor = int(table.indices[0, 0])
        model = _model(tuple(map(len, components)))
        _, structure = model.draw(rng, anchor=nodes.index(anchor))
        values, modulus = component_levels(count, anchor, _map_structure(structure, nodes))
        return np.asarray(values), modulus
    ordered = strategy == "polynomial_all_orders"
    while True:
        rank = partition_draw(count, rng, ordered)
        if full_period(rank[table.indices]):
            return rank, 1 << int(rank.max()).bit_length()


def coarsening_draw(period, recipe, rng):
    combiners, strategy = recipe.combiners, recipe.strategy
    product = next((combiner for combiner in combiners if combiner in _PRODUCTS), None)
    if product is not None:
        largest = period * (period + 1) // 2
        if largest > _MAX_COARSENING_GROUPS:
            raise sampler_comparison.ComparisonUnavailable(
                f"Exact merger draws exceed the {_MAX_COARSENING_GROUPS}-group limit. Choose a smaller field."
            )
        q, twist = pre_spaces(period, product_tail=True)[-1].unrank(0)
        witness = Witness(q, twist, product)
        table = witness.tile(period)
        values, modulus = _coarsening_levels(table, strategy, rng)
        return witness, table, values, modulus, 1, 1

    if 2 * period - 1 > _MAX_COARSENING_GROUPS:
        raise sampler_comparison.ComparisonUnavailable(
            f"Exact merger draws exceed the {_MAX_COARSENING_GROUPS}-group limit. Choose a smaller field."
        )
    plans = _coarsening_plans(period, combiners, recipe.max_cells, strategy)
    weights = [(i, plan[3]) for i, plan in enumerate(plans)]
    rows, cols = np.triu_indices(period)
    while True:
        source = pick(rng, weights)
        witness = plans[source][0]
        table = witness.tile(period)
        values, modulus = _coarsening_levels(table, strategy, rng)
        selected = values[table.indices[rows, cols]]
        multiplicity = sum(np.array_equal(selected, selected[first][labels]) for _, labels, first, _ in plans)
        if rng.randrange(multiplicity) == 0:
            return witness, table, values, modulus, len(plans), multiplicity


def odd_odd_sample(recipe, size):
    """Return the compact field, exact native lookup specification, and zero fraction."""
    if size < 8:
        raise sampler_comparison.ComparisonUnavailable(
            "Odd-odd class sampling requires a displayed side of at least 8."
        )
    period = size // 2
    scope = ",".join(recipe.combiners)
    rng = Random(f"odd-odd:{recipe.seed}:{size}:{scope}:{recipe.strategy}:{recipe.draw}")
    offset = Random(f"odd-odd-rotation:{recipe.seed}:{size}:{scope}:{recipe.draw}").random()
    strategy = recipe.strategy
    multiplicity = 1
    if strategy in _COARSENINGS:
        witness, table, values, modulus, source_count, multiplicity = coarsening_draw(period, recipe, rng)
        targets, assignment = np.unique(values, return_inverse=True)
        if strategy == "polynomial_equalities":
            targets = np.asarray(rng.sample(range(len(targets)), len(targets)))
    else:
        witness, source_count = raw_draw(period, recipe, rng)
        table = witness.tile(period)
        if witness.modulus is None:
            targets, assignment = table.labels, np.arange(len(table.labels))
        else:
            targets, assignment = np.unique(table.labels % witness.modulus, return_inverse=True)
        if strategy == "isometric_equalities":
            assert witness.modulus is not None
            modulus = witness.modulus
        else:
            group_counts = 4 * np.bincount(assignment[table.indices].ravel(), minlength=len(targets))
            targets, modulus = group_levels(strategy, group_counts, rng, recipe.concentration)
    targets = (targets - targets[assignment[table.indices[0, 0]]]) % modulus
    tile = assignment[table.indices].astype(np.min_scalar_type(len(targets) - 1))
    counts = 4 * np.bincount(tile.ravel(), minlength=len(targets))
    spec = {
        "n": size,
        "K": witness.pre_modulus(period),
        "M": modulus,
        "pre": [["pow", witness.q], ["poly", _pre_polynomial(witness.twist)]],
        "combine": witness.combiner,
        "sampling": "odd_odd",
        "post": [
            ["lookup", {str(z): hex(int(value)) for z, value in zip(table.labels, targets[assignment], strict=True)}]
        ],
        "color": "cmr.emergency",
        "color_offset": offset,
        "odd_odd_sample": {
            "strategy": ODD_STRATEGIES[strategy],
            "combiners": list(recipe.combiners),
            "draw": recipe.draw,
            "source_partitions": source_count,
            "multiplicity": multiplicity,
            "pre_power": witness.q,
            "twist": list(witness.twist),
            **level_statistics(targets, counts, modulus, offset),
        },
    }
    positions = np.r_[np.arange(period), np.arange(period - 1, -1, -1)]
    indices = tile[positions[:, None], positions]
    return IndexedValues(targets, indices), spec, int(counts[targets == 0].sum()) / (size * size)
