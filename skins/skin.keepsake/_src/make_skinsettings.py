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
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

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

# 0.9.8 main menu (HideMenu.*): one more line, "the menu shows  films  series  music  search". A word circled in pen is
# shown on Home; Left / Right move the pen (Window(Home).Property(keepsake.menucur), 1-4) and OK circles or uncircles
# the word under it. Settings always stays on Home, so it is not on the line.
MENU_ID = 9516
MENU_WORDS = [("films", "Movies"), ("series", "TVShows"), ("music", "Music"), ("search", "Search")]
MENU_HELP = "Circle the words Home shows; the others leave, with their prints. Settings always stays."
CUR = "Window(Home).Property(keepsake.menucur)"


def cur_is(k):
    """the pen is on word k (1-based); empty = the first word"""
    return f"[String.IsEmpty({CUR}) | String.IsEqual({CUR},1)]" if k == 1 else f"String.IsEqual({CUR},{k})"


def menu_row():
    top = TOP + len(ROWS) * PITCH
    rid = MENU_ID
    o = ['\t\t<!-- the menu shows (HideMenu.*) -->', '\t\t<control type="group">', '\t\t\t<left>112</left>', f'\t\t\t<top>{top}</top>',
         '\t\t\t<width>860</width>', f'\t\t\t<height>{PITCH}</height>',
         f'\t\t\t<control type="button" id="{rid}">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>0</top>',
         '\t\t\t\t<width>860</width>', '\t\t\t\t<height>84</height>', '\t\t\t\t<texturefocus />', '\t\t\t\t<texturenofocus />',
         f'\t\t\t\t<onup>{ROWS[-1][0]}</onup>', f'\t\t\t\t<ondown>{CMENU_IDS[0]}</ondown>']
    n = len(MENU_WORDS)
    for k in range(1, n + 1):
        key = MENU_WORDS[k - 1][1]
        o.append(f'\t\t\t\t<onright condition="{cur_is(k)}">{f"SetProperty(keepsake.menucur,{k + 1},home)" if k < n else "noop"}</onright>')
        o.append(f'\t\t\t\t<onleft condition="{cur_is(k)}">{f"SetProperty(keepsake.menucur,{k - 1},home)" if k > 1 else "noop"}</onleft>')
        o.append(f'\t\t\t\t<onclick condition="{cur_is(k)}">Skin.ToggleSetting(HideMenu.{key})</onclick>')
    o.append('\t\t\t</control>')
    o += ['\t\t\t<control type="label">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>4</top>', '\t\t\t\t<width>500</width>',
          '\t\t\t\t<height>64</height>', '\t\t\t\t<font>hand_46</font>', f'\t\t\t\t<textcolor>$VAR[SkinSet_Ink_{rid}]</textcolor>',
          '\t\t\t\t<label>the menu shows</label>', '\t\t\t</control>',
          '\t\t\t<control type="image">', '\t\t\t\t<left>-4</left>', '\t\t\t\t<top>58</top>', '\t\t\t\t<width>360</width>',
          '\t\t\t\t<height>22</height>', '\t\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
          f'\t\t\t\t<visible>Control.HasFocus({rid})</visible>', '\t\t\t</control>']
    for k, (word, key) in enumerate(MENU_WORDS, 1):
        w = opt_w(len(MENU_WORDS))
        x = OPT_X - 112 + (k - 1) * w
        o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{x - 4}</left>', '\t\t\t\t<top>2</top>',
              f'\t\t\t\t<width>{w - 8}</width>', '\t\t\t\t<height>64</height>',
              '\t\t\t\t<texture border="30" colordiffuse="ink">ks/pen_box.png</texture>',
              f'\t\t\t\t<visible>!Skin.HasSetting(HideMenu.{key})</visible>', '\t\t\t</control>',
              # the pen: a short stroke under the word it is on, while the line has focus
              '\t\t\t<control type="image">', f'\t\t\t\t<left>{x + 8}</left>', '\t\t\t\t<top>66</top>',
              f'\t\t\t\t<width>{w - 32}</width>', '\t\t\t\t<height>16</height>',
              '\t\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
              f'\t\t\t\t<visible>Control.HasFocus({rid}) + {cur_is(k)}</visible>', '\t\t\t</control>',
              '\t\t\t<control type="label">', f'\t\t\t\t<left>{x}</left>', '\t\t\t\t<top>20</top>',
              f'\t\t\t\t<width>{w - 16}</width>', '\t\t\t\t<height>30</height>', '\t\t\t\t<align>center</align>',
              '\t\t\t\t<font>lbln_20</font>', f'\t\t\t\t<textcolor>$VAR[SkinSet_Opt_{rid}]</textcolor>',
              f'\t\t\t\t<label>{word}</label>', '\t\t\t</control>']
    o.append('\t\t</control>')
    return o
