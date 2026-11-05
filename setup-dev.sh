#!/bin/sh
set -eu
cd "$(dirname "$0")"
sh scripts/setup-rumdl.sh
git config --local core.hooksPath scripts/hooks
sh research/interactive/setup.sh
echo 'Installed development dependencies and enabled Markdown and Python pre-commit gates.'
