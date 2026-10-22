"""icon.png (256x256) and fanart.jpg (1920x1080) for skin.keepsake: a print on black album paper, photo corners,
"keepsake" written on it and the orange date stamp. No film art (the add-on art must not carry anyone's posters).
Run: python skins/skin.keepsake/_src/make_addon_art.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SKIN = HERE.parent
MEDIA = SKIN / "media" / "ks"
FONTS = SKIN / "fonts"


def print_card(w, h, b, photo_fill, text, stamp, font_px, stamp_px):
    S = 2
    W, H = (w + 2 * b) * S, (h + 2 * b) * S
    im = Image.new("RGBA", (W, H), (244, 241, 234, 255))
    ph = Image.new("RGB", (w * S, h * S), photo_fill)
    # a soft night-sky gradient photo
    arr = np.asarray(ph, np.float32)
    yy = np.linspace(0, 1, h * S)[:, None, None]
    arr = arr * (0.55 + 0.6 * yy)
    ph = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(ph)
    hand = ImageFont.truetype(str(FONTS / "KeepsakeHand-SemiBold.ttf"), font_px * S)
    tw = d.textlength(text, font=hand)
    d.text(((w * S - tw) / 2, h * S * 0.28), text, font=hand, fill=(242, 239, 232))
    stampf = ImageFont.truetype(str(FONTS / "KeepsakeStamp-Bold.ttf"), stamp_px * S)
    glow = ImageFont.truetype(str(FONTS / "KeepsakeStampGlow2-Bold.ttf"), stamp_px * S)
    sw = d.textlength(stamp, font=stampf)
    x, y = w * S - sw - 14 * S, h * S - stamp_px * 1.6 * S
    layer = Image.new("RGBA", ph.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x, y), stamp, font=glow, fill=(255, 90, 20, 90))
    ImageDraw.Draw(layer).text((x, y), stamp, font=stampf, fill=(255, 106, 31, 245))
    ph = Image.alpha_composite(ph.convert("RGBA"), layer)
    im.paste(ph, (b * S, b * S))
    sheen = Image.open(MEDIA / "sheen.png").convert("RGBA").resize((W, H))
    im = Image.alpha_composite(im, sheen)
    return im.resize((W // S, H // S), Image.LANCZOS)


def corners(card, cs):
    c = Image.open(MEDIA / "corner.png").convert("RGBA").resize((cs, cs), Image.LANCZOS)
    W, H = card.size
    for img, (x, y) in ((c, (-5, -5)), (c.transpose(Image.FLIP_LEFT_RIGHT), (W - cs + 5, -5)),
                        (c.transpose(Image.FLIP_TOP_BOTTOM), (-5, H - cs + 5)),
                        (c.transpose(Image.ROTATE_180), (W - cs + 5, H - cs + 5))):
        card.alpha_composite(img, (max(0, x), max(0, y)))
    return card


def place(bg, card, cx, cy, angle):
    rot = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", rot.size, (0, 0, 0, 0))
    a = rot.split()[3].point(lambda v: int(v * .65)).filter(ImageFilter.GaussianBlur(10))
    sh.putalpha(a)
    bg.alpha_composite(sh, (int(cx - rot.width / 2 + 4), int(cy - rot.height / 2 + 12)))
    bg.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def main():
    page = Image.open(MEDIA / "paper_spread.jpg").convert("RGBA")
    # fanart
    fan = page.copy()
    c1 = corners(print_card(620, 350, 18, (40, 52, 78), "keepsake", "'26~10~19", 120, 30), 52)
    c2 = corners(print_card(360, 230, 14, (74, 52, 40), "", "'25~10~06", 40, 22), 46)
    place(fan, c2, 560, 640, 4)
    place(fan, c1, 1180, 470, -2)
    fan.convert("RGB").save(SKIN / "resources" / "fanart.jpg", quality=90)
    # icon
    icon = page.crop((660, 300, 1260, 900)).resize((256, 256), Image.LANCZOS)
    card = corners(print_card(176, 132, 10, (40, 52, 78), "keepsake", "'26~10~19", 44, 15), 26)
    place(icon, card, 128, 128, -4)
    icon.convert("RGB").save(SKIN / "resources" / "icon.png")
    print("ok")


if __name__ == "__main__":
    main()
