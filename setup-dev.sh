#!/bin/sh
set -eu
cd "$(dirname "$0")"
sh scripts/setup-rumdl.sh
git config --local core.hooksPath scripts/hooks
echo 'Installed rumdl and enabled the Markdown pre-commit gate.'
