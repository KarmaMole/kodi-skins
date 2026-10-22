"""Generate 1080i/SkinSettings.xml + Includes_SkinSettings.xml (SPEC 14).   python skins/skin.groove/_src/make_skinsettings.py

One row = one button in a vertical grouplist (9500): label left, current value right (label2). Left / Right step
through the values and apply at once; OK steps forward. Up / Down move between rows (the grouplist), Back leaves.
Focused row is lit (soft glow + ink); the note on the right explains it. Nothing needs a skin reload: every setting
is read at run time (Room recolours the whole skin instantly). Settings and values: docs/skin.groove/SETTINGS.md.
M4 redraws this window in its final look (icons + labels); the table stays the source of truth.
"""
from pathlib import Path

import strip_defaults  # _src/, next to this script

X = Path(__file__).resolve().parents[1] / "1080i"
OUT, INC = X / "SkinSettings.xml", X / "Includes_SkinSettings.xml"

# id, label string, kind, key, values [(stored, label string)] in display order ("" = default), help string, visible
#   kind "string": Skin.String(key); "bool": Skin.HasSetting(key) (values [off, on]); "boolinv": stored inverted
ROWS = [
    (9501, 31501, "bool", "groove.light", [(False, 31502), (True, 31503)], 31540, None),
    (9502, 31504, "string", "groove.record", [("", 31505), ("vinyl", 31506)], 31541, None),
    (9503, 31507, "string", "groove.glow", [("soft", 31508), ("", 31509), ("vivid", 31510)], 31542, None),
    (9504, 31511, "string", "groove.npopen", [("", 31504), ("last", 31512)], 31543, None),
    (9505, 31513, "string", "groove.mini", [("", 31514), ("still", 31515), ("off", 31516)], 31544, None),
    (9506, 31518, "bool", "groove.reducemotion", [(False, 31516), (True, 31517)], 31545, None),
    (9507, 31519, "boolinv", "groove.notmdbcolours", [(False, 31516), (True, 31517)], 31546,
     "System.HasAddon(plugin.video.themoviedb.helper)"),
    (9508, 31520, "string", "groove.osdhide", [("3", 31521), ("", 31522), ("10", 31523), ("off", 31524)], 31547, None),
    # 1.0.2 main menu (HideMenu.*): the rail icons on Home. Settings always stays.
    (9514, 31650, "bool", "HideMenu.Music", [(False, 31654), (True, 31655)], 31656, None),
    (9515, 31651, "bool", "HideMenu.Movies", [(False, 31654), (True, 31655)], 31656, None),
    (9516, 31652, "bool", "HideMenu.TVShows", [(False, 31654), (True, 31655)], 31656, None),
    (9517, 31653, "bool", "HideMenu.Search", [(False, 31654), (True, 31655)], 31657, None),
]
RESET_ID, RESET_HELP = 9509, 31548
# 1.0.2 custom rows on Home (Includes_CustomRows.xml): OK opens the row's options (choose / rename / clear); the value
# is what the row shows. Not touched by Restore defaults. id, row number
CUSTOM = [(9518, 1), (9519, 2), (9520, 3)]
# Action rows for Groove's optional companions (Kodi never installs optional add-ons by itself). Shown only while the
# add-on is missing (Install) or installed but disabled (Enable); InstallAddon asks Kodi's own yes/no and finds the
# add-on in the user's repositories (KarmaMole's). id, label string, value string, help string, icon, visible, onclick
HELPER, VIZ = "script.karmamole.helper", "service.vizpalette"
ACTION_ROWS = [
    (9510, 31527, 31531, 31549, "addons", f"!System.HasAddon({HELPER})", f"InstallAddon({HELPER})"),
    (9511, 31528, 31516, 31549, "addons", f"System.HasAddon({HELPER}) + !System.AddonIsEnabled({HELPER})",
     f"EnableAddon({HELPER})"),
    (9512, 31529, 31531, 31550, "visualiser", f"!System.HasAddon({VIZ})", f"InstallAddon({VIZ})"),
    (9513, 31530, 31516, 31550, "visualiser", f"System.HasAddon({VIZ}) + !System.AddonIsEnabled({VIZ})",
     f"EnableAddon({VIZ})"),
]
# row icon (media/icons/<name>.png), drawn by an overlay group after each row button (skin-developer, M4)
ICONS = {9501: "skin", 9502: "record", 9503: "glow", 9504: "play", 9505: "music", 9506: "system",
         9507: "films", 9508: "runtime", 9509: "update", 9514: "music", 9515: "films", 9516: "tv", 9517: "search"}
