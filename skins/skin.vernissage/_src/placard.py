"""The curator's card (DESIGN 6, revised 2026-10-21): one parametric placard for every context.

Port of docs/skin.vernissage/mockups/_src/placards.py to Kodi. A placard is exactly as tall as the work's mat and holds
three blocks: TOP (identity) hangs from the top padding, MIDDLE (the card) sits between, BOTTOM (the state) stands on
the bottom padding. Kodi can't measure text or add heights, so:
  * the TITLE is fitted by on-screen probe textboxes (NumPages > 1 = "doesn't fit on one line"): step 1, else 2,
    else 3 on one line, else two lines at step 3 with the "..." fade (Inter Tight 44 / 36 / 30 on the walls, Fraunces
    80 / 64 / 52 on the info page);
  * the byline tries font_body, then font_small (a probe);
  * everything else is solved HERE, at generation time, for EVERY case Kodi can tell apart at runtime (v2, M3): title
    on one line or two, tagline absent / one line / two lines (a probe), and the presence of every field that has a
    `when` (plot, set, studio, flags, ...). For each case the generator runs the drop order and the premise growth
    with the other fields at their worst case, so a missing field hands its room to the premise first. Each field
    variant is shown on a compact condition of the cases that keep it (a decision tree: placard.tree);
  * what is left over is split EXACTLY evenly between the two gaps at runtime, with no case table: the middle block
    lives in a vertical grouplist aligned centre that also holds clear copies of the top and bottom blocks (a nested
    vertical grouplist is as tall as its visible content: CGUIControlGroupList::GetHeight, Omega), so the middle
    block lands halfway between the real top and bottom blocks, whatever their real heights. Missing fields close
    up (grouplists + visibility), so nothing ever leaves a hole: the premise grows, the gaps stay equal.
Fields are plain dicts built with the helpers below; contexts (Home, easel, Salon, gallery wall, Catalogue, info,
listening room) pass their own field lists, widths and drop orders.
"""
from __future__ import annotations

import itertools
import re

from vnxml import NL, card, group, img, ind, join_and, label

GAP = 22
PITCH = {"font_placard_xl": 51, "font_placard_l": 49, "font_placard": 44, "font_placard_s": 37, "font_body": 41,
         "font_small": 38, "font_quote": 42, "font_label": 36,
         "font_display": 84, "font_display_m": 68, "font_display_s": 56}
# one-line title label slots (labels don't clip; serif slots keep room for the tails, LESSONS Void 0.9.3)
SLOT = {"font_placard_xl": 51, "font_placard": 44, "font_placard_s": 37, "font_placard_l": 49,
        "font_display": 92, "font_display_m": 74, "font_display_s": 62}
TITLE_STEPS = ("font_placard_xl", "font_placard", "font_placard_s")
DISPLAY_STEPS = ("font_display", "font_display_m", "font_display_s")
# the premise textbox of each placard variant (its "…" fade reads its NumPages): 10 x the placard's first title probe
# id + the variant number (91510-99269 with today's probe ids; screens README 5)
PREMISE_ID = lambda probes, vi: probes["t44"] * 10 + vi  # noqa: E731
DROP = ["credit", "cast", "premise:3", "made", "collection", "premise:2", "tagline:1", "premise", "tagline", "flags",
        "genres"]
DROP_SALON = ["credit", "premise", "cast", "made", "collection", "tagline:1", "tagline", "flags", "genres"]


# ------------------------------------------------------------------ field constructors
def title(text, color="$VAR[ink]", steps=TITLE_STEPS):
    return dict(key="title", kind="title", text=text, color=color, gap=0, block="top", steps=steps, when=None)


def byline(text, gap=8):
    return dict(key="byline", kind="byline", text=text, gap=gap, block="top", when=None)


def line(key, text, block, font="font_small", color="$VAR[ink2]", gap=0, when=None):
    return dict(key=key, kind="line", text=text, font=font, color=color, gap=gap, when=when, block=block)


def box(key, text, block, font, lines, color="$VAR[ink2]", gap=0, when=None, grow=0, probe=False):
    """A multi-line field: `lines` = its starting cap, `grow` = how far it may grow into spare room (premise)."""
    return dict(key=key, kind="box", text=text, font=font, lines=lines, grow=grow or lines, color=color, gap=gap,
                when=when, block=block, probe=probe)


