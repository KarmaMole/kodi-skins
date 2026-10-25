"""Generate skins/skin.fold/1080i/Includes_Home.xml (Fold Home: die-cut tabs, a row of closed cards that lift
and tilt toward you, the info block of the focused card, and a second row of cream cards).
    python skins/skin.fold/_src/make_home.py

Design contract: docs/concepts/round4/mockups/FoldHome.html (pixel values below come from it).
Ids
  9000 tab group: 9001 Films, 9002 Series, 9003 Music, 9004 Search, 9005 Settings (9001-9004 hide with HideMenu.*)
  row A (closed cards, fixedlist focusposition 2): 9110 films, 9130 series, 9150 music, 9180 settings
  row B (cream cards): 9120 films in progress | 9121 recently added films (when 9120 is empty),
                       9140 new episodes, 9160 recently played albums | 9161 random albums (fallback)
  9170 search card
  title probes (NumPages tier tests): 9310 + n
  counters (hidden, loaded after a 1 s rest): 9191 films, 9192 unwatched films, 9193 shows, 9194 albums
Window(Home) properties
  fold.section  films|series|music|search|settings (focused tab; kept while focus is in the rows)
  fold.from     slot the info spread opens from (h0..h6 row A, b0..b5 row B), set right before Action(Info)
  fold.n.films / fold.n.series / fold.n.music   tab counts for the other windows' decorative tabs
"""
from pathlib import Path
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Home.xml"

# ---------------------------------------------------------------------------------------------- geometry
LIST_X, LIST_Y, LIST_W, LIST_H = 56, 100, 1864, 590
PAD = 40                     # card x inside its slot
S_W, S_H, S_TOP = 214, 330, 112      # resting card (FoldHome .card.sm: top 212)
F_W, F_H, F_TOP = 248, 382, 60       # lifted card (FoldHome .card.f: top 160)
SLOT_S, SLOT_F = S_W + 34, F_W + 36
# music sleeves (square plate)
MS_W, MS_H, MF_W, MF_H = 270, 330, 312, 382
MSLOT_S, MSLOT_F = MS_W + 34, MF_W + 36
# row B cream cards (FoldHome .ccard)
B_Y = 872                    # row head
B_LIST_Y = 912 - 40
C_W, C_H, C_PITCH = 270, 220, 294
CAM_Y = 540 - LIST_Y         # camera y relative to the list (screen centre height)
SLIDE_B = 330                # the page slides up while row B has focus

ROWB_FOCUS = {
    "films": "Control.HasFocus(9120) | Control.HasFocus(9121)",
    "series": "Control.HasFocus(9140)",
    "music": "Control.HasFocus(9160) | Control.HasFocus(9161)",
}

RM = "Skin.HasSetting(fold.reducemotion)"

# ---- 0.9.10 custom rows (Includes_CustomRows.xml, tools/customrows/make_customrows.py): opt-in cream rows below
# row B in every section. Down from the section's last row continues into them; the page slides on so the focused
# one sits where a focused row B sits (head y 542), and row A folds flat as it does for row B.
CUSTOM_IDS = (9881, 9882, 9883)
C_ROW_Y = B_Y + 300          # first custom row head
C_ROW_PITCH = 300
DOWN_TO_CUSTOM = """
				<ondown condition="$EXP[CustomRow1On]">9881</ondown>
				<ondown condition="!$EXP[CustomRow1On] + $EXP[CustomRow2On]">9882</ondown>
				<ondown condition="!$EXP[CustomRow1On] + !$EXP[CustomRow2On] + $EXP[CustomRow3On]">9883</ondown>"""


def custom_rows():
    out = []
    for i, rid in enumerate(CUSTOM_IDS):
        n = i + 1
        slides = ""
        if n == 1:  # under the tabs once the third row has focus below two others: fade
            slides += '\n\t\t\t\t\t<animation effect="fade" start="100" end="0" time="200" condition="Control.HasFocus(9883) + $EXP[CustomRow1On] + $EXP[CustomRow2On]">Conditional</animation>'
        if n >= 2:
            slides += '\n\t\t\t\t\t<animation effect="slide" start="0,0" end="0,300" time="0" condition="$EXP[CustomRow1On]">Conditional</animation>'
        if n == 3:
            slides += '\n\t\t\t\t\t<animation effect="slide" start="0,0" end="0,300" time="0" condition="$EXP[CustomRow2On]">Conditional</animation>'
        ups = []
        if n == 3:
            ups.append(('$EXP[CustomRow2On]', 9882))
            ups.append(('!$EXP[CustomRow2On] + $EXP[CustomRow1On]', 9881))
        if n == 2:
            ups.append(('$EXP[CustomRow1On]', 9881))
        ups += [('$EXP[Home_Films] + Integer.IsGreater(Container(9120).NumItems,0)', 9120), ('$EXP[Home_Films]', 9121),
                ('$EXP[Home_Series]', 9140),
                ('$EXP[Home_Music] + Integer.IsGreater(Container(9160).NumItems,0)', 9160), ('$EXP[Home_Music]', 9161),
                ('$EXP[Home_Search]', 9170), ('$EXP[Home_Settings]', 9180)]
        up_xml = "".join(f'\n\t\t\t\t\t\t<onup condition="{c}">{t}</onup>' for c, t in ups) + "\n\t\t\t\t\t\t<onup>9000</onup>"
        downs = []
        if n == 1:
            downs = [('$EXP[CustomRow2On]', 9882), ('!$EXP[CustomRow2On] + $EXP[CustomRow3On]', 9883)]
        if n == 2:
            downs = [('$EXP[CustomRow3On]', 9883)]
        down_xml = "".join(f'\n\t\t\t\t\t\t<ondown condition="{c}">{t}</ondown>' for c, t in downs) + "\n\t\t\t\t\t\t<ondown>noop</ondown>"
        card = lambda f: cream_card(f, rid, "video", art="$VAR[CustomRow_WideArt]", vtitle="$VAR[Home_CustomTitle]")
        out.append(f"""
				<control type="group">{slides}
					<control type="label">
						<left>96</left>
						<top>0</top>
						<width>1300</width>
						<height>32</height>
						<font>caps_20_b</font>
						<textcolor>ink</textcolor>
						<label>$VAR[CustomRow_Title{n}][COLOR cap2]   $VAR[CustomRow_Count{n}][/COLOR]</label>
						<visible>$EXP[CustomRow{n}On]</visible>
					</control>
					<control type="list" id="{rid}">
						<left>{LIST_X}</left>
						<top>0</top>
						<width>{C_PITCH * 6}</width>
						<height>{C_H + 120}</height>
						<orientation>horizontal</orientation>
						<preloaditems>2</preloaditems>
						<scrolltime tween="cubic" easing="out">240</scrolltime>{up_xml}{down_xml}
						<onleft>noop</onleft>
						<onright>noop</onright>
						<onback>9000</onback>
						<itemlayout width="{C_PITCH}" height="{C_H + 120}">{card(False)}
						</itemlayout>
						<focusedlayout width="{C_PITCH}" height="{C_H + 120}">{card(True)}
						</focusedlayout>
						<include content="CustomRow_Content"><param name="row" value="{n}"/></include>
					</control>
				</control>""")
    return f"""
			<!-- custom rows (0.9.10): below row B in every section; the lists always load (no <visible>), empty ones draw nothing -->
			<control type="group">
				<top>{C_ROW_Y}</top>{''.join(out)}
			</control>"""


