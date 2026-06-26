const DB_NAME = "kv-web";
const STORE = "docs";

const PROMPTS = {
  counsel: `너는 보험 설계사의 상담 정리 비서야. 아래 상담 전사 내용을 읽고 다음 형식으로 정리해줘.
개인정보는 내가 입력한 것만 사용하고 추측하지 마.

# 핵심 요약 (3줄 이내)
# 고객 니즈
# 파악된 정보
- 가족구성:
- 가입/갱신 변동:
- 추천할 유형태그: (갱신임박 / 자녀보험미가입 / VIP / 신규 중 해당)
# 다음 액션 (체크리스트)

[상담 전사 내용]
"""
{{TRANSCRIPT}}
"""`,

  propose: `아래 [고객 정보]와 [상품 목록]을 바탕으로, 이 고객에게 맞는 보험 제안서를 작성해줘.
- 고객의 니즈·가족구성·갱신 상황을 근거로 1~2개 상품을 추천
- 각 상품마다 "왜 이 고객에게 맞는지" 한 문장 근거 포함
- 표로 보장·월보험료 비교
- 마지막에 부드러운 권유 문구 2~3줄

[고객 정보]
"""
{{CUSTOMER}}
"""

[상품 목록]
"""
{{PRODUCTS}}
"""`,

  message: `아래 고객에게 보낼 짧은 안내 메시지(문자/카톡용)를 작성해줘.
- 유형태그에 맞는 톤: 갱신임박=갱신 안내, 자녀보험미가입=자녀 보장 제안
- 3~4문장, 부담스럽지 않게, 상담 예약을 유도
- 과장·확정적 보장 표현 금지

[고객 정보]
"""
{{CUSTOMER}}
"""`,
};

const PAIN_POINTS = [
  { chip: "흩어진 정보", asis: "여기저기 분산", tobe: "웹에 파일 드래그", tab: "collect" },
  { chip: "녹취 정리 20분", asis: "20분", tobe: "1분", tab: "prompt" },
  { chip: "고객 찾기 5분", asis: "엑셀", tobe: "즉시", tab: "search" },
  { chip: "제안서 30분", asis: "30분", tobe: "2분", tab: "prompt" },
  { chip: "안내 문자 10분", asis: "10분", tobe: "30초", tab: "prompt" },
  { chip: "갱신 확인 15분", asis: "엑셀", tobe: "대시보드 0분", tab: "pain" },
];

let docs = [];
let customers = {};
let customerRecords = {};
let products = "";
let vaultSource = "demo";

function parseFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return {};
  const fm = {};
  for (const line of m[1].split("\n")) {
    const idx = line.indexOf(":");
    if (idx < 0) continue;
    const key = line.slice(0, idx).trim();
    let val = line.slice(idx + 1).trim();
    if (val.startsWith("[")) {
      try { val = JSON.parse(val.replace(/'/g, '"')); } catch { /* keep string */ }
    }
    fm[key] = val;
  }
  return fm;
}

function ingestCustomerRecord(name, text) {
  const fm = parseFrontmatter(text);
  if (fm.type && fm.type !== "고객") return;
  const record = {
    name: fm.이름 || name,
    phone: fm.연락처 || "",
    tags: Array.isArray(fm.유형태그) ? fm.유형태그 : [],
    renewal: fm.다음갱신일 || "",
    family: Array.isArray(fm.가족구성) ? fm.가족구성.join(", ") : String(fm.가족구성 || ""),
    lastCounsel: fm.최근상담일 || "",
    raw: text,
  };
  if (!record.name) return;
  customerRecords[record.name] = record;
  customers[record.name] = text;
}

function daysUntil(dateStr) {
  if (!dateStr) return 9999;
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return 9999;
  return Math.ceil((d - new Date()) / 86400000);
}

function renderDashboard() {
  const records = Object.values(customerRecords).sort((a, b) => a.renewal.localeCompare(b.renewal));
  const renewal = records.filter(r => daysUntil(r.renewal) <= 60 && daysUntil(r.renewal) >= 0);
  const child = records.filter(r => r.tags.some(t => t.includes("자녀보험")));

  document.getElementById("dash-stats").innerHTML = `
    <div class="stat"><b>${records.length}</b>전체 고객</div>
    <div class="stat"><b>${renewal.length}</b>갱신 임박</div>
    <div class="stat"><b>${child.length}</b>자녀보험 미가입</div>
    <div class="stat"><b>${vaultSource === "demo" ? "데모" : "볼트"}</b>데이터 출처</div>`;

  const pill = tags => tags.map(t => `<span class="tag-pill">${esc(t)}</span>`).join("");

  document.querySelector("#dash-renewal tbody").innerHTML = renewal.length
    ? renewal.map(r => `<tr>
        <td><b>${esc(r.name)}</b></td><td>${esc(r.renewal)} <small>(${daysUntil(r.renewal)}일)</small></td>
        <td>${pill(r.tags)}</td><td>${esc(r.phone)}</td>
        <td><button class="btn-link" data-pick="${esc(r.name)}">AI 작업</button></td></tr>`).join("")
    : `<tr><td colspan="5" class="hint">해당 없음</td></tr>`;

  document.querySelector("#dash-child tbody").innerHTML = child.length
    ? child.map(r => `<tr>
        <td><b>${esc(r.name)}</b></td><td>${esc(r.family)}</td><td>${esc(r.phone)}</td>
        <td><button class="btn-link" data-pick="${esc(r.name)}">AI 작업</button></td></tr>`).join("")
    : `<tr><td colspan="4" class="hint">해당 없음</td></tr>`;

  document.querySelector("#dash-all tbody").innerHTML = records.length
    ? records.map(r => `<tr>
        <td><b>${esc(r.name)}</b></td><td>${esc(r.renewal)}</td>
        <td>${pill(r.tags)}</td><td>${esc(r.lastCounsel)}</td></tr>`).join("")
    : `<tr><td colspan="4" class="hint">볼트 폴더를 열거나 데모 데이터를 불러오세요</td></tr>`;

  document.querySelectorAll("[data-pick]").forEach(btn => {
    btn.onclick = () => {
      document.getElementById("customer-select").value = btn.dataset.pick;
      switchTab("prompt");
      toast(`${btn.dataset.pick} 선택됨`);
    };
  });
}

async function loadDemoCustomers() {
  try {
    const rows = await fetch("data/demo-customers.json").then(r => r.json());
    customerRecords = {};
    customers = {};
    for (const r of rows) {
      const tagsYaml = JSON.stringify(r.tags);
      const raw = `---\ntype: 고객\n이름: ${r.name}\n연락처: ${r.phone}\n유형태그: ${tagsYaml}\n다음갱신일: ${r.renewal}\n최근상담일: ${r.lastCounsel}\n---\n\n# ${r.name}`;
      ingestCustomerRecord(r.name, raw);
    }
    vaultSource = "demo";
    updateCustomerSelect();
    renderDashboard();
  } catch (e) {
    console.warn("demo load failed", e);
  }
}

function openDB() {
  return new Promise((res, rej) => {
    const r = indexedDB.open(DB_NAME, 1);
    r.onupgradeneeded = () => r.result.createObjectStore(STORE, { keyPath: "id" });
    r.onsuccess = () => res(r.result);
    r.onerror = () => rej(r.error);
  });
}

async function loadDocs() {
  const db = await openDB();
  return new Promise((res) => {
    const tx = db.transaction(STORE, "readonly");
    const req = tx.objectStore(STORE).getAll();
    req.onsuccess = () => { docs = req.result || []; res(docs); };
  });
}

async function saveDoc(doc) {
  const db = await openDB();
  return new Promise((res) => {
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).put(doc);
    tx.oncomplete = () => res();
  });
}

function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }

