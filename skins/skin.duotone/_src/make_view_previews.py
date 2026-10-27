"""Schematic view previews for the view picker (Custom_1156_ViewPicker.xml).

    python skins/skin.duotone/_src/make_view_previews.py

Writes media/duotone/views/<view>.png (320 x 180). Each preview is drawn at the real 1920 x 1080 geometry of
the view (numbers copied from Includes_Views_Video.xml / Includes_Views.xml / Includes_Views_Music.xml) and
scaled down, so the layout reads at a glance. No artwork: tiles are neutral grey blocks with a hint of a
title line. The PNGs are greyscale (paper = white, ink = black); the picker tints them with the section
colour (colordiffuse = $VAR[SectionColor]), which turns them into Duotone's one-colour prints.
The Dark look can't get a light print from a near-black multiply, so media/duotone/views/dark/<view>.png is the
same preview inverted onto the Dark palette (dk_sec_paper field, dk_ink marks, read from colors/defaults.xml)
and drawn untinted (the picker's second image, ListItem.Property(dark)).
"""
from pathlib import Path
from PIL import Image, ImageDraw

from theme_tokens import palette, rgba

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "duotone" / "views"
W, H = 1920, 1080
SIZE = (320, 180)
FIELD, INK = 255, 17
TONES = [118, 150, 96, 172, 132, 108, 160, 140, 88, 126]


def canvas():
    im = Image.new("L", (W, H), FIELD)
    return im, ImageDraw.Draw(im)


def tone(i):
    return TONES[i % len(TONES)]


def rule(d, x, y, w, h=8, c=INK):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def bar(d, x, y, w, h, c=INK):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def print_tile(d, x, y, w, h, i, title=True):
    """A poster / thumb print: a grey block, a darker band and a pale title line near the foot."""
    t = tone(i)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=t)
    d.rectangle([x, y + int(h * 0.55), x + w - 1, y + h - 1], fill=max(t - 26, 40))
    if title:
        d.rectangle([x + int(w * 0.12), y + int(h * 0.74), x + int(w * 0.80), y + int(h * 0.74) + max(int(h * 0.05), 10)], fill=min(t + 70, 235))


def frame(d, x, y, w, h, t=8):
    """Duotone focus: an 8 px ink frame just outside the item."""
    d.rectangle([x - t, y - t, x + w + t - 1, y + h + t - 1], outline=INK, width=t)


def header(d, words=True):
    bar(d, 64, 80, 90, 18)                   # caption: section
    bar(d, 186, 80, 130, 18, 90)             # sort
    bar(d, 346, 80, 120, 18)                 # position
    if words:
        for x, w in ((1000, 100), (1130, 190), (1360, 60), (1440, 22)):
            bar(d, x, 80, w, 18)
        bar(d, 1514, 68, 146, 40)            # the view word (focused look)
    bar(d, 1742, 70, 112, 56)                # Anton clock
    rule(d, 64, 136, 1792)


