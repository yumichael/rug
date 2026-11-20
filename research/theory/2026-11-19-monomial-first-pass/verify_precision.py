"""Reproduce modulus proofs, complete twist comparisons, and the selector atlas."""

import argparse
import json
from dataclasses import asdict
from random import Random

import numpy as np
from precision import checkerboard_twists, moduli, odd_twists, preserving_unit_powers
from ruglab._orders.core import poly
from ruglab.engine import evaluate
from ruglab.exploration import PatternRecipe, _distinct_powers, _minimum_group_values, sample_field
from study import (
    CHECKER_COMBINERS,
    CHECKERBOARD,
    ODD_COMBINERS,
    ODD_COSETS,
    ODD_ODD,
    Base,
    catalogues,
    checkerboard_groups,
    joint_positions,
    partition,
    postpowers,
    valuation,
)
from verify import HERE, measure, render

POWERS = (1, 2, 3, 4, 8, 16)


def check_recipe(base, p):
    expected = moduli(base, p)
    residues, catalogue = _distinct_powers(np.asarray(base.labels[0], dtype=np.int64), p)
    _, distinct = _minimum_group_values(residues, catalogue)
    assert (base.minimum(p), distinct, catalogue) == tuple(asdict(expected).values()), (base, p, expected)
    return expected


def check_workbench():
    total = 0
    for N in (16, 64, 128):
        for name, combiners in ((CHECKERBOARD, CHECKER_COMBINERS), (ODD_ODD, ODD_COMBINERS)):
            for c in combiners:
                for q in (2, 4, 8, 16, 32):
                    for twist in (0, -3, 1):
                        base = Base(N, name, c, q, (twist,) if twist else ())
                        for p in (1, 2, 7):
                            recipe = PatternRecipe(c, q, twist, p)
                            for selection, M in asdict(moduli(base, p)).items():
                                workbench = sample_field(recipe, N, name, m_selection=selection)
                                assert workbench.spec["M"] == M, (base, p, selection)
                                assert np.array_equal(workbench.values.expand(), evaluate(base.spec(p, 1, M)).values)
                                total += 1
    return total


def labels_at(base, p, M, a=1):
    return np.asarray([a * pow(z, p, M) % M for z in base.labels[0]], dtype=object)


def check_and_count_twists(N, name, c, q):
    twists = checkerboard_twists(N, q) if name == CHECKERBOARD else odd_twists(N, q)
    base_partitions = set()
    min_partitions = {p: set() for p in POWERS}
    identity = Base(N, name, c, q)
    for Q in twists:
        base = Base(N, name, c, q, Q)
        values, indices = base.labels
        base_partitions.add(partition(indices.ravel()).astype(np.uint16).tobytes())
        if name == ODD_ODD:
            assert values == identity.labels[0]
            assert np.array_equal(np.bincount(indices.ravel()), np.bincount(identity.labels[1].ravel()))
        for p in POWERS:
            M = check_recipe(base, p).minimum_period
            levels = labels_at(base, p, M)
            key = partition(levels[indices.ravel()]).astype(np.uint16).tobytes()
            min_partitions[p].add(key)
    return {
        "twist_actions": len(twists),
        "distinct_and_catalogue_partitions": len(base_partitions),
        "minimum_period_partitions_by_p": {p: len(keys) for p, keys in min_partitions.items()},
    }


def exact_twists(N):
    summary = {}
    for name, combiners in ((CHECKERBOARD, CHECKER_COMBINERS), (ODD_ODD, ODD_COMBINERS)):
        powers = (
            tuple(q for _, group in checkerboard_groups(N) for q in group)
            if name == CHECKERBOARD
            else (2, 4, 6, 8, 16, 32)
        )
        summary[name] = {q: {c: check_and_count_twists(N, name, c, q) for c in combiners} for q in powers}
    return summary


def twist_action(values, Q, K):
    return tuple((z + 2 * z * (z - 1) * poly(Q, z, K)) % K for z in values)


def check_twist_coordinates():
    rng = Random(774)
    total = 0
    for N in (16, 32, 64, 128):
        for q in (2, 4, 6, 8, 16):
            base = Base(N, ODD_ODD, "or", q)
            values = range(1, base.K, 1 << (valuation(q) + 2))

            reps = odd_twists(N, q)
            signatures = {twist_action(values, Q, base.K) for Q in reps}
            assert len(signatures) == len(reps)
            for _ in range(32):
                Q = tuple(rng.randrange(-30, 31) for _ in range(11))
                assert twist_action(values, Q, base.K) in signatures
                total += 1
    return total


def operand_sequences(N, w, sampling):
    tail = sampling == CHECKERBOARD
    K = (N if tail else 2 * N) << w
    T = N // (4 if tail else 2)
    make_twists = checkerboard_twists if tail else odd_twists
    plain, twisted = set(), set()
    for u in range(1, T, 2):
        q = u << w
        while tail and q < valuation(K):
            q += T << w
        raw = tuple(pow(2 * i + 1, q, K) for i in range(N))
        plain.add(raw)
        for Q in make_twists(N, q):
            twisted.add(twist_action(raw, Q, K))
    assert plain <= twisted
    if w + 2 >= valuation(T) - 1:
        assert plain == twisted
    return plain, twisted


def operand_coverage(N, sampling):
    """Count operand sequences before and after adding twists to the full odd-part cycle."""
    results = {}
    for w in range(1, valuation(N)):
        plain, twisted = operand_sequences(N, w, sampling)
        results[w] = {"vary_pre_power": len(plain), "vary_pre_power_and_twist": len(twisted)}
    return results


