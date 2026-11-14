"""Shared controls and pager for Cartesian recipe galleries."""

from bisect import bisect_left
from copy import deepcopy
from functools import lru_cache
from html import escape
from itertools import product
from math import prod
from sys import getsizeof
from time import perf_counter

import ipywidgets as widgets
from IPython import get_ipython
from IPython.display import HTML, DisplayHandle, display
from IPython.display import Image as NotebookImage
from ipywidgets.widgets.widget_bool import CheckboxStyle
from PIL import Image

from . import exploration
from .exploration import FIELD_SIZES, M_SELECTIONS, RecipeCatalogue, recipe_description, sample_field
from .indexed import byte_lru
from .plotting import indexed_order_palette
from .previews import PreviewPanel, palette_preview, preview_grid
from .sampling import resample_view
from .specs import ADDITIONAL_SAMPLINGS, SAMPLINGS


def _schedule_stage(callback):
    shell = get_ipython()
    kernel = getattr(shell, "kernel", None)
    loop = getattr(kernel, "io_loop", None)
    if loop is None:
        callback()
    else:
        loop.add_callback(callback)


class _GalleryView(widgets.VBox):
    """Display the preview independently of the widget frontend's startup."""

    def __init__(self, controls, preview, load_hidden):
        super().__init__([controls, preview], layout=widgets.Layout(width="100%"))
        self._preview_displays: list[DisplayHandle] = []
        self._load_hidden = load_hidden
        self._hidden_loaded = False
        self._visible_controls = widgets.VBox(controls.children[:-1], layout=controls.layout, _view_count=0)
        self._hidden_view = None
        self._status_displays: list[DisplayHandle] = []
        self._status = controls.children[-1]
        self._track_frontend = getattr(get_ipython(), "kernel", None) is not None
        self._visible_controls.observe(self._update_loading, names="_view_count")
        self._status.observe(self._update_loading, names="value")
        preview.observe(self._update_preview, names="value")

    def _native_preview(self):
        data = bytes(self.children[1].value)
        return NotebookImage(data=data) if data else HTML("")

    def _loading_html(self):
        visible_ready = (self._visible_controls._view_count or 0) > 0
        hidden_ready = self._hidden_loaded and (self._hidden_view is None or (self._hidden_view._view_count or 0) > 0)
        if not self._track_frontend or (visible_ready and hidden_ready):
            return self._status.value
        label = "Loading parameter filters…" if visible_ready else "Loading controls…"
        return (
            '<div role="status" aria-live="polite" style="box-sizing:border-box;height:30px;'
            'display:flex;align-items:center;gap:10px;overflow:hidden;white-space:nowrap;'
            'background:#fff3cd;color:#a66a00;border-left:4px solid #a66a00;'
            'border-radius:4px;padding:4px 8px;font-size:13px">'
            f'<strong>⏳ {label}</strong><progress aria-label="{label}" '
            'style="width:80px;height:8px;margin:0"></progress></div>'
        )

    def _update_loading(self, change=None):
        for handle in self._status_displays:
            handle.update(HTML(self._loading_html()))

    def _ipython_display_(self):  # noqa: PLW3201 - IPython rich-display protocol.
        controls_slot = display(HTML(""), display_id=True)
        status_slot = display(HTML(self._loading_html()), display_id=True)
        if status_slot is not None:
            self._status_displays.append(status_slot)
        handle = display(self._native_preview(), display_id=True)
        if handle is not None:
            self._preview_displays.append(handle)

        def load_hidden():
            if not self._hidden_loaded:
                self._hidden_view = self._load_hidden()
                self._hidden_loaded = True
                if self._hidden_view is not None:
                    self._hidden_view.observe(self._update_loading, names="_view_count")
                self._update_loading()

        def show_controls():
            if controls_slot is None:
                display(self._visible_controls)
            else:
                controls_slot.update(self._visible_controls)
            _schedule_stage(load_hidden)

        _schedule_stage(show_controls)

    def _update_preview(self, change):
        for handle in self._preview_displays:
            handle.update(self._native_preview())


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
    if name == "m_selection":
        return {"catalogue": "Catalogue", "distinct_outputs": "Distinct outputs", "minimum_period": "Minimum period"}[
            value
        ]
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
    selected_m_selections=None,
):
    """Browse a recipe catalogue with field size and two sampling dimensions."""
    view_dimensions = {
        "size": FIELD_SIZES,
        "m_selection": M_SELECTIONS,
        "sampling": SAMPLINGS,
        "additional_sampling": ADDITIONAL_SAMPLINGS,
    }
    if view_dimensions.keys() & catalogue.dimensions.keys():
        raise ValueError("Size and sampling dimensions are supplied by the gallery")
    dimensions = {**catalogue.dimensions, **view_dimensions}
    names = tuple(dimensions)
    axis_labels = tuple(
        {"size": "Field size", "m_selection": "M-selection"}.get(name, name.replace("_", " ").capitalize())
        for name in names
    )
    axis_indices = tuple(range(len(names)))
    size_axis = names.index("size")
    order = [size_axis, *(i for i in axis_indices if i != size_axis)]
    options = tuple(tuple(range(len(values))) for values in dimensions.values())
    recipe_options = options[: len(catalogue.dimensions)]
    displayed_specs = {}
    # Static presentation models are shared; each checkbox keeps its own value.
    checkbox_layout = widgets.Layout(width="auto")
    checkbox_style = CheckboxStyle()
    filter_label_layout = widgets.Layout(width="140px")
    row_layout = widgets.Layout(flex_flow="row wrap")
    page_anchor = None
    update_number = 0
    activity_status = widgets.HTML(
        layout=widgets.Layout(
            width="100%", height="30px", min_height="30px", max_height="30px", margin="0", overflow="hidden"
        )
    )

    def set_activity(state, detail, elapsed=None):
        colors = {
            "busy": ("#fff3cd", "#a66a00", "⏳ Calculating and rendering…"),
            "ready": ("#e8f5e9", "#176b35", "✓ Ready"),
            "waiting": ("#eef2f6", "#475569", "Choose a selection"),
            "warning": ("#fff3cd", "#a66a00", "Page too large"),
            "error": ("#fee2e2", "#a61b1b", "Update failed"),
            "interrupted": ("#fff3cd", "#a66a00", "Update interrupted"),
        }
        background, accent, label = colors[state]
        heading = f"{label} · Update #{update_number}"
        if elapsed is not None:
            heading += f" · {elapsed:.2f} s"
        progress = (
            '<progress aria-label="Gallery update in progress" '
            'style="width:80px;height:8px;flex:0 0 80px;margin:0"></progress>'
            if state == "busy"
            else ""
        )
        activity_status.value = (
            '<div role="status" aria-live="polite" '
            f'title="{escape(heading + ": " + detail, quote=True)}" '
            f'style="background:{background};color:{accent};border-left:4px solid {accent};'
            'display:flex;align-items:center;gap:10px;box-sizing:border-box;height:30px;'
            'padding:4px 8px;border-radius:4px;font-size:13px;white-space:nowrap;overflow:hidden">'
            f'<span style="font-weight:700;flex-shrink:0">{escape(heading)}</span>'
            f'{progress}<span style="overflow:hidden;text-overflow:ellipsis">{escape(detail)}</span></div>'
        )

    selections = {
        "size": field_sizes,
        "combiner": selected_combiners,
        "m_selection": selected_m_selections
        if selected_m_selections is not None
        else (("minimum_period",) if minimum_post_modulus else ("catalogue",)),
        "sampling": selected_samplings,
        "additional_sampling": selected_additional_samplings,
    }
    initial_choices = tuple(
        tuple(i for i, value in enumerate(values) if selections.get(name) is None or value in selections[name])
        for name, values in dimensions.items()
    )
    boxes = {}

    density_control = widgets.BoundedIntText(
        min=1,
        max=max(256, page_size),
        value=page_size,
        style={"description_width": "initial"},
        layout=widgets.Layout(width="170px"),
    )
    transpose_control = widgets.Checkbox(
        value=transposed,
        description="Transpose grid",
        tooltip="Fill down columns when ungrouped, or turn each group into a column.",
        indent=False,
        style=checkbox_style,
        layout=widgets.Layout(width="135px"),
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
        options=[(axis_labels[i], i) for i in order],
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
    def prepared_field(recipe, size, sampling, m_selection):
        field = sample_field(recipe, size, sampling, m_selection=m_selection, centered=True)
        return field, indexed_order_palette(field.values, field.spec["color"], anchor=field.spec.get("color_anchor"))

    @lru_cache(maxsize=84)
    def recipe_panel(recipe, size, sampling, additional_sampling, m_selection):
        try:
            field, palette = prepared_field(recipe, size, sampling, m_selection)
        except exploration.PeriodTargetError as error:
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

    def render_page(entries, transpose, wrap):
        rows = []
        specs = {}
        for cases in entries:
            headings = []
            panels = []
            for case in cases:
                recipe_position = case[: len(recipe_options)]
                number = _product_rank(recipe_options, recipe_position) + 1
                recipe = recipe_at(recipe_position)
                size_index, m_index, sampling_index, additional_index = case[len(recipe_options) :]
                m_selection = M_SELECTIONS[m_index]
                size = FIELD_SIZES[size_index]
                sampling = SAMPLINGS[sampling_index]
                additional_sampling = ADDITIONAL_SAMPLINGS[additional_index]
                heading = f"#{number} {recipe.combiner.upper()} · {size}x{size}"
                description = recipe_description(recipe, size) + " · M: " + _option_label("m_selection", m_selection)
                panel, spec = recipe_panel(recipe, size, sampling, additional_sampling, m_selection)
                if spec is not None:
                    specs[number, size, m_selection, sampling, additional_sampling] = spec
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

    def update_page(change=None):
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
        selected = tuple(
            tuple(i for i, box in enumerate(boxes[axis]) if box.value) if axis in boxes else initial_choices[axis]
            for axis in axis_indices
        )
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
        if not entry_count or estimated_pixels > 64 << 20:
            displayed_specs.clear()
            message = (
                "Select at least one value for each dimension."
                if not entry_count
                else "This page is too large. Reduce the page size, group fewer dimensions, or filter some values."
            )
            page_status.value += f" · {message}"
            page_preview.layout.display = "none"
            page_preview.value = b""
            return ("waiting" if not entry_count else "warning"), message

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
        png, specs = render(tuple(page_entries), entries_as_columns, wrap_control.value)
        unchanged = page_preview.layout.display != "none" and page_preview.value == png
        if len(specs) < page_panels:
            page_status.value += f" · {page_panels - len(specs)} unavailable"
        displayed_specs.clear()
        displayed_specs.update(deepcopy(specs))
        page_preview.value = png
        page_preview.layout.display = ""
        return "ready", "Preview unchanged." if unchanged else "Preview updated."

    def redraw(change=None):
        nonlocal update_number
        update_number += 1
        started = perf_counter()
        set_activity("busy", "The previous preview may remain visible below until this update finishes.")
        try:
            state, detail = update_page(change)
        except KeyboardInterrupt:
            set_activity("interrupted", "The requested update did not finish.", perf_counter() - started)
            raise
        except Exception as error:
            set_activity("error", f"{type(error).__name__}: {error}", perf_counter() - started)
            raise
        else:
            set_activity(state, detail, perf_counter() - started)

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
        boxes[axis] = tuple(
            widgets.Checkbox(
                value=i in initial_choices[axis],
                description=_option_label(names[axis], value),
                indent=False,
                layout=checkbox_layout,
                style=checkbox_style,
            )
            for i, value in enumerate(dimensions[names[axis]])
        )
        for box in boxes[axis]:
            box.observe(redraw, names="value")
        return widgets.HBox(
            [widgets.Label(axis_labels[axis], layout=filter_label_layout), *boxes[axis]],
            layout=row_layout,
        )

    quick_names = ("size", "combiner", "m_selection", "sampling", "additional_sampling")
    quick_filters: list[widgets.HBox | widgets.Accordion] = [
        choice_row(names.index(name)) for name in quick_names if name in names
    ]
    other_axes = [i for i, name in enumerate(names) if name not in quick_names]
    hidden_filters = widgets.VBox()
    more_filters = None
    if other_axes:
        more_filters = widgets.Accordion(
            children=[hidden_filters], titles=["More parameter filters · loading…"], selected_index=None
        )
        quick_filters.append(more_filters)

    def load_hidden():
        if more_filters is None:
            return None
        body = widgets.VBox([choice_row(i) for i in other_axes], _view_count=0)
        more_filters.children = (body,)
        more_filters.set_title(0, "More parameter filters")
        return body

    back_button.on_click(lambda button: setattr(page_control, "value", page_control.value - 1))
    next_button.on_click(lambda button: setattr(page_control, "value", page_control.value + 1))
    slower_button.on_click(lambda button: move_dimension(-1))
    faster_button.on_click(lambda button: move_dimension(1))
    dimension_control.observe(update_order_controls, names="value")
    grouped_control.observe(change_grouping, names="value")
    for control in (
        density_control,
        page_control,
        transpose_control,
        wrap_control,
    ):
        control.observe(redraw, names="value")
    controls = widgets.VBox(
        [
            *quick_filters,
            widgets.HBox(
                [dimension_control, slower_button, faster_button, grouped_control, order_label],
                layout=row_layout,
            ),
            widgets.HBox(
                [back_button, next_button, page_control, density_control, transpose_control, wrap_control, page_status],
                layout=row_layout,
            ),
            activity_status,
        ]
    )
    update_order_controls()
    redraw()
    gallery_view = _GalleryView(controls, page_preview, load_hidden)
    return gallery_view, displayed_specs
