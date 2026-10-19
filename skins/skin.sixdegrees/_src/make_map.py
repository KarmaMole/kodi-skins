"""Six Degrees: the map (signature mechanic) -> 1080i/Includes_Map.xml + 1080i/Custom_1160_Map.xml.

Geometry is the board geometry (docs/concepts/round4/mockups/sixdegrees/boards.py, board_map / board_hop).

HOW IT WORKS (see docs/skin.sixdegrees/SPEC.md section 3)
- The centre is a set of Window(Home) properties `sixdegrees.c.*` (dbid, title, year, poster, dir, tmdb, file,
  col) written when a station becomes the centre. `sixdegrees.kind` = movies | tvshows.
- 9001 = script.skinvariables `get_dbitem_<kind>_details&dbid=` (Kodi's own library, no network): billed cast
  as ListItem.Property(cast.N.name) (0 = lead), director.0 / studio.0, genre.0 (the first genre).
  9002 = TMDb Helper `info=details` (fallback for the cast when skinvariables is missing; cast.N.name, 1-based).
- Four line DRIVERS 611 (up), 612 (right), 613 (down), 614 (left): invisible horizontal lists whose
  <content> is a videodb xsp path built from the centre (director / lead actor / year + first genre /
  second star), sorted by rating. Probes 621-623 count the films of billed cast 2-4 (second star = the
  first with >= 2 other films).
- Focus never sits on a list: 700 (centre) and 701-704 (one invisible button per line) take the d-pad and
  drive the lists with Control.Move. Static slots draw the stations from Container(id).ListItemPosition(k),
  so lines can run left, grow a roundel and shift posters without fighting Kodi's list layout.
- OK on a station re-centres: route push (8 slots `sixdegrees.r1..r8.*`), centre <- station, the centre poster
  slides in from the station's side (A/B flip so the Visible animation replays), the lines fade out while
  they reload and draw out again when ready. Back pops the route (799, a hidden-focus button) or leaves.

    python skins/skin.sixdegrees/_src/make_map.py
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i"

P = "sixdegrees"
H = f"Window(Home).Property({P}"


def prop(name):
    return f"Window(Home).Property({P}.{name})"


def info(name):
    return f"$INFO[{prop(name)}]"


RM = f"Skin.HasSetting({P}.reducemotion)"
ALBUMS = f"String.IsEqual(Window(Home).Property({P}.kind),albums)"
FIELDS = ["dbid", "title", "year", "poster", "dir", "genre", "tmdb", "file", "col"]
DEPTH = 8

# line ids, colours, slots
LINES = {
    "up": dict(lst=611, btn=701, col="l_dir", key="dir", k=3, y=190, xs=[690, 440, 190], dots=True),
    "right": dict(lst=612, btn=702, col="l_lead", key="lead", k=4, y=430, xs=[1214, 1354, 1494, 1634], dots=False),
    "down": dict(lst=613, btn=703, col="l_yg", key="yg", k=3, y=920, xs=[1236, 1440, 1644], dots=True),
    "left": dict(lst=614, btn=704, col="l_co", key="co", k=4, y=590, xs=[636, 494, 352, 210], dots=False),
}
ARROW = {"up": "up", "right": "right", "down": "down", "left": "left"}

# ------------------------------------------------------------------ url pieces (static parts encoded)
OPEN = "%7B%22rules%22%3A%7B%22and%22%3A%5B"


def rule(field, op, value):
    return (f"%7B%22field%22%3A%22{field}%22%2C%22operator%22%3A%22{op}%22%2C%22value%22%3A%5B%22"
            f"{value}%22%5D%7D")


def close(typ):
    return f"%5D%7D%2C%22type%22%3A%22{typ}%22%7D"


ROOT = {"movies": "videodb://movies/titles/?xsp=", "tvshows": "videodb://tvshows/titles/?xsp=", "albums": "musicdb://albums/?xsp="}
UPFIELD = {"movies": "director", "tvshows": "studio"}
READY = f"$EXP[Map_Ready]"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ variables
def variables():
    v = []
    a = v.append
    is_tv = f"String.IsEqual({prop('kind')},tvshows)"
    sv = "System.AddonIsEnabled(script.skinvariables)"
    tm = "System.AddonIsEnabled(plugin.video.themoviedb.helper)"
    a("<!-- ============================================================ data sources -->")
    a('<variable name="Map_DetailsPath">')
    a(f'\t<value condition="{sv} + {is_tv} + !String.IsEmpty({prop("c.dbid")})">plugin://script.skinvariables/?info=get_dbitem_tvshow_details&amp;dbid={info("c.dbid")}</value>')
    a(f'\t<value condition="{sv} + !String.IsEmpty({prop("c.dbid")})">plugin://script.skinvariables/?info=get_dbitem_movie_details&amp;dbid={info("c.dbid")}</value>')
    a("</variable>")
    a('<variable name="Map_TMDbPath">')
    a(f'\t<value condition="!{sv} + {tm} + {is_tv} + !String.IsEmpty({prop("c.tmdb")})">plugin://plugin.video.themoviedb.helper/?info=details&amp;tmdb_type=tv&amp;tmdb_id={info("c.tmdb")}</value>')
    a(f'\t<value condition="!{sv} + {tm} + !String.IsEmpty({prop("c.tmdb")})">plugin://plugin.video.themoviedb.helper/?info=details&amp;tmdb_type=movie&amp;tmdb_id={info("c.tmdb")}</value>')
    a("</variable>")
    d_ok = "$EXP[Map_DetailsMatch]"
    t_ok = "$EXP[Map_TMDbMatch]"
    # up value: first director (movies) / first network (tv); raw centre value until details arrive
    a('<variable name="Map_UpName">')
    a(f'\t<value condition="{d_ok} + {is_tv}">$INFO[Container(9001).ListItem.Property(studio.0)]</value>')
    a(f'\t<value condition="{d_ok}">$INFO[Container(9001).ListItem.Property(director.0)]</value>')
    a(f'\t<value>{info("c.dir")}</value>')
    a("</variable>")
    for n in range(4):
        a(f'<variable name="Map_Cast{n}">')
        a(f'\t<value condition="{d_ok}">$INFO[Container(9001).ListItem.Property(cast.{n}.name)]</value>')
        a(f'\t<value condition="{t_ok}">$INFO[Container(9002).ListItem.Property(cast.{n + 1}.name)]</value>')
        a("</variable>")
    a('<variable name="Map_Genre">')
    a(f'\t<value condition="{d_ok}">$INFO[Container(9001).ListItem.Property(genre.0)]</value>')
    a("</variable>")
    # second star: next billed actor with >= 2 other films (probes 621-623 = cast 1-3)
    a('<variable name="Map_CoName">')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(621).NumItems,2)">$VAR[Map_Cast1]</value>')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(622).NumItems,2)">$VAR[Map_Cast2]</value>')
    a('\t<value condition="Integer.IsGreaterOrEqual(Container(623).NumItems,2)">$VAR[Map_Cast3]</value>')
    a("\t<value>$VAR[Map_Cast1]</value>")
    a("</variable>")
    # exclusion of the centre (title isnot). A raw '&' would split the URL options, so titles with '&' skip it
    a('<variable name="Map_Excl">')
    a(f'\t<value condition="!String.Contains({prop("c.title")},&amp;)">%2C{rule("title", "isnot", info("c.title"))}</value>')
    a("</variable>")
    a('<variable name="Map_Unwatched">')
    a(f'\t<value condition="Skin.HasSetting({P}.map.unwatched)">%2C{rule("playcount", "is", "0")}</value>')
    a("</variable>")
    a('<variable name="Map_SortBy">')
    a(f'\t<value condition="String.IsEqual(Skin.String({P}.map.sort),year)">year</value>')
    a("\t<value>rating</value>")
    a("</variable>")
    # paths per kind
    for kind in ("movies", "tvshows"):
        tail = f"$VAR[Map_Excl]$VAR[Map_Unwatched]{close(kind)}"
        up = f"{ROOT[kind]}{OPEN}{rule(UPFIELD[kind], 'is', '$VAR[Map_UpName]')}{tail}"
        lead = f"{ROOT[kind]}{OPEN}{rule('actor', 'is', '$VAR[Map_Cast0]')}{tail}"
        co = f"{ROOT[kind]}{OPEN}{rule('actor', 'is', '$VAR[Map_CoName]')}{tail}"
        yg = f"{ROOT[kind]}{OPEN}{rule('year', 'is', info('c.year'))}%2C{rule('genre', 'is', '$VAR[Map_Genre]')}{tail}"
        yonly = f"{ROOT[kind]}{OPEN}{rule('year', 'is', info('c.year'))}{tail}"
        probes = [f"{ROOT[kind]}{OPEN}{rule('actor', 'is', f'$VAR[Map_Cast{n}]')}{tail}" for n in (1, 2, 3)]
        tvc = f"String.IsEqual({prop('kind')},tvshows)" if kind == "tvshows" else f"!String.IsEqual({prop('kind')},tvshows)"
        for name, path in (("Up", up), ("Right", lead), ("Left", co)):
            a(f'<variable name="Map_Path{name}_{kind}"><value>{path}</value></variable>')
        a(f'<variable name="Map_PathDown_{kind}">')
        a(f'\t<value condition="{d_ok} + !String.IsEmpty(Container(9001).ListItem.Property(genre.0))">{yg}</value>')
        a(f"\t<value>{yonly}</value>")
        a("</variable>")
        for n, pth in zip((1, 2, 3), probes):
            a(f'<variable name="Map_PathProbe{n}_{kind}"><value>{pth}</value></variable>')
    R = ROOT["albums"]
    excl_alb = f"$VAR[Map_ExclAlbum]{close('albums')}"
    a(f'<variable name="Map_ExclAlbum"><value condition="!String.Contains({prop("c.title")},&amp;)">%2C{rule("album", "isnot", info("c.title"))}</value></variable>')
    a(f'<variable name="Map_PathUp_albums"><value>{R}{OPEN}{rule("albumartist", "is", info("c.dir"))}{excl_alb}</value></variable>')
    a(f'<variable name="Map_PathRight_albums"><value>{R}{OPEN}{rule("genre", "is", info("c.genre"))}{excl_alb}</value></variable>')
    a(f'<variable name="Map_PathDown_albums"><value>{R}{OPEN}{rule("year", "is", info("c.year"))}{excl_alb}</value></variable>')
    a(f'<variable name="Map_PathLeft_albums"><value>{R}{OPEN}{rule("artist", "is", info("c.dir"))}%2C{rule("albumartist", "isnot", info("c.dir"))}{excl_alb}</value></variable>')
    for name in ("Up", "Right", "Down", "Left", "Probe1", "Probe2", "Probe3"):
        a(f'<variable name="Map_Path{name}">')
        if name in ("Up", "Right", "Down", "Left"):
            a(f'\t<value condition="String.IsEqual({prop("kind")},albums)">$VAR[Map_Path{name}_albums]</value>')
        a(f'\t<value condition="String.IsEqual({prop("kind")},tvshows)">$VAR[Map_Path{name}_tvshows]</value>')
        a(f"\t<value>$VAR[Map_Path{name}_movies]</value>")
        a("</variable>")

    a("<!-- ============================================================ labels -->")
    alb = f"String.IsEqual({prop('kind')},albums)"
    a(f'<variable name="Map_LineName_up"><value condition="{alb}">{info("c.dir")}</value><value>$VAR[Map_UpName]</value></variable>')
    a(f'<variable name="Map_LineName_right"><value condition="{alb}">{info("c.genre")}</value><value>$VAR[Map_Cast0]</value></variable>')
    a(f'<variable name="Map_LineName_left"><value condition="{alb}">Featured on</value><value>$VAR[Map_CoName]</value></variable>')
    a('<variable name="Map_LineName_down">')
    a(f'\t<value condition="{alb}">{info("c.year")}</value>')
    a(f'\t<value condition="{d_ok} + !String.IsEmpty(Container(9001).ListItem.Property(genre.0))">{info("c.year")} · $INFO[Container(9001).ListItem.Property(genre.0)]</value>')
    a(f"\t<value>{info('c.year')}</value>")
    a("</variable>")
    a('<variable name="Map_LineKind_up">')
    a(f'\t<value condition="{is_tv}">network</value>')
    a("\t<value>director</value>")
    a("</variable>")
    a('<variable name="Map_LineKind_right"><value>lead</value></variable>')
    a('<variable name="Map_LineKind_left"><value>second star</value></variable>')
    a('<variable name="Map_LineKind_down"><value>year + genre</value></variable>')
    for ln, d in LINES.items():
        lst = d["lst"]
        a(f'<variable name="Map_Count_{ln}">')
        a(f'\t<value condition="Control.HasFocus({d["btn"]})"> · $INFO[Container({lst}).CurrentItem] of $INFO[Container({lst}).NumItems]</value>')
        a(f"\t<value> · $INFO[Container({lst}).NumItems]</value>")
        a("</variable>")
        a(f'<variable name="Map_More_{ln}">')
        for n in range(d["k"] + 1, 400):
            a(f'\t<value condition="Integer.IsEqual(Container({lst}).NumItems,{n})">+{n - d["k"]}</value>')
        a("\t<value>+</value>")
        a("</variable>")

    # route colours
    a("<!-- ============================================================ route -->")
    for s in ["c"] + [f"r{i}" for i in range(1, DEPTH + 1)]:
        a(f'<variable name="Map_Col_{s}">')
        for kw, col in (("dir", "l_dir"), ("lead", "l_lead"), ("yg", "l_yg"), ("co", "l_co")):
            a(f'\t<value condition="String.IsEqual({prop(s + ".col")},{kw})">{col}</value>')
        a("\t<value>l_route</value>")
        a("</variable>")
    a('<variable name="Map_FlipNext">')
    a(f'\t<value condition="String.IsEqual({prop("flip")},a)">b</value>')
    a("\t<value>a</value>")
    a("</variable>")
    a('<variable name="Map_BackHint">')
    a(f'\t<value condition="!String.IsEmpty({prop("r1.dbid")})">{info("r1.title")}</value>')
    a("\t<value>home</value>")
    a("</variable>")

    # centre facts
    a("<!-- ============================================================ centre + next stop -->")
    a('<variable name="Map_CentrePoster">')
    a(f'\t<value condition="{d_ok} + !String.IsEmpty(Container(9001).ListItem.Art(poster))">$INFO[Container(9001).ListItem.Art(poster)]</value>')
    a(f"\t<value>{info('c.poster')}</value>")
    a("</variable>")
    a('<variable name="Map_CentreMeta">')
    a(f'\t<value condition="{d_ok} + {is_tv} + Integer.IsEqual(Container(9001).ListItem.Property(totalseasons),1)">$INFO[Container(9001).ListItem.Year,, · ]$INFO[Container(9001).ListItem.Property(studio.0),, · ]1 season</value>')
    a(f'\t<value condition="{d_ok} + {is_tv}">$INFO[Container(9001).ListItem.Year,, · ]$INFO[Container(9001).ListItem.Property(studio.0),, · ]$INFO[Container(9001).ListItem.Property(totalseasons),, seasons]</value>')
    a(f'\t<value condition="{d_ok} + Integer.IsGreater(Container(9001).ListItem.Duration(h),0)">$INFO[Container(9001).ListItem.Year,, · ]$INFO[Container(9001).ListItem.Property(director.0),, · ]$INFO[Container(9001).ListItem.Duration(h),, h ]$INFO[Container(9001).ListItem.Duration(mm)]</value>')
    a(f'\t<value condition="{d_ok}">$INFO[Container(9001).ListItem.Year,, · ]$INFO[Container(9001).ListItem.Property(director.0),, · ]$INFO[Container(9001).ListItem.Duration(m),, min]</value>')
    a(f'\t<value condition="String.IsEqual({prop("kind")},albums)">{info("c.year")}$INFO[{prop("c.dir")}, · ,]$INFO[{prop("c.genre")}, · ,]</value>')
    a(f"\t<value>{info('c.year')}$INFO[{prop('c.dir')}, · ,]</value>")
    a("</variable>")
    a('<variable name="Map_CentreFile">')
    a(f'\t<value condition="{d_ok} + !String.IsEmpty(Container(9001).ListItem.Property(file))">$INFO[Container(9001).ListItem.Property(file)]</value>')
    a(f"\t<value>{info('c.file')}</value>")
    a("</variable>")
    # next stop: the focused station of the focused line (or the centre)
    src = {ln: f"Container({d['lst']}).ListItem" for ln, d in LINES.items()}
    for fld in ("Title", "Plot", "Year", "Rating", "Director", "Studio"):
        a(f'<variable name="Map_NS_{fld}">')
        if fld == "Title":
            for ln, d in LINES.items():
                a(f'\t<value condition="Control.HasFocus({d["btn"]}) + String.IsEqual({prop("kind")},albums)">$INFO[{src[ln]}.Label]</value>')
        for ln, d in LINES.items():
            a(f'\t<value condition="Control.HasFocus({d["btn"]})">$INFO[{src[ln]}.{fld}]</value>')
        if fld in ("Title",):
            a(f"\t<value>{info('c.title')}</value>")
        else:
            a(f'\t<value condition="{d_ok}">$INFO[Container(9001).ListItem.{fld}]</value>')
        a("</variable>")
    a('<variable name="Map_NS_Caption">')
    a('\t<value condition="Control.HasFocus(700) | Control.HasFocus(790)">You are here</value>')
    a("\t<value>Next stop</value>")
    a("</variable>")
    a('<variable name="Map_NS_CaptionCol">')
    for ln, d in LINES.items():
        a(f'\t<value condition="Control.HasFocus({d["btn"]})">{d["col"]}</value>')
    a("\t<value>ink2</value>")
    a("</variable>")
    # watched word for the focused station
    a('<variable name="Map_NS_Watched">')
    a(f'\t<value condition="String.IsEqual({prop("kind")},albums)"></value>')
    for ln, d in LINES.items():
        s = src[ln]
        a(f'\t<value condition="Control.HasFocus({d["btn"]}) + String.IsEqual({s}.DBType,tvshow)">$INFO[{s}.Property(UnWatchedEpisodes), · , unwatched]</value>')
        a(f'\t<value condition="Control.HasFocus({d["btn"]}) + {s}.IsResumable"> · in progress</value>')
        a(f'\t<value condition="Control.HasFocus({d["btn"]}) + Integer.IsGreater({s}.PlayCount,0)"> · watched</value>')
        a(f'\t<value condition="Control.HasFocus({d["btn"]})"> · unwatched</value>')
    a(f'\t<value condition="{d_ok} + Integer.IsGreater(Container(9001).ListItem.PlayCount,0)"> · watched</value>')
    a(f'\t<value condition="{d_ok}"> · never watched</value>')
    a("</variable>")
    a('<variable name="Map_NS_Lead">')
    for ln, d in LINES.items():
        s = src[ln]
        a(f'\t<value condition="Control.HasFocus({d["btn"]}) + String.IsEqual({prop("kind")},albums)">$INFO[{s}.Artist, · ,]$INFO[{s}.Year, · ,]</value>')
        a(f'\t<value condition="Control.HasFocus({d["btn"]}) + String.IsEqual({s}.DBType,tvshow)">$INFO[{s}.Studio, · ,]</value>')
        a(f'\t<value condition="Control.HasFocus({d["btn"]})">$INFO[{s}.Director, · ,]</value>')
    a(f'\t<value condition="{d_ok} + {is_tv}">$INFO[Container(9001).ListItem.Property(studio.0), · ,]</value>')
    a(f'\t<value condition="{d_ok}">$INFO[Container(9001).ListItem.Property(director.0), · ,]</value>')
    a("</variable>")
    return v


def expressions():
    e = []
    sv = "System.AddonIsEnabled(script.skinvariables)"
    e.append(f'<expression name="Map_DetailsMatch">{sv} + String.IsEqual(Container(9001).ListItem.DBID,{prop("c.dbid")}) + '
             f'[[String.IsEqual({prop("kind")},tvshows) + String.IsEqual(Container(9001).ListItem.DBType,tvshow)] | '
             f'[!String.IsEqual({prop("kind")},tvshows) + !String.IsEqual({prop("kind")},albums) + String.IsEqual(Container(9001).ListItem.DBType,movie)]]</expression>')
    e.append(f'<expression name="Map_TMDbMatch">!{sv} + String.IsEqual(Container(9002).ListItem.Property(tmdb_id),{prop("c.tmdb")})</expression>')
    # ready = the centre's own data has arrived (or there is no helper to wait for)
    e.append(f'<expression name="Map_Ready">String.IsEqual({prop("kind")},albums) | $EXP[Map_DetailsMatch] | $EXP[Map_TMDbMatch] | [!{sv} + !System.AddonIsEnabled(plugin.video.themoviedb.helper)] | [!{sv} + String.IsEmpty({prop("c.tmdb")})]</expression>')
    for ln, d in LINES.items():
        lst = d["lst"]
        e.append(f'<expression name="Map_LineOn_{ln}">$EXP[Map_Ready] + Integer.IsGreater(Container({lst}).NumItems,0) + !Container({lst}).IsUpdating</expression>')
    return e


# ------------------------------------------------------------------ XML helpers
def img(left, top, w, h, tex, diffuse=None, vis=None, extra="", border=None, aspect=None, bg=False, fade=None):
    t = []
    t.append('<control type="image">')
    t.append(f"\t<left>{left}</left><top>{top}</top><width>{w}</width><height>{h}</height>")
    if aspect:
        t.append(f"\t<aspectratio>{aspect}</aspectratio>")
    if fade:
        t.append(f"\t<fadetime>{fade}</fadetime>")
    attrs = ""
    if border:
        attrs += f' border="{border}"'
    if diffuse:
        attrs += f' colordiffuse="{diffuse}"'
    if bg:
        attrs += ' background="true"'
    t.append(f"\t<texture{attrs}>{tex}</texture>")
    if vis:
        t.append(f"\t<visible>{vis}</visible>")
    if extra:
        t.append(extra)
    t.append("</control>")
    return "\n".join(t)


def lbl(left, top, w, h, text, font, color, align="left", aligny="center", vis=None, extra="", wrap=False):
    t = ['<control type="label">',
         f"\t<left>{left}</left><top>{top}</top><width>{w}</width><height>{h}</height>",
         f"\t<font>{font}</font><textcolor>{color}</textcolor><align>{align}</align><aligny>{aligny}</aligny>",
         f"\t<label>{text}</label>"]
    if wrap:
        t.append("\t<wrapmultiline>true</wrapmultiline>")
    if vis:
        t.append(f"\t<visible>{vis}</visible>")
    if extra:
        t.append(extra)
    t.append("</control>")
    return "\n".join(t)


def group(children, vis=None, left=None, top=None, anims="", desc=None):
    t = ['<control type="group">']
    if desc:
        t.append(f"\t<description>{desc}</description>")
    if left is not None:
        t.append(f"\t<left>{left}</left>")
    if top is not None:
        t.append(f"\t<top>{top}</top>")
    if vis:
        t.append(f"\t<visible>{vis}</visible>")
    if anims:
        t.append(anims)
    t += children
    t.append("</control>")
    return "\n".join(t)


def anim_line_reveal(dx, dy):
    return (f'<animation type="Visible" condition="!{RM}"><effect type="fade" start="0" end="100" time="300" tween="cubic" easing="out"/>'
            f'<effect type="slide" start="{dx},{dy}" end="0,0" time="300" tween="cubic" easing="out"/></animation>'
            f'<animation type="Hidden" condition="!{RM}"><effect type="fade" start="100" end="0" time="120"/></animation>')


# ------------------------------------------------------------------ station slots
def slot_on(ln, k):
    d = LINES[ln]
    return f"!String.IsEmpty(Container({d['lst']}).ListItemPosition({k}).DBID)"


def slot_focus(ln, k):
    d = LINES[ln]
    return f"Control.HasFocus({d['btn']}) + Container({d['lst']}).Position({k})"


def visited(ln, k):
    d = LINES[ln]
    ids = " | ".join(f"String.IsEqual(Container({d['lst']}).ListItemPosition({k}).DBID,{prop(f'r{i}.dbid')})" for i in range(1, DEPTH + 1))
    return f"[{ids}]"


def xdots(ln, k, x, y):
    """Interchange tags: the station is also on this centre's director line (vermilion) or year + genre line
    (green). Actor lines can't be tested: ListItem.Cast is empty for library list items (device 2026-10-19)."""
    out = []
    for i, (col, cond) in enumerate(xdot_checks(ln, k)):
        cx = x + i * 16
        out.append(img(cx - 17, y - 17, 34, 34, "sd/shadow_xdot.png", diffuse="shadow", vis=cond))
        out.append(img(cx - 14, y - 14, 28, 28, "sd/disc_22.png", diffuse="white", vis=cond))
        out.append(img(cx - 10, y - 10, 20, 20, "sd/disc_14.png", diffuse=col, vis=cond))
    return out


