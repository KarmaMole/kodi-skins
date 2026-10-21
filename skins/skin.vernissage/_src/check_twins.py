"""Animation twin scanner (SPEC 16, LESSONS Groove device pass 2 / Sets row + reduce-motion twins).
    python skins/skin.vernissage/_src/check_twins.py

For every <control> (in windows and inside include definitions) it expands the control's own <animation> children
plus its <include>s recursively (params resolved by name only; a load-time include with condition="...reducemotion"
counts as a variant, not a twin) and flags:
  * more than one Hidden animation (Kodi resets only the FIRST of a type when the control shows again: a second one
    that ran stays applied and the control never comes back);
  * more than one Focus / Unfocus / Visible animation whose end state is not identity (fade 100, slide 0,0, zoom 100,
    rotate 0) - the second, non-identity one sticks.
Exit 1 on any finding (build.py fails the build).
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

X = Path(__file__).resolve().parents[1] / "1080i"


def load_includes():
    out = {}
    for f in sorted(X.glob("*.xml")):
        root = ET.fromstring(f.read_bytes())
        if root.tag != "includes":
            continue
        for inc in root.findall("include"):
            if inc.get("name"):
                d = inc.find("definition")
                out[inc.get("name")] = d if d is not None else inc
    return out


def identity(anim):
    effects = anim.findall("effect") or [anim]
    for e in effects:
        t = e.get("type") or e.get("effect")
        end = e.get("end")
        if t == "fade" and end not in (None, "100"):
            return False
        if t == "slide" and end not in (None, "0", "0,0"):
            return False
        if t == "zoom" and end not in (None, "100", "100,100"):
            return False
        if t and t.startswith("rotate") and end not in (None, "0"):
            return False
    return True


def anims_of(ctrl, incs, seen=()):
    out = []
    for ch in ctrl:
        if ch.tag == "animation":
            out.append(ch)
        elif ch.tag == "include":
            cond = ch.get("condition") or ""
            if "reducemotion" in cond and not cond.strip().startswith("!"):
                continue  # the reduce-motion load-time variant (one of the pair loads): not a twin of the normal one
            name = ch.get("content") or (ch.text or "").strip()
            if name in incs and name not in seen:
                out += anims_of(incs[name], incs, seen + (name,))
    return out


def main():
    incs = load_includes()
    bad = []
    for f in sorted(X.glob("*.xml")):
        root = ET.fromstring(f.read_bytes())
        for ctrl in root.iter("control"):
            a = anims_of(ctrl, incs)
            kinds = {}
            for an in a:
                t = (an.get("type") or an.text or "").strip()
                kinds.setdefault(t, []).append(an)
            hid = kinds.get("Hidden", [])
            if len(hid) > 1:
                bad.append(f"{f.name}: control {ctrl.get('id') or ctrl.get('type')}: {len(hid)} Hidden animations")
            for t in ("Focus", "Unfocus", "Visible"):
                lst = kinds.get(t, [])
                if len(lst) > 1 and any(not identity(x) for x in lst[1:]):
                    bad.append(f"{f.name}: control {ctrl.get('id') or ctrl.get('type')}: {len(lst)} {t} animations, a later one ends off identity")
    for b in bad:
        print(b)
    print(f"{len(bad)} twin finding(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
