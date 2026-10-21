"""Room-token lint for Groove (CONVENTIONS.md section 4).   python skins/skin.groove/_src/check_tokens.py

Every colour slot in 1080i must be a room token ($VAR[<token>]), a dynamic value ($INFO / $PARAM / $VAR of another
variable), or one of the static names. dk_* / lt_* colour names may appear only in Includes_Theme.xml.
A bare room-colour name would ignore the Light room, a hex would ignore both. Exit 1 on any finding.
Animation colours (fadediffuse start/end) are not colour slots: Kodi parses them once, they can't follow the room.
"""
from pathlib import Path
import re
import sys

X = Path(__file__).resolve().parents[1] / "1080i"
STATIC = {"white", "black", "clear", "dim_video", "ground_static", "false"} | {f"white_{n}" for n in (10, 20, 30, 40, 45, 55, 65, 70, 80, 90)}
SLOT = re.compile(r"<(textcolor|focusedcolor|disabledcolor|selectedcolor|invalidcolor|shadowcolor|headlinecolor|colordiffuse|backgroundcolor)>([^<]*)<|"
                  r'colordiffuse="([^"]*)"|\[COLOR ([^\]]+)\]')
PARAM = re.compile(r'<param name="[^"]*(?:colou?r|diffuse|tint)[^"]*"(?: value="([^"]*)"\s*/>|>([^<]*)</param>)')


def ok(v):
    v = v.strip()
    return not v or v.startswith("$") or v in STATIC


def main():
    bad = 0
    for f in sorted(X.glob("*.xml")):
        s = f.read_text(encoding="utf-8")
        s = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), s, flags=re.S)  # keep line numbers
        for n, line in enumerate(s.split("\n"), 1):
            for m in SLOT.finditer(line):
                v = next(g for g in m.groups()[1:] if g is not None) if m.group(1) else (m.group(3) if m.group(3) is not None else m.group(4))
                if not ok(v):
                    print(f"{f.name}:{n}: colour '{v}' is not a room token")
                    bad += 1
            for m in PARAM.finditer(line):
                v = m.group(1) if m.group(1) is not None else m.group(2)
                if not ok(v):
                    print(f"{f.name}:{n}: colour param '{v}' is not a room token")
                    bad += 1
            if f.name != "Includes_Theme.xml" and re.search(r"\b(dk|lt)_[a-z_]+\b", line) and not line.strip().startswith("<!--"):
                if re.search(r"[>\"\[ ](dk|lt)_[a-z_]+[<\"\]]", line):
                    print(f"{f.name}:{n}: dk_/lt_ colour used outside Includes_Theme.xml")
                    bad += 1
    print(f"{bad} finding(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
