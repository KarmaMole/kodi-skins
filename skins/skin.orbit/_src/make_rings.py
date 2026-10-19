"""Generate Orbit's ring instruments: static dials + frame sets indexed by infolabels.

Kodi has no arc control, but an image control loads whatever file an infolabel names,
so every dynamic ring is a pre-rendered frame set:

  rings/rating_<S>/<v>.png    v = 0.0 ... 10.0 (step 0.1, 101 frames)
        ListItem.Rating is StringUtils::FormatNumber(float) = fixed, precision 1 -> "7.6",
        "10.0", "8.0" (Kodi 21 VideoGUIInfo.cpp). Empty when the rating is 0 -> XML falls
        back to 0.0.png via fallback="" and hides the readout.
  rings/progress_<S>/<n>.png  n = 0 ... 100 (101 frames)
        Player.Progress = std::to_string(lrintf(percentage)) (PlayerGUIInfo.cpp) and
        ListItem.PercentPlayed are integers.
  rings/runtime_<S>/<m>.png   m = 0 ... 240 minutes (241 frames)
        ListItem.Duration(mins) = lrintf(seconds / 60) (StringUtils::SecondsToTimeString,
        TIME_FORMAT_MINS). Longer films fall back to 240.png. The sector starts at 12 o'clock
        and covers m/720 of the 12-hour face; XML rotates it to the current time.
  rings/osd/<n>.png           640px OSD scrubber progress (sweep + nib), n = 0 ... 100

  Sizes S: 180 (Home), 200 (library arc), 260 (info page).

Static faces (white/grey baked colours, used without colordiffuse):
  rings/dial_rating_<S>.png   60 minor + 12 major engraved ticks, track circle, "0"/"5"
  rings/dial_progress_<S>.png ... "0"/"25"/"50"/"75"
  rings/dial_clock_<S>.png    ... "12"/"3"/"6"/"9"
  rings/hand_<S>.png          now-hand + hub pointing to 12 (rotated in XML)
  rings/osd_face.png          640px OSD face
  rings/home_dial.png         Home section ring (centre 200,540 in screen space)
  rings/home_arc.png          Home arc track (centre 2100,540, r 1290 / 900)
  rings/lib_arc.png           Library arc track (centre 2400,540, r 800 / 1300)

Geometry is scaled from the mockups (OrbitHome/Arc/Info/OSD.dc.html), 260px gauge:
ticks r 118-128, track r 99, sweep 4px, needle r 89-109, numerals r 78.

Usage: python skins/skin.orbit/_src/make_rings.py
"""
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media" / "rings"
FONT = HERE.parent / "fonts" / "OrbitMono-Regular.ttf"
SS = 4

AMBER = (255, 181, 71, 255)
AMBER_FILL = (255, 181, 71, 33)  # rgba(255,181,71,.13)
LINE = (43, 50, 64, 255)          # #2B3240
LINE2 = (58, 66, 82, 255)         # #3A4252
TICK = (86, 96, 117, 255)         # #566075
TICK_OSD = (122, 132, 150, 255)   # #7A8496
SECOND = (139, 149, 167, 255)     # #8B95A7
TEXT = (233, 237, 243, 255)
GROUND = (7, 9, 13, 255)
FAINT = (28, 34, 45, 255)         # #1C222D
FAINTER = (22, 27, 37, 255)       # #161B25


def save(img, rel):
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def pol(cx, cy, r, deg):
    """deg clockwise from 12 o'clock"""
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def ticks(d, cx, cy, r_in, r_out, n, width, color, offset_deg=0.0):
    for i in range(n):
        deg = offset_deg + i * 360.0 / n
        x0, y0 = pol(cx, cy, r_in, deg)
        x1, y1 = pol(cx, cy, r_out, deg)
        d.line([(x0, y0), (x1, y1)], fill=color, width=max(1, int(round(width))))


def ring(d, cx, cy, r, width, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=max(1, int(round(width))))


def arc(d, cx, cy, r, deg0, deg1, width, color):
    # PIL: 0 = 3 o'clock, clockwise
    if deg1 - deg0 <= 0.01:
        return
    d.arc([cx - r, cy - r, cx + r, cy + r], deg0 - 90, deg1 - 90, fill=color, width=max(1, int(round(width))))


def font(px):
    return ImageFont.truetype(str(FONT), int(px))


def text_c(d, x, y, s, px, color):
    f = font(px)
    d.text((x, y), s, font=f, fill=color, anchor="mm")


