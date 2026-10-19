"""Kodi draws the labels of a list's SELECTED item in <selectedcolor> (LESSONS, Sentence 0.9.1). Give every label
whose textcolor is set a selectedcolor equal to it, in the given XML files (idempotent).
    python skins/skin.fold/_src/fix_selectedcolor.py Includes_Common.xml Includes_Views_Video.xml ...
"""
import re
import sys
from pathlib import Path

X = Path(__file__).resolve().parents[1] / "1080i"
PAT = re.compile(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)")
for name in sys.argv[1:]:
    p = X / name
    s = p.read_text(encoding="utf-8")
    n = len(PAT.findall(s))
    s = PAT.sub(lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", s)
    p.write_text(s, encoding="utf-8", newline="\n")
    print(f"{name}: {n} labels")
