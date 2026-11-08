"""Build views of even-pre-power patterns on a certified display torus."""

from dataclasses import dataclass
from itertools import product

import numpy as np

from .engine import Result, clear_cache, evaluate
from .specs import SAMPLINGS

COMBINER_COLORS = {
    "and": "cmr.ember",
    "or": "cmr.freeze",
    "xor": "cmr.fall",
    "add": "cmr.savanna",
    "mult": "cmr.ocean",
    "clmul": "cmr.guppy",
    "absdiff": "cmr.amber",
}


@dataclass(frozen=True)
class PatternRecipe:
    combiner: str
    pre_power: int
    twist: int
    post_power: int


def exploration_recipes():
    return [
        PatternRecipe(combiner, pre_power, twist, post_power)
        for twist, post_power, pre_power, combiner in product(
            (0, 1, -3), (3, 7, 14, 27), (2, 4, 6, 8, 10, 12, 14, 16), COMBINER_COLORS
        )
    ]


def _repeat_shape(values):
    """Recognize square and diamond tiles on a known dyadic square torus."""
    half = values.shape[0] // 2
    if np.array_equal(values, np.roll(values, half, axis=0)) or np.array_equal(values, np.roll(values, half, axis=1)):
        return None
    if not np.array_equal(values, np.roll(values, (half, half), axis=(0, 1))):
        return "square"
    quarter = half // 2
    # A larger subgroup would contain an order-four shift whose double is
    # the half-diagonal. The other two candidates are inverses of these.
    if any(np.array_equal(values, np.roll(values, (quarter, dy), axis=(0, 1))) for dy in (quarter, -quarter)):
        return None
    return "diamond"


def _distinct_powers(inputs, power):
    """Return powered residues at the least modulus preserving inputs and zero."""
    atoms = [int(z) for z in inputs]
    if atoms == [0]:
        return np.array([0], dtype=object), 1
    max_depth = max((z & -z).bit_length() - 1 for z in atoms if z)
    low = max_depth * power + 1
    # Bound the difference depth using the input width, the greatest input
    # valuation and the valuation of the power.
    high = atoms[-1].bit_length() + (power - 1) * max_depth + (power & -power).bit_length()
    residues = [pow(z, power, 1 << high) for z in atoms]
    while low < high:
        middle = (low + high) // 2
        mask = (1 << middle) - 1
        if len({r & mask for r in residues}) == len(atoms):
            high = middle
        else:
            low = middle + 1
    modulus = 1 << low
    return np.array([r % modulus for r in residues], dtype=object), modulus


@dataclass
class SampledField:
    result: Result
    repeat_shape: str
    zero_fraction: float
    distinct_values: int


def sample_field(recipe: PatternRecipe, size: int, sampling: str) -> SampledField:
    """Build one sampled field with its own pre- and post-moduli."""
    if size not in (256, 512, 1024):
        raise ValueError("Choose a field size of 256, 512, or 1024 cells")
    if sampling not in SAMPLINGS:
        raise ValueError("Unknown sampling: " + sampling)
    q = recipe.pre_power
    if q < 2 or q % 2 or recipe.post_power < 1:
        raise ValueError("Use a positive even pre-power and a positive post-power")
    pre = [["pow", q]]
    if recipe.twist:
        # f(t) = t + 2c*t*(t-1) preserves the pre-power's periods.
        pre.append(["poly", [0, 1 - 2 * recipe.twist, 2 * recipe.twist]])
    K = size * (q & -q)
    if sampling == "even_even":
        # (2i)^q leaves q low zero bits, so i^q sees a modulus of K >> q.
        K <<= q
    elif sampling in ("even_odd", "odd_even", "odd_odd"):
        # The odd branch advances by two. A mixed view uses the same K on
        # both operands, and the even branch can repeat sooner.
        K <<= 1
    elif sampling == "checkerboard_same" and recipe.combiner == "xor":
        # A size-cell shift toggles the top bit of both odd operands and
        # preserves both even operands. XOR cancels the paired toggles.
        K <<= 1
    if K > 1 << 31:
        raise ValueError("Pre-modulus too large for the catalogue's integer tables")
    spec = {
        "n": size,
        "K": K,
        "M": 1,
        "pre": pre,
        "sampling": sampling,
        "combine": recipe.combiner,
        "color": COMBINER_COLORS[recipe.combiner],
    }
    # Even full products fit in int64 at the bounded pre-modulus.
    values = evaluate(spec).stages["z0"].astype(np.int64)
    clear_cache()
    inputs, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    zeros = int(counts[0]) if inputs[0] == 0 else 0
    repeat = "constant" if len(inputs) == 1 else (_repeat_shape(values) or "smaller tile")
    powers, modulus = _distinct_powers(inputs, recipe.post_power)
    spec.update(M=modulus, post=[["pow", recipe.post_power]])
    result = Result(powers[inverse.reshape(values.shape)], modulus, spec, colors=spec["color"])
    return SampledField(result, repeat, zeros / values.size, len(inputs))
