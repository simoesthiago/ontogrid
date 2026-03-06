# API conventions

- Source of truth: `docs/API_SPEC.md`.
- Base path: `/api/v1`.
- Auth: bearer JWT.
- `tenant_id` comes from the token.
- Keep product APIs JSON-first; multipart is allowed only for ingestion uploads.
- Keep alert delivery on polling in v0.1.
