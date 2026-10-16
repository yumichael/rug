#!/bin/sh
# Install pinned npm tools locally or under a dedicated external prefix.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
command -v node >/dev/null 2>&1 || { echo 'Error: Node.js is required.' >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo 'Error: npm is required.' >&2; exit 1; }

if [ -n "${RUG_NPM_PREFIX:-}" ]; then
  case "$RUG_NPM_PREFIX" in
    /*) ;;
    *) echo 'Error: RUG_NPM_PREFIX must be an absolute path.' >&2; exit 1 ;;
  esac
  if [ "$RUG_NPM_PREFIX" = / ] || [ "$RUG_NPM_PREFIX" = "$root" ]; then
    echo 'Error: use a dedicated external directory for RUG_NPM_PREFIX.' >&2
    exit 1
  fi
  if [ -e node_modules ] && [ ! -L node_modules ]; then
    echo 'Error: node_modules is a directory. Move it aside before selecting an external install.' >&2
    exit 1
  fi
  mkdir -p "$RUG_NPM_PREFIX"
  modules="$(CDPATH= cd -- "$RUG_NPM_PREFIX" && pwd -P)/node_modules"
  if [ -L node_modules ] && [ "$(readlink node_modules)" != "$modules" ]; then
    echo 'Error: node_modules points to a different installation. Review that link before changing it.' >&2
    exit 1
  fi
  cp package.json package-lock.json "$RUG_NPM_PREFIX/"
  npm ci --prefix "$RUG_NPM_PREFIX"
  if [ ! -L node_modules ]; then
    ln -s "$modules" node_modules
  fi
else
  if [ -L node_modules ]; then
    echo 'Error: node_modules is external. Set RUG_NPM_PREFIX to its existing prefix and rerun setup.' >&2
    exit 1
  fi
  npm ci
  modules="$root/node_modules"
fi

git config --local rug.nodeExecutable "$(command -v node)"
git config --local rug.nodeModules "$modules"
echo 'Installed rumdl and recorded its Node.js runtime for Git hooks.'
