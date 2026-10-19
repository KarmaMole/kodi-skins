"""One-off fork pass: skin.majan 1.0.4 engine -> skin.nocturne (run once, 2026-10-19; kept for the record).

Rewrites skins/skin.nocturne/1080i (copied from skin.majan) in place:
  * majan.* setting/property prefix -> nocturne.*, Majan_ include names -> Noc_, playlists majan_ -> nocturne_
  * the user accent ($VAR[ColorAccent]) -> `light` (Nocturne has no accent: the torch is the highlight)
  * rounded corners collapse to "never" (frames are square)
  * Majan font names -> Nocturne font names (Font.xml from make_fontxml.py)
Every window is then redesigned by hand.  DO NOT re-run after hand edits.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
X = ROOT / "1080i"

FONT_MAP = {
    "display_100": "title_76", "display_92": "title_76", "display_72": "title_64", "display_68": "title_64",
    "display_64": "title_56", "display_48": "title_48", "ghost_220": "title_120", "header_34": "title_40",
    "clock_34": "clock_30", "stat_30": "serif_32",
    "title_28_bold": "sans_28", "title_28_medium": "sans_28", "title_28_semibold": "sans_28",
    "menu_26_bold": "sans_26", "menu_26_medium": "sans_26",
    "body_26": "body_26", "body_25": "body_26", "body_23": "body_24",
    "label_25_semibold": "sans_26", "label_25_bold": "sans_26", "section_24": "caps_22",
    "button_23_bold": "btn_22", "button_23_semibold": "btn_22",
    "credits_22": "body_22", "credits_21": "body_22", "credits_21_semibold": "sans_22",
    "card_21_bold": "sans_22", "card_21_medium": "sans_22", "card_21": "body_22",
    "small_19_bold": "sans_20", "small_19": "body_20", "small_16": "body_20",
    "mono_17": "caps_20", "mono_15": "caps_20", "mono_14": "caps_20", "mono_13": "caps_20", "tab_13": "caps_20",
    "num_16": "num_20", "num_14": "num_20", "num_22": "num_22", "Mono26": "num_26",
}


def transform(s: str) -> str:
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf'<font>({fn})</font>', lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<value(?: condition="[^"]*")?>)({fn})(</value>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = s.replace("$VAR[ColorAccent]", "light")
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "true")
    s = s.replace("Skin.HasSetting(majan.roundedcorners)", "false")
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.NocturnePlayer").replace("prefix=MajanPlayer", "prefix=NocturnePlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/nocturne_")
    s = s.replace("majan.", "nocturne.").replace("Majan_", "Noc_")
    s = s.replace("docs/skin.majan", "docs/skin.nocturne").replace("skin.majan", "skin.nocturne")
    s = s.replace("Majan", "Nocturne")
    return s


def main() -> None:
    if "--yes" not in sys.argv:
        sys.exit("refusing to run without --yes (see docstring)")
    for f in sorted(X.glob("*.xml")):
        if f.name == "Font.xml":
            continue
        f.write_text(transform(f.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    for f in (ROOT / "playlists").glob("majan_*.xsp"):
        t = transform(f.read_text(encoding="utf-8"))
        (ROOT / "playlists" / f.name.replace("majan_", "nocturne_")).write_text(t, encoding="utf-8", newline="\n")
        f.unlink()
    po = ROOT / "language" / "resource.language.en_gb" / "strings.po"
    po.write_text(transform(po.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print("fork pass done")


if __name__ == "__main__":
    main()
