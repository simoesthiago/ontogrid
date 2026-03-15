# OntoGrid

OntoGrid e o **MVP publico v1 do Energy Data Hub** para o setor eletrico brasileiro. O produto quer catalogar e servir o universo inventariado de **345 datasets publicos** de ANEEL, ONS e CCEE, com navegacao por dataset, analise estruturada, entidades canonicas cross-dataset e um copilot grounded.

## Baseline do produto

- O catalogo alvo do repo e **345 datasets**: `ANEEL 69`, `ONS 80`, `CCEE 196`.
- A IA principal do app tem **5 paginas**:
  - `Analysis`
  - `Entities`
  - `Datasets`
  - `Copilot`
  - `Settings`
- `Entities` e o eixo canonico de navegacao do produto.
- Grafo/Neo4j continuam no MVP, mas como infraestrutura de suporte e enriquecimento, nao como pagina principal da UX.
- O frontend nunca carrega arquivo bruto; ele consome apenas a camada curada servida pelo backend.

## Estado atual do repo

- Todos os **345 datasets** estao inventariados e catalogados.
- **11 datasets** ja possuem adapter implementado no repo.
- **334 datasets** seguem catalogados, mas ainda sem adapter.
- O snapshot oficial desse status esta em [CATALOG_STATUS.md](/C:/Users/tsimoe01/coding/ontogrid/docs/datasets/CATALOG_STATUS.md) e [catalog_status.json](/C:/Users/tsimoe01/coding/ontogrid/docs/datasets/catalog_status.json).

## Ordem de leitura recomendada

1. [MVP_PUBLICO_ENERGY_DATA_HUB.md](/C:/Users/tsimoe01/coding/ontogrid/docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md)
2. [API_SPEC.md](/C:/Users/tsimoe01/coding/ontogrid/docs/contracts/API_SPEC.md)
3. [DATA_MODEL.md](/C:/Users/tsimoe01/coding/ontogrid/docs/platform/DATA_MODEL.md)
4. [ARCHITECTURE.md](/C:/Users/tsimoe01/coding/ontogrid/docs/platform/ARCHITECTURE.md)
5. [DATA_INGESTION.md](/C:/Users/tsimoe01/coding/ontogrid/docs/platform/DATA_INGESTION.md)
6. [USER_STORIES.md](/C:/Users/tsimoe01/coding/ontogrid/docs/product/USER_STORIES.md)
7. [STATUS_E_MATURIDADE_ONTOGRID.md](/C:/Users/tsimoe01/coding/ontogrid/docs/product/STATUS_E_MATURIDADE_ONTOGRID.md)
8. [INFRA_DEPLOY.md](/C:/Users/tsimoe01/coding/ontogrid/docs/platform/INFRA_DEPLOY.md)
9. [CATALOG_STATUS.md](/C:/Users/tsimoe01/coding/ontogrid/docs/datasets/CATALOG_STATUS.md)

## Runtime oficial de desenvolvimento

O baseline local e `docker compose` com:

- FastAPI
- TimescaleDB/PostgreSQL
- Neo4j
- Redis
- Next.js

O runtime local **nao** deve baixar o universo completo de dados reais por padrao.

`BOOTSTRAP_MODE` controla o comportamento do backend no startup:

- `catalog`: aplica migrations e seeda o catalogo completo, sem ingerir dados
- `sample`: aplica migrations, seeda o catalogo e materializa apenas fixtures leves dos datasets com adapter
- `selected_live`: aplica migrations, seeda o catalogo e ingere apenas os datasets listados em `BOOTSTRAP_DATASET_CODES`

Default recomendado para desenvolvimento local: `BOOTSTRAP_MODE=sample`.

## Quick start

### Stack local completa

```powershell
Copy-Item .env.example .env
docker compose up --build
```

### Backend isolado

```powershell
cd src/backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
python -m app.cli bootstrap-catalog
python -m app.cli bootstrap-sample-data
python -m pytest
uvicorn app.main:app --reload --port 8000
```

Para ingestao live selecionada:

```powershell
$env:BOOTSTRAP_MODE="selected_live"
$env:BOOTSTRAP_DATASET_CODES="carga_horaria_submercado,pld_horario_submercado"
python -m app.cli bootstrap-selected-live-data
```

### Frontend

```powershell
cd src/frontend
npm install
npm run dev
```

## Regenerar o snapshot do catalogo

```powershell
python scripts/generate_catalog_status.py
```

## Regra de operacao

- O repo quer expor os **345 datasets** no catalogo desde ja.
- Nem todo dataset catalogado precisa estar publicado em todo ambiente.
- `publicado` e estado operacional do ambiente e deve ser lido via `GET /api/v1/catalog/coverage`.
- Ingestao live pesada deve rodar apenas de forma explicita ou em ambiente centralizado.
