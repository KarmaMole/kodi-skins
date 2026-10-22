"""icon.png (512, solid) and fanart.jpg (1920x1080) for skin.groove, in the skin's own art direction.
    python skins/skin.groove/_src/make_addon_art.py      (Pillow + numpy; reads media/groove/vinyl*.png, fonts/)

Concept (DESIGN.md §1, "art as light"): the near-black listening room, one record in your hands. The sleeve is the
only light source: it is lit at full brightness, its colours wash the room and halo behind it, and the disc slides
out of it (the Now Playing slide-out, +40% of the diameter). The fanart adds the dimmed neighbours of the crate and
the one caption line. Every picture here is generated (a Bauhaus-style sleeve drawn from circles and thin lines);
there is no real album art and no third-party art.
The official Kodi repository wants a solid icon, so the icon is saved as RGB.
"""
import colorsys
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKIN = Path(__file__).resolve().parents[1]
G = SKIN / "media" / "groove"
FONTS = SKIN / "fonts"
RNG = np.random.default_rng(20261021)
SS = 4

ROOM_CENTRE = (34, 31, 28)     # FF221F1C
ROOM_EDGE = (25, 23, 21)       # FF191715

# generated sleeves: (ground, big disc, second shape, line colour)
SLEEVES = {
    "hero":  [(214, 120, 44), (178, 46, 38), (240, 196, 112), (246, 232, 206)],   # amber / vermilion / ochre
    "teal":  [(30, 84, 92), (222, 160, 78), (16, 46, 54), (232, 222, 200)],
    "rose":  [(150, 52, 70), (238, 196, 170), (64, 24, 40), (250, 236, 222)],
    "ink":   [(28, 30, 44), (88, 132, 200), (222, 204, 160), (230, 230, 236)],
    "olive": [(110, 112, 54), (230, 214, 160), (52, 56, 30), (240, 236, 214)],
}


# ------------------------------------------------------------------------------------------------- helpers
def tpdf(shape, amp=1.0):
    return (RNG.random(shape) - RNG.random(shape)) * amp


def to_img(rgb):
    return Image.fromarray(np.clip(np.round(rgb + tpdf(rgb.shape)), 0, 255).astype(np.uint8), "RGB")


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def room(w, h, cx, cy, rx, ry):
    """The dark room: an opaque radial from room_centre to room_edge (float array, dithered on save)."""
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    t = smooth(d)[..., None]
    c, e = np.array(ROOM_CENTRE, float), np.array(ROOM_EDGE, float)
    return c * (1 - t) + e * t


def radial_mask(w, h, cx, cy, r, power=1.0):
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    return smooth(1 - d) ** power


def over(base, layer_rgb, alpha):
    a = alpha[..., None]
    return base * (1 - a) + layer_rgb * a


def soft_art(art: Image.Image, w, h, sat=1.45, bright=1.12, vcap=0.5):
    """Groove.Art.Soft: the art at 12 px, upscaled and blurred, saturated, brightened, value-capped."""
    s = art.convert("RGB").resize((12, 12), Image.BOX).resize((w, h), Image.BICUBIC)
    s = s.filter(ImageFilter.GaussianBlur(max(w, h) / 18))
    a = np.asarray(s, float) / 255
    # vectorised HSV tweak
    mx, mn = a.max(-1), a.min(-1)
    v = mx
    sat_now = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    grey = v[..., None]
    k = np.where(sat_now > 0, np.minimum(sat_now * sat, 1) / np.maximum(sat_now, 1e-6), 1)[..., None]
    out = grey - (grey - a) * k
    out = out * bright
    vmax = out.max(-1, keepdims=True)
    out = np.where(vmax > vcap, out * (vcap / np.maximum(vmax, 1e-6)), out)
    return np.clip(out, 0, 1) * 255


def main_colour(art: Image.Image):
    """Saturation-weighted mean colour with lightness reset to 0.55 (Groove.Color.Main)."""
    a = np.asarray(art.convert("RGB").resize((48, 48), Image.BOX), float) / 255
    mx, mn = a.max(-1), a.min(-1)
    wgt = (mx - mn) + 0.02
    m = (a * wgt[..., None]).sum((0, 1)) / wgt.sum()
    h, l, s = colorsys.rgb_to_hls(*m)
    return np.array(colorsys.hls_to_rgb(h, 0.55, min(1, s * 1.1))) * 255