ICONS.update({r[0]: r[4] for r in ACTION_ROWS})
ICONS.update({cid: "favourites" for cid, _n in CUSTOM})
ROW_W, ROW_H, ROW_GAP = 1000, 72, 8
EXTRA_RESET = ["groove.np.viz"]  # runtime state that Restore defaults also clears


def cond_is(key, stored, values):
    if stored:
        return f"String.IsEqual(Skin.String({key}),{stored})"
    others = [s for s, _ in values if s]
    return "[" + " + ".join(f"!String.IsEqual(Skin.String({key}),{s})" for s in others) + "]"


def value_var(row):
    rid, _l, kind, key, values, *_ = row
    o = []
    if kind == "string":
        for stored, sid in values:
            if stored:
                o.append(f'\t\t<value condition="{cond_is(key, stored, values)}">$LOCALIZE[{sid}]</value>')
        default = [sid for s, sid in values if not s][0]
        o.append(f"\t\t<value>$LOCALIZE[{default}]</value>")
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
            set_n = f"Skin.SetString({key},{nxt})" if nxt else f"Skin.Reset({key})"
            set_p = f"Skin.SetString({key},{prv})" if prv else f"Skin.Reset({key})"
            for tag, act in (("onright", set_n), ("onclick", set_n), ("onleft", set_p)):
                o.append(f'\t\t\t\t<{tag} condition="{c}">{act}</{tag}>')
    else:
        for tag in ("onright", "onclick", "onleft"):
            o.append(f"\t\t\t\t<{tag}>Skin.ToggleSetting({key})</{tag}>")
    return "\n".join(o)


def row_look():
    """One Groove row (M4): the lit band (row_focus tinted ink: a 12 % band + a solid edge, reads in Dark and Light),
    label at x 88 after the icon, value right-aligned (ink2, ink on focus)."""
    return f"""				<width>{ROW_W}</width>
				<height>{ROW_H}</height>
				<font>font_label</font>
				<textoffsetx>88</textoffsetx>
				<aligny>center</aligny>
				<textcolor>$VAR[ink2]</textcolor>
				<focusedcolor>$VAR[ink]</focusedcolor>
				<texturefocus border="8,0,0,0" colordiffuse="$VAR[ink]">groove/row_focus.png</texturefocus>
				<texturenofocus />"""


def icon_xml(rid, vis=None):
    """The row's icon, over the button: a group shifted back by the row height (net height = the gap)."""
    v = f"\n\t\t\t\t<visible>{vis}</visible>" if vis else ""
    icon = ICONS[rid]
    return f"""			<control type="group" id="{rid + 50}">
				<top>-{ROW_H}</top>
				<width>{ROW_W}</width>
				<height>{ROW_H + ROW_GAP}</height>{v}
				<control type="image">
					<left>24</left>
					<top>16</top>
					<width>40</width>
					<height>40</height>
					<texture colordiffuse="$VAR[ink]">icons/{icon}.png</texture>
					<visible>Control.HasFocus({rid})</visible>
				</control>
				<control type="image">
					<left>24</left>
					<top>16</top>
					<width>40</width>
					<height>40</height>
					<texture colordiffuse="$VAR[icon_rest]">icons/{icon}.png</texture>
					<visible>!Control.HasFocus({rid})</visible>
				</control>
			</control>"""


def row_xml(row):
    rid, sid, *_r, vis = row
    v = f"\n\t\t\t\t<visible>{vis}</visible>" if vis else ""
    return f"""			<control type="button" id="{rid}">
{row_look()}
				<label>$LOCALIZE[{sid}]</label>
				<label2>$VAR[SkinSet_Value_{rid}]</label2>{v}
{actions(row)}
			</control>
{icon_xml(rid, vis)}"""


def custom_row_xml(cid, n):
    return f"""			<control type="button" id="{cid}">
{row_look()}
				<label>$LOCALIZE[{31959 + n}]</label>
				<label2>$VAR[CustomRow_Value{n}]</label2>
				<include content="CustomRows_SettingsClick"><param name="row" value="{n}"/><param name="heading" value="$LOCALIZE[{31959 + n}]"/></include>
			</control>
{icon_xml(cid)}"""


def action_row_xml(row):
    rid, sid, vid, _h, _i, vis, onclick = row
    return f"""			<control type="button" id="{rid}">
{row_look()}
				<label>$LOCALIZE[{sid}]</label>
				<label2>$LOCALIZE[{vid}]</label2>
				<visible>{vis}</visible>
				<onclick>{onclick}</onclick>
			</control>
{icon_xml(rid, vis)}"""


