"""Generate Six Degrees' font derivatives from Hanken Grotesk (reproducible).

Kodi's Font.xml has no letter-spacing control and no glyph fallback, so both are baked into renamed
derivatives of the upstream static TTFs in ../fonts:

  * tracking (CSS letter-spacing, added after every glyph; outlines and kerning untouched):
      display headings -0.03 em, line labels / captions +0.10 em, line counts +0.04 em;
  * a few geometric symbols Hanken lacks, drawn here as simple outlines so labels can use them:
      U+25B2 ▲ U+25B6 ▶ U+25BC ▼ U+25C0 ◀ (direction badges, transport), U+2605 ★ (ratings),
      U+2190 ← U+2191 ↑ U+2193 ↓ (hints).

Outputs (all SIL OFL 1.1, Hanken Grotesk has no Reserved Font Name; renamed anyway):
    SixDegreesText-Regular / -SemiBold / -ExtraBold   Hanken + symbols (no tracking)
    SixDegreesDisplay-ExtraBold                        Hanken 800, -30/1000 em, + symbols
    SixDegreesCaps-SemiBold                            Hanken 600, +100/1000 em, + symbols
    SixDegreesCapsXB-ExtraBold                         Hanken 800, +40/1000 em, + symbols

Usage:  python skins/skin.sixdegrees/_src/make_fonts.py      (needs fontTools)
"""
import math
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"

JOBS = [
    # (source, output, tracking per 1000 em, family, style)
    ("HankenGrotesk-Regular.ttf", "SixDegreesText-Regular.ttf", 0, "Six Degrees Text", "Regular"),
    ("HankenGrotesk-SemiBold.ttf", "SixDegreesText-SemiBold.ttf", 0, "Six Degrees Text", "SemiBold"),
    ("HankenGrotesk-ExtraBold.ttf", "SixDegreesText-ExtraBold.ttf", 0, "Six Degrees Text", "ExtraBold"),
    ("HankenGrotesk-ExtraBold.ttf", "SixDegreesDisplay-ExtraBold.ttf", -30, "Six Degrees Display", "ExtraBold"),
    ("HankenGrotesk-SemiBold.ttf", "SixDegreesCaps-SemiBold.ttf", 100, "Six Degrees Caps", "SemiBold"),
    ("HankenGrotesk-ExtraBold.ttf", "SixDegreesCapsXB-ExtraBold.ttf", 40, "Six Degrees Caps XB", "ExtraBold"),
]

ADV = 760  # advance of the added symbols (font units, before tracking)


def poly(points):
    pen = TTGlyphPen(None)
    pen.moveTo(points[0])
    for p in points[1:]:
        pen.lineTo(p)
    pen.closePath()
    return pen


def symbols():
    """name -> (codepoint, contour point lists). Box: x 70..690, cap height ~700."""
    s = {}
    s["sd_tri_up"] = (0x25B2, [[(380, 690), (690, 120), (70, 120)]])
    s["sd_tri_right"] = (0x25B6, [[(110, 690), (690, 400), (110, 110)]])
    s["sd_tri_down"] = (0x25BC, [[(70, 680), (690, 680), (380, 110)]])
    s["sd_tri_left"] = (0x25C0, [[(650, 690), (650, 110), (70, 400)]])
    pts = []
    cx, cy, R, r = 380, 360, 380, 160
    for k in range(10):
        a = math.pi / 2 - k * math.pi / 5
        rad = R if k % 2 == 0 else r
        pts.append((round(cx + rad * math.cos(a)), round(cy + rad * math.sin(a))))
    s["sd_star"] = (0x2605, [pts])
    # arrows: shaft + head as one outline
    s["sd_arrow_up"] = (0x2191, [[(380, 700), (650, 420), (450, 420), (450, 0), (310, 0), (310, 420), (110, 420)]])
    s["sd_arrow_down"] = (0x2193, [[(310, 700), (450, 700), (450, 280), (650, 280), (380, 0), (110, 280), (310, 280)]])
    s["sd_arrow_left"] = (0x2190, [[(60, 350), (340, 620), (340, 420), (700, 420), (700, 280), (340, 280), (340, 80)]])
    return s


def add_symbols(font):
    glyf, hmtx = font["glyf"], font["hmtx"]
    order = list(font.getGlyphOrder())
    cmap_tables = [t for t in font["cmap"].tables if t.isUnicode()]
    best = font.getBestCmap()
    for name, (cp, contours) in symbols().items():
        if cp in best:
            continue
        pen = TTGlyphPen(None)
        for c in contours:
            pen.moveTo(c[0])
            for p in c[1:]:
                pen.lineTo(p)
            pen.closePath()
        g = pen.glyph()
        order.append(name)
        glyf.glyphOrder = order
        glyf[name] = g
        g.recalcBounds(glyf)
        hmtx[name] = (ADV, g.xMin)
        for t in cmap_tables:
            if t.format in (4, 12) or t.format == 0 and cp < 256:
                t.cmap[cp] = name
    font.setGlyphOrder(order)
    glyf.glyphOrder = order
    for tag in ("hdmx", "LTSH", "VDMX"):
        if tag in font:
            del font[tag]


def derive(src: Path, dst: Path, units_per_1000: int, family: str, style: str) -> None:
    font = TTFont(src)
    add_symbols(font)
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    if delta:
        hmtx = font["hmtx"].metrics
        for name, (adv, lsb) in list(hmtx.items()):
            if adv == 0:
                continue
            hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in font["hmtx"].metrics.values())
    ps_family = family.replace(" ", "")
    full = f"{family} {style}"
    ps = f"{ps_family}-{style}"
    names = font["name"]
    for rec in list(names.names):
        nid = rec.nameID
        if nid in (1, 16):
            names.setName(family, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 17:
            names.setName(style, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 3:
            names.setName(f"{ps};sixdegrees{units_per_1000:+d}", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 4:
            names.setName(full, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 6:
            names.setName(ps, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (21, 22):
            names.removeNames(nameID=nid)
    note = (f"Modified for skin.sixdegrees: tracking {units_per_1000:+d}/1000 em, symbols added. "
            f"Derived from {src.name}. Licensed under the SIL Open Font License 1.1.")
    names.setName(note, 10, 3, 1, 0x409)
    font.save(dst)
    print(f"{src.name} -> {dst.name}  tracking {delta:+d}")


def main() -> None:
    for src, dst, t, fam, style in JOBS:
        derive(HERE / "fontsrc" / src, FONTS / dst, t, fam, style)


if __name__ == "__main__":
    main()