def anim_focus_lift(cx, bottom, scale, list_id):
    """Lift on focus (0.9.3): ONE zoom + tilt on ONE group, about the bottom edge, 180 ms sine out, no overshoot.
    Both layouts are the resting size, so the row never reflows; the lift is the zoom.
    Reduce motion (0.9.8): the lifted state is a time-0 Conditional on the list's focus, not a second Focus animation
    (Kodi resets only the FIRST Focus animation on unfocus, so a reduce-motion Focus twin stayed lifted)."""
    z = f"{scale:.1f}"
    return f"""
						<animation type="Focus" condition="!{RM}">
							<effect type="zoom" start="100" end="{z}" center="{cx},{bottom}" time="180" tween="sine" easing="out"/>
							<effect type="rotatex" start="0" end="-9" center="{bottom}" time="180" tween="sine" easing="out"/>
						</animation>
						<animation type="Conditional" condition="{RM} + Control.HasFocus({list_id})">
							<effect type="zoom" start="{z}" end="{z}" center="{cx},{bottom}" time="0"/>
							<effect type="rotatex" start="-9" end="-9" center="{bottom}" time="0"/>
						</animation>
						<animation type="Unfocus" condition="!{RM}">
							<effect type="zoom" start="{z}" end="100" center="{cx},{bottom}" time="140" tween="sine" easing="out"/>
							<effect type="rotatex" start="-9" end="0" center="{bottom}" time="140" tween="sine" easing="out"/>
						</animation>"""


def card_layout(kind, focused, list_id):
    """Closed card in a row-A layout. kind: poster | square | system"""
    if kind == "square":
        sw, sh, fw, fh = MS_W, MS_H, MF_W, MF_H
    else:
        sw, sh, fw, fh = S_W, S_H, F_W, F_H
    w, h, top = sw, sh, S_TOP            # 0.9.3: the focused layout is the resting card, lifted by zoom
    scale = fw / sw * 100
    cx, bottom = PAD + w // 2, top + h
    pl, pt = 18, 16
    pw = w - pl - 14
    ph = pw if kind == "square" else 258
    foot_font, foot_b = "num_20", 15
    if kind == "system":
        art = ""
        foot_l, foot_r = "$INFO[ListItem.Label2]", ""
    elif kind == "square":
        art = "$INFO[ListItem.Art(thumb)]"
        foot_l, foot_r = "$INFO[ListItem.Year]", "$VAR[Home_SquareFootR]"
    else:
        art = "$VAR[Home_CardArt]"
        foot_l, foot_r = "$INFO[ListItem.Year]", "$VAR[Home_CardFootR]"
    shadow = f"""
					<control type="image">
						<left>{PAD - 48}</left>
						<top>{top - 48}</top>
						<width>{w + 96}</width>
						<height>{h + 96}</height>
						<texture border="56">fold/shadow_card.png</texture>"""
    if focused:
        # deeper shadow of the lifted card: pre-sized to the lifted bounds, it only fades (no scale)
        lw, lh = round(w * scale / 100), round(h * scale / 100)
        shadow += f"""
					</control>
					<control type="image">
						<left>{cx - lw // 2 - 96}</left>
						<top>{bottom - lh - 96}</top>
						<width>{lw + 192}</width>
						<height>{lh + 192}</height>
						<texture border="104">fold/shadow_lift.png</texture>
						<visible>Control.HasFocus({list_id})</visible>
						<animation type="Focus" condition="!{RM}">
							<effect type="fade" start="0" end="100" time="180" tween="sine" easing="out"/>
						</animation>"""
    shadow += "\n\t\t\t\t\t</control>"
    body_extra = ""
    if kind == "system":
        body_extra = f"""
							<control type="label">
								<left>{pl + 14}</left>
								<top>{pt + 14}</top>
								<width>{pw - 28}</width>
								<height>40</height>
								<font>head_28</font>
								<textcolor>ink</textcolor>
								<label>$INFO[ListItem.Label]</label>
							</control>
							<control type="textbox">
								<left>{pl + 14}</left>
								<top>{pt + 58}</top>
								<width>{pw - 28}</width>
								<height>155</height>
								<font>body_22</font>
								<textcolor>ink2</textcolor>
								<label>$INFO[ListItem.Property(Desc)]</label>
							</control>
"""
    light = ""
    if focused:
        light = f"""
							<control type="image">
								<left>0</left>
								<top>0</top>
								<width>{w}</width>
								<height>{h}</height>
								<texture>fold/card_light.png</texture>
								<visible>Control.HasFocus({list_id})</visible>
							</control>"""
    color = {"poster": "$VAR[Home_RowColor]", "square": "mari", "system": "graph"}[kind]
    punch = ""
    if kind == "poster":
        punch = f"""
							<control type="image">
								<left>{pl + pw - 40}</left>
								<top>{pt + 8}</top>
								<width>34</width>
								<height>34</height>
								<texture>fold/punch.png</texture>
								<visible>Integer.IsGreater(ListItem.PlayCount,0) + !ListItem.IsFolder + $EXP[ShowWatchedMarkers]</visible>
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
							</control>"""
    plate_art = "" if kind == "system" else "true"
    body = f"""
					<control type="group">
						<left>{PAD}</left>
						<top>{top}</top>
						<width>{w}</width>
						<height>{h}</height>
						<camera x="{PAD + w // 2}" y="{CAM_Y}"/>{anim_focus_lift(cx, bottom, scale, list_id) if focused else ''}
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
							<param name="foot_l" value="{foot_l}"/>
							<param name="foot_r" value="{foot_r}"/>
							<param name="foot_font" value="{foot_font}"/>
							<param name="foot_b" value="{foot_b}"/>
							<param name="foot_color" value="{'ink' if kind == 'square' else 'on_card'}"/>
							<param name="aspect" value="scale"/>
							<param name="fallback" value="{'' if kind == 'system' else '$INFO[ListItem.Label]'}"/>
						</include>{body_extra}{punch}{light}
					</control>"""
    return shadow + body


def row_a(list_id, kind, content, onup, ondown, onclick, extra_visible="true", sort="", limit="", focuspos=2):
    if kind == "square":
        slot_s, slot_f = MSLOT_S, MSLOT_F
    else:
        slot_s, slot_f = SLOT_S, SLOT_F
    sortattr = f' sortby="{sort[0]}" sortorder="{sort[1]}"' if sort else ""
    lim = f' limit="{limit}"' if limit else ""
    content_xml = (f'<content target="videos"{sortattr}{lim} browse="never">{content}</content>' if content.startswith(("special://skin/playlists/fold_unwatched", "videodb"))
                   else content)
    if content.startswith("musicdb"):
        content_xml = f'<content target="music"{sortattr}{lim} browse="never">{content}</content>'
    if content.startswith("special://skin/playlists/fold_inprogress_tv"):
        content_xml = f'<content target="videos"{sortattr}{lim} browse="never">{content}</content>'
    clicks = "\n".join(f"\t\t\t\t<onclick>{c}</onclick>" for c in onclick)
    return f"""
			<control type="list" id="{list_id}">
				<left>{LIST_X}</left>
				<top>{LIST_Y}</top>
				<width>{LIST_W}</width>
				<height>{LIST_H}</height>
				<orientation>horizontal</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="sine" easing="out">200</scrolltime>
				<visible>{extra_visible}</visible>
				<onup>{onup}</onup>
				<ondown>{ondown}</ondown>
				<onback>{onup}</onback>
{clicks}
				<itemlayout width="{slot_s}" height="{LIST_H}">{card_layout(kind, False, list_id)}
				</itemlayout>
				<focusedlayout width="{slot_s}" height="{LIST_H}">{card_layout(kind, True, list_id)}
				</focusedlayout>
				{content_xml}
			</control>"""


