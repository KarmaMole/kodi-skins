"""One-off restyle pass (2026-10-19): Majan's shared look in Includes_Common.xml -> Six Degrees.

Top bar = wordmark + a one-stop route ("o Home ---- O Page"), clock only (no date, no rule),
focus frame = the 6 px ink ring of the boards (gap 7), buttons = pills (primary ink, secondary hair outline,
focused = ink fill + outer ring like the station page's Play), sub-nav = ink pill on focus.
Kept for the record; do not re-run after hand edits.
"""
import re
from pathlib import Path

X = Path(__file__).resolve().parents[1] / "1080i"


def replace_include(path, name, new):
    p = X / path
    s = p.read_text(encoding="utf-8")
    start = s.index(f'<include name="{name}"')
    depth = 0
    end = None
    tok = re.compile(r"<include\b[^>]*?(/?)>|</include>")
    for m in tok.finditer(s, start):
        if m.group(0) == "</include>":
            depth -= 1
            if depth == 0:
                end = m.end()
                break
        elif m.group(1) == "/":
            continue
        else:
            depth += 1
    s = s[:start] + new.strip() + s[end:]
    p.write_text(s, encoding="utf-8")


F = "Includes_Common.xml"
replace_include(F, "SD_Clock", """<include name="SD_Clock">
		<control type="label">
			<left>1500</left>
			<top>62</top>
			<width>356</width>
			<height>48</height>
			<align>right</align>
			<font>xb_30</font>
			<textcolor>ink</textcolor>
			<label>$INFO[System.Time]</label>
		</control>
	</include>""")
replace_include(F, "SD_TopRule", """<include name="SD_TopRule">
		<description>No rule under the top bar in Six Degrees (boards); kept as an empty hook.</description>
	</include>""")
replace_include(F, "SD_PageHeader", """<include name="SD_PageHeader">
		<param name="index"></param>
		<param name="title"></param>
		<param name="sub"></param>
		<definition>
			<!-- wordmark + a one-stop route: (o) Home, grey line, (O) Page title, sub -->
			<control type="image">
				<left>64</left>
				<top>66</top>
				<width>44</width>
				<height>44</height>
				<texture>sd/wordmark.png</texture>
			</control>
			<control type="label">
				<left>122</left>
				<top>64</top>
				<width>290</width>
				<height>48</height>
				<font>xb_28</font>
				<textcolor>ink</textcolor>
				<label>Six Degrees</label>
			</control>
			<control type="grouplist">
				<left>420</left>
				<top>70</top>
				<width>1060</width>
				<height>36</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<usecontrolcoords>true</usecontrolcoords>
				<control type="group">
					<width>30</width>
					<height>36</height>
					<control type="image"><left>2</left><top>6</top><width>24</width><height>24</height><texture colordiffuse="white">sd/disc_18.png</texture></control>
					<control type="image"><left>2</left><top>6</top><width>24</width><height>24</height><texture colordiffuse="l_route">sd/ring_18_5.png</texture></control>
				</control>
				<control type="label">
					<width>auto</width>
					<height>36</height>
					<font>semi_24</font>
					<textcolor>ink2</textcolor>
					<label>$LOCALIZE[31019]</label>
				</control>
				<control type="label"><width>16</width><height>36</height><label></label></control>
				<control type="image">
					<top>15</top>
					<width>72</width>
					<height>6</height>
					<texture border="3,0,3,0" colordiffuse="l_route">sd/line_h6.png</texture>
				</control>
				<control type="group">
					<width>44</width>
					<height>36</height>
					<control type="image"><left>-1</left><top>-1</top><width>38</width><height>38</height><texture colordiffuse="white">sd/disc_32.png</texture></control>
					<control type="image"><left>-1</left><top>-1</top><width>38</width><height>38</height><texture colordiffuse="ink">sd/ring_32_8.png</texture></control>
				</control>
				<control type="label">
					<width max="640">auto</width>
					<height>36</height>
					<font>xb_24</font>
					<textcolor>ink</textcolor>
					<label>$PARAM[title]</label>
				</control>
				<control type="label">
					<left>16</left>
					<width max="360">auto</width>
					<height>36</height>
					<font>semi_24</font>
					<textcolor>ink2</textcolor>
					<label>$PARAM[sub]</label>
				</control>
			</control>
		</definition>
	</include>""")
