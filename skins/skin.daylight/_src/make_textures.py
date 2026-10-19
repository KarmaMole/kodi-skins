"""Generate every Daylight texture into ../media (reproducible; run after any change).

All shapes are WHITE (tinted at runtime with the mood tokens via colordiffuse), except where noted.
Soft things (gradients, glows, shadows) are dithered with blue-ish noise before 8-bit quantisation so
the pale Morning/Afternoon palettes don't band on the Shield.

Needs: Pillow, numpy, cairosvg.   Usage: python skins/skin.daylight/_src/make_textures.py
Texture names that the forked engine already references (common/, focus/, icons/, markers/,
masks/, osd/, dialogs/, vidview/, music/) are kept, redrawn in Daylight's language; new ones live in
media/daylight/.
"""
from pathlib import Path
import io

import numpy as np
from PIL import Image, ImageFilter
import cairosvg

MEDIA = Path(__file__).resolve().parents[1] / "media"
RNG = np.random.default_rng(7)


# ------------------------------------------------------------------ helpers
def save(img: Image.Image, rel: str) -> None:
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def alpha_img(a: np.ndarray, dither: bool = True) -> Image.Image:
    """float alpha 0..1 -> white RGBA, dithered."""
    a = np.clip(a, 0, 1) * 255.0
    if dither:
        a = a + RNG.uniform(-0.5, 0.5, a.shape) + RNG.uniform(-0.5, 0.5, a.shape)
    a = np.clip(np.round(a), 0, 255).astype(np.uint8)
    h, w = a.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = a
    return Image.fromarray(rgba, "RGBA")


def svg(body: str, w: int, h: int, vb: str | None = None) -> Image.Image:
    vb = vb or f"0 0 {w} {h}"
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{body}</svg>'
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=doc.encode()))).convert("RGBA")


def rrect(w, h, r, fill=True, stroke=0.0, inset=0.0):
    if fill:
        return svg(f'<rect x="{inset}" y="{inset}" width="{w - 2 * inset}" height="{h - 2 * inset}" rx="{r}" fill="#fff"/>', w, h)
    s = stroke / 2 + inset
    return svg(f'<rect x="{s}" y="{s}" width="{w - 2 * s}" height="{h - 2 * s}" rx="{max(r - s, 0)}" fill="none" stroke="#fff" stroke-width="{stroke}"/>', w, h)


def icon(paths: str, px: int, stroke: float = 2.0, fill_mode: bool = False) -> Image.Image:
    if fill_mode:
        body = f'<g fill="#fff">{paths}</g>'
    else:
        body = f'<g fill="none" stroke="#fff" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{paths}</g>'
    return svg(body, px, px, "0 0 24 24")


def blur_shape(w, h, shape: Image.Image, radius: float, ox=0, oy=0) -> Image.Image:
    base = Image.new("L", (w, h), 0)
    base.paste(shape.split()[3], (ox, oy))
    a = np.asarray(base.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255.0
    return alpha_img(a)


# ------------------------------------------------------------------ common
def common():
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "common/white.png")
    hl = Image.new("RGBA", (8, 1), (255, 255, 255, 255)); save(hl, "common/hairline.png")
    save(Image.new("RGBA", (1, 8), (255, 255, 255, 255)), "common/hairline_v.png")
    t = np.linspace(0, 1, 256)[:, None]
    ease = t * t * (3 - 2 * t)
    save(alpha_img(np.repeat(ease, 16, 1)), "common/gradient_bottom.png")          # opaque at bottom
    save(alpha_img(np.repeat(ease[::-1], 16, 1)), "common/gradient_top.png")       # opaque at top
    save(alpha_img(np.repeat(ease.T, 16, 0)), "common/gradient_right.png")
    save(alpha_img(np.repeat(ease.T[:, ::-1], 16, 0)), "common/gradient_left.png")
    st = np.linspace(0, 1, 540)[:, None]
    save(alpha_img(np.repeat(np.clip(st * 1.4, 0, 1) ** 1.6, 16, 1)), "common/gradient_stage.png")
    s = np.linspace(0, 1, 512)[:, None]
    save(alpha_img(np.repeat(0.92 * s ** 1.4, 16, 1)), "common/scrim_bottom.png")
    save(alpha_img(np.repeat((0.92 * s[::-1] ** 1.4).T, 16, 0)), "common/scrim_left.png")
    # buttons / boxes (32x32, border 10)
    save(rrect(32, 32, 10), "common/rect_round8.png")
    save(rrect(32, 32, 7), "common/rect_square.png")
    save(rrect(32, 32, 10, False, 2), "common/rect_outline_1.png")
    save(rrect(32, 32, 10, False, 2), "common/rect_outline_1_round8.png")
    # soft shadow 384 (border 128): blurred 128px rounded square in the middle
    sq = rrect(128, 128, 28)
    save(blur_shape(384, 384, sq, 34, 128, 128), "common/shadow_soft.png")


