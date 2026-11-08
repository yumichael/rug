"""Fixed-scale previews and color tools, with no display-time arithmetic changes."""

import colorsys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from PIL import Image

from .engine import Result, evaluate


def convert_color(a, space):
    if space == "rgb":
        return a
    if space == "hsv":
        return colors.hsv_to_rgb(a)
    if space == "hsl":
        flat = np.asarray([colorsys.hls_to_rgb(h, l, s) for h, s, l in a.reshape(-1, 3)])
        return flat.reshape(a.shape)
    raise ValueError("Color space must be RGB, HSV, or HSL")


def _colormap(name):
    if name.startswith("cmr."):
        import cmasher  # noqa: F401 - Registers the cmr colormaps.

    return plt.get_cmap(name)


def colorize(result, mode="values", cmap=None):
    from .diagnostics import ranks

    if mode == "order":
        a = ranks(result)
        a = a / max(1, int(a.max()))
    else:
        a = result.normalized(anchored=mode == "anchored")
    return _colormap(cmap or result.colors)(np.clip(a, 0, 1))[..., :3]


def indexed_order_palette(values, cmap):
    """Map distinct residues to RGBA bytes in the same order as export."""
    count = len(values.labels)
    ranks = np.empty(count, dtype=np.intp)
    labels = values.labels
    order = sorted(range(count), key=labels.tolist().__getitem__) if labels.dtype == object else labels.argsort()
    ranks[order] = np.arange(count)
    # Anchoring rotates the sorted residues around the first cell.
    ranks = (ranks - ranks[values.indices[0, 0]]) % count
    colors = _colormap(cmap)(ranks / max(1, count - 1))
    return np.rint(colors * 255).astype(np.uint8)


def grid(items, cols=4, width=12, mode="values", cmap=None):
    items = list(items.items() if isinstance(items, dict) else items)
    if not items:
        raise ValueError("No patterns to show")
    rows = (len(items) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(width, width / cols * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, (name, spec) in zip(axes.flat, items, strict=False):
        if isinstance(spec, list):
            from .dsl import render

            image = render(spec)
            caption = "DSL"
        else:
            r = spec if isinstance(spec, Result) else evaluate(spec)
            image = colorize(r, mode, cmap)
            caption = f"{r.values.shape} M={r.modulus}"
        ax.imshow(image, interpolation="nearest")
        ax.set_title(f"{name}\n{caption}", fontsize=9)
    fig.tight_layout()
    return fig


def sampling_gallery(spec, **kwargs):
    from .specs import SAMPLINGS

    return grid([(name, {**spec, "sampling": name}) for name in SAMPLINGS], **kwargs)


def stages(result):
    items = []
    for name, a in result.stages.items():
        # Raw stages use a declared range label rather than implying channel normalization.
        high = max(1, max(int(x) for x in a.flat) + 1)
        items.append((name, Result(a, high, {})))
    items.append(("final", result))
    return grid(items)


def export(result, path, scale=1, mode="values"):
    image = Image.fromarray(np.rint(colorize(result, mode) * 255).astype("uint8"))
    if scale != 1:
        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    from pathlib import Path

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
