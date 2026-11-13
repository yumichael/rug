"""Polynomial realization of a sampled component order at its own minimum M."""

from math import prod

from core import nu, poly


def realize(basic, structure, anchor=None):
    anchor = basic.anchor if anchor is None else anchor
    need = sum(1 + max(len(P), len(Q)) for A, B, P, Q in structure)
    L = 1 << (need - 1).bit_length()
    labels = [None] * len(basic.nodes)
    position = 0
    for A, B, P, Q in structure:
        for node in A:
            labels[node] = position
        for node in B:
            labels[node] = position + L
        for groups, start in ((P, position), (Q, position + L)):
            for offset, group in enumerate(groups, 1):
                for node in group:
                    labels[node] = start + offset
        position += 1 + max(len(P), len(Q))
    labels = [(v - labels[anchor]) % (2 * L) for v in labels]
    nodes = basic.nodes
    denominators = [prod(t - u for j, u in enumerate(nodes) if j != i) for i, t in enumerate(nodes)]
    d = int(max(map(nu, denominators)))
    M = (1 << d) * (2 * L)
    coefficients = [0] * len(nodes)
    for i, t in enumerate(nodes):
        polynomial = [1]
        for j, u in enumerate(nodes):
            if j == i:
                continue
            new = [0] * (len(polynomial) + 1)
            for k, a in enumerate(polynomial):
                new[k] -= u * a
                new[k + 1] += a
            polynomial = new
        depth = int(nu(denominators[i]))
        scale = (1 << (d - depth)) * pow(denominators[i] // (1 << depth), -1, M) * labels[i]
        coefficients = [(a + scale * b) % M for a, b in zip(coefficients, polynomial)]
    values = [poly(coefficients, z, M) for z in nodes]
    assert values == [v << d for v in labels]
    assert basic.full(values) and not basic.full([v % (M // 2) for v in values])
    return coefficients, M, values


def pre_polynomial(Q):
    coefficients = [0, 1] + [0] * len(Q)
    for j, c in enumerate(Q):
        coefficients[j + 1] -= 2 * c
        coefficients[j + 2] += 2 * c
    return coefficients
