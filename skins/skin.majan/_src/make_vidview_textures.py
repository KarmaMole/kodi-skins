"""Textures owned by Builder B (video library views). Pillow only, reproducible.

Writes:
  media/vidview/underline.png  8 x 80, white, bottom 4 rows opaque, rest transparent.
      Used as the <texturenofocus> of the ACTIVE library filter button (ALL / UNWATCHED /
      IN PROGRESS) so the 2 px accent underline sits under the label without knowing the
      button's auto width. Buttons are 40 px tall (constant subnav_h): Kodi stretches the
      texture to the button rect, so 80 -> 40 is an exact 2:1 downscale at 1080p (2 px line)
      and 1:1 at a 2160p GUI (SPEC decision 8, 4K readiness). Tint with $VAR[ColorAccent].

Usage:  python skins/skin.majan/_src/make_vidview_textures.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media" / "vidview"


def underline() -> Image.Image:
    img = Image.new("RGBA", (8, 80), (255, 255, 255, 0))
    for y in range(76, 80):
        for x in range(8):
            img.putpixel((x, y), (255, 255, 255, 255))
    return img


def dim(alpha: int) -> Image.Image:
    """Solid black at a baked alpha, laid over an OPAQUE poster in a fixed-focus row.
    Black at alpha a over an opaque image = brightness (1 - a): the result stays opaque,
    nothing behind the poster shows through (DESIGN 6 "dim, never fade").
    dim_passed: brightness .45 (a = .55) / dim_ahead: brightness .80 (a = .20)."""
    return Image.new("RGBA", (8, 8), (0, 0, 0, alpha))


def main() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    outputs = {
        "underline.png": underline(),
        "dim_passed.png": dim(round(255 * 0.55)),
        "dim_ahead.png": dim(round(255 * 0.20)),
    }
    for name, img in outputs.items():
        if name == "underline.png":
            continue  # no XML names it (removed from media/ 2026-10-30)
        out = MEDIA / name
        img.save(out, optimize=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
