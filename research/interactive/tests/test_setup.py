import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("external", [False, True])
def test_setup_environment_is_opt_in(tmp_path, external):
    script = tmp_path / "setup.sh"
    script.write_text(Path("setup.sh").read_text())
    binary = tmp_path / "uv"
    binary.write_text(
        """#!/bin/sh
{
    printf '%s\\t%s' "${UV_PROJECT_ENVIRONMENT-unset}" "${VIRTUAL_ENV-unset}"
    printf '\\t%s' "$@"
    printf '\\n'
} >> "$SETUP_LOG"
"""
    )
    binary.chmod(0o755)
    env = {
        **os.environ,
        "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
        "SETUP_LOG": str(tmp_path / "calls.tsv"),
        "VIRTUAL_ENV": "stale",
    }
    env.pop("UV_PROJECT_ENVIRONMENT", None)
    if external:
        env["UV_PROJECT_ENVIRONMENT"] = str(tmp_path / "external")
    subprocess.run(["sh", str(script)], env=env, check=True)
    calls = [line.split("\t") for line in (tmp_path / "calls.tsv").read_text().splitlines()]
    assert calls[0][2:] == ["sync", "--locked"]
    assert calls[1][2:6] == ["run", "--no-sync", "python", "-m"]
    assert all(call[:2] == [env.get("UV_PROJECT_ENVIRONMENT", "unset"), "unset"] for call in calls)
    assert not (tmp_path / ".venv").is_symlink()
