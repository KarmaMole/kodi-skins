"""Six Degrees Home ("Start somewhere") -> 1080i/Home.xml + 1080i/Includes_Home.xml + 1080i/Timers.xml.

Board: docs/concepts/round4/mockups/SixDegreesHome.html (boards2.py board_home).

Model
- Section words Movies / Series / Music (9001-9003) switch `sixdegrees.section`; Search 9005, Index 9006,
  System 9007 (gear) sit right of them, the clock at the right edge.
- The start line is one horizontal list per section (9110 films, 9120 series, 9130 music) of STATIC
  items fed by hidden data lists (lesson 107 / Nocturne): Continue x2, Newest x1, Unwatched 7.5+ x2,
  Tonight's surprise x1, then the Index terminus. The focused starter grows (focusedlayout 302 vs 234),
  captions and the grey line are drawn inside the item layouts, so empty groups simply close up.
- OK boards the map at the focused starter; Down reaches three real buttons (Board / Play / Station page)
  because the Shield remote has no Info or Play key on a list.
- The preview mini-map (right) is the focused starter's four lines at small scale. Its data loads only
  after focus rests 1 s (Timers.xml writes `sixdegrees.pv.*`, then the hidden lists 92xx reload).

    python skins/skin.sixdegrees/_src/make_home.py
"""
from __future__ import annotations

from pathlib import Path

from make_map import (P, RM, OPEN, rule, close, prop, info, img, lbl, group, DEPTH, FIELDS, map_timers,
                      ruleq, esc_info, url_safe, qvar)

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i"


def tag(name, value, cond=None):
    c = f' condition="{cond}"' if cond else ""
    return f"<{name}{c}>{value}</{name}>"


# ------------------------------------------------------------------ geometry (board)
LIST_X, LIST_Y = 40, 230          # list origin; posters start at +24 (x 64)
PAD = 24
PW, PH = 184, 276                 # unfocused poster
FW, FH = 224, 336                 # focused poster
SLOT, FSLOT = 234, 302            # slot widths (gap 50; focused +14 each side)
LINE_Y = 474 - LIST_Y             # 244: the start line (centre)
CAP_Y, HAIR_Y = 8, 42             # caption top, hairline top (y 238 / 272 on screen)
P_TOP = LINE_Y - PH // 2          # 106
F_TOP = LINE_Y - FH // 2          # 76
TITLE_Y = P_TOP + PH + 20         # 402

SECTIONS = {
    "movies": dict(list=9110, word=9001, kind="movies", label="Movies", textx=420, tw=85),
    "tvshows": dict(list=9120, word=9002, kind="tvshows", label="Series", textx=549, tw=75),
    "music": dict(list=9130, word=9003, kind="albums", label="Music", textx=668, tw=70),
}

# data lists per section: (id, content, sortby, sortorder, limit)
DATA = {
    "movies": [
        (9101, "special://skin/playlists/sd_continue_movies.xsp", "lastplayed", "descending", 2),
        (9102, "special://skin/playlists/sd_added_movies.xsp", "dateadded", "descending", 1),
        (9103, "special://skin/playlists/sd_spotlight.xsp", "random", "ascending", 2),
        (9104, "special://skin/playlists/sd_surprise_movies.xsp", "random", "ascending", 1),
        (9105, "special://skin/playlists/sd_toprated_unwatched_all.xsp", "", "", 0),
        (9106, "videodb://movies/titles/", "", "", 0),
    ],
    "tvshows": [
        (9121, "special://skin/playlists/sd_inprogress_tvshows.xsp", "lastplayed", "descending", 2),
        (9122, "special://skin/playlists/sd_new_episodes.xsp", "dateadded", "descending", 1),
        (9123, "special://skin/playlists/sd_toprated_tvshows.xsp", "random", "ascending", 2),
        (9124, "special://skin/playlists/sd_surprise_tvshows.xsp", "random", "ascending", 1),
        (9125, "special://skin/playlists/sd_toprated_tvshows_all.xsp", "", "", 0),
        (9126, "videodb://tvshows/titles/", "", "", 0),
    ],
    "music": [
        (9131, "musicdb://recentlyplayedalbums/", "lastplayed", "descending", 2),
        (9132, "musicdb://recentlyaddedalbums/", "dateadded", "descending", 1),
        (9133, "special://skin/playlists/sd_random_albums.xsp", "random", "ascending", 2),
        (9134, "special://skin/playlists/sd_surprise_albums.xsp", "random", "ascending", 1),
        (9135, "special://skin/playlists/sd_random_albums.xsp", "", "", 0),
        (9136, "musicdb://albums/", "", "", 0),
    ],
}

CAPS = {
    "movies": ["Continue", "Newest", "Unwatched", "Tonight's surprise"],
    "tvshows": ["Continue", "New episodes", "Unwatched", "Tonight's surprise"],
    "music": ["Recently played", "Newest", "From the shelves", "Tonight's surprise"],
}
CAP_STAR_X = 156  # measured: "UNWATCHED " in SixDegreesCaps 21 (+ slack)


# ------------------------------------------------------------------ static items
def item_props(sec, src, idx, cap, join, why, star=False, joined=False):
    """A static list item whose label/art/properties read Container(src).ListItemAbsolute(idx)."""
    li = f"Container({src}).ListItemAbsolute({idx})"
    kind = SECTIONS[sec]["kind"]
    if sec == "tvshows" and src == 9122:   # newest episode -> its show
        dbid, title, poster = f"$INFO[{li}.TvShowDBID]", f"$INFO[{li}.TVShowTitle]", f"$INFO[{li}.Art(tvshow.poster)]"
        year, dirv = f"$INFO[{li}.Year]", f"$INFO[{li}.Studio]"
    elif sec == "tvshows":
        dbid, title, poster = f"$INFO[{li}.DBID]", f"$INFO[{li}.Title]", f"$INFO[{li}.Art(poster)]"
        year, dirv = f"$INFO[{li}.Year]", f"$INFO[{li}.Studio]"
    elif sec == "music":
        dbid, title, poster = f"$INFO[{li}.DBID]", f"$INFO[{li}.Label]", f"$INFO[{li}.Art(thumb)]"
        year, dirv = f"$INFO[{li}.Year]", f"$INFO[{li}.Artist]"
    else:
        dbid, title, poster = f"$INFO[{li}.DBID]", f"$INFO[{li}.Title]", f"$INFO[{li}.Art(poster)]"
        year, dirv = f"$INFO[{li}.Year]", f"$INFO[{li}.Director]"
    p = [f"<label>{title}</label>",
         f"<icon>{poster}</icon>",
         f'<property name="dbid">{dbid}</property>',
         f'<property name="year">{year}</property>',
         f'<property name="dir">{dirv}</property>',
         f'<property name="genre">$INFO[{li}.Genre]</property>',
         f'<property name="tmdb">$INFO[{li}.UniqueID(tmdb)]</property>',
         f'<property name="file">$INFO[{li}.FileNameAndPath]</property>',
         f'<property name="pct">$INFO[{li}.PercentPlayed]</property>',
         f'<property name="cap">{cap}</property>',
         f'<property name="join">{join}</property>',
         f'<property name="why">{why}</property>',
         f'<property name="star">{"yes" if star else ""}</property>',
         f'<property name="joined">{"yes" if joined else ""}</property>',
         f'<property name="kind">{kind}</property>',
         f"<visible>!String.IsEmpty({li}.Label)</visible>"]
    return p


def why_label(sec, src, idx, group):
    li = f"Container({src}).ListItemAbsolute({idx})"
    if sec == "music":
        return f"$INFO[{li}.Artist]"
    if group == 0:  # continue
        if sec == "tvshows":
            return f"$INFO[{li}.Property(UnWatchedEpisodes),, unwatched]"
        return f"$INFO[{li}.EndTimeResume,ends ,]"
    if group == 1:
        if sec == "tvshows":
            return f"$INFO[{li}.Season,S,]$INFO[{li}.Episode, E, new]"
        return "added $VAR[Home_AddedDay] $VAR[Home_AddedMonth]"
    if group == 2:
        if sec == "tvshows":
            return f"$INFO[{li}.Rating,★ ,]"
        return f"$INFO[{li}.Rating]"
    if sec == "tvshows":
        return f"$VAR[Home_Seasons_{src}]"
    return f"$VAR[Home_Time_{src}]$INFO[{li}.EndTime, · ends ,]"