# ------------------------------------------------------------------ dialogs / focus
def dialogs_focus():
    save(rrect(64, 64, 24), "dialogs/panel_framed.png")                 # border 26
    rr = Image.new("RGBA", (4, 8), (0, 0, 0, 0))
    for x in range(4):
        rr.putpixel((x, 7), (255, 255, 255, 255))
    save(rr, "dialogs/row_rule.png")
    # focus rings 40x40 border 16 (radius 16, 3 px / 4 px)
    save(rrect(40, 40, 16, False, 3), "focus/outline_2.png")
    save(rrect(40, 40, 16, False, 3), "focus/outline_2_round.png")
    save(rrect(40, 40, 16, False, 4), "focus/outline_3.png")
    save(rrect(40, 40, 16, False, 4), "focus/outline_3_round.png")
    save(blur_shape(96, 96, rrect(32, 32, 12), 10, 32, 32), "focus/halo.png")


# ------------------------------------------------------------------ masks (diffuse)
def mask(w, h, r_ratio, rel, corners="all"):
    r = r_ratio * w
    img = rrect(w, h, r)
    if corners == "right":   # square left corners
        a = np.asarray(img).copy()
        a[:, : w // 2, 3] = 255
        img = Image.fromarray(a, "RGBA")
    save(img, rel)


def masks():
    pr = 20 / 184
    mask(336, 504, pr, "masks/poster_round8.png")
    mask(660, 990, pr, "masks/poster_round8_large.png")
    mask(1040, 1560, pr, "masks/poster_round8_xl.png")
    mask(336, 504, pr, "masks/poster_square.png")
    lr = 16 / 192
    mask(640, 360, lr, "masks/landscape_round8.png")
    mask(1920, 1080, 28 / 1140, "masks/landscape_round8_large.png")
    mask(640, 360, lr, "masks/landscape_square.png")
    sr = 18 / 200
    mask(438, 438, sr, "masks/square_round8.png")
    mask(760, 760, sr, "masks/square_round8_large.png")
    mask(438, 438, sr, "masks/square_square.png")
    mask(1120, 1120, sr, "music/square_round8_560.png")
    # Daylight specific
    mask(368, 552, 16 / 140, "daylight/mask_poster_s.png")             # Home posters 140x210 r16
    mask(288, 432, 14 / 72, "daylight/mask_poster_xs.png")             # OSD poster 72x108 r14
    mask(1140, 352, 28 / 1140, "daylight/mask_hero.png", "right")       # hero art: right corners only
    mask(384, 216, 16 / 192, "daylight/mask_thumb.png")                # episode thumbs 192x108 r16
    mask(1140, 520, 28 / 1140, "daylight/mask_hero_tall.png", "right")  # info page art 1140x520
    mask(520, 780, 20 / 260, "daylight/mask_poster_info.png")          # info poster 260x390 r20
    mask(336, 336, 0.5, "daylight/mask_circle.png")                    # round portraits
    mask(780, 780, 20 / 390, "daylight/mask_cover.png")                # info covers 390x390 r20
    mask(1200, 1200, 28 / 600, "daylight/mask_cover_l.png")            # now playing cover 600x600 r28
    mask(144, 144, 10 / 48, "daylight/mask_cover_s.png")               # row covers 48-72 r10


# ------------------------------------------------------------------ Daylight surfaces
def daylight_surfaces():
    save(rrect(128, 128, 28), "daylight/card.png")                      # border 40
    save(rrect(128, 128, 28, False, 2), "daylight/card_line.png")       # 2px outline, border 40
    save(rrect(64, 64, 20), "daylight/card20.png")                      # border 24
    save(rrect(64, 64, 16), "daylight/card16.png")                      # border 20
    # card shadow: 9-slice 400 (border 180). Place at card rect -120 (left/right/top) / +120 bottom, shifted +30 y.
    save(blur_shape(400, 400, rrect(160, 160, 28), 32, 120, 120), "daylight/card_shadow.png")
    # pills: exact heights, border "h/2,0,h/2,0"
    for h in (40, 44, 52, 56, 64, 72):
        save(rrect(h * 2, h, h / 2), f"daylight/pill_{h}.png")
        save(rrect(h * 2, h, h / 2, False, 2), f"daylight/pill_{h}_line.png")
    # focus halo for pills: blurred pill, drawn 24 px larger on each side
    for h in (52, 56, 64):
        W, H = h * 2 + 48, h + 48
        save(blur_shape(W, H, rrect(h * 2, h, h / 2), 9, 24, 24), f"daylight/pill_{h}_glow.png")
        # 5 px ring just outside the pill: drawn at -5 each side
        save(rrect(h * 2 + 10, h + 10, (h + 10) / 2, False, 5), f"daylight/pill_{h}_ring.png")
    # circles
    for d in (12, 24, 38, 64):
        save(svg(f'<circle cx="{d / 2}" cy="{d / 2}" r="{d / 2}" fill="#fff"/>', d * 2, d * 2, f"0 0 {d} {d}"), f"daylight/circle_{d}.png")
    save(svg('<circle cx="18" cy="18" r="15.5" fill="none" stroke="#fff" stroke-width="5"/>', 72, 72, "0 0 36 36"), "daylight/nib_ring.png")
    # progress / slider track, 12 px high (border 6,0,6,0)
    save(rrect(24, 12, 6), "daylight/track_12.png")
    save(rrect(6, 30, 3), "daylight/tick_bed.png")  # bedtime tick on the OSD track
    save(rrect(16, 8, 4), "daylight/track_8.png")
    # focus rings around rounded art: gap ring (surface colour, 5 px) + accent ring (4 px), radius per art
    for r in (14, 16, 20, 28):
        g = 5
        size = 2 * (r + g) + 32
        save(rrect(size, size, r + g, False, g), f"daylight/ring_gap_{r}.png")           # place at -5
        size2 = 2 * (r + g + 4) + 32
        save(rrect(size2, size2, r + g + 4, False, 4), f"daylight/ring_{r}.png")         # place at -9
        save(blur_shape(size2 + 80, size2 + 80, rrect(size2 - 18, size2 - 18, r + 4), 16, 49, 49), f"daylight/ring_glow_{r}.png")  # place at -44
    # hero fade over the art (art-local x: opaque 0..65, .82 at 300, 0 at 838), 1140 wide
    x = np.arange(1140, dtype=np.float32)
    a = np.interp(x, [0, 65, 300, 838, 1140], [1.0, 1.0, 0.82, 0.0, 0.0])
    save(alpha_img(np.repeat(a[None, :], 8, 0)), "daylight/hero_fade.png")
    # bottom fade for the poster grid card (150 px, to surface at 85%)
    y = np.linspace(0, 1, 150)
    a = np.clip(y / 0.85, 0, 1) ** 1.2
    save(alpha_img(np.repeat(a[:, None], 8, 1)), "daylight/fade_bottom_150.png")
    # bottom-fade masks: rectangles whose BOTTOM corners follow the 28 px card radius
    for w, name in ((1120, "mask_fade_card"), (1680, "mask_fade_wide"), (500, "mask_fade_panel")):
        img = Image.new("RGBA", (w, 150), (255, 255, 255, 255))
        rr = rrect(w, 300, 28)
        img = Image.fromarray(np.asarray(rr)[150:, :, :].copy(), "RGBA")
        save(img, f"daylight/{name}.png")
    # radial glow (dithered), stretched to ellipses at runtime
    n = 1024
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    d = np.sqrt(((xx - n / 2 + 0.5) / (n / 2)) ** 2 + ((yy - n / 2 + 0.5) / (n / 2)) ** 2)
    g = np.clip(1 - d / 0.70, 0, 1)                 # CSS radial "... 0) 70%"
    g = g * g * (3 - 2 * g)
    save(alpha_img(g), "daylight/glow.png")
    g2 = np.clip(1 - d, 0, 1) ** 1.6
    save(alpha_img(g2), "daylight/glow_soft.png")
    # borrowed-colour glows: the TMDb colour arrives opaque (FFrrggbb), so the per-mood strength is
    # baked into the alpha (mockup: morning .34, afternoon .30, evening .24, night .14; second glow ~half)
    for m, k in (("m", 0.34), ("a", 0.30), ("e", 0.24), ("n", 0.14)):
        save(alpha_img(g * k), f"daylight/glow_art_{m}.png")
        save(alpha_img(g * k * 0.48), f"daylight/glow_art2_{m}.png")
    # OSD scrims (night mockup): bottom 560 px 0 -> .55 @50% -> .92; top 240 px .78 -> 0
    y = np.linspace(0, 1, 560)
    a = np.interp(y, [0, 0.5, 1], [0.0, 0.55, 0.92])
    save(alpha_img(np.repeat(a[:, None], 8, 1)), "daylight/osd_scrim_bottom.png")
    y = np.linspace(0, 1, 240)
    a = 0.78 * (1 - y) ** 1.3
    save(alpha_img(np.repeat(a[:, None], 8, 1)), "daylight/osd_scrim_top.png")
    # rain streaks, tileable 960x540 (drawn 1920x1080 at ~7% via colordiffuse)
    rain = Image.new("L", (960, 540), 0)
    arr = np.zeros((540, 960), np.float32)
    for _ in range(70):
        x0 = RNG.uniform(0, 960); y0 = RNG.uniform(0, 540); ln = RNG.uniform(30, 75); op = RNG.uniform(0.55, 1.0)
        for i in range(int(ln)):
            t = i / ln
            xi = int(x0 + i * 0.25) % 960; yi = int(y0 + i) % 540
            arr[yi, xi] = max(arr[yi, xi], op * t)
    save(alpha_img(arr, dither=False), "daylight/rain.png")


# ------------------------------------------------------------------ OSD / misc legacy names
def osd_legacy():
    # invisible slider bar: sliders / ranges draw only their nib / ticks; the visible track is a
    # separate rounded image + progress control
    save(Image.new("RGBA", (16, 32), (255, 255, 255, 0)), "osd/slider_bg.png")
    nib = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    nib.paste(svg('<circle cx="12" cy="12" r="12" fill="#fff"/>', 24, 24), (20, 4))
    save(nib, "osd/slider_nib.png")
    # Daylight playhead: 24 px nib + 6 px halo ring at 22 % (one tint), 64x40 canvas, nib centred
    nib2 = svg('<circle cx="32" cy="20" r="18" fill="#fff" fill-opacity="0.22"/><circle cx="32" cy="20" r="12" fill="#fff"/>', 64, 40)
    save(nib2, "daylight/nib.png")
    tick = Image.new("RGBA", (2, 32), (255, 255, 255, 255)); save(tick, "osd/tick.png")
    w, h = 480, 270
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx / w) ** 2 + ((h - yy) / h) ** 2)
    save(alpha_img(np.clip(1 - d, 0, 1) ** 1.3 * 0.85), "osd/scrim_corner_bl.png")
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "misc/epg_now.png")
    dimp = Image.new("RGBA", (8, 8), (0, 0, 0, 140)); save(dimp, "vidview/dim_passed.png")
    dima = Image.new("RGBA", (8, 8), (0, 0, 0, 51)); save(dima, "vidview/dim_ahead.png")
    ul = Image.new("RGBA", (8, 80), (0, 0, 0, 0))
    ul.paste(rrect(8, 4, 2), (0, 72)); save(ul, "vidview/underline.png")
    tu = Image.new("RGBA", (8, 12), (0, 0, 0, 0))
    tu.paste(rrect(8, 4, 2), (0, 8)); save(tu, "music/tab_underline.png")


