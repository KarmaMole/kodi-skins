"""Generate 1080i/SkinSettings.xml (Nocturne's eight settings + restore).  python skins/skin.nocturne/_src/make_skinsettings.py

One row = one focus target (button). Left / Right step through the values and apply at once; OK steps forward.
Up / Down move between rows; Back leaves (Kodi). The focused row is lit (glow + bright text); the curator's note on
the right explains the focused setting. Reduce motion reloads the skin from the row itself (Home picks its glide
include at load); focus returns through Window(Home).Property(nocturne.refocus). Never ReloadSkin() in onunload.
Settings and values: docs/skin.nocturne/SETTINGS.md.
"""
from pathlib import Path
from strip_defaults import strip_defaults  # drops tags that repeat Defaults.xml (kdk xml.redundant)
from localize import localize_xml  # literal label words -> $LOCALIZE[id] from strings.po (kdk labels.not-translated)
STRINGS_PO = Path(__file__).resolve().parent.parent / "language" / "resource.language.en_gb" / "strings.po"
DEFAULTS_XML = Path(__file__).resolve().parent.parent / "1080i" / "Defaults.xml"

OUT = Path(__file__).resolve().parents[1] / "1080i" / "SkinSettings.xml"

# id, label, kind, key, values [(stored, label)], help title, help text, reload
#   kind "string": Skin.String(key) values; first value is the default (stored as listed; "" = reset)
#   kind "bool":  values [(False, off-label), (True, on-label)] on Skin.HasSetting(key)
ROWS = [
    (9501, "Darkness of the room", "string", "nocturne.darkness",
     [("", "Velvet"), ("dusk", "Dusk"), ("deep", "Deep")],
     "How dark the wall is",
     "Velvet is the mockup's night. Dusk lets more of the unlit wall show (kinder to TVs that crush dark greys). Deep is the museum with every light off.",
     False),
    (9502, "Dust in the beam", "bool", "nocturne.dust", None,
     "Dust in the beam", "Slow motes drift through the torchlight. Off (the default) keeps the light still and the Shield quicker: the drifting dust makes Kodi redraw every frame.", False),
    (9503, "Wandering torch", "boolinv", "nocturne.noambient", None,
     "The wandering torch",
     "Rest on Home for twenty seconds and the torch drifts across the wall on its own, lingering on films you have not seen. Any key brings it back.",
     False),
    (9504, "Light takes the picture's colour", "bool", "nocturne.halocolour", None,
     "Coloured spill",
     "An outer halo picks up the lit picture's own colour through TMDb Helper. Off (the default, quicker) keeps the plain warm 2700 K pool.",
     False),
    (9505, "Brass pins on watched films", "boolinv", "nocturne.nopins", None,
     "Watched pins", "A small brass pin in the corner of a frame marks what you have already seen.", False),
    (9506, "Trailer on the brass rail", "boolinv", "nocturne.hidetrailer", None,
     "Trailer", "Show TRAILER on the info page's rail when a film has one (plays through YouTube).", False),
    (9507, "Playback controls hide after", "string", "nocturne.osdhide",
     [("", "5 seconds"), ("10", "10 seconds"), ("off", "Never"), ("3", "3 seconds")],
     "Playback controls",
     "The brass rail over a playing film fades away after this long without a key press (never while paused).",
     False),
    (9508, "Reduce motion", "bool", "nocturne.reducemotion", None,
     "Reduce motion",
     "The torch jumps instead of gliding, the dust and the wandering torch rest, and windows only fade. The skin reloads when you change it.",
     True),
]
RESET_ID = 9509
# 0.9.9 main menu (HideMenu.*): a compact panel under the curator's note, after Restore in the Up / Down chain
MENU = [(9511, "$LOCALIZE[31200]", "HideMenu.Movies"), (9512, "$LOCALIZE[31201]", "HideMenu.TVShows"),
        (9513, "$LOCALIZE[31202]", "HideMenu.Music"), (9514, "$LOCALIZE[137]", "HideMenu.Search")]
