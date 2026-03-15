# Arquitetura Tecnica - OntoGrid Energy Data Hub MVP

Este documento descreve a arquitetura necessaria para o MVP publico com **catalogo de 345 datasets**, UX principal em **5 paginas** e ingestao local leve por padrao. A fonte de verdade dos contratos HTTP continua sendo [API_SPEC.md](../contracts/API_SPEC.md).

## Objetivo arquitetural

Entregar um produto que permita:

- catalogar os 345 datasets inventariados de ANEEL, ONS e CCEE;
- ingerir seletivamente datasets priorizados sem exigir download total no ambiente local;
- servir `Analysis`, `Entities`, `Datasets`, `Copilot` e `Settings`;
- consolidar entidades canonicas cross-dataset;
- responder perguntas grounded em datasets, versoes e entidades.

## Decisoes fechadas

- monolito modular;
- FastAPI como backend HTTP e orquestrador do copilot;
- PostgreSQL 16 + TimescaleDB para catalogo, versoes, series e observacoes;
- Neo4j 5 para suporte de vizinhanca e relacoes do eixo `Entities`;
- Redis 7 para cache e contexto do copilot;
- inventario completo no catalogo, ingestao seletiva por ambiente;
- sem `tenant_id` no nucleo publico;
- sem GraphQL e sem WebSocket no primeiro corte.

## Responsabilidade por componente

| Componente | Responsabilidade |
|---|---|
| FastAPI | Catalogo, analysis, entidades, coverage, series, insights, copilot e operacoes administrativas |
| Worker mode do backend | Bootstrap, refresh, parsing, normalizacao e publicacao |
| PostgreSQL/TimescaleDB | `source`, `dataset`, `dataset_version`, `refresh_job`, `metric_series`, `observation` e metadados da camada curada |
| Neo4j | Vizinhanca e relacoes projetadas para o eixo `Entities` |
| Redis | Cache de consultas frequentes e apoio ao copilot |
| Next.js | IA principal com `Analysis`, `Entities`, `Datasets`, `Copilot` e `Settings` |

## Regra principal de dados

- o frontend nunca carrega arquivo bruto;
- o backend guarda arquivo original e serve a camada curada;
- `Analysis`, `Entities` e `Copilot` consultam apenas a camada curada;
- um `dataset_version` pode representar multiplos arquivos de origem;
- processamento de arquivo grande deve ser por lote/streaming, nao por carga integral em memoria.

## Fluxos principais

### 1. Catalogo e cobertura

1. `docs/datasets/*.md` definem o inventario base.
2. `src/backend/app/catalog_inventory.py` materializa esse inventario como catalogo do repo.
3. `docs/datasets/catalog_status.json` e `docs/datasets/CATALOG_STATUS.md` registram o snapshot oficial do repo.
4. `GET /api/v1/catalog/coverage` mostra o estado operacional do ambiente.

### 2. Bootstrap local

1. `bootstrap-catalog` aplica migrations e seeda o catalogo dos 345 datasets.
2. `bootstrap-sample-data` materializa apenas fixtures leves dos datasets com adapter.
3. `bootstrap-selected-live-data` materializa apenas os datasets listados em `BOOTSTRAP_DATASET_CODES`.
4. `docker compose` local usa `BOOTSTRAP_MODE=sample` por padrao.

### 3. Navegacao principal da UI

1. `Datasets` organiza o catalogo completo e mostra status de cobertura.
2. `Analysis` opera sobre um dataset selecionado e usa queries da camada curada.
3. `Entities` lista entidades canonicas e leva ao perfil consolidado.
4. `Copilot` recebe pergunta e busca grounding em datasets, versoes e entidades.
5. `Settings` permanece top-level, ainda nao implementada como fluxo core.

## Ambientes

| Ambiente | Objetivo | Regra |
|---|---|---|
| Local | Desenvolvimento diario | `catalog` ou `sample`; nunca ingestao live total por padrao |
| Shared/Staging | Validacao interna e demos | Ingestao live controlada e publicacao de datasets priorizados |
| Prod | Fase posterior | Operacao centralizada com storage apropriado |

## Regra de leitura do grafo

- `Entities` e a experiencia de produto.
- Neo4j e grafo publico continuam importantes, mas como infraestrutura de suporte.
- Endpoints de grafo permanecem como capacidade tecnica e enriquecimento, nao como pagina top-level da UX.
