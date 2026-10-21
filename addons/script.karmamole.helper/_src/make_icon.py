"""icon.png (512x512, solid RGB) and fanart.jpg (1920x1080) for script.karmamole.helper.
Run: python tools/script.karmamole.helper/_src/make_icon.py   (Pillow + numpy; _src/ is not shipped)

The KarmaMole Skin Helper reads colours out of the art for KarmaMole's skins, so its mark is a colour reader: a
thin-line ring of twelve 30-degree slices in the dark room, each slice lit in a different art colour (the hue circle,
starting from the amber of Groove's first icon at 3 o'clock), the ring's own blurred light washing the room, and a
plain grooved hub (no label art, no skin's motif). Same family as the Groove icon (dark room, hairline ring, glow,
TPDF dither); everything is generated, no real album art.
"""
import colorsys
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = [ROOT.parents[1] / "skins" / "skin.groove" / "fonts", ROOT.parents[1] / "skin.groove" / "fonts"]   # studio / public layout
RNG = np.random.default_rng(7)
SS = 4
ROOM_CENTRE, ROOM_EDGE = (34, 31, 28), (25, 23, 21)
AMBER_HUE = 22 / 360.0                         # Groove's lit slice (222, 112, 52): the 3 o'clock slice keeps it
HUB = (30, 28, 26)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def room(w, h, cx, cy):
    y, x = np.mgrid[0:h, 0:w]
    t = smooth(np.sqrt(((x - cx) / (w * 0.8)) ** 2 + ((y - cy) / (h * 0.9)) ** 2))[..., None]
    return np.array(ROOM_CENTRE, float) * (1 - t) + np.array(ROOM_EDGE, float) * t


def radial(w, h, cx, cy, r, p=1.0):
    y, x = np.mgrid[0:h, 0:w]
    return smooth(1 - np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r) ** p


def over(base, rgb, a):
    return base * (1 - a[..., None]) + np.asarray(rgb, float) * a[..., None]


def to_img(a):
    n = RNG.random(a.shape) - RNG.random(a.shape)    # TPDF dither: no banding in the glow
    return Image.fromarray(np.clip(np.round(a + n), 0, 255).astype(np.uint8), "RGB")


def slice_colours():
    """Twelve art colours round the hue circle (clockwise from 3 o'clock), lifted like the helper lifts Main (L 0.55)."""
    out = []
    for k in range(12):
        h = (AMBER_HUE + k / 12.0) % 1.0
        r, g, b = colorsys.hls_to_rgb(h, 0.52 + 0.04 * (k % 2), 0.44 if k else 0.62)  # muted sleeve colours; the 3 o'clock one reads
        out.append(np.array((r * 255, g * 255, b * 255)))
    return out


