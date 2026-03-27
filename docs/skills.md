# Skills

LedgerMind ships an **accountant-style** skill for agents that use the MCP tools:  
`src/ledgermind/skills/accountant_skill/SKILL.md`.

## What it does

- Describes **how** to use each MCP tool (when to call what, milliunits vs currency).
- Encodes **workflows**: debt payoff, savings goals, affordability, monthly review.
- Sets **output style**: direct answer → assumptions → options → risks → next action.
- States **limitations** (read-only, simplified models, heuristics) and **privacy** (no tokens in chat).

## How to use it

1. Run the MCP server: `ledgermind run-mcp` (see [setup](setup.md) and [mcp-tools](mcp-tools.md)).
2. In your client (e.g. ChatGPT with MCP), add the LedgerMind MCP server and attach the skill:
   - **Cursor / Codex:** copy or symlink `SKILL.md` into your skills directory, or paste the contents into a project skill.
   - **ChatGPT:** follow the product’s flow for uploading or linking a skill file that matches your workspace.
3. Point the skill at the same environment as the MCP server (`YNAB_ACCESS_TOKEN`, optional `YNAB_BUDGET_ID`).

## Related docs

- [Example prompts](../examples/prompts.md) — copy-paste starters by workflow.
- [Planning brief (initial_plan)](planning/initial_plan.md) — full product and skill plan.

## Repo layout

```
src/ledgermind/skills/
├── README.md
└── accountant_skill/
    └── SKILL.md
```