MENU_TOP = 812  # 0.9.9: was 712; the custom rows panel sits above it
# 0.9.9 custom rows (Includes_CustomRows.xml): a compact panel between the curator's note and the main menu,
# after Restore in the Up / Down chain; OK opens the row's options
CUSTOM = [(9515, "$LOCALIZE[31941]", 1), (9516, "$LOCALIZE[31942]", 2), (9517, "$LOCALIZE[31943]", 3)]
CUSTOM_TOP = 564
# 0.9.14 custom menu items (Includes_CustomMenu.xml): no room left on the page, so they are a second tab of the custom
# rows panel ("CUSTOM ROWS · CUSTOM MENU ITEMS"): Right on a row goes to the menu item beside it, Left comes back.
# The tab on show follows Window(Home).Property(nocturne.cmtab) (set by the menu items' onfocus, cleared by the rows').
CMENU = [(9518, "$LOCALIZE[31981]", 1), (9519, "$LOCALIZE[31982]", 2), (9520, "$LOCALIZE[31983]", 3)]
CMTAB = "String.IsEqual(Window(Home).Property(nocturne.cmtab),1)"
PANEL_FOCUS = " | ".join(f"Control.HasFocus({r[0]})" for r in CUSTOM + CMENU)


def onup_xml(up):
    """the first main-menu row goes up into the custom panel's tab on show"""
    if up is not None:
        return f"\t\t\t\t<onup>{up}</onup>"
    return (f"\t\t\t\t<onup condition=\"!{CMTAB}\">{CUSTOM[-1][0]}</onup>\n"
            f"\t\t\t\t<onup condition=\"{CMTAB}\">{CMENU[-1][0]}</onup>")


def menu_xml():
    o = [f"""		<!-- main menu panel -->
		<control type="group">
			<left>1240</left>
			<top>{MENU_TOP - 44}</top>
			<control type="label">
				<left>0</left>
				<top>0</top>
				<width>590</width>
				<height>32</height>
				<aligny>center</aligny>
				<font>caps_20</font>
				<textcolor>8cc8b8a0</textcolor>
				<label>$LOCALIZE[31740]</label>
			</control>
		</control>"""]
    for k, (rid, label, key) in enumerate(MENU):
        up = MENU[k - 1][0] if k else None
        down = MENU[k + 1][0] if k + 1 < len(MENU) else ROWS[0][0]
        o.append(f"""		<control type="group">
			<left>1240</left>
			<top>{MENU_TOP + k * 64}</top>
			<control type="image">
				<left>-40</left>
				<top>0</top>
				<width>670</width>
				<height>56</height>
				<texture border="64,0,64,0" colordiffuse="light">noc/glow_bar.png</texture>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>12</top>
				<width>3</width>
				<height>32</height>
				<texture>noc/tick.png</texture>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="button" id="{rid}">
				<left>0</left>
				<top>0</top>
				<width>590</width>
				<height>56</height>
				<font>sans_26</font>
				<textoffsetx>28</textoffsetx>
				<aligny>center</aligny>
				<textcolor>b8e2d0b4</textcolor>
				<focusedcolor>text_lit</focusedcolor>
				<texturefocus />
				<texturenofocus />
				<label>{label}</label>
{onup_xml(up)}
				<ondown>{down}</ondown>
				<onright>Skin.ToggleSetting({key})</onright>
				<onclick>Skin.ToggleSetting({key})</onclick>
				<onleft>Skin.ToggleSetting({key})</onleft>
			</control>
			<control type="label">
				<left>250</left>
				<top>0</top>
				<width>320</width>
				<height>56</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>caps_22</font>
				<textcolor>8cc8b8a0</textcolor>
				<label>$VAR[SkinSet_Value_{rid}]</label>
				<visible>!Control.HasFocus({rid})</visible>
			</control>
			<control type="label">
				<left>250</left>
				<top>0</top>
				<width>320</width>
				<height>56</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>caps_22</font>
				<textcolor>fff4e6cf</textcolor>
				<label>◀   $VAR[SkinSet_Value_{rid}]   ▶</label>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>59</top>
				<width>590</width>
				<height>1</height>
				<texture colordiffuse="1adcbe8c">common/white.png</texture>
			</control>
		</control>""")
    return "\n".join(o)


