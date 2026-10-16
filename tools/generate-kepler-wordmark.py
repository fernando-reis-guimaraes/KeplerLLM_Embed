#!/usr/bin/env python3
"""Deterministic Kepler LLM wordmark generator (embed variant).

Reproduces the AnythingLLM embed wordmark pattern (infinity mark + Name LLM,
monochrome) with the text swapped to Kepler LLM, using the repo's own
Plus Jakarta Sans font (copied from KeplerLLM/frontend).

Reference geometry is measured from the last upstream embed wordmark asset
(origin/main:src/assets/anything-llm-dark.png, 634x99):
  - canvas 634x99; icon preserved verbatim (crop x 0..104, i.e. icon_end=99
    plus 5px margin)
  - text drawn with anchor='lt' at text_start=123, orig_top=16
  - dark variant color (34,38,40); transparent background
  - text 'Kepler LLM' (with space, monochrome) at size 86, stroke 2

Rendering recipe inherited from the validated QuantaLLM rebrand
(PlusJakartaSans Regular at size 86 with stroke_width=2 -- the look the
owner already approved as 'muito bom'), adapted for the embed canvas
(634x99 vs 704x99) and spaced text 'Kepler LLM'.

Output (single file):
  - src/assets/kepler-llm-dark.png

Determinism: no timestamps, no randomness; PNG saved with default
encoder settings. Re-running yields byte-identical files (hash printed).

Requires: Pillow (pip install pillow). Run from repo root:
  python3 tools/generate-kepler-wordmark.py
"""

import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "tools/fonts/PlusJakartaSans.ttf"
OUTPUT_PATH = "src/assets/kepler-llm-dark.png"

TEXT = "Kepler LLM"
SIZE = 86
STROKE = 2
ICON_END = 99
TEXT_X = 123
TEXT_Y = 16  # orig_top
CANVAS = (634, 99)

DARK = (34, 38, 40, 255)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    # Regular weight + stroke (validated recipe); no variation axes.
    return ImageFont.truetype(str(FONT_PATH), size)


def build_wordmark(ref_image: Image.Image, color: tuple) -> Image.Image:
    w, h = ref_image.size
    font = load_font(SIZE)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # Icon pixels preserved verbatim from the original variant.
    canvas.alpha_composite(ref_image.crop((0, 0, ICON_END + 5, h)), (0, 0))
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    full = tmp.textbbox((0, 0), TEXT, font=font, stroke_width=STROKE,
                        anchor="lt")
    first = tmp.textbbox((0, 0), TEXT[0], font=font, stroke_width=STROKE,
                         anchor="lt")
    draw = ImageDraw.Draw(canvas)
    draw.text((TEXT_X - first[0], TEXT_Y - full[1]), TEXT, font=font,
              fill=color, stroke_width=STROKE, stroke_fill=color,
              anchor="lt")
    return canvas


def main() -> int:
    # Geometry measured from upstream asset; validate before rendering.
    assert CANVAS == (634, 99), CANVAS
    assert ICON_END == 99, ICON_END
    assert TEXT_X == 123, TEXT_X
    assert TEXT_Y == 16, TEXT_Y

    ref_path = ROOT / OUTPUT_PATH
    assert FONT_PATH.is_file(), f"missing font: {FONT_PATH}"
    assert ref_path.is_file(), f"missing reference/output: {ref_path}"
    ref = Image.open(ref_path).convert("RGBA")
    assert ref.size == CANVAS, ref.size

    # Sanity: gap between icon (ends at 99) and text (starts at 123)
    # must be transparent in the reference (validates icon_end/text_start).
    # Note: after first regeneration the reference IS the regenerated file
    # (same icon pixels, wider gap due to shorter text) -- gap check still
    # holds because both original (99..123) and regenerated (99..131)
    # gaps are transparent; we check the narrower original gap.
    gap = ref.crop((99, 0, 123, ref.size[1]))
    assert gap.getbbox() is None, gap.getbbox()

    out = build_wordmark(ref, DARK)
    assert out.size == CANVAS, out.size
    # Kepler LLM (10 chars incl. space) renders narrower than the 12-char
    # upstream text; its right edge must land well within canvas so existing
    # layout is preserved (original right ~505 rel.; new ~441 rel.).
    right = out.crop((TEXT_X, 0, CANVAS[0], CANVAS[1])).getbbox()[2]
    assert 400 <= right <= 500, right

    out.save(ref_path)
    data = ref_path.read_bytes()
    print(f"{hashlib.md5(data).hexdigest()}  {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
