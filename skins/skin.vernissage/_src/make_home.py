"""Generate 1080i/Includes_Home.xml: Vernissage's Home (M2).   python skins/skin.vernissage/_src/make_home.py

docs/skin.vernissage/screens/Home.md (ids, geometry, focus map), SPEC 6, boards 01 / 02 / 03.

Three rooms, each a whole wall (exhibition title, works, one lit work + its placard, the light), swapped with Up /
Down (300 ms fade, no slide), then the rail. All walls stay processed (faded with Conditional animations, LESSONS
Passe-partout: a hidden container never loads); only the current room takes focus.
  Tonight 9101   five unseen films that fit before midnight (Includes_Times.xml: the daily slice + the bucket)
  Easel   9110   the helper's easel list (feature `easel`), else the two-part wall 9111 films in progress + 9112
                 shows in progress (VN two-part rule below)
  New     9120   the helper's new list, else 9121 films added this week + 9122 episodes added this week, else 9123
                 recently added films
  Rail    9000   Films, Series, Music, Search, Settings (the rest control: Back from any wall lands here, no onback)
  Back office 9130 (Settings' OK), clean card 9131 ("No" first), update card 9132, Now playing card 9950.
Room state: Window(Home).Property(vn.room) = tonight | easel | new, set by each wall's onfocus; the shown room is the
property's room when it has works, else the first room with works (Home_ShowTonight / Easel / New). Parts of the
two-part walls: vn.easel.part = films | shows, vn.new.part = films | eps.

Two-part walls (no helper, SPEC 6.3): while part A has focus, part B hangs after A's visible works (r = works after
A's lit one that are still on screen; generated slides keyed on Container(A).ListItemNoWrap(k).Label, more parks B
off-screen). B's selected item keeps its wide focused slot even unfocused (LESSONS Passe-partout 0.9.2), so while B
is not the active part it draws its small print at the slot's right and the list slides left by the difference; B is
reset to its first work when it loses focus (Control.Move pair, LESSONS 0.9.4). While B is active, A fades out and B
hangs at x 120.

Helper New list (9120): Kodi picks a list's layout per container, not per item, so a list mixing films and episodes
can't hang films as posters and episodes as landscapes; 9120 hangs every work landscape (film fanart, show fanart) at
the easel's geometry (screens README 9 deviation #20). The two-part fallback keeps posters for films.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placard as PL  # noqa: E402
from vnxml import (spot, no_self, DARK, DAY, NBSP, NL, RM, card, fade_cond, group, img, ind, join_and, label, lit_layers,  # noqa: E402
                   print_layers, slide_cond, stack_label, stack_text, textbox, twin_img, x)

OUT = HERE.parent / "1080i" / "Includes_Home.xml"

# ---------------------------------------------------------------- ids
TONIGHT, EASEL_H, EASEL_F, EASEL_S, NEW_H, NEW_F, NEW_E, NEW_R = 9101, 9110, 9111, 9112, 9120, 9121, 9122, 9123
RAIL, OFFICE, CLEAN, UPDATE, NOWPLAYING = 9000, 9130, 9131, 9132, 9950
P_TONIGHT, P_EASEL, P_NEW_L, P_NEW_P = 9161, 9162, 9163, 9164
# placard probes (placard.curator): title at 44 / 36 / 30, the 2-line title box, byline, tagline; 6 ids per placard
PROBES = {cid: dict(zip(("t44", "t36", "t30", "t2", "byline", "tagline"), range(base, base + 6)))
          for cid, base in ((P_TONIGHT, 9170), (P_EASEL, 9176), (P_NEW_L, 9182), (P_NEW_P, 9188))}
# visible title boxes (their own NumPages = "longer than the cap") and probes (9151-9159)
T_TONIGHT, T_EASEL, T_NEW_L, T_NEW_P = 9151, 9152, 9153, 9154
PR_TONIGHT_KEY, PR_EASEL_TITLE, PR_NEWL_TITLE, PR_NEWP_KEY = 9155, 9156, 9157, 9158

# ---------------------------------------------------------------- geometry (screens/Home.md)
X0 = 120
# posters (Tonight, New films): prints 180 x 270 at item y 166, lit work 380 x 570 in a 14 px mat
P_Y = 226
P_PRINT_W, P_PRINT_H, P_PITCH, P_PRINT_Y = 150, 225, 186, 189    # board 01 (2026-10-21 revision)
P_FRAME_W, P_FRAME_H, P_MAT = 412, 602, 14
P_PLACARD_X, P_PLACARD_W = X0 + P_FRAME_W + 32, 504
P_LIT = P_FRAME_W + 32 + P_PLACARD_W + 40         # 988: frame, 32, placard 504, 40 to the next print
# landscapes (easel, New episodes): prints 360 x 203 at item y 95, lit work 640 x 360 in a 14 px mat
L_Y = 286                                        # board 03: the lit work 800 x 450 in a 14 px mat
L_PRINT_W, L_PRINT_H, L_PITCH, L_PRINT_Y = 360, 203, 404, 139
L_FRAME_W, L_FRAME_H, L_MAT = 832, 482, 14
L_PLACARD_X, L_PLACARD_W = X0 + L_FRAME_W + 32, 560   # 984
L_LIT = L_FRAME_W + 32 + L_PLACARD_W + 44         # 1468
L_TRACK_Y, L_CAP1_Y, L_CAP2_Y = L_PRINT_Y + L_PRINT_H + 12, L_PRINT_Y + L_PRINT_H + 26, L_PRINT_Y + L_PRINT_H + 62
L_H = max(L_FRAME_H, L_CAP2_Y + 38) + 4        # 486: the lit frame is the tallest thing in the row
L_SMALL_X = L_LIT - L_PITCH                      # inactive part B: its small print at the slot's right (724)
GLIDE = 200
# grey print paths are built with the layout (LESSONS 625): re-read them every 2 s, so a generation the helper
# publishes (or replaces) while a list is open reaches its prints (no reload: an unchanged path keeps its texture)
UPD = 'infoupdate="2000"'
N_TONIGHT = 5
RAIL_LIST_X, RAIL_LIST_Y, RAIL_PITCH, RAIL_H, ICON = 74, 922, 226, 140, 48

# ---------------------------------------------------------------- strings
S = dict(ends=31451, tonight=31452, today=31453, films_unseen=31454, film_unseen=31455, short_unseen=31456,
         easel=31457, new=31458, now_playing=31459, short_one=31465, works=31466, work=31467, last_first=31468,
         films=31469, film=31470, series_prog=31471, week=31472, recent=31473, next_ep=31474, in_prog=31475,
         eps_to_go=31476, ep_to_go=31477, new_eps=31478, new_ep=31479, new_week=31483, recent_cap=31484,
         room=31485, auto=31486, day=31487, evening=31488, clean_q=31489, clean_body=31490, update_q=31491,
         stop_video=31492, stop_music=31493, part_of=31495, last_ep=31499, in_prog_lc=31497, week_only=31498, min=31221)
COUNT_WORDS = {1: 31460, 2: 31461, 3: 31462, 4: 31463, 5: 31464}

H = "$EXP[HasKMEasel]"


def n_items(cid):
    return f"Container({cid}).NumItems"


def has(cid):
    return f"Integer.IsGreater(Container({cid}).NumItems,0)"


def empty(cid):
    return f"Integer.IsEqual(Container({cid}).NumItems,0)"


PROP = "Window(Home).Property(vn.room)"
EPART = "Window(Home).Property(vn.easel.part)"
NPART = "Window(Home).Property(vn.new.part)"

# ---------------------------------------------------------------- expressions (names; text below for timers)
EXPR = {
    "Home_HasTonight": has(TONIGHT),
    "Home_HasEasel": f"[{H} + {has(EASEL_H)}] | [!{H} + [{has(EASEL_F)} | {has(EASEL_S)}]]",
    "Home_HasNew": f"[{H} + {has(NEW_H)}] | [!{H} + [{has(NEW_F)} | {has(NEW_E)} | {has(NEW_R)}]]",
    # the room on show: vn.room's room when it has works, else the first room with works
    "Home_ShowTonight": f"$EXP[Home_HasTonight] + ![String.IsEqual({PROP},easel) + $EXP[Home_HasEasel]] + ![String.IsEqual({PROP},new) + $EXP[Home_HasNew]]",
    "Home_ShowEasel": f"$EXP[Home_HasEasel] + !$EXP[Home_ShowTonight] + ![String.IsEqual({PROP},new) + $EXP[Home_HasNew]]",
    "Home_ShowNew": f"$EXP[Home_HasNew] + !$EXP[Home_ShowTonight] + !$EXP[Home_ShowEasel]",
    # two-part walls: which part is active
    "Home_EaselS": f"!{H} + {has(EASEL_S)} + [String.IsEqual({EPART},shows) | {empty(EASEL_F)}]",
    "Home_EaselF": f"!{H} + {has(EASEL_F)} + ![String.IsEqual({EPART},shows) + {has(EASEL_S)}]",
    "Home_NewE": f"!{H} + {has(NEW_E)} + [String.IsEqual({NPART},eps) | {empty(NEW_F)}]",
    "Home_NewF": f"!{H} + {has(NEW_F)} + ![String.IsEqual({NPART},eps) + {has(NEW_E)}]",
    "Home_NewR": f"!{H} + {empty(NEW_F)} + {empty(NEW_E)} + {has(NEW_R)}",
    # the lit work's list has focus (pool up) / the New wall shows posters (9121 / 9123) or landscapes (9120 / 9122)
    "Home_NewPoster": f"$EXP[Home_NewF] | $EXP[Home_NewR]",
}

EASEL_SRC = [(H, f"Container({EASEL_H}).ListItem"), ("$EXP[Home_EaselS]", f"Container({EASEL_S}).ListItem"),
             ("$EXP[Home_EaselF]", f"Container({EASEL_F}).ListItem")]
NEWL_SRC = [(H, f"Container({NEW_H}).ListItem"), (f"!{H}", f"Container({NEW_E}).ListItem")]
NEWP_SRC = [("$EXP[Home_NewR]", f"Container({NEW_R}).ListItem"), ("!$EXP[Home_NewR]", f"Container({NEW_F}).ListItem")]

# Focus targets per room: (condition, id), the first match wins (numeric navigation, LESSONS Orbit 0.9.2)
EASEL_TARGETS = [(H, EASEL_H), ("$EXP[Home_EaselS]", EASEL_S), ("$EXP[Home_EaselF]", EASEL_F)]
NEW_TARGETS = [(H, NEW_H), ("$EXP[Home_NewE]", NEW_E), ("$EXP[Home_NewF]", NEW_F), ("$EXP[Home_NewR]", NEW_R)]


def nav(tag_name, targets, default=None):
    o = [f'<{tag_name} condition="{c}">{t}</{tag_name}>' for c, t in targets]
    if default is not None:
        o.append(f"<{tag_name}>{default}</{tag_name}>")
    return o


def down_from(room):
    if room == "tonight":
        return (nav("ondown", [(f"$EXP[Home_HasEasel] + {c}", t) for c, t in EASEL_TARGETS])
                + nav("ondown", [(f"!$EXP[Home_HasEasel] + $EXP[Home_HasNew] + {c}", t) for c, t in NEW_TARGETS], RAIL))
    if room == "easel":
        return nav("ondown", [(f"$EXP[Home_HasNew] + {c}", t) for c, t in NEW_TARGETS], RAIL)
    return [f"<ondown>{RAIL}</ondown>"]


def up_from(room):
    audio = [("Player.HasAudio", NOWPLAYING)]
    if room == "tonight":
        return nav("onup", audio)
    if room == "easel":
        return nav("onup", [("$EXP[Home_HasTonight]", TONIGHT)] + audio)
    return (nav("onup", [(f"$EXP[Home_HasEasel] + {c}", t) for c, t in EASEL_TARGETS])
            + nav("onup", [("$EXP[Home_HasTonight]", TONIGHT)] + audio))


def to_room():
    """Up from the rail / the back office: the room on show."""
    return (nav("onup", [("$EXP[Home_ShowTonight]", TONIGHT)])
            + nav("onup", [(f"$EXP[Home_ShowEasel] + {c}", t) for c, t in EASEL_TARGETS])
            + nav("onup", [(f"$EXP[Home_ShowNew] + {c}", t) for c, t in NEW_TARGETS]))


def nav_np():
    o = [f"<onup>{NOWPLAYING}</onup>"]
    o += nav("ondown", [("$EXP[Home_HasTonight]", TONIGHT)])
    o += nav("ondown", [(f"$EXP[Home_HasEasel] + {c}", t) for c, t in EASEL_TARGETS])
    o += nav("ondown", [(f"$EXP[Home_HasNew] + {c}", t) for c, t in NEW_TARGETS], RAIL)
    o.append(f"<onback>{RAIL}</onback>")
    return o


def onfocus(room, part=None):
    o = [f"<onfocus>SetProperty(vn.room,{room},home)</onfocus>"]
    if part:
        o.append(f"<onfocus>SetProperty({part[0]},{part[1]},home)</onfocus>")
    return o


def reset_on_unfocus(cid):
    return [f"<onunfocus>Control.Move({cid},-$INFO[Container({cid}).CurrentItem])</onunfocus>",
            f"<onunfocus>Control.Move({cid},1)</onunfocus>"]


def li(cid):
    return f"Container({cid}).ListItem"


def ends(prefix):
    """"ends 11:19 pm": the end from the resume point when there is one (region clock, lowercase)."""
    return (f"$LOCALIZE[{S['ends']}]{NBSP}[LOWERCASE]$INFO[{prefix}.EndTimeResume][/LOWERCASE]")


def mins(prefix):
    return f"$INFO[{prefix}.Duration(mins)]{NBSP}$LOCALIZE[{S['min']}]"


# ================================================================ layouts
def poster_layouts(cid, when_big=None):
    """Tonight / New film walls: itemlayout 216 (print at y 166), focusedlayout 868 (the lit work)."""
    greys = [("movie_poster/$INFO[ListItem.DBID].jpg", "true")]
    item = print_layers(0, P_PRINT_Y, P_PRINT_W, P_PRINT_H, "$INFO[ListItem.Art(poster)]", greys)
    lit = lit_layers(0, 0, P_FRAME_W, P_FRAME_H, P_MAT, "$INFO[ListItem.Art(poster)]",
                     grey=print_layers(P_MAT + 2, P_MAT + 2, P_FRAME_W - 2 * P_MAT - 4, P_FRAME_H - 2 * P_MAT - 4,
                                       "$INFO[ListItem.Art(poster)]", greys))
    return (f'<itemlayout {UPD} width="{P_PITCH}" height="{P_FRAME_H}">{NL}{ind(item, 1)}{NL}</itemlayout>{NL}'
            f'<focusedlayout {UPD} width="{P_LIT}" height="{P_FRAME_H}">{NL}{ind(lit, 1)}{NL}</focusedlayout>')


def land_art(kind):
    """Colour art for a landscape card: show fanart for episodes (else landscape, else the thumb), film fanart."""
    if kind == "show":
        return "$INFO[ListItem.Art(fanart)]"
    return "$VAR[Home_LandArt]"


def land_greys(kind):
    if kind == "helper":
        return [("movie_fanart/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,movie)"),
                ("tvshow_fanart/$INFO[ListItem.Property(KarmaMole.TvShowDBID)].jpg", "String.IsEqual(ListItem.DBType,episode)")]
    if kind == "film":
        return [("movie_fanart/$INFO[ListItem.DBID].jpg", "true")]
    if kind == "show":
        return [("tvshow_fanart/$INFO[ListItem.DBID].jpg", "true")]
    return [("tvshow_fanart/$INFO[ListItem.TvShowDBID].jpg", "true")]           # library episodes


def captions(x0, kind, when=None):
    """Under a landscape print: the title (show name for episodes) and the time left / what's next."""
    cap1 = "$VAR[Home_CapTitle]"
    cap2 = {"helper": "$VAR[Home_CapHelper]", "film": "$VAR[VN_Left]", "show": "$VAR[Home_CapShow]",
            "ep": "$VAR[Home_CapEp]"}[kind]
    o = [label(x0, L_CAP1_Y, L_PRINT_W, 38, cap1, "font_small", "$VAR[ink2]", aligny="center", vis=when),
         label(x0, L_CAP2_Y, L_PRINT_W, 38, cap2, "font_small", "$VAR[ink2]", aligny="center", vis=when)]
    if kind in ("helper", "film"):
        # the 3 px progress track under the print: the track (rule) and the fill (ink2) as room twins
        started = join_and("Integer.IsGreater(ListItem.PercentPlayed,0)", when)
        o.append(twin_img(x0, L_TRACK_Y, L_PRINT_W, 3, "vn/white.png", "rule", vis=started))
        for room, gate in (("day", DAY), ("eve", DARK)):
            o.append(f"""<control type="progress">
	<left>{x0}</left>
	<top>{L_TRACK_Y}</top>
	<width>{L_PRINT_W}</width>
	<height>3</height>
	<info>ListItem.PercentPlayed</info>
	<texturebg>vn/clear.png</texturebg>
	<midtexture colordiffuse="{room}_ink2">vn/white.png</midtexture>
	<visible>{join_and(started, gate)}</visible>
</control>""")
    return NL.join(o)


