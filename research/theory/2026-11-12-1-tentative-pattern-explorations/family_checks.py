"""Exact workbench comparisons for the exploratory pre-power and precision claims."""

from collections import Counter
from hashlib import sha256
from itertools import product
from math import factorial, inf
from random import Random

import numpy as np
from ruglab.diagnostics import periods, signature
from ruglab.engine import evaluate
from ruglab.exploration import (
    _STUDY_POSTS,
    _STUDY_TWISTS,
    PatternRecipe,
    PrePowerStudyRecipe,
    _base_field,
    _distinct_polynomial,
    _pre_modulus,
    _study_twist,
    sample_field,
)
from ruglab.operations import operation
from ruglab.post_polynomials import POST_STRATA, _full_period, draw_post_polynomial


def digest(array):
    return sha256(np.ascontiguousarray(array, dtype=np.uint32).tobytes()).hexdigest()


def partition(indices):
    _, first = np.unique(indices, return_index=True)
    order = indices.ravel()[np.sort(first)]
    lookup = np.empty(int(indices.max()) + 1, dtype=np.uint32)
    lookup[order] = np.arange(len(order))
    return digest(lookup[indices])


def order_signature(labels, indices):
    lookup = np.empty(len(labels), dtype=np.int64)
    lookup[np.argsort(labels)] = np.arange(len(labels))
    return digest((lookup[indices] - lookup[indices[0, 0]]) % len(labels))


def grouped(items):
    groups = {}
    for exponent, key in items:
        groups.setdefault(key, []).append(exponent)
    return list(groups.values())


def valuation(number):
    number = abs(int(number))
    return (number & -number).bit_length() - 1 if number else inf