def xdot_checks(ln, k):
    """(colour, condition) of each interchange dot on station k of line ln (shared with Map_AnyXdot)."""
    d = LINES[ln]
    li = f"Container({d['lst']}).ListItemPosition({k})"
    checks = []
    if ln != "up":
        checks.append(("l_dir", f"$EXP[Map_DetailsMatch] + !String.IsEmpty(Container(9001).ListItem.Property(director.0)) + String.Contains({li}.Director,Container(9001).ListItem.Property(director.0))"))
    if ln != "down":
        checks.append(("l_yg", f"$EXP[Map_DetailsMatch] + String.IsEqual({li}.Year,{prop('c.year')}) + !String.IsEmpty(Container(9001).ListItem.Property(genre.0)) + String.Contains({li}.Genre,Container(9001).ListItem.Property(genre.0))"))
    return checks


def dot_slot(ln, k):
    d = LINES[ln]
    lst, y, cx = d["lst"], d["y"], d["xs"][k]
    li = f"Container({lst}).ListItemPosition({k})"
    on, foc = slot_on(ln, k), slot_focus(ln, k)
    lf = f"Control.HasFocus({d['btn']})"
    ch = []
    # unfocused dot
    ch.append(img(cx - 16, y - 16, 32, 32, "sd/disc_26.png", diffuse="white", vis=f"!$EXP[Map_SF_{ln}{k}]"))
    ch.append(img(cx - 16, y - 16, 32, 32, "sd/ring_26_7.png", diffuse=d["col"], vis=f"!$EXP[Map_SF_{ln}{k}]"))
    # visited marker: a grey dot
    ch.append(img(cx - 16, y - 16, 32, 32, "sd/ring_26_7.png", diffuse="l_route", vis=f"!$EXP[Map_SF_{ln}{k}] + {visited(ln, k)}"))
    ch += xdots(ln, k, cx + 22, y - 24)
    # focused roundel
    rf = [img(cx - 108, y - 94, 216, 216, "sd/shadow_roundel.png", diffuse="shadow"),
          img(cx - 63, y - 63, 126, 126, "sd/disc_120.png", diffuse="ink"),
          img(cx - 55, y - 55, 110, 110, "sd/disc_104.png", diffuse="white"),
          '<control type="image">'
          f"<left>{cx - 47}</left><top>{y - 47}</top><width>94</width><height>94</height><aspectratio>scale</aspectratio>"
          f'<fadetime>150</fadetime><texture background="true" diffuse="sd/mask_circle.png">$INFO[{li}.Art(poster)]</texture><visible>!{ALBUMS}</visible></control>',
          '<control type="image">'
          f"<left>{cx - 47}</left><top>{y - 47}</top><width>94</width><height>94</height><aspectratio>scale</aspectratio>"
          f'<fadetime>150</fadetime><texture background="true" diffuse="sd/mask_circle.png">$INFO[{li}.Art(thumb)]</texture><visible>{ALBUMS}</visible></control>']
    ch.append(group(rf, vis=f"$EXP[Map_SF_{ln}{k}]",
                    anims=f'<animation type="Visible" condition="!{RM}"><effect type="zoom" start="40" end="100" center="{cx},{y}" time="220" tween="back" easing="out"/></animation>'))
    # titles: line unfocused -> 2-line title + year; line focused -> neighbours 1 line, focused big
    ty = y + 24
    if ln == "down":
        ty = y + 24
    tw_ = 230 if ln == "up" else 196
    gl = ['<control type="grouplist">',
          f"\t<left>{cx - tw_ // 2}</left><top>{ty}</top><width>{tw_}</width><height>100</height>",
          "\t<orientation>vertical</orientation><itemgap>2</itemgap><usecontrolcoords>true</usecontrolcoords>",
          f"\t<visible>!{lf}</visible>",
          '\t<control type="textbox">',
          f"\t\t<width>{tw_}</width><height max=\"62\">auto</height>",
          f"\t\t<font>st_24</font><textcolor>ink</textcolor><align>center</align>",
          f"\t\t<label>$INFO[{li}.Title]</label>",
          "\t</control>",
          lbl(0, 0, tw_, 26, f"$INFO[{li}.Year]", "reg_21", "ink2", align="center").replace("<left>0</left><top>0</top>", "<top>-2</top>"),
          "</control>"]
    ch.append("\n".join(gl))
    ch.append(lbl(cx - 110, ty, 220, 30, f"$INFO[{li}.Label]", "st_24", "ink2", align="center",
                  vis=f"{lf} + !Container({lst}).Position({k})"))
    bl = min(cx - 190, 780 - 380) if ln == "up" else cx - 190  # keep clear of the centre poster
    big = [lbl(bl, y + 72, 380, 40, f"$INFO[{li}.Label]", "xb_30", "ink", align="center"),
           lbl(bl, y + 112, 380, 30, f"$INFO[{li}.Year]$INFO[{li}.Duration(h), · , h ]$INFO[{li}.Duration(mm)]", "reg_21", "ink2", align="center",
               vis=f"Integer.IsGreater({li}.Duration(h),0)"),
           lbl(bl, y + 112, 380, 30, f"$INFO[{li}.Year]$INFO[{li}.Duration(m), · , min]", "reg_21", "ink2", align="center",
               vis=f"!Integer.IsGreater({li}.Duration(h),0)")]
    ch.append(group(big, vis=f"$EXP[Map_SF_{ln}{k}]"))
    return group(ch, vis=on, desc=f"{ln} station {k}")


