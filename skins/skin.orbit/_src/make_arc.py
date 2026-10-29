"""Generate 1080i/Includes_Arc.xml: Orbit's signature mechanics, computed from the mockup geometry.

1. The ARC (OrbitHome / OrbitArc mockups). A hidden 1px fixedlist owns focus and the items; 11 slots
   (offsets -5..+5, the outer two mostly off-screen) are ordinary image controls placed on a circle
   and show Container(id).ListItemNoWrap(k).Art(...). Slot k: centre on the circle at arc length
   c_k from the lens (9 o'clock), height H_k, rotation = its angle (max 18 deg), brightness B_k.

   Motion: Container(id).OnNext / OnPrevious is a ONE-FRAME pulse in Kodi 21 (GUIControlsGUIInfo
   m_containerMoves, cleared at the end of every Application::Render). So each slot carries
   Conditional animations on !Container(id).OnNext / !OnPrevious with reversible="false": the
   condition drops for one frame on a move (animation reset) and the animation replays from the
   neighbour slot's pose (slide + zoom + rotate about the slot centre) back to its own pose.
   CAnimation::SetInitialCondition applies the end state on window load, so nothing plays on open.
   Brightness rides the same animations with fadediffuse (colour multiply, never above 1): the
   animation whose source slot is brighter holds the slot's base brightness, the other holds white.

2. The DIAL (Home section ring): 5 labels at -64/-32/0/32/64 deg on a ring centred (200,540),
   showing Container(9000).ListItem(k) of a wraplist; moves rotate the labels about the ring centre.

3. The DIAL LIST (rows on a shallow circle bulging right): text rows for lists (files, episodes,
   songs, settings). Same pulse mechanics, rows rotate with the circle.

4. Clock rotation includes: rotate a group to the current time on a 12-hour face
   (24 hour conditions x 30 deg + 60 minute conditions x 0.5 deg), used by the runtime sector.

Usage: python skins/skin.orbit/_src/make_arc.py
"""
import math
import re
from pathlib import Path

from make_textures import ROUND_SHADOW_D  # 0.9.20: round shadow sizes

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "Includes_Arc.xml"

T_MOVE = 180          # ms, slide time
T_MOVE_RM = 0         # reduce motion

B = [1.0, 0.62, 0.44, 0.32, 0.22, 0.15]


def hexgray(b):
    v = max(0, min(255, int(round(255 * b))))
    return "ff%02x%02x%02x" % (v, v, v)


def hexalpha(b):
    """white at alpha b: text rows fade INTO the blue ground instead of turning grey-black on it
    (0.9.4: far settings / dial-list rows read dark-on-dark with the grey multiply)"""
    v = max(0, min(255, int(round(255 * b))))
    return "%02xffffff" % v


def arc_slots(cx, cy, R, F, H, aspect, extra_h, gap=18, rotmax=30.0):
    """Return dict k -> (x, y, w, h, kodi_rot) for k in -5..5.
    0.9.1: posters are spaced evenly along the circle with a fixed gap (no overlap): the arc
    length between neighbours = half of each poster's height + gap (posters are rotated to the
    tangent, so height is their extent along the arc). Rotation = tangent angle, max rotmax.
    (F is kept for signature compatibility and ignored.)"""
    Hs = list(H) + [extra_h]
    c = [0.0]
    for k in range(1, 6):
        c.append(c[k - 1] + (Hs[k - 1] + Hs[k]) / 2 + gap)
    slots = {}
    for k in range(-5, 6):
        a = abs(k)
        th = (1 if k > 0 else -1 if k < 0 else 0) * c[a] / R
        h = Hs[a]
        w = round(h * aspect)
        x = cx - R * math.cos(th)
        y = cy + R * math.sin(th)
        rot = max(-rotmax, min(rotmax, th * 180 / math.pi))
        slots[k] = (x, y, w, h, rot)  # Kodi: positive = counter-clockwise
    return slots


def wrapify(lines):
    """Home arcs wrap (wraplist): ListItem(k) instead of ListItemNoWrap(k), and a slot only shows
    when the list is long enough that no item appears twice (NumItems > 2|k|)."""
    t = chr(10).join(lines).replace("ListItemNoWrap(", "ListItem(")
    t = re.sub(r"<visible>!String.IsEmpty\(Container\(\$PARAM\[id\]\)\.ListItem\((-?\d+)\)\.Label\)</visible>",
               lambda m: f"<visible>!String.IsEmpty(Container($PARAM[id]).ListItem({m.group(1)}).Label) + "
                         f"Integer.IsGreater(Container($PARAM[id]).NumItems,{2 * abs(int(m.group(1)))})</visible>", t)
    return t.split(chr(10))


