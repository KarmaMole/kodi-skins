"""Generate icon.png (256x256) and fanart.jpg (1920x1080) for skin.daylight.

Fanart: the four moods as one soft sweep of light (morning -> afternoon -> evening -> night), dithered,
with the wordmark in Fraunces (soft) and a Figtree line. Icon: a rounded tile at dusk with a sun
sinking behind the horizon line (the Evening mood icon), wordmark initial.

Usage: python skins/skin.daylight/_src/make_addon_art.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
RNG = np.random.default_rng(3)

STOPS = [(0.00, (0xEE, 0xF1, 0xF4)), (0.30, (0xF5, 0xF2, 0xEC)), (0.55, (0xF2, 0xC0, 0x8A)),
         (0.72, (0x2A, 0x22, 0x20)), (1.00, (0x0E, 0x14, 0x24))]


def lerp_stops(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            k = (t - t0) / (t1 - t0)
            k = k * k * (3 - 2 * k)
            return tuple(c0[i] + (c1[i] - c0[i]) * k for i in range(3))
    return STOPS[-1][1]


def sweep(w, h):
    xs = np.linspace(0, 1, w)
    row = np.array([lerp_stops(t) for t in xs], np.float32)
    img = np.repeat(row[None, :, :], h, 0)
    # soft glows: sun top-left, amber middle, moon right
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for cx, cy, r, col, k in ((0.12, -0.1, 0.55, (0x3E, 0x7C, 0xB1), 0.10), (0.55, 0.15, 0.45, (0xF2, 0xA6, 0x5A), 0.35),
                              (0.9, 0.2, 0.35, (0x7A, 0x9C, 0xFF), 0.18)):
        d = np.sqrt(((xx / w - cx) / r) ** 2 + ((yy / h - cy) / (r * w / h)) ** 2)
        g = np.clip(1 - d, 0, 1) ** 2 * k
        for i in range(3):
            img[..., i] = img[..., i] * (1 - g) + col[i] * g
    img += RNG.uniform(-1.2, 1.2, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def fanart():
    W, H = 1920, 1080
    img = sweep(W, H)
    d = ImageDraw.Draw(img)
    serif = ImageFont.truetype(str(FONTS / "DaylightDisplay-Medium.ttf"), 190)
    ui = ImageFont.truetype(str(FONTS / "Figtree-Medium.ttf"), 40)
    d.text((150, 380), "Daylight", font=serif, fill=(0x1F, 0x29, 0x33))
    d.text((158, 640), "A skin that knows what time it is.", font=ui, fill=(0x5B, 0x68, 0x75))
    # four mood dots along the bottom
    for i, col in enumerate([(0x3E, 0x7C, 0xB1), (0xD9, 0x82, 0x2B), (0xF2, 0xA6, 0x5A), (0x7A, 0x9C, 0xFF)]):
        x = 162 + i * 46
        d.ellipse((x, 740, x + 22, 762), fill=col)
    img.save(ROOT / "resources" / "fanart.jpg", quality=92)


def icon():
    S = 256 * 4
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    grad = np.zeros((S, S, 3), np.float32)
    top, bot = np.array([0x2A, 0x22, 0x20], np.float32), np.array([0x0E, 0x14, 0x24], np.float32)
    t = np.linspace(0, 1, S)[:, None]
    grad[:] = (top * (1 - t) + bot * t)[:, None, :] if False else (top[None, :] * (1 - t) + bot[None, :] * t)[:, None, :]
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    dd = np.sqrt(((xx - S * 0.5) / (S * 0.55)) ** 2 + ((yy - S * 0.62) / (S * 0.45)) ** 2)
    g = np.clip(1 - dd, 0, 1) ** 1.6 * 0.55
    amber = np.array([0xF2, 0xA6, 0x5A], np.float32)
    for i in range(3):
        grad[..., i] = grad[..., i] * (1 - g) + amber[i] * g
    tile = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22), fill=255)
    base.paste(tile, (0, 0), mask)
    d = ImageDraw.Draw(base)
    # sun setting behind the horizon
    cx, cy, r = S // 2, int(S * 0.64), int(S * 0.22)
    sun = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sun).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    ImageDraw.Draw(sun).rectangle((0, cy, S, S), fill=0)
    base.paste(Image.new("RGBA", (S, S), (0xF2, 0xA6, 0x5A, 255)), (0, 0), sun)
    lw = int(S * 0.028)
    d.rounded_rectangle((int(S * 0.16), cy - lw // 2, int(S * 0.84), cy + lw // 2), radius=lw // 2, fill=(0xF6, 0xE9, 0xDF, 255))
    d.rounded_rectangle((int(S * 0.32), cy + int(S * 0.09), int(S * 0.68), cy + int(S * 0.09) + lw), radius=lw // 2, fill=(0xF6, 0xE9, 0xDF, 150))
    # rays
    for ang in (-60, -30, 0, 30, 60):
        a = np.deg2rad(ang - 90)
        r1, r2 = r + S * 0.06, r + S * 0.12
        x1, y1 = cx + np.cos(a) * r1, cy + np.sin(a) * r1
        x2, y2 = cx + np.cos(a) * r2, cy + np.sin(a) * r2
        d.line((x1, y1, x2, y2), fill=(0xF2, 0xA6, 0x5A, 255), width=lw)
    base = base.resize((256, 256), Image.LANCZOS)
    # the official Kodi repository requires a solid icon (no transparency): flatten onto the ground colour
    _flat = Image.new("RGB", base.size, (28, 27, 34))  # the night tone at the corners: reads as a full square
    _flat.paste(base, mask=base.convert("RGBA").split()[3])
    _flat.save(ROOT / "resources" / "icon.png", optimize=True)


if __name__ == "__main__":
    fanart()
    icon()
    print("icon.png + fanart.jpg written")
