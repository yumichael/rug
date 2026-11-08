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
# Each row shows one recipe across all seven samplings. Edit `ROWS_PER_PAGE` in the next cell to set the default, or adjust **Rows per page** in the pager. Pick a field size, filter by combiner, and use the arrows or enter a page number. The two checkerboard views use axes rotated 45° from the operand grid.
#
# Each panel uses a pre-modulus chosen for its sampling and a post-modulus computed from its own combined values. The post-modulus is the smallest power of two that keeps distinct values separate and preserves every nonzero value. Titles report both moduli, the zero share, and the repeat. A diamond has half the area of the displayed square. A smaller tile can occur when one operand branch repeats sooner, or when the combiner erases variation. Constant fields are shown too.
#
# The catalogue varies the combiner, even pre-power, post-power, and twist coefficient $c$. The pre-polynomial uses $t=x^q$ and evaluates $t+2c t(t-1)$. See the [November research report](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#3-a-shared-pre-modulus-for-useful-even-pre-polynomial-families).
#

# %%
ROWS_PER_PAGE = 2

research_recipes = list(enumerate(exploration_recipes(), 1))
displayed_specs = {}

size_control = widgets.Dropdown(options=(256, 512, 1024), description="Field size")
combiner_control = widgets.Dropdown(
    options=["All", *sorted({recipe.combiner.upper() for _, recipe in research_recipes})],
    description="Combiner",
)
density_control = widgets.BoundedIntText(
    min=1,
    max=max(16, ROWS_PER_PAGE),
    value=ROWS_PER_PAGE,
    description="Rows per page",
    style={"description_width": "initial"},
    layout=widgets.Layout(width="170px"),
)
page_control = widgets.BoundedIntText(min=1, max=len(research_recipes), value=1, description="Page")
back_button = widgets.Button(description="Back", layout=widgets.Layout(width="auto"))
next_button = widgets.Button(description="Next", layout=widgets.Layout(width="auto"))
page_status = widgets.HTML()
page_preview = widgets.Image(format="png", layout=widgets.Layout(width="100%"))


def redraw(change=None):
    size = size_control.value
    rows_per_page = density_control.value
    if not isinstance(size, int):
        return
    if change and change["owner"] is combiner_control and page_control.value != 1:
        page_control.value = 1
        return
    entries = [
        (number, recipe)
        for number, recipe in research_recipes
        if combiner_control.value in ("All", recipe.combiner.upper())
    ]
    page_count = (len(entries) + rows_per_page - 1) // rows_per_page
    if change and change["owner"] is density_control:
        first_recipe = (page_control.value - 1) * change["old"]
        page = first_recipe // rows_per_page + 1
        if page != page_control.value:
            page_control.max = max(page_control.max, page_count)
            page_control.value = page
            return
    page_control.max = page_count
    back_button.disabled = page_control.value == 1
    next_button.disabled = page_control.value == page_control.max
    first = (page_control.value - 1) * rows_per_page
    page_status.value = f"Page {page_control.value} of {page_control.max} · {len(entries)} recipes"
    page_entries = entries[first : first + rows_per_page]
    displayed_specs.clear()
    with plt.ioff(), BytesIO() as buffer:
        fig = plt.figure(
            figsize=(3.2 * len(SAMPLINGS), 4.1 * len(page_entries)),
            dpi=125,
            layout="constrained",
        )
        try:
            rows = fig.subfigures(len(page_entries), 1, squeeze=False)
            for (number, recipe), row in zip(page_entries, rows.flat, strict=True):
                row.suptitle(
                    f"#{number} {recipe.combiner.upper()} · Pre {recipe.pre_power} · "
                    f"twist {recipe.twist} · post {recipe.post_power}",
                    fontsize=12,
                )
                for sampling, ax in zip(SAMPLINGS, row.subplots(1, len(SAMPLINGS)), strict=True):
                    field = sample_field(recipe, size, sampling)
                    spec = field.result.spec
                    displayed_specs[number, sampling] = spec
                    name = sampling.replace("_", " ")
                    k, m = (spec[key].bit_length() - 1 for key in ("K", "M"))
                    ax.set_axis_off()
                    ax.imshow(colorize(field.result, mode="order"), interpolation="antialiased")
                    ax.set_title(
                        f"{name} · {field.repeat_shape}\n"
                        f"{field.zero_fraction:.1%} zero · {field.distinct_values:,} values\n"
                        f"$K=2^{{{k}}}$ · $M=2^{{{m}}}$",
                        fontsize=10,
                    )
            fig.savefig(buffer, format="png", bbox_inches="tight")
            page_preview.value = buffer.getvalue()
        finally:
            plt.close(fig)


def previous_page(button):
    page_control.value -= 1


def next_page(button):
    page_control.value += 1


back_button.on_click(previous_page)
next_button.on_click(next_page)
for control in (size_control, combiner_control, density_control, page_control):
    control.observe(redraw, names="value")
controls = widgets.VBox(
    [
        widgets.HBox([size_control, combiner_control], layout=widgets.Layout(flex_flow="row wrap")),
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
# For a closer look, retrieve a specification from `displayed_specs` using its recipe number and sampling, such as `displayed_specs[1, "even_odd"]`. Use `export(evaluate(spec), "../output/field.png", mode="order")` to see it at one pixel per cell.
#