def sleeve_art(size, pal, variant=0):
    """A generated sleeve in the record-sleeve modernist tradition: flat ground, one big disc, one offset shape,
    a set of thin concentric lines. Square corners (DESIGN §4)."""
    ground, big, second, line = pal
    S = size * SS
    im = Image.new("RGB", (S, S), ground)
    d = ImageDraw.Draw(im)
    if variant == 0:      # sun over horizon, groove arcs
        d.rectangle([0, int(S * 0.64), S, S], fill=second)
        r = S * 0.30
        cx, cy = S * 0.42, S * 0.52
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=big)
        lw = max(1, int(S * 0.006))
        for i in range(7):
            rr = S * (0.36 + i * 0.045)
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 200, 340, fill=line, width=lw)
        d.ellipse([S * 0.78 - S * 0.035, S * 0.20 - S * 0.035, S * 0.78 + S * 0.035, S * 0.20 + S * 0.035], fill=line)
    elif variant == 1:    # quarter circles
        d.pieslice([-S * 0.5, S * 0.5, S * 0.5, S * 1.5], 270, 360, fill=big)
        d.pieslice([S * 0.5, -S * 0.5, S * 1.5, S * 0.5], 90, 180, fill=second)
        lw = max(1, int(S * 0.006))
        for i in range(5):
            rr = S * (0.62 + i * 0.05)
            d.arc([-rr, S - rr, rr, S + rr], 270, 360, fill=line, width=lw)
    elif variant == 2:    # stacked bands and a dot
        for i in range(6):
            y0 = S * (0.18 + i * 0.11)
            d.rectangle([S * 0.12, y0, S * 0.88, y0 + S * 0.05], fill=big if i % 2 == 0 else second)
        d.ellipse([S * 0.62, S * 0.10, S * 0.82, S * 0.30], fill=line)
    else:                 # one ring
        lw = int(S * 0.08)
        d.ellipse([S * 0.18, S * 0.18, S * 0.82, S * 0.82], outline=big, width=lw)
        d.ellipse([S * 0.40, S * 0.40, S * 0.60, S * 0.60], fill=second)
        d.line([0, S * 0.86, S, S * 0.86], fill=line, width=max(1, int(S * 0.006)))
    im = im.resize((size, size), Image.LANCZOS)
    # a faint print grain so the flat fields read as ink on card, not as vector fills
    g = RNG.normal(0, 2.2, (size, size, 1))
    return Image.fromarray(np.clip(np.asarray(im, float) + g, 0, 255).astype(np.uint8), "RGB")


def record(d_px, label_art: Image.Image):
    """vinyl.png at d_px with the label (the sleeve art, cropped round) in the hole, and the still sheen."""
    v = Image.open(G / "vinyl.png").convert("RGBA").resize((d_px, d_px), Image.LANCZOS)
    lab_d = int(d_px * 0.335 * 2) + 2
    lab = label_art.resize((lab_d, lab_d), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (lab_d * SS, lab_d * SS), 0)
    ImageDraw.Draw(m).ellipse([0, 0, lab_d * SS - 1, lab_d * SS - 1], fill=255)
    lab.putalpha(m.resize((lab_d, lab_d), Image.LANCZOS))
    out = Image.new("RGBA", (d_px, d_px), (0, 0, 0, 0))
    o = (d_px - lab_d) // 2
    out.alpha_composite(lab, (o, o))
    out.alpha_composite(v)
    sheen = Image.open(G / "vinyl_sheen.png").convert("RGBA").resize((d_px, d_px), Image.LANCZOS)
    out.alpha_composite(sheen)
    # spindle hole
    hd = max(4, d_px // 40)
    hm = Image.new("L", (hd * SS, hd * SS), 0)
    ImageDraw.Draw(hm).ellipse([0, 0, hd * SS - 1, hd * SS - 1], fill=255)
    hole = Image.new("RGBA", (hd, hd), ROOM_EDGE + (255,))
    hole.putalpha(hm.resize((hd, hd), Image.LANCZOS))
    out.alpha_composite(hole, ((d_px - hd) // 2, (d_px - hd) // 2))
    return out


def shadow_layer(w, h, box, sigma, dy, strength):
    m = Image.new("L", (w, h), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rectangle([x0, y0 + dy, x1, y1 + dy], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(sigma)), float) / 255 * strength


def disc_shadow(w, h, cx, cy, r, sigma, dy, strength):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r + dy, cx + r, cy + r + dy], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(sigma)), float) / 255 * strength


def light_the_room(base, art, cx, cy, item, wash_r, wash_a=0.42, halo_a=0.85):
    """§6 glow recipe: wash (soft art through a radial) + halo (soft art mixed 60/40 with the main colour)."""
    h, w = base.shape[:2]
    soft = soft_art(art, w, h)
    base = over(base, soft, radial_mask(w, h, cx, cy, wash_r, 1.0) * wash_a)
    mc = main_colour(art)
    halo = soft_art(art, w, h, vcap=0.72) * 0.6 + mc * 0.4
    vmax = halo.max(-1, keepdims=True)
    halo = np.where(vmax > 0.72 * 255, halo * (0.72 * 255 / vmax), halo)
    base = over(base, halo, radial_mask(w, h, cx, cy, item * 1.05, 1.4) * halo_a)
    return base


def place(base_img: Image.Image, layer: Image.Image, xy, dim=1.0):
    if dim < 1.0:
        r, g, b, a = layer.split()
        rgb = Image.merge("RGB", (r, g, b)).point(lambda v: int(v * dim))
        layer = Image.merge("RGBA", (*rgb.split(), a))
    base_img.alpha_composite(layer, xy)


