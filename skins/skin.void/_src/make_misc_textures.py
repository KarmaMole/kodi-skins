"""Generate the textures Builder F (remaining windows) needs: media/misc/*.

Kodi's calibration window needs images for its movers/resizer (Estuary ships
calibrate/cal_*.png; Void has its own so nothing is borrowed), and the EPG grid
needs a 'now' line texture. Same rules as make_textures.py:
  * white on transparent, tinted in XML with colordiffuse
  * drawn at SS x and downsampled (anti-aliased)
  * exported at 2x the size they are drawn at in 1920x1080 skin space
    (4K readiness, SPEC decision 8); XML sizes are the 1x values in comments
  * lowercase filenames

Usage:  python skins/skin.void/_src/make_misc_textures.py
Writes: skins/skin.void/media/misc/cal_tl.png, cal_br.png, cal_ratio.png,
        cal_sub.png, cal_reset.png (SettingsScreenCalibration) and epg_now.png
        (MyPVRGuide time indicator)
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "media" / "misc"
SS = 8
WHITE = (255, 255, 255, 255)


def canvas(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w * SS, h * SS), (255, 255, 255, 0))
    return img, ImageDraw.Draw(img)


def save(img: Image.Image, w: int, h: int, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    img.resize((w, h), Image.LANCZOS).save(OUT / name, optimize=True)
    print(f"  media/misc/{name}  {w}x{h}")


def corner(name: str, flip: bool) -> None:
    """L-shaped corner mark: 128x128 drawn (256 exported). The mover's corner is
    the overscan corner Kodi calibrates, so the stroke hugs that corner."""
    px, t, arm = 256, 4, 160          # export size, stroke, arm length (2x)
    img, d = canvas(px, px)
    s = SS
    d.rectangle([0, 0, arm * s, t * s], fill=WHITE)          # top arm
    d.rectangle([0, 0, t * s, arm * s], fill=WHITE)          # left arm
    # small diagonal tick pointing into the screen: "this corner moves"
    d.line([(t * 3 * s, t * 3 * s), (t * 9 * s, t * 9 * s)], fill=WHITE, width=4 * s)
    if flip:
        img = img.transpose(Image.ROTATE_180)
    save(img, px, px, name)


def ratio() -> None:
    """Pixel-ratio circle: 500x500 drawn (exported 1:1, it is already large).
    A true circle on screen means the pixel aspect ratio is right."""
    px, t = 500, 2
    img, d = canvas(px, px)
    s = SS
    d.ellipse([t * s, t * s, (px - t) * s, (px - t) * s], outline=WHITE, width=t * s)
    c = px * s // 2
    d.line([(c, c - 40 * s), (c, c + 40 * s)], fill=WHITE, width=2 * s)   # crosshair
    d.line([(c - 40 * s, c), (c + 40 * s, c)], fill=WHITE, width=2 * s)
    save(img, px, px, name="cal_ratio.png")


def subtitle_bar() -> None:
    """Subtitle position mover: 380x90 drawn, 760x180 exported. Kodi expects 40px
    of transparency above and below the bar (Estuary note), so the bar is the
    middle 10px band, with end ticks."""
    w, h = 760, 180
    img, d = canvas(w, h)
    s = SS
    top, bar = 80, 20                 # 40 / 10 at 1x
    d.rectangle([0, top * s, w * s, (top + bar) * s], fill=WHITE)
    d.rectangle([0, (top - 24) * s, 6 * s, (top + bar + 24) * s], fill=WHITE)
    d.rectangle([(w - 6) * s, (top - 24) * s, w * s, (top + bar + 24) * s], fill=WHITE)
    save(img, w, h, "cal_sub.png")


def reset_icon() -> None:
    """Reset mover: circular arrow, 100x100 drawn, 200x200 exported."""
    px = 200
    img, d = canvas(px, px)
    s = SS
    m, t = 36, 14
    box = [m * s, m * s, (px - m) * s, (px - m) * s]
    d.arc(box, start=-60, end=250, fill=WHITE, width=t * s)
    # arrow head at the arc's start (-60 deg)
    r = (px - 2 * m) / 2
    cx = cy = px / 2
    a = math.radians(-60)
    ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
    head = 30
    pts = [
        (ex + head * 0.9, ey + head * 0.15),
        (ex - head * 0.55, ey - head * 0.75),
        (ex - head * 0.35, ey + head * 0.85),
    ]
    d.polygon([(x * s, y * s) for x, y in pts], fill=WHITE)
    save(img, px, px, "cal_reset.png")


def epg_now() -> None:
    """EPG grid 'now' indicator: Kodi stretches the progress texture from the grid's
    left edge to the current time. 9-slice, used with border="0,0,2,0": only the
    right 2px column is drawn (the now line), the rest is transparent. 1x (9-slice)."""
    w, h = 8, 8
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    ImageDraw.Draw(img).rectangle([w - 2, 0, w - 1, h - 1], fill=WHITE)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "epg_now.png", optimize=True)
    print(f"  media/misc/epg_now.png  {w}x{h}  border=0,0,2,0")


if __name__ == "__main__":
    epg_now()
    corner("cal_tl.png", flip=False)
    corner("cal_br.png", flip=True)
    ratio()
    subtitle_bar()
    reset_icon()
