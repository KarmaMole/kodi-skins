"""Look tokens shared by make_theme.py, tokenize_colours.py and check_tokens.py (docs/skin.duotone/CONVENTIONS.md).

A look token is a colour that changes with the Look setting (Colour / Light / Dark). colors/defaults.xml holds
it three times (co_<t>, lt_<t>, dk_<t>); 1080i/Includes_Theme.xml (make_theme.py) defines a variable <t> that
returns the right name. XML writes $VAR[<t>] in every colour slot.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COLORS = ROOT / "colors" / "defaults.xml"
XML = ROOT / "1080i"
LOOKS = ("co", "lt", "dk")
STATIC = {"white", "black", "clear", "ground_static"}

# XML files written by a generator (edit the generator, not the file); Includes_Theme.xml is make_theme.py's
GENERATED = {"Includes_Theme.xml", "DialogKeyboard.xml", "SkinSettings.xml", "Includes_Titles.xml",
             "Custom_1155_LibraryPanel.xml", "Custom_1156_ViewPicker.xml", "Includes_Library.xml", "Font.xml"}

# colour slots: tags, colordiffuse attributes, [COLOR x] in labels
SLOT_TAGS = ("textcolor", "focusedcolor", "disabledcolor", "selectedcolor", "invalidcolor", "shadowcolor",
             "headlinecolor", "colordiffuse", "backgroundcolor")
SLOT = re.compile(r"<(%s)>([^<]*)<|colordiffuse=\"([^\"]*)\"|\[COLOR ([^\]]+)\]" % "|".join(SLOT_TAGS))


def palette():
    """{name: AARRGGBB} from colors/defaults.xml."""
    return {m.group(1): m.group(2).lower() for m in
            re.finditer(r'<color name="([a-z_0-9]+)">([0-9a-fA-F]{8})</color>', COLORS.read_text(encoding="utf-8"))}


def tokens():
    """Look tokens in defaults.xml order; asserts every co_ token has lt_ and dk_ twins (and no orphans)."""
    pal = palette()
    names = [n[3:] for n in pal if n.startswith("co_")]
    for look in ("lt", "dk"):
        missing = [n for n in names if f"{look}_{n}" not in pal]
        assert not missing, f"co_ tokens without a {look}_ twin: {missing}"
        orphans = [n for n in pal if n.startswith(look + "_") and n[3:] not in names]
        assert not orphans, f"{look}_ colours without a co_ twin: {orphans}"
    return names


def rgba(hex8):
    """AARRGGBB -> (r, g, b, a) for PIL."""
    a, r, g, b = (int(hex8[i:i + 2], 16) for i in (0, 2, 4, 6))
    return r, g, b, a