def rim(img: Image.Image, box, width, alpha=0.60):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle(box, outline=(255, 255, 255, int(255 * alpha)), width=width)
    img.alpha_composite(ov)


# ------------------------------------------------------------------------------------------------- scenes
def hero_scene(w, h, sx, sy, sz, neighbours=(), caption=None, font_scale=1.0):
    art = sleeve_art(sz, SLEEVES["hero"], 0)
    disc_d = int(sz * 0.96)
    slide = int(disc_d * 0.40)
    dcx, dcy = sx + sz // 2 + slide, sy + sz // 2
    cx, cy = sx + sz / 2 + slide * 0.35, sy + sz / 2
    base = room(w, h, cx, cy * 0.98, w * 0.75, h * 0.85)
    base = light_the_room(base, art, cx, cy, sz, wash_r=max(w, h) * 0.55)
    # dimmed neighbours sit in the room's shadow: drawn before the light spill reaches them
    for (nx, ny, nsz, key, var) in neighbours:
        sh = shadow_layer(w, h, (nx, ny, nx + nsz, ny + nsz), nsz * 0.08, int(nsz * 0.08), 0.55)
        base = over(base, np.zeros(3), sh)
    img = to_img(base).convert("RGBA")
    for (nx, ny, nsz, key, var) in neighbours:
        place(img, sleeve_art(nsz, SLEEVES[key], var).convert("RGBA"), (nx, ny), dim=112 / 255)   # dim_cover FF707070
    # the halo spills over the dimmed neighbours (focused item is drawn last)
    arr = np.asarray(img.convert("RGB"), float)
    mc = main_colour(art)
    arr = over(arr, mc * 0.85, radial_mask(w, h, cx, cy, sz * 1.5, 2.2) * 0.22)
    # shadows of the record and the sleeve
    arr = over(arr, np.zeros(3), disc_shadow(w, h, dcx, dcy, disc_d / 2, sz * 0.05, int(sz * 0.05), 0.65))
    arr = over(arr, np.zeros(3), shadow_layer(w, h, (sx, sy, sx + sz, sy + sz), sz * 0.07, int(sz * 0.07), 0.75))
    img = to_img(arr).convert("RGBA")
    img.alpha_composite(record(disc_d, art), (dcx - disc_d // 2, dcy - disc_d // 2))
    # contact shadow on the disc under the sleeve's right edge
    cs = Image.new("L", (w, h), 0)
    ImageDraw.Draw(cs).rectangle([sx + sz - 2, sy, sx + sz + int(sz * 0.02), sy + sz], fill=255)
    cs = cs.filter(ImageFilter.GaussianBlur(sz * 0.02)).point(lambda v: int(v * 0.6))
    img.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (w, h), 0).split(), cs)))
    img.alpha_composite(art.convert("RGBA"), (sx, sy))
    rim(img, (sx, sy, sx + sz - 1, sy + sz - 1), max(2, int(round(2 * font_scale))))
    if caption:
        d = ImageDraw.Draw(img)
        fm = ImageFont.truetype(str(FONTS / "Groove-Medium.ttf"), int(30 * font_scale))
        fl = ImageFont.truetype(str(FONTS / "Groove-Light.ttf"), int(28 * font_scale))
        x, y = caption
        title, rest = "Groove", "  ·  art as light"
        d.text((x, y), title, font=fm, fill=(255, 255, 255, 235))
        tw = d.textlength(title, font=fm)
        d.text((x + tw, y + 2 * font_scale), rest, font=fl, fill=(255, 255, 255, int(235 * 0.62)))
    return img


def main():
    # fanart: the crate row at rest, one record lit, a caption line in the safe area
    sz = 500
    sx, sy = 560, 250
    gap = 64
    nb = [
        (sx - gap - 380, sy + 120, 380, "teal", 1),
        (sx - 2 * gap - 2 * 380 + 40, sy + 120, 380, "ink", 3),
        (sx + sz + int(sz * 0.96 * 0.40) + 64, sy + 120, 380, "rose", 2),
        (sx + sz + int(sz * 0.96 * 0.40) + 64 + 380 + gap, sy + 120, 380, "olive", 1),
    ]
    fan = hero_scene(1920, 1080, sx, sy, sz, neighbours=nb, caption=(96, 1080 - 54 - 40))
    fan.convert("RGB").save(SKIN / "resources" / "fanart.jpg", quality=92)

    # icon: drawn at 1024 and reduced; the sleeve with the disc half out, nothing else
    big = hero_scene(1024, 1024, 144, 242, 540, font_scale=2.0)
    icon = big.convert("RGB").resize((512, 512), Image.LANCZOS)
    icon.save(SKIN / "resources" / "icon.png", optimize=True)
    print("wrote", SKIN / "resources" / "icon.png", icon.size, icon.mode, "|", SKIN / "resources" / "fanart.jpg", fan.size)


if __name__ == "__main__":
    main()
