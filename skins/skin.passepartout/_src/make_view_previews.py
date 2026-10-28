"""Schematic view previews for the view picker (Custom_1156_ViewPicker.xml).

Each preview is the view's real geometry (the numbers below are copied from Includes_Views_Video.xml,
Includes_Views_Music.xml, Includes_Views.xml and make_wall.py) drawn on the neutral paper with neutral
placeholder prints: blocks with a little tonal variety, a hint of a title line, the white bevel. No
artwork, no screenshots (the skin is GPL and goes to the official repository).

The chosen print carries Passe-partout's focus language: it hangs larger, lifted on its soft shadow
(the hang, the salon, the wall's mat), or the ink placard (list rows).

Drawn at 1920x1080 and reduced to 320x180 (media/pp/views/<name>.png).
Run: python make_view_previews.py
"""
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "pp" / "views"
W, H = 1920, 1080
SIZE = (320, 180)

PAPER = (238, 234, 227)
INK = (28, 27, 25)
INK2 = (95, 91, 85)
INK3 = (160, 155, 147)
RULE = (205, 200, 192)
WHITE = (252, 251, 249)
SHADOW = (74, 68, 60)
# muted placeholder tones (no colour that reads as a real poster)
TONES = [(176, 166, 152), (146, 153, 160), (192, 178, 154), (128, 134, 128), (170, 146, 138),
         (152, 160, 144), (122, 124, 138), (188, 172, 168), (160, 150, 128), (138, 146, 150)]


