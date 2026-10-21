"""Groove music playback lane (skin-developer, M3, 2026-10-21): generate the two include files of the lane.

    python skins/skin.groove/_src/make_player.py

Writes (GENERATED, edit here and re-run):
  1080i/Includes_Player.xml     Now Playing: room glow, record (disc art / vinyl), sleeve, tonearm, right column,
                                progress line, tray (MusicOSD), Up next stack, video lookup, mini player.
  1080i/Includes_MusicInfo.xml  Liner notes page (player / album-info sources), DialogMusicInfo pieces.
Hand-written windows that call them: MusicVisualisation.xml, MusicOSD.xml, DialogMusicInfo.xml.

WHY THE TRAY LIVES IN MusicOSD (read before changing the structure)
  Kodi's keymap maps the d-pad in the Visualisation window to actions, not moves (keyboard.xml <Visualisation>:
  left StepBack, right StepForward, up SkipNext, down SkipPrevious, enter OSD, backspace FullScreen). A focusable
  tray inside MusicVisualisation.xml can never be walked with the remote. So MusicVisualisation.xml draws the stage
  (room, record, arm, words, progress line) and opens MusicOSD in its onload; MusicOSD (a modal dialog with the
  normal keymap) holds every focusable control: tray 9601-9609, progress 9620, Up next 9631-9640, Liner notes
  9651-9670, wake catcher 9690. Back on the tray closes the OSD AND leaves Now Playing (Action(FullScreen,...)).
  MusicOSD is modal, so the record's "stop under a modal dialog" test excludes it (Window.IsModalDialogTopmost).

Geometry: docs/skin.groove/screens/MusicVisualisation_NowPlaying.md, UpNextStack.md, LinerNotes.md, MiniPlayer.md,
DialogMusicInfo_Album.md, DialogMusicInfo_Artist.md; boards B3/B4/B5/B12. Tonearm: DESIGN 8 (texture pivot 70,60,
L 340; outer groove 105.6 deg, inner 132.2 deg, screen clockwise; Kodi rotate is counter-clockwise for positive).
Write generator edits with the file tools, never a shell heredoc (LESSONS, backslashes).
"""
from __future__ import annotations

import math
from itertools import product
from pathlib import Path

SKIN = Path(__file__).resolve().parent.parent
OUT_PLAYER = SKIN / "1080i" / "Includes_Player.xml"
OUT_INFO = SKIN / "1080i" / "Includes_MusicInfo.xml"

RM = "Skin.HasSetting(groove.reducemotion)"
VIZ = "$EXP[NP_VizMode]"
LIGHT = "$EXP[GrooveLight]"
HELPER = "$EXP[HasGrooveHelper]"   # the shared HELPER_API 0 guard (Includes_Groove.xml)
# No-helper shuffled play (DEVICE_AUDIT M1, DATA 5): append a songs xsp with random order to the item's library node.
# Never PlayerControl(RandomOn|RandomOff|Random) from a play action: it SAVES Kodi's music shuffle setting for good.
# {"type":"songs","order":{"method":"random"}}
RANDOM_SONGS = "?xsp=%7B%22type%22%3A%22songs%22%2C%22order%22%3A%7B%22method%22%3A%22random%22%7D%7D"

# ------------------------------------------------------------------ geometry (screens/MusicVisualisation_NowPlaying.md)
SLEEVE = (150, 150, 620)                 # x, y, size
DISC = (520, 170, 580)                   # x, y, size -> centre 810, 460
DISC_C = (810, 460)
LABEL = 196                              # 0.335 x 580 x 1.01 (board): the cover label of the fallback vinyl
PIVOT = (1160, 210)
ARM_TEX = (70, 60, 440, 120)             # pivot pixel in tonearm.png, canvas size
ARM_OUTER, ARM_INNER = 105.6, 132.2      # screen degrees, clockwise (DESIGN 8)
TRAY_Y, TRAY_ICON = 950, 48
PROG = (150, 852, 1620)                  # x, y, width

TRAY = [  # id, key, 8-slot index, 9-slot index
    (9601, "previous", 0, 0), (9602, "play", 1, 1), (9603, "next", 2, 2), (9604, "upnext", 3, 3),
    (9605, "liner", 4, 4), (9606, "viz", 5, 5), (9607, "watch", None, 6), (9608, "shuffle", 6, 7),
    (9609, "repeat", 7, 8),
]
TRAY_IDS = [t[0] for t in TRAY]

# Up next fan (UpNextStack.md / MOTION 5.13)
CARD = (1130, 340, 290)                  # base card x, y, size; pivot = bottom-left corner
CARD_PIVOT = (1130, 630)
FAN = 5.5                                # degrees per depth step, counter-clockwise (Kodi positive)
LIFT = (1436, 200, 324)                  # walked card x, y, size
LIFT_C = (LIFT[0] + LIFT[2] / 2, LIFT[1] + LIFT[2] / 2)
LIFT_ROT = -2                            # Kodi degrees (CSS +2)


def x8(i):
    return 150 + 216 * i


def x9(i):
    return 96 + 196 * i


def esc(s: str) -> str:
    return s.replace("&", "&amp;")


def block(lines, n):
    pad = "\t" * n
    return "\n".join(pad + ln if ln else ln for ln in "\n".join(lines).split("\n"))


def img(x, y, w, h, tex, diffuse=None, extra="", tex_attr="", aspect=None):
    cd = f' colordiffuse="{diffuse}"' if diffuse else ""
    # a mask on cropped art stays on the control rect (scalediffuse false), DEVICE_AUDIT m7
    sd = ' scalediffuse="false"' if aspect == "scale" and ' diffuse="groove/' in tex_attr else ""
    a = f"\n\t<aspectratio{sd}>{aspect}</aspectratio>" if aspect else ""
    return (f'<control type="image">\n\t<left>{x}</left>\n\t<top>{y}</top>\n\t<width>{w}</width>\n\t<height>{h}</height>'
            f'{a}\n\t<texture{cd}{tex_attr}>{tex}</texture>' + (f"\n{block([extra], 1)}" if extra else "") + "\n</control>")


def label(x, y, w, h, text, font, color, extra="", align=None, aligny="center"):
    al = f"\n\t<align>{align}</align>" if align else ""
    return (f'<control type="label">\n\t<left>{x}</left>\n\t<top>{y}</top>\n\t<width>{w}</width>\n\t<height>{h}</height>'
            f"{al}\n\t<aligny>{aligny}</aligny>\n\t<font>{font}</font>\n\t<textcolor>{color}</textcolor>"
            f"\n\t<label>{text}</label>" + (f"\n{block([extra], 1)}" if extra else "") + "\n</control>")


def rim(x, y, w, h, color, t=2):
    return "\n".join([
        img(x, y, w, t, "groove/white.png", color),
        img(x, y + h - t, w, t, "groove/white.png", color),
        img(x, y + t, t, h - 2 * t, "groove/white.png", color),
        img(x + w - t, y + t, t, h - 2 * t, "groove/white.png", color),
    ])


def cond_anim(effect_xml, condition, reversible=True, rm_effect=None):
    """A Conditional animation with its reduce-motion twin (rm_effect None = no twin)."""
    r = "true" if reversible else "false"
    out = [f'<animation type="Conditional" condition="{condition} + !{RM}" reversible="{r}">', block([effect_xml], 1),
           "</animation>"]
    if rm_effect:
        out += [f'<animation type="Conditional" condition="{condition} + {RM}" reversible="{r}">', block([rm_effect], 1),
                "</animation>"]
    return "\n".join(out)


def fade_cond(condition, to, t=160):
    """Reversible dim (fades are not motion: the same in both motion modes)."""
    return (f'<animation type="Conditional" condition="{condition}" reversible="true">'
            f'<effect type="fade" start="100" end="{to}" time="{t}" tween="cubic" easing="out"/></animation>')


def static_rotate(angle, center):
    return f'<animation effect="rotate" end="{angle:g}" center="{center}" time="0" condition="true">Conditional</animation>'


# =============================================================================================== Includes_Player.xml
def player_vars():
    o = []
    o.append("<!-- ============================================================ expressions -->")
    o.append("<!-- Visualiser mode: the setting AND a visualiser exists (with none set in Kodi the record shows). -->")
    o.append('<expression name="NP_VizMode">Skin.HasSetting(groove.np.viz) + Visualisation.Enabled</expression>')
    o.append("<!-- Printed disc art for the playing song (DATA 6.2 chain), unless the Record setting says Always vinyl. -->")
    o.append('<expression name="NP_HasDisc">!String.IsEqual(Skin.String(groove.record),vinyl) + [!String.IsEmpty(Player.Art(discart)) | !String.IsEmpty(Player.Art(album.discart)) | !String.IsEmpty(Player.Art(album.discart1))]</expression>')
    o.append('<expression name="NP_HasCover">!String.IsEmpty(Player.Art(thumb))</expression>')
    o.append("<!-- TMDb Helper's blur of the playing cover (Timers.xml groove_np_colours) belongs to this cover -->")
    o.append('<expression name="NP_BlurReady">!String.IsEmpty(Window(Home).Property(TMDbHelper.GroovePlayer.BlurImage)) + String.IsEqual(Window(Home).Property(groove.np.colorsrc),Player.Art(thumb))</expression>')
    o.append('<expression name="NP_HasLogo">!String.IsEmpty(Player.Art(artist.clearlogo)) | !String.IsEmpty(Player.Art(albumartist.clearlogo))</expression>')
    o.append("<!-- Watch the video: YouTube installed + the song has a video link (DATA 6.4, lookup list 9695 in MusicOSD). -->")
    o.append('<expression name="NP_NineSlots">System.HasAddon(plugin.video.youtube) + System.AddonIsEnabled(plugin.video.youtube) + !String.IsEmpty(Container(9695).ListItem.SongVideoURL) + String.IsEqual(Container(9695).ListItem.Title,MusicPlayer.Title)</expression>')
    o.append("<!-- Up next: a card is picked up (helper only) -->")
    o.append('<expression name="NP_PickMode">!String.IsEmpty(Window(Home).Property(groove.upnext.pick))</expression>')
    o.append("<!-- the record stops while the Liner notes page covers it (set by the page's scrollers, cleared by the tray) -->")
    o.append('<expression name="NP_LinerOpen">String.IsEqual(Window(Home).Property(groove.np.overlay),liner)</expression>')
    o.append("<!-- a modal dialog OTHER than MusicOSD (MusicOSD is itself modal and is always up on Now Playing) -->")
    o.append('<expression name="NP_OtherModal">System.HasActiveModalDialog + !Window.IsModalDialogTopmost(musicosd)</expression>')
    o.append("")
    o.append("<!-- ============================================================ variables -->")
    o.append('<variable name="NP_Disc">')
    o.append("\t<value condition=\"!String.IsEmpty(Player.Art(discart))\">$INFO[Player.Art(discart)]</value>")
    o.append("\t<value condition=\"!String.IsEmpty(Player.Art(album.discart))\">$INFO[Player.Art(album.discart)]</value>")
    o.append("\t<value>$INFO[Player.Art(album.discart1)]</value>")
    o.append("</variable>")
    o.append('<variable name="NP_Logo">')
    o.append("\t<value condition=\"!String.IsEmpty(Player.Art(artist.clearlogo))\">$INFO[Player.Art(artist.clearlogo)]</value>")
    o.append("\t<value>$INFO[Player.Art(albumartist.clearlogo)]</value>")
    o.append("</variable>")
    o.append("<!-- The playing album's colour: glow_playing (Includes_Theme.xml, HELPER_API 6 priority). -->")
    o.append('<variable name="NP_Glow"><value>$VAR[glow_playing]</value></variable>')
    o.append("<!-- helper soft art of the playing album for the room wash (Light room: the pastel variant) -->")
    o.append('<variable name="NP_SoftArt">')
    o.append(f"\t<value condition=\"{LIGHT} + !String.IsEmpty(Window(Home).Property(Groove.Player.Art.SoftLight))\">$INFO[Window(Home).Property(Groove.Player.Art.SoftLight)]</value>")
    o.append("\t<value>$INFO[Window(Home).Property(Groove.Player.Art.Soft)]</value>")
    o.append("</variable>")
    o.append('<variable name="NP_AlbumYear">')
    o.append("\t<value condition=\"!String.IsEmpty(MusicPlayer.Album) + !String.IsEmpty(MusicPlayer.Year)\">$INFO[MusicPlayer.Album] · $INFO[MusicPlayer.Year]</value>")
    o.append("\t<value condition=\"!String.IsEmpty(MusicPlayer.Album)\">$INFO[MusicPlayer.Album]</value>")
    o.append("\t<value>$INFO[MusicPlayer.Year]</value>")
    o.append("</variable>")
    for name, pairs in [
        ("NP_PlayIcon", [("Player.Paused", "icons/play.png"), (None, "icons/pause.png")]),
        ("NP_PlayLabel", [("Player.Paused", "$LOCALIZE[31702]"), (None, "$LOCALIZE[31703]")]),
        ("NP_VizIcon", [(VIZ, "icons/record.png"), (None, "icons/visualiser.png")]),
        ("NP_VizLabel", [(VIZ, "$LOCALIZE[31708]"), (None, "$LOCALIZE[31707]")]),
        ("NP_RepeatIcon", [("Playlist.IsRepeatOne", "icons/repeat-one.png"), (None, "icons/repeat.png")]),
        ("NP_LinerLabel", [("$EXP[NP_NineSlots]", "$LOCALIZE[31737]"), (None, "$LOCALIZE[31706]")]),
        ("NP_WatchLabel", [(None, "$LOCALIZE[31736]")]),
    ]:
        o.append(f'<variable name="{name}">')
        for c, v in pairs:
            o.append(f'\t<value condition="{c}">{v}</value>' if c else f"\t<value>{v}</value>")
        o.append("</variable>")
    o.append("<!-- \"+N\" under the Up next pile = songs queued after the sixth card (XML can't subtract: the highest")
    o.append("     offset that exists). Hidden with repeat all (the queue is a loop then). -->")
    o.append('<variable name="NP_UpNextRest">')
    for k in range(60, 6, -1):
        o.append(f'\t<value condition="MusicPlayer.offset({k}).Exists">+{k - 6}</value>')
    o.append("</variable>")
    o.append("<!-- Watch the video: the playing song itself, by database id (DATA 6.4). No free text in the path, so nothing")
    o.append("     to URL-encode (official review: xml.xsp-unencoded); a file outside the library has no id and no video. -->")
    o.append('<variable name="NP_VideoPath">')
    o.append('\t<value condition="Integer.IsGreater(MusicPlayer.DBID,0)">musicdb://songs/?songid=$INFO[MusicPlayer.DBID]</value>')
    o.append("</variable>")
    o.append("<!-- m:ss like the board (Kodi pads Player.Time to mm:ss); h:mm:ss for tracks of an hour or more -->")
    o.append('<variable name="NP_TimeElapsed">')
    o.append('	<value condition="Integer.IsGreaterOrEqual(Player.Duration,3600)">$INFO[Player.Time(h:mm:ss)]</value>')
    o.append('	<value>$INFO[Player.Time(m)]:$INFO[Player.Time(ss)]</value>')
    o.append("</variable>")
    o.append('<variable name="NP_TimeRemaining">')
    o.append('	<value condition="Integer.IsGreaterOrEqual(Player.Duration,3600)">-$INFO[Player.TimeRemaining(h:mm:ss)]</value>')
    o.append('	<value>-$INFO[Player.TimeRemaining(m)]:$INFO[Player.TimeRemaining(ss)]</value>')
    o.append("</variable>")
    o.append("<!-- mini player ring: 101 frames named 000..100 from Player.Progress (an integer) -->")
    o.append('<variable name="Mini_Ring">')
    for k in range(100, 0, -1):
        o.append(f'\t<value condition="Integer.IsGreaterOrEqual(Player.Progress,{k})">groove/progress_ring/{k:03d}.png</value>')
    o.append("\t<value>groove/progress_ring/000.png</value>")
    o.append("</variable>")
    return o


