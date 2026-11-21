# 오싹한 새싹 (인스타 ossac_saessac, account id 17841437219154272)

괴이록(goeirok_archive)에 올라간 카드뉴스를 같은 디자인으로, 빨간 글씨 채도만 높여(vivid) 올린다. 캡션은 괴이록과 똑같이.

- 이미지: goeirok/posts/{slug}/ossac/01~0N.jpg, caption.txt
  만들기: python3 tools/goeirok_render.py goeirok/stories/{slug}.json goeirok/posts/{slug}/ossac vivid
- posted.txt: "{날짜} {시} {slug} {제목}" 게시 기록. 같은 slug 를 두 번 올리지 않는다.
- 게시 시각(사용자 결정, 2026-11-21):
  - 04·13·19시 = 괴이록 03·12·18시 글을 1시간 뒤에 올림(그 글이 아직 괴이록에 없으면 그 시각은 건너뜀).
  - 10·22시 = 지난 글 채우기: goeirok/posted.txt 순서대로 아직 안 올린 가장 오래된 글. 다 따라잡으면 이 시각은 조용히 건너뜀.
