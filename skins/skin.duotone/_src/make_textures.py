"""Generate Duotone's textures (reproducible). Everything is white-on-transparent and coloured in XML
with colordiffuse ($VAR look tokens), except the few marked "baked": those come once per look, with the colours
read from colors/defaults.xml (co_ / lt_ / dk_ tokens), and Includes_Theme.xml picks the file
($VAR[DT_TexWatched], $VAR[DT_PanelTex]). Re-run after changing those palette values.

Duotone rules: no gradients, no rounding, thick 8px ink rules and frames, solid geometric icons.

  common/white.png            8x8 solid
  common/hairline.png         8x8 solid (rules are just solid strips; thickness comes from XML)
  common/hairline_v.png       8x8 solid
  common/rect_square.png      32x32 solid (block fill, border 10)
  common/rect_outline_1.png   40x40 4px ring + transparent buffer (border 10) - small controls
  common/rect_outline_8.png   48x48 8px ring + transparent buffer (border 16) - action blocks
  focus/outline_2.png, outline_3.png, frame_8.png   48x48 8px ring (border 16), placed at item -8px
  focus/halo.png              transparent (flat design: no glow)
  markers/watched.png         44x44 ink block with a paper check (mockup .wt)  - baked: Colour look
  markers/watched_light.png, watched_dark.png   the same in the Light / Dark looks' ink and paper
  markers/unwatched.png       24x24 solid square (colordiffuse)
  markers/check.png           48x48 bold check (radio buttons)
  overlays/dots.png           1920x1080 halftone, 8px grid, white dots r1.4/1.9 at 12% (mockup .dots), $VAR[dots]
  overlays/dots_art.png       1920x1080 halftone for art, 8px grid, slightly bigger dots at 14%, $VAR[dots_art]
  icons/*.png                 64x64 solid icons
  osd/slider_bg.png, osd/slider_nib.png, osd/tick.png
  vidview/underline.png       8px bar; dialogs/row_rule.png 2px rule + buffer
  dialogs/panel_framed.png    48x48 white fill + 8px ink frame (Colour / Light: tinted with the field)
  dialogs/panel_framed_dark.png   baked Dark panel: dk_sec_paper fill + dk_ink frame, drawn untinted

Usage:  python skins/skin.duotone/_src/make_textures.py
"""
from pathlib import Path
import math

from PIL import Image, ImageDraw

from theme_tokens import palette, rgba

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
WHITE = (255, 255, 255, 255)
PAL = palette()
INK = rgba(PAL["co_ink"])          # (17, 17, 17, 255)
PAPER = rgba(PAL["co_paper"])      # (241, 237, 228, 255)
SS = 4  # supersampling for icons


# Drawn below but named by no XML (removed from media/ 2026-10-30): never written again.
UNUSED = {
    "common/shadow_soft.png", "focus/outline_2_round.png", "focus/outline_3.png", "focus/outline_3_round.png",
    "icons/chevron_down.png", "markers/unwatched_round.png", "markers/watched_round.png"
}


def save(img: Image.Image, rel: str) -> None:
    if rel in UNUSED:
        return
    p = MEDIA / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)


def solid(w, h, col=WHITE):
    return Image.new("RGBA", (w, h), col)


def ring(size, thick):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, size - 1, thick - 1], fill=WHITE)
    d.rectangle([0, size - thick, size - 1, size - 1], fill=WHITE)
    d.rectangle([0, 0, thick - 1, size - 1], fill=WHITE)
    d.rectangle([size - thick, 0, size - 1, size - 1], fill=WHITE)
    return im


def dots(w, h, pitch=8, r_in=1.4, r_out=1.9, alpha=0.12, offset=4.0):
    """radial-gradient(circle, ink a r_in, transparent r_out) on a pitch grid (CSS background-size)."""
    tile = Image.new("RGBA", (pitch, pitch), (0, 0, 0, 0))
    px = tile.load()
    n = 8  # subsamples per axis
    for y in range(pitch):
        for x in range(pitch):
            acc = 0.0
            for sy in range(n):
                for sx in range(n):
                    fx = x + (sx + 0.5) / n - offset
                    fy = y + (sy + 0.5) / n - offset
                    dist = math.hypot(fx, fy)
                    if dist <= r_in:
                        a = 1.0
                    elif dist >= r_out:
                        a = 0.0
                    else:
                        a = 1.0 - (dist - r_in) / (r_out - r_in)
                    acc += a
            a = acc / (n * n) * alpha
            px[x, y] = (255, 255, 255, round(a * 255))   # white: the look token tints it
    im = Image.new("RGBA", (w, h))
    for yy in range(0, h, pitch):
        for xx in range(0, w, pitch):
            im.paste(tile, (xx, yy))
    return im


# ---------------------------------------------------------------- icons (drawn at 64*SS)
def canvas():
    return Image.new("RGBA", (64 * SS, 64 * SS), (0, 0, 0, 0))


def P(*pts):
    return [(x * SS, y * SS) for x, y in pts]


def finish(im):
    return im.resize((64, 64), Image.LANCZOS)


