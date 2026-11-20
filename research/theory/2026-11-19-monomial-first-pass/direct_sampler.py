"""Rank and sample monomial classes through their algebraic coordinates."""

from dataclasses import dataclass
from math import comb
from random import Random

from precision import moduli
from study import CHECKER_COMBINERS, CHECKERBOARD, ODD_COSETS, ODD_ODD, Base, Witness, valuation

MINIMUM = "minimum_period"
PRESERVING = ("distinct_outputs", "catalogue")


def _check_side(side):
    if side < 16 or side & (side - 1):
        raise ValueError("Use a power-of-two displayed side of at least 16.")


def _select(counts, rank):
    if 0 <= rank < sum(counts):
        for index, count in enumerate(counts):
            if rank < count:
                return index, rank
            rank -= count
    raise ValueError("Rank is outside the class space.")


class Sampler:
    """Use a uniform bounded integer to select a class."""

    count: int

    def unrank(self, rank: int) -> Witness:
        raise NotImplementedError

    def draw(self, rng: Random) -> Witness:
        return self.unrank(rng.randrange(self.count))

    def sample_spec(self, rng: Random):
        witness = self.draw(rng)
        return witness.spec(rng.randrange(witness.modulus))


@dataclass(frozen=True)
class PostRow:
    unit_modulus: int
    scale_bits: int
    first_power: int
    power_step: int
    power_choices: int
    multiplier_choices: int

    @property
    def count(self):
        return self.power_choices * self.multiplier_choices

    def witness(self, base, rank):
        power_index, multiplier_index = divmod(rank, self.multiplier_choices)
        p = self.first_power + self.power_step * power_index
        M = self.unit_modulus << (valuation(p) + self.scale_bits * p)
        return Witness(base, p, 2 * multiplier_index + 1, M)


