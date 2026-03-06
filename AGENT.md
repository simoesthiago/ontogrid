# OntoGrid Agent Context

Este arquivo e a referencia canônica para coding agents neste repositório.

## Objetivo do produto

Construir o MVP v0.1 de **Asset Health** para o setor elétrico brasileiro. O produto precisa unificar cadastro de ativos, ingestão de telemetria, health score, alertas, casos e um grafo básico de topologia.

## Decisões fechadas do v0.1

- API HTTP **REST-only**.
- Autenticação JWT com `tenant_id` no token.
- `tenant_id` e a chave de isolamento de dados em todas as entidades operacionais.
- `agent` continua existindo apenas como conceito de domínio do setor elétrico, nao como chave de tenancy.
- Alertas no MVP sao consumidos por polling; real-time fica para fase posterior.
- Neo4j entra no v0.1 somente para topologia, vizinhança e impacto.
- Health score v0 e determinístico, baseado em regras e pesos por tipo de ativo.
- Anomalia v0 usa threshold e rolling z-score; sem Prophet, sem PyOD, sem ensemble.

## Fora do escopo do primeiro corte

- GraphQL.
- WebSocket e Socket.io como contrato oficial.
- Forecasting.
- Mobile dedicado.
- SMS/push.
- Mapa geográfico.
- Workflow rico de casos e knowledge base extensa.

## Ordem de precedência documental

1. [docs/API_SPEC.md](/C:/Users/tsimoe01/coding/ontogrid/docs/API_SPEC.md)
2. [docs/DATA_MODEL.md](/C:/Users/tsimoe01/coding/ontogrid/docs/DATA_MODEL.md)
3. [docs/ARCHITECTURE.md](/C:/Users/tsimoe01/coding/ontogrid/docs/ARCHITECTURE.md)
4. [docs/MVP_ROADMAP.md](/C:/Users/tsimoe01/coding/ontogrid/docs/MVP_ROADMAP.md)
5. [docs/USER_STORIES.md](/C:/Users/tsimoe01/coding/ontogrid/docs/USER_STORIES.md)

## Convenções de implementação

- Backend em FastAPI sob [src/backend/app](/C:/Users/tsimoe01/coding/ontogrid/src/backend/app).
- Frontend em Next.js App Router sob [src/frontend/app](/C:/Users/tsimoe01/coding/ontogrid/src/frontend/app).
- Sempre refletir contratos de API primeiro em `docs/API_SPEC.md` antes de expandir o código.
- Novas tabelas operacionais precisam carregar `tenant_id`.
- Timestamp externo sempre normalizado para ISO-8601 com timezone.
- Preferir documentação curta e executável; evitar blueprints especulativos.

## Domínio

- Ativos alvo iniciais: transformadores, geradores, disjuntores e reatores.
- Fontes iniciais de dados: cadastro de ativos, medições históricas/operacionais via upload e lote JSON.
- Entidades principais do MVP: `tenant`, `user`, `asset`, `measurement_point`, `measurement`, `health_score`, `alert`, `case`, `ingestion_job`.

## Limites do que nao deve ser inferido

- Nao reintroduzir GraphQL, Socket.io ou forecasting sem mudar explicitamente a documentação base.
- Nao trocar `tenant_id` por `agent_id` em modelos operacionais.
- Nao assumir integrações ONS, ANEEL, OPC-UA ou notificações multicanal como prontas no v0.1.
- Nao expandir o MVP com novas features “enterprise” sem atualizar roadmap, stories e API spec em conjunto.