def static_items(sec):
    d = DATA[sec]
    caps = CAPS[sec]
    items = []
    # (source list, index, group, caption shown on this item)
    plan = [(d[0][0], 0, 0), (d[0][0], 1, 0), (d[1][0], 0, 1), (d[2][0], 0, 2), (d[2][0], 1, 2), (d[3][0], 0, 3)]
    for src, idx, g in plan:
        first = idx == 0
        cap = caps[g] if first else ""
        join = f"$INFO[Container({src}).ListItemAbsolute(1).Label]" if (first and g in (0, 2)) else ""
        why = why_label(sec, src, idx, g)
        star = (g == 2 and sec != "music")
        body = item_props(sec, src, idx, cap, join, why, star=star and first, joined=(idx == 1))
        items.append("<item>" + "".join(body) + "</item>")
    # Index terminus
    items.append('<item><label>Index</label><property name="terminus">yes</property>'
                 f'<property name="count">$INFO[Container({d[5][0]}).NumItems]</property></item>')
    return items


# ------------------------------------------------------------------ item layouts
def poster_block(x, y, w, h, mask):
    return [img(x - 24, y - 16, w + 48, h + 48, "sd/shadow_poster.png", diffuse="shadow", border="40"),
            img(x, y, w, h, "common/white.png", diffuse="wash"),
            lbl(x + 12, y + 12, w - 24, 90, "$INFO[ListItem.Label]", "semi_22", "ink2", aligny="top", wrap=True),
            '<control type="image">'
            f"<left>{x}</left><top>{y}</top><width>{w}</width><height>{h}</height><aspectratio>scale</aspectratio><fadetime>150</fadetime>"
            f'<texture background="true" diffuse="sd/{mask}">$INFO[ListItem.Icon]</texture></control>']


def resume_bar(x, y, w, h):
    # board: inset 12, bottom 18, 6 px, white 55 % track + white fill
    return ['<control type="progress">'
            f"<left>{x + 12}</left><top>{y + h - 24}</top><width>{w - 24}</width><height>6</height>"
            '<texturebg border="3,0,3,0" colordiffuse="track_on_art">sd/line_h6.png</texturebg>'
            '<lefttexture /><midtexture border="3,0,3,0" colordiffuse="white">sd/line_h6.png</midtexture><righttexture />'
            "<info>ListItem.Property(pct)</info>"
            "<visible>Integer.IsGreater(ListItem.Property(pct),0)</visible></control>"]


def caption_block(x_left, x_right_join, x_right_solo):
    out = [lbl(x_left, CAP_Y, 360, 30, "$INFO[ListItem.Property(cap)]", "caps_21", "ink2", aligny="top",
               vis="String.IsEmpty(ListItem.Property(star))"),
           # "UNWATCHED ★ 7.5+": star glyph is an image (Hanken has no star)
           group([lbl(x_left, CAP_Y, 200, 30, "$INFO[ListItem.Property(cap)]", "caps_21", "ink2", aligny="top"),
                  img(x_left + CAP_STAR_X, CAP_Y + 2, 20, 20, "sd/star.png", diffuse="ink2"),
                  lbl(x_left + CAP_STAR_X + 28, CAP_Y, 100, 30, "7.5+", "caps_21", "ink2", aligny="top")],
                 vis="!String.IsEmpty(ListItem.Property(star))"),
           img(x_left, HAIR_Y, x_right_join - x_left, 2, "common/white.png", diffuse="hair",
               vis="!String.IsEmpty(ListItem.Property(cap)) + !String.IsEmpty(ListItem.Property(join))"),
           img(x_left, HAIR_Y, x_right_solo - x_left, 2, "common/white.png", diffuse="hair",
               vis="!String.IsEmpty(ListItem.Property(cap)) + String.IsEmpty(ListItem.Property(join))"),
           # second item of a joined group: continue the hairline under it
           ]
    return out


def start_line(w):
    return [img(0, LINE_Y - 4, w, 8, "common/white.png", diffuse="l_route")]


def terminus_layout(focused, list_id, count_text):
    # ring at x 164 (+68 when focused, because no starter is focused then)
    rx = 164 + (68 if focused else 0)
    ch = [img(0, LINE_Y - 4, rx, 8, "common/white.png", diffuse="l_route")]
    if focused:
        ch.append(img(rx - 27, LINE_Y - 27, 54, 54, "sd/disc_34.png", diffuse="white"))
        ch.append(img(rx - 27, LINE_Y - 27, 54, 54, "sd/ring_34_8.png", diffuse="ink"))
        ch.append(img(rx + 26, LINE_Y - 40, 128, 50, "sd/pill_48.png", diffuse="ink", border="24",
                      vis=f"Control.HasFocus({list_id})"))
        ch.append(lbl(rx + 26, LINE_Y - 40, 128, 50, "Index", "xb_28", "white", align="center", vis=f"Control.HasFocus({list_id})"))
        ch.append(lbl(rx + 42, LINE_Y - 40, 200, 50, "Index", "xb_28", "ink", vis=f"!Control.HasFocus({list_id})"))
    else:
        ch.append(img(rx - 20, LINE_Y - 20, 40, 40, "sd/disc_34.png", diffuse="white"))
        ch.append(img(rx - 20, LINE_Y - 20, 40, 40, "sd/ring_34_8.png", diffuse="ink"))
        ch.append(lbl(rx + 36, LINE_Y - 40, 200, 40, "Index", "xb_28", "ink"))
    ch.append(lbl(rx + 36 + (6 if focused else 0), LINE_Y + 4, 260, 30, count_text, "semi_21", "ink2"))
    return ch


def layouts(sec):
    lid = SECTIONS[sec]["list"]
    count_text = "A–Z  ·  $INFO[ListItem.Property(count)]"
    sq = sec == "music"  # album covers are square
    ph, fh = (PW, FW) if sq else (PH, FH)
    p_top, f_top = LINE_Y - ph // 2, LINE_Y - fh // 2
    title_y = p_top + ph + 20
    m_unf, m_foc = ("mask_180x180.png", "mask_180x180.png") if sq else ("mask_184x276.png", "mask_224x336.png")
    # unfocused item
    x = PAD
    unf = start_line(SLOT)
    unf += caption_block(x, SLOT + PAD, x + PW)
    unf.append(img(PAD, HAIR_Y, PW, 2, "common/white.png", diffuse="hair",
                   vis="String.IsEmpty(ListItem.Property(cap)) + !String.IsEmpty(ListItem.Property(joined))"))
    unf_body = poster_block(x, p_top, PW, ph, m_unf) + resume_bar(x, p_top, PW, ph)
    unf_body.append('<control type="textbox">'
                    f"<left>{x + PW // 2 - 118}</left><top>{title_y}</top><width>236</width><height>92</height>"
                    "<font>st_22</font><textcolor>ink</textcolor><align>center</align>"
                    "<label>$INFO[ListItem.Label][CR][COLOR ink2]$INFO[ListItem.Property(why)][/COLOR]</label></control>")
    unf.append(group(unf_body, vis="String.IsEmpty(ListItem.Property(terminus))"))
    unf_t = group(terminus_layout(False, lid, count_text), vis="!String.IsEmpty(ListItem.Property(terminus))")
    # focused item
    fx = PAD + 14
    foc = start_line(FSLOT)
    foc += caption_block(fx, FSLOT + PAD, fx + FW)
    foc.append(img(PAD, HAIR_Y, fx + FW - PAD, 2, "common/white.png", diffuse="hair",
                   vis="String.IsEmpty(ListItem.Property(cap)) + !String.IsEmpty(ListItem.Property(joined))"))
    o = 15  # gap 8 + ring 7
    fb = [img(fx - o - 40, f_top - o - 20, FW + 2 * o + 80, fh + 2 * o + 80, "sd/shadow_big.png", diffuse="shadow", border="100",
              vis=f"Control.HasFocus({lid})"),
          img(fx - o, f_top - o, FW + 2 * o, fh + 2 * o, "sd/ringf_fill.png", diffuse="ground", border="20",
              vis=f"Control.HasFocus({lid})"),
          img(fx - o, f_top - o, FW + 2 * o, fh + 2 * o, "sd/ringf_7.png", diffuse="ink", border="20",
              vis=f"Control.HasFocus({lid})")]
    fb += poster_block(fx, f_top, FW, fh, m_foc) + resume_bar(fx, f_top, FW, fh)
    # when the row is not focused, the selected starter stays big (its preview is shown) and keeps its title
    fb.append('<control type="textbox">'
              f"<left>{fx + FW // 2 - 130}</left><top>{f_top + fh + 22}</top><width>260</width><height>92</height>"
              "<font>st_22</font><textcolor>ink</textcolor><align>center</align>"
              f"<label>$INFO[ListItem.Label][CR][COLOR ink2]$INFO[ListItem.Property(why)][/COLOR]</label><visible>!Control.HasFocus({lid})</visible></control>")
    anim = (f'<animation type="Focus" condition="!{RM}"><effect type="zoom" start="86" end="100" center="{fx + FW // 2},{LINE_Y}" time="180" tween="cubic" easing="out"/></animation>')
    foc.append(group(fb, vis="String.IsEmpty(ListItem.Property(terminus))"))
    foc_t = group(terminus_layout(True, lid, count_text), vis="!String.IsEmpty(ListItem.Property(terminus))")
    il = [f'<itemlayout width="{SLOT}" height="520">'] + unf + [unf_t, "</itemlayout>"]
    fl = [f'<focusedlayout width="{FSLOT}" height="520">'] + foc + [foc_t, "</focusedlayout>"]
    return il + fl


