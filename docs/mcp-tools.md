# MCP tools (V1)

Tool names and handlers are defined in `src/ledgermind/mcp/registry.py` (`V1_TOOL_NAMES`, `register_v1_tools`).

Run the server:

```bash
ledgermind run-mcp
```

Configure your MCP client (e.g. ChatGPT Desktop) to launch this command with `YNAB_ACCESS_TOKEN` (and optional `YNAB_BUDGET_ID`) in the environment.

**Units:** Unless noted, money fields are **YNAB milliunits** (`1000` = `1.00` in the budget currency).

**Disclaimer:** Outputs are planning models with explicit assumptions—not tax, legal, or investment advice.

---

## Stdio MCP — not a URL

LedgerMind’s MCP server uses **stdio** (standard input/output): a **local CLI process** that your app **starts** and talks to over pipes. Implementation: `create_mcp_app().run(transport="stdio")` in `src/ledgermind/mcp/server.py`.

There is **no** `https://…` endpoint to paste for this mode. “Setup” means:

1. Install the package (e.g. `pip install -e ".[dev]"` in a venv).
2. Provide **`YNAB_ACCESS_TOKEN`** (and optionally **`YNAB_BUDGET_ID`**) in the **environment of that process**. LedgerMind loads `.env` from the **current working directory** when the process starts, or you can set variables in your MCP client’s server config.
3. Configure your MCP client with a **command** + **arguments**, not a URL:

| Field | Typical value |
|-------|----------------|
| Command | Full path to the venv binary, e.g. `/path/to/LedgerMind/.venv/bin/ledgermind` |
| Arguments | `run-mcp` |

**Sanity check in a terminal** (venv activated, `.env` with token in the repo root):

```bash
ledgermind run-mcp
```

The process should **block** and wait (that is stdio mode). Press Ctrl+C to stop. Your MCP client runs this same command for you when a conversation uses the connector.

### If ChatGPT only asks for a URL

Some UIs expect **remote** MCP over **HTTP/SSE**. LedgerMind **V1** does **not** ship an HTTP MCP server—only **stdio**. In that case you can:

- Use a client that supports **stdio** MCP and a **command**-based connector (e.g. **Cursor** `mcp.json`, **Claude Desktop** MCP config, or other local agents), or  
- Use the **local web UI** (`ledgermind serve`) or **CLI** for budget data without MCP.

### Example: Cursor-style `mcp.json`

Adjust the command path to your machine; avoid committing real tokens (use env or your client’s secret UI).

```json
{
  "mcpServers": {
    "ledgermind": {
      "command": "/ABSOLUTE/PATH/TO/LedgerMind/.venv/bin/ledgermind",
      "args": ["run-mcp"],
      "env": {
        "YNAB_ACCESS_TOKEN": "paste-or-use-env"
      }
    }
  }
}
```

---

## `get_budget_snapshot`

**Input**

| Field   | Type   | Required | Description        |
|---------|--------|----------|--------------------|
| `month` | string | no       | `YYYY-MM`; default current month context |

**Output (high level):** `budget_id`, `budget_name`, `as_of`, `currency_format_iso`, cash on budget, assigned/available totals, `to_be_budgeted_milliunits`, `age_of_money`, `overspent_category_count`, `debt_accounts`.

---

## `get_category_balances`

**Input:** `month` (optional `YYYY-MM`).

**Output:** `categories[]` with `assigned_milliunits`, `activity_milliunits`, `available_milliunits`, `overspent`.

---

## `get_recent_transactions`

**Input**

| Field            | Type    | Default | Description                          |
|------------------|---------|---------|--------------------------------------|
| `limit`          | integer | 50      | Max rows (capped at 500)             |
| `category_id`    | string  | —       | Filter by YNAB category UUID         |
| `payee_filter`   | string  | —       | Substring match on payee (case fold) |
| `since_date`     | string  | 90d ago | `YYYY-MM-DD`                         |

**Output:** `transactions[]` with `date`, `payee`, `amount_milliunits`, `category_id`, truncated `memo_preview`.

---

## `get_spending_by_category`

**Input:** `month` (`YYYY-MM`) — required.

**Output:** `total_spending_milliunits`, `categories[]` with `spending_milliunits`, `percent_of_total`, `change_vs_prior_month_milliunits`.

---

## `find_overspending`

**Input:** `month` (optional `YYYY-MM`).

**Output:** `overspent_categories[]` with `amount_overspent_milliunits` and short notes.

---

## `get_debts`

**Input:** none (uses `LEDGERMIND_DEBT_METADATA_FILE` when set).

**Output:** `debts[]` with balances, optional `apr_annual_pct` / `minimum_payment_milliunits` from local YAML.

---

## `simulate_debt_payoff`

**Input**

| Field                               | Type    | Description |
|-------------------------------------|---------|-------------|
| `strategy`                          | string  | `avalanche` or `snowball` |
| `extra_payment_milliunits`          | integer | On top of minimums each month |
| `monthly_budget_buffer_milliunits`  | integer | optional; default from `LEDGERMIND_MINIMUM_BUFFER` (whole currency units → milliunits). Warns if total payment exceeds this. |

**Output:** `payoff_months`, `projected_payoff_date`, `total_interest_milliunits`, `monthly_schedule_summary`, `warnings`, `assumptions`.

---

## `project_savings_goal`

**Input:** `target_amount_milliunits`, `monthly_contribution_milliunits`, optional `current_saved_milliunits`, optional `target_date` (`YYYY-MM`).

**Output:** months to goal, projected completion month, `contribution_needed_milliunits_for_target_date`, `gap_analysis`, `warnings`, `assumptions`.

---

## `project_cashflow`

**Input:** `months` (required), optional `income_adjustment_pct`, `spending_adjustment_pct`, `minimum_buffer_milliunits`, `lookback_months`.

**Output:** average income/spending from history, adjusted assumptions, `projected_monthly_balances_milliunits`, `months_at_risk`, `assumptions`.

---

## `find_subscription_creep`

**Input:** optional `lookback_months` (default from settings).

**Output:** `recurring_charge_candidates[]` with cadence estimate, typical amount, change flags, `assumptions`.
