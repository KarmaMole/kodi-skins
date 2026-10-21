"""Generate 1080i/SkinSettings.xml + Includes_SkinSettings.xml (SPEC 14).   python skins/skin.vernissage/_src/make_skinsettings.py

Layout, ids and keywords: docs/skin.vernissage/screens/Settings.md. One column of rows (grouplist 9300 at 120, 196):
label left, current value right (label2, inside the fixed-width button: a value change never moves anything).
Left / Right step the value and apply at once; OK steps forward. Up / Down walk the rows and stop at the ends. The
focused row lifts onto the card ground with its 1 px card_edge and a 2 px ink hairline under it, text ink (no colour,
SPEC 2.1; screens/README 4). The note for the focused row sits on the wall at the right, and under it a small live
sample of the lit work at the current light step (frame, mat, a blank print, the Evening pool / Day shadow) with the
step's name: it changes the moment Room or Evening begins changes (screens/Settings.md "Room sample", drawn with the
room tokens instead of the requested room_sample_<step>.png textures, which a palette change would leave stale).
Restore defaults opens a confirm card with "No" first and focused (9311 No / 9312 Yes). Nothing needs a
reload: every setting is read at run time (the Room changes the whole skin at once, LESSONS Groove M1).
Settings, keys and defaults are listed in docs/skin.vernissage/SETTINGS.md; this table is the source of truth.
"""
from __future__ import annotations

from pathlib import Path

import strip_defaults  # _src/, next to this script

X = Path(__file__).resolve().parents[1] / "1080i"
OUT, INC = X / "SkinSettings.xml", X / "Includes_SkinSettings.xml"
HELPER = "script.karmamole.helper"
HAS_HELPER = "$EXP[HasKMHelper]"   # Includes_Vernissage.xml (a control <visible> expands $EXP)
AUTO = "!String.IsEqual(Skin.String(vernissage.room),day) + !String.IsEqual(Skin.String(vernissage.room),evening)"
GRID, CONFIRM, NO, YES, DIVIDER = 9300, 9310, 9311, 9312, 9399

# id, label string, kind, key, values [(stored, label string)], help string, visible, icon
#   kind "string": Skin.String(key), the FIRST value is the default (it also matches an empty string) and is stored as
#   an explicit keyword (LESSONS Void); "bool": Skin.HasSetting(key) [off, on]; "boolinv": stored inverted (default on)
ROWS = [
    (9301, 31551, "string", "vernissage.room", [("auto", 31552), ("day", 31553), ("evening", 31554)], 31570, None, "skin"),
    (9302, 31555, "string", "vernissage.evening", [("h17", 31556), ("h18", 31557), ("sunset", 31558)], 31571, AUTO, "runtime"),
    (9303, 31559, "boolinv", "vernissage.noprints", [(False, 31516), (True, 31517)], 31572, None, "pictures"),
    (9304, 31560, "boolinv", "vernissage.warmspot", [(False, 31516), (True, 31517)], 31573, HAS_HELPER, "sun"),
    (9305, 31561, "bool", "vernissage.reducemotion", [(False, 31516), (True, 31517)], 31574, None, "settings"),
]
# The optional helper (Kodi never installs optional add-ons by itself). InstallAddon asks Kodi's own yes/no and finds
# the add-on in the user's repositories. id, label, value, help, icon, visible, onclick
ACTION_ROWS = [
    (9306, 31527, 31531, 31549, "addons", f"!System.HasAddon({HELPER})", f"InstallAddon({HELPER})"),
    (9308, 31528, 31516, 31549, "addons", f"System.HasAddon({HELPER}) + !System.AddonIsEnabled({HELPER})",
     f"EnableAddon({HELPER})"),
]
RESET_ID, RESET_HELP = 9307, 31575
ROW_W, ROW_H = 900, 72
# Restore defaults also clears the screenshot-only step override (SPEC 5; never shown here) and the first-visit view
# flags are left alone (they record what Kodi already saved)
EXTRA_RESET = ["vernissage.debug.step"]


def cond_is(key, stored, values):
    if stored != values[0][0]:
        return f"String.IsEqual(Skin.String({key}),{stored})"
    return "[" + " + ".join(f"!String.IsEqual(Skin.String({key}),{s})" for s, _ in values[1:]) + "]"


