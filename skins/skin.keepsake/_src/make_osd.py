"""Rewrite the include half of 1080i/Includes_OSD.xml in Keepsake's language (the variables / expressions half,
from the Majan engine, stays as it is). Run after editing:  python skins/skin.keepsake/_src/make_osd.py

The OSD is "a slim black strip with the title in Fraunces, the progress as a pen line, and the times stamped in
orange LCD digits (21:47 -> 23:57)" (docs/concepts/round4/keepsake.md):
  OSD_Scrims        bottom ramp + top ramp (own fades, LESSONS 4)
  OSD_TopLine       kicker (state · type) left, LCD clock + label right
  OSD_Flag(s)       DM Mono tech words, no boxes
  OSD_TitleBlock    Fraunces title + DM Mono meta; LCD "now -> ends" on the right
  OSD_Track         dotted track, cache line, pen-stroke progress with a pen tick at the play position, chapter ticks
  OSD_SeekBubble    the seek time in LCD digits on a small dark tab, slid to Player.SeekBar (100 x 1 % slides)
  OSD_ProgressBlock track + elapsed / remaining in DM Mono (+ the bubble while seeking)
  OSD_BoxButton     an icon in a pen circle (PlayerControls), OSD_PlayButton the same for play/pause
  OSD_PenWord       a handwritten transport / option word with a fixed width (no judder), pen underline on focus
  OSD_TextButton    handwritten caption + DM Mono value (fixed width)
  OSD_InfoRow / OSD_SubtitleRow / OSD_BookmarkItem   process info rows, subtitle results, chapter prints
"""
from pathlib import Path
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

P = Path(__file__).resolve().parents[1] / "1080i" / "Includes_OSD.xml"
MARK = "\t<!-- ============================================================= textures -->"
TRACK_W = 1696
STEP = TRACK_W / 100


def bubble_slides():
    return "\n".join(f'\t\t<animation effect="slide" end="{STEP:.2f},0" time="0" condition="Integer.IsGreater(Player.SeekBar,{k})">Conditional</animation>'
                     for k in range(100))


