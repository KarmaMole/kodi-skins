"""Generate 1080i/Includes_Views_More.xml: the 0.9.16 library views (docs/VIEWS_BRIEF_2026-10-27.md).

    python skins/skin.duotone/_src/make_views_more.py

Duotone's existing views stay as they are: 500 Wall, 503 Episodes, 50 List (video), 504 Albums wall, 50 List (music).
New, all in the poster-print language (every picture a one-colour print in the section colour on the halftone field,
the focused item alone in full colour with the 8 px ink frame, Anton type, 8 px ink rules, no gradients):
  505 Poster   the showcase: Anton masthead, three numerals between rules, the plot, and one 576 x 864 print of the
               focused item (full colour while the view has focus). An invisible list drives it: Left / Right flip
               the item, the ink pager tab on the print says where you are. Every video content.
  506 Screens  3 x 2 wide prints (576 x 324: landscape, episode still, fanart; a poster or icon sits whole on the ink
               block) with the Anton title under each. Every video content (series, episodes, sets, add-ons, plug-ins).
  507 Sheet    the dense wall: a contact sheet of 10 x 3 small prints (156 x 234) and an ink caption band under it.
               Films, sets, series, seasons, music videos.
  508 Stage    music artists / albums: the fanart as a full-width print band, the name in Anton on an ink block,
               a strip of square cover prints underneath (the d-pad moves along the strip).
  509 Tracks   songs: 72 px rows with Anton numerals, title, artist / album, time; focused row = ink bar; the
               focused song's cover as a print in the right column.
0.9.18 (docs/VIEWS_PER_SECTION_2026-10-28.md):
  510 Rows     films, sets, series, music videos: 160 px rows, a 256 x 144 wide print (a poster kept whole on the ink
               block), the Anton title, a meta line in the section colour and two lines of plot; the focused row is
               the ink bar with the print in full colour (Tracks' language). Typed biglist, last in <views>.
  508 Stage    now also songs (the artist's fanart band, the song title in Anton, a strip of the songs' covers).
viewtypes: Kodi's defaults ask for list / icon / big icon / info (CAutoSwitch: info when a quarter of the items carry
metadata), so the new views use bigwrap / wide / bigwide / biglist and never become a folder's default.
Every colour is a look token ($VAR[...], CONVENTIONS 4); check with _src/check_tokens.py.
"""
from pathlib import Path

from default_repeats import strip as strip_defaults
from xmlfinish import finish_xml

ROOT = Path(__file__).resolve().parents[1] / "1080i"
OUT = ROOT / "Includes_Views_More.xml"

V = "Window.IsActive(videos)"
M = "Window.IsActive(music)"
POSTER_KINDS = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
                "Container.Content(seasons) | Container.Content(musicvideos)]")
EMPTY = "Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating"
SEP = "  ·  "
PANEL = "ActivateWindow(1155)"

