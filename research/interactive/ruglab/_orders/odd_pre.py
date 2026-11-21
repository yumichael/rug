"""Exact coordinates for shared pre-maps on an odd operand coset."""

from math import comb


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


class OddPreSpace:
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
