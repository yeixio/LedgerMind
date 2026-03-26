LedgerMind — Cursor Build Instructions

Overview

LedgerMind is an open-source, privacy-first AI financial planning assistant that connects to YNAB and gives users a conversational way to analyze debt payoff, savings goals, cash flow, and budget tradeoffs.

This document is the implementation brief for Cursor. It should be treated as the source of truth for the first production-quality open-source version of LedgerMind.

The project must be:
	•	open source
	•	local-first by default
	•	read-only in early phases
	•	well documented
	•	easy to self-host
	•	safe with user financial data
	•	modular enough to support MCP tools, skills, and a future ChatGPT app UI

⸻

Product Goal

Build a tool that lets a user ask questions such as:
	•	How long until I pay off my debt?
	•	What is the fastest payoff strategy?
	•	Can I save $10,000 by November?
	•	How much can I safely spend this month?
	•	What happens if my income drops by 15%?
	•	Which categories are drifting over time?
	•	What should I cut first if I need $400/month?

LedgerMind should not act like generic budgeting software. It should act like a careful financial planning assistant that uses real YNAB data and produces transparent reasoning, assumptions, and scenario comparisons.

⸻

Core Architecture

Implement the system in layers.

YNAB API
  -> LedgerMind backend services
  -> MCP server
  -> ChatGPT client
  -> optional Skill behavior layer
  -> optional future in-chat UI

Layer responsibilities

1. YNAB API layer
Responsible for authenticated communication with YNAB.

2. Domain service layer
Responsible for transforming raw YNAB data into clean domain models and financial calculations.

3. MCP server layer
Responsible for exposing narrow, reliable tools to ChatGPT.

4. Skill layer
Responsible for defining behavioral workflows such as debt payoff analysis, goal planning, and affordability analysis.

5. UI layer (future)
Optional charts, payoff tables, and scenario controls.

⸻

Non-Negotiable Product Principles

Privacy first
	•	No user financial data should leave the user-controlled runtime unless explicitly configured.
	•	Default mode should support local execution.
	•	Do not send raw YNAB transaction dumps to third-party services unnecessarily.
	•	Do not log sensitive data by default.
	•	Secrets must never be committed, printed, or persisted in plaintext outside explicit config.

Read-only first
	•	V1 should not mutate YNAB data.
	•	No transaction edits.
	•	No category reassignments.
	•	No moving money.
	•	No goal updates.

Transparent calculations
	•	Every recommendation must expose assumptions.
	•	Every forecast must indicate that it is a model, not a guarantee.
	•	Distinguish between observed facts and scenario assumptions.

Safe financial framing
	•	LedgerMind is not a CPA, tax preparer, fiduciary, or licensed investment adviser.
	•	Present budgeting guidance, payoff math, and cash-flow modeling.
	•	Avoid presenting legal, tax, or regulated advice as authoritative.

Open-source quality
	•	Clean architecture.
	•	Strong docs.
	•	Strong tests.
	•	Predictable project layout.
	•	Minimal setup friction.

⸻

Recommended Tech Stack

Use Python for the backend and MCP server.

Backend
	•	Python 3.12+
	•	FastAPI
	•	httpx
	•	pydantic
	•	uv or poetry for dependency management

MCP
	•	Python MCP implementation
	•	Tool registration with clear schemas and docstrings

Data
	•	SQLite for optional cache and derived metrics
	•	In-memory mode for lightweight local use

Testing
	•	pytest
	•	pytest-asyncio if needed
	•	respx or similar for HTTP mocking

Tooling
	•	ruff
	•	mypy
	•	pre-commit
	•	mkdocs or Docusaurus for docs
	•	Docker and docker-compose

⸻

Repository Structure

Create the project with a clean, contributor-friendly structure.

ledgermind/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── .env.example
├── pyproject.toml
├── docker-compose.yml
├── Dockerfile
├── docs/
│   ├── index.md
│   ├── architecture.md
│   ├── setup.md
│   ├── privacy.md
│   ├── mcp-tools.md
│   ├── skills.md
│   ├── roadmap.md
│   └── examples.md
├── src/
│   └── ledgermind/
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── ynab_client.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── normalization.py
│       │   └── types.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── snapshot.py
│       │   ├── spending.py
│       │   ├── debt.py
│       │   ├── forecasting.py
│       │   ├── goals.py
│       │   └── subscriptions.py
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── server.py
│       │   ├── registry.py
│       │   └── tools/
│       │       ├── __init__.py
│       │       ├── budget.py
│       │       ├── transactions.py
│       │       ├── debt.py
│       │       ├── goals.py
│       │       └── forecasting.py
│       ├── skills/
│       │   ├── README.md
│       │   └── accountant_skill/
│       │       └── SKILL.md
│       ├── cache/
│       │   ├── __init__.py
│       │   └── sqlite.py
│       └── cli.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── examples/
    ├── prompts.md
    ├── sample-configs/
    └── sample-outputs/


