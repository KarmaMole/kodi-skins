"""Generate 1080i/Includes_Home.xml: the Grand Gallery (Home).   python skins/skin.nocturne/_src/make_home.py

Geometry from docs/concepts/round4/mockups/NocturneHome.html (the salon hang), adjusted so every focusable frame
has room for its brass plaque below it (docs/skin.nocturne/SPEC.md, Home).

Ids
  9000 cornice group, 9001-9005 words (Films, Series, Music, Search, Settings); 9001-9004 hide with HideMenu.*
  9190 wander list (ambient torch timer)
  Films:  data lists 9201 easel / 9202 unwatched 7.5+ / 9203 new acquisitions / 9204 30-day count;
          slots 9221-9231 (group 9220)
  Series: data lists 9211 easel / 9212 unseen 7.5+ / 9213 new episodes; slots 9241-9251 (group 9240)
  Music:  9260 shelf (listening room)
Runtime properties (Window(Home)): nocturne.section films|series|music, nocturne.slot a1..c3 (the lit slot).
"""
from pathlib import Path
from localize import localize_xml  # literal label words -> $LOCALIZE[id] from strings.po (kdk labels.not-translated)
STRINGS_PO = Path(__file__).resolve().parent.parent / "language" / "resource.language.en_gb" / "strings.po"

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Home.xml"

BASE = (930, 556)          # pool centre of the big frame (b3) = shroud's resting position
GLIDE = 180                # ms (0.9.2: was 480), sine in-out (f(t) + f(1-t) = 1: an exact eased glide)
WANDER = 2600              # ms, ambient drift between frames

# slot: (group, list index, x, y, w, h, kind, plaque)
#   kind  : poster | land (landscape art)
#   plaque: ("2", left, width) two-line label | ("1",) one-line auto plaque
SLOTS = {
    "a1": ("A", 0, 64, 262, 368, 207, "land", ("2", 64, 368)),
    "a2": ("A", 1, 64, 596, 172, 255, "poster", ("2", 48, 260)),
    "a3": ("A", 2, 260, 596, 172, 255, "poster", ("2", 216, 260)),
    "b1": ("B", 1, 500, 262, 196, 291, "poster", ("2", 474, 248)),
    "b2": ("B", 2, 500, 676, 196, 291, "poster", ("2", 474, 248)),
    "b3": ("B", 0, 752, 262, 356, 528, "poster", ("1",)),
    "b4": ("B", 3, 1164, 262, 196, 291, "poster", ("2", 1138, 248)),
    "b5": ("B", 4, 1164, 676, 196, 291, "poster", ("2", 1138, 248)),
    "c1": ("C", 0, 1452, 262, 404, 227, "land", ("2", 1452, 404)),
    "c2": ("C", 1, 1452, 612, 190, 281, "poster", ("2", 1428, 250)),
    "c3": ("C", 2, 1666, 612, 190, 281, "poster", ("2", 1632, 250)),
}
PEEKS = [("A", 3, 64, 985, 172, 255), ("A", 4, 260, 985, 172, 255),
         ("C", 3, 1452, 1018, 190, 281), ("C", 4, 1666, 1018, 190, 281)]
ORDER = ["a1", "a2", "a3", "b1", "b2", "b3", "b4", "b5", "c1", "c2", "c3"]
# ambient tour: unwatched first (group B), wandering across the wall
WANDER_TOUR = ["b3", "c2", "b1", "a1", "b5", "c1", "b2", "a3", "b4", "c3", "a2"]
NAV = {  # Left/Right/Up/Down per slot (slot names; "nav" = the cornice)
    "a1": (None, "b1", "nav", "a2"),
    "a2": (None, "a3", "a1", None),
    "a3": ("a2", "b2", "a1", None),
    "b1": ("a1", "b3", "nav", "b2"),
    "b2": ("a3", "b3", "b1", None),
    "b3": ("b1", "b4", "nav", "b2"),
    "b4": ("b3", "c1", "nav", "b5"),
    "b5": ("b3", "c2", "b4", None),
    "c1": ("b4", None, "nav", "c2"),
    "c2": ("b5", "c3", "c1", None),
    "c3": ("c2", None, "c1", None),
}
# 0.9.9 main menu: words hidden in Skin settings (HideMenu.*); Settings (9005) never hides. A hidden word's room
# hides with it; the words after it slide left by the hidden word's pitch (next x - x).
HIDE = {9001: "Skin.HasSetting(HideMenu.Movies)", 9002: "Skin.HasSetting(HideMenu.TVShows)",
        9003: "Skin.HasSetting(HideMenu.Music)", 9004: "Skin.HasSetting(HideMenu.Search)"}
