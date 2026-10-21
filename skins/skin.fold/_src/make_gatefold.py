"""Generate skins/skin.fold/1080i/DialogMusicInfo.xml: the album as a gatefold sleeve.
    python skins/skin.fold/_src/make_gatefold.py

The closed sleeve (marigold stock, the cover as a tipped-in plate) travels from the card it stood as on Home to
the centre; its front swings open on the gutter (x 960) in two phases (front 0 -> +90 and hide, inside face
-90 -> 0: no back-face culling in Kodi); the inside left shows the cover printed large, the inside right carries
the tracklist; the record slides half out of the right-hand pocket. <= 450 ms; reduce motion = a fade.

Kodi ids (Estuary Omega DialogMusicInfo.xml, GUIDialogMusicInfo.cpp / GUIDialogSongInfo.cpp): 50 the list Kodi
fills (album -> songs, artist -> discography), 6 refresh, 8 play (hidden by Kodi for artists), 12 artist / album
info (Kodi writes its own label into it: it stays offscreen and our word sends a click, LESSONS Duotone 0.9.2).
Fold ids: 9000 words, 9011 shuffle, 9012 play all (artist), 9013 artist/album word (SendClick(12)), 9014 refresh.
"""
from pathlib import Path
from default_repeats import strip as strip_defaults  # kodi-review xml.redundant: drop tags that repeat Defaults.xml
from xmlfinish import finish_xml  # kodi-review labels.not-translated: label text goes to strings.po

OUT = Path(__file__).resolve().parents[1] / "1080i" / "DialogMusicInfo.xml"
RM = "Skin.HasSetting(fold.reducemotion)"
S = 640                      # panel side
TOP = 186
LX, RX = 320, 960           # inside left, inside right (= front cover's resting place)
HINGE = 960
CX, CY = RX + S // 2, TOP + S // 2
T_MOVE, C_DELAY, C_TIME = 190, 110, 170
I_DELAY, I_TIME = C_DELAY + C_TIME, 160
D_DELAY, D_TIME = 230, 210        # disc slides out of the pocket
X_INS, X_COVER_D, X_COVER_T, X_BACK_D, X_BACK_T = 150, 150, 150, 290, 150


def slots():
    out = []
    # Home music row A: lifted sleeve card 312 x 382, left 96 + 304 s, top 160
    for s in range(6):
        cx, cy = 96 + 304 * s + 156, 160 + 191
        out.append((f"String.IsEqual(Window(Home).Property(fold.from),m{s})", cx - CX, cy - CY, 312 / S * 100, 382 / S * 100))
    # Home music row B: cream card 270 x 220 at 96 + 294 s, top 572 (page slid 330)
    for s in range(6):
        cx, cy = 96 + 294 * s + 135, 572 + 110
        out.append((f"String.IsEqual(Window(Home).Property(fold.from),c{s})", cx - CX, cy - CY, 270 / S * 100, 220 / S * 100))
    return out


def anims():
    a = []
    for cond, dx, dy, zx, zy in slots():
        a.append(f"""			<animation type="WindowOpen" condition="{cond} + !{RM}">
				<effect type="slide" start="{dx:.0f},{dy:.0f}" end="0,0" time="{T_MOVE}" tween="cubic" easing="out"/>
				<effect type="zoom" start="{zx:.1f},{zy:.1f}" end="100,100" center="{CX},{CY}" time="{T_MOVE}" tween="cubic" easing="out"/>
			</animation>
			<animation type="WindowClose" condition="{cond} + !{RM}">
				<effect type="slide" start="0,0" end="{dx:.0f},{dy:.0f}" delay="{X_BACK_D}" time="{X_BACK_T}" tween="cubic" easing="in"/>
				<effect type="zoom" start="100,100" end="{zx:.1f},{zy:.1f}" center="{CX},{CY}" delay="{X_BACK_D}" time="{X_BACK_T}" tween="cubic" easing="in"/>
			</animation>""")
    any_slot = " | ".join(f"[{c}]" for c, *_ in slots())
    a.append(f"""			<animation type="WindowOpen" condition="![{any_slot}] + !{RM}">
				<effect type="zoom" start="82" end="100" center="{CX},{CY}" time="{T_MOVE}" tween="cubic" easing="out"/>
				<effect type="fade" start="0" end="100" time="120"/>
			</animation>
			<animation type="WindowClose" condition="![{any_slot}] + !{RM}">
				<effect type="zoom" start="100" end="86" center="{CX},{CY}" delay="{X_BACK_D}" time="{X_BACK_T}" tween="cubic" easing="in"/>
				<effect type="fade" start="100" end="0" delay="{X_BACK_D}" time="{X_BACK_T}"/>
			</animation>
			<animation type="WindowOpen" condition="{RM}"><effect type="fade" start="0" end="100" time="150"/></animation>
			<animation type="WindowClose" condition="{RM}"><effect type="fade" start="100" end="0" time="150"/></animation>""")
    return "\n".join(a)


