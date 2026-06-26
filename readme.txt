================================================================================
  보험 영업 AI 도우미 (work05) — 사용 설명서
  위치: E:\project\work05
================================================================================

이 폴더는 보험 설계사용 "고객 정보 정리 + AI 상담·제안서 도우미"입니다.
Obsidian(노트 앱) + Claude(AI) + 자동 수집 도구가 함께 들어 있습니다.


--------------------------------------------------------------------------------
1. 뭐가 있는지 (한눈에)
--------------------------------------------------------------------------------

  [Obsidian 볼트 — 메인 작업 공간]
    고객DB\       고객 한 명 = 한 장의 카드 (갱신일, 태그, 가입 내역)
    상품DB\       보험 상품 정보
    상담기록\     상담 녹음 전사·정리
    대시보드.md   갱신 임박·자녀보험 미가입 자동 집계 (Dataview 필요)
    프롬프트.md   Claude에 붙여넣을 프롬프트 모음
    AI작업큐\     AI용 제안서·문자 초안이 저장되는 곳
    index.html    소개 페이지 (브라우저로 열면 됨)

  [자동 수집 도구 — 3가지 방식 중 하나만 쓰면 됨]

    (A) 웹 버전 — Python 없이 OK  ★ 가장 쉬움
        kv-web\start_web.bat
        또는 루트의 KnowledgeVault_실행.bat (EXE 없을 때 웹으로 실행)

    (B) Python CLI — 기능 가장 많음
        knowledge-vault\start.bat

    (C) Portable — Whisper 녹음→글자 변환 포함
        KnowledgeVault_실행.bat  (Python 또는 EXE 자동 선택)

  [소개 영상]
    video\start_video.bat       브라우저 자동 재생 + MP4 생성
    video\promo.html            약 43초 소개 슬라이드

  [AI 아키텍처 데모 — 별도 체험용]
    start_demo.bat              http://localhost:8080


--------------------------------------------------------------------------------
2. 처음 시작 (추천 순서)
--------------------------------------------------------------------------------

  ▶ Step 1. Obsidian 설치 (선택이지만 강력 추천)

      winget install Obsidian.Obsidian

      Obsidian 실행 → "Open folder as vault" → E:\project\work05 선택

      설정 → 커뮤니티 플러그인 → "Dataview" 설치·활성화
      (대시보드.md가 작동하려면 필요)

  ▶ Step 2. 웹 실행 (Python 불필요) ★ 추천

      더블클릭:  E:\project\work05\웹시작.bat
      (또는 kv-web\start_web.bat)

      브라우저 http://localhost:8765:
        [시작] 3단계 안내
        [대시보드] 갱신 임박·자녀보험 미가입 (Obsidian 없이!)
        [수집] 파일 드래그
        [AI 작업큐] Claude 프롬프트 복사

  ▶ Step 3. 샘플 데모 돌려보기 (Python 있는 경우)

      knowledge-vault\run_pain_demo.bat

      → 상담기록, AI작업큐 폴더에 결과 파일이 생깁니다.
      → Obsidian에서 열어보세요.


--------------------------------------------------------------------------------
3. 매일 쓰는 흐름 (80분 → 6분 목표)
--------------------------------------------------------------------------------

  [AS-IS 지금]                    [TO-BE 이 시스템]
  녹음 정리 20분                  AI 정리 1분
  제안서 작성 30분                제안서 초안 2분
  문자 작성 10분                  문자 초안 30초
  갱신 확인 15분                  대시보드 자동 0분
  ─────────────                   ─────────────
  합계 약 80분                    합계 약 6분 (+ 검토)

  실제 일과:

    1) 상담 전/후
       - 녹음 파일 → knowledge-vault\inbox\audio\ 에 복사
       - 카톡·메모 → inbox\notes\
       - 명함·서류 사진 → inbox\images\
       - 엑셀 명단 → inbox\excel\

    2) 자동 처리
       - CLI:  python -m kv all        (수집 + 정제 + Obsidian 동기화)
       - 또는: python -m kv watch      (inbox 폴더 감시, 파일 넣으면 자동)

    3) 상담 정리 (Claude)
       - python -m kv counsel --text "전사파일.txt" --customer 홍길동
       - 또는 AI작업큐\ 에 생긴 .md 파일을 Claude에 붙여넣기
       - 프롬프트.md 의 ① 상담 정리 참고

    4) 제안서·문자 (Claude)
       - python -m kv pack propose 홍길동    → 제안서 프롬프트 생성
       - python -m kv pack message 홍길동    → 안내 문자 프롬프트 생성
       - 결과를 AI작업큐\ 에서 확인 → 검토 후 발송

    5) 갱신·타깃 확인
       - Obsidian에서 대시보드.md 열기
       - #갱신임박, #자녀보험미가입 태그 고객 자동 표시


--------------------------------------------------------------------------------
4. 실행 파일 빠른 참조
--------------------------------------------------------------------------------

  파일                              하는 일
  ─────────────────────────────────────────────────────────
  KnowledgeVault_실행.bat           ★ 통합 실행 (EXE/Python/웹 자동)
  kv-web\start_web.bat              웹만 (Python 불필요)
  knowledge-vault\start.bat         CLI 안내 + 상태 확인
  knowledge-vault\run_all.bat       샘플 데이터 전체 파이프라인
  knowledge-vault\run_pain_demo.bat Pain Point 데모 (정수남 샘플)
  video\start_video.bat             소개 영상
  start_demo.bat                    AI 아키텍처 웹 데모
  index.html                        소개 페이지 (더블클릭)


