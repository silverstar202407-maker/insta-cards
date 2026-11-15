#!/usr/bin/env python3
"""다다언니 카드(NN.jpg, 4:5) → 릴스 영상(reel.mp4, 9:16 1080x1920) + 커버(cover.jpg).

사용: python3 dada_reel.py FOLDER
- 카드를 검은 9:16 화면 가운데에 놓는다(다다언니 디자인이 검은 배경이라 위아래가 자연스럽게 이어짐).
- 1장이면 8초, 여러 장이면 장당 5초(장 사이 0.5초 페이드).
- H.264 + 무음 AAC 트랙(인스타 업로드 호환).
"""
import glob, os, subprocess, sys
from PIL import Image

W, H = 1080, 1920


def main(folder):
    import json
    theme = "dada"
    try:
        theme = json.load(open(os.path.join(folder, "data.json"), encoding="utf-8")).get("theme", "dada")
    except Exception:
        pass
    bgc = "#F7F2E8" if theme == "isfj" else "#0a0a0a"
    cards = sorted(glob.glob(os.path.join(folder, "[0-9][0-9].jpg")))
    if not cards:
        sys.exit("no NN.jpg in " + folder)
    frames = []
    for i, c in enumerate(cards, 1):
        im = Image.open(c).convert("RGB")
        bg = Image.new("RGB", (W, H), bgc)
        bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
        p = os.path.join(folder, f"_f{i:02d}.png"); bg.save(p); frames.append(p)
        if i == 1:
            bg.save(os.path.join(folder, "cover.jpg"), "JPEG", quality=92)
    n = len(frames)
    dur = 8.0 if n == 1 else 5.0
    out = os.path.join(folder, "reel.mp4")
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for f in frames:
        args += ["-loop", "1", "-t", str(dur), "-i", f]
    args += ["-f", "lavfi", "-t", str(dur * n - 0.5 * (n - 1)), "-i", "anullsrc=r=44100:cl=stereo"]
    if n == 1:
        fc = "[0:v]format=yuv420p,fps=30[v]"
    else:
        fc, last, off = "", "0:v", 0.0
        for i in range(1, n):
            off += dur - 0.5
            fc += f"[{last}][{i}:v]xfade=transition=fade:duration=0.5:offset={off:.2f}[x{i}];"
            last = f"x{i}"
            off_base = off
        fc += f"[{last}]format=yuv420p,fps=30[v]"
    args += ["-filter_complex", fc, "-map", "[v]", "-map", f"{n}:a",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k",
             "-movflags", "+faststart", "-shortest", out]
    subprocess.run(args, check=True)
    for f in frames:
        os.remove(f)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
