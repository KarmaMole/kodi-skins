"""Generate the video library views: skins/skin.fold/1080i/Includes_Views_Video.xml and 1080i/Timers.xml.
    python skins/skin.fold/_src/make_views.py

Views (MyVideoNav <views>500,501,502,503,505,506,50,509</views>), each gated by Container.Content:
  500 Shelf      films, sets, series, music videos: a 5 x 2 shelf of closed cards that lift and tilt on focus,
                 with the focused card's label in a column on the right (fold_geo.SHELF_*)
  501 Seasons    seasons: the show card on the left, season cards in a row
  502 Concertina episodes: the season pulled open into a zig-zag strip (FoldSeries.html): panels alternate
                 +/-12 deg about their own centres (Integer.IsOdd(ListItem.CurrentItem)), the focused panel
                 flat, lit and 16 % bigger; one shared camera on the list (perspective-origin 1150, 440)
  503 Table      films, sets, series, seasons, music videos: the table covered with small closed cards, 8 across
  505 Leaflet    films, sets, series, seasons, episodes, music videos: the focused title opened as a tri-fold
                 leaflet over a strip of small cards (stills in a season)
  506 Prints     everything: landscape prints (fanart, stills; add-ons and plug-ins keep their own picture)
  509 Accordion  films, sets, series, music videos: the concertina pulled open with posters (0.9.16): panels
                 alternate +/-12 deg, the focused one flat, lit and 16 % bigger; title, story and facts below
                 (503 / 505 / 506: _src/fold_views_more.py, 0.9.13)
  50  List       everything else (Includes_Views.xml)
Header: 9000 filter words (9321 All, 9322 Unwatched, 9323 In progress, 9326 View = the view picker 1156,
9327 Options = the Library panel 1155, 9324 Sort, 9325 direction). Left past the first column (shelf) / off either
end (season cards, concertina) opens the Library panel too.
Kodi ids 3 (sort by), 4 (sort order), 14 (watched toggle, SendClick only).
Timers.xml: a view hidden for the current content is replaced at once (Kodi can select it from a saved
view mode), and the first visit of each content type opens the Fold view.
"""
from pathlib import Path
from fold_geo import (SHELF_X, SHELF_Y, SHELF_SLOT_W, SHELF_SLOT_H, SHELF_PAD_X, SHELF_PAD_Y,
                      SHELF_CARD_W, SHELF_CARD_H, SHELF_LIFT_W, SHELF_LIFT_H, SHELF_COLS)
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po
import fold_views_more as fm

ROOT = Path(__file__).resolve().parents[1] / "1080i"
OUT = ROOT / "Includes_Views_Video.xml"
TIMERS = ROOT / "Timers.xml"
RM = "Skin.HasSetting(fold.reducemotion)"
# Reduce motion keeps a focused lift as a time-0 Conditional on the list's focus, never as a second Focus animation:
# Kodi resets only the FIRST Focus animation on unfocus, so a reduce-motion Focus twin stayed applied (0.9.8).

SHELF_CONTENT = "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(musicvideos)"

# concertina (FoldSeries .pnl): W 196, H 468, top 206, X0 436, ANG 12, ZF 1.16
C_W, C_H, C_TOP, C_X0 = 196, 468, 206, 436
C_SLOT = 192                     # 196 cos 12
C_FSLOT = 18 + 227 + 18          # focused: 196 x 1.16 + 18 either side
C_LIST_TOP = C_TOP - 50          # room for the scaled focused panel
C_LIST_H = C_H + 120


def selcol(xml):
    import re
    return re.sub(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)",
                  lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", xml)


# ------------------------------------------------------------------------------------------ shelf card
def shelf_card(focused):
    w, h = (SHELF_LIFT_W, SHELF_LIFT_H) if focused else (SHELF_CARD_W, SHELF_CARD_H)
    cx = SHELF_PAD_X + SHELF_CARD_W // 2
    bottom = SHELF_PAD_Y + SHELF_CARD_H
    left, top = cx - w // 2, bottom - h
    pl, pt = (19, 17) if focused else (18, 16)
    pw = w - pl - (15 if focused else 14)
    ph = round(pw * 1.5)
    foot_font = "num_22" if focused else "num_20"
    sp = 96 if focused else 48
    tex = "shadow_lift" if focused else "shadow_card"
    lift = ""
    if focused:
        lift = f"""
					<animation type="Focus" condition="!{RM}">
						<effect type="zoom" start="{SHELF_CARD_W / SHELF_LIFT_W * 100:.1f}" end="100" center="{cx},{bottom}" time="260" tween="back" easing="out"/>
						<effect type="rotatex" start="0" end="-9" center="{bottom}" time="260" tween="back" easing="out"/>
					</animation>
					<animation type="Conditional" condition="{RM} + Control.HasFocus(500)">
						<effect type="rotatex" start="-9" end="-9" center="{bottom}" time="0"/>
					</animation>
					<animation type="Unfocus" condition="!{RM}">
						<effect type="rotatex" start="-9" end="0" center="{bottom}" time="180" tween="cubic" easing="out"/>
					</animation>"""
    shadow_anim = ""
    if focused:
        shadow_anim = f"""
				<animation type="Focus" condition="!{RM}">
					<effect type="fade" start="30" end="100" time="260"/>
				</animation>
				<animation type="Unfocus" condition="!{RM}">
					<effect type="fade" start="100" end="45" time="180"/>
				</animation>"""
    return f"""
			<control type="image">
				<left>{left - sp}</left>
				<top>{top - sp}</top>
				<width>{w + 2 * sp}</width>
				<height>{h + 2 * sp}</height>
				<texture border="{sp + 8}" colordiffuse="$VAR[Shelf_ShadowTint]">fold/{tex}.png</texture>{shadow_anim}
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
					<param name="color" value="$VAR[Shelf_CardColor]"/>
					<param name="plate_l" value="{pl}"/>
					<param name="plate_t" value="{pt}"/>
					<param name="plate_w" value="{pw}"/>
					<param name="plate_h" value="{ph}"/>
					<param name="art" value="$VAR[Shelf_Art]"/>
					<param name="foot_l" value="$INFO[ListItem.Year]"/>
					<param name="foot_r" value="$VAR[Shelf_FootR]"/>
					<param name="foot_font" value="{foot_font}"/>
					<param name="foot_b" value="0"/>
					<param name="foot_h" value="{h - pt - ph}"/>
					<param name="foot_aligny" value="center"/>
					<param name="fallback" value="$INFO[ListItem.Label]"/>
				</include>
				<control type="image">
					<left>{pl + pw - 40}</left>
					<top>{pt + 8}</top>
					<width>34</width>
					<height>34</height>
					<texture>fold/punch.png</texture>
					<visible>$EXP[Shelf_Watched] + $EXP[ShowWatchedMarkers]</visible>
				</control>
				<control type="progress">
					<left>{pl}</left>
					<top>{pt + ph - 6}</top>
					<width>{pw}</width>
					<height>6</height>
					<texturebg colordiffuse="99000000">common/white.png</texturebg>
					<midtexture colordiffuse="on_card">common/white.png</midtexture>
					<info>ListItem.PercentPlayed</info>
					<visible>ListItem.IsResumable</visible>
				</control>{'''
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>%d</width>
					<height>%d</height>
					<texture>fold/card_light.png</texture>
					<visible>Control.HasFocus(500)</visible>
				</control>''' % (w, h) if focused else ''}
			</control>
			<!-- the ".." parent item: a cream index card -->
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
					<top>24</top>
					<width>{w - 48}</width>
					<height>80</height>
					<font>disp_64</font>
					<textcolor>$VAR[FoldAccentInk]</textcolor>
					<label>←</label>
				</control>
				<control type="label">
					<left>24</left>
					<top>{h - 70}</top>
					<width>{w - 48}</width>
					<height>40</height>
					<font>tab_22</font>
					<textcolor>ink</textcolor>
					<label>Up a level</label>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{w}</width>
					<height>{h}</height>
					<texture border="4" colordiffuse="$VAR[FoldAccent]">fold/edge_all.png</texture>
					<visible>{'Control.HasFocus(500)' if focused else 'false'}</visible>
				</control>
			</control>"""


