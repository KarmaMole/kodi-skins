"""Six Degrees Now playing (MusicVisualisation.xml) + music OSD (MusicOSD.xml).

Now playing = a station: the cover in an interchange ring, the song title, artist and album, the queue as
a line of stops (played = filled, now = the ink ring, ahead = open), the song itself as a line with the
"now" ring and "arrives" (end clock time), and the next stop. The music OSD adds the white sign with the
transport row at the bottom (Omar's rule 6 order: Play/Pause, Stop, Previous, Next | Shuffle, Repeat, Queue).

Kodi ids (Estuary Omega MusicVisualisation.xml / MusicOSD.xml): 2 visualisation; OSD 602 play/pause
(default), 603 stop, 600 previous, 607 next, 87 seek stepper, 200 group, 70054 shuffle, 70053 repeat,
70051 queue.

    python skins/skin.sixdegrees/_src/make_music_player.py
"""
from pathlib import Path

from make_map import img, lbl, group, RM
from make_osd import icon_btn, text_btn, bubble_slide

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i"

TX = 760
LINE_Y = 640
QX0, QPITCH, QMAX = TX + 12, 52, 20
SX0, SX1 = TX + 12, 1808


def now_playing():
    cov = 500
    cx, cy = 130, 220
    o = 14
    ch = [img(cx - o - 72, cy - o - 50, cov + 2 * o + 144, cov + 2 * o + 144, "sd/shadow_big.png", diffuse="shadow", border="100"),
          img(cx - o, cy - o, cov + 2 * o, cov + 2 * o, "sd/ring_centre_fill.png", diffuse="ground", border="24"),
          img(cx - o, cy - o, cov + 2 * o, cov + 2 * o, "sd/ring_centre.png", diffuse="ink", border="24"),
          img(cx, cy, cov, cov, "common/white.png", diffuse="wash"),
          '<control type="image">' f"<left>{cx}</left><top>{cy}</top><width>{cov}</width><height>{cov}</height>"
          '<aspectratio>scale</aspectratio><fadetime>300</fadetime>'
          '<texture background="true" diffuse="sd/mask_280x280.png">$VAR[Music_PlayerArt]</texture></control>']
    t = [lbl(TX, 214, 1096, 30, "Now playing$INFO[Playlist.Position(music), · station ,]$INFO[Playlist.Length(music), of ,]", "caps_21", "ink2", aligny="top"),
         lbl(TX - 3, 246, 1100, 80, "$INFO[MusicPlayer.Title]", "disp_60", "ink"),
         lbl(TX, 330, 1096, 44, "$INFO[MusicPlayer.Artist]", "xb_30", "ink"),
         lbl(TX, 378, 1096, 36, "$INFO[MusicPlayer.Album]$INFO[MusicPlayer.Year, · ,]$INFO[MusicPlayer.Genre, · ,]", "semi_24", "ink2")]
    # the queue as a line of stops
    q = []
    for n in range(2, QMAX + 1):
        q.append(img(QX0 - 4, 466 - 4, (n - 1) * QPITCH + 8, 8, "sd/line_h8.png", diffuse="hair_strong", border="4,0,4,0",
                     vis=f"Integer.IsEqual(Playlist.Length(music),{n})"))
    q.append(img(QX0 - 4, 466 - 4, 1808 - QX0 + 8, 8, "sd/line_h8.png", diffuse="hair_strong", border="4,0,4,0",
                 vis=f"Integer.IsGreater(Playlist.Length(music),{QMAX})"))
    for k in range(QMAX):
        x = QX0 + k * QPITCH
        on = f"Integer.IsGreater(Playlist.Length(music),{k})"
        played = f"Integer.IsGreater(Playlist.Position(music),{k + 1})"
        now = f"Integer.IsEqual(Playlist.Position(music),{k + 1})"
        q += [img(x - 15, 466 - 15, 30, 30, "sd/disc_24.png", diffuse="white", vis=f"{on} + !{now} + !{played}"),
              img(x - 15, 466 - 15, 30, 30, "sd/ring_24_6.png", diffuse="l_route", vis=f"{on} + !{now} + !{played}"),
              img(x - 15, 466 - 15, 30, 30, "sd/disc_24.png", diffuse="l_route", vis=f"{on} + {played}"),
              img(x - 19, 466 - 19, 38, 38, "sd/disc_32.png", diffuse="white", vis=now),
              img(x - 19, 466 - 19, 38, 38, "sd/ring_32_8.png", diffuse="ink", vis=now)]
    q.append(lbl(TX, 500, 1096, 30, "$VAR[Music_QueueWords]", "semi_22", "ink2", vis="Integer.IsGreater(Playlist.Length(music),1)"))
    # the song as a line
    s = [img(SX0 - 4, LINE_Y - 4, SX1 - SX0 + 8, 8, "sd/line_h8.png", diffuse="l_route", border="4,0,4,0"),
         '<control type="progress">' f"<left>{SX0 - 4}</left><top>{LINE_Y - 4}</top><width>{SX1 - SX0 + 8}</width><height>8</height>"
         '<texturebg border="4,0,4,0" colordiffuse="clear">sd/line_h8.png</texturebg><lefttexture />'
         '<midtexture border="4,0,4,0" colordiffuse="ink">sd/line_h8.png</midtexture><righttexture /><info>Player.SeekBar</info></control>',
         img(SX0 - 15, LINE_Y - 15, 30, 30, "sd/disc_24.png", diffuse="white"),
         img(SX0 - 15, LINE_Y - 15, 30, 30, "sd/ring_24_6.png", diffuse="ink"),
         img(SX1 - 4, LINE_Y - 19, 8, 38, "sd/tick_v8.png", diffuse="ink"),
         '<control type="slider">' f"<left>{SX0 - 20}</left><top>{LINE_Y - 20}</top><width>{SX1 - SX0 + 40}</width><height>40</height>"
         "<texturesliderbar>sd/clear40.png</texturesliderbar><textureslidernib>sd/osd_now.png</textureslidernib>"
         "<textureslidernibfocus>sd/osd_now.png</textureslidernibfocus><info>Player.SeekBar</info></control>",
         lbl(SX0, LINE_Y + 22, 500, 34, "$INFO[Player.Time]", "xb_24", "ink"),
         lbl(SX1 - 600, LINE_Y + 22, 600, 34, "$INFO[Player.TimeRemaining,−,]$INFO[Player.Duration, · ,]", "semi_22", "ink2", align="right"),
         '<control type="grouplist">' f"<left>{SX1 - 600}</left><top>{LINE_Y - 64}</top><width>600</width><height>40</height>"
         "<orientation>horizontal</orientation><align>right</align><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
         '<control type="label"><width>auto</width><height>40</height><font>semi_24</font><textcolor>ink2</textcolor><label>arrives </label></control>'
         '<control type="label"><width>auto</width><height>40</height><font>xb_24</font><textcolor>ink</textcolor><label>$INFO[Player.FinishTime]</label></control>'
         "</control>"]
    nxt = [lbl(TX, 744, 600, 30, "Next stop", "caps_21", "l_lead", aligny="top"),
           '<control type="grouplist">' f"<left>{TX}</left><top>776</top><width>1096</width><height>40</height>"
           "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
           '<control type="label"><width max="700">auto</width><height>40</height><font>xb_26</font><textcolor>ink</textcolor><label>$INFO[MusicPlayer.offset(1).Title]</label></control>'
           '<control type="label"><width max="390">auto</width><height>40</height><font>reg_24</font><textcolor>ink2</textcolor><label>$INFO[MusicPlayer.offset(1).Artist, · ,]</label></control>'
           "</control>"]
    body = ch + t + [group(q, desc="queue"), group(s, desc="song")] + [group(nxt, vis="!String.IsEmpty(MusicPlayer.offset(1).Title)", desc="next stop")]
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_music_player.py. Now playing = a station (see the generator docstring).
	Kodi id contract: 2 = visualisation (shown only when Omar enables a visualisation add-on; the station
	layout then steps aside until the OSD or Info is up). No focusable controls: Kodi's keymap routes OK / Menu
	to the music OSD and Back to the previous window.
