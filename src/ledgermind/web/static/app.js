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
    const msg = data.detail || data.message || r.statusText || "Request failed";
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

function showConnectError(msg) {
  const el = document.getElementById("connect-error");
  el.textContent = msg;
  el.hidden = !msg;
}

function setMonthDefault() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const el = document.getElementById("month");
  el.value = `${y}-${m}`;
  // Allow roughly current + 2 years of months (YNAB may not have data for all of them).
  const max = new Date(d.getFullYear() + 2, 11, 1);
  el.max = `${max.getFullYear()}-${String(max.getMonth() + 1).padStart(2, "0")}`;
}

function showView(authenticated) {
  document.getElementById("view-connect").hidden = authenticated;
  document.getElementById("view-app").hidden = !authenticated;
}

function fillBudgetSelect(budgets) {
  const sel = document.getElementById("budget");
  sel.innerHTML = "";
  const opt0 = document.createElement("option");
  opt0.value = "";
  opt0.textContent = "— Use YNAB default / first —";
  sel.appendChild(opt0);
  for (const b of budgets || []) {
    const o = document.createElement("option");
    o.value = b.id;
    o.textContent = b.name || b.id;
    sel.appendChild(o);
  }
  sel.disabled = false;
}

async function refreshMe() {
  const me = await api("/api/me");
  const label = document.getElementById("session-label");
  if (!me.authenticated || !me.valid) {
    label.textContent = "";
    return me;
  }
  label.textContent = me.budget_name
    ? `${me.budget_name} · ${me.ynab_budget_id}`
    : me.ynab_budget_id || "Connected";
  return me;
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
  const budgetSel = document.getElementById("budget");
  const ynab_budget_id = budgetSel.value || null;
  const btn = document.getElementById("btn-connect");
  btn.disabled = true;
  try {
    const body = { ynab_access_token: token, ynab_budget_id };
    const res = await api("/api/session", { method: "POST", body: JSON.stringify(body) });
    fillBudgetSelect(res.budgets);
    if (!res.budgets || res.budgets.length === 0) {
      showConnectError("YNAB returned no budgets for this token. Check the token at YNAB developer settings.");
    }
    await refreshMe();
    showView(true);
    setMonthDefault();
    await loadSnapshot();
  } catch (e) {
    showConnectError(e.message || String(e));
  } finally {
    btn.disabled = false;
  }
});

document.getElementById("budget").addEventListener("change", async () => {
  const id = document.getElementById("budget").value;
  if (!id) return;
  try {
    await api("/api/session", {
      method: "PATCH",
      body: JSON.stringify({ ynab_budget_id: id }),
    });
    await refreshMe();
    await loadSnapshot();
  } catch (e) {
    showConnectError(e.message || String(e));
  }
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  await api("/api/session", { method: "DELETE" });
  document.getElementById("token").value = "";
  document.getElementById("budget").innerHTML = "<option value=\"\">— Connect first —</option>";
  document.getElementById("budget").disabled = true;
  showView(false);
  showConnectError("");
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
      showView(true);
      const bud = await api("/api/budgets");
      fillBudgetSelect(bud.budgets);
      await refreshMe();
      await loadSnapshot();
    } else {
      showView(false);
    }
  } catch {
    showView(false);
  }
})();