def land_layouts(cid, kind, inactive_small=None):
    """Easel / New landscapes: itemlayout 404 (print at y 95 + captions), focusedlayout 1128 (the lit work).
    inactive_small = condition under which the selected item draws its SMALL print at the slot's right (part B)."""
    art, greys = land_art(kind), land_greys(kind)
    item = NL.join([print_layers(0, L_PRINT_Y, L_PRINT_W, L_PRINT_H, art, greys), captions(0, kind)])
    big = f"![{inactive_small}]" if inactive_small else None
    lit = lit_layers(0, 0, L_FRAME_W, L_FRAME_H, L_MAT, art, when=big,
                     grey=print_layers(L_MAT + 2, L_MAT + 2, L_FRAME_W - 2 * L_MAT - 4, L_FRAME_H - 2 * L_MAT - 4,
                                       art, greys, when=big))
    if inactive_small:
        lit += NL + print_layers(L_SMALL_X, L_PRINT_Y, L_PRINT_W, L_PRINT_H, art, greys, when=inactive_small)
        lit += NL + captions(L_SMALL_X, kind, when=inactive_small)
    return (f'<itemlayout {UPD} width="{L_PITCH}" height="{L_H}">{NL}{ind(item, 1)}{NL}</itemlayout>{NL}'
            f'<focusedlayout {UPD} width="{L_LIT}" height="{L_H}">{NL}{ind(lit, 1)}{NL}</focusedlayout>')


