"""Schematic previews of Void's library views for the view picker (Custom_1161_ViewPicker.xml).

Run:  python skins/skin.void/_src/make_view_previews.py   ->  media/views/{index,wall,covers}.png

No screenshots and no artwork (the skin is GPL and goes to Kodi's official repository): every preview
is drawn from the views' real geometry (Includes_Views.xml, Includes_Rotary.xml via make_rotary.py)
scaled 1920x1080 -> 320x180, on Void's true black with neutral grey placeholder tiles (a little
tonal variety, a hint of a title line). Focus in Void's language: the focused item is brighter and
6 % larger (posters) or the big white row (index). Drawn at 4x and downsampled (anti-aliased).
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "views"
W, H = 320, 180
SS = 4
K = W * SS / 1920.0          # design px -> canvas px

BG = (0, 0, 0, 255)
TEXT = (242, 242, 240)
GREY = (138, 138, 136)
TILES = [(40, 40, 39), (48, 48, 46), (34, 34, 33), (56, 56, 54), (44, 44, 42), (30, 30, 29)]
FOCUS_TILE = (150, 150, 146)


def c(v):
    return v * K


def canvas():
    img = Image.new("RGBA", (W * SS, H * SS), BG)
    return img, ImageDraw.Draw(img)


def bar(d, x, y, w, h, col, alpha=1.0):
    r = min(h, w) / 2
    # Void draws on true black: mix the alpha against it (ImageDraw replaces pixels, it doesn't blend)
    mixed = tuple(round(v * alpha) for v in col) + (255,)
    d.rounded_rectangle([c(x), c(y), c(x + w), c(y + h)], radius=c(r) if r > 0 else 0, fill=mixed)


def header(d, title_w=300, sub_w=180):
    # caps label on the axis (MOVIES . A TO Z) + the 40% clock top right
    bar(d, 160, 90, title_w, 16, GREY, 0.9)
    bar(d, 160 + title_w + 30, 90, sub_w, 16, GREY, 0.55)
    bar(d, 1640, 88, 120, 18, TEXT, 0.4)


def tile(d, x, y, w, h, col, title=True, focused=False):
    if focused:
        # Void_Anim_FocusPoster: zoom 106 about the centre
        gx, gy = w * 0.03, h * 0.03
        x, y, w, h = x - gx, y - gy, w + 2 * gx, h + 2 * gy
    d.rectangle([c(x), c(y), c(x + w), c(y + h)], fill=col + (255,))
    if title:
        # a hint of a title line near the foot of the art
        lc = tuple(min(255, v + 34) for v in col)
        d.rectangle([c(x + w * 0.16), c(y + h * 0.80), c(x + w * 0.84), c(y + h * 0.80 + max(10, h * 0.035))],
                    fill=lc + (255,))


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    out = img.resize((W, H), Image.LANCZOS)
    out.save(OUT / name, optimize=True)
    print(f"  media/views/{name}  {W}x{H}")


def index_view():
    import make_rotary as R
    img, d = canvas()
    header(d)
    rnd = random.Random(50)
    for k in range(-R.F, R.F + 1):
        left, top, height, font, color = R.row_geom(k)
        size = R.SIZE[abs(k)]
        alpha = [1, .46, .36, .29, .24, .20, .17, .15][abs(k)]
        # a title as a bar: x-height band of the serif, a plausible length
        w = (0.55 if k == 0 else rnd.uniform(0.28, 0.62)) * (1200 if k == 0 else 900) * (size / 68.0 if k else 1)
        w = max(90, min(w, 1100))
        band_top = top + 0.28 * size
        bar(d, left + 4, band_top, w, 0.52 * size, TEXT, alpha)
    # floating plate (focused item's poster) + meta lines (Void_View50 grouplist at 1380)
    tile(d, 1380, 282, 300, 450, (70, 70, 68))
    bar(d, 1380, 766, 220, 18, GREY, 0.8)
    bar(d, 1380, 814, 120, 14, GREY, 0.5)
    # A-Z scrubber column at x 1744
    for i in range(26):
        y = 176 + i * 28
        a = 0.95 if i == 7 else 0.3
        d.rectangle([c(1744 - 5), c(y), c(1744 + 5), c(y + 12)], fill=tuple(round(v * a) for v in TEXT) + (255,))
    save(img, "index.png")


def wall_view(name, item_w, item_h, art_h, rows):
    img, d = canvas()
    header(d, 260, 150)
    rnd = random.Random(item_h)
    left, top = 132, 158
    focus = (0, 1)
    for r in range(rows):
        for col in range(6):
            x = left + col * item_w + 28
            y = top + r * item_h + 14
            if (r, col) == focus:
                continue
            tile(d, x, y, 210, art_h, rnd.choice(TILES))
    r, col = focus
    tile(d, left + col * item_w + 28, top + r * item_h + 14, 210, art_h, FOCUS_TILE, focused=True)
    # caption: serif title, meta line, "3 of 412" at the right
    bar(d, 152, 918, 520, 40, TEXT, 0.95)
    bar(d, 160, 990, 300, 16, GREY, 0.8)
    bar(d, 1640, 992, 120, 14, GREY, 0.5)
    save(img, name)


# ---------------------------------------------------------------- 0.9.14 views (_src/make_views.py geometry)
def one_view():
    """One (53): Home's card - neighbour above, kicker, big serif title, meta, plot, neighbour below; art rising."""
    img, d = canvas()
    # the fanart rising behind it (dim, vignetted to the left)
    for x in range(0, 1920, 16):
        a = 0.10 + 0.22 * (x / 1920.0)
        d.rectangle([c(x), c(0), c(x + 16), c(1080)], fill=tuple(round(v * a) for v in (120, 118, 112)) + (255,))
    header(d, 220, 120)
    bar(d, 160, 290, 520, 30, TEXT, 0.28)            # neighbour above (serif 48 at 28 %)
    bar(d, 164, 410, 90, 16, GREY, 0.9)              # kicker (year)
    bar(d, 156, 470, 1010, 110, TEXT, 1.0)           # title (serif 172)
    bar(d, 160, 650, 560, 22, GREY, 0.8)             # meta
    for i in range(3):                               # plot, 3 lines
        bar(d, 160, 712 + i * 42, 820 - (i == 2) * 300, 18, TEXT, 0.6)
    bar(d, 1640, 992, 120, 14, GREY, 0.5)
    save(img, "one.png")