def paper(x, shape):
    return f"""
				<control type="image">
					<left>{x}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture border="8" colordiffuse="cream">fold/{shape}</texture>
				</control>
				<control type="image">
					<left>{x}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture diffuse="fold/{shape}">fold/tooth_cream.png</texture>
				</control>"""


def word(bid, label, width, visible, onclick=None, right=None, left=None):
    oc = f"\n\t\t\t\t\t\t<onclick>{onclick}</onclick>" if onclick else ""
    return f"""
					<control type="button" id="{bid}">
						<width>{width}</width>
						<height>52</height>
						<label>{label}</label>
						<font>word_26</font>
						<textcolor>ink</textcolor>
						<focusedcolor>$VAR[FoldOnAccent]</focusedcolor>
						<align>center</align>
						<textoffsetx>0</textoffsetx>
						<texturefocus border="6" colordiffuse="mari">fold/chip.png</texturefocus>
						<texturenofocus />
						<visible>{visible}</visible>{oc}
					</control>"""


def build():
    from PIL import ImageFont
    f = ImageFont.truetype(str(Path(__file__).resolve().parents[1] / "fonts" / "FoldWord-ExtraBold.ttf"), 26)
    ww = {w: round(f.getlength(w.upper())) + 24 + len(w) + 4 for w in ("Play", "Play all", "Shuffle", "Artist", "Album", "Refresh")}
    x = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by _src/make_gatefold.py - edit the generator, not this file. -->
