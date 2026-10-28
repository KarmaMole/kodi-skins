"""Generate 1080i/Includes_Home.xml: Groove's Home at M1 (icon rail + glow stage).   python skins/skin.groove/_src/make_home.py

SPEC section 5 / DESIGN section 4 / board 01-02. M1 scope: the rail (Music, Films, TV, Search, Settings), each section's
hero on the stage with its glow, the clock. M2 adds the Down row (Spin something / films / next up / settings tiles),
M3 the mini player (Up from the rail).

Rail ids 9001-9005 inside group 9000 (menucontrol). Left/Right walk the rail, no wrap past Music / Settings.
1.0.7 custom menu items (Includes_CustomMenu.xml): rail icons 9006-9008 after TV, before Search / Settings, hidden while
not set; each has a quiet stage (custom_menu_stage). With all eight icons on show the clock on the rail steps aside.
Each button's onfocus stores the section in Window(Home).Property(groove.home) (the stage follows it; Home reopens on
it) and points TMDb Helper's colour service at that section's data list (TMDbHelper.WidgetContainer).
Data list 9102 (last played album) sits under the opaque room: drawn (so its art loads), never seen.
M2 (music lane, _src/home_rows.py): 9101 / 9111 / 9121 / 9122 are now the visible Down rows themselves (random albums,
films in progress or unwatched, embuary next-up or shows in progress, new episodes), so the heroes follow the focused
row item. Settings OK = Down (the settings row 9050 replaces the forked system menu here).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import home_rows as HR  # noqa: E402  (M2 rows, music lane)

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Home.xml"

FILMS_XSP = ("videodb://movies/titles/?xsp=%7B%22rules%22%3A%7B%22or%22%3A%5B%7B%22field%22%3A%22inprogress%22%2C"
             "%22operator%22%3A%22true%22%2C%22value%22%3A%5B%22%22%5D%7D%2C%7B%22field%22%3A%22playcount%22%2C"
             "%22operator%22%3A%22is%22%2C%22value%22%3A%5B%220%22%5D%7D%5D%7D%2C%22type%22%3A%22movies%22%7D")

# id, key, icon, label string, onclick, TMDb widget container
RAIL = [
    (9001, "music", "music", 31400, "ActivateWindow(Music,musicdb://albums/,return)", None),
    (9002, "films", "films", 31401, "ActivateWindow(Videos,videodb://movies/titles/,return)", "9111"),
    (9003, "tv", "tv", 31402, "ActivateWindow(Videos,videodb://tvshows/titles/,return)", None),
    (9004, "search", "search", 31403, "ActivateWindow(1150)", None),
    (9005, "settings", "settings", 31404, "SetFocus(9050)", None),
]
X0, PITCH, Y = 96, 232, 920
# 1.0.2 main menu: rail icons hidden in Skin settings (HideMenu.*); the icons after a hidden one slide left by PITCH.
# Settings never hides. A hidden icon keeps its numeric onleft / onright, so Left / Right fall through it.
HIDE = {"music": "Skin.HasSetting(HideMenu.Music)", "films": "Skin.HasSetting(HideMenu.Movies)",
        "tv": "Skin.HasSetting(HideMenu.TVShows)", "search": "Skin.HasSetting(HideMenu.Search)"}

# 1.0.7 custom menu items: (slot, rail id). They sit after TV (RAIL index 2), before Search; the rail order below drives
# Left / Right (numeric, so a hidden icon is walked past). Search / Settings slide right one PITCH per item shown.
CUSTOM_MENU = [(1, 9006), (2, 9007), (3, 9008)]
RAIL_ORDER = [9001, 9002, 9003, 9006, 9007, 9008, 9004, 9005]


def cm_on(n):
    return f"$EXP[CustomMenu{n}On]"


def rail_lr(cid):
    i = RAIL_ORDER.index(cid)
    left = f"\n\t\t\t\t<onleft>{RAIL_ORDER[i - 1]}</onleft>" if i else ""
    right = f"\n\t\t\t\t<onright>{RAIL_ORDER[i + 1]}</onright>" if i + 1 < len(RAIL_ORDER) else ""
    return left, right


DATA = [  # id, content (target, attrs, path), art key drawn
    (9102, 'target="music" limit="1" browse="never"', "musicdb://recentlyplayedalbums/", "thumb"),
]


def sect(key):
    if key == "music":
        c = ("[String.IsEmpty(Window(Home).Property(groove.home)) | "
             "String.IsEqual(Window(Home).Property(groove.home),music)]")
    else:
        c = f"String.IsEqual(Window(Home).Property(groove.home),{key})"
    c += " + !$EXP[CustomRowsFocus]"  # 1.0.2: a custom row has its own stage (custom_stage)
    return f"{c} + !{HIDE[key]}" if key in HIDE else c


def data_lists():
    o = []
    for lid, attrs, path, art in DATA:
        img = (f'<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height>'
               f'<texture background="true">$INFO[ListItem.Art({art})]</texture></control>')
        o.append(f"""		<control type="list" id="{lid}">
			<left>0</left>
			<top>0</top>
			<width>5</width>
			<height>1</height>
			<orientation>horizontal</orientation>
			<scrolltime>0</scrolltime>
			<itemlayout width="1" height="1">{img}</itemlayout>
			<focusedlayout width="1" height="1">{img}</focusedlayout>
			<content {attrs}>{path.replace('&', '&amp;')}</content>
		</control>""")
    return "\n".join(o)


def rail():
    o = []
    for i, (cid, key, icon, sid, click, widget) in enumerate(RAIL):
        x = X0 + i * PITCH
        left, right = rail_lr(cid)
        wc = []
        if key == "music":
            wc = ['<onfocus condition="Integer.IsGreater(Container(9102).NumItems,0)">SetProperty(TMDbHelper.WidgetContainer,9102,home)</onfocus>',
                  '<onfocus condition="!Integer.IsGreater(Container(9102).NumItems,0)">SetProperty(TMDbHelper.WidgetContainer,9101,home)</onfocus>']
        elif key == "tv":
            wc = ['<onfocus condition="Integer.IsGreater(Container(9121).NumItems,0)">SetProperty(TMDbHelper.WidgetContainer,9121,home)</onfocus>',
                  '<onfocus condition="!Integer.IsGreater(Container(9121).NumItems,0)">SetProperty(TMDbHelper.WidgetContainer,9122,home)</onfocus>']
        elif widget:
            wc = [f"<onfocus>SetProperty(TMDbHelper.WidgetContainer,{widget},home)</onfocus>"]
        else:
            wc = ["<onfocus>ClearProperty(TMDbHelper.WidgetContainer,home)</onfocus>"]
        # script.karmamole.helper follows ListItem.* by default; a rail button has none, so point it at the same data
        # list as TMDb Helper (HELPER_API 1, Groove.Helper.Container). Rows / tiles clear it again (home_rows.py) so
        # an info dialog opened from a row follows its own ListItem; Home.xml clears it on unload.
        wc += [w.replace("TMDbHelper.WidgetContainer", "Groove.Helper.Container") for w in wc]
        wcs = "".join("\n\t\t\t\t" + w for w in wc)
        hide = (f"\n\t\t\t<visible>!{HIDE[key]}</visible>" if key in HIDE else "") + "".join(
            f'\n\t\t\t<animation effect="slide" start="0,0" end="-{PITCH},0" time="0" condition="{HIDE[p[1]]}">Conditional</animation>'
            for p in RAIL[:i] if p[1] in HIDE)
        if key in ("search", "settings"):   # 1.0.7: the custom menu items sit before Search
            hide += "".join(f'\n\t\t\t<animation effect="slide" start="0,0" end="{PITCH},0" time="0" condition="{cm_on(n)}">Conditional</animation>'
                            for n, _c in CUSTOM_MENU)
        if key == "search":
            o.append(custom_rail())
        o.append(f"""			<!-- {key} -->
			<control type="group">{hide}
			<control type="image">
				<left>{x - 45}</left>
				<top>{Y - 45}</top>
				<width>g_icon_glow</width>
				<height>g_icon_glow</height>
				<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
				<visible>Control.HasFocus({cid})</visible>
				<include>Anim_LabelReveal</include>
			</control>
			<control type="button" id="{cid}">
				<left>{x - 8}</left>
				<top>{Y - 8}</top>
				<width>{PITCH - 16}</width>
				<height>80</height>
				<texturefocus />
				<texturenofocus />
				<label />
				<onfocus>SetProperty(groove.home,{key},home)</onfocus>
				<onfocus>SetProperty(groove.railid,{cid},home)</onfocus>{wcs}
				<onclick>{click}</onclick>{left}{right}{HR.rail_nav(key)}
			</control>
			<control type="image">
				<left>{x}</left>
				<top>{Y}</top>
				<width>g_rail_icon</width>
				<height>g_rail_icon</height>
				<texture colordiffuse="$VAR[icon_rest]">icons/{icon}.png</texture>
				<visible>!Control.HasFocus({cid})</visible>
			</control>
			<control type="image">
				<left>{x}</left>
				<top>{Y}</top>
				<width>g_rail_icon</width>
				<height>g_rail_icon</height>
				<texture colordiffuse="$VAR[ink]">icons/{icon}.png</texture>
				<visible>Control.HasFocus({cid})</visible>
			</control>
			<control type="label">
				<left>{x + 80}</left>
				<top>{Y}</top>
				<width>g_rail_label_w</width>
				<height>g_rail_icon</height>
				<aligny>center</aligny>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$LOCALIZE[{sid}]</label>
				<visible>Control.HasFocus({cid})</visible>
				<include>Anim_LabelReveal</include>
			</control>
			</control>""")
    return "\n".join(o)


def custom_rail():
    """1.0.7 custom menu items on the rail: the add-on's own icon (full colour, 72 % at rest like a dimmed icon), else a
    rail glyph (add-on / folder / favourite) tinted like the others; the focused one glows and shows its name."""
    o = []
    for k, (n, cid) in enumerate(CUSTOM_MENU):
        x = X0 + (3 + k) * PITCH
        left, right = rail_lr(cid)
        slides = "".join(f'\n\t\t\t<animation effect="slide" start="0,0" end="-{PITCH},0" time="0" condition="{HIDE[p[1]]}">Conditional</animation>'
                         for p in RAIL[:3] if p[1] in HIDE)
        slides += "".join(f'\n\t\t\t<animation effect="slide" start="0,0" end="-{PITCH},0" time="0" condition="!{cm_on(m)}">Conditional</animation>'
                          for m, _c in CUSTOM_MENU[:k])
        o.append(f"""			<!-- custom menu item {n} -->
			<control type="group">
			<visible>{cm_on(n)}</visible>{slides}
			<control type="image">
				<left>{x - 45}</left>
				<top>{Y - 45}</top>
				<width>g_icon_glow</width>
				<height>g_icon_glow</height>
				<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
				<visible>Control.HasFocus({cid})</visible>
				<include>Anim_LabelReveal</include>
			</control>
			<control type="button" id="{cid}">
				<left>{x - 8}</left>
				<top>{Y - 8}</top>
				<width>{PITCH - 16}</width>
				<height>80</height>
				<texturefocus />
				<texturenofocus />
				<label />
				<onfocus>SetProperty(groove.home,custom{n},home)</onfocus>
				<onfocus>SetProperty(groove.railid,{cid},home)</onfocus>
				<onfocus>ClearProperty(TMDbHelper.WidgetContainer,home)</onfocus>
				<onfocus>ClearProperty(Groove.Helper.Container,home)</onfocus>
				<include content="CustomMenu_OnClick"><param name="item" value="{n}"/></include>{left}{right}
				{HR.MINI_UP}
				{HR.DOWN_CUSTOM}
			</control>
			<control type="image">
				<left>{x}</left>
				<top>{Y}</top>
				<width>g_rail_icon</width>
				<height>g_rail_icon</height>
				<aspectratio>keep</aspectratio>
				<texture background="true" colordiffuse="b8ffffff">$VAR[CustomMenu_Icon{n}]</texture>
				<visible>$EXP[CustomMenu{n}HasIcon] + !Control.HasFocus({cid})</visible>
			</control>
			<control type="image">
				<left>{x}</left>
				<top>{Y}</top>
				<width>g_rail_icon</width>
				<height>g_rail_icon</height>
				<aspectratio>keep</aspectratio>
				<texture background="true">$VAR[CustomMenu_Icon{n}]</texture>
				<visible>$EXP[CustomMenu{n}HasIcon] + Control.HasFocus({cid})</visible>
			</control>
			<control type="image">
				<left>{x}</left>
				<top>{Y}</top>
				<width>g_rail_icon</width>
				<height>g_rail_icon</height>
				<texture colordiffuse="$VAR[icon_rest]">icons/$VAR[Home_CustomGlyph{n}].png</texture>
				<visible>!$EXP[CustomMenu{n}HasIcon] + !Control.HasFocus({cid})</visible>
			</control>
			<control type="image">
				<left>{x}</left>
				<top>{Y}</top>
				<width>g_rail_icon</width>
				<height>g_rail_icon</height>
				<texture colordiffuse="$VAR[ink]">icons/$VAR[Home_CustomGlyph{n}].png</texture>
				<visible>!$EXP[CustomMenu{n}HasIcon] + Control.HasFocus({cid})</visible>
			</control>
			<control type="label">
				<left>{x + 80}</left>
				<top>{Y}</top>
				<width>g_rail_label_w</width>
				<height>g_rail_icon</height>
				<aligny>center</aligny>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[CustomMenu_Label{n}]</label>
				<visible>Control.HasFocus({cid})</visible>
				<include>Anim_LabelReveal</include>
			</control>
			</control>""")
    return "\n".join(o)


def custom_glyphs():
    """the rail / stage glyph of an item without its own icon: addons, files (library, playlist, folder) or favourites"""
    o = []
    for n, _c in CUSTOM_MENU:
        s = lambda k: f"Skin.String(CustomMenu.{n}.{k})"
        o.append(f"""	<variable name="Home_CustomGlyph{n}">
		<value condition="!String.IsEmpty({s('Addon')})">addons</value>
		<value condition="!String.IsEmpty({s('Target')}) | String.EndsWith({s('Path')},.xsp) | String.StartsWith({s('Path')},library://) | String.StartsWith({s('Path')},videodb://) | String.StartsWith({s('Path')},musicdb://)">files</value>
		<value>favourites</value>
	</variable>""")
    o.append('\t<!-- 1.0.7: all eight rail icons on show (three custom menu items, nothing hidden): the eighth reaches the clock -->')
    o.append('\t<expression name="Home_RailFull">' + " + ".join(cm_on(n) for n, _c in CUSTOM_MENU) + " + "
             + " + ".join(f"!{HIDE[k]}" for k in ("music", "films", "tv", "search")) + "</expression>")
    return "\n".join(o)


def custom_menu_stage(n):
    """1.0.7 a custom menu item's stage: the Search / Settings stage's shape (glow + centred icon + one line), with the
    add-on's icon (else the glyph), its name and "Opens <add-on>  ·  OK to open"."""
    vis = f"String.IsEqual(Window(Home).Property(groove.home),custom{n}) + {cm_on(n)} + !$EXP[CustomRowsFocus]"
    return f"""		<control type="group">
			<visible>{vis}</visible>
			<include>Anim_SectionSwap</include>
			<control type="image">
				<left>660</left>
				<top>130</top>
				<width>600</width>
				<height>600</height>
				<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
			</control>
			<control type="image">
				<left>880</left>
				<top>350</top>
				<width>160</width>
				<height>160</height>
				<aspectratio>keep</aspectratio>
				<fadetime>200</fadetime>
				<texture background="true">$VAR[CustomMenu_Icon{n}]</texture>
				<visible>$EXP[CustomMenu{n}HasIcon]</visible>
			</control>
			<control type="image">
				<left>912</left>
				<top>382</top>
				<width>96</width>
				<height>96</height>
				<texture colordiffuse="$VAR[ink]">icons/96/$VAR[Home_CustomGlyph{n}].png</texture>
				<visible>!$EXP[CustomMenu{n}HasIcon]</visible>
			</control>
			<control type="label">
				<left>360</left>
				<top>540</top>
				<width>1200</width>
				<height>48</height>
				<align>center</align>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[CustomMenu_Label{n}]</label>
			</control>
			<control type="label">
				<left>360</left>
				<top>596</top>
				<width>1200</width>
				<height>40</height>
				<align>center</align>
				<font>font_small</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$VAR[CustomMenu_Opens{n}]  ·  $LOCALIZE[31995]</label>
			</control>
		</control>"""