# --------------------------------------------------------------------------------- variables
VARIABLES = f"""
	<!-- ============================================================ variables (views 505-509) -->
	<variable name="View_PosterKicker">
		<value condition="ListItem.IsParentFolder">Up one level</value>
		<value condition="String.IsEqual(ListItem.DBType,episode)">$VAR[VidView_EpKicker]</value>
		<value condition="String.IsEqual(ListItem.DBType,season)">$INFO[ListItem.TVShowTitle]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Collection</value>
		<value>$VAR[VidView_Kicker]</value>
	</variable>
	<variable name="View_PosterPlot">
		<value condition="ListItem.IsParentFolder">OK goes up one level.</value>
		<value condition="!String.IsEmpty(ListItem.Plot)">$INFO[ListItem.Plot]</value>
		<value>$INFO[ListItem.Tagline]</value>
	</variable>
	<!-- Screens (506): the wide print, or a poster / icon kept whole on the ink block -->
	<expression name="View_ScreenHasWide">[String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)] | !String.IsEmpty(ListItem.Art(landscape)) | !String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.fanart))</expression>
	<expression name="View_ScreenHasArt">ListItem.IsParentFolder | $EXP[View_ScreenHasWide] | !String.IsEmpty(ListItem.Art(poster)) | !String.IsEmpty(ListItem.Art(tvshow.poster)) | !String.IsEmpty(ListItem.Art(thumb)) | [!String.IsEmpty(ListItem.Art(icon)) + !String.StartsWith(ListItem.Art(icon),Default)]</expression>
	<variable name="View_ScreenWide">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value>$INFO[ListItem.Art(tvshow.fanart)]</value>
	</variable>
	<variable name="View_ScreenSmall">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value>$INFO[ListItem.Art(icon)]</value>
	</variable>
	<variable name="View_ScreenTitle">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Episode,,  ]$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<!-- Sheet (507) caption band -->
	<variable name="View_SheetMeta">
		<value condition="Container(507).ListItem.IsParentFolder">Up one level</value>
		<value condition="String.IsEqual(Container(507).ListItem.DBType,tvshow)">$INFO[Container(507).ListItem.Year]$INFO[Container(507).ListItem.Property(TotalSeasons),{SEP}, seasons]$INFO[Container(507).ListItem.Property(UnWatchedEpisodes),{SEP}, to watch]</value>
		<value condition="String.IsEqual(Container(507).ListItem.DBType,season)">$INFO[Container(507).ListItem.Property(TotalEpisodes),, episodes]$INFO[Container(507).ListItem.Property(UnWatchedEpisodes),{SEP}, to watch]</value>
		<value condition="String.IsEqual(Container(507).ListItem.DBType,set)">$INFO[Container(507).ListItem.Property(Total),, films]$INFO[Container(507).ListItem.Property(Watched),{SEP}, watched]</value>
		<value condition="!String.IsEmpty(Container(507).ListItem.Year)">$INFO[Container(507).ListItem.Year]$INFO[Container(507).ListItem.Duration(mins),{SEP}, min]$INFO[Container(507).ListItem.Rating,{SEP},]</value>
		<value>$INFO[Container(507).ListItem.Label2]</value>
	</variable>
	<variable name="View_SheetTitle">
		<value condition="Container(507).ListItem.IsParentFolder">Back</value>
		<value>$INFO[Container(507).ListItem.Label]</value>
	</variable>
	<!-- Stage (508): artists and albums -->
	<expression name="Stage_HasFanart">!String.IsEmpty(Container(508).ListItem.Art(fanart)) | !String.IsEmpty(Container(508).ListItem.Art(artist.fanart)) | !String.IsEmpty(Container(508).ListItem.Art(albumartist.fanart))</expression>
	<variable name="Stage_Fanart">
		<value condition="!String.IsEmpty(Container(508).ListItem.Art(fanart))">$INFO[Container(508).ListItem.Art(fanart)]</value>
		<value condition="!String.IsEmpty(Container(508).ListItem.Art(artist.fanart))">$INFO[Container(508).ListItem.Art(artist.fanart)]</value>
		<value>$INFO[Container(508).ListItem.Art(albumartist.fanart)]</value>
	</variable>
	<variable name="Stage_Name">
		<value condition="Container(508).ListItem.IsParentFolder">Back</value>
		<value condition="String.IsEqual(Container(508).ListItem.DBType,song) + !String.IsEmpty(Container(508).ListItem.Title)">$INFO[Container(508).ListItem.Title]</value>
		<value>$INFO[Container(508).ListItem.Label]</value>
	</variable>
	<!-- strip cards without a cover: songs print their title, not Kodi's "01. Artist - Title" label -->
	<variable name="Stage_CellTitle">
		<value condition="String.IsEqual(ListItem.DBType,song) + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Stage_Kicker">
		<value condition="Container(508).ListItem.IsParentFolder">Up one level</value>
		<value condition="String.IsEqual(Container(508).ListItem.DBType,song)">Song$INFO[Container(508).ListItem.Artist,{SEP},]</value>
		<value condition="String.IsEqual(Container(508).ListItem.DBType,artist)">Artist$INFO[Container(508).ListItem.Genre,{SEP},]</value>
		<value>Album$INFO[Container(508).ListItem.Artist,{SEP},]</value>
	</variable>
	<variable name="Stage_Meta">
		<value condition="String.IsEqual(Container(508).ListItem.DBType,song) + !String.IsEmpty(Container(508).ListItem.Album)">$INFO[Container(508).ListItem.Album]$INFO[Container(508).ListItem.Year,{SEP},]$INFO[Container(508).ListItem.Duration,{SEP},]</value>
		<value condition="String.IsEqual(Container(508).ListItem.DBType,song)">$INFO[Container(508).ListItem.Year,,{SEP}]$INFO[Container(508).ListItem.Duration]</value>
		<value condition="String.IsEqual(Container(508).ListItem.DBType,artist)">$INFO[Container(508).ListItem.Property(Artist_Style)]</value>
		<value condition="String.IsEqual(Container(508).ListItem.DBType,album)">$INFO[Container(508).ListItem.Year]$INFO[Container(508).ListItem.Genre,{SEP},]$INFO[Container(508).ListItem.Property(Album_Duration),{SEP},]</value>
	</variable>
	<!-- Tracks (509) -->
	<variable name="Tracks_Title">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Tracks_Num">
		<value condition="ListItem.IsParentFolder"></value>
		<value>$INFO[ListItem.TrackNumber]</value>
	</variable>
	<variable name="Tracks_Where">
		<value condition="!String.IsEmpty(ListItem.Artist) + !String.IsEmpty(ListItem.Album)">$INFO[ListItem.Artist]{SEP}$INFO[ListItem.Album]</value>
		<value>$INFO[ListItem.Artist]$INFO[ListItem.Album]</value>
	</variable>
	<!-- Rows (510) -->
	<variable name="Rows_Title">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Rows_Meta">
		<value condition="ListItem.IsParentFolder">Up one level</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow) + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)">$INFO[ListItem.Year,,{SEP}]$VAR[Rows_Seasons]{SEP}$INFO[ListItem.Property(UnWatchedEpisodes),, to watch]$INFO[ListItem.Genre,{SEP},]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year,,{SEP}]$VAR[Rows_Seasons]{SEP}all seen$INFO[ListItem.Genre,{SEP},]</value>
		<value condition="String.IsEqual(ListItem.DBType,set) + Integer.IsGreater(ListItem.Property(Watched),0)">$INFO[ListItem.Property(Total),, films]$INFO[ListItem.Property(Watched),{SEP}, watched]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Total),, films]</value>
		<value condition="!String.IsEmpty(ListItem.Year) + Integer.IsGreater(ListItem.Duration(mins),0)">$INFO[ListItem.Year]$INFO[ListItem.Duration(mins),{SEP}, min]$INFO[ListItem.Rating,{SEP},]$INFO[ListItem.Genre,{SEP},]</value>
		<value condition="!String.IsEmpty(ListItem.Year)">$INFO[ListItem.Year]$INFO[ListItem.Genre,{SEP},]</value>
		<value>$INFO[ListItem.Label2]</value>
	</variable>
	<variable name="Rows_Seasons">
		<value condition="Integer.IsEqual(ListItem.Property(TotalSeasons),1)">1 season</value>
		<value>$INFO[ListItem.Property(TotalSeasons),, seasons]</value>
	</variable>
	<variable name="Rows_State">
		<value condition="ListItem.IsResumable">$INFO[ListItem.PercentPlayed,,%]</value>
		<value condition="[String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,musicvideo)] + Integer.IsGreater(ListItem.PlayCount,0)">Seen</value>
	</variable>
	<variable name="Tracks_Cover">
		<value condition="!String.IsEmpty(Container(509).ListItem.Art(thumb))">$INFO[Container(509).ListItem.Art(thumb)]</value>
		<value>$INFO[Container(509).ListItem.Art(album.thumb)]</value>
	</variable>"""


