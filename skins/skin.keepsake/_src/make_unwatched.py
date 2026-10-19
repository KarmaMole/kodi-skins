"""Generate 1080i/Custom_1160_Unwatched.xml: "the unwatched" (mockups/KeepsakeUnwatched.html).

Films you added and never played, grouped by the year you added them, oldest first:
  8100  year chips ('09 '10 ... '26): static items, one per year, each visible only when its probe list
        (8200 + year - 2000, limit 1) found a never-played film added that year
  8101  row A = the chip in focus ("waiting since 2019"): poster prints, the one in focus lifts with a note
  8102  row B = the next chip ("since 2020"), a dimmed preview (not focusable)
  8111 / 8112  the last film added in row A / B (sorted descending, limit 1) for "added feb - oct 2019"
  8120  never-played films added on the focused print's day ("seven of them arrived together")
  8199  every never-played film (the count in the label line)
Down on row A = next year, Up = previous year (row A stays where it is, the years scroll through it: Omar's
rule 3/4 - Down never has to walk a row), Up on the first year = the chips. Left/Right on the chips change year.
Back = the window you came from (Home or the diary).
Usage: python skins/skin.keepsake/_src/make_unwatched.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "1080i" / "Custom_1160_Unwatched.xml"
YEARS = range(2000, 2036)
NUMWORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def probes():
    o = []
    for y in YEARS:
        o.append(f'''		<control type="list" id="{8200 + y - 2000}">
			<left>-40</left>
			<top>-40</top>
			<width>1</width>
			<height>1</height>
			<itemlayout width="1" height="1"/>
			<focusedlayout width="1" height="1"/>
			<content target="videos" limit="5" browse="never">$VAR[KS_Path_Waiting{y}]</content>
		</control>''')
    return "\n".join(o)


def chips():
    o = []
    for y in YEARS:
        o.append(f'''					<item>
						<label>'{y % 100:02d}</label>
						<label2>since {y}</label2>
						<property name="year">y{y}</property>
						<visible>Integer.IsGreater(Container({8200 + y - 2000}).NumItems,0)</visible>
					</item>''')
    return "\n".join(o)


def count_word():
    vals = []
    for n in range(2, 13):
        vals.append(f'\t\t<value condition="Integer.IsEqual(Container(8120).NumItems,{n})">{NUMWORDS[n]} of them arrived together,[CR]on $VAR[KS_UF_DM] $VAR[KS_UF_Year]</value>')
    vals.append('\t\t<value condition="Integer.IsGreater(Container(8120).NumItems,12)">$INFO[Container(8120).NumItems] of them arrived together,[CR]on $VAR[KS_UF_DM] $VAR[KS_UF_Year]</value>')
    vals.append('\t\t<value condition="Integer.IsEqual(Container(8120).NumItems,1)">it arrived on its own,[CR]on $VAR[KS_UF_DM] $VAR[KS_UF_Year]</value>')
    return "\n".join(vals)


def row(list_id, probe_id, slot, top, focusable):
    """A row: heading + label + poster list. top = poster top (mockup 300 / 750)."""
    heading_top = top - 93   # mockup heading top 214 / 672 (font 58, lh 1.02 -> Kodi top - 7)
    label_top = top - 59
    head_color = "ink" if focusable else "ink2"
    nav = ""
    if focusable:
        nav = f'''
			<onup condition="Integer.IsGreater(Container(8100).CurrentItem,1)">Control.Move(8100,-1)</onup>
			<onup condition="!Integer.IsGreater(Container(8100).CurrentItem,1)">8100</onup>
			<ondown condition="!String.IsEmpty(Container(8100).ListItemNoWrap(1).Label)">Control.Move(8100,1)</ondown>
			<onleft>noop</onleft>
			<onright>noop</onright>'''
    items = f'''
			<itemlayout width="302" height="440">
				<include content="Unw_Print">
					<param name="dim" value="{'$VAR[Unw_RowADim]' if focusable else 'dim_print_more'}"/>
					<param name="lift" value="false"/>
					<param name="focused" value="false"/>
				</include>
			</itemlayout>
			<focusedlayout width="302" height="440">
				<include content="Unw_Print">
					<param name="dim" value="{'white' if focusable else 'dim_print_more'}"/>
					<param name="lift" value="{'Control.HasFocus(8101)' if focusable else 'false'}"/>
					<param name="focused" value="{'true' if focusable else 'false'}"/>
				</include>{'''
				<include>Unw_FocusNote</include>''' if focusable else ''}
			</focusedlayout>'''
    a = "A" if slot == 0 else "B"
    return f'''		<!-- row {a}: {'the year in focus' if focusable else 'the next year (preview)'} -->
		<control type="grouplist">
			<left>112</left>
			<top>{heading_top}</top>
			<width>1700</width>
			<height>90</height>
			<orientation>horizontal</orientation>
			<itemgap>66</itemgap>
			<usecontrolcoords>true</usecontrolcoords>
			<visible>Integer.IsGreater(Container({list_id}).NumItems,0)</visible>
			<control type="label">
				<width>auto</width>
				<height>80</height>
				<font>hand_58</font>
				<textcolor>{head_color}</textcolor>
				<label>{'waiting ' if focusable else ''}$INFO[Container(8100).ListItem({slot}).Label2]</label>
			</control>
			<control type="label">
				<top>34</top>
				<width>auto</width>
				<height>27</height>
				<font>lbl_20</font>
				<textcolor>label</textcolor>
				<label>$VAR[Unw_Films{a}]  ·  [COLOR label_hi]$VAR[Unw_Added{a}][/COLOR]</label>
			</control>
		</control>
		<control type="{'list' if focusable else 'list'}" id="{list_id}">
			<left>52</left>
			<top>{top - 60}</top>
			<width>1812</width>
			<height>440</height>
			<orientation>horizontal</orientation>
			<scrolltime tween="cubic" easing="out">240</scrolltime>
			<preloaditems>1</preloaditems>{nav}
{items}
			<content target="videos" sortby="dateadded" sortorder="ascending" browse="never">$VAR[KS_Path_UnwRow{slot}]</content>
		</control>
		<control type="list" id="{probe_id}">
			<left>-40</left>
			<top>-40</top>
			<width>1</width>
			<height>1</height>
			<itemlayout width="1" height="1"/>
			<focusedlayout width="1" height="1"/>
			<content target="videos" limit="1" sortby="dateadded" sortorder="descending" browse="never">$VAR[KS_Path_UnwRow{slot}]</content>
		</control>'''


def write_timers():
    """Timers.xml: focus catchers + the unwatched page's opening year (the oldest year with at least 5 films; the
    probes are limit 5). While the year on chip 0 has fewer than 5 and some year has 5, step the chips one to the
    right every frame (stop = true restarts the timer next frame); then mark it done for this visit.
    Timers don't expand $EXP (LESSONS round 4), so the conditions are written out here."""
    probe = lambda y: f"Container({8200 + y - 2000}).NumItems"
    loaded = " + ".join(f"!Container({8200 + y - 2000}).IsUpdating" for y in YEARS)
    any_big = " | ".join(f"Integer.IsGreaterOrEqual({probe(y)},5)" for y in YEARS)
    chip0_small = " | ".join(f"[String.IsEqual(Container(8100).ListItem(0).Property(year),y{y}) + Integer.IsLess({probe(y)},5)]" for y in YEARS)
    base = "Window.IsActive(1160) + String.IsEmpty(Window(Home).Property(keepsake.unwstart)) + Integer.IsGreater(Container(8100).NumItems,0)"
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_unwatched.py.
	Focus catchers: the diary (1161) and the unwatched (1160) load their lists after the window opens, so their
	default control can't take focus at onload; once the list has items and nothing else holds focus, hand it over.
	The unwatched opens on the oldest year with at least five films (keepsake.unwstart marks the visit done). -->
