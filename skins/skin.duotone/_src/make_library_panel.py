"""Library panel (Custom_1155_LibraryPanel.xml) and view picker (Custom_1156_ViewPicker.xml) for Duotone.

    python skins/skin.duotone/_src/make_library_panel.py

docs/requests/library-panel/BRIEF.md. Both are centred section-colour panels with the 8 px ink frame, Anton
title and the numbered Index rows of the System menu (Dlg_IndexListLayout): no new visual language.

1155 Library panel - opened by Left past the first column / Right past the last of every library view, by the
     OPTIONS word in the video and music headers, and from Home's System menu ("Update library" / "Clean library",
     which set Window(Home).Property(duotone.libpanel) to update / clean first).
     In a library: Update library (Stop the update while scanning), Clean library, View, Sort by, Order,
     Unwatched only (video), Sets (films, when the library has sets), Search, Library settings. Update / Clean hide in add-on and plugin folders.
     Clean library never runs straight away: Kodi 21's CleanLibrary() builtin has NO confirmation of its own,
     so the row opens a confirm step (list 101, focus on "No").
     Back closes the panel; focus returns to the item you came from (Kodi restores the window's focus).
1156 View picker - opened by the header view word and the panel's View row. One print per view valid for the
     folder (the same Container.Content conditions the views use), its name, and an ink NOW tag on the current
     one. OK = Container.SetViewMode(id) + close, Back = close, no change.
"""
from pathlib import Path
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

ROOT = Path(__file__).resolve().parents[1] / "1080i"
RM = "Skin.HasSetting(duotone.reducemotion)"

V = "Window.IsActive(videos)"
M = "Window.IsActive(music)"
INLIB = f"[{V} | {M}]"
HOME = f"![{V} | {M}]"
NOPLUG = "String.IsEmpty(Container.PluginName) + !Container.Content(addons)"
PCLEAN = "String.IsEqual(Window(Home).Property(duotone.libpanel),clean)"
CONF = "Window(Home).Property(duotone.libconfirm)"
VIDLIB = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
          "Container.Content(seasons) | Container.Content(episodes) | Container.Content(musicvideos)]")
SORTABLE = "!String.IsEmpty(Container.SortMethod)"
# Sets row (docs/requests/SETS_AND_RM_BRIEF.md): only while the Videos window shows films (or the films root) from the
# library, and the library has sets. Container.* inside this dialog reads the media window underneath (LESSONS).
SETS = (f"{V} + [Container.Content(movies) | String.IsEqual(Container.FolderPath,videodb://movies/)] + "
        "Library.HasContent(moviesets) + String.IsEmpty(Container.PluginName)")

ROW_H = 68
LIST_TOP = 80
PANEL_W = 600


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
    # in a library window
    item("$VAR[DT_Lib_UpdateLabel]", "$VAR[DT_Lib_Kind]", f"{INLIB} + {NOPLUG}",
         [CLOSE, (V, "UpdateLibrary(video)"), (M, "UpdateLibrary(music)")]),
    item("$LOCALIZE[14247]", "$VAR[DT_Lib_Kind]",
         f"{INLIB} + {NOPLUG} + ![{V} + Library.IsScanningVideo] + ![{M} + Library.IsScanningMusic]",
         [(V, "SetProperty(duotone.libconfirm,video,home)"), (M, "SetProperty(duotone.libconfirm,music,home)"),
          ("", "SetFocus(101)")]),
    item("View", "$INFO[Container.Viewmode]", f"{INLIB} + Integer.IsGreater(Container.ViewCount,1)",
         [CLOSE, ("", "ActivateWindow(1156)")]),
    item("Sort by", "$INFO[Container.SortMethod]", f"{INLIB} + {SORTABLE}",
         [CLOSE, (V, "SendClick(videos,3)"), (M, "SendClick(music,3)")]),
    item("Order", "$INFO[Container.SortOrder]", f"{INLIB} + {SORTABLE}",
         [("", "Container.SetSortDirection")]),
    item("Unwatched only", "$VAR[DT_Lib_HideWatched]", f"{V} + {VIDLIB}",
         [CLOSE, ("", "SendClick(14)")]),
    # Sets: the films' sets in this same Videos window (Container.Update keeps the history: Back walks
    # set -> all sets -> films). Not a Home item (Omar).
    item("$LOCALIZE[20434]", "Collections", SETS,
         [CLOSE, ("", "Container.Update(videodb://movies/sets/)")]),
    item("$LOCALIZE[137]", "", INLIB, [CLOSE, ("", "ActivateWindow(1150)")]),
    item("Library settings", "Kodi", INLIB, [CLOSE, ("", "ActivateWindow(mediasettings)")]),
    # from Home (System menu): update / clean, videos and music
    item("$VAR[DT_Lib_UpdateVideoLabel]", "Films + series", f"{HOME} + !{PCLEAN}",
         [CLOSE, ("", "UpdateLibrary(video)")]),
    item("$VAR[DT_Lib_UpdateMusicLabel]", "Albums + songs", f"{HOME} + !{PCLEAN}",
         [CLOSE, ("", "UpdateLibrary(music)")]),
    item("Videos", "Films + series", f"{HOME} + {PCLEAN} + !Library.IsScanningVideo",
         [("", "SetProperty(duotone.libconfirm,video,home)"), ("", "SetFocus(101)")]),
    item("$LOCALIZE[2]", "Albums + songs", f"{HOME} + {PCLEAN} + !Library.IsScanningMusic",
         [("", "SetProperty(duotone.libconfirm,music,home)"), ("", "SetFocus(101)")]),
]

