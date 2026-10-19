"""Generate skins/skin.void/1080i/Font.xml from one table (docs/skin.void/DESIGN.md, type scale).

Two fontsets with identical names (Kodi has no per-glyph fallback):
  * "Default" - Void's Instrument Serif / Instrument Sans derivatives (_src/make_fonts.py)
  * "Arial"   - Kodi's bundled arial.ttf, selectable for scripts the Instrument faces don't cover.

Line spacing: Void fonts have normalised metrics (serif 1.04 em, sans 1.20 em per line at
linespacing 1.0, see make_fonts.py), so linespacing = CSS line-height / 1.04 (serif) or / 1.20 (sans).

Usage:  python skins/skin.void/_src/make_fontxml.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Font.xml"

DISP = "VoidSerifDisplay-Regular.ttf"   # -0.026 em, 112 px and up
TITLE = "VoidSerifTitle-Regular.ttf"    # -0.014 em, 52-104 px
SERIF = "VoidSerif-Regular.ttf"         # -0.004 em, up to 48 px
REG = "VoidSans-Regular.ttf"
MED = "VoidSans-Medium.ttf"
SEMI = "VoidSans-SemiBold.ttf"
NUM = "VoidNum-Regular.ttf"             # tabular figures, +0.03 em
CAPS = "VoidCaps-Medium.ttf"            # +0.23 em, small-caps labels
CAPSW = "VoidCapsWide-Medium.ttf"       # +0.32 em, years / kickers

# name, file, size, linespacing (None = 1.0), style
FONTS = [
    ("font13", REG, 26, None, None),
    # ---- serif display / titles ------------------------------------------------------
    ("serif_172", DISP, 172, None, None),     # Home title (CSS line-height 1.04)
    ("serif_132", DISP, 132, None, None),     # rotary index, focused row
    ("serif_120", DISP, 120, None, None),     # info page title
    ("serif_104", TITLE, 104, None, None),    # fitted titles (Home / rotary step-down)
    ("serif_96", TITLE, 96, None, None),      # music now playing, search
    ("serif_80", TITLE, 80, None, None),
    ("serif_72", TITLE, 72, None, None),      # dialogs heading, keyboard line
    ("serif_68", TITLE, 68, None, None),      # rotary d1
    ("serif_64", TITLE, 64, None, None),      # OSD title
    ("serif_56", TITLE, 56, None, None),      # wall title
    ("serif_52", TITLE, 52, None, None),      # rotary d2
    ("serif_48", SERIF, 48, 1.06, None),      # Home neighbours (CSS 1.1)
    ("serif_44", SERIF, 44, None, None),      # focused row in dialogs / settings
    ("serif_42", SERIF, 42, None, None),      # rotary d3
    ("serif_40", SERIF, 40, None, None),
    ("serif_36", SERIF, 36, None, None),
    ("serif_35", SERIF, 35, None, None),      # rotary d4
    ("serif_32", SERIF, 32, None, None),
    ("serif_30", SERIF, 30, None, None),      # rotary d5
    ("serif_26", SERIF, 26, None, None),      # rotary d6
    ("serif_24", SERIF, 24, None, None),      # rotary d7
    # ---- sans ---------------------------------------------------------------------------
    ("sans_28", REG, 28, 1.25, None),         # plot (CSS 1.5)
    ("sans_26", REG, 26, 1.25, None),         # meta line, body
    ("sans_24", REG, 24, 1.25, None),         # small body, numbers in text
    ("sans_22", REG, 22, 1.2, None),
    ("sans_20", REG, 20, 1.2, None),
    ("sans_28_med", MED, 28, None, None),     # unfocused rows in dialogs / settings
    ("sans_26_med", MED, 26, None, None),
    ("sans_24_med", MED, 24, None, None),
    ("sans_22_med", MED, 22, None, None),
    ("sans_20_med", MED, 20, None, None),     # letter scrubber
    ("sans_22_semi", SEMI, 22, None, None),   # letter scrubber, active
    ("sans_26_semi", SEMI, 26, None, None),
    # ---- caps (uppercase by style) -------------------------------------------------------
    ("caps_20", CAPS, 20, None, "uppercase"),
    ("caps_22", CAPS, 22, None, "uppercase"),
    ("caps_24", CAPS, 24, None, "uppercase"),
    ("capsw_20", CAPSW, 20, None, "uppercase"),
    # ---- numerals (tabular) --------------------------------------------------------------
    ("num_20", NUM, 20, None, None),
    ("num_22", NUM, 22, None, None),
    ("num_24", NUM, 24, None, None),
    ("num_26", NUM, 26, None, None),
    ("num_32", NUM, 32, None, None),
    ("num_48", NUM, 48, None, None),
    # ---- legacy slot names (engine files inherited from Majan); same faces, Void scale ----
    ("display_100", TITLE, 100, None, None),
    ("display_92", TITLE, 92, None, None),
    ("display_72", TITLE, 72, None, None),
    ("display_68", TITLE, 68, None, None),
    ("display_64", TITLE, 64, None, None),
    ("display_48", SERIF, 48, None, None),
    ("ghost_220", DISP, 220, None, None),
    ("header_34", SERIF, 40, None, None),
    ("clock_34", NUM, 32, None, None),
    ("stat_30", NUM, 30, None, None),
    ("title_28_bold", SEMI, 28, None, None),
    ("title_28_medium", MED, 28, None, None),
    ("title_28_semibold", SEMI, 28, None, None),
    ("menu_26_bold", MED, 26, None, None),
    ("menu_26_medium", MED, 26, None, None),
    ("body_26", REG, 26, 1.25, None),
    ("body_25", REG, 25, 1.25, None),
    ("label_25_semibold", MED, 25, None, None),
    ("label_25_bold", SEMI, 25, None, None),
    ("section_24", MED, 24, None, None),
    ("body_23", REG, 24, 1.25, None),
    ("button_23_bold", MED, 24, None, None),
    ("button_23_semibold", MED, 24, None, None),
    ("credits_22", REG, 22, None, None),
    ("credits_21", REG, 22, None, None),
    ("credits_21_semibold", MED, 22, None, None),
    ("card_21_bold", MED, 22, None, None),
    ("card_21_medium", MED, 22, None, None),
    ("card_21", REG, 22, None, None),
    ("small_19_bold", MED, 20, None, None),
    ("small_19", REG, 20, 1.2, None),
    ("small_16", REG, 20, None, None),
    ("mono_17", CAPS, 20, None, "uppercase"),
    ("mono_15", CAPS, 20, None, "uppercase"),
    ("mono_14", CAPS, 20, None, "uppercase"),
    ("mono_13", CAPS, 20, None, "uppercase"),
    ("num_16", NUM, 20, None, None),
    ("num_14", NUM, 20, None, None),
    ("tab_13", NUM, 20, None, None),
    # ---- Estuary names for third-party script windows ------------------------------------
    ("font10", REG, 22, None, None),
    ("font12", REG, 24, None, None),
    ("font14", REG, 28, None, None),
    ("font27", REG, 27, None, None),
    ("font30", MED, 30, None, None),
    ("font37", SERIF, 40, None, None),
    ("font45", TITLE, 52, None, None),
    ("font52_title", TITLE, 56, None, None),
    ("font45_title", TITLE, 52, None, None),
    ("font36_title", SERIF, 40, None, None),
    ("font30_title", SERIF, 32, None, None),
    ("font25_title", MED, 26, None, None),
    ("Mono26", NUM, 26, None, None),
]


def font_xml(name, filename, size, ls, style):
    parts = [f"<name>{name}</name>", f"<filename>{filename}</filename>", f"<size>{size}</size>"]
    if ls is not None:
        parts.append(f"<linespacing>{ls}</linespacing>")
    if style:
        parts.append(f"<style>{style}</style>")
    return "\t\t<font>" + "".join(parts) + "</font>"


def main():
    names = [f[0] for f in FONTS]
    assert len(names) == len(set(names)), "duplicate font name"
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- GENERATED by _src/make_fontxml.py - edit the table there, not this file. -->",
        "<!-- Type scale: docs/skin.void/DESIGN.md. Licences: fonts/OFL-*.txt -->",
        "<fonts>",
        '\t<fontset id="Default" idloc="31900">',
    ]
    out += [font_xml(*f) for f in FONTS]
    out += ["\t</fontset>", "\t<!-- Fallback set: same names, Kodi's bundled arial.ttf (wider script coverage). -->",
            '\t<fontset id="Arial" idloc="31901">']
    for name, _file, size, ls, style in FONTS:
        out.append(font_xml(name, "arial.ttf", size, ls, style))
    out += ["\t</fontset>", "</fonts>", ""]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT} ({len(FONTS)} fonts per set)")


if __name__ == "__main__":
    main()
