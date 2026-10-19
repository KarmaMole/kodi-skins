"""Build Keepsake's font files (reproducible).  Run:  python skins/skin.keepsake/_src/make_fonts.py

Upstream (SIL OFL 1.1, in _src/fontsrc/, excluded from the zip):
    caveat__Caveat[wght].ttf                     google/fonts ofl/caveat   (handwriting, white gel pen)
    fraunces__Fraunces[SOFT,WONK,opsz,wght].ttf  google/fonts ofl/fraunces (titles + body)
    dmmono__DMMono-Regular.ttf                   google/fonts ofl/dmmono   (labels)
    DSEG7Classic-Bold.woff2                      keshikan/DSEG (OFL, Reserved Font Name "DSEG": our
                                                 derivative is renamed "Keepsake Stamp")

Kodi can't pick variable-font axes, has no letter-spacing and no text glow, so every face is baked:
  * axes instanced with fontTools instancer (mockup values: Caveat 500/600/700, Fraunces opsz 144 wght 600
    SOFT 50 for titles, opsz 36 for small titles, opsz 14 wght 400 for body)
  * subset to Latin (+ Latin-1, Latin Extended-A, punctuation) so head.yMax comes from real Latin glyphs:
    Kodi puts the baseline max(head.yMax, hhea.ascender) below the line top (LESSONS round 3, Void)
  * CSS letter-spacing baked into advances; Label faces map lowercase onto capitals (tracked small caps)
  * vertical metrics normalised (ascender/descender below) so label/textbox heights are computable
  * Cyrillic homoglyphs (weather.gismeteo "Сlear") mapped onto Latin glyphs in body/label faces

The date stamp (`'26 10 18`, orange LCD imprint of an old film camera):
  * KeepsakeStamp-Bold       DSEG7 Classic Bold, +45/1000 letter-spacing, plus
        "'"  = the apostrophe bar (.16 x .42 em, skewed 8 deg, raised .55 em; the mockup's separate bar)
        "~"  = the gap between groups (.42 em)
        " ", A, P, M, a, p, m = zero-width blanks, so a region clock label "9:47 PM" prints "9:47"
  * KeepsakeStampGlow1/2     the same glyphs dilated by 45 / 120 units (16 offset copies, nonzero union):
        drawn under the core at falling alpha = the glow (Kodi has no text-shadow blur)
"""
from __future__ import annotations

import math
import shutil
from pathlib import Path

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
UP = HERE / "fontsrc"
OUT = HERE.parent / "fonts"

CAVEAT = UP / "caveat__Caveat[wght].ttf"
FRAUNCES = UP / "fraunces__Fraunces[SOFT,WONK,opsz,wght].ttf"
DMMONO = UP / "dmmono__DMMono-Regular.ttf"
DSEG = UP / "DSEG7Classic-Bold.woff2"

LATIN = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + list(range(0x2010, 0x2028))
         + list(range(0x2030, 0x203B)) + [0x20AC, 0x2122, 0x2190, 0x2192, 0x2212, 0x2026])

# output, source, axes, tracking /1000 em, caps, (ascender, descender) as fraction of em, family, style
JOBS = [
    ("KeepsakeHand-Medium.ttf", CAVEAT, {"wght": 500}, 0, False, (0.90, -0.26), "Keepsake Hand", "Medium"),
    ("KeepsakeHand-SemiBold.ttf", CAVEAT, {"wght": 600}, 0, False, (0.90, -0.26), "Keepsake Hand", "SemiBold"),
    ("KeepsakeHand-Bold.ttf", CAVEAT, {"wght": 700}, 0, False, (0.90, -0.26), "Keepsake Hand", "Bold"),
    ("KeepsakeTitle-SemiBold.ttf", FRAUNCES, {"wght": 600, "opsz": 144, "SOFT": 50, "WONK": 0}, -8, False,
     (0.92, -0.26), "Keepsake Title", "SemiBold"),
    ("KeepsakeTitleText-SemiBold.ttf", FRAUNCES, {"wght": 600, "opsz": 36, "SOFT": 50, "WONK": 0}, 0, False,
     (0.92, -0.26), "Keepsake Title Text", "SemiBold"),
    ("KeepsakeBody-Regular.ttf", FRAUNCES, {"wght": 400, "opsz": 14, "SOFT": 0, "WONK": 0}, 0, False,
     (0.92, -0.26), "Keepsake Body", "Regular"),
    ("KeepsakeLabel-Regular.ttf", DMMONO, None, 130, True, (0.97, -0.25), "Keepsake Label", "Regular"),
    ("KeepsakeLabelNarrow-Regular.ttf", DMMONO, None, 85, True, (0.97, -0.25), "Keepsake Label Narrow", "Regular"),
    ("KeepsakeMono-Regular.ttf", DMMONO, None, 40, False, (0.97, -0.25), "Keepsake Mono", "Regular"),
]

