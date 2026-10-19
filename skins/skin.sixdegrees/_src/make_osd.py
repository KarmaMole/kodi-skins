"""Six Degrees video OSD = a transit sign -> 1080i/Includes_OSD_SD.xml, VideoOSD.xml, DialogSeekBar.xml,
DialogFullScreenInfo.xml.

Brief: "a thin transit line along the bottom: the film as a line from start to end, with chapters as station
dots, 'now' as a ring, the clock time of the end station ('arrives 23:57'), and the title in Hanken 600."
A white sign card sits over the video (no scrim needed); the travelled part of the line is ink, the rest
route grey; chapters are stops (ranges control on Player.Chapters); "now" is a slider nib ring on
Player.SeekBar; while seeking an ink pill shows the target time above the ring.

Kodi ids (Estuary Omega VideoOSD.xml): 602 play/pause (default), 603 stop, 600 previous / 607 next
(chapter or playlist item, gated), 87 hidden seek stepper (Up from the row), 200 the controls group,
70044 chapters, 70046 subtitles, 70049 audio, 70048 video settings, 70043 info, 70051 player stats.
Row order (Omar's rule 6): Play/Pause, Stop, Previous, Next, Chapters | Subtitles, Audio, Video, Info, Stats.
DialogSeekBar keeps Kodi's id 401 (seek target progress); it shows the sign without buttons.

    python skins/skin.sixdegrees/_src/make_osd.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import ImageFont

from make_map import img, lbl, group, RM

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
OUT = SKIN / "1080i"
FONTS = SKIN / "fonts"

CARD_X, CARD_W = 64, 1792
LX0, LX1 = 112, 1808          # the line
LW = LX1 - LX0


def tw(text, font="SixDegreesText-SemiBold.ttf", size=22):
    f = ImageFont.truetype(str(FONTS / font), size)
    return int(f.getlength(text)) + len(text) + 4


def tag(name, value, cond=None):
    c = f' condition="{cond}"' if cond else ""
    return f"<{name}{c}>{value}</{name}>"


# ------------------------------------------------------------------ variables
def variables():
    v = ['<variable name="OSD_SDKicker">',
         '\t<value condition="!String.IsEmpty($VAR[OSD_State])">$VAR[OSD_State]</value>'.replace("!String.IsEmpty($VAR[OSD_State])",
                                                                                                "Player.Caching | !String.IsEmpty(Player.SeekNumeric) | !String.IsEmpty(Player.SeekStepSize) | Player.Forwarding | Player.Rewinding | Player.Paused"),
         "\t<value>Now playing</value>",
         "</variable>",
         '<variable name="OSD_SDKickerCol">',
         '\t<value condition="Player.Paused | Player.Caching">l_dir</value>',
         "\t<value>ink2</value>",
         "</variable>",
         '<variable name="OSD_SDArrives">',
         "\t<value>$INFO[Player.FinishTime]</value>",
         "</variable>",
         '<variable name="Music_QueueWords">',
         '	<value condition="Integer.IsGreater(Playlist.Length(music),20)">$INFO[Playlist.Length(music)] songs in the queue (the first 20 on the line)</value>',
         "	<value>$INFO[Playlist.Length(music)] songs in the queue</value>",
         "</variable>",
         '<variable name="OSD_SDRemain">',
         "\t<value>$INFO[Player.TimeRemaining,−,]$INFO[Player.Duration,  ·  ,]</value>",
         "</variable>"]
    return v


def bubble_slide():
    step = LW / 100
    return "\n".join(f'<animation effect="slide" end="{step:.2f},0" time="0" condition="Integer.IsGreater(Player.SeekBar,{k})">Conditional</animation>'
                     for k in range(100))


# ------------------------------------------------------------------ the sign
def sign(top, show_buttons, with_plot=False):
    """top = card top. Returns controls (card + header + line)."""
    h = 1040 - top
    ch = [img(CARD_X - 60, top - 46, CARD_W + 120, h + 120, "sd/shadow_card.png", diffuse="shadow", border="90",
              extra='<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation><animation effect="fade" start="100" end="0" time="120">WindowClose</animation>'),
          img(CARD_X, top, CARD_W, h, "sd/rr20.png", diffuse="card", border="20",
              extra='<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation><animation effect="fade" start="100" end="0" time="120">WindowClose</animation>')]
    y = top + 26
    # row A: state left, arrives right
    ch.append(lbl(LX0, y, 900, 30, "$VAR[OSD_SDKicker]", "caps_21", "$VAR[OSD_SDKickerCol]", aligny="top"))
    ch.append('<control type="grouplist">'
              f"<left>{LX1 - 600}</left><top>{y - 6}</top><width>600</width><height>40</height>"
              "<orientation>horizontal</orientation><align>right</align><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
              '<control type="label"><width>auto</width><height>40</height><font>semi_24</font><textcolor>ink2</textcolor><label>arrives </label></control>'
              '<control type="label"><width>auto</width><height>40</height><font>xb_24</font><textcolor>ink</textcolor><label>$VAR[OSD_SDArrives]</label></control>'
              "<visible>!String.IsEmpty(Player.FinishTime) + !Player.IsInternetStream | Player.HasDuration</visible>"
              "</control>")
    # row B: title (Hanken 600 per the brief) + meta
    ch.append('<control type="grouplist">'
              f"<left>{LX0}</left><top>{y + 30}</top><width>{LW}</width><height>52</height>"
              "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
              '<control type="label"><width max="1100">auto</width><height>52</height><font>semi_30</font><textcolor>ink</textcolor><label>$VAR[OSD_Title]</label></control>'
              '<control type="label"><left>20</left><width max="560">auto</width><height>52</height><font>reg_24</font><textcolor>ink2</textcolor><label>$VAR[OSD_Meta]</label></control>'
              "</control>")
    ly = y + 30 + 52 + 40 if not with_plot else y + 30 + 52 + 40 + 160
    if with_plot:
        ch.append('<control type="textbox">'
                  f"<left>{LX0}</left><top>{y + 96}</top><width>1300</width><height>136</height>"
                  "<font>reg_24</font><textcolor>body</textcolor><label>$INFO[VideoPlayer.Plot]</label>"
                  '<autoscroll delay="6000" time="3000" repeat="10000">true</autoscroll></control>')
    # the line
    line = [img(LX0 - 4, ly - 4, LW + 8, 8, "sd/line_h8.png", diffuse="l_route", border="4,0,4,0"),
            '<control type="progress">'
            f"<left>{LX0 - 4}</left><top>{ly - 4}</top><width>{LW + 8}</width><height>8</height>"
            '<texturebg border="4,0,4,0" colordiffuse="clear">sd/line_h8.png</texturebg>'
            '<lefttexture /><midtexture border="4,0,4,0" colordiffuse="ink">sd/line_h8.png</midtexture><righttexture />'
            "<info>Player.SeekBar</info></control>",
            '<control type="ranges">'
            f"<left>{LX0}</left><top>{ly - 11}</top><width>{LW}</width><height>22</height>"
            '<texturebg colordiffuse="clear">common/white.png</texturebg><lefttexture /><midtexture />'
            "<righttexture>sd/osd_stop.png</righttexture>"
            "<info>Player.Chapters</info><visible>$EXP[OSD_HasChapters]</visible></control>",
            # start and end stations
            img(LX0 - 15, ly - 15, 30, 30, "sd/disc_24.png", diffuse="white"),
            img(LX0 - 15, ly - 15, 30, 30, "sd/ring_24_6.png", diffuse="ink"),
            img(LX1 - 4, ly - 19, 8, 38, "sd/tick_v8.png", diffuse="ink"),
            # now: a ring riding Player.SeekBar (slider nib, lesson 88)
            '<control type="slider">'
            f"<left>{LX0 - 20}</left><top>{ly - 20}</top><width>{LW + 40}</width><height>40</height>"
            "<texturesliderbar>sd/clear40.png</texturesliderbar>"
            "<textureslidernib>sd/osd_now.png</textureslidernib><textureslidernibfocus>sd/osd_now.png</textureslidernibfocus>"
            "<info>Player.SeekBar</info><visible>Player.HasDuration</visible></control>",
            # times
            lbl(LX0, ly + 22, 600, 34, "$VAR[OSD_SeekTimeLabel]", "xb_24", "ink", vis="![$EXP[OSD_SeekActive] + Player.SeekEnabled]"),
            lbl(LX1 - 700, ly + 22, 700, 34, "$VAR[OSD_SDRemain]", "semi_22", "ink2", align="right")]
    # seek bubble: ink pill above the ring
    bub = group([img(0, 0, 132, 38, "sd/pill_40.png", diffuse="ink", border="19"),
                 lbl(0, 0, 132, 38, "$VAR[OSD_SeekTimeLabel]", "xb_22", "white", align="center")],
                left=LX0 - 66, top=ly + 20, vis="$EXP[OSD_SeekActive] + Player.SeekEnabled", anims=bubble_slide())
    line.append(bub)
    ch.append(group(line, desc="the film as a line"))
    return ch


# ------------------------------------------------------------------ buttons
ICON_W = 64


def icon_btn(cid, icon, onclick, onleft, onright, visible="true", primary=False, icon_var=None):
    nofocus = ('<texturenofocus border="32" colordiffuse="ink">sd/pill_64.png</texturenofocus>' if primary else
               '<texturenofocus border="32" colordiffuse="hair_strong">sd/pill_64_o3.png</texturenofocus>')
    tex = icon_var or icon
    g = [f'<control type="group"><left>9</left><top>9</top><width>{ICON_W}</width><height>{ICON_W}</height><visible>{visible}</visible>',
         f'<control type="button" id="{cid}"><left>0</left><top>0</top><width>{ICON_W}</width><height>{ICON_W}</height><label></label>',
         '<texturefocus border="32" colordiffuse="ink">sd/pill_64.png</texturefocus>', nofocus,
         tag("onclick", onclick), tag("onleft", onleft), tag("onright", onright), tag("onup", "87"), tag("ondown", "noop"),
         "</control>",
         img(18, 18, 28, 28, tex, diffuse="white", vis=f"Control.HasFocus({cid})" if not primary else "true"),
         ]
    if not primary:
        g.append(img(18, 18, 28, 28, tex, diffuse="ink", vis=f"!Control.HasFocus({cid})"))
    g.append(img(-9, -9, ICON_W + 18, ICON_W + 18, "sd/pill_82_ring.png", diffuse="ink", border="41", vis=f"Control.HasFocus({cid})"))
    g.append("</control>")
    return "".join(g)


def text_btn(cid, caption, value, onclick, onleft, onright, visible="true", width=None):
    w = width or (tw(caption.upper(), font="SixDegreesCaps-SemiBold.ttf", size=20) + tw(value or "Settings") + 70)
    g = [f'<control type="group"><left>9</left><top>9</top><width>{w}</width><height>{ICON_W}</height><visible>{visible}</visible>',
         f'<control type="button" id="{cid}"><left>0</left><top>0</top><width>{w}</width><height>{ICON_W}</height><label></label>',
         '<texturefocus border="32" colordiffuse="ink">sd/pill_64.png</texturefocus>',
         '<texturenofocus border="32" colordiffuse="hair_strong">sd/pill_64_o3.png</texturenofocus>',
         tag("onclick", onclick), tag("onleft", onleft), tag("onright", onright), tag("onup", "87"), tag("ondown", "noop"),
         "</control>",
         '<control type="grouplist"><left>26</left><top>0</top>' f"<width>{w - 52}</width><height>{ICON_W}</height>"
         "<orientation>horizontal</orientation><itemgap>10</itemgap><usecontrolcoords>true</usecontrolcoords>",
         f'<control type="label"><width>auto</width><height>{ICON_W}</height><font>caps_20</font><textcolor>ink2</textcolor><label>{caption}</label><visible>!Control.HasFocus({cid})</visible></control>',
         f'<control type="label"><width>auto</width><height>{ICON_W}</height><font>caps_20</font><textcolor>white</textcolor><label>{caption}</label><visible>Control.HasFocus({cid})</visible></control>',
         f'<control type="label"><width max="{w - 60}">auto</width><height>{ICON_W}</height><font>semi_22</font><textcolor>ink</textcolor><label>{value}</label><visible>!Control.HasFocus({cid})</visible></control>',
         f'<control type="label"><width max="{w - 60}">auto</width><height>{ICON_W}</height><font>semi_22</font><textcolor>white</textcolor><label>{value}</label><visible>Control.HasFocus({cid})</visible></control>',
         "</control>",
         img(-9, -9, w + 18, ICON_W + 18, "sd/pill_82_ring.png", diffuse="ink", border="41", vis=f"Control.HasFocus({cid})"),
         "</control>"]
    return "".join(g)


def buttons(top):
    gap = 14 - 9  # itemgap reduced by the 9 px ring room each child carries
    left = ['<control type="grouplist">',
            f"<left>{LX0 - 18}</left><top>{top - 9}</top><width>900</width><height>{ICON_W + 18}</height>",
            f"<orientation>horizontal</orientation><itemgap>{gap}</itemgap><usecontrolcoords>true</usecontrolcoords>",
            icon_btn(602, "", "PlayerControl(Play)", "70051", "603", visible="Player.PauseEnabled", primary=True, icon_var="$VAR[OSD_PlayIcon]"),
            icon_btn(603, "icons/stop.png", "PlayerControl(Stop)", "602", "600"),
            icon_btn(600, "icons/prev.png", "PlayerControl(Previous)", "603", "607", visible="$EXP[OSD_HasPrevNext]"),
            icon_btn(607, "icons/next.png", "PlayerControl(Next)", "600", "70044", visible="$EXP[OSD_HasPrevNext]"),
            icon_btn(70044, "icons/chapters.png", "ActivateWindow(videobookmarks)", "607", "70046",
                     visible="Player.SeekEnabled + !VideoPlayer.Content(livetv)"),
            "</control>"]
    # right group: fixed widths (rule 5); the subtitle/audio values can be long, so they come first and
    # their pills are sized for a long language name and clip with an ellipsis
    right = ['<control type="grouplist">',
             f"<left>{LX0 - 18}</left><top>{top - 9}</top><width>{LW + 36}</width><height>{ICON_W + 18}</height>",
             f"<orientation>horizontal</orientation><align>right</align><itemgap>{gap}</itemgap><usecontrolcoords>true</usecontrolcoords>",
             text_btn(70046, "Subtitles", "$VAR[OSD_SubtitleValue]", "ActivateWindow(osdsubtitlesettings)", "70044", "70049",
                      visible="Player.HasVideo", width=300),
             text_btn(70049, "Audio", "$VAR[OSD_AudioValue]", "ActivateWindow(osdaudiosettings)", "70046", "70048", width=270),
             text_btn(70048, "Video", "Settings", "ActivateWindow(osdvideosettings)", "70049", "70043", visible="Player.HasVideo"),
             text_btn(70043, "Station", "Info", "Action(Info,fullscreenvideo)", "70048", "70051"),
             text_btn(70051, "Player", "Stats", "Action(PlayerProcessInfo)", "70043", "602"),
             "</control>"]
    return ['<control type="group" id="200"><left>0</left><top>0</top><width>1920</width><height>1080</height>',
            "\n".join(left), "\n".join(right), "</control>"]


def video_osd():
    sign_top = 708
    body = sign(sign_top, True)
    stepper = ('<control type="button" id="87"><description>seek stepper</description><include>SD_Hidden</include>'
               "<onup>noop</onup><ondown>200</ondown><onleft>StepBack</onleft>"
               '<onright condition="!Player.Paused">StepForward</onright>'
               '<onright condition="Player.Paused">PlayerControl(FrameAdvance(1))</onright>'
               "<visible>Player.SeekEnabled</visible></control>")
    hint = img(LX0 - 4, sign_top + 26 + 30 + 52 + 40 - 6, LW + 8, 12, "sd/line_h8.png", diffuse="l_dir", border="4,0,4,0",
               vis="Control.HasFocus(87)")
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_osd.py. Video OSD = the transit sign (see the generator docstring for ids and order).
	Focus: opens on 602 (603 when pause is impossible). Left/Right walk the row (wraps). Up = seek stepper 87
	(the line turns vermilion; Left/Right step), Down returns. Back closes the OSD.
-->
<window>
	<onload condition="!Player.PauseEnabled">SetFocus(603)</onload>
	<defaultcontrol always="true">602</defaultcontrol>
	<include>Anim_OSDSlideUp</include>
	<controls>
		<control type="group">
			<visible>!$EXP[OSD_PanelOpen]</visible>
			<include>Anim_FadeVisible</include>
			{chr(10).join(body)}
			{hint}
			{stepper}
			{chr(10).join(buttons(sign_top + 26 + 30 + 52 + 40 + 80))}
		</control>
	</controls>
</window>
"""
    (OUT / "VideoOSD.xml").write_text(w, encoding="utf-8")


