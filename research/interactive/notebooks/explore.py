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
# Each plot comes from one combination of the selected parameter values. The dimension order runs from slowest to fastest. Choose a dimension and click **Slower** or **Faster** to move it. Use **More parameter filters** to choose recipe values such as pre-powers or twists.
#
# **Group fastest** keeps the selected values of the fastest dimensions together when paging. It defaults to 0, so each plot counts individually. Plots fill across rows, or down columns with **Transpose grid** on.
#
# The checkerboard views run vertically along the operand grid's $x=y$ diagonal. Left-right reflection exchanges the two operands. The same-parity tile starts with its cell-centered mirror column at the left edge. The opposite-parity tile starts with the preceding row of its vertical period.
#
# **Additional sampling** selects cells from the finished field, using its top-left cell as the parity origin and keeping the original cell colors. **Full** keeps every cell. Both checkerboard options use the inscribed diamond and show it as a square with half the original side length. The moduli, repeat, zero share, and value count describe the original field. Additional sampling is the fastest dimension by default.
#
# The pager remembers the first plot of the last page you navigated to. Filters, dimension order, and layout changes keep that plot as the anchor. If a filter hides it, the pager shows the next matching entry or the last available page.
#
# Use the wrap control to set how many entries fit per row or column. Set it to 0 for a single block.
#
# By default, each panel uses a pre-modulus chosen for its sampling and a post-modulus computed from its own combined values. The post-modulus is the smallest power of two that keeps distinct values separate and preserves every nonzero value. Titles report both moduli, the zero share, and the repeat. A diamond has half the area of the displayed square. A smaller tile can occur when one operand branch repeats sooner, or when the combiner erases variation. Constant fields are shown too.
#
# **Minimum M (displayed period)** uses the smallest power of two giving the field size as both least axis periods, with the pre-modulus and operations fixed. It can merge value groups or create zeros. Recipes that cannot attain those periods show an unavailable panel. Additional sampling keeps the resulting field's modulus and colors. The option is off by default in each recipe gallery; pass `minimum_post_modulus=True` to start with it enabled.
#
# `PREVIEW_PIXELS` sets the thumbnail width in pixels. The field size control sets the actual grid used for the calculations and export, with power-of-two side lengths from 2 to 4096.
#
# The catalogue varies the combiner, even pre-power, post-power, and twist coefficient $c$. The pre-polynomial uses $t=x^q$ and evaluates $t+2c t(t-1)$. See the [November research report](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#3-a-shared-pre-modulus-for-useful-even-pre-polynomial-families).
#

# %%
PLOTS_PER_PAGE = 32
PREVIEW_PIXELS = 384
DEFAULT_FIELD_SIZES = (128,)
DEFAULT_COMBINERS = ("or",)
DEFAULT_SAMPLINGS = ("full", "checkerboard_same", "checkerboard_opposite", "odd_odd")
DEFAULT_TRANSPOSE = True

gallery_view, displayed_specs = recipe_gallery(
    exploration_catalogue(),
    field_sizes=DEFAULT_FIELD_SIZES,
    selected_combiners=DEFAULT_COMBINERS,
    selected_samplings=DEFAULT_SAMPLINGS,
    transposed=DEFAULT_TRANSPOSE,
    page_size=PLOTS_PER_PAGE,
    preview_pixels=PREVIEW_PIXELS,
    wrap_after=len(DEFAULT_SAMPLINGS),
)
display(gallery_view)

# %% [markdown]
# For a closer look, retrieve the base specification using its recipe number, field size, sampling, and additional sampling, such as `displayed_specs[1, 8, "even_odd", "checkerboard_same"]`. Recipe numbers stay fixed when you reorder dimensions. Use `export(evaluate(spec), "../output/field.png", mode="order", additional_sampling="checkerboard_same")` to export that view at one pixel per cell.
#

# %% [markdown]
# ## Explore XOR post-polynomials
#
# The operands pass straight to the combiner with a pre-modulus. Each round visits odd and even power-plus-multiplier families, sums of powers with a shared exponent valuation, even-only polynomials, and unrestricted polynomials. The headings identify the family and show either the exponent and multiplier or the precision parameter and polynomial degree. The three broader families use several precisions, and the even sums include a representative of the stabilized high-valuation space.
#
# The draw is uniform within each sampled family and precision on the odd XOR inputs. Each round gives those strata equal space in the gallery. Single powers and stabilized even sums cycle through their finite classes before repeating. Other families draw with replacement. Overlaps can occur across strata and under other samplings. The opposite-parity checkerboard is the reference for the full-period test at sizes of four cells and up. Other samplings and combiners show what the same polynomial does to their inputs.
#
# See the [polynomial period and sampling theory](../../theory/2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) and the [order-class analysis](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#6-no-pre-operation-xor-when-order-and-shift-classes-coincide). The gallery colors cells by rank. The research proves uniform order draws for the same-valuation families at a fixed precision. The unrestricted and even-only draws cover numerical shift classes and may repeat an ordering. Use `post_specs[number, size, sampling, additional_sampling]["post"]` to inspect the exact polynomial in ascending coefficient order.
#
# **Minimum M** is applied after drawing the polynomial, using the selected sampling's periods. The stratum label still describes the original draw precision; the panel reports the evaluated $M$. Different draws can become identical after minimizing, so the resulting minimum-modulus patterns need not be sampled uniformly.
#
# %%
POST_DRAWS_PER_STRATUM = 24
POST_SEED = 0

