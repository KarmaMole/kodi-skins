"""Keepsake textures (reproducible). Started from docs/concepts/round4/mockups/keepsake/make_textures.py.

Writes media/ks/*:
  paper_spread.jpg   the open album (fibre paper, gutter shadow, page curvature, leaf edges), 1920x1080
  paper_card.png     a loose album leaf for dialogs (fibre, deckled shadow edge; 9-slice border 40)
  print.png          white print fill with a 3 px transparent margin (bilinear-smoothed edges when rotated), 9-slice 12
  print_mask.png     photo mask with a 1 px feathered edge (diffuse= on photos so rotated edges stay smooth)
  shadow_s/m/l.png   soft print shadows, 9-slice (rest / lifted / big lifted); min sizes in the names' comments
  corner.png         black photo corner (top-left; flipx/flipy for the others), 72 px drawn at 46 / 38 / 30
  tape.png           washi tape strip (white-alpha, tint with `tape`)
  tape_row.png       tape strip for focused rows, 9-slice border 0,24 (torn ends)
  sheen.png          print gloss overlay
  stamp_shade.png    radial darkening behind the date stamp (bottom-right of a photo)
  stamp_haze.png     soft glow blob behind the stamp digits (tint stamp_haze)
  pen_line.png       hand-drawn underline (focus mark), 420x30
  pen_line_s.png     short underline for small words, 200x22
  pen_box.png        hand-drawn pen frame, 9-slice border 36
  pen_box_info.png   the info page's history box at its mockup size (760x190)
  pen_fill.png       pen stroke for progress fills (stretched)
  pen_tick.png       pen tick at the end of a progress fill (righttexture)
  dots_h.png / dots_v.png  dotted rules at native size (aspectratio center clips them to any length)
  erase.png          soft paper-coloured blob that "erases" the gutter behind month words
  pen_arrow.png      curved arrow (note -> print)
  instant.png        square instant-photo fill (thicker bottom margin), 9-slice
Run: python skins/skin.keepsake/_src/make_textures.py   (writes a contact sheet to _src/previews/)
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "ks"
PREV = HERE / "previews"
rnd = random.Random(16)
W, H = 1920, 1080


def noise(w, h, scale, seed):
    r = np.random.default_rng(seed)
    small = r.random((max(2, h // scale), max(2, w // scale)))
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255


def fibres(w, h, n, seed, lo=18, hi=46):
    r = random.Random(seed)
    fib = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(fib)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        a = r.uniform(0, math.pi)
        L = r.uniform(6, 34)
        pts = []
        for t in range(8):
            a += r.uniform(-.35, .35)
            x += math.cos(a) * L / 8
            y += math.sin(a) * L / 8
            pts.append((x, y))
        d.line(pts, fill=r.randint(lo, hi), width=1)
    return fib.filter(ImageFilter.GaussianBlur(.6))


def paper_base(w, h, seed):
    base = np.array([0x12, 0x11, 0x10], np.float32)
    lum = (noise(w, h, 240, seed) - .5) * 5 + (noise(w, h, 60, seed + 1) - .5) * 3 + (noise(w, h, 8, seed + 2) - .5) * 2.4
    lum = lum + np.random.default_rng(seed + 3).normal(0, 1.6, (h, w))
    img = np.clip(base[None, None, :] + lum[..., None], 0, 255)
    im = Image.fromarray(img.astype(np.uint8))
    fib = fibres(w, h, int(5200 * w * h / (W * H)), seed + 4)
    light = Image.new("RGB", (w, h), (84, 79, 72))
    return Image.composite(light, im, fib)


def paper_spread():
    im = paper_base(W, H, 1)
    xs = np.arange(W, dtype=np.float32)
    ys = np.arange(H, dtype=np.float32)
    dx = np.abs(xs - W / 2)
    gut = 1 - .62 * np.exp(-(dx / 34) ** 2) - .22 * np.exp(-(dx / 150) ** 2)
    gut += .10 * np.exp(-((dx - 58) / 22) ** 2)
    edge = 1 - .30 * np.clip((dx - 700) / 260, 0, 1) ** 2
    vy = 1 - .28 * (np.abs(ys - H / 2) / (H / 2)) ** 3
    shade = gut[None, :] * edge[None, :] * vy[:, None]
    arr = np.asarray(im, np.float32) * shade[..., None]
    for side in (0, 1):
        for i in range(7):
            x = (i * 3 + 2) if side == 0 else W - 1 - (i * 3 + 2)
            arr[:, x, :] = np.clip(arr[:, x, :] + 14 - i * 1.6, 0, 255)
        sl = slice(0, 24) if side == 0 else slice(W - 24, W)
        arr[:, sl, :] *= .72
    # TPDF dither before quantising (LESSONS: big dark gradients band otherwise)
    rng = np.random.default_rng(9)
    arr = arr + rng.random(arr.shape) - rng.random(arr.shape)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT / "paper_spread.jpg", quality=92)
    # a flat single page for full-screen windows that are not a spread (OSD panels, settings)
    single = np.asarray(paper_base(W, H, 31), np.float32)
    vy2 = 1 - .22 * (np.abs(ys - H / 2) / (H / 2)) ** 3
    hx = 1 - .18 * (np.abs(xs - W / 2) / (W / 2)) ** 2
    single = single * (vy2[:, None] * hx[None, :])[..., None]
    single = single + rng.random(single.shape) - rng.random(single.shape)
    Image.fromarray(np.clip(single, 0, 255).astype(np.uint8)).save(OUT / "paper_page.jpg", quality=92)


def paper_card():
    """A loose leaf: fibre paper with a soft dark shadow margin (9-slice border 40, content inset 40)."""
    w, h, m = 720, 520, 40
    leaf = paper_base(w - 2 * m, h - 2 * m, 51).convert("RGBA")
    arr = np.asarray(leaf, np.float32)
    arr[..., :3] *= 1.08  # a touch lighter than the page so the card reads
    leaf = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    sh = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sh).rectangle([m - 6, m + 2, w - m + 6, h - m + 14], fill=210)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 0), sh)
    out.paste(leaf, (m, m))
    # 1 px lighter edge (paper edge catching light)
    d = ImageDraw.Draw(out)
    d.rectangle([m, m, w - m - 1, h - m - 1], outline=(58, 55, 51, 255))
    out.save(OUT / "paper_card.png")


def print_fill():
    """White print fill, 3 px transparent margin + 1 px soft edge (9-slice border 12)."""
    S = 4
    n = 48
    im = Image.new("L", (n * S, n * S), 0)
    ImageDraw.Draw(im).rectangle([3 * S, 3 * S, (n - 3) * S - 1, (n - 3) * S - 1], fill=255)
    a = im.resize((n, n), Image.LANCZOS)
    out = Image.merge("RGBA", [Image.new("L", (n, n), 255)] * 3 + [a])
    out.save(OUT / "print.png")
    # instant-photo frame: same edge, used with a thicker bottom by placing the photo higher
    out.save(OUT / "instant.png")


def print_mask():
    """Diffuse mask for photos: opaque with a 1 px feathered edge at 1024 x 1024 (stretched, ~0.5 px on screen)."""
    n = 1024
    a = np.ones((n, n), np.float32)
    for i, v in enumerate((0.0, 0.5)):
        a[i, :] = np.minimum(a[i, :], v)
        a[n - 1 - i, :] = np.minimum(a[n - 1 - i, :], v)
        a[:, i] = np.minimum(a[:, i], v)
        a[:, n - 1 - i] = np.minimum(a[:, n - 1 - i], v)
    out = np.dstack([np.full((n, n), 255, np.uint8)] * 3 + [(a * 255).astype(np.uint8)])
    Image.fromarray(out, "RGBA").save(OUT / "print_mask.png")


def shadow(name, w, h, inset, blur, dy, alpha):
    """Soft shadow around a w x h print placed inset px from every side (9-slice border = inset + 12)."""
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).rectangle([inset, inset + dy, w - inset, h - inset + dy], fill=int(255 * alpha))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    out = Image.merge("RGBA", [Image.new("L", (w, h), 0)] * 3 + [im])
    out.save(OUT / name)


def corner():
    S = 4
    n = 72 * S
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    leg = 66 * S
    sh = Image.new("L", (n, n), 0)
    ImageDraw.Draw(sh).polygon([(3 * S, 3 * S), (leg + 3 * S, 3 * S), (3 * S, leg + 3 * S)], fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(3 * S))
    im.paste(Image.new("RGBA", (n, n), (0, 0, 0, 255)), (0, 0), sh)
    body = Image.new("L", (n, n), 0)
    ImageDraw.Draw(body).polygon([(0, 0), (leg, 0), (0, leg)], fill=255)
    g = np.zeros((n, n, 4), np.uint8)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    t = np.clip((xx + yy) / leg, 0, 1)
    c = 16 + 22 * t ** 2
    g[..., 0] = c
    g[..., 1] = c * .97
    g[..., 2] = c * .93
    g[..., 3] = 255
    im.paste(Image.fromarray(g, "RGBA"), (0, 0), body)
    d = ImageDraw.Draw(im)
    d.line([(leg - 2 * S, 2 * S), (2 * S, leg - 2 * S)], fill=(92, 88, 82, 255), width=int(1.6 * S))
    d.line([(leg - 9 * S, 2 * S), (2 * S, leg - 9 * S)], fill=(8, 8, 8, 200), width=int(1.2 * S))
    im.resize((72, 72), Image.LANCZOS).save(OUT / "corner.png")


def tape(name, w, h, seed, ragged=10):
    r = random.Random(seed)
    S = 2
    a = Image.new("L", (w * S, h * S), 0)
    left = [(r.uniform(0, ragged) * S, y * S) for y in range(0, h + 1, 4)]
    right = [((w - r.uniform(0, ragged)) * S, y * S) for y in range(h, -1, -4)]
    ImageDraw.Draw(a).polygon(left + right, fill=255)
    a = a.resize((w, h), Image.LANCZOS)
    al = np.asarray(a, np.float32) / 255
    streak = np.asarray(Image.fromarray((noise(w, 4, 3, seed + 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
    fib = noise(w, h, 3, seed + 2) - .5
    alpha = al * (0.66 + .10 * streak + .08 * fib)
    lum = 255 + fib * 18
    out = np.dstack([np.clip(lum, 0, 255)] * 3 + [np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(OUT / name)


def sheen():
    n = 512
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    t = (xx * .8 + (1 - yy) * .6)
    band = np.exp(-((t - .62) / .16) ** 2) * .20 + np.exp(-((t - .30) / .05) ** 2) * .06
    top = np.clip(1 - yy * 2.2, 0, 1) * .05
    a = np.clip((band + top) * 255, 0, 255).astype(np.uint8)
    Image.fromarray(np.dstack([np.full((n, n), 255, np.uint8)] * 3 + [a]), "RGBA").save(OUT / "sheen.png")


def stamp_shade():
    """CSS: radial-gradient(ellipse at 100% 100%, rgba(0,0,0,.58), .26 at 42 %, 0 at 74 %), drawn over 60 % x 55 %."""
    w, h = 256, 160
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rx = (w - xx) / w
    ry = (h - yy) / h
    r = np.sqrt(rx ** 2 + ry ** 2) / math.sqrt(2) * 1.414  # ellipse at the corner, farthest-corner sizing
    a = np.interp(r, [0, .42, .78, 2], [.70, .34, 0, 0])
    Image.fromarray(np.dstack([np.zeros((h, w), np.uint8)] * 3 + [(a * 255).astype(np.uint8)]), "RGBA").save(OUT / "stamp_shade.png")


def stamp_haze():
    w, h = 256, 96
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).rounded_rectangle([40, 30, w - 40, h - 30], radius=16, fill=255)
    im = im.filter(ImageFilter.GaussianBlur(14))
    Image.merge("RGBA", [Image.new("L", (w, h), 255)] * 3 + [im]).save(OUT / "stamp_haze.png")


def pen_stroke(d, x0, y0, x1, y1, w0, wob, seed, S, fill=(255, 255, 255, 255)):
    r = random.Random(seed)
    steps = max(8, int(math.hypot(x1 - x0, y1 - y0) / (6 * S)))
    ph = r.uniform(0, 6.28)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        nx, ny = -(y1 - y0), (x1 - x0)
        ln = math.hypot(nx, ny) or 1
        off = math.sin(t * 3.1 + ph) * wob * S + r.uniform(-.25, .25) * S
        pts.append((x0 + (x1 - x0) * t + nx / ln * off, y0 + (y1 - y0) * t + ny / ln * off, t))
    for (xa, ya, ta), (xb, yb, tb) in zip(pts, pts[1:]):
        taper = min(1, ta * 6, (1 - ta) * 5 + .25)
        wd = max(1, w0 * S * (.45 + .55 * taper))
        d.line([(xa, ya), (xb, yb)], fill=fill, width=int(wd))
        d.ellipse([xb - wd / 2, yb - wd / 2, xb + wd / 2, yb + wd / 2], fill=fill)


def pen_line(name="pen_line.png", w=420, h=30, width=3.2, wob=2.2, seed=3):
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pen_stroke(d, 6 * S, 18 * S, (w - 10) * S, 12 * S, width, wob, seed, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / name)


def pen_under():
    """Focus underline for pen words as a 9-slice (border 0,0,0,30): transparent body, stroke in the bottom 30 px."""
    S = 3
    w, h = 420, 90
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pen_stroke(d, 4 * S, 76 * S, (w - 6) * S, 71 * S, 3.0, 1.8, 7, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / "pen_under.png")


def pen_box(w, h, name, seed, m=10):
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = [(m, m + 3), (w - m, m), (w - m + 2, h - m), (m - 1, h - m + 2)]
    for i in range(4):
        (xa, ya), (xb, yb) = c[i], c[(i + 1) % 4]
        dx, dy = xb - xa, yb - ya
        L = math.hypot(dx, dy)
        ox, oy = dx / L * 9, dy / L * 9
        pen_stroke(d, (xa - ox * .4) * S, (ya - oy * .4) * S, (xb + ox) * S, (yb + oy) * S, 2.2, 1.4, seed + i, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / name)


def pen_fill():
    """Progress fill: a firm pen stroke, horizontal, 600x28 (stretched to the fill width)."""
    S = 3
    w, h = 600, 28
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pen_stroke(d, 2 * S, 15 * S, (w - 2) * S, 14 * S, 3.4, 1.0, 31, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / "pen_fill.png")
    # tick (righttexture): a short vertical pen mark, 10x28
    im = Image.new("RGBA", (10 * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pen_stroke(d, 6 * S, 5 * S, 4 * S, 24 * S, 2.6, .4, 40, S)
    im.resize((10, h), Image.LANCZOS).save(OUT / "pen_tick.png")
    # transparent progress background: Kodi sizes the fill and the end tick from the background TEXTURE's
    # width (GUIProgressControl::UpdateLayout), so an empty texturebg breaks the layout
    # one per control width: the caps are scaled by control width / bg texture width, so the bg must be 1:1
    for cw in (170, 210, 290, 740, 1686):  # 350 / 510 / 1090 dropped 2026-10-30: no control that width any more
        Image.new("RGBA", (cw, h), (255, 255, 255, 0)).save(OUT / f"progress_bg_{cw}.png")


def dots():
    """Dotted rules at native size: 9 px pitch, 2.6 px dots (mockup radial-gradient 1.3 px / 9 px)."""
    S = 4
    w, h = 2000, 4
    im = Image.new("L", (w * S, h * S), 0)
    d = ImageDraw.Draw(im)
    for x in range(4, w, 9):
        d.ellipse([(x - 1.3) * S, (2 - 1.3) * S, (x + 1.3) * S, (2 + 1.3) * S], fill=255)
    a = im.resize((w, h), Image.LANCZOS)
    Image.merge("RGBA", [Image.new("L", (w, h), 255)] * 3 + [a]).save(OUT / "dots_h.png")
    Image.merge("RGBA", [Image.new("L", (h, w), 255)] * 3 + [a.transpose(Image.Transpose.ROTATE_90)]).save(OUT / "dots_v.png")


def erase():
    w, h = 400, 100
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).rounded_rectangle([60, 22, w - 60, h - 22], radius=20, fill=255)
    im = im.filter(ImageFilter.GaussianBlur(10))
    Image.merge("RGBA", [Image.new("L", (w, h), 255)] * 3 + [im]).save(OUT / "erase.png")


def pen_arrow():
    S = 3
    w, h = 90, 70
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    for i in range(25):
        t = i / 24
        x = 80 - 66 * t
        y = 62 - 52 * t + math.sin(t * math.pi) * -14
        pts.append((x * S, y * S))
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        d.line([(xa, ya), (xb, yb)], fill=(255, 255, 255, 255), width=int(2.6 * S))
    tip = pts[-1]
    pen_stroke(d, tip[0], tip[1], tip[0] + 18 * S, tip[1] + 2 * S, 2.6, .3, 51, S)
    pen_stroke(d, tip[0], tip[1], tip[0] + 2 * S, tip[1] + 18 * S, 2.6, .3, 52, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / "pen_arrow.png")


def pen_arrow_right():
    """A short straight pen arrow (LCD "now -> ends"), 48 x 20."""
    S = 3
    w, h = 48, 20
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pen_stroke(d, 3 * S, 10 * S, 44 * S, 10 * S, 2.6, .5, 81, S)
    pen_stroke(d, 44 * S, 10 * S, 35 * S, 3 * S, 2.4, .2, 82, S)
    pen_stroke(d, 44 * S, 10 * S, 35 * S, 17 * S, 2.4, .2, 83, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / "pen_arrow_r.png")


def pen_check():
    """A hand-drawn tick for selected rows (white, tint as needed)."""
    S = 3
    w = h = 40
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pen_stroke(d, 6 * S, 22 * S, 15 * S, 32 * S, 3.6, .3, 61, S)
    pen_stroke(d, 15 * S, 32 * S, 35 * S, 7 * S, 3.6, .6, 62, S)
    im.resize((w, h), Image.LANCZOS).save(OUT / "pen_check.png")


def pen_dot():
    S = 4
    n = 24
    im = Image.new("RGBA", (n * S, n * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([5 * S, 5 * S, 19 * S, 19 * S], fill=(255, 255, 255, 255))
    im.resize((n, n), Image.LANCZOS).save(OUT / "pen_dot.png")


def pen_circle():
    """A loose pen ring (radio 'on' / current item), 48 px."""
    S = 3
    n = 48
    im = Image.new("RGBA", (n * S, n * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = random.Random(71)
    pts = []
    for i in range(60):
        t = i / 52 * 2 * math.pi
        rr = 18 + math.sin(t * 1.3) * 1.2 + r.uniform(-.3, .3)
        pts.append((24 * S + math.cos(t - .6) * rr * S, 24 * S + math.sin(t - .6) * rr * S * .92))
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        d.line([(xa, ya), (xb, yb)], fill=(255, 255, 255, 255), width=int(2.6 * S))
    im.resize((n, n), Image.LANCZOS).save(OUT / "pen_circle.png")


def top_masks():
    """Diary: masks that reveal a patch of the page over the item hanging above the top slot (left / right page).
    480 x 270 = the screen at 1/4; opaque above y 360 (soft to 384), left page x < 1040, right page x > 880."""
    w, h = 480, 270
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) * 4
    vert = np.clip((384 - yy) / 24, 0, 1)
    for name, horiz in (("mask_top_left.png", np.clip((1040 - xx) / 16, 0, 1)),
                        ("mask_top_right.png", np.clip((xx - 880) / 16, 0, 1))):
        a = (vert * horiz * 255).astype(np.uint8)
        Image.merge("RGBA", [Image.new("L", (w, h), 255)] * 3 + [Image.fromarray(a)]).save(OUT / name)


def contact():
    PREV.mkdir(exist_ok=True)
    files = sorted(p for p in OUT.iterdir() if p.suffix == ".png")
    sheet = Image.new("RGB", (1600, 140 * ((len(files) + 3) // 4)), (40, 38, 36))
    for i, p in enumerate(files):
        im = Image.open(p).convert("RGBA")
        im.thumbnail((380, 120))
        x, y = (i % 4) * 400 + 10, (i // 4) * 140 + 10
        sheet.paste(im, (x, y), im)
        ImageDraw.Draw(sheet).text((x, y + 122), p.name, fill=(200, 200, 200))
    sheet.save(PREV / "contact.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    paper_spread()
    paper_card()
    print_fill()
    print_mask()
    shadow("shadow_s.png", 96, 96, 24, 7, 4, .55)    # rest: 9-slice border 32 (print >= 64 px)
    shadow("shadow_m.png", 160, 160, 40, 14, 10, .6)  # lifted: border 52 (print >= 104 px)
    shadow("shadow_l.png", 256, 256, 64, 26, 22, .72)  # big lifted: border 84 (print >= 168 px)
    corner()
    tape("tape.png", 300, 78, 16)
    tape("tape_row.png", 600, 64, 17, ragged=8)
    sheen()
    stamp_shade()
    stamp_haze()
    pen_line()
    pen_under()
    pen_box(240, 160, "pen_box.png", 21, m=10)
    pen_box(760, 190, "pen_box_info.png", 21)
    pen_fill()
    dots()
    erase()
    pen_arrow()
    pen_check()
    pen_arrow_right()
    pen_dot()
    pen_circle()
    top_masks()
    contact()
    print("ok", len(list(OUT.iterdir())), "files")
