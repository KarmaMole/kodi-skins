"""Move literal label text into language/resource.language.en_gb/strings.po (kodi-review labels.not-translated).

localize(xml, po_path) returns the XML with every literal <label>, <label2>, <altlabel>, <hinttext> text (and the
fallback="" attribute of those tags) written as $LOCALIZE[id], and <viewtype label=""> as a bare id; the strings are
added to strings.po (an existing identical msgid keeps its id, so re-running a generator writes the same output).
Text counts as literal the way kdk counts it: longer than 2 characters, starting with a letter, with no $INFO / $VAR /
$PARAM / $NUMBER / $ADDON block. Ids are taken from the skin range 31000-31999 (the lowest free one).

Command line (hand-written files): python localize.py <skin> <file.xml> [...]
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

TAGS = ("label", "label2", "altlabel", "hinttext")
BLOCKS = ("$INFO[", "$VAR[", "$PARAM[", "$NUMBER[", "$ADDON[", "$MAP[")
LO, HI, RESERVED = 31000, 31999, {31901}


def literal(text: str) -> bool:
    # "$" anywhere (e.g. $LOCALIZE, $COMMA) stays: a localized string is not parsed for $ blocks again
    return ("$" not in text and len(text) > 2 and not text.endswith(".xml") and text[0].isalpha() and not text.startswith("$")
            and not any(b in text for b in BLOCKS))


def _po_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


def _po_unescape(s: str) -> str:
    return re.sub(r'\\(.)', lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s)


class Po:
    def __init__(self, path: Path):
        self.path = path
        self.raw = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        self.ids: dict[str, int] = {}
        self.used: set[int] = set()
        for m in re.finditer(r'^msgctxt "#(\d+)"\nmsgid "((?:[^"\\]|\\.)*)"', self.raw, re.M):
            i = int(m.group(1))
            self.used.add(i)
            self.ids.setdefault(_po_unescape(m.group(2)), i)
        self.added: list[tuple[int, str]] = []

    def id_for(self, text: str) -> int:
        if text in self.ids:
            return self.ids[text]
        i = next(n for n in range(LO + 300, HI + 1) if n not in self.used and n not in RESERVED)
        self.used.add(i)
        self.ids[text] = i
        self.added.append((i, text))
        return i

    def save(self):
        if not self.added:
            return
        out = self.raw.rstrip("\n") + "\n"
        for i, t in self.added:
            out += f'\nmsgctxt "#{i}"\nmsgid "{_po_escape(t)}"\nmsgstr ""\n'
        self.path.write_text(out, encoding="utf-8", newline="\n")
        self.raw = out
        self.added = []


def localize(xml: str, po: Po) -> str:
    parts = re.split(r"(<!--.*?-->)", xml, flags=re.S)
    return "".join(p if p.startswith("<!--") else _localize(p, po) for p in parts)


def _localize(xml: str, po: Po) -> str:
    def el(m):
        tag, attrs, body = m.group(1), m.group(2) or "", m.group(3)
        text = html.unescape(body)
        if body and literal(text):
            body = f"$LOCALIZE[{po.id_for(text)}]"
        def fb(a):
            t = html.unescape(a.group(1))
            return f'fallback="$LOCALIZE[{po.id_for(t)}]"' if literal(t) else a.group(0)
        attrs = re.sub(r'fallback="([^"]*)"', fb, attrs)
        return f"<{tag}{attrs}>{body}</{tag}>"
    xml = re.sub(r"<(%s)(\s[^<>]*?)?>([^<]*)</\1>" % "|".join(TAGS), el, xml)

    def vt(m):
        t = html.unescape(m.group(2))
        return f'{m.group(1)}"{po.id_for(t)}"' if literal(t) else m.group(0)
    xml = re.sub(r'(<viewtype\b[^>]*?\blabel=)"([^"]*)"', vt, xml)
    return xml


def po_for(xml_path: Path) -> Po:
    return Po(xml_path.resolve().parents[1] / "language" / "resource.language.en_gb" / "strings.po")


if __name__ == "__main__":
    skin = Path(sys.argv[1])
    po = Po(skin / "language" / "resource.language.en_gb" / "strings.po")
    for f in sys.argv[2:]:
        p = skin / "1080i" / f
        s = p.read_bytes().decode("utf-8")
        t = localize(s, po)
        if t != s:
            p.write_bytes(t.encode("utf-8"))
    po.save()
    print("added", len(po.ids), "known strings")
