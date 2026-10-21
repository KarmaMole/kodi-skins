"""Literal label text -> $LOCALIZE[id] from the skin's own strings.po (kdk labels.not-translated).

The words live in language/resource.language.en_gb/strings.po; a label written as literal text whose words
match a skin msgid (31000-31899) is rewritten to $LOCALIZE[id] at generation time, so generators keep readable
English in their tables. Only the words are replaced: $INFO / $VAR / formatting tags and the spaces,
dots and separators around the words stay as written, so the rendered text is identical.

    from localize import localize_xml
    text = localize_xml(text, SKIN / "language" / "resource.language.en_gb" / "strings.po")
"""
from __future__ import annotations

import html
import re
from pathlib import Path

LABEL_TAGS = ("label", "label2", "altlabel", "hinttext")
_ELEM = re.compile(r"<(%s)(\s[^>]*)?>([^<]*)</\1>" % "|".join(LABEL_TAGS))
_FMT = re.compile(r"\[/?(?:B|I|UPPERCASE|LOWERCASE|CAPITALIZE|LIGHT|CR|COLOR(?: [^\]]*)?|TABS(?: [^\]]*)?)\]")
_EXPR_START = re.compile(r"\$(?:INFO|VAR|LOCALIZE|ESCINFO|ESCVAR|ADDON|NUMBER|PARAM|EXP)\[")
SKIN_IDS = range(31000, 31900)


def read_po(path) -> dict[str, int]:
    """msgid -> id for the skin's own ids."""
    t = Path(path).read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'msgctxt "#(\d+)"\nmsgid "((?:[^"\\]|\\.)*)"', t):
        i = int(m.group(1))
        if i in SKIN_IDS:
            mid = m.group(2).replace('\\"', '"').replace("\\\\", "\\")
            out.setdefault(mid, i)
    return out


def split(value: str):
    """Split a label value into [(is_literal, text)] around $EXPR[...] (balanced) and [FORMAT] tags."""
    parts, i, lit = [], 0, []
    while i < len(value):
        m = _EXPR_START.match(value, i)
        if m:
            depth, j = 0, m.end() - 1
            while j < len(value):
                if value[j] == "[":
                    depth += 1
                elif value[j] == "]":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if lit:
                parts.append((True, "".join(lit)))
                lit = []
            parts.append((False, value[i:j + 1]))
            i = j + 1
            continue
        m = _FMT.match(value, i)
        if m:
            if lit:
                parts.append((True, "".join(lit)))
                lit = []
            parts.append((False, m.group(0)))
            i = m.end()
            continue
        lit.append(value[i])
        i += 1
    if lit:
        parts.append((True, "".join(lit)))
    return parts


def cores(value: str):
    """The word runs of a label value: (prefix, core, suffix) per literal part with letters."""
    for is_lit, text in split(value):
        if not is_lit:
            continue
        m = re.match(r"^(\s*)(.*?)(\s*)$", text, re.S)
        core = m.group(2)
        if sum(c.isalpha() for c in core) >= 2:
            yield core


def localize_value(value: str, ids: dict[str, int]) -> str:
    out = []
    for is_lit, text in split(value):
        if is_lit:
            m = re.match(r"^(\s*)(.*?)(\s*)$", text, re.S)
            core = html.unescape(m.group(2))
            if core in ids and sum(c.isalpha() for c in core) >= 2:
                text = f"{m.group(1)}$LOCALIZE[{ids[core]}]{m.group(3)}"
        out.append(text)
    return "".join(out)


def localize_xml(text: str, po_path) -> str:
    ids = read_po(po_path)

    def sub(m):
        return f"<{m.group(1)}{m.group(2) or ''}>{localize_value(m.group(3), ids)}</{m.group(1)}>"

    text = _ELEM.sub(sub, text)

    def vt(m):
        word = html.unescape(m.group(2))
        return f'{m.group(1)}"{ids[word]}"' if word in ids else m.group(0)

    # <viewtype label="The wall">: a numeric label is localized (Container.Viewmode still reads the words)
    return re.sub(r'(<viewtype[^>]*label=)"([^"]*[A-Za-z][^"]*)"', vt, text)


def add_strings(po_path, words) -> dict[str, int]:
    """Append msgids that are missing (next free skin ids). Returns msgid -> id for all of them."""
    p = Path(po_path)
    t = p.read_text(encoding="utf-8")
    ids = read_po(p)
    used = {int(x) for x in re.findall(r'msgctxt "#(\d+)"', t)}
    top = max([i for i in used if i in SKIN_IDS] or [31000])
    free = iter(range(top + 1, SKIN_IDS.stop))
    add = []
    for w in words:
        if w in ids:
            continue
        i = next(free)
        ids[w] = i
        esc = w.replace("\\", "\\\\").replace('"', '\\"')
        add.append(f'msgctxt "#{i}"\nmsgid "{esc}"\nmsgstr ""\n')
    if add:
        block = "\n".join(add) + "\n"
        k = t.find('msgctxt "#319')
        if k != -1:  # keep the fontset names (31900+) last
            t = t[:k] + block + t[k:]
        else:
            if not t.endswith("\n"):
                t += "\n"
            if not t.endswith("\n\n"):
                t += "\n"
            t += block
        p.write_text(t, encoding="utf-8", newline="\n")
    return ids
