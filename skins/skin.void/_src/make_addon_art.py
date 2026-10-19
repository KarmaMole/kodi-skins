"""Generate the add-on artwork for skin.void (Pillow, deterministic).

  icon.png    256 x 256    true black, "Void" in Instrument Serif, warm white
  fanart.jpg  1920 x 1080  true black, the Home composition: caps label, faint neighbours,
                           the word "Void" at 172 px on the x=160 axis, a meta line

Usage:  python skins/skin.void/_src/make_addon_art.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
FONTS = SKIN / "fonts"

BG = (0, 0, 0)
TEXT = (0xF2, 0xF2, 0xF0)
GREY = (0x8A, 0x8A, 0x88)
FAINT = (0x44, 0x44, 0x43)   # 28% of the text colour on black
SEP = (0x3A, 0x3A, 0x38)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def icon():
    k = 4
    s = 256 * k
    img = Image.new("RGB", (s, s), BG)
    d = ImageDraw.Draw(img)
    f = font("VoidSerifDisplay-Regular.ttf", 112 * k)
    w = d.textlength("Void", font=f)
    d.text(((s - w) / 2, s * 0.62), "Void", font=f, fill=TEXT, anchor="ls")
    c = font("VoidCaps-Medium.ttf", 13 * k)
    t = "ONE THING AT A TIME"
    w2 = d.textlength(t, font=c)
    d.text(((s - w2) / 2, s * 0.80), t, font=c, fill=GREY, anchor="ls")
    img.resize((256, 256), Image.LANCZOS).save(SKIN / "icon.png", optimize=True)


def fanart():
    k = 2
    W, H = 1920, 1080
    img = Image.new("RGB", (W * k, H * k), BG)
    d = ImageDraw.Draw(img)
    caps = font("VoidCaps-Medium.ttf", 20 * k)
    d.text((160 * k, 106 * k), "A KODI SKIN FOR OMAR", font=caps, fill=GREY, anchor="ls")
    for i in range(7):
        r = (4 if i == 0 else 3) * k
        cx = (164 + i * 22) * k
        d.ellipse([cx - r, 134 * k - r, cx + r, 134 * k + r], fill=TEXT if i == 0 else SEP)
    serif48 = font("VoidSerif-Regular.ttf", 48 * k)
    d.text((160 * k, 311 * k), "Quiet", font=serif48, fill=FAINT, anchor="ls")
    capsw = font("VoidCapsWide-Medium.ttf", 20 * k)
    d.text((164 * k, 418 * k), "2026", font=capsw, fill=GREY, anchor="ls")
    disp = font("VoidSerifDisplay-Regular.ttf", 172 * k)
    d.text((152 * k, 576 * k), "Void", font=disp, fill=TEXT, anchor="ls")
    sans = font("VoidSans-Regular.ttf", 26 * k)
    d.text((160 * k, 663 * k), "One thing at a time  ·  information arrives the longer you rest",
           font=sans, fill=GREY, anchor="ls")
    d.text((160 * k, 809 * k), "Dark", font=serif48, fill=FAINT, anchor="ls")
    img.resize((W, H), Image.LANCZOS).save(SKIN / "fanart.jpg", quality=90, optimize=True)


if __name__ == "__main__":
    icon()
    fanart()
    print("wrote icon.png (256x256) and fanart.jpg (1920x1080)")
