"""Generate the playback chrome: VideoOSD.xml, DialogSeekBar.xml, DialogFullScreenInfo.xml (skins/skin.fold/1080i).
    python skins/skin.fold/_src/make_osd.py

Fold: the OSD is a cream strip that folds up from the bottom edge (window-level rotatex about y 1080,
Includes_Animations.xml Anim_OSDSlideUp) with the title, a perforated progress line whose playhead is a punched
hole, the times, and the transport words. The seek bar is a slim strip of the same paper; the playing info is
a note with the poster tipped in.

VideoOSD ids (Majan engine, Estuary Omega convention): 602 play/pause (default), 603 stop, 600 previous, 607 next,
70044 chapters, 70049 audio, 70046 subtitles, 70048 video settings, 70043 info, 70051 player stats, 87 seek
stepper (hidden: Up from the words), 200 the words group. Word order = Omar's rule 6: Play/Pause, Stop,
Previous/Next (gated), Chapters, Audio, Subtitles, then Video, Info, Player. Widths are fixed (widest label,
PIL-measured), the row is left-aligned, so nothing moves when Pause turns into Play.
DialogSeekBar: 401 the seek slider Kodi drives. DialogFullScreenInfo: 999 the full-screen focus button.
"""
from pathlib import Path
from PIL import ImageFont
import re
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

ROOT = Path(__file__).resolve().parents[1]
X = ROOT / "1080i"
RM = "Skin.HasSetting(fold.reducemotion)"
FONT = ImageFont.truetype(str(ROOT / "fonts" / "FoldWord-ExtraBold.ttf"), 26)
STRIP_Y = 744


def w(*labels):
    m = max(FONT.getlength(l.upper()) for l in labels)
    return round(m) + 2 * 14 + max(len(l) for l in labels) + 4


def selcol(x):
    return re.sub(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)",
                  lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", x)


def strip(top, height, turn=True):
    """The cream strip with its crease along the top edge and a soft shadow on the picture above it."""
    turn_xml = f"""
			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>{height}</height>
				<texture>fold/strip_turn.png</texture>
				<visible>!{RM}</visible>
				<animation type="WindowOpen"><effect type="fade" start="100" end="0" time="300" tween="sine" easing="in"/></animation>
				<animation type="WindowClose"><effect type="fade" start="0" end="100" time="200"/></animation>
			</control>""" if turn else ""
    return f"""
			<control type="image">
				<left>0</left>
				<top>{top - 180}</top>
				<width>1920</width>
				<height>180</height>
				<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation>
				<animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
				<texture colordiffuse="66000000">common/gradient_bottom.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>{height}</height>
				<texture colordiffuse="cream">common/white.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>{height}</height>
				<texture>fold/tooth_cream.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>{height}</height>
				<texture>fold/strip_shade.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>{top}</top>
				<width>1920</width>
				<height>4</height>
				<texture colordiffuse="$VAR[FoldAccent]">common/white.png</texture>
			</control>{turn_xml}"""


def perforation(top, info="Player.Progress", nib=True, slider_id=None):
    nib_xml = f"""
			<control type="slider"{f' id="{slider_id}"' if slider_id else ''}>
				<left>{96 - 17}</left>
				<top>{top - 15}</top>
				<width>{1728 + 34}</width>
				<height>34</height>
				<texturesliderbar>fold/clear34.png</texturesliderbar>
				<textureslidernib>fold/punch_nib.png</textureslidernib>
				<textureslidernibfocus>fold/punch_nib.png</textureslidernibfocus>
				<info>{info}</info>
				<visible>Player.HasMedia</visible>
			</control>""" if nib else ""
    return f"""
			<control type="image">
				<left>96</left>
				<top>{top}</top>
				<width>1728</width>
				<height>3</height>
				<aspectratio align="left">center</aspectratio>
				<texture colordiffuse="rule_strong">fold/perf.png</texture>
			</control>
			<control type="progress">
				<left>96</left>
				<top>{top - 1}</top>
				<width>1728</width>
				<height>5</height>
				<texturebg />
				<lefttexture />
				<midtexture colordiffuse="$VAR[FoldAccent]">common/white.png</midtexture>
				<righttexture />
				<info>{info}</info>
			</control>{nib_xml}"""