function tagsForType(type) {
  const m = {
    notes: ["수집/노트", "형식/원문"],
    excel: ["수집/엑셀", "형식/표"],
    image: ["수집/사진", "형식/OCR"],
    audio: ["수집/녹음", "painpoint/녹취정리"],
    reference: ["참조/볼트"],
  };
  return ["수집/자동", ...(m[type] || [])];
}

function toMD(title, body, meta) {
  const fm = { title, tags: meta.tags, source_type: meta.type, collected_at: new Date().toISOString(), ...meta.extra };
  const yaml = Object.entries(fm).map(([k, v]) => {
    if (Array.isArray(v)) return `${k}:\n${v.map(t => `  - ${t}`).join("\n")}`;
    return `${k}: ${v}`;
  }).join("\n");
  return `---\n${yaml}\n---\n\n${body}\n`;
}

async function checkServer() {
  const badge = document.getElementById("server-badge");
  try {
    const r = await fetch("/api/health");
    const j = await r.json();
    if (j.whisper) {
      badge.textContent = "Whisper ON";
      badge.style.background = "var(--teal)";
      window.KV_SERVER = true;
      const vp = await fetch("/api/vault-path").then(r => r.json()).catch(() => ({}));
      if (vp.path) window.KV_VAULT_PATH = vp.path;
    }
  } catch {
    badge.textContent = "정적 모드";
    badge.title = "start.bat 또는 KnowledgeVault.exe로 실행하면 Whisper 사용 가능";
    window.KV_SERVER = false;
  }
}

async function whisperCounsel() {
  const file = document.getElementById("audio-input").files[0];
  const customer = document.getElementById("counsel-customer").value.trim();
  const log = document.getElementById("whisper-log");
  if (!file) return toast("녹음 파일을 선택하세요");
  if (!customer) return toast("고객명을 입력하세요");
  if (!window.KV_SERVER) return toast("KnowledgeVault.exe 또는 kv-portable\\start.bat 으로 실행하세요");

  log.style.display = "block";
  log.textContent = "Whisper 변환 중... (첫 실행 시 모델 다운로드로 1~3분 걸릴 수 있음)";

  const fd = new FormData();
  fd.append("file", file);
  fd.append("customer", customer);
  fd.append("channel", "대면");

  try {
    const r = await fetch("/api/counsel", { method: "POST", body: fd });
    const j = await r.json();
    if (!j.ok) throw new Error(j.error || "실패");
    log.textContent = j.transcript || "(완료)";
    document.getElementById("transcript-input").value = j.transcript || "";
    await ingestFile(new File([j.transcript], `전사_${customer}.txt`, { type: "text/plain" }));
    updateStats(); renderRecent();
    toast(`상담기록 저장: ${j.path}`);
    switchTab("prompt");
  } catch (e) {
    log.textContent = "오류: " + e.message;
    toast("변환 실패: " + e.message);
  }
}