def shelf_view():
    return f"""
	<include name="VidView_500_Shelf">
		<control type="group">
			<visible>Control.IsVisible(500)</visible>
			<include content="Anim_StandUp"><param name="bottom" value="{SHELF_Y + SHELF_SLOT_H * 2}"/></include>
			<control type="panel" id="500">
				<left>{SHELF_X}</left>
				<top>{SHELF_Y}</top>
				<width>{SHELF_SLOT_W * SHELF_COLS}</width>
				<height>{SHELF_SLOT_H * 2 + 40}</height>
				<orientation>vertical</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">280</scrolltime>
				<onup>9000</onup>
				<onright>9000</onright>
				<onleft>ActivateWindow(1155)</onleft>
				<onback condition="$EXP[Lib_AtRoot]">9398</onback>
				<viewtype label="Shelf">icon</viewtype>
				<visible>{SHELF_CONTENT}</visible>
				<itemlayout width="{SHELF_SLOT_W}" height="{SHELF_SLOT_H}">{shelf_card(False)}
				</itemlayout>
				<focusedlayout width="{SHELF_SLOT_W}" height="{SHELF_SLOT_H}">{shelf_card(True)}
				</focusedlayout>
			</control>
			<!-- the card label: the focused card's title, facts and story in a column on the right -->
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
					<textcolor>$VAR[FoldAccentInk]</textcolor>
					<label>$VAR[Shelf_Kicker]</label>
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
				<control type="textbox">
					<width>372</width>
					<height max="64">auto</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Shelf_Meta]</label>
				</control>
				<control type="image">
					<width>372</width>
					<height>18</height>
					<texture />
				</control>
				<control type="textbox">
					<width>372</width>
					<height>340</height>
					<font>body_24</font>
					<textcolor>body</textcolor>
					<label>$INFO[ListItem.Plot]</label>
				</control>
				<control type="image">
					<width>372</width>
					<height>18</height>
					<texture />
				</control>
				<control type="label">
					<width>372</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Shelf_Facts]</label>
				</control>
			</control>
		</control>
	</include>"""


# ------------------------------------------------------------------------------------------ show card (left)
def show_card(content_cond, season_label):
    return f"""
		<!-- the show card (FoldSeries .show) with a die-cut season tab -->
		<control type="group">
			<left>96</left>
			<top>166</top>
			<visible>{content_cond}</visible>
			<control type="image">
				<left>-48</left>
				<top>0</top>
				<width>{300 + 96}</width>
				<height>{452 + 96}</height>
				<texture border="56">fold/shadow_card_cool.png</texture>
			</control>
			<control type="group">
				<left>110</left>
				<top>0</top>
				<visible>!String.IsEmpty(ListItem.Season) | Container.Content(seasons)</visible>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>190</width>
					<height>52</height>
					<texture colordiffuse="cobalt">fold/stab.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>190</width>
					<height>52</height>
					<texture diffuse="fold/stab.png">fold/tooth_card_s.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>190</width>
					<height>52</height>
					<texture>fold/stab_shade.png</texture>
				</control>
				<control type="label">
					<left>0</left>
					<top>8</top>
					<width>190</width>
					<height>44</height>
					<align>center</align>
					<font>tab_22</font>
					<textcolor>on_card</textcolor>
					<label>{season_label}</label>
				</control>
			</control>
			<control type="group">
				<left>0</left>
				<top>48</top>
				<width>300</width>
				<height>452</height>
				<include content="Fold_CardBody">
					<param name="w" value="300"/>
					<param name="h" value="452"/>
					<param name="fe_x" value="299"/>
					<param name="fe_h" value="447"/>
					<param name="color" value="cobalt"/>
					<param name="plate_l" value="24"/>
					<param name="plate_t" value="22"/>
					<param name="plate_w" value="258"/>
					<param name="plate_h" value="366"/>
					<param name="art" value="$VAR[Series_ShowPoster]"/>
					<param name="foot_l" value="$VAR[Series_ShowYear]"/>
					<param name="foot_r" value="[UPPERCASE]$VAR[Series_ShowStudio][/UPPERCASE]"/>
					<param name="foot_font" value="num_20"/>
					<param name="foot_b" value="16"/>
					<param name="fallback" value="$INFO[ListItem.TVShowTitle]"/>
				</include>
			</control>
			<control type="textbox">
				<left>0</left>
				<top>534</top>
				<width>320</width>
				<height>130</height>
				<font>disp_64</font>
				<textcolor>ink</textcolor>
				<label>$INFO[ListItem.TVShowTitle]</label>
			</control>
		</control>"""


def watched_cells():
    """Season progress (FoldSeries .bar): one cell per episode, watched cells in cobalt.
    Up to 10 episodes: 24 x 8 cells, pitch 30; 11-20: 12 x 8, pitch 15; more: a plain progress bar."""
    out = []
    for k in range(1, 11):
        out.append(f"""
				<control type="image">
					<left>{(k - 1) * 30}</left>
					<top>0</top>
					<width>24</width>
					<height>8</height>
					<texture colordiffuse="$VAR[Series_Cell{k}]">common/white.png</texture>
					<visible>Integer.IsGreaterOrEqual(Container.NumItems,{k}) + !Integer.IsGreater(Container.NumItems,10)</visible>
				</control>""")
    for k in range(1, 21):
        out.append(f"""
				<control type="image">
					<left>{(k - 1) * 15}</left>
					<top>0</top>
					<width>12</width>
					<height>8</height>
					<texture colordiffuse="$VAR[Series_Cell{k}]">common/white.png</texture>
					<visible>Integer.IsGreaterOrEqual(Container.NumItems,{k}) + Integer.IsGreater(Container.NumItems,10) + !Integer.IsGreater(Container.NumItems,20)</visible>
				</control>""")
    out.append("""
				<control type="progress">
					<left>0</left>
					<top>0</top>
					<width>295</width>
					<height>8</height>
					<texturebg colordiffuse="track">common/white.png</texturebg>
					<midtexture colordiffuse="cobalt">common/white.png</midtexture>
					<info>Container.Property(fold.none)</info>
					<visible>false</visible>
				</control>""")
    return "".join(out)


def cell_vars():
    v = []
    for k in range(1, 21):
        v.append(f"""	<variable name="Series_Cell{k}">
		<value condition="Integer.IsGreaterOrEqual(Container.TotalWatched,{k})">cobalt</value>
		<value>track</value>
	</variable>""")
    return "\n".join(v)


