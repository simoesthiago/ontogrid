---
name: ontogrid
description: Domain and implementation guide for the OntoGrid Energy Data Hub MVP. Use when working in this repository on public API contracts, canonical data model, regulatory ingestion, Energy Graph basics, copilot behavior, or repo-specific agent workflows.
---

# OntoGrid

Use this skill when changing product docs, backend routes, data models, ingestion logic, graph semantics, copilot flows, or the MVP scaffold in this repository.

## Workflow

1. Read [../../docs/strategy/VISAO_PLATAFORMA_ESTRATEGIA.md](../../docs/strategy/VISAO_PLATAFORMA_ESTRATEGIA.md) first for product direction.
2. Read [../../docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md](../../docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md) for the active MVP scope.
3. Read [../../docs/contracts/API_SPEC.md](../../docs/contracts/API_SPEC.md) for HTTP contracts.
4. Read [../../docs/platform/DATA_MODEL.md](../../docs/platform/DATA_MODEL.md) for public entities and the enterprise boundary.
5. Read [../../docs/platform/ARCHITECTURE.md](../../docs/platform/ARCHITECTURE.md) only for module boundaries and runtime responsibilities.
6. Keep the MVP public and narrow:
   - REST-only
   - ANEEL, ONS and CCEE as initial sources
   - no `tenant_id` in the public core
   - Neo4j for the public Energy Graph
   - copilot grounded in datasets, versions and graph context

## Repository rules

- Backend lives in `src/backend/app`.
- Frontend lives in `src/frontend/app`.
- Update docs when changing public behavior.
- Do not add GraphQL, WebSocket, Socket.io, private client data flows, forecasting, SMS, or mobile requirements unless the repo docs are updated together.

## References

- Domain: [references/domain.md](references/domain.md)
- API conventions: [references/api-conventions.md](references/api-conventions.md)
- Data model summary: [references/data-model.md](references/data-model.md)
