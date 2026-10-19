"""One-off restyle pass (2026-10-19): library header + View 50 (the A-Z Index) in the Six Degrees language.

View 50 = "Index": the library as one vertical line; every row is a station (a stop on a grey line, filled
once watched, a half stop while in progress); the focused row is an ink pill and its stop turns into an
interchange ring. Right: the focused item in an interchange ring with title, facts and plot.
Video header: wordmark + route crumb (Home -> page) + left-aligned, fixed-width filter pills (rule 5;
the sort pill, whose label changes, is last so nothing moves).
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


ROW = 66
LINE_X = 104


def index_row(focused):
    """Item layout for the Index. Coordinates relative to the row; list is 1144 wide at x 40."""
    lid = "50"
    f = focused
    parts = []
    # the line (always) and the stop
    parts.append(f'<control type="image"><left>{LINE_X - 4}</left><top>0</top><width>8</width><height>{ROW}</height>'
                 '<texture colordiffuse="hair_strong">common/white.png</texture></control>')
    if f:
        parts.append(f'<control type="image"><left>24</left><top>5</top><width>1120</width><height>{ROW - 10}</height>'
                     f'<texture border="28" colordiffuse="ink">sd/pill_56.png</texture><visible>Control.HasFocus({lid})</visible></control>')
    # stop: white disc + grey ring; watched = filled; in progress = ink ring
    c = ROW // 2
    for vis, ring, fill in (
            ("!ListItem.IsResumable + !Integer.IsGreater(ListItem.PlayCount,0)", "l_route", "white"),
            ("Integer.IsGreater(ListItem.PlayCount,0) + !ListItem.IsResumable", "l_route", "l_route"),
            ("ListItem.IsResumable", "ink", "white")):
        v = vis + (f" + !Control.HasFocus({lid})" if f else "")
        parts.append(f'<control type="image"><left>{LINE_X - 15}</left><top>{c - 15}</top><width>30</width><height>30</height>'
                     f'<texture colordiffuse="{fill}">sd/disc_24.png</texture><visible>{v}</visible></control>')
        parts.append(f'<control type="image"><left>{LINE_X - 15}</left><top>{c - 15}</top><width>30</width><height>30</height>'
                     f'<texture colordiffuse="{ring}">sd/ring_24_6.png</texture><visible>{v}</visible></control>')
    if f:
        parts.append(f'<control type="image"><left>{LINE_X - 19}</left><top>{c - 19}</top><width>38</width><height>38</height>'
                     f'<texture colordiffuse="ink">sd/disc_32.png</texture><visible>Control.HasFocus({lid})</visible></control>')
        parts.append(f'<control type="image"><left>{LINE_X - 19}</left><top>{c - 19}</top><width>38</width><height>38</height>'
                     f'<texture colordiffuse="white">sd/ring_32_8.png</texture><visible>Control.HasFocus({lid})</visible></control>')
    # selected (check) items in pickers keep a check instead of the label offset
    tl = 140
    for col, font, vis in (("ink", "semi_26", f"!Control.HasFocus({lid})" if f else "true"),
                           ("white", "xb_26", f"Control.HasFocus({lid})")):
        if not f and col == "white":
            continue
        parts.append(f'<control type="label"><left>{tl}</left><top>0</top><width>820</width><height>{ROW}</height>'
                     f"<font>{font}</font><textcolor>{col}</textcolor><selectedcolor>{col}</selectedcolor>"
                     f"<label>$INFO[ListItem.Label]</label><visible>{vis}</visible></control>")
        parts.append(f'<control type="label"><left>860</left><top>0</top><width>250</width><height>{ROW}</height><align>right</align>'
                     f"<font>semi_22</font><textcolor>{'ink2' if col == 'ink' else 'white'}</textcolor><selectedcolor>{'ink2' if col == 'ink' else 'white'}</selectedcolor>"
                     f"<label>$INFO[ListItem.Label2]</label><visible>{vis}</visible></control>")
    return "\n\t\t\t\t\t".join(parts)


VIEW50 = f"""<include name="View_50_List">
		<control type="group">
			<visible>Control.IsVisible(50)</visible>
			<include>Anim_VisibleFade</include>
			<!-- the line runs the full height behind the list -->
			<control type="image">
				<left>{40 + LINE_X - 4}</left>
				<top>168</top>
				<width>8</width>
				<height>870</height>
				<texture colordiffuse="hair_strong">common/white.png</texture>
			</control>
			<control type="list" id="50">
				<left>40</left>
				<top>170</top>
				<width>1144</width>
				<height>858</height>
				<onup>9000</onup>
				<ondown>50</ondown>
				<onleft>9000</onleft>
				<onright>60</onright>
				<pagecontrol>60</pagecontrol>
				<scrolltime tween="cubic" easing="out">200</scrolltime>
				<viewtype label="31070">list</viewtype>
				<itemlayout width="1144" height="{ROW}">
					{index_row(False)}
				</itemlayout>
				<focusedlayout width="1144" height="{ROW}">
					{index_row(True)}
				</focusedlayout>
			</control>
			<include content="SD_Scrollbar">
				<param name="id" value="60"/>
				<param name="left" value="1204"/>
				<param name="top" value="170"/>
				<param name="height" value="858"/>
				<param name="onleft" value="50"/>
				<param name="onright" value="50"/>
			</include>
			<!-- focused item: interchange ring (posters) or the plain artwork (covers, thumbs) -->
			<control type="group">
				<left>1264</left>
				<top>170</top>
				<control type="group">
					<visible>!String.IsEmpty(ListItem.Art(poster)) | !String.IsEmpty(ListItem.Art(tvshow.poster))</visible>
					<control type="image"><left>-86</left><top>-64</top><width>472</width><height>622</height><texture border="100" colordiffuse="shadow">sd/shadow_big.png</texture></control>
					<control type="image"><left>-14</left><top>-14</top><width>328</width><height>478</height><texture border="24" colordiffuse="ground">sd/ring_centre_fill.png</texture></control>
					<control type="image"><left>-14</left><top>-14</top><width>328</width><height>478</height><texture border="24" colordiffuse="ink">sd/ring_centre.png</texture></control>
					<control type="image"><left>0</left><top>0</top><width>300</width><height>450</height><texture colordiffuse="wash">common/white.png</texture></control>
					<control type="image">
						<left>0</left><top>0</top><width>300</width><height>450</height>
						<aspectratio>scale</aspectratio><fadetime>120</fadetime>
						<texture background="true" diffuse="sd/mask_300x450.png">$VAR[ListItemArt]</texture>
					</control>
				</control>
				<control type="image">
					<left>0</left><top>0</top><width>592</width><height>450</height>
					<aspectratio align="left" aligny="top">keep</aspectratio><fadetime>120</fadetime>
					<texture background="true">$VAR[ListItemArt]</texture>
					<visible>String.IsEmpty(ListItem.Art(poster)) + String.IsEmpty(ListItem.Art(tvshow.poster))</visible>
				</control>
				<control type="label">
					<left>0</left><top>486</top><width>592</width><height>44</height>
					<font>xb_30</font><textcolor>ink</textcolor>
					<label>$INFO[ListItem.Label]</label>
				</control>
				<control type="label">
					<left>0</left><top>532</top><width>592</width><height>32</height>
					<font>semi_22</font><textcolor>ink2</textcolor>
					<label>$INFO[ListItem.Year]$INFO[ListItem.Duration(m), · , min]$INFO[ListItem.Rating, · ★ ,]$INFO[ListItem.Genre, · ,]</label>
				</control>
				<control type="textbox">
					<left>0</left><top>578</top><width>592</width><height>136</height>
					<font>reg_24</font><textcolor>body</textcolor>
					<label>$INFO[ListItem.Plot]</label>
					<autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll>
				</control>
			</control>
		</control>
	</include>"""


def pill_btn(cid, width, label, extra):
    w = f"<width>{width}</width>" if width else "<width>auto</width>"
    return f"""<control type="button" id="{cid}">
				{w}
				<height>44</height>
				<font>semi_22</font>
				<textcolor>ink2</textcolor>
				<focusedcolor>white</focusedcolor>
				<align>center</align>
				<textoffsetx>18</textoffsetx>
				<texturefocus border="22" colordiffuse="ink">sd/pill_46.png</texturefocus>
				<label>{label}</label>
				{extra}
			</control>"""


HEADER = f"""<include name="VidView_Header">
		<include content="SD_PageHeader">
			<param name="title" value="$VAR[VidView_Title]"/>
			<param name="sub" value="$VAR[VidView_Sub]"/>
		</include>
		<include>SD_Clock</include>
		<control type="grouplist" id="9000">
			<left>900</left>
			<top>66</top>
			<width>800</width>
			<height>44</height>
			<orientation>horizontal</orientation>
			<itemgap>6</itemgap>
			<onup>noop</onup>
			<ondown condition="$EXP[VidView_HasNextUp]">9310</ondown>
			<ondown condition="!$EXP[VidView_HasNextUp]">50</ondown>
			<onleft>noop</onleft>
			<onright>noop</onright>
			<onback>50</onback>
			{pill_btn(9321, 150, "All $VAR[VidView_CountAll]", '''<textcolor>$VAR[VidView_ColNavAll]</textcolor>
				<texturenofocus border="22" colordiffuse="ink">$VAR[VidView_TexNavAll]</texturenofocus>
				<onclick condition="$EXP[VidView_IsInProgressTV]">Action(ParentDir)</onclick>
				<onclick condition="!$EXP[VidView_IsInProgressTV] + System.Setting(hidewatched)">SendClick(14)</onclick>
				<visible>$EXP[VidView_IsLibraryVideo] | $EXP[VidView_IsInProgressTV]</visible>''')}
			{pill_btn(9322, 196, "Unwatched $VAR[VidView_CountUnwatched]", '''<textcolor>$VAR[VidView_ColNavUnwatched]</textcolor>
				<texturenofocus border="22" colordiffuse="ink">$VAR[VidView_TexNavUnwatched]</texturenofocus>
				<onclick condition="!System.Setting(hidewatched)">SendClick(14)</onclick>
				<visible>Container.Content(movies) | Container.Content(sets) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(musicvideos)</visible>''')}
			{pill_btn(9323, 186, "In progress $VAR[VidView_CountInProgress]", '''<textcolor>$VAR[VidView_ColNavInProgress]</textcolor>
				<texturenofocus border="22" colordiffuse="ink">$VAR[VidView_TexNavInProgress]</texturenofocus>
				<onclick condition="!$EXP[VidView_IsInProgressTV]">Container.Update(videodb://inprogresstvshows/)</onclick>
				<visible>$EXP[VidView_IsTVRoot] | $EXP[VidView_IsInProgressTV]</visible>''')}
			{pill_btn(9326, 226, "View · $INFO[Container.Viewmode]", '''<texturenofocus />
				<onclick>Container.NextViewMode</onclick>
				<visible>Integer.IsGreater(Container.ViewCount,1)</visible>''')}
			{pill_btn(9324, 0, "Sort · $INFO[Container.SortMethod] $VAR[VidView_SortArrow]", '''<texturenofocus />
				<onclick>SendClick(3)</onclick>
				<visible>Control.IsEnabled(3)</visible>''')}
			{pill_btn(9325, 0, "$VAR[VidView_SortArrow]", '''<texturenofocus />
				<onclick>SendClick(4)</onclick>
				<visible>false</visible>''')}
		</control>
		<control type="button" id="3">
			<description>Sort by (Kodi)</description>
			<include>SD_Hidden</include>
		</control>
		<control type="button" id="4">
			<description>Sort order (Kodi)</description>
			<include>SD_Hidden</include>
		</control>
	</include>"""

if __name__ == "__main__":
    replace_include("Includes_Views.xml", "View_50_List", VIEW50)
    replace_include("Includes_Views_Video.xml", "VidView_Header", HEADER)
    p = X / "Includes_Views_Video.xml"
    s = p.read_text(encoding="utf-8")
    # active filter: an ink outline pill instead of Majan's underline
    s = s.replace("<value condition=\"$EXP[VidView_NavActiveAll]\">vidview/underline.png</value>",
                  "<value condition=\"$EXP[VidView_NavActiveAll]\">sd/pill_46_o3.png</value>")
    s = s.replace("<value condition=\"System.Setting(hidewatched)\">vidview/underline.png</value>",
                  "<value condition=\"System.Setting(hidewatched)\">sd/pill_46_o3.png</value>")
    s = re.sub(r'(<variable name="VidView_TexNavInProgress">\s*<value condition="[^"]*">)vidview/underline.png', r"\1sd/pill_46_o3.png", s)
    p.write_text(s, encoding="utf-8")
    print("restyled View 50 + video header")
