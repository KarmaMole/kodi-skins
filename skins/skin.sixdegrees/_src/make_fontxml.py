"""Generate skins/skin.sixdegrees/1080i/Font.xml from one table (DESIGN.md section 4.3).

Why a generator: Six Degrees ships TWO fontsets that must define exactly the same
names (Kodi has no per-glyph fallback):
  * "Default" - Hanken Grotesk / JetBrains Mono / the tracked Six Degrees derivatives
  * "Arial"   - Kodi's bundled arial.ttf at the same sizes, selectable in
                Settings > Interface > Skin > Fonts for titles in scripts the
                Six Degrees fonts don't cover (Arabic, CJK...). Estuary pattern.
Editing the table below and re-running keeps both sets in sync.

Usage:  python skins/skin.sixdegrees/_src/make_fontxml.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Font.xml"

DISPLAY = "SixDegreesDisplay-ExtraBold.ttf"   # Hanken 800, -0.03em (headings)
REG = "SixDegreesText-Regular.ttf"   # Hanken 400 + symbols
SEMI = "SixDegreesText-SemiBold.ttf"  # Hanken 600 + symbols
XB = "SixDegreesText-ExtraBold.ttf"   # Hanken 800 + symbols
CAPS = "SixDegreesCaps-SemiBold.ttf"          # 600, +0.10em, uppercase: line labels, captions
CAPSXB = "SixDegreesCapsXB-ExtraBold.ttf"     # 800, +0.04em: the count after a line label

# Hanken's natural line is 1.303 em (hhea 1000 / -303 / 0), baseline 1.0 em below the line top.
# linespacing = CSS line-height / 1.303.
# name, file, size, linespacing (None = font default), style (None = normal)
FONTS = [
    # --- Kodi-required fallback (must exist) -------------------------------
    ("font13", REG, 25, None, None),
    # --- display (tight Hanken 800) ------------------------------------------
    ("disp_84", DISPLAY, 84, 0.80, None),     # station page title
    ("disp_76", DISPLAY, 76, 0.80, None),     # "Start somewhere"
    ("disp_60", DISPLAY, 60, 0.80, None),     # map centre title
    ("disp_52", DISPLAY, 52, 0.80, None),     # Home preview title
    ("disp_44", DISPLAY, 44, 0.82, None),
    ("disp_36", DISPLAY, 36, 0.84, None),
    # --- Hanken 800 ------------------------------------------------------------
    ("xb_34", XB, 34, 0.86, None),            # focused poster station title
    ("xb_30", XB, 30, 0.86, None),            # focused dot station title, clock
    ("xb_28", XB, 28, None, None),            # wordmark, Index terminus
    ("xb_26", XB, 26, None, None),            # active section, Play pill
    ("xb_24", XB, 24, None, None),            # route current, next-stop title, line pill "+10"
    ("xb_22", XB, 22, None, None),
    ("xb_20", XB, 20, None, None),
    ("xb_19", XB, 19, None, None),            # key caps (OK / BACK)
    # --- Hanken 600 ------------------------------------------------------------
    ("semi_30", SEMI, 30, None, None),
    ("semi_28", SEMI, 28, None, None),
    ("semi_26", SEMI, 26, None, None),        # sections, facts row, outline pills
    ("semi_24", SEMI, 24, 0.86, None),
    ("st_24", SEMI, 24, 1.0, None),
    ("st_22", SEMI, 22, 1.0, None),          # Home starter title + why (one textbox, 29 px pitch)          # station titles in auto-height textboxes (31 px pitch, descender-safe)        # station titles (line-height 1.12), route names, meta
    ("semi_22", SEMI, 22, None, None),        # hints
    ("semi_21", SEMI, 21, None, None),
    ("semi_20", SEMI, 20, None, None),
    # --- Hanken 400 ------------------------------------------------------------
    ("reg_26", REG, 26, 1.151, None),         # plot 26 / 39
    ("reg_24", REG, 24, 1.087, None),         # body 24 / 34
    ("reg_22", REG, 22, 1.11, None),
    ("reg_21", REG, 21, None, None),          # station sub line (year)
    ("reg_20", REG, 20, None, None),
    # --- caps (tracked) --------------------------------------------------------
    ("caps_22", CAPS, 22, None, "uppercase"), # line labels
    ("caps_21", CAPS, 21, None, "uppercase"), # captions (NEXT STOP, CONTINUE)
    ("caps_20", CAPS, 20, None, "uppercase"),
    ("capsxb_22", CAPSXB, 22, None, None),    # "· 14"
    ("capsxb_21", CAPSXB, 21, None, None),
    # --- Estuary-name aliases for third-party script windows ------------------
    # Same file+size as a font above => Kodi shares the glyph cache.
    ("font10", REG, 21, None, None),
    ("font12", REG, 22, None, None),
    ("font14", REG, 26, None, None),
    ("font27", REG, 26, None, None),
    ("font30", SEMI, 30, None, None),
    ("font37", XB, 34, None, None),
    ("font45", XB, 44, None, None),
    ("font52_title", DISPLAY, 52, None, None),
    ("font45_title", DISPLAY, 44, None, None),
    ("font36_title", DISPLAY, 36, None, None),
    ("font30_title", XB, 30, None, None),
    ("font25_title", XB, 26, None, None),
    ("Mono26", SEMI, 26, None, None),
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
        "<!-- Type scale: docs/skin.sixdegrees/DESIGN.md section 4.3. Licences: fonts/OFL-*.txt -->",
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
