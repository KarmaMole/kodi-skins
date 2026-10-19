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
    "9151": ("reducemotion", "On", "Off", False),
}

CATS = [
    ("paper", "Paper", "The page takes its colour from the artwork in focus, made pale and quiet so ink always reads."),
    ("home", "Home", "What hangs in the exhibition on Home. Left and right turn the prints; down shows the rest of the room."),
    ("libraries", "Libraries", "How the hang and the salon mark what you have seen, and what the wall label offers."),
    ("playback", "Playback", "The caption bar while a film plays."),
    ("motion", "Motion", "Prints grow and slide into place. Reduce motion makes every change instant."),
    ("kodi", "Kodi settings", "Player, library, interface and system settings, and the add-ons."),
]


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
        for i, (rid, label, font, spec) in enumerate(rows):
            b, v, vl = row(rid, label, font, spec, i == 0, i == len(rows) - 1)
            buttons.append(b)
            variables.append(v)
            values.append(vl.replace("$PARAM[top]", str(340 + i * 76)))
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
    inc = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- GENERATED by _src/make_skinsettings.py -->\n<includes>\n' + "\n".join(variables) + "\n</includes>\n"
    OUT.write_text(out, encoding="utf-8", newline="\n")
    (OUT.parent / "Includes_SkinSettings.xml").write_text(inc, encoding="utf-8", newline="\n")
    print("wrote SkinSettings.xml + Includes_SkinSettings.xml")


if __name__ == "__main__":
    main()