# ================================================================ lists
def wall_list(cid, kind, left, top, width, height, content, ups, downs, lefts, rights, focus, extra=(), vis=None,
              anims=None, layouts=""):
    body = [f"<left>{left}</left>", f"<top>{top}</top>", f"<width>{width}</width>", f"<height>{height}</height>",
            "<orientation>horizontal</orientation>"]
    if kind == "fixed":
        body += ["<focusposition>0</focusposition>", "<movement>0</movement>", "<include>Anim_ScrollRow</include>"]
    else:
        body.append("<scrolltime>0</scrolltime>")
    if vis:
        body.append(f"<visible>{vis}</visible>")
    body += anims or []
    body += ups + downs + lefts + rights
    body.append(f"<onback>{RAIL}</onback>")
    body += focus
    body += list(extra)
    body.append(layouts)
    body.append(content)
    return f'<control type="{"fixedlist" if kind == "fixed" else "list"}" id="{cid}">{NL}' + NL.join(
        ind(b, 1) for b in body if b) + f"{NL}</control>"


def content(path, sortby=None, order="descending", limit=None, target="videos"):
    a = [f'target="{target}"']
    if sortby:
        a.append(f'sortby="{sortby}" sortorder="{order}"')
    if limit:
        a.append(f'limit="{limit}"')
    a.append('browse="never"')
    note = (" <!-- kdk-ignore: xml-validation; &rev= is KarmaMole.Easel.Rev, a revision number the helper publishes"
            " (no encoding needed; KARMAMOLE_HELPER_API 10.3) -->") if path.startswith("plugin://") else ""
    return f'<content {" ".join(a)}>{x(path)}</content>{note}'


def xsp(base, rules, typ):
    import json
    import urllib.parse
    q = urllib.parse.quote(json.dumps({"rules": {"and": rules}, "type": typ}, separators=(",", ":")), safe="")
    return f"{base}?xsp={q}"


def R(f, o, v):
    return {"field": f, "operator": o, "value": v}


PATH_FILMS_PROG = xsp("videodb://movies/titles/", [R("inprogress", "true", [""])], "movies")
PATH_FILMS_WEEK = xsp("videodb://movies/titles/", [R("dateadded", "inthelast", ["7 days"])], "movies")
PATH_EPS_WEEK = xsp("videodb://tvshows/titles/-1/-1/-1/-1/", [R("dateadded", "inthelast", ["7 days"])], "episodes")
PATH_HELPER_EASEL = "plugin://script.karmamole.helper/?info=easel&limit=24&rev=$INFO[Window(Home).Property(KarmaMole.Easel.Rev)]"
PATH_HELPER_NEW = "plugin://script.karmamole.helper/?info=new&days=7&limit=24&rev=$INFO[Window(Home).Property(KarmaMole.Easel.Rev)]"


def two_part_slides(a, b, a_lit, a_pitch, b_inactive, max_r):
    """Part B's placement while it is not active: after part A's works still on screen (r = 0..max_r), else parked."""
    o = []
    base = X0 + L_SMALL_X                     # where B's small print sits with no slide (list at x 120)
    for r in range(max_r + 1):
        conds = [f"!String.IsEmpty(Container({a}).ListItemNoWrap({k}).Label)" for k in range(1, r + 1)]
        conds.append(f"String.IsEmpty(Container({a}).ListItemNoWrap({r + 1}).Label)")
        target = X0 + a_lit + a_pitch * r
        o += slide_cond(join_and(b_inactive, *conds), target - base)
    o += slide_cond(join_and(b_inactive, f"!String.IsEmpty(Container({a}).ListItemNoWrap({max_r + 1}).Label)"), 1920)
    return o


# ================================================================ placards (window level, placard.curator: DESIGN 6)
def src_when(sources, fmt):
    """[(source condition, prefix)] -> a condition that holds when the active source's field is set."""
    return " | ".join(f"[{join_and(c, fmt.format(p=p))}]" for c, p in sources)


def film_card(cid, pv, sources, x, y, slides=None, vis=None):
    """Home poster placard (504 x 598): title / byline / genres; tagline / premise; flags, status, collection, rule,
    runtime · ends."""
    fields = [PL.title(f"$VAR[{pv}Title]"), PL.byline(f"$VAR[{pv}L2]"),
              PL.line("genres", f"$VAR[{pv}Genre]", "top", when=src_when(sources, "!String.IsEmpty({p}.Genre)")),
              PL.box("tagline", f"$VAR[{pv}Tag]", "mid", "font_quote", 2, color="$VAR[ink]", probe=True,
                     when=src_when(sources, "!String.IsEmpty({p}.Tagline)")),
              PL.box("premise", f"$VAR[{pv}Prem]", "mid", "font_small", 2, gap=12, grow=3,
                     when=src_when(sources, "[!String.IsEmpty({p}.PlotOutline) | !String.IsEmpty({p}.Plot)]")),
              PL.flags(list(sources)),
              PL.line("status", f"$VAR[{pv}Status]", "bot", gap=14),
              PL.line("collection", f"$VAR[{pv}Coll]", "bot", gap=4, when=src_when(sources, "!String.IsEmpty({p}.Set)")),
              PL.rule(), PL.keyline(f"$VAR[{pv}Key]")]
    return PL.curator(fields, x, y, P_PLACARD_W, P_FRAME_H - 4, (28, 30), PROBES[cid], vis=vis, anims=slides, cid=cid)


PREM_WHEN = {}   # land_vars() fills it (variables() runs before the rooms are built)


def land_card(cid, pv, sources, progress, vis=None):
    """Easel / New landscape placard (560 x 478): show / S-E · episode / network · year · rating; premise; flags,
    episodes left, progress, time left · ends."""
    fields = [PL.title(f"$VAR[{pv}Title]"), PL.byline(f"$VAR[{pv}L2]"),
              PL.line("genres", f"$VAR[{pv}Facts]", "top"),
              PL.box("premise", f"$VAR[{pv}Prem]", "mid", "font_small", 2, grow=3, when=PREM_WHEN[pv]),
              PL.flags(list(sources)),
              PL.line("state", f"$VAR[{pv}State]", "bot", gap=14),
              PL.progress(progress, gap=16), PL.keyline(f"$VAR[{pv}Key]", gap=14)]
    return PL.curator(fields, L_PLACARD_X, L_Y + 2, L_PLACARD_W, L_FRAME_H - 4, (28, 30), PROBES[cid], vis=vis, cid=cid)


# ================================================================ the rooms
def tonight_slides(glide):
    o = []
    for p in range(1, N_TONIGHT):
        o += slide_cond(f"Integer.IsEqual(Container({TONIGHT}).Position,{p})", P_PITCH * p, 0, glide)
    return o


