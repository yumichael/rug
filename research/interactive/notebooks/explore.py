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
# Each row shows one recipe at one field size across the selected samplings. **Transpose grid** puts those entries in columns and samplings in rows. Check any combination of field sizes, combiners, and sampling methods. The pager groups the selected sizes together for each recipe. Edit `ROWS_PER_PAGE` in the next cell to set the default, or adjust **Rows per page** or **Columns per page** in the pager. Use the arrows or enter a page number. The two checkerboard views use axes rotated 45° from the operand grid.
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
ROWS_PER_PAGE = 8
PREVIEW_PIXELS = 384
DEFAULT_FIELD_SIZES = (128,)
DEFAULT_COMBINERS = ("or",)
DEFAULT_SAMPLINGS = ("full", "checkerboard_opposite", "odd_odd")
DEFAULT_TRANSPOSE = True

gallery_view, displayed_specs = recipe_gallery(
    exploration_recipes(),
    field_sizes=DEFAULT_FIELD_SIZES,
    selected_combiners=DEFAULT_COMBINERS,
    selected_samplings=DEFAULT_SAMPLINGS,
    transposed=DEFAULT_TRANSPOSE,
    page_size=ROWS_PER_PAGE,
    preview_pixels=PREVIEW_PIXELS,
)
display(gallery_view)

# %% [markdown]
# For a closer look, retrieve a specification from `displayed_specs` using its recipe number, field size, and sampling, such as `displayed_specs[1, 8, "even_odd"]`. Use `export(evaluate(spec), "../output/field.png", mode="order")` to see it at one pixel per cell.
#

# %% [markdown]
# ## Explore XOR post-polynomials
#
# The operands pass straight to the combiner with a pre-modulus. Each round visits odd and even power-plus-multiplier families, sums of powers with a shared exponent valuation, even-only polynomials, and unrestricted polynomials. The headings identify the family and show either the exponent and multiplier or the precision parameter and polynomial degree. The three broader families use several precisions, and the even sums include a representative of the stabilized high-valuation space.
#
# The draw is uniform within each sampled family and precision on the odd XOR inputs. Each round gives those strata equal space in the gallery. Single powers and stabilized even sums cycle through their finite classes before repeating. Other families draw with replacement. Overlaps can occur across strata and under other samplings. The opposite-parity checkerboard is the reference for the full-period test at sizes of four cells and up. Other samplings and combiners show what the same polynomial does to their inputs.
#
# See the [polynomial period and sampling theory](../../theory/2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) and the [order-class analysis](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#6-no-pre-operation-xor-when-order-and-shift-classes-coincide). The gallery colors cells by rank. The research proves uniform order draws for the same-valuation families at a fixed precision. The unrestricted and even-only draws cover numerical shift classes and may repeat an ordering. Use `post_specs[number, size, sampling]["post"]` to inspect the exact polynomial in ascending coefficient order.
#
# %%
POST_DRAWS_PER_STRATUM = 24
POST_SEED = 0

post_gallery_view, post_specs = recipe_gallery(
    post_polynomial_recipes(draws=POST_DRAWS_PER_STRATUM, seed=POST_SEED),
    selected_combiners=("xor",),
    field_sizes=(256,),
    page_size=2,
    preview_pixels=512,
)
display(post_gallery_view)
