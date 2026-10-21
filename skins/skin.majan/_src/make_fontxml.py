"""Generate skins/skin.majan/1080i/Font.xml from one table (DESIGN.md section 4.3).

Why a generator: Majan ships TWO fontsets that must define exactly the same
names (Kodi has no per-glyph fallback):
  * "Default" - Hanken Grotesk / JetBrains Mono / the tracked Majan derivatives
  * "Arial"   - Kodi's bundled arial.ttf at the same sizes, selectable in
                Settings > Interface > Skin > Fonts for titles in scripts the
                Majan fonts don't cover (Arabic, CJK...). Estuary pattern.
Editing the table below and re-running keeps both sets in sync.

Usage:  python skins/skin.majan/_src/make_fontxml.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Font.xml"

DISPLAY = "MajanDisplay-ExtraBold.ttf"
REG = "HankenGrotesk-Regular.ttf"
MED = "HankenGrotesk-Medium.ttf"
SEMI = "HankenGrotesk-SemiBold.ttf"
BOLD = "HankenGrotesk-Bold.ttf"
MONO_T = "MajanMono-Regular.ttf"       # tracked +0.10em, captions (uppercase)
MONO = "JetBrainsMono-Regular.ttf"     # numerals, times, codes
MONO_M = "JetBrainsMono-Medium.ttf"    # poster tabs

# name, file, size, linespacing (None = font default), style (None = normal)
FONTS = [
    # --- Kodi-required fallback (must exist) -------------------------------
    ("font13", REG, 25, None, None),
    # --- display (MajanDisplay = Hanken 800 with -0.04em tracking) ---------
    ("display_100", DISPLAY, 100, 0.74, None),
    ("display_92", DISPLAY, 92, 0.71, None),
    ("display_72", DISPLAY, 72, 0.73, None),
    ("display_68", DISPLAY, 68, 0.73, None),
    ("display_64", DISPLAY, 64, 0.73, None),
    ("ghost_220", DISPLAY, 220, None, None),
    ("header_34", DISPLAY, 34, None, None),
    ("display_56", DISPLAY, 56, None, None),      # Poster wall info card title (1 line)
    ("display_48", DISPLAY, 48, 0.75, None),
    # --- Hanken Grotesk ------------------------------------------------------
    ("clock_34", SEMI, 34, None, None),
    ("stat_30", SEMI, 30, None, None),
    ("title_28_bold", BOLD, 28, None, None),
    ("title_28_medium", MED, 28, None, None),
    ("title_28_semibold", SEMI, 28, None, None),
    ("menu_26_bold", BOLD, 26, None, None),
    ("menu_26_medium", MED, 26, None, None),
    ("body_26", REG, 26, 1.11, None),
    ("body_25", REG, 25, 1.09, None),
    ("label_25_semibold", SEMI, 25, None, None),
    ("label_25_bold", BOLD, 25, None, None),
    ("section_24", BOLD, 24, 0.88, None),
    ("body_23", REG, 23, 1.09, None),
    ("button_23_bold", BOLD, 23, None, None),
    ("button_23_semibold", SEMI, 23, None, None),
    ("credits_22", REG, 22, None, None),
    ("credits_21", REG, 21, None, None),
    ("credits_21_semibold", SEMI, 21, None, None),
    ("card_21_bold", BOLD, 21, None, None),
    ("card_21_medium", MED, 21, None, None),
    ("card_21", REG, 21, None, None),
    ("small_19_bold", BOLD, 19, None, None),
    ("small_19", REG, 19, 1.15, None),
    ("small_16", REG, 16, None, None),
    # --- mono ----------------------------------------------------------------
    ("mono_17", MONO_T, 17, None, "uppercase"),
    ("mono_15", MONO_T, 15, None, "uppercase"),
    ("mono_14", MONO_T, 14, None, "uppercase"),
    ("mono_13", MONO_T, 13, None, "uppercase"),
    ("num_16", MONO, 16, None, None),
    ("num_14", MONO, 14, None, None),
    ("tab_13", MONO_M, 13, None, None),
    # --- Estuary-name aliases for third-party script windows (DESIGN 4.3) ---
    # Same file+size as a font above => Kodi shares the glyph cache.
    ("font10", REG, 21, None, None),
    ("font12", REG, 23, None, None),
    ("font14", REG, 28, None, None),
    ("font27", REG, 27, None, None),
    ("font30", SEMI, 30, None, None),
    ("font37", BOLD, 37, None, None),
    ("font45", BOLD, 45, None, None),
    ("font52_title", BOLD, 52, None, None),
    ("font45_title", BOLD, 45, None, None),
    ("font36_title", BOLD, 36, None, None),
    ("font30_title", BOLD, 30, None, None),
    ("font25_title", BOLD, 25, None, None),
    ("Mono26", MONO, 26, None, None),
    ("num_22", MONO, 22, None, None),
]


# Estuary font names kept for third-party script windows (add-on dialogs ask for them by name; Kodi only falls
# back to font13). kdk (the Kodi repository review bot) reports them as unused: each line carries a kdk-ignore.
ESTUARY_ALIASES = {"font10", "font12", "font14", "font27", "font30", "font37", "font45", "font52_title",
                   "font45_title", "font36_title", "font30_title", "font25_title"}
KDK_ALIAS = " <!-- kdk-ignore: fonts; Estuary font name kept for add-on script windows -->"


def font_xml(name, filename, size, ls, style):
    parts = [f"<name>{name}</name>", f"<filename>{filename}</filename>", f"<size>{size}</size>"]
    if ls is not None:
        parts.append(f"<linespacing>{ls}</linespacing>")
    if style:
        parts.append(f"<style>{style}</style>")
    return "\t\t<font>" + "".join(parts) + "</font>" + (KDK_ALIAS if name in ESTUARY_ALIASES else "")


def main():
    names = [f[0] for f in FONTS]
    assert len(names) == len(set(names)), "duplicate font name"
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- GENERATED by _src/make_fontxml.py - edit the table there, not this file. -->",
        "<!-- Type scale: docs/skin.majan/DESIGN.md section 4.3. Licences: fonts/OFL-*.txt -->",
        "<fonts>",
        '\t<fontset id="Default" idloc="31900">',
    ]
    out += [font_xml(*f) for f in FONTS]
    out += ["\t</fontset>", "\t<!-- Fallback set: same names, Kodi's bundled arial.ttf (wider script coverage). -->",
            '\t<fontset id="Arial" idloc="31901">']
    for name, _file, size, ls, style in FONTS:
        out.append(font_xml(name, "arial.ttf", size, ls, style))
    out += ["\t</fontset>", "</fonts>", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(FONTS)} fonts per set)")


if __name__ == "__main__":
    main()