OPT_X = 470
OPT_W = 172


def opt_w(n):
    """0.9.10: pitch of a line's choices by how many it has. Four choices at 172 put the last word past the
    gutter (x 986: "never" sat on the print's caption, "search" on the right page); two at 172 left
    "hand-placed" (154 px) touching its pen box. Every line still ends before the gutter (x ~960)."""
    return {4: 126, 2: 190}.get(n, OPT_W)

# 0.9.8 custom rows on Home (Includes_CustomRows.xml): a line on the right page, under the preview,
# "custom rows  row 1  row 2  row 3": one button per word (Left / Right between them), OK opens that row's options.
# A word is circled in pen while its row is set up; the row under the pen is spelled out below the line.
CUSTOM_IDS = [9517, 9518, 9519]
CUSTOM_TOP = 958  # below "the menu shows", whose last word reaches into the right page
CUSTOM_X = 1380


def custom_line():
    o = ['\t\t<!-- custom rows (Home) -->', '\t\t<control type="group">', '\t\t\t<left>1064</left>', f'\t\t\t<top>{CUSTOM_TOP}</top>',
         '\t\t\t<control type="label">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>4</top>', '\t\t\t\t<width>300</width>',
         '\t\t\t\t<height>64</height>', '\t\t\t\t<font>hand_46</font>', '\t\t\t\t<textcolor>$VAR[SkinSet_Ink_Custom]</textcolor>',
         '\t\t\t\t<label>$LOCALIZE[31960]</label>', '\t\t\t</control>',
         '\t\t\t<control type="image">', '\t\t\t\t<left>-4</left>', '\t\t\t\t<top>58</top>', '\t\t\t\t<width>280</width>',
         '\t\t\t\t<height>22</height>', '\t\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
         f'\t\t\t\t<visible>{" | ".join(f"Control.HasFocus({c})" for c in CUSTOM_IDS)}</visible>', '\t\t\t</control>',
         '\t\t\t<control type="label">', '\t\t\t\t<left>4</left>', '\t\t\t\t<top>84</top>', '\t\t\t\t<width>800</width>',
         '\t\t\t\t<height>27</height>', '\t\t\t\t<font>lbl_20</font>', '\t\t\t\t<textcolor>label_hi</textcolor>',
         '\t\t\t\t<label>$VAR[SkinSet_CustomValue]</label>', '\t\t\t</control>', '\t\t</control>']
    for k, cid in enumerate(CUSTOM_IDS):
        n = k + 1
        x = CUSTOM_X + k * OPT_W
        left = CUSTOM_IDS[k - 1] if k else "noop"
        right = CUSTOM_IDS[k + 1] if k + 1 < len(CUSTOM_IDS) else "noop"
        o += ['\t\t<control type="image">', f'\t\t\t<left>{x - 4}</left>', f'\t\t\t<top>{CUSTOM_TOP + 2}</top>',
              f'\t\t\t<width>{OPT_W - 8}</width>', '\t\t\t<height>64</height>',
              '\t\t\t<texture border="30" colordiffuse="ink">ks/pen_box.png</texture>',
              f'\t\t\t<visible>!String.IsEmpty(Skin.String(CustomRow.{n}.Path))</visible>', '\t\t</control>',
              '\t\t<control type="image">', f'\t\t\t<left>{x + 8}</left>', f'\t\t\t<top>{CUSTOM_TOP + 66}</top>',
              f'\t\t\t<width>{OPT_W - 32}</width>', '\t\t\t<height>16</height>',
              '\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
              f'\t\t\t<visible>Control.HasFocus({cid})</visible>', '\t\t</control>',
              f'\t\t<control type="button" id="{cid}">', f'\t\t\t<left>{x}</left>', f'\t\t\t<top>{CUSTOM_TOP + 2}</top>',
              f'\t\t\t<width>{OPT_W - 16}</width>', '\t\t\t<height>64</height>', '\t\t\t<align>center</align>',
              '\t\t\t<font>lbln_20</font>', f'\t\t\t<textcolor>label_hi</textcolor>', '\t\t\t<focusedcolor>ink_bold</focusedcolor>',
              '\t\t\t<texturefocus />', '\t\t\t<texturenofocus />',
              f'\t\t\t<label>$LOCALIZE[{31960 + n}]</label>',
              f'\t\t\t<onup>{CMENU_IDS[k]}</onup>', f'\t\t\t<ondown>{ROWS[0][0]}</ondown>',
              f'\t\t\t<onleft>{left}</onleft>', f'\t\t\t<onright>{right}</onright>',
              f'\t\t\t<include content="CustomRows_SettingsClick"><param name="row" value="{n}"/><param name="heading" value="$LOCALIZE[{31940 + n}]"/></include>',
              '\t\t</control>']
    return o


