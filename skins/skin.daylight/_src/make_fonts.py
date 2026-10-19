"""Generate Daylight's static font instances (reproducible).

Kodi cannot select variable-font axes, so the upstream variable TTFs from
google/fonts (in _src/fontsrc, SIL OFL 1.1) are instanced into static files
with fontTools.varLib.instancer, and tracking (CSS letter-spacing) is baked
into the advance widths where the mockups use it.

    Fraunces[SOFT,WONK,opsz,wght] -> DaylightDisplay-Medium.ttf  SOFT 100, WONK 0, opsz 96, wght 500, -12/1000 em
                                  -> DaylightSerif-Medium.ttf    SOFT 100, WONK 0, opsz 30, wght 500
    Figtree[wght]                 -> Figtree-Regular/Medium/SemiBold/Bold.ttf (400/500/600/700)

Usage:  python skins/skin.daylight/_src/make_fonts.py
Needs:  fontTools (pip install fonttools)
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
SRC = HERE / "fontsrc"
FONTS = HERE.parent / "fonts"

JOBS = [
    # source, output, axes, tracking per 1000 em, family, style
    ("Fraunces-VF.ttf", "DaylightDisplay-Medium.ttf", {"SOFT": 100, "WONK": 0, "opsz": 96, "wght": 500}, -12, "Daylight Display", "Medium"),
    ("Fraunces-VF.ttf", "DaylightSerif-Medium.ttf", {"SOFT": 100, "WONK": 0, "opsz": 30, "wght": 500}, 0, "Daylight Serif", "Medium"),
    ("Figtree-VF.ttf", "Figtree-Regular.ttf", {"wght": 400}, 0, "Figtree", "Regular"),
    ("Figtree-VF.ttf", "Figtree-Medium.ttf", {"wght": 500}, 0, "Figtree Medium", "Regular"),
    ("Figtree-VF.ttf", "Figtree-SemiBold.ttf", {"wght": 600}, 0, "Figtree SemiBold", "Regular"),
    ("Figtree-VF.ttf", "Figtree-Bold.ttf", {"wght": 700}, 0, "Figtree", "Bold"),
]


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    ps = f"{family.replace(' ', '')}-{style}"
    names = font["name"]
    for nid in (16, 17, 21, 22, 25):
        names.removeNames(nameID=nid)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        names.setName(family, 1, pid, eid, lid)
        names.setName(style, 2, pid, eid, lid)
        names.setName(f"{ps};daylight", 3, pid, eid, lid)
        names.setName(f"{family} {style}" if style != "Regular" else family, 4, pid, eid, lid)
        names.setName(ps, 6, pid, eid, lid)
    names.setName(note, 10, 3, 1, 0x409)


def track(font: TTFont, units_per_1000: int) -> None:
    if not units_per_1000:
        return
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv:
            hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def main() -> None:
    FONTS.mkdir(exist_ok=True)
    for src, dst, axes, trk, fam, style in JOBS:
        vf = TTFont(SRC / src)
        st = instancer.instantiateVariableFont(vf, axes, updateFontNames=False)
        track(st, trk)
        rename(st, fam, style, f"Static instance for skin.daylight ({axes}, tracking {trk:+d}/1000 em) of {src}. SIL Open Font License 1.1.")
        st.save(FONTS / dst)
        print(f"{src} {axes} -> {dst}")
    for lic in ("OFL-Fraunces.txt", "OFL-Figtree.txt"):
        shutil.copy(SRC / lic, FONTS / lic)


if __name__ == "__main__":
    main()
