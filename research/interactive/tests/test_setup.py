import json
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
        "#!/usr/bin/env python3\n"
        + """import json, os, sys
with open(os.environ['SETUP_LOG'], 'a') as log:
    log.write(json.dumps([sys.argv[1:], os.environ.get('UV_PROJECT_ENVIRONMENT'), os.environ.get('VIRTUAL_ENV')]) + '\\n')
"""
    )
    binary.chmod(0o755)
    env = {
        **os.environ,
        "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
        "SETUP_LOG": str(tmp_path / "calls.jsonl"),
        "VIRTUAL_ENV": "stale",
    }
    env.pop("UV_PROJECT_ENVIRONMENT", None)
    if external:
        env["UV_PROJECT_ENVIRONMENT"] = str(tmp_path / "external")
    subprocess.run(["sh", str(script)], env=env, check=True)
    calls = [json.loads(line) for line in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert calls[0][0] == ["sync", "--locked"]
    assert calls[1][0][:4] == ["run", "--no-sync", "python", "-m"]
    assert all(call[1] == env.get("UV_PROJECT_ENVIRONMENT") and call[2] is None for call in calls)
    assert not (tmp_path / ".venv").is_symlink()
