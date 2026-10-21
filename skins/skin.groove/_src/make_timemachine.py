"""Generate 1080i/Custom_1170_TimeMachine.xml: Groove's Time machine.   python skins/skin.groove/_src/make_timemachine.py

screens/Custom_1170_TimeMachine.md (board 09), DATA.md section 3, SPEC 8.1, producer's decision 2 (Up / OK goes deeper:
decades -> years -> albums, Down goes back).

Levels, bottom to top: decades 1201 (static list, buckets gated by count probes) -> years 1202 (musicdb://years/ with an
albums xsp on the bucket's span: exactly the years that have albums, DATA 3.2) -> the arc 1203 (the focused year's albums,
its own FolderPath; the same arc as view 503, make_music_views.arc) -> Play year 1204.

Buckets (DATA 3.1): pre-1980, 80s, 90s, 00s, 10s, 20s, each with an unlimited count probe (1231-1236). A sparse edge
bucket (fewer than 5 albums) folds into its neighbour, using a probe for the merged span (1237 = 1-1989, 1238 =
2010-2039) so the count stays exact. A sparse interior bucket stays on its own (XML can't add counts; with Omar's library
only the edges are sparse: 1967-89 12, 90s 36, 00s 86, 10s 80, 20s 5). Span labels use the earliest / latest year
probes (1260 / 1261). Bucket keys are words (pre, pre80, 80s ...), never bare digits (LESSONS 2).
"""
from pathlib import Path
import json
import re
import sys
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_music_views as MV  # noqa: E402
import strip_defaults  # noqa: E402

OUT = HERE.parent / "1080i" / "Custom_1170_TimeMachine.xml"
NL = "\n"


def xsp_albums(lo, hi):
    j = {"type": "albums", "rules": {"and": [{"field": "year", "operator": "between", "value": [str(lo), str(hi)]}]}}
    return "musicdb://albums/?xsp=" + quote(json.dumps(j, separators=(",", ":")), safe="")


def xsp_year_songs_random():
    """Every song of the focused year in random order (no-helper Play, DEVICE_AUDIT M1): never PlayerControl(Random*),
    which saves Kodi's music shuffle setting. The year comes from the years list's label at click time.
    Device pass 2: PlayMedia(musicdb://songs/?xsp=...,isdir) was opened as a FILE (VideoPlayer "Playback failed");
    the year node musicdb://years/<y>/-1/ (all albums -> songs) is a real folder, like the album / genre fallbacks."""
    return ("musicdb://years/YEAR/-1/?xsp=" + quote(json.dumps({"type": "songs", "order": {"method": "random"}},
            separators=(",", ":")), safe="")).replace("YEAR", "$INFO[Container(1202).ListItem.Label]")


def xsp_years(lo, hi):
    j = {"type": "albums", "group": {"type": "years"},
         "rules": {"and": [{"field": "year", "operator": "between", "value": [str(lo), str(hi)]}]}}
    return "musicdb://years/?xsp=" + quote(json.dumps(j, separators=(",", ":")), safe="")


SPANS = {"pre": (1, 1979), "80s": (1980, 1989), "90s": (1990, 1999), "00s": (2000, 2009), "10s": (2010, 2019),
         "20s": (2020, 2039), "pre80": (1, 1989), "tens20": (2010, 2039)}
PROBE = {"pre": 1231, "80s": 1232, "90s": 1233, "00s": 1234, "10s": 1235, "20s": 1236, "pre80": 1237, "tens20": 1238}


def n(key):
    return f"Container({PROBE[key]}).NumItems"


def sparse(key):
    return f"[Integer.IsGreater({n(key)},0) + !Integer.IsGreaterOrEqual({n(key)},5)]"


BUCKETS = [  # key, label, visible
    ("pre", "$INFO[Container(1260).ListItem.Label,,–79]",
     f"Integer.IsGreater({n('pre')},0) + [Integer.IsGreaterOrEqual({n('pre')},5) | Integer.IsEqual({n('80s')},0)]"),
    ("pre80", "$INFO[Container(1260).ListItem.Label,,–89]", f"{sparse('pre')} + Integer.IsGreater({n('80s')},0)"),
    ("80s", "80s", f"Integer.IsGreater({n('80s')},0) + !{sparse('pre')}"),
    ("90s", "90s", f"Integer.IsGreater({n('90s')},0)"),
    ("00s", "00s", f"Integer.IsGreater({n('00s')},0)"),
    ("10s", "10s", f"Integer.IsGreater({n('10s')},0) + !{sparse('20s')}"),
    ("tens20", "2010–$INFO[Container(1261).ListItem.Label]", f"{sparse('20s')} + Integer.IsGreater({n('10s')},0)"),
    ("20s", "20s", f"Integer.IsGreater({n('20s')},0) + [Integer.IsGreaterOrEqual({n('20s')},5) | Integer.IsEqual({n('10s')},0)]"),
]
KEY = "Container(1201).ListItem.Property(key)"


