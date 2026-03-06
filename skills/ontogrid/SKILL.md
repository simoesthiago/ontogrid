---
name: ontogrid
description: Domain and implementation guide for the OntoGrid Asset Health MVP. Use when working in this repository on API contracts, data model, ingestion, asset health logic, Energy Graph basics, or repo-specific agent workflows.
---

# OntoGrid

Use this skill when changing product docs, backend routes, data models, ingestion logic, alert flows, or the MVP scaffold in this repository.

## Workflow

1. Read [../../docs/API_SPEC.md](../../docs/API_SPEC.md) first for HTTP contracts.
2. Read [../../docs/DATA_MODEL.md](../../docs/DATA_MODEL.md) for entities and tenancy rules.
3. Read [../../docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) only for module boundaries and runtime responsibilities.
4. Keep the MVP v0.1 narrow:
   - REST-only
   - `tenant_id` as the isolation key
   - Neo4j only for topology and impact
   - health score by deterministic rules
   - anomaly v0 by thresholds and rolling z-score

## Repository rules

- Backend lives in `src/backend/app`.
- Frontend lives in `src/frontend/app`.
- Update docs when changing public behavior.
- Do not add GraphQL, WebSocket, Socket.io, forecasting, SMS, or mobile requirements unless the repo docs are updated together.

## References

- Domain: [references/domain.md](references/domain.md)
- API conventions: [references/api-conventions.md](references/api-conventions.md)
- Data model summary: [references/data-model.md](references/data-model.md)
