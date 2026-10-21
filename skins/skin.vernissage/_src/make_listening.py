"""Generate 1080i/Includes_ListeningRoom.xml: "The listening room" (M3).   python skins/skin.vernissage/_src/make_listening.py

Now Playing (MusicVisualisation), its transport row (MusicOSD) and the album / artist / song placard (DialogMusicInfo).
SPEC 9 / 10, DESIGN 6 (board 07), docs/skin.vernissage/screens/MusicVisualisation_ListeningRoom.md. Replaces the M1
hand-written skeleton (same ids, same navigation).

Ids: 2 visualisation (Kodi); 9699 the full-screen OK catcher on the bare Now Playing; MusicOSD transport 9601
Play/Pause (default), 9602 Previous, 9603 Next, 9604 Queue, 9605 Visualiser (Room in Visualiser mode), 9606 Info,
9607 Presets at fixed slots; placard group 9640, its title probes 9641-9646. DialogMusicInfo: action row 9910
(9911 Play, 9912 Shuffle with the helper, 9913 Tracklist, 9914 More), placard 9915, probes 9921-9926, Kodi's list 50,
Kodi's buttons 6 / 8 / 10 / 12 offscreen (ours SendClick them).
Visualiser mode = Skin.HasSetting(vernissage.np.viz): control 2 full screen, the room / sleeve / placard hide, the
transport row draws a caption + progress line over the band. Presets is one Left from Play/Pause (it wraps).
The sleeve hangs as a work; the disc behind it is STATIC (disc art, else a black disc with the cover as its label):
nothing in the room moves on its own (SPEC 2.4).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_textures as T  # noqa: E402
import placard as PL  # noqa: E402
from vnxml import DARK, DAY, NL, group, img, ind, join_and, label  # noqa: E402

OUT = HERE.parent / "1080i" / "Includes_ListeningRoom.xml"
S = dict(room=31652, next=31754, tracks=31734, track=31733, albums=31739, album=31740, play=31755, shuffle=31780,
         tracklist=31760, more=31761, with_=31494)

# board 07: sleeve 560 in a 20 px mat + hairline at (170, 196); the disc (536) slid half out behind it, its centre
# 40 px inside the frame's right edge; the placard 70 px right of the disc, exactly the mat's height
SL = (170, 196, 604, 604)
DISC = (466, 230, 536, 536)
NP_PL = (1072, 198, 728, 600)
NP_PAD = (32, 36)


def music_flags(p):
    """Codec + channels from the playing file (DESIGN 6: albums show codec, bitrate, channels; no bitrate texture)."""
    rows = [(lab, f"String.IsEqual({p}.Codec,{c})") for lab, c in
            (("FLAC", "flac"), ("MP3", "mp3"), ("AAC", "aac"), ("OPUS", "opus"), ("DD", "ac3"), ("DD+", "eac3"),
             ("DTS", "dca"), ("TRUEHD", "truehd"))]
    rows += [(lab, f"String.IsEqual({p}.Channels,{n})") for lab, n in (("1.0", 1), ("2.0", 2), ("5.1", 6), ("7.1", 8))]
    imgs = NL.join(img(None, None, T.flag_width(lab), 36, f"vn/flags/{T.flag_slug(lab)}.png", "$VAR[ink2]", vis=c) for lab, c in rows)
    return NL.join(['<control type="grouplist">', "\t<width>640</width>", "\t<height>36</height>",
                    "\t<orientation>horizontal</orientation>", "\t<itemgap>10</itemgap>", ind(imgs, 1), "</control>"])


def bar(iw):
    """Progress line + elapsed / remaining (board 07): 3 + 12 + 38."""
    return NL.join([
        img(0, 0, iw, 3, "vn/white.png", "$VAR[rule]"),
        NL.join(['<control type="progress">', "\t<left>0</left>", "\t<top>0</top>", f"\t<width>{iw}</width>",
                 "\t<height>3</height>", "\t<info>Player.Progress</info>", "\t<texturebg>vn/clear.png</texturebg>",
                 '\t<midtexture colordiffuse="$VAR[progress]">vn/white.png</midtexture>', "</control>"]),
        label(0, 15, iw // 2, 38, "$VAR[VN_TimeNow]", "font_small", "$VAR[ink2]", aligny="center", selected=False),
        label(iw // 2, 15, iw - iw // 2, 38, "–$VAR[VN_TimeLeft]", "font_small", "$VAR[ink2]", align="right",
              aligny="center", selected=False)])


def sep_join(parts, cond=None):
    """Conditional values for "a · b · c" where any part may be empty (device audit M5: "· Various" when an album has
    no record label). parts = [(infolabel, lead)]: lead is printed before the part when it is the first one shown
    (the rating's star). One value per possible first part, so no line starts or ends with the separator."""
    vals = []
    for i, (lab, lead) in enumerate(parts):
        c = [f"!String.IsEmpty({lab})"] + [f"String.IsEmpty({q})" for q, _ in parts[:i]]
        if cond:
            c = [f"[{cond}]"] + c
        rest = "".join(f"$INFO[{q}, · ,]" for q, _ in parts[i + 1:])
        vals.append((" + ".join(c), f"$INFO[{lab},{lead},]{rest}" if lead else f"$INFO[{lab}]{rest}"))
    return vals


def np_placard():
    x, y, w, h = NP_PL
    iw = w - 2 * NP_PAD[1] - 2
    fields = [
        PL.title("$INFO[MusicPlayer.Album]"),
        PL.byline("$INFO[MusicPlayer.Artist]$INFO[MusicPlayer.Year, · ,]"),
        PL.line("genres", "$VAR[NP_Line3]", "top",
                when="[!String.IsEmpty(MusicPlayer.Property(Album_Label)) | !String.IsEmpty(MusicPlayer.Genre)]"),
        PL.line("made", "$VAR[NP_Styles]", "mid",
                when="[!String.IsEmpty(MusicPlayer.Property(Album_Style)) | !String.IsEmpty(MusicPlayer.Property(Album_Mood)) | "
                     "!String.IsEmpty(MusicPlayer.Property(Artist_Style)) | !String.IsEmpty(MusicPlayer.Property(Artist_Mood))]"),
        PL.box("premise", "$VAR[NP_Prem]", "mid", "font_small", 2, gap=12, grow=5,
               when="!String.IsEmpty(MusicPlayer.Property(Album_Description)) | !String.IsEmpty(MusicPlayer.Property(Artist_Description))"),
        PL.custom("flags", music_flags("MusicPlayer"), 36, when="!String.IsEmpty(MusicPlayer.Codec)"),
        PL.rule(),
        PL.keyline("$INFO[MusicPlayer.TrackNumber,, · ]$INFO[MusicPlayer.Title]", gap=14),
        PL.custom("bar", bar(iw), 53, gap=12),
        PL.line("next", f"$LOCALIZE[{S['next']}]$INFO[MusicPlayer.offset(1).TrackNumber, · ,]$INFO[MusicPlayer.offset(1).Title, · ,]",
                "bot", gap=6, when="!String.IsEmpty(MusicPlayer.offset(1).Title)"),
    ]
    probes = dict(zip(("t44", "t36", "t30", "t2", "byline", "tagline"), range(9641, 9647)))
    return PL.curator(fields, x, y, w, h, NP_PAD, probes, cid=9640)


def lit(fr, art, mat, aspect="scale"):
    x, y, w, h = fr
    a = mat + 2
    return NL.join([
        img(x - 50, y - 42, w + 100, h + 104, "vn/shadow.png", "$VAR[shadow]", border="56", anims=["<include>VN_ShadowSteps</include>"]),
        img(x, y, w, h, "vn/white.png", "$VAR[frame]"),
        img(x + 2, y + 2, w - 4, h - 4, "vn/white.png", "$VAR[mat]"),
        img(x + a, y + a, w - 2 * a, h - 2 * a, art, aspect=aspect, background=True, fadetime=300,
            fallback="vn/print_blank.png"),
        img(x + 2, y + 2, w - 4, h - 4, "vn/mat_falloff.png", vis=DARK)])


def pool(fr, player=True, scale=(2.05, 1.5)):
    x, y, w, h = fr
    pw, ph = round(w * scale[0]), round(h * scale[1])
    px, py = x + w // 2 - pw // 2, y + h // 2 - round(0.03 * h) - ph // 2
    inc = "VN_ArtSpotPlayer" if player else "VN_ArtSpot"
    return NL.join([img(px, py, pw, ph, "vn/spot.png", "$VAR[spot]", anims=["<include>VN_SpotSteps</include>"]),
                    f'<include content="{inc}"><param name="left" value="{px}"/><param name="top" value="{py}"/>'
                    f'<param name="width" value="{pw}"/><param name="height" value="{ph}"/></include>'])


def disc(rect, disc_art, has_disc, cover, day_shadow=True):
    """The static disc behind the sleeve: disc art, else a black disc with the cover as its round label."""
    x, y, w, h = rect
    lab = round(w * 0.335)
    o = []
    if day_shadow:
        o.append(img(x + w // 2 - 26, y + 18 - 42, w // 2 + 100, h + 84, "vn/shadow.png", "$VAR[shadow]", border="56",
                     anims=['<animation effect="fade" start="100" end="35" time="0" condition="true">Conditional</animation>',
                            "<include>VN_ShadowSteps</include>"]))
    o.append(img(x, y, w, h, disc_art, aspect="keep", background=True, vis=has_disc))
    # no disc art: a plain black disc (only its outer half shows beside the sleeve, so a cover label would peek out
    # as a sliver; the device check of 2026-10-21 showed it)
    o.append(img(x, y, w, h, "vn/dot.png", "black", vis=f"!{has_disc}" if "|" not in has_disc else f"![{has_disc}]"))
    return NL.join(o)


HAS_DISC = "[!String.IsEmpty(Player.Art(album.discart)) | !String.IsEmpty(Player.Art(discart))]"


def np_room():
    sub = label(120, 58, 800, 41, f"$LOCALIZE[{S['room']}]", "font_body", "$VAR[ink2]", aligny="center", selected=False)
    body = [ "<include>VN_Room</include>", sub, pool(SL), disc(DISC, "$VAR[NP_Disc]", HAS_DISC, "$VAR[NP_Sleeve]"),
            lit(SL, "$VAR[NP_Sleeve]", 20), np_placard(), "<include>VN_Clock</include>"]
    return group(body, vis="!$EXP[NP_VizMode]", anims=['<animation effect="fade" time="300">Visible</animation>',
                                                        '<animation effect="fade" time="200">Hidden</animation>'])


# ================================================================ the transport row (MusicOSD)
def nav_first(direction, candidates, fallback):
    """Conditional numeric navigation: the first visible candidate, else the fallback (Kodi takes the FIRST numeric
    action whose condition holds: CGUIAction::GetNavigation)."""
    return [f'<{direction} condition="Control.IsVisible({c})">{c}</{direction}>' for c in candidates] + \
           [f"<{direction}>{fallback}</{direction}>"]


# id, x, label box width, icon, label, visible, onclick, navigation. A visible condition goes on the BUTTON itself
# (and its looks), not on a wrapping group: a hidden group stops processing its children, so the button would keep a
# stale "visible" (Control.IsVisible, focus); on its own condition, Kodi moves a focused button that hides to the
# default control 9601 (CGUIWindow::DoProcess: !CanFocus -> default)
TRANSPORT = [
    (9601, 120, 124, "$VAR[NP_PlayPauseIcon]", "$VAR[NP_PlayPauseLabel]", None, "PlayerControl(Play)",
     ['<onleft condition="Control.IsVisible(9607)">9607</onleft>', "<onright>9602</onright>"]),
    (9602, 310, 157, "vn/icons/prev.png", "$LOCALIZE[31753]", None, "PlayerControl(Previous)", ["<onleft>9601</onleft>", "<onright>9603</onright>"]),
    (9603, 533, 101, "vn/icons/next.png", "$LOCALIZE[31754]", None, "PlayerControl(Next)", ["<onleft>9602</onleft>", "<onright>9604</onright>"]),
    (9604, 700, 127, "vn/icons/queue.png", "$LOCALIZE[31752]", None, "ActivateWindow(musicplaylist)",
     ["<onleft>9603</onleft>", *nav_first("onright", (9605, 9606, 9607), 9601)]),
    (9605, 893, 171, "$VAR[NP_VizIcon]", "$VAR[NP_VizLabel]", "Visualisation.Enabled", "Skin.ToggleSetting(vernissage.np.viz)",
     ["<onleft>9604</onleft>", *nav_first("onright", (9606, 9607), 9601)]),
    # Info: library songs only (Kodi opens song information from a library list item: the 1 px list 9608); a stream or
    # a file outside the library has no MusicPlayer.DBID, so the button hides and its neighbours skip it (QA O3)
    (9606, 1130, 90, "vn/icons/info.png", "$LOCALIZE[31757]", "$EXP[NP_HasSongInfo]", "SetFocus(9608)|Action(Info)|SetFocus(9606)",
     [*nav_first("onleft", (9605,), 9604), *nav_first("onright", (9607,), 9601)]),
    (9607, 1286, 109, "vn/icons/presets.png", "$LOCALIZE[31751]", "$EXP[NP_HasPresets]", "ActivateWindow(visualisationpresetlist)",
     [*nav_first("onleft", (9606, 9605), 9604), "<onright>9601</onright>"]),
]


def transport():
    o = [group([img(0, 540, 1920, 280, "vn/scrim_bottom.png"), img(0, 820, 1920, 260, "vn/white.png", "scrim_band")],
               vis="$EXP[NP_VizMode]")]
    # Visualiser mode: what plays, over the band (the room's placard is hidden there)
    viz = group([
        label(120, 838, 1300, 41, "$INFO[MusicPlayer.TrackNumber,, · ]$INFO[MusicPlayer.Title]$INFO[MusicPlayer.Artist, · ,]",
              "font_body", "$VAR[ink]", aligny="center", selected=False),
        label(1300, 840, 500, 38, "$VAR[VN_TimeNow] · –$VAR[VN_TimeLeft]", "font_small", "$VAR[ink2]",
              align="right", aligny="center", selected=False),
        img(120, 904, 1680, 3, "vn/white.png", "track_on_video"),
        NL.join(['<control type="progress">', "\t<left>120</left>", "\t<top>904</top>", "\t<width>1680</width>",
                 "\t<height>3</height>", "\t<info>Player.Progress</info>", "\t<texturebg>vn/clear.png</texturebg>",
                 '\t<midtexture colordiffuse="$VAR[ink]">vn/white.png</midtexture>', "</control>"])], vis="$EXP[NP_VizMode]")
    o.append(viz)
    for cid, x, lw, icon, lab, vis, click, nav in TRANSPORT:
        hf = f"Control.HasFocus({cid})"
        btn = NL.join([f'<control type="button" id="{cid}">', "\t<left>0</left>", "\t<top>0</top>", "\t<width>48</width>",
                       "\t<height>48</height>", "\t<label></label>", "\t<texturefocus />", "\t<texturenofocus />",
                       f"\t<onfocus>SetProperty(vn.np.last,{cid},home)</onfocus>", *[f"\t<onclick>{c}</onclick>" for c in click.split("|")],
                       *[f"\t{n}" for n in nav], *([f"\t<visible>{vis}</visible>"] if vis else []), "</control>"])
        face = NL.join(['<include content="VN_IconFace">', f'\t<param name="id" value="{cid}"/>', f'\t<param name="icon" value="{icon}"/>',
                        f'\t<param name="label" value="{lab}"/>', f'\t<param name="width" value="{lw}"/>',
                        '\t<param name="height" value="48"/>', '\t<param name="icon_top" value="0"/>',
                        '\t<param name="label_x" value="66"/>', "</include>"])
        looks = [img(-46, -46, 140, 140, "vn/spot.png", "$VAR[spot]", vis=f"{hf} + {DARK}",
                     anims=['<animation effect="fade" start="100" end="73" time="0" condition="true">Conditional</animation>']),
                 img(-16, -16, 80, 80, "vn/dot.png", "$VAR[focus_fill]", vis=f"{hf} + {DAY}")]
        if vis:
            o.append(group([group(looks, vis=vis), btn, group([face], vis=vis)], left=x, top=968))
        else:
            o.append(group([*looks, btn, face], left=x, top=968))
    o.append(NL.join(['<control type="list" id="9608">', "\t<left>0</left>", "\t<top>0</top>", "\t<width>1</width>",
                      "\t<height>1</height>", "\t<onup>9606</onup>", "\t<ondown>9606</ondown>", "\t<onleft>9606</onleft>",
                      "\t<onright>9606</onright>", '\t<itemlayout width="1" height="1" />', '\t<focusedlayout width="1" height="1" />',
                      '\t<content target="music" limit="1" browse="never">musicdb://songs/?songid=$INFO[MusicPlayer.DBID]</content>',
                      "\t<visible>!String.IsEmpty(MusicPlayer.DBID)</visible>", "</control>"]))
    return group(o, anims=['<animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>',
                           '<animation effect="fade" start="100" end="0" time="150">WindowClose</animation>'])


def viz_hint():
    band = group([img(960, 900, 960, 180, "vn/scrim_bottom.png")], vis="$EXP[NP_HasPresets] + !Window.IsVisible(musicosd)",
                 anims=['<animation effect="fade" time="300">Visible</animation>', '<animation effect="fade" time="200">Hidden</animation>'])
    return band + NL + label(None, 984, 1000, 38, "$LOCALIZE[31759]", "font_small", "$VAR[ink2]", align="right", aligny="center",
                 vis="$EXP[NP_HasPresets] + !Window.IsVisible(musicosd)", selected=False,
                 anims=['<animation effect="fade" time="300">Visible</animation>', '<animation effect="fade" time="200">Hidden</animation>']
                 ).replace("<top>984</top>", "<right>vn_margin</right>\n\t<top>984</top>")


# ================================================================ DialogMusicInfo: album / artist / song
MI_FR = (120, 130, 644, 644)          # sleeve 600 in a 20 px mat
MI_DISC = (420, 164, 576, 576)        # centre 40 px inside the frame's right edge
MI_PL = (1078, 132, 722, 640)
MI_PAD = (32, 36)
AL, AR, SO = ("String.IsEqual(ListItem.DBType,album)", "String.IsEqual(ListItem.DBType,artist)",
              "String.IsEqual(ListItem.DBType,song)")
HELPER_SHUFFLE = ("System.HasAddon(script.karmamole.helper) + System.AddonIsEnabled(script.karmamole.helper) + "
                  "String.IsEqual(Window(Home).Property(KarmaMole.Helper.Running),true) + "
                  "String.Contains(Window(Home).Property(KarmaMole.Helper.Active),shuffle)")


def mi_variables():
    v = []

    def var(name, values):
        v.append(f'\t<variable name="{name}">')
        for c, val in values:
            v.append(f'\t\t<value condition="{c}">{val}</value>' if c else f"\t\t<value>{val}</value>")
        v.append("\t</variable>")
    var("MI_Title", [(AL, "$INFO[ListItem.Album]"), (SO, "$INFO[ListItem.Title]"), (None, "$INFO[ListItem.Label]")])
    var("MI_Byline", [(AL, "$INFO[ListItem.Artist]$INFO[ListItem.Year, · ,]"), (AR, "$INFO[ListItem.Property(Artist_Genre)]"),
                      (SO, "$INFO[ListItem.Artist]$INFO[ListItem.Album, · ,]"), (None, "$INFO[ListItem.Year]")])
    var("MI_Line3", sep_join([("ListItem.Property(Album_Label)", ""), ("ListItem.Genre", "")], AL) + [(AL, "")]
        + sep_join([("ListItem.Property(Artist_Born)", ""), ("ListItem.Property(Artist_Formed)", ""),
                    ("ListItem.Property(Artist_YearsActive)", "")], AR) + [(AR, "")]
        + sep_join([("ListItem.Year", ""), ("ListItem.Genre", "")]))
    var("MI_Styles", sep_join([("ListItem.Rating", "★ "), ("ListItem.Property(Album_Style)", ""),
                               ("ListItem.Property(Album_Mood)", "")], AL) + [(AL, "")]
        + sep_join([("ListItem.Property(Artist_Style)", ""), ("ListItem.Property(Artist_Mood)", "")]))
    var("MI_Prem", [(AL, "$INFO[ListItem.Property(Album_Description)]"), (AR, "$INFO[ListItem.Property(Artist_Description)]"),
                    (None, "$INFO[ListItem.Comment]")])
    var("MI_Key", [(f"{AL} + Integer.IsEqual(Container(50).NumItems,1)", f"1 $LOCALIZE[{S['track']}]"),
                   (AL, f"$INFO[Container(50).NumItems] $LOCALIZE[{S['tracks']}]"),
                   (f"{AR} + Integer.IsEqual(Container(50).NumItems,1)", f"1 $LOCALIZE[{S['album']}]"),
                   (AR, f"$INFO[Container(50).NumItems] $LOCALIZE[{S['albums']}]"),
                   (None, "$INFO[ListItem.Duration]")])
    var("MI_Art", [("!String.IsEmpty(ListItem.Art(thumb))", "$INFO[ListItem.Art(thumb)]"), (None, "$INFO[ListItem.Icon]")])
    var("MI_Disc", [("!String.IsEmpty(ListItem.Art(discart))", "$INFO[ListItem.Art(discart)]"), (None, "$INFO[ListItem.Art(album.discart)]")])
    var("MI_ShufflePath", [(AR, "musicdb://artists/$INFO[ListItem.DBID]/"), (None, "musicdb://albums/$INFO[ListItem.DBID]/")])
    return NL.join(v)


def mi_placard():
    fields = [
        PL.title("$VAR[MI_Title]"), PL.byline("$VAR[MI_Byline]"),
        PL.line("genres", "$VAR[MI_Line3]", "top", when="!String.IsEmpty(ListItem.Genre) | !String.IsEmpty(ListItem.Property(Album_Label)) | "
                "!String.IsEmpty(ListItem.Property(Artist_Born)) | !String.IsEmpty(ListItem.Property(Artist_Formed))"),
        PL.line("made", "$VAR[MI_Styles]", "mid", when="!String.IsEmpty(ListItem.Property(Album_Style)) | !String.IsEmpty(ListItem.Property(Album_Mood)) | "
                "!String.IsEmpty(ListItem.Property(Artist_Style)) | !String.IsEmpty(ListItem.Property(Artist_Mood))"),
        PL.box("premise", "$VAR[MI_Prem]", "mid", "font_small", 2, gap=12, grow=8,
               when="!String.IsEmpty(ListItem.Property(Album_Description)) | !String.IsEmpty(ListItem.Property(Artist_Description)) | "
                    "!String.IsEmpty(ListItem.Comment)"),
        PL.rule(), PL.keyline("$VAR[MI_Key]", gap=14), PL.custom("actions", "", 64, gap=22)]
    probes = dict(zip(("t44", "t36", "t30", "t2", "byline", "tagline"), range(9921, 9927)))
    return PL.curator(fields, *MI_PL, MI_PAD, probes, cid=9915)


MI_SLOTS = [(9911, 9916, 168, "vn/icons/play.png", f"$LOCALIZE[{S['play']}]", "!String.IsEqual(ListItem.DBType,artist)", "SendClick(8)"),
            (9912, 9917, 196, "vn/icons/shuffle.png", f"$LOCALIZE[{S['shuffle']}]", f"{HELPER_SHUFFLE} + [{AL} | {AR}]",
             'RunScript(script.karmamole.helper,action=play_shuffled,"path=$VAR[MI_ShufflePath]")'),
            (9913, 9918, 220, "vn/icons/songs.png", "$VAR[MI_ListLabel]", "Integer.IsGreater(Container(50).NumItems,0)", "SetFocus(50)"),
            (9914, 9919, 168, "vn/icons/more.png", f"$LOCALIZE[{S['more']}]", "Control.IsEnabled(12)", "SendClick(12)")]


def mi_actions():
    x, y, w, h = MI_PL
    kids = []
    for cid, gid, sw, icon, lab, vis, click in MI_SLOTS:
        btn = NL.join([f'<control type="button" id="{cid}">', f"\t<width>{sw}</width>", "\t<height>64</height>", "\t<label></label>",
                       "\t<texturefocus />", "\t<texturenofocus />", f"\t<onclick>{click}</onclick>", "\t<onup>noop</onup>",
                       "\t<ondown>50</ondown>", f"\t<visible>{vis}</visible>", "</control>"])
        face = NL.join([f'<control type="group" id="{gid}">', f"\t<left>-{sw}</left>", f"\t<width>{sw}</width>", "\t<height>64</height>",
                        f"\t<visible>{vis}</visible>", '\t<include content="VN_IconFace">', f'\t\t<param name="id" value="{cid}"/>',
                        f'\t\t<param name="icon" value="{icon}"/>', f'\t\t<param name="label" value="{lab}"/>',
                        f'\t\t<param name="width" value="{sw - 62}"/>', '\t\t<param name="label_x" value="62"/>', "\t</include>", "</control>"])
        kids += [btn, face]
    return NL.join(['<control type="grouplist" id="9910">', f"\t<left>{x + MI_PAD[1] + 1}</left>", f"\t<top>{y + h - MI_PAD[0] - 1 - 64}</top>",
                    f"\t<width>{w - 2 * MI_PAD[1] - 2}</width>", "\t<height>64</height>", "\t<orientation>horizontal</orientation>",
                    "\t<itemgap>0</itemgap>", "\t<usecontrolcoords>true</usecontrolcoords>", "\t<onleft>noop</onleft>",
                    "\t<onright>noop</onright>", ind(NL.join(kids), 1), "</control>"])


def mi_list():
    rule = lambda room, gate: img(0, 0, 1680, 64, "vn/row_rule.png", f"{room}_ink", border="0,0,0,3", vis=f"Control.HasFocus(50) + {gate}")  # noqa: E731
    row = lambda c1, c2: NL.join(['<include content="Lib_CatalogueRow">', f'\t<param name="color" value="{c1}"/>',  # noqa: E731
                                  f'\t<param name="color2" value="{c2}"/>', "</include>"])
    return NL.join(['<control type="list" id="50">', "\t<left>120</left>", "\t<top>808</top>", "\t<width>1680</width>",
                    "\t<height>192</height>", "\t<onup>9910</onup>", "\t<ondown>noop</ondown>", "\t<onleft>noop</onleft>",
                    "\t<onright>noop</onright>", "\t<onback>9910</onback>", '\t<scrolltime tween="cubic" easing="out">200</scrolltime>',
                    f'\t<itemlayout width="1680" height="64">{NL}{ind(row("$VAR[ink2]", "$VAR[ink2]"), 2)}{NL}\t</itemlayout>',
                    f'\t<focusedlayout width="1680" height="64">{NL}{ind(NL.join([rule("day", DAY), rule("eve", DARK), row("$VAR[ink]", "$VAR[ink2]")]), 2)}'
                    f"{NL}\t</focusedlayout>", "</control>"])


def mi_body():
    has_disc = "[!String.IsEmpty(ListItem.Art(discart)) | !String.IsEmpty(ListItem.Art(album.discart))]"
    stage = [pool(MI_FR, player=False), group([disc(MI_DISC, "$VAR[MI_Disc]", has_disc, "$VAR[MI_Art]")], vis=AL),
             lit(MI_FR, "$VAR[MI_Art]", 20), mi_placard(), mi_actions(), mi_list(), "<include>VN_Clock</include>"]
    kodi = [NL.join([f'<control type="button" id="{k}">', "\t<include>VN_Hidden</include>", "</control>"]) for k in (8, 12, 6, 10)]
    return NL.join(["<include>VN_Room</include>", group(stage, anims=["<include>Anim_WindowContent</include>"]), *kodi])


def main():
    PL.set_prefix("NP")
    room, osd, hint, mi = np_room(), transport(), viz_hint(), mi_body()
    def xml_var(name, values):
        o = [f'\t<variable name="{name}">']
        o += [f'\t\t<value condition="{c}">{val}</value>' if c else f"\t\t<value>{val}</value>" for c, val in values]
        return NL.join(o + ["\t</variable>"])
    alb_style = "!String.IsEmpty(MusicPlayer.Property(Album_Style)) | !String.IsEmpty(MusicPlayer.Property(Album_Mood))"
    np_sep = NL.join([
        xml_var("NP_Line3", sep_join([("MusicPlayer.Property(Album_Label)", ""), ("MusicPlayer.Genre", "")])),
        xml_var("NP_Styles", sep_join([("MusicPlayer.Rating", "★ "), ("MusicPlayer.Property(Album_Style)", ""),
                                       ("MusicPlayer.Property(Album_Mood)", "")], alb_style)
                + sep_join([("MusicPlayer.Property(Artist_Style)", ""), ("MusicPlayer.Property(Artist_Mood)", "")]))])
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_listening.py - edit the generator, then re-run. "The listening room": Now Playing,
     its transport row (MusicOSD) and the album / artist / song placard (DialogMusicInfo). -->
<includes>
	<expression name="NP_VizMode">Skin.HasSetting(vernissage.np.viz) + Visualisation.Enabled</expression>
	<expression name="NP_HasPresets">$EXP[NP_VizMode] + Visualisation.HasPresets</expression>
	<expression name="NP_HasSongInfo">!String.IsEmpty(MusicPlayer.DBID)</expression>
__PLACARD_EXPRS__
	<variable name="NP_PlayPauseIcon">
		<value condition="Player.Paused">vn/icons/play.png</value>
		<value>vn/icons/pause.png</value>
	</variable>
	<variable name="NP_PlayPauseLabel">
		<value condition="Player.Paused">$LOCALIZE[31755]</value>
		<value>$LOCALIZE[31756]</value>
	</variable>
	<variable name="NP_Sleeve">
		<value condition="!String.IsEmpty(Player.Art(thumb))">$INFO[Player.Art(thumb)]</value>
		<value>$INFO[MusicPlayer.Cover]</value>
	</variable>
{np_sep}
	<variable name="NP_Prem">
		<value condition="!String.IsEmpty(MusicPlayer.Property(Album_Description))">$INFO[MusicPlayer.Property(Album_Description)]</value>
		<value>$INFO[MusicPlayer.Property(Artist_Description)]</value>
	</variable>
	<variable name="NP_Disc">
		<value condition="!String.IsEmpty(Player.Art(album.discart))">$INFO[Player.Art(album.discart)]</value>
		<value>$INFO[Player.Art(discart)]</value>
	</variable>
	<variable name="NP_VizIcon">
		<value condition="Skin.HasSetting(vernissage.np.viz)">vn/icons/music.png</value>
		<value>vn/icons/visualiser.png</value>
	</variable>
	<variable name="NP_VizLabel">
		<value condition="Skin.HasSetting(vernissage.np.viz)">$LOCALIZE[31762]</value>
		<value>$LOCALIZE[31750]</value>
	</variable>
	<variable name="MI_ListLabel">
		<value condition="String.IsEqual(ListItem.DBType,artist)">$LOCALIZE[{31741}]</value>
		<value>$LOCALIZE[{S['tracklist']}]</value>
	</variable>
{mi_variables()}

	<!-- Now Playing (MusicVisualisation): the sleeve hung as a work, the static disc, the curator's card -->
	<include name="NP_Room">
{ind(room, 2)}
	</include>

	<!-- Visualiser mode: the quiet presets hint, bottom right, while the transport row is closed -->
	<include name="NP_VizHint">
{ind(hint, 2)}
	</include>

	<!-- the transport row (MusicOSD): seven standalone buttons at fixed slots (screens: conditional numeric
	     navigation, which grouplist exits don't take); Left from Play/Pause wraps to Presets when it shows -->
	<include name="NP_Transport">
{ind(osd, 2)}
	</include>

	<!-- album / artist / song placard (DialogMusicInfo; Kodi also loads it for songinformation) -->
	<include name="MInfo_Body">
{ind(mi, 2)}
	</include>
</includes>
"""
    body = body.replace("__PLACARD_EXPRS__", PL.expressions_xml(body))
    OUT.write_text(body, encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {body.count('<control')} controls, {len(body) // 1024} KB")


if __name__ == "__main__":
    main()
