"""Generate 1080i/SkinSettings.xml (mockup PassepartoutSettings). Edit the table, re-run.

Categories (list 9000, static) on the left; one grouplist of rows per category on the right
(9101...). Every row is a button (Geist 28 on 76px, 12% hairline, ink placard on focus) with its
value on the right in caps or Geist Mono. Cycles are written as conditional onclicks (all conditions
are evaluated before any action runs, so each click moves exactly one step). Every stored value is
an explicit keyword (LESSONS round 3: never Skin.SetString with an empty $VAR).

Usage:  python skins/skin.passepartout/_src/make_skinsettings.py
Settings reference: docs/skin.passepartout/SETTINGS.md
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "SkinSettings.xml"


def S(name):
    return f"Skin.String(passepartout.{name})"


def cycle(name, values, default, extra=None):
    """values: [(stored, label)]. Returns (onclicks, value_label_variable_values)."""
    stored = [v for v, _ in values]
    clicks, labels = [], []
    for i, (v, lab) in enumerate(values):
        nxt = stored[(i + 1) % len(stored)]
        if v == default:
            cond = f"String.IsEqual({S(name)},{v}) | " + "[" + " + ".join(f"!String.IsEqual({S(name)},{o})" for o in stored) + "]"
        else:
            cond = f"String.IsEqual({S(name)},{v})"
        clicks.append((cond, f"Skin.SetString(passepartout.{name},{nxt})"))
        if extra:
            clicks.append((cond, extra.format(v=nxt)))
        labels.append((cond, lab))
    return clicks, labels


ROWS = {
    "paper": [
        ("9111", "Paper colour", "cap", None),
        ("9112", "Luminance", "mono", ("lum", [("0.80", "0.80"), ("0.83", "0.83"), ("0.86", "0.86"), ("0.89", "0.89"), ("0.92", "0.92")], "0.86",
                                       "Skin.SetString(TMDbHelper.Colors.Luminance,{v})")),
        ("9113", "Saturation", "mono", ("sat", [("0.12", "0.12"), ("0.17", "0.17"), ("0.22", "0.22"), ("0.28", "0.28"), ("0.34", "0.34")], "0.22",
                                        "Skin.SetString(TMDbHelper.Colors.Saturation,{v})")),
        ("9114", "Shadow under the focused print", "cap", None),
    ],
    "home": [
        ("9121", "The exhibition", "cap", ("exhibition", [("best", "Unwatched, best rated"), ("recent", "Unwatched, recently acquired"), ("random", "Unwatched, drawn at random")], "best", None)),
    ],
    "libraries": [
        ("9131", "Watched dots", "cap", None),
        ("9132", "Trailer button", "cap", None),
        ("section", "9139", "The wall"),
        ("9133", "Print size", "cap", ("wall.size", [("ten", "Ten across"), ("eight", "Eight across"), ("six", "Six across")], "eight", None)),
        ("9134", "Paper between the prints", "cap", None),
        ("9135", "A mat around the chosen print", "cap", None),
        ("9136", "Wall label beside the print", "cap", ("wall.label", [("off", "Off"), ("1", "After 1 second"), ("2", "After 2 seconds")], "off", None)),
    ],
    "playback": [
        ("9141", "Controls hide after", "cap", ("osdhide", [("3", "3 seconds"), ("5", "5 seconds"), ("10", "10 seconds"), ("off", "Never")], "5", None)),
        ("9142", "Sync strip sits", "cap", ("offsetbar", [("top", "At the top"), ("bottom", "At the bottom")], "top", None)),
    ],
    "motion": [
        ("9151", "Reduce motion", "cap", None),
    ],
}

BOOLS = {
    "9111": ("neutralpaper", "Neutral", "From the artwork", True),
    "9114": ("noshadow", "Off", "On", False),
    "9131": ("nowatched", "Off", "On", False),
    "9132": ("hidetrailer", "Hidden", "Shown", False),
    "9134": ("wall.butted", "Hidden", "Shown", False),
    "9135": ("wall.nomat", "Off", "On", False),
    "9151": ("reducemotion", "On", "Off", False),
}

CATS = [
    ("paper", "Paper", "The page takes its colour from the artwork in focus, made pale and quiet so ink always reads."),
    ("home", "Home", "What hangs in the exhibition on Home. Left and right turn the prints; down shows the rest of the room."),
    ("libraries", "Libraries", "How the hang, the salon and the wall mark what you have seen, and what the wall label offers."),
    ("playback", "Playback", "The caption bar while a film plays."),
    ("motion", "Motion", "Prints grow and slide into place. Reduce motion makes every change instant."),
    ("kodi", "Kodi settings", "Player, library, interface and system settings, and the add-ons."),
]


SECTION = '''				<control type="group" id="{id}">
					<width>1120</width>
					<height>72</height>
					<control type="label">
						<left>0</left>
						<top>30</top>
						<width>1120</width>
						<height>28</height>
						<font>cap_20</font>
						<textcolor>ink2</textcolor>
						<label>{label}</label>
					</control>
				</control>'''

STRIP_INCLUDES = '''	<!-- "the wall, as set" strip: a 56x84 print with a 2 px white edge and a 10 % ink hairline -->
	<include name="SS_WallStripPrint">
		<param name="edge">true</param>
		<definition>
			<control type="group">
				<left>0</left>
				<top>0</top>
				<width>56</width>
				<height>84</height>
				<control type="image">
					<left>-3</left>
					<top>-3</top>
					<right>-3</right>
					<bottom>-3</bottom>
					<texture colordiffuse="rule_card">common/white.png</texture>
					<visible>$PARAM[edge]</visible>
				</control>
				<control type="image">
					<left>-2</left>
					<top>-2</top>
					<right>-2</right>
					<bottom>-2</bottom>
					<texture colordiffuse="white">common/white.png</texture>
					<visible>$PARAM[edge]</visible>
				</control>
				<include content="PP_Picture">
					<param name="art" value="$INFO[ListItem.Art(poster)]"/>
					<param name="title" value=""/>
					<param name="font" value="body_20"/>
				</include>
			</control>
		</definition>
	</include>
	<!-- the strip's chosen print: mat (6 px, when the mat is on) + lift, drawn over the list's slot 3 -->
	<include name="SS_WallStripChosen">
		<control type="image">
			<left>-36</left>
			<top>-18</top>
			<right>-36</right>
			<bottom>-46</bottom>
			<texture border="64,48,64,76" colordiffuse="$VAR[ShadowColor]">pp/lift_xs.png</texture>
			<visible>!Skin.HasSetting(passepartout.wall.nomat) + !Skin.HasSetting(passepartout.noshadow)</visible>
		</control>
		<control type="image">
			<left>-36</left>
			<top>-12</top>
			<right>-36</right>
			<bottom>-40</bottom>
			<texture border="64,48,64,76" colordiffuse="$VAR[ShadowColor]">pp/lift_xs.png</texture>
			<visible>Skin.HasSetting(passepartout.wall.nomat) + !Skin.HasSetting(passepartout.noshadow)</visible>
		</control>
		<control type="group">
			<visible>!Skin.HasSetting(passepartout.wall.nomat)</visible>
			<control type="image">
				<left>-7</left>
				<top>-7</top>
				<right>-7</right>
				<bottom>-7</bottom>
				<texture colordiffuse="rule_mat">common/white.png</texture>
			</control>
			<control type="image">
				<left>-6</left>
				<top>-6</top>
				<right>-6</right>
				<bottom>-6</bottom>
				<texture colordiffuse="$VAR[PaperColor]">common/white.png</texture>
			</control>
			<control type="image">
				<left>-6</left>
				<top>-6</top>
				<right>-6</right>
				<bottom>-6</bottom>
				<texture colordiffuse="card_lift">common/white.png</texture>
			</control>
		</control>
		<control type="image">
			<left>0</left>
			<top>0</top>
			<width>56</width>
			<height>84</height>
			<aspectratio>scale</aspectratio>
			<texture background="true">$INFO[Container(9190).ListItemAbsolute(3).Art(poster)]</texture>
		</control>
	</include>
'''


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row(rid, label, font, spec, first, last):
    clicks, values = [], []
    if rid in BOOLS:
        name, on_lab, off_lab, paper = BOOLS[rid]
        clicks.append(("true", f"Skin.ToggleSetting(passepartout.{name})"))
        if paper:
            clicks.append((f"Skin.HasSetting(passepartout.{name})", "Skin.SetBool(TMDbHelper.EnableColors)"))
            clicks.append((f"!Skin.HasSetting(passepartout.{name})", "Skin.Reset(TMDbHelper.EnableColors)"))
            values.append(("!System.AddonIsEnabled(plugin.video.themoviedb.helper)", "Neutral (TMDb Helper is off)"))
        values.append((f"Skin.HasSetting(passepartout.{name})", on_lab))
        values.append(("true", off_lab))
    else:
        name, vals, default, extra = spec
        c, v = cycle(name, vals, default, extra)
        clicks += c
        values += v
    vfont = "mono_24" if font == "mono" else "cap_20"
    onclick = "\n".join(f'\t\t\t\t\t<onclick condition="{c}">{a}</onclick>' if c != "true" else f"\t\t\t\t\t<onclick>{a}</onclick>" for c, a in clicks)
    var = "\n".join(f'\t\t<value condition="{c}">{esc(l)}</value>' if c != "true" else f"\t\t<value>{esc(l)}</value>" for c, l in values)
    btn = f'''				<control type="button" id="{rid}">
					<width>1120</width>
					<height>76</height>
					<font>body_28</font>
					<textcolor>ink</textcolor>
					<focusedcolor>$VAR[PaperColor]</focusedcolor>
					<textoffsetx>28</textoffsetx>
					<aligny>center</aligny>
					<texturefocus colordiffuse="ink">common/white.png</texturefocus>
					<texturenofocus border="0,0,0,2" colordiffuse="rule_row">pp/underline.png</texturenofocus>
					<label>{esc(label)}</label>
{onclick}
				</control>'''
    value_labels = f'''		<control type="label">
			<left>680</left>
			<top>$PARAM[top]</top>
			<width>1092</width>
			<height>76</height>
			<align>right</align>
			<font>{vfont}</font>
			<textcolor>ink2</textcolor>
			<label>$VAR[SS_Value_{rid}]</label>
			<visible>!Control.HasFocus({rid})</visible>
		</control>
		<control type="label">
			<left>680</left>
			<top>$PARAM[top]</top>
			<width>1092</width>
			<height>76</height>
			<align>right</align>
			<font>{vfont}</font>
			<textcolor>$VAR[PaperColor]</textcolor>
			<label>$VAR[SS_Value_{rid}]</label>
			<visible>Control.HasFocus({rid})</visible>
		</control>'''
    return btn, f'\t<variable name="SS_Value_{rid}">\n{var}\n\t</variable>', value_labels


def main():
    variables, pages = [], []
    for ci, (cid, title, desc) in enumerate(CATS):
        gid = 9101 + ci
        rows = ROWS.get(cid, [])
        buttons, values = [], []
        y = 340
        for i, r in enumerate(rows):
            if r[0] == "section":   # a caps heading inside the grouplist (72 px; an id so the chain passes it)
                buttons.append(SECTION.format(id=r[1], label=esc(r[2])))
                y += 72
                continue
            rid, label, font, spec = r
            b, v, vl = row(rid, label, font, spec, i == 0, i == len(rows) - 1)
            buttons.append(b)
            variables.append(v)
            values.append(vl.replace("$PARAM[top]", str(y)))
            y += 76
        if cid == "kodi":
            buttons.append('''				<control type="button" id="9161">
					<width>1120</width>
					<height>76</height>
					<font>body_28</font>
					<textcolor>ink</textcolor>
					<focusedcolor>$VAR[PaperColor]</focusedcolor>
					<textoffsetx>28</textoffsetx>
					<aligny>center</aligny>
					<texturefocus colordiffuse="ink">common/white.png</texturefocus>
					<texturenofocus border="0,0,0,2" colordiffuse="rule_row">pp/underline.png</texturenofocus>
					<label>Open Kodi's settings</label>
					<onclick>ActivateWindow(settings)</onclick>
				</control>''')
        vis = f'String.IsEqual(Container(9000).ListItem.Property(cat),{cid})'
        pages.append(f'''		<control type="group">
			<visible>{vis}</visible>
			<animation effect="fade" start="0" end="100" time="200">Visible</animation>
			<control type="label">
				<left>680</left>
				<top>134</top>
				<width>1120</width>
				<height>112</height>
				<font>disp_96</font>
				<textcolor>ink</textcolor>
				<label>{esc(title)}</label>
			</control>
			<control type="textbox">
				<left>680</left>
				<top>256</top>
				<width>1040</width>
				<height>68</height>
				<font>body_24</font>
				<textcolor>ink2</textcolor>
				<label>{esc(desc)}</label>
			</control>
			<control type="image">
				<left>680</left>
				<top>339</top>
				<width>1120</width>
				<height>1</height>
				<texture colordiffuse="rule">common/white.png</texture>
			</control>
			<control type="grouplist" id="{gid}">
				<left>680</left>
				<top>340</top>
				<width>1120</width>
				<height>540</height>
				<orientation>vertical</orientation>
				<itemgap>0</itemgap>
				<onleft>9000</onleft>
				<onright>noop</onright>
				<onup>noop</onup>
				<ondown>noop</ondown>
				<onback>9000</onback>
{chr(10).join(buttons)}
			</control>
{chr(10).join(values)}
		</control>''')
    cat_items = "\n".join(
        f'\t\t\t\t<item><label>{esc(t)}</label><property name="cat">{c}</property><onclick>SetFocus({9101 + i})</onclick></item>'
        for i, (c, t, _) in enumerate(CATS))
    right = "\n".join(f'\t\t\t<onright condition="String.IsEqual(Container(9000).ListItem.Property(cat),{c})">{9101 + i}</onright>'
                      for i, (c, _, _) in enumerate(CATS))
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_skinsettings.py - edit the generator, not this file.
	Skin settings (mockup PassepartoutSettings): categories 9000 on the left, the page on the right
	(rows 9101-9106 per category). Settings: docs/skin.passepartout/SETTINGS.md -->
<window>
	<defaultcontrol always="true">9000</defaultcontrol>
	<backgroundcolor>paper</backgroundcolor>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>PP_Background</include>
		<include content="PP_Crumbs2">
			<param name="a" value="$LOCALIZE[5]"/>
			<param name="b" value="Skin"/>
		</include>
		<control type="list" id="9000">
			<left>100</left>
			<top>162</top>
			<width>460</width>
			<height>704</height>
			<scrolltime>0</scrolltime>
			<onup>9000</onup>
			<ondown>9000</ondown>
			<onleft>noop</onleft>
{right}
			<include content="PP_IndexLayout"><param name="list_id" value="9000"/></include>
			<content>
{cat_items}
			</content>
		</control>
		<include>PP_SettingsDivider</include>
{chr(10).join(pages)}
		<!-- the wall, as set (Libraries page): ten small prints with paper between them (or butted), the chosen one
		     (slot 3) matted and lifted like on the wall. The list draws the prints, so their art loads (LESSONS 2). -->
		<control type="group">
			<visible>String.IsEqual(Container(9000).ListItem.Property(cat),libraries)</visible>
			<control type="label">
				<left>680</left>
				<top>872</top>
				<width>600</width>
				<height>28</height>
				<font>cap_20</font>
				<textcolor>ink2</textcolor>
				<label>The wall, as set</label>
			</control>
			<control type="list" id="9190">
				<left>680</left>
				<top>924</top>
				<width>720</width>
				<height>84</height>
				<orientation>horizontal</orientation>
				<scrolltime>0</scrolltime>
				<itemlayout width="70" height="84" condition="!Skin.HasSetting(passepartout.wall.butted)">
					<include>SS_WallStripPrint</include>
				</itemlayout>
				<focusedlayout width="70" height="84" condition="!Skin.HasSetting(passepartout.wall.butted)">
					<include>SS_WallStripPrint</include>
				</focusedlayout>
				<itemlayout width="56" height="84" condition="Skin.HasSetting(passepartout.wall.butted)">
					<include content="SS_WallStripPrint"><param name="edge" value="false"/></include>
				</itemlayout>
				<focusedlayout width="56" height="84" condition="Skin.HasSetting(passepartout.wall.butted)">
					<include content="SS_WallStripPrint"><param name="edge" value="false"/></include>
				</focusedlayout>
				<content sortby="dateadded" sortorder="descending" limit="10" browse="never" target="videos">videodb://movies/titles/</content>
			</control>
			<control type="group">
				<left>890</left>
				<top>924</top>
				<width>56</width>
				<height>84</height>
				<visible>!Skin.HasSetting(passepartout.wall.butted) + Integer.IsGreater(Container(9190).NumItems,3)</visible>
				<include>SS_WallStripChosen</include>
			</control>
			<control type="group">
				<left>848</left>
				<top>924</top>
				<width>56</width>
				<height>84</height>
				<visible>Skin.HasSetting(passepartout.wall.butted) + Integer.IsGreater(Container(9190).NumItems,3)</visible>
				<include>SS_WallStripChosen</include>
			</control>
			<control type="textbox">
				<left>1440</left>
				<top>930</top>
				<width>360</width>
				<height>90</height>
				<font>body_20</font>
				<textcolor>ink2</textcolor>
				<label>Choose the wall under View, beside The hang and Salon. Up from the top row shows the words.</label>
			</control>
		</control>
		<!-- paint chips (Paper page): the paper on this page now, and the neutral paper -->
		<control type="group">
			<visible>String.IsEqual(Container(9000).ListItem.Property(cat),paper)</visible>
			<control type="label">
				<left>680</left>
				<top>864</top>
				<width>600</width>
				<height>28</height>
				<font>cap_20</font>
				<textcolor>ink2</textcolor>
				<label>Papers</label>
			</control>
			<control type="image">
				<left>680</left>
				<top>904</top>
				<width>160</width>
				<height>56</height>
				<texture colordiffuse="$VAR[PaperColor]">common/white.png</texture>
			</control>
			<control type="image">
				<left>680</left>
				<top>904</top>
				<width>160</width>
				<height>56</height>
				<texture border="2" colordiffuse="rule_div">pp/frame_1.png</texture>
			</control>
			<control type="label">
				<left>680</left>
				<top>970</top>
				<width>200</width>
				<height>26</height>
				<font>body_20</font>
				<textcolor>ink2</textcolor>
				<label>This page</label>
			</control>
			<control type="image">
				<left>872</left>
				<top>904</top>
				<width>160</width>
				<height>56</height>
				<texture colordiffuse="paper">common/white.png</texture>
			</control>
			<control type="image">
				<left>872</left>
				<top>904</top>
				<width>160</width>
				<height>56</height>
				<texture border="2" colordiffuse="rule_div">pp/frame_1.png</texture>
			</control>
			<control type="label">
				<left>872</left>
				<top>970</top>
				<width>200</width>
				<height>26</height>
				<font>body_20</font>
				<textcolor>ink2</textcolor>
				<label>Neutral</label>
			</control>
			<control type="textbox">
				<left>1064</left>
				<top>902</top>
				<width>736</width>
				<height>64</height>
				<font>body_22</font>
				<textcolor>ink2</textcolor>
				<label>Luminance sets how pale, saturation how much hue. New values show on the next print you focus.</label>
			</control>
		</control>
	</controls>
</window>
'''
    out = xml
    # value variables live in an includes file (window-level variables are unreliable: LESSONS 2)
    inc = ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by _src/make_skinsettings.py -->\n<includes>\n'
           + "\n".join(variables) + "\n" + STRIP_INCLUDES + "</includes>\n")
    OUT.write_text(out, encoding="utf-8", newline="\n")
    (OUT.parent / "Includes_SkinSettings.xml").write_text(inc, encoding="utf-8", newline="\n")
    print("wrote SkinSettings.xml + Includes_SkinSettings.xml")


if __name__ == "__main__":
    main()
