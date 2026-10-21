"""Leave out tags a control repeats from its type's <default> in 1080i/Defaults.xml.

Team Kodi's kodi-review check (kdk, rule xml.redundant) warns about every control tag whose text and attributes
equal the <default type="..."> one. Kodi adds the default only when the control lacks the tag, so dropping an exact
copy renders the same. Generators call strip() on their XML before writing it.

Safe by construction: a tag is dropped only when
  - it is a direct child of a <control type="T"> and holds no child elements,
  - <default type="T"> has exactly one copy of that tag with the same text and the same attributes (no condition),
  - the control has no other copy of the tag, and none of its <include> children (looked up by name in the
    1080i folder; an include with a condition, $PARAM or an unknown name blocks it) sets that tag,
  - the element is alone on its line (so the line can go without touching anything else).
"""
from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

_SKIP = {"include", "control", "content", "itemlayout", "focusedlayout", "animation", "visible", "onclick",
         "onfocus", "onunfocus", "onup", "ondown", "onleft", "onright", "onback", "oninfo", "onload", "onunload",
         "altclick", "description", "param", "definition"}


def _defaults(path: Path) -> dict:
    root = etree.parse(str(path)).getroot()
    out = {}
    for d in root.iter("default"):
        t = d.get("type")
        tags = {}
        for c in d:
            if isinstance(c.tag, str):
                tags.setdefault(c.tag, []).append(c)
        out[t] = {k: v[0] for k, v in tags.items() if len(v) == 1 and len(v[0]) == 0 and "condition" not in v[0].attrib}
    return out


def _same(a, b) -> bool:
    return (a.text or "").strip() == (b.text or "").strip() and dict(a.attrib) == dict(b.attrib)


def _include_tags(folder: Path) -> dict:
    """include name -> set of tags its body puts directly into the control that calls it (None = unknown)."""
    out = {}
    for f in folder.glob("*.xml"):
        try:
            root = etree.parse(str(f)).getroot()
        except etree.XMLSyntaxError:
            continue
        for inc in root.iter("include"):
            name = inc.get("name")
            if not name or inc.getparent() is None or inc.getparent().tag != "includes":
                continue
            body = inc.find("definition")
            body = inc if body is None else body
            tags = set()
            for c in body:
                if not isinstance(c.tag, str) or c.tag == "param":
                    continue
                if c.tag == "include":
                    tags = None
                    break
                tags.add(c.tag)
            out[name] = tags
    return out


def strip(xml: str, defaults_path: Path) -> str:
    defaults = _defaults(defaults_path)
    includes = _include_tags(defaults_path.parent)
    parser = etree.XMLParser(remove_comments=False, resolve_entities=False)
    root = etree.fromstring(xml.encode("utf-8"), parser)
    lines = xml.split("\n")
    drop = set()
    cut = {}
    for ctl in root.iter("control"):
        d = defaults.get(ctl.get("type"))
        if not d:
            continue
        kids = [c for c in ctl if isinstance(c.tag, str)]
        inc_tags = set()
        for c in kids:
            if c.tag != "include":
                continue
            name = (c.get("content") or (c.text or "")).strip()
            tags = includes.get(name)
            if tags is None or c.get("condition") or "$" in name:
                inc_tags = None
                break
            inc_tags |= tags
        if inc_tags is None:
            continue
        for c in kids:
            if c.tag in _SKIP or len(c) or c.tag not in d:
                continue
            if sum(1 for k in kids if k.tag == c.tag) != 1 or c.tag in inc_tags:
                continue
            if not _same(c, d[c.tag]):
                continue
            n = c.sourceline - 1
            if not 0 <= n < len(lines):
                continue
            if re.fullmatch(r"[ \t]*<%s\b[^\n]*?(?:/>|</%s>)[ \t]*\r?" % (c.tag, c.tag), lines[n]) \
                    and lines[n].count("<") <= 2:
                drop.add(n)
                continue
            # one of several elements on the line: cut just this one when it occurs once there
            el = re.compile(r"<%s(?:\s[^<>]*?)?(?:/>|>[^<]*</%s>)" % (c.tag, c.tag))
            found = el.findall(lines[n])
            if len(found) == 1:
                cut[n] = el
    out = []
    for i, l in enumerate(lines):
        if i in drop:
            continue
        if i in cut:
            l = cut[i].sub("", l, count=1)
        out.append(l)
    return "\n".join(out)
