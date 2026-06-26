// State and Elements
let currentMode = "1";
const diagramContainer = document.getElementById('diagram-container');
const modeTitle = document.getElementById('mode-title');
const modeDesc = document.getElementById('mode-desc');
const resultBoard = document.getElementById('result-content');
const runBtn = document.getElementById('run-btn');
const terminal = document.getElementById('terminal');
const autoDemoBtn = document.getElementById('auto-demo-btn');

// Definitions of modes
const modesData = {
    "1": {
        title: "1. 도입 전 (단일 AI + 하드코딩)",
        desc: "거대한 AI 뇌(Single Agent) 하나가 모든 역할을 수행합니다.<br>AI 코드 안에 'DB 접속 함수'가 딱딱하게 박혀있습니다(하드코딩).<br>그래서 기능 한 번 치명적인 오류가 발생할 위험이 높습니다.",
        nodes: [
            { id: "user", text: "👤 사용자", style: "top: 10%; left: 50%; width: 150px; transform: translate(-50%, 0);" },
            { id: "ai", text: "🧠 거대 AI (단일)", style: "top: 40%; left: 50%; width: 220px; transform: translate(-50%, 0);" },
            { id: "db_todo", text: "🗄️ Todo DB (내장)", style: "top: 75%; left: 25%; width: 170px; transform: translate(-50%, 0); background:#451a03; border-color:#f59e0b;" },
            { id: "db_schedule", text: "🗄️ 달력 DB (내장)", style: "top: 75%; left: 75%; width: 170px; transform: translate(-50%, 0); background:#451a03; border-color:#f59e0b;" }
        ],
        connections: [
            { id: "c1", from: "user", to: "ai" },
            { id: "c2", from: "ai", to: "db_todo" },
            { id: "c3", from: "ai", to: "db_schedule" }
        ]
    },
    "2": {
        title: "2. MCP 도입 (단일 AI + 외부 도구)",
        desc: "여전히 AI는 하나지만, <strong>표준 규격인 MCP</strong>를 도입했습니다.<br>이제 AI는 직접 DB에 접근하지 않고, 외부의 '도구 서버'에 접속해서 필요한 기능만 안전하게 빌려 씁니다 (플러그인).",
        nodes: [
            { id: "user", text: "👤 사용자", style: "top: 10%; left: 50%; width: 150px; transform: translate(-50%, 0);" },
            { id: "ai", text: "🧠 거대 AI (단일)", style: "top: 40%; left: 50%; width: 220px; transform: translate(-50%, 0);" },
            { id: "mcp", text: "🔌 표준 MCP 도구 서버", sub: "[ Todo 도구 | Schedule 도구 ]", style: "top: 75%; left: 50%; width: 280px; transform: translate(-50%, 0); background:linear-gradient(135deg, #064e3b, #10b981);" }
        ],
        connections: [
            { id: "c1", from: "user", to: "ai" },
            { id: "c2", from: "ai", to: "mcp" }
        ]
    },
    "3": {
        title: "3. 다중 에이전트 도입 (팀 협업 - 툴 내장)",
        desc: "거대한 AI를 쪼개어 '일정 봇'과 '할 일 봇'으로 전문화(Multi-Agent)했습니다.<br>하지만 각자의 코드 안에 여전히 예전 방식(하드코딩)으로 DB 접근법이 적혀있어서, 유지보수는 여전히 불편합니다.",
        nodes: [
            { id: "user", text: "👤 사용자", style: "top: 5%; left: 50%; width: 150px; transform: translate(-50%, 0);" },
            { id: "manager", text: "👑 매니저 AI", style: "top: 30%; left: 50%; width: 180px; transform: translate(-50%, 0); background:linear-gradient(135deg, #4c1d95, #8b5cf6);" },
            { id: "agent_todo", text: "🤖 Todo 에이전트", style: "top: 55%; left: 25%; width: 170px; transform: translate(-50%, 0); background:linear-gradient(135deg, #1e3a8a, #3b82f6);" },
            { id: "agent_schedule", text: "🤖 스케줄 에이전트", style: "top: 55%; left: 75%; width: 170px; transform: translate(-50%, 0); background:linear-gradient(135deg, #1e3a8a, #3b82f6);" },
            { id: "db_todo", text: "🗄️ Todo DB", style: "top: 85%; left: 25%; width: 170px; transform: translate(-50%, 0); background:#451a03; border-color:#f59e0b;" },
            { id: "db_schedule", text: "🗄️ 달력 DB", style: "top: 85%; left: 75%; width: 170px; transform: translate(-50%, 0); background:#451a03; border-color:#f59e0b;" }
        ],
        connections: [
            { id: "c1", from: "user", to: "manager" },
            { id: "c2", from: "manager", to: "agent_todo" },
            { id: "c3", from: "manager", to: "agent_schedule" },
            { id: "c4", from: "agent_todo", to: "db_todo" },
            { id: "c5", from: "agent_schedule", to: "db_schedule" }
        ]
    },
    "4": {
        title: "4. 최종 형태 🚀 (다중 에이전트 + MCP)",
        desc: "최고의 아키텍처입니다! <br>역할이 나뉜 <strong>전문 에이전트 팀</strong>과, 중앙 집중 관리되는 <strong>표준 MCP 도구 서버</strong>가 만났습니다. 어떤 새로운 AI 모델이 나와도, 도구 코드를 한 줄도 수정할 필요가 없습니다!",
        nodes: [
            { id: "user", text: "👤 사용자", style: "top: 5%; left: 50%; width: 150px; transform: translate(-50%, 0);" },
            { id: "manager", text: "👑 매니저 AI (허브)", style: "top: 30%; left: 50%; width: 180px; transform: translate(-50%, 0); background:linear-gradient(135deg, #4c1d95, #8b5cf6);" },
            { id: "agent_todo", text: "🤖 Todo 에이전트", style: "top: 55%; left: 25%; width: 170px; transform: translate(-50%, 0); background:linear-gradient(135deg, #1e3a8a, #3b82f6);" },
            { id: "agent_schedule", text: "🤖 스케줄 에이전트", style: "top: 55%; left: 75%; width: 170px; transform: translate(-50%, 0); background:linear-gradient(135deg, #1e3a8a, #3b82f6);" },
            { id: "mcp", text: "🔌 전사 표준 MCP 서버", sub: "[ 권한 기반 도구 자동 할당 ]", style: "top: 85%; left: 50%; width: 300px; transform: translate(-50%, 0); background:linear-gradient(135deg, #064e3b, #10b981);" }
        ],
        connections: [
            { id: "c1", from: "user", to: "manager" },
            { id: "c2", from: "manager", to: "agent_todo" },
            { id: "c3", from: "manager", to: "agent_schedule" },
            { id: "c4", from: "agent_todo", to: "mcp" },
            { id: "c5", from: "agent_schedule", to: "mcp" }
        ]
    }
};

