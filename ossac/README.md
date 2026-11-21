# 오싹한 새싹 (인스타 ossac_saessac, account id 17841437219154272)

괴이록(goeirok_archive)과 같은 공포 단편 카드뉴스 형식·디자인이지만 **괴이록과 다른 이야기만** 올린다(사용자 결정, 2026-11-21). 빨간 글씨는 채도를 높인 vivid.
게시 시각: 매일 04·13·19시(한국시간), 하루 3개.

- 소재·작성 지침·쓰지 않는 소재·캡션 형식·해시태그는 goeirok/README.md 와 같다.
- 소재 중복 방지: goeirok/used.txt 를 두 계정이 같이 쓴다(새 글을 쓰면 반드시 한 줄 추가, 오싹한 새싹 글은 끝에 "— 오싹한 새싹" 표시). goeirok/stories/*.json, ossac/stories/*.json 어느 것과도 소재·결말 패턴이 겹치지 않게.
- 원고: ossac/stories/{slug}.json (형식은 tools/goeirok_render.py docstring). slug 는 goeirok/stories, ossac/stories 어디와도 겹치지 않게.
- 이미지: python3 tools/goeirok_render.py ossac/stories/{slug}.json ossac/posts/{slug} vivid → 01~0N.jpg, caption.txt
- posted.txt: "{날짜} {시} {slug} {제목}" 게시 기록.
- 예전 기록: 2026-11-21 22시 관리비(gwanribi)는 괴이록 글을 그대로 올린 것(방침 바뀌기 전).
