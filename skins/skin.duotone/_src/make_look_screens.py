"""Section screens for the monochrome Looks (docs/skin.duotone/DESIGN.md "Looks: Light and Dark").

In Light and Dark there are no section colours, so each section gets its own print screen instead:
  Films   fine dot screen      overlays/dots.png / dots_art.png  (already made by make_textures.py)
  Series  45-degree line screen overlays/screen_lines.png / screen_lines_art.png
  Music   coarse dot screen    overlays/screen_coarse.png / screen_coarse_art.png
  Paper   no screen            (Search / Settings / system windows stay plain)

Same convention as dots.png: WHITE on transparent, the screen's strength baked into the alpha (field 12 %,
art 14 % at full coverage), 1920x1080, drawn unscaled with aspectratio center, tinted in XML with the
existing dots / dots_art tokens (ink in Light, light ink in Dark). Every pattern tiles exactly into 1920x1080
(periods 8, 12 and 16 divide both), so the screen lines up across neighbouring controls.

  python skins/skin.duotone/_src/make_look_screens.py
"""
from pathlib import Path
import math

from PIL import Image

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
N = 8  # subsamples per axis


def _tile(period, cover):
    """cover(fx, fy) -> 0..1 for a point inside one period; returns an L tile of coverage."""
    t = Image.new("L", (period, period), 0)
    px = t.load()
    for y in range(period):
        for x in range(period):
            acc = 0.0
            for sy in range(N):
                for sx in range(N):
                    acc += cover(x + (sx + 0.5) / N, y + (sy + 0.5) / N)
            px[x, y] = round(acc / (N * N) * 255)
    return t


def dot_cover(period, r_in, r_out):
    c = period / 2.0

    def f(fx, fy):
        d = math.hypot(fx - c, fy - c)
        return 1.0 if d <= r_in else 0.0 if d >= r_out else 1.0 - (d - r_in) / (r_out - r_in)
    return f


def line_cover(period, width):
    """Lines along x + y = k * period (45 degrees); perpendicular spacing period / sqrt 2."""
    half = width / 2.0
    s2 = math.sqrt(2)

    def f(fx, fy):
        u = ((fx + fy) % period)          # distance along the diagonal axis, in x+y units
        d = min(u, period - u) / s2       # perpendicular distance to the nearest line
        edge = 0.5                        # 1px soft edge
        return 1.0 if d <= half - edge else 0.0 if d >= half + edge else (half + edge - d) / (2 * edge)
    return f


def screen(period, cover, alpha, w=1920, h=1080):
    tile = _tile(period, cover)
    a = Image.new("L", (w, h))
    for yy in range(0, h, period):
        for xx in range(0, w, period):
            a.paste(tile, (xx, yy))
    a = a.point(lambda v: round(v * alpha))
    im = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    im.putalpha(a)
    return im


SCREENS = {
    # name: (period, field cover, art cover)
    "screen_lines": (12, line_cover(12, 1.25), line_cover(12, 1.6)),
    "screen_coarse": (16, dot_cover(16, 3.0, 3.8), dot_cover(16, 3.4, 4.2)),
}


def build(out_dir=MEDIA / "overlays"):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, (period, field, art) in SCREENS.items():
        screen(period, field, 0.12).save(out_dir / f"{name}.png", optimize=True)
        screen(period, art, 0.14).save(out_dir / f"{name}_art.png", optimize=True)
        print(out_dir / f"{name}.png", "+ _art")


if __name__ == "__main__":
    build()
