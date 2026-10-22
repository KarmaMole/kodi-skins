"""Generate 1080i/Includes_Sentence.xml: the machinery behind the Home sentence.

ONE table below (kinds -> phrases -> options) drives everything:
  * the static "spinner" lists (wraplists, one per phrase per kind) whose items carry
    label / key / rule (raw xsp JSON fragment) / enc (the same, URL-encoded) / sortby / sortorder
  * the results content path, assembled from those item properties
  * the committed (persisted) copy of the sentence in Skin.String(sentence.<kind>.<phrase>)
  * spin / commit / restore / save / load action blocks for the Home window

Debounce (the results only reload once a phrase rests): a hidden 2-item timer list (399) with
<autoscroll time="REST"> moves to item 2 after REST ms without a spin (Kodi only accumulates the
autoscroll delay while its condition holds: GUIBaseContainer::UpdateAutoScrolling; Majan's proven
"rest timer"). Every spin resets it to item 1. The results path is
    rested  -> built from the LIVE spinner items  ($INFO[Container(id).ListItem.Property(rule)])
    moving  -> built from the COMMITTED Skin.Strings (what the results already show)
Each spin first commits the live sentence if it was rested, so "moving" keeps showing the last
rested results and nothing reloads until you stop. Leaving a phrase commits unconditionally.
Kodi resolves the conditions and $INFO of an action list before running any of it
(CGUIAction::ExecuteActions), so commit-then-move in one <onup> commits the pre-move value.

xsp JSON accepted by Kodi 21 in videodb:// and musicdb:// paths (verified over JSON-RPC
Files.GetDirectory on Omar's library, 2026-10-18):
  videodb://movies/titles/?xsp={"rules":{"and":[{"field":"time","operator":"lessthan","value":["7200"]}]},"type":"movies"}
  - time is in seconds; year compares the release year; playcount "is 0" = unwatched;
    several values in one rule are OR'ed; "order" inside the xsp is IGNORED by the library
    node, so ordering uses the container's sortby/sortorder (dynamic via $VAR).
  - every "and" array starts with an always-true base rule so each fragment can carry its
    own leading comma; "any" options have an empty fragment.
  - never put & + % # in values (URL option separators / decoding): use "contains" on a stem.
The raw form goes into <content>; ActivateWindow needs the URL-encoded form (no commas/quotes,
which the builtin parser would split on).

Usage:  python skins/skin.sentence/_src/make_sentence.py
"""
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

OUT = Path(__file__).resolve().parent.parent / "1080i" / "Includes_Sentence.xml"
REST_MS = {"quick": 250, "normal": 400, "patient": 700}

# -------------------------------------------------------------------------------- the table
DECADES = [
    ("any", "any decade", []),
    ("d2020", "the 2020s", [("year", "greaterthan", ["2019"])]),
    ("d2010", "the 2010s", [("year", "greaterthan", ["2009"]), ("year", "lessthan", ["2020"])]),
    ("d2000", "the 2000s", [("year", "greaterthan", ["1999"]), ("year", "lessthan", ["2010"])]),
    ("d1990", "the 90s", [("year", "greaterthan", ["1989"]), ("year", "lessthan", ["2000"])]),
    ("d1980", "the 80s", [("year", "greaterthan", ["1979"]), ("year", "lessthan", ["1990"])]),
    ("d1970", "the 70s", [("year", "greaterthan", ["1969"]), ("year", "lessthan", ["1980"])]),
    ("old", "before 1970", [("year", "lessthan", ["1970"])]),
]
SEEN_VIDEO = [
    ("any", "may have seen", []),
    ("unseen", "haven't seen", [("playcount", "is", ["0"])]),
    ("started", "have started", [("inprogress", "true", [])]),
    ("seen", "have seen", [("playcount", "greaterthan", ["0"])]),
]
TV_GENRES = [
    ("any", "any genre", []),
    ("drama", "serious", [("genre", "contains", ["Drama"])]),
    ("comedy", "funny", [("genre", "contains", ["Comedy"])]),
    ("scifi", "science fiction", [("genre", "contains", ["Sci-Fi", "Science Fiction"])]),
    ("crime", "about crime", [("genre", "contains", ["Crime"])]),
    ("mystery", "mysterious", [("genre", "contains", ["Mystery"])]),
    ("action", "action-packed", [("genre", "contains", ["Action"])]),
    ("adventure", "adventurous", [("genre", "contains", ["Adventure"])]),
    ("fantasy", "fantastical", [("genre", "contains", ["Fantasy"])]),
    ("thriller", "thrilling", [("genre", "contains", ["Thriller", "Suspense"])]),
    ("animation", "animated", [("genre", "contains", ["Animation", "Anime"])]),
    ("horror", "scary", [("genre", "contains", ["Horror"])]),
    ("documentary", "documentary", [("genre", "contains", ["Documentary"])]),
]

