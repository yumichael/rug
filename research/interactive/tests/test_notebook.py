from pathlib import Path

import jupytext
from nbclient import NotebookClient


def test_text_notebook_roundtrip():
    book = jupytext.read("explore.py")
    text = jupytext.writes(book, fmt="py:percent")
    again = jupytext.reads(text, fmt="py:percent")
    assert [c.source for c in book.cells] == [c.source for c in again.cells]


def test_fresh_kernel():
    book = jupytext.read("explore.py")
    NotebookClient(
        book,
        timeout=120,
        kernel_name="rug-research",
        resources={"metadata": {"path": str(Path.cwd())}},
    ).execute()
