"""Small XML builders shared by Vernissage's generators (make_home.py, make_libviews.py, make_times.py).

Every builder returns XML text (tab-indented, LF). Colour rules (CONVENTIONS 4):
  * outside list layouts a colour slot is $VAR[<token>];
  * INSIDE list layouts an image colordiffuse keeps its build-time value (LESSONS Groove M3), so room-dependent images
    are ROOM TWINS: one control tinted day_<token> gated $EXP[VN_Day], one eve_<token> gated $EXP[VN_Dark]
    (twin_img). Labels may keep $VAR (they switch live).
"""
from __future__ import annotations

from xml.sax.saxutils import escape

NL = "\n"
DAY, DARK = "$EXP[VN_Day]", "$EXP[VN_Dark]"
RM = "$EXP[VN_RM]"
NBSP = " "


def ind(text: str, n: int) -> str:
    return NL.join(("\t" * n + ln) if ln.strip() else ln for ln in text.split(NL))


def x(s: str) -> str:
    """Escape text for an XML element (& < >)."""
    return escape(s)


def tag(name: str, value, attrs: str = "") -> str:
    if value is None:
        return ""
    a = f" {attrs}" if attrs else ""
    return f"<{name}{a}>{value}</{name}>"


def join_and(*conds) -> str | None:
    c = [f"[{c}]" if "|" in c else c for c in conds if c]   # always bracket an OR ("[a] | [b]" is one too)
    return " + ".join(c) if c else None


def control(kind: str, body: list[str], cid: int | str | None = None) -> str:
    i = f' id="{cid}"' if cid is not None else ""
    inner = NL.join(ind(b, 1) for b in body if b)
    return f'<control type="{kind}"{i}>{NL}{inner}{NL}</control>'


def pos(left=None, top=None, width=None, height=None, right=None, bottom=None) -> list[str]:
    out = []
    for n, v in (("left", left), ("top", top), ("right", right), ("bottom", bottom), ("width", width), ("height", height)):
        if v is not None:
            out.append(tag(n, v))
    return out


def img(left, top, width, height, tex, color=None, vis=None, aspect=None, border=None, fadetime=None,
        background=False, fallback=None, anims: list[str] | None = None, cid=None, right=None, bottom=None) -> str:
    attrs = []
    if border:
        attrs.append(f'border="{border}"')
    if background:
        attrs.append('background="true"')
    if fallback:
        attrs.append(f'fallback="{fallback}"')
    if color:
        attrs.append(f'colordiffuse="{color}"')
    body = pos(left, top, width, height, right, bottom)
    if aspect:
        body.append(tag("aspectratio", aspect))
    if fadetime is not None:
        body.append(tag("fadetime", fadetime))
    body.append(tag("texture", tex, " ".join(attrs)))
    if vis:
        body.append(tag("visible", vis))
    body += anims or []
    return control("image", body, cid)


def twin_img(left, top, width, height, tex, token, vis=None, border=None, anims=None, right=None, bottom=None) -> str:
    """Room twins for an image inside a list layout: day_<token> gated VN_Day, eve_<token> gated VN_Dark."""
    return NL.join(img(left, top, width, height, tex, f"{room}_{token}", join_and(gate, vis), border=border,
                       anims=anims, right=right, bottom=bottom)
                   for room, gate in (("day", DAY), ("eve", DARK)))


def label(left, top, width, height, text, font, color="$VAR[ink]", align=None, aligny=None, vis=None,
          cid=None, selected=True, wrap=False, scroll=None, anims=None, width_auto_max=None) -> str:
    body = pos(left, top, None if width_auto_max else width, height)
    if width_auto_max:
        body.insert(2 if left is not None else 1, f'<width max="{width_auto_max}">auto</width>')
    if align:
        body.append(tag("align", align))
    if aligny:
        body.append(tag("aligny", aligny))
    body.append(tag("font", font))
    body.append(tag("textcolor", color))
    if selected:
        body.append(tag("selectedcolor", color))
    if wrap:
        body.append(tag("wrapmultiline", "true"))
    if scroll is not None:
        body.append(tag("scroll", scroll))
    body.append(tag("label", text))
    if vis:
        body.append(tag("visible", vis))
    body += anims or []
    return control("label", body, cid)


def textbox(left, top, width, height, text, font, color="$VAR[ink]", vis=None, cid=None, auto_max=None,
            align=None) -> str:
    body = pos(left, top, width, None)
    body.append(f'<height max="{auto_max}">auto</height>' if auto_max else tag("height", height))
    if align:
        body.append(tag("align", align))
    body.append(tag("font", font))
    body.append(tag("textcolor", color))
    body.append(tag("label", text))
    if vis:
        body.append(tag("visible", vis))
    return control("textbox", body, cid)