def np_spin_anims(center, stop):
    """The record's loop (MOTION 5.12) with NP_OtherModal instead of System.HasActiveModalDialog (MusicOSD is modal)."""
    loop = (f"Player.HasAudio + !{RM} + !$EXP[NP_VizMode] + !System.ScreenSaverActive + ![{stop}]"
            f" + [[!Player.Paused + !$EXP[NP_OtherModal]] | !System.IdleTime(1)]")
    halt = f"Player.Paused | $EXP[NP_OtherModal] | System.ScreenSaverActive | {RM} | [{stop}]"
    return "\n".join([
        f'<animation type="Conditional" condition="{loop}" reversible="false" loop="true">',
        f'\t<effect type="rotate" start="0" end="-360" center="{center}" time="1800" tween="linear"/>',
        "</animation>",
        f'<animation type="Conditional" condition="{halt}" reversible="true">',
        '\t<effect type="fade" start="100" end="0" time="150"/>',
        "</animation>",
    ])


def record_layers(prefix_vis, spinning):
    """One copy of the record: printed disc art, or vinyl + the cover as its label (rotate together)."""
    dx, dy, ds = DISC
    lx = DISC_C[0] - LABEL // 2
    ly = DISC_C[1] - LABEL // 2
    o = ['<control type="group">']
    if spinning:
        o.append(block([np_spin_anims(f"{DISC_C[0]},{DISC_C[1]}", "$EXP[NP_LinerOpen]")], 1))
    vinyl = [
        img(lx, ly, LABEL, LABEL, "groove/disc_mask.png", "black"),
        img(lx, ly, LABEL, LABEL, "$INFO[Player.Art(thumb)]", tex_attr=' background="true" diffuse="groove/disc_mask.png"',
            aspect="scale", extra="<include>Anim_ArtFadetime</include>"),
        img(dx, dy, ds, ds, "groove/vinyl.png"),
    ]
    o += ['\t<control type="group">', "\t\t<visible>!$EXP[NP_HasDisc]</visible>", block(vinyl, 2), "\t</control>"]
    o.append(block([img(dx, dy, ds, ds, "$VAR[NP_Disc]", tex_attr=' background="true"', aspect="keep",
                        extra="<visible>$EXP[NP_HasDisc]</visible>\n<include>Anim_ArtFadetime</include>")], 1))
    o.append("</control>")
    return "\n".join(o)


