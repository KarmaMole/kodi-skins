"""Groove (skin.groove) texture + icon generator. Reproducible, no real artwork, both rooms.

  python skins/skin.groove/_src/make_textures.py            -> skins/skin.groove/media/...
  python skins/skin.groove/_src/make_textures.py --list     -> print the file list only

Source of truth for every value: docs/skin.groove/DESIGN.md (§6 glow recipe, §8 textures, "Light room").
Rules:
  - UI chrome is WHITE on transparent and tinted in XML with colordiffuse = a room token ($VAR[...]).
  - Only real materials and the grounds are pre-coloured, and those come in two copies with the SAME base name:
        media/groove/dark/<name>.png   and   media/groove/light/<name>.png
    so XML picks the folder with one variable (e.g. groove/$VAR[Groove_RoomDir]/room.png). Everything outside
    dark/ and light/ is shared by both rooms.
  - Large soft gradients (grounds, radials, ramps) are TPDF-dithered so the Shield's 8-bit GUI shows no banding.
  - 9-slice textures list their border in NINE_SLICE below (copy into <texture border="l,t,r,b">).
Requires: numpy, Pillow, cairosvg (icons).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = Path(__file__).resolve().parent
SKIN = SRC.parent
MEDIA = SKIN / "media"
G = MEDIA / "groove"
SS = 4                                   # supersampling for drawn shapes
RNG = np.random.default_rng(20261021)

# ---------------------------------------------------------------------------------------------- room colours
ROOMS = {
    "dark":  dict(centre=(34, 31, 28), edge=(25, 23, 21), radii=(1250, 820), grain=0.0),     # FF221F1C / FF191715
    "light": dict(centre=(237, 231, 221), edge=(227, 220, 208), radii=(1300, 860), grain=1.2),  # FFEDE7DD / FFE3DCD0
}
WOOD = {   # crate + shelf material per room: dark stained wood / pale birch ply
    "dark":  dict(top=(52, 48, 43), mid=(38, 35, 31), bot=(29, 27, 24), ply=(70, 64, 56), shadow=(0, 0, 0), shadow_a=0.60),
    "light": dict(top=(214, 196, 166), mid=(196, 175, 143), bot=(172, 150, 117), ply=(232, 218, 194), shadow=(74, 59, 44), shadow_a=0.30),
}
SLEEVE_BACK = {"dark": (44, 42, 40), "light": (216, 209, 196)}

NINE_SLICE = {   # file -> border l,t,r,b (design px at 1:1)
    "groove/glow_frame.png": "48,48,48,48",
    "groove/shadow_square.png": "96,60,96,120",
    "groove/shadow_contact.png": "24,16,24,32",
    "groove/spine_edge.png": "3,0,3,0",
    "groove/pill.png": "2,2,2,2",
}
WRITTEN: list[Path] = []


# ---------------------------------------------------------------------------------------------- helpers
def save(img: Image.Image, rel: str):
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)
    WRITTEN.append(p)


def tpdf(shape, amp=1.0):
    return (RNG.random(shape) - RNG.random(shape)) * amp


def white_alpha(alpha: np.ndarray, dither=True) -> Image.Image:
    """White RGB + alpha (0..1), dithered to 8 bits."""
    a = alpha * 255 + (tpdf(alpha.shape) if dither else 0)
    a = np.clip(np.round(a), 0, 255).astype(np.uint8)
    w = np.full(alpha.shape, 255, np.uint8)
    return Image.fromarray(np.dstack([w, w, w, a]), "RGBA")


def rgba(rgb: np.ndarray, alpha: np.ndarray, dither=True) -> Image.Image:
    rgb = rgb + (tpdf(rgb.shape) if dither else 0)
    a = alpha * 255 + (tpdf(alpha.shape) if dither else 0)
    return Image.fromarray(np.dstack([np.clip(np.round(rgb), 0, 255), np.clip(np.round(a), 0, 255)]).astype(np.uint8), "RGBA")


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def radial(size, power=1.0):
    y, x = np.mgrid[0:size, 0:size]
    c = (size - 1) / 2
    d = np.sqrt((x - c) ** 2 + (y - c) ** 2) / (size / 2)
    return smooth(1 - d) ** power


def gauss_rect(w, h, rect, sigma) -> np.ndarray:
    """Alpha of a blurred filled rectangle (x0,y0,x1,y1) on a w x h canvas."""
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle(rect, fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(sigma)), float) / 255


def aa_mask(w, h, draw_fn) -> np.ndarray:
    """Anti-aliased mask: draw at SS x then box-downsample."""
    m = Image.new("L", (w * SS, h * SS), 0)
    draw_fn(ImageDraw.Draw(m), SS)
    return np.asarray(m.resize((w, h), Image.BOX), float) / 255


def grain(shape, amp, blur=0.7, stretch=(1, 1)):
    """Fine fibre/wood grain: blurred noise, optionally stretched along an axis."""
    h, w = shape
    sh, sw = max(1, h // stretch[0]), max(1, w // stretch[1])
    n = ((RNG.normal(0, 1, (sh, sw)) * 40) + 128).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(n).filter(ImageFilter.GaussianBlur(blur)).resize((w, h), Image.BICUBIC)
    return (np.asarray(im, float) - 128) / 40 * amp


# ---------------------------------------------------------------------------------------------- grounds
def grounds():
    """room.png per room: 1280x720 opaque radial (centre -> edge), dithered; light adds paper fibre."""
    W, H = 1280, 720
    y, x = np.mgrid[0:H, 0:W]
    for room, c in ROOMS.items():
        rx, ry = c["radii"][0] / 1.5, c["radii"][1] / 1.5
        d = np.clip(np.sqrt(((x - 640) / rx) ** 2 + ((y - 313) / ry) ** 2), 0, 1) ** 2
        rgb = np.array(c["centre"], float) * (1 - d[..., None]) + np.array(c["edge"], float) * d[..., None]
        if c["grain"]:
            rgb += grain((H, W), c["grain"])[..., None]
        rgb += tpdf(rgb.shape)
        save(Image.fromarray(np.clip(np.round(rgb), 0, 255).astype(np.uint8), "RGB"), f"groove/{room}/room.png")


# ---------------------------------------------------------------------------------------------- light & masks
def light_and_masks():
    save(white_alpha(radial(512, 1.0)), "groove/glow_radial.png")          # pool / halo / tint (tinted in XML)
    save(white_alpha(radial(512, 0.8)), "groove/wash_mask.png")            # diffuse for the full-room wash
    # glow_frame: 9-slice soft frame (64 core, border 48): bloom hugging the item. Dark room only.
    n = 160
    a = gauss_rect(n, n, (48, 48, 111, 111), 16) * 0.9
    a[48:112, 48:112] = 0.9
    save(white_alpha(a), "groove/glow_frame.png")
    # shadow_square: hollow 9-slice drop shadow. Core (= the item) 64x64 at (96,60); shadow = item offset +30 y,
    # CSS blur 60 (sigma 30). The core is punched out so alpha-faded covers never show their own shadow through.
    w, h = 256, 244
    a = gauss_rect(w, h, (96, 90, 159, 153), 30)
    a[60:124, 96:160] = 0
    save(white_alpha(a / max(a.max(), 1e-6)), "groove/shadow_square.png")
    # shadow_contact: tight hollow 9-slice (offset +6, sigma 7) that keeps an edge on pale sleeves (both rooms)
    w, h = 112, 112
    a = gauss_rect(w, h, (24, 22, 87, 85), 7)
    a[16:80, 24:88] = 0
    save(white_alpha(a / max(a.max(), 1e-6)), "groove/shadow_contact.png")
    # shadow_cast: the Light room's coloured shadow (tinted Groove.Color.Main). Drawn at 1.5x the item, centred
    # on the item + 40/620 of its height down. Peak alpha baked at 0.75.
    n = 384
    a = gauss_rect(n, n, (n / 2 - 0.46 * 256, n / 2 - 0.46 * 256, n / 2 + 0.46 * 256, n / 2 + 0.46 * 256), 256 * 0.12)
    save(white_alpha(a / a.max() * 0.75), "groove/shadow_cast.png")
    # shadow_disc: round soft shadow under records / the mini disc (offset is the control's job)
    n = 256
    y, x = np.mgrid[0:n, 0:n]
    m = (np.sqrt((x - 127.5) ** 2 + (y - 127.5) ** 2) <= 100).astype(np.uint8) * 255
    a = np.asarray(Image.fromarray(m).filter(ImageFilter.GaussianBlur(14)), float) / 255
    save(white_alpha(a), "groove/shadow_disc.png")
    # scrim ramps (diffuse masks for "scrims made of the ground"): alpha 1 -> 0 along the axis, smoothstep
    t = smooth(np.linspace(1, 0, 256))
    save(white_alpha(np.tile(t[:, None], (1, 16))), "groove/ramp_v.png")    # opaque at top
    save(white_alpha(np.tile(t[None, :], (16, 1))), "groove/ramp_h.png")    # opaque at left
    # circle mask for disc art, cover labels, hub collage, artist round crops
    save(white_alpha(aa_mask(512, 512, lambda d, s: d.ellipse([0, 0, 512 * s - 1, 512 * s - 1], fill=255)), False),
         "groove/disc_mask.png")
    # small primitives
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "groove/white.png")
    save(white_alpha(aa_mask(16, 16, lambda d, s: d.ellipse([0, 0, 16 * s - 1, 16 * s - 1], fill=255)), False), "groove/dot.png")
    save(white_alpha(aa_mask(8, 4, lambda d, s: d.rounded_rectangle([0, 0, 8 * s - 1, 4 * s - 1], 2 * s, fill=255)), False), "groove/pill.png")


# ---------------------------------------------------------------------------------------------- records
def records():
    size = 1000
    c = size / 2
    y, x = np.mgrid[0:size, 0:size]
    r = np.sqrt((x - c + .5) ** 2 + (y - c + .5) ** 2) / c
    ang = np.arctan2(y - c, x - c)
    base = np.full((size, size), 17.0)
    grooves = np.sin(r * 900) * 1.6 + np.sin(r * 2300 + 1.3) * 1.0
    bands = np.zeros_like(r)
    for rr in (0.52, 0.61, 0.70, 0.78, 0.86, 0.93):            # six track gaps
        bands += np.exp(-((r - rr) / 0.004) ** 2)
    lum = base + grooves * (1 - bands) - bands * 4 + RNG.normal(0, 0.8, r.shape)
    lum = np.where(r > 0.985, 26 + (r - 0.985) * 400, lum)     # rim
    lum = np.where((r < 0.40) & (r > 0.335), 14 + np.sin(r * 300) * 0.5, lum)   # dead wax
    # anti-aliased outer edge and label hole (r <= 0.335 transparent: the cover label sits there)
    edge = np.clip((1.0 - r) * c, 0, 1) * np.clip((r - 0.335) * c, 0, 1)
    rgb = np.stack([lum, lum, lum * 1.03], -1)
    save(rgba(rgb, edge, dither=False), "groove/vinyl.png")
    # sheen: two still wedges of light at -40 and 140 degrees (does not rotate)
    s = np.zeros_like(r)
    for a0 in (math.radians(-40), math.radians(140)):
        d = np.angle(np.exp(1j * (ang - a0)))
        s += np.exp(-(d / 0.30) ** 2)
    s *= np.clip((r - 0.40) / 0.08, 0, 1) * np.clip((0.985 - r) / 0.02, 0, 1)
    s *= 0.22 + 0.10 * np.sin(r * 40)
    save(white_alpha(np.clip(s * 0.85, 0, 1)), "groove/vinyl_sheen.png")
    # spindle: small metal post (real material, both rooms)
    n = 48
    yy, xx = np.mgrid[0:n, 0:n]
    rr = np.sqrt((xx - 23.5) ** 2 + (yy - 23.5) ** 2) / 24
    hl = np.sqrt((xx - 18) ** 2 + (yy - 16) ** 2) / 30
    v = 230 - hl * 150
    a = aa_mask(n, n, lambda d, s_: d.ellipse([0, 0, n * s_ - 1, n * s_ - 1], fill=255))
    save(rgba(np.stack([v, v * 0.985, v * 0.96], -1), a, dither=False), "groove/spindle.png")


def tonearm():
    """Tonearm on one canvas, arm pointing +x from the pivot. Pivot pixel = (PX, PY); stylus tip = (PX + L, PY).
    Rotate it about the pivot (Player.Progress steps). tonearm_shadow.png is the same canvas: tint with the room's
    shadow token and draw it 8 px right / 14 px down of the arm (it shares the rotation)."""
    PX, PY, L = 70, 60, 340
    W, H = PX + L + 30, 120
    canvas = np.zeros((H * SS, W * SS, 4))

    def layer(draw_fn, top_rgb, bot_rgb, y0, y1):
        m = Image.new("L", (W * SS, H * SS), 0)
        draw_fn(ImageDraw.Draw(m))
        a = np.asarray(m, float) / 255
        t = np.clip((np.arange(H * SS)[:, None] - y0 * SS) / max((y1 - y0) * SS, 1), 0, 1)
        rgb = np.array(top_rgb, float) * (1 - t[..., None]) + np.array(bot_rgb, float) * t[..., None]
        rgb = np.broadcast_to(rgb, (H * SS, W * SS, 3))
        canvas[..., :3] = canvas[..., :3] * (1 - a[..., None]) + rgb * a[..., None]
        canvas[..., 3] = canvas[..., 3] * (1 - a) + a

    S = SS
    layer(lambda d: d.rounded_rectangle([(PX - 58) * S, (PY - 7) * S, (PX - 14) * S, (PY + 7) * S], 4 * S, fill=255),
          (207, 202, 195), (141, 135, 128), PY - 7, PY + 7)                                   # counterweight
    layer(lambda d: d.rounded_rectangle([(PX - 14) * S, (PY - 3.5) * S, (PX + L - 36) * S, (PY + 3.5) * S], 4 * S, fill=255),
          (244, 241, 236), (169, 163, 155), PY - 3.5, PY + 3.5)                               # tube

    def head(d):
        cx, cy, w, h, a = PX + L - 21, PY, 50, 22, math.radians(-14)
        pts = []
        for ux, uy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
            pts.append(((cx + ux * math.cos(a) - uy * math.sin(a)) * S, (cy + ux * math.sin(a) + uy * math.cos(a)) * S))
        d.polygon(pts, fill=255)
    layer(head, (233, 229, 223), (143, 138, 131), PY - 14, PY + 14)                           # headshell
    # pivot base: radial metal + dark socket
    yy, xx = np.mgrid[0:H * S, 0:W * S] / S
    rr = np.sqrt((xx - PX) ** 2 + (yy - PY) ** 2)
    base_a = np.clip(30 - rr, 0, 1)
    hl = np.sqrt((xx - (PX - 6)) ** 2 + (yy - (PY - 9)) ** 2) / 30
    v = np.clip(232 - hl * 140, 90, 240)
    for i, k in enumerate((1.0, 0.985, 0.955)):
        canvas[..., i] = canvas[..., i] * (1 - base_a) + v * k * base_a
    canvas[..., 3] = canvas[..., 3] * (1 - base_a) + base_a
    sock = np.clip(12 - rr, 0, 1)
    for i, k in enumerate((43, 41, 38)):
        canvas[..., i] = canvas[..., i] * (1 - sock) + k * sock
    img = Image.fromarray(np.dstack([np.clip(canvas[..., :3], 0, 255), canvas[..., 3:] * 255]).astype(np.uint8), "RGBA")
    img = img.resize((W, H), Image.LANCZOS)
    save(img, "groove/tonearm.png")
    a = np.asarray(img, float)[..., 3] / 255
    sh = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)), float) / 255
    save(white_alpha(sh * 0.9), "groove/tonearm_shadow.png")
    return PX, PY, L


def tonearm_angles(PX, PY, L):
    """Rotation of the arm for the Now Playing geometry in DESIGN (disc centre 810,460, D 580, pivot 1160,210):
    the angle (degrees, screen, clockwise positive) where the stylus meets the outer (0.93 R) and inner (0.42 R)
    groove. Kodi's rotate is counter-clockwise for positive angles, so the XML uses the negated value."""
    cx, cy, R = 810, 460, 290
    px, py = 1160, 210
    out = []
    for rr in (0.93 * R, 0.42 * R):
        d = math.hypot(cx - px, cy - py)
        a = math.atan2(cy - py, cx - px)
        cosb = (L * L + d * d - rr * rr) / (2 * L * d)
        b = math.acos(max(-1, min(1, cosb)))
        out.append(math.degrees(a - b))   # the solution on the pivot's left/upper side of the line (outer arc)
    return out


