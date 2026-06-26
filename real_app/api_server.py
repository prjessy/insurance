"""웹 데모(index.html)와 연동하는 FastAPI 자동화 서버."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from scenario_runner import DEFAULT_INTENT, run_all_modes_demo, run_scenario, scenario_to_dict

WEB_DEMO_DIR = Path(__file__).resolve().parent.parent / "web_demo"

app = FastAPI(title="AI Architecture Automation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    intent: str = Field(default=DEFAULT_INTENT, description="사용자 시나리오 문장")


class AutoDemoRequest(BaseModel):
    intent: str = Field(default=DEFAULT_INTENT)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ai-architecture-automation"}


@app.post("/api/run/{mode}")
async def run_mode(mode: str, body: RunRequest | None = None):
    if mode not in ("1", "2", "3", "4"):
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")
    intent = body.intent if body else DEFAULT_INTENT
    result = run_scenario(mode, intent)
    return scenario_to_dict(result)


@app.post("/api/auto-demo")
async def auto_demo(body: AutoDemoRequest | None = None):
    """4가지 아키텍처 모드를 순서대로 자동 실행합니다."""
    intent = body.intent if body else DEFAULT_INTENT
    results = await run_all_modes_demo(intent)
    return {"modes": results, "intent": intent}


@app.get("/api/db/status")
def db_status():
    from scenario_runner import _load_db

    todos, schedules = _load_db()
    return {"todos": todos, "schedules": schedules}


if WEB_DEMO_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(WEB_DEMO_DIR), html=True), name="web_demo")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    print(f"AI Architecture Automation Server -> http://localhost:{port}")
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=False)
