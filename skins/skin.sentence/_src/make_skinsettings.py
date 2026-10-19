"""Generate 1080i/SkinSettings.xml (+ Includes_SkinSettings.xml): Sentence's own settings, one sentence each.

  "Results wait [400 ms] after you stop spinning a phrase."   OK / Right = next value, Left = previous.
Every row: a horizontal grouplist (words + one phrase button); the rows stack in a vertical grouplist
(Up/Down). Left/Right sit on the ROW grouplist because a grouplist re-wires its children's
list-axis actions to its own. Rows whose value Home reads at skin load (rest time) reload the skin
from the row itself and come back via Window(Home).Property(sentence.refocus) (never from onunload).
Storage and meanings: docs/skin.sentence/SETTINGS.md.

Usage: python skins/skin.sentence/_src/make_skinsettings.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "1080i" / "SkinSettings.xml"

# id, before, after, kind, key, options[(stored, label)], help, reload
# kind "string": Skin.String, the FIRST option is the default (stored empty or as given)
# kind "bool":   Skin.HasSetting ("" = off, "1" = on)
ROWS = [
    (9510, "Results wait", "after you stop spinning.", "string", "sentence.resttime",
     [("normal", "400 ms"), ("patient", "700 ms"), ("quick", "250 ms")],
     "How long the results row waits after your last Up or Down before it asks the library again. "
     "Shorter feels livelier; longer is calmer. Changing it reloads the skin for a second.", True),
    (9511, "The Home sentence starts with", ".", "bool", "sentence.alwaystonight",
     [("", "the time of day"), ("1", "“Tonight”, always")],
     "“This morning I'd like…”, “This afternoon…”, “Tonight…”, or always “Tonight I'd like…”.", False),
    (9512, "Captions under posters say", ".", "string", "sentence.captions",
     [("", "when you'd finish"), ("facts", "the year and rating")],
     "Under every poster: “1 h 46 · finish 23:33”, or “2006 · rated 8.2”.", False),
    (9513, "The time sentence", ".", "bool", "sentence.noweather",
     [("", "mentions the weather"), ("1", "leaves the weather out")],
     "“It's 21:47 and light rain.” The weather comes from your weather add-on; "
     "without one it is left out anyway.", False),
    (9514, "Posters", ".", "bool", "sentence.nomarkers",
     [("", "mark what you've seen"), ("1", "stay unmarked")],
     "A small lilac tick on what you've seen and a thin line on what you've started. "
     "The captions and paragraphs always say it in words.", False),
    (9515, "Info pages", ".", "bool", "sentence.hidetrailer",
     [("", "offer the trailer"), ("1", "leave trailers out")],
     "“…watch the trailer…” appears only when a film has a trailer link. "
     "Trailers play through the YouTube add-on.", False),
    (9516, "The player sentence hides after", ".", "string", "sentence.osdhide",
     [("", "5 seconds"), ("10", "10 seconds"), ("off", "never, until Back"), ("3", "3 seconds")],
     "How long the playback sentence stays after your last button press. "
     "It always stays while paused or while a menu is open.", False),
    (9517, "Sync strips sit at the", "of the picture.", "string", "sentence.offsetbar",
     [("", "top"), ("bottom", "bottom")],
     "Where the subtitle and audio offset strip appears while you sync. Top keeps bottom subtitles in view.", False),
    (9518, "Things move", ".", "bool", "sentence.reducemotion",
     [("", "gently"), ("1", "as little as possible")],
     "Gently: text settles into place with short fades and slides. As little as possible: quick fades only.", False),
]


def cond_is(kind, key, stored, opts):
    if kind == "bool":
        return f"Skin.HasSetting({key})" if stored else f"!Skin.HasSetting({key})"
    if stored == opts[0][0]:
        others = [o for o, _ in opts[1:]]
        return " + ".join(f"!String.IsEqual(Skin.String({key}),{o})" for o in others)
    return f"String.IsEqual(Skin.String({key}),{stored})"


def set_action(kind, key, stored):
    if kind == "bool":
        return f"Skin.SetBool({key})" if stored else f"Skin.Reset({key})"
    return f"Skin.SetString({key},{stored})" if stored else f"Skin.Reset({key})"


WID = [9700]


def words(text, left=None):
    # Every grouplist child needs its own id: a grouplist chains Left/Right through its children's ids,
    # and a non-focusable child WITH an id passes focus on in the direction of travel (id 0 = dead end).
    WID[0] += 1
    lp = f"<left>{left}</left>" if left is not None else ""
    return (f'\t\t\t\t<control type="label" id="{WID[0]}">{lp}<width>auto</width><height>84</height>'
            f"<font>serif_40</font><textcolor>text</textcolor><label>{escape(text)}</label></control>")


def row(r):
    rid, before, after, kind, key, opts, _help, reload = r
    L = []
    a = L.append
    a(f'\t\t\t<control type="grouplist" id="{rid + 100}">')
    a("\t\t\t\t<width>1180</width><height>84</height>")
    a("\t\t\t\t<orientation>horizontal</orientation><usecontrolcoords>true</usecontrolcoords><itemgap>0</itemgap>")
    n = len(opts)
    for i, (stored, _lab) in enumerate(opts):
        c = cond_is(kind, key, stored, opts)
        for tag, target in (("onright", opts[(i + 1) % n][0]), ("onleft", opts[(i - 1) % n][0])):
            a(f'\t\t\t\t<{tag} condition="{c}">{set_action(kind, key, target)}</{tag}>')
            if reload:
                a(f'\t\t\t\t<{tag} condition="{c}">SetProperty(sentence.refocus,{rid},home)</{tag}>')
                a(f'\t\t\t\t<{tag} condition="{c}">ReloadSkin()</{tag}>')
    a(words(before))
    a(f'\t\t\t\t<control type="button" id="{rid}">')
    a("\t\t\t\t\t<left>-2</left><top>6</top><width>auto</width><height>72</height><font>serif_40</font>")
    a("\t\t\t\t\t<include>Sen_PhraseTextures</include>")
    a(nav(rid))
    a(f"\t\t\t\t\t<label>$VAR[SkinSet_L{rid}]</label>")
    for i, (stored, _lab) in enumerate(opts):
        c = cond_is(kind, key, stored, opts)
        a(f'\t\t\t\t\t<onclick condition="{c}">{set_action(kind, key, opts[(i + 1) % n][0])}</onclick>')
        if reload:
            a(f'\t\t\t\t\t<onclick condition="{c}">SetProperty(sentence.refocus,{rid},home)</onclick>')
            a(f'\t\t\t\t\t<onclick condition="{c}">ReloadSkin()</onclick>')
    a("\t\t\t\t</control>")
    a(words(after, -22 if after == "." else -2))
    a("\t\t\t</control>")
    return L


ORDER = [r[0] for r in ROWS] + [9530, 9531]
UP = {rid: ORDER[(i - 1) % len(ORDER)] for i, rid in enumerate(ORDER)}
DOWN = {rid: ORDER[(i + 1) % len(ORDER)] for i, rid in enumerate(ORDER)}
# the saved-sentences row (9530) only shows while some are saved: the rows around it skip it


def nav(rid):
    up = f"<onup>{UP[rid]}</onup>"
    down = f"<ondown>{DOWN[rid]}</ondown>"
    if rid == 9518:
        down = '<ondown condition="Control.IsVisible(9530)">9530</ondown><ondown condition="!Control.IsVisible(9530)">9531</ondown>'
    if rid == 9531:
        up = '<onup condition="Control.IsVisible(9530)">9530</onup><onup condition="!Control.IsVisible(9530)">9518</onup>'
    return "					" + up + down



def main():
    L = []
    a = L.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a("<!-- GENERATED by _src/make_skinsettings.py - edit the table there. Settings: docs/skin.sentence/SETTINGS.md -->")
    a("<!--")
    a("\tSentence's own settings, one sentence each. Up/Down move between them; OK or Right changes the phrase,")
    a("\tLeft steps it back. Rows that reload the skin come back through Window(Home).Property(sentence.refocus).")
    a("\tIds: phrases 9510-9518 (rows 9610-9618), 9530 forget saved sentences, 9531 reset everything (OK twice).")
    a("-->")
    a("<window>")
    a('\t<defaultcontrol always="true">9600</defaultcontrol>')
    a("\t<backgroundcolor>ground</backgroundcolor>")
    a("\t<onload>ClearProperty(sentence.resetarmed,home)</onload>")
    a('\t<onload condition="!String.IsEmpty(Window(Home).Property(sentence.refocus))">SetFocus($INFO[Window(Home).Property(sentence.refocus)])</onload>')
    a("\t<onload>ClearProperty(sentence.refocus,home)</onload>")
    a("\t<include>Anim_WindowOpenClose</include>")
    a("\t<controls>")
    a("\t\t<include>Sen_Background</include>")
    a('\t\t<include content="Sen_PageHeader"><param name="title" value="How Sentence behaves"/></include>')
    a("\t\t<include>Sen_Clock</include>")
    a('\t\t<control type="grouplist" id="9600">')
    a("\t\t\t<left>page_margin</left><top>150</top><width>1200</width><height>900</height>")
    a("\t\t\t<orientation>vertical</orientation><itemgap>0</itemgap>")
    a("\t\t\t<onup>noop</onup><ondown>noop</ondown><onleft>noop</onleft><onright>noop</onright>")
    for r in ROWS:
        L.extend(row(r))
    # saved sentences
    a('\t\t\t<control type="grouplist" id="9630">')
    a("\t\t\t\t<width>1180</width><height>84</height><orientation>horizontal</orientation><usecontrolcoords>true</usecontrolcoords>")
    a("\t\t\t\t<visible>!String.IsEmpty(Skin.String(sentence.slot1.name)) | !String.IsEmpty(Skin.String(sentence.slot2.name)) | !String.IsEmpty(Skin.String(sentence.slot3.name))</visible>")
    a(words("Your saved sentences can be"))
    a('\t\t\t\t<control type="button" id="9530">')
    a("\t\t\t\t\t<left>-2</left><top>6</top><width>auto</width><height>72</height><font>serif_40</font>")
    a("\t\t\t\t\t<include>Sen_PhraseTextures</include><label>forgotten</label>")
    a(nav(9530))
    for n in (1, 2, 3):
        for f in ("name", "kind", "len", "genre", "decade", "seen", "order"):
            a(f"\t\t\t\t\t<onclick>Skin.Reset(sentence.slot{n}.{f})</onclick>")
    a("\t\t\t\t</control>")
    a(words(".", -22))
    a("\t\t\t</control>")
    # reset
    a('\t\t\t<control type="grouplist" id="9631">')
    a("\t\t\t\t<width>1180</width><height>84</height><orientation>horizontal</orientation><usecontrolcoords>true</usecontrolcoords>")
    a(words("Or"))
    a('\t\t\t\t<control type="button" id="9531">')
    a("\t\t\t\t\t<left>-2</left><top>6</top><width>auto</width><height>72</height><font>serif_40</font>")
    a("\t\t\t\t\t<include>Sen_PhraseTextures</include><label>$VAR[SkinSet_ResetLabel]</label>")
    a(nav(9531))
    armed = "!String.IsEmpty(Window(Home).Property(sentence.resetarmed))"
    a(f'\t\t\t\t\t<onclick condition="!{armed}">SetProperty(sentence.resetarmed,1,home)</onclick>')
    a(f'\t\t\t\t\t<onclick condition="{armed}">ClearProperty(sentence.resetarmed,home)</onclick>')
    a(f'\t\t\t\t\t<onclick condition="{armed}">Skin.ResetSettings</onclick>')
    a(f'\t\t\t\t\t<onclick condition="{armed}">ReloadSkin()</onclick>')
    a("\t\t\t\t\t<onunfocus>ClearProperty(sentence.resetarmed,home)</onunfocus>")
    a("\t\t\t\t</control>")
    a(words(".", -22))
    a("\t\t\t</control>")
    a("\t\t</control>")
    a('\t\t<control type="textbox">')
    a("\t\t\t<left>1380</left><top>166</top><width>420</width><height>520</height>")
    a("\t\t\t<font>serif_28</font><textcolor>muted</textcolor><label>$VAR[SkinSet_Help]</label>")
    a("\t\t</control>")
    a('\t\t<control type="label">')
    a("\t\t\t<left>page_margin</left><top>1010</top><width>page_width</width><height>30</height>")
    a("\t\t\t<font>ui_20</font><textcolor>muted</textcolor>")
    a("\t\t\t<label>Up and down move between sentences. OK or right changes a phrase, left steps it back. Kodi's own settings are under Settings.</label>")
    a("\t\t</control>")
    a("\t</controls>")
    a("</window>")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

    V = ['<?xml version="1.0" encoding="UTF-8"?>', "<!-- GENERATED by _src/make_skinsettings.py -->", "<includes>"]
    for r in ROWS:
        rid, _b, _a, kind, key, opts, _h, _rl = r
        V.append(f'\t<variable name="SkinSet_L{rid}">')
        for stored, lab in opts:
            V.append(f'\t\t<value condition="{cond_is(kind, key, stored, opts)}">{escape(lab)}</value>')
        V.append("\t</variable>")
    V.append('\t<variable name="SkinSet_Help">')
    for r in ROWS:
        V.append(f'\t\t<value condition="Control.HasFocus({r[0]})">{escape(r[6])}</value>')
    V.append('\t\t<value condition="Control.HasFocus(9530)">Removes the sentences you kept on Home. Your current sentence stays.</value>')
    V.append('\t\t<value condition="Control.HasFocus(9531)">Puts every Sentence setting back the way it came and reloads the skin. Press OK twice.</value>')
    V.append("\t</variable>")
    V.append('\t<variable name="SkinSet_ResetLabel">')
    V.append(f'\t\t<value condition="{armed}">press OK again to reset everything</value>')
    V.append("\t\t<value>reset every setting</value>")
    V.append("\t</variable>")
    V.append("</includes>")
    (OUT.parent / "Includes_SkinSettings.xml").write_text("\n".join(V) + "\n", encoding="utf-8")
    print("wrote", OUT, "and Includes_SkinSettings.xml")


if __name__ == "__main__":
    main()
