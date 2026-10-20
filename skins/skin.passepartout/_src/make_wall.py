"""Generate 1080i/Includes_Wall.xml: view 506 "The wall" (request docs/requests/poster-wall, boards
Passepartout{Default,Small,LargeOverlay}.html, values from make_boards.py / FEASIBILITY.md).

One vertical panel 1920x1080 at 0,0. Six itemlayout/focusedlayout pairs (size x paper), picked by
`condition` on the skin settings (re-laid out when the window opens again):
  size   ten / eight (default) / six   -> columns 10 / 8 / 6, cell width 1920 / columns
  paper  shown (default): paper between the prints (28 / 40 / 48), every print keeps its bevel, rows keep 2:3
         (row pitch = print height + gap); hidden (passepartout.wall.butted): a contact wall, no bevels
Panel rows = int(1080 / pitch): only full rows take focus, the partial row below is drawn and clipped.

The chosen print (focused layout, drawn last) zooms 112 % (Large 110 %) with its lift shadow and bevel;
with the mat on (default) it gets a card-paper mat (18 / 24 / 28) first. The watched dot sits in the gutter
under unfocused prints (paper shown) and on the chosen print's mat.

The wall label (passepartout.wall.label = 1 / 2 seconds) is a paper card drawn INSIDE the focused layout, under
the print, so the zoomed mat and its shadow lie on top of it: it covers Small 4 / Medium 3 / Large 2 cells of
the same row, on the right, or on the left when the print is in the last `span` columns (Container(506).Column).

Usage: python skins/skin.passepartout/_src/make_wall.py
"""
from math import floor
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Includes_Wall.xml"

COLS = {"small": 10, "medium": 8, "large": 6}
GAP = {"small": 28, "medium": 40, "large": 48}
MAT = {"small": 18, "medium": 24, "large": 28}
ZOOM = {"small": 112, "medium": 112, "large": 110}
SPAN = {"small": 4, "medium": 3, "large": 2}

S_SIZE = "Skin.String(passepartout.wall.size)"
COND_SIZE = {
    "small": f"String.IsEqual({S_SIZE},ten)",
    "large": f"String.IsEqual({S_SIZE},six)",
    "medium": f"!String.IsEqual({S_SIZE},ten) + !String.IsEqual({S_SIZE},six)",
}
BUTTED = "Skin.HasSetting(passepartout.wall.butted)"
MAT_ON = "!Skin.HasSetting(passepartout.wall.nomat)"
MAT_OFF = "Skin.HasSetting(passepartout.wall.nomat)"
S_LABEL = "Skin.String(passepartout.wall.label)"
LABEL_ON = (f"[[String.IsEqual({S_LABEL},1) + System.IdleTime(1)] | [String.IsEqual({S_LABEL},2) + System.IdleTime(2)]]"
            " + Control.HasFocus(506) + !Container(506).Scrolling + !ListItem.IsParentFolder")

# wall label text block per (size, butted): pad, title top, cap1, cap2, rule (None), plot top, plot lines, status top
CARD = {
    ("large", False): dict(pad=44, title=38, cap1=114, cap2=144, rule=194, plot=216, lines=3),
    ("large", True): dict(pad=44, title=38, cap1=114, cap2=144, rule=194, plot=216, lines=4),
    ("medium", False): dict(pad=40, title=32, cap1=108, cap2=138, rule=188, plot=None, lines=0),
    ("medium", True): dict(pad=40, title=32, cap1=108, cap2=138, rule=188, plot=208, lines=2),
    ("small", False): dict(pad=32, title=26, cap1=100, cap2=130, rule=None, plot=None, lines=0),
    ("small", True): dict(pad=36, title=30, cap1=106, cap2=136, rule=186, plot=None, lines=0),
}
STATUS_BOTTOM = {"large": 36, "medium": 34, "small": 30}