WORDS = [
    # id, label(s), onclick, visible, onleft, onright
    (602, "$VAR[OSD_PlayWord]", ("Pause", "Play"), "PlayerControl(Play)", "true"),
    (603, "Stop", ("Stop",), "PlayerControl(Stop)", "true"),
    (600, "Previous", ("Previous",), "PlayerControl(Previous)", "$EXP[OSD_HasPrevNext]"),
    (607, "Next", ("Next",), "PlayerControl(Next)", "$EXP[OSD_HasPrevNext]"),
    (70044, "Chapters", ("Chapters",), "ActivateWindow(videobookmarks)", "Player.SeekEnabled + !VideoPlayer.Content(livetv)"),
    (70049, "Audio", ("Audio",), "ActivateWindow(osdaudiosettings)", "true"),
    (70046, "Subtitles", ("Subtitles",), "ActivateWindow(osdsubtitlesettings)", "Player.HasVideo"),
    (70048, "Video", ("Video",), "ActivateWindow(osdvideosettings)", "Player.HasVideo"),
    (70043, "Info", ("Info",), "Action(Info,fullscreenvideo)", "true"),
    (70051, "Player", ("Player",), "Action(PlayerProcessInfo)", "true"),
]


def words_row():
    out = []
    ids = [wd[0] for wd in WORDS]
    for i, (bid, label, labels, click, vis) in enumerate(WORDS):
        left = ids[i - 1]
        right = ids[(i + 1) % len(ids)]
        out.append(f"""
				<control type="button" id="{bid}">
					<width>{w(*labels)}</width>
					<height>56</height>
					<label>{label}</label>
					<font>word_26</font>
					<textcolor>ink</textcolor>
					<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
					<align>center</align>
					<textoffsetx>0</textoffsetx>
					<texturefocus border="6" colordiffuse="$VAR[FoldAccent]">fold/chip.png</texturefocus>
					<texturenofocus />
					<onclick>{click}</onclick>
					<onup condition="Player.SeekEnabled">87</onup>
					<visible>{vis}</visible>
				</control>""")
        if i in (1, 3, 6):
            dvis = "$EXP[OSD_HasPrevNext]" if i == 3 else "true"
            out.append(f"""
				<control type="label" id="{9500 + i}">
					<width>24</width>
					<height>56</height>
					<align>center</align>
					<font>word_26</font>
					<textcolor>$VAR[FoldAccentInk]</textcolor>
					<label>·</label>
					<visible>{dvis}</visible>
				</control>""")
    return "".join(out)


