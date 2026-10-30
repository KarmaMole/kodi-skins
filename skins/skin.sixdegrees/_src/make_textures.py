"""Six Degrees textures -> ../media/sd/*.png (+ the engine textures Majan's windows reference by name).

Everything is drawn 4x supersampled and downsampled with LANCZOS. Shapes are WHITE with alpha, so one
texture serves every line colour through colordiffuse (brief, mechanic 6). Multi-colour art (compass,
wordmark) is baked in colour. Geometry is taken from the mockup generator
(docs/concepts/round4/mockups/sixdegrees/gen.py, boards.py, boards2.py): line width 8, rounded bends r 26.

    python skins/skin.sixdegrees/_src/make_textures.py
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
SD = MEDIA / "sd"
SS = 4  # supersampling

INK = (21, 22, 26)
RED, BLUE, VIO, GRN, ROUTE = (232, 73, 47), (45, 91, 216), (138, 79, 214), (31, 157, 87), (140, 142, 148)
GROUND = (244, 244, 241)
WHITE = (255, 255, 255)


def canvas(w, h, mode="RGBA", fill=(255, 255, 255, 0)):
    return Image.new(mode, (w * SS, h * SS), fill)


def down(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


# Drawn below but named by no XML (removed from media/ 2026-10-30): never written again.
UNUSED = {
    "sd/icon_i.png", "sd/mask_120x180.png", "sd/mask_160x240.png", "sd/mask_200x300.png", "sd/mask_240x360.png",
    "sd/mask_320x180.png", "sd/pill_36.png", "sd/pill_36_o3.png", "sd/pill_40_o3.png", "sd/pill_46_o3.png",
    "sd/pill_66_ring.png", "sd/ring_20_6.png", "sd/rr16.png", "sd/rr16_o2.png", "sd/rr16_o3.png", "sd/rr20_o2.png",
    "sd/rr20_o3.png", "sd/rr8.png", "sd/rr8_o2.png", "sd/rr8_o3.png", "sd/tri_down.png", "sd/tri_up.png"
}


def save(im, rel):
    if rel in UNUSED:
        return
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p, optimize=True)


def white_alpha(mask: Image.Image) -> Image.Image:
    """L mask -> white RGBA with that alpha."""
    out = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    out.putalpha(mask)
    return out


# ------------------------------------------------------------------ primitives
def rrect_mask(w, h, r, inset=0.0):
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    i = inset * SS
    d.rounded_rectangle([i, i, w * SS - 1 - i, h * SS - 1 - i], radius=max(0, r * SS - i), fill=255)
    return m


def rrect(w, h, r):
    return white_alpha(down(rrect_mask(w, h, r), w, h))


def rrect_outline(w, h, r, stroke):
    outer = rrect_mask(w, h, r)
    inner = Image.new("L", outer.size, 0)
    d = ImageDraw.Draw(inner)
    s = stroke * SS
    d.rounded_rectangle([s, s, w * SS - 1 - s, h * SS - 1 - s], radius=max(0, (r - stroke) * SS), fill=255)
    m = Image.composite(Image.new("L", outer.size, 0), outer, inner)
    return white_alpha(down(m, w, h))


def disc(d, pad=0):
    n = d + 2 * pad
    m = Image.new("L", (n * SS, n * SS), 0)
    ImageDraw.Draw(m).ellipse([pad * SS, pad * SS, (pad + d) * SS - 1, (pad + d) * SS - 1], fill=255)
    return white_alpha(down(m, n, n))


def ring(d, stroke, pad=0):
    n = d + 2 * pad
    m = Image.new("L", (n * SS, n * SS), 0)
    dr = ImageDraw.Draw(m)
    dr.ellipse([pad * SS, pad * SS, (pad + d) * SS - 1, (pad + d) * SS - 1], fill=255)
    s = stroke
    dr.ellipse([(pad + s) * SS, (pad + s) * SS, (pad + d - s) * SS - 1, (pad + d - s) * SS - 1], fill=0)
    return white_alpha(down(m, n, n))


def shadow_box(w, h, r, blur, alpha, oy=0, pad=None):
    """Soft drop shadow 9-slice source: a rounded rect blurred; returns (image, pad)."""
    pad = pad or blur * 3
    W, H = w + 2 * pad, h + 2 * pad
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad + oy, pad + w - 1, pad + h - 1 + oy], radius=r, fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    out.putalpha(m)
    return out, pad


def stroke_path(pts, w, size, r=26, cap=True):
    """Thick polyline with rounded (quadratic) corners, as an L mask at SS. pts in px (unscaled)."""
    W, H = size
    m = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(m)
    samples = []
    for i in range(len(pts)):
        if i == 0:
            samples.append(pts[0])
            continue
        if i == len(pts) - 1:
            samples.append(pts[-1])
            continue
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr = min(r, l1 / 2, l2 / 2)
        ax, ay = x1 - (x1 - x0) / l1 * rr, y1 - (y1 - y0) / l1 * rr
        bx, by = x1 + (x2 - x1) / l2 * rr, y1 + (y2 - y1) / l2 * rr
        samples.append((ax, ay))
        for k in range(1, 24):
            t = k / 24
            qx = (1 - t) ** 2 * ax + 2 * (1 - t) * t * x1 + t * t * bx
            qy = (1 - t) ** 2 * ay + 2 * (1 - t) * t * y1 + t * t * by
            samples.append((qx, qy))
        samples.append((bx, by))
    # dense resample + stamp discs (round joins/caps)
    rad = w * SS / 2
    for (xa, ya), (xb, yb) in zip(samples, samples[1:]):
        L = math.hypot(xb - xa, yb - ya)
        n = max(1, int(L * 2))
        for k in range(n + 1):
            t = k / n
            x, y = (xa + (xb - xa) * t) * SS, (ya + (yb - ya) * t) * SS
            d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=255)
    return m


def tri(size, direction, box=None, color=255):
    """Filled triangle pointing up/right/down/left inside size x size (L mask at SS)."""
    m = Image.new("L", (size * SS, size * SS), 0)
    d = ImageDraw.Draw(m)
    s = size * SS
    b = box or (0.30, 0.70)
    lo, hi = b[0] * s, b[1] * s
    mid = s / 2
    if direction == "up":
        p = [(mid, lo), (hi, hi - s * 0.04), (lo, hi - s * 0.04)]
    elif direction == "down":
        p = [(lo, lo + s * 0.04), (hi, lo + s * 0.04), (mid, hi)]
    elif direction == "right":
        p = [(lo + s * 0.04, lo), (hi, mid), (lo + s * 0.04, hi)]
    else:
        p = [(hi - s * 0.04, lo), (hi - s * 0.04, hi), (lo, mid)]
    d.polygon(p, fill=color)
    return m


# ------------------------------------------------------------------ map lines
# Map geometry (boards.py): centre poster 810,292 300x450.
CONNECTORS = {
    # name: (polyline in screen px, bounding box x0,y0,x1,y1 to cut)
    "up": ([(870, 296), (870, 252), (808, 190), (780, 190)], (772, 182, 878, 300)),
    "left": ([(814, 524), (772, 524), (706, 590), (680, 590)], (672, 516, 818, 598)),
    "down": ([(1052, 738), (1052, 858), (1114, 920), (1140, 920)], (1044, 734, 1148, 928)),
}


def make_connectors():
    for name, (pts, (x0, y0, x1, y1)) in CONNECTORS.items():
        w, h = x1 - x0, y1 - y0
        local = [(x - x0, y - y0) for x, y in pts]
        m = stroke_path(local, 8, (w, h))
        save(white_alpha(down(m, w, h)), f"sd/conn_{name}.png")
        print(f"conn_{name}: left {x0} top {y0} {w}x{h}")


def make_lines():
    # straight segments: 8 px (map), 6 px (route bar, mini map, OSD); round caps; 9-slice border = h/2
    for h in (8, 6):
        m = rrect_mask(32, h, h / 2)
        save(white_alpha(down(m, 32, h)), f"sd/line_h{h}.png")
        m = rrect_mask(h, 32, h / 2)
        save(white_alpha(down(m, h, 32)), f"sd/line_v{h}.png")
    # terminus tick (perpendicular, k = w * 1.9 each side): 8 x 38 vertical bar, round caps
    save(white_alpha(down(rrect_mask(8, 38, 4), 8, 38)), "sd/tick_v8.png")
    save(white_alpha(down(rrect_mask(6, 30, 3), 6, 30)), "sd/tick_v6.png")


def make_underline():
    # 0.9.18 custom menu words: the active word's 6 px underline as the nofocus texture of a disabled auto-width
    # button with textoffsetx 22 (Home top bar). 80 x 12: the line runs x 22-58 on rows 6-11 with round caps; the
    # 9-slice border 25,0,25,0 keeps the caps and the 22 px insets, so the line is exactly as wide as the text.
    m = Image.new("L", (80 * SS, 12 * SS), 0)
    m.paste(rrect_mask(36, 6, 3), (22 * SS, 6 * SS))
    save(white_alpha(down(m, 80, 12)), "sd/uline_22.png")


# ------------------------------------------------------------------ mini map (Home preview, boards2.py)
def make_station_conns():
    """Station page: four lines leave the poster as a bundle and peel off to their rows (boards2.py)."""
    for i, tx in enumerate((264, 250, 236, 222)):
        ry = 782 + 70 * i
        x0, y0 = tx - 6, 677
        W, H = 82, ry + 6 - y0
        pts = [(tx - x0, 681 - y0), (tx - x0, ry - 46 - y0), (tx + 46 - x0, ry - y0), (tx + 76 - x0, ry - y0)]
        m = stroke_path(pts, 8, (W, H), r=14)
        save(white_alpha(down(m, W, H)), f"sd/st_conn_{i}.png")


def make_minimap():
    cx, top, w, h = 1380, 790, 100, 150
    # red: (cx-30,top)->(cx-30,top-16)->(cx-52,top-38)->(1004,top-38) : connector part only
    pieces = {
        "mm_up": ([(cx - 30, top + 4), (cx - 30, top - 16), (cx - 52, top - 38), (cx - 72, top - 38)], (cx - 78, top - 44, cx - 24, top + 8)),
        "mm_left": ([(cx - w / 2 + 4, top + 96), (cx - w / 2 - 14, top + 96), (cx - w / 2 - 38, top + 120), (cx - w / 2 - 56, top + 120)],
                    (cx - w // 2 - 62, top + 90, cx - w // 2 + 8, top + 126)),
        "mm_down": ([(cx + 30, top + h - 4), (cx + 30, top + h + 10), (cx + 54, top + h + 34), (cx + 74, top + h + 34)],
                    (cx + 24, top + h - 8, cx + 80, top + h + 40)),
    }
    for name, (pts, (x0, y0, x1, y1)) in pieces.items():
        W, H = int(x1 - x0), int(y1 - y0)
        local = [(x - x0, y - y0) for x, y in pts]
        m = stroke_path(local, 6, (W, H), r=12)
        save(white_alpha(down(m, W, H)), f"sd/{name}.png")
        print(f"{name}: left {x0} top {y0} {W}x{H}")


# ------------------------------------------------------------------ stations
def make_stations():
    # dot station: d 26, ring 7 (white fill drawn by disc). pad 3 so AA isn't clipped.
    for d, s in ((26, 7), (18, 5), (24, 6), (22, 6), (32, 8), (20, 6), (34, 8)):
        save(ring(d, s, pad=3), f"sd/ring_{d}_{s}.png")
    for d in (14, 16, 18, 20, 22, 24, 26, 32, 34, 104, 120):
        save(disc(d, pad=3), f"sd/disc_{d}.png")
    # roundel shadow (box-shadow 0 14px 30px .25) for a d 120 disc
    sh, pad = shadow_box(120, 120, 60, 15, 0.30, oy=14, pad=48)
    save(sh, "sd/shadow_roundel.png")  # 216 x 216, disc at pad 48
    # circle mask for a poster roundel (diffuse)
    save(disc(94), "sd/mask_circle.png")
    # xdot: white disc 22 with a 14 inner (tint) + shadow
    sh, pad = shadow_box(22, 22, 11, 2, 0.35, oy=1, pad=6)
    save(sh, "sd/shadow_xdot.png")


# ------------------------------------------------------------------ posters, rings, frames
def make_posters():
    # poster masks (diffuse): rounded 7 at the line size, 8 for the centre, 5 for the mini map
    for (w, h, r) in ((110, 165, 7), (164, 246, 7), (184, 276, 7), (224, 336, 7), (300, 450, 8),
                      (330, 495, 8), (100, 150, 5), (240, 360, 7), (160, 240, 7), (120, 180, 6),
                      (200, 300, 7), (280, 280, 8), (180, 180, 7), (320, 180, 8), (560, 315, 10), (400, 225, 8), (1040, 585, 14)):
        save(rrect(w, h, r), f"sd/mask_{w}x{h}.png")
    # poster frame on a line (CSS outline 3-4px, offset 0): outer radius r+4 -> 9-slice border 14
    save(rrect_outline(40, 40, 11, 4), "sd/frame_o4.png")
    save(rrect_outline(40, 40, 10, 3), "sd/frame_o3.png")
    # focus ring around a focused poster: 6 px ink, outer radius 15+? (gen: border-radius 15 on a box
    # = poster + 2*(gap 7 + ring 6)); 9-slice 48x48 border 20
    save(rrect_outline(48, 48, 19, 6), "sd/ringf_6.png")
    save(rrect_outline(48, 48, 19, 7), "sd/ringf_7.png")
    save(rrect(48, 48, 19), "sd/ringf_fill.png")
    # interchange ring around the centre: 8 px ink, radius 20, box = poster + 2*14 (gap 6)
    save(rrect_outline(56, 56, 22, 8), "sd/ring_centre.png")
    save(rrect(56, 56, 22), "sd/ring_centre_fill.png")
    # 6 px variant for the mini map (radius 13)
    save(rrect_outline(40, 40, 13, 6), "sd/ring_mini.png")
    # poster shadow: 0 2px 3px .14, 0 10px 22px .16 (approximated by one blur) for a 100x150 rect
    sh, pad = shadow_box(100, 150, 8, 9, 0.30, oy=8, pad=32)
    save(sh, "sd/shadow_poster.png")  # 9-slice border 48
    # big soft shadow for the centre / focus rings (0 24px 60px .22)
    sh, pad = shadow_box(200, 300, 20, 22, 0.30, oy=22, pad=72)
    save(sh, "sd/shadow_big.png")  # 9-slice border 110
    # card shadow for dialogs
    sh, pad = shadow_box(200, 200, 20, 18, 0.22, oy=14, pad=60)
    save(sh, "sd/shadow_card.png")  # border 90


# ------------------------------------------------------------------ pills, keys, badges
def make_pills():
    # 9-slice pills: border = h/2 (Kodi stretches the middle)
    for h in (46, 64, 56, 48, 40, 36):
        save(rrect(h * 2, h, h / 2), f"sd/pill_{h}.png")
        save(rrect_outline(h * 2, h, h / 2, 3), f"sd/pill_{h}_o3.png")
    # focused Play: ring 4 px at offset 5 around a 64 pill -> box 82, radius 41
    save(rrect_outline(164, 82, 41, 4), "sd/pill_82_ring.png")
    save(rrect_outline(132, 66, 33, 4), "sd/pill_66_ring.png")
    save(rrect_outline(152, 76, 38, 4), "sd/pill_76_ring.png")
    # rounded rows / cards
    for r in (8, 12, 16, 20):
        save(rrect(r * 4, r * 4, r), f"sd/rr{r}.png")
        save(rrect_outline(r * 4, r * 4, r, 2), f"sd/rr{r}_o2.png")
        save(rrect_outline(r * 4, r * 4, r, 3), f"sd/rr{r}_o3.png")
    # key caps (gen.py .key): 2 px ink border, radius 9, height 36
    save(rrect_outline(36, 36, 9, 2), "sd/key.png")  # 9-slice border 12


def make_station_pill():
    """Library header "Options" pill (library panel, 0.9.8): a station roundel at the left of a 46 px pill.
    Focused = ink pill with the roundel cut out (the paper shows through as a white ring); unfocused = the ring
    alone. 9-slice border h,0,h/2,0 keeps the roundel unscaled. White + alpha (tint with colordiffuse ink)."""
    for h, ro, ri in ((46, 12, 6), (36, 10, 5)):
        w = h * 3
        cx = cy = h / 2
        fill = rrect_mask(w, h, h / 2)
        hole = Image.new("L", fill.size, 0)
        dr = ImageDraw.Draw(hole)
        dr.ellipse([(cx - ro) * SS, (cy - ro) * SS, (cx + ro) * SS - 1, (cy + ro) * SS - 1], fill=255)
        dr.ellipse([(cx - ri) * SS, (cy - ri) * SS, (cx + ri) * SS - 1, (cy + ri) * SS - 1], fill=0)
        on = Image.composite(Image.new("L", fill.size, 0), fill, hole)
        save(white_alpha(down(on, w, h)), f"sd/pill_station_{h}.png")
        save(white_alpha(down(hole, w, h)), f"sd/pill_station_{h}_off.png")


def make_badges():
    # badge: disc d 34 with a knocked-out triangle (one texture per direction, tinted by line colour)
    for n in (34, 28, 24):
        for dname in ("up", "down", "left", "right"):
            m = Image.new("L", (n * SS, n * SS), 0)
            ImageDraw.Draw(m).ellipse([0, 0, n * SS - 1, n * SS - 1], fill=255)
            t = tri(n, dname, box=(0.33, 0.67))
            m = Image.composite(Image.new("L", m.size, 0), m, t)
            save(white_alpha(down(m, n, n)), f"sd/badge_{n}_{dname}.png")
    # plain triangles (white) for key caps / play icon
    for dname in ("up", "down", "left", "right"):
        save(white_alpha(down(tri(32, dname, box=(0.18, 0.82)), 32, 32)), f"sd/tri_{dname}.png")
    # star (rating), 5 points
    n = 32
    m = Image.new("L", (n * SS, n * SS), 0)
    cx = cy = n * SS / 2
    R, r = n * SS * 0.48, n * SS * 0.20
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rad = R if k % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a) + n * SS * 0.03))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    save(white_alpha(down(m, n, n)), "sd/star.png")
    # "visited" hook arrow (U+21A9 look): an arc + arrow head
    n = 32
    m = Image.new("L", (n * SS, n * SS), 0)
    d = ImageDraw.Draw(m)
    s = SS
    d.arc([10 * s, 6 * s, 28 * s, 22 * s], start=-90, end=90, fill=255, width=3 * s)
    d.line([12 * s, 22 * s, 19 * s, 22 * s], fill=255, width=3 * s)
    d.line([19 * s, 6 * s, 9 * s, 6 * s], fill=255, width=3 * s)
    d.polygon([(4 * s, 6 * s), (11 * s, 1 * s), (11 * s, 11 * s)], fill=255)
    save(white_alpha(down(m, n, n)), "sd/visited.png")
    # info "i"
    n = 32
    m = Image.new("L", (n * SS, n * SS), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([13.5 * SS, 5 * SS, 18.5 * SS, 10 * SS], fill=255)
    d.rounded_rectangle([13.8 * SS, 12 * SS, 18.2 * SS, 27 * SS], radius=2 * SS, fill=255)
    save(white_alpha(down(m, n, n)), "sd/icon_i.png")


# ------------------------------------------------------------------ colour art
def make_colour_art():
    # wordmark glyph (gen.py wordmark): 44x44
    n = 44
    im = Image.new("RGBA", (n * SS, n * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def ln(x1, y1, x2, y2, col, w=6):
        rad = w * SS / 2
        steps = 40
        for k in range(steps + 1):
            t = k / steps
            x, y = (x1 + (x2 - x1) * t) * SS, (y1 + (y2 - y1) * t) * SS
            d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col + (255,))
    ln(22, 3, 22, 14, RED)
    ln(30, 22, 41, 22, BLUE)
    ln(22, 30, 22, 41, GRN)
    ln(3, 22, 14, 22, VIO)
    r_o, r_i = 10.5 * SS, 5.5 * SS
    c = 22 * SS
    d.ellipse([c - r_o, c - r_o, c + r_o, c + r_o], fill=INK + (255,))
    d.ellipse([c - r_i, c - r_i, c + r_i, c + r_i], fill=WHITE + (255,))
    save(im.resize((n, n), Image.LANCZOS), "sd/wordmark.png")
    # big version for the add-on icon / settings
    # compass (map key): 140x140
    n = 140
    im = Image.new("RGBA", (n * SS, n * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def ln2(x1, y1, x2, y2, col, w=8):
        rad = w * SS / 2
        for k in range(81):
            t = k / 80
            x, y = (x1 + (x2 - x1) * t) * SS, (y1 + (y2 - y1) * t) * SS
            d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col + (255,))
    ln2(70, 8, 70, 50, RED)
    ln2(90, 70, 132, 70, BLUE)
    ln2(70, 90, 70, 132, GRN)
    ln2(8, 70, 50, 70, VIO)
    c = 70 * SS
    ro, ri = 18.5 * SS, 11.5 * SS
    d.ellipse([c - ro, c - ro, c + ro, c + ro], fill=INK + (255,))
    d.ellipse([c - ri, c - ri, c + ri, c + ri], fill=WHITE + (255,))
    save(im.resize((n, n), Image.LANCZOS), "sd/compass.png")


# ------------------------------------------------------------------ engine textures (names Majan's XML uses)
def make_osd():
    """Colour textures for the OSD line (two-tone, not tinted): the 'now' ring and a chapter stop."""
    for name, d, ring_w, pad in (("osd_now", 30, 8, 5), ("osd_stop", 16, 4, 3)):
        n = d + 2 * pad
        im = Image.new("RGBA", (n * SS, n * SS), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.ellipse([pad * SS, pad * SS, (pad + d) * SS - 1, (pad + d) * SS - 1], fill=INK + (255,))
        r = ring_w
        dr.ellipse([(pad + r) * SS, (pad + r) * SS, (pad + d - r) * SS - 1, (pad + d - r) * SS - 1], fill=WHITE + (255,))
        save(im.resize((n, n), Image.LANCZOS), f"sd/{name}.png")
    save(Image.new("RGBA", (4, 40), (255, 255, 255, 0)), "sd/clear40.png")


def make_markers():
    """Poster markers (colour, not tinted): watched = a filled grey stop with a white check; unwatched = nothing."""
    n = 28
    im = Image.new("RGBA", (n * SS, n * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, n * SS - 1, n * SS - 1], fill=(255, 255, 255, 255))
    i = 3 * SS
    d.ellipse([i, i, n * SS - 1 - i, n * SS - 1 - i], fill=ROUTE + (255,))
    w = int(2.6 * SS)
    d.line([(8.5 * SS, 14.5 * SS), (12.5 * SS, 18.5 * SS), (20 * SS, 10 * SS)], fill=(255, 255, 255, 255), width=w, joint="curve")
    im = im.resize((n, n), Image.LANCZOS)
    for name in ("markers/watched.png", "markers/watched_round.png"):
        save(im, name)
    blank = Image.new("RGBA", (4, 4), (255, 255, 255, 0))
    for name in ("markers/unwatched.png", "markers/unwatched_round.png"):
        save(blank, name)


def make_engine():
    # focus frames (Majan's names; grown -13 px around the item: gap 7 + ring 6)
    for name, st in (("focus/outline_2.png", 6), ("focus/outline_2_round.png", 6),
                     ("focus/outline_3.png", 7), ("focus/outline_3_round.png", 7)):
        save(rrect_outline(48, 48, 19, st), name)
    # buttons / rows
    save(rrect(32, 32, 10), "common/rect_round8.png")
    save(rrect(32, 32, 10), "common/rect_square.png")
    save(rrect_outline(32, 32, 10, 2), "common/rect_outline_1_round8.png")
    save(rrect_outline(32, 32, 10, 2), "common/rect_outline_1.png")
    # dialog panel: white card (9-slice border 20)
    save(rrect(48, 48, 20), "dialogs/panel_framed.png")


def main():
    SD.mkdir(parents=True, exist_ok=True)
    make_lines()
    make_underline()
    make_connectors()
    make_minimap()
    make_station_conns()
    make_stations()
    make_posters()
    make_pills()
    make_station_pill()
    make_badges()
    make_colour_art()
    make_engine()
    make_osd()
    make_markers()
    print("done:", len(list(SD.glob('*.png'))), "files in media/sd")


if __name__ == "__main__":
    main()
