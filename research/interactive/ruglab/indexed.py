"""Compact Cartesian tables for exact, nonnegative machine-integer operands."""

from collections import OrderedDict
from dataclasses import dataclass
from functools import wraps
from threading import RLock

import numpy as np


@dataclass(frozen=True)
class IndexedValues:
    labels: np.ndarray
    indices: np.ndarray

    def expand(self):
        return self.labels[self.indices]

    @property
    def nbytes(self):
        return self.labels.nbytes + self.indices.nbytes


def byte_lru(max_entries, max_bytes, measure):
    """Cache positional calls under entry and retained-byte limits."""

    def decorate(function):
        entries = OrderedDict()
        retained = 0
        lock = RLock()

        @wraps(function)
        def cached(*args):
            nonlocal retained
            with lock:
                if args in entries:
                    entries.move_to_end(args)
                    return entries[args][0]
                result = function(*args)
                cost = measure(result)
                if cost <= max_bytes:
                    while entries and (retained + cost > max_bytes or len(entries) >= max_entries):
                        _, (_, removed) = entries.popitem(last=False)
                        retained -= removed
                    entries[args] = result, cost
                    retained += cost
                return result

        return cached

    return decorate


def _clmul_table(left, right):
    values = np.zeros((left.size, right.size), dtype=np.int64)
    bits = int(np.bitwise_or.reduce(right, axis=None))
    while bits:
        bit = bits & -bits
        shift = bit.bit_length() - 1
        np.bitwise_xor(values, left << shift, out=values, where=(right & bit) != 0)
        bits ^= bit
    return values


def combination_table(left, right, combiner):
    """Index the combined values of two nonnegative 32-bit operand lists."""
    a, b = left[:, None], right[None, :]
    functions = {
        "and": np.bitwise_and,
        "or": np.bitwise_or,
        "xor": np.bitwise_xor,
        "add": np.add,
    }
    if combiner == "clmul":
        values = _clmul_table(a, b)
    elif combiner == "mult":
        values = a.astype(np.uint64) * b.astype(np.uint64)
    elif combiner == "absdiff":
        values = np.abs(a - b)
    else:
        values = functions[combiner](a, b)
    maximum = int(values.max())
    if maximum < min(values.size, 1 << 20):
        # Small output ranges can be indexed directly without sorting pairs.
        present = np.zeros(maximum + 1, dtype=bool)
        present[values] = True
        labels = np.flatnonzero(present)
        lookup = np.empty(maximum + 1, dtype=np.min_scalar_type(len(labels) - 1))
        lookup[labels] = np.arange(len(labels), dtype=lookup.dtype)
        indices = lookup[values]
    else:
        labels, indices = np.unique(values, return_inverse=True)
        indices = indices.reshape(values.shape).astype(np.min_scalar_type(len(labels) - 1))
    labels.flags.writeable = indices.flags.writeable = False
    return IndexedValues(labels, indices)
