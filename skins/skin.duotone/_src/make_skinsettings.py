"""Generate skins/skin.duotone/1080i/SkinSettings.xml (docs/skin.duotone/SETTINGS.md).

One page, paper field (Search / Settings section). Left column: Anton "SKIN" + the focused row's help.
Right column: 13 rows of 58 + Reset (0.9.13: 3 main menu rows). Each row is ONE focus target: Left / Right step through the options and
apply at once (Left on the first option returns... nowhere: the page has no other column), OK cycles.
The current option is a chip: ink block + paper text on a resting row, paper block + ink text on the
focused (ink) row. Spotlight interval runs ReloadSkin() from the row itself (Home reads <autoscroll time>
at skin load) and restores focus through Window(Home).Property(duotone.refocus) - never from onunload
(LESSONS 2). Reset is armed by a first press (duotone.resetarmed) and fires on the second.

Usage: python skins/skin.duotone/_src/make_skinsettings.py
"""
from pathlib import Path
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

OUT = Path(__file__).resolve().parents[1] / "1080i" / "SkinSettings.xml"
S = "Skin.String"


def eq(name, val):
    return f"String.IsEqual({S}({name}),{val})"


def empty_or(name, val):
    return f"[String.IsEmpty({S}({name})) | {eq(name, val)}]"


# Each row: label, help, kind, setting, options [(stored, label, condition)], reload. Ids are 9501... in table order.
LOOK_LIGHT, LOOK_DARK = eq("duotone.look", "light"), eq("duotone.look", "dark")
ROWS = [
    dict(label="Look", help="Colour: every section in its own colour. Light and Dark: the same pages in black and white, near-white or near-black. The focused picture still bursts into full colour.",
         kind="string", name="duotone.look",
         opts=[("", "Colour", f"!{LOOK_LIGHT} + !{LOOK_DARK}"), ("light", "Light", LOOK_LIGHT), ("dark", "Dark", LOOK_DARK)]),
    dict(label="Monotone prints", help="Every picture in a section is printed in its colour; the focused one bursts into full colour. Light keeps more of the art. Off shows everything in colour.",
         kind="string", name="duotone.mono",
         opts=[("", "Full", f"String.IsEmpty({S}(duotone.mono))"), ("light", "Light", eq("duotone.mono", "light")), ("off", "Off", eq("duotone.mono", "off"))]),
    dict(label="True black and white", help="TMDb Helper turns the big artwork (Home spotlight, info page) into a black-and-white print first, so the section colour prints cleanly. Off: the colour art is tinted.",
         kind="bool_inv", name="duotone.nodesaturate",
         opts=[(None, "On", "!Skin.HasSetting(duotone.nodesaturate)"), (None, "Off", "Skin.HasSetting(duotone.nodesaturate)")]),
    dict(label="Halftone dots", help="The fine dot screen over every field and print.",
         kind="bool_inv", name="duotone.nohalftone",
         opts=[(None, "On", "!Skin.HasSetting(duotone.nohalftone)"), (None, "Off", "Skin.HasSetting(duotone.nohalftone)")]),
    dict(label="Reduce motion", help="No field wipe, no focus zoom, no slides: short fades only.",
         kind="bool", name="duotone.reducemotion",
         opts=[(None, "Off", "!Skin.HasSetting(duotone.reducemotion)"), (None, "On", "Skin.HasSetting(duotone.reducemotion)")]),
    dict(label="Watched marks", help="Watched: an ink block with a tick on watched posters. Both adds a small square on unwatched ones.",
         kind="string", name="duotone.watchedmarkers",
         opts=[("", "Watched", f"[String.IsEmpty({S}(duotone.watchedmarkers)) | {eq('duotone.watchedmarkers','watched')}]"),
               ("both", "Both", eq("duotone.watchedmarkers", "both")), ("unwatched", "Unwatched", eq("duotone.watchedmarkers", "unwatched")),
               ("off", "Off", eq("duotone.watchedmarkers", "off"))]),
    dict(label="Trailer block", help="Show TRAILER on the info page when a film has a trailer (plays via YouTube).",
         kind="bool_inv", name="duotone.hidetrailer",
         opts=[(None, "Show", "!Skin.HasSetting(duotone.hidetrailer)"), (None, "Hide", "Skin.HasSetting(duotone.hidetrailer)")]),
    dict(label="Spotlight rotation", help="How often the Home spotlight moves to the next pick. Changing it reloads the skin.",
         kind="string", name="duotone.spotlightrotate", reload=True,
         opts=[("8", "8 s", eq("duotone.spotlightrotate", "8")), ("", "15 s", f"[String.IsEmpty({S}(duotone.spotlightrotate)) | {eq('duotone.spotlightrotate','15')}]"),
               ("30", "30 s", eq("duotone.spotlightrotate", "30")), ("off", "Off", eq("duotone.spotlightrotate", "off"))]),
    dict(label="OSD auto-hide", help="Seconds of no input before the playback controls hide by themselves (not while paused).",
         kind="string", name="duotone.osdhide",
         opts=[("3", "3 s", eq("duotone.osdhide", "3")), ("", "5 s", f"[String.IsEmpty({S}(duotone.osdhide)) | {eq('duotone.osdhide','5')}]"),
               ("10", "10 s", eq("duotone.osdhide", "10")), ("off", "Off", eq("duotone.osdhide", "off"))]),
    dict(label="Offset strip", help="Where the slim strip sits while you sync audio or subtitles.",
         kind="string", name="duotone.offsetbar",
         opts=[("", "Top", f"[String.IsEmpty({S}(duotone.offsetbar)) | {eq('duotone.offsetbar','top')}]"), ("bottom", "Bottom", eq("duotone.offsetbar", "bottom"))]),
]
# 0.9.13 main menu: which sections the Home stack shows (HideMenu.* bools; Search, with the settings, never hides)
_MENU_HELP = ("Takes the section off the Home stack, with its spotlight and rows; the others move up. "
              "Search stays, with the settings and power, so you can always come back here.")
