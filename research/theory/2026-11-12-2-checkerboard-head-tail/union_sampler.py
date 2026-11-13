"""Exact multiplicity-corrected union sampling for an explicit finite set of bases."""

from functools import cache

import numpy as np

from fast_sampler import OrderSampler
from order_sampler import pick


@cache
def model(sizes):
    start = 0
    groups = []
    for size in sizes:
        groups.append(tuple(range(start, start + size)))
        start += size
    return OrderSampler(groups)


def canonical_partition(indices):
    flat = indices.ravel()
    _, first = np.unique(flat, return_index=True)
    order = flat[np.sort(first)]
    mapping = np.empty(int(flat.max()) + 1, dtype=np.uint32)
    mapping[order] = np.arange(len(order))
    return mapping[indices]


class UnionSampler:
    def __init__(self, bases):
        self.entries = []
        seen = set()
        for basic in bases:
            indices = canonical_partition(basic.indices)
            key = indices.tobytes()
            if key in seen:
                continue
            seen.add(key)
            components = sorted(basic.components, key=lambda g: (len(g), g))
            nodes = tuple(v for g in components for v in g)
            sampler = model(tuple(map(len, components)))
            inverse = np.empty(len(nodes), dtype=np.int64)
            inverse[list(nodes)] = np.arange(len(nodes))
            paired_indices = inverse[basic.indices]
            _, first = np.unique(indices, return_index=True)
            self.entries.append((basic, sampler, paired_indices, indices, first))

    def draw(self, rng):
        while True:
            i = pick(rng, [(i, e[1].total) for i, e in enumerate(self.entries)])
            basic, sampler, indices, _, _ = self.entries[i]
            rank, _ = sampler.draw(rng, anchor=int(indices[0, 0]))
            field = np.asarray(rank)[indices]
            flat = field.ravel()
            multiplicity = sum(np.array_equal(flat, flat[first][partition.ravel()])
                               for _, _, _, partition, first in self.entries)
            if rng.randrange(multiplicity) == 0:
                return field, {'source': i, 'multiplicity': multiplicity, 'q': basic.q, 'combiner': basic.combiner}
