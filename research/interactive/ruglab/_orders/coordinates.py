"""Finite dyadic twist coordinates from the November 12 research."""

from .core import nu, twist_degree_bound


def diagonalize(columns, modulus):
    """Dyadic elimination, retaining the full invertible column transform.

    Adapted from ../2026-11-02-xor-polynomial-period/xor_polynomial_period.py.
    """
    n = len(columns)
    if not n:
        return [], []
    matrix = [[v % modulus for v in row] for row in zip(*columns, strict=True)]
    transform = [[int(i == j) for j in range(n)] for i in range(n)]
    bits = []
    for k in range(min(len(matrix), n)):
        candidates = [(nu(matrix[i][j]), i, j) for i in range(k, len(matrix)) for j in range(k, n) if matrix[i][j]]
        if not candidates:
            break
        depth, i, j = min(candidates)
        matrix[k], matrix[i] = matrix[i], matrix[k]
        for row in matrix:
            row[k], row[j] = row[j], row[k]
        for row in transform:
            row[k], row[j] = row[j], row[k]
        inverse = pow(matrix[k][k] >> depth, -1, modulus)
        for row in matrix:
            row[k] = row[k] * inverse % modulus
        for row in transform:
            row[k] = row[k] * inverse % modulus
        for i in range(k + 1, len(matrix)):
            factor = matrix[i][k] >> depth
            matrix[i] = [(a - factor * b) % modulus for a, b in zip(matrix[i], matrix[k], strict=True)]
        for j in range(k + 1, n):
            factor = matrix[k][j] >> depth
            for row in matrix:
                row[j] = (row[j] - factor * row[k]) % modulus
            for row in transform:
                row[j] = (row[j] - factor * row[k]) % modulus
        bits.append(modulus.bit_length() - 1 - int(depth))
    return bits, transform


def image(columns, modulus):
    bits, transform = diagonalize(columns, modulus)
    generators = [
        tuple(
            sum(columns[k][i] * transform[k][j] for k in range(len(columns))) % modulus for i in range(len(columns[0]))
        )
        for j in range(len(bits))
    ]
    return bits, generators


def twist_space(N, q):
    """Independent coordinates for every shared-family pre-function at this K."""
    K = N * (q & -q)
    D = sum(twist_degree_bound(N, q))
    inputs = [pow(x, q, K) for x in range(N)]
    columns = [tuple(2 * t * (t - 1) * pow(t, j, K) % K for t in inputs) for j in range(D)]
    bits, transform = diagonalize(columns, K)
    return bits, transform
