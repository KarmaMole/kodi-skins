"""Writes Majan's library dialogs (request docs/requests/library-panel, 1.0.9):
  1080i/Custom_1155_LibraryPanel.xml   the numbered Library panel (OPTIONS, Left/Right past a view's edges)
  1080i/Custom_1156_ViewPicker.xml     the view picker with schematic previews (media/majan/views)
  1080i/Custom_1157_LibraryTask.xml    Update / Clean with the choice of library and the confirmation
Labels and expressions live in 1080i/Includes_Library.xml. Run: python make_library_dialogs.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "1080i"
INPROG = "String.StartsWith(Container.FolderPath,videodb://inprogresstvshows)"


def panels(width, base, lo, hi, pitch=68, indent="\t\t\t"):
    """One framed panel per visible-row count (Container(100).NumItems counts visible static items only)."""
    out = []
    for n in range(lo, hi + 1):
        if n == lo:
            cond = f"!Integer.IsGreater(Container(100).NumItems,{n})"
        elif n == hi:
            cond = f"Integer.IsGreaterOrEqual(Container(100).NumItems,{n})"
        else:
            cond = f"Integer.IsEqual(Container(100).NumItems,{n})"
        out.append(f"""{indent}<control type="image">
{indent}	<left>0</left>
{indent}	<top>0</top>
{indent}	<width>{width}</width>
{indent}	<height>{base + pitch * n}</height>
{indent}	<texture border="2">dialogs/panel_framed.png</texture>
{indent}	<visible>{cond}</visible>
{indent}</control>""")
    return "\n".join(out)


def item(label, label2, onclicks, visible=None, props=None, icon=None):
    t = "\t\t\t\t\t"
    lines = [f"{t}<item>", f"{t}\t<label>{label}</label>"]
    if label2:
        lines.append(f"{t}\t<label2>{label2}</label2>")
    if icon:
        lines.append(f"{t}\t<icon>{icon}</icon>")
    for k, v in (props or {}).items():
        lines.append(f'{t}\t<property name="{k}">{v}</property>')
    for oc in onclicks:
        if isinstance(oc, tuple):
            lines.append(f'{t}\t<onclick condition="{oc[0]}">{oc[1]}</onclick>')
        else:
            lines.append(f"{t}\t<onclick>{oc}</onclick>")
    if visible:
        lines.append(f"{t}\t<visible>{visible}</visible>")
    lines.append(f"{t}</item>")
    return "\n".join(lines)


DIM = """		<control type="image">
			<description>backdrop dim (own fades: LESSONS 4)</description>
			<left>0</left>
			<top>0</top>
			<width>screen_w</width>
			<height>screen_h</height>
			<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
			<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
			<texture colordiffuse="dim_dialog">common/white.png</texture>
		</control>"""


def heading(left_label, right_label=None, width=600):
    s = f"""			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>{width - 48}</width>
				<height>56</height>
				<font>num_22</font>
				<textcolor>$VAR[ColorAccent]</textcolor>
				<label>{left_label}</label>
			</control>"""
    if right_label:
        s += f"""
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>{width - 48}</width>
				<height>56</height>
				<align>right</align>
				<font>num_22</font>
				<textcolor>text_tertiary</textcolor>
				<label>{right_label}</label>
			</control>"""
    return s


def rows(list_id, top, height, items_xml):
    return f"""			<control type="list" id="{list_id}">
				<left>12</left>
				<top>{top}</top>
				<width>576</width>
				<height>{height}</height>
				<onup>{list_id}</onup>
				<ondown>{list_id}</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="576"/>
					<param name="height" value="68"/>
					<param name="list_id" value="{list_id}"/>
					<param name="index_font" value="num_22"/>
					<param name="hint_font" value="num_22"/>
					<param name="hint_w" value="230"/>
				</include>
				<content>
{items_xml}
				</content>
			</control>"""


def panel():
    c = "Dialog.Close(1155,true)"
    m = "$EXP[MJ_LibInMusic]"
    items = [
        item("$VAR[MJ_LibUpdateLabel]", "$VAR[MJ_LibUpdateHint]",
             [c, (m, "UpdateLibrary(music)"), ("!" + m, "UpdateLibrary(video)")], "$EXP[MJ_LibCanUpdate]"),
        item("$LOCALIZE[31202]", "$LOCALIZE[31300]",
             ["SetProperty(majan.libtask,clean,home)", (m, "SetProperty(majan.libtarget,music,home)"),
              ("!" + m, "SetProperty(majan.libtarget,video,home)"), c, "ActivateWindow(1157)"], "$EXP[MJ_LibCanUpdate]"),
        item("$LOCALIZE[31011]", "[UPPERCASE]$INFO[Container.Viewmode][/UPPERCASE]", [c, "ActivateWindow(1156)"],
             "Integer.IsGreater(Container.ViewCount,1)"),
        item("$LOCALIZE[31010]", "[UPPERCASE]$INFO[Container.SortMethod][/UPPERCASE]", [c, "SendClick(3)"],
             "!String.IsEmpty(Container.SortMethod)"),
        item("$LOCALIZE[31301]", "$VAR[MJ_LibOrderHint]", [c, (m, "Container.SetSortDirection"), ("!" + m, "SendClick(4)")],
             "!String.IsEmpty(Container.SortMethod)"),
        item("$LOCALIZE[31302]", "$VAR[MJ_LibShowHint]", [c, "SendClick(14)"], "$EXP[MJ_LibHasWatchedFilter]"),
        # Sets (2026-10-21, docs/requests/SETS_AND_RM_BRIEF.md): the films' sets in this same Videos window.
        # Container.Update keeps the history, so Back walks set -> all sets -> films. Never a Home item (Omar).
        # SetFocus(50) first lands on the current view (CGUIMediaWindow), so the sets list has focus.
        item("$LOCALIZE[20434]", "$LOCALIZE[31303]", [c, "SetFocus(50)", "Container.Update(videodb://movies/sets/)"],
             "$EXP[MJ_LibShowSets]"),
        item("$LOCALIZE[137]", "", [c, "ActivateWindow(1150)"]),
        item("$LOCALIZE[31304]", "KODI", [c, "ActivateWindow(MediaSettings)"]),
    ]
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_dialogs.py - edit the generator, not this file.
	Majan Library panel (custom dialog 1155, request docs/requests/library-panel; Sets row 1.0.10). Opened by the header's
	OPTIONS word and by Left past the first item / Right past the last one in every library view. Drops
	under the header at the right (x 1224, the end of the filter bar), the System menu's numbered Index
	rows (Dlg_IndexListLayout, labels of 20 px and more). Only the rows that apply: Update / Clean hide in
	add-on and plug-in folders (as Estuary's menu 9000), Show only where Kodi's watched filter works, View
	only with more than one view. Every row closes the panel, then runs what the header words run
	(SendClick(3) sort, SendClick(4) / Container.SetSortDirection order, SendClick(14) watched filter).
	Back closes it and focus is back on the item you came from. -->
<window type="dialog" id="1155">
	<defaultcontrol always="true">100</defaultcontrol>
	<!-- always open on the first row (Kodi keeps a list's selected item between visits; Control.Move wraps:
	     -CurrentItem lands on the last row, +1 on the first) -->
	<onload>Control.Move(100,-$INFO[Container(100).CurrentItem])</onload>
	<onload>Control.Move(100,1)</onload>
	<include>Anim_DialogOpenClose</include>
	<controls>
{DIM}
		<control type="group">
			<left>1224</left>
			<top>below_bar_top</top>
			<width>600</width>
			<height>680</height>
			<!-- panel sized to the visible rows: 56 heading + 68 per row + 12 (9 rows end at y 816) -->
{panels(600, 68, 2, 9)}
{heading("$LOCALIZE[31305]", "$VAR[MJ_LibCaption]")}
{rows(100, 56, 612, chr(10).join(items))}
		</control>
	</controls>
</window>
"""
    (OUT / "Custom_1155_LibraryPanel.xml").write_text(xml, encoding="utf-8", newline="\n")