def poster_slot(ln, k):
    d = LINES[ln]
    lst, y, cx0 = d["lst"], d["y"], d["xs"][k]
    sgn = 1 if ln == "right" else -1
    li = f"Container({lst}).ListItemPosition({k})"
    on = slot_on(ln, k)
    lf = f"Control.HasFocus({d['btn']})"
    w, h = 110, 165
    x, yy = cx0 - w // 2, y - h // 2
    vis_ = visited(ln, k)
    ch = []
    # shift for focus growth: slots after the focused one move 76 px outwards
    before = " | ".join(f"Container({lst}).Position({j})" for j in range(k)) or "false"
    anim = ""
    if k > 0:
        anim = (f'<animation type="Conditional" condition="!{RM} + {lf} + [{before}]" reversible="true">'
                f'<effect type="slide" start="0,0" end="{76 * sgn},0" time="160" tween="cubic" easing="out"/></animation>'
                f'<animation type="Conditional" condition="{RM} + {lf} + [{before}]" reversible="true">'
                f'<effect type="slide" start="0,0" end="{76 * sgn},0" time="0"/></animation>')
    unf = [img(x - 24, yy - 16, w + 48, h + 48, "sd/shadow_poster.png", diffuse="shadow", border="40", vis=f"!{ALBUMS}"),
           img(x - 34, y - 81, 178, 178, "sd/shadow_poster.png", diffuse="shadow", border="40", vis=ALBUMS),
           img(x, yy, w, h, "common/white.png", diffuse="wash", vis=f"!{ALBUMS}"),
           lbl(x + 8, yy + 8, w - 16, 60, f"$INFO[{li}.Label]", "semi_20", "ink2", aligny="top", wrap=True, vis=f"!{vis_}"),
           '<control type="image">'
           f"<left>{x}</left><top>{yy}</top><width>{w}</width><height>{h}</height><aspectratio>scale</aspectratio><fadetime>120</fadetime>"
           f'<texture background="true" diffuse="sd/mask_110x165.png">$INFO[{li}.Art(poster)]</texture>'
           f"<visible>!{vis_} + !{ALBUMS}</visible></control>",
           '<control type="image">'
           f"<left>{x - 10}</left><top>{y - 65}</top><width>130</width><height>130</height><aspectratio>scale</aspectratio><fadetime>120</fadetime>"
           f'<texture background="true" diffuse="sd/mask_180x180.png">$INFO[{li}.Art(thumb)]</texture>'
           f"<visible>{ALBUMS}</visible></control>",
           '<control type="image">'
           f"<left>{x}</left><top>{yy}</top><width>{w}</width><height>{h}</height><aspectratio>scale</aspectratio><fadetime>120</fadetime>"
           f'<texture background="true" diffuse="sd/mask_110x165.png" colordiffuse="61ffffff">$INFO[{li}.Art(poster)]</texture>'
           f"<visible>{vis_} + !{ALBUMS}</visible></control>",
           img(x - 4, yy - 4, w + 8, h + 8, "sd/frame_o4.png", diffuse=d["col"], border="14", vis=f"!{vis_} + !{ALBUMS}"),
           img(x - 14, y - 69, 138, 138, "sd/frame_o4.png", diffuse=d["col"], border="14", vis=ALBUMS),
           img(x - 4, yy - 4, w + 8, h + 8, "sd/frame_o4.png", diffuse="hair_strong", border="14", vis=vis_),
           ]
    unf.append(group([img(cx0 - 66, yy + h + 12, 22, 22, "sd/visited.png", diffuse="ink2"),
                      lbl(cx0 - 38, yy + h + 6, 120, 34, "visited", "semi_20", "ink2")], vis=vis_))
    unf += xdots(ln, k, x + w - 10, yy + 8)
    ch.append(group(unf, vis=f"!$EXP[Map_SF_{ln}{k}]"))
    # focused: 164x246 at centre + 38 (outwards), ink ring 6 px with a 7 px ground gap
    fw, fh = 164, 246
    fcx = cx0 + 38 * sgn
    fx, fy = fcx - fw // 2, y - fh // 2
    o = 13
    film = [img(fx - o - 40, fy - o - 20, fw + 2 * o + 80, fh + 2 * o + 80, "sd/shadow_big.png", diffuse="shadow", border="100"),
            img(fx - o, fy - o, fw + 2 * o, fh + 2 * o, "sd/ringf_fill.png", diffuse="ground", border="20"),
            img(fx - o, fy - o, fw + 2 * o, fh + 2 * o, "sd/ringf_6.png", diffuse="ink", border="20"),
            img(fx, fy, fw, fh, "common/white.png", diffuse="wash"),
            '<control type="image">'
            f"<left>{fx}</left><top>{fy}</top><width>{fw}</width><height>{fh}</height><aspectratio>scale</aspectratio><fadetime>120</fadetime>"
            f'<texture background="true" diffuse="sd/mask_164x246.png">$INFO[{li}.Art(poster)]</texture></control>']
    sq, sy = 180, y - 90
    sx = fcx - sq // 2
    album = [img(sx - o - 40, sy - o - 20, sq + 2 * o + 80, sq + 2 * o + 80, "sd/shadow_big.png", diffuse="shadow", border="100"),
             img(sx - o, sy - o, sq + 2 * o, sq + 2 * o, "sd/ringf_fill.png", diffuse="ground", border="20"),
             img(sx - o, sy - o, sq + 2 * o, sq + 2 * o, "sd/ringf_6.png", diffuse="ink", border="20"),
             '<control type="image">'
             f"<left>{sx}</left><top>{sy}</top><width>{sq}</width><height>{sq}</height><aspectratio>scale</aspectratio><fadetime>120</fadetime>"
             f'<texture background="true" diffuse="sd/mask_180x180.png">$INFO[{li}.Art(thumb)]</texture></control>']
    foc = [group(film, vis=f"!{ALBUMS}"), group(album, vis=ALBUMS)]
    if ln == "right":
        tl = max(1150, fcx - 170)
        foc.append(lbl(tl, fy + fh + 18, 340, 44, f"$INFO[{li}.Label]", "xb_34", "ink", align="center"))
        foc.append(lbl(tl, fy + fh + 60, 340, 30, f"$INFO[{li}.Year]$INFO[{li}.Duration(h), · , h ]$INFO[{li}.Duration(mm)]", "reg_21", "ink2", align="center",
                       vis=f"Integer.IsGreater({li}.Duration(h),0)"))
        foc.append(lbl(tl, fy + fh + 60, 340, 30, f"$INFO[{li}.Year]$INFO[{li}.Duration(m), · , min]", "reg_21", "ink2", align="center",
                       vis=f"!Integer.IsGreater({li}.Duration(h),0)"))
    ch.append(group(foc, vis=f"$EXP[Map_SF_{ln}{k}]",
                    anims=f'<animation type="Visible" condition="!{RM}"><effect type="zoom" start="70" end="100" center="{fcx},{y}" time="200" tween="cubic" easing="out"/></animation>'))
    return group(ch, vis=on, anims=anim, desc=f"{ln} station {k}")


