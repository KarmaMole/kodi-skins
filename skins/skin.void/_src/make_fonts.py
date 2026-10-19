"""Build Void's font files (reproducible). Run:  python skins/skin.void/_src/make_fonts.py

Upstream (SIL OFL 1.1, google/fonts, in _src/fonts_upstream/, excluded from the zip):
    InstrumentSerif-Regular.ttf            static
    InstrumentSans-VF.ttf                  variable (wdth 75-100, wght 400-700)

Kodi can't pick variable-font axes, has no letter-spacing and no OpenType feature
switches, so everything the mockups need is baked into static derivatives:

  * weights instanced from the variable Sans (fontTools instancer)
  * tracking (CSS letter-spacing) added to every advance width
  * tabular figures (tnum) remapped into the cmap for the "Num" faces (timecodes, clock)
  * Cyrillic look-alike letters mapped onto the Latin glyphs (weather.gismeteo text)
  * vertical metrics normalised so Kodi's text boxes are predictable:
      Kodi puts the baseline max(head.yMax, hhea.ascender) below the line top and the line
      pitch is linespacing x (ascender - descender + lineGap) (GUIFontTTF.cpp, Omega).
      Serif: ascender 800 / descender -240 -> pitch 1.04 em at linespacing 1.0, which is the
      mockups' CSS line-height for display titles, and the descenders (-215) stay inside the
      cell, so an N-line textbox of (N-1) x pitch + 1.04 em never clips g/j/p/q/y.
      Sans:  ascender 950 / descender -250 (1.20 em; accented capitals reach 950).

Outputs go to ../fonts with the OFL licence files. Derived fonts are renamed (OFL good practice).
"""
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
UP = HERE / "fonts_upstream"
OUT = HERE.parent / "fonts"

SERIF = UP / "InstrumentSerif-Regular.ttf"
SANS_VF = UP / "InstrumentSans-VF.ttf"

# output file, source, wght (None = static source), tracking /1000 em, tnum, metrics, family, style
JOBS = [
    ("VoidSerifDisplay-Regular.ttf", SERIF, None, -26, False, "serif", "Void Serif Display", "Regular"),
    ("VoidSerifTitle-Regular.ttf", SERIF, None, -14, False, "serif", "Void Serif Title", "Regular"),
    ("VoidSerif-Regular.ttf", SERIF, None, -4, False, "serif", "Void Serif", "Regular"),
    ("VoidSans-Regular.ttf", SANS_VF, 400, 4, False, "sans", "Void Sans", "Regular"),
    ("VoidSans-Medium.ttf", SANS_VF, 500, 4, False, "sans", "Void Sans", "Medium"),
    ("VoidSans-SemiBold.ttf", SANS_VF, 600, 4, False, "sans", "Void Sans", "SemiBold"),
    ("VoidNum-Regular.ttf", SANS_VF, 400, 30, True, "sans", "Void Num", "Regular"),
    ("VoidCaps-Medium.ttf", SANS_VF, 500, 230, True, "sans", "Void Caps", "Medium"),
    ("VoidCapsWide-Medium.ttf", SANS_VF, 500, 320, True, "sans", "Void Caps Wide", "Medium"),
]

METRICS = {"serif": (800, -240), "sans": (950, -250)}


def bake_tnum(font: TTFont) -> None:
    """Point the digit codepoints at their tabular glyphs (GSUB 'tnum' single substitutions)."""
    gsub = font["GSUB"].table
    subst = {}
    for rec in gsub.FeatureList.FeatureRecord:
        if rec.FeatureTag != "tnum":
            continue
        for li in rec.Feature.LookupListIndex:
            lookup = gsub.LookupList.Lookup[li]
            for st in lookup.SubTable:
                if st.LookupType == 7:  # extension
                    st = st.ExtSubTable
                if hasattr(st, "mapping"):
                    subst.update(st.mapping)
    if not subst:
        return
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp, g in list(table.cmap.items()):
            if g in subst:
                table.cmap[cp] = subst[g]


# Cyrillic letters that look exactly like Latin ones. weather.gismeteo writes conditions with them
# ("Сlear"); Instrument has no Cyrillic, so map them onto the Latin glyphs (LESSONS round 3).
HOMOGLYPHS = {
    0x0410: "A", 0x0412: "B", 0x0415: "E", 0x041A: "K", 0x041C: "M", 0x041D: "H", 0x041E: "O",
    0x0420: "P", 0x0421: "C", 0x0422: "T", 0x0425: "X", 0x0423: "Y", 0x0405: "S", 0x0406: "I",
    0x0408: "J", 0x0430: "a", 0x0435: "e", 0x043E: "o", 0x0440: "p", 0x0441: "c", 0x0443: "y",
    0x0445: "x", 0x0455: "s", 0x0456: "i", 0x0458: "j", 0x04BB: "h",
}


