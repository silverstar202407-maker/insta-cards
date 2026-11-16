"""괴이록 릴스(9:16) 생성기 — 카드뉴스 원고(story.json)를 그대로 영상으로 만든다.

사용법: python3 tools/goeirok_reel.py goeirok/stories/{slug}.json goeirok/posts/{slug}
  -> reel.mp4 (1080x1920, 30fps, 무음이 아닌 직접 합성한 낮은 앰비언트 소리), reel_cover.jpg, reel_caption.txt
필요: pillow, ffmpeg

구성: 표지(송명체 빨강 후킹 문구, 2.5초) -> 본문 장마다 문단이 하나씩 나타남(글자 수에 비례해 머무름)
      -> 마지막 장면(빨강 반전 문장) 추가로 2.5초 유지 -> 끝 화면(괴이록 / 팔로우 안내, 3초)
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
    d.text((W / 2, H / 2 + 70), "매일 밤, 기이한 기록 한 편", font=SMALL, fill=GREY, anchor="mm")
    d.text((W / 2, H / 2 + 125), "팔로우하고 다음 이야기를 받아보세요", font=SMALL, fill=GREY, anchor="mm")
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

def main(src, out):
    s = json.load(open(src, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    scenes = [(cover_img(s["cover"]), 2.5)]
    for pg in s["pages"]:
        scenes += page_frames(s["title"], pg)
    img, dur = scenes[-1]; scenes[-1] = (img, dur + 2.5)
    scenes.append((end_img(), 3.0))
    total = sum(t for _, t in scenes)
    tmpd = tempfile.mkdtemp()
    lst = []
    for i, (img, t) in enumerate(scenes):
        p = os.path.join(tmpd, f"{i:03d}.png"); img.save(p)
        lst.append(f"file '{p}'\nduration {t:.2f}")
    lst.append(f"file '{os.path.join(tmpd, f'{len(scenes)-1:03d}.png')}'")
    open(os.path.join(tmpd, "list.txt"), "w").write("\n".join(lst) + "\n")
    video = os.path.join(out, "reel.mp4")
    audio = (f"anoisesrc=color=brown:amplitude=0.25:d={total:.2f},lowpass=f=300,"
             f"volume=0.35,afade=t=in:d=2,afade=t=out:st={max(total-3,0):.2f}:d=3[n];"
             f"sine=f=55:d={total:.2f},volume=0.12[s];[n][s]amix=inputs=2:normalize=0[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(tmpd, "list.txt"),
           "-filter_complex", audio, "-map", "0:v", "-map", "[a]",
           "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-b:a", "128k", "-t", f"{total:.2f}", "-movflags", "+faststart", video]
    subprocess.run(cmd, check=True)
    scenes[0][0].save(os.path.join(out, "reel_cover.jpg"), quality=92)
    cap = s["caption"].strip().split("\n")
    try:
        end = cap.index("", 2); hook = cap[2:end]
    except ValueError:
        hook = cap[2:3]
    reel_cap = "\n".join([f"「{s['title']}」", "", *hook, "",
                          "🕯 소리 켜고 끝까지 보세요.",
                          "📖 카드로 천천히 읽고 싶다면 프로필 피드에서.",
                          "💬 당신이 겪은 기이한 일도 댓글로 들려주세요.", "", TAGS])
    open(os.path.join(out, "reel_caption.txt"), "w", encoding="utf-8").write(reel_cap + "\n")
    print("ok", f"{total:.1f}s")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