def flags(prefix, gap=0, when=None):
    """prefix: an infolabel prefix, or [(condition, prefix)] for a placard fed by several lists. Present = the item
    has a resolution or an audio codec (a runtime case of its own)."""
    variants = prefix if isinstance(prefix, list) else [(None, prefix)]
    pres = " | ".join(f"[{join_and(c, flags_present(p))}]" for c, p in variants) if len(variants) > 1 else \
        join_and(variants[0][0], flags_present(variants[0][1]))
    return dict(key="flags", kind="flags", variants=variants, gap=gap, when=join_and(when, pres), block="bot")


def rule(gap=16):
    return dict(key="rule", kind="rule", gap=gap, block="bot", when=None)


def progress(variants, gap=16):
    """variants = [(condition, infolabel prefix)]: one fill per source list."""
    return dict(key="progress", kind="progress", variants=variants, gap=gap, block="bot", when=None)


def keyline(text, gap=14, key="key", when=None):
    return dict(key=key, kind="line", text=text, font="font_body", color="$VAR[ink]", gap=gap, block="bot", when=when)


def custom(key, xml, height, block="bot", gap=0, when=None):
    """A fixed-height piece (a progress bar with its times, the info page's action row room): `xml` is drawn in a
    group of that height; its clear copy is an empty group of the same height."""
    return dict(key=key, kind="custom", xml=xml, height=height, gap=gap, block=block, when=when)


# ------------------------------------------------------------------ heights and the solver
def f_height(f, lines=None, title_lines=1):
    k = f["kind"]
    if k == "title":
        st = f["steps"]
        return max(SLOT[s] for s in st) if title_lines == 1 else 2 * PITCH[st[-1]]
    if k == "byline":
        return PITCH["font_body"]
    if k == "line":
        return PITCH[f["font"]]
    if k == "box":
        return (lines if lines is not None else f["lines"]) * PITCH[f["font"]]
    if k == "flags":
        return 36
    if k == "rule":
        return 2
    if k == "progress":
        return 3
    if k == "custom":
        return f["height"]
    raise ValueError(k)


def solve(fields, inner_h, drop, title_lines, tag_lines, absent=frozenset()):
    """One runtime case: title lines, tagline lines (0 = none), and the keys whose `when` is false. Returns (kept
    keys, caps {key: lines}, gaps {key: gap above it}, spare)."""
    present = [f for f in fields if f["key"] not in absent and not (f["key"] == "tagline" and tag_lines == 0)]
    caps = {f["key"]: (min(f["lines"], tag_lines) if f["key"] == "tagline" else f["lines"])
            for f in present if f["kind"] == "box"}

    def blocks():
        return [[f for f in present if f["block"] == b] for b in ("top", "mid", "bot")]

    def total():
        hs = [sum(f_height(f, caps.get(f["key"]), title_lines) + (f["gap"] if i else 0) for i, f in enumerate(fs))
              for fs in blocks()]
        return sum(hs) + GAP * (sum(1 for h in hs if h) - 1)

    t = total()
    for d in drop:
        if t <= inner_h:
            break
        key, _, cap = d.partition(":")
        f = next((x for x in present if x["key"] == key), None)
        if not f:
            continue
        if cap:
            if caps.get(key, 0) > int(cap):
                caps[key] = int(cap)
        else:
            present.remove(f)
            caps.pop(key, None)
        t = total()
    prem = next((x for x in present if x["key"] == "premise"), None)
    while prem and t <= inner_h and caps["premise"] < prem["grow"]:
        caps["premise"] += 1
        t2 = total()
        if t2 > inner_h:
            caps["premise"] -= 1
            break
        t = t2
    t = total()
    assert t <= inner_h, f"placard overflow even after the drop order ({t} > {inner_h})"
    gaps = {f["key"]: (f["gap"] if i else 0) for fs in blocks() for i, f in enumerate(fs)}
    return {f["key"] for f in present}, caps, gaps, inner_h - t


# ------------------------------------------------------------------ runtime cases -> minimised conditions
# Every case variable becomes a named <expression> (the generator that uses the curator emits expressions_xml()), so
# the minimised conditions stay short: "$EXP[Lib_PC3] + !$EXP[Lib_PC7]".
PREFIX = ["PC"]
_EXPRS: dict[str, str] = {}


def set_prefix(prefix):
    """Call once per generated file (expression names must be unique across the skin)."""
    PREFIX[0] = prefix
    _EXPRS.clear()


