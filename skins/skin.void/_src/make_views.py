"""Generate skins/skin.void/1080i/Includes_ViewsMore.xml: the 0.9.14 library views and the view picker's items.

Run:  python skins/skin.void/_src/make_views.py      (then make_view_previews.py for the picker previews)

docs/VIEWS_BRIEF_2026-10-27.md. Void's own views (Includes_Views.xml, hand-written) stay as they are:
  50 Index   rotary text index (every window)
  51 Wall    sparse poster wall (movies, sets, shows, seasons, music videos)
  52 Covers  sparse square wall (albums, artists, songs)
New here, all in Void's language (true black, grey -> white + scale is the only focus, serif titles on the x 160 axis,
information that arrives the longer you rest):
  53 One     the Home card for the library: one item in large serif, neighbours above / below at 28 %, meta after
             1 s, plot after 3 s, the fanart rises behind it after 8 s (videos: every content; music: albums, artists)
  54 Frames  3 x 2 wall of 16:9 frames (landscape / still / fanart; posters and icons sit whole on a quiet tile; a
             serif title when there is no art): series, episodes, sets, add-ons and plug-ins that only have thumbs
  55 Notes   a plain text list on the left, a reading column on the right (title, meta, ten lines of plot, credits)
  56 Stills  episodes: a still per row, its number, title and two lines of plot; since 0.9.17 also films, series,
             sets, seasons and music videos (their landscape / fanart; a poster sits whole on the tile)
  57 Tracks  songs: number, title, artist / album, time, as a tracklist
viewtypes: list (50) and Kodi's panel default (51 / 52, = icon) keep the defaults; the new views use types no Kodi
default asks for (bigwrap / wide / biglist / biginfo / bigwide; not info: CAutoSwitch picks info for folders with metadata), so a folder without a saved view still opens in Index.
The view picker (Custom_1161) gets its items and its "open on the current view" onloads from here.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_ViewsMore.xml"

SEP = "[COLOR sep_light]  ·  [/COLOR]"

# ---------------------------------------------------------------- views, labels and where they are offered
VID = "Window.IsActive(videos)"
MUS = "Window.IsActive(music)"
POSTER_KINDS = "[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(musicvideos)]"
VIEWS = [  # id, string id, preview, condition in the picker (None = always)
    (50, 31217, "index", None),
    (51, 31218, "wall", f"{VID} + {POSTER_KINDS}"),
    (52, 31219, "covers", f"{MUS} + [Container.Content(albums) | Container.Content(artists) | Container.Content(songs)]"),
    (53, 31350, "one", f"{VID} | [{MUS} + [Container.Content(albums) | Container.Content(artists)]]"),
    (54, 31351, "frames", VID),
    (55, 31352, "notes", VID),
    (56, 31353, "stills", f"{VID} + [{POSTER_KINDS[1:-1]} | Container.Content(episodes)]"),
    (57, 31354, "tracks", f"{MUS} + Container.Content(songs)"),
]
# content cases the picker can open on: (condition, views visible in this case, in picker order)
CASES = [
    (f"{VID} + {POSTER_KINDS}", [50, 51, 53, 54, 55, 56]),
    (f"{VID} + Container.Content(episodes)", [50, 53, 54, 55, 56]),
    (f"{VID} + !{POSTER_KINDS} + !Container.Content(episodes)", [50, 53, 54, 55]),
    (f"{MUS} + [Container.Content(albums) | Container.Content(artists)]", [50, 52, 53]),
    (f"{MUS} + Container.Content(songs)", [50, 52, 57]),
]


def cur(sid):
    return f"String.IsEqual(Container.Viewmode,$LOCALIZE[{sid}])"


# ---------------------------------------------------------------- per-container variables
def li(c, x):
    return f"Container({c}).ListItem.{x}" if c else f"ListItem.{x}"


def dbt(c, t):
    return f"String.IsEqual({li(c, 'DBType')},{t})"


def runtime_vars(c, name):
    d = lambda u: li(c, f"Duration({u})")
    return f"""	<variable name="{name}_Runtime">
		<value condition="Integer.IsGreater({d('h')},0) + Integer.IsGreater({d('m')},0)">$INFO[{d('h')},, h ]$INFO[{d('m')},, min]</value>
		<value condition="Integer.IsGreater({d('h')},0)">$INFO[{d('h')},, h]</value>
		<value condition="Integer.IsGreater({d('m')},0)">$INFO[{d('m')},, min]</value>
	</variable>
	<variable name="{name}_RuntimePart">
		<value condition="Integer.IsGreater({d('h')},0) | Integer.IsGreater({d('m')},0)">{SEP}$VAR[{name}_Runtime]</value>
	</variable>
	<variable name="{name}_Rating">
		<value condition="!String.IsEmpty({li(c, 'Rating')}) + !String.IsEqual({li(c, 'Rating')},0.0)">{SEP}[COLOR value]$INFO[{li(c, 'Rating')}][/COLOR]</value>
	</variable>"""


def item_vars(c, name, parent_meta=""):
    """Kicker / title / meta / plot / credits / state for one container (c = id) or the drawn item (c = None)."""
    L = lambda x: li(c, x)
    I = lambda x, pre="", post="": f"$INFO[{L(x)},{pre},{post}]" if (pre or post) else f"$INFO[{L(x)}]"
    out = [runtime_vars(c, name)]
    out.append(f"""	<variable name="{name}_Kicker">
		<value condition="{L('IsParentFolder')}"></value>
		<value condition="{dbt(c, 'episode')} + !String.IsEmpty({L('Season')}) + !String.IsEmpty({L('Episode')})">Season {I('Season')}{SEP}Episode {I('Episode')}</value>
		<value condition="{dbt(c, 'episode')}">{I('Episode', 'Episode ')}</value>
		<value condition="{dbt(c, 'season')}">{I('TVShowTitle')}</value>
		<value condition="{dbt(c, 'album')} | {dbt(c, 'song')} | {dbt(c, 'musicvideo')}">{I('Artist')}</value>
		<value condition="{dbt(c, 'artist')}">{I('Genre')}</value>
		<value>{I('Year')}</value>
	</variable>
	<variable name="{name}_Title">
		<value condition="{L('IsParentFolder')}">Back</value>
		<value condition="{dbt(c, 'episode')} + !String.IsEmpty({L('Title')})">{I('Title')}</value>
		<value>{I('Label')}</value>
	</variable>
	<variable name="{name}_Meta">
		<value condition="{L('IsParentFolder')}">{parent_meta}</value>
		<value condition="{dbt(c, 'movie')} + [Integer.IsGreater({L('Duration(h)')},0) | Integer.IsGreater({L('Duration(m)')},0)]">$VAR[{name}_Runtime]$VAR[{name}_Rating]{I('Genre', SEP)}</value>
		<value condition="{dbt(c, 'movie')} + !String.IsEmpty({L('Rating')}) + !String.IsEqual({L('Rating')},0.0)">[COLOR value]{I('Rating')}[/COLOR]{I('Genre', SEP)}</value>
		<value condition="{dbt(c, 'movie')}">{I('Genre')}</value>
		<value condition="{dbt(c, 'tvshow')}">$VAR[{name}_Seasons]$VAR[{name}_Rating]{I('Genre', SEP)}</value>
		<value condition="{dbt(c, 'season')}">$VAR[{name}_Episodes]{I('Property(UnWatchedEpisodes)', SEP, ' to watch')}</value>
		<value condition="{dbt(c, 'episode')}">$VAR[{name}_Runtime]$VAR[{name}_Rating]{I('Premiered', SEP + 'aired ')}</value>
		<value condition="{dbt(c, 'set')}">$VAR[{name}_Films]{I('Property(Watched)', SEP, ' watched')}</value>
		<value condition="{dbt(c, 'musicvideo')}">{I('Year')}$VAR[{name}_RuntimePart]{I('Genre', SEP)}</value>
		<value condition="{dbt(c, 'album')}">{I('Year')}{I('Genre', SEP)}</value>
		<value condition="{dbt(c, 'song')}">{I('Album')}{I('Duration', SEP)}</value>
		<value condition="{dbt(c, 'artist')}"></value>
		<value>{I('Label2')}</value>
	</variable>
	<variable name="{name}_Plot">
		<value condition="{L('IsParentFolder')}"></value>
		<value condition="{dbt(c, 'artist')}">{I('Property(Artist_Description)')}</value>
		<value condition="{dbt(c, 'album')}">{I('Property(Album_Description)')}</value>
		<value condition="!String.IsEmpty({L('Plot')})">{I('Plot')}</value>
		<value>{I('PlotOutline')}</value>
	</variable>
	<variable name="{name}_Seasons">
		<value condition="Integer.IsEqual({L('Property(TotalSeasons)')},1)">1 season</value>
		<value>{I('Property(TotalSeasons)', '', ' seasons')}</value>
	</variable>
	<variable name="{name}_Episodes">
		<value condition="Integer.IsEqual({L('Property(TotalEpisodes)')},1)">1 episode</value>
		<value>{I('Property(TotalEpisodes)', '', ' episodes')}</value>
	</variable>
	<variable name="{name}_Films">
		<value condition="Integer.IsEqual({L('Property(Total)')},1)">1 film</value>
		<value>{I('Property(Total)', '', ' films')}</value>
	</variable>
	<expression name="{name}_HasPlot">!{L('IsParentFolder')} + [!String.IsEmpty({L('Plot')}) | !String.IsEmpty({L('PlotOutline')}) | [{dbt(c, 'artist')} + !String.IsEmpty({L('Property(Artist_Description)')})] | [{dbt(c, 'album')} + !String.IsEmpty({L('Property(Album_Description)')})]]</expression>
	<variable name="{name}_State">
		<value condition="{L('IsResumable')}">Resume at {I('PercentPlayed')}%</value>
		<value condition="[{dbt(c, 'movie')} | {dbt(c, 'episode')}] + Integer.IsGreater({L('PlayCount')},0)">Watched</value>
		<value condition="{dbt(c, 'movie')} | {dbt(c, 'episode')}">Unwatched</value>
	</variable>
	<variable name="{name}_Credits">
		<value condition="!String.IsEmpty({L('Director')})">{I('Director', 'Directed by ')}{I('Studio', SEP)}</value>
		<value condition="!String.IsEmpty({L('Studio')})">{I('Studio')}</value>
		<value condition="{dbt(c, 'artist')} | {dbt(c, 'album')}">{I('Property(Artist_Style)')}</value>
	</variable>""")
    return "\n".join(out)


def ambient_art_var(c, name):
    L = lambda x: li(c, x)
    return f"""	<variable name="{name}_Art">
		<value condition="!String.IsEmpty({L('Art(fanart)')})">$INFO[{L('Art(fanart)')}]</value>
		<value condition="!String.IsEmpty({L('Art(tvshow.fanart)')})">$INFO[{L('Art(tvshow.fanart)')}]</value>
		<value condition="!String.IsEmpty({L('Art(artist.fanart)')})">$INFO[{L('Art(artist.fanart)')}]</value>
		<value>$INFO[{L('Art(landscape)')}]</value>
	</variable>"""


def has_ambient(c):
    return " | ".join(f"!String.IsEmpty({li(c, f'Art({a})')})" for a in ("fanart", "tvshow.fanart", "artist.fanart", "landscape"))


# drawn-item art for frames / stills (inside list layouts: bare ListItem)
FRAME_WIDE_HAS = ("[[String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)]"
                  " | !String.IsEmpty(ListItem.Art(landscape)) | !String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.fanart))]")
SMALL_HAS = ("[!String.IsEmpty(ListItem.Art(poster)) | !String.IsEmpty(ListItem.Art(tvshow.poster)) | !String.IsEmpty(ListItem.Art(thumb))"
             " | [!String.IsEmpty(ListItem.Art(icon)) + !String.StartsWith(ListItem.Art(icon),Default)]]")
STATIC_VARS = """	<variable name="Frame_Wide">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value>$INFO[ListItem.Art(tvshow.fanart)]</value>
	</variable>
	<variable name="Frame_Small">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value>$INFO[ListItem.Art(icon)]</value>
	</variable>
	<variable name="Still_Kicker">
		<value condition="ListItem.IsParentFolder">Up one level</value>
		<value condition="String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,musicvideo)">$INFO[ListItem.Year]$VAR[Still_RuntimePart]$VAR[Still_Seen]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow) + Integer.IsGreater(ListItem.Property(TotalSeasons),1)">$INFO[ListItem.Year]""" + SEP + """$INFO[ListItem.Property(TotalSeasons)] seasons$INFO[ListItem.Genre,""" + SEP + """,]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$INFO[ListItem.Genre,""" + SEP + """,]</value>
		<value condition="String.IsEqual(ListItem.DBType,season)">$INFO[ListItem.TVShowTitle]$VAR[PL_TotalEpisodes_Episode2]</value>
		<value condition="String.IsEqual(ListItem.DBType,set) + Integer.IsGreater(ListItem.Property(Watched),0)">$VAR[PL_Total_Film]$INFO[ListItem.Property(Watched),""" + SEP + """, watched]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$VAR[PL_Total_Film]</value>
		<value condition="!String.IsEmpty(ListItem.Season) + !String.IsEmpty(ListItem.Episode)">Season $INFO[ListItem.Season]""" + SEP + """Episode $INFO[ListItem.Episode]$VAR[Still_RuntimePart]$VAR[Still_Seen]</value>
		<value>$INFO[ListItem.Label2]$VAR[Still_Seen]</value>
	</variable>
	<variable name="Still_Title">
		<value condition="!""" + FRAME_WIDE_HAS + " + " + SMALL_HAS + """"></value>
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Episode,Episode ,]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Still_Seen">
		<value condition="ListItem.IsResumable">""" + SEP + """$INFO[ListItem.PercentPlayed]% seen</value>
		<value condition="Integer.IsGreater(ListItem.PlayCount,0)">""" + SEP + """watched</value>
	</variable>
	<variable name="View_RowTitle">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="[String.IsEqual(ListItem.DBType,episode) | String.IsEqual(ListItem.DBType,song)] + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Track_Number">
		<value condition="ListItem.IsParentFolder"></value>
		<value>$INFO[ListItem.TrackNumber]</value>
	</variable>
	<variable name="Track_Where">
		<value condition="!String.IsEmpty(ListItem.Artist) + !String.IsEmpty(ListItem.Album)">$INFO[ListItem.Artist]""" + SEP + """$INFO[ListItem.Album]</value>
		<value>$INFO[ListItem.Artist]$INFO[ListItem.Album]</value>
	</variable>"""


