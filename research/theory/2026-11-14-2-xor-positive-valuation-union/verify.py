"""Bounded exact verification for the positive-valuation union theorem."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random

from union_sampler import UnionSampler, conditional_unrank, coordinates, tail_start

checks = 0


def require(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def invariant(recipe):
    q = recipe.domain // 4
    step = 1 << (recipe.valuation + 2)
    value = ((recipe.value(25) - 2 * recipe.value(5)) % recipe.modulus) // step
    depth = (value & -value).bit_length() - 1 if value else q.bit_length() - 1
    require(depth == min(recipe.valuation + 2, q.bit_length() - 1), "curvature valuation")
    require(recipe.value(5) // step % 2 == 1, "unit first increment")


def exhaustive(samplers):
    coverage = []
    for C in (8, 16, 32, 64, 128, 256):
        sampler = samplers[C]
        seen = set()
        for v, space in enumerate(sampler.rows, 1):
            base, switches = coordinates.binary_recipe(space)
            expected = set()
            for bits in range(1 << len(switches)):
                values = list(base)
                for j, switch in enumerate(switches):
                    if bits >> j & 1:
                        values = [(a + b) % space["modulus"] for a, b in zip(values, switch)]
                expected.add(tuple(x // (1 << (v + 2)) for x in values))
            start = sampler.ends[v - 2] if v > 1 else 0
            actual = set()
            for rank in range(start, sampler.ends[v - 1]):
                recipe = sampler.unrank(rank)
                table = recipe.normalized_table()
                invariant(recipe)
                require(set(table) == set(range(C // 4)), "complete value grid")
                require(all(table[i] == table[C // 2 - 1 - i] for i in range(C // 2)), "complement pairs")
                require(all((recipe.value(z + C // 2) - recipe.value(z)) % recipe.modulus == recipe.modulus // 2
                            for z in range(1, C // 2, 2)), "period and minimum precision")
                actual.add(table)
            require(actual == expected, "global unrank covers the independent conditional controls")
            require(not actual & seen, "distinct productive valuations")
            seen.update(actual)
        require(len(seen) == sampler.count, "one global rank per class")
        coverage.append({"C": C, "exhaustive_union_classes": len(seen)})
    return coverage


def affine_kernel(C, v, space):
    q, step = C // 4, 1 << (v + 2)
    generators = [[x // step for x in column] for column in space["generators"]]
    active = min((j for j, flag in enumerate(space["character"]) if flag), key=lambda j: space["bits"][j])
    base = generators[active]
    kernel = [[2 * x % q for x in base]]
    kernel += [[(x - flag * y) % q for x, y in zip(column, base)]
               for j, (column, flag) in enumerate(zip(generators, space["character"])) if j != active]
    return base, kernel


def overlap_checks(samplers):
    pairs = 0
    for C in (8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096):
        sampler = samplers[C]
        rows = list(sampler.rows) + [coordinates.same_v_space(C, sampler.tail + 1)]
        for i, j in combinations(range(len(rows)), 2):
            a, A = affine_kernel(C, i + 1, rows[i])
            b, B = affine_kernel(C, j + 1, rows[j])
            combined = sum(coordinates.image_coordinates(A + B, C // 4)["bits"])
            enlarged = sum(coordinates.image_coordinates(A + B + [[(x - y) % (C // 4) for x, y in zip(a, b)]], C // 4)["bits"])
            intersects = combined == enlarged
            require(intersects == (i + 1 >= sampler.tail), "independent affine-module intersection test")
            if intersects:
                size_bits = rows[i]["valid_bits"] + rows[j]["valid_bits"] - combined
                require(size_bits == rows[i]["valid_bits"] == rows[j]["valid_bits"], "equal complete tail sets")
            pairs += 1
    return pairs


def sampled_checks(samplers):
    rng = Random(20261114)
    draws = 0
    for C, sampler in samplers.items():
        for v, space in enumerate(sampler.rows, 1):
            for _ in range(8):
                recipe = conditional_unrank(C, v, space, rng.randrange(space["valid_shift_classes"]))
                invariant(recipe)
                for _ in range(8):
                    z = 2 * rng.randrange(C // 4) + 1
                    difference = (recipe.value(z + C // 2) - recipe.value(z)) % recipe.modulus
                    require(difference == recipe.modulus // 2, "seeded half-period difference")
                draws += 1
        # Independent, arbitrary odd coefficient sums, rather than only
        # polynomials decoded from the coordinate recipe.
        for v in range(1, sampler.tail + 2):
            for _ in range(8):
                exponents = [((2 * rng.randrange(8) + 1) << v) for _ in range(5)]
                coefficients = [rng.randrange(-16, 17) for _ in exponents]
                coefficients[0] += (1 - sum(coefficients)) % 2
                M = C << v
                values = [sum(a * (pow(z, p, M) - 1) for a, p in zip(coefficients, exponents)) % M for z in (5, 25)]
                difference = (values[1] - 2 * values[0]) % M
                depth = ((difference & -difference).bit_length() - 1 - (v + 2)) if difference else C.bit_length() - 3
                require(depth == min(v + 2, C.bit_length() - 3), "arbitrary odd-sum coefficient curvature")
        # All positive valuations above the cutoff represent the same set;
        # verify their cyclic generator against the exact discrete-log table.
        q = C // 4
        logs = {}
        value = 1
        for j in range(q):
            logs[value] = logs[-value % C] = j
            value = value * 5 % C
        for v in (sampler.tail, sampler.tail + 1, sampler.tail + 7):
            M = C << v
            step = 1 << (v + 2)
            eta = ((pow(5, 1 << v, M) - 1) % M) // step
            require(eta % 2 == 1, "tail unit")
            for z in range(1, C, 2):
                value = ((pow(z, 1 << v, M) - 1) % M) // step
                require(value == eta * logs[z] % q, "pointwise logarithmic tail formula")
    return draws


def native_checks():
    from ruglab.diagnostics import periods, signature
    from ruglab.engine import evaluate
    from ruglab.post_polynomials import draw_post_polynomial, xor_valuation_tail

    rng, fields, gallery = Random(14), 0, 0
    for C in (8, 16, 32, 64, 128, 256):
        sampler = UnionSampler(C)
        require(xor_valuation_tail(C) == sampler.tail, "dedicated gallery tail cutoff")
        for v, space in enumerate(sampler.rows, 1):
            for _ in range(3):
                recipe = conditional_unrank(C, v, space, rng.randrange(space["valid_shift_classes"]))
                common = {"n": C, "shape": [C // 2] * 2, "K": C, "M": recipe.modulus,
                          "sampling": "checkerboard_opposite", "pre": [], "combine": "xor",
                          "post": [["poly", recipe.polynomial()]]}
                for axis in ("horizontal", "vertical"):
                    result = evaluate({**common, "checkerboard_axis": axis})
                    require(all(int(value) == recipe.value(int(z)) for value, z in zip(result.values.flat, result.stages["z0"].flat)), "native factored/expanded evaluation")
                    require(periods(result, certified_torus=True) == (C // 2, C // 2), "native least axis periods")
                    reduced = evaluate({**common, "checkerboard_axis": axis, "M": recipe.modulus // 2})
                    require(all(period <= C // 4 for period in periods(reduced, certified_torus=True)), "native loss of target period at half precision")
                    numeric = signature(result, "shift")
                    require(numeric[1] == C // 4 and numeric[2] == signature(result, "order")[1], "native shift/order equivalence")
                    fields += 1
                polynomial, modulus = draw_post_polynomial(C, "even sum", v, 14, gallery)
                values = [sum(coefficient * pow(z, degree, modulus) for degree, coefficient in enumerate(polynomial)) % modulus
                          for z in (1, 5, 25)]
                difference = (values[2] - 2 * values[1] + values[0]) % modulus
                depth = ((difference & -difference).bit_length() - 1 - (v + 2)) if difference else C.bit_length() - 3
                require(depth == min(v + 2, C.bit_length() - 3), "existing gallery curvature")
                gallery += 1
    return {"native_fields": fields, "existing_gallery_draws": gallery, "axes": ["horizontal", "vertical"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", action="store_true", help="also use the optional research workbench")
    args = parser.parse_args()
    samplers = {1 << c: UnionSampler(1 << c) for c in range(3, 17)}
    rows = [sampler.summary() for sampler in samplers.values()]
    for row in rows:
        row["ratio_to_single_powers"] = str(Fraction(row["union_classes"], row["single_power_union_classes"]))
    coverage = {"exhaustive": exhaustive(samplers), "affine_intersection_pairs": overlap_checks(samplers),
                "seeded_conditional_draws": sampled_checks(samplers), "coefficient_sum_examples_per_row": 8}
    if args.native:
        coverage["native"] = native_checks()
    sampler = samplers[4096]
    example = asdict(sampler.draw(Random(0)))
    hashes = {str(path.relative_to(Path(__file__).resolve().parents[3])): sha256(path.read_bytes()).hexdigest()
              for path in (Path(__file__), Path(__file__).with_name("union_sampler.py"),
                           Path(coordinates.__file__))}
    result = {"scope": "positive exponent valuations; odd sum of nonconstant coefficients; no-pre XOR",
              "coverage": coverage, "checks": checks, "counts": rows, "example": example, "source_sha256": hashes}
    Path(__file__).with_name("results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": checks, "coverage": coverage, "counts": rows}, indent=2))


if __name__ == "__main__":
    main()
