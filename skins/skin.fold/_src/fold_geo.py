"""Shared geometry for the generators (library shelf slots the info spread opens from)."""

# Library shelf (view 500, Includes_Views_Video.xml): panel 5 x 2, slot 268 x 412, panel at (56, 150).
# Resting card 228 x 352 at (40, 44) in its slot; the lifted card is 252 x 388, bottom-centre anchored.
SHELF_X, SHELF_Y = 56, 150
SHELF_SLOT_W, SHELF_SLOT_H = 268, 412
SHELF_COLS, SHELF_ROWS = 5, 2
SHELF_PAD_X, SHELF_PAD_Y = 40, 44
SHELF_CARD_W, SHELF_CARD_H = 228, 352
SHELF_LIFT_W, SHELF_LIFT_H = 252, 388

SHELF_SLOTS = {}
for _pos in range(SHELF_COLS * SHELF_ROWS):
    _c, _r = _pos % SHELF_COLS, _pos // SHELF_COLS
    _cx = SHELF_X + SHELF_SLOT_W * _c + SHELF_PAD_X + SHELF_CARD_W // 2
    _bottom = SHELF_Y + SHELF_SLOT_H * _r + SHELF_PAD_Y + SHELF_CARD_H
    SHELF_SLOTS[_pos] = (_cx, _bottom - SHELF_LIFT_H // 2, SHELF_LIFT_W, SHELF_LIFT_H)