# ---------------------------------------------------------------- shared pieces
def view_group(vid, body, extra_visible=None):
    vis = f"Control.IsVisible({vid})"
    return f"""		<control type="group">
			<visible>{vis}</visible>
			<include>Anim_FadeVisible</include>
			<include content="Void_Anim_Recede"><param name="condition" value="$EXP[Lib_OptionsFocus]"/><param name="level" value="25"/></include>
{body}
		</control>"""


def list_nav(vid, t="\t\t\t\t"):
    first = f"Integer.IsLess(Container({vid}).CurrentItem,2)"  # item 1, or ".." (CurrentItem 0)
    last = f"Integer.IsEqual(Container({vid}).CurrentItem,Container({vid}).NumItems)"
    return (f"{t}<onup>SetFocus(9000)</onup>\n{t}<ondown>noop</ondown>\n"
            f"{t}<onleft condition=\"{first}\">SetFocus(9000)</onleft>\n"
            f"{t}<onleft condition=\"!{first} + $EXP[SortIsAlpha]\">Action(prevletter)</onleft>\n"
            f"{t}<onleft condition=\"!{first} + !$EXP[SortIsAlpha]\">Action(pageup)</onleft>\n"
            f"{t}<!-- Right on the last item (nowhere left to jump) = the Library panel -->\n"
            f"{t}<onright condition=\"{last}\">ActivateWindow(1160)</onright>\n"
            f"{t}<onright condition=\"!{last} + $EXP[SortIsAlpha]\">Action(nextletter)</onright>\n"
            f"{t}<onright condition=\"!{last} + !$EXP[SortIsAlpha]\">Action(pagedown)</onright>")


