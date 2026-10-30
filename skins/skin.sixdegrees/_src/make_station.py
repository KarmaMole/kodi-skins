"""Six Degrees station page (DialogVideoInfo) -> 1080i/DialogVideoInfo.xml + 1080i/Includes_VideoInfo.xml.

Board: docs/concepts/round4/mockups/SixDegreesStation.html (boards2.py board_station).

Kodi id contract (Estuary Omega DialogVideoInfo.xml / CGUIDialogVideoInfo): 8 play (from the start when
resumable; browse for tvshow / season / set), 9 resume (enabled by Kodi only with a resume point), 11 trailer,
50 cast list (set: the films of the set), 6 refresh, 7 user rating, 10 choose art, 12 choose fanart,
13 director search, 14 versions, 15 extras, 443 go to collection (Estuary convention). Kodi's buttons are
kept offscreen and clicked from our pills (SendClick) so every pill has a fixed width (rule 5).

Six Degrees ids: 9000 pill row (9001 Play/Resume, 9002 From start, 9003 Trailer, 9004 Board this line,
9005 More), 9100 More row, 9200 full story (focus 61 / 9203), 9301-9304 the four lines (OK = board the map on that line),
data: 9601 skinvariables details, 9611-9614 lines, 9621-9623 second-star probes.
A map station opened with Info is a script.skinvariables item (a folder): Play then uses its file.

    python skins/skin.sixdegrees/_src/make_station.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import ImageFont
from localize import localize_xml  # literal label words -> $LOCALIZE[id] from strings.po (kdk labels.not-translated)
STRINGS_PO = Path(__file__).resolve().parent.parent / "language" / "resource.language.en_gb" / "strings.po"

from make_map import (P, RM, OPEN, rule, close, prop, info, img, lbl, group, DEPTH, FIELDS, push_actions,
                      ruleq, qvar, kdk_mute, Encoder, excl_value)

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
OUT = SKIN / "1080i"
FONTS = SKIN / "fonts"


def width(text, font, size):
    f = ImageFont.truetype(str(FONTS / font), size)
    return int(f.getlength(text)) + len(text) + 4  # lesson: Kodi lays labels out ~1 px per glyph wider


XB = "SixDegreesText-ExtraBold.ttf"
SEMI = "SixDegreesText-SemiBold.ttf"

PX, PY, PW, PH = 78, 176, 330, 495
TX = 480
IS_MOVIE = "String.IsEqual(ListItem.DBType,movie)"
IS_TV = "String.IsEqual(ListItem.DBType,tvshow)"
HAS_LINES = f"[{IS_MOVIE} | {IS_TV}]"
IS_EP = "String.IsEqual(ListItem.DBType,episode)"
IS_SET = "String.IsEqual(ListItem.DBType,set)"
IS_SEASON = "String.IsEqual(ListItem.DBType,season)"
PLUGIN_MOVIE = f"{IS_MOVIE} + ListItem.IsFolder + !String.IsEmpty(ListItem.Property(file))"

ROWS = [  # key, colour, arrow, kind word, list id, trunk x
    ("up", "l_dir", "up", "$VAR[St_KindUp]", 9611, 264),
    ("right", "l_lead", "right", "lead", 9612, 250),
    ("down", "l_yg", "down", "year + genre", 9613, 236),
    ("left", "l_co", "left", "second star", 9614, 222),
]
ROW_Y0, ROW_DY = 782, 70


def tag(name, value, cond=None):
    c = f' condition="{cond}"' if cond else ""
    return f"<{name}{c}>{value}</{name}>"


# gate: the details list has this item (movie / show), or there is no details list for this kind
# slot toggle sixdegrees.st.slot: flipped in the window's onload (one centre per opening)
ST_ENC = Encoder("St", ["ListItem.DBType", "ListItem.DBID", "Container(9601).ListItem.DBID"],
                 f"[$EXP[St_Match] | [!{IS_MOVIE} + !{IS_TV}]]", "st.slot")


# ------------------------------------------------------------------ variables
def variables():
    v = []
    a = v.append
    sv = "System.AddonIsEnabled(script.skinvariables)"
    a('<variable name="St_Details">')
    a(f'\t<value condition="{sv} + {IS_TV}">plugin://script.skinvariables/?info=get_dbitem_tvshow_details&amp;dbid=$INFO[ListItem.DBID]</value>')
    a(f'\t<value condition="{sv} + {IS_MOVIE}">plugin://script.skinvariables/?info=get_dbitem_movie_details&amp;dbid=$INFO[ListItem.DBID]</value>')
    a("</variable>")
    a(f'<expression name="St_Match">{sv} + String.IsEqual(Container(9601).ListItem.DBID,ListItem.DBID) + !String.IsEmpty(ListItem.DBID) + String.IsEqual(Container(9601).ListItem.DBType,ListItem.DBType)</expression>')
    a('<variable name="St_Up">')
    a(f'\t<value condition="$EXP[St_Match] + {IS_TV}">$INFO[Container(9601).ListItem.Property(studio.0)]</value>')
    a(f'\t<value condition="$EXP[St_Match]">$INFO[Container(9601).ListItem.Property(director.0)]</value>')
    a(f'\t<value condition="{IS_TV}">$INFO[ListItem.Studio]</value>')
    a("\t<value>$INFO[ListItem.Director]</value>")
    a("</variable>")
    for n in range(4):
        a(f'<variable name="St_Cast{n}"><value condition="$EXP[St_Match]">$INFO[Container(9601).ListItem.Property(cast.{n}.name)]</value></variable>')
    a('<variable name="St_Co">')
    for n, cid in ((1, 9621), (2, 9622), (3, 9623)):
        a(f'\t<value condition="Integer.IsGreaterOrEqual(Container({cid}).NumItems,2)">$VAR[St_Cast{n}]</value>')
    a("\t<value>$VAR[St_Cast1]</value>")
    a("</variable>")
    # 0.9.7: free text goes into the xsp JSON as $ESCINFO string literals; '&' / '%' values become ""
    v.extend(qvar("St_UpQ", [(f"$EXP[St_Match] + {IS_TV}", "Container(9601).ListItem.Property(studio.0)"),
                             ("$EXP[St_Match]", "Container(9601).ListItem.Property(director.0)"),
                             (IS_TV, "ListItem.Studio"),
                             (None, "ListItem.Director")], ST_ENC))
    for n in range(4):
        v.extend(qvar(f"St_Cast{n}Q", [("$EXP[St_Match]", f"Container(9601).ListItem.Property(cast.{n}.name)")], ST_ENC))
    v.extend(qvar("St_GenreQ", [("$EXP[St_Match]", "Container(9601).ListItem.Property(genre.0)")], ST_ENC))
    a('<variable name="St_CoQ">')
    for n, cid in ((1, 9621), (2, 9622), (3, 9623)):
        a(f'\t<value condition="Integer.IsGreaterOrEqual(Container({cid}).NumItems,2)">$VAR[St_Cast{n}Q]</value>')
    a("\t<value>$VAR[St_Cast1Q]</value>")
    a("</variable>")
    a('<variable name="St_Excl">')
    for v_ in excl_value(ST_ENC, "title", "ListItem.Title"):
        a("\t" + v_)
    a("</variable>")
    roots = {"movies": "videodb://movies/titles/?xsp=", "tvshows": "videodb://tvshows/titles/?xsp="}
    upf = {"movies": "director", "tvshows": "studio"}
    for kind in roots:
        tail = f"$VAR[St_Excl]{close(kind)}"
        R = roots[kind]
        paths = {
            "up": f"{R}{OPEN}{ruleq(upf[kind], 'is', '$VAR[St_UpQ]')}{tail}",
            "right": f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[St_Cast0Q]')}{tail}",
            "left": f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[St_CoQ]')}{tail}",
            "down": f"{R}{OPEN}{rule('year', 'is', '$INFO[ListItem.Year]')}%2C{ruleq('genre', 'is', '$VAR[St_GenreQ]')}{tail}",
            "downy": f"{R}{OPEN}{rule('year', 'is', '$INFO[ListItem.Year]')}{tail}",
            "p1": f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[St_Cast1Q]')}{tail}",
            "p2": f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[St_Cast2Q]')}{tail}",
            "p3": f"{R}{OPEN}{ruleq('actor', 'is', '$VAR[St_Cast3Q]')}{tail}",
        }
        for k, pth in paths.items():
            a(f'<variable name="St_Path_{k}_{kind}"><value>{pth}</value></variable>')
    for k in ("up", "right", "left", "p1", "p2", "p3"):
        a(f'<variable name="St_Path_{k}">')
        a(f'\t<value condition="!{HAS_LINES}">videodb://movies/sets/</value>')
        a(f'\t<value condition="{IS_TV}">$VAR[St_Path_{k}_tvshows]</value>')
        a(f"\t<value>$VAR[St_Path_{k}_movies]</value>")
        a("</variable>")
    a('<variable name="St_Path_down">')
    a(f'\t<value condition="!{HAS_LINES}">videodb://movies/sets/</value>')
    a(f'\t<value condition="{IS_TV} + $EXP[St_Match] + !String.IsEmpty(Container(9601).ListItem.Property(genre.0))">$VAR[St_Path_down_tvshows]</value>')
    a(f'\t<value condition="{IS_TV}">$VAR[St_Path_downy_tvshows]</value>')
    a('\t<value condition="$EXP[St_Match] + !String.IsEmpty(Container(9601).ListItem.Property(genre.0))">$VAR[St_Path_down_movies]</value>')
    a("\t<value>$VAR[St_Path_downy_movies]</value>")
    a("</variable>")
    a('<variable name="St_Name_up"><value>$VAR[St_Up]</value></variable>')
    a('<variable name="St_Name_right"><value>$VAR[St_Cast0]</value></variable>')
    a('<variable name="St_Name_left"><value>$VAR[St_Co]</value></variable>')
    a('<variable name="St_Name_down">')
    a('\t<value condition="$EXP[St_Match] + !String.IsEmpty(Container(9601).ListItem.Property(genre.0))">$INFO[ListItem.Year] · $INFO[Container(9601).ListItem.Property(genre.0)]</value>')
    a("\t<value>$INFO[ListItem.Year]</value>")
    a("</variable>")
    a('<variable name="St_KindUp">')
    a(f'\t<value condition="{IS_TV}">network</value>')
    a("\t<value>director</value>")
    a("</variable>")
    # caption over the title
    a('<variable name="St_Caption">')
    a(f'\t<value condition="{IS_EP}">Station · $INFO[ListItem.TVShowTitle] · $INFO[ListItem.Season,S,]$INFO[ListItem.Episode, E,]</value>')
    a(f'\t<value condition="{IS_SEASON}">Station · $INFO[ListItem.TVShowTitle]</value>')
    # 0.9.10: the Line view shows this caption too, where Container(50) is not the set's films ("0 films" for a
    # 4-film set); a set item carries its count in Property(Total) (Daylight / Fold); the dialog's list 50 stays
    # the fallback
    # 2026-10-30: "1 film", not "1 films"
    a(f'\t<value condition="{IS_SET} + Integer.IsEqual(ListItem.Property(Total),1)">Collection · 1 film</value>')
    a(f'\t<value condition="{IS_SET} + !String.IsEmpty(ListItem.Property(Total))">Collection$INFO[ListItem.Property(Total), · , films]</value>')
    a(f'\t<value condition="{IS_SET} + Window.IsVisible(movieinformation) + Integer.IsEqual(Container(50).NumItems,1)">Collection · 1 film</value>')
    a(f'\t<value condition="{IS_SET} + Window.IsVisible(movieinformation)">Collection$INFO[Container(50).NumItems, · , films]</value>')
    a(f'\t<value condition="{IS_SET}">Collection</value>')
    a("\t<value>Station$INFO[ListItem.Year, · ,] · $VAR[St_GenreCaps]</value>")
    a("</variable>")
    a('<variable name="St_GenreCaps"><value>$INFO[ListItem.Genre]</value></variable>')
    # facts row values (separators drawn as hair pipes)
    # 0.9.10: a pipe shows only between two shown parts (part shown + any earlier part shown). Sets have no
    # director / time / MPAA, so the old per-part pipes drew a stray "|" before the rating. Used by the
    # station page and the Line view (Includes_Views_Video.xml).
    tvlike = f"[{IS_TV} | {IS_EP} | {IS_SEASON}]"
    on = {"Lead": f"[{tvlike} + !String.IsEmpty(ListItem.Studio)] | [!{tvlike} + !String.IsEmpty(ListItem.Director)]",
          "Time": f"Integer.IsGreater(ListItem.Duration,0) | [{IS_TV} + !String.IsEmpty(ListItem.Property(TotalSeasons))]",
          "Mpaa": "!String.IsEmpty(ListItem.MPAA)",
          "Rating": "!String.IsEmpty(ListItem.Rating)"}
    keys = list(on)
    for k in keys:
        a(f'<expression name="St_Fact{k}_On">[{on[k]}]</expression>')  # bracketed: safe inside + and |
    for i, k in enumerate(keys[1:] + ["Watched"], start=1):
        before = " | ".join(f"$EXP[St_Fact{x}_On]" for x in keys[:i])
        mine = "" if k == "Watched" else f"$EXP[St_Fact{k}_On] + "
        a(f'<expression name="St_FactPipe_{k}">{mine}[{before}]</expression>')
    a('<variable name="St_FactLead">')
    a(f'\t<value condition="{IS_TV} | {IS_EP} | {IS_SEASON}">$INFO[ListItem.Studio]</value>')
    a("\t<value>$INFO[ListItem.Director]</value>")
    a("</variable>")
    a('<variable name="St_FactTime">')
    a('\t<value condition="Integer.IsGreater(ListItem.Duration(h),0)">$INFO[ListItem.Duration(h),, h ]$INFO[ListItem.Duration(mm)]</value>')
    a('\t<value condition="Integer.IsGreater(ListItem.Duration(m),0)">$INFO[ListItem.Duration(m),, min]</value>')
    a(f'\t<value condition="{IS_TV} + Integer.IsEqual(ListItem.Property(TotalSeasons),1)">1 season</value>')
    a(f'\t<value condition="{IS_TV}">$INFO[ListItem.Property(TotalSeasons),, seasons]</value>')
    a("</variable>")
    a('<variable name="St_FactWatched">')
    a(f'\t<value condition="{IS_TV} | {IS_SEASON}">$INFO[ListItem.Property(UnWatchedEpisodes),, unwatched]</value>')
    a('\t<value condition="ListItem.IsResumable">$INFO[ListItem.PercentPlayed,,% watched]</value>')
    a('\t<value condition="Integer.IsGreater(ListItem.PlayCount,0)">watched</value>')
    a("\t<value>never watched</value>")
    a("</variable>")
    a('<variable name="St_Arrives">')
    a('\t<value condition="ListItem.IsResumable">$INFO[ListItem.EndTimeResume]</value>')
    a("\t<value>$INFO[ListItem.EndTime]</value>")
    a("</variable>")
    a('<variable name="St_PlayLabel">')
    a(f'\t<value condition="{IS_TV} | {IS_SEASON} | {IS_SET}">Open</value>')
    a('\t<value condition="Control.IsEnabled(9) + !ListItem.IsFolder">Resume</value>')
    a("\t<value>Play</value>")
    a("</variable>")
    a('<variable name="St_Poster">')
    a(f'\t<value condition="{IS_EP} + !String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>')
    a(f'\t<value condition="{IS_SEASON} + !String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>')
    a('\t<value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>')
    a("\t<value>$INFO[ListItem.Art(thumb)]</value>")
    a("</variable>")
    a('<variable name="St_Wide">')
    a(f'\t<value condition="{IS_EP} + !String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>')
    a('\t<value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>')
    a('\t<value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>')
    a("\t<value>$INFO[ListItem.Art(tvshow.fanart)]</value>")
    a("</variable>")
    for key, col, arrow, kind, cid, tx in ROWS:
        a(f'<expression name="St_Row_{key}">{HAS_LINES} + Integer.IsGreater(Container({cid}).NumItems,0) + !Container({cid}).IsUpdating + [$EXP[St_Match] | !{sv}]</expression>')
    return v


# ------------------------------------------------------------------ pieces
def top():
    out = [img(64, 66, 44, 44, "sd/wordmark.png"), lbl(122, 64, 290, 48, "Six Degrees", "xb_28", "ink")]
    gl = ['<control type="grouplist"><left>420</left><top>72</top><width>1160</width><height>36</height>',
          "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
          '<control type="group"><width>30</width><height>36</height>' + img(2, 6, 24, 24, "sd/disc_18.png", diffuse="white")
          + img(2, 6, 24, 24, "sd/ring_18_5.png", diffuse="l_route") + "</control>",
          '<control type="label"><width>auto</width><height>36</height><font>semi_24</font><textcolor>ink2</textcolor><label>Start</label></control>',
          '<control type="label"><width>16</width><height>36</height><label></label></control>',
          '<control type="image"><top>15</top><width>96</width><height>6</height><texture border="3,0,3,0" colordiffuse="l_route">sd/line_h6.png</texture></control>',
          '<control type="group"><width>44</width><height>36</height>' + img(-1, -1, 38, 38, "sd/disc_32.png", diffuse="white")
          + img(-1, -1, 38, 38, "sd/ring_32_8.png", diffuse="ink") + "</control>",
          '<control type="label"><width max="900">auto</width><height>36</height><font>xb_24</font><textcolor>ink</textcolor><label>$INFO[ListItem.Title]</label></control>',
          "</control>"]
    out.append("\n".join(gl))
    out.append('<control type="label"><left>1500</left><top>62</top><width>356</width><height>48</height><font>xb_30</font>'
               "<textcolor>ink</textcolor><align>right</align><label>$INFO[System.Time]</label></control>")
    return out


def poster():
    o = 14
    return [img(PX - o - 72, PY - o - 50, PW + 2 * o + 144, PH + 2 * o + 144, "sd/shadow_big.png", diffuse="shadow", border="100"),
            img(PX - o, PY - o, PW + 2 * o, PH + 2 * o, "sd/ring_centre_fill.png", diffuse="ground", border="24"),
            img(PX - o, PY - o, PW + 2 * o, PH + 2 * o, "sd/ring_centre.png", diffuse="ink", border="24"),
            img(PX, PY, PW, PH, "common/white.png", diffuse="wash"),
            lbl(PX + 20, PY + 20, PW - 40, 160, "$INFO[ListItem.Title]", "xb_28", "ink2", aligny="top", wrap=True),
            '<control type="image">'
            f"<left>{PX}</left><top>{PY}</top><width>{PW}</width><height>{PH}</height><aspectratio>scale</aspectratio><fadetime>150</fadetime>"
            f'<texture background="true" diffuse="sd/mask_330x495.png">$VAR[St_Poster]</texture></control>']


def text_column():
    ch = [lbl(TX, 168, 1376, 30, "$VAR[St_Caption]", "caps_21", "ink2", aligny="top")]
    # title tiers: 84 if it fits 1376 px, else 60 (probe 9701)
    ch.append('<control type="textbox" id="9701"><left>480</left><top>200</top><width>1376</width><height>96</height>'
              "<font>disp_84</font><textcolor>clear</textcolor><label>$INFO[ListItem.Title]</label></control>")
    ch.append(lbl(TX - 4, 196, 1380, 104, "$INFO[ListItem.Title]", "disp_84", "ink", vis="!Integer.IsGreater(Container(9701).NumPages,1)"))
    ch.append(lbl(TX - 2, 210, 1380, 80, "$INFO[ListItem.Title]", "disp_60", "ink", vis="Integer.IsGreater(Container(9701).NumPages,1)"))
    # facts: Director | 1 h 40 | Rated R | (star) 8.0 | Studio | never watched
    def fact(text, vis="true", first=False, pipe_vis=None):
        pipe = "" if first else ('<control type="label"><width>34</width><height>40</height><font>semi_26</font><textcolor>hair_strong</textcolor>'
                                 f"<align>center</align><label>|</label><visible>{pipe_vis or vis}</visible></control>")
        return pipe + (f'<control type="label"><width max="420">auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor>'
                       f"<label>{text}</label><visible>{vis}</visible></control>")
    gl = ['<control type="grouplist"><left>480</left><top>308</top><width>1376</width><height>40</height>',
          "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
          fact("$VAR[St_FactLead]", "$EXP[St_FactLead_On]", first=True),
          fact("$VAR[St_FactTime]", "$EXP[St_FactTime_On]", pipe_vis="$EXP[St_FactPipe_Time]"),
          fact("$INFO[ListItem.MPAA]", "$EXP[St_FactMpaa_On]", pipe_vis="$EXP[St_FactPipe_Mpaa]"),
          '<control type="label"><width>34</width><height>40</height><font>semi_26</font><textcolor>hair_strong</textcolor><align>center</align><label>|</label><visible>$EXP[St_FactPipe_Rating]</visible></control>',
          '<control type="image"><top>9</top><width>22</width><height>22</height><texture colordiffuse="ink">sd/star.png</texture><visible>!String.IsEmpty(ListItem.Rating)</visible></control>',
          '<control type="label"><left>8</left><width>auto</width><height>40</height><font>semi_26</font><textcolor>ink</textcolor><label>$INFO[ListItem.Rating]</label><visible>!String.IsEmpty(ListItem.Rating)</visible></control>',
          fact("$VAR[St_FactWatched]", pipe_vis="$EXP[St_FactPipe_Watched]"),
          "</control>"]
    ch.append("\n".join(gl))
    # journey: now -> arrives (OSD idea as an inset)
    jy, j0, j1 = 398, TX + 150, TX + 640
    jr = [lbl(TX, jy - 20, 140, 40, "$INFO[System.Time]", "xb_24", "ink"),
          img(j0, jy - 3, j1 - j0, 6, "sd/line_h6.png", diffuse="l_route", border="3,0,3,0"),
          img(j0 - 16, jy - 16, 32, 32, "sd/disc_26.png", diffuse="white"),
          img(j0 - 16, jy - 16, 32, 32, "sd/ring_26_7.png", diffuse="ink"),
          img(j1 - 13, jy - 13, 26, 26, "sd/disc_20.png", diffuse="ink"),
          '<control type="grouplist">' f"<left>{j1 + 24}</left><top>{jy - 20}</top><width>500</width><height>40</height>"
          "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
          '<control type="label"><width>auto</width><height>40</height><font>semi_24</font><textcolor>ink2</textcolor><label>arrives </label></control>'
          '<control type="label"><width>auto</width><height>40</height><font>xb_24</font><textcolor>ink</textcolor><label>$VAR[St_Arrives]</label></control>'
          "</control>"]
    ch.append(group(jr, vis="Integer.IsGreater(ListItem.Duration,0) + !ListItem.IsFolder | " + PLUGIN_MOVIE, desc="journey"))
    ch.append('<control type="textbox" id="9010"><left>480</left><top>440</top><width>760</width><height>156</height>'
              "<font>reg_26</font><textcolor>body</textcolor><label>$INFO[ListItem.Plot]</label></control>")
    # 4 lines; Kodi drops the rest silently, so mark the overflow with a fade and "…" (More > Full story reads it)
    over = "Integer.IsGreater(Container(9010).NumPages,1)"
    ch += [img(1240 - 150, 440 + 117, 150, 39, "common/gradient_right.png", diffuse="ground", vis=over),
           img(1240 - 40, 440 + 117, 40, 39, "common/white.png", diffuse="ground", vis=over),
           lbl(1240 - 40, 440 + 117, 40, 39, "…", "reg_26", "body", align="right", vis=over)]
    # fanart framed (episode: its still)
    has_wide = ("[!String.IsEmpty(ListItem.Art(fanart)) | !String.IsEmpty(ListItem.Art(landscape)) | "
                "!String.IsEmpty(ListItem.Art(tvshow.fanart)) | [String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb))]]")
    ch.append(group([img(1296 - 20, 420 - 10, 600, 360, "sd/shadow_poster.png", diffuse="shadow", border="40"),
                     img(1296, 420, 560, 315, "common/white.png", diffuse="wash"),
                     '<control type="image"><left>1296</left><top>420</top><width>560</width><height>315</height><aspectratio>scale</aspectratio><fadetime>200</fadetime>'
                     '<texture background="true" diffuse="sd/mask_560x315.png">$VAR[St_Wide]</texture></control>'],
                    vis=has_wide, desc="fanart"))
    return ch


# ------------------------------------------------------------------ buttons
def pill(cid, w, label_var, primary, nav, vis, icon=None):
    """Text-tight pill inside a group (room for the 9 px focus ring). The text is a separate label: a button
    clips its own label to width - 2 x textoffsetx, which made "Resume" scroll inside a tight pill."""
    tex_nf = '<texturenofocus border="32" colordiffuse="ink">sd/pill_64.png</texturenofocus>' if primary else         '<texturenofocus border="32" colordiffuse="hair">sd/pill_64_o3.png</texturenofocus>'
    font = "xb_24" if primary else "semi_24"
    lbl_off = 28 + (30 if icon else 0)
    b = [f'<control type="group" id="{cid + 100}"><width>{w + 18}</width><height>82</height><visible>{vis}</visible>',
         f'<control type="button" id="{cid}"><left>9</left><top>9</top><width>{w}</width><height>64</height><label></label>',
         '<texturefocus border="32" colordiffuse="ink">sd/pill_64.png</texturefocus>', tex_nf]
    b += nav
    b.append("</control>")
    b.append(img(0, 0, w + 18, 82, "sd/pill_82_ring.png", diffuse="ink", border="41", vis=f"Control.HasFocus({cid})"))
    if primary:
        b.append(lbl(9 + lbl_off, 9, w - lbl_off, 64, label_var, font, "white"))
    else:
        b.append(lbl(9 + lbl_off, 9, w - lbl_off, 64, label_var, font, "ink", vis=f"!Control.HasFocus({cid})"))
        b.append(lbl(9 + lbl_off, 9, w - lbl_off, 64, label_var, font, "white", vis=f"Control.HasFocus({cid})"))
    if icon:
        b.append(img(9 + 28, 9 + 22, 20, 20, icon, diffuse="white", vis=f"Control.HasFocus({cid})" if not primary else "true"))
        if not primary:
            b.append(img(9 + 28, 9 + 22, 20, 20, icon, diffuse="ink", vis=f"!Control.HasFocus({cid})"))
    b.append("</control>")
    return "\n".join(b)


def buttons():
    wplay = max(width("Resume", XB, 24), width("Play", XB, 24), width("Open", XB, 24)) + 28 + 30 + 30
    wfrom = width("From start", SEMI, 24) + 58
    wtrail = width("Trailer", SEMI, 24) + 58
    wboard = width("Board this line", SEMI, 24) + 58
    wmore = width("More", SEMI, 24) + 58
    down_rows = [tag("ondown", "9301", "Control.IsVisible(9301)"),
                 tag("ondown", "50", f"{IS_SET} + Integer.IsGreater(Container(50).NumItems,0)")]
    common = down_rows + [tag("onup", "noop")]
    play_acts = [tag("onclick", f"PlayMedia($ESCINFO[ListItem.Property(file)],resume)", PLUGIN_MOVIE),
                 tag("onclick", "SendClick(9)", f"!ListItem.IsFolder + Control.IsEnabled(9)"),
                 tag("onclick", "SendClick(8)", f"[ListItem.IsFolder + !{IS_MOVIE}] | [!ListItem.IsFolder + !Control.IsEnabled(9)]")]
    board = board_from_info()
    specs = [(9001, wplay, "$VAR[St_PlayLabel]", True, play_acts, "true", "sd/tri_right.png"),
             (9002, wfrom, "From start", False, [tag("onclick", "SendClick(8)")], "Control.IsEnabled(9) + !ListItem.IsFolder", None),
             (9003, wtrail, "Trailer", False, [tag("onclick", "SendClick(11)")],
              "!Skin.HasSetting(sixdegrees.hidetrailer) + !String.IsEmpty(ListItem.Trailer) + ![Control.IsEnabled(9) + !ListItem.IsFolder]", None),
             (9004, wboard, "Board this line", False, board, f"{HAS_LINES} + Integer.IsGreater(ListItem.DBID,0)", None),
             (9005, wmore, "More", False, [tag("onclick", "SetFocus(9100)")], "true", None)]
    ids = [sp[0] for sp in specs]
    gl = ['<control type="grouplist" id="9000"><left>471</left><top>617</top><width>1400</width><height>82</height>',
          "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
          "<onleft>noop</onleft><onright>noop</onright>"]
    for i, (cid, w, label, primary, acts, vis, icon) in enumerate(specs):
        # buttons inside grouplist child groups get no automatic Left/Right (device 2026-10-19):
        # chain each pill to the next / previous VISIBLE pill (the first matching numeric id wins)
        nav = [tag("onright", f"{n}", f"Control.IsVisible({n + 100})") for n in ids[i + 1:]]
        nav += [tag("onleft", f"{n}", f"Control.IsVisible({n + 100})") for n in reversed(ids[:i])]
        gl.append(pill(cid, w, label, primary, acts + common + nav, vis, icon=icon))
    gl.append("</control>")
    return "\n".join(gl)


def board_from_info():
    """Board the map at the info item. From the map itself: re-centre (push) or just close."""
    on_map = "Window.IsVisible(1160)"
    same = f"String.IsEqual(ListItem.DBID,{prop('c.dbid')})"
    acts = [tag("onclick", "Dialog.Close(movieinformation)", f"{on_map} + {same}")]
    push = push_actions()
    cset = [f"SetProperty({P}.c.dbid,$INFO[ListItem.DBID],home)",
            f"SetProperty({P}.c.title,$ESCINFO[ListItem.Title],home)",
            f"SetProperty({P}.c.year,$INFO[ListItem.Year],home)",
            f"SetProperty({P}.c.poster,$ESCINFO[ListItem.Art(poster)],home)",
            f"SetProperty({P}.c.tmdb,$INFO[ListItem.UniqueID(tmdb)],home)",
            f"SetProperty({P}.c.file,$ESCINFO[ListItem.FileNameAndPath],home)",
            f"SetProperty({P}.c.genre,$ESCINFO[ListItem.Genre],home)"]   # 0.9.2: was left stale
    for a in push + cset + [f"SetProperty({P}.c.dir,$ESCINFO[ListItem.Director],home)", f"SetProperty({P}.c.col,route,home)",
                            f"SetProperty({P}.from,start,home)", f"SetProperty({P}.flip,$VAR[Map_FlipNext],home)",
                            f"SetProperty({P}.landcentre,1,home)"]:
        acts.append(tag("onclick", a, f"{on_map} + !{same}"))
    acts.append(tag("onclick", f"SetProperty({P}.c.dir,$ESCINFO[ListItem.Studio],home)", f"{on_map} + !{same} + {IS_TV}"))
    # 0.9.2: the map's sd_landcentre timer rewinds the line lists and focuses the new centre once the
    # dialog is gone (as an OK on a line does); actions after Dialog.Close would still read the dialog's item
    acts.append(tag("onclick", "Dialog.Close(movieinformation)", f"{on_map} + !{same}"))
    fresh = []
    for i in range(1, DEPTH + 1):
        for f in FIELDS:
            fresh.append(f"ClearProperty({P}.r{i}.{f},home)")
    fresh += cset + [f"SetProperty({P}.c.dir,$ESCINFO[ListItem.Director],home)",
                     f"SetProperty({P}.c.col,route,home)",
                     f"SetProperty({P}.kind,movies,home)"]
    for a in fresh:
        acts.append(tag("onclick", a, f"!{on_map}"))
    acts.append(tag("onclick", f"SetProperty({P}.kind,tvshows,home)", f"!{on_map} + {IS_TV}"))
    acts.append(tag("onclick", f"SetProperty({P}.c.dir,$ESCINFO[ListItem.Studio],home)", f"!{on_map} + {IS_TV}"))
    for a in [f"SetProperty({P}.from,start,home)", f"SetProperty({P}.flip,$VAR[Map_FlipNext],home)",
              "Dialog.Close(all,true)", "ActivateWindow(1160)"]:
        acts.append(tag("onclick", a, f"!{on_map}"))
    return acts


def more_row():
    items = [(443, "Collection", ["Dialog.Close(all,true)", "ActivateWindow(Videos,videodb://movies/sets/$INFO[ListItem.SetId]/?setid=$INFO[ListItem.SetId],return)"],
              "!String.IsEmpty(ListItem.SetID)"),
             (9202, "Trailer", ["SendClick(11)"], "!Skin.HasSetting(sixdegrees.hidetrailer) + !String.IsEmpty(ListItem.Trailer) + Control.IsEnabled(9) + !ListItem.IsFolder"),
             # the card is always processed (faded out), so the textbox's page count is known: a plot longer than
             # the card opens on its scrollbar (Up / Down scroll), a short one on the card's own focus holder 9203
             (9201, "Full story", [("SetFocus(61)", "Integer.IsGreater(Container(9200).NumPages,1)"),
                                   ("SetFocus(9203)", "!Integer.IsGreater(Container(9200).NumPages,1)")],
              "!String.IsEmpty(ListItem.Plot)"),
             (13, "More by director", None, "!String.IsEmpty(ListItem.Director) + !ListItem.IsFolder"),
             (7, "My rating$INFO[ListItem.UserRating,: ,]", None, "Control.IsEnabled(7)"),
             (14, "Versions", None, f"{IS_MOVIE} + !ListItem.IsFolder"),
             (15, "Extras", None, f"{IS_MOVIE} + !ListItem.IsFolder"),
             (10, "Choose art", None, "Control.IsEnabled(10)"),
             (12, "Choose fanart", None, "Control.IsEnabled(12)"),
             (6, "Refresh", None, "Control.IsEnabled(6)")]
    gl = ['<control type="grouplist" id="9100"><left>480</left><top>626</top><width>1376</width><height>48</height>',
          "<orientation>horizontal</orientation><itemgap>12</itemgap>",
          "<onup>9005</onup><ondown>9005</ondown><onback>9005</onback>",
          '<visible allowhiddenfocus="true">ControlGroup(9100).HasFocus()</visible>',
          f'<animation type="Visible" condition="!{RM}"><effect type="fade" start="0" end="100" time="160"/></animation>']
    for cid, label, acts, vis in items:
        b = [f'<control type="button" id="{cid}"><width>auto</width><height>48</height>',
             "<font>semi_22</font><textcolor>ink</textcolor><focusedcolor>white</focusedcolor><textoffsetx>22</textoffsetx>",
             '<texturefocus border="24" colordiffuse="ink">sd/pill_48.png</texturefocus>',
             '<texturenofocus border="24" colordiffuse="hair">sd/pill_48_o3.png</texturenofocus>',
             f"<label>{label}</label><visible>{vis}</visible>"]
        if acts:
            b += [tag("onclick", *a) if isinstance(a, tuple) else tag("onclick", a) for a in acts]
        b.append("</control>")
        gl.append("".join(b))
    gl.append("</control>")
    return "\n".join(gl)


def kodi_hidden():
    out = []
    for cid in (8, 9, 11):
        out.append(f'<control type="button" id="{cid}"><left>-3000</left><top>-3000</top><width>10</width><height>10</height>'
                   "<texturefocus /><texturenofocus /><label></label></control>")
    return out


# ------------------------------------------------------------------ lines
def connectors():
    """Pre-rendered bends for the four rows (generated by make_textures: sd/st_conn_<i>.png)."""
    out = []
    for i, (key, col, arrow, kind, cid, tx) in enumerate(ROWS):
        ry = ROW_Y0 + i * ROW_DY
        x0, y0 = tx - 6, 677
        out.append((key, img(x0, y0, 82, ry + 6 - y0, f"sd/st_conn_{i}.png", diffuse=col, vis=f"$EXP[St_Row_{key}]")))
    return out


def line_rows():
    """Rows close up: line i sits in slot j = how many of the lines before it exist (board order up, right,
    down, left). One focusable button per SLOT (9301-9304); its OK rides whichever line sits in that slot."""
    from itertools import combinations
    ons = [f"$EXP[St_Row_{r[0]}]" for r in ROWS]
    slot_x = [264, 250, 236, 222]

    def occ(i, j):
        """line i is in slot j: line i exists and exactly j of the lines before it exist."""
        before = list(range(i))
        alts = []
        for chosen in combinations(before, j):
            parts = [ons[b] if b in chosen else f"!{ons[b]}" for b in before]
            alts.append(" + ".join(parts) if parts else "true")
        return f"{ons[i]} + [" + " | ".join(f"[{x}]" for x in alts) + "]"

    ch = []
    for i, (key, col, arrow, kind, cid, _tx) in enumerate(ROWS):
        for j in range(i + 1):
            ry = ROW_Y0 + j * ROW_DY
            tx = slot_x[j]
            bid = 9301 + j
            g = [img(tx - 6, 677, 82, ry + 6 - 677, f"sd/st_conn_{j}.png", diffuse=col)]
            for n in range(1, 11):
                xe = 1312 + (n - 1) * 54 + 44
                g.append(img(tx + 70 - 4, ry - 4, xe - tx - 70 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0",
                             vis=f"Integer.IsEqual(Container({cid}).NumItems,{n})"))
                g.append(img(xe - 4, ry - 19, 8, 38, "sd/tick_v8.png", diffuse=col, vis=f"Integer.IsEqual(Container({cid}).NumItems,{n})"))
            g.append(img(tx + 70 - 4, ry - 4, 1856 - tx - 70 + 8, 8, "sd/line_h8.png", diffuse=col, border="4,0,4,0",
                         vis=f"Integer.IsGreater(Container({cid}).NumItems,10)"))
            for k in range(10):
                x = 1312 + k * 54
                v = f"Integer.IsGreater(Container({cid}).NumItems,{k})"
                g.append(img(x - 15, ry - 15, 30, 30, "sd/disc_24.png", diffuse="white", vis=v))
                g.append(img(x - 15, ry - 15, 30, 30, "sd/ring_24_6.png", diffuse=col, vis=v))
            lx = tx + 46 + 26
            gl = ['<control type="grouplist">' f"<left>{lx}</left><top>{ry - 50}</top><width>{1262 - 200 - lx}</width><height>40</height>"
                  "<orientation>horizontal</orientation><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>",
                  img(0, 6, 28, 28, f"sd/badge_28_{arrow}.png", diffuse=col),
                  f'<control type="label"><left>10</left><width max="560">auto</width><height>40</height><font>caps_22</font><textcolor>{col}</textcolor><label>$VAR[St_Name_{key}]</label></control>',
                  f'<control type="label"><left>12</left><width>auto</width><height>40</height><font>caps_20</font><textcolor>ink2</textcolor><label>{kind}</label></control>',
                  "</control>"]
            g.append("\n".join(gl))
            g.append('<control type="grouplist">' f"<left>862</left><top>{ry - 50}</top><width>400</width><height>40</height>"
                     "<orientation>horizontal</orientation><align>right</align><itemgap>0</itemgap><usecontrolcoords>true</usecontrolcoords>"
                     f"<visible>!Control.HasFocus({bid})</visible>"
                     f'<control type="label"><width>auto</width><height>40</height><font>xb_24</font><textcolor>ink</textcolor><label>$INFO[Container({cid}).NumItems]</label></control>'
                     '<control type="label"><width>auto</width><height>40</height><font>semi_24</font><textcolor>ink2</textcolor><label> more</label></control>'
                     "</control>")
            g.append(img(1262 - 236, ry - 52, 236, 44, "sd/pill_46.png", diffuse="ink", border="22", vis=f"Control.HasFocus({bid})"))
            g.append(lbl(1262 - 236, ry - 52, 236, 44, "Ride this line  ›", "xb_22", "white", align="center", vis=f"Control.HasFocus({bid})"))
            ch.append(group(g, vis=occ(i, j), desc=f"line {key} in slot {j}",
                            anims=f'<animation type="Visible" condition="!{RM}"><effect type="fade" start="0" end="100" time="260"/>'
                                  f'<effect type="slide" start="-40,0" end="0,0" time="260" tween="cubic" easing="out"/></animation>'))
    # one focusable button per slot
    board = board_from_info()
    for j in range(4):
        bid = 9301 + j
        ry = ROW_Y0 + j * ROW_DY
        tx = slot_x[j]
        here = " | ".join(f"[{occ(i, j)}]" for i in range(j, 4))
        acts = []
        for i in range(j, 4):
            acts.append(tag("onclick", f"SetProperty({P}.enterline,{ROWS[i][0]},home)", occ(i, j)))
        nav = [tag("onup", "9000" if j == 0 else f"{bid - 1}")]
        if j < 3:
            nav.append(tag("ondown", f"{bid + 1}", f"Control.IsVisible({bid + 1})"))
        nav += [tag("onleft", "noop"), tag("onright", "noop")]
        ch.append('<control type="button" id="' + str(bid) + '">'
                  f"<left>{tx + 40}</left><top>{ry - 56}</top><width>{1262 - tx - 40}</width><height>76</height>"
                  "<texturefocus /><texturenofocus />" + "".join(acts + board + nav) + f"<visible>{here}</visible></control>")
    return ch


def data():
    out = ['<control type="list" id="9601"><left>0</left><top>1079</top><width>1</width><height>1</height>'
           '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
           '<content target="videos">$VAR[St_Details]</content></control>']
    for key, col, arrow, kind, cid, tx in ROWS:
        out.append(f'<control type="list" id="{cid}"><left>{cid - 9600}</left><top>1079</top><width>1</width><height>1</height>'
                   '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
                   f'<content target="videos">$VAR[St_Path_{key}]</content></control>')
    for n, cid in ((1, 9621), (2, 9622), (3, 9623)):
        out.append(f'<control type="list" id="{cid}"><left>{cid - 9600}</left><top>1079</top><width>1</width><height>1</height>'
                   '<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>'
                   f'<content target="videos">$VAR[St_Path_p{n}]</content></control>')
    return out


def set_films():
    """Collections: Kodi fills 50 with the films of the set; they hang on one ink line."""
    il = ('<itemlayout width="150" height="230">'
          + img(20, 30, 110, 165, "common/white.png", diffuse="wash")
          + '<control type="image"><left>20</left><top>30</top><width>110</width><height>165</height><aspectratio>scale</aspectratio>'
            '<texture background="true" diffuse="sd/mask_110x165.png">$INFO[ListItem.Art(poster)]</texture></control>'
          + img(16, 26, 118, 173, "sd/frame_o4.png", diffuse="ink", border="14")
          + "</itemlayout>")
    fl = ('<focusedlayout width="150" height="230">'
          + img(20, 30, 110, 165, "common/white.png", diffuse="wash")
          + '<control type="image"><left>20</left><top>30</top><width>110</width><height>165</height><aspectratio>scale</aspectratio>'
            '<texture background="true" diffuse="sd/mask_110x165.png">$INFO[ListItem.Art(poster)]</texture></control>'
          + img(7, 17, 136, 191, "sd/ringf_6.png", diffuse="ink", border="20", vis="Control.HasFocus(50)")
          + img(16, 26, 118, 173, "sd/frame_o4.png", diffuse="ink", border="14", vis="!Control.HasFocus(50)")
          + lbl(-60, 200, 270, 30, "$INFO[ListItem.Title]", "semi_20", "ink", align="center", vis="Control.HasFocus(50)")
          + "</focusedlayout>")
    lst = ('<control type="list" id="50"><left>460</left><top>760</top><width>1400</width><height>240</height>'
           "<orientation>horizontal</orientation><preloaditems>1</preloaditems>"
           '<scrolltime tween="cubic" easing="out">200</scrolltime><onup>9000</onup>'
           f"<visible>{IS_SET}</visible>" + il + fl + "</control>")
    line = img(64, 860 - 4, 1792, 8, "sd/line_h8.png", diffuse="ink", border="4,0,4,0", vis=f"{IS_SET} + Integer.IsGreater(Container(50).NumItems,0)")
    return [line, lst]


def full_story():
    """The full plot on a card over the page. The card is always processed but faded out until 61 / 9203 have focus
    (a hidden group's textbox has no page count and its scrollbar can't take focus; the textbox itself never can).
    Back / Left return to the Full story pill 9201 (if the More row can't take it, the grouplist's own Back: 9005)."""
    shown = "Control.HasFocus(61) | Control.HasFocus(9203)"
    return group([
        img(-2000, -2000, 6000, 6000, "common/white.png", diffuse="veil"),
        img(320 - 60, 140 - 46, 1280 + 120, 800 + 120, "sd/shadow_card.png", diffuse="shadow", border="90"),
        img(320, 140, 1280, 800, "sd/rr20.png", diffuse="card", border="20"),
        lbl(384, 180, 1100, 30, "The full story", "caps_21", "ink2", aligny="top"),
        lbl(384, 212, 1152, 70, "$INFO[ListItem.Title]", "disp_52", "ink"),
        '<control type="textbox" id="9200"><left>384</left><top>310</top><width>1100</width><height>585</height>'
        "<font>reg_26</font><textcolor>body</textcolor><label>$INFO[ListItem.Plot]</label>"
        "<pagecontrol>61</pagecontrol></control>",
        '<control type="scrollbar" id="61"><left>1520</left><top>310</top><width>6</width><height>585</height>'
        "<orientation>vertical</orientation><onleft>9201</onleft><onback>9201</onback></control>",
        '<control type="button" id="9203"><left>320</left><top>140</top><width>1280</width><height>800</height>'
        "<texturefocus /><texturenofocus /><label></label>"
        "<onup>noop</onup><ondown>noop</ondown><onleft>9201</onleft><onright>noop</onright><onback>9201</onback></control>",
    ], anims=(f'<animation effect="fade" start="100" end="0" time="0" condition="![{shown}]">Conditional</animation>\n'
              f'<animation effect="fade" start="0" end="100" time="160" condition="{shown}">Conditional</animation>'),
        desc="full story")


def includes():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_station.py - edit the generator. The station page (DialogVideoInfo). -->",
             "<includes>"]
    parts += ["\t" + x for x in "\n".join(variables()).split("\n")]

    def inc(name, body):
        parts.append(f'\t<include name="{name}">')
        parts.extend("\t\t" + x for x in "\n".join(body).split("\n"))
        parts.append("\t</include>")

    inc("St_Data", data() + kodi_hidden())
    inc("St_Top", top())
    inc("St_Poster", poster())
    inc("St_Text", text_column())
    inc("St_Lines", line_rows())
    inc("St_Buttons", [buttons(), more_row()])
    inc("St_SetFilms", set_films())
    inc("St_FullStory", [full_story()])
    parts += ["\t" + x for x in ST_ENC.include("St_Encoder")]
    parts.append("</includes>")
    (OUT / "Includes_VideoInfo.xml").write_text(localize_xml(kdk_mute("\n".join(parts)) + "\n", STRINGS_PO), encoding="utf-8", newline="\n")


def window():
    w = """<?xml version="1.0" encoding="UTF-8"?>
