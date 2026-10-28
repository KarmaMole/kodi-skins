"""Poster wall (view 506): generate 1080i/Includes_Wall.xml and the wall's two textures.

    python skins/skin.majan/_src/make_wall.py

Contract: docs/requests/poster-wall/FEASIBILITY.md (Majan, Option A: edge to edge) and the boards in
docs/requests/poster-wall/mockups/Majan*.html (make_boards.py has the same geometry table).

Six size x gap modes share ONE panel (id 506) through conditional itemlayout / focusedlayout pairs.
The panel is 1944 wide so (int)(width / pitch) gives the right column count (the last gutter falls
past x 1920) and 1080 high so (int)(1080 / pitch) gives only the FULL rows: focus never lands on the
peek row, and the wall scrolls one row before focus would leave the screen.

The info card is one group per mode outside the panel, placed with one time-0 Conditional slide per
Container(506).Column(n) / Row(n). It covers `span` cells on the cells' own edges and flips to the left
when the poster is in the last `span` columns.

Settings (SkinSettings.xml, category 04): majan.wall.size small/medium(empty)/large, majan.wall.nogap,
majan.wall.noborder, majan.wall.overlay off(empty)/1/2.

Conditions are written out in full (no $EXP) in layout / animation condition attributes, because Kodi
doesn't expand $EXP everywhere (LESSONS 2).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_textures as mt  # noqa: E402

OUT = HERE.parent / "1080i" / "Includes_Wall.xml"

# ------------------------------------------------------------------ conditions
SMALL = "String.IsEqual(Skin.String(majan.wall.size),small)"
LARGE = "String.IsEqual(Skin.String(majan.wall.size),large)"
MEDIUM = f"!{SMALL} + !{LARGE}"
GAP = "!Skin.HasSetting(majan.wall.nogap)"
NOGAP = "Skin.HasSetting(majan.wall.nogap)"
BORDER = "!Skin.HasSetting(majan.wall.noborder)"
NOBORDER = "Skin.HasSetting(majan.wall.noborder)"
OV1 = "String.IsEqual(Skin.String(majan.wall.overlay),1)"
OV2 = "String.IsEqual(Skin.String(majan.wall.overlay),2)"
RM = "Skin.HasSetting(majan.reducemotion)"
CONTENT = "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons)"

SIZE_COND = {"small": SMALL, "medium": MEDIUM, "large": LARGE}

# (size, gap) -> cols, poster w, poster h, gap, top offset   (FEASIBILITY Option A table)
FIT = {
    ("small", True): (11, 160, 240, 16, 0),
    ("small", False): (12, 160, 240, 0, 0),
    ("medium", True): (8, 226, 339, 16, 16),
    ("medium", False): (8, 240, 360, 0, 0),
    ("large", True): (6, 300, 450, 24, 0),
    ("large", False): (6, 320, 480, 0, 0),
}
SPAN = {"small": 4, "medium": 3, "large": 2}
MASK = {"small": "masks/poster_round8.png", "medium": "masks/poster_round8_wall.png",
        "large": "masks/poster_round8_large.png"}
PANEL_W, PANEL_H = 1944, 1080


def mode_cond(size, gap):
    return f"{SIZE_COND[size]} + {GAP if gap else NOGAP}"


def check():
    for (size, gap), (cols, w, h, g, top) in FIT.items():
        assert cols * w + (cols - 1) * g == 1920, (size, gap)
        assert w * 3 == h * 2
        assert PANEL_W // (w + g) == cols, (size, gap)
        rows = PANEL_H // (h + g)
        full = sum(1 for r in range(10) if top + r * (h + g) + h <= 1080)
        assert rows == full, (size, gap, rows, full)


def full_rows(size, gap):
    cols, w, h, g, top = FIT[(size, gap)]
    return PANEL_H // (h + g)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ind(text: str, n: int) -> str:
    pad = "\t" * n
    return "\n".join(pad + line if line.strip() else line for line in text.strip("\n").split("\n"))


# ------------------------------------------------------------------ poster pieces
def poster_xml(size, gap, color, fade="0"):
    """Art + fallback + markers for one cell, inside a group at the poster rect."""
    if gap:  # follows Poster corners (rounded masks are exported per width range)
        return f"""
<include content="VidView_ArtFallback">
	<param name="mask" value="{MASK[size]}"/>