# ------------------------------------------------------------------------------------------ concertina panel
def panel(focused):
    """One concertina panel (FoldSeries .pnl). Unfocused: rotatey +/-12 about its own centre."""
    if focused:
        slot, x = C_FSLOT, 18 + 16    # 227 wide scaled panel centred: 18 + (227 - 196)/2
    else:
        slot, x = C_SLOT, -2
    cx = x + C_W // 2
    top = C_TOP - C_LIST_TOP
    cy = top + C_H // 2
    if focused:
        anim = f"""
				<animation type="Focus" condition="!{RM}">
					<effect type="zoom" start="100" end="116" center="{cx},{cy}" time="220" tween="cubic" easing="out"/>
				</animation>
				<animation type="Conditional" condition="{RM} + Control.HasFocus(502)">
					<effect type="zoom" start="116" end="116" center="{cx},{cy}" time="0"/>
				</animation>
				<animation type="Unfocus">
					<effect type="zoom" start="116" end="116" center="{cx},{cy}" time="0"/>
				</animation>"""
        rot = ""
    else:
        anim = ""
        rot = f"""
				<animation effect="rotatey" start="12" end="12" center="{cx}" time="0" condition="Integer.IsOdd(ListItem.CurrentItem)">Conditional</animation>
				<animation effect="rotatey" start="-12" end="-12" center="{cx}" time="0" condition="!Integer.IsOdd(ListItem.CurrentItem)">Conditional</animation>"""
    shade = ""
    if focused:
        shade = f"""
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/pnl_focus.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>7</height>
					<texture colordiffuse="cobalt">common/white.png</texture>
				</control>"""
    else:
        shade = f"""
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/pnl_lit.png</texture>
					<visible>Integer.IsOdd(ListItem.CurrentItem)</visible>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/pnl_away.png</texture>
					<visible>!Integer.IsOdd(ListItem.CurrentItem)</visible>
				</control>"""
    shadow = f"""
			<control type="image">
				<left>{x - 48 + 4}</left>
				<top>{top - 48 + 8}</top>
				<width>{C_W + 96}</width>
				<height>{C_H + 96}</height>
				<texture border="56">fold/shadow_panel.png</texture>
				<visible>!Integer.IsOdd(ListItem.CurrentItem)</visible>
			</control>""" if not focused else f"""
			<control type="image">
				<left>{x - 64 - 15 + 8}</left>
				<top>{top - 64 - 37 + 20}</top>
				<width>{227 + 128}</width>
				<height>{543 + 128}</height>
				<texture border="72">fold/shadow_panel_on.png</texture>
				<visible>Control.HasFocus(502)</visible>
			</control>"""
    tt_font = "sans_24_semi" if focused else "sans_22_semi"
    return f"""{shadow}
			<control type="group">
				<left>{x}</left>
				<top>{top}</top>
				<width>{C_W}</width>
				<height>{C_H}</height>{rot}{anim}
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture colordiffuse="cream">common/white.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/tooth_cream.png</texture>
				</control>
				<control type="label">
					<left>18</left>
					<top>4</top>
					<width>150</width>
					<height>72</height>
					<font>disp_60</font>
					<textcolor>cobalt</textcolor>
					<label>$VAR[Concertina_Num]</label>
				</control>
				<control type="label">
					<left>104</left>
					<top>28</top>
					<width>44</width>
					<height>30</height>
					<font>caps_20_b</font>
					<textcolor>cobalt</textcolor>
					<label>$INFO[ListItem.Season,S,]</label>
					<visible>!ListItem.IsParentFolder + Integer.IsGreater(ListItem.Season,0)</visible>
				</control>
				<control type="image">
					<left>{C_W - 16 - 32}</left>
					<top>20</top>
					<width>34</width>
					<height>34</height>
					<texture>fold/punch.png</texture>
					<visible>Integer.IsGreater(ListItem.PlayCount,0) + $EXP[ShowWatchedMarkers]</visible>
				</control>
				<control type="image">
					<left>14</left>
					<top>92</top>
					<width>{C_W - 28}</width>
					<height>196</height>
					<texture colordiffuse="cream_deep">common/white.png</texture>
				</control>
				<control type="image">
					<left>14</left>
					<top>92</top>
					<width>{C_W - 28}</width>
					<height>196</height>
					<aspectratio>scale</aspectratio>
					<fadetime>160</fadetime>
					<texture background="true">$VAR[Concertina_Still]</texture>
				</control>
				<control type="textbox">
					<left>18</left>
					<top>302</top>
					<width>{C_W - 32}</width>
					<height>86</height>
					<font>{tt_font}</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Concertina_Title]</label>
				</control>
				<control type="label">
					<left>18</left>
					<top>{C_H - 52}</top>
					<width>{C_W - 34}</width>
					<height>36</height>
					<font>numr_20</font>
					<textcolor>cap</textcolor>
					<label>$INFO[ListItem.Duration(mins),,′]</label>
				</control>
				<control type="label">
					<left>18</left>
					<top>{C_H - 52}</top>
					<width>{C_W - 34}</width>
					<height>36</height>
					<align>right</align>
					<font>numr_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Concertina_State]</label>
				</control>{shade}
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture border="4">fold/pnl_hl.png</texture>
				</control>
			</control>"""


def concertina_view():
    return f"""
	<include name="VidView_502_Concertina">
		<control type="group">
			<visible>Control.IsVisible(502)</visible>{show_card('true', 'Season $INFO[ListItem.Season]')}
			<control type="group">
				<left>96</left>
				<top>{166 + 48 + 452 + 4}</top>
				<control type="label">
					<left>0</left>
					<top>110</top>
					<width>320</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Concertina_ShowMeta]</label>
				</control>
				<control type="label">
					<left>0</left>
					<top>142</top>
					<width>320</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$INFO[Container.TotalWatched]$INFO[Container.NumItems, of , watched]</label>
				</control>
				<control type="group">
					<left>0</left>
					<top>186</top>{watched_cells()}
				</control>
			</control>
			<!-- crumb + position (FoldSeries .crumb / .pos): on the header crumb line -->
			<control type="label">
				<left>96</left>
				<top>118</top>
				<width>720</width>
				<height>32</height>
				<font>caps_20_b</font>
				<textcolor>cobalt</textcolor>
				<label>$VAR[Concertina_Crumb]</label>
			</control>
			<!-- the strip: pulled out like an accordion when the season opens -->
			<control type="group">
				<animation type="Visible" condition="!{RM}">
					<effect type="zoom" start="12,100" end="100,100" center="{C_X0},{C_TOP + C_H // 2}" time="380" tween="cubic" easing="out"/>
					<effect type="fade" start="0" end="100" time="140"/>
				</animation>
				<animation type="WindowOpen" condition="!{RM}">
					<effect type="zoom" start="12,100" end="100,100" center="{C_X0},{C_TOP + C_H // 2}" time="380" tween="cubic" easing="out"/>
					<effect type="fade" start="0" end="100" time="140"/>
				</animation>
				<control type="list" id="502">
					<left>{C_X0}</left>
					<top>{C_LIST_TOP}</top>
					<width>{1920 - C_X0}</width>
					<height>{C_LIST_H}</height>
					<camera x="1150" y="440"/>
					<orientation>horizontal</orientation>
					<preloaditems>2</preloaditems>
					<scrolltime tween="cubic" easing="out">260</scrolltime>
					<onup>9000</onup>
					<ondown>noop</ondown>
					<onleft>ActivateWindow(1155)</onleft>
					<onright>ActivateWindow(1155)</onright>
					<onback condition="$EXP[Lib_AtRoot]">9398</onback>
					<viewtype label="Concertina">list</viewtype>
					<visible>Container.Content(episodes)</visible>
					<itemlayout width="{C_SLOT}" height="{C_LIST_H}">{panel(False)}
					</itemlayout>
					<focusedlayout width="{C_FSLOT}" height="{C_LIST_H}">{panel(True)}
					</focusedlayout>
				</control>
				<!-- crisp contact line along the bottom of the strip -->
				<control type="image">
					<left>{C_X0}</left>
					<top>{C_TOP + C_H - 6}</top>
					<width>{1920 - C_X0}</width>
					<height>12</height>
					<texture colordiffuse="40281e14">fold/score.png</texture>
				</control>
			</control>
			<!-- the focused episode (FoldSeries .detail) -->
			<control type="group">
				<left>440</left>
				<top>742</top>
				<control type="label">
					<left>0</left>
					<top>-8</top>
					<width>1384</width>
					<height>66</height>
					<font>head_50</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Concertina_Head]</label>
				</control>
				<control type="textbox" id="9372">
					<left>0</left>
					<top>70</top>
					<width>1040</width>
					<height>{37 * 3}</height>
					<font>body_26</font>
					<textcolor>body</textcolor>
					<label>$INFO[ListItem.Plot]</label>
				</control>
				<include content="Fold_PlotEllipsis"><param name="id" value="9372"/><param name="right" value="1040"/><param name="top" value="{70 + 37 * 2}"/><param name="pitch" value="37"/><param name="font" value="body_26"/></include>
				<control type="label">
					<left>0</left>
					<top>196</top>
					<width>1384</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Concertina_Facts]</label>
				</control>
			</control>
			<control type="grouplist">
				<left>440</left>
				<top>1012</top>
				<width>1400</width>
				<height>32</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<include content="Fold_KeyHint"><param name="key" value="OK"/><param name="label" value="$VAR[Concertina_OK]"/></include>
				<include content="Fold_KeyHint"><param name="key" value="← →"/><param name="label" value="Along the strip"/></include>
				<include content="Fold_KeyHint"><param name="key" value="BACK"/><param name="label" value="Fold the season"/></include>
			</control>
		</control>
	</include>"""


