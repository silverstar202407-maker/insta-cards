#!/usr/bin/env python3
"""다다언니 생활정보 카드 생성기 (4:5, 1080x1350 JPEG).

사용: python3 dada_gen.py data.json OUT_DIR
출력: OUT_DIR/01.jpg, 02.jpg ... (내용이 길면 자동으로 다음 장으로 넘김)
OVERFLOW 로 시작하는 줄이 출력되면 그 문구를 줄여 다시 실행할 것.

다다언니 디자인: 검은 배경, 흰 글씨, 중요한 것(제목 2줄째·숫자·핵심 문구)은 노란색,
전체 명조체(Noto Serif CJK KR), 하단 '더 많은 정보는 @다다언니'만 작은 돋움체.
항목마다 이모지(어두운 원 안), 줄 간격 촘촘, 표 형식, 얇은 구분선.

data.json 형식:
{
  "tag": "생활 필수 번호",            # 상단 노란 테두리 태그(짧게, 선택)
  "title1": "일단 저장해둬라.",        # 흰색 제목 1줄 (14자 이내 권장)
  "title2": "살면서 무조건 한번은 쓴다.", # 노란색 제목 2줄 (14자 이내 권장)
  "rows": [                            # 항목 (3~20개)
    {"e": "🏥", "label": "돈 없을 때 응급실", "sub": "국가가 먼저 냄", "value": "129"},
    ...
  ],
  "sub_color": "gray" | "yellow",     # sub 문구 색 (value 없을 때는 yellow 권장)
  "per_page": 7,                       # 1장에 들어갈 항목 수(선택, 기본: 자동)
  "note": "요즘 늘어나는 수법이니 꼭 조심하세요!"  # 마지막 장 하단 한 줄(선택)
}
- label: 18자 이내, sub: 26자 이내, value: 12자 이내(숫자·금액·번호 등 핵심값, 없으면 생략)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 70
NOTO = "/usr/share/fonts/opentype/noto/"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BG, WHITE, YEL, GRAY, LINE, CIRCLE = "#0a0a0a", "#ffffff", "#ffd400", "#8c8c8c", "#262626", "#1c1c1c"


def _noto_serif(w, s): return ImageFont.truetype(NOTO + f"NotoSerifCJK-{w}.ttc", s, index=1)
serif = _noto_serif
HANDLE = "@다다언니"
PILL_A = ("#2a2a2a", "#ffffff"); PILL_B_FG = "#1a1400"
FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


ISFJ_ACCENTS = ["#5E7D4E", "#B0603A", "#4F6D8A", "#8A5A78", "#8E6B1F", "#3F7E78", "#9A4E4E"]  # 세이지·테라코타·더스티블루·모브·머스터드·틸·로즈브라운


def apply_theme(name, accent=None):
    """theme: "dada"(기본, 검정·노랑·명조) / "isfj"(소박한 잇프제: 크림·갈색·세이지, 고운바탕 제목 + 고딕 본문)"""
    global BG, WHITE, YEL, GRAY, LINE, CIRCLE, serif, HANDLE, PILL_A, PILL_B_FG
    if name == "isfj":
        BG, WHITE, YEL, GRAY, LINE, CIRCLE = "#F7F2E8", "#3B3128", "#5E7D4E", "#9C9184", "#E3D8C4", "#EDE4D3"
        if accent:
            YEL = accent
        HANDLE = "@소박한 잇프제"; PILL_A = ("#E3D8C4", "#3B3128"); PILL_B_FG = "#F7F2E8"
        title = os.path.join(FONTDIR, "GowunBatang-Bold.ttf")
        m = {"Black": "Bold", "Bold": "Bold", "SemiBold": "Medium", "Medium": "Regular", "Regular": "Regular"}
        def _isfj(w, s):
            if w == "Black":
                return ImageFont.truetype(title, s)
            return ImageFont.truetype(NOTO + f"NotoSansCJK-{m.get(w, w)}.ttc", s, index=1)
        serif = _isfj
def sans(w, s): return ImageFont.truetype(NOTO + f"NotoSansCJK-{w}.ttc", s, index=1)


EF = ImageFont.truetype(EMOJI, 109)
overflow = []


def emoji(ch, size):
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=EF, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb); r = size / max(im.size)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


def center(d, t, y, font, c):
    d.text(((W - d.textlength(t, font=font)) / 2, y), t, font=font, fill=c)


def fit(d, text, font_fn, size, maxw, minsize):
    s = size
    while s > minsize and d.textlength(text, font=font_fn(s)) > maxw:
        s -= 1
    if d.textlength(text, font=font_fn(s)) > maxw:
        overflow.append(text)
    return font_fn(s)


def footer(d):
    ft = sans("Regular", 28); t1, t2 = "더 많은 정보는 ", HANDLE
    sx = (W - d.textlength(t1 + t2, font=ft)) / 2
    d.text((sx, 1262), t1, font=ft, fill=GRAY)
    d.text((sx + d.textlength(t1, font=ft), 1262), t2, font=ft, fill=YEL)


def page(data, rows, pno, ptotal, first, last):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    if ptotal > 1:
        pf = sans("Regular", 26); t = f"{pno}/{ptotal}"
        d.text((W - M - d.textlength(t, font=pf), 40), t, font=pf, fill=GRAY)
    n = len(rows)
    note_h = 70 if (last and data.get("note")) else 0
    vs = bool(data.get("vs"))
    cap = 84 if (data.get("oneline") or vs) else 118
    hdr_vs = 70 if vs else 0
    if first:
        head = (75 if data.get("tag") else 15) + 215 + hdr_vs
        RH = min(cap, (1225 - 70 - head - note_h) / max(n, 1))
        block = head + n * RH + note_h
        y = max(50, (1245 - block) / 2)
        if data.get("tag"):
            tf = serif("SemiBold", 26); tw = d.textlength(data["tag"], font=tf) + 60
            d.rounded_rectangle([(W - tw) / 2, y, (W + tw) / 2, y + 50], radius=25, outline=YEL, width=2)
            center(d, data["tag"], y + 4, tf, YEL); y += 75
        else:
            y += 15
        f1 = fit(d, data["title1"], lambda s: serif("Black", s), 70, W - 2 * M, 52)
        f2 = fit(d, data["title2"], lambda s: serif("Black", s), 70, W - 2 * M, 52)
        center(d, data["title1"], y, f1, WHITE); center(d, data["title2"], y + 92, f2, YEL)
        top = y + 215 + hdr_vs
    else:
        # 2장째부터: 머리글+항목 묶음 전체를 세로 가운데 정렬
        RH = min(cap, (1225 - 160 - hdr_vs - note_h) / max(n, 1))
        block = 90 + hdr_vs + n * RH + note_h
        hy = max(60, (1240 - block) / 2)
        hf = fit(d, data["title1"] + " " + data["title2"], lambda s: serif("Black", s), 44, W - 2 * M - 80, 32)
        center(d, data["title1"] + " " + data["title2"], hy, hf, YEL)
        top = hy + 90 + hdr_vs
    if vs:
        # A | B 머리 칸
        hw = (W - 2 * M) / 2
        pf = serif("Black", 34)
        for i, (lab, col, fg) in enumerate([("A", PILL_A[0], PILL_A[1]), ("B", YEL, PILL_B_FG)]):
            cx = M + hw * i + hw / 2
            d.rounded_rectangle([cx - 70, top - 62, cx + 70, top - 14], radius=24, fill=col)
            d.text((cx - d.textlength(lab, font=pf) / 2, top - 61), lab, font=pf, fill=fg)
        d.line([(W / 2, top - 62), (W / 2, top + n * RH)], fill=LINE, width=2)
    bottom = 1180 if (last and data.get("note")) else 1225
    has_sub = any(r.get("sub") for r in rows)
    big = RH >= 100
    lf_s = int(min(40, RH * 0.37)); sf_s = int(min(30, RH * 0.27)); vf_s = int(min(46, RH * 0.42))
    subc = YEL if data.get("sub_color", "gray") == "yellow" else GRAY
    d.line([(M, top), (W - M, top)], fill=LINE, width=2)
    if data.get("oneline"):
        cr0 = 34 if big else 31
        mw = W - M - (M + 2 * cr0 + 26)
        s1 = int(min(38, RH * 0.42))
        while s1 > 24 and any(d.textlength(r["label"] + "  ", font=serif("Bold", s1)) + d.textlength(r.get("sub", ""), font=serif("SemiBold", s1)) > mw for r in rows):
            s1 -= 1
        data["_s1"] = s1
    if vs:
        cr = int(min(31, RH * 0.38)); halfw = (W - 2 * M) / 2 - cr - 30
        sv = int(min(36, RH * 0.42))
        while sv > 22 and any(d.textlength(r.get(k, ""), font=serif("Bold", sv)) > halfw for r in rows for k in ("a", "b")):
            sv -= 1
        fa, fb = serif("Bold", sv), serif("Bold", sv)
        for i, r in enumerate(rows):
            y = top + i * RH; cy = y + RH / 2
            for txt, f, col, x0 in ((r.get("a", ""), fa, WHITE, M), (r.get("b", ""), fb, YEL, W / 2 + cr + 30)):
                tw = d.textlength(txt, font=f)
                d.text((x0 + (halfw - tw) / 2 + (0 if x0 == M else -0), cy - sv * 0.72), txt, font=f, fill=col)
            d.ellipse([W / 2 - cr, cy - cr, W / 2 + cr, cy + cr], fill=CIRCLE, outline=LINE, width=2)
            if r.get("e"):
                em = emoji(r["e"], int(cr * 1.1))
                if em: img.paste(em, (int(W / 2 - em.width / 2), int(cy - em.height / 2)), em)
            d.line([(M, y + RH), (W - M, y + RH)], fill=LINE, width=2)
        rows = []
    for i, r in enumerate(rows):
        y = top + i * RH; cy = y + RH / 2
        cr = 34 if big else 31
        cx = M + cr
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=CIRCLE)
        if r.get("e"):
            em = emoji(r["e"], int(cr * 1.15))
            if em: img.paste(em, (int(cx - em.width / 2), int(cy - em.height / 2)), em)
        tx = M + 2 * cr + 26
        vw = 0
        if r.get("value"):
            vf = fit(d, r["value"], lambda s: serif("Black", s), vf_s, 360, 28)
            vw = d.textlength(r["value"], font=vf)
            d.text((W - M - vw, cy - vf.size * 0.68), r["value"], font=vf, fill=YEL)
            vw += 24
        maxw = W - M - tx - vw
        if data.get("oneline") and r.get("sub"):
            # 한 줄 배치: 흰 label + 노란/회색 sub
            sep = "  "
            s0 = data["_s1"]
            lf1, sf1 = serif("Bold", s0), serif("SemiBold", s0)
            if d.textlength(r["label"] + sep, font=lf1) + d.textlength(r["sub"], font=sf1) > maxw:
                overflow.append(r["label"] + " " + r["sub"])
            ly = cy - s0 * 0.72
            d.text((tx, ly), r["label"] + sep, font=lf1, fill=WHITE)
            d.text((tx + d.textlength(r["label"] + sep, font=lf1), ly), r["sub"], font=sf1, fill=subc)
            d.line([(M, y + RH), (W - M, y + RH)], fill=LINE, width=2)
            continue
        lf = fit(d, r["label"], lambda s: serif("Bold", s), lf_s, maxw, 26)
        if r.get("sub"):
            sf = fit(d, r["sub"], lambda s: serif("SemiBold", s), sf_s, maxw, 21)
            gap = 8
            hh = lf.size * 1.25 + gap + sf.size * 1.25
            ly = cy - hh / 2 - lf.size * 0.12
            d.text((tx, ly), r["label"], font=lf, fill=WHITE)
            d.text((tx, ly + lf.size * 1.25 + gap), r["sub"], font=sf, fill=subc)
        else:
            d.text((tx, cy - lf.size * 0.72), r["label"], font=lf, fill=WHITE)
        d.line([(M, y + RH), (W - M, y + RH)], fill=LINE, width=2)
    if last and data.get("note"):
        nf = fit(d, data["note"], lambda s: serif("Bold", s), 30, W - 2 * M, 22)
        center(d, data["note"], top + n * RH + 24, nf, WHITE)
    footer(d)
    return img


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    apply_theme(data.get("theme", "dada"), data.get("accent"))
    rows = data["rows"]
    per1 = data.get("per_page") or (9 if len(rows) <= 9 else 7)
    per = 9
    chunks = [rows[:per1]]
    rest = rows[per1:]
    while rest:
        chunks.append(rest[:per]); rest = rest[per:]
    # 마지막 장이 너무 짧으면 고르게 나눔
    if len(chunks) > 1 and len(chunks[-1]) < 3:
        allr = rows; k = len(chunks)
        base = -(-len(allr) // k)
        chunks = [allr[i:i + base] for i in range(0, len(allr), base)]
    os.makedirs(out, exist_ok=True)
    for i, ch in enumerate(chunks, 1):
        img = page(data, ch, i, len(chunks), i == 1, i == len(chunks))
        img.save(os.path.join(out, f"{i:02d}.jpg"), "JPEG", quality=92)
    print(f"pages {len(chunks)}")
    for t in overflow:
        print("OVERFLOW", t)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
