# Infraestrutura e Deploy - OntoGrid MVP v0.1

## 1. Ambientes

| Ambiente | Objetivo | Forma |
|---|---|---|
| Local | Desenvolvimento diário | `docker compose` |
| Staging inicial | Validação interna e demos | VM única com a mesma topologia do compose |
| Produção | Fase posterior | Fora do escopo desta rodada |

## 2. Componentes locais

| Serviço | Papel |
|---|---|
| `api` | Backend FastAPI |
| `frontend` | Next.js |
| `timescaledb` | PostgreSQL + TimescaleDB |
| `neo4j` | Energy Graph |
| `redis` | Cache e apoio a jobs futuros |

## 3. Arquivos de bootstrap

- [docker-compose.yml](/C:/Users/tsimoe01/coding/ontogrid/docker-compose.yml)
- [.env.example](/C:/Users/tsimoe01/coding/ontogrid/.env.example)
- [src/backend/Dockerfile](/C:/Users/tsimoe01/coding/ontogrid/src/backend/Dockerfile)
- [src/frontend/Dockerfile](/C:/Users/tsimoe01/coding/ontogrid/src/frontend/Dockerfile)
- [scripts/setup.ps1](/C:/Users/tsimoe01/coding/ontogrid/scripts/setup.ps1)

## 4. Variáveis mínimas

- `APP_ENV`
- `JWT_SECRET`
- `POSTGRES_*`
- `DATABASE_URL`
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `REDIS_URL`
- `NEXT_PUBLIC_API_BASE_URL`

## 5. Rotina local

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Backend:

```powershell
cd src/backend
pip install -e .[dev]
pytest
```

Frontend:

```powershell
cd src/frontend
npm install
npm run dev
```

## 6. Deploy inicial recomendado

- staging em VM única;
- banco e grafo persistidos em volumes;
- CI apenas para lint/test/build na primeira etapa;
- CD manual ou semiautomático ate o fluxo estabilizar.

## 7. Fora do escopo

- Kubernetes.
- alta disponibilidade.
- observabilidade completa com Prometheus/Grafana.
- segredos gerenciados por vault.
- backups automatizados de produção.