def tab_label(text, on, dim_when):
    """one header word: lit (the tab on show) or dim"""
    out = []
    for lit in (True, False):
        vis = f"!{dim_when}" if lit else dim_when
        out.append(f"""				<control type="label">
					<width>auto</width>
					<height>32</height>
					<aligny>center</aligny>
					<font>caps_20</font>
					<textcolor>{'8cc8b8a0' if lit else '40c8b8a0'}</textcolor>
					<label>{text}</label>
					<visible>{vis}</visible>
				</control>""")
    return "\n".join(out)


def custom_xml():
    """the custom panel: tab 1 = custom rows (9515-9517), tab 2 = custom menu items (9518-9520)"""
    o = [f"""		<!-- custom rows / custom menu items panel (two tabs; Right / Left on a row switches) -->
		<control type="grouplist">
			<left>1240</left>
			<top>{CUSTOM_TOP - 44}</top>
			<width>590</width>
			<height>32</height>
			<orientation>horizontal</orientation>
			<itemgap>0</itemgap>
{tab_label("$LOCALIZE[31940]", True, CMTAB)}
				<control type="label">
					<width>auto</width>
					<height>32</height>
					<aligny>center</aligny>
					<font>caps_20</font>
					<textcolor>40c8b8a0</textcolor>
					<label>   ·   </label>
				</control>
{tab_label("$LOCALIZE[31980]", True, "!" + CMTAB)}
				<control type="label">
					<width>auto</width>
					<height>32</height>
					<aligny>center</aligny>
					<font>caps_20</font>
					<textcolor>8cc8b8a0</textcolor>
					<label>   ◀ ▶</label>
					<visible>{PANEL_FOCUS}</visible>
				</control>
		</control>"""]
    for tab, items in ((0, CUSTOM), (1, CMENU)):
        for k, (rid, label, n) in enumerate(items):
            up = items[k - 1][0] if k else RESET_ID
            down = items[k + 1][0] if k + 1 < len(items) else MENU[0][0]
            shown = f"!{CMTAB}" if tab == 0 else CMTAB
            if tab == 0:
                side = f"<onleft>noop</onleft>\n\t\t\t\t<onright>{CMENU[k][0]}</onright>"
                focus = "<onfocus>ClearProperty(nocturne.cmtab,home)</onfocus>"
                click = f'<include content="CustomRows_SettingsClick"><param name="row" value="{n}"/><param name="heading" value="{label}"/></include>'
                value = f"$VAR[CustomRow_Value{n}]"
            else:
                side = f"<onleft>{CUSTOM[k][0]}</onleft>\n\t\t\t\t<onright>noop</onright>"
                focus = "<onfocus>SetProperty(nocturne.cmtab,1,home)</onfocus>"
                click = f'<include content="CustomMenu_SettingsClick"><param name="item" value="{n}"/><param name="heading" value="{label}"/></include>'
                value = f"$VAR[CustomMenu_Value{n}]"
            o.append(f"""		<control type="group">
			<left>1240</left>
			<top>{CUSTOM_TOP + k * 64}</top>
			<control type="image">
				<left>-40</left>
				<top>0</top>
				<width>670</width>
				<height>56</height>
				<texture border="64,0,64,0" colordiffuse="light">noc/glow_bar.png</texture>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>12</top>
				<width>3</width>
				<height>32</height>
				<texture>noc/tick.png</texture>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="button" id="{rid}">
				<left>0</left>
				<top>0</top>
				<width>590</width>
				<height>56</height>
				<font>sans_26</font>
				<textoffsetx>28</textoffsetx>
				<textcolor>b8e2d0b4</textcolor>
				<focusedcolor>text_lit</focusedcolor>
				<texturefocus />
				<label>{label}</label>
				<visible allowhiddenfocus="true">{shown}</visible>
				<onup>{up}</onup>
				<ondown>{down}</ondown>
				{side}
				{focus}
				{click}
			</control>
			<control type="label">
				<left>200</left>
				<top>0</top>
				<width>370</width>
				<height>56</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>caps_22</font>
				<textcolor>8cc8b8a0</textcolor>
				<label>{value}</label>
				<visible>{shown} + !Control.HasFocus({rid})</visible>
			</control>
			<control type="label">
				<left>200</left>
				<top>0</top>
				<width>370</width>
				<height>56</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>caps_22</font>
				<textcolor>fff4e6cf</textcolor>
				<label>{value}</label>
				<visible>{shown} + Control.HasFocus({rid})</visible>
			</control>{RULE if tab == 0 else ""}
		</control>""")
    # (no tab visibility on the row groups: a button inside a hidden group can't take focus, even with
    #  allowhiddenfocus; the hairline is drawn once, by the custom rows tab, for both tabs)
    return "\n".join(o)


