"""Schematic view previews for the view picker (SPEC 7).   python skins/skin.vernissage/_src/make_view_previews.py

media/vn/views/{day,evening}/{salon,gallery_wall,catalogue}[_music].png, 320 x 180 (video / music kinds): each view drawn at 1920 x 1080 from its
own geometry (Includes_LibViews.xml / SPEC 8) with the room's palette, then reduced. No real art (public skin,
LESSONS 383): prints are flat greys, the lit work a lighter block in its mat and frame. The picker picks the folder
with $VAR[VN_RoomDir] (Day text set = day). M2 may move to white-alpha layers tinted per step (Daylight pattern).
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "vn" / "views"
COLORS = (ROOT / "colors" / "defaults.xml").read_text(encoding="utf-8")


def col(name):
    h = re.search(rf'<color name="{name}">([0-9a-f]{{8}})</color>', COLORS).group(1)
    return tuple(int(h[i:i + 2], 16) for i in (2, 4, 6))


def palette(room):
    p = "day_" if room == "day" else "eve_"
    pal = {k: col(p + k) for k in ("wall", "card", "card_edge", "ink", "ink2", "rule", "mat", "frame")}
    pal["print"] = (198, 196, 192) if room == "day" else (70, 70, 74)
    pal["print2"] = (214, 212, 208) if room == "day" else (58, 58, 62)
    pal["lit"] = (150, 148, 144) if room == "day" else (176, 172, 166)
    return pal


def lit(d, x, y, w, h, mat, pal):
    d.rectangle((x - mat - 2, y - mat - 2, x + w + mat + 1, y + h + mat + 1), fill=pal["frame"])
    d.rectangle((x - mat, y - mat, x + w + mat - 1, y + h + mat - 1), fill=pal["mat"])
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=pal["lit"])


def placard(d, x, y, w, h, pal, lines=3):
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=pal["card"], outline=pal["card_edge"], width=2)
    for i in range(lines):
        d.rectangle((x + 30, y + 34 + i * 54, x + w - 60 - i * 50, y + 34 + i * 54 + 22), fill=pal["ink2"] if i else pal["ink"])
    d.rectangle((x + 30, y + h - 110, x + 86, y + h - 106), fill=pal["rule"])
    d.rectangle((x + 30, y + h - 80, x + w - 120, y + h - 56), fill=pal["ink"])


def header(d, pal):
    d.rectangle((120, 70, 470, 118), fill=pal["ink"])
    d.rectangle((520, 88, 940, 110), fill=pal["ink2"])


def salon(d, pal, music=False):
    """View 500 (screens/View_500_Salon.md): cells 120 + 188 c / 182 + 283 r (albums 288 / 268), the lit cell
    enlarged in place (10 px mat) with its placard beside it."""
    header(d, pal)
    cols, cw, ch, pw, ph = (6, 288, 268, 240, 240) if music else (9, 188, 283, 170, 255)
    lc, lr = 2, 1
    for r in range(3):
        for c in range(cols):
            if (r, c) == (lr, lc):
                continue
            x, y = 120 + c * cw, 182 + r * ch
            d.rectangle((x, y, x + pw - 1, y + ph - 1), fill=pal["print"] if (r + c) % 2 else pal["print2"])
    aw, ah = (300, 300) if music else (214, 321)
    x = 120 + lc * cw + pw // 2 - aw // 2
    y = 182 + lr * ch + ph // 2 - ah // 2
    lit(d, x, y, aw, ah, 10, pal)
    placard(d, x + aw + 10 + 2 + 26, y - 10, 340, ah + 20, pal)


def gallery(d, pal, music=False):
    """View 510 (screens/View_510_GalleryWall.md): one 560 x 840 work in a 24 px mat (albums 720 square), its 520 px
    placard of the same height, grey neighbours cut by the screen edges."""
    d.rectangle((120, 66, 760, 92), fill=pal["ink2"])
    if music:
        d.rectangle((-170, 258 + 112, 170, 598 + 112), fill=pal["print"])
        d.rectangle((1820, 370, 2160, 710), fill=pal["print"])
        lit(d, 356, 198, 720, 720, 24, pal)
        placard(d, 1158, 174, 520, 768, pal, lines=4)
    else:
        d.rectangle((-170, 285, 170, 795), fill=pal["print"])
        d.rectangle((1660, 285, 2000, 795), fill=pal["print"])
        lit(d, 356, 138, 560, 840, 24, pal)
        placard(d, 998, 114, 520, 888, pal, lines=4)


def catalogue(d, pal, music=False):
    """View 50 (screens/View_50_Catalogue.md): 13 rows of 64 from y 182, one lit row, the figure + placard column."""
    header(d, pal)
    for i in range(13):
        y = 182 + i * 64
        if i == 3:
            d.rectangle((120, y, 1159, y + 63), fill=pal["card"], outline=pal["card_edge"])
        d.rectangle((144, y + 22, 144 + 420 - (i * 37) % 160, y + 42), fill=pal["ink" if i == 3 else "ink2"])
        d.rectangle((1016 - 90, y + 24, 1016, y + 40), fill=pal["ink" if i == 3 else "ink2"])
        if i != 3:
            d.rectangle((144, y + 63, 1136, y + 63), fill=pal["rule"])
    if music:
        lit(d, 1252, 194, 400, 400, 10, pal)
        placard(d, 1240, 630, 552, 374, pal)
    else:
        lit(d, 1252, 194, 528, 297, 10, pal)
        placard(d, 1240, 527, 552, 477, pal)


def main():
    for room in ("day", "evening"):
        pal = palette(room)
        for (name, fn), music in [(v, m) for v in (("salon", salon), ("gallery_wall", gallery), ("catalogue", catalogue))
                                  for m in (False, True)]:
            im = Image.new("RGB", (1920, 1080), pal["wall"])
            fn(ImageDraw.Draw(im), pal, music)
            p = OUT / room / f"{name}{'_music' if music else ''}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            im.resize((320, 180), Image.LANCZOS).save(p, optimize=True)
    print("view previews ->", OUT)


if __name__ == "__main__":
    main()
