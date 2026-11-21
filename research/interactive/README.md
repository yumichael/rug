# Interactive rug research

Open `notebooks/explore.ipynb` with the **Rug research (Python 3.15)** kernel to start experimenting. Open `notebooks/reference.ipynb` for the worked examples and page controls. The versioned sources are [explore.py](notebooks/explore.py) and [reference.py](notebooks/reference.py), and their local `.ipynb` partners retain outputs and are ignored. Numerical and display logic lives in [ruglab](ruglab/).

Write mathematical Markdown reports according to the repository’s [LaTeX policy](../../LATEX.md), including its compatibility fixtures and validation workflow.

## Setup and launch

This is an optional environment for Python research. The repository’s general app development setup does not install it.

Run these commands from this directory:

```sh
sh setup.sh
uv run jupytext --sync notebooks/explore.py
uv run jupytext --sync notebooks/reference.py
uv run jupyter lab notebooks/explore.ipynb
```

Setup installs the locked dependencies and editable `ruglab` package in a local `.venv`, then registers the notebook kernel. This lets kernels started in `notebooks/` import the working copy. After external Python edits, synchronize the corresponding pair before reopening the notebook. After notebook edits in JupyterLab, save and run `uv run jupytext --sync notebooks/explore.ipynb` or `uv run jupytext --sync notebooks/reference.ipynb` before reviewing the Python source.

An external environment is optional, using uv's standard project setting:

```sh
UV_PROJECT_ENVIRONMENT="$HOME/.venvs/rug-research" sh setup.sh
```

Keep that variable set for subsequent uv commands, or optionally create a `.venv` symlink to the external installation for discovery without the variable. Setup does not create or replace symlinks. Before switching an existing environment's location, stop its kernels and preserve the existing environment; remove only an obsolete symlink, or move a real environment aside before recreating it. Virtual environments should be recreated at their final paths.

The Python pin is in [.python-version](.python-version). Use a current uv release to obtain it.

### VS Code

1. Run `sh setup.sh` and synchronize the notebook pair you want to open using the commands above.
1. Open [rug-research.code-workspace](rug-research.code-workspace) using **File → Open Workspace from File** and install its recommended extensions. The workspace opens the repository root with research-specific settings.
1. If the status bar shows a different interpreter in a Python file, run **Python: Select Interpreter** and choose `research/interactive/.venv/bin/python`. In the notebook, select the **Rug research (Python 3.15)** kernel.
1. Save the notebook and review its synced `.py` source before staging it. After editing a notebook's `.py` source directly, synchronize the pair before reopening it.

The workspace uses the locked Ruff from the research environment for both Python and notebook format on save. The notebook is formatted before Jupytext Sync updates the tracked Python source. The editor, pre-commit hook, and CI use the same [Ruff configuration](../../ruff.toml). If the Basedpyright extension is installed, the workspace also uses the shared [type-check configuration](../../.vscode/basedpyright.json).

For an external environment without a symlink, copy the workspace file to `rug-research.local.code-workspace` in this directory. In that local copy, point `python.defaultInterpreterPath`, `jupytextSync.pythonExecutable`, and `ruff.path` at the external environment directory, its Python executable, and its Ruff executable, respectively. Open the local workspace and select the kernel registered by setup. Run commits from a shell with `UV_PROJECT_ENVIRONMENT` exported so the hook can find the same environment.

### Optional terminal activation with direnv

Direnv activates the existing research environment on entry and restores the previous shell environment on exit. It uses `.venv` by default and respects `UV_PROJECT_ENVIRONMENT` for external installations. [Shared direnv configuration](.envrc)

With direnv installed and its shell hook enabled, run this once from the research directory.

```sh
direnv allow .
```

Your terminal can then use `python`, `pytest`, and `ruff` directly. VS Code uses the interpreter and kernel selected in the research workspace.

### Notebook imports

Use this as the first cell of an exploratory notebook under `notebooks/`. Ruff applies the notebook rules to Python and Jupyter files throughout that directory.

```python
from ruglab.studio import *
```

The import enables inline plots and full-module automatic reloading of edited Python modules, so newly added helpers share the module's current globals. It provides the workbench tools, plotting and widget imports, and the example presets. Use `presets = load_presets()` to read a fresh copy after editing the preset file.

```python
grid({"XOR": presets["xor"]})
plt.show()
```

## Exploration loop

