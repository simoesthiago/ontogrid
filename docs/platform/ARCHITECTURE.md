# Arquitetura Tecnica - OntoGrid Energy Data Hub MVP

Este documento descreve apenas a arquitetura necessaria para iniciar a implementacao do MVP publico. A fonte de verdade dos contratos HTTP e [API_SPEC.md](../contracts/API_SPEC.md).

## 1. Objetivo arquitetural

Entregar um produto que permita:

- ingerir dados publicos de ANEEL, ONS e CCEE;
- curar e versionar datasets com lineage;
- consultar series e entidades em uma semantica unificada;
- navegar um Energy Graph publico;
- servir insights e dashboards base;
- responder perguntas via copilot analitico grounded.

## 2. Decisoes fechadas

- Monolito modular.
- FastAPI como backend HTTP e orquestrador do copilot.
- PostgreSQL 16 + TimescaleDB para metadados, versoes, series e observacoes.
- Neo4j 5 para o Energy Graph publico.
- Redis 7 para cache e montagem rapida de contexto do copilot.
- Refresh por pulls agendados, downloads versionados e crawlers especificos.
- Sem `tenant_id` no nucleo publico.
- Sem GraphQL e sem WebSocket no primeiro corte.

## 3. Responsabilidade por componente

| Componente | Responsabilidade |
|---|---|
| FastAPI | Catalogo, series, grafo, insights, endpoint do copilot e operacoes administrativas |
| Worker mode do backend | Refresh agendado, parsing, normalizacao, projeção de grafo e snapshot de insights |
| PostgreSQL/TimescaleDB | `source`, `dataset`, `dataset_version`, `refresh_job`, `metric_series`, `observation`, `insight_snapshot`, `copilot_trace` |
| Neo4j | Entidades e relacoes do Energy Graph publico |
| Redis | Cache de consultas frequentes e montagem de contexto do copilot |
| Next.js | IA principal com `Analysis`, `Entities`, `Datasets` e `Copilot`, alem de drill-down secundario para dataset, versao e entidade |

## 4. Limites entre modulos do backend

```text
app/
|-- api/         # Rotas e composicao HTTP
|-- core/        # Config, logging, dependencies e scheduling
|-- schemas/     # Contratos Pydantic
|-- services/    # Regra de negocio do hub publico
|-- ingestion/   # Refresh, parsing, normalizacao e versionamento
`-- copilot/     # Recuperacao de contexto, grounding e resposta
```

Regras:

- `api` nao implementa regra de negocio.
- `schemas` espelham o contrato de API e os payloads internos minimos.
- `ingestion` concentra extracao, parse, versionamento e lineage.
- `services` concentra harmonizacao publica, evidencia, projections e agregacao de perfis.
- `copilot` orquestra contexto e resposta, mas nao vira camada de logica opaca sem citacao.

## 5. Fluxos principais

### 5.1 Refresh de dataset publico

1. Um refresh e disparado por agenda ou via `POST /api/v1/admin/datasets/{dataset_id}/refresh`.
2. O backend cria `refresh_job`.
3. O artefato bruto e baixado ou consultado na fonte.
4. O parser normaliza os dados em um payload generico do kernel.
5. O harmonizador publico aplica regras deterministicas de match e persiste a camada semantica seletiva.
6. Series, observacoes e relacoes sao atualizadas sem substituir o kernel.
7. Evidencias publicas, projecao Neo4j e snapshots de insight sao rebuildados quando necessario.

### 5.2 Navegacao principal da UI

1. `Datasets` organiza o catalogo publico e leva ao detalhe secundario de dataset e versoes.
2. `Analysis` usa `GET /api/v1/datasets`, `GET /api/v1/analysis/datasets/{dataset_id}/fields` e `POST /api/v1/analysis/query`.
3. `Entities` usa `GET /api/v1/entities` e `GET /api/v1/entities/{entity_id}/profile`.
4. `Copilot` permanece uma pagina propria para perguntas grounded, mas pode receber contexto opcional de dataset e entidade por query params.

### 5.3 Drill-down e capacidades secundarias

1. O detalhe de dataset continua responsavel por versoes, schema, series, observacoes e refresh jobs.
2. O detalhe de entidade continua responsavel por facetas, evidencia, series e contexto relacional.
3. Grafo, insights, coverage e sources continuam como capacidades e contratos de backend, mas nao como paginas top-level da IA atual.

### 5.4 Copilot analitico

1. O usuario envia pergunta para `POST /api/v1/copilot/query`.
2. O backend resolve datasets, versoes, entidades e janelas temporais relevantes.
3. O copilot monta contexto grounded em observacoes, metadados, evidencia publicada e vizinhanca do grafo.
4. A resposta retorna com citacoes e perguntas de seguimento.

## 6. Modelo de deployment inicial

- runtime oficial de desenvolvimento: `docker compose` com FastAPI, TimescaleDB/PostgreSQL, Neo4j, Redis e Next.js;
- SQLite fica restrito a testes locais rapidos e ambientes efemeros;
- staging inicial: mesma topologia do compose em uma VM unica;
- producao posterior: fora do escopo desta etapa.

## 7. Tradeoffs assumidos

- O MVP privilegia dados publicos e explicabilidade sobre profundidade enterprise.
- O grafo nasce publico e canonico antes de ser federado com dados privados.
- O copilot e analitico e grounded; agentic workflows ficam para depois.
- A mesma base tecnica deve suportar a futura fase enterprise sem reescrever semantica e lineage.

## 8. Itens explicitamente adiados

- conectores privados para SCADA, ERP, OMS, CMMS e GIS;
- tenancy como modelo central do produto;
- workflow rico de casos e field assistant;
- RAG sobre documentos privados;
- reliability e classificacao de causas com dados internos de cliente.