async function ingestFile(file) {
  const ext = file.name.split(".").pop().toLowerCase();
  if (["mp3","wav","m4a","ogg","webm","flac"].includes(ext) && window.KV_SERVER) {
    const log = document.getElementById("whisper-log");
    if (log) { log.style.display = "block"; log.textContent = "Whisper 변환 중..."; }
    const fd = new FormData();
    fd.append("file", file);
    const r = await fetch("/api/transcribe", { method: "POST", body: fd });
    const j = await r.json();
    if (log) log.textContent = j.text || j.error || "";
    const text = j.text || "(변환 실패)";
    const title = file.name.replace(/\.[^.]+$/, "");
    const tags = tagsForType("audio");
    const md = toMD(title, `# ${title}\n\n## 변환 텍스트\n\n${text}`, { type: "audio", tags, extra: { whisper: j.engine } });
    const doc = { id: uid(), title, body: md, plain: text, tags: tags.join(","), type: "audio", source: file.name, ts: Date.now() };
    await saveDoc(doc);
    docs.push(doc);
    return doc;
  }
  let type = "notes", body = "", extra = {};
  const ext2 = file.name.split(".").pop().toLowerCase();

  if (["txt", "md", "markdown"].includes(ext2)) {
    body = await file.text();
    if (file.name.includes("전사") || file.name.includes("상담")) type = "audio";
  } else if (["xlsx", "xls"].includes(ext2)) {
    type = "excel";
    const buf = await file.arrayBuffer();
    const wb = XLSX.read(buf);
    const parts = [];
    wb.SheetNames.forEach(name => {
      const rows = XLSX.utils.sheet_to_json(wb.Sheets[name], { header: 1 });
      parts.push(`## 시트: ${name}\n\n` + rows.map(r => "| " + r.join(" | ") + " |").join("\n"));
    });
    body = parts.join("\n\n");
  } else if (["png", "jpg", "jpeg", "webp"].includes(ext2)) {
    type = "image";
    body = `(이미지: ${file.name})\n\n브라우저 OCR은 Tesseract.js 추가 설치 시 가능합니다.\n지금은 파일명과 메모를 적어 두세요.`;
    extra.image_note = file.name;
  } else {
    body = await file.text().catch(() => "(읽기 실패)");
  }

  const title = file.name.replace(/\.[^.]+$/, "");
  const tags = tagsForType(type);
  const md = toMD(title, `# ${title}\n\n## 내용\n\n${body}`, { type, tags, extra });
  const doc = { id: uid(), title, body: md, plain: body, tags: tags.join(","), type, source: file.name, ts: Date.now() };
  await saveDoc(doc);
  docs.push(doc);
  return doc;
}

function searchDocs(q) {
  if (!q.trim()) return [];
  const terms = q.toLowerCase().split(/\s+/);
  return docs.map(d => {
    const text = (d.title + " " + d.plain + " " + d.tags).toLowerCase();
    const score = terms.reduce((s, t) => s + (text.includes(t) ? 1 : 0), 0);
    return { ...d, score };
  }).filter(d => d.score > 0).sort((a, b) => b.score - a.score);
}

function snippet(text, q, len = 120) {
  const i = text.toLowerCase().indexOf(q.toLowerCase());
  if (i < 0) return text.slice(0, len) + "...";
  const start = Math.max(0, i - 40);
  return "..." + text.slice(start, start + len) + "...";
}

async function loadVaultDir() {
  if (!window.showDirectoryPicker) {
    toast("Chrome/Edge에서만 볼트 폴더 열기 지원");
    return;
  }
  const dir = await showDirectoryPicker();
  customers = {};
  products = "";
  let vaultCount = 0;

  async function walk(entry, pathPrefix = "") {
    if (entry.kind === "file" && entry.name.endsWith(".md") && !entry.name.startsWith("_")) {
      const file = await entry.getFile();
      const text = await file.text();
      const rel = pathPrefix + entry.name;
      if (rel.includes("고객DB")) {
        ingestCustomerRecord(entry.name.replace(".md", ""), text);
      }
      if (rel.includes("상품DB")) {
        products += `\n### ${entry.name}\n${text}\n`;
      }
      const doc = {
        id: uid(), title: entry.name.replace(".md", ""), body: text, plain: text,
        tags: "참조/볼트," + (rel.includes("고객DB") ? "참조/고객DB" : rel.includes("상품DB") ? "참조/상품DB" : "참조"),
        type: "reference", source: rel, ts: Date.now(),
      };
      await saveDoc(doc);
      docs.push(doc);
      vaultCount++;
    }
    if (entry.kind === "directory") {
      for await (const child of entry.values()) await walk(child, pathPrefix + entry.name + "/");
    }
  }

  for await (const entry of dir.values()) await walk(entry, "");
  vaultSource = "vault";
  updateCustomerSelect();
  updateStats();
  renderRecent();
  renderDashboard();
  toast(`볼트 ${vaultCount}개 문서 인덱스 완료`);
}

