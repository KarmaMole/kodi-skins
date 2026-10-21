"""One-off (idempotent) conversion of hand-written 1080i XML to look tokens (0.9.11, Look setting).

    python skins/skin.duotone/_src/tokenize_colours.py [--check]

Every bare colour name in a colour slot, an include param or a variable <value> becomes $VAR[<token>]:
vermilion / cobalt / acid -> sec_films / sec_series / sec_music, ink* / paper* / tint* keep their names.
A few places get a ROLE token instead (ROLE_EDITS: the Home paper field, search chips, the artist tiles,
the halftone, the watched marker, the framed panel). Generated files are skipped (their generators write
tokens themselves). Kept for the record and for new hand-written XML: run it, then check_tokens.py.
--check: report what would change, write nothing.
"""
from pathlib import Path
import re
import sys

from theme_tokens import GENERATED, SLOT_TAGS, XML, tokens

RENAME = {"vermilion": "sec_films", "cobalt": "sec_series", "acid": "sec_music"}
HEX = {"ff111111": "ground_static", "FF000000": "black", "00ffffff": "clear", "8c888888": "$VAR[track]"}

# (file, old, new, expected count): roles a generic rename can't know
ROLE_EDITS = [
    ("Includes_Home.xml", '<param name="color" value="paper"/>', '<param name="color" value="$VAR[sec_paper]"/>', 2),
    ("Includes_Search.xml", '<param name="chip">vermilion</param>', '<param name="chip">$VAR[chip_films]</param>', 1),
    ("Includes_Search.xml", '<param name="chiptext">ink</param>', '<param name="chiptext">$VAR[chiptext_films]</param>', 1),
    ("Includes_Search.xml", '<param name="chip" value="vermilion"/>', '<param name="chip" value="$VAR[chip_films]"/>', 1),
    ("Includes_Search.xml", '<param name="chip" value="cobalt"/>', '<param name="chip" value="$VAR[chip_series]"/>', 1),
    ("Includes_Search.xml", '<param name="chiptext" value="paper"/>', '<param name="chiptext" value="$VAR[chiptext_series]"/>', 1),
    ("Includes_Search.xml", '<param name="chip" value="acid"/>',
     '<param name="chip" value="$VAR[chip_music]"/>\n\t\t\t\t<param name="chiptext" value="$VAR[chiptext_music]"/>', 2),
    # artist tiles: music chips on the search field
    ("Includes_Search.xml", '<texture colordiffuse="acid">common/white.png</texture>',
     '<texture colordiffuse="$VAR[chip_music]">common/white.png</texture>', 2),
    ("Includes_Search.xml", '<font>bold_22</font>\n\t\t\t\t\t\t\t<textcolor>ink</textcolor>',
     '<font>bold_22</font>\n\t\t\t\t\t\t\t<textcolor>$VAR[chiptext_music]</textcolor>', 1),
    ("Includes_Search.xml", '<value condition="Control.HasFocus(9104)">paper</value>\n\t\t<value>ink</value>',
     '<value condition="Control.HasFocus(9104)">$VAR[paper]</value>\n\t\t<value>$VAR[chiptext_music]</value>', 1),
    # invalid edit text: an identity colour on the field
    ("Defaults.xml", "<invalidcolor>vermilion</invalidcolor>", "<invalidcolor>$VAR[chip_films]</invalidcolor>", 1),
    ("Includes_Settings.xml", "<invalidcolor>vermilion</invalidcolor>", "<invalidcolor>$VAR[chip_films]</invalidcolor>", 1),
]
# every file: textures with baked colour
TEX_EDITS = [
    ('colordiffuse="bfffffff">overlays/dots.png', 'colordiffuse="$VAR[dots]">overlays/dots.png'),
    ("<texture>overlays/dots_art.png</texture>", '<texture colordiffuse="$VAR[dots_art]">overlays/dots_art.png</texture>'),
    ("<texture>markers/watched.png</texture>", "<texture>$VAR[DT_TexWatched]</texture>"),
    ('colordiffuse="$VAR[SectionColor]">dialogs/panel_framed.png', 'colordiffuse="$VAR[DT_PanelTint]">$VAR[DT_PanelTex]'),
    # dialog / menu backdrops: the scrim role (Dark's ink is near-white; an ink_70 veil brightened the TV)
    ('<texture colordiffuse="$VAR[ink_70]">common/white.png</texture>', '<texture colordiffuse="$VAR[scrim]">common/white.png</texture>'),
]


def convert(text, toks):
    def tok(v):
        s = v.strip()
        if s in RENAME:
            return f"$VAR[{RENAME[s]}]"
        if s in toks:
            return f"$VAR[{s}]"
        return HEX.get(s, v)

    def slot(m):
        if m.group(1):
            return f"<{m.group(1)}>{tok(m.group(2))}<"
        if m.group(3) is not None:
            return f'colordiffuse="{tok(m.group(3))}"'
        return f"[COLOR {tok(m.group(4))}]"

    text = re.sub(r"<(%s)>([^<]*)<|colordiffuse=\"([^\"]*)\"|\[COLOR ([^\]$]+)\]" % "|".join(SLOT_TAGS), slot, text)
    # include params and variable values that are exactly a colour name
    text = re.sub(r'(<param name="[^"]*" value=")([a-z_0-9]+)("\s*/>)', lambda m: m.group(1) + tok(m.group(2)) + m.group(3), text)
    text = re.sub(r'(<param name="[^"]*">)([a-z_0-9]+)(</param>)', lambda m: m.group(1) + tok(m.group(2)) + m.group(3), text)
    text = re.sub(r"(<value(?: condition=\"[^\"]*\")?>)([a-z_0-9]+)(</value>)", lambda m: m.group(1) + tok(m.group(2)) + m.group(3), text)
    return text


def main():
    check = "--check" in sys.argv
    toks = set(tokens()) | set(RENAME)
    toks.discard("white")
    changed = 0
    for f in sorted(XML.glob("*.xml")):
        if f.name in GENERATED:
            continue
        s = f.read_text(encoding="utf-8")
        out = s
        for fn, old, new, n in ROLE_EDITS:
            if fn == f.name and old in out:
                assert out.count(old) == n, (fn, old, out.count(old))
                out = out.replace(old, new)
        for old, new in TEX_EDITS:
            out = out.replace(old, new)
        # comments keep their words (vermilion etc. in prose)
        parts = re.split(r"(<!--.*?-->)", out, flags=re.S)
        out = "".join(p if p.startswith("<!--") else convert(p, toks) for p in parts)
        if out != s:
            changed += 1
            print(("would change " if check else "converted ") + f.name)
            if not check:
                f.write_text(out, encoding="utf-8", newline="\n")
    print(f"{changed} file(s)")


if __name__ == "__main__":
    main()