# --------------------------------------------------------------------------------- pieces
def art(t, art, tint, dots, aspect="scale", title="$INFO[ListItem.Label]", font="an_40"):
    return (f'{t}<include content="DT_Artwork">\n{t}\t<param name="art" value="{art}"/>\n'
            f'{t}\t<param name="tint" value="{tint}"/>\n{t}\t<param name="dots" value="{dots}"/>\n'
            f'{t}\t<param name="aspect" value="{aspect}"/>\n{t}\t<param name="title" value="{title}"/>\n'
            f'{t}\t<param name="titlefont" value="{font}"/>\n{t}</include>')


def label(t, left, top, width, height, font, color, text, align=None, aligny=None, visible=None, ctl_id=None):
    rows = [f'<control type="label"{f" id={chr(34)}{ctl_id}{chr(34)}" if ctl_id else ""}>', f"\t<left>{left}</left>",
            f"\t<top>{top}</top>", f"\t<width>{width}</width>", f"\t<height>{height}</height>"]
    if align:
        rows.append(f"\t<align>{align}</align>")
    if aligny:
        rows.append(f"\t<aligny>{aligny}</aligny>")
    rows += [f"\t<font>{font}</font>", f"\t<textcolor>{color}</textcolor>", f"\t<selectedcolor>{color}</selectedcolor>",
             f"\t<label>{text}</label>"]
    if visible:
        rows.append(f"\t<visible>{visible}</visible>")
    rows.append("</control>")
    return "\n".join(t + r for r in rows)


def ink(t, left, top, width, height, visible=None, color="$VAR[ink]"):
    v = f"\n{t}\t<visible>{visible}</visible>" if visible else ""
    return (f'{t}<control type="image">\n{t}\t<left>{left}</left>\n{t}\t<top>{top}</top>\n{t}\t<width>{width}</width>\n'
            f'{t}\t<height>{height}</height>\n{t}\t<texture colordiffuse="{color}">common/white.png</texture>{v}\n{t}</control>')


def print_pair(t, vid, w, h, art_value, aspect="scale", visible=None, title="$INFO[ListItem.Label]", font="an_40"):
    """Focused-layout art: the print while the view hasn't focus, full colour + frame while it has."""
    v = f" + [{visible}]" if visible else ""
    return f"""{t}<control type="group">
{t}	<visible>!Control.HasFocus({vid}){v}</visible>
{art(t + chr(9), art_value, "$VAR[SectionTint]", "true", aspect, title, font)}
{t}</control>
{t}<control type="group">
{t}	<visible>Control.HasFocus({vid}){v}</visible>
{art(t + chr(9), art_value, "white", "false", aspect, title, font)}
{t}</control>"""


