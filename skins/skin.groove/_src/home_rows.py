"""Home rows below the rail (M2, skin-developer music lane). Imported by make_home.py; not run on its own.

screens/Home.md: Down from a rail icon opens that section's single row; the rail lifts 390 px (y 920 -> 530) and the row
slides up to y 640 (MOTION 5.5: Anim_HomeLift on the rail, Anim_Reveal on the rows, always processed and faded when
closed, never <visible> false: a hidden list never loads, LESSONS Passe-partout). Up / Back return to the rail icon.

Ids (window-local, Home): 9101 music row (random albums; also the music hero's fallback source), 9010 / 9011 Time machine
and Wheel tiles, 9111 films row, 9121 TV row (embuary next-up when that add-on is enabled, else shows in progress),
9122 TV fallback row (new episodes, used when 9121 is empty), 9050 settings row, 9895 clean card, 9897 update card.
The films / TV rows ARE the heroes' data lists, so focusing a row item makes it the hero (the stage variables read
Container(id).ListItem). Every row padded 40 px for the focus light (LESSONS 3).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_music_views as MV  # noqa: E402  (image / lit_layers / cover / rim / fallback builders)

NL = "\n"
T = MV.t
FILMS_XSP = ("videodb://movies/titles/?xsp=%7B%22rules%22%3A%7B%22or%22%3A%5B%7B%22field%22%3A%22inprogress%22%2C"
             "%22operator%22%3A%22true%22%2C%22value%22%3A%5B%22%22%5D%7D%2C%7B%22field%22%3A%22playcount%22%2C"
             "%22operator%22%3A%22is%22%2C%22value%22%3A%5B%220%22%5D%7D%5D%7D%2C%22type%22%3A%22movies%22%7D")
OPEN_IDS = (9101, 9010, 9011, 9111, 9121, 9122, 9050, 9895, 9897, 9881, 9882, 9883)
# 1.0.2 custom rows (Includes_CustomRows.xml, opt-in): 9881-9883 open in the same slot as a section row, one at a time.
# Down from a section row (or a tile, or the Search icon, which has no row) goes to the first custom row that has
# items; Down / Up walk the custom rows; Up from the first returns to the section row you came from; Back -> rail icon.
CUSTOM_IDS = (9881, 9882, 9883)
DOWN_CUSTOM = '<ondown condition="$EXP[CustomRowsAnyOn]">$VAR[Home_DownToCustom]</ondown>'
# the Square art fallback test: the real infolabels behind $VAR[CustomRow_SquareArt] (LESSONS 2)
CUSTOM_ART_EMPTY = ("ListItem.Art(thumb)) + String.IsEmpty(ListItem.Art(poster)) + String.IsEmpty(ListItem.Art(album.thumb))"
                    " + [String.IsEmpty(ListItem.DBType) | [String.IsEmpty(ListItem.Art(landscape))"
                    " + String.IsEmpty(ListItem.Art(fanart))]] + String.IsEmpty(ListItem.Art(thumb)")
ROW_OPEN = "[" + " | ".join(f"Control.HasFocus({i})" for i in OPEN_IDS) + "]"
MINI_UP = '<onup condition="Player.HasAudio + Control.IsVisible(9950)">9950</onup>'


def rail_nav(key):
    """extra navigation for the rail button of `key` (music films tv search settings)"""
    n = {
        "music": ['<ondown condition="Integer.IsGreater(Container(9101).NumItems,0)">9101</ondown>', "<ondown>9010</ondown>"],
        "films": ["<ondown>9111</ondown>"],
        "tv": ['<ondown condition="Integer.IsGreater(Container(9121).NumItems,0)">9121</ondown>', "<ondown>9122</ondown>"],
        "search": [DOWN_CUSTOM],
        "settings": ["<ondown>9050</ondown>"],
    }[key]
    return "".join(NL + T(4) + x for x in [MINI_UP] + n)


def tv_variables(var):
    """TV hero: the focused / first item of 9121 (episodes from embuary, or shows), else of 9122 (episodes)"""
    use22 = "[Control.HasFocus(9122) | !Integer.IsGreater(Container(9121).NumItems,0)]"

    def pick(*items):
        rows = []
        for c in ("9122", "9121"):
            cond = use22 if c == "9122" else None
            for i, it in enumerate(items):
                last = i == len(items) - 1
                parts = [p for p in (cond, None if last else f"!String.IsEmpty(Container({c}).ListItem.{it})") if p]
                rows.append((" + ".join(parts) if parts else None, f"$INFO[Container({c}).ListItem.{it}]"))
        return rows
    var("Home_tv_Fanart", pick("Art(fanart)", "Art(tvshow.fanart)"))
    var("Home_tv_Logo", pick("Art(clearlogo)", "Art(tvshow.clearlogo)"))
    var("Home_tv_Title", pick("TVShowTitle", "Label"))
    var("Home_tv_Runtime", [(None, "")])
    var("Home_tv_Rating", [(f"!{use22}", "$INFO[Container(9121).ListItem.Rating]"), (None, "")])


def music_open_hero():
    """Music stage while the row is open (Home.md): clearlogo top-left (fallback the artist name) + one caption line"""
    # same order as make_home.py Home_Music_*: playing album > focused row item > last played > first random
    nologo = ("[Player.HasAudio + String.IsEmpty(Player.Art(artist.clearlogo))] | "
              "[!Player.HasAudio + Control.HasFocus(9101) + String.IsEmpty(Container(9101).ListItem.Art(artist.clearlogo))] | "
              "[!Player.HasAudio + !Control.HasFocus(9101) + Integer.IsGreater(Container(9102).NumItems,0) + String.IsEmpty(Container(9102).ListItem.Art(artist.clearlogo))] | "
              "[!Player.HasAudio + !Control.HasFocus(9101) + !Integer.IsGreater(Container(9102).NumItems,0) + String.IsEmpty(Container(9101).ListItem.Art(artist.clearlogo))]")
    return f"""			<control type="group">
				<!-- row open: the artist + album at the top left, the room keeps the album's glow -->
				<include content="Anim_Dim"><param name="condition" value="!$EXP[Home_RowOpen]"/><param name="to" value="0"/></include>
				<control type="image">
					<left>96</left>
					<top>120</top>
					<width>600</width>
					<height>210</height>
					<aspectratio align="left" aligny="bottom">keep</aspectratio>
					<texture background="true" colordiffuse="$VAR[logo_tint]">$VAR[Home_Music_Logo]</texture>
				</control>
				<control type="label">
					<left>96</left>
					<top>250</top>
					<width>1200</width>
					<height>72</height>
					<aligny>center</aligny>
					<font>font_title_l</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$VAR[Home_Music_Artist]</label>
					<visible>{nologo}</visible>
				</control>
				<control type="label">
					<left>96</left>
					<top>360</top>
					<width>1400</width>
					<height>48</height>
					<aligny>center</aligny>
					<font>font_caption</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$VAR[Home_Music_Album][COLOR $VAR[ink2]]  ·  $VAR[Home_Music_Artist][/COLOR]</label>
				</control>
			</control>"""


# ---------------------------------------------------------------- row pieces
def lifted(open_cond, dy=120, t=320):
    return (f'<include content="Anim_Reveal"><param name="closed" value="!{open_cond}"/>'
            f'<param name="dy" value="{dy}"/><param name="t" value="{t}"/></include>')


def art_item(w, h, art, label, list_id, focused, round_=False, extra_after=""):
    """one row item: the art at (40, 40) of a slot padded 40 px for its light"""
    ind = 4
    diffuse = None if focused else "$VAR[dim_cover]"
    # the fallback tests the real infolabels: String.IsEmpty($VAR[...]) is invalid (LESSONS 2)
    if art.startswith("$INFO["):
        probe = art[len("$INFO["):-1]
    elif art == "$VAR[CustomRow_SquareArt]":
        probe = CUSTOM_ART_EMPTY
    elif art == "$VAR[Home_TVCard]":
        probe = ("ListItem.Art(thumb)) + String.IsEmpty(ListItem.Art(tvshow.landscape)) + String.IsEmpty(ListItem.Art(landscape))"
                 " + String.IsEmpty(ListItem.Art(tvshow.fanart)) + String.IsEmpty(ListItem.Art(fanart)")
    else:
        raise ValueError("art_item: no empty-test for " + art)
    g = []
    lit = f"Control.HasFocus({list_id})"
    if focused:
        g.append(MV.lit_layers(w, h, lit, ind + 1, radial=2.2, clamp=24))
    else:
        g.append(MV.image(-24, -16, w + 48, h + 48, "groove/shadow_contact.png", "$VAR[shadow]", None, ind=ind + 1,
                          texattr=' border="24,16,24,32"'))
    g.append(MV.fallback(w, h, label, probe, ind + 1))
    g.append(MV.image(0, 0, w, h, art, diffuse, None, "<include>Anim_FocusBrighten</include>" if focused else "",
                      aspect="scale", bg=True, ind=ind + 1))
    if focused:
        g.append(MV.rim(w, h, lit, ind + 1, "<include>Anim_FocusRim</include>"))
    zoom = (f'{NL}{T(ind + 1)}<include content="Anim_FocusCover"><param name="center" value="{24 + w // 2},{40 + h // 2}"/></include>'
            if focused else "")
    return f"""{T(ind)}<control type="group">
{T(ind + 1)}<left>24</left>
{T(ind + 1)}<top>40</top>
{T(ind + 1)}<width>{w}</width>
{T(ind + 1)}<height>{h}</height>{zoom}
{NL.join(g)}
{T(ind)}</control>{extra_after}"""


def row(list_id, left, width, item_w, item_h, art_w, art_h, art, label, content, nav, movement, extra="", after_f=""):
    return f"""		<control type="fixedlist" id="{list_id}">
			<left>{left}</left>
			<top>600</top>
			<width>{width}</width>
			<height>{item_h}</height>
			<orientation>horizontal</orientation>
			<focusposition>0</focusposition>
			<movement>{movement}</movement>
			<preloaditems>2</preloaditems>
			<include>Anim_ScrollRow</include>
			<onfocus>SetProperty(TMDbHelper.WidgetContainer,{list_id},home)</onfocus>
			<onfocus>ClearProperty(Groove.Helper.Container,home)</onfocus>
{nav}{extra}
			<itemlayout width="{item_w}" height="{item_h}">
{art_item(art_w, art_h, art, label, list_id, False)}
			</itemlayout>
			<focusedlayout width="{item_w}" height="{item_h}">
{art_item(art_w, art_h, art, label, list_id, True, extra_after=after_f)}
			</focusedlayout>
			{content}
		</control>"""


def tile(cid, x, icon, label, nav, click):
    # label wraps inside the 136 px tile ("Time machine" is 149 px in Jost Medium 24: two lines, Pass 2 n7)
    ix, iy = x + 36, 726
    return f"""		<control type="image">
			<left>{x}</left>
			<top>640</top>
			<width>136</width>
			<height>300</height>
			<texture border="4" colordiffuse="$VAR[line_hair]">groove/card_edge.png</texture>
		</control>
		<control type="image">
			<left>{ix - 45}</left>
			<top>{iy - 45}</top>
			<width>154</width>
			<height>154</height>
			<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
			<visible>Control.HasFocus({cid})</visible>
			<include>Anim_LabelReveal</include>
		</control>
		<control type="button" id="{cid}">
			<left>{x}</left>
			<top>640</top>
			<width>136</width>
			<height>300</height>
			<texturefocus border="4" colordiffuse="$VAR[rim]">groove/card_edge.png</texturefocus>
			<texturenofocus />
			<label />
			<onclick>{click}</onclick>
			<onfocus>ClearProperty(TMDbHelper.WidgetContainer,home)</onfocus>
			<onfocus>ClearProperty(Groove.Helper.Container,home)</onfocus>
{nav}
		</control>
		<control type="image">
			<left>{ix}</left>
			<top>{iy}</top>
			<width>64</width>
			<height>64</height>
			<texture colordiffuse="$VAR[icon_rest]">icons/{icon}.png</texture>
			<visible>!Control.HasFocus({cid})</visible>
		</control>
		<control type="image">
			<left>{ix}</left>
			<top>{iy}</top>
			<width>64</width>
			<height>64</height>
			<texture colordiffuse="$VAR[ink]">icons/{icon}.png</texture>
			<visible>Control.HasFocus({cid})</visible>
		</control>
		<control type="label">
			<left>{x + 8}</left>
			<top>824</top>
			<width>120</width>
			<height>72</height>
			<align>center</align>
			<aligny>center</aligny>
			<wrapmultiline>true</wrapmultiline>
			<font>font_tray</font>
			<textcolor>$VAR[ink]</textcolor>
			<label>{label}</label>
			<visible>Control.HasFocus({cid})</visible>
			<include>Anim_LabelReveal</include>
		</control>"""


def card_row(list_id, focused):
    f = f"Control.HasFocus({list_id})" if focused else "false"
    return f"""				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>616</width>
					<height>64</height>
					<texture colordiffuse="$VAR[focus_fill]">groove/white.png</texture>
					<visible>{f}</visible>
				</control>
				<control type="image">
					<left>12</left>
					<top>12</top>
					<width>40</width>
					<height>40</height>
					<texture colordiffuse="$VAR[ink2]">$INFO[ListItem.Icon]</texture>
					<visible>!{f}</visible>
				</control>
				<control type="image">
					<left>12</left>
					<top>12</top>
					<width>40</width>
					<height>40</height>
					<texture colordiffuse="$VAR[ink]">$INFO[ListItem.Icon]</texture>
					<visible>{f}</visible>
				</control>
				<control type="label">
					<left>76</left>
					<top>0</top>
					<width>360</width>
					<height>64</height>
					<aligny>center</aligny>
					<font>font_label</font>
					<textcolor>$VAR[ink2]</textcolor>
					<selectedcolor>$VAR[ink2]</selectedcolor>
					<label>$INFO[ListItem.Label]</label>
					<visible>!{f}</visible>
				</control>
				<control type="label">
					<left>76</left>
					<top>0</top>
					<width>360</width>
					<height>64</height>
					<aligny>center</aligny>
					<font>font_label</font>
					<textcolor>$VAR[ink]</textcolor>
					<selectedcolor>$VAR[ink]</selectedcolor>
					<label>$INFO[ListItem.Label]</label>
					<visible>{f}</visible>
				</control>
				<control type="label">
					<left>404</left>
					<top>0</top>
					<width>200</width>
					<height>64</height>
					<align>right</align>
					<aligny>center</aligny>
					<font>font_small</font>
					<textcolor>$VAR[ink2]</textcolor>
					<selectedcolor>$VAR[ink2]</selectedcolor>
					<label>$INFO[ListItem.Label2]</label>
				</control>"""


def card(group_id, list_id, top, rows_n, icon, title, items):
    h = 96 + 64 * rows_n
    return f"""		<control type="group" id="{group_id}">
			<include content="Lib_FadeGate"><param name="show" value="Control.HasFocus({list_id})"/></include>
			<include>Lib_Dim</include>
			<control type="group">
				<left>640</left>
				<top>{top}</top>
				<include content="Lib_Card">
					<param name="left" value="0"/><param name="top" value="0"/><param name="width" value="640"/><param name="height" value="{h}"/>
					<param name="shadow_w" value="832"/><param name="shadow_h" value="{h + 180}"/>
				</include>
				<control type="image">
					<left>24</left>
					<top>16</top>
					<width>40</width>
					<height>40</height>
					<texture colordiffuse="$VAR[ink]">icons/{icon}.png</texture>
				</control>
				<control type="label">
					<left>88</left>
					<top>0</top>
					<width>520</width>
					<height>72</height>
					<aligny>center</aligny>
					<font>font_label</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>{title}</label>
				</control>
				<control type="list" id="{list_id}">
					<left>12</left>
					<top>72</top>
					<width>616</width>
					<height>{64 * rows_n}</height>
					<!-- Up (first row) / Left also leave: while something plays Kodi takes Back on Home first (DEVICE_AUDIT M3) -->
					<onup>9050</onup>
					<ondown>noop</ondown>
					<onleft>9050</onleft>
					<onright>noop</onright>
					<onback>9050</onback>
					<itemlayout width="616" height="64">
{card_row(list_id, False)}
					</itemlayout>
					<focusedlayout width="616" height="64">
{card_row(list_id, True)}
					</focusedlayout>
					<content>
{items}
					</content>
				</control>
			</control>
		</control>"""


SETTINGS = [  # label string, icon, onclick(s), visible
    (31620, "skin", ["ActivateWindow(SkinSettings)"], None),
    (31621, "system", ["ActivateWindow(Settings)"], None),
    (31622, "update", ["SetFocus(9897,0,absolute)"], None),
    (31623, "clean", ["SetFocus(9895,0,absolute)"], None),
    (31624, "addons", ["ActivateWindow(AddonBrowser)"], None),
    (31625, "files", ["ActivateWindow(Videos,sources://video/,return)"], None),
    (31626, "pictures", ["ActivateWindow(Pictures)"], None),
    (31627, "favourites", ["ActivateWindow(FavouritesBrowser)"], None),
    (31628, "livetv", ["ActivateWindow(TVChannels)"], "System.HasPVRAddon"),
    (31629, "power", ["ActivateWindow(ShutdownMenu)"], None),
]


def settings_tile(focused):
    f = "Control.HasFocus(9050)" if focused else "false"
    o = [MV.image(40, 40, 160, 160, "groove/white.png", "$VAR[focus_fill]", f, ind=4),
         MV.image(-17, -17, 274, 274, "groove/glow_radial.png", "$VAR[focus_glow]", f, "<include>Anim_FocusLight</include>", ind=4),
         MV.image(40, 40, 160, 160, "groove/card_edge.png", "$VAR[line_hair]", f"!{f}", ind=4, texattr=' border="4"'),
         MV.image(40, 40, 160, 160, "groove/card_edge.png", "$VAR[rim]", f, ind=4, texattr=' border="4"'),
         MV.image(72, 72, 96, 96, "$INFO[ListItem.Icon]", "$VAR[icon_rest]", f"!{f}", ind=4),
         MV.image(72, 72, 96, 96, "$INFO[ListItem.Icon]", "$VAR[ink]", f, ind=4)]
    if focused:
        o.append(f"""{T(4)}<control type="label">
{T(5)}<left>-20</left>
{T(5)}<top>216</top>
{T(5)}<width>280</width>
{T(5)}<height>40</height>
{T(5)}<align>center</align>
{T(5)}<aligny>center</aligny>
{T(5)}<font>font_label</font>
{T(5)}<textcolor>$VAR[ink]</textcolor>
{T(5)}<selectedcolor>$VAR[ink]</selectedcolor>
{T(5)}<label>$INFO[ListItem.Label]</label>
{T(5)}<visible>{f}</visible>
{T(4)}</control>""")
    return NL.join(o)


def custom_rows():
    """the three custom rows: square art (albums, posters, add-on folders) in the music row's size, full width"""
    o = []
    for k, cid in enumerate(CUSTOM_IDS):
        n = k + 1
        ups = [f'<onup condition="$EXP[CustomRow{j + 1}On]">{CUSTOM_IDS[j]}</onup>' for j in range(k - 1, -1, -1)]
        downs = [f'<ondown condition="$EXP[CustomRow{j + 1}On]">{CUSTOM_IDS[j]}</ondown>' for j in range(k + 1, len(CUSTOM_IDS))]
        nav = "\n".join("\t\t\t" + x for x in ups + ["<onup>$VAR[Home_UpFromCustom]</onup>"] + downs
                        + ["<ondown>noop</ondown>", "<onleft>noop</onleft>", "<onright>noop</onright>",
                           "<onback>$VAR[Home_BackFromCustom]</onback>"])
        r = row(cid, 72, 1848, 324, 380, 300, 300, "$VAR[CustomRow_SquareArt]", "$INFO[ListItem.Label]",
                f'<include content="CustomRow_Content"><param name="row" value="{n}"/></include>', nav, 4)
        # the custom rows clear the TMDb Helper / KarmaMole containers (no colour service for an add-on folder)
        r = r.replace(f"<onfocus>SetProperty(TMDbHelper.WidgetContainer,{cid},home)</onfocus>",
                      "<onfocus>ClearProperty(TMDbHelper.WidgetContainer,home)</onfocus>")
        o.append(f"""		<control type="group">
			{lifted(f"Control.HasFocus({cid})")}
{r}
		</control>""")
    return "\n".join(o)


