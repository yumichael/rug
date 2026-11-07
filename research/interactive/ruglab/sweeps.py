"""Lazy Cartesian grids and explicit paired variations."""

from copy import deepcopy
from math import prod

from .specs import resolve


class Sweep:
    def __init__(self, spec):
        self.spec = deepcopy(spec)
        self.axes = (
            [options for _, options in spec.get("pre", [])]
            + [spec["combine"]]
            + [options for _, options in spec.get("post", [])]
        )
        self.count = prod(map(len, self.axes))

    def page(self, start=0, size=12):
        if start < 0 or size < 1:
            raise ValueError("Invalid page")
        for index in range(start, min(start + size, self.count)):
            yield str(index), self.get(index)

    def get(self, index):
        if not 0 <= index < self.count:
            raise IndexError(index)
        choices = []
        for axis in reversed(self.axes):
            index, digit = divmod(index, len(axis))
            choices.append(axis[digit])
        choices.reverse()
        s = deepcopy(self.spec)
        p = len(s.get("pre", []))
        s["pre"] = [[name, v] for (name, _), v in zip(s.get("pre", []), choices[:p], strict=True)]
        s["combine"] = choices[p]
        s["post"] = [[name, v] for (name, _), v in zip(s.get("post", []), choices[p + 1 :], strict=True)]
        return resolve(s)


def paired(base, **columns):
    lengths = {len(v) for v in columns.values()}
    if len(lengths) != 1:
        raise ValueError("Paired variation lengths differ")
    for i, values in enumerate(zip(*columns.values(), strict=True)):
        s = deepcopy(base)
        s.update(zip(columns, values, strict=True))
        yield str(i), resolve(s)
