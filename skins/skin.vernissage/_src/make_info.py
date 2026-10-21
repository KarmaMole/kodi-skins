"""Generate 1080i/Includes_VideoInfo.xml: "The placard" (M3).   python skins/skin.vernissage/_src/make_info.py

DialogVideoInfo for films, series, seasons, episodes and sets (SPEC 9, DESIGN 6 revised board 06,
docs/skin.vernissage/screens/DialogVideoInfo_Placard.md for ids, focus and the More card).

Geometry (board 06, mockups/_src/make_boards.py b06): the work = fanart cropped 6:5 (880 x 733, aspectratio scale)
in an 18 px mat + 2 px hairline -> frame 920 x 773 at (120, 130); the placard 40 px right of it, exactly the mat's
height: (1080, 132, 720, 769), padding 28 / 36. No fanart: the poster (489 x 733), work and placard centred.

Kodi ids (Estuary Omega DialogVideoInfo.xml, GUIDialogVideoInfo.cpp): 8 play / browse, 9 resume (enabled only when
part-way), 10 choose art, 11 trailer, 6 refresh, 50 the list Kodi fills (cast; a set's films). Kodi writes labels into
its buttons, so they stay offscreen and ours click them (SendClick from inside the dialog targets the dialog).
Ours: action row 9930 (grouplist): 9931 Play (film / episode not part-way: SendClick(8); show: the next episode),
9932 Resume (SendClick(9)), 9933 Episodes / Works (SendClick(8): Kodi opens the folder), 9935 Trailer (SendClick(11)),
9934 More. Placards: one per kind (film 9900, show / season, episode, set), probes 9901-9924 (6 per kind). More card 9940: plot 9941,
scrollbar 9942, rows 9946 (9947 From the start, 9948 Series of works, 9949 Choose art, 9945 Refresh), cast 50.
Data lists (always processed while their kind is on show, LESSONS 139): 9960 = a show's next unseen episode, 9961 =
the works of the film's set (count, years, "n of N in <set>"); every read is gated on the ids matching (LESSONS 222).

Focus: opens on the first action (defaultcontrol always 9930); Left / Right walk the row (ends stop); Down opens More
on the cast row (or its rows); More: Up / Down / Left / Right inside, Back -> 9934 (numeric, consumes Back), Back on
the row closes the dialog (Kodi).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placard as PL  # noqa: E402
from vnxml import DARK, NBSP, NL, fade_cond, group, img, ind, join_and, label, twin_img  # noqa: E402

OUT = HERE.parent / "1080i" / "Includes_VideoInfo.xml"
S = dict(of=31671, in_=31763, resume=31764, trailer=31765, works=31766, start=31767, all_seen=31774, next=31775,
         art=31776, refresh=31777, story=31778, cast=31779, not_started=31781, written=31782, series=31785,
         with_=31494, part_of=31495, play=31755, more=31761, episodes=31663, Unseen=31669, Seen=31670,
         in_progress=31475, eps_to_go=31476, ep_to_go=31477, none_seen=31672, seen=31673, work=31662, works_lc=31661,
         aired=31678, ends=31451, min=31221)

DB = lambda t: f"String.IsEqual(ListItem.DBType,{t})"  # noqa: E731
FILM, SHOW, SEASON, EP, SET = (DB(t) for t in ("movie", "tvshow", "season", "episode", "set"))
FOLDER = f"[{SHOW} | {SEASON} | {SET}]"
PLAYABLE = f"!{FOLDER}"
PARTWAY = "Control.IsEnabled(9)"
NEXT_OK = ("String.IsEqual(ListItem.DBType,tvshow) + Integer.IsGreater(Container(9960).NumItems,0) + "
           "Integer.IsEqual(Container(9960).ListItem.TvShowDBID,ListItem.DBID)")
SET_OK = ("[[String.IsEqual(ListItem.DBType,set) + Integer.IsEqual(Container(9961).ListItemAbsolute(0).SetId,ListItem.DBID)] | "
          "[!String.IsEqual(ListItem.DBType,set) + !String.IsEmpty(ListItem.Set) + "
          "Integer.IsEqual(Container(9961).ListItemAbsolute(0).SetId,ListItem.SetId)]] + Integer.IsGreater(Container(9961).NumItems,0)")
WIDE = (f"[{EP} + [!String.IsEmpty(ListItem.Art(thumb)) | !String.IsEmpty(ListItem.Art(tvshow.fanart)) | !String.IsEmpty(ListItem.Art(fanart))]] | "
        f"[!{EP} + [!String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(tvshow.fanart))]]")
MAXSET = 30

# board 06
FR = (120, 130, 920, 773)           # fanart frame (art 880 x 733, mat 18)
FR_P = (120, 130, 529, 773)         # poster frame (art 489 x 733)
MAT = 18
PL_W = (1080, 132, 720, 769)
PAD = (28, 36)
ACT_H = 64


def ends(p="ListItem"):
    return f"$LOCALIZE[{S['ends']}]{NBSP}[LOWERCASE]$INFO[{p}.EndTimeResume][/LOWERCASE]"


def mins(p="ListItem"):
    return f"$INFO[{p}.Duration(mins)]{NBSP}$LOCALIZE[{S['min']}]"


# ================================================================ variables
def variables():
    v = []

    def var(name, values):
        v.append(f'\t<variable name="{name}">')
        for c, val in values:
            v.append(f'\t\t<value condition="{c}">{val}</value>' if c else f"\t\t<value>{val}</value>")
        v.append("\t</variable>")

    rt = "Integer.IsGreater(ListItem.Duration(mins),0)"
    var("VI_Art", [(f"{EP} + !String.IsEmpty(ListItem.Art(thumb))", "$INFO[ListItem.Art(thumb)]"),
                   ("!String.IsEmpty(ListItem.Art(fanart))", "$INFO[ListItem.Art(fanart)]"),
                   (None, "$INFO[ListItem.Art(tvshow.fanart)]")])
    var("VI_Poster", [("!String.IsEmpty(ListItem.Art(poster))", "$INFO[ListItem.Art(poster)]"),
                      ("!String.IsEmpty(ListItem.Art(tvshow.poster))", "$INFO[ListItem.Art(tvshow.poster)]"),
                      (None, "$INFO[ListItem.Art(thumb)]")])
    var("VI_Title", [(f"{SEASON} | String.IsEmpty(ListItem.Title)", "$INFO[ListItem.Label]"), (None, "$INFO[ListItem.Title]")])
    # set: "3 works · 1993-1994" (years from the set's own list, first and last by year)
    span = [(f"$EXP[VI_SetOK] + Integer.IsEqual(Container(9961).NumItems,{n})",
             f"$INFO[Container(9961).ListItemAbsolute(0).Year]–$INFO[Container(9961).ListItemAbsolute({n - 1}).Year]")
            for n in range(2, MAXSET + 1)]
    var("VI_SetSpan", span)
    var("VI_Byline", [
        (FILM, "$INFO[ListItem.Year]$INFO[ListItem.Director, · ,]"),
        (SHOW, "$INFO[ListItem.Year]$INFO[ListItem.Studio, · ,]"),
        (SEASON, "$INFO[ListItem.TVShowTitle]"),
        (EP, f"S$INFO[ListItem.Season]·E$INFO[ListItem.Episode]$INFO[ListItem.Premiered, · $LOCALIZE[{S['aired']}] ,]"),
        (f"{SET} + $EXP[VI_SetOK] + Integer.IsEqual(Container(9961).NumItems,1)", f"1 $LOCALIZE[{S['work']}]"),
        (f"{SET} + $EXP[VI_SetOK]", f"$INFO[Container(9961).NumItems] $LOCALIZE[{S['works_lc']}] · $VAR[VI_SetSpan]"),
        (None, "$INFO[ListItem.Year]$INFO[ListItem.Director, · ,]"),
    ])
    var("VI_Made", [(None, "$INFO[ListItem.Studio]$INFO[ListItem.Country, · ,]")])
    var("VI_Prem", [(EP, "$INFO[Container.ShowPlot]"),
                    (f"{SEASON} + String.IsEmpty(ListItem.Plot)", "$INFO[Container.ShowPlot]"),
                    ("!String.IsEmpty(ListItem.PlotOutline)", "$INFO[ListItem.PlotOutline]"), (None, "$INFO[ListItem.Plot]")])
    # "With A, B, C" from Kodi's cast list (ListItem.Cast is one string; the list gives names)
    var("VI_Cast1", [("!String.IsEmpty(Container(50).ListItemAbsolute(1).Label)", ", $INFO[Container(50).ListItemAbsolute(1).Label]")])
    var("VI_Cast2", [("!String.IsEmpty(Container(50).ListItemAbsolute(2).Label)", ", $INFO[Container(50).ListItemAbsolute(2).Label]")])
    var("VI_Cast", [(None, f"$LOCALIZE[{S['with_']}] $INFO[Container(50).ListItemAbsolute(0).Label]$VAR[VI_Cast1]$VAR[VI_Cast2]")])
    star = "$INFO[ListItem.Rating,★ , · ]"
    togo = lambda w: f"$INFO[ListItem.Property(UnWatchedEpisodes)]{NBSP}$LOCALIZE[{w}]"  # noqa: E731
    var("VI_State", [("Integer.IsGreater(ListItem.PlayCount,0)", f"$LOCALIZE[{S['Seen']}]"),
                     (PARTWAY, f"$LOCALIZE[{S['in_progress']}]"), (None, f"$LOCALIZE[{S['Unseen']}]")])
    var("VI_Status", [
        (f"[{SHOW} | {SEASON}] + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),1)", f"{star}1{NBSP}$LOCALIZE[{S['ep_to_go']}]"),
        (f"[{SHOW} | {SEASON}] + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0) + Integer.IsGreater(ListItem.Property(WatchedEpisodes),0)",
         f"{star}$LOCALIZE[{S['in_progress']}] · {togo(S['eps_to_go'])}"),
        (f"[{SHOW} | {SEASON}] + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)",
         f"{star}$LOCALIZE[{S['not_started']}] · {togo(S['eps_to_go'])}"),
        (f"{SHOW} | {SEASON}", f"{star}$LOCALIZE[{S['all_seen']}]"),
        (None, f"{star}$VAR[VI_State]"),
    ])
    # "3 of 3 in Three Colors Collection": the film's place in its set (by year) from list 9961
    pos = [(f"Integer.IsEqual(Container(9961).ListItemAbsolute({k}).DBID,ListItem.DBID)",
            f"{k + 1} $LOCALIZE[{S['of']}] $INFO[Container(9961).NumItems] $LOCALIZE[{S['in_']}] $INFO[ListItem.Set]")
           for k in range(MAXSET)]
    var("VI_Coll", [(None, f"$LOCALIZE[{S['part_of']}] $INFO[ListItem.Set]")])
    var("VI_CollPos", pos + [(None, "$VAR[VI_Coll]")])
    var("VI_Key", [
        (f"{SHOW} + $EXP[VI_NextOK] + Container(9960).ListItem.IsResumable", f"$VAR[VN_Left9960] · {ends('Container(9960).ListItem')}"),
        (f"{SHOW} + $EXP[VI_NextOK] + Integer.IsGreater(Container(9960).ListItem.Duration(mins),0)",
         f"{mins('Container(9960).ListItem')} · {ends('Container(9960).ListItem')}"),
        (f"{SHOW} + !$EXP[VI_NextOK] + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)", f"$LOCALIZE[{S['all_seen']}]"),
        (f"{SET} + Integer.IsGreater(ListItem.Property(Watched),0)",
         f"$INFO[ListItem.Property(Watched)] $LOCALIZE[{S['of']}] $INFO[ListItem.Property(Total)] $LOCALIZE[{S['seen']}]"),
        (SET, f"$LOCALIZE[{S['none_seen']}]"),
        (f"{PLAYABLE} + {rt} + {PARTWAY}", f"$VAR[VN_Left] · {ends()}"),
        (f"{PLAYABLE} + {rt}", f"{mins()} · {ends()}"),
    ])
    var("VI_Next", [(None, f"$LOCALIZE[{S['next']}] · S$INFO[Container(9960).ListItem.Season]·E$INFO[Container(9960).ListItem.Episode]"
                           f"$INFO[Container(9960).ListItem.Title, · ,]")])
    var("VI_BrowseLabel", [(SET, f"$LOCALIZE[{S['works']}]"), (None, f"$LOCALIZE[{S['episodes']}]")])
    var("VI_BrowseIcon", [(SET, "vn/icons/sets.png"), (None, "vn/icons/episodes.png")])
    var("VI_SetPath", [(SET, "videodb://movies/sets/$INFO[ListItem.DBID]/"), (None, "videodb://movies/sets/$INFO[ListItem.SetId]/")])
    var("VI_NextPath", [(None, "videodb://tvshows/titles/$INFO[ListItem.DBID]/-2/?xsp=%7B%22rules%22%3A%7B%22and%22%3A%5B%7B%22field%22%3A"
                               "%22playcount%22%2C%22operator%22%3A%22is%22%2C%22value%22%3A%5B%220%22%5D%7D%2C%7B%22field%22%3A%22season%22"
                               "%2C%22operator%22%3A%22greaterthan%22%2C%22value%22%3A%5B%220%22%5D%7D%5D%7D%2C%22type%22%3A%22episodes%22%7D")])
    var("VI_Fact1", [("!String.IsEmpty(ListItem.Director)", "$LOCALIZE[20339] · $INFO[ListItem.Director]")])
    var("VI_Fact2", [("!String.IsEmpty(ListItem.Writer)", "$LOCALIZE[20417] · $INFO[ListItem.Writer]")])
    var("VI_Fact3", [("!String.IsEmpty(ListItem.Country)", "$LOCALIZE[574] · $INFO[ListItem.Country]")])
    var("VI_Fact4", [("!String.IsEmpty(ListItem.Studio)", "$LOCALIZE[572] · $INFO[ListItem.Studio]")])
    return NL.join(v)


def expressions():
    return NL.join([
        f'\t<expression name="VI_NextOK">{NEXT_OK}</expression>',
        f'\t<expression name="VI_SetOK">{SET_OK}</expression>',
        f'\t<expression name="VI_Wide">{WIDE}</expression>',
        '\t<expression name="VI_More">ControlGroup(9940).HasFocus()</expression>',
    ])


# ================================================================ the work
def pool(x, y, w, h, scale):
    """The pool for a lit work (DESIGN 5): centre 3 % above the frame's centre; the art-coloured layer (helper)."""
    pw, ph = round(w * scale[0]), round(h * scale[1])
    px, py = x + w // 2 - pw // 2, y + h // 2 - round(0.03 * h) - ph // 2
    return img(px, py, pw, ph, "vn/spot.png", "$VAR[spot]", anims=["<include>VN_SpotSteps</include>"]) + NL + \
        "<include content=\"VN_ArtSpot\">" + "".join(f'<param name="{k}" value="{val}"/>' for k, val in
                                                    (("left", px), ("top", py), ("width", pw), ("height", ph))) + "</include>"


