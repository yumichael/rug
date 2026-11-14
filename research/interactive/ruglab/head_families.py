"""Competing exhaustive head-family proposals based on the existing research."""

from dataclasses import dataclass
from functools import lru_cache, reduce
from operator import or_
from random import Random

from .order_classes import ORDER_COMBINERS, OrderClassRecipe, _basic, head_powers

PROPOSALS = {
    "bit_depth": "Bit depth",
    "even_branch": "Even branch",
    "half_period_graph": "Half-period graph",
    "carry_behavior": "Carry behavior",
    "or_twist_mask": "OR twist mask",
}


@lru_cache(maxsize=256)
def head_family_keys(size, power, twist, combiner):
    """Classify any allowed head base; no restriction on the twist coefficients."""
    if power not in head_powers(size) or combiner not in ORDER_COMBINERS:
        raise ValueError("Choose a head pre-power and OR, XOR, ADD, or ABSDIFF")
    basic = _basic(size, power, twist, combiner)
    width = (power & -power).bit_length() - 1
    depth = power - width - 2
    depth_key = (
        "Low-bit crossing"
        if depth < 0
        else ("Stride boundary" if depth == 0 else "Middle-bit modulation" if depth <= 3 else "Deep-bit modulation")
    )
    even = set(basic.pre[::2])
    nonzero = even - {0}
    layers = {int(v & -v).bit_length() - 1 for v in nonzero}
    if len(even) == 2:
        branch = "Top-bit binary" if basic.K // 2 in nonzero else "Interior-bit binary"
    else:
        branch = "One-layer multilevel" if len(layers) == 1 else "Multiple even layers"
    sizes = tuple(map(len, basic.components))
    if max(sizes) > 2:
        graph = "Linked components"
    elif min(sizes) == 1:
        graph = "Pairs plus singletons"
    else:
        graph = "Tail-count pairs" if len(basic.nodes) == size // 4 else "Expanded pairs"
    overlaps = bool(reduce(or_, basic.pre[1::2], 0) & reduce(or_, even, 0))
    if combiner == "absdiff":
        carry = "Folded differences"
    elif not overlaps:
        carry = "Carry-free merge"
    else:
        carry = {"or": "Saturating bits", "xor": "Toggling bits", "add": "Carrying sums"}[combiner]
    if power == 2 and combiner == "or":
        forced = (-(twist[0] if twist else 0) % 4).bit_count()
        mask = f"OR: {forced} forced bits" if size >= 32 else "Small-domain OR"
    else:
        mask = "Other low-bit bases" if power == 2 else "Higher-power bases"
    return dict(zip(PROPOSALS, (depth_key, branch, graph, carry, mask), strict=True))


@dataclass(frozen=True)
class HeadFamilyCase:
    proposal: str
    category: str
    size: int
    members: tuple[tuple[int, tuple[int, ...], str], ...]

    def __str__(self):
        return f"{PROPOSALS[self.proposal]}: {self.category}"

    def recipe(self, seed, draw):
        power, twist, combiner = self.members[draw % len(self.members)]
        # Each base's first sampled order is the same in every proposal.
        return OrderClassRecipe(
            "head",
            seed,
            draw // len(self.members),
            power,
            twist,
            combiner,
            proposal=self.proposal,
            candidate_family=self.category,
            proposal_size=self.size,
            preview_example=draw,
        )


def head_family_cases(size=64, seed=0, twists=((), (1,), (3, -2, 1)), proposals=tuple(PROPOSALS)):
    """Finite representative bases grouped under universal family definitions."""
    if size < 8 or size > 4096 or size & (size - 1):
        raise ValueError("Choose a power-of-two side from 8 to 4096")
    if not proposals or set(proposals) - PROPOSALS.keys():
        raise ValueError("Choose at least one known head-family proposal")
    bases = [(q, tuple(Q), c) for q in head_powers(size) for Q in twists for c in ORDER_COMBINERS]
    if not bases:
        raise ValueError("Supply at least one twist polynomial")
    Random(f"head-family-bases:{seed}:{size}").shuffle(bases)
    result = []
    for proposal in proposals:
        groups = {}
        for base in bases:
            category = head_family_keys(size, *base)[proposal]
            groups.setdefault(category, []).append(base)
        for category, members in sorted(groups.items()):
            result.append(HeadFamilyCase(proposal, category, size, tuple(members)))
    return tuple(result)


def audit_head_family_proposals(sizes=(8, 16, 32, 64, 128, 256, 512), seed=0, twists=((), (1,), (3, -2, 1))):
    """Bounded coverage and identical-raw-partition overlap audit, not a visual score."""
    import numpy as np

    from .order_classes import _indices

    records = []
    for size in sizes:
        cases = head_family_cases(size, seed, twists)
        bases = list(dict.fromkeys(base for case in cases for base in case.members))
        partitions = {}
        for power, twist, combiner in bases:
            indices = _indices(size, power, twist, combiner)
            _, first = np.unique(indices, return_index=True)
            labels = indices.ravel()[np.sort(first)]
            remap = np.empty(int(indices.max()) + 1, dtype=np.uint32)
            remap[labels] = np.arange(len(labels), dtype=np.uint32)
            partitions.setdefault(remap[indices].tobytes(), []).append((power, twist, combiner))
        proposals = {}
        for proposal in PROPOSALS:
            crossing = sum(
                len({head_family_keys(size, *base)[proposal] for base in group}) > 1 for group in partitions.values()
            )
            proposals[proposal] = {
                "families": {case.category: len(case.members) for case in cases if case.proposal == proposal},
                "raw_partitions_crossing_families": crossing,
            }
        records.append(
            {"side": size, "bases": len(bases), "distinct_raw_partitions": len(partitions), "proposals": proposals}
        )
    return {"seed": seed, "twists": [list(q) for q in twists], "domain_checks": records}
