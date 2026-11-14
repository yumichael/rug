"""Reference fidelity and notebook integration for conditional order sampling."""

import json
from pathlib import Path

import numpy as np
import pytest
from ruglab import evaluate
from ruglab._orders.core import Basic
from ruglab._orders.sampler import OrderSampler
from ruglab.diagnostics import periods
from ruglab.exploration import PeriodTargetError, order_class_catalogue, sample_field
from ruglab.order_classes import OrderClassRecipe, head_powers, order_sample, realize_order_polynomial, tail_power
from ruglab.pager import recipe_gallery

REFERENCE = json.loads((Path(__file__).parent / "fixtures/order_classes_reference.json").read_text())


@pytest.mark.parametrize("case", REFERENCE["cases"])
def test_draws_and_interpolation_match_frozen_research(case):
    recipe = OrderClassRecipe(
        "head" if case["power"] < tail_power(case["size"]) else "tail",
        case["seed"],
        case["draw"],
        case["power"],
        tuple(case["twist"]),
        case["combiner"],
    )
    base, values, spec = order_sample(recipe, case["size"])
    assert hex(spec["M"]) == case["modulus"]
    assert [hex(int(v)) for v in values] == case["outputs"]
    assert spec["order_sample"]["class_count_hex"] == case["class_count"]
    field = sample_field(recipe, case["size"], "checkerboard_opposite", centered=True)
    exact = evaluate(field.spec)
    roundtrip = json.loads(json.dumps(field.spec))
    assert np.array_equal(exact.values, evaluate(roundtrip).values)
    assert np.array_equal(field.result.values, exact.values)
    polynomial = realize_order_polynomial(field.spec)
    assert np.array_equal(exact.values, evaluate(polynomial).values)
    assert periods(exact, certified_torus=True) == (case["size"], case["size"])
    lower = evaluate({**field.spec, "M": field.spec["M"] // 2})
    assert periods(lower, certified_torus=True) != (case["size"], case["size"])
    assert base.indices.shape == (case["size"], case["size"])


@pytest.mark.parametrize("pairs,total", [(1, 1), (2, 12), (4, 2640), (8, 1986611520)])
def test_tail_counts_match_the_research(pairs, total):
    assert OrderSampler(tuple((2 * i, 2 * i + 1) for i in range(pairs))).total == total


@pytest.mark.parametrize("size", [2**r for r in range(3, 13)])
def test_domain_dependent_head_tail_choices(size):
    q = tail_power(size)
    assert head_powers(size) == tuple(range(2, q, 2))
    for power in head_powers(size):
        assert any(Basic(size, power, (), 'or').pre[::2])
    for power in (q, q + 2, q + 4):
        assert not any(Basic(size, power, (), 'or').pre[::2])


def test_seed_reproducibility_and_actual_spacing_statistics():
    recipe = OrderClassRecipe("tail", 123, 5)
    base, values, spec = order_sample(recipe, 64)
    _, again, other = order_sample(recipe, 64)
    assert np.array_equal(values, again)
    assert spec == other
    _, changed, _ = order_sample(OrderClassRecipe("tail", 124, 5), 64)
    assert not np.array_equal(values, changed)
    info = spec["order_sample"]
    expanded = values[base.indices]
    histogram = [sum(int(v) * 16 // spec["M"] == i for v in expanded.flat) for i in range(16)]
    assert info["cell_bins"] == histogram
    positions = sorted(set(map(int, values)))
    gaps = np.diff(np.array([*positions, positions[0] + spec["M"]], dtype=object))
    assert info["min_gap_ratio"] == int(min(gaps)) * len(positions) / spec["M"]
    assert info["max_gap_ratio"] == int(max(gaps)) * len(positions) / spec["M"]


def test_tail_draw_is_identical_across_the_four_combiners():
    fields = [
        sample_field(OrderClassRecipe("tail", 0, 3, combiner=c), 64, "checkerboard_opposite", centered=True)
        for c in ("or", "xor", "add", "absdiff")
    ]
    assert all(np.array_equal(f.result.values, fields[0].result.values) for f in fields)


@pytest.mark.parametrize("case", REFERENCE["cases"])
def test_doubled_sampler_reuses_the_polynomial_and_modulus(case):
    recipe = OrderClassRecipe(
        "head" if case["power"] < tail_power(case["size"]) else "tail",
        case["seed"],
        case["draw"],
        case["power"],
        tuple(case["twist"]),
        case["combiner"],
    )
    checker = sample_field(recipe, case["size"], "checkerboard_opposite", centered=True)
    doubled = sample_field(recipe, case["size"], "doubled_checkerboard_opposite", centered=True)
    assert doubled.spec["post"] == checker.spec["post"]
    assert doubled.spec["M"] == checker.spec["M"]
    assert doubled.spec["order_sample"] == checker.spec["order_sample"]
    exact = evaluate(doubled.spec)
    assert np.array_equal(doubled.result.values, exact.values)
    assert np.array_equal(doubled.result.values, evaluate(realize_order_polynomial(doubled.spec)).values)
    assert periods(exact, certified_torus=True) == (case["size"], case["size"])
    assert periods(evaluate({**doubled.spec, "M": doubled.spec["M"] // 2}), certified_torus=True) != (
        case["size"],
        case["size"],
    )
    assert sorted(map(int, exact.values.flat)) == sorted(map(int, checker.result.values.flat))
    center = case["size"] // 2
    assert exact.values[center, center] == checker.result.values[center, center]


def test_head_base_that_moves_into_tail_is_unavailable():
    with pytest.raises(PeriodTargetError, match="belongs to the tail"):
        sample_field(OrderClassRecipe("head", 0, 0, pre_power=10), 64, "checkerboard_opposite")


def test_new_galleries_page_reproducibly_and_export_evaluable_specs():
    for family in ("tail", "head"):
        view, specs = recipe_gallery(
            order_class_catalogue(family, seed=7, draws=4, size=16),
            field_sizes=(16,),
            selected_combiners=("or",),
            selected_samplings=("checkerboard_opposite",),
            selected_m_selections=("minimum_period",),
            page_size=2,
            preview_pixels=64,
        )
        before = dict(specs)
        image = bytes(view.children[1].value)
        page = view.children[0].children[-2].children[2]
        page.value = 2
        assert specs != before
        page.value = 1
        assert specs == before and bytes(view.children[1].value) == image
        assert len(specs) == 2
        for spec in specs.values():
            assert periods(evaluate(spec), certified_torus=True) == (16, 16)
