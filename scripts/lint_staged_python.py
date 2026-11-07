"""Check indexed Python with Ruff and enforce the ruglab import boundary."""

import ast
import subprocess
import sys
import tempfile
from pathlib import Path

INTERACTIVE = Path('research/interactive')
RUGLAB = INTERACTIVE / 'ruglab'
PYTHON_SUFFIXES = {'.py', '.pyi'}
DEPENDENCY_IMPORTS = {'IPython', 'PIL', 'cmasher', 'ipywidgets', 'json5', 'matplotlib', 'numpy'}
DYNAMIC_LOADERS = {'importlib', 'runpy'}
DYNAMIC_BUILTINS = {'__import__', 'exec', 'eval'}


def git(*args):
    return subprocess.check_output(['git', *args])


def maintained(path):
    source = Path(path)
    return source.suffix in PYTHON_SUFFIXES and (
        source.is_relative_to(INTERACTIVE) or path == 'scripts/lint_staged_python.py'
    )


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
        if path == INTERACTIVE / 'explore.py' or path.is_relative_to(INTERACTIVE / 'tests'):
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


def main():
    if sys.argv[1:] == ['--imports']:
        return 0 if check_imports(staged=False) else 1

    changed = git('diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR').decode().split('\0')
    paths = git('ls-files', '-z').decode().split('\0') if 'ruff.toml' in changed else changed
    paths = [path for path in paths if maintained(path)]
    if not paths:
        return 0
    failed = not check_imports(staged=True)
    with tempfile.TemporaryDirectory(prefix='rug-index-') as directory:
        root = Path(directory)
        config = root / 'ruff.toml'
        config.write_bytes(git('show', ':ruff.toml'))
        for path in paths:
            source = git('show', ':' + path)
            for label, command in (('formatting', ['format', '--diff']), ('lint', ['check', '--quiet'])):
                result = subprocess.run(
                    [
                        sys.executable,
                        '-m',
                        'ruff',
                        *command,
                        '--config',
                        str(config),
                        '--stdin-filename',
                        path,
                        '-',
                    ],
                    input=source,
                    cwd=root,
                    check=False,
                )
                if result.returncode:
                    print(f'Python {label} failed (Ruff) for {path}', file=sys.stderr)
                    failed = True
                elif label == 'lint':
                    print(f'Python lint passed (Ruff) for {path}')
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