def count_label(t="\t\t\t"):
    return f"""{t}<include>Void_ViewCount</include>"""


def hint(vid, top=1000):
    return f"""			<include content="Void_Hint">
				<param name="label" value="$VAR[Lib_Hint]"/>
				<param name="top" value="{top}"/>
				<param name="visible" value="$EXP[Dwell2] + Control.HasFocus({vid})"/>
			</include>"""


def label(left, top, width, height, font, color, text, visible=None, t="\t\t\t\t", extra=""):
    v = f"\n{t}\t<visible>{visible}</visible>" if visible else ""
    return (f"{t}<control type=\"label\">\n{t}\t<left>{left}</left>\n{t}\t<top>{top}</top>\n{t}\t<width>{width}</width>\n"
            f"{t}\t<height>{height}</height>\n{t}\t<aligny>top</aligny>\n{t}\t<font>{font}</font>\n"
            f"{t}\t<textcolor>{color}</textcolor>\n{t}\t<selectedcolor>{color}</selectedcolor>\n{t}\t<label>{text}</label>{v}{extra}\n{t}</control>")


# ---------------------------------------------------------------- 53 One
def view53():
    C = 53
    recede = f"$EXP[One_AmbientDwell] + !Container({C}).Scrolling + [{has_ambient(C)}]"
    body = f"""			<!-- the driver: invisible fixedlist like the index; the card reads Container(53) -->
			<control type="fixedlist" id="{C}">
				<left>0</left>
				<top>0</top>
				<width>8</width>
				<height>60</height>
				<orientation>vertical</orientation>
				<focusposition>7</focusposition>
				<movement>0</movement>
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<viewtype label="31350">bigwrap</viewtype>
				<visible>{VIEWS[3][3]}</visible>
{list_nav(C)}
				<itemlayout height="4" width="8"/>
				<focusedlayout height="4" width="8"/>
			</control>
			<!-- the card: Home's display block (Includes_Home.xml shelf display), vertically centred -->
			<control type="grouplist">
				<left>0</left>
				<top>8</top>
				<width>1920</width>
				<height>1080</height>
				<orientation>vertical</orientation>
				<align>center</align>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<include content="Void_Anim_Roll"><param name="id" value="{C}"/></include>
				<visible>Integer.IsGreater(Container({C}).NumItems,0) | Container({C}).ListItem.IsParentFolder</visible>
				<!-- neighbour above (retracts with the plot) -->
				<control type="group">
					<width>1920</width>
					<height>126</height>
{label(160, 0, 1500, 53, "serif_48", "neighbour", f"$VAR[One_Prev]", "![$EXP[Dwell2] + $EXP[One_HasPlot]]", t=chr(9)*5, extra=chr(10) + chr(9)*6 + "<include>Void_Anim_Dwell</include>")}
				</control>
				<!-- kicker: year / season + episode / artist -->
				<control type="group">
					<width>1920</width>
					<height>40</height>
{label(164, 0, 1400, 24, "capsw_20", "grey", f"$VAR[One_Kicker]", t=chr(9)*5, extra=chr(10) + chr(9)*6 + f'<include content="Void_Anim_Recede"><param name="condition" value="{recede}"/><param name="level" value="85"/></include>')}
				</control>
				<!-- title fitted to the width (Includes_Titles.xml): 172 / 132 on one line, then 132 / 104 on two -->
				<include content="Title_Home_Visible">
					<param name="label" value="$VAR[One_Title]"/>
					<param name="recede" value="{recede}"/>
					<param name="p0" value="7531"/>
					<param name="p1" value="7532"/>
					<param name="p2" value="7533"/>
				</include>
				<include content="Title_Home_Layout">
					<param name="label" value="$VAR[One_Title]"/>
					<param name="p0" value="7531"/>
					<param name="p1" value="7532"/>
					<param name="p2" value="7533"/>
				</include>
				<!-- meta line (after 1 s) -->
				<control type="group">
					<width>1920</width>
					<height>87</height>
{label(160, 21, 1500, 32, "sans_26", "grey", "$VAR[One_Meta]", "$EXP[Dwell1]", t=chr(9)*5, extra=chr(10) + chr(9)*6 + "<include>Void_Anim_Dwell</include>")}
				</control>
				<!-- plot (after 3 s) shares the band with the neighbour below, which retracts -->
				<control type="group">
					<width>1920</width>
					<height>119</height>
					<control type="textbox">
						<left>160</left>
						<top>0</top>
						<width>820</width>
						<height>118</height>
						<font>sans_28</font>
						<textcolor>text_72</textcolor>
						<label>$VAR[One_Plot]</label>
						<visible>$EXP[Dwell2] + $EXP[One_HasPlot]</visible>
						<include>Void_Anim_Dwell</include>
					</control>
{label(160, 66, 1500, 53, "serif_48", "neighbour", "$VAR[One_Next]", "![$EXP[Dwell2] + $EXP[One_HasPlot]]", t=chr(9)*5, extra=chr(10) + chr(9)*6 + "<include>Void_Anim_Dwell</include>")}
				</control>
			</control>
{hint(C, 966)}
{count_label()}"""
    return f"""	<!-- ============================================================ 53: One -->
	<include name="Void_View53">
{view_group(C, body)}
	</include>
	<!-- One's ambient fanart: drawn by the window right after Void_Background (under the header), like Home -->
	<include name="Void_View53_Ambient">
		<control type="group">
			<visible>Control.IsVisible({C}) + !$EXP[Lib_OptionsFocus] + $EXP[One_AmbientDwell] + !Container({C}).Scrolling + !Container({C}).ListItem.IsParentFolder + [{has_ambient(C)}]</visible>
			<include>Void_Anim_AmbientRise</include>
			<control type="group">
				<include>Void_Anim_KenBurns</include>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>1920</width>
					<height>1080</height>
					<aspectratio>scale</aspectratio>
					<fadetime>400</fadetime>
					<texture background="true" colordiffuse="$VAR[AmbientLevel]">$VAR[One_Art]</texture>
				</control>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<texture colordiffuse="scrim">common/vignette_home.png</texture>
			</control>
		</control>
	</include>"""


