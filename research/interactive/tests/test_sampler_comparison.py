"""Exact comparison sample spaces and portable render specifications."""

from fractions import Fraction
from itertools import product
from math import factorial

import ipywidgets as widgets
import numpy as np
import pytest
from ruglab._orders.combinatorics import admissible
from ruglab.exploration import PeriodTargetError, sample_field, sampler_comparison_catalogue
from ruglab.sampler_comparison import (
    STRATEGIES,
    ComparisonRecipe,
    base_pool,
    canonical_partition,
    component_model,
    isometric_coordinates,
    isometric_equalities,
    isometric_order_extras,
    isometric_window_orders,
    partition_count,
    power_groups,
)
from ruglab.studio import evaluate, periods, recipe_gallery


def test_complete_side64_twist_pools_and_domain_groups():
    groups = power_groups(64)
    assert [g.powers for g in groups] == [(2,), (4,), (6, 8), (10,)]
    assert [len(base_pool(64, g, 4096)[0]) for g in groups] == [416, 224, 49, 1]
    assert [len(base_pool(64, g, 4096)[1]) for g in groups[:3]] == [512, 256, 64]
    assert power_groups(1024)[-2].powers == (10,)


def test_subset_unions_deduplicate_partitions_and_isometric_orders():
    size = 16
    group = power_groups(size)[0]
    combiners = ("xor", "add")
    _, all_bases = base_pool(size, group, 4096)
    expected = {canonical_partition(basic.indices).tobytes() for basic in all_bases if basic.combiner in combiners}
    entries, _ = base_pool(size, group, 4096, combiners=combiners)
    assert {entry.partition.tobytes() for entry in entries} == expected
    assert len(entries) == 3

    def window_keys(scope):
        choices = isometric_window_orders(size, group, 4096, (0, 1, 2), 50000, combiners=scope)
        keys = set()
        for basic, values, _ in choices:
            _, ranks = np.unique(values, return_inverse=True)
            anchored = (ranks - ranks[basic.anchor]) % (int(ranks.max()) + 1)
            keys.add(anchored[basic.indices].tobytes())
        return keys

    xor, add = (window_keys((combiner,)) for combiner in combiners)
    assert xor & add
    assert window_keys(combiners) == xor | add
    # XOR's raw partition already supplies the coarse ADD orders in this pool.
    assert isometric_order_extras(size, group, 4096, 50000, combiners=("add",))
    assert not isometric_order_extras(size, group, 4096, 50000, combiners=combiners)


