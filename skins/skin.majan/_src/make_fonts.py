"""Generate Majan's tracked font derivatives (reproducible).

Kodi's Font.xml has no letter-spacing control, but the Index design depends on
it: display titles are set tight (-0.04em) and JetBrains Mono caps labels are
tracked out (+0.10em). We bake that tracking into the advance widths, exactly
like CSS letter-spacing (space is added/removed after every glyph; outlines
are untouched, kerning/GPOS is preserved).

Inputs (upstream static TTFs, already in ../fonts):
    HankenGrotesk-ExtraBold.ttf  -> MajanDisplay-ExtraBold.ttf  (-40/1000 em)
    JetBrainsMono-Regular.ttf    -> MajanMono-Regular.ttf       (+100/1000 em)

Both upstreams are SIL OFL 1.1 with no Reserved Font Name; the derivatives are
renamed anyway (good OFL practice) and remain OFL (see fonts/OFL-*.txt).

Usage:  python skins/skin.majan/_src/make_fonts.py
Needs:  fontTools (pip install fonttools)
"""
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"

JOBS = [
    # (source, output, tracking in font units per 1000 em, new family, style)
    ("HankenGrotesk-ExtraBold.ttf", "MajanDisplay-ExtraBold.ttf", -40, "Majan Display", "ExtraBold"),
    ("JetBrainsMono-Regular.ttf", "MajanMono-Regular.ttf", 100, "Majan Mono", "Regular"),
]


def track(src: Path, dst: Path, units_per_1000: int, family: str, style: str) -> None:
    font = TTFont(src)
    upm = font["head"].unitsPerEm
    delta = round(units_per_1000 * upm / 1000)
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv == 0:  # combining marks / zero-width: leave alone
            continue
        hmtx[name] = (max(1, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())
    # Tracked mono advances stay uniform, so post.isFixedPitch remains valid.

    ps_family = family.replace(" ", "")
    full = f"{family} {style}"
    ps = f"{ps_family}-{style}"
    names = font["name"]
    for rec in list(names.names):
        nid = rec.nameID
        if nid in (1, 16):
            names.setName(family, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (2, 17):
            names.setName(style if nid == 17 else rec.toUnicode(), nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 3:
            names.setName(f"{ps};majan-tracked{units_per_1000:+d}", nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 4:
            names.setName(full, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid == 6:
            names.setName(ps, nid, rec.platformID, rec.platEncID, rec.langID)
        elif nid in (21, 22):
            names.removeNames(nameID=nid)
    note = (f"Modified for skin.majan: tracking {units_per_1000:+d}/1000 em baked into advance widths. "
            f"Derived from {src.name}. Licensed under the SIL Open Font License 1.1.")
    names.setName(note, 10, 3, 1, 0x409)
    font.save(dst)
    print(f"{src.name} -> {dst.name}  tracking {delta:+d} units")


def main() -> None:
    for src, dst, t, fam, style in JOBS:
        track(FONTS / src, FONTS / dst, t, fam, style)


if __name__ == "__main__":
    main()