# ---------------------------------------------------------------- 54 Frames
def view54():
    C = 54
    body = f"""			<control type="panel" id="{C}">
				<left>132</left>
				<top>158</top>
				<width>1656</width>
				<height>700</height>
				<orientation>vertical</orientation>
				<onup>SetFocus(9000)</onup>
				<ondown>noop</ondown>
				<onleft>ActivateWindow(1160)</onleft>  <!-- past the first / last column = Library panel, as on the wall -->
				<onright>ActivateWindow(1160)</onright>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">220</scrolltime>
				<viewtype label="31351">wide</viewtype>
				<visible>{VIEWS[4][3]}</visible>
				<itemlayout width="552" height="350">
					<include content="Void_FrameItem"><param name="color" value="art_35"/></include>
				</itemlayout>
				<focusedlayout width="552" height="350">
					<include content="Void_FrameItem"><param name="color" value="white"/><param name="focused" value="true"/></include>
				</focusedlayout>
			</control>
			<include content="Void_WallCaption"><param name="id" value="{C}"/></include>"""
    return f"""	<!-- ============================================================ 54: Frames -->
	<!-- One 16:9 frame: the wide art fills it; an item with only a poster / icon sits whole on a quiet tile; no art at
	     all = the title in serif on the tile (never a black hole); the title also sits under wide art, so a
	     picture that fails to load still names the item. Frames 496 x 279 at a 552 pitch: the grid ends on x 1760. params: color (art_35 at rest), focused -->
	<include name="Void_FrameItem">
		<param name="color">white</param>
		<param name="focused">false</param>
		<definition>
			<control type="group">
				<left>28</left>
				<top>14</top>
				<width>496</width>
				<height>279</height>
				<include condition="$PARAM[focused]">Void_Anim_FocusPoster</include>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>496</width>
					<height>279</height>
					<texture colordiffuse="bg_raised">common/white.png</texture>
				</control>
				<control type="textbox">
					<left>24</left>
					<top>20</top>
					<width>448</width>
					<height>200</height>
					<font>serif_40</font>
					<textcolor>grey</textcolor>
					<label>$VAR[Wall_Title]</label>
					<visible>{FRAME_WIDE_HAS} | !{SMALL_HAS}</visible>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>496</width>
					<height>279</height>
					<aspectratio>scale</aspectratio>
					<fadetime>160</fadetime>
					<texture background="true" colordiffuse="$PARAM[color]">$VAR[Frame_Wide]</texture>
					<visible>{FRAME_WIDE_HAS}</visible>
				</control>
				<control type="image">
					<left>16</left>
					<top>16</top>
					<width>464</width>
					<height>247</height>
					<aspectratio>keep</aspectratio>
					<fadetime>160</fadetime>
					<texture background="true" colordiffuse="$PARAM[color]">$VAR[Frame_Small]</texture>
					<visible>!{FRAME_WIDE_HAS} + {SMALL_HAS}</visible>
				</control>
				<include>Void_WatchedMarkers</include>
			</control>
		</definition>
	</include>
	<include name="Void_View54">
{view_group(C, body)}
	</include>"""