def geo(size, butted):
    cols = COLS[size]
    cw = 1920 // cols
    g = 0 if butted else GAP[size]
    w = cw - g
    h = w * 3 // 2
    return cols, cw, g, w, h, h + g


def card_box(size, butted, mat):
    """(left of the right-hand card, left of the left-hand card, width), relative to the cell origin."""
    cols, cw, g, w, h, ch = geo(size, butted)
    span = SPAN[size]
    if not butted:      # on the covered prints' own edges (the boards)
        return cw + g // 2, -span * cw + g // 2, span * cw - g
    mw = MAT[size] if mat else 0
    ext = mw + (ZOOM[size] - 100) / 200 * (w + 2 * mw)   # how far the zoomed print / mat reaches into the next cell
    tuck = floor(ext) - 2                                  # the card starts 2 px under it: no sliver of the neighbour
    return cw + tuck, -span * cw, span * cw - tuck


def card_xml(size, butted, mat, side, probe):
    cols, cw, g, w, h, ch = geo(size, butted)
    span = SPAN[size]
    rl, ll, cwid = card_box(size, butted, mat)
    left = rl if side == "right" else ll
    left_cols = " | ".join(f"Container(506).Column({c})" for c in range(cols - span, cols))
    side_cond = f"![{left_cols}]" if side == "right" else f"[{left_cols}]"
    mat_cond = ""
    if butted:
        mat_cond = " + " + (MAT_ON if mat else MAT_OFF)
    c = CARD[(size, butted)]
    # paper between the prints: the card also covers the covered prints' bevels (picture + 5), so grow it by 5;
    # the text keeps its place (every inner position + e)
    e = 0 if butted else 5
    pad, tw = c["pad"] + e, cwid - 2 * c["pad"]
    shadow_bottom = max(104, 370 - 16 - h - 2 * e)    # pp/card.png 9-slice minimum is 296 x 370
    status_top = e + h - STATUS_BOTTOM[size] - 34
    c = {k: (v + e if isinstance(v, int) and k not in ("pad", "lines") else v) for k, v in c.items()}
    # a genre line too long for one line (probe {probe + 20}) wraps to two lines and pushes the rule and the
    # curator text down one caps line (the plot gives up a line). Small has no room: its line rolls instead.
    can_wrap = size != "small"
    wrapped = f"Integer.IsGreater(Container({probe + 20}).NumPages,1)"
    states = [("!" + wrapped, 0, 0), (wrapped, 28, 1)] if can_wrap else [("true", 0, 0)]
    rule = plot = ""
    for cond, dy, dl in states:
        if c["rule"] is not None:
            rule += f'''
					<control type="image">
						<left>{pad}</left>
						<top>{c["rule"] + dy}</top>
						<width>64</width>
						<height>1</height>
						<texture colordiffuse="ink">common/white.png</texture>
						<visible>{cond}</visible>
					</control>'''
        if c["plot"] is not None and c["lines"] - dl > 0:
            plot += f'''
					<control type="textbox">
						<left>{pad}</left>
						<top>{c["plot"] + dy}</top>
						<width>{tw}</width>
						<height>{(c["lines"] - dl) * 36 + 6}</height>
						<font>body_24_loose</font>
						<textcolor>body</textcolor>
						<label>$INFO[ListItem.Plot]</label>
						<visible>{cond}</visible>
					</control>'''
    cap2_vis = f"\n\t\t\t\t\t\t<visible>!{wrapped}</visible>" if can_wrap else ""
    cap2_wrap = ""
    if can_wrap:
        cap2_wrap = f'''
					<control type="textbox">
						<left>{pad}</left>
						<top>{c["cap2"]}</top>
						<width>{tw}</width>
						<height>60</height>
						<font>cap_20</font>
						<textcolor>ink2</textcolor>
						<label>$VAR[Wall_Line2]</label>
						<visible>{wrapped}</visible>
					</control>'''
    return f'''				<!-- wall label, {side} -->
				<control type="group">
					<left>{left - e}</left>
					<top>{g // 2 - e}</top>
					<width>{cwid + 2 * e}</width>
					<height>{h + 2 * e}</height>
					<visible>{LABEL_ON} + {side_cond}{mat_cond}</visible>
					<animation effect="fade" start="0" end="100" time="200">Visible</animation>
					<control type="image">
						<left>-48</left>
						<top>-16</top>
						<right>-48</right>
						<bottom>-{shadow_bottom}</bottom>
						<texture border="148,146,148,224" colordiffuse="$VAR[ShadowColor]">pp/card.png</texture>
					</control>
					<control type="image">
						<left>-1</left>
						<top>-1</top>
						<right>-1</right>
						<bottom>-1</bottom>
						<texture colordiffuse="rule_card">common/white.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<right>0</right>
						<bottom>0</bottom>
						<texture colordiffuse="$VAR[PaperColor]">common/white.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<right>0</right>
						<bottom>0</bottom>
						<texture colordiffuse="card_lift">common/white.png</texture>
					</control>
					<!-- title: Geist Light 56 when it fits on one line (probe {probe}), else 40, rolling if still too long -->
					<control type="label">
						<left>{pad}</left>
						<top>{c["title"]}</top>
						<width>{tw}</width>
						<height>66</height>
						<font>ttl_56</font>
						<textcolor>ink</textcolor>
						<aligny>center</aligny>
						<label>$INFO[ListItem.Label]</label>
						<visible>!Integer.IsGreater(Container({probe}).NumPages,1)</visible>
					</control>
					<control type="label">
						<left>{pad}</left>
						<top>{c["title"]}</top>
						<width>{tw}</width>
						<height>66</height>
						<font>ttl_40</font>
						<textcolor>ink</textcolor>
						<aligny>center</aligny>
						<scroll>true</scroll>
						<label>$INFO[ListItem.Label]</label>
						<visible>Integer.IsGreater(Container({probe}).NumPages,1)</visible>
					</control>
					<control type="label">
						<left>{pad}</left>
						<top>{c["cap1"]}</top>
						<width>{tw}</width>
						<height>28</height>
						<font>cap_20</font>
						<textcolor>ink</textcolor>
						<scroll>true</scroll>
						<label>$VAR[Wall_Line1]</label>
					</control>
					<control type="label">
						<left>{pad}</left>
						<top>{c["cap2"]}</top>
						<width>{tw}</width>
						<height>28</height>
						<font>cap_20</font>
						<textcolor>ink2</textcolor>
						<scroll>true</scroll>
						<label>$VAR[Wall_Line2]</label>{cap2_vis}
					</control>{cap2_wrap}{rule}{plot}
					<control type="label">
						<left>{pad}</left>
						<top>{status_top}</top>
						<width>{tw}</width>
						<height>34</height>
						<font>body_24</font>
						<textcolor>ink2</textcolor>
						<scroll>true</scroll>
						<label>$VAR[Wall_Status]</label>
					</control>
				</control>'''


