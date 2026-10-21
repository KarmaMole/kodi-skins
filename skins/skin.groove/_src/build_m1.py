"""Rebuild every generated part of Groove, in order.   python skins/skin.groove/_src/build_m1.py [--fork]

  --fork   also re-run the Nocturne fork (fork_engine.py --yes) first. ONLY while no forked window has been edited by
           hand (M1). From M2 on, never pass --fork: it overwrites the forked windows.
Then: motion draft merge, theme (room tokens), Font.xml, Home, SkinSettings, music views, Time machine, Wheel,
Now Playing / album info / mini player, placeholder textures (never overwrite), the room-token lint and the validator.
Textures (make_textures.py, make_view_previews.py) and fonts (make_fonts.py) are run by hand.
"""
from pathlib import Path
import subprocess
import sys

SRC = Path(__file__).resolve().parent
REPO = SRC.parents[2]
PY = sys.executable


def run(*args):
    print(">", " ".join(str(a) for a in args))
    r = subprocess.run([PY, *map(str, args)], cwd=REPO)
    if r.returncode:
        sys.exit(r.returncode)


def main():
    if "--fork" in sys.argv:
        run(SRC / "fork_engine.py", "--yes")
    # always: idempotent, and it carries the Hidden-twin collapse (DEVICE_AUDIT pass 2 P2-4) into every build
    run(SRC / "merge_motion.py")
    run(SRC / "make_theme.py")
    run(SRC / "make_fontxml.py")
    run(SRC / "make_home.py")
    run(SRC / "make_skinsettings.py")
    # M2-M3 lanes (all deterministic; QA 2026-10-21 checked that a re-run reproduces the shipped XML byte for byte)
    run(SRC / "make_music_views.py")
    run(SRC / "make_timemachine.py")
    run(SRC / "make_wheel.py")
    run(SRC / "make_player.py")
    run(SRC / "make_placeholders.py")
    run(SRC / "check_tokens.py")
    run(REPO / ".claude/skills/kodi-skin-validate/scripts/validate_skin.py", "skins/skin.groove",
        "--reference", "reference/skin.estuary-omega")


if __name__ == "__main__":
    main()