def map_homoglyphs(font: TTFont) -> None:
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp, latin in HOMOGLYPHS.items():
            g = table.cmap.get(ord(latin))
            if g and cp not in table.cmap:
                table.cmap[cp] = g


# Vulgar fractions (Instrument has none: "8½" showed a box). Built as TrueType composites from the
# font's own digits (60 %, numerator raised to cap height) and slash, so they match the style.
FRACTIONS = {0x00BD: "12", 0x00BC: "14", 0x00BE: "34", 0x2153: "13", 0x2154: "23", 0x215B: "18",
             0x215C: "38", 0x215D: "58", 0x215E: "78", 0x2044: None}


def add_fractions(font: TTFont) -> None:
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    cmap = font.getBestCmap()
    if any(cp in cmap for cp in FRACTIONS if FRACTIONS[cp]):
        return
    gs = font.getGlyphSet()
    hmtx = font["hmtx"].metrics
    cap = font["OS/2"].sCapHeight or 720
    s = 0.6
    slash = cmap[ord("/")]
    order = font.getGlyphOrder()
    new = {}
    for cp, digits in FRACTIONS.items():
        name = f"void_frac{cp:04X}"
        pen = TTGlyphPen(gs)
        if digits is None:  # fraction slash = the slash
            pen.addComponent(slash, (1, 0, 0, 1, 0, 0))
            adv = hmtx[slash][0]
        else:
            num, den = cmap[ord(digits[0])], cmap[ord(digits[1])]
            nw, dw, sw = hmtx[num][0] * s, hmtx[den][0] * s, hmtx[slash][0] * 0.8
            pen.addComponent(num, (s, 0, 0, s, 0, round(cap - cap * s)))
            pen.addComponent(slash, (0.8, 0, 0, 0.8, round(nw - 50), 0))
            pen.addComponent(den, (s, 0, 0, s, round(nw - 50 + sw - 50), 0))
            adv = round(nw + sw + dw - 100)
        new[name] = (pen.glyph(), adv, cp)
    font.setGlyphOrder(order + list(new))
    for name, (glyph, adv, cp) in new.items():
        font["glyf"][name] = glyph
        hmtx[name] = (adv, 0)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[cp] = name
    if "post" in font and hasattr(font["post"], "extraNames"):
        font["post"].formatType = 3.0  # drop stored names; Kodi needs only the cmap


def track(font: TTFont, units_per_1000: int) -> None:
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    if not delta:
        return
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv == 0:
            continue
        hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def set_metrics(font: TTFont, asc: int, desc: int) -> None:
    hhea, os2, head = font["hhea"], font["OS/2"], font["head"]
    hhea.ascent, hhea.descent, hhea.lineGap = asc, desc, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, desc, 0
    os2.usWinAscent, os2.usWinDescent = asc, -desc
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS
    head.yMax, head.yMin = asc, desc  # Kodi uses max(bbox.yMax, ascender) for the baseline


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style}"
    for rec in list(names.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for nid, val in ((1, family), (2, style), (3, f"{ps};void"), (4, f"{family} {style}"), (6, ps)):
        names.setName(val, nid, 3, 1, 0x409)
        names.setName(val, nid, 1, 0, 0)
    names.setName(note, 10, 3, 1, 0x409)
    if "STAT" in font:
        del font["STAT"]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for out, src, wght, trk, tnum, met, fam, style in JOBS:
        font = TTFont(src)
        if wght is not None:
            font = instancer.instantiateVariableFont(font, {"wght": wght, "wdth": 100}, updateFontNames=False)
        if tnum:
            bake_tnum(font)
        map_homoglyphs(font)
        add_fractions(font)
        track(font, trk)
        set_metrics(font, *METRICS[met])
        rename(font, fam, style,
               f"Modified for skin.void from {src.name}"
               f"{'' if wght is None else f' (wght {wght})'}: tracking {trk:+d}/1000 em"
               f"{', tabular figures' if tnum else ''}, vertical metrics {METRICS[met]}. SIL Open Font License 1.1.")
        font.save(OUT / out)
        print(f"{out:30s} <- {src.name} wght={wght} track={trk:+d} tnum={tnum}")
    for lic in ("OFL-InstrumentSerif.txt", "OFL-InstrumentSans.txt"):
        (OUT / lic).write_bytes((UP / lic).read_bytes())


if __name__ == "__main__":
    main()
