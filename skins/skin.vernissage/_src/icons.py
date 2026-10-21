"""Vernissage icon set: in-house line icons, 48 grid, 2.6 px stroke, round caps and joins, white on transparent
(tinted in XML). Rendered by make_textures.py to media/vn/icons/<name>.png (48 px) and media/vn/icons/72/<name>.png.

APPROVED (DESIGN 7, the IC dict of docs/skin.vernissage/mockups/_src/make_boards.py, copied verbatim):
  films series music search settings play pause trailer more prev next subs audio info queue sun moon down up resume
FINAL SET (the M1 architect drafts after visual-designer's review, SPEC 21 task 1, 2026-10-21): everything after the
  APPROVED block, same grid and stroke. Names are the file names the XML uses (CONVENTIONS 6). Review changes:
  upnext no longer duplicates queue (a work arriving: arrow into a portrait frame); playall is a play mark with its
  list (not queue again); episodes is one screen over a row of dashes (no longer a twin of sets); presets is the
  visualiser between two "flip" brackets (no longer a twin of addons / view); stop grew to the pause bars' optical
  size; clean is a broom with a real head. Badges are square 2 px outline boxes in Inter Tight Medium, the media flags' own style (DESIGN 5 + 6: 0 radius).
"""
from __future__ import annotations

import math

SW = 2.6  # stroke at 48 px

APPROVED = {
    "films": "<rect x='8' y='7' width='32' height='34' rx='2'/><path d='M15 7v34M33 7v34M8 15h7M8 24h7M8 33h7M33 15h7M33 24h7M33 33h7'/>",
    "series": "<rect x='5' y='9' width='38' height='25' rx='3'/><path d='M17 41h14M24 34v7'/>",
    "music": "<circle cx='24' cy='24' r='17'/><circle cx='24' cy='24' r='4.5'/>",
    "search": "<circle cx='21' cy='21' r='12.5'/><path d='M30.5 30.5L41 41'/>",
    "settings": "<path d='M7 16h26M39 16h2M7 32h4M17 32h24'/><circle cx='36' cy='16' r='4'/><circle cx='14' cy='32' r='4'/>",
    "play": "<path d='M16 10.5L37 24L16 37.5Z' stroke-linejoin='round'/>",
    "pause": "<path d='M18 12v24M30 12v24'/>",
    "trailer": "<rect x='6' y='10' width='36' height='28' rx='3'/><path d='M20.5 18l9 6-9 6z' stroke-linejoin='round'/>",
    "more": "<circle cx='13' cy='24' r='1.6'/><circle cx='24' cy='24' r='1.6'/><circle cx='35' cy='24' r='1.6'/>",
    "prev": "<path d='M33 12L19 24l14 12z' stroke-linejoin='round'/><path d='M14 12v24'/>",
    "next": "<path d='M15 12l14 12-14 12z' stroke-linejoin='round'/><path d='M34 12v24'/>",
    "subs": "<rect x='5' y='10' width='38' height='28' rx='3'/><path d='M12 25h9M25 25h11M12 31h24'/>",
    "audio": "<path d='M8 19h7l9-7v24l-9-7H8z' stroke-linejoin='round'/><path d='M30 18c2.8 3.6 2.8 8.4 0 12M35 13.5c5.4 6 5.4 15 0 21'/>",
    "info": "<circle cx='24' cy='24' r='17'/><path d='M24 22v11'/><circle cx='24' cy='15.5' r='.6'/>",
    "queue": "<path d='M8 14h24M8 22h24M8 30h14'/><path d='M30 28l10 6-10 6z' stroke-linejoin='round'/>",
    "sun": "<circle cx='24' cy='24' r='7.5'/><path d='M24 6v5M24 37v5M6 24h5M37 24h5M11.3 11.3l3.5 3.5M33.2 33.2l3.5 3.5M11.3 36.7l3.5-3.5M33.2 14.8l3.5-3.5'/>",
    "moon": "<path d='M35 31.5A14 14 0 0 1 18.5 11 14 14 0 1 0 35 31.5z' stroke-linejoin='round'/>",
    "down": "<path d='M15 19l9 9 9-9'/>",
    "up": "<path d='M15 29l9-9 9 9'/>",
    "resume": "<path d='M12 11v26'/><path d='M19 10.5L39 24L19 37.5Z' stroke-linejoin='round'/>",
}
FILLED = {"more"}  # drawn with fill (dots)


def _pt(cx, cy, r, a):
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


def _cog():
    pts = []
    for i in range(8):
        base = i * 45
        for da, rr in ((-12, 12.5), (-7, 17), (7, 17), (12, 12.5)):
            pts.append(_pt(24, 24, rr, base + da))
    return "<path d='M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z' stroke-linejoin='round'/><circle cx='24' cy='24' r='5'/>"


def _star(cx=24, cy=25, ro=16, ri=7):
    pts = [_pt(cx, cy, ro if i % 2 == 0 else ri, -90 + i * 36) for i in range(10)]
    return "<path d='M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z' stroke-linejoin='round'/>"