def main():
    keys = [r[3] for r in ROWS] + EXTRA_RESET
    resets = "\n".join(f'\t\t\t\t<onclick condition="!String.IsEmpty(Window(Home).Property(groove.resetarmed))">Skin.Reset({k})</onclick>' for k in keys)
    help_text = "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">$LOCALIZE[{r[5]}]</value>' for r in ROWS)
    help_text += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">$LOCALIZE[{r[3]}]</value>' for r in ACTION_ROWS)
    help_title = "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">$LOCALIZE[{r[1]}]</value>' for r in ROWS + ACTION_ROWS)
    help_text += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({cid})">$LOCALIZE[31950]</value>' for cid, _n in CUSTOM)
    help_title += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({cid})">$LOCALIZE[{31959 + n}]</value>' for cid, n in CUSTOM)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_skinsettings.py - edit the table there, then re-run. Settings: docs/skin.groove/SETTINGS.md -->
<window>
	<defaultcontrol always="true">9500</defaultcontrol>
	<backgroundcolor>ground_static</backgroundcolor>
	<onload>ClearProperty(groove.resetarmed,home)</onload>
	<controls>
		<include>Groove_Room</include>
		<include>CustomRows_FavData</include>
		<control type="group">
			<include>Anim_WindowContent</include>
			<!-- header: the settings icon + its word -->
			<control type="image">
				<left>g_safe_x</left>
				<top>g_header_y</top>
				<width>g_header_icon</width>
				<height>g_header_icon</height>
				<texture colordiffuse="$VAR[ink]">icons/skin.png</texture>
			</control>
			<control type="label">
				<left>160</left>
				<top>g_header_y</top>
				<width>900</width>
				<height>g_header_icon</height>
				<aligny>center</aligny>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$LOCALIZE[31500][COLOR $VAR[ink2]]   $INFO[System.AddonVersion(skin.groove)][/COLOR]</label>
			</control>
			<control type="grouplist" id="9500">
				<left>96</left>
				<top>170</top>
				<width>{ROW_W}</width>
				<height>800</height>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<onup>{RESET_ID}</onup>
				<ondown>{ROWS[0][0]}</ondown>
{chr(10).join(row_xml(r) for r in ROWS)}
{chr(10).join(custom_row_xml(cid, n) for cid, n in CUSTOM)}
{chr(10).join(action_row_xml(r) for r in ACTION_ROWS)}
			<control type="button" id="{RESET_ID}">
{row_look()}
				<label>$VAR[SkinSet_ResetLabel]</label>
				<onunfocus>ClearProperty(groove.resetarmed,home)</onunfocus>
{resets}
				<onclick condition="!String.IsEmpty(Window(Home).Property(groove.resetarmed))">ClearProperty(groove.resetarmed,home)</onclick>
				<onclick condition="String.IsEmpty(Window(Home).Property(groove.resetarmed))">SetProperty(groove.resetarmed,1,home)</onclick>
			</control>
{icon_xml(RESET_ID)}
			</control>
			<!-- the note for the focused setting -->
			<control type="label">
				<left>1200</left>
				<top>182</top>
				<width>624</width>
				<height>48</height>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[SkinSet_HelpTitle]</label>
			</control>
			<control type="textbox">
				<left>1200</left>
				<top>244</top>
				<width>624</width>
				<height>400</height>
				<font>font_body</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$VAR[SkinSet_HelpText]</label>
			</control>
		</control>
	</controls>
</window>
"""
    inc = ["\t" + value_var(r).lstrip("\t") for r in ROWS]
    inc.append(f"""	<variable name="SkinSet_HelpTitle">
{help_title}
		<value condition="Control.HasFocus({RESET_ID})">$LOCALIZE[31525]</value>
	</variable>
	<variable name="SkinSet_HelpText">
{help_text}
		<value condition="Control.HasFocus({RESET_ID})">$LOCALIZE[{RESET_HELP}]</value>
	</variable>
	<variable name="SkinSet_ResetLabel">
		<value condition="!String.IsEmpty(Window(Home).Property(groove.resetarmed))">$LOCALIZE[31526]</value>
		<value>$LOCALIZE[31525]</value>
	</variable>""")
    # the include file first: strip_defaults reads the skin's includes to see which tags a control's includes bring
    INC.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by _src/make_skinsettings.py -->\n<includes>\n'
                   + "\n".join(inc) + "\n</includes>\n", encoding="utf-8", newline="\n")
    xml, _ = strip_defaults.strip(xml)   # tags that only repeat Defaults.xml (official review xml.redundant)
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, INC.name)


if __name__ == "__main__":
    main()
