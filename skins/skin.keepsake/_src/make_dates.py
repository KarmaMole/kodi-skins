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

Month-first regions (0.9.17, ported from Fold 0.9.12 / Passe-partout 0.9.21): USA prints MM/DD/YYYY ("Added 4 2020").
Each date label is read month-first ($EXP[KS_MF_<label>]) when its middle field is over 12 (only possible as a day),
or its first field is 12 or less AND the region's long date puts the month before the day: Home.xml / Startup.xml
onload store $INFO[System.Date(MMMM D)] ("October 25") in Window(Home).Property(keepsake.monthday), and
String.Contains(System.Date,<that property>) is true for "Sunday, October 25, 2026", false for "Sunday, 25 October 2026"
($EXP[KS_RegionMonthFirst]). On the 2nd and the 20th "20 July 2026" also contains "July 20" / "July 2" (the start
of "July 2026"), so the test also needs the long date NOT to contain $INFO[System.Date(MMMM YYYY)]
(Window(Home).Property(keepsake.monthyear)): "July 2026" is only there when the day comes first. Month-first, day = String.Contains(<d>,/DD/), month = String.StartsWith(<d>,MM/).
KS_Yesterday and $EXP[KS_Today_<F>] follow the region's order.

Usage: python skins/skin.keepsake/_src/make_dates.py
"""
from __future__ import annotations

import calendar
import datetime as dt
import re
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
# "today" tests used by hand-written includes ($EXP[KS_Today_<key>])
TODAY = {
    "LP": "ListItem.LastPlayed",
    "CLP": "Container.ListItem.LastPlayed",
    "EP": "Container(9130).ListItem.LastPlayed",  # Home: you're on
}
MD = "Window(Home).Property(keepsake.monthday)"
MY = "Window(Home).Property(keepsake.monthyear)"
RMF = "$EXP[KS_RegionMonthFirst]"
NUM_WORDS = "midnight one two three four five six seven eight nine ten eleven noon".split()


def U(s) -> str:
    """Digit-only labels are read as string ids (LESSONS 2): wrap them."""
    return f"[UPPERCASE]{s}[/UPPERCASE]"


_MF = {}  # date label -> name of its "read month-first" expression


def mf(lab) -> str:
    """$EXP[...] that is true when this date label is month-first (see the docstring)."""
    if lab not in _MF:
        _MF[lab] = "KS_MF_" + re.sub(r"[^A-Za-z0-9]+", "_", lab.replace("(-", "(m")).strip("_")  # ListItemNoWrap(-1) -> m1
    return f"$EXP[{_MF[lab]}]"


def mf_expressions():
    o = [f'\t<expression name="KS_RegionMonthFirst">!String.IsEmpty({MD}) + String.Contains(System.Date,{MD}) + !String.Contains(System.Date,{MY})</expression>']
    for lab, name in _MF.items():
        first_big = " | ".join(f"String.StartsWith({lab},{d}/)" for d in range(13, 32))
        mid_big = " | ".join(f"String.Contains({lab},/{d}/)" for d in range(13, 32))
        o.append(f'\t<expression name="{name}">[{mid_big}] | [{RMF} + ![{first_big}]]</expression>')
    return o


# the day / month tests of a dd/mm/yyyy (df) and of a mm/dd/yyyy (mf) label
def dfd(lab, d): return f"String.StartsWith({lab},{d:02d}/)"
def mfd(lab, d): return f"String.Contains({lab},/{d:02d}/)"
def dfm(lab, m): return f"String.Contains({lab},/{m:02d}/)"
def mfm(lab, m): return f"String.StartsWith({lab},{m:02d}/)"
def dfmy(lab, m, y): return f"String.Contains({lab},/{m:02d}/{y})"
def mfmy(lab, m, y): return f"String.StartsWith({lab},{m:02d}/) + String.EndsWith({lab},/{y})"


def split(name, lab, make, tail=()):
    """A variable for both orders: <name> tests the label's order once and hands over to <name>_F (month-first)
    or <name>_DF (day-first). make(day_test, month_test, month_year_test) -> [(cond, value)]; tail = values
    added to both lists."""
    return (var(name, [(mf(lab), f"$VAR[{name}_F]"), (None, f"$VAR[{name}_DF]")])
            + var(f"{name}_F", make(mfd, mfm, mfmy) + list(tail))
            + var(f"{name}_DF", make(dfd, dfm, dfmy) + list(tail)))


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
    o += split(f"KS_{key}_DD", lab, lambda D, M, MY: [(D(lab, d), U(f"{d:02d}")) for d in range(1, 32)])
    o += split(f"KS_{key}_D", lab, lambda D, M, MY: [(D(lab, d), U(d)) for d in range(1, 32)])
    o += split(f"KS_{key}_MM", lab, lambda D, M, MY: [(M(lab, m), U(f"{m:02d}")) for m in range(1, 13)])
    o += split(f"KS_{key}_Month", lab, lambda D, M, MY: [(M(lab, m), MONTHS[m - 1]) for m in range(1, 13)])
    o += split(f"KS_{key}_MonS", lab, lambda D, M, MY: [(M(lab, m), MONTHS[m - 1][:3]) for m in range(1, 13)])
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
        # month-first: grouped by year (the year is at the end in both orders)
        by_year = {}
        for y, m in months:
            by_year.setdefault(y, []).append(m)
        cond = " | ".join(f"[String.EndsWith({lab},/{y}) + [{' | '.join(mfm(lab, m) for m in ms)}]]" for y, ms in by_year.items())
        o_exp.append(f'\t<expression name="KS_{key}_MCF{k}">{cond}</expression>')
    def weekdays(short):
        def make(D, M, MY):
            cls = "MCF" if D is mfd else "MC"
            vals = []
            for w in range(7):
                parts = []
                for k in range(7):
                    dcond = " | ".join(D(lab, d) for d in range(1, 32) if (k + d - 1) % 7 == w)
                    parts.append(f"[$EXP[KS_{key}_{cls}{k}] + [{dcond}]]")
                vals.append((" | ".join(parts), WD[w][:3] if short else WD[w]))
            return vals
        return make
    o += split(f"KS_{key}_Wd", lab, weekdays(False))
    o += split(f"KS_{key}_WdS", lab, weekdays(True))
    o += var(f"KS_{key}_Long", [(f"String.Contains({lab},/)", f"$VAR[KS_{key}_Wd] $VAR[KS_{key}_D] $VAR[KS_{key}_Month]")])
    o += var(f"KS_{key}_LongY", [(f"String.Contains({lab},/)", f"$VAR[KS_{key}_Wd] $VAR[KS_{key}_D] $VAR[KS_{key}_Month] $VAR[KS_{key}_Year]")])
    o += var(f"KS_{key}_Gutter", [(f"String.Contains({lab},/)", f"$VAR[KS_{key}_WdS] $VAR[KS_{key}_D]")])
    return o_exp, o


def same_year(a, b, la, lb):
    cond = " | ".join(f"[String.EndsWith({la},/{y}) + String.EndsWith({lb},/{y})]" for y in range(1995, 2036))
    return f'\t<expression name="KS_SameYear_{a}_{b}">{cond}</expression>'


def same_month(a, b, la, lb):
    """Same year (KS_SameYear_<a>_<b>) and same month; each label read in its own order."""
    combos = []
    for ga, ma in ((mf(la), mfm), (f"!{mf(la)}", dfm)):
        for gb, mb in ((mf(lb), mfm), (f"!{mf(lb)}", dfm)):
            months = " | ".join(f"[{ma(la, m)} + {mb(lb, m)}]" for m in range(1, 13))
            combos.append(f"[{ga} + {gb} + [{months}]]")
    return f'\t<expression name="KS_SameMonth_{a}_{b}">$EXP[KS_SameYear_{a}_{b}] + [{" | ".join(combos)}]</expression>'


def yesterday():
    """Yesterday in the region's short-date order: mm/dd/yyyy when the region is month-first (listed first)."""
    vals = []
    for region, order in ((RMF + " + ", lambda d, m: f"{m:02d}/{d:02d}"), ("", lambda d, m: f"{d:02d}/{m:02d}")):
        vals += _yesterday(region, order)
    o = var("KS_Yesterday", vals)
    o += var("KS_LastYear", [(f"String.IsEqual(System.Date(yyyy),{y})", U(y - 1)) for y in range(2024, 2041)])
    return o


