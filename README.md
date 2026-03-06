# OntoGrid

OntoGrid e uma plataforma de dados e decisao para o setor eletrico brasileiro. O recorte atual do repositório e o **MVP v0.1 de Asset Health**: cadastro de ativos, ingestão de medições, health score determinístico, detecção básica de anomalias, alertas, casos simples e Energy Graph focado em topologia e impacto.

## Escopo do MVP v0.1

- Cadastro e consulta de ativos críticos por tenant.
- Ingestão de dados via arquivo CSV/Excel ou lote JSON por API.
- Armazenamento operacional em PostgreSQL/TimescaleDB.
- Energy Graph em Neo4j apenas para topologia, vizinhança e impacto.
- Health score v0 por regras e pesos por tipo de ativo.
- Anomalia v0 por threshold e rolling z-score.
- Alertas consumidos por polling HTTP.
- Casos básicos criados a partir de alertas.

## Fora do escopo inicial

- GraphQL.
- WebSocket e Socket.io como requisito do MVP.
- Prophet, forecasting e ensemble complexo com PyOD.
- SMS, push notification e mobile dedicado.
- Mapa geográfico, knowledge base extensa e workflow rico de casos.

## Estado atual do repo

O repositório agora contem:

- Documentação consolidada para um baseline único do MVP.
- Bootstrap mínimo de backend FastAPI em [src/backend](/C:/Users/tsimoe01/coding/ontogrid/src/backend).
- Bootstrap mínimo de frontend Next.js em [src/frontend](/C:/Users/tsimoe01/coding/ontogrid/src/frontend).
- Infra local com [docker-compose.yml](/C:/Users/tsimoe01/coding/ontogrid/docker-compose.yml) e [.env.example](/C:/Users/tsimoe01/coding/ontogrid/.env.example).
- Skill local do projeto em [skills/ontogrid](/C:/Users/tsimoe01/coding/ontogrid/skills/ontogrid).

## Ordem de leitura recomendada

1. [docs/API_SPEC.md](/C:/Users/tsimoe01/coding/ontogrid/docs/API_SPEC.md)
2. [docs/DATA_MODEL.md](/C:/Users/tsimoe01/coding/ontogrid/docs/DATA_MODEL.md)
3. [docs/ARCHITECTURE.md](/C:/Users/tsimoe01/coding/ontogrid/docs/ARCHITECTURE.md)
4. [docs/DATA_INGESTION.md](/C:/Users/tsimoe01/coding/ontogrid/docs/DATA_INGESTION.md)
5. [docs/USER_STORIES.md](/C:/Users/tsimoe01/coding/ontogrid/docs/USER_STORIES.md)
6. [docs/MVP_ROADMAP.md](/C:/Users/tsimoe01/coding/ontogrid/docs/MVP_ROADMAP.md)
7. [docs/TECH_STACK.md](/C:/Users/tsimoe01/coding/ontogrid/docs/TECH_STACK.md)
8. [docs/INFRA_DEPLOY.md](/C:/Users/tsimoe01/coding/ontogrid/docs/INFRA_DEPLOY.md)

## Estrutura

```text
ontogrid/
├── docs/                 # Fonte de verdade do produto e arquitetura
├── infra/                # Notas e convenções de infra local
├── scripts/              # Scripts utilitários de bootstrap/teste
├── skills/ontogrid/      # Skill local para agents
├── src/backend/          # FastAPI scaffold
├── src/frontend/         # Next.js scaffold
├── AGENT.md              # Contexto canônico para coding agents
├── AGENTS.md             # Compatibilidade com ferramentas que buscam AGENTS.md
├── docker-compose.yml    # Stack local
└── .env.example          # Variáveis base
```

## Quick start

### Backend

```powershell
cd src/backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd src/frontend
npm install
npm run dev
```

### Stack local completa

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Próximo passo recomendado

1. Persistência real do backend em PostgreSQL/TimescaleDB.
2. Fluxo real de ingestão e criação de `ingestion_job`.
3. Health score e geração de alertas persistidos.
4. Integração do frontend com as rotas do backend.
5. Sincronização do Energy Graph com Neo4j.