# ------------------------------------------------------------------ lines (track, terminus, pill, label)
def line_track(ln):
    d = LINES[ln]
    col, y, lst, k = d["col"], d["y"], d["lst"], d["k"]
    lf = f"Control.HasFocus({d['btn']})"
    out = []
    n_is = lambda n: f"Integer.IsEqual(Container({lst}).NumItems,{n})"
    more = f"Integer.IsGreater(Container({lst}).NumItems,{k})"
    if ln == "up":
        out.append(img(772, 182, 106, 118, "sd/conn_up.png", diffuse=col))
        for n in range(1, k + 1):
            xe = d["xs"][n - 1] - 62
            out.append(img(xe - 4, y - 4, 780 - xe + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=n_is(n)))
            out.append(img(xe - 4, y - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=n_is(n)))
        out.append(img(134 - 4, y - 4, 780 - 134 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + !{lf}"))
        out.append(img(64, y - 4, 780 - 64 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + {lf}"))
        pill = (102, y)
    elif ln == "down":
        out.append(img(1044, 734, 104, 194, "sd/conn_down.png", diffuse=col))
        for n in range(1, k + 1):
            xe = d["xs"][n - 1] + 62
            out.append(img(1140 - 4, y - 4, xe - 1140 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=n_is(n)))
            out.append(img(xe - 4, y - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=n_is(n)))
        out.append(img(1136, y - 4, 1790 - 1140 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + !{lf}"))
        out.append(img(1136, y - 4, 1856 - 1140 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + {lf}"))
        pill = (1808, y)
    elif ln == "right":
        for n in range(1, k + 1):
            xe = d["xs"][n - 1] + 55 + 30
            out.append(img(1106, y - 4, xe - 1110 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{n_is(n)} + !{lf}"))
            out.append(img(xe - 4, y - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=f"{n_is(n)} + !{lf}"))
            xe2 = xe + 76
            out.append(img(1106, y - 4, xe2 - 1110 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{n_is(n)} + {lf}"))
            out.append(img(xe2 - 4, y - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=f"{n_is(n)} + {lf}"))
        out.append(img(1106, y - 4, 1800 - 1110 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + !{lf}"))
        out.append(img(1106, y - 4, 1856 - 1110 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + {lf}"))
        pill = (1818, y)
    else:  # left
        out.append(img(672, 516, 146, 82, "sd/conn_left.png", diffuse=col))
        for n in range(1, k + 1):
            xe = d["xs"][n - 1] - 55 - 30
            out.append(img(xe - 4, y - 4, 680 - xe + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{n_is(n)} + !{lf}"))
            out.append(img(xe - 4, y - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=f"{n_is(n)} + !{lf}"))
            xe2 = xe - 76
            out.append(img(xe2 - 4, y - 4, 680 - xe2 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{n_is(n)} + {lf}"))
            out.append(img(xe2 - 4, y - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=f"{n_is(n)} + {lf}"))
        out.append(img(130, y - 4, 680 - 134 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + !{lf}"))
        out.append(img(64, y - 4, 680 - 64 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0", vis=f"{more} + {lf}"))
        pill = (102, y)
    # "+N" pill (unfocused lines with more stations than slots)
    pw = 72 if ln == "right" else 64
    px, py = pill
    out.append(group([img(px - pw // 2, py - 23, pw, 46, "sd/pill_46.png", diffuse=col, border="23"),
                      lbl(px - pw // 2, py - 23, pw, 46, f"$VAR[Map_More_{ln}]", "xb_24", "white", align="center")],
                     vis=f"{more} + !{lf}"))
    return out


def line_label(ln):
    d = LINES[ln]
    col = d["col"]
    pos = {"up": (64, 124, "left"), "right": (1856, 536, "right"), "down": (1856, 848, "right"), "left": (64, 696, "left")}
    x, y, al = pos[ln]
    gl = ['<control type="grouplist">',
          f"\t<left>{64 if al == 'left' else 400}</left><top>{y}</top><width>{1456 if al == 'right' else 1100}</width><height>40</height>",
          f"\t<orientation>horizontal</orientation><align>{al}</align><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"]
    if al == "left":
        gl[1] = f"\t<left>{x}</left><top>{y}</top><width>1100</width><height>40</height>"
    else:
        gl[1] = f"\t<left>{x - 1456}</left><top>{y}</top><width>1456</width><height>40</height>"
    slides = {"left": ("Control.HasFocus(704)", "0,28"),
              "right": ("Control.HasFocus(702)", "0,124"),
              "down": ("Control.HasFocus(703)", "0,-44"),
              "up": ("Control.HasFocus(701) + [Container(611).Position(1) | Container(611).Position(2)]", "456,0")}
    cond, end = slides[ln]
    gl.append(f'<animation type="Conditional" condition="!{RM} + {cond}" reversible="true"><effect type="slide" start="0,0" end="{end}" time="160" tween="cubic" easing="out"/></animation>')
    gl.append(f'<animation type="Conditional" condition="{RM} + {cond}" reversible="true"><effect type="slide" start="0,0" end="{end}" time="0"/></animation>')
    gl.append(img(0, 3, 34, 34, f"sd/badge_34_{ARROW[ln]}.png", diffuse=col).replace("<left>0</left>", "<left>0</left>"))
    gl.append('<control type="label"><left>12</left><top>0</top><width>auto</width><height>40</height>'
              f"<font>caps_22</font><textcolor>{col}</textcolor><label>$VAR[Map_LineName_{ln}]</label></control>")
    gl.append('<control type="label"><width>auto</width><height>40</height>'
              f"<font>capsxb_22</font><textcolor>ink</textcolor><label>$VAR[Map_Count_{ln}]</label></control>")
    gl.append("</control>")
    return "\n".join(gl)


# ------------------------------------------------------------------ centre
CX, CY, CW, CHH = 810, 292, 300, 450
FROM = {
    "right": ("420,-90", 55), "up": ("-260,-300", 40), "left": ("-420,72", 55),
    "down": ("420,400", 40), "back": ("0,0", 104), "start": ("0,40", 96),
}


def centre():
    ch = []
    o = 14
    for ab in ("a", "b"):
        anims = []
        for frm, (st, z) in FROM.items():
            anims.append(f'<animation type="Visible" condition="!{RM} + String.IsEqual({prop("from")},{frm})">'
                         f'<effect type="slide" start="{st}" end="0,0" time="340" tween="cubic" easing="out"/>'
                         f'<effect type="zoom" start="{z}" end="100" center="960,517" time="340" tween="cubic" easing="out"/>'
                         f'<effect type="fade" start="40" end="100" time="200"/></animation>')
        anims.append(f'<animation type="Focus" condition="!{RM}"><effect type="zoom" start="100" end="103" center="960,517" time="160"/></animation>')
        g = [img(CX - o - 72, CY - o - 50, CW + 2 * o + 144, CHH + 2 * o + 144, "sd/shadow_big.png", diffuse="shadow", border="100"),
             img(CX - o, CY - o, CW + 2 * o, CHH + 2 * o, "sd/ring_centre_fill.png", diffuse="ground", border="24"),
             img(CX - o, CY - o, CW + 2 * o, CHH + 2 * o, "sd/ring_centre.png", diffuse="ink", border="24"),
             img(CX, CY, CW, CHH, "common/white.png", diffuse="wash"),
             lbl(CX + 20, CY + 20, CW - 40, 120, info("c.title"), "xb_28", "ink2", aligny="top", wrap=True),
             '<control type="image">'
             f"<left>{CX}</left><top>{CY}</top><width>{CW}</width><height>{CHH}</height><aspectratio>scale</aspectratio><fadetime>100</fadetime>"
             f'<texture background="true" diffuse="sd/mask_300x450.png">$VAR[Map_CentrePoster]</texture></control>',
             ]
        sqy = CY + (CHH - CW) // 2
        sq = [img(CX - o - 72, sqy - o - 50, CW + 2 * o + 144, CW + 2 * o + 144, "sd/shadow_big.png", diffuse="shadow", border="100"),
              img(870 - 4, CY - 4, 8, sqy - CY + 8, "sd/line_v8.png", diffuse="l_dir", border="0,4,0,4", vis="$EXP[Map_LineOn_up]"),
              img(1052 - 4, sqy + CW - 4, 8, CY + CHH - sqy - CW + 8, "sd/line_v8.png", diffuse="l_yg", border="0,4,0,4", vis="$EXP[Map_LineOn_down]"),
              img(CX - o, sqy - o, CW + 2 * o, CW + 2 * o, "sd/ring_centre_fill.png", diffuse="ground", border="24"),
              img(CX - o, sqy - o, CW + 2 * o, CW + 2 * o, "sd/ring_centre.png", diffuse="ink", border="24"),
              img(CX, sqy, CW, CW, "common/white.png", diffuse="wash"),
              '<control type="image">'
              f"<left>{CX}</left><top>{sqy}</top><width>{CW}</width><height>{CW}</height><aspectratio>scale</aspectratio><fadetime>100</fadetime>"
              f'<texture background="true" diffuse="sd/mask_280x280.png">{info("c.poster")}</texture></control>']
        ch.append(group([group(g, vis=f"!{ALBUMS}"), group(sq, vis=ALBUMS)],
                        vis=f"String.IsEqual({prop('flip')},{ab})", anims="\n".join(anims), desc=f"centre {ab}"))
    # "you are here" lift: thicker ring while the centre has focus
    ch.append(img(CX - 22, CY + (CHH - CW) // 2 - 22, CW + 44, CW + 44, "sd/ring_centre.png", diffuse="ink", border="24", vis=f"Control.HasFocus(700) + {ALBUMS}",
                  extra=f'<animation type="Visible" condition="!{RM}"><effect type="fade" start="0" end="100" time="160"/></animation>'))
    ch.append(img(CX - 22, CY - 22, CW + 44, CHH + 44, "sd/ring_centre.png", diffuse="ink", border="24", vis=f"Control.HasFocus(700) + !{ALBUMS}",
                  extra=f'<animation type="Visible" condition="!{RM}"><effect type="fade" start="0" end="100" time="160"/><effect type="zoom" start="97" end="100" center="960,517" time="160"/></animation>'))
    # title tiers: 60 if it fits 640 px, else 44 (probe 7701)
    # probes: invisible textboxes ON screen (an offscreen textbox reports NumPages 0)
    ch.append('<control type="textbox" id="7701"><left>464</left><top>766</top><width>560</width><height>66</height>'
              f"<font>disp_60</font><textcolor>clear</textcolor><label>{info('c.title')}</label></control>")
    ch.append('<control type="textbox" id="7702"><left>464</left><top>766</top><width>560</width><height>50</height>'
              f"<font>disp_44</font><textcolor>clear</textcolor><label>{info('c.title')}</label></control>")
    t60 = "Integer.IsEqual(Container(7701).NumPages,1)"
    t44 = "!Integer.IsEqual(Container(7701).NumPages,1) + Integer.IsEqual(Container(7702).NumPages,1)"
    t36 = "!Integer.IsEqual(Container(7701).NumPages,1) + !Integer.IsEqual(Container(7702).NumPages,1)"
    ch.append(lbl(464, 766, 560, 74, info("c.title"), "disp_60", "ink", align="right", vis=t60))
    ch.append(lbl(464, 778, 560, 60, info("c.title"), "disp_44", "ink", align="right", vis=t44))
    ch.append('<control type="textbox"><left>464</left><top>760</top><width>560</width><height>84</height>'
              f"<font>disp_36</font><textcolor>ink</textcolor><align>right</align><label>{info('c.title')}</label><visible>{t36}</visible></control>")
    ch.append(lbl(464, 844, 560, 34, "$VAR[Map_CentreMeta]", "semi_24", "ink2", align="right"))
    return ch


def next_stop():
    ch = [lbl(1160, 146, 696, 30, "$VAR[Map_NS_Caption]", "caps_21", "$VAR[Map_NS_CaptionCol]")]
    gl = ['<control type="grouplist">',
          "	<left>1160</left><top>180</top><width>696</width><height>36</height>",
          "	<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
          '	<control type="label" id="7711"><width max="340">auto</width><height>36</height><font>xb_24</font><textcolor>ink</textcolor><label>$VAR[Map_NS_Title]</label></control>',
          '	<control type="label" id="7712"><width max="250">auto</width><height>36</height><font>reg_24</font><textcolor>ink2</textcolor><label>$VAR[Map_NS_Lead]</label></control>',
          '	<control type="label" id="7713"><width>auto</width><height>36</height><font>reg_24</font><textcolor>ink2</textcolor><label> · </label><visible>$EXP[Map_NS_HasRating]</visible></control>',
          '	<control type="image" id="7714"><top>8</top><width>20</width><height>20</height><texture colordiffuse="ink2">sd/star.png</texture><visible>$EXP[Map_NS_HasRating]</visible></control>',
          '	<control type="label" id="7715"><left>6</left><width>auto</width><height>36</height><font>reg_24</font><textcolor>ink2</textcolor><label>$VAR[Map_NS_RatingNum]</label><visible>$EXP[Map_NS_HasRating]</visible></control>',
          '	<control type="label" id="7716"><width>auto</width><height>36</height><font>reg_24</font><textcolor>ink2</textcolor><label>$VAR[Map_NS_Watched]</label></control>',
          "</control>"]
    ch.append("\n".join(gl))
    # plot clamped to 2 lines. Kodi drops the overflow without an ellipsis (GUITextLayout::WrapText) and can't
    # split off a first sentence, so the textbox's own NumPages tells when it overflows and the end of line 2
    # fades into the paper and gets a "…" (producer review 0.9.1)
    ch.append('<control type="textbox" id="7720"><left>1160</left><top>216</top><width>696</width><height>68</height>'
              "<font>reg_24</font><textcolor>ink2</textcolor><label>$VAR[Map_NS_Plot]</label></control>")
    over = "Integer.IsGreater(Container(7720).NumPages,1)"
    ch.append(img(1856 - 150, 216 + 34, 150, 34, "common/gradient_right.png", diffuse="ground", vis=over))
    ch.append(img(1856 - 40, 216 + 34, 40, 34, "common/white.png", diffuse="ground", vis=over))
    ch.append(lbl(1856 - 40, 216 + 34, 40, 34, "…", "reg_24", "ink2", align="right", vis=over))
    return ch


def hints():
    # right edge 1024, rows at 912 and 962 (gen.py: line-height 50)
    def key(label_x_from_right):
        pass
    out = []
    row1 = ['<control type="grouplist">',
            "\t<left>224</left><top>914</top><width>800</width><height>40</height>",
            "\t<orientation>horizontal</orientation><align>right</align><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"]

    def keycap(text, icon=None, gap=12, cid=None):
        # disabled auto-width button draws its key texture around the text (lesson 141 / 235)
        idattr = f' id="{cid}"' if cid else ""
        b = (f'<control type="button"{idattr}><width>auto</width><height>36</height><top>2</top><font>xb_19</font>'
             f"<textcolor>ink</textcolor><disabledcolor>ink</disabledcolor><textoffsetx>11</textoffsetx><align>center</align>"
             f'<texturenofocus border="12" colordiffuse="ink">sd/key.png</texturenofocus><texturefocus border="12" colordiffuse="ink">sd/key.png</texturefocus>'
             f"<label>{text}</label><enable>false</enable></control>")
        return b

    def word(text, cid=None, right=30):
        return (f'<control type="label"><left>12</left><width>auto</width><height>40</height><font>semi_22</font><textcolor>ink2</textcolor>'
                f"<label>{text}</label></control>"
                f'<control type="label"><width>{right}</width><height>40</height><label></label></control>')
    row1.append(f'<control type="group"><width>0</width><height>40</height><visible>false</visible></control>')
    row1.append(keycap("OK"))
    row1.append(f'<control type="label"><left>12</left><width>auto</width><height>40</height><font>semi_22</font><textcolor>ink2</textcolor><label>$VAR[Map_HintOK]</label></control>')
    row1.append("</control>")
    out.append("\n".join(row1))
    row2 = ['<control type="grouplist">',
            "\t<left>224</left><top>964</top><width>800</width><height>40</height>",
            "\t<orientation>horizontal</orientation><align>right</align><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
            keycap("BACK"),
            '<control type="label"><left>12</left><width max="520">auto</width><height>40</height><font>semi_22</font><textcolor>ink2</textcolor><label>$VAR[Map_BackHint]</label></control>',
            "</control>"]
    out.append("\n".join(row2))
    return out


def compass():
    x, y = 64, 818
    rows = [("l_dir", "Up", "$VAR[Map_KeyUp]"), ("l_lead", "Right", "$VAR[Map_KeyRight]"), ("l_yg", "Down", "$VAR[Map_KeyDown]"), ("l_co", "Left", "$VAR[Map_KeyLeft]")]
    ch = [img(x, y, 140, 140, "sd/compass.png")]
    for i, (col, k, v) in enumerate(rows):
        ty = y + 4 + i * 33
        ch.append(lbl(x + 170, ty, 70, 33, k, "xb_22", col))
        ch.append(lbl(x + 238, ty, 300, 33, v, "semi_22", "ink2"))
    ty = y + 138
    # 0.9.3 (Omar): the sample dot is neutral grey (a line colour read as a line), and only shown when a
    # station on this map really carries an interchange dot; otherwise the row is text only
    ch.append(img(x + 170, ty + 8, 18, 18, "sd/disc_14.png", diffuse="ink2", vis="$EXP[Map_AnyXdot]"))
    ch.append(lbl(x + 198, ty, 400, 33, "also on another line", "semi_22", "ink2", vis="$EXP[Map_AnyXdot]"))
    ch.append(lbl(x + 170, ty, 430, 33, "No station here is on another line", "semi_22", "ink2", vis="!$EXP[Map_AnyXdot]"))
    return group(ch, vis=f"!Skin.HasSetting({P}.map.hidekey)", desc="map key")


def route_bar(top=72):
    """Start · [··· ] · r2 · r1 · current. Segment before a stop is drawn in the colour of the line that led to it.
    0.9.3: widths capped so the longest route (··· + r2 + r1 + current) ends before Index (x 1540)."""
    def seg(col_var, w, vis):
        return (f'<control type="image"><top>15</top><width>{w}</width><height>6</height>'
                f'<texture border="3,0,3,0" colordiffuse="$VAR[{col_var}]">sd/line_h6.png</texture><visible>{vis}</visible></control>')

    def stop(slot, vis, cur=False):
        if cur:
            return (f'<control type="group"><width>44</width><height>36</height><visible>{vis}</visible>'
                    + img(-1, -1, 38, 38, "sd/disc_32.png", diffuse="white")
                    + img(-1, -1, 38, 38, "sd/ring_32_8.png", diffuse="ink") + "</control>"
                    f'<control type="label"><width max="280">auto</width><height>36</height><font>xb_24</font><textcolor>ink</textcolor><label>{info(slot + ".title")}</label><visible>{vis}</visible></control>')
        return (f'<control type="group"><width>34</width><height>36</height><visible>{vis}</visible>'
                + img(4, 4, 28, 28, "sd/disc_22.png", diffuse="white")
                + img(4, 4, 28, 28, "sd/ring_22_6.png", diffuse="ink") + "</control>"
                f'<control type="label"><width max="160">auto</width><height>36</height><font>semi_24</font><textcolor>ink2</textcolor><label>{info(slot + ".title")}</label><visible>{vis}</visible></control>'
                f'<control type="label"><width>16</width><height>36</height><label></label><visible>{vis}</visible></control>')
    r1, r2, r3 = (f"!String.IsEmpty({prop(f'r{i}.dbid')})" for i in (1, 2, 3))
    gl = ['<control type="grouplist">',
          f"\t<left>420</left><top>{top}</top><width>1230</width><height>36</height>",
          "\t<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
          '<control type="group"><width>30</width><height>36</height>' + img(2, 6, 24, 24, "sd/disc_18.png", diffuse="white") + img(2, 6, 24, 24, "sd/ring_18_5.png", diffuse="l_route") + "</control>",
          '<control type="label"><width>auto</width><height>36</height><font>semi_24</font><textcolor>ink2</textcolor><label>Start</label></control>',
          '<control type="label"><width>16</width><height>36</height><label></label></control>',
          # Start -> (… or oldest shown)
          seg("Map_Col_r2", 72, f"{r2} + !{r3}"),
          seg("Map_Col_r1", 72, f"{r1} + !{r2}"),
          seg("Map_Col_c", 96, f"!{r1}"),
          seg("Map_RouteGrey", 40, r3),
          f'<control type="label"><width>auto</width><height>36</height><font>xb_24</font><textcolor>ink2</textcolor><label>  ···  </label><visible>{r3}</visible></control>',
          seg("Map_Col_r2", 40, r3),
          stop("r2", r2),
          seg("Map_Col_r1", 56, r2),
          stop("r1", r1),
          seg("Map_Col_c", 72, r1),
          stop("c", "true", cur=True),
          "</control>"]
    return "\n".join(gl)


def brand_and_right(index_btn=True):
    out = [img(64, 66, 44, 44, "sd/wordmark.png"),
           lbl(122, 64, 300, 48, "Six Degrees", "xb_28", "ink")]
    out.append('<control type="label"><left>1500</left><top>64</top><width>356</width><height>48</height><font>xb_30</font>'
               "<textcolor>ink</textcolor><align>right</align><label>$INFO[System.Time]</label></control>")
    return out


# ------------------------------------------------------------------ buttons + actions
def reset(lst):
    return [f"Control.Move({lst},-$INFO[Container({lst}).CurrentItem])", f"Control.Move({lst},1)"]


def push_actions():
    acts = []
    for i in range(DEPTH, 1, -1):
        for f in FIELDS:
            acts.append(f"SetProperty({P}.r{i}.{f},$ESCINFO[{prop(f'r{i - 1}.{f}')}],home)")
    for f in FIELDS:
        acts.append(f"SetProperty({P}.r1.{f},$ESCINFO[{prop(f'c.{f}')}],home)")
    return acts


def set_centre_actions(src, col, kind_from_item=False):
    """centre <- the item `src` (an infolabel prefix such as Container(612).ListItem)."""
    a = [f"SetProperty({P}.c.dbid,$INFO[{src}.DBID],home)",
         f"SetProperty({P}.c.title,$ESCINFO[{src}.Title],home)",
         f"SetProperty({P}.c.year,$INFO[{src}.Year],home)",
         f"SetProperty({P}.c.poster,$ESCINFO[{src}.Art(poster)],home)",
         f"SetProperty({P}.c.tmdb,$INFO[{src}.UniqueID(tmdb)],home)",
         f"SetProperty({P}.c.file,$ESCINFO[{src}.FileNameAndPath],home)",
         f"SetProperty({P}.c.col,{col},home)"]
    return a


def recentre(ln):
    d = LINES[ln]
    src = f"Container({d['lst']}).ListItem"
    acts = push_actions() + set_centre_actions(src, d["key"])
    # up-line raw value (director for films, network for series) for the no-helper fallback
    acts.append(f"SetProperty({P}.c.dir,$ESCINFO[{src}.Director],home)")
    acts.append(f"SetProperty({P}.c.genre,$ESCINFO[{src}.Genre],home)")
    alb, tv = f"String.IsEqual({prop('kind')},albums)", f"String.IsEqual({prop('kind')},tvshows)"
    acts.append((f"SetProperty({P}.c.dir,$ESCINFO[{src}.Studio],home)", tv))
    acts.append((f"SetProperty({P}.c.title,$ESCINFO[{src}.Label],home)", alb))
    acts.append((f"SetProperty({P}.c.poster,$ESCINFO[{src}.Art(thumb)],home)", alb))
    acts.append((f"SetProperty({P}.c.dir,$ESCINFO[{src}.Artist],home)", alb))
    acts.append(f"SetProperty({P}.from,{ln},home)")
    acts.append(f"SetProperty({P}.flip,$VAR[Map_FlipNext],home)")
    for L in LINES.values():
        acts += reset(L["lst"])
    acts.append("SetFocus(700)")
    return acts


def pop_actions():
    acts = []
    for f in FIELDS:
        acts.append(f"SetProperty({P}.c.{f},$ESCINFO[{prop(f'r1.{f}')}],home)")
    for i in range(1, DEPTH):
        for f in FIELDS:
            acts.append(f"SetProperty({P}.r{i}.{f},$ESCINFO[{prop(f'r{i + 1}.{f}')}],home)")
    for f in FIELDS:
        acts.append(f"ClearProperty({P}.r{DEPTH}.{f},home)")
    acts.append(f"SetProperty({P}.from,back,home)")
    acts.append(f"SetProperty({P}.flip,$VAR[Map_FlipNext],home)")
    for L in LINES.values():
        acts += reset(L["lst"])
    acts.append("SetFocus(700)")
    return acts


def tag(name, value, cond=None):
    c = f' condition="{cond}"' if cond else ""
    return f"\t<{name}{c}>{value}</{name}>"


def button(cid, nav, extra=""):
    t = [f'<control type="button" id="{cid}">',
         "\t<left>-400</left><top>-400</top><width>10</width><height>10</height>",
         "\t<texturefocus /><texturenofocus />"]
    t += nav
    if extra:
        t.append(extra)
    t.append("</control>")
    return "\n".join(t)


def enter(ln):
    d = LINES[ln]
    return [f"Control.Move({d['lst']},-$INFO[Container({d['lst']}).CurrentItem])", f"Control.Move({d['lst']},1)", f"SetFocus({d['btn']})"]


def buttons():
    out = []
    back = tag("onback", "799", f"!String.IsEmpty({prop('r1.dbid')})")
    # centre
    nav = []
    for ln, dirn in (("up", "onup"), ("right", "onright"), ("down", "ondown"), ("left", "onleft")):
        for a in enter(ln):
            nav.append(tag(dirn, a, f"$EXP[Map_LineOn_{ln}]"))
    nav.append(tag("onup", "SetFocus(790)", "!$EXP[Map_LineOn_up]"))
    info_acts = ["SetFocus(9001)", "Action(Info)", "SetFocus(700)"]
    for a in info_acts:
        nav.append(tag("onclick", a, "$EXP[Map_DetailsMatch]"))
        nav.append(tag("oninfo", a, "$EXP[Map_DetailsMatch]"))
    nav.append(tag("onclick", f"PlayMedia($ESCINFO[{prop('c.file')}],resume)", f"!$EXP[Map_DetailsMatch] + !String.IsEmpty({prop('c.file')}) + !String.IsEqual({prop('kind')},albums)"))
    nav.append(tag("onclick", f"ActivateWindow(Music,musicdb://albums/{info('c.dbid')}/,return)", f"String.IsEqual({prop('kind')},albums)"))
    nav.append(tag("oninfo", f"ActivateWindow(Music,musicdb://albums/{info('c.dbid')}/,return)", f"String.IsEqual({prop('kind')},albums)"))
    nav.append(back)
    out.append(button(700, nav))

    def line_btn(ln, fwd, bwd, ups):
        d = LINES[ln]
        lst = d["lst"]
        nav = []
        last = f"Integer.IsLess(Container({lst}).CurrentItem,Container({lst}).NumItems)"
        first = f"Integer.IsGreater(Container({lst}).CurrentItem,1)"
        nav.append(tag(fwd, f"Control.Move({lst},1)", last))
        nav.append(tag(bwd, f"Control.Move({lst},-1)", first))
        for a in reset(lst) + ["SetFocus(700)"]:
            nav.append(tag(bwd, a, f"!{first}"))
        for dirn, target in ups:
            if target == "centre":
                for a in reset(lst) + ["SetFocus(700)"]:
                    nav.append(tag(dirn, a))
            elif target == "index":
                for a in reset(lst) + ["SetFocus(790)"]:
                    nav.append(tag(dirn, a))
            else:
                t = LINES[target]
                for a in reset(lst) + enter(target):
                    nav.append(tag(dirn, a, f"$EXP[Map_LineOn_{target}]"))
                for a in reset(lst) + ["SetFocus(700)"]:
                    nav.append(tag(dirn, a, f"!$EXP[Map_LineOn_{target}]"))
        for a in recentre(ln):
            if isinstance(a, tuple):
                nav.append(tag("onclick", a[0], a[1]))
            else:
                nav.append(tag("onclick", a))
        for a in [f"SetFocus({lst})", "Action(Info)", f"SetFocus({d['btn']})"]:
            nav.append(tag("oninfo", a))
        nav.append(back)
        return button(d["btn"], nav)

    out.append(line_btn("up", "onleft", "onright", [("ondown", "centre"), ("onup", "index")]))
    out.append(line_btn("right", "onright", "onleft", [("onup", "up"), ("ondown", "down")]))
    out.append(line_btn("down", "onright", "onleft", [("onup", "centre")]))
    out.append(line_btn("left", "onleft", "onright", [("onup", "up"), ("ondown", "down")]))
    # Index (top right): the plain A-Z library
    idx = ['<control type="button" id="790">',
           "\t<left>1540</left><top>64</top><width>104</width><height>48</height>",
           "\t<font>semi_24</font><textcolor>ink2</textcolor><focusedcolor>white</focusedcolor><align>center</align><textoffsetx>0</textoffsetx>",
           '\t<texturefocus border="24" colordiffuse="ink">sd/pill_48.png</texturefocus><texturenofocus />',
           "\t<label>Index</label>",
           tag("onclick", "ActivateWindow(Videos,videodb://tvshows/titles/,return)", f"String.IsEqual({prop('kind')},tvshows)"),
           tag("onclick", "ActivateWindow(Music,musicdb://albums/,return)", f"String.IsEqual({prop('kind')},albums)"),
           tag("onclick", "ActivateWindow(Videos,videodb://movies/titles/,return)", f"!String.IsEqual({prop('kind')},tvshows) + !String.IsEqual({prop('kind')},albums)"),
           tag("ondown", "700"), tag("onleft", "700"),
           back,
           "</control>"]
    out.append("\n".join(idx))
    # pop (Back): hidden-focus button, actions in onfocus (lesson 170)
    pop = ['<control type="button" id="799">',
           "\t<left>-400</left><top>-400</top><width>10</width><height>10</height>",
           "\t<texturefocus /><texturenofocus />",
           '\t<visible allowhiddenfocus="true">false</visible>']
    for a in pop_actions():
        pop.append(tag("onfocus", a))
    pop.append("</control>")
    out.append("\n".join(pop))
    return out


def data():
    out = []
    # details (skinvariables) + TMDb fallback: always visible (lesson 139), drawn 1 px
    for cid, var in ((9001, "Map_DetailsPath"), (9002, "Map_TMDbPath")):
        out.append(f'<control type="list" id="{cid}">'
                   "<left>0</left><top>1079</top><width>1</width><height>1</height><orientation>vertical</orientation>"
                   "<scrolltime>0</scrolltime>"
                   '<itemlayout width="1" height="1"><control type="image"><width>1</width><height>1</height><texture colordiffuse="00ffffff">$INFO[ListItem.Art(poster)]</texture></control></itemlayout>'
                   '<focusedlayout width="1" height="1"><control type="image"><width>1</width><height>1</height><texture colordiffuse="00ffffff">$INFO[ListItem.Art(poster)]</texture></control></focusedlayout>'
                   f'<content target="videos">$VAR[{var}]</content></control>')
    names = {"up": "Map_PathUp", "right": "Map_PathRight", "down": "Map_PathDown", "left": "Map_PathLeft"}
    for ln, d in LINES.items():
        k = d["k"]
        out.append(f'<control type="list" id="{d["lst"]}">'
                   f"<left>{10 + 60 * (d['lst'] - 611)}</left><top>1079</top><width>{k * 10}</width><height>1</height><orientation>horizontal</orientation>"
                   "<scrolltime>0</scrolltime>"
                   f"<onfocus>noop</onfocus>"
                   '<itemlayout width="10" height="1"><control type="image"><width>1</width><height>1</height><texture colordiffuse="00ffffff">$INFO[ListItem.Art(poster)]</texture></control></itemlayout>'
                   '<focusedlayout width="10" height="1"><control type="image"><width>1</width><height>1</height><texture colordiffuse="00ffffff">$INFO[ListItem.Art(poster)]</texture></control></focusedlayout>'
                   f'<content target="videos" sortby="$VAR[Map_SortBy]" sortorder="descending">$VAR[{names[ln]}]</content></control>')
    for n, cid in zip((1, 2, 3), (621, 622, 623)):
        out.append(f'<control type="list" id="{cid}">'
                   "<left>0</left><top>1079</top><width>1</width><height>1</height><orientation>vertical</orientation>"
                   '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
                   f'<content target="videos">$VAR[Map_PathProbe{n}]</content></control>')
    return out


def slot_expressions():
    e = []
    parts = [f"[Control.HasFocus({d['btn']}) + !String.IsEmpty(Container({d['lst']}).ListItem.Rating)]" for d in LINES.values()]
    nofocus = " + ".join(f"!Control.HasFocus({d['btn']})" for d in LINES.values())
    parts.append(f"[{nofocus} + $EXP[Map_DetailsMatch] + !String.IsEmpty(Container(9001).ListItem.Rating)]")
    e.append(f'<expression name="Map_NS_HasRating">{" | ".join(parts)}</expression>')
    for ln, d in LINES.items():
        for k in range(d["k"]):
            e.append(f'<expression name="Map_SF_{ln}{k}">Control.HasFocus({d["btn"]}) + Container({d["lst"]}).Position({k})</expression>')
    # 0.9.3: is any interchange dot on screen? The same chain that draws them: line shown + slot filled
    # (+ poster slot not the focused one, whose dots hide) + the dot's own condition
    terms = []
    for ln, d in LINES.items():
        for k in range(d["k"]):
            chain = [f"$EXP[Map_LineOn_{ln}]", slot_on(ln, k)]
            if not d["dots"]:
                chain.append(f"!$EXP[Map_SF_{ln}{k}]")
            for _col, cond in xdot_checks(ln, k):
                terms.append("[" + " + ".join(chain + [cond]) + "]")
    e.append(f'<expression name="Map_AnyXdot">{" | ".join(terms)}</expression>')
    return e


def more_vars():
    v = []
    v.append('<variable name="Map_RouteGrey"><value>l_route</value></variable>')
    for k, alb_word, other in (("Right", "Same genre", "Lead actor"), ("Down", "Same year", "Year + genre"), ("Left", "Featured on", "Second star")):
        v.append(f'<variable name="Map_Key{k}"><value condition="String.IsEqual({prop("kind")},albums)">{alb_word}</value><value>{other}</value></variable>')
    v.append('<variable name="Map_KeyUp">')
    v.append(f'\t<value condition="String.IsEqual({prop("kind")},albums)">Artist</value>')
    v.append(f'\t<value condition="String.IsEqual({prop("kind")},tvshows)">Network</value>')
    v.append("\t<value>Director</value>")
    v.append("</variable>")
    v.append('<variable name="Map_HintOK">')
    v.append(f'\t<value condition="Control.HasFocus(700) + String.IsEqual({prop("kind")},albums)">open the album</value>')
    v.append('\t<value condition="Control.HasFocus(700)">station page and play</value>')
    v.append('\t<value condition="Control.HasFocus(790)">the A-Z index</value>')
    v.append("\t<value>change here</value>")
    v.append("</variable>")
    v.append('<variable name="Map_NS_RatingNum">')
    for ln, d in LINES.items():
        sl = f"Container({d['lst']}).ListItem"
        v.append(f'	<value condition="Control.HasFocus({d["btn"]})">$INFO[{sl}.Rating]</value>')
    v.append('	<value condition="$EXP[Map_DetailsMatch]">$INFO[Container(9001).ListItem.Rating]</value>')
    v.append("</variable>")
    v.append('<variable name="Map_NS_RatingTxt">')
    for ln, d in LINES.items():
        s = f"Container({d['lst']}).ListItem"
        v.append(f'\t<value condition="Control.HasFocus({d["btn"]}) + !String.IsEmpty({s}.Rating)"> · $INFO[{s}.Rating]/10</value>')
    v.append('\t<value condition="$EXP[Map_DetailsMatch] + !String.IsEmpty(Container(9001).ListItem.Rating) + !Control.HasFocus(701) + !Control.HasFocus(702) + !Control.HasFocus(703) + !Control.HasFocus(704)"> · $INFO[Container(9001).ListItem.Rating]/10</value>')
    v.append("</variable>")
    return v


def build_includes():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_map.py - edit the generator, not this file. The map: see the generator docstring. -->",
             "<includes>"]
    parts += ["\t" + x for x in "\n".join(variables() + more_vars()).split("\n")]
    parts += ["\t" + x for x in "\n".join(expressions() + slot_expressions()).split("\n")]

    def inc(name, body):
        parts.append(f'\t<include name="{name}">')
        parts.extend("\t\t" + x for x in "\n".join(body).split("\n"))
        parts.append("\t</include>")

    inc("Map_Data", data())
    lines = []
    for ln, (dx, dy) in (("up", (40, 30)), ("right", (-60, 0)), ("down", (-40, -40)), ("left", (60, 0))):
        g = line_track(ln)
        d = LINES[ln]
        for k in range(d["k"]):
            g.append(dot_slot(ln, k) if d["dots"] else poster_slot(ln, k))
        g.append(line_label(ln))
        lines.append(group(g, vis=f"$EXP[Map_LineOn_{ln}]", anims=anim_line_reveal(dx, dy), desc=f"line {ln}"))
    # draw order: right and left posters can overlap the centre's shadow only; centre drawn after lines
    inc("Map_Lines", [lines[0], lines[2], lines[1], lines[3]])
    inc("Map_Centre", centre())
    inc("Map_NextStop", next_stop())
    inc("Map_Hints", hints())
    inc("Map_Compass", [compass()])
    inc("SD_RouteBar", [route_bar()])
    inc("SD_BrandAndClock", brand_and_right())
    inc("Map_Buttons", buttons())
    # boarding: other windows call this with the item to start from (route cleared)
    board = []
    for i in range(1, DEPTH + 1):
        for f in FIELDS:
            board.append(f"ClearProperty({P}.r{i}.{f},home)")
    parts.append('\t<include name="SD_BoardActions">')
    parts.append('\t\t<param name="src">ListItem</param>')
    parts.append('\t\t<param name="kind">movies</param>')
    parts.append('\t\t<param name="is_album">false</param>')
    parts.append('\t\t<param name="is_tv">false</param>')
    parts.append("\t\t<definition>")
    # 0.9.2: kind-aware (albums read Label / thumb / Artist, series the network), sets the genre too,
    # and closes any dialog first (used by the album info dialog's "Board the map")
    src = "$PARAM[src]"
    # String.IsEqual(albums,albums) is always false (the first argument must be an infolabel): the caller
    # passes is_album / is_tv = true instead
    alb, tv = "$PARAM[is_album]", "$PARAM[is_tv]"
    acts = [(a, None) for a in board + set_centre_actions(src, "route")]
    acts += [(f"SetProperty({P}.c.dir,$ESCINFO[{src}.Director],home)", None),
             (f"SetProperty({P}.c.genre,$ESCINFO[{src}.Genre],home)", None),
             (f"SetProperty({P}.c.dir,$ESCINFO[{src}.Studio],home)", tv),
             (f"SetProperty({P}.c.title,$ESCINFO[{src}.Label],home)", alb),
             (f"SetProperty({P}.c.poster,$ESCINFO[{src}.Art(thumb)],home)", alb),
             (f"SetProperty({P}.c.dir,$ESCINFO[{src}.Artist],home)", alb),
             (f"SetProperty({P}.kind,$PARAM[kind],home)", None),
             (f"SetProperty({P}.from,start,home)", None), (f"SetProperty({P}.flip,$VAR[Map_FlipNext],home)", None),
             ("Dialog.Close(all,true)", None), ("ActivateWindow(1160)", None)]
    for a, c in acts:
        parts.append("\t\t" + tag("onclick", a, c))
    parts.append("\t\t</definition>")
    parts.append("\t</include>")
    parts.append("</includes>")
    (OUT / "Includes_Map.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


def build_window():
    w = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_map.py. The map (custom window 1160): centre station + four lines.
	Focus: 700 centre, 701 up line, 702 right, 703 down, 704 left (invisible buttons that drive the lists
	611-614 with Control.Move), 790 Index, 799 Back = route pop (hidden focus). See SPEC.md section 3.
-->
<window type="window" id="1160">
	<defaultcontrol always="true">700</defaultcontrol>
	<backgroundcolor>ground</backgroundcolor>
	<onload condition="String.IsEmpty(Window(Home).Property({P}.flip))">SetProperty({P}.flip,a,home)</onload>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>SD_Background</include>
		<include>Map_Data</include>
		<include>Map_Lines</include>
		<include>Map_Centre</include>
		<include>Map_NextStop</include>
		<include>Map_Hints</include>
		<include>Map_Compass</include>
		<include>SD_BrandAndClock</include>
		<include>SD_RouteBar</include>
		<include>Map_Buttons</include>
	</controls>
</window>
"""
    (OUT / "Custom_1160_Map.xml").write_text(w, encoding="utf-8")


def expand_exp(text, defs=None):
    """Timers don't expand $EXP[]: inline the generated expressions (recursively)."""
    import re as _re
    if defs is None:
        defs = {}
        for e in expressions() + slot_expressions():
            m = _re.match(r'<expression name="([^"]+)">(.*)</expression>', e)
            defs[m.group(1)] = m.group(2)
    for _ in range(6):
        text = _re.sub(r"\$EXP\[([A-Za-z0-9_]+)\]", lambda m: "[" + defs[m.group(1)] + "]", text)
    return text


def map_timers():
    """Arriving from a station page's line row: focus that line once it has loaded."""
    t = []
    for ln, d in LINES.items():
        t += ["	<timer>",
              f"		<name>sd_enter_{ln}</name>",
              f"		<start reset=\"false\">Window.IsActive(1160) + String.IsEqual({prop('enterline')},{ln}) + {expand_exp(f'$EXP[Map_LineOn_{ln}]')}</start>",
              f"		<stop>String.IsEmpty({prop('enterline')}) | !Window.IsActive(1160)</stop>",
              f"		<onstart>ClearProperty({P}.enterline,home)</onstart>"]
        t += [f"		<onstart>{a}</onstart>" for a in enter(ln)]
        t.append("	</timer>")
    # a line that never loads (no second star): drop the request after the map is ready
    t += ["	<timer>", "		<name>sd_enter_none</name>",
          f"		<start reset=\"false\">Window.IsActive(1160) + !String.IsEmpty({prop('enterline')}) + System.IdleTime(3)</start>",
          f"		<stop>String.IsEmpty({prop('enterline')})</stop>",
          f"		<onstart>ClearProperty({P}.enterline,home)</onstart>", "	</timer>"]
    # 0.9.2: re-centred from a station page opened on the map: once the dialog is gone, rewind the lines
    # and land on the new centre (a line's own OK does this inline)
    t += ["	<timer>", "		<name>sd_landcentre</name>",
          f"		<start reset=\"false\">Window.IsActive(1160) + !String.IsEmpty({prop('landcentre')}) + !Window.IsVisible(movieinformation) + !Window.IsVisible(DialogBusy.xml)</start>",
          f"		<stop>String.IsEmpty({prop('landcentre')})</stop>",
          f"		<onstart>ClearProperty({P}.landcentre,home)</onstart>"]
    for L in LINES.values():
        t += [f"		<onstart>{a}</onstart>" for a in reset(L["lst"])]
    t += [f"		<onstart condition=\"String.IsEmpty({prop('enterline')})\">SetFocus(700)</onstart>", "	</timer>"]
    # 0.9.2: boarding from a dialog (Dialog.Close(all,true) + ActivateWindow(1160)) left the map with NO focused
    # control on the Shield, so the first key press was swallowed. Safety net: map on top, nothing focused -> centre.
    t += ["	<timer>", "		<name>sd_mapfocus</name>",
          "		<start reset=\"false\">Window.IsActive(1160) + String.IsEmpty(System.CurrentControlId) + String.IsEmpty(" + prop('enterline') + ")</start>",
          "		<stop>!String.IsEmpty(System.CurrentControlId) | !Window.IsActive(1160)</stop>",
          "		<onstart>SetFocus(700)</onstart>", "	</timer>"]
    return t


if __name__ == "__main__":
    build_includes()
    build_window()
    print("wrote Includes_Map.xml + Custom_1160_Map.xml")
