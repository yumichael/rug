"""Compare all three actual selectors inside the opposite-checkerboard tail."""

import numpy as np
from ruglab.diagnostics import periods
from ruglab.engine import evaluate
from ruglab.exploration import (
    _STUDY_POSTS,
    M_SELECTIONS,
    PatternRecipe,
    PrePowerStudyRecipe,
    _base_field,
    _distinct_polynomial,
    _finish_field,
    _pre_modulus,
    sample_field,
)


def selector_fields(recipe, side):
    return [sample_field(recipe, side, 'checkerboard_opposite', m_selection=method) for method in M_SELECTIONS]


def check_agreement(fields, expected):
    assert [field.spec['M'] for field in fields] == [expected] * len(M_SELECTIONS)
    reference = fields[0].values.expand()
    assert all(np.array_equal(reference, field.values.expand()) for field in fields[1:])


def run_checks():
    report = {}
    comparisons = 0
    # All displayed twists and posts, across several distinct exponent valuations.
    for q in (10, 12, 16, 48, 64):
        for twist in range(16):
            for post, coefficients in enumerate(_STUDY_POSTS):
                derivative = sum(i * a for i, a in enumerate(coefficients))
                K = _pre_modulus(q, 128, 'checkerboard_opposite', 'or')
                check_agreement(
                    selector_fields(PrePowerStudyRecipe(q, twist, post), 128), K * (derivative & -derivative)
                )
                comparisons += 1
    report['all_twists_posts_N128'] = {'recipes': comparisons, 'selectors_per_recipe': len(M_SELECTIONS)}

    comparisons = 0
    for side, q in ((8, 6), (32, 6), (128, 10), (512, 10), (1024, 12)):
        for combiner in ('or', 'xor', 'add', 'absdiff'):
            for post in (0, 3, 9):
                derivative = sum(i * a for i, a in enumerate(_STUDY_POSTS[post]))
                K = _pre_modulus(q, side, 'checkerboard_opposite', combiner)
                recipe = PrePowerStudyRecipe(q, 0, post, combiner=combiner)
                check_agreement(selector_fields(recipe, side), K * (derivative & -derivative))
                comparisons += 1
    report['domain_and_combiner_sweep'] = {'recipes': comparisons, 'selectors_per_recipe': len(M_SELECTIONS)}

    comparisons = 0
    for twist in (0, 1, -3):
        for power in (1, 2, 3, 4, 7, 14, 32, 64):
            K = _pre_modulus(10, 128, 'checkerboard_opposite', 'or')
            check_agreement(selector_fields(PatternRecipe('or', 10, twist, power), 128), K * (power & -power))
            comparisons += 1
    report['positive_post_powers'] = {'recipes': comparisons, 'selectors_per_recipe': len(M_SELECTIONS)}

    # Same tail, monotone positive-coefficient post, but outside the ten-post family.
    side, q = 128, 10
    K = _pre_modulus(q, side, 'checkerboard_opposite', 'or')
    base, repeat, counts = _base_field(q, 0, K, 'or', side, 'checkerboard_opposite')
    coefficients = (0, 6, 1)
    outputs, catalogue = _distinct_polynomial(base.labels.astype(object), coefficients)
    spec = {
        'n': side,
        'K': K,
        'M': catalogue,
        'pre': [['pow', q]],
        'post': [['poly', coefficients]],
        'sampling': 'checkerboard_opposite',
        'checkerboard_axis': 'vertical',
        'combine': 'or',
    }
    counterexample = {}
    for method in M_SELECTIONS:
        field = _finish_field(base, outputs, counts, spec, repeat, method)
        counterexample[method] = {'M': field.spec['M'], 'groups': field.distinct_values}
    assert [counterexample[method]['M'] for method in M_SELECTIONS] == [4096, 4096, 2048]
    assert periods(evaluate({**spec, 'M': 2048}), certified_torus=True) == (128, 128)
    assert periods(evaluate({**spec, 'M': 1024}), certified_torus=True) != (128, 128)
    report['outside_catalogue_H_z2_plus_6z'] = counterexample
    return report


if __name__ == '__main__':
    print(run_checks())