# LESSONS: String.IsEmpty($VAR[...]) is invalid - test the real infolabels
RUNTIME_VIS = {"films": "!String.IsEmpty(Container(9111).ListItem.Duration)", "tv": "false"}
RATING_VIS = {"films": "!String.IsEmpty(Container(9111).ListItem.Rating)",
              "tv": "Integer.IsGreater(Container(9121).NumItems,0) + !String.IsEmpty(Container(9121).ListItem.Rating)"}


def video_stage(key, a, b):
    """Cinema glow hero for films / TV: fanart at 66 % over the room, the room laid back over it through two ramps,
    clearlogo (fallback title) + runtime / rating / 4K line, top left (board 02)."""
    item = f"Home_{key}_"
    return f"""		<control type="group">
			<visible>{sect(key)}</visible>
			<include>Anim_SectionSwap</include>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<aspectratio>scale</aspectratio>
				<fadetime>300</fadetime>
				<texture background="true">$VAR[{item}Fanart]</texture>
				<animation effect="fade" start="100" end="66" time="0" condition="true">Conditional</animation>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<texture colordiffuse="$VAR[ground]">groove/white.png</texture>
				<animation effect="fade" start="100" end="28" time="0" condition="true">Conditional</animation>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1240</width>
				<height>1080</height>
				<texture colordiffuse="$VAR[ground]">groove/ramp_h.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>560</top>
				<width>1920</width>
				<height>520</height>
				<texture colordiffuse="$VAR[ground]" flipy="true">groove/ramp_v.png</texture>
			</control>
			<control type="image">
				<left>g_safe_x</left>
				<top>140</top>
				<width>600</width>
				<height>200</height>
				<aspectratio aligny="bottom" align="left">keep</aspectratio>
				<texture background="true" colordiffuse="$VAR[logo_tint]">$VAR[{item}Logo]</texture>
			</control>
			<control type="textbox">
				<left>g_safe_x</left>
				<top>184</top>
				<width>900</width>
				<height>140</height>
				<font>font_title_xl</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[{item}Title]</label>
				<visible>String.IsEmpty($VAR_PLACEHOLDER)</visible>
			</control>
			<control type="grouplist">
				<left>g_safe_x</left>
				<top>368</top>
				<width>1000</width>
				<height>48</height>
				<orientation>horizontal</orientation>
				<itemgap>16</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<control type="image" id="{a}">
					<top>6</top>
					<width>36</width>
					<height>36</height>
					<texture colordiffuse="$VAR[ink]">icons/runtime.png</texture>
					<visible>{RUNTIME_VIS[key]}</visible>
				</control>
				<control type="label" id="{a + 1}">
					<width>auto</width>
					<height>48</height>
					<font>font_label</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$VAR[{item}Runtime]</label>
				</control>
				<control type="image" id="{a + 2}">
					<left>24</left>
					<top>6</top>
					<width>36</width>
					<height>36</height>
					<texture colordiffuse="$VAR[ink]">icons/rating.png</texture>
					<visible>{RATING_VIS[key]}</visible>
				</control>
				<control type="label" id="{a + 3}">
					<width>auto</width>
					<height>48</height>
					<font>font_label</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$VAR[{item}Rating]</label>
				</control>
				<control type="image" id="{a + 4}">
					<left>24</left>
					<top>8</top>
					<width>64</width>
					<height>32</height>
					<aspectratio>keep</aspectratio>
					<texture colordiffuse="$VAR[ink]">icons/badge-4k.png</texture>
					<visible>$EXP[{item}Is4K]</visible>
				</control>
			</control>
		</control>"""


