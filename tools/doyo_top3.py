#!/usr/bin/env python3
"""도요명리 TOP3 릴스 생성기 — 기대되는 띠 / 주의가 필요한 띠 (각 한 장, 9:16 + 7초 mp4).
사용:
  python3 doyo_top3.py ilJin YYYY-MM-DD
  python3 doyo_top3.py data.json OUTDIR   -> OUTDIR/good.jpg good.mp4 bad.jpg bad.mp4
data.json 형식:
{"date":"2026-11-16",
 "sub":"11월 16일 (월) · 기해월 갑오일",
 "good_tag":"갑오일, 천을귀인과 합이 드는 띠",
 "bad_tag":"갑오일, 충·형·원진이 걸리는 띠",
 "good":[{"z":"미","meta":"오미 육합 · 천을귀인","hd":"헤드라인(~16자, ~날이다)","us":"활용 한 줄(~16자)",
          "lines":["생년1 문구(~20자)","생년2","생년3","생년4","생년5"]}, ...정확히 3개, 1위부터],
 "bad":[ 같은 형식 3개, us 는 '주의' 한 줄 ]}
z 는 한글 지지 한 글자(자축인묘진사오미신유술해). lines 는 그 띠의 1956~2015년 생년 5개(오래된 순)에 맞춰 각각 다른 주제로.
글자가 넘치면 자동으로 줄이고 같은 종류의 줄은 모두 같은 크기로 맞춘다. 'OVERFLOW' 가 출력되면 문구를 줄여 다시 실행.
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

WINE = "#7a2e3a"
EXTRA = f"""
.rk{{display:inline-flex;align-items:center;justify-content:center;width:62px;height:34px;border-radius:3px;background:{RED};color:#fff;font-size:22px;font-weight:800;margin-right:12px;vertical-align:3px;line-height:1}}
.bad .rk{{background:{WINE}}}
.bad .us em{{background:{WINE}}}
.yl{{display:flex;align-items:baseline;gap:14px;font-weight:700;font-size:34px;white-space:nowrap;line-height:1.55}}
.yl b{{color:{RED};font-weight:800;flex:none;width:110px}}
.bad .yl b{{color:{WINE}}}
.nm{{font-weight:800;font-size:40px;line-height:1.4;white-space:nowrap}}
.hd{{font-size:46px}}.ln{{font-size:34px}}.us{{font-size:34px}}.kk{{font-size:26px}}.bd{{width:180px;height:220px}}.bd b{{font-size:100px}}.bd i{{font-size:28px}}.tx{{display:flex;flex-direction:column;gap:2px}}.hd{{font-size:48px;line-height:1.3}}.yl{{font-size:35px;line-height:1.4;gap:12px}}.yl b{{width:auto}}.us{{font-size:35px;margin-top:6px}}.us em{{width:76px;height:40px;font-size:24px}}.nm{{font-size:40px}}.rk{{width:70px;height:40px;font-size:25px}}.nm small{{font-size:25px}}.bd{{width:120px;height:170px}}.bd b{{font-size:76px}}.bd i{{font-size:24px}}.row{{padding:0 14px 0 14px;gap:18px}}.panel{{top:150px!important;bottom:110px!important;left:36px!important;right:36px!important;padding:22px 16px 16px!important}}.top,.ft{{left:36px!important;right:36px!important}}.rows{{gap:12px}}.sub{{font-size:42px}}.ti{{font-size:64px;margin:4px 0 2px}}.tg{{font-size:27px;margin-bottom:16px}}.cta{{font-size:30px}}
.nm small{{font-size:23px;color:#857a6e;font-weight:700;margin-left:10px}}
"""


def years(z): return [y for y in range(1956, 2016) if ZHI[(y - 4) % 12] == z]

def card(title, accent, tag, rows_html, eng, bad):
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}{EXTRA}</style></head><body class='{"bad" if bad else ""}'>
<div class='top'><div class='br'>도요명리</div><div class='en'>{eng}</div></div>
<div class='panel'><div class='sub'>{e(SUB)}</div>
<div class='ti'>{e(title)} <span{" style='color:"+WINE+"'" if bad else ""}>{e(accent)}</span></div><div class='tg'>{e(tag)}</div>
<div class='rows'>{rows_html}</div>
<div class='cta'>가족·친구 띠도 찾아서 <span>보내 주세요</span></div></div>
<div class='ft'><span>도요명리</span></div>
<script>document.querySelectorAll('.hd,.ln,.us,.kk,.ti,.yl,.nm').forEach(el=>{{let f=parseFloat(getComputedStyle(el).fontSize);const w=el.parentElement.clientWidth;while(el.scrollWidth>w&&f>16){{f-=1;el.style.fontSize=f+'px';}}}});['.hd','.yl','.ln','.us','.kk'].forEach(c=>{{const els=[...document.querySelectorAll(c)];if(!els.length)return;const m=Math.min(...els.map(x=>parseFloat(getComputedStyle(x).fontSize)));els.forEach(x=>x.style.fontSize=m+'px')}});</script>
</body></html>"""

def badge(z): return f"<div class='bd' style='background:{BC[z]}'><b>{HZ[ZHI.index(z)]}</b><i>{DDI[z]}띠</i></div>"

def top_rows(items, bad):
    h = ""
    for i, (z, meta, hd, ln, us, _) in enumerate(items):
        ys = " · ".join(f"{y%100:02d}" for y in years(z)) + "년생"
        h += (f"<div class='row'>{badge(z)}<div class='tx'><div class='kk'><u>{ys}</u> · {e(meta)}</div>"
              f"<div class='hd'><span class='rk'>{i+1}위</span>{e(hd)}</div><div class='ln'>{e(ln)}</div>"
              f"<div class='us'><em>{'주의' if bad else '활용'}</em><span>{e(us)}</span></div></div></div>")
    return h

def merged_rows(items, bad):
    h = ""
    for i, (z, meta, hd, ln, us, lines) in enumerate(items):
        yl = "".join(f"<div class='yl'><b>{y%100:02d}년생</b><span>{e(t)}</span></div>" for y, t in zip(years(z), lines))
        h += (f"<div class='row'>{badge(z)}<div class='tx'><div class='nm'><span class='rk'>{i+1}위</span>{DDI[z]}띠<small>{e(meta)}</small></div>"
              f"<div class='hd'>{e(hd)}</div>{yl}<div class='us'><em>{'주의' if bad else '활용'}</em><span>{e(us)}</span></div></div></div>")
    return h


GAN="갑을병정무기경신임계"; HG="甲乙丙丁戊己庚辛壬癸"
def iljin(d):
    i=(dt.date.fromisoformat(d).toordinal()+1721425+49)%60
    return GAN[i%10]+ZHI[i%12], HG[i%10]+HZ[i%12], "월화수목금토일"[dt.date.fromisoformat(d).weekday()]

if __name__ == "__main__":
    if sys.argv[1] == "ilJin":
        print(*iljin(sys.argv[2])); sys.exit()
    from playwright.sync_api import sync_playwright
    from PIL import Image
    data = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    SUB = data["sub"]
    conv = lambda L: [(x["z"], x["meta"], x["hd"], "", x["us"], x["lines"]) for x in L]
    G, B = conv(data["good"]), conv(data["bad"])
    cards = [("good", "오늘 기대되는 띠", "TOP 3", data["good_tag"], merged_rows(G, False), G, False),
             ("bad", "오늘 주의가 필요한 띠", "TOP 3", data["bad_tag"], merged_rows(B, True), B, True)]
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"]); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for name, t, a, tag, rows, items, bad in cards:
            eng = " · ".join(ENG[it[0]] for it in items)
            open("/tmp/_dt.html", "w", encoding="utf-8").write(card(t, a, tag, rows, eng, bad))
            pg.goto("file:///tmp/_dt.html"); pg.wait_for_timeout(500)
            mins = pg.evaluate("['.hd','.yl','.us','.nm'].map(c=>{const e=document.querySelector(c);return e?c+' '+parseFloat(e.style.fontSize||getComputedStyle(e).fontSize):''})")
            for s in mins:
                if s and float(s.split()[1]) < 28: print("OVERFLOW", name, s)
            pg.screenshot(path=f"/tmp/_dt_{name}.png")
            Image.open(f"/tmp/_dt_{name}.png").convert("RGB").save(f"{out}/{name}.jpg", quality=93)
            subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"{out}/{name}.jpg","-f","lavfi","-i","anullsrc=r=44100:cl=stereo",
                "-t","7","-r","30","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-shortest","-movflags","+faststart",f"{out}/{name}.mp4"],check=True)
            print("done", name)
        b.close()
