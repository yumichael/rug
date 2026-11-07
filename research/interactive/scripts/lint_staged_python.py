"""Check indexed research Python and enforce the ruglab import boundary."""

import ast
import json
import os
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

INTERACTIVE = Path('research/interactive')
RUGLAB = INTERACTIVE / 'ruglab'
NOTEBOOKS = INTERACTIVE / 'notebooks'
GATE = INTERACTIVE / 'scripts/lint_staged_python.py'
TYPECHECK_CONFIG = Path('.vscode/basedpyright.json')
DEPENDENCY_FILES = (INTERACTIVE / 'pyproject.toml', INTERACTIVE / 'uv.lock')
PYTHON_SUFFIXES = {'.py', '.pyi'}
DEPENDENCY_IMPORTS = {'IPython', 'PIL', 'cmasher', 'ipywidgets', 'json5', 'matplotlib', 'numpy'}
DYNAMIC_LOADERS = {'importlib', 'runpy'}
DYNAMIC_BUILTINS = {'__import__', 'exec', 'eval'}


def git(*args):
    return subprocess.check_output(['git', *args])


def maintained(path):
    source = Path(path)
    return source.suffix in PYTHON_SUFFIXES and source.is_relative_to(INTERACTIVE)


def module_roots(paths, base):
    roots = set()
    for path in paths:
        if path.is_relative_to(base):
            relative = path.relative_to(base)
            roots.add(relative.parts[0] if len(relative.parts) > 1 else relative.stem)
    return roots


def imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield node.lineno, node.module or '', node.level
            if not node.level and node.module == 'builtins':
                for alias in node.names:
                    if alias.name in DYNAMIC_BUILTINS:
                        yield node.lineno, alias.name, 0
        elif isinstance(node, ast.Name) and node.id in DYNAMIC_BUILTINS:
            yield node.lineno, node.id, 0
        elif isinstance(node, ast.Attribute) and node.attr in DYNAMIC_BUILTINS:
            yield node.lineno, node.attr, 0


def check_imports(*, staged):
    options = ('--cached',) if staged else ('--cached', '--others', '--exclude-standard')
    names = git('ls-files', '-z', *options).decode().split('\0')
    paths = {path for name in names if (path := Path(name)).suffix in PYTHON_SUFFIXES and (staged or path.is_file())}
    repo_modules = module_roots(paths, Path('.'))
    local_modules = repo_modules | module_roots(paths, INTERACTIVE)
    external = (sys.stdlib_module_names | DEPENDENCY_IMPORTS) - DYNAMIC_LOADERS - local_modules
    allowed_absolute = external | ({'ruglab'} - repo_modules)
    passed = True
    for path in sorted(paths):
        if not path.is_relative_to(INTERACTIVE):
            continue
        if path == GATE or path.is_relative_to(NOTEBOOKS) or path.is_relative_to(INTERACTIVE / 'tests'):
            continue
        if not path.is_relative_to(RUGLAB):
            print(f'{path}: place workbench Python source inside ruglab', file=sys.stderr)
            passed = False
            continue
        source = git('show', f':{path.as_posix()}') if staged else path.read_bytes()
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as error:
            print(error, file=sys.stderr)
            passed = False
            continue
        package_depth = len(path.relative_to(RUGLAB).parts)
        for line, name, level in imports(tree):
            allowed = level <= package_depth if level else name.partition('.')[0] in allowed_absolute
            if not allowed:
                print(f'{path}:{line}: import outside ruglab boundary: {"." * level}{name}', file=sys.stderr)
                passed = False
    return passed


def check_ruff(root, paths):
    if not paths:
        return True
    config = root / 'ruff.toml'
    config.write_bytes(git('show', ':ruff.toml'))
    passed = True
    for path in paths:
        source = git('show', ':' + path)
        for label, command in (('formatting', ['format', '--diff']), ('lint', ['check', '--quiet'])):
            result = subprocess.run(
                [sys.executable, '-m', 'ruff', *command, '--config', str(config), '--stdin-filename', path, '-'],
                input=source,
                cwd=root,
                check=False,
            )
            if result.returncode:
                print(f'Python {label} failed (Ruff) for {path}', file=sys.stderr)
                passed = False
            elif label == 'lint':
                print(f'Python lint passed (Ruff) for {path}')
    return passed


def check_types(root, paths):
    # uv selects dependencies from the working files. Require them to match the index.
    for path in DEPENDENCY_FILES:
        if path.read_bytes() != git('show', f':{path.as_posix()}'):
            print(f'{path}: align staged and working dependency files before type checking', file=sys.stderr)
            return False

    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git('show', ':' + path))

    # Use installed dependencies without search-path files pointing into the live checkout.
    version = f'python{sys.version_info.major}.{sys.version_info.minor}'
    site_packages = root / '.typecheck-env' / 'lib' / version / 'site-packages'
    site_packages.mkdir(parents=True)
    for dependency in Path(sysconfig.get_path('purelib')).iterdir():
        if dependency.name in {'ruglab', 'ruglab.py', 'ruglab.pyi'} or dependency.suffix in {'.pth', '.egg-link'}:
            continue
        (site_packages / dependency.name).symlink_to(dependency)
    if (root / RUGLAB).is_dir():
        (site_packages / 'ruglab').symlink_to(root / RUGLAB)

    indexed_config = root / TYPECHECK_CONFIG
    indexed_config.parent.mkdir(parents=True)
    indexed_config.write_bytes(git('show', f':{TYPECHECK_CONFIG.as_posix()}'))
    config_path = indexed_config.with_name('basedpyright-index.json')
    config_path.write_text(
        json.dumps({'extends': indexed_config.name, 'venvPath': str(root), 'venv': '.typecheck-env'})
    )
    environment = {key: value for key, value in os.environ.items() if key not in {'PYTHONPATH', 'PYTHONHOME'}}
    print('Checking indexed Python types (Basedpyright)', flush=True)
    return (
        subprocess.run(
            [sys.executable, '-m', 'basedpyright', '--project', str(config_path), '--warnings'],
            cwd=root,
            env=environment,
            check=False,
        ).returncode
        == 0
    )


def main():
    if sys.argv[1:] == ['--imports']:
        return 0 if check_imports(staged=False) else 1

    changed = set(git('diff', '--cached', '--name-only', '-z', '--no-renames').decode().split('\0'))
    indexed = [path for path in git('ls-files', '-z').decode().split('\0') if maintained(path)]
    lint_paths = indexed if 'ruff.toml' in changed else [path for path in indexed if path in changed]
    typecheck = any(maintained(path) for path in changed) or any(
        path.as_posix() in changed for path in (TYPECHECK_CONFIG, *DEPENDENCY_FILES)
    )
    if not lint_paths and not typecheck:
        return 0
    failed = not check_imports(staged=True)
    with tempfile.TemporaryDirectory(prefix='rug-index-') as directory:
        root = Path(directory)
        failed = not check_ruff(root, lint_paths) or failed
        if typecheck and indexed and not failed:
            failed = not check_types(root, indexed)
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