SEC_HIDE = {"films": HIDE[9001], "series": HIDE[9002], "music": HIDE[9003]}


def sec_on(sec):
    """the room of sec is on show (films is also the default while no section is set)"""
    c = f"String.IsEqual(Window(Home).Property(nocturne.section),{sec})"
    if sec == "films":
        c = f"[{c} | String.IsEmpty(Window(Home).Property(nocturne.section))]"
    # 0.9.9 custom rows: the room steps aside while one of the back rooms (Includes_Gallery.xml) has focus
    return f"{c} + !{SEC_HIDE[sec]} + !$EXP[CustomRowsFocus]"


# 0.9.9 custom rows (Includes_CustomRows.xml): Down from a frame with nothing below it walks into the back rooms
DOWN_TO_CUSTOM = ['<ondown condition="$EXP[CustomRow1On]">9881</ondown>',
                  '<ondown condition="!$EXP[CustomRow1On] + $EXP[CustomRow2On]">9882</ondown>',
                  '<ondown condition="!$EXP[CustomRow1On] + !$EXP[CustomRow2On] + $EXP[CustomRow3On]">9883</ondown>']


def word_hide_xml(cid, indent):
    """visible + close-up slides for one word's controls"""
    o = []
    if cid in HIDE:
        o.append(f"{indent}<visible>!{HIDE[cid]}</visible>")
    xs = [w[2] for w in WORDS]
    ids = [w[0] for w in WORDS]
    for j, pid in enumerate(ids[: ids.index(cid)]):
        o.append(f'{indent}<animation effect="slide" start="0,0" end="-{xs[j + 1] - xs[j]},0" time="0" condition="{HIDE[pid]}">Conditional</animation>')
    return o


WORDS = [  # id, label, x, width (NocturneNav 24 measured + slack), section
    (9001, "$LOCALIZE[31200]", 96, 104, "films"),
    (9002, "$LOCALIZE[31201]", 236, 118, "series"),
    (9003, "$LOCALIZE[31202]", 391, 112, "music"),
    (9004, "$LOCALIZE[137]", 539, 134, ""),
    (9005, "$LOCALIZE[5]", 710, 168, ""),
]

SECTIONS = {
    "films": dict(group=9220, first=9221, lists={"A": 9201, "B": 9202, "C": 9203},
                  labels={"A": "$LOCALIZE[31210]", "B": "$LOCALIZE[31211]", "C": "$LOCALIZE[31212]"},
                  counts={"A": 9201, "B": 9202, "C": 9204},
                  art={"A": "fanart", "B": "poster", "C": "poster"}, land_art={"A": "fanart", "C": "fanart"}),
    "series": dict(group=9240, first=9241, lists={"A": 9211, "B": 9212, "C": 9213},
                   labels={"A": "$LOCALIZE[31210]", "B": "$LOCALIZE[31213]", "C": "$LOCALIZE[31214]"},
                   counts={"A": 9211, "B": 9212, "C": 9214},
                   art={"A": "poster", "B": "poster", "C": "tvshow.poster"}, land_art={"A": "fanart", "C": "thumb"}),
}

WANDERING = ("System.IdleTime(20) + !Skin.HasSetting(nocturne.reducemotion) + !Skin.HasSetting(nocturne.noambient)"
             " + [ControlGroup(9220).HasFocus() | ControlGroup(9240).HasFocus()] + !System.HasActiveModalDialog"
             " + !Window.IsVisible(1151) + !System.ScreenSaverActive")


def lit(slot):
    n = WANDER_TOUR.index(slot) + 1
    return (f"[String.IsEqual(Window(Home).Property(nocturne.slot),{slot}) + !$EXP[Home_Wandering]] | "
            f"[$EXP[Home_Wandering] + Integer.IsEqual(Container(9190).CurrentItem,{n})]")


def esc(s):
    return s.replace("&", "&amp;")


