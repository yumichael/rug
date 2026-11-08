"""Convenience imports and display setup for interactive research notebooks."""

from copy import deepcopy
from functools import lru_cache
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
from .exploration import FIELD_SIZES, exploration_recipes, sample_field
from .operations import steps
from .plotting import colorize
from .previews import PreviewPanel, indexed_preview, preview_grid
from .research import family_pre_modulus, minimum_post_modulus, uniform_xor
from .specs import SAMPLINGS

__all__ = [
    "FIELD_SIZES",
    "SAMPLINGS",
    "BytesIO",
    "Path",
    "PreviewPanel",
    "Result",
    "Sweep",
    "clear_cache",
    "colorize",
    "deepcopy",
    "display",
    "dsl",
    "duplicates",
    "evaluate",
    "exploration_recipes",
    "export",
    "family_pre_modulus",
    "gallery",
    "grid",
    "indexed_preview",
    "load_presets",
    "lru_cache",
    "minimum_post_modulus",
    "np",
    "paired",
    "periods",
    "plt",
    "preview_grid",
    "sample_field",
    "sampling_gallery",
    "signature",
    "stages",
    "steps",
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
