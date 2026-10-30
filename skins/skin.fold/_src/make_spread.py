"""Generate the info spread: skins/skin.fold/1080i/Includes_VideoInfo.xml (DialogVideoInfo.xml includes it).
    python skins/skin.fold/_src/make_spread.py

Design contract: docs/concepts/round4/mockups/FoldOpen.html + FoldHalfOpen.html.
The card opens in place: the closed card (cover) travels from the slot it stood in to the centre, the cover
swings open on its left hinge in TWO PHASES (Kodi has no back-face culling: the cover turns 0 -> +90 and hides,
then the inside face turns -90 -> 0 on the same hinge), and the right flap unfolds (+90 -> 0). Fold shading
overlays fade in the same timings. Back runs it in reverse. Everything stays inside 450 ms.

Kodi rotation conventions (proven on the Shield, 2026-10-19, _device/fold-probe2.png):
  rotatey center="x[,z]": +angle brings the side RIGHT of the hinge toward the viewer (CSS is the opposite)
  rotatex center="y[,z]": -angle brings the side ABOVE the hinge toward the viewer
  <camera x y> is in the parent's coordinate space; Kodi's eye sits 2 x 540 = 1080 px in front of the screen.

Kodi ids (Estuary Omega DialogVideoInfo + CGUIDialogVideoInfo): 8 play (from start when 9 exists; browses
tvshow/season/set), 9 resume, 11 trailer, 50 cast (or the films of a set), 6 refresh, 7 user rating,
10 choose art, 12 choose fanart, 13 director search, 14 versions, 15 extras, 443 go to collection.
Fold ids: 9000 action words, 9010 More, 9012 Open (folders, sends 8), 9013 From start (sends 8),
9100 More note, 9101 Full plot, 9200 full-plot note + scrollbar 61, 9310-9312 title probes.
"""
from pathlib import Path
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

ROOT = Path(__file__).resolve().parents[1] / "1080i"
OUT = ROOT / "Includes_VideoInfo.xml"
RM = "Skin.HasSetting(fold.reducemotion)"

# panels (FoldOpen .panel)
TOP, H, W = 186, 770, 560
P1, P2, P3 = 120, 680, 1240
HINGE_L, HINGE_R = P2, P3
CX, CY = P2 + W // 2, TOP + H // 2          # closed cover centre (960, 571)

# timeline (ms)
T_MOVE = 190          # card travels to the centre
C_DELAY, C_TIME = 110, 170      # cover 0 -> 90
I_DELAY, I_TIME = C_DELAY + C_TIME, 160   # inside face -90 -> 0 (ends 440)
F_DELAY, F_TIME = 200, 230      # flap 90 -> 0 (ends 430)
# close
X_FLAP, X_INS = 160, 150
X_COVER_D, X_COVER_T = 150, 150
X_BACK_D, X_BACK_T = 290, 150   # back to the slot (ends 440)


def slots():
    """(condition, dx, dy, zx, zy) where the closed card stood when OK was pressed."""
    out = []
    # Home row A (0.9.3): resting card 214 x 330 at left 96 + 248 s, zoomed 115.9 % about its bottom centre (y 542)
    for s in range(7):
        cx, cy = 96 + 248 * s + 107, 542 - 191
        out.append((f"String.IsEqual(Window(Home).Property(fold.from),h{s})", cx - CX, cy - CY, 248 / W * 100, 382 / H * 100))
    # Home row B (page slid up 330, card lifted 10): cream card 270 x 220 at 96 + 294 s, top 572
    for s in range(6):
        cx, cy = 96 + 294 * s + 135, 572 + 110
        out.append((f"String.IsEqual(Window(Home).Property(fold.from),b{s})", cx - CX, cy - CY, 270 / W * 100, 220 / H * 100))
    # Library shelf (view 500): 5 x 2 cards 248 x 382 (focused), see make_views.py (SHELF_*)
    from fold_geo import SHELF_SLOTS
    for pos, (cx, cy, w, h) in SHELF_SLOTS.items():
        out.append((f"Window.IsVisible(videos) + String.IsEqual(Container.Viewmode,Shelf) + Integer.IsEqual(Container.Position,{pos})", cx - CX, cy - CY, w / W * 100, h / H * 100))
    return out


def open_close_anims():
    a = []
    for cond, dx, dy, zx, zy in slots():
        a.append(f"""			<animation type="WindowOpen" condition="{cond} + !{RM}">
				<effect type="slide" start="{dx:.0f},{dy:.0f}" end="0,0" time="{T_MOVE}" tween="cubic" easing="out"/>
				<effect type="zoom" start="{zx:.1f},{zy:.1f}" end="100,100" center="{CX},{CY}" time="{T_MOVE}" tween="cubic" easing="out"/>
			</animation>
			<animation type="WindowClose" condition="{cond} + !{RM}">
				<effect type="slide" start="0,0" end="{dx:.0f},{dy:.0f}" delay="{X_BACK_D}" time="{X_BACK_T}" tween="cubic" easing="in"/>
				<effect type="zoom" start="100,100" end="{zx:.1f},{zy:.1f}" center="{CX},{CY}" delay="{X_BACK_D}" time="{X_BACK_T}" tween="cubic" easing="in"/>
			</animation>""")
    any_slot = " | ".join(f"[{c}]" for c, *_ in slots())
    a.append(f"""			<!-- opened from anywhere else: the closed card rises in place -->
			<animation type="WindowOpen" condition="![{any_slot}] + !{RM}">
				<effect type="zoom" start="82" end="100" center="{CX},{CY}" time="{T_MOVE}" tween="cubic" easing="out"/>
				<effect type="fade" start="0" end="100" time="120"/>
			</animation>
			<animation type="WindowClose" condition="![{any_slot}] + !{RM}">
				<effect type="zoom" start="100" end="86" center="{CX},{CY}" delay="{X_BACK_D}" time="{X_BACK_T}" tween="cubic" easing="in"/>
				<effect type="fade" start="100" end="0" delay="{X_BACK_D}" time="{X_BACK_T}"/>
			</animation>
			<animation type="WindowOpen" condition="{RM}">
				<effect type="fade" start="0" end="100" time="150"/>
			</animation>
			<animation type="WindowClose" condition="{RM}">
				<effect type="fade" start="100" end="0" time="150"/>
			</animation>""")
    return "\n".join(a)