<timers>
	<timer>
		<name>keepsake_diary_focus</name>
		<start reset="true">Window.IsActive(1161) + Integer.IsGreater(Container(520).NumItems,0) + !Control.HasFocus(520) + !ControlGroup(9300).HasFocus()</start>
		<stop>Control.HasFocus(520) | !Window.IsActive(1161)</stop>
		<onstart>SetFocus(520)</onstart>
	</timer>
	<timer>
		<name>keepsake_unwatched_focus</name>
		<start reset="true">Window.IsActive(1160) + Integer.IsGreater(Container(8101).NumItems,0) + !Control.HasFocus(8101) + !Control.HasFocus(8100) + !Control.HasFocus(9301)</start>
		<stop>Control.HasFocus(8101) | !Window.IsActive(1160)</stop>
		<onstart>SetFocus(8101)</onstart>
	</timer>
	<timer>
		<name>keepsake_unwatched_step</name>
		<start>{base} + {loaded} + [{any_big}] + [{chip0_small}]</start>
		<stop>true</stop>
		<onstart>Control.Move(8100,1)</onstart>
	</timer>
	<timer>
		<name>keepsake_unwatched_settled</name>
		<start>{base} + {loaded} + [![{chip0_small}] | ![{any_big}]]</start>
		<stop>true</stop>
		<onstart>SetProperty(keepsake.unwstart,1,home)</onstart>
	</timer>