CONFIRM_ITEMS = [
    item("No, keep everything", "", "true", [("", "Dialog.Close(1155)")]),
    item("Yes, clean the video library", "", f"String.IsEqual({CONF},video)",
         [CLOSE, ("", "CleanLibrary(video)")]),
    item("Yes, clean the music library", "", f"String.IsEqual({CONF},music)",
         [CLOSE, ("", "CleanLibrary(music)")]),
]

MAXROWS = 9   # films: update, clean, view, sort, order, unwatched, sets, search, settings


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
			<texture colordiffuse="$VAR[scrim]">common/white.png</texture>
		</control>"""


def panel():
    full_h = LIST_TOP + MAXROWS * ROW_H + 16
    top0 = (1080 - full_h) // 2
    slides = "".join(
        f"""
			<animation effect="slide" start="0,0" end="0,{(MAXROWS - n) * ROW_H // 2}" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>"""
        for n in range(1, MAXROWS))
    frames = "".join(
        f"""
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{PANEL_W}</width>
					<height>{LIST_TOP + n * ROW_H + 16}</height>
					<texture border="16" colordiffuse="$VAR[DT_PanelTint]">$VAR[DT_PanelTex]</texture>
					<visible>Integer.IsEqual(Container(100).NumItems,{n})</visible>
				</control>""" for n in range(1, MAXROWS + 1))
    conf_h = 80 + 92 + 2 * ROW_H + 16
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file. -->
<!--{__doc__}-->
<window type="dialog" id="1155">
	<defaultcontrol always="true">100</defaultcontrol>
	<onload>ClearProperty(duotone.libconfirm,home)</onload>
	<onload>SetFocus(100,0,absolute)</onload>
	<onunload>ClearProperty(duotone.libconfirm,home)</onunload>
	<onunload>ClearProperty(duotone.libpanel,home)</onunload>
	<include>Anim_DialogOpenClose</include>
	<controls>{backdrop()}
		<!-- the rows -->
		<control type="group">
			<left>660</left>
			<top>{top0}</top>
			<width>{PANEL_W}</width>
			<height>{full_h}</height>
			<visible>String.IsEmpty({CONF})</visible>{slides}
			<control type="group">{frames}
			</control>
			<control type="label">
				<left>32</left>
				<top>12</top>
				<width>536</width>
				<height>60</height>
				<aligny>center</aligny>
				<font>an_48</font>
				<textcolor>$VAR[SectionText]</textcolor>
				<label>$VAR[DT_Lib_Title]</label>
			</control>
			<control type="label">
				<left>32</left>
				<top>12</top>
				<width>536</width>
				<height>60</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>cap_20</font>
				<textcolor>$VAR[SectionText]</textcolor>
				<label>$VAR[DT_Lib_Caption]</label>
			</control>
			<control type="list" id="100">
				<left>16</left>
				<top>{LIST_TOP}</top>
				<width>568</width>
				<height>{MAXROWS * ROW_H}</height>
				<onup>100</onup>
				<ondown>100</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="568"/>
					<param name="height" value="{ROW_H}"/>
					<param name="list_id" value="100"/>
				</include>
				<content>{''.join(PANEL_ITEMS)}
				</content>
			</control>
		</control>
		<!-- the confirm step for Clean library (focus starts on No) -->
		<control type="group">
			<left>660</left>
			<top>{(1080 - conf_h) // 2}</top>
			<width>{PANEL_W}</width>
			<height>{conf_h}</height>
			<!-- no <visible> on this group: a hidden parent stops SetFocus(101) (LESSONS Void 0.9.3) -->
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>{PANEL_W}</width>
				<height>{conf_h}</height>
				<texture border="16" colordiffuse="$VAR[DT_PanelTint]">$VAR[DT_PanelTex]</texture>
				<visible>!String.IsEmpty({CONF})</visible>
			</control>
			<control type="label">
				<left>32</left>
				<top>12</top>
				<width>536</width>
				<height>60</height>
				<aligny>center</aligny>
				<font>an_48</font>
				<textcolor>$VAR[SectionText]</textcolor>
				<label>$VAR[DT_Lib_ConfirmTitle]</label>
				<visible>!String.IsEmpty({CONF})</visible>
			</control>
			<control type="textbox">
				<left>32</left>
				<top>80</top>
				<width>536</width>
				<height>72</height>
				<font>body_24</font>
				<textcolor>$VAR[SectionText]</textcolor>
				<label>Kodi removes every entry whose file it can no longer find. It can't be undone.</label>
				<visible>!String.IsEmpty({CONF})</visible>
			</control>
			<control type="list" id="101">
				<left>16</left>
				<top>172</top>
				<width>568</width>
				<height>{2 * ROW_H}</height>
				<onup>101</onup>
				<ondown>101</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<visible allowhiddenfocus="true">!String.IsEmpty({CONF})</visible>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="568"/>
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
WALL_V = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
          "Container.Content(seasons) | Container.Content(musicvideos)]")
EPIS_V = "[Container.Content(episodes) | Container.Content(seasons)]"
ALB_V = "[Container.Content(albums) | Container.Content(artists)]"
IS_WALL = "String.IsEqual(Container.Viewmode,Wall)"
IS_EPIS = "String.IsEqual(Container.Viewmode,Episodes)"
IS = lambda name: f"String.IsEqual(Container.Viewmode,{name})"
# 0.9.16 views (_src/make_views_more.py): Poster / Screens / Sheet (video), Stage / Tracks (music)
NAMED = ("Wall", "Episodes", "Poster", "Screens", "Sheet", "Stage", "Tracks", "Rows")
# 0.9.18 (docs/VIEWS_PER_SECTION_2026-10-28.md): Rows 510 (films, sets, series, music videos), Stage 508 also songs
ROWS_V = "[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(musicvideos)]"
IS_LIST = " + ".join(f"!{IS(n)}" for n in NAMED)

# (view id, name, preview, visible, is-current)
VIEWS = [
    (500, "Wall", "wall", f"{V} + {WALL_V}", f"{V} + {IS_WALL}"),
    (503, "Episodes", "episodes", f"{V} + {EPIS_V}", f"{V} + {IS_EPIS}"),
    (505, "Poster", "poster", V, f"{V} + {IS('Poster')}"),
    (506, "Screens", "screens", V, f"{V} + {IS('Screens')}"),
    (507, "Sheet", "sheet", f"{V} + {WALL_V}", f"{V} + {IS('Sheet')}"),
    (510, "Rows", "rows", f"{V} + {ROWS_V}", f"{V} + {IS('Rows')}"),
    (50, "$LOCALIZE[535]", "list", V, f"{V} + {IS_LIST}"),
    (504, "Wall", "albums", f"{M} + {ALB_V}", f"{M} + {IS_WALL}"),
    (508, "Stage", "stage", f"{M} + [Container.Content(albums) | Container.Content(artists) | Container.Content(songs)]", f"{M} + {IS('Stage')}"),
    (509, "Tracks", "tracks", f"{M} + Container.Content(songs)", f"{M} + {IS('Tracks')}"),
    (50, "$LOCALIZE[535]", "list_music", M, f"{M} + {IS_LIST}"),
]
CARD_W, CARD_H = 360, 280   # slot: 20 + 320 x 180 print + 16 + Anton name 60
# 0.9.16: up to six views (seasons: Wall, Episodes, Poster, Screens, Sheet, List) -> a 3-column panel, 1 or 2 rows
COLS, MAXROWS_PICK = 3, 2
PRE_W, PRE_H = 320, 180


def picker():
    # the current view comes first (focus starts on it; Control.Move in <onload> or one AlarmClock tick later
    # never moved the list on the Shield), then the others in their usual order
    entries = [(vid, name, pre, vis, f"[{now}]", "Now") for vid, name, pre, vis, now in VIEWS] + \
              [(vid, name, pre, vis, f"![{now}]", "") for vid, name, pre, vis, now in VIEWS]
    items = "".join(f"""
					<item>
						<label>{name}</label>
						<label2>{mark}</label2>
						<icon>duotone/views/{pre}.png</icon>
						<property name="dark">duotone/views/dark/{pre}.png</property>
						<visible>{esc(vis)} + {cur}</visible>
						<onclick>Dialog.Close(1156,true)</onclick>
						<onclick>Container.SetViewMode({vid})</onclick>
					</item>""" for vid, name, pre, vis, cur, mark in entries)
    nowvars = ""
    # a static list keeps its selected row between openings: start on the first (= current) view every time
    onload = "\n\t<onload>SetFocus(100,0,absolute)</onload>"
    layout = lambda focused: f"""
					<control type="group">
						<left>20</left>
						<top>20</top>
						<width>{PRE_W}</width>
						<height>{PRE_H}</height>{'''
						<include>Anim_FocusZoom</include>''' if focused else ''}
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{PRE_W}</width>
							<height>{PRE_H}</height>
							<texture colordiffuse="$VAR[SectionColor]">$INFO[ListItem.Icon]</texture>
							<visible>!$EXP[DT_LookDark]</visible>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{PRE_W}</width>
							<height>{PRE_H}</height>
							<texture>$INFO[ListItem.Property(dark)]</texture>
							<visible>$EXP[DT_LookDark]</visible>
						</control>
						<control type="group">
							<visible>!String.IsEmpty(ListItem.Label2)</visible>
							<control type="image">
								<left>0</left>
								<top>0</top>
								<width>72</width>
								<height>36</height>
								<texture colordiffuse="$VAR[ink]">common/white.png</texture>
							</control>
							<control type="label">
								<left>0</left>
								<top>0</top>
								<width>72</width>
								<height>36</height>
								<align>center</align>
								<aligny>center</aligny>
								<font>cap_20</font>
								<textcolor>$VAR[paper]</textcolor>
								<selectedcolor>$VAR[paper]</selectedcolor>
								<label>$INFO[ListItem.Label2]</label>
							</control>
						</control>{'''
						<include content="DT_FocusFrame">
							<param name="visible" value="Control.HasFocus(100)"/>
						</include>''' if focused else ''}
					</control>
					<control type="label">
						<left>20</left>
						<top>{20 + PRE_H + 16}</top>
						<width>{PRE_W}</width>
						<height>60</height>
						<aligny>center</aligny>
						<font>an_48</font>
						<textcolor>$VAR[SectionText{'' if focused else '2'}]</textcolor>
						<selectedcolor>$VAR[SectionText{'' if focused else '2'}]</selectedcolor>
						<label>$INFO[ListItem.Label]</label>
					</control>"""
    frames = []
    slides = []
    for n in range(1, COLS * MAXROWS_PICK + 1):
        cols, rows = min(n, COLS), (n + COLS - 1) // COLS
        frames.append(f"""
				<control type="image">
					<left>{(COLS - cols) * CARD_W // 2}</left>
					<top>0</top>
					<width>{cols * CARD_W + 24}</width>
					<height>{76 + rows * CARD_H + 12}</height>
					<texture border="16" colordiffuse="$VAR[DT_PanelTint]">$VAR[DT_PanelTex]</texture>
					<visible>Integer.IsEqual(Container(100).NumItems,{n})</visible>
				</control>""")
        if cols < COLS:
            slides.append(f"""
				<animation effect="slide" start="0,0" end="{(COLS - cols) * CARD_W // 2},0" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>""")
    # one row: the whole card sits half a row lower (centred like the two-row card)
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
			<top>{(1080 - 76 - MAXROWS_PICK * CARD_H - 12) // 2}</top>
			<width>{total_w}</width>
			<height>{76 + MAXROWS_PICK * CARD_H + 12}</height>{vslide}{''.join(frames)}
			<control type="group">{''.join(slides)}
				<control type="label">
					<left>32</left>
					<top>12</top>
					<width>{2 * CARD_W}</width>
					<height>60</height>
					<aligny>center</aligny>
					<font>an_48</font>
					<textcolor>$VAR[SectionText]</textcolor>
					<label>View</label>
				</control>
				<control type="panel" id="100">
					<left>12</left>
					<top>76</top>
					<width>{3 * CARD_W + 40}</width>
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
			<control type="label">
				<left>32</left>
				<top>12</top>
				<width>{total_w - 64}</width>
				<height>60</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>cap_20</font>
				<textcolor>$VAR[SectionText]</textcolor>
				<label>OK switches  ·  Back keeps it</label>
				<visible>Integer.IsGreater(Container(100).NumItems,2)</visible>
			</control>
		</control>
	</controls>
</window>
""", nowvars


def variables(nowvars):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file.
     Labels for the Library panel (Custom_1155) and the view picker (Custom_1156). -->
<includes>
	<variable name="DT_Lib_Title">
		<value condition="{HOME} + {PCLEAN}">$LOCALIZE[14247]</value>
		<value condition="{HOME}">$LOCALIZE[653]</value>
		<value>Library</value>
	</variable>
	<variable name="DT_Lib_Caption">
		<value condition="{M}">$LOCALIZE[2]</value>
		<value condition="{V} + [Container.Content(tvshows) | Container.Content(seasons) | Container.Content(episodes)]">Series</value>
		<value condition="{V} + [Container.Content(movies) | Container.Content(sets)]">Films</value>
		<value condition="{V}">$LOCALIZE[3]</value>
		<value>Videos + music</value>
	</variable>
	<variable name="DT_Lib_Kind">
		<value condition="{M}">$LOCALIZE[2]</value>
		<value>Films + series</value>
	</variable>
	<variable name="DT_Lib_UpdateLabel">
		<value condition="{V} + Library.IsScanningVideo">Stop the update</value>
		<value condition="{M} + Library.IsScanningMusic">Stop the update</value>
		<value>$LOCALIZE[653]</value>
	</variable>
	<variable name="DT_Lib_UpdateVideoLabel">
		<value condition="Library.IsScanningVideo">Stop the video update</value>
		<value>$LOCALIZE[3]</value>
	</variable>
	<variable name="DT_Lib_UpdateMusicLabel">
		<value condition="Library.IsScanningMusic">Stop the music update</value>
		<value>$LOCALIZE[2]</value>
	</variable>
	<variable name="DT_Lib_HideWatched">
		<value condition="System.Setting(hidewatched)">On</value>
		<value>Off</value>
	</variable>
	<!-- list 50's scrollbar: Right goes on to the Library panel in the video / music library -->
	<variable name="DT_Lib_ScrollRight">
		<value condition="{INLIB}">ActivateWindow(1155)</value>
		<value>SetFocus(50)</value>
	</variable>
	<variable name="DT_Lib_ConfirmTitle">
		<value condition="String.IsEqual({CONF},music)">Clean music?</value>
		<value>Clean videos?</value>
	</variable>{nowvars}
</includes>
"""


if __name__ == "__main__":
    (ROOT / "Custom_1155_LibraryPanel.xml").write_text(finish_xml(strip_defaults(panel(), ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    xml, nowvars = picker()
    (ROOT / "Custom_1156_ViewPicker.xml").write_text(finish_xml(strip_defaults(xml, ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    (ROOT / "Includes_Library.xml").write_text(finish_xml(variables(nowvars)), encoding="utf-8", newline="\n")
    print("wrote Custom_1155_LibraryPanel.xml, Custom_1156_ViewPicker.xml, Includes_Library.xml")