-->
<window>
	<defaultcontrol></defaultcontrol>
	<backgroundcolor>ground</backgroundcolor>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>SD_Background</include>
		<control type="visualisation" id="2">
			<left>0</left><top>0</top><width>1920</width><height>1080</height>
			<visible>Player.HasAudio + Visualisation.Enabled</visible>
		</control>
		<control type="group">
			<visible>!Visualisation.Enabled | Window.IsVisible(musicosd) | Player.ShowInfo</visible>
			<include>Anim_FadeVisible</include>
			<include content="SD_PageHeader">
				<param name="title" value="Now playing"/>
			</include>
			<include>SD_Clock</include>
			{chr(10).join(body)}
		</control>
	</controls>
</window>
"""
    (OUT / "MusicVisualisation.xml").write_text(w, encoding="utf-8")


def music_osd():
    top = 880
    card = [img(64 - 60, top - 46, 1792 + 120, 136 + 120, "sd/shadow_card.png", diffuse="shadow", border="90",
                extra='<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation><animation effect="fade" start="100" end="0" time="120">WindowClose</animation>'),
            img(64, top, 1792, 136, "sd/rr20.png", diffuse="card", border="20",
                extra='<animation effect="fade" start="0" end="100" time="180">WindowOpen</animation><animation effect="fade" start="100" end="0" time="120">WindowClose</animation>')]
    by = top + 36
    left = ['<control type="grouplist" id="201">',
            f"<left>{SX0 - 670 - 18}</left><top>{by - 9}</top><width>900</width><height>82</height>".replace(f"<left>{SX0 - 670 - 18}</left>", "<left>94</left>"),
            "<orientation>horizontal</orientation><itemgap>5</itemgap><usecontrolcoords>true</usecontrolcoords>",
            "<onup>87</onup><ondown>noop</ondown>",
            icon_btn(602, "", "PlayerControl(Play)", "70051", "603", visible="Player.PauseEnabled", primary=True, icon_var="$VAR[OSD_PlayIcon]"),
            icon_btn(603, "icons/stop.png", "PlayerControl(Stop)", "602", "600"),
            icon_btn(600, "icons/prev.png", "PlayerControl(Previous)", "603", "607"),
            icon_btn(607, "icons/next.png", "PlayerControl(Next)", "600", "70054"),
            "</control>"]
    right = ['<control type="grouplist" id="202">',
             f"<left>94</left><top>{by - 9}</top><width>1732</width><height>82</height>",
             "<orientation>horizontal</orientation><align>right</align><itemgap>5</itemgap><usecontrolcoords>true</usecontrolcoords>",
             "<onup>87</onup><ondown>noop</ondown>",
             text_btn(70054, "Shuffle", "$VAR[Music_OSDShuffleValue]", "PlayerControl(Random)", "607", "70053", visible="!MusicPartyMode.Enabled", width=210),
             text_btn(70053, "Repeat", "$VAR[Music_OSDRepeatValue]", "PlayerControl(Repeat)", "70054", "70051", visible="!MusicPartyMode.Enabled", width=230),
             text_btn(70051, "Queue", "$VAR[Music_OSDQueueValue]", "ActivateWindow(musicplaylist)", "70053", "602",
                      visible="Integer.IsGreater(Playlist.Length(music),0)", width=250),
             "</control>"]
    stepper = ('<control type="button" id="87"><description>seek stepper</description><include>SD_Hidden</include>'
               "<onup>200</onup><ondown>200</ondown><onleft>StepBack</onleft><onright>StepForward</onright></control>")
    seekline = img(SX0 - 4, LINE_Y - 6, SX1 - SX0 + 8, 12, "sd/line_h8.png", diffuse="l_dir", border="4,0,4,0", vis="Control.HasFocus(87)")
    seekhint = lbl(SX0, LINE_Y + 60, 600, 30, "◀ ▶  ride the song", "semi_22", "l_dir", vis="Control.HasFocus(87)")
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_music_player.py. Music OSD: the white sign with the transport row over Now playing.
	Focus opens on 602 (603 when pause is impossible). Up = seek stepper 87 (the song line turns vermilion),
	Up / Down from it return. Back closes the OSD.
-->
<window>
	<onload condition="!Player.PauseEnabled">SetFocus(603)</onload>
	<defaultcontrol always="true">602</defaultcontrol>
	<include>Anim_OSDSlideUp</include>
	<controls>
		{chr(10).join(card)}
		{stepper}
		{seekline}
		{seekhint}
		<control type="group" id="200">
			{chr(10).join(left)}
			{chr(10).join(right)}
		</control>
	</controls>
</window>
"""
    (OUT / "MusicOSD.xml").write_text(w, encoding="utf-8")


if __name__ == "__main__":
    now_playing()
    music_osd()
    print("wrote MusicVisualisation.xml + MusicOSD.xml")