def room_tonight():
    hf = f"Control.HasFocus({TONIGHT})"
    lst = wall_list(
        TONIGHT, "list", X0, P_Y, 1700, P_FRAME_H,
        content("$VAR[Home_TonightPath]", "rating", "descending", N_TONIGHT),
        up_from("tonight"), down_from("tonight"), [f"<onleft>{TONIGHT}</onleft>"], [f"<onright>{TONIGHT}</onright>"],
        onfocus("tonight"), extra=["<onclick>Action(Info)</onclick>"], layouts=poster_layouts(TONIGHT))
    placard = film_card(P_TONIGHT, "Home_T", [(None, li(TONIGHT))], P_PLACARD_X, P_Y + 2, slides=tonight_slides(0),
                        vis=has(TONIGHT))
    title = f"""<control type="grouplist">
	<left>116</left>
	<top>70</top>
	<width>1440</width>
	<height>66</height>
	<orientation>horizontal</orientation>
	<itemgap>0</itemgap>
	<visible>{has(TONIGHT)}</visible>
{ind(label(None, None, None, 66, "$VAR[Home_TonightLead]", "font_exhibit_it", "$VAR[ink]", width_auto_max=400, selected=False), 1)}
{ind(label(None, None, None, 66, "$VAR[Home_TonightTitle]", "font_exhibit", "$VAR[ink]", width_auto_max=1100, selected=False), 1)}
</control>"""
    # the light: the pool glides between the five slots, the shadow jumps
    slides = tonight_slides(GLIDE)
    pool_w, pool_h = round(P_FRAME_W * 2.05), round(P_FRAME_H * 1.5)
    pool_x = X0 + P_FRAME_W // 2 - pool_w // 2
    pool_y = P_Y + P_FRAME_H // 2 - round(0.03 * P_FRAME_H) - pool_h // 2
    lt = group([
        group([img(X0 - 50, P_Y - 42, P_FRAME_W + 100, P_FRAME_H + 104, "vn/shadow.png", "$VAR[shadow]", border="56",
                   anims=["<include>VN_ShadowSteps</include>"])], anims=tonight_slides(0)),
        group([spot(pool_x, pool_y, pool_w, pool_h)],
              anims=slides + fade_cond(f"!{hf}", 200)),
    ], vis=has(TONIGHT))
    return group([lt, lst, placard, title], anims=fade_cond("!$EXP[Home_ShowTonight]"))


def land_light(focus_cond, vis=None):
    fx, fy = X0, L_Y
    pool_w, pool_h = round(L_FRAME_W * 2.05), round(L_FRAME_H * 1.5)
    pool_x = fx + L_FRAME_W // 2 - pool_w // 2
    pool_y = fy + L_FRAME_H // 2 - round(0.03 * L_FRAME_H) - pool_h // 2
    return group([
        img(fx - 50, fy - 42, L_FRAME_W + 100, L_FRAME_H + 104, "vn/shadow.png", "$VAR[shadow]", border="56",
            anims=["<include>VN_ShadowSteps</include>"]),
        group([spot(pool_x, pool_y, pool_w, pool_h)],
              anims=fade_cond(f"![{focus_cond}]", 200)),
    ], vis=vis)


def poster_light(focus_cond, vis=None):
    pool_w, pool_h = round(P_FRAME_W * 2.05), round(P_FRAME_H * 1.5)
    pool_x = X0 + P_FRAME_W // 2 - pool_w // 2
    pool_y = P_Y + P_FRAME_H // 2 - round(0.03 * P_FRAME_H) - pool_h // 2
    return group([
        img(X0 - 50, P_Y - 42, P_FRAME_W + 100, P_FRAME_H + 104, "vn/shadow.png", "$VAR[shadow]", border="56",
            anims=["<include>VN_ShadowSteps</include>"]),
        group([spot(pool_x, pool_y, pool_w, pool_h)],
              anims=fade_cond(f"![{focus_cond}]", 200)),
    ], vis=vis)


def room_title(text_label, sub_var, vis):
    return group([
        label(116, 70, 1440, 66, text_label, "font_exhibit", "$VAR[ink]", selected=False),
        label(X0, 150, 1300, 41, f"$VAR[{sub_var}]", "font_body", "$VAR[ink2]", selected=False),
    ], vis=vis)


def room_easel():
    lists = []
    common_lr = lambda cid: ([f"<onleft>{cid}</onleft>"], [f"<onright>{cid}</onright>"])  # noqa: E731
    # helper list
    l, r = common_lr(EASEL_H)
    lists.append(wall_list(
        EASEL_H, "fixed", X0, L_Y, 1800, L_H, content("$VAR[Home_EaselHelperPath]", target="videos"),
        up_from("easel"), down_from("easel"), l, r, onfocus("easel"),
        extra=[f"<onclick>PlayMedia($ESCINFO[ListItem.Property(file)],resume)</onclick>"],
        vis=H, layouts=land_layouts(EASEL_H, "helper")))
    # films in progress (part A)
    a_active = "$EXP[Home_EaselF]"
    lists.append(wall_list(
        EASEL_F, "fixed", X0, L_Y, 1800, L_H, content(PATH_FILMS_PROG, "lastplayed", "descending", 12),
        up_from("easel"), down_from("easel"), [f"<onleft>{EASEL_F}</onleft>"],
        [f'<onright condition="{has(EASEL_S)}">{EASEL_S}</onright>', f"<onright>{EASEL_F}</onright>"],
        onfocus("easel", ("vn.easel.part", "films")),
        extra=["<onclick>PlayMedia($ESCINFO[ListItem.FileNameAndPath],resume)</onclick>"],
        vis=f"!{H}", anims=fade_cond(f"!{a_active}", 150), layouts=land_layouts(EASEL_F, "film")))
    # shows in progress (part B)
    b_inactive = "!$EXP[Home_EaselS]"
    lists.append(wall_list(
        EASEL_S, "fixed", X0, L_Y, 1800, L_H, content("videodb://inprogresstvshows/", "lastplayed", "descending", 12),
        up_from("easel"), down_from("easel"),
        [f'<onleft condition="{has(EASEL_F)}">{EASEL_F}</onleft>', f"<onleft>{EASEL_S}</onleft>"],
        [f"<onright>{EASEL_S}</onright>"],
        onfocus("easel", ("vn.easel.part", "shows")), extra=reset_on_unfocus(EASEL_S),
        vis=f"!{H}", anims=two_part_slides(EASEL_F, EASEL_S, L_LIT, L_PITCH, b_inactive, 1),
        layouts=land_layouts(EASEL_S, "show", inactive_small=b_inactive)))
    # Right from 9111's last work moves to 9112; its first work then sits where it hung (no jump): fine at 200 ms
    placard = land_card(P_EASEL, "Home_E", EASEL_SRC, [
        (f"{H} + !String.IsEqual({li(EASEL_H)}.Property(KarmaMole.Next),true) + Integer.IsGreater({li(EASEL_H)}.PercentPlayed,0)", li(EASEL_H)),
        (f"$EXP[Home_EaselF] + Integer.IsGreater({li(EASEL_F)}.PercentPlayed,0)", li(EASEL_F))], vis="$EXP[Home_HasEasel]")
    focus = f"Control.HasFocus({EASEL_H}) | Control.HasFocus({EASEL_F}) | Control.HasFocus({EASEL_S})"
    return group([land_light(focus, vis="$EXP[Home_HasEasel]"), *lists, placard,
                  room_title(f"$LOCALIZE[{S['easel']}]", "Home_EaselSub", "$EXP[Home_HasEasel]")],
                 anims=fade_cond("!$EXP[Home_ShowEasel]"))