def cream_card(focused, list_id, kind, art="$VAR[Home_CreamArt]", vtitle="$VAR[Home_CreamTitle]"):
    """Row-B cream card (FoldHome .ccard): title + mono runtime, perforated progress, art.
    art / vtitle: the video card's picture and title (0.9.10 custom rows pass their own)."""
    lift = ""
    if focused:
        lift = f"""
						<animation type="Focus" condition="!{RM}">
							<effect type="slide" start="0,0" end="0,-10" time="180" tween="sine" easing="out"/>
						</animation>
						<animation type="Conditional" condition="{RM} + Control.HasFocus({list_id})">
							<effect type="slide" start="0,-10" end="0,-10" time="0"/>
						</animation>
						<animation type="Unfocus" condition="!{RM}">
							<effect type="slide" start="0,-10" end="0,0" time="140" tween="sine" easing="out"/>
						</animation>"""
    shadow = f"""
					<control type="image">
						<left>{PAD - 40}</left>
						<top>0</top>
						<width>{C_W + 80}</width>
						<height>{C_H + 80}</height>
						<texture border="48">fold/shadow_cream.png</texture>
					</control>"""
    if focused:
        shadow += f"""
					<control type="image">
						<left>{PAD - 56}</left>
						<top>{40 - 56}</top>
						<width>{C_W + 112}</width>
						<height>{C_H + 112}</height>
						<texture border="60" colordiffuse="99ffffff">fold/shadow_lift_s.png</texture>
						<visible>Control.HasFocus({list_id})</visible>
						<animation effect="fade" start="0" end="100" time="220">Visible</animation>
					</control>"""
    if kind == "album":
        art_xml = f"""
						<control type="image">
							<left>16</left>
							<top>64</top>
							<width>140</width>
							<height>140</height>
							<texture colordiffuse="cream_deep">common/white.png</texture>
						</control>
						<control type="image">
							<left>16</left>
							<top>64</top>
							<width>140</width>
							<height>140</height>
							<aspectratio>scale</aspectratio>
							<fadetime>160</fadetime>
							<texture background="true">$INFO[ListItem.Art(thumb)]</texture>
						</control>
						<control type="textbox">
							<left>172</left>
							<top>66</top>
							<width>84</width>
							<height>140</height>
							<font>caps_20</font>
							<textcolor>cap</textcolor>
							<label>$INFO[ListItem.Year]</label>
						</control>"""
        title, right = "$INFO[ListItem.Label]", ""
        line2 = "$INFO[ListItem.Artist]"
    else:
        art_xml = f"""
						<control type="image">
							<left>16</left>
							<top>64</top>
							<width>238</width>
							<height>150</height>
							<texture colordiffuse="cream_deep">common/white.png</texture>
						</control>
						<control type="image">
							<left>16</left>
							<top>64</top>
							<width>238</width>
							<height>150</height>
							<aspectratio>scale</aspectratio>
							<fadetime>160</fadetime>
							<texture background="true">{art}</texture>
						</control>"""
        title, right = vtitle, "$INFO[ListItem.Duration(mins),,′]"
        line2 = ""
    edge = ""
    if focused:
        edge = f"""
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{C_W}</width>
							<height>{C_H}</height>
							<texture border="6" colordiffuse="$VAR[FoldAccent]">fold/edge_all.png</texture>
							<visible>Control.HasFocus({list_id})</visible>
						</control>"""
    return f"""{shadow}
					<control type="group">
						<left>{PAD}</left>
						<top>40</top>
						<width>{C_W}</width>
						<height>{C_H}</height>
						<camera x="{PAD + C_W // 2}" y="{540 - B_LIST_Y}"/>{lift}
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{C_W}</width>
							<height>{C_H}</height>
							<texture border="6" colordiffuse="cream">fold/rr4.png</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{C_W}</width>
							<height>{C_H}</height>
							<texture diffuse="fold/rr4.png">fold/tooth_cream.png</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{C_W}</width>
							<height>2</height>
							<texture colordiffuse="white">common/white.png</texture>
						</control>
						<control type="label">
							<left>16</left>
							<top>8</top>
							<width>{170 if right else 238}</width>
							<height>36</height>
							<font>sans_22_semi</font>
							<textcolor>ink</textcolor>
							<selectedcolor>ink</selectedcolor>
							<label>{title}</label>
						</control>
						<control type="label">
							<left>16</left>
							<top>8</top>
							<width>238</width>
							<height>36</height>
							<align>right</align>
							<font>numr_20</font>
							<textcolor>cap</textcolor>
							<label>{right}</label>
						</control>
						<control type="label">
							<left>16</left>
							<top>30</top>
							<width>238</width>
							<height>30</height>
							<font>body_20</font>
							<textcolor>cap</textcolor>
							<label>{line2}</label>
							<visible>{'true' if line2 else 'false'}</visible>
						</control>
						<!-- perforated progress (FoldHome .perf): dashes 6 on / 5 off, the played part in the accent -->
						<control type="image">
							<left>16</left>
							<top>50</top>
							<width>238</width>
							<height>3</height>
							<aspectratio align="left">center</aspectratio>
							<texture colordiffuse="rule_strong">fold/perf.png</texture>
							<visible>{'false' if kind == 'album' else 'true'}</visible>
						</control>
						<control type="progress">
							<left>16</left>
							<top>50</top>
							<width>238</width>
							<height>3</height>
							<texturebg />
							<lefttexture />
							<midtexture colordiffuse="$VAR[FoldAccent]">common/white.png</midtexture>
							<righttexture />
							<info>ListItem.PercentPlayed</info>
							<visible>{'false' if kind == 'album' else 'true'}</visible>
						</control>{art_xml}
{edge}
					</control>"""


def row_b(list_id, kind, content_xml, onup, onclick, visible="true"):
    onback = {9120: 9001, 9121: 9001, 9140: 9002, 9160: 9003, 9161: 9003}[list_id]
    clicks = "\n".join(f"\t\t\t\t<onclick>{c}</onclick>" for c in onclick)
    return f"""
			<control type="list" id="{list_id}">
				<left>{LIST_X}</left>
				<top>{B_LIST_Y}</top>
				<width>{C_PITCH * 6}</width>
				<height>{C_H + 120}</height>
				<orientation>horizontal</orientation>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">240</scrolltime>
				<visible>{visible}</visible>
				<onup>{onup}</onup>{DOWN_TO_CUSTOM}
				<onback>{onback}</onback>
{clicks}
				<itemlayout width="{C_PITCH}" height="{C_H + 120}">{cream_card(False, list_id, kind)}
				</itemlayout>
				<focusedlayout width="{C_PITCH}" height="{C_H + 120}">{cream_card(True, list_id, kind)}
				</focusedlayout>
				{content_xml}
			</control>"""


