# OntoGrid Agent Context

Este arquivo e a referencia canonica para coding agents neste repositorio.

## Objetivo do produto

Construir o MVP publico v1 do **Energy Data Hub** do OntoGrid para o setor eletrico brasileiro. O produto precisa curar e versionar dados publicos de ANEEL, ONS e CCEE, projetar um Energy Graph publico, expor APIs e dashboards e oferecer um copilot analitico grounded nesses dados.

## Decisoes fechadas do MVP publico

- API HTTP **REST-only**.
- Dados publicos sao o nucleo do MVP; nao dependemos de SCADA, ERP, OMS ou CMMS do cliente.
- `tenant_id` nao e a chave central do modelo publico inicial.
- Auth, se existir, serve para conta, favoritos, historico ou limites de uso, nao para isolar o dataset publico.
- Neo4j entra no v1 para ontologia publica, navegacao e relacoes setoriais.
- IA entra como copilot analitico grounded em datasets, metadados e grafo publico.
- Refresh de dados usa pulls agendados, downloads versionados e crawlers especificos.
- O slice enterprise fica para a fase seguinte sob o nome **Vigilancia Operacional de Ativos** e outros apps setoriais.

## Fora do escopo do primeiro corte

- Integracoes privadas de cliente via SCADA, ERP, CMMS, OMS ou GIS.
- Upload manual de dados do cliente como fluxo principal do produto.
- RAG sobre SOPs privados.
- Workflow rico de casos e assistente de campo.
- Classificacao de causas com dados internos de OMS.
- GraphQL.
- WebSocket e Socket.io como contrato oficial.
- Forecasting pesado.
- Mobile dedicado.

## Ordem de precedencia documental

1. [docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md](docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md)
2. [docs/contracts/API_SPEC.md](docs/contracts/API_SPEC.md)
3. [docs/platform/DATA_MODEL.md](docs/platform/DATA_MODEL.md)
4. [docs/platform/ARCHITECTURE.md](docs/platform/ARCHITECTURE.md)
5. [docs/product/MVP_ROADMAP.md](docs/product/MVP_ROADMAP.md)
6. [docs/strategy/PORTFOLIO_E_ROADMAP.md](docs/strategy/PORTFOLIO_E_ROADMAP.md)
7. [docs/platform/DATA_INGESTION.md](docs/platform/DATA_INGESTION.md)
8. [docs/product/USER_STORIES.md](docs/product/USER_STORIES.md)

## Convencoes de implementacao

- Backend em FastAPI sob [src/backend/app](src/backend/app).
- Frontend em Next.js App Router sob [src/frontend/app](src/frontend/app).
- Sempre refletir contratos de API primeiro em `docs/contracts/API_SPEC.md` antes de expandir o codigo.
- Entidades publicas centrais nao carregam `tenant_id` por default; entidades enterprise passam a carregar `tenant_id` na fase seguinte.
- Timestamp externo sempre normalizado para ISO-8601 com timezone.
- Preferir documentacao curta e executavel; evitar blueprints especulativos.

## Dominio

- Fontes iniciais do MVP publico: ANEEL, ONS e CCEE.
- EPE e outras fontes setoriais entram como expansao logo apos o nucleo inicial.
- Entidades principais do MVP publico: `source`, `dataset`, `dataset_version`, `entity`, `entity_alias`, `relation`, `metric_series`, `observation`, `insight_snapshot`.
- Entidades centrais da fase enterprise: `tenant`, `user`, `private_connection`, `asset`, `measurement`, `alert`, `case`.

## Limites do que nao deve ser inferido

- Nao reintroduzir `tenant_id` como pivote universal do modelo publico.
- Nao assumir integracoes SCADA, OMS, ERP ou CMMS como prontas no MVP publico.
- Nao reintroduzir GraphQL, Socket.io ou forecasting sem mudar explicitamente a documentacao base.
- Nao promover apps enterprise para o MVP publico sem atualizar visao, roadmap, API spec e data model em conjunto.

## Regras rapidas

- O baseline oficial do produto e o MVP publico v1 do Energy Data Hub.
- A fonte de verdade dos contratos HTTP e [docs/contracts/API_SPEC.md](docs/contracts/API_SPEC.md).
- `tenant_id` fica reservado para a futura camada enterprise.
- O repo e REST-only no primeiro corte.
- Neo4j no v1 serve ao grafo publico, navegacao e semantica setorial.
