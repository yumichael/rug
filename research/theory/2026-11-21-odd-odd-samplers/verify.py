"""Cross-check odd-odd class sets against native arithmetic and brute partitions."""

import sys
from itertools import combinations, combinations_with_replacement
from math import factorial
from pathlib import Path

import numpy as np
from ruglab import evaluate, periods
from ruglab.exploration import odd_odd_catalogue, sample_field
from ruglab.odd_odd import ODD_COMBINERS, ODD_STRATEGIES, partition_pool, pre_spaces
from ruglab.operations import combine, steps
from ruglab.sampler_comparison import partition_count

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-11-19-monomial-first-pass"))
from precision import odd_twists


def equality_key(flat):
    labels = {}
    signature = [labels.setdefault(int(value), len(labels)) for value in flat]
    return np.asarray(signature, dtype=np.min_scalar_type(len(labels) - 1)).tobytes()


def reference_classes(side):
    T = side // 2
    triangle = np.triu_indices(T)
    coordinates = np.arange(1, side, 2, dtype=object)
    raw = {c: set() for c in ODD_COMBINERS}
    residues = {c: set() for c in ODD_COMBINERS}
    for w in range(1, T.bit_length() + 2):
        K = 2 * side << w
        seen = set()
        for u in range(1, T, 2):
            q = u << w
            powers = steps(coordinates, [["pow", q]], modulus=K)
            for Q in odd_twists(side, q):
                twist = steps(powers, [["poly", Q]], modulus=K)
                axis = tuple(int(z) for z in (powers + 2 * powers * (powers - 1) * twist) % K)
                if axis in seen:
                    continue
                seen.add(axis)
                pre = np.asarray(axis, dtype=object)
                for c in ODD_COMBINERS:
                    tile = np.asarray(combine(c, pre[:, None], pre), dtype=np.int64)
                    raw[c].add(equality_key(tile[triangle]))
                    for m in range(1, int(tile.max()).bit_length() + 1):
                        reduced = tile & ((1 << m) - 1)
                        if not np.array_equal(reduced, reduced[::-1]):
                            residues[c].add(equality_key(reduced[triangle]))
    return raw, residues


def check_class_sets():
    scopes = (ODD_COMBINERS, *((c,) for c in ODD_COMBINERS))
    for side in (8, 16, 32, 64):
        inventories = []
        for residue, expected in enumerate(reference_classes(side)):
            actual = {c: partition_pool(side // 2, c, bool(residue), 16_000_000) for c in scopes}
            for c in ODD_COMBINERS:
                assert actual[(c,)].keys() == expected[c], (side, c, residue)
            assert actual[ODD_COMBINERS].keys() == set.union(*expected.values()), (side, residue)
            if not residue:
                count = sum(space.count for space in pre_spaces(side // 2))
                assert all(count == len(actual[(c,)]) for c in ("and", "or", "add", "absdiff"))
            if side == 16:
                for k in range(1, len(ODD_COMBINERS) + 1):
                    for subset in combinations(ODD_COMBINERS, k):
                        pool = partition_pool(side // 2, subset, bool(residue), 16_000_000)
                        assert pool.keys() == set.union(*(expected[c] for c in subset)), (subset, residue)
            inventories.append([len(actual[c]) for c in scopes])
        print(side, "raw", inventories[0], "residues", inventories[1], flush=True)


def set_partitions(labels, groups=1):
    if len(labels) == 10:
        yield labels, groups
        return
    for i in range(groups + 1):
        yield from set_partitions((*labels, i), max(groups, i + 1))


def check_coarsening_counts():
    # At side eight, the finest partition is ten unordered pairs of four inputs.
    pairs = list(combinations_with_replacement(range(4), 2))
    half_shift = [pairs.index(tuple(sorted((3 - a, b)))) for a, b in pairs]
    equalities = orders = 0
    for labels, groups in set_partitions((0,)):
        if any(labels[i] != labels[j] for i, j in enumerate(half_shift)):
            equalities += 1
            orders += factorial(groups - 1)
    assert equalities == partition_count(10, False) - partition_count(3, False)
    assert orders == partition_count(10, True) - partition_count(3, True)
    print("side eight finest support:", equalities, "merged or raw partitions;", orders, "orders")


def check_draws():
    catalogue = odd_odd_catalogue(draws=2)
    scopes = (ODD_COMBINERS, ("and", "xor"), ("or", "add", "absdiff"), ("xor", "clmul"))
    cases = 0
    for side in (16, 64):
        for subset in (*scopes, *((c,) for c in ODD_COMBINERS)):
            for strategy in ODD_STRATEGIES:
                for draw in range(2):
                    recipe = catalogue.build(combiners=subset, strategy=strategy, draw=draw)
                    panel = sample_field(recipe, side, "odd_odd", centered=True)
                    assert panel.spec["combine"] in subset
                    assert panel.spec["odd_odd_sample"]["combiners"] == list(subset)
                    native = evaluate(panel.spec)
                    assert np.array_equal(panel.values.expand(), native.values)
                    assert periods(native, certified_torus=True) == (side, side)
                    assert native.values[side // 2, side // 2] == 0
                    assert native.spec["origin"] == [-side // 2, -side // 2]
                    assert np.max(native.values) < native.modulus
                    if strategy == "polynomial_orders":
                        half = side // 2
                        reduced = native.values % (native.modulus // 2)
                        assert np.array_equal(reduced[:half], reduced[half:])
                        assert np.array_equal(reduced[:, :half], reduced[:, half:])
                    if strategy.endswith("_equal"):
                        assert panel.distinct_values == native.modulus
                    cases += 1
    print(cases, "native full-period draws checked")


if __name__ == "__main__":
    check_class_sets()
    check_coarsening_counts()
    check_draws()
