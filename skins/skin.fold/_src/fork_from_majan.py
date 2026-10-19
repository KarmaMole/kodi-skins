"""One-off fork pass: skin.majan 1.0.4 engine -> skin.fold (run once, 2026-10-19; kept for the record).

Reads the pristine XML from skins/skin.majan/1080i and writes skins/skin.fold/1080i:
  * majan.* setting/property prefix -> fold.*, Majan_ include names -> Fold_, playlist names
  * Majan's dark "Index" colour names -> Fold's table / card / ink names (colors/defaults.xml)
  * the accent ($VAR[ColorAccent]) -> $VAR[FoldAccent] (section colour)
  * removed Majan settings collapse to constants (rounded corners = never, art background = off)
  * Majan font names -> Fold font names (Font.xml from make_fontxml.py)
Every window is then redesigned by hand; this pass only makes the engine speak the new tokens.

DO NOT re-run after hand edits: it overwrites 1080i/ from Majan.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skin.majan" / "1080i"
DST = ROOT / "skin.fold" / "1080i"

COLOR_MAP = {
    "text_primary": "ink", "text_body": "body", "text_secondary": "ink2", "text_tertiary": "cap",
    "accent": "verm", "accent_signal": "verm",
    "hairline": "rule_soft", "hairline_soft": "rule_soft", "hairline_art": "rule_soft",
    "hairline_strong": "rule", "hairline_art_strong": "rule",
    "border_control": "rule_strong", "border_button": "rule_strong",
    "ink": "on_card", "bg": "table", "bg_raised": "cream", "bg_ghost": "cream_deep",
    "disabled": "disabled", "scrim": "table", "scrim_tab": "veil", "scrim_track": "track",
    "shadow": "shadow", "focus_halo": "clear",
    "dim_row": "white", "dim_passed": "white", "dim_ahead": "white",
    "dim_dialog": "veil", "dim_video": "video_dim",
    "art_faint": "clear", "art_soft": "clear", "art_visible": "clear",
}
VAR_MAP = {"ColorAccent": "FoldAccent", "ColorRule": "FoldRule", "ColorRuleStrong": "FoldRuleStrong",
           "ColorCaption": "FoldCaption"}
FONT_MAP = {
    "display_100": "disp_96", "display_92": "disp_96", "display_72": "disp_72", "display_68": "disp_64",
    "display_64": "disp_64", "display_48": "head_50", "ghost_220": "disp_158", "header_34": "head_34",
    "clock_34": "num_38", "stat_30": "head_28",
    "title_28_bold": "sans_28_semi", "title_28_medium": "sans_28_semi", "title_28_semibold": "sans_28_semi",
    "menu_26_bold": "tab_26", "menu_26_medium": "sans_26_semi",
    "body_26": "body_26", "body_25": "body_26", "body_23": "body_24",
    "label_25_semibold": "sans_26_semi", "label_25_bold": "sans_26_semi", "section_24": "caps_20_b",
    "button_23_bold": "word_26", "button_23_semibold": "word_26",
    "credits_22": "body_22", "credits_21": "body_22", "credits_21_semibold": "sans_22_semi",
    "card_21_bold": "sans_22_semi", "card_21_medium": "sans_22_semi", "card_21": "body_22",
    "small_19_bold": "sans_20_semi", "small_19": "body_20", "small_16": "body_20",
    "mono_17": "caps_20", "mono_15": "caps_20", "mono_14": "caps_20", "mono_13": "caps_20",
    "num_16": "num_20", "num_14": "num_20", "num_22": "num_22", "Mono26": "num_26", "tab_13": "caps_20",
}
COLOR_TAGS = "textcolor|focusedcolor|selectedcolor|disabledcolor|shadowcolor|invalidcolor|colordiffuse|color"


def transform(s: str) -> str:
    names = "|".join(sorted(COLOR_MAP, key=len, reverse=True))
    s = re.sub(rf'\b({COLOR_TAGS})="({names})"', lambda m: f'{m.group(1)}="{COLOR_MAP[m.group(2)]}"', s)
    s = re.sub(rf'<({COLOR_TAGS})>({names})</', lambda m: f'<{m.group(1)}>{COLOR_MAP[m.group(2)]}</', s)
    s = re.sub(rf'\[COLOR ({names})\]', lambda m: f'[COLOR {COLOR_MAP[m.group(1)]}]', s)
    s = re.sub(rf'(<value(?: condition="[^"]*")?>)({names})(</value>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]+" value=")({names})("\s*/>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]+">)({names})(</param>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'<backgroundcolor>({names})</backgroundcolor>', lambda m: f'<backgroundcolor>{COLOR_MAP[m.group(1)]}</backgroundcolor>', s)
    for old, new in VAR_MAP.items():
        s = s.replace(f"$VAR[{old}]", f"$VAR[{new}]")
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf'<font>({fn})</font>', lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "true")
    s = s.replace("Skin.HasSetting(majan.roundedcorners)", "false")
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.FoldPlayer").replace("prefix=MajanPlayer", "prefix=FoldPlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/fold_")
    s = s.replace("majan.", "fold.").replace("Majan_", "Fold_")
    s = s.replace("docs/skin.majan", "docs/skin.fold").replace("skin.majan", "skin.fold")
    s = s.replace("Majan", "Fold")
    return s


def main() -> None:
    if "--yes" not in sys.argv:
        sys.exit("refusing to overwrite 1080i/ without --yes (see docstring)")
    for f in sorted(SRC.glob("*.xml")):
        if f.name == "Font.xml":
            continue
        (DST / f.name).write_text(transform(f.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    pl = ROOT / "skin.fold" / "playlists"
    for f in sorted(pl.glob("majan_*.xsp")):
        f.with_name(f.name.replace("majan_", "fold_")).write_text(transform(f.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        f.unlink()
    po = ROOT / "skin.fold" / "language" / "resource.language.en_gb" / "strings.po"
    po.write_text(transform(po.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print("fork pass done")


if __name__ == "__main__":
    main()
