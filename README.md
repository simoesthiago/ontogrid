# OntoGrid

OntoGrid e uma plataforma vertical de dados, ontologia e IA aplicada para o setor eletrico brasileiro. O recorte atual do repositorio e o **MVP publico v1 do Energy Data Hub**: ingestao e curadoria de dados publicos de ANEEL, ONS e CCEE, versionamento de datasets, Energy Graph publico, APIs e dashboards e um copilot analitico grounded nesses dados.

## Posicionamento do produto

- Inspirado em benchmarks como Palantir Foundry/AIP, sem buscar paridade literal de produto.
- Public-first: o MVP nao depende de onboarding de dados privados do cliente.
- O hub publico e a porta de entrada da ontologia, da visualizacao e da IA.
- A fase seguinte e o Enterprise Data Plane, que conecta dados sensiveis e habilita apps operacionais.

## Escopo do MVP publico v1

- Catalogo de fontes e datasets publicos.
- Refresh versionado para ANEEL, ONS e CCEE.
- Normalizacao temporal e semantica dos dados.
- Energy Graph publico com entidades e relacoes setoriais.
- APIs REST para catalogo, series, grafo e insights.
- Dashboards base para exploracao dos dados.
- Copilot analitico para perguntas, explicacoes e resumos grounded.

## Fase seguinte

- Enterprise Data Plane tenant-scoped.
- Federacao com dados privados do cliente.
- Apps como de Reliability / Outage Intelligence, Smart Alerting Copilot, Technical Issue Resolution Assistant, Field Ops, entre outros

## Estado atual do repo

O repositorio agora contem:

- documentacao consolidada para o pivot do MVP publico;
- bootstrap minimo de backend FastAPI em [src/backend](src/backend);
- bootstrap minimo de frontend Next.js em [src/frontend](src/frontend);
- runtime oficial de desenvolvimento via [docker-compose.yml](docker-compose.yml) e [.env.example](.env.example);
- skill local do projeto em [skills/ontogrid](skills/ontogrid).

## Ordem de leitura recomendada

1. [docs/strategy/VISAO_PLATAFORMA_ESTRATEGIA.md](docs/strategy/VISAO_PLATAFORMA_ESTRATEGIA.md)
2. [docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md](docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md)
3. [docs/contracts/API_SPEC.md](docs/contracts/API_SPEC.md)
4. [docs/platform/DATA_MODEL.md](docs/platform/DATA_MODEL.md)
5. [docs/platform/ARCHITECTURE.md](docs/platform/ARCHITECTURE.md)
6. [docs/product/MVP_ROADMAP.md](docs/product/MVP_ROADMAP.md)
7. [docs/strategy/PORTFOLIO_E_ROADMAP.md](docs/strategy/PORTFOLIO_E_ROADMAP.md)
8. [docs/platform/DATA_INGESTION.md](docs/platform/DATA_INGESTION.md)
9. [docs/product/USER_STORIES.md](docs/product/USER_STORIES.md)
10. [docs/strategy/HISTORICO_E_RECONCILIACAO.md](docs/strategy/HISTORICO_E_RECONCILIACAO.md)
11. [docs/platform/TECH_STACK.md](docs/platform/TECH_STACK.md)
12. [docs/platform/INFRA_DEPLOY.md](docs/platform/INFRA_DEPLOY.md)

## Estrutura

```text
ontogrid/
|-- docs/
|   |-- strategy/         # Visao e PDFs estrategicos
|   |-- product/          # MVP publico, roadmap e user stories
|   |-- contracts/        # Contratos HTTP
|   `-- platform/         # Arquitetura, modelo, ingestao, stack e deploy
|-- infra/                # Notas e convencoes de infra local
|-- scripts/              # Scripts utilitarios de bootstrap/teste
|-- skills/ontogrid/      # Skill local para agents
|-- src/backend/          # FastAPI scaffold
|-- src/frontend/         # Next.js scaffold
|-- AGENT.md              # Contexto canonico para coding agents
|-- AGENTS.md             # Compatibilidade com ferramentas que buscam AGENTS.md
|-- docker-compose.yml    # Stack local
`-- .env.example          # Variaveis base
```

## Runtime oficial de desenvolvimento

O baseline de desenvolvimento agora e `docker compose` com:

- FastAPI
- TimescaleDB/PostgreSQL
- Neo4j
- Redis
- Next.js

SQLite fica reservado para testes locais rapidos e ambientes efemeros.
No runtime oficial, o container `api` aplica `alembic upgrade head`, seeda o catalogo e busca dados reais ausentes antes de subir o FastAPI.

## Quick start

### Stack local completa

```powershell
Copy-Item .env.example .env
docker compose up --build
```

### Backend isolado

Use esse fluxo apenas quando quiser iterar o backend fora do compose. Para o runtime oficial, prefira a stack completa acima.

```powershell
cd src/backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
alembic upgrade head
python -m app.cli bootstrap-live-data
python -m pytest
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd src/frontend
npm install
npm run dev
```

## Proximo passo recomendado

1. Expandir a cobertura de datasets CKAN com o contrato interno unificado de ingestao.
2. Reforcar reconciliacao de entidades, aliases e relacoes no grafo publico.
3. Evoluir dashboards e exploracao de series sobre APIs reais do hub.
4. Endurecer observabilidade do pipeline e do runtime compose.
5. Endurecer a operacao do copilot grounded com provider LLM e cache.