@pytest.mark.parametrize("sampling", ("checkerboard_opposite", "doubled_checkerboard_opposite"))
@pytest.mark.parametrize("strategy", tuple(STRATEGIES))
@pytest.mark.parametrize("group", power_groups(8))
@pytest.mark.parametrize("combiners", [("or", "xor", "add", "absdiff"), ("xor", "add")])
def test_lookup_roundtrips_with_full_period_and_reproducible_rotation(strategy, group, sampling, combiners):
    recipe = ComparisonRecipe(group, strategy, 1, 17, combiners=combiners)
    field = sample_field(recipe, 8, sampling, centered=True)
    result = evaluate(field.spec)
    assert np.array_equal(result.values, field.values.expand())
    assert periods(result, certified_torus=True) == (8, 8)
    assert field.spec["combine"] in combiners
    assert field.spec["comparison_sample"]["combiners"] == list(combiners)
    assert 0 <= field.spec["color_offset"] < 1
    assert sample_field(recipe, 8, sampling, centered=True).spec == field.spec

    if sampling == "doubled_checkerboard_opposite":
        from ruglab.sampling import coordinates

        opposite = sample_field(recipe, 8, "checkerboard_opposite", centered=True)
        x, y = coordinates((8, 8), sampling, (-4, -4))
        cols = np.asarray(((x - y - 1) // 2 + 4) % 8, dtype=np.intp)
        rows = np.asarray(((x + y + 1) // 2 + 3) % 8, dtype=np.intp)
        assert np.array_equal(field.values.expand(), opposite.values.expand()[rows, cols])
        assert np.array_equal(
            np.unique(field.values.expand(), return_counts=True)[1],
            np.unique(opposite.values.expand(), return_counts=True)[1],
        )
        assert field.spec["color_offset"] == opposite.spec["color_offset"]
        assert field.spec["post"] == opposite.spec["post"]
        assert field.spec["M"] == opposite.spec["M"]


def test_all_precision_counts_match_exhaustive_partitions_and_orders():
    for n in range(2, 6):
        equalities, orders = set(), set()
        for k in range(1, n + 1):
            for rest in product(range(k), repeat=n - 1):
                rank = np.array((0, *rest))
                if len(set(rank)) != k:
                    continue
                orders.add(tuple(rank))
                equalities.add(tuple(canonical_partition(rank)))
        assert partition_count(n, True) == len(orders)
        assert partition_count(n, False) == len(equalities)


def test_union_correction_equalizes_exact_small_spatial_class_masses():
    entries, _ = base_pool(8, power_groups(8)[0], 4096)
    masses = {}
    for e in entries:
        model, _ = component_model(e.basic)
        classes = set()
        n = len(e.basic.nodes)
        for k in range(2, n + 1):
            for rest in product(range(k), repeat=n - 1):
                rank = (0, *rest)
                if len(set(rank)) != k or not admissible(rank, e.basic.components):
                    continue
                field = np.array(rank)[e.basic.indices]
                classes.add(field.tobytes())
                flat = field.ravel()
                b = sum(np.array_equal(flat, flat[o.first][o.partition.ravel()]) for o in entries)
                masses[field.tobytes()] = masses.get(field.tobytes(), 0) + Fraction(1, b)
        assert len(classes) == model.total
    assert set(masses.values()) == {1}
    assert sum(factorial(len(e.first) - 1) for e in entries) > len(entries)


def test_isometry_coordinates_match_bruteforce_parity_conditions():
    nodes, modulus = (1, 3, 5, 7), 8
    bits, generators = isometric_coordinates(nodes, modulus)
    got = set()
    for a in product(*(range(1 << b) for b in bits)):
        got.add(
            tuple(
                (z - 1 + sum(c * g[i] for c, g in zip(a, generators, strict=True))) % modulus
                for i, z in enumerate(nodes)
            )
        )
    expected = set()
    for a1, a2, a3 in product(range(8), repeat=3):
        if a1 % 2 == 0 or a2 % 2 or a3 % 2:
            continue
        expected.add(tuple((a1 * (z - 1) + a2 * (z * z - 1) + a3 * (z**3 - 1)) % modulus for z in nodes))
    assert got == expected


def test_isometric_equalities_are_full_period_and_deduplicated():
    choices = isometric_equalities(8, power_groups(8)[0], 4096)
    keys = []
    for basic, values, _ in choices:
        keys.append(canonical_partition(values[basic.indices]).tobytes())
        assert basic.full(values)
    assert len(keys) == len(set(keys))
    assert isometric_order_extras(8, power_groups(8)[0], 4096, 50000)


def test_work_limits_never_return_partial_spaces():
    with pytest.raises(PeriodTargetError, match="No restricted subset"):
        sample_field(
            ComparisonRecipe(power_groups(64)[0], "equality_iid", 0, 0, max_bases=1), 64, "checkerboard_opposite"
        )
    with pytest.raises(PeriodTargetError, match="no partial union"):
        sample_field(
            ComparisonRecipe(power_groups(8)[0], "isometric_orders", 0, 0, max_isometry_tables=1),
            8,
            "checkerboard_opposite",
        )


def test_gallery_and_dynamic_groups():
    catalogue = sampler_comparison_catalogue(size=8, draws=2, strategies=("equality_equal",))
    assert catalogue.for_size is not None
    assert len(catalogue.for_size(64).dimensions["power_group"]) == 4
    view, specs = recipe_gallery(
        catalogue,
        field_sizes=(8,),
        selected_samplings=("checkerboard_opposite",),
        selected_m_selections=("catalogue",),
        grouped_dimensions=4,
        group_wrap_after=2,
        page_size=1,
        preview_pixels=32,
    )
    assert view.children[1].value and len(specs) == 2
    rows = {
        w.children[0].value: w
        for w in view.children[0].children
        if isinstance(w, widgets.HBox) and w.children and isinstance(w.children[0], widgets.Label)
    }
    combiner_boxes = {box.description: box for box in rows["Combiners (pooled)"].children[1:]}
    assert all(box.value for box in combiner_boxes.values())
    combiner_boxes["OR"].value = combiner_boxes["ABSDIFF"].value = False
    assert len(specs) == 2
    assert all(spec["comparison_sample"]["raw_partitions"] == 1 for spec in specs.values())

    size_boxes = {box.description: box for box in rows["Field size"].children[1:]}
    size_boxes["8"].value = False
    size_boxes["64"].value = True
    assert len(specs) == 2
    for spec in specs.values():
        assert spec["comparison_sample"]["combiners"] == ["xor", "add"]
        assert spec["comparison_sample"]["raw_partitions"] == 160


def test_isometric_high_precision_witness_has_global_isometric_polynomial():
    from math import prod
    from random import Random

    from ruglab._orders.core import nu
    from ruglab.sampler_comparison import draw_isometric_union

    group = power_groups(8)[1]
    recipe = ComparisonRecipe(group, "isometric_orders", 0, 3)
    entries, _ = base_pool(8, group, 4096)
    basic, values, modulus = draw_isometric_union(entries, 8, recipe, Random(3))
    nodes = basic.nodes
    # Interpolate the actual selected witness independently, including odd denominator inversion.
    coefficients = [0] * len(nodes)
    for i, node in enumerate(nodes):
        polynomial = [1]
        for other in nodes:
            if other == node:
                continue
            out = [0] * (len(polynomial) + 1)
            for j, a in enumerate(polynomial):
                out[j] -= other * a
                out[j + 1] += a
            polynomial = out
        denominator = prod(node - other for other in nodes if other != node)
        depth = int(nu(denominator))
        # Subtract the identity first; this correction is divisible by 2^(depth+2).
        target = int(values[i]) - node
        assert target % (1 << depth) == 0
        scale = (target >> depth) * pow(denominator >> depth, -1, modulus)
        coefficients = [(a + scale * b) % modulus for a, b in zip(coefficients, polynomial, strict=True)]
    coefficients[1] = (coefficients[1] + 1) % modulus
    assert coefficients[1] % 2 == 1
    assert sum(coefficients[2::2]) % 2 == 0
    assert sum(coefficients[3::2]) % 2 == 0
    assert [sum(a * pow(z, j, modulus) for j, a in enumerate(coefficients)) % modulus for z in nodes] == list(values)


@pytest.mark.parametrize("size", [8, 16, 32, 64, 128])
def test_isometric_tail_reduction_covers_extra_valuations_odd_parts_and_twists(size):
    from ruglab._orders.core import Basic, nu
    from ruglab.sampler_comparison import minimum_bits

    group = power_groups(size)[-1]
    entries, _ = base_pool(size, group, 4096)
    raw_keys = {e.partition.tobytes() for e in entries}

    def signature(basic, values):
        field = np.asarray(values)[basic.indices]
        if canonical_partition(field).tobytes() in raw_keys:
            return None
        _, ranks = np.unique(values, return_inverse=True)
        ranks = (ranks - ranks[basic.anchor]) % (int(ranks.max()) + 1)
        return ranks[basic.indices].astype(np.uint32).tobytes()

    expected = {signature(b, v) for b, v, _ in isometric_order_extras(size, group, 4096, 50000)}
    r = size.bit_length() - 1
    for w in range(1, max(1, r - 4) + 4):
        for u in (1, 3, 5):
            while (1 << w) * u < r + w:
                u += 2
            for Q in ((), (3, -2, 1)):
                basic = Basic(size, (1 << w) * u, Q, "or")
                upper = max(int(nu(a - b)) for i, a in enumerate(basic.nodes) for b in basic.nodes[:i])
                for m in range(minimum_bits(basic), upper + 1):
                    modulus = 1 << m
                    bits, generators = isometric_coordinates(basic.nodes, modulus)
                    assert sum(bits) < 14
                    for coefficients in product(*(range(1 << b) for b in bits)):
                        values = [
                            (z - basic.nodes[0] + sum(c * g[i] for c, g in zip(coefficients, generators, strict=True)))
                            % modulus
                            for i, z in enumerate(basic.nodes)
                        ]
                        key = signature(basic, values)
                        assert key is None or key in expected
