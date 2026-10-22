"""Six Degrees add-on art -> ../resources/icon.png (256x256) and ../resources/fanart.jpg (1920x1080).

Icon: the interchange (ink ring, white centre) with the four coloured lines leaving it, on the map paper.
Fanart: a quiet transit map: a centre station and four lines with stops and 45-degree bends.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
SS = 4
GROUND = (244, 244, 241)
INK = (21, 22, 26)
RED, BLUE, VIO, GRN, ROUTE = (232, 73, 47), (45, 91, 216), (138, 79, 214), (31, 157, 87), (140, 142, 148)


def stroke(d, pts, w, col, r=26):
    """Rounded-corner polyline (quadratic bends) stamped with discs."""
    samples = [pts[0]]
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr = min(r, l1 / 2, l2 / 2)
        ax, ay = x1 - (x1 - x0) / l1 * rr, y1 - (y1 - y0) / l1 * rr
        bx, by = x1 + (x2 - x1) / l2 * rr, y1 + (y2 - y1) / l2 * rr
        samples.append((ax, ay))
        for k in range(1, 30):
            t = k / 30
            samples.append(((1 - t) ** 2 * ax + 2 * (1 - t) * t * x1 + t * t * bx, (1 - t) ** 2 * ay + 2 * (1 - t) * t * y1 + t * t * by))
        samples.append((bx, by))
    samples.append(pts[-1])
    rad = w * SS / 2
    for (xa, ya), (xb, yb) in zip(samples, samples[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) * 2))
        for k in range(n + 1):
            t = k / n
            x, y = (xa + (xb - xa) * t) * SS, (ya + (yb - ya) * t) * SS
            d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col)


def stop(d, x, y, dia, ring, col, fill=(255, 255, 255)):
    r = dia * SS / 2
    d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=col)
    r2 = (dia / 2 - ring) * SS
    d.ellipse([x * SS - r2, y * SS - r2, x * SS + r2, y * SS + r2], fill=fill)


def icon():
    n = 256
    im = Image.new("RGB", (n * SS, n * SS), GROUND)
    d = ImageDraw.Draw(im)
    w = 22
    stroke(d, [(128, 18), (128, 92)], w, RED)
    stroke(d, [(164, 128), (238, 128)], w, BLUE)
    stroke(d, [(128, 164), (128, 238)], w, GRN)
    stroke(d, [(18, 128), (92, 128)], w, VIO)
    stop(d, 128, 128, 92, 20, INK)
    im.resize((n, n), Image.LANCZOS).save(SKIN / "resources" / "icon.png", optimize=True)


def fanart():
    W, H = 1920, 1080
    im = Image.new("RGB", (W * SS, H * SS), GROUND)
    d = ImageDraw.Draw(im)
    cx, cy = 960, 520
    lines = [
        (RED, [(cx - 40, cy - 150), (cx - 40, cy - 250), (cx - 120, cy - 330), (180, cy - 330)], [(760, cy - 330), (560, cy - 330), (360, cy - 330)]),
        (BLUE, [(cx + 150, cy - 40), (1760, cy - 40)], [(1240, cy - 40), (1400, cy - 40), (1560, cy - 40), (1700, cy - 40)]),
        (GRN, [(cx + 60, cy + 150), (cx + 60, cy + 270), (cx + 140, cy + 350), (1740, cy + 350)], [(1300, cy + 350), (1480, cy + 350), (1660, cy + 350)]),
        (VIO, [(cx - 150, cy + 60), (cx - 260, cy + 60), (cx - 340, cy + 140), (200, cy + 140)], [(500, cy + 140), (350, cy + 140)]),
    ]
    for col, pts, stops in lines:
        stroke(d, pts, 12, col)
        for x, y in stops:
            stop(d, x, y, 40, 11, col)
    # the interchange: a rounded square with an ink ring
    r = 28 * SS
    box = [(cx - 150) * SS, (cy - 150) * SS, (cx + 150) * SS, (cy + 150) * SS]
    d.rounded_rectangle(box, radius=r, fill=INK)
    inset = 16 * SS
    d.rounded_rectangle([box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset], radius=r - inset, fill=(255, 255, 255))
    stop(d, cx, cy, 120, 26, INK)
    im.resize((W, H), Image.LANCZOS).save(SKIN / "resources" / "fanart.jpg", quality=90)


if __name__ == "__main__":
    icon()
    fanart()
    print("wrote icon.png + fanart.jpg")
