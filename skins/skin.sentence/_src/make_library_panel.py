"""Library panel (Custom_1155_LibraryPanel.xml) and view picker (Custom_1156_ViewPicker.xml) for Sentence.

    python skins/skin.sentence/_src/make_library_panel.py

docs/requests/library-panel/BRIEF.md. Both are the System menu's card (surface round6, Young Serif title, rows
in serif with the lilac block on focus, Dlg_IndexListLayout): no new visual language, and they talk in phrases.

1155 Library panel - "Or would you like to..." Opened by Left past the first column / Right past the last of every
     library view, by the header's last phrase ("..., or [more]"), and from the System menu ("Update the library" /
     "Clean the library", which set Window(Home).Property(sentence.libpanel) to update / clean first).
     In a library: update the library (stop updating while a scan runs), clean the library, see them another way,
     sort them another way, turn the order round, show only the unseen / show everything (video), see the sets
     (films, when the library has sets), find something,
     change the library settings. Update / clean hide in add-on and plugin folders.
     Clean never runs straight away: Kodi 21's CleanLibrary() builtin has NO confirmation of its own, so the row
     opens a confirm step (list 101, focus on "no, leave it as it is").
     Back closes the panel; focus returns to the item you came from.
1156 View picker - "See them as..." Opened by the header's view phrase ("as [a grid]") and the panel. One preview per
     view valid for the folder (the views' own Container.Content conditions), its name, "now" on the current one.
     OK = Container.SetViewMode(id) + close, Back = close, no change.
"""
from pathlib import Path
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

ROOT = Path(__file__).resolve().parents[1] / "1080i"
SK = "sentence"

V = "Window.IsActive(videos)"
M = "Window.IsActive(music)"
INLIB = f"[{V} | {M}]"
HOME = f"![{V} | {M}]"
NOPLUG = "String.IsEmpty(Container.PluginName) + !Container.Content(addons)"
PCLEAN = f"String.IsEqual(Window(Home).Property({SK}.libpanel),clean)"
CONF = f"Window(Home).Property({SK}.libconfirm)"
VIDLIB = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
          "Container.Content(seasons) | Container.Content(episodes) | Container.Content(musicvideos)]")
SORTABLE = "!String.IsEmpty(Container.SortMethod)"
# Sets row (docs/requests/SETS_AND_RM_BRIEF.md): only while the Videos window shows films (or the films root) from the
# library, and the library has sets. Container.* inside this dialog reads the media window underneath (LESSONS).
SETS = (f"{V} + [Container.Content(movies) | String.IsEqual(Container.FolderPath,videodb://movies/)] + "
        "Library.HasContent(moviesets) + String.IsEmpty(Container.PluginName)")

ROW_H = 68
LIST_TOP = 64
PANEL_W = 720


def esc(s):
    return s.replace("&", "&amp;")


def item(label, label2, visible, clicks):
    c = "".join(
        f"\n\t\t\t\t\t\t<onclick{(' condition=' + chr(34) + esc(cond) + chr(34)) if cond else ''}>{a}</onclick>"
        for cond, a in clicks)
    return f"""
					<item>
						<label>{label}</label>
						<label2>{label2}</label2>
						<visible>{esc(visible)}</visible>{c}
					</item>"""


CLOSE = ("", "Dialog.Close(1155,true)")