def info_block(c, probe, section, rowb, kind):
    """Title (two size tiers picked by a NumPages probe), meta line, tagline / status, plot, facts."""
    if rowb:
        vis = f"$EXP[Home_{section.title()}] + [{ROWB_FOCUS[section]}] + Control.HasFocus({c})"
    elif c == 9131:
        vis = f"$EXP[Home_Series] + !Integer.IsGreater(Container(9130).NumItems,0) + ![{ROWB_FOCUS['series']}] + !$EXP[CustomRowsFocus]"
    else:
        vis = f"$EXP[Home_{section.title()}] + ![{ROWB_FOCUS.get(section, 'false')}] + !$EXP[CustomRowsFocus]"
    C = f"Container({c})"
    return f"""
			<!-- info: {c} -->
			<control type="group">
				<left>96</left>
				<top>586</top>
				<visible>{vis}</visible>
				<visible>!String.IsEmpty({C}.ListItem.Label)</visible>
				<control type="textbox" id="{probe}">
					<left>-3000</left>
					<top>0</top>
					<width>860</width>
					<height>186</height>
					<font>disp_132</font>
					<textcolor>clear</textcolor>
					<label>$VAR[Home_Title_{c}]</label>
				</control>
				<control type="textbox" id="{probe + 20}">
					<left>-3000</left>
					<top>300</top>
					<width>880</width>
					<height>108</height>
					<font>disp_72</font>
					<textcolor>clear</textcolor>
					<label>$VAR[Home_Title_{c}]</label>
				</control>
				<control type="label">
					<left>0</left>
					<top>-10</top>
					<width>880</width>
					<height>150</height>
					<font>disp_132</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Home_Title_{c}]</label>
					<visible>!Integer.IsGreater(Container({probe}).NumPages,1)</visible>
				</control>
				<control type="label">
					<left>0</left>
					<top>45</top>
					<width>880</width>
					<height>80</height>
					<font>disp_72</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Home_Title_{c}]</label>
					<visible>Integer.IsGreater(Container({probe}).NumPages,1) + !Integer.IsGreater(Container({probe + 20}).NumPages,1)</visible>
				</control>
				<control type="textbox">
					<left>0</left>
					<top>4</top>
					<width>880</width>
					<height>140</height>
					<font>disp_64</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Home_Title_{c}]</label>
					<visible>Integer.IsGreater(Container({probe + 20}).NumPages,1)</visible>
				</control>
				<control type="label">
					<left>0</left>
					<top>144</top>
					<width>880</width>
					<height>36</height>
					<font>meta_22</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Home_Meta_{c}]</label>
				</control>
				<control type="label">
					<left>0</left>
					<top>188</top>
					<width>880</width>
					<height>46</height>
					<font>light_34</font>
					<textcolor>ink2</textcolor>
					<label>$VAR[Home_Tag_{c}]</label>
				</control>
				<control type="group">
					<!-- 0.9.3: the plot re-flows only once the row rests, then crossfades in -->
					<visible>!{C}.Scrolling</visible>
					<animation effect="fade" start="0" end="100" time="160" tween="sine" easing="out">Visible</animation>
				<control type="textbox" id="{probe + 50}">
					<left>912</left>
					<top>14</top>
					<width>836</width>
					<height>148</height>
					<font>body_26</font>
					<textcolor>body</textcolor>
					<label>$VAR[Home_Plot_{c}]</label>
				</control>
				<include content="Fold_PlotEllipsis"><param name="id" value="{probe + 50}"/><param name="right" value="1748"/><param name="top" value="{14 + 37 * 3}"/><param name="pitch" value="37"/><param name="font" value="body_26"/></include>
				</control>
				<control type="label">
					<left>912</left>
					<top>182</top>
					<width>836</width>
					<height>32</height>
					<font>caps_20</font>
					<textcolor>cap</textcolor>
					<label>$VAR[Home_Facts_{c}]</label>
				</control>
			</control>"""


DOT = "[COLOR verm]  ·  [/COLOR]"


def dot(color):
    return f"[COLOR {color}] · [/COLOR]"


def variables():
    v = []

    def var(name, values):
        lines = [f'\t<variable name="{name}">']
        for cond, val in values:
            if cond:
                lines.append(f'\t\t<value condition="{cond}">{val}</value>')
            else:
                lines.append(f"\t\t<value>{val}</value>")
        lines.append("\t</variable>")
        v.append("\n".join(lines))

    for c in (9110, 9120, 9121):
        C = f"Container({c}).ListItem"
        d = dot("verm")
        var(f"Home_Title_{c}", [(f"!String.IsEmpty({C}.Title)", f"$INFO[{C}.Title]"), ("", f"$INFO[{C}.Label]")])
        var(f"Home_Meta_{c}", [("", f"$INFO[{C}.Director,,{d}]$INFO[{C}.Year]$INFO[{C}.Duration(mins),{d}, MIN]$VAR[Home_MPAA_{c}]")])
        var(f"Home_MPAA_{c}", [(f"String.IsEmpty({C}.MPAA)", ""),
                               (f"String.IsEqual({C}.MPAA,Rated R)", f"{d}R"),
                               (f"String.IsEqual({C}.MPAA,Rated PG-13)", f"{d}PG-13"),
                               (f"String.IsEqual({C}.MPAA,Rated PG)", f"{d}PG"),
                               (f"String.IsEqual({C}.MPAA,Rated G)", f"{d}G"),
                               (f"String.IsEqual({C}.MPAA,Rated NC-17)", f"{d}NC-17"),
                               (f"String.IsEqual({C}.MPAA,Rated NR) | String.IsEqual({C}.MPAA,Rated)", ""),
                               ("", f"{d}$INFO[{C}.MPAA]")])
        var(f"Home_Tag_{c}", [(f"{C}.IsResumable", f"Stopped at $INFO[{C}.PercentPlayed]%$INFO[{C}.Tagline,  ·  ,]"),
                              ("", f"$INFO[{C}.Tagline]")])
        var(f"Home_Plot_{c}", [("", f"$INFO[{C}.Plot]")])
    # Films facts: rebuild cleanly (Rating 7.6   Ends 11:34 PM   Genre)
    for c in (9110, 9120, 9121):
        C = f"Container({c}).ListItem"
        var(f"Home_Facts_{c}", [("", f"$INFO[{C}.Rating,Rating [COLOR ink],[/COLOR]   ]$INFO[{C}.EndTime,Ends [COLOR ink],[/COLOR]   ]$INFO[{C}.Genre]")])

    # Series: shows (9130 / 9131) and episodes (9140)
    for c in (9130, 9131):
        C = f"Container({c}).ListItem"
        d = dot("cobalt")
        var(f"Home_Title_{c}", [(f"!String.IsEmpty({C}.TVShowTitle)", f"$INFO[{C}.TVShowTitle]"), ("", f"$INFO[{C}.Label]")])
        var(f"Home_Meta_{c}", [(f"Integer.IsEqual({C}.Property(TotalSeasons),1)", f"$INFO[{C}.Genre,,{d}]$INFO[{C}.Year]{d}1 season$INFO[{C}.Studio,{d},]"),
                               ("", f"$INFO[{C}.Genre,,{d}]$INFO[{C}.Year]$INFO[{C}.Property(TotalSeasons),{d}, seasons]$INFO[{C}.Studio,{d},]")])
        var(f"Home_Tag_{c}", [(f"Integer.IsGreater({C}.Property(TotalEpisodes),0)", f"$INFO[{C}.Property(WatchedEpisodes)] of $INFO[{C}.Property(TotalEpisodes)] episodes watched"),
                              ("", "")])
        var(f"Home_Plot_{c}", [("", f"$INFO[{C}.Plot]")])
        var(f"Home_Facts_{c}", [("", f"$INFO[{C}.Rating,Rating [COLOR ink],[/COLOR]   ]$INFO[{C}.Property(UnWatchedEpisodes),[COLOR ink],[/COLOR] to watch      ]$INFO[{C}.Status]")])
    C = "Container(9140).ListItem"
    d = dot("cobalt")
    var("Home_Title_9140", [("", f"$INFO[{C}.TVShowTitle]")])
    var("Home_Meta_9140", [("", f"Season $INFO[{C}.Season]{d}Episode $INFO[{C}.Episode]$INFO[{C}.Duration(mins),{d}, MIN]{d}$VAR[Date_H9140]")])
    var("Home_Tag_9140", [("", f"$INFO[{C}.Title]")])
    var("Home_Plot_9140", [("", f"$INFO[{C}.Plot]")])
    var("Home_Facts_9140", [("", f"$INFO[{C}.Rating,Rating [COLOR ink],[/COLOR]   ]$INFO[{C}.EndTime,Ends [COLOR ink],[/COLOR]   ]")])

    # Music: albums
    for c in (9150, 9160, 9161):
        C = f"Container({c}).ListItem"
        d = dot("mari_ink")
        var(f"Home_Title_{c}", [(f"!String.IsEmpty({C}.Album)", f"$INFO[{C}.Album]"), ("", f"$INFO[{C}.Label]")])
        var(f"Home_Meta_{c}", [("", f"$INFO[{C}.Artist,,{d}]$INFO[{C}.Year]$INFO[{C}.Genre,{d},]")])
        var(f"Home_Tag_{c}", [(f"!String.IsEmpty({C}.Property(Album_Label))", f"$INFO[{C}.Property(Album_Label)]"),
                              ("", f"$INFO[{C}.Property(Album_Type)]")])
        var(f"Home_Plot_{c}", [(f"!String.IsEmpty({C}.Property(Album_Description))", f"$INFO[{C}.Property(Album_Description)]"),
                               ("", f"$INFO[{C}.Property(Artist_Description)]")])
        var(f"Home_Facts_{c}", [(f"Integer.IsEqual({C}.PlayCount,1)", f"$INFO[{C}.Rating,Rating [COLOR ink],[/COLOR]   ]Played [COLOR ink]once[/COLOR]    $INFO[{C}.Property(Album_Mood)]"),
                                (f"Integer.IsGreater({C}.PlayCount,1)", f"$INFO[{C}.Rating,Rating [COLOR ink],[/COLOR]   ]Played [COLOR ink]$INFO[{C}.PlayCount][/COLOR] times    $INFO[{C}.Property(Album_Mood)]"),
                                ("", f"$INFO[{C}.Rating,Rating [COLOR ink],[/COLOR]   ]Not played yet      $INFO[{C}.Property(Album_Mood)]")])

    # System cards
    C = "Container(9180).ListItem"
    var("Home_Title_9180", [(f"!String.IsEmpty({C}.Property(Title))", f"$INFO[{C}.Property(Title)]"), ("", f"$INFO[{C}.Label]")])
    var("Home_Meta_9180", [("", f"$INFO[{C}.Label2]")])
    var("Home_Tag_9180", [("", f"$INFO[{C}.Property(Tag)]")])
    var("Home_Plot_9180", [("", f"$INFO[{C}.Property(Desc)]")])
    var("Home_Facts_9180", [("", "$INFO[System.BuildVersion,Kodi [COLOR ink],[/COLOR]   ]$INFO[System.FriendlyName,[COLOR ink],[/COLOR]   ]$INFO[System.Uptime,Up [COLOR ink],[/COLOR]]")])
    return "\n".join(v)