</include>
<include content="VidView_ArtImage">
	<param name="mask" value="{MASK[size]}"/>
	<param name="color" value="{color}"/>
	<param name="fade" value="{fade}"/>
</include>
<include content="VidView_Markers"/>
<include>VidView_TVMarkers</include>"""
    # contact wall: always square (rounded corners would leave black notches between posters)
    return f"""
<include content="VidView_ParentTile"/>
<control type="group">
	<visible>!ListItem.IsParentFolder</visible>
	<include>VidView_ArtFallbackSquare</include>
	<control type="label">
		<left>12</left>
		<right>12</right>
		<top>10</top>
		<height>60</height>
		<font>small_19_bold</font>
		<textcolor>text_secondary</textcolor>
		<wrapmultiline>true</wrapmultiline>
		<aligny>top</aligny>
		<label>$INFO[ListItem.Label]</label>
		<visible>String.IsEmpty(ListItem.Art(poster))</visible>
	</control>
</control>
<include content="VidView_ArtImageSquare">
	<param name="art" value="$INFO[ListItem.Art(poster)]"/>
	<param name="color" value="{color}"/>
	<param name="visible" value="true"/>
	<param name="aspect" value="scale"/>
	<param name="fade" value="{fade}"/>
</include>
<include content="VidView_MarkersSquare">
	<param name="marker" value="marker_s"/>
	<param name="tab" value="marker_tab"/>
</include>
<control type="progress">
	<left>0</left>
	<right>0</right>
	<bottom>0</bottom>
	<height>progress_h</height>
	<texturebg colordiffuse="scrim_track">common/white.png</texturebg>
	<midtexture colordiffuse="$VAR[ColorAccent]">common/white.png</midtexture>
	<info>ListItem.PercentPlayed</info>
	<visible>$EXP[ShowUnwatchedMarkers] + ListItem.IsResumable + !$EXP[VidView_IsFolderType]</visible>
</control>
<include>VidView_TVMarkersSquare</include>
<control type="progress">
	<left>0</left>
	<right>0</right>
	<bottom>0</bottom>
	<height>progress_h</height>
	<texturebg colordiffuse="scrim_track">common/white.png</texturebg>
	<midtexture colordiffuse="$VAR[ColorAccent]">common/white.png</midtexture>
	<info>ListItem.Property(WatchedEpisodePercent)</info>
	<visible>$EXP[ShowUnwatchedMarkers] + $EXP[VidView_IsTVType] + $EXP[VidView_TVStarted]</visible>
</control>"""


def layouts(size, gap):
    cols, w, h, g, top = FIT[(size, gap)]
    cond = mode_cond(size, gap)
    pw, ph = w + g, h + g
    has = "Control.HasFocus(506)"
    if gap:
        frame = f"""
<control type="image">
	<left>focus_out</left>
	<top>focus_out</top>
	<right>focus_out</right>
	<bottom>focus_out</bottom>
	<texture border="16" colordiffuse="$VAR[ColorAccent]">$VAR[FocusFrameAlways]</texture>
	<visible>{has} + [{BORDER} | {RM}]</visible>
</control>"""
    else:  # inside the poster edge: 3 px accent line, 2 px page-black line inside it
        frame = f"""
<control type="group">
	<visible>{has} + [{BORDER} | {RM}]</visible>
	<control type="image">
		<left>0</left>
		<top>0</top>
		<right>0</right>
		<bottom>0</bottom>
		<texture border="16" colordiffuse="$VAR[ColorAccent]">focus/outline_3.png</texture>
	</control>
	<control type="image">
		<left>0</left>
		<top>0</top>
		<right>0</right>
		<bottom>0</bottom>
		<texture border="16" colordiffuse="bg">focus/inset_3_gap.png</texture>
	</control>
</control>"""
    unf = f"""
<itemlayout width="{pw}" height="{ph}" condition="{cond}">
	<control type="group">
		<left>0</left>
		<top>0</top>
		<width>{w}</width>
		<height>{h}</height>
{ind(poster_xml(size, gap, '$VAR[Wall_ArtDim]'), 2)}
	</control>
</itemlayout>"""
    foc = f"""