def work(fr, art, aspect="scale", scale=(1.55, 1.75)):
    x, y, w, h = fr
    a = MAT + 2
    return NL.join([
        pool(x, y, w, h, scale),
        img(x - 50, y - 42, w + 100, h + 104, "vn/shadow.png", "$VAR[shadow]", border="56", anims=["<include>VN_ShadowSteps</include>"]),
        img(x, y, w, h, "vn/white.png", "$VAR[frame]"),
        img(x + 2, y + 2, w - 4, h - 4, "vn/white.png", "$VAR[mat]"),
        img(x + a, y + a, w - 2 * a, h - 2 * a, art, aspect=aspect, background=True, fadetime=200),
        img(x + 2, y + 2, w - 4, h - 4, "vn/mat_falloff.png", vis=DARK),
    ])


# ================================================================ the placard
# One curator per kind (each has few runtime cases, so the solved conditions stay short), all 720 wide: with no
# fanart the poster frame + placard are centred instead of widening the card (one set of probes per kind).
PREM_ITEM = "[!String.IsEmpty(ListItem.PlotOutline) | !String.IsEmpty(ListItem.Plot)]"
CAST = "!String.IsEmpty(Container(50).ListItemAbsolute(0).Label)"
KINDS = {  # kind: (condition, probe base, fields)
    "film": (f"{PLAYABLE} + !{EP}", 9901, lambda: [
        PL.title("$VAR[VI_Title]", steps=PL.DISPLAY_STEPS), PL.byline("$VAR[VI_Byline]", gap=14),
        PL.line("genres", "$INFO[ListItem.Genre]", "top", gap=2, when="!String.IsEmpty(ListItem.Genre)"),
        PL.line("made", "$VAR[VI_Made]", "top", gap=2, when="[!String.IsEmpty(ListItem.Studio) | !String.IsEmpty(ListItem.Country)]"),
        PL.box("tagline", "$INFO[ListItem.Tagline]", "mid", "font_quote", 2, color="$VAR[ink]", probe=True,
               when="!String.IsEmpty(ListItem.Tagline)"),
        PL.box("premise", "$VAR[VI_Prem]", "mid", "font_small", 2, gap=12, grow=6, when=PREM_ITEM),
        PL.line("cast", "$VAR[VI_Cast]", "mid", gap=10, when=CAST),
        PL.flags("ListItem"), PL.line("status", "$VAR[VI_Status]", "bot", gap=14),
        PL.line("collection", "$VAR[VI_CollPos]", "bot", gap=4, when="!String.IsEmpty(ListItem.Set)"),
        PL.rule(), PL.keyline("$VAR[VI_Key]", gap=14), PL.custom("actions", "", ACT_H, gap=22)]),
    "show": (f"[{SHOW} | {SEASON}]", 9907, lambda: [
        PL.title("$VAR[VI_Title]", steps=PL.DISPLAY_STEPS), PL.byline("$VAR[VI_Byline]", gap=14),
        PL.line("genres", "$INFO[ListItem.Genre]", "top", gap=2, when="!String.IsEmpty(ListItem.Genre)"),
        PL.box("premise", "$VAR[VI_Prem]", "mid", "font_small", 2, grow=6,
               when="[!String.IsEmpty(ListItem.Plot) | !String.IsEmpty(Container.ShowPlot)]"),
        PL.line("cast", "$VAR[VI_Cast]", "mid", gap=10, when=CAST),
        PL.line("status", "$VAR[VI_Status]", "bot"), PL.rule(),
        PL.keyline("$VAR[VI_Next]", key="next", gap=14, when="$EXP[VI_NextOK]"),
        PL.keyline("$VAR[VI_Key]", gap=14), PL.custom("actions", "", ACT_H, gap=22)]),
    "episode": (EP, 9913, lambda: [
        PL.line("kicker", "$INFO[ListItem.TVShowTitle]", "top", font="font_body"),
        PL.title("$VAR[VI_Title]", steps=PL.DISPLAY_STEPS), PL.byline("$VAR[VI_Byline]", gap=14),
        PL.line("genres", "$INFO[ListItem.Director]", "top", gap=2, when="!String.IsEmpty(ListItem.Director)"),
        PL.box("premise", "$VAR[VI_Prem]", "mid", "font_small", 2, grow=6, when="!String.IsEmpty(Container.ShowPlot)"),
        PL.line("cast", "$VAR[VI_Cast]", "mid", gap=10, when=CAST),
        PL.flags("ListItem"), PL.line("status", "$VAR[VI_Status]", "bot", gap=14),
        PL.rule(), PL.keyline("$VAR[VI_Key]", gap=14), PL.custom("actions", "", ACT_H, gap=22)]),
    "set": (SET, 9919, lambda: [
        PL.title("$VAR[VI_Title]", steps=PL.DISPLAY_STEPS), PL.byline("$VAR[VI_Byline]", gap=14),
        PL.line("genres", "$INFO[ListItem.Genre]", "top", gap=2, when="!String.IsEmpty(ListItem.Genre)"),
        PL.box("premise", "$VAR[VI_Prem]", "mid", "font_small", 2, grow=8, when=PREM_ITEM),
        PL.rule(), PL.keyline("$VAR[VI_Key]", gap=14), PL.custom("actions", "", ACT_H, gap=22)]),
}
DROP = ["credit", "cast", "premise:3", "made", "collection", "premise:2", "tagline:1", "premise", "tagline", "flags", "genres"]
POSTER_DX = (1920 - (FR_P[2] + 40 + PL_W[2])) // 2 - FR_P[0]     # centre poster + placard on the wall


