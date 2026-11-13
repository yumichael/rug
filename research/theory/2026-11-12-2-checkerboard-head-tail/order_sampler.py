"""Exact uniform order sampler for connected half-period components of any sizes."""

from functools import cache
from itertools import product
from math import comb, prod


def pick(rng, choices):
    choices = [(item, weight) for item, weight in choices if weight]
    choice = rng.randrange(sum(weight for _, weight in choices))
    for item, weight in choices:
        if choice < weight:
            return item
        choice -= weight
    raise AssertionError


@cache
def fubini(n):
    return 1 if n == 0 else sum(comb(n, j) * fubini(n - j) for j in range(1, n + 1))


@cache
def double_sequences(n):
    return sum(comb(n, j) * fubini(j) * fubini(n - j) for j in range(n + 1))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def choose_counts(a, b):
    return prod(comb(x, y) for x, y in zip(a, b))


class OrderSampler:
    def __init__(self, components):
        self.components = tuple(tuple(g) for g in components)
        self.sizes = tuple(sorted(set(map(len, self.components))))
        self.state = tuple(sum(len(g) == size for g in self.components) for size in self.sizes)
        self.n = sum(map(len, self.components))
        self.total = sum(self.R(self.state, k) // (2 * k) for k in range(1, len(self.components) + 1))

    @cache
    def subsets(self, state):
        return tuple(a for a in product(*(range(c + 1) for c in state)) if any(a))

    @cache
    def Y(self, state):
        n = sum(state)
        return sum(choose_counts(state, a) * (2 ** sum(s * c for s, c in zip(self.sizes, a)) - 2 ** sum(a))
                   * double_sequences(n - sum(a)) for a in self.subsets(state))

    @cache
    def R(self, state, k):
        n = sum(state)
        if k == 0:
            return int(n == 0)
        if not k <= n:
            return 0
        return sum(choose_counts(state, b) * self.Y(b) * self.R(subtract(state, b), k - 1)
                   for b in self.subsets(state) if sum(b) <= n - k + 1)

    def state_of(self, labels):
        return tuple(sum(len(self.components[i]) == s for i in labels) for s in self.sizes)

    def take(self, rng, labels, state):
        selected = set()
        for size, number in zip(self.sizes, state):
            selected.update(rng.sample([i for i in labels if len(self.components[i]) == size], number))
        return tuple(i for i in labels if i in selected), tuple(i for i in labels if i not in selected)

    def same_groups(self, rng, labels):
        if not labels:
            return []
        n = len(labels)
        count = pick(rng, [(j, comb(n, j) * fubini(n - j)) for j in range(1, n + 1)])
        selected = set(rng.sample(labels, count))
        group = tuple(v for i in labels if i in selected for v in self.components[i])
        return [group, *self.same_groups(rng, tuple(i for i in labels if i not in selected))]

    def double_block(self, rng, labels):
        state = self.state_of(labels)
        core_state = pick(rng, [(a, choose_counts(state, a)
                                * (2 ** sum(s * c for s, c in zip(self.sizes, a)) - 2 ** sum(a))
                                * double_sequences(len(labels) - sum(a))) for a in self.subsets(state)])
        core, rest = self.take(rng, labels, core_state)
        nodes = tuple(v for i in core for v in self.components[i])
        while True:
            assignment = {v: rng.randrange(2) for v in nodes}
            if any(len({assignment[v] for v in self.components[i]}) == 2 for i in core):
                break
        A, B = (tuple(v for v in nodes if assignment[v] == bit) for bit in (0, 1))
        split = pick(rng, [(j, comb(len(rest), j) * fubini(j) * fubini(len(rest) - j))
                          for j in range(len(rest) + 1)])
        selected = set(rng.sample(rest, split))
        P = self.same_groups(rng, tuple(i for i in rest if i in selected))
        Q = self.same_groups(rng, tuple(i for i in rest if i not in selected))
        return A, B, P, Q

    def sequence(self, rng, labels, k):
        if not k:
            assert not labels
            return []
        state = self.state_of(labels)
        subset = pick(rng, [(b, choose_counts(state, b) * self.Y(b) * self.R(subtract(state, b), k - 1))
                           for b in self.subsets(state) if sum(b) <= len(labels) - k + 1])
        block, rest = self.take(rng, labels, subset)
        return [self.double_block(rng, block), *self.sequence(rng, rest, k - 1)]

    def draw(self, rng, anchor=0):
        if not self.total:
            raise ValueError('No nonconstant minimum-period order classes')
        k = pick(rng, [(k, self.R(self.state, k) // (2 * k)) for k in range(1, len(self.components) + 1)])
        structure = self.sequence(rng, tuple(range(len(self.components))), k)
        groups = [g for A, B, P, Q in structure for g in [A, *P]]
        groups += [g for A, B, P, Q in structure for g in [B, *Q]]
        start = next(i for i, g in enumerate(groups) if anchor in g)
        groups = groups[start:] + groups[:start]
        rank = [None] * self.n
        for i, group in enumerate(groups):
            for v in group:
                rank[v] = i
        return tuple(rank), structure


def admissible(rank, components):
    partners = {}
    for group in components:
        values = set(rank[i] for i in group)
        if len(values) > 2:
            return False
        if len(values) == 2:
            a, b = values
            if partners.get(a, b) != b or partners.get(b, a) != a:
                return False
            partners[a], partners[b] = b, a
    if not partners:
        return False
    sequence = sorted(partners)
    half = len(sequence) // 2
    return all(partners[a] == b for a, b in zip(sequence[:half], sequence[half:]))