def room_new():
    lists = []
    lists.append(wall_list(
        NEW_H, "fixed", X0, L_Y, 1800, L_H, content("$VAR[Home_NewHelperPath]", target="videos"),
        up_from("new"), down_from("new"), [f"<onleft>{NEW_H}</onleft>"], [f"<onright>{NEW_H}</onright>"],
        onfocus("new"), extra=["<onclick>Action(Info)</onclick>"], vis=H, layouts=land_layouts(NEW_H, "helper")))
    lists.append(wall_list(
        NEW_F, "fixed", X0, P_Y, 1800, P_FRAME_H, content(PATH_FILMS_WEEK, "dateadded", "descending", 12),
        up_from("new"), down_from("new"), [f"<onleft>{NEW_F}</onleft>"],
        [f'<onright condition="{has(NEW_E)}">{NEW_E}</onright>', f"<onright>{NEW_F}</onright>"],
        onfocus("new", ("vn.new.part", "films")), extra=["<onclick>Action(Info)</onclick>"],
        vis=f"!{H}", anims=fade_cond("!$EXP[Home_NewF]", 150), layouts=poster_layouts(NEW_F)))
    b_inactive = "!$EXP[Home_NewE]"
    lists.append(wall_list(
        NEW_E, "fixed", X0, L_Y, 1800, L_H, content(PATH_EPS_WEEK, "dateadded", "descending", 12),
        up_from("new"), down_from("new"),
        [f'<onleft condition="{has(NEW_F)}">{NEW_F}</onleft>', f"<onleft>{NEW_E}</onleft>"],
        [f"<onright>{NEW_E}</onright>"],
        onfocus("new", ("vn.new.part", "eps")), extra=["<onclick>Action(Info)</onclick>"] + reset_on_unfocus(NEW_E),
        vis=f"!{H}", anims=two_part_slides(NEW_F, NEW_E, P_LIT, P_PITCH, b_inactive, 3),
        layouts=land_layouts(NEW_E, "ep", inactive_small=b_inactive)))
    lists.append(wall_list(
        NEW_R, "fixed", X0, P_Y, 1800, P_FRAME_H, content("videodb://recentlyaddedmovies/", limit=12),
        up_from("new"), down_from("new"), [f"<onleft>{NEW_R}</onleft>"], [f"<onright>{NEW_R}</onright>"],
        onfocus("new"), extra=["<onclick>Action(Info)</onclick>"],
        vis=f"!{H}", anims=fade_cond("!$EXP[Home_NewR]", 150), layouts=poster_layouts(NEW_R)))
    pl = land_card(P_NEW_L, "Home_N", NEWL_SRC, [
        (f"{H} + Integer.IsGreater({li(NEW_H)}.PercentPlayed,0)", li(NEW_H))], vis="$EXP[Home_HasNew] + !$EXP[Home_NewPoster]")
    pp = film_card(P_NEW_P, "Home_NP", NEWP_SRC, P_PLACARD_X, P_Y + 2, vis="$EXP[Home_HasNew] + $EXP[Home_NewPoster]")
    focus = " | ".join(f"Control.HasFocus({c})" for c in (NEW_H, NEW_F, NEW_E, NEW_R))
    return group([land_light(focus, vis="$EXP[Home_HasNew] + !$EXP[Home_NewPoster]"),
                  poster_light(focus, vis="$EXP[Home_HasNew] + $EXP[Home_NewPoster]"),
                  *lists, pl, pp, room_title(f"$LOCALIZE[{S['new']}]", "Home_NewSub", "$EXP[Home_HasNew]")],
                 anims=fade_cond("!$EXP[Home_ShowNew]"))


def hint():
    to_e = "$EXP[Home_ShowTonight] + $EXP[Home_HasEasel]"
    to_n = "[$EXP[Home_ShowTonight] + !$EXP[Home_HasEasel] + $EXP[Home_HasNew]] | [$EXP[Home_ShowEasel] + $EXP[Home_HasNew]]"
    return group([
        label(952, 980, 800, 41, f"$LOCALIZE[{S['easel']}]", "font_body", "$VAR[ink2]", align="right", vis=to_e, selected=False),
        label(952, 980, 800, 41, f"$LOCALIZE[{S['new']}]", "font_body", "$VAR[ink2]", align="right", vis=to_n, selected=False),
        img(1756, 976, 44, 44, "vn/icons/down.png", "$VAR[ink2]", vis=f"[{to_e}] | {to_n}"),
    ])


