# Plano: Arquitetura de Ingestão Real, Ontologia e Visualizações do OntoGrid

## Contexto

O OntoGrid hoje roda com 3 fixtures CSV de 2-3 linhas cada. Não há dado real, não há ontologia, não há visualização com valor analítico. Os 3 portais públicos (ANEEL: 69 datasets, ONS: 80, CCEE: 196) usam CKAN e oferecem API + CSV para download sem autenticação. Este plano define **como baixar dados reais**, **que ontologia formar**, **que visões construir** e **que arquitetura usar**.

---

## A. Estratégia de Aquisição de Dados

### Como baixar

Todos os portais usam CKAN. Duas abordagens complementares:

1. **CKAN Data API (`datastore_search`)** — para datasets que têm DataStore ativo (maioria na CCEE, vários na ONS). Permite paginar e filtrar server-side sem baixar o arquivo inteiro.
2. **Download de recurso CSV/Parquet** — para datasets grandes ou particionados por ano (maioria na ANEEL). Usa `package_show` para descobrir resource_id → download direto.

**Implementação**: Criar uma `CkanDatasetAdapter` que herda de `BaseDatasetAdapter` e adiciona:
- `ckan_base_url`: URL do portal CKAN
- `ckan_package_id`: ID do dataset no CKAN
- `ckan_resource_id`: ID do recurso específico (se conhecido)
- `fetch_bytes()` override que usa `ckanapi.RemoteCKAN` ou `requests` para baixar

**Sem cloud para o MVP**. Tudo roda local com SQLite/PostgreSQL. A cloud entra na fase enterprise.

### Quais datasets priorizar (15 datasets para o MVP)

Critério: datasets que criam **cruzamento entre fontes** (ANEEL ↔ ONS ↔ CCEE) e que geram entidades para o grafo.

#### ONS (5 datasets prioritários)
| Dataset | Valor | Entidades geradas |
|---------|-------|-------------------|
| **Geração por Usina - Base Horária** | Série principal de geração do SIN | Usina, Subsistema |
| **Carga Horária por Submercado** | Demanda do sistema | Submercado |
| **EAR Diário por Subsistema** | Energia armazenada (risco hídrico) | Subsistema, REE |
| **Capacidade Instalada de Geração** | Cadastro mestre de potência | Usina, Fonte |
| **Reservatórios** | Cadastro mestre hidrológico | Reservatório, Bacia |

#### ANEEL (5 datasets prioritários)
| Dataset | Valor | Entidades geradas |
|---------|-------|-------------------|
| **SIGA** | Cadastro do parque gerador nacional | Usina, Agente, UF, Fonte |
| **Tarifas homologadas de distribuição** | Valores de TE e TUSD | Distribuidora, Subgrupo |
| **Indicadores DEC/FEC** | Qualidade do serviço de distribuição | Distribuidora, Conjunto Elétrico |
| **Resultado de Leilões** | Expansão de geração e transmissão | Leilão, Empreendimento |
| **Agentes de Geração** | Relação usina → agente → CNPJ | Agente, Usina |

#### CCEE (5 datasets prioritários)
| Dataset | Valor | Entidades geradas |
|---------|-------|-------------------|
| **PLD Horário por Submercado** | Preço de curto prazo | Submercado |
| **Agentes de Mercado (LISTA_AGENTE_ASSOCIADO)** | Cadastro de participantes | Agente, Classe |
| **Infomercado - Geração** | Geração contabilizada por usina | Usina, Agente |
| **Infomercado - Consumo** | Consumo por classe/submercado | Submercado, Classe |
| **CVU Conjuntural** | Custo variável de térmicas | Usina, Combustível |

---

## B. Ontologia — O Que Conecta as 3 Fontes

### Entidades centrais do grafo público

| Entidade | Tipo | Aparece em | Papel |
|----------|------|------------|-------|
| **Submercado** (SE/CO, S, NE, N) | `submarket` | ONS (carga, geração), CCEE (PLD, mercado) | Eixo geográfico-elétrico principal |
| **Usina/Empreendimento** | `plant` | ONS (geração), ANEEL (SIGA, leilões), CCEE (Infomercado) | Ativo de geração |
| **Agente/Empresa** | `agent` | ANEEL (agentes, SIGA), CCEE (agentes) | Participante do mercado |
| **Distribuidora** | `distributor` | ANEEL (tarifas, DEC/FEC), CCEE (contratos) | Concessionária de distribuição |
| **Reservatório/Bacia** | `reservoir` | ONS (hidrologia, EAR) | Ativo hídrico |
| **Fonte de Geração** | `energy_source` | ONS (capacidade), ANEEL (SIGA) | Tipo de energia (eólica, solar, hidro, térmica) |