def icon_play():
    im = canvas(); ImageDraw.Draw(im).polygon(P((16, 8), (56, 32), (16, 56)), fill=WHITE); return finish(im)


def icon_pause():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rectangle(P((14, 8), (27, 56)), fill=WHITE); d.rectangle(P((37, 8), (50, 56)), fill=WHITE); return finish(im)


def icon_stop():
    im = canvas(); ImageDraw.Draw(im).rectangle(P((10, 10), (54, 54)), fill=WHITE); return finish(im)


def icon_next():
    im = canvas(); d = ImageDraw.Draw(im)
    d.polygon(P((8, 10), (40, 32), (8, 54)), fill=WHITE); d.rectangle(P((44, 10), (54, 54)), fill=WHITE); return finish(im)


def icon_prev():
    return icon_next().transpose(Image.FLIP_LEFT_RIGHT)


def icon_forward():
    im = canvas(); d = ImageDraw.Draw(im)
    d.polygon(P((4, 12), (32, 32), (4, 52)), fill=WHITE); d.polygon(P((32, 12), (60, 32), (32, 52)), fill=WHITE); return finish(im)


def icon_rewind():
    return icon_forward().transpose(Image.FLIP_LEFT_RIGHT)


def icon_chevron_right():
    im = canvas(); ImageDraw.Draw(im).line(P((22, 10), (44, 32), (22, 54)), fill=WHITE, width=9 * SS, joint="curve"); return finish(im)


def icon_chevron_down():
    return icon_chevron_right().rotate(-90)


def icon_back():
    im = canvas(); d = ImageDraw.Draw(im)
    d.line(P((30, 12), (10, 32), (30, 52)), fill=WHITE, width=9 * SS, joint="curve")
    d.line(P((12, 32), (56, 32)), fill=WHITE, width=9 * SS); return finish(im)


def icon_info():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rectangle(P((26, 8), (38, 19)), fill=WHITE); d.rectangle(P((26, 25), (38, 56)), fill=WHITE)
    d.rectangle(P((18, 25), (38, 32)), fill=WHITE); d.rectangle(P((18, 50), (46, 56)), fill=WHITE); return finish(im)


def icon_search():
    im = canvas(); d = ImageDraw.Draw(im)
    d.ellipse(P((6, 6), (42, 42)), outline=WHITE, width=9 * SS)
    d.line(P((36, 36), (58, 58)), fill=WHITE, width=11 * SS); return finish(im)


def icon_settings():
    im = canvas(); d = ImageDraw.Draw(im)
    c = 32 * SS
    for k in range(8):
        a = k * math.pi / 4
        dx, dy = math.cos(a), math.sin(a)
        w = 7 * SS
        pts = [(c + dx * 18 * SS - dy * w, c + dy * 18 * SS + dx * w), (c + dx * 30 * SS - dy * w, c + dy * 30 * SS + dx * w),
               (c + dx * 30 * SS + dy * w, c + dy * 30 * SS - dx * w), (c + dx * 18 * SS + dy * w, c + dy * 18 * SS - dx * w)]
        d.polygon(pts, fill=WHITE)
    d.ellipse([c - 22 * SS, c - 22 * SS, c + 22 * SS, c + 22 * SS], fill=WHITE)
    d.ellipse([c - 9 * SS, c - 9 * SS, c + 9 * SS, c + 9 * SS], fill=(0, 0, 0, 0)); return finish(im)


def icon_audio():
    im = canvas(); d = ImageDraw.Draw(im)
    for x0, top in ((6, 30), (20, 14), (34, 22), (48, 6)):
        d.rectangle(P((x0, top), (x0 + 9, 58)), fill=WHITE)
    return finish(im)


def icon_subtitles():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rectangle(P((4, 10), (60, 54)), outline=WHITE, width=7 * SS)
    d.rectangle(P((14, 30), (32, 36)), fill=WHITE); d.rectangle(P((36, 30), (50, 36)), fill=WHITE)
    d.rectangle(P((14, 41), (24, 47)), fill=WHITE); d.rectangle(P((28, 41), (50, 47)), fill=WHITE); return finish(im)


def icon_chapters():
    im = canvas(); d = ImageDraw.Draw(im)
    for y in (8, 26, 44):
        d.rectangle(P((6, y), (16, y + 11)), fill=WHITE); d.rectangle(P((22, y), (58, y + 11)), fill=WHITE)
    return finish(im)


def icon_shuffle():
    im = canvas(); d = ImageDraw.Draw(im)
    d.line(P((6, 16), (22, 16), (42, 48), (52, 48)), fill=WHITE, width=7 * SS, joint="curve")
    d.line(P((6, 48), (22, 48), (42, 16), (52, 16)), fill=WHITE, width=7 * SS, joint="curve")
    d.polygon(P((50, 6), (62, 16), (50, 26)), fill=WHITE); d.polygon(P((50, 38), (62, 48), (50, 58)), fill=WHITE); return finish(im)