KINDS = [
    {
        "key": "film", "label": "a film", "one": "film", "many": "films", "window": "Videos",
        "base": "videodb://movies/titles/", "type": "movies", "basefield": "title", "prefix": "that's",
        "phrases": {
            "len": ([
                ("any", "any length", []),
                ("u90", "under 90 minutes", [("time", "lessthan", ["5400"])]),
                ("u120", "under 2 hours", [("time", "lessthan", ["7200"])]),
                ("long", "something long", [("time", "greaterthan", ["8100"])]),
            ], 3),
            "genre": ([
                ("any", "any genre", []),
                ("drama", "serious", [("genre", "is", ["Drama"])]),
                ("comedy", "funny", [("genre", "is", ["Comedy"])]),
                ("thriller", "thrilling", [("genre", "is", ["Thriller"])]),
                ("action", "action-packed", [("genre", "is", ["Action"])]),
                ("scifi", "science fiction", [("genre", "is", ["Science Fiction"])]),
                ("adventure", "adventurous", [("genre", "is", ["Adventure"])]),
                ("crime", "about crime", [("genre", "is", ["Crime"])]),
                ("fantasy", "fantastical", [("genre", "is", ["Fantasy"])]),
                ("romance", "romantic", [("genre", "is", ["Romance"])]),
                ("mystery", "mysterious", [("genre", "is", ["Mystery"])]),
                ("history", "historical", [("genre", "is", ["History"])]),
                ("horror", "scary", [("genre", "is", ["Horror"])]),
                ("documentary", "documentary", [("genre", "is", ["Documentary"])]),
                ("family", "for the family", [("genre", "is", ["Family"])]),
                ("animation", "animated", [("genre", "is", ["Animation"])]),
                ("war", "about war", [("genre", "is", ["War"])]),
                ("music", "about music", [("genre", "is", ["Music"])]),
                ("western", "a western", [("genre", "is", ["Western"])]),
            ], 1),
            "decade": (DECADES, 1),
            "seen": (SEEN_VIDEO, 2),
            "order": ([
                ("rating", "best rated first", "rating", "descending"),
                ("newest", "newest first", "year", "descending"),
                ("added", "recently added first", "dateadded", "descending"),
                ("short", "shortest first", "time", "ascending"),
                ("random", "in no order at all", "random", "ascending"),
                ("az", "A to Z", "title", "ascending"),
            ], 1),
        },
    },
    {
        "key": "episode", "label": "an episode", "one": "episode", "many": "episodes", "window": "Videos",
        "base": "videodb://tvshows/titles/-1/-1/-1/-1/", "type": "episodes", "basefield": "title", "prefix": "that's",
        "phrases": {
            "len": ([
                ("any", "any length", []),
                ("u30", "under 30 minutes", [("time", "lessthan", ["1800"])]),
                ("u60", "under an hour", [("time", "lessthan", ["3600"])]),
                ("o60", "over an hour", [("time", "greaterthan", ["3599"])]),
            ], 1),
            "genre": (TV_GENRES, 1),
            "decade": (DECADES, 1),
            "seen": (SEEN_VIDEO, 2),
            "order": ([
                ("added", "recently added first", "dateadded", "descending"),
                ("newest", "newest first", "year", "descending"),
                ("rating", "best rated first", "rating", "descending"),
                ("short", "shortest first", "time", "ascending"),
                ("random", "in no order at all", "random", "ascending"),
            ], 1),
        },
    },
    {
        "key": "show", "label": "a show", "one": "show", "many": "shows", "window": "Videos",
        "base": "videodb://tvshows/titles/", "type": "tvshows", "basefield": "title", "prefix": "that's",
        "phrases": {
            "genre": (TV_GENRES, 1),
            "decade": (DECADES, 1),
            "seen": ([
                ("any", "may have seen", []),
                ("unseen", "haven't started", [("numwatched", "is", ["0"])]),
                ("started", "have started", [("inprogress", "true", [])]),
                ("seen", "have finished", [("playcount", "greaterthan", ["0"])]),
            ], 1),
            "order": ([
                ("added", "recently added first", "dateadded", "descending"),
                ("newest", "newest first", "year", "descending"),
                ("rating", "best rated first", "rating", "descending"),
                ("random", "in no order at all", "random", "ascending"),
                ("az", "A to Z", "title", "ascending"),
            ], 1),
        },
    },
    {
        "key": "album", "label": "an album", "one": "album", "many": "albums", "window": "Music",
        "base": "musicdb://albums/", "type": "albums", "basefield": "album", "prefix": "of",
        "phrases": {
            "genre": ([
                ("any", "any style", []),
                ("rock", "rock", [("genre", "contains", ["Rock"])]),
                ("alternative", "alternative", [("genre", "contains", ["Alternative", "Alt."])]),
                ("indie", "indie", [("genre", "contains", ["Indie"])]),
                ("pop", "pop", [("genre", "contains", ["Pop"])]),
                ("metal", "metal", [("genre", "contains", ["Metal"])]),
                ("soundtrack", "soundtracks", [("genre", "contains", ["Soundtrack"])]),
                ("classical", "classical music", [("genre", "contains", ["Classical"])]),
                ("electronic", "electronic music", [("genre", "contains", ["Electronic", "Dance"])]),
                ("comedy", "comedy", [("genre", "contains", ["Comedy"])]),
            ], 1),
            "decade": ([d for d in DECADES if d[0] not in ("d1970", "old")] + [("old", "before 1980", [("year", "lessthan", ["1980"])])], 1),
            "seen": ([
                ("any", "may have played", []),
                ("unseen", "haven't played", [("playcount", "is", ["0"])]),
                ("seen", "have played", [("playcount", "greaterthan", ["0"])]),
            ], 1),
            "order": ([
                ("newest", "newest first", "year", "descending"),
                ("added", "recently added first", "dateadded", "descending"),
                ("random", "in no order at all", "random", "ascending"),
                ("played", "most played first", "playcount", "descending"),
                ("az", "A to Z", "album", "ascending"),
            ], 1),
        },
    },
]
PHRASES = ["len", "genre", "decade", "seen", "order"]
PHRASE_NO = {"len": 2, "genre": 3, "decade": 4, "seen": 5, "order": 6}   # list id = 3<kind><no>
KIND_LIST = 311
# 0.9.11 main menu: kinds hidden in Skin settings (HideMenu.*). The kind list keeps all four items (saved
# sentences and the committed path store the kind's INDEX), so spinning steps over hidden kinds and a restore
# that lands on a hidden kind moves to the first shown one.
KIND_HIDE = {"film": "Skin.HasSetting(HideMenu.Movies)", "episode": "Skin.HasSetting(HideMenu.TVShows)",
             "show": "Skin.HasSetting(HideMenu.TVShows)", "album": "Skin.HasSetting(HideMenu.Music)"}


