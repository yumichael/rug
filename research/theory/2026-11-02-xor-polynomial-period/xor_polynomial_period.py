#!/usr/bin/env python3
"""Exact, standard-library checks and coordinates for the companion report."""

from __future__ import annotations

import itertools
import json
import math
import random
from pathlib import Path


def valuation(n: int) -> int:
    assert n != 0
    return (n & -n).bit_length() - 1


def image_coordinates(columns: list[list[int]], modulus: int) -> dict:
    """Diagonalize over Z/(2**m), retaining polynomial column combinations.

    Row operations are invertible changes of output coordinates. Column
    operations are retained in `transform`; evaluating original columns with
    its j-th column recovers the j-th independent output generator.
    """
    assert modulus >= 2 and modulus & (modulus - 1) == 0
    if not columns:
        return {"bits": [], "transform": [], "generators": []}
    matrix = [list(row) for row in zip(*columns)]
    row_count, column_count = len(matrix), len(columns)
    transform = [[int(i == j) for j in range(column_count)]
                 for i in range(column_count)]
    bits = []
    for k in range(min(row_count, column_count)):
        candidates = [(valuation(matrix[i][j]), i, j)
                      for i in range(k, row_count)
                      for j in range(k, column_count) if matrix[i][j]]
        if not candidates:
            break
        depth, i, j = min(candidates)
        matrix[k], matrix[i] = matrix[i], matrix[k]
        for row in matrix:
            row[k], row[j] = row[j], row[k]
        for row in transform:
            row[k], row[j] = row[j], row[k]
        unit_inverse = pow(matrix[k][k] >> depth, -1, modulus)
        for row in matrix:
            row[k] = row[k] * unit_inverse % modulus
        for row in transform:
            row[k] = row[k] * unit_inverse % modulus
        for i in range(k + 1, row_count):
            quotient = matrix[i][k] >> depth
            matrix[i] = [(a - quotient * b) % modulus
                         for a, b in zip(matrix[i], matrix[k])]
        for j in range(k + 1, column_count):
            quotient = matrix[k][j] >> depth
            for row in matrix:
                row[j] = (row[j] - quotient * row[k]) % modulus
            for row in transform:
                row[j] = (row[j] - quotient * row[k]) % modulus
        bits.append(modulus.bit_length() - 1 - depth)
    rank = len(bits)
    transform = [row[:rank] for row in transform]
    generators = [
        [sum(columns[k][i] * transform[k][j] for k in range(column_count))
         % modulus for i in range(row_count)]
        for j in range(rank)
    ]
    return {"bits": bits, "transform": transform, "generators": generators}


def same_v_columns(C: int, v: int) -> tuple[int, list[list[int]]]:
    """Short polynomial spanning list; all columns anchored at z=1."""
    assert C >= 8 and C & (C - 1) == 0 and v >= 0
    m = C.bit_length() - 1 + v
    modulus = 1 << m
    e = 3 if v == 0 else v + 3
    columns = []
    k, factorial = 0, 1
    while e * k + valuation(factorial) < m:
        column = []
        for z in range(1, C, 2):
            w = pow(z, 1 << v, modulus)
            value = w
            for j in range(k):
                value = value * (w * w - (1 + (1 << e) * j)) % modulus
            column.append((value - int(k == 0)) % modulus)
        columns.append(column)
        k += 1
        factorial *= k
    return modulus, columns


def same_v_space(C: int, v: int) -> dict:
    modulus, columns = same_v_columns(C, v)
    result = image_coordinates(columns, modulus)
    result["modulus"] = modulus
    result["spanning_columns"] = len(columns)
    result["character"] = [row % 2 for row in result["transform"][0]]
    assert any(result["character"])
    result["valid_bits"] = sum(result["bits"]) - 1
    result["valid_shift_classes"] = 1 << result["valid_bits"]
    return result


def binary_recipe(space: dict) -> tuple[list[int], list[list[int]]]:
    """A fixed base plus independent on/off additions, all full-period."""
    modulus = space["modulus"]
    bits = space["bits"]
    generators = [g[:] for g in space["generators"]]
    character = space["character"]
    active = min((i for i, value in enumerate(character) if value),
                 key=lambda i: bits[i])
    base = generators[active][:]
    for j in range(len(generators)):
        if j != active and character[j]:
            generators[j] = [(x - y) % modulus
                             for x, y in zip(generators[j], base)]
    switches = []
    for j, generator in enumerate(generators):
        start = 1 if j == active else 0
        for bit in range(start, bits[j]):
            switches.append([(x << bit) % modulus for x in generator])
    assert len(switches) == space["valid_bits"]
    return base, switches