class Board:
    def __init__(self, seed):
        self.rnd = random.Random(seed)
        self.img = Image.new("RGB", (W, H), PAPER)
        self.shadow = Image.new("L", (W, H), 0)
        self.d = ImageDraw.Draw(self.img)
        self.mask = Image.new("L", (W, H), 0)
        self.md = ImageDraw.Draw(self.mask)

    def rect(self, box, fill):
        self.d.rectangle(box, fill=fill)
        self.md.rectangle(box, fill=255)

    def tone(self):
        return self.rnd.choice(TONES)

    def lift(self, x, y, w, h, strength=200, blur=34):
        sd = ImageDraw.Draw(self.shadow)
        sd.rectangle([x + 10, y + 28, x + w - 10, y + h + 26], fill=strength)

    def print_(self, x, y, w, h, tone=None, bevel=8, title=True):
        tone = tone or self.tone()
        d = self.d
        self.rect([x, y, x + w - 1, y + h - 1], WHITE)
        ix, iy, iw, ih = x + bevel, y + bevel, w - 2 * bevel, h - 2 * bevel
        # a gentle vertical ramp inside the print
        for k in range(ih):
            t = k / max(1, ih - 1)
            c = tuple(int(v * (1.06 - 0.16 * t)) for v in tone)
            c = tuple(min(255, v) for v in c)
            d.line([ix, iy + k, ix + iw - 1, iy + k], fill=c)
        if title and iw > 60:
            bw = int(iw * self.rnd.uniform(0.45, 0.7))
            bh = max(6, ih // 18)
            by = iy + int(ih * 0.72)
            bc = tuple(max(0, v - 46) for v in tone)
            d.rectangle([ix + (iw - bw) // 2, by, ix + (iw + bw) // 2, by + bh], fill=bc)

    def bar(self, x, y, w, h, color=INK):
        self.rect([x, y, x + w, y + h], color)

    def rule(self, x, y, w, color=RULE, t=4):
        self.rect([x, y, x + w, y + t], color)

    def header(self, words=(76, 182, 232, 126), section_w=None):
        """FILMS (underlined) · words · count, clock on the right."""
        x = 120
        sw = section_w or words[0]
        self.bar(x, 72, sw, 14, INK)
        self.rule(x, 96, sw, INK, 3)
        x += sw + 56
        for w in words[1:]:
            self.bar(x, 72, w, 14, INK3)
            x += w + 52
        self.bar(x, 70, 42, 16, INK3)
        self.bar(1560, 72, 150, 14, INK3)
        self.bar(1740, 66, 60, 22, INK2)

    def save(self, name):
        sh = self.shadow.filter(ImageFilter.GaussianBlur(30))
        base = Image.new("RGB", (W, H), PAPER)
        tint = Image.new("RGB", (W, H), SHADOW)
        base = Image.composite(tint, base, sh.point(lambda v: int(v * 0.8)))
        # paste the prints over the shadowed paper (everything that isn't paper)
        base.paste(self.img, (0, 0), self.mask)
        OUT.mkdir(parents=True, exist_ok=True)
        base.resize(SIZE, Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
        print("wrote", name)


def caption(b, x, y, title_w=420, cap_w=700, museum_w=520):
    b.bar(x, y + 14, title_w, 44, INK)
    b.bar(x, y + 100, cap_w, 14, INK)
    b.bar(x, y + 140, museum_w, 16, INK2)


def hang():
    """500: one row on the line, the third print chosen (400x600 at x 520, neighbours 216x324)."""
    b = Board(500)
    b.header()
    xs = [-56, 232]
    for x in xs:
        b.print_(x, 308, 216, 324)
    b.lift(516, 170, 408, 608)
    b.print_(516, 170, 408, 608, TONES[2], bevel=10)
    for k in range(4):
        b.print_(988 + k * 288, 308, 216, 324)
    caption(b, 520, 806)
    b.save("hang")


def salon():
    """501: 9 columns of 148x222 prints (pitch 192 x 262) from 98,118; caption bottom left."""
    b = Board(501)
    b.header()
    fx, fy = 2, 1
    for r in range(3):
        for c in range(9):
            if (c, r) == (fx, fy):
                continue
            b.print_(98 + c * 192 + 22, 118 + r * 262 + 22, 148, 222)
    # the chosen print: 112 % about its centre, small lift
    cx, cy = 98 + fx * 192 + 96, 118 + fy * 262 + 133
    w, h = int(148 * 1.12), int(222 * 1.12)
    b.lift(cx - w // 2, cy - h // 2, w, h)
    b.print_(cx - w // 2, cy - h // 2, w, h, TONES[0])
    b.bar(120, 940, 380, 32, INK)
    b.bar(120, 990, 560, 14, INK2)
    b.save("salon")


def series():
    """502: the chosen poster first (300x450 at 120,130), neighbours 160x240 on the line at y 355,
    caption under it, Next up on the right, the seasons row at the bottom."""
    b = Board(502)
    b.header(words=(88, 113, 232, 168))
    b.lift(120, 130, 300, 450)
    b.print_(120, 130, 300, 450, TONES[1], bevel=10)
    for k in range(7):
        b.print_(492 + k * 232, 235, 160, 240)
    b.bar(120, 640, 220, 50, INK)
    b.bar(120, 716, 560, 14, INK)
    b.bar(120, 752, 420, 16, INK2)
    b.rule(904, 596, 896)
    b.bar(904, 616, 120, 14, INK2)
    b.print_(904, 656, 120, 180, TONES[4], title=False)
    b.bar(1064, 658, 300, 14, INK)
    b.bar(1064, 696, 340, 36, INK)
    b.bar(1064, 762, 380, 14, INK2)
    b.bar(1064, 800, 460, 16, INK2)
    b.bar(120, 906, 96, 14, INK2)
    for k in range(4):
        b.bar(248 + k * 170, 906, 118, 14, INK)
    b.save("series")


def episodes():
    """503: landscape hang, chosen still 704x396 at 120,174, neighbours 352x198; label left, plot right."""
    b = Board(503)
    b.header(words=(60, 140, 232))
    b.lift(120, 174, 704, 396)
    b.print_(120, 174, 704, 396, TONES[3], bevel=10, title=False)
    for k in range(3):
        b.print_(896 + k * 424, 273, 352, 198, title=False)
    b.bar(120, 628, 300, 14, INK)
    b.bar(120, 664, 360, 40, INK)
    b.bar(120, 800, 480, 14, INK2)
    b.bar(120, 838, 520, 16, INK2)
    b.rule(904, 596, 896)
    for k in range(3):
        b.bar(904, 636 + k * 40, 896 if k < 2 else 540, 14, (90, 87, 82))
    b.save("episodes")


def wall():
    """506 (Medium, paper between): 8 across, print 200x300, pitch 240x340; the chosen print on its mat."""
    b = Board(506)
    fc, fr = 3, 1
    for r in range(4):
        for c in range(8):
            if (c, r) == (fc, fr):
                continue
            b.print_(c * 240 + 20, r * 340 + 20, 200, 300)
    cx, cy = fc * 240 + 120, fr * 340 + 170
    w, h = int(200 * 1.12), int(300 * 1.12)
    m = 24
    b.lift(cx - w // 2 - m, cy - h // 2 - m, w + 2 * m, h + 2 * m)
    b.rect([cx - w // 2 - m, cy - h // 2 - m, cx + w // 2 + m, cy + h // 2 + m], (246, 243, 238))
    b.print_(cx - w // 2, cy - h // 2, w, h, TONES[5])
    b.save("wall")


def listview(square=False):
    """50: rows of 66 from 120,200 (1080 wide, the focused row is the ink placard); the item as a small
    wall label on the right (print at 1304,210, title, caption, plot)."""
    b = Board(50 + square)
    b.header(words=(81, 103, 105, 86, 99) if square else (76, 182, 232, 126))
    for k in range(12):
        y = 200 + k * 66
        if k == 2:
            b.bar(120, y, 1080, 66, INK)
            b.bar(160, y + 26, 360, 16, (238, 234, 227))
            b.bar(1030, y + 26, 120, 14, (210, 205, 198))
            continue
        b.rule(120, y + 64, 1080, (222, 217, 209), 3)
        b.bar(160, y + 26, self_w(k), 16, INK2)
        b.bar(1070, y + 26, 80, 14, INK3)
    if square:
        b.lift(1304, 210, 400, 400)
        b.print_(1304, 210, 400, 400, TONES[6])
        top = 650
    else:
        b.lift(1304, 210, 268, 400)
        b.print_(1304, 210, 268, 400, TONES[6])
        top = 650
    b.bar(1300, top + 6, 360, 40, INK)
    b.bar(1300, top + 72, 300, 14, INK2)
    for k in range(4):
        b.bar(1300, top + 116 + k * 34, 480 if k < 3 else 300, 12, (110, 106, 100))
    b.save("music_list" if square else "list")


def self_w(k):
    return [300, 420, 360, 260, 480, 340, 300, 400, 280, 440, 320, 380][k]


def music_hang():
    """504: square prints on the line, the third chosen (480 at 540,230; neighbours 280 at y 330)."""
    b = Board(504)
    b.header(words=(81, 103, 105, 86, 99, 81))
    for x in (-196, 168):
        b.print_(x, 330, 280, 280)
    b.lift(536, 226, 488, 488)
    b.print_(536, 226, 488, 488, TONES[7], bevel=10)
    for k in range(3):
        b.print_(1108 + k * 368, 330, 280, 280)
    b.bar(540, 786, 380, 50, INK)
    b.bar(540, 872, 420, 14, INK)
    b.save("music_hang")


def music_salon():
    """505: 8 columns of 172 squares (pitch 216 x 256) from 98,118; caption bottom left."""
    b = Board(505)
    b.header(words=(81, 103, 105, 86, 99, 81))
    fx, fy = 1, 1
    for r in range(3):
        for c in range(8):
            if (c, r) == (fx, fy):
                continue
            b.print_(98 + c * 216 + 22, 118 + r * 256 + 22, 172, 172)
    cx, cy = 98 + fx * 216 + 108, 118 + fy * 256 + 108
    s = int(172 * 1.12)
    b.lift(cx - s // 2, cy - s // 2, s, s)
    b.print_(cx - s // 2, cy - s // 2, s, s, TONES[8])
    b.bar(120, 910, 380, 32, INK)
    b.bar(120, 958, 520, 14, INK2)
    b.save("music_salon")


def widehang():
    """503 for films / series: the landscape hang, chosen print 704x396 at 120,174; label left, plot right."""
    b = Board(513)
    b.header()
    b.lift(120, 174, 704, 396)
    b.print_(120, 174, 704, 396, TONES[5], bevel=10)
    for k in range(3):
        b.print_(896 + k * 424, 273, 352, 198)
    b.bar(120, 628, 420, 14, INK)
    b.bar(120, 664, 300, 40, INK)
    b.bar(120, 800, 360, 14, INK2)
    b.bar(120, 838, 520, 16, INK2)
    b.rule(904, 596, 896)
    for k in range(3):
        b.bar(904, 636 + k * 40, 896 if k < 2 else 540, 14, (90, 87, 82))
    b.save("widehang")


def printroom():
    """507: 4 x 3 landscape prints 352x198 (pitch 432 x 300) from 98,118, a label under each; one chosen."""
    b = Board(507)
    b.header()
    fx, fy = 1, 0
    for r in range(3):
        for c in range(4):
            x, y = 98 + c * 432 + 40, 118 + r * 300 + 22
            b.bar(x, y + 222, 240, 16, INK)
            b.bar(x, y + 252, 170, 12, INK2)
            if (c, r) == (fx, fy):
                continue
            b.print_(x, y, 352, 198, title=False)
    x, y = 98 + fx * 432 + 40, 118 + fy * 300 + 22
    w, h = int(352 * 1.08), int(198 * 1.08)
    cx, cy = x + 176, y + 99
    b.lift(cx - w // 2, cy - h // 2, w, h)
    b.print_(cx - w // 2, cy - h // 2, w, h, TONES[1], title=False)
    b.save("printroom")


def music_tracklist():
    """508: caps column head at y 132 over a rule, rows of 66 from 120,174 (1680 wide), the focused row the placard."""
    b = Board(508)
    b.header(words=(81, 103, 105, 86, 99, 81))
    for x, w in ((144, 34), (220, 70), (844, 80), (1248, 70), (1612, 50), (1716, 60)):
        b.bar(x, 138, w, 14, INK2)
    b.rule(120, 172, 1680, RULE, 3)
    for k in range(11):
        y = 174 + k * 66
        if k == 2:
            b.bar(120, y, 1680, 66, INK)
            for x, w in ((144, 30), (220, 360), (844, 220), (1248, 200), (1612, 48), (1716, 60)):
                b.bar(x, y + 26, w, 14, (238, 234, 227))
            continue
        b.rule(120, y + 64, 1680, (222, 217, 209), 3)
        b.bar(144, y + 26, 30, 14, INK3)
        b.bar(220, y + 24, self_w(k), 16, INK)
        b.bar(844, y + 26, self_w(k + 1) * 2 // 3, 14, INK2)
        b.bar(1248, y + 26, self_w(k) // 2, 14, INK2)
        b.bar(1612, y + 26, 48, 14, INK3)
        b.bar(1716, y + 26, 60, 14, INK3)
    b.save("music_tracklist")


if __name__ == "__main__":
    hang()
    salon()
    series()
    episodes()
    wall()
    listview()
    listview(square=True)
    music_hang()
    music_salon()
    widehang()
    printroom()
    music_tracklist()
