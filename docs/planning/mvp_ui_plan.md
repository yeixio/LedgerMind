# MVP UI plan — local web app with in-UI credentials

This document describes a **minimum viable browser UI** for LedgerMind: read-only YNAB insights, **credentials entered in the UI**, and **no third-party LedgerMind backend**. Implementation is **not** scheduled here; this is the product and technical plan to build against.

---

## 1. Goals

| Goal | Description |
|------|-------------|
| **Lower friction** | Users who do not want to edit `.env` or use the CLI only can connect from a single screen. |
| **Same trust model** | All YNAB traffic still originates **from the user’s machine**; the UI does not ship tokens to a hosted LedgerMind server (there is none in this MVP). |
| **Credential UX** | Collect **YNAB personal access token** and optional **budget ID** in the UI; validate before saving session. |
| **Reuse core** | Snapshot, debt, cash-flow, and related flows call existing **`services/`** and **`YNABClient`** — no duplicate business logic. |

## 2. Non-goals (MVP)

- **YNAB OAuth** — deferred to broader multi-user / cloud work ([phase6_future.md](phase6_future.md) §1). MVP uses PAT only.
- **Hosted multi-tenant SaaS** — out of scope; single-user, local process.
- **Writes to YNAB** — remains read-only (V1 contract).
- **Full parity with CLI/MCP** — MVP may ship **snapshot + budget list + one “analysis” view** first; expand later.

---

## 3. Deployment model (recommended for MVP)

**Local web application:** a small **HTTP server bound to `127.0.0.1`** (not `0.0.0.0` by default), started by a CLI command such as `ledgermind serve` or `ledgermind ui`.

- **Why:** Matches “local-first”; the browser talks only to the loopback interface; credentials are posted to **your** process, not a remote origin.
- **Optional later:** Desktop shell (Tauri/Electron) or `open http://127.0.0.1:8765` from the CLI; same backend.

**Security note:** Anyone who can open `http://127.0.0.1:<port>` on **that** machine can use the session if the server is running. MVP mitigations: bind to `127.0.0.1`, random high port or configurable port, optional **shared secret** (see §6), and clear shutdown.

---

## 4. Credential flow (in-UI)

### 4.1 What the user enters

| Field | Required | Notes |
|-------|----------|--------|
| **YNAB personal access token** | Yes | Password-style input; masked; paste-friendly. |
| **Budget** | Recommended | Either **dropdown after “Test connection”** (preferred) or manual **budget UUID** if API listing fails. |

Optional advanced fields (can be post-MVP or collapsed): **debt metadata file path**, cache toggles — keep CLI/env for power users initially.

### 4.2 Validation flow

1. User submits token (and optional budget id).
2. Backend calls YNAB **GET `/v1/budgets`** (or existing `list_budgets` path) to verify the token.
3. On success: populate budget list; user picks a budget or confirms pre-filled UUID.
4. **Session established** — see §5.

### 4.3 What we never do

- Send the token to any host other than **YNAB’s API** (and only from the local server process).
- Log the token or full `Authorization` header (existing logging redaction rules apply).
- Store the token in **browser `localStorage`** in plain text for MVP; prefer server-side session or OS keychain (§5).

---

## 5. Where credentials live (storage options)

Pick **one** for MVP v1; document the choice in the implementation PR.

| Option | Behavior | Pros | Cons |
|--------|----------|------|------|
| **A — Session memory** | Token held in RAM only; lost on server restart. | Simplest; no disk secret. | User must re-enter after each `ledgermind serve` run. |
| **B — Server-side encrypted cookie / session store** | Opaque session id in cookie; token in server memory or encrypted server-side store. | Good UX for one long-lived session. | Still process-local; restart clears unless combined with C. |
| **C — OS keychain** (e.g. `keyring` on macOS/Windows/Linux secret service) | Persist token after first entry; load on next launch. | Best repeat UX for local app. | Extra dependency; platform quirks. |

**Recommendation:** start with **A** for the smallest MVP, add **C** as soon as “retype token every time” hurts adoption.

**“Disconnect”** must clear session memory and any persisted secret for that profile.

---

## 6. Optional hardening (still MVP-compatible)

