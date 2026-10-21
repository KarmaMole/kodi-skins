"""Reachability pass (LESSONS Groove QA).   python skins/skin.vernissage/_src/reach.py [--prune]

Roots: every window file in 1080i (anything whose root isn't <includes>), Timers.xml and Defaults.xml. From there it
follows every identifier in the reached text (include names in <include> / content= / include-name params, $VAR /
$EXP names, variables named inside other variables), to a fixpoint. Conservative on purpose: any word equal to a
definition's name counts as a reference.
  default   report unreached include / variable / expression definitions and unreferenced textures; exit 1 if any
  --prune   delete unreached definitions from FORKED files only (the ones fork_from_groove.py marked), and delete
            unreferenced textures under media/fork and the forked engine folders. Generated and hand-written files are
            only reported (fix them at the source). Re-run until it reports nothing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
X = ROOT / "1080i"
MEDIA = ROOT / "media"
FORK_MARK = "Forked from skin.groove 1.0.1 by _src/fork_from_groove.py"
PRUNE_MEDIA = ("fork", "common", "focus", "masks", "markers", "misc", "osd")
TOK = re.compile(r"<!--.*?-->|<(include|variable|expression|constant)\b[^>]*?/>|<(include|variable|expression|constant)\b[^>]*>|</(include|variable|expression|constant)>", re.S)
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")


def definitions():
    """{(kind, name): (file, start, end, body)} for top-level definitions in <includes> files."""
    out = {}
    for f in sorted(X.glob("*.xml")):
        s = f.read_text(encoding="utf-8")
        if not re.search(r"<includes\b", s):
            continue
        depth, start, cur = 0, 0, None
        for m in TOK.finditer(s):
            t = m.group(0)
            if t.startswith("<!--"):
                continue
            kind = m.group(1) or m.group(2) or m.group(3)
            if t.startswith("</"):
                depth -= 1
                if depth == 0 and cur:
                    out[cur] = (f, start, m.end(), s[start:m.end()])
                    cur = None
                continue
            nm = re.search(r'\bname="([^"]+)"', t)
            if depth == 0 and nm and kind in ("include", "variable", "expression") and "file=" not in t:
                if t.endswith("/>"):
                    out[(kind, nm.group(1))] = (f, m.start(), m.end(), t)
                    continue
                cur, start = (kind, nm.group(1)), m.start()
            if not t.endswith("/>"):
                depth += 1
    return out


def strip_comments(s):
    return re.sub(r"<!--.*?-->", " ", s, flags=re.S)


def reach(defs):
    names = {}
    for (k, n) in defs:
        names.setdefault(n, []).append((k, n))
    roots = []
    for f in sorted(X.glob("*.xml")):
        s = f.read_text(encoding="utf-8")
        if not re.search(r"<includes\b", s):
            roots.append(strip_comments(s))
    seen, todo = set(), list(roots)
    while todo:
        text = todo.pop()
        for w in set(WORD.findall(text)):
            for key in names.get(w, ()):
                if key not in seen:
                    seen.add(key)
                    todo.append(strip_comments(defs[key][3]))
    return seen


def texture_refs():
    refs, patterns = set(), []
    for f in list(X.glob("*.xml")):
        s = strip_comments(f.read_text(encoding="utf-8"))
        for m in re.finditer(r"[A-Za-z0-9_$\[\]().,/-]+\.(?:png|jpg|gif)", s):
            p = m.group(0)
            p = p[p.rfind(">") + 1:] if ">" in p else p
            if "$" in p:
                patterns.append(re.compile("^" + re.sub(r"\\\$[A-Z]+\\\[[^\]]*\\\]", ".*", re.escape(p)) + "$"))
            else:
                refs.add(p.lstrip("/"))
    return refs, patterns


def main(prune):
    defs = definitions()
    seen = reach(defs)
    dead = sorted(k for k in defs if k not in seen)
    forked = {f for f in X.glob("*.xml") if FORK_MARK in f.read_text(encoding="utf-8")}
    report_only = [k for k in dead if defs[k][0] not in forked]
    if prune:
        by_file = {}
        for k in dead:
            if defs[k][0] in forked:
                by_file.setdefault(defs[k][0], []).append(defs[k])
        for f, items in by_file.items():
            s = f.read_text(encoding="utf-8")
            for _f, a, b, _body in sorted(items, key=lambda x: -x[1]):
                ls = s.rfind("\n", 0, a) + 1
                if s[ls:a].strip() == "":
                    a = ls
                # drop the comment block right above the definition too (it documents the dead thing)
                pre = s[:a].rstrip(" \t\n")
                if pre.endswith("-->"):
                    c = pre.rfind("<!--")
                    cl = s.rfind("\n", 0, c) + 1
                    if c >= 0 and s[cl:c].strip() == "" and "=====" not in pre[c:] and s[c:a].count("<!--") == 1:
                        a = cl
                e = b + 1 if s[b:b + 1] == "\n" else b
                s = s[:a] + s[e:]
            f.write_text(s, encoding="utf-8", newline="\n")
            print(f"{f.name}: {len(items)} dead definition(s) removed")
    refs, pats = texture_refs()
    unused = []
    for d in PRUNE_MEDIA:
        for p in sorted((MEDIA / d).rglob("*")) if (MEDIA / d).is_dir() else []:
            if not p.is_file():
                continue
            rel = p.relative_to(MEDIA).as_posix()
            if rel in refs or any(pt.match(rel) for pt in pats):
                continue
            unused.append(p)
    if prune:
        for p in unused:
            p.unlink()
        for d in PRUNE_MEDIA:
            for sub in sorted((MEDIA / d).rglob("*"), reverse=True) if (MEDIA / d).is_dir() else []:
                if sub.is_dir() and not any(sub.iterdir()):
                    sub.rmdir()
            if (MEDIA / d).is_dir() and not any((MEDIA / d).iterdir()):
                (MEDIA / d).rmdir()
        print(f"{len(unused)} unreferenced texture(s) deleted")
    else:
        for k in dead:
            print(f"dead {k[0]} {k[1]}  ({defs[k][0].name})")
        for p in unused:
            print(f"unreferenced texture {p.relative_to(MEDIA).as_posix()}")
    if report_only:
        print("not forked (fix at the source):", ", ".join(f"{k[1]} ({defs[k][0].name})" for k in report_only))
    missing = sorted(r for r in refs if r.split("/")[0] in PRUNE_MEDIA + ("vn",) and not (MEDIA / r).exists())
    for r in missing:
        print(f"MISSING texture {r}")
    n = (0 if prune else len(dead) + len(unused)) + len(missing) + (len(report_only) if prune else 0)
    print(f"reach: {len(dead)} dead definition(s), {len(unused)} unreferenced texture(s), {len(missing)} missing")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main("--prune" in sys.argv))