def odd_newton_bits(C: int, m: int) -> list[int]:
    """Independent anchored polynomial columns on the actual odd input set."""
    result = []
    factorial = 1
    for k in range(1, C // 2):
        factorial *= k
        bits = m - k - valuation(factorial)
        if bits <= 0:
            break
        result.append(bits)
    return result


def newton_value_derivative(z: int, k: int, modulus: int) -> tuple[int, int]:
    value, derivative = 1, 0
    for j in range(k):
        factor = z - (1 + 2 * j)
        derivative = (derivative * factor + value) % modulus
        value = value * factor % modulus
    return value, derivative


def arbitrary_space(C: int, v: int) -> dict:
    c = C.bit_length() - 1
    assert C >= 32 and 0 <= v <= c - 4
    m = c + v
    bits = odd_newton_bits(C, m)
    derivative_modulus = 1 << (v + 1)
    derivatives = [
        [newton_value_derivative(z, k, derivative_modulus)[1]
         for z in range(1, derivative_modulus, 2)]
        for k in range(1, len(bits) + 1)
    ]
    derivative_bits = image_coordinates(derivatives, derivative_modulus)["bits"]
    total_bits = sum(bits)
    delta = sum(derivative_bits)
    valid = ((1 << delta) - 1) << (total_bits - delta)
    return {"C": C, "v": v, "modulus": 1 << m,
            "coordinate_bits": bits, "all_shift_class_bits": total_bits,
            "derivative_coordinate_bits": derivative_bits,
            "derivative_image_bits": delta, "valid_shift_classes": valid}


def arbitrary_space_general(C: int, v: int, checker: bool = False) -> dict:
    """Exact finite-difference count, with no upper restriction on v."""
    assert C >= 8 and C & (C - 1) == 0 and v >= 0
    m = C.bit_length() - 1 + v
    M = 1 << m
    bits = odd_newton_bits(C, m)
    lower = list(range(1, C // 2, 2))
    inputs = (lower, lower) if checker else (lower[:C // 8], lower[C // 8:])
    differences = []
    for zs in inputs:
        differences.append([
            [(newton_value_derivative(z + C // 2, k, M)[0] -
              newton_value_derivative(z, k, M)[0]) % M for z in zs]
            for k in range(1, len(bits) + 1)
        ])
    joined = [a + b for a, b in zip(*differences)]
    image_bits = [sum(image_coordinates(cols, M)["bits"])
                  for cols in (*differences, joined)]
    S = sum(bits)
    x, y, both = image_bits
    valid = (1 << S) - (1 << (S - x)) - (1 << (S - y)) + (1 << (S - both))
    return {"C": C, "v": v, "checker": checker,
            "coordinate_bits": bits, "difference_image_bits": image_bits,
            "valid_shift_classes": valid}


def xor_table(C: int, checker: bool = False) -> list[list[int]]:
    R = C // 2
    if checker:
        return [[C - 1 - 2 * (x ^ y) for x in range(R)] for y in range(R)]
    return [[((y - x - 1) % C) ^ ((y + x) % C)
             for x in range(R)] for y in range(R)]


def half_shift_pairs(table: list[list[int]], horizontal: bool) -> set[tuple[int, int]]:
    R = len(table)
    return {(table[y][x], table[y if horizontal else (y + R // 2) % R]
             [(x + R // 2) % R if horizontal else x])
            for y in range(R) for x in range(R)}


def full_period(values: tuple[int, ...], pairs: tuple[set, set]) -> bool:
    return all(any(values[(a - 1) // 2] != values[(b - 1) // 2]
                   for a, b in axis_pairs) for axis_pairs in pairs)


def coordinate_tables(generators: list[list[int]], bits: list[int], modulus: int):
    for coefficients in itertools.product(*(range(1 << b) for b in bits)):
        yield tuple(sum(a * g[i] for a, g in zip(coefficients, generators)) % modulus
                    for i in range(len(generators[0])))


def monomial_closure(C: int, v: int) -> set[tuple[int, ...]]:
    """Independent subgroup construction from the old complete power list."""
    modulus = C << v
    size = C // 2
    group = {(0,) * size}
    for u in range(1, C // 4, 2):
        g = tuple((pow(z, (1 << v) * u, modulus) - 1) % modulus
                  for z in range(1, C, 2))
        multiples = [(0,) * size]
        current = g
        while current not in group:
            multiples.append(current)
            current = tuple((a + b) % modulus for a, b in zip(current, g))
        old = group
        group = {tuple((a + b) % modulus for a, b in zip(h, multiple))
                 for h in old for multiple in multiples}
    return group


def run_checks() -> dict:
    checks = 0
    coverage = {}

    def check(condition: bool):
        nonlocal checks
        if not condition:
            raise AssertionError(f"Check {checks + 1} failed")
        checks += 1

    pair_cache = {}
    for c in range(3, 7):
        C = 1 << c
        for checker in (False, True):
            table = xor_table(C, checker)
            pairs = tuple(half_shift_pairs(table, axis) for axis in (True, False))
            pair_cache[C, checker] = pairs
            for axis, axis_pairs in enumerate(pairs):
                predicted = {(z, z ^ (C // 2)) if checker or
                             bool(z & (C // 4)) == bool(axis) else (z, z)
                             for z in range(1, C, 2)}
                check(axis_pairs == predicted)
    coverage["literal_spatial_pair_cases"] = len(pair_cache)

    for C in (8, 16, 32, 64):
        c = C.bit_length() - 1
        for v in range(4):
            space = same_v_space(C, v)
            M = space["modulus"]
            expected = monomial_closure(C, v)
            actual = set(coordinate_tables(space["generators"], space["bits"], M))
            check(actual == expected)
            check(len(actual) == 1 << sum(space["bits"]))
            base, switches = binary_recipe(space)
            binary = set()
            for selection in itertools.product((0, 1), repeat=len(switches)):
                values = tuple((base[i] + sum(a * g[i] for a, g in
                                             zip(selection, switches))) % M
                               for i in range(C // 2))
                check(values not in binary)
                binary.add(values)
                for checker in (False, True):
                    check(full_period(values, pair_cache[C, checker]))
            check(len(binary) == space["valid_shift_classes"])
            for values in actual:
                character = values[C // 4] == M // 2
                check(values[C // 4] in (0, M // 2))
                check((values in binary) == character)
                for checker in (False, True):
                    check(full_period(values, pair_cache[C, checker]) == character)
    coverage["exhaustive_same_v_spaces"] = 16

    # Exercise the general change of cyclic coordinates when the active
    # period bit occurs in generators of different orders.
    synthetic = {"modulus": 8, "bits": [3, 1], "character": [1, 1],
                 "generators": [[1, 0], [0, 4]], "valid_bits": 3}
    base, switches = binary_recipe(synthetic)
    synthetic_values = set()
    for selection in itertools.product((0, 1), repeat=len(switches)):
        value = tuple((base[i] + sum(a*g[i] for a, g in zip(selection, switches))) % 8
                      for i in range(2))
        check((value[0] + value[1] // 4) % 2 == 1)
        synthetic_values.add(value)
    check(len(synthetic_values) == 8)

    # Independent monomial enumeration modulo eight, rather than Newton coordinates.
    C, M = 8, 8
    monomials = {tuple(sum(a * pow(z, p, M) for p, a in enumerate(coefficients)) % M
                       for z in range(1, C, 2))
                 for coefficients in itertools.product(range(M), repeat=4)}
    newton_columns = [[newton_value_derivative(z, k, M)[0]
                       for z in range(1, C, 2)] for k in range(2)]
    newton_tables = set(coordinate_tables(newton_columns, [3, 2], M))
    check(monomials == newton_tables)
    coverage["independent_monomial_coefficient_vectors"] = M ** 4

    arbitrary_cases = [(8, v) for v in range(4)] + [(16, v) for v in range(3)]
    arbitrary_cases += [(32, 0), (32, 1), (64, 0)]
    for C, v in arbitrary_cases:
        c = C.bit_length() - 1
        space = arbitrary_space_general(C, v)
        M = C << v
        bits = space["coordinate_bits"]
        columns = [[newton_value_derivative(z, k, M)[0]
                    for z in range(1, C, 2)] for k in range(1, len(bits) + 1)]
        seen = set()
        valid_counts = [0, 0]
        for coefficients in itertools.product(*(range(1 << b) for b in bits)):
            values = tuple(sum(a * g[i] for a, g in zip(coefficients, columns)) % M
                           for i in range(C // 2))
            check(values not in seen)
            seen.add(values)
            L = 1 << (v + 1)
            predicted = any(sum(a * newton_value_derivative(z, k, L)[1]
                                for k, a in enumerate(coefficients, 1)) % L
                            for z in range(1, L, 2))
            for checker in (False, True):
                actual = full_period(values, pair_cache[C, checker])
                valid_counts[int(checker)] += actual
                if C >= 32 and v <= c - 4:
                    check(actual == predicted)
        for checker in (False, True):
            expected = arbitrary_space_general(C, v, checker)["valid_shift_classes"]
            check(valid_counts[int(checker)] == expected)
        if C >= 32 and v <= c - 4:
            check(valid_counts[0] == arbitrary_space(C, v)["valid_shift_classes"])
    coverage["exhaustive_arbitrary_polynomial_spaces"] = arbitrary_cases

    rng = random.Random(20261102)
    random_cases = 0
    for c in range(5, 10):
        C = 1 << c
        for v in range(c - 3):
            M, L = C << v, 1 << (v + 1)
            for _ in range(24):
                coefficients = [rng.randrange(M) for _ in range(12)]
                def h(z):
                    return sum(a * pow(z, p, M) for p, a in enumerate(coefficients)) % M
                def derivative(z):
                    return sum(p * a * pow(z, p - 1, L)
                               for p, a in enumerate(coefficients) if p) % L
                for z in range(1, C // 2, 2):
                    check((h(z + C // 2) - h(z)) % M == C // 2 * derivative(z) % M)
                x = any(h(z) != h(z + C // 2) for z in range(1, C // 4, 2))
                y = any(h(z) != h(z + C // 2) for z in range(C // 4 + 1, C // 2, 2))
                check(x == y == any(derivative(z) for z in range(1, L, 2)))
                random_cases += 1
    coverage["seeded_arbitrary_polynomials"] = random_cases

    # Verify both explicitly displayed polynomial recipes.
    for v, expected_bits in ((0, [7, 5, 1]), (1, [6, 2])):
        check(same_v_space(256, v)["bits"] == expected_bits)
    M = 512
    explicit = [[(z*z - 1) % M for z in range(1, 256, 2)],
                [(pow(z, 6, M) - 91*z*z + 90) % M for z in range(1, 256, 2)]]
    check(image_coordinates(explicit, M)["bits"] == [6, 2])
    literal_pairs = [tuple(half_shift_pairs(xor_table(256, checker), axis)
                           for axis in (True, False)) for checker in (False, True)]
    for v, generators, bits in (
            (0, [[(z-1) % 256 for z in range(1, 256, 2)],
                 [(z*(z*z-1)) % 256 for z in range(1, 256, 2)],
                 [(z*(z*z-1)*(z*z-9)) % 256 for z in range(1, 256, 2)]], [7, 5, 1]),
            (1, explicit, [6, 2])):
        seen = set()
        valid = 0
        for values in coordinate_tables(generators, bits, 256 << v):
            check(values not in seen)
            seen.add(values)
            actual = [full_period(values, pairs) for pairs in literal_pairs]
            check(actual[0] == actual[1])
            valid += actual[0]
        check(len(seen) == 1 << sum(bits))
        check(valid == 1 << (sum(bits) - 1))
    coverage["explicit_recipe_cases"] = 2

    same_v = []
    arbitrary = []
    for C in (256, 1024, 2048, 4096):
        c = C.bit_length() - 1
        for v in range(c - 3):
            space = same_v_space(C, v)
            same_v.append({"C": C, "v": v, "modulus": space["modulus"],
                           "spanning_columns": space["spanning_columns"],
                           "coordinate_bits": space["bits"],
                           "period_character": space["character"],
                           "valid_bits": space["valid_bits"],
                           "valid_shift_classes": space["valid_shift_classes"]})
            arbitrary.append(arbitrary_space(C, v))
            if v == 0:
                expected = [c - 1]
                k = 1
                while c - 3*k - valuation(math.factorial(k)) > 0:
                    expected.append(c - 3*k - valuation(math.factorial(k)))
                    k += 1
                check(space["bits"] == expected)
            if v >= max(1, c - 5):
                check(space["bits"] == [c - 2])
    for C in (32, 64, 128):
        c = C.bit_length() - 1
        for v in range(c - 3):
            count = arbitrary_space(C, v)["valid_shift_classes"]
            for checker in (False, True):
                check(count == arbitrary_space_general(C, v, checker)["valid_shift_classes"])
    coverage["general_vs_derivative_formula_cases"] = 18
    return {"checks": checks, "coverage": coverage,
            "same_valuation": same_v, "arbitrary_polynomials": arbitrary}


if __name__ == "__main__":
    results = run_checks()
    target = Path(__file__).with_name("results.json")
    target.write_text(json.dumps(results, indent=2) + "\n")
    print(f"Passed {results['checks']:,} exact checks; wrote {target.name}.")
    print("Same-valuation exact-period shift classes:")
    for row in results["same_valuation"]:
        if row["v"] <= 4:
            print(f"  C={row['C']:4}, v={row['v']}: "
                  f"{row['valid_bits']:2} bits, {row['valid_shift_classes']:,} patterns")
    print("Arbitrary polynomial derivative-image bits by valuation:")
    for row in results["arbitrary_polynomials"]:
        if row["C"] == 4096:
            print(f"  v={row['v']}: delta={row['derivative_image_bits']}")
