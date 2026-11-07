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

presets = load_presets()

# %% [markdown]
# ## November research gallery
#
# Each panel is one complete square repeat tile in displayed cells. The gallery covers all seven combiners using even pre-polynomials, larger post-powers, and a balanced XOR post-polynomial. Order coloring spreads the distinct anchored values across each palette so that small numerical gaps are visible.
#
# The checkerboard examples use even polynomials chosen to give the two sampled operand branches the same period. The whole-grid XOR example uses the same-valuation post-polynomial rule. See the [November research report](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md), sections 4 and 6.3.

# %%
# The checkerboard pre-operation is x**q + coefficient * x**degree.
# input_depth is the smallest 2-adic valuation of a nonzero combined value.
checkerboard_recipes = (
    # Combiner, q, degree, coefficient, K/size, post-power, input depth, palette
    ("and", 2, 6, 3, 8, 17, 2, "cmr.ember"),
    ("or", 4, 12, 13, 64, 58, 1, "cmr.freeze"),
    ("add", 2, 10, 1, 8, 77, 1, "cmr.savanna"),
    ("absdiff", 6, 22, -9, 128, 38, 3, "cmr.amber"),
    ("mult", 4, 12, 13, 64, 29, 5, "cmr.ocean"),
    ("clmul", 2, 14, 3, 8, 43, 4, "cmr.guppy"),
    ("xor", 6, 22, -9, 128, 31, 3, "cmr.fall"),
)


def research_field_specs(size):
    if size not in (256, 512, 1024):
        raise ValueError("Choose a field size of 256, 512, or 1024 cells")
    specs = {}
    for combiner, q, degree, coefficient, stride, power, input_depth, palette in checkerboard_recipes:
        coefficients = [0] * (degree // 2 + 1)
        coefficients[q // 2] = 1
        coefficients[-1] = coefficient
        K = stride * size
        # Restore the bits consumed by powering a multiple of 2**input_depth.
        post_depth = input_depth * power + (power & -power).bit_length() - 1
        label = f"{combiner.upper()} · checkerboard\nPre {q}, {degree} · post {power}"
        specs[label] = {
            "n": size,
            "sampling": "checkerboard_same",
            "pre": [["pow", 2], ["poly", coefficients]],
            "combine": combiner,
            "post": [["pow", power]],
            "K": K,
            "M": K << post_depth,
            "color": palette,
        }

    specs["XOR · whole grid\nPost 26, 58, 122"] = {
        "n": size,
        "sampling": "full",
        "combine": "xor",
        "K": 2 * size,
        "M": 4 * size,
        "expression": "z**26 - 3*z**58 + 5*z**122",
        "color": "cmr.infinity",
    }
    return specs


def show_research_fields(size):
    fig, axes = plt.subplots(2, 4, figsize=(13, 7), dpi=160, layout="constrained")
    half = size // 2
    for ax, (label, spec) in zip(axes.flat, research_field_specs(size).items(), strict=True):
        # The checkerboard operands vary independently along the displayed axes.
        # Test each parity branch over a complete residue cycle to certify the tile.
        # The whole-grid XOR tile follows from the balanced post-polynomial rule.
        if spec["sampling"] == "checkerboard_same":
            residues = steps(np.arange(spec["K"], dtype=object), spec["pre"], modulus=spec["K"])
            if any(not np.array_equal(branch, np.roll(branch, size)) for branch in (residues[::2], residues[1::2])):
                raise ValueError(f"{label} does not repeat at {size} cells")
        result = evaluate(spec)
        rgb = np.rint(255 * colorize(result, mode="order")).astype(np.uint8)
        # Any smaller translation subgroup of this dyadic torus contains a
        # half-axis or half-diagonal translation. Check the displayed colors too.
        for shift in ((half, 0), (0, half), (half, half)):
            if np.array_equal(rgb, np.roll(rgb, shift, axis=(0, 1))):
                raise ValueError(f"{label} has a smaller repeat at {size} cells")
        ax.imshow(rgb, interpolation="nearest")
        ax.set_title(f"{label}\nK = 2^{spec['K'].bit_length() - 1} · M = 2^{spec['M'].bit_length() - 1}", fontsize=9)
        ax.set_axis_off()
        clear_cache()
    fig.suptitle(f"{size} by {size} cells")
    plt.show()


# %%
show_research_fields(256)

# %%
show_research_fields(512)

# %%
show_research_fields(1024)

# %% [markdown]
# For an individual field, pick a specification from `research_field_specs(1024)` and use `grid({name: spec}, cols=1, mode="order")` for a larger view or `export(evaluate(spec), "../output/field.png", mode="order")` for a PNG at one pixel per cell.