def video_osd():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_osd.py - edit the generator, not this file. -->
<!--{__doc__}-->
<window>
	<onload condition="!Player.PauseEnabled">SetFocus(603)</onload>
	<defaultcontrol always="true">602</defaultcontrol>
	<include>Anim_OSDSlideUp</include>
	<controls>
		<control type="group">
			<visible>!$EXP[OSD_PanelOpen]</visible>
			<include>Anim_FadeVisible</include>
			<!-- the clock on a cream tab hanging from the top edge -->
			<control type="group">
				<left>1628</left>
				<top>0</top>
				<include>Anim_TopStrip</include>
				<control type="image">
					<left>-48</left>
					<top>-48</top>
					<width>292</width>
					<height>162</height>
					<texture>fold/tab_shadow.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>196</width>
					<height>66</height>
					<texture colordiffuse="cream">fold/tab.png</texture>
				</control>
				<control type="label">
					<left>0</left>
					<top>14</top>
					<width>196</width>
					<height>40</height>
					<align>center</align>
					<font>num_26</font>
					<textcolor>ink</textcolor>
					<label>$VAR[ClockLabel]</label>
				</control>
			</control>
{strip(STRIP_Y, 1080 - STRIP_Y)}
			<control type="label">
				<left>96</left>
				<top>{STRIP_Y + 24}</top>
				<width>1100</width>
				<height>32</height>
				<font>caps_20_b</font>
				<textcolor>$VAR[FoldAccentInk]</textcolor>
				<label>$VAR[OSD_State][COLOR cap2]   $VAR[OSD_Type][/COLOR]</label>
			</control>
			<control type="label">
				<left>96</left>
				<top>{STRIP_Y + 52}</top>
				<width>1100</width>
				<height>66</height>
				<font>head_50</font>
				<textcolor>ink</textcolor>
				<label>$VAR[OSD_Title]</label>
			</control>
			<control type="label">
				<left>96</left>
				<top>{STRIP_Y + 114}</top>
				<width>1100</width>
				<height>40</height>
				<font>light_30</font>
				<textcolor>ink2</textcolor>
				<label>$VAR[OSD_FoldMeta]</label>
			</control>
			<control type="label">
				<left>1224</left>
				<top>{STRIP_Y + 40}</top>
				<width>600</width>
				<height>50</height>
				<align>right</align>
				<font>num_38</font>
				<textcolor>ink</textcolor>
				<label>$VAR[OSD_SeekTimeLabel]</label>
			</control>
			<control type="label">
				<left>1024</left>
				<top>{STRIP_Y + 96}</top>
				<width>800</width>
				<height>32</height>
				<align>right</align>
				<font>caps_20</font>
				<textcolor>cap</textcolor>
				<label>$VAR[OSD_TimeLine]</label>
			</control>
{perforation(STRIP_Y + 176)}
			<!-- seek stepper (Up from the words): Left / Right skip, the perforation glows while it has focus -->
			<control type="button" id="87">
				<include>Fold_Hidden</include>
				<onup>noop</onup>
				<ondown>200</ondown>
				<onleft>StepBack</onleft>
				<onright condition="!Player.Paused">StepForward</onright>
				<onright condition="Player.Paused">PlayerControl(FrameAdvance(1))</onright>
				<visible>Player.SeekEnabled</visible>
			</control>
			<control type="image">
				<left>96</left>
				<top>{STRIP_Y + 168}</top>
				<width>1728</width>
				<height>18</height>
				<texture border="6" colordiffuse="33ffffff">fold/chip.png</texture>
				<visible>Control.HasFocus(87)</visible>
			</control>
			<control type="label">
				<left>96</left>
				<top>{STRIP_Y + 140}</top>
				<width>1728</width>
				<height>30</height>
				<font>caps_20_b</font>
				<textcolor>$VAR[FoldAccentInk]</textcolor>
				<label>← skip back · skip on →</label>
				<align>center</align>
				<visible>Control.HasFocus(87)</visible>
			</control>
			<!-- the words -->
			<control type="grouplist" id="200">
				<left>82</left>
				<top>{STRIP_Y + 210}</top>
				<width>1756</width>
				<height>56</height>
				<orientation>horizontal</orientation>
				<itemgap>4</itemgap>
				<onleft>70051</onleft>
				<onright>602</onright>
				<onup condition="Player.SeekEnabled">87</onup>{words_row()}
			</control>
			<control type="grouplist">
				<left>96</left>
				<top>{STRIP_Y + 286}</top>
				<width>1100</width>
				<height>32</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<include content="Fold_KeyHint"><param name="key" value="↑"/><param name="label" value="Seek"/><param name="visible" value="Player.SeekEnabled"/></include>
				<include content="Fold_KeyHint"><param name="key" value="← →"/><param name="label" value="The words"/></include>
				<include content="Fold_KeyHint"><param name="key" value="BACK"/><param name="label" value="Fold it away"/></include>
			</control>
			<control type="label">
				<left>1124</left>
				<top>{STRIP_Y + 286}</top>
				<width>700</width>
				<height>32</height>
				<align>right</align>
				<font>caps_20</font>
				<textcolor>cap</textcolor>
				<label>$VAR[OSD_WordInfo]</label>
			</control>
		</control>
	</controls>