# ---------------------------------------------------------------- 55 Notes
def view55():
    C = 55
    body = f"""			<control type="list" id="{C}">
				<left>146</left>
				<top>180</top>
				<width>760</width>
				<height>768</height>
				<orientation>vertical</orientation>
{list_nav(C)}
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<viewtype label="31352">biglist</viewtype>
				<visible>{VIEWS[5][3]}</visible>
				<include content="Void_ListLayout">
					<param name="width" value="760"/>
					<param name="height" value="64"/>
					<param name="list_id" value="{C}"/>
					<param name="label" value="$VAR[Wall_Title]"/>
					<param name="label_right" value="190"/>
				</include>
			</control>
			<!-- the reading column (x 1000, 760 wide): kicker, fitted title, meta, ten lines of plot, credits / state -->
			<control type="grouplist">
				<left>0</left>
				<top>184</top>
				<width>1920</width>
				<height>780</height>
				<orientation>vertical</orientation>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<visible>!Container({C}).ListItem.IsParentFolder</visible>
				<control type="group">
					<width>1920</width>
					<height>44</height>
{label(1004, 0, 760, 24, "capsw_20", "grey", "$VAR[Notes_Kicker]", t=chr(9)*5)}
				</control>
				<include content="Title_Notes_Visible">
					<param name="label" value="$VAR[Notes_Title]"/>
					<param name="p0" value="7551"/>
					<param name="p1" value="7552"/>
				</include>
				<include content="Title_Notes_Layout">
					<param name="label" value="$VAR[Notes_Title]"/>
					<param name="p0" value="7551"/>
					<param name="p1" value="7552"/>
				</include>
				<control type="group">
					<width>1920</width>
					<height>60</height>
{label(1000, 10, 760, 32, "sans_26", "grey", "$VAR[Notes_Meta]", t=chr(9)*5)}
				</control>
				<!-- plot, auto height in whole lines (sans 28: (n - 1) x 42 + 34, at most 10 lines = 412), so the credits
				     follow it; a "..." outside the column on the last line when there is more (Kodi has no ellipsis for
				     multi-line text) -->
				<control type="textbox" id="5590">
					<left>1000</left>
					<width>760</width>
					<height max="412">auto</height>
					<font>sans_28</font>
					<textcolor>text_72</textcolor>
					<label>$VAR[Notes_Plot]</label>
				</control>
				<control type="group">
					<width>1920</width>
					<height>0</height>
					<visible>Integer.IsGreater(Container(5590).NumPages,1)</visible>
{label(1764, -34, 40, 34, "sans_28", "grey", "…", t=chr(9)*5)}
				</control>
				<control type="group">
					<width>1920</width>
					<height>30</height>
					<visible>$EXP[Notes_HasPlot]</visible>
				</control>
				<control type="group">
					<width>1920</width>
					<height>34</height>
					<control type="label">
						<left>1000</left>
						<top>0</top>
						<width>760</width>
						<height>24</height>
						<aligny>top</aligny>
						<font>caps_20</font>
						<textcolor>grey</textcolor>
						<label>$VAR[Notes_Credits]</label>
					</control>
				</control>
				<control type="group">
					<width>1920</width>
					<height>30</height>
{label(1000, 0, 760, 24, "caps_20", "grey_soft", "$VAR[Notes_State]", t=chr(9)*5)}
				</control>
			</control>
{hint(C)}
{count_label()}"""
    return f"""	<!-- ============================================================ 55: Notes -->
	<include name="Void_View55">
{view_group(C, body)}
	</include>"""


