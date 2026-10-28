"""0.9.13 video views for Fold (docs/VIEWS_BRIEF_2026-10-27.md), imported by make_views.py.

  503 Table     the whole table covered with small closed cards, 8 across (a dense wall); the focused card lifts
                and tilts like the shelf, its title rides on the crumb line.
  505 Leaflet   the focused title opened as a tri-fold leaflet standing on the table (poster or still inside the
                left panel, title / meta / story in the middle, the fanart print and facts on the right), over a
                strip of small closed cards (or stills, in a season).
  506 Prints    landscape prints: section-colour cards with a wide plate (fanart, episode still, landscape; add-ons
                and plug-in items keep their own picture whole), title and facts on the card's foot. Every content.
All in Fold's language: Fold_CardBody stock, lift + tilt on focus (reduce motion: a time-0 Conditional on the
list's focus), panel crease shading from the spread, the section colour from $VAR[FoldAccent].
"""

RM = "Skin.HasSetting(fold.reducemotion)"

# ------------------------------------------------------------------------------ shared closed card
def closed_card(focused, lid, cw, ch, lw, lh, px, py, color, art, foot_l, foot_r, fonts=("num_20", "num_20"),
                plate_ratio=1.5, fallback="$INFO[ListItem.Label]", aspect="scale", parent_word="Up a level",
                shadow_tint="$VAR[Shelf_ShadowTint]", foot_color="on_card", marks=True, parent_color="$VAR[FoldAccentInk]"):
    """A Fold card in a list/panel slot: the shelf card (make_views.shelf_card) at any size. Resting cw x ch at
    (px, py) in the slot; lifted lw x lh, bottom-centre anchored, zoom + rotatex -9 on focus."""
    w, h = (lw, lh) if focused else (cw, ch)
    cx = px + cw // 2
    bottom = py + ch
    left, top = cx - w // 2, bottom - h
    k = w / 228.0
    pl, pt = round(18 * k), round(16 * k)
    pw = w - pl - round(14 * k)
    ph = round(pw * plate_ratio) if plate_ratio else h - pt - round(48 * k)
    sp = 72 if focused else 40
    tex = "shadow_lift" if focused else "shadow_card"
    lift = ""
    if focused:
        lift = f"""
					<animation type="Focus" condition="!{RM}">
						<effect type="zoom" start="{cw / lw * 100:.1f}" end="100" center="{cx},{bottom}" time="240" tween="back" easing="out"/>
						<effect type="rotatex" start="0" end="-9" center="{bottom}" time="240" tween="back" easing="out"/>
					</animation>
					<animation type="Conditional" condition="{RM} + Control.HasFocus({lid})">
						<effect type="rotatex" start="-9" end="-9" center="{bottom}" time="0"/>
					</animation>
					<animation type="Unfocus" condition="!{RM}">
						<effect type="rotatex" start="-9" end="0" center="{bottom}" time="180" tween="cubic" easing="out"/>
					</animation>"""
    shadow_anim = """
				<animation type="Focus" condition="!%s">
					<effect type="fade" start="30" end="100" time="240"/>
				</animation>
				<animation type="Unfocus" condition="!%s">
					<effect type="fade" start="100" end="45" time="180"/>
				</animation>""" % (RM, RM) if focused else ""
    light = f"""
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture>fold/card_light.png</texture>
						<visible>Control.HasFocus({lid})</visible>
					</control>""" if focused else ""
    return f"""
				<control type="image">
					<left>{left - sp}</left>
					<top>{top - sp}</top>
					<width>{w + 2 * sp}</width>
					<height>{h + 2 * sp}</height>
					<texture border="{sp + 8}" colordiffuse="{shadow_tint}">fold/{tex}.png</texture>{shadow_anim}
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
						<param name="color" value="{color}"/>
						<param name="plate_l" value="{pl}"/>
						<param name="plate_t" value="{pt}"/>
						<param name="plate_w" value="{pw}"/>
						<param name="plate_h" value="{ph}"/>
						<param name="art" value="{art}"/>
						<param name="aspect" value="{aspect}"/>
						<param name="foot_l" value="{foot_l}"/>
						<param name="foot_r" value="{foot_r}"/>
						<param name="foot_font" value="{fonts[1] if focused else fonts[0]}"/>
						<param name="foot_b" value="{round(12 * k)}"/>
						<param name="foot_color" value="{foot_color}"/>
						<param name="fallback" value="{fallback}"/>
					</include>
					<control type="image">
						<left>{pl + pw - 34}</left>
						<top>{pt + 6}</top>
						<width>28</width>
						<height>28</height>
						<texture>fold/punch.png</texture>
						<visible>{'$EXP[Shelf_Watched] + $EXP[ShowWatchedMarkers]' if marks else 'false'}</visible>
					</control>
					<control type="progress">
						<left>{pl}</left>
						<top>{pt + ph - 6}</top>
						<width>{pw}</width>
						<height>6</height>
						<texturebg colordiffuse="99000000">common/white.png</texturebg>
						<midtexture colordiffuse="on_card">common/white.png</midtexture>
						<info>ListItem.PercentPlayed</info>
						<visible>{'ListItem.IsResumable' if marks else 'false'}</visible>
					</control>{light}
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
						<left>16</left>
						<top>12</top>
						<width>{w - 32}</width>
						<height>72</height>
						<font>disp_50</font>
						<textcolor>{parent_color}</textcolor>
						<label>←</label>
					</control>
					<control type="label">
						<left>16</left>
						<top>{h - 52}</top>
						<width>{w - 32}</width>
						<height>36</height>
						<font>tab_22</font>
						<textcolor>ink</textcolor>
						<label>{parent_word}</label>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture border="4" colordiffuse="$VAR[FoldAccent]">fold/edge_all.png</texture>
						<visible>{'Control.HasFocus(%d)' % lid if focused else 'false'}</visible>
					</control>
				</control>"""