<!--{__doc__}-->
<window>
	<defaultcontrol always="true">9000</defaultcontrol>
	<onunload>ClearProperty(fold.from,home)</onunload>
	<controls>
		<control type="group">
			<animation type="WindowOpen"><effect type="fade" start="0" end="100" time="150"/></animation>
			<animation type="WindowClose"><effect type="fade" start="100" end="0" delay="{X_BACK_D}" time="{X_BACK_T}"/></animation>
			<include>Fold_Background</include>
			<include content="Fold_Tabs"><param name="dim" value="true"/></include>
			<include>Fold_Clock</include>
		</control>
		<control type="group">
			<camera x="960" y="540"/>
{anims()}
			<!-- shadow of the open sleeve -->
			<control type="image">
				<left>{LX - 96}</left>
				<top>{TOP - 96}</top>
				<width>{2 * S + 192}</width>
				<height>{S + 192}</height>
				<texture border="104">fold/shadow_spread.png</texture>
				<animation type="WindowOpen" condition="!{RM}"><effect type="fade" start="0" end="100" delay="{I_DELAY}" time="160"/></animation>
				<animation type="WindowClose" condition="!{RM}"><effect type="fade" start="100" end="0" time="120"/></animation>
			</control>
			<!-- the record, in the right-hand pocket: slides half out -->
			<control type="group">
				<animation type="WindowOpen" condition="!{RM}">
					<effect type="slide" start="-300,0" end="0,0" delay="{D_DELAY}" time="{D_TIME}" tween="cubic" easing="out"/>
					<effect type="rotate" start="40" end="0" center="{RX + S},{CY}" delay="{D_DELAY}" time="{D_TIME}" tween="cubic" easing="out"/>
				</animation>
				<animation type="WindowClose" condition="!{RM}">
					<effect type="slide" start="0,0" end="-300,0" time="160" tween="cubic" easing="in"/>
				</animation>
				<visible>$EXP[Music_InfoIsAlbum]</visible>
				<control type="image">
					<left>{RX + S - 300}</left>
					<top>{CY - 300}</top>
					<width>600</width>
					<height>600</height>
					<texture>fold/disc.png</texture>
				</control>
				<control type="image">
					<left>{RX + S - 105}</left>
					<top>{CY - 105}</top>
					<width>210</width>
					<height>210</height>
					<texture colordiffuse="mari">fold/disc_label.png</texture>
				</control>
				<control type="image">
					<left>{RX + S - 105}</left>
					<top>{CY - 105}</top>
					<width>210</width>
					<height>210</height>
					<aspectratio>scale</aspectratio>
					<texture background="true" diffuse="fold/disc_label.png">$INFO[ListItem.Art(thumb)]</texture>
				</control>
			</control>

			<!-- ===== inside right: the tracklist (rests flat under the closed front) -->
			<control type="group">{paper(RX, 'rr5_r.png')}
				<control type="label">
					<left>{RX + 48}</left>
					<top>{TOP + 30}</top>
					<width>{S - 96}</width>
					<height>32</height>
					<font>caps_20_b</font>
					<textcolor>mari_ink</textcolor>
					<label>$VAR[Gate_Kicker]</label>
				</control>
				<control type="textbox" id="9320">
					<left>-3000</left>
					<top>0</top>
					<width>{S - 96}</width>
					<height>80</height>
					<font>head_50</font>
					<textcolor>clear</textcolor>
					<label>$VAR[Music_InfoTitle]</label>
				</control>
				<control type="label">
					<left>{RX + 48}</left>
					<top>{TOP + 60}</top>
					<width>{S - 96}</width>
					<height>64</height>
					<font>head_50</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Music_InfoTitle]</label>
					<visible>!Integer.IsGreater(Container(9320).NumPages,1)</visible>
				</control>
				<control type="label">
					<left>{RX + 48}</left>
					<top>{TOP + 64}</top>
					<width>{S - 96}</width>
					<height>56</height>
					<font>head_34</font>
					<textcolor>ink</textcolor>
					<label>$VAR[Music_InfoTitle]</label>
					<visible>Integer.IsGreater(Container(9320).NumPages,1)</visible>
				</control>
				<control type="label">
					<left>{RX + 48}</left>
					<top>{TOP + 122}</top>
					<width>{S - 96}</width>
					<height>42</height>
					<font>light_32</font>
					<textcolor>ink2</textcolor>
					<label>$VAR[Gate_Sub]</label>
				</control>
				<control type="image">
					<left>{RX + 48}</left>
					<top>{TOP + 178}</top>
					<width>{S - 96}</width>
					<height>2</height>
					<aspectratio align="left">center</aspectratio>
					<texture colordiffuse="rule">fold/dots.png</texture>
				</control>
				<control type="list" id="50">
					<left>{RX + 36}</left>
					<top>{TOP + 190}</top>
					<width>{S - 72}</width>
					<height>{44 * 8}</height>
					<orientation>vertical</orientation>
					<scrolltime tween="cubic" easing="out">160</scrolltime>
					<onup>9000</onup>
					<ondown>9000</ondown>
					<onleft>noop</onleft>
					<onright>noop</onright>
					<itemlayout width="{S - 72}" height="44">
						<include content="Gate_Row"><param name="focused" value="false"/></include>
					</itemlayout>
					<focusedlayout width="{S - 72}" height="44">
						<control type="image">
							<left>0</left>
							<top>2</top>
							<width>{S - 72}</width>
							<height>40</height>
							<texture border="6" colordiffuse="mari">fold/chip.png</texture>
							<visible>Control.HasFocus(50)</visible>
						</control>
						<include content="Gate_Row"><param name="focused" value="Control.HasFocus(50)"/></include>
					</focusedlayout>
				</control>
				<!-- song info: no list, the facts instead -->
				<control type="textbox">
					<left>{RX + 48}</left>
					<top>{TOP + 200}</top>
					<width>{S - 96}</width>
					<height>{34 * 9}</height>
					<font>body_24</font>
					<textcolor>body</textcolor>
					<label>$VAR[Music_InfoDescription]</label>
					<visible>!Integer.IsGreater(Container(50).NumItems,0)</visible>
				</control>
				<control type="grouplist" id="9000">
					<left>{RX + 36}</left>
					<top>{TOP + S - 40 - 52}</top>
					<width>{S - 72}</width>
					<height>52</height>
					<orientation>horizontal</orientation>
					<itemgap>8</itemgap>
					<onup condition="Integer.IsGreater(Container(50).NumItems,0)">50</onup>
					<ondown condition="Integer.IsGreater(Container(50).NumItems,0)">50</ondown>
					<onleft>noop</onleft>
					<onright>noop</onright>{word(8, 'Play', ww['Play'], '!$EXP[Music_InfoIsArtist]')}{word(9012, 'Play all', ww['Play all'], '$EXP[Music_InfoIsArtist] + Integer.IsGreater(ListItem.DBID,0)', 'PlayMedia(musicdb://artists/$INFO[ListItem.DBID]/,isdir)')}{word(9011, 'Shuffle', ww['Shuffle'], '[$EXP[Music_InfoIsAlbum] | $EXP[Music_InfoIsArtist]] + Integer.IsGreater(ListItem.DBID,0)', '$VAR[Music_InfoShuffleAction]')}{word(9013, '$VAR[Gate_InfoWord]', ww['Artist'], '!$EXP[Music_InfoIsArtist]', 'SendClick(12)')}{word(9014, 'Refresh', ww['Refresh'], '!$EXP[Music_InfoIsSong]', 'SendClick(6)')}
				</control>
				<control type="button" id="12">
					<include>Fold_Hidden</include>
				</control>
				<control type="button" id="6">
					<include>Fold_Hidden</include>
				</control>
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture>fold/gate_r.png</texture>
				</control>
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture border="4" colordiffuse="ffc98a17">fold/edge_r.png</texture>
				</control>
				<!-- the lifted front's shadow on the right panel -->
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture>fold/cast_shadow.png</texture>
					<visible>!{RM}</visible>
					<animation type="WindowOpen" condition="!{RM}">
						<effect type="fade" start="100" end="0" delay="{C_DELAY}" time="{C_TIME + 120}" tween="sine" easing="in"/>
					</animation>
					<animation type="WindowClose" condition="!{RM}">
						<effect type="fade" start="0" end="100" delay="{X_COVER_D}" time="{X_COVER_T}"/>
					</animation>
				</control>
			</control>

			<!-- ===== inside left: the cover printed large (lands in phase 2) -->
			<control type="group">
				<animation effect="rotatey" start="-4" end="-4" center="{HINGE}" time="0" condition="true">Conditional</animation>
				<control type="group">
					<animation type="WindowOpen" condition="!{RM}">
						<effect type="rotatey" start="-90" end="0" center="{HINGE}" delay="{I_DELAY}" time="{I_TIME}" tween="cubic" easing="out"/>
						<effect type="fade" start="0" end="100" delay="{I_DELAY}" time="1"/>
					</animation>
					<animation type="WindowClose" condition="!{RM}">
						<effect type="rotatey" start="0" end="-90" center="{HINGE}" time="{X_INS}" tween="cubic" easing="in"/>
						<effect type="fade" start="100" end="0" delay="{X_INS}" time="1"/>
					</animation>{paper(LX, 'rr5_l.png')}
					<control type="group">
						<left>{LX + 48}</left>
						<top>{TOP + 40}</top>
						<width>{S - 96}</width>
						<height>{S - 96}</height>
						<control type="image">
							<left>-12</left>
							<top>-12</top>
							<right>-12</right>
							<bottom>-12</bottom>
							<texture border="14">fold/plate_frame.png</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{S - 96}</width>
							<height>{S - 96}</height>
							<texture colordiffuse="cream_deep">common/white.png</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{S - 96}</width>
							<height>{S - 96}</height>
							<aspectratio>scale</aspectratio>
							<texture background="true">$VAR[Gate_Cover]</texture>
						</control>
						<control type="image">
							<left>0</left>
							<top>0</top>
							<width>{S - 96}</width>
							<height>{S - 96}</height>
							<texture>fold/plate_sheen.png</texture>
						</control>
					</control>
					<control type="label">
						<left>{LX + 48}</left>
						<top>{TOP + S - 46}</top>
						<width>{S - 96}</width>
						<height>32</height>
						<font>caps_20</font>
						<textcolor>cap2</textcolor>
						<label>$INFO[ListItem.Property(Album_Label)]$INFO[ListItem.Label2]</label>
					</control>
					<control type="label">
						<left>{LX + 48}</left>
						<top>{TOP + S - 46}</top>
						<width>{S - 96}</width>
						<height>32</height>
						<align>right</align>
						<font>caps_20</font>
						<textcolor>cap2</textcolor>
						<label>$INFO[ListItem.Year]</label>
					</control>
					<control type="image">
						<left>{LX}</left>
						<top>{TOP}</top>
						<width>{S}</width>
						<height>{S}</height>
						<texture>fold/gate_l.png</texture>
					</control>
					<control type="image">
						<left>{LX}</left>
						<top>{TOP}</top>
						<width>{S}</width>
						<height>{S}</height>
						<texture border="4" colordiffuse="ffc98a17">fold/edge_l.png</texture>
					</control>
					<control type="image">
						<left>{LX}</left>
						<top>{TOP}</top>
						<width>{S}</width>
						<height>{S}</height>
						<texture>fold/inside_shade.png</texture>
						<visible>!{RM}</visible>
						<animation type="WindowOpen" condition="!{RM}">
							<effect type="fade" start="100" end="0" delay="{I_DELAY}" time="{I_TIME}"/>
						</animation>
						<animation type="WindowClose" condition="!{RM}">
							<effect type="fade" start="0" end="100" time="{X_INS}"/>
						</animation>
					</control>
				</control>
			</control>

			<!-- ===== the front of the sleeve: turns 0 -> +90 on the gutter, then hides -->
			<control type="group">
				<visible>!{RM}</visible>
				<animation type="WindowOpen" condition="!{RM}">
					<effect type="fade" start="100" end="100" time="{C_DELAY}"/>
					<effect type="rotatey" start="0" end="90" center="{HINGE}" delay="{C_DELAY}" time="{C_TIME}" tween="cubic" easing="in"/>
					<effect type="fade" start="100" end="0" delay="{C_DELAY + C_TIME}" time="1"/>
				</animation>
				<animation type="WindowClose" condition="!{RM}">
					<effect type="fade" start="0" end="100" delay="{X_COVER_D}" time="1"/>
					<effect type="rotatey" start="90" end="0" center="{HINGE}" delay="{X_COVER_D}" time="{X_COVER_T}" tween="cubic" easing="out"/>
				</animation>
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture border="8" colordiffuse="mari">fold/rr6_r.png</texture>
				</control>
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture diffuse="fold/rr6_r.png">fold/tooth_card.png</texture>
				</control>
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture>fold/card_sheen.png</texture>
				</control>
				<control type="image">
					<left>{RX + 14}</left>
					<top>{TOP}</top>
					<width>3</width>
					<height>{S}</height>
					<texture>fold/score3.png</texture>
				</control>
				<control type="group">
					<left>{RX + 36}</left>
					<top>{TOP + 30}</top>
					<width>{S - 66}</width>
					<height>{S - 66}</height>
					<control type="image">
						<left>-12</left>
						<top>-12</top>
						<right>-12</right>
						<bottom>-12</bottom>
						<texture border="14">fold/plate_frame.png</texture>
					</control>
					<control type="image">
						<left>0</left>
						<top>0</top>
						<width>{S - 66}</width>
						<height>{S - 66}</height>
						<aspectratio>scale</aspectratio>
						<texture background="true">$VAR[Gate_Cover]</texture>
					</control>
				</control>
				<control type="image">
					<left>{RX}</left>
					<top>{TOP}</top>
					<width>{S}</width>
					<height>{S}</height>
					<texture>fold/cover_shade.png</texture>
					<animation type="WindowOpen" condition="!{RM}">
						<effect type="fade" start="0" end="100" delay="{C_DELAY}" time="{C_TIME}" tween="sine" easing="in"/>
					</animation>
					<animation type="WindowClose" condition="!{RM}">
						<effect type="fade" start="100" end="0" delay="{X_COVER_D}" time="{X_COVER_T}"/>
					</animation>
				</control>
			</control>

			<control type="grouplist">
				<left>{LX}</left>
				<top>{TOP + S + 44}</top>
				<width>1280</width>
				<height>32</height>
				<orientation>horizontal</orientation>
				<itemgap>0</itemgap>
				<animation type="WindowOpen"><effect type="fade" start="0" end="100" delay="{I_DELAY}" time="120"/></animation>
				<include content="Fold_KeyHint"><param name="key" value="OK"/><param name="label" value="$VAR[Gate_Hint]"/></include>
				<include content="Fold_KeyHint"><param name="key" value="↑ ↓"/><param name="label" value="Tracks and words"/></include>
				<include content="Fold_KeyHint"><param name="key" value="BACK"/><param name="label" value="Close the sleeve"/></include>
			</control>
		</control>
	</controls>
</window>
"""
    import re
    x = re.sub(r"(\s*)<textcolor>([^<]+)</textcolor>(?!\s*<selectedcolor>)",
               lambda m: f"{m.group(1)}<textcolor>{m.group(2)}</textcolor>{m.group(1)}<selectedcolor>{m.group(2)}</selectedcolor>", x)
    OUT.write_text(finish_xml(strip_defaults(x, OUT.parent / "Defaults.xml")), encoding="utf-8", newline="\n")
    print("DialogMusicInfo.xml written", ww)


if __name__ == "__main__":
    build()