def _yesterday(region, order):
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
            vals.append((f"{region}String.IsEqual(System.Date(dd/mm),{d:02d}/{m:02d})", f"{order(prev.day, prev.month)}/{yv}"))
    # 1 March: 29/02 in leap years, else 28/02
    leap = " | ".join(f"String.IsEqual(System.Date(yyyy),{y})" for y in range(2024, 2041) if calendar.isleap(y))
    vals.append((f"{region}String.IsEqual(System.Date(dd/mm),01/03) + [{leap}]", f"{order(29, 2)}/$INFO[System.Date(yyyy)]"))
    vals.append((f"{region}String.IsEqual(System.Date(dd/mm),01/03)", f"{order(28, 2)}/$INFO[System.Date(yyyy)]"))
    return vals


def today(key, lab):
    return (f'\t<expression name="KS_Today_{key}">[!{RMF} + String.IsEqual({lab},System.Date(dd/mm/yyyy))]'
            f' | [{RMF} + String.IsEqual({lab},System.Date(mm/dd/yyyy))]</expression>')


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
    o = split(f"KS_{key}_YM", lab, lambda D, M, MY: [(MY(lab, m, y), f"{y}-{m:02d}") for y in range(2000, 2036) for m in range(1, 13)])
    o += split(f"KS_{key}_PD", lab, lambda D, M, MY: [(D(lab, d), f"-{d:02d}") for d in range(1, 32)])
    return o