# ---------------------------------------------------------------------------------------------- crate / shelf / sleeves
def wood_fill(w, h, m: dict, vertical=True):
    t = np.linspace(0, 1, h)[:, None]
    top, mid, bot = (np.array(m[k], float) for k in ("top", "mid", "bot"))
    rgb = np.where(t[..., None] < 0.14, top + (mid - top) * (t[..., None] / 0.14), mid + (bot - mid) * ((t[..., None] - 0.14) / 0.86))
    rgb = np.broadcast_to(rgb, (h, w, 3)).copy()
    g = grain((h, w), 2.2, blur=1.2, stretch=(1, 24))          # long horizontal grain
    g += np.sin(np.linspace(0, 1, h)[:, None] * 90 + grain((h, w), 2.0, blur=6, stretch=(1, 8))) * 1.2
    return rgb + g[..., None]


def crates():
    W, Hf = 1120, 190
    for room, m in WOOD.items():
        # front wall (on top of the records): rounded 4/8, top ply edge, handle cut-out (a real hole)
        rgb = wood_fill(W, Hf, m)
        a = aa_mask(W, Hf, lambda d, s: d.rounded_rectangle([0, 0, W * s - 1, Hf * s - 1], 8 * s, fill=255))
        ply = np.array(m["ply"], float)
        for i, yy in enumerate(range(0, 6)):                    # birch/stained ply edge: thin alternating lines
            rgb[yy] = ply * (0.92 if i % 2 else 1.0)
        rgb[6] *= 0.8
        hole = aa_mask(W, Hf, lambda d, s: d.rounded_rectangle([490 * s, 46 * s, 630 * s, 78 * s], 16 * s, fill=255))
        ring = aa_mask(W, Hf, lambda d, s: d.rounded_rectangle([486 * s, 42 * s, 634 * s, 82 * s], 20 * s, fill=255)) - hole
        rgb *= (1 - ring[..., None] * 0.35)                    # bevel darkening around the hole
        save(rgba(rgb, a * (1 - hole)), f"groove/{room}/crate_front.png")
        # back + side walls (behind the records): canvas origin = crate front's left, back-wall top (210 px higher)
        Hb = 330
        cb = np.zeros((Hb, W, 3))
        ab = np.zeros((Hb, W))
        back = aa_mask(W, Hb, lambda d, s: d.polygon([(175 * s, 0), (945 * s, 0), (945 * s, 150 * s), (175 * s, 150 * s)], fill=255))
        left = aa_mask(W, Hb, lambda d, s: d.polygon([(0, 210 * s), (175 * s, 0), (175 * s, 150 * s), (0, 330 * s)], fill=255))
        right = aa_mask(W, Hb, lambda d, s: d.polygon([(W * s, 210 * s), (945 * s, 0), (945 * s, 150 * s), (W * s, 330 * s)], fill=255))
        wf = wood_fill(W, Hb, m)
        dark = np.array(m["bot"], float) * 0.9
        cb = cb * (1 - back[..., None]) + dark * back[..., None]
        for side in (left, right):
            cb = cb * (1 - side[..., None]) + wf * 0.95 * side[..., None]
        ab = np.clip(back + left + right, 0, 1)
        edge = aa_mask(W, Hb, lambda d, s: (d.line([(0, 210 * s), (175 * s, 0)], fill=255, width=2 * s),
                                             d.line([(W * s, 210 * s), (945 * s, 0)], fill=255, width=2 * s),
                                             d.line([(175 * s, 0), (945 * s, 0)], fill=255, width=2 * s)))
        hi = 1.16 if room == "dark" else 1.08
        cb = cb * (1 - edge[..., None]) + np.clip(cb * hi + 18, 0, 255) * edge[..., None]
        save(rgba(cb, ab), f"groove/{room}/crate_back.png")


