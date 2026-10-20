"""Schematic view previews for the view picker (docs/requests/library-panel/BRIEF.md).

    python _src/make_view_previews.py

Writes media/noc/views/<name>.png (320x180). Every preview is drawn on the 1920x1080 design grid with the
real geometry of the view (Includes_Views_Video.xml, Includes_Views_Music.xml, Includes_Gallery.xml) and
downsampled 6x, so a viewer recognises the layout at a glance. No artwork: neutral placeholder tiles with a
little tonal variety and a hint of a title line, in the Nocturne palette; focus = the warm pool of light.
"""
from pathlib import Path
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "noc" / "views"
W, H = 1920, 1080
SIZE = (320, 180)

WALL = (24, 23, 25)
WALL_EDGE = (12, 13, 16)
LIGHT = (255, 231, 194)
BRASS = (184, 146, 79)
BRASS_LIGHT = (217, 179, 119)
LACQUER = (8, 8, 9)
TEXT = (226, 208, 180)
TEXT_DIM = (120, 110, 96)
TONES = [(62, 58, 56), (74, 68, 62), (56, 60, 64), (82, 74, 66), (66, 62, 70), (90, 82, 72), (60, 66, 62)]


def tone(i, lit=False):
    r, g, b = TONES[i % len(TONES)]
    if lit:
        return (min(255, int(r * 2.1)), min(255, int(g * 2.0)), min(255, int(b * 1.8)))
    return (r, g, b)


def ground():
    """The wall: dark plaster, a cornice band at the top and a darker floor."""
    im = Image.new("RGB", (W, H), WALL)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 150], fill=(30, 28, 28))
    d.rectangle([0, 146, W, 156], fill=(14, 14, 16))
    return im


def pool(im, cx, cy, rx, ry, strength=0.55):
    """Additive warm light pool (the torch)."""
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=int(255 * strength))
    glow = glow.filter(ImageFilter.GaussianBlur(min(rx, ry) * 0.45))
    warm = Image.new("RGB", (W, H), (140, 116, 82))
    return Image.composite(ImageChops.add(im, warm), im, glow)


def shroud(im, cx, cy, rx, ry, dark=0.55):
    """Darkness outside the light (velvet shroud)."""
    mask = Image.new("L", (W, H), int(255 * dark))
    ImageDraw.Draw(mask).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(min(rx, ry) * 0.5))
    return Image.composite(Image.new("RGB", (W, H), WALL_EDGE), im, mask)