def custom_stage():
    """1.0.2 custom rows: the focused item is the hero, cinema glow like films / TV; the row's name and size above"""
    ids = (9881, 9882, 9883)
    no_logo = " | ".join(f"[Control.HasFocus({c}) + String.IsEmpty(Container({c}).ListItem.Art(clearlogo))]" for c in ids)
    return f"""		<control type="group">
			<visible>$EXP[CustomRowsFocus]</visible>
			<include>Anim_SectionSwap</include>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<aspectratio>scale</aspectratio>
				<fadetime>300</fadetime>
				<texture background="true">$VAR[Home_custom_Fanart]</texture>
				<animation effect="fade" start="100" end="66" time="0" condition="true">Conditional</animation>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<texture colordiffuse="$VAR[ground]">groove/white.png</texture>
				<animation effect="fade" start="100" end="28" time="0" condition="true">Conditional</animation>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1240</width>
				<height>1080</height>
				<texture colordiffuse="$VAR[ground]">groove/ramp_h.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>560</top>
				<width>1920</width>
				<height>520</height>
				<texture colordiffuse="$VAR[ground]" flipy="true">groove/ramp_v.png</texture>
			</control>
			<control type="label">
				<left>g_safe_x</left>
				<top>84</top>
				<width>1200</width>
				<height>40</height>
				<font>font_small</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$VAR[Home_custom_Kicker]</label>
			</control>
			<control type="image">
				<left>g_safe_x</left>
				<top>140</top>
				<width>600</width>
				<height>200</height>
				<aspectratio aligny="bottom" align="left">keep</aspectratio>
				<texture background="true" colordiffuse="$VAR[logo_tint]">$VAR[Home_custom_Logo]</texture>
			</control>
			<control type="textbox">
				<left>g_safe_x</left>
				<top>184</top>
				<width>900</width>
				<height>140</height>
				<font>font_title_xl</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[Home_custom_Title]</label>
				<visible>{no_logo}</visible>
			</control>
		</control>"""