function updateCustomerSelect() {
  const sel = document.getElementById("customer-select");
  sel.innerHTML = '<option value="">— 고객 선택 —</option>';
  Object.keys(customers).sort().forEach(name => {
    const o = document.createElement("option");
    o.value = name; o.textContent = name;
    sel.appendChild(o);
  });
}

async function buildPack(mode) {
  const sel = document.getElementById("customer-select");
  const target = (sel && sel.value) || "";
  const transcript = document.getElementById("transcript-input").value;
  if (mode !== "counsel" && !target) return toast("고객을 선택하세요");
  const out = document.getElementById("prompt-output");
  out.innerHTML = '<p class="hint">⏳ 생성 중…</p>';
  try {
    const r = await fetch("/api/pack", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, target, transcript }),
    });
    const d = await r.json();
    if (!r.ok) { out.innerHTML = `<p class="hint">오류: ${esc(d.error || "")}</p>`; return; }
    if (d.answer) {
      out.innerHTML = `<h3>🤖 자동 생성 (LLM)</h3>` + renderAnswer(d.answer);
    } else {
      out.innerHTML = `<h3>프롬프트 — 외부 AI에 복사</h3><div class="prompt-box" id="pack-text">${esc(d.prompt)}</div><button class="btn" id="btn-copy">📋 복사</button>`;
      const cp = document.getElementById("btn-copy");
      if (cp) cp.onclick = () => { navigator.clipboard.writeText(d.prompt); toast("복사됨"); };
    }
  } catch {
    out.innerHTML = '<p class="hint">API 연결 실패 — 서버(웹시작.bat)로 실행해야 합니다.</p>';
  }
}

function esc(s) { return s.replace(/&/g,"&amp;").replace(/</g,"&lt;"); }

function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg; t.style.display = "block";
  setTimeout(() => t.style.display = "none", 2500);
}

function updateStats() {
  document.getElementById("stat-docs").textContent = docs.filter(d => d.type !== "reference").length;
  document.getElementById("stat-vault").textContent = docs.filter(d => d.type === "reference").length;
}

function renderRecent() {
  const el = document.getElementById("recent-list");
  const recent = [...docs].sort((a, b) => b.ts - a.ts).slice(0, 12);
  el.innerHTML = recent.map(d => `
    <div class="file-item">
      <span><b>${d.title}</b> <span class="tags">${d.tags}</span></span>
      <small>${d.source}</small>
    </div>`).join("");
}

function renderPain() {
  const grid = document.getElementById("pain-grid");
  if (!grid) return;
  grid.innerHTML = PAIN_POINTS.map(p => `
    <div class="pain-card">
      <h3>${p.chip}</h3>
      <div class="time">${p.asis} → <b style="color:var(--teal)">${p.tobe}</b></div>
      <button class="btn secondary" style="margin-top:8px" data-goto="${p.tab}">이동</button>
    </div>`).join("");
  document.querySelectorAll("[data-goto]").forEach(btn => {
    btn.onclick = () => switchTab(btn.dataset.goto);
  });
}

function switchTab(name) {
  document.querySelectorAll(".tabs button").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".panel").forEach(p => p.classList.toggle("active", p.id === `panel-${name}`));
  if (name === "dashboard") renderDashboard();
}

function downloadBlob(content, filename, type = "text/plain") {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = filename;
  a.click();
}

function exportAll() {
  docs.filter(d => d.type !== "reference").forEach((d, i) => {
    setTimeout(() => downloadBlob(d.body, `${d.title}.md`, "text/markdown"), i * 200);
  });
  toast(`${docs.filter(d => d.type !== "reference").length}개 MD 다운로드 시작`);
}

// --- init ---
document.querySelectorAll(".tabs button").forEach(btn => {
  btn.onclick = () => switchTab(btn.dataset.tab);
});

