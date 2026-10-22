"""Fold add-on art: icon.png (512) and fanart.jpg (1920x1080).  python skins/skin.fold/_src/make_addon_art.py
A vermilion card swinging open on its hinge over a cream spread, on the table; the section colours as die-cut tabs.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TABLE = (0xE9, 0xE7, 0xE2)
CREAM = (0xF6, 0xF1, 0xE7)
VERM = (0xD9, 0x45, 0x2B)
COLS = [(0xD9, 0x45, 0x2B), (0x23, 0x47, 0xA8), (0xE7, 0xA4, 0x2B), (0x1E, 0x8A, 0x6A), (0x3A, 0x3A, 0x3C)]
INK = (0x1D, 0x1B, 0x18)
SS = 3


def project(x, y, z, cx, cy, d=1080):
    s = d / (d + z)
    return cx + (x - cx) * s, cy + (y - cy) * s


def card_quad(hx, top, h, w, angle_deg, cx, cy, direction=1):
    """A panel hinged at x = hx, turned by angle (deg, positive = free edge toward the viewer)."""
    a = np.deg2rad(angle_deg)
    fx = hx + direction * w * np.cos(a)
    fz = -w * np.sin(a)
    return [project(hx, top, 0, cx, cy), project(fx, top, fz, cx, cy), project(fx, top + h, fz, cx, cy), project(hx, top + h, 0, cx, cy)]


def shadow(img, poly, offset, blur, alpha):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([(x + offset[0], y + offset[1]) for x, y in poly], fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    dark = Image.new("RGB", img.size, (70, 40, 20))
    img.paste(dark, (0, 0), m)


def scene(W, H, scale, tabs=True, title=True, dx=0):
    img = Image.open(ROOT / "media" / "fold" / "table.jpg").convert("RGB").resize((W, H), Image.LANCZOS)
    S = scale
    cx, cy = W / 2 + dx, H / 2
    pw, ph = 300 * S, 420 * S
    hinge = cx - pw * 0.15
    top = cy - ph / 2 + 30 * S
    # the open spread (p2 flat, p3 at +8, p1 landed)
    p2 = [(hinge, top), (hinge + pw, top), (hinge + pw, top + ph), (hinge, top + ph)]
    p3 = card_quad(hinge + pw, top, ph, pw * 0.7, 18, cx, cy)
    shadow(img, p2 + p3[1:3], (14 * S, 22 * S), 22 * S, .28)
    d = ImageDraw.Draw(img)
    d.polygon(p2, fill=CREAM)
    d.polygon(p3, fill=(0xEF, 0xE8, 0xDB))
    d.line([p2[1], p2[2]], fill=(0xD9, 0xD1, 0xC1), width=max(1, int(2 * S)))
    # printed lines on the spread
    for i in range(6):
        y = top + (110 + i * 34) * S
        d.line([(hinge + 30 * S, y), (hinge + (230 - (i % 3) * 40) * S, y)], fill=(0xC9, 0xC0, 0xB0), width=max(1, int(8 * S)))
    d.rectangle([hinge + 30 * S, top + 40 * S, hinge + 200 * S, top + 80 * S], fill=INK)
    # the cover rising at +60 on the left hinge (free edge toward the viewer)
    cov = card_quad(hinge, top, ph, pw, 118, cx, cy)
    shadow(img, cov, (-30 * S, 20 * S), 30 * S, .30)
    d = ImageDraw.Draw(img)
    d.polygon(cov, fill=VERM)
    # inset plate on the cover
    inset = card_quad(hinge, top + 26 * S, ph - 90 * S, pw - 30 * S, 118, cx, cy)
    d.polygon(inset, fill=(0xF6, 0xD9, 0xCF))
    d.line([cov[0], cov[3]], fill=(0xB8, 0x36, 0x20), width=max(1, int(3 * S)))
    if tabs:
        tw, th = 120 * S, 42 * S
        x0 = W / 2 - (len(COLS) * (tw + 8 * S)) / 2
        for i, c in enumerate(COLS):
            x = x0 + i * (tw + 8 * S)
            h = th * (1.5 if i == 0 else 1)
            d.rounded_rectangle([x, -20 * S, x + tw, h], radius=int(10 * S), fill=c)
    if title:
        f = ImageFont.truetype(str(ROOT / "fonts" / "FoldDisplay-ExtraBold.ttf"), int(150 * S))
        tx = 140 * S
        d.text((tx, H - 260 * S), "Fold", font=f, fill=INK)
        f2 = ImageFont.truetype(str(ROOT / "fonts" / "FoldCaps-Regular.ttf"), int(30 * S))
        d.text((tx + 8 * S, H - 90 * S), "everything unfolds", font=f2, fill=(0x5B, 0x57, 0x50))
    return img


def main():
    fan = scene(1920, 1080, 1.45, dx=300)
    fan.save(ROOT / "resources" / "fanart.jpg", quality=90)
    icon = scene(512, 512, 0.52, tabs=True, title=False, dx=-40)
    icon.save(ROOT / "resources" / "icon.png")
    print("icon.png, fanart.jpg")


if __name__ == "__main__":
    main()
