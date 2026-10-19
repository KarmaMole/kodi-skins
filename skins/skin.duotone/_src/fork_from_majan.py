"""One-off fork pass: skin.majan engine -> skin.duotone (run once, 2026-10-18; kept for the record).

Reads the pristine XML from skins/skin.majan/1080i and writes skins/skin.duotone/1080i:
  * majan.* setting/property prefix -> duotone.*, Majan_ include names -> DT_, playlist names
  * removed Majan settings collapse to constants (rounded corners, focus outline, accent,
    artwork background all disappear: Duotone has one look)
  * every Majan colour NAME used in a colour context -> a Duotone colour or section variable
  * Majan font names -> Duotone font names (Font.xml from make_fontxml.py)

After this pass every window is redesigned by hand. DO NOT re-run: it overwrites 1080i/.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skin.majan" / "1080i"
DST = ROOT / "skin.duotone" / "1080i"

V = lambda n: f"$VAR[{n}]"  # noqa: E731
COLOR_MAP = {
    "text_primary": V("SectionText"), "text_body": V("SectionText"),
    "text_secondary": V("SectionText2"), "text_tertiary": V("SectionText3"),
    "accent": "ink", "accent_signal": "ink",
    "hairline": "ink", "hairline_soft": "ink_20", "hairline_art": "ink",
    "hairline_strong": "ink", "hairline_art_strong": "ink",
    "border_control": "ink", "border_button": "ink",
    "ink": "paper", "bg": V("SectionColor"), "bg_raised": "ink_12", "bg_ghost": "ink_12",
    "disabled": V("SectionText3"), "scrim": "ink", "scrim_track": "ink", "scrim_tab": "ink",
    "dim_row": V("SectionTint"), "dim_passed": V("SectionTint"), "dim_ahead": V("SectionTint"),
    "dim_dialog": "ink_70", "dim_video": "ink_55",
    "shadow": "clear", "focus_halo": "clear",
    "art_faint": "white", "art_soft": "white", "art_visible": "white",
}
VAR_MAP = {
    "$VAR[ColorAccent]": "ink", "$VAR[ColorRule]": "ink", "$VAR[ColorRuleStrong]": "ink",
    "$VAR[ColorCaption]": V("SectionText3"),
}
FONT_MAP = {
    "mono_13": "cap_20", "mono_14": "cap_20", "mono_15": "cap_20", "mono_17": "cap_20",
    "num_14": "bold_22", "num_16": "bold_22", "num_22": "bold_24", "Mono26": "bold_26", "tab_13": "cap_20",
    "small_16": "ui_22", "small_19": "ui_22", "small_19_bold": "bold_22",
    "card_21": "ui_22", "card_21_medium": "ui_22", "card_21_bold": "bold_22",
    "credits_21": "ui_22", "credits_22": "ui_22", "credits_21_semibold": "bold_22",
    "body_23": "body_24", "body_25": "body_24", "body_26": "body_26",
    "button_23_bold": "btn_24", "button_23_semibold": "btn_24",
    "section_24": "cap_24", "label_25_semibold": "bold_26", "label_25_bold": "bold_26",
    "menu_26_bold": "bold_26", "menu_26_medium": "ui_26",
    "title_28_bold": "bold_28", "title_28_medium": "ui_28", "title_28_semibold": "bold_28",
    "stat_30": "an_40", "clock_34": "an_48", "header_34": "an_48",
    "display_48": "an_60", "display_64": "an_72", "display_68": "an_72",
    "display_72": "an_72", "display_92": "an_104", "display_100": "an_104", "ghost_220": "an_232",
}
COLOR_TAGS = "textcolor|focusedcolor|selectedcolor|disabledcolor|shadowcolor|invalidcolor|colordiffuse|color|controllerdiffuse|backgroundcolor"


def transform(s: str) -> str:
    names = "|".join(sorted(COLOR_MAP, key=len, reverse=True))
    s = re.sub(rf'\b({COLOR_TAGS})="({names})"', lambda m: f'{m.group(1)}="{COLOR_MAP[m.group(2)]}"', s)
    s = re.sub(rf'<({COLOR_TAGS})>({names})</', lambda m: f'<{m.group(1)}>{COLOR_MAP[m.group(2)]}</', s)
    s = re.sub(rf'(<value(?: condition="[^"]*")?>)({names})(</value>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]+" value=")({names})("\s*/>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]+">)({names})(</param>)', lambda m: m.group(1) + COLOR_MAP[m.group(2)] + m.group(3), s)
    for old, new in VAR_MAP.items():
        s = s.replace(old, new)
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf'<font>({fn})</font>', lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    # removed settings -> constants
    s = s.replace("!Skin.HasSetting(majan.roundedcorners)", "true").replace("Skin.HasSetting(majan.roundedcorners)", "false")
    # names
    s = s.replace("TMDbHelper.MajanPlayer", "TMDbHelper.DuotonePlayer").replace("prefix=MajanPlayer", "prefix=DuotonePlayer")
    s = s.replace("special://skin/playlists/majan_", "special://skin/playlists/duotone_")
    s = s.replace("majan.", "duotone.").replace("Majan_", "DT_")
    s = s.replace("docs/skin.majan", "docs/skin.duotone").replace("skin.majan", "skin.duotone").replace("Majan", "Duotone")
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