const drop = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
drop.onclick = () => fileInput.click();
drop.ondragover = e => { e.preventDefault(); drop.classList.add("drag"); };
drop.ondragleave = () => drop.classList.remove("drag");
drop.ondrop = async e => {
  e.preventDefault(); drop.classList.remove("drag");
  for (const f of e.dataTransfer.files) await ingestFile(f);
  updateStats(); renderRecent();
  toast("수집 완료");
};
fileInput.onchange = async () => {
  for (const f of fileInput.files) await ingestFile(f);
  fileInput.value = "";
  updateStats(); renderRecent();
  toast("수집 완료");
};

const _on = (id, fn) => { const el = document.getElementById(id); if (el) el.onclick = fn; };
_on("btn-pick-vault", loadVaultDir);
_on("btn-home-vault", loadVaultDir);
document.querySelectorAll("[data-goto-tab]").forEach(btn => {
  btn.onclick = () => switchTab(btn.dataset.gotoTab);
});
_on("btn-paste-transcript", () => {
  switchTab("prompt");
  document.getElementById("transcript-input")?.focus();
});
_on("btn-whisper", whisperCounsel);

document.getElementById("search-input").oninput = e => {
  const hits = searchDocs(e.target.value);
  document.getElementById("search-results").innerHTML = hits.length ? hits.map(h => `
    <div class="search-hit">
      <h4>${h.title} <small style="color:var(--muted)">${h.source}</small></h4>
      <div class="snip">${snippet(h.plain, e.target.value)}</div>
      <div class="tags">${h.tags}</div>
    </div>`).join("") : '<p class="hint">결과 없음</p>';
};

document.querySelectorAll("[data-pack]").forEach(btn => {
  btn.onclick = () => buildPack(btn.dataset.pack);
});

document.getElementById("btn-export-all").onclick = exportAll;
document.getElementById("btn-export-json").onclick = () => downloadBlob(JSON.stringify(docs), "kv-backup.json", "application/json");
document.getElementById("btn-import-json").onclick = () => document.getElementById("import-json").click();
document.getElementById("import-json").onchange = async e => {
  const text = await e.target.files[0].text();
  const imported = JSON.parse(text);
  for (const d of imported) await saveDoc(d);
  docs = [...docs, ...imported];
  updateStats(); renderRecent();
  toast("백업 복원 완료");
};

// --- 프로파일(카테고리) ---
async function loadProfile() {
  try {
    const p = await fetch("/api/profile").then(r => r.json());
    if (!p || !p.category) return;
    const b = document.getElementById("profile-badge");
    if (b) b.textContent = p.category;            // 배지는 카테고리만 (중복 제거)
    const sp = document.getElementById("settings-profile");
    const f = p.folders || {};
    if (sp) sp.textContent = `현재: ${p.category} · 폴더 ${f.entity_db}/${f.catalog_db}/${f.records}`;
    const sel = document.getElementById("settings-category");
    if (sel && p.active) sel.value = p.active;
  } catch { /* 정적 서버면 무시 */ }
}

async function setCategory(profileKey) {
  try {
    const r = await fetch("/api/profile", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile: profileKey }),
    });
    const d = await r.json();
    if (r.ok && d.ok) {
      toast(`카테고리 변경됨 → ${profileKey}`);
      await loadProfile();
      await loadServerDashboard();
    } else { toast("변경 실패: " + (d.error || "")); }
  } catch { toast("API 연결 실패"); }
}

