"""Generate every static texture in skin.orbit/media (except the ring frame sets: make_rings.py).

Orbit's look is drawn here, so the whole media/ tree is reproducible:
  common/   fills, fine lines, gradients, scrims, radial lifts, chips, shadow
  focus/    corner brackets (posters/tiles), row focus (lists/settings/dialogs)
  btn/      round buttons at exact pixel sizes (fill, outline, focus halo)
  masks/    4px-radius poster/square/landscape masks + circle mask
  markers/  watched badge, unwatched pip, check
  icons/    1.8px line icons drawn on the mockups' 24-unit grid
  misc/     calibration targets, EPG now marker (Kodi-owned windows)
Everything is drawn at 4x and downsampled (LANCZOS) for clean anti-aliasing.

Palette (docs/skin.orbit/DESIGN.md): ground #0A1226 (full screens: make_ground.py), panel #0D1529, line #2B3240,
tick #566075, text #E9EDF3, secondary #8B95A7, accent amber #FFB547.
Most textures are WHITE and tinted with colordiffuse in XML; the few that carry
their own colours say so.

Usage: python skins/skin.orbit/_src/make_textures.py
"""
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
SS = 4  # supersampling

WHITE = (255, 255, 255, 255)
AMBER = (255, 181, 71, 255)
TEXT = (233, 237, 243, 255)
GROUND = (10, 18, 38, 255)   # 0.9.2 navy ground (bg token #0A1226)
RAISED = (26, 39, 68, 255)   # bg_raised #1A2744


def save(img, rel):
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def canvas(w, h, ss=SS):
    img = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------ basics
def basics():
    save(Image.new("RGBA", (8, 8), WHITE), "common/white.png")
    # 1px rules with a transparent buffer row (9-slice bleed lesson): hairline used stretched
    h = Image.new("RGBA", (8, 1), WHITE)
    save(h, "common/hairline.png")
    save(Image.new("RGBA", (1, 8), WHITE), "common/hairline_v.png")
    # rect fills / outlines, 32px, border 10 (legacy names kept; Orbit corner radius is 4)
    for name, radius, outline in [("rect_square", 0, 0), ("rect_round8", 4, 0),
                                  ("rect_outline_1", 0, 1.5), ("rect_outline_1_round8", 4, 1.5)]:
        img, d = canvas(32, 32)
        r = radius * SS
        if outline:
            sw = outline * SS
            d.rounded_rectangle([sw / 2, sw / 2, 32 * SS - sw / 2 - 1, 32 * SS - sw / 2 - 1], radius=r,
                                outline=WHITE, width=int(sw))
        else:
            d.rounded_rectangle([0, 0, 32 * SS - 1, 32 * SS - 1], radius=r, fill=WHITE)
        save(down(img, 32, 32), f"common/{name}.png")
    # chip: 4px radius, 1.5px outline (codec chips, small tags) - 9-slice border 8
    img, d = canvas(24, 24)
    sw = 1.5 * SS
    d.rounded_rectangle([sw / 2, sw / 2, 24 * SS - sw / 2 - 1, 24 * SS - sw / 2 - 1], radius=4 * SS,
                        outline=WHITE, width=int(sw))
    save(down(img, 24, 24), "common/chip.png")
    img, d = canvas(24, 24)
    d.rounded_rectangle([0, 0, 24 * SS - 1, 24 * SS - 1], radius=4 * SS, fill=WHITE)
    save(down(img, 24, 24), "common/chip_fill.png")
    # pill (fully rounded ends), 9-slice border 24, height 48
    img, d = canvas(96, 48)
    d.rounded_rectangle([0, 0, 96 * SS - 1, 48 * SS - 1], radius=24 * SS, fill=WHITE)
    save(down(img, 96, 48), "common/pill_fill.png")
    img, d = canvas(96, 48)
    d.rounded_rectangle([sw / 2, sw / 2, 96 * SS - sw / 2 - 1, 48 * SS - sw / 2 - 1], radius=24 * SS,
                        outline=WHITE, width=int(sw))
    save(down(img, 96, 48), "common/pill_line.png")


def gradient_v(w, h, a0, a1, curve=1.0):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        a = a0 + (a1 - a0) * (t ** curve)
        for x in range(w):
            px[x, y] = (255, 255, 255, int(round(a * 255)))
    return img


