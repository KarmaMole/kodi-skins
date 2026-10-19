"""Generate the music library: skins/skin.fold/1080i/Includes_Views_Music.xml and MyMusicNav.xml.
    python skins/skin.fold/_src/make_music_views.py

Views: 504 Sleeves (albums, artists: a 5 x 3 shelf of marigold sleeves with the cover as a tipped-in square
plate, lift and tilt on focus, the label column on the right), 50 List (songs, genres, files).
Header words (grouplist 9000): Albums 9320, Artists 9321, Songs 9322, Genres 9323 (ReplaceWindow, so Back
stays one press: LESSONS Daylight 0.9.2), Sort 9324, direction 9325, View 9326; Kodi ids 3 / 4.
Timers for these views are written by make_views.py (Timers.xml).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "1080i"
RM = "Skin.HasSetting(fold.reducemotion)"
X, Y = 56, 176
SLOT_W, SLOT_H = 268, 300
PAD_X, PAD_Y = 40, 18
CW, CH = 228, 268          # resting sleeve
LW, LH = 252, 296          # lifted
COLS, ROWS = 5, 3


def selcol(x):
    return re.sub(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)",
                  lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", x)


def sleeve(focused):
    w, h = (LW, LH) if focused else (CW, CH)
    cx, bottom = PAD_X + CW // 2, PAD_Y + CH
    left, top = cx - w // 2, bottom - h
    pl, pt = (20, 18) if focused else (18, 16)
    pw = w - pl - (16 if focused else 14)
    sp = 96 if focused else 48
    tex = "shadow_lift" if focused else "shadow_card"
    lift = f"""
				<animation type="Focus" condition="!{RM}">
					<effect type="zoom" start="{CW / LW * 100:.1f}" end="100" center="{cx},{bottom}" time="260" tween="back" easing="out"/>
					<effect type="rotatex" start="0" end="-9" center="{bottom}" time="260" tween="back" easing="out"/>
				</animation>
				<animation type="Focus" condition="{RM}">
					<effect type="rotatex" start="-9" end="-9" center="{bottom}" time="0"/>
				</animation>
				<animation type="Unfocus" condition="!{RM}">
					<effect type="rotatex" start="-9" end="0" center="{bottom}" time="180" tween="cubic" easing="out"/>
				</animation>""" if focused else ""
    return f"""
			<control type="image">
				<left>{left - sp}</left>
				<top>{top - sp}</top>
				<width>{w + 2 * sp}</width>
				<height>{h + 2 * sp}</height>
				<texture border="{sp + 8}">fold/{tex}.png</texture>
			</control>
			<control type="group">
				<left>{left}</left>
				<top>{top}</top>
				<width>{w}</width>
				<height>{h}</height>{lift}
				<visible>!ListItem.IsParentFolder</visible>
				<include content="Fold_CardBody">
					<param name="w" value="{w}"/>
					<param name="h" value="{h}"/>
					<param name="fe_x" value="{w - 1}"/>
					<param name="fe_h" value="{h - 5}"/>
					<param name="color" value="mari"/>
					<param name="plate_l" value="{pl}"/>
					<param name="plate_t" value="{pt}"/>
					<param name="plate_w" value="{pw}"/>
					<param name="plate_h" value="{pw}"/>
					<param name="art" value="$INFO[ListItem.Art(thumb)]"/>
					<param name="foot_l" value="$VAR[Sleeve_FootL]"/>
					<param name="foot_r" value="$VAR[Sleeve_FootR]"/>
					<param name="foot_font" value="{'num_22' if focused else 'num_20'}"/>
					<param name="foot_b" value="{12 if focused else 10}"/>
					<param name="foot_color" value="ink"/>
					<param name="fallback" value="$INFO[ListItem.Label]"/>
				</include>{'''
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>%d</width>
					<height>%d</height>
					<texture>fold/card_light.png</texture>
					<visible>Control.HasFocus(504)</visible>
				</control>''' % (w, h) if focused else ''}
			</control>
			<control type="group">
				<left>{left}</left>
				<top>{top}</top>
				<visible>ListItem.IsParentFolder</visible>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{w}</width>
					<height>{h}</height>
					<texture border="6" colordiffuse="cream">fold/rr4.png</texture>
				</control>
				<control type="label">
					<left>24</left>
					<top>20</top>
					<width>{w - 48}</width>
					<height>80</height>
					<font>disp_64</font>
					<textcolor>mari_ink</textcolor>
					<label>←</label>
				</control>
				<control type="label">
					<left>24</left>
					<top>{h - 64}</top>
					<width>{w - 48}</width>
					<height>40</height>
					<font>tab_22</font>
					<textcolor>ink</textcolor>
					<label>Up a level</label>
				</control>
			</control>"""


def word(bid, label, onclick, vis="true", width=None, active=None):
    w = f"<width>{width}</width>" if width else "<width>auto</width>"
    tex = f'<texturenofocus border="6" colordiffuse="$VAR[{active}]">fold/chip.png</texturenofocus>' if active else "<texturenofocus />"
    return f"""
			<control type="button" id="{bid}">
				{w}
				<height>40</height>
				<font>caps_20_b</font>
				<textcolor>ink2</textcolor>
				<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
				<align>center</align>
				<textoffsetx>12</textoffsetx>
				<texturefocus border="6" colordiffuse="mari">fold/chip.png</texturefocus>
				{tex}
				<label>{label}</label>
				<onclick>{onclick}</onclick>
				<visible>{vis}</visible>
			</control>"""


def build():
    inc = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_music_views.py - edit the generator, not this file. -->
<!--{__doc__}-->
<includes>
	<variable name="Sleeve_FootL">
		<value condition="String.IsEqual(ListItem.DBType,artist)">$INFO[ListItem.Property(Artist_Genre)]</value>
		<value>$INFO[ListItem.Year]</value>
	</variable>
	<variable name="Sleeve_FootR">
		<value condition="Integer.IsGreater(ListItem.PlayCount,0)">$INFO[ListItem.PlayCount,,×]</value>
	</variable>
	<variable name="Music_TabChip_Albums"><value condition="$EXP[Music_TabAlbums]">1f1d1b18</value><value>00ffffff</value></variable>
	<variable name="Music_TabChip_Artists"><value condition="$EXP[Music_TabArtists]">1f1d1b18</value><value>00ffffff</value></variable>
	<variable name="Music_TabChip_Songs"><value condition="$EXP[Music_TabSongs]">1f1d1b18</value><value>00ffffff</value></variable>
	<variable name="Music_TabChip_Genres"><value condition="$EXP[Music_TabGenres]">1f1d1b18</value><value>00ffffff</value></variable>
	<variable name="Music_Crumb">
		<value condition="$EXP[Music_TabArtists]">Artists</value>
		<value condition="$EXP[Music_TabSongs]">Songs</value>
		<value condition="$EXP[Music_TabGenres]">Genres</value>
		<value condition="$EXP[Music_TabAlbums] + Container.Content(albums)">Albums</value>
		<value condition="!String.IsEmpty(Container.FolderName)">$INFO[Container.FolderName]</value>
		<value>$LOCALIZE[31202]</value>
	</variable>
	<variable name="Music_ViewWord">
		<value condition="Control.IsVisible(50)">View: list</value>
		<value>View: sleeves</value>
	</variable>
	<variable name="Sleeve_Kicker">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="String.IsEqual(ListItem.DBType,artist)">Artist$INFO[ListItem.Property(Artist_Genre), · ,]</value>
		<value>$INFO[ListItem.Year]$INFO[ListItem.Genre, · ,]</value>
	</variable>
	<variable name="Sleeve_Desc">
		<value condition="!String.IsEmpty(ListItem.Property(Album_Description))">$INFO[ListItem.Property(Album_Description)]</value>
		<value>$INFO[ListItem.Property(Artist_Description)]</value>
	</variable>

	<include name="Music_View_504">
		<control type="group">
			<visible>Control.IsVisible(504)</visible>
			<include content="Anim_StandUp"><param name="bottom" value="{Y + SLOT_H * ROWS}"/></include>
			<control type="panel" id="504">
				<left>{X}</left>
				<top>{Y}</top>
				<width>{SLOT_W * COLS}</width>
				<height>{SLOT_H * ROWS}</height>
				<orientation>vertical</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">280</scrolltime>
				<onup>9000</onup>
				<onright>9000</onright>
				<onleft>noop</onleft>
				<onback condition="$EXP[Music_AtTabRoot]">9398</onback>
				<viewtype label="Sleeves">icon</viewtype>
				<visible>Container.Content(albums) | Container.Content(artists)</visible>
				<itemlayout width="{SLOT_W}" height="{SLOT_H}">{sleeve(False)}
				</itemlayout>
				<focusedlayout width="{SLOT_W}" height="{SLOT_H}">{sleeve(True)}
				</focusedlayout>
			</control>
			<control type="grouplist">
				<left>1452</left>
				<top>176</top>
				<width>380</width>
				<height>860</height>
				<orientation>vertical</orientation>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<control type="label">
					<width>372</width>
					<height>40</height>
					<font>caps_20_b</font>
					<textcolor>mari_ink</textcolor>
					<label>$VAR[Sleeve_Kicker]</label>
				</control>
				<control type="group">
					<width>372</width>
					<height>0</height>
					<control type="textbox">
						<left>0</left>
						<top>0</top>
						<width>372</width>
						<height>184</height>
						<font>head_50</font>
						<textcolor>ink</textcolor>
						<label>$VAR[List_Title]</label>
					</control>
				</control>
				<control type="textbox">
					<width>372</width>
					<height max="162">auto</height>
					<font>head_50</font>
					<textcolor>clear</textcolor>
					<label>$VAR[List_Title]</label>
				</control>
				<control type="image">
					<width>372</width>
					<height>22</height>
					<texture />
				</control>
				<control type="label">
					<width>372</width>
					<height>42</height>
					<font>light_32</font>
					<textcolor>ink2</textcolor>
					<label>$INFO[ListItem.Artist]</label>
					<visible>String.IsEqual(ListItem.DBType,album)</visible>
				</control>
				<control type="image">
					<width>372</width>
					<height>18</height>
					<texture />
				</control>
				<control type="textbox">
					<width>372</width>
					<height>442</height>
					<font>body_24</font>
					<textcolor>body</textcolor>
					<label>$VAR[Sleeve_Desc]</label>
				</control>
			</control>
		</control>
	</include>

	<include name="Music_Header">
		<include content="Fold_RowHead">
			<param name="top" value="118"/>
			<param name="label" value="$VAR[Music_Crumb]"/>
			<param name="sub" value="$INFO[Container.NumItems,   ,]"/>
			<param name="color" value="mari_ink"/>
			<param name="width" value="560"/>
		</include>
		<control type="grouplist" id="9000">
			<left>640</left>
			<top>112</top>
			<width>1190</width>
			<height>40</height>
			<orientation>horizontal</orientation>
			<itemgap>6</itemgap>
			<onup>noop</onup>
			<ondown condition="Control.IsVisible(504)">504</ondown>
			<ondown>50</ondown>
			<onleft>noop</onleft>
			<onright>noop</onright>
			<onback condition="Control.IsVisible(504)">504</onback>
			<onback>50</onback>{word(9320, 'Albums', 'ReplaceWindow(Music,musicdb://albums/,return)', width=118, active='Music_TabChip_Albums')}{word(9321, 'Artists', 'ReplaceWindow(Music,musicdb://artists/,return)', width=133, active='Music_TabChip_Artists')}{word(9322, 'Songs', 'ReplaceWindow(Music,musicdb://songs/,return)', width=103, active='Music_TabChip_Songs')}{word(9323, 'Genres', 'ReplaceWindow(Music,musicdb://genres/,return)', width=118, active='Music_TabChip_Genres')}{word(9326, '$VAR[Music_ViewWord]', 'Container.SetViewMode(504)', 'Control.IsVisible(50) + [Container.Content(albums) | Container.Content(artists)]', 223)}{word(9327, '$VAR[Music_ViewWord]', 'Container.SetViewMode(50)', 'Control.IsVisible(504)', 223)}{word(9324, 'Sort $INFO[Container.SortMethod]', 'SendClick(3)', 'Control.IsEnabled(3) + !String.IsEmpty(Container.SortMethod)')}{word(9325, '$VAR[Music_SortArrow]', 'Container.SetSortDirection', 'Control.IsEnabled(3) + !String.IsEmpty(Container.SortMethod)', 44)}
		</control>
		<control type="button" id="3">
			<include>Fold_Hidden</include>
		</control>
		<control type="button" id="4">
			<include>Fold_Hidden</include>
		</control>
		<control type="button" id="9398">
			<include>Fold_Hidden</include>
			<visible allowhiddenfocus="true">false</visible>
			<onfocus>ActivateWindow(Home)</onfocus>
		</control>
	</include>
</includes>
"""
    (ROOT / "Includes_Views_Music.xml").write_text(selcol(inc), encoding="utf-8", newline="\n")
    win = """<?xml version="1.0" encoding="UTF-8"?>
<!--
	Music library (GENERATED by _src/make_music_views.py). Views: 504 Sleeves (albums, artists), 50 List.
	Kodi id contract (Estuary Omega MyMusicNav.xml / GUIWindowMusicNav.cpp): <views>, menucontrol 9000, 3 sort by,
	4 sort order. Focus: view <-> Up/Down <-> header words. Back = Kodi's parent folder; at a tab root -> Home.
-->
<window>
	<defaultcontrol always="true">50</defaultcontrol>
	<menucontrol>9000</menucontrol>
	<onload condition="Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating">SetFocus(9000)</onload>
	<backgroundcolor>table</backgroundcolor>
	<views>504,50</views>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>Fold_Background</include>
		<include>Fold_Tabs</include>
		<include>Fold_Clock</include>
		<include>Music_View_504</include>
		<include>View_50_List</include>
		<include>Music_Header</include>
		<control type="group">
			<visible>Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating</visible>
			<control type="label">
				<left>96</left>
				<top>240</top>
				<width>1200</width>
				<height>80</height>
				<font>disp_64</font>
				<textcolor>ink</textcolor>
				<label>Nothing in this folder.</label>
			</control>
		</control>
	</controls>
</window>
"""
    (ROOT / "MyMusicNav.xml").write_text(win, encoding="utf-8", newline="\n")
    print("music views written")


if __name__ == "__main__":
    build()
