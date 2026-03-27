const MIN_CONNECT_MS = 1100;
const CONNECT_SUCCESS_EXTRA_MS = 450;

/** Last active budget list from API (for “Change budget” without reconnect). */
let cachedBudgets = [];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function api(path, opts = {}) {
  const r = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  const text = await r.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text };
  }
  if (!r.ok) {
    const d = data.detail;
    if (typeof d === "object" && d !== null && d.message) {
      const err = new Error(String(d.message));
      err.needsBudgetChoice = d.needs_budget_choice === true;
      throw err;
    }
    const msg = d || data.message || r.statusText || "Request failed";
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

function showStep(step) {
  const map = {
    connect: "view-connect",
    connecting: "view-connecting",
    budget: "view-budget",
    app: "view-app",
  };
  for (const id of Object.values(map)) {
    const el = document.getElementById(id);
    if (el) el.hidden = true;
  }
  const show = document.getElementById(map[step]);
  if (show) show.hidden = false;
}

function showConnectError(msg) {
  const el = document.getElementById("connect-error");
  el.textContent = msg;
  el.hidden = !msg;
}

function showBudgetError(msg) {
  const el = document.getElementById("budget-error");
  el.textContent = msg;
  el.hidden = !msg;
}

function setMonthDefault() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const el = document.getElementById("month");
  el.value = `${y}-${m}`;
  const max = new Date(d.getFullYear() + 2, 11, 1);
  el.max = `${max.getFullYear()}-${String(max.getMonth() + 1).padStart(2, "0")}`;
}

function fillBudgetPicker(budgets) {
  const sel = document.getElementById("budget-picker");
  sel.innerHTML = "";
  const opt0 = document.createElement("option");
  opt0.value = "";
  const n = (budgets && budgets.length) || 0;
  opt0.textContent = n ? "— Select a budget —" : "— No active budgets —";
  sel.appendChild(opt0);
  for (const b of budgets || []) {
    const o = document.createElement("option");
    o.value = b.id;
    o.textContent = b.name || b.id;
    sel.appendChild(o);
  }
  const btn = document.getElementById("btn-continue-budget");
  btn.disabled = n === 0;
}

async function refreshMe() {
  return api("/api/me");
}

function updateSessionLabel(me) {
  const label = document.getElementById("session-label");
  if (!me || !me.authenticated || !me.valid) {
    label.textContent = "";
    return;
  }
  if (me.needs_budget_choice) {
    label.textContent = "";
    return;
  }
  label.textContent = me.budget_name
    ? `${me.budget_name}`
    : me.ynab_budget_id || "";
}

async function loadSnapshot() {
  const monthEl = document.getElementById("month");
  const month = monthEl.value || null;
  const q = month ? `?month=${encodeURIComponent(month)}` : "";
  const out = document.getElementById("snapshot-out");
  out.textContent = "Loading…";
  try {
    const snap = await api(`/api/snapshot${q}`);
    let text = JSON.stringify(snap, null, 2);
    if (snap && snap._note) {
      text = snap._note + "\n\n" + text;
    }
    out.textContent = text;
  } catch (e) {
    out.textContent = String(e.message || e);
  }
}

async function loadCashflow() {
  const months = document.getElementById("cf-months").value || "6";
  const out = document.getElementById("cashflow-out");
  out.textContent = "Loading…";
  try {
    const data = await api(`/api/cashflow?months=${encodeURIComponent(months)}`);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = String(e.message || e);
  }
}

document.getElementById("form-connect").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  showConnectError("");
  const token = document.getElementById("token").value.trim();
  if (!token) {
    showConnectError("Token is required.");
    return;
  }
  const btn = document.getElementById("btn-connect");
  btn.disabled = true;
  document.getElementById("connect-status").textContent = "Connecting to YNAB…";
  const sub = document.querySelector("#view-connecting .connect-sub");
  if (sub) sub.textContent = "Validating your token";
  showStep("connecting");

  const resPromise = api("/api/session", {
    method: "POST",
    body: JSON.stringify({ ynab_access_token: token, ynab_budget_id: null }),
  });

  try {
    await delay(MIN_CONNECT_MS);
    const res = await resPromise;

    document.getElementById("connect-status").textContent = "Connected";
    if (sub) sub.textContent = "Preparing your budget list…";
    await delay(CONNECT_SUCCESS_EXTRA_MS);

    cachedBudgets = res.budgets || [];
    fillBudgetPicker(cachedBudgets);
    if (!cachedBudgets.length) {
      showBudgetError(
        "No active budgets found (all may be archived). Un-archive one in YNAB or check your token.",
      );
    } else {
      showBudgetError("");
    }
    showStep("budget");
  } catch (e) {
    showConnectError(e.message || String(e));
    showStep("connect");
  } finally {
    btn.disabled = false;
  }
});

document.getElementById("btn-continue-budget").addEventListener("click", async () => {
  const id = document.getElementById("budget-picker").value;
  if (!id) {
    showBudgetError("Select a budget to continue.");
    return;
  }
  showBudgetError("");
  const btn = document.getElementById("btn-continue-budget");
  btn.disabled = true;
  try {
    await api("/api/session", {
      method: "PATCH",
      body: JSON.stringify({ ynab_budget_id: id }),
    });
    const me = await refreshMe();
    updateSessionLabel(me);
    showAppError("");
    showStep("app");
    setMonthDefault();
    await loadSnapshot();
  } catch (e) {
    showBudgetError(e.message || String(e));
  } finally {
    btn.disabled = false;
  }
});

function showAppError(msg) {
  const el = document.getElementById("app-error");
  if (!el) return;
  el.textContent = msg || "";
  el.hidden = !msg;
}

document.getElementById("btn-back-budget").addEventListener("click", async () => {
  showAppError("");
  try {
    await api("/api/session/budget", { method: "DELETE" });
    const me = await refreshMe();
    updateSessionLabel(me);
    fillBudgetPicker(cachedBudgets);
    document.getElementById("budget-picker").value = "";
    document.getElementById("snapshot-out").textContent = "—";
    document.getElementById("cashflow-out").textContent = "—";
    showStep("budget");
  } catch (e) {
    showAppError(e.message || String(e));
  }
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  try {
    await api("/api/session", { method: "DELETE" });
  } catch {
    /* still reset UI */
  }
  document.getElementById("token").value = "";
  cachedBudgets = [];
  fillBudgetPicker([]);
  showConnectError("");
  showBudgetError("");
  showStep("connect");
});

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    const name = btn.getAttribute("data-tab");
    document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === btn));
    document.getElementById("tab-dash").hidden = name !== "dash";
    document.getElementById("tab-cash").hidden = name !== "cash";
  });
});

document.getElementById("btn-refresh-snap").addEventListener("click", () => loadSnapshot());
document.getElementById("btn-cashflow").addEventListener("click", () => loadCashflow());

(async function init() {
  setMonthDefault();
  try {
    const me = await api("/api/me");
    if (me.authenticated && me.valid) {
      const bud = await api("/api/budgets");
      cachedBudgets = bud.budgets || [];
      fillBudgetPicker(cachedBudgets);
      if (me.needs_budget_choice) {
        showStep("budget");
      } else {
        updateSessionLabel(me);
        showStep("app");
        setMonthDefault();
        await loadSnapshot();
      }
    } else {
      showStep("connect");
    }
  } catch {
    showStep("connect");
  }
})();
