"""Schematic view previews for the view picker (docs/requests/library-panel/BRIEF.md).

    python _src/make_view_previews.py

Writes media/ks/views/<name>.png (320x180). Each preview is drawn on the 1920x1080 design grid with the view's real
geometry (Includes_Views_Video.xml, Includes_Views_Music.xml, Includes_Views.xml) and downsampled 6x. No artwork:
white-bordered prints with neutral dark placeholder photos (a little tonal variety), photo corners, and pen strokes
for the handwritten notes, on the black album paper; focus = the lifted print with its pen note.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "ks" / "views"
W, H = 1920, 1080
SIZE = (320, 180)

PAPER = (18, 17, 16)
PAPER_RAISED = (28, 26, 24)
PRINT = (244, 241, 234)
INK = (242, 239, 232)
INK_FAINT = (150, 148, 144)
LABEL = (140, 135, 128)
STAMP = (255, 106, 31)
TONES = [(70, 74, 82), (88, 80, 72), (64, 72, 70), (96, 88, 80), (78, 70, 84), (72, 84, 92), (90, 76, 70), (60, 64, 72)]


def ground():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # the album gutter: a soft darker fold at 960
    for k in range(60):
        c = max(0, PAPER[0] - (60 - k) // 12)
        d.line([960 - 60 + k, 0, 960 - 60 + k, H], fill=(c, c, c))
        d.line([960 + 60 - k, 0, 960 + 60 - k, H], fill=(c, c, c))
    return im


def pen(d, x, y, w, h=16, col=INK_FAINT):
    """A handwritten note: a slightly wavy stroke."""
    pts = [(x + i * w / 12, y + (4 if i % 2 else 0)) for i in range(13)]
    d.line(pts, fill=col, width=h // 2 + 4, joint="curve")


def label(d, x, y, w, col=LABEL):
    d.rectangle([x, y, x + w, y + 10], fill=col)


def shadow(im, box, r=26):
    m = Image.new("L", (W, H), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rectangle([x0 + 8, y0 + 14, x1 + 8, y1 + 18], fill=170)
    m = m.filter(ImageFilter.GaussianBlur(r))
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)


def photo_print(im, x, y, w, h, i, lift=False, border=14, stamp=False):
    """A white-bordered print with photo corners; the photo is a neutral placeholder."""
    im = shadow(im, (x, y, x + w, y + h), 34 if lift else 20)
    d = ImageDraw.Draw(im)
    d.rectangle([x, y, x + w, y + h], fill=PRINT)
    c = TONES[i % len(TONES)]
    if not lift:
        c = tuple(int(v * 0.8) for v in c)
    d.rectangle([x + border, y + border, x + w - border, y + h - border], fill=c)
    d.rectangle([x + border, y + border + int((h - 2 * border) * 0.18), x + w - border,
                 y + border + int((h - 2 * border) * 0.45)], fill=tuple(min(255, v + 18) for v in c))
    s = max(18, w // 9)
    for cx, cy, sx, sy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        d.polygon([(cx - 4 * sx, cy - 4 * sy), (cx + s * sx, cy - 4 * sy), (cx - 4 * sx, cy + s * sy)], fill=(22, 21, 20))
    if stamp:
        d.rectangle([x + w - border - 120, y + h - border - 38, x + w - border - 16, y + h - border - 16], fill=STAMP)
    return im


def header(d, title_w=260, pen_words=(170, 110)):
    pen(d, 112, 96, title_w, 34, INK)
    label(d, 118, 170, 260)
    x = 940 - sum(pen_words) - 30 * (len(pen_words) - 1)
    for w in pen_words:
        pen(d, x, 166, w, 18, INK_FAINT)
        x += w + 30
    d.rectangle([1716, 64, 1806, 104], fill=STAMP)
    label(d, 1508, 120, 300)
    x = 1180
    for w in (230, 150, 200):
        label(d, x, 170, w - 30, (181, 175, 166))
        x += w + 6


def finish(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    im.resize(SIZE, Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
    print("wrote", OUT / f"{name}.png")


# ------------------------------------------------------------------ video
def wall(note_lines=1):
    """521 / 522: a wall of poster prints, 6 across (pitch 302 x 420), the focused print lifted with its note."""
    im = ground()
    for r in range(2):
        for c in range(6):
            x = 52 + c * 302 + 60
            y = 176 + r * 420 + 60
            if (r, c) == (1, 1):
                continue
            im = photo_print(im, x, y, 184, 252, r * 6 + c, stamp=(c in (4, 5) and r == 0))
    im = photo_print(im, 52 + 302 + 44, 176 + 420 + 40, 216, 292, 2, lift=True, stamp=True)
    d = ImageDraw.Draw(im)
    label(d, 398, 176 + 420 + 360, 260)
    for k in range(note_lines):
        pen(d, 398, 176 + 420 + 400 + k * 46, 340 - k * 80, 22, INK)
    header(d)
    return im


def seasons():
    """523: a row of season prints under the show's title."""
    im = ground()
    for c in range(6):
        x = 52 + c * 302 + 40
        if c == 1:
            continue
        im = photo_print(im, x, 236, 224, 324, c + 3)
    im = photo_print(im, 52 + 302 + 24, 222, 256, 368, 1, lift=True)
    d = ImageDraw.Draw(im)
    label(d, 380, 640, 200)
    pen(d, 380, 680, 380, 22, INK)
    pen(d, 380, 730, 260, 18, INK_FAINT)
    header(d, 420)
    return im


