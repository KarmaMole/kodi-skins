"""Drop control tags that repeat the skin's <default type="..."> (kdk xml.redundant) from generated XML.

Kodi appends the default's tags to every control of that type that lacks them (CGUIIncludes::SetDefaults, and
the FIRST copy of a tag wins), so a control's own copy that equals the default changes nothing. Removed only
when the tag is a direct child of the control, appears once there, the control has no <include> child (an
include could bring a second copy) and the default holds it unconditionally. Formatting is kept: the tag and
the whitespace before it go; a line left empty goes too.

    from strip_defaults import strip_defaults
    text = strip_defaults(text, SKIN / "1080i" / "Defaults.xml")
"""
from __future__ import annotations

import re
from pathlib import Path

STYLE_TAGS = {
    "font", "textcolor", "focusedcolor", "disabledcolor", "selectedcolor", "shadowcolor", "invalidcolor",
    "align", "aligny", "textoffsetx", "textoffsety", "texturefocus", "texturenofocus", "lefttexture",
    "righttexture", "midtexture", "overlaytexture", "texturebg", "itemgap", "pulseonselect", "aspectratio",
    "scroll", "scrollspeed", "orientation",
}
_TAG = re.compile(r"<(/?)([A-Za-z_][\w.-]*)((?:\s+[\w:-]+\s*=\s*\"[^\"]*\")*)\s*(/?)>|<!--.*?-->", re.S)
_ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
_cache: dict[str, dict] = {}


def _key(attrs: str, text: str):
    return (tuple(sorted(_ATTR.findall(attrs or ""))), (text or "").strip())


def load_defaults(path) -> dict:
    path = str(path)
    if path in _cache:
        return _cache[path]
    t = Path(path).read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'<default type="(\w+)">(.*?)</default>', t, re.S):
        body = re.sub(r"<!--.*?-->", "", m.group(2), flags=re.S)
        if "<include" in body:
            continue
        tags = {}
        for e in re.finditer(r"<([\w]+)((?:\s+[\w:-]+\s*=\s*\"[^\"]*\")*)\s*(?:/>|>([^<]*)</\1>)", body):
            name, attrs, text = e.group(1), e.group(2), e.group(3)
            if "condition" in (attrs or ""):
                continue
            tags.setdefault(name, []).append(_key(attrs, text))
        out[m.group(1)] = {k: v[0] for k, v in tags.items() if len(v) == 1}
    _cache[path] = out
    return out


def strip_defaults(text: str, defaults_path) -> str:
    defaults = load_defaults(defaults_path)
    # stack of open elements: [name, ctype, children(list of (name, start, end, attrs, inner)), has_include]
    stack = []
    removals = []  # (start, end)
    for m in _TAG.finditer(text):
        if m.group(0).startswith("<!--"):
            continue
        closing, name, attrs, selfclose = m.group(1) == "/", m.group(2), m.group(3), m.group(4) == "/"
        if name.startswith("?"):
            continue
        if closing:
            el = stack.pop()
            if el[0] != name:
                raise ValueError(f"unbalanced </{name}> near {m.start()}")
            if el[0] == "control" and el[1] in defaults and not el[3]:
                d = defaults[el[1]]
                counts = {}
                for ch in el[2]:
                    counts[ch[0]] = counts.get(ch[0], 0) + 1
                for ch in el[2]:
                    cname, cs, ce, cattrs, cinner = ch
                    if cname in STYLE_TAGS and counts[cname] == 1 and cname in d and cinner is not None \
                            and "$PARAM" not in cinner and _key(cattrs, cinner) == d[cname]:
                        removals.append((cs, ce))
            # register this element as a child of its parent
            if stack:
                inner = text[el[4]:m.start()] if "<" not in text[el[4]:m.start()] else None
                stack[-1][2].append((name, el[5], m.end(), el[6], inner))
            continue
        ctype = re.search(r'type="(\w+)"', attrs or "")
        if selfclose:
            if stack:
                if name == "include":
                    stack[-1][3] = True
                stack[-1][2].append((name, m.start(), m.end(), attrs, ""))
            continue
        if name == "include" and stack:
            stack[-1][3] = True
        stack.append([name, ctype.group(1) if (name == "control" and ctype) else None, [], False, m.end(), m.start(), attrs])
    if stack:
        raise ValueError("unbalanced document")
    if not removals:
        return text
    out = []
    last = 0
    for s, e in sorted(removals):
        # take the whitespace before the tag on the same line with it
        ws = s
        while ws > last and text[ws - 1] in " \t":
            ws -= 1
        out.append(text[last:ws])
        last = e
    out.append(text[last:])
    res = "".join(out)
    return _drop_emptied_lines(text, res)


def _drop_emptied_lines(before: str, after: str) -> str:
    """Remove whitespace-only lines in `after` that were not whitespace-only in `before` (line-by-line diff)."""
    import difflib
    a = before.split("\n")
    b = after.split("\n")
    keep = []
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            keep += b[j1:j2]
        else:
            keep += [ln for ln in b[j1:j2] if ln.strip()]
    return "\n".join(keep)
