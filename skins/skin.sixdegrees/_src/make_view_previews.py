"""Schematic view previews for the view picker (docs/requests/library-panel/BRIEF.md).

    python _src/make_view_previews.py

Writes media/sd/views/<name>.png (320x180, rounded corners). Each preview is drawn on the 1920x1080 design grid
with the view's real geometry (Includes_Views_Video.xml, Includes_Views.xml, Includes_Views_Music.xml) and
downsampled 6x. No artwork: neutral placeholder tiles with a little tonal variety and a hint of a title line, on
the map paper; focus = the ink ring, lines in the four line colours where the view draws them.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "sd" / "views"
W, H = 1920, 1080
SIZE = (320, 180)

GROUND = (244, 244, 241)
CARD = (255, 255, 255)
WASH = (234, 234, 230)
INK = (21, 22, 26)
INK2 = (107, 109, 116)
INK3 = (154, 156, 162)
HAIR = (217, 218, 214)
ROUTE = (140, 142, 148)
RED, BLUE, VIO, GRN = (232, 73, 47), (45, 91, 216), (138, 79, 214), (31, 157, 87)
TONES = [(196, 200, 207), (184, 189, 196), (209, 203, 195), (174, 181, 190), (201, 196, 205), (189, 199, 192),
         (214, 208, 199), (180, 186, 199)]


def tone(i):
    return TONES[i % len(TONES)]


def tile(d, x, y, w, h, i, focus=False, title=True, r=10):
    c = tone(i)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=c)
    band = tuple(max(0, v - 22) for v in c)
    d.rectangle([x, y + int(h * 0.55), x + w, y + int(h * 0.8)], fill=band)
    if title:
        tw = int(w * (0.5 + 0.3 * ((i * 37) % 10) / 10))
        d.rounded_rectangle([x + (w - tw) // 2, y + int(h * 0.84), x + (w + tw) // 2, y + int(h * 0.84) + max(10, h // 16)],
                            radius=5, fill=tuple(min(255, v + 34) for v in c))
    if focus:
        d.rounded_rectangle([x - 14, y - 14, x + w + 14, y + h + 14], radius=r + 10, outline=INK, width=12)


def bar(d, x, y, w, h=20, col=INK3):
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=col)


def header(d, pills=(150, 196, 226, 210, 150)):
    # wordmark + route crumbs + header pills + clock
    d.ellipse([64, 66, 108, 110], outline=INK, width=8)
    bar(d, 122, 76, 150, 26, INK)
    d.ellipse([424, 76, 448, 100], outline=INK2, width=6)
    bar(d, 456, 78, 70, 22, INK2)
    d.rectangle([530, 85, 600, 91], fill=ROUTE)
    d.ellipse([604, 70, 640, 106], outline=INK, width=9)
    bar(d, 650, 76, 110, 26, INK)
    x = 1700 - sum(pills) - 6 * (len(pills) - 1)
    for k, w in enumerate(pills):
        bar(d, x + 24, 78, w - 48, 22, INK2)
        x += w + 6
    bar(d, 1730, 70, 126, 34, INK)


def finish(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    small = im.resize(SIZE, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (SIZE[0] * 4, SIZE[1] * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE[0] * 4 - 1, SIZE[1] * 4 - 1], radius=40, fill=255)
    small.putalpha(mask.resize(SIZE, Image.LANCZOS))
    small.save(OUT / f"{name}.png", optimize=True)
    print("wrote", OUT / f"{name}.png")


def ground():
    return Image.new("RGB", (W, H), GROUND)


# ------------------------------------------------------------------ video
def line_view():
    """500 Line: hero poster + station text, the strip of posters on a grey line."""
    im = ground()
    d = ImageDraw.Draw(im)
    header(d)
    tile(d, 78, 176, 330, 495, 0, focus=True, title=False)
    bar(d, 480, 172, 520, 22, INK2)
    bar(d, 480, 214, 520, 70, INK)
    bar(d, 480, 318, 700, 26, INK)
    for k in range(3):
        bar(d, 480, 384 + k * 40, 1300 - k * 260, 20, INK3)
    d.rectangle([0, 812, W, 820], fill=ROUTE)
    for k in range(14):
        x = 54 + k * 140
        if k == 3:
            tile(d, 454, 712, 154, 222, 3, focus=True, title=False)
            continue
        if k > 3:
            x += 60
        tile(d, x, 740, 112, 166, k + 1, title=False)
    bar(d, 64, 1006, 120, 20, INK2)
    for k, w in enumerate((160, 230, 200, 160)):
        bar(d, 980 + sum((160, 230, 200, 160)[:k]) + k * 40, 1006, w, 20, INK3)
    return im


def platform():
    """501 Platform: big posters on the platform, focus slot 1, the station text below."""
    im = ground()
    d = ImageDraw.Draw(im)
    header(d)
    for k in range(6):
        x = 64 + k * 354
        tile(d, x, 160, 330, 495, k, focus=(k == 1), title=False)
    bar(d, 64, 700, 120, 18, INK3)
    bar(d, 64, 734, 150, 18, INK2)
    bar(d, 450, 700, 420, 22, INK2)
    bar(d, 450, 740, 520, 56, INK)
    bar(d, 450, 816, 640, 20, INK2)
    for k in range(2):
        bar(d, 450, 856 + k * 34, 1100 - k * 400, 18, INK3)
    return im


def wall():
    """502 Wall: Next up cards on top, a ten-column poster wall below."""
    im = ground()
    d = ImageDraw.Draw(im)
    header(d, (150, 186, 226, 210, 150))
    bar(d, 64, 158, 140, 22, INK)
    for k in range(6):
        x = 64 + k * 344
        tile(d, x, 200, 320, 180, k + 2, title=False)
        bar(d, x, 396, 220, 20, INK)
        bar(d, x, 426, 280, 16, INK2)
    d.rectangle([64, 474, 1856, 478], fill=HAIR)
    bar(d, 64, 496, 300, 22, INK)
    for r in range(2):
        for c in range(10):
            x = 96 + c * 174
            y = 540 + r * 253
            tile(d, x, y, 158, 237, r * 10 + c + 1, focus=(r == 1 and c == 5), title=False)
            d.ellipse([x + 116, y + 8, x + 150, y + 42], fill=CARD)
    return im


def episodes():
    """503 Episodes: rows with a 16:9 still, code line, title and plot."""
    im = ground()
    d = ImageDraw.Draw(im)
    header(d)
    for r in range(5):
        y = 160 + r * 174
        if r == 1:
            d.rectangle([64, y - 8, 1856, y + 166], fill=CARD)
        tile(d, 72, y + 8, 256, 144, r + 3, focus=(r == 1), title=False)
        bar(d, 384, y + 18, 260, 16, INK2)
        bar(d, 384, y + 46, 360, 24, INK)
        bar(d, 384, y + 90, 1300, 16, INK3)
        bar(d, 384, y + 118, 900, 16, INK3)
        d.rectangle([64, y + 168, 1856, y + 170], fill=HAIR)
    return im


def index_view(music=False):
    """50 Index: a line of station dots with the titles, the focused one in an ink pill; poster + text right."""
    im = ground()
    d = ImageDraw.Draw(im)
    header(d)
    d.rectangle([138, 168, 150, 1040], fill=(200, 201, 204))
    for r in range(13):
        y = 203 + r * 66
        if r == 8:
            d.rounded_rectangle([64, y - 28, 1184, y + 28], radius=28, fill=INK)
            d.ellipse([128, y - 16, 160, y + 16], fill=CARD)
            d.ellipse([137, y - 7, 151, y + 7], fill=INK)
            bar(d, 180, y - 11, 320, 22, CARD)
            bar(d, 1100, y - 10, 50, 20, CARD)
            continue
        d.ellipse([130, y - 14, 158, y + 14], fill=CARD, outline=INK if r in (3, 10) else INK3, width=7)
        bar(d, 180, y - 11, 220 + (r * 71) % 260, 22, INK)
        bar(d, 1100, y - 10, 50, 20, INK2)
    d.rectangle([1204, 170, 1206, 1028], fill=HAIR)
    if music:
        tile(d, 1264, 170, 400, 400, 2, focus=True, title=False)
        bar(d, 1264, 610, 360, 30, INK)
        bar(d, 1264, 656, 420, 20, INK2)
    else:
        tile(d, 1264, 170, 300, 450, 2, focus=True, title=False)
        bar(d, 1264, 666, 220, 30, INK)
        bar(d, 1264, 710, 460, 20, INK2)
        for k in range(3):
            bar(d, 1264, 760 + k * 34, 580 - k * 140, 18, INK3)
    return im


# ------------------------------------------------------------------ music
def music_header(d):
    d.ellipse([64, 66, 108, 110], outline=INK, width=8)
    bar(d, 122, 76, 150, 26, INK)
    x = 1530 - 700
    for w in (120, 120, 100, 110, 150, 40):
        bar(d, x + 14, 78, w - 28, 22, INK2)
        x += w + 12
    bar(d, 1730, 70, 126, 34, INK)


def grid():
    """504 Grid: a panel of album squares, titles under them."""
    im = ground()
    d = ImageDraw.Draw(im)
    music_header(d)
    for r in range(3):
        for c in range(8):
            x = 96 + c * 220
            y = 160 + r * 300
            if y > 1000:
                continue
            tile(d, x, y, 196, 196, r * 8 + c, focus=(r == 0 and c == 1), title=False, r=8)
            bar(d, x + 20, y + 214, 156, 18, INK)
            bar(d, x + 40, y + 242, 116, 14, INK2)
    return im


def big_album():
    """505 Big album: one big cover in front, the next covers beside it, the album text."""
    im = ground()
    d = ImageDraw.Draw(im)
    music_header(d)
    tile(d, 96, 170, 560, 560, 0, focus=True, title=False, r=12)
    for k in range(5):
        tile(d, 720 + k * 236, 470, 212, 212, k + 1, title=False, r=8)
    bar(d, 96, 790, 760, 54, INK)
    bar(d, 96, 864, 520, 24, INK2)
    for k in range(2):
        bar(d, 96, 912 + k * 34, 1100 - k * 300, 18, INK3)
    return im


if __name__ == "__main__":
    finish(line_view(), "line")
    finish(platform(), "platform")
    finish(wall(), "wall")
    finish(episodes(), "episodes")
    finish(index_view(False), "index_video")
    finish(grid(), "grid")
    finish(big_album(), "big_album")
    finish(index_view(True), "index_music")