def expr(cond):
    for name, c in _EXPRS.items():
        if c == cond:
            return f"$EXP[{name}]"
    name = f"{PREFIX[0]}_C{len(_EXPRS) + 1}"
    _EXPRS[name] = cond
    return f"$EXP[{name}]"


def expressions_xml(body):
    """The case variables that `body` reads, as expressions (one tab-indented line each); a variable the
    minimisation removed everywhere is left out (reach.py: no dead definitions)."""
    return NL.join(f'	<expression name="{n}">{c}</expression>' for n, c in _EXPRS.items() if f"$EXP[{n}]" in body)


class Cases:
    """Every runtime case of one placard: variables (name, Kodi condition), the cases (tuples of 0/1) and what the
    solver decided for each. `cond(pred)` = the minimised condition of the cases where pred(result) holds."""

    def __init__(self, fields, inner_h, drop, probes):
        np_ = lambda i: f"Integer.IsGreater(Container({i}).NumPages,1)"  # noqa: E731
        self.vars = [("t2", expr(np_(probes["t30"])))]
        tagf = next((f for f in fields if f["key"] == "tagline"), None)
        if tagf:
            self.vars += [("gp", expr(tagf["when"])), ("g2", expr(np_(probes["tagline"])))]
        self.opt = [f["key"] for f in fields if f.get("when") and f["key"] != "tagline"]
        self.vars += [(k, expr(next(f for f in fields if f["key"] == k)["when"])) for k in self.opt]
        names = [n for n, _ in self.vars]
        self.cases, self.dont = {}, []
        for bits in itertools.product((0, 1), repeat=len(names)):
            v = dict(zip(names, bits))
            if tagf and not v["gp"] and v["g2"]:
                self.dont.append(bits)             # "two tagline lines" without a tagline never happens
                continue
            tl = 2 if v["t2"] else 1
            gl = (2 if v["g2"] else 1) if tagf and v["gp"] else 0
            absent = frozenset(k for k in self.opt if not v[k])
            self.cases[bits] = solve(fields, inner_h, drop, tl, gl, absent)

    def cond(self, pred):
        hit = {b: bool(pred(*r)) for b, r in self.cases.items()}
        if all(hit.values()):
            return None
        if not any(hit.values()):
            return "false"
        return tree(tuple(c for _, c in self.vars), hit)


def _lit(c, neg=False):
    if neg:
        return f"![{c}]" if ("|" in c or "+" in c) else f"!{c}"
    return f"[{c}]" if "|" in c else c


def tree(conds, hit):
    """A compact condition for the cases where hit[bits] is true: a decision tree over the case variables in order
    (cases that never happen are don't-cares), folded into AND / OR forms. Linear in the cases (a Quine-McCluskey
    minimisation of 12 variables took minutes)."""
    T, F = "T", "F"

    def rec(i, cases):
        vals = set(cases.values())
        if not vals:
            return None                      # no case here: don't care
        if vals == {True}:
            return T
        if vals == {False}:
            return F
        c1 = rec(i + 1, {b: h for b, h in cases.items() if b[i]})
        c0 = rec(i + 1, {b: h for b, h in cases.items() if not b[i]})
        if c1 is None:
            return c0
        if c0 is None or c0 == c1:
            return c1
        v, nv = _lit(conds[i]), _lit(conds[i], True)
        if (c1, c0) == (T, F):
            return v
        if (c1, c0) == (F, T):
            return nv
        br = lambda x: f"[{x}]" if "|" in x else x  # noqa: E731
        if c1 == T:
            return f"{v} | {br(c0)}"
        if c0 == T:
            return f"{nv} | {br(c1)}"
        if c1 == F:
            return f"{nv} + {br(c0)}"
        if c0 == F:
            return f"{v} + {br(c1)}"
        return f"[{v} + {br(c1)}] | [{nv} + {br(c0)}]"

    return rec(0, hit)


