from io import BytesIO
from pathlib import Path

import json5
import numpy as np
import pytest
from PIL import Image
from ruglab import Sweep, dsl, evaluate, gallery, paired
from ruglab.diagnostics import periods, signature
from ruglab.exploration import (
    COMBINER_COLORS,
    PatternRecipe,
    PeriodTargetError,
    PostRecipe,
    PrePowerStudyRecipe,
    _minimum_group_values,
    pre_power_study_catalogue,
    sample_field,
)
from ruglab.indexed import IndexedValues, combination_table
from ruglab.operations import clmul
from ruglab.plotting import colorize, export, indexed_order_palette
from ruglab.previews import PreviewPanel, indexed_preview, preview_grid
from ruglab.research import family_pre_modulus, minimum_post_modulus, uniform_xor
from ruglab.sampling import coordinates, resample_view
from ruglab.specs import SAMPLINGS


@pytest.mark.parametrize(
    "name,fn",
    [
        ("and", lambda a, b: a & b),
        ("or", lambda a, b: a | b),
        ("xor", lambda a, b: a ^ b),
        ("add", lambda a, b: a + b),
        ("mult", lambda a, b: a * b),
        ("clmul", clmul),
        ("absdiff", lambda a, b: abs(a - b)),
    ],
)
def test_combiner_reference(name, fn):
    s = {
        "n": 16,
        "K": 32,
        "M": 128,
        "pre": [["pow", 2]],
        "combine": name,
        "post": [["pow", 3], ["mult", 7], ["add", 11]],
    }
    r = evaluate(s)
    for y in range(16):
        for x in range(16):
            a, b = pow(x, 2, 32), pow(y, 2, 32)
            assert r.values[y, x] == (pow(fn(a, b), 3, 128) * 7 + 11) % 128


@pytest.mark.parametrize(
    "method,phase",
    [("even_even", (0, 0)), ("even_odd", (0, 1)), ("odd_even", (1, 0)), ("odd_odd", (1, 1))],
)
def test_absolute_parity(method, phase):
    x, y = coordinates((8, 8), method)
    assert set((x % 2).flat) == {phase[0]}
    assert set((y % 2).flat) == {phase[1]}


def test_checkerboard():
    spec = {"n": 32, "K": 32, "M": 64, "post": [["pow", 2]]}
    full, same, opposite = (
        evaluate({**spec, "sampling": method}) for method in ("full", "checkerboard_same", "checkerboard_opposite")
    )

    def pairs(result):
        return {(a % 2, b % 2) for a, b in zip(result.stages["A"].flat, result.stages["B"].flat, strict=True)}

    assert pairs(full) == {(0, 0), (0, 1), (1, 0), (1, 1)}
    assert pairs(same) == {(0, 0), (1, 1)}
    assert pairs(opposite) == {(0, 1), (1, 0)}
    assert not np.array_equal(same.values, opposite.values)

    # The native checkerboard reindexes the same operands as the legacy renderer.
    app_phase = evaluate({**spec, "sampling": "checkerboard_opposite", "shape": [16, 16], "origin": [-1, -16]})
    assert np.array_equal(app_phase.values.T, dsl.channel("32;;^;diag1:**2:%64;gray").values)


def test_large_powers_and_moduli():
    p = 2**40 + 6
    M = 2**100
    r = evaluate({"n": 8, "K": 8, "M": M, "post": [["pow", p], ["mult", 2**70 + 1]]})
    assert int(r.values[1, 3]) == pow(3 ^ 1, p, M) * (2**70 + 1) % M
    assert clmul(1 << 70, 1 << 70) == 1 << 140


def test_polynomials_and_features():
    r = evaluate(
        {
            "n": 8,
            "K": 16,
            "M": 64,
            "pre": [["poly", [1, 0, 3]]],
            "combine": ["xor", "absdiff"],
            "expression": "z0+z1**3",
        }
    )
    for y in range(8):
        for x in range(8):
            a = (1 + 3 * x**2) % 16
            b = (1 + 3 * y**2) % 16
            assert r.values[y, x] == ((a ^ b) + abs(a - b) ** 3) % 64


