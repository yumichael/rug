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

The workspace uses the locked Ruff from the research environment for both Python and notebook format on save. The notebook is formatted before Jupytext Sync updates the tracked Python source. The editor, pre-commit hook, and CI use the same [Ruff configuration](../../ruff.toml).

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

The import enables inline plots and automatic reloading of edited Python modules. It provides the workbench tools, plotting and widget imports, and the example presets. Use `presets = load_presets()` to read a fresh copy after editing the preset file.

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

## Native numerical specifications

```python
from ruglab import evaluate, grid

spec = {
    "n": 64,
    "shape": [64, 64],
    "coordinates": "historical",
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

`shape` is `[rows, columns]`; native arrays use rows for y and columns for x. `origin` is `[x, y]` in displayed sample indices. Historical coordinates use `a=y-x-1, b=y+x`; straight coordinates use `a=x, b=y`. Both receive the same pre-operations, then reduction modulo K. The basic combiner has full integer output; post-operations are finally reduced modulo M. No implicit coordinate reduction modulo n is inserted.

Sampling names are `full`, `checkerboard_same`, `checkerboard_opposite`, `even_even`, `even_odd`, `odd_even`, and `odd_odd`. Their exact original-grid maps are in [sampling.py](ruglab/sampling.py). `shape` describes the selected displayed grid, so sampling does not silently halve that shape. Native defaults are full sampling, historical coordinates, and K=M=n; choose moduli explicitly for research claims. The JSON sweep frontend defaults to straight coordinates to match the original operand-grid workflow.

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

[research.py](ruglab/research.py) exposes `family_pre_modulus`, the proved full-grid family rules for all seven combiners; `minimum_post_modulus`, a complete-torus difference-depth check for a single post-power; and `uniform_xor`, the proved uniform shift/order-class sampler for the balanced XOR family. The latter uses a local seed and the established odd/even weights, and covers full-grid and checkerboard sampling. General polynomial evaluation is available, but this workbench does not claim a general efficient uniform polynomial order sampler. The research adapters load only repository-local proof helpers and do not run their experiments on import.

## Validation

Run `uv run pytest -q -m 'not integration'` for the unit tests. The full suite also exercises Git hooks, staged Ruff checks, and fresh-kernel notebook execution, as CI does.

```sh
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

Tests cover literal integer references, large powers and moduli, sampling phases, polynomial features, DSL rendering and colors, lazy sweeps, exact signatures, saved specifications, research rules, Jupytext round trips, and fresh-kernel notebook execution. The project lockfile pins the resolved dependency set.
