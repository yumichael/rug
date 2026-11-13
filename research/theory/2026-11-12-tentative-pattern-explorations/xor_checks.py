"""Exact checks for the no-pre XOR complement-symmetry theorem.

Run with research/interactive/.venv/bin/python from the Rug checkout.
The general claims rest on the accompanying proofs, not this finite sample.
"""

from math import comb, inf

from ruglab.diagnostics import periods
from ruglab.engine import evaluate
from ruglab.post_polynomials import draw_post_polynomial


def value(coefficients, z):
    result = 0
    for coefficient in reversed(coefficients):
        result = result * z + coefficient
    return result


def valuation(z):
    return (abs(z) & -abs(z)).bit_length() - 1 if z else inf


def classify(coefficients, side):
    width = 2 * side
    odd_inputs = range(1, width, 2)
    half_differences = {z: value(coefficients, z + side) - value(coefficients, z) for z in range(1, side, 2)}
    depths = [
        min(valuation(delta) for z, delta in half_differences.items() if (z < side // 2) == lower)
        for lower in [True, False]
    ]
    symmetry_depth = min(valuation(value(coefficients, width - z) - value(coefficients, z)) for z in odd_inputs)
    minimum_exponent = 1 + max(depths)
    return minimum_exponent, symmetry_depth


def symmetric_representative(coefficients, side):
    # H(N+x) = A(x^2) + x B(x^2). On symmetric odd-input tables,
    # x B(x^2) = B(x^2) modulo M. Substitute x^2=N^2-z(2N-z).
    centered = [
        sum(coefficients[j] * comb(j, k) * side ** (j - k) for j in range(k, len(coefficients)))
        for k in range(len(coefficients))
    ]
    square_poly = [
        centered[2 * i] + (centered[2 * i + 1] if 2 * i + 1 < len(centered) else 0)
        for i in range((len(centered) + 1) // 2)
    ]
    return [
        (-1) ** k * sum(square_poly[j] * comb(j, k) * side ** (2 * (j - k)) for j in range(k, len(square_poly)))
        for k in range(len(square_poly))
    ]


def run_checks():
    counterexample = (0, 0, 11, 0, 25, 0, 1)
    m, symmetry_depth = classify(counterexample, 8)
    assert (m, symmetry_depth) == (12, 11)
    for modulus, expected in [(2048, (4, 4)), (4096, (8, 8))]:
        spec = {
            'n': 8,
            'K': 16,
            'M': modulus,
            'pre': [],
            'post': [['poly', counterexample]],
            'combine': 'xor',
            'sampling': 'checkerboard_opposite',
            'checkerboard_axis': 'vertical',
        }
        assert periods(evaluate(spec), certified_torus=True) == expected
    assert value(counterexample, 1) % 4096 == 37
    assert value(counterexample, 15) % 4096 == 2085

    counts = {'polynomials': 0, 'low_precision_cases': 0, 'nonsymmetric_minima': 0, 'equivalent_representatives': 0}
    for side in [4, 8, 16, 32]:
        width = 2 * side
        for precision in [1, 2, 4, 8, 16, 32]:
            for draw in range(100):
                coefficients, _ = draw_post_polynomial(width, 'even only', precision, 1, draw)
                m, symmetry_depth = classify(coefficients, side)
                assert m != inf
                modulus = 1 << int(m)
                counts['polynomials'] += 1
                if modulus <= 2 * side * side:
                    counts['low_precision_cases'] += 1
                    assert symmetry_depth >= m
                if symmetry_depth < m:
                    counts['nonsymmetric_minima'] += 1
                else:
                    representative = symmetric_representative(coefficients, side)
                    assert all(
                        (value(coefficients, z) - value(representative, z * (width - z))) % modulus == 0
                        for z in range(1, width, 2)
                    )
                    counts['equivalent_representatives'] += 1
    return counts


if __name__ == "__main__":
    print(run_checks())