def kind_targets(i, step, n):
    """from 1-based kind index i, spinning by step: [(conditions, offset, target index)] for each candidate
    (the next kind, or past it while hidden). Mutually exclusive; none when every other kind is hidden."""
    out, skipped, j, off = [], [], i, 0
    for _ in range(n - 1):
        j = (j - 1 + step) % n + 1
        off += step
        h = KIND_HIDE[KINDS[j - 1]["key"]]
        if h in skipped:
            continue
        out.append((list(skipped) + [f"!{h}"], off, j))
        skipped.append(h)
    return out


def first_shown(n):
    """[(conditions, index)] of the first shown kind in list order"""
    out, skipped = [], []
    for j in range(1, n + 1):
        h = KIND_HIDE[KINDS[j - 1]["key"]]
        if h in skipped:
            continue
        out.append((list(skipped) + [f"!{h}"], j))
        skipped.append(h)
    return out
TIMER = 399
RESTED = f"Integer.IsEqual(Container({TIMER}).CurrentItem,2)"


def list_id(ki: int, p: str) -> int:
    return 300 + (ki + 1) * 10 + PHRASE_NO[p]


def frag(rules) -> str:
    out = []
    for field, op, vals in rules:
        v = ",".join('"%s"' % x for x in vals)
        out.append('{"field":"%s","operator":"%s","value":[%s]}' % (field, op, v))
    return "".join("," + r for r in out)


def base_rule(k) -> str:
    return '{"field":"%s","operator":"doesnotcontain","value":["~~~"]}' % k["basefield"]


def has(k, p) -> bool:
    return p in k["phrases"]


def lk(k) -> str:   # live kind condition
    return f"String.IsEqual(Container({KIND_LIST}).ListItem.Property(key),{k['key']})"


