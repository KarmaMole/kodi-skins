"""Textures for the 0.9.15 library views (docs/VIEWS_BRIEF_2026-10-27.md). Run:
    python skins/skin.daylight/_src/make_view_textures.py

  daylight/mask_spot.png        Spotlight art mask (1140x520, art-local): top-right corner follows the card's
                                28 px radius, alpha rises from the text column (the same curve as hero_fade.png,
                                inverted) and falls away over the last 170 px, so the art melts into the card
                                above the poster strip instead of ending on a hard line.
  daylight/timebar/bar_NNN.png  Time view runtime bars: 960x28 canvas, one rounded bar NNN minutes long at
                                4 px a minute (5..240, 5-minute steps) drawn from the left, the rest clear.
                                One texture per bucket, chosen by $VAR[VidView_TimeBar] (no arithmetic in Kodi).
  daylight/timebar/bar_max.png  more than 4 hours: the full axis with a soft end (the film runs on past it).
  daylight/shade55.png          white at 55 %: the Time view's "past bedtime" shade, tinted with DL_Surface.
  daylight/ring_circle.png      accent focus ring around round artist portraits.
All white + alpha, tinted at runtime. Writes only these files (make_textures.py owns everything else).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

MEDIA = Path(__file__).resolve().parents[1] / "media"
SS = 4


def save(img, rel):
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def white_alpha(a):
    a8 = np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    out = np.zeros(a8.shape + (4,), np.uint8)
    out[..., :3] = 255
    out[..., 3] = a8
    return Image.fromarray(out, "RGBA")


def spot_mask():
    w, h, r = 1140, 520, 28
    x = np.arange(w, dtype=np.float32)
    ax = 1.0 - np.interp(x, [0, 65, 300, 838, 1140], [1.0, 1.0, 0.82, 0.0, 0.0])
    y = np.arange(h, dtype=np.float32)
    ay = np.interp(y, [0, h - 170, h - 20, h], [1.0, 1.0, 0.0, 0.0])
    ay = ay ** 1.4
    a = ay[:, None] * ax[None, :]
    corner = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(corner)
    d.rounded_rectangle([0, 0, w * SS - 1, (h + 2 * r) * SS], radius=r * SS, fill=255)
    d.rectangle([0, 0, (w // 2) * SS, h * SS], fill=255)       # only the top-right corner is rounded
    cm = np.asarray(corner.resize((w, h), Image.LANCZOS), np.float32) / 255.0
    save(white_alpha(a * cm), "daylight/mask_spot.png")


def bar(length, soft_end=False):
    W, H = 960, 28
    img = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(img).rounded_rectangle([0, 0, length * SS - 1, H * SS - 1], radius=H * SS // 2, fill=255)
    a = np.asarray(img.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    if soft_end:
        x = np.arange(W, dtype=np.float32)
        a = a * np.interp(x, [0, W - 120, W], [1.0, 1.0, 0.15])[None, :]
    return white_alpha(a)


def main():
    spot_mask()
    for m in range(5, 241, 5):
        save(bar(m * 4), f"daylight/timebar/bar_{m:03d}.png")
    save(bar(960, soft_end=True), "daylight/timebar/bar_max.png")
    save(white_alpha(np.full((8, 8), 0.55, np.float32)), "daylight/shade55.png")
    # focus ring for round portraits (music Wall / Spotlight): drawn 9 px outside the portrait, 4 px stroke at
    # ~180 px, i.e. the same 5 px gap + 4 px accent as ring_<r>.png around square art
    n = 372
    img = Image.new("L", (n * SS, n * SS), 0)
    ImageDraw.Draw(img).ellipse([0, 0, n * SS - 1, n * SS - 1], outline=255, width=8 * SS)
    save(white_alpha(np.asarray(img.resize((n, n), Image.LANCZOS), np.float32) / 255.0), "daylight/ring_circle.png")
    print("ok: mask_spot + 49 time bars")


if __name__ == "__main__":
    main()