def episodes():
    """524: a strip of small 16:9 prints, stamped; the focused episode written out below."""
    im = ground()
    for c in range(4):
        x = 52 + c * 404 + 40
        if c == 0:
            continue
        im = photo_print(im, x, 256, 324, 193, c + 4, stamp=True)
    im = photo_print(im, 52 + 20, 236, 364, 217, 2, lift=True, stamp=True)
    d = ImageDraw.Draw(im)
    label(d, 112, 640, 260)
    pen(d, 112, 690, 620, 30, INK)
    for k in range(3):
        d.rectangle([112, 760 + k * 40, 112 + 1200 - k * 300, 772 + k * 40], fill=(120, 118, 114))
    header(d, 420)
    return im


def list_view(music=False):
    """50: rows on the left page (tape on the focused row), the print on the right page."""
    im = ground()
    d = ImageDraw.Draw(im)
    for r in range(12):
        y = 236 + r * 64
        if r == 3:
            d.rectangle([126, y + 6, 926, y + 58], fill=(242, 234, 212))
            pen(d, 150, y + 26, 300, 18, (21, 19, 15))
            label(d, 820, y + 26, 80, (21, 19, 15))
            continue
        pen(d, 150, y + 28, 220 + (r * 67) % 260, 16, INK if r % 3 else INK_FAINT)
        label(d, 820, y + 28, 80)
    if music:
        im = photo_print(im, 1200, 236, 480, 480, 2, lift=True)
    else:
        im = photo_print(im, 1240, 236, 400, 580, 2, lift=True, stamp=True)
    d = ImageDraw.Draw(im)
    pen(d, 1200, 880, 420, 26, INK)
    label(d, 1200, 940, 300)
    header(d)
    return im


# ------------------------------------------------------------------ music
def instant_prints(square=False):
    """530 albums: instant prints (a deeper white chin); 531 artists: square prints."""
    im = ground()
    h = 234 if square else 280
    for r in range(2):
        for c in range(6):
            x = 52 + c * 302 + 60
            y = 196 + r * 400 + 50
            if (r, c) == (0, 2):
                continue
            im = photo_print(im, x, y, 234, h, r * 6 + c + 1)
            if not square:
                d = ImageDraw.Draw(im)
                d.rectangle([x + 14, y + 220, x + 220, y + 266], fill=PRINT)
    im = photo_print(im, 52 + 604 + 40, 196 + 30, 270, h + 40, 0, lift=True)
    d = ImageDraw.Draw(im)
    if not square:
        d.rectangle([52 + 604 + 54, 196 + 30 + 250, 52 + 604 + 296, 196 + 30 + h + 26], fill=PRINT)
        pen(d, 52 + 604 + 80, 196 + 30 + 280, 180, 16, (60, 56, 52))
    header(d, 190, (260, 110))
    return im


# ------------------------------------------------------------------ views added 2026-10-27
def a_page():
    """525: the big print + tucked poster on the left page, title / plot / pen line on the right, a strip below."""
    im = ground()
    im = photo_print(im, 124, 226, 728, 422, 1, lift=True, stamp=True)
    im = photo_print(im, 650, 470, 224, 309, 3, border=12)
    d = ImageDraw.Draw(im)
    label(d, 1064, 220, 200)
    d.rectangle([1060, 250, 1640, 340], fill=(239, 230, 214))
    label(d, 1066, 400, 420, (201, 194, 184))
    for k in range(4):
        d.rectangle([1066, 450 + k * 40, 1066 + 740 - (k == 3) * 300, 462 + k * 40], fill=(120, 118, 114))
    pen(d, 1064, 660, 520, 26, INK)
    for c in range(9):
        x = 52 + c * 200 + 15
        if c == 2:
            continue
        im = photo_print(im, x, 804, 170, 245, c + 2, border=10)
    im = photo_print(im, 52 + 400 + 8, 790, 184, 262, 5, lift=True, border=10)
    d = ImageDraw.Draw(im)
    header(d)
    return im


