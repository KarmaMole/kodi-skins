"""One-off: Dlg_IndexListLayout (Settings hub, System menu, button menu) as a line of stops instead of Majan's
numbered index. Kept for the record."""
import re
from pathlib import Path

X = Path(__file__).resolve().parents[1] / "1080i"


def replace_include(path, name, new):
    p = X / path
    s = p.read_text(encoding="utf-8")
    start = s.index(f'<include name="{name}"')
    depth, end = 0, None
    for m in re.compile(r"<include\b[^>]*?(/?)>|</include>").finditer(s, start):
        if m.group(0) == "</include>":
            depth -= 1
            if depth == 0:
                end = m.end()
                break
        elif m.group(1) == "/":
            continue
        else:
            depth += 1
    p.write_text(s[:start] + new.strip() + s[end:], encoding="utf-8")

ROW = """<control type="image"><left>33</left><top>0</top><width>6</width><height>$PARAM[height]</height><texture colordiffuse="hair_strong">common/white.png</texture></control>"""


def stop(focused):
    if focused:
        return ("""<control type="image"><left>17</left><centertop>50%</centertop><width>38</width><height>38</height><texture colordiffuse="white">sd/disc_32.png</texture><visible>!Control.HasFocus($PARAM[list_id])</visible></control>
				<control type="image"><left>17</left><centertop>50%</centertop><width>38</width><height>38</height><texture colordiffuse="ink">sd/ring_32_8.png</texture><visible>!Control.HasFocus($PARAM[list_id])</visible></control>
				<control type="image"><left>17</left><centertop>50%</centertop><width>38</width><height>38</height><texture colordiffuse="ink">sd/disc_32.png</texture><visible>Control.HasFocus($PARAM[list_id])</visible></control>
				<control type="image"><left>17</left><centertop>50%</centertop><width>38</width><height>38</height><texture colordiffuse="white">sd/ring_32_8.png</texture><visible>Control.HasFocus($PARAM[list_id])</visible></control>""")
    return ("""<control type="image"><left>21</left><centertop>50%</centertop><width>30</width><height>30</height><texture colordiffuse="white">sd/disc_24.png</texture></control>
				<control type="image"><left>21</left><centertop>50%</centertop><width>30</width><height>30</height><texture colordiffuse="l_route">sd/ring_24_6.png</texture></control>""")


def labels(focused):
    out = []
    for vis, col, col2, font in (("!Control.HasFocus($PARAM[list_id])" if focused else "true", "ink", "ink2", "xb_26" if focused else "semi_26"),
                                 ("Control.HasFocus($PARAM[list_id])", "white", "white", "xb_26")):
        if not focused and col == "white":
            continue
        out.append(f"""<control type="label"><left>72</left><top>0</top><right>230</right><height>$PARAM[height]</height><font>{font}</font>
					<textcolor>{col}</textcolor><selectedcolor>{col}</selectedcolor><label>$INFO[ListItem.Label]</label><visible>{vis}</visible></control>
				<control type="label"><right>28</right><top>0</top><width>210</width><height>$PARAM[height]</height><align>right</align><font>semi_22</font>
					<textcolor>{col2}</textcolor><selectedcolor>{col2}</selectedcolor><label>$INFO[ListItem.Label2]</label><visible>{vis}</visible></control>""")
    return "\n				".join(out)


NEW = f"""<include name="Dlg_IndexListLayout">
		<param name="width">860</param>
		<param name="height">72</param>
		<param name="list_id">9000</param>
		<definition>
			<itemlayout width="$PARAM[width]" height="$PARAM[height]">
				{ROW}
				{stop(False)}
				{labels(False)}
			</itemlayout>
			<focusedlayout width="$PARAM[width]" height="$PARAM[height]">
				{ROW}
				<include content="Dlg_RowFocus">
					<param name="list_id" value="$PARAM[list_id]"/>
					<param name="width" value="$PARAM[width]"/>
					<param name="height" value="$PARAM[height]"/>
				</include>
				{stop(True)}
				{labels(True)}
			</focusedlayout>
		</definition>
	</include>"""

if __name__ == "__main__":
    replace_include("Includes_Dialogs.xml", "Dlg_IndexListLayout", NEW)
    print("index list restyled")