# ------------------------------------------------------------------------------ 503 Table
T_X, T_Y = 56, 150
T_SW, T_SH = 222, 288          # slot
T_CW, T_CH = 168, 252          # resting card
T_LW, T_LH = 186, 279          # lifted
T_PX, T_PY = 27, 18
# 0.9.16: also the index nodes (genres, years, people, studios, countries, tags): a vermilion card with the name in
# the plate (no art) or the actor's portrait; the views-per-section floor (docs/VIEWS_PER_SECTION_2026-10-28.md)
NODE_CONTENT = ("Container.Content(genres) | Container.Content(years) | Container.Content(actors) | "
                "Container.Content(directors) | Container.Content(studios) | Container.Content(countries) | "
                "Container.Content(tags)")
TABLE_CONTENT = ("Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
                 "Container.Content(seasons) | Container.Content(musicvideos) | " + NODE_CONTENT)


def table_view():
    def card(f):
        return closed_card(f, 503, T_CW, T_CH, T_LW, T_LH, T_PX, T_PY, "$VAR[Table_CardColor]", "$VAR[Table_Art]",
                           "$INFO[ListItem.Year]", "$VAR[Shelf_FootR]")
    return f"""
	<include name="VidView_503_Table">
		<control type="group">
			<visible>Control.IsVisible(503)</visible>
			<include content="Anim_StandUp"><param name="bottom" value="{T_Y + T_SH * 3}"/></include>
			<control type="panel" id="503">
				<left>{T_X}</left>
				<top>{T_Y}</top>
				<width>{T_SW * 8}</width>
				<height>{T_SH * 3 + 30}</height>
				<orientation>vertical</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">260</scrolltime>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onright>9000</onright>
				<onleft>ActivateWindow(1155)</onleft>
				<onback condition="$EXP[Lib_AtRoot]">9398</onback>
				<viewtype label="Table">wrap</viewtype>
				<visible>{TABLE_CONTENT}</visible>
				<itemlayout width="{T_SW}" height="{T_SH}">{card(False)}
				</itemlayout>
				<focusedlayout width="{T_SW}" height="{T_SH}">{card(True)}
				</focusedlayout>
			</control>
		</control>
	</include>"""


# ------------------------------------------------------------------------------ 505 Leaflet
L_TOP, L_H, L_W = 160, 540, 552
L_P1, L_P2, L_P3 = 132, 132 + 552, 132 + 2 * 552
LEAF_CONTENT = ("Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | "
                "Container.Content(seasons) | Container.Content(episodes) | Container.Content(musicvideos)")