PANEL_ITEMS = [
    item("$VAR[Sen_Lib_UpdateLabel]", "$VAR[Sen_Lib_Kind]", f"{INLIB} + {NOPLUG}",
         [CLOSE, (V, "UpdateLibrary(video)"), (M, "UpdateLibrary(music)")]),
    item("clean the library", "$VAR[Sen_Lib_Kind]",
         f"{INLIB} + {NOPLUG} + ![{V} + Library.IsScanningVideo] + ![{M} + Library.IsScanningMusic]",
         [(V, f"SetProperty({SK}.libconfirm,video,home)"), (M, f"SetProperty({SK}.libconfirm,music,home)"),
          ("", "SetFocus(101)")]),
    item("see them another way", "$INFO[Container.Viewmode]",
         f"{INLIB} + Integer.IsGreater(Container.ViewCount,1)", [CLOSE, ("", "ActivateWindow(1156)")]),
    item("sort them another way", "$INFO[Container.SortMethod,by ,]", f"{INLIB} + {SORTABLE}",
         [CLOSE, (V, "SendClick(videos,3)"), (M, "SendClick(music,3)")]),
    item("turn the order round", "$VAR[Lib_Direction]", f"{INLIB} + {SORTABLE}",
         [("", "Container.SetSortDirection")]),
    item("$VAR[Sen_Lib_WatchedLabel]", "", f"{V} + {VIDLIB}", [CLOSE, ("", "SendClick(14)")]),
    # Sets: the films' sets in this same Videos window (Container.Update keeps the history: Back walks
    # set -> all sets -> films). Not a Home item (Omar).
    item("see the sets", "collections", SETS,
         [CLOSE, ("", "Container.Update(videodb://movies/sets/)")]),
    item("find something", "", INLIB, [CLOSE, ("", "ActivateWindow(1150)")]),
    item("change the library settings", "Kodi", INLIB, [CLOSE, ("", "ActivateWindow(mediasettings)")]),
    # from Home (the System menu)
    item("$VAR[Sen_Lib_UpdateVideoLabel]", "", f"{HOME} + !{PCLEAN}", [CLOSE, ("", "UpdateLibrary(video)")]),
    item("$VAR[Sen_Lib_UpdateMusicLabel]", "", f"{HOME} + !{PCLEAN}", [CLOSE, ("", "UpdateLibrary(music)")]),
    item("clean the films and shows", "", f"{HOME} + {PCLEAN} + !Library.IsScanningVideo",
         [("", f"SetProperty({SK}.libconfirm,video,home)"), ("", "SetFocus(101)")]),
    item("clean the music", "", f"{HOME} + {PCLEAN} + !Library.IsScanningMusic",
         [("", f"SetProperty({SK}.libconfirm,music,home)"), ("", "SetFocus(101)")]),
]

CONFIRM_ITEMS = [
    item("no, leave it as it is", "", "true", [("", "Dialog.Close(1155)")]),
    item("yes, clean the films and shows", "", f"String.IsEqual({CONF},video)", [CLOSE, ("", "CleanLibrary(video)")]),
    item("yes, clean the music", "", f"String.IsEqual({CONF},music)", [CLOSE, ("", "CleanLibrary(music)")]),
]

MAXROWS = 9   # films: update, clean, view, sort, order, unseen, sets, find, settings


def backdrop():
    return """
		<control type="image">
			<description>backdrop dim (own fades: without them Kodi draws the dim over the dialog)</description>
			<left>0</left>
			<top>0</top>
			<width>screen_w</width>
			<height>screen_h</height>
			<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
			<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
			<texture colordiffuse="dim_dialog">common/white.png</texture>
		</control>"""


def card(w, h, vis=None):
    v = f"\n\t\t\t\t<visible>{vis}</visible>" if vis else ""
    return f"""
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>{w}</width>
				<height>{h}</height>
				<texture border="8" colordiffuse="surface">sentence/round6.png</texture>{v}
			</control>"""


