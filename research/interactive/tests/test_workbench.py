from pathlib import Path

import json5
import numpy as np
import pytest
from ruglab import Sweep, dsl, evaluate, gallery, paired
from ruglab.diagnostics import periods, signature
from ruglab.operations import clmul
from ruglab.research import family_pre_modulus, minimum_post_modulus, uniform_xor
from ruglab.sampling import coordinates


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
            a, b = pow(y - x - 1, 2, 32), pow(y + x, 2, 32)
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
    x, y = coordinates((8, 8), "checkerboard_opposite")
    assert set(((x + y) % 2).flat) == {1}
    s = {"n": 32, "K": 32, "M": 64, "post": [["pow", 2]]}
    assert np.array_equal(
        evaluate({**s, "sampling": "checkerboard_same"}).values,
        evaluate({**s, "sampling": "checkerboard_opposite"}).values,
    )


def test_large_powers_and_moduli():
    p = 2**40 + 6
    M = 2**100
    r = evaluate({"n": 8, "K": 8, "M": M, "post": [["pow", p], ["mult", 2**70 + 1]]})
    assert int(r.values[1, 3]) == pow(((1 - 3 - 1) % 8) ^ ((1 + 3) % 8), p, M) * (2**70 + 1) % M
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
            a = (1 + 3 * (y - x - 1) ** 2) % 16
            b = (1 + 3 * (y + x) ** 2) % 16
            assert r.values[y, x] == ((a ^ b) + abs(a - b) ** 3) % 64


@pytest.mark.parametrize("name,arg", [("gray", 1), ("bitrev", 1), ("rotl", 3), ("inv", 1)])
def test_bit_operations(name, arg):
    r = evaluate({"n": 16, "K": 16, "M": 16, "coordinates": "straight", "pre": [[name, arg]]})
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
    assert family_pre_modulus(8, 512, "and") == 16384
    s = {"n": 64, "K": 64, "M": 64, "pre": [["pow", 2]], "combine": "and"}
    r = evaluate(s)
    assert periods(r, certified_torus=True) == (32, 32)
    assert minimum_post_modulus(s, 32, 2) == 2048
    with pytest.raises(ValueError, match="known complete periodic torus"):
        periods(r)
    with pytest.raises(ValueError, match="exceeds max_cells"):
        minimum_post_modulus({**s, "K": 1024}, 32)


def test_signatures_and_gallery(tmp_path):
    a = evaluate({"n": 8, "M": 32, "coordinates": "straight", "expression": "4*z"})
    b = evaluate({"n": 8, "M": 64, "coordinates": "straight", "expression": "8*z"})
    assert signature(a) == signature(b)
    p = tmp_path / "favorites.json"
    gallery.save(p, "one", {"n": 8}, notes="interesting", seed=2)
    saved = gallery.load(p, "interesting")["one"]
    assert saved["seed"] == 2 and saved["spec"]["M"] == 8


def test_seed_is_local_and_repeatable():
    assert uniform_xor(64, 3) == uniform_xor(64, 3)
    assert uniform_xor(64, 3)["post"][1][1] % 2 == 1


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
            "coordinates": "straight",
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