RULE = """
			<control type="image">
				<left>0</left>
				<top>59</top>
				<width>590</width>
				<height>1</height>
				<texture colordiffuse="1adcbe8c">common/white.png</texture>
			</control>"""


def esc(s):
    return s.replace("&", "&amp;").replace("'", "&apos;")


def value_label(row):
    rid, label, kind, key, values, *_ = row
    o = []
    if kind == "string":
        for stored, lab in values[1:]:
            o.append(f'\t\t<value condition="String.IsEqual(Skin.String({key}),{stored})">{lab}</value>')
        o.append(f"\t\t<value>{values[0][1]}</value>")
    elif kind == "bool":
        o.append(f'\t\t<value condition="Skin.HasSetting({key})">On</value>')
        o.append("\t\t<value>Off</value>")
    else:
        o.append(f'\t\t<value condition="Skin.HasSetting({key})">Off</value>')
        o.append("\t\t<value>On</value>")
    return f'\t<variable name="SkinSet_Value_{rid}">\n' + "\n".join(o) + "\n\t</variable>"


def actions(row):
    rid, label, kind, key, values, _t, _h, reload = row
    o = []
    pre = []
    if reload:
        pre = [f"SetProperty(nocturne.refocus,{rid},home)"]
    if kind == "string":
        n = len(values)
        for i, (stored, _l) in enumerate(values):
            cond = f"String.IsEqual(Skin.String({key}),{stored})" if stored else \
                "[" + " + ".join(f"!String.IsEqual(Skin.String({key}),{s})" for s, _ in values if s) + "]"
            nxt = values[(i + 1) % n][0]
            prv = values[(i - 1) % n][0]
            set_n = f"Skin.SetString({key},{nxt})" if nxt else f"Skin.Reset({key})"
            set_p = f"Skin.SetString({key},{prv})" if prv else f"Skin.Reset({key})"
            for tag, act in (("onright", set_n), ("onclick", set_n), ("onleft", set_p)):
                o.append(f'\t\t\t\t<{tag} condition="{cond}">{act}</{tag}>')
    else:
        for tag in ("onright", "onclick", "onleft"):
            for a in pre:
                o.append(f"\t\t\t\t<{tag}>{a}</{tag}>")
            o.append(f"\t\t\t\t<{tag}>Skin.ToggleSetting({key})</{tag}>")
            if reload:
                o.append(f"\t\t\t\t<{tag}>ReloadSkin()</{tag}>")
    return "\n".join(o)