### Relações no Neo4j

```
(:Plant)-[:LOCATED_IN]->(:Submarket)
(:Plant)-[:OPERATED_BY]->(:Agent)
(:Plant)-[:USES_SOURCE]->(:EnergySource)
(:Plant)-[:SOLD_AT]->(:Auction)
(:Agent)-[:DISTRIBUTES_IN]->(:Submarket)        (distribuidoras)
(:Distributor)-[:REGULATED_BY]->(:Source{ANEEL})
(:Reservoir)-[:BELONGS_TO]->(:Basin)
(:Reservoir)-[:FEEDS]->(:Plant)
(:Dataset)-[:PUBLISHED_BY]->(:Source)
(:Dataset)-[:REFERENCES]->(:Entity)
```

### Resolução de entidades (entity_alias)

A mesma usina aparece com nomes diferentes:
- ONS: `cod_usina=123`, `nom_usina="ITAIPU"`
- ANEEL/SIGA: `CEG=ABC.01.23`, `NomeEmpreendimento="UHE Itaipu"`
- CCEE: `SIGLA_AGENTE="ITAI"`, `USINA="Itaipu"`

O modelo `entity_alias` resolve isso: cada fonte registra seu código/nome como alias apontando para a mesma `entity.id` canônica. Isso é o que faz a ontologia funcionar.

---

## C. Visualizações e Insights

### Dashboard 1: Panorama do SIN (cross-source)
- **Carga vs Geração** por submercado (ONS) com PLD sobreposto (CCEE)
- **EAR** por subsistema com alerta de risco hídrico (ONS)
- **Mix de geração** por fonte: hidro, eólica, solar, térmica (ONS + ANEEL)
- Valor: responde "qual o estado do sistema elétrico agora?"

### Dashboard 2: Mercado e Preços
- **Evolução do PLD** horário/médio (CCEE) correlacionado com EAR (ONS)
- **CVU de térmicas** por combustível (CCEE) vs despacho térmico (ONS)
- **Custo da energia** para o consumidor via tarifas (ANEEL)
- Valor: responde "por que a energia está cara/barata?"

### Dashboard 3: Parque Gerador
- **Mapa do parque gerador** por fonte, UF e potência (ANEEL/SIGA)
- **Pipeline de expansão**: usinas em construção vs em operação (ANEEL/RALIE)
- **Fator de capacidade** de eólicas e solares (ONS)
- Valor: responde "como está a oferta de energia?"

### Dashboard 4: Qualidade da Distribuição
- **DEC/FEC** por distribuidora e região (ANEEL)
- **Tarifas** comparativas entre distribuidoras (ANEEL)
- **Ranking** de qualidade do serviço
- Valor: responde "quem entrega melhor serviço ao consumidor?"

### Dashboard 5: Energy Graph Explorer
- Navegação visual de entidades e relações
- Drill-down: Usina → Agente → Submercado → Datasets relacionados
- Busca por entidade com auto-complete
- Valor: responde "como as coisas se conectam no setor?"

---

## D. Decisões de Arquitetura

### Cloud? **Não para o MVP.**
- SQLite para dev local, PostgreSQL para staging
- Os dados públicos somam poucos GB — cabe em qualquer máquina
- Cloud entra na fase enterprise com tenant isolation

### RAG? **Sprint 3, não antes.**
- O copilot analítico precisa de dados reais primeiro (Sprint 2)
- RAG sobre metadados do catálogo + chunks de datasets + grafo Neo4j
- Redis para cache de respostas do copilot
- Implementar como endpoint `POST /api/v1/copilot/query`

### Storage — o que vai onde

| Armazenamento | O que guarda | Por quê |
|---------------|-------------|---------|
| **PostgreSQL** | `source`, `dataset`, `dataset_version`, `refresh_job`, `entity`, `entity_alias`, `relation`, `metric_series`, `insight_snapshot`, `copilot_trace` | Modelo relacional canônico |
| **TimescaleDB** (extensão do PG) | `observation` (hypertable particionada por tempo) | Séries temporais com compressão e queries eficientes |
| **Neo4j** | Projeção de `Entity` + `Relation` + `Dataset` + `Source` | Navegação de grafo, vizinhança, contexto ontológico |
| **Filesystem** | Artefatos CSV/Parquet baixados | Lineage e re-processamento |

### Integração CKAN — padrão de adapter

```
CkanDatasetAdapter(BaseDatasetAdapter)
  ├── fetch_bytes(): usa ckanapi para baixar recurso
  ├── fetch_via_datastore(): usa datastore_search com paginação
  ├── parse(): extrai linhas, entidades, relações
  └── extract_entities(): retorna lista de entidades para o grafo
```

