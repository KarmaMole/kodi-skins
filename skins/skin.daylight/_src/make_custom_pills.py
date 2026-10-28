"""Generate 1080i/Includes_CustomMenuPills.xml: custom main-menu items as nav pills on Home (0.9.17,
docs/CUSTOM_MENU_BRIEF_2026-10-28.md; slots / strings / picker: Includes_CustomMenu.xml from
tools/customrows/make_customrows.py).

The top-line pills are absolutely placed and anchored at the gear (DL_NavPills, Includes_Common.xml). Custom pills
1-3 sit between Search and the gear; everything to their left slides left by their widths, exactly like a hidden
pill makes the row slide right (time-0 Conditional slides add up). A Kodi pill can't take the width of an unknown
label, so a custom pill takes the narrowest of a few fixed widths its name fits in (probe textboxes: NumPages > 1 =
the name needs a second line at that width; the same trick as Duotone's titles), capped by how many custom pills show
so the row never reaches the mood line on the left (1 pill <= 260, 2 <= 220, 3 <= 150; longer names are cut).

Home only: the library windows keep their own top line (Options + the library pills), with no room for more.
Ids: pills 9011-9013 (Home), probes 7500-7533.   Usage: python skins/skin.daylight/_src/make_custom_pills.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_CustomMenuPills.xml"
W = [120, 150, 180, 220, 260]     # pill widths (text + 2 x 22 px padding, as the built-in pills)
CAP = {1: 260, 2: 220, 3: 150}    # widest pill while 1 / 2 / 3 custom pills show
GAP = 6
GEAR_X = 1582
PILL_ID = {1: 9011, 2: 9012, 3: 9013}


def pid(slot, w):
    return 7500 + 10 * slot + W.index(w)


def too_long(slot, w):
    return f"Integer.IsGreater(Container({pid(slot, w)}).NumPages,1)"


def tier_expr(slot, w):
    """slot uses width w: it shows, w is allowed at the current count, the name fits w (unless w is the cap) and
    does not fit the next narrower width"""
    terms = []
    for count, cap in CAP.items():
        if w > cap:
            continue
        c = [f"$EXP[CustomMenuCount{count}]"]
        i = W.index(w)
        if w < cap:
            c.append("!" + too_long(slot, w))
        if i > 0:
            c.append(too_long(slot, W[i - 1]))
        terms.append("[" + " + ".join(c) + "]")
    return f"$EXP[CustomMenu{slot}On] + [" + " | ".join(terms) + "]"


def shift(first):
    """time-0 slides: left by every shown custom pill from slot `first` on"""
    out = []
    for slot in range(first, 4):
        for w in W:
            out.append(f'\t\t<animation effect="slide" start="0,0" end="-{w + GAP},0" time="0" '
                       f'condition="$EXP[DL_CMTier{slot}_{w}]">Conditional</animation>')
    return out


def pill(slot):
    i = PILL_ID[slot]
    left = PILL_ID[slot - 1] if slot > 1 else "$PARAM[p]5"
    right = PILL_ID[slot + 1] if slot < 3 else "$PARAM[p]6"
    out = ["\t\t\t<control type=\"group\">", f"\t\t\t\t<left>{GEAR_X}</left>", "\t\t\t\t<top>topbar_item_top</top>",
           "\t\t\t\t<width>260</width>", "\t\t\t\t<height>52</height>", f"\t\t\t\t<visible>$EXP[CustomMenu{slot}On]</visible>",
           f'\t\t\t\t<include>DL_CMShift{slot}</include>',
           f'\t\t\t\t<control type="button" id="{i}">', "\t\t\t\t\t<left>0</left>", "\t\t\t\t\t<top>0</top>",
           f"\t\t\t\t\t<width>{W[0]}</width>", "\t\t\t\t\t<height>52</height>", "\t\t\t\t\t<label></label>",
           "\t\t\t\t\t<texturefocus />", "\t\t\t\t\t<texturenofocus />",
           f"\t\t\t\t\t<onclick>SetProperty(daylight.custommenu,{slot},home)</onclick>",
           f'\t\t\t\t\t<include content="CustomMenu_OnClick"><param name="item" value="{slot}"/></include>',
           f"\t\t\t\t\t<onleft>{left}</onleft>", f"\t\t\t\t\t<onright>{right}</onright>",
           "\t\t\t\t\t<ondown>$PARAM[ondown]</ondown>", "\t\t\t\t</control>"]
    for w in W:
        out += [f"\t\t\t\t<control type=\"group\">", f"\t\t\t\t\t<width>{w}</width>", "\t\t\t\t\t<height>52</height>",
                f"\t\t\t\t\t<visible>$EXP[DL_CMTier{slot}_{w}]</visible>",
                "\t\t\t\t\t<control type=\"image\">", "\t\t\t\t\t\t<left>0</left>", "\t\t\t\t\t\t<top>0</top>",
                f"\t\t\t\t\t\t<width>{w}</width>", "\t\t\t\t\t\t<height>52</height>",
                '\t\t\t\t\t\t<texture border="26,0,26,0" colordiffuse="$VAR[DL_Accent]">daylight/pill_52.png</texture>',
                f"\t\t\t\t\t\t<visible>Control.HasFocus({i})</visible>", "\t\t\t\t\t</control>"]
        for vis, col in ((f"!Control.HasFocus({i})", "$VAR[DL_Ink2]"), (f"Control.HasFocus({i})", "$VAR[DL_OnAccent]")):
            out += ["\t\t\t\t\t<control type=\"label\">", "\t\t\t\t\t\t<left>22</left>", "\t\t\t\t\t\t<top>0</top>",
                    f"\t\t\t\t\t\t<width>{w - 44}</width>", "\t\t\t\t\t\t<height>52</height>", "\t\t\t\t\t\t<align>center</align>",
                    "\t\t\t\t\t\t<aligny>center</aligny>", "\t\t\t\t\t\t<font>ui_22_semibold</font>",
                    f"\t\t\t\t\t\t<textcolor>{col}</textcolor>", f"\t\t\t\t\t\t<label>$VAR[CustomMenu_Label{slot}]</label>",
                    f"\t\t\t\t\t\t<visible>{vis}</visible>", "\t\t\t\t\t</control>"]
        out.append("\t\t\t\t</control>")
    out.append("\t\t\t</control>")
    return out


def main():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         "<!-- GENERATED by _src/make_custom_pills.py - edit the generator, not this file. Custom main-menu items as",
         "     Home nav pills between Search and the gear (see the generator's docstring). -->", "<includes>"]
    for slot in (1, 2, 3):
        for w in W:
            L.append(f'\t<expression name="DL_CMTier{slot}_{w}">{tier_expr(slot, w)}</expression>')
    for first in (1, 2, 3):
        L.append(f'\t<include name="DL_CMShift{first}">')
        L += shift(first)
        L.append("\t</include>")
    L += ["\t<!-- the pills (params p = the pill id prefix of DL_NavPills, ondown) -->", '\t<include name="DL_CustomMenuPills">',
          "\t\t<definition>"]
    for slot in (1, 2, 3):
        L += pill(slot)
    L += ["\t\t</definition>", "\t</include>",
          "\t<!-- clear probes, one per slot and width: NumPages > 1 = the name doesn't fit that pill on one line -->",
          '\t<include name="DL_CustomMenuProbes">', "\t\t<control type=\"group\">", "\t\t\t<left>0</left>",
          "\t\t\t<top>0</top>", "\t\t\t<width>300</width>", "\t\t\t<height>40</height>"]
    for slot in (1, 2, 3):
        for w in W[:-1]:
            L += [f'\t\t\t<control type="textbox" id="{pid(slot, w)}">', "\t\t\t\t<left>0</left>", "\t\t\t\t<top>0</top>",
                  f"\t\t\t\t<width>{w - 44}</width>", "\t\t\t\t<height>40</height>", "\t\t\t\t<font>ui_22_semibold</font>",
                  "\t\t\t\t<textcolor>00000000</textcolor>", f"\t\t\t\t<label>$VAR[CustomMenu_Label{slot}]</label>",
                  f"\t\t\t\t<visible>$EXP[CustomMenu{slot}On]</visible>", "\t\t\t</control>"]
    L += ["\t\t</control>", "\t</include>", "</includes>", ""]
    OUT.write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
