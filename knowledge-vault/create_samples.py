"""샘플 데이터 생성 스크립트."""
from pathlib import Path

from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
EXCEL = ROOT / "inbox" / "excel" / "프로젝트_일정.xlsx"
IMG = ROOT / "inbox" / "images" / "화이트보드_메모.png"

# 엑셀 샘플
wb = Workbook()
ws = wb.active
ws.title = "3월일정"
ws.append(["날짜", "시간", "제목", "담당"])
ws.append(["2026-03-05", "09:00", "기획 회의", "김팀장"])
ws.append(["2026-03-07", "14:00", "AI 데모 리허설", "박대리"])
ws.append(["2026-03-10", "10:00", "Obsidian 워크숍", "이과장"])
wb.save(EXCEL)
print(f"created: {EXCEL}")

# 이미지 샘플 (OCR 테스트용)
img = Image.new("RGB", (800, 400), "white")
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("malgun.ttf", 36)
except OSError:
    font = ImageFont.load_default()
lines = [
    "Knowledge Vault Test",
    "Meeting 09:00",
    "Project: AI Automation",
    "Tag: #기획 #회의",
]
y = 40
for line in lines:
    draw.text((40, y), line, fill="black", font=font)
    y += 70
img.save(IMG)
print(f"created: {IMG}")
