"""Generate skin.orbit/1080i/Custom_1160_LibraryPanel.xml and Custom_1161_ViewPicker.xml (Library panel + view picker,
docs/requests/library-panel/BRIEF.md). Run:  python skins/skin.orbit/_src/make_library_panel.py
The panel's static rows (library / Home update / Home clean modes), the card frames sized per row count, and the
picker's "open on the current view" table (SetFocus(100,k,absolute), k = place of the current view among the views
valid for the folder; positions are 0-based; Kodi restores a dialog list's last selection otherwise).
Variables and the picker card: 1080i/Includes_LibraryPanel.xml (hand-written).
"""
import re
from itertools import product
from pathlib import Path



def items(prefix, video_word, ind="\t\t\t\t\t", direction_var="VidLib_Direction", watched_var="LibPanel_Watched",
          search="ActivateWindow(1150)", words=None):
    w = dict(view="$LOCALIZE[31011]", sort="$LOCALIZE[31010]", order="$LOCALIZE[31300]", watched="$LOCALIZE[31301]", search="$LOCALIZE[31302]",
             update="$LOCALIZE[31202]", stop="$LOCALIZE[31303]", clean="$LOCALIZE[31204]",
             settings="$LOCALIZE[31304]", kodi="Kodi", music="$LOCALIZE[31305]", upd_short="$LOCALIZE[31306]", cln_short="$LOCALIZE[31307]",
             sets="$LOCALIZE[20434]", sets_hint="$LOCALIZE[31308]")
    if words:
        w.update(words)
    lib = f"String.IsEmpty(Window(Home).Property({prefix}.libmode))"
    noplug = "String.IsEmpty(Container.PluginName) + !Container.Content(addons)"
    out = []

    def item(label, label2, clicks, visible):
        out.append(f"{ind}<item>")
        out.append(f"{ind}\t<label>{label}</label>")
        if label2:
            out.append(f"{ind}\t<label2>{label2}</label2>")
        for cl in clicks:
            if isinstance(cl, tuple):
                out.append(f'{ind}\t<onclick condition="{cl[0]}">{cl[1]}</onclick>')
            else:
                out.append(f"{ind}\t<onclick>{cl}</onclick>")
        out.append(f"{ind}\t<visible>{visible}</visible>")
        out.append(f"{ind}</item>")

    close = "Dialog.Close(1160,true)"
    out.append(f"{ind}<!-- ===== the library underneath ({prefix}.libmode empty) ===== -->")
    item(w["view"], "$INFO[Container.Viewmode]", [close, "ActivateWindow(1161)"],
         f"{lib} + Integer.IsGreater(Container.ViewCount,1)")
    item(w["sort"], "$INFO[Container.SortMethod]", [close, "SendClick(3)"],
         f"{lib} + !String.IsEmpty(Container.SortMethod)")
    item(w["order"], f"$VAR[{direction_var}]", [close, ("Window.IsActive(videos)", "SendClick(4)"),
                                                 ("!Window.IsActive(videos)", "Container.SetSortDirection")],
         f"{lib} + !String.IsEmpty(Container.SortMethod)")
    item(w["watched"], f"$VAR[{watched_var}]", [close, "SendClick(14)"],
         f"{lib} + Window.IsActive(videos) + !String.StartsWith(Container.FolderPath,videodb://inprogresstvshows) + "
         "[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | "
         "Container.Content(episodes) | Container.Content(musicvideos)]")
    # Sets (docs/requests/SETS_AND_RM_BRIEF.md, 2026-10-21): the films' sets in this same Videos window, only while
    # browsing films and the library has sets ($EXP[LibPanel_ShowSets], Includes_LibraryPanel.xml). SetFocus(50) first
    # puts focus on the view (CGUIMediaWindow redirects 50 to the current view); Container.Update keeps the history,
    # so Back walks set -> all sets -> films. Never a Home item (Omar).
    item(w["sets"], w["sets_hint"], [close, "SetFocus(50)", "Container.Update(videodb://movies/sets/)"],
         f"{lib} + $EXP[LibPanel_ShowSets]")
    item(w["search"], "", [close, search], lib)
    for kind, win, word in (("video", "videos", video_word), ("music", "music", w["music"])):
        scan = "Library.IsScanningVideo" if kind == "video" else "Library.IsScanningMusic"
        item(w["update"], word, [close, f"UpdateLibrary({kind})"], f"{lib} + Window.IsActive({win}) + !{scan} + {noplug}")
        item(w["stop"], word, [close, f"UpdateLibrary({kind})"], f"{lib} + Window.IsActive({win}) + {scan} + {noplug}")
    for kind, win, word in (("video", "videos", video_word), ("music", "music", w["music"])):
        item(w["clean"], word, [f"SetProperty({prefix}.libclean,{kind},home)", "SetFocus(200,0,absolute)"],
             f"{lib} + Window.IsActive({win}) + {noplug}")
    item(w["settings"], w["kodi"], [close, "ActivateWindow(MediaSettings)"], lib)
    out.append(f"{ind}<!-- ===== from the System menu: Update library ===== -->")
    upd = f"String.IsEqual(Window(Home).Property({prefix}.libmode),update)"
    for kind, word in (("video", video_word), ("music", w["music"])):
        scan = "Library.IsScanningVideo" if kind == "video" else "Library.IsScanningMusic"
        item(word, w["upd_short"], [close, f"UpdateLibrary({kind})"], f"{upd} + !{scan}")
        item(word, w["stop"], [close, f"UpdateLibrary({kind})"], f"{upd} + {scan}")
    out.append(f"{ind}<!-- ===== from the System menu: Clean library ===== -->")
    cln = f"String.IsEqual(Window(Home).Property({prefix}.libmode),clean)"
    for kind, word in (("video", video_word), ("music", w["music"])):
        item(word, w["cln_short"], [f"SetProperty({prefix}.libclean,{kind},home)", "SetFocus(200,0,absolute)"], cln)
    return "\n".join(out)


