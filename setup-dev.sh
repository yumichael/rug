#!/bin/sh
set -eu
cd "$(dirname "$0")"
sh scripts/setup-rumdl.sh
git config --local core.hooksPath scripts/hooks
echo 'Installed app development dependencies and enabled the pre-commit checks.'