for _label, _key in (("Home: Films", "Movies"), ("Home: Series", "TVShows"), ("Home: Music", "Music")):
    ROWS.append(dict(label=_label, help=_MENU_HELP, kind="bool", name=f"HideMenu.{_key}",
                     opts=[(None, "Show", f"!Skin.HasSetting(HideMenu.{_key})"), (None, "Hide", f"Skin.HasSetting(HideMenu.{_key})")]))
# 0.9.13 custom rows on Home: OK opens the row's options (Includes_CustomRows.xml, tools/customrows/make_customrows.py)
for _n in (1, 2, 3):
    ROWS.append(dict(label=f"$LOCALIZE[{31940 + _n}]", help="$LOCALIZE[31950]", kind="custom", row=_n, opts=[]))
for _i, _r in enumerate(ROWS):
    _r["id"] = 9501 + _i
RESET_ID = 9501 + len(ROWS)
FIRST, LAST = ROWS[0]["id"], RESET_ID
ROW_TOP, ROW_H = 176, 50  # 0.9.13: 50 (was 72, then 58) so the main menu and custom rows fit; Reset keeps 72
CHIP_H = 40


def set_action(row, opt):
    stored = opt[0]
    k, n = row["kind"], row["name"]
    acts = []
    if k == "string":
        acts.append(f"Skin.Reset({n})" if stored == "" else f"Skin.SetString({n},{stored})")
    elif k in ("bool", "bool_inv"):
        # opts[0] = "false" state for bool, "true(=unset)" for bool_inv
        idx = row["opts"].index(opt)
        set_true = (idx == 1) if k == "bool" else (idx == 1)
        acts.append(f"Skin.SetBool({n})" if set_true else f"Skin.Reset({n})")
    if row.get("reload"):
        acts.append(f"SetProperty(duotone.refocus,{row['id']},home)")
        acts.append("ReloadSkin()")
    return acts