# ------------------------------------------------------------------ the XML
def flag_row(prefix, width):
    """Media flags (DESIGN 6): resolution, HDR, audio, channels; textures in media/vn/flags/ (make_textures.py)."""
    import make_textures as T  # noqa: PLC0415
    P = prefix
    atmos = f"[String.Contains({P}.AudioCodec,atmos) | String.Contains({P}.FileNameAndPath,atmos)]"
    dtsx = f"[String.Contains({P}.FileNameAndPath,dts-x) | String.Contains({P}.FileNameAndPath,dtsx)]"
    plain = f"!{atmos} + !{dtsx}"
    rows = [("4K", f"String.IsEqual({P}.VideoResolution,4K)"), ("1080p", f"String.IsEqual({P}.VideoResolution,1080)"),
            ("720p", f"String.IsEqual({P}.VideoResolution,720)"),
            ("SD", f"[String.IsEqual({P}.VideoResolution,480) | String.IsEqual({P}.VideoResolution,540) | String.IsEqual({P}.VideoResolution,576)]"),
            ("DOLBY VISION", f"String.IsEqual({P}.HdrType,dolbyvision)"), ("HDR10", f"String.IsEqual({P}.HdrType,hdr10)"),
            ("HLG", f"String.IsEqual({P}.HdrType,hlg)"),
            ("ATMOS", atmos), ("DTS:X", f"!{atmos} + {dtsx}")]
    for lab, codec in (("TRUEHD", "truehd"), ("DTS-HD MA", "dtshd_ma"), ("DTS-HD", "dtshd_hra"), ("DTS", "dca"),
                       ("DD+", "eac3"), ("DD", "ac3"), ("AAC", "aac"), ("FLAC", "flac"), ("MP3", "mp3"), ("OPUS", "opus")):
        rows.append((lab, f"{plain} + String.IsEqual({P}.AudioCodec,{codec})"))
    for lab, n in (("1.0", 1), ("2.0", 2), ("5.0", 5), ("5.1", 6), ("6.1", 7), ("7.1", 8)):
        rows.append((lab, f"String.IsEqual({P}.AudioChannels,{n})"))
    imgs = NL.join(img(None, None, T.flag_width(lab), 36, f"vn/flags/{T.flag_slug(lab)}.png", "$VAR[ink2]", vis=c)
                   for lab, c in rows)
    return f"""<control type="grouplist">
	<width>{width}</width>
	<height>36</height>
	<orientation>horizontal</orientation>
	<itemgap>10</itemgap>
{ind(imgs, 1)}
</control>"""


def flags_present(prefix):
    return f"[!String.IsEmpty({prefix}.VideoResolution) | !String.IsEmpty({prefix}.AudioCodec)]"


def textbox_pair(text, font, width, lines, color, gap, vis, cid=None, fade=False):
    """Visible textbox (lines x pitch + 4, so the last line's descenders aren't cut) in a zero-height group + a clear
    auto-height copy that pushes what follows (LESSONS Void). fade (needs cid): when the text is longer than `lines`
    (NumPages of the visible box, whose page is exactly `lines` lines), line `lines` ends in a card-coloured fade and
    a "…" (Kodi never adds an ellipsis to wrapped text, LESSONS Six Degrees 0.9.1), drawn AFTER the text so they
    cover it (as vnxml.stack_text)."""
    p = PITCH[font]
    tb = [f'<control type="textbox"{f" id=\"{cid}\"" if cid else ""}>', "\t<left>0</left>", "\t<top>0</top>",
          f"\t<width>{width}</width>", f"\t<height>{lines * p + 4}</height>", f"\t<font>{font}</font>",
          f"\t<textcolor>{color}</textcolor>", f"\t<label>{text}</label>", "</control>"]
    vis_box = [NL.join(tb)]
    if fade and cid:
        more = f"Integer.IsGreater(Container({cid}).NumPages,1)"
        y = (lines - 1) * p
        vis_box += [img(width - 150, y, 150, p, "vn/fade_h.png", "$VAR[card]", vis=more),
                    label(width - 40, y, 40, p, "…", font, color, align="right", aligny="center", vis=more,
                          selected=False)]
    vis_tag = f"\t<visible>{vis}</visible>" if vis else ""
    out = [group(vis_box, top=gap, width=width, height=0, vis=vis),
           NL.join(['<control type="textbox">', f"\t<width>{width}</width>", f'\t<height max="{lines * p}">auto</height>',
                    f"\t<font>{font}</font>", "\t<textcolor>clear</textcolor>", f"\t<label>{text}</label>"]
                   + ([vis_tag] if vis else []) + ["</control>"])]
    return NL.join(out)


def ghost(xml):
    """The clear copy of a block for the centred middle grouplist: same controls, same visibility, nothing drawn and
    no ids (probes and focusable things never live in placard blocks)."""
    xml = re.sub(r"<(textcolor|selectedcolor)>[^<]*</\1>", r"<\1>clear</\1>", xml)
    xml = re.sub(r'colordiffuse="[^"]*"', 'colordiffuse="clear"', xml)
    return re.sub(r'(<control type="[a-z]+") id="[^"]*"', r"\1", xml)


