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
# Run the initial import cell once. Every code cell below defines its own settings and can then run independently.
#
# Each plot comes from one combination of the selected parameter values. The dimension order runs from slowest to fastest. Choose a dimension and click **Slower** or **Faster** to move it. Use **More parameter filters** to choose recipe values such as pre-powers or twists.
#
# **Group fastest** keeps the selected values of the fastest dimensions together when paging. It defaults to 0, so each plot counts individually. Plots fill across rows, or down columns with **Transpose grid** on.
#
# Gallery fields offset both displayed axes by half the side length, centering the original coordinates. Full sampling uses $[-C/2,C/2)^2$ for a full side length $C$. Cartesian sampling preserves its original even/odd phases around the origin; the checkerboard views keep their vertical diagonal orientation. The central cell samples $(0,0)$ where it is included, or a nearest selected coordinate otherwise. The returned specification records the offset in `origin`, so evaluation and export match the centered plot. Additional sampling selects from this centered field.
#
# The checkerboard views run vertically along the operand grid's $x=y$ diagonal. Left-right reflection exchanges the two operands. Centering translates the existing periodic tile without changing the sampling orientation. Checkerboard opposite advances one row to center its reflection axis and put the original coordinate $(1,0)$ at the middle cell, matching doubled checkerboard opposite. Gallery colors apply the colormap directly to the final residue divided by $M$, with no rank remapping or anchoring.
#
# **Sampling** includes **doubled checkerboard opposite** immediately before **checkerboard opposite**. It uses the full grid's pre-modulus rule and duplicates the opposite-parity values one cell left before choosing the post-modulus. **Minimum period** targets the doubled field's periods.
#
# **Additional sampling** resamples cells from the finished field, using its top-left cell as the parity origin and keeping the original cell colors. **Full** keeps every cell. **Checkerboard same** and **checkerboard opposite** use the inscribed diamond and show it as a square with half the original side length. **Doubled checkerboard opposite** keeps the full size: it keeps opposite-parity cells and copies their values one cell left onto same-parity cells, wrapping at the right edge. The moduli, repeat, zero share, and value count describe the original field. Additional sampling is the fastest dimension by default.
#
# The pager remembers the first plot of the last page you navigated to. Filters, dimension order, and layout changes keep that plot as the anchor. When a filter removes the anchor value, the pager substitutes a remaining value in that dimension while preserving the other parameter values. A temporarily empty selection retains the anchor, so either order of checking and unchecking works. The page containing that anchor is shown.
#
# The compact status bar below the paging controls and immediately above the preview keeps the same height during updates. Hover to read any clipped details. Amber **Preparing preview…** shows that Python is calculating or encoding the preview. Green **Preview prepared** shows the update number and **Python** preparation time. The timer measures Python preparation rather than frontend delivery and display. **Preview unchanged** confirms that Python produced the same picture. Empty selections, oversized pages, failures, and interruptions show their own status.
#
# Use the wrap control to set how many entries fit per row or column. Set it to 0 for a single block.
#
# By default, each panel uses a pre-modulus chosen for its sampling and a post-modulus computed from its own combined values. The post-modulus is the smallest power of two that keeps distinct values separate and preserves every nonzero value. Titles report both moduli, the zero share, and the repeat. A diamond has half the area of the displayed square. A smaller tile can occur when one operand branch repeats sooner, or when the combiner erases variation. Constant fields are shown too.
#
# **M-selection** is a parameter dimension immediately before **Sampling**. **Catalogue** keeps the original modulus rule. **Distinct outputs** chooses the smallest power-of-two modulus preserving the distinct output groups in the catalogue field; zero needs its own group only when it is already an output. A lone output uses $M=1$. **Minimum period** chooses the smallest power-of-two modulus giving the field size as both least axis periods, with the pre-modulus and operations fixed; it may merge groups, and unattainable periods show an unavailable panel. Select several policies to compare them. Additional sampling keeps the chosen modulus and colors. Set `selected_m_selections=("catalogue", "distinct_outputs", "minimum_period")` to start with all three selected.
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
    selected_m_selections=("minimum_period",),
)
display(gallery_view)