# ================================================================ variables
def variables():
    v = []

    def var(name, values):
        v.append(f'\t<variable name="{name}">')
        for c, val in values:
            v.append(f'\t\t<value condition="{c}">{val}</value>' if c else f"\t\t<value>{val}</value>")
        v.append("\t</variable>")

    # the helper's lists ask the plug-in only while its easel feature runs: an unguarded path reloaded when the helper
    # stopped (the revision cleared) and logged "Unable to find plugin" (device audit M5; also every Home load
    # without the helper). Empty = no request; the two-part walls take over.
    note = (" <!-- kdk-ignore: xml-validation; &rev= is KarmaMole.Easel.Rev, a revision number the helper publishes"
            " (no encoding needed; KARMAMOLE_HELPER_API 10.3) -->")
    var("Home_EaselHelperPath", [("$EXP[HasKMEasel]", x(PATH_HELPER_EASEL))])
    v[-2] += note
    var("Home_NewHelperPath", [("$EXP[HasKMEasel]", x(PATH_HELPER_NEW))])
    v[-2] += note
    t = li(TONIGHT)
    n = n_items(TONIGHT)
    var("Home_TonightLead", [("$EXP[VN_Day]", f"$LOCALIZE[{S['today']}]"), (None, f"$LOCALIZE[{S['tonight']}]")])
    vals = []
    for k in range(1, N_TONIGHT + 1):
        one = k == 1
        vals.append((f"Integer.IsEqual({n},{k}) + $EXP[Home_TonightShort]",
                     f": $LOCALIZE[{COUNT_WORDS[k]}] $LOCALIZE[{S['short_one'] if one else S['short_unseen']}]"))
        vals.append((f"Integer.IsEqual({n},{k})", f": $LOCALIZE[{COUNT_WORDS[k]}] $LOCALIZE[{S['film_unseen'] if one else S['films_unseen']}]"))
    vals.append((None, f": $LOCALIZE[{S['films_unseen']}]"))
    var("Home_TonightTitle", vals)

    # ---- placard fields (DESIGN 6). One set of variables per placard; several sources pick by condition.
    def star(p):
        return f"$INFO[{p}.Rating,★ , · ]"

    def keyline(p, resumable=True):
        rt = f"Integer.IsGreater({p}.Duration(mins),0)"
        vals = []
        if resumable:
            vals.append((f"{rt} + {p}.IsResumable", f"$VAR[{'VN_Left9111' if p == li(EASEL_F) else 'VN_Left'}] · {ends(p)}"))
        vals.append((rt, f"{mins(p)} · {ends(p)}"))
        return vals

    def film_vars(pv, sources, state):
        """sources = [(condition, prefix)]; state = [(condition, text)] for the status word."""
        def pick(fn):
            return [(c, fn(p)) for c, p in sources]
        var(f"{pv}Title", pick(lambda p: f"$INFO[{p}.Title]"))
        var(f"{pv}L2", pick(lambda p: f"$INFO[{p}.Year]$INFO[{p}.Director, · ,]"))
        var(f"{pv}Genre", pick(lambda p: f"$INFO[{p}.Genre]"))
        var(f"{pv}Tag", pick(lambda p: f"$INFO[{p}.Tagline]"))
        prem = []
        for c, p in sources:
            prem.append((join_and(c, f"!String.IsEmpty({p}.PlotOutline)"), f"$INFO[{p}.PlotOutline]"))
            prem.append((c, f"$INFO[{p}.Plot]"))
        var(f"{pv}Prem", prem)
        st = []
        for c, p in sources:
            for sc, txt in state:
                st.append((join_and(c, sc), f"{star(p)}{txt}"))
        var(f"{pv}Status", st)
        var(f"{pv}Coll", pick(lambda p: f"$LOCALIZE[{S['part_of']}] $INFO[{p}.Set]"))
        kv = []
        for c, p in sources:
            kv += [(join_and(c, kc), kt) for kc, kt in keyline(p)]
        var(f"{pv}Key", kv)

    unseen = [(None, f"$LOCALIZE[31669]")]
    film_vars("Home_T", [(None, li(TONIGHT))], unseen)
    film_vars("Home_NP", NEWP_SRC, [("$EXP[Home_NewR]", f"$LOCALIZE[{S['recent_cap']}]"), (None, f"$LOCALIZE[{S['new_week']}]")])

    # ---- landscape placards: easel (helper item / film in progress / show in progress) and New (helper / episode)
    sxe = lambda p: f"S$INFO[{p}.Season]·E$INFO[{p}.Episode]$INFO[{p}.Title, · ,]"  # noqa: E731
    yd = lambda p: f"$INFO[{p}.Year]$INFO[{p}.Director, · ,]"  # noqa: E731
    net = lambda p: f"$INFO[{p}.Studio,, · ]$INFO[{p}.Year]$INFO[{p}.Rating, · ★ ,]"  # noqa: E731
    to_go = lambda p: (f"$INFO[{p}.Property(UnWatchedEpisodes)]{NBSP}$LOCALIZE[{S['eps_to_go']}]")  # noqa: E731

    def land_vars(pv, helper, show=None, film=None, ep=None):
        """helper / show / film / ep: the prefix of each possible source (None = not in this room)."""
        hp = helper
        isep = f"String.IsEqual({hp}.DBType,episode)"
        hs = [(f"{H} + {isep}", None), (H, None)]
        rest = []
        if show:
            rest.append(("$EXP[Home_EaselS]", show, "show"))
        if film:
            rest.append(("$EXP[Home_EaselF]", film, "film"))
        if ep:
            rest.append((f"!{H}", ep, "ep"))

        def build(name, helper_ep, helper_film, by_kind):
            vals = [(hs[0][0], helper_ep(hp)), (hs[1][0], helper_film(hp))]
            for c, p, kind in rest:
                vals.append((c, by_kind[kind](p)))
            var(f"{pv}{name}", vals)

        build("Title", lambda p: f"$INFO[{p}.TVShowTitle]", lambda p: f"$INFO[{p}.Title]",
              dict(show=lambda p: f"$INFO[{p}.Title]", film=lambda p: f"$INFO[{p}.Title]", ep=lambda p: f"$INFO[{p}.TVShowTitle]"))
        build("L2", sxe, yd, dict(show=lambda p: f"$INFO[{p}.Year]$INFO[{p}.Studio, · ,]", film=yd, ep=sxe))
        # films: genres only (their rating is on the status line); episodes: network · year · rating; a show card's
        # line 2 already says "year · network" (device audit M5: printed twice without the helper), so genres
        build("Facts", net, lambda p: f"$INFO[{p}.Genre]",
              dict(show=lambda p: f"$INFO[{p}.Genre]", film=lambda p: f"$INFO[{p}.Genre]", ep=net))
        # premise: films their own plot; shows the show's plot; helper episodes the SHOW's plot (helper property
        # KarmaMole.ShowPlot, spoiler-safe); Kodi's own episode items nothing (the episode plot spoils, DESIGN 6)
        build("Prem", lambda p: f"$INFO[{p}.Property(KarmaMole.ShowPlot)]", lambda p: f"$INFO[{p}.Plot]",
              dict(show=lambda p: f"$INFO[{p}.Plot]", film=lambda p: f"$INFO[{p}.Plot]", ep=lambda p: ""))
        # ... and the same as a presence condition (a runtime case of the placard: a missing premise hands its room on)
        pw = [f"[{hs[0][0]} + !String.IsEmpty({hp}.Property(KarmaMole.ShowPlot))]",
              f"[{H} + !{isep} + !String.IsEmpty({hp}.Plot)]"]
        pw += [f"[{c} + !String.IsEmpty({p_}.Plot)]" for c, p_, kind in rest if kind != "ep"]
        PREM_WHEN[pv] = " | ".join(pw)
        state = [(f"{H} + {isep} + Integer.IsEqual({hp}.Property(KarmaMole.EpisodesLeft),1)", f"$LOCALIZE[{S['last_ep']}]"),
                 (f"{H} + {isep} + Integer.IsGreater({hp}.Property(KarmaMole.EpisodesLeft),1)",
                  f"$INFO[{hp}.Property(KarmaMole.EpisodesLeft)]{NBSP}$LOCALIZE[{S['eps_to_go']}]")]
        if pv == "Home_N":
            state += [(f"{H} + {isep} + Integer.IsGreater({hp}.Property(KarmaMole.NewCount),1)",
                       f"$INFO[{hp}.Property(KarmaMole.NewCount)]{NBSP}$LOCALIZE[{S['new_eps']}]"),
                      (f"{H} + String.IsEqual({hp}.Property(KarmaMole.Window),recent)", f"$LOCALIZE[{S['recent_cap']}]"),
                      (H, f"$LOCALIZE[{S['new_week']}]")]
        else:
            state.append((H, f"$LOCALIZE[{S['in_prog']}]"))
        for c, p, kind in rest:
            if kind == "show":
                state += [(f"{c} + Integer.IsEqual({p}.Property(UnWatchedEpisodes),1)", f"1{NBSP}$LOCALIZE[{S['ep_to_go']}]"),
                          (c, to_go(p))]
            elif kind == "film":
                state.append((c, f"{star(p)}$LOCALIZE[{S['in_prog']}]"))
            else:
                state.append((c, f"$LOCALIZE[{S['new_week']}]"))
        var(f"{pv}State", state)
        left = "VN_HelperLeft9110" if pv == "Home_E" else "VN_HelperLeft9120"
        key = [(f"{H} + !String.IsEmpty({hp}.Property(KarmaMole.MinLeft))", f"$VAR[{left}] · {ends(hp)}"),
               (f"{H} + Integer.IsGreater({hp}.Duration(mins),0)", f"{mins(hp)} · {ends(hp)}")]
        for c, p, kind in rest:
            if kind == "film":
                key += [(f"{c} + {kv}", t) for kv, t in keyline(p)]
            elif kind == "ep":
                key.append((f"{c} + Integer.IsGreater({p}.Duration(mins),0)", f"{mins(p)} · {ends(p)}"))
        var(f"{pv}Key", key)

    land_vars("Home_E", li(EASEL_H), show=li(EASEL_S), film=li(EASEL_F))
    land_vars("Home_N", li(NEW_H), ep=li(NEW_E))

    nf, ns = n_items(EASEL_F), n_items(EASEL_S)
    count = lambda nn, cid: f"$INFO[{nn}]$VAR[Home_Plus_{cid}]"  # noqa: E731
    var("Home_EaselSub", [
        (f"{H} + Integer.IsEqual(Window(Home).Property(KarmaMole.Easel.Count),1)",
         f"1 $LOCALIZE[{S['work']}] · $LOCALIZE[{S['last_first']}]"),
        (f"{H} + !String.IsEmpty(Window(Home).Property(KarmaMole.Easel.Count))",
         f"$INFO[Window(Home).Property(KarmaMole.Easel.Count)] $LOCALIZE[{S['works']}] · $LOCALIZE[{S['last_first']}]"),
        (H, f"$LOCALIZE[{S['last_first']}]"),
        (None, f"$VAR[Home_EaselCountF]$VAR[Home_EaselCountS] $LOCALIZE[{S['in_prog_lc']}]"),
    ])
    var("Home_EaselCountF", [(f"Integer.IsEqual({nf},1)", f"1 $LOCALIZE[{S['film']}]"),
                             (f"Integer.IsGreater({nf},1)", f"{count(nf, EASEL_F)} $LOCALIZE[{S['films']}]")])
    var("Home_EaselCountS", [(f"Integer.IsGreater({nf},0) + Integer.IsGreater({ns},0)", f" · {count(ns, EASEL_S)} $LOCALIZE[{S['series_prog']}]"),
                             (f"Integer.IsGreater({ns},0)", f"{count(ns, EASEL_S)} $LOCALIZE[{S['series_prog']}]")])
    for cid in (EASEL_F, EASEL_S):   # a full list (limit 12) says "12+" (the source may hold more, LESSONS Sentence 0.9.3)
        var(f"Home_Plus_{cid}", [(f"Integer.IsEqual(Container({cid}).NumItems,12)", "+")])

    nh = li(NEW_H)
    var("Home_NewSub", [(f"{H} + String.IsEqual({nh}.Property(KarmaMole.Window),recent)", f"$LOCALIZE[{S['recent']}]"),
                        (H, f"$LOCALIZE[{S['week']}]"),
                        ("$EXP[Home_NewR]", f"$LOCALIZE[{S['recent']}]"),
                        (None, f"$LOCALIZE[{S['week_only']}]")])

    # ---- in-layout captions and art (ListItem = the drawn item)
    var("Home_LandArt", [("String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(tvshow.fanart))", "$INFO[ListItem.Art(tvshow.fanart)]"),
                         ("String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(tvshow.landscape))", "$INFO[ListItem.Art(tvshow.landscape)]"),
                         ("String.IsEqual(ListItem.DBType,episode)", "$INFO[ListItem.Art(thumb)]"),
                         ("!String.IsEmpty(ListItem.Art(fanart))", "$INFO[ListItem.Art(fanart)]"),
                         (None, "$INFO[ListItem.Art(thumb)]")])
    var("Home_CapTitle", [("String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.TVShowTitle)", "$INFO[ListItem.TVShowTitle]"),
                          (None, "$INFO[ListItem.Title]")])
    var("Home_CapHelper", [("!String.IsEmpty(ListItem.Property(KarmaMole.MinLeft))", "$VAR[VN_HelperLeft]"),
                           ("String.IsEqual(ListItem.DBType,episode) + Integer.IsGreater(ListItem.Duration(mins),0)",
                            f"S$INFO[ListItem.Season]·E$INFO[ListItem.Episode] · {mins('ListItem')}"),
                           ("Integer.IsGreater(ListItem.Duration(mins),0)", mins("ListItem"))])
    var("Home_CapShow", [("Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),1)", f"1{NBSP}$LOCALIZE[{S['ep_to_go']}]"),
                         ("Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)", to_go("ListItem"))])
    var("Home_CapEp", [("Integer.IsGreater(ListItem.Duration(mins),0)", f"S$INFO[ListItem.Season]·E$INFO[ListItem.Episode] · {mins('ListItem')}"),
                       (None, f"S$INFO[ListItem.Season]·E$INFO[ListItem.Episode]")])
    # ---- back office: the room value and the update rows
    var("Home_RoomValue", [("String.IsEqual(Skin.String(vernissage.room),day)", f"$LOCALIZE[{S['day']}]"),
                           ("String.IsEqual(Skin.String(vernissage.room),evening)", f"$LOCALIZE[{S['evening']}]"),
                           (None, f"$LOCALIZE[{S['auto']}]")])
    var("Home_UpdateVideo", [("Library.IsScanningVideo", f"$LOCALIZE[{S['stop_video']}]"), (None, "$LOCALIZE[31634]")])
    var("Home_UpdateMusic", [("Library.IsScanningMusic", f"$LOCALIZE[{S['stop_music']}]"), (None, "$LOCALIZE[31633]")])
    return NL.join(v)


