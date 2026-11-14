# Writing mathematics in Markdown

Use this policy for maintained Markdown in this repository, including research reports. It targets GitHub’s rendered file view and VS Code’s built-in Markdown preview with `markdown.math.enabled` enabled. Notebook renderers and third-party preview extensions need their own checks. Follow the [Markdown workflow](README.md#markdown) for formatting and validation.

## Writing rules

Write inline mathematics with `$...$`, including in ordinary prose, list items, and table cells. Keep each expression on one source line, with no whitespace immediately inside the delimiters. Use LaTeX for mathematical notation in prose, such as $M=2^m$ and $\nu_2(q)$; prefer $\tau$ when naming the circle constant.

Put whitespace before an opening math delimiter when it follows a word or hyphen. Write `a high $v$ tail`, rather than `a high-$v$ tail`. Leave whitespace between a closing delimiter and a following letter or digit: write `values of $M$`, rather than `$M$s`. A hyphen after a closing delimiter, as in `$M$-selection`, worked in the tested renderers. Ordinary punctuation such as commas and parentheses can touch the delimiters. Escape literal dollar signs as `\$`.

Use plain text or Unicode notation in headings. This is a repository convention for predictable anchors and navigation; the tested GitHub headings did render inline math.

Keep math outside italic spans. Bold spans containing math worked in the compatibility probe. In tables, use `\lvert`, `\rvert`, or `\mid` instead of a raw pipe, including a Markdown-escaped pipe, inside an equation. For example:

| Quantity         | Condition |
| ---------------- | --------- |
| $\lvert x\rvert$ | $a\mid b$ |

Place display equations at the top level, separated from prose by blank lines. Put unindented `$$` delimiters on their own lines, without blank lines inside the formula. Keep the formula on one source line where practical; a standalone `=` can become a Markdown heading. Move displays outside lists and blockquotes.

$$
H(z)=\widetilde G\!\left((z-N)^2\right).
$$

Use `\mathrm{ord}` instead of `\operatorname{ord}`. Rewrite equations requiring `\\` row breaks as separate equations or conditions. For coordinate columns, `(x,y)^{\mathsf T}` avoids a matrix row break. Check that rewritten cases still cover exactly the original conditions.

Use dollar delimiters, rather than `\(...\)`, `\[...\]`, or GitHub’s backtick-in-dollar alternative. Reserve code spans and code fences for source examples and actual code; write ordinary equations as visible math rather than fenced `math` blocks.

## What the compatibility evidence establishes

The public [rendering probe and results](https://github.com/yumichael/markdown-math-rendering-probe/blob/d4987cdb795ca743fd60dc50eac41bd40aa019ed/RESULTS.md) record observations from November 12, 2026. GitHub’s public rendered files were inspected visually. The VS Code comparison used the parser and math plugin bundled with VS Code 1.142.0 and KaTeX 0.16.21 to generate HTML; it did not verify the editor’s preview UI. The [hyphen probe](https://github.com/yumichael/markdown-math-rendering-probe/blob/d4987cdb795ca743fd60dc50eac41bd40aa019ed/HYPHENS.md) includes both adjacency directions in headings and prose.

Inline math rendered in prose, headings, table headers and cells, unordered and ordered lists, nested lists, blockquotes, and bold text. These contexts are not blanket limitations. The tested italic span and list-indented display remained literal on GitHub. GitHub rejected `\operatorname`, altered tested double-backslash row breaks, and failed to render math immediately preceded by a word and hyphen. Math followed by a hyphen and word rendered. Raw pipes split table cells in both parsers.

These are bounded observations, not an exhaustive LaTeX support specification. Consult the official [GitHub math documentation](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions), [VS Code math documentation](https://code.visualstudio.com/docs/languages/markdown#_math-formula-rendering), and [VS Code math plugin](https://github.com/microsoft/vscode-markdown-it-katex) when extending the supported subset. A successful local KaTeX render does not establish GitHub compatibility.

## Checks and performance

The [math checker](scripts/math-policy.mjs) runs inside the existing Markdown Node process. Pre-commit checks only staged Markdown sources from the index for known delimiter, adjacency, context, and command problems. Files without math markers skip parser loading. There is no browser, network request, per-equation subprocess, or equation rendering in pre-commit. Existing repository-wide indexed link checks continue independently.

On November 13, 2026, eight measured fresh-process runs per case gave median Markdown-stage times of 411 ms before and 419 ms after for a small math change, and 400 ms before and 420 ms after for the largest existing math report. With no staged Markdown, medians were 360 ms and 353 ms, within timing variation. The staged cases used read-only Git shims supplying indexed sources and the real runner and rumdl; no repository index was changed. These local measurements cover the Markdown stage, with roughly 8–21 ms added for the tested math edits, rather than a bound on every machine or document size.

`npm run check:markdown` also renders extracted equations with the pinned local KaTeX reference, catching malformed or unsupported formulas. CI runs this command and `npm run test:markdown`. `npm run format:markdown` formats Markdown and then runs the same math checks; it leaves mathematical rewrites to the author. Optional path arguments apply to both checks. Archived, vendored, and Git-ignored files follow the Markdown exclusions. Mathematical source in Python notebook cells is outside this Markdown gate.

The local reference uses `markdown-it` 14.3.3, `@vscode/markdown-it-katex` 1.1.2, and KaTeX 0.19.1, pinned in [package.json](package.json). The KaTeX override keeps the plugin on the patched shared dependency. These versions provide a reproducible local check; they do not claim to reproduce the installed VS Code version or GitHub’s renderer exactly.

Diagnostics use `MATH001` for delimiters, `MATH002` for adjacency, `MATH003` for the operator-name command, `MATH004` for row breaks, `MATH005` for backticks in formulas, `MATH006` for italics, `MATH007` for display layout, `MATH008` for local rendering errors, `MATH009` for the heading convention, and `MATH010` for table pipes. Markdown parsing can expose a broken table formula as a delimiter error. The checker catches known problems; it cannot certify that every accepted expression renders identically on both platforms.

## Tracking the boundary

Keep the local [compatibility cases](scripts/tests/fixtures/math-cases.json) as the versioned executable record. They include accepted syntax, observed platform failures, repository conventions, and local syntax failures. Run `npm run test:markdown` after changing the checker, fixtures, or renderer dependencies.

For a new command or Markdown context, add a minimal case and its expected checker result. Check it in the actual VS Code preview and GitHub’s public rendered file view, inspecting the equation’s meaning as well as whether a math element exists. Use synthetic examples in the public probe repository; keep project research and personal notes here. Record the date, VS Code version and settings, exact source revision, both results, and whether the result came from UI inspection or generated HTML.

Treat the public probe as an evidence laboratory and this file as the repository policy. Link to a fixed probe commit when updating evidence. Recheck the affected cases when changing the renderer dependencies or when a platform’s behavior changes, then update the fixtures and policy together. Publish copies of the local cases when retesting rather than maintaining a second independent catalogue. Browser checks stay manual and outside pre-commit and CI.
