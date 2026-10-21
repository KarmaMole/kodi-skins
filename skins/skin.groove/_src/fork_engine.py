"""Fork pass: skin.nocturne 0.9.6 engine -> skin.groove (M1, 2026-10-21).   python skins/skin.groove/_src/fork_engine.py --yes

Copies Nocturne's 1080i windows/includes, playlists and strings into skins/skin.groove and rewrites them for Groove:
  * names: nocturne.* settings/properties -> groove.*, Noc_ includes/variables -> Groove_ (a few renamed to what
    they now are, see INCLUDE_RENAME), playlists nocturne_ -> groove_, TMDbHelper.NocturnePlayer -> GroovePlayer
  * fonts: Nocturne's serif/sans scale -> Groove's Jost scale (FONT_MAP; Font.xml comes from make_fontxml.py)
  * colours: every colour slot (textcolor & co, colordiffuse, [COLOR], include params, variable values) -> a ROOM TOKEN
    $VAR[<token>] (Includes_Theme.xml), so the Dark and Light rooms come from the same XML. Hex and Nocturne names
    are classified by role (COLOR_MAP / classify_hex). Statics (white, black, clear, white_NN) stay plain names.
  * textures: Nocturne's brass/torch textures -> media/fork/* (white-alpha copies made by make_placeholders.py, tinted
    by tokens), the plaster wall -> $VAR[Tex_Room], cards -> $VAR[Tex_Card], icons -> Groove icon names.
Files Groove writes itself are NOT forked (HAND below): Home, Includes_Home, Includes_Groove, Includes_Theme, Includes,
Font.xml, SkinSettings, Includes_SkinSettings, Timers. Re-running overwrites every FORKED file: once M2-M4 start
editing forked windows by hand, DO NOT re-run (keep it for the record, like Nocturne's fork_from_majan.py).
"""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parent / "skin.nocturne"
X_SRC, X = SRC / "1080i", ROOT / "1080i"

HAND = {"Home.xml", "Includes_Home.xml", "Includes_Nocturne.xml", "Font.xml", "SkinSettings.xml",
        "Includes_SkinSettings.xml", "Includes.xml", "Timers.xml"}

# ------------------------------------------------------------------ fonts
FONT_MAP = {
    "title_120": "font_display", "title_76": "font_title_xl", "title_64": "font_title_xl", "title_56": "font_hero",
    "title_48": "font_title_l", "title_40": "font_title", "title_34": "font_title_s", "title_30": "font_caption",
    "serif_32": "font_lead", "serif_28": "font_caption_light", "serifr_40": "font_title", "serifr_32": "font_lead",
    "clock_30": "font_clock", "sans_28": "font_label", "sans_26": "font_label_m", "sans_24": "font_label_s",
    "sans_22": "font_label_xs", "sans_20": "font_label_xs",
    "body_26": "font_body", "body_24": "font_body_s", "body_22": "font_body_xs", "body_20": "font_body_xs",
    "caps_20": "font_caps", "caps_22": "font_fact_label", "nav_24": "font_label_s",
    "capss_20": "font_caps", "capss_22": "font_fact_label", "btn_22": "font_label_s", "btn_20": "font_label_xs",
    "num_20": "font_small_22", "num_22": "font_small_22", "num_26": "font_fact",
}

# ------------------------------------------------------------------ colours
STATIC = {"white", "black", "clear", "dim_video"}
COLOR_MAP = {  # Nocturne name -> Groove token (room token unless in STATIC / white_NN)
    "light": "ink", "text_primary": "ink", "text_lit": "ink", "text_body": "ink",
    "text_secondary": "ink2", "text_tertiary": "ink2", "serif_soft": "ink2", "caption_lit": "ink2",
    "text_unlit": "ink3", "brass": "ink", "brass_light": "ink", "brass_word": "ink2", "brass_dim": "line_strong",
    "hairline": "line", "hairline_soft": "line_hair", "hairline_strong": "line_strong",
    "border_control": "line_strong", "border_button": "line_strong",
    "hairline_art": "line", "hairline_art_strong": "line_strong",
    "accent": "ink", "accent_signal": "ink", "accent_cobalt": "ink", "accent_mint": "ink", "accent_amber": "ink",
    "accent_rose": "ink", "accent_ice": "ink", "accent_bone": "ink",
    "scrim": "ground", "scrim_tab": "dim_dialog", "scrim_track": "scrim_soft", "shadow": "shadow",
    "focus_halo": "clear", "dim_passed": "dim_cover", "dim_ahead": "dim_cover", "dim_row": "dim_cover",
    "unlit_art": "dim_cover", "art_faint": "white_30", "art_soft": "white_45", "art_visible": "white_65",
    "warm_art": "white", "disabled": "disabled", "dim_dialog": "dim_dialog", "dim_video": "dim_video",
    "bg": "ground", "velvet": "ground", "bg_raised": "surface_raised", "bg_ghost": "surface", "ink": "on_lit",
    "white": "white", "black": "black", "clear": "clear",
}
GLOW_TEX = re.compile(r"(glow|halo|cone|strip|glint|filament|dust|rail_on|focus/halo)")