def gradients():
    save(gradient_v(16, 256, 0, 1), "common/gradient_bottom.png")
    save(gradient_v(16, 256, 1, 0), "common/gradient_top.png")
    save(gradient_v(16, 256, 0, 1).rotate(90, expand=True), "common/gradient_right.png")
    save(gradient_v(16, 256, 0, 1).rotate(-90, expand=True), "common/gradient_left.png")
    save(gradient_v(16, 540, 0.2, 0.9, 1.6), "common/gradient_stage.png")
    # scrims (tint with "scrim" = ground colour)
    save(gradient_v(16, 512, 0, 0.92, 1.4), "common/scrim_bottom.png")
    # left scrim: info page "linear-gradient(90deg,.96 0%,.9 45%,.72 100%)" -> left opaque, right lighter
    w = 512
    img = Image.new("RGBA", (w, 16))
    px = img.load()
    for x in range(w):
        t = x / (w - 1)
        a = 0.96 + (0.90 - 0.96) * (t / 0.45) if t < 0.45 else 0.90 + (0.72 - 0.90) * ((t - 0.45) / 0.55)
        for y in range(16):
            px[x, y] = (255, 255, 255, int(a * 255))
    save(img, "common/scrim_info_h.png")
    # info vertical: .2 at top -> 0 at 30% -> .9 at bottom
    h = 512
    img = Image.new("RGBA", (16, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        a = 0.2 * (1 - t / 0.3) if t < 0.3 else 0.9 * ((t - 0.3) / 0.7)
        for x in range(16):
            px[x, y] = (255, 255, 255, int(a * 255))
    save(img, "common/scrim_info_v.png")
    # left-dark ramp used behind text columns over art (0.95 -> 0)
    img = Image.new("RGBA", (w, 16))
    px = img.load()
    for x in range(w):
        t = x / (w - 1)
        a = 0.95 * (1 - t) ** 1.3
        for y in range(16):
            px[x, y] = (255, 255, 255, int(a * 255))
    save(img, "common/scrim_left.png")
    # OSD right ramp: linear-gradient(90deg, 0 40%, .82 100%)
    img = Image.new("RGBA", (w, 16))
    px = img.load()
    for x in range(w):
        t = x / (w - 1)
        a = 0 if t < 0.4 else 0.82 * (t - 0.4) / 0.6
        for y in range(16):
            px[x, y] = (255, 255, 255, int(a * 255))
    save(img, "common/scrim_right.png")


def radial(size, stops, name, dither=True):
    """stops: list of (radius fraction 0..1, alpha 0..1) - white, tinted in XML."""
    import random
    rnd = random.Random(7)
    img = Image.new("RGBA", (size, size))
    px = img.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            r = math.hypot(x - c, y - c) / c
            a = stops[-1][1]
            for (r0, a0), (r1, a1) in zip(stops, stops[1:]):
                if r0 <= r <= r1:
                    t = (r - r0) / (r1 - r0) if r1 > r0 else 0
                    t = t * t * (3 - 2 * t)
                    a = a0 + (a1 - a0) * t
                    break
            v = a * 255 + (rnd.random() - 0.5 if dither else 0)
            px[x, y] = (255, 255, 255, max(0, min(255, int(round(v)))))
    save(img, name)


def radials():
    # Lift behind the lens: #121722 0 -> .55 at 360px -> 0 at 760px (draw 1520px wide, tint "lift")
    radial(256, [(0, 1.0), (360 / 760, 0.55), (1.0, 0.0)], "common/radial_lift.png")
    # OSD ring scrim: .94 0 -> .86 300 -> .45 560 -> 0 820 (draw 1640px wide, tint "scrim")
    radial(256, [(0, 0.94), (300 / 820, 0.86), (560 / 820, 0.45), (1.0, 0.0)], "common/radial_osd.png")
    # soft dark disc under round buttons / gauges over video
    radial(128, [(0, 0.85), (0.7, 0.6), (1.0, 0.0)], "common/radial_soft.png")


def shadow():
    # box-shadow 0 26px 60px rgba(0,0,0,.7) for posters: 9-slice, border 96, rect inset 96
    S = 288
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([96, 96, S - 97, S - 97], fill=(0, 0, 0, 180))
    img = img.filter(ImageFilter.GaussianBlur(30))
    save(img, "common/shadow_soft.png")
    round_shadows(img)


# 0.9.20: round art (artist discs, search artists) gets a round shadow. Diameters = the arc slots that carry a
# shadow (|k| <= 2) in Arc_LibrarySquares (libsq), Arc_Search9104 (homesq) and Arc_HorizonSquares (HORIZON_SQ);
# make_arc.py refuses to write a round shadow whose texture is missing here.
ROUND_SHADOW_D = (132, 148, 168, 176, 200, 210, 300, 330, 380)


def round_shadows(square):
    """Same box as the square 9-slice (art rect + 96 each side, drawn at left/right -96, top -70, bottom -122 =
    26 px lower), same falloff: the alpha at distance s from the box's outer edge is the square texture's
    mid-row alpha at column s (its edge profile), so softness, offset and opacity match; only the shape is a disc.
    Drawn at half size (the falloff is smooth) to keep Shield texture memory small."""
    prof = [square.getpixel((x, 144))[3] for x in range(145)]  # 0..144: edge -> centre (plateau beyond)

    def alpha(s):
        if s <= 0:
            return 0.0
        if s >= 144:
            return float(prof[144])
        i = int(s)
        f = s - i
        return prof[i] * (1 - f) + prof[i + 1] * f

    for d in ROUND_SHADOW_D:
        box = d + 192
        n = box // 2
        img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        px = img.load()
        c = box / 2
        for y in range(n):
            for x in range(n):
                r = math.hypot((x + 0.5) * 2 - c, (y + 0.5) * 2 - c)
                a = int(round(alpha(96 + d / 2 - r)))
                if a:
                    px[x, y] = (0, 0, 0, a)
        save(img, f"common/shadow_round_{d}.png")


# ------------------------------------------------------------------ focus
def brackets(size, arm, stroke, name, color=WHITE):
    img, d = canvas(size, size)
    s, a, w = size * SS, arm * SS, stroke * SS
    for (x0, y0, dx, dy) in [(0, 0, 1, 1), (s, 0, -1, 1), (0, s, 1, -1), (s, s, -1, -1)]:
        # horizontal arm
        xs = sorted([x0, x0 + dx * a])
        ys = sorted([y0, y0 + dy * w])
        d.rectangle([xs[0], ys[0], xs[1] - 1, ys[1] - 1], fill=color)
        xs = sorted([x0, x0 + dx * w])
        ys = sorted([y0, y0 + dy * a])
        d.rectangle([xs[0], ys[0], xs[1] - 1, ys[1] - 1], fill=color)
    save(down(img, size, size), name)


def focus():
    # Poster / tile focus: 4 corner brackets, 2px, 30px arms (mockup .bk), 9-slice border 32
    brackets(96, 30, 2, "focus/brackets.png")
    # small brackets for rows/chips: 16px arms, border 18
    brackets(48, 16, 2, "focus/brackets_s.png")
    # legacy names (Majan_FocusFrame used border 16): Orbit look = brackets with 16px arms
    brackets(40, 16, 2, "focus/outline_2.png")
    brackets(40, 16, 2, "focus/outline_2_round.png")
    brackets(40, 16, 3, "focus/outline_3.png")
    brackets(40, 16, 3, "focus/outline_3_round.png")
    # Row focus (lists, settings, dialogs): raised fill + 3px amber edge on the left. Own colours,
    # use WITHOUT colordiffuse. 9-slice border 8 (left column carries the amber edge).
    img = Image.new("RGBA", (32, 32), RAISED)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 2, 31], fill=AMBER)
    save(img, "focus/row.png")
    # same without the edge (inner focus inside grids / keyboard keys)
    save(Image.new("RGBA", (32, 32), RAISED), "focus/fill.png")
    # halo kept for legacy refs: soft dark glow behind focus
    img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([32, 32, 63, 63], fill=(255, 255, 255, 255))
    img = img.filter(ImageFilter.GaussianBlur(10))
    save(img, "focus/halo.png")