def _unit_row(unit_modulus, s, scale_bits=0, *, even=False):
    T = unit_modulus >> s
    step = 2 if even else 1
    return PostRow(unit_modulus, scale_bits, step, step, max(1, T >> (s + even)), T // 2)


def _odd_nonunit_rows(base):
    t = valuation(base.size) - 1
    s = valuation(base.q) + 2
    if base.combiner == "absdiff":
        return (PostRow(4, s, 1, 2, 2, 2),)
    T = 1 << t
    small = PostRow(T, s, 1, 2, t // 2, T // 2)
    tail = PostRow(T, s, t | 1, 2, T // 8, T // 2)
    return small, tail


class PostSampler(Sampler):
    """Exact conditional union over post-powers and odd multipliers.

    Minimum period indexes both shift and order classes. The preserving
    selectors index shift classes. The nonunit odd-odd cases support odd
    post-powers at Minimum period.
    """

    def __init__(self, base: Base, selector=MINIMUM, *, odd_powers_only=False):
        _check_side(base.size)
        if base.q < 2 or base.q % 2:
            raise ValueError("Use a positive even pre-power.")
        if selector not in (MINIMUM, *PRESERVING):
            raise ValueError("Unknown modulus selector.")
        self.base = base
        w = valuation(base.q)
        if odd_powers_only:
            if base.sampling != ODD_ODD or base.combiner not in ("xor", "absdiff") or selector != MINIMUM:
                raise ValueError("Odd-power mode is for odd-odd XOR and ABSDIFF at Minimum period.")
            self.rows = _odd_nonunit_rows(base)
        elif base.sampling == CHECKERBOARD and base.combiner in CHECKER_COMBINERS:
            s = min(base.q, w + 2)
            if base.combiner == "absdiff" and base.q < valuation(base.K):
                if selector == MINIMUM:
                    odd = PostRow(4, 0, 1, 1, 1, 1)
                else:
                    odd = PostRow(base.K, 0, 1, 2, (base.K >> s) // 2, base.K // 4)
                even_modulus = getattr(moduli(base, 2), selector) >> 1
                self.rows = odd, _unit_row(even_modulus, s, even=True)
            else:
                self.rows = (_unit_row(getattr(moduli(base, 1), selector), s),)
        elif base.sampling == ODD_ODD and base.combiner in ODD_COSETS:
            factor = int(base.combiner == "add")
            s = w + 2 - factor
            self.rows = (_unit_row(getattr(moduli(base, 1), selector) >> factor, s, factor),)
        else:
            raise ValueError("This sampling, combiner and selector have no direct conditional sampler here.")
        self.counts = tuple(row.count for row in self.rows)
        self.count = sum(self.counts)
        if odd_powers_only:
            self.equality_counts = (2,) if base.combiner == "absdiff" else (self.rows[0].power_choices, 1)
        else:
            self.equality_counts = (1, 1) if len(self.rows) == 2 and selector == MINIMUM else (1,)
        self.equality_count = sum(self.equality_counts)

    def unrank(self, rank):
        row, local = _select(self.counts, rank)
        return self.rows[row].witness(self.base, local)

    def unrank_equality(self, rank):
        row, power_index = _select(self.equality_counts, rank)
        return self.rows[row].witness(self.base, power_index * self.rows[row].multiplier_choices)


def _twist_polynomial(coefficients, s, t):
    """Convert normalized falling-factorial coordinates to the native Q."""
    if not any(coefficients):
        return ()
    S = 1 << s
    mask = (1 << (t - 1)) - 1
    R = [0] * (1 + (t - 2) // s)
    product = [1]
    for k, coefficient in enumerate(coefficients, 1):
        for j, value in enumerate(product):
            R[j] = (R[j] + coefficient * value) & mask
        if k < len(coefficients):
            factor = -S * k
            product = [
                ((product[j] * factor if j < len(product) else 0) + (product[j - 1] if j else 0)) & mask
                for j in range(len(product) + 1)
            ]

    # Divide by 1+y in the truncated Taylor ring, then substitute y=z-1.
    Q = []
    previous = 0
    for value in R:
        previous = (value - previous) & mask
        Q.append(previous)
    return tuple(sum(Q[j] * comb(j, i) * (-1) ** (j - i) for j in range(i, len(Q))) & mask for i in range(len(Q)))


class PreSpace:
    """All distinct pre-maps at one valuation on a complete odd operand coset."""

    def __init__(self, t, w, twists):
        self.t = t
        self.w = w
        self.s = w + 2
        self.T = 1 << t
        self.twists = twists
        depths = tuple(self.s * (k - 1) + k - k.bit_count() for k in range(1, 2 + (t - 1) // self.s))
        active = tuple(depth for depth in depths if depth < t)
        self.bits = tuple(t - 1 - depth for depth in active)
        self.power_choices = 1 << (len(active).bit_length() - 1) if twists else self.T // 2
        self.count = self.power_choices << sum(self.bits) if twists else self.power_choices

    def unrank(self, rank, *, normalize=False):
        """Optionally fix the code at original operand 5 to its value at u=1."""
        if normalize and not self.twists:
            if rank != 0:
                raise ValueError("Rank is outside the class space.")
            return 1 << self.w, ()
        count = self.count // (self.T // 2) if normalize else self.count
        if not 0 <= rank < count:
            raise ValueError("Rank is outside the class space.")
        digits, i = divmod(rank, self.power_choices)
        q = (2 * i + 1) << self.w
        if not self.twists:
            return q, ()

        coefficients = [0] if normalize else []
        for width in self.bits[int(normalize) :]:
            digits, coefficient = divmod(digits, 1 << width)
            coefficients.append(coefficient)
        if normalize:
            K = self.T << self.s
            B = (pow(5, q, K) - 1) >> self.s
            target = (pow(5, 1 << self.w, K) - 1) >> self.s
            falling, higher = B, 0
            for k, coefficient in enumerate(coefficients[1:], 2):
                falling *= B - (k - 1)
                higher += (coefficient * falling) << (self.s * (k - 1))
            # The factor of two has been removed from both sides.
            coefficients[0] = (((target - B) // 2 - higher) * pow(B, -1, self.T // 2)) % (self.T // 2)
        return q, _twist_polynomial(coefficients, self.s, self.t)


class OddBitwiseSampler(Sampler):
    """Odd-odd AND/OR, over every positive even pre-power and post-power."""

    def __init__(self, size, combiners=("and", "or"), *, twists=False):
        _check_side(size)
        combiners = tuple(combiners)
        if not combiners or len(set(combiners)) != len(combiners) or not set(combiners) <= {"and", "or"}:
            raise ValueError("Choose a nonempty subset of AND and OR.")
        self.size = size
        self.combiners = combiners
        t = valuation(size) - 1
        self.rows = tuple(PreSpace(t, w, twists) for w in range(1, t - 1))
        self.posts = tuple(_unit_row(row.T << row.s, row.s) for row in self.rows)
        self.counts = tuple(pre.count * post.count for pre, post in zip(self.rows, self.posts, strict=True))
        self.count = sum(self.counts) * len(self.combiners)
        self.equality_count = sum(row.count for row in self.rows) * len(self.combiners)

    def unrank(self, rank):
        rank, combiner = divmod(rank, len(self.combiners))
        row, local = _select(self.counts, rank)
        pre, post = self.rows[row], self.posts[row]
        pre_rank, post_rank = divmod(local, post.count)
        q, twist = pre.unrank(pre_rank)
        return post.witness(Base(self.size, ODD_ODD, self.combiners[combiner], q, twist), post_rank)

    def unrank_equality(self, rank):
        rank, combiner = divmod(rank, len(self.combiners))
        row, local = _select(tuple(pre.count for pre in self.rows), rank)
        pre = self.rows[row]
        q, twist = pre.unrank(local)
        base = Base(self.size, ODD_ODD, self.combiners[combiner], q, twist)
        return Witness(base, 1, 1, base.K)


def _erased_power(size, t, q):
    w = valuation(q)
    width = 1 << (w + t)
    missing = valuation(size) + w - q
    return q + max(0, (missing + width - 1) // width) * width


def composed_sampler(size, sampling, combiner):
    """Identity-twist union over every pre-power in the erased tail or odd-odd MULT."""
    _check_side(size)
    if sampling == CHECKERBOARD and combiner in CHECKER_COMBINERS:
        q = _erased_power(size, valuation(size) - 2, 2)
    elif sampling == ODD_ODD and combiner == "mult":
        q = 2
    else:
        raise ValueError("Choose the erased checkerboard tail or odd-odd MULT.")
    return PostSampler(Base(size, sampling, combiner, q))


class TwistedTailOddPosts(Sampler):
    """Erased checkerboard tail with all pre-twists and odd post-powers."""

    def __init__(self, size, combiner):
        _check_side(size)
        if combiner not in CHECKER_COMBINERS:
            raise ValueError("Choose a surviving checkerboard tail combiner.")
        self.size = size
        self.combiner = combiner
        self.t = valuation(size) - 2
        self.rows = tuple(PreSpace(self.t, w, True) for w in range(1, max(1, self.t - 2) + 1))
        self.counts = tuple(pre.count for pre in self.rows)
        self.count = sum(self.counts)
        self.equality_count = 1

    def unrank(self, rank):
        row, local = _select(self.counts, rank)
        q, twist = self.rows[row].unrank(local)
        q = _erased_power(self.size, self.t, q)
        base = Base(self.size, CHECKERBOARD, self.combiner, q, twist)
        return Witness(base, 1, 1, base.K)

    def unrank_equality(self, rank):
        if rank != 0:
            raise ValueError("Rank is outside the equality-class space.")
        return self.unrank(0)


class OddProductRow(Sampler):
    """Odd-odd MULT with all pre-twists and post-powers at a fixed pre-valuation."""

    def __init__(self, size, w):
        _check_side(size)
        if w < 1:
            raise ValueError("Use a positive pre-valuation.")
        self.size = size
        self.pre = PreSpace(valuation(size) - 1, w, True)
        self.post = _unit_row(self.pre.T << self.pre.s, self.pre.s)
        self.equality_count = self.pre.count // (self.pre.T // 2)
        self.count = self.equality_count * self.post.count

    def unrank(self, rank):
        if not 0 <= rank < self.count:
            raise ValueError("Rank is outside the class space.")
        pre_rank, post_rank = divmod(rank, self.post.count)
        q, twist = self.pre.unrank(pre_rank, normalize=True)
        return self.post.witness(Base(self.size, ODD_ODD, "mult", q, twist), post_rank)

    def unrank_equality(self, rank):
        return self.unrank(rank * self.post.count)


def odd_linear_add_sampler(size):
    """Odd-odd ADD tail, including every pre-valuation w >= log2(size)-3."""
    _check_side(size)
    w = valuation(size) - 3
    return PostSampler(Base(size, ODD_ODD, "add", 1 << w))


class OddLinearClmulSampler(Sampler):
    """Odd-odd CLMUL tail, including every pre-valuation w >= log2(size)-3."""

    def __init__(self, size):
        _check_side(size)
        self.size = size
        self.T = size // 2
        self.w = valuation(size) - 3
        self.K = 2 * size << self.w
        self.s = self.w + 2
        reference_slope = (pow(5, 1 << self.w, self.K) - 1) >> self.s
        self.inverse_slope = pow(reference_slope, -1, self.T)
        self.equality_count = self.T // 4
        self.count = self.equality_count * (self.T // 2)

    def unrank(self, rank):
        if not 0 <= rank < self.count:
            raise ValueError("Rank is outside the class space.")
        pre, post = divmod(rank, self.T // 2)
        slope = 2 * pre + 1
        q = ((slope * self.inverse_slope) % self.T) << self.w
        return Witness(Base(self.size, ODD_ODD, "clmul", q), 1, 2 * post + 1, self.K)

    def unrank_equality(self, rank):
        return self.unrank(rank * (self.T // 2))


class TopBitHeadSampler(Sampler):
    """Checkerboard-opposite head whose surviving even branch is the top bit."""

    def __init__(self, size, combiner, *, twists=False):
        _check_side(size)
        if combiner not in CHECKER_COMBINERS:
            raise ValueError("Choose OR, XOR, ADD, or ABSDIFF.")
        r = valuation(size)
        self.t = r - 2
        self.T = 1 << self.t
        self.size = size
        self.combiner = combiner
        qs = tuple(r + w - 1 for w in range(1, r + 1) if valuation(r + w - 1) == w)
        if not qs:
            raise ValueError("This side has no pre-power with a top-bit even branch.")
        if (twists or combiner in ("or", "absdiff")) and valuation(qs[0]) + 2 < self.t - 2:
            raise ValueError("This full union needs the regime where the odd-branch twists are linear.")
        self.rows = []
        if combiner != "or":
            q = qs[0]
            w = valuation(q)
            post = _unit_row(size << w, w + 2, even=combiner == "absdiff")
            self.rows.append((q, 1, post))
        if combiner in ("or", "absdiff"):
            high_slopes = set()
            for q in qs:
                w = valuation(q)
                K, s = size << w, w + 2
                if s >= self.t:
                    # High rows are linear. A twisted row already contains every odd slope.
                    slope = 1 if twists else (pow(5, q, K) - 1) >> s
                    if slope in high_slopes:
                        continue
                    high_slopes.add(slope)
                post = _unit_row(K, s) if combiner == "or" else PostRow(4, 0, 1, 1, 1, 1)
                self.rows.append((q, self.T // 2 if twists else 1, post))
        self.equality_counts = tuple(slopes for _, slopes, _ in self.rows)
        self.counts = tuple(slopes * post.count for _, slopes, post in self.rows)
        self.count = sum(self.counts)
        self.equality_count = sum(self.equality_counts)

    def unrank(self, rank):
        row, local = _select(self.counts, rank)
        q, _, post = self.rows[row]
        slope_index, post_rank = divmod(local, post.count)
        twist = _twist_polynomial((slope_index,), valuation(q) + 2, self.t)
        return post.witness(Base(self.size, CHECKERBOARD, self.combiner, q, twist), post_rank)

    def unrank_equality(self, rank):
        row, local = _select(self.equality_counts, rank)
        return self.unrank(sum(self.counts[:row]) + local * self.rows[row][2].count)
