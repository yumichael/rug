"""Verify formulas against native fields and build the first-pass atlas."""

import argparse
import json
from pathlib import Path
from random import Random

import numpy as np

from ruglab.engine import evaluate
from ruglab.sampler_comparison import base_pool, power_groups

from study import (
    CHECKER_COMBINERS,
    CHECKERBOARD,
    ODD_COMBINERS,
    ODD_COSETS,
    ODD_ODD,
    Base,
    catalogues,
    checkerboard_groups,
    checkerboard_tail_prepowers,
    draw,
    nonunit_order_powers,
    joint_positions,
    odd_odd_prepowers,
    odd_odd_tail,
    postpowers,
    valuation,
)

HERE = Path(__file__).resolve().parent
POWERS = tuple(range(1, 9))


def expected(base, p):
    w, v = valuation(base.q), valuation(p)
    s = 1 << (w + 2)
    t = base.size // 2
    if base.sampling == CHECKERBOARD:
        if base.combiner == "absdiff" and p % 2 and base.q < valuation(base.K):
            return 4, 2
        return base.K << v, base.K >> min(base.q, w + 2)
    if base.combiner == "add":
        return base.K << (p - 1 + v), t
    if base.combiner in ODD_COSETS:
        return base.K << v, t
    if base.combiner == "absdiff" and p % 2:
        return 4 * s**p, 4 if p == 1 else 3
    return (s**p * t) << v, None