<!--
	GENERATED by _src/make_station.py. The station page (board SixDegreesStation): poster in an interchange
	ring, title, facts, now -> arrives, plot, fanart, pills, and the four lines out of this station with their
	counts (OK on a line boards the map on it). Kodi id contract and Six Degrees ids: see the generator.
	Focus: 9000 pills (Down -> the lines, or the films of a collection), More -> 9100, Full story -> 61 (scrollbar) or 9203.
-->
<window>
	<defaultcontrol always="true">9000</defaultcontrol>
	<onload>@ENC_FLIP@</onload>  <!-- a new centre: the URL encoder's other slot (Encoder in _src/make_map.py) -->
	<onload>SetFocus(9001)</onload>  <!-- 0.9.2: the grouplist re-focused the last pill (e.g. Board); always open on Play -->
	<include>Anim_DialogOpenClose</include>
	<controls>
		<include>SD_Background</include>
		<include>St_Data</include>
		<include>St_Encoder</include>
		<include>St_Lines</include>
		<include>St_Poster</include>
		<include>St_Text</include>
		<include>St_Buttons</include>
		<include>St_SetFilms</include>
		<include>St_Top</include>
		<include>St_FullStory</include>
	</controls>
</window>
"""
    w = w.replace("@ENC_FLIP@", ST_ENC.flip_action())
    (OUT / "DialogVideoInfo.xml").write_text(localize_xml(w, STRINGS_PO), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    includes()
    window()
    print("wrote DialogVideoInfo.xml + Includes_VideoInfo.xml")