class Gauge:
    def __init__(self, S):
        self.S = S
        k = S / 260.0
        self.k = k
        self.c = S * SS / 2
        self.r_tick_out = 128 * k * SS
        self.r_minor_in = 118 * k * SS
        self.r_major_in = 108 * k * SS
        self.r_track = 99 * k * SS
        self.sweep_w = 4 * SS * max(0.85, k)  # keep the sweep ~4px even on smaller gauges
        self.needle = (89 * k * SS, 109 * k * SS)
        self.r_num = 78 * k * SS
        self.num_px = 20 * SS * (1.0 if S >= 200 else 0.95)

    def blank(self):
        img = Image.new("RGBA", (self.S * SS, self.S * SS), (0, 0, 0, 0))
        return img, ImageDraw.Draw(img)

    def out(self, img):
        return img.resize((self.S, self.S), Image.LANCZOS)

    def face(self, labels):
        img, d = self.blank()
        c = self.c
        ticks(d, c, c, self.r_minor_in, self.r_tick_out, 60, 1.5 * SS, LINE)
        ticks(d, c, c, self.r_major_in, self.r_tick_out, 12, 1.5 * SS, TICK)
        ring(d, c, c, self.r_track, 1.5 * SS, LINE)
        for deg, s in labels:
            x, y = pol(c, c, self.r_num, deg)
            text_c(d, x, y, s, self.num_px, SECOND)
        return self.out(img)

    def sweep(self, frac, fill_sector=False, needle_color=AMBER):
        img, d = self.blank()
        c = self.c
        deg = 360.0 * frac
        if fill_sector and deg > 0.01:
            d.pieslice([c - self.r_track, c - self.r_track, c + self.r_track, c + self.r_track],
                       -90, deg - 90, fill=AMBER_FILL)
        arc(d, c, c, self.r_track, 0, deg, self.sweep_w, AMBER)
        x0, y0 = pol(c, c, self.needle[0], deg)
        x1, y1 = pol(c, c, self.needle[1], deg)
        d.line([(x0, y0), (x1, y1)], fill=needle_color, width=int(2 * SS))
        return self.out(img)

    def hand(self):
        img, d = self.blank()
        c = self.c
        x, y = pol(c, c, self.r_track - 6 * self.k * SS, 0)
        d.line([(c, c), (x, y)], fill=TEXT, width=int(2 * SS))
        r = 4.5 * SS
        d.ellipse([c - r, c - r, c + r, c + r], fill=GROUND, outline=TEXT, width=int(1.5 * SS))
        return self.out(img)


def gauges():
    for S in (180, 200, 260):
        g = Gauge(S)
        save(g.face([(0, "0"), (180, "5")]), f"dial_rating_{S}.png")
        save(g.face([(0, "0"), (90, "25"), (180, "50"), (270, "75")]), f"dial_progress_{S}.png")
        # clock numerals sit a little further out (mockup r 75 on the 260 face)
        g2 = Gauge(S)
        g2.r_num = 75 * g2.k * SS
        save(g2.face([(0, "12"), (90, "3"), (180, "6"), (270, "9")]), f"dial_clock_{S}.png")
        save(g.hand(), f"hand_{S}.png")
        save(g.face([]), f"dial_ticks_{S}.png")  # ticks + track, no numerals (time readouts inside)
        # minimal ring style: bare track (+ quarter ticks for the clock)
        img, d = g.blank()
        ring(d, g.c, g.c, g.r_track, 1.5 * SS, LINE)
        save(g.out(img), f"dial_min_{S}.png")
        img, d = g.blank()
        ring(d, g.c, g.c, g.r_track, 1.5 * SS, LINE)
        ticks(d, g.c, g.c, g.r_track + 6 * g.k * SS, g.r_track + 18 * g.k * SS, 4, 1.5 * SS, TICK)
        save(g.out(img), f"dial_minclock_{S}.png")
        for i in range(101):
            v = i / 10.0
            save(g.sweep(v / 10.0), f"rating_{S}/{v:.1f}.png")
        for n in range(101):
            save(g.sweep(n / 100.0), f"progress_{S}/{n}.png")
        for m in range(241):
            save(g.sweep(m / 720.0, fill_sector=True), f"runtime_{S}/{m}.png")
        print(f"gauge {S}: faces + 101 rating + 101 progress + 241 runtime frames")


