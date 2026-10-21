"""Generate skins/skin.passepartout/1080i/Font.xml from one table (docs/skin.passepartout/DESIGN.md, type scale).

Two fontsets with identical names (Kodi has no per-glyph fallback):
  * "Default" - the Geist derivatives built by make_fonts.py
  * "Arial"   - Kodi's bundled arial.ttf at the same sizes (Settings > Interface > Skin > Fonts),
                for titles in scripts Geist doesn't cover.

Line spacing: Geist derivatives have ascender 950 / descender -250 = 1.20 em natural pitch,
so linespacing = CSS line-height / (1.2 x size). Single-line labels: height = CSS line-height,
aligny center.

Usage:  python skins/skin.passepartout/_src/make_fontxml.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Font.xml"

TITLE = "PPTitle-Light.ttf"       # Geist 300, -0.025em
DISPLAY = "PPDisplay-Light.ttf"   # Geist 300, -0.035em
REG = "PPSans-Regular.ttf"        # Geist 400
MED = "PPSans-Medium.ttf"         # Geist 500
CAPS = "PPCaps-Medium.ttf"        # Geist 500, +0.16em, uppercase cmap
CAPSW = "PPCapsWide-Medium.ttf"   # Geist 500, +0.20em, uppercase cmap
MONO = "PPMono-Regular.ttf"       # Geist Mono 400
CLOCK = "PPClock-Regular.ttf"     # Geist Mono 400, +0.02em
NUM = "PPNum-Regular.ttf"         # Geist Mono 400, +0.04em


def ls(line_height, size):
    return round(line_height / (1.2 * size), 3)


# name, file, size, linespacing (None = 1.0), style
FONTS = [
    ("font13", REG, 24, None, None),
    # --- display / titles (Geist Light) --------------------------------------------------
    ("disp_112", DISPLAY, 112, ls(132, 112), None),   # wall label title, 112 / 132
    ("disp_104", DISPLAY, 104, ls(124, 104), None),     # search query 104 / 124
    ("disp_96", DISPLAY, 96, ls(112, 96), None),
    ("ttl_72", TITLE, 72, ls(84, 72), None),           # captions under prints, 72 / 84
    ("ttl_64", TITLE, 64, ls(76, 64), None),
    ("ttl_56", TITLE, 56, ls(66, 56), None),
    ("ttl_48", TITLE, 48, ls(58, 48), None),
    ("ttl_44", TITLE, 44, ls(54, 44), None),           # episode titles 44 / 54
    ("ttl_40", TITLE, 40, ls(50, 40), None),
    ("ttl_34", TITLE, 34, ls(44, 34), None),
    # --- text (Geist Regular / Medium) ------------------------------------------------------
    ("key_34", REG, 34, None, None),                  # keyboard keys (Search board)
    ("body_30", REG, 30, ls(40, 30), None),           # settings categories 30 / 40
    ("body_28", REG, 28, ls(42, 28), None),
    ("body_26", REG, 26, ls(40, 26), None),            # curator text, 26 / 40
    ("body_24", REG, 24, ls(34, 24), None),            # caption line, 24 / 34
    ("body_24_loose", REG, 24, ls(36, 24), None),      # "With ..." 24 / 36
    ("body_22", REG, 22, ls(32, 22), None),
    ("body_20", REG, 20, ls(28, 20), None),
    ("sans_28_med", MED, 28, None, None),
    ("sans_26_med", MED, 26, None, None),
    ("sans_22_med", MED, 22, None, None),
    ("sans_20_med", MED, 20, None, None),
    # --- tracked capitals (museum-label voice) --------------------------------------------
    ("cap_20", CAPS, 20, ls(28, 20), "uppercase"),     # .cap 20 / 28 / .16em
    ("capw_22", CAPSW, 22, None, "uppercase"),          # action buttons 22 / .2em
    # --- numbers (Geist Mono) -------------------------------------------------------------
    ("clock_24", CLOCK, 24, None, None),                # clock .02em
    ("num_20", NUM, 20, None, None),
    ("num_22", NUM, 22, None, None),                    # counts .04em
    ("mono_22", MONO, 22, None, None),                  # times, counter
    ("mono_24", MONO, 24, None, None),
    ("mono_26", MONO, 26, None, None),
    # --- Estuary-name aliases for third-party script windows ------------------------------
    ("font10", REG, 20, None, None),
    ("font12", REG, 22, None, None),
    ("font14", REG, 28, None, None),
    ("font27", REG, 26, None, None),
    ("font30", MED, 30, None, None),
    ("font37", TITLE, 40, None, None),
    ("font45", TITLE, 48, None, None),
    ("font52_title", TITLE, 56, None, None),
    ("font45_title", TITLE, 48, None, None),
    ("font36_title", TITLE, 40, None, None),
    ("font30_title", TITLE, 34, None, None),
    ("font25_title", MED, 26, None, None),
    ("Mono26", MONO, 26, None, None),
]



# Estuary font names kept for third-party script windows (add-on dialogs ask for them by name; Kodi only falls
# back to font13). kdk (the Kodi repository review bot) reports them as unused: each line carries a kdk-ignore.
ESTUARY_ALIASES = {"font10", "font12", "font14", "font27", "font30", "font37", "font45", "font52_title",
                   "font45_title", "font36_title", "font30_title", "font25_title"}
KDK_ALIAS = " <!-- kdk-ignore: fonts; Estuary font name kept for add-on script windows -->"

def font_xml(name, filename, size, lsp, style):
    parts = [f"<name>{name}</name>", f"<filename>{filename}</filename>", f"<size>{size}</size>"]
    if lsp is not None and lsp != 1.0:
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
        "<!-- Type scale: docs/skin.passepartout/DESIGN.md. Licences: fonts/OFL-*.txt -->",
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
