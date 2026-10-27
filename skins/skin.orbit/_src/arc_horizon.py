"""0.9.16 Horizon arcs (docs/VIEWS_BRIEF_2026-10-27.md), used by make_arc.py.

The library arc (view 500) runs down the right edge on a circle centred off-screen right. The HORIZON runs along
the bottom of the screen on a flat circle centred far below it, so wide pictures (fanart, stills, landscape art)
and album covers / artist portraits can ride the dial too: Left / Right turn it, the lens sits at the top of the
circle in the middle of the screen, the neighbours lean with the circle and dim with distance. Same mechanics as
every Orbit arc (poster_arc: one-frame OnNext / OnPrevious pulse, Conditional slide + zoom + rotate from the
neighbour's pose, fadediffuse brightness), only the geometry and the focus-owning list's orientation differ.
"""
import math


def horizon_slots(cx, cy, R, W, ratio, extra_w, gap=26, rotmax=30.0):
    """k -> (x, y, w, h, kodi_rot) for k in -5..5 on a circle centred (cx, cy) below the screen.
    W = widths for |k| = 0..4 (lens first), ratio = height / width. Neighbours are spaced along the circle by half
    of each width + gap (cards are turned to the tangent, so width is their extent along the arc)."""
    Ws = list(W) + [extra_w]
    c = [0.0]
    for k in range(1, 6):
        c.append(c[k - 1] + (Ws[k - 1] + Ws[k]) / 2 + gap)
    slots = {}
    for k in range(-5, 6):
        a = abs(k)
        th = (1 if k > 0 else -1 if k < 0 else 0) * c[a] / R
        w = Ws[a]
        h = round(w * ratio)
        x = cx + R * math.sin(th)
        y = cy - R * math.cos(th)
        # Kodi: positive rotation = counter-clockwise; right of the lens the card leans clockwise
        rot = max(-rotmax, min(rotmax, -th * 180 / math.pi))
        slots[k] = (x, y, w, h, rot)
    return slots


def wide_art_variables(prefix, cid):
    """Art for the video horizon: an episode's own still (never a generated image://video@ frame grab, which
    often never loads), else landscape, fanart, the show's fanart / landscape, thumb, icon."""
    L = []
    for k in range(-5, 6):
        nm = f"{prefix}_{'m' if k < 0 else 'p'}{abs(k)}"
        li = f"Container({cid}).ListItemNoWrap({k})"
        L.append(f'\t<variable name="{nm}">')
        L.append(f'\t\t<value condition="String.IsEqual({li}.DBType,episode) + !String.IsEmpty({li}.Art(thumb)) + '
                 f'!String.StartsWith({li}.Art(thumb),image://video@)">$INFO[{li}.Art(thumb)]</value>')
        for art in ("Art(landscape)", "Art(fanart)", "Art(tvshow.fanart)", "Art(tvshow.landscape)"):
            L.append(f'\t\t<value condition="!String.IsEmpty({li}.{art})">$INFO[{li}.{art}]</value>')
        L.append(f'\t\t<value condition="!String.StartsWith({li}.Art(thumb),image://video@)">$INFO[{li}.Art(thumb)]</value>')
        L.append("\t</variable>")
    return L


def hidden_list_h(name, desc, art="ListItem.Art(fanart)"):
    """The focus-owning list for a horizon: 11 x 1 px items side by side, lens at item 5; art drawn invisibly so
    Kodi loads it (LESSONS 2)."""
    return [f"\t<!-- {desc} -->",
            f'\t<include name="{name}">',
            "\t\t<orientation>horizontal</orientation>",
            "\t\t<width>11</width>",
            "\t\t<height>1</height>",
            "\t\t<focusposition>5</focusposition>",
            "\t\t<movement>0</movement>",
            "\t\t<scrolltime>0</scrolltime>",
            "\t\t<preloaditems>2</preloaditems>",
            '\t\t<itemlayout width="1" height="1">',
            '\t\t\t<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height>'
            f'<texture background="true" colordiffuse="01ffffff">$INFO[{art}]</texture></control>',
            "\t\t</itemlayout>",
            '\t\t<focusedlayout width="1" height="1">',
            '\t\t\t<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height>'
            f'<texture background="true" colordiffuse="01ffffff">$INFO[{art}]</texture></control>',
            "\t\t</focusedlayout>",
            "\t</include>", ""]


# lens at (960, 706); flat enough that the neighbours stay clear of the option bar (y 1000)
HORIZON = dict(cx=960, cy=3106, R=2400, W=[480, 300, 236, 196, 168], ratio=9 / 16, extra_w=150)
HORIZON_SQ = dict(cx=960, cy=3060, R=2400, W=[330, 210, 168, 140, 118], ratio=1.0, extra_w=104)