def ck(ki, k) -> str:  # committed kind condition (empty = film)
    if ki == 0:
        return "[String.IsEmpty(Skin.String(sentence.kind)) | String.IsEqual(Skin.String(sentence.kind),1)]"
    return f"String.IsEqual(Skin.String(sentence.kind),{ki + 1})"


def sk(k, p) -> str:
    return f"sentence.{k['key']}.{p}"


def x(s: str) -> str:
    return escape(s)


def gen() -> str:
    L = []
    a = L.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a("<!-- GENERATED by _src/make_sentence.py - edit the table there, not this file. -->")
    a("<!-- The Home sentence: spinner lists, live/committed xsp paths, spin/commit/restore/save/load. -->")
    a("<includes>")

    # ------------------------------------------------------------ expressions
    a(f'\t<expression name="Sen_Rested">{RESTED}</expression>')
    for ki, k in enumerate(KINDS):
        a(f'\t<expression name="Sen_LK_{k["key"]}">{lk(k)}</expression>')
        a(f'\t<expression name="Sen_CK_{k["key"]}">{ck(ki, k)}</expression>')
        a(f'\t<expression name="Sen_Shown_{k["key"]}">[{RESTED} + {lk(k)}] | [!{RESTED} + {ck(ki, k)}]</expression>')
    a(f'\t<expression name="Sen_LiveHasLen">{lk(KINDS[0])} | {lk(KINDS[1])}</expression>')

    # ------------------------------------------------------------ committed lookups
    for ki, k in enumerate(KINDS):
        for p in PHRASES:
            if not has(k, p):
                continue
            opts, default = k["phrases"][p]
            key = sk(k, p)
            # committed label / rule / encoded rule (or sortby / sortorder)
            def cond(i):
                c = f"String.IsEqual(Skin.String({key}),{i})"
                if i == default:
                    c = f"[{c} | String.IsEmpty(Skin.String({key}))]"
                return c
            if p != "order":  # the order phrase needs only its sort columns below
                a(f'\t<variable name="Sen_CL_{k["key"]}_{p}">')
                for i, o in enumerate(opts, 1):
                    a(f'\t\t<value condition="{cond(i)}">{x(o[1])}</value>')
                a("\t</variable>")
            if p == "order":
                for nm, col in (("CS", 2), ("CSO", 3)):
                    a(f'\t<variable name="Sen_{nm}_{k["key"]}">')
                    for i, o in enumerate(opts, 1):
                        a(f'\t\t<value condition="{cond(i)}">{o[col]}</value>')
                    a("\t</variable>")
            else:
                for nm, enc in (("CR", False), ("CE", True)):
                    a(f'\t<variable name="Sen_{nm}_{k["key"]}_{p}">')
                    for i, o in enumerate(opts, 1):
                        f = frag(o[2])
                        if not f:
                            continue
                        a(f'\t\t<value condition="{cond(i)}">{x(quote(f, safe="") if enc else f)}</value>')
                    a("\t</variable>")
    # committed labels by committed kind (library header / saved sentence text). The library header spells the
    # order its own way, so there is no Sen_CL_order (kodi-review flags unused variables).
    for p in PHRASES:
        if p == "order":
            continue
        a(f'\t<variable name="Sen_CL_{p}">')
        for ki, k in enumerate(KINDS):
            if has(k, p):
                a(f'\t\t<value condition="{ck(ki, k)}">$VAR[Sen_CL_{k["key"]}_{p}]</value>')
        a("\t</variable>")

    # ------------------------------------------------------------ live labels (by live kind)
    for off, nm in ((-1, "m1"), (0, ""), (1, "p1")):
        sfx = f"_{nm}" if nm else ""
        o = f"({off})" if off else ""
        a(f'\t<variable name="Sen_LL_kind{sfx}"><value>$INFO[Container({KIND_LIST}).ListItem{o}.Label]</value></variable>')
        for p in PHRASES:
            a(f'\t<variable name="Sen_LL_{p}{sfx}">')
            for ki, k in enumerate(KINDS):
                if has(k, p):
                    a(f'\t\t<value condition="{lk(k)}">$INFO[Container({list_id(ki, p)}).ListItem{o}.Label]</value>')
            a("\t</variable>")
    a('\t<variable name="Sen_Prefix">')
    for k in KINDS:
        a(f'\t\t<value condition="{lk(k)}">{x(k["prefix"])}</value>')
    a("\t</variable>")

    # ------------------------------------------------------------ paths
    def path(ki, k, live: bool, enc: bool) -> str:
        parts = []
        for p in PHRASES:
            if p == "order" or not has(k, p):
                continue
            if live:
                prop = "enc" if enc else "rule"
                parts.append(f"$INFO[Container({list_id(ki, p)}).ListItem.Property({prop})]")
            else:
                parts.append(f"$VAR[Sen_{'CE' if enc else 'CR'}_{k['key']}_{p}]")
        head = '{"rules":{"and":[' + base_rule(k)
        tail = ']},"type":"' + k["type"] + '"}'
        if enc:
            return k["base"] + "?xsp=" + quote(head, safe="") + "".join(parts) + quote(tail, safe="")
        return k["base"] + "?xsp=" + head + "".join(parts) + tail

    a('\t<variable name="Sen_Path">')
    for ki, k in enumerate(KINDS):
        a(f'\t\t<value condition="{RESTED} + {lk(k)}">{x(path(ki, k, True, False))}</value>')
    for ki, k in enumerate(KINDS):
        a(f'\t\t<value condition="{ck(ki, k)}">{x(path(ki, k, False, False))}</value>')
    a("\t</variable>")
    for nm, col, cv in (("Sen_SortBy", "sortby", "CS"), ("Sen_SortOrder", "sortorder", "CSO")):
        a(f'\t<variable name="{nm}">')
        for ki, k in enumerate(KINDS):
            a(f'\t\t<value condition="{RESTED} + {lk(k)}">$INFO[Container({list_id(ki, "order")}).ListItem.Property({col})]</value>')
        for ki, k in enumerate(KINDS):
            a(f'\t\t<value condition="{ck(ki, k)}">$VAR[Sen_{cv}_{k["key"]}]</value>')
        a("\t</variable>")
    # library: live encoded path + window (for "see them all" from Home)
    a('\t<variable name="Sen_LibPathLive">')
    for ki, k in enumerate(KINDS):
        a(f'\t\t<value condition="{lk(k)}">{x(path(ki, k, True, True))}</value>')
    a("\t</variable>")
    # nouns by the kind the results show
    for nm, fld in (("Sen_NounMany", "many"), ("Sen_NounOne", "one")):
        a(f'\t<variable name="{nm}">')
        for k in KINDS:
            a(f'\t\t<value condition="$EXP[Sen_Shown_{k["key"]}]">{k[fld]}</value>')
        a("\t</variable>")
    for nm, fld in (("Sen_NounManyC", "many"),):
        a(f'\t<variable name="{nm}">')
        for ki, k in enumerate(KINDS):
            a(f'\t\t<value condition="{ck(ki, k)}">{k[fld]}</value>')
        a("\t</variable>")

    # ------------------------------------------------------------ empty-state suggestion
    # relax the first narrowing phrase (genre, len, decade, seen) of the live kind
    order = ["genre", "len", "decade", "seen"]
    cs = []
    for ki, k in enumerate(KINDS):
        parts = [f"Integer.IsGreater(Container({list_id(ki, p)}).CurrentItem,1)" for p in order if has(k, p)]
        cs.append(f"[{lk(k)} + [{' | '.join(parts)}]]")
    a(f'\t<expression name="Sen_CanSuggest">{" | ".join(cs)}</expression>')
    a('\t<variable name="Sen_SuggestLabel">')
    for ki, k in enumerate(KINDS):
        for p in order:
            if has(k, p):
                lid = list_id(ki, p)
                a(f'\t\t<value condition="{lk(k)} + Integer.IsGreater(Container({lid}).CurrentItem,1)">{x(k["phrases"][p][0][0][1])}</value>')
    a("\t</variable>")
    a('\t<include name="Sen_SuggestClick">')
    for ki, k in enumerate(KINDS):
        prior = []
        for p in order:
            if not has(k, p):
                continue
            lid = list_id(ki, p)
            c = f"{lk(k)} + Integer.IsGreater(Container({lid}).CurrentItem,1)" + "".join(f" + Integer.IsEqual(Container({q}).CurrentItem,1)" for q in prior)
            a(f'\t\t<onclick condition="{c}">Control.Move({lid},-$INFO[Container({lid}).CurrentItem])</onclick>')
            a(f'\t\t<onclick condition="{c}">Control.Move({lid},1)</onclick>')
            a(f'		<onclick condition="{c}">Skin.SetString(sentence.live.{k["key"]}.{p},1)</onclick>')
            prior.append(lid)
    a(f'\t\t<onclick condition="{RESTED}">Control.Move({TIMER},-1)</onclick>')
    a("\t</include>")

    # ------------------------------------------------------------ data lists
    a('\t<include name="Sen_DataLists">')
    a("\t\t<!-- spinner lists: drawn 1px and transparent (offscreen controls still process) -->")

    def wraplist(lid, items):
        a(f'\t\t<control type="wraplist" id="{lid}">')
        a("\t\t\t<left>offscreen</left><top>offscreen</top><width>1</width><height>1</height>")
        a("\t\t\t<orientation>vertical</orientation><focusposition>0</focusposition><scrolltime>0</scrolltime>")
        a('\t\t\t<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>')
        a("\t\t\t<content>")
        for it in items:
            a("\t\t\t\t" + it)
        a("\t\t\t</content>")
        a("\t\t</control>")

    wraplist(KIND_LIST, [f'<item><label>{x(k["label"])}</label><property name="key">{k["key"]}</property><onclick>noop</onclick></item>' for k in KINDS])
    for ki, k in enumerate(KINDS):
        for p in PHRASES:
            if not has(k, p):
                continue
            opts, _ = k["phrases"][p]
            items = []
            for o in opts:
                if p == "order":
                    props = f'<property name="key">{o[0]}</property><property name="sortby">{o[2]}</property><property name="sortorder">{o[3]}</property>'
                else:
                    f = frag(o[2])
                    props = f'<property name="key">{o[0]}</property><property name="rule">{x(f)}</property><property name="enc">{x(quote(f, safe=""))}</property>'
                items.append(f"<item><label>{x(o[1])}</label>{props}<onclick>noop</onclick></item>")
            wraplist(list_id(ki, p), items)
    a("\t\t<!-- rest timer: item 2 = the sentence has rested REST ms since the last spin -->")
    a(f'\t\t<control type="list" id="{TIMER}">')
    a("\t\t\t<left>offscreen</left><top>offscreen</top><width>1</width><height>2</height>")
    a("\t\t\t<orientation>vertical</orientation><scrolltime>0</scrolltime>")
    for name, ms in REST_MS.items():
        cond = f'String.IsEqual(Skin.String(sentence.resttime),{name})' if name != "normal" else '!String.IsEqual(Skin.String(sentence.resttime),quick) + !String.IsEqual(Skin.String(sentence.resttime),patient)'
        a(f'\t\t\t<include condition="{cond}">Sen_Timer{ms}</include>')
    a('\t\t\t<itemlayout width="1" height="1"/><focusedlayout width="1" height="1"/>')
    a("\t\t\t<content><item><label>moving</label><onclick>noop</onclick></item><item><label>rested</label><onclick>noop</onclick></item></content>")
    a("\t\t</control>")
    a("\t</include>")
    for ms in REST_MS.values():
        a(f'\t<include name="Sen_Timer{ms}"><autoscroll time="{ms}">Integer.IsEqual(Container({TIMER}).CurrentItem,1)</autoscroll></include>')

    # ------------------------------------------------------------ commit / spin / restore
    def commit_lines(tag, extra_cond=""):
        ec = f"{extra_cond} + " if extra_cond else ""
        out = [f'\t\t<{tag}{(" condition=" + chr(34) + extra_cond + chr(34)) if extra_cond else ""}>Skin.SetString(sentence.kind,$INFO[Container({KIND_LIST}).CurrentItem])</{tag}>']
        for ki, k in enumerate(KINDS):
            for p in PHRASES:
                if has(k, p):
                    out.append(f'\t\t<{tag} condition="{ec}{lk(k)}">Skin.SetString({sk(k, p)},$INFO[Container({list_id(ki, p)}).CurrentItem])</{tag}>')
        return out

    # only the commits the skin calls (onleft / onright / onback / onup / ondown variants went unused)
    for tag in ("onclick", "onunfocus"):
        a(f'\t<include name="Sen_Commit_{tag}">')
        L.extend(commit_lines(tag))
        a("\t</include>")
    a('\t<include name="Sen_CommitOnUnload">')
    L.extend(commit_lines("onunload"))
    a("\t</include>")

    for p in ["kind"] + PHRASES:
        for tag, step in (("onup", -1), ("ondown", 1)):
            a(f'\t<include name="Sen_Spin_{p}_{tag}">')
            L.extend(commit_lines(tag, RESTED))
            if p == "kind":
                # move to the next shown kind (step over hidden ones) and keep the exact live value for restore
                # (sentence.live.*): the post-move index, written literally
                n = len(KINDS)
                for i in range(1, n + 1):
                    for conds, off, nxt in kind_targets(i, step, n):
                        c = " + ".join([f"Integer.IsEqual(Container({KIND_LIST}).CurrentItem,{i})"] + conds)
                        a(f'\t\t<{tag} condition="{c}">Control.Move({KIND_LIST},{off})</{tag}>')
                        a(f'\t\t<{tag} condition="{c}">Skin.SetString(sentence.live.kind,{nxt})</{tag}>')
            else:
                for ki, k in enumerate(KINDS):
                    if has(k, p):
                        lid = list_id(ki, p)
                        a(f'\t\t<{tag} condition="{lk(k)}">Control.Move({lid},{step})</{tag}>')
                        n = len(k["phrases"][p][0])
                        for i in range(1, n + 1):
                            nxt = (i - 1 + step) % n + 1
                            a(f'\t\t<{tag} condition="{lk(k)} + Integer.IsEqual(Container({lid}).CurrentItem,{i})">Skin.SetString(sentence.live.{k["key"]}.{p},{nxt})</{tag}>')
            a(f'\t\t<{tag} condition="{RESTED}">Control.Move({TIMER},-1)</{tag}>')
            a("\t</include>")

    a('\t<include name="Sen_Restore">')
    a(f"\t\t<onload>Control.Move({KIND_LIST},-$INFO[Container({KIND_LIST}).CurrentItem])</onload>")
    # restore order: the exact live value (sentence.live.*, written on every spin), else the committed
    # value, else the default. A digit-only $VAR value used in an action is read as a string id
    # (device 2026-10-18), so defaults go in literally and stored indexes through $INFO.
    lv, cm = "Skin.String(sentence.live.kind)", "Skin.String(sentence.kind)"
    n = len(KINDS)
    # the kind to restore, by source; a hidden kind is replaced by the first shown one (written literally)
    for v in range(1, n + 1):
        src = (f"[[!String.IsEmpty({lv}) + String.IsEqual({lv},{v})] | [String.IsEmpty({lv}) + !String.IsEmpty({cm}) + String.IsEqual({cm},{v})]"
               + (f" | [String.IsEmpty({lv}) + String.IsEmpty({cm})]]" if v == 1 else "]"))
        h = KIND_HIDE[KINDS[v - 1]["key"]]
        a(f'\t\t<onload condition="{src} + !{h}">Control.Move({KIND_LIST},{v})</onload>')
        for conds, j in first_shown(n):
            if j == v:
                continue
            a(f'\t\t<onload condition="{src} + {h} + {" + ".join(conds)}">Control.Move({KIND_LIST},{j})</onload>')
            a(f'\t\t<onload condition="{src} + {h} + {" + ".join(conds)}">Skin.SetString(sentence.live.kind,{j})</onload>')
    for ki, k in enumerate(KINDS):
        for p in PHRASES:
            if has(k, p):
                lid = list_id(ki, p)
                default = k["phrases"][p][1]
                lv = f"Skin.String(sentence.live.{k['key']}.{p})"
                cm = f"Skin.String({sk(k, p)})"
                a(f"\t\t<onload>Control.Move({lid},-$INFO[Container({lid}).CurrentItem])</onload>")
                a(f'\t\t<onload condition="!String.IsEmpty({lv})">Control.Move({lid},$INFO[{lv}])</onload>')
                a(f'\t\t<onload condition="String.IsEmpty({lv}) + !String.IsEmpty({cm})">Control.Move({lid},$INFO[{cm}])</onload>')
                a(f'\t\t<onload condition="String.IsEmpty({lv}) + String.IsEmpty({cm})">Control.Move({lid},{default})</onload>')
    a("\t</include>")

    # ------------------------------------------------------------ library header (MyVideoNav / MyMusicNav)
    # The collapsed sentence stays editable: OK on a phrase moves it to its next value, saves it (so the
    # Home sentence follows) and re-filters the window in place (Container.Update(...,replace)). The new
    # path is written out with the NEXT fragment literally, because $VAR/$INFO in an action list are
    # resolved before the Skin.SetString runs.
    a('\t<variable name="Sen_LibLead">')
    for ki, k in enumerate(KINDS):
        lead = {"film": "Films", "episode": "Episodes", "show": "Shows that are", "album": "Albums of"}[k["key"]]
        a(f'\t\t<value condition="{ck(ki, k)}">{lead}</value>')
    a("\t</variable>")
    for p in PHRASES:
        if p == "order":
            continue
        conds = [ck(ki, k) for ki, k in enumerate(KINDS) if has(k, p)]
        a(f'\t<expression name="Sen_CHas_{p}">{" | ".join(conds)}</expression>')
        a(f'\t<include name="Sen_LibOnclick_{p}">')
        for ki, k in enumerate(KINDS):
            if not has(k, p):
                continue
            opts, default = k["phrases"][p]
            key = sk(k, p)
            for i, o in enumerate(opts, 1):
                nxt = i % len(opts) + 1
                c = f"String.IsEqual(Skin.String({key}),{i})"
                if i == default:
                    c = f"[{c} | String.IsEmpty(Skin.String({key}))]"
                c = f"{ck(ki, k)} + {c}"
                parts = []
                for q in PHRASES:
                    if q == "order" or not has(k, q):
                        continue
                    if q == p:
                        parts.append(quote(frag(opts[nxt - 1][2]), safe=""))
                    else:
                        parts.append(f"$VAR[Sen_CE_{k['key']}_{q}]")
                head = '{"rules":{"and":[' + base_rule(k)
                tail = ']},"type":"' + k["type"] + '"}'
                pth = k["base"] + "?xsp=" + quote(head, safe="") + "".join(parts) + quote(tail, safe="")
                a(f'\t\t<onclick condition="{c}">Skin.SetString({key},{nxt})</onclick>')
                a(f'		<onclick condition="{c}">Skin.SetString(sentence.live.{k["key"]}.{p},{nxt})</onclick>')
                a(f'\t\t<onclick condition="{c}">Container.Update({x(pth)},replace)</onclick>')
        a("\t</include>")

    # ------------------------------------------------------------ saved sentences (3 slots)
    for n in (1, 2, 3):
        # save live sentence into slot n
        a(f'\t<include name="Sen_SlotSave{n}">')
        prev = "".join(f" + !String.IsEmpty(Skin.String(sentence.slot{m}.name))" for m in range(1, n))
        c = f"String.IsEmpty(Skin.String(sentence.slot{n}.name)){prev}"
        if n == 3:  # all three kept: the newest replaces the third
            c = prev[3:]
        a(f'\t\t<onclick condition="{c}">Skin.SetString(sentence.slot{n}.name)</onclick>')
        a(f'\t\t<onclick condition="{c}">Skin.SetString(sentence.slot{n}.kind,$INFO[Container({KIND_LIST}).CurrentItem])</onclick>')
        for ki, k in enumerate(KINDS):
            for p in PHRASES:
                if has(k, p):
                    a(f'\t\t<onclick condition="{c} + {lk(k)}">Skin.SetString(sentence.slot{n}.{p},$INFO[Container({list_id(ki, p)}).CurrentItem])</onclick>')
        a("\t</include>")
        # load slot n into committed + live
        a(f'\t<include name="Sen_SlotLoad{n}">')
        a(f"\t\t<onclick>Skin.SetString(sentence.kind,$INFO[Skin.String(sentence.slot{n}.kind)])</onclick>")
        a(f"		<onclick>Skin.SetString(sentence.live.kind,$INFO[Skin.String(sentence.slot{n}.kind)])</onclick>")
        a(f"\t\t<onclick>Control.Move({KIND_LIST},-$INFO[Container({KIND_LIST}).CurrentItem])</onclick>")
        a(f"\t\t<onclick>Control.Move({KIND_LIST},$INFO[Skin.String(sentence.slot{n}.kind)])</onclick>")
        for ki, k in enumerate(KINDS):
            sc = f"String.IsEqual(Skin.String(sentence.slot{n}.kind),{ki + 1})"
            for p in PHRASES:
                if has(k, p):
                    lid = list_id(ki, p)
                    a(f'\t\t<onclick condition="{sc}">Skin.SetString({sk(k, p)},$INFO[Skin.String(sentence.slot{n}.{p})])</onclick>')
                    a(f'		<onclick condition="{sc}">Skin.SetString(sentence.live.{k["key"]}.{p},$INFO[Skin.String(sentence.slot{n}.{p})])</onclick>')
                    a(f'\t\t<onclick condition="{sc}">Control.Move({lid},-$INFO[Container({lid}).CurrentItem])</onclick>')
                    a(f'\t\t<onclick condition="{sc}">Control.Move({lid},$INFO[Skin.String(sentence.slot{n}.{p})])</onclick>')
        a("\t</include>")
        # the slot's sentence, read back as text (top line hint)
    a("</includes>")
    return "\n".join(L) + "\n"


def main():
    OUT.write_text(finish_xml(gen()), encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
