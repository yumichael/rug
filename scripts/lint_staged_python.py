"""Check maintained indexed Python using indexed Ruff configuration, without writes."""

import subprocess
import sys
import tempfile
from pathlib import Path


def git(*args):
    return subprocess.check_output(['git', *args])


def maintained(path):
    return path.endswith(('.py', '.pyi')) and (
        path.startswith('research/interactive/') or path == 'scripts/lint_staged_python.py'
    )


def main():
    changed = git('diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR').decode().split('\0')
    paths = git('ls-files', '-z').decode().split('\0') if 'ruff.toml' in changed else changed
    paths = [path for path in paths if maintained(path)]
    if not paths:
        return 0
    failed = False
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