def view_group(vid, body, extra=""):
    return f"""		<control type="group">
			<visible>Control.IsVisible({vid})</visible>
			<include>Anim_FadeVisible</include>{extra}
{body}
		</control>"""


def empty_slide(dy):
    """With nothing but ".." the shared empty message sits at the top of the page: move the view below it."""
    return (f'\n\t\t\t<animation effect="slide" start="0,0" end="0,{dy}" time="0" condition="{EMPTY}">Conditional</animation>')


# --------------------------------------------------------------------------------- 505 Poster
def numeral(t, left, top, lab, val):
    return (label(t, left, top, 300, 24, "cap_20", "$VAR[SectionText]", lab) + "\n" +
            label(t, left, top + 21, 330, 136, "an_136", "$VAR[SectionText]", val, aligny="center"))


def view505():
    t = "\t\t\t"
    left_col = f"""			<!-- left column: kicker, fitted Anton title, numerals between 8 px rules, plot (hidden with nothing but "..") -->
			<control type="group">
				<visible>!Integer.IsEqual(Container.NumItems,0)</visible>
{label(t + chr(9), "page_margin", 176, 1096, 24, "cap_20", "$VAR[SectionText]", "$VAR[View_PosterKicker]")}
				<include content="Title_Poster"><param name="left" value="58"/><param name="top" value="236"/></include>
				<control type="group">
					<visible>!ListItem.IsParentFolder</visible>
					<include content="DT_RuleThick"><param name="top" value="500"/><param name="width" value="1096"/></include>
{numeral(t + chr(9) * 2, 64, 528, "$VAR[VidView_N1L]", "$VAR[VidView_N1V]")}
					<include content="DT_RuleV"><param name="left" value="400"/><param name="top" value="528"/><param name="height" value="160"/></include>
{numeral(t + chr(9) * 2, 432, 528, "$VAR[VidView_N2L]", "$VAR[VidView_N2V]")}
					<include content="DT_RuleV"><param name="left" value="768"/><param name="top" value="528"/><param name="height" value="160"/></include>
{numeral(t + chr(9) * 2, 800, 528, "$VAR[VidView_N3L]", "$VAR[VidView_N3V]")}
					<include content="DT_RuleThick"><param name="top" value="712"/><param name="width" value="1096"/></include>
				</control>
				<control type="textbox">
					<left>page_margin</left>
					<top>740</top>
					<width>1096</width>
					<height>238</height>
					<font>body_24</font>
					<textcolor>$VAR[SectionText]</textcolor>
					<label>$VAR[View_PosterPlot]</label>
					<autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>
				</control>
				<!-- pager tab (Home spotlight pattern): an ink tab at the end of the column, under the plot -->
				<control type="group">
					<left>920</left>
					<top>992</top>
					<width>240</width>
					<height>48</height>
					<visible>Integer.IsGreater(Container.NumItems,1)</visible>
{ink(chr(9) * 5, 0, 0, 240, 48)}
{label(chr(9) * 5, 0, 0, 240, 48, "cap_20", "$VAR[paper]", "$VAR[VidView_PosPad]$INFO[Container.CurrentItem] / $INFO[Container.NumItems]", align="center", aligny="center")}
{label(chr(9) * 5, 14, 0, 30, 48, "bold_28", "$VAR[SectionColor]", "‹", aligny="center", visible="Control.HasFocus(505)")}
{label(chr(9) * 5, 196, 0, 30, 48, "bold_28", "$VAR[SectionColor]", "›", align="right", aligny="center", visible="Control.HasFocus(505)")}
				</control>
			</control>"""
    poster = f"""			<!-- the print: 576 x 864, full colour + 8 px frame while the view has focus -->
			<control type="group">
				<left>1280</left>
				<top>176</top>
				<width>576</width>
				<height>864</height>
				<control type="group">
					<visible>!ListItem.IsParentFolder</visible>
{print_pair(chr(9) * 5, 505, 576, 864, "$VAR[VidView_PosterArt]")}
					<include>VidView_WallMarkers</include>
				</control>
				<include>VidView_WallParent</include>
				<include content="DT_FocusFrame"><param name="visible" value="Control.HasFocus(505)"/></include>
			</control>"""
    driver = f"""			<!-- the driver: an invisible horizontal list (Left / Right flip the item; past either end = Library panel) -->
			<control type="list" id="505">
				<left>0</left>
				<top>0</top>
				<width>8</width>
				<height>4</height>
				<orientation>horizontal</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime>0</scrolltime>
				<viewtype label="Poster">bigwrap</viewtype>
				<visible>{V}</visible>
				<itemlayout width="4" height="4"/>
				<focusedlayout width="4" height="4"/>
			</control>"""
    return f"""	<!-- ============================================================== 505 Poster -->
	<include name="VidView_505_Poster">
{view_group(505, driver + chr(10) + left_col + chr(10) + poster)}
	</include>"""