def save(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    small = im.resize(SIZE, Image.LANCZOS)
    ImageDraw.Draw(small).rectangle([0, 0, SIZE[0] - 1, SIZE[1] - 1], outline=INK, width=2)  # the print's ink edge
    small.save(OUT / f"{name}.png", optimize=True)
    print("wrote", OUT / f"{name}.png")
    # Dark: luminance inverted between the Dark field (v = 255) and the Dark ink (v = INK)
    pal = palette()
    field, ink = rgba(pal["dk_sec_paper"])[:3], rgba(pal["dk_ink"])[:3]
    lut = []
    for c in range(3):
        for v in range(256):
            t = min(max((FIELD - v) / (FIELD - INK), 0.0), 1.0)
            lut.append(round(field[c] + t * (ink[c] - field[c])))
    (OUT / "dark").mkdir(exist_ok=True)
    small.convert("RGB").point(lut).save(OUT / "dark" / f"{name}.png", optimize=True)


def wall():
    im, d = canvas()
    header(d)
    bar(d, 64, 168, 470, 190)                # Anton masthead title
    for x in (976, 1280, 1584):              # three numerals
        bar(d, x, 188, 120, 18)
        bar(d, x, 224, 180, 116)
    rule(d, 1248, 188, 8, 170)
    rule(d, 1552, 188, 8, 170)
    bar(d, 64, 380, 240, 20)                 # kicker
    bar(d, 330, 378, 820, 24, 70)            # one-line plot
    rule(d, 64, 424, 1792)
    i = 0
    for r in range(2):
        for c in range(7):
            print_tile(d, 64 + c * 260, 460 + r * 376, 232, 348, i)
            i += 1
    frame(d, 64 + 260, 460, 232, 348)
    save(im, "wall")


def list_view(name, square):
    im, d = canvas()
    header(d)
    for r in range(12):
        y = 176 + r * 72
        if y + 72 > 1040:
            break
        rule(d, 64, y, 1000, 2)
        if r == 2:                           # focused row: ink bar, paper text
            bar(d, 64, y, 1000, 72)
            bar(d, 92, y + 26, 420, 20, FIELD)
            bar(d, 900, y + 28, 130, 16, 200)
        else:
            bar(d, 92, y + 26, 260 + (r * 97) % 300, 20)
            bar(d, 900, y + 28, 130, 16, 120)
    bar(d, 1084, 176, 4, 864, 220)           # scrollbar
    bar(d, 1084, 300, 4, 140)
    rule(d, 1112, 176, 2, 864)
    if square:
        print_tile(d, 1160, 176, 520, 520, 3, title=False)
    else:
        print_tile(d, 1160, 176, 347, 520, 3)
    bar(d, 1160, 716, 520, 64)               # Anton title
    bar(d, 1160, 808, 380, 18, 90)           # caption meta
    for k in range(4):                       # plot
        bar(d, 1160, 852 + k * 32, 680 - (k == 3) * 260, 16, 120)
    save(im, name)


def episodes():
    im, d = canvas()
    header(d)
    bar(d, 64, 180, 300, 18)                 # kicker
    bar(d, 64, 222, 330, 170)                # giant episode numeral
    bar(d, 64, 474, 600, 70)                 # Anton title
    bar(d, 64, 620, 420, 18, 90)             # meta
    for k in range(7):
        bar(d, 64, 668 + k * 34, 660 - (k == 6) * 300, 16, 120)
    rule(d, 772, 176, 8, 840)
    for r in range(6):
        y = 176 + r * 136
        if r == 1:
            bar(d, 824, y, 1032, 136)
            print_tile(d, 840, y + 14, 192, 108, r, title=False)
            bar(d, 1064, y + 30, 70, 44, FIELD)
            bar(d, 1160, y + 34, 420, 22, FIELD)
            bar(d, 1160, y + 72, 300, 16, 200)
        else:
            print_tile(d, 840, y + 14, 192, 108, r, title=False)
            bar(d, 1064, y + 30, 70, 44)
            bar(d, 1160, y + 34, 300 + (r * 83) % 260, 22)
            bar(d, 1160, y + 72, 300, 16, 110)
            rule(d, 824, y + 134, 1032, 2)
    bar(d, 1868, 176, 4, 816, 220)
    bar(d, 1868, 176, 4, 160)
    save(im, "episodes")


def albums():
    im, d = canvas()
    bar(d, 64, 80, 90, 18)                   # MUSIC caption + tabs
    for x, w in ((190, 120), (340, 130), (500, 110), (640, 110), (780, 60), (860, 22), (910, 68)):
        bar(d, x, 80, w, 18, 60)
    bar(d, 64, 164, 240, 18)                 # ARTIST kicker
    bar(d, 64, 190, 760, 170)                # Anton artist
    rule(d, 64, 388, 1032)
    i = 0
    for r in range(3):
        for c in range(5):
            y = 420 + r * 210
            if y + 192 > 1024:
                continue
            print_tile(d, 64 + c * 210, y, 192, 192, i, title=False)
            i += 1
    frame(d, 64 + 210, 420, 192, 192)
    print_tile(d, 1128, 0, 792, 392, 7, title=False)   # artist fanart print
    bar(d, 1160, 64, 176, 72)                # ink clock block
    rule(d, 1120, 0, 8, 400)
    rule(d, 1120, 392, 800)
    bar(d, 1160, 428, 200, 18)               # ALBUM kicker
    bar(d, 1160, 470, 560, 120)              # Anton album
    rule(d, 1160, 612, 696)
    bar(d, 1160, 640, 220, 18, 90)
    for k in range(6):
        y = 672 + k * 42
        bar(d, 1160, y + 10, 40, 22)
        bar(d, 1256, y + 12, 260 + (k * 71) % 180, 18, 60)
        bar(d, 1736, y + 12, 80, 16, 110)
        rule(d, 1160, y + 40, 696, 2, 150)
    save(im, "albums")


# ------------------------------------------------------------ 0.9.16 views (_src/make_views_more.py geometry)
def poster():
    im, d = canvas()
    header(d)
    bar(d, 64, 180, 300, 18)                 # kicker
    bar(d, 64, 236, 900, 172)                # Anton title
    rule(d, 64, 500, 1096)
    for x in (64, 432, 800):                 # three numerals between rules
        bar(d, x, 532, 110, 18)
        bar(d, x, 566, 200, 116)
    rule(d, 400, 528, 8, 160)
    rule(d, 768, 528, 8, 160)
    rule(d, 64, 712, 1096)
    for k in range(6):                       # plot
        bar(d, 64, 748 + k * 34, 1096 - (k == 5) * 420, 16, 120)
    print_tile(d, 1280, 176, 576, 864, 3)    # the print, focused
    frame(d, 1280, 176, 576, 864)
    bar(d, 920, 992, 240, 48)                # pager tab under the plot
    bar(d, 980, 1010, 120, 14, FIELD)
    save(im, "poster")


def screens():
    im, d = canvas()
    header(d)
    i = 0
    for r in range(2):
        for c in range(3):
            x, y = 64 + c * 608, 176 + r * 420
            print_tile(d, x, y, 576, 324, i, title=False)
            bar(d, x, y + 352, 260 + (i * 61) % 200, 28)      # Anton title under the print
            i += 1
    frame(d, 64 + 608, 176, 576, 324)
    save(im, "screens")


def sheet():
    im, d = canvas()
    header(d)
    i = 0
    for r in range(3):
        for c in range(10):
            print_tile(d, 64 + c * 180, 176 + r * 266, 156, 234, i)
            i += 1
    frame(d, 64 + 2 * 180, 176, 156, 234)
    bar(d, 64, 976, 1792, 64)                # ink caption band
    bar(d, 88, 992, 520, 32, FIELD)
    bar(d, 1560, 1000, 270, 16, 170)
    save(im, "sheet")


def stage():
    im, d = canvas()
    bar(d, 64, 80, 90, 18)                   # MUSIC caption + tabs
    for x, w in ((190, 120), (340, 130), (500, 110), (640, 110), (780, 60), (860, 22), (910, 68)):
        bar(d, x, 80, w, 18, 60)
    bar(d, 1742, 70, 112, 56)
    rule(d, 64, 136, 1792)
    print_tile(d, 0, 144, 1920, 512, 5, title=False)   # fanart band
    bar(d, 0, 456, 1152, 200)                # ink name block
    bar(d, 64, 474, 260, 18, 200)
    bar(d, 64, 508, 760, 116, FIELD)         # Anton name
    rule(d, 0, 656, 1920)
    for c in range(8):                       # cover strip
        print_tile(d, 64 + c * 224, 688, 192, 192, c, title=False)
    frame(d, 64 + 224, 688, 192, 192)
    bar(d, 64, 908, 420, 16, 90)
    save(im, "stage")


def tracks():
    im, d = canvas()
    bar(d, 64, 80, 90, 18)
    for x, w in ((190, 120), (340, 130), (500, 110), (640, 110), (780, 60), (860, 22), (910, 68)):
        bar(d, x, 80, w, 18, 60)
    bar(d, 1742, 70, 112, 56)
    rule(d, 64, 136, 1792)
    for r in range(12):
        y = 176 + r * 72
        if r == 3:
            bar(d, 64, y, 1160, 72)
            bar(d, 80, y + 18, 50, 36, 200)
            bar(d, 176, y + 26, 420, 22, FIELD)
            bar(d, 836, y + 28, 220, 16, 200)
            bar(d, 1150, y + 28, 60, 16, FIELD)
        else:
            bar(d, 80, y + 18, 50, 36)
            bar(d, 176, y + 26, 220 + (r * 89) % 300, 22)
            bar(d, 836, y + 28, 200, 16, 110)
            bar(d, 1150, y + 28, 60, 16)
            rule(d, 64, y + 70, 1160, 2)
    rule(d, 1248, 176, 8, 864)
    print_tile(d, 1288, 176, 568, 568, 4, title=False)
    frame(d, 1288, 176, 568, 568)
    bar(d, 1288, 776, 200, 18)
    bar(d, 1288, 808, 420, 48)
    bar(d, 1288, 876, 240, 16, 90)
    save(im, "tracks")


if __name__ == "__main__":
    poster()
    screens()
    sheet()
    stage()
    tracks()
    wall()
    list_view("list", square=False)
    list_view("list_music", square=True)
    episodes()
    albums()