# %% [markdown]
# For a closer look, retrieve the base specification using its recipe number, field size, M-selection, sampling, and additional sampling, such as `displayed_specs[1, 8, "minimum_period", "even_odd", "checkerboard_same"]`. Recipe numbers stay fixed when you reorder dimensions. Use `export(evaluate(spec), "../output/field.png", mode="values", additional_sampling="checkerboard_same")` to export that view at one pixel per cell.
#

# %% [markdown]
# ## Explore XOR post-polynomials
#
# The operands pass straight to the combiner with a pre-modulus. Each round visits odd and even power-plus-multiplier families, sums of powers with a shared exponent valuation, even-only polynomials, and unrestricted polynomials. The headings identify the family and show either the exponent and multiplier or the precision parameter and polynomial degree. The three broader families use several precisions, and the even sums include a representative of the stabilized high-valuation space.
#
# The draw is uniform within each sampled family and precision on the odd XOR inputs. Each round gives those strata equal space in the gallery. Single powers and stabilized even sums cycle through their finite classes before repeating. Other families draw with replacement. Overlaps can occur across strata and under other samplings. The opposite-parity checkerboard is the reference for the full-period test at sizes of four cells and up. Other samplings and combiners show what the same polynomial does to their inputs.
#
# See the [polynomial period and sampling theory](../../theory/2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md) and the [order-class analysis](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#6-no-pre-operation-xor-when-order-and-shift-classes-coincide). The gallery colors each final residue $v$ directly at colormap position $v/M$. The research proves uniform order draws for the same-valuation families at a fixed precision. The unrestricted and even-only draws cover numerical shift classes and may repeat an ordering. Use `post_specs[number, size, m_selection, sampling, additional_sampling]["post"]` to inspect the exact polynomial in ascending coefficient order.
#
# **Minimum period** is applied after drawing the polynomial, using the selected sampling's periods. The stratum label still describes the original draw precision; the panel reports the evaluated $M$. Different draws can become identical after minimizing, so the resulting minimum-modulus patterns need not be sampled uniformly.
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
# Both panels use no-pre-operation XOR, the gallery's vertical opposite checkerboard, and the same post-square $H(z)=z^2$. For side length $N=128$, the pre-modulus is $K=2N=256$. The minimum post-modulus retaining least axis periods $(128,128)$ is $M=2K=512$. At that precision, $H(K-z)=H(z)$ on all odd inputs, giving the pseudo-square motifs. One extra bit, $M=1024$, breaks that equality while retaining the same periods. The panels use the gallery's direct $v/M$ coloring.
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
    "color": "cmr.emergency",
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
grid(xor_square_examples, cols=2, width=12, mode="values")
plt.show()

# %% [markdown]
# ## Compare pre-powers across combiners
#
# With the default dimension order, each page runs through the even pre-powers 2 through 64 in the same positions. Read across the first row, then continue on the next row. The defaults show one field size and one sampling in four rows of eight. Keep **Plots per page** at 32 to keep each sweep together.
#
# Use **Combiner** to compare OR, AND, XOR, addition, absolute difference, multiplication, and carryless multiplication. OR is selected initially. By default, pages change the post-polynomial first, then the twist, then the combiner. The headings give their catalogue indices. Twist 0 and post 0 give the pre-power alone. The scan crosses 16 twists, through degree nine in the powered input, with 10 post-polynomials, including mixed degrees. With **Catalogue** selected, the post-modulus preserves the combined value groups, so the post-polynomials can change their color order. Inspect the exact operations in `pre_power_specs[number, size, m_selection, sampling, additional_sampling]`.
#
# %%
pre_power_gallery_view, pre_power_specs = recipe_gallery(
    pre_power_study_catalogue(),
    selected_combiners=("or",),
    field_sizes=(128,),
    selected_samplings=("checkerboard_opposite",),
    transposed=False,
    page_size=32,
    wrap_after=8,
)
display(pre_power_gallery_view)