# --------------------------------------------------------------------------------- 506 Screens
def screen_cell(focused):
    t = "\t\t\t\t\t\t"
    wide, small = "$EXP[View_ScreenHasWide]", "!$EXP[View_ScreenHasWide]"
    if focused:
        prints = (print_pair(t, 506, 576, 324, "$VAR[View_ScreenWide]", visible=wide, title="$VAR[View_ScreenTitle]") + "\n" +
                  print_pair(t, 506, 576, 324, "$VAR[View_ScreenSmall]", "keep", visible=small, title="$VAR[View_ScreenTitle]"))
    else:
        prints = (f"{t}<control type=\"group\">\n{t}\t<visible>{wide}</visible>\n"
                  f"{art(t + chr(9), '$VAR[View_ScreenWide]', '$VAR[SectionTint]', 'true', title='$VAR[View_ScreenTitle]')}\n{t}</control>\n"
                  f"{t}<control type=\"group\">\n{t}\t<visible>{small}</visible>\n"
                  f"{art(t + chr(9), '$VAR[View_ScreenSmall]', '$VAR[SectionTint]', 'true', 'keep', title='$VAR[View_ScreenTitle]')}\n{t}</control>")
    frame = ('\n\t\t\t\t\t\t<include content="DT_FocusFrame"><param name="visible" value="Control.HasFocus(506)"/></include>'
             if focused else "")
    zoom = "\n\t\t\t\t\t\t<include>Anim_FocusZoom</include>" if focused else ""
    return f"""					<control type="group">
						<left>24</left>
						<top>24</top>
						<width>576</width>
						<height>324</height>{zoom}
						<control type="group">
							<visible>!ListItem.IsParentFolder</visible>
{prints.replace(chr(10) + t, chr(10) + t + chr(9)).replace(t + "<control", t + chr(9) + "<control", 1)}
							<include>DT_WatchedMarkers</include>
						</control>
						<include>VidView_WallParent</include>{frame}
					</control>
{label(chr(9) * 5, 24, 362, 576, 44, "an_32", "$VAR[SectionText]", "$VAR[View_ScreenTitle]", aligny="center", visible="$EXP[View_ScreenHasArt]")}"""


def view506():
    body = f"""			<control type="panel" id="506">
				<left>40</left>
				<top>152</top>
				<width>1824</width>
				<height>840</height>
				<orientation>vertical</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<preloaditems>1</preloaditems>
				<viewtype label="Screens">wide</viewtype>
				<visible>{V}</visible>
				<itemlayout width="608" height="420">
{screen_cell(False)}
				</itemlayout>
				<focusedlayout width="608" height="420">
{screen_cell(True)}
				</focusedlayout>
			</control>"""
    return f"""	<!-- ============================================================== 506 Screens -->
	<include name="VidView_506_Screens">
{view_group(506, body, empty_slide(96))}
	</include>"""


# --------------------------------------------------------------------------------- 507 Sheet
def sheet_cell(focused):
    t = "\t\t\t\t\t\t\t"
    if focused:
        prints = print_pair(t, 507, 156, 234, "$VAR[VidView_PosterArt]", font="an_32")
    else:
        prints = art(t, "$VAR[VidView_PosterArt]", "$VAR[SectionTint]", "true", font="an_32")
    return f"""					<control type="group">
						<left>16</left>
						<top>16</top>
						<width>156</width>
						<height>234</height>{chr(10) + chr(9) * 6 + "<include>Anim_FocusZoom</include>" if focused else ""}
						<control type="group">
							<visible>!ListItem.IsParentFolder</visible>
{prints}
							<include>VidView_WallMarkers</include>
						</control>
						<include>VidView_WallParent</include>{chr(10) + chr(9) * 6 + '<include content="DT_FocusFrame"><param name="visible" value="Control.HasFocus(507)"/></include>' if focused else ""}
					</control>"""