def seek_bar():
    p = OUT / "DialogSeekBar.xml"
    s = p.read_text(encoding="utf-8")
    head = s[: s.index("<controls>")]
    sign_top = 800
    body = sign(sign_top, False)
    # keep Kodi's 401 (seek target) as an invisible progress
    k401 = ('<control type="progress" id="401"><left>-3000</left><top>-3000</top><width>10</width><height>2</height>'
            "<info>Player.SeekBar</info></control>")
    s = head + f"""<controls>
		<control type="group">
			<visible>!$EXP[OSD_SeekBarHidden]</visible>
			<visible>!Player.HasGame</visible>
			<include>Anim_FadeVisible</include>
			{chr(10).join(body)}
			{k401}
		</control>
	</controls>
</window>
"""
    s = s.replace("<!--\n\tSeek bar (M3, Builder D).", "<!--\n\tGENERATED by _src/make_osd.py (sign without buttons). Was: Seek bar (M3, Builder D).", 1)
    p.write_text(s, encoding="utf-8")


def fullscreen_info():
    sign_top = 640
    body = sign(sign_top, False, with_plot=True)
    ptop = sign_top - 500
    poster = [img(1460 - 14, ptop - 14, 328, 478, "sd/ring_centre_fill.png", diffuse="ground", border="24"),
              img(1460 - 14, ptop - 14, 328, 478, "sd/ring_centre.png", diffuse="ink", border="24"),
              '<control type="image"><left>1460</left><top>' f"{ptop}" '</top><width>300</width><height>450</height>'
              '<aspectratio>scale</aspectratio><texture background="true" diffuse="sd/mask_300x450.png">$VAR[OSDInfo_Poster]</texture></control>']
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_osd.py. Fullscreen info (Info while playing): the transit sign with the plot and
	the station poster in its interchange ring.