# ---------------------------------------------------------------- 56 Stills
def stills_layout(focused):
    C = 56
    art_color = "white" if focused else "art_35"
    f = focused
    title_unf = label(300, 46, 1300, 36, "sans_28_med", "grey", "$VAR[View_RowTitle]", f"!Control.HasFocus({C})" if f else None, t=chr(9)*4)
    title_foc = label(300, 38, 1300, 50, "serif_40", "text", "$VAR[View_RowTitle]", f"Control.HasFocus({C})", t=chr(9)*4) if f else ""
    plot_col = "grey" if f else "grey_soft"
    return f"""				<control type="group">
					<left>28</left>
					<top>12</top>
					<width>240</width>
					<height>135</height>
					<visible>!ListItem.IsParentFolder</visible>
					{'<include>Void_Anim_FocusPoster</include>' if f else ''}
					<include content="Void_Artwork">
						<param name="art" value="$VAR[Frame_Wide]"/>
						<param name="color" value="{art_color}"/>
						<param name="title" value="$VAR[Still_Title]"/>
					</include>
					<!-- no wide art: the poster / icon sits whole on the tile (never cropped), the title under it -->
					<control type="image">
						<left>8</left>
						<top>8</top>
						<width>224</width>
						<height>119</height>
						<aspectratio>keep</aspectratio>
						<fadetime>160</fadetime>
						<texture background="true" colordiffuse="{art_color}">$VAR[Frame_Small]</texture>
						<visible>!{FRAME_WIDE_HAS} + {SMALL_HAS}</visible>
					</control>
					<include>Void_WatchedMarkers</include>
				</control>
{label(300, 16, 1300, 24, "capsw_20", "grey" if f else "grey_soft", "$VAR[Still_Kicker]", t=chr(9)*4)}
{title_unf}
{title_foc}
				<control type="textbox">
					<left>300</left>
					<top>92</top>
					<width>1240</width>
					<height>60</height>
					<font>sans_22</font>
					<textcolor>{plot_col}</textcolor>
					<label>$INFO[ListItem.Plot]</label>
				</control>"""


