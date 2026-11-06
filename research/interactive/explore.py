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

# %% [markdown]
# # Rug pattern workbench
#
# Edit the small specifications below and rerun a cell. Numerical evaluation, plotting, diagnostics, and persistence live in `ruglab`. Rows are y, columns x for native specifications; imported DSL keeps its original array orientation.
#

# %%
from IPython import get_ipython

get_ipython().run_line_magic("load_ext", "autoreload")
get_ipython().run_line_magic("autoreload", "2")
get_ipython().run_line_magic("matplotlib", "inline")
import json
from pathlib import Path

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import clear_output, display

from ruglab import (
    Sweep,
    duplicates,
    evaluate,
    grid,
    paired,
    periods,
    sampling_gallery,
    stages,
    summary,
    symmetries,
)
from ruglab.research import family_pre_modulus, minimum_post_modulus, uniform_xor

presets = json.loads(Path("presets/examples.json").read_text())

# %% [markdown]
# ## JSON parameter grid
#
# The original sweep shape is retained. K, M, coordinates, and sampling now control evaluation explicitly. Only the requested page is generated.
#

# %%
sweep_spec = {
    "n": 64,
    "shape": [64, 64],
    "K": 64,
    "M": 128,
    "coordinates": "historical",
    "sampling": "full",
    "pre": [["pow", [2, 4, 6]]],
    "combine": ["and", "or", "xor", "add", "mult", "clmul", "absdiff"],
    "post": [["pow", [1, 2]]],
}
sweep = Sweep(sweep_spec)
page = list(sweep.page(start=0, size=8))
print(f"{sweep.count} combinations; showing {len(page)}")
grid(page, cols=4)
plt.show()
# %% [markdown]
# ## Optional page controls
#
# Updating these controls evaluates one page. Color changes reuse basic stages.
#

# %%
page_control = widgets.IntSlider(min=0, max=(sweep.count - 1) // 8, description="Page", continuous_update=False)
mode_control = widgets.Dropdown(options=["values", "anchored", "order"], description="View")
output = widgets.Output()


def redraw(change=None):
    with output:
        clear_output(wait=True)
        fig = grid(sweep.page(page_control.value * 8, 8), cols=4, mode=mode_control.value)
        display(fig)
        plt.close(fig)


page_control.observe(redraw, names="value")
mode_control.observe(redraw, names="value")
display(widgets.HBox([page_control, mode_control]), output)
# Change a control or call redraw() to populate this panel.

# %% [markdown]
# ## DSL, including color channels
#
# Five sections: n ; pre ; combiner ; post ; color.
#

# %%
dsl_examples = {
    "existing XOR": presets["dsl"],
    "odd power": ["64;;^;diag1:**3:*7:%64:map01;gray"],
    "HSV": [
        f"64;;^;diag1:**2:*{a}:+{b}:%128:{mapping};{channel}"
        for a, b, mapping, channel in [
            (3, 0, "map01", "H"),
            (5, 32, "map01cyclic", "S"),
            (7, 64, "map01cyclic", "V"),
        ]
    ],
}
grid(dsl_examples, cols=3)
plt.show()
# %% [markdown]
# ## Native research specifications
#
# Compare sampling with the same arithmetic first. Then choose each style's appropriate modulus. Polynomial coefficients are listed constant-term first.
#

# %%
selected = presets["squared_and"]
result = evaluate(selected)
display(summary(result))
sampling_gallery(selected, cols=4)
plt.show()
# %%
stages(result)
grid({"numerical": result}, mode="anchored", cols=1, width=5)
grid({"ordering": result}, mode="order", cols=1, width=5)
print(periods(result, certified_torus=True))  # This example evaluates a complete K x K torus.
print(symmetries(result))

# %%
q, target = 6, 32
K = family_pre_modulus(q, target, "or")
research_spec = {"n": K, "K": K, "M": K, "pre": [["pow", q]], "combine": "or"}
M = minimum_post_modulus(research_spec, target, power=2)
print({"K": K, "minimum M": M})
grid(
    {
        "selected modulus": {**research_spec, "M": M, "post": [["pow", 2]]},
        "pre-polynomial": presets["polynomial"],
        "joint expression": presets["multiple_features"],
    },
    cols=3,
)
plt.show()
# %% [markdown]
# ## Paired variations, uniform XOR classes, and duplicate inspection
#

# %%
base = presets["xor"]
variations = list(paired(base, M=[128, 256, 512], post=[[["pow", 2]], [["pow", 4]], [["pow", 8]]]))
grid(variations, cols=3)
random_examples = [(str(seed), uniform_xor(64, seed, parity="even")) for seed in range(6)]
grid(random_examples, cols=3)
print("Order groups:", duplicates([(name, evaluate(s)) for name, s in random_examples]))

# %% [markdown]
# ## Favorites and exports
#
# Run these examples deliberately after choosing a candidate. Everything saved is relative to this workbench; presets can be shared as JSON without outputs.
#

# %%
# from ruglab import gallery
# gallery.save('output/favorites.json', 'my candidate', selected, notes='What I liked')
# saved = gallery.load('output/favorites.json', query='candidate')
# from ruglab import export
# export(result, 'output/candidate.png', scale=4)
