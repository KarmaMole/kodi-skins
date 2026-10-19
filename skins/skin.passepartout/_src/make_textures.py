"""Generate Passe-partout's mat textures (reproducible, numpy + Pillow).

Run:  python skins/skin.passepartout/_src/make_textures.py
Writes media/pp/*.png and _src/previews/mat_preview.png, prints the XML border= values.

The mat is the mockups' CSS rebuilt pixel for pixel (docs/concepts/mockups/Passepartout*.dc.html):

  .win  border 3px solid #FFFFFF #F2F0EC #E6E3DE #FBFAF8   (the bevel cut, white core, darker
        padding 1px on rgba(28,27,25,.25)                   bottom-right) + 1px hairline 25% ink
        box-shadow 0 0 0 1px rgba(28,27,25,.07)             outer 1px ring
  .dep  inset 0 4px 5px -2px rgba(18,16,14,.42)             inner shadow over the picture's top
        inset 4px 0 5px -3px rgba(18,16,14,.26)             ... and left edge
        inset -1px -1px 0 rgba(255,255,255,.10)             1px light on the bottom/right inside edge
  .lift 0 2px 4px s/.10, 0 24px 46px -14px s/.34, 0 56px 100px -36px s/.30   (focused print only)

Everything is rendered at SS x supersampling and box-filtered down. 9-slice textures stay at 1x
pixel size on purpose: Kodi uses the border= value both as texture pixels and as GUI units, so a
2x bitmap would draw 2x corners; at the Shield's 1080p GUI 1x is exactly one screen pixel.

Shadows:
  * RGB is a neutral dark grey (G=62) and the XML tints them with colordiffuse = the paper colour
    (TMDb Helper Colors.Main): grey x paper = a darker version of the paper's own hue, which is
    what the mockups' --s colour does ("tinted toward the paper").
  * Alpha is dithered (triangular noise, +-1 LSB) before 8-bit quantisation, so the long soft
    falloffs don't band on the Shield.
  * The inside of the print rect is cleared (CSS draws outer shadows only outside the box).
  * 9-slice: corner patches are cut from a large render so the stretched middle strips are
    constant along their length (checked: max deviation printed).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
PREVIEW = HERE / "previews"
SS = 4
RNG = np.random.default_rng(20261018)
SHADOW_GREY = 62
BORDERS: dict[str, str] = {}


def gauss_blur(a: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        return a
    r = int(np.ceil(sigma * 3.5))
    x = np.arange(-r, r + 1)
    k = np.exp(-(x ** 2) / (2 * sigma ** 2))
    k /= k.sum()
    pad = np.pad(a, r, mode="edge")
    out = np.apply_along_axis(lambda v: np.convolve(v, k, mode="valid"), 0, pad)
    out = np.apply_along_axis(lambda v: np.convolve(v, k, mode="valid"), 1, out)
    return out


def downsample(a: np.ndarray, f: int) -> np.ndarray:
    h, w = a.shape[0] // f, a.shape[1] // f
    return a[: h * f, : w * f].reshape(h, f, w, f, *a.shape[2:]).mean(axis=(1, 3))


def to_png(rgb, alpha: np.ndarray, dither: bool) -> Image.Image:
    a = alpha * 255.0
    if dither:
        a = a + (RNG.random(a.shape) - RNG.random(a.shape))  # triangular, +-1 LSB
    a = np.clip(np.round(a), 0, 255).astype(np.uint8)
    h, w = a.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = np.asarray(rgb, np.uint8) if np.ndim(rgb) == 1 else rgb
    out[..., 3] = a
    return Image.fromarray(out, "RGBA")


def save(img: Image.Image, rel: str, border: str | None = None) -> None:
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)
    if border:
        BORDERS[rel] = border
    print(f"  {rel:28s} {img.size[0]}x{img.size[1]}" + (f"  border=\"{border}\"" if border else ""))


# ----------------------------------------------------------------------------- bevel
def make_bevel() -> None:
    """Frame overlay. XML: frame control = print rect grown 1px on every side (outer ring);
    the picture sits at print rect inset 4px (3px bevel + 1px hairline)."""
    B = 16                         # border (texture px == GUI px)
    C = 2                          # stretched transparent centre
    N = 2 * B + C                  # texture size
    s = SS
    W = N * s
    rgba = np.zeros((W, W, 4), np.float64)

    def over(dst, colour, alpha):
        a = alpha[..., None]
        dst[..., :3] = dst[..., :3] * (1 - a) + np.asarray(colour, float)[None, None, :] * a
        dst[..., 3] = dst[..., 3] * (1 - alpha) + alpha

    yy, xx = np.mgrid[0:W, 0:W] + 0.5
    # geometry in texture px (box spans 1..N-1; ring 0..1; bevel 1..4; hairline 4..5; picture 5..)
    def rect(x0, y0, x1, y1):
        return ((xx >= x0 * s) & (xx < x1 * s) & (yy >= y0 * s) & (yy < y1 * s)).astype(float)

    lo, hi = 1, N - 1
    ring = rect(0, 0, N, N) - rect(lo, lo, hi, hi)
    over(rgba, (28, 27, 25), ring * 0.07)
    # bevel: 3px, four colours meeting on the diagonals (CSS border joins)
    bev = rect(lo, lo, hi, hi) - rect(lo + 3, lo + 3, hi - 3, hi - 3)
    u = xx / s - lo
    v = yy / s - lo
    size = hi - lo
    top = (v <= u) & (v <= size - u)
    bottom = (size - v <= u) & (size - v <= size - u)
    left = (u < v) & (u < size - v) & ~top & ~bottom
    right = ~top & ~bottom & ~left
    col = np.zeros((W, W, 3))
    col[top] = (0xFF, 0xFF, 0xFF)
    col[right] = (0xF2, 0xF0, 0xEC)
    col[bottom] = (0xE6, 0xE3, 0xDE)
    col[left] = (0xFB, 0xFA, 0xF8)
    a = bev[..., None]
    rgba[..., :3] = rgba[..., :3] * (1 - a) + col * a
    rgba[..., 3] = rgba[..., 3] * (1 - bev) + bev
    # hairline: padding 1px on rgba(28,27,25,.25)
    hair = rect(lo + 3, lo + 3, hi - 3, hi - 3) - rect(lo + 4, lo + 4, hi - 4, hi - 4)
    over(rgba, (28, 27, 25), hair * 0.25)
    # inner shadows over the picture (picture area = 5 .. N-5)
    p0, p1 = lo + 4, hi - 4
    pic = rect(p0, p0, p1, p1)
    # big virtual picture so the shadow is the edge behaviour, then cut: render along each axis
    def inset(dx, dy, blur, spread, alpha):
        # hole = picture rect shifted by (dx,dy) and grown by -spread
        hole = rect(p0 + dx + spread, p0 + dy + spread, p1 + 400, p1 + 400)
        # extend the hole far to the bottom/right: our tile is a corner of a large picture
        sh = gauss_blur(1.0 - hole, blur / 2 * s)
        return sh * pic * alpha

    # the tile is symmetric only for the bevel; shadows live on the top/left edges, the highlight
    # on the bottom/right edges. Build each quadrant from the proper corner of a large picture.
    top_left = 1 - (1 - inset(0, 4, 5, -2, 0.42)) * (1 - inset(4, 0, 5, -3, 0.26))
    # top-left render is valid for the top and left edges; the bottom/right edges get no shadow
    m = np.zeros((W, W))
    half = W // 2
    m[:half, :] = top_left[:half, :]
    m[:, :half] = np.maximum(m[:, :half], top_left[:, :half])
    # the top edge's shadow continues along the full width; the left edge's along the full height
    m[:half, half:] = np.repeat(top_left[:half, half - 1:half], W - half, axis=1)
    m[half:, :half] = np.repeat(top_left[half - 1:half, :half], W - half, axis=0)
    m *= pic
    over(rgba, (18, 16, 14), m)
    # bottom/right inner highlight: 1px white 10% on the picture's inside edge
    hl = (rect(p0, p1 - 1, p1, p1) + rect(p1 - 1, p0, p1, p1)).clip(0, 1)
    over(rgba, (255, 255, 255), hl * 0.10)

    small = downsample(rgba, s)
    rgb = np.where(small[..., 3:4] > 0, small[..., :3] / np.maximum(small[..., 3:4], 1e-6), 255)
    rgb = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    img = to_png(rgb, small[..., 3], dither=False)
    # buffer: the stretched centre (B..B+C) must be fully transparent (LESSONS 4)
    arr = np.array(img)
    print("      centre alpha max", arr[B - 1:B + C + 1, B - 1:B + C + 1, 3].max())
    assert arr[B:B + C, B:B + C, 3].max() == 0, "bevel centre not clear"
    save(img, "pp/bevel.png", f"{B}")


# ----------------------------------------------------------------------------- shadows
def outer_shadow(box_w, box_h, margins, layers, s=2):
    """Render CSS outer box-shadows for a box of box_w x box_h; margins (l,t,r,b) around it.
    layers: (dx, dy, blur, spread, alpha). Returns float alpha at 1x, interior cleared."""
    ml, mt, mr, mb = margins
    W = (ml + box_w + mr) * s
    H = (mt + box_h + mb) * s
    yy, xx = np.mgrid[0:H, 0:W] + 0.5
    total = np.zeros((H, W))
    for dx, dy, blur, spread, alpha in layers:
        x0 = (ml + dx - spread) * s
        y0 = (mt + dy - spread) * s
        x1 = (ml + box_w + dx + spread) * s
        y1 = (mt + box_h + dy + spread) * s
        shape = ((xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)).astype(float)
        sh = gauss_blur(shape, blur / 2 * s) * alpha
        total = 1 - (1 - total) * (1 - sh)
    a = downsample(total, s)
    inside = np.zeros_like(a, bool)
    inside[mt:mt + box_h, ml:ml + box_w] = True
    a[inside] = 0
    return a


def nine_slice_shadow(name, layers, margins, k, preview_box=(400, 600)):
    """Cut a 9-slice shadow: corner patches of (margin + k) from a large render, 2px middles."""
    ml, mt, mr, mb = margins
    kl, kt, kr, kb = k
    big_w, big_h = kl + kr + 600, kt + kb + 600
    a = outer_shadow(big_w, big_h, margins, layers)
    H, W = a.shape
    cols = list(range(0, ml + kl)) + [ml + kl + 300, ml + kl + 301] + list(range(W - (mr + kr), W))
    rows = list(range(0, mt + kt)) + [mt + kt + 300, mt + kt + 301] + list(range(H - (mb + kb), H))
    # check the middles are constant along the stretch direction (within 1 LSB)
    dev_x = np.abs(a[:, ml + kl:W - (mr + kr)] - a[:, ml + kl + 300:ml + kl + 301]).max() * 255
    dev_y = np.abs(a[mt + kt:H - (mb + kb), :] - a[mt + kt + 300:mt + kt + 301, :]).max() * 255
    tile = a[np.ix_(rows, cols)]
    img = to_png((SHADOW_GREY,) * 3, tile, dither=True)
    border = f"{ml + kl},{mt + kt},{mr + kr},{mb + kb}"
    save(img, f"pp/{name}.png", border)
    print(f"      stretch deviation x {dev_x:.2f} LSB, y {dev_y:.2f} LSB; "
          f"min print size {kl + kr + 2}x{kt + kb + 2}; XML rect = print grown by {margins}")
    return img


def make_shadows() -> None:
    lift = [(0, 2, 4, 0, 0.10), (0, 24, 46, -14, 0.34), (0, 56, 100, -36, 0.30)]
    # lift: the focused print (hang 408x608, wall label 488x728, music 488x488, home 1100x620)
    nine_slice_shadow("lift", lift, margins=(80, 24, 80, 180), k=(150, 230, 150, 170))
    # lift_s: salon focus / small cards (half-strength geometry)
    lift_s = [(0, 1, 3, 0, 0.10), (0, 12, 24, -8, 0.30), (0, 28, 52, -18, 0.24)]
    nine_slice_shadow("lift_s", lift_s, margins=(44, 14, 44, 96), k=(80, 120, 80, 100))
    # lift_xs: salon grid focus (fits inside the 40px row gap)
    lift_xs = [(0, 1, 3, 0, 0.12), (0, 10, 22, -6, 0.32)]
    nine_slice_shadow("lift_xs", lift_xs, margins=(24, 8, 24, 36), k=(40, 40, 40, 40))
    # placard: the ink button's shadow (0 18px 30px -14px rgba(60,46,32,.55))
    placard = [(0, 18, 30, -14, 0.55)]
    nine_slice_shadow("placard", placard, margins=(24, 4, 24, 56), k=(50, 30, 50, 30))
    # card: dialog paper cards on the light veil
    card = [(0, 2, 6, 0, 0.08), (0, 30, 60, -20, 0.26)]
    nine_slice_shadow("card", card, margins=(48, 16, 48, 104), k=(100, 130, 100, 120))


def make_card_full() -> None:
    """Context-menu card as ONE 9-slice image (Kodi resizes only image 999): shadow + 1px edge at
    10% ink + white fill. XML tints it with the paper colour (white x paper = the paper)."""
    card = [(0, 2, 6, 0, 0.08), (0, 30, 60, -20, 0.26)]
    ml, mt, mr, mb = 48, 16, 48, 104
    kl, kt, kr, kb = 100, 130, 100, 120
    bw, bh = kl + kr + 600, kt + kb + 600
    a = outer_shadow(bw, bh, (ml, mt, mr, mb), card)
    H, W = a.shape
    grey = np.full((H, W, 3), SHADOW_GREY, float)
    alpha = a + (RNG.random(a.shape) - RNG.random(a.shape)) / 255 * (a > 0)
    # edge ring: 1px just outside the card at 10% ink (premultiply onto the shadow)
    ring = np.zeros((H, W), bool)
    ring[mt - 1, ml - 1:ml + bw + 1] = ring[mt + bh, ml - 1:ml + bw + 1] = True
    ring[mt - 1:mt + bh + 1, ml - 1] = ring[mt - 1:mt + bh + 1, ml + bw] = True
    ra = 0.10
    out_a = ra + alpha * (1 - ra)
    out_rgb = (np.array([28, 27, 25]) * ra + grey * (alpha * (1 - ra))[..., None]) / np.maximum(out_a, 1e-6)[..., None]
    grey[ring] = out_rgb[ring]
    alpha[ring] = out_a[ring]
    grey[mt:mt + bh, ml:ml + bw] = 255
    alpha[mt:mt + bh, ml:ml + bw] = 1
    cols = list(range(0, ml + kl)) + [ml + kl + 300, ml + kl + 301] + list(range(W - (mr + kr), W))
    rows = list(range(0, mt + kt)) + [mt + kt + 300, mt + kt + 301] + list(range(H - (mb + kb), H))
    img = to_png(np.clip(grey, 0, 255).astype(np.uint8)[np.ix_(rows, cols)], np.clip(alpha, 0, 1)[np.ix_(rows, cols)], dither=False)
    save(img, "pp/card_full.png", f"{ml + kl},{mt + kt},{mr + kr},{mb + kb}")


def make_basics() -> None:
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "common/white.png")
    # watched dot, 10px in the mockup -> 20px (2x, scaled down by Kodi)
    s = 8
    n = 20 * s
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    disc = (((xx - n / 2) ** 2 + (yy - n / 2) ** 2) <= (n / 2 - s * 0.5) ** 2).astype(float)
    save(to_png((255, 255, 255), downsample(disc, s), dither=False), "pp/dot.png")
    # 1px hairline with a transparent buffer row (horizontal rules stretched in width only)
    a = np.zeros((4, 4))
    a[1, :] = 1
    save(to_png((255, 255, 255), a, dither=False), "pp/rule_h.png", "0,1,0,2")

    # 1px outline frame, 9-slice with a transparent buffer ring (LESSONS 4)
    a = np.zeros((6, 6))
    a[0, :] = a[-1, :] = a[:, 0] = a[:, -1] = 1
    save(to_png((255, 255, 255), a, dither=False), "pp/frame_1.png", "2")
    # underline: 1px at the bottom with a transparent buffer row above it (border 0,0,0,2)
    a = np.zeros((4, 4))
    a[3, :] = 1
    save(to_png((255, 255, 255), a, dither=False), "pp/underline.png", "0,0,0,2")
    # panel_shadow: 40px soft shadow left of a full-height side panel (baked warm dark, dithered)
    x = np.arange(40) + 0.5
    a = (0.28 * np.exp(-((40 - x) / 14.0) ** 2))[None, :].repeat(8, axis=0)
    save(to_png((40, 34, 28), a, dither=True), "pp/panel_shadow.png")
    # OSD playhead: slider bar (transparent) + nib (1px ink line) at 2x: 4x42 / 2x42 -> 1x21 at height 21
    save(Image.new("RGBA", (4, 42), (255, 255, 255, 0)), "pp/playhead_bar.png")
    save(Image.new("RGBA", (2, 42), (255, 255, 255, 255)), "pp/playhead.png")
    # frame_pad: a 1px frame around the block of a placard-sized control (margins 24/4/24/56)
    a = np.zeros((70, 60))
    a[4, 24:36] = a[13, 24:36] = 1
    a[4:14, 24] = a[4:14, 35] = 1
    save(to_png((255, 255, 255), a, dither=False), "pp/frame_pad.png", "26,6,26,58")
    # sheet_shadow: 40px soft shadow above a paper sheet rising from the bottom (dithered)
    y = np.arange(40) + 0.5
    a = (0.30 * np.exp(-((40 - y) / 14.0) ** 2))[:, None].repeat(8, axis=1)
    save(to_png((20, 18, 15), a, dither=True), "pp/sheet_shadow.png")
    # focus bar for forked overlay frames (placed 7px outside the item): 2px bar on the bottom edge
    a = np.zeros((40, 40))
    a[38:40, 7:33] = 1
    a[38:40, :] = 1
    save(to_png((255, 255, 255), a, dither=False), "pp/focus_bar.png", "16")
    # slider: 2px track in a 12px row, square nib 12px (2x)
    a = np.zeros((12, 8))
    a[5:7, :] = 1
    save(to_png((255, 255, 255), a, dither=False), "pp/slider_track.png")
    save(Image.new("RGBA", (24, 24), (255, 255, 255, 255)), "pp/slider_nib.png")
    # switches 40x22 drawn at 2x: off = 2px outline + knob left; on = solid with a knob cut out right
    W, H = 80, 44
    off = np.zeros((H, W))
    off[0:3, :] = off[-3:, :] = off[:, 0:3] = off[:, -3:] = 1
    off[9:35, 9:35] = 1
    save(to_png((255, 255, 255), off, dither=False), "pp/switch_off.png")
    on = np.ones((H, W))
    on[9:35, W - 35:W - 9] = 0
    save(to_png((255, 255, 255), on, dither=False), "pp/switch_on.png")


def placard_button(name, bw, bh, stretch_x=True):
    """Ink block + its baked shadow in one texture, for button texturefocus.
    The control is the block grown by (24, 4, 24, 56); XML: itemgap -= 48, textoffsety for the label."""
    ml, mt, mr, mb = 24, 4, 24, 56
    a = outer_shadow(bw, bh, (ml, mt, mr, mb), [(0, 18, 30, -14, 0.55)])
    h, w = a.shape
    rgb = np.zeros((h, w, 3))
    rgb[...] = (60, 46, 32)
    alpha = a.copy()
    rgb[mt:mt + bh, ml:ml + bw] = (0x1C, 0x1B, 0x19)
    alpha[mt:mt + bh, ml:ml + bw] = 1.0
    alpha = alpha + (RNG.random(alpha.shape) - RNG.random(alpha.shape)) / 255 * (alpha < 1)
    img = to_png(np.clip(rgb, 0, 255).astype(np.uint8), np.clip(alpha, 0, 1), dither=False)
    if stretch_x:
        k = 50
        cols = list(range(0, ml + k)) + [w // 2, w // 2 + 1] + list(range(w - (mr + k), w))
        img = Image.fromarray(np.asarray(img)[:, cols])
        save(img, f"pp/{name}.png", f"{ml + k},0,{mr + k},0")
    else:
        save(img, f"pp/{name}.png")


def make_placards() -> None:
    placard_button("placard_btn", 400, 64)          # 64px action buttons (wall label, OSD transport)
    placard_button("placard_btn56", 400, 56)        # 56px buttons (keyboard Space/Delete, small dialogs)
    placard_button("placard_key", 88, 88, False)    # keyboard key 88 x 88
    placard_button("placard_btn_key", 400, 88)      # keyboard keys of any width, 88 tall


def preview() -> None:
    """Paper + lifted print + neighbours, to eyeball against the mockup."""
    PREVIEW.mkdir(exist_ok=True)
    paper = np.array([0xD9, 0xE1, 0xDF], float)
    W, H = 1100, 760
    canvas = np.ones((H, W, 3)) * paper

    def nine(img: Image.Image, border, w, h):
        a = np.asarray(img).astype(float) / 255
        l, t, r, b = border
        th, tw = a.shape[:2]
        cols = np.r_[np.arange(l), np.linspace(l, tw - r - 1, max(1, w - l - r)).round().astype(int), np.arange(tw - r, tw)]
        rows = np.r_[np.arange(t), np.linspace(t, th - b - 1, max(1, h - t - b)).round().astype(int), np.arange(th - b, th)]
        return a[np.ix_(rows, cols)]

    def comp(dst, src, x, y, tint=None):
        h, w = src.shape[:2]
        rgb = src[..., :3] * (tint / 255 if tint is not None else 1)
        al = src[..., 3:4]
        dst[y:y + h, x:x + w] = dst[y:y + h, x:x + w] * (1 - al) + rgb * 255 * al

    def bstr(name):
        return [int(v) for v in BORDERS[name].split(",")] * (4 if "," not in BORDERS[name] else 1)

    lift = Image.open(MEDIA / "pp/lift.png")
    bevel = Image.open(MEDIA / "pp/bevel.png")
    art = np.ones((600, 400, 4))
    art[..., :3] = np.linspace(0.15, 0.45, 600)[:, None, None] * np.array([0.6, 0.8, 0.85])
    bx, by, bw, bh = 120, 60, 408, 608
    lb = bstr("pp/lift.png")
    l, t, r, b = 80, 24, 80, 180
    sh = nine(lift, lb, bw + l + r, bh + t + b)
    sh = sh[: H - (by - t), : W - (bx - l)]
    comp(canvas, sh, bx - l, by - t, tint=paper)
    canvas[by + 4:by + 4 + 600, bx + 4:bx + 4 + 400] = art[..., :3] * 255
    fr = nine(bevel, [16] * 4, bw + 2, bh + 2)
    comp(canvas, fr, bx - 1, by - 1)
    # small neighbour
    sx, sy, sw, shh = 600, 198, 224, 332
    canvas[sy + 4:sy + 4 + shh - 8, sx + 4:sx + 4 + sw - 8] = 90
    comp(canvas, nine(bevel, [16] * 4, sw + 2, shh + 2), sx - 1, sy - 1)
    Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).save(PREVIEW / "mat_preview.png")
    print(f"  preview -> {PREVIEW / 'mat_preview.png'}")


def main() -> None:
    print("writing textures")
    make_basics()
    make_bevel()
    make_shadows()
    make_placards()
    make_card_full()
    preview()
    print("XML borders:")
    for k, v in BORDERS.items():
        print(f"  {k}: border=\"{v}\"")


if __name__ == "__main__":
    main()
