"""Generate skins/skin.void/1080i/Includes_Home.xml (Void Home: one item at a time).

Why a generator: seven shelves share one mechanism but each needs its own container id inside
every infolabel (Container(9102).ListItem.Title ...), plus per-shelf stand-in buttons. Editing the SHELVES table and re-running keeps them identical. Never hand-edit the
output.  Usage:  python skins/skin.void/_src/make_home.py

Mechanism (docs/skin.void/SPEC.md, Home):
  * one invisible fixedlist per shelf (9101-9107) drives focus: Up/Down moves within the shelf,
    Left/Right switches shelf (onleft/onright), Select plays/resumes or opens, Info = Kodi's info.
  * everything visible is drawn outside the lists from Container(id).ListItem / ListItemNoWrap(+-1):
    a vertically centred grouplist (neighbour above, year, title 1-2 lines, meta, plot / neighbour
    below) so a two-line title grows the block both ways instead of pushing it off screen.
  * dwell layers: meta at $EXP[Dwell1], plot + hint at $EXP[Dwell2], ambient fanart at $EXP[Dwell3]
    (and never while the list is scrolling). Any key resets System.IdleTime: layers retract.
  * 9111-9117 are per-shelf stand-ins used while a shelf is empty or still loading (an empty list
    can't take focus): they forward Up/Down/Select/Info to their list and switch shelves like it.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Includes_Home.xml"

PLAYLISTS = "special://skin/playlists"

# n, id, caps label, kind, content (dynamic path + attrs) or None for static
SHELVES = [
    (1, 9101, "Next up", "nextup", ("$VAR[Home_NextUpPath]", 'target="videos" limit="25" browse="never"')),
    (2, 9102, "Unwatched[COLOR sep_light]  ·  [/COLOR]rated 7.5+", "movie",
     (f"{PLAYLISTS}/void_toprated_unwatched.xsp", 'target="videos" browse="never"')),
    (3, 9103, "Newest", "movie", ("videodb://recentlyaddedmovies/", 'target="videos" limit="25" browse="never"')),
    (4, 9104, "Albums[COLOR sep_light]  ·  [/COLOR]recently added", "album",
     ("musicdb://recentlyaddedalbums/", 'target="music" limit="25" browse="never"')),
    (5, 9105, "Shows[COLOR sep_light]  ·  [/COLOR]last watched", "show",
     ("videodb://tvshows/titles/", 'target="videos" sortby="lastplayed" sortorder="descending" limit="30" browse="never"')),
    (6, 9106, "Library", "static", None),
    (7, 9107, "Search", "static", None),
]
N = len(SHELVES)

STATIC_ITEMS = {
    9106: [
        # label, label2 (meta), kicker, onclick, visible
        ("Now playing", "$INFO[MusicPlayer.Artist,,[COLOR sep_light]  ·  [/COLOR]]$INFO[Player.Title]", "Playing",
         "ActivateWindow(visualisation)", "Player.HasAudio + !Player.HasVideo"),
        ("Now playing", "$INFO[Player.Title]", "Playing", "ActivateWindow(fullscreenvideo)", "Player.HasVideo"),
        ("Movies", "$INFO[Window(Home).Property(Movies.Count),, films]$INFO[Window(Home).Property(Movies.UnWatched),[COLOR sep_light]  ·  [/COLOR], unwatched]",
         "Library", "ActivateWindow(Videos,videodb://movies/titles/,return)", "Library.HasContent(movies)"),
        ("TV Shows", "$INFO[Window(Home).Property(TVShows.Count),, shows]$INFO[Window(Home).Property(Episodes.Count),[COLOR sep_light]  ·  [/COLOR], episodes]",
         "Library", "ActivateWindow(Videos,videodb://tvshows/titles/,return)", "Library.HasContent(tvshows)"),
        ("Music", "$INFO[Window(Home).Property(Music.AlbumsCount),, albums]$INFO[Window(Home).Property(Music.ArtistsCount),[COLOR sep_light]  ·  [/COLOR], artists]",
         "Library", "ActivateWindow(Music,musicdb://albums/,return)", "Library.HasContent(music)"),
        ("Music videos", "$INFO[Window(Home).Property(MusicVideos.Count),, videos]",
         "Library", "ActivateWindow(Videos,videodb://musicvideos/titles/,return)", "Library.HasContent(musicvideos)"),
        ("Live TV", "Channels and the guide", "Library", "ActivateWindow(TVChannels)", "System.HasPVRAddon"),
        ("Weather", "$INFO[Weather.Temperature]$INFO[Weather.Conditions,[COLOR sep_light]  ·  [/COLOR],]$INFO[Weather.Location,[COLOR sep_light]  ·  [/COLOR],]",
         "Outside", "ActivateWindow(Weather)", "!String.IsEmpty(Weather.Conditions)"),
        ("Add-ons", "Video, music and program add-ons", "Elsewhere", "ActivateWindow(AddonBrowser,addons://sources/video/,return)", ""),
        ("Favourites", "Things you starred", "Elsewhere", "ActivateWindow(FavouritesBrowser)", ""),
        ("Pictures", "Photo sources", "Elsewhere", "ActivateWindow(Pictures)", ""),
        ("Files", "Browse video sources", "Elsewhere", "ActivateWindow(Videos,sources://video/,return)", ""),
        ("Settings", "Kodi, the skin, your profile", "System", "ActivateWindow(Settings)", ""),
        ("System", "Update or clean the library, power", "System", "ActivateWindow(1151)", ""),
    ],
    9107: [
        ("Search", "Films, shows, episodes, people and music", "Find", "ActivateWindow(1150)", ""),
    ],
}

# ---------------------------------------------------------------- per-kind variables


def C(i, info, offset=None):
    if offset is None:
        return f"Container({i}).ListItem.{info}"
    return f"Container({i}).ListItemNoWrap({offset}).{info}"


def var(name, values):
    out = [f'\t<variable name="{name}">']
    for cond, val in values:
        if cond:
            out.append(f'\t\t<value condition="{cond}">{val}</value>')
        else:
            out.append(f"\t\t<value>{val}</value>")
    out.append("\t</variable>")
    return "\n".join(out)


SEP = "[COLOR sep_light]  ·  [/COLOR]"


def runtime(i):
    return [
        (f"Integer.IsGreater({C(i,'Duration(h)')},0) + Integer.IsGreater({C(i,'Duration(m)')},0)",
         f"$INFO[{C(i,'Duration(h)')},, h ]$INFO[{C(i,'Duration(m)')},, min]"),
        (f"Integer.IsGreater({C(i,'Duration(h)')},0)", f"$INFO[{C(i,'Duration(h)')},, h]"),
        (None, f"$INFO[{C(i,'Duration(m)')},, min]"),
    ]


def shelf_vars(n, i, kind):
    v = []
    # neighbours: episodes / next-up show the show name
    for name, off in (("Prev", -1), ("Next", 1)):
        if kind == "nextup":
            v.append(var(f"Home_{name}_{i}", [
                (f"!String.IsEmpty({C(i,'TVShowTitle',off)})", f"$INFO[{C(i,'TVShowTitle',off)}]"),
                (None, f"$INFO[{C(i,'Label',off)}]")]))
        else:
            v.append(var(f"Home_{name}_{i}", [(None, f"$INFO[{C(i,'Label',off)}]")]))
    # kicker (the small caps line above the title)
    if kind == "nextup":
        kick = [(f"String.IsEqual({C(i,'DBType')},episode) + Integer.IsLess({C(i,'Episode')},10)",
                 f"Season $INFO[{C(i,'Season')}][COLOR sep]  ·  [/COLOR]Episode $INFO[{C(i,'Episode')}]"),
                (f"String.IsEqual({C(i,'DBType')},episode)",
                 f"Season $INFO[{C(i,'Season')}][COLOR sep]  ·  [/COLOR]Episode $INFO[{C(i,'Episode')}]"),
                (None, f"$INFO[{C(i,'Year')}]")]
    elif kind == "static":
        kick = [(None, f"$INFO[{C(i,'Property(kicker)')}]")]
    else:
        kick = [(None, f"$INFO[{C(i,'Year')}]")]
    v.append(var(f"Home_Kicker_{i}", kick))
    # title
    if kind == "nextup":
        title = [(f"!String.IsEmpty({C(i,'TVShowTitle')})", f"$INFO[{C(i,'TVShowTitle')}]"), (None, f"$INFO[{C(i,'Label')}]")]
    elif kind in ("movie",):
        title = [(f"!String.IsEmpty({C(i,'Title')})", f"$INFO[{C(i,'Title')}]"), (None, f"$INFO[{C(i,'Label')}]")]
    else:
        title = [(None, f"$INFO[{C(i,'Label')}]")]
    v.append(var(f"Home_Title_{i}", title))
    # meta (layer 1)
    rt = f"$VAR[Home_Runtime_{i}]"
    rating = f"[COLOR value]$INFO[{C(i,'Rating')}][/COLOR]"
    has_rating = f"!String.IsEmpty({C(i,'Rating')}) + !String.IsEqual({C(i,'Rating')},0.0)"
    if kind == "movie":
        v.append(var(f"Home_Runtime_{i}", runtime(i)))
        meta = [
            (f"{has_rating} + !String.IsEmpty({C(i,'Director')})", f"{rt}{SEP}{rating}{SEP}$INFO[{C(i,'Director')}]"),
            (has_rating, f"{rt}{SEP}{rating}"),
            (None, f"{rt}$INFO[{C(i,'Director')},{SEP},]"),
        ]
    elif kind == "nextup":
        v.append(var(f"Home_Runtime_{i}", runtime(i)))
        meta = [
            (f"String.IsEqual({C(i,'DBType')},episode)",
             f"[COLOR value]$INFO[{C(i,'Title')}][/COLOR]$VAR[Home_RuntimeSep_{i}]$INFO[{C(i,'Premiered')},{SEP}aired ,]"),
            (None, f"$INFO[{C(i,'Property(WatchedEpisodes)')},, watched]$INFO[{C(i,'Property(UnWatchedEpisodes)')},{SEP}, to go]$INFO[{C(i,'Studio')},{SEP},]"),
        ]
        v.append(var(f"Home_RuntimeSep_{i}", [
            (f"Integer.IsGreater({C(i,'Duration(m)')},0) | Integer.IsGreater({C(i,'Duration(h)')},0)", f"{SEP}{rt}")]))
    elif kind == "album":
        meta = [(None, f"[COLOR value]$INFO[{C(i,'Artist')}][/COLOR]$INFO[{C(i,'Genre')},{SEP},]")]
    elif kind == "show":
        meta = [
            (f"Integer.IsGreater({C(i,'Property(UnWatchedEpisodes)')},0)",
             f"$INFO[{C(i,'Property(TotalSeasons)')},, seasons]{SEP}[COLOR value]$INFO[{C(i,'Property(UnWatchedEpisodes)')},, to watch][/COLOR]$INFO[{C(i,'Studio')},{SEP},]"),
            (None, f"$INFO[{C(i,'Property(TotalSeasons)')},, seasons]{SEP}all watched$INFO[{C(i,'Studio')},{SEP},]"),
        ]
    else:
        meta = [(None, f"$INFO[{C(i,'Label2')}]")]
    v.append(var(f"Home_Meta_{i}", meta))
    # plot (layer 2)
    if kind == "album":
        plot = [(None, f"$INFO[{C(i,'Property(Album_Description)')}]")]
    elif kind == "static":
        plot = [(None, "")]
    else:
        plot = [(None, f"$INFO[{C(i,'Plot')}]")]
    v.append(var(f"Home_Plot_{i}", plot))
    # ambient art (layer 3)
    if kind == "nextup":
        art = [(f"!String.IsEmpty({C(i,'Art(tvshow.fanart)')})", f"$INFO[{C(i,'Art(tvshow.fanart)')}]"),
               (f"!String.IsEmpty({C(i,'Art(fanart)')})", f"$INFO[{C(i,'Art(fanart)')}]"),
               (None, f"$INFO[{C(i,'Art(thumb)')}]")]
    elif kind == "album":
        art = [(f"!String.IsEmpty({C(i,'Art(fanart)')})", f"$INFO[{C(i,'Art(fanart)')}]"),
               (None, f"$INFO[{C(i,'Art(artist.fanart)')}]")]
    elif kind == "static":
        art = [(None, "")]
    else:
        art = [(f"!String.IsEmpty({C(i,'Art(fanart)')})", f"$INFO[{C(i,'Art(fanart)')}]"),
               (None, f"$INFO[{C(i,'Art(landscape)')}]")]
    v.append(var(f"Home_Art_{i}", art))
    # hint
    if kind == "static":
        hint = [(None, "Select to open")]
    elif kind in ("album", "show"):
        hint = [(None, f"Select to open{SEP}Info for more")]
    else:
        hint = [(f"{C(i,'IsResumable')}", f"Select to resume{SEP}Info for more"),
                (f"{C(i,'IsFolder')}", f"Select to open{SEP}Info for more"),
                (None, f"Select to play{SEP}Info for more")]
    v.append(var(f"Home_Hint_{i}", hint))
    return "\n".join(v)


def art_cond(i, kind):
    """condition for 'this shelf has ambient art for the focused item'."""
    if kind == "nextup":
        return (f"[!String.IsEmpty({C(i,'Art(tvshow.fanart)')}) | !String.IsEmpty({C(i,'Art(fanart)')}) | "
                f"!String.IsEmpty({C(i,'Art(thumb)')})]")
    if kind == "album":
        return f"[!String.IsEmpty({C(i,'Art(fanart)')}) | !String.IsEmpty({C(i,'Art(artist.fanart)')})]"
    if kind == "static":
        return "false"
    return f"[!String.IsEmpty({C(i,'Art(fanart)')}) | !String.IsEmpty({C(i,'Art(landscape)')})]"


# ---------------------------------------------------------------- controls

def nav(n, i, verb, target_n, direction):
    t = SHELVES[target_n - 1][1]
    return (f"\t\t\t\t<{verb}>SetProperty(void.dir,{direction},home)</{verb}>\n"
            f"\t\t\t\t<{verb}>SetProperty(void.shelf,{target_n},home)</{verb}>\n"
            f"\t\t\t\t<{verb} condition=\"Integer.IsGreater(Container({t}).NumItems,0)\">SetFocus({t})</{verb}>\n"
            f"\t\t\t\t<{verb} condition=\"Integer.IsEqual(Container({t}).NumItems,0)\">SetFocus({9110 + target_n})</{verb}>\n")


def prev_n(n):
    return N if n == 1 else n - 1


def next_n(n):
    return 1 if n == N else n + 1


def driver_list(n, i, kind, content):
    clicks = ""
    if kind in ("movie", "nextup"):
        clicks = (
            "\t\t\t\t<onclick condition=\"!ListItem.IsFolder + [String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,episode)]\">"
            "PlayMedia($ESCINFO[ListItem.FilenameAndPath],resume)</onclick>\n"
            "\t\t\t\t<onclick condition=\"ListItem.IsFolder\">ActivateWindow(Videos,$ESCINFO[ListItem.FolderPath],return)</onclick>\n")
    elif kind == "show":
        clicks = "\t\t\t\t<onclick>ActivateWindow(Videos,$ESCINFO[ListItem.FolderPath],return)</onclick>\n"
    elif kind == "album":
        clicks = "\t\t\t\t<onclick>ActivateWindow(Music,$ESCINFO[ListItem.FolderPath],return)</onclick>\n"
    if content:
        path, attrs = content
        body = f"\t\t\t\t<content {attrs}>{path}</content>\n"
    else:
        items = []
        for label, label2, kicker, onclick, vis in STATIC_ITEMS[i]:
            v = f"<visible>{vis}</visible>" if vis else ""
            items.append(
                f"\t\t\t\t\t<item><label>{label}</label><label2>{label2}</label2>"
                f"<property name=\"kicker\">{kicker}</property><onclick>{onclick}</onclick>{v}</item>")
        body = "\t\t\t\t<content>\n" + "\n".join(items) + "\n\t\t\t\t</content>\n"
    # the focused layout draws the fanart invisibly once focus rests (Dwell1) so the provider loads the
    # item's art (LESSONS 2: provider art only loads for drawn items) - never while moving.
    art_probe = ""
    if kind != "static":
        art_probe = (
            "\t\t\t\t\t<control type=\"image\"><left>0</left><top>0</top><width>1</width><height>1</height>"
            "<texture colordiffuse=\"00ffffff\">$INFO[ListItem.Art(fanart)]</texture>"
            "<visible>$EXP[Dwell1]</visible></control>\n")
    return f"""			<control type="fixedlist" id="{i}">
				<description>Shelf {n} driver ({kind})</description>
				<left>0</left>
				<top>0</top>
				<width>4</width>
				<height>12</height>
				<orientation>vertical</orientation>
				<focusposition>1</focusposition>
				<movement>0</movement>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<onfocus>SetProperty(void.shelf,{n},home)</onfocus>
				<onup>noop</onup>
				<ondown>noop</ondown>
{nav(n, i, 'onleft', prev_n(n), 'prev')}{nav(n, i, 'onright', next_n(n), 'next')}				<onback>SetFocus({i},0,absolute)</onback>
{clicks}				<itemlayout height="4" width="4"/>
				<focusedlayout height="4" width="4">
{art_probe}				</focusedlayout>
{body}			</control>"""


def stand_ins():
    """One stand-in button per shelf (9111-9117). An empty or still-loading list can't take focus, so
    navigation lands on the shelf's stand-in instead; it forwards keys to its own list once it has
    items. Static targets only: Kodi caches conditions per frame and may queue builtins, so action
    chains must never branch on a property set earlier in the same chain."""
    out = []
    for n, i, _label, _kind, _c in SHELVES:
        b = 9110 + n
        has = f"Integer.IsGreater(Container({i}).NumItems,0)"
        out.append(f"""			<control type="button" id="{b}">
				<description>Shelf {n} stand-in (empty or loading)</description>
				<left>0</left>
				<top>20</top>
				<width>4</width>
				<height>4</height>
				<texturefocus />
				<texturenofocus />
				<label></label>
				<onfocus>SetProperty(void.shelf,{n},home)</onfocus>
				<onup condition="{has}">SetFocus({i})</onup>
				<ondown condition="{has}">Control.Move({i},1)</ondown>
				<ondown condition="{has}">SetFocus({i})</ondown>
				<onclick condition="{has}">SetFocus({i})</onclick>
				<onclick condition="{has}">Action(Select)</onclick>
				<oninfo condition="{has}">SetFocus({i})</oninfo>
				<oninfo condition="{has}">Action(Info)</oninfo>
{nav(n, i, 'onleft', prev_n(n), 'prev')}{nav(n, i, 'onright', next_n(n), 'next')}			</control>""")
    return "\n".join(out)


def shelf_display(n, i, kind):
    is_n = f"String.IsEqual(Window(Home).Property(void.shelf),{n})"
    empty = f"Integer.IsEqual(Container({i}).NumItems,0) + !Container({i}).IsUpdating"
    has = f"Integer.IsGreater(Container({i}).NumItems,0)"
    amb = f"$EXP[Dwell3] + !Container({i}).Scrolling + {art_cond(i, kind)}"
    empty_msg = {
        "nextup": "Nothing in progress. Start a show and its next episode waits here.",
        "movie": "Nothing here yet.",
        "album": "No albums yet.",
        "show": "No shows yet.",
        "static": "",
    }[kind]
    return f"""		<!-- ===== shelf {n}: display ===== -->
		<control type="group">
			<visible>{is_n}</visible>
			<include>Void_Anim_Shelf</include>
			<control type="grouplist">
				<left>0</left>
				<top>8</top>
				<width>1920</width>
				<height>1080</height>
				<orientation>vertical</orientation>
				<align>center</align>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<include content="Void_Anim_Roll"><param name="id" value="{i}"/></include>
				<visible>{has}</visible>
				<!-- neighbour above (retracts with the plot) -->
				<control type="group">
					<width>1920</width>
					<height>126</height>
					<control type="label">
						<left>160</left>
						<top>0</top>
						<width>1500</width>
						<height>53</height>
						<aligny>top</aligny>
						<font>serif_48</font>
						<textcolor>neighbour</textcolor>
						<label>$VAR[Home_Prev_{i}]</label>
						<visible>!$EXP[Dwell2]</visible>
						<include>Void_Anim_Dwell</include>
					</control>
				</control>
				<!-- kicker: year / season + episode -->
				<control type="group">
					<width>1920</width>
					<height>40</height>
					<control type="label">
						<left>164</left>
						<top>0</top>
						<width>1400</width>
						<height>24</height>
						<aligny>top</aligny>
						<font>capsw_20</font>
						<textcolor>grey</textcolor>
						<label>$VAR[Home_Kicker_{i}]</label>
						<include content="Void_Anim_Recede"><param name="condition" value="{amb}"/><param name="level" value="85"/></include>
					</control>
				</control>
				<!-- title fitted to the width (Includes_Titles.xml): 172 / 132 on one line, then 132 / 104 on two -->
				<include content="Title_Home_Visible">
					<param name="label" value="$VAR[Home_Title_{i}]"/>
					<param name="recede" value="{amb}"/>
					<param name="p0" value="{7700 + n * 10}"/>
					<param name="p1" value="{7701 + n * 10}"/>
					<param name="p2" value="{7702 + n * 10}"/>
				</include>
				<include content="Title_Home_Layout">
					<param name="label" value="$VAR[Home_Title_{i}]"/>
					<param name="p0" value="{7700 + n * 10}"/>
					<param name="p1" value="{7701 + n * 10}"/>
					<param name="p2" value="{7702 + n * 10}"/>
				</include>
				<!-- meta line (layer 1) -->
				<control type="group">
					<width>1920</width>
					<height>87</height>
					<control type="label">
						<left>160</left>
						<top>21</top>
						<width>1500</width>
						<height>32</height>
						<aligny>top</aligny>
						<font>sans_26</font>
						<textcolor>grey</textcolor>
						<label>$VAR[Home_Meta_{i}]</label>
						<visible>$EXP[Dwell1]</visible>
						<include>Void_Anim_Dwell</include>
					</control>
				</control>
				<!-- plot (layer 2) shares the band with the neighbour below, which retracts -->
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
						<label>$VAR[Home_Plot_{i}]</label>
						<visible>$EXP[Dwell2]</visible>
						<include>Void_Anim_Dwell</include>
					</control>
					<control type="label">
						<left>160</left>
						<top>66</top>
						<width>1500</width>
						<height>53</height>
						<aligny>top</aligny>
						<font>serif_48</font>
						<textcolor>neighbour</textcolor>
						<label>$VAR[Home_Next_{i}]</label>
						<visible>!$EXP[Dwell2]</visible>
						<include>Void_Anim_Dwell</include>
					</control>
				</control>
			</control>
			<!-- empty shelf -->
			<control type="group">
				<visible>{empty}</visible>
				<include>Void_Anim_Dwell</include>
				<control type="label">
					<left>152</left>
					<top>438</top>
					<width>1600</width>
					<height>90</height>
					<aligny>top</aligny>
					<font>serif_72</font>
					<textcolor>neighbour</textcolor>
					<label>Nothing here</label>
				</control>
				<control type="label">
					<left>160</left>
					<top>548</top>
					<width>1600</width>
					<height>32</height>
					<aligny>top</aligny>
					<font>sans_26</font>
					<textcolor>grey</textcolor>
					<label>{empty_msg}</label>
				</control>
			</control>
			<!-- hint (layer 2) -->
			<include content="Void_Hint">
				<param name="label" value="$VAR[Home_Hint_{i}]"/>
				<param name="top" value="966"/>
				<param name="visible" value="$EXP[Dwell2] + {has}"/>
			</include>
		</control>"""


def shelf_ambient(n, i, kind):
    is_n = f"String.IsEqual(Window(Home).Property(void.shelf),{n})"
    amb = f"$EXP[Dwell3] + !Container({i}).Scrolling + {art_cond(i, kind)}"
    plate = ""
    if kind == "album":
        plate = f"""
		<!-- album without fanart: the cover rises as a plate on the right -->
		<control type="group">
			<visible>{is_n} + $EXP[Dwell3] + !Container({i}).Scrolling + !{art_cond(i, kind)} + !String.IsEmpty(Container({i}).ListItem.Art(thumb))</visible>
			<include>Void_Anim_AmbientRise</include>
			<control type="image">
				<left>1160</left>
				<top>240</top>
				<width>600</width>
				<height>600</height>
				<aspectratio>keep</aspectratio>
				<fadetime>300</fadetime>
				<texture background="true" colordiffuse="$VAR[AmbientLevel]">$INFO[Container({i}).ListItem.Art(thumb)]</texture>
			</control>
		</control>"""
    return f"""		<control type="group">
			<visible>{is_n} + {amb}</visible>
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
					<texture background="true" colordiffuse="$VAR[AmbientLevel]">$VAR[Home_Art_{i}]</texture>
				</control>
			</control>
		</control>{plate}"""


def dots():
    out = ["""			<control type="grouplist">
				<left>160</left>
				<top>130</top>
				<width>400</width>
				<height>8</height>
				<orientation>horizontal</orientation>
				<itemgap>14</itemgap>"""]
    for n, i, _l, _k, _c in SHELVES:
        is_n = f"String.IsEqual(Window(Home).Property(void.shelf),{n})"
        out.append(f"""				<control type="group">
					<width>8</width>
					<height>8</height>
					<control type="image">
						<left>0</left><top>0</top><width>8</width><height>8</height>
						<texture colordiffuse="text">common/dot.png</texture>
						<visible>{is_n}</visible>
					</control>
					<control type="image">
						<left>1</left><top>1</top><width>6</width><height>6</height>
						<texture colordiffuse="sep">common/dot.png</texture>
						<visible>!{is_n}</visible>
					</control>
				</control>""")
    out.append("\t\t\t</control>")
    return "\n".join(out)


def main():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_home.py - edit the generator, not this file. -->",
             "<!--",
             "\tVoid Home: one item at a time. See the generator's docstring and docs/skin.void/SPEC.md.",
             "\tIds: 9101-9107 shelf drivers (Next up, Unwatched rated, Newest, Albums, Shows, Library, Search),",
             "\t9111-9117 their stand-ins. Window(Home) properties: void.shelf (1-7), void.dir (prev/next),",
             "\tvoid.reload (Next up refresh stamp).",
             "-->",
             "<includes>"]
    parts.append(var("Home_NextUpPath", [
        ("System.AddonIsEnabled(script.embuary.helper)",
         "plugin://script.embuary.helper/?info=getnextup&amp;reload=$INFO[Window(Home).Property(void.reload)]"),
        (None, f"{PLAYLISTS}/void_inprogress_tvshows.xsp")]))
    shelf_label = [(f"String.IsEqual(Window(Home).Property(void.shelf),{n})", label) for n, i, label, k, c in SHELVES]
    shelf_label.append((None, SHELVES[0][2]))
    parts.append(var("Home_ShelfLabel", shelf_label))
    for n, i, label, kind, content in SHELVES:
        parts.append(shelf_vars(n, i, kind))
    # active-shelf ambient visible (for receding the furniture)
    amb_any = " | ".join(
        f"[String.IsEqual(Window(Home).Property(void.shelf),{n}) + !Container({i}).Scrolling + {art_cond(i, k)}]"
        for n, i, _l, k, _c in SHELVES if k != "static")
    parts.append(f'\t<expression name="Home_AmbientUp">$EXP[Dwell3] + [{amb_any}]</expression>')

    parts.append('\t<include name="Home_Drivers">\n\t\t<control type="group">\n\t\t\t<description>focus drivers (invisible)</description>')
    parts.append(stand_ins())
    for n, i, label, kind, content in SHELVES:
        parts.append(driver_list(n, i, kind, content))
    parts.append("\t\t</control>\n\t</include>")

    parts.append('\t<include name="Home_Ambient">')
    for n, i, label, kind, content in SHELVES:
        if kind != "static":
            parts.append(shelf_ambient(n, i, kind))
    parts.append("""		<control type="image">
			<left>0</left>
			<top>0</top>
			<width>1920</width>
			<height>1080</height>
			<texture colordiffuse="scrim">common/vignette_home.png</texture>
			<visible>$EXP[Home_AmbientUp]</visible>
			<include>Void_Anim_AmbientRise</include>
			<animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
			<animation effect="fade" start="100" end="0" time="150">WindowClose</animation>
		</control>
	</include>""")

    parts.append("""	<include name="Home_Furniture">
		<control type="group">
			<include content="Void_Anim_Recede"><param name="condition" value="$EXP[Home_AmbientUp]"/><param name="level" value="60"/></include>
			<control type="label">
				<left>160</left>
				<top>86</top>
				<width>1200</width>
				<height>24</height>
				<aligny>top</aligny>
				<font>caps_20</font>
				<textcolor>grey</textcolor>
				<label>$VAR[Home_ShelfLabel]</label>
			</control>