# ------------------------------------------------------------------ round buttons
def circle(size, fill=None, ring=None, ring_w=1.5, halo=None, name=None):
    """size = button diameter. halo: (gap, width) ring outside the disc (mockup Play focus)."""
    pad = 0
    if halo:
        pad = int(math.ceil(halo[0] + halo[1])) + 1
    full = size + 2 * pad
    img, d = canvas(full, full)
    c = full * SS / 2
    r = size * SS / 2
    if fill:
        d.ellipse([c - r, c - r, c + r, c + r], fill=fill)
    if ring:
        w = ring_w * SS
        d.ellipse([c - r + w / 2, c - r + w / 2, c + r - w / 2, c + r - w / 2], outline=ring, width=int(round(w)))
    if halo:
        gap, hw = halo
        r2 = r + (gap + hw / 2) * SS
        d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=WHITE, width=int(round(hw * SS)))
    save(down(img, full, full), name)
    return pad


def buttons():
    for s in (40, 48, 56, 64, 72, 84, 96, 108, 120):
        circle(s, fill=WHITE, name=f"btn/disc_{s}.png")
        circle(s, ring=WHITE, name=f"btn/ring_{s}.png")
        # halo ring: 8px gap, 1.5px ring -> texture is (s + 2*10) wide; place at -10
        circle(s, halo=(8, 1.5), name=f"btn/halo_{s}.png")


# ------------------------------------------------------------------ masks
def rounded_mask(w, h, r, name):
    img, d = canvas(w, h, 2)
    d.rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], radius=r * 2, fill=WHITE)
    save(down(img, w, h), name)


