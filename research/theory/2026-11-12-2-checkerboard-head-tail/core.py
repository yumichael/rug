"""Exact compressed checkerboard models; arbitrary integer twists and posts."""

from collections import Counter
from dataclasses import dataclass
from functools import cached_property
from math import inf

import numpy as np


def nu(value):
    value = abs(int(value))
    return (value & -value).bit_length() - 1 if value else inf


def poly(coefficients, x, modulus=None):
    value = 0
    for coefficient in reversed(coefficients):
        value = value * x + coefficient
        if modulus:
            value %= modulus
    return value


def twist_degree_bound(N, q):
    k = N.bit_length() - 1 + int(nu(q))
    a = max(0, (k + q - 2) // q - 1)
    h = int(nu(q)) + 2
    b = max(0, (k + h - 2) // h - 1)
    return a, b


def pre_values(N, q, Q=()):
    K = N * (q & -q)
    values = []
    for x in range(N):
        t = pow(x, q, K)
        values.append((t + 2 * t * (t - 1) * poly(Q, t, K)) % K)
    return tuple(values)


def reduced_twist(N, q, Q):
    """Divide Q by t**a (t-1)**b, using its monic integer coefficients."""
    a, b = twist_degree_bound(N, q)
    divisor = [0] * a + [1]
    for _ in range(b):
        new = [0] * (len(divisor) + 1)
        for i, c in enumerate(divisor):
            new[i] -= c
            new[i + 1] += c
        divisor = new
    remainder = list(Q)
    while len(remainder) >= len(divisor):
        c = remainder[-1]
        start = len(remainder) - len(divisor)
        for j, d in enumerate(divisor):
            remainder[start + j] -= c * d
        remainder.pop()
    return tuple(remainder)


def combine(c, a, b):
    if c == 'or':
        return a | b
    if c == 'xor':
        return a ^ b
    if c == 'add':
        return a + b
    if c == 'absdiff':
        return abs(a - b)
    raise ValueError(c)


@dataclass
class Basic:
    N: int
    q: int
    Q: tuple
    combiner: str

    @cached_property
    def K(self):
        return self.N * (self.q & -self.q)

    @cached_property
    def pre(self):
        return pre_values(self.N, self.q, self.Q)

    @cached_property
    def nodes_edges(self):
        odd = sorted(set(self.pre[1::2]))
        even = sorted(set(self.pre[::2]))
        edges = set()
        for o in odd:
            partner = o ^ (self.K // 2)
            for e in even:
                z = combine(self.combiner, o, e)
                t = combine(self.combiner, partner, e)
                edges.add((min(z, t), max(z, t)))
        nodes = tuple(sorted({v for edge in edges for v in edge}))
        index = {v: i for i, v in enumerate(nodes)}
        return nodes, tuple(sorted((index[a], index[b]) for a, b in edges))

    @property
    def nodes(self):
        return self.nodes_edges[0]

    @property
    def edges(self):
        return self.nodes_edges[1]

    @cached_property
    def components(self):
        parent = list(range(len(self.nodes)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for a, b in self.edges:
            parent[find(a)] = find(b)
        groups = {}
        for i in range(len(parent)):
            groups.setdefault(find(i), []).append(i)
        return tuple(tuple(g) for g in groups.values())

    @cached_property
    def anchor(self):
        return self.nodes.index(combine(self.combiner, self.pre[0], self.pre[-1]))

    @cached_property
    def indices(self):
        """Materialize only when a displayed tile or union membership is needed."""
        j, i = np.indices((self.N, self.N))
        pre = np.array(self.pre, dtype=np.int64)
        a, b = pre[(i + j) % self.N], pre[(j - i - 1) % self.N]
        if self.combiner == 'or':
            z = a | b
        elif self.combiner == 'xor':
            z = a ^ b
        elif self.combiner == 'add':
            z = a + b
        else:
            z = abs(a - b)
        return np.searchsorted(self.nodes, z)

    def full(self, values):
        return any(values[a] != values[b] for a, b in self.edges)

    def summary(self):
        return {'nodes': len(self.nodes), 'components': dict(sorted(Counter(map(len, self.components)).items()))}


def moduli(basic, H):
    """Selectors on integer outputs, including polynomial collisions and constants."""
    outputs = [poly(H, z) for z in basic.nodes]
    distinct = sorted(set(outputs))
    depth = min((nu(outputs[a] - outputs[b]) for a, b in basic.edges), default=inf)
    low, high = 0, (distinct[-1] - distinct[0]).bit_length()
    while low < high:
        middle = (low + high) // 2
        if len({v % (1 << middle) for v in distinct}) == len(distinct):
            high = middle
        else:
            low = middle + 1
    separation = low - 1
    zero = max((nu(v) for v in distinct if v), default=-1)
    return {
        'catalogue': 1 << int(1 + max(separation, zero)),
        'distinct_outputs': 1 << int(1 + separation),
        'minimum_period': None if depth == inf else 1 << int(1 + depth),
    }


def anchored(values, modulus, anchor=0):
    return tuple((int(v) - int(values[anchor])) % modulus for v in values)


def ranks(values, modulus, anchor=0):
    values = anchored(values, modulus, anchor)
    lookup = {v: i for i, v in enumerate(sorted(set(values)))}
    return tuple(lookup[v] for v in values)


def shift_key(values, modulus, anchor=0):
    values = anchored(values, modulus, anchor)
    depth = min((nu(v) for v in values if v), default=modulus.bit_length() - 1)
    divisor = 1 << int(depth)
    return modulus // divisor, tuple(v // divisor for v in values)


def canonical_twists_64(q):
    """Complete pre-function representatives, not a degree/size-limited sample."""
    if q == 2:
        return tuple((C, 0, B - C) for B in range(8) for C in range(16))
    if q == 4:
        return tuple((A, B - A) for A in range(8) for B in range(8))
    if q in (6, 8):
        return tuple((B,) for B in range(8))
    raise ValueError(q)


def diagonalize(columns, modulus):
    """Dyadic elimination, retaining the full invertible column transform.

    Adapted from ../2026-11-02-xor-polynomial-period/xor_polynomial_period.py.
    """
    n = len(columns)
    if not n:
        return [], []
    matrix = [[v % modulus for v in row] for row in zip(*columns)]
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
            matrix[i] = [(a - factor * b) % modulus for a, b in zip(matrix[i], matrix[k])]
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
    generators = [tuple(sum(columns[k][i] * transform[k][j] for k in range(len(columns))) % modulus
                        for i in range(len(columns[0]))) for j in range(len(bits))]
    return bits, generators


def twist_space(N, q):
    """Independent coordinates for every shared-family pre-function at this K."""
    K = N * (q & -q)
    D = sum(twist_degree_bound(N, q))
    inputs = [pow(x, q, K) for x in range(N)]
    columns = [tuple(2 * t * (t - 1) * pow(t, j, K) % K for t in inputs) for j in range(D)]
    bits, transform = diagonalize(columns, K)
    return bits, transform


class ShiftSampler:
    """Uniform distinct numerical tables at fixed M, optionally at minimum precision."""

    def __init__(self, basic, modulus, minimum=True):
        self.basic, self.modulus = basic, modulus
        n = len(basic.nodes)
        columns = [tuple((pow(z, j, modulus) - pow(basic.nodes[basic.anchor], j, modulus)) % modulus
                         for z in basic.nodes) for j in range(1, n)]
        if minimum and columns:
            constraints = [tuple(2 * (g[a] - g[b]) % modulus for a, b in basic.edges) for g in columns]
            bits, transform = diagonalize(constraints, modulus)
            columns = [tuple(sum(columns[k][i] * transform[k][j] for k in range(len(columns)))
                             * (1 << bits[j] if j < len(bits) else 1) % modulus for i in range(n))
                       for j in range(len(columns))]
        self.bits, self.generators = image(columns, modulus)
        differences = [tuple((g[a] - g[b]) % modulus for a, b in basic.edges) for g in self.generators]
        edge_bits = sum(image(differences, modulus)[0])
        self.total_bits = sum(self.bits)
        self.total = (1 << self.total_bits) - (1 << (self.total_bits - edge_bits))

    def draw(self, rng):
        if not self.total:
            raise ValueError('No full-period polynomial tables at this precision')
        while True:
            coefficients = [rng.randrange(1 << b) for b in self.bits]
            result = tuple(sum(a * g[i] for a, g in zip(coefficients, self.generators)) % self.modulus
                           for i in range(len(self.basic.nodes)))
            if self.basic.full(result):
                return result