HOMOGLYPHS = {0x0410: "A", 0x0412: "B", 0x0415: "E", 0x041A: "K", 0x041C: "M", 0x041D: "H", 0x041E: "O",
              0x0420: "P", 0x0421: "C", 0x0422: "T", 0x0425: "X", 0x0430: "a", 0x0435: "e", 0x043E: "o",
              0x0440: "p", 0x0441: "c", 0x0443: "y", 0x0445: "x"}


def instance(src: Path, axes):
    vf = TTFont(src)
    if axes is None:
        return vf
    font = instancer.instantiateVariableFont(vf, axes, updateFontNames=False)
    for t in ("STAT", "fvar", "gvar", "avar", "HVAR", "MVAR", "cvar"):
        if t in font:
            del font[t]
    return font


def do_subset(font: TTFont, unicodes) -> TTFont:
    opts = subset.Options()
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.glyph_names = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=unicodes)
    sub.subset(font)
    return font


def track(font: TTFont, units_per_1000: int) -> None:
    delta = round(units_per_1000 * font["head"].unitsPerEm / 1000)
    if not delta:
        return
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv:
            hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def caps_cmap(font: TTFont) -> None:
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        cmap = table.cmap
        for cp in list(cmap):
            ch = chr(cp)
            up = ch.upper()
            if up != ch and len(up) == 1 and ord(up) in cmap:
                cmap[cp] = cmap[ord(up)]


def homoglyphs(font: TTFont) -> None:
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp, latin in HOMOGLYPHS.items():
            if cp not in table.cmap and ord(latin) in table.cmap:
                table.cmap[cp] = table.cmap[ord(latin)]