def group(body: list[str], left=None, top=None, width=None, height=None, vis=None, cid=None, anims=None) -> str:
    b = pos(left, top, width, height)
    if vis:
        b.append(tag("visible", vis))
    b += anims or []
    b += body
    return control("group", b, cid)


def fade_cond(cond: str, time=300, end=0, start=100) -> list[str]:
    """A reversible Conditional fade with its reduce-motion twin (time 0); fades only, so the twins are safe."""
    return [f'<animation effect="fade" start="{start}" end="{end}" time="{time}" condition="{cond} + !{RM}">Conditional</animation>',
            f'<animation effect="fade" start="{start}" end="{end}" time="0" condition="{cond} + {RM}">Conditional</animation>']


def slide_cond(cond: str, dx: int, dy: int = 0, glide: int = 0) -> list[str]:
    """A reversible Conditional slide; glide > 0 = symmetric sine in-out (LESSONS Nocturne) + a time-0 RM twin."""
    if glide:
        return [f'<animation effect="slide" start="0,0" end="{dx},{dy}" time="{glide}" tween="sine" easing="inout" condition="{cond} + !{RM}">Conditional</animation>',
                f'<animation effect="slide" start="0,0" end="{dx},{dy}" time="0" condition="{cond} + {RM}">Conditional</animation>']
    return [f'<animation effect="slide" start="0,0" end="{dx},{dy}" time="0" condition="{cond}">Conditional</animation>']


# ------------------------------------------------------------------ works, prints, placards
def grey_path(room: str, file_part: str) -> str:
    return f"$INFO[Window(Home).Property(KarmaMole.Grey.Path)]{room}/{file_part}"


def print_layers(left, top, width, height, art, greys=(), aspect="scale", when=None) -> str:
    """An unfocused print inside a layout (DESIGN 6, SPEC 12.1): the helper's grey print (per kind: (file part,
    condition) pairs, room twins), else the ghost (colour art at ghost_tint, room twins), or the colour art when the
    Grey prints setting is off. One control per kind keeps every texture a plain $INFO (LESSONS 120, PROBES P8).
    `when` gates the whole print (several print shapes in one layout)."""
    have = " | ".join(f"[{c}]" for _, c in greys) if greys else "false"
    grey_ok = "$EXP[VN_GreyPrints] + $EXP[HasKMGreyPrints]"
    o = []
    for file_part, cond in greys:
        for room, gate in (("day", DAY), ("evening", DARK)):
            o.append(img(left, top, width, height, grey_path(room, file_part), aspect=aspect, background=True,
                         fallback="vn/print_blank.png", vis=join_and(grey_ok, f"[{cond}]", gate, when)))
    for room, gate in (("day", DAY), ("eve", DARK)):
        o.append(img(left, top, width, height, art, color=f"{room}_ghost_tint", aspect=aspect, background=True,
                     vis=join_and("$EXP[VN_GreyPrints]", f"![{grey_ok} + [{have}]]", gate, when)))
    o.append(img(left, top, width, height, art, aspect=aspect, background=True,
                 vis=join_and("!$EXP[VN_GreyPrints]", when)))
    return NL.join(o)


def blank_print(left, top, width, height, title, when=None) -> str:
    """No art at all: the neutral print card with the title in font_small ink2 (screens/Home.md states)."""
    return NL.join([
        twin_img(left, top, width, height, "vn/white.png", "card", vis=join_and("String.IsEmpty(" + title[0] + ")", when)),
        label(left + 12, top + 12, width - 24, height - 24, title[1], "font_small", "$VAR[ink2]", align="center",
              aligny="center", wrap=True, vis=join_and("String.IsEmpty(" + title[0] + ")", when)),
    ])


def lit_layers(left, top, width, height, mat, art, aspect="scale", falloff=True, grey=None, when=None,
               art_fade=300) -> str:
    """The lit work inside a focused layout: hairline frame + mat (room twins), optionally the grey print under the
    colour art (so a slow colour load shows the print, not a hole), the colour art, and the Evening mat falloff.
    (left, top, width, height) = the FRAME's outer rect; art inset = mat + 2."""
    a = mat + 2
    o = [twin_img(left, top, width, height, "vn/white.png", "frame", vis=when),
         twin_img(left + 2, top + 2, width - 4, height - 4, "vn/white.png", "mat", vis=when)]
    if falloff:
        o.append(img(left + 2, top + 2, width - 4, height - 4, "vn/mat_falloff.png", vis=join_and(DARK, when)))
    if grey:
        o.append(grey)
    o.append(img(left + a, top + a, width - 2 * a, height - 2 * a, art, aspect=aspect, background=True,
                 fadetime=art_fade, vis=when))
    return NL.join(o)


