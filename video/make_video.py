"""index.html 내용을 MP4 소개 영상으로 생성."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1088  # 16의 배수 (코덱 호환)
FPS = 30
BG = (232, 235, 226)
PAPER = (244, 246, 239)
TEXT = (31, 39, 35)
MUTED = (91, 102, 94)
ACCENT = (204, 63, 38)
TEAL = (44, 107, 102)
DARK = (31, 39, 35)


def font(size: int, bold: bool = False):
    names = ["malgunbd.ttf", "malgun.ttf"] if bold else ["malgun.ttf", "arial.ttf"]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    lines, line = [], ""
    for ch in text:
        test = line + ch
        if draw.textlength(test, font=fnt) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = ch
    if line:
        lines.append(line)
    return lines


def draw_centered(draw, text, y, fnt, fill=TEXT, max_w=W - 200):
    for para in text.split("\n"):
        for ln in wrap(draw, para, fnt, max_w):
            tw = draw.textlength(ln, font=fnt)
            draw.text(((W - tw) / 2, y), ln, font=fnt, fill=fill)
            y += fnt.size + 12
        y += 8
    return y


def scene_frame(title, lines=None, subtitle="", bg=BG, dark=False, extras=None):
    img = Image.new("RGB", (W, H), DARK if dark else bg)
    draw = ImageDraw.Draw(img)
    fill = (232, 235, 226) if dark else TEXT
    y = 120
    if subtitle:
        draw_centered(draw, subtitle, y, font(28), fill=TEAL if not dark else (240, 201, 122))
        y += 60
    draw_centered(draw, title, y, font(64, True), fill=fill)
    y += 120
    if lines:
        for ln in lines:
            y = draw_centered(draw, ln, y, font(36), fill=fill if dark else MUTED)
    if extras:
        extras(draw, y)
    return np.array(img)


def scene_compare():
    def extras(draw, y):
        # AS-IS box
        draw.rectangle([280, 400, 880, 780], fill=PAPER, outline=(201, 207, 193))
        draw.text((320, 430), "AS-IS 지금", font=font(40, True), fill=ACCENT)
        draw.text((320, 510), "녹음정리 20분 + 제안서 30분", font=font(32), fill=MUTED)
        draw.text((320, 560), "문자 10분 + 갱신확인 15분", font=font(32), fill=MUTED)
        draw.text((320, 650), "80분", font=font(80, True), fill=ACCENT)
        # TO-BE box
        draw.rectangle([1040, 400, 1640, 780], fill=PAPER, outline=(201, 207, 193))
        draw.text((1080, 430), "TO-BE 이 시스템", font=font(40, True), fill=TEAL)
        draw.text((1080, 510), "AI 정리 1분 + 제안서 2분", font=font(32), fill=MUTED)
        draw.text((1080, 560), "문자 30초 + 대시보드 0분", font=font(32), fill=MUTED)
        draw.text((1080, 650), "6분", font=font(80, True), fill=TEAL)
        draw.text((820, 820), "→", font=font(72, True), fill=MUTED)
    return scene_frame("고객 한 명, 하루가 달라집니다", extras=extras)


SCENES = [
    (5, lambda: scene_frame(
        "흩어진 고객 정보가 스스로 정리되고\nAI가 제안서까지 씁니다",
        subtitle="OBSIDIAN × CLAUDE — 보험 영업 AI 도우미",
    )),
    (4, lambda: scene_frame(
        "지금은 정보가 이렇게 흩어져 있죠",
        lines=["📒 수첩  📊 엑셀  💬 카톡  📞 통화메모  🧾 서류  🧠 기억"],
    )),
    (4, lambda: scene_frame(
        "01 — 고객 한 명 = 한 장의 카드",
        lines=["정수남 · #갱신임박 · #자녀보험미가입", "실손 갱신 7/5 · 월 29,000원"],
    )),
    (4, lambda: scene_frame(
        "02 — 태그만 달면 자동 분류",
        lines=["홍길동 2026-07-20  갱신임박", "정수남 2026-07-05  갱신임박·자녀", "600명이어도 1초"],
        dark=True,
    )),
    (5, lambda: scene_frame(
        "03 — 녹취 → AI 제안서 + 안내 문자",
        lines=[
            '"실손 갱신 부담돼요, 아이 보험도 알아보고 싶어요"',
            "→ 우리아이 종합보험 + 실손 4세대 비교안 자동 작성",
        ],
    )),
    (5, scene_compare),
    (4, lambda: scene_frame(
        "Obsidian + Claude",
        lines=["코딩 없이 · 내 컴퓨터 안에서", "고객 정보는 클라우드로 나가지 않습니다"],
        subtitle="🔒 보험 설계사를 위한 영업 자동화",
    )),
]


def pick_output() -> Path:
    name = "보험영업AI도우미_소개.mp4"
    candidates = [
        Path(__file__).parent / name,
        Path("F:/") / name,
        Path.home() / "Videos" / name,
        Path("C:/Users/Public/Videos") / name,
    ]
    for path in candidates:
        root = Path(path.anchor) if path.anchor else path.parent
        try:
            if shutil.disk_usage(root).free < 80 * 1024 * 1024:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        except OSError:
            continue
    return candidates[0]


def main():
    try:
        import imageio
    except ImportError:
        print("imageio 설치: pip install imageio imageio-ffmpeg")
        return 1

    out = pick_output()
    total = sum(dur for dur, _ in SCENES) * FPS
    print(f"출력: {out}")
    print(f"프레임 {total}개 생성 중...")

    writer = imageio.get_writer(
        str(out), fps=FPS, codec="libx264", quality=7, macro_block_size=1,
    )
    try:
        for dur, maker in SCENES:
            img = maker()
            for _ in range(dur * FPS):
                writer.append_data(img)
    finally:
        writer.close()

    print(f"완료: {out}")
    print(f"길이: 약 {total // FPS}초")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
