#!/usr/bin/env python3
"""다다언니 게시물 → 소박한 잇프제(less_but_isfj) 버전 생성.
사용: python3 isfj_build.py D H_isfj   (예: 2026-11-15 12)
원본 배정: isfj/map.txt (잇프제 날짜 시각 → 다다언니 날짜 시각). 다다언니와 같은 날 같은 글이 되지 않게 무작위로 섞는다.
포인트 컬러는 날짜마다 ISFJ_ACCENTS 순서로 바뀐다.
출력: isfj/{D}_{H}/ (data.json, caption.txt, NN.jpg(9:16), reel.mp4, cover.jpg)
"""
import datetime as dt, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = {6: 7, 12: 13, 14: 16, 15: 20, 17: 24}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dada_gen import ISFJ_ACCENTS

MAPFILE = os.path.join(ROOT, "isfj", "map.txt")


def load_map():
    m = {}
    if os.path.exists(MAPFILE):
        for ln in open(MAPFILE, encoding="utf-8"):
            p = ln.split()
            if len(p) >= 4:
                m[(p[0], int(p[1]))] = (p[2], int(p[3]))
    return m


def pick_source(D, H):
    """잇프제 칸 (D,H)에 올릴 다다언니 원본을 고른다.
    isfj/map.txt 에 있으면 그대로, 없으면 승인된 다다언니 글 중
    아직 잇프제에 배정되지 않았고 날짜가 D 와 다른 것을 무작위로 골라 map.txt 에 기록한다.
    (다다언니와 같은 날 같은 글이 올라가지 않게)"""
    import random
    m = load_map()
    if (D, H) in m:
        return m[(D, H)]
    used = set(m.values())
    appr = [tuple(l.split()[:2]) for l in open(os.path.join(ROOT, "dada", "approved.txt"), encoding="utf-8") if l.strip()]
    cand = [(d, int(h)) for d, h in appr if d >= "2026-11-16" and abs((dt.date.fromisoformat(d) - dt.date.fromisoformat(D)).days) >= 2 and (d, int(h)) not in used
            and os.path.exists(os.path.join(ROOT, "dada", f"{d}_{h}", "data.json"))]
    if not cand:
        return None
    cand.sort()
    c = random.choice(cand[:10])
    with open(MAPFILE, "a", encoding="utf-8") as f:
        f.write(f"{D} {H} {c[0]} {c[1]}\n")
    return c


def main(D, H):
    H = int(H)
    s = pick_source(D, H)
    if s is None:
        print("NO_SOURCE"); sys.exit(2)
    src = os.path.join(ROOT, "dada", f"{s[0]}_{s[1]}"); out = os.path.join(ROOT, "isfj", f"{D}_{H}")
    print("SOURCE", s[0], s[1])
    data = json.load(open(os.path.join(src, "data.json"), encoding="utf-8"))
    data["theme"] = "isfj"
    data["accent"] = ISFJ_ACCENTS[(dt.date.fromisoformat(D) - dt.date(2026, 11, 15)).days % len(ISFJ_ACCENTS)]
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".jpg") or f.endswith(".mp4"):
            os.remove(os.path.join(out, f))
    json.dump(data, open(os.path.join(out, "data.json"), "w"), ensure_ascii=False, indent=1)
    cap = open(os.path.join(src, "caption.txt"), encoding="utf-8").read().replace("@다다언니", "@소박한 잇프제")
    open(os.path.join(out, "caption.txt"), "w").write(cap)
    t = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(t, "dada_gen.py"), os.path.join(out, "data.json"), out], check=True)
    # 9:16(1080x1920)로 위아래 여백을 붙여 저장
    from PIL import Image
    for f in sorted(os.listdir(out)):
        if f[:2].isdigit() and f.endswith(".jpg"):
            p = os.path.join(out, f); im = Image.open(p).convert("RGB")
            if im.size != (1080, 1920):
                bg = Image.new("RGB", (1080, 1920), "#F7F2E8")
                bg.paste(im, (0, (1920 - im.height) // 2)); bg.save(p, "JPEG", quality=92)
    subprocess.run([sys.executable, os.path.join(t, "dada_reel.py"), out], check=True)
    print(out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