# ------------------------------------------------------------------------------------------ 509 accordion (0.9.16)
# The concertina for films and series: the same panels (196 x 468, +/-12 deg, focused flat at 116 %) with the year
# as the panel number and a 2:3 poster plate. No <camera> (text under a camera group is clipped on D3D, LESSONS Fold
# 2026-10-28), no show card: the strip starts at the left margin.
A_X0 = 96
A_PLATE_H = 252


def acc_panel(focused):
    if focused:
        slot, x = C_FSLOT, 18 + 16
    else:
        slot, x = C_SLOT, -2
    cx = x + C_W // 2
    top = C_TOP - C_LIST_TOP
    cy = top + C_H // 2
    if focused:
        anim = f"""
				<animation type="Focus" condition="!{RM}">
					<effect type="zoom" start="100" end="116" center="{cx},{cy}" time="220" tween="cubic" easing="out"/>
				</animation>
				<animation type="Conditional" condition="{RM} + Control.HasFocus(509)">
					<effect type="zoom" start="116" end="116" center="{cx},{cy}" time="0"/>
				</animation>
				<animation type="Unfocus">
					<effect type="zoom" start="116" end="116" center="{cx},{cy}" time="0"/>
				</animation>"""
        rot = ""
        shade = f"""
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/pnl_focus.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>7</height>
					<texture colordiffuse="$VAR[Table_CardColor]">common/white.png</texture>
				</control>"""
        shadow = f"""
			<control type="image">
				<left>{x - 64 - 15 + 8}</left>
				<top>{top - 64 - 37 + 20}</top>
				<width>{227 + 128}</width>
				<height>{543 + 128}</height>
				<texture border="72">fold/shadow_panel_on.png</texture>
				<visible>Control.HasFocus(509)</visible>
			</control>"""
    else:
        anim = ""
        rot = f"""
				<animation effect="rotatey" start="12" end="12" center="{cx}" time="0" condition="Integer.IsOdd(ListItem.CurrentItem)">Conditional</animation>
				<animation effect="rotatey" start="-12" end="-12" center="{cx}" time="0" condition="!Integer.IsOdd(ListItem.CurrentItem)">Conditional</animation>"""
        shade = f"""
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/pnl_lit.png</texture>
					<visible>Integer.IsOdd(ListItem.CurrentItem)</visible>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/pnl_away.png</texture>
					<visible>!Integer.IsOdd(ListItem.CurrentItem)</visible>
				</control>"""
        shadow = f"""
			<control type="image">
				<left>{x - 48 + 4}</left>
				<top>{top - 48 + 8}</top>
				<width>{C_W + 96}</width>
				<height>{C_H + 96}</height>
				<texture border="56">fold/shadow_panel.png</texture>
				<visible>!Integer.IsOdd(ListItem.CurrentItem)</visible>
			</control>"""
    tt_font = "sans_24_semi" if focused else "sans_22_semi"
    pt = 82
    return f"""{shadow}
			<control type="group">
				<left>{x}</left>
				<top>{top}</top>
				<width>{C_W}</width>
				<height>{C_H}</height>{rot}{anim}
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture colordiffuse="cream">common/white.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture>fold/tooth_cream.png</texture>
				</control>
				<control type="label">
					<left>18</left>
					<top>10</top>
					<width>{C_W - 70}</width>
					<height>60</height>
					<font>disp_50</font>
					<textcolor>$VAR[Table_CardColor]</textcolor>
					<label>$VAR[Accordion_Num]</label>
				</control>
				<control type="image">
					<left>{C_W - 16 - 32}</left>
					<top>20</top>
					<width>34</width>
					<height>34</height>
					<texture>fold/punch.png</texture>
					<visible>$EXP[Shelf_Watched] + $EXP[ShowWatchedMarkers]</visible>
				</control>
				<!-- the plate: the title printed on the stock under the poster (a poster that fails to load shows it) -->
				<control type="image">
					<left>14</left>
					<top>{pt}</top>
					<width>{C_W - 28}</width>
					<height>{A_PLATE_H}</height>
					<texture colordiffuse="cream_deep">common/white.png</texture>
				</control>
				<control type="textbox">
					<left>24</left>
					<top>{pt + 12}</top>
					<width>{C_W - 48}</width>
					<height>{A_PLATE_H - 24}</height>
					<font>sans_22_semi</font>
					<textcolor>ink2</textcolor>
					<label>$VAR[Accordion_PlateTitle]</label>
				</control>
				<control type="image">
					<left>14</left>
					<top>{pt}</top>
					<width>{C_W - 28}</width>
					<height>{A_PLATE_H}</height>
					<aspectratio>scale</aspectratio>
					<fadetime>160</fadetime>
					<texture background="true">$VAR[Table_Art]</texture>
				</control>
				<control type="textbox">
					<left>18</left>
					<top>{pt + A_PLATE_H + 12}</top>
					<width>{C_W - 32}</width>
					<height>62</height>
					<font>{tt_font}</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Accordion_Title]</label>
				</control>
				<control type="label">
					<left>18</left>
					<top>{C_H - 52}</top>
					<width>{C_W - 34}</width>
					<height>36</height>
					<font>numr_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Shelf_FootR]</label>
				</control>
				<control type="label">
					<left>18</left>
					<top>{C_H - 52}</top>
					<width>{C_W - 34}</width>
					<height>36</height>
					<align>right</align>
					<font>numr_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Concertina_State]</label>
				</control>{shade}
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>{C_W}</width>
					<height>{C_H}</height>
					<texture border="4">fold/pnl_hl.png</texture>
				</control>
			</control>"""


ACC_CONTENT = "Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(musicvideos)"


