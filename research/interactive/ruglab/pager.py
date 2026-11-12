"""Shared controls and pager for Cartesian recipe galleries."""

from bisect import bisect_left
from copy import deepcopy
from functools import lru_cache
from itertools import product
from math import prod
from sys import getsizeof

import ipywidgets as widgets
from PIL import Image

from .exploration import FIELD_SIZES, PeriodTargetError, RecipeCatalogue, recipe_description, sample_field
from .indexed import byte_lru
from .plotting import indexed_order_palette
from .previews import PreviewPanel, palette_preview, preview_grid
from .sampling import resample_view
from .specs import SAMPLINGS


def _product_position(options, index):
    """Decode an index in product order, with the last dimension fastest."""
    position = []
    for choices in reversed(options):
        index, digit = divmod(index, len(choices))
        position.append(choices[digit])
    return tuple(reversed(position))


def _product_rank(options, position):
    """Find the position of a key, or where it would be inserted."""
    rank = 0
    for axis, (choices, value) in enumerate(zip(options, position, strict=True)):
        digit = bisect_left(choices, value)
        rank = rank * len(choices) + digit
        if digit == len(choices) or choices[digit] != value:
            return rank * prod(map(len, options[axis + 1 :]))
    return rank


def _option_label(name, value):
    if name == "combiner":
        return value.upper()
    if name == "stratum":
        family, valuation = value
        return f"{family} (v={valuation})"
    return str(value).replace("_", " ")


def _prepared_field_bytes(result):
    field, palette = result
    labels = field.values.labels
    integers = labels.size * getsizeof(field.spec["M"]) if labels.dtype == object else 0
    return field.values.nbytes + integers + palette.nbytes


