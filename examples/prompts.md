# Example prompts (LedgerMind + MCP)

Use with the accountant skill (`src/ledgermind/skills/accountant_skill/SKILL.md`) and `ledgermind run-mcp` (or your client’s MCP config).

Treat answers as **models with assumptions**, not guarantees.

## Debt

- “How long until my credit cards are paid off if I put an extra **$200/month** toward debt? Compare avalanche vs snowball.”
- “Given my YNAB debt accounts, what’s the interest cost difference between avalanche and snowball with **$extra** extra per month?”
- “Which debt should get any extra payment first, and what assumptions are you using?”

## Savings goals

- “Can I save **$10,000** by **November 2027** at my current pace? What monthly contribution would hit that date?”
- “I can save **$300/month** toward a **$5k** emergency fund. How many months to finish, and what if I only save **$250**?”

## Affordability

- “Do I have room for a **$400/month** subscription after keeping my usual buffer?”
- “If my income drops **10%**, what does the next **6 months** of on-budget cash look like?”

## Monthly review

- “Give me a **March** check-in: spending vs last month, overspending, and biggest category moves.”
- “What should I look at first based on last month’s overspending and subscription heuristics?”

## Category / cash flow

- “What were my top spending categories last month, and how did they change vs the prior month?”
- “Show recent transactions for payee **X** and summarize.”

## Subscriptions (heuristic)

- “Any recurring charges that look like they’re creeping up?” (Remember: confirm in YNAB; heuristics can be wrong.)