def osd():
    S = 640
    c = S * SS / 2
    img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ticks(d, c, c, 272 * SS, 282 * SS, 60, 1.5 * SS, LINE2)
    ticks(d, c, c, 260 * SS, 282 * SS, 12, 2 * SS, TICK_OSD)
    ring(d, c, c, 196 * SS, 1.5 * SS, LINE)
    ring(d, c, c, 230 * SS, 1.5 * SS, LINE2)
    save(img.resize((S, S), Image.LANCZOS), "osd_face.png")
    for n in range(101):
        img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        deg = 3.6 * n
        arc(d, c, c, 230 * SS, 0, deg, 6 * SS, AMBER)
        x, y = pol(c, c, 230 * SS, deg)
        r = 11 * SS
        d.ellipse([x - r - 4 * SS, y - r - 4 * SS, x + r + 4 * SS, y + r + 4 * SS], fill=GROUND)
        d.ellipse([x - r, y - r, x + r, y + r], fill=AMBER)
        save(img.resize((S, S), Image.LANCZOS), f"osd/{n}.png")
    print("osd: face + 101 frames")


def screen_piece(x0, y0, w, h, draw_fn, name, ss=2):
    """Draw in screen coordinates (1920x1080 space) and crop to (x0,y0,w,h)."""
    img = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def T(x, y):
        return (x - x0) * ss, (y - y0) * ss

    draw_fn(d, T, ss)
    save(img.resize((w, h), Image.LANCZOS), name)


def home_dial():
    # Home section ring: centre (200,540), mockup OrbitHome.dc.html
    def fn(d, T, ss):
        cx, cy = T(200, 540)
        ticks(d, cx, cy, 240 * ss, 250 * ss, 60, 1.5 * ss, LINE)
        ticks(d, cx, cy, 230 * ss, 250 * ss, 12, 1.5 * ss, TICK)
        ring(d, cx, cy, 250 * ss, 1.5 * ss, LINE)
        ring(d, cx, cy, 196 * ss, 1.5 * ss, LINE)
        # amber lens marker at 3 o'clock (x 422..478)
        x0, y = T(422, 540)
        x1, _ = T(478, 540)
        d.line([(x0, y), (x1, y)], fill=AMBER, width=3 * ss)
        # station dots at +-32, +-64 deg on r 250
        for a in (-64, -32, 32, 64):
            px, py = pol(cx, cy, 250 * ss, 90 + a)
            r = 5 * ss
            d.ellipse([px - r, py - r, px + r, py + r], fill=GROUND, outline=SECOND, width=int(1.5 * ss))
        for deg, s in ((0, "00"), (180, "30"), (270, "45")):
            px, py = pol(cx, cy, 172 * ss, deg)
            d.text((px, py), s, font=font(20 * ss), fill=TICK, anchor="mm")
    screen_piece(0, 280, 470, 520, fn, "home_dial.png")


def home_arc():
    # 0.9.1 geometry: posters on r 880 about (1880,540); engraved track r 1070 (outside the posters),
    # faint inner ring r 680; amber lens marker on the track at 3 o'clock of the lens
    def fn(d, T, ss):
        cx, cy = T(1880, 540)
        ring(d, cx, cy, 1070 * ss, 1.5 * ss, LINE)
        ticks(d, cx, cy, 1082 * ss, 1090 * ss, 360, 1.5 * ss, LINE)
        ticks(d, cx, cy, 1072 * ss, 1090 * ss, 72, 1.5 * ss, TICK)
        ring(d, cx, cy, 680 * ss, 1.5 * ss, FAINT)
        x0, y = T(800, 540)
        x1, _ = T(834, 540)
        d.line([(x0, y), (x1, y)], fill=AMBER, width=3 * ss)
    screen_piece(760, 0, 1160, 1080, fn, "home_arc.png", ss=2)


def lib_arc():
    # 0.9.1 geometry: posters on r 880 about (2180,540); inner engraved ring r 580, faint ring r 1080
    def fn(d, T, ss):
        cx, cy = T(2180, 540)
        ring(d, cx, cy, 580 * ss, 1.5 * ss, LINE)
        ticks(d, cx, cy, 571 * ss, 580 * ss, 180, 1.5 * ss, LINE, offset_deg=0.4)
        ticks(d, cx, cy, 562 * ss, 580 * ss, 36, 1.5 * ss, TICK, offset_deg=2.4)
        ring(d, cx, cy, 1080 * ss, 1.5 * ss, FAINTER)
        x0, y = T(1576, 540)
        x1, _ = T(1624, 540)
        d.line([(x0, y), (x1, y)], fill=AMBER, width=3 * ss)
    screen_piece(1090, 0, 830, 1080, fn, "lib_arc.png", ss=2)