// SVG Draw Line function
function getElCenter(id) {
    const el = document.getElementById(`node-${id}`);
    if (!el) return null;
    return {
        x: el.offsetLeft + el.offsetWidth / 2,
        y: el.offsetTop + el.offsetHeight / 2
    };
}

function drawSVG() {
    // Remove old svg
    const oldSvg = document.getElementById('diagram-svg');
    if (oldSvg) oldSvg.remove();

    const container = document.getElementById('diagram-container');
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('id', 'diagram-svg');
    svg.setAttribute('class', 'line-overlay');

    // Setup Connections
    const conns = modesData[currentMode].connections;
    conns.forEach(c => {
        const p1 = getElCenter(c.from);
        const p2 = getElCenter(c.to);
        if (!p1 || !p2) return;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute('id', `line-${c.id}`);
        path.setAttribute('class', 'conn-line');
        // Simple curve
        const d = `M ${p1.x} ${p1.y} C ${p1.x} ${(p1.y + p2.y) / 2}, ${p2.x} ${(p1.y + p2.y) / 2}, ${p2.x} ${p2.y}`;
        path.setAttribute('d', d);
        svg.appendChild(path);
    });

    container.appendChild(svg);
}

// Render Diagram
function renderMode(modeStr) {
    const data = modesData[modeStr];
    modeTitle.innerHTML = data.title;
    modeDesc.innerHTML = data.desc;

    // Render Nodes
    diagramContainer.innerHTML = '';
    data.nodes.forEach(n => {
        const div = document.createElement('div');
        div.id = `node-${n.id}`;
        div.className = 'node';
        div.style = n.style;
        div.innerHTML = `<div>${n.text}</div>` + (n.sub ? `<div class="mcp-plugin-sub">${n.sub}</div>` : "");
        diagramContainer.appendChild(div);
    });

    // Must wait for render to calculate offsets
    setTimeout(drawSVG, 100);
}

// UI Setup
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active', 'highlight'));
        btn.classList.add(btn.dataset.mode === "4" ? 'highlight' : 'active');
        currentMode = btn.dataset.mode;
        resetApp();
    });
});

window.addEventListener('resize', drawSVG);

