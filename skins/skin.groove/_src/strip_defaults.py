"""Drop control tags that only repeat 1080i/Defaults.xml.   python skins/skin.groove/_src/strip_defaults.py [files...]

The official review (kdk xml.redundant) warns about a tag written on a control when the control type's <default>
already sets the same value. Kodi (CGUIIncludes::SetDefaults) appends every default tag to the end of each control
of that type, and the control reads the FIRST copy of a single-value tag, so removing an own tag that equals the
default changes nothing on screen.

Used by the generators (make_skinsettings.py, make_timemachine.py, make_wheel.py) on their output, and once by hand
over the hand-written windows (pass file paths). Conservative on purpose, mirroring kdk:
  - only leaf tags that are direct children of a <control type="X">, where Defaults.xml has a <default type="X">
    with a tag of the same name, text and attributes (whitespace-normalised);
  - only when the control has exactly one such tag (a second copy, conditional or not, keeps both);
  - when the control has direct <include> children, only for tags none of those includes can bring (their top-level
    tags, nested includes followed; an include named by a $PARAM counts as bringing anything), because an included
    copy would come before the default and win;
  - never inside include definitions (<includes> files): a param could make the value differ per call.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "1080i" / "Defaults.xml"

_TOKEN = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|</?[A-Za-z][^>]*?/?>", re.S)
_ATTR = re.compile(r'([\w:.-]+)\s*=\s*"([^"]*)"')


def _norm(tag, attrs, text):
    return (tag.lower(), tuple(sorted(_ATTR.findall(attrs or ""))), (text or "").strip())


def load_defaults(path=DEFAULTS):
    """{control type: {tag: normalised (tag, attrs, text)}} from the top-level <default> blocks."""
    s = Path(path).read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'<default\s+type="([^"]+)"\s*>(.*?)</default>', s, re.S):
        tags = {}
        body = re.sub(r"<!--.*?-->", "", m.group(2), flags=re.S)
        for t in re.finditer(r"<(\w+)((?:\s+[^>]*?)?)\s*(?:/>|>([^<]*)</\1>)", body):
            tags[t.group(1).lower()] = _norm(t.group(1), t.group(2), t.group(3))
        out[m.group(1)] = tags
    return out


def load_includes(folder=ROOT / "1080i"):
    """{include name: body text} for every <include name="..."> definition in the skin (the <definition> part when
    the include has params)."""
    out = {}
    for f in sorted(Path(folder).glob("*.xml")):
        s = f.read_text(encoding="utf-8")
        if not re.search(r"<includes\b", s):
            continue
        depth, start, name = 0, 0, None
        for m in re.finditer(r"<!--.*?-->|<include\b[^>]*?/>|<include\b[^>]*>|</include>", s, re.S):
            t = m.group(0)
            if t.startswith("<!--") or t.endswith("/>"):
                continue
            if t.startswith("</"):
                depth -= 1
                if depth == 0 and name:
                    body = s[start:m.start()]
                    d = re.search(r"<definition>(.*)</definition>", body, re.S)
                    out[name] = d.group(1) if d else body
                    name = None
            else:
                if depth == 0:
                    n = re.search(r'name="([^"]+)"', t)
                    name, start = (n.group(1) if n else None), m.end()
                depth += 1
    return out


ANY = "*"


def include_tags(name, includes, seen=frozenset()):
    """Top-level tag names an include brings into the control that calls it (ANY when unknown)."""
    if "$" in name or name not in includes:
        return {ANY}
    if name in seen:
        return set()
    out, depth = set(), 0
    body = includes[name]
    for m in _TOKEN.finditer(body):
        tok = m.group(0)
        if tok.startswith(("<!--", "<![CDATA[", "<?")):
            continue
        tag = re.match(r"</?([A-Za-z][\w:.-]*)", tok).group(1)
        if tok.startswith("</"):
            depth -= 1
            continue
        if depth == 0:
            if tag == "include":
                c = re.search(r'content="([^"]+)"', tok)
                inner = c.group(1) if c else body[m.end():body.find("</include>", m.end())].strip()
                out |= include_tags(inner, includes, seen | {name})
            else:
                out.add(tag.lower())
        if not tok.endswith("/>"):
            depth += 1
    return out


def strip(text, defaults=None, includes=None):
    """Return (text without the redundant tags, number removed)."""
    defaults = load_defaults() if defaults is None else defaults
    includes = load_includes() if includes is None else includes
    if re.search(r"<includes\b", text):
        return text, 0
    # frames: [tag, control type or None, {tag: [spans]}, set of tags the control's direct includes bring]
    stack, drops = [], []
    tokens = list(_TOKEN.finditer(text))
    i = 0
    while i < len(tokens):
        m = tokens[i]
        tok = m.group(0)
        i += 1
        if tok.startswith(("<!--", "<![CDATA[", "<?")):
            continue
        name = re.match(r"</?([A-Za-z][\w:.-]*)", tok).group(1)
        if tok.startswith("</"):
            frame = stack.pop()
            assert frame[0] == name, (frame[0], name, m.start())
            if frame[1] and ANY not in frame[3]:
                dflt = defaults.get(frame[1], {})
                for tag, found in frame[2].items():
                    if len(found) == 1 and tag in dflt and found[0][1] == dflt[tag] and tag not in frame[3]:
                        drops.append(found[0][0])
            continue
        parent = stack[-1] if stack else None
        attrs = tok[len(name) + 1:].rstrip("/>").rstrip()
        selfclose = tok.endswith("/>")
        if parent is not None and parent[1] is not None and name == "include":
            c = re.search(r'content="([^"]+)"', tok)
            if c:
                inc = c.group(1)
            elif selfclose:
                inc = "$"   # <include/> with no name: unknown
            else:
                inc = text[m.end():text.find("<", m.end())].strip()
            parent[3] |= include_tags(inc, includes)
        if selfclose:
            if parent is not None and parent[1] is not None:
                parent[2].setdefault(name.lower(), []).append(((m.start(), m.end()), _norm(name, attrs, "")))
            continue
        # a leaf element written as <tag ...>text</tag>?
        nxt = tokens[i] if i < len(tokens) else None
        if (nxt is not None and nxt.group(0) == f"</{name}>" and "<" not in text[m.end():nxt.start()]
                and parent is not None and parent[1] is not None):
            parent[2].setdefault(name.lower(), []).append(
                ((m.start(), nxt.end()), _norm(name, attrs, text[m.end():nxt.start()])))
            i += 1
            continue
        ctype = None
        if name == "control":
            t = re.search(r'\btype="([^"]+)"', tok)
            ctype = t.group(1) if t else None
        stack.append([name, ctype, {}, set()])
    assert not stack, [f[0] for f in stack]
    # remove whole lines (indent + tag + newline) when the tag is alone on its line, else just the tag
    out, last, n = [], 0, 0
    for a, b in sorted(drops):
        ls = text.rfind("\n", 0, a) + 1
        le = text.find("\n", b)
        le = len(text) if le < 0 else le
        if text[ls:a].strip() == "" and text[b:le].strip() == "":
            a, b = ls, min(le + 1, len(text))
        out.append(text[last:a])
        last = b
        n += 1
    out.append(text[last:])
    return "".join(out), n


def main(paths):
    defaults, includes = load_defaults(), load_includes()
    total = 0
    for p in map(Path, paths):
        s = p.read_text(encoding="utf-8")
        new, n = strip(s, defaults, includes)
        if n:
            p.write_text(new, encoding="utf-8", newline="\n")
            print(f"{p.name}: {n} tag(s) that repeat Defaults.xml removed")
        total += n
    print(f"total {total}")


if __name__ == "__main__":
    main(sys.argv[1:])