def shelves():
    W, P, SH = 1920, 34, 60
    for room, m in WOOD.items():
        rgb = np.zeros((P + SH, W, 3))
        a = np.zeros((P + SH, W))
        rgb[:P] = wood_fill(W, P, m)
        rgb[:2] = np.clip(rgb[:2] * 1.12 + 255 * 0.12 * (0.6 if room == "light" else 1), 0, 255)   # top highlight
        a[:P] = 1
        t = np.linspace(0, 1, SH)
        sh = (1 - smooth(t)) * m["shadow_a"]
        rgb[P:] = np.array(m["shadow"], float)
        a[P:] = sh[:, None]
        save(rgba(rgb, a), f"groove/{room}/shelf.png")


def sleeves():
    n = 400
    for room, c in SLEEVE_BACK.items():
        base = np.array(c, float)
        g = grain((n, n), 3.0, blur=0.8)
        y, x = np.mgrid[0:n, 0:n]
        v = g - (np.abs(x - 200) / 200) ** 3 * (8 if room == "dark" else 10)
        rgb = base[None, None, :] + v[..., None]
        save(Image.fromarray(np.clip(np.round(rgb + tpdf(rgb.shape)), 0, 255).astype(np.uint8), "RGB"), f"groove/{room}/sleeve_back.png")


