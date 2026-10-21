"""Generate 1080i/Includes_Dates.xml: Keepsake's date stamps, diary dates and spoken times.

Kodi 21 formats ListItem.LastPlayed / DateAdded with the region's short date and has no date maths and no
substrings (VideoGUIInfo.cpp: GetAsLocalizedDate(), date only). Omar's region prints dd/mm/yyyy (verified on the
Shield for Passe-partout), so string tests decompose a date (Passe-partout _src/make_dates.py):
    day   String.StartsWith(<d>,DD/)   month  String.Contains(<d>,/MM/)   year  String.Contains(<d>,/YYYY)
Everything here is built from those tests:
  KS_<F>_Stamp      'yy~mm~dd for the stamp font ("'" = the apostrophe bar, "~" = the gap)  -> '26 10 18
  KS_<F>_Long       Sunday 4 October          KS_<F>_LongY   Sunday 4 October 2026
  KS_<F>_DM         4 October                 KS_<F>_Short   4 Oct 2026      KS_<F>_MonY  October 2026
  KS_<F>_Gutter     Sun 4  (diary gutter)     KS_<F>_Wd      Sunday           KS_<F>_Year  2026
  KS_<F>_MonS       Oct                       KS_<F>_Month   October
Weekday = first weekday of (month, year) + day - 1 (mod 7): expressions KS_<F>_MC<k> list the months
2012-2032 whose 1st falls on weekday k; each weekday value tests (month class AND day set).
Raw library datetimes from Skin Variables (script.skinvariables get_dbitem_*_details, property "lastplayed",
"2026-10-04 04:54:12") give the time of day the region label lacks:
  KS_T_<S>_Clock    4:54 am        KS_T_<S>_Part   in the morning / that afternoon / that evening / that night /
  KS_T_<S>_Spoken   just after nine / around half past four / nearly ten
Also: KS_Yesterday (dd/mm/yyyy of yesterday from System.Date, stored in Window(Home) on Home load),
KS_DA_YearsAgo ("7 years ago"), expressions KS_SameYear_<a>_<b>, KS_SameMonth_<a>_<b>.
Resume minutes (Kodi has no resume time label): KS_ResumeMin = round(PercentPlayed x Duration / 100) from
nested tables (exact durations 1-60 min, 5-minute buckets 61-240 min), inside list layouts (ListItem.*).

Usage: python skins/skin.keepsake/_src/make_dates.py
"""
from __future__ import annotations

import calendar
import datetime as dt
from pathlib import Path
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Dates.xml"
MONTHS = "January February March April May June July August September October November December".split()
WD = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
Y0, Y1 = 2012, 2032          # weekday tables (lastplayed history on the box starts 2015)
YEARS_ALL = range(1990, 2041)  # plain year tables

# fields that get date variables: key -> infolabel
FIELDS = {
    "LP": "ListItem.LastPlayed",
    "DA": "ListItem.DateAdded",
    "CLP": "Container.ListItem.LastPlayed",
    "CDA": "Container.ListItem.DateAdded",
    "PR": "ListItem.Premiered",
    "MEM": "Container(9110).ListItem.LastPlayed",           # Home: a year ago
    "WAIT": "Container(9164).ListItem.DateAdded",           # Home: waiting since (oldest never played)
    "UA0": "Container(8101).ListItemAbsolute(0).DateAdded",  # unwatched row A: first added
    "UZ0": "Container(8111).ListItem.DateAdded",            # row A: last added (probe sorted descending)
    "UA1": "Container(8102).ListItemAbsolute(0).DateAdded",  # row B
    "UZ1": "Container(8112).ListItem.DateAdded",
    "UF": "Container(8101).ListItem.DateAdded",             # the focused print on the unwatched page
    "VP": "VideoPlayer.LastPlayed",                         # the playing film / episode (fullscreen info)
    "MP": "MusicPlayer.LastPlayed",                         # the playing song (now playing)
}
# fields that also need weekdays
WEEKDAY_FIELDS = {"LP", "CLP", "MEM", "VP", "MP"}
# diary slots: month-year of the items around the focus (static month dividers), view 520
DIARY = 520
SLOTS = range(-2, 8)
# raw datetime sources (Skin Variables detail containers)
RAW = {
    "MEM": "Container(9171).ListItem.Property(lastplayed)",   # Home: a year ago
    "STOP": "Container(9172).ListItem.Property(lastplayed)",  # Home: you stopped
    "EP": "Container(9173).ListItem.Property(lastplayed)",    # Home: you're on
    "DIA": "Container(9174).ListItem.Property(lastplayed)",   # diary: focused print
    "INF": "Container(9175).ListItem.Property(lastplayed)",   # info page
}
NUM_WORDS = "midnight one two three four five six seven eight nine ten eleven noon".split()


