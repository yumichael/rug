import json
import os
import sys
from importlib import util
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import ipywidgets as widgets
import jupytext
import pytest
from IPython.core.formatters import DisplayFormatter
from IPython.display import HTML
from IPython.display import Image as NotebookImage
from IPython.extensions.autoreload import AutoreloadMagics
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import KernelManager
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell
from PIL import Image
from ruglab import exploration, pager, studio
from ruglab.exploration import PatternRecipe, PrePowerStudyRecipe, RecipeCatalogue, sample_field
from ruglab.pager import recipe_gallery

NOTEBOOKS = Path("notebooks")


def _filter_rows(gallery):
    return gallery.children[0].children


def test_gallery_displays_native_png_and_updates_it_when_paging_or_filtering():
    catalogue = RecipeCatalogue({"pre_power": (2, 4)}, lambda pre_power: PatternRecipe("or", pre_power, 0, 1))
    gallery, _ = recipe_gallery(
        catalogue, field_sizes=(8,), selected_samplings=("full",), page_size=1, preview_pixels=64
    )
    controls, preview = gallery.children
    assert isinstance(controls.children[0], widgets.HBox)
    more = next(control for control in controls.children if isinstance(control, widgets.Accordion))
    assert not more.children[0].children
    updates = []
    handle = SimpleNamespace(update=updates.append)
    controls_handle = SimpleNamespace(update=lambda value: None)
    with patch(
        "ruglab.pager.display", side_effect=[controls_handle, SimpleNamespace(update=lambda value: None), handle]
    ) as publish:
        assert DisplayFormatter().format(gallery) == ({}, {})
        assert isinstance(publish.call_args_list[0].args[0], HTML)
        assert more.children[0].children
        native = publish.call_args_list[2].args[0]
        assert isinstance(native, NotebookImage)
        assert native.data == bytes(preview.value)
        assert publish.call_args_list[2].kwargs == {"display_id": True}
    controls.children[-2].children[2].value = 2
    assert len(updates) == 1
    assert isinstance(updates[-1], NotebookImage)
    assert updates[-1].data == bytes(preview.value) != native.data
    sizes = _filter_rows(gallery)[0].children[1:]
    selected = next(box for box in sizes if box.value)
    selected.value = False
    assert isinstance(updates[-1], HTML) and updates[-1].data == ""
    selected.value = True
    assert isinstance(updates[-1], NotebookImage)
    assert updates[-1].data == bytes(preview.value)


def test_gallery_loads_preview_then_visible_controls_then_hidden_filters_automatically():
    catalogue = RecipeCatalogue({"pre_power": (2, 4)}, lambda pre_power: PatternRecipe("or", pre_power, 0, 1))
    gallery, specs = recipe_gallery(
        catalogue, field_sizes=(8,), selected_samplings=("full",), page_size=1, preview_pixels=64
    )
    controls, preview = gallery.children
    more = next(control for control in controls.children if isinstance(control, widgets.Accordion))
    queued, visible, statuses = [], [], []
    gallery._track_frontend = True
    handles = [
        SimpleNamespace(update=visible.append),
        SimpleNamespace(update=statuses.append),
        SimpleNamespace(update=lambda value: None),
    ]
    with (
        patch("ruglab.pager._schedule_stage", side_effect=queued.append),
        patch("ruglab.pager.display", side_effect=handles) as publish,
    ):
        DisplayFormatter().format(gallery)
        assert isinstance(publish.call_args_list[2].args[0], NotebookImage)
        loading = publish.call_args_list[1].args[0].data
        assert "Loading controls…" in loading and "<progress " in loading
        assert "height:30px" in loading
        assert not visible and not more.children[0].children
        assert len(queued) == 1
        queued.pop(0)()
        assert visible == [gallery._visible_controls]
        assert gallery._visible_controls.children == controls.children[:-1]
        assert "Loading controls…" in gallery._loading_html()
        gallery._visible_controls._view_count = 1
        assert "Loading parameter filters…" in statuses[-1].data
        assert not more.children[0].children and len(queued) == 1
        # Visible controls are usable while hidden filters are still pending.
        controls.children[-2].children[2].value = 2
        before_specs, before_preview = dict(specs), bytes(preview.value)
        queued.pop(0)()
        assert not queued and more.selected_index is None
        assert more.get_title(0) == "More parameter filters"
        assert "Loading parameter filters…" in statuses[-1].data
        more.children[0]._view_count = 1
        assert statuses[-1].data == controls.children[-1].value
        assert "<progress " not in statuses[-1].data
        powers = more.children[0].children[0].children[1:]
        assert all(box.value for box in powers)
        assert specs == before_specs and bytes(preview.value) == before_preview
        powers[0].value = False
        assert specs == before_specs
        assert controls.children[-2].children[2].value == 1