def spines():
    """Spines are objects: same in both rooms. scrim = black alpha 18 -> 55 -> 18 % across the width (title band);
    edge = 1 px light left, 2 px dark right (9-slice 3,0,3,0)."""
    x = np.linspace(0, 1, 64)
    a = 0.18 + (0.55 - 0.18) * (1 - np.abs(x - 0.5) * 2)
    arr = np.zeros((16, 64, 4), np.uint8)
    arr[..., 3] = np.round(np.tile(a, (16, 1)) * 255)
    save(Image.fromarray(arr, "RGBA"), "groove/spine_scrim.png")
    e = np.zeros((16, 8, 4), np.uint8)
    e[:, 0] = (255, 255, 255, 26)
    e[:, 6:8] = (0, 0, 0, 90)
    save(Image.fromarray(e, "RGBA"), "groove/spine_edge.png")


# ---------------------------------------------------------------------------------------------- wheel + rings
RINGS = {"genre": (162, 352, 0.6), "style": (364, 414, 0.8), "mood": (426, 476, 0.8)}   # r0, r1, gap (deg each side)


def wheel():
    """One 30-degree slice per ring, centred on 0 deg (3 o'clock), cropped to its bounding box.
    Place each image at (wheel_cx + ox, wheel_cy + oy) and rotate about (wheel_cx, wheel_cy). Offsets in WHEEL_OFFSETS.
    _fill = white solid (tint: ring_fill / ring_fill_focus); _edge = 2 px white outline (ring_edge / ring_edge_focus)."""
    offsets = {}
    for name, (r0, r1, gap) in RINGS.items():
        a0, a1 = math.radians(-15 + gap), math.radians(15 - gap)
        xs = [r0 * math.cos(a0), r1, r0 * math.cos(a1)]
        ox = int(math.floor(min(xs))) - 2
        oy = -int(math.ceil(r1 * math.sin(math.radians(15)))) - 2
        w, h = r1 - ox + 3, -oy * 2

        def sector(d, s, inset=0.0):
            pts = []
            for k in range(0, 61):
                a = a0 + (a1 - a0) * k / 60
                pts.append((((r1 - inset) * math.cos(a) - ox) * s, ((r1 - inset) * math.sin(a) - oy) * s))
            for k in range(60, -1, -1):
                a = a0 + (a1 - a0) * k / 60
                pts.append((((r0 + inset) * math.cos(a) - ox) * s, ((r0 + inset) * math.sin(a) - oy) * s))
            d.polygon(pts, fill=255)
        fill = aa_mask(w, h, lambda d, s: sector(d, s))
        # inner outline: fill minus the fill shrunk by 2 px (angular inset approximated by the gap + radial inset)
        inner = aa_mask(w, h, lambda d, s: sector_inset(d, s, r0 + 2, r1 - 2, a0 + 2 / ((r0 + r1) / 2), a1 - 2 / ((r0 + r1) / 2), ox, oy))
        save(white_alpha(fill, False), f"groove/ring_{name}_fill.png")
        save(white_alpha(np.clip(fill - inner, 0, 1), False), f"groove/ring_{name}_edge.png")
        offsets[name] = (ox, oy, w, h)
    # pointer: open chevron pointing left (the notch at 3 o'clock), 2.5 px stroke
    save(white_alpha(aa_mask(32, 40, lambda d, s: d.line([(26 * s, 6 * s), (8 * s, 20 * s), (26 * s, 34 * s)], fill=255, width=int(2.5 * s), joint="curve")), False),
         "groove/wheel_pointer.png")
    return offsets


