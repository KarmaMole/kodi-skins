"""Build Passe-partout's font files (reproducible). Run:  python skins/skin.passepartout/_src/make_fonts.py

Upstream (SIL OFL 1.1, google/fonts ofl/geist + ofl/geistmono, in _src/fontsrc/, excluded from the zip):
    Geist-VF.ttf       variable (wght 100-900)
    GeistMono-VF.ttf   variable (wght 100-900)

Kodi can't pick variable-font axes and Font.xml has no letter-spacing, so every face the
mockups use is baked into a static derivative:

  * weight instanced from the variable font (fontTools instancer)
  * CSS letter-spacing added to every advance width (mockup values, /1000 em):
        titles  Geist Light 300   -25  (.ttl  letter-spacing -.025em)
        display Geist Light 300   -35  (wall-label title -.035em)
        caps    Geist Medium 500 +160  (.cap  letter-spacing .16em, uppercase)
        capsw   Geist Medium 500 +200  (action buttons .2em)
        clock   Geist Mono 400    +20  (.clk b .02em)
        num     Geist Mono 400    +40  (counts .04em)
  * CAPS faces map every lowercase letter onto its capital glyph in the cmap, so dynamic
    labels (genres, artist names) come out in tracked uppercase without [UPPERCASE] tags.
  * vertical metrics normalised so Kodi text boxes are computable (LESSONS round 3, Void):
        Kodi puts the baseline max(head.yMax, hhea.ascender) below the line top and pitches
        lines at linespacing x (ascender - descender + lineGap).
        Geist: ascender 950 / descender -250 -> 1.20 em. Accented capitals reach 940,
        descenders -162, so nothing is cut. A label with aligny=center and height = the CSS
        line-height puts the baseline where the browser does (centre + 0.35 em vs 0.355 em).
        Textbox linespacing = CSS line-height / (1.2 x size).

Outputs go to ../fonts with the OFL licence files. Derived fonts are renamed (OFL good practice).
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
UP = HERE / "fontsrc"
OUT = HERE.parent / "fonts"

SANS = UP / "Geist-VF.ttf"
MONO = UP / "GeistMono-VF.ttf"

# output, source, wght, tracking /1000 em, caps, family, style
JOBS = [
    ("PPTitle-Light.ttf", SANS, 300, -25, False, "PP Title", "Light"),
    ("PPDisplay-Light.ttf", SANS, 300, -35, False, "PP Display", "Light"),
    ("PPSans-Regular.ttf", SANS, 400, 0, False, "PP Sans", "Regular"),
    ("PPSans-Medium.ttf", SANS, 500, 0, False, "PP Sans", "Medium"),
    ("PPCaps-Medium.ttf", SANS, 500, 160, True, "PP Caps", "Medium"),
    ("PPCapsWide-Medium.ttf", SANS, 500, 200, True, "PP Caps Wide", "Medium"),
    ("PPMono-Regular.ttf", MONO, 400, 0, False, "PP Mono", "Regular"),
    ("PPClock-Regular.ttf", MONO, 400, 20, False, "PP Clock", "Regular"),
    ("PPNum-Regular.ttf", MONO, 400, 40, False, "PP Num", "Regular"),
]

ASC, DESC = 950, -250


def track(font: TTFont, units_per_1000: int) -> None:
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    if not delta:
        return
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv == 0:  # combining marks
            continue
        hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def caps_cmap(font: TTFont) -> None:
    """Point lowercase code points at the uppercase glyphs (a tracked small-caps voice)."""
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        cmap = table.cmap
        for cp in list(cmap):
            ch = chr(cp)
            up = ch.upper()
            if up != ch and len(up) == 1 and ord(up) in cmap:
                cmap[cp] = cmap[ord(up)]


def set_metrics(font: TTFont) -> None:
    hhea, os2, head = font["hhea"], font["OS/2"], font["head"]
    hhea.ascent, hhea.descent, hhea.lineGap = ASC, DESC, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = ASC, DESC, 0
    os2.usWinAscent, os2.usWinDescent = ASC, -DESC
    os2.fsSelection |= 1 << 7  # USE_TYPO_METRICS
    head.yMax, head.yMin = ASC, DESC


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style}"
    for rec in list(names.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(family, 1, pid, eid, lid)
        names.setName(style, 2, pid, eid, lid)
        names.setName(f"{ps};passepartout", 3, pid, eid, lid)
        names.setName(f"{family} {style}", 4, pid, eid, lid)
        names.setName(ps, 6, pid, eid, lid)
    names.setName(note, 10, 3, 1, 0x409)


def build(out, src, wght, trk, caps, family, style):
    vf = TTFont(src)
    font = instancer.instantiateVariableFont(vf, {"wght": wght}, updateFontNames=False)
    for t in ("STAT", "fvar", "gvar", "avar", "HVAR", "MVAR"):
        if t in font:
            del font[t]
    track(font, trk)
    if caps:
        caps_cmap(font)
    set_metrics(font)
    rename(font, family, style,
           f"Derived from {src.name} (wght {wght}) for skin.passepartout: tracking {trk:+d}/1000 em, "
           f"{'uppercase cmap, ' if caps else ''}metrics {ASC}/{DESC}. SIL Open Font License 1.1.")
    font.save(OUT / out)
    print(f"{out:26s} wght {wght} tracking {trk:+d}{' caps' if caps else ''}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for job in JOBS:
        build(*job)
    shutil.copy(UP / "OFL-Geist.txt", OUT / "OFL-Geist.txt")
    shutil.copy(UP / "OFL-GeistMono.txt", OUT / "OFL-GeistMono.txt")


if __name__ == "__main__":
    main()