def value_var(row):
    rid, _l, kind, key, values, *_ = row
    o = []
    if kind == "string":
        for stored, sid in values[1:]:
            o.append(f'\t\t<value condition="{cond_is(key, stored, values)}">$LOCALIZE[{sid}]</value>')
        o.append(f"\t\t<value>$LOCALIZE[{values[0][1]}]</value>")
    elif kind == "bool":
        o.append(f'\t\t<value condition="Skin.HasSetting({key})">$LOCALIZE[{values[1][1]}]</value>')
        o.append(f"\t\t<value>$LOCALIZE[{values[0][1]}]</value>")
    else:  # boolinv: set = off
        o.append(f'\t\t<value condition="Skin.HasSetting({key})">$LOCALIZE[{values[0][1]}]</value>')
        o.append(f"\t\t<value>$LOCALIZE[{values[1][1]}]</value>")
    return f'\t<variable name="SkinSet_Value_{rid}">\n' + "\n".join(o) + "\n\t</variable>"


def actions(row):
    rid, _l, kind, key, values, *_ = row
    o = []
    if kind == "string":
        n = len(values)
        for i, (stored, _s) in enumerate(values):
            c = cond_is(key, stored, values)
            nxt, prv = values[(i + 1) % n][0], values[(i - 1) % n][0]
            for tag, v in (("onright", nxt), ("onclick", nxt), ("onleft", prv)):
                o.append(f'\t\t\t\t<{tag} condition="{c}">Skin.SetString({key},{v})</{tag}>')
    else:
        for tag in ("onright", "onclick", "onleft"):
            o.append(f"\t\t\t\t<{tag}>Skin.ToggleSetting({key})</{tag}>")
    return "\n".join(o)


def row_look():
    """A placard row (900 x 72): label at x 88 after the icon (ink2, ink on focus), value right-aligned; focus = the
    card ground (the edge and the 2 px ink hairline are drawn by the row's overlay group), the resting rows a rule
    hairline."""
    return f"""				<width>{ROW_W}</width>
				<height>{ROW_H}</height>
				<font>font_body</font>
				<textoffsetx>88</textoffsetx>
				<aligny>center</aligny>
				<textcolor>$VAR[ink2]</textcolor>
				<focusedcolor>$VAR[ink]</focusedcolor>
				<texturefocus colordiffuse="$VAR[card]">vn/white.png</texturefocus>
				<texturenofocus border="0,0,0,3" colordiffuse="$VAR[rule]">vn/row_rule.png</texturenofocus>"""


def icon_xml(rid, icon, vis=None):
    """The row's icon over the button: a group pulled back by the row height (net height 0 in the grouplist). It also
    draws the focused row's card edge and its 2 px ink hairline (a button has one focus texture: the card ground)."""
    v = f"\n\t\t\t\t<visible>{vis}</visible>" if vis else ""
    return f"""			<control type="group" id="{rid + 50}">
				<top>-{ROW_H}</top>
				<width>{ROW_W}</width>
				<height>{ROW_H}</height>{v}
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{ROW_W}</width>
					<height>{ROW_H}</height>
					<texture border="4" colordiffuse="$VAR[card_edge]">vn/card_edge.png</texture>
					<visible>Control.HasFocus({rid})</visible>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{ROW_W}</width>
					<height>{ROW_H}</height>
					<texture border="0,0,0,3" colordiffuse="$VAR[ink]">vn/row_rule.png</texture>
					<visible>Control.HasFocus({rid})</visible>
				</control>
				<control type="image">
					<left>20</left>
					<top>14</top>
					<width>44</width>
					<height>44</height>
					<texture colordiffuse="$VAR[ink]">vn/icons/{icon}.png</texture>
					<visible>Control.HasFocus({rid})</visible>
				</control>
				<control type="image">
					<left>20</left>
					<top>14</top>
					<width>44</width>
					<height>44</height>
					<texture colordiffuse="$VAR[ink2]">vn/icons/{icon}.png</texture>
					<visible>!Control.HasFocus({rid})</visible>
				</control>
			</control>"""


def row_xml(row):
    rid, sid, _k, _key, _v, _h, vis, icon = row
    v = f"\n\t\t\t\t<visible>{vis}</visible>" if vis else ""
    return f"""			<control type="button" id="{rid}">
{row_look()}
				<label>$LOCALIZE[{sid}]</label>
				<label2>$VAR[SkinSet_Value_{rid}]</label2>{v}
{actions(row)}
			</control>
{icon_xml(rid, icon, vis)}"""