def token(t):
    return t if (t in STATIC or t.startswith("white_")) else f"$VAR[{t}]"


def classify_hex(h, ctx):
    a, r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
    lum = (r + g + b) / 3
    if ctx == "shadow":
        return "text_shadow"
    if min(r, g, b) >= 0xf0 and ctx == "tint":  # pure white alpha = an art multiplier
        steps = [10, 20, 30, 40, 45, 55, 65, 70, 80, 90]
        if a >= 0xf8:
            return "white"
        if a == 0:
            return "clear"
        return "white_%d" % min(steps, key=lambda s: abs(s - a / 2.55))
    if lum >= 140:
        if ctx == "glow":
            return "focus_glow"
        if a >= 0xc0:
            return "ink"
        if a >= 0x80:
            return "ink2"
        if a >= 0x5a:
            return "icon_rest"
        if a >= 0x30:
            return "ink3"
        return "line" if a >= 0x1e else "line_hair"
    if lum <= 70:
        if (r, g, b) == (0, 0, 0):
            return "black" if a == 0xff else "shadow"
        if a == 0xff:
            return "ground"
        return "dim_dialog" if a >= 0xb0 else "scrim_soft"
    return "ink2"


def map_color(v, ctx="text"):
    s = v.strip()
    if not s or s.startswith("$PARAM") or s.startswith("$INFO"):
        return v
    if s in ("$VAR[Noc_HaloColor]", "$VAR[Noc_PlayerHaloColor]"):
        return "$VAR[glow]"
    if s.startswith("$"):
        return v
    if s.lower() == "ffffe2b8":
        return "$VAR[glow_fallback]"
    if re.fullmatch(r"[0-9a-fA-F]{8}", s):
        return token(classify_hex(s.lower(), ctx))
    if ctx == "shadow" and s in COLOR_MAP:
        return "$VAR[text_shadow]"
    if s in COLOR_MAP:
        t = COLOR_MAP[s]
        if ctx == "glow" and s in ("light", "warm_art", "text_primary", "text_lit"):
            t = "focus_glow"
        return token(t)
    return v


# ------------------------------------------------------------------ textures
TINT_INK, TINT_LINE, TINT_GLOW, TINT_GROUND, TINT_SURF = "$VAR[ink]", "$VAR[line_strong]", "$VAR[focus_glow]", "$VAR[ground]", "$VAR[surface]"
TEX_MAP = {  # Nocturne path -> (Groove path, tint added when the element has no colordiffuse)
    "noc/plaster.jpg": ("$VAR[Tex_Room]", None),
    "common/white.png": ("groove/white.png", None),
    "noc/card.png": ("groove/white.png", TINT_SURF),
    "dialogs/panel_framed.png": ("groove/white.png", TINT_SURF),
    "media/dialogs/panel_framed.png": ("groove/white.png", TINT_SURF),
    "noc/key.png": ("groove/white.png", "$VAR[surface_raised]"),
    "noc/frame.png": ("", None),          # Groove: no frames
    "noc/lamp.png": ("", None),
    "noc/cornice.png": ("", None),
    "noc/shadow.png": ("fork/shadow.png", "$VAR[shadow]"),
    "noc/floor.png": ("fork/floor.png", TINT_SURF),
    "noc/ledge.png": ("fork/ledge.png", TINT_SURF),
    "noc/views/corridor.png": ("fork/views/corridor.png", None),
    "noc/views/salon.png": ("fork/views/salon.png", None),
    "noc/views/stills.png": ("fork/views/stills.png", None),
    "noc/views/listening_room.png": ("fork/views/listening_room.png", None),
    "noc/views/record_bins.png": ("fork/views/record_bins.png", None),
    "noc/views/list_video.png": ("fork/views/list_video.png", None),
    "noc/views/list_music.png": ("fork/views/list_music.png", None),
    "icons/prev.png": ("icons/previous.png", None),
    "icons/chevron_right.png": ("icons/chevron-right.png", None),
    "icons/chevron_down.png": ("icons/chevron-down.png", None),
    "markers/watched.png": ("markers/watched.png", TINT_INK),
    "markers/watched_round.png": ("markers/watched.png", TINT_INK),
    "markers/unwatched_round.png": ("markers/unwatched.png", None),
}
for _n in ("shroud_cast", "shroud_corridor", "shroud_gallery", "shroud_info", "shroud_info_wide", "shroud_music",
           "shroud_page", "shroud_small", "shroud_wide", "ceiling_ramp", "floor_ramp"):
    TEX_MAP[f"noc/{_n}.png"] = (f"fork/{_n}.png", TINT_GROUND)
