# Arquitetura Técnica - OntoGrid MVP v0.1

Este documento descreve apenas a arquitetura necessária para iniciar a implementação. A fonte de verdade dos contratos HTTP e [API_SPEC.md](/C:/Users/tsimoe01/coding/ontogrid/docs/API_SPEC.md).

## 1. Objetivo arquitetural

Entregar um produto que permita:

- cadastrar ativos por tenant;
- ingerir medições em lote;
- calcular health score v0;
- gerar alertas;
- criar casos simples;
- consultar topologia e impacto no Energy Graph.

## 2. Decisões fechadas

- Monolito modular.
- FastAPI como backend HTTP.
- PostgreSQL 16 + TimescaleDB para dados operacionais e time-series.
- Neo4j 5 para topologia e impacto.
- Redis 7 para cache simples e fila futura.
- Polling HTTP para alertas no v0.1.
- Sem GraphQL e sem WebSocket no primeiro corte.

## 3. Responsabilidade por componente

| Componente | Responsabilidade |
|---|---|
| FastAPI | Auth, CRUD operacional, ingestão, leitura de alertas e casos, rotas de grafo |
| PostgreSQL/TimescaleDB | `tenant`, `user`, `asset`, `measurement_point`, `measurement`, `health_score`, `alert`, `case`, `ingestion_job` |
| Neo4j | Nós e relações da topologia elétrica; vizinhança e impacto |
| Redis | Cache de consultas frequentes e apoio futuro a jobs assíncronos |
| Next.js | Telas de ativos, alertas, casos e overview do sistema |

## 4. Limites entre módulos do backend

```text
app/
├── api/         # Rotas e composição HTTP
├── core/        # Config, logging, dependências
├── schemas/     # Contratos Pydantic
└── services/    # Regras de domínio e adaptação para persistência
```

Regras:

- `api` nao implementa regra de negócio.
- `schemas` espelham o contrato de API e os payloads internos mínimos.
- `services` concentram o comportamento do MVP e devem ser o ponto de troca do storage em memória por persistência real.

## 5. Fluxos principais

### 5.1 Login

1. Cliente envia credenciais para `POST /api/v1/auth/login`.
2. Backend valida usuário.
3. Resposta inclui token JWT com `sub`, `tenant_id`, `role` e `exp`.

### 5.2 Ingestão

1. Cliente cria `ingestion_job` via `POST /api/v1/ingestion/jobs`.
2. Backend valida origem, formato e payload.
3. Job entra como `queued` ou `processing`.
4. Medicoes validadas sao persistidas em `measurement`.
5. Resultado do job fica disponível em `GET /api/v1/ingestion/jobs/{job_id}`.

### 5.3 Health score e alerta

1. Novas medições atualizam a janela operacional do ativo.
2. O serviço calcula `health_score` por regras e pesos por tipo.
3. Thresholds e rolling z-score produzem anomalias v0.
4. O backend materializa alertas em `alert`.
5. O frontend consulta `GET /api/v1/alerts` por polling.

### 5.4 Case a partir de alerta

1. Usuário lista alertas.
2. Usuário confirma ou reconhece um alerta.
3. Cliente cria `case` ligado ao `alert_id`.
4. Caso entra com estado `open`.

### 5.5 Topologia e impacto

1. O Energy Graph replica a topologia mínima de ativos e subestações.
2. `neighbors` retorna o contexto local do ativo.
3. `impact` retorna o conjunto de ativos e subestações afetados em profundidade limitada.

## 6. Modelo de deployment inicial

- Desenvolvimento local: `docker compose`.
- Staging inicial: mesma topologia do compose em uma VM única.
- Produção posterior: fora do escopo desta etapa.

## 7. Tradeoffs assumidos

- O MVP privilegia velocidade e clareza de domínio em vez de automação avançada.
- A persistência em memória do scaffold existe apenas para destravar implementação; a interface já foi desenhada para troca por Postgres/Neo4j.
- O uso de Neo4j e limitado para que o produto capture o diferencial do grafo sem travar o início do desenvolvimento.

## 8. Itens explicitamente adiados

- GraphQL.
- WebSocket e Socket.io.
- Realtime ingestion via OPC-UA.
- Forecasting.
- Notificações por SMS/push.
- Supressão avançada de alarmes.