⸻

MVP Scope

Build V1 around read-only data access and planning analysis.

In scope
	•	Authenticate to YNAB using a personal access token
	•	Read budgets, accounts, categories, payees, and transactions
	•	Normalize YNAB data into LedgerMind domain models
	•	Expose core MCP tools
	•	Provide debt payoff simulation
	•	Provide savings goal projections
	•	Provide cash-flow trend analysis
	•	Provide category spending summaries
	•	Provide clear docs and self-host instructions

Out of scope for V1
	•	Writing to YNAB
	•	OAuth multi-user cloud platform
	•	Subscription billing
	•	Bank account integrations outside YNAB
	•	Tax filing or tax advice
	•	Investment optimization
	•	Browser scraping of YNAB

⸻

Functional Requirements

A. YNAB integration

Implement a dedicated YNAB client that:
	•	accepts a personal access token from environment config
	•	supports listing budgets
	•	supports selecting a default budget
	•	fetches accounts
	•	fetches categories and category groups
	•	fetches transactions
	•	fetches payees if useful
	•	handles pagination or batching if required
	•	handles API failures gracefully
	•	respects rate limits

B. Domain normalization

Build a normalization layer that converts raw YNAB objects into stable internal models.

Normalize at least:
	•	account
	•	debt account
	•	category
	•	transaction
	•	budget snapshot
	•	monthly spending summary
	•	goal projection input

All money handling must be consistent. Clearly document units and conversions.

C. Financial analysis services

Implement separate service modules for:

Snapshot service
	•	current month available amounts
	•	current month spending totals
	•	net cash position
	•	simple high-level summary

Spending service
	•	monthly spending by category
	•	trend over N months
	•	average spending by category
	•	drift detection
	•	top spending changes month-over-month

Debt service
	•	identify debt-like accounts
	•	store APR/minimum payment metadata via config if YNAB does not expose all needed fields
	•	simulate avalanche strategy
	•	simulate snowball strategy
	•	estimate payoff date
	•	estimate interest paid
	•	compare strategies

Goal service
	•	estimate months to target amount
	•	compare current contribution vs needed contribution
	•	show best/base/stress scenarios

Forecasting service
	•	project short-term cash flow using recent average income/spending or configured assumptions
	•	support configurable safety buffer
	•	expose assumptions in output

Subscription detection service
	•	infer recurring transactions based on payee, cadence, and amount similarity
	•	flag increases over time

⸻

MCP Tool Plan

Expose a small number of clear, composable tools. Keep responses structured and concise.

Tool design rules
	•	Each tool should do one thing well.
	•	Inputs must be explicit and validated.
	•	Outputs should be structured JSON-friendly objects.
	•	Avoid giant raw dumps unless explicitly requested.
	•	Add human-readable summaries only when helpful.
	•	Include assumptions and caveats where relevant.

V1 MCP tools

get_budget_snapshot
Purpose: Return a high-level picture of current financial state.

Output should include:
	•	selected budget name
	•	as-of date
	•	total cash on budget
	•	total assigned
	•	total available
	•	overspent categories count
	•	credit/debt account summary if possible

get_category_balances
Inputs:
	•	month (optional)

Output should include:
	•	categories
	•	assigned
	•	activity
	•	available
	•	overspent flag

get_recent_transactions
Inputs:
	•	limit
	•	category filter optional
	•	payee filter optional
	•	since date optional

Output should include:
	•	date
	•	payee
	•	amount
	•	category
	•	memo if present

get_spending_by_category
Inputs:
	•	month

Output should include:
	•	category totals
	•	percent of total spending
	•	change vs previous month when available

find_overspending
Inputs:
	•	month optional

Output should include:
	•	overspent categories
	•	amount overspent
	•	notes about likely coverage needed