def recipe_gallery(
    catalogue: RecipeCatalogue,
    *,
    field_sizes=(128,),
    selected_combiners=None,
    selected_samplings=None,
    selected_additional_samplings=("full",),
    transposed=False,
    page_size=2,
    initial_page=1,
    preview_pixels=384,
    wrap_after=0,
    grouped_dimensions=0,
    minimum_post_modulus=False,
):
    """Browse a recipe catalogue with field size and two sampling dimensions."""
    view_dimensions = {"size": FIELD_SIZES, "sampling": SAMPLINGS, "additional_sampling": SAMPLINGS}
    if view_dimensions.keys() & catalogue.dimensions.keys():
        raise ValueError("Size and sampling dimensions are supplied by the gallery")
    dimensions = {**catalogue.dimensions, **view_dimensions}
    names = tuple(dimensions)
    axis_labels = tuple("Field size" if name == "size" else name.replace("_", " ").capitalize() for name in names)
    axis_indices = tuple(range(len(names)))
    order = list(axis_indices)
    options = tuple(tuple(range(len(values))) for values in dimensions.values())
    recipe_options = options[: len(catalogue.dimensions)]
    displayed_specs = {}
    page_anchor = None

    selections = {
        "size": field_sizes,
        "combiner": selected_combiners,
        "sampling": selected_samplings,
        "additional_sampling": selected_additional_samplings,
    }
    boxes = []
    for name, values in dimensions.items():
        selected = selections.get(name)
        boxes.append(
            tuple(
                widgets.Checkbox(
                    value=selected is None or value in selected,
                    description=_option_label(name, value),
                    indent=False,
                    layout=widgets.Layout(width="auto"),
                )
                for value in values
            )
        )

    density_control = widgets.BoundedIntText(
        min=1,
        max=max(16, page_size),
        value=page_size,
        style={"description_width": "initial"},
        layout=widgets.Layout(width="170px"),
    )
    transpose_control = widgets.Checkbox(
        value=transposed,
        description="Transpose grid",
        tooltip="Fill down columns when ungrouped, or turn each group into a column.",
        indent=False,
        layout=widgets.Layout(width="135px"),
    )
    minimum_control = widgets.Checkbox(
        value=minimum_post_modulus,
        description="Minimum M (displayed period)",
        tooltip="Use the smallest power of two giving the field size as both least axis periods, with K fixed.",
        indent=False,
        layout=widgets.Layout(width="auto"),
    )
    wrap_control = widgets.BoundedIntText(
        min=0,
        max=max(16, page_size, wrap_after),
        value=wrap_after,
        tooltip="Set to 0 to leave the page unwrapped.",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="155px"),
    )
    page_control = widgets.BoundedIntText(
        min=1, max=max(1, prod(map(len, options))), value=initial_page, description="Page"
    )
    back_button = widgets.Button(description="Back", layout=widgets.Layout(width="auto"))
    next_button = widgets.Button(description="Next", layout=widgets.Layout(width="auto"))
    page_status = widgets.HTML()
    page_preview = widgets.Image(format="png", layout=widgets.Layout(max_width="100%", align_self="flex-start"))

    dimension_control = widgets.Dropdown(
        description="Dimension",
        options=list(zip(axis_labels, axis_indices, strict=True)),
        layout=widgets.Layout(width="220px"),
    )
    slower_button = widgets.Button(description="Slower", layout=widgets.Layout(width="auto"))
    faster_button = widgets.Button(description="Faster", layout=widgets.Layout(width="auto"))
    order_label = widgets.Label()
    grouped_control = widgets.BoundedIntText(
        description="Group fastest",
        min=0,
        max=len(names),
        value=grouped_dimensions,
        tooltip="Keep the rightmost dimensions together in one entry. Set to 0 to paginate individual plots.",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="145px"),
    )

    @lru_cache(maxsize=128)
    def recipe_at(position):
        parameters = {
            name: values[index] for (name, values), index in zip(catalogue.dimensions.items(), position, strict=True)
        }
        return catalogue.build(**parameters)

    @byte_lru(84, 128 << 20, _prepared_field_bytes)
    def prepared_field(recipe, size, sampling, minimum_m):
        field = sample_field(recipe, size, sampling, minimum_post_modulus=minimum_m)
        return field, indexed_order_palette(field.values, field.spec["color"])

    @lru_cache(maxsize=84)
    def recipe_panel(recipe, size, sampling, additional_sampling, minimum_m):
        try:
            field, palette = prepared_field(recipe, size, sampling, minimum_m)
        except PeriodTargetError as error:
            detail = str(error).replace(" at K=", "\nat K=")
            caption = f"{sampling.replace('_', ' ')} · unavailable\n{detail}"
            return PreviewPanel(Image.new("RGB", (preview_pixels, preview_pixels), "#f4f4f4"), caption), None
        indices = resample_view(field.values.indices, additional_sampling)
        spec = field.spec
        k, m = (spec[key].bit_length() - 1 for key in ("K", "M"))
        name = sampling.replace("_", " ")
        caption = (
            f"{name} · {field.repeat_shape}\n"
            f"{field.zero_fraction:.1%} zero · {field.distinct_values:,} values\n"
            f"K=2^{k} · M=2^{m}"
        )
        if additional_sampling != "full":
            height, width = indices.shape
            additional_name = additional_sampling.replace("_", " ")
            caption += f"\n↳ {additional_name} · {width}x{height}"
        return PreviewPanel(palette_preview(indices, palette, preview_pixels), caption), spec

    def render_page(entries, transpose, wrap, minimum_m):
        rows = []
        specs = {}
        for cases in entries:
            headings = []
            panels = []
            for case in cases:
                recipe_position = case[: len(recipe_options)]
                number = _product_rank(recipe_options, recipe_position) + 1
                recipe = recipe_at(recipe_position)
                size_index, sampling_index, additional_index = case[len(recipe_options) :]
                size = FIELD_SIZES[size_index]
                sampling = SAMPLINGS[sampling_index]
                additional_sampling = SAMPLINGS[additional_index]
                heading = f"#{number} {recipe.combiner.upper()} · {size}x{size}"
                description = recipe_description(recipe, size)
                panel, spec = recipe_panel(recipe, size, sampling, additional_sampling, minimum_m)
                if spec is not None:
                    specs[number, size, sampling, additional_sampling] = spec
                headings.append((heading, description))
                panels.append(panel)
            if all(heading == headings[0] for heading in headings):
                heading = " · ".join(headings[0])
            else:
                heading = ""
                panels = [
                    PreviewPanel(panel.image, "\n".join((*title, panel.caption)))
                    for title, panel in zip(headings, panels, strict=True)
                ]
            rows.append((heading, panels))
        return preview_grid(rows, preview_pixels, transpose=transpose, wrap_after=wrap), specs

    cached_page = lru_cache(maxsize=8)(render_page)

    def redraw(change=None):
        nonlocal page_anchor

        page_size = density_control.value
        transpose = transpose_control.value
        grouped = grouped_control.value
        if grouped:
            density_control.description = "Columns per page" if transpose else "Rows per page"
            wrap_control.description = "Wrap columns at" if transpose else "Wrap rows at"
        else:
            density_control.description = "Plots per page"
            wrap_control.description = "Plots per column" if transpose else "Plots per row"
        selected = tuple(tuple(i for i, box in enumerate(axis) if box.value) for axis in boxes)
        split = len(order) - grouped
        entry_options = tuple(selected[i] for i in order[:split])
        panel_options = tuple(selected[i] for i in order[split:])
        panels_per_entry = prod(map(len, panel_options))
        entry_count = prod(map(len, entry_options)) if panels_per_entry else 0
        page_count = max(1, (entry_count + page_size - 1) // page_size)
        to_canonical = tuple(order.index(i) for i in axis_indices)

        if entry_count and (page_anchor is None or (change and change["owner"] is page_control)):
            first = (min(page_control.value, page_count) - 1) * page_size
            position = _product_position(entry_options, first) + _product_position(panel_options, 0)
            page_anchor = tuple(position[i] for i in to_canonical)
        page = 1
        if entry_count and page_anchor is not None:
            anchor = tuple(page_anchor[i] for i in order[:split])
            rank = min(_product_rank(entry_options, anchor), entry_count - 1)
            page = rank // page_size + 1

        # A layout or filter update must not replace the last navigated case.
        page_control.unobserve(redraw, names="value")
        try:
            with page_control.hold_sync():
                page_control.max = page_count
                page_control.value = page
        finally:
            page_control.observe(redraw, names="value")
        back_button.disabled = page == 1
        next_button.disabled = page == page_count
        first = (page - 1) * page_size
        stop = min(first + page_size, entry_count)
        page_status.value = (
            f"Page {page} of {page_count} · {entry_count:,} entries · {entry_count * panels_per_entry:,} plots"
        )
        page_panels = (stop - first) * panels_per_entry
        estimated_pixels = page_panels * (preview_pixels + 8) * (preview_pixels + 130)
        if not entry_count or estimated_pixels > 48 << 20:
            displayed_specs.clear()
            message = (
                "Select at least one value for each dimension."
                if not entry_count
                else "This page is too large. Reduce the page size, group fewer dimensions, or filter some values."
            )
            page_status.value += f" · {message}"
            page_preview.layout.display = "none"
            page_preview.value = b""
            return

        panel_positions = tuple(product(*panel_options))
        page_entries = []
        for index in range(first, stop):
            entry = _product_position(entry_options, index)
            positions = (entry + panel for panel in panel_positions)
            page_entries.append(tuple(tuple(position[i] for i in to_canonical) for position in positions))
        # Cache complete small pages for instant revisits. Larger pages reuse panels.
        render = cached_page if page_panels <= 21 else render_page
        # The renderer puts entries in columns to fill a flat page across rows.
        entries_as_columns = transpose if grouped else not transpose
        png, specs = render(tuple(page_entries), entries_as_columns, wrap_control.value, minimum_control.value)
        if minimum_control.value and len(specs) < page_panels:
            page_status.value += f" · {page_panels - len(specs)} unavailable"
        displayed_specs.clear()
        displayed_specs.update(deepcopy(specs))
        page_preview.value = png
        page_preview.layout.display = ""

    def update_order_controls(change=None):
        selected_axis = dimension_control.value
        if not isinstance(selected_axis, int):
            return
        index = order.index(selected_axis)
        slower_button.disabled = index == 0
        faster_button.disabled = index == len(order) - 1
        split = len(order) - grouped_control.value
        labels = [axis_labels[i] for i in order]
        parts = [" → ".join(labels[:split]), " → ".join(labels[split:])]
        order_label.value = "Slow → fast: " + " | ".join(part for part in parts if part)
        if grouped_control.value:
            order_label.value += " (right of | kept together per entry)"

    def move_dimension(step):
        selected_axis = dimension_control.value
        if not isinstance(selected_axis, int):
            return
        index = order.index(selected_axis)
        target = index + step
        if 0 <= target < len(order):
            order[index], order[target] = order[target], order[index]
            update_order_controls()
            redraw()

    def change_grouping(change):
        update_order_controls()
        redraw()

    def choice_row(axis):
        return widgets.HBox(
            [widgets.Label(axis_labels[axis], layout=widgets.Layout(width="140px")), *boxes[axis]],
            layout=widgets.Layout(flex_flow="row wrap"),
        )

    quick_names = ("size", "combiner", "sampling", "additional_sampling")
    quick_filters: list[widgets.HBox | widgets.Accordion] = [
        choice_row(names.index(name)) for name in quick_names if name in names
    ]
    other_filters = [choice_row(i) for i, name in enumerate(names) if name not in quick_names]
    if other_filters:
        quick_filters.append(
            widgets.Accordion(
                children=[widgets.VBox(other_filters)], titles=["More parameter filters"], selected_index=None
            )
        )

    back_button.on_click(lambda button: setattr(page_control, "value", page_control.value - 1))
    next_button.on_click(lambda button: setattr(page_control, "value", page_control.value + 1))
    slower_button.on_click(lambda button: move_dimension(-1))
    faster_button.on_click(lambda button: move_dimension(1))
    dimension_control.observe(update_order_controls, names="value")
    grouped_control.observe(change_grouping, names="value")
    for control in (
        *[box for axis in boxes for box in axis],
        density_control,
        page_control,
        transpose_control,
        wrap_control,
        minimum_control,
    ):
        control.observe(redraw, names="value")
    controls = widgets.VBox(
        [
            *quick_filters,
            minimum_control,
            widgets.HBox(
                [dimension_control, slower_button, faster_button, grouped_control, order_label],
                layout=widgets.Layout(flex_flow="row wrap"),
            ),
            widgets.HBox(
                [back_button, next_button, page_control, density_control, transpose_control, wrap_control, page_status],
                layout=widgets.Layout(flex_flow="row wrap"),
            ),
        ]
    )
    update_order_controls()
    redraw()
    gallery_view = widgets.VBox([controls, page_preview], layout=widgets.Layout(width="100%"))
    return gallery_view, displayed_specs