def sid(sec, slot):
    return SECTIONS[sec]["first"] + ORDER.index(slot)


def slot_xml(sec, slot):
    S = SECTIONS[sec]
    grp, idx, x, y, w, h, kind, plq = SLOTS[slot]
    L = S["lists"][grp]
    item = f"Container({L}).ListItemAbsolute({idx})"
    art_key = S["land_art"][grp] if kind == "land" else S["art"][grp]
    art = f"$VAR[Home_Art_{sec}_{slot}]"
    cid = sid(sec, slot)
    exists = f"!String.IsEmpty({item}.Label)"
    L_, R_, U_, D_ = NAV[slot]

    def target(t):
        if t is None:
            return None
        if t == "nav":
            return {"films": 9001, "series": 9002}[sec]
        return sid(sec, t)

    easel = grp == "A"
    o = []
    o.append(f"\t\t<!-- {sec} {slot} : {item} -->")
    o.append("\t\t<control type=\"group\">")
    o.append(f"\t\t\t<left>{x}</left>\n\t\t\t<top>{y}</top>\n\t\t\t<width>{w}</width>\n\t\t\t<height>{h}</height>")
    o.append(f"\t\t\t<visible>{exists}</visible>")
    o.append("\t\t\t<include content=\"Noc_FrameParts\">")
    o.append(f"\t\t\t\t<param name=\"art\" value=\"{art}\"/>")
    o.append(f"\t\t\t\t<param name=\"lit\" value=\"{lit(slot)}\"/>")
    o.append(f"\t\t\t\t<param name=\"label\" value=\"$INFO[{item}.Label]\"/>")
    o.append("\t\t\t</include>")
    o.append("\t\t\t<include content=\"Noc_Pin\">")
    o.append(f"\t\t\t\t<param name=\"visible\" value=\"Integer.IsGreater({item}.PlayCount,0)\"/>")
    o.append("\t\t\t</include>")
    if easel:
        o.append("\t\t\t<control type=\"progress\">")
        o.append(f"\t\t\t\t<left>0</left>\n\t\t\t\t<top>{h + 22}</top>\n\t\t\t\t<width>{w}</width>\n\t\t\t\t<height>2</height>")
        o.append("\t\t\t\t<texturebg colordiffuse=\"brass_dim\">common/white.png</texturebg>")
        o.append("\t\t\t\t<midtexture colordiffuse=\"brass_light\">common/white.png</midtexture>")
        o.append(f"\t\t\t\t<info>{item}.PercentPlayed</info>")
        o.append(f"\t\t\t\t<visible>Integer.IsGreater({item}.PercentPlayed,0)</visible>")
        o.append("\t\t\t</control>")
    o.append("\t\t</control>")
    # the focus holder (invisible button over the frame)
    o.append(f"\t\t<control type=\"button\" id=\"{cid}\">")
    o.append(f"\t\t\t<left>{x}</left>\n\t\t\t<top>{y}</top>\n\t\t\t<width>{w}</width>\n\t\t\t<height>{h}</height>")
    o.append("\t\t\t<texturefocus />\n\t\t\t<texturenofocus />\n\t\t\t<label></label>")
    o.append(f"\t\t\t<visible>{exists}</visible>")
    o.append(f"\t\t\t<onfocus>SetProperty(nocturne.slot,{slot},home)</onfocus>")
    o.append(f"\t\t\t<onfocus condition=\"Skin.HasSetting(nocturne.halocolour)\">SetProperty(TMDbHelper.WidgetContainer,{L},home)</onfocus>")
    o.append(f"\t\t\t<onfocus condition=\"Skin.HasSetting(nocturne.halocolour) + !Integer.IsEqual(Container({L}).CurrentItem,{idx + 1})\">Control.Move({L},-$INFO[Container({L}).CurrentItem])</onfocus>")
    # Control.Move wraps (MoveUp/MoveDown with wrap): from item i, -CurrentItem lands on the last item, so the
    # second hop is idx + 1 (LESSONS, Sentence 0.9.x: the modular arithmetic lands exactly)
    o.append(f"\t\t\t<onfocus condition=\"Skin.HasSetting(nocturne.halocolour) + !Integer.IsEqual(Container({L}).CurrentItem,{idx + 1})\">Control.Move({L},{idx + 1})</onfocus>")
    o.append(f"\t\t\t<onclick>SetFocus({L},{idx},absolute)</onclick>")
    o.append("\t\t\t<onclick>Action(Info)</onclick>")
    o.append(f"\t\t\t<onclick>SetFocus({cid})</onclick>")
    for tag, t in (("onleft", L_), ("onright", R_), ("onup", U_), ("ondown", D_)):
        tt = target(t)
        if tt is not None:
            o.append(f"\t\t\t<{tag}>{tt}</{tag}>")
        elif tag == "ondown":
            o += [f"\t\t\t{d}" for d in DOWN_TO_CUSTOM]
    o.append(f"\t\t\t<onback>{ {'films': 9001, 'series': 9002}[sec] }</onback>")
    o.append("\t\t</control>")
    return "\n".join(o)