def f1(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-6 else str(int(round(v)))


def move_anims(slot, src, cond, indent, extra=""):
    """Animation taking the slot from the src pose back to its own pose."""
    x, y, w, h, r = slot
    sx, sy, sw, sh, sr = src
    zoom = sh / h * 100
    dr = sr - r
    t = "$PARAM[t]"
    out = [f'{indent}<animation type="Conditional" condition="!Container($PARAM[id]).{cond}" reversible="false">',
           f'{indent}\t<effect type="slide" start="{f1(sx - x)},{f1(sy - y)}" end="0,0" time="{t}" tween="cubic" easing="out"/>',
           f'{indent}\t<effect type="zoom" start="{f1(zoom)}" end="100" center="{f1(x)},{f1(y)}" time="{t}" tween="cubic" easing="out"/>']
    if abs(dr) > 0.01:
        out.append(f'{indent}\t<effect type="rotate" start="{f1(dr)}" end="0" center="{f1(x)},{f1(y)}" time="{t}" tween="cubic" easing="out"/>')
    out.append(f"{indent}</animation>")
    return out


def bright_anims(k, cond_next_src, cond_prev_src, indent):
    """fadediffuse pair: the direction whose source is brighter holds the base brightness."""
    a = abs(k)
    base = B[a]
    out = []
    for cond, src in (("OnNext", cond_next_src), ("OnPrevious", cond_prev_src)):
        sb = B[min(abs(src), 5)]
        if sb >= base and a != 0:
            start, end = hexgray(sb), hexgray(base)       # holder: ends at the base brightness
        else:
            start, end = hexgray(min(1.0, sb / base)), "ffffffff"  # identity holder
        out.append(f'{indent}<animation type="Conditional" condition="!Container($PARAM[id]).{cond}" reversible="false">')
        out.append(f'{indent}\t<effect type="fadediffuse" start="{start}" end="{end}" time="$PARAM[t]" tween="cubic" easing="out"/>')
        out.append(f"{indent}</animation>")
    return out


def poster_arc(name, slots, art_var, mask, desc, shadows=2, lens_extra=True, circle_cond=None, icon_mode=False,
               song_titles=False):
    """Emit an include drawing the arc for container $PARAM[id]."""
    L = [f"\t<!-- {desc} -->",
         f'\t<include name="{name}">',
         '\t\t<param name="t">' + str(T_MOVE) + '</param>',
         "\t\t<definition>",
         "\t\t\t<control type=\"group\">",
         "\t\t\t\t<left>0</left>", "\t\t\t\t<top>0</top>"]
    order = [5, -5, 4, -4, 3, -3, 2, -2, 1, -1, 0]  # far slots first (z-order: lens on top)
    for k in order:
        x, y, w, h, r = slots[k]
        nxt = slots.get(k + 1) if k < 5 else (x, y, w, h, r)
        prv = slots.get(k - 1) if k > -5 else (x, y, w, h, r)
        ind = "\t\t\t\t"
        kk = f"{k}"
        L.append(f"{ind}<!-- slot {k:+d}: centre {x:.0f},{y:.0f} size {w}x{h} rot {r:.1f} -->")
        L.append(f'{ind}<control type="group">')
        L.append(f"{ind}\t<left>0</left>")
        L.append(f"{ind}\t<top>0</top>")
        L.append(f"{ind}\t<visible>!String.IsEmpty(Container($PARAM[id]).ListItemNoWrap({kk}).Label)</visible>")
        if k < 5:
            L += move_anims(slots[k], nxt, "OnNext", ind + "\t")
        else:
            L += move_anims(slots[k], (x, y + (y - slots[4][1]) * 0.6, w, h * 0.8, r), "OnNext", ind + "\t")
        if k > -5:
            L += move_anims(slots[k], prv, "OnPrevious", ind + "\t")
        else:
            L += move_anims(slots[k], (x, y + (y - slots[-4][1]) * 0.6, w, h * 0.8, r), "OnPrevious", ind + "\t")
        # static pose: rotation about the slot centre
        L.append(f'{ind}\t<control type="group">')
        L.append(f"{ind}\t\t<left>{round(x - w / 2)}</left>")
        L.append(f"{ind}\t\t<top>{round(y - h / 2)}</top>")
        L.append(f"{ind}\t\t<width>{w}</width>")
        L.append(f"{ind}\t\t<height>{h}</height>")
        if abs(r) > 0.01:
            L.append(f'{ind}\t\t<animation effect="rotate" end="{f1(r)}" center="auto" time="0" condition="true">Conditional</animation>')
        i2 = ind + "\t\t"
        # 0.9.20: round art (circle mask, or circle_cond = artists) sits on a round shadow and a round plate;
        # square / poster art keeps the 9-slice shadow and its own mask
        round_always = mask == "masks/circle.png"
        shapes = ([(mask, None)] if not circle_cond or round_always
                  else [(mask, f"!{circle_cond}"), ("masks/circle.png", circle_cond)])
        if abs(k) <= shadows:
            for msk, cond in shapes:
                if msk == "masks/circle.png":
                    if w != h or w not in ROUND_SHADOW_D:
                        raise SystemExit(f"{name} slot {k}: no common/shadow_round_{w}.png (make_textures.ROUND_SHADOW_D)")
                    tex_sh = f"common/shadow_round_{w}.png"
                else:
                    tex_sh = None
                L += [f'{i2}<control type="image">', f"{i2}\t<left>-96</left>", f"{i2}\t<top>-70</top>",
                      f"{i2}\t<right>-96</right>", f"{i2}\t<bottom>-122</bottom>",
                      f"{i2}\t<texture>{tex_sh}</texture>" if tex_sh else
                      f'{i2}\t<texture border="128">common/shadow_soft.png</texture>']
                if cond:
                    L.append(f"{i2}\t<visible>{cond}</visible>")
                L.append(f"{i2}</control>")
        # plate + fallback title
        for msk, cond in shapes:
            L += [f'{i2}<control type="image">', f"{i2}\t<left>0</left>", f"{i2}\t<top>0</top>",
                  f"{i2}\t<width>{w}</width>", f"{i2}\t<height>{h}</height>",
                  f'{i2}\t<texture colordiffuse="{'panel' if icon_mode else 'plate'}" diffuse="{msk}">common/white.png</texture>']
            if cond:
                L.append(f"{i2}\t<visible>{cond}</visible>")
            L.append(f"{i2}</control>")
        if h >= 150 and not icon_mode:
            L += [f'{i2}<control type="textbox">', f"{i2}\t<left>12</left>", f"{i2}\t<top>12</top>",
                  f"{i2}\t<width>{w - 24}</width>", f"{i2}\t<height>{h - 24}</height>",
                  f"{i2}\t<font>label_20</font>", f"{i2}\t<textcolor>text_secondary</textcolor>",
                  f"{i2}\t<align>center</align>", f"{i2}\t<aligny>center</aligny>",
                  f"{i2}\t<label>$INFO[Container($PARAM[id]).ListItemNoWrap({kk}).Label]</label>",
                  f"{i2}\t<visible>!Container($PARAM[id]).ListItemNoWrap({kk}).IsParentFolder"
                  + (f" + !String.IsEqual(Container($PARAM[id]).ListItemNoWrap({kk}).DBType,song)" if song_titles else "")
                  + "</visible>",
                  f"{i2}</control>"]
            if song_titles:  # 0.9.19: songs print their title, not the songs node's "01. Artist - Title" label
                L += [f'{i2}<control type="textbox">', f"{i2}\t<left>12</left>", f"{i2}\t<top>12</top>",
                      f"{i2}\t<width>{w - 24}</width>", f"{i2}\t<height>{h - 24}</height>",
                      f"{i2}\t<font>label_20</font>", f"{i2}\t<textcolor>text_secondary</textcolor>",
                      f"{i2}\t<align>center</align>", f"{i2}\t<aligny>center</aligny>",
                      f"{i2}\t<label>$INFO[Container($PARAM[id]).ListItemNoWrap({kk}).Title]</label>",
                      f"{i2}\t<visible>String.IsEqual(Container($PARAM[id]).ListItemNoWrap({kk}).DBType,song)</visible>",
                      f"{i2}</control>"]
        # parent folder tile: back icon in the plate
        L += [f'{i2}<control type="image">', f"{i2}\t<centerleft>50%</centerleft>", f"{i2}\t<centertop>50%</centertop>",
              f"{i2}\t<width>{max(24, w // 4)}</width>", f"{i2}\t<height>{max(24, w // 4)}</height>",
              f'{i2}\t<texture colordiffuse="text_secondary">icons/back.png</texture>',
              f"{i2}\t<visible>Container($PARAM[id]).ListItemNoWrap({kk}).IsParentFolder</visible>", f"{i2}</control>"]
        # art (brightness by distance, animated)
        tex = f"$VAR[{art_var}_{'m' if k < 0 else 'p'}{abs(k)}]"
        if icon_mode:
            ins = round(w * 0.3)
            L += [f'{i2}<control type="image">', f"{i2}	<left>0</left>", f"{i2}	<top>0</top>",
                  f"{i2}	<width>{w}</width>", f"{i2}	<height>{h}</height>",
                  f'{i2}	<texture colordiffuse="border_button">btn/ring_120.png</texture>']
            L += bright_anims(k, k + 1, k - 1, i2 + "	")
            L.append(f"{i2}</control>")
            L += [f'{i2}<control type="image">', f"{i2}	<left>{ins}</left>", f"{i2}	<top>{ins}</top>",
                  f"{i2}	<width>{w - 2 * ins}</width>", f"{i2}	<height>{h - 2 * ins}</height>",
                  f'{i2}	<texture colordiffuse="text_primary">$INFO[Container($PARAM[id]).ListItemNoWrap({kk}).Icon]</texture>']
            L += bright_anims(k, k + 1, k - 1, i2 + "	")
            L.append(f"{i2}</control>")
            if k == 0 and lens_extra:
                L += [f'{i2}<control type="image">', f"{i2}	<left>-14</left>", f"{i2}	<top>-14</top>",
                      f"{i2}	<width>{w + 28}</width>", f"{i2}	<height>{h + 28}</height>",
                      f'{i2}	<texture border="32" colordiffuse="text_primary">focus/brackets.png</texture>',
                      f"{i2}	<visible>Control.HasFocus($PARAM[id])</visible>",
                      f'{i2}	<animation effect="fade" start="0" end="100" time="160">Visible</animation>',
                      f"{i2}</control>"]
            L.append(f"{ind}	</control>")
            L.append(f"{ind}</control>")
            continue
        for msk, cond in (([mask, None],) if not circle_cond else ((mask, f"!{circle_cond}"), ("masks/circle.png", circle_cond))):
            L += [f'{i2}<control type="image">', f"{i2}\t<left>0</left>", f"{i2}\t<top>0</top>",
                  f"{i2}\t<width>{w}</width>", f"{i2}\t<height>{h}</height>",
                  # 0.9.20: a circle mask stays on the control rect (LESSONS: scalediffuse), so a non-square thumb
                  # is still a disc over its round shadow, not an ellipse cut flat by the control
                  f"{i2}\t<aspectratio{' scalediffuse=\"false\"' if msk == 'masks/circle.png' else ''}>scale</aspectratio>",
                  f"{i2}\t<fadetime>100</fadetime>",
                  f'{i2}\t<texture background="true" diffuse="{msk}">{tex}</texture>']
            if cond:
                L.append(f"{i2}\t<visible>{cond}</visible>")
            L += bright_anims(k, k + 1, k - 1, i2 + "\t")
            L.append(f"{i2}</control>")
        if circle_cond:
            pass
        # watched badge
        if h >= 150:
            L += [f'{i2}<control type="image">', f"{i2}\t<right>8</right>", f"{i2}\t<top>8</top>",
                  f"{i2}\t<width>30</width>", f"{i2}\t<height>30</height>",
                  f"{i2}\t<texture>markers/watched_badge.png</texture>",
                  f"{i2}\t<visible>$EXP[ShowWatchedMarkers] + Integer.IsGreater(Container($PARAM[id]).ListItemNoWrap({kk}).PlayCount,0) + !Container($PARAM[id]).ListItemNoWrap({kk}).IsResumable</visible>"]
            L += bright_anims(k, k + 1, k - 1, i2 + "\t")
            L.append(f"{i2}</control>")
        if k == 0 and lens_extra:
            # resume bar + focus brackets on the lens
            L += [f'{i2}<control type="progress">', f"{i2}\t<left>0</left>", f"{i2}\t<top>{h - 5}</top>",
                  f"{i2}\t<width>{w}</width>", f"{i2}\t<height>5</height>",
                  f'{i2}\t<texturebg colordiffuse="scrim_track">common/white.png</texturebg>',
                  f'{i2}\t<midtexture colordiffuse="accent">common/white.png</midtexture>',
                  f"{i2}\t<info>Container($PARAM[id]).ListItem.PercentPlayed</info>",
                  f"{i2}\t<visible>Container($PARAM[id]).ListItem.IsResumable</visible>", f"{i2}</control>"]
            L += [f'{i2}<control type="image">', f"{i2}\t<left>-14</left>", f"{i2}\t<top>-14</top>",
                  f"{i2}\t<width>{w + 28}</width>", f"{i2}\t<height>{h + 28}</height>",
                  f'{i2}\t<texture border="32" colordiffuse="text_primary">focus/brackets.png</texture>',
                  f"{i2}\t<visible>Control.HasFocus($PARAM[id])</visible>",
                  f'{i2}\t<animation effect="zoom" start="94" end="100" center="auto" time="200" tween="cubic" easing="out">Visible</animation>',
                  f'{i2}\t<animation effect="fade" start="0" end="100" time="160">Visible</animation>',
                  f"{i2}</control>"]
        L.append(f"{ind}\t</control>")
        L.append(f"{ind}</control>")
    L += ["\t\t\t</control>", "\t\t</definition>", "\t</include>", ""]
    return L


def art_variables(prefix, cid, chain, wrap=False):
    """$VAR[prefix_m3] etc: first non-empty art in chain for Container(cid).ListItemNoWrap(k)."""
    L = []
    LI = "ListItem" if wrap else "ListItemNoWrap"
    for k in range(-5, 6):
        nm = f"{prefix}_{'m' if k < 0 else 'p'}{abs(k)}"
        L.append(f'\t<variable name="{nm}">')
        for art in chain[:-1]:
            L.append(f'\t\t<value condition="!String.IsEmpty(Container({cid}).{LI}({k}).{art})">$INFO[Container({cid}).{LI}({k}).{art}]</value>')
        L.append(f"\t\t<value>$INFO[Container({cid}).{LI}({k}).{chain[-1]}]</value>")
        L.append("\t</variable>")
    return L


def hidden_list(name, desc, rows=11, focuspos=5, art="ListItem.Art(poster)", ctype="fixedlist"):
    """The focus-owning list: 1px items, art drawn invisibly so Kodi loads it (LESSONS 2)."""
    return [f"\t<!-- {desc} -->",
            f'\t<include name="{name}">',
            "\t\t<orientation>vertical</orientation>",
            "\t\t<width>1</width>",
            f"\t\t<height>{rows}</height>",
            f"\t\t<focusposition>{focuspos}</focusposition>",
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


# ------------------------------------------------------------------ dial (Home sections)
DIAL_C = (200, 540)
DIAL_ANGLES = {-2: -64, -1: -32, 0: 0, 1: 32, 2: 64}
DIAL_R = {0: 300, 1: 292, 2: 292}
DIAL_TIERS = (44, 38, 34, 30)          # 0.9.18: focused station sizes for long custom item names
DIAL_PITCH = {44: 54, 38: 46, 34: 44}  # wide font line pitches (make_titles.py)
DIAL_FIT_W = 295                       # room before the amber lens dash
DIAL_PROBE = 9762


def dial():
    cx, cy = DIAL_C
    L = ["\t<!-- Home section dial: labels on the ring centred (200,540) (OrbitHome mockup). Shows",
         "\t     Container(9000).ListItem(k) of the 5-item wraplist; a move rotates every label about the",
         "\t     ring centre from its neighbour's station (pulse mechanics, see file header). -->",
         '\t<include name="Arc_HomeDial">',
         '\t\t<param name="t">220</param>',
         "\t\t<definition>"]
    for k in (-2, -1, 1, 2, 0):
        a = DIAL_ANGLES[k]
        r = DIAL_R[abs(k)]
        x = cx + r * math.cos(math.radians(a))
        y = cy + r * math.sin(math.radians(a))
        focused = k == 0
        h = 54 if focused else 32
        font = "wide_44" if focused else "wide_26"
        L.append(f"\t\t\t<!-- station {k:+d} at {a} deg -->")
        L.append('\t\t\t<control type="group">')
        L.append("\t\t\t\t<left>0</left>")
        L.append("\t\t\t\t<top>0</top>")
        if k:  # 0.9.12: items can be hidden (HideMenu.*); a wraplist repeats a short list, so a station only shows
            # while it holds an item no other station shows (-1: 2 items, +1: 3, -2: 4, +2: 5)
            need = 2 * abs(k) + (1 if k > 0 else 0)
            L.append(f"\t\t\t\t<visible>Integer.IsGreaterOrEqual(Container(9000).NumItems,{need})</visible>")
        for cond, src in (("OnNext", k + 1), ("OnPrevious", k - 1)):
            sa = DIAL_ANGLES.get(src, 96 if src > 0 else -96)
            d_ang = sa - a  # clockwise degrees to the source station
            src_size = 44 if src == 0 else 26
            own = 44 if focused else 26
            L.append(f'\t\t\t\t<animation type="Conditional" condition="!Container(9000).{cond}" reversible="false">')
            L.append(f'\t\t\t\t\t<effect type="rotate" start="{f1(-d_ang)}" end="0" center="{cx},{cy}" time="$PARAM[t]" tween="cubic" easing="out"/>')
            L.append(f'\t\t\t\t\t<effect type="zoom" start="{f1(src_size / own * 100)}" end="100" center="{f1(x)},{f1(y)}" time="$PARAM[t]" tween="cubic" easing="out"/>')
            if abs(src) > 2:
                L.append('\t\t\t\t\t<effect type="fade" start="0" end="100" time="$PARAM[t]"/>')
            L.append("\t\t\t\t</animation>")
        L.append('\t\t\t\t<control type="grouplist">')
        L.append(f"\t\t\t\t\t<left>{round(x)}</left>")
        L.append(f"\t\t\t\t\t<top>{round(y - h / 2)}</top>")
        L.append("\t\t\t\t\t<width>560</width>")
        L.append(f"\t\t\t\t\t<height>{h}</height>")
        L.append("\t\t\t\t\t<orientation>horizontal</orientation>")
        L.append("\t\t\t\t\t<itemgap>14</itemgap>")
        L.append("\t\t\t\t\t<usecontrolcoords>true</usecontrolcoords>")
        # 0.9.18: custom menu items carry any name. Unfocused stations are capped at 300 px; the focused one has only
        # 295 px before the amber lens dash (x 800), so a long name steps down 44 -> 38 -> 34 -> 30 (probes 9762-9764
        # in Arc_HomeDial: NumPages > 1 = the name needs a second line at that size) and is cut only at 30.
        # Every built-in label fits at 44 (SETTINGS 291 px), so those render exactly as before.
        tiers = [(font, None)] if not focused else [
            (f"wide_{sz}", " + ".join([f"Integer.IsGreater(Container({DIAL_PROBE + j}).NumPages,1)" for j in range(i)]
                                      + ([f"!Integer.IsGreater(Container({DIAL_PROBE + i}).NumPages,1)"] if i < 3 else [])))
            for i, sz in enumerate(DIAL_TIERS)]
        for tfont, vis in tiers:
            L.append('\t\t\t\t\t<control type="label">')
            L.append(f'\t\t\t\t\t\t<width max="{DIAL_FIT_W if focused else 300}">auto</width>')
            L.append(f"\t\t\t\t\t\t<height>{h}</height>")
            if tfont != font:
                L.append("\t\t\t\t\t\t<aligny>center</aligny>")
            L.append(f"\t\t\t\t\t\t<font>{tfont}</font>")
            L.append(f"\t\t\t\t\t\t<textcolor>{'text_primary' if focused else 'text_secondary'}</textcolor>")
            L.append(f"\t\t\t\t\t\t<label>$INFO[Container(9000).ListItem({k}).Label]</label>")
            if vis:
                L.append(f"\t\t\t\t\t\t<visible>{vis}</visible>")
            L.append("\t\t\t\t\t</control>")
        if not focused:
            L.append('\t\t\t\t\t<control type="label">')
            L.append("\t\t\t\t\t\t<top>2</top>")
            L.append("\t\t\t\t\t\t<width>auto</width>")
            L.append(f"\t\t\t\t\t\t<height>{h}</height>")
            L.append("\t\t\t\t\t\t<font>mono_20</font>")
            L.append("\t\t\t\t\t\t<textcolor>text_dim</textcolor>")
            L.append(f"\t\t\t\t\t\t<label>$INFO[Container(9000).ListItem({k}).Label2]</label>")
            L.append("\t\t\t\t\t</control>")
        L.append("\t\t\t\t</control>")
        L.append("\t\t\t</control>")
    # fit probes for the focused station (alpha 0, off screen): one line + half of each tier but the last
    for j, sz in enumerate(DIAL_TIERS[:-1]):
        L += [f'\t\t\t<control type="textbox" id="{DIAL_PROBE + j}">', "\t\t\t\t<left>-4000</left>",
              f"\t\t\t\t<top>{-2400 + j * 200}</top>", f"\t\t\t\t<width>{DIAL_FIT_W}</width>",
              f"\t\t\t\t<height>{round(1.5 * DIAL_PITCH[sz])}</height>", f"\t\t\t\t<font>wide_{sz}</font>",
              "\t\t\t\t<textcolor>00ffffff</textcolor>",
              "\t\t\t\t<label>$INFO[Container(9000).ListItem.Label]</label>", "\t\t\t</control>"]
    L += ["\t\t</definition>", "\t</include>", ""]
    return L


# ------------------------------------------------------------------ dial list (rows)
def dial_list_slots(cx, cy, R, pitches):
    """rows on a circle centred left of the screen; returns k -> (x, y, rot_kodi)"""
    c = [0.0]
    for p in pitches:
        c.append(c[-1] + p)
    slots = {}
    for k in range(-5, 6):
        a = abs(k)
        th = (1 if k > 0 else -1 if k < 0 else 0) * c[a] / R
        x = cx + R * math.cos(th)
        y = cy + R * math.sin(th)
        slots[k] = (x, y, -th * 180 / math.pi * 0.7)  # kodi rotation: rows tilt with the circle (70% for legibility)
    return slots


DL_FONTS = {0: ("text_36_semi", 50, 1.0), 1: ("text_30_med", 42, 0.72), 2: ("text_26_med", 36, 0.52),
            3: ("text_26_med", 36, 0.38), 4: ("text_26_med", 36, 0.28), 5: ("text_26_med", 36, 0.18)}


def dial_list(name, cx, cy, R, pitches, width, desc):
    slots = dial_list_slots(cx, cy, R, pitches)
    L = [f"\t<!-- {desc} -->",
         f'\t<include name="{name}">',
         '\t\t<param name="t">160</param>',
         '\t\t<param name="label2">$INFO[Container($PARAM[id]).ListItemNoWrap(K).Label2]</param>',
         "\t\t<definition>",
         '\t\t\t<control type="group">',
         "\t\t\t\t<left>0</left>",
         "\t\t\t\t<top>0</top>"]
    for k in (5, -5, 4, -4, 3, -3, 2, -2, 1, -1, 0):
        x, y, r = slots[k]
        font, h, b = DL_FONTS[abs(k)]
        ind = "\t\t\t\t"
        L.append(f"{ind}<!-- row {k:+d} at {x:.0f},{y:.0f} -->")
        L.append(f'{ind}<control type="group">')
        L.append(f"{ind}\t<left>0</left>")
        L.append(f"{ind}\t<top>0</top>")
        L.append(f"{ind}\t<visible>!String.IsEmpty(Container($PARAM[id]).ListItemNoWrap({k}).Label)</visible>")
        for cond, src in (("OnNext", k + 1), ("OnPrevious", k - 1)):
            if abs(src) <= 5:
                sx, sy, sr = slots[src]
                sfont, sh, sb = DL_FONTS[abs(src)]
            else:
                sx, sy, sr = x, y + (40 if src > 0 else -40), r
                sfont, sh, sb = DL_FONTS[5]
            zoom = sh / h * 100
            L.append(f'{ind}\t<animation type="Conditional" condition="!Container($PARAM[id]).{cond}" reversible="false">')
            L.append(f'{ind}\t\t<effect type="slide" start="{f1(sx - x)},{f1(sy - y)}" end="0,0" time="$PARAM[t]" tween="cubic" easing="out"/>')
            L.append(f'{ind}\t\t<effect type="zoom" start="{f1(zoom)}" end="100" center="{f1(x)},{f1(y)}" time="$PARAM[t]" tween="cubic" easing="out"/>')
            if abs(sr - r) > 0.01:
                L.append(f'{ind}\t\t<effect type="rotate" start="{f1(sr - r)}" end="0" center="{f1(x)},{f1(y)}" time="$PARAM[t]" tween="cubic" easing="out"/>')
            L.append(f"{ind}\t</animation>")
        L.append(f'{ind}\t<control type="group">')
        L.append(f"{ind}\t\t<left>{round(x)}</left>")
        L.append(f"{ind}\t\t<top>{round(y - h / 2)}</top>")
        L.append(f"{ind}\t\t<width>{width}</width>")
        L.append(f"{ind}\t\t<height>{h}</height>")
        if abs(r) > 0.01:
            L.append(f'{ind}\t\t<animation effect="rotate" end="{f1(r)}" center="{round(x)},{f1(y)}" time="0" condition="true">Conditional</animation>')
        i2 = ind + "\t\t"
        col = "text_primary"
        # brightness via fadediffuse on the row group (text only, no overlap issues)
        L += bright_rows(k, i2)
        if k == 0:
            # amber lens tick left of the focused row (Home dial language)
            L += [f'{i2}<control type="image">', f"{i2}\t<left>-64</left>", f"{i2}\t<top>{h // 2 - 1}</top>",
                  f"{i2}\t<width>40</width>", f"{i2}\t<height>3</height>",
                  f'{i2}\t<texture colordiffuse="accent">common/white.png</texture>',
                  f"{i2}\t<visible>Control.HasFocus($PARAM[id])</visible>", f"{i2}</control>"]
            L += [f'{i2}<control type="image">', f"{i2}\t<left>-64</left>", f"{i2}\t<top>{h // 2 - 1}</top>",
                  f"{i2}\t<width>40</width>", f"{i2}\t<height>3</height>",
                  f'{i2}\t<texture colordiffuse="text_dim">common/white.png</texture>',
                  f"{i2}\t<visible>!Control.HasFocus($PARAM[id])</visible>", f"{i2}</control>"]
        lbl2 = f"$INFO[Container($PARAM[id]).ListItemNoWrap({k}).$PARAM[l2],,$PARAM[l2suffix]]"
        L += [f'{i2}<control type="grouplist">', f"{i2}\t<left>0</left>", f"{i2}\t<top>0</top>",
              f"{i2}\t<width>{width}</width>", f"{i2}\t<height>{h}</height>",
              f"{i2}\t<orientation>horizontal</orientation>", f"{i2}\t<itemgap>18</itemgap>",
              f"{i2}\t<usecontrolcoords>true</usecontrolcoords>",
              f'{i2}\t<control type="label">', f"{i2}\t\t<width max=\"{width - 200}\">auto</width>",
              f"{i2}\t\t<height>{h}</height>", f"{i2}\t\t<font>{font}</font>", f"{i2}\t\t<textcolor>{col}</textcolor>",
              f"{i2}\t\t<label>$INFO[Container($PARAM[id]).ListItemNoWrap({k}).Label]</label>", f"{i2}\t</control>",
              f'{i2}\t<control type="label">', f"{i2}\t\t<top>2</top>", f"{i2}\t\t<width max=\"260\">auto</width>",
              f"{i2}\t\t<height>{h}</height>", f"{i2}\t\t<font>mono_20</font>", f"{i2}\t\t<textcolor>text_secondary</textcolor>",
              f"{i2}\t\t<label>{lbl2.replace('ListItemNoWrap(K)', f'ListItemNoWrap({k})')}</label>", f"{i2}\t</control>",
              f'{i2}\t<control type="image">', f"{i2}\t\t<top>{(h - 22) // 2}</top>", f"{i2}\t\t<width>22</width>",
              f"{i2}\t\t<height>22</height>", f'{i2}\t\t<texture colordiffuse="text_secondary">icons/check.png</texture>',
              f"{i2}\t\t<visible>Integer.IsGreater(Container($PARAM[id]).ListItemNoWrap({k}).PlayCount,0)</visible>",
              f"{i2}\t</control>",
              f"{i2}</control>"]
        L.append(f"{ind}\t</control>")
        L.append(f"{ind}</control>")
    L += ["\t\t\t</control>", "\t\t</definition>", "\t</include>", ""]
    return L


def bright_rows(k, indent):
    a = abs(k)
    base = DL_FONTS[a][2]
    out = []
    for cond, src in (("OnNext", k + 1), ("OnPrevious", k - 1)):
        sb = DL_FONTS[min(abs(src), 5)][2]
        if sb >= base and a != 0:
            start, end = hexalpha(sb), hexalpha(base)
        else:
            start, end = hexalpha(min(1.0, sb / base)), "ffffffff"
        out.append(f'{indent}<animation type="Conditional" condition="!Container($PARAM[id]).{cond}" reversible="false">')
        out.append(f'{indent}\t<effect type="fadediffuse" start="{start}" end="{end}" time="$PARAM[t]" tween="cubic" easing="out"/>')
        out.append(f"{indent}</animation>")
    return out


# ------------------------------------------------------------------ cast arc (info page)
def cast_arc():
    """Info page cast: circular portraits on a shallow arc (OrbitInfo mockup), lens in the middle.
    Horizontal: Left/Right on the hidden list 50 slides the portraits along the arc."""
    # lens = leftmost portrait (mockup: 4 portraits left to right on a shallow arc); the item
    # before the lens slides out to the left, the next one comes in from the right.
    pitch = 184
    lift = {-1: 34, 0: 0, 1: -21, 2: -21, 3: 0, 4: 34}
    D = {-1: 90, 0: 120, 1: 104, 2: 104, 3: 104, 4: 90}
    B2 = {-1: 0.0, 0: 1.0, 1: 0.7, 2: 0.7, 3: 0.7, 4: 0.0}
    pos = {k: (92 + pitch * k, 70 + lift[k], D[k]) for k in range(-1, 5)}
    L = ["	<!-- Cast on a shallow arc (container $PARAM[id], filled by Kodi): portraits in circles, films of",
         "	     a collection as posters. Lens = middle slot; names under the lens. -->",
         '	<include name="Arc_Cast">', '		<param name="t">180</param>', "		<definition>"]
    for k in (4, -1, 3, 2, 1, 0):
        x, y, d = pos[k]
        ind = "			"
        L.append(f'{ind}<control type="group">')
        L.append(f"{ind}	<left>0</left>")
        L.append(f"{ind}	<top>0</top>")
        L.append(f"{ind}	<visible>!String.IsEmpty(Container($PARAM[id]).ListItemNoWrap({k}).Label)</visible>")
        for cond, src in (("OnNext", k + 1), ("OnPrevious", k - 1)):
            sx, sy, sd = pos.get(src, (x + pitch * (1 if src > k else -1), y + 30, 70))
            L.append(f'{ind}	<animation type="Conditional" condition="!Container($PARAM[id]).{cond}" reversible="false">')
            L.append(f'{ind}		<effect type="slide" start="{f1(sx - x)},{f1(sy - y)}" end="0,0" time="$PARAM[t]" tween="cubic" easing="out"/>')
            L.append(f'{ind}		<effect type="zoom" start="{f1(sd / d * 100)}" end="100" center="{x},{y}" time="$PARAM[t]" tween="cubic" easing="out"/>')
            L.append(f"{ind}	</animation>")
        i2 = ind + "	"
        L += bright_cast(k, B2, i2)
        if k in (-1, 4):
            # off-stage slots: only visible while they slide (fade in/out with the move)
            L.append(f'{i2}<animation type="Conditional" condition="!Container($PARAM[id]).OnNext" reversible="false"><effect type="fade" start="100" end="0" time="$PARAM[t]"/></animation>' if k == -1 else
                     f'{i2}<animation type="Conditional" condition="!Container($PARAM[id]).OnPrevious" reversible="false"><effect type="fade" start="100" end="0" time="$PARAM[t]"/></animation>')
        r = d // 2
        # 0.9.20: scalediffuse false keeps the circle on the control: 2:3 portraits / posters were cut flat top and bottom
        L += [f'{i2}<control type="group">', f"{i2}	<left>{x - r}</left>", f"{i2}	<top>{y - r}</top>",
              f"{i2}	<width>{d}</width>", f"{i2}	<height>{d}</height>",
              f'{i2}	<control type="image"><left>0</left><top>0</top><width>{d}</width><height>{d}</height><texture colordiffuse="panel">btn/disc_120.png</texture></control>',
              f'{i2}	<control type="image"><left>{d // 4}</left><top>{d // 4}</top><width>{d // 2}</width><height>{d // 2}</height><texture colordiffuse="text_dim">icons/person.png</texture></control>',
              f'{i2}	<control type="image"><left>0</left><top>0</top><width>{d}</width><height>{d}</height><aspectratio scalediffuse="false">scale</aspectratio>'
              f'<texture background="true" diffuse="masks/circle.png">$INFO[Container($PARAM[id]).ListItemNoWrap({k}).Art(thumb)]</texture>'
              f'<visible>!String.IsEqual(Container($PARAM[id]).ListItemNoWrap({k}).DBType,movie)</visible></control>',
              f'{i2}	<control type="image"><left>0</left><top>0</top><width>{d}</width><height>{d}</height><aspectratio scalediffuse="false">scale</aspectratio>'
              f'<texture background="true" diffuse="masks/circle.png">$INFO[Container($PARAM[id]).ListItemNoWrap({k}).Art(poster)]</texture>'
              f'<visible>String.IsEqual(Container($PARAM[id]).ListItemNoWrap({k}).DBType,movie)</visible></control>',
              f'{i2}	<control type="image"><left>0</left><top>0</top><width>{d}</width><height>{d}</height><texture colordiffuse="border_button">btn/ring_120.png</texture></control>']
        if k == 0:
            L += [f'{i2}	<control type="image"><left>-11</left><top>-11</top><width>{d + 22}</width><height>{d + 22}</height>'
                  f'<texture colordiffuse="text_primary">btn/halo_120.png</texture><visible>Control.HasFocus($PARAM[id])</visible></control>']
        L.append(f"{i2}</control>")
        # name under the portrait (lens: 2 lines name + role)
        if 0 <= k <= 3:
            # lens name: 176 wide and scrolling, so a long name reads in full (0.9.4: "Sarocha Cha...")
            w = 176 if k == 0 else 160
            L += [f'{i2}<control type="label">', f"{i2}	<left>{x - w // 2}</left>", f"{i2}	<top>{y + r + 12}</top>",
                  f"{i2}	<width>{w}</width>", f"{i2}	<height>28</height>", f"{i2}	<align>center</align>",
                  f"{i2}	<font>{'text_22_med' if k == 0 else 'text_22'}</font>",
                  f"{i2}	<textcolor>{'text_primary' if k == 0 else 'text_secondary'}</textcolor>"]
            if k == 0:
                L += [f"{i2}	<scroll>true</scroll>", f"{i2}	<scrollspeed>50</scrollspeed>"]
            L += [f"{i2}	<label>$INFO[Container($PARAM[id]).ListItemNoWrap({k}).Label]</label>", f"{i2}</control>"]
        if k == 0:
            L += [f'{i2}<control type="label">', f"{i2}	<left>{x - 120}</left>", f"{i2}	<top>{y + r + 40}</top>",
                  f"{i2}	<width>240</width>", f"{i2}	<height>26</height>", f"{i2}	<align>center</align>",
                  f"{i2}	<font>text_22</font>", f"{i2}	<textcolor>text_dim</textcolor>",
                  f"{i2}	<label>$INFO[Container($PARAM[id]).ListItemNoWrap(0).Label2]</label>", f"{i2}</control>"]
        L.append(f"{ind}</control>")
    L += ["		</definition>", "	</include>", ""]
    return L


def bright_cast(k, B2, indent):
    base = max(B2[k], 0.05)
    out = []
    for cond, src in (("OnNext", k + 1), ("OnPrevious", k - 1)):
        sb = max(B2.get(src, 0.0), 0.05)
        if sb >= base and k != 0:
            start, end = hexgray(sb), hexgray(base)
        else:
            start, end = hexgray(min(1.0, sb / base)), "ffffffff"
        out.append(f'{indent}<animation type="Conditional" condition="!Container($PARAM[id]).{cond}" reversible="false">')
        out.append(f'{indent}	<effect type="fadediffuse" start="{start}" end="{end}" time="$PARAM[t]" tween="cubic" easing="out"/>')
        out.append(f"{indent}</animation>")
    return out


# ------------------------------------------------------------------ clock rotation
def clock_rotation():
    L = ["\t<!-- Rotate a group to the current time on a 12-hour face, about $PARAM[c],$PARAM[c] (Kodi:",
         "\t     positive angle = counter-clockwise, so clockwise time is negative). Hour group outside,",
         "\t     minute group inside. System.Time(hh) is 00-23 (or 01-12 in 12h locales: same result). -->",
         '\t<include name="Orbit_ClockRotationHour">', "\t\t<param name=\"c\">100</param>", "\t\t<definition>"]
    for h in range(24):
        ang = (h % 12) * 30
        if ang == 0:
            continue
        L.append(f'\t\t\t<animation effect="rotate" end="{-ang}" center="$PARAM[c],$PARAM[c]" time="0" condition="Integer.IsEqual(System.Time(hh),{h})">Conditional</animation>')
    L += ["\t\t</definition>", "\t</include>",
          '\t<include name="Orbit_ClockRotationMinute">', "\t\t<param name=\"c\">100</param>", "\t\t<definition>"]
    for m in range(1, 60):
        L.append(f'\t\t\t<animation effect="rotate" end="{-m * 0.5}" center="$PARAM[c],$PARAM[c]" time="0" condition="Integer.IsEqual(System.Time(mm),{m})">Conditional</animation>')
    L += ["\t\t</definition>", "\t</include>", ""]
    return L


# ------------------------------------------------------------------ geometry sets
GEOM = {
    # 0.9.1: evenly spaced, no overlap (lens 360 / 440, gap 18-20, tighter circle so the sweep reads)
    "home": dict(cx=1880, cy=540, R=880, F=1, H=[360, 200, 148, 112, 86], aspect=2 / 3, extra_h=66, gap=18),
    "homesq": dict(cx=1880, cy=540, R=880, F=1, H=[300, 176, 132, 100, 78], aspect=1.0, extra_h=60, gap=18),
    "lib": dict(cx=2180, cy=540, R=880, F=1, H=[440, 220, 160, 120, 92], aspect=2 / 3, extra_h=70, gap=20),
    "libsq": dict(cx=2180, cy=540, R=880, F=1, H=[380, 200, 148, 112, 86], aspect=1.0, extra_h=66, gap=20),
}

POSTER_CHAIN = ["Art(poster)", "Art(tvshow.poster)", "Art(thumb)", "Icon"]
SQUARE_CHAIN = ["Art(thumb)", "Art(poster)", "Icon"]


def main():
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         "<!-- GENERATED by _src/make_arc.py - edit the generator, not this file.",
         "     Orbit mechanics: arc (offset items on a circle), Home dial, dial list, clock rotation.",
         "     See the generator's docstring for how the one-frame OnNext/OnPrevious pulse drives the slides. -->",
         "<includes>"]
    for nm, g in GEOM.items():
        s = arc_slots(g["cx"], g["cy"], g["R"], g["F"], g["H"], g["aspect"], g["extra_h"])
        L.append(f"\t<!-- geometry '{nm}': " + "; ".join(f"{k:+d}: {v[0]:.0f},{v[1]:.0f} {v[2]}x{v[3]} r{v[4]:.1f}" for k, v in sorted(s.items())) + " -->")
    L.append("")
    # art variables per container
    L += art_variables("ArcArt9300", 9300, POSTER_CHAIN, wrap=True)
    L += art_variables("ArcArt9301", 9301, SQUARE_CHAIN, wrap=True)
    L += art_variables("ArcArt500", 500, POSTER_CHAIN)
    L += art_variables("ArcArt504", 504, SQUARE_CHAIN)
    for cid, chain in ((9101, POSTER_CHAIN), (9102, POSTER_CHAIN), (9103, SQUARE_CHAIN), (9104, SQUARE_CHAIN)):
        L += art_variables(f"ArcArt{cid}", cid, chain)
    # 0.9.12 custom rows (Includes_CustomRows.xml): Home arcs for lists 9881-9883
    for cid in (9881, 9882, 9883):
        L += art_variables(f"ArcArt{cid}", cid, POSTER_CHAIN, wrap=True)
    L.append("")
    g = GEOM["home"]
    L += wrapify(poster_arc("Arc_HomePosters", arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")}),
                    "ArcArt9300", "masks/poster_r4.png", "Home arc (container 9300): posters, lens at 1000,540", shadows=2))
    g = GEOM["homesq"]
    L += wrapify(poster_arc("Arc_HomeSquares", arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")}),
                    "ArcArt9301", "masks/square_r4.png", "Home arc (container 9301): album covers", shadows=2))
    g = GEOM["lib"]
    L += poster_arc("Arc_LibraryPosters", arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")}),
                    "ArcArt500", "masks/poster_r4.png", "Library arc (view 500): posters, lens at 1300,540", shadows=2)
    g = GEOM["libsq"]
    L += poster_arc("Arc_LibrarySquares", arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")}),
                    "ArcArt504", "masks/square_r4.png", "Music arc (view 504): album covers / artist discs",
                    shadows=2, circle_cond="Container.Content(artists)")
    g = GEOM["home"]
    L += wrapify(poster_arc("Arc_HomeCustom", arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")}),
                    "ArcArt$PARAM[id]", "masks/poster_r4.png", "Home arcs of the custom rows (containers 9881-9883, 0.9.12)", shadows=2))
    g = GEOM["homesq"]
    L += wrapify(poster_arc("Arc_HomeIcons", arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")}),
                    "unused", "masks/circle.png", "Home arc (container 9310): settings stations as round dials",
                    shadows=0, icon_mode=True))
    # search window: one arc per result type (art variables are per container id)
    g = GEOM["home"]
    hs = arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")})
    L += poster_arc("Arc_Search9101", hs, "ArcArt9101", "masks/poster_r4.png", "Search: films (container 9101)", shadows=2)
    L += poster_arc("Arc_Search9102", hs, "ArcArt9102", "masks/poster_r4.png", "Search: shows (container 9102)", shadows=2)
    g = GEOM["homesq"]
    hq = arc_slots(**{k: g[k] for k in ("cx", "cy", "R", "F", "H", "aspect", "extra_h", "gap")})
    L += poster_arc("Arc_Search9103", hq, "ArcArt9103", "masks/square_r4.png", "Search: albums (container 9103)", shadows=2)
    L += poster_arc("Arc_Search9104", hq, "ArcArt9104", "masks/circle.png", "Search: artists (container 9104)", shadows=2)
    # 0.9.16 horizons (arc_horizon.py): wide pictures (view 503) and covers / portraits (view 507) along the bottom
    from arc_horizon import horizon_slots, wide_art_variables, hidden_list_h, HORIZON, HORIZON_SQ
    L += wide_art_variables("ArcArt503", 503)
    L += art_variables("ArcArt507", 507, SQUARE_CHAIN)
    L += poster_arc("Arc_HorizonWide", horizon_slots(**HORIZON), "ArcArt503", "masks/landscape_r4.png",
                    "Horizon (view 503): wide pictures on a flat circle along the bottom, lens at 960,676", shadows=2)
    L += poster_arc("Arc_HorizonSquares", horizon_slots(**HORIZON_SQ), "ArcArt507", "masks/square_r4.png",
                    "Music horizon (view 507): album covers / artist discs along the bottom, lens at 960,660",
                    shadows=2, circle_cond="Container.Content(artists)", song_titles=True)
    L += hidden_list_h("Arc_HiddenListH", "Focus-owning list for a horizon: 11 x 1px items side by side, lens at item 5")
    L += hidden_list_h("Arc_HiddenListHSquare", "Same, art = thumb (albums, artists)", art="ListItem.Art(thumb)")
    L += hidden_list("Arc_HiddenList", "Focus-owning list for an arc: 11 x 1px rows, lens at row 5")
    L += hidden_list("Arc_HiddenListSquare", "Same, art = thumb (albums, artists)", art="ListItem.Art(thumb)")
    L += hidden_list("Arc_HiddenListIcon", "Same, art = icon (generic items)", art="ListItem.Icon")
    L += dial()
    # dial list: rows on a circle centred (-760,540), R 960 -> focused row at x 200
    L += dial_list("DialList_RowsNarrow", -760, 540, 960, [84, 70, 62, 58, 56], 640,
                   "Dial list, narrower rows (info panel on the right)")
    L += cast_arc()
    L += clock_rotation()
    L.append("</includes>")
    # 0.9.8: the arc glides honour Reduce motion (items land in place and crossfade instead)
    from rm_guard import guard_text
    text, _n = guard_text("\n".join(L) + "\n", "Skin.HasSetting(orbit.reducemotion)")
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(L)} lines)")
    for nm, g in GEOM.items():
        s = arc_slots(g["cx"], g["cy"], g["R"], g["F"], g["H"], g["aspect"], g["extra_h"])
        print(nm, {k: (round(v[0]), round(v[1]), v[2], v[3], round(v[4], 1)) for k, v in s.items()})


if __name__ == "__main__":
    main()