</window>
"""


def seekbar():
    top = 952
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_osd.py. Seek bar: a slim strip of the OSD paper. Kodi id 401 = the seek slider. -->
<window>
	<visible>Window.IsActive(fullscreenvideo)</visible>
	<visible>![Window.IsActive(sliderdialog) | Window.IsActive(pvrosdchannels) | Window.IsActive(pvrchannelguide) | Window.IsActive(pvrguideinfo)]</visible>
	<visible>Player.Seeking | Player.HasPerformedSeek(3) | [Player.Paused + !Player.Caching] | Player.Forwarding | Player.Rewinding | Player.ShowInfo | Window.IsActive(fullscreeninfo) | Player.ShowTime | Window.IsActive(videoosd) | Window.IsActive(musicosd) | Window.IsActive(playerprocessinfo) | !String.IsEmpty(Player.SeekNumeric)</visible>
	<zorder>0</zorder>
	<include>Anim_OSDSlideUp</include>
	<controls>
		<control type="group">
			<visible>!$EXP[OSD_SeekBarHidden]</visible>
			<visible>!Player.HasGame</visible>
			<include>Anim_FadeVisible</include>
{strip(top, 1080 - top, turn=False)}
			<control type="label">
				<left>96</left>
				<top>{top + 20}</top>
				<width>1100</width>
				<height>40</height>
				<font>sans_28_semi</font>
				<textcolor>ink</textcolor>
				<label>$VAR[OSD_Title][COLOR cap]   $VAR[OSD_State][/COLOR]</label>
			</control>
			<control type="label">
				<left>1024</left>
				<top>{top + 20}</top>
				<width>800</width>
				<height>40</height>
				<align>right</align>
				<font>num_26</font>
				<textcolor>ink</textcolor>
				<label>$VAR[OSD_SeekTimeLabel][COLOR cap]$INFO[Player.Duration, / ,][/COLOR]</label>
			</control>
{perforation(top + 86)}
			<control type="slider" id="401">
				<left>-3000</left>
				<top>0</top>
				<width>1</width>
				<height>1</height>
				<texturesliderbar />
				<textureslidernib />
			</control>
			<!-- skip feedback: a cream tab hanging from the top edge -->
			<control type="group">
				<left>1628</left>
				<top>0</top>
				<visible>[!String.IsEmpty(Player.SeekStepSize) | [!String.IsEmpty(Player.SeekOffset) + Player.HasPerformedSeek(3)]] + Window.IsActive(fullscreenvideo)</visible>
				<include>Anim_TopStrip</include>
				<control type="image">
					<left>-48</left>
					<top>-48</top>
					<width>292</width>
					<height>162</height>
					<texture>fold/tab_shadow.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>196</width>
					<height>66</height>
					<texture colordiffuse="$VAR[FoldAccent]">fold/tab.png</texture>
				</control>
				<control type="label">
					<left>0</left>
					<top>14</top>
					<width>196</width>
					<height>40</height>
					<align>center</align>
					<font>num_26</font>
					<textcolor>on_card</textcolor>
					<label>$VAR[OSD_SkipValue]</label>
				</control>
			</control>
		</control>
	</controls>
</window>
"""


def fullscreen_info():
    top = 700
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_osd.py. Playing info: a strip with the poster tipped in. Kodi id 999 = the
     full-screen focus button (Left/Right step seek, Up/Down chapter or big step, OK opens the OSD). -->
