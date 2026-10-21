"""Generate 1080i/Includes_Library.xml: the Library panel, view picker and clean confirm (M2).
python skins/skin.vernissage/_src/make_library.py

docs/skin.vernissage/screens/LibraryPanel.md; engine from Groove's in-window panel (Nocturne 0.9.6 lineage, LESSONS
"Library panel in the window itself"), redrawn as Vernissage placard cards. All three live INSIDE MyVideoNav /
MyMusicNav, so Kodi's own ids (3 sort by, 4 sort order, 14 watched toggle), Control.IsVisible(<view>) and
Container.SetViewMode() work as they do for the header words.

Ids: 9800 panel group / 9801 its list (static rows, up to 9: Sets only over films), 9850 picker group / 9851 its list,
9890 confirm group / 9893 its grouplist (9891 No, first and focused; 9892 Yes).
Opening: SetFocus(9801,0,absolute) / SetFocus(9851,0,absolute) (the view on show is listed first, LESSONS Duotone
0.9.9) / SetFocus(9891). The cards are always processed (a hidden static list never fills and can't take focus) and
fade in only while they have focus (Conditional fades), so focus never sits on something unseen.
Back on a card = a numeric onback to where it was opened from (Window(Home).Property(vernissage.lib.from) = view |
header, vernissage.pick.from = panel | header); the view keeps its item.
Clean library: Kodi 21's CleanLibrary() builtin does NOT ask (LESSONS), so the card asks first, "No" focused.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from vnxml import no_self, NL, card, fade_cond, group, img, ind, label, textbox, twin_img  # noqa: E402

OUT = HERE.parent / "1080i" / "Includes_Library.xml"
S = dict(view=31635, sort=31636, order=31637, show=31638, sets=31651, search=31639, update=31622, stop=31612,
         clean=31623, settings=31640, options=31657, clean_v=31610, clean_m=31609, clean_body=31690, no=31630,
         yes_clean=31623, unseen_only=31682, all=31683, asc=584, desc=585, kodi=31684)
PANEL_X, PANEL_W, ROW = 660, 600, 64


def back_to_view():
    return NL.join(['<onback condition="Control.IsVisible(500)">500</onback>',
                    '<onback condition="Control.IsVisible(510)">510</onback>', "<onback>50</onback>"])


def panel_row(focused):
    hf = "Control.HasFocus(9801)"
    o = []
    if focused:
        o += [twin_img(0, 0, PANEL_W, ROW, "vn/white.png", "wall", vis=hf),
              twin_img(0, 0, PANEL_W, 1, "vn/white.png", "card_edge", vis=hf),
              twin_img(0, ROW - 1, PANEL_W, 1, "vn/white.png", "card_edge", vis=hf),
              label(36, 0, 380, ROW, "$INFO[ListItem.Label]", "font_body", "$VAR[ink]", aligny="center", vis=hf),
              label(36, 0, 380, ROW, "$INFO[ListItem.Label]", "font_body", "$VAR[ink2]", aligny="center", vis=f"!{hf}"),
              label(380, 0, 184, ROW, "$INFO[ListItem.Label2]", "font_small", "$VAR[ink]", align="right", aligny="center", vis=hf),
              label(380, 0, 184, ROW, "$INFO[ListItem.Label2]", "font_small", "$VAR[ink2]", align="right", aligny="center", vis=f"!{hf}")]
    else:
        o += [label(36, 0, 380, ROW, "$INFO[ListItem.Label]", "font_body", "$VAR[ink2]", aligny="center"),
              label(380, 0, 184, ROW, "$INFO[ListItem.Label2]", "font_small", "$VAR[ink2]", align="right", aligny="center")]
    return NL.join(o)


ROWS = [  # label, label2, onclicks, visible
    (f"$LOCALIZE[{S['view']}]", "$VAR[Lib_ViewName]",
     ["SetProperty(vernissage.pick.from,panel,home)", "SetFocus(9851,0,absolute)"], "Integer.IsGreater(Container.ViewCount,1)"),
    (f"$LOCALIZE[{S['sort']}]", "$INFO[Container.SortMethod]", ["SetFocus(50)", "SendClick(3)"],
     "Control.IsEnabled(3) + !String.IsEmpty(Container.SortMethod)"),
    (f"$LOCALIZE[{S['order']}]", "$VAR[Lib_SortOrder]", ["$PARAM[order_click]"], "Control.IsEnabled(4) + !String.IsEmpty(Container.SortMethod)"),
    (f"$LOCALIZE[{S['show']}]", "$VAR[Lib_Unwatched]", ["SendClick(14)"],
     "$PARAM[is_video] + [Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | "
     "Container.Content(episodes) | Container.Content(musicvideos)] + !String.StartsWith(Container.FolderPath,videodb://inprogresstvshows)"),
    # Sets: the sets folder in this window; focus back to the view first (the panel closes), then the update, so
    # Back walks set -> sets -> films (LESSONS Sets row)
    (f"$LOCALIZE[{S['sets']}]", "", ["SetFocus(50)", "Container.Update(videodb://movies/sets/)"],
     "$PARAM[is_video] + Window.IsActive(videos) + [Container.Content(movies) | String.IsEqual(Container.FolderPath,videodb://movies/)] + "
     "!String.StartsWith(Container.FolderPath,videodb://movies/sets/) + Library.HasContent(moviesets) + String.IsEmpty(Container.PluginName)"),
    (f"$LOCALIZE[{S['search']}]", "", ["ActivateWindow(1150)"], None),
    ("$VAR[Lib_UpdateLabel]", "", ["UpdateLibrary($PARAM[kind])"], "$EXP[Lib_LibraryActions]"),
    (f"$LOCALIZE[{S['clean']}]", "", ["SetFocus(9891)"], "$EXP[Lib_LibraryActions]"),
    (f"$LOCALIZE[{S['settings']}]", f"$LOCALIZE[{S['kodi']}]", ["ActivateWindow(MediaSettings)"], None),
]


def panel():
    items = []
    for lab, l2, clicks, vis in ROWS:
        b = [f"<label>{lab}</label>"]
        if l2:
            b.append(f"<label2>{l2}</label2>")
        b += [f"<onclick>{c}</onclick>" for c in clicks]
        if vis:
            b.append(f"<visible>{vis}</visible>")
        items.append("<item>" + NL + NL.join("\t" + z for z in b) + NL + "</item>")
    # one card per row count (5..9), centred on y 540: h = 72 + 64 n + 24
    cards, slides = [], []
    nmax = len(ROWS)
    hmax = 72 + ROW * nmax + 24
    for n in range(4, nmax + 1):
        h = 72 + ROW * n + 24
        cond = (f"Integer.IsLessOrEqual(Container(9801).NumItems,{n})" if n == 4
                else f"Integer.IsEqual(Container(9801).NumItems,{n})")
        cards.append(group([card(0, 0, PANEL_W, h)], vis=cond))
        if n < nmax:
            slides.append(f'<animation effect="slide" start="0,0" end="0,{(hmax - h) // 2}" time="0" condition="{cond}">Conditional</animation>')
    lst = NL.join(['<control type="list" id="9801">', "\t<left>0</left>", "\t<top>72</top>", f"\t<width>{PANEL_W}</width>",
                   f"\t<height>{ROW * nmax}</height>", "\t<onup>9801</onup>", "\t<ondown>9801</ondown>",
                   "\t<onleft>9801</onleft>", "\t<onright>9801</onright>",
                   '\t<onback condition="String.IsEqual(Window(Home).Property(vernissage.lib.from),header)">$PARAM[header_back]</onback>',
                   ind(back_to_view(), 1), "\t<include>Anim_ScrollRow</include>",
                   f'\t<itemlayout width="{PANEL_W}" height="{ROW}">{NL}{ind(panel_row(False), 2)}{NL}\t</itemlayout>',
                   f'\t<focusedlayout width="{PANEL_W}" height="{ROW}">{NL}{ind(panel_row(True), 2)}{NL}\t</focusedlayout>',
                   f"\t<content>{NL}{ind(NL.join(items), 2)}{NL}\t</content>", "</control>"])
    body = group([*cards,
                  label(36, 18, 360, 44, f"$LOCALIZE[{S['options']}]", "font_placard", "$VAR[ink]", aligny="center", selected=False),
                  label(260, 18, 304, 44, "$VAR[Lib_Section]", "font_small", "$VAR[ink2]", align="right", aligny="center", selected=False),
                  lst], left=PANEL_X, top=540 - hmax // 2, anims=slides)
    return group([dim(), body], cid=9800, anims=fade_cond("![Control.HasFocus(9801) | ControlGroup(9890).HasFocus()]", 150))


def dim():
    return img(0, 0, 1920, 1080, "vn/white.png", "$VAR[scrim_card]")


def confirm():
    btn = lambda cid, lab, clicks, left, right: NL.join([  # noqa: E731
        f'<control type="button" id="{cid}">', "\t<width>180</width>", "\t<height>64</height>", "\t<font>font_body</font>",
        "\t<align>center</align>", "\t<aligny>center</aligny>", "\t<textcolor>$VAR[ink2]</textcolor>",
        "\t<focusedcolor>$VAR[ink]</focusedcolor>",
        '\t<texturefocus border="4" colordiffuse="$VAR[ink]">vn/card_edge.png</texturefocus>', "\t<texturenofocus />",
        f"\t<label>{lab}</label>", *[f"\t<onclick>{c}</onclick>" for c in clicks], "\t<onback>9801</onback>", "</control>"])
    gl = NL.join(['<control type="grouplist" id="9893">', "\t<left>36</left>", "\t<top>196</top>", "\t<width>400</width>",
                  "\t<height>64</height>", "\t<orientation>horizontal</orientation>", "\t<itemgap>16</itemgap>",
                  "\t<onleft>9893</onleft>", "\t<onright>9893</onright>", "\t<onup>9893</onup>", "\t<ondown>9893</ondown>",
                  "\t<onback>9801</onback>",
                  ind(btn(9891, f"$LOCALIZE[{S['no']}]", ["SetFocus(9801)"], None, None), 1),
                  ind(btn(9892, f"$LOCALIZE[{S['yes_clean']}]", ["CleanLibrary($PARAM[kind])", "SetFocus(9801)"], None, None), 1),
                  "</control>"])
    body = group([card(0, 0, 800, 300),
                  label(36, 28, 728, 44, f"$LOCALIZE[{S['clean_m']}]", "font_placard", "$VAR[ink]", aligny="center", vis="!$PARAM[is_video]", selected=False),
                  label(36, 28, 728, 44, f"$LOCALIZE[{S['clean_v']}]", "font_placard", "$VAR[ink]", aligny="center", vis="$PARAM[is_video]", selected=False),
                  textbox(36, 80, 728, 80, f"$LOCALIZE[{S['clean_body']}]", "font_small", "$VAR[ink2]"),
                  gl], left=560, top=390)
    return group([dim(), body], cid=9890, anims=fade_cond("!ControlGroup(9890).HasFocus()", 150))


def picker_layout(focused):
    hf = "Control.HasFocus(9851)"
    music = "Window.IsActive(music)"
    o = []
    if focused:
        o += [twin_img(10, 2, 340, 200, "vn/white.png", "frame", vis=hf),
              twin_img(12, 4, 336, 196, "vn/white.png", "mat", vis=hf)]
    for room, gate in (("day", "$EXP[VN_Day]"), ("evening", "$EXP[VN_Dark]")):
        for suffix, mc in (("", f"!{music}"), ("_music", music)):
            anims = [] if focused else ['<animation effect="fade" start="100" end="60" time="0" condition="true">Conditional</animation>']
            vis = f"{gate} + {mc}"
            o.append(img(20, 12, 320, 180, f"vn/views/{room}/$INFO[ListItem.Property(prev)]{suffix}.png", vis=vis, anims=anims))
    col = "$VAR[ink]" if focused else "$VAR[ink2]"
    o.append(label(20, 210, 320, 36, "$INFO[ListItem.Label]", "font_label", col, align="center", aligny="center"))
    o.append(twin_img(173, 258, 14, 14, "vn/dot.png", "ink", vis="String.IsEqual(ListItem.Property(current),yes)"))
    return NL.join(o)


VIEWS = [(500, 31653, "salon", "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(albums) | Container.Content(artists)"),
         (510, 31654, "gallery_wall", "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(albums)"),
         (50, 31655, "catalogue", "true")]


def picker():
    items = []
    for current in (True, False):        # the view on show first (marked), then the others in the usual order
        for vid, sid, prev, allowed in VIEWS:
            vis = f"Control.IsVisible({vid})" if current else f"!Control.IsVisible({vid}) + [{allowed}]"
            b = [f"<label>$LOCALIZE[{sid}]</label>", f'<property name="prev">{prev}</property>',
                 f'<property name="current">{"yes" if current else "no"}</property>',
                 "<onclick>Dialog.Close(all,true)</onclick>" if False else None,
                 f"<onclick>Container.SetViewMode({vid})</onclick>", "<onclick>SetFocus(50)</onclick>", f"<visible>{vis}</visible>"]
            items.append("<item>" + NL + NL.join("\t" + z for z in b if z) + NL + "</item>")
    cards, slides = [], []
    for n in (1, 2, 3):
        w = n * 360 + 64
        cond = f"Integer.IsLessOrEqual(Container(9851).NumItems,{n})" if n == 1 else f"Integer.IsEqual(Container(9851).NumItems,{n})"
        cards.append(group([card(0, 0, w, 380),
                            label(w - 36 - 400, 18, 400, 44, "$VAR[Lib_Section]", "font_small", "$VAR[ink2]", align="right", aligny="center", selected=False)],
                           vis=cond))
        if n < 3:
            slides.append(f'<animation effect="slide" start="0,0" end="{(3 - n) * 180},0" time="0" condition="{cond}">Conditional</animation>')
    lst = NL.join(['<control type="list" id="9851">', "\t<left>32</left>", "\t<top>80</top>", "\t<width>1080</width>",
                   "\t<height>290</height>", "\t<orientation>horizontal</orientation>", "\t<onleft>9851</onleft>",
                   "\t<onright>9851</onright>", "\t<onup>9851</onup>", "\t<ondown>9851</ondown>",
                   '\t<onback condition="String.IsEqual(Window(Home).Property(vernissage.pick.from),panel)">9801</onback>',
                   '\t<onback condition="String.IsEqual(Window(Home).Property(vernissage.pick.from),header)">$PARAM[header_back]</onback>',
                   ind(back_to_view(), 1), "\t<include>Anim_ScrollRow</include>",
                   f'\t<itemlayout width="360" height="290">{NL}{ind(picker_layout(False), 2)}{NL}\t</itemlayout>',
                   f'\t<focusedlayout width="360" height="290">{NL}{ind(picker_layout(True), 2)}{NL}\t</focusedlayout>',
                   f"\t<content>{NL}{ind(NL.join(items), 2)}{NL}\t</content>", "</control>"])
    body = group([*cards, label(36, 18, 300, 44, f"$LOCALIZE[{S['view']}]", "font_placard", "$VAR[ink]", aligny="center", selected=False), lst],
                 left=388, top=350, anims=slides)
    return group([dim(), body], cid=9850, anims=fade_cond("!Control.HasFocus(9851)", 150))


def main():
    o = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_library.py - edit the generator, then re-run. The Library panel 9800, view picker 9850 and
     clean confirm 9890, inside MyVideoNav / MyMusicNav (docs/skin.vernissage/screens/LibraryPanel.md). -->
<includes>
	<expression name="Lib_LibraryActions">!Container.Content(addons) + String.IsEmpty(Container.PluginName)</expression>
	<variable name="Lib_SortOrder">
		<value condition="Container.SortDirection(descending)">$LOCALIZE[{S['desc']}]</value>
		<value>$LOCALIZE[{S['asc']}]</value>
	</variable>
	<variable name="Lib_UpdateLabel">
		<value condition="Window.IsActive(music) + Library.IsScanningMusic">$LOCALIZE[{S['stop']}]</value>
		<value condition="!Window.IsActive(music) + Library.IsScanningVideo">$LOCALIZE[{S['stop']}]</value>
		<value>$LOCALIZE[{S['update']}]</value>
	</variable>
	<variable name="Lib_Unwatched">
		<value condition="System.Setting(hidewatched)">$LOCALIZE[{S['unseen_only']}]</value>
		<value>$LOCALIZE[{S['all']}]</value>
	</variable>
	<variable name="Lib_Section">
		<value condition="Container.Content(movies) | Container.Content(sets)">$LOCALIZE[31401]</value>
		<value condition="Container.Content(tvshows) | Container.Content(seasons)">$LOCALIZE[31450]</value>
		<value condition="Container.Content(episodes)">$LOCALIZE[31663]</value>
		<value condition="Container.Content(albums)">$LOCALIZE[132]</value>
		<value condition="Container.Content(artists)">$LOCALIZE[133]</value>
		<value condition="Container.Content(songs)">$LOCALIZE[134]</value>
		<value condition="Window.IsActive(music)">$LOCALIZE[2]</value>
		<value>$LOCALIZE[3]</value>
	</variable>

	<!-- Open the panel from a view edge (builtins run in order; horizontal lists run these only at their ends,
	     vertical lists / panels at the first / last column, LESSONS library panel) -->
	<include name="Lib_OpenLeft">
		<onleft>SetProperty(vernissage.lib.from,view,home)</onleft>
		<onleft>SetFocus(9801,0,absolute)</onleft>
	</include>
	<include name="Lib_OpenRight">
		<onright>SetProperty(vernissage.lib.from,view,home)</onright>
		<onright>SetFocus(9801,0,absolute)</onright>
	</include>

	<!-- params: is_video (true | false), kind (video | music), order_click, header_back (the Options word) -->
	<include name="Lib_Panel">
		<param name="is_video">true</param>
		<param name="kind">video</param>
		<param name="order_click">SendClick(4)</param>
		<param name="header_back">9522</param>
		<definition>
{ind(panel(), 3)}
{ind(confirm(), 3)}
		</definition>
	</include>

	<!-- params: header_back (the View word) -->
	<include name="Lib_Picker">
		<param name="header_back">9521</param>
		<definition>
{ind(picker(), 3)}
		</definition>
	</include>
</includes>
"""
    o = no_self(o)   # ends stop, never wrap (vnxml.no_self)
    OUT.write_text(o, encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {o.count('<control')} controls")


if __name__ == "__main__":
    main()