get_debts
Output should include:
	•	debt accounts
	•	balance
	•	APR if configured
	•	minimum payment if configured
	•	account type

simulate_debt_payoff
Inputs:
	•	strategy: avalanche | snowball
	•	extra_payment: number
	•	monthly_budget_buffer optional

Output should include:
	•	projected payoff date
	•	total interest estimate
	•	monthly schedule summary
	•	assumptions used
	•	warnings if buffer breached

project_savings_goal
Inputs:
	•	target_amount
	•	current_saved optional
	•	monthly_contribution
	•	target_date optional

Output should include:
	•	projected completion date
	•	contribution needed to hit target date if provided
	•	gap analysis
	•	scenario notes

project_cashflow
Inputs:
	•	months
	•	income_adjustment_pct optional
	•	spending_adjustment_pct optional
	•	minimum_buffer optional

Output should include:
	•	projected monthly balances
	•	months at risk
	•	assumptions

find_subscription_creep
Inputs:
	•	lookback_months optional

Output should include:
	•	recurring charge candidates
	•	estimated cadence
	•	amount changes
	•	flagged increases

⸻

Skill Plan

Create a skill that teaches ChatGPT how to act as a careful budget/accounting assistant on top of MCP tools.

The skill should focus on planning behavior, not raw data access.

Skill goals
	•	Ask clarifying questions only when necessary
	•	Prefer using tools over guessing
	•	Separate facts from projections
	•	Show assumptions clearly
	•	Compare multiple options when recommending a strategy
	•	Preserve a configurable emergency buffer
	•	Avoid overly aggressive recommendations

Core workflows to encode

1. Debt payoff workflow
When the user asks about debt:
	1.	Fetch debt accounts and payment assumptions
	2.	Compare avalanche and snowball
	3.	Estimate payoff dates and interest
	4.	Highlight tradeoffs
	5.	Recommend a strategy with explicit assumptions

2. Savings goal workflow
When the user asks about a savings goal:
	1.	Determine current saved amount if available
	2.	Estimate timeline at current contribution
	3.	Estimate contribution needed for target date
	4.	Show downside scenario if spending rises or income falls

3. Affordability workflow
When the user asks if they can afford something:
	1.	Review current month available funds
	2.	Review cash-flow projection
	3.	Check impact on debt payoff and active goals
	4.	Respond with a plain-language recommendation and tradeoffs

4. Monthly review workflow
When the user asks for a monthly check-in:
	1.	Summarize spending vs prior month
	2.	Flag overspending and category drift
	3.	Identify biggest changes
	4.	Suggest 2 to 3 concrete actions

Output style requirements

The skill should encourage outputs with:
	•	direct answer first
	•	assumptions section
	•	options compared
	•	risks/warnings
	•	next best action

⸻

Privacy and Security Requirements

This section is mandatory. Cursor must treat it as a hard requirement.

Default privacy posture
	•	Local-first deployment must be the default documented path.
	•	No hosted backend should be required for self-use.
	•	Do not collect analytics by default.
	•	Do not store raw financial records beyond what is required for caching.

Secrets handling
	•	Load secrets only from environment variables or secure local config.
	•	Never commit secrets.
	•	Never print the YNAB token.
	•	Redact sensitive headers in logs.

Logging
	•	Default log level should avoid transaction-level PII.
	•	Provide a safe logging mode for debugging with masked values.
	•	Never log full memos, account numbers, or tokens.

Caching
	•	If SQLite cache is enabled, document what fields are stored.
	•	Offer a switch to disable persistence entirely.
	•	Add a simple cache clear command.

Data minimization
	•	MCP tools should return only the fields needed.
	•	Summaries should be preferred over full dumps.
	•	Large transaction exports should require explicit invocation.

Safe recommendations
	•	Include disclaimer language in docs and skill instructions that LedgerMind provides educational and planning assistance, not regulated professional advice.

Threat model to document

Document at least these risks:
	•	local machine compromise
	•	exposed environment variables
	•	accidental debug logging
	•	over-broad tool outputs
	•	misuse of write actions in future versions

⸻

Configuration Design

Create a single configuration system with sane defaults.

Required config
	•	YNAB_ACCESS_TOKEN
	•	YNAB_BUDGET_ID or support selecting the first/default budget

