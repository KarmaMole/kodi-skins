"""0.9.13 music views for Fold (docs/VIEWS_BRIEF_2026-10-27.md), imported by make_music_views.py.

  507 Crate   the table covered with small marigold sleeves, 8 across (a dense album wall); the focused one is
              named on the crumb line.
  508 Poster  the focused artist or album as a folded gig poster lying on the table: the fanart printed edge to
              edge with its two creases (or, with no fanart, the portrait / cover tipped in and the name printed
              large), the name, dates and story in a column beside it, a strip of small sleeves below.
"""
from fold_views_more import closed_card


def crate_view():
    def card(f):
        return closed_card(f, 507, 168, 206, 186, 228, 27, 18, "mari", "$INFO[ListItem.Art(thumb)]",
                           "$VAR[Sleeve_FootL]", "$VAR[Sleeve_FootR]", plate_ratio=1.0, foot_color="ink", marks=False,
                           parent_color="mari_ink")
    return f"""
	<include name="Music_View_507">
		<control type="group">
			<visible>Control.IsVisible(507)</visible>
			<include content="Anim_StandUp"><param name="bottom" value="1012"/></include>
			<control type="panel" id="507">
				<left>56</left>
				<top>164</top>
				<width>{222 * 8}</width>
				<height>{252 * 3 + 40}</height>
				<orientation>vertical</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">260</scrolltime>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onright>9000</onright>
				<onleft>ActivateWindow(1155)</onleft>
				<onback condition="$EXP[Music_AtTabRoot]">9398</onback>
				<viewtype label="Crate">wrap</viewtype>
				<visible>Container.Content(albums) | Container.Content(artists)</visible>
				<itemlayout width="222" height="252">{card(False)}
				</itemlayout>
				<focusedlayout width="222" height="252">{card(True)}
				</focusedlayout>
			</control>
		</control>
	</include>"""


PO_X, PO_Y, PO_W, PO_H = 96, 164, 1240, 540