def print_group(size, butted, focused, probe_ids):
    cols, cw, g, w, h, ch = geo(size, butted)
    ox = g // 2
    mw = MAT[size]
    z = ZOOM[size]
    small = size == "small"
    lift_tex, lift_border, lo = (("pp/lift_xs.png", "64,48,64,76", (24, 12, 24, 40)) if small
                                 else ("pp/lift_s.png", "124,134,124,196", (48, 18, 48, 100)))
    parts = []
    if focused:
        for side in ("right", "left"):
            if butted:
                for mat in (True, False):
                    parts.append(card_xml(size, butted, mat, side, probe_ids[(size, butted, mat)]))
            else:
                parts.append(card_xml(size, butted, True, side, probe_ids[(size, butted, True)]))
    inner = []
    if focused:
        inner.append(f'''					<animation type="Focus" reversible="false">
						<effect type="zoom" start="100" end="{z}" center="{cw // 2},{ch // 2}" time="380" tween="cubic" easing="out"/>
					</animation>
					<animation type="Unfocus">
						<effect type="zoom" start="{z}" end="100" center="{cw // 2},{ch // 2}" time="160"/>
					</animation>''')
        for mat, cond in ((True, MAT_ON), (False, MAT_OFF)):
            m = mw if mat else 0
            inner.append(f'''					<control type="image">
						<left>-{m + lo[0]}</left>
						<top>-{m + lo[1]}</top>
						<right>-{m + lo[2]}</right>
						<bottom>-{m + lo[3]}</bottom>
						<texture border="{lift_border}" colordiffuse="$VAR[ShadowColor]">{lift_tex}</texture>
						<visible>{cond} + Control.HasFocus(506) + !Skin.HasSetting(passepartout.noshadow)</visible>
						<animation type="Focus" reversible="false">
							<effect type="fade" start="0" end="100" time="420" delay="120"/>
						</animation>
					</control>''')
        inner.append(f'''					<!-- the mat: card paper (paper + 40 % white) with a 7 % ink edge -->
					<control type="group">
						<visible>{MAT_ON}</visible>
						<control type="image">
							<left>-{mw + 1}</left>
							<top>-{mw + 1}</top>
							<right>-{mw + 1}</right>
							<bottom>-{mw + 1}</bottom>
							<texture colordiffuse="rule_mat">common/white.png</texture>
						</control>
						<control type="image">
							<left>-{mw}</left>
							<top>-{mw}</top>
							<right>-{mw}</right>
							<bottom>-{mw}</bottom>
							<texture colordiffuse="$VAR[PaperColor]">common/white.png</texture>
						</control>
						<control type="image">
							<left>-{mw}</left>
							<top>-{mw}</top>
							<right>-{mw}</right>
							<bottom>-{mw}</bottom>
							<texture colordiffuse="card_lift">common/white.png</texture>
						</control>
					</control>''')
    bevel = "true" if (focused or not butted) else "false"
    font = "body_22" if size != "small" else "body_20"
    inner.append(f'''					<include content="Wall_PrintBody">
						<param name="bevel" value="{bevel}"/>
						<param name="font" value="{font}"/>
					</include>''')
    if focused:
        inner.append(f'''					<control type="image">
						<right>-{mw - mw // 2 + 1}</right>
						<bottom>-{mw - mw // 2 + 5}</bottom>
						<width>10</width>
						<height>10</height>
						<texture colordiffuse="ink">pp/dot.png</texture>
						<visible>{MAT_ON} + $EXP[ShowWatchedMarkers] + $EXP[ListItemWatched] + !ListItem.IsParentFolder</visible>
					</control>''')
    elif not butted:
        inner.append(f'''					<control type="image">
						<right>-2</right>
						<bottom>-{ox + 5}</bottom>
						<width>10</width>
						<height>10</height>
						<texture colordiffuse="ink">pp/dot.png</texture>
						<visible>$EXP[ShowWatchedMarkers] + $EXP[ListItemWatched] + !ListItem.IsParentFolder</visible>
					</control>''')
    parts.append(f'''				<control type="group">
					<left>{ox}</left>
					<top>{ox}</top>
					<width>{w}</width>
					<height>{h}</height>
{chr(10).join(inner)}
				</control>''')
    return "\n".join(parts)


