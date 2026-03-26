# Contributing

Thanks for helping improve LedgerMind.

## Local setup

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

- Describe **what** changed and **why** in the PR body.
- Add or update tests for non-trivial logic.
- Update docs or the [planning checklist](docs/planning/checklist.md) when completing planned work.

## License

See [LICENSE](LICENSE). Commercial entities need a separate agreement.