def _panel(x, shape, edge, shade):
    return f"""
				<control type="image">
					<left>{x}</left>
					<top>{L_TOP}</top>
					<width>{L_W}</width>
					<height>{L_H}</height>
					<texture border="8" colordiffuse="cream">{shape}</texture>
				</control>
				<control type="image">
					<left>{x}</left>
					<top>{L_TOP}</top>
					<width>{L_W}</width>
					<height>{L_H}</height>
					<texture diffuse="{shape}">fold/tooth_cream.png</texture>
				</control>
				<control type="image">
					<left>{x}</left>
					<top>{L_TOP}</top>
					<width>{L_W}</width>
					<height>{L_H}</height>
					<texture>fold/{shade}</texture>
				</control>
				<control type="image">
					<left>{x}</left>
					<top>{L_TOP}</top>
					<width>{L_W}</width>
					<height>{L_H}</height>
					<texture border="4" colordiffuse="$VAR[FoldAccentEdge]">fold/{edge}</texture>
				</control>"""


def leaflet_strip_item(focused, stills):
    if stills:
        # a cream panel with the still, like the concertina's, small
        w, h = (236, 176) if focused else (212, 158)
        cw, ch, px, py = 212, 158, 14, 40
        cx, bottom = px + cw // 2, py + ch
        left, top = cx - w // 2, bottom - h
        lift = f"""
					<animation type="Focus" condition="!{RM}">
						<effect type="zoom" start="{cw / 236 * 100:.1f}" end="100" center="{cx},{bottom}" time="240" tween="back" easing="out"/>
					</animation>""" if focused else ""
        return f"""
				<control type="image">
					<left>{left - 40}</left>
					<top>{top - 40}</top>
					<width>{w + 80}</width>
					<height>{h + 80}</height>
					<texture border="48">fold/{'shadow_lift' if focused else 'shadow_card'}.png</texture>
				</control>
				<control type="group">
					<left>{left}</left>
					<top>{top}</top>
					<width>{w}</width>
					<height>{h}</height>{lift}
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture border="6" colordiffuse="cream">fold/rr4.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture diffuse="fold/rr4.png">fold/tooth_cream.png</texture>
					</control>
					<control type="image">
						<left>10</left>
						<top>10</top>
						<width>{w - 20}</width>
						<height>{round((w - 20) * 9 / 16)}</height>
						<texture colordiffuse="cream_deep">common/white.png</texture>
					</control>
					<control type="image">
						<left>10</left>
						<top>10</top>
						<width>{w - 20}</width>
						<height>{round((w - 20) * 9 / 16)}</height>
						<aspectratio>scale</aspectratio>
						<fadetime>160</fadetime>
						<texture background="true">$VAR[Concertina_Still]</texture>
						<visible>!ListItem.IsParentFolder</visible>
					</control>
					<control type="label">
						<left>12</left>
						<top>{h - 46}</top>
						<width>{w - 24}</width>
						<height>40</height>
						<font>{'disp_50' if not focused else 'disp_50'}</font>
						<textcolor>$VAR[FoldAccentInk]</textcolor>
						<label>$VAR[Concertina_Num]</label>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>6</height>
						<texture colordiffuse="$VAR[FoldAccent]">common/white.png</texture>
						<visible>{'Control.HasFocus(505)' if focused else 'false'}</visible>
					</control>
				</control>"""
    return closed_card(focused, 505, 128, 192, 142, 213, 20, 50, "$VAR[Table_CardColor]", "$VAR[Shelf_Art]", "", "",
                       parent_word="Up")


