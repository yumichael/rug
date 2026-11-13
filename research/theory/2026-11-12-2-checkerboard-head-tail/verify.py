"""Reproduce the head/tail proofs' bounded checks and sampler examples."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random
from time import perf_counter

import numpy as np

from core import (Basic, ShiftSampler, canonical_twists_64, combine, moduli, nu, poly, pre_values,
                  ranks, reduced_twist, twist_degree_bound, twist_space)
from fast_sampler import OrderSampler
from order_sampler import OrderSampler as ReferenceSampler, admissible
from realize import pre_polynomial, realize


HERE = Path(__file__).resolve().parent


def head(N):
    r = N.bit_length() - 1
    return [q for q in range(2, 2 * r + 2, 2) if q < r + nu(q)]


def exhaustive_orders(sizes):
    n = sum(sizes)
    components = []
    start = 0
    for size in sizes:
        components.append(tuple(range(start, start + size)))
        start += size
    result = set()
    for k in range(2, n + 1):
        for rest in product(range(k), repeat=n - 1):
            rank = (0, *rest)
            if len(set(rank)) == k and admissible(rank, components):
                result.add(rank)
    return components, result


def domain_checks(rng):
    report = []
    checks = 0
    for r in range(3, 13):
        N = 1 << r
        row = {'N': N, 'head': head(N), 'persistent_tail': max(head(N)) + 2, 'twist_coordinate_bits': {}}
        for q in [*head(N), row['persistent_tail']]:
            K = N * (q & -q)
            a, b = twist_degree_bound(N, q)
            bits, _ = twist_space(N, q)
            row['twist_coordinate_bits'][q] = {'degree_below': a + b, 'bits': bits, 'functions': str(1 << sum(bits))}
            for _ in range(8):
                Q = tuple(rng.randrange(-(1 << 30), 1 << 30) for _ in range(14))
                P = pre_values(N, q, Q)
                assert P == pre_values(N, q, reduced_twist(N, q, Q))
                # Native displayed half-axis maps coincide because P has period N.
                assert all(((P[(x + N // 2) % N] - P[x]) % K == (K // 2 if x % 2 else 0))
                           for x in range(N))
                w = int(nu(q))
                stride = 1 << (w + 2)
                assert set(P[1::2]) == set(range(1, K, stride))
                for s in range(1, r):
                    layer = {P[x] for x in range(1 << s, N, 1 << (s + 1))}
                    if s * q >= r + w:
                        expected = {0}
                    else:
                        step = 1 << min(r + w, s * q + w + 2)
                        t = pow(2, s * q, K)
                        center = (t + 2 * t * (t - 1) * poly(Q, t, K)) % K
                        expected = {(center + a) % K for a in range(0, K, step)}
                    assert layer == expected
                checks += 1
            basic = Basic(N, q, (), 'or')
            assert all(len(g) <= 2 for g in basic.components)
            if q >= 4:
                assert len(basic.nodes) == N // 4
                assert all(len(g) == 2 for g in basic.components)
            # Same abstract ADD/ABSDIFF component sizes, without relying on pixels.
            add, difference = Basic(N, q, (), 'add'), Basic(N, q, (), 'absdiff')
            assert sorted(map(len, add.components)) == sorted(map(len, difference.components))
            assert max(map(len, add.components)) <= 4
            if q >= r + nu(q):
                reference = basic.nodes
                for c in ('xor', 'add', 'absdiff'):
                    other = Basic(N, q, (), c)
                    assert other.nodes_edges == basic.nodes_edges
                assert len(reference) == N // 4
        report.append(row)
        print('domain checked', N, flush=True)
    return {'domains': report, 'unrestricted_twist_reduction_checks': checks}


def canonical_checks(rng):
    report = {}
    for q in (2, 4, 6, 8):
        representatives = canonical_twists_64(q)
        tables = {pre_values(64, q, Q) for Q in representatives}
        assert len(tables) == len(representatives)
        bits, _ = twist_space(64, q)
        assert len(tables) == 1 << sum(bits)
        for _ in range(100):
            Q = tuple(rng.randrange(-100000, 100000) for _ in range(12))
            assert pre_values(64, q, Q) in tables
        histograms = {c: Counter() for c in ('or', 'xor', 'add', 'absdiff')}
        for Q in representatives:
            for c in histograms:
                b = Basic(64, q, Q, c)
                histogram = tuple(sorted(Counter(map(len, b.components)).items()))
                histograms[c][histogram] += 1
            assert sorted(map(len, Basic(64, q, Q, 'add').components)) == sorted(map(len, Basic(64, q, Q, 'absdiff').components))
            if q == 2:
                forced = ((-Q[0]) % 4).bit_count()
                assert len(Basic(64, q, Q, 'or').nodes) == 16 + 16 // (1 << forced)
        report[q] = {'pre_functions': len(tables), 'coordinate_bits': bits,
                     'component_histograms': {c: [{'sizes': dict(h), 'pre_functions': n} for h, n in hist.items()]
                                              for c, hist in histograms.items()}}
    return report


def catalogue_checks():
    from ruglab.exploration import _STUDY_POSTS, _STUDY_TWISTS, PrePowerStudyRecipe, sample_field

    summary = {}
    native = 0
    for c, q in product(('or', 'xor', 'add', 'absdiff'), (2, 4, 6, 8)):
        agreement = Counter()
        minimums = Counter()
        for ti, Q in enumerate(_STUDY_TWISTS):
            basic = Basic(64, q, Q, c)
            for pi, H in enumerate(_STUDY_POSTS):
                ms = moduli(basic, H)
                agreement['recipes'] += 1
                agreement['all_equal'] += len(set(ms.values())) == 1
                agreement['catalogue_equals_distinct'] += ms['catalogue'] == ms['distinct_outputs']
                agreement['minimum_unattainable'] += ms['minimum_period'] is None
                minimums[str(ms['minimum_period'])] += 1
                if ti in (0, 1) and pi in (0, 3, 9):
                    for mode, expected in ms.items():
                        result = sample_field(PrePowerStudyRecipe(q, ti, pi, c), 64, 'checkerboard_opposite', m_selection=mode)
                        assert result.spec['M'] == expected
                        desired = np.array([poly(H, z, expected) for z in basic.nodes], dtype=object)[basic.indices]
                        assert np.array_equal(result.values.expand(), desired)
                        native += 1
        summary[f'{q}:{c}'] = {**agreement, 'minimum_M_histogram': dict(minimums)}
    return {'N64_catalogue_comparison': summary, 'actual_selector_field_checks': native}


def sampler_checks(rng):
    report = {'exhaustive_models': [], 'domain_examples': [], 'native_realizations': 0}
    for sizes in ((2,), (3,), (4,), (2, 2), (2, 3), (3, 3), (2, 2, 2), (1, 2), (1, 1, 2)):
        components, expected = exhaustive_orders(sizes)
        sampler = OrderSampler(components)
        assert sampler.total == len(expected)
        assert sampler.total == ReferenceSampler(components).total
        for _ in range(100):
            rank, _ = sampler.draw(rng)
            assert rank in expected
        report['exhaustive_models'].append({'sizes': sizes, 'orders': sampler.total})
    for N in (8, 16, 32, 64, 128):
        q = max(head(N)) + 2
        basic = Basic(N, q, (), 'or')
        start = perf_counter()
        sampler = OrderSampler(basic.components)
        build = perf_counter() - start
        start = perf_counter()
        rank, structure = sampler.draw(rng, anchor=basic.anchor)
        draw = perf_counter() - start
        report['domain_examples'].append({'N': N, 'tail_orders': str(sampler.total), 'build_seconds': build, 'draw_seconds': draw})
    from ruglab.diagnostics import periods
    from ruglab.engine import evaluate

    for N in (8, 16, 32, 64):
        for c, q in product(('or', 'xor', 'add', 'absdiff'), head(N)):
            basic = Basic(N, q, (2, -3, 5, 1), c)
            sampler = OrderSampler(basic.components)
            rank, structure = sampler.draw(rng, anchor=basic.anchor)
            H, M, values = realize(basic, structure)
            assert rank == ranks(values, M, basic.anchor)
            spec = {'n': N, 'K': basic.K, 'M': M, 'pre': [['pow', q], ['poly', pre_polynomial(basic.Q)]],
                    'post': [['poly', H]], 'sampling': 'checkerboard_opposite', 'checkerboard_axis': 'vertical', 'combine': c}
            field = evaluate(spec)
            assert np.array_equal(field.values, np.array(values, dtype=object)[basic.indices])
            assert periods(field, certified_torus=True) == (N, N)
            assert periods(evaluate({**spec, 'M': M // 2}), certified_torus=True) != (N, N)
            report['native_realizations'] += 1
    return report


def broader_sampler_checks(rng):
    from fractions import Fraction
    from union_sampler import UnionSampler

    report = {'head_benchmarks': [], 'N64_fixed_M_counts': []}
    small = UnionSampler([Basic(8, q, Q, c) for q, twists in ((2, ((), (1,))), (4, ((),)))
                          for Q in twists for c in ('or', 'xor', 'add', 'absdiff')])
    occurrences = Counter()
    catalogues = []
    for basic, sampler, _, _, _ in small.entries:
        catalogue = set()
        n = len(basic.nodes)
        for k in range(2, n + 1):
            for word in product(range(k), repeat=n):
                if word[basic.anchor] == 0 and len(set(word)) == k and admissible(word, basic.components):
                    catalogue.add(tuple(np.asarray(word)[basic.indices].ravel()))
        assert len(catalogue) == sampler.total
        catalogues.append(catalogue)
        occurrences.update(catalogue)
    mass = Counter()
    total = sum(map(len, catalogues))
    for catalogue in catalogues:
        for field in catalogue:
            flat = np.asarray(field)
            actual = sum(np.array_equal(flat, flat[first][partition.ravel()])
                         for _, _, _, partition, first in small.entries)
            assert actual == occurrences[field]
            mass[field] += Fraction(1, total * actual)
    assert len(set(mass.values())) == 1
    overlaps = Counter()
    for _ in range(500):
        field, info = small.draw(rng)
        assert tuple(field.ravel()) in occurrences
        overlaps[info['multiplicity']] += 1
    assert any(n > 1 for n in overlaps)
    report['exhaustive_N8_union'] = {'bases': len(small.entries), 'orders': len(occurrences),
                                    'proposal_occurrences': total, 'accepted_multiplicities': dict(overlaps)}
    for N in (64, 128, 256, 512, 1024):
        basic = Basic(N, 2, (), 'add')
        start = perf_counter()
        sampler = OrderSampler(basic.components)
        build = perf_counter() - start
        start = perf_counter()
        rank, _ = sampler.draw(rng, basic.anchor)
        draw = perf_counter() - start
        assert admissible(rank, basic.components)
        report['head_benchmarks'].append({'N': N, **basic.summary(), 'count_bits': sampler.total.bit_length(),
                                          'build_seconds': build, 'rank_draw_seconds': draw})
        print('head benchmark', N, round(build, 3), 'seconds', flush=True)
    for q, c in product((2, 4, 6, 8), ('or', 'xor', 'add', 'absdiff')):
        basic = Basic(64, q, (), c)
        for M in (4, 16, basic.K, 2 * basic.K):
            for minimum in (False, True):
                sampler = ShiftSampler(basic, M, minimum)
                if sampler.total:
                    values = sampler.draw(rng)
                    assert basic.full(values)
                    if minimum:
                        assert not basic.full(tuple(v % (M // 2) for v in values))
                report['N64_fixed_M_counts'].append({'q': q, 'combiner': c, 'M': M,
                                                    'minimum': minimum, 'shift_classes': str(sampler.total)})
    start = perf_counter()
    bases = [Basic(64, q, Q, c) for q in (2, 4, 6, 8) for Q in canonical_twists_64(q)
             for c in ('or', 'xor', 'add', 'absdiff')]
    union = UnionSampler(bases)
    build = perf_counter() - start
    start = perf_counter()
    multiplicities = Counter()
    for _ in range(40):
        field, info = union.draw(rng)
        basic = union.entries[info['source']][0]
        _, first = np.unique(basic.indices, return_index=True)
        assert admissible(field.ravel()[first], basic.components)
        assert field[0, 0] == 0
        multiplicities[info['multiplicity']] += 1
    report['N64_complete_head_union'] = {'input_bases': len(bases), 'distinct_partitions': len(union.entries),
                                       'draws': 40, 'build_seconds': build, 'draw_seconds_total': perf_counter() - start,
                                       'accepted_multiplicities': dict(multiplicities)}
    return report


def arbitrary_post_checks(rng):
    from ruglab.diagnostics import periods
    from ruglab.engine import evaluate

    checks = 0
    for N in (8, 16, 32, 64, 128):
        for q in (head(N)[0], head(N)[-1]):
            Q = tuple(rng.randrange(-100, 101) for _ in range(9))
            for c in ('or', 'xor', 'add', 'absdiff'):
                basic = Basic(N, q, Q, c)
                H = tuple(rng.randrange(-20, 21) for _ in range(10))
                M = moduli(basic, H)['minimum_period']
                assert M is not None
                spec = {'n': N, 'K': basic.K, 'M': M, 'pre': [['pow', q], ['poly', pre_polynomial(Q)]],
                        'post': [['poly', H]], 'sampling': 'checkerboard_opposite', 'checkerboard_axis': 'vertical', 'combine': c}
                field = evaluate(spec)
                expected = np.array([poly(H, z, M) for z in basic.nodes], dtype=object)[basic.indices]
                assert np.array_equal(field.values, expected)
                assert periods(field, certified_torus=True) == (N, N)
                assert periods(evaluate({**spec, 'M': M // 2}), certified_torus=True) != (N, N)
                if N >= 16:
                    assert moduli(Basic(N, q, Q, 'absdiff'), (0, 1))['minimum_period'] == 4
                checks += 1
    return {'signed_degree_nine_posts_and_degree_eight_twists': checks}


def shift_checks(rng):
    report = []
    for q, c in ((2, 'or'), (4, 'xor'), (6, 'add')):
        basic = Basic(8, q, (), c)
        for M in (4, 8, 16):
            if len(basic.nodes) > 4:
                continue
            for minimum in (False, True):
                expected = set()
                for coefficients in product(range(M), repeat=len(basic.nodes) - 1):
                    values = [poly((0, *coefficients), z, M) for z in basic.nodes]
                    phase = values[basic.anchor]
                    values = tuple((v - phase) % M for v in values)
                    if basic.full(values) and (not minimum or not basic.full(tuple(v % (M // 2) for v in values))):
                        expected.add(values)
                sampler = ShiftSampler(basic, M, minimum)
                assert sampler.total == len(expected)
                if expected:
                    assert all(sampler.draw(rng) in expected for _ in range(50))
                report.append({'q': q, 'combiner': c, 'M': M, 'minimum': minimum, 'classes': len(expected)})
    return report


def examples():
    result = {}
    b = Basic(64, 10, (), 'or')
    for name, H in [('identity', (0, 1)), ('constant_offset', (127, 1)), ('quadratic_mergers', (0, 6, 1)), ('constant', (7,))]:
        result[name] = moduli(b, H)
    result['ABSDIFF_N64_identity'] = {q: moduli(Basic(64, q, (), 'absdiff'), (0, 1)) for q in head(64)}
    return result


def figures():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 5, figsize=(11, 9))
    for row, c in enumerate(('or', 'xor', 'add', 'absdiff')):
        for col, q in enumerate((2, 4, 6, 8, 10)):
            b = Basic(64, q, (), c)
            M = moduli(b, (0, 1))['minimum_period']
            rank = ranks(b.nodes, M, b.anchor)
            axes[row, col].imshow(np.array(rank)[b.indices], cmap='gray', interpolation='nearest')
            axes[row, col].set_title(f'{c.upper()}, q={q}\nM={M}, groups={len(set(rank))}', fontsize=9)
            axes[row, col].set_axis_off()
    fig.suptitle('64 × 64 worked example: identity post at minimum period; anchored ranks')
    fig.tight_layout()
    fig.savefig(HERE / 'head-tail-atlas.png', dpi=140)
    plt.close(fig)
    fig, axes = plt.subplots(4, 6, figsize=(12, 8))
    for row, c in enumerate(('or', 'xor', 'add', 'absdiff')):
        b = Basic(64, 4, (), c)
        for col, M in enumerate((4, 16, 64, 256, 512, 1024)):
            v = [(z - b.nodes[b.anchor]) % M for z in b.nodes]
            full = b.full(v)
            axes[row, col].imshow(np.array(v)[b.indices] / M, vmin=0, vmax=1, cmap='gray', interpolation='nearest')
            axes[row, col].set_title(f'{c.upper()}, M={M}\n'+('period 64' if full else 'smaller period'), fontsize=8)
            axes[row, col].set_axis_off()
    fig.suptitle('A dyadic modulus ladder: q=4, identity twist/post; anchored value divided by M')
    fig.tight_layout()
    fig.savefig(HERE / 'modulus-ladder.png', dpi=140)
    plt.close(fig)
    fig, axes = plt.subplots(5, 5, figsize=(14, 14))
    for row, N in enumerate((32, 64, 128, 256, 512)):
        for col, q in enumerate((2, 4, 6, 8, 10)):
            b = Basic(N, q, (), 'or')
            rank = ranks(b.nodes, b.K, b.anchor)
            axes[row, col].imshow(np.array(rank)[b.indices], cmap='gray', interpolation='nearest')
            tail = q >= N.bit_length() - 1 + nu(q)
            axes[row, col].set_title(f'N={N}, q={q}, '+('tail' if tail else 'head')
                                     +f'\neven values={len(set(b.pre[::2]))}', fontsize=9)
            axes[row, col].set_axis_off()
    fig.suptitle('Domain-dependent families: OR, identity twist/post, minimum precision; anchored ranks')
    fig.tight_layout()
    fig.savefig(HERE / 'domain-families.png', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE / 'results.json')
    parser.add_argument('--skip-figures', action='store_true')
    args = parser.parse_args()
    rng = Random(20261112)
    report = {'seed': 20261112}
    for name, function in [('domains', lambda: domain_checks(rng)), ('canonical_N64', lambda: canonical_checks(rng)),
                           ('catalogue', catalogue_checks), ('orders', lambda: sampler_checks(rng)),
                           ('fixed_M_shifts', lambda: shift_checks(rng)), ('broader_samplers', lambda: broader_sampler_checks(rng)),
                           ('arbitrary_polynomials', lambda: arbitrary_post_checks(rng)),
                           ('examples', examples)]:
        start = perf_counter()
        report[name] = function()
        print('completed', name, round(perf_counter() - start, 3), 'seconds', flush=True)
    if not args.skip_figures:
        figures()
    report['source_sha256'] = {p.name: sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
