"""Portable, named JSON bookmarks with no machine-specific output paths."""

import json
from pathlib import Path


def save(path, name, spec, notes="", seed=None):
    path = Path(path)
    data = json.loads(path.read_text()) if path.exists() else {}
    from .specs import resolve

    resolved = resolve(spec) if isinstance(spec, dict) and "dsl" not in spec else spec
    data[name] = {"spec": resolved, "notes": notes, "seed": seed, "format_version": 1}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def load(path, query=""):
    data = json.loads(Path(path).read_text())
    return {
        name: item
        for name, item in data.items()
        if query.lower() in (name + " " + item.get("notes", "")).lower()
    }
