# LedgerMind — developer tasks
# -----------------------------------------------------------------------------
# Intended for macOS and Linux (GNU/BSD make). Requires Python 3.12+ on PATH as
# `python3`. On Windows, use WSL/Git Bash with this Makefile, or run the same
# commands manually (see README "Development" and CONTRIBUTING.md).
#
# Quick start:
#   make help          # list targets
#   make install-all   # venv + editable install with dev + api extras
#   make dev           # one shot: install-all, then API + web UI (single process)
#   make check         # lint, typecheck, tests
#
# The web stack is one server: FastAPI (JSON under /api) + static UI (/, /static).
# There is no separate Node/Vite dev server.
# -----------------------------------------------------------------------------

SHELL := /bin/sh

VENV          ?= .venv
PY            := $(VENV)/bin/python
PIP           := $(VENV)/bin/pip
LEDGERMIND    := $(VENV)/bin/ledgermind

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show available targets and short descriptions
	@printf "%s\n" "LedgerMind development targets (see Makefile header for details):"
	@grep -E '^[a-zA-Z][a-zA-Z0-9_-]*:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Create $(VENV) if it does not exist (python3 -m venv)
	@test -d "$(VENV)" || python3 -m venv "$(VENV)"
	@echo "Virtualenv: $(VENV)"
	@echo "  Activate: source $(VENV)/bin/activate   (Unix)"
	@echo "            $(VENV)\\Scripts\\activate      (Windows cmd)"

.PHONY: install
install: venv ## Install package in editable mode with [dev] extras (tests, lint, docs, FastAPI for web tests)
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

.PHONY: install-all
install-all: venv ## Install with [all] extras ([dev] + [api]; use for full CLI, web UI, MCP, and tooling)
	$(PIP) install -U pip
	$(PIP) install -e ".[all]"

.PHONY: install-api
install-api: venv ## Minimal install: runtime + [api] only (web UI / FastAPI without full dev stack)
	$(PIP) install -U pip
	$(PIP) install -e ".[api]"

.PHONY: test
test: ## Run pytest (uses the virtualenv’s Python)
	$(PY) -m pytest

.PHONY: lint
lint: ## Run Ruff on src/ and tests/
	$(PY) -m ruff check src tests

.PHONY: typecheck
typecheck: ## Run mypy on src/ledgermind
	$(PY) -m mypy src/ledgermind

.PHONY: check
check: lint typecheck test ## Run lint, typecheck, and tests (typical pre-push)

.PHONY: docs
docs: ## Serve documentation with MkDocs (http://127.0.0.1:8000 by default)
	$(PY) -m mkdocs serve

.PHONY: docs-build
docs-build: ## Build static site to site/
	$(PY) -m mkdocs build

.PHONY: dev
dev: install-all ## One shot: install [all] extras, then run API + browser UI (single Uvicorn process)
	$(LEDGERMIND) serve

.PHONY: serve
serve: ## Run local web UI only: FastAPI + static assets (http://127.0.0.1:8765); needs prior install-all or install-api
	$(LEDGERMIND) serve

.PHONY: precommit
precommit: ## Run pre-commit on all files (install hooks once: pre-commit install)
	$(PY) -m pre_commit run --all-files

.PHONY: clean
clean: ## Remove MkDocs output (site/), .pytest_cache, and **/__pycache__ under the repo
	rm -rf site/ .pytest_cache
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