def card_twins(left, top, width, height, when=None) -> str:
    """A placard card inside a layout: card fill + 1 px card_edge, room twins."""
    return NL.join([twin_img(left, top, width, height, "vn/white.png", "card", vis=when),
                    twin_img(left, top, width, height, "vn/card_edge.png", "card_edge", vis=when, border="4")])


def card(left, top, width, height) -> str:
    """A placard card at window level (live tokens)."""
    return NL.join([img(left, top, width, height, "vn/white.png", "$VAR[card]"),
                    img(left, top, width, height, "vn/card_edge.png", "$VAR[card_edge]", border="4")])


def stack_text(text, font, width, max_lines, pitch, color="$VAR[ink2]", gap=0, when=None, cid=None,
               fade_card=False) -> str:
    """One multi-line field in a placard grouplist (usecontrolcoords): the VISIBLE textbox sits in a zero-height
    group, max_lines x pitch + 4 tall, so the last line's descenders aren't cut (a textbox clips to its rect, LESSONS
    3); a clear auto-height copy (max = max_lines x pitch) pushes what follows. With fade_card and an id, line
    max_lines ends in a card-coloured fade + "..." when the text is longer (NumPages of the visible box, LESSONS Six
    Degrees 0.9.1)."""
    h = max_lines * pitch + 4
    vis_box = [textbox(0, 0, width, h, text, font, color, cid=cid)]
    if fade_card and cid:
        more = f"Integer.IsGreater(Container({cid}).NumPages,1)"
        y = (max_lines - 1) * pitch
        vis_box += [img(width - 150, y, 150, pitch, "vn/fade_h.png", "$VAR[card]", vis=more),
                    label(width - 40, y, 40, pitch, "…", font, color, align="right", vis=more, selected=False)]
    return NL.join([
        group(vis_box, top=gap, width=width, height=0, vis=when),
        textbox(None, None, width, None, text, font, "clear", vis=when, auto_max=max_lines * pitch),
    ])


def stack_label(text, font, width, height, color="$VAR[ink2]", gap=0, when=None, cid=None) -> str:
    """A one-line field in a placard grouplist (usecontrolcoords; `gap` = space above it). Kodi's own ellipsis."""
    return label(0, gap, width, height, text, font, color, aligny="center", vis=when, cid=cid)


def no_self(xml: str) -> str:
    """A container whose <onup>/<ondown>/<onleft>/<onright> names ITSELF wraps at that edge (CGUIBaseContainer::OnUp:
    wrapAround = navigation == GetID()). Where a list must STOP at its ends, the edge takes `noop` instead (a
    non-empty action list: no wrap, nothing happens). Applied to each container's own navigation tags, i.e. the
    part before its first layout / content."""
    import re
    out, pos = [], 0
    for m in re.finditer(r'<control type="(?:list|fixedlist|panel|wraplist)" id="(\d+)">', xml):
        cid = m.group(1)
        end = len(xml)
        for t in ("<itemlayout", "<focusedlayout", "<content"):
            i = xml.find(t, m.end())
            if i != -1:
                end = min(end, i)
        head = re.sub(rf"<(on(?:up|down|left|right))>{cid}</\1>", r"<\1>noop</\1>", xml[m.end():end])
        out.append(xml[pos:m.end()] + head)
        pos = end
    out.append(xml[pos:])
    return "".join(out)


def spot(left, top, width, height, player=False) -> str:
    """The spotlight pool (window level): the warm pool at the step's strength, and over it the art-coloured pool
    (helper `colours`, SPEC 12.0: the focused art's colour, or the playing album's with player=True) at 30 %."""
    inc = "VN_ArtSpotPlayer" if player else "VN_ArtSpot"
    return NL.join([img(left, top, width, height, "vn/spot.png", "$VAR[spot]", anims=["<include>VN_SpotSteps</include>"]),
                    f'<include content="{inc}"><param name="left" value="{left}"/><param name="top" value="{top}"/>'
                    f'<param name="width" value="{width}"/><param name="height" value="{height}"/></include>'])
