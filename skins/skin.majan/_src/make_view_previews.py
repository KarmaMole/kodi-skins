"""Schematic view previews for Majan's view picker (Custom_1156_ViewPicker.xml).

Each preview is the view's real geometry (numbers from Includes_Views_Video.xml, Includes_Views_Music.xml,
Includes_Views.xml, Includes_Wall.xml / Constants) drawn on Majan's black page with neutral grey placeholder
tiles (a little tonal variety, a hint of a title line), white title bars and grey mono caption bars.
No artwork, no screenshots (the skin is GPL and goes to the official repository).

Two files per view in media/majan/views/:
  <name>.png        the page, the tiles, the text (320x180)
  <name>_accent.png the accent pieces only (the 2 px focus outline, the list's accent bar, the page index),
                    white on transparent: the picker draws it with colordiffuse = the accent colour the user
                    picked, so the preview's focus mark is always the skin's focus mark.
Drawn at 1920x1080 and reduced to 320x180. Run: python make_view_previews.py
"""
from pathlib import Path
import random

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "majan" / "views"
W, H = 1920, 1080
SIZE = (320, 180)

BG = (11, 11, 11)
RAISED = (20, 20, 20)
PANEL = (24, 24, 24)
HAIR = (44, 44, 44)
TXT1 = (236, 235, 231)
TXT2 = (163, 161, 155)
TXT3 = (120, 118, 113)
TONES = [(58, 58, 60), (72, 70, 66), (50, 54, 60), (80, 74, 70), (62, 66, 60), (86, 84, 80),
         (54, 50, 56), (68, 72, 76), (76, 66, 62), (60, 62, 68)]