def panel_paper(x, shape, edge, shade):
    return f"""
				<control type="image">
					<left>{x}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture border="8" colordiffuse="cream">fold/{shape}</texture>
				</control>
				<control type="image">
					<left>{x}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture diffuse="fold/{shape}">fold/tooth_cream.png</texture>
				</control>"""


def panel_top(x, edge, shade):
    return f"""
				<control type="image">
					<left>{x}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture>fold/{shade}</texture>
				</control>
				<control type="image">
					<left>{x}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture border="4" colordiffuse="$VAR[FoldAccentEdge]">fold/{edge}</texture>
				</control>"""


def title_clip(x_clip, x_text):
    """Title split across the hinge: a grouplist clips it to one panel; the text keeps one position."""
    tiers = []
    # tier 1: one line at 158 (FoldOpen .title: top 46, line-height 1 -> baseline 131 below the top)
    tiers.append(("disp_158", f"!Integer.IsGreater(Container(9310).NumPages,1)", 46 + 131 - 147, 190, "label"))
    tiers.append(("disp_96", f"Integer.IsGreater(Container(9310).NumPages,1) + !Integer.IsGreater(Container(9311).NumPages,2)", 34, 210, "textbox"))
    tiers.append(("disp_64", f"Integer.IsGreater(Container(9311).NumPages,2)", 30, 214, "textbox"))
    out = []
    for font, vis, top, h, kind in tiers:
        out.append(f"""
					<control type="grouplist">
						<left>{x_clip}</left>
						<top>{TOP + top}</top>
						<width>{W}</width>
						<height>{h}</height>
						<orientation>horizontal</orientation>
						<usecontrolcoords>true</usecontrolcoords>
						<visible>{vis}</visible>
						<control type="{kind}">
							<left>{x_text - x_clip}</left>
							<width>1016</width>
							<height>{h}</height>
							<font>{font}</font>
							<textcolor>ink</textcolor>{'''
							<aligny>top</aligny>''' if kind == 'label' else ''}
							<label>$VAR[Spread_Title]</label>
						</control>
					</control>""")
    return "".join(out)


def fact_row(i, y):
    return f"""
					<control type="group">
						<width>452</width>
						<height>35</height>
						<visible>$EXP[Spread_F{i}Show]</visible>
						<control type="image">
							<left>0</left>
							<top>22</top>
							<width>452</width>
							<height>2</height>
							<aspectratio align="left">center</aspectratio>
							<texture colordiffuse="rule">fold/dots.png</texture>
						</control>
						<control type="grouplist">
							<left>0</left>
							<top>0</top>
							<width>452</width>
							<height>35</height>
							<orientation>horizontal</orientation>
							<itemgap>0</itemgap>
							<control type="button">
								<width>auto</width>
								<height>35</height>
								<font>caps_20</font>
								<textcolor>cap2</textcolor>
								<disabledcolor>cap2</disabledcolor>
								<textoffsetx>0</textoffsetx>
								<texturenofocus colordiffuse="cream">common/white.png</texturenofocus>
								<texturefocus colordiffuse="cream">common/white.png</texturefocus>
								<label>$VAR[Spread_F{i}L]  </label>
								<enable>false</enable>
							</control>
						</control>
						<control type="grouplist">
							<left>0</left>
							<top>0</top>
							<width>452</width>
							<height>35</height>
							<orientation>horizontal</orientation>
							<align>right</align>
							<itemgap>0</itemgap>
							<control type="button">
								<width max="380">auto</width>
								<height>35</height>
								<font>caps_20_b</font>
								<textcolor>$VAR[Spread_F{i}C]</textcolor>
								<disabledcolor>$VAR[Spread_F{i}C]</disabledcolor>
								<textoffsetx>10</textoffsetx>
								<texturenofocus colordiffuse="cream">common/white.png</texturenofocus>
								<texturefocus colordiffuse="cream">common/white.png</texturefocus>
								<label>$VAR[Spread_F{i}V]</label>
								<enable>false</enable>
							</control>
						</control>
					</control>"""


def word(bid, label, width, visible, onclick=None, primary=False):
    oc = f"\n\t\t\t\t\t\t\t<onclick>{onclick}</onclick>" if onclick else ""
    return f"""
						<control type="button" id="{bid}">
							<width>{width}</width>
							<height>66</height>
							<label>{label}</label>
							<font>word_36</font>
							<textcolor>ink</textcolor>
							<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
							<disabledcolor>disabled</disabledcolor>
							<align>center</align>
							<aligny>center</aligny>
							<textoffsetx>0</textoffsetx>
							<texturefocus border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texturefocus>
							<texturenofocus />
							<visible>{visible}</visible>{oc}
							<onup>noop</onup>
							<ondown>noop</ondown>
						</control>"""


def dot(did, visible):
    return f"""
						<control type="label" id="{did}">
							<width>16</width>
							<height>66</height>
							<align>center</align>
							<font>word_36</font>
							<textcolor>$VAR[FoldAccentInk]</textcolor>
							<label>·</label>
							<visible>{visible}</visible>
						</control>"""


def build():
    # word_36 widths measured with PIL (FoldWord-ExtraBold 36) + 2 x 12 chip padding + 1 px per glyph slack
    words_w = {"resume": 179, "play": 118, "open": 125, "trailer": 173, "more": 132}
    x = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_spread.py - edit the generator, not this file. -->
