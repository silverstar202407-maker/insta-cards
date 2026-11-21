"""괴이록(goeirok_archive) 공포 카드뉴스 생성기.

사용법: python3 tools/goeirok_render.py story.json OUTDIR [vivid]
  vivid: 오싹한 새싹(ossac_saessac)용. 빨간 글씨 채도만 높임(본문 R·선 #D21414, 표지 #D60000), 나머지 디자인 동일.
  -> OUTDIR/01.jpg(표지) ~ 0N.jpg(본문), OUTDIR/caption.txt

story.json 형식:
{
  "slug": "jeosuji",                 # 영문 소문자 폴더명
  "title": "저수지",                  # 본문 좌상단 작은 제목
  "cover": ["물에 빠져", "죽었어야 할", "사주라고 했다"],   # 표지 후킹 문구 3~4줄(제목 그대로 쓰지 말 것)
  "pages": [                          # 본문 4장 권장(표지 포함 5장)
    ["문단 텍스트", {"t": "강조 문장", "s": "B"}, {"t": "빨간 강조", "s": "R"}],
    ...
  ],
  "caption": "인스타 본문"
}
고정 디자인: 4:5(1080x1350) 검은 바탕. 표지 송명체 빨강(#B20000) 가운데 큰 글씨, 줄 간격 좁게.
본문 본고딕(Noto Sans KR) 31px 흰 글씨, 문단 묶음, 결정적 문장만 따로 떼어 굵게(B)/빨강(R),
상단 좌측 회색 제목·우측 페이지 번호, 하단 좌측 짧은 빨간 선.
본문 한 장이 넘치면 'OVERFLOW 페이지N' 을 출력하고 종료코드 2.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "goeirok", "fonts")
W, H = 1080, 1350
WHITE, GREY, RED, BG = (232, 230, 226), (120, 118, 115), (176, 28, 28), (8, 8, 8)
COVER_RED = (178, 0, 0)
MAXW = W - 220

def sans(size, weight):
    f = ImageFont.truetype(os.path.join(FD, "NotoSansKR.ttf"), size)
    f.set_variation_by_axes([weight]); return f

BODY, BOLD, SMALL = sans(31, 400), sans(32, 700), sans(26, 400)

def wrap(d, text, font):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= MAXW: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def cover(lines, path):
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    size = 300
    while True:
        F = ImageFont.truetype(os.path.join(FD, "SongMyung-Regular.ttf"), size)
        if max(d.textlength(l, font=F) for l in lines) <= W - 200: break
        size -= 4
    LH = int(size * 0.92); y0 = (H - LH * len(lines)) / 2 + LH / 2
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + i * LH), l, font=F, fill=COVER_RED, anchor="mm")
    img.save(path, quality=92)

def body(title, paras, n, total, path):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((110, 90), title, font=SMALL, fill=GREY)
    d.text((W - 110, 90), f"{n:02d} / {total:02d}", font=SMALL, fill=GREY, anchor="ra")
    d.line((110, H - 110, 200, H - 110), fill=RED, width=3)
    blocks = []
    for p in paras:
        if isinstance(p, dict):
            color = RED if p.get("s") == "R" else WHITE
            blocks.append((wrap(d, p["t"], BOLD), color, BOLD))
        else:
            blocks.append((wrap(d, p, BODY), WHITE, BODY))
    LH, GAP = 52, 30
    th = sum(len(l) * LH for l, _, _ in blocks) + GAP * (len(blocks) - 1)
    if th > H - 360:
        print(f"OVERFLOW 페이지{n} ({th}px)"); sys.exit(2)
    y = (H - th) / 2
    for lines, color, font in blocks:
        for ln in lines: d.text((110, y), ln, font=font, fill=color); y += LH
        y += GAP
    img.save(path, quality=92)

def main(src, out):
    global RED, COVER_RED
    if len(sys.argv) > 3 and sys.argv[3] == "vivid":
        RED, COVER_RED = (210, 20, 20), (214, 0, 0)
    s = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    total = len(s["pages"]) + 1
    cover(s["cover"], os.path.join(out, "01.jpg"))
    for i, pg in enumerate(s["pages"], start=2):
        body(s["title"], pg, i, total, os.path.join(out, f"{i:02d}.jpg"))
    open(os.path.join(out, "caption.txt"), "w", encoding="utf-8").write(s["caption"].strip() + "\n")
    print("ok", total)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
