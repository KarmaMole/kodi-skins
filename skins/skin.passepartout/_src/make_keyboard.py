"""Generate skins/skin.passepartout/1080i/DialogKeyboard.xml (on-screen keyboard), in the Search
board's language: a full paper page, the text set large on a hairline, square 88px keys in a 1px
12% frame, the focused key the ink placard (lifted by its shadow).

Id contract copied from reference/skin.estuary-omega/xml/DialogKeyboard.xml:
  311 heading, 312 edit, keys 100-112 / 120-132 / 140-152 / 160-172 (Kodi writes the
  characters), 304 symbols, 303 caps lock, 302 shift, 32 space, 305 left, 306 right,
  8 backspace, side buttons 300 done / 301 cancel / 310 layout / 309 voice-or-IP / 307 IP,
  313 / 314 secondary input labels.

Placard geometry: every key control is its 88px block grown by 24 / 4 / 24 / 56 (texturefocus =
pp/placard_key.png, block + baked shadow; texturenofocus = pp/frame_pad.png, a 1px frame around the
block), so rows are grouplists with itemgap 8 - 48 = -40 placed 24px left / 4px up.

Usage:  python skins/skin.passepartout/_src/make_keyboard.py
"""
from pathlib import Path
from strip_defaults import strip_defaults  # drops tags that repeat Defaults.xml (kdk xml.redundant)
from localize import localize_xml  # literal label words -> $LOCALIZE[id] from strings.po (kdk labels.not-translated)
STRINGS_PO = Path(__file__).resolve().parent.parent / "language" / "resource.language.en_gb" / "strings.po"
DEFAULTS_XML = Path(__file__).resolve().parent.parent / "1080i" / "Defaults.xml"

OUT = Path(__file__).resolve().parent.parent / "1080i" / "DialogKeyboard.xml"

ROWS, COLS = 4, 13
KEY, GAP = 88, 8
PITCH = KEY + GAP
FUNC = [  # id, label, width in keys, columns it maps to (for up/down), type
    (304, "$LOCALIZE[31040]", 2, [0, 1], "radiobutton"),
    (303, "$LOCALIZE[31041]", 1, [2], "radiobutton"),
    (302, "$LOCALIZE[31042]", 1, [3], "radiobutton"),
    (32, "$LOCALIZE[31043]", 4, [4, 5, 6, 7], "button"),
    (305, "←", 1, [8], "button"),
    (306, "→", 1, [9], "button"),
    (8, "$LOCALIZE[31044]", 3, [10, 11, 12], "button"),
]
SIDE = [(300, "$LOCALIZE[12321]"), (301, "$LOCALIZE[222]"), (310, ""), (309, ""), (307, "$LOCALIZE[1006]")]


def key_id(r, c):
    return 100 + 20 * r + c


def func_for_col(c):
    for fid, _l, _w, cols, _t in FUNC:
        if c in cols:
            return fid
    raise ValueError(c)


def block_w(n):
    return n * KEY + (n - 1) * GAP


LOOK = '''{t}\t<texturefocus border="74,0,74,0">pp/placard_btn_key.png</texturefocus>
{t}\t<texturenofocus border="26,6,26,58" colordiffuse="rule_row">pp/frame_pad.png</texturenofocus>
{t}\t<focusedcolor>$VAR[PaperColor]</focusedcolor>
{t}\t<disabledcolor>disabled</disabledcolor>
{t}\t<align>center</align>
{t}\t<aligny>top</aligny>
{t}\t<textoffsetx>24</textoffsetx>
{t}\t<pulseonselect>false</pulseonselect>'''


def key_button(r, c, t):
    up = key_id(r - 1, c) if r > 0 else func_for_col(c)
    down = key_id(r + 1, c) if r < ROWS - 1 else func_for_col(c)
    return (f'{t}<control type="button" id="{key_id(r, c)}">\n'
            f'{t}\t<width>{KEY + 48}</width>\n{t}\t<height>{KEY + 60}</height>\n'
            f'{t}\t<font>key_34</font>\n{t}\t<textcolor>ink</textcolor>\n{t}\t<textoffsety>28</textoffsety>\n'
            f'{LOOK.format(t=t)}\n'
            f'{t}\t<onup>{up}</onup>\n{t}\t<ondown>{down}</ondown>\n'
            f'{t}</control>')