def icon_repeat():
    im = canvas(); d = ImageDraw.Draw(im)
    d.line(P((8, 36), (8, 16), (50, 16)), fill=WHITE, width=7 * SS, joint="curve")
    d.line(P((56, 28), (56, 48), (14, 48)), fill=WHITE, width=7 * SS, joint="curve")
    d.polygon(P((46, 6), (60, 16), (46, 26)), fill=WHITE); d.polygon(P((18, 38), (4, 48), (18, 58)), fill=WHITE); return finish(im)


def check(size, width):
    im = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    s = size / 24.0
    pts = [(4.5 * s * SS, 12.5 * s * SS), (9.5 * s * SS, 17.5 * s * SS), (19.5 * s * SS, 7 * s * SS)]
    ImageDraw.Draw(im).line(pts, fill=WHITE, width=round(width * s * SS), joint="curve")
    return im.resize((size, size), Image.LANCZOS)


def main():
    save(solid(8, 8), "common/white.png")
    save(solid(8, 8), "common/hairline.png")
    save(solid(8, 8), "common/hairline_v.png")
    save(solid(32, 32), "common/rect_square.png")
    save(ring(40, 4), "common/rect_outline_1.png")
    save(ring(48, 8), "common/rect_outline_8.png")
    for n in ("outline_2", "outline_3", "frame_8", "outline_2_round", "outline_3_round"):
        save(ring(48, 8), f"focus/{n}.png")
    save(Image.new("RGBA", (64, 64), (0, 0, 0, 0)), "focus/halo.png")
    save(Image.new("RGBA", (64, 64), (0, 0, 0, 0)), "common/shadow_soft.png")
    # watched block (ink, paper check), baked once per look
    for look, suffix in (("co", ""), ("lt", "_light"), ("dk", "_dark")):
        w = Image.new("RGBA", (44, 44), rgba(PAL[f"{look}_ink"]))
        ck = check(24, 3.2)
        paper_ck = Image.new("RGBA", ck.size, rgba(PAL[f"{look}_paper"]))
        paper_ck.putalpha(ck.split()[3])
        w.alpha_composite(paper_ck, (10, 10))
        save(w, f"markers/watched{suffix}.png")
        if look == "co":
            save(w, "markers/watched_round.png")
    save(solid(24, 24), "markers/unwatched.png"); save(solid(24, 24), "markers/unwatched_round.png")
    save(check(48, 3.4), "markers/check.png")
    # halftone overlays
    save(dots(1920, 1080), "overlays/dots.png")
    save(dots(1920, 1080, r_in=1.7, r_out=2.3, alpha=0.14), "overlays/dots_art.png")
    # icons
    for name, fn in [("play", icon_play), ("pause", icon_pause), ("stop", icon_stop), ("next", icon_next), ("prev", icon_prev),
                     ("forward", icon_forward), ("rewind", icon_rewind), ("chevron_right", icon_chevron_right),
                     ("chevron_down", icon_chevron_down), ("back", icon_back), ("info", icon_info), ("search", icon_search),
                     ("settings", icon_settings), ("audio", icon_audio), ("subtitles", icon_subtitles), ("chapters", icon_chapters),
                     ("shuffle", icon_shuffle), ("repeat", icon_repeat)]:
        save(fn(), f"icons/{name}.png")
    # OSD
    save(Image.new("RGBA", (16, 16), (0, 0, 0, 0)), "osd/slider_bg.png")   # transparent: sliders/ranges draw only nib / ticks
    save(solid(8, 32), "osd/slider_nib.png")   # Kodi draws the nib at 2x the slider height: 16px slider -> 8x32 block
    save(solid(6, 32), "osd/tick.png")
    ul = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); ImageDraw.Draw(ul).rectangle([0, 12, 15, 15], fill=WHITE)
    save(ul, "vidview/underline.png")   # 4px bar at the bottom; use border="0,0,0,6" (2 transparent buffer rows)
    # 2px rule at the bottom + 2 transparent buffer rows inside the border (use border="0,0,0,4": LESSONS 9-slice)
    rr = Image.new("RGBA", (8, 8), (0, 0, 0, 0)); ImageDraw.Draw(rr).rectangle([0, 6, 7, 7], fill=WHITE)
    save(rr, "dialogs/row_rule.png")
    # context menu / system menu panel: paper block with an 8px ink frame (border 16 in XML is fine;
    # Kodi only resizes this one image for the context menu)
    # white fill + ink frame: colordiffuse="$VAR[SectionColor]" gives a section-colour panel, the frame stays ink
    pf = Image.new("RGBA", (48, 48), WHITE); d = ImageDraw.Draw(pf)
    for i in range(8):
        d.rectangle([i, i, 47 - i, 47 - i], outline=INK)
    save(pf, "dialogs/panel_framed.png")
    # Dark look: a multiply can't lighten the frame over a near-black fill, so the panel is baked and drawn white
    pd = Image.new("RGBA", (48, 48), rgba(PAL["dk_sec_paper"])); d = ImageDraw.Draw(pd)
    for i in range(8):
        d.rectangle([i, i, 47 - i, 47 - i], outline=rgba(PAL["dk_ink"]))
    save(pd, "dialogs/panel_framed_dark.png")
    print("textures written to", MEDIA)


if __name__ == "__main__":
    main()