def frames_view():
    """Frames (54): 3 x 2 sparse 16:9 frames, the focused one bright and 6 % larger; serif caption below."""
    img, d = canvas()
    header(d, 260, 150)
    rnd = random.Random(54)
    left, top = 132, 158
    focus = (0, 1)
    for r in range(2):
        for col in range(3):
            if (r, col) == focus:
                continue
            tile(d, left + col * 552 + 28, top + r * 350 + 14, 496, 279, rnd.choice(TILES), title=False)
    r, col = focus
    tile(d, left + col * 552 + 28, top + r * 350 + 14, 496, 279, FOCUS_TILE, title=False, focused=True)
    bar(d, 152, 918, 520, 40, TEXT, 0.95)
    bar(d, 160, 990, 300, 16, GREY, 0.8)
    bar(d, 1640, 992, 120, 14, GREY, 0.5)
    save(img, "frames.png")


def notes_view():
    """Notes (55): a text list on the axis (focused row = white serif) and a reading column at x 1000."""
    img, d = canvas()
    header(d, 220, 150)
    rnd = random.Random(55)
    for i in range(12):
        y = 180 + i * 64
        if i == 3:
            bar(d, 160, y + 14, 520, 34, TEXT, 1.0)
        else:
            bar(d, 160, y + 22, rnd.uniform(220, 560), 20, GREY, 0.75)
            bar(d, 760, y + 24, 70, 14, GREY, 0.35)
    bar(d, 1004, 190, 90, 16, GREY, 0.9)             # kicker
    bar(d, 1000, 236, 560, 52, TEXT, 1.0)            # title (serif 56)
    bar(d, 1000, 318, 440, 20, GREY, 0.8)            # meta
    for i in range(10):                              # plot
        bar(d, 1000, 372 + i * 42, 760 - (i == 9) * 330 - rnd.uniform(0, 60), 18, TEXT, 0.55)
    bar(d, 1000, 806, 380, 14, GREY, 0.7)            # credits
    bar(d, 1640, 992, 120, 14, GREY, 0.5)
    save(img, "notes.png")


def stills_view():
    """Stills (56): one episode per row: a 16:9 still, its number, title and two lines of plot."""
    img, d = canvas()
    header(d, 260, 120)
    rnd = random.Random(56)
    for i in range(5):
        y = 160 + i * 160
        foc = i == 1
        tile(d, 160, y + 12, 240, 135, FOCUS_TILE if foc else rnd.choice(TILES), title=False, focused=foc)
        bar(d, 432, y + 18, 260, 14, GREY, 0.9 if foc else 0.5)
        if foc:
            bar(d, 432, y + 46, 560, 34, TEXT, 1.0)
        else:
            bar(d, 432, y + 52, rnd.uniform(300, 520), 20, GREY, 0.75)
        bar(d, 432, y + 98, 1150, 14, GREY, 0.6 if foc else 0.35)
        bar(d, 432, y + 128, 760, 14, GREY, 0.6 if foc else 0.35)
    bar(d, 1640, 992, 120, 14, GREY, 0.5)
    save(img, "stills.png")


def tracks_view():
    """Tracks (57): a tracklist - number, title (focused = white serif), artist / album, time."""
    img, d = canvas()
    header(d, 260, 120)
    rnd = random.Random(57)
    for i in range(12):
        y = 180 + i * 64
        foc = i == 4
        bar(d, 190, y + 24, 28, 16, GREY, 0.8 if foc else 0.4)
        if foc:
            bar(d, 252, y + 14, 520, 34, TEXT, 1.0)
        else:
            bar(d, 252, y + 22, rnd.uniform(240, 600), 20, GREY, 0.75)
        bar(d, 1132, y + 24, rnd.uniform(200, 380), 16, GREY, 0.7 if foc else 0.4)
        bar(d, 1690, y + 24, 70, 16, GREY, 0.8 if foc else 0.4)
    bar(d, 1640, 992, 120, 14, GREY, 0.5)
    save(img, "tracks.png")


def main():
    import sys
    sys.path.insert(0, str(HERE))
    index_view()
    wall_view("wall.png", 266, 360, 315, 2)
    wall_view("covers.png", 266, 246, 210, 3)
    one_view()
    frames_view()
    notes_view()
    stills_view()
    tracks_view()


if __name__ == "__main__":
    main()
