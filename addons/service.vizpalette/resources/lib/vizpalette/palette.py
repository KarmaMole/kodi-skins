# Visualizer Palette (service.vizpalette)
# Copyright (C) 2026 Omar Kamel
# SPDX-License-Identifier: GPL-2.0-or-later
"""Album palette extraction + tiny PNG writer. Pure Python, no Kodi imports (unit-testable on a PC).

The algorithm is a line-for-line port of extractPalette()/setCover() in visualizers/preview/index.html, so the bench
and the Shield produce the same four colours in the same order:
  48x48 downscale (whole cover stretched, like canvas drawImage) -> k-means k=6, init at luminance quantiles,
  10 iterations -> c0 dominant, c1 second distinct, c2 accent (most vivid), c3 shadow (darkest).
JS semantics kept on purpose: stable sorts, strict '<' (first centroid wins ties), counts from the last assignment
pass, empty clusters keep their centroid, Math.round = floor(x + 0.5).
One deliberate difference from the bench (1.1.1): when the darkest cluster is the dominant colour itself, or is
neither clearly darker than it nor dark (a pale or one-colour cover), the shadow c3 is derived from c0 (SHADOW_FROM_MAIN of its RGB),
so Color4 is always a real darker shade. Covers with a real dark swatch give the bench's c3 unchanged.
"""
import math
import struct
import zlib

K = 6
ITERATIONS = 10
SAMPLE = 48
ART = 128
SHADOW_MAX = 0.75       # a darkest swatch counts as a shadow if its luminance is at most this fraction of the main's
SHADOW_DARK = 48        # ... or if it is this dark anyway (luminance 0..255)
SHADOW_FROM_MAIN = 0.3  # otherwise: the main colour at this brightness (same hue)
HUGE = 2400  # covers above this many px on a side are decoded at reduced scale (Kodi's own cached thumbs are smaller)


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _hsv(c):
    r, g, b = c[0] / 255, c[1] / 255, c[2] / 255
    mx, mn = max(r, g, b), min(r, g, b)
    return ((mx - mn) / mx if mx else 0), mx


def extract_palette(px):
    """px: list of (r, g, b) ints in row-major order. Returns [[r, g, b]] * 4 (ints 0..255)."""
    n = len(px)
    srt = sorted(px, key=lum)  # stable, like Array.prototype.sort
    cents = [list(srt[(2 * i + 1) * n // (2 * K)]) for i in range(K)]
    counts = [0] * K
    for _ in range(ITERATIONS):
        sums = [[0.0, 0.0, 0.0, 0] for _ in range(K)]
        cs = [(c[0], c[1], c[2]) for c in cents]
        for p in px:
            r, g, b = p
            best, bd = 0, 1e18
            for k, (cr, cg, cb) in enumerate(cs):
                dr, dg, db = r - cr, g - cg, b - cb
                d = dr * dr + dg * dg + db * db  # monotonic in hypot(); same argmin, much cheaper
                if d < bd:
                    bd, best = d, k
            s = sums[best]
            s[0] += r
            s[1] += g
            s[2] += b
            s[3] += 1
        cents = [[s[0] / s[3], s[1] / s[3], s[2] / s[3]] if s[3] else c for c, s in zip(cents, sums)]
        counts = [s[3] for s in sums]

    cl = []
    for c, cnt in zip(cents, counts):
        if cnt > 0:
            s, v = _hsv(c)
            cl.append({'c': c, 'n': cnt, 's': s, 'v': v})

    def score(x):
        return x['n'] * (0.35 + x['s'])

    by_score = _sort_desc(cl, score)
    c0 = next((x for x in by_score if x['v'] > 0.12), by_score[0])
    c1 = (next((x for x in by_score if x is not c0 and dist(x['c'], c0['c']) > 48), None)
          or next((x for x in by_score if x is not c0), None) or c0)
    rest = [x for x in cl if x is not c0]
    c2 = _sort_desc(rest, lambda x: x['s'] * x['v'] + 1e-4 * x['n'])[0] if rest else c1
    c3 = sorted(cl, key=lambda x: lum(x['c']))[0]
    pal = [[int(math.floor(v + 0.5)) for v in x['c']] for x in (c0, c1, c2, c3)]
    pal[3] = shadow(pal[0], pal[3], c3 is c0)
    return pal


def shadow(main, darkest, same=False):
    """The shadow colour: the darkest swatch when it is clearly darker than the main colour, else the main colour
    darkened (a pale cover such as Teen Dream gave Color4 == Color1 on the Shield, device audit 2026-10-21)."""
    if not same and (lum(darkest) <= SHADOW_MAX * lum(main) or lum(darkest) <= SHADOW_DARK):
        return list(darkest)
    return [int(math.floor(v * SHADOW_FROM_MAIN + 0.5)) for v in main]


def _sort_desc(items, key):
    """JS `arr.sort((a, b) => key(b) - key(a))`: descending and stable (ties keep input order)."""
    return sorted(items, key=lambda x: -key(x))


# ------------------------------------------------------------------------------------------------ PNG writer
def png_rgba(width, height, rgba):
    """Encode 8-bit RGBA bytes (row 0 = top) as a PNG. Same layout lodepng hands to Shadertoy."""
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw += rgba[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')


def default_palette_png():
    return png_rgba(4, 1, bytes(16))


def default_art_png():
    return png_rgba(ART, ART, bytes(ART * ART * 4))


def palette_png(pal):
    return png_rgba(4, 1, bytes(v for c in pal for v in (c[0], c[1], c[2], 255)))


# ------------------------------------------------------------------------------------------------ PIL side
def cover_pngs(image_bytes, Image, ImageOps=None, with_art=True):
    """Decode a cover with PIL and return (palette, palette_png_bytes, art_png_bytes). art_png_bytes is None when
    with_art is False (no Shadertoy pack installed: only the palette is needed).

    Like the bench: EXIF orientation applied (browsers do), transparency flattened on black (getImageData of a
    transparent pixel reads 0,0,0), whole image stretched to 48x48 / 128x128 (no crop), alpha forced to 255.
    """
    import io
    im = Image.open(io.BytesIO(image_bytes))
    if max(im.size) > HUGE:  # memory guard only: a DCT-scaled decode no longer matches the bench bit for bit
        im.draft('RGB', (HUGE // 2, HUGE // 2))
    if ImageOps is not None:
        try:
            im = ImageOps.exif_transpose(im)
        except Exception:  # noqa: BLE001 - bad EXIF must not cost the palette
            pass
    if im.mode in ('RGBA', 'LA', 'P', 'PA') or 'transparency' in im.info:
        rgba = im.convert('RGBA')
        bg = Image.new('RGBA', rgba.size, (0, 0, 0, 255))
        bg.alpha_composite(rgba)
        im = bg.convert('RGB')
    else:
        im = im.convert('RGB')
    small = im.resize((SAMPLE, SAMPLE), RESAMPLE(Image))
    data = small.tobytes()
    px = [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]
    pal = extract_palette(px)
    if not with_art:
        return pal, palette_png(pal), None
    art = im.resize((ART, ART), RESAMPLE(Image)).convert('RGBA')
    return pal, palette_png(pal), png_rgba(ART, ART, art.tobytes())


def RESAMPLE(Image):  # noqa: N802 - BOX: the bench's boxResize() is a bit-exact JS port of Pillow's BOX resize
    res = getattr(Image, 'Resampling', Image)
    return res.BOX