def task():
    t = "Dialog.Close(1157,true)"
    tk = "String.IsEqual(Window(Home).Property(majan.libtask),{})"
    tg = "String.IsEqual(Window(Home).Property(majan.libtarget),{})"
    clean, upd = tk.format("clean"), tk.format("update")
    vid = f"[{tg.format('video')} | {tg.format('choose')}]"
    mus = f"[{tg.format('music')} | {tg.format('choose')}]"
    items = [
        item("$LOCALIZE[31314]", "", [t], clean),
        item("$LOCALIZE[31315]", "$LOCALIZE[31316]", [t, "CleanLibrary(video)"], f"{clean} + {vid}"),
        item("$LOCALIZE[31317]", "$LOCALIZE[31318]", [t, "CleanLibrary(music)"], f"{clean} + {mus}"),
        item("$VAR[MJ_TaskUpdateVideo]", "$LOCALIZE[31316]", [t, "UpdateLibrary(video)"], f"{upd} + {vid}"),
        item("$VAR[MJ_TaskUpdateMusic]", "$LOCALIZE[31318]", [t, "UpdateLibrary(music)"], f"{upd} + {mus}"),
    ]
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_dialogs.py - edit the generator, not this file.
	Majan library task panel (custom dialog 1157): Update or Clean, with the choice of library (from Home's
	System menu) and the confirmation for Clean. Kodi's CleanLibrary() builtin cleans without asking (Kodi 21
	LibraryBuiltins.cpp has no yes/no), so this panel is the question: "No, leave it as it is" comes first and
	has focus; Back closes it without doing anything. UpdateLibrary() during an update stops it, so those
	rows say "Stop updating" then.
	Window(Home).Property(majan.libtask) = update | clean, majan.libtarget = video | music | choose. -->
