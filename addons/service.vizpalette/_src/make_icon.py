"""icon.png (512x512, solid) and fanart.jpg (1920x1080) for service.vizpalette, in Groove's art direction.
Run: python tools/service.vizpalette/_src/make_icon.py   (Pillow + numpy; _src/ is not shipped)

The service takes four colours from the playing cover (dominant, second, accent, shadow) and hands them to the
skin and the Shadertoy visualisations. The picture: Groove's dark room, one thin white waveform (the visualiser),
lit from behind by four pools of those colours, and the four colours as square swatches (square corners, like
sleeves) on a hairline. All generated; the palette is the one taken from Groove's generated hero sleeve.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = [ROOT.parents[1] / "skins" / "skin.groove" / "fonts", ROOT.parents[1] / "skin.groove" / "fonts"]   # studio / public
RNG = np.random.default_rng(11)
SS = 4
ROOM_CENTRE, ROOM_EDGE = (34, 31, 28), (25, 23, 21)
# VizPalette.Color1..4 for the generated sleeve: dominant, second, accent, shadow
PAL = [(222, 124, 50), (186, 52, 42), (236, 192, 110), (44, 40, 64)]
GLOW = [(222, 124, 50), (196, 58, 48), (232, 176, 92), (84, 76, 140)]   # the shadow colour lifted so it can glow


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def room(w, h):
    y, x = np.mgrid[0:h, 0:w]
    t = smooth(np.sqrt(((x - w / 2) / (w * 0.8)) ** 2 + ((y - h * 0.45) / (h * 0.9)) ** 2))[..., None]
    return np.array(ROOM_CENTRE, float) * (1 - t) + np.array(ROOM_EDGE, float) * t


def ellip(w, h, cx, cy, rx, ry, p=1.0):
    y, x = np.mgrid[0:h, 0:w]
    return smooth(1 - np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)) ** p


def over(base, rgb, a):
    return base * (1 - a[..., None]) + np.asarray(rgb, float) * a[..., None]


def to_img(a):
    n = RNG.random(a.shape) - RNG.random(a.shape)
    return Image.fromarray(np.clip(np.round(a + n), 0, 255).astype(np.uint8), "RGB")


def wave_y(t):
    """A music-like waveform on 0..1: a few partials under a swelling envelope."""
    env = 0.25 + 0.75 * math.sin(math.pi * t) ** 1.4
    v = (math.sin(t * 2 * math.pi * 3.0) * 0.55 + math.sin(t * 2 * math.pi * 7.3 + 0.7) * 0.30
         + math.sin(t * 2 * math.pi * 13.1 + 1.9) * 0.15)
    return v * env


def scene(w, h, x0, x1, wy, amp, sw_y, sw, gap, line_w, caption=None):
    base = room(w, h)
    span = x1 - x0
    for i, c in enumerate(GLOW):                     # four colour pools along the line
        cx = x0 + span * (0.125 + 0.25 * i)
        base = over(base, np.array(c) * 0.62, ellip(w, h, cx, wy, span * 0.24, amp * 3.2, 1.3) * 0.62)
    img = to_img(base).convert("RGBA")
    # soft layers (blurred, at 1x): the line's bloom and the swatches' drop shadows
    soft = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(soft)
    sd.line([(x0 + span * t, wy - amp * wave_y(t)) for t in np.linspace(0, 1, 600)], fill=120, width=int(line_w * 3), joint="curve")
    bloom = soft.filter(ImageFilter.GaussianBlur(line_w * 2.5))
    img.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (w, h), (255, 255, 255)).split(), bloom)))
    total = 4 * sw + 3 * gap
    shadow = Image.new("L", (w, h), 0)
    for i in range(4):
        x = (w - total) / 2 + i * (sw + gap)
        ImageDraw.Draw(shadow).rectangle([x, sw_y + sw * 0.08, x + sw, sw_y + sw * 1.08], fill=170)
    shadow = shadow.filter(ImageFilter.GaussianBlur(sw * 0.08))
    img.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (w, h), 0).split(), shadow)))
    ov = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    pts = [((x0 + span * t) * SS, (wy - amp * wave_y(t)) * SS) for t in np.linspace(0, 1, 600)]
    d.line(pts, fill=(255, 255, 255, 235), width=int(line_w * SS), joint="curve")      # ink line
    # hairline + four square swatches with the 2 px rim of a focused sleeve on the first one
    total = 4 * sw + 3 * gap
    sx0 = (w - total) / 2
    d.line([(x0 * SS, (sw_y + sw / 2) * SS), (x1 * SS, (sw_y + sw / 2) * SS)], fill=(255, 255, 255, 41), width=max(SS, int(line_w * SS * 0.5)))
    for i, c in enumerate(PAL):
        x = sx0 + i * (sw + gap)
        d.rectangle([x * SS, sw_y * SS, (x + sw) * SS, (sw_y + sw) * SS], fill=c + (255,))
        if i == 0:
            d.rectangle([x * SS, sw_y * SS, (x + sw) * SS, (sw_y + sw) * SS], outline=(255, 255, 255, 153), width=int(line_w * SS))
    img.alpha_composite(ov.resize((w, h), Image.LANCZOS))
    if caption:
        fdir = next((p for p in FONTS if p.exists()), None)
        if fdir:
            t = ImageDraw.Draw(img)
            fm = ImageFont.truetype(str(fdir / "Groove-Medium.ttf"), 30)
            fl = ImageFont.truetype(str(fdir / "Groove-Light.ttf"), 28)
            x, y = caption
            t.text((x, y), "Visualizer Palette", font=fm, fill=(255, 255, 255, 235))
            tw = t.textlength("Visualizer Palette", font=fm)
            t.text((x + tw, y + 2), "  ·  four colours from the cover", font=fl, fill=(255, 255, 255, 146))
    return img


def main():
    big = scene(1024, 1024, 112, 912, 430, 150, 700, 132, 36, 6)
    icon = big.convert("RGB").resize((512, 512), Image.LANCZOS)
    icon.save(ROOT / "icon.png", optimize=True)
    fan = scene(1920, 1080, 96, 1824, 470, 190, 720, 120, 40, 3, caption=(96, 1080 - 54 - 40))
    fan.convert("RGB").save(ROOT / "fanart.jpg", quality=92)
    print("wrote", ROOT / "icon.png", icon.size, icon.mode, "|", ROOT / "fanart.jpg", fan.size)


if __name__ == "__main__":
    main()