def accordion_view():
    return f"""
	<include name="VidView_509_Accordion">
		<control type="group">
			<visible>Control.IsVisible(509)</visible>
			<control type="group">
				<animation type="Visible" condition="!{RM}">
					<effect type="zoom" start="12,100" end="100,100" center="{A_X0},{C_TOP + C_H // 2}" time="380" tween="cubic" easing="out"/>
					<effect type="fade" start="0" end="100" time="140"/>
				</animation>
				<animation type="WindowOpen" condition="!{RM}">
					<effect type="zoom" start="12,100" end="100,100" center="{A_X0},{C_TOP + C_H // 2}" time="380" tween="cubic" easing="out"/>
					<effect type="fade" start="0" end="100" time="140"/>
				</animation>
				<control type="list" id="509">
					<left>{A_X0}</left>
					<top>{C_LIST_TOP}</top>
					<width>{1920 - A_X0}</width>
					<height>{C_LIST_H}</height>
					<orientation>horizontal</orientation>
					<preloaditems>2</preloaditems>
					<scrolltime tween="cubic" easing="out">260</scrolltime>
					<onup>9000</onup>
					<ondown>noop</ondown>
					<onleft>ActivateWindow(1155)</onleft>
					<onright>ActivateWindow(1155)</onright>
					<onback condition="$EXP[Lib_AtRoot]">9398</onback>
					<viewtype label="Zigzag">bigwrap</viewtype>
					<visible>{ACC_CONTENT}</visible>
					<itemlayout width="{C_SLOT}" height="{C_LIST_H}">{acc_panel(False)}
					</itemlayout>
					<focusedlayout width="{C_FSLOT}" height="{C_LIST_H}">{acc_panel(True)}
					</focusedlayout>
				</control>
				<control type="image">
					<left>{A_X0}</left>
					<top>{C_TOP + C_H - 6}</top>
					<width>{1920 - A_X0}</width>
					<height>12</height>
					<texture colordiffuse="40281e14">fold/score.png</texture>
				</control>
			</control>
			<!-- the focused title -->
			<control type="group">
				<left>96</left>
				<top>742</top>
				<visible>Integer.IsGreater(Container.NumItems,0)</visible>
				<control type="label">
					<left>0</left>
					<top>-8</top>
					<width>1728</width>
					<height>66</height>
					<font>head_50</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Accordion_Head]</label>
				</control>
				<control type="textbox" id="9373">
					<left>0</left>
					<top>70</top>
					<width>1240</width>
					<height>{37 * 3}</height>
					<font>body_26</font>
					<textcolor>body</textcolor>
					<label>$VAR[Accordion_Plot]</label>
				</control>
				<include content="Fold_PlotEllipsis"><param name="id" value="9373"/><param name="right" value="1240"/><param name="top" value="{70 + 37 * 2}"/><param name="pitch" value="37"/><param name="font" value="body_26"/></include>
				<control type="label">
					<left>0</left>
					<top>196</top>
					<width>1728</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Accordion_Facts]</label>
				</control>
			</control>
			<control type="grouplist">
				<left>96</left>
				<top>1012</top>
				<width>1700</width>
				<height>32</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<include content="Fold_KeyHint"><param name="key" value="OK"/><param name="label" value="$VAR[Accordion_OK]"/></include>
				<include content="Fold_KeyHint"><param name="key" value="← →"/><param name="label" value="Along the strip"/></include>
				<include content="Fold_KeyHint"><param name="key" value="BACK"/><param name="label" value="Fold it closed"/></include>
			</control>
		</control>
	</include>"""


ACC_VARS = """
	<!-- 0.9.16 Accordion 509 -->
	<variable name="Accordion_Num">
		<value condition="ListItem.IsParentFolder">←</value>
		<value condition="String.IsEqual(ListItem.DBType,set) + !String.IsEmpty(ListItem.Property(Total))">$INFO[ListItem.Property(Total)]</value>
		<value>$INFO[ListItem.Year]</value>
	</variable>
	<variable name="Accordion_Title">
		<value condition="ListItem.IsParentFolder">Up a level</value>
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Accordion_PlateTitle">
		<value condition="ListItem.IsParentFolder"></value>
		<value>$VAR[Accordion_Title]</value>
	</variable>
	<variable name="Accordion_Head">
		<value condition="ListItem.IsParentFolder">Up a level</value>
		<value>$VAR[Accordion_Title]</value>
	</variable>
	<variable name="Accordion_Plot">
		<value condition="ListItem.IsParentFolder">OK goes up one level.</value>
		<value>$INFO[ListItem.Plot]</value>
	</variable>
	<variable name="Accordion_Facts">
		<value condition="ListItem.IsParentFolder"></value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow) + Integer.IsEqual(ListItem.Property(TotalSeasons),1)">$INFO[ListItem.Year]$INFO[ListItem.Studio,  ·  ,]  ·  1 season$VAR[Fold_N_TotalEpisodes_episodes]$INFO[ListItem.Property(UnWatchedEpisodes),  ·  , unwatched]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$INFO[ListItem.Studio,  ·  ,]$VAR[Fold_N_TotalSeasons_seasons]$VAR[Fold_N_TotalEpisodes_episodes]$INFO[ListItem.Property(UnWatchedEpisodes),  ·  , unwatched]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Collection$VAR[Fold_N_Total_films]$INFO[ListItem.Property(Watched),  ·  , watched]</value>
		<value condition="!String.IsEmpty(ListItem.Year)">$INFO[ListItem.Year]$INFO[ListItem.Duration(mins),  ·  , min]$INFO[ListItem.Genre,  ·  ,]$INFO[ListItem.Director,  ·  ,]</value>
		<value>$INFO[ListItem.Genre]</value>
	</variable>
	<variable name="Accordion_OK">
		<value condition="ListItem.IsParentFolder">Up a level</value>
		<value condition="ListItem.IsFolder">Open</value>
		<value>Play</value>
	</variable>"""


# ------------------------------------------------------------------------------------------ seasons
def season_card(focused):
    w, h = (SHELF_LIFT_W, SHELF_LIFT_H) if focused else (SHELF_CARD_W, SHELF_CARD_H)
    slot_w = SHELF_SLOT_W
    cx = SHELF_PAD_X + SHELF_CARD_W // 2
    bottom = SHELF_PAD_Y + SHELF_CARD_H
    left, top = cx - w // 2, bottom - h
    xml = shelf_card(focused).replace("Control.HasFocus(500)", "Control.HasFocus(501)")
    return xml


def seasons_view():
    return f"""
	<include name="VidView_501_Seasons">
		<control type="group">
			<visible>Control.IsVisible(501)</visible>{show_card('true', '$VAR[Fold_N_ContainerNumItems_seasons]')}
			<control type="label">
				<left>440</left>
				<top>146</top>
				<width>1000</width>
				<height>32</height>
				<font>caps_20_b</font>
				<textcolor>cobalt</textcolor>
				<label>$INFO[ListItem.TVShowTitle][COLOR cap2]   choose a season to pull it open[/COLOR]</label>
			</control>
			<control type="group">
				<include content="Anim_StandUp"><param name="bottom" value="{SHELF_Y + 40 + SHELF_SLOT_H}"/></include>
				<control type="list" id="501">
					<left>{440 - SHELF_PAD_X}</left>
					<top>{SHELF_Y + 40}</top>
					<width>{SHELF_SLOT_W * 5 + 40}</width>
					<height>{SHELF_SLOT_H + 40}</height>
					<orientation>horizontal</orientation>
					<preloaditems>2</preloaditems>
					<scrolltime tween="cubic" easing="out">260</scrolltime>
					<onup>9000</onup>
					<ondown>noop</ondown>
					<onleft>ActivateWindow(1155)</onleft>
					<onright>ActivateWindow(1155)</onright>
					<onback condition="$EXP[Lib_AtRoot]">9398</onback>
					<viewtype label="Seasons">list</viewtype>
					<visible>Container.Content(seasons)</visible>
					<itemlayout width="{SHELF_SLOT_W}" height="{SHELF_SLOT_H}">{season_card(False)}
					</itemlayout>
					<focusedlayout width="{SHELF_SLOT_W}" height="{SHELF_SLOT_H}">{season_card(True)}
					</focusedlayout>
				</control>
			</control>
			<control type="group">
				<left>440</left>
				<top>{SHELF_Y + 40 + SHELF_SLOT_H + 40}</top>
				<control type="label">
					<left>0</left>
					<top>0</top>
					<width>1384</width>
					<height>66</height>
					<font>head_50</font>
					<textcolor>ink</textcolor>
					<label>$VAR[VidView_ItemTitle]</label>
				</control>
				<control type="label">
					<left>0</left>
					<top>70</top>
					<width>1384</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Seasons_Meta]</label>
				</control>
				<control type="textbox">
					<left>0</left>
					<top>116</top>
					<width>1100</width>
					<height>{37 * 3}</height>
					<font>body_26</font>
					<textcolor>body</textcolor>
					<label>$INFO[ListItem.Plot]</label>
				</control>
			</control>
		</control>
	</include>"""