<focusedlayout width="{pw}" height="{ph}" condition="{cond}">
	<control type="group">
		<left>0</left>
		<top>0</top>
		<width>{w}</width>
		<height>{h}</height>
		<!-- border off: 1.08 zoom + the dark halo (the focused item is drawn last, over its neighbours) -->
		<animation type="Focus" reversible="true" condition="{NOBORDER} + !{RM}">
			<effect type="zoom" start="100" end="108" center="auto" time="150" tween="cubic" easing="out"/>
		</animation>
		<control type="image">
			<left>-32</left>
			<top>-32</top>
			<right>-32</right>
			<bottom>-32</bottom>
			<texture border="32" colordiffuse="focus_halo">focus/halo.png</texture>
			<visible>{has} + {NOBORDER} + !{RM}</visible>
		</control>
{ind(poster_xml(size, gap, 'white'), 2)}
{ind(frame, 2)}
	</control>
</focusedlayout>"""
    return unf + foc


# ------------------------------------------------------------------ info card
CARD = {
    # pad, kicker font/top, title font/top/h, meta font/top, plot top/lines, credits top, flags
    "small": dict(pad=28, kfont="mono_14", ktop=22, tfont="display_48", ttop=42, th=58, mfont="mono_15", mtop=104,
                  ptop=142, plines=2, ctop=None, flags=False),
    "medium": dict(pad=36, kfont="mono_15", ktop=34, tfont="display_48", ttop=60, th=58, mfont="mono_17", mtop=128,
                   ptop=166, plines=3, ctop=279, flags=False),
    "large": dict(pad=32, kfont="mono_15", ktop=34, tfont="display_56", ttop=62, th=66, mfont="mono_15", mtop=138,
                  ptop=176, plines=4, ctop=322, flags=True),
}
PLOT_H = {2: 66, 3: 99, 4: 131}  # body_23 line pitch 32.7 px: ceil(N x pitch). 1.0.17: 64 / 97 / 130 held N-1 lines a page
# (Kodi: floor(height / pitch)) and drew most of line N clipped; 68 showed a sliver of line 3 on the Shield
CARD_ID = {k: 5061 + i for i, k in enumerate(FIT)}  # card groups 5061-5066 (ids only for tests: Control.IsVisible)  # body_23 line pitch 32.7 px: whole lines, no half line


def card_x(size, gap, c):
    cols, w, h, g, top = FIT[(size, gap)]
    s = SPAN[size]
    first = c + 1 if c + s <= cols - 1 else c - s
    return first * (w + g)


def card(size, gap):
    cols, w, h, g, top = FIT[(size, gap)]
    s = SPAN[size]
    cw = s * w + (s - 1) * g
    k = CARD[size]
    pad = k["pad"]
    iw = cw - 2 * pad
    vis = (f"Control.HasFocus(506) + {mode_cond(size, gap)} + [[{OV1} + System.IdleTime(1)] | [{OV2} + System.IdleTime(2)]]"
           " + !Container(506).Scrolling + !ListItem.IsParentFolder")
    anims = [f'<animation effect="slide" start="0,0" end="{card_x(size, gap, c)},0" time="0" condition="Container(506).Column({c})">Conditional</animation>'
             for c in range(cols)]
    anims += [f'<animation effect="slide" start="0,0" end="0,{top + r * (h + g)}" time="0" condition="Container(506).Row({r})">Conditional</animation>'
              for r in range(full_rows(size, gap)) if top + r * (h + g) > 0]
    parts = [f"""
<control type="image">
	<left>0</left>
	<top>0</top>
	<width>{cw}</width>
	<height>{h}</height>
	<texture colordiffuse="bg_raised">common/white.png</texture>
</control>
<control type="image">
	<left>0</left>
	<top>0</top>
	<width>{cw}</width>
	<height>3</height>
	<texture colordiffuse="$VAR[ColorAccent]">common/white.png</texture>
</control>
<control type="label">
	<left>{pad}</left>
	<top>{k['ktop']}</top>
	<width>{iw}</width>
	<height>22</height>
	<font>{k['kfont']}</font>
	<textcolor>$VAR[ColorAccent]</textcolor>
	<label>$VAR[VidView_BigKicker]</label>
</control>
<control type="label">
	<left>{pad}</left>
	<top>{k['ttop']}</top>
	<width>{iw}</width>
	<height>{k['th']}</height>
	<font>{k['tfont']}</font>
	<textcolor>text_primary</textcolor>
	<scroll>true</scroll>
	<label>$VAR[VidView_ItemTitle]</label>
