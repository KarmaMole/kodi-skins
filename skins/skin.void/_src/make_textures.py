"""Generate Void's textures (reproducible). Run:  python skins/skin.void/_src/make_textures.py

Void draws almost everything with text and one white pixel. Textures exist only for:
  common/white.png          8x8 white, tinted with colordiffuse (rules, bars, fills)
  common/dot.png            anti-aliased disc (shelf dots, radio "on")
  common/dash.png           short bar (radio "off")
  common/vignette_home.png  VoidAmbient vignette: black from the left + soft ceiling and floor
  common/scrim_bottom.png   VoidOSD bottom scrim (520 px tall gradient)
  common/scrim_left.png     horizontal ramp, black on the left (info page, context panel)
  common/scrim_right.png    mirrored (OSD side panels over video)
  common/scrim_top.png      short top ramp (clock/label legibility over fanart)
  common/chevron.png        thin chevron for spin controls
  common/underline.png      edit-control rule (1px rule + transparent buffer row, border 0,0,0,3)
  common/sliderbar.png      1px line centred in 24px (slider bar, scaled 1:1 at height 24)
  common/slidernib.png      2px playhead, 24px tall (same language as the OSD timeline)
  common/play.png           play triangle (slideshow paused badge)
  osd/head.png              2px OSD playhead, 28px tall (slider bar AND nib texture -> drawn 1:1)

White on transparent (alpha carries the gradient); tint with colordiffuse="scrim" etc.
Gradients are small and stretched by Kodi (bilinear) - smooth at any size, tiny files.
Stops are copied from the mockups (docs/concepts/mockups/Void*.dc.html).
"""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
SS = 8


def save(img, rel):
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)
    print(f"  media/{rel}  {img.size[0]}x{img.size[1]}")


def interp(stops, t):
    """stops: [(pos 0-1, alpha 0-1)], linear like CSS gradients."""
    for (p0, a0), (p1, a1) in zip(stops, stops[1:]):
        if p0 <= t <= p1:
            return a0 if p1 == p0 else a0 + (a1 - a0) * (t - p0) / (p1 - p0)
    return stops[-1][1] if t > stops[-1][0] else stops[0][1]


def ramp(w, h, stops, axis):
    """axis 'x': alpha varies left->right; 'y': top->bottom. Black-tintable white."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x + 0.5) / w if axis == "x" else (y + 0.5) / h
            px[x, y] = (255, 255, 255, round(255 * interp(stops, t)))
    return img


def white():
    save(Image.new("RGBA", (8, 8), (255, 255, 255, 255)), "common/white.png")


def dot():
    s = 64
    img = Image.new("RGBA", (s * SS, s * SS), (255, 255, 255, 0))
    ImageDraw.Draw(img).ellipse([2 * SS, 2 * SS, (s - 2) * SS, (s - 2) * SS], fill=(255, 255, 255, 255))
    save(img.resize((s, s), Image.LANCZOS), "common/dot.png")


def dash():
    w, h = 32, 8
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    ImageDraw.Draw(img).rectangle([0, 3, w - 1, 4], fill=(255, 255, 255, 255))
    save(img, "common/dash.png")


def chevron():
    s = 48
    img = Image.new("RGBA", (s * SS, s * SS), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    pts = [(17 * SS, 10 * SS), (31 * SS, 24 * SS), (17 * SS, 38 * SS)]
    d.line(pts, fill=(255, 255, 255, 255), width=3 * SS, joint="curve")
    save(img.resize((s, s), Image.LANCZOS), "common/chevron.png")


def vignette_home():
    """VoidAmbient: left ramp (0 1, 18% .92, 36% .70, 56% .30, 76% 0) combined with a vertical
    ramp (0 .65, 22% 0, 72% 0, 100% .85). Composite alpha = 1-(1-a)(1-b) (two stacked layers)."""
    w, h = 480, 270
    left = [(0, 1.0), (0.18, 0.92), (0.36, 0.70), (0.56, 0.30), (0.76, 0.0), (1, 0.0)]
    vert = [(0, 0.65), (0.22, 0.0), (0.72, 0.0), (1, 0.85)]
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        b = interp(vert, (y + 0.5) / h)
        for x in range(w):
            a = interp(left, (x + 0.5) / w)
            px[x, y] = (255, 255, 255, round(255 * (1 - (1 - a) * (1 - b))))
    save(img, "common/vignette_home.png")


def scrims():
    # VoidOSD bottom scrim, 520 px tall: 0deg gradient = bottom->top stops
    osd = [(0, 0.0), (0.20, 0.16), (0.44, 0.48), (0.74, 0.82), (1, 0.94)]  # top->bottom
    save(ramp(4, 520, osd, "y"), "common/scrim_bottom.png")
    save(ramp(512, 4, [(0, 1.0), (0.35, 0.88), (0.65, 0.45), (1, 0.0)], "x"), "common/scrim_left.png")
    save(ramp(512, 4, [(0, 0.0), (0.35, 0.45), (0.65, 0.88), (1, 1.0)], "x"), "common/scrim_right.png")
    save(ramp(4, 256, [(0, 0.7), (1, 0.0)], "y"), "common/scrim_top.png")


def controls():
    u = Image.new("RGBA", (16, 8), (255, 255, 255, 0))
    ImageDraw.Draw(u).rectangle([0, 6, 15, 6], fill=(255, 255, 255, 255))
    save(u, "common/underline.png")
    b = Image.new("RGBA", (8, 24), (255, 255, 255, 0))
    ImageDraw.Draw(b).rectangle([0, 11, 7, 11], fill=(255, 255, 255, 255))
    save(b, "common/sliderbar.png")
    n = Image.new("RGBA", (4, 24), (255, 255, 255, 0))
    ImageDraw.Draw(n).rectangle([1, 0, 2, 23], fill=(255, 255, 255, 255))
    save(n, "common/slidernib.png")
    h = Image.new("RGBA", (4, 28), (255, 255, 255, 0))
    ImageDraw.Draw(h).rectangle([1, 0, 2, 27], fill=(255, 255, 255, 255))
    save(h, "osd/head.png")


def play():
    s = 64
    img = Image.new("RGBA", (s * SS, s * SS), (255, 255, 255, 0))
    ImageDraw.Draw(img).polygon([(18 * SS, 12 * SS), (50 * SS, 32 * SS), (18 * SS, 52 * SS)], fill=(255, 255, 255, 255))
    save(img.resize((s, s), Image.LANCZOS), "common/play.png")


if __name__ == "__main__":
    play()
    controls()
    white()
    dot()
    dash()
    chevron()
    vignette_home()
    scrims()