# 0.9.14 custom menu items (Includes_CustomMenu.xml): a line above the custom rows on the right page, under the
# preview's caption: "menu items  item 1  item 2  item 3". One button per word (Left / Right between them), OK opens
# that item's options; a word is circled while its item is set up. The item under the pen is spelled out in the
# custom rows' line below (SkinSet_CustomValue: the right page has no room for a second one).
# Up / Down: the menu line (9516) > menu items > custom rows > the first line.
CMENU_IDS = [9520, 9521, 9522]
CMENU_TOP = CUSTOM_TOP - 96   # 8 px clear of the preview caption (826-853)


def cmenu_line():
    focus = " | ".join(f"Control.HasFocus({c})" for c in CMENU_IDS)
    o = ['\t\t<!-- custom menu items (Home) -->', '\t\t<control type="group">', '\t\t\t<left>1064</left>', f'\t\t\t<top>{CMENU_TOP}</top>',
         '\t\t\t<control type="label">', '\t\t\t\t<left>0</left>', '\t\t\t\t<top>4</top>', '\t\t\t\t<width>300</width>',
         '\t\t\t\t<height>64</height>', '\t\t\t\t<font>hand_46</font>', '\t\t\t\t<textcolor>$VAR[SkinSet_Ink_CMenu]</textcolor>',
         '\t\t\t\t<label>menu items</label>', '\t\t\t</control>',
         '\t\t\t<control type="image">', '\t\t\t\t<left>-4</left>', '\t\t\t\t<top>58</top>', '\t\t\t\t<width>280</width>',
         '\t\t\t\t<height>22</height>', '\t\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
         f'\t\t\t\t<visible>{focus}</visible>', '\t\t\t</control>', '\t\t</control>']
    for k, cid in enumerate(CMENU_IDS):
        n = k + 1
        x = CUSTOM_X + k * OPT_W
        left = CMENU_IDS[k - 1] if k else "noop"
        right = CMENU_IDS[k + 1] if k + 1 < len(CMENU_IDS) else "noop"
        o += ['\t\t<control type="image">', f'\t\t\t<left>{x - 4}</left>', f'\t\t\t<top>{CMENU_TOP + 2}</top>',
              f'\t\t\t<width>{OPT_W - 8}</width>', '\t\t\t<height>64</height>',
              '\t\t\t<texture border="30" colordiffuse="ink">ks/pen_box.png</texture>',
              f'\t\t\t<visible>!String.IsEmpty(Skin.String(CustomMenu.{n}.Path))</visible>', '\t\t</control>',
              '\t\t<control type="image">', f'\t\t\t<left>{x + 8}</left>', f'\t\t\t<top>{CMENU_TOP + 66}</top>',
              f'\t\t\t<width>{OPT_W - 32}</width>', '\t\t\t<height>16</height>',
              '\t\t\t<texture colordiffuse="ink">ks/pen_line.png</texture>',
              f'\t\t\t<visible>Control.HasFocus({cid})</visible>', '\t\t</control>',
              f'\t\t<control type="button" id="{cid}">', f'\t\t\t<left>{x}</left>', f'\t\t\t<top>{CMENU_TOP + 2}</top>',
              f'\t\t\t<width>{OPT_W - 16}</width>', '\t\t\t<height>64</height>', '\t\t\t<align>center</align>',
              '\t\t\t<font>lbln_20</font>', f'\t\t\t<textcolor>label_hi</textcolor>', '\t\t\t<focusedcolor>ink_bold</focusedcolor>',
              '\t\t\t<texturefocus />', '\t\t\t<texturenofocus />',
              f'\t\t\t<label>item {n}</label>',
              f'\t\t\t<onup>{MENU_ID}</onup>', f'\t\t\t<ondown>{CUSTOM_IDS[k]}</ondown>',
              f'\t\t\t<onleft>{left}</onleft>', f'\t\t\t<onright>{right}</onright>',
              f'\t\t\t<include content="CustomMenu_SettingsClick"><param name="item" value="{n}"/><param name="heading" value="$LOCALIZE[{31980 + n}]"/></include>',
              '\t\t</control>']
    return o