def icon_stage(key, icon, sid):
    return f"""		<control type="group">
			<visible>{sect(key)}</visible>
			<include>Anim_SectionSwap</include>
			<control type="image">
				<left>660</left>
				<top>130</top>
				<width>600</width>
				<height>600</height>
				<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
			</control>
			<control type="image">
				<left>912</left>
				<top>382</top>
				<width>96</width>
				<height>96</height>
				<texture colordiffuse="$VAR[ink]">icons/96/{icon}.png</texture>
			</control>
			<control type="label">
				<left>360</left>
				<top>520</top>
				<width>1200</width>
				<height>40</height>
				<align>center</align>
				<font>font_small</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$LOCALIZE[{sid}]</label>
				<include content="Anim_Dim"><param name="condition" value="$EXP[Home_RowOpen]"/><param name="to" value="0"/></include>
			</control>
		</control>"""


def variables():
    v = []

    def var(name, rows):
        v.append(f'\t<variable name="{name}">')
        for cond, val in rows:
            v.append(f'\t\t<value condition="{cond}">{val}</value>' if cond else f"\t\t<value>{val}</value>")
        v.append("\t</variable>")

    playing = "Player.HasAudio"
    recent = "Integer.IsGreater(Container(9102).NumItems,0)"
    def music(player, item):
        # producer decision (QA m5): while music plays the hero is the playing album, also with the row open;
        # otherwise the focused row item, then the last played album, then the row's first random album
        return [(playing, f"$INFO[{player}]"), ("Control.HasFocus(9101)", f"$INFO[Container(9101).{item}]"),
                (recent, f"$INFO[Container(9102).{item}]"), (None, f"$INFO[Container(9101).{item}]")]
    var("Home_Music_Cover", music("Player.Art(thumb)", "ListItem.Art(thumb)"))
    var("Home_Music_Disc", [("Control.HasFocus(9101)", ""),
                            (playing + " + !$EXP[RecordAlwaysVinyl]", "$INFO[Player.Art(album.discart)]"),
                            (playing, ""),
                            ("$EXP[RecordAlwaysVinyl]", ""),
                            (recent, "$INFO[Container(9102).ListItem.Art(discart)]"),
                            (None, "$INFO[Container(9101).ListItem.Art(discart)]")])
    var("Home_Music_Logo", music("Player.Art(artist.clearlogo)", "ListItem.Art(artist.clearlogo)"))
    var("Home_Music_Album", music("MusicPlayer.Album", "ListItem.Label"))
    var("Home_Music_Artist", music("MusicPlayer.Artist", "ListItem.Artist"))
    # the stage glow: the playing album's soft art and colour while music plays (glow_playing, HELPER_API 6)
    var("Home_Music_Soft", [(playing, "$VAR[NP_SoftArt]"), (None, "$VAR[Groove_SoftArt]")])
    var("Home_Music_Glow", [(playing, "$VAR[glow_playing]"), (None, "$VAR[glow]")])
    for key, a, b in (("films", "9111", None),):
        src = f"Container({a})"
        rows = lambda item: ([(f"Integer.IsGreater({src}.NumItems,0)", f"$INFO[{src}.{item}]"), (None, f"$INFO[Container({b}).{item}]")]
                             if b else [(None, f"$INFO[{src}.{item}]")])
        var(f"Home_{key}_Fanart", rows("ListItem.Art(fanart)"))
        var(f"Home_{key}_Logo", rows("ListItem.Art(clearlogo)") if key == "films" else
            ([(f"Integer.IsGreater({src}.NumItems,0)", f"$INFO[{src}.ListItem.Art(clearlogo)]"),
              (None, f"$INFO[Container({b}).ListItem.Art(tvshow.clearlogo)]")]))
        var(f"Home_{key}_Title", rows("ListItem.Label") if key == "films" else
            ([(f"Integer.IsGreater({src}.NumItems,0)", f"$INFO[{src}.ListItem.Label]"),
              (None, f"$INFO[Container({b}).ListItem.TVShowTitle]")]))
        c = src if not b else src
        dur = f"{src}.ListItem.Duration"
        if key == "films":
            var(f"Home_{key}_Runtime", [(f"Integer.IsGreater({dur}(h),0)", f"$INFO[{dur}(h),,h ]$INFO[{dur}(m),,m]"),
                                       (None, f"$INFO[{dur}(m),,m]")])
            var(f"Home_{key}_Rating", [(None, f"$INFO[{src}.ListItem.Rating]")])
        else:
            var(f"Home_{key}_Runtime", [(None, "")])
            var(f"Home_{key}_Rating", [(f"Integer.IsGreater({src}.NumItems,0)", f"$INFO[{src}.ListItem.Rating]"), (None, "")])
    HR.tv_variables(var)
    # 1.0.2 custom rows: the focused custom row's item
    cids = HR.CUSTOM_IDS
    var("Home_custom_Fanart", [x for c in cids for x in (
        (f"Control.HasFocus({c}) + !String.IsEmpty(Container({c}).ListItem.Art(fanart))", f"$INFO[Container({c}).ListItem.Art(fanart)]"),
        (f"Control.HasFocus({c})", f"$INFO[Container({c}).ListItem.Art(tvshow.fanart)]"))])
    var("Home_custom_Logo", [(f"Control.HasFocus({c})", f"$INFO[Container({c}).ListItem.Art(clearlogo)]") for c in cids])
    var("Home_custom_Title", [(f"Control.HasFocus({c})", f"$INFO[Container({c}).ListItem.Label]") for c in cids])
    var("Home_custom_Kicker", [(f"Control.HasFocus({c})", f"$VAR[CustomRow_Title{n}]  ·  $VAR[CustomRow_Count{n}]")
                               for n, c in enumerate(cids, 1)])
    return "\n".join(v)


