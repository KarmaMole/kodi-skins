"""Fold textures (reproducible):  python skins/skin.fold/_src/make_textures.py

Everything is pre-rendered (Kodi has no blend modes, masks other than alpha, or live blur), with values taken
from the approved mockups (docs/concepts/round4/mockups/Fold*.html):
  * paper tooth: the mockup generator (docs/concepts/round4/mockups/fold/make_tex.py), same seed
  * the table: tooth + the two radial lights of the mockup body, opaque JPG
  * shapes (white, tinted in XML with colordiffuse): card, tabs, panels, chips, season tab, key caps
  * shadows (baked warm brown with alpha, CSS box-shadow sigma = blur / 2, filter:blur sigma = px)
  * shading overlays animated in sync with the folds (crease gradients, cover / flap shading, cast shadow)
Outputs: media/fold/*.png|jpg. Preview sheet: _src/previews/fold_textures.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "fold"
PREV = HERE / "previews"
SS = 4  # supersampling for shapes

WARM = (60, 20, 10)       # card shadows (mockup rgba(60,20,10,...))
WARM2 = (70, 30, 15)      # lift shadow
WARM3 = (70, 50, 30)      # spread shadow
COOL = (10, 20, 60)       # cobalt cards


# ----------------------------------------------------------------------------- paper tooth (mockup generator)
rng = np.random.default_rng(15)


def periodic_noise(n, lo, hi):
    w = rng.standard_normal((n, n))
    f = np.fft.fft2(w)
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    r = np.sqrt(fx * fx + fy * fy)
    band = np.exp(-((r - (lo + hi) / 2) ** 2) / (2 * ((hi - lo) / 2) ** 2))
    out = np.real(np.fft.ifft2(f * band))
    out /= np.abs(out).max()
    return out


def fibres(n, count, length, seed):
    r = np.random.default_rng(seed)
    img = np.zeros((n, n))
    for _ in range(count):
        x, y = r.uniform(0, n, 2)
        a = r.uniform(0, np.pi)
        curv = r.normal(0, 0.04)
        L = r.uniform(length * 0.5, length)
        for _t in np.linspace(0, L, int(L * 2)):
            a += curv / 2
            x += np.cos(a) * 0.5
            y += np.sin(a) * 0.5
            img[int(y) % n, int(x) % n] = 1
    return img


def to_rgba(v, dark_a, light_a):
    n = v.shape[0]
    rgba = np.zeros((n, n, 4), np.uint8)
    pos = v > 0
    rgba[..., :3] = np.where(pos[..., None], 255, 0)
    a = np.where(pos, v * light_a, -v * dark_a)
    rgba[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def tooth_fields():
    N = 512
    grain = periodic_noise(N, 0.18, 0.5)
    grain = np.sign(grain) * np.abs(grain) ** 0.8
    mottle = periodic_noise(N, 0.004, 0.02)
    fib = fibres(N, 260, 26, 3)
    fib2 = fibres(N, 160, 18, 4)
    card = np.clip(grain * 0.8 + mottle * 0.35 - fib * 0.6 + fib2 * 0.7, -1, 1)
    cream = np.clip(grain * 0.7 + mottle * 0.45 - fib * 0.5 + fib2 * 0.5, -1, 1)
    table = np.clip(grain * 0.6 + mottle * 0.6 - fib * 0.3, -1, 1)
    return card, cream, table


# ----------------------------------------------------------------------------- helpers
def save(img, name):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if name.endswith(".jpg"):
        img.convert("RGB").save(path, quality=92, subsampling=0)
    else:
        img.save(path, optimize=True)
    return img


def rrect_mask(w, h, r, corners=(1, 1, 1, 1)):
    """Antialiased rounded-rect alpha mask. corners = (tl, tr, br, bl) on/off."""
    big = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(big)
    R = r * SS
    d.rectangle([0, 0, w * SS - 1, h * SS - 1], fill=255)
    if r:
        for i, (cx, cy) in enumerate([(0, 0), (w * SS - 2 * R, 0), (w * SS - 2 * R, h * SS - 2 * R), (0, h * SS - 2 * R)]):
            if not corners[i]:
                continue
            # clear the corner square then draw the quarter circle
            sq = [(0, 0, R, R), (w * SS - R, 0, w * SS, R), (w * SS - R, h * SS - R, w * SS, h * SS), (0, h * SS - R, R, h * SS)][i]
            d.rectangle([sq[0], sq[1], sq[2] - 1, sq[3] - 1], fill=0)
            d.ellipse([cx, cy, cx + 2 * R - 1, cy + 2 * R - 1], fill=255)
    return big.resize((w, h), Image.LANCZOS)


def path_mask(w, h, pts, scale=SS):
    big = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(big).polygon([(x * scale, y * scale) for x, y in pts], fill=255)
    return big.resize((w, h), Image.LANCZOS)


def quad(p0, p1, p2, n=10):
    out = []
    for i in range(1, n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def tab_points(h):
    """Mockup clip-path: M0,0 H196 L188,(h-16) Q186,h 170,h H26 Q10,h 8,(h-16) Z"""
    pts = [(0, 0), (196, 0), (188, h - 16)]
    pts += quad((188, h - 16), (186, h), (170, h))
    pts += [(26, h)]
    pts += quad((26, h), (10, h), (8, h - 16))
    return pts


def white_shape(mask):
    img = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    img.putalpha(mask)
    return img


def shadow(shape_mask, pad, layers, rgb, size=None):
    """Composite CSS-like drop shadows of a shape. layers: (dx, dy, blur_sigma, alpha, spread).
    Returns an RGBA image of shape size + 2*pad (the shape sits at (pad, pad))."""
    w, h = shape_mask.size
    W, H = w + 2 * pad, h + 2 * pad
    acc = np.zeros((H, W), np.float64)  # combined alpha (over)
    for dx, dy, sig, a, spread in layers:
        m = Image.new("L", (W, H), 0)
        sm = shape_mask
        if spread:
            sm = shape_mask.filter(ImageFilter.MaxFilter(2 * spread + 1)) if spread > 0 else shape_mask
        m.paste(sm, (pad + dx, pad + dy))
        if sig > 0:
            m = m.filter(ImageFilter.GaussianBlur(sig))
        la = np.asarray(m, np.float64) / 255 * a
        acc = acc + la * (1 - acc)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = rgb
    rgba[..., 3] = np.clip(acc * 255 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def hgrad(w, h, stops):
    """Horizontal gradient strip. stops: [(pos 0..1, (r,g,b,a 0..1))]."""
    xs = np.linspace(0, 1, w)
    arr = np.zeros((h, w, 4), np.float64)
    pos = [s[0] for s in stops]
    for c in range(4):
        vals = [s[1][c] / (255 if c < 3 else 1) for s in stops]
        arr[..., c] = np.interp(xs, pos, vals)[None, :]
    arr[..., :3] *= 255
    arr[..., 3] *= 255
    return Image.fromarray(np.clip(arr + 0.5, 0, 255).astype(np.uint8), "RGBA")


def vgrad(w, h, stops):
    return hgrad(h, w, stops).transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)


def angle_grad(w, h, deg, stops):
    """CSS linear-gradient(deg, stops) over a w x h box."""
    a = np.deg2rad(deg)
    dx, dy = np.sin(a), -np.cos(a)
    L = abs(w * np.sin(a)) + abs(h * np.cos(a))
    ys, xs = np.mgrid[0:h, 0:w]
    t = ((xs - w / 2) * dx + (ys - h / 2) * dy) / L + 0.5
    arr = np.zeros((h, w, 4), np.float64)
    pos = [s[0] for s in stops]
    for c in range(4):
        vals = [s[1][c] / (255 if c < 3 else 1) for s in stops]
        arr[..., c] = np.interp(t, pos, vals)
    arr[..., :3] *= 255
    arr[..., 3] *= 255
    return Image.fromarray(np.clip(arr + 0.5, 0, 255).astype(np.uint8), "RGBA")


def tooth_tile(field, dark, light, size):
    img = to_rgba(field, dark, light)
    if size != img.size[0]:
        img = img.resize((size, size), Image.LANCZOS)
    return img


# ----------------------------------------------------------------------------- the table
def make_table(table_field):
    W, H = 1920, 1080
    base = np.ones((H, W, 3)) * np.array([0xE9, 0xE7, 0xE2], np.float64)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)

    def radial(cx, cy, rx, ry, rgb, a0, stop):
        d = np.sqrt(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2)
        a = a0 * np.clip(1 - d / stop, 0, 1)
        return a[..., None], np.array(rgb, np.float64)

    # radial-gradient(1400px 900px at 22% 8%, rgba(255,255,255,.55), 0 70%)
    a, c = radial(0.22 * W, 0.08 * H, 1400, 900, (255, 255, 255), 0.55, 0.70)
    base = base * (1 - a) + c * a
    # radial-gradient(1200px 700px at 100% 110%, rgba(60,50,40,.10), 0 70%)
    a, c = radial(W, 1.10 * H, 1200, 700, (60, 50, 40), 0.10, 0.70)
    base = base * (1 - a) + c * a
    # tooth overlay (tiled 512)
    t = np.tile(table_field, (H // 512 + 1, W // 512 + 1))[:H, :W]
    pos = t > 0
    al = np.where(pos, t * 0.07, -t * 0.07)[..., None]
    col = np.where(pos[..., None], 255.0, 0.0)
    base = base * (1 - al) + col * al
    # TPDF dither
    base += (np.random.default_rng(1).random(base.shape) - np.random.default_rng(2).random(base.shape))
    img = Image.fromarray(np.clip(base + 0.5, 0, 255).astype(np.uint8), "RGB")
    save(img, "table.jpg")
    return img


# ----------------------------------------------------------------------------- build
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(exist_ok=True)
    card_f, cream_f, table_f = tooth_fields()
    made = {}

    made["table"] = make_table(table_f)
    made["tooth_card"] = save(tooth_tile(card_f, 0.16, 0.10, 512), "tooth_card.png")
    made["tooth_cream"] = save(tooth_tile(cream_f, 0.09, 0.08, 512), "tooth_cream.png")
    # smaller tile for small cards / tabs (finer grain after stretching)
    save(tooth_tile(card_f, 0.16, 0.10, 512).crop((0, 0, 256, 256)), "tooth_card_s.png")

    # --- card: 4px radius shape (9-slice border 6), rim, sheen ------------------------------------------
    save(white_shape(rrect_mask(32, 32, 4)), "rr4.png")
    save(white_shape(rrect_mask(32, 32, 3)), "rr3.png")
    save(white_shape(rrect_mask(32, 32, 5)), "rr5.png")
    save(white_shape(rrect_mask(32, 32, 5, (1, 0, 0, 1))), "rr5_l.png")
    save(white_shape(rrect_mask(32, 32, 5, (0, 1, 1, 0))), "rr5_r.png")
    save(white_shape(rrect_mask(32, 32, 6, (0, 1, 1, 0))), "rr6_r.png")
    # rim: inset 0 1px 0 rgba(255,255,255,.22), inset 0 -1px 0 rgba(0,0,0,.18); 9-slice border 6
    rim = np.zeros((32, 32, 4), np.uint8)
    rim[0, :, :] = (255, 255, 255, 56)
    rim[31, :, :] = (0, 0, 0, 46)
    rimg = Image.fromarray(rim, "RGBA")
    rimg.putalpha(Image.fromarray(np.minimum(np.asarray(rimg.getchannel("A")), np.asarray(rrect_mask(32, 32, 4)))))
    save(rimg, "card_rim.png")
    rim2 = rim.copy()
    rim2[0, :, 3] = 72
    save(Image.fromarray(rim2, "RGBA"), "card_rim_on.png")
    # sheen: linear-gradient(165deg, rgba(255,255,255,.07), 0 45%, rgba(0,0,0,.07))
    sheen = angle_grad(128, 196, 165, [(0, (255, 255, 255, .07)), (.45, (255, 255, 255, 0)), (.55, (0, 0, 0, 0)), (1, (0, 0, 0, .07))])
    save(sheen, "card_sheen.png")
    # focused card light: linear-gradient(180deg, rgba(255,255,255,.14), 0 55%)
    save(vgrad(4, 128, [(0, (255, 255, 255, .14)), (.55, (255, 255, 255, 0)), (1, (255, 255, 255, 0))]), "card_light.png")
    # hinge score on the spine: linear-gradient(90deg, rgba(0,0,0,.22), rgba(255,255,255,.22)), 2px
    save(hgrad(2, 4, [(0, (0, 0, 0, .22)), (1, (255, 255, 255, .22))]), "score.png")
    save(hgrad(3, 4, [(0, (0, 0, 0, .25)), (1, (255, 255, 255, .25))]), "score3.png")
    # fore-edge of the cream inside page: 4px, linear-gradient(90deg,#d9d1c1,#f3ede1), radius 0 3 3 0
    fe = hgrad(4, 64, [(0, (0xd9, 0xd1, 0xc1, 1)), (1, (0xf3, 0xed, 0xe1, 1))])
    fe.putalpha(rrect_mask(4, 64, 2, (0, 1, 1, 0)))
    save(fe, "foredge.png")

    # card shadows (rest / lifted), shape 120x180, pad 48: 9-slice border 56
    cm = rrect_mask(120, 180, 4)
    rest = [(0, 1, 0.5, .30, 0), (0, 3, 3, .14, 0), (0, 10, 11, .08, 0)]
    save(shadow(cm, 48, rest, WARM), "shadow_card.png")
    save(shadow(cm, 48, rest, COOL), "shadow_card_cool.png")
    # focused (mockup .liftshadow blur 24 @ .42 translate 26,40 and .liftshadow2 blur 8 @ .34 translate 10,16,
    # contact blur 5 @ .45 under the bottom edge), shape 248x382, pad 96
    fm = rrect_mask(248, 382, 6)
    lift = [(0, 1, 0.5, .35, 0), (10, 16, 8, .30, -4), (26, 40, 24, .38, 4)]
    save(shadow(fm, 96, lift, WARM2), "shadow_lift.png")
    save(shadow(fm, 96, lift, COOL), "shadow_lift_cool.png")
    # small lift for small items (squares, cream cards), shape 120x120, pad 56
    sm = rrect_mask(120, 120, 4)
    save(shadow(sm, 56, [(0, 1, 0.5, .30, 0), (6, 12, 6, .26, 0), (14, 24, 14, .26, 0)], WARM2), "shadow_lift_s.png")
    # cream card shadow (continue watching): 0 1px 1px .25, 0 4px 10px .10 rgb(60,45,30)
    save(shadow(rrect_mask(120, 120, 4), 40, [(0, 1, 0.5, .25, 0), (0, 4, 5, .10, 0)], (60, 45, 30)), "shadow_cream.png")
    # spread / note shadow (mockup FoldOpen .shadow): blur 26 @.20 translate 14,22 + blur 4 @.30 translate 2,4
    nm = rrect_mask(400, 300, 6)
    save(shadow(nm, 96, [(2, 4, 4, .30, 0), (14, 22, 26, .20, 0)], WARM3), "shadow_spread.png")
    # rising flap shadow on the table (blur 30 @ .24, translate 40,30, rounded 30/60)
    flm = rrect_mask(300, 400, 40)
    save(shadow(flm, 110, [(40, 30, 30, .24, 0)], WARM3), "shadow_flap.png")

    # plate (tipped-in poster): ring 1px .18 + 0 1px 1px .35 + 0 2px 4px .18; pad 12, 9-slice border 14
    pm = Image.new("L", (64, 96), 255)
    pl = shadow(pm, 12, [(0, 0, 0, .18, 1), (0, 1, 0.5, .35, 0), (0, 2, 2, .18, 0)], (30, 10, 5))
    arr = np.asarray(pl).copy()
    arr[12:12 + 96, 12:12 + 64, 3] = 0  # hollow: the art draws on top anyway, keep the centre clear
    save(Image.fromarray(arr, "RGBA"), "plate_frame.png")
    # plate sheen: linear-gradient(160deg, rgba(255,255,255,.10), 0 35%)
    save(angle_grad(128, 180, 160, [(0, (255, 255, 255, .10)), (.35, (255, 255, 255, 0)), (1, (255, 255, 255, 0))]), "plate_sheen.png")

    # --- section tabs (196 x 66 / 98), shading, shadows -----------------------------------------------------
    for name, h in (("tab", 66), ("tab_on", 98)):
        m = path_mask(196, h, tab_points(h))
        save(white_shape(m), f"{name}.png")
        # linear-gradient(180deg, rgba(0,0,0,.10), 0 40%, rgba(255,255,255,.05)) + ::after top 6px .18
        g = vgrad(196, h, [(0, (0, 0, 0, .10)), (.4, (0, 0, 0, 0)), (1, (255, 255, 255, .05))])
        top = vgrad(196, h, [(0, (0, 0, 0, .18)), (6 / h, (0, 0, 0, 0)), (1, (0, 0, 0, 0))])
        g = Image.alpha_composite(g, top)
        g.putalpha(Image.fromarray(np.minimum(np.asarray(g.getchannel("A")), np.asarray(m))))
        save(g, f"{name}_shade.png")
        if name == "tab":
            lay = [(0, 1, 0.5, .32, 0), (0, 5, 4, .14, 0)]
        else:
            lay = [(0, 2, 0.5, .32, 0), (0, 12, 8, .20, 0), (0, 26, 17, .10, 0)]
        save(shadow(m, 48, lay, (40, 25, 15)), f"{name}_shadow.png")

    # season tab (die-cut on the show card's top edge): M0,52 L10,12 Q13,0 26,0 H164 Q177,0 180,12 L190,52 Z
    spts = [(0, 52), (10, 12)] + quad((10, 12), (13, 0), (26, 0)) + [(164, 0)] + quad((164, 0), (177, 0), (180, 12)) + [(190, 52)]
    sm2 = path_mask(190, 52, spts)
    save(white_shape(sm2), "stab.png")
    sg = vgrad(190, 52, [(0, (255, 255, 255, .08)), (.7, (0, 0, 0, 0)), (1, (0, 0, 0, .12))])
    sg.putalpha(Image.fromarray(np.minimum(np.asarray(sg.getchannel("A")), np.asarray(sm2))))
    save(sg, "stab_shade.png")

    # --- spread panels: crease shading, ridge, cut edges ---------------------------------------------------
    B = (60, 45, 30)
    save(hgrad(560, 4, [(0, (255, 255, 255, .18)), (.30, (255, 255, 255, 0)), (.80, B + (0,)), (.96, B + (.10,)), (1, B + (.20,))]), "shade_p1.png")
    save(hgrad(560, 4, [(0, B + (.20,)), (.05, B + (.05,)), (.12, B + (0,)), (.88, B + (0,)), (.96, B + (.08,)), (1, B + (.22,))]), "shade_p2.png")
    save(hgrad(560, 4, [(0, (255, 255, 255, .7)), (2 / 560, (255, 255, 255, 0)), (3 / 560, B + (.16,)), (.06, B + (.04,)), (.14, B + (0,)), (.70, B + (0,)), (1, B + (.06,))]), "shade_p3.png")
    save(hgrad(2, 4, [(0, (255, 255, 255, .85)), (1, (255, 255, 255, 0))]), "ridge.png")
    # cover shading as it rises (FoldHalfOpen .cshade): deeper near the hinge, sheen toward the free edge
    save(hgrad(560, 4, [(0, (40, 10, 0, .30)), (.22, (40, 10, 0, .08)), (.55, (255, 240, 225, 0)), (.92, (255, 240, 225, .16)), (1, (255, 250, 240, .32))]), "cover_shade.png")
    # the inside face arriving (turned away from the light until it lands): darker toward its free (left) edge
    save(hgrad(560, 4, [(0, (50, 35, 20, .30)), (.5, (50, 35, 20, .16)), (1, (50, 35, 20, .04))]), "inside_shade.png")
    # the flap turning away (FoldHalfOpen .fshade)
    save(hgrad(560, 4, [(0, (255, 255, 255, .35)), (3 / 560, (255, 255, 255, 0)), (4 / 560, (50, 35, 20, .06)), (.60, (50, 35, 20, .16)), (1, (50, 35, 20, .26))]), "flap_shade.png")
    # cast shadow of the lifted cover on the centre panel (470 of 560)
    save(hgrad(560, 4, [(0, (45, 25, 10, .42)), (.336, (45, 25, 10, .22)), (.671, (45, 25, 10, .06)), (.839, (45, 25, 10, 0)), (1, (45, 25, 10, 0))]), "cast_shadow.png")
    # cut edges of the duplex board (2px inset lines, tinted verm_edge in XML): 9-slice border 4
    for name, sides in (("edge_l", "ltb"), ("edge_c", "tb"), ("edge_r", "rtb"), ("edge_all", "ltrb")):
        e = np.zeros((16, 16, 4), np.uint8)
        e[..., :3] = 255
        if "l" in sides:
            e[:, 0:2, 3] = 255
        if "r" in sides:
            e[:, 14:16, 3] = 255
        if "t" in sides:
            e[0:2, :, 3] = 255
        if "b" in sides:
            e[14:16, :, 3] = 255
        save(Image.fromarray(e, "RGBA"), f"{name}.png")

    # --- action chip (PLAY): radius 3 + shadows (inset 0 1px 0 .25 white, 0 1 1 .35, 0 6 12 .22, 0 14 24 .10)
    save(white_shape(rrect_mask(32, 32, 3)), "chip.png")
    crim = np.zeros((32, 32, 4), np.uint8)
    crim[0, 2:30] = (255, 255, 255, 64)
    save(Image.fromarray(crim, "RGBA"), "chip_rim.png")
    save(shadow(rrect_mask(120, 64, 3), 40, [(0, 1, 0.5, .35, 0), (0, 6, 6, .22, 0), (0, 14, 12, .10, 0)], (80, 25, 10)), "chip_shadow.png")
    # a focused slip (rows on notes): 0 1 1 .25 + 0 4 8 .14
    save(shadow(rrect_mask(120, 64, 3), 32, [(0, 1, 0.5, .25, 0), (0, 4, 4, .14, 0)], (60, 40, 20)), "slip_shadow.png")

    # --- rating stamp ring: 136 px, 3px border -----------------------------------------------------------
    S = 136 * SS
    ring = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(ring)
    d.ellipse([0, 0, S - 1, S - 1], fill=255)
    d.ellipse([3 * SS, 3 * SS, S - 1 - 3 * SS, S - 1 - 3 * SS], fill=0)
    save(white_shape(ring.resize((136, 136), Image.LANCZOS)), "stamp.png")

    # --- dotted leader (2px dotted = 2x2 dots every 4 px) and perforation (6 on, 5 off, 3 tall) -----------
    dots = np.zeros((2, 2000, 4), np.uint8)
    dots[..., :3] = 255
    for x in range(0, 2000, 4):
        dots[:, x:x + 2, 3] = 255
    save(Image.fromarray(dots, "RGBA"), "dots.png")
    perf = np.zeros((3, 2000, 4), np.uint8)
    perf[..., :3] = 255
    for x in range(0, 2000, 11):
        perf[:, x:x + 6, 3] = 255
    save(Image.fromarray(perf, "RGBA"), "perf.png")

    # --- punched hole (watched): 30 px, table colour, inset 0 3 4 .55, inset 0 -1 0 white .6, 0 1 0 white .8
    P = 30
    big = P * SS
    hole = Image.new("RGBA", (P + 4, P + 4), (0, 0, 0, 0))
    m = Image.new("L", (big, big), 0)
    ImageDraw.Draw(m).ellipse([0, 0, big - 1, big - 1], fill=255)
    m = m.resize((P, P), Image.LANCZOS)
    base = Image.new("RGBA", (P, P), (0xDE, 0xDA, 0xD3, 255))
    base.putalpha(m)
    # outer highlight below (0 1px 0 white .8)
    hl = Image.new("RGBA", (P + 4, P + 4), (255, 255, 255, 0))
    hlm = Image.new("L", (P + 4, P + 4), 0)
    hlm.paste(m, (2, 3))
    hl.putalpha(hlm.point(lambda v: int(v * .8)))
    hole = Image.alpha_composite(hole, hl)
    tmp = Image.new("RGBA", (P + 4, P + 4), (0, 0, 0, 0))
    tmp.paste(base, (2, 2), base)
    hole = Image.alpha_composite(hole, tmp)
    # inner shadow: dark from the top edge
    inner = np.zeros((P, P), np.float64)
    mm = np.asarray(m, np.float64) / 255
    shifted = np.zeros_like(mm)
    shifted[3:, :] = mm[:-3, :]
    sh = Image.fromarray(((mm - np.minimum(mm, shifted)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    inner = np.asarray(sh, np.float64) / 255 * .55 * mm
    ish = np.zeros((P, P, 4), np.uint8)
    ish[..., :3] = (40, 30, 20)
    ish[..., 3] = np.clip(inner * 255 * 2.2, 0, 255).astype(np.uint8)
    tmp = Image.new("RGBA", (P + 4, P + 4), (0, 0, 0, 0))
    tmp.paste(Image.fromarray(ish, "RGBA"), (2, 2))
    hole = Image.alpha_composite(hole, tmp)
    save(hole, "punch.png")

    # --- concertina panel shading (196 x 468) ----------------------------------------------------------------
    save(hgrad(196, 4, [(0, (255, 255, 255, .22)), (.6, (255, 255, 255, .04)), (1, (60, 45, 30, .06))]), "pnl_lit.png")
    save(hgrad(196, 4, [(0, (60, 45, 30, .10)), (.7, (60, 45, 30, .20)), (1, (60, 45, 30, .28))]), "pnl_away.png")
    save(vgrad(4, 468, [(0, (255, 255, 255, .18)), (.4, (255, 255, 255, 0)), (1, (255, 255, 255, 0))]), "pnl_focus.png")
    hlp = np.zeros((16, 16, 4), np.uint8)
    hlp[0:2, :] = (255, 255, 255, 230)
    hlp[15, :] = (60, 45, 30, 46)
    save(Image.fromarray(hlp, "RGBA"), "pnl_hl.png")
    # table shadow under a valley panel (blur 16 @ .24)
    save(shadow(Image.new("L", (196, 468), 255), 48, [(4, 8, 16, .24, 0)], (50, 40, 30)), "shadow_panel.png")
    save(shadow(Image.new("L", (196, 468), 255), 64, [(8, 20, 22, .30, 0)], (20, 30, 70)), "shadow_panel_on.png")

    # --- key caps (hints), radius 5 ---------------------------------------------------------------------------
    save(white_shape(rrect_mask(32, 32, 5)), "key.png")

    # --- notes (dialogs): crease shading across the middle (folded once, opened flat) ------------------------
    save(vgrad(4, 256, [(0, (255, 255, 255, .25)), (.30, (255, 255, 255, 0)), (.47, (60, 45, 30, 0)), (.497, (60, 45, 30, .10)),
                        (.5, (255, 255, 255, .55)), (.506, (60, 45, 30, .06)), (.6, (60, 45, 30, 0)), (1, (60, 45, 30, .05))]), "note_crease.png")
    # the halves while they open (turned away = darker)
    save(vgrad(4, 128, [(0, (50, 35, 20, .05)), (1, (50, 35, 20, .28))]), "half_top_shade.png")
    save(vgrad(4, 128, [(0, (50, 35, 20, .28)), (1, (50, 35, 20, .05))]), "half_bottom_shade.png")
    # OSD strip: crease along the top edge (rotatex hinge at the bottom), lit as it lays down
    save(vgrad(4, 128, [(0, (255, 255, 255, .8)), (.02, (255, 255, 255, 0)), (.03, (60, 45, 30, .14)), (.14, (60, 45, 30, 0)), (1, (60, 45, 30, .04))]), "strip_shade.png")
    save(vgrad(4, 128, [(0, (50, 35, 20, .30)), (1, (50, 35, 20, .10))]), "strip_turn.png")

    # --- vinyl disc (gatefold): 600 px, grooves, label hole --------------------------------------------------
    D = 600
    yy, xx = np.mgrid[0:D, 0:D].astype(np.float64)
    r = np.sqrt((xx - D / 2 + .5) ** 2 + (yy - D / 2 + .5) ** 2)
    disc = np.zeros((D, D, 4), np.float64)
    groove = 18 + 6 * (np.sin(r * 1.7) > 0) + 4 * np.sin(r * .21)
    shade = 1 + .5 * np.cos(np.arctan2(yy - D / 2, xx - D / 2) * 2) * (r > 110)
    val = np.clip(groove * shade, 8, 60)
    val = np.where(r < 205, 34 + 2 * np.sin(r * .9), val)  # run-out area
    disc[..., 0] = val
    disc[..., 1] = val
    disc[..., 2] = val + 2
    alpha = np.clip(D / 2 - r, 0, 1)
    alpha *= np.clip(r - 7, 0, 1)  # spindle hole
    disc[..., 3] = alpha * 255
    lab = np.clip(105 - r, 0, 1) * np.clip(r - 7, 0, 1)
    disc_img = Image.fromarray(np.clip(disc, 0, 255).astype(np.uint8), "RGBA")
    save(disc_img, "disc.png")
    labimg = np.zeros((D, D, 4), np.uint8)
    labimg[..., :3] = 255
    labimg[..., 3] = (lab * 255).astype(np.uint8)
    save(Image.fromarray(labimg, "RGBA"), "disc_label.png")
    # sleeve spine shading for the gatefold (the cover half seen from inside: cream with a gutter)
    save(hgrad(560, 4, [(0, (60, 45, 30, 0)), (.85, (60, 45, 30, .02)), (.97, (60, 45, 30, .12)), (1, (60, 45, 30, .22))]), "gate_l.png")
    save(hgrad(560, 4, [(0, (255, 255, 255, .7)), (2 / 560, (60, 45, 30, .18)), (.05, (60, 45, 30, .04)), (.15, (60, 45, 30, 0)), (1, (60, 45, 30, .05))]), "gate_r.png")

    # --- focus mount (generic focus, drawn 7 px outside the item; 9-slice border 16) ---------------------------
    for name in ("outline_2.png", "outline_3.png", "outline_2_round.png", "outline_3_round.png"):
        outer = rrect_mask(40, 40, 7)
        inner = Image.new("L", (40, 40), 0)
        inner.paste(rrect_mask(26, 26, 2), (7, 7))
        a = np.clip(np.asarray(outer, np.int32) - np.asarray(inner, np.int32), 0, 255).astype(np.uint8)
        im = Image.new("RGBA", (40, 40), (255, 255, 255, 0))
        im.putalpha(Image.fromarray(a))
        im.save(OUT.parent / "focus" / name)

    # --- Majan's shared utility textures, redrawn in Fold's language (same names: the forked windows use them)
    common = OUT.parent / "common"
    # 2px rounded outline (fields, radio boxes), 9-slice border 10
    outer = rrect_mask(32, 32, 5)
    inner = Image.new("L", (32, 32), 0)
    inner.paste(rrect_mask(28, 28, 3), (2, 2))
    a = np.clip(np.asarray(outer, np.int32) - np.asarray(inner, np.int32), 0, 255).astype(np.uint8)
    for name in ("rect_outline_1.png", "rect_outline_1_round8.png"):
        im = Image.new("RGBA", (32, 32), (255, 255, 255, 0))
        im.putalpha(Image.fromarray(a))
        im.save(common / name)
    # fills: chips (radius 3)
    for name in ("rect_square.png", "rect_round8.png"):
        white_shape(rrect_mask(32, 32, 3)).save(common / name)
    # the context-menu / system-menu panel Kodi stretches (border 2): cream stock with a 2px card edge
    pf = np.zeros((24, 24, 4), np.uint8)
    pf[..., :3] = (0xF6, 0xF1, 0xE7)
    pf[..., 3] = 255
    pf[0:2, :, :3] = (0xD9, 0xD1, 0xC1)
    pf[-2:, :, :3] = (0xD9, 0xD1, 0xC1)
    pf[:, 0:2, :3] = (0xD9, 0xD1, 0xC1)
    pf[:, -2:, :3] = (0xD9, 0xD1, 0xC1)
    Image.fromarray(pf, "RGBA").save(OUT.parent / "dialogs" / "panel_framed.png")

    # --- plot ellipsis: the end of a clamped textbox's last line fades into the paper
    save(hgrad(96, 4, [(0, (255, 255, 255, 0)), (.55, (255, 255, 255, 1)), (1, (255, 255, 255, 1))]), "fade_r.png")

    # --- OSD playhead: a punched hole riding the perforation (slider nib) + a clear slider bar
    Image.new("RGBA", (4, 34), (255, 255, 255, 0)).save(OUT / "clear34.png")
    nib = Image.open(OUT / "punch.png").convert("RGBA").resize((34, 34), Image.LANCZOS)
    ring = Image.new("L", (34 * SS, 34 * SS), 0)
    ImageDraw.Draw(ring).ellipse([2 * SS, 2 * SS, 32 * SS - 1, 32 * SS - 1], outline=255, width=3 * SS)
    ringimg = Image.new("RGBA", (34, 34), (29, 27, 24, 0))
    ringimg.putalpha(ring.resize((34, 34), Image.LANCZOS).point(lambda v: int(v * .55)))
    save(Image.alpha_composite(nib, ringimg), "punch_nib.png")

    # --- preview sheet -----------------------------------------------------------------------------------------
    sheet = Image.new("RGBA", (1600, 900), (0xE9, 0xE7, 0xE2, 255))
    sheet.paste(made["table"].resize((480, 270)), (10, 10))
    x, y = 500, 10
    for name in ("shadow_lift.png", "shadow_card.png", "tab_on.png", "tab_on_shadow.png", "stab.png", "punch.png", "stamp.png", "chip_shadow.png", "disc.png"):
        im = Image.open(OUT / name).convert("RGBA")
        im.thumbnail((200, 200))
        sheet.alpha_composite(im, (x, y))
        x += 210
        if x > 1400:
            x, y = 500, y + 220
    sheet.save(PREV / "fold_textures.png")
    print("textures ->", OUT)


if __name__ == "__main__":
    main()
