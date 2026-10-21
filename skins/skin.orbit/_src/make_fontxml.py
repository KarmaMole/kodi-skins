"""Generate skins/skin.orbit/1080i/Font.xml from one table (docs/skin.orbit/DESIGN.md section 3).

Two fontsets with identical names (Kodi has no per-glyph fallback):
  * "Default" - Orbit faces (static Archivo instances + JetBrains Mono with slashed zero)
  * "Arial"   - Kodi's bundled arial.ttf at the same sizes (Settings > Interface > Skin >
                Fonts) for titles in scripts Archivo doesn't cover.

linespacing = CSS line-height / (size x natural line height). Natural line heights
(hhea): Archivo 1.088 em, JetBrains Mono 1.32 em.

Orbit roles
  wide_*   OrbitWide (Archivo wdth 125, 600, +0.01em), uppercase - headings (.wd)
  label_*  OrbitLabel (Archivo wdth 112, 600, +0.18em), uppercase - engraved labels (.lb)
  text_*   OrbitText (Archivo wdth 100) - body, rows, names
  mono_*   OrbitMono (JetBrains Mono, slashed zero) - every number
Legacy Majan names (display_*, menu_*, mono_1x, ...) stay defined and point at Orbit
faces, so any window that still uses them renders in the Orbit language.

Usage:  python skins/skin.orbit/_src/make_fontxml.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Font.xml"

WIDE = "OrbitWide-SemiBold.ttf"
LABEL = "OrbitLabel-SemiBold.ttf"
REG = "OrbitText-Regular.ttf"
MED = "OrbitText-Medium.ttf"
SEMI = "OrbitText-SemiBold.ttf"
MONO = "OrbitMono-Regular.ttf"
MONO_M = "OrbitMono-Medium.ttf"

A = 1.088   # Archivo natural line height
M = 1.32    # JetBrains Mono natural line height


def ls(size, line_height, nat=A):
    return round(line_height / (size * nat), 3)


U = "uppercase"

# name, file, size, linespacing (None = font default), style
FONTS = [
    ("font13", REG, 26, None, None),
    # ---- wide headings (uppercase) -------------------------------------
    ("wide_84", WIDE, 84, ls(84, 96), U),
    ("wide_66", WIDE, 66, ls(66, 78), U),
    ("wide_56", WIDE, 56, ls(56, 66), U),
    ("wide_50", WIDE, 50, ls(50, 62), U),
    ("wide_44", WIDE, 44, ls(44, 54), U),
    ("wide_38", WIDE, 38, ls(38, 46), U),
    ("wide_34", WIDE, 34, ls(34, 44), U),
    ("wide_30", WIDE, 30, ls(30, 38), U),
    ("wide_26", WIDE, 26, ls(26, 32), U),
    # ---- engraved labels (uppercase, tracked) ----------------------------
    ("label_22", LABEL, 22, None, U),
    ("label_20", LABEL, 20, None, U),
    # ---- text ------------------------------------------------------------
    ("text_28", REG, 28, ls(28, 42), None),
    ("text_26", REG, 26, ls(26, 38), None),
    ("text_24", REG, 24, ls(24, 34), None),
    ("text_22", REG, 22, ls(22, 30), None),
    ("text_36_semi", SEMI, 36, ls(36, 44), None),
    ("text_30_semi", SEMI, 30, None, None),
    ("text_30_med", MED, 30, None, None),
    ("text_26_semi", SEMI, 26, None, None),
    ("text_26_med", MED, 26, None, None),
    ("text_24_med", MED, 24, None, None),
    ("text_22_med", MED, 22, None, None),
    # ---- mono numerals ---------------------------------------------------
    ("mono_80", MONO_M, 80, None, None),
    ("mono_58", MONO_M, 58, None, None),
    ("mono_50", MONO_M, 50, None, None),
    ("mono_44", MONO_M, 44, None, None),
    ("mono_40", MONO_M, 40, None, None),
    ("mono_34", MONO_M, 34, None, None),
    ("mono_30", MONO, 30, None, None),
    ("mono_26", MONO, 26, None, None),
    ("mono_22", MONO, 22, None, None),
    ("mono_20", MONO, 20, None, None),
    # ---- legacy names (Majan-derived windows) -> Orbit faces ----------------
    ("display_100", WIDE, 84, ls(84, 96), U),
    ("header_34", WIDE, 34, None, U),
    ("clock_34", MONO_M, 34, None, None),
    ("stat_30", MONO_M, 30, None, None),
    ("title_28_bold", SEMI, 28, None, None),
    ("title_28_semibold", SEMI, 28, None, None),
    ("body_25", REG, 25, ls(25, 36), None),
    ("label_25_semibold", SEMI, 25, None, None),
    ("label_25_bold", SEMI, 25, None, None),
    ("body_23", REG, 24, ls(24, 34), None),
    ("button_23_bold", LABEL, 22, None, U),
    ("button_23_semibold", LABEL, 22, None, U),
    ("credits_21", REG, 22, None, None),
    ("credits_21_semibold", SEMI, 22, None, None),
    ("card_21_bold", SEMI, 22, None, None),
    ("card_21_medium", MED, 22, None, None),
    ("card_21", REG, 22, None, None),
    ("small_19_bold", SEMI, 20, None, None),
    ("small_19", REG, 20, ls(20, 28), None),
    ("small_16", REG, 20, None, None),
    ("mono_15", LABEL, 20, None, U),
    ("mono_14", LABEL, 20, None, U),
    ("mono_13", LABEL, 20, None, U),
    ("num_16", MONO, 20, None, None),
    ("num_14", MONO, 20, None, None),
    # ---- Estuary-name aliases for third-party script windows ----------------
    ("font10", REG, 22, None, None),
    ("font12", REG, 24, None, None),
    ("font14", REG, 28, None, None),
    ("font27", REG, 27, None, None),
    ("font30", SEMI, 30, None, None),
    ("font37", SEMI, 37, None, None),
    ("font45", SEMI, 45, None, None),
    ("font52_title", WIDE, 46, None, U),
    ("font45_title", WIDE, 40, None, U),
    ("font36_title", WIDE, 32, None, U),
    ("font30_title", WIDE, 28, None, U),
    ("font25_title", WIDE, 24, None, U),
    ("Mono26", MONO, 26, None, None),
]


# Estuary font names kept for third-party script windows (add-on dialogs ask for them by name; Kodi only falls
# back to font13). kdk (the Kodi repository review bot) reports them as unused: each line carries a kdk-ignore.
ESTUARY_ALIASES = {"font10", "font12", "font14", "font27", "font30", "font37", "font45", "font52_title",
                   "font45_title", "font36_title", "font30_title", "font25_title"}
KDK_ALIAS = " <!-- kdk-ignore: fonts; Estuary font name kept for add-on script windows -->"


def font_xml(name, filename, size, lsp, style):
    parts = [f"<name>{name}</name>", f"<filename>{filename}</filename>", f"<size>{size}</size>"]
    if lsp is not None:
        parts.append(f"<linespacing>{lsp}</linespacing>")
    if style:
        parts.append(f"<style>{style}</style>")
    return "\t\t<font>" + "".join(parts) + "</font>" + (KDK_ALIAS if name in ESTUARY_ALIASES else "")


def main():
    names = [f[0] for f in FONTS]
    assert len(names) == len(set(names)), "duplicate font name"
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- GENERATED by _src/make_fontxml.py - edit the table there, not this file. -->",
        "<!-- Type scale: docs/skin.orbit/DESIGN.md section 3. Licences: fonts/OFL-*.txt -->",
        "<fonts>",
        '\t<fontset id="Default" idloc="31900">',
    ]
    out += [font_xml(*f) for f in FONTS]
    out += ["\t</fontset>", "\t<!-- Fallback set: same names, Kodi's bundled arial.ttf (wider script coverage). -->",
            '\t<fontset id="Arial" idloc="31901">']
    for name, _file, size, lsp, style in FONTS:
        out.append(font_xml(name, "arial.ttf", size, lsp, style))
    out += ["\t</fontset>", "</fonts>", ""]
    OUT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(FONTS)} fonts per set)")


if __name__ == "__main__":
    main()
