"""Textures owned by Builder C (Music) for skin.majan.

Writes:
  media/music/tab_underline.png  8 x 12, rows 9-11 white, rest transparent.
      9-slice, use with border="0,8,0,3" (left,top,right,bottom): the transparent top rows
      and the 3 px white bottom rows keep their size, the 1 transparent middle row stretches.
      Result on any button: a 3 px bar flush with the bottom edge, as wide as the button.
      Tint with colordiffuse="$VAR[ColorAccent]". Used for the active music header tab
      (Music.dc.html: "ALBUMS 229" with a 3 px accent underline).
      9-slice art stays 1x (see make_textures.py, 4K note): Kodi reads border in texels.
  media/music/square_round8_560.png  1120 x 1120 (2x), white rounded square, radius 8 at 560 px.
      Diffuse mask for 560 x 560 covers (Now playing, playlist art panel, music list panel):
      outside the 340-420 range of masks/square_round8_large.png (DESIGN 7.1).

Usage:  python skins/skin.majan/_src/make_music_textures.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SS = 8      # supersampling, same as make_textures.py
HIDPI = 2   # masks are exported at 2x their drawn size (4K readiness, DESIGN / SPEC decision 8)

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"


def tab_underline() -> Path:
    img = Image.new("RGBA", (8, 12), (255, 255, 255, 0))
    for y in range(9, 12):
        for x in range(8):
            img.putpixel((x, y), (255, 255, 255, 255))
    out = MEDIA / "music" / "tab_underline.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


def rounded_mask(size: int, radius: float, rel: str) -> Path:
    w = size * HIDPI
    big = Image.new("L", (w * SS, w * SS), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * SS - 1, w * SS - 1), radius=radius * HIDPI * SS, fill=255)
    alpha = big.resize((w, w), Image.LANCZOS)
    img = Image.new("RGBA", (w, w), (255, 255, 255, 255))
    img.putalpha(alpha)
    out = MEDIA / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


def main() -> None:
    p = tab_underline()
    print(f"wrote {p.relative_to(HERE.parent)}  (border=\"0,8,0,3\")")
    p = rounded_mask(560, 8, "music/square_round8_560.png")
    print(f"wrote {p.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