def expressions():
    return NL.join(f'\t<expression name="{k}">{val}</expression>' for k, val in EXPR.items())


# ================================================================ the rail, back office, cards
def rail_layout(focused):
    o = []
    hf = f"Control.HasFocus({RAIL})"
    if focused:
        o.append(img(0, 0, 140, 140, "vn/spot.png", "eve_spot", vis=f"{hf} + {DARK}",
                     anims=['<animation effect="fade" start="100" end="73" time="0" condition="true">Conditional</animation>']))
        o.append(img(30, 30, 80, 80, "vn/dot.png", "day_focus_fill", vis=f"{hf} + {DAY}"))
    for room, gate in (("day", DAY), ("eve", DARK)):
        if focused:
            o.append(img(46, 46, ICON, ICON, "$INFO[ListItem.Icon]", f"{room}_ink", vis=f"{hf} + {gate}"))
            o.append(img(46, 46, ICON, ICON, "$INFO[ListItem.Icon]", f"{room}_ink2", vis=f"!{hf} + {gate}"))
        else:
            o.append(img(46, 46, ICON, ICON, "$INFO[ListItem.Icon]", f"{room}_ink2", vis=gate))
    if focused:
        o.append(label(112, 52, 124, 36, "$INFO[ListItem.Label]", "font_label", "$VAR[ink]", aligny="center", vis=hf))
    return NL.join(o)


RAIL_ITEMS = [  # key, icon, label string, onclick
    ("films", "films", 31401, "ActivateWindow(Videos,videodb://movies/titles/,return)"),
    ("series", "series", 31450, "ActivateWindow(Videos,videodb://tvshows/titles/,return)"),
    ("music", "music", 31400, "ActivateWindow(Music,musicdb://albums/,return)"),
    ("search", "search", 31403, "ActivateWindow(1150)"),
    ("settings", "settings", 31404, f"SetFocus({OFFICE},0,absolute)"),
]


def rail():
    items = NL.join(f"""<item>
	<label>$LOCALIZE[{sid}]</label>
	<icon>vn/icons/{icon}.png</icon>
	<property name="key">{key}</property>
	<onclick>{click}</onclick>
</item>""" for key, icon, sid, click in RAIL_ITEMS)
    body = [f"<left>{RAIL_LIST_X}</left>", f"<top>{RAIL_LIST_Y}</top>", f"<width>{RAIL_PITCH * len(RAIL_ITEMS) + 46}</width>",
            f"<height>{RAIL_H}</height>", "<orientation>horizontal</orientation>", "<scrolltime>0</scrolltime>",
            f"<onleft>{RAIL}</onleft>", f"<onright>{RAIL}</onright>", *to_room(),
            f'<itemlayout width="{RAIL_PITCH}" height="{RAIL_H}">{NL}{ind(rail_layout(False), 1)}{NL}</itemlayout>',
            f'<focusedlayout width="{RAIL_PITCH}" height="{RAIL_H}">{NL}{ind(rail_layout(True), 1)}{NL}</focusedlayout>',
            f"<content>{NL}{ind(items, 1)}{NL}</content>"]
    return f'<control type="list" id="{RAIL}">{NL}' + NL.join(ind(b, 1) for b in body) + f"{NL}</control>"


OFFICE_ITEMS = [  # key, icon, label, label2, onclick list, visible
    ("room", "sun", 31485, "$VAR[Home_RoomValue]",
     ['<onclick condition="String.IsEqual(Skin.String(vernissage.room),day)">Skin.SetString(vernissage.room,evening)</onclick>',
      '<onclick condition="String.IsEqual(Skin.String(vernissage.room),evening)">Skin.SetString(vernissage.room,auto)</onclick>',
      '<onclick condition="!String.IsEqual(Skin.String(vernissage.room),day) + !String.IsEqual(Skin.String(vernissage.room),evening)">Skin.SetString(vernissage.room,day)</onclick>'], None),
    ("skin", "skin", 31620, None, ["<onclick>ActivateWindow(SkinSettings)</onclick>"], None),
    ("kodi", "system", 31621, None, ["<onclick>ActivateWindow(Settings)</onclick>"], None),
    ("update", "update", 31622, None, [f"<onclick>SetFocus({UPDATE},0,absolute)</onclick>"], None),
    ("clean", "clean", 31623, None, [f"<onclick>SetFocus({CLEAN},0,absolute)</onclick>"], None),
    ("addons", "addons", 31624, None, ["<onclick>ActivateWindow(AddonBrowser)</onclick>"], None),
    ("files", "files", 31625, None, ["<onclick>ActivateWindow(Videos,sources://video/,return)</onclick>"], None),
    ("pictures", "pictures", 31626, None, ["<onclick>ActivateWindow(Pictures)</onclick>"], None),
    ("favourites", "favourites", 31627, None, ["<onclick>ActivateWindow(FavouritesBrowser)</onclick>"], None),
    ("livetv", "livetv", 31628, None, ["<onclick>ActivateWindow(TVChannels)</onclick>"], "System.HasPVRAddon"),
    ("power", "power", 31629, None, ["<onclick>ActivateWindow(ShutdownMenu)</onclick>"], None),
]


def office_layout(focused):
    """A plaque (80 x 80 card at item (40, 40), icon 40 centred). Focused: zoom 1.08 about the plaque centre, ink icon,
    the small pool (Evening) / 7 % disc (Day) behind it. The Room plaque shows the room glyph (sun / moon)."""
    hf = f"Control.HasFocus({OFFICE})"
    o, zoom = [], []
    lit = hf if focused else None
    if focused:
        o.append(img(0, 0, 160, 160, "vn/spot.png", "eve_spot", vis=f"{hf} + {DARK}",
                     anims=['<animation effect="fade" start="100" end="73" time="0" condition="true">Conditional</animation>']))
        o.append(img(36, 36, 88, 88, "vn/dot.png", "day_focus_fill", vis=f"{hf} + {DAY}"))
        zoom = [f'<animation effect="zoom" start="100" end="108" center="80,80" time="150" tween="cubic" easing="out" condition="{hf} + !{RM}">Conditional</animation>',
                f'<animation effect="zoom" start="100" end="108" center="80,80" time="0" condition="{hf} + {RM}">Conditional</animation>']
    inner = [twin_img(40, 40, 80, 80, "vn/white.png", "card"),
             twin_img(40, 40, 80, 80, "vn/card_edge.png", "card_edge", border="4")]
    room_item = "String.IsEqual(ListItem.Property(key),room)"
    states = [("ink", lit), ("ink2", f"!{hf}")] if focused else [("ink2", None)]
    for room, gate in (("day", DAY), ("eve", DARK)):
        for tok, cond in states:
            inner.append(img(60, 60, 40, 40, "$INFO[ListItem.Icon]", f"{room}_{tok}", vis=join_and(f"!{room_item}", cond, gate)))
            inner.append(img(60, 60, 40, 40, "vn/icons/sun.png", f"{room}_{tok}", vis=join_and(room_item, "$EXP[VN_Day]", cond, gate)))
            inner.append(img(60, 60, 40, 40, "vn/icons/moon.png", f"{room}_{tok}", vis=join_and(room_item, "$EXP[VN_Dark]", cond, gate)))
    o.append(group(inner, anims=zoom))
    return NL.join(o)


