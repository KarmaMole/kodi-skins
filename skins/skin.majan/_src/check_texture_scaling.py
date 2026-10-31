"""Verify skin.majan textures as Kodi will actually draw them (1080p and 2160p GUI).

Kodi samples GUI textures with GL_LINEAR and no mipmaps (xbmc/guilib/TextureGL.cpp:
only textures flagged with SetMipmapping get mipmaps, skin media does not). This
script reproduces that sampler with numpy, so you can see whether an icon or mask
stays clean at its on-screen size.

  * Opens and fully decodes every PNG under media/ (fails loudly on a bad file).
  * Renders each icon / marker / rounded mask at its 1080 draw size (D) and at
    2D (GUI rendered at 2160p), compares with an ideal anti-aliased rendering,
    and prints the mean alpha error (0 = identical, < ~4 is visually clean).
  * Writes previews/scaling_sheet.png: per texture, BASELINE vs CURRENT at D
    (1080p) and at 2D (2160p), drawn accent-on-black, 3x nearest-neighbour
    magnified so the pixels are inspectable.

Usage:
  python skins/skin.majan/_src/check_texture_scaling.py [--baseline DIR]
    --baseline  a copy of an older media/ folder to compare against (optional)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent / "media"
sys.path.insert(0, str(HERE))
import make_textures as mt  # noqa: E402

# On-screen sizes in the 1920x1080 skin space (keep in sync with ICON_PX comments).
DRAW = {
    "icons/chevron_right.png": [24], "icons/chevron_down.png": [24], "icons/back.png": [24],
    "icons/search.png": [26], "icons/settings.png": [26, 56], "icons/play.png": [18, 56],
    **{f"icons/{n}.png": [56] for n in ("pause", "stop", "next", "prev",
                                        "audio", "chapters", "shuffle", "repeat")},
    "markers/check.png": [20, 22, 26], "markers/unwatched.png": [12], "markers/unwatched_round.png": [12],
    "markers/watched.png": [22], "markers/watched_round.png": [22],
    "masks/poster_round8.png": [158], "masks/poster_round8_large.png": [330],
    "masks/poster_round8_xl.png": [520], "masks/square_round8.png": [219],
    "masks/square_round8_large.png": [380], "masks/landscape_round8.png": [320],
    "masks/landscape_round8_large.png": [960],
}


def _axis(src: int, dst: int):
    c = np.clip((np.arange(dst) + 0.5) * src / dst - 0.5, 0, src - 1)
    i0 = np.floor(c).astype(int)
    return i0, np.minimum(i0 + 1, src - 1), c - i0


def kodi_sample(a: np.ndarray, w: int, h: int) -> np.ndarray:
    """GL_LINEAR, no mipmaps: bilinear tap at each destination pixel centre."""
    y0, y1, fy = _axis(a.shape[0], h)
    x0, x1, fx = _axis(a.shape[1], w)
    r = a[y0] * (1 - fy)[:, None] + a[y1] * fy[:, None]
    return r[:, x0] * (1 - fx) + r[:, x1] * fx


def ideal(rel: str, w: int, h: int, k: int) -> np.ndarray | None:
    """Reference rendering drawn directly at the target size (k = GUI scale)."""
    name = Path(rel).stem
    if rel.startswith("icons/"):
        img = mt.draw_icon(mt.ICONS[name], w)
    elif rel == "markers/check.png":
        img = mt.draw_icon(lambda d, s: mt.check_path(d, s, 4, 6, 16, 12, 2.4), w)
    elif rel == "markers/unwatched_round.png":
        return np.asarray(mt.rounded_alpha(w, h, 3 * k), float)
    elif rel.startswith("masks/"):
        return np.asarray(mt.rounded_alpha(w, h, 8 * k), float)  # radius 8 GUI px
    else:
        return None  # solids / baked two-tone: no analytic reference
    return np.asarray(img.getchannel("A"), float)


def alpha(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA").getchannel("A"), float)


def tile(a: np.ndarray, mag: int = 3) -> Image.Image:
    accent = Image.new("RGBA", (a.shape[1], a.shape[0]), (0xFF, 0x5A, 0x1F, 255))
    accent.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    bg = Image.new("RGBA", accent.size, (0x0B, 0x0B, 0x0B, 255))
    bg.alpha_composite(accent)
    return bg.resize((a.shape[1] * mag, a.shape[0] * mag), Image.NEAREST)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path)
    args = ap.parse_args()

    bad = 0
    pngs = sorted(MEDIA.rglob("*.png"))
    for p in pngs:
        try:
            with Image.open(p) as im:
                im.load()
                assert im.mode == "RGBA", f"{im.mode}"
        except Exception as e:  # noqa: BLE001
            bad += 1
            print(f"BAD  {p.relative_to(MEDIA)}: {e}")
    print(f"{len(pngs)} PNGs decoded, {bad} bad")

    rows: list[tuple[str, list[Image.Image]]] = []
    print(f"\n{'texture':34} {'src':>9} {'draw':>9}  err1080  err2160" + ("  | baseline 1080/2160" if args.baseline else ""))
    for rel, sizes in DRAW.items():
        cur = alpha(MEDIA / rel)
        base = alpha(args.baseline / rel) if args.baseline and (args.baseline / rel).exists() else None
        for d in sizes:
            w = d
            h = round(w * cur.shape[0] / cur.shape[1])
            errs, tiles = [], []
            for k in (1, 2):
                ref = ideal(rel, w * k, h * k, k)
                c = kodi_sample(cur, w * k, h * k)
                b = kodi_sample(base, w * k, h * k) if base is not None else None
                if rel.startswith("masks/"):  # corner only (the rest is solid)
                    crop = lambda x: x[:24 * k, :24 * k]  # noqa: E731
                else:
                    crop = lambda x: x  # noqa: E731
                e = lambda x: np.abs(crop(x) - crop(ref)).mean() if ref is not None else float("nan")  # noqa: E731
                errs.append((e(c), e(b) if b is not None else None))
                if b is not None:
                    tiles.append(tile(crop(b)))
                tiles.append(tile(crop(c)))
            line = f"{rel:34} {cur.shape[1]:>4}x{cur.shape[0]:<4} {w:>4}x{h:<4}  {errs[0][0]:7.2f}  {errs[1][0]:7.2f}"
            if base is not None:
                line += f"  | {errs[0][1]:7.2f}  {errs[1][1]:7.2f}"
            print(line)
            rows.append((f"{rel} @{d}", tiles))

    # sheet
    pad, lab = 12, 18
    width = max(sum(t.width for t in ts) + pad * (len(ts) + 1) for _, ts in rows)
    height = sum(max(t.height for t in ts) + lab + pad for _, ts in rows) + pad
    sheet = Image.new("RGBA", (max(width, 600), height), (0x1D, 0x1D, 0x1D, 255))
    dr = ImageDraw.Draw(sheet)
    y = pad
    hdr = "baseline@1080 | current@1080 | baseline@2160 | current@2160" if args.baseline else "@1080 | @2160"
    for name, ts in rows:
        dr.text((pad, y), f"{name}    ({hdr}, 3x zoom; masks: corner only)", fill=(0xA3, 0xA1, 0x9B, 255))
        x = pad
        for t in ts:
            sheet.alpha_composite(t, (x, y + lab))
            x += t.width + pad
        y += max(t.height for t in ts) + lab + pad
    out = HERE / "previews" / "scaling_sheet.png"
    out.parent.mkdir(exist_ok=True)
    sheet.save(out)
    print(f"\nsheet: {out}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