for _n in ("glow_bar", "glow_row", "glow_word", "glow_warm", "halo_warm", "halo_white", "cone", "strip", "glint",
           "filament", "dust", "dust_white", "rail_on"):
    TEX_MAP[f"noc/{_n}.png"] = (f"fork/{_n}.png", TINT_GLOW)
for _n in ("tick", "dot_on", "hook", "pin", "pin_s", "wire", "picrail", "plaque", "plaque2", "plaque_capl",
           "plaque_capr", "plaque_l", "plaque_mid", "plaque_r", "plate", "rail"):
    TEX_MAP[f"noc/{_n}.png"] = (f"fork/{_n}.png", TINT_INK)
for _n in ("dot_off", "rail_mid", "rail_capl", "rail_capr", "rail_sep", "rail_sep_tall", "plaque_dim"):
    TEX_MAP[f"noc/{_n}.png"] = (f"fork/{_n}.png", TINT_LINE)

TEX_TAGS = ("texture|texturefocus|texturenofocus|alttexturefocus|alttexturenofocus|texturebg|midtexture|lefttexture|"
            "righttexture|textureradioonfocus|textureradioofffocus|textureradioonnofocus|textureradiooffnofocus|"
            "textureradioondisabled|textureradiooffdisabled|textureup|texturedown|textureupfocus|texturedownfocus|"
            "textureupdisabled|texturedowndisabled|texturesliderbar|texturesliderbarfocus|textureslidernib|"
            "textureslidernibfocus|textureslidernibdisabled|texturesliderbackground|texturesliderbardisabled|"
            "texturecolormask|texturecolordisabledmask|bordertexture|overlaytexture")
TEX_EL = re.compile(rf"<({TEX_TAGS})((?:\s+[a-z]+=\"[^\"]*\")*)\s*>([^<]*)</\1>")

INCLUDE_RENAME = {
    "Noc_Wall": "Groove_Room", "Noc_Background": "Groove_Page", "Noc_FrameParts": "Groove_ArtParts",
    "Noc_Plaque": "Groove_Caption", "Noc_Plaque2": "Groove_Caption2", "Noc_ShroudStatic": "Groove_Shade",
}


def tex_element(m):
    tag, attrs, path = m.group(1), m.group(2), m.group(3)
    p = path.strip()
    ctx = "glow" if GLOW_TEX.search(p) else "tint"
    if p in TEX_MAP:
        new, tint = TEX_MAP[p]
        if tint and "colordiffuse=" not in attrs:
            attrs += f' colordiffuse="{tint}"'
        p = new
    attrs = re.sub(r'colordiffuse="([^"]*)"', lambda mm: f'colordiffuse="{map_color(mm.group(1), ctx)}"', attrs)
    if p == "groove/white.png":
        attrs = re.sub(r'\s+border="[^"]*"', "", attrs)
    return f"<{tag}{attrs}>{p}</{tag}>"


