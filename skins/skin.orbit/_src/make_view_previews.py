"""Schematic previews of Orbit's library views for the view picker (Custom_1161_ViewPicker.xml).

Run:  python skins/skin.orbit/_src/make_view_previews.py   ->  media/views/*.png (320x180)
(make_textures.py keeps media/views/ when it wipes media/, and runs this script at the end.)

No screenshots and no artwork (GPL skin, Kodi's official repository). Every preview is drawn from the
views' real geometry, scaled 1920x1080 -> 320x180:
  arc        view 500   make_arc.GEOM["lib"] slots (posters on the library circle) + info block + rings
  grid       view 501   panel 40,224, 230 x 352 cells, 196 x 294 posters (Includes_Views_Video.xml)
  episodes   view 502   dial list rows (make_arc.dial_list_slots) + episode panel at 1000,236
  list       view 50    dial list rows + item panel at 1080,236 (Includes_Views.xml)
  music_arc  view 504   make_arc.GEOM["libsq"] squares + the record dial at 940,360
  music_grid view 505   panel 40,224, 262 x 262 cells, 214 squares
  music_list view 50    dial list rows + a square cover in the item panel
Ground: Orbit's own pre-rendered navy grounds (media/ground/*.png) and engraved arcs (media/rings/),
neutral blue-grey placeholder tiles with a hint of a title line, focus in Orbit's language (white
corner brackets, the amber lens tick, amber values). Drawn at 4x and downsampled.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
OUT = MEDIA / "views"
sys.path.insert(0, str(HERE))
import make_arc as A  # noqa: E402  (geometry only; importing does not write anything)

W, H = 320, 180
SS = 4
CW, CH = W * SS, H * SS
K = CW / 1920.0

TEXT = (233, 237, 243)
TEXT2 = (139, 149, 167)
DIM = (86, 96, 117)
LINE = (43, 50, 64)
ACCENT = (255, 181, 71)
TILES = [(38, 50, 78), (46, 58, 88), (32, 42, 66), (54, 66, 96), (42, 52, 80), (28, 38, 60)]
FOCUS = (120, 134, 166)


def c(v):
    return v * K


def ground(name):
    img = Image.open(MEDIA / "ground" / f"{name}.png").convert("RGBA").resize((CW, CH), Image.LANCZOS)
    return img


def layer():
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay)


def comp(img, lay):
    img.alpha_composite(lay)


def texture(img, rel, x, y, w, h, alpha=1.0):
    t = Image.open(MEDIA / rel).convert("RGBA").resize((max(1, round(c(w))), max(1, round(c(h)))), Image.LANCZOS)
    if alpha < 1:
        a = t.getchannel("A").point(lambda v: round(v * alpha))
        t.putalpha(a)
    img.alpha_composite(t, (round(c(x)), round(c(y))))


def bar(d, x, y, w, h, col, a=1.0):
    d.rounded_rectangle([c(x), c(y), c(x + w), c(y + h)], radius=c(h / 2), fill=col + (round(255 * a),))


def header(img, title_w=220):
    lay, d = layer()
    bar(d, 66, 62, title_w, 26, TEXT, 0.95)          # MOVIES (wide caps)
    bar(d, 66, 110, 200, 22, TEXT2, 0.8)             # 0004 / 997
    bar(d, 1730, 62, 126, 34, TEXT, 0.95)            # clock
    bar(d, 1466, 114, 390, 16, TEXT2, 0.6)           # date . weather
    comp(img, lay)


def option_bar(img, widths=(168, 298, 276, 220, 44)):
    lay, d = layer()
    x = 52
    for i, w in enumerate(widths):
        col = TEXT if i == 0 else LINE
        if i == 0:
            d.rounded_rectangle([c(x), c(1000), c(x + w), c(1040)], radius=c(20), fill=TEXT + (235,))
        else:
            d.rounded_rectangle([c(x), c(1000), c(x + w), c(1040)], radius=c(20), outline=LINE + (255,), width=max(2, round(c(2))))
        x += w + 12
    comp(img, lay)


def poster(w, h, col, title=True, radius=4):
    t = Image.new("RGBA", (max(2, round(c(w))), max(2, round(c(h)))), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.rounded_rectangle([0, 0, t.width - 1, t.height - 1], radius=c(radius), fill=col + (255,))
    if title:
        lc = tuple(min(255, v + 40) for v in col)
        d.rectangle([t.width * 0.16, t.height * 0.80, t.width * 0.84, t.height * 0.80 + max(2, t.height * 0.035)], fill=lc + (255,))
    return t


def place(img, tile, cx, cy, rot=0.0):
    if abs(rot) > 0.01:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(tile, (round(c(cx) - tile.width / 2), round(c(cy) - tile.height / 2)))


def brackets(img, x, y, w, h, out=12, arm=30):
    lay, d = layer()
    x0, y0, x1, y1 = x - out, y - out, x + w + out, y + h + out
    lw = max(2, round(c(4)))
    for (px, py, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([c(px), c(py), c(px + sx * arm), c(py)], fill=TEXT + (255,), width=lw)
        d.line([c(px), c(py), c(px), c(py + sy * arm)], fill=TEXT + (255,), width=lw)
    comp(img, lay)


def ring(img, x, y, S, sweep):
    lay, d = layer()
    lw = max(2, round(c(6)))
    d.ellipse([c(x), c(y), c(x + S), c(y + S)], outline=LINE + (255,), width=lw)
    d.arc([c(x), c(y), c(x + S), c(y + S)], start=-90, end=-90 + 360 * sweep, fill=ACCENT + (255,), width=lw)
    bar(d, x + S * 0.3, y + S * 0.42, S * 0.4, S * 0.16, TEXT, 0.9)
    comp(img, lay)


def info_block(img, top=236, width=900, plot_lines=3):
    lay, d = layer()
    bar(d, 64, top, 300, 18, TEXT2, 0.8)                # genres
    bar(d, 64, top + 42, 560, 54, TEXT, 0.95)           # wide title
    bar(d, 64, top + 120, 420, 18, TEXT2, 0.7)          # year . rating . people
    for i in range(plot_lines):
        bar(d, 64, top + 166 + i * 36, width * (0.92 if i < plot_lines - 1 else 0.6), 18, TEXT2, 0.55)
    comp(img, lay)


def arc_view(name, geom, aspect_sq=False, record=False):
    img = ground("arc")
    texture(img, "rings/lib_arc.png", 1090, 0, 830, 1080)
    header(img)
    g = A.GEOM[geom]
    slots = A.arc_slots(g["cx"], g["cy"], g["R"], g["F"], g["H"], g["aspect"], g["extra_h"], g["gap"])
    rnd = random.Random(len(name))
    lens = slots[0]
    if record:
        texture(img, "music/vinyl.png", 940, 360, 360, 360)
    for k in (5, -5, 4, -4, 3, -3, 2, -2, 1, -1):
        x, y, w, h, rot = slots[k]
        b = A.B[abs(k)]
        base = rnd.choice(TILES)
        col = tuple(round(v * (0.55 + 0.45 * b)) for v in base)
        place(img, poster(w, h, col, title=abs(k) <= 2), x, y, rot)
    x, y, w, h, rot = lens
    place(img, poster(w, h, FOCUS), x, y, rot)
    brackets(img, x - w / 2, y - h / 2, w, h, out=14)
    info_block(img, plot_lines=3)
    for i, S in enumerate((200, 200, 200)):
        if record and i:
            break
        ring(img, 64 + i * 320, 636, S, (0.76, 0.45, 0.3)[i])
    option_bar(img, (232, 238, 232, 150, 276, 200) if record else (168, 298, 276, 220, 44))
    save(img, name)


def grid_view(name, cell_w, cell_h, art_w, art_h, cols):
    img = ground("page")
    header(img)
    lay, d = layer()
    bar(d, 64, 172, 420, 32, TEXT, 0.95)
    bar(d, 508, 180, 220, 20, TEXT2, 0.7)
    comp(img, lay)
    rnd = random.Random(cell_h)
    focus = (0, 2)
    rows = 3
    for r in range(rows):
        for col in range(cols):
            x = 40 + col * cell_w + 24
            y = 224 + r * cell_h + 24
            if y + art_h > 980 + art_h * 0.6:
                continue
            if (r, col) == focus:
                continue
            t = poster(art_w, art_h, tuple(round(v * 0.69) for v in rnd.choice(TILES)))
            if y + art_h > 980:   # the panel clips the partial row
                t = t.crop((0, 0, t.width, max(1, round(c(980 - y)))))
            img.alpha_composite(t, (round(c(x)), round(c(y))))
    r, col = focus
    x = 40 + col * cell_w + 24
    y = 224 + r * cell_h + 24
    zw, zh = art_w * 1.06, art_h * 1.06
    zx, zy = x - (zw - art_w) / 2, y - (zh - art_h) / 2
    img.alpha_composite(poster(zw, zh, FOCUS), (round(c(zx)), round(c(zy))))
    brackets(img, zx, zy, zw, zh, out=12)
    option_bar(img)
    save(img, name)


def dial_rows(img, focus_w=360):
    texture(img, "rings/dial_list.png", 0, 0, 320, 1080)
    slots = A.dial_list_slots(-760, 540, 960, [84, 70, 62, 58, 56])
    rnd = random.Random(7)
    for k in range(-5, 6):
        x, y, rot = slots[k]
        font, h, b = A.DL_FONTS[abs(k)]
        w = focus_w if k == 0 else rnd.uniform(170, 330) * (0.8 + 0.2 * b)
        bh = h * 0.42
        t = Image.new("RGBA", (round(c(w)) + 4, max(2, round(c(bh)))), (0, 0, 0, 0))
        dd = ImageDraw.Draw(t)
        dd.rounded_rectangle([0, 0, t.width - 1, t.height - 1], radius=t.height / 2,
                             fill=TEXT + (round(255 * (1.0 if k == 0 else b)),))
        # rows rotate about their left end (the generator rotates the row group about x, y)
        t2 = t.rotate(rot, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(t2, (round(c(x)), round(c(y) - t2.height / 2)))
    lay, d = layer()
    d.rectangle([c(200 - 64), c(540 - 2), c(200 - 24), c(540 + 2)], fill=ACCENT + (255,))   # lens tick
    comp(img, lay)


def episodes_view():
    img = ground("list")
    header(img)
    dial_rows(img)
    rnd = random.Random(3)
    img.alpha_composite(poster(560, 315, rnd.choice(TILES), title=False), (round(c(1000)), round(c(236))))
    lay, d = layer()
    bar(d, 1596, 240, 180, 30, TEXT, 0.95)       # S01E04
    bar(d, 1596, 296, 140, 16, TEXT2, 0.7)
    bar(d, 1596, 326, 200, 18, TEXT2, 0.6)
    bar(d, 1000, 590, 520, 34, TEXT, 0.95)       # title
    bar(d, 1000, 674, 800, 16, TEXT2, 0.55)
    bar(d, 1000, 708, 560, 16, TEXT2, 0.55)
    comp(img, lay)
    for i in range(3):
        ring(img, 1000 + i * 300, 764, 180, (0.7, 0.42, 0.25)[i])
    option_bar(img, (168, 298, 276, 220, 44))
    save(img, "episodes.png")


def list_view(name, square=False):
    img = ground("list")
    header(img)
    dial_rows(img)
    rnd = random.Random(11)
    if square:
        img.alpha_composite(poster(400, 400, rnd.choice(TILES)), (round(c(1080)), round(c(236))))
    else:
        img.alpha_composite(poster(267, 400, rnd.choice(TILES)), (round(c(1080)), round(c(236))))
    lay, d = layer()
    bar(d, 1080, 676, 460, 40, TEXT, 0.95)       # wide title
    bar(d, 1080, 740, 380, 18, TEXT2, 0.7)       # year . min . rating
    for i in range(3):
        bar(d, 1080, 790 + i * 38, 776 * (0.95 if i < 2 else 0.6), 18, TEXT2, 0.55)
    comp(img, lay)
    option_bar(img, (232, 238, 232, 150, 276) if square else (168, 298, 276, 220, 44))
    save(img, name)


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    out.save(OUT / name, optimize=True)
    print(f"  media/views/{name}  {W}x{H}")


def main():
    arc_view("arc.png", "lib")
    grid_view("grid.png", 230, 352, 196, 294, 8)
    episodes_view()
    list_view("list.png")
    arc_view("music_arc.png", "libsq", record=True)
    grid_view("music_grid.png", 262, 262, 214, 214, 7)
    list_view("music_list.png", square=True)


if __name__ == "__main__":
    main()