def main():
    stage_music = f"""		<control type="group">
			<visible>{sect('music')}</visible>
			<include>Anim_SectionSwap</include>
			<include content="Groove_Glow">
				<param name="art" value="$VAR[Home_Music_Cover]"/>
				<param name="soft" value="$VAR[Home_Music_Soft]"/>
				<param name="soft_ready" value="$EXP[HasGrooveHelper] + [[Player.HasAudio + !String.IsEmpty(Window(Home).Property(Groove.Player.Art.Soft))] | [!Player.HasAudio + !String.IsEmpty(Window(Home).Property(Groove.Art.Soft))]]"/>
				<param name="colour" value="$VAR[Home_Music_Glow]"/>
				<param name="wash_x" value="206"/>
				<param name="wash_y" value="-540"/>
				<param name="wash_s" value="1984"/>
				<param name="halo_x" value="516"/>
				<param name="halo_y" value="-230"/>
				<param name="halo_s" value="1364"/>
			</include>
			<control type="group">
				<!-- rest state: the big sleeve; it gives way to the row (Home.md: row open) -->
				<include content="Anim_Dim"><param name="condition" value="$EXP[Home_RowOpen]"/><param name="to" value="0"/></include>
			<!-- the printed disc peeks out of the sleeve (only when the album has disc art) -->
			<control type="image">
				<left>1228</left>
				<top>172</top>
				<width>560</width>
				<height>560</height>
				<aspectratio>keep</aspectratio>
				<fadetime>200</fadetime>
				<texture background="true">$VAR[Home_Music_Disc]</texture>
			</control>
			<control type="group">
				<left>g_cover_home_x</left>
				<top>g_cover_home_y</top>
				<width>g_cover_home</width>
				<height>g_cover_home</height>
				<include content="Groove_ArtParts">
					<param name="art" value="$VAR[Home_Music_Cover]"/>
					<param name="label" value="$VAR[Home_Music_Album]"/>
					<param name="noart" value="[Player.HasAudio + String.IsEmpty(Player.Art(thumb))] | [!Player.HasAudio + String.IsEmpty(Container(9102).ListItem.Art(thumb)) + String.IsEmpty(Container(9101).ListItem.Art(thumb))]"/>
				</include>
			</control>
			<!-- the artist: clearlogo (fallback: the name), right-aligned left of the sleeve -->
			<control type="image">
				<left>424</left>
				<top>150</top>
				<width>400</width>
				<height>90</height>
				<aspectratio align="right" aligny="center">keep</aspectratio>
				<texture background="true" colordiffuse="$VAR[logo_tint]">$VAR[Home_Music_Logo]</texture>
			</control>
			<control type="label">
				<left>224</left>
				<top>164</top>
				<width>600</width>
				<height>60</height>
				<align>right</align>
				<font>font_title_l</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[Home_Music_Artist]</label>
				<visible>[Player.HasAudio + String.IsEmpty(Player.Art(artist.clearlogo))] | [!Player.HasAudio + String.IsEmpty(Container(9101).ListItem.Art(artist.clearlogo)) + String.IsEmpty(Container(9102).ListItem.Art(artist.clearlogo))]</visible>
			</control>
			<include content="Groove_Caption">
				<param name="left" value="598"/>
				<param name="top" value="792"/>
				<param name="title" value="$VAR[Home_Music_Album]"/>
				<param name="meta" value="$VAR[Home_Music_Artist]"/>
			</include>
			</control>
{HR.music_open_hero()}
			<control type="label">
				<left>598</left>
				<top>420</top>
				<width>1200</width>
				<height>40</height>
				<align>center</align>
				<font>font_small</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$LOCALIZE[31415]</label>
				<visible>!Player.HasAudio + Integer.IsEqual(Container(9101).NumItems,0) + !Container(9101).IsUpdating</visible>
			</control>
		</control>"""
    films = video_stage("films", 9611, None).replace("String.IsEmpty($VAR_PLACEHOLDER)", "String.IsEmpty(Container(9111).ListItem.Art(clearlogo))")
    tv = video_stage("tv", 9621, None).replace(
        "String.IsEmpty($VAR_PLACEHOLDER)",
        "[Integer.IsGreater(Container(9121).NumItems,0) + String.IsEmpty(Container(9121).ListItem.Art(clearlogo))] | "
        "[!Integer.IsGreater(Container(9121).NumItems,0) + String.IsEmpty(Container(9122).ListItem.Art(tvshow.clearlogo))]")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_home.py - edit the generator, then re-run. Home at M1: rail + stage (SPEC 5). -->