@pytest.mark.parametrize("name,arg", [("gray", 1), ("bitrev", 1), ("rotl", 3), ("inv", 1)])
def test_bit_operations(name, arg):
    r = evaluate({"n": 16, "K": 16, "M": 16, "pre": [[name, arg]]})
    assert r.values.shape == (16, 16)
    assert all(0 <= v < 16 for v in r.values.flat)


def test_dsl_reference_and_fusion():
    text = "16;;^;diag1:**1048576:*7:+3:%33554432:map01;gray"
    r = dsl.channel(text)
    expected = np.empty((8, 8))
    for i in range(8):
        for j in range(8):
            z = ((7 + i - j) % 16) ^ ((-8 + i + j) % 16)
            expected[i, j] = ((pow(z, 1048576, 33554432) * 7 + 3) % 33554432) / 33554432
    assert np.array_equal(r.values, expected)
    assert dsl.render([text]).shape == (8, 8, 3)


def test_dsl_pre_and_colors():
    r = dsl.channel("8;**2:%8;+;**2:%32:map01;gray")
    for i in range(8):
        for j in range(8):
            assert r.values[i, j] == ((i * i % 8 + j * j % 8) ** 2 % 32) / 32
    for color in ("RGB", "HSV", "HSL"):
        assert dsl.render([f"8;;^;%8:map01;{c}" for c in color]).shape == (8, 8, 3)


def test_dsl_rejects_unknown_execution():
    with pytest.raises(ValueError, match="Unsupported DSL expression"):
        dsl.channel("8;;^;__import__(1);gray")


def test_sweep_and_pairs():
    sweep = Sweep({"n": 8, "pre": [["pow", [2, 4]]], "combine": ["or", "xor"], "post": [["pow", [1, 2]]]})
    assert sweep.count == 8
    assert [n for n, _ in sweep.page(6, 8)] == ["6", "7"]
    assert next(iter(sweep.page(0, 1)))[1]["pre"] == [["pow", 2]]
    with pytest.raises(ValueError, match="Paired variation lengths differ"):
        list(paired({}, M=[1], K=[1, 2]))


def test_research_rules_and_periods():
    assert family_pre_modulus(8, 512, "and") == 4096
    assert family_pre_modulus(8, 512, "and", sampling="checkerboard_opposite") == 16384
    s = {"n": 64, "K": 64, "M": 64, "pre": [["pow", 2]], "combine": "and"}
    r = evaluate(s)
    assert periods(r, certified_torus=True) == (32, 32)
    assert minimum_post_modulus(s, 32, 2) == 128
    assert minimum_post_modulus({**s, "sampling": "checkerboard_opposite"}, 32, 2) == 2048
    with pytest.raises(ValueError, match="known complete periodic torus"):
        periods(r)
    with pytest.raises(ValueError, match="exceeds max_cells"):
        minimum_post_modulus({**s, "K": 1024}, 32)


def test_signatures_and_gallery(tmp_path):
    a = evaluate({"n": 8, "M": 32, "expression": "4*z"})
    b = evaluate({"n": 8, "M": 64, "expression": "8*z"})
    assert signature(a) == signature(b)
    p = tmp_path / "favorites.json"
    gallery.save(p, "one", {"n": 8}, notes="interesting", seed=2)
    saved = gallery.load(p, "interesting")["one"]
    assert saved["seed"] == 2 and saved["spec"]["M"] == 8


def test_seed_is_local_and_repeatable():
    assert uniform_xor(64, 3) == uniform_xor(64, 3)
    assert uniform_xor(64, 3)["post"][1][1] % 2 == 1
    assert uniform_xor(64, 3)["sampling"] == "checkerboard_opposite"
    with pytest.raises(ValueError, match="opposite-parity operand checkerboard"):
        uniform_xor(64, sampling="checkerboard_same")