def view507():
    t = "\t\t\t"
    body = f"""			<control type="panel" id="507">
				<left>48</left>
				<top>160</top>
				<width>1800</width>
				<height>798</height>
				<orientation>vertical</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<preloaditems>1</preloaditems>
				<viewtype label="Sheet">bigwide</viewtype>
				<visible>{V} + {POSTER_KINDS}</visible>
				<itemlayout width="180" height="266">
{sheet_cell(False)}
				</itemlayout>
				<focusedlayout width="180" height="266">
{sheet_cell(True)}
				</focusedlayout>
			</control>
			<!-- caption band: the focused print's title on an ink block, its numbers in the section colour -->
			<control type="group">
				<visible>!$EXP[VidView_SheetEmpty]</visible>
{ink(t + chr(9), "page_margin", 976, 1792, 64)}
{label(t + chr(9), 88, 976, 1300, 64, "an_40", "$VAR[paper]", "$VAR[View_SheetTitle]", aligny="center")}
{label(t + chr(9), 1376, 976, 456, 64, "cap_20", "$VAR[SectionColor]", "$VAR[View_SheetMeta]", align="right", aligny="center")}
			</control>"""
    return f"""	<!-- ============================================================== 507 Sheet -->
	<expression name="VidView_SheetEmpty">{EMPTY}</expression>
	<include name="VidView_507_Sheet">
{view_group(507, body, empty_slide(96))}
	</include>"""


# --------------------------------------------------------------------------------- 508 Stage
def stage_cell(focused):
    t = "\t\t\t\t\t\t\t"
    if focused:
        prints = print_pair(t, 508, 192, 192, "$INFO[ListItem.Art(thumb)]", title="$VAR[Stage_CellTitle]", font="an_32")
    else:
        prints = art(t, "$INFO[ListItem.Art(thumb)]", "$VAR[SectionTint]", "true", title="$VAR[Stage_CellTitle]", font="an_32")
    return f"""					<control type="group">
						<left>24</left>
						<top>24</top>
						<width>192</width>
						<height>192</height>{chr(10) + chr(9) * 6 + "<include>Anim_FocusZoom</include>" if focused else ""}
						<control type="group">
							<visible>!ListItem.IsParentFolder</visible>
{prints}
						</control>
						<include>VidView_WallParent</include>{chr(10) + chr(9) * 6 + '<include content="DT_FocusFrame"><param name="visible" value="Control.HasFocus(508)"/></include>' if focused else ""}
					</control>"""


def view508():
    t = "\t\t\t"
    band = f"""			<!-- the fanart as a full-width print band (full colour while the strip has focus); none = the ink slab -->
			<control type="group">
				<left>0</left>
				<top>144</top>
				<width>1920</width>
				<height>512</height>
				<visible>!Integer.IsEqual(Container.NumItems,0)</visible>
{ink(t + chr(9), 0, 0, 1920, 512)}
				<control type="group">
					<visible>$EXP[Stage_HasFanart] + !Container(508).ListItem.IsParentFolder</visible>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>1920</width>
						<height>512</height>
						<aspectratio aligny="top">scale</aspectratio>
						<fadetime>200</fadetime>
						<texture background="true" colordiffuse="$VAR[SectionTint]">$VAR[Stage_Fanart]</texture>
						<visible>!Control.HasFocus(508)</visible>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>1920</width>
						<height>512</height>
						<aspectratio aligny="top">scale</aspectratio>
						<fadetime>200</fadetime>
						<texture background="true">$VAR[Stage_Fanart]</texture>
						<visible>Control.HasFocus(508)</visible>
					</control>
					<include content="DT_PrintGhost"><param name="visible" value="!Control.HasFocus(508)"/></include>
					<include content="DT_PrintVeil"><param name="visible" value="!Control.HasFocus(508)"/></include>
					<include content="DT_ArtDots"><param name="visible" value="!Control.HasFocus(508)"/></include>
				</control>
				<!-- no fanart: the artist photo / album cover as a square print at the right of the ink slab -->
				<control type="group">
					<left>1344</left>
					<top>0</top>
					<width>512</width>
					<height>512</height>
					<visible>!$EXP[Stage_HasFanart] + !Container(508).ListItem.IsParentFolder + !String.IsEmpty(Container(508).ListItem.Art(thumb))</visible>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>512</width>
						<height>512</height>
						<aspectratio>scale</aspectratio>
						<fadetime>200</fadetime>
						<texture background="true" colordiffuse="$VAR[Stage_ThumbTint]">$INFO[Container(508).ListItem.Art(thumb)]</texture>
					</control>
					<include content="DT_PrintGhost"><param name="visible" value="!Control.HasFocus(508)"/></include>
					<include content="DT_PrintVeil"><param name="visible" value="!Control.HasFocus(508)"/></include>
					<include content="DT_ArtDots"><param name="visible" value="!Control.HasFocus(508)"/></include>
				</control>
				<!-- the name block: ink, Anton name in paper, kicker in the section colour -->
{ink(t + chr(9), 0, 312, 1152, 200)}
{label(t + chr(9), "page_margin", 330, 1040, 24, "cap_20", "$VAR[SectionColor]", "$VAR[Stage_Kicker]")}
				<include content="Title_Stage"><param name="left" value="58"/><param name="top" value="364"/></include>
			</control>
			<include content="DT_RuleThick"><param name="top" value="656"/><param name="left" value="0"/><param name="width" value="1920"/></include>"""
    strip = f"""			<control type="list" id="508">
				<left>40</left>
				<top>664</top>
				<width>1792</width>
				<height>240</height>
				<orientation>horizontal</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<preloaditems>1</preloaditems>
				<viewtype label="Stage">biglist</viewtype>
				<visible>{M} + [Container.Content(albums) | Container.Content(artists) | Container.Content(songs)]</visible>
				<itemlayout width="224" height="240">
{stage_cell(False)}
				</itemlayout>
				<focusedlayout width="224" height="240">
{stage_cell(True)}
				</focusedlayout>
			</control>
{label(t, "page_margin", 904, 1792, 24, "cap_20", "$VAR[SectionText]", "$VAR[Stage_Meta]")}"""
    return f"""	<!-- ============================================================== 508 Stage (music) -->
	<include name="Music_View_508">
{view_group(508, band + chr(10) + strip)}
	</include>"""