def set_metrics(font: TTFont, asc: int, desc: int) -> None:
    hhea, os2 = font["hhea"], font["OS/2"]
    hhea.ascent, hhea.descent, hhea.lineGap = asc, desc, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, desc, 0
    os2.usWinAscent, os2.usWinDescent = asc, -desc
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style}"
    for rec in list(names.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(family, 1, pid, eid, lid)
        names.setName(style, 2, pid, eid, lid)
        names.setName(f"{ps};keepsake", 3, pid, eid, lid)
        names.setName(f"{family} {style}", 4, pid, eid, lid)
        names.setName(ps, 6, pid, eid, lid)
    names.setName(note, 10, 3, 1, 0x409)


def build(out, src, axes, trk, caps, metrics, family, style):
    font = instance(src, axes)
    upm = font["head"].unitsPerEm
    do_subset(font, LATIN)
    track(font, trk)
    if caps:
        caps_cmap(font)
    homoglyphs(font)
    asc, desc = round(metrics[0] * upm), round(metrics[1] * upm)
    set_metrics(font, asc, desc)
    rename(font, family, style,
           f"Derived from {src.name} {axes or ''} for skin.keepsake: Latin subset, tracking {trk:+d}/1000 em, "
           f"{'uppercase cmap, ' if caps else ''}metrics {asc}/{desc}. SIL Open Font License 1.1.")
    font.save(OUT / out)
    font = TTFont(OUT / out)
    head = font["head"]
    print(f"{out:34s} upm {upm} asc {asc} desc {desc} head.yMax {head.yMax} yMin {head.yMin}"
          f"  -> baseline {max(head.yMax, asc) / upm:.3f} em, line {(max(head.yMax, asc) + max(-head.yMin, -desc)) / upm:.3f} em")


# ------------------------------------------------------------------------------------------------ stamp
STAMP_TRACK = 45          # CSS letter-spacing 1px at 22px
GAP = 420                 # .42 em gap span
BAR = dict(w=160, h=420, raise_=550, skew=math.tan(math.radians(8)), after=180)


def glyph_from_recording(rec, ox=0.0, oy=0.0):
    """Replay a recording into a TTGlyphPen with an offset; returns the pen."""
    pen = TTGlyphPen(None)
    rec.replay(TransformPen(pen, (1, 0, 0, 1, ox, oy)))
    return pen


def dilated(rec, d: int):
    pen = TTGlyphPen(None)
    rec.replay(pen)
    if d:
        for k in range(16):
            a = 2 * math.pi * k / 16
            rec.replay(TransformPen(pen, (1, 0, 0, 1, d * math.cos(a), d * math.sin(a))))
    return pen.glyph()


def bar_recording():
    """The apostrophe bar as a recording (clockwise outer contour, TrueType winding)."""
    w, h, r, s = BAR["w"], BAR["h"], BAR["raise_"], BAR["skew"]
    # skew about the bar's centre: bottom moves left, top moves right
    half = h / 2 * s
    pts = [(0 - half, r), (0 + half, r + h), (w + half, r + h), (w - half, r)]
    from fontTools.pens.recordingPen import RecordingPen
    rec = RecordingPen()
    rec.moveTo(pts[0])
    for p in pts[1:]:
        rec.lineTo(p)
    rec.closePath()
    return rec


def build_stamp(out: str, family: str, style: str, dilate: int) -> None:
    font = TTFont(DSEG)
    font.flavor = None  # the source is WOFF2: without this fontTools saves WOFF2, which Kodi's FreeType can't open
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    hmtx = font["hmtx"].metrics
    order = list(font.getGlyphOrder())

    def recording(name):
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        return rec

    keep = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "colon", "hyphen",
            "period", "space", ".notdef"}
    # dilate the visible glyphs, track the advances
    for name in order:
        if name in keep and name not in (".notdef", "space"):
            rec = recording(name)
            g = dilated(rec, dilate)
            glyf[name] = g
            g.recalcBounds(glyf)
            adv, _ = hmtx[name]
            # lsb must equal the outline's xMin: FreeType shifts TrueType outlines by (lsb - xMin), so a stale
            # lsb moved the dilated glow layers sideways against the core digits (seen on the Shield)
            hmtx[name] = (adv + STAMP_TRACK if adv else 0, getattr(g, "xMin", 0))
    # new glyphs: apostrophe bar, gap, blank
    bar = dilated(bar_recording(), dilate)
    gap = TTGlyphPen(None).glyph()
    blank = TTGlyphPen(None).glyph()
    for name, g, adv in (("ksbar", bar, BAR["w"] + BAR["after"] + STAMP_TRACK), ("ksgap", gap, GAP + STAMP_TRACK),
                         ("ksblank", blank, 0)):
        order.append(name)
        glyf.glyphs[name] = g
        if hasattr(g, "coordinates") and g.numberOfContours:
            g.recalcBounds(glyf)
        hmtx[name] = (adv, getattr(g, "xMin", 0))
    font.setGlyphOrder(order)
    glyf.glyphOrder = order
    hmtx["space"] = (0, 0)
    # cmap: digits, : - . kept; ' = bar, ~ = gap, space + AM/PM letters = blank, everything else dropped
    newmap = {}
    for cp, name in cmap.items():
        if name in keep:
            newmap[cp] = name
    newmap[ord("'")] = "ksbar"
    newmap[0x2019] = "ksbar"
    newmap[ord("~")] = "ksgap"
    for ch in " APMapm  ":
        newmap[ord(ch)] = "ksblank"
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap = dict(newmap)
    font["maxp"].numGlyphs = len(order)
    # drop GDEF etc. that reference old glyph sets are fine; recompute bounds on save
    for t in ("GDEF", "FFTM"):
        if t in font:
            del font[t]
    set_metrics(font, 1150, -150)  # same baseline for core and glow layers (glow2 reaches 1120 / -120)
    rename(font, family, style,
           f"Derived from DSEG7 Classic Bold (keshikan, OFL 1.1, RFN 'DSEG') for skin.keepsake: "
           f"+{STAMP_TRACK} tracking, apostrophe bar, gap and blanks, outlines dilated {dilate} units.")
    font.save(OUT / out)
    f2 = TTFont(OUT / out)
    print(f"{out:34s} dilate {dilate:3d}  head.yMax {f2['head'].yMax} yMin {f2['head'].yMin}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for job in JOBS:
        build(*job)
    build_stamp("KeepsakeStamp-Bold.ttf", "Keepsake Stamp", "Bold", 0)
    build_stamp("KeepsakeStampGlow1-Bold.ttf", "Keepsake Stamp Glow1", "Bold", 45)
    build_stamp("KeepsakeStampGlow2-Bold.ttf", "Keepsake Stamp Glow2", "Bold", 120)
    shutil.copy(UP / "caveat__OFL.txt", OUT / "OFL-Caveat.txt")
    shutil.copy(UP / "fraunces__OFL.txt", OUT / "OFL-Fraunces.txt")
    shutil.copy(UP / "dmmono__OFL.txt", OUT / "OFL-DMMono.txt")
    shutil.copy(UP / "dseg_LICENSE.txt", OUT / "OFL-DSEG.txt")


if __name__ == "__main__":
    main()
