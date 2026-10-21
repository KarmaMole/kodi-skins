"""Generate skin.daylight/1080i/Custom_1160_LibraryPanel.xml and Custom_1161_ViewPicker.xml (Library panel + view picker,
docs/requests/library-panel/BRIEF.md). Run:  python skins/skin.daylight/_src/make_library_panel.py
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
             update="$LOCALIZE[31203]", stop="$LOCALIZE[31303]", clean="$LOCALIZE[31205]",
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


# ---------------------------------------------------------------- daylight_gen.py

SKIN = str(Path(__file__).resolve().parent.parent / "1080i")
P = "daylight"
ROW = 68
TOP = 72

# ------------------------------------------------------------------ panel 1160
frames = []
for n in range(1, 10):
    cond = f"Integer.IsEqual(Container(100).NumItems,{n})" if n < 9 else "Integer.IsGreaterOrEqual(Container(100).NumItems,9)"
    frames.append(f"""			<control type="group">
				<left>0</left>
				<top>0</top>
				<width>600</width>
				<height>{TOP + ROW * n + 16}</height>
				<visible>String.IsEmpty(Window(Home).Property({P}.libclean)) + {cond}</visible>
				<include>DL_Card</include>
			</control>""")
frames.append(f"""			<control type="group">
				<left>0</left>
				<top>0</top>
				<width>600</width>
				<height>{TOP + 128 + 2 * ROW + 16}</height>
				<visible>!String.IsEmpty(Window(Home).Property({P}.libclean))</visible>
				<include>DL_Card</include>
			</control>""")
words = dict(watched="$LOCALIZE[31081]", update="$LOCALIZE[31203]", clean="$LOCALIZE[31205]", settings="$LOCALIZE[31304]",
             kodi="Kodi", stop="$LOCALIZE[31303]", upd_short="$LOCALIZE[31306]", cln_short="$LOCALIZE[31307]")
body = items(P, "$LOCALIZE[31309]", watched_var="LibPanel_Unwatched", direction_var="LibPanel_Direction", words=words)
conf = confirm_items(P, "$LOCALIZE[31310]", "$LOCALIZE[31311]")

panel = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	Daylight Library panel (custom dialog 1160; docs/requests/library-panel/BRIEF.md). The library's
	general-purpose menu: View, Sort, Order, Unwatched only, Sets (films), Search, Update library, Clean library,
	Library settings. Opened by Left / Right past the edges of any library view, Left / Right past the
	ends of the header pills, the Options pill, and the System menu (Update / Clean library,
	daylight.libmode = update / clean: choose Films and shows or Music).
	Same language as the System menu: a soft card under the header pills, Fraunces title, accent-fill
	rows. Kodi's CleanLibrary() has no confirmation of its own, so the card asks first (list 200, "No"
	focused). Back closes the card (Kodi's Back); the library keeps the item you came from.
	Variables: Includes_LibraryPanel.xml. No Kodi-owned ids. GENERATED by _src/make_library_panel.py.
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
			<texture colordiffuse="$VAR[DL_DimDialog]">common/white.png</texture>
		</control>
		<control type="group">
			<left>1160</left>
			<top>264</top>
			<width>600</width>
			<height>760</height>
			<!-- card sized to the visible rows -->
{chr(10).join(frames)}
			<control type="label">
				<left>28</left>
				<top>12</top>
				<width>552</width>
				<height>56</height>
				<font>serif_28</font>
				<label>$VAR[LibPanel_Title]</label>
			</control>
			<control type="label">
				<left>24</left>
				<top>15</top>
				<width>552</width>
				<height>56</height>
				<align>right</align>
				<font>small_20</font>
				<textcolor>$VAR[DL_Ink2]</textcolor>
				<label>$VAR[LibPanel_Where]</label>
			</control>
			<control type="list" id="100">
				<left>12</left>
				<top>{TOP}</top>
				<width>576</width>
				<height>{ROW * 9}</height>
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
				<left>36</left>
				<top>{TOP + 4}</top>
				<width>528</width>
				<height>108</height>
				<font>ui_24</font>
				<textcolor>$VAR[DL_Ink2]</textcolor>
				<label>$VAR[LibPanel_CleanText]</label>
				<visible>!String.IsEmpty(Window(Home).Property({P}.libclean))</visible>
			</control>
			<control type="list" id="200">
				<left>12</left>
				<top>{TOP + 128}</top>
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
open(SKIN + "/Custom_1160_LibraryPanel.xml", "w", encoding="utf-8", newline="\n").write(panel)

# ------------------------------------------------------------------ picker 1161
G = "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(musicvideos)"
VIEWS = [
    ("videos", 500, "$LOCALIZE[31312]", "views/grid", G, "Pick_Cur_Grid"),
    ("videos", 501, "$LOCALIZE[31313]", "views/wall", G, "Pick_Cur_Wall"),
    ("videos", 503, "$LOCALIZE[31314]", "views/episodes", "Container.Content(episodes)", "Pick_Cur_Episodes"),
    ("videos", 50, "$LOCALIZE[535]", "views/list", None, "Pick_Cur_List"),
    ("music", 504, "$LOCALIZE[31312]", "views/music_grid", "Container.Content(albums) | Container.Content(artists) | Container.Content(genres) | Container.Content(years)", "Pick_Cur_Grid"),
    ("music", 50, "$LOCALIZE[535]", "views/music_list", None, "Pick_Cur_List"),
]
PITCH = 380
cards = []
for n in range(1, 5):
    cards.append(f"""			<control type="group">
				<left>0</left>
				<top>0</top>
				<width>{n * PITCH + 40}</width>
				<height>420</height>
				<visible>Integer.IsEqual(Container(100).NumItems,{n})</visible>
				<include>DL_Card</include>
			</control>""")
slides = [f'\t\t\t<animation effect="slide" end="{(4 - n) * PITCH // 2},0" time="0" condition="Integer.IsEqual(Container(100).NumItems,{n})">Conditional</animation>' for n in range(1, 4)]
# display names (localized); VIEWS keeps the viewtype labels (string ids) that Container.Viewmode is compared with
names = {("videos", 500): "$LOCALIZE[31312]", ("videos", 501): "$LOCALIZE[31313]", ("videos", 503): "$LOCALIZE[31314]", ("videos", 50): "$LOCALIZE[31315]",
         ("music", 504): "$LOCALIZE[31312]", ("music", 50): "$LOCALIZE[31315]"}
pitems = picker_items(VIEWS, name_map=names)
pitems = re.sub(r"<icon>(views/[a-z_]+)</icon>", r'<property name="prev">\1</property>', pitems)
picker = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	Daylight view picker (custom dialog 1161; docs/requests/library-panel/BRIEF.md). Opened by the View
	pill of the card header and View in the Library panel. One schematic preview per view valid for the
	content underneath (the views' own Container.Content conditions), its name and an accent dot +
	"Current" under the view on screen. The previews are layered white-alpha PNGs tinted with the live
	mood colours, so they look like the page at any time of day (_src/make_view_previews.py).
	OK = Container.SetViewMode(id), closes, focus back on the view; Back closes with no change.
	Opens on the current view: SetFocus(100,k,absolute), k = its place among the valid views (generated).
	The card centres itself on the number of previews (Container(100).NumItems counts visible items).
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
			<texture colordiffuse="$VAR[DL_DimDialog]">common/white.png</texture>
		</control>
		<control type="group">
			<left>{(1920 - 4 * PITCH - 40) // 2}</left>
			<top>330</top>
			<width>{4 * PITCH + 40}</width>
			<height>420</height>
{chr(10).join(slides)}
{chr(10).join(cards)}
			<control type="label">
				<left>48</left>
				<top>16</top>
				<width>600</width>
				<height>56</height>
				<font>serif_28</font>
				<label>$LOCALIZE[31011]</label>
			</control>
			<control type="label">
				<left>124</left>
				<top>19</top>
				<width>600</width>
				<height>56</height>
				<font>small_20</font>
				<textcolor>$VAR[DL_Ink2]</textcolor>
				<label>$VAR[LibPanel_Where]</label>
			</control>
			<control type="list" id="100">
				<left>20</left>
				<top>76</top>
				<width>{4 * PITCH}</width>
				<height>330</height>
				<orientation>horizontal</orientation>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<onup>noop</onup>
				<ondown>noop</ondown>
				<scrolltime tween="cubic" easing="out">160</scrolltime>
				<itemlayout width="{PITCH}" height="330">
					<include>Pick_Item</include>
				</itemlayout>
				<focusedlayout width="{PITCH}" height="330">
					<include content="Pick_Item"><param name="focused" value="true"/></include>
				</focusedlayout>
				<content>
{pitems}
				</content>
			</control>
		</control>
	</controls>
</window>
"""
open(SKIN + "/Custom_1161_ViewPicker.xml", "w", encoding="utf-8", newline="\n").write(picker)
print("ok")
