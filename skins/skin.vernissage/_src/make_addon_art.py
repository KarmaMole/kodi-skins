"""icon.png (512, SOLID RGB) and fanart.jpg (1920x1080) for skin.vernissage, in the skin's own art direction.
    python skins/skin.vernissage/_src/make_addon_art.py     (Pillow + numpy; reads media/vn/spot.png, vignette.png,
                                                             media/vn/flags/*.png and fonts/, so it runs after
                                                             make_textures.py)

Concept (DESIGN 1, "monochrome walls, one work in colour"): the Evening room at the private view. Grey prints hang
bare on one centre line; the one work in colour is matted (lit mat + 2 px hairline frame, DESIGN 6) under the
spotlight pool (spot.png tinted FFF0DA at 30 %, 2.05 x 1.5 the frame, centre 3 % above, DESIGN 5). The fanart adds
the exhibition title and the curator's placard beside the work, built to the placard rules (height = the mat's
height, three blocks, equal gaps, a 56 x 2 rule, the media flags as the skin draws them).
Every picture is generated here (colour-field and horizon studies drawn from noise and soft rectangles); there is no
real or third-party art. Prints are made grey the way the helper makes them (Rec.709 luma on linear values) and
multiplied by print_tint (FF8C8C8C). The official Kodi repository wants a solid icon, so icon.png is saved as RGB.
Deterministic: every random field has its own fixed seed.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKIN = Path(__file__).resolve().parents[1]
VN = SKIN / "media" / "vn"
FONTS = SKIN / "fonts"

# Evening tokens (DESIGN 3)
WALL = (0x16, 0x16, 0x1A)
CARD = (0x1F, 0x1F, 0x24)
CARD_EDGE = (0x2A, 0x2A, 0x30)
INK = (0xED, 0xEB, 0xE6)
INK2 = (0xA8, 0xA6, 0xA1)
PLACARD_RULE = (0x4A, 0x4A, 0x52)
MAT = (0xE6, 0xE1, 0xD8)
FRAME = (0x0B, 0x0B, 0x0D)
SPOT = (0xFF, 0xF0, 0xDA)
SPOT_ALPHA = 0x4D / 255
PRINT_TINT = 0x8C / 255

# the one work in colour: a warm colour field (oxblood ground, cadmium block, ochre block)
LIT = {"ground": (84, 20, 26), "blocks": [((0.09, 0.07, 0.91, 0.55), (214, 78, 40)),
                                          ((0.09, 0.63, 0.91, 0.90), (228, 162, 70))]}
# the grey prints (only their luma survives; the hues just give the studies their tonal structure)
FIELD_COOL = {"ground": (30, 46, 60), "blocks": [((0.10, 0.10, 0.90, 0.36), (170, 186, 196)),
                                                 ((0.10, 0.44, 0.90, 0.88), (70, 96, 120))]}
FIELD_DARK = {"ground": (40, 34, 30), "blocks": [((0.12, 0.12, 0.88, 0.70), (120, 96, 80)),
                                                 ((0.12, 0.77, 0.88, 0.88), (200, 184, 160))]}


# ------------------------------------------------------------------------------------------------- fields
def smooth_noise(h: int, w: int, cells: tuple[int, int], seed: int) -> np.ndarray:
    """Value noise in 0..1: a small random grid upscaled bicubically (cells = rows, cols)."""
    g = np.random.default_rng(seed).random(cells).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8), "L").resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def colour_field(w: int, h: int, spec: dict, seed: int) -> np.ndarray:
    """A colour-field painting: soft-edged blocks on a ground, brushed, on canvas. Float RGB 0..255."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    out = np.zeros((h, w, 3), np.float32) + np.array(spec["ground"], np.float32)
    feather = w * 0.034
    for i, ((fx0, fy0, fx1, fy1), col) in enumerate(spec["blocks"]):
        inside = np.minimum.reduce([x - fx0 * w, fx1 * w - x, y - fy0 * h, fy1 * h - y])
        # a soft painted edge: a slight slow drift plus a fine ragged dry-brush fringe (no visible waves)
        drift = (smooth_noise(h, w, (5, 4), seed + 11 * i) - 0.5) * w * 0.016
        fringe = (smooth_noise(h, w, (max(12, h // 16), max(10, w // 16)), seed + 13 * i) - 0.5) * w * 0.02
        m = sstep(-feather, feather, inside + drift + fringe)
        m = np.asarray(Image.fromarray((m * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(w / 220)), np.float32) / 255
        # the block is thinner at its edges (the ground breathes through), denser at its heart
        body = 0.82 + 0.18 * sstep(0, w * 0.12, inside)
        tone = 1 + (smooth_noise(h, w, (6, 5), seed + 31 * i) - 0.5) * 0.16
        c = np.array(col, np.float32) * (body * tone)[..., None]
        out = out * (1 - m[..., None]) + c * m[..., None]
    # brushed: long horizontal strokes (many rows, few columns) and a faint wide sweep
    strokes = (smooth_noise(h, w, (max(8, h // 6), 5), seed + 97) - 0.5) * 0.07
    sweep = (smooth_noise(h, w, (4, 3), seed + 98) - 0.5) * 0.10
    out *= (1 + strokes + sweep)[..., None]
    return canvas(out, seed)


def horizon(w: int, h: int, seed: int) -> np.ndarray:
    """A tonal sea study: graded sky, a low sun, banded water. Float RGB 0..255 (it only ever hangs grey)."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = y / h
    sky = np.array([60, 70, 86], np.float32) * (1 - t[..., None] / 0.58) + np.array([196, 190, 176], np.float32) * (t[..., None] / 0.58)
    sea_t = np.clip((t - 0.58) / 0.42, 0, 1)[..., None]
    sea = np.array([110, 112, 112], np.float32) * (1 - sea_t) + np.array([28, 32, 38], np.float32) * sea_t
    bands = (smooth_noise(h, w, (max(10, h // 9), 3), seed) - 0.5) * 0.22
    sea = sea * (1 + bands)[..., None]
    out = np.where((t < 0.58)[..., None], sky, sea)
    r = np.sqrt((x - w * 0.62) ** 2 + (y - h * 0.47) ** 2) / (w * 0.09)
    out = out + (255 - out) * (sstep(1.05, 0.9, r) * 0.85)[..., None]
    out = out + (np.exp(-(r / 3.2) ** 2) * 26)[..., None]
    return canvas(out, seed)


def canvas(rgb: np.ndarray, seed: int) -> np.ndarray:
    """Canvas weave and pigment grain, so flat fields read as paint on cloth, not vector fills."""
    h, w = rgb.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    weave = np.sin(x * np.pi / 1.6) * np.sin(y * np.pi / 1.6) * 0.018
    grain = np.random.default_rng(seed + 7).normal(0, 0.022, (h, w)).astype(np.float32)
    return np.clip(rgb * (1 + weave + grain)[..., None], 0, 255)


def grey_print(rgb: np.ndarray) -> np.ndarray:
    """The helper's neutral grey copy (Rec.709 luma on linearised values) under print_tint (multiply .55)."""
    lin = (rgb / 255) ** 2.2
    lum = (lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)) ** (1 / 2.2) * 255
    return np.repeat(lum[..., None], 3, -1) * PRINT_TINT


# ------------------------------------------------------------------------------------------------- the room
def tpdf(shape, seed):
    g = np.random.default_rng(seed)
    return (g.random(shape) - g.random(shape)).astype(np.float32)


def alpha_of(name: str, size: tuple[int, int]) -> np.ndarray:
    im = Image.open(VN / name).convert("RGBA").resize(size, Image.BICUBIC)
    return np.asarray(im, np.float32)[..., 3] / 255


def over(base: np.ndarray, colour, alpha: np.ndarray, box=(0, 0)) -> None:
    """Composite a flat colour through alpha onto base at box (x, y), clipped to the canvas. In place."""
    H, W = base.shape[:2]
    x, y = box
    h, w = alpha.shape
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    c = np.asarray(colour, np.float32)
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1 - a) + c * a


def paste(base: np.ndarray, rgb: np.ndarray, x: int, y: int) -> None:
    H, W = base.shape[:2]
    h, w = rgb.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 < x1 and y0 < y1:
        base[y0:y1, x0:x1] = rgb[y0 - y:y1 - y, x0 - x:x1 - x]


def fill(base: np.ndarray, rect, colour) -> None:
    x0, y0, x1, y1 = rect
    base[max(0, y0):y1, max(0, x0):x1] = np.asarray(colour, np.float32)


def room(W: int, H: int, frame_rect, vignette_gain=1.0, seed=1) -> np.ndarray:
    """The Evening wall, its vignette, and the spotlight pool for the work in frame_rect (DESIGN 5)."""
    base = np.zeros((H, W, 3), np.float32) + np.array(WALL, np.float32)
    over(base, (0, 0, 0), np.clip(alpha_of("vignette.png", (W, H)) * vignette_gain, 0, 1))
    fx0, fy0, fx1, fy1 = frame_rect
    fw, fh = fx1 - fx0, fy1 - fy0
    pw, ph = int(round(fw * 2.05)), int(round(fh * 1.5))
    cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2 - 0.03 * fh
    over(base, SPOT, alpha_of("spot.png", (pw, ph)) * SPOT_ALPHA, (int(round(cx - pw / 2)), int(round(cy - ph / 2))))
    return base + tpdf(base.shape, seed)


def lit_work(base: np.ndarray, x: int, y: int, art: np.ndarray, mat: int, hair: int) -> tuple[int, int, int, int]:
    """Frame (hairline) > mat (with its top-lit falloff) > the work at 100 %. Returns the frame's outer rect."""
    h, w = art.shape[:2]
    fw, fh = w + 2 * (mat + hair), h + 2 * (mat + hair)
    fill(base, (x, y, x + fw, y + fh), FRAME)
    mx0, my0, mx1, my1 = x + hair, y + hair, x + fw - hair, y + fh - hair
    fill(base, (mx0, my0, mx1, my1), MAT)
    t = np.linspace(0, 1, my1 - my0, dtype=np.float32)[:, None].repeat(mx1 - mx0, 1)
    over(base, (0, 0, 0), np.clip((t - 0.3) / 0.7, 0, 1) * 0.16, (mx0, my0))   # mat_falloff.png
    paste(base, art, x + hair + mat, y + hair + mat)
    return x, y, x + fw, y + fh


def seen_dot(base: np.ndarray, px1: int, py1: int, d: int = 14, ring: int = 3, ss: int = 4) -> None:
    """DESIGN 6: a 14 px ink dot with a 3 px wall ring, 10 px in from the print's bottom-right corner."""
    def disc(diam):
        m = Image.new("L", (diam * ss, diam * ss), 0)
        ImageDraw.Draw(m).ellipse((0, 0, diam * ss - 1, diam * ss - 1), fill=255)
        return np.asarray(m.resize((diam, diam), Image.LANCZOS), np.float32) / 255
    cx, cy = px1 - 10 - d // 2, py1 - 10 - d // 2
    D = d + 2 * ring
    over(base, WALL, disc(D), (cx - D // 2, cy - D // 2))
    over(base, INK, disc(d), (cx - d // 2, cy - d // 2))


def to_image(rgb: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(np.round(rgb), 0, 255).astype(np.uint8), "RGB")


# ------------------------------------------------------------------------------------------------- type
def font(name: str, px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), px)


def flag_strip(img: Image.Image, x: int, y: int, slugs: list[str], gap: int = 10) -> None:
    """The media flags exactly as the skin draws them: the white textures tinted ink2."""
    for s in slugs:
        a = Image.open(VN / "flags" / f"{s}.png").convert("RGBA").getchannel("A")
        img.paste(Image.new("RGB", a.size, INK2), (x, y), a)
        x += a.size[0] + gap


def wrap(text: str, f, measure: float, max_lines: int) -> list[str]:
    """Greedy word wrap to the measure; the art is fixed text, so overflow is a build error, not a cut."""
    words, lines = text.split(), [""]
    for wd in words:
        t = (lines[-1] + " " + wd).strip()
        if f.getlength(t) <= measure:
            lines[-1] = t
        else:
            lines.append(wd)
    assert len(lines) <= max_lines, (text, lines)
    return lines


def placard(img: Image.Image, rect) -> None:
    """The curator's card (DESIGN 6) for the skin itself: identity / the card / the state, equal gaps."""
    x0, y0, x1, y1 = rect
    d = ImageDraw.Draw(img)
    d.rectangle(rect, fill=CARD, outline=CARD_EDGE, width=1)
    px, pt, pb = x0 + 30, y0 + 28, y1 - 28
    measure = (x1 - x0 + 1) - 2 * 30
    title, body, small = font("InterTight-SemiBold.ttf", 44), font("InterTight-Regular.ttf", 30), font("InterTight-Regular.ttf", 28)
    quote = font("Fraunces-DisplayItalic.ttf", 32)
    # top block: title, byline, "genres"
    top = [("Vernissage", title, INK, 0), ("2026 · Omar Kamel", body, INK2, 8), ("A skin for Kodi · Day, dusk, Evening", small, INK2, 0)]
    # middle block: tagline (2 lines) + premise (3 lines)
    mid = [("Monochrome walls,", quote, INK, 0), ("one work in colour.", quote, INK, 0),
           ]
    premise = "A private gallery that changes with the light. At night only the work in front of you is lit."
    for n, ln in enumerate(wrap(premise, small, measure, 3)):
        mid.append((ln, small, INK2, 12 if n == 0 else 0))
    for text, f, _, _ in top + mid:
        assert f.getlength(text) <= measure, text

    def block_h(lines):
        return sum(f.getbbox("Hg")[3] - f.getbbox("H")[1] + 10 + g for _, f, _, g in lines) - 10

    def draw_block(lines, y):
        for text, f, col, g in lines:
            y += g
            d.text((px, y - f.getbbox("H")[1]), text, font=f, fill=col)
            y += f.getbbox("Hg")[3] - f.getbbox("H")[1] + 10
        return y

    # bottom block, laid out from the bottom padding up: key line, rule, status, flags
    key_y = pb - (body.getbbox("Hg")[3] - body.getbbox("H")[1])
    rule_y = key_y - 14 - 2
    status_y = rule_y - 16 - (body.getbbox("Hg")[3] - body.getbbox("H")[1])
    flags_y = status_y - 14 - 36
    th, mh = block_h(top), block_h(mid)
    gap = (flags_y - pt - th - mh) / 2       # the two gaps are always equal
    draw_block(top, pt)
    draw_block(mid, int(round(pt + th + gap)))
    flag_strip(img, px, flags_y, ["4k", "dolby_vision", "atmos", "7_1"])
    d.text((px, status_y - body.getbbox("H")[1]), "★ Unseen · opening night", font=body, fill=INK2)
    d.rectangle((px, rule_y, px + 55, rule_y + 1), fill=PLACARD_RULE)
    d.text((px, key_y - body.getbbox("H")[1]), "Doors 7:00 pm · ends 11:18 pm", font=body, fill=INK)


def exhibition_title(img: Image.Image, x: int, baseline: int) -> None:
    """DESIGN 4: the italic lead word, then the roman rest as a second label right after it."""
    d = ImageDraw.Draw(img)
    it, ro = font("Fraunces-DisplayItalic.ttf", 60), font("Fraunces-Display.ttf", 60)
    d.text((x, baseline), "Tonight", font=it, fill=INK, anchor="ls")
    x += d.textlength("Tonight", font=it)
    d.text((x, baseline), ": the private view", font=ro, fill=INK, anchor="ls")


# ------------------------------------------------------------------------------------------------- scenes
def fanart() -> Image.Image:
    W, H, line = 1920, 1080, 584                          # centre line of the hang
    art = colour_field(408, 544, LIT, 501)
    mat, hair = 22, 2
    fw, fh = 408 + 2 * (mat + hair), 544 + 2 * (mat + hair)
    fx, fy = 700, line - fh // 2
    base = room(W, H, (fx, fy, fx + fw, fy + fh), seed=11)
    # grey prints, bare, on the centre line (A carries the seen dot); C runs off the wall to the right
    prints = [(-40, 300, 400, grey_print(horizon(300, 400, 601))),
              (330, 300, 400, grey_print(colour_field(300, 400, FIELD_COOL, 602))),
              (1770, 260, 360, grey_print(colour_field(260, 360, FIELD_DARK, 603)))]
    for x, w, h, rgb in prints:
        paste(base, rgb, x, line - h // 2)
    seen_dot(base, 330 + 300, line + 200)
    lit_work(base, fx, fy, art, mat, hair)
    img = to_image(base)
    # the placard: 40 px right of the frame, its edges on the mat's edges (frame.top + 2, frame height - 4)
    placard(img, (fx + fw + 40, fy + hair, fx + fw + 40 + 504 - 1, fy + fh - hair - 1))
    exhibition_title(img, 120, 150)
    return img


def icon() -> Image.Image:
    """Drawn at 1024 and reduced: the lit work under its pool, a grey print at each edge, no words."""
    S = 1024
    art = colour_field(360, 480, LIT, 501)
    mat, hair = 34, 4
    fw, fh = 360 + 2 * (mat + hair), 480 + 2 * (mat + hair)
    fx, fy = (S - fw) // 2, 532 - fh // 2
    base = room(S, S, (fx, fy, fx + fw, fy + fh), vignette_gain=1.25, seed=12)
    # a grey print at each edge, 60 px off the frame, on the same centre line
    for x, rgb in ((fx - 60 - 260, grey_print(horizon(260, 350, 611))),
                   (fx + fw + 60, grey_print(colour_field(260, 350, FIELD_COOL, 612)))):
        paste(base, rgb, x, 532 - 175)
    lit_work(base, fx, fy, art, mat, hair)
    return to_image(base).resize((512, 512), Image.LANCZOS)


def main() -> None:
    fan = fanart()
    fan.save(SKIN / "fanart.jpg", quality=90, optimize=True)
    ic = icon()
    ic.save(SKIN / "icon.png", optimize=True)
    print("wrote", SKIN / "icon.png", ic.size, ic.mode, "|", SKIN / "fanart.jpg", fan.size)


if __name__ == "__main__":
    main()
