"""Generate 1080i/Includes_Views_More.xml: the 0.9.16 library views (docs/VIEWS_BRIEF_2026-10-27.md).

    python skins/skin.sentence/_src/make_views_more.py

Sentence's existing views stay: 500 a grid (with the note), 501 a wall, 503 episodes, 50 a list (video); 504 a grid,
50 a list (music). New, in Sentence's language (the page talks in sentences, anything you can press is lilac, the
focused thing is the lilac block / bar, serif paragraphs, quiet captions):
  505 a page       the showcase: one item written out as the info page writes it (position, the paragraph in serif 46,
                   the plot), its fanart behind the right of the page with the info page's ramps (no fanart: its
                   poster on the right). Left / Right turn the page; an invisible list drives it. Every video content.
  506 scenes       4 x 2 wide pictures (episode still / landscape / fanart; a poster or icon sits whole on the raised
                   block) with title and caption under each, the focused one in a sentence under the grid.
                   Every video content (series, episodes, sets, add-ons and plug-ins with thumbs).
  507 a tracklist  songs as a contents page: number, title, "by artist, from album", time; the focused row is the
                   lilac block; the cover and a sentence about the song on the right.
  508 portraits    artists / albums: the page layout with the artist's fanart and biography (or the album's review);
                   without fanart the photo / cover sits on the right.
viewtypes: Kodi's defaults ask for list / icon / big icon / info, so the new views use bigwrap / wide / bigwide /
biglist and never become a folder's default. Header phrase: "as [a page]", "as [scenes]", "as [a tracklist]",
"as [portraits]" (the viewtype labels, 31509-31512).
"""
from pathlib import Path

from default_repeats import strip as strip_defaults
from xmlfinish import finish_xml

ROOT = Path(__file__).resolve().parents[1] / "1080i"
OUT = ROOT / "Includes_Views_More.xml"
V = "Window.IsActive(videos)"
M = "Window.IsActive(music)"
EMPTY = "Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating"
PANEL = "ActivateWindow(1155)"

VARIABLES = """
	<!-- ============================================================ variables (views 505-508) -->
	<!-- page / portraits: the backdrop and, without one, the poster / cover / photo -->
	<expression name="Page_HasFanart">!ListItem.IsParentFolder + [!String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.fanart)) | !String.IsEmpty(ListItem.Art(artist.fanart)) | !String.IsEmpty(ListItem.Art(albumartist.fanart))]</expression>
	<variable name="Page_Fanart">
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(artist.fanart))">$INFO[ListItem.Art(artist.fanart)]</value>
		<value>$INFO[ListItem.Art(albumartist.fanart)]</value>
	</variable>
	<variable name="Page_Poster">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Page_MusicPlot">
		<value condition="ListItem.IsParentFolder"></value>
		<value condition="String.IsEqual(ListItem.DBType,artist)">$INFO[ListItem.Property(Artist_Description)]</value>
		<value>$INFO[ListItem.Property(Album_Description)]</value>
	</variable>
	<variable name="Page_Position">
		<value condition="ListItem.IsParentFolder">Back up a level</value>
		<value>Page $INFO[Container.CurrentItem] of $INFO[Container.NumItems]</value>
	</variable>
	<!-- scenes: the wide picture, or a poster / icon kept whole -->
	<expression name="Scene_HasWide">[String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)] | !String.IsEmpty(ListItem.Art(landscape)) | !String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.fanart))</expression>
	<expression name="Scene_HasArt">ListItem.IsParentFolder | $EXP[Scene_HasWide] | !String.IsEmpty(ListItem.Art(poster)) | !String.IsEmpty(ListItem.Art(tvshow.poster)) | !String.IsEmpty(ListItem.Art(thumb)) | [!String.IsEmpty(ListItem.Art(icon)) + !String.StartsWith(ListItem.Art(icon),Default)]</expression>
	<variable name="Scene_Wide">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value>$INFO[ListItem.Art(tvshow.fanart)]</value>
	</variable>
	<variable name="Scene_Small">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value>$INFO[ListItem.Art(icon)]</value>
	</variable>
	<variable name="Scene_Title">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Episode,,. ]$INFO[ListItem.Title]</value>
		<value>$VAR[Sen_ItemTitle]</value>
	</variable>
	<variable name="Scene_Dim">
		<value condition="Control.HasFocus(506)">dim_art</value>
		<value>white</value>
	</variable>
	<!-- tracklist -->
	<variable name="Track_Title">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Track_From">
		<value condition="ListItem.IsParentFolder">up a level</value>
		<value condition="!String.IsEmpty(ListItem.Artist) + !String.IsEmpty(ListItem.Album)">by $INFO[ListItem.Artist], from $INFO[ListItem.Album]</value>
		<value condition="!String.IsEmpty(ListItem.Artist)">by $INFO[ListItem.Artist]</value>
		<value>$INFO[ListItem.Album]</value>
	</variable>
	<variable name="Track_Ink">
		<value condition="Control.HasFocus(507)">on_lilac</value>
		<value>text</value>
	</variable>
	<variable name="Track_InkSoft">
		<value condition="Control.HasFocus(507)">on_lilac</value>
		<value>muted</value>
	</variable>
	<variable name="Track_Cover">
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value>$INFO[ListItem.Art(album.thumb)]</value>
	</variable>"""


