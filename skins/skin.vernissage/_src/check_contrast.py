"""Contrast proof for the five light steps (SPEC 5).   python skins/skin.vernissage/_src/check_contrast.py [-v]

For every step 0-4, the wall and the card as the skin draws them at rest (make_rooms.py composites the ground tokens:
Evening layer over Day layer at the step's alpha) must carry ink AND ink2 at >= 4.5:1 (WCAG 2.x relative luminance).
Extra pairs from DESIGN.md section 3:
  * Evening ink2 on the brightest pool skirt text can reach (#3A3936 at full pool; at step 2 the pool is at 60 %,
    at step 3 at 85 %: the lift above the wall scales with it);
  * Evening ink / ink2 on the OSD placard over a white video frame (card at 90 % over white);
  * on_ink on an ink fill (focused chips), both text sets;
  * Day-set ink2 on the darkest vignetted wall measured on the TV at steps 0-1 (CORNER).
Exit 1 on any pair under 4.5:1 (the build fails). -v prints every pair.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_rooms as R  # noqa: E402

MIN = 4.5
SKIRT = "ff3a3936"
CORNER = {0: "DEDCD9", 1: "B4B2B1"}  # darkest vignetted wall near text, steps 0-1 (device screenshots 2026-10-21)


def lin(c: int) -> float:
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(h: str):
    h = h[-6:]
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def over(top: str, bottom_rgb):
    """Composite an ARGB colour over an opaque RGB."""
    a = int(top[:2], 16) / 255
    return [round(t * a + b * (1 - a)) for t, b in zip(rgb(top), bottom_rgb)]


def lum(c) -> float:
    r, g, b = c
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b) -> float:
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def main(verbose: bool) -> int:
    _s, _h, pal = R.read_palette()
    bad = 0
    rows = []

    def check(what, fg, bg):
        nonlocal bad
        r = ratio(fg, bg)
        ok = r >= MIN
        bad += not ok
        rows.append((ok, what, r))

    for k in range(5):
        wall = rgb(R.step_rgb(pal, "wall", k))
        card = rgb(R.step_rgb(pal, "card", k))
        for tok in ("ink", "ink2"):
            fg_argb = R.step_rgb(pal, tok, k)
            check(f"step {k}: {tok} on wall #{''.join(f'{c:02X}' for c in wall)}", over(fg_argb, wall), wall)
            check(f"step {k}: {tok} on card #{''.join(f'{c:02X}' for c in card)}", over(fg_argb, card), card)
        # pool skirt: the spot colour at the skirt's alpha (DESIGN: #3A3936 = spot over the Evening wall at full pool),
        # scaled by this step's pool strength, over this step's wall
        pool = R.SPOT_ALPHA[k] / 100
        if pool and k >= R.TEXT_SWITCH:
            spot, ew = rgb(pal["eve_spot"]), rgb(pal["eve_wall"])
            a_full = (rgb(SKIRT)[0] - ew[0]) / (spot[0] - ew[0])
            a = a_full * pool
            lit = [round(w * (1 - a) + sp * a) for w, sp in zip(wall, spot)]
            check(f"step {k}: ink2 on the pool skirt ({R.SPOT_ALPHA[k]} %)", over(R.step_rgb(pal, "ink2", k), lit), lit)
        # the room washes' vignette, measured on the TV (M5 device audit, Home screenshots): the darkest wall under
        # Day-set text (the Home hint / rail icons sit in the bottom-right corner) at the light steps
        if k in CORNER:
            c = rgb(CORNER[k])
            check(f"step {k}: ink2 on the vignette corner #{CORNER[k]} (TV)", over(R.step_rgb(pal, "ink2", k), c), c)
        # text on an ink fill
        ink = rgb(R.step_rgb(pal, "ink", k))
        check(f"step {k}: on_ink on ink", over(R.step_rgb(pal, "on_ink", k), ink), ink)
    # OSD placard over a white frame (playback is always Evening)
    osd = over("e6" + pal["eve_card"][2:], [255, 255, 255])
    for tok in ("ink", "ink2"):
        check(f"OSD: eve {tok} on card 90 % over white", over(pal[f"eve_{tok}"], osd), osd)

    for ok, what, r in rows:
        if verbose or not ok:
            print(f"{'ok  ' if ok else 'FAIL'} {r:5.2f}:1  {what}")
    print(f"{len(rows)} pairs, {bad} under {MIN}:1")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main("-v" in sys.argv))