def U(s) -> str:
    """Digit-only labels are read as string ids (LESSONS 2): wrap them."""
    return f"[UPPERCASE]{s}[/UPPERCASE]"


def var(name, values):
    out = [f'\t<variable name="{name}">']
    for cond, val in values:
        if cond is None:
            out.append(f"\t\t<value>{val}</value>")
        else:
            out.append(f'\t\t<value condition="{cond}">{val}</value>')
    out.append("\t</variable>")
    return out


def date_vars(key, lab):
    o = []
    ok = f"String.Contains({lab},/)"
    o += var(f"KS_{key}_DD", [(f"String.StartsWith({lab},{d:02d}/)", U(f"{d:02d}")) for d in range(1, 32)])
    o += var(f"KS_{key}_D", [(f"String.StartsWith({lab},{d:02d}/)", U(d)) for d in range(1, 32)])
    o += var(f"KS_{key}_MM", [(f"String.Contains({lab},/{m:02d}/)", U(f"{m:02d}")) for m in range(1, 13)])
    o += var(f"KS_{key}_Month", [(f"String.Contains({lab},/{m:02d}/)", MONTHS[m - 1]) for m in range(1, 13)])
    o += var(f"KS_{key}_MonS", [(f"String.Contains({lab},/{m:02d}/)", MONTHS[m - 1][:3]) for m in range(1, 13)])
    o += var(f"KS_{key}_Year", [(f"String.EndsWith({lab},/{y})", U(y)) for y in YEARS_ALL])
    o += var(f"KS_{key}_YY", [(f"String.EndsWith({lab},/{y})", U(f"{y % 100:02d}")) for y in YEARS_ALL])
    # Skin settings > the date stamp: camera order 'yy mm dd (default), day first dd mm 'yy, or none
    o += var(f"KS_{key}_Stamp", [(f"String.IsEqual(Skin.String(keepsake.stamp),off)", ""),
                                 (f"{ok} + String.IsEqual(Skin.String(keepsake.stamp),dmy)", f"$VAR[KS_{key}_DD]~$VAR[KS_{key}_MM]~'$VAR[KS_{key}_YY]"),
                                 (ok, f"'$VAR[KS_{key}_YY]~$VAR[KS_{key}_MM]~$VAR[KS_{key}_DD]")])
    o += var(f"KS_{key}_DM", [(ok, f"$VAR[KS_{key}_D] $VAR[KS_{key}_Month]")])
    o += var(f"KS_{key}_Short", [(ok, f"$VAR[KS_{key}_D] $VAR[KS_{key}_MonS] $VAR[KS_{key}_Year]"), (None, f"$INFO[{lab}]")])
    o += var(f"KS_{key}_MonY", [(ok, f"$VAR[KS_{key}_Month] $VAR[KS_{key}_Year]")])
    o += var(f"KS_{key}_MonSY", [(ok, f"$VAR[KS_{key}_MonS] $VAR[KS_{key}_Year]")])
    return o


def month_classes():
    classes = {k: [] for k in range(7)}
    for y in range(Y0, Y1 + 1):
        for m in range(1, 13):
            classes[dt.date(y, m, 1).weekday()].append((y, m))
    return classes