def rows():
    music_open = "[Control.HasFocus(9101) | Control.HasFocus(9010) | Control.HasFocus(9011)]"
    music_row = row(
        9101, 408, 1512, 324, 380, 300, 300, "$INFO[ListItem.Art(thumb)]", "$INFO[ListItem.Label]",
        '<content target="music" sortby="random" limit="20" browse="never">special://skin/playlists/groove_random_albums.xsp</content>',
        "\t\t\t<onup>9001</onup>\n\t\t\t<onback>9001</onback>\n\t\t\t" + DOWN_CUSTOM + "\n\t\t\t<ondown>noop</ondown>\n\t\t\t<onleft>9011</onleft>\n\t\t\t<onright>noop</onright>",
        3, "\n\t\t\t<onclick>Action(Info)</onclick>")
    films_row = row(
        9111, 72, 1848, 224, 400, 200, 300, "$INFO[ListItem.Art(poster)]", "$INFO[ListItem.Label]",
        f'<content target="videos" sortby="lastplayed" sortorder="descending" limit="24" browse="never">{FILMS_XSP}</content>',
        "\t\t\t<onup>9002</onup>\n\t\t\t<onback>9002</onback>\n\t\t\t" + DOWN_CUSTOM + "\n\t\t\t<ondown>noop</ondown>\n\t\t\t<onleft>noop</onleft>\n\t\t\t<onright>noop</onright>",
        6)
    tvline = f"""
{T(4)}<control type="label">
{T(5)}<left>24</left>
{T(5)}<top>326</top>
{T(5)}<width>480</width>
{T(5)}<height>36</height>
{T(5)}<font>font_small</font>
{T(5)}<textcolor>$VAR[ink2]</textcolor>
{T(5)}<selectedcolor>$VAR[ink2]</selectedcolor>
{T(5)}<label>$VAR[Home_TVCardLine]</label>
{T(4)}</control>"""
    tv_nav = lambda rail: f"\t\t\t<onup>{rail}</onup>\n\t\t\t<onback>{rail}</onback>\n\t\t\t{DOWN_CUSTOM}\n\t\t\t<ondown>noop</ondown>\n\t\t\t<onleft>noop</onleft>\n\t\t\t<onright>noop</onright>"
    tv_row = row(9121, 72, 1848, 504, 380, 480, 270, "$VAR[Home_TVCard]", "$INFO[ListItem.Label]",
                 '<content target="videos" sortby="$VAR[Home_TVSort]" sortorder="descending" limit="24" browse="never">$VAR[Home_TVPath]</content>',
                 tv_nav(9003), 2, after_f=tvline)
    tv_row2 = row(9122, 72, 1848, 504, 380, 480, 270, "$VAR[Home_TVCard]", "$INFO[ListItem.Label]",
                  '<content target="videos" sortby="dateadded" sortorder="descending" limit="24" browse="never">special://skin/playlists/groove_tv_new_episodes.xsp</content>',
                  tv_nav(9003), 2, after_f=tvline)
    items = []
    for sid, icon, clicks, vis in SETTINGS:
        c = "".join(f"\n\t\t\t\t\t<onclick>{x}</onclick>" for x in clicks)
        v = f"\n\t\t\t\t\t<visible>{vis}</visible>" if vis else ""
        items.append(f"\t\t\t\t<item>\n\t\t\t\t\t<label>$LOCALIZE[{sid}]</label>\n\t\t\t\t\t<icon>icons/96/{icon}.png</icon>{c}{v}\n\t\t\t\t</item>")
    settings_row = f"""		<control type="list" id="9050">
			<left>56</left>
			<top>620</top>
			<width>1864</width>
			<height>280</height>
			<orientation>horizontal</orientation>
			<onup>9005</onup>
			<onback>9005</onback>
			{DOWN_CUSTOM}
			<ondown>noop</ondown>
			<onleft>noop</onleft>
			<onright>noop</onright>
			<onfocus>ClearProperty(TMDbHelper.WidgetContainer,home)</onfocus>
			<onfocus>ClearProperty(Groove.Helper.Container,home)</onfocus>
			<include>Anim_ScrollRow</include>
			<itemlayout width="184" height="280">
{settings_tile(False)}
			</itemlayout>
			<focusedlayout width="184" height="280">
{settings_tile(True)}
			</focusedlayout>
			<content>
{NL.join(items)}
			</content>
		</control>"""
    clean_items = "\n".join([
        "\t\t\t\t\t\t<item><label>$LOCALIZE[31630]</label><icon>icons/back.png</icon><onclick>SetFocus(9050)</onclick></item>",
        "\t\t\t\t\t\t<item><label>$LOCALIZE[31631]</label><icon>icons/music.png</icon><onclick>CleanLibrary(music)</onclick><onclick>SetFocus(9050)</onclick></item>",
        "\t\t\t\t\t\t<item><label>$LOCALIZE[31632]</label><icon>icons/films.png</icon><onclick>CleanLibrary(video)</onclick><onclick>SetFocus(9050)</onclick></item>",
    ])
    update_items = "\n".join([
        "\t\t\t\t\t\t<item><label>$LOCALIZE[31633]</label><label2>$VAR[Home_ScanMusic]</label2><icon>icons/music.png</icon><onclick>UpdateLibrary(music)</onclick><onclick>SetFocus(9050)</onclick></item>",
        "\t\t\t\t\t\t<item><label>$LOCALIZE[31634]</label><label2>$VAR[Home_ScanVideo]</label2><icon>icons/films.png</icon><onclick>UpdateLibrary(video)</onclick><onclick>SetFocus(9050)</onclick></item>",
    ])
    return f"""	<!-- ============================================================ Home rows (M2, _src/home_rows.py) -->
	<expression name="Home_RowOpen">{ROW_OPEN}</expression>
	<variable name="Home_TVPath">
		<value condition="System.AddonIsEnabled(script.embuary.helper)">plugin://script.embuary.helper/?info=getnextup</value>
		<value>special://skin/playlists/groove_inprogress_tvshows.xsp</value>
	</variable>
	<variable name="Home_TVSort">
		<value condition="System.AddonIsEnabled(script.embuary.helper)">none</value>
		<value>lastplayed</value>
	</variable>
	<variable name="Home_TVCard">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.landscape))">$INFO[ListItem.Art(tvshow.landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
		<value>$INFO[ListItem.Art(fanart)]</value>
	</variable>
	<variable name="Home_TVCardLine">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle,,  ·  ]S$INFO[ListItem.Season]·E$INFO[ListItem.Episode]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Home_ScanMusic">
		<value condition="Library.IsScanningMusic">$LOCALIZE[31612]</value>
	</variable>
	<variable name="Home_ScanVideo">
		<value condition="Library.IsScanningVideo">$LOCALIZE[31612]</value>
	</variable>

	<!-- custom rows (1.0.2, opt-in): the way in and the way back to the section row (by the rail icon you came from) -->
	<variable name="Home_DownToCustom">
		<value condition="$EXP[CustomRow1On]">SetFocus(9881)</value>
		<value condition="$EXP[CustomRow2On]">SetFocus(9882)</value>
		<value condition="$EXP[CustomRow3On]">SetFocus(9883)</value>
	</variable>
	<variable name="Home_UpFromCustom">
		<value condition="String.IsEqual(Window(Home).Property(groove.railid),9001) + Integer.IsGreater(Container(9101).NumItems,0)">SetFocus(9101)</value>
		<value condition="String.IsEqual(Window(Home).Property(groove.railid),9001)">SetFocus(9010)</value>
		<value condition="String.IsEqual(Window(Home).Property(groove.railid),9002)">SetFocus(9111)</value>
		<value condition="String.IsEqual(Window(Home).Property(groove.railid),9003) + Integer.IsGreater(Container(9121).NumItems,0)">SetFocus(9121)</value>
		<value condition="String.IsEqual(Window(Home).Property(groove.railid),9003)">SetFocus(9122)</value>
		<value condition="String.IsEqual(Window(Home).Property(groove.railid),9005)">SetFocus(9050)</value>
		<value condition="!String.IsEmpty(Window(Home).Property(groove.railid))">SetFocus($INFO[Window(Home).Property(groove.railid)])</value>
		<value>SetFocus(9005)</value>
	</variable>
	<variable name="Home_BackFromCustom">
		<value condition="!String.IsEmpty(Window(Home).Property(groove.railid))">SetFocus($INFO[Window(Home).Property(groove.railid)])</value>
		<value>SetFocus(9005)</value>
	</variable>

	<include name="Home_Rows">
		<control type="group">
			{lifted(music_open, t=340)}
{tile(9010, 96, "timemachine", "$LOCALIZE[31407]", f"			<onup>9001</onup>{NL}			<onback>9001</onback>{NL}			{DOWN_CUSTOM}{NL}			<ondown>noop</ondown>{NL}			<onleft>noop</onleft>{NL}			<onright>9011</onright>", "ActivateWindow(1170)")}
{tile(9011, 256, "wheel", "$LOCALIZE[31408]", f"			<onup>9001</onup>{NL}			<onback>9001</onback>{NL}			{DOWN_CUSTOM}{NL}			<ondown>noop</ondown>{NL}			<onleft>9010</onleft>{NL}			<onright condition=\"Integer.IsGreater(Container(9101).NumItems,0)\">9101</onright>{NL}			<onright>noop</onright>", "ActivateWindow(1171)")}
		</control>
		<control type="group">
			{lifted(music_open)}
{music_row}
		</control>
		<control type="group">
			{lifted("Control.HasFocus(9111)")}
{films_row}
		</control>
		<control type="group">
			{lifted("Control.HasFocus(9121)")}
{tv_row}
		</control>
		<control type="group">
			{lifted("Control.HasFocus(9122)")}
{tv_row2}
		</control>
		<control type="group">
			{lifted("[Control.HasFocus(9050) | Control.HasFocus(9895) | Control.HasFocus(9897)]")}
{settings_row}
		</control>
{custom_rows()}
	</include>

	<!-- Clean / Update cards: drawn after Home_Rail (Home.xml) so the dim and the card cover the rail icons (DEVICE_AUDIT pass 2) -->
	<include name="Home_Cards">
{card(9894, 9895, 396, 3, "clean", "$LOCALIZE[31641]", clean_items)}
{card(9896, 9897, 428, 2, "update", "$LOCALIZE[31642]", update_items)}
	</include>"""
