"""Cross-check direct samplers against small exhaustive unions and native fields."""

import json
from collections import Counter
from random import Random
from time import perf_counter

import numpy as np
from direct_sampler import (
    OddBitwiseSampler,
    OddLinearClmulSampler,
    OddProductRow,
    PostSampler,
    PreSpace,
    TopBitHeadSampler,
    TwistedTailOddPosts,
    composed_sampler,
    odd_linear_add_sampler,
)
from precision import checkerboard_twists, moduli, odd_twists, preserving_unit_powers
from study import (
    CHECKER_COMBINERS,
    CHECKERBOARD,
    ODD_COMBINERS,
    ODD_ODD,
    Base,
    Witness,
    catalogues,
    checkerboard_tail_prepowers,
    nonunit_order_powers,
    partition,
    postpowers,
    valuation,
)
from verify import HERE
from verify_precision import twist_action


def anchored(values, anchor, p, a, M):
    start = pow(anchor, p, M)
    residues = tuple((a * (pow(z, p, M) - start)) % M for z in values)
    shift = min(valuation(z) for z in residues if z)
    return M >> shift, tuple(z >> shift for z in residues)


def conditional_key(witness):
    values, indices = witness.base.labels
    anchor = values[indices[0, 0]]
    return anchored(values, anchor, witness.p, witness.a, witness.modulus)


def order_key(residues):
    return np.unique(np.array(residues), return_inverse=True)[1].astype(np.uint32).tobytes()


def exhaustive_post(base, selector, powers):
    values, indices = base.labels
    anchor = values[indices[0, 0]]
    result = set()
    for p in powers:
        M = getattr(moduli(base, p), selector)
        width, output = anchored(values, anchor, p, 1, M)
        for a in range(1, width, 2):
            result.add((width, tuple(a * z % width for z in output)))
    return result


def check_conditional():
    checked = 0
    for N in (16, 32, 64):
        for sampling, combiners in ((CHECKERBOARD, CHECKER_COMBINERS), (ODD_ODD, ODD_COMBINERS)):
            for c in combiners:
                for q, Q in ((2, ()), (2, (1,)), (4, (-3, 2)), (6, ()), (16, (1,))):
                    base = Base(N, sampling, c, q, Q)
                    nonunit = sampling == ODD_ODD and c in ("xor", "absdiff")
                    sampler = PostSampler(base, odd_powers_only=nonunit)
                    powers = tuple(p for p in nonunit_order_powers(base) if p % 2) if nonunit else postpowers(base)
                    reference = exhaustive_post(base, "minimum_period", powers)
                    direct = {conditional_key(sampler.unrank(rank)) for rank in range(sampler.count)}
                    assert direct == reference and len(direct) == sampler.count, base
                    assert len({order_key(values) for _, values in direct}) == sampler.count, base
                    expected_partitions = {partition(values).tobytes() for _, values in direct}
                    actual_partitions = {
                        partition(conditional_key(sampler.unrank_equality(i))[1]).tobytes()
                        for i in range(sampler.equality_count)
                    }
                    assert actual_partitions == expected_partitions and len(actual_partitions) == sampler.equality_count
                    checked += len(reference)

    for N in (16, 32):
        for sampling, combiners in (
            (CHECKERBOARD, CHECKER_COMBINERS),
            (ODD_ODD, ("and", "or", "add")),
        ):
            for c in combiners:
                for q, Q in ((2, ()), (2, (1,)), (4, (-3, 2)), (16, (1,))):
                    base = Base(N, sampling, c, q, Q)
                    sampler = PostSampler(base, "distinct_outputs")
                    reference = exhaustive_post(base, "distinct_outputs", preserving_unit_powers(base))
                    direct = {conditional_key(sampler.unrank(rank)) for rank in range(sampler.count)}
                    assert direct == reference and len(direct) == sampler.count, base
                    checked += len(reference)
    return checked


def pre_units(t, q, Q):
    s = valuation(q) + 2
    K = 1 << (t + s)
    root = pow(5, q, K)
    values = tuple(pow(root, j, K) for j in range(1 << t))
    return twist_action(values, Q, K)