def main():
    probe_ids, probes = {}, []
    pid = 9601
    for size in ("small", "medium", "large"):
        for butted in (False, True):
            for mat in ((True, False) if butted else (True,)):
                probe_ids[(size, butted, mat)] = pid
                c = CARD[(size, butted)]
                tw = card_box(size, butted, mat)[2] - 2 * c["pad"]
                cond = COND_SIZE[size] + (" + " + BUTTED if butted else " + !" + BUTTED)
                if butted:
                    cond += " + " + (MAT_ON if mat else MAT_OFF)
                probes.append(f'''		<control type="textbox" id="{pid}">
			<left>0</left>
			<top>0</top>
			<width>{tw}</width>
			<height>99</height>
			<font>ttl_56</font>
			<textcolor>clear</textcolor>
			<label>$INFO[Container(506).ListItem.Label]</label>
			<visible>{cond}</visible>
		</control>
		<control type="textbox" id="{pid + 20}">
			<left>0</left>
			<top>0</top>
			<width>{tw}</width>
			<height>42</height>
			<font>cap_20</font>
			<textcolor>clear</textcolor>
			<label>$VAR[Wall_Line2]</label>
			<visible>{cond}</visible>
		</control>''')
                pid += 1
    layouts = []
    for size in ("small", "medium", "large"):
        for butted in (False, True):
            cols, cw, g, w, h, ch = geo(size, butted)
            assert cols * cw == 1920 and w * 3 == h * 2
            cond = COND_SIZE[size] + (" + " + BUTTED if butted else " + !" + BUTTED)
            note = (f"<!-- {size}, {'contact wall' if butted else 'paper between'}: {cols} across, print {w}x{h}, "
                    f"pitch {cw}x{ch}, {1080 // ch} full rows + {1080 - (1080 // ch) * ch} px -->")
            layouts.append(f'''			{note}
			<itemlayout width="{cw}" height="{ch}" condition="{cond}">
{print_group(size, butted, False, probe_ids)}
			</itemlayout>
			<focusedlayout width="{cw}" height="{ch}" condition="{cond}">
{print_group(size, butted, True, probe_ids)}
			</focusedlayout>''')
    band = '''			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>140</height>
				<texture colordiffuse="paper">common/white.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>140</height>
				<texture colordiffuse="$VAR[PaperColor]">common/white.png</texture>
				<visible>$EXP[PP_HasArtPaper]</visible>
			</control>'''
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_wall.py - edit the generator, not this file.
	View 506 "The wall": a full-screen wall of 2:3 prints (docs/requests/poster-wall). Settings in
	Skin settings > Libraries > The wall (passepartout.wall.size / .butted / .nomat / .label). -->
