"""Generate skins/skin.duotone/1080i/SkinSettings.xml (docs/skin.duotone/SETTINGS.md).

One page, paper field (Search / Settings section). Left column: Anton "SKIN" + the focused row's help.
Right column: 10 rows of 80. Each row is ONE focus target: Left / Right step through the options and
apply at once (Left on the first option returns... nowhere: the page has no other column), OK cycles.
The current option is a chip: ink block + paper text on a resting row, paper block + ink text on the
focused (ink) row. Spotlight interval runs ReloadSkin() from the row itself (Home reads <autoscroll time>
at skin load) and restores focus through Window(Home).Property(duotone.refocus) - never from onunload
(LESSONS 2). Reset is armed by a first press (duotone.resetarmed) and fires on the second.

Usage: python skins/skin.duotone/_src/make_skinsettings.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "SkinSettings.xml"
S = "Skin.String"


def eq(name, val):
    return f"String.IsEqual({S}({name}),{val})"


def empty_or(name, val):
    return f"[String.IsEmpty({S}({name})) | {eq(name, val)}]"


# Each row: id, label, help, kind, setting, options [(stored, label, condition)], reload
ROWS = [
    dict(id=9501, label="Monotone prints", help="Every picture in a section is printed in its colour; the focused one bursts into full colour. Light keeps more of the art. Off shows everything in colour.",
         kind="string", name="duotone.mono",
         opts=[("", "Full", f"String.IsEmpty({S}(duotone.mono))"), ("light", "Light", eq("duotone.mono", "light")), ("off", "Off", eq("duotone.mono", "off"))]),
    dict(id=9502, label="True black and white", help="TMDb Helper turns the big artwork (Home spotlight, info page) into a black-and-white print first, so the section colour prints cleanly. Off: the colour art is tinted.",
         kind="bool_inv", name="duotone.nodesaturate",
         opts=[(None, "On", "!Skin.HasSetting(duotone.nodesaturate)"), (None, "Off", "Skin.HasSetting(duotone.nodesaturate)")]),
    dict(id=9503, label="Halftone dots", help="The fine dot screen over every field and print.",
         kind="bool_inv", name="duotone.nohalftone",
         opts=[(None, "On", "!Skin.HasSetting(duotone.nohalftone)"), (None, "Off", "Skin.HasSetting(duotone.nohalftone)")]),
    dict(id=9504, label="Reduce motion", help="No field wipe, no focus zoom, no slides: short fades only.",
         kind="bool", name="duotone.reducemotion",
         opts=[(None, "Off", "!Skin.HasSetting(duotone.reducemotion)"), (None, "On", "Skin.HasSetting(duotone.reducemotion)")]),
    dict(id=9505, label="Watched marks", help="Watched: a black block with a tick on watched posters. Both adds a small square on unwatched ones.",
         kind="string", name="duotone.watchedmarkers",
         opts=[("", "Watched", f"[String.IsEmpty({S}(duotone.watchedmarkers)) | {eq('duotone.watchedmarkers','watched')}]"),
               ("both", "Both", eq("duotone.watchedmarkers", "both")), ("unwatched", "Unwatched", eq("duotone.watchedmarkers", "unwatched")),
               ("off", "Off", eq("duotone.watchedmarkers", "off"))]),
    dict(id=9506, label="Trailer block", help="Show TRAILER on the info page when a film has a trailer (plays via YouTube).",
         kind="bool_inv", name="duotone.hidetrailer",
         opts=[(None, "Show", "!Skin.HasSetting(duotone.hidetrailer)"), (None, "Hide", "Skin.HasSetting(duotone.hidetrailer)")]),
    dict(id=9507, label="Spotlight rotation", help="How often the Home spotlight moves to the next pick. Changing it reloads the skin.",
         kind="string", name="duotone.spotlightrotate", reload=True,
         opts=[("8", "8 s", eq("duotone.spotlightrotate", "8")), ("", "15 s", f"[String.IsEmpty({S}(duotone.spotlightrotate)) | {eq('duotone.spotlightrotate','15')}]"),
               ("30", "30 s", eq("duotone.spotlightrotate", "30")), ("off", "Off", eq("duotone.spotlightrotate", "off"))]),
    dict(id=9508, label="OSD auto-hide", help="Seconds of no input before the playback controls hide by themselves (not while paused).",
         kind="string", name="duotone.osdhide",
         opts=[("3", "3 s", eq("duotone.osdhide", "3")), ("", "5 s", f"[String.IsEmpty({S}(duotone.osdhide)) | {eq('duotone.osdhide','5')}]"),
               ("10", "10 s", eq("duotone.osdhide", "10")), ("off", "Off", eq("duotone.osdhide", "off"))]),
    dict(id=9509, label="Offset strip", help="Where the slim strip sits while you sync audio or subtitles.",
         kind="string", name="duotone.offsetbar",
         opts=[("", "Top", f"[String.IsEmpty({S}(duotone.offsetbar)) | {eq('duotone.offsetbar','top')}]"), ("bottom", "Bottom", eq("duotone.offsetbar", "bottom"))]),
]
RESET_ID = 9510
FIRST, LAST = ROWS[0]["id"], RESET_ID
ROW_TOP, ROW_H = 176, 80


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
    a('\t\t\t\t<texturefocus colordiffuse="ink">common/white.png</texturefocus>')
    a('\t\t\t\t<texturenofocus border="0,0,0,4" colordiffuse="$VAR[SectionText]">dialogs/row_rule.png</texturenofocus>')
    a(f'\t\t\t\t<onup>{up}</onup>\n\t\t\t\t<ondown>{down}</ondown>')
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
    for vis, col in ((f"!Control.HasFocus({rid})", "$VAR[SectionText]"), (f"Control.HasFocus({rid})", "paper")):
        a('\t\t\t<control type="label">')
        a(f'\t\t\t\t<left>24</left>\n\t\t\t\t<top>0</top>\n\t\t\t\t<width>480</width>\n\t\t\t\t<height>{ROW_H}</height>')
        a(f'\t\t\t\t<aligny>center</aligny>\n\t\t\t\t<font>bold_28</font>\n\t\t\t\t<textcolor>{col}</textcolor>')
        a(f'\t\t\t\t<label>{row["label"]}</label>\n\t\t\t\t<visible>{vis}</visible>')
        a('\t\t\t</control>')
    # chips
    a('\t\t\t<control type="grouplist">')
    a(f'\t\t\t\t<left>440</left>\n\t\t\t\t<top>18</top>\n\t\t\t\t<width>568</width>\n\t\t\t\t<height>44</height>')
    a('\t\t\t\t<orientation>horizontal</orientation>\n\t\t\t\t<align>right</align>\n\t\t\t\t<itemgap>4</itemgap>')
    for opt in opts:
        cond = opt[2]
        variants = [
            (f"!Control.HasFocus({rid}) + [{cond}]", "ink", "paper"),           # resting row, current
            (f"!Control.HasFocus({rid}) + ![{cond}]", None, "$VAR[SectionText2]"),
            (f"Control.HasFocus({rid}) + [{cond}]", "$VAR[SectionColor]", "$VAR[SectionText]"),
            (f"Control.HasFocus({rid}) + ![{cond}]", None, "paper_70"),
        ]
        for vis, fill, txt in variants:
            a('\t\t\t\t<control type="button">')
            a('\t\t\t\t\t<width>auto</width>\n\t\t\t\t\t<height>44</height>\n\t\t\t\t\t<font>cap_20</font>')
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
    reset_top = ROW_TOP + len(ROWS) * ROW_H + 24
    helps = "\n".join(f'\t\t<value condition="Control.HasFocus({r["id"]})">{r["help"]}</value>' for r in ROWS)
    refocus = "\n".join(f'\t<onload condition="String.IsEqual(Window(Home).Property(duotone.refocus),{r["id"]})">SetFocus({r["id"]})</onload>' for r in ROWS if r.get("reload"))
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_skinsettings.py - edit the table there, not this file.
	Duotone skin settings (docs/skin.duotone/SETTINGS.md). Paper field. Rows 9501-9509, reset 9510.
	Each row is one focus target: Left / Right step through the options and apply at once, OK cycles.
	Spotlight rotation reloads the skin from the row itself and refocuses through duotone.refocus. -->
<window>
	<defaultcontrol always="true">{FIRST}</defaultcontrol>
	<backgroundcolor>ff111111</backgroundcolor>
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
		<!-- the four section colours, as printed -->
		<control type="group">
			<left>page_margin</left>
			<top>848</top>
			<width>696</width>
			<height>168</height>
			<control type="image"><left>0</left><top>0</top><width>168</width><height>168</height><texture colordiffuse="vermilion">common/white.png</texture></control>
			<control type="image"><left>176</left><top>0</top><width>168</width><height>168</height><texture colordiffuse="cobalt">common/white.png</texture></control>
			<control type="image"><left>352</left><top>0</top><width>168</width><height>168</height><texture colordiffuse="acid">common/white.png</texture></control>
			<control type="image"><left>528</left><top>0</top><width>168</width><height>168</height><texture border="16" colordiffuse="ink">common/rect_outline_8.png</texture></control>
			<control type="label"><left>16</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>ink</textcolor><label>Films</label></control>
			<control type="label"><left>192</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>paper</textcolor><label>Series</label></control>
			<control type="label"><left>368</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>ink</textcolor><label>Music</label></control>
			<control type="label"><left>544</left><top>124</top><width>150</width><height>24</height><font>cap_20</font><textcolor>ink</textcolor><label>System</label></control>
		</control>
		<include content="DT_RuleV"><param name="left" value="772"/><param name="top" value="176"/><param name="height" value="840"/></include>
		<include content="DT_RuleThick"><param name="top" value="168"/><param name="left" value="824"/><param name="width" value="1032"/></include>
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
				<focusedcolor>paper</focusedcolor>
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
    OUT.write_text(xml, encoding="utf-8", newline="\n")
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
    inc.write_text(s, encoding="utf-8", newline="\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
