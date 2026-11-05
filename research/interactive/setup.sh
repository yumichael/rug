#!/bin/sh
set -eu
cd "$(dirname "$0")"
rug_env="${RUG_PYTHON_ENV:-$HOME/.local/share/rug/interactive/venv}"
if [ -e .venv ] || [ -L .venv ]; then
    if [ ! -L .venv ] || [ "$(readlink .venv)" != "$rug_env" ]; then
        echo 'Existing .venv differs from the requested external environment; leaving it untouched.' >&2
        exit 1
    fi
else
    ln -s "$rug_env" .venv
fi
UV_PROJECT_ENVIRONMENT="$rug_env" uv sync --python 3.12 --locked
"$rug_env/bin/python" -m ipykernel install --user --name rug-research --display-name 'Rug research (Python 3.12)'
