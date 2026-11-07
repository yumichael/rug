# Rug: A math based program to generate images of rugs

Get your rug here: <https://yumichael.github.io/rug/>

Agent-specific guidance is in [AGENTS.md](AGENTS.md).

## Documentation

Project documentation lives in [docs/](docs/). The [original kickoff prompt](docs/prototype.md) was a one-time instruction to an agent to begin implementing the app. It is preserved as historical context, rather than maintained as a description of the current design.

The [theory research](research/theory/) contains mathematical reports and their verification scripts. The [interactive research workbench](research/interactive/README.md) provides Python pattern tools, a notebook for experiments, and a reference notebook with worked examples.

## Development

Install Node.js 22 or newer with npm, then run:

```sh
sh setup-dev.sh
```

Setup installs the pinned rumdl npm dependency, records the Node.js executable and installation in local Git configuration as `rug.nodeExecutable` and `rug.nodeModules`, and activates the versioned hook with `git config --local core.hooksPath scripts/hooks`. The hook uses the recorded Node.js executable when committing from an editor. Rerun `sh scripts/setup-rumdl.sh` after moving or replacing that runtime.

### External dependencies

For a cloud-synced checkout, install npm dependencies in a dedicated directory outside the repository:

```sh
RUG_NPM_PREFIX="$HOME/.local/share/rug/npm" sh setup-dev.sh
```

Setup copies the package manifests to that prefix, installs there, and creates an ignored `node_modules` symbolic link for editor integration. Set `RUG_NPM_PREFIX` to the same prefix whenever rerunning setup. An existing local `node_modules` directory or a link to another installation requires you to move it aside before switching; setup preserves it. Without this variable, a fresh checkout installs locally. CI installs locally with `npm ci`.

### Markdown

rumdl is the Markdown formatter and checker. The [ruleset](.rumdl.toml) uses default rules plus table alignment, nested-fence checks, and unique heading anchors, with single-line prose paragraphs and no line-length limit. Archived, vendored, and Git-ignored files are excluded. rumdl discovers Markdown using its native extensions; the staged checker mirrors that selection.

```sh
npm run check:markdown
npm run format:markdown
```

Both commands accept optional paths, such as `npm run check:markdown -- README.md`. Formatting applies permitted fixes; structural issues that require a human decision remain errors. Use `1.` ordered-list markers. Keep mathematical expressions as `$...$` inline math or `$$...$$` display math, and use plain text or Unicode notation in headings for consistent VS Code and GitHub rendering.

VS Code recommends the rumdl extension and uses `node_modules/.bin/rumdl` to format Markdown on save. Files under `.vscode/` use JSONC, allowing comments and trailing commas.

The pre-commit hook checks formatting and lint in added, copied, modified, and renamed Markdown from the Git index. It also checks relative links and heading anchors throughout indexed Markdown, so deleting or renaming a target can fail the gate even when no Markdown is staged. Unstaged edits are left untouched. After formatting, review and stage the intended changes before committing. CI runs `npm run check:markdown` on pull requests and pushes to `main`.

### Optional Python research tools

Install the research tools separately when working on Python patterns or notebooks:

```sh
sh research/interactive/setup.sh
```

This optional setup requires uv, installs Python 3.15.2 and the locked research dependencies, and registers the notebook kernel. General HTML/JS app development requires only the app setup above. Research setup uses a local `research/interactive/.venv` by default; external Python environments are opt-in through `UV_PROJECT_ENVIRONMENT`, as described in the [workbench setup](research/interactive/README.md#setup-and-launch).

Use the [optional VS Code research workspace](research/interactive/README.md#vs-code) for notebook editing and Python format on save.

Ruff configuration lives in [ruff.toml](ruff.toml). Its rules cover correctness, NumPy, pytest, imports, and modernization, with allowances for notebook cells. Dated mathematical proof artifacts retain their original formatting. From the repository root, run:

```sh
uv run --project research/interactive ruff check .
uv run --project research/interactive ruff format --check .
uv run --project research/interactive python research/interactive/scripts/lint_staged_python.py --imports
uv run --locked --project research/interactive basedpyright --project .vscode/basedpyright.json --warnings
```

Reusable workbench Python lives in `research/interactive/ruglab/`. The notebook and tests call into the package, and the dated theory scripts serve as standalone verification. Imports in `ruglab` must resolve to the package, the standard library, or a declared dependency approved by the boundary check. Use static imports so the hook and CI can check them.

The pre-commit gate runs Ruff and Basedpyright on indexed research Python. Ruff checks staged Python files, or all indexed research Python when its configuration changes. Basedpyright checks the full indexed research tree when Python, its type-check configuration, or the research dependency files change. Stage the manifest and lockfile together after updating dependencies. App and documentation commits run the whitespace and Markdown checks without invoking uv or installing Python.

CI runs Ruff, the import boundary check, and Basedpyright using the locked research environment. Basedpyright uses its standard ruleset with a wildcard import exception for notebook sources. CI also runs the workbench tests and fresh-kernel notebook execution on Linux. Notebook tests create a temporary kernel specification using their current interpreter.