</control>
<control type="label">
	<left>{pad}</left>
	<top>{k['mtop']}</top>
	<width>{iw}</width>
	<height>26</height>
	<font>{k['mfont']}</font>
	<textcolor>text_secondary</textcolor>
	<scroll>true</scroll>
	<label>$VAR[Wall_CardMeta]</label>
</control>
<control type="textbox">
	<left>{pad}</left>
	<top>{k['ptop']}</top>
	<width>{iw}</width>
	<height>{PLOT_H[k['plines']]}</height>
	<font>body_23</font>
	<textcolor>text_body</textcolor>
	<label>$INFO[ListItem.Plot]</label>
	<include>Majan_PlotScroll</include>
</control>"""]
    if k["ctop"]:
        parts.append(f"""
<control type="label">
	<left>{pad}</left>
	<top>{k['ctop']}</top>
	<width>{iw}</width>
	<height>30</height>
	<font>credits_21</font>
	<textcolor>text_secondary</textcolor>
	<scroll>true</scroll>
	<label>$VAR[Wall_CardCredits]</label>
</control>""")
    if k["flags"]:
        flags = [("$VAR[VidInfo_FlagRes]", "!String.IsEmpty(ListItem.VideoResolution)"),
                 ("$VAR[VidInfo_FlagHDR]", "!String.IsEmpty(ListItem.HdrType)"),
                 ("$VAR[VidInfo_FlagVideo]", "!String.IsEmpty(ListItem.VideoCodec)"),
                 ("$VAR[VidInfo_AudioCodec]$VAR[VidInfo_AudioChannels]", "!String.IsEmpty(ListItem.AudioCodec)"),
                 ("$INFO[ListItem.VideoAspect,,:1]", "!String.IsEmpty(ListItem.VideoAspect)")]
        inc = "\n".join(f"""	<include content="OSD_Flag">
		<param name="label" value="{lab}"/>
		<param name="visible" value="{v}"/>
	</include>""" for lab, v in flags)
        parts.append(f"""
<control type="grouplist">
	<left>{pad}</left>
	<top>{h - pad - 32}</top>
	<width>{iw}</width>
	<height>32</height>
	<orientation>horizontal</orientation>
	<itemgap>8</itemgap>
{inc}
</control>""")
    body = "\n".join(ind(p, 1) for p in parts)
    return f"""
<!-- {size}, {'gap' if gap else 'no gap'}: card {cw} x {h} over {s} cells -->
<control type="group" id="{CARD_ID[(size, gap)]}">
	<left>0</left>
	<top>0</top>
	<width>{cw}</width>
	<height>{h}</height>
	<visible>{vis}</visible>
	<animation effect="fade" start="0" end="100" time="200">Visible</animation>
{ind(chr(10).join(anims), 1)}
{body}
</control>"""


# ------------------------------------------------------------------ settings preview
K = 292 / 1920  # the preview is the screen at 292 x 164


def preview_layouts(size, gap):
    """The preview panel is never focused, so it styles the item at row 1, column 1 (1-based index
    cols + 2) as the selection, inside the item layout via ListItem.CurrentItem (Container(9591).CurrentItem did not
    resolve per drawn item in a panel on the Shield). Item and focused layouts are identical."""
    cols, w, h, g, top = FIT[(size, gap)]
    px, py = int((w + g) * K), int((h + g) * K)
    pw = px - round(g * K)
    ph = round(pw * 1.5)
    cond = mode_cond(size, gap)
    sel = f"Integer.IsEqual(ListItem.CurrentItem,{cols + 2})"
    ring = ('<left>-2</left><top>-2</top><right>-2</right><bottom>-2</bottom>' if gap
            else '<left>0</left><top>0</top><right>0</right><bottom>0</bottom>')
    body = f"""<control type="group">
	<width>{pw}</width>
	<height>{ph}</height>
	<animation effect="zoom" start="100" end="108" center="auto" time="0" condition="{NOBORDER} + !{RM} + {sel}">Conditional</animation>
	<control type="image">
		<left>0</left>
		<top>0</top>
		<right>0</right>
		<bottom>0</bottom>
		<texture colordiffuse="bg_raised">common/white.png</texture>
	</control>
	<control type="image">
		<left>0</left>
		<top>0</top>
		<right>0</right>
		<bottom>0</bottom>
		<aspectratio>scale</aspectratio>
		<texture background="true">$INFO[ListItem.Art(poster)]</texture>
		<visible>{BORDER} | {sel}</visible>
	</control>
	<control type="image">
		<left>0</left>
		<top>0</top>
		<right>0</right>
		<bottom>0</bottom>
		<aspectratio>scale</aspectratio>
		<texture background="true" colordiffuse="dim_wall">$INFO[ListItem.Art(poster)]</texture>
		<visible>{NOBORDER} + !{sel}</visible>
	</control>
	<control type="image">
		{ring}
		<texture border="10" colordiffuse="$VAR[ColorAccent]">common/rect_outline_1.png</texture>
		<visible>{sel} + [{BORDER} | {RM}]</visible>
	</control>
