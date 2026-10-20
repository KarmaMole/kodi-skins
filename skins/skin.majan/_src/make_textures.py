"""Generate every UI texture for skin.majan (reproducible, Pillow only).

Rules (see docs/skin.majan/DESIGN.md, "Textures"):
  * UI chrome is WHITE on TRANSPARENT and tinted in XML with colordiffuse
    (accent, text, hairline, scrim...). The only baked two-tone asset is the
    watched tab (ink tab + bone check), which is never accent-coloured.
  * Anti-aliased shapes are drawn at SS x resolution and downsampled (LANCZOS).
  * Diffuse masks stretch with the control, so each rounded mask is exported
    at the exact control size it is designed for (radius = 8 px there).
  * 9-slice frames: the `border` value to use in XML is listed in BORDERS and
    printed at the end of the run.
  * Lowercase filenames only (the Shield's filesystem is case-sensitive).
  * 4K readiness (SPEC decision 8): icons, markers and rounded masks are
    exported at ~2x the size they are DRAWN at in the 1920x1080 skin space
    (same filenames; Kodi stretches a texture to the control rect, so XML
    sizes do not change). Why "2x the drawn size" and not "2x the old file":
    Kodi samples GUI textures with GL_LINEAR and NO mipmaps, so shrinking a
    texture by more than 2x on screen aliases its edges. Exactly 2x gives a
    clean 2:1 box-filter at 1080p and 1:1 pixels at 2160p. See ICON_PX and
    _src/check_texture_scaling.py (simulates Kodi's sampler).
    9-slice frames, solids, gradients and blurred shadows stay 1x: Kodi uses
    the `border` value both as texture pixels and as GUI units, so doubling
    a 9-slice bitmap would require doubling `border` AND double the on-screen
    corner size. Their XML `border=` values are unchanged.

Usage:  python skins/skin.majan/_src/make_textures.py
Writes: skins/skin.majan/media/**   and   skins/skin.majan/_src/previews/contact_sheet.png
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
PREVIEW = HERE / "previews"
SS = 8  # supersampling factor
HIDPI = 2  # pixel multiplier for non-9-slice art (icons, markers, masks)

WHITE = (255, 255, 255, 255)
CLEAR = (255, 255, 255, 0)

# Design tokens needed for the two baked assets (keep in sync with colors/defaults.xml)
INK = (0x0B, 0x0B, 0x0B)
BONE = (0xEC, 0xEB, 0xE7)

BORDERS: dict[str, str] = {}
WRITTEN: list[Path] = []


# --------------------------------------------------------------------------- helpers
def save(img: Image.Image, rel: str, border: str | None = None) -> None:
    assert rel == rel.lower(), rel
    path = MEDIA / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    WRITTEN.append(path)
    if border:
        BORDERS[rel] = border


def alpha_to_white(alpha: Image.Image) -> Image.Image:
    """White RGB + given L-mode alpha channel."""
    out = Image.new("RGBA", alpha.size, WHITE)
    out.putalpha(alpha)
    return out


def rounded_alpha(w: int, h: int, r: float, inset: float = 0.0) -> Image.Image:
    """Anti-aliased filled rounded rect as an L image of size (w, h)."""
    big = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(big)
    i = inset * SS
    d.rounded_rectangle((i, i, w * SS - 1 - i, h * SS - 1 - i), radius=max(0, r * SS), fill=255)
    return big.resize((w, h), Image.LANCZOS)


def ring_alpha(w: int, h: int, stroke: float, r_outer: float, margin: float = 0.0) -> Image.Image:
    """Anti-aliased frame of `stroke` px whose outer edge sits `margin` px
    inside the image edge (margin lets frames of different weights share one
    canvas, border value and placement)."""
    if r_outer == 0 and float(stroke).is_integer() and float(margin).is_integer():
        # Square frames: pixel-exact, no resampling softness.
        a = Image.new("L", (w, h), 0)
        m, st = int(margin), int(stroke)
        ImageDraw.Draw(a).rectangle((m, m, w - 1 - m, h - 1 - m), outline=255, width=st)
        return a
    outer = rounded_alpha(w, h, r_outer, inset=margin)
    inner = rounded_alpha(w, h, max(0.0, r_outer - stroke), inset=margin + stroke)
    return ImageChops.subtract(outer, inner)


def blurred_rect_alpha(size: int, rect: tuple[int, int, int, int], sigma: float, peak: int = 255) -> Image.Image:
    a = Image.new("L", (size, size), 0)
    ImageDraw.Draw(a).rectangle(rect, fill=peak)
    return a.filter(ImageFilter.GaussianBlur(sigma))


def dither(values: list[float], width: int, vertical: bool, seed: int = 7) -> Image.Image:
    """Build an L gradient (values 0..1 along the axis) with +-0.5 LSB noise to
    soften 8-bit banding over near-black backgrounds."""
    rnd = random.Random(seed)
    n = len(values)
    if vertical:
        img = Image.new("L", (width, n))
        px = img.load()
        for y, v in enumerate(values):
            for x in range(width):
                px[x, y] = max(0, min(255, round(v * 255 + rnd.uniform(-0.5, 0.5))))
    else:
        img = Image.new("L", (n, width))
        px = img.load()
        for x, v in enumerate(values):
            for y in range(width):
                px[x, y] = max(0, min(255, round(v * 255 + rnd.uniform(-0.5, 0.5))))
    return img


def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def piecewise(stops: list[tuple[float, float]], n: int) -> list[float]:
    """Linear interpolation of (position 0..1, alpha 0..1) stops, n samples."""
    out = []
    for i in range(n):
        p = i / (n - 1)
        for (p0, a0), (p1, a1) in zip(stops, stops[1:]):
            if p0 <= p <= p1:
                t = 0 if p1 == p0 else (p - p0) / (p1 - p0)
                out.append(a0 + (a1 - a0) * t)
                break
    return out


def draw_icon(path_fn, size: int = 48, grid: int = 24) -> Image.Image:
    """Icons are authored on a 24-unit grid (like the mockup SVGs) with a
    2-unit stroke, rendered white at `size` px."""
    s = size * SS / grid
    big = Image.new("L", (size * SS, size * SS), 0)
    d = ImageDraw.Draw(big)
    path_fn(d, s)
    return alpha_to_white(big.resize((size, size), Image.LANCZOS))


def line(d, s, pts, w=2.0):
    pts = [(x * s, y * s) for x, y in pts]
    d.line(pts, fill=255, width=round(w * s), joint="curve")
    r = w * s / 2  # round caps
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)


def poly(d, s, pts):
    d.polygon([(x * s, y * s) for x, y in pts], fill=255)


def circle(d, s, cx, cy, r, w=2.0, fill=False):
    box = ((cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s)
    if fill:
        d.ellipse(box, fill=255)
    else:
        d.ellipse(box, outline=255, width=round(w * s))


def rect(d, s, x0, y0, x1, y1, w=2.0, r=0.0, fill=False):
    box = (x0 * s, y0 * s, x1 * s, y1 * s)
    if fill:
        d.rounded_rectangle(box, radius=r * s, fill=255)
    else:
        d.rounded_rectangle(box, radius=r * s, outline=255, width=round(w * s))


# --------------------------------------------------------------------------- common
def make_common() -> None:
    save(Image.new("RGBA", (8, 8), WHITE), "common/white.png")
    save(Image.new("RGBA", (8, 1), WHITE), "common/hairline.png")
    save(Image.new("RGBA", (1, 8), WHITE), "common/hairline_v.png")

    # Filled rounded panel (buttons / chips in "Slightly rounded" mode). r = 8.
    save(alpha_to_white(rounded_alpha(32, 32, 8)), "common/rect_round8.png", "10")
    # 1px outline boxes: secondary buttons, segmented controls, media-flag boxes.
    # All four button/box textures share 32x32 + border="10" so XML can swap
    # them with $VAR[...] (Square vs Slightly rounded) without touching `border`.
    save(Image.new("RGBA", (32, 32), WHITE), "common/rect_square.png", "10")
    save(alpha_to_white(ring_alpha(32, 32, 1, 0)), "common/rect_outline_1.png", "10")
    save(alpha_to_white(ring_alpha(32, 32, 1, 8)), "common/rect_outline_1_round8.png", "10")

    # Linear gradients, alpha 1 -> 0 in the named direction (tint with `bg`).
    ramp = [1 - smooth(i / 255) for i in range(256)]
    save(alpha_to_white(dither(ramp, 16, vertical=True)), "common/gradient_top.png")
    save(alpha_to_white(dither(ramp[::-1], 16, vertical=True)), "common/gradient_bottom.png")
    save(alpha_to_white(dither(ramp, 16, vertical=False)), "common/gradient_left.png")
    save(alpha_to_white(dither(ramp[::-1], 16, vertical=False)), "common/gradient_right.png")

    # Music "stage" scrim, 1:1 with the MusicStage mockup:
    # linear-gradient(180deg, .55 0%, 0 30%, .2 55%, 1 92%, 1 100%) of #0b0b0b
    stage = piecewise([(0, .55), (.30, 0), (.55, .20), (.92, 1), (1, 1)], 540)
    save(alpha_to_white(dither(stage, 16, vertical=True)), "common/gradient_stage.png")

    # Text-zone scrims for artwork background >= Faint (see DESIGN.md contrast).
    # Flat 0.70 plateau, then eased to 0. Stretch to full height/width.
    left = [0.70 * (1 - smooth((i / 511 - 0.55) / 0.45)) if i / 511 > 0.55 else 0.70 for i in range(512)]
    save(alpha_to_white(dither(left, 16, vertical=False)), "common/scrim_left.png")
    bottom = left[::-1]
    save(alpha_to_white(dither(bottom, 16, vertical=True)), "common/scrim_bottom.png")

    # Soft drop shadow (CSS: 0 30px 60px rgba(0,0,0,.45)) as a 9-slice.
    # Canvas 384, core rect 128..255, sigma 30. Place control at item rect
    # expanded by 128 px on every side and shifted +30 px in y; tint `shadow`.
    sh = blurred_rect_alpha(384, (128, 128, 255, 255), 30)
    save(alpha_to_white(sh), "common/shadow_soft.png", "128")


# --------------------------------------------------------------------------- focus
def make_focus() -> None:
    # One geometry for every frame so a single control can swap them with
    # $VAR[...]: canvas 40x40, border="16", control = item rect expanded by
    # 7 px on every side (outline-offset 4 + up to 3 px stroke). The 2 px
    # frames carry a 1 px transparent margin so their stroke still sits at
    # offset 4 from the item.
    # Square (Poster corners = Square):
    save(alpha_to_white(ring_alpha(40, 40, 2, 0, margin=1)), "focus/outline_2.png", "16")
    save(alpha_to_white(ring_alpha(40, 40, 3, 0)), "focus/outline_3.png", "16")
    # Rounded (Poster corners = Slightly rounded), like a CSS outline around an
    # 8 px radius: stroke inner edge radius 8 + 4 = 12, outer = 12 + stroke.
    save(alpha_to_white(ring_alpha(40, 40, 2, 14, margin=1)), "focus/outline_2_round.png", "16")
    save(alpha_to_white(ring_alpha(40, 40, 3, 15)), "focus/outline_3_round.png", "16")
    # Dark halo behind the outline so the accent stroke never melts into bright
    # artwork (Soft/Visible backgrounds). Item rect expanded by 32 px; tint `focus_halo`.
    halo = blurred_rect_alpha(96, (32, 32, 63, 63), 7)
    save(alpha_to_white(halo), "focus/halo.png", "32")
    # Poster wall contact wall: 2 px page-black line inside outline_3 drawn on the poster edge (make_wall.py)
    save(alpha_to_white(ring_alpha(40, 40, 2, 0, margin=3)), "focus/inset_3_gap.png", "16")


# --------------------------------------------------------------------------- masks
MASKS = [
    # name, w, h, radius, used by
    ("poster_round8.png", 168, 252, 8, "widget rows 140-176 px wide, TV wall 158 px"),
    ("poster_round8_wall.png", 226, 339, 8, "Poster wall Medium + gap 226 px"),
    ("poster_round8_large.png", 330, 495, 8, "Big Poster view 300-360 px wide"),
    ("poster_round8_xl.png", 520, 780, 8, "Info page / Showcase poster 460-560 px wide"),
    ("square_round8.png", 219, 219, 8, "album grid 180-240 px"),
    ("square_round8_large.png", 380, 380, 8, "Big Album view 340-420 px"),
    ("landscape_round8.png", 320, 180, 8, "episode thumbs / Next up 280-360 px wide"),
    ("landscape_round8_large.png", 960, 540, 8, "spotlight fanart 860-1060 px wide"),
]


def make_masks() -> None:
    # "Square" mode: opaque masks (lets XML use one include with a diffuse
    # param for both modes). Tiny: stretching a solid is free.
    save(Image.new("RGBA", (4, 6), WHITE), "masks/poster_square.png")
    save(Image.new("RGBA", (4, 4), WHITE), "masks/square_square.png")
    save(Image.new("RGBA", (16, 9), WHITE), "masks/landscape_square.png")
    for name, w, h, r, _ in MASKS:
        save(alpha_to_white(rounded_alpha(w * HIDPI, h * HIDPI, r * HIDPI)), f"masks/{name}")


# --------------------------------------------------------------------------- markers
def check_path(d, s, x0, y0, w, h, stroke):
    """Check mark matching JetBrains Mono's U+2713 proportions."""
    pts = [(x0 + 0.05 * w, y0 + 0.55 * h), (x0 + 0.36 * w, y0 + 0.88 * h), (x0 + 0.95 * w, y0 + 0.12 * h)]
    line(d, s, pts, stroke)


