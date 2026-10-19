"""Generate skins/skin.keepsake/1080i/Font.xml from one table (docs/skin.keepsake/DESIGN.md "Type").

Three voices + the stamp (fonts built by _src/make_fonts.py):
  hand_*   Keepsake Hand (Caveat)          white gel-pen sentences, words, headings
  ttl_* / ttt_*  Keepsake Title (Fraunces opsz 144 / 36, 600)   titles, cream
  body_*   Keepsake Body (Fraunces opsz 14, 400)                  plots
  lbl_* / lbln_*  Keepsake Label (DM Mono, tracked caps)          small-caps labels
  mono_*   Keepsake Mono (DM Mono)         numbers, mixed case mono
  stamp_* (+ g1_*, g2_* glow layers)       orange LCD date imprint / clock

Line metrics (make_fonts.py): Hand 0.96 em baseline / 1.25 em line; Title/Body 0.92 / 1.18; Label/Mono 0.97 / 1.24.
Textbox linespacing = CSS line-height / line-em (e.g. hand 1.12 -> 0.896, body 1.45 -> 1.228).

Two fontsets with identical names (Kodi has no per-glyph fallback): "Default" and "Arial" (Kodi's arial.ttf,
for titles in scripts the Keepsake faces don't cover).

Usage:  python skins/skin.keepsake/_src/make_fontxml.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Font.xml"

HM = "KeepsakeHand-Medium.ttf"
HS = "KeepsakeHand-SemiBold.ttf"
HB = "KeepsakeHand-Bold.ttf"
TD = "KeepsakeTitle-SemiBold.ttf"
TT = "KeepsakeTitleText-SemiBold.ttf"
BODY = "KeepsakeBody-Regular.ttf"
LBL = "KeepsakeLabel-Regular.ttf"
LBLN = "KeepsakeLabelNarrow-Regular.ttf"
MONO = "KeepsakeMono-Regular.ttf"
ST = "KeepsakeStamp-Bold.ttf"
G1 = "KeepsakeStampGlow1-Bold.ttf"
G2 = "KeepsakeStampGlow2-Bold.ttf"

# name, file, size, linespacing (None = font default), style
FONTS = [
    ("font13", BODY, 26, None, None),
    # ---------------------------------------------------------------- hand (Caveat)
    ("hand_100", HS, 100, None, None),
    ("hand_92", HS, 92, None, None),
    ("hand_66", HS, 66, None, None),
    ("hand_66x", HB, 66, None, None),
    ("hand_64x", HB, 64, None, None),
    ("hand_60", HS, 60, None, None),
    ("hand_58", HS, 58, None, None),
    ("hand_54", HS, 54, None, None),
    ("hand_52", HM, 52, None, None),
    ("hand_52b", HS, 52, None, None),
    ("hand_48", HS, 48, None, None),
    ("hand_46", HM, 46, 0.88, None),
    ("hand_44", HM, 44, 0.896, None),
    ("hand_44b", HS, 44, 0.896, None),
    ("hand_42", HM, 42, 0.86, None),
    ("hand_40", HM, 40, 0.84, None),
    ("hand_40b", HS, 40, 0.84, None),
    ("hand_36", HM, 36, 0.84, None),
    ("hand_36b", HS, 36, 0.84, None),
    ("hand_34", HM, 34, 0.84, None),
    ("hand_30", HM, 30, 0.84, None),
    # ---------------------------------------------------------------- titles (Fraunces)
    ("ttl_168", TD, 168, 0.83, None),
    ("ttl_132", TD, 132, 0.83, None),
    ("ttl_104", TD, 104, 0.83, None),
    ("ttl_84", TD, 84, 0.84, None),
    ("ttl_72", TD, 72, 0.84, None),
    ("ttl_64", TD, 64, 0.84, None),
    ("ttl_54", TD, 54, 0.85, None),
    ("ttl_48", TD, 48, 0.86, None),
    ("ttt_40", TT, 40, 0.92, None),
    ("ttt_34", TT, 34, 0.92, None),
    ("ttt_30", TT, 30, 0.95, None),
    ("ttt_28", TT, 28, 0.95, None),
    ("ttt_26", TT, 26, 0.95, None),
    ("ttt_24", TT, 24, 0.95, None),
    # ---------------------------------------------------------------- body (Fraunces text)
    ("body_28", BODY, 28, 1.228, None),
    ("body_26", BODY, 26, 1.185, None),
    ("body_24", BODY, 24, 1.185, None),
    # ---------------------------------------------------------------- labels (DM Mono caps)
    ("lbl_20", LBL, 20, 1.09, None),
    ("lbl_22", LBL, 22, 1.09, None),
    ("lbl_24", LBL, 24, 1.09, None),
    ("lbln_20", LBLN, 20, 1.09, None),
    ("lbln_22", LBLN, 22, 1.09, None),
    ("lbln_24", LBLN, 24, 1.09, None),
    ("mono_20", MONO, 20, None, None),
    ("mono_22", MONO, 22, None, None),
    ("mono_24", MONO, 24, None, None),
    ("mono_26", MONO, 26, None, None),
    # ---------------------------------------------------------------- stamp / LCD (core + 2 glow layers)
]
for px in (19, 20, 22, 26, 30, 34, 44):
    FONTS += [(f"stamp_{px}", ST, px, None, None), (f"g1_{px}", G1, px, None, None), (f"g2_{px}", G2, px, None, None)]
FONTS += [
    # ---------------------------------------------------------------- Estuary names for script windows
    ("font10", BODY, 24, None, None),
    ("font12", BODY, 24, None, None),
    ("font14", TT, 28, None, None),
    ("font27", TT, 28, None, None),
    ("font30", TT, 30, None, None),
    ("font37", TT, 34, None, None),
    ("font45", TD, 48, None, None),
    ("font52_title", TD, 54, None, None),
    ("font45_title", TD, 48, None, None),
    ("font36_title", TT, 40, None, None),
    ("font30_title", TT, 30, None, None),
    ("font25_title", TT, 26, None, None),
    ("Mono26", MONO, 26, None, None),
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
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           "<!-- GENERATED by _src/make_fontxml.py - edit the table there, not this file. -->",
           "<!-- Licences: fonts/OFL-*.txt -->", "<fonts>", '\t<fontset id="Default" idloc="31900">']
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