def curator(fields, x, y, w, h, pad, probes, drop=DROP, vis=None, anims=None, cid=None):
    """fields: the constructors above, in order. probes: dict with ids t44, t36, t30 (title steps 1 / 2 / 3), t2 (the
    2-line title box), byline, tagline (if a tagline field exists)."""
    pt, ps = pad
    iw, ih = w - 2 * ps - 2, h - 2 * pt - 2
    cs = Cases(fields, ih, drop, probes)
    np_ = lambda i: f"Integer.IsGreater(Container({i}).NumPages,1)"  # noqa: E731
    blocks = {"top": [], "mid": [], "bot": []}
    probe_xml = []
    for f in fields:
        k, tgt, key = f["kind"], blocks[f["block"]], f["key"]
        # one variant per (cap, gap above): the gap disappears when the field is the first one left in its block
        variants = sorted({(caps.get(key), gaps[key]) for kept, caps, gaps, _ in cs.cases.values() if key in kept},
                          key=lambda v: (v[0] or 0, v[1]))
        for vi, (cap, gap) in enumerate(variants):
            vis_f = cs.cond(lambda kept, caps, gaps, _s, c=cap, g=gap: key in kept and caps.get(key) == c and gaps[key] == g)
            if k == "title":
                tgt.append(title_xml(f, iw, probes, vis_f))
            elif k == "byline":
                bp = np_(probes["byline"])
                tgt.append(label(0, gap, iw, PITCH["font_body"], f["text"], "font_body", "$VAR[ink2]", aligny="center", vis=join_and(vis_f, f"!{bp}")))
                tgt.append(label(0, gap, iw, PITCH["font_body"], f["text"], "font_small", "$VAR[ink2]", aligny="center", vis=join_and(vis_f, bp)))
            elif k == "line":
                tgt.append(label(0, gap, iw, PITCH[f["font"]], f["text"], f["font"], f["color"], aligny="center", vis=vis_f))
            elif k == "box":
                # the premise's "…" fade: every variant measures itself with its own id (a hidden variant keeps a
                # stale NumPages, and Kodi's id lookup prefers a visible control but sees only the control's own
                # visibility, not its group's: CGUIControlLookup::GetControl)
                pid = PREMISE_ID(probes, vi) if key == "premise" else None
                assert vi < 10 or not pid, "more than 10 premise variants: widen PREMISE_ID"
                tgt.append(textbox_pair(f["text"], f["font"], iw, cap, f["color"], gap, vis_f, cid=pid,
                                        fade=bool(pid)))
            elif k == "flags":
                for c, pfx in f["variants"]:
                    tgt.append(group([flag_row(pfx, iw)], top=gap, width=iw, height=36,
                                     vis=join_and(vis_f, c, flags_present(pfx))))
            elif k == "rule":
                tgt.append(img(0, gap, "vn_rule_w", "vn_rule_h", "vn/white.png", "$VAR[placard_rule]", vis=vis_f))
            elif k == "progress":
                when = " | ".join(f"[{c}]" for c, _ in f["variants"])
                bars = [img(0, 0, iw, 3, "vn/white.png", "$VAR[rule]")] + [NL.join([
                    '<control type="progress">', "\t<left>0</left>", "\t<top>0</top>", f"\t<width>{iw}</width>",
                    "\t<height>3</height>", f"\t<info>{p}.PercentPlayed</info>", "\t<texturebg>vn/clear.png</texturebg>",
                    '\t<midtexture colordiffuse="$VAR[ink]">vn/white.png</midtexture>', f"\t<visible>{c}</visible>",
                    "</control>"]) for c, p in f["variants"]]
                tgt.append(group(bars, top=gap, width=iw, height=3, vis=join_and(vis_f, when)))
            elif k == "custom":
                tgt.append(group([f["xml"]], top=gap, width=iw, height=f["height"], vis=vis_f))
        if k == "title":
            for n, font in zip(("t44", "t36", "t30"), f["steps"]):
                probe_xml.append(probe(probes[n], iw, PITCH[font], f["text"], font))
        elif k == "byline":
            probe_xml.append(probe(probes["byline"], iw, PITCH["font_body"], f["text"], "font_body"))
        elif k == "box" and f.get("probe"):
            probe_xml.append(probe(probes["tagline"], iw, PITCH[f["font"]], f["text"], f["font"]))

    def gl(inner, align=None, left=ps + 1, top=pt + 1):
        return NL.join(['<control type="grouplist">', f"\t<left>{left}</left>", f"\t<top>{top}</top>",
                        f"\t<width>{iw}</width>", f"\t<height>{ih}</height>", "\t<itemgap>0</itemgap>",
                        *([f"\t<align>{align}</align>"] if align else []), "\t<usecontrolcoords>true</usecontrolcoords>",
                        ind(NL.join(inner), 1), "</control>"])

    parts = [card(0, 0, w, h), group(probe_xml, left=ps + 1, top=pt + 1)]
    parts.append(gl(blocks["top"]))
    if blocks["mid"]:
        # the middle block between clear copies of the other two, centred: both gaps = GAP + half the spare
        sp = lambda: img(0, 0, 8, GAP, "vn/clear.png")  # noqa: E731
        parts.append(gl([gl([ghost(x_) for x_ in blocks["top"]], left=0, top=0), sp(), *blocks["mid"], sp(),
                         gl([ghost(x_) for x_ in blocks["bot"]], left=0, top=0)], align="center"))
    parts.append(gl(blocks["bot"], align="bottom"))
    return group(parts, left=x, top=y, width=w, height=h, vis=vis, anims=anims, cid=cid)


