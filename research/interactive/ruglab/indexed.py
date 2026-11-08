"""Compact Cartesian tables for exact, nonnegative machine-integer operands."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class IndexedValues:
    labels: np.ndarray
    indices: np.ndarray

    def expand(self):
        return self.labels[self.indices]


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
    """Index the combined values of two operand lists in row-major order."""
    a, b = left[:, None], right[None, :]
    functions = {
        "and": np.bitwise_and,
        "or": np.bitwise_or,
        "xor": np.bitwise_xor,
        "add": np.add,
        "mult": np.multiply,
    }
    if combiner == "clmul":
        values = _clmul_table(a, b)
    elif combiner == "absdiff":
        values = np.abs(a - b)
    else:
        values = functions[combiner](a, b)
    labels, indices = np.unique(values, return_inverse=True)
    indices = indices.reshape(values.shape).astype(np.min_scalar_type(len(labels) - 1))
    labels.flags.writeable = indices.flags.writeable = False
    return IndexedValues(labels, indices)
