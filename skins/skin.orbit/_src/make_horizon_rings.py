"""Engraved tracks for the 0.9.16 Horizon views (arc_horizon.py geometry). Run:
    python skins/skin.orbit/_src/make_horizon_rings.py

  rings/horizon_arc.png     video horizon (view 503): track r 2210 about (960, 3106), under the wide cards;
                            1-degree hairline ticks, 5-degree major ticks, the amber lens marker under the lens.
  rings/horizon_arc_sq.png  music horizon (view 507): track r 2200 about (960, 3060), under the covers / discs.
Both are screen pieces of the bottom of the page (drawn in screen coordinates, cropped), same pens as lib_arc.png.
Writes only these two files (make_rings.py owns the rest of media/rings).
"""
from make_rings import AMBER, LINE, TICK, ring, screen_piece, ticks


def horizon(cy, r, lens_bottom, y0, name):
    def fn(d, T, ss):
        cx, ccy = T(960, cy)
        ring(d, cx, ccy, r * ss, 1.5 * ss, LINE)
        ticks(d, cx, ccy, r * ss, (r + 10) * ss, 360, 1.5 * ss, LINE, offset_deg=0.5)
        ticks(d, cx, ccy, (r - 12) * ss, (r + 10) * ss, 72, 1.5 * ss, TICK)
        x, y_top = T(960, lens_bottom + 18)
        _, y_bot = T(960, cy - r + 12)
        d.line([(x, y_top), (x, y_bot)], fill=AMBER, width=3 * ss)
    screen_piece(0, y0, 1920, 1080 - y0, fn, name, ss=2)


if __name__ == "__main__":
    horizon(3106, 2210, 841, 760, "horizon_arc.png")
    horizon(3060, 2200, 825, 740, "horizon_arc_sq.png")
    print("wrote rings/horizon_arc.png, rings/horizon_arc_sq.png")
