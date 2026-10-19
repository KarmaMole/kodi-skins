"""Add-on icon (512) and fanart (1920x1080) for skin.passepartout, in the skin's own language:
art-coloured paper, matted prints on a hanging line, a museum caption in Geist.

Usage:  python skins/skin.passepartout/_src/make_addon_art.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONTS = ROOT / "fonts"
INK = (0x1C, 0x1B, 0x19)
INK2 = (0x6E, 0x6A, 0x63)


def mat(img, box, fill, shadow=True):
    """Draw a matted print: lift shadow, picture, 3px bevel, 1px hairline, ring."""
    x0, y0, x1, y1 = box
    if shadow:
        sh = Image.new("L", img.size, 0)
        d = ImageDraw.Draw(sh)
        d.rectangle((x0 + 18, y0 + 40, x1 - 18, y1 + 30), fill=110)
        sh = sh.filter(ImageFilter.GaussianBlur(26))
        dark = Image.new("RGB", img.size, tuple(int(c * 0.35) for c in img.getpixel((2, 2))[:3]))
        img.paste(dark, (0, 0), sh)
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 5, y0 - 5, x1 + 4, y1 + 4), outline=(0xD8, 0xD3, 0xCC))
    d.rectangle((x0 - 4, y0 - 4, x1 + 3, y1 + 3), fill=(0xFF, 0xFF, 0xFF))
    d.rectangle((x0 - 1, y0 - 4, x1 + 3, y1 + 3), fill=(0xF2, 0xF0, 0xEC))
    d.rectangle((x0 - 4, y1 + 1, x1 + 3, y1 + 3), fill=(0xE6, 0xE3, 0xDE))
    d.rectangle((x0 - 4, y0 - 4, x1 + 3, y0 - 2), fill=(0xFF, 0xFF, 0xFF))
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=(0xB0, 0xAB, 0xA4))
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=fill)
    # inner shadow at the top edge
    for i in range(6):
        a = int(70 * (1 - i / 6))
        ov = Image.new("RGBA", (x1 - x0, 1), (18, 16, 14, a))
        img.paste(ov, (x0, y0 + i), ov)


def gradient_print(w, h, top, bottom):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line((0, y, w, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g


def icon():
    img = Image.new("RGB", (512, 512), (0xEE, 0xDF, 0xDB))
    box = (126, 92, 386, 382)
    mat(img, box, (0, 0, 0))
    img.paste(gradient_print(260, 290, (0x3A, 0x2C, 0x3C), (0xC9, 0x7B, 0x6E)), (126, 92))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(str(FONTS / "PPCaps-Medium.ttf"), 22)
    t = "PASSE-PARTOUT"
    d.text(((512 - d.textlength(t, font=f)) / 2, 420), t, font=f, fill=INK)
    img.save(ROOT / "icon.png", optimize=True)


def fanart():
    img = Image.new("RGB", (1920, 1080), (0xD9, 0xE1, 0xDF))
    prints = [(-56, 308, 216, 324, ((0x2A, 0x3A, 0x40), (0x8A, 0xA6, 0xA8))),
              (232, 308, 216, 324, ((0x40, 0x30, 0x28), (0xB0, 0x90, 0x70))),
              (520, 170, 400, 600, ((0x1E, 0x33, 0x3A), (0x9C, 0xC0, 0xBE))),
              (992, 308, 216, 324, ((0x3A, 0x2A, 0x2A), (0xC8, 0xA0, 0x8C))),
              (1280, 308, 216, 324, ((0x22, 0x22, 0x2C), (0x80, 0x84, 0x9C))),
              (1568, 308, 216, 324, ((0x34, 0x3A, 0x22), (0xB4, 0xB8, 0x84))),
              (1856, 308, 216, 324, ((0x3C, 0x2C, 0x3A), (0xA8, 0x8C, 0xB0)))]
    for x, y, w, h, (a, b) in prints:
        mat(img, (x, y, x + w, y + h), (0, 0, 0), shadow=(w == 400))
        img.paste(gradient_print(w, h, a, b), (x, y))
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(str(FONTS / "PPTitle-Light.ttf"), 72)
    f2 = ImageFont.truetype(str(FONTS / "PPCaps-Medium.ttf"), 20)
    d.text((520, 806), "Passe-partout", font=f1, fill=INK)
    d.text((520, 908), "EVERY FILM, FRAMED · KODI 21 · NVIDIA SHIELD", font=f2, fill=INK2)
    img.save(ROOT / "fanart.jpg", quality=90)


if __name__ == "__main__":
    icon()
    fanart()
    print("icon.png + fanart.jpg written")