def odd_odd_spatial_coverage():
    N, w = 64, 1
    plain, twisted = operand_sequences(N, w, ODD_ODD)
    identity = tuple(pow(2 * i + 1, 1 << w, 2 * N << w) for i in range(N))
    positions = {value: i for i, value in enumerate(identity)}
    results = {}
    for c in ODD_COMBINERS:
        base = Base(N, ODD_ODD, c, 1 << w)
        counts = results[c] = {}
        for name, M in (
            ("minimum_period", moduli(base, 1).minimum_period),
            ("distinct_outputs_and_catalogue", moduli(base, 1).catalogue),
        ):
            tile = base.field % M

            def keys(sequences, tile):
                result = set()
                for sequence in sequences:
                    axes = [positions[value] for value in sequence]
                    field = tile[np.ix_(axes, axes)]
                    result.add(partition(field.ravel()).astype(np.uint16).tobytes())
                return result

            counts[name] = {
                "vary_pre_power": len(keys(plain, tile)),
                "vary_pre_power_and_twist": len(keys(twisted, tile)),
            }
    return results


def order_pilot():
    """Exact all-power order unions for unit cases at fixed N and q."""
    N, q = 16, 2

    def keep(base, p):
        return moduli(base, p).distinct_outputs

    results = {}
    rng = Random(331)
    for sampling, combiners in ((CHECKERBOARD, CHECKER_COMBINERS), (ODD_ODD, ODD_COMBINERS)):
        output = results[sampling] = {}
        for c in combiners:
            twists = checkerboard_twists(N, q) if sampling == CHECKERBOARD else odd_twists(N, q)
            unit = sampling == CHECKERBOARD or c in ODD_COSETS
            if unit:
                min_powers, keep_powers = postpowers, preserving_unit_powers
            else:
                # Shared finite power range for the comparison of the two selector supports.
                min_powers = keep_powers = lambda _: (1, 2, 3, 4)
            for use_twists in (False, True):
                bases = [Base(N, sampling, c, q, Q) for Q in (twists if use_twists else ((),))]
                minimum = catalogues(bases, min_powers, retain_shifts=False)["order"]
                preserving = catalogues(bases, keep_powers, modulus=keep, retain_shifts=False)["order"]
                if unit:
                    base = bases[-1]
                    reference = catalogues([base], keep_powers, modulus=keep, retain_shifts=False)["order"]
                    for p in (17, 33, 64, 96, 129):
                        M = keep(base, p)
                        a = 2 * rng.randrange(M // 2) + 1
                        values = evaluate(base.spec(p, a, M)).values
                        residues = (values.ravel()[joint_positions([base])] - values[0, 0]) % M
                        ranks = np.unique(residues, return_inverse=True)[1].astype(np.uint32).tobytes()
                        assert ranks in reference, (base, p, M)
                output.setdefault(c, {"post_powers": "all" if unit else [1, 2, 3, 4]})
                output[c]["all_twists" if use_twists else "identity"] = {
                    "minimum_period": len(minimum),
                    "distinct_outputs_and_catalogue": len(preserving),
                    "shared": len(minimum.keys() & preserving.keys()),
                }
    return results


def selector_atlas(figures):
    N = 64
    cases = (
        (CHECKERBOARD, "add", 2, 1),
        (CHECKERBOARD, "absdiff", 2, 1),
        (ODD_ODD, "xor", 2, 3),
        (ODD_ODD, "mult", 16, 1),
        (ODD_ODD, "clmul", 16, 1),
    )
    results, rows = [], []
    for sampling, combiner, q, p in cases:
        minimum_and_preserving = []
        stats = {"sampling": sampling, "combiner": combiner, "q": q, "p": p}
        for Q in ((), (1,)):
            base = Base(N, sampling, combiner, q, Q)
            choices = moduli(base, p)
            label = "Q = 1" if Q else "Identity"
            stats[label] = {}
            for method, M in (("Minimum period", choices.minimum_period), ("Distinct / Catalogue", choices.catalogue)):
                spec = base.spec(p, 1, M)
                name = "Checkerboard" if sampling == CHECKERBOARD else "Odd-odd"
                minimum_and_preserving.append((f"{name} {combiner.upper()} · {label}\n{method}, M = {M:,}", spec))
                stats[label][method] = {"M": M, **measure(spec)[1]}
        rows.append(minimum_and_preserving)
        results.append(stats)
    if figures:
        render(rows, "Modulus selectors and pre-twists · side 64", HERE / "selectors-and-twists.png")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-figure", action="store_true")
    args = parser.parse_args()
    workbench_checks = check_workbench()
    twist_counts = exact_twists(64)
    twist_checks = len(POWERS) * sum(
        c["twist_actions"] for sampling in twist_counts.values() for q in sampling.values() for c in q.values()
    )
    results = {
        "side_for_complete_twist_catalogues": 64,
        "post_powers_for_exhaustive_twist_modulus_checks": POWERS,
        "workbench_recipe_and_selector_checks": workbench_checks,
        "all_twists_modulus_triples_checked": twist_checks,
        "fixed_pre_power_twist_counts": twist_counts,
        "odd_odd_twist_coordinate_checks": check_twist_coordinates(),
        "odd_odd_operand_coverage": {N: operand_coverage(N, ODD_ODD) for N in (32, 64, 128)},
        "checkerboard_tail_operand_coverage": {N: operand_coverage(N, CHECKERBOARD) for N in (32, 64, 128)},
        "side_64_odd_odd_spatial_coverage_at_post_1_and_pre_valuation_1": odd_odd_spatial_coverage(),
        "side_16_pre_2_order_pilot": order_pilot(),
        "side_64_atlas_metrics": selector_atlas(not args.skip_figure),
    }
    (HERE / "selector-results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"{workbench_checks:,} workbench selector checks and {twist_checks:,} all-twist modulus triples")


if __name__ == "__main__":
    main()