function resetApp() {
    terminal.innerHTML = `<div class="log system">시스템 로드 완료. 위 실행 버튼을 눌러보세요.</div>`;
    resultBoard.innerHTML = `[시나리오 대기 중] "내일 9시 회의 스케줄 잡고, 할 일에 '자료 준비' 추가해줘"`;
    renderMode(currentMode);
}

// Logging and Animation logic
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function log(msg, type = "system") {
    const el = document.createElement("div");
    el.className = `log ${type}`;
    el.innerHTML = msg;
    terminal.appendChild(el);
    terminal.scrollTop = terminal.scrollHeight;
    await sleep(800);
}

function activateNode(id, error = false) {
    const el = document.getElementById(`node-${id}`);
    if (!el) return;
    el.classList.add(error ? 'error-node' : 'active-node');
    setTimeout(() => el.classList.remove('error-node', 'active-node'), 1200);
}

function activateLine(id, error = false) {
    const el = document.getElementById(`line-${id}`);
    if (!el) return;
    const c = error ? 'error-line' : 'active-line';
    el.classList.add(c);
    setTimeout(() => el.classList.remove(c), 1200);
}

const API_BASE = window.location.origin;
const SCENARIO_INTENT = "내일 9시 회의 스케줄 잡고, 할 일에 '자료 준비' 추가해줘";

