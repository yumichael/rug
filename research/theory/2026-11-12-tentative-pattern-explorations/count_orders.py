"""Exact counts and an independent small ordered-partition enumeration."""

from functools import lru_cache
from itertools import permutations
from math import comb


@lru_cache(None)
def ordered_bell(n):
    if n == 0:
        return 1
    return sum(comb(n, j) * ordered_bell(n - j) for j in range(1, n + 1))


def counts(pmax):
    f = [ordered_bell(n) for n in range(pmax + 1)]
    d = [sum(comb(n, j) * f[j] * f[n - j] for j in range(n + 1)) for n in range(pmax + 1)]
    y = [0] + [sum(comb(n, a) * (4**a - 2**a) * d[n - a] for a in range(1, n + 1)) for n in range(1, pmax + 1)]
    R = [[0] * (pmax + 1) for _ in range(pmax + 1)]
    R[0][0] = 1
    for p in range(1, pmax + 1):
        for k in range(1, p + 1):
            R[p][k] = sum(comb(p, s) * y[s] * R[p - s][k - 1] for s in range(1, p - k + 2))
    for p in range(1, pmax + 1):
        assert all(R[p][k] % (2 * k) == 0 for k in range(1, p + 1))
    return f, d, y, R


def partitions(n):
    # Restricted-growth strings, giving every set partition once.
    a = [0] * n

    def visit(i, top):
        if i == n:
            yield tuple(a)
            return
        for v in range(top + 2):
            a[i] = v
            yield from visit(i + 1, max(top, v))

    yield from visit(1, 0)


def admissible(rank):
    k = max(rank) + 1
    partner = {}
    for i in range(0, len(rank), 2):
        a, b = rank[i], rank[i + 1]
        if a == b:
            continue
        if (a in partner and partner[a] != b) or (b in partner and partner[b] != a):
            return False
        partner[a] = b
        partner[b] = a
    if not partner:
        return False
    paired = [i for i in range(k) if i in partner]
    half = len(paired) // 2
    return all(partner[paired[i]] == paired[(i + half) % len(paired)] for i in range(len(paired)))


def enumerate_orders(p):
    result = set()
    for part in partitions(2 * p):
        groups = max(part) + 1
        # Node zero's group is the anchored first color.
        for rest in permutations(range(1, groups)):
            order = (0, *rest)
            lookup = {g: i for i, g in enumerate(order)}
            rank = tuple(lookup[g] for g in part)
            if admissible(rank):
                result.add(rank)
    return result


if __name__ == '__main__':
    f, d, y, R = counts(10)
    for p in range(1, 11):
        total = sum(R[p][k] // (2 * k) for k in range(1, p + 1))
        print(
            'abstract paired-inputs=',
            p,
            'order classes=',
            total,
            'Rug side=' + str(4 * p) if p & (p - 1) == 0 else '(combinatorial model only)',
        )
        if p <= 3:
            actual = len(enumerate_orders(p))
            assert actual == total, (p, actual, total)
            print('  verified by independent ordered-partition enumeration')