def sector_inset(d, s, r0, r1, a0, a1, ox, oy):
    pts = []
    for k in range(0, 61):
        a = a0 + (a1 - a0) * k / 60
        pts.append(((r1 * math.cos(a) - ox) * s, (r1 * math.sin(a) - oy) * s))
    for k in range(60, -1, -1):
        a = a0 + (a1 - a0) * k / 60
        pts.append(((r0 * math.cos(a) - ox) * s, (r0 * math.sin(a) - oy) * s))
    d.polygon(pts, fill=255)


# ---------------------------------------------------------------------------------------------- mini player ring
def progress_ring():
    """120 px ring, radius 57, 3 px stroke, round caps, from 12 o'clock clockwise. 000 = empty. track = full circle."""
    n, r, sw = 120, 57, 3

    def arc_img(frac):
        def fn(d, s):
            if frac <= 0:
                return
            box = [(60 - r) * s, (60 - r) * s, (60 + r) * s, (60 + r) * s]
            if frac >= 1:
                d.ellipse(box, outline=255, width=sw * s)
                return
            d.arc(box, -90, -90 + 360 * frac, fill=255, width=sw * s)
            for a in (-90, -90 + 360 * frac):                  # round caps
                rr, rc = sw / 2, r - sw / 2                       # PIL strokes inward: the arc centre line is r - sw/2
                cx, cy = 60 + rc * math.cos(math.radians(a)), 60 + rc * math.sin(math.radians(a))
                d.ellipse([(cx - rr) * s, (cy - rr) * s, (cx + rr) * s, (cy + rr) * s], fill=255)
        return white_alpha(aa_mask(n, n, fn), False)
    save(arc_img(1.0), "groove/progress_ring/track.png")
    for k in range(101):
        save(arc_img(k / 100), f"groove/progress_ring/{k:03d}.png")


