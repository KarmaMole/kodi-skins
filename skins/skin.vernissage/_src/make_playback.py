"""Generate 1080i/Includes_VideoOSD.xml: playback (M3).   python skins/skin.vernissage/_src/make_playback.py

VideoOSD, DialogSeekBar, DialogFullScreenInfo and VideoFullScreen's paused layer (SPEC 11, board 08,
docs/skin.vernissage/screens/VideoOSD.md). Always Evening (VN_Playback pins step 4 over fullscreen video).

Nothing covers the picture while it plays. OSD: the corner placard (bottom left, 600 wide, its bottom at y 934; the
OSD's placard is exempt from the equal-height rule: it grows upward), a 3 px progress line with a knob at y 1000, the
icon row at the bottom right (rule 6 order: Play/Pause 602, Stop 603, Previous / Next chapter 600 / 607 only with
chapters, Subtitles 70046, Audio 70049, Info 70043, Settings 70048; labels centred under the focused icon), the seek
line 87 above the icons' row (Left / Right step, OK play / pause, a time chip over the knob while it has focus).
Paused: the frame dims (scrim_pause, its own fades), the bottom band, the placard grows (40 px title) and adds
"Paused at 1:06:12 of 1:57:00"; VideoFullScreen draws it without the OSD (the playhead reads Player.Progress).
Kodi ids copied from Estuary Omega VideoOSD.xml (600, 602, 603, 607, 70043, 70046, 70048, 87; 70049 ours) and
DialogSeekBar.xml (401: Kodi sets it to the seek target; kept offscreen). Our ids: icon grouplist 9880, placard group
9881, title probes 9882 (paused font) / 9883 (playing font) / 9884 (fullscreen info).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from vnxml import NBSP, NL, group, img, ind, join_and, label  # noqa: E402

OUT = HERE.parent / "1080i" / "Includes_VideoOSD.xml"
S = dict(play=31755, pause=31756, stop=31758, subs=31769, audio=31770, info=31757, settings=31771, prev=31772,
         next=31773, paused_at=31768, of=31671, ends=31451, min_left=31480)
PAUSED = "[Player.Paused | Player.Forwarding | Player.Rewinding]"
CHAPTERS = "Integer.IsGreater(Player.ChapterCount,1) + !VideoPlayer.Content(livetv)"
LIVE = "VideoPlayer.Content(livetv)"
X0, LW = 120, 1680      # the progress line
LINE_Y = 1000


def ends():
    return f"$LOCALIZE[{S['ends']}]{NBSP}[LOWERCASE]$INFO[Player.FinishTime][/LOWERCASE]"


def variables():
    v = []

    def var(name, values):
        v.append(f'\t<variable name="{name}">')
        for c, val in values:
            v.append(f'\t\t<value condition="{c}">{val}</value>' if c else f"\t\t<value>{val}</value>")
        v.append("\t</variable>")
    var("VOSD_Title", [("VideoPlayer.Content(episodes) + !String.IsEmpty(VideoPlayer.TVShowTitle)", "$INFO[VideoPlayer.TVShowTitle]"),
                       ("!String.IsEmpty(VideoPlayer.Title)", "$INFO[VideoPlayer.Title]"), (None, "$INFO[Player.Title]")])
    var("VOSD_Line2", [("VideoPlayer.Content(episodes) + !String.IsEmpty(VideoPlayer.Episode)",
                        "S$INFO[VideoPlayer.Season]·E$INFO[VideoPlayer.Episode]$INFO[VideoPlayer.Title, · ,]"),
                       (LIVE, "$INFO[VideoPlayer.ChannelName]$INFO[VideoPlayer.StartTime, · ,]$INFO[VideoPlayer.EndTime,–,]"),
                       (None, "$INFO[VideoPlayer.Year]$INFO[VideoPlayer.Director, · ,]")])
    var("VOSD_Key", [(LIVE, f"$LOCALIZE[{S['ends']}]{NBSP}[LOWERCASE]$INFO[VideoPlayer.EndTime][/LOWERCASE]"),
                     ("Integer.IsGreater(Player.TimeRemaining(mins),0)",
                      f"$INFO[Player.TimeRemaining(mins)]{NBSP}$LOCALIZE[{S['min_left']}] · {ends()}"),
                     (None, ends())])
    # times without leading zeros (device audit M5, O-4): h:mm:ss for an hour or more, else m:ss (Groove's NP_Time*
    # pattern; Kodi pads plain Player.Time to mm:ss / hh:mm:ss, and a ':' label compares as seconds: LESSONS Duotone)
    hour = "Integer.IsGreaterOrEqual(Player.Duration,3600)"
    for name, info in (("VN_TimeNow", "Player.Time"), ("VN_TimeTotal", "Player.Duration"),
                       ("VN_TimeLeft", "Player.TimeRemaining"), ("VN_TimeSeek", "Player.SeekTime")):
        var(name, [(hour, f"$INFO[{info}(h:mm:ss)]"), (None, f"$INFO[{info}(m)]:$INFO[{info}(ss)]")])
    # "elapsed / total" and "-left / total" strips (forked dialogs): the total only when Kodi knows the duration
    var("VN_TimeOfTotal", [("Integer.IsGreater(Player.Duration,0)", "$VAR[VN_TimeNow] / $VAR[VN_TimeTotal]"),
                           (None, "$VAR[VN_TimeNow]")])
    var("VN_LeftOfTotal", [("Integer.IsGreater(Player.Duration,0)", "−$VAR[VN_TimeLeft]  /  $VAR[VN_TimeTotal]")])
    var("VOSD_PausedAt", [(None, f"$LOCALIZE[{S['paused_at']}] $VAR[VN_TimeNow] $LOCALIZE[{S['of']}] $VAR[VN_TimeTotal]")])
    var("VOSD_PlayIcon", [(PAUSED, "vn/icons/play.png"), (None, "vn/icons/pause.png")])
    var("VOSD_PlayLabel", [(PAUSED, f"$LOCALIZE[{S['play']}]"), (None, f"$LOCALIZE[{S['pause']}]")])
    var("VOSD_SeekTime", [("!String.IsEmpty(Player.SeekNumeric)", "$INFO[Player.SeekNumeric]"),
                          ("Player.Seeking", "$VAR[VN_TimeSeek]"),
                          ("Player.HasPerformedSeek(1)", f"[LOWERCASE]{ends()}[/LOWERCASE]"),
                          (None, "$VAR[VN_TimeNow]")])
    return NL.join(v)


# ================================================================ pieces
def fades(t_in=200, t_out=150):
    return [f'<animation effect="fade" time="{t_in}">Visible</animation>', f'<animation effect="fade" time="{t_out}">Hidden</animation>',
            f'<animation effect="fade" start="0" end="100" time="{t_in}">WindowOpen</animation>',
            f'<animation effect="fade" start="100" end="0" time="{t_out}">WindowClose</animation>']


def band(full=True, vis=None):
    """The bottom band (0 -> 72 % ramp 600..880, flat 72 % below): icons and labels >= 4.5:1 over a white frame.
    Each layer has its own fades (LESSONS 4)."""
    o = []
    if full:
        o.append(img(0, 600, 1920, 280, "vn/scrim_bottom.png", anims=fades()))
    o.append(img(0, 880, 1920, 200, "vn/white.png", "scrim_band", anims=fades()))
    return group(o, vis=vis)


def pause_dim():
    return img(0, 0, 1920, 1080, "vn/white.png", "scrim_pause", vis=PAUSED, anims=fades(300, 200))


def knob_slides(cond_extra=None):
    """Time-0 slides that put a child at the playhead: one 1 % step each (Daylight's bedtime tick pattern)."""
    out = []
    for k in range(1, 101):
        dx = round(k * LW / 100) - round((k - 1) * LW / 100)
        c = join_and(f"Integer.IsGreaterOrEqual(Player.Progress,{k})", cond_extra)
        out.append(f'<animation effect="slide" start="0,0" end="{dx},0" time="0" condition="{c}">Conditional</animation>')
    return out


def progress_line(chip=None, big="false"):
    """The 3 px line with its knob (15 px; 21 px and a time chip while `big` holds)."""
    o = [img(X0, LINE_Y, LW, 3, "vn/white.png", "track_on_video"),
         NL.join(['<control type="progress">', f"\t<left>{X0}</left>", f"\t<top>{LINE_Y}</top>", f"\t<width>{LW}</width>",
                  "\t<height>3</height>", "\t<info>Player.Progress</info>", "\t<texturebg>vn/clear.png</texturebg>",
                  '\t<midtexture colordiffuse="$VAR[ink]">vn/white.png</midtexture>', "</control>"])]
    knob = [img(X0 - 7, LINE_Y - 6, 15, 15, "vn/progress_knob.png", "$VAR[ink]", vis=f"!{big}" if big != "false" else None)]
    if big != "false":
        knob.append(img(X0 - 10, LINE_Y - 9, 21, 21, "vn/progress_knob.png", "$VAR[ink]", vis=big))
    if chip:
        clamp, cum = [], 0
        for k in range(1, 101):
            dx = round(k * LW / 100) - round((k - 1) * LW / 100)
            cum += dx
            if cum <= 110 or cum > LW - 110:   # hold the chip while the knob is within 110 px of either end
                clamp.append(f'<animation effect="slide" start="0,0" end="{-dx},0" time="0" condition="Integer.IsGreaterOrEqual(Player.Progress,{k})">Conditional</animation>')
        knob.append(group([img(-110, 0, 220, 48, "vn/white.png", "$VAR[card]",
                               anims=['<animation effect="fade" start="100" end="90" time="0" condition="true">Conditional</animation>']),
                           img(-110, 0, 220, 48, "vn/card_edge.png", "$VAR[card_edge]", border="4"),
                           label(-110, 0, 220, 48, chip, "font_body", "$VAR[ink]", align="center", aligny="center", selected=False)],
                          left=X0 + 110, top=LINE_Y - 76, vis=big if big != "false" else None, anims=clamp))
    o.append(group(knob, anims=knob_slides()))
    return NL.join(o)


def corner_placard(width=600, plot=False, cid=None, probes=(9882, 9883), paused_vis=PAUSED):
    """The corner placard (bottom left, its bottom at y 934): title (36 playing / 40 paused, <= 2 lines), line 2,
    rule, key line, paused: "Paused at ... of ...". The card's height follows the state (probes pick 1 / 2 title
    lines); the stack is a bottom-aligned grouplist so it never needs a height table."""
    iw = width - 68
    pl, pp = probes
    np_ = lambda i: f"Integer.IsGreater(Container({i}).NumPages,1)"  # noqa: E731
    plot_h = 4 * 41 + 18 if plot else 0
    heights = {}   # (paused, two lines) -> card height
    for paused in (0, 1):
        for two in (0, 1):
            t = 49 if paused else 44
            h = t * (2 if two else 1) + 8 + 41 + 22 + 2 + 18 + 41 + (4 + 38 if paused else 0) + plot_h + 64
            heights[(paused, two)] = h
    cards = []
    for (paused, two), h in heights.items():
        probe = pp if paused else pl
        c = join_and(paused_vis if paused else f"!{paused_vis}", np_(probe) if two else f"!{np_(probe)}")
        cards.append(group([img(0, 934 - h, width, h, "vn/white.png", "$VAR[card]",
                                anims=['<animation effect="fade" start="100" end="90" time="0" condition="true">Conditional</animation>']),
                            img(0, 934 - h, width, h, "vn/card_edge.png", "$VAR[card_edge]", border="4")], vis=c))
    title = lambda font, pitch, vis: NL.join([  # noqa: E731
        group([NL.join(['<control type="textbox">', "\t<left>0</left>", "\t<top>0</top>", f"\t<width>{iw}</width>",
                        f"\t<height>{2 * pitch + 4}</height>", f"\t<font>{font}</font>", "\t<textcolor>$VAR[ink]</textcolor>",
                        "\t<label>$VAR[VOSD_Title]</label>", "</control>"])], width=iw, height=0, vis=vis),
        NL.join(['<control type="textbox">', f"\t<width>{iw}</width>", f'\t<height max="{2 * pitch}">auto</height>',
                 f"\t<font>{font}</font>", "\t<textcolor>clear</textcolor>", "\t<label>$VAR[VOSD_Title]</label>",
                 f"\t<visible>{vis}</visible>", "</control>"])])
    stack = [title("font_placard_l", 49, paused_vis), title("font_placard", 44, f"!{paused_vis}"),
             label(0, 8, iw, 41, "$VAR[VOSD_Line2]", "font_body", "$VAR[ink2]", aligny="center", selected=False),
             img(0, 22, "vn_rule_w", "vn_rule_h", "vn/white.png", "$VAR[placard_rule]"),
             label(0, 18, iw, 41, "$VAR[VOSD_Key]", "font_body", "$VAR[ink]", aligny="center", selected=False),
             label(0, 4, iw, 38, "$VAR[VOSD_PausedAt]", "font_small", "$VAR[ink2]", aligny="center", vis=paused_vis, selected=False)]
    if plot:
        # 4 whole lines; a longer plot ends line 4 in a card-coloured fade + "…" (NumPages of the box itself, LESSONS
        # Six Degrees 0.9.1), drawn after the text so they cover it
        more = "Integer.IsGreater(Container(9889).NumPages,1)"
        stack.append(group([
            NL.join(['<control type="textbox" id="9889">', "\t<left>0</left>", "\t<top>0</top>", f"\t<width>{iw}</width>",
                     f"\t<height>{4 * 41}</height>", "\t<font>font_body</font>", "\t<textcolor>$VAR[ink2]</textcolor>",
                     "\t<label>$INFO[VideoPlayer.Plot]</label>", "</control>"]),
            img(iw - 150, 3 * 41, 150, 41, "vn/fade_h.png", "$VAR[card]", vis=more,  # the card's own 90 %
                anims=['<animation effect="fade" start="100" end="90" time="0" condition="true">Conditional</animation>']),
            label(iw - 40, 3 * 41, 40, 41, "…", "font_body", "$VAR[ink2]", align="right", aligny="center", vis=more,
                  selected=False)], top=18, width=iw, height=4 * 41))
    gl = NL.join(['<control type="grouplist">', "\t<left>34</left>", "\t<top>300</top>", f"\t<width>{iw}</width>",
                  "\t<height>600</height>", "\t<itemgap>0</itemgap>", "\t<align>bottom</align>",
                  "\t<usecontrolcoords>true</usecontrolcoords>", ind(NL.join(stack), 1), "</control>"])
    probes_xml = NL.join(NL.join([f'<control type="textbox" id="{i}">', "\t<left>34</left>", "\t<top>300</top>",
                                  f"\t<width>{iw}</width>", f"\t<height>{p + p // 2}</height>", f"\t<font>{f}</font>",
                                  "\t<textcolor>clear</textcolor>", "\t<label>$VAR[VOSD_Title]</label>", "</control>"])
                         for i, f, p in ((pp, "font_placard_l", 49), (pl, "font_placard", 44)))
    return group(cards + [probes_xml, gl], left=120, cid=cid)


# ================================================================ the icon row
ICONS = [  # id, icon, label, onclick, visible
    (602, "$VAR[VOSD_PlayIcon]", "$VAR[VOSD_PlayLabel]", "PlayerControl(Play)", "Player.PauseEnabled"),
    (603, "vn/icons/stop.png", f"$LOCALIZE[{S['stop']}]", "PlayerControl(Stop)", None),
    (600, "vn/icons/chapter-prev.png", f"$LOCALIZE[{S['prev']}]", "PlayerControl(Previous)", CHAPTERS),
    (607, "vn/icons/chapter-next.png", f"$LOCALIZE[{S['next']}]", "PlayerControl(Next)", CHAPTERS),
    (70046, "vn/icons/subs.png", f"$LOCALIZE[{S['subs']}]", "ActivateWindow(osdsubtitlesettings)", None),
    (70049, "vn/icons/audio.png", f"$LOCALIZE[{S['audio']}]", "ActivateWindow(osdaudiosettings)", None),
    (70043, "vn/icons/info.png", f"$LOCALIZE[{S['info']}]", "Action(Info,fullscreenvideo)", None),
    (70048, "vn/icons/settings.png", f"$LOCALIZE[{S['settings']}]", "ActivateWindow(osdvideosettings)", None),
]


def icon_row():
    kids = [img(0, 0, 80, 40, "vn/clear.png", cid=9879)]         # room for the light / label (a grouplist clips)
    for cid, icon, lab, click, vis in ICONS:
        hf = f"Control.HasFocus({cid})"
        btn = NL.join([f'<control type="button" id="{cid}">', "\t<top>40</top>", "\t<width>104</width>", "\t<height>48</height>",
                       "\t<label></label>", "\t<texturefocus />", "\t<texturenofocus />", f"\t<onclick>{click}</onclick>",
                       "\t<onup>87</onup>", "\t<ondown>noop</ondown>", *([f"\t<visible>{vis}</visible>"] if vis else []), "</control>"])
        face = group([img(-46, -46, 140, 140, "vn/spot.png", "$VAR[spot]", vis=hf,
                          anims=['<animation effect="fade" start="100" end="73" time="0" condition="true">Conditional</animation>']),
                      img(0, 0, 48, 48, icon, "$VAR[ink]", vis=hf, aspect="keep"),
                      img(0, 0, 48, 48, icon, "$VAR[ink2]", vis=f"!{hf}", aspect="keep"),
                      label(-76, 56, 200, 36, lab, "font_label", "$VAR[ink]", align="center", aligny="center", vis=hf, selected=False)],
                     left=-104, top=40, width=104, height=48, vis=vis)
        kids += [btn, face.replace("<control type=\"group\">", f'<control type="group" id="{cid + 90000 if cid > 1000 else cid + 9000}">', 1)]
    return NL.join(['<control type="grouplist" id="9880">', "\t<left>944</left>", "\t<top>840</top>", "\t<width>976</width>",
                    "\t<height>200</height>", "\t<orientation>horizontal</orientation>", "\t<itemgap>0</itemgap>",
                    "\t<usecontrolcoords>true</usecontrolcoords>", "\t<onleft>noop</onleft>", "\t<onright>noop</onright>",
                    ind(NL.join(kids), 1), "</control>"])


def seek_line():
    return NL.join(['<control type="button" id="87">', f"\t<left>{X0}</left>", "\t<top>978</top>", f"\t<width>{LW}</width>",
                    "\t<height>44</height>", "\t<label></label>", "\t<texturefocus />", "\t<texturenofocus />",
                    "\t<onleft>StepBack</onleft>", "\t<onright>StepForward</onright>", "\t<onclick>PlayerControl(Play)</onclick>",
                    "\t<onup>noop</onup>", "\t<ondown>602</ondown>", "\t<onback>602</onback>",
                    "\t<visible>Player.SeekEnabled</visible>", "</control>"])


# ================================================================ windows
def osd():
    return group([pause_dim(), band(), corner_placard(cid=9881), progress_line(chip="$VAR[VOSD_SeekTime]", big="Control.HasFocus(87)"),
                  seek_line(), icon_row(), "<include>VN_Clock</include>"],
                 vis="![Window.IsVisible(osdaudiosettings) | Window.IsVisible(osdvideosettings) | Window.IsVisible(osdsubtitlesettings) | "
                     "Window.IsVisible(videobookmarks) | Window.IsVisible(fullscreeninfo) | Window.IsVisible(movieinformation)]",
                 anims=['<animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>',
                        '<animation effect="fade" start="100" end="0" time="150">WindowClose</animation>'])


def seekbar():
    """DialogSeekBar (Kodi shows it on pause and while seeking; VideoFullScreen's own controls are not drawn over the
    picture on the Shield, so the paused layer lives here): paused = the dim, the band, the paused corner placard and
    the line; seeking = the flat band, the line and the knob's time chip."""
    seeking = "[Player.Seeking | Player.HasPerformedSeek(3) | !String.IsEmpty(Player.SeekNumeric)]"
    kodi = NL.join(['<control type="slider" id="401">', "\t<left>offscreen</left>", "\t<top>offscreen</top>", "\t<width>1</width>",
                    "\t<height>1</height>", "\t<texturesliderbar />", "\t<textureslidernib />", "\t<textureslidernibfocus />", "</control>"])
    fade = ['<animation effect="fade" time="200">Visible</animation>', '<animation effect="fade" time="150">Hidden</animation>']
    return NL.join([pause_dim(),
                    group([band(), corner_placard(probes=(9886, 9887)), progress_line()], vis=f"{PAUSED} + !{seeking}", anims=fade),
                    group([band(full=False), progress_line(chip="$VAR[VOSD_SeekTime]", big="true")], vis=f"!{PAUSED} | {seeking}", anims=fade),
                    kodi])


def fullscreen_info():
    return NL.join([band(), corner_placard(width=900, plot=True, probes=(9884, 9885), paused_vis="false"), progress_line()])


def main():
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_playback.py - edit the generator, then re-run. Playback: VideoOSD, DialogSeekBar,
     DialogFullScreenInfo, VideoFullScreen's paused layer (docs/skin.vernissage/screens/VideoOSD.md, board 08). -->
<includes>
{variables()}

	<!-- VideoOSD: band, corner placard, progress line + seek line 87, the icon row (rule 6 order) -->
	<include name="VOSD_Window">
{ind(osd(), 2)}
	</include>

	<!-- DialogSeekBar: paused = dim, band, the paused placard, the line; seeking = the flat band, the line, the chip -->
	<include name="VOSD_SeekBar">
{ind(seekbar(), 2)}
	</include>

	<!-- DialogFullScreenInfo: the wide corner placard with the plot (asked for, so it may be read) -->
	<include name="VOSD_FullScreenInfo">
{ind(fullscreen_info(), 2)}
	</include>
</includes>
"""
    OUT.write_text(body, encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {body.count('<control')} controls, {len(body) // 1024} KB")


if __name__ == "__main__":
    main()
