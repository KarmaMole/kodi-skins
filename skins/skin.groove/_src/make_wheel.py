"""Generate 1080i/Custom_1171_Wheel.xml + Includes_Wheel.xml: the mood & genre wheel.   python skins/skin.groove/_src/make_wheel.py

screens/Custom_1171_Wheel.md (board 10), SPEC 8.4, HELPER_API 4, DATA 4, producer's decision 1: the pointer sits at
3 o'clock, so Up / Down turn the wheel (slices pass the pointer vertically) and Left / Right step between the rings
(Genre inner, Style, Mood outer) and on to Play mix / Albums.

Rings: invisible 1 px vertical wraplists 1301 (genre), 1302 (style), 1303 (mood), 11 items drawn (focusposition 5).
Eleven slots at 30 degrees (k = -5..5; slot k is k x 30 degrees clockwise from the pointer; the gap at 9 o'clock holds
the ring legend). Slot k reads Container(130x).ListItem(k) and is drawn only while the ring has more than 2|k| slices
(a short ring never repeats). A move turns the ring group one slice with a 200 ms pulse (Anim_PulseRotate).
  With script.karmamole.helper: slices from plugin://script.karmamole.helper/?info=wheel&ring=genre|style|mood (3+ albums,
  counts, ready AlbumsPath / PlayPath). Style and Mood show only when the helper returns slices for them.
  Without it (Kodi 21 limit, flagged in SPEC 8.4): the Genre ring from musicdb://genres/ (every genre, small ones
  included: per-slot probes cost 11 queries per press, so the spec's "show all genres" fallback is used), the slice's
  albums from musicdb://genres/<id>/-1/ (no escaping, R&B safe), its count from the hub list.
Hub: 2x2 collage of the slice's first four covers (list 1320), four quarter-disc masks make it one disc.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_music_views as MV  # noqa: E402
import strip_defaults  # noqa: E402

OUT = HERE.parent / "1080i" / "Custom_1171_Wheel.xml"
INC = HERE.parent / "1080i" / "Includes_Wheel.xml"
NL = "\n"
CX, CY = 600, 540
HELPER = "$EXP[HasGrooveHelper]"   # HELPER_API 0
# {"type":"songs","order":{"method":"random"}} (random order without PlayerControl(Random*), DEVICE_AUDIT M1)
RANDOM_SONGS = "?xsp=%7B%22type%22%3A%22songs%22%2C%22order%22%3A%7B%22method%22%3A%22random%22%7D%7D"
# a real path that lists nothing (an empty <content> path logs a GetDirectory error on every refresh, LESSONS Orbit 0.9.5)
NOTHING = "musicdb://years/?xsp=%7B%22type%22%3A%22albums%22%2C%22group%22%3A%7B%22type%22%3A%22years%22%7D%2C%22rules%22%3A%7B%22and%22%3A%5B%7B%22field%22%3A%22year%22%2C%22operator%22%3A%22is%22%2C%22value%22%3A%5B%22-1%22%5D%7D%5D%7D%7D"
RINGS = {  # id, key, texture base, (ox, oy, w, h) of the sector at 3 o'clock, label radius, label width, font
    1301: ("genre", "ring_genre", (154, -94, 201, 188), 257, 176, "font_small_22"),
    1302: ("style", "ring_style", (350, -110, 67, 220), 389, 190, "font_small_22"),
    1303: ("mood", "ring_mood", (410, -126, 69, 252), 451, 220, "font_small_22"),
}
LEGEND = {1301: (343, 31645), 1302: (211, 31646), 1303: (149, 31647)}


def ring_rows(rid):
    key, tex, (ox, oy, w, h), r, lw, font = RINGS[rid]
    o = []
    for k in range(-5, 6):
        rot = -30 * k  # Kodi: positive = counter-clockwise; slot k is k x 30 degrees clockwise
        vis = f"Integer.IsGreater(Container({rid}).NumItems,{2 * abs(k)})"
        lab_cx = CX + r + (8 if (k == 0 and rid == 1301) else 0)
        focus = f"Control.HasFocus({rid}) | [String.IsEqual(Window(Home).Property(groove.wheel.ring),{key}) + [Control.HasFocus(1311) | Control.HasFocus(1312)]]"
        if rid == 1301:  # radial text, flipped on the left half so it never reads upside down
            flip = 180 if abs(k) >= 4 else 0
            inner = f'<animation effect="rotate" end="{flip}" center="{lab_cx},{CY}" time="0" condition="true">Conditional</animation>' if flip else ""
        else:  # tangential text: reads along the ring, turned so the lower half isn't upside down
            base = -90 if k <= 0 else 90
            inner = f'<animation effect="rotate" end="{base}" center="{lab_cx},{CY}" time="0" condition="true">Conditional</animation>'
        big = k == 0
        lab = lambda colour, vis2, fnt: f"""					<control type="label">
						<left>{lab_cx - lw // 2}</left>
						<top>{CY - 22}</top>
						<width>{lw}</width>
						<height>44</height>
						<align>center</align>
						<aligny>center</aligny>
						<font>{fnt}</font>
						<textcolor>{colour}</textcolor>
						<label>$INFO[Container({rid}).ListItem({k}).Label]</label>
						<visible>{vis2}</visible>
						{inner}
					</control>"""
        labels = (lab("$VAR[ink]", f"{focus}", "font_label" if rid == 1301 else "font_small") + NL
                  + lab("$VAR[ink2]", f"![{focus}]", font)) if big else lab("$VAR[ink2]", "true", font)
        sector = (MV.image(CX + ox, CY + oy, w, h, f"groove/{tex}_fill.png", "$VAR[ring_fill]", None, ind=5) + NL
                  + MV.image(CX + ox, CY + oy, w, h, f"groove/{tex}_edge.png", "$VAR[ring_edge]", None, ind=5))
        if big:
            sector += (NL + MV.image(CX + ox, CY + oy, w, h, f"groove/{tex}_fill.png", "$VAR[ring_fill_focus]", focus, ind=5)
                       + NL + MV.image(CX + ox, CY + oy, w, h, f"groove/{tex}_edge.png", "$VAR[ring_edge_focus]", focus, ind=5))
        o.append(f"""				<control type="group">
					<visible>{vis}</visible>
					<animation effect="rotate" end="{rot}" center="{CX},{CY}" time="0" condition="true">Conditional</animation>
{sector}
{labels}
				</control>""")
    return NL.join(o)


def ring_group(rid):
    key = RINGS[rid][0]
    rest = f"!Control.HasFocus({rid}) + ![String.IsEqual(Window(Home).Property(groove.wheel.ring),{key}) + [Control.HasFocus(1311) | Control.HasFocus(1312)]]"
    return f"""			<control type="group">
				<visible>Integer.IsGreater(Container({rid}).NumItems,0)</visible>
				<include content="Anim_Dim"><param name="condition" value="{rest}"/><param name="to" value="55"/></include>
				<include content="Anim_PulseRotate"><param name="id" value="{rid}"/><param name="center" value="{CX},{CY}"/></include>
{ring_rows(rid)}
			</control>"""


def legend(rid):
    x, sid = LEGEND[rid]
    key = RINGS[rid][0]
    return f"""			<control type="label">
				<left>{x - 100}</left>
				<top>{CY - 16}</top>
				<width>200</width>
				<height>32</height>
				<align>center</align>
				<aligny>center</aligny>
				<font>font_fact_label</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>[UPPERCASE]$LOCALIZE[{sid}][/UPPERCASE]</label>
				<visible>Integer.IsGreater(Container(1302).NumItems,0) | Integer.IsGreater(Container(1303).NumItems,0)</visible>
				<visible>Integer.IsGreater(Container({rid}).NumItems,0)</visible>
				<animation effect="rotate" end="90" center="{x},{CY}" time="0" condition="true">Conditional</animation>
				<animation effect="fade" start="100" end="60" time="0" condition="!Control.HasFocus({rid}) + !String.IsEqual(Window(Home).Property(groove.wheel.ring),{key})">Conditional</animation>
			</control>"""


def driver(rid, nav, content):
    key = RINGS[rid][0]
    return f"""		<control type="wraplist" id="{rid}">
			<left>{CX}</left>
			<top>{1068 - 11 + (rid - 1301) * 0}</top>
			<width>1</width>
			<height>11</height>
			<orientation>vertical</orientation>
			<focusposition>5</focusposition>
			<scrolltime>0</scrolltime>
			<onfocus>SetProperty(groove.wheel.ring,{key},home)</onfocus>
{nav}
			<include>Wheel_PlayActions</include>
			<itemlayout width="1" height="1" />
			<focusedlayout width="1" height="1" />
			<content target="music" sortby="label" sortorder="ascending">{content}</content>
		</control>"""


def hub():
    o = []
    for i, (name, x, y) in enumerate((("tl", 450, 390), ("tr", 600, 390), ("bl", 450, 540), ("br", 600, 540))):
        o.append(MV.image(x, y, 150, 150, f"$INFO[Container(1320).ListItemAbsolute({i}).Art(thumb)]", None,
                          f"Integer.IsGreaterOrEqual(Container(1320).NumItems,4) + !String.IsEmpty(Container(1320).ListItemAbsolute({i}).Art(thumb))",
                          "<include>Anim_ArtFadetime</include>",
                          aspect="scale", bg=True, ind=3, texattr=f' diffuse="groove/disc_q_{name}.png"'))
    # fewer than four albums: the first cover fills the whole disc (no empty quarters)
    o.append(MV.image(450, 390, 300, 300, "$INFO[Container(1320).ListItemAbsolute(0).Art(thumb)]", None,
                      "!Integer.IsGreaterOrEqual(Container(1320).NumItems,4)", "<include>Anim_ArtFadetime</include>",
                      aspect="scale", bg=True, ind=3, texattr=' diffuse="groove/disc_mask.png"'))
    return NL.join(o)


def action_button(cid, y, icon, label, nav, vis_label):
    return f"""		<control type="image">
			<left>1254</left>
			<top>{y}</top>
			<width>84</width>
			<height>84</height>
			<texture colordiffuse="$VAR[focus_fill]">groove/disc_mask.png</texture>
			<visible>Control.HasFocus({cid})</visible>
		</control>
		<control type="image">
			<left>1238</left>
			<top>{y - 16}</top>
			<width>116</width>
			<height>116</height>
			<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
			<visible>Control.HasFocus({cid})</visible>
			<include>Anim_LabelReveal</include>
		</control>
		<control type="image">
			<left>1254</left>
			<top>{y}</top>
			<width>84</width>
			<height>84</height>
			<texture colordiffuse="$VAR[rim]">groove/ring_84.png</texture>
			<visible>Control.HasFocus({cid})</visible>
		</control>
		<control type="image">
			<left>1254</left>
			<top>{y}</top>
			<width>84</width>
			<height>84</height>
			<texture colordiffuse="$VAR[line_strong]">groove/ring_84.png</texture>
			<visible>!Control.HasFocus({cid})</visible>
		</control>
		<control type="button" id="{cid}">
			<left>1246</left>
			<top>{y - 8}</top>
			<width>360</width>
			<height>100</height>
			<texturefocus />
			<texturenofocus />
			<label />
{nav}
		</control>
		<control type="image">
			<left>1272</left>
			<top>{y + 18}</top>
			<width>48</width>
			<height>48</height>
			<texture colordiffuse="$VAR[icon_rest]">icons/{icon}.png</texture>
			<visible>!Control.HasFocus({cid})</visible>
		</control>
		<control type="image">
			<left>1272</left>
			<top>{y + 18}</top>
			<width>48</width>
			<height>48</height>
			<texture colordiffuse="$VAR[ink]">icons/{icon}.png</texture>
			<visible>Control.HasFocus({cid})</visible>
		</control>
		<control type="label">
			<left>1360</left>
			<top>{y + 20}</top>
			<width>440</width>
			<height>44</height>
			<aligny>center</aligny>
			<font>font_label</font>
			<textcolor>$VAR[ink]</textcolor>
			<label>{label}</label>
			<visible>{vis_label}</visible>
			<include>Anim_LabelReveal</include>
		</control>"""


def var(name, rows):
    o = [f'\t<variable name="{name}">']
    for c, v in rows:
        o.append(f'\t\t<value condition="{c}">{v}</value>' if c else f"\t\t<value>{v}</value>")
    o.append("\t</variable>")
    return NL.join(o)


def main():
    ring_is = lambda k: f"String.IsEqual(Window(Home).Property(groove.wheel.ring),{k})"
    style, mood = "Integer.IsGreater(Container(1302).NumItems,0)", "Integer.IsGreater(Container(1303).NumItems,0)"
    variables = NL.join([
        var("Wheel_GenrePath", [(HELPER, "plugin://script.karmamole.helper/?info=wheel&amp;ring=genre"), (None, "musicdb://genres/")]),
        var("Wheel_StylePath", [(HELPER, "plugin://script.karmamole.helper/?info=wheel&amp;ring=style"), (None, NOTHING)]),
        var("Wheel_MoodPath", [(HELPER, "plugin://script.karmamole.helper/?info=wheel&amp;ring=mood"), (None, NOTHING)]),
        # the slice's albums: helper's ready path, else the genre's id path with -1/ (all artists) appended
        var("Wheel_HubPath", [
            (f"{ring_is('style')} + !String.IsEmpty(Container(1302).ListItem.Property(Groove.AlbumsPath))", "$INFO[Container(1302).ListItem.Property(Groove.AlbumsPath)]"),
            (f"{ring_is('mood')} + !String.IsEmpty(Container(1303).ListItem.Property(Groove.AlbumsPath))", "$INFO[Container(1303).ListItem.Property(Groove.AlbumsPath)]"),
            ("!String.IsEmpty(Container(1301).ListItem.Property(Groove.AlbumsPath))", "$INFO[Container(1301).ListItem.Property(Groove.AlbumsPath)]"),
            ("!String.IsEmpty(Container(1301).ListItem.FolderPath)", "$INFO[Container(1301).ListItem.FolderPath,,-1/]"),
            (None, "musicdb://genres/")]),
        # no-helper Play mix (DEVICE_AUDIT M1): every song of the genre (id path, so R&B / Soul needs no escaping) through a
        # songs xsp with random order. Never PlayerControl(Random*): it saves Kodi's music shuffle setting for good.
        var("Wheel_ShufflePath", [
            ("!String.IsEmpty(Container(1301).ListItem.FolderPath)", "$INFO[Container(1301).ListItem.FolderPath]-1/-1/" + RANDOM_SONGS)]),
        # Producer 2026-10-21: only the helper can shuffle one play without saving Kodi's shuffle setting, so without it
        # the button says "Play" (the genre plays in library order: PlayMedia re-sorts the queue, DEVICE_AUDIT pass 2).
        var("Wheel_PlayLabel", [(HELPER, "$LOCALIZE[31617]"), (None, "$LOCALIZE[31702]")]),
        var("Wheel_PlayPath", [
            (f"{ring_is('style')}", "$INFO[Container(1302).ListItem.Property(Groove.PlayPath)]"),
            (f"{ring_is('mood')}", "$INFO[Container(1303).ListItem.Property(Groove.PlayPath)]"),
            (None, "$INFO[Container(1301).ListItem.Property(Groove.PlayPath)]")]),
        var("Wheel_SliceName", [(ring_is("style"), "$INFO[Container(1302).ListItem.Label]"),
                                (ring_is("mood"), "$INFO[Container(1303).ListItem.Label]"),
                                (None, "$INFO[Container(1301).ListItem.Label]")]),
        var("Wheel_Count", [
            (f"{ring_is('style')} + !String.IsEmpty(Container(1302).ListItem.Property(Groove.Count))", "$INFO[Container(1302).ListItem.Property(Groove.Count)] $LOCALIZE[31615]"),
            (f"{ring_is('mood')} + !String.IsEmpty(Container(1303).ListItem.Property(Groove.Count))", "$INFO[Container(1303).ListItem.Property(Groove.Count)] $LOCALIZE[31615]"),
            ("Container(1320).IsUpdating", ""),
            ("Integer.IsEqual(Container(1320).NumItems,1)", "1 $LOCALIZE[31616]"),
            ("Integer.IsGreater(Container(1320).NumItems,0)", "$INFO[Container(1320).NumItems] $LOCALIZE[31615]")]),
        f"""	<!-- OK on a ring = Play mix. Helper: its ready play path, else its play_shuffled on the slice's albums (first song random
	     too). No helper: the genre's songs through a random-order xsp, which PlayMedia re-sorts, so they play in library
	     order and the button reads "Play" (Wheel_PlayLabel). The skin never touches Kodi's shuffle setting. -->
	<include name="Wheel_PlayActions">
		<onclick condition="{HELPER} + !String.IsEmpty($VAR_PLAY)">RunPlugin($VAR[Wheel_PlayPath])</onclick>
		<onclick condition="{HELPER} + ![!String.IsEmpty($VAR_PLAY)]">RunScript(script.karmamole.helper,action=play_shuffled,"path=$VAR[Wheel_HubPath]")</onclick>
		<onclick condition="!{HELPER} + !String.IsEmpty(Container(1301).ListItem.FolderPath)">PlayMedia($VAR[Wheel_ShufflePath],isdir)</onclick>
	</include>""".replace("!String.IsEmpty($VAR_PLAY)", "[!String.IsEmpty(Container(1301).ListItem.Property(Groove.PlayPath)) | !String.IsEmpty(Container(1302).ListItem.Property(Groove.PlayPath)) | !String.IsEmpty(Container(1303).ListItem.Property(Groove.PlayPath))]"),
    ])
    INC.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_wheel.py - paths and labels of the Wheel (Custom_1171). -->
<includes>
{variables}
</includes>
""", encoding="utf-8", newline="\n")

    back_ring = (f'<onleft condition="{ring_is("mood")} + {mood}">1303</onleft>\n\t\t\t<onleft condition="{ring_is("style")} + {style}">1302</onleft>\n\t\t\t<onleft>1301</onleft>\n'
                 f'\t\t\t<onback condition="{ring_is("mood")} + {mood}">1303</onback>\n\t\t\t<onback condition="{ring_is("style")} + {style}">1302</onback>\n\t\t\t<onback>1301</onback>')
    nav1301 = f"""			<onleft>noop</onleft>
			<onright condition="{style}">1302</onright>
			<onright condition="{mood}">1303</onright>
			<onright>1311</onright>"""
    nav1302 = f"""			<onleft>1301</onleft>
			<onright condition="{mood}">1303</onright>
			<onright>1311</onright>
			<onback>1301</onback>"""
    nav1303 = f"""			<onleft condition="{style}">1302</onleft>
			<onleft>1301</onleft>
			<onright>1311</onright>
			<onback>1301</onback>"""
    play_nav = ("\t\t\t<onup condition=\"Control.IsVisible(9950)\">9950</onup>\n\t\t\t<ondown>1312</ondown>\n\t\t\t<onright>noop</onright>\n\t\t\t"
                + back_ring + "\n\t\t\t<include>Wheel_PlayActions</include>")
    albums_nav = ("\t\t\t<onup>1311</onup>\n\t\t\t<ondown>noop</ondown>\n\t\t\t<onright>noop</onright>\n\t\t\t" + back_ring
                  + "\n\t\t\t<onclick>ActivateWindow(Music,$VAR[Wheel_HubPath],return)</onclick>")
    on_ring = "Control.HasFocus(1301) | Control.HasFocus(1302) | Control.HasFocus(1303)"
    has_mini = "name=\"Groove_MiniPlayer\"" in "".join(p.read_text(encoding="utf-8", errors="ignore") for p in (HERE.parent / "1080i").glob("Includes*.xml"))
    mini = ('\t\t<include content="Groove_MiniPlayer"><param name="down" value="1311"/><param name="left" value="1311"/>'
            '<param name="back" value="1311"/></include>') if has_mini else "\t\t<!-- Groove_MiniPlayer (9950, lane B) is included here by this generator once it exists -->"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_wheel.py - edit the generator, then re-run.
	Wheel (custom window 1171, screens/Custom_1171_Wheel.md, board 10). Opened from Home's Wheel tile and the music header.
	Focus map: Genre 1301 | Style 1302 | Mood 1303 (Up / Down turn, Left / Right change ring; rings without slices are
	skipped) -Right-> Play mix 1311 -Down-> Albums 1312. OK on a ring = Play mix. Up on Play mix -> mini player 9950.
	Back: Play mix / Albums -> the ring you came from, Style / Mood -> Genre, Genre -> the window that opened it.