<!--{__doc__}-->
<includes>
	<!-- ============================================================== expressions -->
	<expression name="Spread_IsFolder">String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season) | String.IsEqual(ListItem.DBType,set)</expression>
	<expression name="Spread_ShowResume">Control.IsEnabled(9) + !$EXP[Spread_IsFolder]</expression>
	<expression name="Spread_ShowPlay">!Control.IsEnabled(9) + !$EXP[Spread_IsFolder]</expression>
	<expression name="Spread_F1Show">String.IsEqual(ListItem.DBType,episode) | String.IsEqual(ListItem.DBType,set) | !String.IsEmpty(ListItem.Genre)</expression>
	<expression name="Spread_F2Show">[String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Premiered)] | String.IsEqual(ListItem.DBType,set) | [!String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Studio)]</expression>
	<expression name="Spread_F3Show">[String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Director)] | [String.IsEqual(ListItem.DBType,tvshow) + !String.IsEmpty(ListItem.Status)] | [!$EXP[Spread_IsFolder] + !String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.MPAA)]</expression>
	<expression name="Spread_F4Show">!String.IsEqual(ListItem.DBType,set)</expression>
	<expression name="Spread_F5Show">!$EXP[Spread_IsFolder] + !String.IsEmpty(ListItem.Duration)</expression>
	<expression name="Spread_ShowTrailer">!Skin.HasSetting(fold.hidetrailer) + !String.IsEmpty(ListItem.Trailer)</expression>

	<!-- ============================================================== variables -->
	<variable name="FoldAccentEdge">
		<value condition="$EXP[SectionSeries]">ff1d3a8c</value>
		<value condition="$EXP[SectionMusic]">ffc98a17</value>
		<value condition="$EXP[SectionSearch]">ff17735a</value>
		<value condition="$EXP[SectionSettings]">ff2c2c2e</value>
		<value>verm_edge</value>
	</variable>
	<variable name="Spread_Title">
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Spread_Poster">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(season.poster))">$INFO[ListItem.Art(season.poster)]</value>
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Spread_CoverFootR">
		<value condition="String.IsEqual(ListItem.DBType,episode)">S$INFO[ListItem.Season]·E$INFO[ListItem.Episode]</value>
		<value condition="$EXP[Spread_IsFolder]">$INFO[ListItem.Property(TotalEpisodes),, EP]</value>
		<value>$INFO[ListItem.Duration(mins),,′]</value>
	</variable>
	<variable name="Spread_Caption">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
		<value>$INFO[ListItem.Studio]</value>
	</variable>
	<variable name="Spread_Meta">
		<value condition="String.IsEqual(ListItem.DBType,episode)">Season $INFO[ListItem.Season][COLOR cobalt] · [/COLOR]Episode $INFO[ListItem.Episode]$INFO[ListItem.Duration(mins),[COLOR cobalt] · [/COLOR], min]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow) + Integer.IsEqual(ListItem.Property(TotalSeasons),1)">$INFO[ListItem.Year][COLOR cobalt] · [/COLOR]1 season$VAR[Fold_N_TotalEpisodes_episodes3]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$VAR[Fold_N_TotalSeasons_seasons3]$VAR[Fold_N_TotalEpisodes_episodes3]</value>
		<value condition="String.IsEqual(ListItem.DBType,season)">$INFO[ListItem.TVShowTitle]$VAR[Fold_N_TotalEpisodes_episodes3]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Collection$VAR[Fold_N_Total_films5]</value>
		<value>$INFO[ListItem.Director,,[COLOR verm] · [/COLOR]]$INFO[ListItem.Year]$INFO[ListItem.Duration(mins),[COLOR verm] · [/COLOR], min]</value>
	</variable>
	<variable name="Spread_Tag">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
		<value condition="$EXP[Spread_IsFolder] + Integer.IsGreater(ListItem.Property(TotalEpisodes),0)">$INFO[ListItem.Property(WatchedEpisodes)] of $INFO[ListItem.Property(TotalEpisodes)]$VAR[Fold_N_EpWord] watched</value>
		<value condition="ListItem.IsResumable">Stopped at $INFO[ListItem.PercentPlayed]%$INFO[ListItem.Tagline,  ·  ,]</value>
		<value>$INFO[ListItem.Tagline]</value>
	</variable>
	<variable name="Spread_CastHead">
		<value condition="String.IsEqual(ListItem.DBType,set)">Films</value>
		<value>Cast</value>
	</variable>
	<variable name="Spread_MPAA">
		<value condition="String.IsEqual(ListItem.MPAA,Rated R)">R</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated PG-13)">PG-13</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated PG)">PG</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated G)">G</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated NC-17)">NC-17</value>
		<value condition="String.IsEqual(ListItem.MPAA,Rated NR) | String.IsEqual(ListItem.MPAA,Rated)"></value>
		<value>$INFO[ListItem.MPAA]</value>
	</variable>
	<variable name="Spread_Status">
		<value condition="ListItem.IsResumable">In progress</value>
		<value condition="Integer.IsEqual(ListItem.PlayCount,1)">Watched once</value>
		<value condition="Integer.IsGreater(ListItem.PlayCount,1)">Watched $INFO[ListItem.PlayCount] times</value>
		<value>Unwatched</value>
	</variable>
	<!-- facts (label / value / colour) by type -->
	<variable name="Spread_F1L">
		<value condition="String.IsEqual(ListItem.DBType,episode)">Show</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Films</value>
		<value>Genre</value>
	</variable>
	<variable name="Spread_F1V">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Total)]</value>
		<value>$INFO[ListItem.Genre]</value>
	</variable>
	<variable name="Spread_F2L">
		<value condition="String.IsEqual(ListItem.DBType,episode)">Aired</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">Network</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Watched</value>
		<value>Studio</value>
	</variable>
	<variable name="Spread_F2V">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$VAR[Date_PR]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Watched)]$INFO[ListItem.Property(Total), of ,]</value>
		<value>$INFO[ListItem.Studio]</value>
	</variable>
	<variable name="Spread_F3L">
		<value condition="String.IsEqual(ListItem.DBType,episode)">Director</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">Status</value>
		<value>Rated</value>
	</variable>
	<variable name="Spread_F3V">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Director]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Status]</value>
		<value condition="$EXP[Spread_IsFolder]"></value>
		<value>$VAR[Spread_MPAA]</value>
	</variable>
	<variable name="Spread_F4L">
		<value condition="$EXP[Spread_IsFolder]">Episodes</value>
		<value>Added</value>
	</variable>
	<variable name="Spread_F4V">
		<value condition="String.IsEqual(ListItem.DBType,set)"></value>
		<value condition="$EXP[Spread_IsFolder]">$INFO[ListItem.Property(WatchedEpisodes)]$INFO[ListItem.Property(TotalEpisodes), of , watched]</value>
		<value condition="!String.IsEmpty(ListItem.DateAdded)">$VAR[Date_DA]  ·  $VAR[Spread_Status]</value>
		<value>$VAR[Spread_Status]</value>
	</variable>
	<variable name="Spread_F5L">
		<value condition="ListItem.IsResumable">Ends if resumed</value>
		<value>Ends at</value>
	</variable>
	<variable name="Spread_F5V">
		<value condition="$EXP[Spread_IsFolder]"></value>
		<value condition="ListItem.IsResumable">$INFO[ListItem.EndTime(Resume)]</value>
		<value>$INFO[ListItem.EndTime]</value>
	</variable>
	<variable name="Spread_F1C"><value>ink</value></variable>
	<variable name="Spread_F2C"><value>ink</value></variable>
	<variable name="Spread_F3C"><value>ink</value></variable>
	<variable name="Spread_F4C"><value>ink</value></variable>
	<variable name="Spread_F5C"><value>$VAR[FoldAccentInk]</value></variable>
	<variable name="Spread_Hint">
		<value condition="Control.HasFocus(50)">Opens the person</value>
		<value condition="Control.HasFocus(9)">Resume</value>
		<value condition="Control.HasFocus(9013)">Play from the start</value>
		<value condition="Control.HasFocus(9012)">Open</value>
		<value condition="Control.HasFocus(11)">Play the trailer</value>
		<value condition="Control.HasFocus(9010)">More options</value>
		<value>Play</value>
	</variable>
	<variable name="Spread_Words">
		<value condition="$EXP[Spread_IsFolder] + $EXP[Spread_ShowTrailer]">Open · Trailer · More · Cast</value>
		<value condition="$EXP[Spread_IsFolder]">Open · More · Cast</value>
		<value condition="$EXP[Spread_ShowResume] + $EXP[Spread_ShowTrailer]">Resume · Trailer · More · Cast</value>
		<value condition="$EXP[Spread_ShowResume]">Resume · More · Cast</value>
		<value condition="$EXP[Spread_ShowTrailer]">Play · Trailer · More · Cast</value>
		<value>Play · More · Cast</value>
	</variable>

	<!-- ============================================================== the spread -->
	<include name="Spread_Window">
		<!-- the table covers Home while the card is open -->
		<control type="group">
			<animation type="WindowOpen">
				<effect type="fade" start="0" end="100" time="150"/>
			</animation>
			<animation type="WindowClose">
				<effect type="fade" start="100" end="0" delay="{X_BACK_D}" time="{X_BACK_T}"/>
			</animation>
			<include>Fold_Background</include>
		</control>
		<control type="group">
			<animation type="WindowOpen"><effect type="fade" start="0" end="100" time="150"/></animation>
			<animation type="WindowClose"><effect type="fade" start="100" end="0" delay="{X_BACK_D}" time="{X_BACK_T}"/></animation>
			<include content="Fold_Tabs"><param name="dim" value="true"/></include>
			<include>Fold_Clock</include>
		</control>

		<control type="group">
			<camera x="960" y="540"/>
{open_close_anims()}
			<!-- spread shadow on the table (FoldOpen .shadow), arrives when the flap lands -->
			<control type="image">
				<left>{P1 - 96}</left>
				<top>{TOP - 96}</top>
				<width>{3 * W + 192}</width>
				<height>{H + 192}</height>
				<texture border="104">fold/shadow_spread.png</texture>
				<animation type="WindowOpen" condition="!{RM}"><effect type="fade" start="0" end="100" delay="{I_DELAY}" time="160"/></animation>
				<animation type="WindowClose" condition="!{RM}"><effect type="fade" start="100" end="0" time="120"/></animation>
			</control>
			<!-- the rising flap's shadow on the table: grows and softens with the lift, gone when it lands -->
			<control type="image">
				<left>{P3 - 110}</left>
				<top>{TOP - 60}</top>
				<width>{W + 300}</width>
				<height>{H + 160}</height>
				<texture border="150">fold/shadow_flap.png</texture>
				<animation type="WindowOpen" condition="!{RM}">
					<effect type="fade" start="0" end="100" delay="{F_DELAY}" time="80"/>
					<effect type="fade" start="100" end="0" delay="{F_DELAY + 80}" time="{F_TIME - 60}"/>
				</animation>
				<animation type="WindowOpen" condition="{RM}"><effect type="fade" start="0" end="0" time="0"/></animation>
				<animation type="WindowClose" condition="!{RM}">
					<effect type="fade" start="0" end="100" time="80"/>
					<effect type="fade" start="100" end="0" delay="80" time="80"/>
				</animation>
				<visible>!{RM}</visible>
			</control>

			<!-- ===== centre panel p2 (rests flat: the cover is hinged on its left edge) -->
			<control type="group">{panel_paper(P2, 'white.png', 'edge_c.png', 'shade_p2.png').replace('fold/white.png', 'common/white.png').replace('border="8" ', '')}{title_clip(P2, P2 + 52)}
				<!-- title probes: tier 1 = one line at 158 in 1016 px, tier 2 = up to two lines at 96 -->
				<control type="textbox" id="9310">
					<left>-3000</left>
					<top>0</top>
					<width>1016</width>
					<height>240</height>
					<font>disp_158</font>
					<textcolor>clear</textcolor>
					<label>$VAR[Spread_Title]</label>
				</control>
				<control type="textbox" id="9311">
					<left>-3000</left>
					<top>300</top>
					<width>1016</width>
					<height>140</height>
					<font>disp_96</font>
					<textcolor>clear</textcolor>
					<label>$VAR[Spread_Title]</label>
				</control>
				<control type="label">
					<left>{P2 + 56}</left>
					<top>{TOP + 246}</top>
					<width>480</width>
					<height>34</height>
					<font>meta_22</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Spread_Meta]</label>
				</control>
				<control type="label">
					<left>{P2 + 56}</left>
					<top>{TOP + 290}</top>
					<width>470</width>
					<height>44</height>
					<font>light_32</font>
					<textcolor>ink2</textcolor>
					<label>$VAR[Spread_Tag]</label>
				</control>
				<control type="textbox" id="9370">
					<left>{P2 + 56}</left>
					<top>{TOP + 366}</top>
					<width>456</width>
					<height>{38 * 6}</height>
					<font>body_26_spread</font>
					<textcolor>body</textcolor>
					<label>$INFO[ListItem.Plot]</label>
				</control>
				<include content="Fold_PlotEllipsis"><param name="id" value="9370"/><param name="right" value="{P2 + 56 + 456}"/><param name="top" value="{TOP + 366 + 38 * 5}"/><param name="pitch" value="38"/><param name="font" value="body_26_spread"/><param name="bg" value="cream"/></include>
				<control type="image">
					<left>{P2}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture>fold/shade_p2.png</texture>
				</control>
				<control type="image">
					<left>{P2}</left>
					<top>{TOP}</top>
					<width>2</width>
					<height>{H}</height>
					<texture>fold/ridge.png</texture>
				</control>
				<control type="image">
					<left>{P2}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture border="4" colordiffuse="$VAR[FoldAccentEdge]">fold/edge_c.png</texture>
				</control>
				<!-- the lifted cover's shadow printed on p2 (phase 1) -->
				<control type="image">
					<left>{P2}</left>
					<top>{TOP}</top>
					<width>{W}</width>
					<height>{H}</height>
					<texture>fold/cast_shadow.png</texture>
					<visible>!{RM}</visible>
					<animation type="WindowOpen" condition="!{RM}">
						<effect type="fade" start="100" end="0" delay="{C_DELAY}" time="{C_TIME + 120}" tween="sine" easing="in"/>
					</animation>
					<animation type="WindowClose" condition="!{RM}">
						<effect type="fade" start="0" end="100" delay="{X_COVER_D}" time="{X_COVER_T}"/>
					</animation>
				</control>
			</control>

			<!-- ===== right flap p3: rests at +4 deg (FoldOpen rotateY(-4deg)); unfolds +90 -> 0 -->
			<control type="group">
				<animation effect="rotatey" start="4" end="4" center="{HINGE_R}" time="0" condition="true">Conditional</animation>
				<control type="group">
					<animation type="WindowOpen" condition="!{RM}">
						<effect type="rotatey" start="90" end="0" center="{HINGE_R}" delay="{F_DELAY}" time="{F_TIME}" tween="cubic" easing="out"/>
						<effect type="fade" start="0" end="100" delay="{F_DELAY}" time="40"/>
					</animation>
					<animation type="WindowClose" condition="!{RM}">
						<effect type="rotatey" start="0" end="90" center="{HINGE_R}" time="{X_FLAP}" tween="cubic" easing="in"/>
						<effect type="fade" start="100" end="0" delay="{X_FLAP - 20}" time="20"/>
					</animation>{panel_paper(P3, 'rr5_r.png', 'edge_r.png', 'shade_p3.png')}{title_clip(P3, P2 + 52)}
					<control type="label">
						<left>{P3 + 56}</left>
						<top>{TOP + 246}</top>
						<width>300</width>
						<height>32</height>
						<font>caps_20_b</font>
						<textcolor>$VAR[FoldAccentInk]</textcolor>
						<label>$VAR[Spread_CastHead]</label>
						<visible>Integer.IsGreater(Container(50).NumItems,0)</visible>
					</control>
					<control type="list" id="50">
						<left>{P3 + 44}</left>
						<top>{TOP + 284}</top>
						<width>380</width>
						<height>{37 * 6}</height>
						<orientation>vertical</orientation>
						<scrolltime tween="cubic" easing="out">160</scrolltime>
						<onleft>9000</onleft>
						<onright>noop</onright>
						<onup>noop</onup>
						<ondown>noop</ondown>
						<itemlayout width="380" height="37">
							<control type="label">
								<left>12</left>
								<top>0</top>
								<width>356</width>
								<height>37</height>
								<font>sans_28_semi</font>
								<textcolor>ink</textcolor>
								<selectedcolor>ink</selectedcolor>
								<label>$INFO[ListItem.Label]</label>
								<visible>Integer.IsLessOrEqual(ListItem.CurrentItem,3)</visible>
							</control>
							<control type="label">
								<left>12</left>
								<top>0</top>
								<width>356</width>
								<height>37</height>
								<font>body_28</font>
								<textcolor>ink2</textcolor>
								<selectedcolor>ink2</selectedcolor>
								<label>$INFO[ListItem.Label]</label>
								<visible>Integer.IsGreater(ListItem.CurrentItem,3)</visible>
							</control>
						</itemlayout>
						<focusedlayout width="380" height="37">
							<control type="image">
								<left>0</left>
								<top>0</top>
								<width>380</width>
								<height>37</height>
								<texture border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texture>
								<visible>Control.HasFocus(50)</visible>
							</control>
							<control type="label">
								<left>12</left>
								<top>0</top>
								<width>356</width>
								<height>37</height>
								<font>sans_28_semi</font>
								<textcolor>ink</textcolor>
								<selectedcolor>ink</selectedcolor>
								<label>$INFO[ListItem.Label]</label>
								<visible>!Control.HasFocus(50) + Integer.IsLessOrEqual(ListItem.CurrentItem,3)</visible>
							</control>
							<control type="label">
								<left>12</left>
								<top>0</top>
								<width>356</width>
								<height>37</height>
								<font>body_28</font>
								<textcolor>ink2</textcolor>
								<selectedcolor>ink2</selectedcolor>
								<label>$INFO[ListItem.Label]</label>
								<visible>!Control.HasFocus(50) + Integer.IsGreater(ListItem.CurrentItem,3)</visible>
							</control>
							<control type="label">
								<left>12</left>
								<top>0</top>
								<width>356</width>
								<height>37</height>
								<font>sans_28_semi</font>
								<textcolor>on_card</textcolor>
								<selectedcolor>on_card</selectedcolor>
								<label>$INFO[ListItem.Label]</label>
								<visible>Control.HasFocus(50)</visible>
							</control>
						</focusedlayout>
					</control>
					<!-- rating stamp (FoldOpen .stamp): ring + number, rotated 8 deg -->
					<control type="group">
						<left>{P3 + W - 48 - 136}</left>
						<top>{TOP + 262}</top>
						<visible>!String.IsEmpty(ListItem.Rating)</visible>
						<animation effect="rotate" start="8" end="8" center="{P3 + W - 48 - 68},{TOP + 262 + 68}" time="0" condition="true">Conditional</animation>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>136</width>
							<height>136</height>
							<texture colordiffuse="$VAR[FoldAccentInk]">fold/stamp.png</texture>
							<animation effect="fade" start="92" end="92" time="0" condition="true">Conditional</animation>
						</control>
						<control type="label">
							<left>0</left>
							<top>26</top>
							<width>136</width>
							<height>60</height>
							<align>center</align>
							<font>disp_50</font>
							<textcolor>$VAR[FoldAccentInk]</textcolor>
							<label>$INFO[ListItem.Rating]</label>
						</control>
						<control type="label">
							<left>0</left>
							<top>80</top>
							<width>136</width>
							<height>30</height>
							<align>center</align>
							<font>caps_20</font>
							<textcolor>$VAR[FoldAccentInk]</textcolor>
							<label>Rating</label>
						</control>
					</control>
					<control type="label">
						<left>{P3 + 56}</left>
						<top>{TOP + 518}</top>
						<width>300</width>
						<height>32</height>
						<font>caps_20_b</font>
						<textcolor>$VAR[FoldAccentInk]</textcolor>
						<label>Facts</label>
					</control>
					<control type="grouplist">
						<left>{P3 + 56}</left>
						<top>{TOP + 556}</top>
						<width>452</width>
						<height>{35 * 5}</height>
						<orientation>vertical</orientation>
						<itemgap>0</itemgap>{''.join(fact_row(i, 0) for i in range(1, 6))}
					</control>{panel_top(P3, 'edge_r.png', 'shade_p3.png')}
					<!-- the flap turning away from the light -->
					<control type="image">
						<left>{P3}</left>
						<top>{TOP}</top>
						<width>{W}</width>
						<height>{H}</height>
						<texture>fold/flap_shade.png</texture>
						<visible>!{RM}</visible>
						<animation type="WindowOpen" condition="!{RM}">
							<effect type="fade" start="100" end="0" delay="{F_DELAY}" time="{F_TIME}" tween="sine" easing="in"/>
						</animation>
						<animation type="WindowClose" condition="!{RM}">
							<effect type="fade" start="0" end="100" time="{X_FLAP}"/>
						</animation>
					</control>
				</control>
			</control>

			<!-- ===== left panel p1 = the inside of the cover: rests at -5 deg (FoldOpen rotateY(5deg)) -->
			<control type="group">
				<animation effect="rotatey" start="-5" end="-5" center="{HINGE_L}" time="0" condition="true">Conditional</animation>
				<control type="group">
					<animation type="WindowOpen" condition="!{RM}">
						<effect type="rotatey" start="-90" end="0" center="{HINGE_L}" delay="{I_DELAY}" time="{I_TIME}" tween="cubic" easing="out"/>
						<effect type="fade" start="0" end="100" delay="{I_DELAY}" time="1"/>
					</animation>
					<animation type="WindowClose" condition="!{RM}">
						<effect type="rotatey" start="0" end="-90" center="{HINGE_L}" time="{X_INS}" tween="cubic" easing="in"/>
						<effect type="fade" start="100" end="0" delay="{X_INS}" time="1"/>
					</animation>{panel_paper(P1, 'rr5_l.png', 'edge_l.png', 'shade_p1.png')}
					<control type="group">
						<left>{P1 + 76}</left>
						<top>{TOP + 64}</top>
						<width>408</width>
						<height>582</height>
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
							<width>408</width>
							<height>582</height>
							<texture colordiffuse="cream_deep">common/white.png</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>408</width>
							<height>582</height>
							<aspectratio>scale</aspectratio>
							<texture background="true">$VAR[Spread_Poster]</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>408</width>
							<height>582</height>
							<texture>fold/plate_sheen.png</texture>
						</control>
					</control>
					<control type="label">
						<left>{P1 + 76}</left>
						<top>{TOP + 672}</top>
						<width>300</width>
						<height>32</height>
						<font>caps_20</font>
						<textcolor>cap2</textcolor>
						<label>$VAR[Spread_Caption]</label>
					</control>
					<control type="label">
						<left>{P1 + 76}</left>
						<top>{TOP + 672}</top>
						<width>408</width>
						<height>32</height>
						<align>right</align>
						<font>caps_20</font>
						<textcolor>cap2</textcolor>
						<label>$INFO[ListItem.Year]</label>
					</control>{panel_top(P1, 'edge_l.png', 'shade_p1.png')}
					<control type="image">
						<left>{P1}</left>
						<top>{TOP}</top>
						<width>{W}</width>
						<height>{H}</height>
						<texture>fold/inside_shade.png</texture>
						<visible>!{RM}</visible>
						<animation type="WindowOpen" condition="!{RM}">
							<effect type="fade" start="100" end="0" delay="{I_DELAY}" time="{I_TIME}"/>
						</animation>
						<animation type="WindowClose" condition="!{RM}">
							<effect type="fade" start="0" end="100" time="{X_INS}"/>
						</animation>
					</control>
				</control>
			</control>

			<!-- ===== the cover (front face): turns 0 -> +90 on the left hinge, then hides -->
			<control type="group">
				<animation type="WindowOpen" condition="!{RM}">
					<effect type="fade" start="100" end="100" time="{C_DELAY}"/>
					<effect type="rotatey" start="0" end="90" center="{HINGE_L}" delay="{C_DELAY}" time="{C_TIME}" tween="cubic" easing="in"/>
					<effect type="fade" start="100" end="0" delay="{C_DELAY + C_TIME}" time="1"/>
				</animation>
				<animation type="WindowClose" condition="!{RM}">
					<effect type="fade" start="0" end="100" delay="{X_COVER_D}" time="1"/>
					<effect type="rotatey" start="90" end="0" center="{HINGE_L}" delay="{X_COVER_D}" time="{X_COVER_T}" tween="cubic" easing="out"/>
				</animation>
				<visible>!{RM}</visible>
				<include content="Spread_Cover"/>
			</control>

			<!-- ===== action words (FoldOpen .actions), on p2 -->
			<control type="grouplist" id="9000">
				<left>{P2 + 36}</left>
				<top>{TOP + H - 34 - 66 - 4}</top>
				<width>{W - 40}</width>
				<height>74</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<onright>50</onright>
				<onleft>noop</onleft>
				<onup>noop</onup>
				<ondown>noop</ondown>
				<animation type="WindowOpen" condition="!{RM}"><effect type="fade" start="0" end="100" delay="{C_DELAY + C_TIME}" time="80"/></animation>
				<animation type="WindowClose" condition="!{RM}"><effect type="fade" start="100" end="0" time="60"/></animation>{word(9, 'Resume', words_w['resume'], '$EXP[Spread_ShowResume]')}{word(8, 'Play', words_w['play'], '$EXP[Spread_ShowPlay]')}{word(9012, 'Open', words_w['open'], '$EXP[Spread_IsFolder]', 'SendClick(8)')}{dot(9022, '$EXP[Spread_ShowTrailer]')}{word(11, 'Trailer', words_w['trailer'], '$EXP[Spread_ShowTrailer]')}{dot(9023, 'true')}{word(9010, 'More', words_w['more'], 'true', 'SetFocus(9100)')}
			</control>

			<!-- ===== the More note: Kodi's secondary actions, unfolding up from the action row -->
			<control type="group">
				<left>{P2 + 40}</left>
				<top>{TOP + 300}</top>
				<visible allowhiddenfocus="true">ControlGroup(9100).HasFocus()</visible>
				<animation type="Visible" condition="!{RM}">
					<effect type="rotatex" start="80" end="0" center="{TOP + 300 + 456}" time="220" tween="cubic" easing="out"/>
					<effect type="fade" start="0" end="100" time="80"/>
				</animation>
				<animation type="Hidden" condition="!{RM}">
					<effect type="rotatex" start="0" end="80" center="{TOP + 300 + 456}" time="160" tween="cubic" easing="in"/>
					<effect type="fade" start="100" end="0" delay="120" time="40"/>
				</animation>
				<control type="image">
					<left>-96</left>
					<top>-96</top>
					<width>{480 + 192}</width>
					<height>{456 + 192}</height>
					<texture border="104">fold/shadow_spread.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>480</width>
					<height>456</height>
					<texture border="6" colordiffuse="cream">fold/rr4.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>480</width>
					<height>456</height>
					<texture diffuse="fold/rr4.png">fold/tooth_cream.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>480</width>
					<height>456</height>
					<texture border="4" colordiffuse="$VAR[FoldAccentEdge]">fold/edge_all.png</texture>
				</control>
				<control type="label">
					<left>28</left>
					<top>18</top>
					<width>420</width>
					<height>32</height>
					<font>caps_20_b</font>
					<textcolor>$VAR[FoldAccentInk]</textcolor>
					<label>More</label>
				</control>
				<control type="grouplist" id="9100">
					<left>16</left>
					<top>58</top>
					<width>448</width>
					<height>384</height>
					<orientation>vertical</orientation>
					<itemgap>0</itemgap>
					<onleft>9010</onleft>
					<onright>9010</onright>
					<onback>9010</onback>{''.join(f'''
					<control type="button" id="{bid}">
						<width>448</width>
						<height>48</height>
						<label>{lab}</label>
						<font>caps_22_b</font>
						<textcolor>ink</textcolor>
						<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
						<textoffsetx>14</textoffsetx>
						<texturefocus border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texturefocus>
						<texturenofocus />
						<visible>{vis}</visible>{f"""
						<onclick>{oc}</onclick>""" if oc else ''}
					</control>''' for bid, lab, vis, oc in (
        (9013, 'Play from the start', '$EXP[Spread_ShowResume]', 'SendClick(8)'),
        (9101, 'Read the full plot', '!String.IsEmpty(ListItem.Plot)', 'SetFocus(61)'),
        (443, 'Go to the collection', '!String.IsEmpty(ListItem.SetID)', None),
        (13, 'More by the director', '!String.IsEmpty(ListItem.Director)', None),
        (7, 'My rating$INFO[ListItem.UserRating,: ,]', 'Control.IsEnabled(7)', None),
        (14, 'Versions', 'String.IsEqual(ListItem.DBType,movie)', None),
        (15, 'Extras', 'String.IsEqual(ListItem.DBType,movie)', None),
        (10, 'Choose art', 'Control.IsEnabled(10)', None),
        (12, 'Choose fanart', 'Control.IsEnabled(12)', None),
        (6, 'Refresh information', 'Control.IsEnabled(6)', None)))}
				</control>
			</control>

			<!-- key hints (FoldOpen .hint) -->
			<control type="grouplist">
				<left>{P1}</left>
				<top>{TOP + H + 40}</top>
				<width>1680</width>
				<height>32</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<animation type="WindowOpen"><effect type="fade" start="0" end="100" delay="{I_DELAY}" time="120"/></animation>
				<animation type="WindowClose"><effect type="fade" start="100" end="0" time="80"/></animation>
				<include content="Fold_KeyHint"><param name="id" value="9031"/><param name="key" value="OK"/><param name="label" value="$VAR[Spread_Hint]"/></include>
				<include content="Fold_KeyHint"><param name="id" value="9032"/><param name="key" value="← →"/><param name="label" value="$VAR[Spread_Words]"/></include>
				<include content="Fold_KeyHint"><param name="id" value="9033"/><param name="key" value="BACK"/><param name="label" value="Fold closed"/></include>
			</control>
		</control>

		<!-- ===== full plot: a large note over the spread -->
		<control type="group" id="9200">
			<visible allowhiddenfocus="true">ControlGroup(9200).HasFocus()</visible>
			<animation type="Visible" condition="!{RM}">
				<effect type="rotatex" start="70" end="0" center="540" time="220" tween="cubic" easing="out"/>
				<effect type="fade" start="0" end="100" time="100"/>
			</animation>
			<animation type="Hidden"><effect type="fade" start="100" end="0" time="120"/></animation>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>1080</height>
				<texture colordiffuse="veil">common/white.png</texture>
			</control>
			<control type="group">
				<left>360</left>
				<top>120</top>
				<camera x="600" y="420"/>
				<control type="image">
					<left>-96</left>
					<top>-96</top>
					<width>{1200 + 192}</width>
					<height>{840 + 192}</height>
					<texture border="104">fold/shadow_spread.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>1200</width>
					<height>840</height>
					<texture border="6" colordiffuse="cream">fold/rr4.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>1200</width>
					<height>840</height>
					<texture diffuse="fold/rr4.png">fold/tooth_cream.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>1200</width>
					<height>840</height>
					<texture>fold/note_crease.png</texture>
				</control>
				<control type="label">
					<left>64</left>
					<top>48</top>
					<width>1000</width>
					<height>32</height>
					<font>caps_20_b</font>
					<textcolor>$VAR[FoldAccentInk]</textcolor>
					<label>The story</label>
				</control>
				<control type="label">
					<left>64</left>
					<top>84</top>
					<width>1072</width>
					<height>80</height>
					<font>disp_64</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Spread_Title]</label>
				</control>
				<control type="textbox">
					<left>64</left>
					<top>190</top>
					<width>1040</width>
					<height>{37 * 15}</height>
					<font>body_26</font>
					<textcolor>body</textcolor>
					<pagecontrol>61</pagecontrol>
					<label>$INFO[ListItem.Plot]</label>
				</control>
				<control type="scrollbar" id="61">
					<left>1128</left>
					<top>190</top>
					<width>6</width>
					<height>{37 * 15}</height>
					<orientation>vertical</orientation>
					<showonepage>true</showonepage>
					<texturesliderbackground colordiffuse="track">common/white.png</texturesliderbackground>
					<texturesliderbar colordiffuse="$VAR[FoldAccent]">common/white.png</texturesliderbar>
					<texturesliderbarfocus colordiffuse="$VAR[FoldAccent]">common/white.png</texturesliderbarfocus>
					<onleft>9010</onleft>
					<onright>9010</onright>
					<onback>9010</onback>
				</control>
				<control type="grouplist">
					<left>64</left>
					<top>776</top>
					<width>1000</width>
					<height>32</height>
					<orientation>horizontal</orientation>
					<itemgap>0</itemgap>
					<include content="Fold_KeyHint"><param name="id" value="9034"/><param name="key" value="↑ ↓"/><param name="label" value="Scroll"/></include>
					<include content="Fold_KeyHint"><param name="id" value="9035"/><param name="key" value="BACK"/><param name="label" value="Fold it away"/></include>
				</control>
			</control>
		</control>
	</include>

	<!-- The closed card's front: vermilion stock, the poster as a tipped-in plate, mono foot (half.css .cover) -->
	<include name="Spread_Cover">
		<control type="image">
			<left>{P2 + W - 1}</left>
			<top>{TOP + 3}</top>
			<width>5</width>
			<height>{H - 6}</height>
			<texture>fold/foredge.png</texture>
		</control>
		<control type="image">
			<left>{P2}</left>
			<top>{TOP}</top>
			<width>{W}</width>
			<height>{H}</height>
			<texture border="8" colordiffuse="$VAR[FoldAccent]">fold/rr6_r.png</texture>
		</control>
		<control type="image">
			<left>{P2}</left>
			<top>{TOP}</top>
			<width>{W}</width>
			<height>{H}</height>
			<texture diffuse="fold/rr6_r.png">fold/tooth_card.png</texture>
		</control>
		<control type="image">
			<left>{P2}</left>
			<top>{TOP}</top>
			<width>{W}</width>
			<height>{H}</height>
			<texture>fold/card_sheen.png</texture>
		</control>
		<control type="image">
			<left>{P2 + 14}</left>
			<top>{TOP}</top>
			<width>3</width>
			<height>{H}</height>
			<texture>fold/score3.png</texture>
		</control>
		<control type="group">
			<left>{P2 + 42}</left>
			<top>{TOP + 38}</top>
			<width>484</width>
			<height>630</height>
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
				<width>484</width>
				<height>630</height>
				<texture colordiffuse="cream_deep">common/white.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>484</width>
				<height>630</height>
				<aspectratio>scale</aspectratio>
				<texture background="true">$VAR[Spread_Poster]</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>484</width>
				<height>630</height>
				<texture>fold/plate_sheen.png</texture>
			</control>
		</control>
		<control type="label">
			<left>{P2 + 42}</left>
			<top>{TOP + H - 30 - 44}</top>
			<width>200</width>
			<height>44</height>
			<font>num_34</font>
			<textcolor>on_card</textcolor>
			<label>$INFO[ListItem.Year]</label>
		</control>
		<control type="label">
			<left>{P2 + 242}</left>
			<top>{TOP + H - 30 - 44}</top>
			<width>284</width>
			<height>44</height>
			<align>right</align>
			<font>num_34</font>
			<textcolor>on_card</textcolor>
			<label>$VAR[Spread_CoverFootR]</label>
		</control>
		<!-- the cover catches the window light as it rises (half.css .cshade), in sync with the turn -->
		<control type="image">
			<left>{P2}</left>
			<top>{TOP}</top>
			<width>{W}</width>
			<height>{H}</height>
			<texture>fold/cover_shade.png</texture>
			<animation type="WindowOpen" condition="!{RM}">
				<effect type="fade" start="0" end="100" delay="{C_DELAY}" time="{C_TIME}" tween="sine" easing="in"/>
			</animation>
			<animation type="WindowClose" condition="!{RM}">
				<effect type="fade" start="100" end="0" delay="{X_COVER_D}" time="{X_COVER_T}"/>
			</animation>
		</control>
	</include>
</includes>
"""
    OUT.write_text(finish_xml(x), encoding="utf-8", newline="\n")
    print("Includes_VideoInfo.xml written")


if __name__ == "__main__":
    build()