-->
<window>
	<defaultcontrol always="true">999</defaultcontrol>
	<include>Anim_OSDSlideUp</include>
	<controls>
		<control type="button" id="999">
			<left>0</left><top>0</top><width>1920</width><height>1080</height><label></label>
			<texturefocus /><texturenofocus />
			<onright>StepForward</onright><onleft>StepBack</onleft>
			<onup>ChapterOrBigStepForward</onup><ondown>ChapterOrBigStepBack</ondown>
			<onclick>OSD</onclick>
		</control>
		<control type="group">
			<visible>!Window.IsVisible(sliderdialog) + !Window.IsVisible(selectdialog) + !Window.IsVisible(osdsubtitlesettings) + !Window.IsVisible(osdaudiosettings) + !Window.IsVisible(osdvideosettings)</visible>
			<include>Anim_FadeVisible</include>
			{chr(10).join(body)}
			{group(poster, vis="!String.IsEmpty(VideoPlayer.Cover) | !String.IsEmpty(Player.Art(poster)) | !String.IsEmpty(Player.Art(tvshow.poster))")}
		</control>
	</controls>
</window>
"""
    (OUT / "DialogFullScreenInfo.xml").write_text(w, encoding="utf-8")


def includes():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_osd.py. Variables for the transit-sign OSD. -->",
             "<includes>"]
    parts += ["\t" + x for x in variables()]
    parts.append("</includes>")
    (OUT / "Includes_OSD_SD.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    includes()
    video_osd()
    seek_bar()
    fullscreen_info()
    print("wrote the transit-sign OSD")