def row_xml(i, row):
    rid = row["id"]
    top = ROW_TOP + i * ROW_H
    up = rid - 1 if rid > FIRST else LAST
    down = rid + 1
    opts = row["opts"]
    lines = []
    a = lines.append
    a(f'\t\t<!-- {row["label"]} -->')
    a('\t\t<control type="group">')
    a(f'\t\t\t<left>824</left>\n\t\t\t<top>{top}</top>\n\t\t\t<width>1032</width>\n\t\t\t<height>{ROW_H}</height>')
    a(f'\t\t\t<control type="button" id="{rid}">')
    a(f'\t\t\t\t<left>0</left>\n\t\t\t\t<top>0</top>\n\t\t\t\t<width>1032</width>\n\t\t\t\t<height>{ROW_H}</height>')
    a('\t\t\t\t<label></label>')
    a('\t\t\t\t<texturefocus colordiffuse="$VAR[ink]">common/white.png</texturefocus>')
    a('\t\t\t\t<texturenofocus border="0,0,0,4" colordiffuse="$VAR[SectionText]">dialogs/row_rule.png</texturenofocus>')
    a(f'\t\t\t\t<onup>{up}</onup>\n\t\t\t\t<ondown>{down}</ondown>')
    if row["kind"] == "custom":
        a(f'\t\t\t\t<include content="CustomRows_SettingsClick"><param name="row" value="{row["row"]}"/><param name="heading" value="{row["label"]}"/></include>')
        a('\t\t\t\t<onleft>noop</onleft>\n\t\t\t\t<onright>noop</onright>')
    n = len(opts)
    for j, opt in enumerate(opts):
        cond = opt[2]
        nxt = opts[(j + 1) % n]
        for act in set_action(row, nxt):
            a(f'\t\t\t\t<onclick condition="{cond}">{act}</onclick>')
        if j + 1 < n:
            for act in set_action(row, opts[j + 1]):
                a(f'\t\t\t\t<onright condition="{cond}">{act}</onright>')
        if j > 0:
            for act in set_action(row, opts[j - 1]):
                a(f'\t\t\t\t<onleft condition="{cond}">{act}</onleft>')
    a('\t\t\t</control>')
    # label (two colours)
    for vis, col in ((f"!Control.HasFocus({rid})", "$VAR[SectionText]"), (f"Control.HasFocus({rid})", "$VAR[paper]")):
        a('\t\t\t<control type="label">')
        a(f'\t\t\t\t<left>24</left>\n\t\t\t\t<top>0</top>\n\t\t\t\t<width>480</width>\n\t\t\t\t<height>{ROW_H}</height>')
        a(f'\t\t\t\t<aligny>center</aligny>\n\t\t\t\t<font>bold_28</font>\n\t\t\t\t<textcolor>{col}</textcolor>')
        a(f'\t\t\t\t<label>{row["label"]}</label>\n\t\t\t\t<visible>{vis}</visible>')
        a('\t\t\t</control>')
    if row["kind"] == "custom":
        # value: the row's name (or "Not set"), right-aligned where the chips end
        k = row["row"]
        for vis, col in ((f"!Control.HasFocus({rid})", "$VAR[SectionText2]"), (f"Control.HasFocus({rid})", "$VAR[paper_70]")):
            a('\t\t\t<control type="label">')
            a(f'\t\t\t\t<left>440</left>\n\t\t\t\t<top>0</top>\n\t\t\t\t<width>568</width>\n\t\t\t\t<height>{ROW_H}</height>')
            a(f'\t\t\t\t<align>right</align>\n\t\t\t\t<aligny>center</aligny>\n\t\t\t\t<font>cap_20</font>\n\t\t\t\t<textcolor>{col}</textcolor>')
            a(f'\t\t\t\t<label>$VAR[CustomRow_Value{k}]</label>\n\t\t\t\t<visible>{vis}</visible>')
            a('\t\t\t</control>')
        a('\t\t</control>')
        return "\n".join(lines)
    # chips
    a('\t\t\t<control type="grouplist">')
    a(f'\t\t\t\t<left>440</left>\n\t\t\t\t<top>{(ROW_H - CHIP_H) // 2}</top>\n\t\t\t\t<width>568</width>\n\t\t\t\t<height>{CHIP_H}</height>')
    a('\t\t\t\t<orientation>horizontal</orientation>\n\t\t\t\t<align>right</align>\n\t\t\t\t<itemgap>4</itemgap>')
    for opt in opts:
        cond = opt[2]
        variants = [
            (f"!Control.HasFocus({rid}) + [{cond}]", "$VAR[ink]", "$VAR[paper]"),           # resting row, current
            (f"!Control.HasFocus({rid}) + ![{cond}]", None, "$VAR[SectionText2]"),
            (f"Control.HasFocus({rid}) + [{cond}]", "$VAR[SectionColor]", "$VAR[SectionText]"),
            (f"Control.HasFocus({rid}) + ![{cond}]", None, "$VAR[paper_70]"),
        ]
        for vis, fill, txt in variants:
            a('\t\t\t\t<control type="button">')
            a(f'\t\t\t\t\t<width>auto</width>\n\t\t\t\t\t<height>{CHIP_H}</height>\n\t\t\t\t\t<font>cap_20</font>')
            a(f'\t\t\t\t\t<textcolor>{txt}</textcolor>\n\t\t\t\t\t<focusedcolor>{txt}</focusedcolor>')
            a('\t\t\t\t\t<textoffsetx>16</textoffsetx>\n\t\t\t\t\t<aligny>center</aligny>')
            if fill:
                a(f'\t\t\t\t\t<texturenofocus colordiffuse="{fill}">common/white.png</texturenofocus>')
                a(f'\t\t\t\t\t<texturefocus colordiffuse="{fill}">common/white.png</texturefocus>')
            else:
                a('\t\t\t\t\t<texturenofocus />\n\t\t\t\t\t<texturefocus />')
            a(f'\t\t\t\t\t<label>{opt[1]}</label>')
            a(f'\t\t\t\t\t<onup>{rid}</onup><ondown>{rid}</ondown><onleft>{rid}</onleft><onright>{rid}</onright>')
            a(f'\t\t\t\t\t<visible>{vis}</visible>')
            a('\t\t\t\t</control>')
    a('\t\t\t</control>')
    a('\t\t</control>')
    return "\n".join(lines)