# --------------------------------------------------------------------------------- 510 Rows
ROWS_KINDS = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
              "Container.Content(musicvideos)]")


def rows_row(focused):
    """One 160 px row: the 256 x 144 print at 16,8, text from x 304 (1472 wide).
    focused=True draws the ink bar version (paper text, print in full colour)."""
    t = "\t\t\t\t\t\t"
    on = focused
    txt_c = "$VAR[paper]" if on else "$VAR[SectionText]"
    sub_c = "$VAR[SectionColor]" if on else "$VAR[SectionText]"
    plot_c = "$VAR[paper_80]" if on else "$VAR[SectionText2]"
    wide, small = "$EXP[View_ScreenHasWide]", "!$EXP[View_ScreenHasWide]"
    tint = "white" if on else "$VAR[SectionTint]"
    dots = "false" if on else "true"
    rows = []
    if not on:
        rows.append(ink(t, 0, 158, 1792, 2, color="$VAR[SectionText3]"))
    rows.append(f"""{t}<control type="group">
{t}	<left>16</left>
{t}	<top>8</top>
{t}	<width>256</width>
{t}	<height>144</height>
{t}	<control type="group">
{t}		<visible>!ListItem.IsParentFolder</visible>
{t}		<control type="group">
{t}			<visible>{wide}</visible>
{art(t + chr(9) * 3, "$VAR[View_ScreenWide]", tint, dots, title="", font="an_32")}
{t}		</control>
{t}		<control type="group">
{t}			<visible>{small}</visible>
{art(t + chr(9) * 3, "$VAR[View_ScreenSmall]", tint, dots, "keep", title="", font="an_32")}
{t}		</control>
{t}		<include>DT_WatchedMarkers</include>
{t}	</control>
{t}	<include>VidView_WallParent</include>
{t}</control>""")
    rows += [label(t, 304, 8, 1300, 52, "an_40", txt_c, "$VAR[Rows_Title]", aligny="center"),
             label(t, 1620, 22, 156, 24, "cap_20", sub_c, "$VAR[Rows_State]", align="right"),
             label(t, 304, 62, 1472, 24, "cap_20", sub_c, "$VAR[Rows_Meta]")]
    rows.append(f"""{t}<control type="textbox">
{t}	<left>304</left>
{t}	<top>88</top>
{t}	<width>1400</width>
{t}	<height>68</height>  <!-- 2 x 34 (Inter Tight 24 x 1.171) -->
{t}	<font>body_24</font>
{t}	<textcolor>{plot_c}</textcolor>
{t}	<label>$INFO[ListItem.Plot]</label>
{t}	<visible>!ListItem.IsParentFolder</visible>
{t}</control>""")
    return "\n".join(rows)


def view510():
    body = f"""			<control type="list" id="510">
				<left>page_margin</left>
				<top>168</top>
				<width>1792</width>
				<height>800</height>
				<orientation>vertical</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<preloaditems>1</preloaditems>
				<viewtype label="Rows">biglist</viewtype>
				<visible>{V} + {ROWS_KINDS}</visible>
				<itemlayout width="1792" height="160">
					<control type="group">
{rows_row(False)}
					</control>
				</itemlayout>
				<focusedlayout width="1792" height="160">
					<control type="group">
						<visible>!Control.HasFocus(510)</visible>
{rows_row(False)}
					</control>
					<control type="group">
						<visible>Control.HasFocus(510)</visible>
{ink(chr(9) * 6, 0, 0, 1792, 160)}
{rows_row(True)}
					</control>
				</focusedlayout>
			</control>"""
    return f"""	<!-- ============================================================== 510 Rows (0.9.18) -->
	<include name="VidView_510_Rows">
{view_group(510, body, empty_slide(120))}
	</include>"""