// --- 대시보드 (백엔드 고객DB 집계 — Obsidian 불필요) ---
async function loadServerDashboard() {
  try {
    const d = await fetch("/api/dashboard").then(r => r.json());
    if (!d || d.total === undefined) return false;
    const stats = document.getElementById("dash-stats");
    if (stats) stats.innerHTML =
      `<div class="stat"><b>${d.total}</b>${esc(d.entity_label)} 수</div>` +
      `<div class="stat"><b>${d.renewal_soon.length}</b>갱신 임박(60일)</div>` +
      Object.entries(d.by_tag || {}).map(([t, n]) => `<div class="stat"><b>${n}</b>${esc(t)}</div>`).join("");
    const rt = document.querySelector("#dash-renewal tbody");
    if (rt) rt.innerHTML = d.renewal_soon.length ? d.renewal_soon.map(r =>
      `<tr><td>${esc(r.name)}</td><td>${esc(r.next_date)} (D-${r._days})</td><td>${esc(r.tags)}</td><td>${esc(r.contact)}</td><td></td></tr>`).join("")
      : '<tr><td colspan="5" class="hint">갱신 임박 없음</td></tr>';
    const at = document.querySelector("#dash-all tbody");
    if (at) at.innerHTML = d.all.map(r =>
      `<tr><td>${esc(r.name)}</td><td>${esc(r.next_date)}</td><td>${esc(r.tags)}</td><td>${esc(r.contact)}</td></tr>`).join("");
    // 수동 프롬프트용 고객 선택 채우기
    const cs = document.getElementById("customer-select");
    if (cs && d.all.length) cs.innerHTML = '<option value="">— 고객 선택 —</option>' +
      d.all.map(r => `<option value="${esc(r.name)}">${esc(r.name)}</option>`).join("");
    return true;
  } catch { return false; }
}

// --- AI 질문 (LLM 자동 답변) ---
async function checkAskLLM() {
  const el = document.getElementById("ask-llm-state");
  const ss = document.getElementById("settings-status");
  let txt, bg;
  try {
    const h = await fetch("/api/health").then(r => r.json());
    if (h.llm_available) { txt = `🤖 자동 모드 — LLM 연결됨 (${h.model || "LLM"})`; bg = "var(--emerald)"; }
    else { txt = "✋ 수동 모드 — LLM 없음 (프롬프트 복사해 외부 AI에 붙여넣기)"; bg = "var(--amber)"; }
  } catch {
    txt = "⚠️ API 없음 — 서버(웹시작.bat)로 실행해야 합니다"; bg = "var(--accent)";
  }
  if (el) { el.textContent = txt.replace(/^[🤖✋⚠️] /, ""); el.style.background = bg; }
  if (ss) { ss.textContent = txt; ss.style.background = bg; ss.style.color = "#fff"; }
}

function renderAnswer(text) {
  const safe = esc(text || "").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n/g, "<br>");
  return `<div class="prompt-box" style="white-space:normal;line-height:1.6">${safe}</div>`;
}

async function doAsk() {
  const q = document.getElementById("ask-input").value.trim();
  if (!q) { toast("질문을 입력하세요"); return; }
  const ansEl = document.getElementById("ask-answer");
  const srcEl = document.getElementById("ask-sources");
  ansEl.style.display = "block";
  ansEl.innerHTML = '<p class="hint">⏳ 자료 검색 + 답변 생성 중…</p>';
  srcEl.innerHTML = "";
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, top: 5 }),
    });
    const data = await res.json();
    if (!res.ok) { ansEl.innerHTML = `<p class="hint">오류: ${esc(data.error || "")}</p>`; return; }
    if (data.answer) {
      ansEl.innerHTML = "<h3>🤖 자동 답변</h3>" + renderAnswer(data.answer);
    } else {
      ansEl.innerHTML = '<p class="hint">LLM이 꺼져 있어 답변이 없습니다. 검색된 자료를 참고하거나 AI작업큐 프롬프트를 AI에 붙여넣으세요.</p>';
    }
    const hits = data.hits || [];
    srcEl.innerHTML = hits.length ? "<h3 style='margin-top:16px'>📎 참고 자료</h3>" + hits.map(h => `
      <div class="search-hit">
        <h4>${esc(h.title)}</h4>
        <div class="snip">${esc(h.snippet || "")}</div>
      </div>`).join("") : "";
  } catch (e) {
    ansEl.innerHTML = `<p class="hint">API 연결 실패 — <code>python -m kv serve</code> 로 실행해야 AI 질문이 동작합니다.</p>`;
  }
}

