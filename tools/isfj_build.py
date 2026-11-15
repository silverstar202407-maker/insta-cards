#!/usr/bin/env python3
"""다다언니 게시물 → 소박한 잇프제(less_but_isfj) 버전 생성.
사용: python3 isfj_build.py D H_isfj   (예: 2026-11-15 12)
시각 대응: 잇프제 6←다다 7, 12←13, 14←16, 15←20, 17←24 (같은 날짜)
포인트 컬러는 날짜마다 ISFJ_ACCENTS 순서로 바뀐다.
출력: isfj/{D}_{H}/ (data.json, caption.txt, NN.jpg, reel.mp4, cover.jpg)
"""
import datetime as dt, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = {6: 7, 12: 13, 14: 16, 15: 20, 17: 24}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dada_gen import ISFJ_ACCENTS

def main(D, H):
    H = int(H); src = os.path.join(ROOT, "dada", f"{D}_{MAP[H]}"); out = os.path.join(ROOT, "isfj", f"{D}_{H}")
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
    subprocess.run([sys.executable, os.path.join(t, "dada_reel.py"), out], check=True)
    print(out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