# ---------------------------------------------------------------------------------------------- icons
# 96 px copies only where the XML draws icons at 96 (Home's settings row, home_rows.py SETTINGS); QA N4 2026-10-21
ICONS96 = {"addons", "clean", "favourites", "files", "livetv", "pictures", "power", "search", "settings", "skin",
           "system", "update"}


def sizes(name):
    return ((64, "icons"), (96, "icons/96")) if name in ICONS96 else ((64, "icons"),)


def icons():
    import cairosvg
    sys.path.insert(0, str(SRC))
    import icons as IC
    for name in IC.ICONS:
        for size, sub in sizes(name):
            svg = IC.svg(name, size, color="#ffffff")
            p = MEDIA / sub / f"{name}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(p), output_width=size, output_height=size)
            WRITTEN.append(p)


# ---------------------------------------------------------------------------------------------- developer (video lane)
def developer_video():
    """Added by the skin-developer (M3 video / M4 dialogs, 2026-10-21). All white alpha, tinted in XML.
    groove/ramp_v_up.png   opaque at the BOTTOM (scrims over fanart rising from the bottom edge)
    groove/row_focus.png   lit list row: 4 px solid edge at the left + 13 % fill; border 8,0,0,0; tint $VAR[ink]
                           (Dark: 12 % white band + white edge; Light: 12 % ink band + ink edge, reads on paper)
    groove/card_edge.png   2 px hollow outline with a 2 px transparent buffer (LESSONS 4); border 4
    groove/btn_fill.png    square fill for dialog buttons (8 px, kept apart from white.png so it can be restyled)"""
    t = smooth(np.linspace(1, 0, 256))
    save(white_alpha(np.tile(t[::-1][:, None], (1, 16))), "groove/ramp_v_up.png")
    a = np.full((16, 64), 0.13)
    a[:, :4] = 1.0
    save(white_alpha(a, dither=False), "groove/row_focus.png")
    e = np.zeros((16, 16))
    e[:2, :] = e[-2:, :] = e[:, :2] = e[:, -2:] = 1.0
    save(white_alpha(e, dither=False), "groove/card_edge.png")
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "groove/btn_fill.png")
    NINE_SLICE.update({"groove/row_focus.png": "8,0,0,0", "groove/card_edge.png": "4,4,4,4"})
    # three line icons in the set's style (64 grid, live area 8..56, 2 px stroke at 64 / 3 at 96, round caps)
    import cairosvg
    sys.path.insert(0, str(SRC))
    import icons as IC
    rays = " ".join(f"M{32 + 15 * math.cos(math.radians(a)):.2f} {32 + 15 * math.sin(math.radians(a)):.2f} "
                    f"L{32 + 23 * math.cos(math.radians(a)):.2f} {32 + 23 * math.sin(math.radians(a)):.2f}"
                    for a in range(0, 360, 45))
    extra = {
        # gamepad: rounded body, d-pad cross at left, two buttons at right
        "games": '<path d="M18 20 H46 C52 20 56 25 57 32 L58 42 C59 48 52 51 48 46 L44 41 H20 L16 46 C12 51 5 48 6 42 L7 32 C8 25 12 20 18 20 Z"/>'
                 '<path d="M20 26 V36 M15 31 H25"/><circle cx="42" cy="28" r="1.8" fill="#fff" stroke="none"/>'
                 '<circle cx="48" cy="34" r="1.8" fill="#fff" stroke="none"/>',
        # weather: a sun peeking over a cloud
        "weather": '<path d="M22 22 A9 9 0 0 1 39 19 M17 13 L19 15 M30 8 V11 M41 13 L39 15 M12 25 H15"/>'
                   '<path d="M18 50 H46 C52 50 56 46 56 40 C56 34 51 30 45 31 C43 25 38 22 32 22 C24 22 19 28 19 35 C13 35 9 39 9 43 C9 47 13 50 18 50 Z"/>',
        # glow: a lit disc with rays (the light the art gives off)
        "glow": f'<circle cx="32" cy="32" r="9"/><path d="{rays}"/>',
    }
    for name, body in extra.items():
        for size, sub in sizes(name):
            sw = IC.SW * size / 64
            svg = (f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none" stroke="#ffffff" '
                   f'stroke-width="{IC.SW}" stroke-linecap="round" stroke-linejoin="round" '
                   f'xmlns="http://www.w3.org/2000/svg">{body}</svg>')
            p = MEDIA / sub / f"{name}.png"
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(p), output_width=size, output_height=size)
            WRITTEN.append(p)