# --------------------------------------------------------------------------------- 509 Tracks
def track_row(focused):
    t = "\t\t\t\t\t"
    on = focused
    num_c = "$VAR[SectionColor]" if on else "$VAR[SectionText]"
    txt_c = "$VAR[paper]" if on else "$VAR[SectionText]"
    sub_c = "$VAR[paper_80]" if on else "$VAR[SectionText2]"
    rows = []
    if not on:
        rows.append(ink(t, 0, 70, 1160, 2, color="$VAR[SectionText3]"))
    rows += [label(t, 16, 0, 80, 72, "an_40", num_c, "$VAR[Tracks_Num]", aligny="center"),
             label(t, 112, 0, 640, 72, "bold_26", txt_c, "$VAR[Tracks_Title]", aligny="center"),
             label(t, 772, 0, 292, 72, "cap_20", sub_c, "$VAR[Tracks_Where]", aligny="center"),
             label(t, 1064, 0, 80, 72, "cap_20", txt_c, "$INFO[ListItem.Duration]", align="right", aligny="center")]
    return "\n".join(rows)


def view509():
    t = "\t\t\t"
    body = f"""			<control type="list" id="509">
				<left>page_margin</left>
				<top>176</top>
				<width>1160</width>
				<height>864</height>
				<orientation>vertical</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<viewtype label="Tracks">bigwide</viewtype>
				<visible>{M} + Container.Content(songs)</visible>
				<itemlayout width="1160" height="72">
{track_row(False)}
				</itemlayout>
				<focusedlayout width="1160" height="72">
					<control type="group">
						<visible>!Control.HasFocus(509)</visible>
{track_row(False).replace(chr(10) + chr(9) * 5, chr(10) + chr(9) * 6).replace(chr(9) * 5 + "<control", chr(9) * 6 + "<control", 1)}
					</control>
					<control type="group">
						<visible>Control.HasFocus(509)</visible>
{ink(chr(9) * 6, 0, 0, 1160, 72)}
{track_row(True).replace(chr(10) + chr(9) * 5, chr(10) + chr(9) * 6).replace(chr(9) * 5 + "<control", chr(9) * 6 + "<control", 1)}
					</control>
				</focusedlayout>
			</control>
			<include content="DT_RuleV"><param name="left" value="1248"/><param name="top" value="176"/><param name="height" value="864"/></include>
			<!-- the focused song's cover as a print (full colour while the list has focus), album and year -->
			<control type="group">
				<left>1288</left>
				<top>176</top>
				<width>568</width>
				<height>568</height>
				<visible>!Container(509).ListItem.IsParentFolder</visible>
{art(t + chr(9), "$VAR[Tracks_Cover]", "$VAR[SectionTint]", "!Control.HasFocus(509)", title="$INFO[Container(509).ListItem.Album]").replace('value="$VAR[SectionTint]"', 'value="$VAR[Tracks_CoverTint]"')}
				<include content="DT_FocusFrame"><param name="visible" value="Control.HasFocus(509)"/></include>
			</control>
{label(t, 1288, 772, 568, 24, "cap_20", "$VAR[SectionText]", "$INFO[Container(509).ListItem.Artist]", visible="!Container(509).ListItem.IsParentFolder")}
{label(t, 1288, 800, 568, 64, "an_48", "$VAR[SectionText]", "$INFO[Container(509).ListItem.Album]", aligny="center", visible="!Container(509).ListItem.IsParentFolder")}
{label(t, 1288, 872, 568, 24, "cap_20", "$VAR[SectionText2]", "$INFO[Container(509).ListItem.Year]$INFO[Container(509).ListItem.Genre,  ·  ,]", visible="!Container(509).ListItem.IsParentFolder")}"""
    return f"""	<!-- ============================================================== 509 Tracks (music) -->
	<variable name="Stage_ThumbTint">
		<value condition="Control.HasFocus(508)">white</value>
		<value>$VAR[SectionTint]</value>
	</variable>
	<variable name="Tracks_CoverTint">
		<value condition="Control.HasFocus(509)">white</value>
		<value>$VAR[SectionTint]</value>
	</variable>
	<include name="Music_View_509">
{view_group(509, body, empty_slide(120))}
	</include>"""


def main():
    text = "\n".join(['<?xml version="1.0" encoding="UTF-8"?>',
                      "<!-- GENERATED by _src/make_views_more.py - edit the generator, not this file. -->",
                      "<includes>", VARIABLES, view505(), view506(), view507(), view508(), view509(), view510(), "</includes>", ""])
    text = "\n".join(l for l in text.split("\n") if l.strip() != "")
    OUT.write_text(finish_xml(strip_defaults(text + "\n", ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