def placards():
    o = []
    for kind, (cond, base, fl) in KINDS.items():
        probes = dict(zip(("t44", "t36", "t30", "t2", "byline", "tagline"), range(base, base + 6)))
        o.append(PL.curator(fl(), *PL_W, PAD, probes, drop=DROP, vis=cond, cid=9900 if kind == "film" else None))
    return group(o, anims=[f'<animation effect="slide" start="0,0" end="{FR_P[0] + FR_P[2] + 40 + POSTER_DX - PL_W[0]},0" time="0" '
                           'condition="!$EXP[VI_Wide]">Conditional</animation>'])


# ================================================================ the action row
SLOTS = [  # id, face group, slot width (icon 48 + 14 + widest label + 36), icon, label, visible, clicks
    (9931, 9936, 168, "vn/icons/play.png", f"$LOCALIZE[{S['play']}]",
     # shows: shown at once when episodes are unseen (the next-episode list loads after onload picks the focus)
     f"[{PLAYABLE} + !{PARTWAY}] | [{SHOW} + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)]",
     [(f"{PLAYABLE}", "SendClick(8)"),
      ("$EXP[VI_NextOK]", "Dialog.Close(movieinformation,true)"),
      ("$EXP[VI_NextOK]", "PlayMedia($ESCINFO[Container(9960).ListItem.FileNameAndPath],resume)")]),
    (9932, 9937, 216, "vn/icons/resume.png", f"$LOCALIZE[{S['resume']}]", f"{PLAYABLE} + {PARTWAY}", [(None, "SendClick(9)")]),
    (9933, 9938, 233, "$VAR[VI_BrowseIcon]", "$VAR[VI_BrowseLabel]", FOLDER, [(None, "SendClick(8)")]),
    (9935, 9939, 203, "vn/icons/trailer.png", f"$LOCALIZE[{S['trailer']}]",
     f"{PLAYABLE} + !String.IsEmpty(ListItem.Trailer) + [!String.Contains(ListItem.Trailer,plugin.video.youtube) | System.HasAddon(plugin.video.youtube)]",
     [(None, "SendClick(11)")]),
    (9934, 9944, 168, "vn/icons/more.png", f"$LOCALIZE[{S['more']}]", None,
     [("Integer.IsGreater(Container(9941).NumPages,1)", "SetFocus(9942)"),
      ("!Integer.IsGreater(Container(9941).NumPages,1) + $EXP[VI_HasRows]", "SetFocus(9946)"),
      ("!Integer.IsGreater(Container(9941).NumPages,1) + !$EXP[VI_HasRows]", "SetFocus(50)")]),
]


