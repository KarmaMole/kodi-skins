"""Generate 1080i/SkinSettings.xml: Keepsake's six settings (docs/skin.keepsake/SETTINGS.md).

One page of the album: the settings are lines on the left page, written in pen, each with its choices in DM Mono;
the chosen one is circled in pen (like ticking a form). One focus per row: Left / Right change the value at once,
OK cycles, Back leaves. The right page shows a print from your diary with the current stamp order and tilt, and a
note about the focused line.
Settings (all empty = the default):
  keepsake.stamp        "" = '26 10 18 (camera)   dmy = 18 10 '26   off = no stamp
  keepsake.straight     bool: prints sit straight (no hand-placed tilt)
  keepsake.notime       bool: don't say the time of day (Skin Variables)
  keepsake.hidetrailer  bool: no "trailer" word on the info page
  keepsake.reducemotion bool: no lifts / slides
  keepsake.osdhide      3 / "" (5) / 10 / off: OSD hides after N seconds idle (Custom_1152)
Usage: python skins/skin.keepsake/_src/make_skinsettings.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "SkinSettings.xml"

# id, label, help, options: (word, is_selected condition, set action)
ROWS = [
    (9510, "the date stamp", "How the orange camera date is printed in the corner of a print you watched.", [
        ("'26 10 18", "String.IsEmpty(Skin.String(keepsake.stamp))", "Skin.Reset(keepsake.stamp)"),
        ("18 10 '26", "String.IsEqual(Skin.String(keepsake.stamp),dmy)", "Skin.SetString(keepsake.stamp,dmy)"),
        ("none", "String.IsEqual(Skin.String(keepsake.stamp),off)", "Skin.SetString(keepsake.stamp,off)"),
    ]),
    (9511, "the prints", "Hand-placed prints sit a little crooked, like a real album; straight lines them up.", [
        ("hand-placed", "!Skin.HasSetting(keepsake.straight)", "Skin.Reset(keepsake.straight)"),
        ("straight", "Skin.HasSetting(keepsake.straight)", "Skin.SetBool(keepsake.straight)"),
    ]),
    (9512, "the time of day", "\"Just after nine\", \"that evening, 8:26 pm\": read from your library by Skin Variables.", [
        ("written", "!Skin.HasSetting(keepsake.notime)", "Skin.Reset(keepsake.notime)"),
        ("left out", "Skin.HasSetting(keepsake.notime)", "Skin.SetBool(keepsake.notime)"),
    ]),
    (9513, "the trailer word", "The \"trailer\" word on a film's page, when the film has a trailer.", [
        ("shown", "!Skin.HasSetting(keepsake.hidetrailer)", "Skin.Reset(keepsake.hidetrailer)"),
        ("hidden", "Skin.HasSetting(keepsake.hidetrailer)", "Skin.SetBool(keepsake.hidetrailer)"),
    ]),
    (9514, "motion", "Prints lift and straighten, pages fade. Reduced keeps everything still.", [
        ("full", "!Skin.HasSetting(keepsake.reducemotion)", "Skin.Reset(keepsake.reducemotion)"),
        ("reduced", "Skin.HasSetting(keepsake.reducemotion)", "Skin.SetBool(keepsake.reducemotion)"),
    ]),
    (9515, "the words hide after", "During playback the words at the bottom close by themselves after this long.", [
        ("3 s", "String.IsEqual(Skin.String(keepsake.osdhide),3)", "Skin.SetString(keepsake.osdhide,3)"),
        ("5 s", "String.IsEmpty(Skin.String(keepsake.osdhide))", "Skin.Reset(keepsake.osdhide)"),
        ("10 s", "String.IsEqual(Skin.String(keepsake.osdhide),10)", "Skin.SetString(keepsake.osdhide,10)"),
        ("never", "String.IsEqual(Skin.String(keepsake.osdhide),off)", "Skin.SetString(keepsake.osdhide,off)"),
    ]),
]
TOP = 252
PITCH = 104
OPT_X = 470
OPT_W = 172


def esc(t):
    return t.replace("&", "&amp;").replace('"', "&quot;")


def row(i, rid, label, help_, opts):
    top = TOP + i * PITCH
    up = ROWS[i - 1][0] if i > 0 else ROWS[-1][0]
    down = ROWS[(i + 1) % len(ROWS)][0]
    o = [f'\t\t<!-- {label} -->', '\t\t<control type="group">', '\t\t\t<left>112</left>', f'\t\t\t<top>{top}</top>',
         '\t\t\t<width>860</width>', f'\t\t\t<height>{PITCH}</height>']
    # the focus holder (clear button) with Left/Right/OK
    o += [f'\t\t\t<control type="button" id="{rid}">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>0</top>',
          '\t\t\t\t<width>860</width>', '\t\t\t\t<height>84</height>', '\t\t\t\t<texturefocus />', '\t\t\t\t<texturenofocus />',
          f'\t\t\t\t<onup>{up}</onup>', f'\t\t\t\t<ondown>{down}</ondown>']
    n = len(opts)
    for k, (word, cond, act) in enumerate(opts):
        nxt = opts[(k + 1) % n][2]
        prv = opts[(k - 1) % n][2]
        o.append(f'\t\t\t\t<onright condition="{cond}">{esc(nxt) if k < n - 1 else "noop"}</onright>')
        o.append(f'\t\t\t\t<onleft condition="{cond}">{esc(prv) if k > 0 else "noop"}</onleft>')
        o.append(f'\t\t\t\t<onclick condition="{cond}">{esc(nxt)}</onclick>')
    o.append('\t\t\t</control>')
    # label + pen underline on focus
    o += ['\t\t\t<control type="label">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>4</top>', '\t\t\t\t<width>500</width>',
          '\t\t\t\t<height>64</height>', '\t\t\t\t<font>hand_46</font>', f'\t\t\t\t<textcolor>$VAR[SkinSet_Ink_{rid}]</textcolor>',
          f'\t\t\t\t<label>{esc(label)}</label>', '\t\t\t</control>',
          '\t\t\t<control type="image">', '\t\t\t\t<left>-4</left>', '\t\t\t\t<top>58</top>', '\t\t\t\t<width>360</width>',
          '\t\t\t\t<height>22</height>', '\t\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
          f'\t\t\t\t<visible>Control.HasFocus({rid})</visible>', '\t\t\t</control>']
    for k, (word, cond, act) in enumerate(opts):
        x = OPT_X - 112 + k * OPT_W
        o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{x - 4}</left>', '\t\t\t\t<top>2</top>',
              f'\t\t\t\t<width>{OPT_W - 8}</width>', '\t\t\t\t<height>64</height>',
              '\t\t\t\t<texture border="30" colordiffuse="ink">ks/pen_box.png</texture>',
              f'\t\t\t\t<visible>{cond}</visible>', '\t\t\t</control>',
              '\t\t\t<control type="label">', f'\t\t\t\t<left>{x}</left>', '\t\t\t\t<top>20</top>',
              f'\t\t\t\t<width>{OPT_W - 16}</width>', '\t\t\t\t<height>30</height>', '\t\t\t\t<align>center</align>',
              '\t\t\t\t<font>lbln_20</font>', f'\t\t\t\t<textcolor>$VAR[SkinSet_Opt_{rid}]</textcolor>',
              f'\t\t\t\t<label>{esc(word)}</label>', '\t\t\t</control>']
    o.append('\t\t</control>')
    return o


def main():
    o = ['<?xml version="1.0" encoding="UTF-8"?>', '<!-- GENERATED by _src/make_skinsettings.py - edit the generator. -->',
         '<!--', '\tSkin settings: six lines on the left page, the choice circled in pen; a print from the diary on the right',
         '\tshows the stamp and the tilt. Rows 9510-9515 (one focus each; Left/Right change, OK cycles). 9590 preview data.', '-->',
         '<window>', '\t<defaultcontrol always="true">9510</defaultcontrol>', '\t<backgroundcolor>paper</backgroundcolor>',
         '\t<include>Anim_WindowOpenClose</include>', '\t<controls>', '\t\t<include>KS_Page</include>',
         '\t\t<include content="KS_TopBar">', '\t\t\t<param name="title" value="skin settings"/>',
         '\t\t\t<param name="sub" value="keepsake  ·  [COLOR label_hi]left and right change a line[/COLOR]"/>', '\t\t</include>']
    for i, (rid, label, help_, opts) in enumerate(ROWS):
        o += row(i, rid, label, help_, opts)
    # preview + help on the right page
    o += ['\t\t<control type="list" id="9590">', '\t\t\t<left>1064</left>', '\t\t\t<top>200</top>', '\t\t\t<width>560</width>',
          '\t\t\t<height>420</height>', '\t\t\t<orientation>horizontal</orientation>',
          '\t\t\t<itemlayout width="560" height="420">', '\t\t\t\t<include>SkinSet_Preview</include>', '\t\t\t</itemlayout>',
          '\t\t\t<focusedlayout width="560" height="420">', '\t\t\t\t<include>SkinSet_Preview</include>', '\t\t\t</focusedlayout>',
          '\t\t\t<content target="videos" limit="1" sortby="random" browse="never">$VAR[KS_Path_Watched]</content>',
          '\t\t</control>',
          '\t\t<control type="textbox">', '\t\t\t<left>1080</left>', '\t\t\t<top>640</top>', '\t\t\t<width>700</width>',
          '\t\t\t<height>150</height>', '\t\t\t<font>hand_44</font>', '\t\t\t<textcolor>ink2</textcolor>',
          '\t\t\t<label>$VAR[SkinSet_Help]</label>', '\t\t</control>',
          '\t\t<control type="label">', '\t\t\t<left>1084</left>', '\t\t\t<top>826</top>', '\t\t\t<width>700</width>',
          '\t\t\t<height>27</height>', '\t\t\t<font>lbl_20</font>', '\t\t\t<textcolor>label</textcolor>',
          '\t\t\t<label>$INFO[Container(9590).ListItem.Title]$VAR[SkinSet_PreviewWhen]</label>', '\t\t</control>',
          '\t</controls>', '</window>', '']
    OUT.write_text("\n".join(o), encoding="utf-8", newline="\n")
    inc = ['<?xml version="1.0" encoding="UTF-8"?>', '<!-- GENERATED by _src/make_skinsettings.py -->', '<includes>']
    for rid, label, help_, opts in ROWS:
        inc += [f'\t<variable name="SkinSet_Ink_{rid}">', f'\t\t<value condition="Control.HasFocus({rid})">ink_bold</value>',
                '\t\t<value>ink_soft</value>', '\t</variable>',
                f'\t<variable name="SkinSet_Opt_{rid}">', f'\t\t<value condition="Control.HasFocus({rid})">ink_bold</value>',
                '\t\t<value>label_hi</value>', '\t</variable>']
    inc.append('\t<variable name="SkinSet_Help">')
    for rid, label, help_, opts in ROWS:
        inc.append(f'\t\t<value condition="Control.HasFocus({rid})">{esc(help_)}</value>')
    inc.append('\t</variable>')
    inc += ['\t<variable name="SkinSet_PreviewWhen">',
            '\t\t<value condition="!String.IsEmpty(Container(9590).ListItem.LastPlayed)">  ·  watched $INFO[Container(9590).ListItem.LastPlayed]</value>',
            '\t</variable>',
            '\t<include name="SkinSet_Preview">',
            '\t\t<control type="group">', '\t\t\t<left>40</left>', '\t\t\t<top>60</top>', '\t\t\t<width>436</width>', '\t\t\t<height>259</height>',
            '\t\t\t<include content="KS_TiltFixed"><param name="angle" value="-1.6"/></include>',
            '\t\t\t<include content="KS_Print_Land">', '\t\t\t\t<param name="art" value="$VAR[KS_LandscapeArt]"/>',
            '\t\t\t\t<param name="stamp" value="$VAR[KS_LP_Stamp]"/>', '\t\t\t\t<param name="stamped" value="!String.IsEmpty(ListItem.LastPlayed)"/>',
            '\t\t\t\t<param name="title" value="$INFO[ListItem.Label]"/>', '\t\t\t</include>', '\t\t</control>', '\t</include>',
            '</includes>', '']
    (OUT.parent / "Includes_SkinSettings.xml").write_text("\n".join(inc), encoding="utf-8", newline="\n")
    print("wrote", OUT.name, "+ Includes_SkinSettings.xml")


if __name__ == "__main__":
    main()
