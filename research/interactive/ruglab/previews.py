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


def preview_grid(rows, pixels=384, *, transpose=False, wrap_after=0):
    """Encode recipe rows as a PNG, optionally wrapping them into bands."""
    padding = 8
    heading_font = _font(20)
    heading_height = 0 if transpose else 30
    column_headings = [_heading_lines(heading, pixels, heading_font) for heading, _ in rows] if transpose else []
    column_heading_height = 22 * max(map(len, column_headings), default=0)
    line_height = 18
    caption_height = line_height * max(panel.caption.count("\n") + 1 for _, panels in rows for panel in panels) + 6
    row_height = heading_height + caption_height + pixels + 2 * padding
    band_size = min(wrap_after or len(rows), len(rows))
    band_count = (len(rows) + band_size - 1) // band_size
    sampling_count = max(len(panels) for _, panels in rows)
    columns, row_count = (band_size, sampling_count) if transpose else (sampling_count, band_size)
    band_width = columns * (pixels + padding) + padding
    band_height = column_heading_height + row_count * row_height
    width, height = (band_width, band_height * band_count) if transpose else (band_width * band_count, band_height)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    def draw_band(band, headings, offset_x, offset_y):
        for col_index, lines in enumerate(headings):
            center = offset_x + padding + col_index * (pixels + padding) + pixels // 2
            for line, text in enumerate(lines):
                draw.text((center, offset_y + padding + line * 22), text, anchor="mt", font=heading_font, fill="black")
        for row_index, (heading, panels) in enumerate(band):
            top = offset_y + column_heading_height + row_index * row_height + padding
            if heading:
                draw.text((offset_x + band_width // 2, top), heading, anchor="mt", font=heading_font, fill="black")
            for col_index, panel in enumerate(panels):
                left = offset_x + padding + col_index * (pixels + padding)
                for line, text in enumerate(panel.caption.split("\n")):
                    draw.text(
                        (left + pixels // 2, top + heading_height + line * line_height),
                        text,
                        anchor="mt",
                        font=_font(16),
                        fill="black",
                    )
                image.paste(panel.image, (left, top + heading_height + caption_height))

    for index, start in enumerate(range(0, len(rows), band_size)):
        band = rows[start : start + band_size]
        if transpose:
            transposed = [("", panels) for panels in zip(*(panels for _, panels in band), strict=True)]
            draw_band(transposed, column_headings[start : start + band_size], 0, index * band_height)
        else:
            draw_band(band, (), index * band_width, 0)
    with BytesIO() as output:
        image.save(output, format="PNG", compress_level=1)
        return output.getvalue()
