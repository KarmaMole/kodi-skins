"""Convert Majan-style focused rows (raised fill + thin accent bar) to Daylight's accent fill.

For every <focusedlayout> that contains the list_bar_w accent bar:
  - the bar image is removed,
  - the raised fill becomes the accent fill,
  - each label / textbox / accent-tinted image is split into two copies: the original (shown while
    the list does NOT have focus) and an on-accent copy (shown while it does).
The list id comes from the closest enclosing <control type="list|panel|fixedlist|wraplist" id="N">.
Usage: python _src/daylight_focus.py 1080i/EventLog.xml [...]
"""
import re
import sys

CONTAINER = re.compile(r'<control type="(?:list|panel|fixedlist|wraplist)" id="([^"]+)">')
FL = re.compile(r'<focusedlayout[^>]*>.*?</focusedlayout>', re.S)
BAR = re.compile(r'[\t ]*<control type="image">(?:(?!</control>).)*?<width>list_bar_w</width>.*?</control>\n', re.S)
TEXT = re.compile(r'(?P<ind>[\t ]*)<control type="(?P<t>label|textbox)">(?P<body>.*?)</control>', re.S)
ACC_IMG = re.compile(r'(?P<ind>[\t ]*)<control type="(?P<t>image)">(?P<body>(?:(?!</control>).)*?<texture[^>]*colordiffuse="\$VAR\[DL_(?:Accent|AccentText)\]"[^>]*>(?!daylight/card16)[^<]*</texture>(?:(?!</control>).)*?)</control>', re.S)


def split_block(m, on, off):
    ind, t, body = m.group("ind"), m.group("t"), m.group("body")
    vm = re.search(r"\n[\t ]*<visible>(.*?)</visible>", body)
    orig, base = None, body
    if vm:
        orig, base = vm.group(1), body.replace(vm.group(0), "")
    inner = ind + "\t"

    def vis(c):
        return f"\n{inner}<visible>{'[' + orig + '] + ' if orig else ''}{c}</visible>"

    if t == "image":
        b_on = re.sub(r'colordiffuse="\$VAR\[DL_(?:Accent|AccentText)\]"', 'colordiffuse="$VAR[DL_OnAccent]"', base)
    else:
        b_on = re.sub(r"<textcolor>.*?</textcolor>", "<textcolor>$VAR[DL_OnAccent]</textcolor>", base)
        if "<textcolor>" not in base:
            b_on = base.rstrip() + f"\n{inner}<textcolor>$VAR[DL_OnAccent]</textcolor>"
    a = f'{ind}<control type="{t}">{base.rstrip()}{vis(off)}\n{ind}</control>'
    b = f'{ind}<control type="{t}">{b_on.rstrip()}{vis(on)}\n{ind}</control>'
    return a + "\n" + b


def convert(s: str) -> tuple[str, int]:
    out, pos, n = [], 0, 0
    for m in FL.finditer(s):
        seg = m.group(0)
        if "list_bar_w" not in seg:
            continue
        hf = re.search(r"Control\.HasFocus\(([^)]+)\)", seg)
        ids = CONTAINER.findall(s[: m.start()])
        if hf:
            lid = hf.group(1)
        elif ids:
            lid = ids[-1]
        else:
            continue
        on, off = f"Control.HasFocus({lid})", f"!Control.HasFocus({lid})"
        seg2 = BAR.sub("", seg)
        seg2 = seg2.replace('colordiffuse="$VAR[DL_Raised]">daylight/card16.png', 'colordiffuse="$VAR[DL_Accent]">daylight/card16.png')
        seg2 = TEXT.sub(lambda mm: split_block(mm, on, off), seg2)
        seg2 = ACC_IMG.sub(lambda mm: split_block(mm, on, off), seg2)
        out.append(s[pos: m.start()])
        out.append(seg2)
        pos = m.end()
        n += 1
    out.append(s[pos:])
    return "".join(out), n


if __name__ == "__main__":
    for path in sys.argv[1:]:
        src = open(path, encoding="utf-8").read()
        res, n = convert(src)
        if n:
            open(path, "w", encoding="utf-8", newline="").write(res)
        print(f"{path}: {n} focused layout(s) converted")