def inc_np_curtain():
    return "\n".join([
        "<!-- The room over the visualisation: fades out in Visualiser mode (MOTION 5.12). Fixed textures per Room",
        "     setting, so the Light paper dissolves into the dark visualiser instead of flipping first. -->",
        '<include name="NP_Curtain">',
        '\t<control type="group">',
        block([cond_anim('<effect type="fade" start="100" end="0" time="400" tween="cubic" easing="out"/>', VIZ,
                         rm_effect='<effect type="fade" start="100" end="0" time="150"/>')], 2),
        block([img(0, 0, 1920, 1080, "groove/dark/room.png", extra="<visible>!Skin.HasSetting(groove.light)</visible>"),
               img(0, 0, 1920, 1080, "groove/light/room.png", extra="<visible>Skin.HasSetting(groove.light)</visible>")], 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_glow():
    sx, sy, ss = SLEEVE
    cx, cy = sx + ss // 2, sy + ss // 2
    halo = 1180
    pool = 1488
    dhalo = 986
    wash = ('<control type="image">\n\t<left>-800</left>\n\t<top>-480</top>\n\t<width>3000</width>\n\t<height>1900</height>'
            '\n\t<aspectratio>stretch</aspectratio>\n\t<texture background="true" diffuse="groove/wash_mask.png" colordiffuse="$VAR[wash]">{tex}</texture>'
            '\n\t<visible>{vis}</visible>\n\t<include>Anim_GlowFadetime</include>\n</control>')
    return "\n".join([
        "<!-- Room light of the playing album (DESIGN 6): wash (helper soft art, else the cover itself through the",
        "     mask), the Light room's pool, the halo behind the sleeve and, with disc art, behind the disc. -->",
        '<include name="NP_RoomGlow">',
        '\t<control type="group">',
        f"\t\t<visible>!{VIZ}</visible>",
        "\t\t<include>Anim_StageToggle</include>",
        block([wash.format(tex="$VAR[NP_SoftArt]", vis="$EXP[HasGrooveHelper] + !String.IsEmpty(Window(Home).Property(Groove.Player.Art.Soft))"),
               wash.format(tex="$INFO[Window(Home).Property(TMDbHelper.GroovePlayer.BlurImage)]",
                           vis="![$EXP[HasGrooveHelper] + !String.IsEmpty(Window(Home).Property(Groove.Player.Art.Soft))] + $EXP[NP_BlurReady]"),
               img(cx - pool // 2, cy - pool // 2, pool, pool, "groove/glow_radial.png", "$VAR[art_pool]",
                   extra=f"<visible>{LIGHT}</visible>"),
               img(cx - halo // 2, cy - halo // 2, halo, halo, "groove/glow_radial.png", "$VAR[NP_Glow]",
                   extra="<include>Groove_GlowStrength</include>"),
               img(DISC_C[0] - dhalo // 2, DISC_C[1] - dhalo // 2, dhalo, dhalo, "groove/glow_radial.png", "$VAR[NP_Glow]",
                   extra="<visible>$EXP[NP_HasDisc]</visible>\n<include>Groove_GlowStrength</include>"
                         '\n<animation effect="fade" start="100" end="70" time="0" condition="true">Conditional</animation>')], 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_record():
    dx, dy, ds = DISC
    sh = 768                                      # shadow_disc's circle is 200/256 of the texture
    sheen = img(dx, dy, ds, ds, "groove/vinyl_sheen.png", extra="<visible>!$EXP[NP_HasDisc]</visible>")
    spindle = img(DISC_C[0] - 9, DISC_C[1] - 9, 18, 18, "groove/spindle.png", extra="<visible>!$EXP[NP_HasDisc]</visible>")
    return "\n".join([
        "<!-- The record: slides out of the sleeve on open (600 ms) and turns (1.8 s per turn). A still copy lies under",
        "     the spinning one; on pause / dialog / screensaver / Reduce motion / Liner notes the spinning copy fades",
        "     out and its loop stops a second later (MOTION 5.12). Drawn BEFORE the sleeve (it comes from behind it). -->",
        '<include name="NP_Record">',
        '\t<control type="group">',
        f"\t\t<visible>!{VIZ}</visible>",
        '\t\t<include content="Anim_RecordSlideOut"><param name="dx" value="-350"/></include>',
        block([img(DISC_C[0] - sh // 2, DISC_C[1] - sh // 2 + 22, sh, sh, "groove/shadow_disc.png", "$VAR[shadow]"),
               record_layers("", spinning=False),
               record_layers("", spinning=True),
               sheen, spindle], 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_sleeve():
    sx, sy, ss = SLEEVE
    cast = int(ss * 1.5)
    parts = [
        img(ss // 2 - cast // 2, ss // 2 + 40 - cast // 2, cast, cast, "groove/shadow_cast.png", "$VAR[NP_Glow]",
            extra=f"<visible>{LIGHT}</visible>"),
        '<control type="image">\n\t<left>-96</left>\n\t<top>-60</top>\n\t<width>812</width>\n\t<height>800</height>'
        '\n\t<texture border="96,60,96,120" colordiffuse="$VAR[shadow]">groove/shadow_square.png</texture>\n</control>',
        img(0, 0, ss, ss, "$VAR[Tex_SleeveBack]", extra="<visible>!$EXP[NP_HasCover]</visible>"),
        '<control type="textbox">\n\t<left>60</left>\n\t<top>220</top>\n\t<width>500</width>\n\t<height>180</height>'
        '\n\t<align>center</align>\n\t<aligny>center</aligny>\n\t<font>font_title</font>\n\t<textcolor>$VAR[ink2]</textcolor>'
        '\n\t<label>$INFO[MusicPlayer.Album]</label>\n\t<visible>!$EXP[NP_HasCover]</visible>\n</control>',
        img(0, 0, ss, ss, "$INFO[Player.Art(thumb)]", tex_attr=' background="true"', aspect="scale",
            extra="<visible>$EXP[NP_HasCover]</visible>\n<include>Anim_ArtFadetime</include>"),
        rim(0, 0, ss, ss, "$VAR[rim_soft]"),
    ]
    return "\n".join([
        "<!-- The sleeve (620 px), drawn above the record. Light room: the cover casts a coloured shadow. -->",
        '<include name="NP_Sleeve">',
        '\t<control type="group">',
        f"\t\t<left>{sx}</left>\n\t\t<top>{sy}</top>\n\t\t<width>{ss}</width>\n\t\t<height>{ss}</height>",
        f"\t\t<visible>!{VIZ}</visible>",
        "\t\t<include>Anim_StageToggle</include>",
        block(parts, 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_tonearm():
    px, py = PIVOT
    tx, ty, tw, th = ARM_TEX
    step = (ARM_INNER - ARM_OUTER) / 100
    steps = [f'<include content="Anim_TonearmStep"><param name="k" value="{k}"/><param name="step" value="{step:.3f}"/>'
             f'<param name="pivot" value="{px},{py}"/></include>' for k in range(1, 101)]
    return "\n".join([
        f"<!-- Tonearm: one canvas pointing +x, pivot pixel {tx},{ty}; rotated about the screen pivot {px},{py} to the",
        f"     outer groove ({ARM_OUTER} deg clockwise) and one 0.266 deg step per Player.Progress percent toward the",
        f"     inner groove ({ARM_INNER} deg). Lifts 6 deg and fades to 55 % on pause; swings in on open. -->",
        '<include name="NP_Tonearm">',
        '\t<control type="group">',
        f"\t\t<visible>!{VIZ}</visible>",
        "\t\t<include>Anim_StageToggle</include>",
        f'\t\t<include content="Anim_TonearmSwingIn"><param name="pivot" value="{px},{py}"/><param name="angle" value="20"/></include>',
        '\t\t<control type="group">',
        f"\t\t\t{static_rotate(-ARM_OUTER, f'{px},{py}')}",
        block(steps, 3),
        f'\t\t\t<include content="Anim_TonearmLift"><param name="pivot" value="{px},{py}"/><param name="angle" value="6"/></include>',
        '\t\t\t<animation effect="fade" start="100" end="55" time="300" condition="Player.Paused" reversible="true">Conditional</animation>',
        block([img(px - tx + 8, py - ty + 14, tw, th, "groove/tonearm_shadow.png", "$VAR[shadow]"),
               img(px - tx, py - ty, tw, th, "groove/tonearm.png")], 3),
        "\t\t</control>",
        "\t</control>",
        "</include>",
    ])


def inc_np_info():
    parts = [
        '<control type="image">\n\t<left>1290</left>\n\t<top>250</top>\n\t<width>534</width>\n\t<height>150</height>'
        '\n\t<aspectratio align="left" aligny="bottom">keep</aspectratio>'
        '\n\t<texture background="true" colordiffuse="$VAR[logo_tint]">$VAR[NP_Logo]</texture>'
        '\n\t<visible>$EXP[NP_HasLogo]</visible>\n\t<include>Anim_ArtFadetime</include>\n</control>',
        label(1290, 340, 534, 60, "$INFO[MusicPlayer.Artist]", "font_name_light", "$VAR[ink2]",
              extra="<visible>!$EXP[NP_HasLogo]</visible>"),
        label(1290, 440, 534, 70, "$INFO[MusicPlayer.Title]", "font_np_title", "$VAR[ink]"),
        label(1290, 524, 534, 40, "$VAR[NP_AlbumYear]", "font_lead", "$VAR[ink2]"),
    ]
    return "\n".join([
        "<!-- Right column: clearlogo (else the name in Light), title, album · year. One line each, ellipsis. -->",
        '<include name="NP_Info">',
        '\t<control type="group">',
        f"\t\t<visible>!{VIZ}</visible>",
        "\t\t<include>Anim_StageToggle</include>",
        '\t\t<include content="Anim_OpenEnter"><param name="dx" value="24"/><param name="dy" value="0"/><param name="delay" value="120"/><param name="t" value="280"/></include>',
        '\t\t<include content="Anim_Dim"><param name="condition" value="String.IsEqual(Window(Home).Property(groove.np.overlay),upnext)"/><param name="to" value="0"/></include>',
        block(parts, 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_vizcaption():
    return "\n".join([
        "<!-- Visualiser mode: a dark scrim at the bottom + \"Title · Artist\"; fades out after 4 s idle. -->",
        '<include name="NP_VizCaption">',
        '\t<control type="group">',
        f"\t\t<visible>{VIZ}</visible>",
        "\t\t<include>Anim_StageToggle</include>",
        '\t\t<include content="Anim_IdleFade"><param name="condition" value="System.IdleTime(4)"/><param name="to" value="0"/></include>',
        block([img(0, 640, 1920, 440, "groove/ramp_v_up.png", "$VAR[ground]"),
               '<control type="grouplist">\n\t<left>150</left>\n\t<top>780</top>\n\t<width>1620</width>\n\t<height>48</height>'
               '\n\t<orientation>horizontal</orientation>\n\t<itemgap>16</itemgap>\n\t<usecontrolcoords>true</usecontrolcoords>\n'
               + block([
                   '<control type="label" id="9681">\n\t<width max="1000">auto</width>\n\t<height>48</height>\n\t<aligny>center</aligny>'
                   '\n\t<font>font_caption</font>\n\t<textcolor>$VAR[ink]</textcolor>\n\t<label>$INFO[MusicPlayer.Title]</label>\n</control>',
                   '<control type="label" id="9682">\n\t<width max="600">auto</width>\n\t<height>48</height>\n\t<aligny>center</aligny>'
                   '\n\t<font>font_caption_light</font>\n\t<textcolor>$VAR[ink2]</textcolor>\n\t<label>$INFO[MusicPlayer.Artist,·  ,]</label>\n</control>',
               ], 1) + "\n</control>"], 2),
        "\t</control>",
        "</include>",
    ])


def progress_parts(time_color, extra_fill=True):
    x, y, w = PROG
    o = []
    if extra_fill:
        o.append('<control type="progress">\n'
                 f"\t<left>{x}</left>\n\t<top>{y - 3}</top>\n\t<width>{w}</width>\n\t<height>8</height>\n"
                 '\t<texturebg colordiffuse="clear">groove/white.png</texturebg>\n\t<lefttexture />\n'
                 '\t<midtexture border="2" colordiffuse="$VAR[ink]">groove/pill.png</midtexture>\n'
                 "\t<righttexture />\n\t<overlaytexture />\n\t<info>Player.Progress</info>\n</control>")
    o.append(label(x, y + 12, 600, 34, "$VAR[NP_TimeElapsed]", "font_small", time_color))
    o.append(label(x + w - 600, y + 12, 600, 34, "$VAR[NP_TimeRemaining]", "font_small", time_color, align="right"))
    return o


def inc_np_progress():
    x, y, w = PROG
    return "\n".join([
        "<!-- Progress line (2 px track, 4 px fill) + elapsed / remaining. Fades with the tray in Visualiser mode. -->",
        '<include name="NP_Progress">',
        '\t<control type="group">',
        f'\t\t<include content="Anim_IdleFade"><param name="condition" value="{VIZ} + System.IdleTime(4)"/><param name="to" value="0"/></include>',
        block([img(x, y, w, 2, "groove/white.png", "$VAR[line]")] + progress_parts("$VAR[ink2]"), 2),
        "\t</control>",
        "</include>",
    ])


def tray_icon(key):
    return {"previous": "icons/previous.png", "play": "$VAR[NP_PlayIcon]", "next": "icons/next.png",
            "upnext": "icons/upnext.png", "liner": "icons/liner.png", "viz": "$VAR[NP_VizIcon]",
            "watch": "icons/watchvideo.png", "shuffle": "icons/shuffle.png", "repeat": "$VAR[NP_RepeatIcon]"}[key]


def tray_label(key):
    return {"previous": "$LOCALIZE[31701]", "play": "$VAR[NP_PlayLabel]", "next": "$LOCALIZE[31704]",
            "upnext": "$LOCALIZE[31705]", "liner": "$VAR[NP_LinerLabel]", "viz": "$VAR[NP_VizLabel]",
            "watch": "$VAR[NP_WatchLabel]", "shuffle": "$LOCALIZE[31710]", "repeat": "$LOCALIZE[31711]"}[key]


TRAY_MARK = {"shuffle": "Playlist.IsRandom", "repeat": "Playlist.IsRepeat | Playlist.IsRepeatOne",
             "upnext": "ControlGroup(9630).HasFocus()"}
TRAY_VIS = {"viz": "Visualisation.Enabled", "watch": "$EXP[NP_NineSlots]"}
TRAY_ENABLE = {"next": "MusicPlayer.HasNext | Playlist.IsRepeat | Playlist.IsRepeatOne"}


def tray_slot(tid, key, i8, i9, interactive=True):
    """One tray slot: soft glow, icon, one-word label, state dot, invisible 48 px button (MusicOSD only)."""
    x = x8(i8) if i8 is not None else x9(i9)
    dx = x9(i9) - x
    origin = "upnext" if key == "upnext" else None
    o = ['<control type="group">', f"\t<left>{x}</left>\n\t<top>{TRAY_Y}</top>\n\t<width>48</width>\n\t<height>48</height>"]
    if dx:
        o.append(f'\t<animation effect="slide" end="{dx},0" time="0" condition="$EXP[NP_NineSlots]">Conditional</animation>')
    if key in TRAY_VIS:
        o.append(f"\t<visible>{TRAY_VIS[key]}</visible>")
    if not interactive:
        o.append(block([img(0, 0, 48, 48, tray_icon(key), "$VAR[ink3]")], 1))
        if key in TRAY_MARK and key != "upnext":
            o.append(block([img(20, 62, 8, 8, "groove/dot.png", "$VAR[ink3]", extra=f"<visible>{TRAY_MARK[key]}</visible>")], 1))
        o.append("</control>")
        return "\n".join(o)
    foc = f"Control.HasFocus({tid})"
    icon_anims = [fade_cond(f"!{foc}" + (" + !ControlGroup(9630).HasFocus()" if origin else ""), 54)]
    if key in TRAY_ENABLE:
        icon_anims.append(f'<animation effect="fade" start="100" end="55" time="0" condition="![{TRAY_ENABLE[key]}]">Conditional</animation>')
    if not origin:
        icon_anims.append(fade_cond("ControlGroup(9630).HasFocus()", 55, 200))
    parts = [
        img(-34, -34, 116, 116, "groove/glow_radial.png", "$VAR[focus_glow]", extra=f"<visible>{foc}</visible>\n<include>Anim_FadeVisible</include>"),
        img(0, 0, 48, 48, tray_icon(key), "$VAR[ink]", extra="\n".join(icon_anims)),
        label(60, 0, 170, 48, tray_label(key), "font_tray", "$VAR[ink]", extra=f"<visible>{foc}</visible>\n<include>Anim_LabelReveal</include>"),
    ]
    if key in TRAY_MARK:
        parts.append(img(20, 62, 8, 8, "groove/dot.png", "$VAR[ink]", extra=f"<visible>{TRAY_MARK[key]}</visible>"))
    o.append(block(parts, 1))
    # the button
    idx = TRAY_IDS.index(tid)
    left = TRAY_IDS[idx - 1] if idx > 0 else None
    right = TRAY_IDS[idx + 1] if idx < len(TRAY_IDS) - 1 else None
    onclick = {
        "previous": ["PlayerControl(Previous)"],
        "play": ["PlayerControl(Play)"],
        "next": ["PlayerControl(Next)"],
        "upnext": ['condition="MusicPlayer.offset(1).Exists">SetFocus(9631)', 'condition="!MusicPlayer.offset(1).Exists">SetFocus(9640)'],
        "liner": None,
        "viz": ["Skin.ToggleSetting(groove.np.viz)"],
        "watch": ["PlayMedia($ESCINFO[Container(9695).ListItem.SongVideoURL])"],
        "shuffle": ["PlayerControl(Random)"],
        "repeat": ["PlayerControl(Repeat)"],
    }[key]
    b = [f'<control type="button" id="{tid}">', "\t<left>0</left>\n\t<top>0</top>\n\t<width>48</width>\n\t<height>48</height>",
         "\t<label></label>\n\t<texturefocus />\n\t<texturenofocus />"]
    if key in TRAY_ENABLE:
        b.append(f"\t<enable>{TRAY_ENABLE[key]}</enable>")
    b.append(f"\t<onfocus>SetProperty(groove.tray.last,{tid},home)</onfocus>")
    b.append("\t<onfocus>ClearProperty(groove.np.overlay,home)</onfocus>")
    if onclick is None:
        b.append("\t<include>Liner_Open_player</include>")
    else:
        for a in onclick:
            if a.startswith("condition="):
                b.append(f"\t<onclick {a}</onclick>")
            else:
                b.append(f"\t<onclick>{a}</onclick>")
    if left:
        b.append(f"\t<onleft>{left}</onleft>")
    if right:
        b.append(f"\t<onright>{right}</onright>")
    b.append("\t<onup>9620</onup>")
    b.append('\t<onback condition="Window.IsActive(visualisation)">Action(FullScreen,visualisation)</onback>')
    b.append("</control>")
    o.append(block(["\n".join(b)], 1))
    o.append("</control>")
    return "\n".join(o)


def inc_np_tray():
    slots = [tray_slot(t, k, a, b) for t, k, a, b in TRAY]
    return "\n".join([
        "<!-- The tray (MusicOSD): 8 fixed slots at pitch 216 from x 150; with Watch video, 9 slots at pitch 196 from",
        "     x 96 (time-0 slides, nothing re-flows). Hidden / disabled slots are skipped by Kodi's fall-through (a hidden",
        "     numeric target passes the key on in the same direction). Rest: unfocused 50 %, idle 5 s 30 %; Visualiser",
        "     mode: gone after 4 s (Timers.xml moves focus to the wake catcher 9690). Up next open: 30 % + origin dot. -->",
        '<include name="NP_Tray">',
        '\t<control type="group">',
        "\t\t<include>Anim_OSD</include>",
        f'\t\t<include content="Anim_IdleFade"><param name="condition" value="System.IdleTime(5) + !{VIZ} + !ControlGroup(9630).HasFocus()"/><param name="to" value="30"/></include>',
        f'\t\t<include content="Anim_IdleFade"><param name="condition" value="{VIZ} + System.IdleTime(4)"/><param name="to" value="0"/></include>',
        block(slots, 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_tray_rest():
    slots = [tray_slot(t, k, a, b, interactive=False) for t, k, a, b in TRAY if k != "watch"]
    return "\n".join([
        "<!-- The tray as drawn by MusicVisualisation while MusicOSD is not up (30 %, nothing focusable). -->",
        '<include name="NP_TrayRest">',
        '\t<control type="group">',
        f"\t\t<visible>!Window.IsVisible(musicosd) + !{VIZ}</visible>",
        "\t\t<include>Anim_FadeVisible</include>",
        block(slots, 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_progress_focus():
    x, y, w = PROG
    last = [f'<ondown condition="Integer.IsEqual(Window(Home).Property(groove.tray.last),{t})">{t}</ondown>' for t in TRAY_IDS]
    back = [f'<onback condition="Integer.IsEqual(Window(Home).Property(groove.tray.last),{t})">{t}</onback>' for t in TRAY_IDS]
    playhead = ('<control type="progress">\n'
                f"\t<left>{x - 6}</left>\n\t<top>{y + 1 - 6}</top>\n\t<width>{w + 12}</width>\n\t<height>12</height>\n"
                "\t<texturebg>groove/np_track.png</texturebg>\n\t<lefttexture />\n\t<midtexture />\n"
                '\t<righttexture colordiffuse="$VAR[ink]">groove/dot_12.png</righttexture>\n\t<overlaytexture />\n'
                "\t<info>Player.Progress</info>\n</control>")
    return "\n".join([
        "<!-- Up from the tray: the progress line takes focus (track to 30 %, a playhead dot, times in ink).",
        "     Left / Right seek 10 s, OK play / pause, Down / Back return to the tray button you came from. -->",
        '<include name="NP_ProgressFocus">',
        '\t<control type="group">',
        "\t\t<visible>Control.HasFocus(9620)</visible>",
        "\t\t<include>Anim_FadeVisible</include>",
        block([img(x, y, w, 2, "groove/white.png", "$VAR[ink3]"), playhead] + progress_parts("$VAR[ink]", extra_fill=False), 2),
        "\t</control>",
        '\t<control type="button" id="9620">',
        f"\t\t<left>{x}</left>\n\t\t<top>{y - 20}</top>\n\t\t<width>{w}</width>\n\t\t<height>44</height>",
        "\t\t<label></label>\n\t\t<texturefocus />\n\t\t<texturenofocus />",
        "\t\t<onfocus>ClearProperty(groove.np.overlay,home)</onfocus>",
        "\t\t<onleft>Seek(-10)</onleft>",
        "\t\t<onright>Seek(10)</onright>",
        "\t\t<onclick>PlayerControl(Play)</onclick>",
        block(last + ["<ondown>9602</ondown>"] + back + ["<onback>9602</onback>"], 2),
        "\t</control>",
        "</include>",
    ])


def inc_np_wake():
    acts = []
    for tag in ("onup", "ondown", "onleft", "onright", "onclick"):
        acts.append(f'<{tag} condition="!String.IsEmpty(Window(Home).Property(groove.tray.last))">SetFocus($INFO[Window(Home).Property(groove.tray.last)])</{tag}>')
        acts.append(f'<{tag} condition="String.IsEmpty(Window(Home).Property(groove.tray.last))">SetFocus(9602)</{tag}>')
    return "\n".join([
        "<!-- Wake catcher: holds focus while the tray is hidden in Visualiser mode. Any key only wakes the tray",
        "     (SetFocus back to the last tray button); Back leaves Now Playing like the tray. -->",
        '<include name="NP_WakeCatcher">',
        '\t<control type="button" id="9690">',
        "\t\t<left>0</left>\n\t\t<top>0</top>\n\t\t<width>1</width>\n\t\t<height>1</height>",
        "\t\t<label></label>\n\t\t<texturefocus />\n\t\t<texturenofocus />",
        block(acts, 2),
        '\t\t<onback condition="Window.IsActive(visualisation)">Action(FullScreen,visualisation)</onback>',
        "\t</control>",
        "</include>",
    ])


def inc_np_video_lookup():
    return "\n".join([
        "<!-- Hidden one-song lookup for Watch the video (DATA 6.4). Stays visible (1 px) or it never loads. -->",
        '<include name="NP_VideoLookup">',
        '\t<control type="list" id="9695">',
        "\t\t<left>0</left>\n\t\t<top>0</top>\n\t\t<width>1</width>\n\t\t<height>1</height>",
        "\t\t<itemlayout width=\"1\" height=\"1\" />",
        "\t\t<focusedlayout width=\"1\" height=\"1\" />",
        '\t\t<content target="music" browse="never">$VAR[NP_VideoPath]</content>',
        "\t</control>",
        "</include>",
    ])


def slot_centre(depth):
    th = math.radians(FAN * depth)
    rx, ry = CARD[2] / 2, -CARD[2] / 2          # card centre relative to the pivot (bottom-left)
    x = rx * math.cos(th) + ry * math.sin(th)
    y = -rx * math.sin(th) + ry * math.cos(th)
    return CARD_PIVOT[0] + x, CARD_PIVOT[1] + y


def card_art(x, y, s, j, diffuse):
    cov = f"MusicPlayer.offset({j}).Cover"
    nocov = f"[String.IsEmpty({cov}) | String.IsEqual({cov},DefaultAlbumCover.png)]"
    return [
        '<control type="image">\n'
        f"\t<left>{x - 96 * s // 290}</left>\n\t<top>{y - 60 * s // 290}</top>\n\t<width>{s + 192 * s // 290}</width>\n\t<height>{s + 180 * s // 290}</height>\n"
        '\t<texture border="96,60,96,120" colordiffuse="$VAR[shadow]">groove/shadow_square.png</texture>\n</control>',
        img(x, y, s, s, "$VAR[Tex_SleeveBack]", diffuse),
        img(x, y, s, s, f"$INFO[{cov}]", diffuse, tex_attr=' background="true"', aspect="scale",
            extra=f"<visible>!{nocov}</visible>\n<include>Anim_ArtFadetime</include>"),
        '<control type="textbox">\n'
        f"\t<left>{x + 24}</left>\n\t<top>{y + 24}</top>\n\t<width>{s - 48}</width>\n\t<height>{s - 48}</height>\n"
        "\t<align>center</align>\n\t<aligny>center</aligny>\n\t<font>font_caption</font>\n\t<textcolor>$VAR[ink2]</textcolor>\n"
        f"\t<label>$INFO[MusicPlayer.offset({j}).Title]</label>\n\t<visible>{nocov}</visible>\n</control>",
    ]


def inc_np_upnext():
    cx, cy, cs = CARD
    pv = f"{CARD_PIVOT[0]},{CARD_PIVOT[1]}"
    lx, ly, ls = LIFT
    lc = f"{LIFT_C[0]:g},{LIFT_C[1]:g}"
    closed = "!ControlGroup(9630).HasFocus()"
    o = []
    o.append("<!-- Up next veil: the room drawn over the Now Playing stage while the stack is open (MOTION 3.2). -->")
    o.append('<include name="NP_UpNextVeil">')
    o.append(block([img(0, 0, 1920, 1080, "$VAR[Tex_Room]", "$VAR[veil_stage]",
                        extra=f'<include content="Anim_StageVeil"><param name="closed" value="{closed}"/></include>')], 1))
    o.append("</include>")
    o.append("")
    o.append("<!-- Up next stack (UpNextStack.md, board B4): six cards from MusicPlayer.offset(1..6), fanned about the")
    o.append("     bottom-left corner (1130,630) at 5.5 deg per depth; the walked card lifts out to (1436,200) with its title.")
    o.append("     Focus lives on invisible buttons 9631-9636 (group 9630); 9640 = empty queue. -->")
    o.append('<include name="NP_UpNext">')
    vis = ['<control type="group">',
           f'\t<include content="Anim_Reveal"><param name="closed" value="{closed}"/><param name="dx" value="160"/><param name="dy" value="0"/><param name="t" value="300"/></include>']
    # header
    vis.append(block([img(96, 54, 44, 44, "icons/upnext.png", "$VAR[ink]"),
                      label(156, 54, 600, 44, "$LOCALIZE[31705]", "font_label", "$VAR[ink]")], 1))
    # empty queue
    vis.append(block(['<control type="group">\n\t<visible>!MusicPlayer.offset(1).Exists</visible>\n'
                      + block([img(cx, cy, cs, cs, "$VAR[Tex_SleeveBack]", "white_20"),
                               label(cx, 656, 700, 40, "$LOCALIZE[31712]", "font_caption_light", "$VAR[ink2]")], 1)
                      + "\n</control>"], 1))
    # the pile, back to front
    for j in range(6, 0, -1):
        d = j - 1
        a = FAN * d
        g = ['<control type="group">', f"\t<visible>MusicPlayer.offset({j}).Exists + !Control.HasFocus({9630 + j})</visible>",
             "\t<include>Anim_StackReturn</include>"]
        if d:
            g.append(f"\t{static_rotate(a, pv)}")
            g.append(f'\t<include content="Anim_StackFan"><param name="closed" value="{closed}"/><param name="angle" value="{a:g}"/><param name="pivot" value="{pv}"/></include>')
        g.append(block(card_art(cx, cy, cs, j, f"$VAR[stack_{d}]"), 1))
        g.append(block(['<control type="group">\n'
                        f"\t<visible>$EXP[NP_PickMode] + Integer.IsEqual(Window(Home).Property(groove.upnext.to),{j})</visible>\n"
                        + block([rim(cx - 6, cy - 6, cs + 12, cs + 12, "$VAR[ink]", 3)], 1) + "\n</control>"], 1))
        g.append("</control>")
        vis.append(block(g, 1))
    # target outline for the drop slot when it is the picked card's own (empty) slot
    # lifted cards (one per slot, shown while its button has focus)
    for j in range(1, 7):
        d = j - 1
        scx, scy = slot_centre(d)
        sdx, sdy = round(scx - LIFT_C[0]), round(scy - LIFT_C[1])
        start_rot = FAN * d - LIFT_ROT
        zoom = round(cs / ls * 100, 1)
        fvis = f"<visible>Control.HasFocus({9630 + j})</visible>"
        inner = [
            img(lx - 40, ly - 40, ls + 80, ls + 80, "groove/glow_frame.png", "$VAR[glow_fallback]", tex_attr=' border="48"',
                extra=f"<visible>!{LIGHT}</visible>\n<include>Groove_GlowStrength</include>"),
            img(round(LIFT_C[0] - ls * 0.75), round(LIFT_C[1] + 21 - ls * 0.75), round(ls * 1.5), round(ls * 1.5),
                "groove/shadow_cast.png", "$VAR[glow_fallback]", extra=f"<visible>{LIGHT}</visible>"),
        ] + card_art(lx, ly, ls, j, None) + [rim(lx, ly, ls, ls, "$VAR[rim]")]
        # outer group: slide from the slot's centre; middle: turn + scale from the slot's pose about the rest centre
        # (nested groups, so the slide never gets rotated); inner: the rest pose (-2 deg). Visible animations fire
        # when the card's button takes focus (no reduce-motion twin: the end state is the control's own pose).
        lifted = [
            '<control type="group">', f"\t{fvis}",
            f'\t<animation type="Visible" condition="!{RM}"><effect type="slide" start="{sdx},{sdy}" end="0,0" time="250" tween="cubic" easing="out"/></animation>',
            '\t<control type="group">', f"\t\t{fvis}",
            f'\t\t<animation type="Visible" condition="!{RM}"><effect type="rotate" start="{start_rot:g}" end="0" center="{lc}" time="250" tween="cubic" easing="out"/>'
            f'<effect type="zoom" start="{zoom}" end="100" center="{lc}" time="250" tween="cubic" easing="out"/></animation>',
            f'\t\t<include content="Anim_PickUp"><param name="condition" value="$EXP[NP_PickMode]"/><param name="center" value="{lc}"/></include>',
            '\t\t<control type="group">', f"\t\t\t{static_rotate(LIFT_ROT, lc)}",
            block(inner, 3), "\t\t</control>", "\t</control>",
            "</control>",
            '<control type="group">', f"\t{fvis}", "\t<include>Anim_LabelReveal</include>",
            block([label(lx, 560, 388, 48, f"$INFO[MusicPlayer.offset({j}).Title]", "font_title_s", "$VAR[ink]"),
                   label(lx, 612, 388, 40, f"$INFO[MusicPlayer.offset({j}).Artist]", "font_caption_light", "$VAR[ink2]")], 1),
            "</control>",
        ]
        vis.append(block(lifted, 1))
    # rest count + pick-up glyph
    vis.append(block([label(cx, 656, 300, 36, "$VAR[NP_UpNextRest]", "font_small", "$VAR[ink2]",
                            extra="<visible>MusicPlayer.offset(7).Exists + !Playlist.IsRepeat</visible>"),
                      img(1778, 340, 44, 44, "icons/pickup.png", "$VAR[ink]",
                          extra="<visible>$EXP[HasGrooveHelper] + MusicPlayer.offset(1).Exists</visible>\n"
                                '<animation effect="fade" start="100" end="40" time="160" condition="!$EXP[NP_PickMode]" reversible="true">Conditional</animation>')], 1))
    vis.append("</control>")
    o.append(block(vis, 1))
    # focus buttons
    btn = ['<control type="group" id="9630">']
    pick = "$EXP[NP_PickMode]"
    nopick = "!$EXP[NP_PickMode]"
    for j in range(1, 7):
        b = [f'<control type="button" id="{9630 + j}">', "\t<left>0</left>\n\t<top>0</top>\n\t<width>1</width>\n\t<height>1</height>",
             "\t<label></label>\n\t<texturefocus />\n\t<texturenofocus />", f"\t<visible>MusicPlayer.offset({j}).Exists</visible>",
             "\t<onfocus>SetProperty(groove.np.overlay,upnext,home)</onfocus>"]
        # normal mode
        if j > 1:
            b.append(f'\t<onup condition="{nopick}">{9630 + j - 1}</onup>')
        if j < 6:
            b.append(f'\t<ondown condition="{nopick}">{9630 + j + 1}</ondown>')
        if j == 1:
            b.append(f'\t<onleft condition="{nopick}">PlayerControl(Next)</onleft>')
        b.append(f'\t<onright condition="{nopick} + $EXP[HasGrooveHelper]">SetProperty(groove.upnext.to,{j},home)</onright>')
        b.append(f'\t<onright condition="{nopick} + $EXP[HasGrooveHelper]">SetProperty(groove.upnext.pick,{j},home)</onright>')
        # pick mode: Up / Down move the drop target, OK drops, Back cancels
        for t in range(2, 7):
            b.append(f'\t<onup condition="{pick} + Integer.IsEqual(Window(Home).Property(groove.upnext.to),{t})">SetProperty(groove.upnext.to,{t - 1},home)</onup>')
        for t in range(1, 6):
            b.append(f'\t<ondown condition="{pick} + Integer.IsEqual(Window(Home).Property(groove.upnext.to),{t}) + MusicPlayer.offset({t + 1}).Exists">SetProperty(groove.upnext.to,{t + 1},home)</ondown>')
        for t in range(1, 7):
            b.append(f'\t<onclick condition="{pick} + Integer.IsEqual(Window(Home).Property(groove.upnext.to),{t})">SetFocus({9630 + t})</onclick>')
        b.append(f'\t<onclick condition="{pick}">RunScript(script.karmamole.helper,action=queue_move,from=$INFO[Window(Home).Property(groove.upnext.pick)],to=$INFO[Window(Home).Property(groove.upnext.to)])</onclick>')
        b.append(f'\t<onclick condition="{pick}">ClearProperty(groove.upnext.to,home)</onclick>')
        b.append(f'\t<onclick condition="{pick}">ClearProperty(groove.upnext.pick,home)</onclick>')
        b.append(f'\t<onclick condition="{nopick}">Playlist.PlayOffset({j})</onclick>')
        b.append(f'\t<onclick condition="{nopick}">SetFocus(9604)</onclick>')
        b.append(f'\t<onback condition="{pick}">{9630 + j}</onback>')
        b.append(f'\t<onback condition="{pick}">ClearProperty(groove.upnext.to,home)</onback>')
        b.append(f'\t<onback condition="{pick}">ClearProperty(groove.upnext.pick,home)</onback>')
        b.append("\t<onback>9604</onback>")
        b.append("</control>")
        btn.append(block(["\n".join(b)], 1))
    btn.append(block(['<control type="button" id="9640">\n\t<left>0</left>\n\t<top>0</top>\n\t<width>1</width>\n\t<height>1</height>'
                      "\n\t<label></label>\n\t<texturefocus />\n\t<texturenofocus />\n\t<visible>!MusicPlayer.offset(1).Exists</visible>"
                      "\n\t<onfocus>SetProperty(groove.np.overlay,upnext,home)</onfocus>"
                      "\n\t<onclick>SetFocus(9604)</onclick>\n\t<onback>9604</onback>\n</control>"], 1))
    btn.append("</control>")
    o.append(block(btn, 1))
    o.append("</include>")
    return "\n".join(o)


def inc_mini():
    X, Y, S, D = 1704, 54, 120, 92
    c = (X + S // 2, Y + S // 2)
    dx, dy = X + (S - D) // 2, Y + (S - D) // 2
    lab = 32
    lx, ly = c[0] - lab // 2, c[1] - lab // 2

    def disc(spin):
        o = ['<control type="group">']
        if spin:
            o.append(f'\t<include content="Anim_MiniSpin"><param name="center" value="{c[0]},{c[1]}"/></include>')
            o.append("\t<include>Anim_MiniSpinStop</include>")
        o.append(block([img(lx, ly, lab, lab, "groove/disc_mask.png", "black"),
                        img(lx, ly, lab, lab, "$INFO[Player.Art(thumb)]", tex_attr=' background="true" diffuse="groove/disc_mask.png"',
                            aspect="scale", extra="<include>Anim_ArtFadetime</include>"),
                        img(dx, dy, D, D, "groove/vinyl.png")], 1))
        o.append("</control>")
        return "\n".join(o)

    foc = "Control.HasFocus(9950)"
    zoom = cond_anim(f'<effect type="zoom" start="100" end="108" center="{c[0]},{c[1]}" time="160" tween="cubic" easing="out"/>', foc,
                     rm_effect=f'<effect type="zoom" start="100" end="108" center="{c[0]},{c[1]}" time="0"/>')
    return "\n".join([
        "<!-- Mini player (MiniPlayer.md, id 9950): a 92 px disc turning slowly (8 s per turn) inside a progress ring,",
        "     top right at 1704,54. Place it at the TOP LEVEL of a window (absolute coordinates, no offset group).",
        "     Shown while music plays and Skin setting Mini player != Off; never on Now Playing or over video.",
        "     OK = Now Playing. params:",
        "       down    Down from the disc (numeric id or a SetFocus(...) builtin)   default: nothing",
        "       left    Left from the disc                                         default: noop (stays)",
        "       back    Back from the disc: give a NUMERIC id so Back only moves focus (LESSONS Back audit)",
        "       back_nav include of conditional numeric onbacks tried before `back` (Mini_BackHome / _Music / _Video:",
        "               the icon you came up from)                                 default: Misc_None",
        "       visible extra condition                                             default: true",
        "       rest    condition under which the disc steps aside (fades out) while it has no focus; it stays focusable",
        "               and fades back in on focus. Home: the Music section at rest, whose hero IS the playing album",
        "               (DEVICE_AUDIT n2); MyMusicNav / MyVideoNav: the Cover wall's first row has focus (the disc",
        "               sits over the top-right cover, Pass 2)                    default: false",
        "     Home: down = SetFocus(the rail icon), back_nav Mini_BackHome. Libraries: down =",
        "     SetFocus($INFO[Window(Home).Property(groove.mini.from)]), back_nav Mini_BackMusic / Mini_BackVideo, back = Options.",
        "     Info dialogs / custom windows: down / back = the control below. -->",
        '<include name="Groove_MiniPlayer">',
        '\t<param name="down"></param>',
        '\t<param name="left">noop</param>',
        '\t<param name="back"></param>',
        '\t<param name="back_nav">Misc_None</param>',
        '\t<param name="visible">true</param>',
        '\t<param name="rest">false</param>',
        "\t<definition>",
        '\t\t<control type="group">',
        "\t\t\t<visible>Player.HasAudio + !String.IsEqual(Skin.String(groove.mini),off) + !Window.IsActive(visualisation) + !Window.IsActive(fullscreenvideo) + !Window.IsVisible(musicosd) + [$PARAM[visible]]</visible>",
        f'\t\t\t<include content="Anim_MiniAppear"><param name="center" value="{c[0]},{c[1]}"/></include>',
        '\t\t\t<control type="group">',
        f'\t\t\t\t<animation effect="fade" start="100" end="0" time="200" condition="[$PARAM[rest]] + !{foc}" reversible="true">Conditional</animation>',
        block([img(c[0] - 144, c[1] - 144, 288, 288, "groove/glow_radial.png", "$VAR[focus_glow]",
                   extra=f"<visible>{foc}</visible>\n<include>Anim_FadeVisible</include>"),
               '<control type="group">', block([zoom], 1),
               block([img(X, Y, S, S, "groove/progress_ring/track.png", "$VAR[line]"),
                      img(X, Y, S, S, "$VAR[Mini_Ring]", "$VAR[ink]"),
                      img(dx - 8, dy - 2, D + 16, D + 16, "groove/shadow_disc.png", "$VAR[shadow]"),
                      disc(False), disc(True),
                      img(dx, dy, D, D, "groove/vinyl_sheen.png"),
                      img(c[0] - 3, c[1] - 3, 6, 6, "groove/dot.png", "black")], 1),
               "</control>",
               '<control type="group">', f"\t<visible>{foc}</visible>", "\t<include>Anim_LabelReveal</include>",
               block([label(1184, 64, 496, 32, "$LOCALIZE[31700]", "font_tray", "$VAR[ink2]", align="right"),
                      label(1184, 96, 496, 40, "$INFO[MusicPlayer.Title]", "font_label", "$VAR[ink]", align="right")], 1),
               "</control>",
               '<control type="button" id="9950">',
               f"\t<left>{X}</left>\n\t<top>{Y}</top>\n\t<width>{S}</width>\n\t<height>{S}</height>",
               "\t<label></label>\n\t<texturefocus />\n\t<texturenofocus />",
               "\t<onclick>ActivateWindow(visualisation)</onclick>",
               "\t<ondown>$PARAM[down]</ondown>",
               "\t<onleft>$PARAM[left]</onleft>",
               "\t<include content=\"$PARAM[back_nav]\"/>",
               "\t<onback>$PARAM[back]</onback>",
               "</control>"], 4),
        "\t\t\t</control>",
        "\t\t</control>",
        "\t</definition>",
        "</include>",
        "",
        mini_back_navs(),
    ])


# the focusable controls Up / Right reaches the mini player from, per window, and the property that names the one used
MINI_FROM = {
    "Mini_BackHome": ("groove.railid", [9001, 9002, 9003, 9004, 9005]),             # Home rail (make_home.py)
    "Mini_BackMusic": ("groove.mini.from", [9501, 9502, 9503, 9504, 9505, 9511, 9512, 9513]),  # make_music_views header
    "Mini_BackVideo": ("groove.mini.from", [9521, 9522, 9531, 9532, 9533]),          # Includes_Views_Video header
}


def mini_back_navs():
    """Back from the mini player = the icon you came up from (MiniPlayer.md). Back must be numeric to only move focus
    (LESSONS Back audit), so one conditional numeric onback per icon; the first match wins, Groove_MiniPlayer's own
    `back` param is the fallback after them."""
    o = ["<!-- Groove_MiniPlayer back_nav includes: conditional numeric onbacks, one per icon the disc can be reached from -->"]
    for name, (prop, ids) in MINI_FROM.items():
        o.append(f'<include name="{name}">')
        o += [f'\t<onback condition="Integer.IsEqual(Window(Home).Property({prop}),{i})">{i}</onback>' for i in ids]
        o.append("</include>")
    return "\n".join(o)


def build_player():
    parts = player_vars()
    for f in (inc_np_curtain, inc_np_glow, inc_np_record, inc_np_sleeve, inc_np_tonearm, inc_np_info, inc_np_vizcaption,
              inc_np_progress, inc_np_tray_rest, inc_np_tray, inc_np_progress_focus, inc_np_wake, inc_np_video_lookup,
              inc_np_upnext, inc_mini):
        parts.append("")
        parts.append(f())
    head = ['<?xml version="1.0" encoding="UTF-8"?>',
            "<!-- GENERATED by _src/make_player.py - edit the generator, then re-run it. -->",
            "<!--",
            "\tMusic playback (M3): Now Playing stage (MusicVisualisation.xml), the tray and its overlays (MusicOSD.xml),",
            "\tthe mini player (Groove_MiniPlayer, placed by Home / libraries / info / custom windows).",
            "\tIds: tray 9601-9609, progress 9620, Up next 9630 group / 9631-9636 / 9640, Liner notes 9650-9670,",
            "\tviz caption 9681-9682, wake catcher 9690, video lookup 9695, mini player 9950.",
            "\tRuntime properties (Window(Home)): groove.tray.last (last tray button), groove.np.overlay (liner while the",
            "\tLiner notes page is open), groove.upnext.pick / .to (helper pick-up), groove.np.colorsrc (TMDb colour source).",
            "-->",
            "<includes>"]
    return "\n".join(head + [block(parts, 1), "</includes>", ""])


# =============================================================================================== Includes_MusicInfo.xml
SRC = {
    # name: (album-level prefix, artist-property prefix, artist gate)
    "player": dict(review="MusicPlayer.Property(Album_Description)", bio="MusicPlayer.Property(Artist_Description)",
                   year="MusicPlayer.Year", label="MusicPlayer.Property(Album_Label)",
                   genre=["MusicPlayer.Property(Album_Genre)", "MusicPlayer.Genre"],
                   style="MusicPlayer.Property(Album_Style)", mood="MusicPlayer.Property(Album_Mood)",
                   artistp="MusicPlayer.Property(Artist_{})", gate=None,
                   album=["MusicPlayer.Album"], artist="MusicPlayer.Artist",
                   cover="Player.Art(thumb)"),
    "item": dict(review="ListItem.Property(Album_Description)", bio="Container(9940).ListItem.Property(Artist_Description)",
                 year="ListItem.Year", label="ListItem.Property(Album_Label)", genre=["ListItem.Genre"],
                 style="ListItem.Property(Album_Style)", mood="ListItem.Property(Album_Mood)",
                 artistp="Container(9940).ListItem.Property(Artist_{})", gate="$EXP[MInfo_ArtistMatch]",
                 album=["ListItem.Album", "ListItem.Label"], artist="ListItem.Artist",
                 cover="ListItem.Art(thumb)"),
}
ROLES = [("Composer", 31726), ("Lyricist", 31727), ("Conductor", 31728), ("Remixer", 31729)]


def chain_var(name, infos, gate=None):
    o = [f'<variable name="{name}">']
    g = f"{gate} + " if gate else ""
    for i, info in enumerate(infos):
        if i < len(infos) - 1:
            o.append(f'\t<value condition="{g}!String.IsEmpty({info})">$INFO[{info}]</value>')
        else:
            o.append(f'\t<value condition="{gate}">$INFO[{info}]</value>' if gate else f"\t<value>$INFO[{info}]</value>")
    o.append("</variable>")
    return o


def facts_line_var(name, ap, gate, third):
    """Born/Formed · Died/Disbanded · third piece; empty pieces drop with their separators (LESSONS Orbit 0.9.4)."""
    B, F, D, X = (ap.format(k) for k in ("Born", "Formed", "Died", "Disbanded"))
    p1 = [(f"!String.IsEmpty({F})", f"$LOCALIZE[31722] $INFO[{F}]"),          # groups: Formed (Kodi fills Born too)
          (f"String.IsEmpty({F}) + !String.IsEmpty({B})", f"$LOCALIZE[31721] $INFO[{B}]"),
          (f"String.IsEmpty({F}) + String.IsEmpty({B})", None)]
    p2 = [(f"!String.IsEmpty({D})", f"$LOCALIZE[31723] $INFO[{D}]"),
          (f"String.IsEmpty({D}) + !String.IsEmpty({X})", f"$LOCALIZE[31724] $INFO[{X}]"),
          (f"String.IsEmpty({D}) + String.IsEmpty({X})", None)]
    t_info, t_text = third
    p3 = [(f"!String.IsEmpty({t_info})", t_text), (f"String.IsEmpty({t_info})", None)]
    o = [f'<variable name="{name}">']
    g = f"{gate} + " if gate else ""
    for (c1, v1), (c2, v2), (c3, v3) in product(p1, p2, p3):
        vals = [v for v in (v1, v2, v3) if v]
        if not vals:
            continue
        o.append(f'\t<value condition="{g}{c1} + {c2} + {c3}">{" · ".join(vals)}</value>')
    o.append("</variable>")
    return o


def credits_var(name):
    o = [f'<variable name="{name}">']
    infos = [(f"MusicPlayer.Property(Role.{r})", sid) for r, sid in ROLES]
    for mask in range(15, 0, -1):
        on = [infos[i] for i in range(4) if mask >> (3 - i) & 1]
        conds = [f"!String.IsEmpty({inf})" if mask >> (3 - i) & 1 else f"String.IsEmpty({inf})" for i, (inf, _s) in enumerate(infos)]
        val = " · ".join(f"$LOCALIZE[{sid}]: $INFO[{inf}]" for inf, sid in on)
        o.append(f'\t<value condition="{" + ".join(conds)}">{val}</value>')
    o.append("</variable>")
    return o


def info_vars():
    o = []
    o.append("<!-- ============================================================ Liner notes sources (DATA 7) -->")
    o.append("<!-- Album info: the album item carries only Album_*; the artist's bio comes from the hidden artists list 9940")
    o.append("     (DialogMusicInfo), used only when its item really is this album's artist (single-artist albums). -->")
    o.append('<expression name="MInfo_ArtistMatch">String.IsEqual(Container(9940).ListItem.Label,ListItem.Artist) + String.IsEqual(Container(9940).ListItem.DBType,artist)</expression>')
    o.append("<!-- by database id, so no name goes into the path (official review: xml.xsp-unencoded): an album lists its album")
    o.append("     artists (MusicDatabase GetFilter albumid), a song its artists (songid), an artist itself (artistid) -->")
    o.append('<variable name="MInfo_ArtistPath">')
    for dbtype, key in [("album", "albumid"), ("song", "songid"), ("artist", "artistid")]:
        o.append(f'\t<value condition="Integer.IsGreater(ListItem.DBID,0) + String.IsEqual(ListItem.DBType,{dbtype})">'
                 f"musicdb://artists/?{key}=$INFO[ListItem.DBID]</value>")
    o.append("</variable>")
    for s, d in SRC.items():
        g = d["gate"]
        gp = f"{g} + " if g else ""
        o.append(f"<!-- source: {s} -->")
        o.append(f'<expression name="Liner_HasReview_{s}">!String.IsEmpty({d["review"]})</expression>')
        o.append(f'<expression name="Liner_HasBio_{s}">{gp}!String.IsEmpty({d["bio"]})</expression>')
        o.append(f'<variable name="Liner_Review_{s}"><value>$INFO[{d["review"]}]</value></variable>')
        o += chain_var(f"Liner_Bio_{s}", [d["bio"]], g)
        o += chain_var(f"Liner_Album_{s}", d["album"])
        o.append(f'<variable name="Liner_Artist_{s}"><value>$INFO[{d["artist"]}]</value></variable>')
        o.append(f'<variable name="Liner_Cover_{s}"><value>$INFO[{d["cover"]}]</value></variable>')
        o.append(f'<variable name="Liner_Year_{s}"><value>$INFO[{d["year"]}]</value></variable>')
        o.append(f'<variable name="Liner_Label_{s}"><value>$INFO[{d["label"]}]</value></variable>')
        o += chain_var(f"Liner_Genre_{s}", d["genre"])
        o.append(f'<variable name="Liner_Style_{s}"><value>$INFO[{d["style"]}]</value></variable>')
        o.append(f'<variable name="Liner_Mood_{s}"><value>$INFO[{d["mood"]}]</value></variable>')
        yrs = d["artistp"].format("YearsActive")
        o += facts_line_var(f"Liner_ArtistFacts_{s}", d["artistp"], g, (yrs, f"$LOCALIZE[31725] $INFO[{yrs}]"))
        o.append(f'<expression name="Liner_HasArtistFacts_{s}">{gp}[' + " | ".join(
            f"!String.IsEmpty({d['artistp'].format(k)})" for k in ("Born", "Formed", "Died", "Disbanded", "YearsActive")) + "]</expression>")
        # fact visibility
        o.append(f'<expression name="Liner_HasGenre_{s}">' + " | ".join(f"!String.IsEmpty({i})" for i in d["genre"]) + "</expression>")
        for k in ("year", "label", "style", "mood"):
            o.append(f'<expression name="Liner_Has{k.capitalize()}_{s}">!String.IsEmpty({d[k]})</expression>')
    o.append("<!-- album info's Liner notes button shows only when the page has something to read (Pass 2 n5): a review, a bio,")
    o.append("     or a label / style / mood. A year, a genre or the artist's dates alone don't make a page. -->")
    o.append('<expression name="Liner_HasNotes_item">' + " | ".join(
        f"$EXP[Liner_Has{k}_item]" for k in ("Review", "Bio", "Label", "Style", "Mood")) + "</expression>")
    o.append('<variable name="Liner_Glow_player"><value>$VAR[NP_Glow]</value></variable>')
    o.append("<!-- the page's wash: blurred art only (helper soft art, else TMDb Helper's blur), never the raw cover -->")
    o.append('<variable name="Liner_Wash_player"><value condition="$EXP[HasGrooveHelper] + !String.IsEmpty(Window(Home).Property(Groove.Player.Art.Soft))">$VAR[NP_SoftArt]</value><value>$INFO[Window(Home).Property(TMDbHelper.GroovePlayer.BlurImage)]</value></variable>')
    o.append('<expression name="Liner_HasWash_player">[$EXP[HasGrooveHelper] + !String.IsEmpty(Window(Home).Property(Groove.Player.Art.Soft))] | $EXP[NP_BlurReady]</expression>')
    o.append('<variable name="Liner_Wash_item"><value>$VAR[MInfo_Wash]</value></variable>')
    o.append('<expression name="Liner_HasWash_item">$EXP[MInfo_HasWash]</expression>')
    o.append('<variable name="Liner_Glow_item"><value>$VAR[glow]</value></variable>')
    o += credits_var("Liner_Credits_player")
    o.append('<variable name="Liner_Credits_item"><value></value></variable>')
    o.append('<expression name="Liner_HasCredits_player">' + " | ".join(f"!String.IsEmpty(MusicPlayer.Property(Role.{r}))" for r, _ in ROLES) + "</expression>")
    o.append('<expression name="Liner_HasCredits_item">false</expression>')
    o.append('<variable name="Liner_Format_player"><value>[UPPERCASE]$INFO[MusicPlayer.Codec][/UPPERCASE]$INFO[MusicPlayer.BitRate, · , kbps]$INFO[MusicPlayer.SampleRate, · , kHz]</value></variable>')
    o.append('<variable name="Liner_Format_item"><value></value></variable>')
    o.append('<expression name="Liner_HasFormat_player">!String.IsEmpty(MusicPlayer.Codec) | !String.IsEmpty(MusicPlayer.BitRate)</expression>')
    o.append('<expression name="Liner_HasFormat_item">false</expression>')
    o.append('<expression name="Liner_HasDisc_player">$EXP[NP_HasDisc]</expression>')
    o.append('<expression name="Liner_HasDisc_item">!String.IsEmpty(ListItem.Art(discart))</expression>')
    o.append('<variable name="Liner_Disc_player"><value>$VAR[NP_Disc]</value></variable>')
    o.append('<variable name="Liner_Disc_item"><value>$INFO[ListItem.Art(discart)]</value></variable>')
    o.append("<!-- artist info facts line: Born / Formed · Died / Disbanded · genre -->")
    o += facts_line_var("MInfo_ArtistFacts", "ListItem.Property(Artist_{})", None, ("ListItem.Genre", "$INFO[ListItem.Genre]"))
    # open actions
    for s in SRC:
        R, B = f"$EXP[Liner_HasReview_{s}]", f"$EXP[Liner_HasBio_{s}]"
        o.append(f"<!-- open the Liner notes page ({s}): focus the reading part that exists -->")
        o.append(f'<include name="Liner_Open_{s}">')
        if s == "player":   # scrollbars run no <onfocus>: the opener tells MusicVisualisation (the record stops)
            o.append("\t<onclick>SetProperty(groove.np.overlay,liner,home)</onclick>")
        o.append(f'\t<onclick condition="{R} + {B}">SetFocus(9661)</onclick>')
        o.append(f'\t<onclick condition="{R} + !{B}">SetFocus(9663)</onclick>')
        o.append(f'\t<onclick condition="!{R} + {B}">SetFocus(9664)</onclick>')
        o.append(f'\t<onclick condition="!{R} + !{B}">SetFocus(9665)</onclick>')
        o.append("</include>")
    return o


def textbox(tid, x, y, w, h, text, pagecontrol):
    return (f'<control type="textbox" id="{tid}">\n\t<left>{x}</left>\n\t<top>{y}</top>\n\t<width>{w}</width>\n\t<height>{h}</height>'
            f"\n\t<font>font_body</font>\n\t<textcolor>$VAR[ink]</textcolor>\n\t<label>{text}</label>\n\t<pagecontrol>{pagecontrol}</pagecontrol>"
            "\n\t<include>Anim_ScrollText</include>\n</control>")


def text_fade(tid, mask):
    """Fade over a clipped text's last line, made of the room itself (full-frame mask from make_textures.py)."""
    return img(0, 0, 1920, 1080, "$VAR[Tex_Room]", tex_attr=f' diffuse="groove/{mask}.png"',
               extra=f"<visible>Integer.IsLess(Container({tid}).CurrentPage,Container({tid}).NumPages)</visible>\n<include>Anim_FadeVisible</include>")


def scroller(sid, x, y, h, up=None, down=None):
    o = [f'<control type="scrollbar" id="{sid}">', f"\t<left>{x}</left>\n\t<top>{y}</top>\n\t<width>4</width>\n\t<height>{h}</height>",
         "\t<texturesliderbackground />\n\t<texturesliderbar />",
         '\t<texturesliderbarfocus colordiffuse="$VAR[ink]">groove/white.png</texturesliderbarfocus>',
         "\t<textureslidernib />\n\t<textureslidernibfocus />",
         "\t<orientation>vertical</orientation>\n\t<showonepage>true</showonepage>"]
    # no <onfocus>: Kodi never runs it on a scrollbar (GUIControlFactory gives focus actions to other types only);
    # the openers (Liner_Open_*) set groove.np.overlay instead
    if up:
        o.append(f"\t<onup>{up}</onup>")
    if down:
        o.append(f"\t<ondown>{down}</ondown>")
    o.append("\t<onback>$PARAM[origin]</onback>")
    o.append("</control>")
    return "\n".join(o)


def fact(key, sid, value_var, vis, probe=None):
    """One fact in the column: caps label + value (one line; 2 lines when its probe says it wraps)."""
    lab = f"[UPPERCASE]$LOCALIZE[{sid}][/UPPERCASE]"
    one = ('<control type="group">\n\t<width>324</width>\n\t<height>64</height>'
           f"\n\t<visible>{vis}" + (f" + !Integer.IsGreater(Container({probe}).NumPages,1)" if probe else "") + "</visible>\n"
           + block([label(0, 0, 324, 26, lab, "font_fact_label", "$VAR[ink2]"),
                    label(0, 30, 324, 34, value_var, "font_fact", "$VAR[ink]")], 1) + "\n</control>")
    if not probe:
        return [one]
    two = ('<control type="group">\n\t<width>324</width>\n\t<height>98</height>'
           f"\n\t<visible>{vis} + Integer.IsGreater(Container({probe}).NumPages,1)</visible>\n"
           + block([label(0, 0, 324, 26, lab, "font_fact_label", "$VAR[ink2]"),
                    '<control type="textbox">\n\t<left>0</left>\n\t<top>30</top>\n\t<width>324</width>\n\t<height>68</height>'
                    f"\n\t<font>font_fact</font>\n\t<textcolor>$VAR[ink]</textcolor>\n\t<label>{value_var}</label>\n</control>"], 1)
           + "\n</control>")
    return [one, two]


def inc_liner():
    s = "$PARAM[src]"
    R, B = f"$EXP[Liner_HasReview_{s}]", f"$EXP[Liner_HasBio_{s}]"
    cov = (96, 190, 400)
    parts = []
    # room + light
    parts.append(img(0, 0, 1920, 1080, "$VAR[Tex_Room]", extra="<visible>$PARAM[room]</visible>"))
    # the wash stays inside the page (in album info the page sits under the info screen until it slides up)
    parts.append('<control type="image">\n\t<left>-450</left>\n\t<top>0</top>\n\t<width>1300</width>\n\t<height>1080</height>'
                 '\n\t<aspectratio>stretch</aspectratio>'
                 f'\n\t<texture background="true" diffuse="groove/wash_mask.png" colordiffuse="$VAR[wash]">$VAR[Liner_Wash_{s}]</texture>'
                 f'\n\t<visible>$EXP[Liner_HasWash_{s}]</visible>'
                 '\n\t<animation effect="fade" start="100" end="50" time="0" condition="true">Conditional</animation>'
                 "\n\t<include>Anim_GlowFadetime</include>\n</control>")
    parts.append(img(cov[0] + cov[2] // 2 - 380, cov[1] + cov[2] // 2 - 380, 760, 760, "groove/glow_radial.png", f"$VAR[Liner_Glow_{s}]",
                     extra="<include>Groove_GlowStrength</include>"))
    # header
    parts.append(img(96, 54, 44, 44, "icons/liner.png", "$VAR[ink]"))
    parts.append(label(156, 54, 600, 44, "$LOCALIZE[31706]", "font_label", "$VAR[ink]"))
    # disc behind the cover, cover, words
    parts.append(img(381, 205, 370, 370, f"$VAR[Liner_Disc_{s}]", tex_attr=' background="true"', aspect="keep",
                     extra=f"<visible>$EXP[Liner_HasDisc_{s}]</visible>\n<include>Anim_ArtFadetime</include>"))
    parts.append('<control type="group">\n'
                 f"\t<left>{cov[0]}</left>\n\t<top>{cov[1]}</top>\n\t<width>{cov[2]}</width>\n\t<height>{cov[2]}</height>\n"
                 + block(['<control type="image">\n\t<left>-96</left>\n\t<top>-60</top>\n\t<width>592</width>\n\t<height>580</height>'
                          '\n\t<texture border="96,60,96,120" colordiffuse="$VAR[shadow]">groove/shadow_square.png</texture>\n</control>',
                          img(-40, -40, cov[2] + 80, cov[2] + 80, "groove/glow_frame.png", "$VAR[glow_fallback]", tex_attr=' border="48"',
                              extra=f"<visible>!{LIGHT}</visible>\n"
                                    '<animation effect="fade" start="100" end="50" time="0" condition="true">Conditional</animation>'),
                          img(0, 0, cov[2], cov[2], "$VAR[Tex_SleeveBack]"),
                          img(0, 0, cov[2], cov[2], f"$VAR[Liner_Cover_{s}]", tex_attr=' background="true"', aspect="scale",
                              extra="<include>Anim_ArtFadetime</include>"),
                          rim(0, 0, cov[2], cov[2], "$VAR[rim]")], 1) + "\n</control>")
    parts.append(label(96, 612, 600, 48, f"$VAR[Liner_Album_{s}]", "font_title_s", "$VAR[ink]"))
    parts.append(label(96, 664, 600, 40, f"$VAR[Liner_Artist_{s}]", "font_caption_light", "$VAR[ink2]"))
    # probes for the two facts that may wrap (real position, clear text: LESSONS Six Degrees)
    for pid, var in ((9668, f"$VAR[Liner_Credits_{s}]"), (9669, f"$VAR[Liner_Style_{s}]"), (9670, f"$VAR[Liner_Format_{s}]")):
        parts.append(f'<control type="textbox" id="{pid}">\n\t<left>1500</left>\n\t<top>220</top>\n\t<width>324</width>\n\t<height>34</height>'
                     f"\n\t<font>font_fact</font>\n\t<textcolor>clear</textcolor>\n\t<label>{var}</label>\n</control>")
    # variant A: review + bio
    a = [textbox(9651, 760, 190, 680, 280, f"$VAR[Liner_Review_{s}]", 9661), text_fade(9651, "fade_liner_review"),
         label(760, 496, 680, 44, "$LOCALIZE[31713]", "font_label", "$VAR[ink]"),
         textbox(9652, 760, 550, 680, 200, f"$VAR[Liner_Bio_{s}]", 9662), text_fade(9652, "fade_liner_bio"),
         label(760, 764, 680, 34, f"$VAR[Liner_ArtistFacts_{s}]", "font_small", "$VAR[ink2]")]
    parts.append('<control type="group">\n' f"\t<visible>{R} + {B}</visible>\n" + block(a, 1) + "\n</control>")
    # review only
    r = [textbox(9653, 760, 190, 680, 560, f"$VAR[Liner_Review_{s}]", 9663), text_fade(9653, "fade_liner_reviewlong")]
    parts.append('<control type="group">\n' f"\t<visible>{R} + !{B}</visible>\n" + block(r, 1) + "\n</control>")
    # bio only
    b = [label(760, 186, 680, 44, "$LOCALIZE[31713]", "font_label", "$VAR[ink]"),
         textbox(9654, 760, 240, 680, 480, f"$VAR[Liner_Bio_{s}]", 9664), text_fade(9654, "fade_liner_biolong"),
         label(760, 734, 680, 34, f"$VAR[Liner_ArtistFacts_{s}]", "font_small", "$VAR[ink2]")]
    parts.append('<control type="group">\n' f"\t<visible>!{R} + {B}</visible>\n" + block(b, 1) + "\n</control>")
    # neither: the artist facts line under the facts column start, if there are any
    parts.append(label(760, 734, 680, 34, f"$VAR[Liner_ArtistFacts_{s}]", "font_small", "$VAR[ink2]",
                       extra=f"<visible>!{R} + !{B} + $EXP[Liner_HasArtistFacts_{s}]</visible>"))
    # facts column
    facts = []
    facts += fact("year", 31714, f"$VAR[Liner_Year_{s}]", f"$EXP[Liner_HasYear_{s}]")
    facts += fact("label", 31715, f"$VAR[Liner_Label_{s}]", f"$EXP[Liner_HasLabel_{s}]")
    facts += fact("genre", 31716, f"$VAR[Liner_Genre_{s}]", f"$EXP[Liner_HasGenre_{s}]")
    facts += fact("style", 31717, f"$VAR[Liner_Style_{s}]", f"$EXP[Liner_HasStyle_{s}]", probe=9669)
    facts += fact("mood", 31718, f"$VAR[Liner_Mood_{s}]", f"$EXP[Liner_HasMood_{s}]")
    facts += fact("credits", 31719, f"$VAR[Liner_Credits_{s}]", f"$EXP[Liner_HasCredits_{s}]", probe=9668)
    facts += fact("format", 31720, f"$VAR[Liner_Format_{s}]", f"$EXP[Liner_HasFormat_{s}]", probe=9670)
    parts.append('<control type="grouplist" id="9667">\n\t<left>1500</left>\n\t<top>190</top>\n\t<width>324</width>\n\t<height>760</height>'
                 "\n\t<orientation>vertical</orientation>\n\t<itemgap>22</itemgap>\n\t<usecontrolcoords>true</usecontrolcoords>"
                 f'\n\t<animation effect="slide" end="-740,0" time="0" condition="!{R} + !{B}">Conditional</animation>'
                 f'\n\t<animation effect="slide" end="0,40" time="0" condition="!{R} + !{B} + $EXP[Liner_HasArtistFacts_{s}]">Conditional</animation>\n'
                 + block(facts, 1) + "\n</control>")
    # focus: the scrollers (group 9650) + a holder when there is nothing to scroll
    sc = [scroller(9661, 1450, 190, 280, down=9662), scroller(9662, 1450, 550, 200, up=9661),
          scroller(9663, 1450, 190, 560), scroller(9664, 1450, 240, 480),
          '<control type="button" id="9665">\n\t<left>0</left>\n\t<top>0</top>\n\t<width>1</width>\n\t<height>1</height>'
          "\n\t<label></label>\n\t<texturefocus />\n\t<texturenofocus />"
          f"\n\t<visible>!{R} + !{B}</visible>\n\t<onfocus>SetProperty(groove.np.overlay,liner,home)</onfocus>"
          "\n\t<onback>$PARAM[origin]</onback>\n</control>"]
    parts.append('<control type="group" id="9650">\n' + block(sc, 1) + "\n</control>")
    return "\n".join([
        "<!-- Liner notes page (LinerNotes.md, board B5). params:",
        "       src        player (MusicPlayer.*, Now Playing) | item (ListItem.*, DialogMusicInfo album)",
        "       origin     numeric id Back returns to (9605 tray / 9904 album info)",
        "       room       true: draw the room ground under the page",
        "     Every row hides when empty (Liner_Has*_<src> expressions); the layout follows review / bio presence.",
        "     Focus: scrollers 9661 (review) -> 9662 (bio); 9663 review only; 9664 bio only; 9665 holder (facts only).",
        "     A vertical scrollbar at its end passes Up / Down on to its navigation. Group 9650 = page has focus. -->",
        '<include name="Groove_LinerNotes">',
        '\t<param name="room">true</param>',
        "\t<definition>",
        block(parts, 2),
        "\t</definition>",
        "</include>",
    ])


def icon_button(bid, x, y, icon, text, actions, nav, visible=None, enable=None, labelw=170):
    """Info-dialog icon button: soft glow, icon (50 % at rest), one-word label to its right on focus."""
    foc = f"Control.HasFocus({bid})"
    o = ['<control type="group">', f"\t<left>{x}</left>\n\t<top>{y}</top>\n\t<width>48</width>\n\t<height>48</height>"]
    if visible:
        o.append(f"\t<visible>{visible}</visible>")
    anims = [fade_cond(f"!{foc}", 54)]
    if enable:
        anims.append(f'<animation effect="fade" start="100" end="55" time="0" condition="![{enable}]">Conditional</animation>')
    o.append(block([img(-34, -34, 116, 116, "groove/glow_radial.png", "$VAR[focus_glow]", extra=f"<visible>{foc}</visible>\n<include>Anim_FadeVisible</include>"),
                    img(0, 0, 48, 48, icon, "$VAR[ink]", extra="\n".join(anims)),
                    label(60, 0, labelw, 48, text, "font_tray", "$VAR[ink]", extra=f"<visible>{foc}</visible>\n<include>Anim_LabelReveal</include>")], 1))
    b = [f'<control type="button" id="{bid}">', "\t<left>0</left>\n\t<top>0</top>\n\t<width>48</width>\n\t<height>48</height>",
         "\t<label></label>\n\t<texturefocus />\n\t<texturenofocus />"]
    if enable:
        b.append(f"\t<enable>{enable}</enable>")
    b += ["\t" + a for a in actions] + ["\t" + n for n in nav]
    b.append("</control>")
    o.append(block(["\n".join(b)], 1))
    o.append("</control>")
    return "\n".join(o)


def inc_info_buttons():
    up = ["<onup>9950</onup>"]
    album = "$EXP[MInfo_IsAlbum]"
    song = "$EXP[MInfo_IsSong]"
    artist = "$EXP[MInfo_IsArtist]"
    shuffle_album = [f'<onclick condition="{HELPER}">RunScript(script.karmamole.helper,action=play_shuffled,"path=musicdb://albums/$INFO[ListItem.DBID]/")</onclick>',
                     f'<onclick condition="![{HELPER}]">PlayMedia(musicdb://albums/$INFO[ListItem.DBID]/{RANDOM_SONGS},isdir)</onclick>']
    shuffle_artist = [f'<onclick condition="{HELPER}">RunScript(script.karmamole.helper,action=play_shuffled,"path=musicdb://artists/$INFO[ListItem.DBID]/")</onclick>',
                      f'<onclick condition="![{HELPER}]">PlayMedia(musicdb://artists/$INFO[ListItem.DBID]/-1/{RANDOM_SONGS},isdir)</onclick>']
    has_list = "Integer.IsGreater(Container(50).NumItems,0)"
    longbio = "Integer.IsGreater(Container(9930).NumPages,1)"
    a_row = [
        icon_button(9901, x9(0) + 54, 700, "icons/play.png", "$LOCALIZE[31702]", ["<onclick>SendClick(8)</onclick>"],
                    up + ["<onright>9902</onright>", f'<ondown condition="{album}">50</ondown>'],
                    visible=f"{album} | {song}"),
        icon_button(9902, x9(1) + 54, 700, "icons/shuffle.png", "$LOCALIZE[31710]", shuffle_album,
                    up + ["<onleft>9901</onleft>", "<onright>9904</onright>", "<ondown>50</ondown>"],
                    visible=f"{album} + {HELPER}", enable=f"Integer.IsGreater(ListItem.DBID,0) + {has_list}"),
        icon_button(9904, x9(2) + 54, 700, "icons/liner.png", "$LOCALIZE[31706]", ["<include>Liner_Open_item</include>"],
                    up + ["<onleft>9902</onleft>", "<onright>9905</onright>", "<ondown>50</ondown>"],
                    visible=f"{album} + $EXP[Liner_HasNotes_item]"),
        icon_button(9905, x9(3) + 54, 700, "$VAR[MInfo_OtherIcon]", "$VAR[MInfo_OtherLabel]", ["<onclick>SendClick(12)</onclick>"],
                    up + ["<onleft>9904</onleft>", f'<onright condition="{album}">50</onright>', f'<ondown condition="{album}">50</ondown>'],
                    visible=f"{album} | {song}"),
    ]
    # x9(i) + 54 == 150 + 196 i  (album row pitch 196 from x 150)
    r_row = [
        icon_button(9911, 96, 660, "icons/playall.png", "$LOCALIZE[31731]",
                    ["<onclick>PlayMedia(musicdb://artists/$INFO[ListItem.DBID]/,isdir)</onclick>"],
                    up + ["<onright>9912</onright>", "<ondown>50</ondown>"], visible=artist, enable="Integer.IsGreater(ListItem.DBID,0)"),
        icon_button(9912, 292, 660, "icons/shuffle.png", "$LOCALIZE[31710]", shuffle_artist,
                    up + ["<onleft>9911</onleft>", f'<onright condition="{longbio}">9913</onright>', "<onright>9914</onright>",
                          "<ondown>50</ondown>"], visible=f"{artist} + {HELPER}",
                    enable="Integer.IsGreater(ListItem.DBID,0)"),
        icon_button(9913, 488, 660, "icons/artists.png", "$LOCALIZE[31732]", ["<onclick>SetFocus(9922)</onclick>"],
                    up + ["<onleft>9912</onleft>", "<onright>9914</onright>", "<ondown>50</ondown>"], visible=f"{artist} + {longbio}"),
    ]
    # Choose art (Kodi's 10, QA N5): the artist row's last button; it takes Biography's slot when that is hidden
    # (a time-0 slide set at load). The album row has no room for a fifth button (it would run into the tracklist):
    # album art stays with the library context menu.
    r_art = icon_button(9914, 684, 660, "icons/pictures.png", "$LOCALIZE[31268]", ["<onclick>SendClick(10)</onclick>"],
                        up + [f'<onleft condition="{longbio}">9913</onleft>', "<onleft>9912</onleft>", "<ondown>50</ondown>"],
                        visible=artist, enable="Control.IsEnabled(10)")
    return "\n".join([
        "<!-- DialogMusicInfo button rows (group 9899 = the window's default control: the first visible button).",
        "     Album / song: 9901 Play (Kodi's 8), 9902 Shuffle, 9904 Liner notes, 9905 Artist (song: Album; Kodi's 12).",
        "     Artist: 9911 Play all, 9912 Shuffle, 9913 Biography (only when the bio runs over 5 lines), 9914 Choose art",
        "     (Kodi's 10; slides into 9913's slot when that is hidden).",
        "     Shuffle (9902 / 9912) shows only with script.karmamole.helper (producer 2026-10-21: without it a skin can't shuffle",
        "     one play without saving Kodi's shuffle setting); the buttons after it slide one slot left. Navigation to the",
        "     hidden button falls through to its own onleft / onright (LESSONS). Liner notes (9904) shows only when there is",
        "     something to read (Liner_HasNotes_item); Artist then takes its slot. -->",
        '<include name="MInfo_Buttons">',
        '\t<control type="group" id="9899">',
        "\t\t<defaultcontrol>9901</defaultcontrol>",
        block(a_row[:2], 2),
        '\t\t<control type="group">',
        f'\t\t\t<animation effect="slide" end="-196,0" time="0" condition="{album} + ![{HELPER}]">Conditional</animation>',
        block(a_row[2:3], 3),
        '\t\t\t<control type="group">',
        f'\t\t\t\t<animation effect="slide" end="-196,0" time="0" condition="{album} + ![$EXP[Liner_HasNotes_item]]">Conditional</animation>',
        f'\t\t\t\t<animation effect="slide" end="-392,0" time="0" condition="{song}">Conditional</animation>',
        block(a_row[3:], 4),
        "\t\t\t</control>",
        "\t\t</control>",
        '\t\t<control type="group">',
        '\t\t\t<animation effect="slide" end="0,-210" time="0" condition="String.IsEmpty(ListItem.Property(Artist_Description))">Conditional</animation>',
        block(r_row[:2], 3),
        '\t\t\t<control type="group">',
        f'\t\t\t\t<animation effect="slide" end="-196,0" time="0" condition="![{HELPER}]">Conditional</animation>',
        block(r_row[2:], 4),
        '\t\t\t\t<control type="group">',
        f'\t\t\t\t\t<animation effect="slide" end="-196,0" time="0" condition="!{longbio}">Conditional</animation>',
        block([r_art], 5),
        "\t\t\t\t</control>",
        "\t\t\t</control>",
        "\t\t</control>",
        "\t</control>",
        "</include>",
    ])


def build_info():
    parts = []
    parts.append('<expression name="MInfo_IsArtist">String.IsEqual(ListItem.DBType,artist)</expression>')
    parts.append("<!-- no real art: Kodi gives discography entries that aren't in the library DefaultAlbumCover.png -->")
    parts.append('<expression name="MInfo_ItemNoArt">String.IsEmpty(ListItem.Art(thumb)) | String.StartsWith(ListItem.Art(thumb),Default)</expression>')
    parts.append('<expression name="MInfo_IsAlbum">String.IsEqual(ListItem.DBType,album)</expression>')
    parts.append('<expression name="MInfo_IsSong">String.IsEqual(ListItem.DBType,song)</expression>')
    parts.append('<variable name="MInfo_OtherIcon"><value condition="$EXP[MInfo_IsSong]">icons/albums.png</value><value>icons/artists.png</value></variable>')
    parts.append('<variable name="MInfo_OtherLabel"><value condition="$EXP[MInfo_IsSong]">$LOCALIZE[31735]</value><value>$LOCALIZE[31730]</value></variable>')
    parts.append('<variable name="MInfo_Logo"><value condition="!String.IsEmpty(ListItem.Art(artist.clearlogo))">$INFO[ListItem.Art(artist.clearlogo)]</value><value>$INFO[ListItem.Art(clearlogo)]</value></variable>')
    parts.append("<!-- info dialog wash: TMDb Helper's blur of this item's cover (DialogMusicInfo onload, prefix GrooveInfo) -->")
    parts.append('<expression name="MInfo_HasWash">!String.IsEmpty(Window(Home).Property(TMDbHelper.GrooveInfo.BlurImage)) + String.IsEqual(Window(Home).Property(groove.info.blursrc),ListItem.Art(thumb))</expression>')
    parts.append('<variable name="MInfo_Wash"><value>$INFO[Window(Home).Property(TMDbHelper.GrooveInfo.BlurImage)]</value></variable>')
    parts.append('<expression name="MInfo_HasLogo">!String.IsEmpty(ListItem.Art(artist.clearlogo)) | !String.IsEmpty(ListItem.Art(clearlogo))</expression>')
    parts.append("<!-- album meta: year · genre · N tracks · total time (pieces drop when empty) -->")
    parts.append('<variable name="MInfo_Tracks">')
    parts.append('\t<value condition="Integer.IsEqual(Container(50).NumItems,1)">1 $LOCALIZE[31733]</value>')
    parts.append('\t<value condition="Integer.IsGreater(Container(50).NumItems,1)">$INFO[Container(50).NumItems] $LOCALIZE[31734]</value>')
    parts.append("</variable>")
    pieces = [("ListItem.Year", "$INFO[ListItem.Year]"), ("ListItem.Genre", "$INFO[ListItem.Genre]"),
              ("Container(50).NumItems", "$VAR[MInfo_Tracks]"), ("ListItem.Property(Album_Duration)", "$INFO[ListItem.Property(Album_Duration)]")]
    parts.append('<variable name="MInfo_AlbumMeta">')
    for mask in range(15, 0, -1):
        conds, vals = [], []
        for i, (inf, val) in enumerate(pieces):
            on = mask >> (3 - i) & 1
            if inf == "Container(50).NumItems":
                conds.append("Integer.IsGreater(Container(50).NumItems,0)" if on else "!Integer.IsGreater(Container(50).NumItems,0)")
            else:
                conds.append(f"!String.IsEmpty({inf})" if on else f"String.IsEmpty({inf})")
            if on:
                vals.append(val)
        parts.append(f'\t<value condition="{" + ".join(conds)}">{" · ".join(vals)}</value>')
    parts.append("</variable>")
    parts.append("<!-- song meta: album · duration (the artist is already the line above, as name or clearlogo: Pass 2 n6) -->")
    parts.append('<variable name="MInfo_SongMeta"><value condition="!String.IsEmpty(ListItem.Album)">$INFO[ListItem.Album]$INFO[ListItem.Duration, · ,]</value>'
                 '<value>$INFO[ListItem.Duration]</value></variable>')
    parts.append('<variable name="MInfo_Meta"><value condition="$EXP[MInfo_IsSong]">$VAR[MInfo_SongMeta]</value><value>$VAR[MInfo_AlbumMeta]</value></variable>')
    parts.append('<variable name="MInfo_Title">')
    parts.append('\t<value condition="$EXP[MInfo_IsSong] + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>')
    parts.append('\t<value condition="$EXP[MInfo_IsAlbum] + !String.IsEmpty(ListItem.Album)">$INFO[ListItem.Album]</value>')
    parts.append("\t<value>$INFO[ListItem.Label]</value>")
    parts.append("</variable>")
    parts += info_vars()
    parts.append("")
    parts.append(inc_liner())
    parts.append("")
    parts.append(inc_info_buttons())
    head = ['<?xml version="1.0" encoding="UTF-8"?>',
            "<!-- GENERATED by _src/make_player.py - edit the generator, then re-run it. -->",
            "<!--",
            "\tMusic info (M3): the Liner notes page (Now Playing overlay + album info page), DialogMusicInfo pieces.",
            "\tIds: Liner notes 9650 (group), 9651-9654 text, 9661-9665 focus, 9667 facts, 9668-9669 probes;",
            "\tinfo buttons 9899 (group) / 9901-9905 / 9911-9913; artist bio 9930; biography page 9920-9922;",
            "\thidden artists list 9940 (album info: the artist's bio and facts).",
            "-->",
            "<includes>"]
    return "\n".join(head + [block(parts, 1), "</includes>", ""])


def main():
    OUT_PLAYER.write_text(build_player(), encoding="utf-8", newline="\n")
    OUT_INFO.write_text(build_info(), encoding="utf-8", newline="\n")
    for p in (OUT_PLAYER, OUT_INFO):
        t = p.read_text(encoding="utf-8")
        assert t.count("<?xml") == 1 and not any(ord(ch) < 9 or 13 < ord(ch) < 32 for ch in t), p
        print("wrote", p.relative_to(SKIN), f"({t.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
