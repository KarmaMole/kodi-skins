"""Add-on icon (512x512) and fanart (1920x1080) for skin.sentence, drawn in the skin's own language:
ink-green ground, Young Serif sentence, lilac phrases (underlined; the focused one a lilac block).

Usage: python skins/skin.sentence/_src/make_addon_art.py   (Pillow)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
GROUND = (15, 20, 18)
TEXT = (237, 234, 224)
MUTED = (140, 145, 139)
LILAC = (185, 166, 255)


def serif(size):
    return ImageFont.truetype(str(FONTS / "YoungSerif-Regular.ttf"), size)


def sans(size):
    return ImageFont.truetype(str(FONTS / "SentenceCaps-Bold.ttf"), size)


def glow(img, cx, cy, r, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(40, 0, -1):
        rr = r * i / 40
        a = int(alpha * (1 - i / 40) ** 1.5)
        d.ellipse([cx - rr, cy - rr * 0.6, cx + rr, cy + rr * 0.6], fill=LILAC + (a,))
    img.alpha_composite(layer)


def sentence_line(d, x, y, parts, size, pad, focused=None):
    """parts: list of (text, kind) kind = words | phrase. Returns end x."""
    f = serif(size)
    asc, desc = f.getmetrics()
    space = f.getlength(" ")
    for i, (text, kind) in enumerate(parts):
        w = f.getlength(text)
        if kind == "punct":
            x -= size * 0.12 + (pad * 1.6 - pad if focused == i - 1 else 0)
            x += 0 if focused != i - 1 else pad + 2
            d.text((x, y), text, font=f, fill=TEXT)
            x += w + space
            continue
        if kind == "phrase":
            if focused == i:
                x += pad if i > 0 else 0
                d.rounded_rectangle([x - pad - 6, y - pad * 0.4 - 6, x + w + pad + 6, y + asc + desc * 0.6 + 6], radius=pad // 2 + 6, fill=LILAC + (36,))
                d.rounded_rectangle([x - pad, y - pad * 0.4, x + w + pad, y + asc + desc * 0.6], radius=pad // 2, fill=LILAC)
                d.text((x, y), text, font=f, fill=GROUND)
                x += w + pad * 1.6 + space * 0.2
            else:
                d.text((x, y), text, font=f, fill=LILAC)
                uy = y + asc + desc * 0.55
                d.rectangle([x, uy, x + w, uy + max(2, size // 22)], fill=LILAC)
                x += w + size * 0.12
        else:
            d.text((x, y), text, font=f, fill=TEXT)
            x += w + space
    return x


def icon():
    img = Image.new("RGBA", (512, 512), GROUND + (255,))
    glow(img, 180, 160, 420, 26)
    d = ImageDraw.Draw(img)
    d.text((56, 88), "I'D LIKE", font=sans(34), fill=MUTED)
    sentence_line(d, 76, 176, [("a film", "phrase")], 104, 26, focused=0)
    sentence_line(d, 56, 330, [("tonight", "phrase")], 80, 20)
    img.convert("RGB").save(ROOT / "resources" / "icon.png", optimize=True)


def fanart():
    img = Image.new("RGBA", (1920, 1080), GROUND + (255,))
    glow(img, 560, 220, 1300, 22)
    d = ImageDraw.Draw(img)
    d.text((120, 70), "YOUR SENTENCES", font=sans(22), fill=MUTED)
    y = 190
    sentence_line(d, 120, y, [("Tonight I'd like", "words"), ("a film", "phrase")], 74, 22)
    sentence_line(d, 120, y + 150, [("that's", "words"), ("under 2 hours", "phrase"), (",", "punct"), ("funny", "phrase"), (",", "punct")], 74, 22, focused=1)
    sentence_line(d, 120, y + 300, [("from", "words"), ("the 90s", "phrase"), (",", "punct"), ("that I", "words"), ("haven't seen", "phrase"), (".", "punct")], 74, 22)
    img.convert("RGB").save(ROOT / "resources" / "fanart.jpg", quality=90)


if __name__ == "__main__":
    icon()
    fanart()
    print("icon.png + fanart.jpg written")
