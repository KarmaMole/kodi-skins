"""One-off fork pass: skin.majan engine (1.0.4) -> skin.keepsake (run once, 2026-10-19; kept for the record).

Reads the pristine XML from skins/skin.majan/1080i and writes skins/skin.keepsake/1080i:
  * majan.* setting/property prefix -> keepsake.*, Majan_ include names -> KS_, playlist names
  * Majan's dark "Index" colour names -> Keepsake's album names (colors/defaults.xml)
  * the accent ($VAR[ColorAccent]) -> ink_bold: Keepsake's focus is pen and tape, its only colour is the stamp
  * removed Majan settings collapse to constants (rounded corners never, outline default, art background off)
  * Majan font names -> Keepsake font names (Font.xml from make_fontxml.py)
Every window is then redesigned by hand; this pass only makes the engine speak the new tokens.

DO NOT re-run after hand edits: it overwrites 1080i/ from Majan (refuses without --yes).
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skin.majan" / "1080i"
DST = ROOT / "skin.keepsake" / "1080i"

COLOR_MAP = {
    "text_primary": "ink_bold", "text_body": "body", "text_secondary": "ink2", "text_tertiary": "label",
    "accent": "ink_bold", "accent_signal": "stamp",
    "accent_cobalt": "ink_bold", "accent_mint": "ink_bold", "accent_amber": "ink_bold", "accent_rose": "ink_bold",
    "accent_ice": "ink_bold", "accent_bone": "ink_bold",
    "hairline": "rule", "hairline_soft": "rule", "hairline_art": "rule",
    "hairline_strong": "rule_strong", "hairline_art_strong": "rule_strong",
    "border_control": "rule_strong", "border_button": "rule_strong",
    "ink": "on_tape", "bg": "paper", "bg_raised": "paper_raised", "bg_ghost": "paper_raised",
    "disabled": "disabled", "scrim": "shade", "scrim_track": "track", "scrim_tab": "shade_tab",
    "dim_row": "dim_print", "dim_passed": "dim_print_more", "dim_ahead": "dim_print",
    "dim_dialog": "veil", "dim_video": "video_dim",
    "shadow": "shadow", "focus_halo": "clear",
    "art_faint": "clear", "art_soft": "clear", "art_visible": "clear",
}
VAR_MAP = {"ColorAccent": "ink_bold", "ColorRule": "rule", "ColorRuleStrong": "rule_strong", "ColorCaption": "label"}
FONT_MAP = {
    "display_100": "ttl_84", "display_92": "ttl_84", "display_72": "ttl_72", "display_68": "ttl_64",
    "display_64": "ttl_64", "display_48": "ttl_48", "ghost_220": "ttl_168", "header_34": "hand_48",
    "clock_34": "stamp_34", "stat_30": "ttt_30",
    "title_28_bold": "ttt_28", "title_28_medium": "ttt_28", "title_28_semibold": "ttt_28",
    "menu_26_bold": "ttt_26", "menu_26_medium": "ttt_26",
    "body_26": "body_26", "body_25": "body_26", "body_23": "body_24",
    "label_25_semibold": "ttt_26", "label_25_bold": "ttt_26", "section_24": "lbl_22",
    "button_23_bold": "hand_36b", "button_23_semibold": "hand_36",
    "credits_22": "body_24", "credits_21": "body_24", "credits_21_semibold": "ttt_24",
    "card_21_bold": "ttt_24", "card_21_medium": "ttt_24", "card_21": "body_24",
    "small_19_bold": "lbl_20", "small_19": "body_24", "small_16": "lbl_20",
    "mono_17": "lbl_20", "mono_15": "lbl_20", "mono_14": "lbl_20", "mono_13": "lbl_20",
    "num_16": "mono_20", "num_14": "mono_20", "num_22": "mono_22", "Mono26": "mono_26", "tab_13": "lbl_20",
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
    # collapsed Majan settings
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "true")
    s = s.replace("Skin.HasSetting(majan.roundedcorners)", "false")
    s = s.replace("!String.IsEqual(Skin.String(majan.focusoutline),medium)", "true")
    s = s.replace("String.IsEqual(Skin.String(majan.focusoutline),medium)", "false")
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.KSPlayer").replace("prefix=MajanPlayer", "prefix=KSPlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/keepsake_")
    s = s.replace("majan.", "keepsake.").replace("Majan_", "KS_")
    s = s.replace("docs/skin.majan", "docs/skin.keepsake").replace("skin.majan", "skin.keepsake")
    s = s.replace("Majan", "Keepsake")
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
