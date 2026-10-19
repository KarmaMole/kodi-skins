"""Build Nocturne's font files (reproducible).  python skins/skin.nocturne/_src/make_fonts.py

Upstream (SIL OFL 1.1, google/fonts ofl/cormorant + ofl/intertight, in _src/fontsrc/, excluded from the zip):
    Cormorant-VF.ttf, Cormorant-Italic-VF.ttf   (wght 300-700)
    InterTight-VF.ttf                           (wght 100-900)

Kodi can't pick variable axes and Font.xml has no letter-spacing, so every face the mockups use is a
static derivative (weight instanced, CSS letter-spacing baked into the advances, /1000 em):
    serif   Cormorant Italic 600     0   titles, plaques            (.plaque .t, wall-label title)
    serifi  Cormorant Italic 500     0   "With Ralph Fiennes..."
    serifr  Cormorant 500            0   "Wes Anderson, 2014"
    sans    Inter Tight 400 / 500    0   body, names
    caps    Inter Tight 500       +200   labels (.caps 20px / 4px), uppercase cmap
    nav     Inter Tight 500       +250   cornice words (24px / 6px), uppercase cmap
    capss   Inter Tight 600       +120   plaque meta (20px / 2.4px), uppercase cmap
    btn     Inter Tight 600       +230   rail words (22px / 5px), uppercase cmap
    clock   Inter Tight 500        +65   clock (30px / 2px)
Vertical metrics are normalised (LESSONS, Void): Kodi puts the baseline max(head.yMax, hhea.ascender) below the
line top and pitches lines at linespacing x (asc - desc).  Both families end up at ~1.21 em per line:
    Cormorant  924 / -287 (/1000)      Inter Tight 1984 / -494 (/2048)
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
UP = HERE / "fontsrc"
OUT = HERE.parent / "fonts"
SERIF, SERIF_I, SANS = UP / "Cormorant-VF.ttf", UP / "Cormorant-Italic-VF.ttf", UP / "InterTight-VF.ttf"
METRICS = {SERIF: (924, -287), SERIF_I: (924, -287), SANS: (1984, -494)}

JOBS = [  # output, source, wght, tracking /1000 em, caps, family, style
    ("NocturneSerif-SemiBoldItalic.ttf", SERIF_I, 600, 0, False, "Nocturne Serif", "SemiBold Italic"),
    ("NocturneSerif-MediumItalic.ttf", SERIF_I, 500, 0, False, "Nocturne Serif", "Medium Italic"),
    ("NocturneSerif-Medium.ttf", SERIF, 500, 0, False, "Nocturne Serif", "Medium"),
    ("NocturneSans-Regular.ttf", SANS, 400, 0, False, "Nocturne Sans", "Regular"),
    ("NocturneSans-Medium.ttf", SANS, 500, 0, False, "Nocturne Sans", "Medium"),
    ("NocturneCaps-Medium.ttf", SANS, 500, 200, True, "Nocturne Caps", "Medium"),
    ("NocturneNav-Medium.ttf", SANS, 500, 250, True, "Nocturne Nav", "Medium"),
    ("NocturneCapsSemi-SemiBold.ttf", SANS, 600, 120, True, "Nocturne Caps Semi", "SemiBold"),
    ("NocturneButton-SemiBold.ttf", SANS, 600, 230, True, "Nocturne Button", "SemiBold"),
    ("NocturneClock-Medium.ttf", SANS, 500, 65, False, "Nocturne Clock", "Medium"),
]


def track(font, per_1000):
    upm = font["head"].unitsPerEm
    delta = round(per_1000 * upm / 1000)
    if not delta:
        return
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv:
            hmtx[name] = (adv + delta, lsb)
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


def set_metrics(font, asc, desc):
    hhea, os2, head = font["hhea"], font["OS/2"], font["head"]
    hhea.ascent, hhea.descent, hhea.lineGap = asc, desc, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, desc, 0
    os2.usWinAscent, os2.usWinDescent = asc, -desc
    os2.fsSelection |= 1 << 7
    head.yMax, head.yMin = asc, desc


def rename(font, family, style, note):
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style.replace(' ', '')}"
    for rec in list(names.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            names.removeNames(nameID=rec.nameID)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(family, 1, pid, eid, lid)
        names.setName(style, 2, pid, eid, lid)
        names.setName(f"{ps};nocturne", 3, pid, eid, lid)
        names.setName(f"{family} {style}", 4, pid, eid, lid)
        names.setName(ps, 6, pid, eid, lid)
    names.setName(note, 10, 3, 1, 0x409)


def build(out, src, wght, trk, caps, family, style):
    font = instancer.instantiateVariableFont(TTFont(src), {"wght": wght}, updateFontNames=False)
    for t in ("STAT", "fvar", "gvar", "avar", "HVAR", "MVAR"):
        if t in font:
            del font[t]
    track(font, trk)
    if caps:
        caps_cmap(font)
    set_metrics(font, *METRICS[src])
    rename(font, family, style, f"Derived from {src.name} (wght {wght}) for skin.nocturne: tracking {trk:+d}/1000 em"
           f"{', uppercase cmap' if caps else ''}. SIL Open Font License 1.1.")
    font.save(OUT / out)
    print(f"{out:36s} wght {wght} tracking {trk:+d}{' caps' if caps else ''}")


def main():
    OUT.mkdir(exist_ok=True)
    for job in JOBS:
        build(*job)
    shutil.copy(UP / "OFL-Cormorant.txt", OUT / "OFL-Cormorant.txt")
    shutil.copy(UP / "OFL-InterTight.txt", OUT / "OFL-InterTight.txt")


if __name__ == "__main__":
    main()
