"""Duotone add-on art: icon.png (512) and fanart.jpg (1920x1080), in the skin's language.
Four section fields in a strict grid, Anton type, halftone dots, an 8px ink frame. No gradients.
Usage: python skins/skin.duotone/_src/make_addon_art.py
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ANTON = str(ROOT / "fonts" / "Anton-Regular.ttf")
CAPS = str(ROOT / "fonts" / "DuotoneCaps-Bold.ttf")
V, C, A, P, K = (255, 77, 46), (46, 91, 255), (198, 244, 50), (241, 237, 228), (17, 17, 17)


def dots(im, pitch=8, r=1.6, alpha=30):
    d = ImageDraw.Draw(im, "RGBA")
    for y in range(pitch // 2, im.height, pitch):
        for x in range(pitch // 2, im.width, pitch):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(17, 17, 17, alpha))


def icon():
    s = 512
    im = Image.new("RGB", (s, s), V)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 352, 170, 512], fill=C)
    d.rectangle([170, 352, 341, 512], fill=A)
    d.rectangle([341, 352, 512, 512], fill=P)
    dots(im)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(ANTON, 300)
    d.text((40, 352), "DT", font=f, fill=K, anchor="ls")
    d.rectangle([0, 344, 512, 352], fill=K)
    d.rectangle([170, 352, 178, 512], fill=K)
    d.rectangle([341, 352, 349, 512], fill=K)
    for i in range(16):
        d.rectangle([i, i, s - 1 - i, s - 1 - i], outline=K)
    im.save(ROOT / "resources" / "icon.png", optimize=True)


def fanart():
    w, h = 1920, 1080
    im = Image.new("RGB", (w, h), V)
    d = ImageDraw.Draw(im)
    d.rectangle([1120, 0, w, 540], fill=C)
    d.rectangle([1120, 540, 1520, h], fill=A)
    d.rectangle([1520, 540, w, h], fill=P)
    dots(im)
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(ANTON, 330)
    d.text((56, 470), "DUO", font=big, fill=K, anchor="ls")
    d.text((56, 900), "TONE", font=big, fill=K, anchor="ls")
    d.rectangle([64, 160, 1056, 168], fill=K)
    d.rectangle([1112, 0, 1120, h], fill=K)
    d.rectangle([1120, 532, w, 540], fill=K)
    d.rectangle([1512, 540, 1520, h], fill=K)
    cap = ImageFont.truetype(CAPS, 24)
    d.text((64, 80), "FILMS  ·  SERIES  ·  MUSIC  ·  SEARCH", font=cap, fill=K)
    d.text((64, 1000), "EVERY PICTURE IN ITS SECTION'S COLOUR", font=cap, fill=K)
    im.save(ROOT / "resources" / "fanart.jpg", quality=90)


if __name__ == "__main__":
    icon(); fanart(); print("icon.png + fanart.jpg written")