SYSTEM_ITEMS = [
    ("Settings", "Kodi", "ActivateWindow(Settings)", "Everything Kodi itself does: player, library, interface, network, system.", "The engine room", "icons/settings.png"),
    ("Skin", "Fold", "ActivateWindow(SkinSettings)", "Fold's own options: reduce motion, OSD auto-hide, clock, watched marks, info on Home.", "Fold's options", "icons/settings.png"),
    ("Add-ons", "Library", "ActivateWindow(AddonBrowser)", "Installed add-ons, updates and repositories. Video and music add-ons open from here too.", "What's installed", "icons/info.png"),
    ("Update|Update library", "Videos · music", "SetProperty(fold.libpanel,update,home)|ActivateWindow(1155)", "Look for new films, episodes and albums in your sources. Choose videos or music.", "Scan the sources", "icons/repeat.png"),
    ("Clean up|Clean library", "Videos · music", "SetProperty(fold.libpanel,clean,home)|ActivateWindow(1155)", "Remove entries whose files are gone. Choose videos or music; it asks before it cleans.", "Tidy up", "icons/chapters.png"),
    ("Favourites", "Shortcuts", "ActivateWindow(FavouritesBrowser)", "The items you marked as favourites from any menu.", "Pinned things", "icons/play.png"),
    ("Files", "Sources", "ActivateWindow(FileManager)", "Browse, copy and manage the sources on this Shield and the network.", "File manager", "icons/chapters.png"),
    # 0.9.12: the media browsers lived only in the System menu (1151), which nothing opens (Greptile, repo-skins #509)
    ("Live TV", "Media", "ActivateWindow(TVChannels)", "Channels, the guide and recordings from your TV add-on.", "Television", "icons/play.png", "System.HasPVRAddon"),
    ("$LOCALIZE[1]", "Media", "ActivateWindow(Pictures)", "Photos on your picture sources, as folders and slideshows.", "Photos", "icons/search.png"),
    ("Folders", "Sources", "ActivateWindow(Videos,sources://video/,return)", "Your video sources as plain folders, for files that are not in the library.", "Video folders", "icons/chapters.png"),
    ("System", "Info", "ActivateWindow(SystemInfo)", "Versions, storage, network, video and hardware details.", "System information", "icons/info.png"),
    ("Power", "Quit · Reboot", "ActivateWindow(ShutdownMenu)", "Quit Kodi, reboot, suspend or power down.", "Shut down menu", "icons/stop.png"),
]


def system_content():
    items = []
    for label, label2, click, desc, tag, icon, *vis in SYSTEM_ITEMS:
        label, _, title = label.partition("|")
        title_prop = f'\n\t\t\t\t\t\t<property name="Title">{title}</property>' if title else ""
        vis_tag = f"\n\t\t\t\t\t\t<visible>{vis[0]}</visible>" if vis else ""
        items.append(f"""					<item>
						<label>{label}</label>
						<label2>{label2}</label2>
						<icon>{icon}</icon>
						<property name="Desc">{desc}</property>
						<property name="Tag">{tag}</property>{title_prop}
{chr(10).join(f"						<onclick>{c}</onclick>" for c in click.split("|"))}{vis_tag}
					</item>""")
    return "<content>\n" + "\n".join(items) + "\n\t\t\t\t</content>"


# 0.9.10 main menu: tabs hidden in Skin settings (HideMenu.*); the tabs after a hidden one slide left by its pitch
# (206). A hidden tab keeps its numeric onleft / onright, so Left / Right fall through it. Settings never hides.
TAB_HIDE = {9001: "Skin.HasSetting(HideMenu.Movies)", 9002: "Skin.HasSetting(HideMenu.TVShows)",
            9003: "Skin.HasSetting(HideMenu.Music)", 9004: "Skin.HasSetting(HideMenu.Search)"}


def tab_hide(tid):
    o = []
    if tid in TAB_HIDE:
        o.append(f"\n\t\t\t\t<visible>!{TAB_HIDE[tid]}</visible>")
    for p in range(9001, tid):
        o.append(f'\n\t\t\t\t<animation effect="slide" start="0,0" end="-206,0" time="0" condition="{TAB_HIDE[p]}">Conditional</animation>')
    return "".join(o)