def office():
    items = []
    for key, icon, sid, l2, clicks, vis in OFFICE_ITEMS:
        b = [f"<label>$LOCALIZE[{sid}]</label>"]
        if l2:
            b.append(f"<label2>{l2}</label2>")
        b.append(f"<icon>vn/icons/{icon}.png</icon>")
        b.append(f'<property name="key">{key}</property>')
        b += clicks
        if vis:
            b.append(f"<visible>{vis}</visible>")
        items.append("<item>" + NL + NL.join(ind(z, 1) for z in b) + NL + "</item>")
    lst = NL.join([f'<control type="list" id="{OFFICE}">', "\t<left>80</left>", "\t<top>816</top>",
                   f"\t<width>{96 * len(OFFICE_ITEMS) + 80}</width>", "\t<height>160</height>",
                   "\t<orientation>horizontal</orientation>", "\t<scrolltime>0</scrolltime>",
                   f"\t<onleft>{OFFICE}</onleft>", f"\t<onright>{OFFICE}</onright>",
                   *[ind(z, 1) for z in to_room()], f"\t<ondown>{RAIL}</ondown>", f"\t<onback>{RAIL}</onback>",
                   f'\t<itemlayout width="96" height="160">{NL}{ind(office_layout(False), 2)}{NL}\t</itemlayout>',
                   f'\t<focusedlayout width="96" height="160">{NL}{ind(office_layout(True), 2)}{NL}\t</focusedlayout>',
                   f"\t<content>{NL}{ind(NL.join(items), 2)}{NL}\t</content>", "</control>"])
    cap = NL.join([
        label(1196, 878, 600, 36, f"$INFO[Container({OFFICE}).ListItem.Label][COLOR $VAR[ink2]]$INFO[Container({OFFICE}).ListItem.Label2, · ,][/COLOR]",
              "font_label", "$VAR[ink]", aligny="center", selected=False),
    ])
    show = f"Control.HasFocus({OFFICE}) | Control.HasFocus({CLEAN}) | Control.HasFocus({UPDATE})"
    return group([lst, cap], anims=fade_cond(f"![{show}]", 150))


def card_list(cid, left, top, width, rows):
    items = []
    for lab, clicks in rows:
        items.append("<item>" + NL + NL.join(ind(z, 1) for z in [f"<label>{lab}</label>", *clicks]) + NL + "</item>")
    hf = f"Control.HasFocus({cid})"

    def row(focused):
        o = []
        if focused:
            o += [twin_img(0, 0, width, 64, "vn/white.png", "wall", vis=hf),
                  twin_img(0, 0, width, 1, "vn/white.png", "card_edge", vis=hf),
                  twin_img(0, 63, width, 1, "vn/white.png", "card_edge", vis=hf),
                  label(36, 0, width - 72, 64, "$INFO[ListItem.Label]", "font_body", "$VAR[ink]", aligny="center", vis=hf),
                  label(36, 0, width - 72, 64, "$INFO[ListItem.Label]", "font_body", "$VAR[ink2]", aligny="center", vis=f"!{hf}")]
        else:
            o.append(label(36, 0, width - 72, 64, "$INFO[ListItem.Label]", "font_body", "$VAR[ink2]", aligny="center"))
        return NL.join(o)
    return NL.join([f'<control type="list" id="{cid}">', f"\t<left>{left}</left>", f"\t<top>{top}</top>",
                    f"\t<width>{width}</width>", f"\t<height>{64 * len(rows)}</height>", "\t<scrolltime>0</scrolltime>",
                    f"\t<onup>{OFFICE}</onup>", f"\t<ondown>{cid}</ondown>", f"\t<onleft>{OFFICE}</onleft>",
                    f"\t<onright>{cid}</onright>", f"\t<onback>{OFFICE}</onback>",
                    f'\t<itemlayout width="{width}" height="64">{NL}{ind(row(False), 2)}{NL}\t</itemlayout>',
                    f'\t<focusedlayout width="{width}" height="64">{NL}{ind(row(True), 2)}{NL}\t</focusedlayout>',
                    f"\t<content>{NL}{ind(NL.join(items), 2)}{NL}\t</content>", "</control>"])


def cards():
    """Clean confirm 9131 ("No" first, focused: Kodi 21's CleanLibrary doesn't ask, LESSONS) and update chooser 9132,
    over the room dimmed by the role scrim (its own fades), drawn after the rail (LESSONS Groove pass 2). A list whose
    first row is the target opens with SetFocus(id,0,absolute)."""
    back = f"SetFocus({OFFICE})"
    clean = card_list(CLEAN, 600, 520, 720, [
        ("$LOCALIZE[31630]", [f"<onclick>{back}</onclick>"]),
        ("$LOCALIZE[31632]", ["<onclick>CleanLibrary(video)</onclick>", f"<onclick>{back}</onclick>"]),
        ("$LOCALIZE[31631]", ["<onclick>CleanLibrary(music)</onclick>", f"<onclick>{back}</onclick>"]),
    ])
    update = card_list(UPDATE, 600, 488, 720, [
        ("$VAR[Home_UpdateVideo]", ["<onclick>UpdateLibrary(video)</onclick>", f"<onclick>{back}</onclick>"]),
        ("$VAR[Home_UpdateMusic]", ["<onclick>UpdateLibrary(music)</onclick>", f"<onclick>{back}</onclick>"]),
    ])
    dim = img(0, 0, 1920, 1080, "vn/white.png", "$VAR[scrim_card]")
    c1 = group([dim, card(600, 330, 720, 420),
                label(636, 352, 648, 50, f"$LOCALIZE[{S['clean_q']}]", "font_placard", "$VAR[ink]", aligny="center", selected=False),
                textbox(636, 414, 648, 80, f"$LOCALIZE[{S['clean_body']}]", "font_small", "$VAR[ink2]"),
                clean], anims=fade_cond(f"!Control.HasFocus({CLEAN})", 150))
    c2 = group([dim, card(600, 380, 720, 300),
                label(636, 402, 648, 50, f"$LOCALIZE[{S['update_q']}]", "font_placard", "$VAR[ink]", aligny="center", selected=False),
                update], anims=fade_cond(f"!Control.HasFocus({UPDATE})", 150))
    return NL.join([c1, c2])



def main():
    PL.set_prefix("Home")
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_home.py - edit the generator, then re-run. Home: docs/skin.vernissage/screens/Home.md.
     Rooms: Tonight {TONIGHT}, Still on the easel {EASEL_H} (helper) / {EASEL_F} + {EASEL_S}, New in the collection
     {NEW_H} (helper) / {NEW_F} + {NEW_E} / {NEW_R}; rail {RAIL}; back office {OFFICE}; cards {CLEAN} / {UPDATE};
     placards {P_TONIGHT}-{P_NEW_P}; title boxes {T_TONIGHT}-{T_NEW_P}; probes {PR_TONIGHT_KEY}-{PR_NEWP_KEY}. -->
<includes>
{expressions()}
__PLACARD_EXPRS__
{variables()}

	<!-- The three rooms (each faded in only while it is the room on show; all stay processed) -->
	<include name="Home_Rooms">
{ind(room_tonight(), 2)}
{ind(room_easel(), 2)}
{ind(room_new(), 2)}
{ind(hint(), 2)}
	</include>

	<!-- The rail 9000 (SPEC 6.5): Films, Series, Music, Search, Settings at fixed 226 px slots padded 46 px so the
	     pool isn't clipped. Left / Right stop at the ends, Up = the room on show, no onback: the rail is where Back
	     rests (SPEC 6.1). Settings' OK raises the back office. -->
	<include name="Home_Rail">
{ind(rail(), 2)}
	</include>

	<!-- The back office 9130 (Settings' OK): plaques above the rail, caption at the row's right end; faded in only
	     while it or its cards have focus (always processed: a hidden static list can't take focus). -->
	<include name="Home_BackOffice">
{ind(office(), 2)}
	</include>

	<!-- Now playing card 9950 (VN_NowPlaying): Down = the first room with works, Back = the rail -->
	<include name="Home_NowPlayingNav">
{ind(NL.join(nav_np()), 2)}
	</include>

	<include name="Home_Cards">
{ind(cards(), 2)}
	</include>
</includes>
"""
    body = body.replace("__PLACARD_EXPRS__", PL.expressions_xml(body))
    body = no_self(body)   # ends stop, never wrap (vnxml.no_self)
    OUT.write_text(body, encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {body.count('<control')} controls, {len(body) // 1024} KB")


if __name__ == "__main__":
    main()
