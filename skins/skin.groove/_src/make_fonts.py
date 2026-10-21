"""Build Groove's font files (reproducible).  python skins/skin.groove/_src/make_fonts.py

Upstream (SIL OFL 1.1, google/fonts ofl/jost, in _src/fontsrc/, excluded from the zip):
    Jost-VF.ttf   (wght 100-900)

Kodi can't pick variable axes and Font.xml has no letter-spacing, so every face DESIGN.md section 3 uses is a static
derivative (weight instanced, CSS letter-spacing baked into the advances, /1000 em):
    Groove-Thin       Jost 200    -14   the Time machine year numeral (440 px, letter-spacing -6 px)
    Groove-Light      Jost 300      0   secondary lines >= 24 px, clock, times, counts
    Groove-Text       Jost 400      0   reading text (liner notes, plots), fact values
    Groove-Medium     Jost 500    +10   focused labels, captions, titles (letter-spacing .3 px at 28)
    GrooveCaps-Text   Jost 400    +90   fact labels / ring labels in caps (2 px at 22), uppercase cmap

Vertical metrics are normalised (LESSONS, Void): Kodi puts the baseline max(head.yMax, hhea.ascender) below the line
top and pitches lines at linespacing x (asc - desc). Jost ships 1070 / -375 (1.445 em); Groove uses 960 / -250
(1.21 em, the same pitch as the Majan/Nocturne engine, so forked textbox heights stay valid). The tallest Latin
accent (A-ring 898) and the deepest common descender (g -230) stay inside the box.
    linespacing for a CSS line-height L at size S = L / (S x 1.21)   (body 26 / 40 -> 1.27)
Glyphs Jost lacks (checked 2026-10-21): star, triangles/arrows, check mark, katakana. Use icons, never those glyphs.
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
UP = HERE / "fontsrc"
OUT = HERE.parent / "fonts"
JOST = UP / "Jost-VF.ttf"
ASC, DESC = 960, -250

JOBS = [  # output, wght, tracking /1000 em, caps, family, style
    ("Groove-Thin.ttf", 200, -14, False, "Groove", "Thin"),
    ("Groove-Light.ttf", 300, 0, False, "Groove", "Light"),
    ("Groove-Text.ttf", 400, 0, False, "Groove", "Text"),
    ("Groove-Medium.ttf", 500, 10, False, "Groove", "Medium"),
    ("GrooveCaps-Text.ttf", 400, 90, True, "Groove Caps", "Text"),
]


def track(font, per_1000):
    upm = font["head"].unitsPerEm
    delta = round(per_1000 * upm / 1000)
    if not delta:
        return
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv:
            hmtx[name] = (max(0, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def caps_cmap(font):
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        cmap = table.cmap
        for cp in list(cmap):
            ch = chr(cp)
            up = ch.upper()
            if up != ch and len(up) == 1 and ord(up) in cmap:
                cmap[cp] = cmap[ord(up)]


def set_metrics(font):
    hhea, os2, head = font["hhea"], font["OS/2"], font["head"]
    hhea.ascent, hhea.descent, hhea.lineGap = ASC, DESC, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ASC, DESC, 0
    os2.usWinAscent, os2.usWinDescent = ASC, -DESC
    os2.fsSelection |= 1 << 7
    head.yMax, head.yMin = ASC, DESC


def rename(font, family, style, note):
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style.replace(' ', '')}"
    for rec in list(names.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(family, 1, pid, eid, lid)
        names.setName(style, 2, pid, eid, lid)
        names.setName(f"{ps};groove", 3, pid, eid, lid)
        names.setName(f"{family} {style}", 4, pid, eid, lid)
        names.setName(ps, 6, pid, eid, lid)
    names.setName(note, 10, 3, 1, 0x409)


def build(out, wght, trk, caps, family, style):
    font = instancer.instantiateVariableFont(TTFont(JOST), {"wght": wght}, updateFontNames=False)
    for t in ("STAT", "fvar", "gvar", "avar", "HVAR", "MVAR"):
        if t in font:
            del font[t]
    track(font, trk)
    if caps:
        caps_cmap(font)
    set_metrics(font)
    rename(font, family, style, f"Derived from Jost-VF.ttf (wght {wght}) for skin.groove: tracking {trk:+d}/1000 em"
           f"{', uppercase cmap' if caps else ''}, metrics {ASC}/{DESC}. SIL Open Font License 1.1.")
    font.flavor = None  # LESSONS Keepsake: never save a WOFF2 flavour as .ttf
    font.save(OUT / out)
    print(f"{out:24s} wght {wght} tracking {trk:+d}{' caps' if caps else ''}")


def main():
    OUT.mkdir(exist_ok=True)
    for job in JOBS:
        build(*job)
    shutil.copy(UP / "OFL-Jost.txt", OUT / "OFL-Jost.txt")


if __name__ == "__main__":
    main()
