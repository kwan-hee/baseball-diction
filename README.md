# 야구사전 (baseball-diction)

야구 용어·규칙을 3~5분 롱폼 영상으로 만드는 콘텐츠 파이프라인.

## 구조

- `skills/baseball-dictionary/SKILL.md` — Claude Code `/야구사전` 스킬 (리서치 + 말리 대본 + SEO 생성)
- `content/` — 생성된 콘텐츠 문서 (리서치·대본·SEO, Obsidian vault 사본)
- `output/{날짜}_{용어}/` — 영상 에셋
  - `make_narration.py` — edge-tts 내레이션 생성 (ko-KR-InJoonNeural)
  - `compose.py` — ffmpeg 조립 (Ken Burns + seedance 클립 + 자막 burn-in)
  - `images/` 삽화, `audio/` 내레이션, `clips/` seedance 클립, `*.srt` 자막, 썸네일
  - 최종 mp4·BGM 음원은 용량/저작권 문제로 리포에서 제외

## 파이프라인

1. `/야구사전 {용어}` → 리서치 + 말리 페르소나 대본 + SEO 패키지 (Obsidian 저장)
2. 장면 분할 + 점수판(emotion/motion/importance)으로 엔진 결정
   — motion 7~10 & importance 85+ 장면만 seedance, 나머지 정지 삽화 + Ken Burns
3. nano_banana_2 삽화 + edge-tts 내레이션 + ffmpeg 조립 + BGM 믹싱