def poster_view():
    def strip_card(f):
        return closed_card(f, 508, 148, 180, 162, 197, 18, 50, "mari", "$INFO[ListItem.Art(thumb)]", "", "",
                           plate_ratio=1.0, foot_color="ink", marks=False, parent_word="Up", parent_color="mari_ink")
    half = PO_W // 2
    return f"""
	<include name="Music_View_508">
		<control type="group">
			<visible>Control.IsVisible(508)</visible>
			<control type="group">
				<visible>Integer.IsGreater(Container.NumItems,0)</visible>
				<include>Anim_FadeVisible</include>
				<!-- the poster: cream paper, the picture printed with a 14 px margin, folded in four -->
				<control type="image">
					<left>{PO_X - 72}</left>
					<top>{PO_Y - 40}</top>
					<width>{PO_W + 144}</width>
					<height>{PO_H + 150}</height>
					<texture border="104">fold/shadow_spread.png</texture>
				</control>
				<control type="image">
					<left>{PO_X}</left>
					<top>{PO_Y}</top>
					<width>{PO_W}</width>
					<height>{PO_H}</height>
					<texture border="6" colordiffuse="cream">fold/rr4.png</texture>
				</control>
				<control type="image">
					<left>{PO_X}</left>
					<top>{PO_Y}</top>
					<width>{PO_W}</width>
					<height>{PO_H}</height>
					<texture diffuse="fold/rr4.png">fold/tooth_cream.png</texture>
				</control>
				<control type="image">
					<left>{PO_X + 14}</left>
					<top>{PO_Y + 14}</top>
					<width>{PO_W - 28}</width>
					<height>{PO_H - 28}</height>
					<aspectratio>scale</aspectratio>
					<fadetime>240</fadetime>
					<texture background="true">$VAR[Poster_Fanart]</texture>
					<visible>$EXP[Poster_HasFanart]</visible>
				</control>
				<!-- no fanart: the portrait / cover tipped in, the name printed large beside it -->
				<control type="group">
					<left>{PO_X + 56}</left>
					<top>{PO_Y + 50}</top>
					<width>440</width>
					<height>440</height>
					<visible>!$EXP[Poster_HasFanart] + !ListItem.IsParentFolder + !String.IsEmpty(ListItem.Art(thumb))</visible>
					<control type="image">
						<left>-12</left>
						<top>-12</top>
						<right>-12</right>
						<bottom>-12</bottom>
						<texture border="14">fold/plate_frame.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>440</width>
						<height>440</height>
						<texture colordiffuse="mari">common/white.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>440</width>
						<height>440</height>
						<aspectratio>scale</aspectratio>
						<fadetime>200</fadetime>
						<texture background="true">$INFO[ListItem.Art(thumb)]</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>440</width>
						<height>440</height>
						<texture>fold/plate_sheen.png</texture>
					</control>
				</control>
				<control type="textbox">
					<left>{PO_X + 560}</left>
					<top>{PO_Y + 60}</top>
					<width>{PO_W - 620}</width>
					<height>370</height>
					<font>disp_96</font>
					<textcolor>ink</textcolor>
					<label>$VAR[List_Title]</label>
					<visible>!$EXP[Poster_HasFanart] + !ListItem.IsParentFolder + !String.IsEmpty(ListItem.Art(thumb))</visible>
				</control>
				<!-- no picture at all: a typographic poster, the name printed across it -->
				<control type="textbox">
					<left>{PO_X + 60}</left>
					<top>{PO_Y + 60}</top>
					<width>{PO_W - 120}</width>
					<height>370</height>
					<font>disp_112</font>
					<textcolor>ink</textcolor>
					<label>$VAR[List_Title]</label>
					<visible>!$EXP[Poster_HasFanart] + !ListItem.IsParentFolder + String.IsEmpty(ListItem.Art(thumb))</visible>
				</control>
				<control type="label">
					<left>{PO_X + 560}</left>
					<top>{PO_Y + 452}</top>
					<width>{PO_W - 620}</width>
					<height>40</height>
					<font>caps_22_b</font>
					<textcolor>mari_ink</textcolor>
					<label>$VAR[Poster_Kicker]</label>
					<visible>!$EXP[Poster_HasFanart] + !ListItem.IsParentFolder + !String.IsEmpty(ListItem.Art(thumb))</visible>
				</control>
				<control type="label">
					<left>{PO_X + 60}</left>
					<top>{PO_Y + 60}</top>
					<width>400</width>
					<height>140</height>
					<font>disp_112</font>
					<textcolor>mari_ink</textcolor>
					<label>←</label>
					<visible>ListItem.IsParentFolder</visible>
				</control>
				<!-- the folds: a vertical crease (gatefold shading either side) and a horizontal one -->
				<control type="image">
					<left>{PO_X}</left>
					<top>{PO_Y}</top>
					<width>{half}</width>
					<height>{PO_H}</height>
					<texture>fold/gate_l.png</texture>
				</control>
				<control type="image">
					<left>{PO_X + half}</left>
					<top>{PO_Y}</top>
					<width>{PO_W - half}</width>
					<height>{PO_H}</height>
					<texture>fold/gate_r.png</texture>
				</control>
				<control type="image">
					<left>{PO_X}</left>
					<top>{PO_Y}</top>
					<width>{PO_W}</width>
					<height>{PO_H}</height>
					<texture>fold/note_crease.png</texture>
				</control>
				<control type="image">
					<left>{PO_X}</left>
					<top>{PO_Y}</top>
					<width>{PO_W}</width>
					<height>{PO_H}</height>
					<texture border="4" colordiffuse="mari">fold/edge_all.png</texture>
				</control>
				<!-- the column beside the poster -->
				<control type="grouplist">
					<left>1400</left>
					<top>{PO_Y + 6}</top>
					<width>424</width>
					<height>{PO_H}</height>
					<orientation>vertical</orientation>
					<itemgap>0</itemgap>
					<usecontrolcoords>true</usecontrolcoords>
					<control type="label">
						<width>424</width>
						<height>36</height>
						<font>caps_20_b</font>
						<textcolor>mari_ink</textcolor>
						<label>$VAR[Poster_Kicker]</label>
					</control>
					<!-- the name: printed on the poster itself when there is no fanart, so only here with one -->
					<control type="group">
						<width>424</width>
						<height>0</height>
						<visible>$EXP[Poster_HasFanart] | ListItem.IsParentFolder</visible>
						<control type="textbox">
							<left>0</left>
							<top>0</top>
							<width>424</width>
							<height>184</height>
							<font>head_50</font>
							<textcolor>ink</textcolor>
							<label>$VAR[List_Title]</label>
						</control>
					</control>
					<control type="textbox">
						<width>424</width>
						<height max="162">auto</height>
						<font>head_50</font>
						<textcolor>clear</textcolor>
						<label>$VAR[List_Title]</label>
						<visible>$EXP[Poster_HasFanart] | ListItem.IsParentFolder</visible>
					</control>
					<control type="image">
						<width>10</width>
						<height>12</height>
						<texture />
					</control>
					<control type="textbox">
						<width>424</width>
						<height max="64">auto</height>
						<font>caps_20</font>
						<textcolor>cap</textcolor>
						<label>$VAR[Poster_Facts]</label>
					</control>
					<control type="image">
						<width>10</width>
						<height>14</height>
						<texture />
					</control>
					<control type="textbox">
						<width>424</width>
						<height>{34 * 8}</height>
						<font>body_24</font>
						<textcolor>body</textcolor>
						<label>$VAR[Sleeve_Desc]</label>
					</control>
				</control>
			</control>
			<!-- the strip of sleeves -->
			<control type="group">
				<include content="Anim_StandUp"><param name="bottom" value="1040"/></include>
				<control type="list" id="508">
					<left>96</left>
					<top>744</top>
					<width>1760</width>
					<height>300</height>
					<orientation>horizontal</orientation>
					<preloaditems>2</preloaditems>
					<scrolltime tween="cubic" easing="out">260</scrolltime>
					<onup>9000</onup>
					<ondown>noop</ondown>
					<onleft>ActivateWindow(1155)</onleft>
					<onright>ActivateWindow(1155)</onright>
					<onback condition="$EXP[Music_AtTabRoot]">9398</onback>
					<viewtype label="Poster">biginfo</viewtype>
					<visible>Container.Content(artists) | Container.Content(albums)</visible>
					<itemlayout width="186" height="300">{strip_card(False)}
					</itemlayout>
					<focusedlayout width="186" height="300">{strip_card(True)}
					</focusedlayout>
				</control>
			</control>
		</control>
	</include>"""