def esc(t):
    return t.replace("&", "&amp;").replace('"', "&quot;")


def row(i, rid, label, help_, opts):
    top = TOP + i * PITCH
    up = ROWS[i - 1][0] if i > 0 else CUSTOM_IDS[0]
    down = ROWS[i + 1][0] if i + 1 < len(ROWS) else MENU_ID
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
        w = opt_w(len(opts))
        x = OPT_X - 112 + k * w
        o += ['\t\t\t<control type="image">', f'\t\t\t\t<left>{x - 4}</left>', '\t\t\t\t<top>2</top>',
              f'\t\t\t\t<width>{w - 8}</width>', '\t\t\t\t<height>64</height>',
              '\t\t\t\t<texture border="30" colordiffuse="ink">ks/pen_box.png</texture>',
              f'\t\t\t\t<visible>{cond}</visible>', '\t\t\t</control>',
              '\t\t\t<control type="label">', f'\t\t\t\t<left>{x}</left>', '\t\t\t\t<top>20</top>',
              f'\t\t\t\t<width>{w - 16}</width>', '\t\t\t\t<height>30</height>', '\t\t\t\t<align>center</align>',
              '\t\t\t\t<font>lbln_20</font>', f'\t\t\t\t<textcolor>$VAR[SkinSet_Opt_{rid}]</textcolor>',
              f'\t\t\t\t<label>{esc(word)}</label>', '\t\t\t</control>']
    o.append('\t\t</control>')
    return o


