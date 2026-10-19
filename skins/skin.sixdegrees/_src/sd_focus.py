"""One-off pass (2026-10-19): Majan focused rows -> Six Degrees focused rows (after Daylight's daylight_focus.py).

Majan marks a focused list row with a raised fill + a 4 px accent bar (list_bar_w) or with Dlg_RowFocus
(fill + frame). Six Degrees uses ONE language for every row: an ink rounded fill (sd/rr12.png) with white
text, like the ink pills on the map.

For every <focusedlayout> that has the bar or Dlg_RowFocus:
  - the bar image is removed and the raised fill (colordiffuse="card" common/white.png) becomes the ink fill;
  - every label / textbox and every ink-tinted image (check marks) is split into two copies: the original,
    shown while the list does NOT have focus, and a white copy shown while it does. Both copies carry a
    <selectedcolor> equal to their text colour (lesson 135).
The list id comes from Control.HasFocus(...) in the layout or the closest enclosing list/panel id.

    python _src/sd_focus.py 1080i/*.xml
"""
import re
import sys

CONTAINER = re.compile(r'<control type="(?:list|panel|fixedlist|wraplist)" id="([^"]+)">')
FL = re.compile(r"<focusedlayout[^>]*>.*?</focusedlayout>", re.S)
BAR = re.compile(r'[\t ]*<control type="image">(?:(?!</control>).)*?<width>list_bar_w</width>.*?</control>\n', re.S)
TEXT = re.compile(r'(?P<ind>[\t ]*)<control type="(?P<t>label|textbox)">(?P<body>.*?)</control>', re.S)
INK_IMG = re.compile(r'(?P<ind>[\t ]*)<control type="(?P<t>image)">(?P<body>(?:(?!</control>).)*?<texture[^>]*colordiffuse="ink"[^>]*>(?!common/hairline)[^<]*</texture>(?:(?!</control>).)*?)</control>', re.S)


def split_block(m, on, off):
    ind, t, body = m.group("ind"), m.group("t"), m.group("body")
    vm = re.search(r"\n?[\t ]*<visible>(.*?)</visible>", body)
    orig, base = None, body
    if vm:
        orig, base = vm.group(1), body.replace(vm.group(0), "")
    inner = ind + "\t"

    def vis(c):
        return f"\n{inner}<visible>{'[' + orig + '] + ' if orig else ''}{c}</visible>"

    if t == "image":
        b_on = base.replace('colordiffuse="ink"', 'colordiffuse="white"')
        b_off = base
    else:
        tc = re.search(r"<textcolor>(.*?)</textcolor>", base)
        col = tc.group(1) if tc else "ink"
        b_off = re.sub(r"<selectedcolor>.*?</selectedcolor>", "", base)
        if "<textcolor>" not in b_off:
            b_off = b_off.rstrip() + f"\n{inner}<textcolor>{col}</textcolor>"
        b_off = b_off.rstrip() + f"\n{inner}<selectedcolor>{col}</selectedcolor>"
        b_on = re.sub(r"<textcolor>.*?</textcolor>", "<textcolor>white</textcolor>", b_off)
        b_on = re.sub(r"<selectedcolor>.*?</selectedcolor>", "<selectedcolor>white</selectedcolor>", b_on)
        if "<textcolor>" not in b_on:
            b_on = b_on.rstrip() + f"\n{inner}<textcolor>white</textcolor>"
    a = f'{ind}<control type="{t}">{b_off.rstrip()}{vis(off)}\n{ind}</control>'
    b = f'{ind}<control type="{t}">{b_on.rstrip()}{vis(on)}\n{ind}</control>'
    return a + "\n" + b


def convert(s: str):
    out, pos, n = [], 0, 0
    for m in FL.finditer(s):
        seg = m.group(0)
        if "list_bar_w" not in seg and "Dlg_RowFocus" not in seg:
            continue
        hf = re.search(r"Control\.HasFocus\(([^)]+)\)", seg)
        ids = CONTAINER.findall(s[: m.start()])
        rf = re.search(r'<param name="list_id" value="([^"]+)"', seg)
        if hf:
            lid = hf.group(1)
        elif rf:
            lid = rf.group(1)
        elif ids:
            lid = ids[-1]
        else:
            continue
        on, off = f"Control.HasFocus({lid})", f"!Control.HasFocus({lid})"
        seg2 = BAR.sub("", seg)
        seg2 = seg2.replace('<texture colordiffuse="card">common/white.png</texture>',
                            '<texture border="12" colordiffuse="ink">sd/rr12.png</texture>')
        seg2 = TEXT.sub(lambda mm: split_block(mm, on, off), seg2)
        seg2 = INK_IMG.sub(lambda mm: split_block(mm, on, off), seg2)
        out.append(s[pos: m.start()])
        out.append(seg2)
        pos = m.end()
        n += 1
    out.append(s[pos:])
    return "".join(out), n


def convert_masked(src: str):
    """Comments may mention <focusedlayout>: hide them while converting."""
    comments = []

    def keep(m):
        comments.append(m.group(0))
        return f"@@C{len(comments) - 1}@@"
    masked = re.sub(r"<!--.*?-->", keep, src, flags=re.S)
    res, n = convert(masked)
    res = re.sub(r"@@C(\d+)@@", lambda m: comments[int(m.group(1))], res)
    return res, n


if __name__ == "__main__":
    for path in sys.argv[1:]:
        src = open(path, encoding="utf-8").read()
        res, n = convert_masked(src)
        if n:
            open(path, "w", encoding="utf-8", newline="").write(res)
            print(f"{path}: {n} focused layout(s) converted")