1. Edit the JSON sweep or DSL examples and rerun their cell.
1. Browse one page at a time. Thumbnail labels are stable sweep indices; `sweep.get(index)` retrieves one specification directly without generating earlier pages.
1. Inspect a candidate with `evaluate`, `stages`, and `sampling_gallery`. Toggle numerical, anchored, or order coloring in the page controls.
1. Save a complete specification and notes with `gallery.save`. Reload and search it with `gallery.load`.
1. Export an image with `export`. Output files and local favorites default to the ignored `output/` directory. To share selected specifications, copy them into a `.jsonc` file in `presets/`.

Preset files use JSONC, which allows `//` and `/* ... */` comments and trailing commas in arrays and objects. [Example presets](presets/examples.jsonc)

The examples are adaptations of the existing JSON parameter-grid viewer and the five-section DSL experiments, inspected November 4, 2026. Their dependencies and useful numerical operations have been extracted into this repository. The workbench does not import the original notebooks, their common imports module, or their output directories.

The recipe galleries have an **M-selection** dimension immediately before **Sampling**. **Catalogue** keeps the original modulus rule. **Distinct outputs** reduces that modulus to the smallest power of two preserving all distinct output groups actually present in the field. It preserves zero as a separate group only when zero is already an output; a lone output uses M=1. **Minimum period** chooses the smallest power-of-two post-modulus giving the displayed side length as both least axis periods, with the pre-modulus and operations fixed. It may merge groups, and unattainable periods show an unavailable panel. Additional sampling retains the chosen modulus and colors. Use `selected_m_selections=("catalogue", "distinct_outputs", "minimum_period")` in `recipe_gallery(...)` to compare all three, or `m_selection="distinct_outputs"` in `sample_field(...)` for a single field. The existing `minimum_post_modulus=True` argument selects Minimum period. Returned gallery specifications use `(recipe_number, size, m_selection, sampling, additional_sampling)` keys.

Gallery fields are centered around the original coordinate origin by offsetting each displayed axis by half its side length. Full sampling uses `[-C/2, C/2)` on each original axis. Cartesian and checkerboard sampling keep their phases and orientation; samplings excluding `(0, 0)` place nearby selected coordinates at the center. Additional sampling operates on the centered field. Returned specifications include `origin`, so exported values reproduce the preview. For standalone calculations, pass `centered=True` to `sample_field(...)`; its default retains the corner origin. Centering preserves the field's modulus, output groups, and statistics. Checkerboard opposite advances one row to center its reflection axis and match doubled checkerboard opposite at the original coordinate `(1, 0)`. Gallery colors apply the colormap directly to each final residue divided by M, with no rank remapping or anchoring. Use `export(evaluate(spec), path, mode="values")` to reproduce these colors.

Both **Sampling** and **Additional sampling** include **Doubled checkerboard opposite** immediately before **Checkerboard opposite**. As a main sampling it uses the full grid’s pre-modulus rule, then restricts to opposite-parity values and duplicates them before choosing the post-modulus; **Minimum period** checks the doubled field’s periods. It keeps the full dimensions and opposite-parity cells, replacing each same-parity cell with its right-hand neighbour, wrapping at the edge. Parity starts at the finished field’s top-left cell. When used as additional sampling, colors and moduli come from the base field.

The XOR polynomial gallery draws at its original stratum precision before applying this option. Minimizing can map several draws to the same pattern, so uniformity of the original draws does not imply uniformity over the minimized patterns. The option does not change which polynomial was drawn.

The **Compare pre-powers across combiners** gallery compares even pre-powers across OR, AND, XOR, addition, absolute difference, multiplication, and carryless multiplication. Choose them with **Combiner**; OR is selected initially. Each sweep retains the same 32 pre-powers, twists, and post-polynomials. The pre-modulus follows the sampling rule, and **Minimum period** tests the selected combiner’s actual field periods.

Recipe galleries load automatically in stages: the native preview is published first, visible controls are shown on the next kernel event-loop turn, and hidden recipe filters are constructed on a subsequent turn. No expansion is needed to trigger loading. The fixed-height status row shows **Loading controls…**, then **Loading parameter filters…**, until the widget frontend reports those views ready. Page and filter changes update the same native image.

Each recipe gallery has a compact status bar below its paging controls, immediately above the preview. Its height stays fixed during updates; long details are available on hover. Amber **Preparing preview…** means Python is calculating or encoding the preview. Green **Preview prepared** shows the update number and Python preparation time. The timer measures Python preparation rather than frontend delivery and display. **Preview unchanged** means the generated PNG is identical. The PNG is published through the native notebook output only; the internal image holder does not synchronize its bytes through the widget channel. Empty selections, oversized pages, failures, and interruptions show their own status.

