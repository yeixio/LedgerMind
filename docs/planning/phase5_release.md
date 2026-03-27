# Phase 5 — Polish and release readiness

This document captures **release-oriented** work: documentation depth, contributor workflow, and **privacy default verification** (no telemetry; local-first).

## Contributor workflow

- **Issues:** [Bug report](https://github.com/yeixio/LedgerMind/blob/main/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature request](https://github.com/yeixio/LedgerMind/blob/main/.github/ISSUE_TEMPLATE/feature_request.md) templates under `.github/ISSUE_TEMPLATE/`.
- **Pull requests:** [PR template](https://github.com/yeixio/LedgerMind/blob/main/.github/pull_request_template.md) at `.github/pull_request_template.md`.

## Privacy defaults verification (V1)

Verified behaviors for a stock install:

| Item | Expected | Notes |
|------|----------|--------|
| Telemetry / analytics | None | No third-party analytics in code paths |
| Default cache | Off | `LEDGERMIND_CACHE_ENABLED` defaults to `false` |
| Token handling | Env / `.env` only | Not committed; redacted in log formatter |
| Default log level | `INFO` | Not transaction-level by default |
| Debug logging | Opt-in | `LEDGERMIND_DEBUG_LOG=true` only when explicitly set |
| MCP | Read-only tools | No YNAB write endpoints in V1 |

See [privacy](../privacy.md), [cache](../cache.md), and [SECURITY](https://github.com/yeixio/LedgerMind/blob/main/SECURITY.md) in the repository.

## Docs map (release)

| Doc | Role |
|-----|------|
| [index](../index.md) | Entry |
| [setup](../setup.md) | Install (under 15 minutes) |
| [architecture](../architecture.md) | Layers and money units |
| [privacy](../privacy.md) | Data flows and threat notes |
| [cache](../cache.md) | Optional SQLite (present vs future) |
| [mcp-tools](../mcp-tools.md) | Tool reference |
| [skills](../skills.md) | Accountant skill |

## Sample artifacts

- Config: `examples/sample-configs/debt-metadata.example.yaml`
- Example tool-style output: `examples/sample-outputs/`

**Phase 5 exit:** public release candidate with templates, verified privacy defaults, and consolidated docs.