def masks():
    # Orbit poster radius: 4px at ~370px wide. Masks are stretched to the image rect.
    rounded_mask(400, 600, 4, "masks/poster_r4.png")
    rounded_mask(400, 400, 4, "masks/square_r4.png")
    rounded_mask(640, 360, 4, "masks/landscape_r4.png")
    # legacy names -> same 4px look
    rounded_mask(336, 504, 4, "masks/poster_round8.png")
    rounded_mask(660, 990, 4, "masks/poster_round8_large.png")
    rounded_mask(1040, 1560, 4, "masks/poster_round8_xl.png")
    rounded_mask(438, 438, 4, "masks/square_round8.png")
    rounded_mask(760, 760, 4, "masks/square_round8_large.png")
    rounded_mask(640, 360, 4, "masks/landscape_round8.png")
    rounded_mask(1920, 1080, 6, "masks/landscape_round8_large.png")
    rounded_mask(1120, 1120, 4, "music/square_round8_560.png")
    save(Image.new("RGBA", (4, 6), WHITE), "masks/poster_square.png")
    save(Image.new("RGBA", (4, 4), WHITE), "masks/square_square.png")
    save(Image.new("RGBA", (16, 9), WHITE), "masks/landscape_square.png")
    img, d = canvas(512, 512, 2)
    d.ellipse([0, 0, 1023, 1023], fill=WHITE)
    save(down(img, 512, 512), "masks/circle.png")