def test_exploration_preserves_a_diamond_without_power_aliases():
    recipe = PatternRecipe("and", pre_power=2, twist=1, post_power=14)
    straight = sample_field(recipe, 256, "odd_odd")
    rotated = sample_field(recipe, 256, "checkerboard_same")
    assert straight.zero_fraction == 0
    assert rotated.repeat_shape == "diamond"

    result = evaluate(rotated.result.spec)
    assert np.array_equal(result.values, rotated.result.values)
    assert periods(result, certified_torus=True) == (256, 256)
    assert np.array_equal(result.values, np.roll(result.values, (128, 128), axis=(0, 1)))
    assert result.modulus is not None
    inputs = set(result.stages["z0"].flat) | {0}
    assert len(set(result.values.flat) | {0}) == len(inputs)
    assert len({pow(z, recipe.post_power, result.modulus // 2) for z in inputs}) < len(inputs)


def test_exploration_parameters_follow_sampling():
    recipe = PatternRecipe("xor", pre_power=2, twist=1, post_power=7)
    for sampling, K, expected_periods in (
        ("full", 512, (256, 256)),
        ("checkerboard_same", 1024, (256, 256)),
        ("checkerboard_opposite", 512, (256, 256)),
        ("even_even", 2048, (256, 256)),
        ("even_odd", 1024, (128, 256)),
        ("odd_even", 1024, (256, 128)),
        ("odd_odd", 1024, (256, 256)),
    ):
        field = sample_field(recipe, 256, sampling)
        assert field.result.spec["K"] == K
        assert periods(field.result, certified_torus=True) == expected_periods
        exact = evaluate(field.result.spec)
        assert np.array_equal(field.result.values, exact.values)
        assert field.distinct_values == len(set(exact.stages["z0"].flat))

    constant = sample_field(PatternRecipe("and", pre_power=16, twist=0, post_power=7), 256, "even_odd")
    assert constant.repeat_shape == "constant"
    assert constant.zero_fraction == 1
    assert constant.result.modulus == 1
    assert not constant.result.values.any()


def test_exploration_classifies_two_cell_fields():
    recipe = PatternRecipe("xor", 2, 0, 3)
    diamond = sample_field(recipe, 2, "full")
    assert diamond.repeat_shape == "diamond"
    assert np.array_equal(diamond.result.values, [[0, 1], [1, 0]])
    assert sample_field(recipe, 2, "odd_odd").repeat_shape == "constant"


@pytest.mark.parametrize("twist,post", [(0, 0), (13, 7)])
@pytest.mark.parametrize("combiner", COMBINER_COLORS)
def test_pre_power_study_preserves_wide_even_even_values(twist, post, combiner):
    field = sample_field(PrePowerStudyRecipe(64, twist, post, combiner), 16, "even_even")
    exact = evaluate(field.spec)
    assert field.spec["K"] > 2**64
    if twist:
        assert len(field.spec["pre"][1][1]) == 10
    assert np.array_equal(field.result.values, exact.values)
    assert field.distinct_values == len(set(exact.stages["z0"].flat))
    values = set(exact.values.flat) | {0}
    assert len({value % (field.spec["M"] // 2) for value in values}) < len(values)


@pytest.mark.parametrize("combiner", COMBINER_COLORS)
@pytest.mark.parametrize("sampling", SAMPLINGS)
def test_pre_power_study_combiners_match_exact_evaluation(combiner, sampling):
    recipe = PrePowerStudyRecipe(4, 13, 7, combiner)
    field = sample_field(recipe, 8, sampling)
    exact = evaluate(field.spec)
    assert field.spec["combine"] == combiner
    assert np.array_equal(field.result.values, exact.values)
    assert field.distinct_values == len(set(exact.values.flat))
    assert field.zero_fraction == np.count_nonzero(exact.values == 0) / exact.values.size
    larger = evaluate({**field.spec, "shape": [16, 16]})
    assert np.array_equal(larger.values, np.tile(exact.values, (2, 2)))


def test_pre_power_catalogue_groups_sweeps_in_combiner_order():
    catalogue = pre_power_study_catalogue()
    expected = ("and", "or", "xor", "add", "absdiff", "mult", "clmul")
    assert catalogue.dimensions["combiner"] == expected
    recipes = catalogue.recipes()
    for recipe, power in zip(recipes[:32], range(2, 65, 2), strict=True):
        assert isinstance(recipe, PrePowerStudyRecipe)
        assert recipe.pre_power == power
    for index, combiner in enumerate(expected):
        assert all(recipe.combiner == combiner for recipe in recipes[index * 5120 : (index + 1) * 5120])


@pytest.mark.parametrize("combiner", COMBINER_COLORS)
@pytest.mark.parametrize("sampling", SAMPLINGS)
def test_pre_power_combiners_minimum_modulus(combiner, sampling):
    recipe = PrePowerStudyRecipe(4, 13, 7, combiner)
    original = sample_field(recipe, 8, sampling)
    try:
        field = sample_field(recipe, 8, sampling, minimum_post_modulus=True)
    except PeriodTargetError:
        assert periods(original.result, certified_torus=True) != (8, 8)
        return
    exact = evaluate(field.spec)
    assert np.array_equal(field.result.values, exact.values)
    assert periods(exact, certified_torus=True) == (8, 8)
    smaller = evaluate({**field.spec, "M": field.spec["M"] // 2})
    assert periods(smaller, certified_torus=True) != (8, 8)


@pytest.mark.parametrize("sampling,phase", [("checkerboard_same", 0), ("checkerboard_opposite", 1)])
@pytest.mark.parametrize("recipe", [PatternRecipe("or", 2, 1, 3), PostRecipe("xor", "any powers", 2, 2, 1)])
def test_explore_checkerboards_reflect_before_the_combiner(recipe, sampling, phase):
    size = 16
    field = sample_field(recipe, size, sampling)
    result = evaluate(field.spec)
    reflected = (-np.arange(size) - phase) % size
    assert field.spec["checkerboard_axis"] == "vertical"
    a, b = coordinates((size, size), sampling, checkerboard_axis="vertical")
    mirror_a, mirror_b = coordinates((size, size), sampling, (1 - size - phase, 0), checkerboard_axis="vertical")
    assert np.array_equal(mirror_a[:, ::-1], b)
    assert np.array_equal(mirror_b[:, ::-1], a)
    assert np.array_equal(result.values[:, reflected], result.values)
    assert np.array_equal(result.values, field.result.values)
    horizontal = evaluate({**field.spec, "checkerboard_axis": "horizontal"})
    assert result.values.shape == (size, size)
    assert np.array_equal(result.values, np.roll(horizontal.values.T, phase, axis=0))


@pytest.mark.parametrize(
    "family,valuation",
    [("odd power", 0), ("even power", 1), ("odd sum", 0), ("even sum tail", 5), ("even only", 2), ("any powers", 4)],
)
def test_post_polynomial_draw_keeps_the_reference_period(family, valuation):
    recipe = PostRecipe("xor", family, valuation, seed=2, draw=1)
    field = sample_field(recipe, 16, "checkerboard_opposite")
    assert field.spec["pre"] == []
    assert np.array_equal(field.result.values, evaluate(field.spec).values)
    assert periods(field.result, certified_torus=True) == (16, 16)
    bigger = evaluate({**field.spec, "shape": [32, 32]})
    assert np.array_equal(bigger.values, np.tile(field.result.values, (2, 2)))


@pytest.mark.parametrize(
    "recipe,size,sampling,expected_modulus",
    [
        (PatternRecipe("or", 2, 0, 3), 8, "full", 16),
        (PrePowerStudyRecipe(2, 0, 2), 8, "full", 16),
        (PrePowerStudyRecipe(2, 0, 5), 8, "checkerboard_opposite", 16),
        (PostRecipe("xor", "even only", 4, 0, 0), 16, "checkerboard_opposite", 64),
        (PostRecipe("xor", "even only", 60, 0, 0), 8, "checkerboard_opposite", 32),
        (PostRecipe("xor", "even power", 1, 0, 0), 8, "checkerboard_same", 64),
        (PrePowerStudyRecipe(64, 13, 7), 16, "even_even", 2**74),
    ],
)
def test_gallery_minimum_modulus_matches_native_periods(recipe, size, sampling, expected_modulus):
    original = sample_field(recipe, size, sampling)
    field = sample_field(recipe, size, sampling, minimum_post_modulus=True)
    assert field.spec["K"] == original.spec["K"]
    assert field.spec["M"] == expected_modulus
    exact = evaluate(field.spec)
    assert np.array_equal(field.result.values, exact.values)
    assert field.distinct_values == len(set(exact.values.flat))
    assert field.zero_fraction == np.count_nonzero(exact.values == 0) / exact.values.size
    assert periods(exact, certified_torus=True) == (size, size)
    smaller = evaluate({**field.spec, "M": expected_modulus // 2})
    assert periods(smaller, certified_torus=True) != (size, size)
    larger_window = evaluate({**field.spec, "shape": [2 * size, 2 * size]})
    assert np.array_equal(larger_window.values, np.tile(exact.values, (2, 2)))


@pytest.mark.parametrize(
    "recipe,sampling",
    [(PatternRecipe("and", 16, 0, 7), "even_odd"), (PrePowerStudyRecipe(2, 0, 0), "odd_even")],
)
def test_gallery_minimum_modulus_rejects_unattainable_periods(recipe, sampling):
    with pytest.raises(PeriodTargetError, match="No M gives 16x16 axis periods"):
        sample_field(recipe, 16, sampling, minimum_post_modulus=True)


def test_indexed_combination_preserves_unsigned_products():
    operand = 2**32 - 2**16
    table = combination_table(np.array([0, operand]), np.array([operand]), "mult")
    assert table.labels.tolist() == [0, operand**2]
    assert table.expand().tolist() == [[0], [operand**2]]


def test_strip_preview_matches_full_bilinear_resize():
    rng = np.random.default_rng(1)
    values = IndexedValues(np.arange(32), rng.integers(32, size=(257, 1025), dtype=np.uint8))
    palette = indexed_order_palette(values, "gray")
    rgb = Image.fromarray(palette[values.indices][..., :3])
    expected = rgb.resize((37, 37), Image.Resampling.BILINEAR)
    assert np.array_equal(np.asarray(indexed_preview(values, "gray", 37)), np.asarray(expected))


@pytest.mark.parametrize(
    "sampling,expected",
    [
        ("checkerboard_same", [[8, 5], [13, 10]]),
        ("checkerboard_opposite", [[4, 1], [9, 6]]),
        ("doubled_checkerboard_opposite", [[1, 1, 3, 3], [4, 6, 6, 4], [9, 9, 11, 11], [12, 14, 14, 12]]),
        ("even_odd", [[4, 6], [12, 14]]),
        ("odd_even", [[1, 3], [9, 11]]),
    ],
)
def test_additional_sampling_selects_finished_cells(sampling, expected):
    values = np.arange(16).reshape(4, 4)
    assert resample_view(values, sampling).tolist() == expected


@pytest.mark.parametrize("n", [8, 16, 32])
def test_doubled_checkerboard_matches_xor_mirror_axes(n):
    field = evaluate(
        {
            "n": n,
            "K": 2 * n,
            "M": 4 * n,
            "pre": [],
            "combine": "xor",
            "sampling": "checkerboard_opposite",
            "checkerboard_axis": "vertical",
            "post": [["pow", 2]],
        }
    ).values
    doubled = resample_view(field, "doubled_checkerboard_opposite")
    rows = (-np.arange(n)) % n
    for view in (field, doubled):
        assert np.array_equal(view, view[rows])
        assert np.array_equal(view, view[:, ::-1])


@pytest.mark.parametrize("minimum", [False, True])
@pytest.mark.parametrize(
    "recipe",
    [
        PatternRecipe("or", 2, 1, 3),
        PatternRecipe("xor", 4, 0, 2),
        PostRecipe("xor", "even power", 1, 0, 0),
        PrePowerStudyRecipe(2, 1, 2),
    ],
)
def test_doubled_main_sampling_matches_exact_evaluation(recipe, minimum):
    field = sample_field(recipe, 16, "doubled_checkerboard_opposite", minimum_post_modulus=minimum)
    assert np.array_equal(field.result.values, evaluate(field.spec).values)
    full = evaluate({**field.spec, "sampling": "full"}).values
    assert np.array_equal(field.result.values, resample_view(full, "doubled_checkerboard_opposite"))
    bigger = evaluate({**field.spec, "shape": [32, 32]})
    assert np.array_equal(bigger.values, np.tile(field.result.values, (2, 2)))
    if minimum:
        assert periods(field.result, certified_torus=True) == (16, 16)


def test_doubled_checkerboard_export_preserves_colors_and_dimensions(tmp_path):
    field = sample_field(PatternRecipe("or", 2, 1, 3), 4, "checkerboard_opposite")
    original = field.result.values.copy()
    path = tmp_path / "doubled.png"
    export(field.result, path, mode="order", additional_sampling="doubled_checkerboard_opposite")
    colors = np.asarray(indexed_preview(field.values, field.spec["color"], 4))
    row, column = np.indices((4, 4))
    expected = np.where(((row + column) % 2 == 0)[..., None], np.roll(colors, -1, axis=1), colors)
    with Image.open(path) as image:
        assert image.size == (4, 4)
        assert np.array_equal(np.asarray(image), expected)
    assert np.array_equal(field.result.values, original)


def test_additional_sampling_export_preserves_base_colors(tmp_path):
    field = sample_field(PatternRecipe("or", 2, 1, 3), 4, "checkerboard_opposite")
    path = tmp_path / "diamond.png"
    export(field.result, path, mode="order", additional_sampling="checkerboard_same")
    colors = np.asarray(indexed_preview(field.values, field.spec["color"], 4))
    expected = colors[[[2, 1], [3, 2]], [[0, 1], [1, 2]]]
    with Image.open(path) as image:
        assert np.array_equal(np.asarray(image), expected)


@pytest.mark.parametrize(
    "recipe,sampling,wide",
    [
        (PatternRecipe("clmul", 2, 1, 3), "odd_even", False),
        (PatternRecipe("clmul", 16, -3, 27), "even_even", True),
    ],
)
def test_indexed_preview_matches_exact_order_colors(recipe, sampling, wide):
    field = sample_field(recipe, 256, sampling)
    exact = evaluate(field.spec)
    assert exact.modulus is not None
    assert (exact.modulus > 2**64) == wide
    assert np.array_equal(field.result.values, exact.values)
    expected_rgb = np.rint(colorize(exact, mode="order") * 255).astype(np.uint8)
    preview = indexed_preview(field.values, exact.colors, 256)
    assert np.array_equal(np.asarray(preview), expected_rgb)


def test_presets_render():
    presets = json5.loads(Path("presets/examples.jsonc").read_text(encoding="utf-8"))
    for key, value in presets.items():
        if key == "dsl":
            dsl.render(value)
        else:
            assert evaluate(value).values.size > 0


def test_sweep_direct_lookup_and_truncated_clmul():
    sweep = Sweep({"n": 8, "pre": [["pow", [2, 4]]], "combine": ["or", "xor"], "post": [["pow", [1, 2]]]})
    assert sweep.get(7)["post"] == [["pow", 2]]
    with pytest.raises(IndexError):
        sweep.get(8)
    assert clmul(8, 8) == 64
    r = evaluate(
        {
            "n": 16,
            "K": 16,
            "M": 256,
            "combine": {"name": "clmul_low", "width": 4},
        }
    )
    assert r.values[8, 8] == 0


def test_nonpolynomial_expression_does_not_reduce_before_division():
    r = evaluate({"n": 8, "K": 8, "M": 8, "expression": "(z0 + 8) // 2"})
    z = r.stages["z0"]
    assert np.array_equal(r.values, ((z + 8) // 2) % 8)
    assert np.array_equal(evaluate({"n": 8, "expression": "7"}).values, np.full((8, 8), 7))
    with pytest.raises(ValueError, match="Integer operations require integer arguments"):
        dsl.expression("z**0.5", {"z": np.arange(8, dtype=object)})


def test_native_rejects_fractional_arithmetic():
    with pytest.raises(ValueError, match="Native expressions use integer arithmetic"):
        evaluate({"n": 8, "expression": "z0/2"})


@pytest.mark.parametrize(
    "values,initial,expected",
    [
        ([4, 6, 4], 8, 4),
        ([0, 4, 6], 8, 8),
        ([64, 64], 128, 1),
        ([0, 0], 1, 1),
        ([2**80, 2**80 + 2], 2**81, 4),
    ],
)
def test_minimum_group_values_only_preserves_actual_outputs(values, initial, expected):
    outputs, modulus = _minimum_group_values(np.array(values, dtype=object), initial)
    assert modulus == expected
    assert outputs.tolist() == [value % expected for value in values]


@pytest.mark.parametrize("transpose", [False, True])
def test_preview_titles_and_captions_stay_out_of_neighbouring_plots(transpose):
    panel = PreviewPanel(Image.new("RGB", (128, 128), "red"), "checkerboard opposite · M: Minimum period")
    heading = "#123 OR · 128x128 · Pre 64 · twist 13 · post 7 · M: Minimum period"
    png = preview_grid(
        [(heading, [panel]), (heading, [panel])], 128, transpose=transpose, wrap_after=2 if transpose else 1
    )
    with Image.open(BytesIO(png)) as image:
        pixels = np.asarray(image)
    assert np.all(pixels[:, 136:144] == 255)
    assert np.count_nonzero(np.all(pixels == [255, 0, 0], axis=-1)) == 2 * 128 * 128


@pytest.mark.parametrize("sampling", SAMPLINGS)
@pytest.mark.parametrize(
    "recipe",
    [
        PatternRecipe("or", 2, 1, 3),
        PostRecipe("xor", "any powers", 4, 0, 0),
        PrePowerStudyRecipe(64, 13, 7),
    ],
)
def test_distinct_outputs_policy_preserves_the_partition_at_minimum_modulus(recipe, sampling):
    original = sample_field(recipe, 8, sampling)
    field = sample_field(recipe, 8, sampling, m_selection="distinct_outputs")
    before = original.result.values
    after = field.result.values
    assert np.array_equal(after, evaluate(field.spec).values)
    assert field.distinct_values == original.distinct_values
    assert np.array_equal(after, before % field.spec["M"])
    if (before == 0).any():
        assert np.array_equal(before == 0, after == 0)
    if field.spec["M"] > 1:
        assert len(set((after % (field.spec["M"] // 2)).flat)) < field.distinct_values
    assert field.zero_fraction == np.count_nonzero(after == 0) / after.size
    assert periods(field.result, certified_torus=True) == periods(original.result, certified_torus=True)


@pytest.mark.parametrize("sampling", SAMPLINGS)
@pytest.mark.parametrize("policy", ["catalogue", "distinct_outputs", "minimum_period"])
@pytest.mark.parametrize(
    "recipe", [PatternRecipe("or", 2, 1, 3), PostRecipe("xor", "even power", 1, 0, 0), PrePowerStudyRecipe(64, 13, 7)]
)
def test_centered_fields_match_saved_coordinates_and_preserve_statistics(recipe, sampling, policy):
    try:
        corner = sample_field(recipe, 8, sampling, m_selection=policy)
    except PeriodTargetError:
        with pytest.raises(PeriodTargetError):
            sample_field(recipe, 8, sampling, m_selection=policy, centered=True)
        return
    field = sample_field(recipe, 8, sampling, m_selection=policy, centered=True)
    row_offset = 1 if sampling == "checkerboard_opposite" else 0
    assert field.spec == {
        **corner.spec,
        "origin": [-4, -4 + row_offset],
        "color_anchor": int(field.result.values[4, 4]),
    }
    assert np.array_equal(field.result.values, evaluate(field.spec).values)
    assert np.array_equal(field.result.values, np.roll(corner.result.values, (4 - row_offset, 4), axis=(0, 1)))
    assert field.zero_fraction == corner.zero_fraction
    assert field.repeat_shape == corner.repeat_shape
    assert field.distinct_values == corner.distinct_values


@pytest.mark.parametrize(
    "sampling,nearest",
    [
        ("full", (0, 0)),
        ("checkerboard_same", (0, 0)),
        ("checkerboard_opposite", (1, 0)),
        ("doubled_checkerboard_opposite", (1, 0)),
        ("even_even", (0, 0)),
        ("even_odd", (0, 1)),
        ("odd_even", (1, 0)),
        ("odd_odd", (1, 1)),
    ],
)
def test_centered_sampling_places_original_origin_near_middle(sampling, nearest):
    origin = (-4, -3) if sampling == "checkerboard_opposite" else (-4, -4)
    x, y = coordinates((8, 8), sampling, origin, checkerboard_axis="vertical")
    assert (x[4, 4], y[4, 4]) == nearest
    full_side = 8 if sampling in ("full", "doubled_checkerboard_opposite") else 16
    assert x.min() >= -full_side // 2
    assert y.min() >= -full_side // 2
    # Doubling may read the next periodic neighbour at the right boundary.
    assert (
        x.max() <= full_side // 2
        if sampling in ("doubled_checkerboard_opposite", "checkerboard_opposite")
        else x.max() < full_side // 2
    )
    assert y.max() < full_side // 2
    for additional in SAMPLINGS:
        sx, sy = resample_view(x, additional), resample_view(y, additional)
        distance = sx * sx + sy * sy
        center = distance.shape[0] // 2
        nearby = distance[max(0, center - 1) : center + 2, max(0, center - 1) : center + 2]
        assert nearby.min() == distance.min()


@pytest.mark.parametrize("size", [8, 32, 128])
def test_centered_opposite_checkerboards_align_center_values_and_colors(size, tmp_path):
    recipe = PrePowerStudyRecipe(2, 0, 0, "xor")
    checker, doubled = (
        sample_field(recipe, size, sampling, centered=True)
        for sampling in ("checkerboard_opposite", "doubled_checkerboard_opposite")
    )
    values = checker.result.values
    assert np.array_equal(values, values[::-1])
    assert np.array_equal(values, values[:, ::-1])
    center = slice(size // 2 - 1, size // 2 + 1)
    assert np.array_equal(values[center, center], doubled.result.values[center, center])
    assert checker.spec["color_anchor"] == doubled.spec["color_anchor"] == 1
    palettes = []
    for field in (checker, doubled):
        palette = indexed_order_palette(field.values, field.spec["color"], anchor=field.spec["color_anchor"])
        colors = palette[field.values.indices][..., :3]
        palettes.append(colors[center, center])
        path = tmp_path / (field.spec["sampling"] + ".png")
        export(evaluate(field.spec), path, mode="order")
        with Image.open(path) as image:
            assert np.array_equal(np.asarray(image), colors)
    assert np.array_equal(*palettes)
