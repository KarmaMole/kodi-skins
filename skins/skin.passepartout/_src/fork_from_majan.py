"""One-off fork pass: skin.majan engine -> skin.passepartout (run once, 2026-10-18; kept for the record).

Reads the pristine XML from skins/skin.majan/1080i and writes skins/skin.passepartout/1080i:
  * majan.* setting/property prefix -> passepartout.*, Majan_ include names -> PP_, playlist names
  * Majan's dark "Index" colour names -> Passe-partout's light paper/ink names (colors/defaults.xml)
  * the accent ($VAR[ColorAccent]) -> ink: Passe-partout has no accent colour
  * removed Majan settings collapse to constants (rounded corners = never, art background = off)
  * Majan font names -> Passe-partout font names (Font.xml from make_fontxml.py)
Every window is then redesigned by hand; this pass only makes the engine speak the new tokens.

DO NOT re-run after hand edits: it overwrites 1080i/ from Majan.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skin.majan" / "1080i"
DST = ROOT / "skin.passepartout" / "1080i"

COLOR_MAP = {
    "text_primary": "ink", "text_body": "body", "text_secondary": "ink2", "text_tertiary": "ink3",
    "accent": "ink", "accent_signal": "ink",
    "hairline": "rule", "hairline_soft": "rule", "hairline_art": "rule",
    "hairline_strong": "rule_strong", "hairline_art_strong": "rule_strong",
    "border_control": "rule_strong", "border_button": "rule_strong",
    "ink": "on_ink", "bg": "paper", "bg_raised": "wash", "bg_ghost": "wash",
    "disabled": "disabled", "scrim": "shade", "scrim_track": "rule_strong", "scrim_tab": "shade",
    "dim_row": "white", "dim_passed": "white", "dim_ahead": "white",
    "dim_dialog": "veil", "dim_video": "video_dim",
    "shadow": "shadow", "focus_halo": "clear",
    "art_faint": "clear", "art_soft": "clear", "art_visible": "clear",
}
VAR_MAP = {"ColorAccent": "ink", "ColorRule": "rule", "ColorRuleStrong": "rule_strong", "ColorCaption": "ink2"}
FONT_MAP = {
    "display_100": "ttl_72", "display_92": "ttl_72", "display_72": "ttl_64", "display_68": "ttl_64",
    "display_64": "ttl_56", "display_48": "ttl_48", "ghost_220": "disp_112", "header_34": "ttl_40",
    "clock_34": "clock_24", "stat_30": "ttl_34",
    "title_28_bold": "sans_28_med", "title_28_medium": "sans_28_med", "title_28_semibold": "sans_28_med",
    "menu_26_bold": "sans_26_med", "menu_26_medium": "sans_26_med",
    "body_26": "body_26", "body_25": "body_26", "body_23": "body_24",
    "label_25_semibold": "sans_26_med", "label_25_bold": "sans_26_med", "section_24": "cap_20",
    "button_23_bold": "capw_22", "button_23_semibold": "capw_22",
    "credits_22": "body_22", "credits_21": "body_22", "credits_21_semibold": "sans_22_med",
    "card_21_bold": "sans_22_med", "card_21_medium": "sans_22_med", "card_21": "body_22",
    "small_19_bold": "sans_20_med", "small_19": "body_20", "small_16": "body_20",
    "mono_17": "cap_20", "mono_15": "cap_20", "mono_14": "cap_20", "mono_13": "cap_20",
    "num_16": "num_20", "num_14": "num_20", "num_22": "num_22", "Mono26": "mono_26", "tab_13": "cap_20",
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
        s = s.replace(f"$VAR[{old}]", new)
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf'<font>({fn})</font>', lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "true")
    s = s.replace("Skin.HasSetting(majan.roundedcorners)", "false")
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.PPPlayer").replace("prefix=MajanPlayer", "prefix=PPPlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/pp_")
    s = s.replace("majan.", "passepartout.").replace("Majan_", "PP_")
    s = s.replace("docs/skin.majan", "docs/skin.passepartout").replace("skin.majan", "skin.passepartout")
    s = s.replace("Majan", "Passe-partout")
    return s


def main() -> None:
    if "--yes" not in sys.argv:
        sys.exit("refusing to overwrite 1080i/ without --yes (see docstring)")
    for f in sorted(SRC.glob("*.xml")):
        if f.name == "Font.xml":
            continue
        (DST / f.name).write_text(transform(f.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print("fork pass done")


if __name__ == "__main__":
    main()
