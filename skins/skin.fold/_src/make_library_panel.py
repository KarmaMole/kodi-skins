"""Library panel (Custom_1155_LibraryPanel.xml) and view picker (Custom_1156_ViewPicker.xml) for Fold.

    python skins/skin.fold/_src/make_library_panel.py

docs/requests/library-panel/BRIEF.md. Both are folded notes (Fold_GenericDialog: cream stock, centre crease, cut
edge in the section colour, head_34 heading + caps kicker, dotted rule) that unfold from their crease
(Anim_DialogOpenClose), with the lifted slip rows of the dialogs (Dlg_IndexListLayout): no new visual language.

1155 Library panel - opened by Left past the first column of the shelf / sleeves / list, Left or Right off the ends
     of the season cards and the concertina strip, the "Options" header word (video and music), and from Home's
     Settings cards "Update library" / "Clean library" (they set Window(Home).Property(fold.libpanel) first).
     In a library: Update library (Stop the update while scanning), Clean library, View, Sort by, Order,
     Unwatched only (video), Sets (films, when the library has sets: Container.Update to videodb://movies/sets/
     in the same Videos window), Search, Library settings. Update / Clean hide in add-on and plugin folders.
     Clean never runs straight away: Kodi 21's CleanLibrary() builtin has NO confirmation of its own, so the row
     opens a confirm note (list 101, focus on No).
     Back closes the note; focus returns to the card you came from.
1156 View picker - opened by the "View: ..." header word and the panel's View row. One preview per view valid for
     the folder (the views' own Container.Content conditions), its name, a NOW chip on the current one.
     OK = Container.SetViewMode(id) + close, Back = close, no change.
"""
import re
from pathlib import Path
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

ROOT = Path(__file__).resolve().parents[1] / "1080i"
SK = "fold"

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
# Sets row (docs/requests/SETS_AND_RM_BRIEF.md): only while Videos browses films and the library has sets
FILMS = ("[Container.Content(movies) | String.IsEqual(Container.FolderPath,videodb://movies/) | "
         "String.IsEqual(Container.FolderPath,library://video/movies/)]")
SETS = f"{V} + {FILMS} + Library.HasContent(moviesets)"

ROW_H = 64            # dialog_row_h
LIST_TOP = 104        # dialog_header_h + 16
PANEL_W = 640


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
    item("$VAR[Fold_Lib_UpdateLabel]", "$VAR[Fold_Lib_Kind]", f"{INLIB} + {NOPLUG}",
         [CLOSE, (V, "UpdateLibrary(video)"), (M, "UpdateLibrary(music)")]),
    item("$LOCALIZE[14247]", "$VAR[Fold_Lib_Kind]",
         f"{INLIB} + {NOPLUG} + ![{V} + Library.IsScanningVideo] + ![{M} + Library.IsScanningMusic]",
         [(V, f"SetProperty({SK}.libconfirm,video,home)"), (M, f"SetProperty({SK}.libconfirm,music,home)"),
          ("", "SetFocus(101)")]),
    item("View", "$VAR[Fold_Lib_ViewName]", f"{INLIB} + Integer.IsGreater(Container.ViewCount,1)",
         [CLOSE, ("", "ActivateWindow(1156)")]),
    item("Sort by", "$INFO[Container.SortMethod]", f"{INLIB} + {SORTABLE}",
         [CLOSE, (V, "SendClick(videos,3)"), (M, "SendClick(music,3)")]),
    item("Order", "$INFO[Container.SortOrder]", f"{INLIB} + {SORTABLE}", [("", "Container.SetSortDirection")]),
    item("Unwatched only", "$VAR[Fold_Lib_HideWatched]", f"{V} + {VIDLIB}", [CLOSE, ("", "SendClick(14)")]),
    item("$LOCALIZE[20434]", "Film collections", SETS, [CLOSE, ("", "Container.Update(videodb://movies/sets/)")]),
    item("$LOCALIZE[137]", "", INLIB, [CLOSE, ("", "ActivateWindow(1150)")]),
    item("Library settings", "Kodi", INLIB, [CLOSE, ("", "ActivateWindow(mediasettings)")]),
    # from Home (the Settings cards)
    item("$VAR[Fold_Lib_UpdateVideoLabel]", "Films · series", f"{HOME} + !{PCLEAN}", [CLOSE, ("", "UpdateLibrary(video)")]),
    item("$VAR[Fold_Lib_UpdateMusicLabel]", "Albums · songs", f"{HOME} + !{PCLEAN}", [CLOSE, ("", "UpdateLibrary(music)")]),
    item("$LOCALIZE[3]", "Films · series", f"{HOME} + {PCLEAN} + !Library.IsScanningVideo",
         [("", f"SetProperty({SK}.libconfirm,video,home)"), ("", "SetFocus(101)")]),
    item("$LOCALIZE[2]", "Albums · songs", f"{HOME} + {PCLEAN} + !Library.IsScanningMusic",
         [("", f"SetProperty({SK}.libconfirm,music,home)"), ("", "SetFocus(101)")]),
]

