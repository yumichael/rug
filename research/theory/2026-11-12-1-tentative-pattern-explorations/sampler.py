"""Uniform anchored order classes in the complete pseudo-square XOR family.

This is a research prototype. It samples order tables on the N/2 distinct
complement-paired XOR inputs, over all attainable minimum moduli.
"""

from math import comb
from random import Random

from count_orders import admissible, counts, enumerate_orders


def pick(rng, weighted):
    weighted = [(x, w) for x, w in weighted if w]
    total = sum(w for _, w in weighted)
    choice = rng.randrange(total)
    for x, w in weighted:
        if choice < w:
            return x
        choice -= w
    raise AssertionError


def take(rng, labels, n):
    chosen = set(rng.sample(labels, n))
    return tuple(x for x in labels if x in chosen), tuple(x for x in labels if x not in chosen)


class Sampler:
    def __init__(self, p):
        self.p = p
        self.f, self.d, self.y, self.R = counts(p)
        self.weights = [(k, self.R[p][k] // (2 * k)) for k in range(1, p + 1)]
        self.total = sum(w for _, w in self.weights)

    def same_groups(self, rng, labels):
        if not labels:
            return []
        n = len(labels)
        size = pick(rng, [(s, comb(n, s) * self.f[n - s]) for s in range(1, n + 1)])
        block, rest = take(rng, labels, size)
        group = tuple(v for label in block for v in (2 * label, 2 * label + 1))
        return [group, *self.same_groups(rng, rest)]

    def double_block(self, rng, labels):
        n = len(labels)
        core_size = pick(rng, [(a, comb(n, a) * (4**a - 2**a) * self.d[n - a]) for a in range(1, n + 1)])
        core, rest = take(rng, labels, core_size)
        first_size = pick(
            rng, [(b, comb(len(rest), b) * self.f[b] * self.f[len(rest) - b]) for b in range(len(rest) + 1)]
        )
        first, second = take(rng, rest, first_size)
        while True:
            bits = rng.getrandbits(2 * core_size)
            if any(((bits >> (2 * i)) & 1) != ((bits >> (2 * i + 1)) & 1) for i in range(core_size)):
                break
        A = []
        B = []
        for i, label in enumerate(core):
            for endpoint in [0, 1]:
                (B if (bits >> (2 * i + endpoint)) & 1 else A).append(2 * label + endpoint)
        return tuple(A), tuple(B), self.same_groups(rng, first), self.same_groups(rng, second)

    def sequence(self, rng, labels, k):
        if k == 0:
            assert not labels
            return []
        n = len(labels)
        size = pick(rng, [(s, comb(n, s) * self.y[s] * self.R[n - s][k - 1]) for s in range(1, n - k + 2)])
        block, rest = take(rng, labels, size)
        return [self.double_block(rng, block), *self.sequence(rng, rest, k - 1)]

    def draw(self, rng, anchor=0):
        k = pick(rng, self.weights)
        structure = self.sequence(rng, tuple(range(self.p)), k)
        groups = []
        for A, _B, P, _Q in structure:
            groups.extend([A, *P])
        for _A, B, _P, Q in structure:
            groups.extend([B, *Q])
        start = next(i for i, g in enumerate(groups) if anchor in g)
        groups = groups[start:] + groups[:start]
        rank = [None] * (2 * self.p)
        for i, g in enumerate(groups):
            for v in g:
                assert rank[v] is None
                rank[v] = i
        rank = tuple(rank)
        assert admissible(rank)
        return rank, structure


if __name__ == '__main__':
    from collections import Counter

    rng = Random(0)
    for p in [1, 2, 3, 4]:
        sampler = Sampler(p)
        expected = enumerate_orders(p)
        assert sampler.total == len(expected)
        seen = Counter(sampler.draw(rng)[0] for _ in range(10000 if p < 4 else 30000))
        assert set(seen) <= expected
        if p < 4:
            assert set(seen) == expected
        print(
            'p',
            p,
            'classes',
            sampler.total,
            'sampled',
            len(seen),
            'frequency range',
            min(seen.values()),
            max(seen.values()),
        )