## Seeded head and tail order galleries

The seeded head and tail sections of [explore.py](notebooks/explore.py) use the existing [conditional component-order sampler and interpolation](../theory/2026-11-12-2-checkerboard-head-tail/sampling.md). After the initial import cell, every explore code cell runs independently. The tail cell defines `TAIL_ORDER_SEED`, `TAIL_ORDER_SIDE`, and `TAIL_ORDER_DRAWS`; the head cell defines its own `HEAD_ORDER_SEED`, `HEAD_ORDER_SIDE`, and `HEAD_ORDER_DRAWS`. Tail draws are uniform over the whole spatial tail order space at that fixed domain. Head draws are uniform conditional on the chosen pre-power, twist, and combiner; combining these bases does not give a uniform head union. Draws are independent with replacement. A finite set of seeds does not uniformly enumerate the class space.

The head pre-power choices are built for `HEAD_ORDER_SIDE`; rerun the head cell after changing that variable to refresh them. Each twist tuple is the ascending coefficient list of the shared twist polynomial. Checkerboard-opposite and doubled checkerboard-opposite sampling at sides 8 through 4096 are supported. Both use the same sampled polynomial and interpolation modulus; only the coordinate map changes. Other main samplings and head powers that have entered the tail produce unavailable panels. Large exact counting tables can take substantial time on the first draw and are reused afterward. A local tail first-draw check took about 4 seconds at side 2048 and 147 seconds at side 4096; the largest head bases can cost more. These are Python timings, excluding notebook frontend display. Additional sampling retains the base field's colors and statistics.

The previews use the exact values and modulus assigned by the existing interpolation procedure. Each draw applies a seed-reproducible float color offset after normalization, wrapping the sum into [0, 1). The offset is saved in `color_offset`, is shared across sampling views of that draw, and is honored by value-mode exports. They do not substitute evenly spaced ranks or optimize the spacing. Caption gap ratios compare distinct-output circular gaps with ideal equal spacing; the heaviest of 16 bins measures pixel-weighted concentration on the color circle after the random rotation. Circular gap ratios do not change with the rotation. These plots show the color offset instead of zero percentage. Equal bin masses would be 6.25%. These are descriptive checks, not an aesthetic score.

Saved specifications contain an exact `lookup` post-operation on the attained raw values, avoiding eager expansion of potentially huge polynomial coefficients. Outputs are hexadecimal strings so large integer values remain serializable. `evaluate(spec)` and `export(evaluate(spec), path, mode="values")` work directly. `realize_order_polynomial(spec)` expands the same interpolant into integer coefficients when needed; its chosen modulus is minimum-period for that constructed polynomial, not globally smallest over all realizations of the order. Seeds, draw indices, pre-parameters, class counts, interpolation structures, and spacing summaries are recorded in `spec["order_sample"]`.

## XOR valuation comparison