def view56():
    C = 56
    body = f"""			<control type="list" id="{C}">
				<left>132</left>
				<top>160</top>
				<width>1656</width>
				<height>800</height>
				<orientation>vertical</orientation>
{list_nav(C)}
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<viewtype label="31353">biginfo</viewtype>
				<visible>{VIEWS[6][3]}</visible>
				<itemlayout width="1656" height="160">
{stills_layout(False)}
				</itemlayout>
				<focusedlayout width="1656" height="160">
{stills_layout(True)}
				</focusedlayout>
			</control>
{count_label()}"""
    return f"""	<!-- ============================================================ 56: Stills (episodes; films, series, sets, seasons, music videos) -->
	<include name="Void_View56">
{view_group(C, body)}
	</include>"""


# ---------------------------------------------------------------- 57 Tracks
def tracks_layout(focused):
    C = 57
    f = focused
    num_col = "grey" if f else "grey_soft"
    side_col = "grey" if f else "grey_soft"
    out = [label(28, 0, 64, 64, "num_24", num_col, "$VAR[Track_Number]", t=chr(9)*4,
                 extra=chr(10) + chr(9)*5 + "<align>right</align>")]
    out.append(label(120, 14, 840, 36, "sans_28_med", "grey", "$VAR[View_RowTitle]", f"!Control.HasFocus({C})" if f else None, t=chr(9)*4))
    if f:
        out.append(label(120, 6, 840, 50, "serif_40", "text", "$VAR[View_RowTitle]", f"Control.HasFocus({C})", t=chr(9)*4))
    out.append(label(1000, 20, 460, 28, "sans_22", side_col, "$VAR[Track_Where]", t=chr(9)*4))
    out.append(label(1480, 18, 148, 30, "num_22", side_col, "$INFO[ListItem.Duration]", t=chr(9)*4,
                     extra=chr(10) + chr(9)*5 + "<align>right</align>"))
    # labels with aligny top except the number (centred in the row)
    s = "\n".join(out)
    return s.replace("<aligny>top</aligny>\n\t\t\t\t\t<font>num_24</font>", "<aligny>center</aligny>\n\t\t\t\t\t<font>num_24</font>")


