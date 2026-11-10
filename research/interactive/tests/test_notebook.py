import json
import sys
from io import BytesIO
from pathlib import Path

import jupytext
import pytest
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import KernelManager
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell
from PIL import Image
from ruglab.exploration import PatternRecipe, RecipeCatalogue
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
        catalogue, field_sizes=(2,), selected_samplings=("full", "odd_odd"), grouped_dimensions=0, preview_pixels=128
    )
    controls, preview = gallery.children
    dimension, slower, faster, grouped, _ = controls.children[-2].children
    _, _, page, density, transpose, wrap, status = controls.children[-1].children
    assert "8 plots" in status.value
    assert density.description == "Plots per page"
    assert wrap.description == "Plots per row"
    with Image.open(BytesIO(preview.value)) as image:
        assert image.width > image.height
    transpose.value = True
    assert wrap.description == "Plots per column"
    assert list(specs) == [(1, 2, "full"), (1, 2, "odd_odd")]
    with Image.open(BytesIO(preview.value)) as image:
        assert image.height > image.width
    transpose.value = False
    page.value = 2
    original = list(specs)
    assert original == [(2, 2, "full"), (2, 2, "odd_odd")]

    dimension.value = dict(dimension.options)["Sampling"]
    slower.click()
    slower.click()
    assert page.value == 1
    assert list(specs) == [(1, 2, "full"), (2, 2, "full")]

    faster.click()
    faster.click()
    assert page.value == 2
    assert list(specs) == original
    grouped.value = 1
    assert page.value == 1
    assert list(specs) == [(n, 2, sampling) for n in (1, 2) for sampling in ("full", "odd_odd")]


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