def start_list(sec):
    s = SECTIONS[sec]
    lid = s["list"]
    t = [f'<control type="list" id="{lid}">',
         f"<left>{LIST_X}</left><top>{LIST_Y}</top><width>{1920 - LIST_X}</width><height>520</height>",
         "<orientation>horizontal</orientation><scrolltime tween=\"cubic\" easing=\"out\">240</scrolltime>",
         f"<visible>$EXP[Home_Is_{sec}]</visible>",
         f"<onup>{s['word']}</onup><onback>{s['word']}</onback>",
         f'<ondown condition="String.IsEmpty(Container({lid}).ListItem.Property(terminus))">9151</ondown>',
         f'<onfocus>SetProperty({P}.homefocus,{lid},home)</onfocus>']
    t += layouts(sec)
    # OK = board the map at this starter (static-content onclick runs with the clicked item, lesson 143)
    t.append(f'<onclick condition="!String.IsEmpty(ListItem.Property(terminus))">$VAR[Home_IndexAction]</onclick>')
    for a in board_actions("ListItem", sec):
        t.append(f'<onclick condition="String.IsEmpty(ListItem.Property(terminus))">{a}</onclick>')
    t.append("<content>")
    t += static_items(sec)
    t.append("</content>")
    t.append("</control>")
    return "\n".join(t)


def board_actions(src, sec):
    """Start a new journey at the item (route cleared). Reads the static item's properties."""
    a = []
    for i in range(1, DEPTH + 1):
        for f in FIELDS:
            a.append(f"ClearProperty({P}.r{i}.{f},home)")
    a += [f"SetProperty({P}.c.dbid,$INFO[{src}.Property(dbid)],home)",
          f"SetProperty({P}.c.title,$ESCINFO[{src}.Label],home)",
          f"SetProperty({P}.c.year,$INFO[{src}.Property(year)],home)",
          f"SetProperty({P}.c.poster,$ESCINFO[{src}.Icon],home)",
          f"SetProperty({P}.c.tmdb,$INFO[{src}.Property(tmdb)],home)",
          f"SetProperty({P}.c.file,$ESCINFO[{src}.Property(file)],home)",
          f"SetProperty({P}.c.dir,$ESCINFO[{src}.Property(dir)],home)",
          f"SetProperty({P}.c.genre,$ESCINFO[{src}.Property(genre)],home)",
          f"SetProperty({P}.c.col,route,home)",
          f"SetProperty({P}.kind,$INFO[{src}.Property(kind)],home)",
          f"SetProperty({P}.from,start,home)",
          f"SetProperty({P}.flip,$VAR[Map_FlipNext],home)",
          "ActivateWindow(1160)"]
    return a


# ------------------------------------------------------------------ data lists
def data_lists():
    out = []
    for sec, rows in DATA.items():
        for cid, path, sb, so, lim in rows:
            attrs = ' target="videos"' if sec != "music" else ' target="music"'
            if sb:
                attrs += f' sortby="{sb}" sortorder="{so}"'
            if lim:
                attrs += f' limit="{lim}" browse="never"'
            draw = ('<itemlayout width="1" height="1"><control type="image"><width>1</width><height>1</height>'
                    '<texture colordiffuse="00ffffff">$INFO[ListItem.Icon]</texture></control></itemlayout>'
                    '<focusedlayout width="1" height="1"><control type="image"><width>1</width><height>1</height>'
                    '<texture colordiffuse="00ffffff">$INFO[ListItem.Icon]</texture></control></focusedlayout>') if lim else \
                '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
            # 0.9.2: 2 px tall so BOTH items of a limit-2 list sit on the page: SetFocus(id,1,absolute) on a
            # 1-item-high list did nothing on the Shield (Home "Station page" on the second starter)
            out.append(f'<control type="list" id="{cid}"><left>{(cid % 100) * 4}</left><top>1078</top><width>3</width><height>2</height>'
                       f"<orientation>vertical</orientation>{draw}"
                       f'<onfocus>noop</onfocus><content{attrs}>{path}</content></control>')
    return out


# ------------------------------------------------------------------ preview (mini map)
PV = {"det": 9201, "up": 9211, "right": 9212, "down": 9213, "left": 9214, "p1": 9221, "p2": 9222, "p3": 9223}
ROOT = {"movies": "videodb://movies/titles/?xsp=", "tvshows": "videodb://tvshows/titles/?xsp=",
        "albums": "musicdb://albums/?xsp="}


def pvprop(n):
    return prop("pv." + n)