""" + dots() + """
			<include>Void_Clock</include>
		</control>
	</include>""")

    parts.append("""	<include name="Home_NowPlaying">
		<control type="group">
			<visible>Player.HasMedia</visible>
			<include>Anim_FadeVisible</include>
			<include content="Void_Anim_Recede"><param name="condition" value="$EXP[Home_AmbientUp]"/><param name="level" value="60"/></include>
			<control type="label">
				<right>160</right>
				<top>124</top>
				<width>900</width>
				<height>26</height>
				<align>right</align>
				<aligny>top</aligny>
				<font>sans_22</font>
				<textcolor>clock</textcolor>
				<label>[COLOR grey_soft]PLAYING  [/COLOR]$INFO[MusicPlayer.Artist,,  ·  ]$INFO[Player.Title]</label>
			</control>
			<control type="progress">
				<right>160</right>
				<top>160</top>
				<width>240</width>
				<height>1</height>
				<texturebg colordiffuse="hairline">common/white.png</texturebg>
				<midtexture colordiffuse="clock">common/white.png</midtexture>
				<info>Player.Progress</info>
			</control>
		</control>
	</include>""")
    parts.append('\t<include name="Home_Shelves">')
    for n, i, label, kind, content in SHELVES:
        parts.append(shelf_display(n, i, kind))
    parts.append("\t</include>")
    parts.append("</includes>\n")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