def row_xml(i, row):
    rid, label, kind, key, values, *_ = row
    top = 196 + i * 84
    up = ROWS[i - 1][0] if i else MENU[-1][0]
    down = ROWS[i + 1][0] if i + 1 < len(ROWS) else RESET_ID
    return f"""		<!-- {label} -->
		<control type="group">
			<left>96</left>
			<top>{top}</top>
			<control type="image">
				<left>-40</left>
				<top>0</top>
				<width>1080</width>
				<height>76</height>
				<texture border="64,0,64,0" colordiffuse="light">noc/glow_bar.png</texture>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>22</top>
				<width>3</width>
				<height>32</height>
				<texture>noc/tick.png</texture>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="button" id="{rid}">
				<left>0</left>
				<top>0</top>
				<width>1000</width>
				<height>76</height>
				<font>sans_26</font>
				<textoffsetx>28</textoffsetx>
				<aligny>center</aligny>
				<textcolor>b8e2d0b4</textcolor>
				<focusedcolor>text_lit</focusedcolor>
				<texturefocus />
				<texturenofocus />
				<label>{esc(label)}</label>
				<onup>{up}</onup>
				<ondown>{down}</ondown>
{actions(row)}
			</control>
			<control type="label">
				<left>560</left>
				<top>0</top>
				<width>420</width>
				<height>76</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>caps_22</font>
				<textcolor>8cc8b8a0</textcolor>
				<label>$VAR[SkinSet_Value_{rid}]</label>
				<visible>!Control.HasFocus({rid})</visible>
			</control>
			<control type="label">
				<left>560</left>
				<top>0</top>
				<width>420</width>
				<height>76</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>caps_22</font>
				<textcolor>fff4e6cf</textcolor>
				<label>◀   $VAR[SkinSet_Value_{rid}]   ▶</label>
				<visible>Control.HasFocus({rid})</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>79</top>
				<width>1000</width>
				<height>1</height>
				<texture colordiffuse="1adcbe8c">common/white.png</texture>
			</control>
		</control>"""


def main():
    resets = "\n".join(f"\t\t\t\t<onclick condition=\"!String.IsEmpty(Window(Home).Property(nocturne.resetarmed))\">Skin.Reset({k})</onclick>"
                       for k in [r[3] for r in ROWS] + [m[2] for m in MENU])
    help_title = "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">{esc(r[5])}</value>' for r in ROWS)
    help_text = "\n".join(f'\t\t<value condition="Control.HasFocus({r[0]})">{esc(r[6])}</value>' for r in ROWS)
    top_reset = 196 + len(ROWS) * 84 + 24
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_skinsettings.py - edit the table there, then re-run. -->
<window>
	<defaultcontrol always="true">{ROWS[0][0]}</defaultcontrol>
	<backgroundcolor>bg</backgroundcolor>
	<onload>ClearProperty(nocturne.resetarmed,home)</onload>
	<onload>ClearProperty(nocturne.cmtab,home)</onload>
	<onload condition="!String.IsEmpty(Window(Home).Property(nocturne.refocus))">SetFocus($INFO[Window(Home).Property(nocturne.refocus)])</onload>
	<onload>ClearProperty(nocturne.refocus,home)</onload>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>Noc_Background</include>
		<include content="Noc_TopBar">
			<param name="title" value="$LOCALIZE[31021]"/>
			<param name="sub" value="·   Nocturne $INFO[System.AddonVersion(skin.nocturne)]"/>
		</include>
{chr(10).join(row_xml(i, r) for i, r in enumerate(ROWS))}
		<!-- restore: OK arms, OK again resets every Nocturne setting -->
		<control type="group">
			<left>96</left>
			<top>{top_reset}</top>
			<control type="button" id="{RESET_ID}">
				<left>0</left>
				<top>0</top>
				<width>420</width>
				<height>64</height>
				<font>btn_22</font>
				<align>center</align>
				<aligny>center</aligny>
				<textcolor>brass_word</textcolor>
				<focusedcolor>ink</focusedcolor>
				<texturenofocus border="26,0,26,0">noc/plaque_dim.png</texturenofocus>
				<texturefocus border="26,0,26,0">noc/plaque.png</texturefocus>
				<label>$VAR[SkinSet_ResetLabel]</label>
				<onup>{ROWS[-1][0]}</onup>
				<ondown condition="!{CMTAB}">{CUSTOM[0][0]}</ondown>
				<ondown condition="{CMTAB}">{CMENU[0][0]}</ondown>
				<onunfocus>ClearProperty(nocturne.resetarmed,home)</onunfocus>
{resets}
				<onclick condition="!String.IsEmpty(Window(Home).Property(nocturne.resetarmed))">ClearProperty(nocturne.resetarmed,home)</onclick>
				<onclick condition="String.IsEmpty(Window(Home).Property(nocturne.resetarmed))">SetProperty(nocturne.resetarmed,1,home)</onclick>
			</control>
		</control>
{custom_xml()}
{menu_xml()}
		<include>CustomRows_FavData</include>
		<!-- the curator's note for the focused setting -->
		<control type="group">
			<left>1240</left>
			<top>196</top>
			<control type="image">
				<left>-120</left>
				<top>-120</top>
				<width>800</width>
				<height>600</height>
				<texture colordiffuse="light">noc/glow_warm.png</texture>
			</control>
			<control type="label">
				<left>0</left>
				<top>0</top>
				<width>590</width>
				<height>32</height>
				<aligny>center</aligny>
				<font>caps_20</font>
				<textcolor>8cc8b8a0</textcolor>
				<label>$LOCALIZE[31291]</label>
			</control>
			<control type="label">
				<left>-4</left>
				<top>40</top>
				<width>600</width>
				<height>64</height>
				<font>title_48</font>
				<textcolor>text_lit</textcolor>
				<label>$VAR[SkinSet_HelpTitle]</label>
			</control>
			<control type="image">
				<left>0</left>
				<top>120</top>
				<width>56</width>
				<height>2</height>
				<texture colordiffuse="ccb8924f">common/white.png</texture>
			</control>
			<control type="textbox">
				<left>0</left>
				<top>146</top>
				<width>590</width>
				<height>164</height>  <!-- 0.9.9: four lines (the longest note), the custom rows panel starts below -->
				<font>body_26</font>
				<textcolor>dbeadcc6</textcolor>
				<label>$VAR[SkinSet_HelpText]</label>
			</control>
		</control>
	</controls>