</timers>
'''
    (OUT.parent / "Timers.xml").write_text(xml, encoding="utf-8", newline="\n")


def main():
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_unwatched.py - edit the generator. -->
<!--
	The unwatched (custom window 1160): films you added and never played, by the year you added them.
	Opened from Home ("waiting since") and from the diary's header word. See the generator for the ids.
-->
<window type="window" id="1160">
	<defaultcontrol always="true">8101</defaultcontrol>
	<backgroundcolor>paper</backgroundcolor>
	<onload>ClearProperty(keepsake.unwstart,home)</onload>
	<include>Anim_WindowOpenClose</include>
	<controls>
		<include>KS_Page</include>
		<!-- the probes: is there a never-played film added in this year? -->
{probes()}
		<control type="list" id="8199">
			<left>-40</left>
			<top>-40</top>
			<width>1</width>
			<height>1</height>
			<itemlayout width="1" height="1"/>
			<focusedlayout width="1" height="1"/>
			<content target="videos" browse="never">$VAR[KS_Path_Waiting]</content>
		</control>
		<control type="list" id="8120">
			<left>-40</left>
			<top>-40</top>
			<width>1</width>
			<height>1</height>
			<itemlayout width="1" height="1"/>
			<focusedlayout width="1" height="1"/>
			<content target="videos" browse="never">$VAR[KS_Path_SameDay]</content>
		</control>

		<!-- header -->
		<control type="label">
			<left>112</left>
			<top>33</top>
			<width>560</width>
			<height>118</height>
			<font>hand_92</font>
			<textcolor>ink</textcolor>
			<label>the unwatched</label>
		</control>
		<control type="button" id="9301">
			<left>668</left>
			<top>72</top>
			<width>auto</width>
			<height>74</height>
			<textoffsetx>4</textoffsetx>
			<font>hand_52</font>
			<textcolor>ink_ghost</textcolor>
			<include>KS_PenWordLook</include>
			<label>the diary</label>
			<onclick>ReplaceWindow(1161)</onclick>
			<onup>noop</onup>
			<onleft>noop</onleft>
			<onright>8100</onright>
			<ondown>8100</ondown>
		</control>
		<control type="label">
			<left>118</left>
			<top>161</top>
			<width>900</width>
			<height>27</height>
			<font>lbl_20</font>
			<textcolor>label</textcolor>
			<label>films  ·  $INFO[Container(8199).NumItems] never played  ·  [COLOR label_hi]oldest first[/COLOR]</label>
		</control>
		<include>KS_Clock</include>

		<!-- year chips -->
		<control type="list" id="8100">
			<left>986</left>
			<top>166</top>
			<width>832</width>
			<height>48</height>
			<orientation>horizontal</orientation>
			<scrolltime tween="cubic" easing="out">200</scrolltime>
			<onup>9301</onup>
			<ondown>8101</ondown>
			<onleft>noop</onleft>
			<onright>noop</onright>
			<itemlayout width="52" height="48">
				<control type="label">
					<left>0</left>
					<top>10</top>
					<width>52</width>
					<height>27</height>
					<align>center</align>
					<font>mono_20</font>
					<textcolor>label</textcolor>
					<label>$INFO[ListItem.Label]</label>
				</control>
			</itemlayout>
			<focusedlayout width="52" height="48">
				<control type="image">
					<left>2</left>
					<top>4</top>
					<width>48</width>
					<height>40</height>
					<texture border="24,0,24,0" colordiffuse="tape">ks/tape_row.png</texture>
					<visible>Control.HasFocus(8100)</visible>
				</control>
				<control type="label">
					<left>0</left>
					<top>10</top>
					<width>52</width>
					<height>27</height>
					<align>center</align>
					<font>mono_20</font>
					<textcolor>$VAR[Unw_ChipColor]</textcolor>
					<label>$INFO[ListItem.Label]</label>
				</control>
				<control type="image">
					<left>9</left>
					<top>38</top>
					<width>34</width>
					<height>2</height>
					<texture colordiffuse="ink">common/white.png</texture>
					<visible>!Control.HasFocus(8100)</visible>
				</control>
			</focusedlayout>
			<content>
{chips()}
			</content>
		</control>

{row(8101, 8111, 0, 300, True)}
{row(8102, 8112, 1, 750, False)}

		<!-- "seven of them arrived together, on 4 February 2019" (the other page from the focused print) -->
		<control type="textbox">
			<left>1080</left>
			<top>581</top>
			<width>720</width>
			<height>100</height>
			<font>hand_40</font>
			<textcolor>ink_soft</textcolor>
			<label>$VAR[Unw_Together]</label>
			<visible>Control.HasFocus(8101) + Integer.IsLess(Container(8101).Position,3)</visible>
		</control>
		<control type="textbox">
			<left>112</left>
			<top>581</top>
			<width>720</width>
			<height>100</height>
			<font>hand_40</font>
			<textcolor>ink_soft</textcolor>
			<label>$VAR[Unw_Together]</label>
			<visible>Control.HasFocus(8101) + !Integer.IsLess(Container(8101).Position,3)</visible>
		</control>
		<!-- nothing waiting -->
		<control type="textbox">
			<left>112</left>
			<top>262</top>
			<width>1200</width>
			<height>110</height>
			<font>hand_46</font>
			<textcolor>ink_faint</textcolor>
			<label>Nothing is waiting: you have played every film you added.</label>
			<visible>!Integer.IsGreater(Container(8199).NumItems,0) + !Container(8199).IsUpdating</visible>
		</control>
	</controls>
</window>
'''
    OUT.write_text(xml, encoding="utf-8", newline="\n")
    write_timers()
    inc = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_unwatched.py - pieces of the unwatched page (Custom_1160_Unwatched.xml). -->
