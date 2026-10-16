# AGENTS.md

This file is the single source of truth for repository-specific agent instructions. `CLAUDE.md` imports it; put instruction changes here. Keep contributor setup, commands, editor configuration, and hook and CI documentation in [README.md](README.md), and link to that information rather than duplicating it.

## Repository layout

The web application lives in `index.html`. See [Documentation](README.md#documentation) for project documents and their purpose. `research/` contains mathematical investigations and supporting artifacts, and `saved-settings/` contains saved generator settings. Development tooling lives in `scripts/` and `.github/workflows/`.

## Working in this repository

- Follow [development setup](README.md#development), including the [external dependency workflow](README.md#external-dependencies), before installing or changing tooling.
- Follow the [Markdown conventions and validation workflow](README.md#markdown). Resolve checker findings without weakening the ruleset to hide violations.
- Prefer `tau` instead of `pi` in mathematical and computing work.
- Verify changed behavior with focused checks and report any validation you could not complete.

## Writing instructions and specifications

Write concise, direct statements of intent. Include examples or derived rules when they resolve a likely ambiguity. Describe the current design directly and remove obsolete explanations when revising it.

Define a shared concept once when several rules apply to the same stable set of cases, then refer to that concept rather than repeating lists that can drift.

## Git

Perform Git mutations only when the user explicitly requests the specific operation. This includes setup scripts that write Git configuration; editing working-tree files does not authorize staging or committing. Read-only Git operations are allowed.

In commit messages, describe code and test changes and leave validation results to CI.
