# 오싹한 새싹 (인스타 ossac_saessac, account id 17841437219154272)

괴이록(goeirok_archive)과 같은 공포 단편 카드뉴스 형식·디자인이지만 **괴이록과 다른 이야기만** 올린다(사용자 결정, 2026-11-21). 빨간 글씨는 채도를 높인 vivid.
게시 시각: 매일 04·13·19시(한국시간), 하루 3개.

- 소재·작성 지침·쓰지 않는 소재·캡션 형식·해시태그는 goeirok/README.md 와 같다.
- 소재 중복 방지: goeirok/used.txt 를 두 계정이 같이 쓴다(새 글을 쓰면 반드시 한 줄 추가, 오싹한 새싹 글은 끝에 "— 오싹한 새싹" 표시). goeirok/stories/*.json, ossac/stories/*.json 어느 것과도 소재·결말 패턴이 겹치지 않게.
- 원고: ossac/stories/{slug}.json (형식은 tools/goeirok_render.py docstring). slug 는 goeirok/stories, ossac/stories 어디와도 겹치지 않게.
- 이미지: python3 tools/goeirok_render.py ossac/stories/{slug}.json ossac/posts/{slug} vivid → 01~0N.jpg, caption.txt
- posted.txt: "{날짜} {시} {slug} {제목}" 게시 기록.
- 예전 기록: 2026-11-21 22시 관리비(gwanribi)는 괴이록 글을 그대로 올린 것(방침 바뀌기 전).

## 릴스 (하루 3개: 08·16·23시, 사용자 결정 2026-11-24)
- 괴이록 릴스와 같은 양식: 정지 이미지 한 장(제목 + 도입부 teaser + "뒷이야기는 프로필에서 / @ossac_saessac"), 3초, 낮은 웅웅 소리. 빨강은 vivid.
- 고르는 법: ossac/posted.txt 에서 가장 최근에 올린 글 중 ossac/reels_posted.txt 에 아직 없는 slug.
- 만들기: 원고가 goeirok/stories/{slug}.json 이면 → python3 tools/goeirok_reel.py goeirok/stories/{slug}.json goeirok/posts/{slug}/ossac ossac
          원고가 ossac/stories/{slug}.json 이면 → python3 tools/goeirok_reel.py ossac/stories/{slug}.json ossac/posts/{slug} ossac
  (reel.mp4, reel_cover.jpg, reel_caption.txt 생성. 원고에 "teaser" 가 없으면 먼저 써 넣는다)
- reels_posted.txt: "{날짜} {시} {slug} {제목}" 릴스 게시 기록.
