"""Generate skin.orbit icon.png (512) and fanart.jpg (1920x1080) in the Orbit language:
blue-black ground, engraved tick rings, one amber sweep, wide Archivo wordmark.

Usage: python skins/skin.orbit/_src/make_addon_art.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
FONTS = SKIN / "fonts"
SS = 3

GROUND = (7, 9, 13)
LIFT = (18, 23, 34)
LINE = (43, 50, 64)
TICK = (86, 96, 117)
TEXT = (233, 237, 243)
SECOND = (139, 149, 167)
AMBER = (255, 181, 71)


def pol(cx, cy, r, deg):
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def lift(img, cx, cy, r):
    glow = Image.new("RGB", img.size, GROUND)
    d = ImageDraw.Draw(glow)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIFT)
    glow = glow.filter(ImageFilter.GaussianBlur(r * 0.45))
    return Image.blend(img, glow, 1.0)


def dial(d, cx, cy, R, sweep, k=1.0):
    for i in range(60):
        deg = i * 6
        major = i % 5 == 0
        r0 = R - (24 if major else 12) * k
        x0, y0 = pol(cx, cy, r0, deg)
        x1, y1 = pol(cx, cy, R, deg)
        d.line([(x0, y0), (x1, y1)], fill=TICK if major else LINE, width=max(1, int(3 * k)))
    rt = R - 46 * k
    d.ellipse([cx - rt, cy - rt, cx + rt, cy + rt], outline=LINE, width=max(1, int(3 * k)))
    d.arc([cx - rt, cy - rt, cx + rt, cy + rt], -90, -90 + 360 * sweep, fill=AMBER, width=max(2, int(9 * k)))
    x0, y0 = pol(cx, cy, rt - 22 * k, 360 * sweep)
    x1, y1 = pol(cx, cy, rt + 22 * k, 360 * sweep)
    d.line([(x0, y0), (x1, y1)], fill=AMBER, width=max(2, int(5 * k)))


def icon():
    S = 512
    img = Image.new("RGB", (S * SS, S * SS), GROUND)
    img = lift(img, S * SS / 2, S * SS / 2, S * SS * 0.42)
    d = ImageDraw.Draw(img)
    c = S * SS / 2
    dial(d, c, c, S * SS * 0.44, 0.72, k=SS * 1.3)
    # lens marker at 9 o'clock and a small orbiting tile
    f = ImageFont.truetype(str(FONTS / "OrbitWide-SemiBold.ttf"), int(64 * SS))
    d.text((c, c - 6 * SS), "O", font=f, fill=TEXT, anchor="mm")
    img = img.resize((S, S), Image.LANCZOS)
    img.save(SKIN / "resources" / "icon.png", optimize=True)


def fanart():
    W, H = 1920, 1080
    img = Image.new("RGB", (W * 2, H * 2), GROUND)
    img = lift(img, 1300 * 2, 540 * 2, 760 * 2)
    d = ImageDraw.Draw(img)
    # big library arc track (centre off-screen right)
    cx, cy = 2400 * 2, 540 * 2
    for r, col, w in ((800 * 2, LINE, 3), (1300 * 2, (22, 27, 37), 3)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=w)
    for i in range(180):
        deg = 0.4 + i * 2
        major = i % 5 == 0
        x0, y0 = pol(cx, cy, (782 if major else 791) * 2, deg)
        x1, y1 = pol(cx, cy, 800 * 2, deg)
        d.line([(x0, y0), (x1, y1)], fill=TICK if major else LINE, width=3)
    d.line([(1586 * 2, 540 * 2), (1634 * 2, 540 * 2)], fill=AMBER, width=6)
    # three gauges lower left
    for i, sw in enumerate((0.76, 0.18, 0.63)):
        dial(d, (164 + i * 330) * 2, 760 * 2, 100 * 2, sw, k=1.6)
    fw = ImageFont.truetype(str(FONTS / "OrbitWide-SemiBold.ttf"), 150 * 2)
    fl = ImageFont.truetype(str(FONTS / "OrbitLabel-SemiBold.ttf"), 26 * 2)
    d.text((64 * 2, 210 * 2), "ORBIT", font=fw, fill=TEXT)
    d.text((70 * 2, 420 * 2), "BROWSE ON A DIAL", font=fl, fill=SECOND)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(SKIN / "resources" / "fanart.jpg", quality=90)


if __name__ == "__main__":
    icon()
    fanart()
    print("wrote icon.png and fanart.jpg")