Cada adapter concreto define:
- `ckan_base_url`, `ckan_package_id`, `ckan_resource_id`
- `parse()` com lógica específica do dataset
- `extract_entities()` que retorna entidades e aliases para persistir

---

## E. Implementação — Sequência

### Sprint 2: Dados Reais + Grafo + Séries

**Passo 1 — Infra de ingestão CKAN**
- Criar `CkanDatasetAdapter` base com `ckanapi`
- Estender `RefreshService` para persistir entidades + observações (não só versions)
- Adicionar `ckanapi` ao `pyproject.toml`

**Passo 2 — Modelos de dados faltantes**
- Criar models SQLAlchemy: `Entity`, `EntityAlias`, `Relation`, `MetricSeries`, `Observation`
- Configurar `observation` como hypertable do TimescaleDB (para prod)

**Passo 3 — 5 adapters ONS prioritários**
- `OnsGeracaoUsinaAdapter`: geração horária por usina
- `OnsCargaSubmercadoAdapter` (já existe, migrar para CKAN real)
- `OnsEarSubsistemaAdapter`: EAR diária
- `OnsCapacidadeInstaladaAdapter`: cadastro mestre
- `OnsReservatoriosAdapter`: cadastro mestre

**Passo 4 — 5 adapters ANEEL prioritários**
- `AneelSigaAdapter`: cadastro do parque gerador
- `AneelTarifasAdapter` (já existe, migrar para CKAN real)
- `AneelDecFecAdapter`: indicadores de qualidade
- `AneelLeiloesAdapter`: resultados de leilões
- `AneelAgentesGeracaoAdapter`: agentes e usinas

**Passo 5 — 5 adapters CCEE prioritários**
- `CceePldAdapter` (já existe, migrar para CKAN real)
- `CceeAgentesAdapter`: cadastro de agentes
- `CceeInfomercadoGeracaoAdapter`: geração contabilizada
- `CceeInfomercadoConsumoAdapter`: consumo por classe
- `CceeCvuAdapter`: custo variável térmicas

**Passo 6 — Neo4j integration**
- Service para projetar entidades e relações no grafo
- Queries de vizinhança para a API `/graph/entities/{id}/neighbors`
- Substituir `public_data_store.py` por queries reais

**Passo 7 — Frontend com dados reais**
- Dashboards com charts (Recharts ou similar)
- Página de Graph Explorer com navegação de entidades
- Séries temporais com gráficos de linha

### Sprint 3: Copilot + Insights

**Passo 8 — Insights automatizados**
- `InsightSnapshot` gerado por análise dos dados ingeridos
- Endpoint `GET /api/v1/insights/overview`
- Cards: cobertura dos dados, alertas de freshness, destaques

**Passo 9 — Copilot analítico**
- Endpoint `POST /api/v1/copilot/query`
- RAG sobre metadados + chunks de datasets + contexto do grafo
- Citações com rastreabilidade até dataset_version
- Redis para cache

---

## Arquivos críticos a modificar

| Arquivo | Mudança |
|---------|---------|
| `src/backend/app/ingestion/base.py` | Criar `CkanDatasetAdapter` base |
| `src/backend/app/ingestion/registry.py` | Registrar 15 adapters |
| `src/backend/app/db/models.py` | Adicionar Entity, EntityAlias, Relation, MetricSeries, Observation |
| `src/backend/app/db/seed.py` | Expandir seeds de 3 para 15 datasets com package_ids CKAN |
| `src/backend/app/services/refresh_service.py` | Estender para persistir entidades e observações |
| `src/backend/app/services/graph_service.py` | **Novo**: integração Neo4j |
| `src/backend/app/services/public_data_store.py` | **Remover**: substituído por queries reais |
| `src/backend/app/api/routes/graph.py` | Migrar de mock para Neo4j |
| `src/backend/app/api/routes/series.py` | Migrar de mock para PostgreSQL |
| `src/backend/app/core/config.py` | Adicionar `neo4j_uri`, `neo4j_user`, `neo4j_password` |
| `src/frontend/` | Adicionar charts, graph explorer, dashboards reais |
| `pyproject.toml` | Adicionar `ckanapi`, `neo4j` (driver Python) |

## Verificação

- Backend: `pytest` continua passando + novos testes para adapters CKAN
- Subir com `uvicorn` + `npm run dev` e verificar:
  - `/api/v1/sources` retorna 3 fontes
  - `/api/v1/datasets` retorna 15 datasets com versões reais
  - `/api/v1/series` retorna observações de séries reais
  - `/api/v1/graph/entities` retorna entidades do Neo4j
  - Frontend mostra dashboards com dados reais
- Disparar refresh manual: `POST /admin/datasets/{id}/refresh` baixa dado real do CKAN
