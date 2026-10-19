"""Generate the add-on artwork for skin.majan in the Index style.

  icon.png    256 x 256   black page, "Majan" wordmark (Majan Display), accent rule
  fanart.jpg  1920 x 1080 black page, big wordmark, mono caption, hairline

Pillow only, deterministic. Colours mirror colors/defaults.xml (bg, text_primary,
text_tertiary, hairline, accent = Signal).

Usage:  python skins/skin.majan/_src/make_addon_art.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
FONTS = SKIN / "fonts"

BG = (0x0B, 0x0B, 0x0B)
PRIMARY = (0xEC, 0xEB, 0xE7)
TERTIARY = (0x8D, 0x8B, 0x85)
HAIRLINE = (0x26, 0x26, 0x26)
ACCENT = (0xFF, 0x5A, 0x1F)
SS = 4  # supersampling


def display(size):
    return ImageFont.truetype(str(FONTS / "MajanDisplay-ExtraBold.ttf"), size)


def mono(size):
    return ImageFont.truetype(str(FONTS / "MajanMono-Regular.ttf"), size)


def icon():
    s = 256 * SS
    img = Image.new("RGB", (s, s), BG)
    d = ImageDraw.Draw(img)
    f = display(62 * SS)
    text = "Majan"
    w = d.textlength(text, font=f)
    x = (s - w) / 2
    y = s * 0.40
    d.text((x, y), text, font=f, fill=PRIMARY, anchor="ls")
    # accent underline (3 px at 1x) under the wordmark, like the active top-bar item
    d.rectangle([x, y + 20 * SS, x + w, y + 23 * SS], fill=ACCENT)
    m = mono(13 * SS)
    d.text((x, s * 0.80), "01 / INDEX", font=m, fill=TERTIARY, anchor="ls")
    img = img.resize((256, 256), Image.LANCZOS)
    img.save(SKIN / "icon.png", optimize=True)


def fanart():
    W, H = 1920, 1080
    img = Image.new("RGB", (W * 2, H * 2), BG)
    d = ImageDraw.Draw(img)
    k = 2
    # header rule at y=119 like every Majan screen
    d.rectangle([96 * k, 119 * k, (W - 96) * k, 120 * k - 1], fill=HAIRLINE)
    d.text((96 * k, 72 * k), "01", font=mono(14 * k), fill=ACCENT, anchor="ls")
    d.text((126 * k, 72 * k), "MAJAN / A KODI SKIN FOR OMAR", font=mono(15 * k), fill=TERTIARY, anchor="ls")
    f = display(300 * k)
    d.text((88 * k, 640 * k), "Majan", font=f, fill=PRIMARY, anchor="ls")
    w = d.textlength("Majan", font=f)
    d.rectangle([96 * k, 732 * k, 96 * k + w - 8 * k, 738 * k], fill=ACCENT)
    d.rectangle([96 * k, 960 * k, (W - 96) * k, 961 * k - 1], fill=HAIRLINE)
    d.text((96 * k, 1000 * k), "FIG. 01: MOVIES / TV SHOWS / MUSIC", font=mono(15 * k), fill=TERTIARY, anchor="ls")
    img = img.resize((W, H), Image.LANCZOS)
    img.save(SKIN / "fanart.jpg", quality=90, optimize=True)


if __name__ == "__main__":
    icon()
    fanart()
    print("wrote icon.png (256x256) and fanart.jpg (1920x1080)")