def var(name, rows):
    o = [f'\t<variable name="{name}">']
    for c, v in rows:
        o.append(f'\t\t<value condition="{c}">{v}</value>' if c else f"\t\t<value>{v}</value>")
    o.append("\t</variable>")
    return NL.join(o)


def probes():
    o = []
    lists = [(PROBE[k], xsp_albums(*SPANS[k]), "") for k in PROBE]
    lists += [(1260, "musicdb://years/", 'sortby="label" sortorder="ascending" limit="1" browse="never"'),
              (1261, "musicdb://years/", 'sortby="label" sortorder="descending" limit="1" browse="never"')]
    for lid, path, attrs in lists:
        o.append(f"""		<control type="list" id="{lid}">
			<left>0</left>
			<top>0</top>
			<width>1</width>
			<height>1</height>
			<itemlayout width="1" height="1" />
			<focusedlayout width="1" height="1" />
			<content target="music" {attrs}>{path}</content>
		</control>""")
    return NL.join(o)


def decade_item(focused):
    f = focused
    font = "font_label" if f else "font_small"
    ink = "$VAR[ink]" if f else "$VAR[ink2]"
    o = [f"""				<control type="label">
					<left>0</left>
					<top>30</top>
					<width>264</width>
					<height>64</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>{font}</font>
					<textcolor>{ink}</textcolor>
					<selectedcolor>{ink}</selectedcolor>
					<label>$INFO[ListItem.Label]  [COLOR $VAR[ink3]]$INFO[ListItem.Label2][/COLOR]</label>
				</control>"""]
    if f:
        o.insert(0, MV.image(72, 9, 120, 4, "groove/white.png", "$VAR[ink]", None, ind=4) + NL
                 + MV.image(-8, -40, 280, 200, "groove/glow_radial.png", "$VAR[focus_glow]", "Control.HasFocus(1201)",
                            "<include>Anim_FocusLight</include>", ind=4))
    return NL.join(o)


def year_item(focused):
    if focused:
        return (MV.image(54, 6, 4, 100, "groove/white.png", "$VAR[ink]", None, ind=4) + NL
                + MV.image(-14, 30, 140, 140, "groove/glow_radial.png", "$VAR[focus_glow]", "Control.HasFocus(1202)",
                           "<include>Anim_FocusLight</include>", ind=4) + NL
                + """				<control type="label">
					<left>0</left>
					<top>116</top>
					<width>112</width>
					<height>44</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_label</font>
					<textcolor>$VAR[ink]</textcolor>
					<selectedcolor>$VAR[ink]</selectedcolor>
					<label>$INFO[ListItem.Label]</label>
				</control>""")
    return (MV.image(55, 46, 2, 60, "groove/white.png", "$VAR[ink2]", None, ind=4) + NL
            + """				<control type="label">
					<left>0</left>
					<top>118</top>
					<width>112</width>
					<height>40</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_small</font>
					<textcolor>$VAR[ink2]</textcolor>
					<selectedcolor>$VAR[ink2]</selectedcolor>
					<label>$INFO[ListItem.Label]</label>
				</control>""")


