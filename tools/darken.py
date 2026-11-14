#!/usr/bin/env python3
"""능파명리 카드 → 백록사주 다크 버전: 라벨 '백록사주'로 교체 + 검은 배경/흰 글씨(명도 반전, 색상 유지).
사용: python3 darken.py SRC DST KIND   (KIND: top | promo | reel | reel11 | daily | nolabel(라벨 교체 없이 어둡게만))"""
import sys, os
import numpy as np
from PIL import Image
from skimage import color
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rebrand_lib as rb
rb.FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nm800.ttf")
BOX = {"top": (380, 40, 700, 92), "promo": (452, 64, 628, 106), "reel": (400, 330, 680, 392),
       "reel11": (400, 300, 680, 520), "daily": (380, 20, 700, 110), "nolabel": None}
def darken(im):
    a = np.asarray(im.convert("RGB")).astype(np.float64) / 255
    lab = color.rgb2lab(a)
    L = lab[..., 0]; C = np.hypot(lab[..., 1], lab[..., 2])
    w = np.clip((C - 12) / 25, 0, 1)            # 0 = 무채색(배경·글씨), 1 = 유채색(배지·강조)
    Linv = 100 - L
    Lacc = np.where(L < 55, np.clip(L + 30, 0, 82), L)   # 어두운 강조색은 검은 바탕에서 보이게 밝힘
    lab[..., 0] = Linv * (1 - w) + Lacc * w
    lab[..., 0] = np.where(L > 97, 4, lab[..., 0])       # 흰 바탕 → 거의 검정
    out = np.clip(color.lab2rgb(lab), 0, 1)
    return Image.fromarray((out * 255).round().astype(np.uint8))
def run(src, dst, kind):
    im = Image.open(src).convert("RGB")
    box = BOX[kind]
    if kind == "reel11":
        g = np.asarray(im.convert("L")).astype(int)
        rows = np.where((g[60:1000, 300:780] < 200).any(1))[0] + 60
        y0 = y1 = rows[0]
        for r in rows[1:]:
            if r > y1 + 3: break
            y1 = r
        box = (380, int(y0) - 6, 700, int(y1) + 7)
    if kind != "nolabel":
        im, _ = rb.replace_label(im, box, text="백록사주")
    darken(im).save(dst, quality=93)
if __name__ == "__main__":
    run(*sys.argv[1:4])
