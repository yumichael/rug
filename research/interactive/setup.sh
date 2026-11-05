#!/bin/sh
set -eu
cd "$(dirname "$0")"
unset VIRTUAL_ENV
# uv creates .venv locally unless UV_PROJECT_ENVIRONMENT selects another path.
uv sync --locked
uv run --no-sync python -m ipykernel install --user --name rug-research --display-name 'Rug research (Python 3.15)'
