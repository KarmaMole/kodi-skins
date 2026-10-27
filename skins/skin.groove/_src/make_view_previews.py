"""Schematic view previews for the view picker (Library panel 9851).   python skins/skin.groove/_src/make_view_previews.py

Writes media/groove/views/{dark,light}/<view>.png at 576x324 (drawn at 288x162, 2x for the 1.06 focus zoom).
Each preview is drawn on the 1920x1080 grid from the views' own constants (screens/View_*.md), then reduced:
no real art anywhere (public skin). Grey blocks stand for covers; the focused one is lit with a warm glow.
Previews: cover_wall_music, crate_dig, shelf, orbit, list_music (music lane); cover_wall_video, backdrop_carousel,
list_video (MyVideoNav's VidView_PickerItems reads these names).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[1] / "media" / "groove" / "views"
W, H = 1920, 1080
SCALE = 576 / 1920

ROOMS = {
    "dark": dict(ground=(34, 31, 28), edge=(25, 23, 21), block=(74, 69, 64), block2=(56, 52, 48), lit=(214, 200, 182),
                 glow=(232, 217, 196), ink=(235, 235, 235), ink2=(140, 140, 140), line=(70, 66, 62), wood=(52, 44, 38),
                 wood2=(40, 34, 29), glow_a=0.55),
    "light": dict(ground=(237, 231, 221), edge=(227, 220, 208), block=(206, 198, 186), block2=(219, 212, 201),
                  lit=(150, 128, 98), glow=(200, 174, 136), ink=(29, 26, 23), ink2=(110, 104, 98), line=(200, 192, 180),
                  wood=(214, 196, 168), wood2=(196, 176, 146), glow_a=0.45),
}
SPINES = [(150, 70, 60), (90, 110, 80), (140, 120, 70), (80, 90, 120), (120, 80, 110), (160, 110, 60), (70, 110, 110),
          (130, 130, 130), (110, 60, 60), (90, 90, 70)]


def ground(c):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - 960) / 1100) ** 2 + ((y - 470) / 800) ** 2).clip(0, 1)
    rgb = np.array(c["ground"]) * (1 - d[..., None]) + np.array(c["edge"]) * d[..., None]
    return Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")


def glow(img, c, cx, cy, r):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    a = (1 - d.clip(0, 1)) ** 2 * c["glow_a"]
    layer = np.zeros((H, W, 4), np.uint8)
    layer[..., :3] = c["glow"]
    layer[..., 3] = (a * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(layer, "RGBA"))


def rect(d, x, y, w, h, col, outline=None, width=0):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=col, outline=outline, width=width)


def header(d, c):
    for i in range(5):
        d.ellipse([96 + 96 * i, 54, 96 + 96 * i + 44, 98], outline=c["ink2"], width=5)
    for x in (1584, 1680, 1776):
        d.ellipse([x, 54, x + 44, 98], outline=c["ink2"], width=5)


def caption(d, c, cx, y, w=640):
    rect(d, cx - w // 2, y, int(w * 0.62), 26, c["ink"])
    rect(d, cx - w // 2 + int(w * 0.66), y + 4, int(w * 0.34), 20, c["ink2"])


def lit(img, d, c, x, y, w, h, r=None):
    glow(img, c, x + w / 2, y + h / 2, r or max(w, h) * 1.4)
    d = ImageDraw.Draw(img)
    rect(d, x, y, w, h, c["lit"], outline=c["ink"], width=5)
    return d


def cover_wall(img, c, video=False):
    d = ImageDraw.Draw(img)
    header(d, c)
    ch, h = (360, 336) if video else (240, 224)
    for r in range(4 if not video else 3):
        for col in range(8):
            if (r, col) != ((0, 2) if video else (1, 5)):
                rect(d, 8 + 240 * col, 158 + ch * r, 224, h, c["block"] if r < (3 if not video else 2) else c["block2"])
    if video:
        lit(img, d, c, 8 + 240 * 2, 158, 224, 336)
    else:
        lit(img, d, c, 8 + 240 * 5, 158 + 240, 224, 224)
    d = ImageDraw.Draw(img)
    caption(d, c, 960, 976)


def crate(img, c):
    d = ImageDraw.Draw(img)
    header(d, c)
    rect(d, 400, 572, 1120, 330, c["wood2"])
    for k in range(9, 0, -1):
        w = round(500 * (1 - 0.024 * k))
        rect(d, 960 - w // 2, 262 - 21 * k, w, 30, c["block"] if k % 2 else c["block2"])
    d = lit(img, d, c, 710, 262, 500, 500, 700)
    rect(d, 400, 782, 1120, 190, c["wood"])
    rect(d, 890, 828, 140, 32, c["wood2"])
    caption(d, c, 960, 992)


def shelf(img, c):
    d = ImageDraw.Draw(img)
    header(d, c)
    for k in range(-19, 17):
        if k == 0:
            continue
        x = 694 - 42 * (-k - 1) if k < 0 else 1286 + 42 * (k - 1)
        col = SPINES[(k + 40) % len(SPINES)]
        if c is ROOMS["light"]:
            col = tuple(min(255, v + 70) for v in col)
        rect(d, x, 300, 40, 500, col)
    rect(d, 0, 800, 1920, 34, c["wood"])
    d = lit(img, d, c, 760, 326, 500, 500, 700)
    caption(d, c, 1010, 870)


def orbit(img, c):
    d = ImageDraw.Draw(img)
    header(d, c)
    slots = [(-3, 115, 178, 100), (3, 1705, 178, 100), (-2, 250, 230, 160), (2, 1510, 230, 160), (-1, 445, 280, 250),
             (1, 1225, 280, 250)]
    for k, x, y, s in slots:
        rect(d, x, y + 120, s, s, c["block"] if abs(k) == 1 else c["block2"])
    d = lit(img, d, c, 750, 340, 420, 420, 600)
    caption(d, c, 960, 800, 420)


def list_view(img, c, video=False):
    d = ImageDraw.Draw(img)
    header(d, c)
    for i in range(13):
        y = 150 + 64 * i
        if i == 3:
            rect(d, 84, y, 784, 64, c["block2"])
        if not video:
            rect(d, 96, y + 10, 44, 44, c["block"])
        rect(d, 96 + (64 if not video else 0), y + 22, 380 - (i * 37) % 160, 20, c["ink"] if i == 3 else c["ink2"])
        rect(d, 760, y + 24, 80, 16, c["ink2"])
    rect(d, 872, 150, 3, 832, c["line"])
    if video:
        lit(img, d, c, 1224, 180, 400, 600, 600)
    else:
        lit(img, d, c, 1144, 200, 560, 560, 650)
    d = ImageDraw.Draw(img)
    caption(d, c, 1424, 812, 520)


def carousel(img, c):
    d = ImageDraw.Draw(img)
    y, x = np.mgrid[0:H, 0:W]
    a = ((x / W) * 0.55 * (1 - (y / H) * 0.5)).clip(0, 1)
    layer = np.zeros((H, W, 4), np.uint8)
    layer[..., :3] = c["block2"]
    layer[..., 3] = (a * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(layer, "RGBA"))
    d = ImageDraw.Draw(img)
    header(d, c)
    rect(d, 96, 200, 520, 150, c["ink2"])
    for i in range(4):
        rect(d, 96 + 140 * i, 390, 110, 26, c["ink2"])
    d = lit(img, d, c, 96, 560, 720, 405, 700)
    for k in range(3):
        rect(d, 856 + 480 * k, 650, 440, 248, c["block"])


def sleeve(img, c):
    """520 Sleeve: square sleeve with the record half out of it, notes on the right, a row of small sleeves."""
    d = ImageDraw.Draw(img)
    header(d, c)
    d.ellipse([380, 160, 940, 720], fill=(20, 20, 20))
    for r in range(270, 100, -24):
        d.ellipse([660 - r, 440 - r, 660 + r, 440 + r], outline=(44, 44, 44), width=3)
    d.ellipse([564, 344, 756, 536], fill=c["block"])
    d = lit(img, d, c, 96, 160, 560, 560, 700)
    rect(d, 1010, 180, 620, 60, c["ink"])
    rect(d, 1010, 340, 420, 30, c["ink2"])
    for k in range(6):
        rect(d, 1010, 410 + k * 40, 800 - (k == 5) * 300, 18, c["ink2"])
    for k in range(10):
        x = 96 + 184 * k
        if k == 2:
            d = lit(img, d, c, x - 8, 808, 176, 176, 260)
            continue
        rect(d, x, 816, 160, 160, c["block"])


def gatefold(img, c):
    """521 Gatefold: 16:9 cards four across with a crease, the focused one lit."""
    d = ImageDraw.Draw(img)
    header(d, c)
    for r in range(3):
        for k in range(4):
            x, y = 32 + 480 * k, 158 + 300 * r
            if (r, k) == (0, 1):
                continue
            rect(d, x, y, 416, 234, c["block"])
            rect(d, x + 207, y, 2, 234, c["line"])
    d = lit(img, d, c, 32 + 480 - 10, 148, 436, 254, 520)
    rect(d, 32 + 480 + 207, 148, 2, 254, c["line"])
    caption(d, c, 960, 966)


def liner(img, c):
    """522 Liner notes: rows of picture + title + details + a line of the story; the lit picture and the story."""
    d = ImageDraw.Draw(img)
    header(d, c)
    for i in range(7):
        y = 150 + 120 * i
        if i == 2:
            rect(d, 84, y, 884, 120, c["block2"])
        rect(d, 120, y + 10, 66, 100, c["block"])
        rect(d, 210, y + 20, 360 - (i * 37) % 160, 22, c["ink"] if i == 2 else c["ink2"])
        rect(d, 210, y + 58, 220, 16, c["ink2"])
        rect(d, 210, y + 88, 640, 14, c["line"])
    d = lit(img, d, c, 1032, 150, 792, 446, 700)
    rect(d, 1032, 648, 480, 34, c["ink"])
    rect(d, 1032, 706, 360, 24, c["ink2"])
    for k in range(5):
        rect(d, 1032, 770 + k * 40, 780 - (k == 4) * 300, 18, c["ink2"])


PREVIEWS = {
    "cover_wall_music": lambda i, c: cover_wall(i, c),
    "crate_dig": crate,
    "shelf": shelf,
    "orbit": orbit,
    "list_music": lambda i, c: list_view(i, c),
    "cover_wall_video": lambda i, c: cover_wall(i, c, True),
    "backdrop_carousel": carousel,
    "list_video": lambda i, c: list_view(i, c, True),
    "sleeve": sleeve,
    "gatefold": gatefold,
    "liner_notes": liner,
}


def main():
    for room, c in ROOMS.items():
        (OUT / room).mkdir(parents=True, exist_ok=True)
        for name, fn in PREVIEWS.items():
            img = ground(c)
            fn(img, c)
            img = img.filter(ImageFilter.GaussianBlur(0.6)).resize((576, 324), Image.LANCZOS).convert("RGB")
            img.save(OUT / room / f"{name}.png", optimize=True)
    print("wrote", sum(1 for _ in OUT.rglob("*.png")), "previews to", OUT)


if __name__ == "__main__":
    main()
