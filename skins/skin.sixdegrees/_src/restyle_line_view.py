"""One-off pass (2026-10-19): Majan's Showcase (view 500) -> Six Degrees "Line" view.

The library looks like a station page (every film is a station): the focused film in an interchange ring,
caption, title (84 / 60 tiers), facts with hair pipes, plot. The browse strip (fixedlist 500, focus fixed in
slot 1) hangs on a grey line like the map's lines; the focused station grows inside an ink ring.
Kept for the record.
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
    for m in re.compile(r"<include\b[^>]*?(/?)>|</include>").finditer(s, start):
        if m.group(0) == "</include>":
            depth -= 1
            if depth == 0:
                end = m.end()
                break
        elif m.group(1) == "/":
            continue
        else:
            depth += 1
    p.write_text(s[:start] + new.strip() + s[end:], encoding="utf-8")


LINE_Y = 820
PITCH = 140


def strip_item(focused):
    w, h = (150, 225) if focused else (110, 165)
    x = (PITCH - 110) // 2 + (0 if focused else 0) if not focused else 15
    y = 40 + (165 - h) // 2
    o = 13
    parts = [f'<control type="image"><left>0</left><top>{LINE_Y - 700 - 4}</top><width>{PITCH}</width><height>8</height>'
             '<texture colordiffuse="l_route">common/white.png</texture></control>']
    if focused:
        parts += [f'<control type="image"><left>{x - o - 30}</left><top>{y - o - 16}</top><width>{w + 2 * o + 60}</width><height>{h + 2 * o + 64}</height>'
                  '<texture border="100" colordiffuse="shadow">sd/shadow_big.png</texture><visible>Control.HasFocus(500)</visible></control>',
                  f'<control type="image"><left>{x - o}</left><top>{y - o}</top><width>{w + 2 * o}</width><height>{h + 2 * o}</height>'
                  '<texture border="20" colordiffuse="ground">sd/ringf_fill.png</texture></control>',
                  f'<control type="image"><left>{x - o}</left><top>{y - o}</top><width>{w + 2 * o}</width><height>{h + 2 * o}</height>'
                  '<texture border="20" colordiffuse="ink">sd/ringf_6.png</texture><visible>Control.HasFocus(500)</visible></control>']
    parts += [f'<control type="image"><left>{x}</left><top>{y}</top><width>{w}</width><height>{h}</height>'
              '<texture colordiffuse="wash">common/white.png</texture></control>',
              f'<control type="label"><left>{x + 8}</left><top>{y + 8}</top><width>{w - 16}</width><height>80</height>'
              '<font>semi_20</font><textcolor>ink2</textcolor><aligny>top</aligny><wrapmultiline>true</wrapmultiline><label>$INFO[ListItem.Label]</label></control>',
              f'<control type="image"><left>{x}</left><top>{y}</top><width>{w}</width><height>{h}</height><aspectratio>scale</aspectratio><fadetime>120</fadetime>'
              f'<texture background="true" diffuse="sd/mask_{"164x246" if focused else "110x165"}.png">$VAR[ListItemArt]</texture></control>']
    if not focused:
        parts.append(f'<control type="image"><left>{x - 3}</left><top>{y - 3}</top><width>{w + 6}</width><height>{h + 6}</height>'
                     '<texture border="14" colordiffuse="hair_strong">sd/frame_o3.png</texture></control>')
    # watched: a filled stop under the poster; unwatched: an open stop
    sx = x + w // 2
    sy = y + h + 22
    parts += [f'<control type="image"><left>{sx - 11}</left><top>{sy - 11}</top><width>22</width><height>22</height>'
              '<texture colordiffuse="l_route">sd/disc_16.png</texture><visible>Integer.IsGreater(ListItem.PlayCount,0)</visible></control>']
    return "\n\t\t\t\t\t".join(parts)


LINE_VIEW = f"""<include name="VidView_500_Showcase">
		<control type="group">
			<visible>Control.IsVisible(500)</visible>
			<include>Anim_FadeVisible</include>
			<!-- the focused station: interchange ring (as on the station page) -->
			<control type="group">
				<visible>!ListItem.IsParentFolder</visible>
				<control type="image"><left>-8</left><top>112</top><width>502</width><height>667</height><texture border="100" colordiffuse="shadow">sd/shadow_big.png</texture></control>
				<control type="image"><left>64</left><top>162</top><width>358</width><height>523</height><texture border="24" colordiffuse="ground">sd/ring_centre_fill.png</texture></control>
				<control type="image"><left>64</left><top>162</top><width>358</width><height>523</height><texture border="24" colordiffuse="ink">sd/ring_centre.png</texture></control>
				<control type="image"><left>78</left><top>176</top><width>330</width><height>495</height><texture colordiffuse="wash">common/white.png</texture></control>
				<control type="label"><left>98</left><top>196</top><width>290</width><height>160</height><font>xb_28</font><textcolor>ink2</textcolor><aligny>top</aligny><wrapmultiline>true</wrapmultiline><label>$INFO[ListItem.Label]</label></control>
				<control type="image">
					<left>78</left><top>176</top><width>330</width><height>495</height>
					<aspectratio>scale</aspectratio><fadetime>120</fadetime>
					<texture background="true" diffuse="sd/mask_330x495.png">$VAR[ListItemArt]</texture>
				</control>
				<control type="label">
					<left>480</left><top>168</top><width>1376</width><height>30</height>
					<font>caps_21</font><textcolor>ink2</textcolor><aligny>top</aligny>
					<label>$VAR[St_Caption]</label>
				</control>
				<control type="textbox" id="5091">
					<left>480</left><top>200</top><width>1376</width><height>96</height>
					<font>disp_84</font><textcolor>clear</textcolor><label>$INFO[ListItem.Title]</label>
				</control>
				<control type="label">
					<left>476</left><top>196</top><width>1380</width><height>104</height>
					<font>disp_84</font><textcolor>ink</textcolor><label>$INFO[ListItem.Title]</label>
					<visible>!Integer.IsGreater(Container(5091).NumPages,1)</visible>
				</control>
				<control type="label">
					<left>478</left><top>210</top><width>1380</width><height>80</height>
					<font>disp_60</font><textcolor>ink</textcolor><label>$INFO[ListItem.Title]</label>
					<visible>Integer.IsGreater(Container(5091).NumPages,1)</visible>
				</control>
				<control type="grouplist">
					<left>480</left><top>308</top><width>1376</width><height>40</height>
					<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>
					<control type="label"><width max="420">auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor><label>$VAR[St_FactLead]</label></control>
					<control type="label"><width>34</width><height>40</height><font>semi_26</font><textcolor>hair_strong</textcolor><align>center</align><label>|</label><visible>Integer.IsGreater(ListItem.Duration,0) | String.IsEqual(ListItem.DBType,tvshow)</visible></control>
					<control type="label"><width>auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor><label>$VAR[St_FactTime]</label></control>
					<control type="label"><width>34</width><height>40</height><font>semi_26</font><textcolor>hair_strong</textcolor><align>center</align><label>|</label><visible>!String.IsEmpty(ListItem.MPAA)</visible></control>
					<control type="label"><width>auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor><label>$INFO[ListItem.MPAA]</label></control>
					<control type="label"><width>34</width><height>40</height><font>semi_26</font><textcolor>hair_strong</textcolor><align>center</align><label>|</label><visible>!String.IsEmpty(ListItem.Rating)</visible></control>
					<control type="label"><width>auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor><label>$INFO[ListItem.Rating,★ ,]</label></control>
					<control type="label"><width>34</width><height>40</height><font>semi_26</font><textcolor>hair_strong</textcolor><align>center</align><label>|</label></control>
					<control type="label"><width>auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor><label>$VAR[St_FactWatched]</label></control>
				</control>
				<control type="textbox">
					<left>480</left><top>372</top><width>1376</width><height>234</height>
					<font>reg_26</font><textcolor>body</textcolor>
					<label>$INFO[ListItem.Plot]</label>
					<autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>
				</control>
			</control>
			<control type="group">
				<left>480</left>
				<top>168</top>
				<width>1376</width>
				<height>200</height>
				<visible>ListItem.IsParentFolder</visible>
				<include>VidView_ParentInfo</include>
			</control>
			<!-- the line the films hang on -->
			<control type="image"><left>0</left><top>{LINE_Y - 4}</top><width>1920</width><height>8</height><texture colordiffuse="l_route">common/white.png</texture></control>
			<control type="fixedlist" id="500">
				<left>40</left>
				<top>700</top>
				<width>1840</width>
				<height>300</height>
				<orientation>horizontal</orientation>
				<focusposition>3</focusposition>
				<movement>0</movement>
				<preloaditems>2</preloaditems>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<onup>9000</onup>
				<ondown>noop</ondown>
				<viewtype label="31201">list</viewtype>
				<visible>Container.Content(movies) | Container.Content(sets)</visible>
				<itemlayout width="{PITCH}" height="300">
					{strip_item(False)}
				</itemlayout>
				<focusedlayout width="{PITCH + 40}" height="300">
					{strip_item(True)}
				</focusedlayout>
			</control>
			<control type="label">
				<left>64</left><top>1000</top><width>600</width><height>30</height>
				<font>semi_22</font><textcolor>ink2</textcolor>
				<label>$INFO[Container.CurrentItem] of $INFO[Container.NumItems]</label>
			</control>
			<control type="label">
				<left>656</left><top>1000</top><width>1200</width><height>30</height><align>right</align>
				<font>semi_22</font><textcolor>ink2</textcolor>
				<label>◀ ▶ ride the line   ·   OK play or station page   ·   hold OK for options   ·   ▲ filter and sort</label>
			</control>
		</control>
	</include>"""

if __name__ == "__main__":
    replace_include("Includes_Views_Video.xml", "VidView_500_Showcase", LINE_VIEW)
    print("Line view written")
