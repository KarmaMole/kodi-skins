"""One-off fork pass: skin.majan engine -> skin.sentence (run once on 2026-10-18; kept for the record).

Reads the pristine XML from skins/skin.majan/1080i and writes skins/skin.sentence/1080i:
  * majan.* setting/property prefix -> sentence.*, Majan_ include names -> Sen_, playlists, TMDb prefixes
  * Majan colour names -> Sentence palette names (colors/defaults.xml), $VAR colour helpers -> names
  * Majan font names -> Sentence font names (Font.xml from make_fontxml.py)
  * removed Majan settings collapse to constants (square corners, no blurred art background)
Windows are then redesigned by hand; DO NOT re-run after hand edits (it overwrites 1080i/).
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skin.majan" / "1080i"
DST = ROOT / "skin.sentence" / "1080i"

COLOR_MAP = {
    "text_primary": "text", "text_body": "body", "text_secondary": "muted", "text_tertiary": "muted",
    "accent": "lilac", "accent_signal": "lilac", "accent_cobalt": "lilac", "accent_mint": "lilac",
    "accent_amber": "lilac", "accent_rose": "lilac", "accent_ice": "lilac", "accent_bone": "lilac",
    "hairline": "rule", "hairline_soft": "rule", "hairline_art": "rule",
    "hairline_strong": "rule_strong", "hairline_art_strong": "rule_strong",
    "border_control": "rule_strong", "border_button": "rule_strong",
    "ink": "on_lilac", "bg": "ground", "bg_raised": "raised", "bg_ghost": "surface",
    "scrim_track": "scrim_80", "scrim_tab": "scrim_80",
    "dim_row": "dim_art", "dim_passed": "dim_art", "dim_ahead": "dim_art_soft",
    "focus_halo": "shadow", "art_faint": "art_bg", "art_soft": "art_bg", "art_visible": "art_bg",
    # unchanged names that exist in both palettes
    "disabled": "disabled", "scrim": "scrim", "white": "white", "black": "black", "clear": "clear",
    "shadow": "shadow", "dim_dialog": "dim_dialog", "dim_video": "dim_video",
}
VAR_MAP = {"$VAR[ColorAccent]": "lilac", "$VAR[ColorRule]": "rule",
           "$VAR[ColorRuleStrong]": "rule_strong", "$VAR[ColorCaption]": "muted"}
FONT_MAP = {
    "mono_13": "cap_20", "mono_14": "cap_20", "mono_15": "cap_20", "mono_17": "cap_22",
    "num_14": "num_20", "num_16": "num_20", "tab_13": "cap_20",
    "small_16": "ui_20", "small_19": "ui_20", "small_19_bold": "ui_20_bold",
    "card_21": "ui_22", "card_21_medium": "ui_22", "card_21_bold": "ui_22_bold",
    "credits_21": "ui_22", "credits_22": "ui_22", "credits_21_semibold": "ui_22_bold",
    "body_23": "body_24", "body_25": "body_24", "body_26": "body_26",
    "button_23_bold": "ui_24_bold", "button_23_semibold": "ui_24_bold",
    "section_24": "ui_24_bold", "label_25_semibold": "ui_24_bold", "label_25_bold": "ui_24_bold",
    "menu_26_bold": "ui_26_bold", "menu_26_medium": "ui_26",
    "title_28_bold": "ui_28_bold", "title_28_medium": "ui_28_bold", "title_28_semibold": "ui_28_bold",
    "stat_30": "ui_30_bold", "clock_34": "ui_30_bold", "header_34": "serif_34",
    "display_48": "serif_46", "display_64": "serif_60", "display_68": "serif_60", "display_72": "serif_66",
    "display_92": "serif_80", "display_100": "serif_80", "ghost_220": "serif_80",
}
COLOR_TAGS = "textcolor|focusedcolor|selectedcolor|disabledcolor|shadowcolor|invalidcolor|colordiffuse|color"


def transform(s: str) -> str:
    for old, new in VAR_MAP.items():
        s = s.replace(old, new)
    names = "|".join(sorted(COLOR_MAP, key=len, reverse=True))
    s = re.sub(rf'\b({COLOR_TAGS})="({names})"', lambda m: f'{m.group(1)}="{COLOR_MAP[m.group(2)]}"', s)
    s = re.sub(rf'<({COLOR_TAGS})>({names})</', lambda m: f'<{m.group(1)}>{COLOR_MAP[m.group(2)]}</', s)
    s = re.sub(rf'\[COLOR ({names})\]', lambda m: f'[COLOR {COLOR_MAP[m.group(1)]}]', s)
    s = re.sub(rf'(<value(?: condition="[^"]*")?>)({names})(</value>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]+" value=")({names})("\s*/>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]+">)({names})(</param>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(r'<backgroundcolor>bg</backgroundcolor>', '<backgroundcolor>ground</backgroundcolor>', s)
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf'<font>({fn})</font>', lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "true")
    s = s.replace("Skin.HasSetting(majan.roundedcorners)", "false")
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.SentencePlayer").replace("prefix=MajanPlayer", "prefix=SentencePlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/sentence_")
    s = s.replace("majan.", "sentence.").replace("Majan_", "Sen_")
    s = s.replace("docs/skin.majan", "docs/skin.sentence").replace("skin.majan", "skin.sentence")
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
