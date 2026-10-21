"""ONE-OFF fork pass: skin.groove 1.0.1 engine -> skin.vernissage (M1, 2026-10-21).
    python skins/skin.vernissage/_src/fork_from_groove.py --yes

Never re-run after M1: it overwrites every forked window (docs/skin.vernissage/CONVENTIONS.md section 2). Kept for the
record, like Groove's fork_engine.py.

What it copies (SPEC section 4): Groove's engine windows and includes (dialogs, settings pages, OSD family, Search,
info, OSD auto-hide 1152, play curtain 1153 / 1154, the in-window Library panel + view picker + clean confirm), the
Defaults / Constants / Expressions / Variables files, Groove's strings.po (+ _src/strings_vernissage.po) and, for the
transitional textures the forked XML still names, copies under media/fork/ (white alpha, tinted by tokens).

What it drops (SPEC section 4: Groove's music-object language): Time machine 1170, Wheel 1171, the crate / shelf /
orbit music views (Includes_Views_Music.xml), Now Playing record / tonearm / Up next / Liner notes
(Includes_Player.xml, Includes_MusicInfo.xml, MusicOSD.xml, MusicVisualisation.xml, DialogMusicInfo.xml), Groove's
Home, theme, look, fonts and icons, every mini player call, and every glow / wash / halo / drop-shadow image layer.
Vernissage writes those files itself (HAND / GENERATED in CONVENTIONS.md section 2).

Rewrites in every forked file:
  * names: Groove_ -> VN_, groove.<setting/property> -> vernissage.<...>, Groove.Search.Encoded ->
    Vernissage.Search.Encoded, HasGrooveHelper -> HasKMHelper, GrooveLight -> VN_Day, skin.groove -> skin.vernissage.
    Helper-published names (Groove.Helper.Container, KarmaMole.*) are left alone: they are the helper's API.
  * colours: Groove's room tokens -> Vernissage's room tokens (TOKEN_MAP); static names map 1:1.
  * fonts: Groove's Jost scale -> Vernissage's Inter Tight / Fraunces roles (FONT_MAP; 28 px floor, DESIGN 4).
  * textures: groove/<x> -> vn/<x> (Vernissage's own, _src/make_textures.py) or fork/<x> (transitional copy);
    icons/<x> -> vn/icons/<x> (48 px), icons/96/<x> -> vn/icons/72/<x> (drawn by _src/icons.py in the
    Vernissage line style).
After the fork, _src/reach.py --prune removes include / variable / expression definitions nothing reaches (LESSONS
Groove QA: a fresh fork carries dozens of dead includes and their textures).
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
GROOVE = ROOT.parent / "skin.groove"
X_SRC, X = GROOVE / "1080i", ROOT / "1080i"
NL = "\n"

# Groove files Vernissage writes itself (hand or generated) or drops (music-object language)
HAND = {"Home.xml", "Includes_Home.xml", "Includes_Groove.xml", "Includes_Theme.xml", "Font.xml", "SkinSettings.xml",
        "Includes_SkinSettings.xml", "Includes.xml", "Timers.xml", "MyMusicNav.xml", "MyVideoNav.xml",
        "MusicOSD.xml", "MusicVisualisation.xml", "DialogMusicInfo.xml", "Custom_1152_OSDAutoHide.xml"}
DROP = {"Custom_1170_TimeMachine.xml", "Custom_1171_Wheel.xml", "Includes_TimeMachine.xml", "Includes_Wheel.xml",
        "Includes_Views_Music.xml", "Includes_Player.xml", "Includes_MusicInfo.xml"}

# ------------------------------------------------------------------ colours: Groove token -> Vernissage token
TOKEN_MAP = {
    "ground": "wall", "ground_edge": "wall", "surface": "card", "surface_raised": "card",
    "ink": "ink", "ink2": "ink2", "ink3": "ink2", "ink_faint": "rule", "icon_rest": "ink2", "header_rest": "ink2",
    "rim": "ink", "rim_soft": "rule", "line": "rule", "line_strong": "placard_rule", "line_hair": "rule",
    "focus_glow": "focus_fill", "focus_fill": "focus_fill", "on_lit": "on_ink", "disabled": "disabled",
    "text_shadow": "clear", "shadow": "shadow", "dim_cover": "print_tint", "dim_stage": "print_tint",
    "dim_dialog": "scrim", "scrim_soft": "scrim_soft", "glow_fallback": "spot", "glow": "spot",
    "glow_playing": "spot", "wash": "spot", "art_pool": "spot", "logo_tint": "logo_tint", "halo": "white",
    "veil_stage": "scrim", **{f"shade_{i}": "print_tint" for i in range(1, 6)},
    **{f"stack_{i}": "print_tint" for i in range(6)},
}
STATIC_MAP = {"ground_static": "wall_static", "dim_video": "scrim_pause"}  # plain names (no $VAR)


def map_tokens(s: str) -> str:
    def var(m):
        t = TOKEN_MAP.get(m.group(1))
        if t is None:
            return m.group(0)
        return t if t in ("clear", "white") else f"$VAR[{t}]"
    s = re.sub(r"\$VAR\[([a-z_0-9]+)\]", var, s)
    for old, new in STATIC_MAP.items():
        s = re.sub(rf"\b{old}\b", new, s)
    return s


# ------------------------------------------------------------------ fonts (Vernissage: DESIGN 4, nothing under 28 px)
FONT_MAP = {
    "font_label": "font_label", "font_tray": "font_label", "font_caption": "font_label",
    "font_caption_light": "font_small", "font_np_title": "font_placard_l", "font_hero": "font_exhibit",
    "font_body": "font_body", "font_fact_label": "font_small", "font_fact": "font_small", "font_small": "font_small",
    "font_small_22": "font_small", "font_clock": "font_clock", "font_spine": "font_small",
    "font_name_light": "font_placard_l", "font_name_xl": "font_exhibit", "font_title_xl": "font_exhibit",
    "font_title_l": "font_placard_l", "font_title": "font_placard_l", "font_title_s": "font_placard",
    "font_lead": "font_body", "font_label_m": "font_label", "font_label_s": "font_small", "font_label_xs": "font_small",
    "font_body_s": "font_small", "font_body_xs": "font_small", "font_caps": "font_small", "font_numeral": "font_exhibit",
}


def map_fonts(s: str) -> str:
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf"<font>({fn})</font>", lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf"(<value(?: condition=\"[^\"]*\")?>)({fn})(</value>)", lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    return s


# ------------------------------------------------------------------ textures
# Groove textures Vernissage draws itself (media/vn/, _src/make_textures.py), same role
VN_TEX = {"white.png": "white.png", "dot.png": "dot.png", "dot_12.png": "dot.png", "card_edge.png": "card_edge.png",
          "row_focus.png": "row_rule.png", "pill.png": "white.png", "btn_fill.png": "white.png"}
# Groove icon names -> Vernissage's (_src/icons.py)
ICON_RENAME = {"tv": "series", "subtitles": "subs", "previous": "prev", "chapters": "chapter-next"}
# image layers the fork removes outright: Groove's light (glow / wash / halo) and drop shadows (DESIGN 5: Vernissage
# has no elevation except the Day shadow behind the lit work)
DROP_LAYER = re.compile(r"groove/(glow_radial|glow_frame|wash_mask|shadow_square|shadow_cast|shadow_contact|"
                        r"shadow_disc|spindle|tonearm|vinyl)|fork/(glow_bar|glow_warm|rail_on)")
IMAGE = re.compile(r'[ \t]*<control type="image"[^>]*>(?:(?!<control\b).)*?</control>\n?', re.S)


def drop_layers(s: str) -> tuple[str, int]:
    n = 0

    def f(m):
        nonlocal n
        if DROP_LAYER.search(m.group(0)):
            n += 1
            return ""
        return m.group(0)
    return IMAGE.sub(f, s), n


def map_textures(s: str) -> str:
    def g(m):
        name = m.group(1)
        return "vn/" + VN_TEX[name] if name in VN_TEX else "fork/" + name
    s = re.sub(r"\bgroove/([a-z0-9_]+\.png)", g, s)
    s = re.sub(r"\bgroove/(dark|light|views|progress_ring)/", r"fork/\1/", s)
    s = re.sub(r"(?<![/\w])icons/96/", "vn/icons/72/", s)
    s = re.sub(r"(?<![/\w])icons/", "vn/icons/", s)
    s = s.replace('vn/white.png" border="4"', 'vn/white.png"')
    # the focused row: Groove's lit band with a left edge (border 8,0,0,0) -> Vernissage's hairline rule under the row
    s = s.replace('border="8,0,0,0" colordiffuse="$VAR[ink]">vn/row_rule.png', 'border="0,0,0,3" colordiffuse="$VAR[ink]">vn/row_rule.png')
    for old, new in ICON_RENAME.items():
        s = s.replace(f"vn/icons/{old}.png", f"vn/icons/{new}.png").replace(f"vn/icons/72/{old}.png", f"vn/icons/72/{new}.png")
    return s


# ------------------------------------------------------------------ include calls the fork removes (depth-aware)
DROP_CALLS = ("VidView_MiniPlayer", "Groove_MiniPlayer")


def drop_calls(s: str) -> tuple[str, int]:
    n = 0
    for name in DROP_CALLS:
        while True:
            m = re.search(rf'[ \t]*<include content="{name}">', s)
            if m:
                depth, i = 0, m.start()
                for t in re.finditer(r"<include\b[^>]*?/>|<include\b[^>]*>|</include>", s[m.start():]):
                    tok = t.group(0)
                    if tok.endswith("/>"):
                        continue
                    depth += -1 if tok.startswith("</") else 1
                    if depth == 0:
                        end = m.start() + t.end()
                        break
                end += 1 if s[end:end + 1] == NL else 0
                s = s[:i] + s[end:]
                n += 1
                continue
            m2 = re.search(rf'[ \t]*<include(?: content="{name}"\s*/|>{name}</include)>\n?', s)
            if m2:
                s = s[:m2.start()] + s[m2.end():]
                n += 1
                continue
            break
    return s, n


# ------------------------------------------------------------------ names
def map_names(s: str) -> str:
    s = s.replace("Groove.Search.Encoded", "Vernissage.Search.Encoded")
    s = re.sub(r"\bHasGrooveHelper\b", "HasKMHelper", s)
    s = re.sub(r"\bGrooveLight\b", "VN_Day", s)
    s = re.sub(r"\bGroove_", "VN_", s)
    s = re.sub(r"\bgroove\.(?=[a-z])", "vernissage.", s)          # skin settings / Home properties (lowercase)
    s = s.replace("skin.groove", "skin.vernissage")
    s = s.replace("prefix=GroovePlayer", "prefix=VernissagePlayer").replace("TMDbHelper.GroovePlayer", "TMDbHelper.VernissagePlayer")
    s = s.replace("prefix=GrooveInfo", "prefix=VernissageInfo").replace("TMDbHelper.GrooveInfo", "TMDbHelper.VernissageInfo")
    return s


HEADER = ("<!-- Forked from skin.groove 1.0.1 by _src/fork_from_groove.py (M1, never re-run). Names, colours, fonts and "
          "textures are Vernissage's; prose references to screens / boards in the comments below are Groove's "
          "(docs/skin.groove/) until this file is redrawn. -->")


def transform(s: str) -> tuple[str, dict]:
    s, n_calls = drop_calls(s)
    s, n_layers = drop_layers(s)
    s = map_textures(s)
    s = map_tokens(s)
    s = map_fonts(s)
    s = map_names(s)
    return s, {"calls": n_calls, "layers": n_layers}


def main() -> None:
    if "--yes" not in sys.argv:
        sys.exit("refusing to run without --yes (one-off fork, see the docstring)")
    X.mkdir(parents=True, exist_ok=True)
    tot = {"files": 0, "calls": 0, "layers": 0}
    for f in sorted(X_SRC.glob("*.xml")):
        if f.name in HAND or f.name in DROP:
            continue
        t, st = transform(f.read_text(encoding="utf-8"))
        t = t.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>' + NL + HEADER, 1)
        (X / f.name).write_text(t, encoding="utf-8", newline=NL)
        tot["files"] += 1
        tot["calls"] += st["calls"]
        tot["layers"] += st["layers"]
    # strings: Groove's (forked engine words, renamed) + Vernissage's own
    po = (GROOVE / "language" / "resource.language.en_gb" / "strings.po").read_text(encoding="utf-8")
    po = po.replace("skin.groove", "skin.vernissage")
    head, body = po.split("\n\n", 1)
    extra = (Path(__file__).parent / "strings_vernissage.po").read_text(encoding="utf-8")
    out = ROOT / "language" / "resource.language.en_gb" / "strings.po"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + NL + NL + body.rstrip(NL) + NL + NL + extra.strip(NL) + NL, encoding="utf-8", newline=NL)
    # engine textures (neutral white shapes, masks, markers, calibration art) the forked XML may name
    for d in ("common", "focus", "masks", "markers", "misc", "osd"):
        src = GROOVE / "media" / d
        if src.is_dir():
            shutil.copytree(src, ROOT / "media" / d, dirs_exist_ok=True)
    # transitional Groove textures (copied whole; reach.py --prune deletes the ones nothing names)
    fork = ROOT / "media" / "fork"
    fork.mkdir(parents=True, exist_ok=True)
    for f in (GROOVE / "media" / "groove").rglob("*.png"):
        rel = f.relative_to(GROOVE / "media" / "groove")
        if rel.name in VN_TEX:
            continue
        (fork / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, fork / rel)
    for f in (GROOVE / "media" / "fork").glob("*.png"):
        shutil.copy(f, fork / f.name)
    print(f"fork pass done: {tot['files']} files, {tot['calls']} mini-player calls and {tot['layers']} light / shadow "
          f"layers removed")


if __name__ == "__main__":
    main()
