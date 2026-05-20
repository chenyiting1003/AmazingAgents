/* Lab UI — fetch outputs + student continuation via /api/continue */

const views = {
  intro: documentElementById("view-intro"),
  transcript: documentElementById("view-transcript"),
  report: documentElementById("view-report"),
  variables: documentElementById("view-variables"),
  leakage: documentElementById("view-leakage"),
  continue: documentElementById("view-continue"),
};

/** @type {string[]} */
let cachedAgents = [];

function documentElementById(id) {
  return document.getElementById(id);
}

function showView(name) {
  Object.entries(views).forEach(([k, el]) => {
    if (!el) return;
    el.hidden = k !== name;
  });
  document.querySelectorAll("nav button[data-view]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === name);
  });
}

async function fetchJson(url, options) {
  const r = await fetch(url, options);
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

async function fetchText(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status}`);
  return r.text();
}

function renderStatus(status) {
  const el = documentElementById("output-status");
  if (!el) return;
  const items = [
    ["Baseline 对话", status.transcript],
    ["总结报告", status.report],
    ["变量摘要", status.variables],
    ["角色越界报告", status.role_leakage],
    ["续聊记录文件", status.continuations],
  ];
  el.innerHTML = items
    .map(
      ([label, ok]) =>
        `<span class="status-pill ${ok ? "status-ok" : "status-miss"}">${label}：${
          ok ? "已有" : "暂无"
        }</span>`
    )
    .join("");
}

function buildAgentCheckboxes(agents) {
  const host = documentElementById("agent-checkboxes");
  if (!host) return;
  if (!agents || !agents.length) {
    host.innerHTML = '<span class="hint">尚无 baseline，无法勾选代表。请先运行 <code>run_minisim</code> 并刷新。</span>';
    return;
  }
  const strong = document.createElement("strong");
  strong.textContent = "本局要发言的代表（可多选；全选 = 与默认「全体成员发言」相同）";
  host.innerHTML = "";
  host.appendChild(strong);
  agents.forEach((a) => {
    const lab = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.value = a;
    cb.name = "agents";
    cb.checked = true;
    lab.appendChild(cb);
    lab.appendChild(document.createTextNode(` ${a}`));
    host.appendChild(lab);
  });
}

function renderTranscript(data) {
  const host = documentElementById("transcript-mount");
  if (!host) return;
  host.innerHTML = "";
  const rounds = data.rounds || [];
  rounds.forEach((r) => {
    const card = document.createElement("div");
    card.className = "round-card";
    const h = document.createElement("h3");
    h.textContent = `第 ${r.round} 轮 · ${r.title}`;
    card.appendChild(h);
    (r.statements || []).forEach((s) => {
      const st = document.createElement("div");
      st.className = "statement";
      const alabel = document.createElement("div");
      alabel.className = "agent";
      alabel.textContent = s.agent;
      st.appendChild(alabel);
      const body = document.createElement("div");
      body.className = "body";
      body.textContent = s.statement || "";
      st.appendChild(body);
      if (s.statement_role_leakage) {
        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `角色边界提示：可能存在越界（${(s.role_leakage_issues || []).join(", ") || "见 JSON"}）`;
        st.appendChild(meta);
      }
      card.appendChild(st);
    });
    if (r.summary) {
      const sum = document.createElement("div");
      sum.className = "summary-box";
      sum.textContent = `本轮摘要：${r.summary}`;
      card.appendChild(sum);
    }
    host.appendChild(card);
  });
}

function renderContinuations(data) {
  const host = documentElementById("continuation-history");
  if (!host) return;
  const entries = data.entries || [];
  if (!entries.length) {
    host.innerHTML = '<p class="hint">还没有任何续聊记录。在上方提交指令后即会出现在这里。</p>';
    return;
  }
  host.innerHTML = "";
  [...entries].reverse().forEach((ent) => {
    const div = document.createElement("div");
    div.className = "continuation-entry";
    const meta = document.createElement("div");
    meta.className = "continuation-meta";
    meta.textContent = `${ent.timestamp || ""} · 指定代表：${(ent.agents_requested || []).join("、")}`;
    div.appendChild(meta);
    const ins = document.createElement("div");
    ins.className = "continuation-instruction";
    ins.textContent = `指令：${ent.instruction || ""}`;
    div.appendChild(ins);
    const res = ent.result || {};
    if (res.round_title) {
      const t = document.createElement("h4");
      t.style.margin = "0.5rem 0";
      t.textContent = res.round_title;
      div.appendChild(t);
    }
    (res.statements || []).forEach((s) => {
      const st = document.createElement("div");
      st.className = "statement";
      const ag = document.createElement("div");
      ag.className = "agent";
      ag.textContent = s.agent || "";
      st.appendChild(ag);
      const body = document.createElement("div");
      body.className = "body";
      body.textContent = s.statement || "";
      st.appendChild(body);
      div.appendChild(st);
    });
    if (res.round_summary) {
      const sum = document.createElement("div");
      sum.className = "summary-box";
      sum.textContent = res.round_summary;
      div.appendChild(sum);
    }
    host.appendChild(div);
  });
}

async function loadContinuationHistory() {
  try {
    const d = await fetchJson("/api/outputs/continuations");
    renderContinuations(d);
  } catch {
    const host = documentElementById("continuation-history");
    if (host) host.innerHTML = '<p class="hint">无法读取续聊记录（若尚未续聊属正常）。</p>';
  }
}

async function refreshAll() {
  try {
    const status = await fetchJson("/api/outputs/status");
    renderStatus(status);
    if (status.transcript) {
      const data = await fetchJson("/api/outputs/transcript");
      cachedAgents = data.agents || [];
      buildAgentCheckboxes(cachedAgents);
      renderTranscript(data);
    } else {
      cachedAgents = [];
      buildAgentCheckboxes([]);
      const host = documentElementById("transcript-mount");
      if (host) {
        host.innerHTML =
          '<p class="hint">尚无 transcript。请在项目根目录运行 <code>python scripts/student_run_lab.py</code> 或 <code>python scripts/run_minisim.py</code> 后点击「刷新结果」。</p>';
      }
    }
    const repEl = documentElementById("report-body");
    if (repEl) {
      if (status.report) repEl.textContent = await fetchText("/api/outputs/report");
      else repEl.textContent = "暂无报告文件。";
    }
    const varEl = documentElementById("variables-body");
    if (varEl) {
      if (status.variables) {
        const v = await fetchJson("/api/outputs/variables");
        varEl.textContent = JSON.stringify(v, null, 2);
      } else varEl.textContent = "{}";
    }
    const leakEl = documentElementById("leakage-body");
    if (leakEl) {
      if (status.role_leakage) leakEl.textContent = await fetchText("/api/outputs/role_leakage");
      else leakEl.textContent = "暂无文件。";
    }
    await loadContinuationHistory();
  } catch (e) {
    documentElementById("output-status").innerHTML =
      `<span class="status-pill status-miss">无法连接 API（${e.message}）。请确认本页面是通过 <code>python scripts/serve_lab_ui.py</code> 打开的，不要直接用磁盘上的 index.html 双击打开。</span>`;
  }
}

document.querySelectorAll("nav button[data-view]").forEach((btn) => {
  btn.addEventListener("click", () => showView(btn.dataset.view));
});

documentElementById("btn-refresh")?.addEventListener("click", refreshAll);

documentElementById("form-continue")?.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const st = documentElementById("continue-status");
  const btn = documentElementById("btn-continue");
  const instrEl = documentElementById("instr-text");
  const instr = (instrEl?.value || "").trim();
  if (!instr) {
    if (st) st.textContent = "请填写指令。";
    return;
  }
  if (!cachedAgents.length) {
    if (st) st.textContent = "请先生成 baseline（model_un_transcript.json）并点击刷新。";
    return;
  }
  const checked = Array.from(document.querySelectorAll('#view-continue input[name="agents"]:checked')).map((c) => c.value);
  if (!checked.length) {
    if (st) st.textContent = "请至少勾选一名代表。";
    return;
  }
  const body = { instruction: instr };
  if (checked.length < cachedAgents.length) {
    body.agents = checked;
  }
  if (st) st.textContent = "正在请求大模型，请稍候（会产生 API 费用）…";
  if (btn) btn.disabled = true;
  try {
    const r = await fetch("/api/continue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const res = await r.json();
    if (res.ok) {
      if (st) st.textContent = "已生成并保存。见下方「已保存的续聊记录」。";
      await refreshAll();
    } else {
      if (st) st.textContent = `未成功：${res.error || JSON.stringify(res)}`;
    }
  } catch (e) {
    if (st) st.textContent = `请求失败：${e.message}`;
  } finally {
    if (btn) btn.disabled = false;
  }
});

showView("intro");
refreshAll();