# ------------------------------------------------------------------------------------------ header
def header():
    def word(bid, label, vis, onclick, width=None, active=None):
        wtag = f"<width>{width}</width>" if width else "<width>auto</width>"
        col = f"$VAR[{active}]" if active else "ink2"
        clicks = "".join(f"\n\t\t\t\t<onclick{(' condition=' + chr(34) + c + chr(34)) if c else ''}>{a}</onclick>" for c, a in onclick)
        return f"""
			<control type="button" id="{bid}">
				{wtag}
				<height>40</height>
				<font>caps_20_b</font>
				<textcolor>{col}</textcolor>
				<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
				<align>center</align>
				<textoffsetx>12</textoffsetx>
				<texturefocus border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texturefocus>
				<texturenofocus border="6" colordiffuse="$VAR[{active}_Tex]">fold/chip.png</texturenofocus>
				<label>{label}</label>{clicks}
				<visible>{vis}</visible>
			</control>""" if active else f"""
			<control type="button" id="{bid}">
				{wtag}
				<height>40</height>
				<font>caps_20_b</font>
				<textcolor>ink2</textcolor>
				<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
				<align>center</align>
				<textoffsetx>12</textoffsetx>
				<texturefocus border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texturefocus>
				<texturenofocus />
				<label>{label}</label>{clicks}
				<visible>{vis}</visible>
			</control>"""
    return f"""
	<include name="VidView_Header">
		<control type="group">
			<visible>!Control.IsVisible(502)</visible>
			<include content="Fold_RowHead">
				<param name="top" value="118"/>
				<param name="label" value="$VAR[VidView_Title]"/>
				<param name="sub" value="$VAR[VidView_Sub]"/>
				<param name="width" value="720"/>
			</include>
		</control>
		<!-- filter words on the top edge: fixed widths first, the sort words (which change) last -->
		<control type="grouplist" id="9000">
			<left>760</left>
			<top>112</top>
			<width>1070</width>
			<height>40</height>
			<orientation>horizontal</orientation>
			<align>right</align>  <!-- 0.9.7: ends at the margin, so the crumb on the left keeps its room (Options added) -->
			<itemgap>6</itemgap>
			<onup>noop</onup>
			<ondown condition="Control.IsVisible(500)">500</ondown>
			<ondown condition="Control.IsVisible(501)">501</ondown>
			<ondown condition="Control.IsVisible(502)">502</ondown>
			<ondown condition="Control.IsVisible(503)">503</ondown>
			<ondown condition="Control.IsVisible(505)">505</ondown>
			<ondown condition="Control.IsVisible(506)">506</ondown>
			<ondown>50</ondown>
			<onleft>noop</onleft>
			<onright>noop</onright>
			<onback condition="Control.IsVisible(500)">500</onback>
			<onback condition="Control.IsVisible(501)">501</onback>
			<onback condition="Control.IsVisible(502)">502</onback>
			<onback condition="Control.IsVisible(503)">503</onback>
			<onback condition="Control.IsVisible(505)">505</onback>
			<onback condition="Control.IsVisible(506)">506</onback>
			<onback condition="Control.IsVisible(50)">50</onback>{word(9321, 'All $VAR[VidView_CountAll]', '$EXP[VidView_IsLibraryVideo] | $EXP[VidView_IsInProgressTV]', [('$EXP[VidView_IsInProgressTV]', 'Action(ParentDir)'), ('!$EXP[VidView_IsInProgressTV] + System.Setting(hidewatched)', 'SendClick(14)')], 163, 'VidView_ColNavAll')}{word(9322, 'Unwatched $VAR[VidView_CountUnwatched]', 'Container.Content(movies) | Container.Content(sets) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(musicvideos)', [('!System.Setting(hidewatched)', 'SendClick(14)')], 238, 'VidView_ColNavUnwatched')}{word(9323, 'In progress', '$EXP[VidView_IsTVRoot] | $EXP[VidView_IsInProgressTV]', [('!$EXP[VidView_IsInProgressTV]', 'Container.Update(videodb://inprogresstvshows/)')], 193, 'VidView_ColNavInProgress')}{word(9326, '$VAR[VidView_ViewWord]', 'Integer.IsGreater(Container.ViewCount,1)', [('', 'ActivateWindow(1156)')], 221)}{word(9327, 'Options', 'true', [('', 'ActivateWindow(1155)')], 134)}{word(9324, 'Sort $INFO[Container.SortMethod]', 'Control.IsEnabled(3)', [('', 'SendClick(3)')])}{word(9325, '$VAR[VidView_SortArrow]', 'Control.IsEnabled(4)', [('', 'SendClick(4)')], 44)}
		</control>
		<control type="button" id="3">
			<description>Sort by (Kodi)</description>
			<include>Fold_Hidden</include>
		</control>
		<control type="button" id="4">
			<description>Sort order (Kodi)</description>
			<include>Fold_Hidden</include>
		</control>
		<!-- Back at the window's start folder leaves for Home in one press (LESSONS round 3, Sentence) -->
		<control type="button" id="9398">
			<include>Fold_Hidden</include>
			<visible allowhiddenfocus="true">false</visible>
			<onfocus>ActivateWindow(Home)</onfocus>
		</control>
	</include>"""


def build():
    x = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_views.py - edit the generator, not this file. -->