def main():
    years_paths = [(f"String.IsEqual({KEY},{k})", xsp_years(*SPANS[k])) for k, _, _ in BUCKETS]
    album_paths = [(f"String.IsEqual({KEY},{k})", xsp_albums(*SPANS[k])) for k, _, _ in BUCKETS]
    variables = NL.join([
        var("TM_YearsPath", years_paths + [(None, "musicdb://years/")]),
        var("TM_ArcPath", [("!String.IsEmpty(Container(1202).ListItem.FolderPath)", "$INFO[Container(1202).ListItem.FolderPath]")]
            + album_paths + [(None, xsp_albums(1990, 1999))]),
    ])
    items = []
    for k, label, vis in BUCKETS:
        items.append(f"""					<item>
						<label>{label}</label>
						<label2>$INFO[Container({PROBE[k]}).NumItems]</label2>
						<property name="key">{k}</property>
						<onclick>SetFocus(1202)</onclick>
						<visible>{vis}</visible>
					</item>""")
    centre_dec = NL.join(
        f'\t\t\t\t<animation effect="slide" start="0,0" end="{(6 - c) * 132},0" time="0" condition="Integer.IsEqual(Container(1201).NumItems,{c})">Conditional</animation>'
        for c in range(1, 6))
    centre_years = NL.join(
        f'\t\t\t\t<animation effect="slide" start="0,0" end="{(15 - c) * 56},0" time="0" condition="Integer.IsEqual(Container(1202).NumItems,{c})">Conditional</animation>'
        for c in range(1, 15))
    arc_nav = """			<onup>1204</onup>
			<ondown>1202</ondown>
			<onback>1202</onback>
			<onleft>noop</onleft>
			<onright>1204</onright>
			<onclick>Action(Info)</onclick>
			<onfocus condition="!String.IsEmpty(Container(1201).ListItem.Property(key))">Skin.SetString(groove.tm.bucket,$INFO[Container(1201).ListItem.Property(key)])</onfocus>
			<onfocus condition="!String.IsEmpty(Container(1202).ListItem.Label)">Skin.SetString(groove.tm.year,$INFO[Container(1202).ListItem.Label])</onfocus>"""
    content = '\n\t\t\t<content target="music" sortby="artist" sortorder="ascending">$VAR[TM_ArcPath]</content>'
    driver, stage = MV.arc(1203, 0, arc_nav, content=content, title_y=670)
    has_mini = "name=\"Groove_MiniPlayer\"" in "".join(p.read_text(encoding="utf-8", errors="ignore") for p in (HERE.parent / "1080i").glob("Includes*.xml"))
    mini = ('\t\t<include content="Groove_MiniPlayer"><param name="down" value="1204"/><param name="left" value="1204"/>'
            '<param name="back" value="1204"/></include>') if has_mini else "\t\t<!-- Groove_MiniPlayer (9950, lane B) is included here by this generator once it exists -->"
    helper = "$EXP[HasGrooveHelper]"
    year_songs = xsp_year_songs_random()
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_timemachine.py - edit the generator, then re-run.
	Time machine (custom window 1170, screens/Custom_1170_TimeMachine.md, board 09). Opened from Home's Time machine tile
	and the music library header.
	Focus map: decades 1201 -Up/OK-> years 1202 -Up/OK-> arc 1203 -Up / Right at the end-> Play year 1204 -Up-> mini player
	9950 (while music plays). Down goes back one level; Back: arc -> years -> decades -> the window that opened it.
	Paths change with the focused bucket / year; the arc reads the focused year item's own folder (musicdb://years/Y/?xsp).
