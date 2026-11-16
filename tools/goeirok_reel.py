"""괴이록 릴스(9:16) 생성기 — 카드뉴스 원고(story.json)를 그대로 영상으로 만든다.

사용법: python3 tools/goeirok_reel.py goeirok/stories/{slug}.json goeirok/posts/{slug}
  -> reel.mp4 (1080x1920, 30fps, 무음이 아닌 직접 합성한 낮은 앰비언트 소리), reel_cover.jpg, reel_caption.txt
필요: pillow, ffmpeg

릴스는 흥미 유도용 예고편이다(사용자 결정): 결말을 보여주지 않는다.
구성(사용자 결정): 움직이지 않는 정지 이미지 한 장. 그 한 장 안에 송명체 빨강 제목 + story.json 의
      "teaser"(3~5문단, 궁금해서 프로필로 들어올 지점에서 끊음, 마지막 문장 {"s":"R"}) +
      "뒷이야기는 프로필에서 / @goeirok_archive" 를 모두 넣는다. 길이는 3초 고정(사용자는 2초를 원했으나 인스타 최소 3초),
      배경 웅웅 소리 유지.
story.json 에 "teaser" 가 없으면 에러로 끝난다(먼저 teaser 를 써 넣을 것).
디자인: 카드뉴스와 같은 검은 바탕, 본문 Noto Sans KR 흰 글씨, 강조 B=굵게, R=빨강.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "goeirok", "fonts")
W, H = 1080, 1920
WHITE, GREY, RED, BG = (232, 230, 226), (120, 118, 115), (176, 28, 28), (8, 8, 8)
COVER_RED = (178, 0, 0)
MAXW = W - 200
TAGS = "#괴담 #공포 #무서운이야기 #공포썰 #실화"

def sans(size, weight):
    f = ImageFont.truetype(os.path.join(FD, "NotoSansKR.ttf"), size)
    f.set_variation_by_axes([weight]); return f

BODY, BOLD, SMALL = sans(44, 400), sans(45, 700), sans(30, 400)
SONG = lambda s: ImageFont.truetype(os.path.join(FD, "SongMyung-Regular.ttf"), s)

def wrap(d, text, font):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= MAXW: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def base(title):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((100, 150), "괴이록", font=SMALL, fill=GREY)
    d.text((W - 100, 150), title, font=SMALL, fill=GREY, anchor="ra")
    d.line((100, H - 230, 190, H - 230), fill=RED, width=3)
    return img, d

def cover_img(lines):
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    size = 300
    while True:
        F = SONG(size)
        if max(d.textlength(l, font=F) for l in lines) <= W - 200: break
        size -= 4
    LH = int(size * 0.92); y0 = (H - LH * len(lines)) / 2 + LH / 2
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + i * LH), l, font=F, fill=COVER_RED, anchor="mm")
    return img

def end_img():
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    d.text((W / 2, H / 2 - 90), "괴이록", font=SONG(170), fill=COVER_RED, anchor="mm")
    d.text((W / 2, H / 2 + 70), "뒷이야기는 프로필에서", font=sans(40, 700), fill=WHITE, anchor="mm")
    d.text((W / 2, H / 2 + 135), "@goeirok_archive", font=SMALL, fill=GREY, anchor="mm")
    return img

def page_frames(title, paras):
    """문단이 하나씩 누적되는 장면들: [(img, 머무를 초)]"""
    tmp = Image.new("RGB", (10, 10)); d0 = ImageDraw.Draw(tmp)
    blocks = []
    for p in paras:
        if isinstance(p, dict):
            blocks.append((wrap(d0, p["t"], BOLD), RED if p.get("s") == "R" else WHITE, BOLD, p["t"]))
        else:
            blocks.append((wrap(d0, p, BODY), WHITE, BODY, p))
    LH, GAP = 72, 42
    th = sum(len(l) * LH for l, *_ in blocks) + GAP * (len(blocks) - 1)
    if th > H - 600:
        print(f"OVERFLOW {title} ({th}px)"); sys.exit(2)
    y0 = (H - th) / 2
    out = []
    for k in range(1, len(blocks) + 1):
        img, d = base(title); y = y0
        for lines, color, font, _ in blocks[:k]:
            for ln in lines: d.text((100, y), ln, font=font, fill=color); y += LH
            y += GAP
        n = len(blocks[k - 1][3].replace(" ", ""))
        out.append((img, max(2.2, n * 0.075)))
    return out

def still_img(s):
    """한 장 안에 제목 + 예고 본문 + 프로필 유도 문구를 모두 넣은 정지 화면"""
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.text((100, 150), "괴이록", font=SMALL, fill=GREY)
    d.line((100, H - 230, 190, H - 230), fill=RED, width=3)
    size = 150
    while d.textlength(s["title"], font=SONG(size)) > W - 200: size -= 4
    blocks = []
    for p in s["teaser"]:
        if isinstance(p, dict):
            blocks.append((wrap(d, p["t"], BOLD), RED if p.get("s") == "R" else WHITE, BOLD))
        else:
            blocks.append((wrap(d, p, BODY), WHITE, BODY))
    LH, GAP = 70, 38
    body_h = sum(len(l) * LH for l, _, _ in blocks) + GAP * (len(blocks) - 1)
    total_h = size + 90 + body_h + 110 + 50 + 50
    if total_h > H - 520:
        print(f"OVERFLOW teaser ({total_h}px)"); sys.exit(2)
    y = (H - total_h) / 2 + 20
    d.text((100, y), s["title"], font=SONG(size), fill=COVER_RED); y += size + 90
    for lines, color, font in blocks:
        for ln in lines: d.text((100, y), ln, font=font, fill=color); y += LH
        y += GAP
    y += 110 - GAP
    d.text((100, y), "뒷이야기는 프로필에서", font=sans(42, 700), fill=WHITE); y += 62
    d.text((100, y), "@goeirok_archive", font=SMALL, fill=GREY)
    return img

def main(src, out):
    s = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    if "teaser" not in s:
        print("NO_TEASER"); sys.exit(3)
    img = still_img(s)
    chars = sum(len((p["t"] if isinstance(p, dict) else p).replace(" ", "")) for p in s["teaser"])
    total = 3.0  # 사용자 요청은 2초였으나 인스타 API 최소 길이가 3초라 3초로 고정
    tmpd = tempfile.mkdtemp(); still = os.path.join(tmpd, "still.png"); img.save(still)
    video = os.path.join(out, "reel.mp4")
    audio = (f"anoisesrc=color=brown:amplitude=0.25:d={total:.2f},lowpass=f=300,"
             f"volume=0.35,afade=t=in:d=0.3,afade=t=out:st={max(total-0.6,0):.2f}:d=0.6[n];"
             f"sine=f=55:d={total:.2f},volume=0.12[s];[n][s]amix=inputs=2:normalize=0[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", still,
           "-filter_complex", audio, "-map", "0:v", "-map", "[a]",
           "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "20",
           "-c:a", "aac", "-b:a", "128k", "-t", f"{total:.2f}", "-movflags", "+faststart", video]
    subprocess.run(cmd, check=True)
    img.save(os.path.join(out, "reel_cover.jpg"), quality=92)
    cap = s["caption"].strip().split("\n")
    try:
        end = cap.index("", 2); hook = cap[2:end]
    except ValueError:
        hook = cap[2:3]
    reel_cap = "\n".join([f"「{s['title']}」", "", *hook, "",
                          "🕯 이 이야기의 결말은 프로필 피드에 있습니다.",
                          "👉 @goeirok_archive",
                          "💬 당신이 겪은 기이한 일도 댓글로 들려주세요.", "", TAGS])
    open(os.path.join(out, "reel_caption.txt"), "w", encoding="utf-8").write(reel_cap + "\n")
    print("ok", f"{total}s")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