def title_xml(f, iw, probes, vis):
    """The fitted title: step 1 / 2 / 3 on one line, else two lines at step 3 with the "..." fade on line 2."""
    np_ = lambda i: f"Integer.IsGreater(Container({i}).NumPages,1)"  # noqa: E731
    a, b_, c = (np_(probes[n]) for n in ("t44", "t36", "t30"))
    s1, s2, s3 = f["steps"]
    p3 = PITCH[s3]
    o = [label(0, 0, iw, SLOT[s1], f["text"], s1, f["color"], aligny="center", vis=join_and(vis, f"!{a}")),
         label(0, 0, iw, SLOT[s2], f["text"], s2, f["color"], aligny="center", vis=join_and(vis, f"{a} + !{b_}")),
         label(0, 0, iw, SLOT[s3], f["text"], s3, f["color"], aligny="center", vis=join_and(vis, f"{b_} + !{c}"))]
    # two lines at step 3; the "…" fade on line 2 when longer, drawn over the text (it used to sit under it)
    o.append(textbox_pair(f["text"], s3, iw, 2, f["color"], 0, join_and(vis, c), cid=probes["t2"], fade=True))
    return NL.join(o)


def probe(cid, width, pitch, text, font):
    """One-line probe at the placard's real position (off-screen probes report NumPages 0, LESSONS Six Degrees):
    height 1.5 lines, so NumPages > 1 = the text needs more than one line at this font."""
    return NL.join([f'<control type="textbox" id="{cid}">', "\t<left>0</left>", "\t<top>0</top>", f"\t<width>{width}</width>",
                    f"\t<height>{pitch + pitch // 2}</height>", f"\t<font>{font}</font>", "\t<textcolor>clear</textcolor>",
                    f"\t<label>{text}</label>", "</control>"])


def report(fields, h, pad, drop=DROP):
    """The fit log for build.py: every distinct outcome of one context over all its runtime cases."""
    ih = h - 2 * pad[0] - 2
    probes = dict(t30=1, tagline=2)
    cs = Cases(fields, ih, drop, probes)
    names = [n for n, _ in cs.vars]
    out = {}
    for bits, (kept, caps, _g, spare) in cs.cases.items():
        v = dict(zip(names, bits))
        missing = [k for k in cs.opt if not v[k]]
        dropped = sorted(f["key"] for f in fields if f["key"] not in kept and f["key"] not in missing
                         and not (f["key"] == "tagline" and not v.get("gp")))
        sig = (tuple(sorted(caps.items())), tuple(dropped))
        o = out.setdefault(sig, [0, 10 ** 6, 0])
        o[0] += 1
        o[1] = min(o[1], spare)
        o[2] = max(o[2], spare)
    return [f"{n:3d} case(s): caps {dict(c)}, dropped {list(d) or '-'}, spare {lo}-{hi}px (split evenly)"
            for (c, d), (n, lo, hi) in sorted(out.items(), key=lambda kv: -kv[1][0])]
