# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: rug-research (3.15.2)
#     language: python
#     name: python3
# ---

# %%
from ruglab.studio import *

# %% [markdown]
# ## Explore repeating fields
#
# Each row shows one recipe at one field size across all seven samplings. Check any combination of field sizes and combiners. The pager groups the selected sizes together for each recipe. Edit `ROWS_PER_PAGE` in the next cell to set the default, or adjust **Rows per page** in the pager. Use the arrows or enter a page number. The two checkerboard views use axes rotated 45° from the operand grid.
#
# The pager remembers the first row of the last page you navigated to. Filters and row-count changes keep that row as the anchor. If a filter hides it, the pager shows the next matching row or the last available page.
#
# Each panel uses a pre-modulus chosen for its sampling and a post-modulus computed from its own combined values. The post-modulus is the smallest power of two that keeps distinct values separate and preserves every nonzero value. Titles report both moduli, the zero share, and the repeat. A diamond has half the area of the displayed square. A smaller tile can occur when one operand branch repeats sooner, or when the combiner erases variation. Constant fields are shown too.
#
# `PREVIEW_PIXELS` sets the thumbnail width in pixels. The field size control sets the actual grid used for the calculations and export, with power-of-two side lengths from 2 to 4096.
#
# The catalogue varies the combiner, even pre-power, post-power, and twist coefficient $c$. The pre-polynomial uses $t=x^q$ and evaluates $t+2c t(t-1)$. See the [November research report](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#3-a-shared-pre-modulus-for-useful-even-pre-polynomial-families).
#

# %%
ROWS_PER_PAGE = 2
PREVIEW_PIXELS = 384
DEFAULT_FIELD_SIZES = (8,)
DEFAULT_COMBINERS = None  # All combiners, or a tuple of names such as ("xor", "clmul").

research_recipes = list(enumerate(exploration_recipes(), 1))
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


size_controls = choice_boxes(((size, str(size)) for size in FIELD_SIZES), DEFAULT_FIELD_SIZES, "72px")
combiners = sorted({recipe.combiner for _, recipe in research_recipes})
combiner_controls = choice_boxes(((name, name.upper()) for name in combiners), DEFAULT_COMBINERS, "88px")
filter_controls = (*size_controls.values(), *combiner_controls.values())
density_control = widgets.BoundedIntText(
    min=1,
    max=max(16, ROWS_PER_PAGE),
    value=ROWS_PER_PAGE,
    description="Rows per page",
    style={"description_width": "initial"},
    layout=widgets.Layout(width="170px"),
)
page_control = widgets.BoundedIntText(min=1, max=len(research_recipes) * len(FIELD_SIZES), value=1, description="Page")
back_button = widgets.Button(description="Back", layout=widgets.Layout(width="auto"))
next_button = widgets.Button(description="Next", layout=widgets.Layout(width="auto"))
page_status = widgets.HTML()
page_preview = widgets.Image(format="png", layout=widgets.Layout(width="100%"))


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
    return PreviewPanel(indexed_preview(field.values, spec["color"], pixels), caption), spec


def render_page(entries, pixels):
    rows = []
    specs = {}
    for number, recipe, size in entries:
        heading = (
            f"#{number} {recipe.combiner.upper()} · {size}\N{MULTIPLICATION SIGN}{size} · Pre {recipe.pre_power} · "
            f"twist {recipe.twist} · post {recipe.post_power}"
        )
        panels = []
        for sampling in SAMPLINGS:
            panel, specs[number, size, sampling] = recipe_panel(recipe, size, sampling, pixels)
            panels.append(panel)
        rows.append((heading, panels))
    return preview_grid(rows, pixels), specs


cached_page = lru_cache(maxsize=8)(render_page)


def redraw(change=None):
    global page_anchor

    rows_per_page = density_control.value
    sizes = [size for size, box in size_controls.items() if box.value]
    selected_combiners = {name for name, box in combiner_controls.items() if box.value}
    entries = [
        (number, recipe, size)
        for number, recipe in research_recipes
        if recipe.combiner in selected_combiners
        for size in sizes
    ]
    page_count = max(1, (len(entries) + rows_per_page - 1) // rows_per_page)
    if entries and (page_anchor is None or (change and change["owner"] is page_control)):
        number, _, size = entries[(page_control.value - 1) * rows_per_page]
        page_anchor = (number, size)
    index = next(
        (i for i, (number, _, size) in enumerate(entries) if page_anchor is not None and (number, size) >= page_anchor),
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
    if not entries:
        displayed_specs.clear()
        page_status.value = "Select at least one field size and one combiner."
        page_preview.layout.display = "none"
        page_preview.value = b""
        return
    first = (page - 1) * rows_per_page
    page_status.value = f"Page {page} of {page_count} · {len(entries):,} rows"
    page_entries = tuple(entries[first : first + rows_per_page])
    # Cache complete small pages for instant revisits. Larger pages reuse panels.
    render = cached_page if len(page_entries) <= 3 else render_page
    png, specs = render(page_entries, PREVIEW_PIXELS)
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
for control in (*filter_controls, density_control, page_control):
    control.observe(redraw, names="value")
controls = widgets.VBox(
    [
        choice_row("Field sizes", size_controls),
        choice_row("Combiners", combiner_controls),
        widgets.HBox(
            [back_button, next_button, page_control, density_control, page_status],
            layout=widgets.Layout(flex_flow="row wrap"),
        ),
    ]
)
redraw()
gallery_view = widgets.VBox([controls, page_preview], layout=widgets.Layout(width="100%"))
display(gallery_view)

# %% [markdown]
# For a closer look, retrieve a specification from `displayed_specs` using its recipe number, field size, and sampling, such as `displayed_specs[1, 8, "even_odd"]`. Use `export(evaluate(spec), "../output/field.png", mode="order")` to see it at one pixel per cell.
#