def action_row_xml(row):
    rid, sid, vid, _h, icon, vis, onclick = row
    return f"""			<control type="button" id="{rid}">
{row_look()}
				<label>$LOCALIZE[{sid}]</label>
				<label2>$LOCALIZE[{vid}]</label2>
				<visible>{vis}</visible>
				<onclick>{onclick}</onclick>
			</control>
{icon_xml(rid, icon, vis)}"""


def confirm_button(cid, label, actions_, left, right):
    acts = "\n".join(f"\t\t\t\t\t<onclick>{a}</onclick>" for a in actions_)
    return f"""				<control type="button" id="{cid}">
					<width>240</width>
					<height>64</height>
					<font>font_body</font>
					<align>center</align>
					<aligny>center</aligny>
					<textcolor>$VAR[ink2]</textcolor>
					<focusedcolor>$VAR[ink]</focusedcolor>
					<texturefocus border="0,0,0,3" colordiffuse="$VAR[ink]">vn/row_rule.png</texturefocus>
					<texturenofocus />
					<label>{label}</label>
					<onleft>{left}</onleft>
					<onright>{right}</onright>
					<onback>{RESET_ID}</onback>
{acts}
				</control>"""


def room_sample():
    """The room sample (screens/Settings.md: 1100, 420, 700 x 394): the lit work at the current light step, drawn
    live with the room tokens: Day shadow / Evening pool (their step fades), hairline frame, mat, a blank print."""
    sx, sy, sw, sh = 1100, 420, 700, 394
    aw, ah, mat = 140, 210, 10
    fw, fh = aw + 2 * (mat + 2), ah + 2 * (mat + 2)
    fx, fy = (sw - fw) // 2, (sh - fh) // 2
    pw, ph = round(2.05 * fw), round(1.5 * fh)
    px, py = sw // 2 - pw // 2, round(sh / 2 - 0.03 * fh - ph / 2)
    return f"""			<!-- the room sample: the lit work at the current light step (live), and the step's name -->
			<control type="group">
				<left>{sx}</left>
				<top>{sy}</top>
				<width>{sw}</width>
				<height>{sh}</height>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{sw}</width>
					<height>{sh}</height>
					<texture border="4" colordiffuse="$VAR[card_edge]">vn/card_edge.png</texture>
				</control>
				<include content="VN_Pool">
					<param name="left" value="{px}"/>
					<param name="top" value="{py}"/>
					<param name="width" value="{pw}"/>
					<param name="height" value="{ph}"/>
				</include>
				<control type="group">
					<left>{fx}</left>
					<top>{fy}</top>
					<width>{fw}</width>
					<height>{fh}</height>
					<include content="VN_LitWork">
						<param name="width" value="{fw}"/>
						<param name="height" value="{fh}"/>
						<param name="shadow_w" value="{fw + 112}"/>
						<param name="shadow_h" value="{fh + 112}"/>
						<param name="mat" value="{mat}"/>
						<param name="art_x" value="{mat + 2}"/>
						<param name="art" value="vn/print_blank.png"/>
					</include>
				</control>
			</control>
			<control type="label">
				<left>{sx}</left>
				<top>{sy + sh + 16}</top>
				<width>{sw}</width>
				<height>38</height>
				<font>font_small</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$LOCALIZE[31584]  ·  $VAR[SkinSet_StepName]</label>
			</control>"""


def main():
    keys = [r[3] for r in ROWS] + EXTRA_RESET
    resets = [f"Skin.Reset({k})" for k in keys] + [f"SetFocus({RESET_ID})"]
    help_text = "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">$LOCALIZE[{r[5]}]</value>' for r in ROWS)
    help_text += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">$LOCALIZE[{r[3]}]</value>' for r in ACTION_ROWS)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_skinsettings.py - edit the table there, then re-run. docs/skin.vernissage/screens/Settings.md,
     docs/skin.vernissage/SETTINGS.md.
     Focus map: rows {ROWS[0][0]}-{RESET_ID} in grouplist {GRID} (Up / Down walk and stop at the ends; Left / Right / OK change the
     value); Restore defaults -> confirm card {CONFIRM}: {NO} No (first, focused) / {YES} Yes, Back -> {RESET_ID}. Back on a row leaves (Kodi). -->