# %% [markdown]
# ## Sample the complete tail order space
#
# Set `TAIL_ORDER_SEED` to reproduce these draws. Each draw is uniform over the complete tail space of spatial order classes at the selected side length, shared by OR, XOR, ADD, ABSDIFF, all tail pre-powers, and all allowed twists. One representative pre-power is chosen from the domain size. Draws are independent with replacement; a finite set of seeds is not a uniform enumeration of all classes. This is an order-class sampler, not a uniform sampler of numerical shift classes.
#
# The displayed values are exactly the targets of the existing [interpolation procedure](../../theory/2026-11-12-2-checkerboard-head-tail/realize.py), including its chosen modulus and circular phase. Each draw has a reproducible random float offset $\delta$ and uses $(v/M+\delta)\bmod1$ for coloring. Paired sampling views of the same draw share the offset. There is no rank remapping or spacing optimization; the offset is saved in `color_offset` and is honored by `mode="values"` exports. Coefficients are left unexpanded for fast previews; the saved post-operation is an exact lookup table on the attained raw values. `evaluate(spec)` and `export(evaluate(spec), path, mode="values")` work directly. Use `realize_order_polynomial(spec)` when you want the actual integer coefficients of that same interpolant. Its modulus is minimum-period for that polynomial, not globally smallest among every interpolant realizing the order.
#
# Captions report the minimum and maximum circular gap between distinct outputs, divided by ideal equal spacing. A gap ratio of 1 means equal spacing. The heaviest of 16 equal-width color-circle bins measures pixel-weighted concentration; perfect balance would be 6.25%. Gap ratios are invariant under color rotation. Bin occupancy describes the displayed values after rotation, not ranks. Captions show the color offset instead of a zero percentage; the numerical polynomial outputs are unchanged. Additional sampling keeps the base colors; its caption statistics still describe the whole base field.
#
# Both galleries support power-of-two sides 8 through 4096. Exact count construction can be expensive at the largest sides, especially for head bases; the tables are cached and reused across draws. Both checkerboard-opposite and doubled checkerboard-opposite are supported. They use the same sampled scalar polynomial and interpolation modulus, with their respective coordinate maps. Other samplings show an unavailable panel. The initial M-selection is Minimum period, the precision returned by the interpolation; no search for better spacing is added.
#

# %%
TAIL_ORDER_SEED = 0
TAIL_ORDER_SIDE = 64
TAIL_ORDER_DRAWS = 64
TAIL_ORDER_PAGE_SIZE = 16
TAIL_ORDER_PREVIEW_PIXELS = 512

tail_order_view, tail_order_specs = recipe_gallery(
    order_class_catalogue("tail", seed=TAIL_ORDER_SEED, draws=TAIL_ORDER_DRAWS, size=TAIL_ORDER_SIDE),
    field_sizes=(TAIL_ORDER_SIDE,),
    selected_samplings=("checkerboard_opposite",),
    selected_m_selections=("minimum_period",),
    page_size=TAIL_ORDER_PAGE_SIZE,
    preview_pixels=TAIL_ORDER_PREVIEW_PIXELS,
    wrap_after=8,
)
display(tail_order_view)

# %% [markdown]
# ## Sample conditional head orders
#
# Each draw is uniform conditional on the selected pre-power, twist, and combiner. This is not a uniform draw from their union: bases overlap and have different class counts. The tail gallery above has the stronger whole-family guarantee because every tail base shares the same spatial order space. The head catalogue initially includes every even pre-power below the tail at `HEAD_ORDER_SIDE`, the three explicit twist polynomials in `HEAD_ORDER_TWISTS`, and OR, XOR, ADD, ABSDIFF. These are arithmetic bases to compare, not a claim that the head has been divided into visually coherent styles.
#
# A twist tuple supplies the coefficients of $Q(t)$ in ascending degree in $f(t)=t+2t(t-1)Q(t)$. Edit `HEAD_ORDER_TWISTS` to try any finite integer polynomial. Draw changes fastest, so a page compares repeated draws at one fixed base. Changing Field size preserves the chosen pre-power; a base that moves into the tail shows an unavailable panel. Changing `HEAD_ORDER_SIDE` and rerunning this cell refreshes the head pre-power choices for that size. This cell has its own seed and settings and can run directly after the initial import cell.
#

