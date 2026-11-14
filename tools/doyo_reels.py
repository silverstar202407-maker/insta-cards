#!/usr/bin/env python3
"""도요명리 오늘의운세 릴스 생성기 (6띠씩 2장, 9:16 + 7초 mp4).
사용:
  python3 doyo_reels.py ilJin YYYY-MM-DD      -> 예: 계사 癸巳 일
  python3 doyo_reels.py data.json OUTDIR      -> OUTDIR/1.jpg 2.jpg 1.mp4 2.mp4
data.json 형식:
{"date":"2026-11-15",
 "sub":"11월 15일 (일) · 기해월 계사일",
 "tags":["물과 나무의 삼합 · 한 줄 설명", "불과 쇠의 삼합 · 한 줄 설명"],
 "rows":{"신":["관계 태그","헤드라인(~16자, ~날이다)","설명 한 줄(~22자)","활용 한 줄(~18자)"], ... 12지지 모두(자축인묘진사오미신유술해)}}
1장 = 신자진·해묘미(신,자,진,해,묘,미), 2장 = 인오술·사유축(인,오,술,사,유,축).
글자가 칸을 넘으면 자동으로 줄이며 'shrink' 로그를 남긴다. 28px 아래로 줄어든 줄은 'OVERFLOW' 로 출력되니 문구를 줄여 다시 실행.
글꼴: 환경변수 FONTDIR (기본 ./node_modules/@fontsource/nanum-myeongjo/files)."""
import html
from playwright.sync_api import sync_playwright
from PIL import Image

import os, sys, json, subprocess, datetime as dt
FD = os.path.abspath(os.environ.get("FONTDIR", "./node_modules/@fontsource/nanum-myeongjo/files"))
FF = "".join(f"@font-face{{font-family:NM;src:url('file://{FD}/nanum-myeongjo-{s}-{w}-normal.woff2');font-weight:{w};}}"
             for s in ("korean", "latin") for w in (400, 700, 800))
ZHI = "자축인묘진사오미신유술해"; HZ = "子丑寅卯辰巳午未申酉戌亥"
DDI = dict(zip(ZHI, ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]))
ENG = dict(zip(ZHI, ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]))
BC = {"자":"#2f5079","해":"#2f5079","축":"#a8853c","진":"#9c7a3c","미":"#a8853c","술":"#8a6a45",
      "인":"#557a4b","묘":"#6a9050","사":"#ad5038","오":"#b0442c","신":"#8a8f96","유":"#777c85"}
RED, NAVY = "#b0402c", "#2e4d78"
e = html.escape

def ystr(z):
    ys = [y for y in range(1956, 2016) if ZHI[(y - 4) % 12] == z]
    return " · ".join(f"{y % 100:02d}" for y in ys) + "년생"

CSS = f"""{FF}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#e9e1d6;font-family:NM,'Noto Serif CJK KR',serif;color:#2b2622;position:relative;overflow:hidden}}
.top{{position:absolute;left:64px;right:64px;top:56px;border-top:3px solid #3a332c;padding-top:20px;display:flex;align-items:baseline;gap:34px;border-bottom:1.5px solid #c9bfb1;padding-bottom:18px}}
.br{{font-weight:800;font-size:34px;letter-spacing:2px;white-space:nowrap}}
.en{{font-family:'FreeSerif',serif;font-style:italic;font-size:24px;overflow:hidden;color:#7a7064;white-space:nowrap;flex:1}}
.no{{font-size:21px;letter-spacing:5px;color:#8a8075;white-space:nowrap}}
.panel{{position:absolute;left:64px;right:64px;top:200px;bottom:150px;background:#f1eade;padding:26px 22px 20px;display:flex;flex-direction:column}}
.sub{{text-align:center;color:{RED};font-weight:700;font-size:40px;letter-spacing:3px}}
.ti{{text-align:center;font-weight:800;font-size:58px;letter-spacing:-1px;margin:6px 0 4px;white-space:nowrap;line-height:1.25}}
.ti span{{color:{RED}}}
.tg{{text-align:center;font-weight:700;font-size:25px;color:#857a6e;margin-bottom:22px}}
.rows{{flex:1;display:flex;flex-direction:column;gap:14px}}
.row{{flex:1;background:#f8f3ea;border-radius:8px;display:flex;align-items:center;padding:0 20px 0 16px;gap:24px}}
.bd{{width:150px;height:186px;border-radius:6px;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;flex:none}}
.bd b{{font-family:'Noto Serif CJK KR',serif;font-weight:700;font-size:84px;line-height:1}}
.bd i{{font-style:normal;font-weight:700;font-size:24px;margin-top:10px;line-height:1}}
.tx{{flex:1;min-width:0}}
.kk{{font-size:24px;font-weight:700;color:#857a6e;white-space:nowrap;line-height:1.45}}
.kk u{{text-decoration:none;color:#2b2622}}
.hd{{color:{RED};font-weight:800;font-size:40px;white-space:nowrap;line-height:1.4}}
.ln{{font-weight:700;font-size:30px;white-space:nowrap;line-height:1.5}}
.us{{display:flex;align-items:center;gap:12px;font-weight:700;font-size:30px;white-space:nowrap;line-height:1.5;margin-top:2px}}
.us em{{font-style:normal;background:{NAVY};color:#fff;font-size:21px;width:64px;height:34px;border-radius:3px;display:flex;align-items:center;justify-content:center;flex:none;line-height:1}}
.cta{{margin-top:14px;text-align:center;font-weight:700;font-size:27px;color:#4a4239}}
.cta span{{color:{RED}}}
.ft{{position:absolute;left:64px;right:64px;bottom:32px;border-top:1.5px solid #c9bfb1;padding-top:16px;display:flex;justify-content:space-between;color:#8a8075;font-size:25px;letter-spacing:3px}}
"""

