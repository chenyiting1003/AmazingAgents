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
    ["Baseline transcript", status.transcript],
    ["Summary report", status.report],
    ["Variables summary", status.variables],
    ["Role-leakage report", status.role_leakage],
    ["Continuations file", status.continuations],
  ];
  el.innerHTML = items
    .map(
      ([label, ok]) =>
        `<span class="status-pill ${ok ? "status-ok" : "status-miss"}">${label}: ${
          ok ? "found" : "missing"
        }</span>`
    )
    .join("");
}

function buildAgentCheckboxes(agents) {
  const host = documentElementById("agent-checkboxes");
  if (!host) return;
  if (!agents || !agents.length) {
    host.innerHTML =
      '<span class="hint">No baseline yet; cannot select delegates. Run the baseline cells in <code>Mini_Model_UN_Student_Lab.ipynb</code> (or <code>run_minisim</code>), then refresh.</span>';
    return;
  }
  const strong = document.createElement("strong");
  strong.textContent =
    "Delegates who should speak this round (multi-select; all checked = default full roster)";
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
    h.textContent = `Round ${r.round} · ${r.title}`;
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
        meta.textContent = `Role boundary note: possible leakage (${(s.role_leakage_issues || []).join(", ") || "see JSON"})`;
        st.appendChild(meta);
      }
      card.appendChild(st);
    });
    if (r.summary) {
      const sum = document.createElement("div");
      sum.className = "summary-box";
      sum.textContent = `Round summary: ${r.summary}`;
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
    host.innerHTML = '<p class="hint">No continuations yet. Submit an instruction above to record one here.</p>';
    return;
  }
  host.innerHTML = "";
  [...entries].reverse().forEach((ent) => {
    const div = document.createElement("div");
    div.className = "continuation-entry";
    const meta = document.createElement("div");
    meta.className = "continuation-meta";
    meta.textContent = `${ent.timestamp || ""} · Delegates: ${(ent.agents_requested || []).join(", ")}`;
    div.appendChild(meta);
    const ins = document.createElement("div");
    ins.className = "continuation-instruction";
    ins.textContent = `Instruction: ${ent.instruction || ""}`;
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
    if (host) host.innerHTML = '<p class="hint">Could not load continuations (normal if you have not run any yet).</p>';
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
      const host = document.getElementById("transcript-mount");
      if (host) {
        host.innerHTML =
          '<p class="hint">No transcript yet. Run the baseline cells in <code>Mini_Model_UN_Student_Lab.ipynb</code> (or <code>python scripts/run_minisim.py</code> for debugging), then click <strong>Refresh results</strong>.</p>';
      }
    }
    const repEl = documentElementById("report-body");
    if (repEl) {
      if (status.report) repEl.textContent = await fetchText("/api/outputs/report");
      else repEl.textContent = "No report file yet.";
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
      else leakEl.textContent = "No file yet.";
    }
    await loadContinuationHistory();
  } catch (e) {
    documentElementById("output-status").innerHTML =
      `<span class="status-pill status-miss">Cannot reach API (${e.message}). Serve this page with <code>python scripts/serve_lab_ui.py</code>; do not open <code>index.html</code> directly from disk.</span>`;
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
    if (st) st.textContent = "Please enter an instruction.";
    return;
  }
  if (!cachedAgents.length) {
    if (st) st.textContent = "Generate baseline (model_un_transcript.json) first, then refresh.";
    return;
  }
  const checked = Array.from(document.querySelectorAll('#view-continue input[name="agents"]:checked')).map((c) => c.value);
  if (!checked.length) {
    if (st) st.textContent = "Select at least one delegate.";
    return;
  }
  const body = { instruction: instr };
  if (checked.length < cachedAgents.length) {
    body.agents = checked;
  }
  if (st) st.textContent = "Calling the LLM; please wait (API usage applies)…";
  if (btn) btn.disabled = true;
  try {
    const r = await fetch("/api/continue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const res = await r.json();
    if (res.ok) {
      if (st) st.textContent = "Saved. See “Saved continuations” below.";
      await refreshAll();
    } else {
      if (st) st.textContent = `Failed: ${res.error || JSON.stringify(res)}`;
    }
  } catch (e) {
    if (st) st.textContent = `Request failed: ${e.message}`;
  } finally {
    if (btn) btn.disabled = false;
  }
});

showView("intro");
refreshAll();