def tab(tid, x, color, label, section, count, onclick, ondown, left, right):
    focus_cond = f"Control.HasFocus({tid})"
    return f"""
			<control type="group">{tab_hide(tid)}
				<include content="Fold_TabLook">
					<param name="x" value="{x}"/>
					<param name="color" value="{color}"/>
					<param name="label" value="$LOCALIZE[{label}]"/>
					<param name="count" value="{count}"/>
					<param name="active" value="String.IsEqual(Window(Home).Property(fold.section),{section}){' | String.IsEmpty(Window(Home).Property(fold.section))' if section == 'films' else ''}"/>
					<param name="focus" value="{focus_cond}"/>
					<param name="text" value="{'ink' if color == 'mari' else 'on_card'}"/>
					<param name="text2" value="{'cap' if color == 'mari' else 'on_card2'}"/>
				</include>
				<control type="button" id="{tid}">
					<left>{x}</left>
					<top>0</top>
					<width>196</width>
					<height>98</height>
					<texturefocus />
					<texturenofocus />
					<label></label>
					<onfocus>SetProperty(fold.section,{section},home)</onfocus>
					<onclick>{onclick}</onclick>
					<ondown>{ondown}</ondown>
					<onleft>{left}</onleft>
					<onright>{right}</onright>
				</control>
			</control>"""


def postprocess(out):
    import re
    # selected items draw labels in <selectedcolor>: keep it equal to the textcolor everywhere
    out = re.sub(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)",
                 lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", out)
    # Series tab: Down = the in-progress row, or the latest-series row when there is none
    out = out.replace("<ondown>9130</ondown>", '<ondown condition="Integer.IsGreater(Container(9130).NumItems,0)">9130</ondown>\n\t\t\t\t\t<ondown>9131</ondown>', 1)
    return out