def action_row(x, y, w, vis):
    """Icon slots with the label right of the focused icon (board 06), fixed widths (rule 5): a grouplist of
    invisible buttons, each followed by its face shifted back over it (zero net width, LESSONS Groove M3)."""
    kids = []
    for cid, gid, sw, icon, lab, v, clicks in SLOTS:
        clicks_xml = [f'\t<onclick condition="{c}">{a}</onclick>' if c else f"\t<onclick>{a}</onclick>" for c, a in clicks]
        btn = NL.join([f'<control type="button" id="{cid}">', f"\t<width>{sw}</width>", f"\t<height>{ACT_H}</height>",
                       "\t<label></label>", "\t<texturefocus />", "\t<texturenofocus />", *clicks_xml,
                       "\t<onup>noop</onup>",
                       '\t<ondown condition="Integer.IsGreater(Container(50).NumItems,0)">SetFocus(50)</ondown>',
                       '\t<ondown condition="!Integer.IsGreater(Container(50).NumItems,0)">SetFocus(9946)</ondown>',
                       *([f"\t<visible>{v}</visible>"] if v else []), "</control>"])
        face = NL.join([f'<control type="group" id="{gid}">', f"\t<left>-{sw}</left>", f"\t<width>{sw}</width>",
                        f"\t<height>{ACT_H}</height>", *([f"\t<visible>{v}</visible>"] if v else []),
                        '\t<include content="VN_IconFace">', f'\t\t<param name="id" value="{cid}"/>',
                        f'\t\t<param name="icon" value="{icon}"/>', f'\t\t<param name="label" value="{lab}"/>',
                        f'\t\t<param name="width" value="{sw - 62}"/>', f'\t\t<param name="height" value="{ACT_H}"/>',
                        '\t\t<param name="label_x" value="62"/>', "\t</include>", "</control>"])
        kids += [btn, face]
    return NL.join(['<control type="grouplist" id="9930">', f"\t<left>{x}</left>", f"\t<top>{y}</top>",
                    f"\t<width>{w}</width>", f"\t<height>{ACT_H}</height>", "\t<orientation>horizontal</orientation>",
                    "\t<itemgap>0</itemgap>", "\t<usecontrolcoords>true</usecontrolcoords>", "\t<onleft>noop</onleft>",
                    "\t<onright>noop</onright>", f"\t<visible>{vis}</visible>" if vis else "", ind(NL.join(kids), 1),
                    "</control>"])