-->
<window type="window" id="1171">
	<defaultcontrol always="true">1301</defaultcontrol>
	<backgroundcolor>ground_static</backgroundcolor>
	<onload>SetProperty(groove.wheel.ring,genre,home)</onload>
	<controls>
		<control type="list" id="1320">
			<left>0</left>
			<top>0</top>
			<width>4</width>
			<height>1</height>
			<orientation>horizontal</orientation>
			<itemlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true">$INFO[ListItem.Art(thumb)]</texture></control>
			</itemlayout>
			<focusedlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true">$INFO[ListItem.Art(thumb)]</texture></control>
			</focusedlayout>
			<content target="music" sortby="random">$VAR[Wheel_HubPath]</content>
		</control>
		<include>Groove_Room</include>
		<control type="group">
			<visible>!String.IsEmpty(Container(1320).ListItemAbsolute(0).Art(thumb))</visible>
{MV.wash(1320, 600, 540, 1500, ind=3).replace("Container(1320).ListItem.Art(thumb)", "Container(1320).ListItemAbsolute(0).Art(thumb)")}
		</control>
		<control type="group">
			<include>Anim_WindowContent</include>
{ring_group(1303)}
{ring_group(1302)}
{ring_group(1301)}
{legend(1301)}
{legend(1302)}
{legend(1303)}
			<!-- hub: the slice's covers as one disc -->
			<control type="group">
				<visible>Integer.IsGreater(Container(1320).NumItems,0) + !String.IsEmpty(Container(1301).ListItem.Label)</visible>
				<include>Anim_GlowLayer</include>
{MV.image(410, 364, 380, 380, "groove/shadow_disc.png", "$VAR[shadow]", None, ind=4)}
{MV.image(450, 390, 300, 300, "groove/disc_mask.png", "$VAR[surface_raised]", None, ind=4)}
{hub()}
			</control>
			<control type="image">
				<left>1078</left>
				<top>528</top>
				<width>12</width>
				<height>24</height>
				<texture colordiffuse="$VAR[ink]">groove/wheel_pointer.png</texture>
				<visible>Integer.IsGreater(Container(1301).NumItems,0)</visible>
				<!-- sits against the outermost ring that is drawn: mood (x 1078), style (1018) or genre only (956) -->
				<animation effect="slide" start="0,0" end="-60,0" time="0" condition="!Integer.IsGreater(Container(1303).NumItems,0) + Integer.IsGreater(Container(1302).NumItems,0)">Conditional</animation>
				<animation effect="slide" start="0,0" end="-122,0" time="0" condition="!Integer.IsGreater(Container(1303).NumItems,0) + !Integer.IsGreater(Container(1302).NumItems,0)">Conditional</animation>
			</control>
			<!-- the slice, right of the wheel -->
			<control type="label">
				<left>1260</left>
				<top>410</top>
				<width>564</width>
				<height>76</height>
				<aligny>center</aligny>
				<font>font_hero</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$VAR[Wheel_SliceName]</label>
			</control>
			<control type="label">
				<left>1260</left>
				<top>494</top>
				<width>564</width>
				<height>44</height>
				<aligny>center</aligny>
				<font>font_caption_light</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$VAR[Wheel_Count]</label>
			</control>
{action_button(1311, 580, "play", "$VAR[Wheel_PlayLabel]", play_nav, f"Control.HasFocus(1311) | {on_ring}")}
{action_button(1312, 700, "albums", "$LOCALIZE[132]", albums_nav, "Control.HasFocus(1312)")}
			<control type="label">
				<left>0</left>
				<top>516</top>
				<width>1920</width>
				<height>48</height>
				<align>center</align>
				<aligny>center</aligny>
				<font>font_caption</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$LOCALIZE[31618]</label>
				<visible>Integer.IsEqual(Container(1301).NumItems,0) + !Container(1301).IsUpdating</visible>
			</control>
			<!-- window header -->
			<control type="image">
				<left>96</left>
				<top>54</top>
				<width>44</width>
				<height>44</height>
				<texture colordiffuse="$VAR[ink]">icons/wheel.png</texture>
			</control>
			<control type="label">
				<left>156</left>
				<top>54</top>
				<width>600</width>
				<height>44</height>
				<aligny>center</aligny>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$LOCALIZE[31408]</label>
			</control>
		</control>
{driver(1301, nav1301, "$VAR[Wheel_GenrePath]")}
{driver(1302, nav1302, "$VAR[Wheel_StylePath]")}
{driver(1303, nav1303, "$VAR[Wheel_MoodPath]")}
{mini}
	</controls>
</window>
"""
    xml, _ = strip_defaults.strip(xml)   # tags that only repeat Defaults.xml (official review xml.redundant)
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, "and", INC.name)


if __name__ == "__main__":
    main()
