"""Build Fold's font files (reproducible).  python skins/skin.fold/_src/make_fonts.py

Upstream (SIL OFL 1.1, google/fonts ofl/bricolagegrotesque + ofl/ibmplexmono, in _src/fontsrc/, not zipped):
    BricolageGrotesque-VF.ttf   variable (opsz 12-96, wght 200-800, wdth 75-100)
    IBMPlexMono-{Regular,Medium,SemiBold}.ttf   static

Kodi can't pick variable-font axes and Font.xml has no letter-spacing, so every face the mockups use is
baked into a static derivative (docs/skin.fold/DESIGN.md, type):
  * opsz + wght instanced from the variable font (the browser used font-optical-sizing auto = the px size)
  * CSS letter-spacing added to every advance width (mockup values, /1000 em)
  * CAPS faces point lowercase code points at the capitals (tabs, action words, mono captions are
    text-transform:uppercase in the mockups; dynamic labels come out right without [UPPERCASE])
  * vertical metrics normalised (LESSONS round 3 Void): Kodi puts the baseline max(head.yMax, hhea.ascender)
    below the line top and pitches lines at linespacing x (asc - desc + gap).
      Bricolage 930 / -270 = 1.20 em  (accented capitals reach 888, descenders -180)
      Plex Mono 1025 / -275 = 1.30 em (accented capitals 949, descenders -212)
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
UP = HERE / "fontsrc"
OUT = HERE.parent / "fonts"

VF = UP / "BricolageGrotesque-VF.ttf"
MONO_R = UP / "IBMPlexMono-Regular.ttf"
MONO_M = UP / "IBMPlexMono-Medium.ttf"
MONO_S = UP / "IBMPlexMono-SemiBold.ttf"

# output, source, axes (None = static), tracking /1000 em, caps, family, style, metrics
BRIC = (930, -270)
PLEX = (1025, -275)
JOBS = [
    # display titles: 800 at opsz 96, -.04em (Home 132 px -.035, spread 158 px -.045)
    ("FoldDisplay-ExtraBold.ttf", VF, {"opsz": 96, "wght": 800, "wdth": 100}, -40, False, "Fold Display", "ExtraBold", BRIC),
    # headings 50-64 px 700/800 -.025em (episode line, show title)
    ("FoldHead-Bold.ttf", VF, {"opsz": 60, "wght": 700, "wdth": 100}, -25, False, "Fold Head", "Bold", BRIC),
    # taglines 300 at 32-34 px
    ("FoldText-Light.ttf", VF, {"opsz": 32, "wght": 300, "wdth": 100}, -5, False, "Fold Text", "Light", BRIC),
    # body 400 at 22-26 px
    ("FoldText-Regular.ttf", VF, {"opsz": 24, "wght": 400, "wdth": 100}, 0, False, "Fold Text", "Regular", BRIC),
    # names / card titles 600, -.01em
    ("FoldText-SemiBold.ttf", VF, {"opsz": 24, "wght": 600, "wdth": 100}, -8, False, "Fold Text", "SemiBold", BRIC),
    # die-cut tabs: 600, +.06em, uppercase
    ("FoldTab-SemiBold.ttf", VF, {"opsz": 24, "wght": 600, "wdth": 100}, 60, True, "Fold Tab", "SemiBold", BRIC),
    # action words PLAY · TRAILER · MORE: 800, +.01em, uppercase
    ("FoldWord-ExtraBold.ttf", VF, {"opsz": 40, "wght": 800, "wdth": 100}, 10, True, "Fold Word", "ExtraBold", BRIC),
    # mono captions: Plex Mono, +.12em, uppercase (rowheads .14, facts .08, meta .08: one tracked voice)
    ("FoldCaps-Regular.ttf", MONO_R, None, 120, True, "Fold Caps", "Regular", PLEX),
    ("FoldCaps-SemiBold.ttf", MONO_S, None, 120, True, "Fold Caps", "SemiBold", PLEX),
    # mono meta lines (22 px, .06-.08em), uppercase
    ("FoldMeta-Regular.ttf", MONO_R, None, 70, True, "Fold Meta", "Regular", PLEX),
    # numbers: clock 38 .02em, card feet 20 .04em, runtimes; mixed case ("watched")
    ("FoldNum-Medium.ttf", MONO_M, None, 30, False, "Fold Num", "Medium", PLEX),
    ("FoldNum-Regular.ttf", MONO_R, None, 20, False, "Fold Num", "Regular", PLEX),
]


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


def set_metrics(font: TTFont, asc: int, desc: int) -> None:
    hhea, os2, head = font["hhea"], font["OS/2"], font["head"]
    hhea.ascent, hhea.descent, hhea.lineGap = asc, desc, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, desc, 0
    os2.usWinAscent, os2.usWinDescent = asc, -desc
    os2.fsSelection |= 1 << 7
    head.yMax, head.yMin = asc, desc


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style}"
    for rec in list(names.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(family, 1, pid, eid, lid)
        names.setName(style, 2, pid, eid, lid)
        names.setName(f"{ps};skin.fold", 3, pid, eid, lid)
        names.setName(f"{family} {style}", 4, pid, eid, lid)
        names.setName(ps, 6, pid, eid, lid)
    names.setName(note, 10, 3, 1, 0x409)


def build(out, src, axes, trk, caps, family, style, metrics):
    font = TTFont(src)
    if axes:
        font = instancer.instantiateVariableFont(font, axes, updateFontNames=False)
    for t in ("STAT", "fvar", "gvar", "avar", "HVAR", "MVAR", "cvar"):
        if t in font:
            del font[t]
    track(font, trk)
    if caps:
        caps_cmap(font)
    set_metrics(font, *metrics)
    rename(font, family, style,
           f"Derived from {src.name} ({axes or 'static'}) for skin.fold: tracking {trk:+d}/1000 em, "
           f"{'uppercase cmap, ' if caps else ''}metrics {metrics}. SIL Open Font License 1.1.")
    font.save(OUT / out)
    print(f"{out:28s} {axes or 'static'} tracking {trk:+d}{' caps' if caps else ''}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for job in JOBS:
        build(*job)
    shutil.copy(UP / "OFL-Bricolage.txt", OUT / "OFL-BricolageGrotesque.txt")
    shutil.copy(UP / "OFL-IBMPlexMono.txt", OUT / "OFL-IBMPlexMono.txt")


if __name__ == "__main__":
    main()