def actions():
    """One row per placard variant would duplicate ids: the row is one control, moved for the poster variant."""
    x, y, w, h = PL_W
    ax, ay = x + PAD[1] + 1, y + h - PAD[0] - 1 - ACT_H
    row = action_row(ax, ay, w - 2 * PAD[1] - 2, None)
    dx = FR_P[0] + FR_P[2] + 40 + POSTER_DX - PL_W[0]
    return group([row], anims=[f'<animation effect="slide" start="0,0" end="{dx},0" time="0" condition="!$EXP[VI_Wide]">Conditional</animation>'])


# ================================================================ the More card
ROWS = [(9947, f"$LOCALIZE[{S['start']}]", f"{PLAYABLE} + {PARTWAY}", ["SendClick(8)"]),
        (9948, f"$LOCALIZE[{S['series']}]", "!String.IsEmpty(ListItem.SetId) + !String.IsEqual(ListItem.DBType,set)",
         ["Dialog.Close(all,true)", "ActivateWindow(Videos,videodb://movies/sets/$INFO[ListItem.SetId]/,return)"]),
        (9949, f"$LOCALIZE[{S['art']}]", "Control.IsEnabled(10)", ["SendClick(10)"]),
        (9945, f"$LOCALIZE[{S['refresh']}]", "Control.IsEnabled(6)", ["SendClick(6)"])]