def diary_slots():
    o = []
    for k in SLOTS:
        lab = f"Container({DIARY}).ListItemNoWrap({k}).LastPlayed"
        key = f"KS_DS{k}".replace("-", "m")
        # what a month divider says: "September" this year, "December 2025" before
        o += split(f"{key}_Disp", lab, lambda D, M, MY: [(f"{M(lab, m)} + String.EndsWith({lab},System.Date(yyyy))", MONTHS[m - 1])
                                                         for m in range(1, 13)],
                   tail=[(f"String.Contains({lab},/)", f"$VAR[{key}_MonY]")])
        # "December 2025": the month name and the year (2015 on: the box's history starts 2015)
        years = " | ".join(f"String.EndsWith({lab},/{y})" for y in range(2015, Y1 + 1))
        o += var(f"{key}_MonY", [(f"[{years}]", f"$VAR[{key}_Mo] $VAR[{key}_Yr]")])
        o += split(f"{key}_Mo", lab, lambda D, M, MY: [(M(lab, m), MONTHS[m - 1]) for m in range(1, 13)])
        o += var(f"{key}_Yr", [(f"String.EndsWith({lab},/{y})", U(y)) for y in range(2015, Y1 + 1)])
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
    out += [today(k, lab) for k, lab in TODAY.items()]
    out += years_ago("DA", "ListItem.DateAdded")
    out += years_ago("CDA", "Container.ListItem.DateAdded")
    for key, raw in RAW.items():
        out += spoken(key, raw)
    out += day_key("UF", FIELDS["UF"])
    out += resume_minutes()
    out += diary_slots()
    out[3:3] = mf_expressions()  # after the header; needs every label seen above
    out, dropped = prune(out)
    out += ["</includes>", ""]
    OUT.write_text(finish_xml("\n".join(out)), encoding="utf-8", newline="\n")
    print("wrote", OUT, f"{OUT.stat().st_size // 1024} KB", len(out), "lines;", dropped, "unused variables / expressions left out")


def prune(lines):
    """Leave out the variables nothing calls (Team Kodi's kodi-review check flags unused variables). A variable
    is kept when another 1080i file names it ($VAR / $ESCVAR), an expression here does, or a kept variable here
    does. So after using another date variable in a window, re-run this generator."""
    blocks = {}
    i = 0
    while i < len(lines):
        m = re.match(r'\t<variable name="([^"]+)">$', lines[i])
        e = re.match(r'\t<expression name="([^"]+)">', lines[i])
        if e:
            blocks["EXP:" + e.group(1)] = (i, i)
            i += 1
        elif m:
            j = lines.index("\t</variable>", i)
            blocks[m.group(1)] = (i, j)
            i = j + 1
        else:
            i += 1
    rx = re.compile(r"\$(?:ESC)?(VAR|EXP)\[([A-Za-z0-9_]+)")

    class ref:  # names found in a text; expressions as "EXP:<name>"
        @staticmethod
        def findall(t):
            return [("EXP:" if k == "EXP" else "") + n for k, n in rx.findall(t)]
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