def label(t, left, top, width, height, font, color, text, align=None, aligny=None, visible=None, extra=None):
    rows = ["<control type=\"label\">", f"\t<left>{left}</left>", f"\t<top>{top}</top>", f"\t<width>{width}</width>",
            f"\t<height>{height}</height>"]
    if align:
        rows.append(f"\t<align>{align}</align>")
    if aligny:
        rows.append(f"\t<aligny>{aligny}</aligny>")
    rows += [f"\t<font>{font}</font>", f"\t<textcolor>{color}</textcolor>", f"\t<selectedcolor>{color}</selectedcolor>",
             f"\t<label>{text}</label>"]
    if visible:
        rows.append(f"\t<visible>{visible}</visible>")
    if extra:
        rows.append(f"\t{extra}")
    rows.append("</control>")
    return "\n".join(t + r for r in rows)


def image(t, left, top, width, height, texture, color=None, visible=None, aspect=None, fade=None, background=False):
    rows = ["<control type=\"image\">", f"\t<left>{left}</left>", f"\t<top>{top}</top>", f"\t<width>{width}</width>",
            f"\t<height>{height}</height>"]
    if aspect:
        rows.append(f"\t<aspectratio{aspect[1] if isinstance(aspect, tuple) else ''}>{aspect[0] if isinstance(aspect, tuple) else aspect}</aspectratio>")
    if fade:
        rows.append(f"\t<fadetime>{fade}</fadetime>")
    attrs = (' background="true"' if background else "") + (f' colordiffuse="{color}"' if color else "")
    rows.append(f"\t<texture{attrs}>{texture}</texture>")
    if visible:
        rows.append(f"\t<visible>{visible}</visible>")
    rows.append("</control>")
    return "\n".join(t + r for r in rows)


def view_group(vid, body, empty_slide=0):
    slide = (f'\n\t\t\t<animation effect="slide" start="0,0" end="0,{empty_slide}" time="0" condition="{EMPTY}">Conditional</animation>'
             if empty_slide else "")
    return f"""		<control type="group">
			<visible>Control.IsVisible({vid})</visible>
			<include>Anim_VisibleFade</include>{slide}
{body}
		</control>"""


# --------------------------------------------------------------------------------- 505 a page / 508 portraits
def page(vid, label_id, vtype, visible, about, plot, plot_color="body"):
    t = "\t\t\t"
    backdrop = f"""			<!-- the item's fanart behind the right of the page, with the info page's ramps (VidInfo_Backdrop) -->
			<control type="group">
				<visible>$EXP[Page_HasFanart]</visible>
{image(t + chr(9), 760, 230, 1160, 850, "$VAR[Page_Fanart]", "ff7a7a7a", aspect="scale", fade=300, background=True)}
{image(t + chr(9), 760, 230, 600, 850, "sentence/ramp_info_left.png", "scrim")}
{image(t + chr(9), 760, 230, 1160, 160, "sentence/ramp_top.png", "bf0f1412")}
{image(t + chr(9), 760, 760, 1160, 320, "sentence/ramp_bottom.png", "e60f1412")}
			</control>
			<!-- no fanart: the poster / cover / photo on the right, as the list's note shows it -->
{image(t, 1308, 256, 492, 700, "$VAR[Page_Poster]", aspect=("keep", ' align="left" aligny="top"'), fade=160, background=True,
       visible="!$EXP[Page_HasFanart] + !ListItem.IsParentFolder")}"""
    article = f"""			<!-- the article: where you are, the item as a paragraph, its plot -->
			<control type="grouplist">
				<left>page_margin</left>
				<top>252</top>
				<width>900</width>
				<height>740</height>
				<orientation>vertical</orientation>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<visible>!Integer.IsEqual(Container.NumItems,0)</visible>
{label(t + chr(9), 0, 0, 900, 46, "cap_20", "muted", "$VAR[Page_Position]")}
				<control type="textbox">
					<description>the paragraph, 6 lines max (serif 46 at 64 px)</description>
					<width>900</width>
					<height max="384">auto</height>
					<font>serif_46</font>
					<textcolor>text</textcolor>
					<label>{about}</label>
				</control>
				<control type="group">
					<width>900</width>
					<height>30</height>
				</control>
				<control type="textbox">
					<description>the plot, 5 lines max (body 24 at 38 px)</description>
					<width>820</width>
					<height max="186">auto</height>
					<font>body_24</font>
					<textcolor>{plot_color}</textcolor>
					<label>{plot}</label>
				</control>
			</control>
			<control type="label">
				<left>page_margin</left>
				<top>1000</top>
				<width>900</width>
				<height>30</height>
				<font>ui_20</font>
				<textcolor>muted</textcolor>
				<label>$LOCALIZE[31513]</label>
				<visible>Control.HasFocus({vid}) + Integer.IsGreater(Container.NumItems,1)</visible>
			</control>"""
    driver = f"""			<!-- the driver: an invisible horizontal list (Left / Right turn the page; past either end = the Library panel) -->
			<control type="list" id="{vid}">
				<include>Lib_BackHomeNav</include>
				<left>0</left>
				<top>0</top>
				<width>8</width>
				<height>4</height>
				<orientation>horizontal</orientation>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<scrolltime>0</scrolltime>
				<viewtype label="{label_id}">{vtype}</viewtype>
				<visible>{visible}</visible>
				<itemlayout width="4" height="4"/>
				<focusedlayout width="4" height="4"/>
			</control>"""
    return view_group(vid, backdrop + "\n" + driver + "\n" + article)


