"""One Hidden animation per include in 1080i/Includes_Animations.xml (reduce-motion stuck-hide fix, 2026-10-21).

    python skins/skin.<id>/_src/collapse_hidden_twins.py          # rewrite (idempotent)
    python skins/skin.<id>/_src/collapse_hidden_twins.py --check  # list includes that still have twins, exit 1

docs/requests/SETS_AND_RM_BRIEF.md, LESSONS "Groove device pass 2": Kodi's CGUIControl::QueueAnimation resets only the
FIRST Hidden animation of a control when it shows again (GetAnimation(type, false) ignores conditions), so the
reduce-motion twin listed second stays applied at fade 0 once it has run: the control never comes back.
Fade-only twins become one unconditional fade (the normal timing; fades stay under reduce motion); twins with motion
(slide / zoom / rotate) keep only the normal one, so reduce motion hides instantly. Visible / Focus / WindowOpen /
WindowClose twins stay: their end states are identity, and WindowClose ends with the window.
Same logic as skins/skin.groove/_src/merge_motion.py collapse_hidden_twins(). Includes_Animations.xml is hand-written
in this skin; this is a pass over it, re-run it after editing the file.
"""
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Animations.xml"
HIDDEN = re.compile(r'[ \t]*<animation type="Hidden"[^>]*>.*?</animation>\n?', re.S)


def blocks(s):
    """Top-level <include name="..."> blocks of an <includes> file: {name: (start, end)}."""
    out, depth = {}, 0
    tok = re.compile(r"<!--.*?-->|<include\b[^>]*?/>|<include\b[^>]*>|</include>", re.S)
    start = name = None
    for m in tok.finditer(s):
        t = m.group(0)
        if t.startswith("<!--") or t.endswith("/>"):
            continue
        if t.startswith("</"):
            depth -= 1
            if depth == 0 and name:
                out[name] = (start, m.end())
                name = None
        else:
            if depth == 0:
                n = re.search(r'name="([^"]+)"', t)
                start, name = m.start(), (n.group(1) if n else None)
            depth += 1
    return out


def twins(text):
    return [n for n, (a, b) in blocks(text).items() if len(HIDDEN.findall(text[a:b])) > 1]


def collapse_hidden_twins(text):
    out, pos = [], 0
    for name, (a, b) in sorted(blocks(text).items(), key=lambda x: x[1][0]):
        block = text[a:b]
        anims = list(HIDDEN.finditer(block))
        if len(anims) > 1:
            first = anims[0].group(0)
            if all(not re.search(r'type="(slide|zoom|rotate[xy]?)"', m.group(0)) for m in anims):
                first = re.sub(r'\s+condition="[^"]*"', "", first, count=1)
            keep = block[:anims[0].start()] + first
            for prev, m in zip(anims, anims[1:]):
                keep += block[prev.end():m.start()]
            block = keep + block[anims[-1].end():]
        out.append(text[pos:a])
        out.append(block)
        pos = b
    out.append(text[pos:])
    return "".join(out)


if __name__ == "__main__":
    text = OUT.read_text(encoding="utf-8")
    if "--check" in sys.argv:
        left = twins(text)
        print("Hidden twins:", ", ".join(left) if left else "none")
        sys.exit(1 if left else 0)
    before = twins(text)
    OUT.write_text(collapse_hidden_twins(text), encoding="utf-8", newline="\n")
    print("collapsed:", ", ".join(before) if before else "nothing to do")
