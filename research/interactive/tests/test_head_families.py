"""Coverage and matched-example behavior of the competing head proposals."""

from itertools import product

import numpy as np
import pytest
from ruglab.exploration import PeriodTargetError, head_family_catalogue, sample_field
from ruglab.head_families import PROPOSALS, audit_head_family_proposals, head_family_cases, head_family_keys
from ruglab.order_classes import ORDER_COMBINERS, OrderClassRecipe, head_powers
from ruglab.pager import recipe_gallery


@pytest.mark.parametrize("size", [8, 16, 64, 512])
def test_every_proposal_covers_each_configured_head_base_exactly_once(size):
    twists = ((), (1,), (3, -2, 1), (-11, 7, -3, 9, 1))
    expected = set(product(head_powers(size), twists, ORDER_COMBINERS))
    cases = head_family_cases(size, twists=twists)
    for proposal in PROPOSALS:
        observed = [base for case in cases if case.proposal == proposal for base in case.members]
        assert len(observed) == len(set(observed))
        assert set(observed) == expected
        for case in cases:
            if case.proposal == proposal:
                assert all(head_family_keys(size, *base)[proposal] == case.category for base in case.members)


def test_domain_adaptive_proposal_separates_six_and_eight_at_512():
    for q in (6, 8):
        assert head_family_keys(64, q, (), "or")["even_branch"] == "Top-bit binary"
        assert head_family_keys(512, q, (), "or")["bit_depth"] == "Middle-bit modulation"
    assert head_family_keys(512, 6, (), "or")["even_branch"] == "One-layer multilevel"
    assert head_family_keys(512, 8, (), "or")["even_branch"] == "Interior-bit binary"
    assert head_family_keys(1024, 10, (), "or")["bit_depth"] == "Deep-bit modulation"


def test_or_twist_refinement_has_all_three_masks_and_small_domain_fallback():
    assert {head_family_keys(64, 2, q, "or")["or_twist_mask"] for q in ((), (1,), (3,))} == {
        "OR: 0 forced bits",
        "OR: 1 forced bits",
        "OR: 2 forced bits",
    }
    assert head_family_keys(8, 2, (1,), "or")["or_twist_mask"] == "Small-domain OR"


def test_same_base_and_order_draw_are_identical_across_proposals():
    cases = head_family_cases(32, seed=7)
    seen = {}
    for case in cases:
        for i in range(len(case.members)):
            recipe = case.recipe(7, i)
            key = (recipe.pre_power, recipe.twist, recipe.combiner, recipe.draw)
            field = sample_field(recipe, 32, "checkerboard_opposite", centered=True)
            ordinary = sample_field(
                OrderClassRecipe("head", 7, recipe.draw, recipe.pre_power, recipe.twist, recipe.combiner),
                32,
                "checkerboard_opposite",
                centered=True,
            )
            assert np.array_equal(field.result.values, ordinary.result.values)
            assert field.spec["color_offset"] == ordinary.spec["color_offset"]
            if key in seen:
                assert field.spec["post"] == seen[key]
            seen[key] = field.spec["post"]
            assert field.spec["order_sample"]["family_proposal"]["family"] == case.category


def test_gallery_groups_family_examples_and_marks_stale_domains_unavailable():
    catalogue = head_family_catalogue(size=16, seed=0, draws=2, proposals=("even_branch",))
    view, specs = recipe_gallery(
        catalogue,
        field_sizes=(16,),
        selected_samplings=("checkerboard_opposite",),
        selected_m_selections=("minimum_period",),
        grouped_dimensions=4,
        page_size=1,
        preview_pixels=64,
    )
    assert len(specs) == 2
    labels = {s["order_sample"]["family_proposal"]["family"] for s in specs.values()}
    assert len(labels) == 1
    assert view.children[1].value
    recipe = catalogue.recipes()[0]
    with pytest.raises(PeriodTargetError, match="Rebuild"):
        sample_field(recipe, 32, "checkerboard_opposite")


def test_bounded_audit_detects_known_cross_family_raw_partition_overlap():
    record = audit_head_family_proposals((8,))["domain_checks"][0]
    assert record["bases"] == 24
    assert record["distinct_raw_partitions"] == 6
    assert record["proposals"]["carry_behavior"]["raw_partitions_crossing_families"] == 1


