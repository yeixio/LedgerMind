# Phase 6 — Future work (design; not V1)

LedgerMind V1 is **read-only**, **local-first**, and **personal-token** based. Phase 6 tracks **possible** directions **after** a stable V1. Nothing here is committed on a timeline; items are **design notes** for discussion.

---

## 1. OAuth and multi-user / cloud

**Goal:** Let multiple users use a hosted LedgerMind without sharing one YNAB personal access token.

**Design considerations**

- YNAB OAuth app registration, redirect URLs, token refresh, and per-user budget scope.
- Tenant isolation: no cross-user data in process memory, cache, or logs.
- Commercial licensing (see root `LICENSE`) if offering a hosted product.

**Risks:** Higher operational and compliance burden; must not weaken V1’s privacy story for self-hosters.

---

## 2. Optional web UI

**Goal:** Browser UI for charts, scenario tables, and budget exploration—still backed by the same services layer.

**Concrete plan / implementation:** [mvp_ui_plan.md](mvp_ui_plan.md) describes the design; **`ledgermind serve`** ships the MVP (loopback, in-UI PAT + budget, in-memory session). OS keychain persistence remains future work.

**Design considerations**

- Same read-only contract unless an explicit “write” phase ships with confirmations.
- Authn/z for any hosted variant; local single-user UI could bind to `127.0.0.1` only.

**Tech:** Often pairs with FastAPI or a separate static frontend; keep API and MCP sharing one service layer to avoid duplication.

---

## 3. Write actions to YNAB (with confirmations)

**Goal:** Category moves, goal edits, or transaction splits from LedgerMind—**only** with strong UX and API safeguards.

**Design considerations**

- Explicit confirm step; idempotent operations; dry-run preview where YNAB API allows.
- Audit log locally (optional) without sending extra data off-device.

**Constraint:** Contradicts current “read-only V1” promise; would be a **major version** with migration guide.

---

## 4. Richer forecasting and modeling

**Ideas**

- Recurring income modeling (payroll cadence vs monthly average).
- Multi-budget support (switch or aggregate views).
- Scenario tables (side-by-side debt or savings options).
- Optional charts in docs or UI.

**Approach:** Extend `services/forecasting.py` and related modules; keep assumptions explicit in outputs.

---

## 5. Plugin ecosystem

**Goal:** Custom analysis modules (e.g. tax-year summaries, FIRE milestones) without forking core.

**Design considerations**

- Stable internal APIs (`services/*`, domain models).
- Sandboxed or import-based plugins; document security expectations for third-party code.

---

## 6. Multi-user abstraction (hosted)

**Goal:** Shared code paths for “single local user” vs “hosted multi-tenant” without `if cloud` scattered everywhere.

**Design considerations**

- Identity and budget context passed into services as an explicit context object.
- Storage: per-user encrypted cache keys if SQLite cache is ever enabled in multi-tenant mode.

---

## Summary

| Theme | Type |
|-------|------|
| OAuth / multi-user | Product + infra |
| Web UI | Product |
| YNAB writes | Product + safety |
| Forecasting / plugins | Engineering depth |
| Multi-tenant abstractions | Architecture |

**Phase 6 exit:** roadmap and tradeoffs documented; implementation deferred until after V1 maintenance window and user demand.
