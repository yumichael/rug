"""Convenience imports and display setup for interactive research notebooks."""

from io import BytesIO
from pathlib import Path

import ipywidgets as widgets
import json5
import matplotlib.pyplot as plt
import numpy as np
from IPython import get_ipython
from IPython.display import display

from . import (
    Result,
    Sweep,
    clear_cache,
    dsl,
    duplicates,
    evaluate,
    export,
    gallery,
    grid,
    paired,
    periods,
    sampling_gallery,
    signature,
    stages,
    summary,
    symmetries,
)
from .research import family_pre_modulus, minimum_post_modulus, uniform_xor

__all__ = [
    "BytesIO",
    "Path",
    "Result",
    "Sweep",
    "clear_cache",
    "display",
    "dsl",
    "duplicates",
    "evaluate",
    "export",
    "family_pre_modulus",
    "gallery",
    "grid",
    "load_presets",
    "minimum_post_modulus",
    "np",
    "paired",
    "periods",
    "plt",
    "sampling_gallery",
    "signature",
    "stages",
    "summary",
    "symmetries",
    "uniform_xor",
    "widgets",
]


def load_presets():
    """Read a fresh copy of the shared example presets."""
    path = Path(__file__).resolve().parents[1] / "presets" / "examples.jsonc"
    return json5.loads(path.read_text(encoding="utf-8"))


_shell = get_ipython()
if _shell is not None:
    _shell.extension_manager.load_extension("autoreload")
    _shell.run_line_magic("autoreload", "2")
    _shell.run_line_magic("matplotlib", "inline")
