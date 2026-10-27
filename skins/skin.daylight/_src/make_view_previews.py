"""Schematic previews of Daylight's library views for the view picker (Custom_1161_ViewPicker.xml).

Run:  python skins/skin.daylight/_src/make_view_previews.py
      -> media/views/<view>_<layer>.png (320x180, white + alpha)   and   _src/previews/views_*.png (check sheets)

Daylight's palette follows the time of day, so a preview is not one coloured picture: it is seven
white-alpha LAYERS that the picker tints with the live mood colours (the same $VAR the views use):
  ground   DL_Ground     the page
  surface  DL_Surface    the soft cards
  raised   DL_Raised     poster / thumb placeholders, rows, pills (tonal variety = alpha)
  ink      DL_Ink        titles
  ink2     DL_Ink2       secondary lines (a hint of a title line on each placeholder)
  accent   DL_Accent     focus ring, kicker dot, the focused list row
  onaccent DL_OnAccent   text on the focused list row
So morning / afternoon / evening / night previews match the page around them.
No screenshots and no artwork (GPL skin, Kodi's official repository): the geometry is the views' own
(Includes_Views_Video.xml / Includes_Views_Music.xml) scaled 1920x1080 -> 320x180, drawn at 4x.
Views: grid (500), wall (501), spotlight (502), episodes (503), wide (505), time (506), list (50),
music_grid (504), music_wall (508), music_spot (507), music_list (50).
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "views"
SHEETS = HERE / "previews"
W, H = 320, 180
SS = 4
CW, CH = W * SS, H * SS
K = CW / 1920.0
LAYERS = ["ground", "surface", "raised", "ink", "ink2", "accent", "onaccent"]

# palettes for the check sheets only (colors/defaults.xml: a_* afternoon, n_* night)
PAL = {
    "afternoon": dict(ground=(245, 242, 236), surface=(255, 253, 249), raised=(236, 230, 220), ink=(34, 32, 28),
                      ink2=(98, 91, 80), accent=(217, 130, 43), onaccent=(255, 253, 249)),
    "night": dict(ground=(14, 20, 36), surface=(21, 29, 49), raised=(31, 42, 71), ink=(185, 195, 214),
                  ink2=(138, 150, 173), accent=(122, 156, 255), onaccent=(14, 20, 36)),
}


def c(v):
    return v * K


class Prev:
    def __init__(self):
        self.img = {n: Image.new("L", (CW, CH), 0) for n in LAYERS}
        self.d = {n: ImageDraw.Draw(self.img[n]) for n in LAYERS}

    def rect(self, layer, x, y, w, h, r=0, a=1.0):
        self.d[layer].rounded_rectangle([c(x), c(y), c(x + w), c(y + h)], radius=c(r), fill=round(255 * a))

    def bar(self, layer, x, y, w, h, a=1.0):
        self.rect(layer, x, y, w, h, r=h / 2, a=a)

    def ring(self, layer, x, y, w, h, r, width=4, a=1.0):
        self.d[layer].rounded_rectangle([c(x), c(y), c(x + w), c(y + h)], radius=c(r), outline=round(255 * a),
                                        width=max(2, round(c(width))))

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        # the preview itself has Daylight's rounded corners (radius 28 at 1920 -> ~5 px)
        mask = Image.new("L", (CW, CH), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW - 1, CH - 1], radius=c(84), fill=255)
        for n in LAYERS:
            a = Image.composite(self.img[n], Image.new("L", (CW, CH), 0), mask) if n != "ground" else mask
            a = a.resize((W, H), Image.LANCZOS)
            out = Image.new("RGBA", (W, H), (255, 255, 255, 0))
            out.putalpha(a)
            out.save(OUT / f"{name}_{n}.png", optimize=True)
        print(f"  media/views/{name}_*.png  ({len(LAYERS)} layers)")
        return self

    def sheet(self, pal):
        base = Image.new("RGB", (CW, CH), (0, 0, 0))
        for n in LAYERS:
            col = Image.new("RGB", (CW, CH), PAL[pal][n])
            base = Image.composite(col, base, self.img[n] if n != "ground" else Image.new("L", (CW, CH), 255))
        return base.resize((W, H), Image.LANCZOS)


def top_line(p, active):
    p.bar("ink2", 120, 80, 40, 26, 0.9)            # mood icon
    p.bar("ink", 164, 80, 140, 22, 0.9)            # "Past midnight"
    p.bar("ink2", 330, 82, 90, 18, 0.7)            # weather
    xs = [(996, 133), (1135, 96), (1237, 110), (1353, 103), (1462, 114)]
    for i, (x, w) in enumerate(xs):
        if i == active:
            p.rect("surface", x, 64, w, 52, r=26)
        p.bar("ink2" if i != active else "ink", x + 24, 82, w - 48, 18, 0.85)
    p.rect("ink2", 1597, 75, 30, 30, r=15, a=0.7)  # gear
    p.bar("ink", 1676, 76, 124, 28, 0.95)          # clock


def card(p, x, y, w, h):
    p.rect("surface", x, y, w, h, r=28)


def header(p, x, pills, title_w=85):
    p.bar("ink", x, 206, title_w, 30, 0.95)
    p.bar("ink2", x + title_w + 18, 214, 150, 16, 0.75)
    px = 1760
    for i, w in enumerate(reversed(pills)):
        px -= w
        p.rect("raised", px, 204, w, 40, r=20, a=0.9)
        p.bar("ink", px + 16, 216, w - 32, 14, 0.7)
        px -= 10


def detail(p, plot=4, when=True):
    p.rect("accent", 160, 177, 10, 10, r=5)
    p.bar("accent", 180, 172, 200, 18, 0.9)
    p.bar("ink", 160, 214, 380, 48, 0.95)
    p.bar("ink", 160, 290, 260, 20, 0.8)
    p.bar("ink2", 160, 330, 300, 16, 0.75)
    for i in range(plot):
        p.bar("ink2", 160, 376 + i * 34, 500 * (0.94 if i < plot - 1 else 0.55), 16, 0.6)
    if when:
        card(p, 160, 822, 500, 194)
        p.bar("accent", 190, 848, 180, 18, 0.9)
        p.bar("ink", 190, 890, 300, 28, 0.95)
        p.bar("ink2", 190, 940, 380, 16, 0.7)


def poster_grid(p, x0, y0, cell_w, cell_h, w, h, cols, rows, focus, r=16, clip=1016):
    rnd = random.Random(cell_w * 7 + cols)
    for row in range(rows):
        for col in range(cols):
            x = x0 + col * cell_w + 18
            y = y0 + row * cell_h + 18
            if y > clip - 30:
                continue
            hh = min(h, clip - y)
            if (row, col) == focus:
                gx, gy = w * 0.03, h * 0.03
                p.rect("raised", x - gx, y - gy, w + 2 * gx, h + 2 * gy, r=r, a=1.0)
                p.ring("accent", x - gx - 9, y - gy - 9, w + 2 * gx + 18, h + 2 * gy + 18, r + 9, width=4)
                p.bar("ink2", x + w * 0.18, y + h * 0.82, w * 0.64, 10, 0.55)
                continue
            p.rect("raised", x, y, w, hh, r=r, a=rnd.uniform(0.55, 1.0))
            if hh == h:
                p.bar("ink2", x + w * 0.18, y + h * 0.82, w * 0.64, 10, 0.3)


def grid():
    p = Prev()
    top_line(p, 1)
    detail(p)
    card(p, 680, 168, 1120, 848)
    header(p, 720, [176, 200, 44, 124, 110])
    poster_grid(p, 702, 262, 214, 306, 184, 276, 5, 3, (0, 1))
    return p.save("grid")


def wall():
    p = Prev()
    top_line(p, 1)
    card(p, 160, 168, 1600, 848)
    header(p, 200, [176, 200, 44, 124, 110], title_w=85)
    poster_grid(p, 142, 262, 204, 292, 168, 252, 8, 3, (0, 2))
    return p.save("wall")


def episodes():
    p = Prev()
    top_line(p, 2)
    detail(p, plot=3)
    card(p, 680, 168, 1120, 848)
    header(p, 720, [176, 200, 44, 164, 110], title_w=120)
    rnd = random.Random(5)
    for i in range(5):
        y = 262 + i * 168
        if y > 990:
            break
        if i == 1:
            p.rect("raised", 706, y + 4, 1068, 160, r=20)
        p.rect("raised", 724, y + 21, 224, 126, r=12, a=1.0 if i == 1 else rnd.uniform(0.6, 1.0))
        p.bar("accent", 974, y + 22, 90, 14, 0.9)
        p.bar("ink", 974, y + 52, 380, 24, 0.95)
        p.bar("ink2", 974, y + 90, 300, 14, 0.7)
        p.bar("ink2", 974, y + 120, 640, 14, 0.5)
    return p.save("episodes")


def list_view(name, square=False):
    p = Prev()
    top_line(p, 3 if square else 1)
    if square:
        p.rect("raised", 160, 168, 340, 340, r=20)
        p.bar("ink", 160, 548, 360, 40, 0.95)
        p.bar("ink2", 160, 606, 260, 18, 0.75)
        for i in range(3):
            p.bar("ink2", 160, 650 + i * 34, 480 * (0.92 if i < 2 else 0.5), 16, 0.6)
    else:
        detail(p, plot=4, when=False)
    card(p, 680, 168, 1120, 848)
    header(p, 720, [208, 44, 124, 110] if square else [176, 200, 44, 124, 110])
    rnd = random.Random(9)
    for i in range(10):
        y = 262 + i * 76 + 18
        if y > 990:
            break
        if i == 2:
            p.rect("accent", 706, y - 14, 1068, 70, r=35)
            p.bar("onaccent", 740, y + 8, 420, 22, 1.0)
            p.bar("onaccent", 1640, y + 10, 100, 16, 0.8)
            continue
        p.bar("ink", 740, y + 8, rnd.uniform(240, 520), 22, 0.85)
        p.bar("ink2", 1640, y + 10, 100, 16, 0.6)
    return p.save(name)


def music_grid():
    p = Prev()
    top_line(p, 3)
    p.rect("raised", 160, 168, 340, 340, r=20)
    p.bar("ink", 160, 548, 360, 40, 0.95)
    p.bar("ink2", 160, 606, 260, 18, 0.75)
    for i in range(3):
        p.bar("ink2", 160, 650 + i * 34, 480 * (0.92 if i < 2 else 0.5), 16, 0.6)
    card(p, 680, 168, 1120, 848)
    p.rect("accent", 720, 204, 120, 40, r=20, a=0.25)
    for i, w in enumerate((120, 116, 108, 118)):
        x = 720 + sum((120, 116, 108, 118)[:i]) + 8 * i
        p.rect("raised", x, 204, w, 40, r=20, a=0.9)
        p.bar("ink", x + 18, 216, w - 36, 14, 0.7)
    header(p, 2000, [208, 44, 124, 110])
    poster_grid(p, 702, 262, 214, 282, 184, 184, 5, 3, (0, 1))
    return p.save("music_grid")


# ------------------------------------------------------------------ 0.9.15 views
def wide_header(p, pills):
    p.bar("ink", 160, 206, 85, 30, 0.95)
    p.bar("ink2", 263, 214, 150, 16, 0.75)
    header(p, 4000, pills)          # pills only (title drawn above at the card inset)


def spot_hero(p, square=False, round_=False):
    # fanart melting into the card from the right (raised, stepped alpha), text column on the left
    for i, a in enumerate((0.25, 0.45, 0.65, 0.85, 1.0)):
        p.rect("raised", 1000 + i * 70, 168, 800 - i * 70, 470 - i * 18, r=28, a=a * 0.8)
    if round_:
        p.rect("ink2", 1330, 270, 300, 300, r=150, a=0.35)
    p.rect("accent", 160, 281, 10, 10, r=5)
    p.bar("accent", 180, 274, 200, 18, 0.9)
    p.bar("ink", 160, 312, 520, 52, 0.95)
    p.bar("ink", 160, 392, 300, 22, 0.8)
    p.bar("ink2", 160, 430, 260, 16, 0.7)
    for i in range(3):
        p.bar("ink2", 160, 476 + i * 34, 700 * (0.94 if i < 2 else 0.6), 16, 0.6)
    if not (square or round_):
        p.rect("accent", 160, 656, 22, 22, r=11, a=0.9)
        p.bar("accent", 196, 658, 420, 18, 0.9)


def spotlight():
    p = Prev()
    top_line(p, 1)
    card(p, 120, 168, 1680, 848)
    wide_header(p, [176, 200, 44, 172])
    spot_hero(p)
    rnd = random.Random(21)
    for i in range(10):
        x = 160 + i * 176
        if x > 1700:
            break
        if i == 1:
            p.rect("raised", x - 4, 708, 148, 218, r=16)
            p.ring("accent", x - 13, 699, 166, 236, 25, width=4)
            p.bar("accent", x + 20, 948, 100, 14, 0.9)
            continue
        p.rect("raised", x, 712, 140, 210, r=16, a=rnd.uniform(0.55, 1.0))
        p.bar("ink2", x + 20, 948, 100, 14, 0.5)
    return p.save("spotlight")


def wide_view():
    p = Prev()
    top_line(p, 2)
    card(p, 120, 168, 1680, 848)
    wide_header(p, [128, 176, 200, 44, 172])
    rnd = random.Random(33)
    for row in range(3):
        for col in range(4):
            x = 160 + col * 409
            y = 280 + row * 306
            if y > 990:
                continue
            hh = min(210, 1016 - y)
            if (row, col) == (0, 1):
                p.rect("raised", x - 7, y - 4, 387, 218, r=16)
                p.ring("accent", x - 16, y - 13, 405, 236, 25, width=4)
            else:
                p.rect("raised", x, y, 373, hh, r=16, a=rnd.uniform(0.55, 1.0))
            if y + 240 < 1000:
                p.bar("ink", x, y + 228, rnd.uniform(160, 300), 20, 0.85)
                p.bar("ink2", x, y + 262, 150, 14, 0.6)
    return p.save("wide")


def time_view():
    p = Prev()
    top_line(p, 1)
    card(p, 120, 168, 1680, 848)
    wide_header(p, [176, 200, 44, 172])
    p.bar("accent", 760, 268, 160, 18, 0.9)
    for x in (1000, 1240, 1480, 1720):
        p.rect("raised", x - 1, 300, 3, 716, a=0.9)
        p.bar("ink2", x - 30, 270, 60, 14, 0.6)
    rnd = random.Random(44)
    bed = 1420
    for i in range(8):
        y = 300 + i * 96
        if y > 980:
            break
        if i == 2:
            p.rect("raised", 146, y + 4, 1628, 88, r=20)
        p.rect("raised", 200, y + 6, 56, 84, r=10, a=1.0 if i == 2 else rnd.uniform(0.55, 1.0))
        p.bar("ink", 316, y + 22, rnd.uniform(220, 380), 20, 0.9)
        p.bar("ink2", 316, y + 56, 200, 14, 0.6)
        mins = rnd.choice((92, 104, 118, 131, 145, 158, 176))
        p.bar("accent", 760, y + 34, mins * 4, 28, 1.0)
        p.bar("onaccent", 774, y + 42, 130, 12, 0.9)
    p.rect("surface", bed, 300, 1780 - bed, 716, a=0.55)
    p.rect("accent", bed - 1, 300, 3, 716)
    p.rect("surface", bed - 84, 260, 168, 36, r=18)
    p.bar("accent", bed - 60, 270, 120, 16, 0.9)
    return p.save("time")


def music_wall():
    p = Prev()
    top_line(p, 3)
    card(p, 120, 168, 1680, 848)
    for i, w in enumerate((120, 116, 108, 118)):
        x = 160 + sum((120, 116, 108, 118)[:i]) + 8 * i
        p.rect("raised", x, 204, w, 40, r=20, a=0.9)
        p.bar("ink", x + 18, 216, w - 36, 14, 0.7)
    header(p, 4000, [208, 44, 172])
    poster_grid(p, 142, 262, 204, 262, 168, 168, 8, 3, (0, 2), r=14)
    return p.save("music_wall")


def music_spot():
    p = Prev()
    top_line(p, 3)
    card(p, 120, 168, 1680, 848)
    for i, w in enumerate((120, 116, 108, 118)):
        x = 160 + sum((120, 116, 108, 118)[:i]) + 8 * i
        p.rect("raised", x, 204, w, 40, r=20, a=0.9)
        p.bar("ink", x + 18, 216, w - 36, 14, 0.7)
    header(p, 4000, [208, 44, 172])
    spot_hero(p, round_=True)
    rnd = random.Random(55)
    for i in range(9):
        x = 160 + i * 186
        if i == 1:
            p.ring("accent", x - 9, 729, 168, 168, 84, width=4)
        p.rect("raised", x, 738, 150, 150, r=75, a=1.0 if i == 1 else rnd.uniform(0.55, 1.0))
        p.bar("ink" if i == 1 else "ink2", x + 25, 908, 100, 14, 0.7)
    return p.save("music_spot")


def main():
    made = {"grid": grid(), "wall": wall(), "spotlight": spotlight(), "episodes": episodes(), "wide": wide_view(),
            "time": time_view(), "list": list_view("list"),
            "music_grid": music_grid(), "music_wall": music_wall(), "music_spot": music_spot(),
            "music_list": list_view("music_list", square=True)}
    SHEETS.mkdir(parents=True, exist_ok=True)
    for pal in PAL:
        sheet = Image.new("RGB", (4 * 330, 3 * 190), (128, 128, 128))
        for i, (n, p) in enumerate(made.items()):
            sheet.paste(p.sheet(pal), ((i % 4) * 330 + 5, (i // 4) * 190 + 5))
        sheet.save(SHEETS / f"views_{pal}.png")
        print(f"  _src/previews/views_{pal}.png")


if __name__ == "__main__":
    main()