@pytest.mark.parametrize("source", ["explore.py", "reference.py"])
def test_text_notebook_roundtrip(source):
    book = jupytext.read(NOTEBOOKS / source)
    text = jupytext.writes(book, fmt="py:percent")
    again = jupytext.reads(text, fmt="py:percent")
    assert [c.source for c in book.cells] == [c.source for c in again.cells]


def test_gallery_reorders_dimensions_and_keeps_the_navigated_plot():
    catalogue = RecipeCatalogue(
        {"twist": (0, 1), "pre_power": (2, 4)},
        lambda twist, pre_power: PatternRecipe("or", pre_power, twist, 3),
    )
    gallery, specs = recipe_gallery(
        catalogue, field_sizes=(2,), selected_samplings=("full", "odd_odd"), preview_pixels=128
    )
    controls, preview = gallery.children
    dimension, slower, faster, grouped, _ = controls.children[-3].children
    _, _, page, density, transpose, wrap, status = controls.children[-2].children
    assert "8 plots" in status.value
    assert grouped.value == 0
    assert dimension.options[-1][0] == "Additional sampling"
    assert density.description == "Plots per page"
    assert wrap.description == "Plots per row"
    with Image.open(BytesIO(preview.value)) as image:
        assert image.width > image.height
    transpose.value = True
    assert wrap.description == "Plots per column"
    assert list(specs) == [(1, 2, "full", "full"), (1, 2, "odd_odd", "full")]
    with Image.open(BytesIO(preview.value)) as image:
        assert image.height > image.width
    transpose.value = False
    page.value = 2
    original = list(specs)
    assert original == [(2, 2, "full", "full"), (2, 2, "odd_odd", "full")]

    dimension.value = dict(dimension.options)["Sampling"]
    slower.click()
    slower.click()
    assert page.value == 1
    assert list(specs) == [(1, 2, "full", "full"), (2, 2, "full", "full")]

    faster.click()
    faster.click()
    assert page.value == 2
    assert list(specs) == original
    grouped.value = 2
    assert page.value == 1
    assert list(specs) == [(n, 2, sampling, "full") for n in (1, 2) for sampling in ("full", "odd_odd")]


def test_gallery_reuses_the_computed_field_for_additional_sampling():
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe("or", 2, 0, 3))
    with patch("ruglab.pager.sample_field", wraps=sample_field) as calculate:
        gallery, specs = recipe_gallery(
            catalogue, field_sizes=(8,), selected_samplings=("checkerboard_same",), preview_pixels=128, page_size=3
        )
        controls, preview = gallery.children
        additional = next(
            row
            for row in _filter_rows(gallery)
            if isinstance(row, widgets.HBox) and row.children[0].value == "Additional sampling"
        )
        next(box for box in additional.children[1:] if box.description == "checkerboard opposite").value = True
        names = [box.description for box in additional.children[1:]]
        assert names[names.index("checkerboard opposite") - 1] == "doubled checkerboard opposite"
        next(box for box in additional.children[1:] if box.description == "doubled checkerboard opposite").value = True
        dimension, _, faster, _, _ = controls.children[-3].children
        dimension.value = dict(dimension.options)["Additional sampling"]
        assert faster.disabled
        assert calculate.call_count == 1
        assert list(specs) == [
            (1, 8, "checkerboard_same", phase)
            for phase in ("full", "doubled_checkerboard_opposite", "checkerboard_opposite")
        ]
        assert specs[1, 8, "checkerboard_same", "full"] == specs[1, 8, "checkerboard_same", "checkerboard_opposite"]
        assert (
            specs[1, 8, "checkerboard_same", "full"]
            == specs[1, 8, "checkerboard_same", "doubled_checkerboard_opposite"]
        )
        with Image.open(BytesIO(preview.value)) as image:
            assert image.width > 2 * 128