def exhaustive_pre(t, w, twists):
    return {
        pre_units(t, u << w, Q)
        for u in range(1, 1 << t, 2)
        for Q in (odd_twists(1 << (t + 1), u << w) if twists else ((),))
    }


def check_pre_spaces():
    total = 0
    for t in range(2, 8):
        T = 1 << t
        for w in range(1, t + 1):
            for twists in (False, True):
                pre = PreSpace(t, w, twists)
                expected = exhaustive_pre(t, w, twists)
                actual = {pre_units(t, *pre.unrank(rank)) for rank in range(pre.count)}
                assert actual == expected and len(actual) == pre.count, (t, w, twists)
                count = pre.count // (T // 2)
                norm = {pre_units(t, *pre.unrank(rank, normalize=True)) for rank in range(count)}
                K = T << pre.s
                first = pow(5, 1 << w, K)
                expected_norm = {a for a in expected if a[1] == first}
                assert norm == expected_norm and len(norm) == count, (t, w, twists)
                total += len(expected)
    return total


def raw_array(values, combiner):
    values = np.asarray(values, dtype=np.int64)
    if combiner == "and":
        return values[:, None] & values[None, :]
    if combiner == "or":
        return values[:, None] | values[None, :]
    if combiner == "add":
        return values[:, None] + values[None, :]
    if combiner == "mult":
        return values[:, None] * values[None, :]
    # CLMUL here is limited to the high pre-valuation tail at minimum precision.
    return 1 + ((values[:, None] - 1) ^ (values[None, :] - 1))


