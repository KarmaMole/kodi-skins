"""Generate 1080i/SkinSettings.xml (Daylight skin settings page).

Rows are ONE focus target each: Left / Right step through the options and apply at once (Left on the
first option returns to the categories), OK cycles, Back returns to the categories. Segment widths
are measured from Figtree Bold 22 (+32 px padding) so every row is right-aligned at x 860.
Settings and defaults: docs/skin.daylight/SETTINGS.md.

Usage: python skins/skin.daylight/_src/make_skinsettings.py
"""
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "1080i" / "SkinSettings.xml"
FONT = ImageFont.truetype(str(HERE.parent / "fonts" / "Figtree-Bold.ttf"), 22)
ROW_RIGHT = 860


def w(text):
    return round(FONT.getlength(text)) + 32


# Each option: (label, condition that it is the current value, action to select it)
def opts_string(name, values, default):
    out = []
    for key, label in values:
        if key == default:
            cond = f"[String.IsEmpty(Skin.String({name})) | String.IsEqual(Skin.String({name}),{key})]"
        else:
            cond = f"String.IsEqual(Skin.String({name}),{key})"
        out.append((label, cond, f"Skin.SetString({name},{key})"))
    return out


def opts_bool(name, off_label, on_label, inverted=False):
    """bool setting: off = default. inverted: the visible 'On' means the bool is NOT set."""
    if inverted:
        return [(on_label, f"!Skin.HasSetting({name})", f"Skin.Reset({name})"),
                (off_label, f"Skin.HasSetting({name})", f"Skin.SetBool({name})")]
    return [(off_label, f"!Skin.HasSetting({name})", f"Skin.Reset({name})"),
            (on_label, f"Skin.HasSetting({name})", f"Skin.SetBool({name})")]


CATS = [
    ("time", "Time &amp; mood", 9550),
    ("look", "Look", 9551),
    ("playback", "Playback", 9552),
    ("motion", "Motion &amp; reset", 9553),
]

ROWS = {
    "time": [
        (9510, "Mood", "Palette by the clock", "seg",
         opts_string("daylight.mood", [("auto", "Auto"), ("morning", "Morning"), ("afternoon", "Afternoon"),
                                       ("evening", "Evening"), ("night", "Night")], "auto")),
        (9511, "Bedtime", "Countdown and fits-before rows", "bedtime", None),
        (9512, "Weather row and rain", "Uses weather.gismeteo", "seg",
         opts_bool("daylight.noweather", "Off", "On", inverted=True)),
    ],
    "look": [
        (9520, "Borrowed colour", "The focused film tints the light", "seg",
         opts_bool("daylight.noartcolour", "Off", "On", inverted=True)),
        (9521, "Watched indicators", "Dots and checks on posters", "seg",
         opts_string("daylight.watchedmarkers", [("unwatched", "Unwatched"), ("watched", "Watched"),
                                                 ("both", "Both"), ("off", "Off")], "both")),
        (9522, "Trailer button", "Only when a film has a trailer", "seg",
         opts_bool("daylight.hidetrailer", "Show", "Hide")),
    ],
    "playback": [
        (9530, "OSD auto-hide", "Controls close by themselves", "seg",
         opts_string("daylight.osdhide", [("off", "Off"), ("3", "3 s"), ("5", "5 s"), ("10", "10 s")], "5")),
        (9531, "Offset strip", "Subtitle / audio sync strip", "seg",
         opts_string("daylight.offsetbar", [("top", "Top"), ("bottom", "Bottom")], "top")),
    ],
    "motion": [
        (9540, "Reduce motion", "Fades instead of zooms and slides", "seg",
         opts_bool("daylight.reducemotion", "Off", "On")),
        (9541, "Reset all skin settings", "Back to the defaults", "reset", None),
    ],
}

HELP = {
    9550: "When Daylight changes its colours, what counts as bedtime, and whether the weather may pick a row.[CR][CR]Up / Down picks a group, Right enters it.",
    9551: "How much of each film's own colour reaches the page, and the small markers on posters.",
    9552: "How the playback controls behave.",
    9553: "Motion, and a way back to the defaults.",
    9510: "Auto follows the clock: pale morning (6-11), bright afternoon (11-17), amber evening (17-22) and a dim deep-blue night (22-6). Pick one to keep it all day.[CR][CR]Greetings and suggestions always follow the real time.",
    9511: "Home counts down to it, the first card shows films that end before it, and the playback controls tell you when a film runs past it. Midnight says \"midnight\".",
    9512: "When it rains or snows, the third card on Home suggests something long and a few slow streaks drift over the page. Off keeps the weather in the top line only.",
    9520: "TMDb Helper reads the colour of the focused poster and Daylight lets it glow softly behind the page, gentler at night.[CR][CR]Needs TMDb Helper; Off uses nothing.",
    9521: "Unwatched: a small dot. Watched: a check disc. Shows add the number of unwatched episodes.",
    9522: "Shows a Trailer button next to Play when a film has a trailer link (played through the YouTube add-on).",
    9530: "How long the playback controls stay up after your last button press. They stay while paused and while a menu is open.",
    9531: "Where the subtitle and audio offset strip appears while you sync. Top keeps bottom subtitles in view.",
    9540: "Replaces zooms, slides and the rain with short fades. Focus changes stay instant.",
    9541: "Puts every Daylight setting back to its default and reloads the skin. Press OK twice to confirm.",
}