def postcards():
    """526: wide prints four across the spread, names written under them."""
    im = ground()
    for r in range(3):
        for c in range(4):
            x = 52 + c * 453 + 22
            y = 176 + r * 300 + 14
            if (r, c) == (0, 1):
                continue
            im = photo_print(im, x, y, 408, 242, r * 4 + c)
            d = ImageDraw.Draw(im)
            pen(d, x + 120, y + 266, 160, 14, INK_FAINT)
    x, y = 52 + 453 + 12, 176 + 6
    im = photo_print(im, x, y, 428, 254, 6, lift=True, stamp=True)
    d = ImageDraw.Draw(im)
    pen(d, x + 110, y + 278, 200, 16, INK)
    header(d)
    return im


def album_pages():
    """532: the cover as a big print on the left page; title, meta and the tracks on the right; instant prints below."""
    im = ground()
    im = photo_print(im, 220, 232, 492, 492, 2, lift=True, border=16)
    d = ImageDraw.Draw(im)
    d.rectangle([1060, 226, 1560, 290], fill=(239, 230, 214))
    label(d, 1066, 312, 380, (201, 194, 184))
    for k in range(10):
        y = 360 + k * 40
        label(d, 1064, y + 8, 22)
        pen(d, 1116, y + 12, 200 + (k * 53) % 300, 12, (190, 186, 180))
        label(d, 1760, y + 8, 50)
    for c in range(7):
        x = 52 + c * 262 + 14
        if c == 1:
            continue
        im = photo_print(im, x, 794, 234, 280, c + 3, border=12)
        d = ImageDraw.Draw(im)
        d.rectangle([x + 12, y + 0, x + 12, y + 0], fill=PRINT)
    im = photo_print(im, 52 + 262 + 4, 780, 254, 300, 0, lift=True, border=12)
    d = ImageDraw.Draw(im)
    header(d, 190, (260, 110))
    return im


def contact_sheet():
    """527 (0.9.15): ten small prints to a row across the spread, a year under each, the focused one lifted."""
    im = ground()
    for r in range(3):
        for c in range(10):
            x = 52 + c * 181 + 6
            y = 186 + r * 300 + 16
            if (r, c) == (0, 2):
                continue
            im = photo_print(im, x, y, 170, 245, r * 10 + c, border=10)
            d = ImageDraw.Draw(im)
            label(d, x + 60, y + 254, 50)
    x, y = 52 + 2 * 181 - 4, 186 + 4
    im = photo_print(im, x, y, 190, 268, 5, lift=True, border=10)
    d = ImageDraw.Draw(im)
    pen(d, x + 20, y + 290, 150, 16, INK)
    header(d)
    return im


def mixtape():
    """533 (0.9.15): the songs written out as a tape's track card on the right page, the cover taped on the left."""
    im = ground()
    im = photo_print(im, 220, 232, 492, 492, 4, lift=True, border=16)
    d = ImageDraw.Draw(im)
    pen(d, 300, 790, 340, 20, INK)
    label(d, 330, 846, 280, (201, 194, 184))
    for k in range(15):
        y = 214 + k * 52
        if k == 3:
            d.rectangle([1036, y + 4, 1844, y + 50], fill=(226, 206, 150))
        label(d, 1050, y + 20, 22)
        pen(d, 1106, y + 22, 180 + (k * 61) % 220, 12, (60, 50, 40) if k == 3 else (190, 186, 180))
        label(d, 1560, y + 20, 110)
        label(d, 1780, y + 20, 50)
    header(d, 190, (260, 110))
    return im


if __name__ == "__main__":
    finish(contact_sheet(), "contact_sheet")
    finish(mixtape(), "mixtape")
    finish(a_page(), "a_page")
    finish(postcards(), "postcards")
    finish(album_pages(), "album_pages")
    finish(wall(1), "prints_films")
    finish(wall(1), "prints_series")
    finish(seasons(), "seasons")
    finish(episodes(), "episodes")
    finish(list_view(False), "list_video")
    finish(instant_prints(False), "instant_prints")
    finish(instant_prints(True), "artist_prints")
    finish(list_view(True), "list_music")