# %%
HEAD_ORDER_SEED = 0
HEAD_ORDER_SIDE = 64
HEAD_ORDER_DRAWS = 64
HEAD_ORDER_PAGE_SIZE = 16
HEAD_ORDER_PREVIEW_PIXELS = 512
HEAD_ORDER_TWISTS = ((), (1,), (3, -2, 1))

head_order_view, head_order_specs = recipe_gallery(
    order_class_catalogue(
        "head", seed=HEAD_ORDER_SEED, draws=HEAD_ORDER_DRAWS, size=HEAD_ORDER_SIDE, twists=HEAD_ORDER_TWISTS
    ),
    field_sizes=(HEAD_ORDER_SIDE,),
    selected_combiners=("or",),
    selected_samplings=("checkerboard_opposite",),
    selected_m_selections=("minimum_period",),
    page_size=HEAD_ORDER_PAGE_SIZE,
    preview_pixels=HEAD_ORDER_PREVIEW_PIXELS,
    wrap_after=8,
)
display(head_order_view)


# %% [markdown]
# ## Compare candidate head-family groupings
#
# This gallery tests five competing groupings, rather than proposing one final classification. Each grouping classifies every allowed head base. The induced pattern families can overlap because different bases can produce the same order class. The [definitions, coverage argument, and bounded investigation](../../theory/2026-11-14-head-family-proposals/report.md) explain the scope and the initial visual assessment. **Even branch** is the most promising initial hypothesis from the side-64 examples; **Half-period graph** is a deliberately contrasting proposal that groups some visibly different textures together.
#
# Choose candidates in **Family**, or restrict `FAMILY_PROPOSALS` below to one or more of `"bit_depth"`, `"even_branch"`, `"half_period_graph"`, `"carry_behavior"`, and `"or_twist_mask"`. Each row contains examples from one candidate family. Bases are visited in seeded order before repeating with another conditional order draw. When the same base and draw occur under different proposals, the sampled polynomial and random color offset match exactly. Examples illustrate the configured twist set; they are not uniform samples of the union of a family. The family definitions themselves allow any finite integer twist polynomial.
#
# Set `FAMILY_SIDE` for the initial domain, or switch **Field size** in the gallery to rebuild domain-dependent families automatically. Empty candidates for the selected domains and twist examples are omitted. When several sizes are selected, a panel marks candidates absent at one size. At side 512, for example, pre-power six moves into One-layer multilevel while pre-power eight remains Interior-bit binary. That is why the alternatives include a domain-adaptive branch proposal alongside the shared bit-depth proposal. This cell is independently runnable after the initial import cell.
#

# %%
FAMILY_SIDE = 64
FAMILY_SEED = 0
FAMILY_EXAMPLES = 20
FAMILY_TWISTS = ((), (1,), (3, -2, 1))
FAMILY_PROPOSALS = ("bit_depth", "even_branch", "half_period_graph", "carry_behavior", "or_twist_mask")

head_family_view, head_family_specs = recipe_gallery(
    head_family_catalogue(
        size=FAMILY_SIDE,
        seed=FAMILY_SEED,
        draws=FAMILY_EXAMPLES,
        twists=FAMILY_TWISTS,
        proposals=FAMILY_PROPOSALS,
    ),
    field_sizes=(FAMILY_SIDE,),
    selected_samplings=("checkerboard_opposite",),
    selected_m_selections=("minimum_period",),
    page_size=3,
    grouped_dimensions=4,
    preview_pixels=512,
)
display(head_family_view)
