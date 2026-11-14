#!/usr/bin/env python3
"""능파명리 카드를 도요명리 버전으로: 상단 라벨 글자 교체 + 브랜드 강조색 색상 회전."""
import sys, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/tmp/nm800.ttf"

def find_text(a, box, th=90):
    x0, y0, x1, y1 = box
    r = a[y0:y1, x0:x1].astype(int)
    bg = np.median(np.concatenate([r[:, :6].reshape(-1, 3), r[:, -6:].reshape(-1, 3)]), 0)
    d = np.abs(r - bg).sum(2)
    ys, xs = np.where(d > th)
    if not len(ys):
        return None
    col = np.median(r[d > 200].reshape(-1, 3), 0) if (d > 200).sum() > 20 else np.median(r[d > th], 0)
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1), tuple(int(c) for c in bg), tuple(int(c) for c in col)

def replace_label(im, box, text="도요명리"):
    a = np.asarray(im.convert("RGB"))
    found = find_text(a, box)
    if not found:
        return im, None
    (bx0, by0, bx1, by1), bg, col = found
    d = ImageDraw.Draw(im)
    d.rectangle([bx0 - 3, by0 - 3, bx1 + 3, by1 + 3], fill=bg)
    h = by1 - by0
    font = ImageFont.truetype(FONT, int(h * 1.12))
    ws = [d.textbbox((0, 0), ch, font=font) for ch in text]
    gw = sum(w[2] - w[0] for w in ws)
    sp = max(0, ((bx1 - bx0) - gw) / (len(text) - 1))
    x = bx0
    for ch, w in zip(text, ws):
        top = d.textbbox((0, 0), "도", font=font)[1]
        d.text((x - w[0], by0 - top), ch, font=font, fill=col)
        x += (w[2] - w[0]) + sp
    return im, col

def shift_accent(im, accent_rgb, deg, tol=14, smin=0.12):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    import matplotlib.colors as mc
    hsv = mc.rgb_to_hsv(a)
    ah = colorsys.rgb_to_hsv(*[c / 255 for c in accent_rgb])[0]
    dh = np.abs(((hsv[..., 0] - ah + 0.5) % 1) - 0.5)
    m = (dh < tol / 360) & (hsv[..., 1] > smin) & (hsv[..., 2] < 0.99)
    hsv[..., 0] = np.where(m, (hsv[..., 0] + deg / 360) % 1, hsv[..., 0])
    out = (mc.hsv_to_rgb(hsv) * 255).round().clip(0, 255).astype(np.uint8)
    return Image.fromarray(out)

def run(src, dst, kind, deg):
    im = Image.open(src).convert("RGB")
    box = {"top": (380, 40, 700, 92), "promo": (452, 64, 628, 106), "reel": (400, 330, 680, 392)}[kind]
    im, col = replace_label(im, box)
    if col:
        im = shift_accent(im, col, deg, *((8, 0.03) if kind == "reel" else (14, 0.12)))
    im.save(dst, quality=93)
    return col

if __name__ == "__main__":
    print(run(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])))
