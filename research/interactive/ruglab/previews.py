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


def _packed_image(indices, palette):
    height, width = indices.shape
    packed = np.ascontiguousarray(palette[indices])
    return Image.frombuffer("RGBX", (width, height), packed, "raw", "RGBX", 0, 1)


def indexed_preview(values, cmap, pixels):
    """Render an order-color thumbnail while preserving exact values for export."""
    palette = indexed_order_palette(values, cmap).view(np.uint32).ravel()
    height, width = values.indices.shape
    if width > 1024 and pixels < width:
        # Bilinear resize is separable. Color and shrink horizontally by
        # strips, then resize vertically without a full-size RGB raster.
        image = Image.new("RGBX", (pixels, height))
        for start in range(0, height, 128):
            block = values.indices[start : start + 128]
            strip = _packed_image(block, palette).resize((pixels, len(block)), Image.Resampling.BILINEAR)
            image.paste(strip, (0, start))
    else:
        image = _packed_image(values.indices, palette)
    if image.size != (pixels, pixels):
        resampling = Image.Resampling.NEAREST if max(width, height) <= 128 else Image.Resampling.BILINEAR
        image = image.resize((pixels, pixels), resampling)
    return image.convert("RGB")


@lru_cache(maxsize=2)
def _font(size):
    return ImageFont.load_default(size)


def _heading_lines(heading, width, font):
    lines = []
    line = ""
    for word in heading.split():
        joined = f"{line} {word}".lstrip()
        if line and font.getlength(joined) > width:
            lines.append(line)
            line = word
        else:
            line = joined
    return [*lines, line]


def preview_grid(rows, pixels=384, *, transpose=False):
    """Encode (heading, panels) rows as a PNG. Transpose requires equal row lengths."""
    padding = 8
    heading_font = _font(20)
    heading_height = 0 if transpose else 30
    column_headings = []
    if transpose:
        column_headings = [_heading_lines(heading, pixels, heading_font) for heading, _ in rows]
        rows = [("", panels) for panels in zip(*(panels for _, panels in rows), strict=True)]
    column_heading_height = 22 * max(map(len, column_headings), default=0)
    line_height = 18
    caption_height = line_height * max(panel.caption.count("\n") + 1 for _, panels in rows for panel in panels) + 6
    row_height = heading_height + caption_height + pixels + 2 * padding
    columns = max(len(panels) for _, panels in rows)
    width = columns * (pixels + padding) + padding
    image = Image.new("RGB", (width, column_heading_height + len(rows) * row_height), "white")
    draw = ImageDraw.Draw(image)
    for col_index, lines in enumerate(column_headings):
        center = padding + col_index * (pixels + padding) + pixels // 2
        for line, text in enumerate(lines):
            draw.text((center, padding + line * 22), text, anchor="mt", font=heading_font, fill="black")
    for row_index, (heading, panels) in enumerate(rows):
        top = column_heading_height + row_index * row_height + padding
        if heading:
            draw.text((width // 2, top), heading, anchor="mt", font=heading_font, fill="black")
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