def dial_list():
    # guide arc for the dial list (rows on a circle centred (-760,540), text starts at r 960)
    def fn(d, T, ss):
        cx, cy = T(-760, 540)
        ring(d, cx, cy, 890 * ss, 1.5 * ss, LINE)
        ticks(d, cx, cy, 892 * ss, 902 * ss, 360, 1.2 * ss, LINE)
        ticks(d, cx, cy, 892 * ss, 912 * ss, 72, 1.5 * ss, TICK)
    screen_piece(0, 0, 320, 1080, fn, "dial_list.png", ss=2)


def cast_arc():
    # info page: shallow dashed guide under the cast portraits (mockup path M92 56 Q368 6 644 56)
    W, H, ss = 736, 140, 3
    img = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(201):
        t = i / 200
        x = (1 - t) ** 2 * 32 + 2 * (1 - t) * t * 368 + t * t * 704
        y = (1 - t) ** 2 * 96 + 2 * (1 - t) * t * 30 + t * t * 96
        pts.append((x * ss, y * ss))
    # dashes 2 on / 6 off along the curve
    acc, on = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0) / ss
        if on:
            d.line([(x0, y0), (x1, y1)], fill=(255, 255, 255, 255), width=int(1.5 * ss))
        acc += seg
        if (on and acc >= 2) or (not on and acc >= 6):
            on, acc = not on, 0.0
    save(img.resize((W, H), Image.LANCZOS), "cast_arc.png")


def ruler():
    """Engraved tick ruler (dialog headers, settings): drawn unscaled (aspectratio center,
    align left) and clipped to the control width. Minor tick / 12px, major / 60px, own colours."""
    W, H = 1920, 14
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(0, W, 12):
        major = i % 60 == 0
        d.rectangle([i, 0, i + 1, (12 if major else 6) - 1], fill=TICK if major else LINE)
    save(img, "ruler.png")
    # vertical ruler for side panels
    save(img.rotate(90, expand=True), "ruler_v.png")


def knobs():
    """Skin settings knob: N detents spread over the top 240 deg, amber pointer at detent i.
    rings/knob/<N>_<i>.png, N = 2..4. Own colours."""
    S = 300
    for N in (2, 3, 4):
        span = 90 if N == 2 else 120 if N == 3 else 150
        angles = [-span / 2 + span * j / (N - 1) for j in range(N)]
        for i in range(N):
            img = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            c = S * SS / 2
            ticks(d, c, c, 128 * SS, 138 * SS, 72, 1.5 * SS, LINE)
            ring(d, c, c, 118 * SS, 1.5 * SS, LINE)
            r = 92 * SS
            d.ellipse([c - r, c - r, c + r, c + r], fill=(12, 15, 21, 255), outline=(58, 66, 82, 255), width=int(1.5 * SS))
            for j, a in enumerate(angles):
                x0, y0 = pol(c, c, 122 * SS, a)
                x1, y1 = pol(c, c, 146 * SS, a)
                d.line([(x0, y0), (x1, y1)], fill=AMBER if j == i else TICK, width=int((3 if j == i else 2) * SS))
            # pointer on the knob face
            x0, y0 = pol(c, c, 40 * SS, angles[i])
            x1, y1 = pol(c, c, 84 * SS, angles[i])
            d.line([(x0, y0), (x1, y1)], fill=AMBER, width=int(4 * SS))
            rr = 6 * SS
            d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=GROUND, outline=TEXT, width=int(1.5 * SS))
            save(img.resize((S, S), Image.LANCZOS), f"knob/{N}_{i}.png")


def ticks_only():
    for S in (180, 200, 260):
        save(Gauge(S).face([]), f"dial_ticks_{S}.png")


def main():
    if MEDIA.exists():
        shutil.rmtree(MEDIA)
    gauges()
    osd()
    home_dial()
    home_arc()
    lib_arc()
    dial_list()
    cast_arc()
    ruler()
    knobs()
    n = sum(1 for _ in MEDIA.rglob("*.png"))
    size = sum(p.stat().st_size for p in MEDIA.rglob("*.png"))
    print(f"wrote {n} ring textures ({size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