def plaque_xml(sec, slot):
    S = SECTIONS[sec]
    grp, idx, x, y, w, h, kind, plq = SLOTS[slot]
    L = S["lists"][grp]
    item = f"Container({L}).ListItemAbsolute({idx})"
    vis = f"!String.IsEmpty({item}.Label) + [{lit(slot)}]"
    if sec == "films":
        title = f"$INFO[{item}.Title]"
        if grp == "A":
            meta = f"$INFO[{item}.Year]$INFO[{item}.PercentPlayed,  ·  ,% $LOCALIZE[31220]]"
        else:
            meta = f"$INFO[{item}.Year]$INFO[{item}.Duration(mins),  ·  , $LOCALIZE[31221]]"
    else:
        if grp == "C":
            title = f"$INFO[{item}.TVShowTitle]"
            meta = f"$INFO[{item}.Season,$LOCALIZE[31222] ,]$INFO[{item}.Episode,  ·  $LOCALIZE[31223] ,]"
        else:
            title = f"$INFO[{item}.Title]"
            meta = f"$INFO[{item}.Year]$INFO[{item}.Property(TotalSeasons),  ·  , $LOCALIZE[31224]]"
    if plq[0] == "1":
        cx = x + w // 2
        return "\n".join([
            "\t\t<include content=\"Noc_Plaque\">",
            f"\t\t\t<param name=\"left\" value=\"{cx - 600}\"/>",
            f"\t\t\t<param name=\"top\" value=\"{y + h + 36}\"/>",
            f"\t\t\t<param name=\"title\" value=\"{title}\"/>",
            f"\t\t\t<param name=\"meta\" value=\"{meta}\"/>",
            f"\t\t\t<param name=\"visible\" value=\"{vis}\"/>",
            "\t\t</include>"])
    _, pl, pw = plq
    top = y + h + (30 if grp == "A" else 18)
    return "\n".join([
        "\t\t<include content=\"Noc_Plaque2\">",
        f"\t\t\t<param name=\"left\" value=\"{pl}\"/>",
        f"\t\t\t<param name=\"top\" value=\"{top}\"/>",
        f"\t\t\t<param name=\"width\" value=\"{pw}\"/>",
        f"\t\t\t<param name=\"title\" value=\"{title}\"/>",
        f"\t\t\t<param name=\"meta\" value=\"{meta}\"/>",
        f"\t\t\t<param name=\"visible\" value=\"{vis}\"/>",
        "\t\t</include>"])


def glint_xml(slot):
    grp, idx, x, y, w, h, kind, plq = SLOTS[slot]
    return "\n".join([
        "\t\t<control type=\"image\">",
        f"\t\t\t<left>{x + 8}</left>\n\t\t\t<top>{y - 19}</top>\n\t\t\t<width>{w - 16}</width>\n\t\t\t<height>9</height>",
        "\t\t\t<texture>noc/glint.png</texture>",
        f"\t\t\t<visible>{lit(slot)}</visible>",
        "\t\t\t<include>Anim_PlaqueVisible</include>",
        "\t\t</control>"])


def peek_xml(sec, peek):
    S = SECTIONS[sec]
    grp, idx, x, y, w, h = peek
    L = S["lists"][grp]
    item = f"Container({L}).ListItemAbsolute({idx})"
    return "\n".join([
        "\t\t<control type=\"group\">",
        f"\t\t\t<left>{x}</left>\n\t\t\t<top>{y}</top>\n\t\t\t<width>{w}</width>\n\t\t\t<height>{h}</height>",
        f"\t\t\t<visible>!String.IsEmpty({item}.Label)</visible>",
        "\t\t\t<include content=\"Noc_FrameParts\">",
        f"\t\t\t\t<param name=\"art\" value=\"$VAR[Home_Art_{sec}_peek{PEEKS.index(peek)}]\"/>",
        "\t\t\t</include>",
        "\t\t</control>"])