def weekday_vars(key, lab):
    o_exp, o = [], []
    classes = month_classes()
    for k, months in classes.items():
        cond = " | ".join(f"String.Contains({lab},/{m:02d}/{y})" for y, m in months)
        o_exp.append(f'\t<expression name="KS_{key}_MC{k}">{cond}</expression>')
    vals_long, vals_short = [], []
    for w in range(7):
        parts = []
        for k in range(7):
            days = [d for d in range(1, 32) if (k + d - 1) % 7 == w]
            dcond = " | ".join(f"String.StartsWith({lab},{d:02d}/)" for d in days)
            parts.append(f"[$EXP[KS_{key}_MC{k}] + [{dcond}]]")
        cond = " | ".join(parts)
        vals_long.append((cond, WD[w]))
        vals_short.append((cond, WD[w][:3]))
    o += var(f"KS_{key}_Wd", vals_long)
    o += var(f"KS_{key}_WdS", vals_short)
    o += var(f"KS_{key}_Long", [(f"String.Contains({lab},/)", f"$VAR[KS_{key}_Wd] $VAR[KS_{key}_D] $VAR[KS_{key}_Month]")])
    o += var(f"KS_{key}_LongY", [(f"String.Contains({lab},/)", f"$VAR[KS_{key}_Wd] $VAR[KS_{key}_D] $VAR[KS_{key}_Month] $VAR[KS_{key}_Year]")])
    o += var(f"KS_{key}_Gutter", [(f"String.Contains({lab},/)", f"$VAR[KS_{key}_WdS] $VAR[KS_{key}_D]")])
    return o_exp, o


def same_year(a, b, la, lb):
    cond = " | ".join(f"[String.EndsWith({la},/{y}) + String.EndsWith({lb},/{y})]" for y in range(1995, 2036))
    return f'\t<expression name="KS_SameYear_{a}_{b}">{cond}</expression>'


def same_month(a, b, la, lb):
    cond = " | ".join(f"[String.Contains({la},/{m:02d}/{y}) + String.Contains({lb},/{m:02d}/{y})]"
                      for y in range(Y0, Y1 + 1) for m in range(1, 13))
    return f'\t<expression name="KS_SameMonth_{a}_{b}">{cond}</expression>'


def yesterday():
    vals = []
    for m in range(1, 13):
        for d in range(1, 32):
            try:
                day = dt.date(2024, m, d)  # leap year so 29/02 exists
            except ValueError:
                continue
            prev = day - dt.timedelta(days=1)
            if m == 1 and d == 1:
                yv = "$VAR[KS_LastYear]"
            elif m == 3 and d == 1:
                continue  # handled below (leap aware)
            else:
                yv = "$INFO[System.Date(yyyy)]"
            vals.append((f"String.IsEqual(System.Date(dd/mm),{d:02d}/{m:02d})", f"{prev.day:02d}/{prev.month:02d}/{yv}"))
    # 1 March: 29/02 in leap years, else 28/02
    leap = " | ".join(f"String.IsEqual(System.Date(yyyy),{y})" for y in range(2024, 2041) if calendar.isleap(y))
    vals.append((f"String.IsEqual(System.Date(dd/mm),01/03) + [{leap}]", "29/02/$INFO[System.Date(yyyy)]"))
    vals.append(("String.IsEqual(System.Date(dd/mm),01/03)", "28/02/$INFO[System.Date(yyyy)]"))
    o = var("KS_Yesterday", vals)
    o += var("KS_LastYear", [(f"String.IsEqual(System.Date(yyyy),{y})", U(y - 1)) for y in range(2024, 2041)])
    return o


def years_ago(key, lab):
    vals = []
    for cy in range(2026, 2041):
        for ay in range(1995, cy + 1):
            n = cy - ay
            word = "this year" if n == 0 else ("last year" if n == 1 else f"{n} years ago")
            vals.append((f"String.IsEqual(System.Date(yyyy),{cy}) + String.EndsWith({lab},/{ay})", word))
    return var(f"KS_{key}_YearsAgo", vals)


