# Interactive rug research

Open `notebooks/explore.ipynb` with the **Rug research (Python 3.15)** kernel to start experimenting. Open `notebooks/reference.ipynb` for the worked examples and page controls. The versioned sources are [explore.py](notebooks/explore.py) and [reference.py](notebooks/reference.py), and their local `.ipynb` partners retain outputs and are ignored. Numerical and display logic lives in [ruglab](ruglab/).

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

Gallery fields are centered around the original coordinate origin by offsetting each displayed axis by half its side length. Full sampling uses `[-C/2, C/2)` on each original axis. Cartesian and checkerboard sampling keep their phases and orientation; samplings excluding `(0, 0)` place nearby selected coordinates at the center. Additional sampling operates on the centered field. Returned specifications include `origin`, so exported values reproduce the preview. For standalone calculations, pass `centered=True` to `sample_field(...)`; its default retains the corner origin. Centering preserves the field's modulus, output groups, and statistics. Checkerboard opposite advances one row to center its reflection axis and match doubled checkerboard opposite at the original coordinate `(1, 0)`. Centered fields anchor rank colors at the middle cell; the saved `color_anchor` value keeps preview and export colors consistent.

Both **Sampling** and **Additional sampling** include **Doubled checkerboard opposite** immediately before **Checkerboard opposite**. As a main sampling it uses the full grid’s pre-modulus rule, then restricts to opposite-parity values and duplicates them before choosing the post-modulus; **Minimum period** checks the doubled field’s periods. It keeps the full dimensions and opposite-parity cells, replacing each same-parity cell with its right-hand neighbour, wrapping at the edge. Parity starts at the finished field’s top-left cell. When used as additional sampling, colors and moduli come from the base field.

The XOR polynomial gallery draws at its original stratum precision before applying this option. Minimizing can map several draws to the same pattern, so uniformity of the original draws does not imply uniformity over the minimized patterns. The option does not change which polynomial was drawn.

The last explore gallery compares even pre-powers across OR, AND, XOR, addition, absolute difference, multiplication, and carryless multiplication. Choose them with **Combiner**; OR is selected initially. Each sweep retains the same 32 pre-powers, twists, and post-polynomials. The pre-modulus follows the sampling rule, and **Minimum period** tests the selected combiner’s actual field periods.

Recipe galleries load automatically in stages: the native preview is published first, visible controls are shown on the next kernel event-loop turn, and hidden recipe filters are constructed on a subsequent turn. No expansion is needed to trigger loading. The fixed-height status row shows **Loading controls…**, then **Loading parameter filters…**, until the widget frontend reports those views ready. Page and filter changes update the same native image.

Each recipe gallery has a compact status bar below its paging controls, immediately above the preview. Its height stays fixed during updates; long details are available on hover. Amber **Calculating and rendering…** with an animated progress bar means an update is running; the previous preview can remain visible during that time. Green **Ready** shows the update number and elapsed time, and reports **Preview unchanged** when the resulting image is identical. Empty selections, oversized pages, failures, and interruptions show their own status.

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
