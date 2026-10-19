"""Generate the playback (OSD / seek bar / offset strip) textures for skin.majan.

Owner: Builder D (Playback). Pillow only, reproducible. White on transparent, tinted in XML.

Why these exist (Kodi Omega GUISliderControl / GUIRangesControl maths):
  * Slider nib: Kodi sizes a horizontal nib as  h = nibTexH * (controlH / barTexH),  w = 2 * h.
    So a thin "playhead" needs a nib texture that is twice as wide as tall with a narrow
    opaque column in the middle. With the transparent bar texture below (16x32) and the nib
    (64x32), a slider control H px tall draws a playhead H px tall and H/4 px wide
    (16 -> 4 px, 20 -> 5 px). Exported at 2x (SPEC decision 8, 4K readiness).
  * slider_bg: fully transparent bar texture (the visible track is a separate 2-4 px image).
  * tick: chapter tick for <control type="ranges">. Ranges draw end textures at their RAW
    texture width (unscaled) and height = controlH * texH / bgTexH, so the tick is exactly
    2 px wide and as tall as the ranges control when its texturebg is slider_bg (32 px tall).

Usage:  python skins/skin.majan/_src/make_osd_textures.py
Writes: skins/skin.majan/media/osd/{slider_nib,slider_bg,tick}.png
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "osd"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # 64x32 nib, 8 px opaque column centred (x 28..35) -> 1/8 of the nib width
    nib = Image.new("RGBA", (64, 32), (255, 255, 255, 0))
    ImageDraw.Draw(nib).rectangle([28, 0, 35, 31], fill=(255, 255, 255, 255))
    nib.save(OUT / "slider_nib.png", optimize=True)

    # transparent bar, 16x32 (its height is what the nib/tick scale against)
    Image.new("RGBA", (16, 32), (255, 255, 255, 0)).save(OUT / "slider_bg.png", optimize=True)

    # 2x32 chapter tick
    Image.new("RGBA", (2, 32), (255, 255, 255, 255)).save(OUT / "tick.png", optimize=True)

    for p in sorted(OUT.glob("*.png")):
        print(p.relative_to(HERE.parent), Image.open(p).size)


if __name__ == "__main__":
    main()
