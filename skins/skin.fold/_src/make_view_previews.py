"""Schematic view previews for the view picker (Custom_1156_ViewPicker.xml).

    python skins/skin.fold/_src/make_view_previews.py

Writes media/fold/views/<view>.png (320 x 180). Each preview is drawn at the view's real 1920 x 1080 geometry
(fold_geo.py, make_views.py, make_music_views.py, Includes_Views.xml) in Fold's palette - the light table, the
die-cut tabs, coloured closed cards with cream plates, the cream list sheet - then scaled down. No artwork: the
plates are neutral grey blocks with a hint of a title line. The shelf comes in the Films and the Series colour.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw
from fold_geo import (SHELF_X, SHELF_Y, SHELF_SLOT_W, SHELF_SLOT_H, SHELF_PAD_X, SHELF_PAD_Y,
                      SHELF_CARD_W, SHELF_CARD_H, SHELF_COLS)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "fold" / "views"
W, H = 1920, 1080
SIZE = (320, 180)
TABLE = (233, 231, 226)
CREAM = (246, 241, 231)
INK = (29, 27, 24)
INK2 = (58, 54, 47)
CAP = (91, 87, 80)
RULE = (205, 201, 194)
SHADOW = (205, 199, 188)
VERM, COBALT, MARI, JADE, GRAPH = (217, 69, 43), (35, 71, 168), (231, 164, 43), (30, 138, 106), (58, 58, 60)
PLATES = [(120, 116, 108), (146, 140, 130), (104, 100, 96), (160, 154, 142), (132, 128, 120), (112, 110, 104)]


def canvas():
    im = Image.new("RGB", (W, H), TABLE)
    return im, ImageDraw.Draw(im)


def bar(d, x, y, w, h, c):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def tabs(d, active):
    for i, c in enumerate((VERM, COBALT, MARI, JADE, GRAPH)):
        x = 96 + i * 206
        h = 98 if i == active else 66
        d.rounded_rectangle([x, -20, x + 196, h], radius=16, fill=c)
        bar(d, x + 24, h - 40, 90, 16, CREAM if i != 2 else INK)
    bar(d, 1700, 36, 124, 30, INK)               # clock
    bar(d, 1684, 86, 140, 14, CAP)


def words(d, accent, x0=930):
    bar(d, 96, 126, 110, 16, accent)              # row head
    bar(d, 236, 126, 60, 16, CAP)
    x = x0
    for w in (112, 182, 150, 98, 126, 24):
        bar(d, x + 12, 126, w, 16, INK2)
        x += w + 30


def card(d, x, y, w, h, color, i, plate=True, shadow=True):
    if shadow:
        d.rounded_rectangle([x + 6, y + 10, x + w + 6, y + h + 12], radius=6, fill=SHADOW)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=color)
    if plate:
        pl, pt = int(w * 0.08), int(h * 0.045)
        pw, ph = w - 2 * pl, int((w - 2 * pl) * 1.5)
        bar(d, x + pl, y + pt, pw, min(ph, h - pt - 40), PLATES[i % len(PLATES)])
        bar(d, x + pl, y + h - 30, 60, 12, CREAM)
        bar(d, x + w - pl - 40, y + h - 30, 40, 12, CREAM)


def label_column(d, accent, x=1452, top=176):
    bar(d, x, top + 12, 200, 16, accent)
    bar(d, x, top + 56, 320, 40, INK)
    bar(d, x, top + 104, 220, 40, INK)
    bar(d, x, top + 170, 260, 14, CAP)
    bar(d, x, top + 200, 300, 14, CAP)
    for k in range(4):
        bar(d, x, top + 240 + k * 34, 350 - (k == 3) * 150, 16, INK2)


def save(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    im.resize(SIZE, Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
    print("wrote", OUT / f"{name}.png")


def shelf(name, color, active):
    im, d = canvas()
    tabs(d, active)
    words(d, color)
    i = 0
    for r in range(2):
        for c in range(SHELF_COLS):
            x = SHELF_X + c * SHELF_SLOT_W + SHELF_PAD_X
            y = SHELF_Y + r * SHELF_SLOT_H + SHELF_PAD_Y
            if (r, c) == (0, 1):                  # the lifted card
                card(d, x - 12, y - 36, SHELF_CARD_W + 24, SHELF_CARD_H + 36, color, i)
            else:
                card(d, x, y, SHELF_CARD_W, SHELF_CARD_H, color, i)
            i += 1
    label_column(d, color)
    save(im, name)


def show_card(d):
    card(d, 96, 166, 300, 452, COBALT, 2)
    d.rounded_rectangle([206, 140, 396, 192], radius=8, fill=COBALT)   # die-cut season tab
    bar(d, 96, 680, 240, 14, CAP)
    bar(d, 96, 712, 200, 14, CAP)
    for k in range(10):
        bar(d, 96 + k * 30, 752, 22, 22, COBALT if k < 6 else RULE)


def seasons():
    im, d = canvas()
    tabs(d, 1)
    words(d, COBALT)
    show_card(d)
    bar(d, 440, 150, 260, 16, COBALT)
    for c in range(5):
        x = 400 + c * SHELF_SLOT_W + SHELF_PAD_X
        y = SHELF_Y + 40 + SHELF_PAD_Y
        if c == 0:
            card(d, x - 12, y - 36, SHELF_CARD_W + 24, SHELF_CARD_H + 36, COBALT, c)
        else:
            card(d, x, y, SHELF_CARD_W, SHELF_CARD_H, COBALT, c)
    bar(d, 440, 700, 520, 50, INK)
    bar(d, 440, 770, 300, 14, CAP)
    for k in range(3):
        bar(d, 440, 816 + k * 37, 1000 - (k == 2) * 400, 16, INK2)
    save(im, "seasons")


def strip():
    im, d = canvas()
    tabs(d, 1)
    bar(d, 96, 126, 420, 16, COBALT)              # crumb
    words(d, COBALT)
    show_card(d)
    x = 436
    for k in range(8):
        w = 227 if k == 2 else 192
        top, h = (206 - 30, 468 + 60) if k == 2 else (206, 468)
        tilt = 0 if k == 2 else (14 if k % 2 else -14)
        if x > 1920:
            break
        col = CREAM if k == 2 else (CREAM if k % 2 else (236, 229, 216))
        poly = [(x, top + max(tilt, 0)), (x + w, top + max(-tilt, 0)), (x + w, top + h - max(-tilt, 0)), (x, top + h - max(tilt, 0))]
        d.polygon(poly, fill=col, outline=RULE)
        bar(d, x + 16, top + 30, w - 32, int((w - 32) * 0.56), PLATES[k % len(PLATES)])
        bar(d, x + 16, top + 180, w - 70, 16, INK if k == 2 else INK2)
        for j in range(4):
            bar(d, x + 16, top + 220 + j * 26, w - 40 - (j == 3) * 50, 10, CAP)
        if k == 2:
            bar(d, x, top + h - 8, w, 8, COBALT)
        x += w
    bar(d, 436, 668, 1484, 6, (200, 194, 184))     # contact line
    bar(d, 440, 742, 760, 50, INK)
    for k in range(3):
        bar(d, 440, 818 + k * 37, 1040 - (k == 2) * 400, 16, INK2)
    bar(d, 440, 938, 520, 14, CAP)
    save(im, "strip")


def sleeves():
    im, d = canvas()
    tabs(d, 2)
    words(d, (168, 108, 12), x0=640)
    i = 0
    for r in range(3):
        for c in range(5):
            x, y = 56 + c * 268 + 40, 176 + r * 300 + 18
            if (r, c) == (0, 2):
                card(d, x - 12, y - 28, 252, 296, MARI, i, plate=False)
                bar(d, x + 6, y - 10, 216, 216, PLATES[i % 6])
            else:
                card(d, x, y, 228, 268, MARI, i, plate=False)
                bar(d, x + 18, y + 18, 192, 192, PLATES[i % 6])
            bar(d, x + 18, y + 236, 60, 12, INK)
            i += 1
    label_column(d, (168, 108, 12))
    save(im, "sleeves")


def list_view(name, accent, active, square):
    im, d = canvas()
    tabs(d, active)
    words(d, accent)
    d.rounded_rectangle([72, 156, 1232, 1044], radius=6, fill=CREAM)
    for r in range(13):
        y = 170 + r * 66
        if y + 66 > 1030:
            break
        if r == 2:                                 # the lifted slip with its accent bar
            d.rounded_rectangle([90, y + 6, 1186, y + 72], radius=4, fill=SHADOW)
            d.rounded_rectangle([96, y, 1180, y + 66], radius=4, fill=(255, 252, 246))
            bar(d, 96, y, 6, 66, accent)
            bar(d, 124, y + 24, 420, 18, INK)
        else:
            bar(d, 124, y + 24, 260 + (r * 113) % 380, 18, INK2)
            bar(d, 96, y + 65, 1084, 2, RULE)
        bar(d, 1000, y + 26, 140, 14, CAP)
    bar(d, 1204, 176, 4, 846, RULE)
    bar(d, 1204, 260, 4, 140, CAP)
    if square:
        bar(d, 1296, 170, 528, 528, PLATES[3])
    else:
        bar(d, 1296, 170, 373, 560, PLATES[3])
    bar(d, 1296, 760, 420, 44, INK)
    bar(d, 1296, 830, 300, 14, accent)
    for k in range(4):
        bar(d, 1296, 872 + k * 34, 500 - (k == 3) * 200, 14, INK2)
    save(im, name)


# ---------------------------------------------------------------- 0.9.13 views (fold_views_more.py / fold_music_more.py)
def table(name, color, active, w=168, h=252, slot=(222, 288), top=150, square=False):
    im, d = canvas()
    tabs(d, active)
    words(d, color if color != MARI else (168, 108, 12), x0=640 if square else 930)
    bar(d, 236, 126, 300, 16, INK)                 # the crumb names the focused card
    i = 0
    for r in range(4):
        for c in range(8):
            x = 56 + c * slot[0] + 27
            y = top + r * slot[1] + 18
            if y > 1040:
                continue
            hh = min(h, 1080 - y)
            if (r, c) == (0, 2):
                card(d, x - 9, y - 27, w + 18, h + 27, color, i, plate=not square)
                if square:
                    bar(d, x + 7, y - 12, w - 14 + 18 - 14, w - 14 + 18 - 14, PLATES[i % 6])
            else:
                card(d, x, y, w, hh, color, i, plate=not square)
                if square:
                    bar(d, x + 14, y + 14, w - 28, w - 28, PLATES[i % 6])
            i += 1
    save(im, name)


def leaflet():
    im, d = canvas()
    tabs(d, 0)
    words(d, VERM)
    top, h, w = 160, 540, 552
    d.rounded_rectangle([132 + 10, top + 14, 132 + 3 * w + 10, top + h + 18], radius=6, fill=SHADOW)
    # outer panels turned toward you: drawn a little taller at their outer edge
    d.polygon([(132, top - 14), (132 + w, top), (132 + w, top + h), (132, top + h + 14)], fill=CREAM, outline=RULE)
    d.rectangle([132 + w, top, 132 + 2 * w, top + h], fill=(250, 246, 238), outline=RULE)
    d.polygon([(132 + 2 * w, top), (132 + 3 * w, top - 14), (132 + 3 * w, top + h + 14), (132 + 2 * w, top + h)], fill=CREAM, outline=RULE)
    bar(d, 184, top + 44, 300, 450, PLATES[2])
    x2 = 132 + w + 40
    bar(d, x2, top + 44, 220, 16, VERM)
    bar(d, x2, top + 80, 420, 48, INK)
    bar(d, x2, top + 136, 300, 48, INK)
    bar(d, x2, top + 210, 360, 14, CAP)
    for k in range(5):
        bar(d, x2, top + 260 + k * 34, 460 - (k == 4) * 200, 16, INK2)
    x3 = 132 + 2 * w + 36
    bar(d, x3, top + 44, 480, 270, PLATES[4])
    for k in range(3):
        bar(d, x3 + 4, top + 352 + k * 40, 340 - k * 60, 14, CAP)
    for k in range(11):
        x = 96 + 16 + k * 160
        if x > 1880:
            break
        if k == 1:
            card(d, x - 7, 790 - 21, 142, 213, VERM, k)
            bar(d, x - 7, 790 + 192 + 2, 142, 6, VERM)
        else:
            card(d, x, 790, 128, 192, VERM, k)
    save(im, "leaflet")


def prints():
    im, d = canvas()
    tabs(d, 1)
    words(d, COBALT)
    i = 0
    for r in range(3):
        for c in range(4):
            x, y = 52 + c * 444 + 16, 150 + r * 352 + 18
            if y > 1040:
                continue
            col = COBALT if (r + c) % 3 else VERM
            ww, hh = (436, 334) if (r, c) == (0, 1) else (412, 316)
            if (r, c) == (0, 1):
                x, y = x - 12, y - 18
            hh = min(hh, 1080 - y)
            d.rounded_rectangle([x + 6, y + 10, x + ww + 6, y + hh + 12], radius=6, fill=SHADOW)
            d.rounded_rectangle([x, y, x + ww, y + hh], radius=6, fill=col)
            pw = ww - 32
            bar(d, x + 18, y + 16, pw, min(int(pw * 9 / 16), hh - 20), PLATES[i % 6])
            if y + 16 + int(pw * 9 / 16) + 60 < 1080:
                bar(d, x + 18, y + 16 + int(pw * 9 / 16) + 18, 240, 18, CREAM)
                bar(d, x + 18, y + 16 + int(pw * 9 / 16) + 50, 160, 12, CREAM)
            i += 1
    save(im, "prints")


def poster():
    im, d = canvas()
    tabs(d, 2)
    words(d, (168, 108, 12), x0=640)
    x, y, w, h = 96, 164, 1240, 540
    d.rounded_rectangle([x + 10, y + 14, x + w + 10, y + h + 18], radius=6, fill=SHADOW)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=CREAM)
    bar(d, x + 14, y + 14, w - 28, h - 28, PLATES[1])
    bar(d, x + w // 2 - 2, y, 4, h, (220, 214, 204))
    bar(d, x, y + h // 2 - 2, w, 4, (220, 214, 204))
    cx = 1400
    bar(d, cx, y + 12, 220, 16, (168, 108, 12))
    bar(d, cx, y + 50, 380, 46, INK)
    bar(d, cx, y + 120, 260, 14, CAP)
    for k in range(7):
        bar(d, cx, y + 160 + k * 34, 400 - (k == 6) * 180, 16, INK2)
    for k in range(10):
        sx = 96 + 18 + k * 186
        if sx > 1880:
            break
        if k == 1:
            card(d, sx - 7, 794 - 17, 162, 197, MARI, k, plate=False)
            bar(d, sx + 7, 794 - 3, 134, 134, PLATES[k % 6])
        else:
            card(d, sx, 794, 148, 180, MARI, k, plate=False)
            bar(d, sx + 12, 806, 124, 124, PLATES[k % 6])
    save(im, "poster")


def accordion():
    """0.9.16 Accordion 509: the concertina of posters from the left margin, the title / story / facts below."""
    im, d = canvas()
    tabs(d, 0)
    words(d, VERM)
    x = 96
    for k in range(10):
        w = 227 if k == 2 else 192
        top, h = (206 - 30, 468 + 60) if k == 2 else (206, 468)
        tilt = 0 if k == 2 else (14 if k % 2 else -14)
        if x > 1920:
            break
        col = CREAM if k == 2 else (CREAM if k % 2 else (236, 229, 216))
        poly = [(x, top + max(tilt, 0)), (x + w, top + max(-tilt, 0)), (x + w, top + h - max(-tilt, 0)), (x, top + h - max(tilt, 0))]
        d.polygon(poly, fill=col, outline=RULE)
        bar(d, x + 16, top + 24, 70, 26, VERM)                            # the year
        bar(d, x + 16, top + 82, w - 32, int((w - 32) * 1.5), PLATES[k % len(PLATES)])
        bar(d, x + 16, top + 82 + int((w - 32) * 1.5) + 14, w - 60, 14, INK if k == 2 else INK2)
        if k == 2:
            bar(d, x, top, w, 8, VERM)
        x += w
    bar(d, 96, 668, 1824, 6, (200, 194, 184))      # contact line
    bar(d, 96, 742, 760, 50, INK)
    for k in range(3):
        bar(d, 96, 818 + k * 37, 1240 - (k == 2) * 400, 16, INK2)
    bar(d, 96, 938, 620, 14, CAP)
    save(im, "accordion")


if __name__ == "__main__":
    accordion()
    table("table", VERM, 0)
    leaflet()
    prints()
    table("crate", MARI, 2, w=168, h=206, slot=(222, 252), top=164, square=True)
    poster()
    shelf("shelf_films", VERM, 0)
    shelf("shelf_series", COBALT, 1)
    seasons()
    strip()
    sleeves()
    list_view("list", VERM, 0, square=False)
    list_view("list_music", (168, 108, 12), 2, square=True)