post_gallery_view, post_specs = recipe_gallery(
    post_polynomial_catalogue(draws=POST_DRAWS_PER_STRATUM, seed=POST_SEED),
    selected_combiners=("xor",),
    field_sizes=(1024,),
    selected_samplings=("checkerboard_opposite",),
    transposed=False,
    page_size=15,
    initial_page=24,
    preview_pixels=512,
    wrap_after=5,
)
display(post_gallery_view)

# %% [markdown]
# ## An even post-power at two precisions
#
# Both panels use no-pre-operation XOR, the gallery's vertical opposite checkerboard, and the same post-square $H(z)=z^2$. For side length $N=128$, the pre-modulus is $K=2N=256$. The minimum post-modulus retaining least axis periods $(128,128)$ is $M=2K=512$. At that precision, $H(K-z)=H(z)$ on all odd inputs, giving the pseudo-square motifs. One extra bit, $M=1024$, breaks that equality while retaining the same periods. The panels use the gallery's anchored rank coloring.
#

# %%
XOR_SQUARE_SIDE = 128
xor_square_base = {
    "n": XOR_SQUARE_SIDE,
    "K": 2 * XOR_SQUARE_SIDE,
    "pre": [],
    "combine": "xor",
    "sampling": "checkerboard_opposite",
    "checkerboard_axis": "vertical",
    "post": [["pow", 2]],
    "color": "cmr.fall",
}
xor_square_minimum = 2 * xor_square_base["K"]
xor_square_inputs = np.arange(1, xor_square_base["K"], 2, dtype=object)
xor_square_examples = {}
extra_bits = 1
for label, modulus in (
    ("Minimum M · pseudo-square", xor_square_minimum),
    (f"{extra_bits} extra bit · symmetry fails", 2**extra_bits * xor_square_minimum),
):
    result = evaluate({**xor_square_base, "M": modulus})
    axis_periods = periods(result, certified_torus=True)
    post_values = steps(xor_square_inputs, xor_square_base["post"], modulus=modulus)
    complement_symmetric = np.array_equal(post_values, post_values[::-1])
    assert axis_periods == (XOR_SQUARE_SIDE, XOR_SQUARE_SIDE)
    assert complement_symmetric == (modulus == xor_square_minimum)
    print(f"M={modulus}: least axis periods={axis_periods}; complement symmetry={complement_symmetric}")
    print(f"  H(1)={post_values[0]}, H(K-1)={post_values[-1]}")
    xor_square_examples[label] = result

assert periods(evaluate({**xor_square_base, "M": xor_square_minimum // 2}), certified_torus=True) == (
    XOR_SQUARE_SIDE // 2,
    XOR_SQUARE_SIDE // 2,
)
grid(xor_square_examples, cols=2, width=12, mode="order")
plt.show()

# %% [markdown]
# ## Compare OR pre-powers
#
# With the default dimension order, each page runs through the even pre-powers 2 through 64 in the same positions. Read across the first row, then continue on the next row. The defaults show one field size and one sampling in four rows of eight. Keep **Plots per page** at 32 to keep each sweep together.
#
# By default, pages change the post-polynomial first, then the twist. The headings give their catalogue indices. Twist 0 and post 0 give the pre-power alone. The scan crosses 16 twists, through degree nine in the powered input, with 10 post-polynomials, including mixed degrees. With **Minimum M** off, the post-modulus preserves the combined value groups, so the post-polynomials can change their color order. Inspect the exact operations in `pre_power_specs[number, size, sampling, additional_sampling]`.
#
# %%
pre_power_gallery_view, pre_power_specs = recipe_gallery(
    pre_power_study_catalogue(),
    field_sizes=(128,),
    selected_samplings=("checkerboard_opposite",),
    transposed=False,
    page_size=32,
    wrap_after=8,
)
display(pre_power_gallery_view)