for name in ("SD_FocusFrame", "SD_FocusFrameAlways"):
    replace_include(F, name, f"""<include name="{name}">
		<param name="visible">true</param>
		<definition>
			<control type="image">
				<left>focus_out</left>
				<top>focus_out</top>
				<right>focus_out</right>
				<bottom>focus_out</bottom>
				<texture border="20" colordiffuse="ink">sd/ringf_6.png</texture>
				<visible>$PARAM[visible]</visible>
			</control>
		</definition>
	</include>""")
for name in ("SD_Tex_ButtonPrimary", "SD_Tex_ButtonPrimary_Round"):
    replace_include(F, name, f"""<include name="{name}">
		<texturefocus border="28" colordiffuse="ink">sd/pill_56.png</texturefocus>
		<texturenofocus border="28" colordiffuse="ink">sd/pill_56.png</texturenofocus>
	</include>""")
for name in ("SD_Tex_ButtonSecondary", "SD_Tex_ButtonSecondary_Round"):
    replace_include(F, name, f"""<include name="{name}">
		<texturefocus border="28" colordiffuse="ink">sd/pill_56.png</texturefocus>
		<texturenofocus border="28" colordiffuse="hair">sd/pill_56_o3.png</texturenofocus>
	</include>""")
replace_include(F, "SD_SubNavButton", """<include name="SD_SubNavButton">
		<param name="visible">true</param>
		<param name="onclick">noop</param>
		<definition>
			<control type="button" id="$PARAM[id]">
				<width>auto</width>
				<height>subnav_h</height>
				<font>semi_22</font>
				<textcolor>ink2</textcolor>
				<focusedcolor>white</focusedcolor>
				<textoffsetx>16</textoffsetx>
				<texturefocus border="20" colordiffuse="ink">sd/pill_40.png</texturefocus>
				<texturenofocus />
				<label>$PARAM[label]</label>
				<onclick>$PARAM[onclick]</onclick>
				<visible>$PARAM[visible]</visible>
			</control>
		</definition>
	</include>""")

p = X / F
s = p.read_text(encoding="utf-8")
s = s.replace("""					<font>xb_24</font>
					<textcolor>on_ink</textcolor>
					<focusedcolor>on_ink</focusedcolor>""", """					<font>xb_24</font>
					<textcolor>white</textcolor>
					<focusedcolor>white</focusedcolor>""")
s = s.replace('<texture colordiffuse="on_ink">$PARAM[icon]</texture>', '<texture colordiffuse="white">$PARAM[icon]</texture>')
s = s.replace("""					<font>semi_24</font>
					<textcolor>ink</textcolor>
					<focusedcolor>ink</focusedcolor>""", """					<font>semi_24</font>
					<textcolor>ink</textcolor>
					<focusedcolor>white</focusedcolor>""")
RING = """<control type="image">
					<left>-9</left>
					<top>-9</top>
					<right>-9</right>
					<bottom>-9</bottom>
					<texture border="38" colordiffuse="ink">sd/pill_76_ring.png</texture>
					<visible>{v}</visible>
				</control>"""
s = s.replace("""<include content="SD_FocusFrameAlways">
					<param name="visible" value="Control.HasFocus($PARAM[id])"/>
				</include>""", RING.format(v="Control.HasFocus($PARAM[id])"))
s = s.replace("""<include content="SD_FocusFrameAlways">
					<param name="visible" value="Control.HasFocus($PARAM[id]) | $PARAM[focus_also]"/>
				</include>""", RING.format(v="Control.HasFocus($PARAM[id]) | $PARAM[focus_also]"))
p.write_text(s, encoding="utf-8")

p = X / "Constants.xml"
s = p.read_text(encoding="utf-8")
s = s.replace('<constant name="focus_out">-7</constant>', '<constant name="focus_out">-13</constant>')
s = s.replace('<constant name="focus_grow">14</constant>', '<constant name="focus_grow">26</constant>')
s = s.replace('<constant name="page_margin">96</constant>', '<constant name="page_margin">64</constant>')
s = s.replace('<constant name="page_width">1728</constant>', '<constant name="page_width">1792</constant>')
p.write_text(s, encoding="utf-8")
print("restyled Includes_Common.xml + Constants.xml")
