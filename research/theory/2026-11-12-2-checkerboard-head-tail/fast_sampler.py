"""Uniform component orders via crossing-component counts and Stirling transforms."""

from functools import cache
from math import comb, factorial

from order_sampler import admissible, pick


@cache
def stirling(n):
    rows = [[1]]
    for i in range(1, n + 1):
        previous = rows[-1]
        rows.append([0] + [(previous[k - 1] if k - 1 < len(previous) else 0)
                           + (k * previous[k] if k < len(previous) else 0) for k in range(1, i + 1)])
    return rows


def symmetric(weights):
    result = [1] + [0] * len(weights)
    for i, weight in enumerate(weights):
        for b in range(i + 1, 0, -1):
            result[b] += weight * result[b - 1]
    return result


class OrderSampler:
    def __init__(self, components):
        self.components = tuple(tuple(g) for g in components)
        self.n = sum(map(len, self.components))
        C = len(self.components)
        self.S = stirling(C)
        self.factorials = [factorial(i) for i in range(C + 1)]
        self.cross_weights = [2 ** len(g) - 2 for g in self.components]
        self.elementary = symmetric(self.cross_weights)
        self.A, self.R = {}, {}
        for k in range(1, C + 1):
            j = 2 * k
            coefficients = [1, 2 * j]
            for ell in range(1, C):
                numerator = 2 * j * coefficients[ell] + (ell - 1) * coefficients[ell - 1]
                assert numerator % (ell + 1) == 0
                coefficients.append(numerator // (ell + 1))
            A = [sum(self.factorials[ell] * self.S[n][ell] * coefficients[ell] for ell in range(n + 1))
                 for n in range(C + 1)]
            self.A[k] = A
            self.R[k] = sum(self.elementary[b] * self.factorials[k] * self.S[b][k] * A[C - b]
                            for b in range(k, C + 1))
        self.total = sum(self.R[k] // (2 * k) for k in self.R)

    def weighted_subset(self, rng, count):
        weights = self.cross_weights
        C = len(weights)
        suffix = [[0] * (count + 1) for _ in range(C + 1)]
        suffix[C][0] = 1
        for i in range(C - 1, -1, -1):
            suffix[i][0] = 1
            for b in range(1, count + 1):
                suffix[i][b] = suffix[i + 1][b] + weights[i] * suffix[i + 1][b - 1]
        chosen = []
        for i in range(C):
            if count and rng.randrange(suffix[i][count]) < weights[i] * suffix[i + 1][count - 1]:
                chosen.append(i)
                count -= 1
        assert count == 0
        return chosen

    def partition(self, rng, labels, k):
        decisions = []
        for n in range(len(labels), 0, -1):
            singleton = self.S[n - 1][k - 1]
            together = k * (self.S[n - 1][k] if k < n else 0)
            is_singleton = rng.randrange(singleton + together) < singleton
            decisions.append((labels[n - 1], is_singleton))
            k -= is_singleton
        assert k == 0
        groups = []
        for label, is_singleton in reversed(decisions):
            if is_singleton:
                groups.append([label])
            else:
                groups[rng.randrange(len(groups))].append(label)
        return groups

    @cache
    def sequence_counts(self, j, n):
        return sum(self.factorials[ell] * self.S[n][ell] * comb(ell + j - 1, j - 1)
                   for ell in range(n + 1))

    def draw(self, rng, anchor=0):
        if not self.total:
            raise ValueError('No nonconstant minimum-period order classes')
        C = len(self.components)
        k = pick(rng, [(k, self.R[k] // (2 * k)) for k in self.R])
        b = pick(rng, [(b, self.elementary[b] * self.factorials[k] * self.S[b][k] * self.A[k][C - b])
                      for b in range(k, C + 1)])
        crossing = self.weighted_subset(rng, b)
        crossing_set = set(crossing)
        roots = self.partition(rng, crossing, k)
        rng.shuffle(roots)
        endpoints = [[] for _ in range(2 * k)]
        for root, labels in enumerate(roots):
            for label in labels:
                nodes = self.components[label]
                while True:
                    assignment = rng.getrandbits(len(nodes))
                    if assignment not in (0, (1 << len(nodes)) - 1):
                        break
                for i, node in enumerate(nodes):
                    endpoints[root + k * ((assignment >> i) & 1)].append(node)
        rest = [i for i in range(C) if i not in crossing_set]
        n = len(rest)
        t = pick(rng, [(t, comb(n, t) * (2 * k) ** t * self.sequence_counts(2 * k, n - t))
                      for t in range(n + 1)])
        monochrome = set(rng.sample(rest, t))
        for label in monochrome:
            endpoints[rng.randrange(2 * k)].extend(self.components[label])
        unpaired = [i for i in rest if i not in monochrome]
        ell = pick(rng, [(ell, self.factorials[ell] * self.S[len(unpaired)][ell]
                         * comb(ell + 2 * k - 1, 2 * k - 1)) for ell in range(len(unpaired) + 1)])
        blocks = self.partition(rng, unpaired, ell)
        rng.shuffle(blocks)
        bars = sorted(rng.sample(range(ell + 2 * k - 1), 2 * k - 1))
        boundaries = [-1, *bars, ell + 2 * k - 1]
        sizes = [right - left - 1 for left, right in zip(boundaries, boundaries[1:])]
        gaps, cursor = [], 0
        for size in sizes:
            gaps.append([tuple(v for label in group for v in self.components[label])
                         for group in blocks[cursor:cursor + size]])
            cursor += size
        structure = [(tuple(endpoints[i]), tuple(endpoints[i + k]), gaps[i], gaps[i + k]) for i in range(k)]
        groups = [g for A, B, P, Q in structure for g in [A, *P]]
        groups += [g for A, B, P, Q in structure for g in [B, *Q]]
        start = next(i for i, group in enumerate(groups) if anchor in group)
        groups = groups[start:] + groups[:start]
        rank = [None] * self.n
        for i, group in enumerate(groups):
            for v in group:
                rank[v] = i
        assert admissible(rank, self.components)
        return tuple(rank), structure
