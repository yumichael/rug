"""Regenerate the bounded exact evidence accompanying these tentative reports."""

import argparse
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from random import Random
from statistics import median
from time import perf_counter

from count_orders import counts, enumerate_orders
from family_checks import (
    fixed_modulus_checks,
    modulus_and_counterexample_checks,
    pre_power_checks,
    xor_gallery_checks,
)
from realize import realize
from sampler import Sampler
from tail_modulus_checks import run_checks as tail_modulus_checks
from xor_checks import run_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', action='store_true', help='Also time N=1024 order sampling on this machine.')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('results.json'))
    args = parser.parse_args()
    result = {'recorded_date': '2026-11-12', 'seed': 0, 'status': 'tentative exploration'}
    root = Path(__file__).resolve().parents[3]
    result['source_sha256'] = {
        str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
        for path in [
            root / 'research/interactive/ruglab/exploration.py',
            root / 'research/interactive/ruglab/post_polynomials.py',
            root / 'research/interactive/ruglab/sampling.py',
            root / 'research/interactive/ruglab/engine.py',
        ]
    }
    for name, function in [
        ('xor_theorems', run_checks),
        ('xor_gallery', xor_gallery_checks),
        ('modulus_examples', modulus_and_counterexample_checks),
        ('fixed_modulus_sampling', fixed_modulus_checks),
        ('pre_power_families', pre_power_checks),
        ('tail_modulus_selection', tail_modulus_checks),
    ]:
        result[name] = function()
        print(f'{name}: exact checks passed', flush=True)

    order_report = {}
    for p in (1, 2, 3, 4):
        _, _, _, R = counts(p)
        expected = enumerate_orders(p)
        by_pairs = Counter()
        for rank in expected:
            edges = {tuple(sorted((rank[i], rank[i + 1]))) for i in range(0, 2 * p, 2) if rank[i] != rank[i + 1]}
            by_pairs[len(edges)] += 1
        predicted = {k: R[p][k] // (2 * k) for k in range(1, p + 1)}
        assert dict(by_pairs) == predicted
        sampler = Sampler(p)
        assert sampler.total == len(expected)
        rng = Random(0)
        for _ in range(1000):
            rank, _ = sampler.draw(rng)
            assert rank in expected
        order_report[p] = {
            'order_classes': len(expected),
            'by_antipodal_pairs': predicted,
            'Rug_side': 4 * p if p & (p - 1) == 0 else None,
        }
    result['exhaustive_order_counts'] = order_report
    _, _, _, R = counts(8)
    assert sum(R[8][k] // (2 * k) for k in range(1, 9)) == 1986611520
    print('order counts: independent enumeration and sampler support agree', flush=True)

    realization_report = {}
    rng = Random(0)
    for side in (4, 8, 16, 32):
        sampler = Sampler(side // 4)
        exponents = []
        for _ in range(25):
            rank, structure = sampler.draw(rng)
            modulus = realize(side, rank, structure)
            exponents.append(modulus.bit_length() - 1)
        realization_report[side] = {
            'native_polynomial_checks': 25,
            'minimum_modulus_exponent_range': [min(exponents), max(exponents)],
        }
    result['order_realizations'] = realization_report
    print('order realizations: 100 exact native tables and minimum moduli passed', flush=True)

    if args.benchmark:
        start = perf_counter()
        sampler = Sampler(1024 // 4)
        setup = perf_counter() - start
        rng, times = Random(0), []
        for _ in range(10):
            start = perf_counter()
            sampler.draw(rng)
            times.append(perf_counter() - start)
        result['benchmark_N1024'] = {
            'setup_seconds': setup,
            'median_draw_seconds': median(times),
            'draws': len(times),
            'class_count_bits': sampler.total.bit_length(),
            'excludes': 'polynomial realization and rendering',
        }
        print('N1024 benchmark:', result['benchmark_N1024'], flush=True)

    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {args.output}', flush=True)


if __name__ == '__main__':
    main()