--------------------------------------------------------------------------------
5. CLI 명령어 (knowledge-vault 폴더에서)
--------------------------------------------------------------------------------

  cd /d E:\project\work05\knowledge-vault

  python -m kv status              현재 상태 (인덱스, Obsidian 경로)
  python -m kv collect             inbox → vault\raw (MD 변환)
  python -m kv refine              raw → refined + 검색 인덱스
  python -m kv sync                refined → Obsidian 볼트 복사
  python -m kv all                 collect + refine + sync 한번에
  python -m kv watch               inbox 자동 감시
  python -m kv search "종신보험"   전체 검색
  python -m kv pain                pain point 목록 + 해결 명령 안내
  python -m kv counsel --text 파일 --customer 이름
  python -m kv pack propose 이름   제안서 프롬프트팩
  python -m kv pack message 이름   안내 문자 프롬프트팩

  Python 패키지 설치 (최초 1회):
    pip install -r requirements.txt


--------------------------------------------------------------------------------
6. inbox 폴더 — 파일 넣는 곳
--------------------------------------------------------------------------------

  knowledge-vault\inbox\
    audio\     녹음 (.mp3, .wav, .m4a …)  → Whisper로 전사 (Python/Portable)
    images\    사진·서류 (.jpg, .png …)   → OCR (Tesseract 설치 시)
    excel\     엑셀 (.xlsx, .csv)
    notes\     메모·카톡 복사·전사 텍스트 (.txt, .md)

  index.html 에 나온 흩어진 정보 → 위 폴더에 넣으면 자동 태그·MD 변환


--------------------------------------------------------------------------------
7. Claude 쓰는 법 (API 키 없이)
--------------------------------------------------------------------------------

  1. Claude 앱(또는 claude.ai) 실행
  2. AI작업큐\ 폴더의 .md 파일 내용 복사
     또는 프롬프트.md 에서 해당 번호 프롬프트 복사
  3. 고객 카드(고객DB\이름.md) 내용도 함께 붙여넣기
  4. AI 결과를 검토한 뒤 고객 카드·상담기록에 반영

  ※ 토큰(사용량)은 Claude/ Cursor 대시보드에서 확인
     Cursor: https://cursor.com/dashboard/usage


--------------------------------------------------------------------------------
8. Whisper 녹음→글자 (Portable)
--------------------------------------------------------------------------------

  녹음 파일 자동 전사는 Python + faster-whisper 필요합니다.

  방법 1) KnowledgeVault_실행.bat  (kv-portable 서버, 포트 8765)
  방법 2) knowledge-vault CLI + config.yaml 의 whisper 설정

  EXE로 만들려면 (디스크 2GB 이상 여유 필요):
    kv-portable\build_exe.bat

  ※ E: 드라이브 용량이 부족하면 빌드/영상 저장이 실패할 수 있습니다.
     영상 MP4는 C:\Users\jessy\Videos\ 에 저장될 수 있습니다.


--------------------------------------------------------------------------------
9. 주의사항
--------------------------------------------------------------------------------

  • 실제 고객 정보는 공개 저장소(GitHub)에 올리지 마세요.
  • 이 볼트의 고객·상품 데이터는 데모용 가상 데이터입니다.
  • AI 초안은 반드시 설계사가 검토 후 발송하세요.
  • 보험사 사이트 자동 로그인/수집은 하지 않습니다.
  • 카톡은 자동 수집 안 됨 → 대화 복사 후 inbox\notes\ 에 붙여넣기

  자세한 보안 체크: 개인정보-주의.md


--------------------------------------------------------------------------------
10. 문제 해결
--------------------------------------------------------------------------------

  Q. 웹이 안 열려요
  A. kv-web\start_web.bat 다시 실행. 방화벽에서 localhost:8765 허용.

  Q. 검색이 안 돼요
  A. python -m kv all 한 번 실행해서 인덱스 갱신.

  Q. 대시보드가 비어 있어요
  A. Obsidian + Dataview 플러그인 설치 확인.
     고객DB\*.md 에 #갱신임박 등 태그가 있는지 확인.

  Q. 녹음이 글자로 안 바뀌어요
  A. 웹만 쓰면 Whisper 없음 → KnowledgeVault_실행.bat (Portable) 사용.
     pip install faster-whisper

  Q. E: 드라이브 용량 부족
  A. 불필요 파일 삭제 후 재시도. kv-portable\build\ 폴더가 크면 삭제 가능.


--------------------------------------------------------------------------------
11. 더 보기
--------------------------------------------------------------------------------

  README.md              GitHub용 상세 설명
  시간절약-예제.md       항목별 AS-IS / TO-BE
  프롬프트.md            Claude 프롬프트 원본
  https://prjessy.github.io/insurance/   온라인 소개 사이트

================================================================================
  요약: 웹시작.bat 실행 → 브라우저에서 전부 사용 (Python 불필요)
        Obsidian은 선택 — 대시보드·고객DB 연동용
================================================================================