def post_key(raw, p, a, M, T):
    values, inverse = np.unique(raw, return_inverse=True)
    z0 = pow(int(raw.flat[0]), p, M)
    residues = [(a * (pow(int(z), p, M) - z0)) % M for z in values]
    assert all(z % (M // T) == 0 for z in residues)
    levels = np.asarray([z // (M // T) for z in residues], dtype=np.uint32)
    return levels[inverse.ravel()].tobytes()


def union_witness_key(witness):
    base = witness.base
    T = base.size // (4 if base.sampling == CHECKERBOARD else 2)
    values = pre_units(valuation(T), base.q, base.twist)
    raw = np.asarray(values) if base.sampling == CHECKERBOARD else raw_array(values, base.combiner)
    return post_key(raw, witness.p, witness.a, witness.modulus, T)


def exhaustive_union(base, ws, *, twists=False, odd_posts=False):
    T = base.size // (4 if base.sampling == CHECKERBOARD else 2)
    t = valuation(T)
    reference = set()
    for w in ws:
        q = (
            next(q for q in checkerboard_tail_prepowers(base.size) if valuation(q) == w)
            if base.sampling == CHECKERBOARD
            else 1 << w
        )
        trial = Base(base.size, base.sampling, base.combiner, q)
        for values in exhaustive_pre(t, w, twists):
            raw = np.asarray(values) if base.sampling == CHECKERBOARD else raw_array(values, base.combiner)
            for p in postpowers(trial):
                if odd_posts and p % 2 == 0:
                    continue
                M = moduli(trial, p).minimum_period
                for a in range(1, T, 2):
                    reference.add(post_key(raw, p, a, M, T))
    return reference


def check_unions():
    checked = 0
    for N in (16, 32, 64):
        t = valuation(N) - 1
        for c in ("and", "or"):
            for twists in (False, True):
                base = Base(N, ODD_ODD, c, 2)
                sampler = OddBitwiseSampler(N, (c,), twists=twists)
                keys = {union_witness_key(sampler.unrank(i)) for i in range(sampler.count)}
                expected = exhaustive_union(base, range(1, t), twists=twists)
                assert keys == expected and len(keys) == sampler.count, (N, c, twists)
                partitions = {partition(np.frombuffer(key, dtype=np.uint32)).tobytes() for key in keys}
                equality = {
                    partition(np.frombuffer(union_witness_key(sampler.unrank_equality(i)), dtype=np.uint32)).tobytes()
                    for i in range(sampler.equality_count)
                }
                assert equality == partitions and len(equality) == sampler.equality_count
                checked += len(keys)

        for w in (1, 2):
            sampler = OddProductRow(N, w)
            keys = {union_witness_key(sampler.unrank(i)) for i in range(sampler.count)}
            expected = exhaustive_union(Base(N, ODD_ODD, "mult", 1 << w), (w,), twists=True)
            assert keys == expected and len(keys) == sampler.count, (N, w)
            checked += len(keys)

        for c in ("add", "clmul"):
            sampler = odd_linear_add_sampler(N) if c == "add" else OddLinearClmulSampler(N)
            keys = {union_witness_key(sampler.unrank(i)) for i in range(sampler.count)}
            expected = exhaustive_union(Base(N, ODD_ODD, c, 1 << (t - 2)), range(t - 2, t + 1), twists=True)
            assert keys == expected and len(keys) == sampler.count, (N, c)
            checked += len(keys)

        for sampling, c in ((CHECKERBOARD, "xor"), (ODD_ODD, "mult")):
            sampler = composed_sampler(N, sampling, c)
            keys = {union_witness_key(sampler.unrank(i)) for i in range(sampler.count)}
            ws = (
                tuple(sorted({valuation(q) for q in checkerboard_tail_prepowers(N)}))
                if sampling == CHECKERBOARD
                else range(1, t)
            )
            expected = exhaustive_union(sampler.base, ws)
            assert keys == expected and len(keys) == sampler.count, (N, c)
            checked += len(keys)

        sampler = TwistedTailOddPosts(N, "xor")
        ws = tuple(sorted({valuation(q) for q in checkerboard_tail_prepowers(N)}))
        keys = {union_witness_key(sampler.unrank(i)) for i in range(sampler.count)}
        expected = exhaustive_union(composed_sampler(N, CHECKERBOARD, "xor").base, ws, twists=True, odd_posts=True)
        assert keys == expected and len(keys) == sampler.count
        checked += len(keys)
    return checked


def check_top_bit_head():
    N, qs = 64, (6, 8)
    total = 0
    for c in CHECKER_COMBINERS:
        for twists in (False, True):
            bases = [
                Base(N, CHECKERBOARD, c, q, Q) for q in qs for Q in (checkerboard_twists(N, q) if twists else ((),))
            ]
            reference = catalogues(bases, postpowers, retain_shifts=False)
            # Compare full spatial signatures, including the native checkerboard orientation.
            expected = set()
            for witness in reference["order"].values():
                residues = conditional_key(witness)[1]
                expected.add(order_key(np.asarray(residues)[witness.base.labels[1].ravel()]))
            expected_partitions = {partition(np.frombuffer(key, dtype=np.uint32)).tobytes() for key in expected}
            sampler = TopBitHeadSampler(N, c, twists=twists)
            actual = set()
            for i in range(sampler.count):
                witness = sampler.unrank(i)
                residues = conditional_key(witness)[1]
                actual.add(order_key(np.asarray(residues)[witness.base.labels[1].ravel()]))
            assert actual == expected and len(actual) == sampler.count, (c, twists)
            equality = set()
            for i in range(sampler.equality_count):
                witness = sampler.unrank_equality(i)
                residues = conditional_key(witness)[1]
                equality.add(partition(np.asarray(residues)[witness.base.labels[1].ravel()]).tobytes())
            assert equality == expected_partitions and len(equality) == sampler.equality_count, (c, twists)
            total += len(expected)
    return total


def check_native():
    from ruglab.engine import evaluate

    rng = Random(101)
    checked = 0
    for N in (16, 32, 64, 128):
        samplers = (
            OddBitwiseSampler(N, twists=True),
            composed_sampler(N, CHECKERBOARD, "absdiff"),
            composed_sampler(N, ODD_ODD, "mult"),
            TwistedTailOddPosts(N, "add"),
            OddProductRow(N, 1),
            OddLinearClmulSampler(N),
            odd_linear_add_sampler(N),
        )
        for sampler in samplers:
            for _ in range(4):
                witness = sampler.draw(rng)
                phase = rng.randrange(witness.modulus)
                result = evaluate(witness.spec(phase))
                original = evaluate(witness.spec()).values
                assert np.array_equal((original + phase) % witness.modulus, result.values)
                assert witness.base.minimum(witness.p) == witness.modulus
                denominator, outputs = conditional_key(witness)
                raw = witness.base.labels[1]
                actual = (result.values - result.values[0, 0]) % witness.modulus
                expected = np.asarray(outputs, dtype=object)[raw] * (witness.modulus // denominator)
                assert np.array_equal(actual, expected)
                checked += 1
        for c in ("mult", "clmul"):
            # Large selectors: match the independently derived order of the unit root on reachable values.
            base = Base(N, ODD_ODD, c, 2, (1, 2))
            sampler = PostSampler(base, "catalogue")
            for p in (1, 2, 3, 4, 7, 16, 64, 125, 256):
                a = 2 * rng.randrange(sampler.rows[0].multiplier_choices) + 1
                M = moduli(base, p).catalogue
                row = sampler.rows[0]
                canonical = ((p - 1) % row.power_choices) + 1
                actual = Witness(base, p, a, M)
                # A change of post-valuation can change the first geometric difference by an odd unit.
                s = valuation(base.q) + 2
                eta = (pow(1 << s | 1, p, M) - 1) >> (s + valuation(p))
                C = moduli(base, canonical).catalogue
                eta0 = (pow(1 << s | 1, canonical, C) - 1) >> (s + valuation(canonical))
                width = row.multiplier_choices * 2
                corrected = a * eta * pow(eta0, -1, width) % width
                assert conditional_key(actual) == conditional_key(Witness(base, canonical, corrected, C))
                checked += 1
    return checked


def preserving_order_collision():
    base = Base(16, CHECKERBOARD, "absdiff", 4)
    M = moduli(base, 1).distinct_outputs
    first, second = (conditional_key(Witness(base, 1, a, M)) for a in (1, 5))
    assert first != second and order_key(first[1]) == order_key(second[1])
    sampler = PostSampler(base, "distinct_outputs")
    orders = Counter(order_key(conditional_key(sampler.unrank(i))[1]) for i in range(sampler.count))
    multiplicities = dict(sorted(Counter(orders.values()).items()))
    assert multiplicities == {1: 2, 4: 6, 5: 2}
    return {
        "side": base.size,
        "pre_power": base.q,
        "post_power": 1,
        "modulus": M,
        "raw_labels": base.labels[0],
        "normalized_denominator": first[0],
        "order_counts_by_shift_multiplicity": multiplicities,
        "anchored_numerators_by_multiplier": {1: first[1], 5: second[1]},
    }


def main():
    results = {
        "conditional_classes_checked": check_conditional(),
        "pre_map_classes_checked": check_pre_spaces(),
        "cross_base_classes_checked": check_unions(),
        "top_bit_head_classes_checked": check_top_bit_head(),
        "side_64_top_bit_head_counts_with_twists": {
            c: {
                "orders": TopBitHeadSampler(64, c, twists=True).count,
                "equalities": TopBitHeadSampler(64, c, twists=True).equality_count,
            }
            for c in CHECKER_COMBINERS
        },
        "native_and_large_precision_checks": check_native(),
        "preserving_order_collision": preserving_order_collision(),
    }
    results["class_counts"] = {
        N: {
            "odd_odd_and_or_all_twists": OddBitwiseSampler(N, twists=True).count,
            "odd_odd_and_or_identity": OddBitwiseSampler(N).count,
            "erased_checkerboard_tail_identity": composed_sampler(N, CHECKERBOARD, "xor").count,
            "erased_checkerboard_tail_twists_odd_posts": TwistedTailOddPosts(N, "xor").count,
            "odd_odd_mult_identity": composed_sampler(N, ODD_ODD, "mult").count,
            "odd_odd_mult_w1_all_twists": OddProductRow(N, 1).count,
            "odd_odd_linear_pre_add": odd_linear_add_sampler(N).count,
            "odd_odd_linear_pre_clmul": OddLinearClmulSampler(N).count,
        }
        for N in (16, 32, 64, 128, 256, 4096)
    }
    (HERE / "direct-results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    sampler, rng = OddBitwiseSampler(4096, twists=True), Random(0)
    start = perf_counter()
    for _ in range(10_000):
        sampler.draw(rng)
    print(f"Side-4096 odd-odd AND/OR, 10,000 independent draws: {perf_counter() - start:.3f} s")


if __name__ == "__main__":
    main()
