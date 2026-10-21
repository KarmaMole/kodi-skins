"""Merge motion-designer's draft into 1080i/Includes_Animations.xml.   python skins/skin.groove/_src/merge_motion.py

Source: docs/skin.groove/Includes_Animations.draft.xml (MOTION.md). The forked Nocturne animation includes stay for the
forked windows; where a name exists in both, the DRAFT wins (Groove's motion is the authority). Depth-aware: whole
top-level <include name> blocks are swapped (LESSONS: never splice XML with naive substring replaces).
Re-run whenever the draft changes. Once motion-designer owns the file outright, delete this script.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT.parents[1] / "docs" / "skin.groove" / "Includes_Animations.draft.xml"
OUT = ROOT / "1080i" / "Includes_Animations.xml"
MARK = "\t<!-- ===== MOTION DRAFT (merged by _src/merge_motion.py; edit MOTION.md's draft, then re-run) ===== -->"


def blocks(s):
    """Top-level <include name="..."> blocks of an <includes> file: {name: (start, end)}."""
    out, depth, i = {}, 0, 0
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


# Draft includes no window calls (yet): kept in the draft as motion-designer's library (MOTION.md), left out of the
# shipped file because the official review (kdk includes.unused) reports every include nothing calls. Take a name
# off this list when a window starts using it.
NOT_SHIPPED = {
    "Anim_OSDVisible", "Anim_GlideSlot", "Anim_FocusShadow", "Anim_FocusIcon", "Anim_FocusLabel",
    "Anim_HomeStageOpen", "Anim_RecordSpin", "Anim_RecordSpinStop", "Anim_VizCurtain", "Anim_StackLift",
    "Anim_BusySpin",
}


HIDDEN = re.compile(r'[ \t]*<animation type="Hidden"[^>]*>.*?</animation>\n?', re.S)


def collapse_hidden_twins(text):
    """Device pass 2 (2026-10-21): one Hidden animation per include, never a reduce-motion twin.
    Kodi's CGUIControl::QueueAnimation resets only the FIRST Hidden animation of a control when it shows again
    (GetAnimation(type, false) ignores conditions), so a second Hidden twin that ran (reduce motion on) stays applied
    at fade 0: the control never comes back (rail labels vanished for good). Fade-only twins become one unconditional
    fade (fades stay under reduce motion); twins with motion keep only the normal one (reduce motion: instant hide)."""
    out, pos = [], 0
    for name, (a, b) in sorted(blocks(text).items(), key=lambda x: x[1][0]):
        block = text[a:b]
        anims = list(HIDDEN.finditer(block))
        if len(anims) > 1:
            first = anims[0].group(0)
            if all('type="slide"' not in m.group(0) and 'type="zoom"' not in m.group(0) and 'type="rotate' not in m.group(0)
                   for m in anims):
                first = re.sub(r'\s+condition="[^"]*"', "", first, count=1)
            keep = block[:anims[0].start()] + first
            for prev, m in zip(anims, anims[1:]):
                keep += block[prev.end():m.start()]
            block = keep + block[anims[-1].end():]
        out.append(text[pos:a]); out.append(block); pos = b
    out.append(text[pos:])
    return "".join(out)


def main():
    base = OUT.read_text(encoding="utf-8")
    if MARK in base:
        base = base[:base.index(MARK)].rstrip() + "\n</includes>\n"
    draft = DRAFT.read_text(encoding="utf-8")
    db = {n: span for n, span in blocks(draft).items() if n not in NOT_SHIPPED}
    bb = blocks(base)
    # drop forked blocks the draft replaces (from the end so offsets stay valid)
    for name, (a, b) in sorted(((n, bb[n]) for n in db if n in bb), key=lambda x: -x[1][0]):
        base = base[:a] + f"<!-- {name}: replaced by the motion draft below -->" + base[b:]
    body = "\n\n".join("\t" + draft[a:b] for a, b in sorted(db.values()))
    base = base.rstrip()
    assert base.endswith("</includes>")
    base = base[: -len("</includes>")].rstrip() + "\n\n" + MARK + "\n" + body + "\n</includes>\n"
    base = collapse_hidden_twins(base)  # forked blocks too (Anim_FadeVisible)
    OUT.write_text(base, encoding="utf-8", newline="\n")
    print(f"merged {len(db)} draft includes ({sum(1 for n in db if n in bb)} replaced forked ones)")


if __name__ == "__main__":
    main()