<window type="dialog" id="1157">
	<defaultcontrol always="true">100</defaultcontrol>
	<!-- always open on the first row (Kodi keeps a list's selected item between visits; Control.Move wraps:
	     -CurrentItem lands on the last row, +1 on the first) - here that is the safe No -->
	<onload>Control.Move(100,-$INFO[Container(100).CurrentItem])</onload>
	<onload>Control.Move(100,1)</onload>
	<include>Anim_DialogOpenClose</include>
	<controls>
{DIM}
		<control type="group">
			<left>1224</left>
			<top>below_bar_top</top>
			<width>600</width>
			<height>480</height>
			<!-- 56 heading + 120 text + 68 per row + 12 -->
{panels(600, 188, 2, 3)}
{heading("$VAR[MJ_TaskHeading]")}
			<control type="textbox">
				<left>24</left>
				<top>60</top>
				<width>552</width>
				<height>97</height>
				<font>body_23</font>
				<label>$VAR[MJ_TaskBody]</label>
			</control>
{rows(100, 176, 204, chr(10).join(items))}
		</control>
	</controls>
</window>
"""
    (OUT / "Custom_1157_LibraryTask.xml").write_text(xml, encoding="utf-8", newline="\n")


V = "Window.IsVisible(videos)"
M = "Window.IsVisible(music)"
# (key, label, preview, visible = the view's own visible condition, view id). 1.0.18: one view can have two picker
# entries with exclusive visibility when it reads differently per content (501 = "Big still" for episodes, 503 =
# "Rows" outside TV); MJ_PickCurrent matches both entries on the view's own viewtype label.
C = "Container.Content"
NAME = "$EXP[VidView_IsNameNode]"
FILMS_TV = f"{C}(movies) | {C}(sets) | {C}(tvshows) | {C}(seasons)"
PICKS = [
    ("showcase", "$LOCALIZE[31306]", "showcase", f"{V} + [{FILMS_TV}]", 500),
    ("bigposter", "$LOCALIZE[31307]", "bigposter", f"{V} + [{FILMS_TV}]", 501),
    ("bigstill", "$LOCALIZE[31324]", "bigstill", f"{V} + {C}(episodes)", 501),
    ("tvwall", "$LOCALIZE[31308]", "tvwall", f"{V} + [{C}(tvshows) | {C}(seasons)]", 502),
    ("episodes", "$LOCALIZE[31309]", "episodes", f"{V} + [{C}(episodes) | {C}(seasons)]", 503),
    ("rows", "$LOCALIZE[31325]", "rows", f"{V} + [{C}(movies) | {C}(sets) | {C}(tvshows)]", 503),
    ("posterwall", "$LOCALIZE[31310]", "posterwall", f"{V} + [{FILMS_TV} | {NAME}]", 506),
    ("stills", "$LOCALIZE[31322]", "stills", f"{V} + [{C}(episodes) | {FILMS_TV} | {C}(musicvideos) | {NAME}]", 507),
    ("list", "$LOCALIZE[31311]", "list", V, 50),
    ("grid", "$LOCALIZE[31312]", "music_grid", f"{M} + [{C}(albums) | {C}(artists)]", 504),
    ("bigalbum", "$LOCALIZE[31313]", "music_bigalbum", f"{M} + [{C}(albums) | {C}(artists) | {C}(songs)]", 505),
    ("tracklist", "$LOCALIZE[31323]", "music_tracklist", f"{M} + {C}(songs)", 508),
    ("list", "$LOCALIZE[31311]", "music_list", M, 50),
]
# viewtype label each picker entry stands for (Container.Viewmode returns it)
VIEWMODE = {500: 31306, 501: 31307, 502: 31308, 503: 31309, 506: 31310, 507: 31322, 504: 31312, 505: 31313, 508: 31323}
# mutually exclusive content classes per window, and which picker entries each shows (in picker order)
VIDEO_CLASSES = [(f"{C}({c})", c) for c in ("movies", "sets", "tvshows", "seasons", "episodes", "musicvideos")] + [(NAME, "names")]
MUSIC_CLASSES = [(f"{C}({c})", c) for c in ("albums", "artists", "songs")]
SHOWS = {
    "movies": ["showcase", "bigposter", "rows", "posterwall", "stills", "list"],
    "sets": ["showcase", "bigposter", "rows", "posterwall", "stills", "list"],
    "tvshows": ["showcase", "bigposter", "tvwall", "rows", "posterwall", "stills", "list"],
    "seasons": ["showcase", "bigposter", "tvwall", "episodes", "posterwall", "stills", "list"],
    "episodes": ["bigstill", "episodes", "stills", "list"],
    "musicvideos": ["stills", "list"],
    "names": ["posterwall", "stills", "list"],
    "albums": ["grid", "bigalbum", "list"],
    "artists": ["grid", "bigalbum", "list"],
    "songs": ["bigalbum", "tracklist", "list"],
}


def picker_onloads():
    """Land on the view on show: after the reset to the first item, move k places (k = its place among the entries
    this content shows). The list is always last, so it keeps the old Control.Move(100,-1) (wraps to the end)."""
    vid = {k: v for k, _, _, _, v in PICKS}
    out = []
    for win, classes in (("Window.IsVisible(videos)", VIDEO_CLASSES), ("Window.IsVisible(music)", MUSIC_CLASSES)):
        for cond, cls in classes:
            for k, key in enumerate(SHOWS[cls]):
                if k == 0 or key == "list":
                    continue
                vm = VIEWMODE[vid[key]]
                out.append(f'\t<onload condition="String.IsEqual(Container.Viewmode,$LOCALIZE[{vm}]) + {win} + {cond}">Control.Move(100,{k})</onload>')
    out.append('\t<onload condition="$EXP[MJ_PickIsList]">Control.Move(100,-1)</onload>')
    return "\n".join(out)


def check_shows():
    """SHOWS must agree with the entries' own visible conditions (a picker with a wrong count lands off by one)."""
    import re
    for key, _, _, vis, _ in PICKS:
        for cls, keys in SHOWS.items():
            music = cls in ("albums", "artists", "songs")
            if ("Window.IsVisible(music)" in vis) != music and key != "list":
                assert key not in keys, (key, cls)
                continue
            if key == "list":
                continue
            token = NAME if cls == "names" else f"{C}({cls})"
            assert (token in vis) == (key in keys), (key, cls)


