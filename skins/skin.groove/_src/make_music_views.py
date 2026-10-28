"""Generate 1080i/Includes_Views_Music.xml: Groove's music library (MyMusicNav) - header, the five music views and
their shared caption / light.   python skins/skin.groove/_src/make_music_views.py

Screens: docs/skin.groove/screens/MyMusicNav.md, View_500_CoverWall.md, View_501_CrateDig.md,
View_502_ShelfOfSpines.md, View_503_Orbit.md, View_50_List.md. Motion: MOTION.md 5.6-5.9 (Anim_* includes).

Views (MyMusicNav <views>500,501,502,503,50</views>, ids are window-local, MyVideoNav has its own 500/510/50):
  500 Cover wall   panel 8 x 240, covers 224, focused cover lit (albums, artists = round crops; 1.0.8 songs too)
  501 Crate dig    invisible 1 px driver fixedlist (13 items drawn, focusposition 3) + static slots fed by
                   Container(501).ListItemNoWrap(k): 9 records behind, the focused record tilted forward, 3 flipped
  502 Shelf        driver fixedlist (36 items, focusposition 19) + static spines -18..-1 / +1..+16 and the face-out
                   cover in the gap. Spine = the helper's colour spine over the cover's left edge strip.
  503 Orbit        driver fixedlist (7 items, focusposition 3) + the shared arc (arc() below; Custom_1170 reuses it)
                   (1.0.8: albums, artists and songs; docs/VIEWS_PER_SECTION_2026-10-28.md)
  50  List         one line per item, the focused item's art lit at the right
Every album view shares MusicLib_Caption (one line after a 1 s rest) and MusicLib_Wash (the room light).

Static slots and the one-frame OnNext / OnPrevious pulse: LESSONS Orbit (Conditional, reversible="false",
replays from the neighbour's pose). Depth shade of overlapping records: colordiffuse $VAR[shade_N] (multiply in both
rooms, lighter in Light, MOTION 3.2). Receding slots that don't overlap fade by alpha (into the room's ground).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Views_Music.xml"

VIEWS = (500, 501, 502, 503, 50)
ANYVIEW = "[" + " | ".join(f"Control.HasFocus({v})" for v in VIEWS) + "]"
ROOTS = ("musicdb://albums/", "musicdb://artists/", "musicdb://songs/", "musicdb://genres/", "musicdb://")
AT_ROOT = "[" + " | ".join(f"String.IsEqual(Container.FolderPath,{p})" for p in ROOTS) + "]"
RM = "Skin.HasSetting(groove.reducemotion)"
LIGHT = "$EXP[GrooveLight]"


NL = "\n"


def t(n):
    return "\t" * n


# ---------------------------------------------------------------- small builders
def image(x, y, w, h, tex, diffuse=None, vis=None, extra="", aspect=None, bg=False, ind=3, texattr=""):
    d = f' colordiffuse="{diffuse}"' if diffuse else ""
    b = ' background="true"' if bg else ""
    if aspect == "scale" and ' diffuse="groove/' in texattr:
        # a mask (disc, quarter disc) on cropped art: keep the mask on the control rect, not on the whole scaled image
        # (otherwise a non-square photo gets a wide ellipse cut flat at the sides, DEVICE_AUDIT m7)
        aspect = ("scale", ' scalediffuse="false"')
    a = f"\n{t(ind + 1)}<aspectratio{aspect[1] if isinstance(aspect, tuple) else ''}>{aspect[0] if isinstance(aspect, tuple) else aspect}</aspectratio>" if aspect else ""
    v = f"\n{t(ind + 1)}<visible>{vis}</visible>" if vis else ""
    e = ("\n" + t(ind + 1) + extra) if extra else ""
    return (f"{t(ind)}<control type=\"image\">\n{t(ind + 1)}<left>{x}</left>\n{t(ind + 1)}<top>{y}</top>\n"
            f"{t(ind + 1)}<width>{w}</width>\n{t(ind + 1)}<height>{h}</height>{a}\n"
            f"{t(ind + 1)}<texture{b}{d}{texattr}>{tex}</texture>{v}{e}\n{t(ind)}</control>")


def static_fade(pct):
    return f'<animation effect="fade" start="100" end="{pct}" time="0" condition="true">Conditional</animation>'


def rim(w, h, vis, ind, anim=""):
    a = f"\n{t(ind + 1)}{anim}" if anim else ""
    return (f"{t(ind)}<control type=\"group\">\n{t(ind + 1)}<visible>{vis}</visible>{a}\n"
            + image(0, 0, w, 2, "groove/white.png", "$VAR[rim]", ind=ind + 1) + "\n"
            + image(0, h - 2, w, 2, "groove/white.png", "$VAR[rim]", ind=ind + 1) + "\n"
            + image(0, 2, 2, h - 4, "groove/white.png", "$VAR[rim]", ind=ind + 1) + "\n"
            + image(w - 2, 2, 2, h - 4, "groove/white.png", "$VAR[rim]", ind=ind + 1) + f"\n{t(ind)}</control>")


def fallback(w, h, label, art, ind, font="font_small", round_=False):
    """designed blank sleeve: only when the item has no art (DESIGN 12.5: never under real art)"""
    vis = f"String.IsEmpty({art})"
    return (image(0, 0, w, h, "groove/disc_mask.png" if round_ else "groove/white.png", "$VAR[surface_raised]", vis, ind=ind) + "\n"
            f"{t(ind)}<control type=\"textbox\">\n{t(ind + 1)}<left>{max(8, w // 14)}</left>\n{t(ind + 1)}<top>{max(8, h // 14)}</top>\n"
            f"{t(ind + 1)}<width>{w - 2 * max(8, w // 14)}</width>\n{t(ind + 1)}<height>{h - 2 * max(8, h // 14)}</height>\n"
            f"{t(ind + 1)}<align>center</align>\n{t(ind + 1)}<aligny>center</aligny>\n{t(ind + 1)}<font>{font}</font>\n"
            f"{t(ind + 1)}<textcolor>$VAR[ink2]</textcolor>\n{t(ind + 1)}<label>{label}</label>\n"
            f"{t(ind + 1)}<visible>{vis}</visible>\n{t(ind)}</control>")


def lit_layers(w, h, lit, ind, radial=2.4, round_=False, in_layout=True, glow_alpha=None, clamp=None):
    """The light behind one focused cover (DESIGN 5 / 12.4), in the cover's own coordinates (0,0,w,h):
    pool (Light), halo radial tinted glow, cast (Light), bloom frame (Dark), drop + contact shadows (hollow).
    clamp: inside a list / panel, the padding in px around the item; every layer stays inside it (a container clips
    its children, so a bigger halo shows a hard-edged box); the window-level wash gives the wide light."""
    anim = "<include>Anim_FocusLight</include>" if in_layout else "<include>Anim_GlowLayer</include>"
    o = []
    s = int(radial * w) if clamp is None else w + 2 * clamp
    o.append(image((w - s) // 2, (h - s) // 2, s, s, "groove/glow_radial.png", "$VAR[art_pool]",
                   f"{LIGHT} + {lit}", anim, ind=ind))
    s2 = int(min(radial + 0.6, 3.0) * w) if clamp is None else w + 2 * clamp
    o.append(image((w - s2) // 2, (h - s2) // 2, s2, s2, "groove/glow_radial.png", "$VAR[glow]", lit,
                   anim + "\n" + t(ind + 1) + "<include>Groove_GlowStrength</include>", ind=ind))
    cs = int(1.5 * w) if clamp is None else w + 2 * clamp
    o.append(image((w - cs) // 2, (h - cs) // 2 + int(h * 40 / 620), cs, cs, "groove/shadow_cast.png", "$VAR[glow]",
                   f"{LIGHT} + {lit}", anim, ind=ind))
    if round_:
        ds = int(w * 1.3)
        o.append(image((w - ds) // 2, (h - ds) // 2 + 14, ds, ds, "groove/shadow_disc.png", "$VAR[shadow]", None, ind=ind))
        return "\n".join(o)
    o.append(image(-40, -40, w + 80, h + 80, "groove/glow_frame.png", "$VAR[glow]", f"!{LIGHT} + {lit}",
                   anim + "\n" + t(ind + 1) + "<include>Groove_GlowStrength</include>", ind=ind, texattr=' border="48"'))
    if clamp is None:
        o.append(image(-96, -60, w + 192, h + 180, "groove/shadow_square.png", "$VAR[shadow]", None, ind=ind,
                   texattr=' border="96,60,96,120"'))
    o.append(image(-24, -16, w + 48, h + 48, "groove/shadow_contact.png", "$VAR[shadow]", None, ind=ind,
                   texattr=' border="24,16,24,32"'))
    return "\n".join(o)


def cover(w, h, art, label, ind, diffuse=None, round_=False, extra="", aspect="scale"):
    """fallback sleeve (only without art) + the art (+ round crop for artists)"""
    texattr = ' diffuse="groove/disc_mask.png"' if round_ else ""
    probe = art[len("$INFO["):-1] if art.startswith("$INFO[") else art
    return (fallback(w, h, label, probe, ind, round_=round_) + NL
            + image(0, 0, w, h, art, diffuse, None, extra, aspect=aspect, bg=True, ind=ind, texattr=texattr))


# ---------------------------------------------------------------- shared navigation
def nav_view():
    """inside every view container: Up to the header tab of this content, Back at the start folder -> Home"""
    return """			<onup condition="Container.Content(artists)">9502</onup>
			<onup condition="Container.Content(songs)">9503</onup>
			<onup>9501</onup>
			<onback condition="{root}">9398</onback>
			<include>Lib_OpenLeft</include>
			<include>Lib_OpenRight</include>""".replace("{root}", AT_ROOT)


# ---------------------------------------------------------------- caption + wash
def caption(id_, cx, top, width, font_title="font_caption", font_meta="font_caption_light"):
    left = cx - width // 2
    return f"""		<control type="grouplist">
			<left>{left}</left>
			<top>{top}</top>
			<width>{width}</width>
			<height>48</height>
			<orientation>horizontal</orientation>
			<align>center</align>
			<itemgap>14</itemgap>
			<usecontrolcoords>true</usecontrolcoords>
			<visible>System.IdleTime(1) + !Container({id_}).Scrolling + Control.IsVisible({id_}) + !Container({id_}).ListItem.IsParentFolder + !String.IsEmpty(Container({id_}).ListItem.Label)</visible>
			<include>Anim_CaptionRest</include>
			<control type="label">
				<width max="{width - 380}">auto</width>
				<height>48</height>
				<aligny>center</aligny>
				<font>{font_title}</font>
				<textcolor>$VAR[ink]</textcolor>
				<shadowcolor>$VAR[text_shadow]</shadowcolor>
				<label>$VAR[MusicLib_Title{id_}]</label>
			</control>
			<control type="label">
				<top>2</top>
				<width max="560">auto</width>
				<height>48</height>
				<aligny>center</aligny>
				<font>{font_meta}</font>
				<textcolor>$VAR[ink2]</textcolor>
				<shadowcolor>$VAR[text_shadow]</shadowcolor>
				<label>$VAR[MusicLib_Meta{id_}]</label>
			</control>
		</control>"""


def meta_var(id_):
    c = f"Container({id_}).ListItem"
    return f"""	<variable name="MusicLib_Title{id_}">
		<value condition="String.IsEqual({c}.DBType,song) + !String.IsEmpty({c}.Title)">$INFO[{c}.Title]</value>
		<value>$INFO[{c}.Label]</value>
	</variable>
	<variable name="MusicLib_Meta{id_}">
		<value condition="Container.Content(artists)"></value>
		<value condition="!String.IsEmpty({c}.Artist) + !String.IsEmpty({c}.Year)">·  $INFO[{c}.Artist]  ·  $INFO[{c}.Year]</value>
		<value condition="!String.IsEmpty({c}.Artist)">·  $INFO[{c}.Artist]</value>
		<value condition="!String.IsEmpty({c}.Year)">·  $INFO[{c}.Year]</value>
	</variable>"""


def wash(id_, cx, cy, size, ind=2):
    """the room light (SPEC 11 / DESIGN 6.2): the helper's soft art (Groove_SoftArt), else the art itself, through
    wash_mask at the Glow strength alpha. Centred on (cx, cy) in window coordinates."""
    x, y = cx - size // 2, cy - size // 2
    art = f"$INFO[Container({id_}).ListItem.Art(thumb)]"
    helper = "$EXP[HasGrooveHelper] + !String.IsEmpty(Window(Home).Property(Groove.Art.Soft))"
    return "\n".join([
        image(x, y, size, size, "$VAR[Groove_SoftArt]", "$VAR[wash]", helper, "<include>Anim_GlowLayer</include>",
              aspect="stretch", bg=True, ind=ind, texattr=' diffuse="groove/wash_mask.png"').replace(
            "</texture>", "</texture>\n" + t(ind + 1) + "<include>Anim_GlowFadetime</include>", 1),
        image(x, y, size, size, art, "$VAR[wash]", "!" + "[" + helper + "]", "<include>Anim_GlowLayer</include>",
              aspect="stretch", bg=True, ind=ind, texattr=' diffuse="groove/wash_mask.png"').replace(
            "</texture>", "</texture>\n" + t(ind + 1) + "<include>Anim_GlowFadetime</include>", 1),
    ])


# ---------------------------------------------------------------- header
LEFT_TABS = [  # id, icon, label, onclick, current
    (9501, "albums", "$LOCALIZE[132]", "ReplaceWindow(Music,musicdb://albums/,return)", "$EXP[MusicLib_TabAlbums]"),
    (9502, "artists", "$LOCALIZE[133]", "ReplaceWindow(Music,musicdb://artists/,return)", "$EXP[MusicLib_TabArtists]"),
    (9503, "songs", "$LOCALIZE[134]", "ReplaceWindow(Music,musicdb://songs/,return)", "$EXP[MusicLib_TabSongs]"),
    (9504, "timemachine", "$LOCALIZE[31407]", "ActivateWindow(1170)", "false"),
    (9505, "wheel", "$LOCALIZE[31408]", "ActivateWindow(1171)", "false"),
]
RIGHT = [  # id, icon, label, onclick(s), enabled
    (9511, "view", "$LOCALIZE[31011]", ["SetProperty(groove.pick.from,header,home)", "<include>Lib_PickFocusMusic</include>"],
     "Integer.IsGreater(Container.ViewCount,1)"),
    (9512, "sort", "$LOCALIZE[31010]", ["SendClick(3)"], "Control.IsEnabled(3) + !String.IsEmpty(Container.SortMethod)"),
    (9513, "options", "$LOCALIZE[31600]", ["SetProperty(groove.lib.from,header,home)", "SetFocus(9801,0,absolute)"], "true"),
]
HX0, HPITCH, HY, HICON = 96, 96, 54, 48
RX = [1584, 1680, 1776]
MINI = "[Player.HasAudio + !$EXP[MiniPlayerOff]]"


def header_button(cid, x, icon, label, clicks, nav, enabled="true", label_align="left", current="false", ind=3):
    clicks_x = "".join(NL + t(ind + 1) + (c if c.startswith("<") else f"<onclick>{c}</onclick>") for c in clicks)
    lab_x = x if label_align == "left" else x + HICON - 300
    gsz = 116
    return f"""{t(ind)}<control type="image">
{t(ind + 1)}<left>{x + HICON // 2 - gsz // 2}</left>
{t(ind + 1)}<top>{HY + HICON // 2 - gsz // 2}</top>
{t(ind + 1)}<width>{gsz}</width>
{t(ind + 1)}<height>{gsz}</height>
{t(ind + 1)}<texture colordiffuse="$VAR[focus_glow]">groove/glow_radial.png</texture>
{t(ind + 1)}<visible>Control.HasFocus({cid})</visible>
{t(ind + 1)}<include>Anim_LabelReveal</include>
{t(ind)}</control>
{t(ind)}<control type="button" id="{cid}">
{t(ind + 1)}<left>{x - 16}</left>
{t(ind + 1)}<top>{HY - 16}</top>
{t(ind + 1)}<width>{HICON + 32}</width>
{t(ind + 1)}<height>{HICON + 32}</height>
{t(ind + 1)}<texturefocus />
{t(ind + 1)}<texturenofocus />
{t(ind + 1)}<label />
{t(ind + 1)}<enable>{enabled}</enable>{clicks_x}
{nav}
{t(ind)}</control>
{t(ind)}<control type="image">
{t(ind + 1)}<left>{x}</left>
{t(ind + 1)}<top>{HY}</top>
{t(ind + 1)}<width>{HICON}</width>
{t(ind + 1)}<height>{HICON}</height>
{t(ind + 1)}<texture colordiffuse="$VAR[icon_rest]">icons/{icon}.png</texture>
{t(ind + 1)}<visible>!Control.HasFocus({cid}) + [{enabled}]</visible>
{t(ind)}</control>
{t(ind)}<control type="image">
{t(ind + 1)}<left>{x}</left>
{t(ind + 1)}<top>{HY}</top>
{t(ind + 1)}<width>{HICON}</width>
{t(ind + 1)}<height>{HICON}</height>
{t(ind + 1)}<texture colordiffuse="$VAR[disabled]">icons/{icon}.png</texture>
{t(ind + 1)}<visible>![{enabled}]</visible>
{t(ind + 1)}{static_fade(60)}
{t(ind)}</control>
{t(ind)}<control type="image">
{t(ind + 1)}<left>{x}</left>
{t(ind + 1)}<top>{HY}</top>
{t(ind + 1)}<width>{HICON}</width>
{t(ind + 1)}<height>{HICON}</height>
{t(ind + 1)}<texture colordiffuse="$VAR[ink]">icons/{icon}.png</texture>
{t(ind + 1)}<visible>Control.HasFocus({cid})</visible>
{t(ind)}</control>
{t(ind)}<control type="image">
{t(ind + 1)}<left>{x + HICON // 2 - 4}</left>
{t(ind + 1)}<top>112</top>
{t(ind + 1)}<width>8</width>
{t(ind + 1)}<height>8</height>
{t(ind + 1)}<texture colordiffuse="$VAR[ink]">groove/dot.png</texture>
{t(ind + 1)}<visible>{current}</visible>
{t(ind)}</control>
{t(ind)}<control type="label">
{t(ind + 1)}<left>{lab_x}</left>
{t(ind + 1)}<top>122</top>
{t(ind + 1)}<width>300</width>
{t(ind + 1)}<height>36</height>
{t(ind + 1)}<align>{label_align}</align>
{t(ind + 1)}<aligny>center</aligny>
{t(ind + 1)}<font>font_tray</font>
{t(ind + 1)}<textcolor>$VAR[ink]</textcolor>
{t(ind + 1)}<label>{label}</label>
{t(ind + 1)}<visible>Control.HasFocus({cid})</visible>
{t(ind + 1)}<include>Anim_LabelReveal</include>
{t(ind)}</control>"""


def header():
    o = []
    common = [f'<onup condition="{MINI} + Control.IsVisible(9950)">9950</onup>']
    common += [f'<ondown condition="Control.IsVisible({v})">{v}</ondown>' for v in VIEWS[:-1]] + ["<ondown>50</ondown>"]
    common += [f'<onback condition="Control.IsVisible({v})">{v}</onback>' for v in VIEWS[:-1]] + ["<onback>50</onback>"]
    # the mini player's Down / Back return to the icon you came up from (MiniPlayer.md): record it first
    def to_mini(cid, d="onup"):
        return f'<{d} condition="{MINI} + Control.IsVisible(9950)">SetProperty(groove.mini.from,{cid},home)</{d}>'
    for i, (cid, icon, label, click, cur) in enumerate(LEFT_TABS):
        x = HX0 + i * HPITCH
        nav = [to_mini(cid)] + list(common)
        nav.append("<onleft>noop</onleft>" if i == 0 else f"<onleft>{LEFT_TABS[i - 1][0]}</onleft>")
        if i + 1 < len(LEFT_TABS):
            nav.append(f"<onright>{LEFT_TABS[i + 1][0]}</onright>")
        else:  # skip disabled right-hand icons (disabled icons are never focus targets)
            nav.append(f'<onright condition="{RIGHT[0][4]}">9511</onright>')
            nav.append(f'<onright condition="{RIGHT[1][4]}">9512</onright>')
            nav.append("<onright>9513</onright>")
        o.append(header_button(cid, x, icon, label, [click], t(4) + (NL + t(4)).join(nav), current=cur))
    o.append(image(550, 62, 2, 32, "groove/white.png", "$VAR[line_strong]", ind=3))
    right = []
    for i, (cid, icon, label, clicks, en) in enumerate(RIGHT):
        nav = [to_mini(cid)] + list(common)
        if i == 0:
            nav.append("<onleft>9505</onleft>")
            nav.append(f'<onright condition="{RIGHT[1][4]}">9512</onright>')
            nav.append("<onright>9513</onright>")
        elif i == 1:
            nav.append(f'<onleft condition="{RIGHT[0][4]}">9511</onleft>')
            nav.append("<onleft>9505</onleft>")
            nav.append("<onright>9513</onright>")
        else:
            nav.append(f'<onleft condition="{RIGHT[1][4]}">9512</onleft>')
            nav.append(f'<onleft condition="{RIGHT[0][4]}">9511</onleft>')
            nav.append("<onleft>9505</onleft>")
            nav.append(to_mini(cid, "onright"))
            nav.append(f'<onright condition="{MINI} + Control.IsVisible(9950)">9950</onright>')
            nav.append("<onright>noop</onright>")
        right.append(header_button(cid, RX[i], icon, label, clicks, t(4) + (NL + t(4)).join(nav), en, "right"))
    left_group = "\n".join(o)
    right_group = "\n".join(right)
    return f"""	<!-- Header (screens/MyMusicNav.md): five tabs left, View / Sort / Options right, one word under the focused icon.
	     Individual buttons with explicit navigation (positions never move). The header steps back to 20 % while a view
	     has focus (a Conditional fade, not <visible>, so the numeric onup from the views keeps working, LESSONS Majan 1.0.7).
	     The right group moves 168 px left while the mini player shows (Right from Options reaches it). -->
	<include name="MusicLib_Header">
		<control type="group">
			<animation effect="fade" start="100" end="44" time="200" tween="sine" easing="inout" condition="{ANYVIEW}" reversible="true">Conditional</animation>
			<control type="group">
{left_group}
			</control>
			<control type="group">
				<animation effect="slide" start="0,0" end="-168,0" time="0" condition="{MINI}">Conditional</animation>
{right_group}
			</control>
		</control>
		<control type="button" id="3">
			<description>Sort by (Kodi)</description>
			<include>Groove_Hidden</include>
		</control>
		<control type="button" id="4">
			<description>Sort order (Kodi)</description>
			<include>Groove_Hidden</include>
		</control>
		<!-- Back at a start folder: one press to Home (LESSONS Back audit, Lib_BackHomeNav) -->
		<control type="button" id="9398">
			<include>Groove_Hidden</include>
			<onfocus>ActivateWindow(Home)</onfocus>
			<visible allowhiddenfocus="true">false</visible>
		</control>
	</include>"""


# ---------------------------------------------------------------- 500 cover wall
def view500():
    art = "$INFO[ListItem.Art(thumb)]"
    lab = "$VAR[MusicLib_ItemTitle]"
    sq, rnd = "!Container.Content(artists)", "Container.Content(artists)"
    parent = "ListItem.IsParentFolder"

    def item(focused):
        ind = 5
        diffuse = None if focused else "$VAR[dim_cover]"
        anim = "<include>Anim_FocusBrighten</include>" if focused else ""
        g = []
        if focused:
            g.append(lit_layers(224, 224, f"Control.HasFocus(500) + {sq} + !{parent}", ind, radial=2.4, clamp=44))
            g.append(f"{t(ind)}<control type=\"group\">\n{t(ind + 1)}<visible>{rnd}</visible>\n"
                     + lit_layers(224, 224, f"Control.HasFocus(500) + !{parent}", ind + 1, radial=2.4, round_=True, clamp=44)
                     + f"\n{t(ind)}</control>")
        else:
            g.append(image(-24, -16, 272, 272, "groove/shadow_contact.png", "$VAR[shadow]", f"{sq} + !{parent}", ind=ind,
                           texattr=' border="24,16,24,32"'))
        g.append(f"{t(ind)}<control type=\"group\">\n{t(ind + 1)}<visible>{sq} + !{parent}</visible>\n"
                 + cover(224, 224, art, lab, ind + 1, diffuse, extra=anim) + f"\n{t(ind)}</control>")
        g.append(f"{t(ind)}<control type=\"group\">\n{t(ind + 1)}<visible>{rnd} + !{parent}</visible>\n"
                 + cover(224, 224, art, lab, ind + 1, diffuse, round_=True, extra=anim) + f"\n{t(ind)}</control>")
        # ".." (Kodi's parent item, when the user keeps it on): a back icon, never the text ".."
        g.append(image(80, 80, 64, 64, "icons/back.png", "$VAR[ink]" if focused else "$VAR[icon_rest]", parent, ind=ind))
        if focused:
            g.append(rim(224, 224, f"Control.HasFocus(500) + {sq} + !{parent}", ind, "<include>Anim_FocusRim</include>"))
        zoom = "\n\t\t\t\t\t<include content=\"Anim_FocusCover\"><param name=\"center\" value=\"120,160\"/></include>" if focused else ""
        return f"""				<control type="group">
					<left>8</left>
					<top>48</top>
					<width>224</width>
					<height>224</height>{zoom}
{chr(10).join(g)}
				</control>"""

    return f"""	<!-- 500 Cover wall (View_500_CoverWall.md): 8 columns x 240, covers 224 at cell (8, 48); 3 rows take focus, the
	     4th peeks under the scrim. The focused cover: 1.06 + its light (focused layout = drawn last, over the dimmed
	     neighbours). Artists are round crops. No text in the wall except a coverless item's title. -->
	<include name="MusicLib_View500">
		<control type="panel" id="500">
			<left>0</left>
			<top>110</top>
			<width>1920</width>
			<height>959</height>
			<orientation>vertical</orientation>
			<preloaditems>2</preloaditems>
			<viewtype label="31601">panel</viewtype>
			<ondown>noop</ondown>
{nav_view()}
			<include>Anim_ScrollPanel</include>
			<visible>Container.Content(albums) | Container.Content(artists) | Container.Content(songs)</visible>
			<itemlayout width="240" height="240">
{item(False)}
			</itemlayout>
			<focusedlayout width="240" height="240">
{item(True)}
			</focusedlayout>
		</control>
	</include>"""


def light500():
    """the wall's room light follows the focused cell: Column / Row time-0 slides (LESSONS Majan 1.0.7)"""
    slides = [f'<animation effect="slide" start="0,0" end="{240 * c},0" time="0" condition="Integer.IsEqual(Container(500).Column,{c})">Conditional</animation>'
              for c in range(1, 8)]
    slides += [f'<animation effect="slide" start="0,0" end="0,{240 * r}" time="0" condition="Integer.IsEqual(Container(500).Row,{r})">Conditional</animation>'
               for r in range(1, 4)]
    sl = (NL + t(4)).join(slides)
    return f"""		<control type="group">
			<visible>Control.IsVisible(500)</visible>
			<control type="group">
				{sl}
{wash(500, 120, 270, 900, ind=4)}
			</control>
		</control>"""


def front500():
    """top fade (after a scroll the previous row's covers peek out under the header), bottom scrim (the partial row
    fades into the room) + the caption"""
    return f"""		<control type="group">
			<visible>Control.IsVisible(500)</visible>
			<control type="image">
				<left>0</left>
				<top>0</top>
				<width>1920</width>
				<height>144</height>
				<texture colordiffuse="$VAR[ground_edge]">groove/white.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>144</top>
				<width>1920</width>
				<height>40</height>
				<texture colordiffuse="$VAR[ground_edge]">groove/ramp_v.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>850</top>
				<width>1920</width>
				<height>230</height>
				<texture colordiffuse="$VAR[ground_edge]" flipy="true">groove/ramp_v.png</texture>
			</control>
			<control type="image">
				<left>0</left>
				<top>940</top>
				<width>1920</width>
				<height>140</height>
				<texture colordiffuse="$VAR[ground_edge]">groove/white.png</texture>
				{static_fade(70)}
			</control>
{caption(500, 960, 962, 1728)}
		</control>"""


# ---------------------------------------------------------------- 501 crate dig
def crate_slot(k):
    w = round(500 * (1 - 0.024 * k))
    h = round(0.82 * w)
    x = 960 - w // 2
    y = 262 - 21 * k
    return x, y, w, h


SHADE = {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4, 8: 5, 9: 5}


def view501():
    o = []
    # behind records, far -> near
    for k in range(9, 0, -1):
        x, y, w, h = crate_slot(k)
        c = f"Container(501).ListItemNoWrap({k})"
        art = f"$INFO[{c}.Art(thumb)]"
        cx = 960
        o.append(f"""				<control type="group">
					<left>{x}</left>
					<top>{y}</top>
					<width>{w}</width>
					<height>{h}</height>
					<visible>!String.IsEmpty({c}.Label) + !{c}.IsParentFolder</visible>
					<include content="Anim_PulseSlot">
						<param name="id" value="501"/>
						<param name="ny" value="-21"/>
						<param name="nz" value="97.6"/>
						<param name="py" value="21"/>
						<param name="pz" value="102.4"/>
						<param name="center" value="{w // 2},{h}"/>
						<param name="t" value="180"/>
					</include>
{image(0, 0, w, h, "groove/white.png", f"$VAR[shade_{SHADE[k]}]", f"String.IsEmpty({c}.Art(thumb))", ind=5).replace("groove/white.png", "groove/white.png")}
{image(0, 0, w, h, art, f"$VAR[shade_{SHADE[k]}]", None, aspect=("scale", ' aligny="top"'), bg=True, ind=5)}
{image(0, 0, w, 1, "groove/white.png", "$VAR[line]", None, ind=5)}
				</control>""")
    behind = "\n".join(o)
    # the focused record (500 x 500 at 710, 262), tilted forward about its bottom edge (y 762)
    c = "Container(501).ListItem"
    art = f"$INFO[{c}.Art(thumb)]"
    lit = "Control.HasFocus(501)"
    focus = f"""				<control type="group">
					<include content="Anim_CrateSettle">
						<param name="condition" value="!Control.HasFocus(501)"/>
					</include>
					<control type="group">
						<include content="Anim_CratePulseFocus"><param name="id" value="501"/></include>
						<include content="Anim_CrateLift"><param name="id" value="501"/></include>
						<control type="group">
							<left>710</left>
							<top>262</top>
							<width>500</width>
							<height>500</height>
{lit_layers(500, 500, lit, 7, radial=1.6, in_layout=False)}
{fallback(500, 500, "$INFO[Container(501).ListItem.Label]", f"{c}.Art(thumb)", 7, "font_caption")}
{image(0, 0, 500, 500, art, None, None, "<include>Anim_ArtFadetime</include>", aspect="scale", bg=True, ind=7)}
{rim(500, 500, lit, 7)}
						</control>
					</control>
				</control>"""
    # the record you just flipped falls forward onto the pile (ghost of ListItemNoWrap(-1))
    g = "Container(501).ListItemNoWrap(-1)"
    ghost = f"""				<control type="group">
					<left>710</left>
					<top>262</top>
					<width>500</width>
					<height>500</height>
					<visible>!String.IsEmpty({g}.Label) + !{g}.IsParentFolder</visible>
					<include content="Anim_CrateGhost"><param name="id" value="501"/></include>
{image(0, 0, 500, 500, f"$INFO[{g}.Art(thumb)]", "$VAR[shade_1]", None, aspect="scale", bg=True, ind=5)}
				</control>"""
    slivers = []
    for j, (x, y, w, sh) in enumerate([(702, 756, 515, 1), (697, 765, 525, 2), (692, 774, 535, 3)], 1):
        s = f"Container(501).ListItemNoWrap(-{j})"
        slivers.append(f"""				<control type="group">
					<visible>!String.IsEmpty({s}.Label) + !{s}.IsParentFolder</visible>
					<include content="Anim_PulseSlot">
						<param name="id" value="501"/>
						<param name="ny" value="-9"/>
						<param name="py" value="9"/>
						<param name="t" value="180"/>
					</include>
{image(x, y, w, 60, "$VAR[Tex_SleeveBack]", f"$VAR[shade_{sh}]", None, aspect="stretch", ind=5)}
				</control>""")
    sliv = "\n".join(reversed(slivers))
    return f"""	<!-- 501 Crate dig (View_501_CrateDig.md, MOTION 5.7): the invisible driver list 501 owns focus and the items;
	     static slots show Container(501).ListItemNoWrap(k). One camera for the whole crate (LESSONS Fold). -->
	<include name="MusicLib_View501">
		<control type="fixedlist" id="501">
			<left>954</left>
			<top>1072</top>
			<width>13</width>
			<height>1</height>
			<orientation>horizontal</orientation>
			<focusposition>3</focusposition>
			<movement>0</movement>
			<scrolltime>0</scrolltime>
			<preloaditems>2</preloaditems>
			<viewtype label="31602">wrap</viewtype>
			<ondown>noop</ondown>
{nav_view()}
			<visible>Container.Content(albums)</visible>
			<itemlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true" colordiffuse="clear">$INFO[ListItem.Art(thumb)]</texture></control>
			</itemlayout>
			<focusedlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true" colordiffuse="clear">$INFO[ListItem.Art(thumb)]</texture></control>
			</focusedlayout>
		</control>
	</include>
	<include name="MusicLib_Stage501">
		<control type="group">
			<visible>Control.IsVisible(501)</visible>
			<control type="group">
				<camera x="960" y="480"/>
				<control type="image">
					<left>400</left>
					<top>572</top>
					<width>1120</width>
					<height>330</height>
					<texture>$VAR[Tex_CrateBack]</texture>
				</control>
{behind}
{focus}
{ghost}
{sliv}
				<control type="image">
					<left>400</left>
					<top>782</top>
					<width>1120</width>
					<height>190</height>
					<texture>$VAR[Tex_CrateFront]</texture>
				</control>
			</control>
{caption(501, 960, 990, 1728)}
		</control>
	</include>"""


# ---------------------------------------------------------------- 502 shelf of spines
SP_W, SP_P, SP_Y, SP_H = 40, 42, 300, 500
# Spine slots drawn left / right of the face-out cover. -19 (x -62..-22) was fully off-screen at rest and only peeked
# 20 px in during a Next pulse: dropped (Shield FPS, DEVICE_AUDIT m4). +16 stays: without it a Previous pulse opens a
# 48 px gap at the right edge.
LEFT_N, RIGHT_N = 18, 16
# the helper's spine strips are published and readable (HELPER_API 2)
SPINES_READY = ("$EXP[HasGrooveHelper] + Skin.HasSetting(Groove.SpinesReady) + "
                "!String.IsEmpty(Window(Home).Property(Groove.Spines.Path))")


def spine_x(k):
    return 694 - SP_P * (-k - 1) if k < 0 else 1286 + SP_P * (k - 1)


def spine(k):
    x = spine_x(k)
    c = f"Container(502).ListItemNoWrap({k})"
    helper = SPINES_READY
    shade = "shade_3" if abs(k) > 1 else "shade_2"
    lean = ""
    if k == -1:
        lean = f"""
					<include content="Anim_SpineLean"><param name="id" value="502"/><param name="angle" value="-5"/><param name="center" value="{x + SP_W},{SP_Y + SP_H}"/></include>"""
    elif k == 1:
        lean = f"""
					<include content="Anim_SpineLean"><param name="id" value="502"/><param name="angle" value="5"/><param name="center" value="{x},{SP_Y + SP_H}"/></include>"""
    cx, cy = x + SP_W // 2, SP_Y + SP_H // 2
    label = f"$INFO[{c}.Label]"
    lab = lambda colour, vis: f"""					<control type="label">
						<left>{cx - 232}</left>
						<top>{cy - 20}</top>
						<width>464</width>
						<height>40</height>
						<aligny>center</aligny>
						<font>font_spine</font>
						<textcolor>{colour}</textcolor>
						<label>{label}</label>
						<visible>{vis}</visible>
						<animation effect="rotate" end="90" center="{cx},{cy}" time="0" condition="true">Conditional</animation>
					</control>"""
    on_pale = f"{helper} + Skin.HasSetting(groove.light)"
    return f"""				<control type="group">
					<visible>!String.IsEmpty({c}.Label) + !{c}.IsParentFolder</visible>{lean}
{image(x, SP_Y, SP_W, SP_H, "groove/white.png", "$VAR[surface_raised]", None, ind=5)}
{image(x, SP_Y, SP_W, SP_H, f"$INFO[{c}.Art(thumb)]", f"$VAR[{shade}]", f"![{helper}]", aspect=("scale", ' align="left"'), bg=True, ind=5)}
{image(x, SP_Y, SP_W, SP_H, f"$INFO[Window(Home).Property(Groove.Spines.Path)]$VAR[Groove_RoomDir]/$INFO[{c}.DBID].png", f"$VAR[{shade}]", helper, aspect="stretch", ind=5)}
{image(x, SP_Y, SP_W, SP_H, "groove/spine_scrim.png", None, f"![{on_pale}]", aspect="stretch", ind=5)}
{image(x, SP_Y, SP_W, SP_H, "groove/spine_edge.png", None, None, ind=5, texattr=' border="3,0,3,0"')}
{lab("white_90", f"![{on_pale}]")}
{lab("$VAR[ink]", on_pale)}
				</control>"""


def view502():
    left = "\n".join(spine(k) for k in range(-LEFT_N, 0))
    right = "\n".join(spine(k) for k in range(RIGHT_N, 0, -1))
    c = "Container(502).ListItem"
    lit = "Control.HasFocus(502)"
    pulse = lambda: """					<include content="Anim_PulseSlot">
						<param name="id" value="502"/>
						<param name="nx" value="42"/>
						<param name="px" value="-42"/>
						<param name="t" value="180"/>
					</include>"""
    return f"""	<!-- 502 Shelf of spines (View_502_ShelfOfSpines.md, MOTION 5.8): driver 502 (36 items drawn, focusposition 19)
	     + static spines read from Container(502).ListItemNoWrap(k) (the motion-designer's static-slot advice: a wider
	     focused layout would reflow the row on every press). The face-out cover sits in the gap and pulls out
	     (rotatey about its left edge) on every move. Spines: helper colour strip when the helper has built them
	     (Groove.SpinesReady), else the cover's own left edge (aspectratio scale + align left) under a dark scrim.
	     Cost (Shield, DEVICE_AUDIT m4): with helper spines no cover is decoded for a spine (the strip layer and the
	     driver's 1 px art draws are off; only the focused item's cover loads, for the face-out). A spine without a
	     helper file then shows the plain raised fill + its title. -->
	<include name="MusicLib_View502">
		<control type="fixedlist" id="502">
			<left>942</left>
			<top>1072</top>
			<width>36</width>
			<height>1</height>
			<orientation>horizontal</orientation>
			<focusposition>19</focusposition>
			<movement>0</movement>
			<scrolltime>0</scrolltime>
			<preloaditems>2</preloaditems>
			<viewtype label="31603">bigwrap</viewtype>
			<ondown>noop</ondown>
{nav_view()}
			<visible>Container.Content(albums)</visible>
			<itemlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true" colordiffuse="clear">$INFO[ListItem.Art(thumb)]</texture><visible>![{SPINES_READY}]</visible></control>
			</itemlayout>
			<focusedlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true" colordiffuse="clear">$INFO[ListItem.Art(thumb)]</texture></control>
			</focusedlayout>
		</control>
	</include>
	<include name="MusicLib_Stage502">
		<control type="group">
			<visible>Control.IsVisible(502)</visible>
			<control type="group">
{pulse()}
{left}
			</control>
			<control type="group">
{pulse()}
{right}
			</control>
			<control type="image">
				<left>0</left>
				<top>800</top>
				<width>1920</width>
				<height>94</height>
				<texture>$VAR[Tex_Shelf]</texture>
			</control>
			<control type="group">
				<camera x="1010" y="576"/>
				<include content="Anim_SpinePull"><param name="id" value="502"/><param name="hinge" value="760"/></include>
				<control type="group">
					<left>760</left>
					<top>326</top>
					<width>500</width>
					<height>500</height>
{lit_layers(500, 500, lit, 5, radial=1.6, in_layout=False)}
{fallback(500, 500, f"$INFO[{c}.Label]", f"{c}.Art(thumb)", 5, "font_caption")}
{image(0, 0, 500, 500, f"$INFO[{c}.Art(thumb)]", None, None, "<include>Anim_ArtFadetime</include>", aspect="scale", bg=True, ind=5)}
{rim(500, 500, lit, 5)}
				</control>
			</control>
{caption(502, 1010, 866, 1248)}
		</control>
	</include>"""


# ---------------------------------------------------------------- the arc (503 and Custom_1170)
ARC = {0: (750, 220, 420), -1: (445, 280, 250), 1: (1225, 280, 250), -2: (250, 230, 160), 2: (1510, 230, 160),
       -3: (115, 178, 100), 3: (1705, 178, 100), -4: (-60, 150, 64), 4: (1916, 150, 64)}
ARC_ALPHA = {0: 100, 1: 55, 2: 38, 3: 24}


def arc_center(k, dy):
    x, y, s = ARC[k]
    return x + s / 2, y + dy + s / 2, s


def arc(id_, dy, nav, content="", extra_vis="true", title_y=670, title=None, sub=None):
    """Groove_Arc (View_503_Orbit.md): 7 static slots on a curve fed by Container(id).ListItemNoWrap(-3..3) from an
    invisible driver fixedlist; slots glide one position per move (Anim_PulseSlot from the neighbour's pose)."""
    slots = []
    for k in (-3, 3, -2, 2, -1, 1):
        x, y, s = ARC[k]
        y += dy
        cx, cy, _ = arc_center(k, dy)
        nx_, ny_, ns = arc_center(k + 1, dy)
        px_, py_, ps = arc_center(k - 1, dy)
        c = f"Container({id_}).ListItemNoWrap({k})"
        slots.append(f"""			<control type="group">
				<visible>!String.IsEmpty({c}.Label) + !{c}.IsParentFolder</visible>
				<include content="Anim_PulseSlot">
					<param name="id" value="{id_}"/>
					<param name="nx" value="{round(nx_ - cx)}"/>
					<param name="ny" value="{round(ny_ - cy)}"/>
					<param name="nz" value="{round(100 * ns / s, 1)}"/>
					<param name="px" value="{round(px_ - cx)}"/>
					<param name="py" value="{round(py_ - cy)}"/>
					<param name="pz" value="{round(100 * ps / s, 1)}"/>
					<param name="center" value="{round(cx)},{round(cy)}"/>
				</include>
				<control type="group">
					<left>{x}</left>
					<top>{y}</top>
					<width>{s}</width>
					<height>{s}</height>
					{static_fade(ARC_ALPHA[abs(k)])}
{image(-12, -8, s + 24, s + 32, "groove/shadow_contact.png", "$VAR[shadow]", None, ind=5, texattr=' border="24,16,24,32"')}
{fallback(s, s, f"$INFO[{c}.Label]", f"{c}.Art(thumb)", 5)}
{image(0, 0, s, s, f"$INFO[{c}.Art(thumb)]", None, None, aspect="scale", bg=True, ind=5)}
				</control>
			</control>""")
    x, y, s = ARC[0]
    y += dy
    cx, cy, _ = arc_center(0, dy)
    nx_, ny_, ns = arc_center(1, dy)
    px_, py_, ps = arc_center(-1, dy)
    c = f"Container({id_}).ListItem"
    lit = f"Control.HasFocus({id_})"
    centre = f"""			<control type="group">
				<visible>!String.IsEmpty({c}.Label)</visible>
				<include content="Anim_PulseSlot">
					<param name="id" value="{id_}"/>
					<param name="nx" value="{round(nx_ - cx)}"/>
					<param name="ny" value="{round(ny_ - cy)}"/>
					<param name="nz" value="{round(100 * ns / s, 1)}"/>
					<param name="px" value="{round(px_ - cx)}"/>
					<param name="py" value="{round(py_ - cy)}"/>
					<param name="pz" value="{round(100 * ps / s, 1)}"/>
					<param name="center" value="{round(cx)},{round(cy)}"/>
				</include>
				<animation effect="fade" start="100" end="72" time="200" condition="!{lit}" reversible="true">Conditional</animation>
				<control type="group">
					<left>{x}</left>
					<top>{y}</top>
					<width>{s}</width>
					<height>{s}</height>
{lit_layers(s, s, lit, 5, radial=1.9, in_layout=False)}
{fallback(s, s, f"$INFO[{c}.Label]", f"{c}.Art(thumb)", 5, "font_caption")}
{image(0, 0, s, s, f"$INFO[{c}.Art(thumb)]", None, None, "<include>Anim_ArtFadetime</include>", aspect="scale", bg=True, ind=5)}
{rim(s, s, lit, 5)}
				</control>
			</control>"""
    texts = f"""			<control type="group">
				<visible>!Container({id_}).Scrolling</visible>
				<include>Anim_CaptionRest</include>
				<control type="label">
					<left>460</left>
					<top>{title_y + dy}</top>
					<width>1000</width>
					<height>40</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_caption</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>{title or f"$INFO[{c}.Label]"}</label>
				</control>
				<control type="label">
					<left>460</left>
					<top>{title_y + 44 + dy}</top>
					<width>1000</width>
					<height>36</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_caption_light</font>
					<textcolor>$VAR[ink2]</textcolor>
					<label>{sub or f"$INFO[{c}.Artist]"}</label>
				</control>
			</control>"""
    driver = f"""		<control type="fixedlist" id="{id_}">
			<left>957</left>
			<top>1072</top>
			<width>7</width>
			<height>1</height>
			<orientation>horizontal</orientation>
			<focusposition>3</focusposition>
			<movement>0</movement>
			<scrolltime>0</scrolltime>
			<preloaditems>2</preloaditems>
{nav}
			<itemlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true" colordiffuse="clear">$INFO[ListItem.Art(thumb)]</texture></control>
			</itemlayout>
			<focusedlayout width="1" height="1">
				<control type="image"><left>0</left><top>0</top><width>1</width><height>1</height><texture background="true" colordiffuse="clear">$INFO[ListItem.Art(thumb)]</texture></control>
			</focusedlayout>{content}
		</control>"""
    stage = f"""		<control type="group">
			<visible>{extra_vis}</visible>
{chr(10).join(slots)}
{centre}
{texts}
		</control>"""
    return driver, stage


def view503():
    nav = f"""			<viewtype label="31604">wide</viewtype>
			<ondown>noop</ondown>
{nav_view()}
			<visible>Container.Content(albums) | Container.Content(artists) | Container.Content(songs)</visible>"""
    driver, stage = arc(503, 120, nav, extra_vis="Control.IsVisible(503)", title="$VAR[MusicLib_Title503]",
                        sub="$VAR[MusicLib_Sub503]")
    return f"""	<!-- 503 Orbit (View_503_Orbit.md): the shared arc, 120 px lower than in the Time machine (no timeline below). -->
	<include name="MusicLib_View503">
{driver}
	</include>
	<include name="MusicLib_Stage503">
{stage}
	</include>"""


# ---------------------------------------------------------------- 50 list
def list_row(focused):
    ind = 4
    ink = "$VAR[ink]" if focused else "$VAR[ink2]"
    o = []
    if focused:
        o.append(image(-12, 0, 784, 64, "groove/white.png", "$VAR[focus_fill]", "Control.HasFocus(50)", ind=ind))
    thumbs = "[Container.Content(albums) | Container.Content(artists) | [Container.Content(songs) + !$EXP[MusicLib_Tracklist]]] + !ListItem.IsParentFolder"
    o.append(image(0, 8, 48, 48, "$INFO[ListItem.Art(thumb)]", None, f"{thumbs} + !Container.Content(artists)",
                   aspect="scale", bg=True, ind=ind))
    o.append(image(0, 8, 48, 48, "$INFO[ListItem.Art(thumb)]", None, f"{thumbs} + Container.Content(artists)",
                   aspect="scale", bg=True, ind=ind, texattr=' diffuse="groove/disc_mask.png"'))
    o.append(image(8, 16, 32, 32, "icons/back.png", ink, "ListItem.IsParentFolder", ind=ind))
    o.append(image(16, 20, 24, 24, "icons/play.png", ink, "$EXP[MusicLib_Tracklist] + ListItem.IsPlaying", ind=ind))
    o.append(f"""{t(ind)}<control type="label">
{t(ind + 1)}<left>0</left>
{t(ind + 1)}<top>0</top>
{t(ind + 1)}<width>48</width>
{t(ind + 1)}<height>64</height>
{t(ind + 1)}<align>right</align>
{t(ind + 1)}<aligny>center</aligny>
{t(ind + 1)}<font>font_small</font>
{t(ind + 1)}<textcolor>$VAR[ink2]</textcolor>
{t(ind + 1)}<selectedcolor>$VAR[ink2]</selectedcolor>
{t(ind + 1)}<label>$INFO[ListItem.TrackNumber]</label>
{t(ind + 1)}<visible>$EXP[MusicLib_Tracklist] + !ListItem.IsPlaying + !ListItem.IsParentFolder</visible>
{t(ind)}</control>""")
    has_lead = f"[{thumbs}] | $EXP[MusicLib_Tracklist] | ListItem.IsParentFolder"
    for vis, x in ((has_lead, 64), (f"!{'[' + has_lead + ']'}", 0)):
        o.append(f"""{t(ind)}<control type="label">
{t(ind + 1)}<left>{x}</left>
{t(ind + 1)}<top>0</top>
{t(ind + 1)}<width>{624 - x if x == 0 else 560}</width>
{t(ind + 1)}<height>64</height>
{t(ind + 1)}<aligny>center</aligny>
{t(ind + 1)}<font>font_label</font>
{t(ind + 1)}<textcolor>{ink}</textcolor>
{t(ind + 1)}<selectedcolor>{ink}</selectedcolor>
{t(ind + 1)}<label>$VAR[MusicLib_RowLabel]</label>
{t(ind + 1)}<visible>{vis}</visible>
{t(ind)}</control>""")
    o.append(f"""{t(ind)}<control type="label">
{t(ind + 1)}<left>624</left>
{t(ind + 1)}<top>0</top>
{t(ind + 1)}<width>136</width>
{t(ind + 1)}<height>64</height>
{t(ind + 1)}<align>right</align>
{t(ind + 1)}<aligny>center</aligny>
{t(ind + 1)}<font>font_small</font>
{t(ind + 1)}<textcolor>$VAR[ink2]</textcolor>
{t(ind + 1)}<selectedcolor>$VAR[ink2]</selectedcolor>
{t(ind + 1)}<label>$INFO[ListItem.Label2]</label>
{t(ind)}</control>""")
    return "\n".join(o)


def view50():
    art = "$INFO[Container(50).ListItem.Art(thumb)]"
    hasart = "!String.IsEmpty(Container(50).ListItem.Art(thumb)) + !Container(50).ListItem.IsParentFolder"
    lit = "Control.HasFocus(50)"
    return f"""	<!-- 50 List (View_50_List.md): one line per item, 13 rows of 64; the focused item's art lit at the right.
	     Songs of one album read as a tracklist (numbers, no thumbs). Left / Right open the Library panel. -->
	<include name="MusicLib_View50">
		<control type="list" id="50">
			<left>96</left>
			<top>150</top>
			<width>760</width>
			<height>864</height>
			<orientation>vertical</orientation>
			<pagecontrol>60</pagecontrol>
			<preloaditems>2</preloaditems>
			<viewtype label="535">list</viewtype>
			<ondown>noop</ondown>
{nav_view()}
			<include>Anim_ScrollRow</include>
			<itemlayout width="760" height="64">
{list_row(False)}
			</itemlayout>
			<focusedlayout width="760" height="64">
{list_row(True)}
			</focusedlayout>
		</control>
		<control type="scrollbar" id="60">
			<left>872</left>
			<top>150</top>
			<width>2</width>
			<height>832</height>
			<texturesliderbackground colordiffuse="$VAR[line]">groove/white.png</texturesliderbackground>
			<texturesliderbar colordiffuse="$VAR[ink2]">groove/white.png</texturesliderbar>
			<texturesliderbarfocus colordiffuse="$VAR[ink]">groove/white.png</texturesliderbarfocus>
			<orientation>vertical</orientation>
			<showonepage>false</showonepage>
			<onleft>50</onleft>
			<onright>50</onright>
			<visible>Control.IsVisible(50)</visible>
		</control>
	</include>
	<include name="MusicLib_Stage50">
		<control type="group">
			<visible>Control.IsVisible(50)</visible>
			<control type="image">
				<left>96</left>
				<top>982</top>
				<width>780</width>
				<height>98</height>
				<texture colordiffuse="$VAR[ground_edge]" flipy="true">groove/ramp_v.png</texture>
			</control>
			<control type="group">
				<left>1144</left>
				<top>200</top>
				<width>560</width>
				<height>560</height>
				<visible>{hasart}</visible>
				<control type="group">
					<visible>!Container.Content(artists)</visible>
{lit_layers(560, 560, "true", 5, radial=1.6, in_layout=False)}
{image(0, 0, 560, 560, art, None, None, "<include>Anim_ArtFadetime</include>", aspect="scale", bg=True, ind=5)}
{rim(560, 560, lit, 5)}
				</control>
				<control type="group">
					<visible>Container.Content(artists)</visible>
{lit_layers(560, 560, "true", 5, radial=1.6, round_=True, in_layout=False)}
{image(0, 0, 560, 560, art, None, None, "<include>Anim_ArtFadetime</include>", aspect="scale", bg=True, ind=5, texattr=' diffuse="groove/disc_mask.png"')}
				</control>
			</control>
			<control type="group">
				<visible>!Container(50).ListItem.IsParentFolder + !String.IsEmpty(Container(50).ListItem.Label) + {hasart}</visible>
				<control type="label">
					<left>1084</left>
					<top>800</top>
					<width>680</width>
					<height>44</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_caption</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$INFO[Container(50).ListItem.Title]$INFO[Container(50).ListItem.Label,,]</label>
					<visible>String.IsEmpty(Container(50).ListItem.Title)</visible>
				</control>
				<control type="label">
					<left>1084</left>
					<top>800</top>
					<width>680</width>
					<height>44</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_caption</font>
					<textcolor>$VAR[ink]</textcolor>
					<label>$INFO[Container(50).ListItem.Title]</label>
					<visible>!String.IsEmpty(Container(50).ListItem.Title)</visible>
				</control>
				<control type="label">
					<left>1084</left>
					<top>844</top>
					<width>680</width>
					<height>40</height>
					<align>center</align>
					<aligny>center</aligny>
					<font>font_caption_light</font>
					<textcolor>$VAR[ink2]</textcolor>
					<label>$VAR[MusicLib_ListMeta]</label>
				</control>
			</control>
		</control>
	</include>"""


# ---------------------------------------------------------------- the whole file
def main():
    metas = "\n".join(meta_var(i) for i in (500, 501, 502))
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_music_views.py - edit the generator, then re-run.
     Groove music library: header + views 500 / 501 / 502 / 503 / 50 + their shared caption and room light.
     MyMusicNav.xml places them; the Library panel / view picker are Includes_Library.xml. -->
<includes>
	<expression name="MusicLib_TabAlbums">String.StartsWith(Container.FolderPath,musicdb://albums/) | String.StartsWith(Container.FolderPath,musicdb://recentlyaddedalbums/) | String.StartsWith(Container.FolderPath,musicdb://compilations/)</expression>
	<expression name="MusicLib_TabArtists">String.StartsWith(Container.FolderPath,musicdb://artists/)</expression>
	<expression name="MusicLib_TabSongs">String.StartsWith(Container.FolderPath,musicdb://songs/)</expression>
	<!-- songs of one album (drilled from an album or an artist's album): a tracklist with numbers, no thumbs -->
	<expression name="MusicLib_Tracklist">Container.Content(songs) + [String.StartsWith(Container.FolderPath,musicdb://albums/) | String.StartsWith(Container.FolderPath,musicdb://artists/)]</expression>
{metas}
	<variable name="MusicLib_ItemTitle">
		<value condition="String.IsEqual(ListItem.DBType,song) + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="MusicLib_Title503">
		<value condition="String.IsEqual(Container(503).ListItem.DBType,song) + !String.IsEmpty(Container(503).ListItem.Title)">$INFO[Container(503).ListItem.Title]</value>
		<value>$INFO[Container(503).ListItem.Label]</value>
	</variable>
	<variable name="MusicLib_Sub503">
		<value condition="String.IsEqual(Container(503).ListItem.DBType,artist)">$INFO[Container(503).ListItem.Genre]</value>
		<value condition="String.IsEqual(Container(503).ListItem.DBType,song)">$INFO[Container(503).ListItem.Artist]$INFO[Container(503).ListItem.Album,  ·  ,]</value>
		<value>$INFO[Container(503).ListItem.Artist]</value>
	</variable>
	<variable name="MusicLib_RowLabel">
		<value condition="ListItem.IsParentFolder">$LOCALIZE[31605]</value>
		<value condition="Container.Content(songs) + $EXP[MusicLib_Tracklist] + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]</value>
		<value condition="Container.Content(songs) + !String.IsEmpty(ListItem.Title)">$INFO[ListItem.Title]$INFO[ListItem.Artist,  ·  ,]</value>
		<value>$INFO[ListItem.Label]</value>
	</variable>
	<variable name="MusicLib_ListMeta">
		<value condition="Container.Content(artists)">$INFO[Container(50).ListItem.Genre]</value>
		<value condition="!String.IsEmpty(Container(50).ListItem.Artist) + !String.IsEmpty(Container(50).ListItem.Year)">$INFO[Container(50).ListItem.Artist]  ·  $INFO[Container(50).ListItem.Year]</value>
		<value condition="!String.IsEmpty(Container(50).ListItem.Artist)">$INFO[Container(50).ListItem.Artist]</value>
		<value>$INFO[Container(50).ListItem.Year]</value>
	</variable>
	<variable name="MusicLib_ViewName">
		<value condition="Control.IsVisible(500)">$LOCALIZE[31601]</value>
		<value condition="Control.IsVisible(501)">$LOCALIZE[31602]</value>
		<value condition="Control.IsVisible(502)">$LOCALIZE[31603]</value>
		<value condition="Control.IsVisible(503)">$LOCALIZE[31604]</value>
		<value>$LOCALIZE[535]</value>
	</variable>
	<variable name="MusicLib_Section">
		<value condition="Container.Content(artists)">$LOCALIZE[133]</value>
		<value condition="Container.Content(songs)">$LOCALIZE[134]</value>
		<value condition="Container.Content(albums)">$LOCALIZE[132]</value>
		<value>$LOCALIZE[31400]</value>
	</variable>

{header()}

	<!-- The room light behind each view (window level, under the views): wash of the focused item -->
	<include name="MusicLib_Light">
{light500()}
		<control type="group">
			<visible>Control.IsVisible(501)</visible>
{wash(501, 960, 512, 1500, ind=3)}
		</control>
		<control type="group">
			<visible>Control.IsVisible(502)</visible>
{wash(502, 1010, 576, 1500, ind=3)}
		</control>
		<control type="group">
			<visible>Control.IsVisible(503)</visible>
{wash(503, 960, 550, 1300, ind=3)}
		</control>
		<control type="group">
			<visible>Control.IsVisible(50) + !String.IsEmpty(Container(50).ListItem.Art(thumb))</visible>
{wash(50, 1424, 480, 1500, ind=3)}
		</control>
	</include>

{view500()}
	<include name="MusicLib_Front500">
{front500()}
	</include>
{view501()}
{view502()}
{view503()}
{view50()}

	<!-- Empty folder: the view can't take focus, so the header has it (MyMusicNav onload). -->
	<include name="MusicLib_Empty">
		<control type="label">
			<left>0</left>
			<top>516</top>
			<width>1920</width>
			<height>48</height>
			<align>center</align>
			<aligny>center</aligny>
			<font>font_caption</font>
			<textcolor>$VAR[ink2]</textcolor>
			<label>$LOCALIZE[31606]</label>
			<visible>Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating</visible>
		</control>
	</include>
</includes>
"""
    xml = xml.replace("\t\t\t\t<control", "\t\t\t\t<control")
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, len(xml.splitlines()), "lines")


if __name__ == "__main__":
    main()
