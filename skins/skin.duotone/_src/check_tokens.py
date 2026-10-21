"""Look-token lint for Duotone (docs/skin.duotone/CONVENTIONS.md section 4).   python skins/skin.duotone/_src/check_tokens.py

Every colour slot in 1080i (textcolor & co, colordiffuse tag / attribute, [COLOR x], colour-ish include params,
variable values that are colour names) must be a look token ($VAR[<token>]), a section variable, a dynamic value
($INFO / $PARAM / $VAR of another variable) or one of the static names (white, black, clear, ground_static).
co_* / lt_* / dk_* names may appear only in Includes_Theme.xml. A bare palette name or a hex would ignore the Look.
Also reports look tokens nothing uses (they need a NO_VARIABLE entry in make_theme.py, kdk variables.unused)
and $VAR[...] names that are neither tokens nor defined variables, and [COLOR $VAR[..]] inside an $INFO prefix
(never expanded there). Exit 1 on any finding.
"""
import re
import sys

from theme_tokens import SLOT, STATIC, XML, palette, tokens

PARAM = re.compile(r'<param name="([^"]*)"(?: value="([^"]*)"\s*/>|>([^<]*)</param>)')
VALUE = re.compile(r"<value(?: condition=\"[^\"]*\")?>([^<]*)</value>")
COLOURISH = re.compile(r"colou?r|diffuse|tint|chip|text$")


def ok(v):
    v = v.strip()
    return not v or v.startswith("$") or v in STATIC


def main():
    pal = palette()
    toks = set(tokens())
    bare = {n for n in pal if n not in STATIC} | {"vermilion", "cobalt", "acid", "paper", "ink"} | toks
    bad = 0
    used = set()
    defined_vars = set()
    var_refs = []
    for f in sorted(XML.glob("*.xml")):
        s = f.read_text(encoding="utf-8")
        s = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), s, flags=re.S)  # keep line numbers
        defined_vars |= set(re.findall(r'<variable name="([^"]+)"', s))
        for n, line in enumerate(s.split("\n"), 1):
            for m in re.finditer(r"\$(?:ESC)?VAR\[([A-Za-z_0-9.]+)\]", line):
                used.add(m.group(1))
                var_refs.append((f.name, n, m.group(1)))
            for m in SLOT.finditer(line):
                v = m.group(2) if m.group(1) else (m.group(3) if m.group(3) is not None else m.group(4))
                if not ok(v):
                    print(f"{f.name}:{n}: colour '{v}' is not a look token")
                    bad += 1
            for m in PARAM.finditer(line):
                v = m.group(2) if m.group(2) is not None else m.group(3)
                if v.strip() in (bare | set(pal)) - STATIC or (COLOURISH.search(m.group(1)) and re.fullmatch(r"[0-9a-fA-F]{8}", v.strip())):
                    print(f"{f.name}:{n}: colour param '{m.group(1)}={v}' is not a look token")
                    bad += 1
            for m in VALUE.finditer(line):
                v = m.group(1).strip()
                if f.name != "Includes_Theme.xml" and (v in bare or re.fullmatch(r"[0-9a-fA-F]{8}", v)):
                    print(f"{f.name}:{n}: variable value '{v}' is a bare colour")
                    bad += 1
            if re.search(r"\$INFO\[[^\]\[]*,[^\]]*\[COLOR \$VAR", line):
                # Kodi keeps an $INFO prefix / postfix literal: a $VAR there is never expanded
                print(f"{f.name}:{n}: [COLOR $VAR[...]] inside an $INFO[...] prefix / postfix: move it outside")
                bad += 1
            if f.name != "Includes_Theme.xml" and re.search(r"[>\"\[ ](co|lt|dk)_[a-z_0-9]+[<\"\]]", line):
                print(f"{f.name}:{n}: co_/lt_/dk_ colour used outside Includes_Theme.xml")
                bad += 1
    for fn, n, name in var_refs:
        if name not in defined_vars:
            print(f"{fn}:{n}: $VAR[{name}] is not defined")
            bad += 1
    from make_theme import NO_VARIABLE
    for t in sorted(toks - NO_VARIABLE):
        if t not in used:
            print(f"token '{t}' is never used: add it to NO_VARIABLE in make_theme.py")
            bad += 1
    print(f"{bad} finding(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