<!--{__doc__}-->
<includes>
	<!-- ================================================================ expressions -->
	<expression name="VidView_IsInProgressTV">String.StartsWith(Container.FolderPath,videodb://inprogresstvshows)</expression>
	<expression name="VidView_IsMoviesRoot">Container.Content(movies) + String.StartsWith(Container.FolderPath,videodb://movies/titles)</expression>
	<expression name="VidView_IsTVRoot">Container.Content(tvshows) + String.StartsWith(Container.FolderPath,videodb://tvshows/titles)</expression>
	<expression name="VidView_IsLibraryVideo">Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(musicvideos)</expression>
	<expression name="VidView_NavActiveAll">!System.Setting(hidewatched) + !String.StartsWith(Container.FolderPath,videodb://inprogresstvshows)</expression>
	<expression name="VidView_IsFolderType">String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season) | String.IsEqual(ListItem.DBType,set)</expression>
	<expression name="VidView_IsTVType">String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season)</expression>
	<expression name="Shelf_Watched">[!$EXP[VidView_IsFolderType] + Integer.IsGreater(ListItem.PlayCount,0)] | [$EXP[VidView_IsTVType] + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0) + Integer.IsGreater(ListItem.Property(TotalEpisodes),0)]</expression>
	<!-- the library's start folder (Back leaves to Home from here in one press) -->
	<expression name="Lib_AtRoot">String.IsEqual(Container.FolderPath,videodb://movies/titles/) | String.IsEqual(Container.FolderPath,videodb://tvshows/titles/) | String.IsEqual(Container.FolderPath,videodb://inprogresstvshows/)</expression>

	<!-- ================================================================== variables -->
	<variable name="VidView_Title">
		<value condition="Container.Content(episodes) + !String.IsEmpty(ListItem.TVShowTitle)">$INFO[ListItem.TVShowTitle]</value>
		<value condition="$EXP[VidView_IsMoviesRoot]">$LOCALIZE[31200]</value>
		<value condition="$EXP[VidView_IsTVRoot] | $EXP[VidView_IsInProgressTV]">$LOCALIZE[31201]</value>
		<value condition="!String.IsEmpty(Container.FolderName)">$INFO[Container.FolderName]</value>
		<value>$LOCALIZE[3]</value>
	</variable>
	<variable name="VidView_Sub">
		<value condition="Control.IsVisible(503) + Integer.IsGreater(Container.NumItems,0) + !ListItem.IsParentFolder">   [COLOR ink]$INFO[ListItem.Label][/COLOR]$INFO[ListItem.Year,  ·  ,]$INFO[Container.NumItems,  ·  , in all]</value>
		<value condition="$EXP[VidView_IsInProgressTV]">   in progress</value>
		<value condition="Container.Content(episodes) + !String.IsEqual(Container.FolderName,ListItem.TVShowTitle)">   $INFO[Container.FolderName]$VAR[Fold_N_ContainerNumItems_episodes]</value>
		<value condition="Container.Content(episodes)">$VAR[Fold_N_ContainerNumItems_episodes2]</value>
		<value>$INFO[Container.NumItems,   ,]</value>
	</variable>
	<variable name="VidView_CountAll">
		<value condition="$EXP[VidView_IsInProgressTV]">$INFO[Window(Home).Property(fold.n.series)]</value>
		<value condition="System.Setting(hidewatched) + $EXP[VidView_IsMoviesRoot]">$INFO[Window(Home).Property(fold.n.films)]</value>
		<value condition="System.Setting(hidewatched) + $EXP[VidView_IsTVRoot]">$INFO[Window(Home).Property(fold.n.series)]</value>
		<value condition="!System.Setting(hidewatched)">$INFO[Container.NumItems]</value>
	</variable>
	<variable name="VidView_CountUnwatched">
		<value condition="System.Setting(hidewatched)">$INFO[Container.NumItems]</value>
		<value>$INFO[Container.TotalUnWatched]</value>
	</variable>
	<variable name="VidView_SortArrow">
		<value condition="Container.SortDirection(descending)">↓</value>
		<value>↑</value>
	</variable>
	<variable name="VidView_ViewWord">
		<value condition="Control.IsVisible(50)">View: list</value>
		<value condition="Control.IsVisible(502)">View: strip</value>
		<value condition="Control.IsVisible(503)">View: table</value>
		<value condition="Control.IsVisible(505)">View: leaflet</value>
		<value condition="Control.IsVisible(506)">View: prints</value>
		<value condition="Control.IsVisible(501)">View: cards</value>
		<value condition="Control.IsVisible(509)">View: zigzag</value>
		<value>View: shelf</value>
	</variable>
	<!-- the active filter word sits on a pale chip -->
	<variable name="VidView_ColNavAll">
		<value condition="$EXP[VidView_NavActiveAll]">ink</value>
		<value>ink2</value>
	</variable>
	<variable name="VidView_ColNavAll_Tex">
		<value condition="$EXP[VidView_NavActiveAll]">1f1d1b18</value>
		<value>00ffffff</value>
	</variable>
	<variable name="VidView_ColNavUnwatched">
		<value condition="System.Setting(hidewatched)">ink</value>
		<value>ink2</value>
	</variable>
	<variable name="VidView_ColNavUnwatched_Tex">
		<value condition="System.Setting(hidewatched)">1f1d1b18</value>
		<value>00ffffff</value>
	</variable>
	<variable name="VidView_ColNavInProgress">
		<value condition="$EXP[VidView_IsInProgressTV]">ink</value>
		<value>ink2</value>
	</variable>
	<variable name="VidView_ColNavInProgress_Tex">
		<value condition="$EXP[VidView_IsInProgressTV]">1f1d1b18</value>
		<value>00ffffff</value>
	</variable>
	<variable name="VidView_ItemTitle">
		<value condition="ListItem.IsParentFolder">Up a level</value>
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="VidView_MPAA">
		<value condition="String.IsEqual(ListItem.MPAA,Rated R)">R</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated PG-13)">PG-13</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated PG)">PG</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated G)">G</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated NR) | String.IsEqual(ListItem.MPAA,Rated)"></value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated NC-17)">NC-17</value>
		<value>$INFO[ListItem.MPAA]</value>
	</variable>
	<!-- shelf -->
	<variable name="Shelf_CardColor">
		<value condition="Container.Content(tvshows)">cobalt</value>
		<value>verm</value>
	</variable>
	<variable name="Shelf_ShadowTint">
		<value>white</value>
	</variable>
	<variable name="Shelf_Art">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Shelf_FootR">
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Property(TotalSeasons),, S]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$VAR[Fold_N_Total_films2]</value>
		<value>$INFO[ListItem.Duration(mins),,′]</value>
	</variable>
	<variable name="Shelf_Kicker">
		<value condition="ListItem.IsParentFolder">Back</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$INFO[ListItem.Studio, · ,]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Collection$VAR[Fold_N_Total_films3]</value>
		<value>$INFO[ListItem.Year]$INFO[ListItem.Duration(mins), · , min]$VAR[Shelf_MPAA]</value>
	</variable>
	<variable name="Shelf_MPAA">
		<value condition="String.IsEmpty(ListItem.MPAA)"></value>
		<value> · $VAR[VidView_MPAA]</value>
	</variable>
	<variable name="Shelf_Meta">
		<value condition="ListItem.IsParentFolder">OK goes up one level</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$VAR[Fold_N_TotalSeasons_seasonsdot]$INFO[ListItem.Property(WatchedEpisodes)]$INFO[ListItem.Property(TotalEpisodes), of , watched]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Watched)]$INFO[ListItem.Property(Total), of , watched]</value>
		<value>$INFO[ListItem.Director,,[CR]]$INFO[ListItem.Genre]</value>
	</variable>
	<variable name="Shelf_Facts">
		<value condition="ListItem.IsResumable">Stopped at $INFO[ListItem.PercentPlayed]%</value>
		<value condition="!$EXP[VidView_IsFolderType] + !String.IsEmpty(ListItem.Duration)">$INFO[ListItem.Rating,Rating [COLOR ink],[/COLOR]   ]Ends [COLOR ink]$INFO[ListItem.EndTime][/COLOR]</value>
		<value>$INFO[ListItem.Rating,Rating [COLOR ink],[/COLOR]]</value>
	</variable>
	<!-- series -->
	<variable name="Series_ShowPoster">
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(season.poster))">$INFO[ListItem.Art(season.poster)]</value>
		<value>$INFO[ListItem.Art(poster)]</value>
	</variable>
	<variable name="Series_ShowYear">
		<value>$INFO[ListItem.Year]</value>
	</variable>
	<variable name="Series_ShowStudio">
		<value>$INFO[ListItem.Studio]</value>
	</variable>
{cell_vars()}
	<variable name="Concertina_Num">
		<value condition="ListItem.IsParentFolder">←</value>
		<value condition="Integer.IsLess(ListItem.Episode,10) + !String.IsEmpty(ListItem.Episode)">[UPPERCASE]0$INFO[ListItem.Episode][/UPPERCASE]</value>
		<value>$INFO[ListItem.Episode]</value>
	</variable>
	<variable name="Concertina_Title">
		<value condition="ListItem.IsParentFolder">Up to the seasons</value>
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Concertina_Still">
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value>$INFO[ListItem.Art(tvshow.fanart)]</value>
	</variable>
	<variable name="Concertina_State">
		<value condition="ListItem.IsResumable">$INFO[ListItem.PercentPlayed,,%]</value>
		<value condition="Integer.IsGreater(ListItem.PlayCount,0)">watched</value>
	</variable>
	<variable name="Concertina_Crumb">
		<value condition="Integer.IsEqual(Container.NumItems,1)">$INFO[Container.FolderName][COLOR cap2]   pulled open · 1 episode[/COLOR]</value>
		<value>$INFO[Container.FolderName][COLOR cap2]   pulled open$VAR[Fold_N_ContainerNumItems_episodes3]   ·   [/COLOR][COLOR cobalt]$INFO[Container.CurrentItem][/COLOR][COLOR cap2]$INFO[Container.NumItems, / ,][/COLOR]</value>
	</variable>
	<variable name="Concertina_Head">
		<value condition="ListItem.IsParentFolder">Up to the seasons</value>
		<value>[COLOR cobalt]$INFO[ListItem.Episode][/COLOR][COLOR mute] · [/COLOR]$INFO[ListItem.Title]$INFO[ListItem.Duration(mins),[COLOR mute] · [/COLOR], min]</value>
	</variable>
	<variable name="Concertina_Facts">
		<value condition="ListItem.IsParentFolder"></value>
		<value condition="!String.IsEmpty(ListItem.Premiered) + !String.IsEmpty(ListItem.LastPlayed)">Aired [COLOR ink]$VAR[Date_PR][/COLOR]      Watched [COLOR ink]$VAR[Date_LP][/COLOR]$INFO[ListItem.EndTime,      Ends [COLOR ink],[/COLOR]]</value>
		<value condition="!String.IsEmpty(ListItem.Premiered)">Aired [COLOR ink]$VAR[Date_PR][/COLOR]$INFO[ListItem.EndTime,      Ends [COLOR ink],[/COLOR]]</value>
		<value>$INFO[ListItem.EndTime,Ends [COLOR ink],[/COLOR]]</value>
	</variable>
	<variable name="Concertina_ShowMeta">
		<value>$INFO[ListItem.Genre,[COLOR ink],[/COLOR]]$INFO[ListItem.Rating,  ·  Rating [COLOR ink],[/COLOR]]</value>
	</variable>
	<variable name="Concertina_OK">
		<value condition="ListItem.IsParentFolder">Up a level</value>
		<value>Play episode $INFO[ListItem.Episode]</value>
	</variable>
	<variable name="Seasons_Meta">
		<value condition="ListItem.IsParentFolder">OK goes up one level</value>
		<value>$VAR[Fold_N_TotalEpisodes_episodes2]$INFO[ListItem.Property(WatchedEpisodes), · , watched]$INFO[ListItem.Year, · ,]</value>
	</variable>
{fm.variables()}
{ACC_VARS}
{shelf_view()}
{seasons_view()}
{concertina_view()}
{fm.table_view()}
{fm.leaflet_view()}
{fm.prints_view()}
{accordion_view()}
{header()}

	<include name="VidView_Empty">
		<control type="group">
			<visible>Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating</visible>
			<!-- 0.9.13: under the first row of cards (the ".." card stands where the message was) -->
			<animation effect="slide" start="0,0" end="0,350" time="0" condition="Control.IsVisible(500)">Conditional</animation>
			<animation effect="slide" start="0,0" end="0,230" time="0" condition="Control.IsVisible(503)">Conditional</animation>
			<animation effect="slide" start="0,0" end="0,300" time="0" condition="Control.IsVisible(506)">Conditional</animation>
			<animation effect="slide" start="0,0" end="0,500" time="0" condition="Control.IsVisible(509)">Conditional</animation>
			<control type="label">
				<left>96</left>
				<top>240</top>
				<width>1200</width>
				<height>80</height>
				<font>disp_64</font>
				<textcolor>ink</textcolor>
				<label>Nothing in this folder.</label>
			</control>
			<control type="label">
				<left>96</left>
				<top>330</top>
				<width>1200</width>
				<height>40</height>
				<font>light_32</font>
				<textcolor>ink2</textcolor>
				<label>Back folds it closed.</label>
			</control>
		</control>
	</include>

	<include name="VidView_Window">
		<include>Fold_Background</include>
		<include>Fold_Tabs</include>
		<include>Fold_Clock</include>
		<include>VidView_500_Shelf</include>
		<include>VidView_501_Seasons</include>
		<include>VidView_502_Concertina</include>
		<include>VidView_503_Table</include>
		<include>VidView_505_Leaflet</include>
		<include>VidView_506_Prints</include>
		<include>VidView_509_Accordion</include>
		<include>View_50_List</include>
		<include>VidView_Empty</include>
		<include>VidView_Header</include>
	</include>
