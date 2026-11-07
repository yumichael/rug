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
# Each panel is one complete square repeat tile in displayed cells. The gallery covers all seven operand-grid selections and all seven combiners. Order coloring spreads the distinct anchored values across each palette so that small numerical gaps are visible.
#
# The whole grid keeps all operand pairs. Both checkerboards rotate the selected operand pairs into a displayed square grid. The opposite-parity checkerboard keeps pairs with one even operand and one odd operand. See the [November research report](../../theory/2026-11-03-combiners-and-order-classes/2026-11-04-combiners-and-order-classes.md#4-the-seven-sampling-rules-symmetry-and-erased-variation).

# %%
# The pre-operation is the sum of the listed (degree, coefficient) terms.
# Input depth is the smallest 2-adic valuation of a nonzero combined value.
cartesian_recipes = (
    # Combiner, sampling, terms, K/size, post-power, input depth, palette
    ("and", "full", ((6, -1), (12, 2)), 2, 17, 0, "cmr.ember"),
    ("or", "even_even", ((4, -1), (8, 2)), 64, 21, 4, "cmr.freeze"),
    ("add", "odd_odd", ((8, -1), (16, 2)), 16, 31, 1, "cmr.savanna"),
    ("absdiff", "full", ((10, -1), (20, 2)), 2, 37, 0, "cmr.amber"),
    ("mult", "even_odd", ((4, 1), (12, 13)), 64, 29, 5, "cmr.ocean"),
    ("clmul", "odd_even", ((2, 1), (14, 3)), 8, 43, 4, "cmr.guppy"),
)


def research_field_specs(size):
    if size not in (256, 512, 1024):
        raise ValueError("Choose a field size of 256, 512, or 1024 cells")
    specs = {}
    for combiner, sampling, terms, stride, power, input_depth, palette in cartesian_recipes:
        coefficients = [0] * (terms[-1][0] // 2 + 1)
        for degree, coefficient in terms:
            coefficients[degree // 2] = coefficient
        K = stride * size
        # Restore the bits consumed by powering a multiple of 2**input_depth.
        post_depth = input_depth * power + (power & -power).bit_length() - 1
        degrees = ", ".join(str(degree) for degree, _ in terms)
        selection = "whole grid" if sampling == "full" else sampling.replace("_", "/")
        label = f"{combiner.upper()} · {selection}\nPre {degrees} · post {power}"
        specs[label] = {
            "n": size,
            "sampling": sampling,
            "pre": [["pow", 2], ["poly", coefficients]],
            "combine": combiner,
            "post": [["pow", power]],
            "K": K,
            "M": K << post_depth,
            "color": palette,
        }

    specs["XOR · same checkerboard\nPost 19"] = {
        "n": size,
        "sampling": "checkerboard_same",
        "combine": "xor",
        "K": 2 * size,
        "M": size << 19,
        "post": [["pow", 19]],
        "color": "cmr.fall",
    }
    specs["XOR · opposite checkerboard\nPost 26, 58, 122"] = {
        "n": size,
        "sampling": "checkerboard_opposite",
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
        # For identity-pre XOR on either checkerboard, an axis shift by K/2
        # toggles the top bit of both operands, leaving their XOR unchanged.
        sampling = spec["sampling"]
        if not sampling.startswith("checkerboard"):
            residues = steps(np.arange(spec["K"], dtype=object), spec["pre"], modulus=spec["K"])
            branches = (
                (residues,)
                if sampling == "full"
                else [residues[(parity == "odd") :: 2] for parity in sampling.split("_")]
            )
            if any(not np.array_equal(branch, np.roll(branch, size)) for branch in branches):
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
