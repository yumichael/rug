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
