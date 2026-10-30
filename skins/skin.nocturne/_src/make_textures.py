"""Nocturne texture generator (reproducible, seed-fixed). Started from the mockup generator
(docs/concepts/round4/mockups/nocturne_assets/make_assets.py); writes media/noc/.

    python skins/skin.nocturne/_src/make_textures.py

Every PNG here is a texture Kodi would load as-is:
  plaster.jpg            lit plaster wall (horizontally tileable for the corridor parallax)
  shroud_*.png           the darkness: deep blue-black with a soft transparent hole = the torch pool.
                         Drawn ABOVE the wall and art, it multiplies everything by (1 - alpha), which is real
                         light falloff using plain alpha blending (no blend modes needed).
  halo_white.png         outer halo, white -> colordiffuse ($INFO[...Colors.Main] or warm-white fallback)
  halo_*.png             pre-tinted previews of halo_white (what colordiffuse produces) for the mockups
  dust.png               one frame of the dust-mote loop, pre-masked to the beam (Kodi: dust_white + diffuse mask)
  frame.png              9-slice picture frame (border 16)
  shadow.png             9-slice baked drop shadow (border 64)
  glint.png              specular streak for the focused frame's top edge
  plaque.png             9-slice brushed brass plaque (border 26,0,26,0)
  pin.png                watched pin
  rail.png               9-slice brass rail with finials (border 34,0,34,0)
  picrail.png            thin picture rail rod (tile x)
  cornice.png            cornice moulding strip (tile x)
  filament.png           glowing progress filament (9-slice 12,0,12,0)
  lamp.png / cone.png    music room pendant lamp and its light volume
  ledge.png              record ledge (9-slice 24,0,24,0)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[1] / "media" / "noc"
OUT.mkdir(parents=True, exist_ok=True)
# cornice.png only feeds plaster_with_cornice(): it lives in _src/build, never in media/ (2026-10-30)
BUILD = Path(__file__).resolve().parent / "build"
# Drawn (kept so the noise RNG sequence stays the same) but named by no XML (removed from media/ 2026-10-30)
UNUSED = {"dust_white.png", "glow_row.png", "halo_warm.png"}
RNG = np.random.default_rng(1947)
WARM = np.array([255, 231, 194], float)          # 2700 K
VELVET = np.array([10, 12, 18], float)            # shroud colour (cool blue-black)


def save(a: np.ndarray, name: str, jpg=False):
    if name in UNUSED:
        return
    a = np.clip(a, 0, 255).astype(np.uint8)
    im = Image.fromarray(a, "RGBA" if a.shape[-1] == 4 else "RGB")
    dst = OUT
    if name == "cornice.png":
        BUILD.mkdir(exist_ok=True)
        dst = BUILD
    if jpg:
        im.convert("RGB").save(dst / name, quality=92)
    else:
        im.save(dst / name, optimize=True)
    print(name, im.size)


def fnoise(h, w, beta=2.0, ax=1.0, ay=1.0, seed=None):
    """Periodic 1/f^beta noise via FFT, anisotropic (ax>ay stretches horizontally). Returns -1..1-ish."""
    rng = np.random.default_rng(seed) if seed is not None else RNG
    wn = rng.standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None] * ay
    fx = np.fft.fftfreq(w)[None, :] * ax
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1
    spec = np.fft.fft2(wn) / f ** (beta / 2)
    spec[0, 0] = 0
    n = np.real(np.fft.ifft2(spec))
    return n / (n.std() * 3 + 1e-9)


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ plaster
def plaster():
    h, w = 1080, 1920
    big = fnoise(h, w, 2.6, seed=1)                       # mottling
    trowel = fnoise(h, w, 2.2, ax=1.6, ay=0.35, seed=2)   # long horizontal sweeps
    trowel2 = fnoise(h, w, 2.2, ax=0.5, ay=1.4, seed=3)
    fine = fnoise(h, w, 1.1, seed=4)                       # grain
    pits = (RNG.random((h, w)) > 0.9985).astype(float)
    pits = np.array(Image.fromarray((pits * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
    # trowel edges: sharpen ridges where sweeps cross zero
    ridge = np.exp(-(trowel / 0.05) ** 2) * 0.5 + np.exp(-(trowel2 / 0.06) ** 2) * 0.3
    # relief: height map shaded by a raking light from upper left (the "Rembrandt" key)
    sw1 = fnoise(h, w, 3.4, ax=1.8, ay=0.45, seed=5)       # broad trowel sweeps
    sw2 = fnoise(h, w, 3.4, ax=0.6, ay=1.5, seed=6)
    cut = np.abs(fnoise(h, w, 2.6, ax=1.6, ay=0.5, seed=8))  # trowel edges = creases
    hmap = 1.0 * sw1 + 0.7 * sw2 - 0.35 * np.exp(-(cut / 0.04) ** 2) + 0.04 * fine - 0.6 * pits
    gx = (np.roll(hmap, -1, 1) - np.roll(hmap, 1, 1)) * 0.5
    gy = (np.roll(hmap, -1, 0) - np.roll(hmap, 1, 0)) * 0.5
    relief = -(gx * 0.7 + gy * 0.7)
    relief = relief / (relief.std() * 3 + 1e-9)
    lum = 1 + 0.13 * big + 0.04 * trowel + 0.035 * fine + 0.16 * relief - 0.05 * ridge - 0.3 * pits
    base = np.array([78, 72, 65], float)                   # lit plaster: warm stone grey
    rgb = lum[..., None] * base[None, None, :]
    rgb += RNG.uniform(-1.2, 1.2, (h, w, 1))               # dither
    save(rgb, "plaster_raw.jpg", jpg=True)


def plaster_with_cornice():
    """0.9.2: the cornice baked into the wall, so a window draws one opaque full-screen layer for both."""
    wall = Image.open(OUT / "plaster_raw.jpg").convert("RGBA")
    wall.alpha_composite(Image.open(BUILD / "cornice.png").convert("RGBA"), (0, 0))
    wall.convert("RGB").save(OUT / "plaster.jpg", quality=92)
    (OUT / "plaster_raw.jpg").unlink()
    print("plaster.jpg (cornice baked)")


# ------------------------------------------------------------------ shroud
def light_field(h, w, lights, scale=1.0):
    """lights: list of dict(cx, cy, r0, sig, spill, rs, sx, sy, gain). coords in output px."""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    xx, yy = xx * scale, yy * scale
    total = np.zeros((h, w))
    for L in lights:
        dx = (xx - L["cx"]) / L.get("sx", 1.0)
        dy = (yy - L["cy"]) / L.get("sy", 1.0)
        r = np.sqrt(dx * dx + dy * dy)
        e = np.maximum(r - L["r0"], 0)
        core = np.exp(-0.5 * (e / L["sig"]) ** 2)
        spill = L["spill"] * np.exp(-e / L["rs"])
        I = np.clip(core + spill * (1 - core), 0, 1) * L.get("gain", 1.0)
        total = 1 - (1 - total) * (1 - I)                  # union of lights
    return total


def shroud_from(I, imin, name):
    T = np.maximum(I, imin)
    a = 1 - T
    a = a + RNG.uniform(-1.0, 1.0, a.shape) / 255.0         # dither against banding
    h, w = I.shape
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = VELVET
    rgba[..., 3] = np.clip(a, 0, 1) * 255
    save(rgba, name)


def halo(name, color=(255, 255, 255), size=1024, a_core=0.05, a_ring=0.16, ring=0.30, width=0.16):
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    a = a_core * np.exp(-(r / 0.35) ** 2) + a_ring * np.exp(-((r - ring) / width) ** 2)
    a *= smooth(1 - r, 0, 0.25)
    rgba = np.zeros((size, size, 4))
    rgba[..., :3] = np.array(color, float)
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.6, 0.6, a.shape) / 255, 0, 1) * 255
    save(rgba, name)


# ------------------------------------------------------------------ dust
def glow(name, size=512, color=WARM, a0=0.32):
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    a = a0 * np.exp(-(r / 0.42) ** 2) * smooth(1 - r, 0, 0.3)
    rgba = np.zeros((size, size, 4))
    rgba[..., :3] = color
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.6, 0.6, a.shape) / 255, 0, 1) * 255
    save(rgba, name)


def dust(name, size=600, n=230, seed=7, masked=True, bokeh=14):
    rng = np.random.default_rng(seed)
    S = 3
    big = Image.new("L", (size * S, size * S), 0)
    d = ImageDraw.Draw(big)
    for i in range(n):
        x, y = rng.random() * size * S, rng.random() * size * S
        rad = (0.5 + rng.random() ** 3 * 1.6) * S
        v = int(110 + rng.random() * 145)
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=v)
    sharp = big.filter(ImageFilter.GaussianBlur(0.9 * S)).resize((size, size), Image.LANCZOS)
    # a few out-of-focus motes close to the lens
    bl = Image.new("L", (size, size), 0)
    d2 = ImageDraw.Draw(bl)
    for i in range(bokeh):
        x, y = rng.random() * size, rng.random() * size
        rad = 5 + rng.random() * 9
        d2.ellipse([x - rad, y - rad, x + rad, y + rad], fill=int(40 + rng.random() * 40))
    bl = bl.filter(ImageFilter.GaussianBlur(2.2))
    a = np.maximum(np.array(sharp, float), np.array(bl, float)) / 255.0
    if masked:
        yy, xx = np.mgrid[0:size, 0:size].astype(float)
        r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
        a *= smooth(1 - r, 0.0, 0.55)
    rgba = np.zeros((size, size, 4))
    rgba[..., :3] = WARM if masked else 255
    rgba[..., 3] = a * 255
    save(rgba, name)


# ------------------------------------------------------------------ frame / shadow / glint
def frame():
    s, b = 64, 16
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    d = np.minimum(np.minimum(xx, yy), np.minimum(s - 1 - xx, s - 1 - yy))  # distance to outer edge
    rgba = np.zeros((s, s, 4))
    # moulding (0..12): black lacquer, rounded profile lit from above
    m = d < 12.5
    t = np.clip(d / 12.0, 0, 1)
    prof = np.cos((t - 0.35) * np.pi) * 0.5 + 0.5           # highlight near the outer third
    top = (yy <= np.minimum(xx, s - 1 - xx)) & (yy < s / 2)
    left = (xx < yy) & (xx < s - 1 - yy) & (xx < s / 2)
    bottom = (s - 1 - yy <= np.minimum(xx, s - 1 - xx)) & (yy >= s / 2)
    facing = np.where(top, 1.0, np.where(left, 0.6, np.where(bottom, 0.22, 0.4)))
    lv = 6 + 24 * prof ** 2.2 * facing
    lip = np.exp(-((d - 1.2) / 0.9) ** 2) * np.where(top, 40, np.where(left, 18, 3))   # outer lip catches light
    lv = lv + lip
    col = np.stack([lv * 1.0, lv * 0.9, lv * 0.78], -1)
    rgba[m, :3] = col[m]
    rgba[m, 3] = 255
    # gilt slip (12.5..15.5): dull gold line, bright on the top/left
    g = (d >= 12.5) & (d < 15.5)
    gl = np.where(top | left, 1.0, 0.55)
    gold = np.stack([170 * gl, 136 * gl, 78 * gl], -1)
    rgba[g, :3] = gold[g]
    rgba[g, 3] = 255
    # inner shadow line onto the art (15.5..16)
    i = (d >= 15.5) & (d < 16)
    rgba[i, :3] = 0
    rgba[i, 3] = 200
    save(rgba, "frame.png")


def shadow():
    s, b = 192, 64
    im = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(im)
    d.rectangle([b - 6, b + 10, s - b + 6, s - b + 30], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(18))
    a = np.array(im, float) / 255 * 0.85
    rgba = np.zeros((s, s, 4))
    rgba[..., 3] = a * 255
    save(rgba, "shadow.png")


def glint():
    w, h = 512, 9
    xx = np.linspace(-1, 1, w)[None, :]
    yy = np.linspace(-1, 1, h)[:, None]
    a = np.exp(-(xx / 0.42) ** 2) * np.exp(-(yy / 0.22) ** 2)
    a += 0.35 * np.exp(-(xx / 0.8) ** 2) * np.exp(-(yy / 0.5) ** 2)
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = np.array([255, 244, 222])
    rgba[..., 3] = np.clip(a, 0, 1) * 255
    save(rgba, "glint.png")


# ------------------------------------------------------------------ brass
def brass_surface(h, w, seed):
    brushed = fnoise(h, w, 1.4, ax=3.0, ay=0.04, seed=seed)
    yy = np.linspace(0, 1, h)[:, None]
    # vertical light gradient: lit top, specular band, darker bottom
    v = 0.78 + 0.28 * np.exp(-((yy - 0.28) / 0.16) ** 2) - 0.22 * yy
    v = v + 0.06 * brushed
    base = np.array([186, 146, 82], float)
    rgb = v[..., None] * base
    # warm specular tint
    rgb += (np.exp(-((yy - 0.28) / 0.1) ** 2) * 38)[..., None] * np.array([1, 0.9, 0.7])
    return rgb


def plaque(name="plaque.png", screws=True, seed=11, h=64):
    w, r = 320, 5
    rgb = brass_surface(h, w, seed)
    a = np.ones((h, w))
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    # rounded corners
    for cx, cy in [(r, r), (w - 1 - r, r), (r, h - 1 - r), (w - 1 - r, h - 1 - r)]:
        m = ((xx < r) | (xx > w - 1 - r)) & ((yy < r) | (yy > h - 1 - r))
        dd = np.hypot(xx - cx, yy - cy)
        a = np.where(m & (np.abs(xx - cx) <= r) & (np.abs(yy - cy) <= r), np.clip(r + 0.5 - dd, 0, 1), a)
    # bevel: 3px chamfer, light from top
    d = np.minimum(np.minimum(xx, yy), np.minimum(w - 1 - xx, h - 1 - yy))
    bev = d < 3
    topish = yy < h / 2
    rgb[bev & topish] *= 1.28
    rgb[bev & ~topish] *= 0.55
    # engraved border line
    line = (np.abs(d - 6) < 0.6)
    rgb[line] *= 0.62
    line2 = (np.abs(d - 7) < 0.6)
    rgb[line2] = np.minimum(rgb[line2] * 1.15, 255)
    # screws in the side borders
    for cx in ((14, w - 15) if screws else ()):
        cy = h / 2
        dd = np.hypot(xx - cx, yy - cy)
        s = dd < 4.2
        sh = 0.75 + 0.45 * np.clip((cy - yy) / 4.2, -1, 1)
        rgb[s] = (rgb[s] * sh[s][:, None])
        ring = (np.abs(dd - 4.4) < 0.7)
        rgb[ring] *= 0.45
        slot = s & (np.abs(yy - cy) < 0.7) & (np.abs(xx - cx) < 3)
        rgb[slot] *= 0.45
    rgba = np.dstack([np.clip(rgb, 0, 255), a * 255])
    save(rgba, name)


def pin():
    s = 28
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    c = s / 2 - 0.5
    r = np.hypot(xx - c, yy - c)
    R = 10
    a = np.clip(R + 0.5 - r, 0, 1)
    nz = np.sqrt(np.clip(1 - (r / R) ** 2, 0, 1))
    lx, ly, lz = -0.4, -0.6, 0.7
    nx, ny = (xx - c) / R, (yy - c) / R
    lam = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
    spec = lam ** 18
    rgb = np.array([150, 112, 52])[None, None, :] * (0.35 + 0.9 * lam[..., None]) + 255 * spec[..., None] * 0.9
    # contact shadow
    sh = Image.new("L", (s, s), 0)
    ImageDraw.Draw(sh).ellipse([c - R + 2, c - R + 4, c + R + 2, c + R + 4], fill=150)
    sh = np.array(sh.filter(ImageFilter.GaussianBlur(2)), float) / 255
    rgba = np.zeros((s, s, 4))
    rgba[..., :3] = rgb * a[..., None]
    alpha = a + sh * (1 - a)
    rgba[..., :3] = np.where(alpha[..., None] > 0, rgba[..., :3] / np.maximum(alpha[..., None], 1e-6), 0)
    rgba[..., 3] = alpha * 255
    save(rgba, "pin.png")


def rail():
    h, w = 40, 512
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cy, R = 20, 9
    t = (yy - cy) / R
    inside = np.abs(t) <= 1
    nz = np.sqrt(np.clip(1 - t * t, 0, 1))
    lam = np.clip(-t * 0.65 + nz * 0.75, 0, 1)
    brushed = fnoise(h, w, 1.3, ax=3, ay=0.05, seed=21)
    base = np.array([180, 140, 76], float)
    rgb = base * (0.22 + 0.85 * lam[..., None]) * (1 + 0.05 * brushed[..., None]) + 255 * (lam ** 22)[..., None] * 0.85
    a = np.clip(R + 0.5 - np.abs(yy - cy), 0, 1)
    # finials (balls) at both ends inside the 34px borders
    for cx in (17, w - 18):
        rr = np.hypot(xx - cx, yy - cy)
        Rb = 13
        ball = rr <= Rb + 0.5
        nzb = np.sqrt(np.clip(1 - (rr / Rb) ** 2, 0, 1))
        lb = np.clip(((xx - cx) / Rb) * -0.3 + ((yy - cy) / Rb) * -0.6 + nzb * 0.75, 0, 1)
        col = base * (0.22 + 0.85 * lb[..., None]) + 255 * (lb ** 22)[..., None] * 0.9
        rgb = np.where(ball[..., None], col, rgb)
        a = np.maximum(a, np.clip(Rb + 0.5 - rr, 0, 1))
        # keep the rod from showing beyond the finials
        if cx < w / 2:
            a = np.where(xx < cx - Rb, 0, a)
        else:
            a = np.where(xx > cx + Rb, 0, a)
    save(np.dstack([np.clip(rgb, 0, 255), a * 255]), "rail.png")


def picrail():
    h, w = 22, 512
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cy, R = 11, 5
    t = (yy - cy) / R
    nz = np.sqrt(np.clip(1 - t * t, 0, 1))
    lam = np.clip(-t * 0.6 + nz * 0.8, 0, 1)
    base = np.array([168, 130, 70], float)
    rgb = base * (0.2 + 0.85 * lam[..., None]) + 255 * (lam ** 24)[..., None] * 0.8
    a = np.clip(R + 0.5 - np.abs(yy - cy), 0, 1)
    save(np.dstack([np.clip(rgb, 0, 255), a * 255]), "picrail.png")


def cornice():
    """Moulding profile, top of wall. Height map per row -> shading with light from below-front (the torch)."""
    h, w = 150, 1920
    y = np.arange(h, dtype=float)
    hmap = np.zeros(h)
    # crown cove
    hmap += 26 * smooth(y, 0, 40) * (1 - smooth(y, 40, 70)) + 18 * smooth(y, 40, 70)
    # bead
    hmap += 7 * np.exp(-((y - 82) / 4.0) ** 2)
    # fillet steps
    hmap += 6 * (1 - smooth(y, 96, 100)) - 2 * smooth(y, 120, 124)
    hmap += 3 * np.exp(-((y - 112) / 3.0) ** 2)
    hmap -= 18 * smooth(y, 124, 150) * 0
    g = np.gradient(hmap)
    # light from below (torch is below the cornice) -> faces tilting down (g<0 means surface faces down) are lit
    lit = 0.55 + np.clip(-g * 0.08, -0.4, 0.45)
    lit[y > 124] = 0.62
    noise = fnoise(h, w, 2.2, seed=31) * 0.06 + fnoise(h, w, 1.1, seed=32) * 0.03
    base = np.array([78, 72, 65], float)
    rgb = (lit[:, None] + noise)[..., None] * base
    # deep shadow line under the cornice and occlusion at the ceiling
    rgb *= (1 - 0.6 * np.exp(-((y - 126) / 2.5) ** 2))[:, None, None]
    rgb *= (0.35 + 0.65 * smooth(y, 0, 26))[:, None, None]
    a = (1 - smooth(y, 128, 150))[:, None] * np.ones((1, w))
    a = np.maximum(a, 0.6 * np.exp(-((y - 130) / 4.0) ** 2)[:, None])  # keep the shadow line
    rgba = np.dstack([rgb, a * 255])
    save(rgba, "cornice.png")


def filament():
    h, w = 24, 128
    yy = np.linspace(-1, 1, h)[:, None]
    xx = np.arange(w)[None, :]
    core = np.exp(-(yy / 0.07) ** 2)
    glow = 0.55 * np.exp(-(yy / 0.35) ** 2)
    a = np.clip(core + glow, 0, 1) * np.ones((1, w))
    a *= smooth(xx, 0, 8) * smooth(w - 1 - xx, 0, 3) * 0 + 1
    rgb = np.zeros((h, w, 3))
    rgb[:] = WARM
    rgb += (core[..., None] * np.array([0, 18, 50])) * np.ones((1, w, 1))   # white-hot core
    save(np.dstack([np.clip(rgb, 0, 255), a * 255]), "filament.png")


def lamp():
    w, h = 420, 300
    S = 2
    W, H = w * S, h * S
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    cx = W / 2
    rgba = np.zeros((H, W, 4))
    # cord
    cord = (np.abs(xx - cx) < 1.6 * S) & (yy < 120 * S)
    rgba[cord] = [30, 28, 26, 255]
    # canopy cap
    cap = ((xx - cx) / (14 * S)) ** 2 + ((yy - 124 * S) / (10 * S)) ** 2 <= 1
    rgba[cap] = [120, 92, 48, 255]
    # dome shade: from y=130 to 236, half-width growing from 40 to 190
    top, bot = 130 * S, 236 * S
    t = np.clip((yy - top) / (bot - top), 0, 1)
    hw = (40 + 150 * np.sin(t * np.pi / 2) ** 1.4) * S
    shade = (yy >= top) & (yy <= bot) & (np.abs(xx - cx) <= hw)
    u = (xx - cx) / np.maximum(hw, 1)
    nz = np.sqrt(np.clip(1 - u * u, 0, 1))
    lam = np.clip(nz * 0.55 - u * 0.35 - t * 0.25, 0, 1)
    base = np.array([120, 88, 44], float)
    col = base * (0.12 + 0.75 * lam[..., None] ** 1.6) + 255 * (lam ** 14)[..., None] * 0.45
    rgba[shade, :3] = col[shade]
    rgba[shade, 3] = 255
    # glowing rim / bulb seen from below
    rim = (((xx - cx) / (188 * S)) ** 2 + ((yy - bot) / (16 * S)) ** 2 <= 1) & (yy >= bot - 2 * S)
    inner = ((xx - cx) / (180 * S)) ** 2 + ((yy - bot) / (12 * S)) ** 2
    rgba[rim, :3] = (WARM * 1.0 + np.array([0, 15, 45]))[None, :] * (1 - 0.25 * np.clip(inner[rim], 0, 1))[:, None]
    rgba[rim, 3] = 255
    # bloom below rim
    glow = np.exp(-(((xx - cx) / (110 * S)) ** 2 + ((yy - bot - 8 * S) / (26 * S)) ** 2) * 1.5) * 0.55
    glow[yy < bot] *= 0
    a0 = rgba[..., 3] / 255
    na = a0 + glow * (1 - a0)
    rgba[..., :3] = (rgba[..., :3] * a0[..., None] + WARM * glow[..., None] * (1 - a0[..., None])) / np.maximum(na[..., None], 1e-6)
    rgba[..., 3] = na * 255
    im = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS)
    im.save(OUT / "lamp.png", optimize=True)
    print("lamp.png", im.size)


def cone():
    w, h = 1400, 840
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx = w / 2
    t = yy / h
    hw = 190 + t * 470
    u = np.abs(xx - cx) / hw
    edge = 1 - smooth(u, 0.55, 1.0)
    a = edge * (0.11 * (1 - t) ** 1.6 + 0.012)
    a *= smooth(yy, 0, 30)
    # streaks of haze
    a *= 1 + 0.18 * fnoise(h, w, 2.0, ax=0.15, ay=1.0, seed=41)
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = WARM
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.7, 0.7, a.shape) / 255, 0, 1) * 255
    save(rgba, "cone.png")


def ledge():
    h, w = 56, 512
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    grain = fnoise(h, w, 1.6, ax=2.5, ay=0.05, seed=51)
    rgb = np.zeros((h, w, 3))
    # top face (0..14) seen slightly from above: lit walnut
    top = yy < 14
    wal = np.array([92, 62, 40], float)
    rgb[top] = (wal * (1.0 + 0.12 * grain[top][:, None]))
    # brass lip (14..19)
    lip = (yy >= 14) & (yy < 19)
    rgb[lip] = np.array([200, 160, 92]) * (1.15 - (yy[lip][:, None] - 14) * 0.12)
    # front face (19..44): darker walnut
    fr = (yy >= 19) & (yy < 44)
    rgb[fr] = wal * (0.55 - (yy[fr][:, None] - 19) * 0.008) * (1 + 0.1 * grain[fr][:, None])
    a = (yy < 44).astype(float)
    # soft contact shadow under the ledge on the wall
    sh = (yy >= 44)
    a[sh] = 0.7 * np.exp(-(yy[sh] - 44) / 4.5)
    rgb[sh] = 0
    rgb[(yy >= 43) & (yy < 44)] *= 0.5
    save(np.dstack([np.clip(rgb, 0, 255), a * 255]), "ledge.png")


def floor():
    """Corridor floor: skirting board + polished dark boards with the (static, centred) pool's reflection."""
    w, h = 1920, 140
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    rgb = np.zeros((h, w, 3))
    a = np.ones((h, w))
    # skirting 0..26
    sk = yy < 26
    rgb[sk] = np.array([40, 33, 27]) * (0.8 + 0.4 * np.exp(-((yy[sk] - 3) / 2.0) ** 2))[:, None]
    # floor 26..140: dark boards running away from the viewer, slightly glossy
    fl = ~sk
    grain = fnoise(h, w, 1.8, ax=3.0, ay=0.08, seed=61)
    boards = (np.sin(xx / 140 * np.pi * 2) > 0.985).astype(float)
    base = np.array([34, 25, 19], float) * (1 + 0.15 * grain[..., None]) * (1 - 0.35 * boards[..., None])
    refl = np.exp(-(((xx - w / 2) / 360) ** 2) - (((yy - 30) / 55) ** 2)) * 0.9
    refl += 0.25 * np.exp(-(((xx - w / 2) / 700) ** 2) - (((yy - 30) / 90) ** 2))
    col = base + refl[..., None] * np.array([120, 96, 66])
    rgb[fl] = col[fl]
    rgb[(yy >= 26) & (yy < 28)] *= 0.4
    save(np.dstack([np.clip(rgb, 0, 255), a * 255]), "floor.png")