def leaflet_view():
    def plate(x, y, w, h, art, vis, aspect="scale"):
        return f"""
				<control type="group">
					<left>{x}</left>
					<top>{y}</top>
					<width>{w}</width>
					<height>{h}</height>
					<visible>{vis}</visible>
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
						<width>{w}</width>
						<height>{h}</height>
						<texture colordiffuse="cream_deep">common/white.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<aspectratio>{aspect}</aspectratio>
						<fadetime>200</fadetime>
						<texture background="true">{art}</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture>fold/plate_sheen.png</texture>
					</control>
				</control>"""
    p1 = L_P1 + 52
    p3 = L_P3 + 48
    lists = [
        ("!Container.Content(episodes)", 168, False),
        ("Container.Content(episodes)", 240, True),
    ]
    layouts = "".join(f"""
				<itemlayout width="{w}" height="300" condition="{c}">{leaflet_strip_item(False, st)}
				</itemlayout>
				<focusedlayout width="{w}" height="300" condition="{c}">{leaflet_strip_item(True, st)}
				</focusedlayout>""" for c, w, st in lists)
    return f"""
	<include name="VidView_505_Leaflet">
		<control type="group">
			<visible>Control.IsVisible(505)</visible>
			<!-- the leaflet: three panels standing on the table, the outer ones turned a little toward you -->
			<control type="group">
				<visible>Integer.IsGreater(Container.NumItems,0)</visible>
				<include>Anim_FadeVisible</include>
				<control type="image">
					<left>{L_P1 - 72}</left>
					<top>{L_TOP - 40}</top>
					<width>{3 * L_W + 144}</width>
					<height>{L_H + 150}</height>
					<texture border="104">fold/shadow_spread.png</texture>
				</control>
				<control type="group">
					<camera x="960" y="{L_TOP + L_H // 2}"/>
					<animation effect="rotatey" start="-7" end="-7" center="{L_P2}" time="0" condition="true">Conditional</animation>{_panel(L_P1, 'fold/rr5_l.png', 'edge_l.png', 'shade_p1.png')}
					{plate(p1, L_TOP + 44, 300, 450, '$VAR[Shelf_Art]', '!Container.Content(episodes) + !ListItem.IsParentFolder')}
					{plate(L_P1 + 28, L_TOP + 120, 496, 279, '$VAR[Concertina_Still]', 'Container.Content(episodes) + !ListItem.IsParentFolder')}
					<control type="label">
						<left>{L_P1 + 40}</left>
						<top>{L_TOP + 40}</top>
						<width>460</width>
						<height>120</height>
						<font>disp_112</font>
						<textcolor>$VAR[FoldAccentInk]</textcolor>
						<label>←</label>
						<visible>ListItem.IsParentFolder</visible>
					</control>
				</control>
				<control type="group">{_panel(L_P2, 'common/white.png', 'edge_c.png', 'shade_p2.png').replace('border="8" ', '')}
					<control type="grouplist">
						<left>{L_P2 + 40}</left>
						<top>{L_TOP + 40}</top>
						<width>{L_W - 80}</width>
						<height>{L_H - 70}</height>
						<orientation>vertical</orientation>
						<itemgap>0</itemgap>
						<usecontrolcoords>true</usecontrolcoords>
						<control type="label">
							<width>{L_W - 80}</width>
							<height>36</height>
							<font>caps_20_b</font>
							<textcolor>$VAR[FoldAccentInk]</textcolor>
							<label>$VAR[Shelf_Kicker]</label>
						</control>
						<control type="group">
							<width>{L_W - 80}</width>
							<height>0</height>
							<control type="textbox">
								<left>0</left>
								<top>0</top>
								<width>{L_W - 80}</width>
								<height>184</height>
								<font>head_50</font>
								<textcolor>ink</textcolor>
								<label>$VAR[Leaflet_Title]</label>
							</control>
						</control>
						<control type="textbox">
							<width>{L_W - 80}</width>
							<height max="162">auto</height>
							<font>head_50</font>
							<textcolor>clear</textcolor>
							<label>$VAR[Leaflet_Title]</label>
						</control>
						<control type="image">
							<width>10</width>
							<height>16</height>
							<texture />
						</control>
						<control type="textbox">
							<width>{L_W - 80}</width>
							<height max="64">auto</height>
							<font>caps_20</font>
							<textcolor>cap</textcolor>
							<label>$VAR[Shelf_Meta]</label>
						</control>
						<control type="image">
							<width>10</width>
							<height>14</height>
							<texture />
						</control>
						<control type="textbox">
							<width>{L_W - 80}</width>
							<height max="42">auto</height>
							<font>light_30</font>
							<textcolor>ink2</textcolor>
							<label>$INFO[ListItem.Tagline]</label>
						</control>
						<control type="image">
							<width>10</width>
							<height>10</height>
							<texture />
							<visible>!String.IsEmpty(ListItem.Tagline)</visible>
						</control>
						<control type="textbox">
							<width>{L_W - 80}</width>
							<height>{34 * 5}</height>
							<font>body_24</font>
							<textcolor>body</textcolor>
							<label>$INFO[ListItem.Plot]</label>
						</control>
					</control>
				</control>
				<control type="group">
					<camera x="960" y="{L_TOP + L_H // 2}"/>
					<animation effect="rotatey" start="7" end="7" center="{L_P3}" time="0" condition="true">Conditional</animation>{_panel(L_P3, 'fold/rr5_r.png', 'edge_r.png', 'shade_p3.png')}
					{plate(L_P3 + 36, L_TOP + 44, 480, 270, '$VAR[Leaflet_Print]', '$EXP[Leaflet_HasPrint]')}
					<control type="label">
						<left>{L_P3 + 40}</left>
						<top>{L_TOP + 44}</top>
						<width>472</width>
						<height>32</height>
						<font>caps_20_b</font>
						<textcolor>$VAR[FoldAccentInk]</textcolor>
						<label>No picture</label>
						<visible>!$EXP[Leaflet_HasPrint] + !ListItem.IsParentFolder</visible>
					</control>
					<control type="group">
						<left>{L_P3 + 40}</left>
						<top>{L_TOP + 352}</top>
						<visible>!ListItem.IsParentFolder</visible>
						<animation effect="slide" start="0,0" end="0,-244" time="0" condition="!$EXP[Leaflet_HasPrint]">Conditional</animation>
						<control type="label">
							<left>0</left>
							<top>0</top>
							<width>472</width>
							<height>32</height>
							<font>caps_20</font>
							<textcolor>cap</textcolor>
							<label>$VAR[Shelf_Facts]</label>
						</control>
						<control type="label">
							<left>0</left>
							<top>40</top>
							<width>472</width>
							<height>32</height>
							<font>caps_20</font>
							<textcolor>cap</textcolor>
							<label>$VAR[Leaflet_Facts2]</label>
						</control>
						<control type="label">
							<left>0</left>
							<top>80</top>
							<width>472</width>
							<height>32</height>
							<font>caps_20</font>
							<textcolor>cap</textcolor>
							<label>$INFO[ListItem.Studio,Studio [COLOR ink],[/COLOR]]</label>
						</control>
					</control>
				</control>
			</control>
			<!-- the strip of closed cards (stills in a season) -->
			<control type="group">
				<include content="Anim_StandUp"><param name="bottom" value="1040"/></include>
				<control type="list" id="505">
					<left>96</left>
					<top>740</top>
					<width>1680</width>
					<height>300</height>
					<orientation>horizontal</orientation>
					<preloaditems>2</preloaditems>
					<scrolltime tween="cubic" easing="out">260</scrolltime>
					<onup>9000</onup>
					<ondown>noop</ondown>
					<onleft>ActivateWindow(1155)</onleft>
					<onright>ActivateWindow(1155)</onright>
					<onback condition="$EXP[Lib_AtRoot]">9398</onback>
					<viewtype label="Leaflet">biginfo</viewtype>
					<visible>{LEAF_CONTENT}</visible>{layouts}
				</control>
			</control>
		</control>
	</include>"""


