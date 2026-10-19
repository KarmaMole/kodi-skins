"""Build Sentence's static font files (reproducible).

Inputs (upstream, SIL OFL 1.1, from github.com/google/fonts, kept in _src/fontsrc/):
    YoungSerif-Regular.ttf   the sentence voice (only one weight, no italic)
    Manrope[wght].ttf        UI voice, variable 200-800 (saved as Manrope-VF.ttf)

Outputs (../fonts/):
    YoungSerif-Regular.ttf           copied as is
    Manrope-Medium.ttf / -Bold.ttf   static instances (wght 500 / 700): Kodi can't pick variable axes
    SentenceCaps-Bold.ttf            Manrope 700, +140/1000 em tracking baked into advances (kicker captions)
    SentenceNum-Bold.ttf             Manrope 700 with the tnum digits mapped in cmap (clock/OSD numbers
                                     don't jitter); Kodi can't switch OpenType features itself

Usage:  python skins/skin.sentence/_src/make_fonts.py        (needs: pip install fonttools)
"""
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
SRC = HERE / "fontsrc"
OUT = HERE.parent / "fonts"


def rename(font: TTFont, family: str, style: str, note: str) -> None:
    names = font["name"]
    ps = f"{family.replace(' ', '')}-{style}"
    for rec in list(names.names):
        nid = rec.nameID
        if nid in (1, 16):
            names.setName(family, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (2, 17):
            names.setName(style, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 3:
            names.setName(f"{ps};sentence", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 4:
            names.setName(f"{family} {style}", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 6:
            names.setName(ps, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (21, 22, 25):
            names.removeNames(nameID=nid)
    names.setName(note + " Licensed under the SIL Open Font License 1.1.", 10, 3, 1, 0x409)


def static(weight: int) -> TTFont:
    vf = TTFont(SRC / "Manrope-VF.ttf")
    return instancer.instantiateVariableFont(vf, {"wght": weight}, updateFontNames=False)


def track(font: TTFont, units_per_1000: int) -> None:
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv:
            hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def tabular(font: TTFont) -> None:
    gsub = font["GSUB"].table
    subst = {}
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != "tnum":
            continue
        for li in fr.Feature.LookupListIndex:
            lk = gsub.LookupList.Lookup[li]
            for st in lk.SubTable:
                ext = getattr(st, "ExtSubTable", None)
                st = ext or st
                if hasattr(st, "mapping"):
                    subst.update(st.mapping)
    for table in font["cmap"].tables:
        for cp, g in list(table.cmap.items()):
            if g in subst:
                table.cmap[cp] = subst[g]
    print(f"  tnum: {len(subst)} glyphs remapped")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    shutil.copy(SRC / "YoungSerif-Regular.ttf", OUT / "YoungSerif-Regular.ttf")
    for w, style in ((500, "Medium"), (700, "Bold")):
        f = static(w)
        rename(f, "Manrope", style, f"Static instance wght {w} of Manrope[wght] for skin.sentence.")
        f.save(OUT / f"Manrope-{style}.ttf")
        print(f"Manrope-{style}.ttf")
    f = static(700)
    track(f, 140)
    rename(f, "Sentence Caps", "Bold", "Manrope wght 700, tracking +140/1000 em baked in, for skin.sentence.")
    f.save(OUT / "SentenceCaps-Bold.ttf")
    print("SentenceCaps-Bold.ttf")
    f = static(700)
    tabular(f)
    rename(f, "Sentence Num", "Bold", "Manrope wght 700 with tabular figures in cmap, for skin.sentence.")
    f.save(OUT / "SentenceNum-Bold.ttf")
    print("SentenceNum-Bold.ttf")
    for lic in ("OFL-YoungSerif.txt", "OFL-Manrope.txt"):
        shutil.copy(SRC / lic, OUT / lic)


if __name__ == "__main__":
    main()