-->
<window type="window" id="1170">
	<defaultcontrol always="true">1201</defaultcontrol>
	<backgroundcolor>ground_static</backgroundcolor>
	<!-- reopen on the decade / year used last: Timers.xml steps the lists there (groove_tm_bucket / groove_tm_year) -->
	<onload>ClearProperty(groove.tm.bucketdone,home)</onload>
	<onload>ClearProperty(groove.tm.yeardone,home)</onload>
	<controls>
{probes()}
		<include>Groove_Room</include>
		<control type="group">
			<visible>Integer.IsGreater(Container(1203).NumItems,0)</visible>
{MV.wash(1203, 960, 430, 1300, ind=3)}
		</control>
		<control type="group">
			<include>Anim_WindowContent</include>
			<!-- the year, huge and faint, behind the arc -->
			<control type="label">
				<left>96</left>
				<top>20</top>
				<width>1728</width>
				<height>440</height>
				<align>center</align>
				<aligny>center</aligny>
				<font>font_numeral</font>
				<textcolor>$VAR[ink_faint]</textcolor>
				<label>$INFO[Container(1202).ListItem.Label]</label>
				<include content="Anim_PulseFade"><param name="id" value="1202"/></include>
			</control>
{stage}
{driver}
			<!-- Play year -->
			<control type="image">
				<left>1697</left>
				<top>266</top>
				<width>116</width>
				<height>116</height>
				<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
				<visible>Control.HasFocus(1204)</visible>
				<include>Anim_LabelReveal</include>
			</control>
			<control type="button" id="1204">
				<left>1715</left>
				<top>284</top>
				<width>80</width>
				<height>80</height>
				<texturefocus />
				<texturenofocus />
				<label />
				<onup condition="Control.IsVisible(9950)">9950</onup>
				<ondown>1203</ondown>
				<onleft>1203</onleft>
				<onright>noop</onright>
				<onback>1203</onback>
				<onclick condition="{helper}">RunScript(script.karmamole.helper,action=play_shuffled,"path=$INFO[Container(1202).ListItem.FolderPath]")</onclick>
				<onclick condition="!{helper}">PlayMedia({year_songs},isdir)</onclick>
				<visible>Integer.IsGreater(Container(1203).NumItems,0)</visible>
			</control>
			<control type="image">
				<left>1731</left>
				<top>300</top>
				<width>48</width>
				<height>48</height>
				<texture colordiffuse="$VAR[icon_rest]">icons/playall.png</texture>
				<visible>!Control.HasFocus(1204) + Integer.IsGreater(Container(1203).NumItems,0)</visible>
			</control>
			<control type="image">
				<left>1731</left>
				<top>300</top>
				<width>48</width>
				<height>48</height>
				<texture colordiffuse="$VAR[ink]">icons/playall.png</texture>
				<visible>Control.HasFocus(1204)</visible>
			</control>
			<control type="label">
				<left>1424</left>
				<top>360</top>
				<width>400</width>
				<height>36</height>
				<align>right</align>
				<aligny>center</aligny>
				<font>font_tray</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$LOCALIZE[31613]</label>
				<visible>Control.HasFocus(1204)</visible>
				<include>Anim_LabelReveal</include>
			</control>
			<!-- the timeline: years above, decades below a baseline; it steps back while the arc has focus -->
			<control type="group">
				<include content="Anim_Dim"><param name="condition" value="Control.HasFocus(1203) | Control.HasFocus(1204)"/><param name="to" value="40"/></include>
				<control type="group">
{centre_years}
					<control type="list" id="1202">
						<left>120</left>
						<top>740</top>
						<width>1680</width>
						<height>160</height>
						<orientation>horizontal</orientation>
						<onup>1203</onup>
						<ondown>1201</ondown>
						<onback>1201</onback>
						<onleft>noop</onleft>
						<onright>noop</onright>
						<onclick>SetFocus(1203)</onclick>
						<onfocus condition="!String.IsEmpty(Container(1201).ListItem.Property(key))">Skin.SetString(groove.tm.bucket,$INFO[Container(1201).ListItem.Property(key)])</onfocus>
						<include>Anim_ScrollRow</include>
						<itemlayout width="112" height="160">
{year_item(False)}
						</itemlayout>
						<focusedlayout width="112" height="160">
{year_item(True)}
						</focusedlayout>
						<content target="music" sortby="label" sortorder="ascending">$VAR[TM_YearsPath]</content>
					</control>
				</control>
				<control type="image">
					<left>240</left>
					<top>930</top>
					<width>1440</width>
					<height>2</height>
					<texture colordiffuse="$VAR[line]">groove/white.png</texture>
				</control>
				<control type="group">
					<include content="Anim_Dim"><param name="condition" value="Control.HasFocus(1202)"/><param name="to" value="55"/></include>
{centre_dec}
					<control type="list" id="1201">
						<left>168</left>
						<top>920</top>
						<width>1584</width>
						<height>94</height>
						<orientation>horizontal</orientation>
						<onup condition="Integer.IsGreater(Container(1202).NumItems,0)">1202</onup>
						<ondown>noop</ondown>
						<onleft>noop</onleft>
						<onright>noop</onright>
						<itemlayout width="264" height="94">
{decade_item(False)}
						</itemlayout>
						<focusedlayout width="264" height="94">
{decade_item(True)}
						</focusedlayout>
						<content>
{NL.join(items)}
						</content>
					</control>
				</control>
			</control>
			<!-- no years at all -->
			<control type="label">
				<left>0</left>
				<top>516</top>
				<width>1920</width>
				<height>48</height>
				<align>center</align>
				<aligny>center</aligny>
				<font>font_caption</font>
				<textcolor>$VAR[ink2]</textcolor>
				<label>$LOCALIZE[31614]</label>
				<visible>Integer.IsEqual(Container(1201).NumItems,0) + !Container(1260).IsUpdating</visible>
			</control>
			<!-- window header -->
			<control type="image">
				<left>96</left>
				<top>54</top>
				<width>44</width>
				<height>44</height>
				<texture colordiffuse="$VAR[ink]">icons/timemachine.png</texture>
			</control>
			<control type="label">
				<left>156</left>
				<top>54</top>
				<width>600</width>
				<height>44</height>
				<aligny>center</aligny>
				<font>font_label</font>
				<textcolor>$VAR[ink]</textcolor>
				<label>$LOCALIZE[31407]</label>
			</control>
		</control>
{mini}
	</controls>
</window>
"""
    # the variables live in an include file (LESSONS: variables inside a window are unreliable)
    inc = HERE.parent / "1080i" / "Includes_TimeMachine.xml"
    inc.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_timemachine.py - content paths of the Time machine (Custom_1170). -->
<includes>
{variables}
</includes>
""", encoding="utf-8", newline="\n")
    xml, _ = strip_defaults.strip(xml)   # tags that only repeat Defaults.xml (official review xml.redundant)
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, "and", inc.name)


if __name__ == "__main__":
    main()
