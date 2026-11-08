"""Build views of pre-power and post-polynomial patterns."""

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import gcd
from sys import getsizeof

import numpy as np

from .engine import Result
from .indexed import IndexedValues, byte_lru, combination_table
from .post_polynomials import POST_STRATA, draw_post_polynomial
from .sampling import CARTESIAN_PHASES, checkerboard_indices
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
FIELD_SIZES = tuple(1 << exponent for exponent in range(1, 13))
_DENSE_CACHE_LIMIT = 1024
_BLOCK_ROWS = 128


@dataclass(frozen=True)
class PatternRecipe:
    combiner: str
    pre_power: int
    twist: int
    post_power: int


@dataclass(frozen=True)
class PostRecipe:
    combiner: str
    family: str
    valuation: int
    seed: int
    draw: int

    def polynomial(self, size):
        return draw_post_polynomial(max(8, 2 * size), self.family, self.valuation, self.seed, self.draw)


def post_polynomial_recipes(draws=24, seed=0):
    """Cycle through the strata on each pass through the catalogue."""
    return [
        PostRecipe(combiner, family, valuation, seed, draw)
        for draw, (family, valuation), combiner in product(range(draws), POST_STRATA, COMBINER_COLORS)
    ]


def recipe_description(recipe, size):
    if isinstance(recipe, PatternRecipe):
        return f"Pre {recipe.pre_power} · twist {recipe.twist} · post {recipe.post_power}"
    coefficients, modulus = recipe.polynomial(size)
    if recipe.family in ("odd power", "even power"):
        return f"{recipe.family} · p={len(coefficients) - 1} · a={coefficients[-1]}"
    valuation = (modulus // max(8, 2 * size)).bit_length() - 1
    return f"{recipe.family} · v={valuation} · degree {len(coefficients) - 1}"


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
    upper_left, upper_right = values[:half, :half], values[:half, half:]
    lower_left, lower_right = values[half:, :half], values[half:, half:]
    if np.array_equal(values[:half], values[half:]) or np.array_equal(values[:, :half], values[:, half:]):
        return None
    if not (np.array_equal(upper_left, lower_right) and np.array_equal(upper_right, lower_left)):
        return "square"
    if half == 1:
        return "diamond"
    quarter = half // 2
    # A larger subgroup would contain an order-four shift whose double is
    # the half-diagonal. The other two candidates are inverses of these.
    if any(_matches_shift(values, quarter, dx) for dx in (quarter, 3 * quarter)):
        return None
    return "diamond"


def _matches_shift(values, dy, dx):
    height, width = values.shape
    rows = ((slice(dy, None), slice(None, height - dy)), (slice(None, dy), slice(height - dy, None)))
    cols = ((slice(dx, None), slice(None, width - dx)), (slice(None, dx), slice(width - dx, None)))
    return all(
        np.array_equal(values[y, x], values[other_y, other_x]) for (y, other_y), (x, other_x) in product(rows, cols)
    )


def _distinct_powers(inputs, power):
    """Return powered residues at the least modulus preserving inputs and zero."""
    if inputs[-1] == 0:
        return np.array([0], dtype=object), 1
    common = int(np.bitwise_or.reduce(inputs))
    shift = (common & -common).bit_length() - 1
    reduced = inputs >> shift if shift else inputs
    nonzero = reduced[1:] if reduced[0] == 0 else reduced
    max_depth = int(np.bitwise_count((nonzero & -nonzero) - 1).max())
    low = max_depth * power + 1
    # Bound the difference depth using the input width, the greatest input
    # valuation and the valuation of the power.
    high = int(reduced[-1]).bit_length() + (power - 1) * max_depth + (power & -power).bit_length()
    if high <= 64:
        # Unsigned wraparound computes exactly the low 64 bits of the power.
        residues = _power_uint64(reduced, power)
    else:
        modulus = 1 << high
        residues = np.asarray([pow(z, power, modulus) for z in reduced.tolist()], dtype=object)
    while low < high:
        middle = (low + high) // 2
        mask = (1 << middle) - 1
        masked = residues & mask
        if residues.dtype == np.uint64:
            distinct = np.unique(masked).size
        else:
            distinct = len(set(masked))
        if distinct == residues.size:
            high = middle
        else:
            low = middle + 1
    mask = (1 << low) - 1
    offset = shift * power
    dtype = np.uint64 if low + offset <= 64 else object
    residues = (residues & mask).astype(dtype, copy=False)
    return residues << offset, 1 << (low + offset)


def _power_uint64(values, power):
    base = values.astype(np.uint64)
    result = np.ones_like(base)
    while power:
        if power & 1:
            result *= base
        power >>= 1
        if power:
            base *= base
    return result


@dataclass(frozen=True)
class SampledField:
    values: IndexedValues
    spec: dict
    repeat_shape: str
    zero_fraction: float

    @property
    def distinct_values(self):
        return len(self.values.labels)

    @property
    def result(self):
        """Materialize exact cell values for analysis or export."""
        return Result(
            self.values.expand().astype(object, copy=False), self.spec["M"], self.spec, colors=self.spec["color"]
        )


@lru_cache(maxsize=64)
def _operand_table(q, twist, K, coordinates):
    mask = K - 1
    pre = [pow(i, q, K) for i in coordinates]
    if twist:
        pre = [(t + 2 * twist * t * (t - 1)) & mask for t in pre]
    return np.unique(np.asarray(pre, dtype=np.int64), return_inverse=True)


@byte_lru(32, 48 << 20, lambda result: result[0].nbytes + result[1].nbytes + result[2].nbytes)
def _indexed_pairs(q, twist, K, combiner, x_coords, y_coords):
    x_values, x_index = _operand_table(q, twist, K, x_coords)
    y_values, y_index = _operand_table(q, twist, K, y_coords)
    return combination_table(y_values, x_values, combiner), x_index, y_index


@lru_cache(maxsize=4)
def _checker_positions(size, period, sampling):
    return _checker_block(size, period, sampling, 0, size)


def _checker_block(size, period, sampling, start, stop):
    x, y = checkerboard_indices(
        np.arange(size, dtype=np.int16)[None, :],
        np.arange(start, stop, dtype=np.int16)[:, None],
        sampling,
        axis="vertical",
    )
    return x % period, y % period


def _identity_xor(size, sampling):
    dtype = np.min_scalar_type(size - 1)
    if sampling.startswith("checkerboard"):
        period = 2 * size
        phase = int(sampling == "checkerboard_opposite")
        indices = np.empty((size, size), dtype=dtype)
        for start in range(0, size, _BLOCK_ROWS):
            stop = min(start + _BLOCK_ROWS, size)
            x, y = _checker_block(size, period, sampling, start, stop)
            indices[start:stop] = (x ^ y) >> 1
        return np.arange(phase, period, 2), indices
    axis = np.arange(size, dtype=dtype)
    indices = axis[:, None] ^ axis[None, :]
    if sampling in CARTESIAN_PHASES:
        x, y = CARTESIAN_PHASES[sampling]
        return np.arange(x ^ y, 2 * size, 2), indices
    return np.arange(size), indices


@byte_lru(32, 96 << 20, lambda result: result[0].nbytes + result[2].nbytes)
def _base_field(q, twist, K, combiner, size, sampling):
    if q == 1 and combiner == "xor":
        labels, indices = _identity_xor(size, sampling)
    elif sampling.startswith("checkerboard"):
        # Same-parity XOR can have a combined period half the operand period.
        period = size * (2 if sampling == "checkerboard_same" and combiner == "xor" else 1)
        pairs, x_index, y_index = _indexed_pairs(q, twist, K, combiner, range(period), range(period))
        labels = pairs.labels
        if size <= _DENSE_CACHE_LIMIT:
            x, y = _checker_positions(size, period, sampling)
            indices = pairs.indices[y_index[y], x_index[x]]
        else:
            indices = np.empty((size, size), dtype=pairs.indices.dtype)
            for start in range(0, size, _BLOCK_ROWS):
                stop = min(start + _BLOCK_ROWS, size)
                x, y = _checker_block(size, period, sampling, start, stop)
                indices[start:stop] = pairs.indices[y_index[y], x_index[x]]
    else:
        phases = CARTESIAN_PHASES.get(sampling)
        x_coords, y_coords = (
            (range(size), range(size))
            if phases is None
            else (
                range(phases[0], 2 * size, 2),
                range(phases[1], 2 * size, 2),
            )
        )
        pairs, x_index, y_index = _indexed_pairs(q, twist, K, combiner, x_coords, y_coords)
        labels = pairs.labels
        indices = pairs.indices[y_index[:, None], x_index[None, :]]

    if size <= _DENSE_CACHE_LIMIT:
        counts = np.bincount(indices.ravel(), minlength=len(labels))
    else:
        counts = np.zeros(len(labels), dtype=np.intp)
        for start in range(0, size, _BLOCK_ROWS):
            block_counts = np.bincount(indices[start : start + _BLOCK_ROWS].ravel())
            counts[: block_counts.size] += block_counts
    present = counts != 0
    if not present.all():
        labels = labels[present]
        counts = counts[present]
        remap = (np.cumsum(present) - 1).astype(np.min_scalar_type(len(labels) - 1))
        if size <= _DENSE_CACHE_LIMIT:
            indices = remap[indices]
        else:
            compact = indices if indices.dtype == remap.dtype else np.empty(indices.shape, dtype=remap.dtype)
            for start in range(0, size, _BLOCK_ROWS):
                block = slice(start, start + _BLOCK_ROWS)
                compact[block] = remap[indices[block]]
            indices = compact
    repeat = "constant" if len(labels) == 1 else (_repeat_shape(indices) or "smaller tile")
    labels.flags.writeable = indices.flags.writeable = counts.flags.writeable = False
    return IndexedValues(labels, indices), repeat, counts


def _power_bytes(result):
    labels, modulus = result
    # Object arrays also own Python integers, each bounded by the modulus.
    return labels.nbytes + (labels.size * getsizeof(modulus) if labels.dtype == object else 0)


@byte_lru(16, 32 << 20, _power_bytes)
def _powered_labels(q, twist, K, combiner, size, sampling, power):
    base, _, _ = _base_field(q, twist, K, combiner, size, sampling)
    powers, modulus = _distinct_powers(base.labels, power)
    powers.flags.writeable = False
    return powers, modulus


def _sample_post_field(recipe, size, sampling):
    coefficients, modulus = recipe.polynomial(size)
    combiner = recipe.combiner
    K = (
        2 * size
        if sampling in CARTESIAN_PHASES or (combiner == "xor" and sampling.startswith("checkerboard"))
        else size
    )
    label_sampling = "even_odd" if sampling == "odd_even" else sampling
    base, repeat, counts = _base_field(1, 0, K, combiner, size, label_sampling)
    inputs = base.labels.astype(np.uint64)
    mask = modulus - 1
    stride = gcd(*(i for i, coefficient in enumerate(coefficients) if coefficient))
    if stride > 1:
        inputs = _power_uint64(inputs, stride) & mask
    outputs = np.zeros_like(inputs)
    for coefficient in reversed(coefficients[::stride]):
        outputs = (outputs * inputs + (coefficient & mask)) & mask
    zeros = int(counts[outputs == 0].sum())
    labels, inverse = np.unique(outputs, return_inverse=True)
    indices = base.indices
    if len(labels) == len(outputs):
        labels = outputs
    else:
        indices = inverse.astype(np.min_scalar_type(len(labels) - 1))[indices]
        repeat = "constant" if len(labels) == 1 else (_repeat_shape(indices) or "smaller tile")
    if sampling == "odd_even":
        indices = indices.T
    spec = {
        "n": size,
        "K": K,
        "M": modulus,
        "pre": [],
        "sampling": sampling,
        "combine": combiner,
        "post": [["poly", list(coefficients)]],
        "color": COMBINER_COLORS[combiner],
    }
    if sampling.startswith("checkerboard"):
        spec["checkerboard_axis"] = "vertical"
    return SampledField(IndexedValues(labels, indices), spec, repeat, zeros / indices.size)


def sample_field(recipe: PatternRecipe | PostRecipe, size: int, sampling: str) -> SampledField:
    """Build one sampled field with its own pre- and post-moduli."""
    if size not in FIELD_SIZES:
        raise ValueError("Choose a power-of-two field size from 2 to 4096 cells")
    if sampling not in SAMPLINGS:
        raise ValueError("Unknown sampling: " + sampling)
    if isinstance(recipe, PostRecipe):
        return _sample_post_field(recipe, size, sampling)
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
    elif sampling in CARTESIAN_PHASES:
        # The odd branch advances by two. A mixed view uses the same K on
        # both operands, and the even branch can repeat sooner.
        K <<= 1
    elif sampling == "checkerboard_same" and recipe.combiner == "xor":
        # A size-cell shift toggles the top bit of both odd operands and
        # preserves both even operands. XOR cancels the paired toggles.
        K <<= 1
    if K > 1 << 32:
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
    if sampling.startswith("checkerboard"):
        spec["checkerboard_axis"] = "vertical"
    # The mixed samplings are transposes because the catalogue combiners are symmetric.
    label_sampling = "even_odd" if sampling == "odd_even" else sampling
    base, repeat, counts = _base_field(q, recipe.twist, K, recipe.combiner, size, label_sampling)
    powers, modulus = _powered_labels(q, recipe.twist, K, recipe.combiner, size, label_sampling, recipe.post_power)
    spec.update(M=modulus, post=[["pow", recipe.post_power]])
    indices = base.indices.T if sampling == "odd_even" else base.indices
    zeros = int(counts[0]) if base.labels[0] == 0 else 0
    return SampledField(IndexedValues(powers, indices), spec, repeat, zeros / indices.size)