def frame(d, x, y, w, h, i, lit=False, title=True):
    """Black lacquer frame with a gilt slip around a neutral tile (+ a title line hint)."""
    d.rectangle([x - 16, y - 16, x + w + 16, y + h + 16], fill=LACQUER)
    d.rectangle([x - 6, y - 6, x + w + 6, y + h + 6], fill=BRASS_LIGHT if lit else (110, 90, 56))
    d.rectangle([x, y, x + w, y + h], fill=tone(i, lit))
    # a lighter band in the art (sky / face) for tonal variety
    band = tuple(min(255, c + (26 if lit else 12)) for c in tone(i, lit))
    d.rectangle([x, y + int(h * 0.12), x + w, y + int(h * 0.42)], fill=band)
    if title:
        tw = int(w * (0.55 + 0.25 * ((i * 37) % 10) / 10))
        ty = y + int(h * 0.78)
        d.rounded_rectangle([x + (w - tw) // 2, ty, x + (w + tw) // 2, ty + max(10, h // 18)],
                            radius=4, fill=tuple(min(255, c + 60) for c in tone(i, lit)))


def wires(d, x, w, top, rail_y):
    d.line([x + w * 0.12, rail_y, x + w * 0.12, top - 16], fill=(70, 66, 60), width=5)
    d.line([x + w * 0.88, rail_y, x + w * 0.88, top - 16], fill=(70, 66, 60), width=5)


def rail(d, y=176):
    d.rectangle([0, y - 8, W, y + 8], fill=(96, 82, 60))


def plaque(d, cx, y, w):
    d.rounded_rectangle([cx - w // 2, y, cx + w // 2, y + 60], radius=8, fill=BRASS)
    d.rounded_rectangle([cx - w // 2 + 30, y + 20, cx + w // 2 - 120, y + 40], radius=6, fill=(70, 50, 22))


def text_line(d, x, y, w, h=18, col=TEXT_DIM):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=col)


def options_row(d, y=1030, words=(110, 220, 260, 240)):
    x = 96
    for w in words:
        text_line(d, x, y - 9, w, 18)
        x += w + 60


def crumbs(d):
    text_line(d, 96, 64, 140, 22, TEXT)
    text_line(d, 280, 64, 220, 22, TEXT_DIM)
    text_line(d, 1640, 60, 180, 30, TEXT_DIM)


def finish(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    im.resize(SIZE, Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
    print("wrote", OUT / f"{name}.png")


# ------------------------------------------------------------------ video
def corridor():
    im = ground()
    im = pool(im, 960, 520, 520, 520, 0.5)
    d = ImageDraw.Draw(im)
    rail(d)
    # slot pitch 360, list left -300, focus slot 3 (focused frame 380x541 at x 770, y 268)
    tops = [300, 318, 372, 344]
    for k in range(-2, 3):
        if k == 0:
            continue
        top = tops[(k + 2) % 4]
        w, h = (236, 350) if k % 2 else (200, 296)
        x = 780 + k * 360 + (62 if k % 2 else 80)
        wires(d, x, w, top, 176)
        frame(d, x, top, w, h, k + 3)
    wires(d, 770, 380, 268, 176)
    frame(d, 770, 268, 380, 541, 0, lit=True)
    im = shroud(im, 960, 540, 640, 560, 0.45)
    d = ImageDraw.Draw(im)
    plaque(d, 960, 850, 420)
    text_line(d, 760, 940, 400, 20)
    options_row(d)
    crumbs(d)
    return im


def salon():
    im = ground()
    d = ImageDraw.Draw(im)
    for r in range(3):
        for c in range(8):
            x = 96 + c * 216 + 24
            y = 170 + r * 340 + 18
            if y > 1000:
                continue
            frame(d, x, y, 168, min(252, 1000 - y), r * 8 + c, lit=(r == 0 and c == 2), title=False)
            if y + 290 < 1040:
                text_line(d, x + 20, y + 280, 128, 16, TEXT if (r == 0 and c == 2) else TEXT_DIM)
    im = pool(im, 96 + 2 * 216 + 108, 170 + 150, 260, 260, 0.6)
    im = shroud(im, 96 + 2 * 216 + 108, 170 + 150, 330, 330, 0.35)
    d = ImageDraw.Draw(im)
    crumbs(d)
    options_row(d)
    return im


def stills():
    im = ground()
    im = pool(im, 960, 480, 560, 420, 0.5)
    d = ImageDraw.Draw(im)
    rail(d)
    # pitch 500, list left -490, focus slot 2: focused 560x315 at x 680, y 308
    for k in (-2, -1, 1, 2):
        x = 740 + k * 500
        top = 366 if k % 2 else 398
        wires(d, x, 380, top, 176)
        frame(d, x, top, 380, 214, k + 5, title=False)
    wires(d, 680, 560, 308, 176)
    frame(d, 680, 308, 560, 315, 1, lit=True, title=False)
    d.rectangle([680, 643, 680 + 330, 649], fill=BRASS_LIGHT)
    im = shroud(im, 960, 470, 700, 430, 0.45)
    d = ImageDraw.Draw(im)
    plaque(d, 960, 680, 460)
    for k, w in enumerate((900, 960, 620)):
        text_line(d, 960 - w // 2, 790 + k * 40, w, 18)
    options_row(d)
    crumbs(d)
    return im


def list_view(music=False):
    im = ground()
    d = ImageDraw.Draw(im)
    top = 250 if music else 190
    rows = 9 if music else 12
    for r in range(rows):
        y = top + r * 66
        d.line([96, y, 1096, y], fill=(52, 48, 44), width=3)
        if r == 3:
            d.rounded_rectangle([96, y + 4, 1096, y + 62], radius=6, fill=(92, 80, 62))
            d.rectangle([96, y + 14, 104, y + 52], fill=BRASS_LIGHT)
        text_line(d, 140, y + 24, 300 + (r * 83) % 260, 18, TEXT if r == 3 else TEXT_DIM)
        text_line(d, 990, y + 24, 70, 18, TEXT_DIM)
    # the focused item lit on the wall to the right
    if music:
        im = pool(im, 1550, top + 220, 360, 330, 0.55)
        d = ImageDraw.Draw(im)
        frame(d, 1330, top, 440, 440, 2, lit=True, title=False)
        text_line(d, 1380, top + 486, 340, 26, TEXT)
        text_line(d, 1420, top + 540, 260, 18)
    else:
        im = pool(im, 1520, 520, 360, 420, 0.55)
        d = ImageDraw.Draw(im)
        frame(d, 1320, 190, 400, 600, 2, lit=True)
        text_line(d, 1360, 836, 320, 28, TEXT)
        text_line(d, 1400, 892, 240, 18)
    crumbs(d)
    if music:
        options_row(d, 208, (180, 150, 130, 140, 260, 200))
    else:
        options_row(d)
    return im


# ------------------------------------------------------------------ music
def listening_room():
    im = ground()
    d = ImageDraw.Draw(im)
    # wraplist: left -260, pitch 340, covers 300 at y 474, focus slot 3 (400 at x 760, y 424)
    for k in (-3, -2, -1, 1, 2, 3):
        x = 790 + k * 340
        d.rectangle([x, 474, x + 300, 774], fill=tone(k + 4))
        d.rectangle([x, 474 + 40, x + 300, 474 + 120], fill=tuple(c + 12 for c in tone(k + 4)))
    d.rectangle([0, 790, W, 812], fill=(70, 58, 42))       # the ledge
    im = pool(im, 960, 600, 460, 380, 0.6)
    d = ImageDraw.Draw(im)
    # lamp + cone
    d.polygon([(900, 150), (1020, 150), (1060, 230), (860, 230)], fill=(40, 34, 28))
    d.ellipse([930, 222, 990, 246], fill=LIGHT)
    d.rectangle([760, 424, 1160, 824], fill=tone(1, True))
    d.rectangle([760, 464, 1160, 584], fill=tuple(min(255, c + 24) for c in tone(1, True)))
    im = shroud(im, 960, 620, 560, 420, 0.5)
    d = ImageDraw.Draw(im)
    plaque(d, 960, 866, 420)
    crumbs(d)
    options_row(d, 208, (180, 150, 130, 140, 260, 200))
    return im


def record_bins():
    im = ground()
    d = ImageDraw.Draw(im)
    for r in range(3):
        for c in range(8):
            x = 96 + c * 216 + 18
            y = 250 + r * 300 + 14
            if y > 1040:
                continue
            lit = (r == 0 and c == 1)
            h = min(180, 1030 - y)
            d.rectangle([x, y, x + 180, y + h], fill=tone(r * 8 + c, lit))
            d.rectangle([x, y + 30, x + 180, y + 80], fill=tuple(min(255, c2 + 14) for c2 in tone(r * 8 + c, lit)))
            if y + 224 < 1040:
                text_line(d, x + 26, y + 206, 128, 16, TEXT if lit else TEXT_DIM)
    im = pool(im, 96 + 216 + 108, 250 + 120, 240, 240, 0.6)
    im = shroud(im, 96 + 216 + 108, 250 + 120, 320, 320, 0.35)
    d = ImageDraw.Draw(im)
    crumbs(d)
    options_row(d, 208, (180, 150, 130, 140, 260, 200))
    return im


if __name__ == "__main__":
    random.seed(7)
    finish(corridor(), "corridor")
    finish(salon(), "salon")
    finish(stills(), "stills")
    finish(list_view(False), "list_video")
    finish(listening_room(), "listening_room")
    finish(record_bins(), "record_bins")
    finish(list_view(True), "list_music")