</includes>
"""
    OUT.write_text(finish_xml(selcol(x)), encoding="utf-8", newline="\n")
    print("Includes_Views_Video.xml written")

    t = ['<?xml version="1.0" encoding="UTF-8"?>',
         "<!-- GENERATED by _src/make_views.py. View self-correction + first-visit defaults (LESSONS: Orbit timers). -->",
         "<timers>"]
    fix = [("movies", "500"), ("sets", "500"), ("tvshows", "500"), ("musicvideos", "500"), ("seasons", "501"), ("episodes", "502")]
    # 0.9.13: the views each content type offers (a view the user picked must never be undone)
    valid = {"movies": ["500", "503", "505", "506", "509"], "sets": ["500", "503", "505", "506", "509"],
             "tvshows": ["500", "503", "505", "506", "509"], "musicvideos": ["500", "503", "505", "506", "509"],
             "seasons": ["501", "503", "505", "506"], "episodes": ["502", "505", "506"]}
    for content, view in fix:
        none_vis = " + ".join(f"!Control.IsVisible({v})" for v in valid[content])
        any_vis = " | ".join(f"Control.IsVisible({v})" for v in valid[content])
        t.append(f"""	<timer>
		<name>fold_view_first_{content}</name>
		<start>Window.IsActive(videos) + Container.Content({content}) + !Container.IsUpdating + Integer.IsGreater(Container.NumItems,0) + !Skin.HasSetting(fold.vreset.{content})</start>
		<stop>Skin.HasSetting(fold.vreset.{content}) | !Window.IsActive(videos)</stop>
		<onstart>Container.SetViewMode({view})</onstart>
		<onstart>Skin.SetBool(fold.vreset.{content})</onstart>
	</timer>
	<timer>
		<name>fold_view_fix_{content}</name>
		<start>Window.IsActive(videos) + Container.Content({content}) + !Container.IsUpdating + Integer.IsGreater(Container.NumItems,0) + {none_vis} + !Control.IsVisible(50) + !System.HasActiveModalDialog + !Window.IsVisible(1155) + !Window.IsVisible(1156)</start>
		<stop>{any_vis} | Control.IsVisible(50) | !Window.IsActive(videos)</stop>
		<onstart>Container.SetViewMode({view})</onstart>
	</timer>""")
    t.append(f"""	<timer>
		<name>fold_view_fix_other</name>
		<start>Window.IsActive(videos) + !Container.IsUpdating + Integer.IsGreater(Container.NumItems,0) + !Control.IsVisible(500) + !Control.IsVisible(501) + !Control.IsVisible(502) + !Control.IsVisible(503) + !Control.IsVisible(505) + !Control.IsVisible(506) + !Control.IsVisible(509) + !Control.IsVisible(50) + !System.HasActiveModalDialog + !Window.IsVisible(1155) + !Window.IsVisible(1156)</start>
		<stop>Control.IsVisible(500) | Control.IsVisible(501) | Control.IsVisible(502) | Control.IsVisible(503) | Control.IsVisible(505) | Control.IsVisible(506) | Control.IsVisible(509) | Control.IsVisible(50) | !Window.IsActive(videos)</stop>
		<onstart>Container.SetViewMode(50)</onstart>
	</timer>""")
    for content in ("albums", "artists"):
        t.append(f"""	<timer>
		<name>fold_music_first_{content}</name>
		<start>Window.IsActive(music) + Container.Content({content}) + !Container.IsUpdating + Integer.IsGreater(Container.NumItems,0) + !Skin.HasSetting(fold.vreset.{content})</start>
		<stop>Skin.HasSetting(fold.vreset.{content}) | !Window.IsActive(music)</stop>
		<onstart>Container.SetViewMode(504)</onstart>
		<onstart>Skin.SetBool(fold.vreset.{content})</onstart>
	</timer>""")
    t.append("""	<timer>
		<name>fold_music_fix</name>
		<start>Window.IsActive(music) + !Container.IsUpdating + Integer.IsGreater(Container.NumItems,0) + !Control.IsVisible(504) + !Control.IsVisible(507) + !Control.IsVisible(508) + !Control.IsVisible(50) + !System.HasActiveModalDialog + !Window.IsVisible(1155) + !Window.IsVisible(1156)</start>
		<stop>Control.IsVisible(504) | Control.IsVisible(507) | Control.IsVisible(508) | Control.IsVisible(50) | !Window.IsActive(music)</stop>
		<onstart>Container.SetViewMode(50)</onstart>
	</timer>""")
    t.append("</timers>\n")
    TIMERS.write_text(finish_xml("\n".join(t)), encoding="utf-8", newline="\n")
    print("Timers.xml written")


if __name__ == "__main__":
    build()