<includes>
	<expression name="Home_films_Is4K">Integer.IsGreaterOrEqual(Container(9111).ListItem.VideoResolution,2160) | String.IsEqual(Container(9111).ListItem.VideoResolution,4K)</expression>
	<expression name="Home_tv_Is4K">false</expression>
{variables()}
{custom_glyphs()}

	<!-- hidden data lists: drawn first, under the opaque room, so their art loads (LESSONS: hidden lists never load) -->
	<include name="Home_DataLists">
{data_lists()}
	</include>

	<!-- the stage: the focused section's hero, lit (board 01 / 02) -->
	<include name="Home_Stage">
{stage_music}
{films}
{tv}
{icon_stage('search', 'search', 31413)}
{icon_stage('settings', 'settings', 31414)}
{custom_stage()}
{chr(10).join(custom_menu_stage(n) for n, _c in CUSTOM_MENU)}
	</include>

	<!-- the rail: five icons (+ up to three custom menu items after TV), the focused one lit with its label (DESIGN 4: y 920, pitch 232) -->
	<include name="Home_Rail">
		<control type="group">
		<include content="Anim_HomeLift"><param name="open" value="$EXP[Home_RowOpen]"/></include>
		<control type="group" id="9000">
{rail()}
		</control>
		<control type="label">
			<right>g_safe_x</right>
			<top>{Y}</top>
			<width>400</width>
			<height>g_rail_icon</height>
			<align>right</align>
			<aligny>center</aligny>
			<font>font_clock</font>
			<textcolor>$VAR[ink2]</textcolor>
			<label>$VAR[ClockLabel]</label>
			<visible>!$EXP[Home_RailFull]</visible>
		</control>
		</control>
	</include>

{HR.rows()}
</includes>
"""
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
