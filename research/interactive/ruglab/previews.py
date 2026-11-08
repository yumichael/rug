"""Fast raster contact sheets for browsing arbitrary groups of fields."""

from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .plotting import indexed_order_palette


@dataclass(frozen=True)
class PreviewPanel:
    image: Image.Image
    caption: str


def indexed_preview(values, cmap, pixels):
    """Render an order-color thumbnail while preserving exact values for export."""
    palette = indexed_order_palette(values, cmap).view(np.uint32).ravel()
    height, width = values.indices.shape
    packed = np.ascontiguousarray(palette[values.indices])
    image = Image.frombuffer("RGBX", (width, height), packed, "raw", "RGBX", 0, 1)
    if image.size != (pixels, pixels):
        image = image.resize((pixels, pixels), Image.Resampling.BILINEAR)
    return image.convert("RGB")


@lru_cache(maxsize=2)
def _font(size):
    return ImageFont.load_default(size)


def preview_grid(rows, pixels=384):
    """Encode rows of (heading, panels) as one PNG. Panels have square images."""
    padding = 8
    heading_height = 30
    line_height = 18
    caption_height = line_height * max(panel.caption.count("\n") + 1 for _, panels in rows for panel in panels) + 6
    row_height = heading_height + caption_height + pixels + 2 * padding
    columns = max(len(panels) for _, panels in rows)
    width = columns * (pixels + padding) + padding
    image = Image.new("RGB", (width, len(rows) * row_height), "white")
    draw = ImageDraw.Draw(image)
    for row_index, (heading, panels) in enumerate(rows):
        top = row_index * row_height + padding
        draw.text((width // 2, top), heading, anchor="mt", font=_font(20), fill="black")
        for col_index, panel in enumerate(panels):
            left = padding + col_index * (pixels + padding)
            for line, text in enumerate(panel.caption.split("\n")):
                draw.text(
                    (left + pixels // 2, top + heading_height + line * line_height),
                    text,
                    anchor="mt",
                    font=_font(16),
                    fill="black",
                )
            image.paste(panel.image, (left, top + heading_height + caption_height))
    with BytesIO() as output:
        image.save(output, format="PNG", compress_level=1)
        return output.getvalue()