# ------------------------------------------------------------------ icons
ICONS = {
    # name: (svg body on a 24 grid, stroke or None for fill)
    "sun": ('<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/>', 2),
    "sunset": ('<path d="M3 17h18M6.5 17a5.5 5.5 0 0 1 11 0M12 4v3.5M5.2 9.2l1.6 1.6M18.8 9.2l-1.6 1.6M8 21h8"/>', 2),
    "moon": ('<path d="M20 14.6A8.2 8.2 0 0 1 9.4 4a8.2 8.2 0 1 0 10.6 10.6z"/>', 2),
    "cloud": ('<path d="M17.2 17H7.4a3.9 3.9 0 1 1 1-7.7 5.3 5.3 0 0 1 10.1 1.6 3.1 3.1 0 0 1-1.3 6.1z"/>', 2),
    "rain": ('<path d="M17.2 14.5H7.4a3.9 3.9 0 1 1 1-7.7 5.3 5.3 0 0 1 10.1 1.6 3.1 3.1 0 0 1-1.3 6.1z"/><path d="M9 17.5l-1 2.5M13 17.5l-1 2.5M17 17.5l-1 2.5"/>', 2),
    "snow": ('<path d="M17.2 14.5H7.4a3.9 3.9 0 1 1 1-7.7 5.3 5.3 0 0 1 10.1 1.6 3.1 3.1 0 0 1-1.3 6.1z"/><path d="M8.5 18.5h.01M12 20h.01M15.5 18.5h.01"/>', 2.6),
    "clock": ('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', 2),
    "nextup": ('<path d="M5 6.5v11l8-5.5z"/><path d="M17 6.5v11"/>', 2),
    "star": ('<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8z"/>', None),
    "check": ('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 2.6),
    "sparkle": ('<path d="M12 3.5l1.9 5.1 5.1 1.9-5.1 1.9-1.9 5.1-1.9-5.1L5 10.5l5.1-1.9z"/><path d="M18.5 16l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>', 1.8),
    "play": ('<path d="M7 4.8v14.4l12-7.2z"/>', None),
    "pause": ('<rect x="6" y="5" width="4" height="14" rx="1.5"/><rect x="14" y="5" width="4" height="14" rx="1.5"/>', None),
    "back10": ('<path d="M4 12a8 8 0 1 0 2.4-5.7L4 8.5"/><path d="M4 4v4.5h4.5"/>', 2),
    "fwd30": ('<path d="M20 12a8 8 0 1 1-2.4-5.7L20 8.5"/><path d="M20 4v4.5h-4.5"/>', 2),
    "sleep": ('<path d="M20 14.6A8.2 8.2 0 0 1 9.4 4a8.2 8.2 0 1 0 10.6 10.6z"/><path d="M15 4h4l-4 4h4"/>', 2.2),
    "search": ('<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4 4"/>', 2.2),
    "settings": ('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>', 1.8),
    "back": ('<path d="M14.5 6l-6 6 6 6"/>', 2.4),
    "chevron_right": ('<path d="M9.5 6l6 6-6 6"/>', 2.4),
    "chevron_down": ('<path d="M6 9.5l6 6 6-6"/>', 2.4),
    "subtitles": ('<rect x="3" y="5" width="18" height="14" rx="4"/><path d="M7 13h4M13 13h4M7 16h7"/>', 2),
    "audio": ('<path d="M11 5L6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/>', 2),
    "chapters": ('<path d="M4 6h16M4 12h16M4 18h10"/>', 2.2),
    "info": ('<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 8h.01"/>', 2.2),
    "stop": ('<rect x="6" y="6" width="12" height="12" rx="3"/>', None),
    "next": ('<path d="M6 5.5v13l9-6.5z"/><rect x="16" y="5.5" width="2.6" height="13" rx="1.2"/>', None),
    "prev": ('<path d="M18 5.5v13l-9-6.5z"/><rect x="5.4" y="5.5" width="2.6" height="13" rx="1.2"/>', None),
    "forward": ('<path d="M3.5 6v12l8.5-6zM12.5 6v12l8.5-6z"/>', None),
    "rewind": ('<path d="M20.5 6v12L12 12zM11.5 6v12L3 12z"/>', None),
    "repeat": ('<path d="M17 3.5l3 3-3 3"/><path d="M4 11.5v-1a4 4 0 0 1 4-4h12M7 20.5l-3-3 3-3"/><path d="M20 12.5v1a4 4 0 0 1-4 4H4"/>', 2),
    "shuffle": ('<path d="M16 3.5h4.5V8M4 20l16.5-16.5M20.5 16v4.5H16M14.5 14.5l6 6M4 4l5 5"/>', 2),
    "power": ('<path d="M12 3.5v8"/><path d="M6.7 6.6a7.5 7.5 0 1 0 10.6 0"/>', 2.2),
    "film": ('<rect x="3.5" y="4.5" width="17" height="15" rx="3.5"/><path d="M8 4.5v15M16 4.5v15M3.5 9.5H8M3.5 14.5H8M16 9.5h4.5M16 14.5h4.5"/>', 1.8),
    "tv": ('<rect x="3" y="5.5" width="18" height="12.5" rx="3"/><path d="M8.5 21h7M9 2.5l3 3 3-3"/>', 2),
    "music": ('<path d="M9 18V6l11-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>', 2),
    "home": ('<path d="M4 11l8-6.5 8 6.5v8a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19z"/><path d="M10 20.5v-5h4v5"/>', 2),
}


def icons():
    for name, (body, stroke) in ICONS.items():
        for px, folder in ((96, "daylight/icons"),):
            img = icon(body, px, stroke or 2, fill_mode=stroke is None)
            save(img, f"{folder}/{name}.png")
    # legacy icon names used by the forked engine
    legacy = {"audio": ("audio", 112), "back": ("back", 48), "chapters": ("chapters", 112), "chevron_down": ("chevron_down", 48),
              "chevron_right": ("chevron_right", 48), "forward": ("fwd30", 112), "info": ("info", 112), "next": ("next", 112),
              "pause": ("pause", 112), "play": ("play", 56), "prev": ("prev", 112), "repeat": ("repeat", 112),
              "rewind": ("back10", 112), "search": ("search", 52), "settings": ("settings", 68), "shuffle": ("shuffle", 112),
              "stop": ("stop", 112), "subtitles": ("subtitles", 112)}
    for out, (src, px) in legacy.items():
        body, stroke = ICONS[src]
        save(icon(body, px, stroke or 2, fill_mode=stroke is None), f"icons/{out}.png")


def markers():
    save(icon(ICONS["check"][0], 48, 2.8), "markers/check.png")
    dot = svg('<circle cx="12" cy="12" r="7" fill="#fff"/>', 24, 24)
    save(dot, "markers/unwatched.png"); save(dot, "markers/unwatched_round.png")
    # watched badge (baked, readable on any art): white disc + slate check, soft shadow
    W = 44
    sh = blur_shape(W, W, svg('<circle cx="19" cy="19" r="17" fill="#fff"/>', 38, 38), 2.2, 3, 4)
    a = np.asarray(sh).astype(np.float32)
    a[..., :3] = 0; a[..., 3] *= 0.35
    base = Image.fromarray(a.astype(np.uint8), "RGBA")
    disc = svg('<circle cx="22" cy="22" r="17" fill="#fff"/><path d="M15 22.5l4.5 4.5L29 17.5" fill="none" stroke="#3E5468" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>', W, W)
    base.alpha_composite(disc)
    save(base, "markers/watched.png"); save(base, "markers/watched_round.png")


def baked_panels():
    """Context-menu panel: Kodi resizes ONE image (id 999), so the shadow and the mood fill are baked
    together, one texture per mood (picked with $VAR[DL_PanelTex])."""
    moods = {"m": ((255, 255, 255), (31, 41, 51), 0.16), "a": ((255, 253, 249), (42, 32, 21), 0.17),
             "e": ((58, 46, 42), (18, 10, 8), 0.45), "n": ((21, 29, 49), (2, 4, 10), 0.55)}
    S, M, R = 192, 40, 24
    for m, (fill, shade, k) in moods.items():
        shape = rrect(S - 2 * M, S - 2 * M, R)
        base = Image.new("L", (S, S), 0)
        base.paste(shape.split()[3], (M, M + 10))
        sh = np.asarray(base.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255.0 * k
        out = np.zeros((S, S, 4), np.float32)
        out[..., 0], out[..., 1], out[..., 2] = shade
        out[..., 3] = sh * 255
        img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
        card = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        fillimg = Image.new("RGBA", (S - 2 * M, S - 2 * M), fill + (255,))
        fillimg.putalpha(shape.split()[3])
        card.paste(fillimg, (M, M))
        img.alpha_composite(card)
        save(img, f"dialogs/panel_{m}.png")


def main():
    common(); dialogs_focus(); masks(); daylight_surfaces(); osd_legacy(); icons(); markers(); baked_panels()
    n = sum(1 for _ in MEDIA.rglob("*.png"))
    print(f"media: {n} png")


if __name__ == "__main__":
    main()