The **Compare XOR post-polynomial valuations** notebook section uses `xor_valuation_catalogue` to show a page of same-valuation no-pre-operation XOR draws. Set `XOR_VALUATION_DRAWS`, `XOR_VALUATION_SEED`, and `XOR_VALUATION_SIDE` in that cell. Valuations are sorted, with zero representing odd exponents and positive valuations representing even exponents. Changing Field size automatically rebuilds valuations from zero through $v_{\mathrm{tail}}=\max(1,\log_2(2N)-4)$, including one representative of the shared tail. The boundary follows the [whole-tail classification](../theory/2026-10-13-post-power/2026-10-13-xor-post-power-theory.md#6-stronger-valuation-result-the-whole-high-v-tail-repeats), combined with the [polynomial stabilization theorem](../theory/2026-11-02-xor-polynomial-period/2026-11-02-xor-polynomial-period.md#8-high-valuations-and-practical-same-valuation-counts); direct class-set checks cover the smaller coordinate domains 8 and 16. This is later than single-generator stabilization at $\max(1,\log_2(2N)-5)$; a cyclic polynomial space can still differ from the next valuation family. Each page keeps the selected draws together. **Plots per group row** wraps plots within a group; zero leaves the group unwrapped. With Transpose grid enabled, the control becomes **Plots per group column**. The notebook argument `group_wrap_after` sets its initial value. Catalogue M-selection retains the sampler's research precision; switching to another selector changes the resulting distribution. The existing sampler cycles through stabilized classes, so draws repeat when the class is smaller than the requested sample count.

## Checkerboard sampler comparison

The **Compare checkerboard samplers** notebook section compares class targets and color-spacing laws across dynamically rebuilt power groups. It covers all admissible shared twists across OR, XOR, ADD, and ABSDIFF, enumerating and deduplicating head partitions and using the proved tail reductions. Change the seed, draws, concentration, strategies, and exact-work limits in that cell. Strategy and Power group filters control the comparison; no base selection is required. The [research report](../theory/2026-11-15-sampler-comparison/report.md) gives the definitions, uniformity proofs, all-precision additions, and feasibility limits. In particular, minimum-modulus orders differ from unrestricted-precision orders, and the extra finite-window isometric tail panels concern the canonical tail pre-power. Work limits produce unavailable panels without substituting a smaller twist set. Use Catalogue with checkerboard opposite or doubled checkerboard opposite to preserve these targets; Additional sampling can change their visible equivalences.

The **Sample odd-odd equality and order classes** section draws uniformly from the deduplicated class space of any checked subset of the seven combiners. It compares raw partitions, their circular orders, isometric residue partitions, and full-period polynomial mergers. The [odd-odd theory](../theory/2026-11-21-odd-odd-samplers/report.md) gives the class definitions, exact distributions, and notebook size limits.

## Competing head-family proposals

The **Compare candidate head-family groupings** section of [explore.py](notebooks/explore.py) provides a gallery comparing alternative classifications: OR versus other combiners crossed with exact bit depth, coarse bit depth, surviving even branch, half-period graph, carry behavior, and an OR-specific twist-mask refinement. Their [implementable definitions and initial visual assessment](../theory/2026-11-14-1-head-family-proposals/report.md) distinguish complete coverage of head bases from possible overlaps of the rendered pattern families. The definitions allow every finite integer twist polynomial; displayed examples use `FAMILY_TWISTS`. The bounded [inventory](../theory/2026-11-14-1-head-family-proposals/inventory.json) records coverage and identical-raw-partition overlaps across seven domains.

Set `FAMILY_SIDE`, `FAMILY_SEED`, `FAMILY_EXAMPLES`, and `FAMILY_PROPOSALS`, then run that cell after the initial import cell. Each row shows examples of one candidate family. Family checkboxes select candidates across proposals. Choose **Page by → Family groups** to page through whole proposals despite their differing numbers of families; **Groups per page** controls how many proposals appear together. The same base and conditional order draw keep the same polynomial values and color offset across proposals, supporting matched visual comparison. Examples cycle through configured bases rather than claiming a uniform union sampler. Changing Field size automatically rebuilds the catalogue and family choices, retaining selected family names when available. The proposals are visual hypotheses, not proved aesthetic taxonomies.

## Native numerical specifications

```python
from ruglab import evaluate, grid

spec = {
    "n": 64,
    "shape": [64, 64],
    "sampling": "full",
    "K": 64,
    "pre": [["pow", 2]],
    "combine": "and",
    "post": [["pow", 2]],
    "M": 2048,
}
result = evaluate(spec)
grid({"candidate": result})
```

`shape` is `[rows, columns]`; native arrays use rows for y and columns for x. `origin` is `[x, y]` in displayed sample indices. `sampling` maps those indices directly to operand pairs. Both operands receive the same pre-operations, then reduction modulo K. The basic combiner has full integer output; post-operations are finally reduced modulo M. No implicit coordinate reduction modulo n is inserted.

Sampling names are `full`, `checkerboard_same`, `checkerboard_opposite`, `even_even`, `even_odd`, `odd_even`, and `odd_odd`. Their exact original-grid maps are in [sampling.py](ruglab/sampling.py). `shape` describes the selected displayed grid, so sampling does not silently halve that shape. The default is the full operand grid with K=M=n. `checkerboard_opposite` keeps pairs with one even operand and one odd operand. The DSL’s `diag1` and `diag1m` give two explicit display maps for that same selection.

For checkerboard samplings, `checkerboard_axis` sets the displayed direction parallel to the operand grid's $x=y$ diagonal. The default is `"horizontal"`. Explore uses `"vertical"`, so a left-right reflection exchanges the operands. With the vertical orientation, the opposite-parity map starts one displayed row earlier.

Operations include `add`, `mult`, `pow`, `expo`, `mod`, `self`, `xor`, `xor0`, `binary`, `gray`, `bitrev`, `rotl`, `inv`, and `poly`. A polynomial's coefficient list is constant-term first. For example, `["poly", [0,0,-1,0,2]]` represents `2*x**4-x**2`. Bit operations use the stage modulus's bit width; inverse maps nonunits to zero as in the original experiment. Use power-of-two stage moduli for these word operations.

The seven research combiners are AND, OR, XOR, ADD, MULT, CLMUL, and ABSDIFF. GCD, MIN, MAX, SUBTRACT, and XOR0 are also available with lowercase names. CLMUL is the full standard binary-polynomial product. An explicitly truncated old-style variant is specified as `{"name":"clmul_low", "width":6}`; it masks both operands and the product. Full MULT and CLMUL do not silently truncate to K bits.

A native `combine` list instead creates several features, with a shared post-expression:

```python
spec = {
    "n": 64,
    "K": 64,
    "M": 256,
    "combine": ["xor", "absdiff"],
    "expression": "z0 + z1**2",
}
```

The expression registry supports arithmetic, bitwise operators, `abs`, and named combinations such as `clmul(z0,z1)`. The DSL and native expression evaluator reject unsupported syntax rather than executing arbitrary Python statements. Python modules remain available for extending the operation registry.

## JSON grids and DSL

`Sweep` accepts the original shape: `pre` and `post` entries contain option lists, and `combine` is a list of alternatives. `page(start,size)` evaluates no arrays itself. Pass its results to `grid`; only that page is rendered. `paired(base, M=[...], post=[...])` varies columns together rather than taking their Cartesian product.

The DSL retains its five sections, colon-separated pre/post steps, legacy sampling functions, named grayscale palettes, and RGB/HSV/HSL channel lists:

```python
from ruglab import dsl, grid

channels = ["64;;^;diag1:**2:%128:map01;cmr.infinity"]
grid({"existing example": channels})
image = dsl.render(channels)
```

Supported legacy sampling functions are `diag0`, `diag1`, `diag1m`, `diag1m_1`, `ddiag0`, `ddiag1`, and `skip`. They retain their original array orientation, phase, and size changes; they are not aliases for the native sampling maps. Display transforms include `map01`, `map01cyclic`, `binary(threshold)`, and `discrete(levels)`. Explicit `%modulus` precedes normalization. The supported function subset is implemented in [dsl.py](ruglab/dsl.py); arbitrary functions from the original notebook namespace are not imported.

K and M are explicit in the JSON frontend. The old viewer's inferred `n * lowbit(pre_power) * lowbit(post_power)` output range is replaced by the declared M, and the previously unused sampling field now controls evaluation. Integer powers no longer rely on accidental int64 overflow. These corrections can change old previews; reproduce a particular old range or word-width operation explicitly.

## Exact arithmetic and diagnostics

The engine uses arbitrary-precision Python integers in NumPy object arrays. Modular exponentiation and polynomial reduction are fused where mathematically equivalent, including the DSL's polynomial steps followed by an explicit modulus. This supports large exponents and moduli exceeding 64 bits. Floating-point conversion occurs only for display. `clear_cache()` releases the bounded cache of basic stages; begin with 64–128-cell previews and render large candidates individually.

`signature(result,"shift")` and `signature(result,"order")` use exact anchored residues. `duplicates` groups matching signatures on the same supplied window. Order coloring spaces the value groups evenly, making equal anchored order signatures visually comparable without asserting that numerical spacing is identical.

`summary` and `symmetries` describe the supplied window. `periods(result, certified_torus=True)` requires the caller to supply a known complete periodic torus; it does not infer a global repetition guarantee from a crop. Historical and sampled phase centers need not coincide with the window center.

[research.py](ruglab/research.py) exposes `family_pre_modulus`, the common family minima on the whole operand grid and the opposite-parity checkerboard; `minimum_post_modulus`, a complete-torus difference-depth check for a single post-power; and `uniform_xor`, the proved uniform shift/order-class sampler for the balanced XOR family. The latter uses a local seed and the established odd/even weights on the opposite-parity operand checkerboard. General polynomial evaluation is available, but this workbench does not claim a general efficient uniform polynomial order sampler. The research adapters load only repository-local proof helpers and do not run their experiments on import.

## Validation

Run `uv run pytest -q -m 'not integration'` for the unit tests. The full suite also exercises Git hooks, staged Python checks, and fresh-kernel notebook execution, as CI does.

```sh
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run --locked basedpyright --project ../../.vscode/basedpyright.json --warnings
```

Tests cover literal integer references, large powers and moduli, sampling phases, polynomial features, DSL rendering and colors, lazy sweeps, exact signatures, saved specifications, research rules, Jupytext round trips, and fresh-kernel notebook execution. The project lockfile pins the resolved dependency set.
