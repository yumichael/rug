# Rug: A math based program to generate images of rugs

Get your rug here: <https://yumichael.github.io/rug/>

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
