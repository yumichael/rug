"""Construct a polynomial representative at minimum-period precision and verify it."""

from math import prod
from random import Random

import numpy as np
from ruglab.diagnostics import periods
from ruglab.engine import evaluate
from sampler import Sampler


def nu(x):
    return (abs(x) & -abs(x)).bit_length() - 1 if x else float('inf')


def target_labels(structure, p, anchor=0):
    need = sum(1 + max(len(P), len(Q)) for A, B, P, Q in structure)
    L = 1 << (need - 1).bit_length()
    labels = [None] * (2 * p)
    base = 0
    for A, B, P, Q in structure:
        for node in A:
            labels[node] = base
        for node in B:
            labels[node] = base + L
        for offset, group in enumerate(P, 1):
            for node in group:
                labels[node] = base + offset
        for offset, group in enumerate(Q, 1):
            for node in group:
                labels[node] = base + offset + L
        base += 1 + max(len(P), len(Q))
    phase = labels[anchor]
    labels = [(v - phase) % (2 * L) for v in labels]
    return labels, 2 * L


def polynomial(nodes, labels, modulus, d):
    coefficients = [0] * len(nodes)
    for i, t in enumerate(nodes):
        D = prod(t - u for j, u in enumerate(nodes) if j != i)
        depth = nu(D)
        poly = [1]
        for j, u in enumerate(nodes):
            if j == i:
                continue
            new = [0] * (len(poly) + 1)
            for k, a in enumerate(poly):
                new[k] -= u * a
                new[k + 1] += a
            poly = new
        scale = (1 << (d - depth)) * pow(D // (1 << depth), -1, modulus) * labels[i]
        for k, a in enumerate(poly):
            coefficients[k] = (coefficients[k] + scale * a) % modulus
    return coefficients


def realize(N, rank, structure, anchor=0):
    p = N // 4
    labels, denominator = target_labels(structure, p, anchor)
    assert tuple({v: i for i, v in enumerate(sorted(set(labels)))}[v] for v in labels) == rank
    xs = [x for i in range(p) for x in (2 * i + 1, N - 2 * i - 1)]
    nodes = [x * x for x in xs]
    d = max(nu(prod(t - u for j, u in enumerate(nodes) if j != i)) for i, t in enumerate(nodes))
    M = (1 << d) * denominator
    G = polynomial(nodes, labels, M, d)
    # Compose G((z-N)^2), preserving integer coefficients.
    H = [0]
    for c in reversed(G):
        new = [0] * (len(H) + 2)
        for i, a in enumerate(H):
            new[i] += N * N * a
            new[i + 1] -= 2 * N * a
            new[i + 2] += a
        new[0] += c
        H = [v % M for v in new]
    spec = {
        'n': N,
        'K': 2 * N,
        'M': M,
        'pre': [],
        'post': [['poly', H]],
        'combine': 'xor',
        'sampling': 'checkerboard_opposite',
        'checkerboard_axis': 'vertical',
    }
    out = evaluate(spec)
    lower = evaluate({**spec, 'M': M // 2})
    assert periods(out, certified_torus=True) == (N, N)
    assert periods(lower, certified_torus=True) != (N, N)
    # Compare exact desired label lookup to every native output cell.
    j, i = np.indices((N, N))
    z = ((i + j) % (2 * N)) ^ ((j - i - 1) % (2 * N))
    x = abs(z - N)
    node = np.where(x < N // 2, x - 1, N - x)  # low x=2i+1 -> node2i=x-1; high x -> node2i+1=N-x.
    expected = np.array(labels, dtype=object)[node] * (1 << d)
    assert np.array_equal(out.values, expected)
    return M


if __name__ == '__main__':
    rng = Random(0)
    for N in [4, 8, 16, 32]:
        s = Sampler(N // 4)
        bits = []
        for _ in range(25):
            rank, structure = s.draw(rng)
            M = realize(N, rank, structure)
            bits.append(M.bit_length() - 1)
        print(
            'N',
            N,
            '25 complete pattern realizations match native evaluator; minimum modulus exponent range',
            min(bits),
            max(bits),
        )