def confirm_items(prefix, no, yes, ind="\t\t\t\t\t"):
    p = f"Window(Home).Property({prefix}.libclean)"
    return "\n".join([
        f"{ind}<item>",
        f"{ind}\t<label>{no}</label>",
        f"{ind}\t<onclick>ClearProperty({prefix}.libclean,home)</onclick>",
        f"{ind}\t<onclick>SetFocus(100)</onclick>",
        f"{ind}</item>",
        f"{ind}<item>",
        f"{ind}\t<label>{yes}</label>",
        f'{ind}\t<onclick condition="String.IsEqual({p},video)">CleanLibrary(video)</onclick>',
        f'{ind}\t<onclick condition="String.IsEqual({p},music)">CleanLibrary(music)</onclick>',
        f"{ind}\t<onclick>Dialog.Close(1160,true)</onclick>",
        f"{ind}</item>"])





def onload_moves(views, ind="\t"):
    # Kodi restores the list's last selected item when the dialog reopens, and Control.Move wraps:
    # select absolutely instead (GUI_MSG_SETFOCUS param2 = 1). First line = item 0 (positions are 0-based).
    out = [f'{ind}<onload>SetFocus(100,0,absolute)</onload>']
    by_win = {}
    for v in views:
        by_win.setdefault(v[0], []).append(v)
    for win, vs in by_win.items():
        for i, (w, vid, label, icon, cond, cur) in enumerate(vs):
            earlier = [x for x in vs[:i]]
            conds = [x[4] for x in earlier]
            opts = [[True] if c is None else [True, False] for c in conds]
            seen = set()
            for combo in product(*opts):
                k = sum(1 for b in combo if b)
                if k == 0:
                    continue
                truth = {}
                ok = True
                if cond:
                    truth[cond] = True
                for c, b in zip(conds, combo):
                    if c is None:
                        continue
                    if truth.get(c, b) != b:
                        ok = False
                    truth[c] = b
                if not ok:
                    continue
                parts = [f"Window.IsActive({win})", f"String.IsEqual(Container.Viewmode,{label})"]
                parts += [f"[{c}]" if b else f"![{c}]" for c, b in truth.items()]
                key = (tuple(parts), k)
                if key in seen:
                    continue
                seen.add(key)
                out.append(f'{ind}<onload condition="{" + ".join(parts)}">SetFocus(100,{k},absolute)</onload>')
    return "\n".join(out)