def strip():
    """Strip of light grazing the now-playing / OSD rail: wide flat warm ellipse."""
    w, h = 1920, 220
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    a = 0.30 * np.exp(-(((xx - w / 2) / 760) ** 4) - (((yy - h * 0.58) / 52) ** 2))
    a += 0.10 * np.exp(-(((xx - w / 2) / 900) ** 2) - (((yy - h * 0.58) / 110) ** 2))
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = WARM
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.6, 0.6, a.shape) / 255, 0, 1) * 255
    save(rgba, "strip.png")


def board_shrouds():
    # Gallery / salon: travelling shroud, texture 1920^2 drawn at 3840^2 (2x). Hole at the texture centre.
    # 0.9.2 (speed): 1024^2 drawn at 3840^2 (was 1920^2), 1:1 shrouds at half size drawn 2x
    S = 3840 / 1024
    n = 1024
    c = n * S / 2
    I = light_field(n, n, [dict(cx=c, cy=c, r0=262, sig=78, spill=0.36, rs=190, sx=0.74, sy=1.0)], scale=S)
    shroud_from(I, 0.06, "shroud_gallery.png")
    # Small travelling pool for the salon grid / landscape walls (tighter, same 2x mechanism)
    I = light_field(n, n, [dict(cx=c, cy=c, r0=170, sig=70, spill=0.34, rs=170, sx=0.9, sy=1.0)], scale=S)
    shroud_from(I, 0.06, "shroud_small.png")
    # Corridor (static, 1:1): the torch stays centred, the wall slides past
    I = light_field(540, 960, [dict(cx=960, cy=556, r0=262, sig=80, spill=0.34, rs=200, sx=0.80, sy=1.0)], scale=2)
    shroud_from(I, 0.06, "shroud_corridor.png")
    # Wide corridor for landscape stills (episodes, seasons)
    I = light_field(540, 960, [dict(cx=960, cy=520, r0=300, sig=90, spill=0.34, rs=210, sx=1.25, sy=0.8)], scale=2)
    shroud_from(I, 0.06, "shroud_wide.png")
    # Info: tight spot on the poster + softer wide light on the wall label (1:1)
    I = light_field(540, 960, [
        dict(cx=395, cy=470, r0=292, sig=46, spill=0.16, rs=110, sx=0.76, sy=1.0),
        dict(cx=1262, cy=540, r0=300, sig=150, spill=0.22, rs=220, sx=1.7, sy=1.12, gain=0.62),
    ], scale=2)
    shroud_from(I, 0.075, "shroud_info.png")
    # Info for landscape art (episodes): spot on a 16:9 still
    I = light_field(540, 960, [
        dict(cx=430, cy=420, r0=300, sig=50, spill=0.16, rs=110, sx=1.3, sy=0.8),
        dict(cx=1262, cy=560, r0=300, sig=150, spill=0.22, rs=220, sx=1.7, sy=1.12, gain=0.62),
    ], scale=2)
    shroud_from(I, 0.075, "shroud_info_wide.png")
    # Music room: pendant pool
    I = light_field(540, 960, [dict(cx=960, cy=560, r0=236, sig=70, spill=0.30, rs=170, sx=0.98, sy=1.0)], scale=2)
    shroud_from(I, 0.06, "shroud_music.png")
    # Pages (settings, lists, dialogs' rooms): a broad soft light on the reading area, dark edges
    I = light_field(540, 960, [dict(cx=900, cy=560, r0=420, sig=260, spill=0.3, rs=320, sx=1.6, sy=1.0, gain=0.46)], scale=2)
    shroud_from(I, 0.12, "shroud_page.png")
    # Info page 2 (cast): a long low band of light along the portraits, below the page's first screen
    I = light_field(240, 960, [dict(cx=960, cy=150, r0=170, sig=120, spill=0.3, rs=220, sx=4.2, sy=1.0, gain=0.62)], scale=2)
    shroud_from(I, 0.07, "shroud_cast.png")