# ------------------------------------------------------------------------------ 506 Prints
P_X, P_Y = 52, 150
P_SW, P_SH = 444, 352
P_CW, P_CH = 412, 316
P_LW, P_LH = 436, 334
P_PX, P_PY = 16, 18


def print_card(focused):
    w, h = (P_LW, P_LH) if focused else (P_CW, P_CH)
    cx, bottom = P_PX + P_CW // 2, P_PY + P_CH
    left, top = cx - w // 2, bottom - h
    k = w / P_CW
    pl, pt = round(18 * k), round(16 * k)
    pw = w - pl - round(14 * k)
    ph = round(pw * 9 / 16)
    sp = 72 if focused else 40
    tex = "shadow_lift" if focused else "shadow_card"
    lift = f"""
					<animation type="Focus" condition="!{RM}">
						<effect type="zoom" start="{P_CW / P_LW * 100:.1f}" end="100" center="{cx},{bottom}" time="240" tween="back" easing="out"/>
						<effect type="rotatex" start="0" end="-7" center="{bottom}" time="240" tween="back" easing="out"/>
					</animation>
					<animation type="Conditional" condition="{RM} + Control.HasFocus(506)">
						<effect type="rotatex" start="-7" end="-7" center="{bottom}" time="0"/>
					</animation>
					<animation type="Unfocus" condition="!{RM}">
						<effect type="rotatex" start="-7" end="0" center="{bottom}" time="180" tween="cubic" easing="out"/>
					</animation>""" if focused else ""
    t_font = "sans_24_semi" if focused else "sans_22_semi"
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
						<param name="color" value="$VAR[Prints_CardColor]"/>
						<param name="plate_l" value="{pl}"/>
						<param name="plate_t" value="{pt}"/>
						<param name="plate_w" value="{pw}"/>
						<param name="plate_h" value="{ph}"/>
						<param name="art" value="$VAR[Prints_WideArt]"/>
						<param name="fallback" value=""/>
					</include>
					<!-- no wide picture: the item's own picture whole on the plate, or a glyph-free title card -->
					<control type="image">
						<left>{pl + 12}</left>
						<top>{pt + 10}</top>
						<width>{pw - 24}</width>
						<height>{ph - 20}</height>
						<aspectratio>keep</aspectratio>
						<fadetime>160</fadetime>
						<texture background="true">$VAR[Prints_Icon]</texture>
						<visible>!$EXP[Prints_HasWide] + $EXP[Prints_HasIcon]</visible>
					</control>
					<control type="textbox">
						<left>{pl + 20}</left>
						<top>{pt + 18}</top>
						<width>{pw - 40}</width>
						<height>{ph - 36}</height>
						<font>head_34</font>
						<textcolor>ink2</textcolor>
						<label>$VAR[List_Title]</label>
						<visible>!$EXP[Prints_HasWide] + !$EXP[Prints_HasIcon]</visible>
					</control>
					<control type="image">
						<left>{pl + pw - 34}</left>
						<top>{pt + 6}</top>
						<width>28</width>
						<height>28</height>
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
					</control>
					<control type="label">
						<left>{pl}</left>
						<top>{pt + ph + 12}</top>
						<width>{pw}</width>
						<height>34</height>
						<font>{t_font}</font>
						<textcolor>$VAR[Prints_OnCard]</textcolor>
						<label>$VAR[List_Title]</label>
						<visible>$EXP[Prints_HasWide] | $EXP[Prints_HasIcon]</visible>
					</control>
					<control type="label">
						<left>{pl}</left>
						<top>{pt + ph + 46}</top>
						<width>{pw}</width>
						<height>30</height>
						<font>caps_20</font>
						<textcolor>$VAR[Prints_OnCard]</textcolor>
						<label>$VAR[Prints_Meta]</label>
					</control>{f'''
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture>fold/card_light.png</texture>
						<visible>Control.HasFocus(506)</visible>
					</control>''' if focused else ''}
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
						<textcolor>$VAR[FoldAccentInk]</textcolor>
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
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{w}</width>
						<height>{h}</height>
						<texture border="4" colordiffuse="$VAR[FoldAccent]">fold/edge_all.png</texture>
						<visible>{'Control.HasFocus(506)' if focused else 'false'}</visible>
					</control>
				</control>"""


def prints_view():
    return f"""
	<include name="VidView_506_Prints">
		<control type="group">
			<visible>Control.IsVisible(506)</visible>
			<include content="Anim_StandUp"><param name="bottom" value="{P_Y + P_SH * 3}"/></include>
			<control type="panel" id="506">
				<left>{P_X}</left>
				<top>{P_Y}</top>
				<width>{P_SW * 4}</width>
				<height>{1080 - P_Y}</height>
				<orientation>vertical</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">280</scrolltime>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<onright>9000</onright>
				<onleft>ActivateWindow(1155)</onleft>
				<onback condition="$EXP[Lib_AtRoot]">9398</onback>
				<viewtype label="Prints">wide</viewtype>
				<itemlayout width="{P_SW}" height="{P_SH}">{print_card(False)}
				</itemlayout>
				<focusedlayout width="{P_SW}" height="{P_SH}">{print_card(True)}
				</focusedlayout>
			</control>
		</control>
	</include>"""


def variables():
    return """
	<!-- 0.9.13 views: Table / Leaflet / Prints -->
	<variable name="Table_Art">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),Default)">$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Table_CardColor">
		<value condition="String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season) | String.IsEqual(ListItem.DBType,episode)">cobalt</value>
		<value>verm</value>
	</variable>
	<variable name="Leaflet_Title">
		<value condition="ListItem.IsParentFolder">Up a level</value>
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Episode,,. ]$INFO[ListItem.Title]</value>
		<value condition="!String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<expression name="Leaflet_HasPrint">!ListItem.IsParentFolder + [!String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.fanart)) | !String.IsEmpty(ListItem.Art(landscape))]</expression>
	<variable name="Leaflet_Print">
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
		<value>$INFO[ListItem.Art(landscape)]</value>
	</variable>
	<variable name="Leaflet_Facts2">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Premiered)">Aired [COLOR ink]$VAR[Date_PR][/COLOR]</value>
		<value condition="!String.IsEmpty(ListItem.Genre)">[COLOR ink]$INFO[ListItem.Genre][/COLOR]</value>
	</variable>
	<!-- prints: library items show a real wide picture; add-ons their fanart; plug-in items / files their own
	     picture whole (keep), never a generated image://video@ frame grab -->
	<expression name="Prints_HasWide">!ListItem.IsParentFolder + [[String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)] | [!String.IsEmpty(ListItem.DBType) + [!String.IsEmpty(ListItem.Art(landscape)) | !String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.landscape)) | !String.IsEmpty(ListItem.Art(tvshow.fanart))]] | [Container.Content(addons) + !String.IsEmpty(ListItem.Art(fanart))]]</expression>
	<expression name="Prints_HasIcon">!ListItem.IsParentFolder + [!String.IsEmpty(ListItem.Art(thumb)) | !String.IsEmpty(ListItem.Art(poster)) | [!String.IsEmpty(ListItem.Art(icon)) + !String.StartsWith(ListItem.Art(icon),Default)]]</expression>
	<variable name="Prints_WideArt">
		<value condition="!$EXP[Prints_HasWide]"></value>
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb)) + !String.StartsWith(ListItem.Art(thumb),image://video@)">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.DBType) + !String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.DBType) + !String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value condition="!String.IsEmpty(ListItem.DBType) + !String.IsEmpty(ListItem.Art(tvshow.landscape))">$INFO[ListItem.Art(tvshow.landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.DBType) + !String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
		<value condition="Container.Content(addons)">$INFO[ListItem.Art(fanart)]</value>
	</variable>
	<variable name="Prints_Icon">
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value>$INFO[ListItem.Art(icon)]</value>
	</variable>
	<variable name="Prints_CardColor">
		<value condition="String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season) | String.IsEqual(ListItem.DBType,episode)">cobalt</value>
		<value condition="String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,set) | String.IsEqual(ListItem.DBType,musicvideo)">verm</value>
		<value>graph</value>
	</variable>
	<variable name="Prints_OnCard">
		<value>on_card</value>
	</variable>
	<variable name="Prints_Meta">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Season,S,]$INFO[ListItem.Episode, · E,]$INFO[ListItem.Duration(mins), · , min]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$INFO[ListItem.Property(TotalSeasons), · , seasons]</value>
		<value condition="String.IsEqual(ListItem.DBType,season)">$INFO[ListItem.Property(TotalEpisodes),, episodes]$INFO[ListItem.Property(WatchedEpisodes), · , watched]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Total),, films]$INFO[ListItem.Property(Watched), · , watched]</value>
		<value condition="String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,musicvideo)">$INFO[ListItem.Year]$INFO[ListItem.Duration(mins), · , min]</value>
		<value>$INFO[ListItem.Label2]</value>
	</variable>"""