<window>
	<defaultcontrol always="true">999</defaultcontrol>
	<include>Anim_OSDSlideUp</include>
	<controls>
		<control type="button" id="999">
			<left>0</left>
			<top>0</top>
			<width>1920</width>
			<height>1080</height>
			<label></label>
			<texturefocus />
			<texturenofocus />
			<onright>StepForward</onright>
			<onleft>StepBack</onleft>
			<onup>ChapterOrBigStepForward</onup>
			<ondown>ChapterOrBigStepBack</ondown>
			<onclick>OSD</onclick>
		</control>
		<control type="group">
			<visible>!Window.IsVisible(sliderdialog) + !Window.IsVisible(selectdialog) + !Window.IsVisible(osdsubtitlesettings) + !Window.IsVisible(osdaudiosettings) + !Window.IsVisible(osdvideosettings)</visible>
{strip(top, 1080 - top)}
			<!-- the poster, tipped in and standing proud of the strip -->
			<control type="group">
				<left>96</left>
				<top>{top - 120}</top>
				<width>240</width>
				<height>360</height>
				<control type="image">
					<left>-96</left>
					<top>-96</top>
					<right>-96</right>
					<bottom>-96</bottom>
					<texture border="104">fold/shadow_spread.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>240</width>
					<height>360</height>
					<texture colordiffuse="cream_deep">common/white.png</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>240</width>
					<height>360</height>
					<aspectratio>scale</aspectratio>
					<texture background="true">$VAR[OSDInfo_Poster]</texture>
				</control>
				<control type="image">
					<left>0</left>
					<top>0</top>
					<width>240</width>
					<height>360</height>
					<texture>fold/plate_sheen.png</texture>
				</control>
			</control>
			<control type="label">
				<left>384</left>
				<top>{top + 26}</top>
				<width>900</width>
				<height>32</height>
				<font>caps_20_b</font>
				<textcolor>$VAR[FoldAccentInk]</textcolor>
				<label>$VAR[OSD_State][COLOR cap2]   $VAR[OSD_Type][/COLOR]</label>
			</control>
			<control type="label">
				<left>384</left>
				<top>{top + 56}</top>
				<width>1000</width>
				<height>66</height>
				<font>head_50</font>
				<textcolor>ink</textcolor>
				<label>$VAR[OSD_Title]</label>
			</control>
			<control type="label">
				<left>384</left>
				<top>{top + 118}</top>
				<width>1000</width>
				<height>40</height>
				<font>light_30</font>
				<textcolor>ink2</textcolor>
				<label>$VAR[OSD_FoldMeta]</label>
			</control>
			<control type="textbox">
				<left>384</left>
				<top>{top + 168}</top>
				<width>1060</width>
				<height>{37 * 3}</height>
				<font>body_26</font>
				<textcolor>body</textcolor>
				<label>$INFO[VideoPlayer.Plot]</label>
			</control>
			<control type="label">
				<left>1224</left>
				<top>{top + 40}</top>
				<width>600</width>
				<height>50</height>
				<align>right</align>
				<font>num_38</font>
				<textcolor>ink</textcolor>
				<label>$INFO[Player.Time]</label>
			</control>
			<control type="label">
				<left>1024</left>
				<top>{top + 96}</top>
				<width>800</width>
				<height>32</height>
				<align>right</align>
				<font>caps_20</font>
				<textcolor>cap</textcolor>
				<label>$VAR[OSD_TimeLine]</label>
			</control>
{perforation(top + 316)}
		</control>
	</controls>
</window>
"""


def main():
    for name, body in (("VideoOSD.xml", video_osd()), ("DialogSeekBar.xml", seekbar()), ("DialogFullScreenInfo.xml", fullscreen_info())):
        (X / name).write_text(finish_xml(strip_defaults(selcol(body), X / "Defaults.xml")), encoding="utf-8", newline="\n")
    print("OSD written; word widths", {wd[1]: w(*wd[2]) for wd in WORDS})


if __name__ == "__main__":
    main()
