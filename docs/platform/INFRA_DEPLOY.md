# Infraestrutura e Deploy - OntoGrid MVP publico v1

## 1. Ambientes

| Ambiente | Objetivo | Forma |
|---|---|---|
| Local | Desenvolvimento diario | `docker compose` |
| Staging inicial | Validacao interna e demos | VM unica com a mesma topologia do compose |
| Producao | Fase posterior | Fora do escopo desta rodada |

## 2. Componentes locais

| Servico | Papel |
|---|---|
| `api` | Backend FastAPI e operacoes administrativas do hub |
| `frontend` | Next.js |
| `timescaledb` | PostgreSQL + TimescaleDB para metadados e series |
| `neo4j` | Energy Graph publico |
| `redis` | Cache e apoio ao copilot |

## 3. Arquivos de bootstrap

- [docker-compose.yml](../docker-compose.yml)
- [.env.example](../.env.example)
- [src/backend/Dockerfile](../src/backend/Dockerfile)
- [src/frontend/Dockerfile](../src/frontend/Dockerfile)
- [scripts/setup.ps1](../scripts/setup.ps1)

## 4. Variaveis minimas

- `APP_ENV`
- `POSTGRES_*`
- `DATABASE_URL`
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `REDIS_URL`
- `LLM_API_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `COPILOT_CACHE_TTL_SECONDS`
- `NEXT_PUBLIC_API_BASE_URL`

`JWT_SECRET` e opcional e so entra quando a camada de conta/autenticacao do produto for ativada.

## 5. Rotina local

```powershell
Copy-Item .env.example .env
docker compose up --build
```

No runtime oficial, o servico `api` roda:

1. `alembic upgrade head`
2. `python -m app.cli bootstrap-live-data`
3. `uvicorn app.main:app ...`

Isso garante catalogo seedado e datasets faltantes materializados antes da API aceitar trafego.

Backend:

```powershell
cd src/backend
pip install -e .[dev]
alembic upgrade head
python -m app.cli bootstrap-live-data
python -m pytest
```

Frontend:

```powershell
cd src/frontend
npm install
npm run dev
```

## 6. Deploy inicial recomendado

- staging em VM unica;
- banco e grafo persistidos em volumes;
- CI apenas para lint/test/build na primeira etapa;
- CD manual ou semiautomatico ate o fluxo estabilizar.

## 7. Fora do escopo

- Kubernetes.
- alta disponibilidade.
- observabilidade completa com Prometheus/Grafana.
- segredos gerenciados por vault.
- backups automatizados de producao.
- orquestracao enterprise de conectores privados.
