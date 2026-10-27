"""Schematic view previews for the view picker (Custom_1156_ViewPicker.xml).

    python skins/skin.sentence/_src/make_view_previews.py

Writes media/sentence/views/<view>.png (320 x 180). Each preview is drawn at the real 1920 x 1080 geometry of the
view (numbers from Includes_Views_Video.xml, Includes_Views.xml and Includes_Views_Music.xml) in Sentence's
palette, then scaled down: the collapsed header sentence with its lilac underlines, the rule, and the view's
grid / rows / note column. No artwork: posters are neutral green-grey blocks with a hint of a title line.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "sentence" / "views"
W, H = 1920, 1080
SIZE = (320, 180)
GROUND = (15, 20, 18)
RAISED = (22, 29, 26)
TEXT = (237, 234, 224)
BODY = (196, 195, 186)
MUTED = (140, 145, 139)
FAINT = (60, 66, 62)
LILAC = (185, 166, 255)
TILES = [(58, 70, 64), (74, 82, 76), (48, 58, 54), (88, 92, 84), (66, 76, 72), (54, 64, 70), (80, 74, 68), (62, 68, 60)]


def canvas():
    im = Image.new("RGB", (W, H), GROUND)
    return im, ImageDraw.Draw(im)


def bar(d, x, y, w, h, c):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def tile(d, x, y, w, h, i, dim=True):
    c = TILES[i % len(TILES)]
    if not dim:
        c = tuple(min(v + 40, 255) for v in c)
    bar(d, x, y, w, h, c)
    bar(d, x, y + int(h * 0.6), w, h - int(h * 0.6), tuple(max(v - 12, 0) for v in c))


def header(d, view_w=116):
    bar(d, 120, 78, 70, 14, MUTED)              # HOME / ALL FILMS crumb
    bar(d, 228, 78, 130, 14, TEXT)
    bar(d, 1580, 76, 220, 16, MUTED)            # "It's 3:27 PM and clear."
    x = 120
    for w, phrase in ((230, False), (90, True), (250, True), (170, False), (315, True), (47, False), (view_w, True), (40, False), (106, True)):
        bar(d, x, 136, w, 26, TEXT if not phrase else (205, 196, 240))
        if phrase:
            bar(d, x, 176, w, 4, LILAC)
        x += w + 24
    bar(d, 120, 214, 1680, 2, FAINT)            # rule


def note(d, top=256):
    bar(d, 1308, top + 4, 200, 14, MUTED)       # NUMBER 9 OF 997
    for k in range(5):                          # the serif paragraph
        bar(d, 1308, top + 64 + k * 52, 470 - (k == 4) * 200, 26, TEXT)
    for k in range(4):                          # plot
        bar(d, 1308, top + 450 + k * 38, 480 - (k == 3) * 180, 16, BODY)


def save(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    im.resize(SIZE, Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
    print("wrote", OUT / f"{name}.png")


def grid():
    im, d = canvas()
    header(d)
    i = 0
    for r in range(3):
        for c in range(5):
            x, y = 108 + c * 228 + 12, 244 + r * 392 + 12
            if y > 1080:
                continue
            f = (r == 0 and c == 2)
            tile(d, x, y, 188, 282, i, dim=not f)
            if f:
                bar(d, x, y + 290, 188, 4, LILAC)
            bar(d, x, y + 304, 130, 14, TEXT if f else MUTED)
            bar(d, x, y + 330, 100, 12, LILAC if f else FAINT)
            i += 1
    note(d)
    save(im, "grid")


def wall():
    im, d = canvas()
    header(d, 125)
    i = 0
    for r in range(3):
        for c in range(8):
            x, y = 108 + c * 210 + 12, 244 + r * 350 + 12
            if y > 1080:
                continue
            f = (r == 0 and c == 3)
            tile(d, x, y, 174, 261, i, dim=not f)
            if f:
                bar(d, x, y + 270, 174, 4, LILAC)
            i += 1
    save(im, "wall")


def episodes():
    im, d = canvas()
    header(d, 173)
    for r in range(5):
        y = 240 + r * 190
        f = r == 1
        if f:
            bar(d, 120, y, 1680, 174, RAISED)
        tile(d, 136, y + 15, 256, 144, r, dim=not f)
        if f:
            bar(d, 136, y + 162, 256, 3, LILAC)
        bar(d, 420, y + 26, 520 + (r * 97) % 300, 28, TEXT if f else BODY)
        bar(d, 420, y + 74, 380, 14, LILAC if f else MUTED)
        for k in range(2):
            bar(d, 420, y + 108 + k * 30, 1100 - k * 400, 14, BODY if f else FAINT)
    save(im, "episodes")


def list_view(name, square):
    im, d = canvas()
    header(d, 101)
    for r in range(12):
        y = 244 + r * 66
        if y + 66 > 1040:
            break
        f = r == 2
        if f:
            bar(d, 120, y, 1080, 66, RAISED)
            bar(d, 120, y, 6, 66, LILAC)
        bar(d, 150, y + 24, 300 + (r * 113) % 360, 18, TEXT if f else MUTED)
        bar(d, 1000, y + 26, 150, 14, MUTED)
        bar(d, 120, y + 65, 1080, 1, FAINT)
    bar(d, 1216, 244, 4, 792, FAINT)
    bar(d, 1216, 360, 4, 120, MUTED)
    if square:
        tile(d, 1308, 244, 492, 492, 3, dim=False)
        bar(d, 1308, 770, 360, 28, TEXT)
        for k in range(3):
            bar(d, 1308, 940 + k * 34, 460 - (k == 2) * 160, 14, BODY)
    else:
        note(d, 256)
    save(im, name)


def albums():
    im, d = canvas()
    header(d)
    i = 0
    for r in range(3):
        for c in range(5):
            x, y = 108 + c * 228 + 12, 244 + r * 292 + 12
            if y > 1000:
                continue
            f = (r == 0 and c == 1)
            tile(d, x, y, 188, 188, i, dim=not f)
            if f:
                bar(d, x, y + 200, 188, 3, LILAC)
            bar(d, x, y + 214, 130, 14, TEXT if f else MUTED)
            bar(d, x, y + 240, 100, 12, FAINT)
            i += 1
    note(d)
    save(im, "albums")


# ------------------------------------------------------------ 0.9.16 views (_src/make_views_more.py geometry)
def page_view(name, square=False):
    """a page / portraits: the paragraph and plot on the left, the fanart behind the right half with ramps."""
    im, d = canvas()
    header(d, 110)
    # the backdrop, fading into the ground towards the article
    for x in range(760, 1920, 8):
        a = min(1.0, (x - 760) / 600.0)
        c = tuple(round(g + (t - g) * a * 0.55) for g, t in zip(GROUND, (96, 104, 98)))
        bar(d, x, 230, 8, 850, c)
    bar(d, 120, 256, 220, 14, MUTED)            # Page 5 of 997
    for k in range(5):                          # the serif paragraph
        bar(d, 120, 316 + k * 64, 860 - (k == 4) * 380, 32, TEXT)
    for k in range(4):                          # plot
        bar(d, 120, 670 + k * 38, 800 - (k == 3) * 300, 16, BODY)
    if square:
        tile(d, 1308, 256, 492, 492, 2, dim=False)
    bar(d, 120, 1004, 520, 12, MUTED)           # hint
    save(im, name)


def scenes():
    im, d = canvas()
    header(d, 104)
    i = 0
    for r in range(2):
        for c in range(4):
            x, y = 108 + c * 430 + 12, 244 + r * 350 + 12
            f = (r == 0 and c == 1)
            tile(d, x, y, 400, 225, i, dim=not f)
            if f:
                bar(d, x, y + 235, 400, 4, LILAC)
            bar(d, x, y + 250, 220, 14, TEXT if f else MUTED)
            bar(d, x, y + 278, 160, 12, LILAC if f else FAINT)
            i += 1
    for k in range(1):                          # the focused one, in a sentence
        bar(d, 120, 962, 1100, 26, TEXT)
    save(im, "scenes")


def tracklist():
    im, d = canvas()
    header(d, 150)
    for r in range(12):
        y = 244 + r * 66
        f = r == 3
        if f:
            bar(d, 120, y, 1080, 64, LILAC)
        ink = GROUND if f else TEXT
        soft = GROUND if f else MUTED
        bar(d, 150, y + 26, 26, 14, soft)                       # number
        bar(d, 204, y + 22, 260 + (r * 97) % 280, 22, ink)      # title (serif)
        bar(d, 780, y + 26, 220, 14, soft)                      # by ..., from ...
        bar(d, 1110, y + 26, 66, 14, soft)                      # time
        bar(d, 120, y + 65, 1080, 1, FAINT)
    tile(d, 1308, 256, 492, 492, 4, dim=False)
    for k in range(3):
        bar(d, 1308, 788 + k * 52, 460 - (k == 2) * 200, 26, TEXT)
    save(im, "tracklist")


if __name__ == "__main__":
    page_view("page")
    page_view("portraits", square=False)
    scenes()
    tracklist()
    grid()
    wall()
    episodes()
    list_view("list", square=False)
    list_view("list_music", square=True)
    albums()
