# Contributing

Thanks for helping improve LedgerMind.

## Local setup

### Makefile (macOS / Linux / Git Bash / WSL)

From the repo root:

```bash
make help           # list targets and descriptions (see Makefile header for full notes)
make install-all    # create .venv if needed; pip install -e ".[all]"
pre-commit install  # optional
make check          # ruff + mypy + pytest
```

**Local web UI:** `make dev` installs dependencies then runs the app (API + static UI in one server). After the first install, `make serve` starts the same server without reinstalling. On Windows without `make`, use the manual commands below.

### Manual (any platform)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install   # optional
pytest
ruff check src tests
mypy src/ledgermind
```

## Style

- Python 3.12+, type hints, Pydantic for validated boundaries.
- Prefer small modules; keep YNAB HTTP details in `api/`, calculations in `services/`.
- No secrets, tokens, or real financial data in tests or fixtures.

## Commits and PRs

- Describe **what** changed and **why** in the PR body. GitHub [issue templates](.github/ISSUE_TEMPLATE/) and [PR template](.github/pull_request_template.md) are available for consistency.
- Add or update tests for non-trivial logic.
- Update docs or the [planning checklist](docs/planning/checklist.md) when completing planned work.

## License

See [LICENSE](LICENSE). Commercial entities need a separate agreement.
