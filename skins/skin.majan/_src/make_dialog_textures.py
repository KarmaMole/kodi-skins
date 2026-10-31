"""Generate the dialog/settings textures owned by Builder E (media/dialogs/).

Why a separate texture: Kodi clones the settings templates (DialogSettings, SettingsCategory,
DialogAddonSettings) as single controls, so a row can't carry an extra hairline image. The row's
<texturenofocus> therefore IS the hairline: a 4x4 white PNG whose bottom row is opaque and the rest
transparent. Use it with border="0,0,0,1" so the bottom pixel row stays 1 px at any row height
Tint with colordiffuse (hairline / hairline_strong). row_rule_top.png is for a top rule, with
border="0,3,0,0": flipy turns the picture but not the border, so flipping row_rule.png stretches the opaque
line down the row. Its line is on row 1, not row 0: past the last column the bench's renderer blends in the
FIRST texel, so an opaque row 0 drew a gradient down the right end of every row.

panel_framed.png: Kodi resizes ONLY image 999 in DialogContextMenu, so the panel fill and its 1 px
frame are baked into one opaque 32x32 texture (frame = hairline_strong #333333, fill = bg #0b0b0b,
the same values as colors/defaults.xml). Use with border="2" and NO colordiffuse.

Usage:  python skins/skin.majan/_src/make_dialog_textures.py
"""
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "media" / "dialogs"


def row_rule():
    # 4x8: rows 0-5 transparent (stretched centre), row 6 transparent buffer, row 7 the 1px rule.
    # Used with border="0,0,0,2": the buffer row sits inside the border, so bilinear filtering of
    # the stretched centre never samples the opaque rule (a 1px border smeared it into a gradient
    # across the whole row on the Shield).
    img = Image.new("RGBA", (4, 8), (255, 255, 255, 0))
    for x in range(4):
        img.putpixel((x, 7), (255, 255, 255, 255))
    return img


def row_rule_top():
    # 4x8: row 0 transparent (see the docstring), row 1 the 1px rule, row 2 buffer, rows 3-7 stretched centre.
    img = Image.new("RGBA", (4, 8), (255, 255, 255, 0))
    for x in range(4):
        img.putpixel((x, 1), (255, 255, 255, 255))
    return img


def panel_framed():
    fill, frame = (11, 11, 11, 255), (51, 51, 51, 255)
    img = Image.new("RGBA", (32, 32), fill)
    for i in range(32):
        for x, y in ((i, 0), (i, 31), (0, i), (31, i)):
            img.putpixel((x, y), frame)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    row_rule().save(OUT / "row_rule.png", optimize=True)
    row_rule_top().save(OUT / "row_rule_top.png", optimize=True)
    panel_framed().save(OUT / "panel_framed.png", optimize=True)
    print(f"wrote {OUT / 'row_rule.png'}, {OUT / 'panel_framed.png'}")


if __name__ == "__main__":
    main()