def art_var(name, item, keys):
    seen = []
    for k in keys:
        if k not in seen:
            seen.append(k)
    o = [f'	<variable name="{name}">']
    for k in seen[:-1]:
        o.append(f'		<value condition="!String.IsEmpty({item}.Art({k}))">$INFO[{item}.Art({k})]</value>')
    o.append(f'		<value>$INFO[{item}.Art({seen[-1]})]</value>')
    o.append('	</variable>')
    return o


POSTER_KEYS = ["poster", "tvshow.poster", "season.poster", "thumb", "fanart", "landscape", "tvshow.fanart"]
LAND_KEYS = ["landscape", "fanart", "tvshow.fanart", "thumb", "poster", "tvshow.poster"]


def art_vars():
    """Every frame falls back through the art it can use before the text plate (poster -> thumb -> fanart)."""
    o = []
    for sec, S in SECTIONS.items():
        for slot in ORDER:
            grp, idx, x, y, w, h, kind, plq = SLOTS[slot]
            item = f"Container({S['lists'][grp]}).ListItemAbsolute({idx})"
            first = S["land_art"][grp] if kind == "land" else S["art"][grp]
            o += art_var(f"Home_Art_{sec}_{slot}", item, [first] + (LAND_KEYS if kind == "land" else POSTER_KEYS))
        for n, (grp, idx, *_r) in enumerate(PEEKS):
            item = f"Container({S['lists'][grp]}).ListItemAbsolute({idx})"
            o += art_var(f"Home_Art_{sec}_peek{n}", item, [S["art"][grp]] + POSTER_KEYS)
    return "\n".join(o)


def wall_xml(sec):
    S = SECTIONS[sec]
    o = [f"\t<include name=\"Home_Wall_{sec}\">",
         "\t<control type=\"group\">",
         f"\t\t<visible>{sec_on(sec)}</visible>",
         "\t\t<include>Anim_SectionSwap</include>"]
    for p in PEEKS:
        o.append(peek_xml(sec, p))
    o.append(f"\t\t<control type=\"group\" id=\"{S['group']}\">")
    for slot in ORDER:
        o.append(slot_xml(sec, slot))
    o.append("\t\t</control>")
    for slot in ORDER:
        o.append(plaque_xml(sec, slot))
    for slot in ORDER:
        o.append(glint_xml(slot))
    o.append("\t</control>")
    o.append("\t</include>")
    return "\n".join(o)


def labels_xml(sec):
    S = SECTIONS[sec]
    xs = {"A": 64, "B": 500, "C": 1452}
    o = [f"\t<include name=\"Home_WallLabels_{sec}\">",
         "\t<control type=\"group\">",
         f"\t\t<visible>{sec_on(sec)}</visible>",
         "\t\t<include>Anim_SectionSwap</include>"]
    for g in "ABC":
        slots = [s for s in ORDER if SLOTS[s][0] == g]
        litc = " | ".join(f"[{lit(s)}]" for s in slots)
        for on in (True, False):
            col = "caption_lit" if on else "4db0a088"
            o += ["\t\t<control type=\"grouplist\">",
                  f"\t\t\t<left>{xs[g]}</left>\n\t\t\t<top>198</top>\n\t\t\t<width>400</width>\n\t\t\t<height>32</height>",
                  "\t\t\t<orientation>horizontal</orientation>\n\t\t\t<itemgap>14</itemgap>",
                  f"\t\t\t<visible>{'' if on else '!['}{litc}{'' if on else ']'}</visible>",
                  f"\t\t\t<visible>!String.IsEmpty(Container({S['lists'][g]}).ListItemAbsolute(0).Label)</visible>",
                  "\t\t\t<control type=\"label\">",
                  "\t\t\t\t<width>auto</width>\n\t\t\t\t<height>32</height>\n\t\t\t\t<aligny>center</aligny>\n\t\t\t\t<font>caps_20</font>",
                  f"\t\t\t\t<textcolor>{col}</textcolor>\n\t\t\t\t<shadowcolor>b3000000</shadowcolor>",
                  f"\t\t\t\t<label>{S['labels'][g]}</label>",
                  "\t\t\t</control>",
                  "\t\t\t<control type=\"label\">",
                  "\t\t\t\t<width>auto</width>\n\t\t\t\t<height>32</height>\n\t\t\t\t<aligny>center</aligny>\n\t\t\t\t<font>caps_20</font>",
                  f"\t\t\t\t<textcolor>{col}</textcolor>\n\t\t\t\t<shadowcolor>b3000000</shadowcolor>",
                  f"\t\t\t\t<label>$INFO[Container({S['counts'][g]}).NumItems]</label>",
                  f"\t\t\t\t<visible>Integer.IsGreater(Container({S['counts'][g]}).NumItems,0)</visible>",
                  "\t\t\t\t<animation effect=\"fade\" start=\"100\" end=\"60\" time=\"0\" condition=\"true\">Conditional</animation>",
                  "\t\t\t</control>",
                  "\t\t</control>"]
    o += ["\t</control>", "\t</include>"]
    return "\n".join(o)


