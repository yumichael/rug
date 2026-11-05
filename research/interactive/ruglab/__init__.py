"""Notebook-facing research tools."""

from . import dsl, gallery
from .diagnostics import duplicates, periods, signature, summary, symmetries
from .engine import Result, clear_cache, evaluate
from .plotting import export, grid, sampling_gallery, stages
from .sweeps import Sweep, paired

__all__ = [
    "Result",
    "Sweep",
    "clear_cache",
    "dsl",
    "duplicates",
    "evaluate",
    "export",
    "gallery",
    "grid",
    "paired",
    "periods",
    "sampling_gallery",
    "signature",
    "stages",
    "summary",
    "symmetries",
]
