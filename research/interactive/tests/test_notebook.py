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
from IPython.extensions.autoreload import AutoreloadMagics
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import KernelManager
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell
from PIL import Image
from ruglab import exploration, studio
from ruglab.exploration import PatternRecipe, PrePowerStudyRecipe, RecipeCatalogue, sample_field
from ruglab.pager import recipe_gallery

NOTEBOOKS = Path("notebooks")


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
    dimension, slower, faster, grouped, _ = controls.children[-2].children
    _, _, page, density, transpose, wrap, status = controls.children[-1].children
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
            catalogue, field_sizes=(8,), selected_samplings=("checkerboard_same",), preview_pixels=128
        )
        controls, preview = gallery.children
        additional = next(row for row in controls.children if row.children[0].value == "Additional sampling")
        next(box for box in additional.children[1:] if box.description == "checkerboard opposite").value = True
        dimension, _, faster, _, _ = controls.children[-2].children
        dimension.value = dict(dimension.options)["Additional sampling"]
        assert faster.disabled
        assert calculate.call_count == 1
        assert list(specs) == [(1, 8, "checkerboard_same", phase) for phase in ("full", "checkerboard_opposite")]
        assert specs[1, 8, "checkerboard_same", "full"] == specs[1, 8, "checkerboard_same", "checkerboard_opposite"]
        with Image.open(BytesIO(preview.value)) as image:
            assert image.width > 2 * 128


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
    page = controls.children[-1].children[2]
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
    assert "1 unavailable" in controls.children[-1].children[-1].value
    assert bytes(preview.value).startswith(b"\x89PNG")
    minimum = next(c for c in controls.children if isinstance(c, widgets.Checkbox))
    minimum.value = False
    assert len(specs) == 1


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
    assert '1 unavailable' in gallery.children[0].children[-1].children[-1].value


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