// 자료 업로드 → 서버에서 변환·인덱싱 → 바로 질문 가능
async function uploadForAsk(file) {
  const log = document.getElementById("ask-upload-log");
  log.textContent = `⏳ "${file.name}" 변환·인덱싱 중…`;
  try {
    const dataUrl = await new Promise((res, rej) => {
      const fr = new FileReader();
      fr.onload = () => res(fr.result);
      fr.onerror = rej;
      fr.readAsDataURL(file);
    });
    const r = await fetch("/api/collect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: file.name, data_base64: dataUrl }),
    });
    const d = await r.json();
    if (r.ok && d.ok) {
      log.innerHTML = `✅ <b>${esc(d.file)}</b> 추가됨 (${d.type}, 인덱스 ${d.indexed}건). 이제 아래에 질문하세요!`;
    } else {
      log.textContent = `오류: ${d.error || "변환 실패"}`;
    }
  } catch (e) {
    log.innerHTML = "API 연결 실패 — <code>python -m kv serve</code> (또는 웹시작.bat)로 실행해야 합니다.";
  }
}

const askDrop = document.getElementById("ask-drop");
const askFile = document.getElementById("ask-file");
if (askDrop && askFile) {
  askDrop.onclick = () => askFile.click();
  askDrop.ondragover = e => { e.preventDefault(); askDrop.classList.add("drag"); };
  askDrop.ondragleave = () => askDrop.classList.remove("drag");
  askDrop.ondrop = async e => {
    e.preventDefault(); askDrop.classList.remove("drag");
    for (const f of e.dataTransfer.files) await uploadForAsk(f);
  };
  askFile.onchange = async () => {
    for (const f of askFile.files) await uploadForAsk(f);
    askFile.value = "";
  };
}

// URL 가져오기 → 변환·인덱싱
async function fetchUrl() {
  const url = document.getElementById("ask-url").value.trim();
  const log = document.getElementById("ask-upload-log");
  if (!url) { toast("URL을 입력하세요"); return; }
  log.textContent = `⏳ "${url}" 가져오는 중…`;
  try {
    const r = await fetch("/api/fetch-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const d = await r.json();
    if (r.ok && d.ok) {
      log.innerHTML = `✅ <b>${esc(d.title)}</b> 가져옴 (${d.chars}자, 인덱스 ${d.indexed}건). 이제 질문하세요!`;
    } else {
      log.textContent = `오류: ${d.error || "가져오기 실패"}`;
    }
  } catch (e) {
    log.innerHTML = "API 연결 실패 — 서버(웹시작.bat)로 실행해야 합니다.";
  }
}
const fetchBtn = document.getElementById("btn-fetch-url");
if (fetchBtn) fetchBtn.onclick = fetchUrl;

// 홈 "파일 선택해서 추가" → AI질문 탭으로 이동 + 파일창 바로 열기
const homeAdd = document.getElementById("btn-home-add");
if (homeAdd) homeAdd.onclick = () => {
  switchTab("ask");
  const fi = document.getElementById("ask-file");
  if (fi) fi.click();   // 같은 클릭 제스처 안에서 파일 선택창 열기
};

const askBtn = document.getElementById("btn-ask");
if (askBtn) askBtn.onclick = doAsk;
const askInput = document.getElementById("ask-input");
if (askInput) askInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) doAsk();
});

// 대시보드 탭 누르면 서버 데이터로 새로고침
document.querySelectorAll('.tabs button[data-tab="dashboard"]').forEach(b => {
  b.addEventListener("click", loadServerDashboard);
});
// 설정: 카테고리(프로파일) 전환
const catSel = document.getElementById("settings-category");
if (catSel) catSel.addEventListener("change", e => setCategory(e.target.value));

await loadDocs();
await loadDemoCustomers();
await checkServer();
await loadProfile();
await checkAskLLM();
await loadServerDashboard();
updateStats();
renderRecent();
renderPain();
renderDashboard();
