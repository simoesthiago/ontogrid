---
name: ontogrid
description: Domain and implementation guide for the OntoGrid Energy Data Hub MVP. Use when working in this repository on public API contracts, canonical data model, regulatory ingestion, Energy Graph basics, copilot behavior, or repo-specific agent workflows.
---

# OntoGrid

Use this skill when changing product docs, backend routes, data models, ingestion logic, graph semantics, copilot flows, or the MVP scaffold in this repository.

## Workflow

1. Read [../../docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md](../../docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md) first for product direction.
2. Read [../../docs/contracts/API_SPEC.md](../../docs/contracts/API_SPEC.md) for HTTP contracts.
3. Read [../../docs/platform/DATA_MODEL.md](../../docs/platform/DATA_MODEL.md) for public entities and the enterprise boundary.
4. Read [../../docs/platform/ARCHITECTURE.md](../../docs/platform/ARCHITECTURE.md) for module boundaries and runtime responsibilities.
5. Read [../../docs/platform/DATA_INGESTION.md](../../docs/platform/DATA_INGESTION.md) for the local-vs-shared ingestion model.
6. Read [../../docs/datasets/CATALOG_STATUS.md](../../docs/datasets/CATALOG_STATUS.md) for the official repo snapshot of the 345 datasets.
7. Keep the MVP public and narrow:
   - REST-only
   - ANEEL, ONS and CCEE as initial sources
   - no `tenant_id` in the public core
   - Neo4j as support for `Entities`, not a top-level UX promise
   - copilot grounded in datasets, versions and entity context

## Repository rules

- Backend lives in `src/backend/app`.
- Frontend lives in `src/frontend/app`.
- Update docs when changing public behavior.
- Do not add GraphQL, WebSocket, Socket.io, private client data flows, forecasting, SMS, or mobile requirements unless the repo docs are updated together.

## References

- Domain: [references/domain.md](references/domain.md)
- API conventions: [references/api-conventions.md](references/api-conventions.md)
- Data model summary: [references/data-model.md](references/data-model.md)