TAIL = r'''	<!-- ============================================================= Keepsake OSD pieces (generated: _src/make_osd.py) -->
	<variable name="OSD_PlayWord">
		<value condition="Player.Paused | Player.Forwarding | Player.Rewinding">play</value>
		<value>pause</value>
	</variable>
	<variable name="OSD_FocusValue">
		<value condition="Control.HasFocus(70046)">subtitles  ·  [COLOR ink_bold]$VAR[OSD_SubtitleValue][/COLOR]</value>
		<value condition="Control.HasFocus(70049)">audio  ·  [COLOR ink_bold]$VAR[OSD_AudioValue]$INFO[VideoPlayer.AudioLanguage,  ·  ,][/COLOR]</value>
		<value condition="Control.HasFocus(70044)">chapters  ·  [COLOR ink_bold]$INFO[Player.Chapter]$INFO[Player.ChapterCount, of ,][/COLOR]$INFO[Player.ChapterName,  ·  ,]</value>
		<value condition="Control.HasFocus(87)">left / right to skip  ·  down for the words</value>
	</variable>
	<!-- fullscreen info: your history with what's playing -->
	<variable name="FSInfo_History">
		<value condition="Integer.IsEqual(VideoPlayer.PlayCount,1) + !String.IsEmpty(VideoPlayer.LastPlayed)">seen once before, on $VAR[KS_VP_Long] $VAR[KS_VP_Year]</value>
		<value condition="Integer.IsEqual(VideoPlayer.PlayCount,2) + !String.IsEmpty(VideoPlayer.LastPlayed)">seen twice before, the last time on $VAR[KS_VP_Long] $VAR[KS_VP_Year]</value>
		<value condition="Integer.IsGreater(VideoPlayer.PlayCount,2) + !String.IsEmpty(VideoPlayer.LastPlayed)">seen $INFO[VideoPlayer.PlayCount] times before, the last on $VAR[KS_VP_Long] $VAR[KS_VP_Year]</value>
		<value condition="!String.IsEmpty(VideoPlayer.LastPlayed)">picked up again, you last stopped on $VAR[KS_VP_Long]</value>
		<value condition="VideoPlayer.Content(movies) | VideoPlayer.Content(episodes)">the first time you're watching it</value>
	</variable>
	<variable name="OSD_EndsAMPM">
		<value condition="String.EndsWith(Player.FinishTime,PM)">pm</value>
		<value condition="String.EndsWith(Player.FinishTime,AM)">am</value>
	</variable>

	<include name="OSD_Scrims">
		<param name="bottom_h">520</param>
		<param name="top_h">220</param>
		<definition>
			<control type="image">
				<left>0</left>
				<bottom>0</bottom>
				<width>1920</width>
				<height>$PARAM[bottom_h]</height>
				<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
				<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
				<texture colordiffuse="shade">common/gradient_bottom.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>$PARAM[top_h]</height>
				<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
				<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
				<texture colordiffuse="shade_tab">common/gradient_top.png</texture>
			</control>
		</definition>
	</include>

	<include name="OSD_TopLine">
		<param name="kicker">$VAR[OSD_State]  ·  $VAR[OSD_Type]</param>
		<definition>
			<control type="label">
				<left>118</left>
				<top>69</top>
				<width>1100</width>
				<height>27</height>
				<font>lbl_20</font>
				<textcolor>label_hi</textcolor>
				<label>$PARAM[kicker]</label>
			</control>
			<include content="KS_Clock"><param name="label" value="now"/></include>
		</definition>
	</include>

	<include name="OSD_Flag">
		<param name="visible">true</param>
		<definition>
			<control type="label">
				<width>auto</width>
				<height>27</height>
				<font>lbln_20</font>
				<textcolor>label</textcolor>
				<label>$PARAM[label]</label>
				<visible>$PARAM[visible]</visible>
			</control>
		</definition>
	</include>
	<include name="OSD_Flags">
		<param name="top">0</param>
		<param name="align">right</param>
		<definition>
			<control type="grouplist">
				<left>112</left>
				<top>$PARAM[top]</top>
				<width>1696</width>
				<height>27</height>
				<orientation>horizontal</orientation>
				<align>$PARAM[align]</align>
				<itemgap>26</itemgap>
				<visible>Player.HasVideo</visible>
				<include content="OSD_Flag"><param name="label" value="$VAR[OSD_FlagResolution]"/><param name="visible" value="!String.IsEmpty(VideoPlayer.VideoResolution)"/></include>
				<include content="OSD_Flag"><param name="label" value="$VAR[OSD_FlagHDR]"/><param name="visible" value="!String.IsEmpty(VideoPlayer.HdrType)"/></include>
				<include content="OSD_Flag"><param name="label" value="$VAR[OSD_FlagVideoCodec]"/><param name="visible" value="!String.IsEmpty(VideoPlayer.VideoCodec)"/></include>
				<include content="OSD_Flag"><param name="label" value="$VAR[OSD_FlagAudio]"/><param name="visible" value="!String.IsEmpty(VideoPlayer.AudioCodec)"/></include>
			</control>
		</definition>
	</include>

	<!-- title (Fraunces 64) + meta; LCD "now -> ends" on the right. param top = title label top -->
	<include name="OSD_TitleBlock">
		<param name="top">776</param>
		<param name="text_shift">false</param>
		<param name="title_width">1180</param>
		<param name="flags">false</param>
		<param name="lcd">true</param>
		<definition>
			<control type="group">
				<left>0</left>
				<top>$PARAM[top]</top>
				<width>1920</width>
				<height>120</height>
				<control type="group">
					<animation effect="slide" end="300,0" time="0" condition="$PARAM[text_shift]">Conditional</animation>
					<control type="label">
						<left>108</left>
						<top>0</top>
						<width>$PARAM[title_width]</width>
						<height>84</height>
						<font>ttl_64</font>
						<textcolor>cream</textcolor>
						<label>$VAR[OSD_Title]</label>
					</control>
					<control type="label">
						<left>114</left>
						<top>84</top>
						<width>1180</width>
						<height>27</height>
						<font>lbl_20</font>
						<textcolor>label_hi</textcolor>
						<label>$VAR[OSD_Meta]</label>
					</control>
				</control>
				<control type="group">
					<visible>$PARAM[lcd] + Player.HasVideo + !String.IsEmpty(Player.FinishTime)</visible>
					<include content="KS_LCD34">
						<param name="label" value="$INFO[System.Time(hh:mm)]"/>
						<param name="left" value="1250"/>
						<param name="top" value="12"/>
						<param name="width" value="300"/>
						<param name="align" value="right"/>
					</include>
					<control type="image">
						<left>1566</left>
						<top>28</top>
						<width>48</width>
						<height>20</height>
						<texture colordiffuse="ink_soft">ks/pen_arrow_r.png</texture>
					</control>
					<include content="KS_LCD34">
						<param name="label" value="$INFO[Player.FinishTime]"/>
						<param name="left" value="1508"/>
						<param name="top" value="12"/>
						<param name="width" value="300"/>
						<param name="align" value="right"/>
					</include>
					<control type="label">
						<left>1250</left>
						<top>66</top>
						<width>300</width>
						<height>27</height>
						<align>right</align>
						<font>lbl_20</font>
						<textcolor>label</textcolor>
						<label>now</label>
					</control>
					<control type="label">
						<left>1408</left>
						<top>66</top>
						<width>400</width>
						<height>27</height>
						<align>right</align>
						<font>lbl_20</font>
						<textcolor>label</textcolor>
						<label>ends$VAR[OSD_EndsAMPM,  ·  ,]</label>
					</control>
				</control>
				<include content="OSD_Flags" condition="$PARAM[flags]">
					<param name="top" value="84"/>
				</include>
			</control>
		</definition>
	</include>

	<include name="OSD_BubbleSlide">
@@SLIDES@@
	</include>

	<!-- the seek target in LCD digits on a dark tab over the playhead. params: top, visible -->
	<include name="OSD_SeekBubble">
		<param name="top">0</param>
		<param name="visible">true</param>
		<definition>
			<control type="group">
				<left>32</left>
				<top>$PARAM[top]</top>
				<width>160</width>
				<height>44</height>
				<visible>$PARAM[visible]</visible>
				<include>OSD_BubbleSlide</include>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>160</width>
					<height>44</height>
					<texture border="12" colordiffuse="shade_tab">ks/print.png</texture>
				</control>
				<include content="KS_LCD26">
					<param name="label" value="$VAR[OSD_SeekTimeLabel]"/>
					<param name="left" value="0"/>
					<param name="top" value="5"/>
					<param name="width" value="160"/>
					<param name="align" value="center"/>
				</include>
			</control>
		</definition>
	</include>

	<!-- dotted track, cache, pen-stroke progress + tick, chapter ticks. params: top (track centre - 14) -->
	<include name="OSD_Track">
		<param name="top">0</param>
		<param name="track_h">4</param>
		<param name="track_color">rule_strong</param>
		<param name="cache_color">rule_strong</param>
		<param name="playhead_h">20</param>
		<param name="playhead_top">-8</param>
		<definition>
			<control type="group">
				<left>112</left>
				<top>$PARAM[top]</top>
				<width>1696</width>
				<height>28</height>
				<control type="image">
					<left>0</left>
					<top>12</top>
					<width>1696</width>
					<height>4</height>
					<aspectratio>center</aspectratio>
					<texture colordiffuse="dotted">ks/dots_h.png</texture>
				</control>
				<control type="progress">
					<left>0</left>
					<top>13</top>
					<width>1696</width>
					<height>2</height>
					<info>Player.ProgressCache</info>
					<texturebg colordiffuse="clear">common/white.png</texturebg>
					<midtexture colordiffuse="rule">common/white.png</midtexture>
					<visible>Player.SeekEnabled</visible>
				</control>
				<control type="progress">
					<left>0</left>
					<top>0</top>
					<width>1686</width>
					<height>28</height>
					<info>Player.SeekBar</info>
					<texturebg>ks/progress_bg_1686.png</texturebg>
					<midtexture colordiffuse="ink_bold">ks/pen_fill.png</midtexture>
					<righttexture colordiffuse="ink_bold">ks/pen_tick.png</righttexture>
				</control>
				<control type="ranges">
					<left>0</left>
					<top>4</top>
					<width>1696</width>
					<height>20</height>
					<texturebg>osd/slider_bg.png</texturebg>
					<lefttexture />
					<midtexture />
					<righttexture colordiffuse="stamp">osd/tick.png</righttexture>
					<info>Player.Chapters</info>
					<visible>$EXP[OSD_HasChapters]</visible>
				</control>
			</control>
		</definition>
	</include>

	<!-- track + elapsed / remaining (or the focused word's value). param top = track top -->
	<include name="OSD_ProgressBlock">
		<param name="top">902</param>
		<param name="bubble_visible">$EXP[OSD_SeekActive]</param>
		<definition>
			<control type="group">
				<left>0</left>
				<top>$PARAM[top]</top>
				<width>1920</width>
				<height>80</height>
				<include content="OSD_Track"><param name="top" value="0"/></include>
				<include content="OSD_SeekBubble">
					<param name="top" value="-52"/>
					<param name="visible" value="$PARAM[bubble_visible] + Player.SeekEnabled"/>
				</include>
				<control type="label">
					<left>114</left>
					<top>36</top>
					<width>600</width>
					<height>30</height>
					<font>mono_22</font>
					<textcolor>ink_bold</textcolor>
					<label>$VAR[OSD_SeekTimeLabel]</label>
				</control>
				<control type="label">
					<left>460</left>
					<top>36</top>
					<width>1000</width>
					<height>30</height>
					<align>center</align>
					<font>lbl_20</font>
					<textcolor>label</textcolor>
					<label>$VAR[OSD_FocusValue]</label>
				</control>
				<control type="label">
					<left>1108</left>
					<top>36</top>
					<width>700</width>
					<height>30</height>
					<align>right</align>
					<font>mono_22</font>
					<textcolor>label_hi</textcolor>
					<label>$INFO[Player.TimeRemaining,−,]$INFO[Player.Duration,  /  ,]</label>
				</control>
			</control>
		</definition>
	</include>

	<!-- a handwritten word in an OSD row: fixed width (labels never shift the row), pen underline on focus.
	     params: id, label, width, onclick, onclick2, onleft, onright, onup, visible -->
	<include name="OSD_PenWord">
		<param name="visible">true</param>
		<param name="onclick2">noop</param>
		<param name="onup">87</param>
		<param name="ondown">noop</param>
		<definition>
			<control type="button" id="$PARAM[id]">
				<width>$PARAM[width]</width>
				<height>74</height>
				<textoffsetx>4</textoffsetx>
				<font>hand_46</font>
				<textcolor>ink_soft</textcolor>
				<align>center</align>
				<include>KS_PenWordLook</include>
				<label>$PARAM[label]</label>
				<onclick>$PARAM[onclick]</onclick>
				<onclick>$PARAM[onclick2]</onclick>
				<onleft>$PARAM[onleft]</onleft>
				<onright>$PARAM[onright]</onright>
				<onup>$PARAM[onup]</onup>
				<ondown>$PARAM[ondown]</ondown>
				<visible>$PARAM[visible]</visible>
			</control>
		</definition>
	</include>

	<!-- an icon in a pen circle (PlayerControls). params: id, icon, onclick, onclick2, onleft, onright, visible -->
	<include name="OSD_BoxButton">
		<param name="visible">true</param>
		<param name="onclick2">noop</param>
		<param name="icon_size">osd_box_icon</param>
		<param name="icon_pos">osd_box_icon_pos</param>
		<param name="icon_color">ink_bold</param>
		<definition>
			<control type="group">
				<top>8</top>
				<left>8</left>
				<width>osd_box</width>
				<height>osd_box</height>
				<visible>$PARAM[visible]</visible>
				<control type="button" id="$PARAM[id]">
					<left>0</left>
					<top>0</top>
					<width>osd_box</width>
					<height>osd_box</height>
					<label></label>
					<texturefocus colordiffuse="ink_bold">ks/pen_circle.png</texturefocus>
					<texturenofocus />
					<onclick>$PARAM[onclick]</onclick>
					<onclick>$PARAM[onclick2]</onclick>
					<onleft>$PARAM[onleft]</onleft>
					<onright>$PARAM[onright]</onright>
					<onup>87</onup>
					<ondown>noop</ondown>
				</control>
				<control type="image">
					<left>$PARAM[icon_pos]</left>
					<top>$PARAM[icon_pos]</top>
					<width>$PARAM[icon_size]</width>
					<height>$PARAM[icon_size]</height>
					<texture colordiffuse="$PARAM[icon_color]">$PARAM[icon]</texture>
				</control>
			</control>
		</definition>
	</include>
	<include name="OSD_PlayButton">
		<param name="onleft">noop</param>
		<param name="onright">noop</param>
		<definition>
			<control type="group">
				<top>8</top>
				<left>8</left>
				<width>osd_box</width>
				<height>osd_box</height>
				<visible>Player.PauseEnabled</visible>
				<control type="button" id="602">
					<left>0</left>
					<top>0</top>
					<width>osd_box</width>
					<height>osd_box</height>
					<label></label>
					<texturefocus colordiffuse="ink_bold">ks/pen_circle.png</texturefocus>
					<texturenofocus colordiffuse="ink_faint">ks/pen_circle.png</texturenofocus>
					<onclick>PlayerControl(Play)</onclick>
					<onleft>$PARAM[onleft]</onleft>
					<onright>$PARAM[onright]</onright>
					<onup>87</onup>
					<ondown>noop</ondown>
				</control>
				<control type="image">
					<left>osd_box_icon_pos</left>
					<top>osd_box_icon_pos</top>
					<width>osd_box_icon</width>
					<height>osd_box_icon</height>
					<texture colordiffuse="ink_bold">$VAR[OSD_PlayIcon]</texture>
				</control>
			</control>
		</definition>
	</include>

	<!-- handwritten caption + DM Mono value, fixed width. params: id, width, caption, value, onclick, onleft, onright, visible -->
	<include name="OSD_TextButton">
		<param name="visible">true</param>
		<definition>
			<control type="group">
				<top>0</top>
				<width>$PARAM[width]</width>
				<height>96</height>
				<visible>$PARAM[visible]</visible>
				<control type="button" id="$PARAM[id]">
					<left>0</left>
					<top>0</top>
					<width>$PARAM[width]</width>
					<height>74</height>
					<textoffsetx>4</textoffsetx>
					<font>hand_46</font>
					<textcolor>ink_soft</textcolor>
					<include>KS_PenWordLook</include>
					<label>[LOWERCASE]$PARAM[caption][/LOWERCASE]</label>
					<onclick>$PARAM[onclick]</onclick>
					<onleft>$PARAM[onleft]</onleft>
					<onright>$PARAM[onright]</onright>
					<onup>87</onup>
					<ondown>noop</ondown>
				</control>
				<control type="label">
					<left>6</left>
					<top>70</top>
					<width>$PARAM[width]</width>
					<height>27</height>
					<font>lbln_20</font>
					<textcolor>label</textcolor>
					<label>$PARAM[value]</label>
				</control>
			</control>
		</definition>
	</include>

	<!-- key / value row (process info). params: key, value, visible -->
	<include name="OSD_InfoRow">
		<param name="visible">true</param>
		<definition>
			<control type="group">
				<width>860</width>
				<height>44</height>
				<visible>$PARAM[visible]</visible>
				<control type="label">
					<left>0</left>
					<top>0</top>
					<width>240</width>
					<height>40</height>
					<font>lbl_20</font>
					<textcolor>label</textcolor>
					<label>$PARAM[key]</label>
				</control>
				<control type="label">
					<left>240</left>
					<top>0</top>
					<width>620</width>
					<height>40</height>
					<font>mono_20</font>
					<textcolor>ink_bold</textcolor>
					<label>$PARAM[value]</label>
				</control>
				<control type="image">
					<left>0</left>
					<top>40</top>
					<width>860</width>
					<height>4</height>
					<aspectratio>center</aspectratio>
					<texture colordiffuse="rule">ks/dots_h.png</texture>
				</control>
			</control>
		</definition>
	</include>

	<!-- one DialogSubtitles result (696 x 84). param focused -->
	<include name="OSD_SubtitleRow">
		<param name="focused">false</param>
		<definition>
			<control type="label">
				<left>16</left>
				<top>24</top>
				<width>60</width>
				<height>36</height>
				<align>center</align>
				<font>mono_22</font>
				<textcolor>stamp</textcolor>
				<label>[UPPERCASE]$INFO[ListItem.Thumb][/UPPERCASE]</label>
			</control>
			<control type="label">
				<left>90</left>
				<top>10</top>
				<width>480</width>
				<height>38</height>
				<font>ttt_24</font>
				<textcolor>ink_bold</textcolor>
				<label>$INFO[ListItem.Label2]</label>
				<scroll>$PARAM[focused]</scroll>
			</control>
			<control type="label">
				<left>90</left>
				<top>46</top>
				<width>480</width>
				<height>27</height>
				<font>lbl_20</font>
				<textcolor>label</textcolor>
				<label>$INFO[ListItem.Label]$INFO[ListItem.ActualIcon,  ·  rating , / 5]</label>
			</control>
			<control type="label">
				<left>580</left>
				<top>28</top>
				<width>100</width>
				<height>27</height>
				<align>right</align>
				<font>lbl_20</font>
				<textcolor>label_hi</textcolor>
				<label>$VAR[OSD_SubBadges]</label>
			</control>
			<control type="image">
				<left>0</left>
				<top>80</top>
				<width>696</width>
				<height>4</height>
				<aspectratio>center</aspectratio>
				<texture colordiffuse="rule">ks/dots_h.png</texture>
			</control>
		</definition>
	</include>
	<variable name="OSD_SubBadges">
		<value condition="ListItem.Property(sync) + ListItem.Property(hearing_imp)">sync · hi</value>
		<value condition="ListItem.Property(sync)">sync</value>
		<value condition="ListItem.Property(hearing_imp)">hi</value>
	</variable>

	<!-- one chapter print (item 344 x 290; photo 300 x 169 + 10 border at 12,12) -->
	<include name="OSD_BookmarkItem">
		<param name="label_color">ink2</param>
		<definition>
			<control type="image">
				<left>9</left>
				<top>9</top>
				<width>326</width>
				<height>195</height>
				<texture border="12" colordiffuse="print">ks/print.png</texture>
			</control>
			<control type="image">
				<left>22</left>
				<top>22</top>
				<width>300</width>
				<height>169</height>
				<texture colordiffuse="paper_raised">common/white.png</texture>
			</control>
			<control type="label">
				<left>22</left>
				<top>22</top>
				<width>300</width>
				<height>169</height>
				<align>center</align>
				<aligny>center</aligny>
				<font>mono_22</font>
				<textcolor>label</textcolor>
				<label>$INFO[ListItem.Label2]</label>
				<visible>String.IsEmpty(ListItem.Art(thumb))</visible>
			</control>
			<control type="image">
				<left>22</left>
				<top>22</top>
				<width>300</width>
				<height>169</height>
				<aspectratio>scale</aspectratio>
				<fadetime>120</fadetime>
				<texture background="true">$INFO[ListItem.Art(thumb)]</texture>
				<visible>!String.IsEmpty(ListItem.Art(thumb))</visible>
			</control>
			<control type="label">
				<left>12</left>
				<top>212</top>
				<width>320</width>
				<height>44</height>
				<font>hand_34</font>
				<textcolor>$PARAM[label_color]</textcolor>
				<label>$INFO[ListItem.Label]</label>
			</control>
			<control type="label">
				<left>14</left>
				<top>254</top>
				<width>320</width>
				<height>27</height>
				<font>mono_20</font>
				<textcolor>label</textcolor>
				<label>$INFO[ListItem.Label2]</label>
			</control>
		</definition>
	</include>
</includes>
'''


def main():
    s = P.read_text(encoding="utf-8")
    i = s.index(MARK) if MARK in s else s.index("\t<!-- ============================================================= Keepsake OSD pieces")
    s = s[:i] + TAIL.replace("@@SLIDES@@", bubble_slides())
    P.write_text(finish_xml(s), encoding="utf-8", newline="\n")
    print("wrote", P)


if __name__ == "__main__":
    main()