def make_markers() -> None:
    # Unwatched: solid square (tint with $VAR accent). Sharp for Square mode, r3 for rounded.
    X = HIDPI
    save(Image.new("RGBA", (12 * X, 12 * X), WHITE), "markers/unwatched.png")
    save(alpha_to_white(rounded_alpha(12 * X, 12 * X, 3 * X)), "markers/unwatched_round.png")

    # Watched tab: baked two-tone, ink tab + bone check (never accent).
    # 22x22 at 1:1 (Hub/Home: 13px mono check + 3/6 px padding).
    for name, r, tab_alpha in (("watched.png", 0, 255), ("watched_round.png", 4, 217)):
        W = H = 22 * X
        tab = rounded_alpha(W, H, r * X)
        tab = tab.point(lambda v: v * tab_alpha // 255)
        img = Image.new("RGBA", (W, H), INK + (0,))
        img.putalpha(tab)
        big = Image.new("L", (W * SS, H * SS), 0)
        check_path(ImageDraw.Draw(big), SS * X, 6.5, 7.5, 9, 7, 1.7)  # 22-unit grid
        chk = big.resize((W, H), Image.LANCZOS)
        bone = Image.new("RGBA", (W, H), BONE + (255,))
        bone.putalpha(chk)
        img = Image.alpha_composite(img, bone)
        save(img, f"markers/{name}")

    # White check alone (tintable): settings radios, fully-watched states.
    # Drawn at 20-26 px (settings radio 26, DialogSelect 22, chip 20) -> 48.
    save(draw_icon(lambda d, s: check_path(d, s, 4, 6, 16, 12, 2.4), 48), "markers/check.png")


# --------------------------------------------------------------------------- icons
ICONS = {
    # 1:1 from the mockup SVG: circle(11,11,r7) + path M20 20 L16 16, stroke 2
    "search": lambda d, s: (circle(d, s, 11, 11, 7), line(d, s, [(20, 20), (16, 16)])),
    # 1:1 from the mockup SVG: M6 4 L20 12 L6 20 z (filled)
    "play": lambda d, s: poly(d, s, [(6, 4), (20, 12), (6, 20)]),
    "pause": lambda d, s: (rect(d, s, 6, 4, 10, 20, fill=True), rect(d, s, 14, 4, 18, 20, fill=True)),
    "stop": lambda d, s: rect(d, s, 5, 5, 19, 19, fill=True),
    "next": lambda d, s: (poly(d, s, [(5, 4), (16, 12), (5, 20)]), rect(d, s, 17, 4, 20, 20, fill=True)),
    "prev": lambda d, s: (poly(d, s, [(19, 4), (8, 12), (19, 20)]), rect(d, s, 4, 4, 7, 20, fill=True)),
    "forward": lambda d, s: (poly(d, s, [(2, 5), (12, 12), (2, 19)]), poly(d, s, [(12, 5), (22, 12), (12, 19)])),
    "rewind": lambda d, s: (poly(d, s, [(22, 5), (12, 12), (22, 19)]), poly(d, s, [(12, 5), (2, 12), (12, 19)])),
    "subtitles": lambda d, s: (rect(d, s, 3, 5, 21, 19, r=2), line(d, s, [(7, 13), (11, 13)]), line(d, s, [(14, 13), (17, 13)]),
                               line(d, s, [(7, 16), (17, 16)])),
    "audio": lambda d, s: (poly(d, s, [(4, 9), (8, 9), (13, 5), (13, 19), (8, 15), (4, 15)]),
                           line(d, s, [(16.5, 9.5), (17.5, 12), (16.5, 14.5)]), line(d, s, [(19.5, 7), (21, 12), (19.5, 17)])),
    "settings": lambda d, s: (line(d, s, [(4, 7), (20, 7)]), line(d, s, [(4, 17), (20, 17)]),
                              circle(d, s, 9, 7, 2.6, fill=True), circle(d, s, 15, 17, 2.6, fill=True)),
    "info": lambda d, s: (circle(d, s, 12, 12, 9), line(d, s, [(12, 11), (12, 16.5)]), circle(d, s, 12, 7.7, 1.25, fill=True)),
    "chapters": lambda d, s: (line(d, s, [(4, 7), (20, 7)]), line(d, s, [(4, 12), (20, 12)]), line(d, s, [(4, 17), (14, 17)])),
    "back": lambda d, s: line(d, s, [(15, 5), (8, 12), (15, 19)]),
    "chevron_right": lambda d, s: line(d, s, [(9, 5), (16, 12), (9, 19)]),
    "chevron_down": lambda d, s: line(d, s, [(5, 9), (12, 16), (19, 9)]),
    "shuffle": lambda d, s: (line(d, s, [(3, 7), (8, 7), (16, 17), (21, 17)]), line(d, s, [(3, 17), (8, 17), (16, 7), (21, 7)]),
                             line(d, s, [(18, 4), (21, 7), (18, 10)]), line(d, s, [(18, 14), (21, 17), (18, 20)])),
    "repeat": lambda d, s: (line(d, s, [(4, 11), (4, 7), (20, 7)]), line(d, s, [(17, 4), (20, 7), (17, 10)]),
                            line(d, s, [(20, 13), (20, 17), (4, 17)]), line(d, s, [(7, 14), (4, 17), (7, 20)])),
}


# Source px per icon = ~2x its on-screen size in the 1080 skin space.
# (uses as of 2026-10-18; if a builder draws an icon at a very different size,
#  re-run check_texture_scaling.py and adjust here, filenames stay the same.)
ICON_PX = {
    # spin/spinex arrows 24 px (Defaults.xml); back/chevron_down: same family
    "chevron_right": 48, "chevron_down": 48, "back": 48,
    # Home top bar, topbar_icon = 26
    "search": 52,
    # shared: Home top bar 26 AND OSD button 56 -> best compromise for both
    "settings": 68,
    # shared: primary Play button glyph 18 AND OSD play/pause alt 56
    "play": 56,
    # OSD transport + track buttons, osd_icon_btn = 56
    "pause": 112, "stop": 112, "next": 112, "prev": 112, "forward": 112, "rewind": 112,
    "subtitles": 112, "audio": 112, "info": 112, "chapters": 112, "shuffle": 112, "repeat": 112,
}


def make_icons() -> None:
    assert set(ICON_PX) == set(ICONS)
    for name, fn in ICONS.items():
        save(draw_icon(fn, ICON_PX[name]), f"icons/{name}.png")


# --------------------------------------------------------------------------- preview
def contact_sheet() -> None:
    """Every texture on #0b0b0b; white chrome shown tinted with the default
    accent (the colordiffuse path), baked assets shown as-is."""
    PREVIEW.mkdir(parents=True, exist_ok=True)
    files = list(WRITTEN)
    cell, cols = 140, 8
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (0x0B, 0x0B, 0x0B, 255))
    for i, p in enumerate(files):
        im = Image.open(p).convert("RGBA")
        im.thumbnail((cell - 30, cell - 30), Image.LANCZOS)
        if p.parent.name == "markers" and p.stem.startswith("watched"):
            tinted = im
        else:
            tinted = Image.new("RGBA", im.size, (0xFF, 0x5A, 0x1F, 255))
            tinted.putalpha(im.getchannel("A"))
        x = (i % cols) * cell + (cell - im.width) // 2
        y = (i // cols) * cell + (cell - 20 - im.height) // 2
        sheet.alpha_composite(Image.new("RGBA", im.size, (0x26, 0x26, 0x26, 255)), (x, y))
        sheet.alpha_composite(tinted, (x, y))
        ImageDraw.Draw(sheet).text(((i % cols) * cell + 4, (i // cols) * cell + cell - 16),
                                   f"{p.parent.name}/{p.stem}"[:22], fill=(0xA3, 0xA1, 0x9B, 255))
    sheet.save(PREVIEW / "contact_sheet.png")


def main() -> None:
    make_common()
    make_focus()
    make_masks()
    make_markers()
    make_icons()
    contact_sheet()
    total = 0
    for p in WRITTEN:
        sz = p.stat().st_size
        total += sz
        w, h = Image.open(p).size
        b = BORDERS.get(p.relative_to(MEDIA).as_posix())
        print(f"{p.relative_to(MEDIA).as_posix():38} {w:>4}x{h:<4} {sz:>7} B" + (f'   border="{b}"' if b else ""))
    print(f"{len(WRITTEN)} files, {total / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