DRAFTS = {
    # transport / playback (SPEC 11 rule 6: Stop beside Play; chapters; listening room)
    "stop": "<rect x='13' y='13' width='22' height='22' rx='1.5'/>",
    "chapter-prev": "<path d='M14 12v24'/><path d='M36 12L22 24l14 12' stroke-linejoin='round'/>",
    "chapter-next": "<path d='M34 12v24'/><path d='M12 12l14 12-14 12' stroke-linejoin='round'/>",
    "visualiser": "<path d='M10 30v8M18 20v18M26 12v26M34 22v16M42 28v10'/>",
    "presets": "<path d='M12 15L6 24l6 9M36 15l6 9-6 9'/><path d='M18 21v6M22 16v16M26 12v24M30 19v10'/>",
    "rating": _star(),
    "runtime": "<circle cx='24' cy='24' r='16'/><path d='M24 15v9l6 4'/>",
    "repeat": "<path d='M10 22v-2a7 7 0 0 1 7-7h20M32 8l5 5-5 5M38 26v2a7 7 0 0 1-7 7H11M16 40l-5-5 5-5'/>",
    "shuffle": "<path d='M8 14h7c9 0 10 20 19 20h6M8 34h7c3 0 5-2 6.5-5M27 19c1.5-3 3.5-5 7-5h6M36 9l5 5-5 5M36 29l5 5-5 5'/>",
    # library header / panel (SPEC 7)
    "options": "<path d='M9 14h30M9 24h30M9 34h30'/>",
    "view": "<rect x='7' y='9' width='14' height='30' rx='2'/><rect x='27' y='9' width='14' height='13' rx='2'/><rect x='27' y='26' width='14' height='13' rx='2'/>",
    "sort": "<path d='M14 10v28M8 32l6 6 6-6M28 12h13M28 22h9M28 32h5'/>",
    "filter": "<path d='M8 10h32L28 25v11l-8 4V25z' stroke-linejoin='round'/>",
    "update": "<path d='M38 24a14 14 0 1 1-4.1-9.9'/><path d='M38 9v7h-7'/>",
    "clean": "<path d='M38 6l-9 15'/><path d='M22 19l14 8-6 13-17-9z' stroke-linejoin='round'/><path d='M16.5 34l5-7.5M23 37.5l5-8'/>",
    "sets": "<rect x='6' y='14' width='22' height='28' rx='2'/><path d='M13 8h20a2 2 0 0 1 2 2v26M20 3h20a2 2 0 0 1 2 2v26'/>",
    # back office (SPEC 6.5)
    "skin": "<rect x='7' y='7' width='34' height='34'/><rect x='14' y='14' width='20' height='20'/>",
    "system": _cog(),
    "addons": "<rect x='8' y='8' width='13' height='13' rx='2'/><rect x='27' y='8' width='13' height='13' rx='2'/><rect x='8' y='27' width='13' height='13' rx='2'/><path d='M33.5 27v13M27 33.5h13'/>",
    "files": "<path d='M6 14a2 2 0 0 1 2-2h10l4 4h18a2 2 0 0 1 2 2v18a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z' stroke-linejoin='round'/>",
    "pictures": "<rect x='6' y='10' width='36' height='28' rx='3'/><path d='M10 34l9-10 7 7 5-5 7 8' stroke-linejoin='round'/><circle cx='33' cy='18' r='3'/>",
    "favourites": "<path d='M24 39S10 30.5 10 21a7.5 7.5 0 0 1 14-3.7A7.5 7.5 0 0 1 38 21c0 9.5-14 18-14 18z' stroke-linejoin='round'/>",
    "livetv": "<rect x='5' y='15' width='38' height='25' rx='3'/><path d='M17 7l7 8 7-8'/>",
    "power": "<path d='M24 7v15'/><path d='M15.5 12.5a14 14 0 1 0 17 0'/>",
    "games": "<path d='M14 16h20a8 8 0 0 1 8 8v4a6 6 0 0 1-11 3l-2-3H19l-2 3A6 6 0 0 1 6 28v-4a8 8 0 0 1 8-8z' stroke-linejoin='round'/><path d='M15 21v6M12 24h6'/><circle cx='32' cy='23' r='.8'/><circle cx='35' cy='26' r='.8'/>",
    "weather": "<path d='M14 36h22a7 7 0 0 0 0-14 10 10 0 0 0-19-2 8 8 0 0 0-3 16z' stroke-linejoin='round'/>",
    # contents (panel, search, info rows)
    "albums": "<rect x='7' y='7' width='34' height='34' rx='1'/><circle cx='24' cy='24' r='9'/><circle cx='24' cy='24' r='1.4'/>",
    "artists": "<circle cx='24' cy='16' r='7'/><path d='M10 40c1.5-8 7-12 14-12s12.5 4 14 12'/>",
    "songs": "<path d='M20 34V11l16-4v23'/><circle cx='15' cy='34' r='5'/><circle cx='31' cy='30' r='5'/>",
    "episodes": "<rect x='6' y='7' width='36' height='24' rx='3'/><path d='M6 40h8M20 40h8M34 40h8'/>",
    "playall": "<path d='M8 10l14 9-14 9z' stroke-linejoin='round'/><path d='M29 13h12M29 25h12M8 37h33'/>",
    "upnext": "<path d='M5 24h15M15 18.5l5.5 5.5-5.5 5.5'/><rect x='26' y='9' width='16' height='30' rx='1.5'/>",
    "liner": "<rect x='9' y='6' width='30' height='36' rx='2'/><path d='M15 15h18M15 22h18M15 29h12'/>",
    # navigation glyphs (spinners, pickers, keyboard)
    "back": "<path d='M28 12L16 24l12 12'/>",
    "chevron-right": "<path d='M20 12l12 12-12 12'/>",
    "chevron-down": "<path d='M12 20l12 12 12-12'/>",
}
ICONS = {**APPROVED, **DRAFTS}
BADGES = {"badge-4k": "4K", "badge-dv": "DV", "badge-hdr10": "HDR10", "badge-hlg": "HLG"}  # text badges (PIL)


def svg(name: str, size: int, color: str = "#ffffff") -> str:
    body = ICONS[name]
    fill = color if name in FILLED else "none"
    sw = SW
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 48 48" fill="{fill}" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'{body.replace(chr(39), chr(34))}</svg>')
