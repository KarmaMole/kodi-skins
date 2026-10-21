"""Vernissage textures (DESIGN 11) and icons (DESIGN 7).   python skins/skin.vernissage/_src/make_textures.py

Writes media/vn/ (white on transparent unless noted, tinted in XML by room tokens):
  white.png 8x8 | frame.png 16x16 (2 px ring + 1 px clear buffer: use border="3", LESSONS 33) | card_edge.png 16x16
  (1 px ring + buffer, border="4") | row_rule.png 16x8 (2 px rule at the bottom + buffer, border="0,0,0,3": the
  focused row's hairline) | spot.png 512 (the pool, DESIGN 5) | shadow.png 176 (border="56", DESIGN 5) |
  mat_falloff.png 8x256 (black 0 -> 16 % from 30 % down) | vignette.png, daylight.png, dayfar.png 960x540 (room
  washes, TPDF-dithered alpha) | scrim_bottom.png 8x256 (black 0 -> 72 %) | dot.png 32 (seen dot / ring) |
  progress_knob.png 32 | print_blank.png 240x360 (neutral opaque print for an item the helper hasn't printed yet) |
  day/wall.png, evening/wall.png 16x16 opaque (Tex_Room) | clear.png 8 (transparent) | fade_h.png 150x8 (clear ->
  white left to right, tinted card: the "..." fade on a clamped last line)
  icons/<name>.png 48 px and icons/72/<name>.png (icons.py; badges: square 2 px outline boxes lettered in Inter Tight
  Medium, the media flags' style). The add-on's icon.png / fanart.jpg are make_addon_art.py's (it reads spot.png and
  vignette.png from here, so it runs after this). Deterministic: the dither uses a fixed seed.
The mockup recipes (spot, shadow, washes) are copied from docs/skin.vernissage/mockups/_src/make_assets.py so the
skin draws what the boards show.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
M = ROOT / "media" / "vn"
sys.path.insert(0, str(HERE))
import icons as IC  # noqa: E402

RNG = np.random.default_rng(20261021)


def save(img: Image.Image, rel: str) -> None:
    p = M / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def white_alpha(a: np.ndarray, dither: bool = True) -> Image.Image:
    """float alpha 0..1 -> white RGBA, TPDF-dithered (smooth on the TV, LESSONS Orbit 0.9.2)."""
    v = a * 255.0
    if dither:
        v = v + (RNG.random(a.shape) - RNG.random(a.shape))
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = np.clip(np.round(v), 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def black_alpha(a: np.ndarray, dither: bool = True) -> Image.Image:
    im = white_alpha(a, dither)
    arr = np.asarray(im).copy()
    arr[..., :3] = 0
    return Image.fromarray(arr, "RGBA")


def basics() -> None:
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "white.png")
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 0)), "clear.png")     # transparent progress bg (LESSONS Keepsake)
    fx = np.tile(np.clip(np.linspace(-0.15, 1.35, 150), 0, 1)[None, :], (8, 1)) ** 1.2
    save(white_alpha(fx.astype(np.float32), False), "fade_h.png")        # the "..." fade at a clamped last line
    for name, n, ring in (("frame.png", 16, 2), ("card_edge.png", 16, 1)):
        a = np.zeros((n, n), np.float32)
        a[:ring, :] = a[-ring:, :] = a[:, :ring] = a[:, -ring:] = 1
        save(white_alpha(a, False), name)
    a = np.zeros((8, 16), np.float32)
    a[-2:, :] = 1
    save(white_alpha(a, False), "row_rule.png")
    # seen dot / knob: anti-aliased discs
    for name in ("dot.png", "progress_knob.png"):
        big = Image.new("L", (256, 256), 0)
        ImageDraw.Draw(big).ellipse((8, 8, 247, 247), fill=255)
        small = big.resize((32, 32), Image.LANCZOS)
        save(white_alpha(np.asarray(small, np.float32) / 255, False), name)
    y = np.linspace(0, 1, 256, dtype=np.float32)[:, None].repeat(8, 1)
    save(black_alpha(np.clip((y - 0.3) / 0.7, 0, 1) * 0.16), "mat_falloff.png")
    save(black_alpha(y * 0.72), "scrim_bottom.png")
    pb = Image.new("RGB", (240, 360), (150, 150, 150))
    save(pb, "print_blank.png")
    # the flat walls as opaque textures (Tex_Room: scrims drawn from the ground itself through a diffuse ramp)
    save(Image.new("RGB", (16, 16), (0xF4, 0xF2, 0xEE)), "day/wall.png")
    save(Image.new("RGB", (16, 16), (0x16, 0x16, 0x1A)), "evening/wall.png")


def spot() -> None:
    n = 512
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    cx, cy = n / 2, n * 0.46
    dx, dy = (x - cx) / (n / 2), (y - cy) / (n / 2)
    r = np.sqrt(dx ** 2 + dy ** 2)
    core = np.exp(-(r / 0.55) ** 2.4)
    skirt = np.exp(-(r / 0.95) ** 2) * 0.35
    scallop = np.exp(-((dy + 0.62) / 0.16) ** 2) * np.exp(-(dx / 0.42) ** 2) * 0.35
    a = np.clip(core * 0.75 + skirt + scallop, 0, 1)
    a *= np.clip(1.0 - r, 0, 1) ** 0.6
    save(white_alpha(a / a.max()), "spot.png")


def shadow() -> None:
    n, b = 176, 56
    m = Image.new("L", (n, n), 0)
    m.paste(255, (b, b + 10, n - b, n - b + 10))
    m = m.filter(ImageFilter.GaussianBlur(20))
    save(white_alpha(np.asarray(m, np.float32) / 255 * 0.42), "shadow.png")


def washes() -> None:
    W, H = 960, 540   # baked at the size they ship (the mockup computes 1920 and halves; same curves)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)
    r = np.sqrt(dx ** 2 * 0.9 + dy ** 2 * 1.1)
    save(black_alpha(np.clip((r - 0.55) / 0.9, 0, 1) ** 1.6 * 0.55), "vignette.png")
    d = np.sqrt(((x - 0.1 * W) / W) ** 2 + ((y + 0.15 * H) / H) ** 2)
    save(white_alpha(np.clip(1 - d / 1.1, 0, 1) ** 1.5 * 0.55), "daylight.png")
    save(black_alpha(np.clip((dx + dy - 0.6) / 1.4, 0, 1) ** 1.5 * 0.10), "dayfar.png")


def icons() -> None:
    import cairosvg
    for name in IC.ICONS:
        for size, sub in ((48, ""), (72, "72/")):
            p = M / "icons" / f"{sub}{name}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(bytestring=IC.svg(name, size).encode(), write_to=str(p), output_width=size, output_height=size)
    font_path = ROOT / "fonts" / "InterTight-Medium.ttf"
    for name, text in IC.BADGES.items():
        for size, sub in ((48, ""), (72, "72/")):
            s = 4  # supersample
            f = ImageFont.truetype(str(font_path), int(size * 0.36 * s))
            tw = f.getlength(text)
            w = int(max(size, tw / s + size * 0.42))
            im = Image.new("L", (w * s, size * s), 0)
            d = ImageDraw.Draw(im)
            sw = int(IC.SW * size / 48 * s)
            d.rectangle((sw // 2, int(size * 0.18 * s), w * s - sw // 2 - 1, int(size * 0.82 * s)), outline=255, width=sw)
            d.text((w * s / 2, size * s / 2), text, font=f, fill=255, anchor="mm")
            a = np.asarray(im.resize((w, size), Image.LANCZOS), np.float32) / 255
            save(white_alpha(a, False), f"icons/{sub}{name}.png")


# media flags (DESIGN 6): 2 px outline box, 36 px tall, Inter Tight Medium 22 px at +6 % tracking, white (tinted ink2).
# Name = the slug; width = text + 2 x 11 + 4. Drawn at 3x and reduced, so the box and the letters stay crisp.
FLAGS = ["4K", "1080p", "720p", "SD", "DOLBY VISION", "HDR10", "HDR10+", "HLG", "ATMOS", "DTS:X", "TRUEHD",
         "DTS-HD MA", "DTS-HD", "DTS", "DD+", "DD", "AAC", "FLAC", "MP3", "OPUS", "1.0", "2.0", "5.0", "5.1", "6.1", "7.1"]


def flag_slug(t: str) -> str:
    return t.lower().replace(" ", "_").replace(":", "").replace("+", "plus").replace(".", "_").replace("-", "_")


def flag_width(t: str) -> int:
    f = ImageFont.truetype(str(ROOT / "fonts" / "InterTight-Medium.ttf"), 22)
    return int(round(f.getlength(t) + 0.06 * 22 * (len(t) - 1) + 2 * 11 + 4))


def flags() -> None:
    S = 3
    f = ImageFont.truetype(str(ROOT / "fonts" / "InterTight-Medium.ttf"), 22 * S)
    for t in FLAGS:
        w, h = flag_width(t), 36
        im = Image.new("L", (w * S, h * S), 0)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w * S - 1, h * S - 1), outline=255, width=2 * S)
        x = (11 + 2) * S
        asc, desc = f.getmetrics()
        y = (h * S - (asc + desc)) // 2
        for ch in t:
            d.text((x, y), ch, font=f, fill=255)
            x += f.getlength(ch) + 0.06 * 22 * S
        a = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255
        save(white_alpha(a, False), f"flags/{flag_slug(t)}.png")


def main() -> None:
    basics()
    flags()
    spot()
    shadow()
    washes()
    icons()
    print("textures ->", M)


if __name__ == "__main__":
    main()