def picker():
    check_shows()
    c = "Dialog.Close(1156,true)"
    items = [item(label, "", [c, f"Container.SetViewMode({vid})", "SetFocus(50)"], vis,
                  {"key": key, "accent": f"majan/views/{img}_accent.png"}, f"majan/views/{img}.png")
             for key, label, img, vis, vid in PICKS]
    slides = "\n".join(
        f"""			<animation effect="slide" start="0,0" end="{296 * (4 - n)},0" time="0" condition="{cond}">Conditional</animation>"""
        for n, cond in ((3, "Integer.IsEqual(Container(100).NumItems,3)"), (2, "!Integer.IsGreater(Container(100).NumItems,2)")))
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library_dialogs.py - edit the generator, not this file.
	Majan view picker (custom dialog 1156): the window's views as schematic previews of their real geometry
	(media/majan/views, _src/make_view_previews.py; no artwork), each with its name; the view on show has
	the accent underline of an active tab, focus is the 2 px accent outline. The previews' own accent
	pieces (focus outline, accent bar, page index) are a second white image tinted with the chosen accent.
	OK switches (Container.SetViewMode after the panel has closed, so the new view takes focus), Back keeps
	the view. Only the views the content can show (their own visible conditions; Container.Content reads
	the media window from a dialog). The panel hangs right-aligned under the header (ends at x 1824) and
	slides right by 296 per missing view. Opened by VIEW: in the header and the Library panel's View row. -->