<includes>
	<variable name="Wall_Line1">
		<value condition="ListItem.IsParentFolder">Up one level</value>
		<value condition="String.IsEqual(ListItem.DBType,movie) + !String.IsEmpty(ListItem.Director)">$INFO[ListItem.Director]$INFO[ListItem.Year,$COMMA ,]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow) + !String.IsEmpty(ListItem.Studio)">$INFO[ListItem.Studio]$INFO[ListItem.Year,$COMMA ,]</value>
		<value condition="String.IsEqual(ListItem.DBType,season) + !String.IsEmpty(ListItem.TVShowTitle)">$INFO[ListItem.TVShowTitle]$INFO[ListItem.Year,$COMMA ,]</value>
		<value condition="String.IsEqual(ListItem.DBType,set)">Collection</value>
		<value condition="String.IsEqual(ListItem.DBType,musicvideo)">$INFO[ListItem.Artist]$INFO[ListItem.Year,$COMMA ,]</value>
		<value>$INFO[ListItem.Year]</value>
	</variable>
	<variable name="Wall_Line2">
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Total),, films]</value>
		<value condition="String.IsEqual(ListItem.DBType,movie) + !String.IsEmpty(ListItem.Genre)">$INFO[ListItem.Genre]$INFO[ListItem.Duration(mins),$COMMA , min]</value>
		<value condition="String.IsEqual(ListItem.DBType,movie)">$INFO[ListItem.Duration(mins),, min]</value>
		<value>$INFO[ListItem.Genre]</value>
	</variable>
	<variable name="Wall_ToGo">
		<value condition="Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)"> · all seen</value>
		<value condition="!String.IsEmpty(ListItem.Property(UnWatchedEpisodes))"> · [COLOR ink]$INFO[ListItem.Property(UnWatchedEpisodes)][/COLOR] to go</value>
	</variable>
	<variable name="Wall_Status">
		<value condition="String.IsEqual(ListItem.DBType,set)">$INFO[ListItem.Property(Watched),, of ]$INFO[ListItem.Property(Total),, seen]</value>
		<value condition="String.IsEqual(ListItem.DBType,tvshow)">$VAR[PP_SeasonsN_L] · $VAR[PP_EpisodesN_L]$VAR[Wall_ToGo]</value>
		<value condition="String.IsEqual(ListItem.DBType,season)">$VAR[PP_EpisodesN_L]$VAR[Wall_ToGo]</value>
		<value condition="ListItem.IsResumable">In progress, $INFO[ListItem.PercentPlayed]% · ends [COLOR ink]$INFO[ListItem.EndTime(Resume)][/COLOR]</value>
		<value condition="Integer.IsGreater(ListItem.PlayCount,0)">Watched · ends [COLOR ink]$INFO[ListItem.EndTime][/COLOR]</value>
		<value condition="String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,episode)">Unwatched · ends [COLOR ink]$INFO[ListItem.EndTime][/COLOR]</value>
	</variable>

	<!-- picture (+ bevel), or the quiet Back card for ".." -->
	<include name="Wall_PrintBody">
		<param name="bevel">true</param>
		<param name="font">body_22</param>
		<definition>
			<control type="group">
				<visible>!ListItem.IsParentFolder</visible>
				<include content="PP_Picture">
					<param name="art" value="$VAR[VidView_SalonArt]"/>
					<param name="title" value="$INFO[ListItem.Label]"/>
					<param name="font" value="$PARAM[font]"/>
				</include>
				<control type="group">
					<visible>$PARAM[bevel]</visible>
					<include>PP_Bevel</include>
				</control>
			</control>
			<control type="group">
				<visible>ListItem.IsParentFolder</visible>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<right>0</right>
					<bottom>0</bottom>
					<texture colordiffuse="rule_strong" border="2">pp/frame_1.png</texture>
				</control>
				<control type="label">
					<left>0</left>
					<top>0</top>
					<right>0</right>
					<bottom>0</bottom>
					<font>cap_20</font>
					<textcolor>ink2</textcolor>
					<align>center</align>
					<label>Back</label>
				</control>
			</control>
		</definition>
	</include>

	<include name="VidView_506_Wall">
		<control type="group">
			<visible>Control.IsVisible(506)</visible>
			<include>Anim_VisibleFade</include>
			<!-- title probes: does the title fit the label's width on one line in Geist Light 56? -->
{chr(10).join(probes)}
		</control>
		<control type="panel" id="506">
			<left>0</left>
			<top>0</top>
			<width>1920</width>
			<height>1080</height>
			<orientation>vertical</orientation>
			<scrolltime tween="cubic" easing="out">300</scrolltime>
			<preloaditems>2</preloaditems>
			<!-- Up from the top row = the header words; Right past the last column / Down at the end = the View words.
			     No onback: Back leaves the folder as in every other view. -->
			<onup>9000</onup>
			<ondown>9330</ondown>
			<onleft>noop</onleft>
			<onright>9330</onright>
			<onfocus>SetProperty(TMDbHelper.Colors.SourceImage,Art(poster)|Art(tvshow.poster)|Art(thumb)|Art(fanart),home)</onfocus>
			<viewtype label="The wall">panel</viewtype>
			<visible>Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons)</visible>
{chr(10).join(layouts)}
		</control>
		<!-- the chrome comes back on paper bands when focus leaves the wall (header 0-140, View words 940-1080) -->
		<control type="group">
			<visible>Control.IsVisible(506) + !Control.HasFocus(506)</visible>
			<animation effect="fade" start="0" end="100" time="200">Visible</animation>
			<animation effect="fade" start="100" end="0" time="160">Hidden</animation>
{band.format(top=0)}
{band.format(top=940)}
		</control>
	</include>
</includes>
'''
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
