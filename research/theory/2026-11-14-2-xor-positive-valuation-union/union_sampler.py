"""Exact rank/unrank for the union of positive-valuation XOR sum classes.

The November 2 coordinate construction supplies each conditional sampler.
The companion report proves that these rows are disjoint through the first
shared tail. This module adds the joint class index, not an app integration.
"""

from __future__ import annotations

import importlib.util
from bisect import bisect_right
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random


def _coordinates_module():
    path = Path(__file__).resolve().parents[1] / "2026-11-02-xor-polynomial-period/xor_polynomial_period.py"
    spec = importlib.util.spec_from_file_location("xor_polynomial_coordinates", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


coordinates = _coordinates_module()


def tail_start(domain: int) -> int:
    if domain < 8 or domain & (domain - 1):
        raise ValueError("Use C=2**c >= 8; displayed side is C/2")
    return max(1, domain.bit_length() - 5)


@dataclass(frozen=True)
class Recipe:
    domain: int
    valuation: int
    modulus: int
    spanning_coefficients: tuple[int, ...]

    def value(self, z: int) -> int:
        """Evaluate the factored integer post-polynomial, anchored at z=1."""
        w = pow(z, 1 << self.valuation, self.modulus)
        product = w
        value = 0
        spacing = 1 << (self.valuation + 3)
        for k, coefficient in enumerate(self.spanning_coefficients):
            value += coefficient * (product - int(k == 0))
            product = product * (w * w - (1 + spacing * k)) % self.modulus
        return value % self.modulus

    def normalized_table(self) -> tuple[int, ...]:
        step = 1 << (self.valuation + 2)
        values = tuple(self.value(z) for z in range(1, self.domain, 2))
        assert all(value % step == 0 for value in values)
        return tuple(value // step for value in values)

    def polynomial(self) -> tuple[int, ...]:
        """Expand only when a consumer requires monomial coefficients."""
        power = 1 << self.valuation
        product = [0] * power + [1]
        result = [0]
        for k, coefficient in enumerate(self.spanning_coefficients):
            result.extend([0] * max(0, len(product) - len(result)))
            for degree, term in enumerate(product):
                result[degree] = (result[degree] + coefficient * term) % self.modulus
            if k == 0:
                result[0] = (result[0] - coefficient) % self.modulus
            node = 1 + (1 << (self.valuation + 3)) * k
            extended = [0] * (len(product) + 2 * power)
            for degree, term in enumerate(product):
                extended[degree] -= node * term
                extended[degree + 2 * power] += term
            product = [term % self.modulus for term in extended]
        while len(result) > 1 and result[-1] == 0:
            result.pop()
        return tuple(result)


def conditional_unrank(domain: int, valuation: int, space: dict, rank: int) -> Recipe:
    count = space["valid_shift_classes"]
    if not 0 <= rank < count:
        raise ValueError("Conditional rank is outside the class range")
    bits, character = space["bits"], space["character"]
    active = min((j for j, flag in enumerate(character) if flag), key=lambda j: bits[j])
    # Decode the character-one coordinate as odd; all remaining coordinates
    # range independently after subtracting the chosen generator as needed.
    width = bits[active] - 1
    coefficients = [0] * len(bits)
    coefficients[active] = 1 + 2 * (rank % (1 << width))
    rank >>= width
    for j, size in enumerate(bits):
        if j != active:
            coefficients[j] = rank % (1 << size)
            rank >>= size
    assert rank == 0
    coefficients[active] -= sum(coefficients[j] * character[j] for j in range(len(bits)) if j != active)
    modulus = space["modulus"]
    weights = tuple(sum(a * b for a, b in zip(row, coefficients)) % modulus for row in space["transform"])
    return Recipe(domain, valuation, modulus, weights)


class UnionSampler:
    """One disjoint global index; construction scales with C, not class count."""

    def __init__(self, domain: int):
        self.domain = domain
        self.tail = tail_start(domain)
        self.rows = [coordinates.same_v_space(domain, v) for v in range(1, self.tail + 1)]
        self.ends = []
        total = 0
        for row in self.rows:
            total += row["valid_shift_classes"]
            self.ends.append(total)
        self.count = total

    def unrank(self, rank: int) -> Recipe:
        if not 0 <= rank < self.count:
            raise ValueError("Union rank is outside the class range")
        row = bisect_right(self.ends, rank)
        local_rank = rank - (self.ends[row - 1] if row else 0)
        return conditional_unrank(self.domain, row + 1, self.rows[row], local_rank)

    def draw(self, rng: Random) -> Recipe:
        # randrange uses bounded-integer sampling, not biased modulo reduction.
        return self.unrank(rng.randrange(self.count))

    def summary(self) -> dict:
        return {
            "C": self.domain,
            "displayed_side": self.domain // 2,
            "shared_tail_starts_at_v": self.tail,
            "valid_bits_by_v": [row["valid_bits"] for row in self.rows],
            "row_counts": [row["valid_shift_classes"] for row in self.rows],
            "union_classes": self.count,
            "single_power_union_classes": self.domain**2 // 256 if self.domain >= 32 else self.domain // 8,
        }


if __name__ == "__main__":
    import json

    sampler = UnionSampler(4096)
    print(json.dumps({"summary": sampler.summary(), "example": asdict(sampler.draw(Random(0)))}, indent=2))