def spoken(key, raw):
    """Time of day from a raw 'yyyy-mm-dd HH:MM:SS' string (Skin Variables detail item)."""
    o = []
    # hour expressions: the hour follows the day's last digit and a space ("...04 04:54:12");
    # a bare "04:" would also match the minutes of 20:04
    for h in range(24):
        cond = " | ".join(f"String.Contains({raw},{d} {h:02d}:)" for d in range(10))
        o.append(f'	<expression name="KS_T_{key}_H{h}">{cond}</expression>')
    hour = lambda h: f"$EXP[KS_T_{key}_H{h}]"
    vals = []
    for h in range(24):
        vals.append((hour(h), f"{h % 12 or 12}:$VAR[KS_T_{key}_MM] {'am' if h < 12 else 'pm'}"))
    o += var(f"KS_T_{key}_Clock", vals)
    o += var(f"KS_T_{key}_HM", [(hour(h), f"{h % 12 or 12}:$VAR[KS_T_{key}_MM]") for h in range(24)])
    o += var(f"KS_T_{key}_MM", [(f"String.Contains({raw},:{mm:02d}:)", U(f"{mm:02d}")) for mm in range(60)])

    def bucket(h):
        return 0 if 4 <= h < 12 else 1 if 12 <= h < 17 else 2 if 17 <= h < 21 else 3 if h >= 21 else 4
    for name, words in (("Part", ["in the morning", "in the afternoon", "in the evening", "at night", "in the small hours"]),
                        ("That", ["that morning", "that afternoon", "that evening", "that night", "in the small hours"]),
                        ("Daypart", ["morning", "afternoon", "evening", "night", "night"])):
        vals = []
        for bkt in range(5):
            hs = [h for h in range(24) if bucket(h) == bkt]
            vals.append((" | ".join(hour(h) for h in hs), words[bkt]))
        o += var(f"KS_T_{key}_{name}", vals)
    # spoken: just after nine / around quarter past nine / around half past nine / around quarter to ten / nearly ten
    def hname(h):
        return "midnight" if h == 0 else "noon" if h == 12 else NUM_WORDS[h % 12]
    o += var(f"KS_T_{key}_HName", [(hour(h), hname(h)) for h in range(24)])
    o += var(f"KS_T_{key}_NName", [(hour(h), hname((h + 1) % 24)) for h in range(24)])
    sp = []
    for lo, hi, phrase in ((0, 14, f"just after $VAR[KS_T_{key}_HName]"), (15, 24, f"around quarter past $VAR[KS_T_{key}_HName]"),
                           (25, 39, f"around half past $VAR[KS_T_{key}_HName]"), (40, 52, f"around quarter to $VAR[KS_T_{key}_NName]"),
                           (53, 59, f"nearly $VAR[KS_T_{key}_NName]")):
        mins = " | ".join(f"String.Contains({raw},:{m:02d}:)" for m in range(lo, hi + 1))
        sp.append((mins, phrase))
    o += var(f"KS_T_{key}_Spoken", sp)
    return o


def resume_minutes():
    """KS_ResumeMin = round(PercentPlayed x Duration(mins) / 100), for list layouts (ListItem.*)."""
    o = []
    top = []
    pct = "ListItem.PercentPlayed"
    dur = "ListItem.Duration(mins)"
    buckets = [(d, d, d) for d in range(1, 61)] + [(d, d - 2, d + 2) for d in range(65, 241, 5)]
    for d, lo, hi in buckets:
        cond = f"Integer.IsEqual({dur},{d})" if lo == hi else f"Integer.IsGreaterOrEqual({dur},{lo}) + Integer.IsLessOrEqual({dur},{hi})"
        top.append((cond, f"$VAR[KS_RM_{d}]"))
        vals = []
        # smallest pct giving each minute value; list from the top so the first match is the largest
        firsts = {}
        for p in range(0, 101):
            m = int(p * d / 100 + 0.5)
            firsts.setdefault(m, p)
        for m in sorted(firsts, reverse=True):
            p = firsts[m]
            if p == 0:
                vals.append((None, U(m)))
            else:
                vals.append((f"Integer.IsGreaterOrEqual({pct},{p})", U(m)))
        o += var(f"KS_RM_{d}", vals)
    return var("KS_ResumeMin", top) + o


def shelf_older(name, da, lp):
    """DA year < LP year: the film sat on the shelf before you watched it ("on the shelf since 2018")."""
    parts = []
    for ly in range(2001, Y1 + 1):
        older = " | ".join(f"String.EndsWith({da},/{dy})" for dy in range(1995, ly))
        parts.append(f"[String.EndsWith({lp},/{ly}) + [{older}]]")
    return f'	<expression name="{name}">{" | ".join(parts)}</expression>'


def day_key(key, lab):
    """yyyy-mm-dd for a smart-playlist value, in two non-numeric halves ("2019-02" + "-04"): a variable value
    that is only digits would be read as a string id."""
    o = var(f"KS_{key}_YM", [(f"String.Contains({lab},/{m:02d}/{y})", f"{y}-{m:02d}") for y in range(2000, 2036) for m in range(1, 13)])
    o += var(f"KS_{key}_PD", [(f"String.StartsWith({lab},{d:02d}/)", f"-{d:02d}") for d in range(1, 32)])
    return o


