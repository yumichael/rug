"""App-only setup and commits must work without Python tooling on PATH."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path.cwd().parents[1]
pytestmark = pytest.mark.integration


def app_repo(tmp_path):
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    binary = tmp_path / 'bin'
    binary.mkdir()
    for command in ('git', 'dirname', 'sh'):
        (binary / command).symlink_to(shutil.which(command))
    node = binary / 'node'
    node.write_text('#!/bin/sh\nexit 0\n')
    node.chmod(0o755)
    return {**os.environ, 'PATH': str(binary), 'RUG_NODE': str(node)}


def test_general_setup_does_not_install_research(tmp_path):
    env = app_repo(tmp_path)
    setup = tmp_path / 'setup-dev.sh'
    setup.write_text((ROOT / 'setup-dev.sh').read_text())
    scripts = tmp_path / 'scripts'
    scripts.mkdir()
    (scripts / 'setup-rumdl.sh').write_text('#!/bin/sh\nexit 0\n')
    subprocess.run(['/bin/sh', str(setup)], env=env, check=True)
    assert not (tmp_path / 'research').exists()


def test_nonresearch_commit_needs_no_uv(tmp_path):
    env = app_repo(tmp_path)
    for path in ('index.html', 'docs/example.md', 'research/theory/dated/proof.py'):
        source = tmp_path / path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('content\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', '.'], check=True)
    subprocess.run(['/bin/sh', str(ROOT / 'scripts/hooks/pre-commit')], cwd=tmp_path, env=env, check=True)


@pytest.mark.parametrize(
    'path',
    [
        'research/interactive/explore.py',
        'research/interactive/ruglab/a.py',
        'research/interactive/a.pyi',
        'scripts/lint_staged_python.py',
        'ruff.toml',
    ],
)
def test_research_commit_requires_uv(tmp_path, path):
    env = app_repo(tmp_path)
    source = tmp_path / path
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('content\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', '.'], check=True)
    result = subprocess.run(
        ['/bin/sh', str(ROOT / 'scripts/hooks/pre-commit')],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert 'Install uv' in result.stderr
