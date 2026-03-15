# Infraestrutura e Deploy - OntoGrid MVP publico v1

## Ambientes

| Ambiente | Objetivo | Regra |
|---|---|---|
| Local | Desenvolvimento diario | `docker compose` com bootstrap leve |
| Shared/Staging | Validacao interna e demos | Ingestao live controlada |
| Producao | Fase posterior | Fora do escopo desta rodada |

## Componentes locais

| Servico | Papel |
|---|---|
| `api` | Backend FastAPI, bootstrap e operacoes administrativas do hub |
| `frontend` | Next.js |
| `timescaledb` | PostgreSQL + TimescaleDB para catalogo, versoes e series |
| `neo4j` | Vizinhanca e relacoes do eixo `Entities` |
| `redis` | Cache e apoio ao copilot |

## Variaveis minimas

- `APP_ENV`
- `ARTIFACTS_DIR`
- `BOOTSTRAP_MODE`
- `BOOTSTRAP_DATASET_CODES`
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

## Rotina local

```powershell
Copy-Item .env.example .env
docker compose up --build
```

No runtime local oficial, o servico `api` roda:

1. `python -m app.cli bootstrap`
2. `uvicorn app.main:app ...`

`BOOTSTRAP_MODE` controla o comportamento:

- `catalog`: sobe apenas o catalogo dos 345 datasets
- `sample`: sobe o catalogo e carrega fixtures leves dos datasets com adapter
- `selected_live`: sobe o catalogo e ingere apenas os datasets listados em `BOOTSTRAP_DATASET_CODES`

Default recomendado: `BOOTSTRAP_MODE=sample`.

## Backend isolado

```powershell
cd src/backend
pip install -e .[dev]
python -m app.cli bootstrap-catalog
python -m app.cli bootstrap-sample-data
python -m pytest
```

Para ingestao live selecionada:

```powershell
$env:BOOTSTRAP_MODE="selected_live"
$env:BOOTSTRAP_DATASET_CODES="carga_horaria_submercado,pld_horario_submercado"
python -m app.cli bootstrap-selected-live-data
```

## Regra de operacao

- o ambiente local nao deve baixar o universo completo de dados reais por padrao;
- o repo continua catalogando os 345 datasets independentemente do modo de bootstrap;
- arquivos originais ficam no backend/storage;
- `publicado` depende do banco e dos refresh jobs daquele ambiente.