def diary_slots():
    o = []
    for k in SLOTS:
        lab = f"Container({DIARY}).ListItemNoWrap({k}).LastPlayed"
        key = f"KS_DS{k}".replace("-", "m")
        # what a month divider says: "September" this year, "December 2025" before
        o += var(f"{key}_Disp", [(f"String.Contains({lab},/{m:02d}/) + String.EndsWith({lab},System.Date(yyyy))", MONTHS[m - 1])
                                 for m in range(1, 13)] + [(f"String.Contains({lab},/)", f"$VAR[{key}_MonY]")])
        o += var(f"{key}_MonY", [(f"String.Contains({lab},/{m:02d}/{y})", f"{MONTHS[m - 1]} {y}")
                                                       for y in range(2015, Y1 + 1) for m in range(1, 13)])
    return o


def main():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           "<!-- GENERATED by _src/make_dates.py - date stamps, diary dates, spoken times. Do not edit. -->",
           "<includes>"]
    for key, lab in FIELDS.items():
        out += date_vars(key, lab)
        if key in WEEKDAY_FIELDS:
            exps, vs = weekday_vars(key, lab)
            out += exps + vs
    out.append(same_year("DA", "LP", "ListItem.DateAdded", "ListItem.LastPlayed"))
    out.append(same_month("DA", "LP", "ListItem.DateAdded", "ListItem.LastPlayed"))
    out.append(same_year("CDA", "CLP", "Container.ListItem.DateAdded", "Container.ListItem.LastPlayed"))
    out.append(same_month("CDA", "CLP", "Container.ListItem.DateAdded", "Container.ListItem.LastPlayed"))
    out.append(shelf_older("KS_ShelfOlder", "ListItem.DateAdded", "ListItem.LastPlayed"))
    out.append(shelf_older("KS_CShelfOlder", "Container.ListItem.DateAdded", "Container.ListItem.LastPlayed"))
    out += yesterday()
    out += years_ago("DA", "ListItem.DateAdded")
    out += years_ago("CDA", "Container.ListItem.DateAdded")
    for key, raw in RAW.items():
        out += spoken(key, raw)
    out += day_key("UF", FIELDS["UF"])
    out += resume_minutes()
    out += diary_slots()
    out, dropped = prune(out)
    out += ["</includes>", ""]
    OUT.write_text(finish_xml("\n".join(out)), encoding="utf-8", newline="\n")
    print("wrote", OUT, f"{OUT.stat().st_size // 1024} KB", len(out), "lines;", dropped, "unused variables left out")


def prune(lines):
    """Leave out the variables nothing calls (Team Kodi's kodi-review check flags unused variables). A variable
    is kept when another 1080i file names it ($VAR / $ESCVAR), an expression here does, or a kept variable here
    does. So after using another date variable in a window, re-run this generator."""
    import re
    blocks = {}
    i = 0
    while i < len(lines):
        m = re.match(r'\t<variable name="([^"]+)">$', lines[i])
        if m:
            j = lines.index("\t</variable>", i)
            blocks[m.group(1)] = (i, j)
            i = j + 1
        else:
            i += 1
    ref = re.compile(r"\$(?:ESC)?VAR\[([A-Za-z0-9_]+)")
    used = set()
    for f in OUT.parent.glob("*.xml"):
        if f.name != OUT.name:
            used |= set(ref.findall(f.read_text(encoding="utf-8")))
    inside = {k for a, b in blocks.values() for k in range(a, b + 1)}
    used |= set(ref.findall("\n".join(l for k, l in enumerate(lines) if k not in inside)))
    keep, todo = set(), [n for n in blocks if n in used]
    while todo:
        n = todo.pop()
        if n in keep:
            continue
        keep.add(n)
        a, b = blocks[n]
        todo += [x for x in ref.findall("\n".join(lines[a:b + 1])) if x in blocks and x not in keep]
    drop = {k for n, (a, b) in blocks.items() if n not in keep for k in range(a, b + 1)}
    return [l for k, l in enumerate(lines) if k not in drop], len(blocks) - len(keep)


if __name__ == "__main__":
    main()
