"""Generate Duotone's static fonts (reproducible).

Kodi can't pick variable-font axes and Font.xml has no letter-spacing, so:
  * Inter Tight (variable, wght axis) is instanced to static 500 and 700.
  * The caption style of the mockups (.lb: Inter Tight 700, uppercase, letter-spacing .14em)
    is baked into a tracked derivative "Duotone Caps" (+140/1000 em on every advance).
  * A lightly tracked derivative "Duotone Caps Tight" (+60/1000) for long caps labels.
  * Anton is static upstream; copied unchanged.

Inputs: _src/fontsrc/ (upstream google/fonts files, SIL OFL 1.1, no Reserved Font Name)
Outputs: fonts/  (+ the OFL licence files)

Usage:  python skins/skin.duotone/_src/make_fonts.py      (needs fonttools)
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
SRC = HERE / "fontsrc"
FONTS = HERE.parent / "fonts"


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    ps = f"{family.replace(' ', '')}-{style}"
    names = font["name"]
    for rec in list(names.names):
        nid = rec.nameID
        if nid in (1, 16):
            names.setName(family, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (2, 17):
            names.setName(style, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 3:
            names.setName(f"{ps};duotone", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 4:
            names.setName(f"{family} {style}", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 6:
            names.setName(ps, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (21, 22, 25):
            names.removeNames(nameID=nid)
    names.setName(note, 10, 3, 1, 0x409)


def track(font: TTFont, units_per_1000: int) -> None:
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv == 0:
            continue
        hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def static_inter(weight: int) -> TTFont:
    vf = TTFont(SRC / "InterTight-wght.ttf")
    return instancer.instantiateVariableFont(vf, {"wght": weight}, updateFontNames=False)


def main() -> None:
    FONTS.mkdir(exist_ok=True)
    jobs = [
        # weight, tracking, family, style, output
        (500, 0, "Inter Tight", "Medium", "InterTight-Medium.ttf"),
        (700, 0, "Inter Tight", "Bold", "InterTight-Bold.ttf"),
        (700, 140, "Duotone Caps", "Bold", "DuotoneCaps-Bold.ttf"),
        (700, 60, "Duotone Caps Tight", "Bold", "DuotoneCapsTight-Bold.ttf"),
    ]
    for weight, trk, fam, style, out in jobs:
        f = static_inter(weight)
        if trk:
            track(f, trk)
        note = (f"Static instance (wght {weight}) of Inter Tight"
                + (f", tracking +{trk}/1000 em baked into advances" if trk else "")
                + " for skin.duotone. SIL Open Font License 1.1.")
        rename(f, fam, style, note)
        f.save(FONTS / out)
        print("wrote", out)
    shutil.copy(SRC / "Anton-Regular.ttf", FONTS / "Anton-Regular.ttf")
    shutil.copy(SRC / "OFL-Anton.txt", FONTS / "OFL-Anton.txt")
    shutil.copy(SRC / "OFL-InterTight.txt", FONTS / "OFL-InterTight.txt")
    for fn in ("Anton-Regular.ttf", "InterTight-Medium.ttf"):
        t = TTFont(FONTS / fn)
        h, o = t["hhea"], t["OS/2"]
        upm = t["head"].unitsPerEm
        print(fn, "upm", upm, "hhea", h.ascent, h.descent, h.lineGap, "natural", round((h.ascent - h.descent + h.lineGap) / upm, 4),
              "capH", getattr(o, "sCapHeight", None), "win", o.usWinAscent, o.usWinDescent)


if __name__ == "__main__":
    main()
