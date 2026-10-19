"""Generate 1080i/Includes_Search.xml (mockup PassepartoutSearch). Edit here, re-run, never hand-edit the XML.

The search page types on its own keyboard (no Kodi keyboard dialog), and the results follow the typing.
Kodi has no string functions, so the query is kept as window properties on Home:
  passepartout.q     the query
  passepartout.qn    its length as n0..n40 (digit-only values can be read as string ids: LESSONS 2)
  passepartout.qh<k> the query as it was before character k (Delete restores it)
  passepartout.qc    the character a key hands to the key handler 9900
Key handler 9900 (hidden): save history, append, count up. Delete 9901: restore, count down.
Conditions of one onclick list are evaluated before any action runs, $INFO in actions when each runs,
so the history save comes first.

Results: three groups on one line from x 840 - films (posters), series (posters), music (albums) -
each a list that shows up to three prints (188 wide, pitch 244); a group starts 40px after the
previous one, placed with conditional slides on the item counts (0 / 1 / 2 / 3+). Down / Up hop between the
groups from any print; the group in focus slides to x 840 and the groups before it fade (0.9.5).

Usage:  python skins/skin.passepartout/_src/make_search.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Includes_Search.xml"

MAXLEN = 40
KEYS = list("abcdefghijklmnopqrstuvwxyz0123456789")
Q = "Window(Home).Property(passepartout.q)"
QN = "Window(Home).Property(passepartout.qn)"


def n_is(k):
    if k == 0:
        return f"[String.IsEmpty({QN}) | String.IsEqual({QN},n0)]"
    return f"String.IsEqual({QN},n{k})"


def key_handler(char="$INFO[Window(Home).Property(passepartout.qc)]", ind="			"):
    lines = []
    for k in range(MAXLEN):
        c = n_is(k)
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.qh{k},"$INFO[{Q}]",home)</onclick>')
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.qn,n{k + 1},home)</onclick>')
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.q,"$INFO[{Q}]{char}",home)</onclick>')
    return "\n".join(lines)


def delete_handler():
    lines = []
    for k in range(1, MAXLEN + 1):
        c = n_is(k)
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.q,"$INFO[Window(Home).Property(passepartout.qh{k - 1})]",home)</onclick>')
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.qn,n{k - 1},home)</onclick>')
    return "\n".join(lines)


def panel_handler():
    """Panel onclick (runs with the clicked item): letters append ListItem.Property(ch); digits can't be
    item values (digit-only values are read as string ids), so they carry digit=d<N> and append literally."""
    lines = []
    for k in range(MAXLEN):
        c = n_is(k)
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.qh{k},"$INFO[{Q}]",home)</onclick>')
        lines.append(f'\t\t\t<onclick condition="{c}">SetProperty(passepartout.qn,n{k + 1},home)</onclick>')
        lines.append(f'\t\t\t<onclick condition="{c} + !String.IsEmpty(ListItem.Property(ch))">SetProperty(passepartout.q,"$INFO[{Q}]$INFO[ListItem.Property(ch)]",home)</onclick>')
        for d in range(10):
            lines.append(f'\t\t\t<onclick condition="{c} + String.IsEqual(ListItem.Property(digit),d{d})">SetProperty(passepartout.q,"$INFO[{Q}]{d}",home)</onclick>')
    return "\n".join(lines)


def key_items():
    out = []
    for ch in KEYS:
        label = f"[UPPERCASE]{ch}[/UPPERCASE]" if ch.isdigit() else ch
        prop = f'<property name="digit">d{ch}</property>' if ch.isdigit() else f'<property name="ch">{ch}</property>'
        out.append('	' * 5 + f'<item><label>{label}</label>{prop}</item>')
    return "\n".join(out)


def xsp(dbtype, field, method, base):
    # URL-encoded smart-playlist JSON; the query goes in as $ESCINFO (quoted, JSON-escaped)
    return (f"{base}?xsp=%7B%22order%22%3A%7B%22direction%22%3A%22ascending%22%2C%22method%22%3A%22{method}%22%7D"
            f"%2C%22rules%22%3A%7B%22and%22%3A%5B%7B%22field%22%3A%22{field}%22%2C%22operator%22%3A%22contains%22"
            f"%2C%22value%22%3A%5B$ESCINFO[{Q}]%5D%7D%5D%7D%2C%22type%22%3A%22{dbtype}%22%7D")


def offsets(prev_ids):
    """Conditional slides placing a group after the previous groups (each 0 / 244 / 488 / 732 wide + 40)."""
    import itertools
    widths = {0: 0, 1: 284, 2: 528, 3: 772}
    lines = []
    for combo in itertools.product(range(4), repeat=len(prev_ids)):
        dx = sum(widths[c] for c in combo)
        if dx == 0:
            continue
        conds = []
        for lid, c in zip(prev_ids, combo):
            if c == 3:
                conds.append(f"Integer.IsGreater(Container({lid}).NumItems,2)")
            else:
                conds.append(f"Integer.IsEqual(Container({lid}).NumItems,{c})")
        lines.append(f'\t\t\t\t<animation effect="slide" start="0,0" end="{dx},0" time="0" condition="{" + ".join(conds)}">Conditional</animation>')
    return "\n".join(lines)


GROUPS = [9101, 9102, 9103]


def has(lid):
    return f"Integer.IsGreater(Container({lid}).NumItems,0)"


def vertical_nav(lid):
    """Down = the next group with results, Up = the previous one (Omar's rule: Down jumps between side-by-side
    rows from any item; walking to the end of a strip was the only way). Up from the first group = the keys."""
    i = GROUPS.index(lid)
    lines = []
    after = GROUPS[i + 1:]
    for k, tgt in enumerate(after):
        conds = [f"!{has(g)}" for g in after[:k]] + [has(tgt)]
        lines.append(f'				<ondown condition="{" + ".join(conds)}">{tgt}</ondown>')
    lines.append('				<ondown>noop</ondown>')
    before = list(reversed(GROUPS[:i]))
    for k, tgt in enumerate(before):
        conds = [f"!{has(g)}" for g in before[:k]] + [has(tgt)]
        lines.append(f'				<onup condition="{" + ".join(conds)}">{tgt}</onup>')
    lines.append('				<onup>9300</onup>')
    return "\n".join(lines)


def focus_shift(lid):
    """While a later group has focus, this group slides left by everything before that group (so the focused
    strip starts at x 840 and its prints stay on screen); groups before the focused one fade out."""
    import itertools
    widths = {0: 0, 1: 284, 2: 528, 3: 772}
    i = GROUPS.index(lid)
    lines = []
    for j in range(1, len(GROUPS)):
        focus = f"Control.HasFocus({GROUPS[j]})"
        if j <= i:
            prev = GROUPS[:j]
            for combo in itertools.product(range(4), repeat=len(prev)):
                dx = sum(widths[c] for c in combo)
                if dx == 0:
                    continue
                conds = [focus] + [f"Integer.IsGreater(Container({g}).NumItems,2)" if c == 3 else f"Integer.IsEqual(Container({g}).NumItems,{c})"
                                   for g, c in zip(prev, combo)]
                lines.append(f'				<animation effect="slide" start="0,0" end="-{dx},0" time="300" tween="cubic" easing="out" condition="{" + ".join(conds)}">Conditional</animation>')
    later = [f"Control.HasFocus({g})" for g in GROUPS[i + 1:]]
    if later:
        lines.append(f'				<animation effect="fade" start="100" end="0" time="200" condition="{" | ".join(later)}">Conditional</animation>')
    return "\n".join(lines)


def group(lid, label, path, art, square, prev, onleft, onright, target):
    h = 188 if square else 282
    top = 560 - h // 2
    cap_top = 560 + 141 + 28
    nav_right = "\n".join(f'\t\t\t\t\t<onright condition="Integer.IsGreater(Container({r}).NumItems,0){" + " + extra if extra else ""}">{r}</onright>'
                          for r, extra in onright)
    nav_left = "\n".join(f'\t\t\t\t\t<onleft condition="{cond}">{tgt}</onleft>' for tgt, cond in onleft)
    return f'''		<control type="group">
			<left>840</left>
			<!-- the list itself never hides: a hidden container isn't processed, so it couldn't load results -->
{offsets(prev)}
{focus_shift(lid)}
			<control type="label">
				<left>0</left>
				<top>360</top>
				<width>700</width>
				<height>28</height>
				<font>cap_20</font>
				<textcolor>ink</textcolor>
				<label>{label}</label>
				<visible>Integer.IsGreater(Container({lid}).NumItems,0)</visible>
			</control>
			<control type="list" id="{lid}">
				<left>-48</left>
				<top>300</top>
				<width>770</width>
				<height>560</height>
				<orientation>horizontal</orientation>
				<scrolltime tween="cubic" easing="out">260</scrolltime>
				<preloaditems>1</preloaditems>
{nav_left}
{nav_right}
{vertical_nav(lid)}
				<onback>9300</onback>
				<onfocus>SetProperty(TMDbHelper.WidgetContainer,{lid},home)</onfocus>
				<onfocus>SetProperty(TMDbHelper.Colors.SourceImage,{"Art(thumb)" if square else "Art(poster)|Art(thumb)"},home)</onfocus>
				<itemlayout width="244" height="560">
					<include content="Search_Item"><param name="top" value="{top - 300}"/><param name="h" value="{h}"/><param name="art" value="{art}"/><param name="captop" value="{cap_top - 300}"/><param name="square" value="{str(square).lower()}"/></include>
				</itemlayout>
				<focusedlayout width="244" height="560">
					<include content="Search_Item"><param name="top" value="{top - 300}"/><param name="h" value="{h}"/><param name="art" value="{art}"/><param name="captop" value="{cap_top - 300}"/><param name="square" value="{str(square).lower()}"/><param name="focused" value="Control.HasFocus({lid})"/></include>
				</focusedlayout>
				<content target="{target}" limit="30">$VAR[{path}]</content>
			</control>
		</control>'''


def main():
    films = group(9101, "Films", "Search_PathMovies", "$INFO[ListItem.Art(poster)]", False, [],
                  [("9300", "true")], [(9102, ""), (9103, "!Integer.IsGreater(Container(9102).NumItems,0)")], "videos")
    series = group(9102, "Series", "Search_PathTV", "$INFO[ListItem.Art(poster)]", False, [9101],
                   [("9101", "Integer.IsGreater(Container(9101).NumItems,0)"), ("9300", "!Integer.IsGreater(Container(9101).NumItems,0)")],
                   [(9103, "")], "videos")
    music = group(9103, "Music", "Search_PathAlbums", "$INFO[ListItem.Art(thumb)]", True, [9101, 9102],
                  [("9102", "Integer.IsGreater(Container(9102).NumItems,0)"),
                   ("9101", "!Integer.IsGreater(Container(9102).NumItems,0) + Integer.IsGreater(Container(9101).NumItems,0)"),
                   ("9300", "!Integer.IsGreater(Container(9102).NumItems,0) + !Integer.IsGreater(Container(9101).NumItems,0)")],
                  [], "music")
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_search.py - edit the generator, not this file.
	Search (Custom_1150_Search.xml, mockup PassepartoutSearch): the query set large on a hairline, an
	on-page keyboard (panel 9300: a-z 0-9, the focused key is the ink placard), Space 9311 / Delete 9312
	(grouplist 9310), results on one line from x 840 (9101 films, 9102 series, 9103 music) that follow
	the typing. How the query is kept: see the generator's docstring.
-->
<includes>
	<expression name="Search_HasQuery">!String.IsEmpty({Q})</expression>
	<expression name="Search_HasResults">Integer.IsGreater(Container(9101).NumItems,0) | Integer.IsGreater(Container(9102).NumItems,0) | Integer.IsGreater(Container(9103).NumItems,0)</expression>

	<variable name="Search_PathMovies">
		<value condition="$EXP[Search_HasQuery]">{xsp("movies", "title", "sorttitle", "videodb://movies/titles/")}</value>
	</variable>
	<variable name="Search_PathTV">
		<value condition="$EXP[Search_HasQuery]">{xsp("tvshows", "title", "sorttitle", "videodb://tvshows/titles/")}</value>
	</variable>
	<variable name="Search_PathAlbums">
		<value condition="$EXP[Search_HasQuery]">{xsp("albums", "album", "album", "musicdb://albums/")}</value>
	</variable>
	<variable name="Search_FirstResults">
		<value condition="Integer.IsGreater(Container(9101).NumItems,0)">SetFocus(9101)</value>
		<value condition="Integer.IsGreater(Container(9102).NumItems,0)">SetFocus(9102)</value>
		<value condition="Integer.IsGreater(Container(9103).NumItems,0)">SetFocus(9103)</value>
	</variable>
	<variable name="Search_KeyText">
		<value condition="Control.HasFocus(9300)">$VAR[PaperColor]</value>
		<value>ink</value>
	</variable>

	<!-- ============================================================== query + keyboard -->
	<include name="Search_Query">
		<control type="grouplist">
			<left>120</left>
			<top>150</top>
			<width>1680</width>
			<height>124</height>
			<orientation>horizontal</orientation>
			<itemgap>10</itemgap>
			<usecontrolcoords>true</usecontrolcoords>
			<control type="label">
				<width max="1640">auto</width>
				<height>124</height>
				<font>disp_104</font>
				<textcolor>ink</textcolor>
				<label>$INFO[{Q}]</label>
				<visible>$EXP[Search_HasQuery]</visible>
			</control>
			<control type="label">
				<width max="1640">auto</width>
				<height>124</height>
				<font>disp_104</font>
				<textcolor>ink3</textcolor>
				<label>Search the collection</label>
				<visible>!$EXP[Search_HasQuery]</visible>
			</control>
			<control type="image">
				<top>24</top>
				<width>2</width>
				<height>92</height>
				<texture colordiffuse="ink">common/white.png</texture>
				<animation effect="fade" start="100" end="0" time="600" delay="400" pulse="true" condition="true">Conditional</animation>
			</control>
		</control>
		<control type="image">
			<left>120</left>
			<top>296</top>
			<width>1680</width>
			<height>1</height>
			<texture colordiffuse="rule_strong">common/white.png</texture>
		</control>

		<!-- keys: 88 x 88, gap 8, six columns from 120,360. Items are 96 x 96 with the key at 24,4 so the
		     focused key's placard shadow (24 / 4 / 24 / 56) stays inside the panel. -->
		<control type="panel" id="9300">
			<left>96</left>
			<top>356</top>
			<width>600</width>
			<height>636</height>
			<orientation>vertical</orientation>
			<scrolltime>0</scrolltime>
			<onup>noop</onup>
			<ondown>9310</ondown>
			<onleft>noop</onleft>
			<onright condition="Integer.IsGreater(Container(9101).NumItems,0)">9101</onright>
			<onright condition="!Integer.IsGreater(Container(9101).NumItems,0) + Integer.IsGreater(Container(9102).NumItems,0)">9102</onright>
			<onright condition="!Integer.IsGreater(Container(9101).NumItems,0) + !Integer.IsGreater(Container(9102).NumItems,0) + Integer.IsGreater(Container(9103).NumItems,0)">9103</onright>
			<onfocus>ClearProperty(TMDbHelper.WidgetContainer,home)</onfocus>
			<!-- the panel's own onclick runs instead of the item's (with the clicked item for $INFO) -->
{panel_handler()}
			<itemlayout width="96" height="96">
				<control type="image">
					<left>24</left>
					<top>4</top>
					<width>88</width>
					<height>88</height>
					<texture border="2" colordiffuse="rule_row">pp/frame_1.png</texture>
				</control>
				<control type="label">
					<left>24</left>
					<top>4</top>
					<width>88</width>
					<height>88</height>
					<font>key_34</font>
					<textcolor>ink</textcolor>
					<align>center</align>
					<label>$INFO[ListItem.Label]</label>
				</control>
			</itemlayout>
			<focusedlayout width="96" height="96">
				<control type="image">
					<left>24</left>
					<top>4</top>
					<width>88</width>
					<height>88</height>
					<texture border="2" colordiffuse="rule_row">pp/frame_1.png</texture>
					<visible>!Control.HasFocus(9300)</visible>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>136</width>
					<height>148</height>
					<texture>pp/placard_key.png</texture>
					<visible>Control.HasFocus(9300)</visible>
				</control>
				<control type="label">
					<left>24</left>
					<top>4</top>
					<width>88</width>
					<height>88</height>
					<font>key_34</font>
					<textcolor>$VAR[Search_KeyText]</textcolor>
					<align>center</align>
					<label>$INFO[ListItem.Label]</label>
				</control>
			</focusedlayout>
			<content>
{key_items()}
			</content>
		</control>

		<!-- Space / Delete: 280 x 56, 1px frame at rest, the placard on focus (control = block + 24/4/24/56) -->
		<control type="grouplist" id="9310">
			<left>96</left>
			<top>948</top>
			<width>700</width>
			<height>116</height>
			<orientation>horizontal</orientation>
			<itemgap>-40</itemgap>
			<onup>9300</onup>
			<ondown>noop</ondown>
			<!-- one unconditional exit: with conditional onright the grouplist wrapped Delete -> Space (0.9.5) -->
			<onright>$VAR[Search_FirstResults]</onright>
			<control type="button" id="9311">
				<width>328</width>
				<height>116</height>
				<font>cap_20</font>
				<textcolor>ink</textcolor>
				<focusedcolor>$VAR[PaperColor]</focusedcolor>
				<align>center</align>
				<aligny>top</aligny>
				<textoffsety>20</textoffsety>
				<texturefocus border="74,0,74,0">pp/placard_btn56.png</texturefocus>
				<texturenofocus border="26,6,26,58" colordiffuse="rule">pp/frame_pad.png</texturenofocus>
				<label>Space</label>
{key_handler(" ", "				")}
			</control>
			<control type="button" id="9312">
				<width>328</width>
				<height>116</height>
				<font>cap_20</font>
				<textcolor>ink</textcolor>
				<focusedcolor>$VAR[PaperColor]</focusedcolor>
				<align>center</align>
				<aligny>top</aligny>
				<textoffsety>20</textoffsety>
				<texturefocus border="74,0,74,0">pp/placard_btn56.png</texturefocus>
				<texturenofocus border="26,6,26,58" colordiffuse="rule">pp/frame_pad.png</texturenofocus>
				<label>Delete</label>
{delete_handler().replace(chr(10) + "			", chr(10) + "				").replace("			<onclick", "				<onclick", 1)}
			</control>
		</control>
	</include>

	<!-- ============================================================== results -->
	<!-- one print + caption. params: top, h, art, captop, square, focused -->
	<include name="Search_Item">
		<param name="focused">false</param>
		<definition>
			<control type="group">
				<left>48</left>
				<top>$PARAM[top]</top>
				<width>188</width>
				<height>$PARAM[h]</height>
				<animation type="Focus" condition="$PARAM[focused]">
					<effect type="zoom" start="100" end="108" center="94,$PARAM[h]" time="240" tween="cubic" easing="out"/>
				</animation>
				<control type="group">
					<visible>$PARAM[focused] + !$PARAM[square]</visible>
					<include>PP_LiftSmall</include>
				</control>
				<!-- a 188 square is below lift_s's 9-slice minimum (it broke into grey blocks): the small lift -->
				<control type="image">
					<left>-24</left>
					<top>-12</top>
					<right>-24</right>
					<bottom>-40</bottom>
					<texture border="64,48,64,76" colordiffuse="$VAR[ShadowColor]">pp/lift_xs.png</texture>
					<visible>$PARAM[focused] + $PARAM[square] + !Skin.HasSetting(passepartout.noshadow)</visible>
				</control>
				<include content="PP_Picture">
					<param name="art" value="$PARAM[art]"/>
					<param name="title" value="$INFO[ListItem.Label]"/>
					<param name="font" value="body_20"/>
				</include>
				<include>PP_Bevel</include>
			</control>
			<control type="textbox">
				<left>48</left>
				<top>$PARAM[captop]</top>
				<width>188</width>
				<height>64</height>
				<font>body_24</font>
				<textcolor>ink</textcolor>
				<label>$INFO[ListItem.Label]</label>
			</control>
			<control type="label">
				<left>48</left>
				<top>$PARAM[captop]</top>
				<width>188</width>
				<height>28</height>
				<font>num_20</font>
				<textcolor>ink2</textcolor>
				<label>$INFO[ListItem.Year]</label>
				<animation effect="slide" start="0,0" end="0,68" time="0" condition="true">Conditional</animation>
				<visible>!$PARAM[square]</visible>
			</control>
			<control type="label">
				<left>48</left>
				<top>$PARAM[captop]</top>
				<width>188</width>
				<height>28</height>
				<font>cap_20</font>
				<textcolor>ink2</textcolor>
				<label>$INFO[ListItem.Artist]</label>
				<animation effect="slide" start="0,0" end="0,68" time="0" condition="true">Conditional</animation>
				<visible>$PARAM[square]</visible>
			</control>
		</definition>
	</include>

	<include name="Search_Results">
{films}
{series}
{music}
		<!-- hint / empty state, bottom of the results column -->
		<control type="label">
			<left>840</left>
			<top>952</top>
			<width>960</width>
			<height>56</height>
			<font>body_24</font>
			<textcolor>ink2</textcolor>
			<label>Results follow your typing. Press [COLOR ink]RIGHT[/COLOR] to walk the hang.</label>
			<visible>$EXP[Search_HasResults]</visible>
		</control>
		<control type="label">
			<left>840</left>
			<top>360</top>
			<width>960</width>
			<height>34</height>
			<font>body_24</font>
			<textcolor>ink2</textcolor>
			<label>Nothing in the collection by that name yet.</label>
			<visible>$EXP[Search_HasQuery] + !$EXP[Search_HasResults] + !Container(9101).IsUpdating + !Container(9102).IsUpdating + !Container(9103).IsUpdating</visible>
		</control>
		<control type="label">
			<left>840</left>
			<top>360</top>
			<width>960</width>
			<height>34</height>
			<font>body_24</font>
			<textcolor>ink2</textcolor>
			<label>Films and series match on title, music on the album's name.</label>
			<visible>!$EXP[Search_HasQuery]</visible>
		</control>
	</include>
</includes>
'''
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
