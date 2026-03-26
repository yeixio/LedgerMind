# Security

## Supported versions

Security fixes are applied to the latest `main` / release branch. Use the newest tag when deploying.

## Reporting a vulnerability

Please email the maintainers privately (add a contact in the repository README when available). Include steps to reproduce and impact. Do not open a public issue for undisclosed vulnerabilities.

## Deployment notes

- Run **local-first**; avoid exposing tokens on shared machines.
- Never commit `.env` or debt metadata with real account names if that risks your threat model.
- Prefer least-privilege YNAB tokens and rotate if leaked.