CONFIRM_ITEMS = [
    item("No, keep everything", "", "true", [("", "Dialog.Close(1155)")]),
    item("Yes, clean the video library", "", f"String.IsEqual({CONF},video)", [CLOSE, ("", "CleanLibrary(video)")]),
    item("Yes, clean the music library", "", f"String.IsEqual({CONF},music)", [CLOSE, ("", "CleanLibrary(music)")]),
]

MAXROWS = 9           # films: update, clean, view, sort, order, unwatched, sets, search, settings


def note(w, h, vis, title, kicker):
    return f"""
		<control type="group">
			<left>{(1920 - w) // 2}</left>
			<top>{(1080 - h) // 2}</top>
			<width>{w}</width>
			<height>{h}</height>
			<visible>{vis}</visible>
			<include content="Fold_GenericDialog">
				<param name="header_label" value="{title}"/>
				<param name="kicker" value="{kicker}"/>
			</include>
		</control>"""


def panel():
    notes = "".join(note(PANEL_W, LIST_TOP + n * ROW_H + 24,
                         f"String.IsEmpty({CONF}) + Integer.IsEqual(Container(100).NumItems,{n})",
                         "$VAR[Fold_Lib_Title]", "$VAR[Fold_Lib_Caption]") for n in range(1, MAXROWS + 1))
    full_h = LIST_TOP + MAXROWS * ROW_H + 24
    slides = "".join(
        f"""
			<animation effect="slide" start="0,0" end="0,{(MAXROWS - n) * ROW_H // 2}" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>"""
        for n in range(1, MAXROWS))
    conf_h = LIST_TOP + 80 + 2 * ROW_H + 24
    conf_vis = f"!String.IsEmpty({CONF})"
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
	<controls>{notes}{note(PANEL_W, conf_h, conf_vis, '$VAR[Fold_Lib_ConfirmTitle]', '$VAR[Fold_Lib_Caption]')}
		<control type="group">
			<left>{(1920 - PANEL_W) // 2}</left>
			<top>{(1080 - full_h) // 2}</top>
			<width>{PANEL_W}</width>
			<height>{full_h}</height>
			<visible>String.IsEmpty({CONF})</visible>{slides}
			<control type="list" id="100">
				<left>dialog_inset</left>
				<top>{LIST_TOP}</top>
				<width>{PANEL_W - 48}</width>
				<height>{MAXROWS * ROW_H}</height>
				<onup>100</onup>
				<ondown>100</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="{PANEL_W - 48}"/>
					<param name="height" value="{ROW_H}"/>
					<param name="list_id" value="100"/>
				</include>
				<content>{''.join(PANEL_ITEMS)}
				</content>
			</control>
		</control>
		<!-- the confirm note for Clean (focus starts on No); no <visible> on the group, a hidden parent stops
		     SetFocus(101) (LESSONS Void 0.9.3) -->
		<control type="group">
			<left>{(1920 - PANEL_W) // 2}</left>
			<top>{(1080 - conf_h) // 2}</top>
			<width>{PANEL_W}</width>
			<height>{conf_h}</height>
			<control type="textbox">
				<left>dialog_pad</left>
				<top>{LIST_TOP}</top>
				<width>{PANEL_W - 80}</width>
				<height>70</height>
				<font>body_24</font>
				<textcolor>body</textcolor>
				<selectedcolor>body</selectedcolor>
				<label>Kodi removes every entry whose file it can no longer find. It can't be undone.</label>
				<visible>{conf_vis}</visible>
			</control>
			<control type="list" id="101">
				<left>dialog_inset</left>
				<top>{LIST_TOP + 80}</top>
				<width>{PANEL_W - 48}</width>
				<height>{2 * ROW_H}</height>
				<onup>101</onup>
				<ondown>101</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<visible allowhiddenfocus="true">{conf_vis}</visible>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="{PANEL_W - 48}"/>
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
NODE = ("Container.Content(genres) | Container.Content(years) | Container.Content(actors) | Container.Content(directors) | "
        "Container.Content(studios) | Container.Content(countries) | Container.Content(tags)")
SHELF_V = "[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(musicvideos)]"
SERIES = "[Container.Content(tvshows) | Container.Content(seasons) | Container.Content(episodes)]"


def isv(label):
    return f"String.IsEqual(Container.Viewmode,{label})"


IS_LIST = (f"!{isv('Shelf')} + !{isv('Seasons')} + !{isv('Concertina')} + !{isv('Sleeves')} + !{isv('Table')} + "
           f"!{isv('Leaflet')} + !{isv('Prints')} + !{isv('Crate')} + !{isv('Poster')} + !{isv('Zigzag')}")
# 0.9.13 views (docs/VIEWS_BRIEF_2026-10-27.md): Table 503, Leaflet 505, Prints 506; music Crate 507, Poster 508
TABLE_V = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | "
           "Container.Content(musicvideos) | " + NODE + "]")
# 0.9.16 (docs/VIEWS_PER_SECTION_2026-10-28.md): Accordion 509 for films / series; Table for genres / years / people;
# Crate + Poster for songs
ACC_V = "[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(musicvideos)]"
MUS3 = "[Container.Content(albums) | Container.Content(artists) | Container.Content(songs)]"
LEAF_V = ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | "
          "Container.Content(episodes) | Container.Content(musicvideos)]")

VIEWS = [
    (500, "Shelf", "shelf_films", f"{V} + {SHELF_V} + !{SERIES}", f"{V} + {isv('Shelf')}"),
    (500, "Shelf", "shelf_series", f"{V} + Container.Content(tvshows)", f"{V} + {isv('Shelf')}"),
    (501, "Cards", "seasons", f"{V} + Container.Content(seasons)", f"{V} + {isv('Seasons')}"),
    (502, "Strip", "strip", f"{V} + Container.Content(episodes)", f"{V} + {isv('Concertina')}"),
    (503, "Table", "table", f"{V} + {TABLE_V}", f"{V} + {isv('Table')}"),
    (505, "Leaflet", "leaflet", f"{V} + {LEAF_V}", f"{V} + {isv('Leaflet')}"),
    (506, "Prints", "prints", V, f"{V} + {isv('Prints')}"),
    (509, "Zigzag", "accordion", f"{V} + {ACC_V}", f"{V} + {isv('Zigzag')}"),
    (50, "List", "list", V, f"{V} + {IS_LIST}"),
    (504, "Sleeves", "sleeves", f"{M} + [Container.Content(albums) | Container.Content(artists)]", f"{M} + {isv('Sleeves')}"),
    (507, "Crate", "crate", f"{M} + {MUS3}", f"{M} + {isv('Crate')}"),
    (508, "Poster", "poster", f"{M} + {MUS3}", f"{M} + {isv('Poster')}"),
    (50, "List", "list_music", M, f"{M} + {IS_LIST}"),
]
# 0.9.13: up to five previews side by side (films: Shelf, Table, Leaflet, Prints, List); the note is as wide as the
# views on offer (one frame per count, the list slid to the middle)
CARD_W, CARD_H = 300, 236   # slot: 24 + 256 x 144 preview + 12 + name 48
PRE_W, PRE_H = 256, 144
MAXN = 6   # 0.9.16: films / series offer six (1880 px note)


def picker():
    # the current view comes first (focus starts on it; Control.Move in <onload> or one AlarmClock tick later
    # never moved the list on the Shield), then the others in their usual order
    entries = [(vid, name, pre, vis, f"[{now}]", "Now") for vid, name, pre, vis, now in VIEWS] + \
              [(vid, name, pre, vis, f"![{now}]", "") for vid, name, pre, vis, now in VIEWS]
    items = "".join(f"""
					<item>
						<label>{name}</label>
						<label2>{mark}</label2>
						<icon>fold/views/{pre}.png</icon>
						<visible>{esc(vis)} + {cur}</visible>
						<onclick>Dialog.Close(1156,true)</onclick>
						<onclick>Container.SetViewMode({vid})</onclick>
					</item>""" for vid, name, pre, vis, cur, mark in entries)
    nowvars = ""
    # a static list keeps its selected row between openings: start on the first (= current) view every time
    onload = "\n\t<onload>SetFocus(100,0,absolute)</onload>"

    def layout(focused):
        lift = f"""
						<animation type="Focus" condition="!Skin.HasSetting(fold.reducemotion)">
							<effect type="zoom" start="100" end="104" center="{PRE_W // 2},{PRE_H}" time="180" tween="sine" easing="out"/>
						</animation>
						<animation type="Conditional" condition="Skin.HasSetting(fold.reducemotion) + Control.HasFocus(100)">
							<effect type="zoom" start="104" end="104" center="{PRE_W // 2},{PRE_H}" time="0"/>
						</animation>""" if focused else ""
        shadow = "fold/shadow_lift_s.png" if focused else "fold/shadow_card.png"
        return f"""
					<control type="group">
						<left>24</left>
						<top>16</top>{lift}
						<control type="image">
							<left>-24</left>
							<top>-20</top>
							<width>{PRE_W + 48}</width>
							<height>{PRE_H + 48}</height>
							<texture border="40" colordiffuse="$VAR[Shelf_ShadowTint]">{shadow}</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{PRE_W}</width>
							<height>{PRE_H}</height>
							<texture>$INFO[ListItem.Icon]</texture>
						</control>{'''
						<control type="image">
							<left>0</left>
							<top>%d</top>
							<width>%d</width>
							<height>6</height>
							<texture colordiffuse="$VAR[FoldAccent]">common/white.png</texture>
							<visible>Control.HasFocus(100)</visible>
						</control>''' % (PRE_H, PRE_W) if focused else ''}
						<control type="group">
							<left>{PRE_W - 84}</left>
							<top>10</top>
							<visible>!String.IsEmpty(ListItem.Label2)</visible>
							<control type="image">
								<left>0</left>
								<top>0</top>
								<width>74</width>
								<height>34</height>
								<texture border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texture>
							</control>
							<control type="label">
								<left>0</left>
								<top>0</top>
								<width>74</width>
								<height>34</height>
								<align>center</align>
								<aligny>center</aligny>
								<font>caps_20_b</font>
								<textcolor>$VAR[FoldOnAccent]</textcolor>
								<label>$INFO[ListItem.Label2]</label>
							</control>
						</control>
						<control type="label">
							<left>0</left>
							<top>{PRE_H + 14}</top>
							<width>{PRE_W}</width>
							<height>44</height>
							<font>head_34</font>
							<textcolor>{'$VAR[FoldAccentInk]' if focused else 'ink2'}</textcolor>
							<label>$INFO[ListItem.Label]</label>
						</control>
					</control>"""
    def note_w(n):
        return max(n, 2) * CARD_W + 2 * 24 + 32
    total_w = note_w(MAXN)
    h = LIST_TOP + CARD_H + 16
    frames = "".join(f"""
			<control type="group">
				<left>{(total_w - note_w(n)) // 2}</left>
				<top>0</top>
				<width>{note_w(n)}</width>
				<height>{h}</height>
				<visible>{'Integer.IsEqual(Container(100).NumItems,%d)' % n if n < MAXN else 'Integer.IsGreaterOrEqual(Container(100).NumItems,%d)' % n}</visible>
				<include content="Fold_GenericDialog">
					<param name="header_label" value="View"/>
					<param name="kicker" value="OK switches"/>
				</include>
			</control>""" for n in range(1, MAXN + 1))
    slides = "".join(f"""
				<animation effect="slide" start="0,0" end="{(MAXN - max(n, 2)) * CARD_W // 2},0" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>""" for n in range(1, MAXN))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file. -->
<!--{__doc__}-->
<window type="dialog" id="1156">
	<defaultcontrol always="true">100</defaultcontrol>{onload}
	<include>Anim_DialogOpenClose</include>
	<controls>
		<control type="group">
			<left>{(1920 - total_w) // 2}</left>
			<top>{(1080 - h) // 2}</top>
			<width>{total_w}</width>
			<height>{h}</height>{frames}
			<control type="list" id="100">
				<left>16</left>
				<top>{LIST_TOP - 4}</top>
				<width>{MAXN * CARD_W + 32}</width>{slides}
				<height>{CARD_H + 8}</height>
				<orientation>horizontal</orientation>
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
	</controls>
</window>
""", nowvars


def variables(nowvars):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_panel.py - edit the generator, not this file.
     Labels for the Library panel (Custom_1155) and the view picker (Custom_1156). -->
<includes>
	<variable name="Fold_Lib_Title">
		<value condition="{HOME} + {PCLEAN}">$LOCALIZE[14247]</value>
		<value condition="{HOME}">$LOCALIZE[653]</value>
		<value>Library</value>
	</variable>
	<variable name="Fold_Lib_Caption">
		<value condition="{M}">$LOCALIZE[2]</value>
		<value condition="{V} + [Container.Content(tvshows) | Container.Content(seasons) | Container.Content(episodes)]">Series</value>
		<value condition="{V} + [Container.Content(movies) | Container.Content(sets)]">Films</value>
		<value condition="{V}">$LOCALIZE[3]</value>
		<value>Videos · music</value>
	</variable>
	<variable name="Fold_Lib_Kind">
		<value condition="{M}">$LOCALIZE[2]</value>
		<value>Films · series</value>
	</variable>
	<variable name="Fold_Lib_UpdateLabel">
		<value condition="[{V} + Library.IsScanningVideo] | [{M} + Library.IsScanningMusic]">Stop the update</value>
		<value>$LOCALIZE[653]</value>
	</variable>
	<variable name="Fold_Lib_UpdateVideoLabel">
		<value condition="Library.IsScanningVideo">Stop the video update</value>
		<value>$LOCALIZE[3]</value>
	</variable>
	<variable name="Fold_Lib_UpdateMusicLabel">
		<value condition="Library.IsScanningMusic">Stop the music update</value>
		<value>$LOCALIZE[2]</value>
	</variable>
	<variable name="Fold_Lib_ViewName">
		<value condition="{isv('Shelf')}">Shelf</value>
		<value condition="{isv('Seasons')}">Cards</value>
		<value condition="{isv('Concertina')}">Strip</value>
		<value condition="{isv('Sleeves')}">Sleeves</value>
		<value condition="{isv('Table')}">Table</value>
		<value condition="{isv('Leaflet')}">Leaflet</value>
		<value condition="{isv('Prints')}">Prints</value>
		<value condition="{isv('Crate')}">Crate</value>
		<value condition="{isv('Poster')}">Poster</value>
		<value>List</value>
	</variable>
	<variable name="Fold_Lib_HideWatched">
		<value condition="System.Setting(hidewatched)">On</value>
		<value>Off</value>
	</variable>
	<variable name="Fold_Lib_ConfirmTitle">
		<value condition="String.IsEqual({CONF},music)">Clean the music library?</value>
		<value>Clean the video library?</value>
	</variable>{nowvars}
</includes>
"""


def selcol(xml):
    return re.sub(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)",
                  lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", xml)


if __name__ == "__main__":
    (ROOT / "Custom_1155_LibraryPanel.xml").write_text(finish_xml(strip_defaults(selcol(panel()), ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    xml, nowvars = picker()
    (ROOT / "Custom_1156_ViewPicker.xml").write_text(finish_xml(strip_defaults(selcol(xml), ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    (ROOT / "Includes_Library.xml").write_text(finish_xml(variables(nowvars)), encoding="utf-8", newline="\n")
    print("wrote Custom_1155_LibraryPanel.xml, Custom_1156_ViewPicker.xml, Includes_Library.xml")