def pv_variables():
    v = []
    a = v.append
    sv = "System.AddonIsEnabled(script.skinvariables)"
    is_tv = f"String.IsEqual({pvprop('kind')},tvshows)"
    is_mu = f"String.IsEqual({pvprop('kind')},albums)"
    a('<variable name="Home_PvDetails">')
    a(f'\t<value condition="{sv} + {is_tv} + !String.IsEmpty({pvprop("dbid")})">plugin://script.skinvariables/?info=get_dbitem_tvshow_details&amp;dbid=$INFO[{pvprop("dbid")}]</value>')
    a(f'\t<value condition="{sv} + !{is_mu} + !String.IsEmpty({pvprop("dbid")})">plugin://script.skinvariables/?info=get_dbitem_movie_details&amp;dbid=$INFO[{pvprop("dbid")}]</value>')
    a("</variable>")
    ok = (f'String.IsEqual(Container(9201).ListItem.DBID,{pvprop("dbid")}) + '
          f'[[{is_tv} + String.IsEqual(Container(9201).ListItem.DBType,tvshow)] | [!{is_tv} + !{is_mu} + String.IsEqual(Container(9201).ListItem.DBType,movie)]]')
    a(f'<expression name="Home_PvMatch">{sv} + {ok}</expression>')
    a('<variable name="Home_PvUp">')
    a(f'\t<value condition="$EXP[Home_PvMatch] + {is_tv}">$INFO[Container(9201).ListItem.Property(studio.0)]</value>')
    a(f'\t<value condition="$EXP[Home_PvMatch]">$INFO[Container(9201).ListItem.Property(director.0)]</value>')
    a(f"\t<value>$INFO[{pvprop('dir')}]</value>")
    a("</variable>")
    for n in range(4):
        a(f'<variable name="Home_PvCast{n}"><value condition="$EXP[Home_PvMatch]">$INFO[Container(9201).ListItem.Property(cast.{n}.name)]</value></variable>')
    a('<variable name="Home_PvGenre">')
    a(f'\t<value condition="$EXP[Home_PvMatch]">$INFO[Container(9201).ListItem.Property(genre.0)]</value>')
    a(f'\t<value condition="{is_mu}">$INFO[{pvprop("genre")}]</value>')
    a("</variable>")
    a('<variable name="Home_PvCo">')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(9221).NumItems,2)">$VAR[Home_PvCast1]</value>')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(9222).NumItems,2)">$VAR[Home_PvCast2]</value>')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(9223).NumItems,2)">$VAR[Home_PvCast3]</value>')
    a("\t<value>$VAR[Home_PvCast1]</value>")
    a("</variable>")
    # 0.9.7: free text goes into the xsp JSON as $ESCINFO string literals (quotes / backslashes escaped);
    # values with '&' or '%' can't sit in the URL and become "" (see make_map.qvar)
    v.extend(qvar("Home_PvUpQ", [(f"$EXP[Home_PvMatch] + {is_tv}", "Container(9201).ListItem.Property(studio.0)"),
                                 ("$EXP[Home_PvMatch]", "Container(9201).ListItem.Property(director.0)"),
                                 (None, pvprop("dir"))]))
    for n in range(4):
        v.extend(qvar(f"Home_PvCast{n}Q", [("$EXP[Home_PvMatch]", f"Container(9201).ListItem.Property(cast.{n}.name)")]))
    v.extend(qvar("Home_PvGenreQ", [("$EXP[Home_PvMatch]", "Container(9201).ListItem.Property(genre.0)"),
                                    (is_mu, pvprop("genre"))]))
    v.extend(qvar("Home_PvCentreGenreQ", [(None, pvprop("genre"))]))
    a('<variable name="Home_PvCoQ">')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(9221).NumItems,2)">$VAR[Home_PvCast1Q]</value>')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(9222).NumItems,2)">$VAR[Home_PvCast2Q]</value>')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(9223).NumItems,2)">$VAR[Home_PvCast3Q]</value>')
    a("\t<value>$VAR[Home_PvCast1Q]</value>")
    a("</variable>")
    a('<variable name="Home_PvExcl">')
    a(f'\t<value condition="{url_safe(pvprop("title"))} + {is_mu}">%2C{ruleq("album", "isnot", esc_info(pvprop("title")))}</value>')
    a(f'\t<value condition="{url_safe(pvprop("title"))}">%2C{ruleq("title", "isnot", esc_info(pvprop("title")))}</value>')
    a("</variable>")
    upf = {"movies": "director", "tvshows": "studio", "albums": "albumartist"}
    for kind in ("movies", "tvshows", "albums"):
        tail = f"$VAR[Home_PvExcl]{close(kind)}"
        R = ROOT[kind]
        paths = {
            "Up": f"{R}{OPEN}{ruleq(upf[kind], 'is', '$VAR[Home_PvUpQ]')}{tail}",
            "Down": f"{R}{OPEN}{rule('year', 'is', '$INFO[' + pvprop('year') + ']')}%2C{ruleq('genre', 'is', '$VAR[Home_PvGenreQ]')}{tail}",
            "DownY": f"{R}{OPEN}{rule('year', 'is', '$INFO[' + pvprop('year') + ']')}{tail}",
        }
        if kind == "albums":
            paths["Right"] = f"{R}{OPEN}{ruleq('genre', 'is', '$VAR[Home_PvCentreGenreQ]')}{tail}"
            paths["Left"] = f"{R}{OPEN}{ruleq('artist', 'is', '$VAR[Home_PvUpQ]')}%2C{ruleq('albumartist', 'isnot', '$VAR[Home_PvUpQ]')}{tail}"
            paths["Down"] = paths["DownY"]
        else:
            paths["Right"] = f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[Home_PvCast0Q]')}{tail}"
            paths["Left"] = f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[Home_PvCoQ]')}{tail}"
            for n in (1, 2, 3):
                paths[f"P{n}"] = f"{R}{OPEN}{ruleq('actor', 'is', f'$VAR[Home_PvCast{n}Q]')}{tail}"
        for k, pth in paths.items():
            a(f'<variable name="Home_PvPath{k}_{kind}"><value>{pth}</value></variable>')
    for k in ("Up", "Right", "Left", "P1", "P2", "P3"):
        a(f'<variable name="Home_PvPath{k}">')
        a(f'\t<value condition="String.IsEmpty({pvprop("dbid")})">videodb://movies/sets/</value>')
        a(f'\t<value condition="{is_tv}">$VAR[Home_PvPath{k}_tvshows]</value>')
        if k in ("Up", "Right", "Left"):
            a(f'\t<value condition="{is_mu}">$VAR[Home_PvPath{k}_albums]</value>')
        else:
            a(f'\t<value condition="{is_mu}">videodb://movies/sets/</value>')
        a(f"\t<value>$VAR[Home_PvPath{k}_movies]</value>")
        a("</variable>")
    a('<variable name="Home_PvPathDown">')
    a(f'\t<value condition="String.IsEmpty({pvprop("dbid")})">videodb://movies/sets/</value>')
    a(f'\t<value condition="{is_mu}">$VAR[Home_PvPathDown_albums]</value>')
    a(f'\t<value condition="{is_tv} + $EXP[Home_PvMatch] + !String.IsEmpty(Container(9201).ListItem.Property(genre.0))">$VAR[Home_PvPathDown_tvshows]</value>')
    a(f'\t<value condition="{is_tv}">$VAR[Home_PvPathDownY_tvshows]</value>')
    a(f'\t<value condition="$EXP[Home_PvMatch] + !String.IsEmpty(Container(9201).ListItem.Property(genre.0))">$VAR[Home_PvPathDown_movies]</value>')
    a("\t<value>$VAR[Home_PvPathDownY_movies]</value>")
    a("</variable>")
    # names for the four labels
    a('<variable name="Home_PvName_up"><value>$VAR[Home_PvUp]</value></variable>')
    a('<variable name="Home_PvName_right">')
    a(f'\t<value condition="{is_mu}">$INFO[{pvprop("genre")}]</value>')
    a("\t<value>$VAR[Home_PvCast0]</value>")
    a("</variable>")
    a('<variable name="Home_PvName_left">')
    a(f'\t<value condition="{is_mu}">Featured on</value>')
    a("\t<value>$VAR[Home_PvCo]</value>")
    a("</variable>")
    a('<variable name="Home_PvName_down">')
    a(f'\t<value condition="!{is_mu} + $EXP[Home_PvMatch] + !String.IsEmpty(Container(9201).ListItem.Property(genre.0))">$INFO[{pvprop("year")}]  ·  $INFO[Container(9201).ListItem.Property(genre.0)]</value>')
    a(f"\t<value>$INFO[{pvprop('year')}]</value>")
    a("</variable>")
    a(f'<expression name="Home_PvReady">!String.IsEmpty({pvprop("dbid")}) + [$EXP[Home_PvMatch] | {is_mu} | !{sv}]</expression>')
    return v


def pv_lists():
    out = []
    det = ('<control type="list" id="9201"><left>0</left><top>1079</top><width>1</width><height>1</height>'
           '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
           '<content target="videos">$VAR[Home_PvDetails]</content></control>')
    out.append(det)
    for key, var in (("up", "Up"), ("right", "Right"), ("down", "Down"), ("left", "Left"), ("p1", "P1"), ("p2", "P2"), ("p3", "P3")):
        cid = PV[key]
        out.append(f'<control type="list" id="{cid}"><left>{4 * (cid - 9200)}</left><top>1079</top><width>1</width><height>1</height>'
                   '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
                   f'<content target="videos">$VAR[Home_PvPath{var}]</content></control>')
    return out