def help_var():
    out = ['\t\t<!-- help text for the focused row -->']
    return out


def main():
    rows = "\n".join(row_xml(i, r) for i, r in enumerate(ROWS))
    reset_top = ROW_TOP + len(ROWS) * ROW_H + 12
    helps = "\n".join(f'\t\t<value condition="Control.HasFocus({r["id"]})">{r["help"]}</value>' for r in ROWS)
    refocus = "\n".join(f'\t<onload condition="String.IsEqual(Window(Home).Property(duotone.refocus),{r["id"]})">SetFocus({r["id"]})</onload>' for r in ROWS if r.get("reload"))
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_skinsettings.py - edit the table there, not this file.
	Duotone skin settings (docs/skin.duotone/SETTINGS.md). Paper field. Rows {FIRST}-{RESET_ID - 1}, reset {RESET_ID}.
	Each row is one focus target: Left / Right step through the options and apply at once, OK cycles.
	Spotlight rotation reloads the skin from the row itself and refocuses through duotone.refocus. -->
<window>
	<defaultcontrol always="true">{FIRST}</defaultcontrol>
	<backgroundcolor>ground_static</backgroundcolor>
	<onload>ClearProperty(duotone.resetarmed,home)</onload>
{refocus}
	<onload>ClearProperty(duotone.refocus,home)</onload>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>DT_Background</include>
		<include content="DT_TopBar">
			<param name="title" value="Settings"/>
			<param name="sub" value="Duotone $INFO[System.AddonVersion(skin.duotone)]"/>
		</include>
		<!-- left column: Anton heading + help for the focused row -->
		<control type="label">
			<left>58</left>
			<top>170</top>
			<width>700</width>
			<height>212</height>
			<aligny>center</aligny>
			<font>an_236</font>
			<textcolor>$VAR[SectionText]</textcolor>
			<label>Skin</label>
		</control>
		<include content="DT_RuleThick"><param name="top" value="400"/><param name="width" value="696"/></include>
		<control type="label">
			<left>page_margin</left>
			<top>428</top>
			<width>696</width>
			<height>24</height>
			<font>cap_20</font>
			<textcolor>$VAR[SectionText]</textcolor>
			<label>$VAR[Skin_HelpTitle]</label>
		</control>
		<control type="textbox">
			<left>page_margin</left>
			<top>468</top>
			<width>696</width>
			<height>272</height>
			<font>body_26</font>
			<textcolor>$VAR[SectionText]</textcolor>
			<label>$VAR[Skin_Help]</label>
		</control>
		<!-- the four section colours, as printed (chip tokens: ink blocks in the Light / Dark looks) -->
		<control type="group">
			<left>page_margin</left>
			<top>848</top>
			<width>696</width>
			<height>168</height>
			<control type="image"><left>0</left><top>0</top><width>168</width><height>168</height><texture colordiffuse="$VAR[chip_films]">common/white.png</texture></control>
			<control type="image"><left>176</left><top>0</top><width>168</width><height>168</height><texture colordiffuse="$VAR[chip_series]">common/white.png</texture></control>
			<control type="image"><left>352</left><top>0</top><width>168</width><height>168</height><texture colordiffuse="$VAR[chip_music]">common/white.png</texture></control>
			<control type="image"><left>528</left><top>0</top><width>168</width><height>168</height><texture border="16" colordiffuse="$VAR[ink]">common/rect_outline_8.png</texture></control>
			<control type="label"><left>16</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>$VAR[chiptext_films]</textcolor><label>Films</label></control>
			<control type="label"><left>192</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>$VAR[chiptext_series]</textcolor><label>Series</label></control>
			<control type="label"><left>368</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>$VAR[chiptext_music]</textcolor><label>Music</label></control>
			<control type="label"><left>544</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>$VAR[ink]</textcolor><label>System</label></control>
		</control>
		<include content="DT_RuleV"><param name="left" value="772"/><param name="top" value="176"/><param name="height" value="840"/></include>
		<include content="DT_RuleThick"><param name="top" value="168"/><param name="left" value="824"/><param name="width" value="1032"/></include>
		<include>CustomRows_FavData</include>
{rows}
		<!-- reset: first OK arms, second OK resets everything and reloads -->
		<control type="group">
			<left>824</left>
			<top>{reset_top}</top>
			<width>1032</width>
			<height>72</height>
			<include content="Anim_BlockZoom"><param name="id" value="{RESET_ID}"/></include>
			<control type="button" id="{RESET_ID}">
				<left>0</left>
				<top>0</top>
				<width>1032</width>
				<height>72</height>
				<font>an_40</font>
				<align>center</align>
				<aligny>center</aligny>
				<textcolor>$VAR[SectionText]</textcolor>
				<focusedcolor>$VAR[paper]</focusedcolor>
				<label>$VAR[Skin_ResetLabel]</label>
				<include>DT_Tex_Block</include>
				<onup>{ROWS[-1]["id"]}</onup>
				<ondown>{FIRST}</ondown>
				<onclick condition="!String.IsEmpty(Window(Home).Property(duotone.resetarmed))">Skin.ResetSettings</onclick>
				<onclick condition="!String.IsEmpty(Window(Home).Property(duotone.resetarmed))">ReloadSkin()</onclick>
				<onclick condition="String.IsEmpty(Window(Home).Property(duotone.resetarmed))">SetProperty(duotone.resetarmed,1,home)</onclick>
				<onunfocus>ClearProperty(duotone.resetarmed,home)</onunfocus>
			</control>
		</control>
	</controls>