</control>"""
    return f"""
<itemlayout width="{px}" height="{py}" condition="{cond}">
{ind(body, 1)}
</itemlayout>
<focusedlayout width="{px}" height="{py}" condition="{cond}">
{ind(body, 1)}
</focusedlayout>"""


# ------------------------------------------------------------------ document
def build() -> str:
    lay = "\n".join(layouts(s, g) for (s, g) in FIT)
    cards = "\n".join(card(s, g) for (s, g) in FIT)
    plays = "\n".join(preview_layouts(s, g) for (s, g) in FIT)
    medium_gap = mode_cond("medium", True)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_wall.py - edit the generator, not this file. -->
<!--
	Poster wall, view 506 (docs/requests/poster-wall/FEASIBILITY.md, Majan Option A: edge to edge).
	One vertical panel 1944 x 1080 at 0,0 with six conditional layout pairs (size x gap); the panel's
	full rows are the only ones that take focus, the next row peeks in at the bottom. Medium + gap
	starts one gutter down (a Conditional slide on the wrapper group, LESSONS: no animation on the view
	container itself). The library header is faded out while the wall has focus; Up from the top row
	(panel onup) focuses it. Back is untouched.
	Info card: one group per mode, placed by Container(506).Column(n) / Row(n) slides; shown after
	System.IdleTime(1|2) when the overlay setting is on.
	Settings preview (SkinSettings, category 04): Wall_Preview = mini panel 9591 at preview scale.
-->
<includes>
	<!-- ============================================================ expressions / variables -->
	<expression name="Wall_Small">{SMALL}</expression>
	<expression name="Wall_Large">{LARGE}</expression>
	<expression name="Wall_Medium">{MEDIUM}</expression>
	<expression name="Wall_Gap">{GAP}</expression>
	<expression name="Wall_Border">{BORDER}</expression>
	<expression name="Wall_OverlayOff">!{OV1} + !{OV2}</expression>

	<!-- unselected posters dim (opaque multiply) while the wall has focus and the border is off -->
	<variable name="Wall_ArtDim">
		<value condition="{NOBORDER} + Control.HasFocus(506)">dim_wall</value>
		<value>white</value>
	</variable>

	<!-- card meta line (mono): films/episodes with the end time, series with seasons/episodes, sets -->
	<variable name="Wall_Seasons">
		<value condition="Integer.IsEqual(ListItem.Property(TotalSeasons),1)"> · 1 season</value>
		<value condition="!String.IsEmpty(ListItem.Property(TotalSeasons))"> · $INFO[ListItem.Property(TotalSeasons)] seasons</value>
	</variable>
	<variable name="Wall_Episodes">
		<value condition="Integer.IsEqual(ListItem.Property(TotalEpisodes),1)"> · 1 episode</value>
		<value condition="!String.IsEmpty(ListItem.Property(TotalEpisodes))"> · $INFO[ListItem.Property(TotalEpisodes)] episodes</value>
	</variable>
	<variable name="Wall_ToGo">
		<value condition="Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0) + Integer.IsGreater(ListItem.Property(WatchedEpisodes),0)"> · $INFO[ListItem.Property(UnWatchedEpisodes)] to go</value>
		<value condition="$EXP[VidView_TVDone]"> · watched</value>
	</variable>
	<variable name="Wall_Ends">
		<value condition="!String.IsEmpty(ListItem.Duration) + !String.IsEmpty(ListItem.EndTimeResume)"> · ends $INFO[ListItem.EndTimeResume]</value>
	</variable>
	<variable name="Wall_CardMeta">
		<value condition="String.IsEqual(ListItem.DBType,set)">Collection$INFO[ListItem.Property(Total), · , films] · $VAR[VidView_Status]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$VAR[Wall_Seasons]$VAR[Wall_Episodes]$VAR[Wall_ToGo]</value>
		<value condition="String.IsEqual(ListItem.DBType,season)">$INFO[ListItem.Label]$VAR[Wall_Episodes]$INFO[ListItem.Property(WatchedEpisodes), · , watched]</value>
		<value condition="!String.IsEmpty(ListItem.Year)">$INFO[ListItem.Year]$VAR[VidView_RuntimeMeta]$VAR[VidView_RatingMeta]$VAR[VidView_MPAAMeta]$VAR[Wall_Ends]</value>
		<value>$VAR[VidView_Status]$VAR[VidView_RuntimeMeta]$VAR[Wall_Ends]</value>
	</variable>
	<!-- director (bright) + genres; library listings carry no cast (LESSONS, Nocturne) -->
	<variable name="Wall_CardCredits">
		<value condition="!String.IsEmpty(ListItem.Director)">[COLOR text_primary]$INFO[ListItem.Director][/COLOR]$INFO[ListItem.Genre,  ·  ,]</value>
		<value condition="!String.IsEmpty(ListItem.Studio)">[COLOR text_primary]$INFO[ListItem.Studio][/COLOR]$INFO[ListItem.Genre,  ·  ,]</value>
		<value>$INFO[ListItem.Genre]</value>
	</variable>

	<!-- ============================================================ view 506 -->
	<include name="VidView_506_PosterWall">
		<control type="group">
			<visible>Control.IsVisible(506)</visible>
			<include>Anim_FadeVisible</include>
			<control type="group">
				<left>0</left>
				<top>0</top>
				<animation effect="slide" start="0,0" end="0,16" time="0" condition="{medium_gap}">Conditional</animation>
				<control type="panel" id="506">
					<left>0</left>
					<top>0</top>
					<width>{PANEL_W}</width>
					<height>{PANEL_H}</height>
					<orientation>vertical</orientation>
					<preloaditems>2</preloaditems>
					<scrolltime tween="cubic" easing="out">200</scrolltime>
					<onup>9000</onup>
					<ondown>noop</ondown>
					<onleft>ActivateWindow(1155)</onleft>
					<onright>ActivateWindow(1155)</onright>
					<viewtype label="31310">list</viewtype>
					<visible>{CONTENT}</visible>
{ind(lay, 5)}
				</control>
			</control>
			<!-- info card (Off / after 1 s / after 2 s) -->
{ind(cards, 3)}
		</control>
	</include>

	<!-- ============================================================ settings preview -->
	<!-- The wall at the current settings, 292 x 164 (the screen at 0.152). Newest films, like the
	     Movies node. Only processed while the Poster wall category is shown. -->
	<include name="Wall_Preview">
		<control type="panel" id="9591">
			<left>0</left>
			<top>0</top>
			<width>296</width>
			<height>164</height>
			<orientation>vertical</orientation>
			<scrolltime>0</scrolltime>
			<animation effect="slide" start="0,0" end="0,2" time="0" condition="{medium_gap}">Conditional</animation>
{ind(plays, 3)}
			<content target="videos" sortby="dateadded" sortorder="descending" limit="60" browse="never">videodb://movies/titles/</content>
		</control>
	</include>
</includes>
"""


def textures():
    # contact-wall focus: outline_3.png (3 px accent on the poster edge) + this 2 px page-black line inside it
    mt.save(mt.alpha_to_white(mt.ring_alpha(40, 40, 2, 0, margin=3)), "focus/inset_3_gap.png", "16")
    # rounded mask for Medium + gap posters (226 x 339, radius 8), 2x like the other masks
    mt.save(mt.alpha_to_white(mt.rounded_alpha(226 * mt.HIDPI, 339 * mt.HIDPI, 8 * mt.HIDPI)), "masks/poster_round8_wall.png")


def main():
    check()
    textures()
    xml = build()
    assert xml.count("<?xml") == 1
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(xml):,} bytes)")


if __name__ == "__main__":
    main()
