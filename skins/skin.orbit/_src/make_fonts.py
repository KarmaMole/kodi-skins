"""Generate Orbit's static font instances (reproducible).

Kodi can't select variable-font axes and Font.xml has no letter-spacing, so the
mockup styles are baked into static TTFs here:

  Archivo[wdth,wght] (google/fonts, OFL, kept in _src/fonts_src/, not shipped)
    -> OrbitWide-SemiBold.ttf    wdth 125 wght 600, tracking +10/1000   (.wd headings, uppercase)
    -> OrbitLabel-SemiBold.ttf   wdth 112 wght 600, tracking +180/1000  (.lb engraved labels)
    -> OrbitText-Regular.ttf     wdth 100 wght 400                      (body / plot)
    -> OrbitText-Medium.ttf      wdth 100 wght 500                      (list rows, names)
    -> OrbitText-SemiBold.ttf    wdth 100 wght 600                      (focused rows, buttons)
  JetBrainsMono-Regular/Medium (OFL, kept in _src/fonts_src/)
    -> OrbitMono-Regular.ttf / OrbitMono-Medium.ttf: '0' remapped to the slashed
       'zero.zero' glyph (the mockups use font-feature-settings 'zero' 1).

Usage:  python skins/skin.orbit/_src/make_fonts.py
Needs:  fontTools (pip install fonttools)
"""
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
SRC = HERE / "fonts_src"
FONTS = HERE.parent / "fonts"

VF = SRC / "Archivo-VF.ttf"

# (output, wdth, wght, tracking per 1000 em, family, style)
ARCHIVO_JOBS = [
    ("OrbitWide-SemiBold.ttf", 125, 600, 10, "Orbit Wide", "SemiBold"),
    ("OrbitLabel-SemiBold.ttf", 112, 600, 180, "Orbit Label", "SemiBold"),
    ("OrbitText-Regular.ttf", 100, 400, 0, "Orbit Text", "Regular"),
    ("OrbitText-Medium.ttf", 100, 500, 0, "Orbit Text", "Medium"),
    ("OrbitText-SemiBold.ttf", 100, 600, 0, "Orbit Text", "SemiBold"),
]
MONO_JOBS = [
    ("JetBrainsMono-Regular.ttf", "OrbitMono-Regular.ttf", "Orbit Mono", "Regular"),
    ("JetBrainsMono-Medium.ttf", "OrbitMono-Medium.ttf", "Orbit Mono", "Medium"),
]


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    ps_family = family.replace(" ", "")
    names = font["name"]
    for rec in list(names.names):
        nid = rec.nameID
        if nid in (1, 16):
            names.setName(family, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (2, 17):
            names.setName(style, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 3:
            names.setName(f"{ps_family}-{style};orbit", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 4:
            names.setName(f"{family} {style}", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 6:
            names.setName(f"{ps_family}-{style}", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (21, 22, 25):
            names.removeNames(nameID=nid)
    names.setName(note + " Licensed under the SIL Open Font License 1.1.", 10, 3, 1, 0x409)


def track(font: TTFont, units_per_1000: int) -> None:
    if not units_per_1000:
        return
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv == 0:
            continue
        hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


# Archivo has no Cyrillic. Weather add-ons on Omar's box (weather.gismeteo) return Latin words
# typed with Cyrillic homoglyphs ("Сlear" = Cyrillic Es + "lear"), which rendered as a box.
# Map the look-alike Cyrillic letters to the Latin glyphs.
HOMOGLYPHS = {
    0x0410: "A", 0x0412: "B", 0x0415: "E", 0x041A: "K", 0x041C: "M", 0x041D: "H", 0x041E: "O",
    0x0420: "P", 0x0421: "C", 0x0422: "T", 0x0425: "X", 0x0423: "Y",
    0x0430: "a", 0x0435: "e", 0x043E: "o", 0x0440: "p", 0x0441: "c", 0x0443: "y", 0x0445: "x",
    0x0455: "s", 0x0456: "i", 0x0458: "j",
}


def add_homoglyphs(font: TTFont) -> None:
    best = font.getBestCmap()
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp, latin in HOMOGLYPHS.items():
            if cp not in table.cmap and ord(latin) in best:
                table.cmap[cp] = best[ord(latin)]


def archivo() -> None:
    for out, wdth, wght, trk, family, style in ARCHIVO_JOBS:
        vf = TTFont(VF)
        inst = instancer.instantiateVariableFont(vf, {"wdth": wdth, "wght": wght}, updateFontNames=False)
        track(inst, trk)
        add_homoglyphs(inst)
        # usWidthClass / weight so Kodi's FreeType doesn't synthesize anything odd
        inst["OS/2"].usWeightClass = wght
        rename(inst, family, style,
               f"Modified for skin.orbit: static instance of Archivo (wdth {wdth}, wght {wght}), "
               f"tracking {trk:+d}/1000 em baked into advance widths.")
        inst.save(FONTS / out)
        print(f"Archivo -> {out}  wdth {wdth} wght {wght} tracking {trk:+d}")


def mono() -> None:
    for src, out, family, style in MONO_JOBS:
        font = TTFont(SRC / src)
        for table in font["cmap"].tables:
            if table.isUnicode() and ord("0") in table.cmap:
                table.cmap[ord("0")] = "zero.zero"
        rename(font, family, style,
               f"Modified for skin.orbit: '0' mapped to the slashed zero.zero glyph. Derived from {src}.")
        font.save(FONTS / out)
        print(f"{src} -> {out}  slashed zero")


if __name__ == "__main__":
    archivo()
    mono()