def view_shrouds():
    """Lights for the views added 2026-10-27 (Vitrine 502, Panorama 506, Catalogue 507, Portraits 508)."""
    label = dict(cx=1262, cy=450, r0=300, sig=150, spill=0.22, rs=220, sx=1.7, sy=1.0, gain=0.62)
    band = dict(cx=960, cy=902, r0=250, sig=90, spill=0.18, rs=160, sx=3.4, sy=0.42, gain=0.52)
    # Vitrine: the info page's spot on the picture + the wall label, plus a low band along the drawer of frames
    I = light_field(540, 960, [dict(cx=395, cy=470, r0=292, sig=46, spill=0.16, rs=110, sx=0.76, sy=1.0), label, band], scale=2)
    shroud_from(I, 0.075, "shroud_vitrine.png")
    I = light_field(540, 960, [dict(cx=430, cy=420, r0=300, sig=50, spill=0.16, rs=110, sx=1.3, sy=0.8), label, band], scale=2)
    shroud_from(I, 0.075, "shroud_vitrine_wide.png")
    # Panorama: a wide travelling pool for 16:9 frames (1024^2 drawn at 3840^2, hole at the centre)
    S = 3840 / 1024
    n = 1024
    c = n * S / 2
    I = light_field(n, n, [dict(cx=c, cy=c, r0=196, sig=74, spill=0.34, rs=170, sx=1.5, sy=0.86)], scale=S)
    shroud_from(I, 0.06, "shroud_land.png")
    # Catalogue: a reading light on the register (left) + a spot on the picture and its text (right)
    I = light_field(540, 960, [
        dict(cx=600, cy=580, r0=380, sig=230, spill=0.3, rs=300, sx=1.35, sy=1.0, gain=0.46),
        dict(cx=1532, cy=372, r0=232, sig=56, spill=0.16, rs=110, sx=1.45, sy=0.86),
        dict(cx=1532, cy=780, r0=230, sig=140, spill=0.2, rs=200, sx=1.4, sy=1.0, gain=0.56),
    ], scale=2)
    shroud_from(I, 0.09, "shroud_catalogue.png")
    # Portraits (music): a spot on the big canvas + a soft light on the index of names
    I = light_field(540, 960, [
        dict(cx=1290, cy=532, r0=360, sig=60, spill=0.16, rs=120, sx=1.5, sy=0.86),
        dict(cx=1290, cy=900, r0=220, sig=120, spill=0.2, rs=180, sx=2.2, sy=0.6, gain=0.6),
        dict(cx=380, cy=600, r0=300, sig=220, spill=0.3, rs=280, sx=1.1, sy=1.25, gain=0.44),
    ], scale=2)
    shroud_from(I, 0.075, "shroud_portraits.png")


