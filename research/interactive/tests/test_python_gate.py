import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path.cwd().parents[1]


def run_gate(tmp_path, staged, working, *, config_change=False, filename="with spaces.py"):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    source = tmp_path / 'research/interactive' / filename
    source.parent.mkdir(parents=True)
    config = tmp_path / 'ruff.toml'
    config.write_text((ROOT / 'ruff.toml').read_text())
    source.write_text(staged)
    subprocess.run(['git', '-C', str(tmp_path), 'add', '.'], check=True)
    source.write_text(working)
    if config_change:
        config.write_text('[lint]\nignore=["F821"]\n')
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/lint_staged_python.py')],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert source.read_text() == working
    return result


@pytest.mark.parametrize(
    ('staged', 'working', 'success'),
    [('x = 1\n', 'x=missing\n', True), ('x = missing\n', 'x = 1\n', False), ('x=1\n', 'x = 1\n', False)],
)
def test_gate_uses_index_and_preserves_worktree(tmp_path, staged, working, success):
    result = run_gate(tmp_path, staged, working)
    assert (result.returncode == 0) == success, result.stdout + result.stderr


def test_gate_uses_indexed_configuration(tmp_path):
    result = run_gate(tmp_path, 'x = missing\n', 'x = 1\n', config_change=True)
    assert result.returncode != 0
    assert 'F821' in result.stdout + result.stderr or 'undefined-name' in result.stdout + result.stderr


def test_gate_preserves_notebook_allowances(tmp_path):
    result = run_gate(tmp_path, 'print(1)\nimport os\n', 'print(1)\nimport os\n', filename='explore.py')
    assert result.returncode == 0, result.stdout + result.stderr
