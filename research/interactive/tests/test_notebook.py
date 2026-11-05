import json
import sys
from pathlib import Path

import jupytext
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient


def test_text_notebook_roundtrip():
    book = jupytext.read("explore.py")
    text = jupytext.writes(book, fmt="py:percent")
    again = jupytext.reads(text, fmt="py:percent")
    assert [c.source for c in book.cells] == [c.source for c in again.cells]


def test_fresh_kernel(tmp_path):
    kernels = tmp_path / 'kernels'
    location = kernels / 'rug-test'
    location.mkdir(parents=True)
    (location / 'kernel.json').write_text(
        json.dumps(
            {
                'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                'display_name': 'Rug test',
                'language': 'python',
            }
        )
    )
    manager = KernelManager(kernel_name='rug-test', kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]))
    book = jupytext.read('explore.py')
    client = NotebookClient(
        book, timeout=120, km=manager, kernel_name='rug-test', resources={'metadata': {'path': str(Path.cwd())}}
    )
    try:
        client.execute()
    finally:
        if client.kc is not None:
            client.kc.stop_channels()
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