- **Loopback secret:** On first start, generate a random token; print `Open: http://127.0.0.1:8765/?key=<secret>` or require `X-LedgerMind-Key` header so other local processes cannot blindly call the API.
- **HTTPS:** Not required for strict `127.0.0.1` HTTP; document that traffic does not leave the machine.

---

## 7. Architecture (conceptual)

```text
Browser (forms, charts)
    -> HTTP JSON (127.0.0.1)
        -> FastAPI app (or equivalent) [new]
            -> Request-scoped credentials (from session)
            -> load_settings() override or context object with token + budget_id
            -> existing services / YNABClient
    -> YNAB API (HTTPS)
```

Today **Settings** is environment-centric ([`config.py`](https://github.com/yeixio/LedgerMind/blob/main/src/ledgermind/config.py)). The UI will need either:

- **Per-request overrides:** build a `Settings` instance (or a slim `Credentials` + `Settings`) with `ynab_access_token` / `ynab_budget_id` from session, **or**
- **Temporary env injection** in the worker (less clean; avoid for tests).

Prefer **explicit dependency injection** into services for the active token so tests stay deterministic.

---

## 8. MVP screens (suggested order)

1. **Connect / Settings** — Token field, “Test connection”, budget selector, “Save & continue”.
2. **Dashboard** — Snapshot summary (cash on budget, assigned/available, TBB, age of money, debt count) — mirrors `GET` snapshot / `get_budget_snapshot`.
3. **Stretch** — **Debts** or **Cash flow** one-pager using existing debt/cashflow services.

Empty states: no session → redirect to Connect. Invalid token → inline error with link to YNAB developer settings.

---

## 9. API sketch (REST, local only)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/session` | Body: `{ "ynab_access_token": "...", "ynab_budget_id": null \| "uuid" }` — validate; create session. |
| `DELETE` | `/api/session` | Logout / clear credentials. |
| `GET` | `/api/me` | Session present? selected budget? (no secrets in response). |
| `GET` | `/api/budgets` | List budgets (uses session token). |
| `GET` | `/api/snapshot?month=YYYY-MM` | Snapshot JSON for UI. |
| `GET` | `/health` | Liveness for smoke tests. |

Names are illustrative; align with OpenAPI and existing domain DTOs.

---

## 10. Frontend stack (choose one)

| Approach | Notes |
|----------|--------|
| **Server-rendered + HTMX** | Few moving parts; fast MVP; weaker for rich charts later. |
| **SPA (Vite + React/Vue/Svelte)** | Separate `ui/` package; better for dashboards and future charts. |

**Recommendation:** If the team wants charts soon, **SPA + FastAPI**; if the goal is “connect + see numbers in a week,” **HTMX + Jinja** is enough.

---

## 11. CLI / packaging

- **Dependency group:** `pip install -e ".[api]"` includes FastAPI + uvicorn ([`pyproject.toml`](https://github.com/yeixio/LedgerMind/blob/main/pyproject.toml)).
- **Entry point:** `ledgermind serve` (defaults: `127.0.0.1:8765`).
- **Docs:** [setup.md](../setup.md#local-web-ui), [privacy.md](../privacy.md#local-web-ui-ledgermind-serve).

---

## 12. Privacy and docs

- [privacy.md](../privacy.md) includes **Local web UI** (loopback, in-memory session, no LedgerMind cloud).
- [cache.md](../cache.md) applies if the UI gains cache toggles (post-MVP).

---

## 13. Milestones (suggested)

| Milestone | Deliverable |
|-----------|-------------|
| **M0** | FastAPI app on `127.0.0.1`; `POST /api/session` validates token; `GET /api/budgets` works. |
| **M1** | Connect + Dashboard pages; snapshot JSON rendered. |
| **M2** | Persist credentials via keyring (optional); disconnect; polish. |
| **M3** | Second analysis view (debts or cashflow); basic tests with mocked YNAB. |

---

## 14. Open questions

- **Port and CORS:** Browser on same origin as API if served by FastAPI static mount; otherwise strict CORS for `127.0.0.1` only.
- **Multiple profiles:** Out of MVP unless trivial (single session is enough).

---

**Summary:** The MVP UI is a **local-only FastAPI (or similar) app** with a **Connect** screen for PAT + budget, **session-scoped credentials**, and **dashboard** built on existing services—no OAuth and no hosted credential store in the first version.
