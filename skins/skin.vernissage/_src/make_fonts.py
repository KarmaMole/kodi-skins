"""Build Vernissage's font files (reproducible) and check their glyphs.   python skins/skin.vernissage/_src/make_fonts.py

Source (SIL OFL 1.1): the static instances visual-designer made from the Google Fonts variable fonts
(docs/skin.vernissage/mockups/_src/make_assets.py static_fonts(): Inter Tight wght 400 / 500 / 600, Fraunces opsz 72
wght 360 / italic wght 340, SOFT 30, WONK 0) in docs/skin.vernissage/mockups/_src/fonts/static/. Kodi draws only
the default instance of a variable font, so static files are required (DESIGN 4).

Font.xml has no letter-spacing (LESSONS 3), so the boards' CSS tracking is baked into the advance widths here
(per 1000 em, the mockup values rounded to one per file): Fraunces-Display -10 (display -12 / exhibit -8),
Fraunces-DisplayItalic -8, InterTight-SemiBold -5 (placard titles), InterTight-Medium +10 (labels; the clock's +20 is
not worth a sixth file), InterTight-Regular 0. Vertical metrics are left as shipped (see CONVENTIONS 5 for the
numbers Kodi uses: baseline = max(head.yMax, ascender), line pitch = ascender - descender).
Glyph check: every character the skin prints literally (GLYPHS) must exist in every face that may print it; the
report also answers SPEC M1 probe "star glyph" (U+2605 in Inter Tight).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT.parents[1] / "docs" / "skin.vernissage" / "mockups" / "_src" / "fonts"
STATIC = SRC / "static"
OUT = ROOT / "fonts"

JOBS = [  # file (same name in and out), tracking /1000 em, family name written into the font
    ("InterTight-Regular.ttf", 0, "Vernissage Inter Tight Regular"),
    ("InterTight-Medium.ttf", 10, "Vernissage Inter Tight Medium"),
    ("InterTight-SemiBold.ttf", -5, "Vernissage Inter Tight SemiBold"),
    ("Fraunces-Display.ttf", -10, "Vernissage Fraunces Display"),
    ("Fraunces-DisplayItalic.ttf", -8, "Vernissage Fraunces Display Italic"),
]
LICENCES = [("OFL-intertight.txt", "OFL-intertight.txt"), ("OFL-fraunces.txt", "OFL-fraunces.txt")]

# characters the XML / strings print literally: middle dot, NBSP, en dash, ellipsis, right quote, multiplication,
# the star (rating, SPEC 9 probe), e acute (Amelie), l stroke (Kieslowski)
GLYPHS = {"·": "middle dot", " ": "NBSP", "–": "en dash", "…": "ellipsis", "’": "right quote",
          "×": "times", "★": "black star", "é": "e acute", "ł": "l stroke"}
SANS_ONLY = {"★"}   # printed only in Inter Tight labels


def track(font: TTFont, per_1000: int) -> None:
    if not per_1000:
        return
    delta = round(per_1000 * font["head"].unitsPerEm / 1000)
    hmtx = font["hmtx"].metrics
    for name, (adv, lsb) in list(hmtx.items()):
        if adv:
            hmtx[name] = (max(0, adv + delta), lsb)
    font["hhea"].advanceWidthMax = max(a for a, _ in hmtx.values())


def rename(font: TTFont, family: str, note: str) -> None:
    nm = font["name"]
    ps = family.replace(" ", "")
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        nm.setName(family, 1, pid, eid, lid)
        nm.setName("Regular", 2, pid, eid, lid)
        nm.setName(f"{ps};vernissage", 3, pid, eid, lid)
        nm.setName(family, 4, pid, eid, lid)
        nm.setName(ps, 6, pid, eid, lid)
    nm.setName(note, 10, 3, 1, 0x409)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    bad = 0
    for fn, trk, family in JOBS:
        f = TTFont(STATIC / fn, recalcTimestamp=False)  # reproducible bytes
        assert "fvar" not in f, f"{fn} is still variable"
        track(f, trk)
        rename(f, family, f"Static instance of {'Inter Tight' if fn.startswith('Inter') else 'Fraunces'} for "
                          f"skin.vernissage, tracking {trk:+d}/1000 em. SIL Open Font License 1.1.")
        f.flavor = None  # LESSONS Keepsake: never save WOFF2 data as .ttf
        f.save(OUT / fn)
        cmap = TTFont(OUT / fn).getBestCmap()
        h, hd = f["hhea"], f["head"]
        upm = hd.unitsPerEm
        missing = [GLYPHS[c] for c in GLYPHS if ord(c) not in cmap and not (c in SANS_ONLY and fn.startswith("Fraunces"))]
        bad += bool(missing)
        print(f"{fn:28s} tracking {trk:+3d}  baseline {max(hd.yMax, h.ascent) / upm:.3f} em  pitch "
              f"{(h.ascent - h.descent) / upm:.3f} em  descender {-h.descent / upm:.3f} em"
              + (f"  MISSING: {', '.join(missing)}" if missing else ""))
        if fn.startswith("Inter"):
            print(f"{'':28s} star U+2605: {'present' if 0x2605 in cmap else 'ABSENT (use the rating icon)'}")
    for src, dst in LICENCES:
        shutil.copy(SRC / src, OUT / dst)
    print("glyph check:", "ok" if not bad else f"{bad} face(s) missing glyphs")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
