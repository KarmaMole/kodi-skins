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
Views: grid (500), wall (501), episodes (503), list (50), music_grid (504), music_list (50).
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


def main():
    made = {"grid": grid(), "wall": wall(), "episodes": episodes(), "list": list_view("list"),
            "music_grid": music_grid(), "music_list": list_view("music_list", square=True)}
    SHEETS.mkdir(parents=True, exist_ok=True)
    for pal in PAL:
        sheet = Image.new("RGB", (3 * 330, 2 * 190), (128, 128, 128))
        for i, (n, p) in enumerate(made.items()):
            sheet.paste(p.sheet(pal), ((i % 3) * 330 + 5, (i // 3) * 190 + 5))
        sheet.save(SHEETS / f"views_{pal}.png")
        print(f"  _src/previews/views_{pal}.png")


if __name__ == "__main__":
    main()