def main():
    o = ['<?xml version="1.0" encoding="UTF-8"?>', '<!-- GENERATED by _src/make_skinsettings.py - edit the generator. -->',
         '<!--', '\tSkin settings: six lines on the left page, the choice circled in pen; a print from the diary on the right',
         '\tshows the stamp and the tilt. Rows 9510-9515 (one focus each; Left/Right change, OK cycles), 9516 the menu (HideMenu.*), 9517-9519 custom rows (right page; OK opens the options of that row, favourites list 9889), 9520-9522 custom menu items (right page, above the rows). 9590 preview data.', '-->',
         '<window>', '\t<defaultcontrol always="true">9510</defaultcontrol>', '\t<backgroundcolor>paper</backgroundcolor>',
         '\t<include>Anim_WindowOpenClose</include>', '\t<controls>', '\t\t<include>KS_Page</include>',
         '\t\t<include content="KS_TopBar">', '\t\t\t<param name="title" value="skin settings"/>',
         '\t\t\t<param name="sub" value="keepsake  ·  [COLOR label_hi]left and right change a line[/COLOR]"/>', '\t\t</include>']
    for i, (rid, label, help_, opts) in enumerate(ROWS):
        o += row(i, rid, label, help_, opts)
    o += menu_row()
    o += cmenu_line()
    o += custom_line()
    o.append('\t\t<include>CustomRows_FavData</include>')
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
    OUT.write_text(finish_xml(strip_defaults("\n".join(o), OUT.parent / "Defaults.xml")), encoding="utf-8", newline="\n")
    inc = ['<?xml version="1.0" encoding="UTF-8"?>', '<!-- GENERATED by _src/make_skinsettings.py -->', '<includes>']
    for rid, label, help_, opts in ROWS + [(MENU_ID, None, MENU_HELP, None)]:
        inc += [f'\t<variable name="SkinSet_Ink_{rid}">', f'\t\t<value condition="Control.HasFocus({rid})">ink_bold</value>',
                '\t\t<value>ink_soft</value>', '\t</variable>',
                f'\t<variable name="SkinSet_Opt_{rid}">', f'\t\t<value condition="Control.HasFocus({rid})">ink_bold</value>',
                '\t\t<value>label_hi</value>', '\t</variable>']
    inc.append('\t<variable name="SkinSet_Help">')
    for rid, label, help_, opts in ROWS + [(MENU_ID, None, MENU_HELP, None)]:
        inc.append(f'\t\t<value condition="Control.HasFocus({rid})">{esc(help_)}</value>')
    for cid in CUSTOM_IDS:
        inc.append(f'\t\t<value condition="Control.HasFocus({cid})">$LOCALIZE[31964]</value>')
    for cid in CMENU_IDS:
        inc.append(f'\t\t<value condition="Control.HasFocus({cid})">$LOCALIZE[31994]</value>')
    inc.append('\t</variable>')
    focus_custom = " | ".join(f"Control.HasFocus({c})" for c in CUSTOM_IDS)
    inc += ['\t<variable name="SkinSet_Ink_Custom">', f'\t\t<value condition="{focus_custom}">ink_bold</value>',
            '\t\t<value>ink_soft</value>', '\t</variable>', '\t<variable name="SkinSet_CustomValue">']
    for k, cid in enumerate(CUSTOM_IDS, 1):
        inc.append(f'\t\t<value condition="Control.HasFocus({cid})">$LOCALIZE[{31940 + k}]  ·  $VAR[CustomRow_Value{k}]</value>')
    for k, cid in enumerate(CMENU_IDS, 1):
        inc.append(f'\t\t<value condition="Control.HasFocus({cid})">$LOCALIZE[{31980 + k}]  ·  $VAR[CustomMenu_Value{k}]</value>')
    inc.append('\t</variable>')
    focus_cmenu = " | ".join(f"Control.HasFocus({c})" for c in CMENU_IDS)
    inc += ['\t<variable name="SkinSet_Ink_CMenu">', f'\t\t<value condition="{focus_cmenu}">ink_bold</value>',
            '\t\t<value>ink_soft</value>', '\t</variable>']
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
    (OUT.parent / "Includes_SkinSettings.xml").write_text(finish_xml("\n".join(inc)), encoding="utf-8", newline="\n")
    print("wrote", OUT.name, "+ Includes_SkinSettings.xml")


if __name__ == "__main__":
    main()
