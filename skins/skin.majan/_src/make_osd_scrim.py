"""Fullscreen-info corner scrim: darkest bottom-left, falling off smoothly up and to the right, so the
poster / title / plot column stays legible over bright frames without a hard edge anywhere.
White RGB + alpha ramp; the skin tints it with colordiffuse="scrim". Stretched to 1920x1080.

    python _src/make_osd_scrim.py  ->  media/osd/scrim_corner_bl.png
"""
import os
from PIL import Image

W, H = 480, 270  # stretched 4x; the ramp is smooth enough for bilinear scaling


def smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


img = Image.new("RGBA", (W, H))
px = img.load()
for y in range(H):
    v = smooth(0.22, 0.80, y / (H - 1))           # nothing above ~y 240, full by ~y 860
    for x in range(W):
        u = 1.0 - smooth(0.45, 1.0, x / (W - 1))  # full over the text column, gone at the right edge
        px[x, y] = (255, 255, 255, round(255 * 0.80 * v * u))
out = os.path.join(os.path.dirname(__file__), "..", "media", "osd", "scrim_corner_bl.png")
img.save(out)
print(out)
