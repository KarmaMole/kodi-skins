"""Groove icon set: in-house thin line icons, 64x64 grid, 2 px stroke, round caps/joins, white on transparent.

Every icon is SVG path data on a 64 grid (live area 8..56). The same source renders:
  - inline SVG in the mockup boards (make_boards.py),
  - icons.png (the review sheet),
  - later, the skin's media/icons/*.png at 64 and 96 px (stroke scales with the icon: 2 px at 64, 3 px at 96).

This is the SKIN's copy (skins/skin.groove/_src/icons.py), read by make_textures.py. It is the approved set from
docs/skin.groove/mockups/_src/icons.py plus the extra HDR badges (badge-hdr10, badge-dv, badge-hlg) and the architect's engine icons (chevron-right,
chevron-down, back, audio, subtitles, chapters, info, forward, rewind) at the end of ICONS.
Edit icons here; the mockup copy is a snapshot of what Omar approved.
"""
from __future__ import annotations

import math

SW = 2.0  # stroke width at 64 px


def arc(cx, cy, r, a0, a1):
    """SVG arc from angle a0 to a1 (degrees, 0 = 3 o'clock, positive = clockwise on screen)."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    sweep = 1 if a1 > a0 else 0
    large = 1 if abs(a1 - a0) > 180 else 0
    return f"M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} {sweep} {x1:.2f} {y1:.2f}"


def pt(cx, cy, r, a):
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


def arrowhead(x, y, ang, size=6):
    """Open chevron arrowhead pointing along ang (degrees) with its tip at x, y."""
    a = math.radians(ang)
    l = (x - size * math.cos(a - 0.7), y - size * math.sin(a - 0.7))
    r = (x - size * math.cos(a + 0.7), y - size * math.sin(a + 0.7))
    return f"M{l[0]:.2f} {l[1]:.2f} L{x:.2f} {y:.2f} L{r[0]:.2f} {r[1]:.2f}"


def gear():
    pts = []
    n = 8
    for i in range(n):
        base = i * 360 / n
        for da, rr in ((-13, 17), (-8, 23), (8, 23), (13, 17)):
            pts.append(pt(32, 32, rr, base + da))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    return f'<path d="{d}"/><circle cx="32" cy="32" r="7"/>'


def star(cx=32, cy=33, ro=22, ri=9.5):
    pts = [pt(cx, cy, ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]
    return '<path d="M' + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + ' Z"/>'


def ticks(cx, cy, r0, r1, angs):
    out = []
    for a in angs:
        x0, y0 = pt(cx, cy, r0, a)
        x1, y1 = pt(cx, cy, r1, a)
        out.append(f"M{x0:.2f} {y0:.2f} L{x1:.2f} {y1:.2f}")
    return " ".join(out)


DOT = 'fill="#fff" stroke="none"'

ICONS: dict[str, str] = {
    # ---- rail
    "music": f'<circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="7"/><circle cx="32" cy="32" r="1.6" {DOT}/>'
             f'<path d="{arc(32, 32, 17, -150, -100)}"/><path d="{arc(32, 32, 17, 30, 80)}"/>',
    "films": '<rect x="10" y="12" width="44" height="40" rx="3"/><path d="M19 12 V52 M45 12 V52 M10 22 H19 M10 32 H19 M10 42 H19 M45 22 H54 M45 32 H54 M45 42 H54"/>',
    "tv": '<rect x="8" y="13" width="48" height="33" rx="4"/><path d="M24 54 H40 M32 46 V54"/>',
    "search": '<circle cx="28" cy="28" r="15"/><path d="M39 39 L53 53"/>',
    "settings": gear(),
    # ---- transport
    "previous": '<path d="M17 16 V48"/><path d="M47 16 L23 32 L47 48 Z"/>',
    "play": '<path d="M22 14 L50 32 L22 50 Z"/>',
    "pause": '<path d="M24 16 V48 M40 16 V48"/>',
    "next": '<path d="M47 16 V48"/><path d="M17 16 L41 32 L17 48 Z"/>',
    "stop": '<rect x="18" y="18" width="28" height="28" rx="2"/>',
    "shuffle": '<path d="M9 21 H19 C31 21 33 43 45 43 H54 M9 43 H19 C31 43 33 21 45 21 H54"/>'
               + f'<path d="{arrowhead(54, 21, 0)} {arrowhead(54, 43, 0)}"/>',
    "repeat": '<path d="M13 35 V29 C13 24 17 20 22 20 H51 M51 29 V35 C51 40 47 44 42 44 H13"/>'
              + f'<path d="{arrowhead(51, 20, 0)} {arrowhead(13, 44, 180)}"/>',
    "repeat-one": '<path d="M13 35 V29 C13 24 17 20 22 20 H51 M51 29 V35 C51 40 47 44 42 44 H13"/>'
                  + f'<path d="{arrowhead(51, 20, 0)} {arrowhead(13, 44, 180)}"/><path d="M29 29 L33 26.5 V38"/>',
    # ---- groove
    "upnext": '<rect x="8" y="26" width="28" height="28" rx="2"/><path d="M16 26 V18 H44 V46 H36 M24 18 V10 H52 V38 H44"/>',
    "liner": '<path d="M32 17 C26 13 17 12 8 14 V50 C17 48 26 49 32 53 C38 49 47 48 56 50 V14 C47 12 38 13 32 17 Z M32 17 V53"/>'
             '<path d="M14 24 H26 M14 31 H26 M14 38 H23 M38 24 H50 M38 31 H50 M38 38 H47"/>',
    "visualiser": '<path d="M10 28 V36 M18 22 V42 M26 12 V52 M34 20 V44 M42 26 V38 M50 18 V46"/>',
    "record": f'<circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="16"/><circle cx="32" cy="32" r="6"/><circle cx="32" cy="32" r="1.6" {DOT}/>',
    "watchvideo": '<rect x="8" y="12" width="48" height="34" rx="4"/><path d="M27 22 L40 29 L27 36 Z M22 54 H42"/>',
    "timemachine": f'<path d="{arc(32, 40, 23, 180, 360)} M7 40 H57"/>'
                   + f'<path d="{ticks(32, 40, 17, 23, [200, 225, 250, 270, 290, 315, 340])}"/>'
                   + f'<path d="M32 40 L{pt(32, 40, 16, 235)[0]:.2f} {pt(32, 40, 16, 235)[1]:.2f}"/><circle cx="32" cy="40" r="2" {DOT}/>',
    "wheel": f'<circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="11"/>'
             + f'<path d="{ticks(32, 32, 11, 24, [i * 45 + 22.5 for i in range(8)])}"/>'
             + f'<path d="{arc(32, 32, 17.5, -22.5 + 6, 22.5 - 6)}" stroke-width="4"/>',
    "pickup": '<rect x="8" y="18" width="28" height="28" rx="2"/><path d="M48 10 V27 M48 37 V54"/>'
              + f'<path d="{arrowhead(48, 10, -90)} {arrowhead(48, 54, 90)}"/>',
    # ---- library
    "albums": f'<rect x="8" y="12" width="34" height="40" rx="2"/><path d="{arc(40, 32, 17, -83.25, 83.25)}"/>',
    "artists": '<circle cx="32" cy="22" r="10"/><path d="M12 54 C12 42 21 35 32 35 C43 35 52 42 52 54"/>',
    "songs": '<path d="M24 46 V15 L50 10 V40"/><circle cx="18" cy="46" r="6"/><circle cx="44" cy="40" r="6"/>',
    "options": f'<circle cx="16" cy="32" r="3" {DOT}/><circle cx="32" cy="32" r="3" {DOT}/><circle cx="48" cy="32" r="3" {DOT}/>',
    "view": '<rect x="10" y="10" width="18" height="18" rx="2"/><rect x="36" y="10" width="18" height="18" rx="2"/>'
            '<rect x="10" y="36" width="18" height="18" rx="2"/><rect x="36" y="36" width="18" height="18" rx="2"/>',
    "sort": '<path d="M10 18 H36 M10 32 H30 M10 46 H22 M48 14 V50"/>' + f'<path d="{arrowhead(48, 50, 90)}"/>',
    "filter": '<path d="M10 14 H54 L37 33 V51 L27 46 V33 Z"/>',
    "update": f'<path d="{arc(32, 32, 20, 200, 330)} {arc(32, 32, 20, 20, 150)}"/>'
              + f'<path d="{arrowhead(*pt(32, 32, 20, 330), 60)} {arrowhead(*pt(32, 32, 20, 150), 240)}"/>',
    "clean": '<path d="M36 8 L31 28"/><path d="M20 28 H42 L48 54 H14 Z"/><path d="M23 40 L21 54 M31 40 V54 M39 40 L41 54"/>',
    "playall": '<path d="M10 16 L26 26 L10 36 Z"/><path d="M34 20 H54 M34 32 H54 M10 46 H54"/>',
    # ---- info
    "runtime": '<circle cx="32" cy="32" r="22"/><path d="M32 18 V32 L42 38"/>',
    "rating": star(),
    "badge-4k": '<rect x="4" y="16" width="56" height="32" rx="5"/><path d="M23 23 L15 37 H28 M24 29 V42 M35 23 V42 M47 23 L35 34 M39 31 L48 42"/>',
    "badge-hdr": '<rect x="2" y="16" width="60" height="32" rx="5"/><path d="M10 23 V41 M21 23 V41 M10 32 H21 M28 23 V41 H31 A9 9 0 0 0 31 23 Z M45 41 V23 H50 A5 5 0 0 1 50 33 H45 M50 33 L56 41"/>',
    "resume": f'<path d="{arc(32, 32, 22, -90, 200)}"/>' + f'<path d="{arrowhead(*pt(32, 32, 22, 200), 290)}"/><path d="M27 22 L42 32 L27 42 Z"/>',
    "trailer": '<rect x="8" y="14" width="48" height="36" rx="3"/><path d="M8 22 H56 M8 42 H56 M16 14 V22 M26 14 V22 M38 14 V22 M48 14 V22 M16 42 V50 M26 42 V50 M38 42 V50 M48 42 V50"/>'
               '<path d="M28 27 L37 32 L28 37 Z"/>',
    "episodes": '<rect x="8" y="10" width="18" height="12" rx="2"/><rect x="8" y="26" width="18" height="12" rx="2"/><rect x="8" y="42" width="18" height="12" rx="2"/>'
                '<path d="M32 16 H56 M32 32 H56 M32 48 H50"/>',
    "more": '<circle cx="32" cy="32" r="22"/><path d="M32 22 V42 M22 32 H42"/>',
    # ---- settings row
    "skin": '<path d="M32 8 C18 8 8 18 8 31 C8 44 18 54 30 54 C34 54 35 51 33 48 C31 45 33 42 37 42 H44 C51 42 56 37 56 30 C56 17 45 8 32 8 Z"/>'
            f'<circle cx="20" cy="30" r="3.2" {DOT}/><circle cx="26" cy="19" r="3.2" {DOT}/><circle cx="38" cy="18" r="3.2" {DOT}/><circle cx="46" cy="27" r="3.2" {DOT}/>',
    "system": '<path d="M10 18 H18 M26 18 H54 M10 32 H38 M46 32 H54 M10 46 H24 M32 46 H54"/><circle cx="22" cy="18" r="4"/><circle cx="42" cy="32" r="4"/><circle cx="28" cy="46" r="4"/>',
    "addons": '<path d="M32 8 L54 20 V44 L32 56 L10 44 V20 Z M10 20 L32 32 L54 20 M32 32 V56"/>',
    "files": '<path d="M8 16 H26 L31 22 H56 V50 H8 Z M8 28 H56"/>',
    "pictures": '<rect x="8" y="12" width="48" height="40" rx="3"/><path d="M8 44 L23 30 L35 42 L43 35 L56 46"/><circle cx="43" cy="23" r="4"/>',
    "favourites": '<path d="M32 52 C20 43 8 35 8 23 C8 16 13 11 20 11 C26 11 30 15 32 19 C34 15 38 11 44 11 C51 11 56 16 56 23 C56 35 44 43 32 52 Z"/>',
    "livetv": '<rect x="8" y="20" width="48" height="32" rx="4"/><path d="M22 8 L32 18 L42 8"/><circle cx="47" cy="30" r="1.6" fill="#fff" stroke="none"/>',
    "power": f'<path d="{arc(32, 35, 19, -55, 235)} M32 10 V32"/>',
    # ---- extra badges (same 32 px frame as badge-4k / badge-hdr; mapped from ListItem.HdrType with a $VAR)
    "badge-hdr10": '<rect x="2" y="16" width="60" height="32" rx="5"/><path d="M8 23 V41 M15 23 V41 M8 32 H15 M19 23 V41 H22 A6 9 0 0 0 22 23 Z'
                   ' M31 41 V23 H34 A4 4.5 0 0 1 34 32 H31 M34 32 L38 41 M42 26 L45 23 V41 M53 23 A4 9 0 0 1 53 41 A4 9 0 0 1 53 23"/>',
    "badge-dv": '<rect x="4" y="16" width="56" height="32" rx="5"/><path d="M17 23 V41 H21 A9 9 0 0 0 21 23 Z M35 23 L41 41 L47 23"/>',
    "badge-hlg": '<rect x="2" y="16" width="60" height="32" rx="5"/><path d="M10 23 V41 M18 23 V41 M10 32 H18 M24 23 V41 H31"/>'
                 + f'<path d="{arc(45, 32, 9, 30, 320)} M46 32 H54 V36"/>',
    # ---- engine icons the architect requested (replace the Nocturne placeholders from make_placeholders.py)
    "chevron-right": '<path d="M24 14 L42 32 L24 50"/>',
    "chevron-down": '<path d="M14 24 L32 42 L50 24"/>',
    "back": '<path d="M52 32 H13 M28 17 L13 32 L28 47"/>',
    "audio": '<path d="M9 25 H19 L31 15 V49 L19 39 H9 Z"/>' + f'<path d="{arc(31, 32, 11, -45, 45)} {arc(31, 32, 20, -50, 50)}"/>',
    "subtitles": '<rect x="8" y="14" width="48" height="36" rx="3"/><path d="M16 35 H28 M34 35 H48 M16 42 H40"/>',
    "chapters": '<path d="M8 36 H18 M24 36 H38 M44 36 H56 M21 25 V47 M41 25 V47"/>',
    "info": f'<circle cx="32" cy="32" r="22"/><path d="M32 29 V44"/><circle cx="32" cy="21" r="2" {DOT}/>',
    "forward": '<path d="M9 18 L30 32 L9 46 Z M33 18 L54 32 L33 46 Z"/>',
    "rewind": '<path d="M55 18 L34 32 L55 46 Z M31 18 L10 32 L31 46 Z"/>',
}

GROUPS = [
    ("Rail", ["music", "films", "tv", "search", "settings"]),
    ("Transport", ["previous", "play", "pause", "next", "stop", "shuffle", "repeat", "repeat-one"]),
    ("Groove", ["upnext", "liner", "visualiser", "record", "watchvideo", "timemachine", "wheel", "pickup"]),
    ("Library", ["albums", "artists", "songs", "options", "view", "sort", "filter", "update", "clean", "playall"]),
    ("Info", ["runtime", "rating", "badge-4k", "badge-hdr", "resume", "trailer", "episodes", "more"]),
    ("Settings row", ["skin", "system", "addons", "files", "pictures", "favourites", "livetv", "power"]),
]

LABELS = {"upnext": "Up next", "liner": "Liner notes", "watchvideo": "Watch video", "timemachine": "Time machine",
          "pickup": "Pick up", "playall": "Play all", "badge-4k": "4K", "badge-hdr": "HDR", "badge-hdr10": "HDR10", "badge-dv": "Dolby Vision", "badge-hlg": "HLG", "repeat-one": "Repeat one",
          "livetv": "Live TV", "chevron-right": "More", "chevron-down": "Down", "audio": "Audio", "subtitles": "Subtitles", "chapters": "Chapters", "info": "Info", "tv": "TV", "addons": "Add-ons", "visualiser": "Visualiser"}


def label(name: str) -> str:
    return LABELS.get(name, name.capitalize())


def svg(name: str, size: int = 64, color: str = "#fff", opacity: float = 1.0, sw: float = SW, extra: str = "") -> str:
    body = ICONS[name]
    return (f'<svg {extra} width="{size}" height="{size}" viewBox="0 0 64 64" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}" '
            f'xmlns="http://www.w3.org/2000/svg">{body.replace("#fff", color)}</svg>')


def sheet_html(font_url: str) -> str:
    rows = []
    for g, names in GROUPS:
        cells = "".join(
            f'<div class="c">{svg(n, 64)}<div class="l">{label(n)}</div><div class="f">{n}.png</div></div>' for n in names)
        rows.append(f'<div class="g"><div class="gh">{g}</div><div class="cells">{cells}</div></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Jost;src:url({font_url});font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:#1d1b18;font-family:Jost;color:rgba(255,255,255,.92)}}
.t{{position:absolute;left:96px;top:54px;font-weight:500;font-size:34px;letter-spacing:.5px}}
.s{{position:absolute;left:96px;top:100px;font-weight:350;font-size:22px;color:rgba(255,255,255,.55)}}
.wrap{{position:absolute;left:96px;top:150px;right:96px}}
.g{{display:flex;align-items:flex-start;margin-bottom:16px}}
.gh{{width:170px;font-size:22px;font-weight:400;color:rgba(255,255,255,.55);padding-top:22px}}
.cells{{display:flex;flex-wrap:wrap;gap:0 6px}}
.c{{width:150px;height:124px;display:flex;flex-direction:column;align-items:center}}
.c svg{{margin-top:6px}}
.l{{font-size:21px;font-weight:400;margin-top:6px}}
.f{{font-size:15px;color:rgba(255,255,255,.35);margin-top:1px}}
</style></head><body>
<div class="t">Groove icons</div>
<div class="s">In-house line set &middot; 64 px grid &middot; 2 px stroke, round caps &middot; white on transparent, tinted in XML &middot; label shows on focus only</div>
<div class="wrap">{''.join(rows)}</div></body></html>"""
