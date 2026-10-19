"""Six Degrees skin settings -> 1080i/SkinSettings.xml (7 settings, docs/skin.sixdegrees/SETTINGS.md).

One list of rows (vertical grouplist 9500, rows 9510-9516 + reset 9519). Each row is one focus target:
Left / Right step the value and apply at once, OK steps forward (wraps). The value sits in a fixed-width
pill on the right of the row (rule 5: nothing moves when it changes). The card on the right explains the
focused setting. Back leaves (Kodi's own Back).

    python skins/skin.sixdegrees/_src/make_skinsettings.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "SkinSettings.xml"
P = "sixdegrees"

# (id, label, help, kind, setting, [(value, shown)...]) ; kind bool: values [(False, off-label), (True, on-label)]
ROWS = [
    (9510, "Reduce motion",
     "Stations stop sliding and growing: the map, Home and the dialogs change at once. Choose this if movement on the TV feels busy.",
     "bool", f"{P}.reducemotion", [("", "Off"), ("1", "On")]),
    (9511, "Hide the player controls after",
     "The transit sign over a playing film closes itself when you leave the remote alone. Paused films keep it open.",
     "string", f"{P}.osdhide", [("off", "Never"), ("3", "3 seconds"), ("", "5 seconds"), ("10", "10 seconds")]),
    (9512, "Stations on a line",
     "How the films on each line of the map are ordered: the best rated first, or the newest first.",
     "string", f"{P}.map.sort", [("", "Best rated first"), ("year", "Newest first")]),
    (9513, "Only unwatched stations",
     "Every line on the map keeps only the films you have not seen yet. Good for finding something new tonight.",
     "bool", f"{P}.map.unwatched", [("", "Off"), ("1", "On")]),
    (9514, "Map key",
     "The little compass at the bottom left of the map that says which direction rides which line.",
     "bool", f"{P}.map.hidekey", [("", "Shown"), ("1", "Hidden")]),
    (9515, "Trailer button",
     "The Trailer pill on station pages (trailers play through the YouTube add-on).",
     "bool", f"{P}.hidetrailer", [("", "Shown"), ("1", "Hidden")]),
    (9516, "Watched marks",
     "Watched films show a filled stop and a small mark on their posters; turn the marks off for clean artwork.",
     "string", f"{P}.watchedmarkers", [("", "Shown"), ("off", "Hidden")]),
]
ROW_H, ROW_W, X0, Y0 = 84, 1080, 64, 176
PILL_W = 300


def is_value(kind, setting, value):
    if kind == "bool":
        return f"Skin.HasSetting({setting})" if value else f"!Skin.HasSetting({setting})"
    if value == "":
        others = [v for v in ROWS_BY_SETTING[setting] if v != ""]
        return " + ".join(f"!String.IsEqual(Skin.String({setting}),{o})" for o in others)
    return f"String.IsEqual(Skin.String({setting}),{value})"


ROWS_BY_SETTING = {r[4]: [v for v, _ in r[5]] for r in ROWS}


def set_value(kind, setting, value):
    if kind == "bool":
        return f"Skin.SetBool({setting})" if value else f"Skin.Reset({setting})"
    return f"Skin.Reset({setting})" if value == "" else f"Skin.SetString({setting},{value})"


def row(r, prev_id, next_id):
    cid, label, help_, kind, setting, values = r
    n = len(values)
    acts = []
    for i, (v, _shown) in enumerate(values):
        cond = is_value(kind, setting, v)
        nxt = values[(i + 1) % n][0]
        prv = values[(i - 1) % n][0]
        acts.append(f'<onright condition="{cond}">{set_value(kind, setting, nxt)}</onright>')
        acts.append(f'<onclick condition="{cond}">{set_value(kind, setting, nxt)}</onclick>')
        acts.append(f'<onleft condition="{cond}">{set_value(kind, setting, prv)}</onleft>')
    labels = "".join(
        f'<control type="label"><left>{ROW_W - PILL_W - 24}</left><top>0</top><width>{PILL_W}</width><height>{ROW_H}</height>'
        f'<align>center</align><font>semi_24</font><textcolor>ink</textcolor><label>{shown}</label>'
        f"<visible>{is_value(kind, setting, v)} + !Control.HasFocus({cid})</visible></control>"
        f'<control type="label"><left>{ROW_W - PILL_W - 24}</left><top>0</top><width>{PILL_W}</width><height>{ROW_H}</height>'
        f'<align>center</align><font>xb_24</font><textcolor>white</textcolor><label>{shown}</label>'
        f"<visible>{is_value(kind, setting, v)} + Control.HasFocus({cid})</visible></control>"
        for v, shown in values)
    return f"""<control type="group" id="{cid + 100}">
				<width>{ROW_W}</width><height>{ROW_H}</height>
				<control type="button" id="{cid}">
					<left>0</left><top>0</top><width>{ROW_W}</width><height>{ROW_H}</height>
					<font>semi_26</font><textcolor>ink</textcolor><focusedcolor>white</focusedcolor><textoffsetx>32</textoffsetx>
					<texturefocus border="12" colordiffuse="ink">sd/rr12.png</texturefocus>
					<texturenofocus />
					<label>{label}</label>
					<onup>{prev_id}</onup><ondown>{next_id}</ondown>
					{''.join(acts)}
				</control>
				<control type="image"><left>{ROW_W - PILL_W - 24}</left><top>{(ROW_H - 52) // 2}</top><width>{PILL_W}</width><height>52</height>
					<texture border="26" colordiffuse="hair_strong">sd/pill_56_o3.png</texture><visible>!Control.HasFocus({cid})</visible></control>
				<control type="image"><left>{ROW_W - PILL_W - 24}</left><top>{(ROW_H - 52) // 2}</top><width>{PILL_W}</width><height>52</height>
					<texture border="26" colordiffuse="white">sd/pill_56_o3.png</texture><visible>Control.HasFocus({cid})</visible></control>
				<control type="label"><left>{ROW_W - PILL_W - 24 - 40}</left><top>0</top><width>40</width><height>{ROW_H}</height><align>center</align>
					<font>xb_22</font><textcolor>white</textcolor><label>◀</label><visible>Control.HasFocus({cid})</visible></control>
				<control type="label"><left>{ROW_W - 24}</left><top>0</top><width>24</width><height>{ROW_H}</height><align>center</align>
					<font>xb_22</font><textcolor>white</textcolor><label>▶</label><visible>Control.HasFocus({cid})</visible></control>
				{labels}
				<control type="image"><left>24</left><top>{ROW_H - 1}</top><width>{ROW_W - 48}</width><height>1</height>
					<texture colordiffuse="hair">common/white.png</texture></control>
			</control>"""


def main():
    ids = [r[0] for r in ROWS] + [9519]
    rows = []
    for i, r in enumerate(ROWS):
        rows.append(row(r, ids[i - 1] if i else 9519, ids[i + 1]))
    reset = [f"Skin.Reset({r[4]})" if r[3] == "bool" else f"Skin.Reset({r[4]})" for r in ROWS]
    reset_btn = f"""<control type="group" id="9619"><width>{ROW_W}</width><height>{ROW_H + 24}</height>
				<control type="button" id="9519">
					<left>0</left><top>24</top><width>360</width><height>64</height>
					<font>semi_24</font><textcolor>ink</textcolor><focusedcolor>white</focusedcolor><align>center</align><textoffsetx>0</textoffsetx>
					<texturefocus border="32" colordiffuse="ink">sd/pill_64.png</texturefocus>
					<texturenofocus border="32" colordiffuse="hair_strong">sd/pill_64_o3.png</texturenofocus>
					<label>Back to the defaults</label>
					<onup>{ids[-2]}</onup><ondown>{ids[0]}</ondown>
					{''.join(f'<onclick>{a}</onclick>' for a in reset)}
				</control>
			</control>"""
    helps = "".join(
        f'<control type="textbox"><left>0</left><top>120</top><width>520</width><height>220</height>'
        f'<font>reg_26</font><textcolor>body</textcolor><label>{r[2]}</label><visible>Control.HasFocus({r[0]})</visible></control>'
        f'<control type="label"><left>0</left><top>60</top><width>520</width><height>44</height>'
        f'<font>xb_28</font><textcolor>ink</textcolor><label>{r[1]}</label><visible>Control.HasFocus({r[0]})</visible></control>'
        for r in ROWS)
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_skinsettings.py. Six Degrees' own options (7), docs/skin.sixdegrees/SETTINGS.md.
	Rows 9510-9516 (Left / Right step the value and apply, OK steps forward), reset 9519.
-->
<window>
	<defaultcontrol always="true">9510</defaultcontrol>
	<backgroundcolor>ground</backgroundcolor>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>SD_Background</include>
		<include content="SD_TopBar">
			<param name="title" value="$LOCALIZE[31021]"/>
		</include>
		<control type="grouplist" id="9500">
			<left>{X0}</left>
			<top>{Y0}</top>
			<width>{ROW_W}</width>
			<height>860</height>
			<orientation>vertical</orientation>
			<itemgap>0</itemgap>
			{chr(10).join(rows)}
			{reset_btn}
		</control>
		<!-- help card: what the focused setting does -->
		<control type="group">
			<left>1264</left>
			<top>{Y0}</top>
			<control type="image"><left>-60</left><top>-46</top><width>712</width><height>560</height><texture border="90" colordiffuse="shadow">sd/shadow_card.png</texture></control>
			<control type="image"><left>0</left><top>0</top><width>592</width><height>440</height><texture border="20" colordiffuse="card">sd/rr20.png</texture></control>
			<control type="group">
				<left>36</left>
				<top>0</top>
				<control type="label"><left>0</left><top>28</top><width>520</width><height>30</height><font>caps_21</font><textcolor>ink2</textcolor><label>What it does</label></control>
				{helps}
				<control type="label"><left>0</left><top>60</top><width>520</width><height>44</height><font>xb_28</font><textcolor>ink</textcolor><label>Back to the defaults</label><visible>Control.HasFocus(9519)</visible></control>
				<control type="textbox"><left>0</left><top>120</top><width>520</width><height>220</height><font>reg_26</font><textcolor>body</textcolor><label>Every Six Degrees option returns to how it shipped. Kodi's own settings are not touched.</label><visible>Control.HasFocus(9519)</visible></control>
			</control>
			<control type="image"><left>36</left><top>360</top><width>60</width><height>60</height><texture>sd/compass.png</texture></control>
			<control type="label"><left>112</left><top>360</top><width>440</width><height>60</height><font>semi_22</font><textcolor>ink2</textcolor><label>Six Degrees $INFO[System.AddonVersion(skin.sixdegrees)]</label></control>
		</control>
	</controls>
</window>
"""
    OUT.write_text(w, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