def build():
    films_from = "SetProperty(fold.from,h$INFO[Container(9110).Position],home)"
    counts = ["SetProperty(fold.n.films,$INFO[Container(9191).NumItems],home)",
              "SetProperty(fold.n.series,$INFO[Container(9193).NumItems],home)",
              "SetProperty(fold.n.music,$INFO[Container(9194).NumItems],home)"]
    x = []
    x.append(f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_home.py - edit the generator, not this file. -->
<!--{__doc__}-->
<includes>
	<!-- ============================================================== expressions -->
	<expression name="Home_Films">[String.IsEmpty(Window(Home).Property(fold.section)) | String.IsEqual(Window(Home).Property(fold.section),films)] + !Skin.HasSetting(HideMenu.Movies)</expression>
	<expression name="Home_Series">String.IsEqual(Window(Home).Property(fold.section),series) + !Skin.HasSetting(HideMenu.TVShows)</expression>
	<expression name="Home_Music">String.IsEqual(Window(Home).Property(fold.section),music) + !Skin.HasSetting(HideMenu.Music)</expression>
	<expression name="Home_Search">String.IsEqual(Window(Home).Property(fold.section),search) + !Skin.HasSetting(HideMenu.Search)</expression>
	<expression name="Home_Settings">String.IsEqual(Window(Home).Property(fold.section),settings)</expression>
	<expression name="Home_RowB">{ROWB_FOCUS['films']} | {ROWB_FOCUS['series']} | {ROWB_FOCUS['music']}</expression>

	<!-- ============================================================== variables -->
	<variable name="Home_RowColor">
		<value condition="String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season) | String.IsEqual(ListItem.DBType,episode)">cobalt</value>
		<value>verm</value>
	</variable>
	<variable name="Home_CardArt">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Home_CardFootR">
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Property(UnWatchedEpisodes),, left]</value>
		<value>$INFO[ListItem.Duration(mins),,′]</value>
	</variable>
	<variable name="Home_SquareFootR">
		<value>$INFO[ListItem.Rating]</value>
	</variable>
	<variable name="Home_CreamArt">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
		<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Home_CreamTitle">
		<value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
		<value>$INFO[ListItem.Title]</value>
	</variable>
	<!-- custom rows: add-on folders often have no title, only a label -->
	<variable name="Home_CustomTitle">
		<value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.TVShowTitle)">$INFO[ListItem.TVShowTitle]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="Home_RowHeadA">
		<value condition="$EXP[Home_Series] + Integer.IsGreater(Container(9130).NumItems,0)">In progress[COLOR cap2]   $INFO[Container(9130).NumItems] shows[/COLOR]</value>
		<value condition="$EXP[Home_Series]">Latest series[COLOR cap2]   newest added first[/COLOR]</value>
		<value condition="$EXP[Home_Music]">New albums[COLOR cap2]   newest added first[/COLOR]</value>
		<value condition="$EXP[Home_Settings]">System[COLOR cap2]   Kodi · Fold · add-ons[/COLOR]</value>
		<value condition="$EXP[Home_Search]">Search[COLOR cap2]   films · series · music · people[/COLOR]</value>
		<value condition="Integer.IsGreater(Container(9192).NumItems,0)">Unwatched[COLOR cap2]   $INFO[Container(9192).NumItems] films[/COLOR]</value>
		<value>Unwatched[COLOR cap2]   newest added first[/COLOR]</value>
	</variable>
	<variable name="Home_RowHeadB">
		<value condition="$EXP[Home_Series]">New episodes[COLOR cap2]   unwatched, newest first[/COLOR]</value>
		<value condition="$EXP[Home_Music] + Integer.IsGreater(Container(9160).NumItems,0)">Recently played[COLOR cap2]   albums[/COLOR]</value>
		<value condition="$EXP[Home_Music]">Albums to try[COLOR cap2]   a random handful[/COLOR]</value>
		<value condition="Integer.IsEqual(Container(9120).NumItems,1)">Continue watching[COLOR cap2]   1 in progress[/COLOR]</value>
		<value condition="Integer.IsGreater(Container(9120).NumItems,0)">Continue watching[COLOR cap2]   $INFO[Container(9120).NumItems] in progress[/COLOR]</value>
		<value>Recently added[COLOR cap2]   films[/COLOR]</value>
	</variable>
{variables()}

	<!-- ============================================================== the tabs (focusable) -->
	<include name="Home_Tabs">
		<control type="group" id="9000">{tab(9001, 96, 'verm', 31200, 'films', '$INFO[Container(9191).NumItems]', 'ActivateWindow(Videos,videodb://movies/titles/,return)', 9110, 9005, 9002)}{tab(9002, 302, 'cobalt', 31201, 'series', '$INFO[Container(9193).NumItems]', 'ActivateWindow(Videos,videodb://tvshows/titles/,return)', 9130, 9001, 9003)}{tab(9003, 508, 'mari', 31202, 'music', '$INFO[Container(9194).NumItems]', 'ActivateWindow(Music,musicdb://albums/,return)', 9150, 9002, 9004)}{tab(9004, 714, 'jade', 31203, 'search', '', 'ActivateWindow(1150)', 9170, 9003, 9005)}{tab(9005, 920, 'graph', 31204, 'settings', '', 'SetFocus(9180)', 9180, 9004, 9001)}
		</control>
	</include>

	<!-- ============================================================== counters (hidden, after a rest) -->
	<include name="Home_Counters">
		<control type="group">
			<left>-200</left>
			<top>-200</top>
{''.join(f'''			<control type="list" id="{cid}">
				<left>0</left>
				<top>0</top>
				<width>1</width>
				<height>1</height>
				<visible>System.IdleTime(1) | Integer.IsGreater(Container({cid}).NumItems,0)</visible>
				<itemlayout width="1" height="1"/>
				<focusedlayout width="1" height="1"/>
				<content target="{tgt}">{path}</content>
			</control>
''' for cid, tgt, path in ((9191, 'videos', 'videodb://movies/titles/'), (9192, 'videos', 'special://skin/playlists/fold_unwatched_movies.xsp'), (9193, 'videos', 'videodb://tvshows/titles/'), (9194, 'music', 'musicdb://albums/')))}		</control>
	</include>

	<!-- ============================================================== section content
	     One sliding page: the row head, row A and the info block slide up {SLIDE_B} px while row B has focus
	     (row A folds away), so the second row is fully on screen. -->
	<include name="Home_Content">
		<control type="group">
			<animation type="Conditional" condition="$EXP[Home_RowB] + !{RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{SLIDE_B}" time="320" tween="cubic" easing="out"/>
			</animation>
			<animation type="Conditional" condition="$EXP[Home_RowB] + {RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{SLIDE_B}" time="0"/>
			</animation>
			<!-- 0.9.10 custom rows: {SLIDE_B} + {C_ROW_PITCH} px to the first one, {C_ROW_PITCH} more per row with items above the focused one -->
			<animation type="Conditional" condition="$EXP[CustomRowsFocus] + !{RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{SLIDE_B + C_ROW_PITCH}" time="320" tween="cubic" easing="out"/>
			</animation>
			<animation type="Conditional" condition="$EXP[CustomRowsFocus] + {RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{SLIDE_B + C_ROW_PITCH}" time="0"/>
			</animation>
			<animation type="Conditional" condition="[Control.HasFocus(9882) | Control.HasFocus(9883)] + $EXP[CustomRow1On] + !{RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{C_ROW_PITCH}" time="280" tween="cubic" easing="out"/>
			</animation>
			<animation type="Conditional" condition="[Control.HasFocus(9882) | Control.HasFocus(9883)] + $EXP[CustomRow1On] + {RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{C_ROW_PITCH}" time="0"/>
			</animation>
			<animation type="Conditional" condition="Control.HasFocus(9883) + $EXP[CustomRow2On] + !{RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{C_ROW_PITCH}" time="280" tween="cubic" easing="out"/>
			</animation>
			<animation type="Conditional" condition="Control.HasFocus(9883) + $EXP[CustomRow2On] + {RM}" reversible="true">
				<effect type="slide" start="0,0" end="0,-{C_ROW_PITCH}" time="0"/>
			</animation>
			<!-- row A head -->
			<control type="label">
				<left>96</left>
				<top>116</top>
				<width>1300</width>
				<height>32</height>
				<font>caps_20_b</font>
				<textcolor>$VAR[FoldAccentInk]</textcolor>
				<label>$VAR[Home_RowHeadA]</label>
				<animation effect="fade" start="100" end="0" time="200" condition="$EXP[Home_RowB] | $EXP[CustomRowsFocus]">Conditional</animation>
			</control>
			<!-- row A: folds down onto the table while row B (or a custom row) has focus; stands up when a section opens -->
			<control type="group">
				<animation type="Conditional" condition="[$EXP[Home_RowB] | $EXP[CustomRowsFocus]] + !{RM}" reversible="true">
					<effect type="rotatex" start="0" end="70" center="{LIST_Y + F_TOP + F_H}" time="300" tween="cubic" easing="in"/>
					<effect type="fade" start="100" end="0" time="300" tween="cubic" easing="in"/>
				</animation>
				<animation type="Conditional" condition="[$EXP[Home_RowB] | $EXP[CustomRowsFocus]] + {RM}" reversible="true">
					<effect type="fade" start="100" end="0" time="0"/>
				</animation>
				<!-- films -->
				<control type="group">
					<visible>$EXP[Home_Films]</visible>
					<include>Home_SectionUnfold</include>{row_a(9110, 'poster', 'special://skin/playlists/fold_unwatched_movies.xsp', 9001, 'SetFocus(9120)' , [films_from] + counts + ['Action(Info)'], sort=('dateadded', 'descending'), limit='25').replace('<ondown>SetFocus(9120)</ondown>', '<ondown condition="Integer.IsGreater(Container(9120).NumItems,0)">9120</ondown>\n\t\t\t\t<ondown condition="!Integer.IsGreater(Container(9120).NumItems,0)">9121</ondown>')}
				</control>
				<!-- series -->
				<control type="group">
					<visible>$EXP[Home_Series]</visible>
					<include>Home_SectionUnfold</include>{row_a(9130, 'poster', 'special://skin/playlists/fold_inprogress_tvshows.xsp', 9002, 9140, counts + ['ActivateWindow(Videos,$INFO[ListItem.FolderPath],return)'], sort=('lastplayed', 'descending'))}{row_a(9131, 'poster', 'videodb://tvshows/titles/', 9002, 9140, counts + ['ActivateWindow(Videos,$INFO[ListItem.FolderPath],return)'], extra_visible='!Integer.IsGreater(Container(9130).NumItems,0)', sort=('dateadded', 'descending'), limit='25')}
				</control>
				<!-- music -->
				<control type="group">
					<visible>$EXP[Home_Music]</visible>
					<include>Home_SectionUnfold</include>{row_a(9150, 'square', 'musicdb://recentlyaddedalbums/', 9003, 'SetFocus(9160)', ['SetProperty(fold.from,m$INFO[Container(9150).Position],home)'] + counts + ['Action(Info)']).replace('<ondown>SetFocus(9160)</ondown>', '<ondown condition="Integer.IsGreater(Container(9160).NumItems,0)">9160</ondown>\n\t\t\t\t<ondown condition="!Integer.IsGreater(Container(9160).NumItems,0)">9161</ondown>')}
				</control>
				<!-- settings -->
				<control type="group">
					<visible>$EXP[Home_Settings]</visible>
					<include>Home_SectionUnfold</include>{row_a(9180, 'system', system_content(), 9005, 9005, [], focuspos=2).replace('<ondown>9005</ondown>', DOWN_TO_CUSTOM.strip() + chr(10) + chr(9) * 4 + '<ondown>9005</ondown>', 1)}
				</control>
				<!-- search: one jade card -->
				<control type="group">
					<visible>$EXP[Home_Search]</visible>
					<include>Home_SectionUnfold</include>
					<include>Home_SearchCard</include>
				</control>
			</control>
			<!-- info blocks (each bound to its container) -->
			<control type="group">
				<animation effect="fade" start="0" end="100" time="160" delay="80">Visible</animation>
{''.join(info_block(c, 9310 + i, s, rb, k) for i, (c, s, rb, k) in enumerate((
    (9110, 'films', False, 'film'), (9120, 'films', True, 'film'), (9121, 'films', True, 'film'),
    (9130, 'series', False, 'show'), (9131, 'series', False, 'show'), (9140, 'series', True, 'episode'),
    (9150, 'music', False, 'album'), (9160, 'music', True, 'album'), (9161, 'music', True, 'album'),
    (9180, 'settings', False, 'system'))))}
			</control>
			<!-- row B -->
			<control type="group">
				<visible>$EXP[Home_Films] | $EXP[Home_Series] | $EXP[Home_Music]</visible>
				<!-- 0.9.10: fades once the page has slid past it (a second custom row has focus), so it never runs under the tabs -->
				<animation effect="fade" start="100" end="0" time="200" condition="[[Control.HasFocus(9882) | Control.HasFocus(9883)] + $EXP[CustomRow1On]] | [Control.HasFocus(9883) + $EXP[CustomRow2On]]">Conditional</animation>
				<control type="label">
					<left>96</left>
					<top>{B_Y}</top>
					<width>1300</width>
					<height>32</height>
					<font>caps_20_b</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Home_RowHeadB]</label>
				</control>
				<control type="group">
					<visible>$EXP[Home_Films]</visible>{row_b(9120, 'video', '<content target="videos" sortby="lastplayed" sortorder="descending" browse="never">special://skin/playlists/fold_inprogress_movies.xsp</content>', 9110, ['SetProperty(fold.from,b$INFO[Container(9120).Position],home)'] + counts + ['Action(Info)'])}{row_b(9121, 'video', '<content target="videos" browse="never">videodb://recentlyaddedmovies/</content>', 9110, ['SetProperty(fold.from,b$INFO[Container(9121).Position],home)'] + counts + ['Action(Info)'], visible='!Integer.IsGreater(Container(9120).NumItems,0)')}
				</control>
				<control type="group">
					<visible>$EXP[Home_Series]</visible>{row_b(9140, 'video', '<content target="videos" sortby="dateadded" sortorder="descending" limit="25" browse="never">special://skin/playlists/fold_new_episodes.xsp</content>', 'SetFocus(9130)', ['SetProperty(fold.from,b$INFO[Container(9140).Position],home)'] + counts + ['Action(Info)']).replace('<onup>SetFocus(9130)</onup>', '<onup condition="Integer.IsGreater(Container(9130).NumItems,0)">9130</onup>\n\t\t\t\t<onup condition="!Integer.IsGreater(Container(9130).NumItems,0)">9131</onup>').replace('<onback>SetFocus(9130)</onback>', '<onback>9002</onback>')}
				</control>
				<control type="group">
					<visible>$EXP[Home_Music]</visible>{row_b(9160, 'album', '<content target="music" browse="never">musicdb://recentlyplayedalbums/</content>', 9150, ['SetProperty(fold.from,c$INFO[Container(9160).Position],home)'] + counts + ['Action(Info)'])}{row_b(9161, 'album', '<content target="music" sortby="random" limit="20" browse="never">musicdb://albums/</content>', 9150, ['SetProperty(fold.from,c$INFO[Container(9161).Position],home)'] + counts + ['Action(Info)'], visible='!Integer.IsGreater(Container(9160).NumItems,0)')}
				</control>
			</control>{custom_rows()}
		</control>
	</include>

	<!-- A section's cards stand up from the table when its tab is chosen (pop-up book). -->
	<include name="Home_SectionUnfold">
		<animation type="Visible" condition="!{RM}">
			<effect type="rotatex" start="80" end="0" center="{LIST_Y + F_TOP + F_H}" time="320" tween="cubic" easing="out"/>
			<effect type="fade" start="0" end="100" time="160"/>
		</animation>
		<animation type="Visible" condition="{RM}">
			<effect type="fade" start="0" end="100" time="120"/>
		</animation>
	</include>

	<!-- Search section: one jade folded card. OK opens the search page. -->
	<include name="Home_SearchCard">
		<control type="group">
			<left>96</left>
			<top>{LIST_Y + F_TOP}</top>
			<control type="image">
				<left>-96</left>
				<top>-96</top>
				<width>{900 + 192}</width>
				<height>{F_H + 192}</height>
				<texture border="104">fold/shadow_lift.png</texture>
				<visible>Control.HasFocus(9170)</visible>
			</control>
			<control type="image">
				<left>-48</left>
				<top>-48</top>
				<width>{900 + 96}</width>
				<height>{F_H + 96}</height>
				<texture border="56">fold/shadow_card.png</texture>
				<visible>!Control.HasFocus(9170)</visible>
			</control>
			<control type="group">
				<camera x="450" y="{CAM_Y - F_TOP}"/>
				<animation type="Focus" condition="!{RM}">
					<effect type="rotatex" start="0" end="-6" center="{F_H}" time="180" tween="sine" easing="out"/>
				</animation>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>900</width>
					<height>{F_H}</height>
					<texture border="6" colordiffuse="jade">fold/rr4.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>900</width>
					<height>{F_H}</height>
					<texture diffuse="fold/rr4.png">fold/tooth_card.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>900</width>
					<height>{F_H}</height>
					<texture>fold/card_sheen.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>900</width>
					<height>{F_H}</height>
					<texture border="6">fold/card_rim.png</texture>
				</control>
				<control type="image">
					<left>9</left>
					<top>0</top>
					<width>2</width>
					<height>{F_H}</height>
					<texture>fold/score.png</texture>
				</control>
				<control type="label">
					<left>56</left>
					<top>48</top>
					<width>800</width>
					<height>120</height>
					<font>disp_112</font>
					<textcolor>on_card</textcolor>
					<label>$LOCALIZE[31203]</label>
				</control>
				<control type="label">
					<left>60</left>
					<top>178</top>
					<width>800</width>
					<height>40</height>
					<font>light_34</font>
					<textcolor>on_card</textcolor>
					<label>Films, series, albums, artists and people.</label>
				</control>
				<!-- a cream slip like a typed query -->
				<control type="image">
					<left>56</left>
					<top>256</top>
					<width>788</width>
					<height>72</height>
					<texture border="6" colordiffuse="cream">fold/rr3.png</texture>
				</control>
				<control type="label">
					<left>80</left>
					<top>256</top>
					<width>740</width>
					<height>72</height>
					<font>caps_22</font>
					<textcolor>cap</textcolor>
					<label>Press OK and start typing</label>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>900</width>
					<height>{F_H}</height>
					<texture>fold/card_light.png</texture>
					<visible>Control.HasFocus(9170)</visible>
				</control>
			</control>
			<control type="button" id="9170">
				<left>0</left>
				<top>0</top>
				<width>900</width>
				<height>{F_H}</height>
				<texturefocus />
				<texturenofocus />
				<label></label>
				<onclick>ActivateWindow(1150)</onclick>
				<onup>9004</onup>{DOWN_TO_CUSTOM}
				<onback>9004</onback>
			</control>
		</control>
	</include>

	<!-- Now playing slip under the clock -->
	<include name="Home_NowPlaying">
		<control type="label">
			<left>1124</left>
			<top>110</top>
			<width>700</width>
			<height>32</height>
			<align>right</align>
			<font>caps_20_b</font>
			<textcolor>$VAR[FoldAccentInk]</textcolor>
			<label>$VAR[Home_NowPlayingLabel]</label>
			<visible>Player.HasMedia</visible>
		</control>
	</include>
	<variable name="Home_NowPlayingLabel">
		<value condition="Player.Paused">Paused[COLOR cap2]   $VAR[Dlg_PlayTitle][/COLOR]</value>
		<value condition="Player.HasAudio">Playing[COLOR cap2]   $INFO[MusicPlayer.Artist,, · ]$INFO[MusicPlayer.Title][/COLOR]</value>
		<value>Playing[COLOR cap2]   $VAR[Dlg_PlayTitle][/COLOR]</value>
	</variable>
</includes>
""")
    out = postprocess("".join(x))
    OUT.write_text(finish_xml(out), encoding="utf-8", newline="\n")
    print("Includes_Home.xml written")


if __name__ == "__main__":
    build()