async function fetchScenario(mode) {
    const res = await fetch(`${API_BASE}/api/run/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intent: SCENARIO_INTENT }),
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return res.json();
}

async function playApiScenario(data) {
    activateNode("user");
    activateLine("c1");

    for (const entry of data.logs) {
        if (entry.message.includes("Schedule 에이전트") || entry.message.includes("add_schedule")) {
            activateLine("c3"); activateNode("agent_schedule");
            activateLine("c5"); activateNode("mcp");
        }
        if (entry.message.includes("Todo 에이전트") || entry.message.includes("add_todo")) {
            activateLine("c2"); activateNode("agent_todo");
            activateLine("c4"); activateNode("mcp");
        }
        if (entry.message.includes("매니저")) activateNode("manager");
        if (entry.message.includes("병렬")) {
            activateLine("c2"); activateLine("c3");
            activateNode("agent_todo"); activateNode("agent_schedule");
        }
        await log(entry.message, entry.type);
        if (entry.delay_ms && entry.delay_ms !== 800) await sleep(entry.delay_ms - 800);
    }
    resultBoard.innerHTML = data.result_html;
}

// Simulation Runs
async function runCurrentModeScenario() {
    runBtn.disabled = true;
    if (autoDemoBtn) autoDemoBtn.disabled = true;
    terminal.innerHTML = '';
    resultBoard.innerHTML = `처리 중... ⏳`;

    try {
        if (currentMode === "4") {
            const data = await fetchScenario("4");
            await playApiScenario(data);
        } else {
            await log(`> 👤 사용자: "내일 9시 스케줄! 그리고 할 일 추가!"`, "ai");
            activateNode("user");
            activateLine("c1");

            if (currentMode === "1") await simulateMode1();
            else if (currentMode === "2") await simulateMode2();
            else if (currentMode === "3") await simulateMode3();
        }
    } catch (err) {
        await log(`⚠️ 백엔드 연결 실패 — 클라이언트 시뮬레이션으로 대체합니다. (${err.message})`, "warning");
        activateNode("user");
        activateLine("c1");
        if (currentMode === "1") await simulateMode1();
        else if (currentMode === "2") await simulateMode2();
        else if (currentMode === "3") await simulateMode3();
        else if (currentMode === "4") await simulateMode4();
    }

    runBtn.disabled = false;
    if (autoDemoBtn) autoDemoBtn.disabled = false;
}

runBtn.addEventListener('click', runCurrentModeScenario);

async function simulateMode1() {
    activateNode("ai");
    await log("[단일 AI] 접수 완료. 내장된 스케줄 DB 접속 코드 실행...", "system");

    // Highlight schedule flow
    activateLine("c3", true); // Let's show a slight error flow
    activateNode("db_schedule", true);
    await log("⚠️ [경고] DB 접속 코드 포맷 변경으로 일시적 오류 발생 (하드코딩의 단점)", "error");
    await sleep(500);

    activateLine("c3"); activateNode("db_schedule");
    await log("[내부 툴] 스케줄 DB 강제 쓰기 완료.", "tool");

    // Highlight todo flow
    activateLine("c2"); activateNode("db_todo");
    await log("[내부 툴] 할 일 DB 파싱 후 쓰기 완료.", "tool");

    await log("✓ 완료. 그러나 하나가 고장나면 전체 시스템이 멈출 위험 상존.", "error");
    resultBoard.innerHTML = `✅ [완료] 단일 AI가 (버벅거리며) 둘 다 처리했습니다.`;
}

async function simulateMode2() {
    activateNode("ai");
    await log("[단일 AI] 접수 완료. 이번엔 외부 도구를 불러오겠습니다.", "system");

    activateLine("c2");
    activateNode("mcp");
    await log("[MCP 서버 연결] 사용 가능한 도구 목록(Todo, Schedule) 획득 성공!", "success");

    activateLine("c2");
    await log("[단일 AI -> MCP] Schedule 도구 실행 요청 (파라미터: 9시 회의)", "tool");
    await log("[단일 AI -> MCP] Todo 도구 실행 요청 (파라미터: 자료 준비)", "tool");

    await log("✓ 완료. 플러그인 연결은 훌륭하나, 한 AI가 두 가지 역할을 다 계산하려니 느립니다.", "warning");
    resultBoard.innerHTML = `✅ [완료] AI(1)가 MCP 도구(2개)를 빌려 써서 처리했습니다.`;
}

async function simulateMode3() {
    activateNode("manager");
    await log("[매니저 AI] '할 일'팀과 '일정'팀으로 업무를 안전하게 분할 지시합니다.", "system");

    // Schedule Flow
    activateLine("c3"); activateNode("agent_schedule");
    await log("[스케줄 에이전트] 9시 회의 스케줄 확인.", "ai");
    activateLine("c5"); activateNode("db_schedule");
    await log(" -> 독자적인 하드코딩된 API로 DB 접속 성공", "tool");

    // Todo Flow
    activateLine("c2"); activateNode("agent_todo");
    await log("[Todo 에이전트] 회의 자료 준비 할 일 확인.", "ai");
    activateLine("c4"); activateNode("db_todo");
    await log(" -> 옛날 방식의 DB 접속 코드를 자기가 직접 실행 성공", "tool");

    await log("✓ 업무 분담은 완벽! 하지만 코드가 에이전트마다 분산되어 있어 확장이 힘듭니다.", "warning");
    resultBoard.innerHTML = `✅ [완료] 매니저가 지시하고, 서브 에이전트들이 (각자 방식대로) 처리했습니다.`;
}

async function simulateMode4() {
    activateNode("manager");
    await log("🚀 [최종 아키텍처 가동]", "system");
    await log("[매니저 AI 허브] 전문 팀들에게 작업 분배 및 권한(MCP 접속 주소) 배포 완료.", "ai");

    // Concurrent flow
    activateLine("c2"); activateLine("c3");
    activateNode("agent_todo"); activateNode("agent_schedule");

    await log("⚡ [다중 에이전트 병렬 처리 시작]", "system");

    // MCP call
    activateLine("c4"); activateLine("c5");
    activateNode("mcp");

    await log(" -> [Todo 에이전트] 공통 MCP 서버의 'Todo 도구' 호출!", "success");
    await log(" -> [Schedule 에이전트] 공통 MCP 서버의 'Schedule 도구' 호출!", "success");

    await sleep(800);
    await log("★ 퍼펙트! 최고의 보안, 표준화된 연결, 분산된 역할로 순식간에 끝났습니다.", "success");
    resultBoard.innerHTML = `🎉 <strong>[퍼펙트 처리 완료!]</strong> <br><br>다중 AI가 '전문성'을 발휘하고,<br>MCP로 '안전하고 통일된 도구'를 동시 다발적으로 이용했습니다!`;
}

// Initial Call
renderMode("1");

// ---- 자동 데모: 4가지 아키텍처를 순서대로 실행 ----

function switchToMode(mode) {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active', 'highlight'));
    const btn = document.querySelector(`.nav-btn[data-mode="${mode}"]`);
    if (btn) btn.classList.add(mode === "4" ? 'highlight' : 'active');
    currentMode = mode;
    resetApp();
}

if (autoDemoBtn) {
    autoDemoBtn.addEventListener('click', async () => {
        autoDemoBtn.disabled = true;
        runBtn.disabled = true;

        for (const mode of ["1", "2", "3", "4"]) {
            switchToMode(mode);
            await sleep(600);
            await runCurrentModeScenario();
            await sleep(1500);
        }

        await log("🎬 4단계 자동 데모 완료! 각 아키텍처 방식을 모두 확인했습니다.", "success");
        autoDemoBtn.disabled = false;
        runBtn.disabled = false;
    });
}

if (new URLSearchParams(window.location.search).get("autoplay") === "1" && autoDemoBtn) {
    window.addEventListener("load", () => setTimeout(() => autoDemoBtn.click(), 1200));
}
