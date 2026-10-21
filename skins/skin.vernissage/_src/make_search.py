"""Generate 1080i/Includes_Search.xml: Search, Custom_1150 (SPEC 13).   python skins/skin.vernissage/_src/make_search.py

Screen: docs/skin.vernissage/screens/Custom_1150_Search.md (ids, geometry, focus map). M4, skin-developer 2026-10-21.
- The query is edit 9001, drawn as the exhibition title: the edit's own text is clear and a font_exhibit label shows
  the typed text between serif quotes ("Search the collection" in ink2 while empty). OK on 9001 opens Kodi's keyboard
  (DialogKeyboard, a Vernissage card). A 56 x 2 ink rule under the title start marks the focus.
- The sub-line counts the non-empty kinds ("Films 3 · Series 1 · Songs 9"); "Nothing in the collection for ..." when
  every kind is empty.
- Six walls in the vertical grouplist 9700 (it scrolls to the focused wall): Films 9701, Series 9702, Episodes 9703,
  Albums 9704, Artists 9705, Songs 9706, each in its group 9721-9726, shown when its always-visible 1 px data list
  9711-9716 has items (a hidden container never loads, LESSONS Passe-partout 139). Walls are plain horizontal lists
  (focus walks to the last full slot, then the row scrolls); itemlayout and focusedlayout have the same width, so the
  lit work never reflows the row (LESSONS Fold 0.9.3).
- Unfocused works hang as grey prints (VN_PrintInLayout: helper grey copies, else the ghost, Grey prints off = colour);
  the focused work of the focused wall is lit: colour art in a 6 px mat and the 2 px hairline frame, 1.10 x the print,
  centred on it (VN_LitInLayout, room twins). The light is drawn per wall OUTSIDE the list (a list clips its layouts,
  LESSONS Groove M3): the Evening pool (VN_SpotSteps) and the Day shadow (VN_ShadowSteps), placed on the focused slot
  with one reversible Conditional slide per Container(id).Position (symmetric sine in-out, 200 ms = a glide, LESSONS
  Nocturne; time 0 with Reduce motion). The grouplist spans the whole screen width (it clips its children).
- Down / Up hop walls from any item (rule 3; a hidden wall passes the move on through its own numeric onup / ondown),
  Left / Right walk a wall and stop at its ends (noop: no wrap), Back on a wall -> 9001 (numeric), Back on 9001 closes.
  OK: films / series / episodes / albums / artists open their info (Action(Info)); songs play (Kodi's default).
- The query is URL-encoded by script.skinvariables (required import): the 1 px list 9719 runs get_encoded_string on
  every change of the typed text and writes Window(Home).Property(Vernissage.Search.Encoded); the xsp paths read it,
  gated on it. Custom_1150 clears it on unload.
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Search.xml"
NL = "\n"
QUERY = "Control.GetLabel(9001).index(1)"
ENC = "Window(Home).Property(Vernissage.Search.Encoded)"
RM = "$EXP[VN_RM]"              # Includes_Vernissage.xml (animation conditions expand $EXP)

# grouplist 9700 and the wall groups (screens: walls start at y 196, x 120)
GL_TOP, GL_H = 156, 924          # each wall group starts with 40 px of room for its light, so the first heading sits at 196
PAD_TOP = 40                     # wall group: light room above the heading
HEAD_H = 36
LIST_W = 1720                    # list width from its left edge (120 - the print's x in its slot); the grouplist spans 0..1920
LIST_PAD = 24                    # print inset at the top / bottom of the list rect (room for the lit frame)
MAT, HAIR = 6, 2
CAP_H = 38

# id, data id, group id, kind label, kind for the xsp, path variable, w, h, pitch, art variable, grey kind, has_grey,
# aspect, info on OK, caption variable
WALLS = [
    (9701, 9711, 9721, "$LOCALIZE[31829]", "movies", "videodb://movies/titles/", "title", 160, 240, 184,
     "$VAR[Search_Art]", "movie_poster/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,movie)", True,
     "Year"),
    (9702, 9712, 9722, "$LOCALIZE[31578]", "tvshows", "videodb://tvshows/titles/", "title", 160, 240, 184,
     "$VAR[Search_Art]", "tvshow_poster/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,tvshow)", True,
     "Year"),
    (9703, 9713, 9723, "$LOCALIZE[31830]", "episodes", "videodb://tvshows/titles/-1/-1/", "title", 320, 180, 344,
     "$VAR[Search_StillArt]", "tvshow_fanart/$INFO[ListItem.TvShowDBID].jpg", "String.IsEqual(ListItem.DBType,episode)",
     True, "Episode"),
    (9704, 9714, 9724, "$LOCALIZE[31826]", "albums", "musicdb://albums/", "album", 200, 200, 224,
     "$INFO[ListItem.Art(thumb)]", "album_thumb/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,album)", True,
     "Artist"),
    (9705, 9715, 9725, "$LOCALIZE[31827]", "artists", "musicdb://artists/", "artist", 200, 200, 224,
     "$VAR[Search_ArtistArt]", "none.jpg", "false", True, ""),
    (9706, 9716, 9726, "$LOCALIZE[31828]", "songs", "musicdb://songs/", "title", 200, 200, 224,
     "$INFO[ListItem.Art(thumb)]", "none.jpg", "false", False, "Artist"),
]
ENCODER = 9719


def xsp(node, kind, field):
    """A url-encoded xsp path: one `contains` rule on the encoded query (LESSONS official-repo fixes)."""
    return (f"{node}?xsp=%7B%22rules%22%3A%7B%22and%22%3A%5B%7B%22field%22%3A%22{field}%22%2C%22operator%22%3A"
            f"%22contains%22%2C%22value%22%3A%5B%22$INFO[{ENC}]%22%5D%7D%5D%7D%2C%22type%22%3A%22{kind}%22%7D")


def geo(w):
    """Geometry of one wall (relative to its group): list rect, print rect in the slot, lit frame, light rects."""
    _id, _d, _g, _l, _k, _n, _f, pw, ph, pitch, *_ = w
    gap = pitch - pw
    list_y = PAD_TOP + HEAD_H
    list_h = LIST_PAD + ph + LIST_PAD
    aw, ah = round(pw * 1.10), round(ph * 1.10)           # lit art 1.10 x the print
    fw, fh = aw + 2 * (MAT + HAIR), ah + 2 * (MAT + HAIR)
    # print x in the slot: far enough in that the lit frame of slot 0 stays inside the list rect, at most the gap
    px = min(gap, max(gap // 2, (fw - pw) // 2 + 2))
    list_x = 120 - px                                     # the first print hangs at x 120
    cx, cy = px + pw / 2, LIST_PAD + ph / 2               # print centre in the item
    fx, fy = round(cx - fw / 2), round(cy - fh / 2)       # frame in the item
    slots = LIST_W // pitch                               # fully visible slots: focus positions 0 .. slots - 1
    # window-level light for slot 0, in group coordinates
    fgx, fgy = list_x + fx, list_y + fy
    pool_w, pool_h = round(2.05 * fw), round(1.5 * fh)
    pool_x = round(fgx + fw / 2 - pool_w / 2)
    pool_y = round(fgy + fh / 2 - 0.03 * fh - pool_h / 2)
    cap_y = list_y + LIST_PAD + ph + (fh - ph) // 2 + 14
    grp_h = cap_y + CAP_H
    return dict(px=px, list_x=list_x, list_y=list_y, list_h=list_h, aw=aw, ah=ah, fw=fw, fh=fh, fx=fx, fy=fy, slots=slots,
                fgx=fgx, fgy=fgy, pool=(pool_x, pool_y, pool_w, pool_h), cap_y=cap_y, grp_h=grp_h, pitch=pitch)


def slides(lid, pitch, slots, ind):
    """One reversible Conditional slide per focus position (the light glides between slots)."""
    o = []
    for k in range(1, slots):
        c = f"Integer.IsEqual(Container({lid}).Position,{k})"
        o.append(f'{ind}<animation effect="slide" end="{k * pitch},0" time="200" tween="sine" easing="inout" '
                 f'condition="{c} + !{RM}" reversible="true">Conditional</animation>')
        o.append(f'{ind}<animation effect="slide" end="{k * pitch},0" time="0" condition="{c} + {RM}">Conditional</animation>')
    return NL.join(o)


def light(w, g):
    lid = w[0]
    px, py, pw_, ph_ = g["pool"]
    ind = "\t\t\t\t"
    sw, sh = g["fw"] + 112, g["fh"] + 112
    return f"""			<!-- the light on the focused slot (outside the list: a list clips its layouts) -->
			<control type="group">
				<left>0</left>
				<top>0</top>
				<animation effect="fade" start="100" end="0" time="200" condition="!Control.HasFocus({lid})">Conditional</animation>
{slides(lid, g["pitch"], g["slots"], ind)}
				<control type="image">
					<left>{px}</left>
					<top>{py}</top>
					<width>{pw_}</width>
					<height>{ph_}</height>
					<texture colordiffuse="$VAR[spot]">vn/spot.png</texture>
					<include>VN_SpotSteps</include>
				</control>
				<control type="image">
					<left>{g["fgx"] - 50}</left>
					<top>{g["fgy"] - 42}</top>
					<width>{sw}</width>
					<height>{sh}</height>
					<texture border="56" colordiffuse="$VAR[shadow]">vn/shadow.png</texture>
					<include>VN_ShadowSteps</include>
				</control>
			</control>"""


def blank_twins(x, y, w, h, ind):
    """No art at all: a card-coloured print (room twins, LESSONS Groove M3) with the title on it."""
    return f"""{ind}<control type="group">
{ind}	<left>{x}</left>
{ind}	<top>{y}</top>
{ind}	<width>{w}</width>
{ind}	<height>{h}</height>
{ind}	<visible>String.IsEmpty(ListItem.Art(thumb)) + String.IsEmpty(ListItem.Art(poster)) + String.IsEmpty(ListItem.Art(tvshow.fanart))</visible>
{ind}	<control type="image">
{ind}		<left>0</left>
{ind}		<top>0</top>
{ind}		<width>{w}</width>
{ind}		<height>{h}</height>
{ind}		<texture colordiffuse="day_card">vn/white.png</texture>
{ind}		<visible>$EXP[VN_Day]</visible>
{ind}	</control>
{ind}	<control type="image">
{ind}		<left>0</left>
{ind}		<top>0</top>
{ind}		<width>{w}</width>
{ind}		<height>{h}</height>
{ind}		<texture colordiffuse="eve_card">vn/white.png</texture>
{ind}		<visible>$EXP[VN_Dark]</visible>
{ind}	</control>
{ind}	<control type="label">
{ind}		<left>12</left>
{ind}		<top>12</top>
{ind}		<width>{w - 24}</width>
{ind}		<height>{h - 24}</height>
{ind}		<align>center</align>
{ind}		<wrapmultiline>true</wrapmultiline>
{ind}		<font>font_small</font>
{ind}		<textcolor>$VAR[ink2]</textcolor>
{ind}		<label>$INFO[ListItem.Label]</label>
{ind}	</control>
{ind}</control>"""


def print_xml(w, g, ind):
    lid, *_ = w
    art, grey, has_grey = w[10], w[11], w[12]
    return f"""{blank_twins(g["px"], LIST_PAD, w[7], w[8], ind)}
{ind}<include content="VN_PrintInLayout">
{ind}	<param name="left" value="{g["px"]}"/>
{ind}	<param name="top" value="{LIST_PAD}"/>
{ind}	<param name="width" value="{w[7]}"/>
{ind}	<param name="height" value="{w[8]}"/>
{ind}	<param name="art" value="{art}"/>
{ind}	<param name="grey" value="{grey}"/>
{ind}	<param name="has_grey" value="{has_grey}"/>
{ind}</include>
{ind}<include content="VN_SeenDotInLayout">
{ind}	<param name="x" value="{g["px"] + w[7] - 30}"/>
{ind}	<param name="y" value="{LIST_PAD + w[8] - 30}"/>
{ind}</include>"""


def wall_xml(w, prev, nxt):
    lid, did, gid, label, kind, node, field, pw, ph, pitch, art, grey, has_grey, info, cap = w
    g = geo(w)
    onclick = "\n\t\t\t\t<onclick>Action(Info)</onclick>" if info else ""
    target = "videos" if node.startswith("videodb") else "music"
    lit = f"""					<control type="group">
						<visible>Control.HasFocus({lid})</visible>
						<animation effect="fade" start="0" end="100" time="200" tween="cubic" easing="out">Focus</animation>
						<include content="VN_LitInLayout">
							<param name="left" value="{g["fx"]}"/>
							<param name="top" value="{g["fy"]}"/>
							<param name="width" value="{g["fw"]}"/>
							<param name="height" value="{g["fh"]}"/>
							<param name="art_x" value="{MAT + HAIR}"/>
							<param name="art" value="{art}"/>
						</include>
					</control>"""
    return f"""		<!-- {kind}: list {lid}, data {did}; print {pw} x {ph} at pitch {pitch} ({g["slots"]} full slots), lit frame {g["fw"]} x {g["fh"]} -->
		<control type="group" id="{gid}">
			<width>1920</width>
			<height>{g["grp_h"]}</height>
			<!-- an emptied path keeps its old items (LESSONS Duotone 0.9.5): gate on the live query too -->
			<visible>$EXP[Search_HasEncoded] + Integer.IsGreater(Container({did}).NumItems,0)</visible>
{light(w, g)}
			<!-- heading: the kind word (ink while the wall has focus) and its count -->
			<control type="grouplist">
				<left>120</left>
				<top>{PAD_TOP}</top>
				<width>1200</width>
				<height>{HEAD_H}</height>
				<orientation>horizontal</orientation>
				<itemgap>16</itemgap>
				<control type="label">
					<width max="600">auto</width>
					<height>{HEAD_H}</height>
					<font>font_label</font>
					<label>{label}</label>
					<visible>Control.HasFocus({lid})</visible>
				</control>
				<control type="label">
					<width max="600">auto</width>
					<height>{HEAD_H}</height>
					<font>font_label</font>
					<textcolor>$VAR[ink2]</textcolor>
					<label>{label}</label>
					<visible>!Control.HasFocus({lid})</visible>
				</control>
				<control type="label">
					<width max="200">auto</width>
					<height>{HEAD_H}</height>
					<font>font_small</font>
					<textcolor>$VAR[ink2]</textcolor>
					<label>$VAR[Search_N{did}]</label>
				</control>
			</control>
			<control type="list" id="{lid}">
				<left>{g["list_x"]}</left>
				<top>{g["list_y"]}</top>
				<width>{LIST_W}</width>
				<height>{g["list_h"]}</height>
				<orientation>horizontal</orientation>
				<onup>{prev}</onup>
				<ondown>{nxt}</ondown>
				<onleft>noop</onleft>
				<onright>noop</onright>
				<onback>9001</onback>
				<onfocus>SetProperty(vn.search.wall,{lid},home)</onfocus>{onclick}
				<preloaditems>2</preloaditems>
				<include>Anim_ScrollRow</include>
				<itemlayout width="{pitch}" height="{g["list_h"]}">
{print_xml(w, g, chr(9) * 5)}
				</itemlayout>
				<focusedlayout width="{pitch}" height="{g["list_h"]}">
					<control type="group">
						<visible>!Control.HasFocus({lid})</visible>
{print_xml(w, g, chr(9) * 6)}
					</control>
{lit}
				</focusedlayout>
				<content target="{target}" limit="30" browse="never">$VAR[Search_Path{did}]</content>
			</control>
			<!-- the focused work, one line under the wall (only while the wall has focus) -->
			<control type="label">
				<left>120</left>
				<top>{g["cap_y"]}</top>
				<width>1680</width>
				<height>{CAP_H}</height>
				<font>font_small</font>
				<label>$VAR[Search_Caption{did}]</label>
				<visible>Control.HasFocus({lid})</visible>
				<include>Anim_LabelReveal</include>
			</control>
		</control>"""


def caption_var(w):
    lid, did, *_ = w
    c = f"Container({lid}).ListItem"
    kind = w[4]
    if kind in ("movies", "tvshows"):
        v = f"$INFO[{c}.Label]$INFO[{c}.Year,  ·  ,]"
    elif kind == "episodes":
        v = (f"$INFO[{c}.TVShowTitle,,  ·  ]$INFO[{c}.Season,S,]$INFO[{c}.Episode,·E,]$INFO[{c}.Title,  ·  ,]")
    elif kind in ("albums", "songs"):
        v = f"$INFO[{c}.Label]$INFO[{c}.Artist,  ·  ,]"
    else:
        v = f"$INFO[{c}.Label]"
    return f'\t<variable name="Search_Caption{did}">\n\t\t<value>{v}</value>\n\t</variable>'


def count_vars():
    """Per kind: its count ('30+' at the limit, LESSONS Sentence 0.9.3), and the sub-line piece with a leading
    separator only when an earlier kind is non-empty."""
    o = []
    for i, w in enumerate(WALLS):
        did, label = w[1], w[3]
        o.append(f"""	<variable name="Search_N{did}">
		<value condition="Integer.IsGreater(Container({did}).NumItems,30)">30+</value>
		<value>$INFO[Container({did}).NumItems]</value>
	</variable>""")
        has = f"Integer.IsGreater(Container({did}).NumItems,0)"
        earlier = " | ".join(f"Integer.IsGreater(Container({x[1]}).NumItems,0)" for x in WALLS[:i])
        vals = []
        if earlier:
            vals.append(f'\t\t<value condition="{has} + [{earlier}]">  ·  {label} $VAR[Search_N{did}]</value>')
        vals.append(f'\t\t<value condition="{has}">{label} $VAR[Search_N{did}]</value>')
        o.append(f'\t<variable name="Search_Count{did}">\n' + NL.join(vals) + "\n\t</variable>")
    return NL.join(o)


def main():
    walls = []
    for i, w in enumerate(WALLS):
        prev = WALLS[i - 1][0] if i else 9001
        nxt = WALLS[i + 1][0] if i + 1 < len(WALLS) else w[0]
        walls.append(wall_xml(w, prev, nxt))
    paths = NL.join(f"""	<variable name="Search_Path{w[1]}">
		<value condition="$EXP[Search_HasEncoded]">{xsp(w[5], w[4], w[6])}</value>
	</variable>""" for w in WALLS)
    nothing = " + ".join(f"Integer.IsEqual(Container({w[1]}).NumItems,0)" for w in WALLS)
    updating = " + ".join(f"!Container({w[1]}).IsUpdating" for w in WALLS)
    sub = "".join(f"$VAR[Search_Count{w[1]}]" for w in WALLS)
    data = NL.join(f'\t\t<include content="Search_Data"><param name="id" value="{w[1]}"/><param name="path" '
                   f'value="$VAR[Search_Path{w[1]}]"/><param name="target" value="{"videos" if w[5].startswith("videodb") else "music"}"/></include>'
                   for w in WALLS)
    first = geo(WALLS[0])
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_search.py - edit the generator, then run _src/build.py. Screen:
     docs/skin.vernissage/screens/Custom_1150_Search.md. M4, skin-developer 2026-10-21. -->
<!--
	Search (Custom_1150): the query 9001 as the exhibition title, the counts sub-line, six walls of grey prints with
	the lit work (Films 9701, Series 9702, Episodes 9703, Albums 9704, Artists 9705, Songs 9706 in groups 9721-9726 of
	grouplist 9700), their 1 px data lists 9711-9716 and the Skin Variables encoder {ENCODER}.
	Focus: 9001 Down -> the first non-empty wall; walls Up / Down = previous / next non-empty wall (9001 above the
	first), Left / Right walk and stop at the ends, Back -> 9001; 9001 Up -> the Now playing card 9950 (M2) while it
	is there; Back on 9001 closes the window.
-->
<includes>
	<expression name="Search_HasQuery">!String.IsEmpty({QUERY})</expression>
	<expression name="Search_HasEncoded">$EXP[Search_HasQuery] + !String.IsEmpty({ENC})</expression>
	<expression name="Search_Nothing">$EXP[Search_HasEncoded] + {nothing} + {updating}</expression>

	<!-- ================================================================ paths -->
	<!-- the query, encoded by script.skinvariables (required import): list {ENCODER} reruns on every change of the text.
	     A query holding " or \\ reaches the JSON raw and that wall stays empty (known limit, LESSONS Kodi review). -->
	<variable name="Search_EncoderPath">
		<value condition="$EXP[Search_HasQuery]">plugin://script.skinvariables/?info=get_encoded_string&amp;unencoded_paths=true&amp;window_prop=Vernissage.Search.Encoded&amp;window_id=home&amp;&amp;$INFO[{QUERY}]</value>
	</variable>
{paths}

	<!-- ================================================================ words -->
{count_vars()}
	<variable name="Search_Title">
		<value condition="$EXP[Search_HasQuery]">“$INFO[{QUERY}]”</value>
	</variable>
{NL.join(caption_var(w) for w in WALLS)}
	<variable name="Search_Art">
		<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<!-- episodes hang the show's fanart (DESIGN 9: thumbs are letterboxed and give the episode away), the thumb when
	     the show has none -->
	<variable name="Search_StillArt">
		<value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
		<value>$INFO[ListItem.Art(thumb)]</value>
	</variable>
	<variable name="Search_ArtistArt">
		<value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
		<value>$INFO[ListItem.Art(fanart)]</value>
	</variable>

	<!-- An offscreen data list (always visible, 1 px): its NumItems gates the wall. params: id, path, target -->
	<include name="Search_Data">
		<control type="list" id="$PARAM[id]">
			<left>-10</left>
			<top>-10</top>
			<width>1</width>
			<height>1</height>
			<itemlayout width="1" height="1" />
			<focusedlayout width="1" height="1" />
			<content target="$PARAM[target]" limit="30" browse="never">$PARAM[path]</content>
		</control>
	</include>

	<!-- ================================================================ the page -->
	<include name="Search_Page">
		<!-- the query as the exhibition title (screens: 116, 70, 1400 x 66) -->
		<control type="label">
			<left>116</left>
			<top>70</top>
			<width>1400</width>
			<height>66</height>
			<font>font_exhibit</font>
			<label>$VAR[Search_Title]</label>
			<visible>$EXP[Search_HasQuery]</visible>
		</control>
		<control type="label">
			<left>116</left>
			<top>70</top>
			<width>1400</width>
			<height>66</height>
			<font>font_exhibit</font>
			<textcolor>$VAR[ink2]</textcolor>
			<label>$LOCALIZE[31576]</label>
			<visible>!$EXP[Search_HasQuery]</visible>
		</control>
		<control type="edit" id="9001">
			<left>116</left>
			<top>70</top>
			<width>1400</width>
			<height>66</height>
			<font>font_exhibit</font>
			<textcolor>clear</textcolor>
			<focusedcolor>clear</focusedcolor>
			<disabledcolor>clear</disabledcolor>
			<invalidcolor>clear</invalidcolor>
			<textoffsetx>0</textoffsetx>
			<label></label>
			<hinttext></hinttext>
			<texturefocus />
			<texturenofocus />
			<onup condition="Control.IsVisible(9950)">9950</onup>
			<onleft>noop</onleft>
			<onright>noop</onright>
			<ondown>{WALLS[0][0]}</ondown>
		</control>
		<control type="image">
			<description>focus: the 56 x 2 rule under the title start</description>
			<left>120</left>
			<top>140</top>
			<width>vn_rule_w</width>
			<height>vn_rule_h</height>
			<texture colordiffuse="$VAR[ink]">vn/white.png</texture>
			<visible>Control.HasFocus(9001)</visible>
		</control>
		<!-- the sub-line: the kinds found and their counts, or "nothing" -->
		<control type="label">
			<left>120</left>
			<top>150</top>
			<width>1300</width>
			<height>41</height>
			<font>font_body</font>
			<textcolor>$VAR[ink2]</textcolor>
			<label>{sub}</label>
			<visible>!$EXP[Search_Nothing]</visible>
		</control>
		<control type="label">
			<left>120</left>
			<top>150</top>
			<width>1300</width>
			<height>41</height>
			<font>font_body</font>
			<textcolor>$VAR[ink2]</textcolor>
			<label>$LOCALIZE[31577] $VAR[Search_Title]</label>
			<visible>$EXP[Search_Nothing]</visible>
		</control>
		<include>VN_Clock</include>
		<!-- the walls (the grouplist spans the screen: it clips its children, and the light reaches past x 120) -->
		<control type="grouplist" id="9700">
			<left>0</left>
			<top>{GL_TOP}</top>
			<width>1920</width>
			<height>{GL_H}</height>
			<orientation>vertical</orientation>
			<usecontrolcoords>true</usecontrolcoords>
			<include>Anim_ScrollRow</include>
{NL.join(walls)}
		</control>
		<!-- the query encoder: its items are never shown; it exists to set Vernissage.Search.Encoded -->
		<include content="Search_Data"><param name="id" value="{ENCODER}"/><param name="path" value="$VAR[Search_EncoderPath]"/><param name="target" value="programs"/></include>
{data}
	</include>
</includes>
"""
    assert first["list_y"] + GL_TOP - HEAD_H == 196, first
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, "walls:", ", ".join(f"{w[4]} {geo(w)['grp_h']}px/{geo(w)['slots']} slots" for w in WALLS))


if __name__ == "__main__":
    main()
