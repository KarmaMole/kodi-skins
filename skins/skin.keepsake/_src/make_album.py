"""Generate 1080i/Includes_Album.xml: Keepsake's album pieces with the pixel maths done here, not in XML.

  KS_Page                 the open album (paper_spread.jpg) / KS_PageSingle (paper_page.jpg)
  KS_Stamp<s>             the orange LCD date imprint at size s: haze + glow2 + glow1 + core labels
                          params: label, right (px from parent right to the text box right), bottom (px from parent
                          bottom to the digits' baseline), visible.  Width of "'26~10~18" = 6.48 x size.
  KS_LCD<s>               LCD text (clock, times) with glow; params: label, left, top, width, align, visible
  KS_Print_<kind>         a mounted print: shadow, white border, photo (dim-able), stamp shade + stamp, sheen,
                          photo corners. Group size = photo + 2 x border. params: art, dim (colordiffuse of the
                          photo), stamp (label), stamped (condition), corners (condition), lift (condition: big
                          shadow), aspect, title (handwritten on the blank print when there is no art)
  KS_TiltItem             itemlayout / static tilt by ListItem.CurrentItem's last digit (hand-placed, fixed per slot)
  KS_TiltFocus            focusedlayout: tilt at rest, straighten + lift on Focus, back on Unfocus. param zoom
  KS_TiltFixed            a fixed tilt for one-off prints. param angle (Kodi degrees, + = counter-clockwise)
  KS_PenProgress<w>       pen progress line: dotted track (native size), pen stroke fill, tick. params: info, visible
  KS_PenWordLook          look of a handwritten focusable word (underline on focus)
  KS_TapeRowLook          look of a focused list row (washi tape)
CSS -> Kodi: rotate(+a deg) (clockwise) == Kodi rotate end="-a" (LESSONS round 3: positive is counter-clockwise).
Usage: python skins/skin.keepsake/_src/make_album.py
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Includes_Album.xml"

# CSS tilt per last digit of the item index (mockups: -1.8, 1.6, -1.2, 2.0, -1.5 ...), Kodi = -CSS
TILT_CSS = {1: -1.8, 2: 1.6, 3: 1.4, 4: -1.2, 5: 2.0, 6: -1.5, 7: -1.0, 8: 1.9, 9: 1.2, 0: -1.6}
STAMP_SIZES = (19, 20, 22, 26, 30, 34, 44)
STAMP_EM = 6.481        # width of "'26~10~18" in em (bar 385 + 6 digits x 861 + 2 gaps x 465) / 1000
ASC = 1.15              # stamp fonts: baseline 1.15 em below the label top, line 1.3 em

# kind: photo w, h, border, stamp size, corner size, shadow at rest
PRINTS = {
    "Memory": (432, 243, 14, 22, 46, "s"),
    "Stop": (300, 169, 14, 19, 46, "s"),
    "EpBig": (440, 248, 14, 20, 46, "s"),
    "Small": (330, 186, 14, 19, 46, "s"),
    "Diary": (360, 203, 14, 19, 46, "s"),
    "InfoBig": (700, 394, 14, 34, 46, "m"),
    "InfoPoster": (200, 285, 12, 19, 38, "s"),
    "Poster": (160, 228, 12, 19, 38, "s"),
    "PosterM": (200, 300, 12, 19, 38, "s"),
    "Thumb": (300, 169, 12, 19, 38, "s"),
    "Square": (210, 210, 12, 19, 38, "s"),
    "SquareL": (460, 460, 16, 26, 46, "m"),
    "Cast": (120, 180, 8, 19, 30, "s"),
    "FSPoster": (240, 360, 12, 19, 38, "m"),
    "Search": (150, 225, 10, 19, 34, "s"),
    "SearchSq": (190, 190, 10, 19, 34, "s"),
    "Land": (380, 214, 14, 19, 46, "s"),
    # instant photos (albums): a thick bottom margin with the title handwritten on it
    "Instant": (210, 210, 12, 19, 38, "s", 58),
    "InstantL": (460, 460, 22, 26, 46, "m", 104),
}
SHADOW = {"s": (24, 36, "shadow_s.png"), "m": (40, 52, "shadow_m.png"), "l": (64, 84, "shadow_l.png")}
PROGRESS_W = (180, 220, 300, 360, 520, 750, 1100)


def stamp(s: int) -> list[str]:
    h = round(1.3 * s)
    top_from_baseline = round(ASC * s)      # label top is this far above the baseline
    lift = h - top_from_baseline            # label bottom is this far below the baseline
    hz_w, hz_h = round(STAMP_EM * s + 40), round(1.7 * s)
    o = [f'\t<include name="KS_Stamp{s}">',
         '\t\t<param name="right">16</param>', '\t\t<param name="bottom">12</param>',
         '\t\t<param name="visible">true</param>', '\t\t<definition>',
         '\t\t\t<control type="group">', '\t\t\t\t<right>$PARAM[right]</right>', '\t\t\t\t<bottom>$PARAM[bottom]</bottom>',
         f'\t\t\t\t<width>{hz_w}</width>', f'\t\t\t\t<height>1</height>',
         '\t\t\t\t<visible>$PARAM[visible]</visible>',
         # haze: centred on the digits (digits occupy baseline-1.0em .. baseline)
         '\t\t\t\t<control type="image">', f'\t\t\t\t\t<right>-20</right>', f'\t\t\t\t\t<top>{-round(0.5 * s) - hz_h // 2}</top>',
         f'\t\t\t\t\t<width>{hz_w}</width>', f'\t\t\t\t\t<height>{hz_h}</height>',
         '\t\t\t\t\t<texture colordiffuse="stamp_haze">ks/stamp_haze.png</texture>', '\t\t\t\t</control>']
    # a faint dark under-glow first: keeps the digits readable on white photos (Blue Collar)
    for font, color in ((f"g2_{s}", "stamp_under"), (f"g2_{s}", "stamp_g2"), (f"g1_{s}", "stamp_g1"), (f"stamp_{s}", "stamp")):
        o += ['\t\t\t\t<control type="label">', '\t\t\t\t\t<right>0</right>', f'\t\t\t\t\t<top>{-top_from_baseline}</top>',
              f'\t\t\t\t\t<width>{hz_w}</width>', f'\t\t\t\t\t<height>{h}</height>', '\t\t\t\t\t<align>right</align>',
              f'\t\t\t\t\t<font>{font}</font>', f'\t\t\t\t\t<textcolor>{color}</textcolor>',
              '\t\t\t\t\t<label>$PARAM[label]</label>', '\t\t\t\t</control>']
    o += ['\t\t\t</control>', '\t\t</definition>', '\t</include>']
    # LCD (clock / times): params left, top (label box top), width, align
    o += [f'\t<include name="KS_LCD{s}">', '\t\t<param name="align">left</param>', '\t\t<param name="visible">true</param>',
          '\t\t<param name="width">400</param>', '\t\t<definition>',
          '\t\t\t<control type="group">', '\t\t\t\t<left>$PARAM[left]</left>', '\t\t\t\t<top>$PARAM[top]</top>',
          '\t\t\t\t<width>$PARAM[width]</width>', f'\t\t\t\t<height>{h}</height>', '\t\t\t\t<visible>$PARAM[visible]</visible>']
    for font, color in ((f"g2_{s}", "stamp_g2"), (f"g1_{s}", "stamp_g1"), (f"stamp_{s}", "stamp")):
        o += ['\t\t\t\t<control type="label">', '\t\t\t\t\t<left>0</left>', '\t\t\t\t\t<top>0</top>',
              '\t\t\t\t\t<width>$PARAM[width]</width>', f'\t\t\t\t\t<height>{h}</height>', '\t\t\t\t\t<align>$PARAM[align]</align>',
              f'\t\t\t\t\t<font>{font}</font>', f'\t\t\t\t\t<textcolor>{color}</textcolor>',
              '\t\t\t\t\t<label>$PARAM[label]</label>', '\t\t\t\t</control>']
    o += ['\t\t\t</control>', '\t\t</definition>', '\t</include>']
    return o


def print_kind(name, w, h, b, s, cs, sh, bb=None) -> list[str]:
    bb = b if bb is None else bb      # bottom border (instant photos have a thick one)
    W, H = w + 2 * b, h + b + bb
    o = [f'\t<!-- {name}: photo {w}x{h}, border {b} -> print {W}x{H}; stamp {s}px; corners {cs}px -->',
         f'\t<include name="KS_Print_{name}">',
         '\t\t<param name="art">$INFO[ListItem.Art(fanart)]</param>', '\t\t<param name="dim">white</param>',
         '\t\t<param name="stamp"></param>', '\t\t<param name="stamped">false</param>',
         '\t\t<param name="corners">true</param>', '\t\t<param name="lift">false</param>',
         '\t\t<param name="aspect">scale</param>',
         '\t\t<param name="title"></param>', '\t\t<param name="caption"></param>',
         '\t\t<definition>']
    # shadows (rest + lifted), white border, photo
    ins, _border, tex = SHADOW[sh]
    o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{-ins}</left>', f'\t\t\t\t<top>{-ins}</top>',
          f'\t\t\t\t<width>{W + 2 * ins}</width>', f'\t\t\t\t<height>{H + 2 * ins}</height>',
          f'\t\t\t\t<texture border="{_border}">ks/{tex}</texture>', '\t\t\t\t<visible>!$PARAM[lift]</visible>', '\t\t\t</control>']
    big = "l" if min(W, H) >= 168 else "m"
    ins2, b2, tex2 = SHADOW[big]
    o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{-ins2}</left>', f'\t\t\t\t<top>{-ins2}</top>',
          f'\t\t\t\t<width>{W + 2 * ins2}</width>', f'\t\t\t\t<height>{H + 2 * ins2}</height>',
          f'\t\t\t\t<texture border="{b2}">ks/{tex2}</texture>', '\t\t\t\t<visible>$PARAM[lift]</visible>', '\t\t\t</control>']
    o += ['\t\t\t<control type="image">', '\t\t\t\t<left>-3</left>', '\t\t\t\t<top>-3</top>',
          f'\t\t\t\t<width>{W + 6}</width>', f'\t\t\t\t<height>{H + 6}</height>',
          '\t\t\t\t<texture border="12" colordiffuse="print">ks/print.png</texture>', '\t\t\t</control>']
    # fallback block + title when there is no art
    o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{b}</left>', f'\t\t\t\t<top>{b}</top>',
          f'\t\t\t\t<width>{w}</width>', f'\t\t\t\t<height>{h}</height>',
          '\t\t\t\t<texture colordiffuse="paper_raised">common/white.png</texture>', '\t\t\t</control>',
          '\t\t\t<control type="textbox">', f'\t\t\t\t<left>{b + 12}</left>', f'\t\t\t\t<top>{b + 10}</top>',
          f'\t\t\t\t<width>{w - 24}</width>', f'\t\t\t\t<height>{min(h - 20, 120)}</height>',
          f'\t\t\t\t<font>{"hand_30" if w < 260 else "hand_40"}</font>', '\t\t\t\t<textcolor>ink2</textcolor>',
          '\t\t\t\t<label>$PARAM[title]</label>', '\t\t\t</control>']
    o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{b}</left>', f'\t\t\t\t<top>{b}</top>',
          f'\t\t\t\t<width>{w}</width>', f'\t\t\t\t<height>{h}</height>', '\t\t\t\t<aspectratio>$PARAM[aspect]</aspectratio>',
          '\t\t\t\t<fadetime>200</fadetime>',
          '\t\t\t\t<texture background="true" diffuse="ks/print_mask.png" colordiffuse="$PARAM[dim]">$PARAM[art]</texture>',
          '\t\t\t</control>']
    # stamp: shade (60% x 55% of the photo) + digits 16 px from the right, 12 px from the bottom
    sw, shh = round(w * .6), round(h * .55)
    o += ['\t\t\t<control type="image">', f'\t\t\t\t<right>{b}</right>', f'\t\t\t\t<bottom>{bb}</bottom>',
          f'\t\t\t\t<width>{sw}</width>', f'\t\t\t\t<height>{shh}</height>',
          '\t\t\t\t<texture>ks/stamp_shade.png</texture>', '\t\t\t\t<visible>$PARAM[stamped] + !String.IsEqual(Skin.String(keepsake.stamp),off)</visible>', '\t\t\t</control>']
    o += [f'\t\t\t<include content="KS_Stamp{s}">', '\t\t\t\t<param name="label" value="$PARAM[stamp]"/>',
          f'\t\t\t\t<param name="right" value="{b + 16}"/>', f'\t\t\t\t<param name="bottom" value="{bb + 12}"/>',
          '\t\t\t\t<param name="visible" value="$PARAM[stamped] + !String.IsEqual(Skin.String(keepsake.stamp),off)"/>', '\t\t\t</include>']
    # sheen over the whole print
    o += ['\t\t\t<control type="image">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>0</top>',
          f'\t\t\t\t<width>{W}</width>', f'\t\t\t\t<height>{H}</height>', '\t\t\t\t<texture>ks/sheen.png</texture>', '\t\t\t</control>']
    if bb != b:
        fnt = "hand_30" if w < 300 else "hand_44"
        o += ['\t\t\t<control type="label">', f'\t\t\t\t<left>{b + 4}</left>', f'\t\t\t\t<top>{b + h + 4}</top>',
              f'\t\t\t\t<width>{w - 8}</width>', f'\t\t\t\t<height>{bb - 8}</height>', '\t\t\t\t<align>center</align>',
              '\t\t\t\t<aligny>center</aligny>', f'\t\t\t\t<font>{fnt}</font>', '\t\t\t\t<textcolor>on_print</textcolor>',
              '\t\t\t\t<label>$PARAM[caption]</label>', '\t\t\t</control>']
    # photo corners
    o += ['\t\t\t<control type="group">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>0</top>',
          f'\t\t\t\t<width>{W}</width>', f'\t\t\t\t<height>{H}</height>', '\t\t\t\t<visible>$PARAM[corners]</visible>']
    for (x, y, fx, fy) in (("left", "top", False, False), ("right", "top", True, False),
                           ("left", "bottom", False, True), ("right", "bottom", True, True)):
        flips = (' flipx="true"' if fx else "") + (' flipy="true"' if fy else "")
        o += ['\t\t\t\t<control type="image">', f'\t\t\t\t\t<{x}>-5</{x}>', f'\t\t\t\t\t<{y}>-5</{y}>',
              f'\t\t\t\t\t<width>{cs}</width>', f'\t\t\t\t\t<height>{cs}</height>',
              f'\t\t\t\t\t<texture{flips}>ks/corner.png</texture>', '\t\t\t\t</control>']
    o += ['\t\t\t</control>', '\t\t</definition>', '\t</include>']
    return o


def tilts() -> list[str]:
    """Tilts honour Skin settings > the prints = straight (keepsake.straight): then no rotation at all, the focused
    print still lifts (zoom). Rotation and zoom are separate animations so either can be switched off."""
    ST = "!Skin.HasSetting(keepsake.straight)"
    RM = "Skin.HasSetting(keepsake.reducemotion)"
    o = ['\t<!-- static hand-placed tilt by the item index (last digit), for itemlayouts and the rest state -->',
         '\t<include name="KS_TiltItem">']
    for d, css in TILT_CSS.items():
        o.append(f'\t\t<animation effect="rotate" end="{-css}" center="auto" time="0" condition="{ST} + String.EndsWith(ListItem.CurrentItem,{d})">Conditional</animation>')
    o.append('\t</include>')
    o += ['\t<!-- focusedlayout inner group: straighten (cancel the tilt) and lift on Focus; back on Unfocus -->',
          '\t<include name="KS_TiltFocus">', '\t\t<param name="zoom">106</param>', '\t\t<definition>']
    for d, css in TILT_CSS.items():
        a = css  # cancelling rotation = -(tilt) = +css in Kodi terms
        c = f"String.EndsWith(ListItem.CurrentItem,{d})"
        o.append(f'\t\t\t<animation type="Focus" condition="!{RM} + {ST} + {c}"><effect type="rotate" start="0" end="{a}" center="auto" time="240" tween="cubic" easing="out"/></animation>')
        o.append(f'\t\t\t<animation type="Focus" condition="{RM} + {ST} + {c}"><effect type="rotate" start="0" end="{a}" center="auto" time="0"/></animation>')
        o.append(f'\t\t\t<animation type="Unfocus" condition="!{RM} + {ST} + {c}"><effect type="rotate" start="{a}" end="0" center="auto" time="180" tween="cubic" easing="out"/></animation>')
    o.append(f'\t\t\t<animation type="Focus" condition="!{RM}"><effect type="zoom" start="100" end="$PARAM[zoom]" center="auto" time="240" tween="cubic" easing="out"/></animation>')
    o.append(f'\t\t\t<animation type="Focus" condition="{RM}"><effect type="zoom" start="100" end="$PARAM[zoom]" center="auto" time="0"/></animation>')
    o.append(f'\t\t\t<animation type="Unfocus" condition="!{RM}"><effect type="zoom" start="$PARAM[zoom]" end="100" center="auto" time="180" tween="cubic" easing="out"/></animation>')
    o += ['\t\t</definition>', '\t</include>']
    o += ['\t<!-- one fixed tilt (Kodi degrees) -->', '\t<include name="KS_TiltFixed">', '\t\t<param name="angle">0</param>',
          '\t\t<definition>', f'\t\t\t<animation effect="rotate" end="$PARAM[angle]" center="auto" time="0" condition="{ST}">Conditional</animation>',
          '\t\t</definition>', '\t</include>']
    o += ['\t<!-- straighten + lift a fixed-tilt print while a control has focus. params: unangle (minus the tilt), focus, zoom -->',
          '\t<include name="KS_LiftOnFocus">', '\t\t<param name="zoom">106</param>', '\t\t<definition>',
          f'\t\t\t<animation type="Conditional" condition="$PARAM[focus] + !{RM} + {ST}" reversible="true"><effect type="rotate" start="0" end="$PARAM[unangle]" center="auto" time="240" tween="cubic" easing="out"/></animation>',
          f'\t\t\t<animation type="Conditional" condition="$PARAM[focus] + {RM} + {ST}"><effect type="rotate" start="0" end="$PARAM[unangle]" center="auto" time="0"/></animation>',
          f'\t\t\t<animation type="Conditional" condition="$PARAM[focus] + !{RM}" reversible="true"><effect type="zoom" start="100" end="$PARAM[zoom]" center="auto" time="240" tween="cubic" easing="out"/></animation>',
          f'\t\t\t<animation type="Conditional" condition="$PARAM[focus] + {RM}"><effect type="zoom" start="100" end="$PARAM[zoom]" center="auto" time="0"/></animation>',
          '\t\t</definition>', '\t</include>']
    return o


def progress(w) -> list[str]:
    return [f'\t<include name="KS_PenProgress{w}">', '\t\t<param name="visible">true</param>', '\t\t<param name="color">ink</param>',
            '\t\t<definition>', '\t\t\t<control type="group">', '\t\t\t\t<left>$PARAM[left]</left>', '\t\t\t\t<top>$PARAM[top]</top>',
            f'\t\t\t\t<width>{w}</width>', '\t\t\t\t<height>28</height>', '\t\t\t\t<visible>$PARAM[visible]</visible>',
            '\t\t\t\t<control type="image">', '\t\t\t\t\t<left>0</left>', '\t\t\t\t\t<top>13</top>', f'\t\t\t\t\t<width>{w}</width>',
            '\t\t\t\t\t<height>4</height>', '\t\t\t\t\t<aspectratio>center</aspectratio>',
            '\t\t\t\t\t<texture colordiffuse="dotted">ks/dots_h.png</texture>', '\t\t\t\t</control>',
            '\t\t\t\t<control type="progress">', '\t\t\t\t\t<left>0</left>', '\t\t\t\t\t<top>0</top>', f'\t\t\t\t\t<width>{w - 10}</width>',
            '\t\t\t\t\t<height>28</height>', f'\t\t\t\t\t<texturebg>ks/progress_bg_{w - 10}.png</texturebg>',
            '\t\t\t\t\t<midtexture colordiffuse="$PARAM[color]">ks/pen_fill.png</midtexture>',
            '\t\t\t\t\t<righttexture colordiffuse="$PARAM[color]">ks/pen_tick.png</righttexture>',
            '\t\t\t\t\t<info>$PARAM[info]</info>', '\t\t\t\t</control>', '\t\t\t</control>', '\t\t</definition>', '\t</include>']


def looks() -> list[str]:
    return [
        '\t<!-- handwritten focusable word: faint ink at rest, bright + pen underline on focus (put font/size on the button) -->',
        '\t<include name="KS_PenWordLook">',
        '\t\t<textcolor>ink_faint</textcolor>', '\t\t<focusedcolor>ink_bold</focusedcolor>', '\t\t<disabledcolor>ink_ghost</disabledcolor>',
        '\t\t<textoffsetx>6</textoffsetx>', '\t\t<aligny>top</aligny>',
        '\t\t<texturefocus border="0,0,0,30" colordiffuse="ink">ks/pen_under.png</texturefocus>',
        '\t\t<texturenofocus />', '\t</include>',
        '\t<!-- focused list row: a strip of washi tape, dark ink on it -->',
        '\t<include name="KS_TapeRowTexture">',
        '\t\t<texturefocus border="24,0,24,0" colordiffuse="tape">ks/tape_row.png</texturefocus>', '\t</include>',
        '\t<include name="KS_Page">',
        '\t\t<control type="image">', '\t\t\t<description>the open album</description>', '\t\t\t<left>0</left>', '\t\t\t<top>0</top>',
        '\t\t\t<width>1920</width>', '\t\t\t<height>1080</height>', '\t\t\t<texture>ks/paper_spread.jpg</texture>', '\t\t</control>',
        '\t</include>',
        '\t<include name="KS_PageSingle">',
        '\t\t<control type="image">', '\t\t\t<description>one album leaf</description>', '\t\t\t<left>0</left>', '\t\t\t<top>0</top>',
        '\t\t\t<width>1920</width>', '\t\t\t<height>1080</height>', '\t\t\t<texture>ks/paper_page.jpg</texture>', '\t\t</control>',
        '\t</include>',
    ]


def main():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           "<!-- GENERATED by _src/make_album.py - prints, stamps, LCD, tilts, pen progress. Edit the generator. -->",
           "<includes>"]
    for s in STAMP_SIZES:
        out += stamp(s)
    for name, spec in PRINTS.items():
        out += print_kind(name, *spec)
    out += tilts()
    for w in PROGRESS_W:
        out += progress(w)
    out += looks()
    out += ["</includes>", ""]
    OUT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("wrote", OUT, len(out), "lines")


if __name__ == "__main__":
    main()