# ------------------------------------------------------------------ Nocturne skin extras
def plaque_halves():
    """plaque.png split for auto-width plaques built from two buttons (title | meta)."""
    im = Image.open(OUT / "plaque.png")
    w, h = im.size
    # (plaque_l/r.png halves dropped 2026-10-30: no XML names them)
    # dim rail under engraved words (mockup: brightness .5, saturate .85)
    a = np.array(im, float)
    g = a[..., :3].mean(-1, keepdims=True)
    a[..., :3] = (g + (a[..., :3] - g) * 0.85) * 0.5
    save(a, "plaque_dim.png")


def plaque_parts():
    """Auto-width plaque = [cap_l 26][title, mid][gap, mid][meta, mid][cap_r 26] in a grouplist."""
    im = Image.open(OUT / "plaque.png")
    w, h = im.size
    im.crop((0, 0, 26, h)).save(OUT / "plaque_capl.png", optimize=True)
    im.crop((w - 26, 0, w, h)).save(OUT / "plaque_capr.png", optimize=True)
    im.crop((40, 0, 104, h)).save(OUT / "plaque_mid.png", optimize=True)
    print("plaque_capl/capr/mid.png")


def wire():
    """Hanging wire (2 px, brass gradient across) and its hook."""
    a = np.zeros((4, 2, 4))
    a[:, 0, :3] = [58, 48, 38]
    a[:, 1, :3] = [138, 115, 86]
    a[..., 3] = 255
    save(a, "wire.png")
    h, w = 12, 10
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    t = yy / (h - 1)
    rgb = np.array([201, 166, 106])[None, None, :] * (1 - t[..., None]) + np.array([91, 68, 38])[None, None, :] * t[..., None]
    a = np.ones((h, w))
    for cx, cy in [(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)]:
        pass
    a[0, 0] = a[0, -1] = a[-1, 0] = a[-1, -1] = 0.3
    save(np.dstack([rgb, a * 255]), "hook.png")