class Board:
    def __init__(self, seed):
        self.rnd = random.Random(seed)
        self.img = Image.new("RGB", (W, H), BG)
        self.d = ImageDraw.Draw(self.img)
        self.acc = Image.new("L", (W, H), 0)
        self.a = ImageDraw.Draw(self.acc)

    def tile(self, x, y, w, h, tone=None, title=True):
        tone = tone or self.rnd.choice(TONES)
        for k in range(h):
            t = k / max(1, h - 1)
            c = tuple(min(255, int(v * (1.12 - 0.3 * t))) for v in tone)
            self.d.line([x, y + k, x + w - 1, y + k], fill=c)
        if title and w > 60:
            bw = int(w * self.rnd.uniform(0.45, 0.7))
            bh = max(6, h // 18)
            by = y + int(h * 0.74)
            self.d.rectangle([x + (w - bw) // 2, by, x + (w + bw) // 2, by + bh], fill=tuple(v + 40 for v in tone))

    def outline(self, x, y, w, h, t=8, out=6):
        """Majan's 2 px focus outline (drawn 8 px at 1920 so it survives the reduction), 6 px outside."""
        x0, y0, x1, y1 = x - out, y - out, x + w + out, y + h + out
        self.a.rectangle([x0, y0, x1, y1], outline=255, width=t)

    def bar(self, x, y, w, h, color=TXT1):
        self.d.rectangle([x, y, x + w, y + h], fill=color)

    def accent_bar(self, x, y, w, h):
        self.a.rectangle([x, y, x + w, y + h], fill=255)

    def rule(self, x, y, w, t=4, color=HAIR):
        self.d.rectangle([x, y, x + w, y + t], fill=color)

    def header(self, title_w=150, words=(88, 143, 110, 11, 176)):
        self.accent_bar(96, 60, 22, 10)                      # page index "02"
        self.bar(136, 44, title_w, 32, TXT1)                 # page name
        x = 1540
        for w in reversed(words):                            # right-aligned filter bar
            x -= w
            self.bar(x, 58, w, 12, TXT3)
            x -= 40
        self.bar(1554, 60, 190, 12, TXT2)                    # date
        self.bar(1760, 46, 64, 30, TXT1)                     # clock
        self.rule(96, 118, 1728, 3)

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        self.img.resize(SIZE, Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
        a = self.acc.resize(SIZE, Image.LANCZOS)
        rgba = Image.new("RGBA", SIZE, (255, 255, 255, 0))
        rgba.putalpha(a)
        rgba.save(OUT / f"{name}_accent.png", optimize=True)
        print("wrote", name)


def showcase():
    """500: the hero panel (96,168 520x780), the text column at 680, the strip of 100x150 tiles at y 818."""
    b = Board(500)
    b.header()
    b.tile(96, 168, 520, 780, TONES[1], title=False)
    b.bar(680, 176, 520, 60, TXT1)
    b.bar(680, 256, 700, 12, TXT3)
    b.rule(680, 366, 1144, 3)
    for k in range(5):
        b.bar(680 + k * 228, 392, 70, 10, TXT3)
        b.bar(680 + k * 228, 420, 140, 22, TXT1)
    b.rule(680, 462, 1144, 3)
    for k in range(3):
        b.bar(680, 500 + k * 36, 1000 if k < 2 else 640, 12, TXT2)
    b.bar(96, 972, 180, 10, TXT3)
    for k in range(10):
        x = 680 + k * 116
        if x > 1900:
            break
        b.tile(x, 818, 100, 150)
    b.outline(796, 818, 100, 150)
    b.save("showcase")


def bigposter():
    """501: posters 330x495 at y 160 (pitch 354 from x 96), the second chosen; its text under it at 450."""
    b = Board(501)
    b.header()
    for k in range(6):
        b.tile(96 + k * 354, 160, 330, 495, TONES[3] if k == 1 else None)
    b.outline(450, 160, 330, 495)
    b.bar(96, 714, 120, 10, TXT3)
    b.bar(96, 744, 140, 12, TXT1)
    b.accent_bar(450, 708, 300, 12)
    b.bar(450, 754, 260, 52, TXT1)
    b.bar(450, 824, 700, 12, TXT3)
    b.bar(450, 862, 1170, 14, TXT2)
    b.bar(450, 896, 220, 14, TXT2)
    b.bar(450, 940, 180, 16, TXT1)
    b.save("bigposter")


def tvwall():
    """502: Next up cards (320x180, pitch 344) at y 200, then the show line and 10 columns of 158x237."""
    b = Board(502)
    b.header(words=(88, 154, 120, 11, 110))
    b.bar(96, 152, 170, 26, TXT1)
    b.bar(1394, 162, 430, 10, TXT3)
    for k in range(6):
        b.tile(96 + k * 344, 200, 320, 180, title=False)
        b.bar(96 + k * 344, 396, 150, 18, TXT1)
        b.bar(96 + k * 344, 428, 200, 10, TXT3)
    b.rule(96, 476, 1728, 3)
    b.bar(96, 496, 340, 24, TXT1)
    b.bar(1474, 500, 350, 10, (150, 150, 150))
    for r in range(2):
        for c in range(10):
            b.tile(96 + c * 174, 540 + r * 253, 158, 237)
    b.outline(96 + 2 * 174, 540, 158, 237)
    b.save("tvwall")


def episodes():
    """503: rows of 174 from y 168; a 256x144 still, code, title, plot; the focused row raised + accent bar."""
    b = Board(503)
    b.header(words=(44, 120, 140, 11, 140))
    for k in range(5):
        y = 168 + k * 174
        if k == 1:
            b.bar(96, y, 1728, 174, RAISED)
            b.accent_bar(96, y, 6, 174)
        b.tile(120, y + 15, 256, 144, title=False)
        b.bar(408, y + 24, 300, 10, TXT3)
        b.bar(408, y + 52, 280, 22, TXT1 if k == 1 else TXT2)
        b.bar(408, y + 96, 1200, 14, TXT2)
        b.bar(408, y + 128, 560, 14, TXT2)
        b.rule(96, y + 172, 1728, 2)
    b.save("episodes")


def posterwall():
    """506 (Medium, gap): 8 across, edge to edge, 2:3 posters; the header gives way while the wall has focus."""
    b = Board(506)
    cw = 1944 / 8
    pw = int(cw - 16)
    ph = int(pw * 1.5)
    for r in range(3):
        for c in range(8):
            x = int(c * cw)
            y = 16 + r * (ph + 16)
            b.tile(x, y, pw, ph)
    b.outline(int(3 * cw), 16 + ph + 16, pw, ph)
    b.save("posterwall")


def listview(music=False):
    """50: rows of 66 from y 200 (96..1176), the focused row raised + accent bar; the item panel at 1264."""
    b = Board(50 + music)
    b.header(title_w=130, words=(110, 77, 55, 66, 121, 11, 110) if music else (88, 143, 110, 11, 120))
    widths = [300, 420, 360, 260, 480, 340, 300, 400, 280, 440, 320]
    for k in range(11):
        y = 200 + k * 66
        if k == 2:
            b.bar(96, y, 1080, 66, RAISED)
            b.accent_bar(96, y, 6, 66)
        b.bar(124, y + 24, widths[k], 16, TXT1 if k == 2 else TXT2)
        b.bar(1060, y + 26, 90, 12, TXT3)
        b.rule(96, y + 64, 1080, 2)
    if music:
        b.tile(1264, 200, 560, 560, TONES[7], title=False)
        top = 790
    else:
        b.tile(1404, 200, 280, 420, TONES[7])
        top = 650
    b.bar(1264, top, 360, 30, TXT1)
    b.bar(1264, top + 50, 300, 12, TXT3)
    for k in range(3):
        b.bar(1264, top + 86 + k * 34, 540 if k < 2 else 300, 12, TXT2)
    b.save("music_list" if music else "list")


def grid():
    """504: 7 columns of 219 squares (pitch 251 x 310) from 96,160, two label lines under each."""
    b = Board(504)
    b.header(title_w=130, words=(110, 77, 55, 66, 121, 11, 110))
    for r in range(3):
        for c in range(7):
            x, y = 96 + c * 251, 160 + r * 310
            if y + 219 > 1080:
                continue
            b.tile(x, y, 219, 219)
            if y + 270 < 1080:
                b.bar(x, y + 236, 150, 16, TXT1)
                b.bar(x, y + 266, 110, 12, TXT3)
    b.outline(96 + 2 * 251, 160, 219, 219)
    b.save("music_grid")


def bigalbum():
    """505: squares of 380 (pitch 408) on y 230, the second chosen at x 504; its details at 504,662."""
    b = Board(505)
    b.header(title_w=130, words=(110, 77, 55, 66, 121, 11, 110))
    for k in range(5):
        b.tile(96 + k * 408, 230, 380, 380, TONES[4] if k == 1 else None, title=False)
    b.outline(504, 230, 380, 380)
    b.bar(96, 668, 120, 10, TXT3)
    b.bar(96, 700, 340, 12, TXT1)
    b.accent_bar(504, 668, 400, 12)
    b.bar(504, 712, 320, 56, TXT1)
    b.bar(504, 800, 300, 22, TXT1)
    b.bar(504, 850, 110, 10, TXT3)
    b.save("music_bigalbum")


def bigstill():
    """501 for episodes: stills 768x432 at y 223 (pitch 792), the focused one at x 450; its text under it at 450."""
    b = Board(511)
    b.header(words=(44, 120, 140, 11, 140))
    for k in range(3):
        b.tile(-342 + k * 792, 223, 768, 432, TONES[2] if k == 1 else None, title=False)
    b.outline(450, 223, 768, 432)
    b.bar(96, 714, 120, 10, TXT3)
    b.bar(96, 744, 140, 12, TXT1)
    b.accent_bar(450, 708, 300, 12)
    b.bar(450, 754, 420, 52, TXT1)
    b.bar(450, 824, 700, 12, TXT3)
    b.bar(450, 862, 1170, 14, TXT2)
    b.bar(450, 896, 220, 14, TXT2)
    b.save("bigstill")


def rows():
    """503 for films / series: rows of 174 from y 168; a 96x144 poster, caption, title, plot; focused row raised."""
    b = Board(513)
    b.header()
    for k in range(5):
        y = 168 + k * 174
        if k == 1:
            b.bar(96, y, 1728, 174, RAISED)
            b.accent_bar(96, y, 6, 174)
        b.tile(120, y + 15, 96, 144, title=False)
        b.bar(248, y + 24, 360, 10, TXT3)
        b.bar(248, y + 52, 320, 22, TXT1 if k == 1 else TXT2)
        b.bar(248, y + 96, 1260, 14, TXT2)
        b.bar(248, y + 128, 600, 14, TXT2)
        b.rule(96, y + 172, 1728, 2)
    b.save("rows")


def stills():
    """507: 4 x 3 cards of 416x234 from 96,168 (pitch 436 x 296), title + mono caption under each."""
    b = Board(507)
    b.header(words=(44, 120, 140, 11, 140))
    for r in range(3):
        for c in range(4):
            x, y = 96 + c * 436, 168 + r * 296
            b.tile(x, y, 416, 234, title=False)
            b.bar(x, y + 246, 220, 16, TXT1)
            b.bar(x, y + 274, 150, 10, TXT3)
    b.outline(96 + 436, 168, 416, 234)
    b.save("stills")


def tracklist():
    """508: a column head at y 160, a rule, rows of 66 from y 198 across the page (96..1824), focused row raised."""
    b = Board(508)
    b.header(title_w=130, words=(110, 77, 55, 66, 121, 11, 110))
    for x, w in ((124, 30), (196, 60), (820, 70), (1224, 60), (1628, 40), (1740, 60)):
        b.bar(x, 166, w, 10, TXT3)
    b.rule(96, 196, 1728, 3)
    widths = [300, 420, 360, 260, 480, 340, 300, 400, 280, 440, 320]
    for k in range(11):
        y = 198 + k * 66
        if k == 2:
            b.bar(96, y, 1728, 66, RAISED)
            b.accent_bar(96, y, 6, 66)
        b.bar(124, y + 26, 30, 12, TXT3)
        b.bar(196, y + 24, widths[k], 16, TXT1 if k == 2 else TXT2)
        b.bar(820, y + 26, widths[(k + 3) % 11] * 2 // 3, 12, TXT2)
        b.bar(1224, y + 26, widths[(k + 6) % 11] * 2 // 3, 12, TXT3)
        b.bar(1628, y + 26, 48, 12, TXT3)
        b.bar(1740, y + 26, 60, 12, TXT3)
        b.rule(96, y + 64, 1728, 2)
    b.save("music_tracklist")


if __name__ == "__main__":
    showcase()
    bigposter()
    tvwall()
    episodes()
    posterwall()
    listview()
    listview(music=True)
    grid()
    bigalbum()
    bigstill()
    rows()
    stills()
    tracklist()