def torch_xml(time, wander_time):
    bx, by = BASE
    o = ["\t<include name=\"Home_Torch\">",
         "\t<control type=\"group\">",
         f"\t\t<visible>[{sec_on('films')}] | [{sec_on('series')}]</visible>",
         "\t\t<include>Anim_SectionSwap</include>"]
    for slot in ORDER:
        grp, idx, x, y, w, h, kind, plq = SLOTS[slot]
        dx, dy = pool_centre(slot)[0] - bx, pool_centre(slot)[1] - by
        if (dx, dy) == (0, 0):
            continue
        o.append(f"\t\t<animation effect=\"slide\" start=\"0,0\" end=\"{dx},{dy}\" time=\"{time}\" tween=\"sine\" easing=\"inout\" "
                 f"condition=\"String.IsEqual(Window(Home).Property(nocturne.slot),{slot}) + !$EXP[Home_Wandering]\">Conditional</animation>")
    for n, slot in enumerate(WANDER_TOUR, 1):
        dx, dy = pool_centre(slot)[0] - bx, pool_centre(slot)[1] - by
        if (dx, dy) == (0, 0):
            continue
        o.append(f"\t\t<animation effect=\"slide\" start=\"0,0\" end=\"{dx},{dy}\" time=\"{wander_time}\" tween=\"sine\" easing=\"inout\" "
                 f"condition=\"$EXP[Home_Wandering] + Integer.IsEqual(Container(9190).CurrentItem,{n})\">Conditional</animation>")
    o += ["\t\t<include content=\"Noc_Dust\">",
          f"\t\t\t<param name=\"left\" value=\"{bx - 380}\"/>\n\t\t\t<param name=\"top\" value=\"{by - 400}\"/>",
          "\t\t</include>",
          "\t\t<control type=\"image\">",
          f"\t\t\t<left>{bx - 1920}</left>\n\t\t\t<top>{by - 1920}</top>\n\t\t\t<width>3840</width>\n\t\t\t<height>3840</height>",
          "\t\t\t<texture colordiffuse=\"$VAR[Noc_ShroudAlpha]\">noc/shroud_gallery.png</texture>",
          "\t\t</control>",
          "\t\t<include content=\"Noc_Halo\">",
          f"\t\t\t<param name=\"left\" value=\"{bx - 620}\"/>\n\t\t\t<param name=\"top\" value=\"{by - 620}\"/>",
          "\t\t</include>",
          "\t</control>",
          "\t</include>"]
    return "\n".join(o)