def picker_items(views, focus_id=50, ind="\t\t\t\t", name_map=None):
    out = []
    for (win, vid, label, icon, cond, cur) in views:
        name = (name_map or {}).get((win, vid), label)
        vis = f"Window.IsActive({win})" + (f" + [{cond}]" if cond else "")
        out += [f"{ind}<item>",
                f"{ind}\t<label>{name}</label>",
                f"{ind}\t<label2>$VAR[{cur}]</label2>",
                f"{ind}\t<icon>{icon}</icon>",
                f"{ind}\t<onclick>Dialog.Close(1161,true)</onclick>",
                f"{ind}\t<onclick>Container.SetViewMode({vid})</onclick>",
                f"{ind}\t<onclick>SetFocus({focus_id})</onclick>",
                f"{ind}\t<visible>{vis}</visible>",
                f"{ind}</item>"]
    return "\n".join(out)


# ---------------------------------------------------------------- orbit_panel.py

SKIN = str(Path(__file__).resolve().parent.parent / "1080i")
P = "orbit"
ROW = 68
TOP = 56

frames = []
NMAX = 10  # 0.9.21: View, Sort, Order, Unwatched only, Sets, Search, Update, Clean, Library settings
for n in range(1, NMAX + 1):
    cond = f"Integer.IsEqual(Container(100).NumItems,{n})" if n < NMAX else f"Integer.IsGreaterOrEqual(Container(100).NumItems,{NMAX})"
    frames.append(f"""			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>600</width>
				<height>{TOP + ROW * n + 12}</height>
				<texture border="2">dialogs/panel_framed.png</texture>
				<visible>String.IsEmpty(Window(Home).Property({P}.libclean)) + {cond}</visible>
			</control>""")
frames.append(f"""			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>600</width>
				<height>{TOP + 150 + 2 * ROW + 16}</height>
				<texture border="2">dialogs/panel_framed.png</texture>
				<visible>!String.IsEmpty(Window(Home).Property({P}.libclean))</visible>
			</control>""")

words = dict(watched="$LOCALIZE[31081]")
body = items(P, "$LOCALIZE[31309]", watched_var="LibPanel_Unwatched", direction_var="LibPanel_Direction", words=words)
conf = confirm_items(P, "$LOCALIZE[31310]", "$LOCALIZE[31311]")

xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	Orbit Library panel (custom dialog 1160; docs/requests/library-panel/BRIEF.md). The library's
	general-purpose menu: View, Sort, Order, Unwatched only, Sets (films), Search, Update library,
	Clean library, Library settings. Opened by the Menu key's "View, sort, filter" row in the library windows (0.9.21, DialogContextMenu.xml), by Right from any library view (arc, grid, episodes, dial list), Left past
	the first pill of the option bar, the OPTIONS pill, and the System menu (Update / Clean library,
	orbit.libmode = update / clean: choose Movies and TV shows or Music).
	Same language as the System menu: navy framed panel, amber mono kicker, numbered rows.
	Kodi's CleanLibrary() has no confirmation of its own, so the panel asks first (list 200, "No"
	focused). Back closes the panel (Kodi's Back); the library keeps the item you came from.
	GENERATED by _src/make_library_panel.py (variables in Includes_LibraryPanel.xml). No Kodi-owned ids.
-->
<window type="dialog" id="1160">
	<defaultcontrol always="true">100</defaultcontrol>
	<include>Anim_DialogOpenClose</include>
	<!-- Kodi restores a dialog list's last selection on reopen: always start on the first row, and
	     the Clean confirmation always on "No" (SetFocus(200,0,absolute) in the Clean rows) -->
	<onload>SetFocus(100,0,absolute)</onload>
	<onunload>ClearProperty({P}.libclean,home)</onunload>
	<onunload>ClearProperty({P}.libmode,home)</onunload>
	<controls>
		<control type="image">
			<description>backdrop dim</description>
			<left>0</left>
			<top>0</top>
			<width>screen_w</width>
			<height>screen_h</height>
			<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
			<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
			<texture colordiffuse="dim_dialog">common/white.png</texture>
		</control>
		<control type="group">
			<left>660</left>
			<top>below_bar_top</top>
			<width>600</width>
			<height>{TOP + ROW * NMAX + 12}</height>
			<!-- frame sized to the visible rows -->
{chr(10).join(frames)}
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>552</width>
				<height>56</height>
				<font>mono_13</font>
				<textcolor>accent</textcolor>
				<label>$VAR[LibPanel_Kicker]</label>
			</control>
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>552</width>
				<height>56</height>
				<align>right</align>
				<font>num_14</font>
				<textcolor>text_tertiary</textcolor>
				<label>$VAR[LibPanel_Where]</label>
				<visible>String.IsEmpty(Window(Home).Property({P}.libmode))</visible>
			</control>
			<control type="list" id="100">
				<left>12</left>
				<top>{TOP}</top>
				<width>576</width>
				<height>{ROW * NMAX}</height>
				<onup>100</onup>
				<ondown>100</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<visible allowhiddenfocus="true">String.IsEmpty(Window(Home).Property({P}.libclean))</visible>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="576"/>
					<param name="height" value="{ROW}"/>
					<param name="list_id" value="100"/>
				</include>
				<content>
{body}
				</content>
			</control>
			<!-- Clean library: ask first ("No" is focused) -->
			<control type="textbox">
				<left>24</left>
				<top>{TOP + 8}</top>
				<width>552</width>
				<height>136</height>
				<font>text_24</font>
				<textcolor>text_secondary</textcolor>
				<label>$VAR[LibPanel_CleanText]</label>
				<visible>!String.IsEmpty(Window(Home).Property({P}.libclean))</visible>
			</control>
			<control type="list" id="200">
				<left>12</left>
				<top>{TOP + 150}</top>
				<width>576</width>
				<height>{ROW * 2}</height>
				<onup>200</onup>
				<ondown>200</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<visible allowhiddenfocus="true">!String.IsEmpty(Window(Home).Property({P}.libclean))</visible>
				<include content="Dlg_IndexListLayout">
					<param name="width" value="576"/>
					<param name="height" value="{ROW}"/>
					<param name="list_id" value="200"/>
				</include>
				<content>
{conf}
				</content>
			</control>
		</control>
	</controls>
</window>
"""
open(SKIN + "/Custom_1160_LibraryPanel.xml", "w", encoding="utf-8", newline="\n").write(xml)
print("ok")

# ---------------------------------------------------------------- orbit_picker.py

SKIN = str(Path(__file__).resolve().parent.parent / "1080i")
ARC = "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(musicvideos)"
EPI = "Container.Content(episodes) | Container.Content(seasons)"
MARC = "Container.Content(albums) | Container.Content(artists)"
MGRID = "Container.Content(albums) | Container.Content(artists) | Container.Content(genres)"
VIEWS = [
    ("videos", 500, "$LOCALIZE[31312]", "views/arc.png", ARC, "Pick_Cur_Arc"),
    ("videos", 501, "$LOCALIZE[31313]", "views/grid.png", ARC + " | Container.Content(genres)", "Pick_Cur_Grid"),
    ("videos", 502, "$LOCALIZE[31314]", "views/episodes.png", ARC + " | Container.Content(episodes)", "Pick_Cur_Episodes"),
    ("videos", 503, "$LOCALIZE[31320]", "views/horizon.png", ARC + " | Container.Content(episodes)", "Pick_Cur_Horizon"),
    ("videos", 506, "$LOCALIZE[31321]", "views/tiles.png", None, "Pick_Cur_Tiles"),
    ("videos", 50, "$LOCALIZE[535]", "views/list.png", None, "Pick_Cur_List"),
    ("music", 504, "$LOCALIZE[31312]", "views/music_arc.png", MARC, "Pick_Cur_Arc"),
    ("music", 505, "$LOCALIZE[31313]", "views/music_grid.png", MGRID + " | Container.Content(songs)", "Pick_Cur_Grid"),
    ("music", 507, "$LOCALIZE[31320]", "views/music_horizon.png", MARC + " | Container.Content(songs)", "Pick_Cur_Horizon"),
    ("music", 50, "$LOCALIZE[535]", "views/music_list.png", None, "Pick_Cur_List"),
]
# 0.9.19 (docs/VIEWS_PER_SECTION_2026-10-28.md): Grid 501 also genres, Episodes 502 also films / sets / shows / music
# videos (with seasons and episodes: the same condition as Horizon 503), music Grid 505 and Horizon 507 also songs.
# 0.9.16 (docs/VIEWS_BRIEF_2026-10-27.md): Horizon 503 / 507 and Tiles 506. Seasons offer six views (Arc, Grid,
# Episodes, Horizon, Tiles, List), so the card holds six smaller previews (260 x 146) side by side.
PITCH = 300
MAXN = 6
# display names (localized); VIEWS keeps the viewtype labels (string ids) that Container.Viewmode is compared with
names = {("videos", 500): "$LOCALIZE[31312]", ("videos", 501): "$LOCALIZE[31313]", ("videos", 502): "$LOCALIZE[31314]", ("videos", 50): "$LOCALIZE[31315]",
         ("videos", 503): "$LOCALIZE[31320]", ("videos", 506): "$LOCALIZE[31321]",
         ("music", 504): "$LOCALIZE[31312]", ("music", 505): "$LOCALIZE[31313]", ("music", 507): "$LOCALIZE[31320]",
         ("music", 50): "$LOCALIZE[31315]"}

frames = []
for n in range(1, MAXN + 1):
    w = n * PITCH + 40
    frames.append(f"""			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>{w}</width>
				<height>340</height>
				<texture border="2">dialogs/panel_framed.png</texture>
				<visible>Integer.IsEqual(Container(100).NumItems,{n})</visible>
			</control>""")
slides = []
for n in range(1, MAXN):
    slides.append(f'\t\t\t<animation effect="slide" end="{(MAXN - n) * PITCH // 2},0" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>')

xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	Orbit view picker (custom dialog 1161; docs/requests/library-panel/BRIEF.md). Opened by the VIEW
	pill of the option bar and View in the Library panel. One schematic preview per view valid for the
	content underneath (the views' own Container.Content conditions), its name and an amber dot +
	"current" under the view on screen. OK = Container.SetViewMode(id), closes, focus back on the view;
	Back closes with no change. Previews: media/views/ (_src/make_view_previews.py). Opens on the
	current view: SetFocus(100,k,absolute), k = its place among the views valid here (generated table).
	The panel centres itself on the number of cards (Container(100).NumItems counts visible items).
	GENERATED by _src/make_library_panel.py.
-->
<window type="dialog" id="1161">
	<defaultcontrol always="true">100</defaultcontrol>
	<include>Anim_DialogOpenClose</include>
{onload_moves(VIEWS)}
	<controls>
		<control type="image">
			<description>backdrop dim</description>
			<left>0</left>
			<top>0</top>
			<width>screen_w</width>
			<height>screen_h</height>
			<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
			<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
			<texture colordiffuse="dim_dialog">common/white.png</texture>
		</control>
		<control type="group">
			<left>{(1920 - MAXN * PITCH - 40) // 2}</left>
			<top>370</top>
			<width>{MAXN * PITCH + 40}</width>
			<height>340</height>
{chr(10).join(slides)}
{chr(10).join(frames)}
			<control type="label">
				<left>24</left>
				<top>0</top>
				<width>600</width>
				<height>56</height>
				<font>mono_13</font>
				<textcolor>accent</textcolor>
				<label>View  ·  $VAR[LibPanel_Where]</label>
			</control>
			<control type="list" id="100">
				<left>20</left>
				<top>56</top>
				<width>{MAXN * PITCH}</width>
				<height>270</height>
				<orientation>horizontal</orientation>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<onup>noop</onup>
				<ondown>noop</ondown>
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<itemlayout width="{PITCH}" height="270">
					<include>Pick_Item</include>
				</itemlayout>
				<focusedlayout width="{PITCH}" height="270">
					<include content="Pick_Item"><param name="focused" value="true"/></include>
				</focusedlayout>
				<content>
{picker_items(VIEWS, name_map=names)}
				</content>
			</control>
		</control>
	</controls>
</window>
"""
open(SKIN + "/Custom_1161_ViewPicker.xml", "w", encoding="utf-8", newline="\n").write(xml)
