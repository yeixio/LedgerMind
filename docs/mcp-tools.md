# MCP tools (V1)

Run the server:

```bash
ledgermind run-mcp
```

Configure your MCP client (e.g. ChatGPT Desktop) to launch this command with `YNAB_ACCESS_TOKEN` (and optional `YNAB_BUDGET_ID`) in the environment.

**Units:** Unless noted, money fields are **YNAB milliunits** (`1000` = `1.00` in the budget currency).

**Disclaimer:** Outputs are planning models with explicit assumptions—not tax, legal, or investment advice.

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