def test_gallery_main_doubled_sampling():
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe("or", 2, 0, 3))
    gallery, specs = recipe_gallery(
        catalogue, field_sizes=(8,), selected_samplings=("doubled_checkerboard_opposite",), preview_pixels=64
    )
    sampling = next(
        row for row in _filter_rows(gallery) if isinstance(row, widgets.HBox) and row.children[0].value == "Sampling"
    )
    names = [box.description for box in sampling.children[1:]]
    assert names[names.index("checkerboard opposite") - 1] == "doubled checkerboard opposite"
    assert list(specs) == [(1, 8, "doubled_checkerboard_opposite", "full")]
    assert specs[1, 8, "doubled_checkerboard_opposite", "full"]["sampling"] == "doubled_checkerboard_opposite"


def test_pre_power_gallery_selects_other_combiners():
    catalogue = exploration.pre_power_study_catalogue()
    gallery, specs = recipe_gallery(
        catalogue,
        field_sizes=(8,),
        selected_combiners=("clmul",),
        selected_samplings=("even_even",),
        page_size=1,
        preview_pixels=64,
    )
    combiners = next(
        row for row in _filter_rows(gallery) if isinstance(row, widgets.HBox) and row.children[0].value == "Combiner"
    )
    assert len(combiners.children[1:]) == 7
    assert len(specs) == 1
    assert next(iter(specs.values()))["combine"] == "clmul"
    assert "Ready" in gallery.children[0].children[-1].value


def test_gallery_minimum_modulus_toggle_preserves_page_and_additional_sampling():
    catalogue = RecipeCatalogue({"pre_power": (2, 4)}, lambda pre_power: PrePowerStudyRecipe(pre_power, 0, 2))
    gallery, specs = recipe_gallery(
        catalogue,
        field_sizes=(8,),
        selected_samplings=("full",),
        selected_additional_samplings=("full", "checkerboard_same"),
        page_size=2,
        preview_pixels=64,
    )
    controls, preview = gallery.children
    minimum = next(c for c in controls.children if isinstance(c, widgets.Checkbox))
    page = controls.children[-2].children[2]
    original = dict(specs)
    original_preview = bytes(preview.value)
    assert {s["M"] for s in specs.values()} == {128}
    minimum.value = True
    assert list(specs) == list(original)
    assert {s["M"] for s in specs.values()} == {16}
    assert bytes(preview.value) != original_preview
    minimum.value = False
    assert specs == original
    assert bytes(preview.value) == original_preview
    page.value = 2
    second_page = list(specs)
    minimum.value = True
    assert page.value == 2
    assert list(specs) == second_page
    assert {s["M"] for s in specs.values()} == {32}


def test_gallery_marks_unattainable_minimum_modulus_panels():
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe("and", 16, 0, 7))
    gallery, specs = recipe_gallery(
        catalogue,
        field_sizes=(16,),
        selected_samplings=("even_odd",),
        minimum_post_modulus=True,
        preview_pixels=64,
    )
    controls, preview = gallery.children
    assert not specs
    assert "1 unavailable" in controls.children[-2].children[-1].value
    assert bytes(preview.value).startswith(b"\x89PNG")
    minimum = next(c for c in controls.children if isinstance(c, widgets.Checkbox))
    minimum.value = False
    assert len(specs) == 1


