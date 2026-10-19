"""One-off fork pass: skin.majan engine -> skin.sixdegrees (run once, 2026-10-19; kept for the record).

Reads the pristine XML from skins/skin.majan/1080i and writes skins/skin.sixdegrees/1080i:
  * majan.* setting/property prefix -> sixdegrees.*, Majan_ include names -> SD_, playlist names
  * Majan's dark "Index" colour names -> Six Degrees' transit-map names (colors/defaults.xml)
  * the accent ($VAR[ColorAccent]) -> ink: focus in Six Degrees is an ink ring / ink pill
  * removed Majan settings collapse to constants (rounded corners = always, art background = off,
    focus outline = always thin)
  * Majan font names -> Six Degrees font names (Font.xml from make_fontxml.py)
Every window is then redesigned by hand; this pass only makes the engine speak the new tokens.

DO NOT re-run after hand edits: it overwrites 1080i/ from Majan.  (python fork_from_majan.py --yes)
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skin.majan" / "1080i"
DST = ROOT / "skin.sixdegrees" / "1080i"

COLOR_MAP = {
    "text_primary": "ink", "text_body": "body", "text_secondary": "ink2", "text_tertiary": "ink2",
    "accent": "ink", "accent_signal": "l_dir",
    "accent_cobalt": "l_lead", "accent_mint": "l_yg", "accent_amber": "l_dir", "accent_rose": "l_co",
    "accent_ice": "l_lead", "accent_bone": "ink",
    "hairline": "hair", "hairline_soft": "hair", "hairline_art": "hair",
    "hairline_strong": "hair_strong", "hairline_art_strong": "hair_strong",
    "border_control": "hair_strong", "border_button": "hair",
    "ink": "on_ink", "bg": "ground", "bg_raised": "card", "bg_ghost": "wash",
    "disabled": "ink3", "scrim": "ground", "scrim_track": "track_on_art", "scrim_tab": "ground",
    "dim_row": "white", "dim_passed": "white", "dim_ahead": "white",
    "dim_dialog": "veil", "dim_video": "video_dim",
    "shadow": "shadow", "focus_halo": "clear",
    "art_faint": "clear", "art_soft": "clear", "art_visible": "clear",
}
VAR_MAP = {"ColorAccent": "ink", "ColorRule": "hair", "ColorRuleStrong": "hair_strong", "ColorCaption": "ink2"}
FONT_MAP = {
    "display_100": "disp_84", "display_92": "disp_84", "display_72": "disp_76", "display_68": "disp_60",
    "display_64": "disp_60", "display_48": "disp_52", "ghost_220": "disp_84", "header_34": "xb_34",
    "clock_34": "xb_30", "stat_30": "xb_30",
    "title_28_bold": "xb_28", "title_28_medium": "semi_28", "title_28_semibold": "semi_28",
    "menu_26_bold": "xb_26", "menu_26_medium": "semi_26",
    "body_26": "reg_26", "body_25": "reg_26", "body_23": "reg_24",
    "label_25_semibold": "semi_26", "label_25_bold": "xb_26", "section_24": "caps_22",
    "button_23_bold": "xb_24", "button_23_semibold": "semi_24",
    "credits_22": "reg_22", "credits_21": "reg_22", "credits_21_semibold": "semi_22",
    "card_21_bold": "xb_22", "card_21_medium": "semi_22", "card_21": "reg_22",
    "small_19_bold": "xb_20", "small_19": "reg_20", "small_16": "reg_20",
    "mono_17": "caps_21", "mono_15": "caps_20", "mono_14": "caps_20", "mono_13": "caps_20",
    "num_16": "semi_20", "num_14": "semi_20", "num_22": "semi_22", "Mono26": "semi_26", "tab_13": "semi_20",
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
    # collapsed settings
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "false")
    s = s.replace("Skin.HasSetting(majan.roundedcorners)", "true")
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.SDPlayer").replace("prefix=MajanPlayer", "prefix=SDPlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/sd_")
    s = s.replace("majan.", "sixdegrees.").replace("Majan_", "SD_")
    s = s.replace("docs/skin.majan", "docs/skin.sixdegrees").replace("skin.majan", "skin.sixdegrees")
    s = s.replace("Majan", "Six Degrees")
    return s


EXPR_OVERRIDES = {
    "IsRounded": "true",
    "FocusOutlineOff": "false",
    "FocusOutlineMedium": "false",
    "ArtBackgroundOn": "false",
}


def main() -> None:
    if "--yes" not in sys.argv:
        sys.exit("refusing to overwrite 1080i/ without --yes (see docstring)")
    for f in sorted(SRC.glob("*.xml")):
        s = transform(f.read_text(encoding="utf-8"))
        if f.name == "Expressions.xml":
            for name, val in EXPR_OVERRIDES.items():
                s = re.sub(rf'(<expression name="{name}">)[^<]*(</expression>)', rf"\g<1>{val}\g<2>", s)
        (DST / f.name).write_text(s, encoding="utf-8")
    for p in (ROOT / "skin.majan" / "playlists").glob("*.xsp"):
        (ROOT / "skin.sixdegrees" / "playlists" / p.name.replace("majan_", "sd_")).write_text(
            transform(p.read_text(encoding="utf-8")), encoding="utf-8")
    print("forked", len(list(SRC.glob('*.xml'))), "files")


if __name__ == "__main__":
    main()
