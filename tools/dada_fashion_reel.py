#!/usr/bin/env python3
"""다다언니 패션 릴스: 착장 사진 N장 → 9:16 카드(표지+Look+마무리) + reel.mp4 + cover.jpg

사용: python3 dada_fashion_reel.py FOLDER   (FOLDER/spec.json 필요)
spec.json: {"title1","title2","sub","looks":[{"img","label"}], "cover_img"(선택), "end_sub"}
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
PINK, YELLOW = (252, 221, 226), (255, 214, 0)


def font(size):
    for idx in (1, 0):
        try:
            f = ImageFont.truetype(BOLD, size, index=idx)
            if "KR" in " ".join(f.getname()):
                return f
        except Exception:
            pass
    return ImageFont.truetype(BOLD, size, index=1)


def fill(path):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def shade(im, top=0, bottom=0, strength=150):
    ov = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ov)
    for i in range(top):
        d.line([(0, i), (W, i)], fill=int(strength * (1 - i / top) ** 1.6))
    for i in range(bottom):
        y = H - 1 - i
        d.line([(0, y), (W, y)], fill=int(strength * (1 - i / bottom) ** 1.4))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, im, ov)


def text(im, xy, s, f, color, anchor="la"):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).text(xy, s, font=f, fill=color, anchor=anchor)


def body_info(im):
    f = font(40)
    text(im, (1010, 200), "163cm", f, "white", "ra")
    text(im, (1010, 250), "48kg", f, "white", "ra")


def main(folder):
    sp = json.load(open(os.path.join(folder, "spec.json"), encoding="utf-8"))
    looks = sp["looks"]
    cards = []
    # 표지
    im = shade(fill(os.path.join(folder, sp.get("cover_img", looks[0]["img"]))), top=360, bottom=1000, strength=170)
    text(im, (70, 200), "@다다언니", font(38), "white")
    body_info(im)
    text(im, (70, 1190), sp["title1"], font(96), "white")
    text(im, (70, 1320), sp["title2"], font(96), PINK)
    text(im, (74, 1465), "▶ " + sp["sub"], font(46), "white")
    cards.append(im)
    # Look 카드
    for i, lk in enumerate(looks, 1):
        im = shade(fill(os.path.join(folder, lk["img"])), top=380, bottom=620, strength=150)
        text(im, (70, 180), f"Look.{i}", font(88), "white")
        body_info(im)
        text(im, (70, 1530), lk["label"], font(48), "white")
        cards.append(im)
    # 마무리
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font(34)
    tw = d.textlength("SAVE & SHARE", font=f)
    d.rounded_rectangle([(W - tw) / 2 - 30, 700, (W + tw) / 2 + 30, 762], 31, outline=YELLOW, width=3)
    d.text((W / 2, 731), "SAVE & SHARE", font=f, fill=YELLOW, anchor="mm")
    d.text((W / 2, 870), "카드 속 착장 정보는", font=font(78), fill="white", anchor="mm")
    d.text((W / 2, 980), "프로필 링크에서 확인!", font=font(78), fill=YELLOW, anchor="mm")
    d.text((W / 2, 1090), sp.get("end_sub", "저장해두고 꺼내 보세요"), font=font(40), fill=(190, 190, 190), anchor="mm")
    d.text((W / 2, 1480), "더 많은 데일리룩은 @다다언니", font=font(38), fill=YELLOW, anchor="mm")
    cards.append(im)

    frames = []
    for i, c in enumerate(cards, 1):
        p = os.path.join(folder, f"{i:02d}.jpg")
        c.save(p, "JPEG", quality=92)
        frames.append(p)
    cards[0].save(os.path.join(folder, "cover.jpg"), "JPEG", quality=92)

    durs = [2.5] + [3.0] * len(looks) + [3.0]
    fd = 0.4
    n = len(frames)
    total = sum(durs) - fd * (n - 1)
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for f, dur in zip(frames, durs):
        args += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", f]
    args += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
    fc, last, off = "", "0:v", 0.0
    for i in range(1, n):
        off += durs[i - 1] - fd
        fc += f"[{last}][{i}:v]xfade=transition=fade:duration={fd}:offset={off:.2f}[x{i}];"
        last = f"x{i}"
    fc += f"[{last}]format=yuv420p,fps=30[v]"
    args += ["-filter_complex", fc, "-map", "[v]", "-map", f"{n}:a", "-c:v", "libx264", "-preset", "medium",
             "-crf", "19", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest",
             os.path.join(folder, "reel.mp4")]
    subprocess.run(args, check=True)
    print("ok", total)


if __name__ == "__main__":
    main(sys.argv[1])