def test_gallery_reports_busy_through_calculation_and_rendering_even_when_preview_is_unchanged():
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe("or", 2, 0, 1))
    gallery, specs = recipe_gallery(
        catalogue, field_sizes=(8,), selected_samplings=("checkerboard_opposite",), preview_pixels=64
    )
    controls, preview = gallery.children
    activity = controls.children[-1]
    minimum = next(c for c in controls.children if isinstance(c, widgets.Checkbox))
    original_preview = bytes(preview.value)
    original_specs = dict(specs)
    assert "✓ Ready · Update #1" in activity.value
    transitions = []
    activity.observe(lambda change: transitions.append(change["new"]), names="value")

    def check_busy(function):
        def checked(*args, **kwargs):
            assert "Calculating and rendering… · Update #2" in activity.value
            assert "<progress " in activity.value
            assert bytes(preview.value) == original_preview
            return function(*args, **kwargs)

        return checked

    with (
        patch("ruglab.pager.sample_field", side_effect=check_busy(sample_field)) as calculate,
        patch("ruglab.pager.preview_grid", side_effect=check_busy(pager.preview_grid)) as render,
    ):
        minimum.value = True
        assert calculate.call_count == render.call_count == 1
    assert specs == original_specs
    assert bytes(preview.value) == original_preview
    assert "✓ Ready · Update #2" in activity.value
    assert "Preview unchanged." in activity.value
    assert " s</span>" in activity.value
    assert activity.layout.height == activity.layout.min_height == activity.layout.max_height == "30px"
    assert len(transitions) == 2
    assert "<progress " in transitions[0]
    assert "<progress " not in transitions[1]

    # A cached page still acknowledges that the control change was processed.
    with patch("ruglab.pager.sample_field") as calculate, patch("ruglab.pager.preview_grid") as render:
        minimum.value = False
        calculate.assert_not_called()
        render.assert_not_called()
    assert "✓ Ready · Update #3" in activity.value
    assert "Preview unchanged." in activity.value
    assert len(transitions) == 4


def test_gallery_status_for_empty_and_oversized_pages():
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe("or", 2, 0, 1))
    gallery, specs = recipe_gallery(catalogue, field_sizes=(8,), selected_samplings=("full",), preview_pixels=64)
    controls, preview = gallery.children
    activity = controls.children[-1]
    sizes = next(
        row for row in _filter_rows(gallery) if isinstance(row, widgets.HBox) and row.children[0].value == "Field size"
    )
    selected_size = next(box for box in sizes.children[1:] if box.value)
    selected_size.value = False
    assert "Choose a selection · Update #2" in activity.value
    assert "<progress " not in activity.value
    assert not specs and not preview.value
    assert preview.layout.display == "none"
    selected_size.value = True
    assert "✓ Ready · Update #3" in activity.value
    assert specs and preview.value

    catalogue = RecipeCatalogue({"pre_power": (2, 4, 6, 8)}, lambda pre_power: PatternRecipe("or", pre_power, 0, 1))
    gallery, specs = recipe_gallery(
        catalogue, field_sizes=(8,), selected_samplings=("full",), page_size=4, preview_pixels=4096
    )
    assert "Page too large" in gallery.children[0].children[-1].value
    assert "<progress " not in gallery.children[0].children[-1].value
    assert not specs and not gallery.children[1].value


@pytest.mark.parametrize("failure", [RuntimeError("<bad>"), KeyboardInterrupt()])
def test_gallery_status_for_failed_or_interrupted_updates_and_recovery(failure):
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe("or", 2, 0, 1))
    gallery, _ = recipe_gallery(catalogue, field_sizes=(8,), selected_samplings=("full",), preview_pixels=64)
    controls, preview = gallery.children
    activity = controls.children[-1]
    minimum = next(c for c in controls.children if isinstance(c, widgets.Checkbox))
    original_preview = bytes(preview.value)
    with patch("ruglab.pager.sample_field", side_effect=failure), pytest.raises(type(failure)):
        minimum.value = True
    assert ("Update interrupted" if isinstance(failure, KeyboardInterrupt) else "Update failed") in activity.value
    assert "<progress " not in activity.value
    assert "✓ Ready" not in activity.value
    assert bytes(preview.value) == original_preview
    if isinstance(failure, RuntimeError):
        assert "RuntimeError: &lt;bad&gt;" in activity.value
    minimum.value = False
    assert "✓ Ready · Update #3" in activity.value