<includes>
	<variable name="Unw_Together">
{count_word()}
	</variable>
	<variable name="Unw_FilmsA">
		<value condition="Integer.IsEqual(Container(8101).NumItems,1)">1 film</value>
		<value>$INFO[Container(8101).NumItems] films</value>
	</variable>
	<variable name="Unw_FilmsB">
		<value condition="Integer.IsEqual(Container(8102).NumItems,1)">1 film</value>
		<value>$INFO[Container(8102).NumItems] films</value>
	</variable>
	<variable name="Unw_AddedA">
		<value condition="String.IsEqual(Container(8101).ListItemAbsolute(0).DateAdded,Container(8111).ListItem.DateAdded)">added $VAR[KS_UA0_DM] $VAR[KS_UA0_Year]</value>
		<value condition="String.IsEqual(Container(8101).NumItems,1)">added $VAR[KS_UA0_MonS] $VAR[KS_UA0_Year]</value>
		<value>added $VAR[KS_UA0_MonS] – $VAR[KS_UZ0_MonS] $VAR[KS_UZ0_Year]</value>
	</variable>
	<variable name="Unw_AddedB">
		<value condition="String.IsEqual(Container(8102).ListItemAbsolute(0).DateAdded,Container(8112).ListItem.DateAdded)">added $VAR[KS_UA1_DM] $VAR[KS_UA1_Year]</value>
		<value condition="String.IsEqual(Container(8102).NumItems,1)">added $VAR[KS_UA1_MonS] $VAR[KS_UA1_Year]</value>
		<value>added $VAR[KS_UA1_MonS] – $VAR[KS_UZ1_MonS] $VAR[KS_UZ1_Year]</value>
	</variable>
	<variable name="Unw_RowADim">
		<value condition="Control.HasFocus(8101)">dim_print</value>
		<value>white</value>
	</variable>
	<variable name="Unw_ChipColor">
		<value condition="Control.HasFocus(8100)">on_tape</value>
		<value>ink_bold</value>
	</variable>
	<include name="Unw_Print">
		<definition>
			<control type="group">
				<left>60</left>
				<top>60</top>
				<width>184</width>
				<height>252</height>
				<include>KS_TiltItem</include>
				<control type="group">
					<width>184</width>
					<height>252</height>
					<include condition="$PARAM[focused]">KS_TiltFocus</include>
					<include content="KS_Print_Poster">
						<param name="art" value="$VAR[KS_PosterArt]"/>
						<param name="dim" value="$PARAM[dim]"/>
						<param name="lift" value="$PARAM[lift]"/>
						<param name="title" value="$INFO[ListItem.Label]"/>
					</include>
				</control>
			</control>
		</definition>
	</include>
	<!-- the focused print's note: arrow + "added 7 years ago, never played" + TITLE · YEAR, to the right of the
	     print on the left page, to its left on the right page (Container.Position 0-5) -->
	<include name="Unw_FocusNote">
		<control type="group">
			<visible>Control.HasFocus(8101) + Integer.IsLess(Container(8101).Position,3)</visible>
			<control type="image">
				<left>144</left>
				<top>316</top>
				<width>90</width>
				<height>70</height>
				<texture colordiffuse="ink">ks/pen_arrow.png</texture>
			</control>
			<control type="textbox">
				<left>244</left>
				<top>317</top>
				<width>520</width>
				<height>100</height>
				<font>hand_44</font>
				<textcolor>ink_bold</textcolor>
				<label>added $VAR[KS_DA_YearsAgo],[CR]never played</label>
			</control>
			<control type="label">
				<left>247</left>
				<top>413</top>
				<width>560</width>
				<height>27</height>
				<font>lbl_20</font>
				<textcolor>label_hi</textcolor>
				<label>$INFO[ListItem.Title]$INFO[ListItem.Year,  ·  ,]</label>
			</control>
		</control>
		<control type="group">
			<visible>Control.HasFocus(8101) + !Integer.IsLess(Container(8101).Position,3)</visible>
			<control type="image">
				<left>-36</left>
				<top>316</top>
				<width>90</width>
				<height>70</height>
				<texture flipx="true" colordiffuse="ink">ks/pen_arrow.png</texture>
			</control>
			<control type="textbox">
				<left>-566</left>
				<top>317</top>
				<width>520</width>
				<height>100</height>
				<align>right</align>
				<font>hand_44</font>
				<textcolor>ink_bold</textcolor>
				<label>added $VAR[KS_DA_YearsAgo],[CR]never played</label>
			</control>
			<control type="label">
				<left>-606</left>
				<top>413</top>
				<width>560</width>
				<height>27</height>
				<align>right</align>
				<font>lbl_20</font>
				<textcolor>label_hi</textcolor>
				<label>$INFO[ListItem.Title]$INFO[ListItem.Year,  ·  ,]</label>
			</control>
		</control>
	</include>
</includes>
'''
    (OUT.parent / "Includes_Unwatched.xml").write_text(inc, encoding="utf-8", newline="\n")
    print("wrote", OUT.name, "and Includes_Unwatched.xml")


if __name__ == "__main__":
    main()