def minimum_on_torus(outputs, indices):
    """The caller supplies a basic table with known N-shifts as exact periods."""
    side = len(indices)
    count = len(outputs)
    depths = []
    for axis in (0, 1):
        pairs = np.unique(indices.astype(np.int64) * count + np.roll(indices, side // 2, axis=axis))
        depths.append(min(valuation(outputs[int(pair) // count] - outputs[int(pair) % count]) for pair in pairs))
    assert max(depths) != inf
    return 1 << int(1 + max(depths))


def polynomial_values(coefficients, inputs, modulus):
    assert modulus <= 1 << 64
    inputs = np.asarray(inputs, dtype=np.uint64)
    result = np.zeros_like(inputs)
    for coefficient in reversed(coefficients):
        result = (result * inputs + (coefficient % modulus)) & (modulus - 1)
    return result


def scalar_ranks(values, modulus):
    return np.unique((values + modulus - values[-1]) % modulus, return_inverse=True)[1]


def xor_gallery_checks():
    side = 1024
    domain = 2 * side
    inputs = np.arange(1, domain, 2, dtype=np.uint64)
    report = {}
    for family, precision in POST_STRATA:
        entry = Counter()
        ratios = Counter()
        for draw in range(24):
            coefficients, modulus = draw_post_polynomial(domain, family, precision, 0, draw)
            minimum = modulus
            while minimum > 1 and _full_period(coefficients, domain, minimum // 2):
                minimum //= 2
            values = polynomial_values(coefficients, inputs, modulus)
            reduced = values % minimum
            before = np.array_equal(values, values[::-1])
            after = np.array_equal(reduced, reduced[::-1])
            entry['draws'] += 1
            entry['excess_precision'] += minimum < modulus
            entry['rank_changes'] += not np.array_equal(scalar_ranks(values, modulus), scalar_ranks(reduced, minimum))
            entry['symmetric_before'] += before
            entry['symmetric_after'] += after
            ratios[modulus // minimum] += 1
            if family == 'even only':
                assert after
        report[f'{family}:v={precision}'] = {**dict(entry), 'modulus_ratios': dict(ratios)}
    assert sum(v['excess_precision'] for v in report.values()) == 103
    return report


def pre_power_checks():
    report = {'opposite': {}, 'odd_odd': {}, 'tail_cutoffs': {}, 'checks': {}}
    for sampling in ('checkerboard_opposite', 'odd_odd'):
        destination = report['opposite' if sampling == 'checkerboard_opposite' else 'odd_odd']
        sides = (
            (8, 16, 32, 64, 128, 256, 512, 1024) if sampling == 'checkerboard_opposite' else (8, 16, 32, 64, 128, 256)
        )
        for side in sides:
            partitions, orders = [], []
            for q in range(2, 65, 2):
                field = sample_field(PrePowerStudyRecipe(q, 0, 0), side, sampling, m_selection='catalogue')
                partitions.append((q, partition(field.values.indices)))
                orders.append((q, order_signature(field.values.labels, field.values.indices)))
            destination[side] = {'partition_groups': grouped(partitions), 'order_groups': grouped(orders)}
    for r in range(3, 13):
        bad = [q for q in range(2, 129, 2) if q < r + valuation(q)]
        report['tail_cutoffs'][1 << r] = max(bad, default=0) + 2
    assert list(report['tail_cutoffs'].values()) == [6, 6, 6, 10, 10, 10, 10, 12, 14, 14]

    zero_checks = 0
    for side, q, twist in product((8, 16, 32, 64, 128), (2, 4, 6, 8, 10, 48, 64), (0, 1, 7, 15)):
        k = side.bit_length() - 1 + valuation(q)
        zero_share = 2 ** (-2 * ((k + q - 1) // q))
        for sampling, factor in [('full', 1), ('checkerboard_same', 2)]:
            field = sample_field(PrePowerStudyRecipe(q, twist, 0), side, sampling)
            assert field.zero_fraction == factor * zero_share
            zero_checks += 1
    report['checks']['zero_occupancy'] = zero_checks

    frequency_checks = 0
    for side, q, twist in product((8, 32, 128), (2, 4, 6, 8, 10, 48, 64), range(16)):
        field = sample_field(PrePowerStudyRecipe(q, twist, 0), side, 'odd_odd')
        actual = sorted(np.bincount(field.values.indices.ravel()).tolist())
        assert actual == sorted(4 * 3 ** j.bit_count() for j in range(side // 2))
        frequency_checks += 1
    report['checks']['odd_odd_frequency_tables'] = frequency_checks

    thresholds = {}
    for side in (8, 16, 32, 64, 128, 256):
        r = side.bit_length() - 1
        observed = Counter()
        for twist in range(16):
            by_post = {post: [] for post in range(10)}
            for w in range(1, r + 1):
                q = 1 << w
                K = _pre_modulus(q, side, 'odd_odd', 'or')
                base, _, _ = _base_field(q, _study_twist(_STUDY_TWISTS[twist]), K, 'or', side, 'odd_odd')
                for post in range(10):
                    labels, _ = _distinct_polynomial(base.labels.astype(object), _STUDY_POSTS[post])
                    by_post[post].append(order_signature(labels, base.indices))
            for signatures in by_post.values():
                threshold = next(w for w in range(1, r + 1) if len(set(signatures[w - 1 :])) == 1)
                assert threshold == max(1, r - 2)
                observed[threshold] += 1
        thresholds[side] = dict(observed)
    report['odd_odd_power_two_tail_thresholds'] = thresholds

    derivative_checks = 0
    for side in (16, 32, 64, 128):
        w = side.bit_length() - 3
        T, S = side // 2, 1 << (w + 2)
        L = np.array([(pow(2 * i + 1, 1 << w, S * T) - 1) // S for i in range(side)])
        for odd_part, twist, post in product((1, 3, 5), range(16), range(10)):
            alpha = (1 + 2 * sum(_STUDY_TWISTS[twist])) * odd_part
            operand = alpha * L % T
            combined = operand[:, None] | operand[None, :]
            derivative = sum(i * a for i, a in enumerate(_STUDY_POSTS[post]))
            beta = derivative // (derivative & -derivative)
            field = sample_field(PrePowerStudyRecipe((1 << w) * odd_part, twist, post), side, 'odd_odd')
            assert order_signature(field.values.labels, field.values.indices) == digest(beta * combined % T)
            derivative_checks += 1
    report['checks']['odd_odd_derivative_formula'] = derivative_checks

    cross_checks = 0
    for q, twist in product(range(10, 65, 2), (0, 1, -3)):
        fields = [
            sample_field(PatternRecipe(name, q, twist, 7), 128, 'checkerboard_opposite')
            for name in ('or', 'xor', 'add', 'absdiff')
        ]
        assert len({field.spec['M'] for field in fields}) == 1
        arrays = [field.values.expand() for field in fields]
        assert all(np.array_equal(arrays[0], array) for array in arrays[1:])
        cross_checks += 1
    report['checks']['four_combiner_matches'] = cross_checks

    # An outside-catalogue post delays the exact rank tail at N=32.
    later_tail = []
    for w in range(3, 11):
        side, q = 32, 1 << w
        K = _pre_modulus(q, side, 'odd_odd', 'or')
        base, _, _ = _base_field(q, 0, K, 'or', side, 'odd_odd')
        outputs = operation(base.labels.astype(object), 'poly', (0, 62, 1))
        labels, catalogue = _distinct_polynomial(base.labels.astype(object), (0, 62, 1))
        minimum = minimum_on_torus(outputs, base.indices)
        # At the period modulus there may be mergers; compact labels first.
        reduced_labels, remap = np.unique(outputs % minimum, return_inverse=True)
        later_tail.append(
            {
                'w': w,
                'catalogue_M': catalogue,
                'minimum_M': minimum,
                'catalogue_order': order_signature(labels, base.indices),
                'minimum_order': order_signature(reduced_labels, remap[base.indices]),
            }
        )
    assert len({row['catalogue_order'] for row in later_tail if row['w'] >= 8}) == 1
    assert len({row['minimum_order'] for row in later_tail if row['w'] >= 8}) == 1
    assert later_tail[4]['minimum_order'] != later_tail[5]['minimum_order']
    report['delayed_tail_H_62z_plus_z2'] = later_tail
    return report


def modulus_and_counterexample_checks():
    report = {}
    for sampling, post_index in [
        ('full', 2),
        ('checkerboard_same', 2),
        ('checkerboard_opposite', 2),
        ('checkerboard_opposite', 5),
    ]:
        field = sample_field(PrePowerStudyRecipe(2, 0, post_index), 8, sampling)
        original = evaluate(field.spec)
        inputs = original.stages['z0']
        outputs = operation(inputs, 'poly', _STUDY_POSTS[post_index])
        unique_inputs, indices = np.unique(inputs, return_inverse=True)
        values = operation(unique_inputs, 'poly', _STUDY_POSTS[post_index])
        minimum = minimum_on_torus(values, indices.reshape(inputs.shape))
        assert periods(evaluate({**field.spec, 'M': minimum}), certified_torus=True) == (8, 8)
        report[f'{sampling}:post={post_index}'] = {
            'catalogue_M': field.spec['M'],
            'minimum_M': minimum,
            'distinct_before': len(set(outputs.flat)),
            'distinct_at_minimum': len(set((outputs % minimum).flat)),
        }
    assert report['full:post=2']['catalogue_M'] == 128
    assert report['full:post=2']['minimum_M'] == 16
    assert report['checkerboard_opposite:post=5']['catalogue_M'] == 256
    assert report['checkerboard_opposite:post=5']['minimum_M'] == 16

    # Same order, different shift, within the pseudo-square family at minimum M.
    results = []
    for multiplier in (1, 3):
        coefficients = [multiplier * a for a in (-31, 0, 30, 0, 1)]
        spec = {
            'n': 8,
            'K': 16,
            'M': 512,
            'pre': [],
            'post': [['poly', coefficients]],
            'combine': 'xor',
            'sampling': 'checkerboard_opposite',
            'checkerboard_axis': 'vertical',
        }
        result = evaluate(spec)
        assert periods(result, certified_torus=True) == (8, 8)
        assert periods(evaluate({**spec, 'M': 256}), certified_torus=True) == (4, 4)
        residues = polynomial_values(coefficients, np.arange(1, 16, 2), 512)
        assert np.array_equal(residues, residues[::-1])
        results.append(result)
    assert signature(results[0], 'order') == signature(results[1], 'order')
    assert signature(results[0], 'shift') != signature(results[1], 'shift')
    report['pseudo_square_shift_order_collision'] = True

    comparisons = {}
    for twist, post, expected_geometry, expected_order in [
        (0, 0, True, True),
        (0, 1, True, False),
        (0, 2, True, True),
        (1, 0, False, False),
    ]:
        a, b = [sample_field(PrePowerStudyRecipe(2, twist, post), 8, sampling) for sampling in ('full', 'even_even')]
        same_geometry = partition(a.values.indices) == partition(b.values.indices)
        same_order = order_signature(a.values.labels, a.values.indices) == order_signature(
            b.values.labels, b.values.indices
        )
        assert (same_geometry, same_order) == (expected_geometry, expected_order)
        comparisons[f'twist={twist}:post={post}'] = {'same_geometry': same_geometry, 'same_order': same_order}
    report['full_even_even_comparison'] = comparisons

    square = {
        'n': 128,
        'K': 256,
        'pre': [],
        'post': [['pow', 2]],
        'combine': 'xor',
        'sampling': 'checkerboard_opposite',
        'checkerboard_axis': 'vertical',
    }
    square_report = {}
    for M in (256, 512, 1024):
        actual = periods(evaluate({**square, 'M': M}), certified_torus=True)
        assert actual == ((64, 64) if M == 256 else (128, 128))
        odd_values = polynomial_values((0, 0, 1), np.arange(1, 256, 2), M)
        symmetric = np.array_equal(odd_values, odd_values[::-1])
        assert symmetric == (M <= 512)
        square_report[M] = {'periods': actual, 'complement_symmetric': symmetric}
    report['post_square_precision_example'] = square_report
    return report


def fixed_modulus_checks():
    nodes = (1, 9, 25, 49)
    columns = [[int(np.prod([t - nodes[i] for i in range(j)], dtype=object)) for t in nodes] for j in range(1, 4)]
    report = {}
    for m in (5, 8, 9, 10, 11, 12):
        M = 1 << m
        limits = [1 << max(0, m - 3 * j - valuation(factorial(j))) for j in range(1, 4)]
        seen, orders = set(), Counter()
        for coefficients in product(*(range(limit) for limit in limits)):
            table = tuple(
                sum(a * column[i] for a, column in zip(coefficients, columns, strict=True)) % M for i in range(4)
            )
            assert table not in seen
            seen.add(table)
            differences = ((table[3] - table[0]) % M, (table[2] - table[1]) % M)
            if not any(differences) or any(delta not in (0, M // 2) for delta in differences):
                continue
            anchored = tuple((v - table[3]) % M for v in table)
            lookup = {v: i for i, v in enumerate(sorted(set(anchored)))}
            orders[tuple(lookup[v] for v in anchored)] += 1
        report[M] = {
            'coefficient_tables': len(seen),
            'minimum_period_shift_classes': sum(orders.values()),
            'order_classes': len(orders),
            'order_multiplicities': dict(Counter(orders.values())),
        }
    assert report[512]['minimum_period_shift_classes'] == 12
    assert report[512]['order_classes'] == 8

    rng = Random(0)
    M, side = 4096, 1024
    nodes = [(2 * i + 1) ** 2 for i in range(side // 2)]
    for _ in range(100):
        a, b, c = rng.randrange(1, 512, 2), rng.randrange(32), rng.randrange(4)
        values = [(a * (t - 1) + b * (t - 1) * (t - 9) + c * (t - 1) * (t - 9) * (t - 25)) % M for t in nodes]
        assert set(values) == set(range(0, M, 8))
        assert all((values[-1 - i] - values[i]) % M == M // 2 for i in range(len(nodes) // 2))
    report['N1024_M4096'] = {'shift_and_order_classes': 32768, 'draws_checked': 100}
    return report