def test_notebook_autoreload_resolves_new_helper_exception(tmp_path, monkeypatch):
    magics = AutoreloadMagics()
    shell = SimpleNamespace(
        extension_manager=SimpleNamespace(load_extension=lambda name: None),
        run_line_magic=lambda name, line: magics.magics['line'][name](line) if name == 'autoreload' else None,
    )
    spec = util.spec_from_file_location('ruglab._studio_reload_test', studio.__file__)
    assert spec is not None and spec.loader is not None
    setup = util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, setup)
    with patch('IPython.get_ipython', return_value=shell):
        spec.loader.exec_module(setup)
    assert magics._reloader.enabled
    assert magics._reloader.check_all
    assert not magics._reloader.deduper_reloader.enabled

    name = '_rug_reload_probe'
    path = tmp_path / f'{name}.py'
    old_source = 'def existing():\n    return 1\n'
    path.write_text(old_source)
    monkeypatch.syspath_prepend(str(tmp_path))
    probe_spec = util.spec_from_file_location(name, path)
    assert probe_spec is not None and probe_spec.loader is not None
    module = util.module_from_spec(probe_spec)
    monkeypatch.setitem(sys.modules, name, module)
    probe_spec.loader.exec_module(module)
    existing = module.existing
    modified = path.stat().st_mtime
    reloader = magics._reloader
    reloader.check_all = False
    reloader.mark_module_reloadable(name)
    reloader.modules_mtimes[name] = modified
    reloader.deduper_reloader.source_by_modname[name] = old_source
    path.write_text(
        'class PeriodTargetError(ValueError):\n'
        '    pass\n\n'
        'def new_helper():\n'
        '    raise PeriodTargetError("unattainable")\n\n'
        'def existing():\n'
        '    return new_helper()\n'
    )
    os.utime(path, (modified + 2, modified + 2))
    reloader.check()
    assert module.new_helper.__globals__ is module.__dict__
    with pytest.raises(module.PeriodTargetError, match='unattainable'):
        existing()


def test_gallery_catches_reloaded_period_exception(monkeypatch):
    class ReloadedPeriodTargetError(ValueError):
        pass

    monkeypatch.setattr(exploration, 'PeriodTargetError', ReloadedPeriodTargetError)
    catalogue = RecipeCatalogue({}, lambda: PatternRecipe('and', 16, 0, 7))
    gallery, specs = recipe_gallery(
        catalogue,
        field_sizes=(16,),
        selected_samplings=('even_odd',),
        minimum_post_modulus=True,
        preview_pixels=64,
    )
    assert not specs
    assert '1 unavailable' in gallery.children[0].children[-2].children[-1].value


@pytest.mark.integration
def test_fresh_kernel(tmp_path):
    kernels = tmp_path / 'kernels'
    location = kernels / 'rug-test'
    location.mkdir(parents=True)
    (location / 'kernel.json').write_text(
        json.dumps(
            {
                'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                'display_name': 'Rug test',
                'language': 'python',
            }
        )
    )
    manager = KernelManager(kernel_name='rug-test', kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]))
    book = jupytext.read(NOTEBOOKS / 'reference.py')
    pager = next(cell for cell in book.cells if 'back_button = widgets.Button' in cell.source)
    navigate = new_code_cell(
        """
assert page_control.value == 0
first_page = bytes(page_preview.value)
assert first_page.startswith(b"\\x89PNG")
assert page_preview.layout.width == "1200px"
width_control.value = 640
assert page_preview.layout.width == "640px"
assert page_control.value == 0
assert bytes(page_preview.value) == first_page
next_button.click()
assert page_control.value == 1
assert page_preview.layout.width == "640px"
assert bytes(page_preview.value) != first_page
back_button.click()
assert page_control.value == 0
assert bytes(page_preview.value) == first_page
"""
    )
    book.cells.append(navigate)
    client = NotebookClient(
        book,
        timeout=120,
        km=manager,
        kernel_name='rug-test',
        resources={'metadata': {'path': str(NOTEBOOKS.resolve())}},
    )
    try:
        client.execute()
    finally:
        if client.kc is not None:
            client.kc.stop_channels()
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)

    assert len(pager.outputs) == 1
    assert 'application/vnd.jupyter.widget-view+json' in pager.outputs[0].data
    assert not navigate.outputs

    # A trailing Figure expression would also render via IPython's display hook.
    images = [
        output for cell in book.cells for output in cell.get('outputs', ()) if 'image/png' in output.get('data', {})
    ]
    assert images
    assert all(output.output_type == 'display_data' for output in images)