def more_card():
    o = [img(0, 0, 1920, 1080, "vn/white.png", "$VAR[scrim_card]"),
         img(120, 160, 1680, 820, "vn/white.png", "$VAR[card]"),
         img(120, 160, 1680, 820, "vn/card_edge.png", "$VAR[card_edge]", border="4"),
         label(156, 176, 1000, 44, "$VAR[VI_Title]", "font_placard", "$VAR[ink]", aligny="center", selected=False),
         img(156, 228, "vn_rule_w", "vn_rule_h", "vn/white.png", "$VAR[placard_rule]")]
    # the plot: whole lines, the "..." fade on line 11 when it is longer (LESSONS Six Degrees 0.9.1)
    o.append(NL.join(['<control type="textbox" id="9941">', "\t<left>156</left>", "\t<top>248</top>", "\t<width>1000</width>",
                      f"\t<height>{11 * 41}</height>", "\t<font>font_body</font>", "\t<textcolor>$VAR[ink2]</textcolor>",
                      "\t<pagecontrol>9942</pagecontrol>", "\t<autoscroll>false</autoscroll>",
                      "\t<label>$INFO[ListItem.Plot]</label>", "</control>"]))
    more = "Integer.IsGreater(Container(9941).NumPages,1) + !Control.HasFocus(9942)"
    o.append(img(1006, 248 + 10 * 41, 150, 41, "vn/fade_h.png", "$VAR[card]", vis=more))
    o.append(label(1116, 248 + 10 * 41, 40, 41, "…", "font_body", "$VAR[ink2]", align="right", vis=more, selected=False))
    o.append(NL.join(['<control type="scrollbar" id="9942">', "\t<left>1172</left>", "\t<top>248</top>", "\t<width>4</width>",
                      f"\t<height>{11 * 41}</height>", '\t<texturesliderbackground colordiffuse="$VAR[rule]">vn/white.png</texturesliderbackground>',
                      '\t<texturesliderbar colordiffuse="$VAR[ink2]">vn/white.png</texturesliderbar>',
                      '\t<texturesliderbarfocus colordiffuse="$VAR[ink]">vn/white.png</texturesliderbarfocus>',
                      "\t<orientation>vertical</orientation>", "\t<showonepage>false</showonepage>",
                      "\t<onleft>noop</onleft>", '\t<onright condition="$EXP[VI_HasRows]">9946</onright>',
                      '\t<ondown condition="!$EXP[VI_HasRows]">50</ondown>', "\t<onback>9934</onback>", "</control>"]))
    # facts (in full: the placard's byline may cut the director)
    for i in range(4):
        o.append(label(1220, 248 + 38 * i, 544, 38, f"$VAR[VI_Fact{i + 1}]", "font_small", "$VAR[ink2]", aligny="center", selected=False))
    o.append(img(1220, 412, "vn_rule_w", "vn_rule_h", "vn/white.png", "$VAR[placard_rule]"))
    rows = []
    for cid, lab, vis, clicks in ROWS:
        rows.append(NL.join([f'<control type="button" id="{cid}">', "\t<width>544</width>", "\t<height>56</height>",
                             "\t<font>font_body</font>", "\t<textoffsetx>0</textoffsetx>", "\t<aligny>center</aligny>",
                             "\t<textcolor>$VAR[ink2]</textcolor>", "\t<focusedcolor>$VAR[ink]</focusedcolor>",
                             '\t<texturefocus border="0,0,0,3" colordiffuse="$VAR[ink]">vn/row_rule.png</texturefocus>',
                             "\t<texturenofocus />", f"\t<label>{lab}</label>", *[f"\t<onclick>{c}</onclick>" for c in clicks],
                             '\t<onleft condition="Integer.IsGreater(Container(9941).NumPages,1)">9942</onleft>',
                             "\t<onright>noop</onright>", "\t<onback>9934</onback>", f"\t<visible>{vis}</visible>", "</control>"]))
    o.append(NL.join(['<control type="grouplist" id="9946">', "\t<left>1220</left>", "\t<top>432</top>", "\t<width>544</width>",
                      "\t<height>240</height>", "\t<itemgap>4</itemgap>", "\t<onup>noop</onup>",
                      '\t<ondown condition="Integer.IsGreater(Container(50).NumItems,0)">50</ondown>',
                      '\t<ondown condition="!Integer.IsGreater(Container(50).NumItems,0)">noop</ondown>',
                      ind(NL.join(rows), 1), "</control>"]))
    o.append(cast_row())
    return group(o, cid=9940, anims=fade_cond("!$EXP[VI_More]", 200))