def minimap():
    cx, top, w, h = 1380, 790, 100, 150
    ch = []
    on = "$EXP[Home_PvReady]"
    n = lambda cid, k: f"Integer.IsGreater(Container({cid}).NumItems,{k})"
    has = lambda cid: f"Integer.IsGreater(Container({cid}).NumItems,0)"

    def dot(x, y, col, vis):
        return [img(x - 12, y - 12, 24, 24, "sd/disc_18.png", diffuse="white", vis=vis),
                img(x - 12, y - 12, 24, 24, "sd/ring_18_5.png", diffuse=col, vis=vis)]

    def label(x, y, arrow, col, name_var, cid, align="left"):
        if align == "left":
            gl = f"<left>{x}</left><top>{y}</top><width>840</width><height>36</height><orientation>horizontal</orientation><align>left</align>"
        else:
            gl = f"<left>{x - 840}</left><top>{y}</top><width>840</width><height>36</height><orientation>horizontal</orientation><align>right</align>"
        return ('<control type="grouplist">' + gl + "<itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
                + img(0, 2, 32, 32, f"sd/badge_34_{arrow}.png", diffuse=col)
                + f'<control type="label"><left>10</left><width max="560">auto</width><height>36</height><font>caps_21</font><textcolor>{col}</textcolor><label>$VAR[{name_var}]</label></control>'
                + f'<control type="label"><width>auto</width><height>36</height><font>capsxb_21</font><textcolor>ink</textcolor><label>$INFO[Container({cid}).NumItems,  ·  ,]</label></control>'
                + "</control>")

    # red (up)
    red = [img(1302, 746, 54, 52, "sd/mm_up.png", diffuse="l_dir"),
           img(1001, top - 41, 1304 - 1001, 6, "sd/line_h6.png", diffuse="l_dir", border="3,0,3,0"),
           img(1001, top - 53, 6, 30, "sd/tick_v6.png", diffuse="l_dir")]
    for k in range(6):
        red += dot(1290 - k * 40, top - 38, "l_dir", n(PV["up"], k))
    red.append(label(1004, top - 108, "up", "l_dir", "Home_PvName_up", PV["up"]))
    ch.append(group(red, vis=has(PV["up"])))
    blue = [img(cx + w // 2 - 3, top + 47, 1800 - cx - w // 2 + 6, 6, "sd/line_h6.png", diffuse="l_lead", border="3,0,3,0"),
            img(1797, top + 35, 6, 30, "sd/tick_v6.png", diffuse="l_lead")]
    for k in range(9):
        blue += dot(1474 + k * 38, top + 50, "l_lead", n(PV["right"], k))
    blue.append(label(1856, top - 18, "right", "l_lead", "Home_PvName_right", PV["right"], align="right"))
    ch.append(group(blue, vis=has(PV["right"])))
    vio = [img(1268, 880, 70, 36, "sd/mm_left.png", diffuse="l_co"),
           img(1001, top + 117, 1272 - 1001, 6, "sd/line_h6.png", diffuse="l_co", border="3,0,3,0"),
           img(1001, top + 105, 6, 30, "sd/tick_v6.png", diffuse="l_co")]
    for k in range(3):
        vio += dot(1250 - k * 40, top + 120, "l_co", n(PV["left"], k))
    vio.append(label(1004, top + 140, "left", "l_co", "Home_PvName_left", PV["left"]))
    ch.append(group(vio, vis=has(PV["left"])))
    grn = [img(1404, 932, 56, 48, "sd/mm_down.png", diffuse="l_yg"),
           img(1456, top + h + 31, 1800 - 1456 + 3, 6, "sd/line_h6.png", diffuse="l_yg", border="3,0,3,0"),
           img(1797, top + h + 19, 6, 30, "sd/tick_v6.png", diffuse="l_yg")]
    for k in range(10):
        grn += dot(1474 + k * 34, top + h + 34, "l_yg", n(PV["down"], k))
    grn.append(label(1856, top + h - 34, "down", "l_yg", "Home_PvName_down", PV["down"], align="right"))
    ch.append(group(grn, vis=has(PV["down"])))
    # centre poster with its ring
    ch += [img(cx - w // 2 - 9, top - 9, w + 18, h + 18, "sd/ringf_fill.png", diffuse="ground", border="20"),
           img(cx - w // 2 - 9, top - 9, w + 18, h + 18, "sd/ring_mini.png", diffuse="ink", border="16"),
           img(cx - w // 2, top, w, h, "common/white.png", diffuse="wash"),
           '<control type="image">'
           f"<left>{cx - w // 2}</left><top>{top}</top><width>{w}</width><height>{h}</height><aspectratio>scale</aspectratio><fadetime>150</fadetime>"
           f'<texture background="true" diffuse="sd/mask_100x150.png">$INFO[{pvprop("poster")}]</texture><visible>!String.IsEqual({pvprop("kind")},albums)</visible></control>',
           '<control type="image">'
           f"<left>{cx - w // 2}</left><top>{top + (h - w) // 2}</top><width>{w}</width><height>{w}</height><aspectratio>scale</aspectratio><fadetime>150</fadetime>"
           f'<texture background="true" diffuse="sd/mask_180x180.png">$INFO[{pvprop("poster")}]</texture><visible>String.IsEqual({pvprop("kind")},albums)</visible></control>']
    anim = (f'<animation type="Visible" condition="!{RM}"><effect type="fade" start="0" end="100" time="260"/>'
            f'<effect type="zoom" start="94" end="100" center="{cx},{top + h // 2}" time="260" tween="cubic" easing="out"/></animation>'
            f'<animation type="Hidden" condition="!{RM}"><effect type="fade" start="100" end="0" time="120"/></animation>')
    return group(ch, vis=f"{on} + $EXP[Home_PvIsSelected]", anims=anim, desc="mini map")


# ------------------------------------------------------------------ top bar
NAV = {9001: (9007, 9002), 9002: (9001, 9003), 9003: (9002, 9005)}


def section_word(sec):
    s = SECTIONS[sec]
    x, tw = s["textx"], s["tw"]
    bx, bw = x - 16, tw + 32 + 10
    lid = s["list"]
    other = [SECTIONS[o]["word"] for o in SECTIONS if o != sec]
    t = [f'<control type="button" id="{s["word"]}">',
         f"<left>{bx}</left><top>62</top><width>{bw}</width><height>48</height>",
         "<font>xb_26</font><textcolor>clear</textcolor><focusedcolor>clear</focusedcolor><textoffsetx>16</textoffsetx>",
         '<texturefocus border="24" colordiffuse="ink">sd/pill_48.png</texturefocus><texturenofocus />',
         f"<label>{s['label']}</label>",
         f'<onfocus>SetProperty({P}.section,{sec},home)</onfocus>',
         f"<ondown>{lid}</ondown>",
         f"<onleft>{NAV[s['word']][0]}</onleft><onright>{NAV[s['word']][1]}</onright>",
         "</control>"]
    # visible text (weights differ for active / inactive; colour white on focus)
    t.append(lbl(x, 62, tw + 12, 48, s["label"], "xb_26", "white", vis=f"Control.HasFocus({s['word']})"))
    t.append(lbl(x, 62, tw + 12, 48, s["label"], "xb_26", "ink", vis=f"!Control.HasFocus({s['word']}) + $EXP[Home_Is_{sec}]"))
    t.append(lbl(x, 62, tw + 12, 48, s["label"], "semi_26", "ink2", vis=f"!Control.HasFocus({s['word']}) + !$EXP[Home_Is_{sec}]"))
    t.append(img(x, 116, tw, 6, "sd/line_h6.png", diffuse="ink", border="3,0,3,0", vis=f"$EXP[Home_Is_{sec}]"))
    return t


def top_bar():
    out = [img(64, 66, 44, 44, "sd/wordmark.png"), lbl(122, 64, 300, 48, "Six Degrees", "xb_28", "ink")]
    words = []
    for sec in SECTIONS:
        words += section_word(sec)
    out += words
    # right cluster: Search, Index, System (gear), clock
    def word_btn(cid, x, w, text, onclick, left, right):
        return (f'<control type="button" id="{cid}"><left>{x}</left><top>62</top><width>{w}</width><height>48</height>'
                "<font>semi_24</font><textcolor>ink2</textcolor><focusedcolor>white</focusedcolor><align>center</align><textoffsetx>0</textoffsetx>"
                '<texturefocus border="24" colordiffuse="ink">sd/pill_48.png</texturefocus><texturenofocus />'
                f"<label>{text}</label><onclick>{onclick}</onclick><onleft>{left}</onleft><onright>{right}</onright>"
                "<ondown>$VAR[Home_RowId]</ondown></control>")
    out.append(word_btn(9005, 1418, 112, "Search", "ActivateWindow(1150)", 9003, 9006))
    out.append(word_btn(9006, 1540, 96, "Index", "$VAR[Home_IndexAction]", 9005, 9007))
    out.append('<control type="button" id="9007"><left>1648</left><top>62</top><width>56</width><height>48</height>'
               '<texturefocus border="24" colordiffuse="ink">sd/pill_48.png</texturefocus><texturenofocus />'
               "<onclick>ActivateWindow(1151)</onclick><onleft>9006</onleft><onright>9001</onright><ondown>$VAR[Home_RowId]</ondown></control>")
    out.append(img(1662, 72, 28, 28, "icons/settings.png", diffuse="ink2", vis="!Control.HasFocus(9007)"))
    out.append(img(1662, 72, 28, 28, "icons/settings.png", diffuse="white", vis="Control.HasFocus(9007)"))
    out.append('<control type="label"><left>1500</left><top>62</top><width>356</width><height>48</height><font>xb_30</font>'
               "<textcolor>ink</textcolor><align>right</align><label>$INFO[System.Time]</label></control>")
    return out


def section_nav():
    # words: Left/Right chain 9001 <-> 9002 <-> 9003 -> 9005 -> 9006 -> 9007 -> 9001
    nav = {9001: (9007, 9002), 9002: (9001, 9003), 9003: (9002, 9005)}
    return nav


# ------------------------------------------------------------------ preview text + buttons
def preview_block():
    sel = "$VAR[Home_Sel]"
    ch = [lbl(64, 752, 860, 30, "Preview  ·  four lines out", "caps_21", "ink2", aligny="top"),
          lbl(60, 782, 900, 64, f"$INFO[{sel}.Label]".replace(f"$INFO[{sel}.Label]", "$VAR[Home_SelTitle]"), "disp_52", "ink"),
          lbl(64, 850, 1000, 34, "$VAR[Home_SelMeta]", "semi_24", "ink2")]

    def kbtn(cid, x, w, key, word, onclick, left, right, icon=None):
        b = [f'<control type="button" id="{cid}"><left>{x}</left><top>902</top><width>{w}</width><height>52</height>',
             '<texturefocus border="26" colordiffuse="ink">sd/pill_56.png</texturefocus><texturenofocus />',
             f"<onup>$VAR[Home_RowId]</onup><onleft>{left}</onleft><onright>{right}</onright><onback>$VAR[Home_RowId]</onback>"]
        b += [tag("onclick", a[0], a[1]) if isinstance(a, tuple) else f"<onclick>{a}</onclick>" for a in onclick]
        b.append("</control>")
        foc = f"Control.HasFocus({cid})"
        kx = x + 12
        kw = 44 if len(key) <= 2 else 70
        # key cap (outline ink / white on focus) + word
        kc = [img(kx, 910, kw, 36, "sd/key.png", diffuse="ink", border="12", vis=f"!{foc}"),
              img(kx, 910, kw, 36, "sd/key.png", diffuse="white", border="12", vis=foc)]
        if icon:
            kc += [img(kx + kw // 2 - 10, 918, 20, 20, icon, diffuse="ink", vis=f"!{foc}"),
                   img(kx + kw // 2 - 10, 918, 20, 20, icon, diffuse="white", vis=foc)]
        else:
            kc += [lbl(kx, 910, kw, 36, key, "xb_19", "ink", align="center", vis=f"!{foc}"),
                   lbl(kx, 910, kw, 36, key, "xb_19", "white", align="center", vis=foc)]
        kc += [lbl(kx + kw + 12, 902, w - kw - 36, 52, word, "semi_22", "ink2", vis=f"!{foc}"),
               lbl(kx + kw + 12, 902, w - kw - 36, 52, word, "semi_22", "white", vis=foc)]
        return ["\n".join(b)] + kc

    def pbtn(cid, x, w, word, onclick, left, right, icon=None):
        """Real buttons (Down from the start line, then OK): outline pills, ink when focused. The Shield
        remote has no Info key, so no key cap pretends there is one (producer review 0.9.1)."""
        b = [f'<control type="button" id="{cid}"><left>{x}</left><top>902</top><width>{w}</width><height>52</height>',
             '<texturefocus border="26" colordiffuse="ink">sd/pill_56.png</texturefocus>',
             '<texturenofocus border="26" colordiffuse="hair_strong">sd/pill_56_o3.png</texturenofocus>',
             f"<onup>$VAR[Home_RowId]</onup><onleft>{left}</onleft><onright>{right}</onright><onback>$VAR[Home_RowId]</onback>"]
        b += [tag("onclick", a[0], a[1]) if isinstance(a, tuple) else f"<onclick>{a}</onclick>" for a in onclick]
        b.append("</control>")
        foc = f"Control.HasFocus({cid})"
        tx = x + 24
        kc = []
        if icon:
            kc += [img(tx, 918, 20, 20, icon, diffuse="ink", vis=f"!{foc}"), img(tx, 918, 20, 20, icon, diffuse="white", vis=foc)]
            tx += 30
        kc += [lbl(tx, 902, w - (tx - x) - 16, 52, word, "semi_22", "ink", vis=f"!{foc}"),
               lbl(tx, 902, w - (tx - x) - 16, 52, word, "semi_22", "white", vis=foc)]
        return ["\n".join(b)] + kc

    # 0.9.2: SendClick(<start list>) from this button boarded with an EMPTY centre ($INFO[ListItem.*] in the
    # list's onclick resolves against the focused control = this button). Board straight from the list's item.
    board = []
    for sec_, s_ in SECTIONS.items():
        src = f"Container({s_['list']}).ListItem"
        board += [(a, f"$EXP[Home_Is_{sec_}] + String.IsEmpty({src}.Property(terminus)) + !String.IsEmpty({src}.Property(dbid))")
                  for a in board_actions(src, sec_)]
    ch += kbtn(9151, 52, 232, "OK", "board the map", board, 9153, 9152)
    ch += pbtn(9152, 300, 120, "Play", ["$VAR[Home_PlayClick]"], 9151, 9153, icon="sd/tri_right.png")
    # 0.9.2: SetFocus(<list>,1,absolute) never moved the hidden 1-px data list on the Shield (the second
    # starter of a pair opened nothing). Focus the data list, rewind it with Control.Move (wraps), step to the item.
    info = []
    for sec_, s_ in SECTIONS.items():
        d_ = DATA[sec_]
        plan = [(d_[0][0], 0), (d_[0][0], 1), (d_[1][0], 0), (d_[2][0], 0), (d_[2][0], 1), (d_[3][0], 0)]
        # ListItemAbsolute(n) must be the FIRST argument: as the second one Kodi 21 compares against the
        # literal text, so the match was always false (device probe 2026-10-19)
        conds = [f'$EXP[Home_Is_{sec_}] + String.IsEqual(Container({src}).ListItemAbsolute({idx}).{"TvShowDBID" if src == 9122 else "DBID"},'
                 f'Container({s_["list"]}).ListItem.Property(dbid))' for src, idx in plan]
        for k, (src, idx) in enumerate(plan):
            cond = conds[k] + "".join(f" + ![{c}]" for c in conds[:k])
            acts = [f"SetFocus({src})", f"Control.Move({src},-$INFO[Container({src}).CurrentItem])", f"Control.Move({src},1)"]
            if idx:
                acts.append(f"Control.Move({src},{idx})")
            info += [(a, cond) for a in acts]
    info += ["Action(Info)", "SetFocus(9153)"]
    ch += pbtn(9153, 436, 196, "Station page", info, 9152, 9151)
    ch.append(lbl(652, 902, 360, 52, "▼ then OK", "semi_22", "ink3",
                  vis="!Control.HasFocus(9151) + !Control.HasFocus(9152) + !Control.HasFocus(9153)"))
    return group(ch, vis="!$EXP[Home_SelIsTerminus]", desc="preview")


def index_preview():
    return group([lbl(64, 752, 860, 30, "The terminus", "caps_21", "ink2", aligny="top"),
                  lbl(60, 782, 900, 64, "Index", "disp_52", "ink"),
                  lbl(64, 850, 1100, 34, "$VAR[Home_IndexMeta]", "semi_24", "ink2")],
                 vis="$EXP[Home_SelIsTerminus]", desc="index preview")


def home_variables():
    v = []
    a = v.append
    for sec in SECTIONS:
        a(f'<expression name="Home_Is_{sec}">' + (
            f"String.IsEqual({prop('section')},{sec})" if sec != "movies"
            else f"!String.IsEqual({prop('section')},tvshows) + !String.IsEqual({prop('section')},music)") + "</expression>")
    a('<variable name="Home_RowId">')
    for sec, s in SECTIONS.items():
        a(f'\t<value condition="$EXP[Home_Is_{sec}]">SetFocus({s["list"]})</value>')
    a("</variable>")
    a('<variable name="Home_Sel">')
    a("\t<value>unused</value>")
    a("</variable>")
    for fld, expr in (("Title", "Label"), ("Dbid", "Property(dbid)"), ("Why", "Property(why)"), ("Dir", "Property(dir)"),
                      ("Year", "Property(year)"), ("Icon", "Icon"), ("Kind", "Property(kind)"), ("Tmdb", "Property(tmdb)"),
                      ("Genre", "Property(genre)"), ("File", "Property(file)")):
        a(f'<variable name="Home_Sel{fld}">')
        for sec, s in SECTIONS.items():
            a(f'\t<value condition="$EXP[Home_Is_{sec}]">$INFO[Container({s["list"]}).ListItem.{expr}]</value>')
        a("</variable>")
    a('<expression name="Home_SelIsTerminus">' + " | ".join(
        f"[$EXP[Home_Is_{sec}] + !String.IsEmpty(Container({s['list']}).ListItem.Property(terminus))]" for sec, s in SECTIONS.items()) + "</expression>")
    a(f'<expression name="Home_PvIsSelected">' + " | ".join(
        f"[$EXP[Home_Is_{sec}] + String.IsEqual(Container({s['list']}).ListItem.Property(dbid),{pvprop('dbid')})"
        f" + String.IsEqual(Container({s['list']}).ListItem.Property(kind),{pvprop('kind')})]" for sec, s in SECTIONS.items()) + "</expression>")
    # meta line under the preview title
    a('<variable name="Home_SelMeta">')
    for sec, s in SECTIONS.items():
        li = f"Container({s['list']}).ListItem"
        is_ = f"$EXP[Home_Is_{sec}]"
        if sec == "music":
            a(f'\t<value condition="{is_}">$INFO[{li}.Property(dir)]$INFO[{li}.Property(year),  ·  ,]$INFO[{li}.Property(genre),  ·  ,]</value>')
        elif sec == "tvshows":
            a(f'\t<value condition="{is_}">$INFO[{li}.Property(dir)]$INFO[{li}.Property(year),  ·  ,]$INFO[{li}.Property(why),  ·  ,]</value>')
        else:
            a(f'\t<value condition="{is_} + !String.IsEmpty({li}.Property(star))">$INFO[{li}.Property(dir)]$INFO[{li}.Property(year),  ·  ,]  ·  never watched  ·  1 of $INFO[Container(9105).NumItems] unwatched 7.5+</value>')
            a(f'\t<value condition="{is_}">$INFO[{li}.Property(dir)]$INFO[{li}.Property(year),  ·  ,]$INFO[{li}.Property(why),  ·  ,]</value>')
    a("</variable>")
    a('<variable name="Home_IndexAction">')
    a('\t<value condition="$EXP[Home_Is_tvshows]">ActivateWindow(Videos,videodb://tvshows/titles/,return)</value>')
    a('\t<value condition="$EXP[Home_Is_music]">ActivateWindow(Music,musicdb://albums/,return)</value>')
    a("\t<value>ActivateWindow(Videos,videodb://movies/titles/,return)</value>")
    a("</variable>")
    a('<variable name="Home_IndexMeta">')
    a('\t<value condition="$EXP[Home_Is_tvshows]">Every series, A to Z  ·  $INFO[Container(9126).NumItems] series</value>')
    a('\t<value condition="$EXP[Home_Is_music]">Every album, A to Z  ·  $INFO[Container(9136).NumItems] albums</value>')
    a("\t<value>Every film, A to Z  ·  $INFO[Container(9106).NumItems] films</value>")
    a("</variable>")
    # buttons under the preview act on the selected starter
    a('<variable name="Home_BoardClick">')
    for sec, s_ in SECTIONS.items():
        a(f'	<value condition="$EXP[Home_Is_{sec}]">SendClick({s_["list"]})</value>')
    a("</variable>")
    a('<variable name="Home_PlayClick">')
    a('	<value condition="$EXP[Home_Is_music]">PlayMedia(musicdb://albums/$INFO[Container(9130).ListItem.Property(dbid)]/,isdir)</value>')
    a('	<value condition="$EXP[Home_Is_tvshows]">ActivateWindow(Videos,videodb://tvshows/titles/$INFO[Container(9120).ListItem.Property(dbid)]/,return)</value>')
    a("	<value>PlayMedia($ESCINFO[Container(9110).ListItem.Property(file)],resume)</value>")
    a("</variable>")
    # station page = Kodi info on the hidden data list item behind the selected starter
    a('<variable name="Home_InfoFocus">')
    for sec, s in SECTIONS.items():
        d = DATA[sec]
        plan = [(d[0][0], 0), (d[0][0], 1), (d[1][0], 0), (d[2][0], 0), (d[2][0], 1), (d[3][0], 0)]
        for src, idx in plan:
            a(f'\t<value condition="$EXP[Home_Is_{sec}] + String.IsEqual(Container({s["list"]}).ListItem.Property(dbid),Container({src}).ListItemAbsolute({idx}).{"TvShowDBID" if src == 9122 else "DBID"})">SetFocus({src},{idx},absolute)</value>')
    a("</variable>")
    # "added 4 Oct" from the region date (dd/mm/yyyy on Omar's box; other formats fall back to the raw date)
    da = "Container(9102).ListItemAbsolute(0).DateAdded"
    a('<variable name="Home_AddedDay">')
    for d in range(1, 32):
        a(f'	<value condition="String.StartsWith({da},{d:02d}/)">[UPPERCASE]{d}[/UPPERCASE]</value>')
    a(f"	<value>$INFO[{da}]</value>")
    a("</variable>")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    a('<variable name="Home_AddedMonth">')
    for i, m in enumerate(months, 1):
        a(f'	<value condition="String.StartsWith({da},0) + String.Contains({da},/{i:02d}/) | !String.StartsWith({da},0) + String.Contains({da},/{i:02d}/)">{m}</value>')
    a("</variable>")
    for src in (9104,):
        li = f"Container({src}).ListItemAbsolute(0)"
        a(f'<variable name="Home_Time_{src}">')
        a(f'	<value condition="Integer.IsGreater({li}.Duration(h),0)">$INFO[{li}.Duration(h),, h ]$INFO[{li}.Duration(mm)]</value>')
        a(f'	<value>$INFO[{li}.Duration(m),, min]</value>')
        a("</variable>")
    for src in (9124,):
        li = f"Container({src}).ListItemAbsolute(0)"
        a(f'<variable name="Home_Seasons_{src}"><value condition="Integer.IsEqual({li}.Property(TotalSeasons),1)">1 season</value>'
          f'<value>$INFO[{li}.Property(TotalSeasons),, seasons]</value></variable>')
    a('<variable name="Home_Sub">')
    a('	<value condition="$EXP[Home_Is_tvshows]">Pick a first series. From there, every direction on the remote is a connection.</value>')
    a('	<value condition="$EXP[Home_Is_music]">Pick a first album. From there, every direction on the remote is a connection.</value>')
    a("	<value>Pick a first station. From there, every direction on the remote is a connection.</value>")
    a("</variable>")
    return v


IS_SEC = {"movies": f"!String.IsEqual({prop('section')},tvshows) + !String.IsEqual({prop('section')},music)",
          "tvshows": f"String.IsEqual({prop('section')},tvshows)", "music": f"String.IsEqual({prop('section')},music)"}


def timers():
    t = ['<?xml version="1.0" encoding="UTF-8"?>',
         "<!-- GENERATED by _src/make_home.py. The Home preview loads after focus rests 1 s on a starter:",
         "     the timer copies the selected starter into sixdegrees.pv.* (the hidden lists 92xx follow). -->",
         "<timers>"]
    for sec, s in SECTIONS.items():
        li = f"Container({s['list']}).ListItem"
        # 0.9.7: films, series and albums have separate id ranges (film 12 and show 12 are different
        # items), so "already previewed" must match the kind as well as the dbid
        same = (f"[String.IsEqual({li}.Property(dbid),{pvprop('dbid')}) + "
                f"String.IsEqual({li}.Property(kind),{pvprop('kind')})]")
        mismatch = (f"[!String.IsEqual({li}.Property(dbid),{pvprop('dbid')}) | "
                    f"!String.IsEqual({li}.Property(kind),{pvprop('kind')})]")
        t += ["\t<timer>",
              f"\t\t<name>sd_preview_{sec}</name>",
              f"\t\t<start reset=\"false\">Window.IsActive(home) + {IS_SEC[sec]} + System.IdleTime(1) + String.IsEmpty({li}.Property(terminus)) + !String.IsEmpty({li}.Property(dbid)) + {mismatch}</start>",
              f"\t\t<stop>{same} | !Window.IsActive(home)</stop>",
              f"\t\t<onstart>SetProperty({P}.pv.title,$ESCINFO[{li}.Label],home)</onstart>",
              f"\t\t<onstart>SetProperty({P}.pv.year,$INFO[{li}.Property(year)],home)</onstart>",
              f"\t\t<onstart>SetProperty({P}.pv.dir,$ESCINFO[{li}.Property(dir)],home)</onstart>",
              f"\t\t<onstart>SetProperty({P}.pv.genre,$ESCINFO[{li}.Property(genre)],home)</onstart>",
              f"\t\t<onstart>SetProperty({P}.pv.poster,$ESCINFO[{li}.Icon],home)</onstart>",
              f"\t\t<onstart>SetProperty({P}.pv.kind,$INFO[{li}.Property(kind)],home)</onstart>",
              f"\t\t<onstart>SetProperty({P}.pv.dbid,$INFO[{li}.Property(dbid)],home)</onstart>",
              "\t</timer>"]
    # arriving on Home: the static starters appear one by one as their data lists load, and the list can be left
    # holding the Index terminus (the only item that existed at first). Once starters exist, focus the first.
    for sec, s_ in SECTIONS.items():
        lid = s_["list"]
        t += ["	<timer>", f"		<name>sd_homeinit_{sec}</name>",
              f"		<start reset=\"false\">Window.IsActive(home) + {IS_SEC[sec]} + String.IsEmpty({prop('homeinit')}) + Integer.IsGreater(Container({lid}).NumItems,1)</start>",
              f"		<stop>!String.IsEmpty({prop('homeinit')}) | !Window.IsActive(home)</stop>",
              f"		<onstart condition=\"!String.IsEmpty(Container({lid}).ListItem.Property(terminus)) + Control.HasFocus({lid})\">SetFocus({lid},0,absolute)</onstart>",
              f"		<onstart>SetProperty({P}.homeinit,1,home)</onstart>", "	</timer>"]
    t += map_timers()
    t.append("</timers>")
    return "\n".join(t) + "\n"


def now_playing():
    """Top bar, between the section words and Search: what is playing (not focusable)."""
    ch = [img(790, 64, 44, 44, "common/white.png", diffuse="wash"),
          '<control type="image"><left>790</left><top>64</top><width>44</width><height>44</height><aspectratio>scale</aspectratio>'
          '<texture background="true" diffuse="sd/mask_180x180.png">$INFO[Player.Art(thumb)]</texture></control>',
          lbl(848, 60, 540, 24, "Now playing", "caps_20", "ink2", aligny="top"),
          lbl(848, 82, 540, 30, "$INFO[Player.Title]$INFO[MusicPlayer.Artist,  ·  ,]", "semi_22", "ink")]
    return group(ch, vis="Player.HasMedia", desc="now playing")


def includes():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_home.py - edit the generator. Home = Start somewhere (see its docstring). -->",
             "<includes>"]
    parts += ["\t" + x for x in "\n".join(home_variables() + pv_variables()).split("\n")]

    def inc(name, body):
        parts.append(f'\t<include name="{name}">')
        parts.extend("\t\t" + x for x in "\n".join(body).split("\n"))
        parts.append("\t</include>")

    inc("Home_DataLists", data_lists() + pv_lists())
    inc("Home_TopBar", top_bar())
    inc("Home_Headline", [lbl(60, 140, 900, 96, "Start somewhere", "disp_76", "ink"),
                          '<control type="textbox"><left>720</left><top>176</top><width>1040</width><height>70</height>'
                          "<font>reg_26</font><textcolor>ink2</textcolor><label>$VAR[Home_Sub]</label></control>"])
    inc("Home_StartLines", [start_list(sec) for sec in SECTIONS])
    inc("Home_Preview", [preview_block(), index_preview(), minimap()])
    inc("Home_NowPlaying", [now_playing()])
    # kept for Search (Includes_Search.xml): poster/cover art with fallback
    parts.append('''	<include name="Home_Art">
		<param name="diffuse">white</param>
		<param name="mask_round">sd/mask_184x276.png</param>
		<param name="mask_square">sd/mask_184x276.png</param>
		<param name="title">$INFO[ListItem.Label]</param>
		<definition>
			<control type="image"><left>0</left><top>0</top><right>0</right><bottom>0</bottom><texture colordiffuse="wash">common/white.png</texture></control>
			<control type="textbox"><left>12</left><right>12</right><top>12</top><height>90</height><font>semi_22</font><textcolor>ink2</textcolor><label>$PARAM[title]</label></control>
			<control type="image"><left>0</left><top>0</top><right>0</right><bottom>0</bottom><aspectratio>scale</aspectratio><fadetime>150</fadetime>
				<texture background="true" diffuse="$PARAM[mask_round]" colordiffuse="$PARAM[diffuse]">$PARAM[art]</texture></control>
		</definition>
	</include>''')
    parts.append("</includes>")
    (OUT / "Includes_Home.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


def home_window():
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_home.py. Home = "Start somewhere" (board SixDegreesHome).
	Focus: words 9001 Movies / 9002 Series / 9003 Music, 9005 Search, 9006 Index, 9007 System;
	start lines 9110 / 9120 / 9130 (OK = board the map); buttons 9151 board / 9152 play / 9153 station page.
	Back: buttons -> start line -> section word (Home has nowhere further to go, Kodi keeps it).
-->
<window>
	<defaultcontrol always="true">9110</defaultcontrol>
	<menucontrol>9001</menucontrol>
	<backgroundcolor>ground</backgroundcolor>
	<onload condition="$EXP[Home_Is_tvshows]">SetFocus(9120)</onload>
	<onload condition="$EXP[Home_Is_music]">SetFocus(9130)</onload>
	<onload>SetProperty({P}.reload,$INFO[System.Time(hh:mm:ss)],home)</onload>
	<onload>ClearProperty({P}.homeinit,home)</onload>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>SD_Background</include>
		<include>Home_DataLists</include>
		<include>Home_Headline</include>
		<include>Home_StartLines</include>
		<include>Home_Preview</include>
		<include>Home_NowPlaying</include>
		<include>Home_TopBar</include>
	</controls>
</window>
"""
    (OUT / "Home.xml").write_text(w, encoding="utf-8")


if __name__ == "__main__":
    includes()
    home_window()
    (OUT / "Timers.xml").write_text(timers(), encoding="utf-8")
    print("wrote Home.xml, Includes_Home.xml, Timers.xml")
