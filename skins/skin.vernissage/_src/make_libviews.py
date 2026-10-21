"""Generate 1080i/Includes_LibViews.xml: "The collection" (M2).   python skins/skin.vernissage/_src/make_libviews.py

docs/skin.vernissage/screens/LibraryWindows.md, View_500_Salon.md, View_510_GalleryWall.md, View_50_Catalogue.md;
SPEC 7 / 8; boards 04 / 05. Shared by MyVideoNav and MyMusicNav (params pick the header word ids).

Ids (screens README 5): views 500 Salon (panel), 510 Gallery wall (fixedlist), 50 Catalogue (list); scrollbars 60
(Salon) / 61 (Catalogue: two scrollbars may not share an id, Kodi routes a page-control message to the first one);
header words View / Options / Sort = 9521-9523 (video) / 9501-9503 (music); 9398 Back-to-Home catcher; Kodi's sort
buttons 3 / 4 off-screen; probes 9551 / 9553 (Salon title 2+ / 3+ lines), 9552 (header title wider than 400 px);
title / tagline boxes 9554 / 9555 (gallery wall) and 9556 (Catalogue) carry their own NumPages for the "..." fade.
The panel, picker and clean confirm (9800-9893) are Includes_Library.xml.

Navigation contract
  views: Up from the top row -> the View word; Left past the first column / Right past the last -> the Library panel
         (the scrollbar too: a numeric onright to a hidden scrollbar falls through to its own onright, LESSONS);
         Catalogue: Down at the end -> the View word (LESSONS 176); Back at a library root -> 9398 -> Home (one press).
  words: Left / Right walk them (no wrap), Down / Back -> the view, Right from Sort -> Now playing (music playing).
The header words fade to 40 % while a view has focus but stay focusable (Conditional fade, LESSONS Majan 1.0.7).
Window-level light (pool, Day shadow) is placed with time-0 / glide slides on Container(500).Column / Row (LESSONS
Groove M3: a container clips its layouts) or at the fixed focus slot (gallery wall, Catalogue figure).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placard as PL  # noqa: E402
from vnxml import (spot, DARK, DAY, NBSP, NL, RM, card, card_twins, fade_cond, group, img, ind, join_and, label,  # noqa: E402
                   lit_layers, print_layers, slide_cond, stack_label, stack_text, textbox, twin_img)

OUT = HERE.parent / "1080i" / "Includes_LibViews.xml"

POSTERS = "[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons)]"
SQUARES = "[Container.Content(albums) | Container.Content(artists)]"
S = dict(collection=31650, sets=31651, listening=31652, salon=31653, gallery=31654, catalogue=31655, empty=31656,
         options=31657, by=31658, unseen=31659, series_n=31660, works=31661, work=31662, episodes=31663,
         seasons=31664, updating=31668, Unseen=31669, Seen=31670, of=31671, none_seen=31672, seen=31673,
         to_go=31674, season=31677, aired=31678, episodes_lc=31679, in_progress=31475, eps_to_go=31476,
         ep_to_go=31477, seasons_lc=31680, season_lc=31681, ends=31451, min=31221, back=31605, films=31401,
         series=31450)
GLIDE = 200
# the spoiler-safe premise (DESIGN 6): the outline or the opening of the plot; an episode takes its SHOW's plot
# (Container.ShowPlot), an album its description, an artist the biography
_EP, _AL, _AR = ("String.IsEqual(ListItem.DBType,episode)", "String.IsEqual(ListItem.DBType,album)",
                 "String.IsEqual(ListItem.DBType,artist)")
PREM_WHEN = (f"[{_EP} + !String.IsEmpty(Container.ShowPlot)] | [{_AL} + !String.IsEmpty(ListItem.Property(Album_Description))] | "
             f"[{_AR} + !String.IsEmpty(ListItem.Property(Artist_Description))] | "
             f"[!{_EP} + !{_AL} + !{_AR} + [!String.IsEmpty(ListItem.PlotOutline) | !String.IsEmpty(ListItem.Plot)]]")
# a set has no state line, nor a show / season with episodes to go and no rating (screens/View_500_Salon.md: the key
# line already says "<w> of <n> seen" / "<u> episodes to go"; device audit M5 found them printed twice): the case
# solver hands the line's room on
STATUS_WHEN = ("!String.IsEqual(ListItem.DBType,set) + ![[String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season)] + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0) + String.IsEmpty(ListItem.Rating)]")
# music items have no key line: Kodi's music listings carry no track count (no ListItem infolabel or album property
# for it in Kodi 21) and nothing else belongs there, so album / artist / song placards close after their last field,
# without the rule and an empty line under it (device audit M5, O-2): the square placards (Salon, gallery wall,
# Catalogue) end on their premise
# grey print paths are built with the layout (LESSONS 625): re-read them every 2 s, so a generation the helper
# publishes (or replaces) while a list is open reaches its prints (no reload: an unchanged path keeps its texture)
UPD = 'infoupdate="2000"'


# ---------------------------------------------------------------- "Acquired <month> <year>" (QA O2)
# Kodi 21 offers ListItem.DateAdded only in the REGION's short date format (VideoGUIInfo: GetAsLocalizedDate(), no
# format parameter; the user may also override it in Settings > Regional), and no infolabel tells the format. So:
#  * the year is the 4-digit field at the start or the end (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, DD.MM.YYYY, ...);
#    a 2-digit year (DD/MM/YY) doesn't parse;
#  * the month is the MIDDLE field for day-first and year-first formats, the FIRST for month-first (US) ones, and
#    only the order is unknown. A probe tells it: 1 px lists 9562 (films) / 9563 (episodes) hold one item added on a
#    day 13-31 (xsp `dateadded contains -13 ... -31`: the database keeps YYYY-MM-DD HH:MM:SS, and months stop at
#    12, so "-13".."-31" can only be the day). Its localized date starts with a month (1-12 + separator) only when
#    the format is month-first: a day-first date starts with 13-31, a year-first one with 4 digits.
# Anything that doesn't parse (no probe item, 2-digit years, other separators) hides the line, and the placard hands
# its room to the premise (the credit field's `when`).
DATE_PROBES = (9562, 9563)
DATE_SEPS = ("/", ".", "-")
DATE_YEARS = range(2000, 2041)


def _date_probe_path(node, kind):
    import json
    import urllib.parse
    rule = {"field": "dateadded", "operator": "contains", "value": [f"-{d}" for d in range(13, 32)]}
    q = json.dumps({"rules": {"and": [rule]}, "type": kind}, separators=(",", ":"))
    return f"{node}?xsp={urllib.parse.quote(q, safe='')}"


def _month_first(p):
    return " | ".join(f"String.StartsWith({p},{m}{s})" for m in [f"{n:02d}" for n in range(1, 13)] + [str(n) for n in range(1, 10)]
                      for s in DATE_SEPS)


def _month_is(m, x="ListItem.DateAdded"):
    """Month m of x in either order (Lib_DateMF picks it)."""
    forms = sorted({f"{m:02d}", str(m)})
    mid = " | ".join(f"String.Contains({x},{s}{f}{s})" for f in forms for s in DATE_SEPS)
    first = " | ".join(f"String.StartsWith({x},{f}{s})" for f in forms for s in DATE_SEPS)
    return f"[!$EXP[Lib_DateMF] + [{mid}]] | [$EXP[Lib_DateMF] + [{first}]]"


def _year_is(y, x="ListItem.DateAdded"):
    return f"String.StartsWith({x},{y}) | String.EndsWith({x},{y})"


def date_expressions():
    a, b = (f"Container({i}).ListItem.DateAdded" for i in DATE_PROBES)
    return NL.join([
        "\t<!-- Acquired line (QA O2): the region's date order from the probe lists 9562 / 9563 (make_libviews.py, DATE) -->",
        f'\t<expression name="Lib_DateKnown">!String.IsEmpty({a}) | !String.IsEmpty({b})</expression>',
        f'\t<expression name="Lib_DateMF">[!String.IsEmpty({a}) + [{_month_first(a)}]] | '
        f'[String.IsEmpty({a}) + !String.IsEmpty({b}) + [{_month_first(b)}]]</expression>',
        '\t<expression name="Lib_DateMonth">' + " | ".join(f"[{_month_is(m)}]" for m in range(1, 13)) + "</expression>",
        '\t<expression name="Lib_DateYear">' + " | ".join(_year_is(y) for y in DATE_YEARS) + "</expression>",
        '\t<expression name="Lib_DateOK">!String.IsEmpty(ListItem.DateAdded) + $EXP[Lib_DateKnown] + $EXP[Lib_DateMonth] + '
        "$EXP[Lib_DateYear]</expression>",
    ])


def date_probes():
    """The two 1 px probe lists (visible, or they never load: LESSONS Passe-partout 139), video windows only."""
    o = ["<!-- date-order probes for the Acquired line: one film / one episode added on a day 13-31 (DATE in the generator) -->"]
    for cid, (node, kind) in zip(DATE_PROBES, (("videodb://movies/titles/", "movies"),
                                               ("videodb://tvshows/titles/-1/-1/-1/-1/", "episodes"))):
        o.append(NL.join([f'<control type="list" id="{cid}">', "\t<left>0</left>", "\t<top>0</top>", "\t<width>1</width>",
                          "\t<height>1</height>", "\t<visible>!$EXP[Lib_IsMusic]</visible>",
                          '\t<itemlayout width="1" height="1" />', '\t<focusedlayout width="1" height="1" />',
                          f'\t<content target="videos" browse="never" limit="1">{_date_probe_path(node, kind)}</content>',
                          "</control>"]))
    return NL.join(o)


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

    db = lambda t: f"String.IsEqual(ListItem.DBType,{t})"  # noqa: E731
    film, sett, show, season, ep, album, artist = (db(t) for t in ("movie", "set", "tvshow", "season", "episode", "album", "artist"))
    rt = "Integer.IsGreater(ListItem.Duration(mins),0)"
    # ---- header
    var("Lib_Title", [
        ("Container.Content(sets)", f"$LOCALIZE[{S['sets']}]"),
        ("String.StartsWith(Container.FolderPath,videodb://movies/sets/) + !String.IsEmpty(Container.FolderName)", "$INFO[Container.FolderName]"),
        ("[Container.Content(seasons) | Container.Content(episodes)] + !String.IsEmpty(Container.ShowTitle)", "$INFO[Container.ShowTitle]"),
        ("[Container.Content(seasons) | Container.Content(episodes)] + !String.IsEmpty(Container.FolderName)", "$INFO[Container.FolderName]"),
        ("$EXP[Lib_IsMusic]", f"$LOCALIZE[{S['listening']}]"),
        ("Container.Content(movies) | Container.Content(tvshows)", f"$LOCALIZE[{S['collection']}]"),
        ("!String.IsEmpty(Container.PluginName) + !String.IsEmpty(Container.FolderName)", "$INFO[Container.FolderName]"),
        ("!String.IsEmpty(Container.FolderName)", "$INFO[Container.FolderName]"),
        (None, f"$LOCALIZE[{S['collection']}]"),
    ])
    n = "$INFO[Container.NumItems]"
    by = f"$LOCALIZE[{S['by']}] [LOWERCASE]$INFO[Container.SortMethod][/LOWERCASE]"
    unseen = f"$INFO[Container.TotalUnWatched, · , $LOCALIZE[{S['unseen']}]]"
    var("Lib_SubFull", [
        ("Container.Content(sets)", f"{n} $LOCALIZE[{S['series_n']}]"),
        ("String.StartsWith(Container.FolderPath,videodb://movies/sets/) + Integer.IsEqual(Container.NumItems,1)", f"1 $LOCALIZE[{S['work']}]"),
        ("String.StartsWith(Container.FolderPath,videodb://movies/sets/)", f"{n} $LOCALIZE[{S['works']}]"),
        ("Container.Content(movies)", f"$LOCALIZE[{S['films']}] · {by} · {n}{unseen}"),
        ("Container.Content(tvshows)", f"$LOCALIZE[{S['series']}] · {by} · {n}"),
        ("Container.Content(episodes)", f"$LOCALIZE[{S['episodes']}] · {n}{unseen}"),
        ("Container.Content(seasons)", f"$LOCALIZE[{S['seasons']}] · {n}"),
        ("Container.Content(albums)", f"$LOCALIZE[132] · {by} · {n}"),
        ("Container.Content(artists)", f"$LOCALIZE[133] · {by} · {n}"),
        ("Container.Content(songs)", f"$LOCALIZE[134] · {by} · {n}"),
        (None, n),
    ])
    var("Lib_SubShort", [("Container.Content(episodes)", f"{n}{unseen}"), (None, n)])
    var("Lib_Scanning", [("$EXP[Lib_IsMusic] + Library.IsScanningMusic", f" · $LOCALIZE[{S['updating']}]"),
                         ("!$EXP[Lib_IsMusic] + Library.IsScanningVideo", f" · $LOCALIZE[{S['updating']}]")])
    var("Lib_Sub", [(f"Integer.IsGreater(Container(9557).NumPages,1)", "$VAR[Lib_SubShort]$VAR[Lib_Scanning]"),
                    (None, "$VAR[Lib_SubFull]$VAR[Lib_Scanning]")])
    # the gallery wall folds the title into the sub-line (board 05): "The collection · Gallery wall · unseen, by title"
    var("Lib_Sub510", [(None, f"$VAR[Lib_Title] · $LOCALIZE[{S['gallery']}] · $VAR[Lib_Sub510Filter]{by}")])
    var("Lib_Sub510Filter", [("!$EXP[Lib_IsMusic] + System.Setting(hidewatched)", f"$LOCALIZE[{S['unseen']}], ")])
    var("Lib_ViewName", [("Control.IsVisible(500)", f"$LOCALIZE[{S['salon']}]"),
                         ("Control.IsVisible(510)", f"$LOCALIZE[{S['gallery']}]"),
                         (None, f"$LOCALIZE[{S['catalogue']}]")])
    # ---- art
    var("Lib_ItemArt", [("!String.IsEmpty(ListItem.Art(poster))", "$INFO[ListItem.Art(poster)]"),
                        ("!String.IsEmpty(ListItem.Art(tvshow.poster))", "$INFO[ListItem.Art(tvshow.poster)]"),
                        (None, "$INFO[ListItem.Art(thumb)]")])
    var("Lib_StillArt", [("!String.IsEmpty(ListItem.Art(thumb))", "$INFO[ListItem.Art(thumb)]"),
                         ("!String.IsEmpty(ListItem.Art(tvshow.fanart))", "$INFO[ListItem.Art(tvshow.fanart)]"),
                         (None, "$INFO[ListItem.Art(fanart)]")])
    var("Lib_SquareArt", [("!String.IsEmpty(ListItem.Art(thumb))", "$INFO[ListItem.Art(thumb)]"),
                          (None, "$INFO[ListItem.Icon]")])
    # ---- placard lines (ListItem = the drawn item in a layout; in the window the view's item, CGUIMediaWindow)
    var("Lib_PTitle", [("ListItem.IsParentFolder", f"$LOCALIZE[{S['back']}]"),
                       (f"{ep} + !String.IsEmpty(ListItem.Title)", "$INFO[ListItem.Title]"), (None, "$INFO[ListItem.Label]")])
    yd = "$INFO[ListItem.Year]$INFO[ListItem.Director, · ,]"
    var("Lib_L2", [
        (film, yd),
        (sett + " + Integer.IsEqual(ListItem.Property(Total),1)", f"1 $LOCALIZE[{S['work']}]"),
        (sett, f"$INFO[ListItem.Property(Total)] $LOCALIZE[{S['works']}]"),
        (show, "$INFO[ListItem.Year]$INFO[ListItem.Studio, · ,]"),
        (season, "$INFO[ListItem.TVShowTitle]"),
        (ep, f"S$INFO[ListItem.Season]·E$INFO[ListItem.Episode]$VAR[Lib_Aired]"),
        (album, "$INFO[ListItem.Artist]"),
        (artist, "$INFO[ListItem.Genre]"),
        (None, "$INFO[ListItem.Label2]"),
    ])
    var("Lib_Aired", [("!String.IsEmpty(ListItem.Premiered)", f" · $LOCALIZE[{S['aired']}] $INFO[ListItem.Premiered]")])
    var("Lib_L3", [
        (season + " + Integer.IsEqual(ListItem.Property(TotalEpisodes),1)", f"1 $LOCALIZE[{S['episodes_lc']}]"),
        (season, f"$INFO[ListItem.Property(TotalEpisodes)] $LOCALIZE[{S['episodes_lc']}]"),
        (album, "$INFO[ListItem.Year]$INFO[ListItem.Genre, · ,]"),
        (ep, "$INFO[ListItem.Director]"),
        (artist, ""),
        (None, "$INFO[ListItem.Genre]"),
    ])
    togo = lambda w: f"$INFO[ListItem.Property(UnWatchedEpisodes)]{NBSP}$LOCALIZE[{w}]"  # noqa: E731
    var("Lib_Key1", [
        (f"[{film} | {ep}] + ListItem.IsResumable", "$VAR[VN_Left]"),
        (f"[{film} | {ep}] + {rt}", mins()),
        (sett + " + Integer.IsGreater(ListItem.Property(Watched),0)",
         f"$INFO[ListItem.Property(Watched)] $LOCALIZE[{S['of']}] $INFO[ListItem.Property(Total)] $LOCALIZE[{S['seen']}]"),
        (sett, f"$LOCALIZE[{S['none_seen']}]"),
        (f"{show} + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),1)", f"1{NBSP}$LOCALIZE[{S['ep_to_go']}]"),
        (f"{show} + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)", togo(S['eps_to_go'])),
        (f"{season} + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)", togo(S['to_go'])),
    ])
    var("Lib_Key2", [
        (f"[{film} | {ep}] + {rt}", ends()),
        (f"{show} + Integer.IsEqual(ListItem.Property(TotalSeasons),1)", f"1 $LOCALIZE[{S['season_lc']}]"),
        (f"{show} + Integer.IsGreater(ListItem.Property(TotalSeasons),1)", f"$INFO[ListItem.Property(TotalSeasons)] $LOCALIZE[{S['seasons_lc']}]"),
    ])
    var("Lib_KeyLine", [  # one line (gallery wall / Catalogue): "ends 11:37 pm" / "51 min left · ends 11:31 pm"
        (f"[{film} | {ep}] + {rt} + ListItem.IsResumable", f"$VAR[VN_Left] · {ends()}"),
        (f"[{film} | {ep}] + {rt}", f"{mins()} · {ends()}"),
        (f"{show} + Integer.IsGreater(ListItem.Property(TotalSeasons),0)", "$VAR[Lib_Key1] · $VAR[Lib_Key2]"),
        (None, "$VAR[Lib_Key1]"),
    ])
    var("Lib_StateWord", [("Integer.IsGreater(ListItem.PlayCount,0)", f"$LOCALIZE[{S['Seen']}]"),
                          ("ListItem.IsResumable", f"$LOCALIZE[{S['in_progress']}]"),
                          (None, f"$LOCALIZE[{S['Unseen']}]")])
    # ---- curator card (DESIGN 6): status, made-by, premise, collection, credit
    star = "$INFO[ListItem.Rating,★ , · ]"
    var("Lib_Status", [
        (f"[{film} | {ep}] + !ListItem.IsParentFolder",
         f"{star}$VAR[Lib_StateWord] · $INFO[Container.CurrentItem]{NBSP}$LOCALIZE[{S['of']}]{NBSP}$INFO[Container.NumItems]"),
        # shows / seasons with episodes to go: the key line says "<u> episodes to go", so the state line keeps the rating only
        (f"[{show} | {season}] + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)", "$INFO[ListItem.Rating,★ ,]"),
        (f"{show} | {season}", f"{star}$LOCALIZE[{S['Seen']}]"),
    ])
    var("Lib_Made", [(None, "$INFO[ListItem.Studio]$INFO[ListItem.Country, · ,]")])
    var("Lib_Prem", [(ep, "$INFO[Container.ShowPlot]"), (album, "$INFO[ListItem.Property(Album_Description)]"),
                     (artist, "$INFO[ListItem.Property(Artist_Description)]"),
                     ("!String.IsEmpty(ListItem.PlotOutline)", "$INFO[ListItem.PlotOutline]"), (None, "$INFO[ListItem.Plot]")])
    var("Lib_Coll", [(None, "$LOCALIZE[31495] $INFO[ListItem.Set]")])
    # "Acquired <month> <year>", region-independent (DATE above); shown only on $EXP[Lib_DateOK]
    var("Lib_CreditMonth", [(_month_is(m), f"$LOCALIZE[{20 + m}]") for m in range(1, 13)])
    var("Lib_Credit", [(_year_is(y), f"$LOCALIZE[31685] $VAR[Lib_CreditMonth] {y}") for y in DATE_YEARS])
    # ---- Catalogue rows
    var("Lib_CLeft", [
        ("ListItem.IsParentFolder", f"$LOCALIZE[{S['back']}]"),
        (f"{ep} + !String.IsEmpty(ListItem.Episode)", "S$INFO[ListItem.Season]·E$INFO[ListItem.Episode]  $INFO[ListItem.Title]"),
        ("String.IsEqual(ListItem.DBType,song) + Integer.IsGreater(ListItem.TrackNumber,0)", "$INFO[ListItem.TrackNumber] · $INFO[ListItem.Title]"),
        (None, "$INFO[ListItem.Label]"),
    ])
    var("Lib_CRight", [
        ("ListItem.IsParentFolder", ""),
        (f"{ep} + ListItem.IsResumable", "$VAR[VN_Left]"),
        (f"{ep} + {rt}", mins()),
        ("String.IsEqual(ListItem.DBType,song)", "$INFO[ListItem.Duration]"),
        (f"[{show} | {season}] + Integer.IsGreater(ListItem.Property(UnWatchedEpisodes),0)", togo(S['to_go'])),
        (f"[{film} | {album} | {sett}] + !String.IsEmpty(ListItem.Year)", "$INFO[ListItem.Year]"),
        (None, "$INFO[ListItem.Label2]"),
    ])
    var("Lib_CRightF", [(f"[{film} | {ep}] + {rt} + !ListItem.IsParentFolder", ends()), (None, "$VAR[Lib_CRight]")])
    return NL.join(v)


def expressions():
    return NL.join([
        '\t<expression name="Lib_IsMusic">Window.IsActive(music)</expression>',
        date_expressions(),
        "\t<!-- one Back from a library root to Home (screens/LibraryWindows.md): prefix tests, shows only at the top level",
        "\t     (no tvshowid), never videodb://movies/sets/ (reached with Container.Update: Back returns to the films).",
        "\t     Albums / artists: the root itself (or the root with options) only, never musicdb://albums/<id>/ (an album's",
        "\t     tracks) or musicdb://artists/<id>/ (an artist's albums), where Back must go up a folder (QA 2026-10-21) -->",
        '\t<expression name="Lib_AtRoot">String.StartsWith(Container.FolderPath,videodb://movies/titles/) | '
        '[String.StartsWith(Container.FolderPath,videodb://tvshows/titles/) + !String.Contains(Container.FolderPath,tvshowid)] | '
        '[String.StartsWith(Container.FolderPath,videodb://inprogresstvshows/) + !String.Contains(Container.FolderPath,tvshowid)] | '
        'String.IsEqual(Container.FolderPath,musicdb://albums/) | String.StartsWith(Container.FolderPath,musicdb://albums/?) | '
        'String.IsEqual(Container.FolderPath,musicdb://artists/) | String.StartsWith(Container.FolderPath,musicdb://artists/?) | '
        'String.StartsWith(Container.FolderPath,musicdb://songs/)</expression>',
        '\t<expression name="Lib_HeaderRest">Control.HasFocus(500) | Control.HasFocus(510) | Control.HasFocus(50) | Control.HasFocus(60) | Control.HasFocus(61)</expression>',
        f'\t<expression name="Lib_Posters">{POSTERS}</expression>',
        f'\t<expression name="Lib_Squares">{SQUARES}</expression>',
        "\t<!-- Salon: the lit cell is in the last two columns of the top row (it would pass under Now playing) -->",
        '\t<expression name="Lib_SalonTopRight">Control.HasFocus(500) + Container(500).Row(0) + [[$EXP[Lib_Posters] + [Container(500).Column(7) | Container(500).Column(8)]] | [$EXP[Lib_Squares] + Container(500).Column(5)]]</expression>',
    ])


# ================================================================ header
def header_word(cid, x, width, label_text, enable, clicks, left_id, right_id, extra_right=()):
    """A header word (screens/LibraryWindows.md): ink2 text; focused = a card chip with its 1 px edge + ink."""
    w = f"<width>{width}</width>" if isinstance(width, int) else f'<width max="{width[1]}">auto</width>'
    rights = list(extra_right) + [f"<onright>{right_id}</onright>"]
    btn = NL.join([f'<control type="button" id="{cid}">', f"\t{w}", "\t<height>48</height>", "\t<font>font_body</font>",
                   "\t<textoffsetx>8</textoffsetx>", "\t<align>center</align>", "\t<aligny>center</aligny>",
                   "\t<textcolor>$VAR[ink2]</textcolor>", "\t<focusedcolor>$VAR[ink]</focusedcolor>",
                   "\t<disabledcolor>$VAR[disabled]</disabledcolor>",
                   '\t<texturefocus border="4" colordiffuse="$VAR[card_edge]">vn/card_edge.png</texturefocus>',
                   "\t<texturenofocus />", f"\t<label>{label_text}</label>", f"\t<onleft>{left_id}</onleft>",
                   *[f"\t{r}" for r in rights], "\t<onup>noop</onup>", "\t<ondown>50</ondown>", "\t<onback>50</onback>",
                   f"\t<enable>{enable}</enable>", *[f"\t<onclick>{c}</onclick>" for c in clicks], "</control>"])
    # the chip fill behind the focused word: a disabled twin of the same width (draws texturenofocus)
    chip = NL.join(['<control type="button">', f"\t{w}", "\t<height>48</height>", "\t<font>font_body</font>",
                    "\t<textoffsetx>8</textoffsetx>", "\t<align>center</align>", "\t<textcolor>clear</textcolor>",
                    "\t<disabledcolor>clear</disabledcolor>",
                    '\t<texturenofocus colordiffuse="$VAR[card]">vn/white.png</texturenofocus>', "\t<texturefocus />",
                    f"\t<label>{label_text}</label>", "\t<enable>false</enable>",
                    f"\t<visible>Control.HasFocus({cid})</visible>", "</control>"])
    return group([chip, btn], left=x, top=76)


def header_word_right(cid, right, maxw, label_text, enable, clicks, left_id, right_id):
    """The View word, right-aligned so its text ENDS on the header grid (screens/LibraryWindows.md: words 40 px apart):
    an auto-width button in a right-aligned horizontal grouplist, and its chip twin in an identical one (both widths
    are the label's, so the chip hugs the word). The grouplist owns Left / Right (it rewires its children's)."""
    def gl(inner, nav):
        return NL.join(['<control type="grouplist">', f"	<left>{right - maxw}</left>", "	<top>0</top>",
                        f"	<width>{maxw}</width>", "	<height>48</height>", "	<orientation>horizontal</orientation>",
                        "	<align>right</align>", "	<itemgap>0</itemgap>", *nav, ind(inner, 1), "</control>"])
    btn = NL.join([f'<control type="button" id="{cid}">', f'	<width max="{maxw}">auto</width>', "	<height>48</height>",
                   "	<font>font_body</font>", "	<textoffsetx>8</textoffsetx>", "	<aligny>center</aligny>",
                   "	<textcolor>$VAR[ink2]</textcolor>", "	<focusedcolor>$VAR[ink]</focusedcolor>",
                   "	<disabledcolor>$VAR[disabled]</disabledcolor>",
                   '	<texturefocus border="4" colordiffuse="$VAR[card_edge]">vn/card_edge.png</texturefocus>',
                   "	<texturenofocus />", f"	<label>{label_text}</label>", "	<onup>noop</onup>", "	<ondown>50</ondown>",
                   "	<onback>50</onback>", f"	<enable>{enable}</enable>", *[f"	<onclick>{c}</onclick>" for c in clicks],
                   "</control>"])
    chip = NL.join(['<control type="button">', f'	<width max="{maxw}">auto</width>', "	<height>48</height>",
                    "	<font>font_body</font>", "	<textoffsetx>8</textoffsetx>", "	<textcolor>clear</textcolor>",
                    "	<disabledcolor>clear</disabledcolor>",
                    '	<texturenofocus colordiffuse="$VAR[card]">vn/white.png</texturenofocus>', "	<texturefocus />",
                    f"	<label>{label_text}</label>", "	<enable>false</enable>", "</control>"])
    return group([group([gl(chip, [])], vis=f"Control.HasFocus({cid})"),
                  gl(btn, [f"	<onleft>{left_id}</onleft>", f"	<onright>{right_id}</onright>"])], top=76)


# the header grid (screens/LibraryWindows.md): Options' text starts at x 1362; the View word's text ends 40 px before
# it, Sort's starts 40 px after it (Inter Tight 30 "Options" = 103 px + Kodi's per-glyph slack -> auto width 126)
HDR_OPT_TEXT, HDR_GAP, HDR_OPT_W = 1362, 40, 126


def header(view_id, opt_id, sort_id):
    title_line = f"""<control type="grouplist">
	<left>116</left>
	<top>58</top>
	<width>1000</width>
	<height>66</height>
	<orientation>horizontal</orientation>
	<itemgap>40</itemgap>
	<usecontrolcoords>true</usecontrolcoords>
	<visible>!Control.IsVisible(510)</visible>
{ind(label(None, None, None, 66, "$VAR[Lib_Title]", "font_exhibit", "$VAR[ink]", width_auto_max=640, selected=False), 1)}
{ind(label(None, 22, None, 41, "$VAR[Lib_Sub]", "font_body", "$VAR[ink2]", width_auto_max=560, selected=False, vis="!Integer.IsGreater(Container(9552).NumPages,1)"), 1)}
{ind(label(None, 22, None, 41, "$VAR[Lib_Sub]", "font_body", "$VAR[ink2]", width_auto_max=490, selected=False, vis="Integer.IsGreater(Container(9552).NumPages,1)"), 1)}
</control>"""
    line510 = label(120, 58, 1000, 41, "$VAR[Lib_Sub510]", "font_body", "$VAR[ink2]", vis="Control.IsVisible(510)", selected=False)
    # title probes: wider than 400 px -> the sub-line gets max 490; wider than 480 -> the count only (LESSONS Daylight 0.9.4)
    probe = NL.join(NL.join([f'<control type="textbox" id="{cid}">', "\t<left>116</left>", "\t<top>58</top>",
                             f"\t<width>{w}</width>", "\t<height>99</height>", "\t<font>font_exhibit</font>",
                             "\t<textcolor>clear</textcolor>", "\t<label>$VAR[Lib_Title]</label>", "</control>"])
                    for cid, w in ((9552, 400), (9557, 480)))
    opt_x = HDR_OPT_TEXT - 8
    words = group([
        header_word_right(view_id, HDR_OPT_TEXT - HDR_GAP + 8, 200, "$VAR[Lib_ViewName]", "Integer.IsGreater(Container.ViewCount,1)",
                          ["SetProperty(vernissage.pick.from,header,home)", "SetFocus(9851,0,absolute)"], "noop", opt_id),
        header_word(opt_id, opt_x, ("auto", 140), f"$LOCALIZE[{S['options']}]", "true",
                    ["SetProperty(vernissage.lib.from,header,home)", "SetFocus(9801,0,absolute)"], view_id, sort_id),
        header_word(sort_id, opt_x + HDR_OPT_W + HDR_GAP - 16, ("auto", 126), "$INFO[Container.SortMethod]", "Control.IsEnabled(3)",
                    ["SendClick(3)"], opt_id, sort_id, extra_right=['<onright condition="Player.HasAudio">9950</onright>']),
    ], cid=9300, anims=['<animation effect="fade" start="100" end="40" time="200" condition="$EXP[Lib_HeaderRest]">Conditional</animation>',
                       # the gallery wall's placard starts at y 114: its words sit on the sub-line (y 54..102)
                       '<animation effect="slide" start="0,0" end="0,-22" time="0" condition="Control.IsVisible(510)">Conditional</animation>'])
    kodi = NL.join([
        '<control type="button" id="3">', "\t<description>Sort by (Kodi)</description>", "\t<include>VN_Hidden</include>", "</control>",
        '<control type="button" id="4">', "\t<description>Sort order (Kodi)</description>", "\t<include>VN_Hidden</include>", "</control>",
        '<control type="button" id="9398">', "\t<description>Back at a library root: Home in one press (LESSONS Back audit)</description>",
        "\t<include>VN_Hidden</include>", "\t<onfocus>ActivateWindow(Home)</onfocus>",
        '\t<visible allowhiddenfocus="true">false</visible>', "</control>"])
    return NL.join([probe, title_line, line510, words, "<include>VN_Clock</include>", kodi])


def view_nav(up, extra=()):
    o = [f"<onup>{up}</onup>"]
    o += list(extra)
    o += ["<include>Lib_OpenLeft</include>"]
    o.append('<onback condition="$EXP[Lib_AtRoot]">9398</onback>')
    return o


# ================================================================ 500 Salon
SAL = dict(left=58, top=95, width=1800, height=985, cw=188, ch=283, pw=170, ph=255, px=62, py=87,
           fw=294, fh=429, mat=10, cols=9, flip=5, pl_w=540, spot=(2.6, 1.7), probes=9570)
SQ = dict(left=78, top=140, width=1752, height=940, cw=288, ch=268, pw=240, ph=240, px=42, py=42,
          fw=324, fh=324, mat=10, cols=6, flip=3, pl_w=540, spot=(2.6, 1.7), probes=9576)
SAFE_BOTTOM = 1026   # title-safe bottom (screens README 1)
HEADER_BOTTOM = 136  # the library header (title + words) ends here


def row_dy(g, r):
    """Where the lit work of panel row r hangs: the row's offset, lifted on a row whose enlarged frame would pass the
    title-safe bottom so the frame's bottom sits on the row's print bottom (it grows upward), and dropped on a row
    whose frame would cover the header so its top sits on the row's print top (it grows downward), like the column
    flip."""
    top = g["top"] + g["ch"] * r
    if top + g["fh"] > SAFE_BOTTOM:
        return g["ch"] * r - (g["fh"] - g["py"] - g["ph"])
    if top < HEADER_BOTTOM:
        return g["ch"] * r + g["py"]
    return g["ch"] * r


def row_lifts(g):
    return {r: g["ch"] * r - row_dy(g, r) for r in range(int(g["height"] / g["ch"])) if row_dy(g, r) != g["ch"] * r}


PROBE_IDS = lambda base: dict(zip(("t44", "t36", "t30", "t2", "byline", "tagline"), range(base, base + 6)))  # noqa: E731


def salon_greys():
    return [("movie_poster/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,movie)"),
            ("set_poster/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,set)"),
            ("tvshow_poster/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,tvshow)"),
            ("tvshow_poster/$INFO[ListItem.TvShowDBID].jpg", "String.IsEqual(ListItem.DBType,season) | String.IsEqual(ListItem.DBType,episode)")]


def seen_dot(x, y):
    w = "Integer.IsGreater(ListItem.PlayCount,0) + !ListItem.IsParentFolder"
    return NL.join([twin_img(x, y, 20, 20, "vn/dot.png", "wall", vis=w), twin_img(x + 3, y + 3, 14, 14, "vn/dot.png", "ink", vis=w)])


def parent_print(x, y, w, h):
    """The ".." item: a blank print with "Back" (Omar's watched-hidden shows can show only "..", LESSONS Fold)."""
    p = "ListItem.IsParentFolder"
    return NL.join([twin_img(x, y, w, h, "vn/white.png", "card", vis=p),
                    label(x + 12, y + 12, w - 24, h - 24, f"$LOCALIZE[{S['back']}]", "font_small", "$VAR[ink2]",
                          align="center", aligny="center", vis=p)])


def salon_card(g, squares):
    """The Salon's placard (DESIGN 6: 540 px, as tall as the framed work, 24 px beside it; right of the frame in the
    first columns, left from column g['flip']). Window level, placed on the lit cell with time-0 Column / Row slides
    (LESSONS Majan 1.0.7): a grouplist can't live in a layout, and fields must close up."""
    fx, fy = g["left"], g["top"]
    x = fx + g["fw"] + 24
    flip_dx = -(24 + g["pl_w"]) - (g["fw"] + 24)
    cols = [f'<animation effect="slide" start="0,0" end="{g["cw"] * c},0" time="0" condition="Container(500).Column({c})">Conditional</animation>'
            for c in range(1, g["cols"])]
    flip = " | ".join(f"Container(500).Column({c})" for c in range(g["flip"], g["cols"]))
    cols.append(f'<animation effect="slide" start="0,0" end="{flip_dx},0" time="0" condition="{flip}">Conditional</animation>')
    rows = [f'<animation effect="slide" start="0,0" end="0,{row_dy(g, r)}" time="0" condition="Container(500).Row({r})">Conditional</animation>'
            for r in range(int(g["height"] / g["ch"])) if row_dy(g, r)]
    if squares:
        fields = [PL.title("$VAR[Lib_PTitle]"), PL.byline("$VAR[Lib_L2]"), PL.line("genres", "$VAR[Lib_L3]", "top"),
                  PL.box("premise", "$VAR[Lib_Prem]", "mid", "font_small", 1, grow=6, when=PREM_WHEN)]
        drop = PL.DROP_SALON
    else:
        fields = [PL.title("$VAR[Lib_PTitle]"), PL.byline("$VAR[Lib_L2]"),
                  PL.line("genres", "$VAR[Lib_L3]", "top", when="!String.IsEmpty(ListItem.Genre)"),
                  PL.box("tagline", "$INFO[ListItem.Tagline]", "mid", "font_quote", 2, color="$VAR[ink]", probe=True,
                         when="!String.IsEmpty(ListItem.Tagline)"),
                  # the premise fills the middle whenever the tagline (or the flags, the genres) leave room: no hole
                  PL.box("premise", "$VAR[Lib_Prem]", "mid", "font_small", 1, gap=12, grow=6, when=PREM_WHEN),
                  # status 12 px under the flags (board 14): Kodi's 41 / 38 px pitches are a hair taller than the
                  # board's 40 / 37.5, and 2 px decide whether a one-line tagline fits (placard_log.py)
                  PL.flags("ListItem"), PL.line("status", "$VAR[Lib_Status]", "bot", gap=12, when=STATUS_WHEN),
                  PL.rule(), PL.keyline("$VAR[Lib_KeyLine]")]
        drop = PL.DROP_SALON
    kind = SQUARES if squares else f"!{SQUARES}"
    card_xml = PL.curator(fields, x, fy + 2, g["pl_w"], g["fh"] - 4, (20, 26), PROBE_IDS(g["probes"]), drop=drop,
                          anims=cols)
    return group([card_xml], anims=rows, vis=f"Control.HasFocus(500) + {kind} + !ListItem.IsParentFolder")


def salon_layouts(g, squares):
    cond = SQUARES if squares else f"!{SQUARES}"
    art = "$VAR[Lib_SquareArt]" if squares else "$VAR[Lib_ItemArt]"
    greys = [("album_thumb/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,album)")] if squares else salon_greys()
    notparent = "!ListItem.IsParentFolder"
    item = NL.join([print_layers(g["px"], g["py"], g["pw"], g["ph"], art, greys, when=notparent),
                    parent_print(g["px"], g["py"], g["pw"], g["ph"]),
                    seen_dot(g["px"] + g["pw"] - 30, g["py"] + g["ph"] - 30)])
    a = g["mat"] + 2
    lit = NL.join([
        lit_layers(0, 0, g["fw"], g["fh"], g["mat"], art, when=notparent,
                   grey=print_layers(a, a, g["fw"] - 2 * a, g["fh"] - 2 * a, art, greys, when=notparent)),
        parent_print(a, a, g["fw"] - 2 * a, g["fh"] - 2 * a),
    ])
    # the last visible row: the enlarged work grows upward (its frame's bottom on the row's print bottom), so it never
    # runs off the screen; Container(500).Row(n) works inside the panel's own focused layout (LESSONS Poster wall)
    lifts = row_lifts(g)
    if lifts:
        lit = group([lit], anims=[f'<animation effect="slide" start="0,0" end="0,{-d}" time="0" condition="Container(500).Row({r})">Conditional</animation>'
                                  for r, d in sorted(lifts.items())])
    # the lifted work's seen dot and parent print move with it (they are in `lit`)
    return (f'<itemlayout condition="{cond}" {UPD} width="{g["cw"]}" height="{g["ch"]}">{NL}{ind(item, 1)}{NL}</itemlayout>{NL}'
            f'<focusedlayout condition="{cond}" {UPD} width="{g["cw"]}" height="{g["ch"]}">{NL}{ind(lit, 1)}{NL}</focusedlayout>')


def salon(up):
    # Down on the last row stops (screens/View_500_Salon.md): a panel with NO action in a direction wraps there too
    # (CGUIBaseContainer::OnDown: wrapAround = navigation == id || !HasActionsMeetingCondition), QA 2026-10-21
    body = [*[f"<{k}>{SAL[k]}</{k}>" for k in ("left", "top", "width", "height")],
            *view_nav(up, ['<onright condition="Control.IsVisible(60)">60</onright>', "<ondown>noop</ondown>"]),
            "<include>Lib_OpenRight</include>", "<pagecontrol>60</pagecontrol>",
            '<scrolltime tween="cubic" easing="out">200</scrolltime>', '<viewtype label="$LOCALIZE[31653]">panel</viewtype>',
            # no preload: with preloaditems the panel also draws the row above the page, whose prints overflow
            # their cells by 17 px (frame room) and peeked under the header
            "<preloaditems>0</preloaditems>",
            f"<visible>{POSTERS} | {SQUARES}</visible>",
            salon_layouts(SAL, False), salon_layouts(SQ, True)]
    panel = '<control type="panel" id="500">' + NL + NL.join(ind(b, 1) for b in body) + NL + "</control>"
    bar = scrollbar(60, 1810, 182, 821, "500")
    return NL.join([salon_light(SAL, False), salon_light(SQ, True), panel, salon_card(SAL, False), salon_card(SQ, True),
                    group([bar], vis="Control.IsVisible(500)")])


def salon_light(g, squares):
    """The pool (glides) and the Day shadow (jumps) on the focused cell: window level, placed with Column / Row."""
    fx, fy = g["left"], g["top"]
    pw, ph = round(g["fw"] * g["spot"][0]), round(g["fh"] * g["spot"][1])
    pool_x = fx + g["fw"] // 2 - pw // 2
    pool_y = fy + g["fh"] // 2 - round(0.03 * g["fh"]) - ph // 2
    rows = int(g["height"] / g["ch"])
    col_glide, row_glide, col0, row0 = [], [], [], []
    for c in range(1, g["cols"]):
        col_glide += slide_cond(f"Container(500).Column({c})", g["cw"] * c, 0, GLIDE)
        col0 += slide_cond(f"Container(500).Column({c})", g["cw"] * c, 0)
    for r in range(rows):
        if not row_dy(g, r):
            continue
        row_glide += slide_cond(f"Container(500).Row({r})", 0, row_dy(g, r), GLIDE)
        row0 += slide_cond(f"Container(500).Row({r})", 0, row_dy(g, r))
    vis = f"Control.IsVisible(500) + {SQUARES if squares else '!' + SQUARES}"
    shadow = group([group([img(fx - 50, fy - 42, g["fw"] + 100, g["fh"] + 104, "vn/shadow.png", "$VAR[shadow]", border="56",
                               anims=["<include>VN_ShadowSteps</include>"])], anims=row0)],
                   anims=col0 + fade_cond("!Control.HasFocus(500)", 150))
    pool = group([group([spot(pool_x, pool_y, pw, ph)],
                        anims=row_glide)], anims=col_glide + fade_cond("!Control.HasFocus(500)", 200))
    return group([shadow, pool], vis=vis)


def scrollbar(cid, x, y, h, view):
    return NL.join([f'<control type="scrollbar" id="{cid}">', f"\t<left>{x}</left>", f"\t<top>{y}</top>", "\t<width>4</width>",
                    f"\t<height>{h}</height>", '\t<texturesliderbackground colordiffuse="$VAR[rule]">vn/white.png</texturesliderbackground>',
                    '\t<texturesliderbar colordiffuse="$VAR[ink2]">vn/white.png</texturesliderbar>',
                    '\t<texturesliderbarfocus colordiffuse="$VAR[ink]">vn/white.png</texturesliderbarfocus>',
                    "\t<orientation>vertical</orientation>", "\t<showonepage>false</showonepage>",
                    f"\t<onleft>{view}</onleft>", "\t<onup>$PARAM[up]</onup>",
                    "\t<onright>SetProperty(vernissage.lib.from,view,home)</onright>",
                    "\t<onright>SetFocus(9801,0,absolute)</onright>", f"\t<onback>{view}</onback>", "</control>"])


# ================================================================ 510 Gallery wall
GW = {  # content key: (layout condition, item print rect, focused width, frame rect, mat, placard rect, pool rect)
    "episodes": ("Container.Content(episodes)", (0, 293, 480, 270), 1650, (30, 132, 1012, 592), 24, (1260, 246, 520, 588)),
    "albums": ("Container.Content(albums)", (160, 258, 340, 340), 1490, (160, 60, 772, 772), 24, (1158, 174, 520, 768)),
    "posters": (None, (160, 173, 340, 510), 1330, (130, 0, 612, 892), 24, (952, 114, 668, 888)),
}
GW_LEFT, GW_TOP, GW_SLOT = -330, 112, 500


def gw_layouts():
    out = []
    for key, (cond, pr, fwid, fr, mat, _pl) in GW.items():
        c = f' condition="{cond}"' if cond else ""
        if key == "episodes":
            art, greys = "$VAR[Lib_StillArt]", [("tvshow_fanart/$INFO[ListItem.TvShowDBID].jpg", "String.IsEqual(ListItem.DBType,episode)")]
        elif key == "albums":
            art, greys = "$VAR[Lib_SquareArt]", [("album_thumb/$INFO[ListItem.DBID].jpg", "String.IsEqual(ListItem.DBType,album)")]
        else:
            art, greys = "$VAR[Lib_ItemArt]", salon_greys()
        np = "!ListItem.IsParentFolder"
        item = NL.join([print_layers(*pr, art, greys, when=np), parent_print(*pr)])
        a = mat + 2
        lit = NL.join([lit_layers(*fr, mat, art, when=np,
                                  grey=print_layers(fr[0] + a, fr[1] + a, fr[2] - 2 * a, fr[3] - 2 * a, art, greys, when=np)),
                       parent_print(fr[0] + a, fr[1] + a, fr[2] - 2 * a, fr[3] - 2 * a)])
        out.append(f'<itemlayout{c} {UPD} width="{GW_SLOT}" height="892">{NL}{ind(item, 1)}{NL}</itemlayout>')
        out.append(f'<focusedlayout{c} {UPD} width="{fwid}" height="892">{NL}{ind(lit, 1)}{NL}</focusedlayout>')
    return NL.join(out)


def gallery(up):
    body = [f"<left>{GW_LEFT}</left>", f"<top>{GW_TOP}</top>", "<width>2250</width>", "<height>892</height>",
            "<orientation>horizontal</orientation>", "<focusposition>1</focusposition>", "<movement>0</movement>",
            *view_nav(up), "<include>Lib_OpenRight</include>", "<ondown>noop</ondown>",
            '<scrolltime tween="cubic" easing="out">200</scrolltime>', '<viewtype label="$LOCALIZE[31654]">wrap</viewtype>',
            "<preloaditems>1</preloaditems>",
            "<visible>Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(albums)</visible>",
            gw_layouts()]
    lst = '<control type="fixedlist" id="510">' + NL + NL.join(ind(b, 1) for b in body) + NL + "</control>"
    return NL.join([gw_light(), lst, gw_placards(), date_probes()])


def gw_kind(key):
    return {"episodes": "Container.Content(episodes)", "albums": "Container.Content(albums)",
            "posters": "!Container.Content(episodes) + !Container.Content(albums)"}[key]


def gw_light():
    o = []
    for key, (_c, _pr, _fw, fr, _m, _pl) in GW.items():
        fx, fy, fw, fh = GW_LEFT + GW_SLOT + fr[0], GW_TOP + fr[1], fr[2], fr[3]
        pw, ph = round(fw * 2.05), round(fh * 1.5)
        px, py = fx + fw // 2 - pw // 2, fy + fh // 2 - round(0.03 * fh) - ph // 2
        o.append(group([
            group([img(fx - 50, fy - 42, fw + 100, fh + 104, "vn/shadow.png", "$VAR[shadow]", border="56",
                       anims=["<include>VN_ShadowSteps</include>"])], anims=fade_cond("!Control.HasFocus(510) | Container(510).Scrolling", 150)),
            group([spot(px, py, pw, ph)],
                  anims=fade_cond("!Control.HasFocus(510)", 200)),
        ], vis=f"Control.IsVisible(510) + {gw_kind(key)} + !ListItem.IsParentFolder"))
    return NL.join(o)


def gw_placards():
    """The gallery wall's curator card (DESIGN 6): the full card on posters (668 x 888); episodes and albums keep their
    520 px placards beside their wider works."""
    o = []
    ids = {"posters": 9582, "episodes": 9588, "albums": 9594}
    for key, (_c, _pr, _fw, _fr, _m, (x0, y0, w, h)) in GW.items():
        if key == "posters":
            fields = [PL.title("$VAR[Lib_PTitle]"), PL.byline("$VAR[Lib_L2]"),
                      PL.line("genres", "$VAR[Lib_L3]", "top", when="!String.IsEmpty(ListItem.Genre)"),
                      PL.line("made", "$VAR[Lib_Made]", "top", when="[!String.IsEmpty(ListItem.Studio) | !String.IsEmpty(ListItem.Country)]"),
                      PL.box("tagline", "$INFO[ListItem.Tagline]", "mid", "font_quote", 2, color="$VAR[ink]", probe=True,
                             when="!String.IsEmpty(ListItem.Tagline)"),
                      PL.box("premise", "$VAR[Lib_Prem]", "mid", "font_small", 2, gap=12, grow=8, when=PREM_WHEN),
                      # no cast line: Kodi's videodb listings carry no cast (LESSONS Nocturne / Six Degrees), so its two
                      # budgeted lines go to the premise; the info page (M3) has the cast
                      PL.flags("ListItem"), PL.line("status", "$VAR[Lib_Status]", "bot", gap=14, when=STATUS_WHEN),
                      PL.line("collection", "$VAR[Lib_Coll]", "bot", gap=4, when="!String.IsEmpty(ListItem.Set)"),
                      PL.line("credit", "$VAR[Lib_Credit]", "bot", gap=4, when="$EXP[Lib_DateOK]"),
                      PL.rule(), PL.keyline("$VAR[Lib_KeyLine]")]
            pad = (36, 38)
        elif key == "episodes":
            fields = [PL.title("$VAR[Lib_PTitle]"), PL.byline("$VAR[Lib_L2]"),
                      PL.line("genres", "$INFO[ListItem.TVShowTitle]", "top"),
                      PL.box("premise", "$VAR[Lib_Prem]", "mid", "font_small", 2, grow=8, when=PREM_WHEN),
                      PL.flags("ListItem"), PL.line("status", "$VAR[Lib_Status]", "bot", gap=14),
                      PL.rule(), PL.keyline("$VAR[Lib_KeyLine]")]
            pad = (32, 36)
        else:
            fields = [PL.title("$VAR[Lib_PTitle]"), PL.byline("$VAR[Lib_L2]"), PL.line("genres", "$VAR[Lib_L3]", "top"),
                      PL.box("premise", "$VAR[Lib_Prem]", "mid", "font_small", 2, grow=12, when=PREM_WHEN)]
            pad = (32, 36)
        o.append(PL.curator(fields, x0, y0, w, h, pad, PROBE_IDS(ids[key]), cid=9561 if key == "posters" else None,
                            vis=f"Control.IsVisible(510) + {gw_kind(key)} + !ListItem.IsParentFolder"))
    return NL.join(o)


def gl(x, y, w, h, inner, bottom_align=False):
    al = "\t<align>bottom</align>\n" if bottom_align else ""
    return (f'<control type="grouplist">\n\t<left>{x}</left>\n\t<top>{y}</top>\n\t<width>{w}</width>\n\t<height>{h}</height>\n'
            f"\t<itemgap>0</itemgap>\n{al}\t<usecontrolcoords>true</usecontrolcoords>\n{ind(inner, 1)}\n</control>")


# ================================================================ 50 Catalogue
CAT_ROWS = 13


def cat_row(focused):
    hf = "Control.HasFocus(50)"
    o = []
    if focused:
        o += [twin_img(0, 0, 1040, 64, "vn/white.png", "card", vis=hf),
              twin_img(0, 0, 1040, 1, "vn/white.png", "card_edge", vis=hf),
              twin_img(0, 63, 1040, 1, "vn/white.png", "card_edge", vis=hf)]
    else:
        o.append(twin_img(24, 63, 992, 1, "vn/white.png", "rule"))
    playing = "ListItem.IsPlaying"
    o.append(twin_img(6, 27, 10, 10, "vn/dot.png", "ink", vis=playing))
    left_col = "$VAR[ink]" if focused else "$VAR[ink2]"
    if focused:
        o.append(label(24, 0, 760, 64, "$VAR[Lib_CLeft]", "font_body", "$VAR[ink]", aligny="center", vis=hf))
        o.append(label(24, 0, 760, 64, "$VAR[Lib_CLeft]", "font_body", "$VAR[ink2]", aligny="center", vis=f"!{hf}"))
        o.append(label(792, 0, 224, 64, "$VAR[Lib_CRightF]", "font_small", "$VAR[ink]", align="right", aligny="center", vis=hf))
        o.append(label(792, 0, 224, 64, "$VAR[Lib_CRight]", "font_small", "$VAR[ink2]", align="right", aligny="center", vis=f"!{hf}"))
    else:
        o.append(label(24, 0, 760, 64, "$VAR[Lib_CLeft]", "font_body", left_col, aligny="center"))
        o.append(label(792, 0, 224, 64, "$VAR[Lib_CRight]", "font_small", "$VAR[ink2]", align="right", aligny="center"))
    o.append(twin_img(1024, 27, 10, 10, "vn/dot.png", "ink2", vis="Integer.IsGreater(ListItem.PlayCount,0) + !ListItem.IsParentFolder"))
    return NL.join(o)


CAT_FIG = {  # kind: (condition, frame w, frame h, art var, aspect)
    "poster": ("[Container.Content(movies) | Container.Content(sets) | Container.Content(tvshows) | Container.Content(seasons) | Container.Content(musicvideos)]",
               304, 444, "$VAR[Lib_ItemArt]", "scale"),
    "land": ("[Container.Content(episodes) | [!Container.Content(movies) + !Container.Content(sets) + !Container.Content(tvshows) + "
             "!Container.Content(seasons) + !Container.Content(musicvideos) + !Container.Content(albums) + !Container.Content(songs) + "
             "!Container.Content(artists) + !Container.Content(addons)]]", 552, 321, "$VAR[Lib_StillArt]", "scale"),
    "square": ("[Container.Content(albums) | Container.Content(songs) | Container.Content(artists) | Container.Content(addons)]",
               424, 424, "$VAR[Lib_SquareArt]", "keep"),
}


def catalogue(up):
    body = ["<left>120</left>", "<top>182</top>", "<width>1040</width>", f"<height>{64 * CAT_ROWS}</height>",
            *view_nav(up, ['<onright condition="Control.IsVisible(61)">61</onright>']), "<include>Lib_OpenRight</include>",
            f"<ondown>{up}</ondown>", "<pagecontrol>61</pagecontrol>", "<include>Anim_ScrollRow</include>",
            '<viewtype label="$LOCALIZE[31655]">list</viewtype>',
            f'<itemlayout width="1040" height="64">{NL}{ind(cat_row(False), 1)}{NL}</itemlayout>',
            f'<focusedlayout width="1040" height="64">{NL}{ind(cat_row(True), 1)}{NL}</focusedlayout>']
    lst = '<control type="list" id="50">' + NL + NL.join(ind(b, 1) for b in body) + NL + "</control>"
    return NL.join([lst, group([scrollbar(61, 1180, 182, 832, "50")], vis="Control.IsVisible(50)"), cat_figure()])


def cat_figure():
    """The focused item's figure in a 10 px mat at x 1240 and its placard below it, down to y 1004 (the placard hangs
    BELOW the work, so it is exempt from the equal-height rule: DESIGN 6)."""
    o = []
    has_art = {}
    for kind, (cond, fw, fh, art, aspect) in CAT_FIG.items():
        src = {"poster": "[!String.IsEmpty(ListItem.Art(poster)) | !String.IsEmpty(ListItem.Art(tvshow.poster)) | !String.IsEmpty(ListItem.Art(thumb))]",
               "land": "[!String.IsEmpty(ListItem.Art(thumb)) | !String.IsEmpty(ListItem.Art(tvshow.fanart)) | !String.IsEmpty(ListItem.Art(fanart))]",
               "square": "[!String.IsEmpty(ListItem.Art(thumb)) | !String.IsEmpty(ListItem.Icon)]"}[kind]
        has_art[kind] = f"{cond} + {src} + !ListItem.IsParentFolder"
        o.append(group([
            img(1240 - 50, 182 - 42, fw + 100, fh + 104, "vn/shadow.png", "$VAR[shadow]", border="56", anims=["<include>VN_ShadowSteps</include>"]),
            img(1240, 182, fw, fh, "vn/white.png", "$VAR[frame]"),
            img(1242, 184, fw - 4, fh - 4, "vn/white.png", "$VAR[mat]"),
            img(1242, 184, fw - 4, fh - 4, "vn/mat_falloff.png", vis=DARK),
            img(1252, 194, fw - 24, fh - 24, art, aspect=aspect, background=True, fadetime=200),
        ], vis=f"Control.IsVisible(50) + {has_art[kind]}"))
    w = 552
    fields = [PL.title("$VAR[Lib_PTitle]"), PL.byline("$VAR[Lib_L2]"),
              PL.line("genres", "$VAR[Lib_L3]", "top"),
              PL.box("tagline", "$INFO[ListItem.Tagline]", "mid", "font_quote", 2, color="$VAR[ink]", probe=True,
                     when="!String.IsEmpty(ListItem.Tagline)"),
              PL.box("premise", "$VAR[Lib_Prem]", "mid", "font_small", 1, gap=12, grow=14, when=PREM_WHEN),
              PL.flags("ListItem"), PL.line("status", "$VAR[Lib_Status]", "bot", gap=14, when=STATUS_WHEN)]
    # squares are music (and add-ons): no key line. Music items always land there (Kodi gives them a default
    # ListItem.Icon even without a thumb), so the art-less placard keeps its key for the video kinds
    keyed = {"square": []}
    any_art = " | ".join(f"[{c}]" for c in has_art.values())
    for i, (kind, fh) in enumerate([(k, v[2]) for k, v in CAT_FIG.items()] + [("none", None)]):
        y = 182 + fh + 24 if fh else 182
        h = 1004 - y
        vis = has_art[kind] if kind != "none" else f"![{any_art}]"
        tail = keyed.get(kind, [PL.rule(), PL.keyline("$VAR[Lib_KeyLine]")])
        o.append(PL.curator(fields + tail, 1240, y, w, h, (26, 30), PROBE_IDS(9620 + 6 * i),
                            vis=f"Control.IsVisible(50) + !ListItem.IsParentFolder + {vis}"))
    return NL.join(o)


# ================================================================ empty folder, the window
def empty():
    return label(120, 480, 1680, 64, f"$LOCALIZE[{S['empty']}]", "font_label", "$VAR[ink2]", align="center",
                 aligny="center", vis="Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating", selected=False)


def window():
    np_nav = NL.join(['\t<include name="Lib_NowPlayingNav">', "\t\t<onup>$PARAM[sort_id]</onup>", "\t\t<ondown>50</ondown>",
                      "\t\t<onback>50</onback>", "\t</include>"])
    return f"""{np_nav}
	<!-- the window body. params: is_video (true | false), kind (video | music), order_click, view_id / opt_id /
	     sort_id (the header words) -->
	<include name="Lib_Window">
		<definition>
			<include>VN_Room</include>
			<control type="group">
				<include>Anim_WindowContent</include>
				<include content="Lib_Header">
					<param name="view_id" value="$PARAM[view_id]"/>
					<param name="opt_id" value="$PARAM[opt_id]"/>
					<param name="sort_id" value="$PARAM[sort_id]"/>
				</include>
				<include content="Lib_View500"><param name="up" value="$PARAM[view_id]"/></include>
				<include content="Lib_View510"><param name="up" value="$PARAM[view_id]"/></include>
				<include content="Lib_View50"><param name="up" value="$PARAM[view_id]"/></include>
				<include>Lib_Empty</include>
				<control type="group">
					<animation effect="fade" start="100" end="0" time="150" condition="$EXP[Lib_SalonTopRight]">Conditional</animation>
					<include content="VN_NowPlaying">
						<param name="maxw" value="560"/>
						<param name="nav" value="Lib_NowPlayingNav"/>
						<param name="sort_id" value="$PARAM[sort_id]"/>
					</include>
				</control>
			</control>
			<include content="Lib_Panel">
				<param name="is_video" value="$PARAM[is_video]"/>
				<param name="kind" value="$PARAM[kind]"/>
				<param name="order_click" value="$PARAM[order_click]"/>
				<param name="header_back" value="$PARAM[opt_id]"/>
			</include>
			<include content="Lib_Picker">
				<param name="header_back" value="$PARAM[view_id]"/>
			</include>
		</definition>
	</include>"""


def main():
    PL.set_prefix("Lib")
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_libviews.py - edit the generator, then re-run. "The collection": header, Salon 500,
     Gallery wall 510, Catalogue 50 (docs/skin.vernissage/screens/LibraryWindows.md and View_*.md). -->
<includes>
{expressions()}
__PLACARD_EXPRS__
{variables()}

	<!-- header (SPEC 7). params: view_id, opt_id, sort_id -->
	<include name="Lib_Header">
		<definition>
{ind(header("$PARAM[view_id]", "$PARAM[opt_id]", "$PARAM[sort_id]"), 3)}
		</definition>
	</include>

	<!-- 500 Salon: 9 columns of 170 x 255 prints (albums / artists 6 of 240), the lit work enlarged in place with its
	     placard inside the focused layout. param: up (the View word) -->
	<include name="Lib_View500">
		<definition>
{ind(salon("$PARAM[up]"), 3)}
		</definition>
	</include>

	<!-- 510 Gallery wall: one big work and its 520 px placard, grey neighbours cut by the screen edges. param: up -->
	<include name="Lib_View510">
		<definition>
{ind(gallery("$PARAM[up]"), 3)}
		</definition>
	</include>

	<!-- 50 Catalogue: single lines, the focused item's figure and placard at the right. param: up -->
	<include name="Lib_View50">
		<definition>
{ind(catalogue("$PARAM[up]"), 3)}
		</definition>
	</include>

	<!-- one Catalogue-style row for lists outside the library views (the listening room's Queue / album tracks).
	     params: color (left label), color2 (right label) -->
	<include name="Lib_CatalogueRow">
		<definition>
{ind(label(24, 0, 1200, 64, "$VAR[Lib_CLeft]", "font_body", "$PARAM[color]", aligny="center"), 3)}
{ind(label(1240, 0, 416, 64, "$VAR[Lib_CRight]", "font_small", "$PARAM[color2]", align="right", aligny="center"), 3)}
		</definition>
	</include>

	<include name="Lib_Empty">
{ind(empty(), 2)}
	</include>

{window()}
</includes>
"""
    body = body.replace("__PLACARD_EXPRS__", PL.expressions_xml(body))
    OUT.write_text(body, encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {body.count('<control')} controls, {len(body) // 1024} KB")


if __name__ == "__main__":
    main()