def esc(s):
    return s.replace("&", "&amp;").replace("&amp;amp;", "&amp;").replace('"', "&quot;")


def main():
    L = []
    a = L.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a("<!-- GENERATED by _src/make_skinsettings.py - edit the generator, not this file. -->")
    a("<!--")
    a("\tDaylight skin settings. Four groups (Time & mood, Look, Playback, Motion & reset); each row is one")
    a("\tfocus target, Left / Right apply at once, Back returns to the groups.")
    a("\tGroup = Window(Home).Property(daylight.skincat). Ids: groups 9550-9553, rows 9510-9541.")
    a("-->")
    a("<window>")
    a('\t<defaultcontrol always="true">9550</defaultcontrol>')
    a("\t<backgroundcolor>ff000000</backgroundcolor>")
    a("\t<onload>SetProperty(daylight.skincat,time,home)</onload>")
    a("\t<onload>ClearProperty(daylight.resetarmed,home)</onload>")
    a("\t<include>Anim_WindowOpenClose</include>")
    a("\t<controls>")
    a("\t\t<include>DL_Background</include>")
    a('\t\t<include content="DL_TopBar"><param name="title" value="Daylight settings"/></include>')
    # categories
    a("\t\t<control type=\"group\">")
    a("\t\t\t<left>page_margin</left>")
    ids = [c[2] for c in CATS]
    for i, (key, label, cid) in enumerate(CATS):
        first_row = ROWS[key][0][0]
        a('\t\t\t<include content="Dlg_SkinCategory">')
        a(f'\t\t\t\t<param name="id" value="{cid}"/><param name="top" value="{176 + i * 84}"/>')
        a(f'\t\t\t\t<param name="label" value="{label}"/><param name="key" value="{key}"/>')
        a(f'\t\t\t\t<param name="onright" value="{first_row}"/><param name="onup" value="{ids[i - 1]}"/><param name="ondown" value="{ids[(i + 1) % len(ids)]}"/>')
        a("\t\t\t</include>")
    a("\t\t</control>")
    # rows card
    a("\t\t<control type=\"group\">")
    a("\t\t\t<left>540</left><top>168</top><width>980</width><height>848</height>")
    a("\t\t\t<include>DL_Card</include>")
    a("\t\t</control>")
    for key, label, cid in CATS:
        rows = ROWS[key]
        a("\t\t<control type=\"group\">")
        a("\t\t\t<left>600</left>")
        a(f"\t\t\t<visible>String.IsEqual(Window(Home).Property(daylight.skincat),{key})</visible>")
        a("\t\t\t<include>Anim_FadeVisible</include>")
        for r, (rid, rlabel, hint, kind, opts) in enumerate(rows):
            up = rows[r - 1][0]
            down = rows[(r + 1) % len(rows)][0]
            a("\t\t\t<control type=\"group\">")
            a(f"\t\t\t\t<top>{208 + r * 116}</top>")
            a('\t\t\t\t<include content="Dlg_SkinRowChrome">')
            a(f'\t\t\t\t\t<param name="id" value="{rid}"/><param name="label" value="{rlabel}"/><param name="hint" value="{esc(hint)}"/>')
            if rid == 9520:
                a('\t\t\t\t\t<param name="enable" value="System.AddonIsEnabled(plugin.video.themoviedb.helper)"/>')
            a("\t\t\t\t</include>")
            a(f'\t\t\t\t<control type="button" id="{rid}">')
            a("\t\t\t\t\t<include>Dlg_SkinRowButton</include>")
            a(f"\t\t\t\t\t<onup>{up}</onup>")
            a(f"\t\t\t\t\t<ondown>{down}</ondown>")
            a(f"\t\t\t\t\t<onback>{cid}</onback>")
            if kind == "seg":
                n = len(opts)
                for i, (olabel, cond, act) in enumerate(opts):
                    nxt = opts[(i + 1) % n]
                    prv = opts[i - 1]
                    a(f'\t\t\t\t\t<onclick condition="{cond}">{nxt[2]}</onclick>')
                    if i < n - 1:
                        a(f'\t\t\t\t\t<onright condition="{cond}">{nxt[2]}</onright>')
                    if i == 0:
                        a(f'\t\t\t\t\t<onleft condition="{cond}">SetFocus({cid})</onleft>')
                    else:
                        a(f'\t\t\t\t\t<onleft condition="{cond}">{prv[2]}</onleft>')
                if rid == 9520:
                    # keep TMDb Helper's colour switch in step
                    a('\t\t\t\t\t<onclick condition="Skin.HasSetting(daylight.noartcolour)">Skin.SetBool(TMDbHelper.EnableColors)</onclick>')
                    a('\t\t\t\t\t<onclick condition="!Skin.HasSetting(daylight.noartcolour)">Skin.Reset(TMDbHelper.EnableColors)</onclick>')
                    a("\t\t\t\t\t<enable>System.AddonIsEnabled(plugin.video.themoviedb.helper)</enable>")
            elif kind == "bedtime":
                a('\t\t\t\t\t<onclick>Skin.SetString(daylight.bedtime,$VAR[DL_NextBedtime])</onclick>')
                a('\t\t\t\t\t<onright>Skin.SetString(daylight.bedtime,$VAR[DL_NextBedtime])</onright>')
                a('\t\t\t\t\t<onleft>Skin.SetString(daylight.bedtime,$VAR[DL_PrevBedtime])</onleft>')
            elif kind == "reset":
                a('\t\t\t\t\t<onclick condition="String.IsEmpty(Window(Home).Property(daylight.resetarmed))">SetProperty(daylight.resetarmed,1,home)</onclick>')
                a('\t\t\t\t\t<onclick condition="!String.IsEmpty(Window(Home).Property(daylight.resetarmed))">Skin.ResetSettings</onclick>')
                a('\t\t\t\t\t<onclick condition="!String.IsEmpty(Window(Home).Property(daylight.resetarmed))">ReloadSkin()</onclick>')
                a(f"\t\t\t\t\t<onleft>SetFocus({cid})</onleft>")
                a("\t\t\t\t\t<onunfocus>ClearProperty(daylight.resetarmed,home)</onunfocus>")
            a("\t\t\t\t</control>")
            if kind == "seg":
                widths = [w(o[0]) for o in opts]
                x = ROW_RIGHT - sum(widths)
                for (olabel, cond, act), ww in zip(opts, widths):
                    a(f'\t\t\t\t<include content="Dlg_SegOption"><param name="left" value="{x}"/><param name="width" value="{ww}"/><param name="label" value="{olabel}"/><param name="selected" value="{cond}"/><param name="row" value="{rid}"/></include>')
                    x += ww
                a(f'\t\t\t\t<include content="Dlg_SegFrame"><param name="left" value="{ROW_RIGHT - sum(widths)}"/><param name="width" value="{sum(widths)}"/></include>')
            elif kind == "bedtime":
                a('\t\t\t\t<include content="Dlg_StepValue">')
                a(f'\t\t\t\t\t<param name="row" value="{rid}"/><param name="label" value="$VAR[DL_BedtimeLabelLong]"/>')
                a("\t\t\t\t</include>")
            elif kind == "reset":
                a('\t\t\t\t<control type="label"><left>400</left><top>0</top><width>460</width><height>100</height><align>right</align><font>small_20_semibold</font><textcolor>$VAR[DL_Ink2]</textcolor><label>OK to reset</label><visible>String.IsEmpty(Window(Home).Property(daylight.resetarmed))</visible></control>')
                a('\t\t\t\t<control type="label"><left>400</left><top>0</top><width>460</width><height>100</height><align>right</align><font>small_20_bold</font><textcolor>$VAR[DL_AccentText]</textcolor><label>Press OK again to reset everything</label><visible>!String.IsEmpty(Window(Home).Property(daylight.resetarmed))</visible></control>')
            a("\t\t\t</control>")
        a("\t\t</control>")
    # aside: help card
    a("\t\t<control type=\"group\">")
    a("\t\t\t<left>1556</left><top>168</top><width>244</width><height>848</height>")
    a("\t\t\t<control type=\"image\"><left>0</left><top>0</top><width>34</width><height>34</height><texture colordiffuse=\"$VAR[DL_Accent]\">$VAR[DL_MoodIcon]</texture></control>")
    a("\t\t\t<control type=\"textbox\"><left>0</left><top>56</top><width>244</width><height>720</height><font>ui_22_reg</font><textcolor>$VAR[DL_Ink2]</textcolor><label>$VAR[Dlg_SkinHelp]</label></control>")
    a("\t\t</control>")
    a("\t</controls>")
    a("</window>")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

    # help variable -> Includes_Settings.xml block between markers
    inc = HERE.parent / "1080i" / "Includes_Settings.xml"
    s = inc.read_text(encoding="utf-8")
    start = s.index("\t<variable name=\"Dlg_SkinHelp\">")
    end = s.index("</variable>", start) + len("</variable>")
    v = ["\t<variable name=\"Dlg_SkinHelp\">"]
    for cid, text in HELP.items():
        v.append(f'\t\t<value condition="Control.HasFocus({cid})">{text.replace("&", "&amp;").replace("&amp;amp;", "&amp;")}</value>')
    v.append("\t\t<value>Daylight's own options. Kodi's settings live under Settings; switch skins in Settings &gt; Interface &gt; Skin.</value>")
    v.append("\t</variable>")
    s = s[:start] + "\n".join(v) + s[end:]
    inc.write_text(s, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