def view505():
    return f"""	<!-- ============================================================== 505 a page (video) -->
	<include name="VidView_505_Page">
{page(505, 31509, "bigwrap", V, "$VAR[Lib_About]", "$VAR[Lib_Plot]")}
	</include>"""


def view508():
    return f"""	<!-- ============================================================== 508 portraits (music) -->
	<include name="Music_View_508">
{page(508, 31512, "biglist", f"{M} + [Container.Content(albums) | Container.Content(artists)]", "$VAR[Music_About]", "$VAR[Page_MusicPlot]")}
	</include>"""


# --------------------------------------------------------------------------------- 506 scenes
def scene_cell(focused):
    t = "\t\t\t\t\t\t"
    dim = "white" if focused else "$VAR[Scene_Dim]"
    zoom = ("""
						<animation type="Conditional" condition="Control.HasFocus(506) + !$EXP[ReduceMotion]" reversible="true">
							<effect type="zoom" start="100" end="106" center="auto" time="200" tween="cubic" easing="out"/>
						</animation>""" if focused else "")
    on = "Control.HasFocus(506)"
    title = (label("\t\t\t\t\t", 12, 258, 400, 28, "ui_20_bold", "muted", "$VAR[Scene_Title]", visible=f"!{on} + $EXP[Scene_HasArt]") + "\n" +
             label("\t\t\t\t\t", 12, 258, 400, 28, "ui_20_bold", "text", "$VAR[Scene_Title]", visible=f"{on} + $EXP[Scene_HasArt]") + "\n" +
             label("\t\t\t\t\t", 12, 286, 400, 28, "ui_20", "muted", "$VAR[Sen_CaptionShort]", visible=f"!{on}") + "\n" +
             label("\t\t\t\t\t", 12, 286, 400, 28, "ui_20", "lilac", "$VAR[Sen_Caption]", visible=on) + "\n" +
             image("\t\t\t\t\t", 12, 247, 400, 3, "sentence/round6.png", "lilac", visible=on)) if focused else (
             label("\t\t\t\t\t", 12, 258, 400, 28, "ui_20_bold", "muted", "$VAR[Scene_Title]", visible="$EXP[Scene_HasArt]") + "\n" +
             label("\t\t\t\t\t", 12, 286, 400, 28, "ui_20", "muted", "$VAR[Sen_CaptionShort]"))
    return f"""					<control type="group">
						<left>12</left>
						<top>12</top>
						<width>400</width>
						<height>225</height>{zoom}
						<control type="group">
							<visible>!ListItem.IsParentFolder</visible>
{image(t + chr(9), 0, 0, 400, 225, "common/white.png", "raised")}
							<control type="textbox">
								<left>14</left>
								<top>14</top>
								<width>372</width>
								<height>197</height>
								<font>serif_26</font>
								<textcolor>muted</textcolor>
								<label>$VAR[Scene_Title]</label>
							</control>
{image(t + chr(9), 0, 0, 400, 225, "$VAR[Scene_Wide]", dim, visible="$EXP[Scene_HasWide]", aspect="scale", fade=160, background=True)}
{image(t + chr(9), 0, 0, 400, 225, "$VAR[Scene_Small]", dim, visible="!$EXP[Scene_HasWide]", aspect="keep", fade=160, background=True)}
							<include>Sen_WatchedMarkers</include>
						</control>
						<control type="group">
							<visible>ListItem.IsParentFolder</visible>
							<include>VidView_ParentTile</include>
						</control>
					</control>
{title}"""


