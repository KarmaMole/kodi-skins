"""Generate 1080i/Font.xml from one table (docs/skin.vernissage/DESIGN.md section 4, type scale).
    python skins/skin.vernissage/_src/make_fontxml.py

Two fontsets with the same names (Kodi has no glyph fallback): "Default" (Inter Tight + Fraunces, built by
make_fonts.py) and "Arial" (Kodi's bundled arial.ttf, for scripts the faces don't cover: CJK; Fraunces also lacks
Cyrillic / Greek, DESIGN 4). font13 is Kodi's hard fallback.
linespacing = the screens' budget pitch (screens/README 2) / (size x the face's natural pitch: Inter Tight 1.210 em,
Fraunces 1.233 em, make_fonts.py prints them), rounded down: Kodi's real pitch never exceeds the budget. Naming: font_<role> (CONVENTIONS 5). Nothing under 28 px (DESIGN 4: the floor).
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "1080i" / "Font.xml"

REG, MED, SEMI = "InterTight-Regular.ttf", "InterTight-Medium.ttf", "InterTight-SemiBold.ttf"
SERIF, SERIF_IT = "Fraunces-Display.ttf", "Fraunces-DisplayItalic.ttf"
PITCH = {REG: 1.21, MED: 1.21, SEMI: 1.21, SERIF: 1.233, SERIF_IT: 1.233}


def ls(face, size, budget):
    """linespacing so Kodi's real pitch (linespacing x size x natural pitch) is AT MOST the screens' budget pitch
    (docs/skin.vernissage/screens/README.md section 2; measure_placards.py --skin checks it). Rounded down."""
    return math.floor(budget / (size * PITCH[face]) * 1000) / 1000


FONTS = [  # name, file, size, linespacing (None = the face's own)
    ("font13", REG, 30, None),
    ("font_display", SERIF, 80, ls(SERIF, 80, 84)),      # info-page title (the big placard), up to 3 lines
    ("font_exhibit", SERIF, 60, ls(SERIF, 60, 66)),       # exhibition titles ("Tonight: ...", "The collection")
    ("font_exhibit_it", SERIF_IT, 60, ls(SERIF_IT, 60, 66)),  # the italic lead word (Tonight / Today), its own label
    ("font_room", SERIF_IT, 48, ls(SERIF_IT, 48, 54)),    # room names (settings, style)
    ("font_quote", SERIF_IT, 32, ls(SERIF_IT, 32, 42)),   # taglines on gallery-wall and info placards
    ("font_placard_l", SEMI, 40, ls(SEMI, 40, 49)),      # big placard title (gallery wall, listening room, OSD)
    ("font_placard_xl", SEMI, 44, ls(SEMI, 44, 51)),     # placard title, step 1 (one line, DESIGN 6)
    ("font_placard", SEMI, 36, ls(SEMI, 36, 44)),        # placard title, step 2
    ("font_placard_s", SEMI, 30, ls(SEMI, 30, 37)),      # placard title, step 3 (one line, else two)
    ("font_display_m", SERIF, 64, ls(SERIF, 64, 68)),    # info title step 2 (M3)
    ("font_display_s", SERIF, 52, ls(SERIF, 52, 56)),    # info title step 3 (M3)
    ("font_label", MED, 30, ls(MED, 30, 36)),                     # the label beside a focused icon, rows, header words
    ("font_clock", MED, 30, ls(MED, 30, 36)),                     # clock
    ("font_body", REG, 30, ls(REG, 30, 41)),           # facts, key line ("ends 11:19 pm"), hints, plots
    ("font_small", REG, 28, ls(REG, 28, 38)),          # genre / runtime lines, captions, counts (the floor)
    # Estuary names for third-party script windows (add-on dialogs ask for them by name; Kodi only falls back to
    # font13). Nothing in Vernissage uses them, so kdk lists them as unused: each line carries a kdk-ignore.
    ("font10", REG, 28, None),
    ("font12", REG, 28, None),
    ("font14", REG, 30, None),
    ("font27", REG, 30, None),
    ("font30", MED, 30, None),
    ("font37", SEMI, 40, None),
    ("font45", SEMI, 48, None),
    ("font52_title", SERIF, 56, None),
    ("font45_title", SERIF, 48, None),
    ("font36_title", SEMI, 40, None),
    ("font30_title", SEMI, 34, None),
    ("font25_title", MED, 30, None),
    ("Mono26", REG, 28, None),             # the forked DialogTextViewer (Groove's name); Inter Tight has tabular figures
]
# DESIGN 4 roles whose first window arrives in M3 / M4 (info title, room names, taglines). They stay in Font.xml so
# screens/_src/measure_placards.py --skin can check their pitch now; muted for kdk until a window uses them.
RESERVED = {"font_room": "M4 settings room names"}   # the info title fonts are used since M3
ESTUARY_ALIASES = {"font10", "font12", "font14", "font27", "font30", "font37", "font45", "font52_title",
                   "font45_title", "font36_title", "font30_title", "font25_title"}
KDK_ALIAS = " <!-- kdk-ignore: fonts; Estuary font name kept for add-on script windows -->"


def font_xml(name, filename, size, lsp):
    p = f"<name>{name}</name><filename>{filename}</filename><size>{size}</size>"
    if lsp is not None:
        p += f"<linespacing>{lsp}</linespacing>"
    note = KDK_ALIAS if name in ESTUARY_ALIASES else ""
    if name in RESERVED:
        note = f" <!-- kdk-ignore: fonts; DESIGN role reserved for {RESERVED[name]} (first use pending) -->"
    return "\t\t<font>" + p + "</font>" + note


def main():
    names = [f[0] for f in FONTS]
    assert len(names) == len(set(names)), "duplicate font name"
    assert all(s >= 28 for n, _f, s, _l in FONTS), "DESIGN 4: no text under 28 px"
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           "<!-- GENERATED by _src/make_fontxml.py - edit the table there. Licences: fonts/OFL-intertight.txt,"
           " fonts/OFL-fraunces.txt -->",
           "<fonts>", '\t<fontset id="Default" idloc="31900">']
    out += [font_xml(*f) for f in FONTS]
    out += ["\t</fontset>", '\t<fontset id="Arial" idloc="31901">']
    out += [font_xml(n, "arial.ttf", s, l) for n, _f, s, l in FONTS]
    out += ["\t</fontset>", "</fonts>", ""]
    OUT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name} ({len(FONTS)} fonts)")


if __name__ == "__main__":
    main()