def pool_centre(slot):
    grp, idx, x, y, w, h, kind, plq = SLOTS[slot]
    if plq[0] == "1":
        return (x + w // 2, 556)
    bottom = y + h + (30 if grp == "A" else 18) + 84
    return (x + w // 2, (y + bottom) // 2)


def wander_list():
    items = "\n".join(f"\t\t\t\t<item><label>{s.upper()}</label><onclick>noop</onclick></item>" for s in WANDER_TOUR)
    cond = WANDERING
    return f"""\t<include name="Home_WanderTimer">
		<control type="list" id="9190">
			<left>0</left>
			<top>0</top>
			<width>1</width>
			<height>1</height>
			<orientation>vertical</orientation>
			<scrolltime>0</scrolltime>
			<autoscroll time="6500">{cond}</autoscroll>
			<itemlayout width="1" height="1"/>
			<focusedlayout width="1" height="1"/>
			<content>
{items}
			</content>
		</control>
	</include>"""


def datalist(lid, content, sort="", order="", limit="", art=("poster",), target="videos"):
    attrs = f' target="{target}"'
    if sort:
        attrs += f' sortby="{sort}"'
    if order:
        attrs += f' sortorder="{order}"'
    if limit:
        attrs += f' limit="{limit}" browse="never"'
    imgs = "".join(f'<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height>'
                   f'<texture background="true">$INFO[ListItem.Art({a})]</texture></control>' for a in art)
    return f"""		<control type="list" id="{lid}">
			<left>0</left>
			<top>0</top>
			<width>5</width>
			<height>1</height>
			<orientation>horizontal</orientation>
			<scrolltime>0</scrolltime>
			<itemlayout width="1" height="1">{imgs}</itemlayout>
			<focusedlayout width="1" height="1">{imgs}</focusedlayout>
			<content{attrs}>{content}</content>
		</control>"""


def datalists():
    return "\n".join([
        "\t<include name=\"Home_DataLists\">",
        datalist(9201, "special://skin/playlists/nocturne_inprogress_movies.xsp", "lastplayed", "descending", art=("poster",)),
        datalist(9202, "special://skin/playlists/nocturne_toprated_unwatched_all.xsp", "random"),
        datalist(9203, "videodb://recentlyaddedmovies/", art=("poster",)),
        datalist(9204, "special://skin/playlists/nocturne_new_acquisitions.xsp", art=()),
        datalist(9211, "special://skin/playlists/nocturne_inprogress_tvshows.xsp", "lastplayed", "descending", art=("poster",)),
        datalist(9212, "special://skin/playlists/nocturne_unseen_tvshows.xsp", "random"),
        datalist(9213, "videodb://recentlyaddedepisodes/", art=("tvshow.poster",)),
        datalist(9214, "special://skin/playlists/nocturne_new_episodes.xsp", art=()),
        "\t</include>"])


def words_xml():
    o = ["\t<include name=\"Home_Cornice\">"]
    # glows (above the shroud, under the words)
    for cid, label, x, w, sec in WORDS:
        cx = x + (w - 10) // 2
        on = f"Control.HasFocus({cid})"
        if sec:
            on += f" | [!ControlGroup(9000).HasFocus() + String.IsEqual(Window(Home).Property(nocturne.section),{sec})]"
            if sec == "films":
                on += " | [!ControlGroup(9000).HasFocus() + String.IsEmpty(Window(Home).Property(nocturne.section))]"
        if cid in HIDE:
            on = f"[{on}] + !{HIDE[cid]}"
        o += ["\t\t<control type=\"image\">",
              f"\t\t\t<left>{cx - 200}</left>\n\t\t\t<top>-78</top>\n\t\t\t<width>400</width>\n\t\t\t<height>300</height>",
              "\t\t\t<texture>noc/glow_warm.png</texture>",
              f"\t\t\t<visible>{on}</visible>",
              *[l for l in word_hide_xml(cid, "\t\t\t") if "<animation" in l],
              "\t\t\t<include>Anim_GlowVisible</include>",
              "\t\t</control>"]
    o += ["\t\t<control type=\"group\" id=\"9000\">"]
    ids = [w[0] for w in WORDS]
    for i, (cid, label, x, w, sec) in enumerate(WORDS):
        on = f"[!ControlGroup(9000).HasFocus() + String.IsEqual(Window(Home).Property(nocturne.section),{sec})]" if sec else "false"
        if sec == "films":
            on += " | [!ControlGroup(9000).HasFocus() + String.IsEmpty(Window(Home).Property(nocturne.section))]"
        o += [f"\t\t\t<control type=\"button\" id=\"{cid}\">",
              f"\t\t\t\t<left>{x}</left>\n\t\t\t\t<top>48</top>\n\t\t\t\t<width>{w}</width>\n\t\t\t\t<height>48</height>",
              "\t\t\t\t<font>nav_24</font>\n\t\t\t\t<textoffsetx>0</textoffsetx>\n\t\t\t\t<aligny>center</aligny>",
              "\t\t\t\t<textcolor>5ca49680</textcolor>\n\t\t\t\t<focusedcolor>text_primary</focusedcolor>",
              "\t\t\t\t<shadowcolor>b3000000</shadowcolor>",
              "\t\t\t\t<texturefocus />\n\t\t\t\t<texturenofocus />",
              f"\t\t\t\t<label>{label}</label>",
              *word_hide_xml(cid, "\t\t\t\t"),
              f"\t\t\t\t<onleft>{ids[i - 1]}</onleft>\n\t\t\t\t<onright>{ids[(i + 1) % len(ids)]}</onright>"]
        if sec in ("films", "series"):
            o += [f"\t\t\t\t<onfocus>SetProperty(nocturne.section,{sec},home)</onfocus>",
                  "\t\t\t\t<onfocus>SetProperty(nocturne.slot,b3,home)</onfocus>",
                  f"\t\t\t\t<ondown>{SECTIONS[sec]['first'] + ORDER.index('b3')}</ondown>"]
        elif sec == "music":
            o += ["\t\t\t\t<onfocus>SetProperty(nocturne.section,music,home)</onfocus>",
                  "\t\t\t\t<onfocus>SetProperty(TMDbHelper.WidgetContainer,9260,home)</onfocus>",
                  "\t\t\t\t<ondown>9260</ondown>"]
        else:
            o += [f"\t\t\t\t<ondown condition=\"{sec_on('music')}\">9260</ondown>",
                  f"\t\t\t\t<ondown condition=\"{sec_on('series')}\">9246</ondown>",
                  f"\t\t\t\t<ondown condition=\"{sec_on('films')}\">9226</ondown>"]
        click = {
            "films": "ActivateWindow(Videos,videodb://movies/titles/,return)",
            "series": "ActivateWindow(Videos,videodb://tvshows/titles/,return)",
            "music": "ActivateWindow(Music,musicdb://albums/,return)",
            "": None,
        }[sec]
        if cid == 9004:
            click = "ActivateWindow(1150)"
        if cid == 9005:
            click = "ActivateWindow(1151)"
        o.append(f"\t\t\t\t<onclick>{click}</onclick>")
        o.append("\t\t\t</control>")
        # lit copy for the active section word while focus is on the wall
        if sec:
            o += ["\t\t\t<control type=\"label\">",
                  f"\t\t\t\t<left>{x}</left>\n\t\t\t\t<top>48</top>\n\t\t\t\t<width>{w}</width>\n\t\t\t\t<height>48</height>",
                  "\t\t\t\t<font>nav_24</font>\n\t\t\t\t<aligny>center</aligny>",
                  "\t\t\t\t<textcolor>text_primary</textcolor>\n\t\t\t\t<shadowcolor>e6281806</shadowcolor>",
                  f"\t\t\t\t<label>{label}</label>",
                  f"\t\t\t\t<visible>[{on}] + !{HIDE[cid]}</visible>",
                  *[l for l in word_hide_xml(cid, "\t\t\t\t") if "<animation" in l],
                  "\t\t\t</control>"]
    o += ["\t\t</control>", "\t</include>"]
    return "\n".join(o)


def main():
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- GENERATED by _src/make_home.py - edit the tables there, then re-run. Home = the Grand Gallery. -->",
             "<includes>",
             art_vars(), datalists(), wander_list(), words_xml(),
             wall_xml("films"), wall_xml("series"),
             labels_xml("films"), labels_xml("series"),
             '\t<include name="Home_TorchNormal">\n' + "\n".join(torch_xml(GLIDE, WANDER).split("\n")[1:]),
             '\t<include name="Home_TorchReduced">\n' + "\n".join(torch_xml(1, 1).split("\n")[1:]),
             "</includes>", ""]
    text = "\n".join(parts)
    text = text.replace("<include name=\"Home_TorchNormal\">\n\t<control", "<include name=\"Home_TorchNormal\">\n\t<control", 1)
    OUT.write_text(localize_xml(text, STRINGS_PO), encoding="utf-8", newline="\n")
    print("wrote", OUT, len(text))


if __name__ == "__main__":
    main()