def ring_masks(size, cx, cy, r0, r1, line_w):
    """At SS: one fill mask per slice (hairline gaps) and one edge mask for all of them, as float arrays at size."""
    S = size * SS
    C = (cx * SS, cy * SS)
    R0, R1 = r0 * SS, r1 * SS
    gap = 1.4
    fills, edge = [], Image.new("L", (S, S), 0)
    de = ImageDraw.Draw(edge)
    for k in range(12):
        a0, a1 = -15 + k * 30 + gap, 15 + k * 30 - gap
        pts = [(C[0] + R1 * math.cos(math.radians(t)), C[1] + R1 * math.sin(math.radians(t))) for t in np.linspace(a0, a1, 40)]
        pts += [(C[0] + R0 * math.cos(math.radians(t)), C[1] + R0 * math.sin(math.radians(t))) for t in np.linspace(a1, a0, 40)]
        m = Image.new("L", (S, S), 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        fills.append(np.asarray(m.resize((size, size), Image.BOX), float) / 255)
        de.line(pts + [pts[0]], fill=255, width=int(line_w * SS), joint="curve")
    return fills, np.asarray(edge.resize((size, size), Image.BOX), float) / 255


def mark_scene(w, h, cx, cy, r1, caption=None, scale=1.0):
    r0 = r1 * 0.62
    hub = r0 * 2 * 0.74
    cols = slice_colours()
    S = max(w, h)                       # build the ring on a square canvas, then crop to the scene
    oy = (S - h) // 2
    fills, edge = ring_masks(S, cx, cy + oy, r0, r1, max(1.5, 2 * scale))
    fills, edge = [f[oy:oy + h, :w] for f in fills], edge[oy:oy + h, :w]
    ring = np.zeros((h, w, 3))
    cover = np.zeros((h, w))
    for f, c in zip(fills, cols):
        ring += f[..., None] * c
        cover += f
    # the ring's own light: a wide and a near blur of the coloured slices wash the room
    glow = Image.fromarray(np.clip(ring, 0, 255).astype(np.uint8), "RGB")
    wide = np.asarray(glow.filter(ImageFilter.GaussianBlur(r1 * 0.55)), float)
    near = np.asarray(glow.filter(ImageFilter.GaussianBlur(r1 * 0.16)), float)
    base = room(w, h, cx, cy)
    base = base + wide * 0.45 + near * 0.28
    base = over(base, (0, 0, 0), np.asarray(Image.fromarray((cover * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(r1 * 0.04)), float) / 255 * 0.45)                                  # slice shadow
    lit = np.minimum(ring * 1.12, 255)
    base = base * (1 - cover[..., None] * 0.9) + lit * 0.9
    base = over(base, (255, 255, 255), edge * 0.42)                                                  # hairline rim
    img = to_img(base).convert("RGBA")
    # hub: shadow, plain dark disc with fine grooves, centre hole
    sh = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sh).ellipse([cx - hub / 2, cy - hub / 2 + hub * 0.05, cx + hub / 2, cy + hub / 2 + hub * 0.05], fill=160)
    sh = sh.filter(ImageFilter.GaussianBlur(hub * 0.06))
    img.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (w, h), 0).split(), sh)))
    D = int(round(hub)) * SS
    disc = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse([0, 0, D - 1, D - 1], fill=HUB + (255,))
    for i in range(7):                                   # grooves: hairlines, brighter toward the rim
        rr = D / 2 * (0.42 + i * 0.085)
        a = int(16 + i * 5)
        dd.ellipse([D / 2 - rr, D / 2 - rr, D / 2 + rr, D / 2 + rr], outline=(255, 255, 255, a), width=max(1, SS))
    rr = D / 2 * 0.24                                    # inner ring in the 3 o'clock colour: the reading
    c = tuple(int(v) for v in cols[0])
    dd.ellipse([D / 2 - rr, D / 2 - rr, D / 2 + rr, D / 2 + rr], outline=c + (235,), width=int(max(2, 2 * scale) * SS))
    disc = disc.resize((int(round(hub)), int(round(hub))), Image.LANCZOS)
    img.alpha_composite(disc, (int(round(cx - hub / 2)), int(round(cy - hub / 2))))
    hole = max(4, hub / 22)
    ImageDraw.Draw(img).ellipse([cx - hole / 2, cy - hole / 2, cx + hole / 2, cy + hole / 2], fill=ROOM_EDGE + (255,))
    if caption:
        fdir = next((p for p in FONTS if p.exists()), None)
        if fdir:
            d = ImageDraw.Draw(img)
            fm = ImageFont.truetype(str(fdir / "Groove-Medium.ttf"), 30)
            fl = ImageFont.truetype(str(fdir / "Groove-Light.ttf"), 28)
            x, y = caption
            d.text((x, y), "KarmaMole Skin Helper", font=fm, fill=(255, 255, 255, 235))
            tw = d.textlength("KarmaMole Skin Helper", font=fm)
            d.text((x + tw, y + 2), "  ·  colour from the art", font=fl, fill=(255, 255, 255, 146))
    return img


def main():
    big = mark_scene(1024, 1024, 512, 512, 380, scale=2.0)
    icon = big.convert("RGB").resize((512, 512), Image.LANCZOS)
    icon.save(ROOT / "icon.png", optimize=True)
    fan = mark_scene(1920, 1080, 1220, 540, 380, caption=(96, 1080 - 54 - 40))
    fan.convert("RGB").save(ROOT / "fanart.jpg", quality=92)
    print("wrote", ROOT / "icon.png", icon.size, icon.mode, "|", ROOT / "fanart.jpg", fan.size)


if __name__ == "__main__":
    main()