def panel():
    full_h = LIST_TOP + MAXROWS * ROW_H + 12
    top0 = (1080 - full_h) // 2
    slides = "".join(
        f"""
			<animation effect="slide" start="0,0" end="0,{(MAXROWS - n) * ROW_H // 2}" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>"""
        for n in range(1, MAXROWS))
    frames = "".join(card(PANEL_W, LIST_TOP + n * ROW_H + 12, f"Integer.IsEqual(Container(100).NumItems,{n})")
                     for n in range(1, MAXROWS + 1))
    conf_vis = f"!String.IsEmpty({CONF})"
    conf_h = 64 + 92 + 2 * ROW_H + 12
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file. -->
<!--{__doc__}-->
<window type="dialog" id="1155">
	<defaultcontrol always="true">100</defaultcontrol>
	<onload>ClearProperty({SK}.libconfirm,home)</onload>
	<onload>SetFocus(100,0,absolute)</onload>
	<onunload>ClearProperty({SK}.libconfirm,home)</onunload>
	<onunload>ClearProperty({SK}.libpanel,home)</onunload>
	<include>Anim_DialogOpenClose</include>
	<controls>{backdrop()}
		<control type="group">
			<left>{(1920 - PANEL_W) // 2}</left>
			<top>{top0}</top>
			<width>{PANEL_W}</width>
			<height>{full_h}</height>
			<visible>String.IsEmpty({CONF})</visible>{slides}
			<control type="group">{frames}
			</control>
			<control type="label">
				<left>24</left>
				<top>4</top>
				<width>{PANEL_W - 48}</width>
				<height>56</height>
				<font>serif_34</font>
				<textcolor>text</textcolor>
				<label>$VAR[Sen_Lib_Title]</label>
			</control>
			<control type="list" id="100">
				<left>12</left>
				<top>{LIST_TOP}</top>
				<width>{PANEL_W - 24}</width>
				<height>{MAXROWS * ROW_H}</height>
				<onup>100</onup>
				<ondown>100</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="{PANEL_W - 24}"/>
					<param name="height" value="{ROW_H}"/>
					<param name="list_id" value="100"/>
				</include>
				<content>{''.join(PANEL_ITEMS)}
				</content>
			</control>
		</control>
		<!-- the confirm step for clean (focus starts on "no"); no <visible> on the group, a hidden parent stops
		     SetFocus(101) (LESSONS Void 0.9.3) -->
		<control type="group">
			<left>{(1920 - PANEL_W) // 2}</left>
			<top>{(1080 - conf_h) // 2}</top>
			<width>{PANEL_W}</width>
			<height>{conf_h}</height>{card(PANEL_W, conf_h, conf_vis)}
			<control type="label">
				<left>24</left>
				<top>4</top>
				<width>{PANEL_W - 48}</width>
				<height>56</height>
				<font>serif_34</font>
				<textcolor>text</textcolor>
				<label>$VAR[Sen_Lib_ConfirmTitle]</label>
				<visible>{conf_vis}</visible>
			</control>
			<control type="textbox">
				<left>24</left>
				<top>64</top>
				<width>{PANEL_W - 48}</width>
				<height>72</height>
				<font>body_24</font>
				<textcolor>body</textcolor>
				<label>Kodi forgets everything whose file it can't find any more. You can't undo it.</label>
				<visible>{conf_vis}</visible>
			</control>
			<control type="list" id="101">
				<left>12</left>
				<top>156</top>
				<width>{PANEL_W - 24}</width>
				<height>{2 * ROW_H}</height>
				<onup>101</onup>
				<ondown>101</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<visible allowhiddenfocus="true">{conf_vis}</visible>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="{PANEL_W - 24}"/>
					<param name="height" value="{ROW_H}"/>
					<param name="list_id" value="101"/>
				</include>
				<content>{''.join(CONFIRM_ITEMS)}
				</content>
			</control>
		</control>
	</controls>
</window>
"""


# ---------------------------------------------------------------------------------------------- view picker
GRID_V = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
          "Container.Content(seasons) | Container.Content(musicvideos)]")
WALL_V = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
          "Container.Content(musicvideos)]")
EPIS_V = "[Container.Content(episodes) | Container.Content(seasons)]"
ALB_V = "[Container.Content(albums) | Container.Content(artists)]"


def isv(label):
    return f"String.IsEqual(Container.Viewmode,{label})"


# 0.9.16 views (_src/make_views_more.py): a page / scenes (video), a tracklist / portraits (music)
NAMED = ("a grid", "a wall", "episodes", "a page", "scenes", "a tracklist", "portraits")
IS_LIST = " + ".join(f"!{isv(n)}" for n in NAMED)

VIEWS = [
    (500, "a grid", "grid", f"{V} + {GRID_V}", f"{V} + {isv('a grid')}"),
    (501, "a wall", "wall", f"{V} + {WALL_V}", f"{V} + {isv('a wall')}"),
    (503, "episodes", "episodes", f"{V} + {EPIS_V}", f"{V} + {isv('episodes')}"),
    (505, "a page", "page", V, f"{V} + {isv('a page')}"),
    (506, "scenes", "scenes", V, f"{V} + {isv('scenes')}"),
    (50, "a list", "list", V, f"{V} + {IS_LIST}"),
    (504, "a grid", "albums", f"{M} + {ALB_V}", f"{M} + {isv('a grid')}"),
    (508, "portraits", "portraits", f"{M} + {ALB_V}", f"{M} + {isv('portraits')}"),
    (507, "a tracklist", "tracklist", f"{M} + Container.Content(songs)", f"{M} + {isv('a tracklist')}"),
    (50, "a list", "list_music", M, f"{M} + {IS_LIST}"),
]
# 0.9.16: up to five views for one folder (films / seasons) -> a 3-column panel of one or two rows
COLS, MAXROWS_PICK = 3, 2
CARD_W, CARD_H = 360, 268   # slot: 20 + 320 x 180 preview + 8 + bar 4 + name 52
PRE_W, PRE_H = 320, 180


def picker():
    # the current view comes first (focus starts on it; Control.Move in <onload> or one AlarmClock tick later
    # never moved the list on the Shield), then the others in their usual order
    entries = [(vid, name, pre, vis, f"[{now}]", "now") for vid, name, pre, vis, now in VIEWS] + \
              [(vid, name, pre, vis, f"![{now}]", "") for vid, name, pre, vis, now in VIEWS]
    items = "".join(f"""
					<item>
						<label>{name}</label>
						<label2>{mark}</label2>
						<icon>sentence/views/{pre}.png</icon>
						<visible>{esc(vis)} + {cur}</visible>
						<onclick>Dialog.Close(1156,true)</onclick>
						<onclick>Container.SetViewMode({vid})</onclick>
					</item>""" for vid, name, pre, vis, cur, mark in entries)
    nowvars = ""
    # a static list keeps its selected row between openings: start on the first (= current) view every time
    onload = "\n\t<onload>SetFocus(100,0,absolute)</onload>"

    def layout(focused):
        dim = "white" if focused else "dim_art"
        bar = f"""
						<control type="image">
							<left>0</left>
							<top>{PRE_H + 8}</top>
							<width>{PRE_W}</width>
							<height>4</height>
							<texture colordiffuse="lilac">common/white.png</texture>
							<visible>Control.HasFocus(100)</visible>
						</control>""" if focused else ""
        col = "text" if focused else "muted"
        return f"""
					<control type="group">
						<left>20</left>
						<top>16</top>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{PRE_W}</width>
							<height>{PRE_H}</height>
							<texture colordiffuse="{dim if focused else 'dim_art'}">$INFO[ListItem.Icon]</texture>{'' if not focused else '''
							<visible>Control.HasFocus(100)</visible>'''}
						</control>{'' if not focused else f'''
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{PRE_W}</width>
							<height>{PRE_H}</height>
							<texture colordiffuse="dim_art">$INFO[ListItem.Icon]</texture>
							<visible>!Control.HasFocus(100)</visible>
						</control>'''}{bar}
						<control type="label">
							<left>0</left>
							<top>{PRE_H + 16}</top>
							<width>{PRE_W}</width>
							<height>48</height>
							<font>serif_30</font>
							<textcolor>{col}</textcolor>
							<selectedcolor>{col}</selectedcolor>
							<label>$INFO[ListItem.Label]$INFO[ListItem.Label2,[COLOR lilac]  · ,[/COLOR]]</label>
						</control>
					</control>"""
    frames, slides = [], []
    for n in range(1, COLS * MAXROWS_PICK + 1):
        cols, rows = min(n, COLS), (n + COLS - 1) // COLS
        frames.append(f"""
			<control type="group">
				<left>{(COLS - cols) * CARD_W // 2}</left>
				<visible>Integer.IsEqual(Container(100).NumItems,{n})</visible>{card(cols * CARD_W + 24, 72 + rows * CARD_H + 12)}
			</control>""")
        if cols < COLS:
            slides.append(f"""
				<animation effect="slide" start="0,0" end="{(COLS - cols) * CARD_W // 2},0" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>""")
    # one row: the whole card sits half a row lower, centred like the two-row card
    vslide = f"""
			<animation effect="slide" start="0,0" end="0,{CARD_H // 2}" time="0" condition="Integer.IsLess(Container(100).NumItems,{COLS + 1})">Conditional</animation>"""
    total_w = 3 * CARD_W + 24
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file. -->
<!--{__doc__}-->
<window type="dialog" id="1156">
	<defaultcontrol always="true">100</defaultcontrol>{onload}
	<include>Anim_DialogOpenClose</include>
	<controls>{backdrop()}
		<control type="group">
			<left>{(1920 - total_w) // 2}</left>
			<top>{(1080 - 72 - MAXROWS_PICK * CARD_H - 12) // 2}</top>
			<width>{total_w}</width>
			<height>{72 + MAXROWS_PICK * CARD_H + 12}</height>{vslide}{''.join(frames)}
			<control type="group">{''.join(slides)}
				<control type="label">
					<left>32</left>
					<top>8</top>
					<width>{2 * CARD_W}</width>
					<height>56</height>
					<font>serif_34</font>
					<textcolor>text</textcolor>
					<label>See them as...</label>
				</control>
				<control type="panel" id="100">
					<left>12</left>
					<top>64</top>
					<width>{3 * CARD_W}</width>
					<height>{MAXROWS_PICK * CARD_H}</height>
					<orientation>vertical</orientation>
					<onup>noop</onup>
					<ondown>noop</ondown>
					<onleft>noop</onleft>
					<onright>noop</onright>
					<scrolltime tween="cubic" easing="out">160</scrolltime>
					<itemlayout width="{CARD_W}" height="{CARD_H}">{layout(False)}
					</itemlayout>
					<focusedlayout width="{CARD_W}" height="{CARD_H}">{layout(True)}
					</focusedlayout>
					<content>{items}
					</content>
				</control>
			</control>
		</control>
	</controls>
</window>
""", nowvars


def variables(nowvars):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file.
     Phrases for the Library panel (Custom_1155) and the view picker (Custom_1156). -->
<includes>
	<variable name="Sen_Lib_Title">
		<value condition="{HOME} + {PCLEAN}">What should I clean?</value>
		<value condition="{HOME}">What should I update?</value>
		<value>Or would you like to...</value>
	</variable>
	<variable name="Sen_Lib_Kind">
		<value condition="{M}">your music</value>
		<value>films and shows</value>
	</variable>
	<variable name="Sen_Lib_UpdateLabel">
		<value condition="[{V} + Library.IsScanningVideo] | [{M} + Library.IsScanningMusic]">stop updating the library</value>
		<value>update the library</value>
	</variable>
	<variable name="Sen_Lib_UpdateVideoLabel">
		<value condition="Library.IsScanningVideo">stop updating the films and shows</value>
		<value>update the films and shows</value>
	</variable>
	<variable name="Sen_Lib_UpdateMusicLabel">
		<value condition="Library.IsScanningMusic">stop updating the music</value>
		<value>update the music</value>
	</variable>
	<variable name="Sen_Lib_WatchedLabel">
		<value condition="System.Setting(hidewatched)">show everything again</value>
		<value>show only the unseen</value>
	</variable>
	<variable name="Sen_Lib_ConfirmTitle">
		<value condition="String.IsEqual({CONF},music)">Clean the music?</value>
		<value>Clean the films and shows?</value>
	</variable>
	<!-- Dlg_IndexListLayout reads per-list ink variables (Includes_Dialogs.xml has them for 100, not for the
	     confirm list 101: without these its focused row printed no text) -->
	<variable name="Dlg_Ink101"><value condition="Control.HasFocus(101)">on_lilac</value><value>text</value></variable>
	<variable name="Dlg_InkSoft101"><value condition="Control.HasFocus(101)">on_lilac</value><value>muted</value></variable>
	<variable name="Dlg_InkMark101"><value condition="Control.HasFocus(101)">on_lilac</value><value>lilac</value></variable>
	<!-- list 50's scrollbar: Right goes on to the panel in the video / music library -->
	<variable name="Sen_Lib_ScrollRight">
		<value condition="{INLIB}">ActivateWindow(1155)</value>
		<value>SetFocus(50)</value>
	</variable>{nowvars}
</includes>
"""


if __name__ == "__main__":
    (ROOT / "Custom_1155_LibraryPanel.xml").write_text(finish_xml(strip_defaults(panel(), ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    xml, nowvars = picker()
    (ROOT / "Custom_1156_ViewPicker.xml").write_text(finish_xml(strip_defaults(xml, ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    (ROOT / "Includes_Library.xml").write_text(finish_xml(variables(nowvars)), encoding="utf-8", newline="\n")
    print("wrote Custom_1155_LibraryPanel.xml, Custom_1156_ViewPicker.xml, Includes_Library.xml")
