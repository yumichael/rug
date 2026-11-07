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
# Run the cells to activate the pager. By default it shows six recipes across the available width. Use **Per page** to change the density. Pick a field size, filter by combiner, and use the arrows or enter a page number. Straight views compare the full grid and odd/odd sampling. The 45° views compare the two operand checkerboards. When both views qualify, they use the same pre-polynomial and post-power. The moduli can differ to match the displayed size and preserve value groups.
#
# The search prefers fewer zero cells, then a smaller largest value group, then more distinct values. A view needs at least eight values and at most half its cells may be zero. The post-modulus is the smallest power of two that keeps every distinct combined value separate and preserves every nonzero value. Titles report the raw zero share and the fundamental repeat. A diamond has half the area of the displayed square.
#
# The catalogue varies the combiner, even pre-power, post-power, and twist coefficient $c$. The pre-polynomial uses $t=x^q$ and evaluates $t+2c t(t-1)$. See the [November research report](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#3-a-shared-pre-modulus-for-useful-even-pre-polynomial-families).
#

# %%
research_recipes = list(enumerate(exploration_recipes(), 1))
displayed_specs = {}

size_control = widgets.Dropdown(options=(256, 512, 1024), description="Field size")
combiner_control = widgets.Dropdown(
    options=["All", *sorted({recipe.combiner.upper() for _, recipe in research_recipes})],
    description="Combiner",
)
view_control = widgets.ToggleButtons(options=("Both", "Straight", "45°"), description="View")
density_control = widgets.Dropdown(options=tuple(range(1, 17)), value=7, description="Per page")
page_control = widgets.BoundedIntText(min=1, max=len(research_recipes), value=1, description="Page")
back_button = widgets.Button(description="Back", layout=widgets.Layout(width="auto"))
next_button = widgets.Button(description="Next", layout=widgets.Layout(width="auto"))
page_status = widgets.HTML()
page_preview = widgets.Image(format="png", layout=widgets.Layout(width="100%"))


def redraw(change=None):
    size = size_control.value
    recipes_per_page = density_control.value
    if not isinstance(size, int) or not isinstance(recipes_per_page, int):
        return
    if change and change["owner"] is combiner_control and page_control.value != 1:
        page_control.value = 1
        return
    entries = [
        (number, recipe)
        for number, recipe in research_recipes
        if combiner_control.value in ("All", recipe.combiner.upper())
    ]
    page_count = (len(entries) + recipes_per_page - 1) // recipes_per_page
    if change and change["owner"] is density_control:
        first_recipe = (page_control.value - 1) * change["old"]
        page = first_recipe // recipes_per_page + 1
        if page != page_control.value:
            page_control.max = max(page_control.max, page_count)
            page_control.value = page
            return
    page_control.max = page_count
    back_button.disabled = page_control.value == 1
    next_button.disabled = page_control.value == page_control.max
    first = (page_control.value - 1) * recipes_per_page
    page_status.value = f"Page {page_control.value} of {page_control.max} · {len(entries)} recipes"
    views = [
        (name, rotated)
        for name, rotated in (("Straight", False), ("45°", True))
        if view_control.value in ("Both", name)
    ]
    displayed_specs.clear()
    with plt.ioff(), BytesIO() as buffer:
        fig, axes = plt.subplots(
            len(views),
            recipes_per_page,
            figsize=(3.2 * recipes_per_page, 4.1 * len(views)),
            dpi=125,
            squeeze=False,
            layout="constrained",
        )
        try:
            for ax in axes.flat:
                ax.set_axis_off()
            for col, (number, recipe) in enumerate(entries[first : first + recipes_per_page]):
                for row, (name, rotated) in enumerate(views):
                    ax = axes[row, col]
                    field = select_field(recipe, size, rotated)
                    heading = f"#{number} {recipe.combiner.upper()} · {name}"
                    parameters = f"Pre {recipe.pre_power} · twist {recipe.twist} · post {recipe.post_power}"
                    if field is None:
                        ax.set_title(f"{heading}\n{parameters}", fontsize=9)
                        ax.text(0.5, 0.5, "No qualifying repeat", ha="center", va="center", transform=ax.transAxes)
                        continue
                    spec = field.result.spec
                    displayed_specs[number, name] = spec
                    sampling = spec["sampling"].replace("_", " ")
                    ax.imshow(colorize(field.result, mode="order"), interpolation="antialiased")
                    ax.set_title(
                        f"{heading}\n{parameters}\n{sampling} · {field.repeat_shape}"
                        f"\n{field.zero_fraction:.1%} zero · {field.distinct_values:,} values",
                        fontsize=9,
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
for control in (size_control, combiner_control, view_control, density_control, page_control):
    control.observe(redraw, names="value")
controls = widgets.VBox(
    [
        widgets.HBox([size_control, combiner_control, view_control], layout=widgets.Layout(flex_flow="row wrap")),
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
# For a closer look, retrieve a specification from `displayed_specs` using its recipe number and view, such as `displayed_specs[1, "Straight"]`. Use `export(evaluate(spec), "../output/field.png", mode="order")` to see it at one pixel per cell.
#