def view57():
    C = 57
    body = f"""			<control type="list" id="{C}">
				<left>132</left>
				<top>180</top>
				<width>1656</width>
				<height>768</height>
				<orientation>vertical</orientation>
{list_nav(C)}
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<viewtype label="31354">bigwide</viewtype>
				<visible>{VIEWS[7][3]}</visible>
				<itemlayout width="1656" height="64">
{tracks_layout(False)}
				</itemlayout>
				<focusedlayout width="1656" height="64">
{tracks_layout(True)}
				</focusedlayout>
			</control>
{hint(C)}
{count_label()}"""
    return f"""	<!-- ============================================================ 57: Tracks (songs) -->
	<include name="Void_View57">
{view_group(C, body)}
	</include>"""


# ---------------------------------------------------------------- picker
def picker():
    items = []
    for vid, sid, prev, cond in VIEWS:
        vis = f"\n\t\t\t<visible>{cond}</visible>" if cond else ""
        items.append(f"""		<item>
			<label>$LOCALIZE[{sid}]</label>
			<label2>$VAR[Pick_Cur_{vid}]</label2>
			<icon>views/{prev}.png</icon>
			<onclick>Dialog.Close(1161,true)</onclick>
			<onclick>Container.SetViewMode({vid})</onclick>
			<onclick>SetFocus(50)</onclick>{vis}
		</item>""")
    cur_vars = "\n".join(
        f'\t<variable name="Pick_Cur_{vid}"><value condition="{cur(sid)}">Current</value></variable>' for vid, sid, _, _ in VIEWS)
    onloads = []
    sid_of = {v[0]: v[1] for v in VIEWS}
    for cond, views in CASES:
        for k, vid in enumerate(views):
            if k:
                onloads.append(f'\t\t<onload condition="[{cond}] + {cur(sid_of[vid])}">SetFocus(100,{k},absolute)</onload>')
    return f"""	<!-- ============================================================ view picker (Custom_1161) -->
	<!-- "Current" under the view the library shows (Container.Viewmode = the viewtype label, localized) -->
{cur_vars}
	<include name="Pick_Items">
{chr(10).join(items)}
	</include>
	<!-- Open on the current view: SetFocus(100,k,absolute), k = its place among the views shown for this content
	     (0-based; item 0 = Index is the window's first onload). -->
	<include name="Pick_Onload">
{chr(10).join(onloads)}
	</include>"""


def main():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_views.py - edit the generator, not this file. -->",
             "<!-- Library views 53-57 (0.9.14) and the view picker's items. docs/VIEWS_BRIEF_2026-10-27.md -->",
             "<includes>",
             "\t<!-- ============================================================ variables -->",
             item_vars(53, "One", parent_meta=""),
             f"""	<variable name="One_Prev">
		<value condition="Container(53).ListItemNoWrap(-1).IsParentFolder">Back</value>
		<value>$INFO[Container(53).ListItemNoWrap(-1).Label]</value>
	</variable>
	<variable name="One_Next">
		<value>$INFO[Container(53).ListItemNoWrap(1).Label]</value>
	</variable>
	<!-- One's art comes up after ~1 s of rest (it rises over 1.6 s), not Home's 8 s ambient dwell (Dwell3):
	     on a one-item-at-a-time view the picture is the content (Shield check 2026-10-27: nothing by 5 s). -->
	<expression name="One_AmbientDwell">!Skin.HasSetting(void.noambient) + [[!String.IsEqual(Skin.String(void.dwell),slow) + System.IdleTime(1)] | [String.IsEqual(Skin.String(void.dwell),slow) + System.IdleTime(3)]]</expression>""",
             ambient_art_var(53, "One"),
             item_vars(55, "Notes", parent_meta="Up one level"),
             runtime_vars(None, "Still"),
             STATIC_VARS,
             """	<!-- "412 of 1360" bottom right (as under the wall) -->
	<include name="Void_ViewCount">
		<control type="label">
			<right>160</right>
			<top>988</top>
			<width>400</width>
			<height>26</height>
			<align>right</align>
			<aligny>top</aligny>
			<font>caps_20</font>
			<textcolor>grey_soft</textcolor>
			<label>[COLOR value]$INFO[Container.CurrentItem][/COLOR] of $INFO[Container.NumItems]</label>
			<visible>!$EXP[Lib_Empty]</visible>
		</control>
	</include>""",
             view53(), view54(), view55(), view56(), view57(), picker(),
             "</includes>", ""]
    text = "\n".join(parts)
    # tidy: drop empty lines left by optional pieces inside layouts
    text = "\n".join(l for l in text.split("\n") if l.strip() != "")
    # the shared builders write a few variables a view doesn't read (kdk: variables.unused)
    import re
    for name in ("One_State", "One_Credits", "Still_Rating"):
        text, n = re.subn(r'\t<variable name="' + name + r'">.*?</variable>\n', "", text, flags=re.S)
        assert n == 1, name
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