def cast_row():
    """Kodi's list 50: the cast (films, shows, episodes) or the set's works: 120 x 180 ghost prints, the focused one in
    colour in a 6 px mat (no helper prints exist for actors), its name and role under the row."""
    art = "$INFO[ListItem.Art(thumb)]"
    poster = "$INFO[ListItem.Art(poster)]"
    pic = lambda x, y, w, h, tint=None: NL.join([  # noqa: E731
        img(x, y, w, h, poster, tint, aspect="scale", background=True, vis="!String.IsEmpty(ListItem.Art(poster))"),
        img(x, y, w, h, art, tint, aspect="scale", background=True, vis="String.IsEmpty(ListItem.Art(poster))")])
    blank = lambda x, y, w, h: NL.join([  # noqa: E731
        twin_img(x, y, w, h, "vn/white.png", "card_edge", vis="String.IsEmpty(ListItem.Art(poster)) + String.IsEmpty(ListItem.Art(thumb))"),
        label(x + 6, y, w - 12, h, "$INFO[ListItem.Label]", "font_small", "$VAR[ink2]", align="center", aligny="center",
              wrap=True, vis="String.IsEmpty(ListItem.Art(poster)) + String.IsEmpty(ListItem.Art(thumb))")])
    item = NL.join([blank(10, 20, 120, 180), pic(10, 20, 120, 180, "eve_ghost_tint") .replace("<visible>", "<visible>$EXP[VN_Dark] + "),
                    pic(10, 20, 120, 180, "day_ghost_tint").replace("<visible>", "<visible>$EXP[VN_Day] + ")])
    hf = "Control.HasFocus(50)"
    lit = NL.join([twin_img(0, 10, 140, 200, "vn/white.png", "frame", vis=hf), twin_img(2, 12, 136, 196, "vn/white.png", "mat", vis=hf),
                   blank(10, 20, 120, 180), pic(10, 20, 120, 180).replace("<visible>", f"<visible>{hf} + "),
                   pic(10, 20, 120, 180, "eve_ghost_tint").replace("<visible>", f"<visible>!{hf} + $EXP[VN_Dark] + "),
                   pic(10, 20, 120, 180, "day_ghost_tint").replace("<visible>", f"<visible>!{hf} + $EXP[VN_Day] + ")])
    lst = NL.join(['<control type="fixedlist" id="50">', "\t<left>146</left>", "\t<top>700</top>", "\t<width>1628</width>",
                   "\t<height>220</height>", "\t<orientation>horizontal</orientation>", "\t<focusposition>0</focusposition>",
                   "\t<movement>8</movement>", "\t<onup>9946</onup>", "\t<ondown>noop</ondown>", "\t<onleft>noop</onleft>",
                   "\t<onright>noop</onright>", "\t<onback>9934</onback>", '\t<scrolltime tween="cubic" easing="out">200</scrolltime>',
                   "\t<preloaditems>1</preloaditems>",
                   f'\t<itemlayout width="148" height="220">{NL}{ind(item, 2)}{NL}\t</itemlayout>',
                   f'\t<focusedlayout width="148" height="220">{NL}{ind(lit, 2)}{NL}\t</focusedlayout>', "</control>"])
    name = label(156, 928, 1608, 38, "$INFO[Container(50).ListItem.Label]$INFO[Container(50).ListItem.Label2, · ,]",
                 "font_small", "$VAR[ink]", aligny="center", vis="Control.HasFocus(50)", selected=False)
    head = label(156, 660, 800, 38, f"$LOCALIZE[{S['cast']}]", "font_small", "$VAR[ink2]", aligny="center",
                 vis="Integer.IsGreater(Container(50).NumItems,0) + !String.IsEqual(ListItem.DBType,set)", selected=False)
    return NL.join([head, lst, name])