# ---------------------------------------------------------------------------------------------- developer (music playback lane)
def developer_player():
    """Added by the skin-developer (M3 music playback, 2026-10-21). White alpha, tinted in XML.
    groove/np_track.png   1632x12 fully transparent: the background of the Now Playing playhead `progress` control.
                          Kodi sizes a progress control's caps from the BACKGROUND texture's pixel size (LESSONS
                          Keepsake), so 1632 px drawn at 1632 px puts a 12 px righttexture centred on the fill end.
    groove/dot_12.png     12 px anti-aliased dot (playhead, small marks)"""
    save(Image.new("RGBA", (1632, 12), (255, 255, 255, 0)), "groove/np_track.png")
    # Full-frame diffuse masks for text fades made of the ROOM ITSELF (draw $VAR[Tex_Room] full screen through
    # them): a flat ground-coloured ramp showed as a paler band on the Light room's paper. 960x540 (half scale),
    # alpha 0 everywhere except a smoothstep ramp (opaque at the bottom) in the fade rectangle (x, y, w, h).
    fades = {"fade_liner_review": (760, 403, 680, 67), "fade_liner_bio": (760, 690, 680, 60),
             "fade_liner_reviewlong": (760, 683, 680, 67), "fade_liner_biolong": (760, 648, 680, 72),
             "fade_tracklist": (1000, 986, 824, 94), "fade_biopage": (760, 870, 680, 120)}
    for name, (x, y, w, h) in fades.items():
        a = np.zeros((540, 960))
        x0, y0, x1, y1 = x // 2, y // 2, (x + w) // 2, min((y + h) // 2, 540)
        a[y0:y1, x0:x1] = smooth(np.linspace(0, 1, y1 - y0))[:, None]
        save(white_alpha(a, dither=False), f"groove/{name}.png")
    save(white_alpha(aa_mask(12, 12, lambda d, s: d.ellipse([0, 0, 12 * s - 1, 12 * s - 1], fill=255)), False),
         "groove/dot_12.png")


