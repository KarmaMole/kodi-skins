"""Generate skins/skin.void/1080i/Includes_Titles.xml: fitted serif titles (no clipping, no running off).

Kodi 21 has no String.Length, but a textbox reports Container(id).NumPages (Duotone's technique, LESSONS
round 3): invisible probe textboxes - same font and width as a tier, height = (lines + 0.5) x pitch -
report NumPages > 1 when the title needs more lines than that tier allows; the next (smaller / more
lines) tier is then shown. The last tier is the fallback and always shows (2 descender-safe lines).

Void serif metrics (make_fonts.py): pitch = 1.04 x size at linespacing 1.0, a text block of n lines is
(n - 1) x pitch + cell, cell = ceil(0.80 x size) + ceil(0.24 x size) (descenders included).

Two kinds of title:
  * grouplist titles (Home, info pages, now playing): `<name>_Visible` goes in a zero-height row (the
    unclipped visible copy), `<name>_Layout` right after it (transparent auto-height copy that pushes
    the rest of the column down by exactly the lines used);
  * placed titles (rotary focus row centred on a y; OSD title anchored on its bottom edge).
Usage:  python skins/skin.void/_src/make_titles.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Titles.xml"


def pitch(s):
    return 1.04 * s


def cell(s):
    return math.ceil(0.80 * s) + math.ceil(0.24 * s)


def block(s, n):
    return (n - 1) * pitch(s) + cell(s)


def room(s):
    """Extra bottom room for a VISIBLE copy. Kodi draws the serif ~0.17 em lower in its box than the 0.80 / 0.24
    metrics say (device, 0.9.3: the 132 / 172 px tiers cut the tails of y / g at box bottom; 64 px fitted in the
    +12). 12 + 0.2 em clears it; the line count per tier is unchanged (height stays < n + 1 lines)."""
    return 12 + math.ceil(0.2 * s)


def below(s):
    """Spacer under a grouplist title (Layout copy): 11 px at 172, scaled with the size."""
    return math.ceil(0.06 * s)


def conds(tiers, i, probe):
    c = [f"Integer.IsGreater(Container($PARAM[{probe}{j}]).NumPages,1)" for j in range(i)]
    if i < len(tiers) - 1:
        c.append(f"!Integer.IsGreater(Container($PARAM[{probe}{i}]).NumPages,1)")
    return " + ".join(c) or "true"


def tb(t, left, top, width, height, size, label, color, visible, tid=None, extra=""):
    idattr = f' id="{tid}"' if tid else ""
    return (f'{t}<control type="textbox"{idattr}>\n{t}\t<left>{left}</left>\n{t}\t<top>{round(top)}</top>\n'
            f'{t}\t<width>{width}</width>\n{t}\t<height>{round(height)}</height>\n{t}\t<font>serif_{size}</font>\n'
            f'{t}\t<textcolor>{color}</textcolor>\n{t}\t<label>{label}</label>\n{t}\t<visible>{visible}</visible>\n'
            f'{extra}{t}</control>')


RECEDE = ('\t\t\t\t<include content="Void_Anim_Recede"><param name="condition" value="$PARAM[recede]"/>'
          '<param name="level" value="84"/></include>\n')


def probes(t, tiers, left, width):
    return "\n".join(tb(t, left, 0, width, (n + 0.5) * pitch(s), s, "$PARAM[label]", "00ffffff", "true",
                        tid=f"$PARAM[p{i}]") for i, (s, n) in enumerate(tiers[:-1]))


def params(tiers, extra=()):
    out = ['\t\t<param name="label"/>', '\t\t<param name="color">text</param>', '\t\t<param name="recede">false</param>']
    out += [f'\t\t<param name="p{i}"/>' for i in range(len(tiers) - 1)]
    out += [f'\t\t<param name="{k}">{v}</param>' for k, v in extra]
    return "\n".join(out)


def grouplist_title(name, desc, left, width, tiers):
    t = "\t\t\t"
    vis = [f"\t<!-- {desc}: tiers {tiers} -->", f'\t<include name="{name}_Visible">', params(tiers), "\t\t<definition>",
           '\t\t\t<control type="group">', f"\t\t\t\t<width>{left + width}</width>", "\t\t\t\t<height>0</height>",
           probes(t + "\t", tiers, left, width)]
    for i, (s, n) in enumerate(tiers):
        vis.append(tb(t + "\t", left, 0, width, block(s, n) + room(s), s, "$PARAM[label]", "$PARAM[color]",
                      conds(tiers, i, "p"), extra=RECEDE))
    vis += ["\t\t\t</control>", "\t\t</definition>", "\t</include>"]
    lay = [f'\t<include name="{name}_Layout">', params(tiers), "\t\t<definition>"]
    for i, (s, n) in enumerate(tiers):
        lay.append(f'\t\t\t<control type="textbox">\n\t\t\t\t<left>{left}</left>\n\t\t\t\t<width>{width}</width>\n'
                   f'\t\t\t\t<height max="{math.floor(n * pitch(s))}">auto</height>\n\t\t\t\t<font>serif_{s}</font>\n'
                   f'\t\t\t\t<textcolor>00000000</textcolor>\n\t\t\t\t<label>$PARAM[label]</label>\n'
                   f'\t\t\t\t<visible>{conds(tiers, i, "p")}</visible>\n\t\t\t</control>')
        # air under the descenders (0.9.4): the line box ends where a y / g tail does, so the next row
        # touched it at 132-172 px. The columns are centred / bottom-anchored, so they re-balance themselves.
        lay.append(f'\t\t\t<control type="group">\n\t\t\t\t<width>{left + width}</width>\n'
                   f'\t\t\t\t<height>{below(s)}</height>\n'
                   f'\t\t\t\t<visible>{conds(tiers, i, "p")}</visible>\n\t\t\t</control>')
    lay += ["\t\t</definition>", "\t</include>"]
    return "\n".join(vis + lay)


def placed_title(name, desc, left, width, tiers, centre=None, bottom=None):
    t = "\t\t\t"
    out = [f"\t<!-- {desc}: tiers {tiers} -->", f'\t<include name="{name}">', params(tiers), "\t\t<definition>",
           probes(t, tiers, left, width)]
    for i, (s, n) in enumerate(tiers):
        h = block(s, n)
        top = centre - h / 2 if centre is not None else bottom - h
        out.append(tb(t, left, top, width, h + room(s), s, "$PARAM[label]", "$PARAM[color]", conds(tiers, i, "p")))
    out += ["\t\t</definition>", "\t</include>"]
    return "\n".join(out)


def main():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_titles.py - edit the generator, not this file. -->",
             "<!-- Probe ids are passed as params p0.. (unique per window). -->", "<includes>",
             grouplist_title("Title_Home", "Home title, x 152, 1616 wide", 152, 1616,
                             [(172, 1), (132, 1), (132, 2), (104, 2)]),
             grouplist_title("Title_Info", "Info page title, x 152, 940 wide", 152, 940,
                             [(120, 2), (96, 2), (72, 2)]),
             grouplist_title("Title_NowPlaying", "Now playing song, x 152, 1100 wide", 152, 1100,
                             [(120, 2), (96, 2), (72, 2)]),
             placed_title("Title_Rotary", "Rotary index focus row, centred on y 544 (0.9.4: 4 px up = air over the next row), x 152, 1110 wide", 152, 1110,
                          [(132, 1), (104, 1), (80, 1), (68, 2)], centre=544),
             placed_title("Title_OSD", "OSD title, bottom edge y 904, x 156, 1600 wide", 156, 1600,
                          [(64, 1), (52, 1), (40, 2)], bottom=904),
             "</includes>", ""]
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
