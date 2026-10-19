"""icon.png (512) and fanart.jpg (1920x1080) for skin.nocturne, built from the skin's own textures.
    python skins/skin.nocturne/_src/make_addon_art.py
A dark plaster wall, one empty gilt frame in a pool of torchlight, dust, and a brass plaque engraved "Nocturne".
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "media" / "noc"
F = ROOT / "fonts"


def nine(img, w, h, b):
    """Minimal 9-slice stretch (border b on all sides)."""
    W, H = img.size
    out = Image.new("RGBA", (w, h))
    xs = [(0, b, 0, b), (b, W - b, b, w - b), (W - b, W, w - b, w)]
    ys = [(0, b, 0, b), (b, H - b, b, h - b), (H - b, H, h - b, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if dx1 > dx0 and dy1 > dy0:
                out.paste(img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS), (dx0, dy0))
    return out


def scene(w, h, frame_box, pool_c, plaque_y, scale=1.0):
    wall = Image.open(M / "plaster.jpg").convert("RGBA").resize((w, h), Image.LANCZOS)
    fx, fy, fw, fh = frame_box
    sh = nine(Image.open(M / "shadow.png").convert("RGBA"), fw + 128, fh + 128, 64)
    wall.alpha_composite(sh, (fx - 64, fy - 64))
    inner = Image.new("RGBA", (fw, fh), (26, 24, 28, 255))
    # a faint painted night inside the frame: a moon over a hill
    d = ImageDraw.Draw(inner)
    d.ellipse([fw * 0.58, fh * 0.16, fw * 0.82, fh * 0.16 + fw * 0.24], fill=(228, 214, 186, 255))
    d.polygon([(0, fh * 0.78), (fw * 0.35, fh * 0.62), (fw * 0.7, fh * 0.74), (fw, fh * 0.66), (fw, fh), (0, fh)], fill=(52, 44, 40, 255))
    wall.alpha_composite(inner, (fx, fy))
    fr = nine(Image.open(M / "frame.png").convert("RGBA"), fw + 32, fh + 32, 16)
    wall.alpha_composite(fr, (fx - 16, fy - 16))
    sw, shh = int(3840 * scale), int(3840 * scale)
    shroud = Image.open(M / "shroud_gallery.png").convert("RGBA").resize((sw, shh), Image.LANCZOS)
    wall.alpha_composite(shroud, (int(pool_c[0] - sw / 2), int(pool_c[1] - shh / 2)))
    dust = Image.open(M / "dust.png").convert("RGBA")
    ds = int(760 * scale)
    wall.alpha_composite(dust.resize((ds, ds), Image.LANCZOS), (int(pool_c[0] - ds / 2), int(pool_c[1] - ds / 2 - 40 * scale)))
    # plaque
    pw, ph = int(380 * scale), int(64 * scale)
    pl = nine(Image.open(M / "plaque.png").convert("RGBA"), pw, ph, int(26))
    px = pool_c[0] - pw // 2
    wall.alpha_composite(pl, (px, plaque_y))
    font = ImageFont.truetype(str(F / "NocturneSerif-SemiBoldItalic.ttf"), int(40 * scale))
    d = ImageDraw.Draw(wall)
    t = "Nocturne"
    tw = d.textlength(t, font=font)
    ty = plaque_y + ph / 2 - 24 * scale
    d.text((pool_c[0] - tw / 2 + 1, ty + 1), t, font=font, fill=(255, 238, 200, 140))
    d.text((pool_c[0] - tw / 2, ty), t, font=font, fill=(43, 29, 12, 255))
    return wall


def main():
    fan = scene(1920, 1080, (782, 230, 356, 528), (960, 520), 826)
    fan.convert("RGB").save(ROOT / "fanart.jpg", quality=90)
    icon = scene(1024, 1024, (362, 190, 300, 444), (512, 470), 690, scale=0.85)
    icon = icon.resize((512, 512), Image.LANCZOS)
    icon.save(ROOT / "icon.png", optimize=True)
    print("icon.png fanart.jpg")


if __name__ == "__main__":
    main()