def transform(s: str) -> str:
    # textures (elements first: the tint depends on the element; then any path left in params/variables)
    s = TEX_EL.sub(tex_element, s)
    for old in sorted(TEX_MAP, key=len, reverse=True):
        s = s.replace(old, TEX_MAP[old][0] if TEX_MAP[old][0] else "")
    # colour slots
    s = re.sub(r"<shadowcolor>([^<]*)</shadowcolor>", lambda m: f"<shadowcolor>{map_color(m.group(1), 'shadow')}</shadowcolor>", s)
    s = re.sub(r"<(textcolor|focusedcolor|disabledcolor|selectedcolor|invalidcolor|headlinecolor|colordiffuse)>([^<]*)</\1>",
               lambda m: f"<{m.group(1)}>{map_color(m.group(2))}</{m.group(1)}>", s)
    s = re.sub(r'colordiffuse="([^"]*)"', lambda m: f'colordiffuse="{map_color(m.group(1), "tint")}"', s)
    s = re.sub(r"\[COLOR ([^\]]+)\]", lambda m: f"[COLOR {map_color(m.group(1))}]", s)
    s = re.sub(r'(<param name="[^"]*(?:colou?r|diffuse|tint)[^"]*" value=")([^"]*)(")',
               lambda m: m.group(1) + map_color(m.group(2)) + m.group(3), s)
    s = re.sub(r'(<param name="[^"]*(?:colou?r|diffuse|tint)[^"]*">)([^<]*)(</param>)',
               lambda m: m.group(1) + map_color(m.group(2)) + m.group(3), s)
    s = re.sub(r"(<value(?: condition=\"[^\"]*\")?>)([0-9a-fA-F]{8}|[a-z_]+)(</value>)",
               lambda m: m.group(1) + (map_color(m.group(2)) if (m.group(2) in COLOR_MAP or re.fullmatch(r"[0-9a-fA-F]{8}", m.group(2))) else m.group(2)) + m.group(3), s)
    s = re.sub(r"<backgroundcolor>[^<]*</backgroundcolor>", "<backgroundcolor>ground_static</backgroundcolor>", s)
    # fonts
    fn = "|".join(sorted(FONT_MAP, key=len, reverse=True))
    s = re.sub(rf"<font>({fn})</font>", lambda m: f"<font>{FONT_MAP[m.group(1)]}</font>", s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*" value=")({fn})(")', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf'(<param name="[^"]*font[^"]*">)({fn})(</param>)', lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    s = re.sub(rf"(<value(?: condition=\"[^\"]*\")?>)({fn})(</value>)", lambda m: m.group(1) + FONT_MAP[m.group(2)] + m.group(3), s)
    # names
    for old, new in INCLUDE_RENAME.items():
        s = re.sub(rf"\b{old}\b", new, s)
    s = s.replace("TMDbHelper.NocturnePlayer", "TMDbHelper.GroovePlayer").replace("prefix=NocturnePlayer", "prefix=GroovePlayer")
    s = s.replace("special://skin/playlists/nocturne_", "special://skin/playlists/groove_")
    s = s.replace("nocturne.", "groove.").replace("Noc_", "Groove_")
    s = s.replace("docs/skin.nocturne", "docs/skin.groove").replace("skin.nocturne", "skin.groove")
    s = s.replace("Nocturne", "Groove")
    s = s.replace("<texture></texture>", "<texture />")
    return s


GATE_NOTE = """	<!-- Groove M1: window-level fades only in the Dark room. A window-level fade shows the window's backgroundcolor
	     (static, dark) between windows, which flashes in the Light room (MOTION.md rule: put open/close animations on
	     the content group). Forked windows keep this window-level include until M2-M4 move it to a content group. -->
"""


def gate_window_fades(s: str) -> str:
    """Anim_WindowOpenClose (used at <window> level by every forked window): Dark room only."""
    a = s.index('\t<include name="Anim_WindowOpenClose">')
    b = s.index("</include>", a) + len("</include>")
    blk = s[a:b].replace('condition="!Skin.HasSetting(groove.reducemotion)"',
                         'condition="!Skin.HasSetting(groove.reducemotion) + !Skin.HasSetting(groove.light)"')
    blk = blk.replace('condition="Skin.HasSetting(groove.reducemotion)"',
                      'condition="Skin.HasSetting(groove.reducemotion) + !Skin.HasSetting(groove.light)"')
    return s[:a] + GATE_NOTE + blk + s[b:]


def main() -> None:
    if "--yes" not in sys.argv:
        sys.exit("refusing to run without --yes (see docstring)")
    X.mkdir(exist_ok=True)
    n = 0
    for f in sorted(X_SRC.glob("*.xml")):
        if f.name in HAND:
            continue
        t = transform(f.read_text(encoding="utf-8"))
        if f.name == "Includes_Animations.xml":
            t = gate_window_fades(t)
        (X / f.name).write_text(t, encoding="utf-8", newline="\n")
        n += 1
    (ROOT / "playlists").mkdir(exist_ok=True)
    for f in (SRC / "playlists").glob("nocturne_*.xsp"):
        t = transform(f.read_text(encoding="utf-8"))
        (ROOT / "playlists" / f.name.replace("nocturne_", "groove_")).write_text(t, encoding="utf-8", newline="\n")
    po = (SRC / "language" / "resource.language.en_gb" / "strings.po").read_text(encoding="utf-8")
    po = transform(po)
    extra = (Path(__file__).parent / "strings_groove.po").read_text(encoding="utf-8")
    out = ROOT / "language" / "resource.language.en_gb" / "strings.po"
    out.parent.mkdir(parents=True, exist_ok=True)
    nl = chr(10)
    out.write_text(po.rstrip(nl) + nl + nl + extra.strip(nl) + nl, encoding="utf-8", newline=nl)
    print(f"fork pass done: {n} files")


if __name__ == "__main__":
    main()