def check_fields(size):
    checked = 0
    for name, combiners, powers in (
        (CHECKERBOARD, CHECKER_COMBINERS, [q for _, qs in checkerboard_groups(size) for q in qs]),
        (ODD_ODD, ODD_COMBINERS, None),
    ):
        for c in combiners:
            chosen = powers if powers is not None else (
                u << w for w, _ in odd_odd_prepowers(size, c) for u in (1, 3, 5)
            )
            for q in chosen:
                base = Base(size, name, c, q)
                for p in (*POWERS, 11, 16, 24, 33, 64):
                    M = base.minimum(p)
                    modulus, coset_size = expected(base, p)
                    assert modulus is None or M == modulus, (base, p, M, modulus)
                    values = evaluate(base.spec(p, 3, M)).values
                    lower = values % (M // 2)
                    half = size // 2
                    assert all(not np.array_equal(values, np.roll(values, half, axis)) for axis in (0, 1))
                    assert any(np.array_equal(lower, np.roll(lower, half, axis)) for axis in (0, 1))
                    if coset_size is not None:
                        assert len(np.unique(values)) == coset_size, (base, p, M)
                        if not (c == "absdiff" and p > 1):
                            assert all((x - values[0, 0]) % (M // coset_size) == 0 for x in values.flat)
                    if name == CHECKERBOARD or c in ODD_COSETS:
                        candidates = postpowers(base)
                        if name == CHECKERBOARD and c == "absdiff" and M == 4:
                            representative = 1
                        else:
                            bits = valuation(coset_size)
                            s = valuation(M) - bits - valuation(p)
                            if c == "add" and name == ODD_ODD:
                                s -= p
                            start = int(name == CHECKERBOARD and c == "absdiff" and q < valuation(base.K))
                            v = min(valuation(p), max(start, bits - s + 1))
                            u = (p >> valuation(p)) % coset_size
                            representative = (1 << v) * u
                        assert representative in candidates
                        assert base.effective_values(representative) == base.effective_values(p)
                    checked += 1

    for c in ODD_COMBINERS:
        cutoff = odd_odd_tail(size, c)
        for u in (1, 3, size // 2 + 3):
            before = Base(size, ODD_ODD, c, u << cutoff)
            for p in (1, 2, 3, 8):
                def effective_field(base):
                    outputs, modulus = base.effective_values(p)
                    return np.asarray(outputs)[base.labels[1]], modulus

                reference, modulus = effective_field(before)
                for q in (u << (cutoff + 1), (u + size // 2) << cutoff):
                    values, other_modulus = effective_field(Base(size, ODD_ODD, c, q))
                    assert modulus == other_modulus and np.array_equal(values, reference), (size, c, u, p, q)
                    checked += 1
    return checked


def measure(spec):
    result = evaluate(spec)
    residues, counts = np.unique(result.values, return_counts=True)
    M = result.modulus
    gaps = [int(b - a) for a, b in zip(residues, residues[1:])]
    return result, {
        "colors": len(residues),
        "largest_cell_share": round(int(max(counts)) / result.values.size, 6),
        "largest_circular_gap": round(max(int(M + residues[0] - residues[-1]), *gaps) / M, 6),
    }


def atlas(size, figures):
    rng = Random(19)
    results = {"side": size, "post_powers_for_window": POWERS, "checkerboard_opposite": {}, "odd_odd": {}}
    checker_panels = []
    for power_group in power_groups(size):
        group = str(power_group)
        qs = checkerboard_tail_prepowers(size) if power_group.tail else power_group.powers
        bases = [Base(size, CHECKERBOARD, c, q) for c in CHECKER_COMBINERS for q in qs]
        counts = catalogues(bases[:len(qs)] if power_group.tail else bases, postpowers)
        assert len(counts["order"]) == len(counts["shift"])
        results["checkerboard_opposite"][group] = {
            "representative_pre_powers": qs,
            "all_twists_raw_equalities": len(base_pool(size, power_group, 4096)[0]),
            "all_post_powers": {name: len(classes) for name, classes in counts.items()},
        }
        row = []
        for c in CHECKER_COMBINERS:
            subset = [base for base in bases if base.combiner == c]
            orders = counts["order"] if power_group.tail else catalogues(subset, postpowers)["order"]
            row.append((f"{group} · {c.upper()}", draw(orders, rng)))
        checker_panels.append(row)

    odd_panels = []
    for c in ODD_COMBINERS:
        head, tail = Base(size, ODD_ODD, c, 2), Base(size, ODD_ODD, c, 1 << odd_odd_tail(size, c))
        count_by_valuation = {}
        for w, qs in odd_odd_prepowers(size, c):
            bases = [Base(size, ODD_ODD, c, q) for q in qs]
            window = catalogues(bases, lambda _: POWERS)
            detail = {"window": {name: len(classes) for name, classes in window.items()}}
            if c in ODD_COSETS:
                complete = catalogues(bases, postpowers)
                detail["all_post_powers"] = {name: len(classes) for name, classes in complete.items()}
                assert len(complete["shift"]) == len(complete["order"])
                assert window["order"].keys() <= complete["order"].keys()
            else:
                complete = catalogues(bases, nonunit_order_powers, retain_shifts=False)
                detail["all_post_powers"] = {
                    "equality": len(complete["equality"]),
                    "order": len(complete["order"]),
                    "shift": "infinite",
                }
                assert window["order"].keys() <= complete["order"].keys()
                check_nonunit_orders(bases[0], rng)
            count_by_valuation[w] = detail
        results["odd_odd"][c] = count_by_valuation
        row = []
        for base in (head, tail):
            for p in (1, 2):
                M = base.minimum(p)
                row.append((f"{c.upper()} · pre {base.q} · post {p}", base.spec(p, 1, M)))
        odd_panels.append(row)

    absdiff = Base(size, ODD_ODD, "absdiff", 2)
    minimum = absdiff.spec(M=absdiff.minimum(1))
    all_colors = absdiff.spec(M=absdiff.K)
    full = evaluate(all_colors).values
    assert all(not np.array_equal(full, np.roll(full, size // 2, axis)) for axis in (0, 1))
    results["odd_odd_absdiff_precision"] = {
        "minimum": {"M": minimum["M"], **measure(minimum)[1]},
        "all_raw_colors": {"M": all_colors["M"], **measure(all_colors)[1]},
    }
    plain, twisted, evidence = twist_comparison(size)
    results["checkerboard_pre_2_twist_witness"] = evidence
    if figures:
        render(checker_panels, "Checkerboard-opposite · uniform circular-order draws within each panel", HERE / "checkerboard.png")
        render(
            odd_panels,
            "Odd-odd · minimum precision at the first and stabilized pre-power valuations",
            HERE / "odd-odd.png",
        )
        render(
            [
                [("Checkerboard OR · identity", plain), ("Checkerboard OR · Q = 1", twisted)],
                [("Odd-odd ABSDIFF · minimum M", minimum), ("Odd-odd ABSDIFF · keep all colors", all_colors)],
            ],
            "Changing one parameter at a time · side 64, pre-power 2, post-power 1",
            HERE / "comparisons.png",
        )
    return results


def check_nonunit_orders(base, rng):
    reference = catalogues([base], nonunit_order_powers, retain_shifts=False)["order"]
    positions = joint_positions([base])
    for p in (17, 21, 32, 47, 64, 96, 128, 256):
        M = base.minimum(p)
        for _ in range(4):
            a = 2 * rng.randrange(M // 2) + 1
            values = evaluate(base.spec(p, a, M)).values
            residues = (values.ravel()[positions] - values[0, 0]) % M
            order = np.unique(residues, return_inverse=True)[1].astype(np.uint32).tobytes()
            assert order in reference, (base, p, a)


def twist_comparison(size):
    base = Base(size, CHECKERBOARD, "or", 2)
    plain = base.spec(M=base.minimum(1))
    twisted = base.spec(M=base.minimum(1))
    # t + 2t(t-1)
    twisted["pre"].append(["poly", [0, -1, 2]])
    values = evaluate(twisted).values
    assert all(not np.array_equal(values, np.roll(values, size // 2, axis)) for axis in (0, 1))
    witnesses = {}
    for c in CHECKER_COMBINERS:
        prior = {}
        identity = Base(size, CHECKERBOARD, c, 2).field
        for index, (z, v) in enumerate(zip(identity.flat, values.flat)):
            before, u = prior.setdefault(z, (index, v))
            if u != v:
                witnesses[c] = {
                    "cells_row_col": [divmod(before, size), divmod(index, size)],
                    "identity_raw_value": int(z),
                    "twisted_or_outputs": [int(u), int(v)],
                }
                break
        assert c in witnesses, c
    return plain, twisted, witnesses


def render(rows, title, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(rows), len(rows[0]), figsize=(10, len(rows) * 2.38), layout="constrained")
    for axes_row, panels in zip(axes, rows):
        for ax, (label, spec) in zip(axes_row, panels):
            result, stats = measure(spec)
            ax.imshow(result.normalized(), cmap="twilight", vmin=0, vmax=1, interpolation="nearest")
            ax.set_title(
                f"{label}\n{stats['colors']} colors · largest gap {stats['largest_circular_gap']:.1%}",
                fontsize=9,
            )
            ax.set_axis_off()
    fig.suptitle(title, fontsize=12)
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-figures", action="store_true")
    args = parser.parse_args()
    checks = {size: check_fields(size) for size in (16, 32, 64, 128)}
    results = atlas(64, not args.skip_figures)
    results["native_checks_by_side"] = checks
    results["additional_odd_odd_order_checks_at_side_64"] = 2 * len(odd_odd_prepowers(64, "xor")) * 8 * 4
    (HERE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"{sum(checks.values()):,} native field and tail checks. Wrote {HERE / 'results.json'}")


if __name__ == "__main__":
    main()