def test_gallery_rebuilds_family_choices_and_recipes_on_domain_change():
    import ipywidgets as widgets

    view, specs = recipe_gallery(
        head_family_catalogue(size=64, draws=1, proposals=("even_branch",)),
        field_sizes=(64,),
        selected_samplings=("checkerboard_opposite",),
        selected_m_selections=("minimum_period",),
        grouped_dimensions=4,
        page_size=8,
        preview_pixels=32,
    )

    def descendants(widget):
        yield widget
        for child in getattr(widget, "children", ()):
            yield from descendants(child)

    def checkbox(label):
        return next(w for w in descendants(view) if isinstance(w, widgets.Checkbox) and w.description == label)

    # Temporarily empty size selections must retain the controls until a new choice.
    checkbox("64").value = False
    checkbox("512").value = True
    labels = {w.description for w in descendants(view) if isinstance(w, widgets.Checkbox)}
    assert "Even branch: One-layer multilevel" in labels
    assert specs
    assert {s["order_sample"]["family_proposal"]["side"] for s in specs.values()} == {512}
    assert "One-layer multilevel" in {s["order_sample"]["family_proposal"]["family"] for s in specs.values()}
    checkbox("64").value = True
    assert {s["order_sample"]["family_proposal"]["side"] for s in specs.values()} == {64, 512}


def test_pager_pages_complete_proposals_with_unequal_family_counts():
    import ipywidgets as widgets

    catalogue = head_family_catalogue(size=64, draws=2)
    view, specs = recipe_gallery(
        catalogue,
        field_sizes=(64,),
        selected_samplings=("checkerboard_opposite",),
        selected_m_selections=("minimum_period",),
        grouped_dimensions=4,
        page_size=4,
        preview_pixels=32,
    )

    def descendants(widget):
        yield widget
        for child in getattr(widget, "children", ()):
            yield from descendants(child)

    controls = list(descendants(view))
    mode = next(w for w in controls if isinstance(w, widgets.Dropdown) and w.description == "Page by")
    page = next(w for w in controls if isinstance(w, widgets.BoundedIntText) and w.description == "Page")
    mode.value = "Family groups"
    assert page.max == len(PROPOSALS)
    counts = []
    for number, proposal in enumerate(PROPOSALS, 1):
        page.value = number
        expected = {c.category for c in catalogue.dimensions["family"] if c.proposal == proposal}
        info = [s["order_sample"]["family_proposal"] for s in specs.values()]
        assert {i["proposal"] for i in info} == {proposal}
        assert {i["family"] for i in info} == expected
        assert len(info) == 2 * len(expected)
        counts.append(len(info))
    assert len(set(counts)) > 1
    page.value = 1
    density = next(w for w in controls if isinstance(w, widgets.BoundedIntText) and w.description == "Groups per page")
    density.value = 2
    assert page.max == 3
    assert {s["order_sample"]["family_proposal"]["proposal"] for s in specs.values()} == set(tuple(PROPOSALS)[:2])
    mode.value = "Rows"
    assert specs


@pytest.mark.parametrize("size", [8, 16, 64, 512, 1024])
def test_depth_and_branch_families_follow_represented_depth(size):
    cases = head_family_cases(size, proposals=("bit_depth", "even_branch"))
    for proposal in ("bit_depth", "even_branch"):
        ranges = []
        for case in cases:
            if case.proposal == proposal:
                depths = [q - (q & -q).bit_length() - 1 for q, _, _ in case.members]
                ranges.append((min(depths), max(depths)))
        assert ranges == sorted(ranges)
    if size == 1024:
        assert [c.category for c in cases if c.proposal == "bit_depth"] == [
            "Low-bit crossing",
            "Stride boundary",
            "Middle-bit modulation",
            "Deep-bit modulation",
        ]
    if size == 64:
        assert [c.category for c in cases if c.proposal == "even_branch"] == [
            "Multiple even layers",
            "Interior-bit binary",
            "Top-bit binary",
        ]
    if size == 512:
        assert [c.category for c in cases if c.proposal == "even_branch"] == [
            "Multiple even layers",
            "One-layer multilevel",
            "Interior-bit binary",
        ]