def glow_row(name="glow_row.png", w=640, h=120, a0=0.34):
    """Soft horizontal pool of light behind a focused row/word (white: tint with colordiffuse)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    u = (xx - w / 2) / (w / 2)
    v = (yy - h / 2) / (h / 2)
    r = np.sqrt(u ** 2 + v ** 2)
    a = a0 * np.exp(-(u / 0.62) ** 4 - (v / 0.5) ** 2) * smooth(1 - np.abs(u), 0, 0.2) * smooth(1 - np.abs(v), 0, 0.3)
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = 255
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.6, 0.6, a.shape) / 255, 0, 1) * 255
    save(rgba, name)


def glow_bar():
    """Focused row light: a soft warm band, 9-slice border 64,0,64,0 (white: tint with colordiffuse)."""
    w, h = 256, 64
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    ex = smooth(np.minimum(xx, w - 1 - xx), 0, 64)
    v = (yy - (h - 1) / 2) / (h / 2)
    ey = np.exp(-(v / 0.75) ** 4)
    a = 0.24 * ex * ey
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = 255
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.5, 0.5, a.shape) / 255, 0, 1) * 255
    save(rgba, "glow_bar.png")
    # a brass tick for the focused row's left edge (2 x 32)
    t = np.zeros((32, 4, 4))
    t[..., :3] = [217, 179, 119]
    t[..., 3] = (np.sin(np.linspace(0, np.pi, 32)) ** 0.6)[:, None] * 255
    save(t, "tick.png")


def rail_parts():
    """Info / dialog rail of engraved words: dim brass parts + the lit plate for the focused word."""
    dim = Image.open(OUT / "plaque_dim.png")
    w, h = dim.size
    dim.crop((0, 0, 26, h)).save(OUT / "rail_capl.png", optimize=True)
    dim.crop((w - 26, 0, w, h)).save(OUT / "rail_capr.png", optimize=True)
    mid = dim.crop((40, 0, 104, h))
    mid.save(OUT / "rail_mid.png", optimize=True)
    # focused word: the dim rail with a lit brass plate on it (9-slice 30,0,30,0 at 320 x 64)
    base = Image.new("RGBA", (320, 64))
    for x in range(0, 320, 64):
        base.paste(mid, (x, 0))
    plate = Image.open(OUT / "plate.png").resize((308, 52), Image.LANCZOS)
    base.alpha_composite(plate, (6, 6))
    base.save(OUT / "rail_on.png", optimize=True)
    # separator between words
    sep = np.zeros((28, 3, 4))
    sep[:, 0:2, :3] = [20, 12, 4]
    sep[:, 0:2, 3] = 140
    sep[:, 2, :3] = [255, 220, 160]
    sep[:, 2, 3] = 46
    save(sep, "rail_sep.png")
    tall = Image.new("RGBA", (3, 64))
    tall.paste(mid.crop((0, 0, 3, 64)), (0, 0))
    tall.alpha_composite(Image.open(OUT / "rail_sep.png"), (0, 18))
    tall.save(OUT / "rail_sep_tall.png", optimize=True)
    print("rail parts")


def card():
    """Dialog card: dark plaster panel, faint brass hairline inset 10, 9-slice border 32."""
    s = 128
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    d = np.minimum(np.minimum(xx, yy), np.minimum(s - 1 - xx, s - 1 - yy))
    rgba = np.zeros((s, s, 4))
    rgba[..., :3] = np.array([22, 21, 25])
    rgba[..., 3] = 250
    line = np.abs(d - 10) < 0.6
    rgba[line, :3] = np.array([150, 120, 72])
    rgba[line, 3] = 140
    edge = d < 1
    rgba[edge, :3] = np.array([60, 52, 44])
    save(rgba, "card.png")


def page_floor():
    """Bottom darkness ramp (opaque velvet -> clear) for rails over video and long pages."""
    h, w = 400, 8
    y = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    a = smooth(y, 0.0, 1.0) ** 1.4 * 0.92
    rgba = np.zeros((h, w, 4))
    rgba[..., :3] = VELVET
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.6, 0.6, a.shape) / 255, 0, 1) * 255
    save(rgba, "floor_ramp.png")
    a = np.flipud(a)
    rgba[..., 3] = np.clip(a + RNG.uniform(-0.6, 0.6, a.shape) / 255, 0, 1) * 255
    save(rgba, "ceiling_ramp.png")


def dot(name, lit):
    """Toggle lamps: a lit brass stud vs a dark one (radio buttons)."""
    s = 40
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    c = s / 2 - 0.5
    r = np.hypot(xx - c, yy - c)
    R = 7
    a = np.clip(R + 0.5 - r, 0, 1)
    nz = np.sqrt(np.clip(1 - (r / R) ** 2, 0, 1))
    lam = np.clip(((xx - c) / R) * -0.4 + ((yy - c) / R) * -0.6 + nz * 0.7, 0, 1)
    if lit:
        base = np.array([255, 214, 150], float)
        rgb = base * (0.7 + 0.4 * lam[..., None])
        halo = 0.55 * np.exp(-((r - R) / 6.0) ** 2) * (r > R)
        rgb = np.where((r > R)[..., None], WARM, rgb)
        alpha = np.maximum(a, halo)
    else:
        base = np.array([96, 82, 62], float)
        rgb = base * (0.35 + 0.6 * lam[..., None])
        ring = np.abs(r - R) < 0.8
        alpha = a
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255])
    save(rgba, name)


def key():
    """Keyboard key: engraved dark tile (9-slice border 12)."""
    s = 48
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    d = np.minimum(np.minimum(xx, yy), np.minimum(s - 1 - xx, s - 1 - yy))
    rgba = np.zeros((s, s, 4))
    rgba[..., :3] = np.array([30, 28, 30])
    rgba[..., 3] = 235
    rgba[d < 1, :3] = np.array([70, 60, 48])
    rgba[(d < 1) & (yy > s / 2), :3] = np.array([12, 10, 10])
    save(rgba, "key.png")


def pin_small():
    im = Image.open(OUT / "pin.png").resize((20, 20), Image.LANCZOS)
    im.save(OUT / "pin_s.png", optimize=True)


# ------------------------------------------------------------------ engine overrides (Majan texture names)
MEDIA = OUT.parent


def engine_overrides():
    """Repaint the Majan-engine textures that many windows reference by name, in Nocturne's language.
    focus/outline_*  -> a soft warm glow ring (light, not a frame); 40 px, border 16 as before
    common/rect_square / rect_round8 (focused fills) -> brushed brass with a bevel (tinted by colordiffuse)
    common/rect_outline_1* (resting button / key) -> a dim brass plate
    dialogs/panel_framed -> dark plaster card with a brass hairline"""
    s = 40
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    d = np.minimum(np.minimum(xx, yy), np.minimum(s - 1 - xx, s - 1 - yy))
    for name, peak, width in (("outline_2", 7.5, 3.2), ("outline_3", 7.5, 4.0), ("outline_2_round", 7.5, 3.2), ("outline_3_round", 7.5, 4.0)):
        a = 0.85 * np.exp(-((d - peak) / width) ** 2) + 0.25 * np.exp(-((d - 12) / 6) ** 2) * (d > peak)
        a = np.clip(a, 0, 1)
        rgba = np.zeros((s, s, 4))
        rgba[..., :3] = 255
        rgba[..., 3] = a * 255
        im = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")
        im.save(MEDIA / "focus" / f"{name}.png", optimize=True)
    # brass fill 32x32 (border 10)
    s = 32
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    t = yy / (s - 1)
    v = 0.92 + 0.22 * np.exp(-((t - 0.3) / 0.18) ** 2) - 0.2 * t
    rgb = np.stack([v * 214, v * 178, v * 112], -1)
    d = np.minimum(np.minimum(xx, yy), np.minimum(s - 1 - xx, s - 1 - yy))
    rgb[(d < 1) & (yy < s / 2)] *= 1.2
    rgb[(d < 1) & (yy >= s / 2)] *= 0.6
    for name in ("rect_square", "rect_round8"):
        a = np.ones((s, s))
        if name == "rect_round8":
            r = 6
            for cx, cy in [(r, r), (s - 1 - r, r), (r, s - 1 - r), (s - 1 - r, s - 1 - r)]:
                m = ((xx < r) | (xx > s - 1 - r)) & ((yy < r) | (yy > s - 1 - r))
                dd = np.hypot(xx - cx, yy - cy)
                a = np.where(m & (np.abs(xx - cx) <= r) & (np.abs(yy - cy) <= r), np.clip(r + 0.5 - dd, 0, 1), a)
        Image.fromarray(np.clip(np.dstack([rgb, a * 255]), 0, 255).astype(np.uint8), "RGBA").save(MEDIA / "common" / f"{name}.png", optimize=True)
    # resting button: dim plate (white-ish so colordiffuse decides the strength) with a 1 px darker edge
    dim = np.stack([v * 200, v * 190, v * 175], -1)
    dim[d < 1] *= 0.55
    for name in ("rect_outline_1", "rect_outline_1_round8"):
        a = np.full((s, s), 0.55)
        a[d < 1] = 0.9
        Image.fromarray(np.clip(np.dstack([dim, a * 255]), 0, 255).astype(np.uint8), "RGBA").save(MEDIA / "common" / f"{name}.png", optimize=True)
    # dark card for context menus etc. (border 10 as before)
    s = 32
    yy, xx = np.mgrid[0:s, 0:s].astype(float)
    d = np.minimum(np.minimum(xx, yy), np.minimum(s - 1 - xx, s - 1 - yy))
    rgba = np.zeros((s, s, 4))
    rgba[..., :3] = [21, 20, 24]
    rgba[..., 3] = 250
    rgba[d < 1, :3] = [118, 96, 62]
    Image.fromarray(rgba.astype(np.uint8), "RGBA").save(MEDIA / "dialogs" / "panel_framed.png", optimize=True)
    print("engine overrides")


if __name__ == "__main__":
    plaster()
    board_shrouds()
    view_shrouds()
    glow("glow_warm.png")
    halo("halo_white.png", size=512)
    halo("halo_warm.png", (255, 226, 184), size=512)
    dust("dust.png")
    dust("dust_white.png", masked=False)
    frame()
    shadow()
    glint()
    plaque()
    plaque("plate.png", screws=False, seed=12)
    pin()
    rail()
    picrail()
    cornice()
    plaster_with_cornice()
    filament()
    lamp()
    cone()
    ledge()
    floor()
    strip()
    plaque_halves()
    plaque_parts()
    plaque("plaque2.png", h=84, seed=13)
    wire()
    glow_row()
    glow_row("glow_word.png", 360, 120, 0.42)
    card()
    glow_bar()
    rail_parts()
    page_floor()
    dot("dot_on.png", True)
    dot("dot_off.png", False)
    key()
    engine_overrides()
