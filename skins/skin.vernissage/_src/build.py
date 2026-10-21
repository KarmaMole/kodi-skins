"""Rebuild every generated part of Vernissage, then run every check.   python skins/skin.vernissage/_src/build.py [--check]

Order: fonts, Font.xml, textures + icons, the add-on art (icon.png / fanart.jpg: reads spot, vignette, flags), view previews, Home, SkinSettings, Search, Timers, then the room engine LAST
(make_rooms.py emits a token variable only when some other file reads it). Then the checks, all of which must pass:
check_contrast (4.5:1 at every step), check_tokens (room tokens / twins), check_twins (Hidden / Focus twins), reach
(no dead definitions, textures, or missing textures), text hygiene (UTF-8, no CRLF, no double-encoded text), the
studio validator, kdk (the Kodi repository review) and the screens' placard budgets against the real Font.xml.
--check   reproducibility: hash every generated file, rebuild, and fail if anything changed (run on a clean tree).
fork_from_groove.py is a one-off and is never run from here.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
SKIN = SRC.parent
REPO = SKIN.parents[1]
PY = sys.executable
GENERATORS = ["make_fonts.py", "make_fontxml.py", "make_textures.py", "make_addon_art.py", "make_view_previews.py", "make_times.py", "make_home.py",
              "make_info.py", "make_listening.py", "make_playback.py",
              "make_libviews.py", "make_library.py",
              "make_skinsettings.py", "make_search.py", "make_timers.py", "make_rooms.py"]
CHECKS = [
    [SRC / "check_contrast.py"], [SRC / "check_tokens.py"], [SRC / "check_twins.py"], [SRC / "reach.py"],
    [REPO / ".claude/skills/kodi-skin-validate/scripts/validate_skin.py", "skins/skin.vernissage",
     "--reference", "reference/skin.estuary-omega"],
    [REPO / "tools/lint/run_kodi_review.py", "skins/skin.vernissage"],
    [REPO / "docs/skin.vernissage/screens/_src/measure_placards.py", "--skin", "skins/skin.vernissage"],
]
MOJIBAKE = re.compile("[ÂÃâ][\u0080-¿€™œš]")


def run(args, quiet=False):
    r = subprocess.run([PY, *map(str, args)], cwd=REPO, capture_output=quiet, text=True)
    return r.returncode


def tree_hash():
    out = {}
    for p in sorted(list(SKIN.rglob("*"))):
        if p.is_file() and "_src" not in p.parts:
            out[p.relative_to(SKIN).as_posix()] = hashlib.md5(p.read_bytes()).hexdigest()
    return out


def hygiene():
    bad = 0
    for p in SKIN.rglob("*"):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix not in (".xml", ".po", ".txt", ".py", ".md"):
            continue
        b = p.read_bytes()
        try:
            t = b.decode("utf-8")
        except UnicodeDecodeError:
            print(f"not UTF-8: {p}")
            bad += 1
            continue
        if b"\r" in b:
            print(f"CRLF: {p}")
            bad += 1
        if b.startswith(b"\xef\xbb\xbf"):
            print(f"BOM: {p}")
            bad += 1
        if MOJIBAKE.search(t):
            print(f"double-encoded text: {p}")
            bad += 1
    print(f"text hygiene: {bad} finding(s)")
    return 1 if bad else 0


def main():
    before = tree_hash() if "--check" in sys.argv else None
    for g in GENERATORS:
        print(">", g)
        if run([SRC / g]):
            sys.exit(f"generator failed: {g}")
    if before is not None:
        after = tree_hash()
        diff = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        for k in diff:
            print("changed by a rebuild:", k)
        print(f"reproducible: {'yes' if not diff else 'NO'}")
        if diff:
            sys.exit(1)
    # the placard solver's fit log (placard.report): every runtime case per context, what dropped, the spare
    sys.path.insert(0, str(SRC))
    import placard_log  # noqa: E402
    placard_log.main()
    failed = []
    for c in CHECKS:
        print(">", Path(c[0]).name, *c[1:])
        if run(c):
            failed.append(Path(c[0]).name)
    if hygiene():
        failed.append("hygiene")
    print("FAILED: " + ", ".join(failed) if failed else "all checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