def view506():
    body = f"""			<control type="panel" id="506">
				<include>Lib_BackHomeNav</include>
				<left>lib_grid_x</left>
				<top>lib_grid_y</top>
				<width>1720</width>
				<height>700</height>
				<orientation>vertical</orientation>
				<preloaditems>1</preloaditems>
				<scrolltime tween="cubic" easing="out">260</scrolltime>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<viewtype label="31510">wide</viewtype>
				<visible>{V}</visible>
				<itemlayout width="430" height="350">
{scene_cell(False)}
				</itemlayout>
				<focusedlayout width="430" height="350">
{scene_cell(True)}
				</focusedlayout>
			</control>
			<!-- the focused one, in a sentence under the scenes (two lines: serif 36 at 52 px, descender-safe) -->
			<control type="textbox">
				<left>page_margin</left>
				<top>948</top>
				<width>page_width</width>
				<height>104</height>
				<font>serif_36</font>
				<textcolor>text</textcolor>
				<label>$VAR[Lib_About]</label>
				<visible>!Integer.IsEqual(Container.NumItems,0)</visible>
			</control>"""
    return f"""	<!-- ============================================================== 506 scenes (video) -->
	<include name="VidView_506_Scenes">
{view_group(506, body, 160)}
	</include>"""


# --------------------------------------------------------------------------------- 507 a tracklist
def track_row(focused):
    t = "\t\t\t\t\t"
    ink, soft = ("$VAR[Track_Ink]", "$VAR[Track_InkSoft]") if focused else ("text", "muted")
    rows = [image(t, 0, 64, 1080, 2, "common/hairline.png", "rule")]
    if focused:
        rows.append('\t\t\t\t\t<include content="Dlg_RowFocus"><param name="list_id" value="507"/><param name="width" value="1080"/><param name="height" value="66"/></include>')
    rows += [label(t, 0, 0, 56, 66, "num_22", soft, "$INFO[ListItem.TrackNumber]", align="right", aligny="center",
                   visible="!ListItem.IsParentFolder"),
             label(t, 84, 0, 560, 66, "serif_34", ink, "$VAR[Track_Title]", aligny="center"),
             label(t, 660, 0, 300, 66, "ui_22", soft, "$VAR[Track_From]", aligny="center"),
             label(t, 960, 0, 96, 66, "num_20", soft, "$INFO[ListItem.Duration]", align="right", aligny="center")]
    return "\n".join(rows)


def view507():
    t = "\t\t\t"
    body = f"""			<control type="list" id="507">
				<include>Lib_BackHomeNav</include>
				<left>page_margin</left>
				<top>244</top>
				<width>1080</width>
				<height>792</height>
				<orientation>vertical</orientation>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onleft>{PANEL}</onleft>
				<onright>{PANEL}</onright>
				<viewtype label="31511">bigwide</viewtype>
				<visible>{M} + Container.Content(songs)</visible>
				<itemlayout width="1080" height="66">
{track_row(False)}
				</itemlayout>
				<focusedlayout width="1080" height="66">
{track_row(True)}
				</focusedlayout>
			</control>
			<!-- the song on the right: its cover and a sentence about it -->
			<control type="group">
				<left>1308</left>
				<top>256</top>
				<width>492</width>
				<visible>!ListItem.IsParentFolder</visible>
{image(t + chr(9), 0, 0, 492, 492, "$VAR[Track_Cover]", aspect=("keep", ' align="left" aligny="top"'), fade=120, background=True)}
				<control type="textbox">
					<left>0</left>
					<top>516</top>
					<width>492</width>
					<height>154</height>
					<font>serif_36</font>
					<textcolor>text</textcolor>
					<label>$VAR[Music_About]</label>
				</control>
			</control>"""
    return f"""	<!-- ============================================================== 507 a tracklist (music) -->
	<include name="Music_View_507">
{view_group(507, body, 160)}
	</include>"""


def main():
    text = "\n".join(['<?xml version="1.0" encoding="UTF-8"?>',
                      "<!-- GENERATED by _src/make_views_more.py - edit the generator, not this file. -->",
                      "<includes>", VARIABLES, view505(), view506(), view507(), view508(), "</includes>", ""])
    text = "\n".join(l for l in text.split("\n") if l.strip() != "")
    OUT.write_text(finish_xml(strip_defaults(text + "\n", ROOT / "Defaults.xml")), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