# ================================================================ data lists, Kodi's buttons
def data_lists():
    def dl(cid, path, vis, extra=""):
        return NL.join([f'<control type="list" id="{cid}">', "\t<left>0</left>", "\t<top>0</top>", "\t<width>1</width>",
                        "\t<height>1</height>", f"\t<visible>{vis}</visible>", '\t<itemlayout width="1" height="1" />',
                        '\t<focusedlayout width="1" height="1" />',
                        f'\t<content target="videos" browse="never" {extra}>{path}</content>', "</control>"])
    return NL.join([
        "<!-- a show's next unseen episode (season > 0, by episode; Omar's shows are flattened, LESSONS Fold) -->",
        dl(9960, "$VAR[VI_NextPath]", SHOW, 'sortby="episode" sortorder="ascending" limit="1"'),
        "<!-- the works of the set (by year): count, years, the film's place in it -->",
        dl(9961, "$VAR[VI_SetPath]", f"{SET} | !String.IsEmpty(ListItem.Set)", f'sortby="year" sortorder="ascending" limit="{MAXSET}"'),
    ] + [NL.join([f'<control type="button" id="{k}">', "\t<include>VN_Hidden</include>", "</control>"]) for k in (8, 9, 10, 11, 6)])


def first_focus():
    seen, o = [], []
    for cid, _g, _w, _i, _l, vis, _c in SLOTS:
        cond = join_and(f"[{vis}]" if vis else None, *[f"![{v}]" for v in seen])
        o.append(f'<onload condition="{cond}">SetFocus({cid})</onload>' if cond else f"<onload>SetFocus({cid})</onload>")
        if not vis:
            break
        seen.append(vis)
    return NL.join(o)


def main():
    PL.set_prefix("VI")
    stage = NL.join([
        group([work(FR, "$VAR[VI_Art]")], vis="$EXP[VI_Wide]"),
        group([work((FR_P[0] + POSTER_DX, *FR_P[1:]), "$VAR[VI_Poster]", scale=(2.05, 1.5))], vis="!$EXP[VI_Wide]"),
        placards(), actions(), "<include>VN_Clock</include>"])
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_info.py - edit the generator, then re-run. "The placard": DialogVideoInfo (film, series,
     season, episode, set), docs/skin.vernissage/screens/DialogVideoInfo_Placard.md + DESIGN 6 (board 06). -->
<includes>
	<expression name="VI_HasRows">[{ROWS[0][2]}] | [{ROWS[1][2]}] | Control.IsEnabled(10) | Control.IsEnabled(6)</expression>
{expressions()}
__PLACARD_EXPRS__
{variables()}

	<!-- the page: the work, its placard, the action row -->
	<include name="VidInfo_Stage">
{ind(stage, 2)}
	</include>

	<!-- the More card over the page (always processed, faded in while it has focus) -->
	<include name="VidInfo_MoreCard">
{ind(more_card(), 2)}
	</include>

	<!-- open on the first action of THIS item (a grouplist remembers the child used last, LESSONS Groove M3) -->
	<include name="VidInfo_FirstFocus">
{ind(first_focus(), 2)}
	</include>

	<!-- data lists and Kodi's own buttons (offscreen; ours click them) -->
	<include name="VidInfo_Data">
{ind(data_lists(), 2)}
	</include>
</includes>
"""
    body = body.replace("__PLACARD_EXPRS__", PL.expressions_xml(body))
    OUT.write_text(body, encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {body.count('<control')} controls, {len(body) // 1024} KB")


if __name__ == "__main__":
    main()