<window type="dialog" id="1156">
	<defaultcontrol always="true">100</defaultcontrol>
	<include>Anim_DialogOpenClose</include>
	<!-- land on the view on show (visible order follows the list below). Kodi keeps the list's selected item between
	     visits, so first go back to the first item: Control.Move wraps, -CurrentItem lands on the last item, +1 on the first -->
	<onload>Control.Move(100,-$INFO[Container(100).CurrentItem])</onload>
	<onload>Control.Move(100,1)</onload>
{picker_onloads()}
	<controls>
{DIM}
		<control type="group">
			<left>600</left>
			<top>below_bar_top</top>
			<width>1224</width>
			<height>320</height>
{slides}
			<!-- 296 per view + 40; the group slides right by 296 per missing view, so the panel ends at x 1824 -->
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1224</width>
				<height>304</height>
				<texture border="2">dialogs/panel_framed.png</texture>
				<visible>Integer.IsGreaterOrEqual(Container(100).NumItems,4)</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>928</width>
				<height>304</height>
				<texture border="2">dialogs/panel_framed.png</texture>
				<visible>Integer.IsEqual(Container(100).NumItems,3)</visible>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>632</width>
				<height>304</height>
				<texture border="2">dialogs/panel_framed.png</texture>
				<visible>!Integer.IsGreater(Container(100).NumItems,2)</visible>
			</control>
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>300</width>
				<height>56</height>
				<font>num_22</font>
				<textcolor>$VAR[ColorAccent]</textcolor>
				<label>$LOCALIZE[31319]</label>
			</control>
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>880</width>
				<height>56</height>
				<align>right</align>
				<font>num_22</font>
				<textcolor>text_tertiary</textcolor>
				<label>$VAR[MJ_LibCaption]</label>
				<visible>Integer.IsEqual(Container(100).NumItems,3)</visible>
			</control>
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>1176</width>
				<height>56</height>
				<align>right</align>
				<font>num_22</font>
				<textcolor>text_tertiary</textcolor>
				<label>$VAR[MJ_LibCaption]</label>
				<visible>Integer.IsGreaterOrEqual(Container(100).NumItems,4)</visible>
			</control>
			<control type="list" id="100">
				<left>20</left>
				<top>56</top>
				<width>1184</width>
				<height>236</height>
				<orientation>horizontal</orientation>
				<onup>noop</onup>
				<ondown>noop</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<include>MJ_PickLayouts</include>
				<content>
{chr(10).join(items)}
				</content>
			</control>
		</control>
	</controls>
</window>
"""
    (OUT / "Custom_1156_ViewPicker.xml").write_text(xml, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    panel()
    task()
    picker()
    print("wrote Custom_1155 / 1156 / 1157")
