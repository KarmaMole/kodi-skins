"""Room-token lint (CONVENTIONS 4).   python skins/skin.vernissage/_src/check_tokens.py

Every colour slot in 1080i must be a room token ($VAR[<token>]), a dynamic value ($INFO / $PARAM / $VAR of another
variable), or a static name. Palette names (day_ / eve_ / duskN_ / sN_) may appear:
  * anywhere in Includes_Rooms.xml (the generated engine);
  * elsewhere only as a ROOM TWIN: on a control whose own <visible> gates it to that text set - day_ with
    $EXP[VN_Day], eve_ with $EXP[VN_Dark] - because inside list layouts a colordiffuse $VAR sticks at its build-time
    value (LESSONS Groove M3). dusk / s1-3 names never appear outside Includes_Rooms.xml.
A hex value or a bare token name is always a finding. Also flags $VAR inside an $INFO[...] prefix / postfix (never
expanded, LESSONS Duotone 0.9.11). Animation colours (fadediffuse) are not slots. Exit 1 on any finding.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

X = Path(__file__).resolve().parents[1] / "1080i"
STATIC = {"white", "black", "clear", "wall_static", "track_on_video", "scrim_pause", "scrim_band", "false"} | {
    f"white_{n}" for n in (10, 20, 30, 40, 45, 55, 65, 70, 80, 90)}
SLOTS = {"textcolor", "focusedcolor", "disabledcolor", "selectedcolor", "invalidcolor", "shadowcolor",
         "headlinecolor", "colordiffuse", "backgroundcolor"}
PALETTE = re.compile(r"^(day|eve|dusk\d|s\d)_[a-z_0-9]+$")
PARAM_NAME = re.compile(r"colou?r|diffuse|tint", re.I)
INFO_VAR = re.compile(r"\$INFO\[[^\]]*\$VAR\[")


def gate_of(el, parents):
    """The <visible> text of the nearest <control> at or above el."""
    c = el
    while c is not None and c.tag != "control":
        c = parents.get(c)
    if c is None:
        return ""
    return " ".join((v.text or "") for v in c.findall("visible"))


def check_value(v, el, parents, where, rooms_file):
    v = (v or "").strip()
    if not v or v.startswith("$") or v in STATIC:
        return None
    if PALETTE.match(v):
        if rooms_file:
            return None
        g = gate_of(el, parents)
        if v.startswith("day_") and "$EXP[VN_Day]" in g:
            return None
        if v.startswith("eve_") and "$EXP[VN_Dark]" in g:
            return None
        return f"{where}: palette colour '{v}' outside a room twin (gate the control on $EXP[VN_Day] / $EXP[VN_Dark])"
    return f"{where}: colour '{v}' is not a room token"


def main():
    bad = []
    for f in sorted(X.glob("*.xml")):
        text = f.read_text(encoding="utf-8")
        rooms = f.name == "Includes_Rooms.xml"
        for n, line in enumerate(text.split("\n"), 1):
            if INFO_VAR.search(line):
                bad.append(f"{f.name}:{n}: $VAR inside an $INFO prefix / postfix is never expanded")
        root = ET.fromstring(text.encode("utf-8"))
        parents = {c: p for p in root.iter() for c in p}
        for el in root.iter():
            where = f"{f.name} <{el.tag}>"
            if el.tag in SLOTS:
                r = check_value(el.text, el, parents, where, rooms)
                if r:
                    bad.append(r)
            cd = el.get("colordiffuse")
            if cd is not None:
                r = check_value(cd, el, parents, where, rooms)
                if r:
                    bad.append(r)
            if el.tag == "param" and PARAM_NAME.search(el.get("name", "")):
                r = check_value(el.get("value", el.text), el, parents, where, rooms)
                if r:
                    bad.append(r)
            for txt in (el.text or "", el.get("value") or ""):
                for m in re.finditer(r"\[COLOR ([^\]]+)\]", txt):
                    r = check_value(m.group(1), el, parents, where, rooms)
                    if r:
                        bad.append(r)
    for b in bad:
        print(b)
    print(f"{len(bad)} finding(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
