"""Engine + transitional textures for the forked windows (M1).   python skins/skin.groove/_src/make_placeholders.py

NEVER overwrites a file that exists: visual-designer's make_textures.py owns media/groove/ and media/icons/ and wins.
Writes:
  * engine textures copied from skin.nocturne (Nocturne's brass-coloured rect_* and dark watched markers whitened) (neutral white shapes, masks, markers, calibration art):
    common/, focus/, masks/, markers/, misc/, osd/  (only the ENGINE_KEEP names the live XML uses)
  * media/fork/: Nocturne's torch/brass textures as WHITE + their alpha (tinted by room tokens in XML). Transitional:
    each disappears when M2-M4 redraw the window that uses it (CONVENTIONS.md section 6).
  * placeholder icons the designer's set doesn't have yet (copied from Nocturne's white engine icons):
    icons/chevron-right, chevron-down, back, audio, subtitles, chapters, info  (requested in CONVENTIONS.md)
  * icon.png (256, solid) and fanart.jpg (1920x1080) placeholders if absent.
"""
from pathlib import Path
import shutil

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NOC = ROOT.parent / "skin.nocturne" / "media"
M = ROOT / "media"
FORK_KEEP = {"tick", "dot_on", "dot_off", "rail_on", "plaque_dim", "glow_bar", "glow_warm"}
# Engine textures the live XML still uses (dead-code pass 2026-10-21 removed the forked includes that named the rest
# and moved those files out). Same rule as FORK_KEEP: grep 1080i before adding one back.
ENGINE_KEEP = {
    "common": {"gradient_bottom", "gradient_top", "hairline", "hairline_v", "rect_outline_1", "rect_outline_1_round8",
               "rect_round8", "rect_square", "scrim_left"},
    "focus": {"outline_2", "outline_2_round", "outline_3", "outline_3_round"},
    "markers": {"check"},
    "masks": {"square_round8"},
    "misc": None,       # None = the whole folder (calibration art, EPG now-line)
    "osd": {"slider_bg", "slider_nib"},
}
made = []


def put(rel, fn):
    p = M / rel
    if p.exists():
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    fn(p)
    made.append(rel)


def copy(src):
    return lambda p: shutil.copy(src, p)


def whiten(src):
    def fn(p):
        im = Image.open(src).convert("RGBA")
        a = im.getchannel("A")
        if src.suffix == ".png" and src.stem.startswith(("shroud", "ceiling", "floor_ramp")):
            pass  # alpha already = darkness
        w = Image.new("RGBA", im.size, (255, 255, 255, 0))
        w.putalpha(a)
        w.save(p, optimize=True)
    return fn


def main():
    for d, keep in ENGINE_KEEP.items():
        for f in sorted((NOC / d).glob("*.png")):
            if keep is not None and f.stem not in keep:
                continue
            if (d == "markers" and f.stem.startswith("watched")) or (d == "common" and f.stem.startswith("rect_")):
                put(f"{d}/{f.name}", whiten(f))
            else:
                put(f"{d}/{f.name}", copy(f))
    # Only the fork textures the live XML still uses (QA 2026-10-21 pruned the other 55 and fork/views/). Before
    # adding one back, grep 1080i for it; when a window stops using one, drop it here and delete the file.
    for f in sorted((NOC / "noc").glob("*.png")):
        if f.stem in FORK_KEEP:
            put(f"fork/{f.name}", whiten(f))
    for new, old in (("chevron-right", "chevron_right"), ("chevron-down", "chevron_down"), ("back", "back"),
                     ("audio", "audio"), ("subtitles", "subtitles"), ("chapters", "chapters"), ("info", "info"),
                     ("rewind", "rewind"), ("forward", "forward")):
        put(f"icons/{new}.png", copy(NOC / "icons" / f"{old}.png"))

    def icon(p):
        im = Image.new("RGB", (256, 256), (34, 31, 28))
        im.save(p)
    if not (ROOT / "resources" / "icon.png").exists():
        icon(ROOT / "resources" / "icon.png")
        made.append("../resources/icon.png")
    if not (ROOT / "resources" / "fanart.jpg").exists():
        room = M / "groove" / "dark" / "room.png"
        im = Image.open(room).convert("RGB").resize((1920, 1080)) if room.exists() else Image.new("RGB", (1920, 1080), (34, 31, 28))
        im.save(ROOT / "resources" / "fanart.jpg", quality=90)
        made.append("../resources/fanart.jpg")
    print(f"{len(made)} placeholder(s) written")
    for r in made:
        print("  ", r)


if __name__ == "__main__":
    main()