# ------------------------------------------------------------------ icons (24-unit grid)
class Icon:
    def __init__(self, px=96):
        self.px = px
        self.k = px * SS / 24.0
        self.img = Image.new("RGBA", (px * SS, px * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def line(self, pts, w=1.8):
        pts = self.P(pts)
        width = max(1, int(round(w * self.k)))
        self.d.line(pts, fill=WHITE, width=width, joint="curve")
        r = width / 2
        for (x, y) in (pts[0], pts[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE)

    def poly(self, pts):
        self.d.polygon(self.P(pts), fill=WHITE)

    def rect(self, x, y, w, h, fill=True, sw=1.8, r=0):
        box = [x * self.k, y * self.k, (x + w) * self.k, (y + h) * self.k]
        if fill:
            self.d.rounded_rectangle(box, radius=r * self.k, fill=WHITE)
        else:
            self.d.rounded_rectangle(box, radius=r * self.k, outline=WHITE, width=int(round(sw * self.k)))

    def circle(self, cx, cy, r, fill=False, sw=1.8):
        box = [(cx - r) * self.k, (cy - r) * self.k, (cx + r) * self.k, (cy + r) * self.k]
        if fill:
            self.d.ellipse(box, fill=WHITE)
        else:
            self.d.ellipse(box, outline=WHITE, width=int(round(sw * self.k)))

    def arc(self, cx, cy, r, a0, a1, sw=1.8):
        box = [(cx - r) * self.k, (cy - r) * self.k, (cx + r) * self.k, (cy + r) * self.k]
        self.d.arc(box, a0, a1, fill=WHITE, width=int(round(sw * self.k)))

    def save(self, name):
        save(down(self.img, self.px, self.px), f"icons/{name}.png")


def icons():
    I = Icon(); I.poly([(8, 5.5), (19, 12), (8, 18.5)]); I.save("play")
    I = Icon(); I.rect(6, 5, 4, 14); I.rect(14, 5, 4, 14); I.save("pause")
    I = Icon(); I.rect(6, 6, 12, 12, r=1); I.save("stop")
    I = Icon(); I.line([(6, 5), (6, 19)]); I.poly([(19, 5.5), (9, 12), (19, 18.5)]); I.save("prev")
    I = Icon(); I.line([(18, 5), (18, 19)]); I.poly([(5, 5.5), (15, 12), (5, 18.5)]); I.save("next")
    I = Icon(); I.poly([(12, 6), (4, 12), (12, 18)]); I.poly([(21, 6), (13, 12), (21, 18)]); I.save("rewind")
    I = Icon(); I.poly([(3, 6), (11, 12), (3, 18)]); I.poly([(12, 6), (20, 12), (12, 18)]); I.save("forward")
    I = Icon(); I.line([(5, 12.5), (9.5, 17), (19, 7.5)]); I.save("check")
    I = Icon(); I.circle(9, 12, 5.5); I.circle(15, 12, 5.5); I.save("similar")
    I = Icon()
    for x in (5.5, 12, 18.5):
        I.circle(x, 12, 1.4, fill=True)
    I.save("more")
    I = Icon(); I.rect(3, 5, 18, 14, fill=False, r=2); I.line([(7, 13), (11, 13)]); I.line([(13.5, 13), (17, 13)])
    I.line([(7, 16), (15, 16)]); I.save("subtitles")
    I = Icon(); I.poly([(4, 9.5), (8, 9.5), (13, 5.5), (13, 18.5), (8, 14.5), (4, 14.5)])
    I.arc(13, 12, 4, -50, 50); I.arc(13, 12, 7.5, -50, 50); I.save("audio")
    # settings = an Orbit knob: ring + pointer tick + centre
    I = Icon(); I.circle(12, 12, 8); I.line([(12, 4.8), (12, 9)]); I.circle(12, 12, 1.4, fill=True); I.save("settings")
    I = Icon(); I.circle(12, 12, 8); I.line([(12, 4.8), (12, 9)]); I.circle(12, 12, 1.4, fill=True); I.save("knob")
    # kodi settings = three sliders
    I = Icon()
    for y, x in ((6.5, 15), (12, 8), (17.5, 13)):
        I.line([(4, y), (20, y)], 1.5); I.circle(x, y, 2.2, fill=True)
    I.save("sliders")
    I = Icon(); I.circle(12, 12, 8.5); I.line([(12, 11), (12, 16.5)]); I.circle(12, 7.9, 1.2, fill=True); I.save("info")
    I = Icon(); I.circle(10.5, 10.5, 6); I.line([(15, 15), (20, 20)]); I.save("search")
    I = Icon(); I.line([(14.5, 6), (8.5, 12), (14.5, 18)]); I.save("back")
    I = Icon(); I.line([(9.5, 6), (15.5, 12), (9.5, 18)]); I.save("chevron_right")
    I = Icon(); I.line([(6, 9.5), (12, 15.5), (18, 9.5)]); I.save("chevron_down")
    I = Icon(); I.line([(6, 14.5), (12, 8.5), (18, 14.5)]); I.save("chevron_up")
    I = Icon()
    I.line([(4, 11), (4, 9), (6, 7), (18, 7)]); I.line([(15.5, 4.5), (18, 7), (15.5, 9.5)])
    I.line([(20, 13), (20, 15), (18, 17), (6, 17)]); I.line([(8.5, 14.5), (6, 17), (8.5, 19.5)]); I.save("repeat")
    I = Icon()
    I.line([(4, 7), (8, 7), (16, 17), (20, 17)]); I.line([(4, 17), (8, 17), (16, 7), (20, 7)])
    I.line([(17.5, 4.5), (20, 7), (17.5, 9.5)]); I.line([(17.5, 14.5), (20, 17), (17.5, 19.5)]); I.save("shuffle")
    I = Icon()
    for y in (7, 12, 17):
        I.circle(5, y, 1.3, fill=True); I.line([(9, y), (20, y)])
    I.save("chapters")
    I = Icon(); I.line([(7, 4), (17, 4), (17, 20), (12, 16), (7, 20), (7, 4)]); I.save("bookmark")
    I = Icon(); I.rect(3, 6, 18, 12, fill=False, r=2); I.poly([(10, 9), (15, 12), (10, 15)]); I.save("trailer")
    I = Icon(); I.arc(12, 13, 7.5, -50, 230); I.line([(12, 3.5), (12, 11)]); I.save("power")
    I = Icon(); I.line([(3, 7), (3, 19), (21, 19), (21, 8.5), (11, 8.5), (9, 6), (3, 6), (3, 7)]); I.save("folder")
    I = Icon()
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 8.5 if i % 2 == 0 else 3.8
        pts.append((12 + r * math.cos(a), 12.5 + r * math.sin(a)))
    pts.append(pts[0]); I.line(pts, 1.6); I.save("star")
    I = Icon()
    for (x, y) in ((4, 4), (13.5, 4), (4, 13.5), (13.5, 13.5)):
        I.rect(x, y, 6.5, 6.5, fill=False, r=1.2)
    I.save("grid")
    I = Icon(); I.line([(12, 5), (12, 19)]); I.line([(5, 12), (19, 12)]); I.save("plus")
    I = Icon(); I.line([(5, 12), (19, 12)]); I.save("minus")
    I = Icon(); I.line([(6, 6), (18, 18)]); I.line([(18, 6), (6, 18)]); I.save("close")
    I = Icon(); I.circle(12, 8.5, 3.8); I.arc(12, 21, 7.5, 200, 340); I.save("person")
    I = Icon(); I.line([(9, 17), (9, 5), (19, 3), (19, 15)]); I.circle(6.8, 17, 2.4, fill=True); I.circle(16.8, 15, 2.4, fill=True); I.save("music")
    I = Icon(); I.rect(3, 5, 18, 14, fill=False, r=2)
    for x in (7, 12, 17):
        I.line([(x, 5), (x, 8)], 1.4); I.line([(x, 16), (x, 19)], 1.4)
    I.save("movies")
    I = Icon(); I.rect(3, 6, 18, 12, fill=False, r=2); I.line([(9, 21), (15, 21)]); I.line([(8, 3), (12, 6), (16, 3)], 1.5); I.save("tv")
    I = Icon(); I.circle(12, 12, 8.5); I.circle(12, 12, 3); I.circle(12, 12, 0.9, fill=True); I.save("disc")
    I = Icon(); I.rect(3, 5, 18, 14, fill=False, r=2); I.circle(9, 10, 1.8); I.line([(4, 17), (10, 12), (14, 15), (17, 12), (20, 15)], 1.5); I.save("pictures")
    I = Icon(); I.rect(4, 8, 16, 10, fill=False, r=3); I.line([(8, 13), (10, 13)], 1.5); I.line([(9, 12), (9, 14)], 1.5); I.circle(15, 12, 0.9, fill=True); I.circle(16.5, 14, 0.9, fill=True); I.save("games")
    I = Icon(); I.circle(12, 12, 8.5); I.line([(12, 7), (12, 12), (15.5, 14)]); I.save("clock")
    I = Icon()
    for y in (6, 10, 14, 18):
        I.line([(5, y), (19, y)], 1.5)
    I.save("list")
    I = Icon(); I.line([(4, 12), (20, 12)]); I.line([(14, 6), (20, 12), (14, 18)]); I.save("arrow_right")
    I = Icon(); I.circle(12, 12, 8.5); I.circle(12, 12, 4.5); I.line([(12, 3.5), (12, 6.5)], 1.5); I.save("arc")
    I = Icon(); I.line([(4, 18), (4, 6)], 1.5); I.circle(12, 12, 1.4, fill=True); I.line([(20, 18), (20, 6)], 1.5); I.save("zoom")
    I = Icon(); I.line([(12, 4), (12, 15)]); I.line([(7, 10), (12, 15), (17, 10)]); I.line([(5, 19), (19, 19)]); I.save("download")
    I = Icon(); I.line([(4.5, 12), (9.5, 12), (12, 6), (15, 18), (17.5, 12), (19.5, 12)], 1.6); I.save("pulse")
    # visualiser presets (0.9.11) = a waveform inside an Orbit dial ring
    I = Icon(); I.circle(12, 12, 8.5); I.line([(6.5, 12), (8.5, 12), (10, 8.5), (12, 15.5), (14, 9.5), (15.5, 12), (17.5, 12)], 1.5); I.save("presets")
    I = Icon(); I.circle(12, 12, 8.5); I.line([(8.5, 8.5), (15.5, 15.5)]); I.save("blocked")
    I = Icon(); I.rect(5, 4, 14, 16, fill=False, r=2); I.line([(9, 9), (15, 9)], 1.5); I.line([(9, 13), (15, 13)], 1.5); I.save("doc")
    I = Icon(); I.circle(12, 12, 8.5); I.line([(8, 12), (16, 12)]); I.line([(12, 8), (12, 16)]); I.save("addcircle")
    I = Icon(); I.line([(4, 15), (12, 7), (20, 15)]); I.save("up")
    I = Icon(); I.arc(12, 12, 7.5, 20, 300); I.line([(19.3, 4.8), (19.3, 9.6), (14.5, 9.6)]); I.save("refresh")
    I = Icon()
    I.line([(12, 3), (20, 7.5), (20, 16.5), (12, 21), (4, 16.5), (4, 7.5), (12, 3)], 1.6)
    I.save("addons")
    I = Icon(); I.circle(12, 12, 4.2)
    for i in range(8):
        a = i * math.pi / 4
        I.line([(12 + 7 * math.cos(a), 12 + 7 * math.sin(a)), (12 + 9.5 * math.cos(a), 12 + 9.5 * math.sin(a))], 1.6)
    I.save("weather")
    I = Icon(); I.circle(12, 12, 8.5); I.line([(12, 6), (12, 12)]); I.line([(12, 12), (8, 15)]); I.save("dial")
    I = Icon(); I.rect(4, 4, 16, 16, fill=False, r=3); I.circle(12, 12, 3.2); I.save("record")
    I = Icon(); I.line([(8, 6), (8, 18)]); I.line([(16, 6), (16, 18)]); I.line([(4, 10), (20, 10)], 1.4); I.line([(4, 14), (20, 14)], 1.4); I.save("pvr")


# ------------------------------------------------------------------ markers
def markers():
    # watched badge: dark disc + check (mockup .wt: 30px, rgba(7,9,13,.82)), own colours
    S = 30
    img, d = canvas(S, S)
    d.ellipse([0, 0, S * SS - 1, S * SS - 1], fill=(6, 11, 28, 210))
    k = SS * S / 30
    pts = [(9.4 * k, 15.6 * k), (13.4 * k, 19.6 * k), (21 * k, 11.4 * k)]
    d.line(pts, fill=TEXT, width=int(2.2 * k), joint="curve")
    save(down(img, S, S), "markers/watched_badge.png")
    # unwatched pip: amber dot 12px (own colour)
    img, d = canvas(12, 12)
    d.ellipse([0, 0, 12 * SS - 1, 12 * SS - 1], fill=AMBER)
    save(down(img, 12, 12), "markers/unwatched_pip.png")
    # legacy names
    save(down(img, 12, 12).resize((24, 24), Image.LANCZOS), "markers/unwatched.png")
    save(down(img, 12, 12).resize((24, 24), Image.LANCZOS), "markers/unwatched_round.png")
    img2, d2 = canvas(44, 44)
    d2.ellipse([0, 0, 44 * SS - 1, 44 * SS - 1], fill=(6, 11, 28, 210))
    k = SS * 44 / 30
    d2.line([(9.4 * k, 15.6 * k), (13.4 * k, 19.6 * k), (21 * k, 11.4 * k)], fill=TEXT, width=int(2.2 * k), joint="curve")
    save(down(img2, 44, 44), "markers/watched.png")
    save(down(img2, 44, 44), "markers/watched_round.png")
    I = Icon(48); I.line([(5, 12.5), (9.5, 17), (19, 7.5)], 2.4); save(down(I.img, 48, 48), "markers/check.png")


# ------------------------------------------------------------------ misc (Kodi-owned windows)
def misc():
    # calibration: crosshair rings in Orbit style
    for name, size in (("cal_tl", 256), ("cal_br", 256)):
        img, d = canvas(size, size)
        w = 2 * SS
        s = size * SS
        d.line([(0, w / 2), (s * 0.6, w / 2)], fill=WHITE, width=w)
        d.line([(w / 2, 0), (w / 2, s * 0.6)], fill=WHITE, width=w)
        d.ellipse([s * 0.12, s * 0.12, s * 0.44, s * 0.44], outline=WHITE, width=w)
        img = down(img, size, size)
        if name == "cal_br":
            img = img.rotate(180)
        save(img, f"misc/{name}.png")
    img, d = canvas(500, 500)
    d.ellipse([SS * 4, SS * 4, 500 * SS - SS * 4, 500 * SS - SS * 4], outline=WHITE, width=3 * SS)
    d.ellipse([500 * SS / 2 - 12 * SS, 500 * SS / 2 - 12 * SS, 500 * SS / 2 + 12 * SS, 500 * SS / 2 + 12 * SS], fill=WHITE)
    save(down(img, 500, 500), "misc/cal_ratio.png")
    img, d = canvas(200, 200)
    d.ellipse([SS * 4, SS * 4, 200 * SS - SS * 4, 200 * SS - SS * 4], outline=WHITE, width=3 * SS)
    d.line([(100 * SS, 30 * SS), (100 * SS, 100 * SS)], fill=WHITE, width=3 * SS)
    save(down(img, 200, 200), "misc/cal_reset.png")
    img, d = canvas(760, 180)
    d.rounded_rectangle([0, 0, 760 * SS - 1, 180 * SS - 1], radius=8 * SS, outline=WHITE, width=2 * SS)
    save(down(img, 760, 180), "misc/cal_sub.png")
    img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([6, 0, 7, 7], fill=WHITE)
    save(img, "misc/epg_now.png")


def vinyl():
    """Record for the music 'record dial': grooved disc, transparent label hole (album art goes
    under it, circle-masked), thin amber label ring. Own colours."""
    S = 480
    img, d = canvas(S, S, 2)
    c = S  # centre in 2x space
    R = S - 2
    d.ellipse([c - R, c - R, c + R, c + R], fill=(10, 12, 16, 255))
    import random
    rnd = random.Random(3)
    r = R - 6
    while r > S * 0.36:
        shade = 22 + rnd.randint(-5, 9)
        d.ellipse([c - r, c - r, c + r, c + r], outline=(shade, shade + 3, shade + 9, 255), width=1)
        r -= 3 + rnd.random() * 2.5
    d.ellipse([c - R, c - R, c + R, c + R], outline=(43, 50, 64, 255), width=3)
    lr = S * 0.32
    d.ellipse([c - lr - 4, c - lr - 4, c + lr + 4, c + lr + 4], outline=AMBER, width=3)
    d.ellipse([c - lr, c - lr, c + lr, c + lr], fill=(0, 0, 0, 0))
    save(down(img, S, S), "music/vinyl.png")
    # spindle
    img, d = canvas(24, 24)
    d.ellipse([0, 0, 24 * SS - 1, 24 * SS - 1], fill=GROUND)
    d.ellipse([3 * SS, 3 * SS, 21 * SS, 21 * SS], outline=(139, 149, 167, 255), width=int(1.5 * SS))
    save(down(img, 24, 24), "music/spindle.png")


PANEL = (13, 21, 41, 255)
BORDER = (58, 66, 82, 255)
INK = (7, 9, 13, 255)
AMBER_C = (255, 181, 71, 255)


def icon_image(name, px):
    """Load a generated white icon and resize it to px."""
    im = Image.open(MEDIA / "icons" / f"{name}.png").convert("RGBA")
    return im.resize((px, px), Image.LANCZOS)


def tint(im, color):
    r, g, b, a = color
    out = Image.new("RGBA", im.size, (r, g, b, 0))
    alpha = im.split()[3]
    out.putalpha(alpha.point(lambda v: v * a // 255))
    return out


def round_button(S, icon, state, label_h=0, icon_px=None, width=None):
    """One pre-rendered round button: disc + icon (+ halo when focused), coloured.
    Canvas = (S + 24) wide, (S + 24 + label_h) tall; disc centred in the top square."""
    pad = 12
    Wd = S + 2 * pad              # disc square
    W = width or Wd
    H = Wd + label_h
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W * SS / 2
    cy = Wd * SS / 2
    c = cx
    r = S * SS / 2
    light = state in ("f", "p")
    if light:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEXT)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PANEL)
        w = 1.5 * SS
        d.ellipse([cx - r + w / 2, cy - r + w / 2, cx + r - w / 2, cy + r - w / 2], outline=BORDER, width=int(round(w)))
    if state == "f":
        r2 = r + 9.25 * SS
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=TEXT, width=int(round(1.5 * SS)))
    img = img.resize((W, H), Image.LANCZOS)
    if icon is None:
        return img
    ip = icon_px or round(S * 0.36)
    ic = icon_image(icon, ip)
    col = INK if light else (AMBER_C if state == "s" else TEXT)
    ic = tint(ic, col)
    img.alpha_composite(ic, (W // 2 - ip // 2, Wd // 2 - ip // 2))
    return img


def round_buttons():
    """Sizes / icons used by the info page (96, labelled), OSD (84 play, 64 transport, 56 tools)."""
    sets = [
        (96, 44, ["play", "prev", "arrow_right", "trailer", "similar", "more", "check", "search", "folder", "music", "info",
                  "shuffle", "person", "disc", "refresh"], ("n", "f", "p")),
        (84, 0, ["play", "pause"], ("n", "f", "p")),
        (64, 0, ["prev", "next", "rewind", "forward", "stop"], ("n", "f")),
        (56, 0, ["subtitles", "audio", "sliders", "chapters", "info", "pulse", "stop", "repeat", "shuffle",
                 "bookmark", "settings", "close", "list", "music", "disc", "zoom", "power", "presets"], ("n", "f", "s")),
    ]
    n = 0
    # blank discs (icon drawn by an image control: the play/pause icon changes with the state,
    # and button textures can't take $VAR/$INFO)
    for st in ("n", "f", "p"):
        save(round_button(84, None, st), f"btn/r84/blank_{st}.png")
    for S, label_h, icons, states in sets:
        for icon in icons:
            for st in states:
                save(round_button(S, icon, st, label_h, width=150 if S == 96 else None), f"btn/r{S}/{icon}_{st}.png")
                n += 1
    return n


def legacy():
    """Names still referenced by Majan-derived windows, redrawn in the Orbit language."""
    # panel_framed (border 2): ground-raised fill with a 1px line frame + buffer
    img = Image.new("RGBA", (32, 32), PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 31], outline=(43, 50, 64, 255))
    save(img, "dialogs/panel_framed.png")
    img = Image.new("RGBA", (4, 8), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([0, 7, 3, 7], fill=WHITE)
    save(img, "dialogs/row_rule.png")
    img = Image.new("RGBA", (8, 80), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([0, 74, 7, 76], fill=WHITE)
    save(img, "vidview/underline.png")
    save(Image.new("RGBA", (8, 8), (0, 0, 0, 120)), "vidview/dim_ahead.png")
    save(Image.new("RGBA", (8, 8), (0, 0, 0, 160)), "vidview/dim_passed.png")
    img = Image.new("RGBA", (8, 12), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([0, 8, 7, 10], fill=WHITE)
    save(img, "music/tab_underline.png")
    # OSD slider pieces
    img, d = canvas(16, 32)
    d.rectangle([0, 15 * SS, 16 * SS, 17 * SS], fill=WHITE)
    save(down(img, 16, 32), "osd/slider_bg.png")
    img, d = canvas(64, 32)
    d.ellipse([24 * SS, 8 * SS, 40 * SS, 24 * SS], fill=WHITE)
    save(down(img, 64, 32), "osd/slider_nib.png")
    img = Image.new("RGBA", (2, 32), WHITE)
    save(img, "osd/tick.png")
    img = Image.new("RGBA", (480, 270))
    px = img.load()
    for y in range(270):
        for x in range(480):
            r = math.hypot(x / 480, (270 - y) / 270)
            a = max(0.0, 1 - r) ** 1.5 * 0.9
            px[x, y] = (255, 255, 255, int(a * 255))
    save(img, "osd/scrim_corner_bl.png")


def main():
    if MEDIA.exists():
        # keep the ring frame sets (make_rings.py) if present; views/ is rebuilt below
        for sub in MEDIA.iterdir():
            if sub.name not in ("rings", "ground", "views"):
                shutil.rmtree(sub) if sub.is_dir() else sub.unlink()
    basics()
    gradients()
    radials()
    shadow()
    focus()
    buttons()
    masks()
    icons()
    markers()
    misc()
    vinyl()
    round_buttons()
    legacy()
    import make_ground  # deep-blue full-screen grounds (media/ground/)
    make_ground.main()
    import make_view_previews  # schematic view-picker previews (media/views/, needs rings + ground)
    make_view_previews.main()
    n = sum(1 for _ in MEDIA.rglob("*.png") if "rings" not in _.parts)
    print(f"wrote {n} textures to {MEDIA}")


if __name__ == "__main__":
    main()