Optional config
	•	LEDGERMIND_CACHE_ENABLED=true|false
	•	LEDGERMIND_CACHE_PATH=...
	•	LEDGERMIND_MINIMUM_BUFFER=1000
	•	LEDGERMIND_DEFAULT_LOOKBACK_MONTHS=6
	•	LEDGERMIND_LOG_LEVEL=INFO
	•	LEDGERMIND_DEBT_METADATA_FILE=...

Debt metadata file

Because YNAB data may not always contain everything needed for realistic debt simulations, support an optional local config file like:

accounts:
  visa:
    apr: 24.99
    minimum_payment: 75
  car_loan:
    apr: 6.25
    minimum_payment: 310

This file must be local-only and documented as sensitive.

⸻

CLI Requirements

Provide a simple CLI for local testing and debugging.

Commands
	•	ledgermind doctor
	•	ledgermind list-budgets
	•	ledgermind snapshot
	•	ledgermind debts
	•	ledgermind cashflow --months 6
	•	ledgermind goal --target 5000 --monthly 300
	•	ledgermind clear-cache
	•	ledgermind run-mcp

The CLI should be friendly enough that a developer can confirm the core system works before wiring ChatGPT to it.

⸻

Documentation Requirements

The docs must be excellent. Treat docs as a first-class deliverable.

README.md must include
	•	what LedgerMind is
	•	why it exists
	•	key features
	•	privacy posture
	•	architecture diagram
	•	quickstart
	•	example questions
	•	screenshots or sample outputs later
	•	roadmap
	•	contribution links

docs/setup.md
	•	local install
	•	environment variables
	•	how to create a YNAB personal access token
	•	how to choose a budget
	•	how to run the CLI
	•	how to run the MCP server

docs/privacy.md
	•	what data LedgerMind accesses
	•	what it stores locally
	•	what it never sends by default
	•	how to disable caching and logging
	•	best practices for self-hosting securely

docs/mcp-tools.md
	•	every tool
	•	input schema
	•	output schema
	•	examples
	•	intended use

docs/skills.md
	•	what the skill does
	•	how to install or use it
	•	example prompts
	•	limitations

SECURITY.md
	•	supported versions
	•	how to report a vulnerability
	•	secure deployment notes

CONTRIBUTING.md
	•	local setup
	•	coding style
	•	test commands
	•	commit conventions
	•	issue/PR expectations

⸻

Testing Requirements

Testing should be taken seriously.

Unit tests

Add unit tests for:
	•	normalization
	•	debt payoff calculations
	•	goal projection calculations
	•	subscription detection heuristics
	•	cash-flow forecasting
	•	config loading

Integration tests

Add integration tests for:
	•	YNAB client with mocked API responses
	•	MCP tool output shape
	•	CLI commands

Golden tests

Add golden tests or fixture-based tests for:
	•	debt comparison output
	•	monthly review output structures
	•	affordability analysis structures

Test data
	•	Provide sanitized fixtures only
	•	Do not include real financial data
	•	Include simple and complex budget examples

⸻

Code Quality Requirements

Style
	•	Use type hints everywhere practical
	•	Prefer small functions
	•	Keep business logic out of route handlers/tool registration code
	•	Use pydantic models for validated inputs and outputs

Reliability
	•	Handle missing fields gracefully
	•	Fail clearly on auth/config issues
	•	Use retries cautiously for transient HTTP errors
	•	Make tool responses deterministic where possible

Maintainability
	•	Keep calculation logic in isolated service modules
	•	Avoid tight coupling between MCP layer and YNAB transport layer
	•	Keep internal domain models stable even if YNAB responses change

⸻

Phased Implementation Plan

Phase 1 — Foundation

Goal: working local project skeleton

Tasks:
	1.	Initialize repository and tooling
	2.	Add config, logging, and CLI foundation
	3.	Implement YNAB client
	4.	Implement core domain models
	5.	Add README, LICENSE, CONTRIBUTING, SECURITY

Deliverable:
	•	project boots locally
	•	can authenticate to YNAB
	•	can list budgets and show a snapshot

Phase 2 — Core analysis services

Goal: useful standalone planning engine

Tasks:
	1.	Implement spending summaries
	2.	Implement overspending detection
	3.	Implement debt models and payoff simulation
	4.	Implement goal timeline projection
	5.	Implement cash-flow projection

Deliverable:
	•	CLI can answer core financial planning questions

Phase 3 — MCP server

Goal: ChatGPT can use LedgerMind tools