def page(no, name, tag, rows):
    body = ""
    for z, meta, hd, ln, us in rows:
        body += (f"<div class='row'><div class='bd' style='background:{BC[z]}'><b>{HZ[ZHI.index(z)]}</b><i>{DDI[z]}띠</i></div>"
                 f"<div class='tx'><div class='kk'><u>{ystr(z)}</u> · {e(meta)}</div>"
                 f"<div class='hd'>{e(hd)}</div><div class='ln'>{e(ln)}</div>"
                 f"<div class='us'><em>활용</em><span>{e(us)}</span></div></div></div>")
    hz = ""
    eng = " · ".join(ENG[c] for c in name if c in ENG)
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='top'><div class='br'>도요명리</div><div class='en'>{eng}</div></div>
<div class='panel'><div class='sub'>{e(SUB)}</div>
<div class='ti'>{name.replace('·',' · ')} <span>오늘의 운세</span></div><div class='tg'>{e(tag)}</div>
<div class='rows'>{body}</div>
<div class='cta'>가족·친구 띠도 찾아서 <span>보내 주세요</span></div></div>
<div class='ft'><span>도요명리</span></div>
<script>document.querySelectorAll('.hd,.ln,.us,.kk,.ti').forEach(el=>{{let f=parseFloat(getComputedStyle(el).fontSize);const w=el.parentElement.clientWidth;while(el.scrollWidth>w&&f>16){{f-=1;el.style.fontSize=f+'px';console.log('shrink',el.textContent.slice(0,12),f)}}}});</script>
</body></html>"""


GAN="갑을병정무기경신임계"; HG="甲乙丙丁戊己庚辛壬癸"
def iljin(d):
    i=(dt.date.fromisoformat(d).toordinal()+1721425+49)%60
    return GAN[i%10]+ZHI[i%12], HG[i%10]+HZ[i%12], "월화수목금토일"[dt.date.fromisoformat(d).weekday()]

if __name__=="__main__":
    if sys.argv[1]=="ilJin":
        a,b,w=iljin(sys.argv[2]); print(a,b,w); sys.exit()
    data=json.load(open(sys.argv[1],encoding="utf-8")); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
    SUB=data["sub"]; R=data["rows"]
    G=[("신자진","해묘미","신자진해묘미"),("인오술","사유축","인오술사유축")]
    with sync_playwright() as p:
        b=p.chromium.launch(args=["--no-sandbox"]); pg=b.new_page(viewport={"width":1080,"height":1920})
        logs=[]; pg.on("console", lambda m: logs.append(m.text))
        for i,(a,c,zs) in enumerate(G,1):
            rows=[(z,*R[z]) for z in zs]
            open("/tmp/_dr.html","w",encoding="utf-8").write(page(i,a+"·"+c,data["tags"][i-1],rows))
            logs.clear(); pg.goto("file:///tmp/_dr.html"); pg.wait_for_timeout(500)
            pg.screenshot(path=f"/tmp/_dr{i}.png")
            Image.open(f"/tmp/_dr{i}.png").convert("RGB").save(f"{out}/{i}.jpg",quality=93)
            for l in logs:
                f=float(l.rsplit(" ",1)[-1]) if l.startswith("shrink") else 99
                print(("OVERFLOW " if f<28 else "")+l)
            subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"{out}/{i}.jpg","-f","lavfi","-i","anullsrc=r=44100:cl=stereo",
                "-t","7","-r","30","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-shortest","-movflags","+faststart",f"{out}/{i}.mp4"],check=True)
            print("done",i)
        b.close()
