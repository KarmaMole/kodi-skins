"""Generate 1080i/Includes_Times.xml: Vernissage's clock maths.   python skins/skin.vernissage/_src/make_times.py

Kodi 21 has no arithmetic, so everything that depends on the date, the time or a resume point is a table:

1. Tonight's wall (SPEC 6.2). The pool is unseen films (playcount 0), not started, with a runtime; a DAILY SLICE of it
   (one of 20: year endswith k AND the seconds digit of dateadded even / odd, PROBES P1: 26-77 films each) and the
   RUNTIME BUCKET of the current time (minutes left before midnight: >= 180 any length, 155-179 under 155 min,
   125-154 under 125, below that under 95 min, kept until 5 am). The container ranks by rating (xsp order is ignored,
   LESSONS Daylight 0.9.3), so narrowing the bucket keeps the films that still fit in place.
   The GALLERY DAY runs 5:00 am to 5:00 am: slice = (day of month + (5 in even months)) mod 20, so consecutive days
   (month ends included: 30/31 -> 1, 28 -> 1) never share a slice. Before 5 am the previous day's slice is used
   (exact per-month tables; 1 March before 5 am counts as 28 February, also in leap years).
   Each $VAR value is a whole URL-encoded rule fragment, never a digit-only piece (LESSONS 292).
2. Minutes left from PercentPlayed x Duration(mins) (no resume-time infolabel in Kodi 21, LESSONS Keepsake):
   exact up to 60 min, 5-minute duration buckets to 240 (within ~2 min). "29 min left" / "1 h 41 left".
   One table per infolabel prefix (ListItem for layouts and the library windows, Container(9111).ListItem for
   Home's easel placard, which must read its list while the rail has focus).
3. The helper's exact KarmaMole.MinLeft (easel items) in the same words.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from vnxml import NBSP, x  # noqa: E402

OUT = HERE.parent / "1080i" / "Includes_Times.xml"
NL = "\n"

EARLY = "System.Time(00:00,05:00)"
ODD = "$EXP[Home_MonthOdd]"
MONTH_LEN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
BUCKETS = [  # (System.Time window, runtime limit or None)
    ("05:00", "21:01", None), ("21:01", "21:26", "02:35:00"), ("21:26", "21:56", "02:05:00"), ("21:56", "05:00", "01:35:00")]
SHORT_FROM = "22:35"
S_MIN_LEFT, S_H, S_LEFT = 31480, 31481, 31482


def enc(obj) -> str:
    return urllib.parse.quote(json.dumps(obj, separators=(",", ":")), safe="")


def rule(field, op, value):
    return {"field": field, "operator": op, "value": value}


def slice_of(d: int, m: int) -> int:
    return (d + (5 if m % 2 == 0 else 0)) % 20


def dd_any(days) -> str:
    return "[" + " | ".join(f"Integer.IsEqual(System.Date(dd),{d})" for d in sorted(days)) + "]"


def slice_condition(s: int) -> str:
    odd_after = [d for d in range(1, 32) if slice_of(d, 1) == s]
    even_after = [d for d in range(1, 32) if slice_of(d, 2) == s]
    odd_early = [d for d in range(2, 32) if slice_of(d - 1, 1) == s]
    even_early = [d for d in range(2, 32) if slice_of(d - 1, 2) == s]
    terms = []
    after = []
    if odd_after:
        after.append(f"[{ODD} + {dd_any(odd_after)}]")
    if even_after:
        after.append(f"[!{ODD} + {dd_any(even_after)}]")
    if after:
        terms.append(f"[!{EARLY} + [{' | '.join(after)}]]")
    early = []
    if odd_early:
        early.append(f"[{ODD} + {dd_any(odd_early)}]")
    if even_early:
        early.append(f"[!{ODD} + {dd_any(even_early)}]")
    for m in range(1, 13):           # 1st of the month before 5 am = the last day of the previous month
        pm = 12 if m == 1 else m - 1
        if slice_of(MONTH_LEN[pm], pm) == s:
            early.append(f"[Integer.IsEqual(System.Date(mm),{m}) + Integer.IsEqual(System.Date(dd),1)]")
    if early:
        terms.append(f"[{EARLY} + [{' | '.join(early)}]]")
    return " | ".join(terms)


def check_slices():
    """Every calendar day hangs a slice different from the day before (incl. month and year ends)."""
    import datetime
    d0 = datetime.date(2026, 1, 1)
    prev = None
    for i in range(800):
        d = d0 + datetime.timedelta(days=i)
        s = slice_of(d.day, d.month)
        assert s != prev, f"{d}: same slice as the day before"
        prev = s


def tonight() -> list[str]:
    o = ['\t<!-- ============================================================ Tonight (SPEC 6.2) -->',
         f'\t<expression name="Home_MonthOdd">{" | ".join(f"Integer.IsEqual(System.Date(mm),{m})" for m in (1, 3, 5, 7, 9, 11))}</expression>',
         f'\t<!-- after {SHORT_FROM} the title says "short films" (the under-95 bucket) until 5 am -->',
         f'\t<expression name="Home_TonightShort">System.Time({SHORT_FROM},05:00)</expression>']
    base = [rule("playcount", "is", ["0"]), rule("inprogress", "false", [""]), rule("time", "greaterthan", "00:00:00")]
    head = '{"rules":{"and":[' + ",".join(json.dumps(r, separators=(",", ":")) for r in base)
    tail = ']},"type":"movies"}'
    path = ("videodb://movies/titles/?xsp=" + urllib.parse.quote(head, safe="") + "$VAR[Home_TonightSlice]$VAR[Home_TonightBucket]"
            + urllib.parse.quote(tail, safe=""))
    o.append("\t<!-- the wall's path: base rules + the day's slice + the bucket (ranked by the container: sortby rating) -->")
    o.append('\t<variable name="Home_TonightPath">')
    o.append(f"\t\t<value>{x(path)}</value>")
    o.append("\t</variable>")
    o.append("\t<!-- the gallery day's slice: year endswith k AND dateadded seconds digit even (s < 10) / odd -->")
    o.append('\t<variable name="Home_TonightSlice">')
    for s in range(20):
        k, par = s % 10, s // 10
        digs = ["0", "2", "4", "6", "8"] if par == 0 else ["1", "3", "5", "7", "9"]
        frag = "," + json.dumps(rule("year", "endswith", [str(k)]), separators=(",", ":")) + "," + json.dumps(
            rule("dateadded", "endswith", digs), separators=(",", ":"))
        o.append(f'\t\t<value condition="{slice_condition(s)}">{urllib.parse.quote(frag, safe="")}</value>')
    o.append("\t</variable>")
    o.append("\t<!-- the runtime bucket: minutes left before midnight (screens/Home.md, SPEC 6.2) -->")
    o.append('\t<variable name="Home_TonightBucket">')
    for a, b, limit in BUCKETS:
        if limit:
            frag = "," + json.dumps(rule("time", "lessthan", limit), separators=(",", ":"))
            o.append(f'\t\t<value condition="System.Time({a},{b})">{urllib.parse.quote(frag, safe="")}</value>')
    # any length: a rule that always holds, so the value is never empty
    o.append(f'\t\t<value>{urllib.parse.quote("," + json.dumps(rule("time", "lessthan", "24:00:00"), separators=(",", ":")), safe="")}</value>')
    o.append("\t</variable>")
    return o


def words(left: int) -> str:
    if left < 60:
        return f"{left}{NBSP}$LOCALIZE[{S_MIN_LEFT}]"
    return f"{left // 60}{NBSP}$LOCALIZE[{S_H}] {left % 60:02d}{NBSP}$LOCALIZE[{S_LEFT}]"


def left_table(name: str, prefix: str) -> list[str]:
    """name = minutes left of the item at <prefix> (resumable items; empty otherwise)."""
    pct, dur = f"{prefix}.PercentPlayed", f"{prefix}.Duration(mins)"
    top, subs = [], []
    buckets = [(d, d, d) for d in range(1, 61)] + [(d, d - 2, d + 2) for d in range(65, 241, 5)]
    for d, lo, hi in buckets:
        cond = (f"Integer.IsEqual({dur},{d})" if lo == hi
                else f"Integer.IsGreaterOrEqual({dur},{lo}) + Integer.IsLessOrEqual({dur},{hi})")
        top.append(f'\t\t<value condition="{cond}">$VAR[{name}_{d}]</value>')
        first = {}
        for p in range(0, 101):          # the smallest PercentPlayed giving each minutes-left value
            left = d - int(p * d / 100 + 0.5)
            first.setdefault(left, p)
        sv = [f'\t<variable name="{name}_{d}">']
        for left in sorted(first):        # fewest minutes left (highest percentage) first: the first match wins
            p = first[left]
            sv.append(f'\t\t<value condition="Integer.IsGreaterOrEqual({pct},{p})">{words(left)}</value>' if p
                      else f"\t\t<value>{words(left)}</value>")
        sv.append("\t</variable>")
        subs += sv
    return ([f'\t<variable name="{name}">', f'\t\t<value condition="!{prefix}.IsResumable">'
             "</value>"] + top + ["\t</variable>"] + subs)


def helper_left(name: str, prefix: str) -> list[str]:
    prop = f"{prefix}.Property(KarmaMole.MinLeft)"
    o = [f'\t<variable name="{name}">']
    for n in range(60, 301):
        o.append(f'\t\t<value condition="Integer.IsEqual({prop},{n})">{words(n)}</value>')
    o.append(f'\t\t<value condition="!String.IsEmpty({prop})">$INFO[{prop}]{NBSP}$LOCALIZE[{S_MIN_LEFT}]</value>')
    o.append("\t</variable>")
    return o


def main():
    check_slices()
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         "<!-- GENERATED by _src/make_times.py - edit the generator, then re-run. The clock maths: Tonight's daily slice",
         "     and runtime bucket, minutes left from resume points (see the generator's docstring). -->",
         "<includes>"]
    o += tonight()
    o.append("\t<!-- ============================================================ minutes left -->")
    o += left_table("VN_Left", "ListItem")
    o += left_table("VN_Left9111", "Container(9111).ListItem")
    o += left_table("VN_Left9960", "Container(9960).ListItem")
    o += helper_left("VN_HelperLeft", "ListItem")
    o += helper_left("VN_HelperLeft9110", "Container(9110).ListItem")
    o += helper_left("VN_HelperLeft9120", "Container(9120).ListItem")
    o.append("</includes>")
    o.append("")
    OUT.write_text(NL.join(o), encoding="utf-8", newline=NL)
    print(f"wrote {OUT.name}: {sum(1 for ln in o if '<value' in ln)} values")


if __name__ == "__main__":
    main()
