# API conventions

- Source of truth: `docs/contracts/API_SPEC.md`.
- Base path: `/api/v1`.
- Public read APIs do not depend on `tenant_id`.
- Product APIs stay JSON-first.
- Administrative refresh endpoints live under `/api/v1/admin`.
- Copilot responses must stay grounded in datasets, versions and graph metadata.