</window>
"""
    vars_xml = "\n".join(value_label(r) for r in ROWS)
    vars_xml += "\n" + "\n".join(f'\t<variable name="SkinSet_Value_{rid}">\n\t\t<value condition="Skin.HasSetting({key})">$LOCALIZE[31742]</value>\n\t\t<value>$LOCALIZE[31741]</value>\n\t</variable>' for rid, _l, key in MENU)
    help_title += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({rid})">{label}</value>' for rid, label, _k in MENU)
    help_text += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({rid})">$LOCALIZE[31743]</value>' for rid, _l, _k in MENU)
    help_title += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({rid})">{label}</value>' for rid, label, _n in CUSTOM)
    help_text += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({rid})">$LOCALIZE[31957]</value>' for rid, _l, _n in CUSTOM)
    help_title += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({rid})">{label}</value>' for rid, label, _n in CMENU)
    help_text += "\n" + "\n".join(f'\t\t<value condition="Control.HasFocus({rid})">$LOCALIZE[31994]</value>' for rid, _l, _n in CMENU)
    vars_xml += f"""
	<variable name="SkinSet_HelpTitle">
{help_title}
		<value condition="Control.HasFocus({RESET_ID})">Restore defaults</value>
	</variable>
	<variable name="SkinSet_HelpText">
{help_text}
		<value condition="Control.HasFocus({RESET_ID})">Every Nocturne setting goes back to how it was built: velvet darkness, no dust, the wandering torch, no coloured spill, pins, trailers, controls hiding after five seconds, full motion.</value>
	</variable>
	<variable name="SkinSet_ResetLabel">
		<value condition="!String.IsEmpty(Window(Home).Property(nocturne.resetarmed))">Press OK again</value>
		<value>Restore defaults</value>
	</variable>"""
    OUT.write_text(localize_xml(strip_defaults(xml, DEFAULTS_XML), STRINGS_PO), encoding="utf-8", newline="\n")
    inc = OUT.parent / "Includes_SkinSettings.xml"
    inc.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by _src/make_skinsettings.py -->\n<includes>\n'
                   + vars_xml + "\n</includes>\n", encoding="utf-8", newline="\n")
    print("wrote", OUT.name, inc.name)


if __name__ == "__main__":
    main()