def func_button(fid, label, n, cols, ctype, t):
    up = key_id(ROWS - 1, cols[0])
    down = key_id(0, cols[0])
    w = block_w(n)
    extra = ""
    if ctype == "radiobutton":
        # the state shows in the key labels (capitals / symbols): no switch squeezed onto an 88px key
        extra = (f'{t}\t<radiowidth>1</radiowidth>\n{t}\t<radioheight>1</radioheight>\n'
                 f'{t}\t<textureradioonfocus />\n{t}\t<textureradioonnofocus />\n'
                 f'{t}\t<textureradioofffocus />\n{t}\t<textureradiooffnofocus />\n')
    return (f'{t}<control type="{ctype}" id="{fid}">\n'
            f'{t}\t<width>{w + 48}</width>\n{t}\t<height>{KEY + 60}</height>\n'
            f'{t}\t<label>{label}</label>\n'
            f'{t}\t<font>cap_20</font>\n{t}\t<textcolor>ink</textcolor>\n{t}\t<textoffsety>{4 + KEY // 2 - 19 + 7}</textoffsety>\n'
            f'{LOOK.format(t=t)}\n{extra}'
            f'{t}\t<onup>{up}</onup>\n{t}\t<ondown>{down}</ondown>\n'
            f'{t}</control>')


def row_group(top, children, t4, t5):
    return (f'{t4}<control type="grouplist">\n{t5}<left>-24</left>\n{t5}<top>{top - 4}</top>\n'
            f'{t5}<width>1400</width>\n{t5}<height>{KEY + 60}</height>\n{t5}<orientation>horizontal</orientation>\n'
            f'{t5}<itemgap>{GAP - 48}</itemgap>\n{t5}<onleft>95200</onleft>\n{t5}<onright>95200</onright>\n'
            f'{children}\n{t4}</control>')


def main():
    t4, t5 = "\t" * 4, "\t" * 5
    rows_xml = [row_group(r * PITCH, "\n".join(key_button(r, c, t5) for c in range(COLS)), t4, t5) for r in range(ROWS)]
    rows_xml.append(row_group(ROWS * PITCH, "\n".join(func_button(*f, t5) for f in FUNC), t4, t5))
    side = "\n".join(
        f'{t4}<include content="PP_DialogButton">\n{t5}<param name="id" value="{sid}"/>\n'
        f'{t5}<param name="label" value="{lab}"/>\n{t5}<param name="width" value="360"/>\n{t5}<param name="height" value="64"/>\n{t4}</include>'
        for sid, lab in SIDE)

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_keyboard.py - edit the generator, not this file.
     On-screen keyboard (Search board language). Id contract: see the generator docstring. -->
<window>
	<defaultcontrol always="true">300</defaultcontrol>
	<include>Anim_DialogOpenClose</include>
	<controls>
		<control type="group">
			<visible>!Window.IsVisible(numericinput)</visible>
			<include>PP_Background</include>
			<control type="label" id="311">
				<description>heading (Kodi)</description>
				<left>120</left>
				<top>64</top>
				<width>1300</width>
				<height>28</height>
				<font>cap_20</font>
				<textcolor>ink</textcolor>
			</control>
			<include>PP_Clock</include>
			<control type="edit" id="312">
				<left>120</left>
				<top>150</top>
				<width>1680</width>
				<height>124</height>
				<font>disp_104</font>
				<textcolor>ink</textcolor>
				<focusedcolor>ink</focusedcolor>
				<textoffsetx>0</textoffsetx>
				<aligny>center</aligny>
				<texturefocus />
				<texturenofocus />
			</control>
			<control type="image">
				<left>120</left>
				<top>296</top>
				<width>1680</width>
				<height>1</height>
				<texture colordiffuse="rule_strong">common/white.png</texture>
			</control>
			<control type="label" id="313">
				<left>120</left>
				<top>304</top>
				<width>1680</width>
				<height>28</height>
				<font>body_20</font>
				<textcolor>ink2</textcolor>
			</control>
			<control type="label" id="314">
				<left>120</left>
				<top>328</top>
				<width>1680</width>
				<height>28</height>
				<font>body_20</font>
				<textcolor>ink2</textcolor>
			</control>
			<control type="group" id="78500">
				<left>120</left>
				<top>360</top>
{chr(10).join(rows_xml)}
			</control>
			<control type="grouplist" id="95200">
				<left>1440</left>
				<top>360</top>
				<width>360</width>
				<height>460</height>
				<orientation>vertical</orientation>
				<itemgap>12</itemgap>
				<onleft>100</onleft>
				<onright>100</onright>
				<onup>95200</onup>
				<ondown>95200</ondown>
{side}
			</control>
		</control>
	</controls>
</window>
'''
    OUT.write_text(localize_xml(strip_defaults(xml, DEFAULTS_XML), STRINGS_PO), encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
