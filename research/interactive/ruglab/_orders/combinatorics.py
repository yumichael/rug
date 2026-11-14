"""Draw helpers from the November 12 component-order sampler."""


def pick(rng, choices):
    choices = [(item, weight) for item, weight in choices if weight]
    choice = rng.randrange(sum(weight for _, weight in choices))
    for item, weight in choices:
        if choice < weight:
            return item
        choice -= weight
    raise AssertionError


def admissible(rank, components):
    partners = {}
    for group in components:
        values = {rank[i] for i in group}
        if len(values) > 2:
            return False
        if len(values) == 2:
            a, b = values
            if partners.get(a, b) != b or partners.get(b, a) != a:
                return False
            partners[a], partners[b] = b, a
    if not partners:
        return False
    sequence = sorted(partners)
    half = len(sequence) // 2
    return all(partners[a] == b for a, b in zip(sequence[:half], sequence[half:], strict=True))