<window>
	<defaultcontrol always="true">{ROWS[0][0]}</defaultcontrol>
	<backgroundcolor>wall_static</backgroundcolor>
	<controls>
		<include>VN_Room</include>
		<control type="group">
			<include>Anim_WindowContent</include>
			<control type="label">
				<left>116</left>
				<top>70</top>
				<width>1300</width>
				<height>66</height>
				<font>font_exhibit</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$LOCALIZE[31564]</label>
			</control>
			<control type="label">
				<left>120</left>
				<top>150</top>
				<width>900</width>
				<height>41</height>
				<font>font_body</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$LOCALIZE[31500]$INFO[System.AddonVersion(skin.vernissage),  ·  ,]</label>
			</control>
			<include>VN_Clock</include>
			<control type="grouplist" id="{GRID}">
				<left>120</left>
				<top>196</top>
				<width>{ROW_W}</width>
				<height>760</height>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
{chr(10).join(row_xml(r) for r in ROWS)}
			<!-- the divider before the action rows: not focusable -->
			<control type="group" id="{DIVIDER}">
				<width>{ROW_W}</width>
				<height>40</height>
				<control type="image">
					<left>36</left>
					<top>19</top>
					<width>vn_rule_w</width>
					<height>vn_rule_h</height>
					<texture colordiffuse="$VAR[placard_rule]">vn/white.png</texture>
				</control>
			</control>
{chr(10).join(action_row_xml(r) for r in ACTION_ROWS)}
			<control type="button" id="{RESET_ID}">
{row_look()}
				<label>$LOCALIZE[31525]</label>
				<onclick>SetFocus({NO})</onclick>
			</control>
{icon_xml(RESET_ID, "update")}
			</control>
			<!-- the note for the focused row, on the wall at the right (4 lines of 38) -->
			<control type="textbox">
				<left>1100</left>
				<top>196</top>
				<width>700</width>
				<height>152</height>
				<font>font_small</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$VAR[SkinSet_HelpText]</label>
			</control>
{room_sample()}
		</control>
		<!-- Restore defaults? "No" first and focused. Always processed (a hidden control can't take focus), faded in
		     while it has focus; drawn last, over everything (LESSONS Groove pass 2). -->
		<control type="group" id="{CONFIRM}">
			<animation effect="fade" start="100" end="0" time="150" condition="!ControlGroup({CONFIRM}).HasFocus()">Conditional</animation>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<texture colordiffuse="$VAR[scrim]">vn/white.png</texture>
			</control>
			<control type="group">
				<left>560</left>
				<top>390</top>
				<include content="VN_PlacardCard">
					<param name="width" value="800"/>
					<param name="height" value="300"/>
				</include>
				<control type="label">
					<left>40</left>
					<top>34</top>
					<width>720</width>
					<height>44</height>
					<font>font_placard</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$LOCALIZE[31563]</label>
				</control>
				<control type="textbox">
					<left>40</left>
					<top>90</top>
					<width>720</width>
					<height>76</height>
					<font>font_small</font>
					<textcolor>$VAR[ink2]</textcolor>
					<label>$LOCALIZE[{RESET_HELP}]</label>
				</control>
				<control type="grouplist" id="{CONFIRM + 3}">
					<left>40</left>
					<top>200</top>
					<width>720</width>
					<height>64</height>
					<orientation>horizontal</orientation>
					<itemgap>16</itemgap>
{confirm_button(NO, "$LOCALIZE[31630]", [f"SetFocus({RESET_ID})"], NO, YES)}
{confirm_button(YES, "$LOCALIZE[31525]", resets, NO, YES)}
				</control>
			</control>
		</control>
	</controls>
</window>
"""
    inc = ["\t" + value_var(r).lstrip("\t") for r in ROWS]
    inc.append("""	<variable name="SkinSet_StepName">
		<value condition="$EXP[VN_S0]">$LOCALIZE[31581]</value>
		<value condition="$EXP[VN_S4]">$LOCALIZE[31583]</value>
		<value>$LOCALIZE[31582]</value>
	</variable>""")
    inc.append(f"""	<variable name="SkinSet_HelpText">
{help_text}
		<value condition="Control.HasFocus({RESET_ID})">$LOCALIZE[{RESET_HELP}]</value>
	</variable>""")
    # the include file first: strip_defaults reads the skin's includes to see which tags a control's includes bring
    INC.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by _src/make_skinsettings.py -->\n<includes>\n'
                   + "\n".join(inc) + "\n</includes>\n", encoding="utf-8", newline="\n")
    xml, _ = strip_defaults.strip(xml)   # tags that only repeat Defaults.xml (official review xml.redundant)
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, INC.name)


if __name__ == "__main__":
    main()
