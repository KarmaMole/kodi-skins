"""Sentence textures (media/sentence/). White + alpha only: every texture is tinted in XML with a
palette colour via colordiffuse, so the palette stays in colors/defaults.xml.

  phrase_block.png   focused phrase: 6px-radius block + 6px halo ring at 14% (border 14)
  phrase_under.png   unfocused phrase: 3px underline under the TEXT only. 24px transparent side margins
                     (= the button textoffsetx) so the line spans the label, not the padding.
                     border="24,0,24,6": a transparent buffer row above the 3px line (9-slice bleed rule)
  phrase_under_m.png / _s.png the same with 18 / 16px margins (library header / small phrases)
  round6.png         6px-radius fill (dialog panels, keys, small blocks), border 8
  outline6.png       2px outline, 6px radius (unfocused keys / fields), border 8
  playhead_nib.png   3px playhead tick for the OSD progress slider
  ring.png           3px ring, 8px radius: generic focus frame for forked controls, border 16
  glow.png           radial warmth behind the Home sentence (tint lilac at ~5%)
  ramp_*.png         exact scrim ramps from the mockups (tint with `scrim`)
  poster_shadow.png  soft drop shadow under posters (0 16px 34px rgba(0,0,0,.45))

Usage: python skins/skin.sentence/_src/make_textures.py   (Pillow)
"""
from pathlib import Path
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "media" / "sentence"
SS = 4  # supersampling for rounded shapes


def rounded(size, radius, inset=0, alpha=255):
    w, h = size
    big = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([inset * SS, inset * SS, (w - inset) * SS - 1, (h - inset) * SS - 1], radius * SS, fill=alpha)
    return big.resize((w, h), Image.LANCZOS)


def white(alpha: Image.Image) -> Image.Image:
    im = Image.new("RGBA", alpha.size, (255, 255, 255, 0))
    im.putalpha(alpha)
    return im


def phrase_block():
    halo = rounded((64, 64), 12, 0, round(255 * 0.14))
    core = rounded((64, 64), 6, 6, 255)
    white(ImageChops.lighter(halo, core)).save(OUT / "phrase_block.png")


def phrase_under():
    # side margins = the phrase textoffsetx (24 big phrases, 16 small); bottom border 6:
    # 1 transparent buffer row, the 3px line, 2 rows of padding under it
    for name, m in (("phrase_under.png", 24), ("phrase_under_m.png", 18), ("phrase_under_s.png", 16)):
        w = 2 * m + 16
        a = Image.new("L", (w, 16), 0)
        ImageDraw.Draw(a).rectangle([m, 11, w - m - 1, 13], fill=255)
        white(a).save(OUT / name)


def round6():
    white(rounded((32, 32), 6)).save(OUT / "round6.png")
    outer = rounded((32, 32), 6)
    inner = rounded((32, 32), 4, 2)
    white(ImageChops.subtract(outer, inner)).save(OUT / "outline6.png")


def ring():
    outer = rounded((40, 40), 8)
    inner = rounded((40, 40), 5, 3)
    white(ImageChops.subtract(outer, inner)).save(OUT / "ring.png")


def playhead():
    # Kodi slider nib maths (see Majan make_osd_textures.py): a horizontal nib is drawn h = control
    # height, w = 2h. 64x32 texture with a 4px column -> a 21px control draws a ~3px playhead.
    a = Image.new("L", (64, 32), 0)
    ImageDraw.Draw(a).rectangle([30, 0, 33, 31], fill=255)
    white(a).save(OUT / "playhead_nib.png")


def glow():
    w, h = 512, 320
    a = Image.new("L", (w, h), 0)
    px = a.load()
    for y in range(h):
        for x in range(w):
            dx = (x - w / 2) / (w / 2)
            dy = (y - h / 2) / (h / 2)
            r = min(1.0, math.hypot(dx, dy))
            px[x, y] = round(255 * (1 - r) ** 1.6)
    white(a).save(OUT / "glow.png")


def ramp(name, stops, length=512, horizontal=True):
    """stops: [(pos 0..1, alpha 0..1)] along the ramp (left->right or top->bottom)."""
    vals = []
    for i in range(length):
        t = i / (length - 1)
        for (p0, a0), (p1, a1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                vals.append(a0 + (a1 - a0) * k)
                break
    if horizontal:
        a = Image.new("L", (length, 4))
        for x, v in enumerate(vals):
            for y in range(4):
                a.putpixel((x, y), round(255 * v))
    else:
        a = Image.new("L", (4, length))
        for y, v in enumerate(vals):
            for x in range(4):
                a.putpixel((x, y), round(255 * v))
    white(a).save(OUT / f"ramp_{name}.png")


def osd_corner():
    """OSD scrim for the bottom half: left-to-right .92 -> .6 -> .25 (mockup), faded in vertically over
    the first 35% so there is no hard top edge over a playing picture."""
    w, h = 480, 270
    a = Image.new("L", (w, h))
    px = a.load()
    for x in range(w):
        t = x / (w - 1)
        hz = 0.92 + (0.6 - 0.92) * (t / 0.55) if t <= 0.55 else 0.6 + (0.25 - 0.6) * ((t - 0.55) / 0.45)
        for y in range(h):
            v = min(1.0, (y / (h - 1)) / 0.35)
            v = v * v * (3 - 2 * v)
            px[x, y] = round(255 * hz * v)
    white(a).save(OUT / "osd_corner.png")


def poster_shadow():
    w, h, pad = 196, 294, 60
    a = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(a).rectangle([pad, pad + 16, pad + w, pad + h + 16], fill=round(255 * 0.45))
    a = a.filter(ImageFilter.GaussianBlur(17))
    white(a).resize((158, 207), Image.LANCZOS).save(OUT / "poster_shadow.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    phrase_block()
    phrase_under()
    round6()
    ring()
    playhead()
    glow()
    # Info page backdrop: 90deg #0F1412 0% -> .86 at 35% -> 0 (760px wide)
    ramp("info_left", [(0, 1.0), (0.35, 0.86), (1, 0.0)])
    # generic: full -> clear
    ramp("left", [(0, 1.0), (1, 0.0)])
    ramp("top", [(0, 1.0), (1, 0.0)], horizontal=False)
    ramp("bottom", [(0, 0.0), (1, 1.0)], horizontal=False)
    # OSD over the paused frame: .92 -> .6 at 55% -> .25
    ramp("osd_left", [(0, 0.92), (0.55, 0.6), (1, 0.25)])
    poster_shadow()
    osd_corner()
    print("textures ->", OUT)


if __name__ == "__main__":
    main()
