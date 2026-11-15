#!/usr/bin/env python3
"""소박한 잇프제 카드 생성기 (9:16, 1080x1920 JPEG). 다다언니 data.json 그대로 사용.

사용: python3 isfj_gen.py data.json OUT_DIR
디자인: 진한 테두리 안 밝은 그라데이션 카드, 제목 2줄째·핵심어 형광펜 강조,
왼쪽 색 배지(이모지), 한 줄 건너 베이지 줄무늬, 설명은 태그칩, 오른쪽 아래 @소박한 잇프제.
포인트 컬러는 data["accent_idx"] (isfj_build.py 가 날짜로 정함) 로 ISFJ_PALETTE 에서 고른다.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
NOTO = "/usr/share/fonts/opentype/noto/"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
# (이름, 진한색-배지·숫자·계정명, 형광펜색, 테두리색)
ISFJ_PALETTE = [
    ("오렌지", "#E07A3F", "#F6B98F", "#3F6F62"),
    ("세이지", "#4F8A63", "#B8DCC2", "#35574A"),
    ("블루", "#3F6FB5", "#B3CBEE", "#2F4766"),
    ("머스터드", "#B98A12", "#F2D677", "#5A4A1E"),
    ("로즈", "#C2577A", "#F4B9CB", "#5E3345"),
    ("퍼플", "#7660AE", "#CFC3EE", "#3E3463"),
    ("틸", "#2B8780", "#A6DCD5", "#24504C"),
]
DARK, MID, CHIP_BG, CHIP_FG, STRIPE = "#2B2A28", "#55524C", "#E2E8E4", "#566660", (243, 229, 214)
HANDLE = "@소박한 잇프제"
EF = ImageFont.truetype(EMOJI, 109)
overflow = []


def sans(w, s): return ImageFont.truetype(NOTO + f"NotoSansCJK-{w}.ttc", s, index=1)


def emoji(ch, size):
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=EF, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb); r = size / max(im.size)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


def fit(d, text, w, size, maxw, minsize):
    s = size
    while s > minsize and d.textlength(text, font=sans(w, s)) > maxw:
        s -= 1
    if d.textlength(text, font=sans(w, s)) > maxw:
        overflow.append(text)
    return sans(w, s)


def hl(d, x, y, text, font, color):
    """형광펜: 글자 아래쪽 45% 높이"""
    tw = d.textlength(text, font=font); s = font.size
    d.rectangle([x - 4, y + s * 0.62, x + tw + 4, y + s * 1.18], fill=color)


def center_hl(d, text, y, font, fg, hlc):
    tw = d.textlength(text, font=font); x = (W - tw) / 2
    if hlc:
        hl(d, x, y, text, font, hlc)
    d.text((x, y), text, font=font, fill=fg)


def base(frame):
    img = Image.new("RGB", (W, H), frame)
    card = Image.new("RGB", (W - 56, H - 56))
    top, bot = (236, 241, 239), (248, 242, 233)
    cd = ImageDraw.Draw(card)
    for yy in range(card.height):
        t = yy / card.height
        cd.line([(0, yy), (card.width, yy)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    mask = Image.new("L", card.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width, card.height], radius=28, fill=255)
    img.paste(card, (28, 28), mask)
    return img


def page(data, rows, pno, ptotal, first, last, pal):
    _, DEEP, LIGHT, FRAME = pal
    img = base(FRAME); d = ImageDraw.Draw(img)
    M = 80; n = len(rows)
    vs = bool(data.get("vs")); one = bool(data.get("oneline"))
    note_h = 110 if (last and data.get("note")) else 0
    head = (70 if data.get("tag") else 0) + 210 if first else 120
    head += 80 if vs else 0
    cap = 118 if (one or vs) else 150
    RH = min(cap, (1640 - head - note_h) / max(n, 1))
    block = head + n * RH + note_h
    y = max(110, (1830 - block) / 2)
    if ptotal > 1:
        pf = sans("Regular", 28); t = f"{pno}/{ptotal}"
        d.text((W - 70 - d.textlength(t, font=pf), 60), t, font=pf, fill=MID)
    if first:
        if data.get("tag"):
            tf = sans("Medium", 34); center_hl(d, data["tag"], y, tf, MID, None); y += 70
        f1 = fit(d, data["title1"], "Black", 74, W - 2 * M, 52)
        f2 = fit(d, data["title2"], "Black", 74, W - 2 * M, 52)
        center_hl(d, data["title1"], y, f1, DARK, None)
        center_hl(d, data["title2"], y + 96, f2, DARK, LIGHT)
        y += 210
    else:
        hf = fit(d, data["title1"] + " " + data["title2"], "Black", 46, W - 2 * M, 32)
        center_hl(d, data["title1"] + " " + data["title2"], y, hf, DARK, LIGHT); y += 120
    if vs:
        hw = (W - 2 * M) / 2; pf = sans("Black", 34)
        for i, (lab, bg, fg) in enumerate([("A", "#3A3936", "#FFFFFF"), ("B", DEEP, "#FFFFFF")]):
            cx = M + hw * i + hw / 2
            d.rounded_rectangle([cx - 70, y + 6, cx + 70, y + 58], radius=26, fill=bg)
            d.text((cx - d.textlength(lab, font=pf) / 2, y + 7), lab, font=pf, fill=fg)
        y += 80
    top = y
    bw, bh = 116, int(min(66, RH * 0.56))
    for i, r in enumerate(rows):
        ry = top + i * RH; cy = ry + RH / 2
        if i % 2 == 1:
            d.rounded_rectangle([M - 24, ry + 6, W - M + 24, ry + RH - 6], radius=18, fill=STRIPE)
        if vs:
            halfw = (W - 2 * M) / 2 - 70
            s = int(min(38, RH * 0.36))
            while s > 22 and max(d.textlength(r.get(k, ""), font=sans("Bold", s)) for k in ("a", "b")) > halfw:
                s -= 1
            f = sans("Bold", s)
            for txt, col, x0 in ((r.get("a", ""), DARK, M), (r.get("b", ""), DEEP, W / 2 + 70)):
                d.text((x0 + (halfw - d.textlength(txt, font=f)) / 2, cy - s * 0.72), txt, font=f, fill=col)
            cr = int(min(32, RH * 0.3))
            d.ellipse([W / 2 - cr, cy - cr, W / 2 + cr, cy + cr], fill="#FFFFFF", outline=LIGHT, width=3)
            em = emoji(r.get("e", ""), int(cr * 1.1)) if r.get("e") else None
            if em: img.paste(em, (int(W / 2 - em.width / 2), int(cy - em.height / 2)), em)
            continue
        # 배지
        bx = M; d.rounded_rectangle([bx, cy - bh / 2, bx + bw, cy + bh / 2], radius=bh / 2, fill=DEEP)
        em = emoji(r.get("e", ""), int(bh * 0.7)) if r.get("e") else None
        if em: img.paste(em, (int(bx + bw / 2 - em.width / 2), int(cy - em.height / 2)), em)
        tx = bx + bw + 34; vw = 0
        if r.get("value"):
            vf = fit(d, r["value"], "Black", int(min(48, RH * 0.38)), 300, 26)
            vw = d.textlength(r["value"], font=vf)
            d.text((W - M - vw, cy - vf.size * 0.72), r["value"], font=vf, fill=DEEP); vw += 24
        maxw = W - M - tx - vw
        if one and r.get("sub"):
            s = int(min(36, RH * 0.36))
            while s > 22 and d.textlength(r["label"] + "  ", font=sans("Bold", s)) + d.textlength(r["sub"], font=sans("Regular", s)) > maxw:
                s -= 1
            lf, sf = sans("Bold", s), sans("Regular", s); ly = cy - s * 0.72
            hl(d, tx, ly, r["label"], lf, LIGHT)
            d.text((tx, ly), r["label"], font=lf, fill=DARK)
            d.text((tx + d.textlength(r["label"] + "  ", font=lf), ly), r["sub"], font=sf, fill=MID)
            continue
        lf = fit(d, r["label"], "Bold", int(min(40, RH * 0.3)), maxw, 24)
        if r.get("sub"):
            cf = fit(d, r["sub"], "Medium", int(min(28, RH * 0.21)), maxw - 36, 18)
            chip_h = cf.size * 1.55
            total = lf.size * 1.3 + 12 + chip_h
            ly = cy - total / 2 - lf.size * 0.1
            hl(d, tx, ly, r["label"], lf, LIGHT); d.text((tx, ly), r["label"], font=lf, fill=DARK)
            chy = ly + lf.size * 1.3 + 12; cw = d.textlength(r["sub"], font=cf) + 36
            d.rounded_rectangle([tx, chy, tx + cw, chy + chip_h], radius=chip_h / 2, fill=CHIP_BG)
            d.text((tx + 18, chy + (chip_h - cf.size) / 2 - cf.size * 0.12), r["sub"], font=cf, fill=CHIP_FG)
        else:
            ly = cy - lf.size * 0.72
            hl(d, tx, ly, r["label"], lf, LIGHT); d.text((tx, ly), r["label"], font=lf, fill=DARK)
    if last and data.get("note"):
        nf = fit(d, data["note"], "Bold", 38, W - 2 * M, 24)
        center_hl(d, data["note"], top + n * RH + 46, nf, DARK, LIGHT)
    hf = sans("Bold", 32)
    d.text((W - 80 - d.textlength(HANDLE, font=hf), H - 110), HANDLE, font=hf, fill=DEEP)
    return img


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    pal = ISFJ_PALETTE[int(data.get("accent_idx", 0)) % len(ISFJ_PALETTE)]
    rows = data["rows"]
    per = int(data.get("per_page") or 10)
    chunks = [rows[i:i + per] for i in range(0, len(rows), per)] or [[]]
    os.makedirs(out, exist_ok=True)
    for i, ch in enumerate(chunks, 1):
        page(data, ch, i, len(chunks), i == 1, i == len(chunks), pal).save(os.path.join(out, f"{i:02d}.jpg"), "JPEG", quality=92)
    print(f"pages {len(chunks)}")
    for t in overflow:
        print("OVERFLOW", t)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