</window>
'''
    OUT.write_text(finish_xml(strip_defaults(xml, OUT.parent / "Defaults.xml")), encoding="utf-8", newline="\n")
    # variables used above live in Includes_Settings.xml (Skin_Help, Skin_HelpTitle, Skin_ResetLabel)
    inc = OUT.parent / "Includes_Settings.xml"
    s = inc.read_text(encoding="utf-8")
    start = s.find("\t<!-- SKINSETTINGS-GENERATED -->")
    if start != -1:
        end = s.index("\t<!-- /SKINSETTINGS-GENERATED -->") + len("\t<!-- /SKINSETTINGS-GENERATED -->\n")
        s = s[:start] + s[end:]
    titles = "\n".join(f'\t\t<value condition="Control.HasFocus({r["id"]})">{r["label"]}</value>' for r in ROWS)
    block = f'''	<!-- SKINSETTINGS-GENERATED -->
	<variable name="Skin_Help">
{helps}
		<value condition="Control.HasFocus({RESET_ID})">Puts every Duotone setting back to its default and reloads the skin. Press OK twice.</value>
	</variable>
	<variable name="Skin_HelpTitle">
{titles}
		<value>Reset</value>
	</variable>
	<variable name="Skin_ResetLabel">
		<value condition="!String.IsEmpty(Window(Home).Property(duotone.resetarmed))">Press OK again to reset</value>
		<value>Reset all</value>
	</variable>
	<!-- /SKINSETTINGS-GENERATED -->
'''
    k = s.rindex("</includes>")
    s = s[:k] + block + s[k:]
    inc.write_text(finish_xml(s), encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
