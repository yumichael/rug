"""Shared controls and pager for recipe galleries."""

from copy import deepcopy
from functools import lru_cache

import ipywidgets as widgets

from .exploration import FIELD_SIZES, recipe_description, sample_field
from .previews import PreviewPanel, indexed_preview, preview_grid
from .specs import SAMPLINGS


def recipe_gallery(
    recipes,
    *,
    field_sizes=(128,),
    selected_combiners=None,
    selected_samplings=None,
    transposed=False,
    page_size=2,
    initial_page=1,
    preview_pixels=384,
):
    """Return a gallery widget and its live dictionary of displayed specifications."""
    research_recipes = list(enumerate(recipes, 1))
    displayed_specs = {}
    page_anchor = None

    def choice_boxes(options, selected, width):
        return {
            value: widgets.Checkbox(
                value=selected is None or value in selected,
                description=label,
                indent=False,
                layout=widgets.Layout(width=width),
            )
            for value, label in options
        }

    size_controls = choice_boxes(((size, str(size)) for size in FIELD_SIZES), field_sizes, "72px")
    combiners = sorted({recipe.combiner for _, recipe in research_recipes})
    combiner_controls = choice_boxes(((name, name.upper()) for name in combiners), selected_combiners, "88px")
    sampling_controls = choice_boxes(((name, name.replace("_", " ")) for name in SAMPLINGS), selected_samplings, "auto")
    filter_controls = (*size_controls.values(), *combiner_controls.values(), *sampling_controls.values())
    density_control = widgets.BoundedIntText(
        min=1,
        max=max(16, page_size),
        value=page_size,
        description="Rows per page",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="170px"),
    )
    transpose_control = widgets.Checkbox(
        value=transposed, description="Transpose grid", indent=False, layout=widgets.Layout(width="135px")
    )
    page_control = widgets.BoundedIntText(
        min=1, max=max(1, len(research_recipes) * len(FIELD_SIZES)), value=initial_page, description="Page"
    )
    back_button = widgets.Button(description="Back", layout=widgets.Layout(width="auto"))
    next_button = widgets.Button(description="Next", layout=widgets.Layout(width="auto"))
    page_status = widgets.HTML()
    page_preview = widgets.Image(format="png", layout=widgets.Layout(max_width="100%", align_self="flex-start"))

    @lru_cache(maxsize=84)
    def recipe_panel(recipe, size, sampling, pixels):
        field = sample_field(recipe, size, sampling)
        spec = field.spec
        k, m = (spec[key].bit_length() - 1 for key in ("K", "M"))
        name = sampling.replace("_", " ")
        caption = (
            f"{name} · {field.repeat_shape}\n"
            f"{field.zero_fraction:.1%} zero · {field.distinct_values:,} values\n"
            f"K=2^{k} · M=2^{m}"
        )
        preview = indexed_preview(field.values, spec["color"], pixels)
        return PreviewPanel(preview, caption), spec

    def render_page(entries, samplings, pixels, transpose):
        rows = []
        specs = {}
        for number, recipe, size in entries:
            heading = f"#{number} {recipe.combiner.upper()} · {size}x{size} · {recipe_description(recipe, size)}"
            panels = []
            for sampling in samplings:
                panel, specs[number, size, sampling] = recipe_panel(recipe, size, sampling, pixels)
                panels.append(panel)
            rows.append((heading, panels))
        return preview_grid(rows, pixels, transpose=transpose), specs

    cached_page = lru_cache(maxsize=8)(render_page)

    def redraw(change=None):
        nonlocal page_anchor

        rows_per_page = density_control.value
        transpose = transpose_control.value
        density_control.description = "Columns per page" if transpose else "Rows per page"
        sizes = [size for size, box in size_controls.items() if box.value]
        selected_combiners = {name for name, box in combiner_controls.items() if box.value}
        samplings = tuple(name for name, box in sampling_controls.items() if box.value)
        entries = [
            (number, recipe, size)
            for number, recipe in research_recipes
            if recipe.combiner in selected_combiners
            for size in sizes
        ]
        page_count = max(1, (len(entries) + rows_per_page - 1) // rows_per_page)
        if entries and (page_anchor is None or (change and change["owner"] is page_control)):
            number, _, size = entries[(min(page_control.value, page_count) - 1) * rows_per_page]
            page_anchor = (number, size)
        index = next(
            (
                i
                for i, (number, _, size) in enumerate(entries)
                if page_anchor is not None and (number, size) >= page_anchor
            ),
            max(0, len(entries) - 1),
        )
        page = index // rows_per_page + 1
        # Filter-driven page updates must preserve the anchor, even when the old page is out of range.
        page_control.unobserve(redraw, names="value")
        try:
            with page_control.hold_sync():
                page_control.max = page_count
                page_control.value = page
        finally:
            page_control.observe(redraw, names="value")
        back_button.disabled = page == 1
        next_button.disabled = page == page_count
        if not entries or not samplings:
            displayed_specs.clear()
            page_status.value = "Select at least one field size, combiner, and sampling method."
            page_preview.layout.display = "none"
            page_preview.value = b""
            return
        first = (page - 1) * rows_per_page
        page_status.value = f"Page {page} of {page_count} · {len(entries):,} entries"
        page_entries = tuple(entries[first : first + rows_per_page])
        # Cache complete small pages for instant revisits. Larger pages reuse panels.
        render = cached_page if len(page_entries) <= 3 else render_page
        png, specs = render(page_entries, samplings, preview_pixels, transpose)
        displayed_specs.clear()
        displayed_specs.update(deepcopy(specs))
        page_preview.value = png
        page_preview.layout.display = ""

    def previous_page(button):
        page_control.value -= 1

    def next_page(button):
        page_control.value += 1

    def choice_row(label, boxes):
        return widgets.HBox(
            [widgets.Label(label, layout=widgets.Layout(width="80px")), *boxes.values()],
            layout=widgets.Layout(flex_flow="row wrap"),
        )

    back_button.on_click(previous_page)
    next_button.on_click(next_page)
    for control in (*filter_controls, density_control, page_control, transpose_control):
        control.observe(redraw, names="value")
    controls = widgets.VBox(
        [
            choice_row("Field sizes", size_controls),
            choice_row("Combiners", combiner_controls),
            choice_row("Samplings", sampling_controls),
            widgets.HBox(
                [back_button, next_button, page_control, density_control, transpose_control, page_status],
                layout=widgets.Layout(flex_flow="row wrap"),
            ),
        ]
    )
    redraw()
    gallery_view = widgets.VBox([controls, page_preview], layout=widgets.Layout(width="100%"))
    return gallery_view, displayed_specs