def music_variables():
    return """
	<!-- 0.9.13 views: Crate / Poster -->
	<expression name="Poster_HasFanart">!ListItem.IsParentFolder + [!String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(artist.fanart)) | !String.IsEmpty(ListItem.Art(albumartist.fanart))]</expression>
	<variable name="Poster_Fanart">
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(artist.fanart))">$INFO[ListItem.Art(artist.fanart)]</value>
		<value>$INFO[ListItem.Art(albumartist.fanart)]</value>
	</variable>
	<variable name="Poster_Kicker">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="String.IsEqual(ListItem.DBType,artist)">$VAR[Poster_ArtistKind]$INFO[ListItem.Property(Artist_Genre), · ,]</value>
		<value>$INFO[ListItem.Artist]$INFO[ListItem.Year, · ,]</value>
	</variable>
	<variable name="Poster_ArtistKind">
		<value condition="!String.IsEmpty(ListItem.Property(Artist_Type))">$INFO[ListItem.Property(Artist_Type)]</value>
		<value>Artist</value>
	</variable>
	<variable name="Poster_Facts">
		<value condition="ListItem.IsParentFolder">OK goes up one level</value>
		<value condition="String.IsEqual(ListItem.DBType,artist) + !String.IsEmpty(ListItem.Property(Artist_Formed))">Formed [COLOR ink]$INFO[ListItem.Property(Artist_Formed)][/COLOR]$INFO[ListItem.Property(Artist_Disbanded), · split [COLOR ink],[/COLOR]]</value>
		<value condition="String.IsEqual(ListItem.DBType,artist) + !String.IsEmpty(ListItem.Property(Artist_Born))">Born [COLOR ink]$INFO[ListItem.Property(Artist_Born)][/COLOR]</value>
		<value condition="String.IsEqual(ListItem.DBType,artist)">$INFO[ListItem.Property(Artist_Style)]</value>
		<value>$INFO[ListItem.Genre]$INFO[ListItem.Property(Album_Label), · ,]</value>
	</variable>
	<variable name="Music_Sub">
		<value condition="Control.IsVisible(507) + Integer.IsGreater(Container.NumItems,0) + !ListItem.IsParentFolder">   [COLOR ink]$INFO[ListItem.Label][/COLOR]$INFO[ListItem.Artist,  ·  ,]$INFO[Container.NumItems,  ·  , in all]</value>
		<value>$INFO[Container.NumItems,   ,]</value>
	</variable>"""