Tasks:
	1.	Implement MCP server
	2.	Register V1 tools
	3.	Validate structured outputs
	4.	Document all tools
	5.	Add integration tests

Deliverable:
	•	ChatGPT-compatible MCP server with read-only tools

Phase 4 — Skill package

Goal: more consistent accountant-like behavior

Tasks:
	1.	Write SKILL.md
	2.	Add example prompts
	3.	Add workflow guidance for debt, goals, and monthly reviews
	4.	Document limitations and assumptions

Deliverable:
	•	reusable assistant behavior layer

Phase 5 — Polish and open-source readiness

Goal: easy adoption by the community

Tasks:
	1.	Improve docs
	2.	Add Docker support
	3.	Add sample configs
	4.	Add roadmap and issue templates
	5.	Verify privacy defaults

Deliverable:
	•	strong public OSS release candidate

Phase 6 — Future work

Not for V1, but design with these in mind:
	•	OAuth support
	•	optional web UI
	•	write actions with confirmations
	•	richer forecasting models
	•	recurring income modeling
	•	multi-budget support
	•	plugin ecosystem for custom analysis modules

⸻

Suggested Initial GitHub Issues

Create clear starter issues.

Foundation
	•	Setup project scaffold and pyproject
	•	Add config and settings module
	•	Add structured logging with redaction
	•	Implement YNAB client auth and budget listing
	•	Implement CLI doctor command

Domain
	•	Create money and account domain models
	•	Create category and transaction normalization
	•	Add monthly snapshot service
	•	Add spending summary service

Analysis
	•	Implement debt payoff engine
	•	Implement savings goal projection engine
	•	Implement cash-flow projection engine
	•	Implement subscription detection heuristics

MCP
	•	Add MCP server skeleton
	•	Implement get_budget_snapshot tool
	•	Implement get_category_balances tool
	•	Implement simulate_debt_payoff tool
	•	Add tool docs and schema tests

Docs
	•	Write README quickstart
	•	Write privacy document
	•	Write setup document
	•	Write architecture document

⸻

Cursor Execution Instructions

Use these instructions when generating code.

General coding instructions for Cursor
	•	Prefer readability over cleverness.
	•	Write production-quality code with docstrings and type hints.
	•	Keep modules focused and small.
	•	Add tests for all non-trivial logic.
	•	Do not hardcode secrets.
	•	Do not add telemetry or analytics.
	•	Default to safe, privacy-preserving behavior.
	•	Do not implement write access to YNAB in V1.
	•	Keep the project easy to self-host.

When building MCP tools
	•	Expose only read-only tools.
	•	Return structured outputs.
	•	Avoid leaking unnecessary transaction detail.
	•	Include assumptions and caveats for forecast tools.

When building docs
	•	Assume the reader is technical but busy.
	•	Include copy-paste setup examples.
	•	Document limitations honestly.
	•	Add examples of safe deployment and local-only use.

When building financial logic
	•	Make all assumptions explicit.
	•	Keep calculations deterministic.
	•	Separate calculation code from presentation code.
	•	Annotate formulas clearly in comments or docs.

⸻

Acceptance Criteria for V1

LedgerMind V1 is complete when:
	1.	A developer can clone the repo, add a YNAB token, and run LedgerMind locally in under 15 minutes.
	2.	The CLI can display a budget snapshot, debt summary, and at least one forecast.
	3.	The MCP server exposes core read-only tools that work reliably.
	4.	The docs are sufficient for another developer to understand architecture and contribute.
	5.	Privacy defaults are strong and clearly documented.
	6.	No write actions to YNAB exist in V1.
	7.	Test coverage exists for the core financial calculations.
	8.	The skill package exists and documents how LedgerMind should behave as a financial planning assistant.

⸻

Nice-to-Have After V1
	•	richer monthly review summaries
	•	better recurring bill detection
	•	what-if scenario comparison tables
	•	optional charts
	•	better debt metadata UX
	•	import/export of scenario assumptions
	•	multi-user abstraction for future hosted deployments

⸻

Final Direction

Build LedgerMind as a trustworthy, privacy-conscious, read-only financial planning assistant first.

Do not overbuild the first release.

The first successful version should be:
	•	boring in architecture
	•	excellent in docs
	•	strong in privacy
	•	solid in calculations
	•	pleasant to self-host
	•	easy for ChatGPT to use through MCP

After that foundation is stable, the project can grow into a richer open-source AI budgeting platform.