# ---------------------------------------------------------------------------------------------- developer (music library lane)
def developer_music():
    """Added by the skin-developer (M2 music library, 2026-10-21). White alpha, tinted / used as diffuse in XML.
    groove/disc_q_tl|tr|bl|br.png  one quarter of a disc each (256 px, the circle's centre in the opposite corner):
                                   `diffuse` masks for the Wheel hub's 2x2 cover collage (four 150 px covers = one disc)
    groove/ring_84.png             84 px circle outline, 2 px (Wheel's Play mix / Albums buttons); tint ink / rim"""
    S = 256
    corners = {"tl": (S, S), "tr": (0, S), "bl": (S, 0), "br": (0, 0)}
    for name, (cx, cy) in corners.items():
        save(white_alpha(aa_mask(S, S, lambda d, s, cx=cx, cy=cy: d.ellipse(
            [(cx - S) * s, (cy - S) * s, (cx + S) * s - 1, (cy + S) * s - 1], fill=255)), False), f"groove/disc_q_{name}.png")
    save(white_alpha(aa_mask(84, 84, lambda d, s: d.ellipse([1 * s, 1 * s, 83 * s - 1, 83 * s - 1], outline=255, width=2 * s)),
                     False), "groove/ring_84.png")


# ---------------------------------------------------------------------------------------------- main
def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    grounds()
    light_and_masks()
    records()
    px, py, L = tonearm()
    crates()
    shelves()
    sleeves()
    spines()
    offs = wheel()
    progress_ring()
    icons()
    developer_video()
    developer_player()
    developer_music()
    total =sum(p.stat().st_size for p in WRITTEN)
    rel = sorted(str(p.relative_to(MEDIA)).replace("\\", "/") for p in WRITTEN)
    singles = [r for r in rel if "/progress_ring/" not in r and not r.startswith("icons/")]
    print("\n".join(singles))
    print(f"groove/progress_ring/: track.png + 000..100.png ({sum('/progress_ring/' in r for r in rel)} files)")
    print(f"icons/<name>.png (64) + icons/96/<name>.png: {sum(r.startswith('icons/') for r in rel)} files")
    print(f"\n{len(rel)} files, {total / 1024:.0f} KB")
    print("\n9-slice borders:", NINE_SLICE)
    print("tonearm pivot px:", (px, py), "stylus tip px:", (px + L, py))
    print("tonearm angles (screen deg, outer -> inner groove):", [round(a, 1) for a in tonearm_angles(px, py, L)])
    print("wheel slice offsets (ox, oy, w, h) from the wheel centre:", offs)


if __name__ == "__main__":
    if "--list" in sys.argv:
        print(__doc__)
    else:
        main()
