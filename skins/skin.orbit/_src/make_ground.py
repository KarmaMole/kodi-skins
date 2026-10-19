"""Generate Orbit's deep-blue ground: opaque, pre-rendered, dithered full-screen PNGs (media/ground/).

Why (0.9.2): the mockups' ground (#07090D + a #121722 radial lift) is so close to black that a TV
crushes it: Omar saw plain black. The ground is now a clearly blue, still quiet navy field drawn as
ONE opaque texture per layout, with the lens glow baked in at the mockup's lens point, so:
  - no colordiffuse x 8-bit alpha maths (the old white-alpha lift had ~11-21 usable levels and banded),
  - every pixel is computed in float and TPDF-dithered (+-1 LSB) before rounding: no banding on the Shield,
  - the same images double as the scrim over fanart (drawn with diffuse="common/scrim_*.png"), so a
    darkened backdrop fades into blue, never into black.

Palette (sRGB):          edge #05091A   field #0B1328   glow #1C2D52 (peak, at the lens)
Variants: lens point x,y (design px), glow radius, glow strength 0..1
  home  1000,540  Home dial + search dial (mockup OrbitHome lens)
  arc   1300,540  library / music arc (mockup OrbitArc lens)
  list   300,540  dial list / episode list / album list (glow behind the text column)
  page   960,620  settings, dialogs, add-ons, secondary windows, info pages (wide soft glow)
  osd    440,520  now playing / visualisation (mockup OrbitOSD ring centre)

Usage: python skins/skin.orbit/_src/make_ground.py   (make_textures.py keeps media/ground/)
Rendered at 1280x720 and drawn stretched to 1920x1080: the GPU interpolates between dithered texels
in float, so it stays smooth; a full 1080p noise PNG would be ~3x the size for no visible gain.
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "ground"

W, H = 1280, 720          # texture size (drawn at 1920x1080)
SX = W / 1920.0

EDGE = np.array([5, 9, 26], dtype=np.float64)     # corners
FIELD = np.array([11, 19, 40], dtype=np.float64)  # broad mid field
GLOW = np.array([28, 45, 82], dtype=np.float64)   # lens peak

VARIANTS = {
    # name: (lens x, lens y, glow radius px, glow strength)
    "home": (1000, 540, 820, 1.0),
    "arc": (1300, 540, 880, 1.0),
    "list": (300, 540, 900, 0.85),
    "page": (960, 620, 1050, 0.75),
    "osd": (440, 520, 860, 0.9),
}


def smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def render(lx, ly, radius, strength, seed):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    x = (xs + 0.5) / SX
    y = (ys + 0.5) / SX
    # broad field: elliptical vignette centred slightly toward the lens, corners fall to EDGE
    cx = 960 + (lx - 960) * 0.35
    cy = 540 + (ly - 540) * 0.35
    d = np.hypot((x - cx) / 1250.0, (y - cy) / 820.0)
    field = 1.0 - smooth((d - 0.15) / 1.0)                 # 1 in the middle -> 0 in the corners
    col = EDGE[None, None, :] + (FIELD - EDGE)[None, None, :] * field[..., None]
    # lens glow (mockup: peak at the lens, ~55% at 360/760 of the radius, 0 at the radius)
    r = np.hypot(x - lx, y - ly) / radius
    g = (1.0 - smooth(r)) ** 1.35 * strength
    col = col + (GLOW - FIELD)[None, None, :] * g[..., None]
    # TPDF dither, +-1 LSB per channel
    rnd = np.random.default_rng(seed)
    col = col + rnd.random(col.shape) - rnd.random(col.shape)
    return Image.fromarray(np.clip(np.round(col), 0, 255).astype(np.uint8), "RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (name, (lx, ly, rad, s)) in enumerate(VARIANTS.items()):
        img = render(lx, ly, rad, s, seed=11 + i)
        p = OUT / f"{name}.png"
        img.save(p, optimize=True)
        print(f"{p.relative_to(HERE.parent)}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
