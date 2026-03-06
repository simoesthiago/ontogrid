# Arquitetura Tecnica - OntoGrid MVP

> **Versao:** 1.0
> **Data:** 2026-03-06
> **MVP:** Asset Health (Equipment Surveillance & Smart Alerting)
> **Status:** Em implementacao

---

## 1. Visao de Alto Nivel

### 1.1 Diagrama de Arquitetura (8 Camadas)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ONTOGRID - ARQUITETURA                          │
│                     MVP: Asset Health (Camadas Ativas)                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ H - Colaboracao Multiempresa                       [FUTURO]    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ G - IA Aplicada e Governada                        [MVP ▓▓░░]  │    │
│  │     Classificacao automatica de alertas                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ F - Workflows e Automacao                          [MVP ▓▓▓░]  │    │
│  │     Cases basicos + SOPs                                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ E - Motor Analitico                                [MVP ▓▓▓▓]  │    │
│  │     Anomaly Detection + Health Score + Forecasting             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ D - Data Products Engine                           [MVP ▓▓▓░]  │    │
│  │     Bronze/Silver para series temporais                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ C - Governanca e Seguranca                         [MVP ▓▓░░]  │    │
│  │     RBAC + Audit Log                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ B - Energy Graph Brasil (Ontologia + MDM)          [MVP ▓▓▓░]  │    │
│  │     Dominio fisico + operacao (Neo4j)                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ A - Conectores e Ingestao                          [MVP ▓▓▓▓]  │    │
│  │     SCADA/Historian + Cadastro de ativos                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Legenda: ▓ = implementado no MVP    ░ = escopo futuro/parcial
```

### 1.2 Diagrama de Componentes do MVP

```
                           ┌──────────────────────┐
                           │    Next.js Frontend   │
                           │   (Dashboard/Alerts)  │
                           └──────────┬───────────┘
                                      │ HTTPS / WSS
                                      ▼
                           ┌──────────────────────┐
                           │   FastAPI Gateway     │
                           │  (Auth + Routing)     │
                           └──┬────┬────┬────┬────┘
                              │    │    │    │
               ┌──────────────┘    │    │    └──────────────┐
               ▼                   ▼    ▼                   ▼
    ┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
    │   TimescaleDB    │  │     Neo4j      │  │      Redis       │
    │  (Time-Series)   │  │ (Energy Graph) │  │  (Cache/Broker)  │
    └──────────────────┘  └────────────────┘  └───────┬──────────┘
                                                      │
                                               ┌──────┴──────┐
                                               │   Celery    │
                                               │  (Workers)  │
                                               └──────┬──────┘
                                                      │
                                          ┌───────────┼───────────┐
                                          ▼           ▼           ▼
                                    ┌──────────┐┌──────────┐┌──────────┐
                                    │Ingestion ││Analytics ││  Alert   │
                                    │ Pipeline ││  Engine  ││ Engine   │
                                    └──────────┘└──────────┘└──────────┘
```

### 1.3 Mapeamento Camada -> Componente

| Camada | Componente(s) MVP | Status |
|--------|-------------------|--------|
| A - Conectores | Ingestion Pipeline (Celery tasks) | Ativo |
| B - Energy Graph | Neo4j + Graph Service | Ativo |
| C - Governanca | JWT Auth + RBAC + Audit Log | Ativo (basico) |
| D - Data Products | TimescaleDB continuous aggregates | Ativo (bronze/silver) |
| E - Motor Analitico | ML Pipeline (scikit-learn/PyOD/Prophet) | Ativo |
| F - Workflows | Case Management Service | Ativo (basico) |
| G - IA Aplicada | Alert Classification (regras + ML) | Parcial |
| H - Multiempresa | -- | Futuro |

---

## 2. Componentes do Sistema

### 2.1 API Gateway (FastAPI)

**Responsabilidade:** Ponto unico de entrada para todas as requisicoes HTTP e WebSocket. Gerencia autenticacao, autorizacao, rate limiting, validacao de payload e roteamento para servicos internos.

**Tecnologia:** Python 3.12, FastAPI, Pydantic v2, Uvicorn (ASGI)

**Estrutura de Rotas:**

```
/api/v1/
├── auth/
│   ├── POST   /login              # JWT token (access + refresh)
│   ├── POST   /refresh             # Refresh token
│   └── POST   /logout              # Revoke token
│
├── assets/
│   ├── GET    /                    # Listar ativos (filtros, paginacao)
│   ├── POST   /                    # Cadastrar ativo
│   ├── GET    /{asset_id}          # Detalhe do ativo
│   ├── PUT    /{asset_id}          # Atualizar ativo
│   ├── GET    /{asset_id}/health   # Health score atual + historico
│   ├── GET    /{asset_id}/measurements  # Series temporais
│   └── GET    /{asset_id}/alerts   # Alertas do ativo
│
├── alerts/
│   ├── GET    /                    # Listar alertas (filtros, paginacao)
│   ├── GET    /{alert_id}          # Detalhe do alerta
│   ├── PUT    /{alert_id}/ack      # Acknowledge alerta
│   └── POST   /{alert_id}/case     # Criar case a partir do alerta
│
├── cases/
│   ├── GET    /                    # Listar cases
│   ├── POST   /                    # Criar case
│   ├── GET    /{case_id}           # Detalhe do case
│   ├── PUT    /{case_id}           # Atualizar case
│   └── POST   /{case_id}/comments  # Adicionar comentario
│
├── measurements/
│   ├── POST   /ingest              # Ingestao batch de medicoes
│   └── GET    /latest/{asset_id}   # Ultima medicao por ativo
│
├── graph/
│   ├── GET    /topology            # Topologia do grafo (subconjunto)
│   ├── GET    /neighbors/{node_id} # Nos vizinhos
│   └── GET    /impact/{asset_id}   # Analise de impacto
│
├── analytics/
│   ├── GET    /anomalies           # Anomalias detectadas
│   ├── GET    /forecast/{asset_id} # Previsao de degradacao
│   └── GET    /dashboard/summary   # KPIs consolidados
│
└── ws/
    └── WS     /alerts              # WebSocket para alertas real-time
```

**Configuracao de Middleware:**

```python
# src/backend/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "OntoGrid"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Databases
    TIMESCALE_URL: str = "postgresql+asyncpg://ontogrid:ontogrid@localhost:5432/ontogrid"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
```

**Middleware Stack:**

```python
# src/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(title="OntoGrid API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Request ID + Audit Logging
app.add_middleware(RequestIdMiddleware)
app.add_middleware(AuditLogMiddleware)
```

**Interfaces:**

| Direcao | Protocolo | Destino |
|---------|-----------|---------|
| Entrada | HTTP/HTTPS | Clientes (frontend, integradores) |
| Entrada | WebSocket | Frontend (alertas real-time) |
| Saida | asyncpg | TimescaleDB |
| Saida | neo4j-driver | Neo4j |
| Saida | aioredis | Redis |
| Saida | Celery | Workers (via Redis broker) |

**Dependencias:** uvicorn, fastapi, pydantic, python-jose (JWT), slowapi, asyncpg, neo4j, redis

---

### 2.2 TimescaleDB (Time-Series)

**Responsabilidade:** Armazenar e consultar series temporais de medicoes SCADA com alta performance. Suporta continuous aggregates para Data Products (bronze -> silver) e retention policies para gestao do ciclo de vida dos dados.

**Tecnologia:** PostgreSQL 16 + TimescaleDB 2.x

**Schema Principal:**

```sql
-- =============================================================
-- TABELAS DIMENSIONAIS (PostgreSQL regular)
-- =============================================================

CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    cnpj            VARCHAR(18) UNIQUE,
    agent_type      VARCHAR(50) NOT NULL,  -- 'generator', 'transmitter', 'distributor'
    ons_code        VARCHAR(20),
    ccee_code       VARCHAR(20),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE substations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    agent_id        UUID REFERENCES agents(id),
    ons_code        VARCHAR(20),
    voltage_level   NUMERIC(10, 2),       -- kV
    latitude        NUMERIC(10, 7),
    longitude       NUMERIC(10, 7),
    region          VARCHAR(10),          -- 'SE', 'S', 'NE', 'N', 'CO'
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    asset_type      VARCHAR(50) NOT NULL,  -- 'transformer', 'generator', 'breaker', 'reactor'
    substation_id   UUID REFERENCES substations(id),
    manufacturer    VARCHAR(255),
    model           VARCHAR(255),
    serial_number   VARCHAR(100),
    year_installed  INTEGER,
    rated_power     NUMERIC(12, 2),       -- MVA ou MW
    rated_voltage   NUMERIC(10, 2),       -- kV
    status          VARCHAR(20) DEFAULT 'active',  -- 'active', 'maintenance', 'decommissioned'
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_substation ON assets(substation_id);
CREATE INDEX idx_assets_status ON assets(status);

CREATE TABLE measurement_points (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID REFERENCES assets(id),
    point_name      VARCHAR(100) NOT NULL,  -- 'winding_temp_1', 'oil_temp_top'
    signal_type     VARCHAR(50) NOT NULL,   -- 'temperature', 'vibration', 'current', 'voltage', 'oil_level'
    unit            VARCHAR(20) NOT NULL,   -- 'celsius', 'mm_s', 'ampere', 'kv', 'percent'
    min_range       NUMERIC(12, 4),
    max_range       NUMERIC(12, 4),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mp_asset ON measurement_points(asset_id);
CREATE INDEX idx_mp_signal_type ON measurement_points(signal_type);

-- =============================================================
-- HYPERTABLE: MEDICOES SCADA (TimescaleDB)
-- =============================================================

CREATE TABLE measurements (
    time            TIMESTAMPTZ NOT NULL,
    point_id        UUID NOT NULL REFERENCES measurement_points(id),
    asset_id        UUID NOT NULL,         -- desnormalizado para performance
    value           DOUBLE PRECISION NOT NULL,
    quality         SMALLINT DEFAULT 0,    -- 0=good, 1=uncertain, 2=bad, 3=missing
    source          VARCHAR(20) DEFAULT 'scada'  -- 'scada', 'manual', 'calculated'
);

-- Converter para hypertable particionada por tempo
SELECT create_hypertable(
    'measurements',
    by_range('time'),
    chunk_time_interval => INTERVAL '1 day'
);

-- Indice composto para queries por ativo + tempo
CREATE INDEX idx_measurements_asset_time
    ON measurements (asset_id, time DESC);

-- Indice para queries por ponto de medicao
CREATE INDEX idx_measurements_point_time
    ON measurements (point_id, time DESC);

-- =============================================================
-- HYPERTABLE: HEALTH SCORES
-- =============================================================

CREATE TABLE health_scores (
    time            TIMESTAMPTZ NOT NULL,
    asset_id        UUID NOT NULL,
    overall_score   NUMERIC(5, 2) NOT NULL,  -- 0.00 a 100.00
    components      JSONB NOT NULL,           -- scores por componente
    anomaly_count   INTEGER DEFAULT 0,
    model_version   VARCHAR(20),
    confidence      NUMERIC(5, 4)             -- 0.0000 a 1.0000
);

SELECT create_hypertable('health_scores', by_range('time'), chunk_time_interval => INTERVAL '1 day');
CREATE INDEX idx_health_asset_time ON health_scores (asset_id, time DESC);

-- =============================================================
-- HYPERTABLE: ALERTAS
-- =============================================================

CREATE TABLE alerts (
    id              UUID DEFAULT gen_random_uuid(),
    time            TIMESTAMPTZ NOT NULL,
    asset_id        UUID NOT NULL,
    severity        VARCHAR(10) NOT NULL,    -- 'critical', 'high', 'medium', 'low'
    alert_type      VARCHAR(50) NOT NULL,    -- 'anomaly', 'threshold', 'trend', 'forecast'
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    signal_type     VARCHAR(50),
    current_value   DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    status          VARCHAR(20) DEFAULT 'open',  -- 'open', 'acknowledged', 'resolved', 'false_positive'
    acknowledged_by UUID,
    acknowledged_at TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}'
);

SELECT create_hypertable('alerts', by_range('time'), chunk_time_interval => INTERVAL '7 days');
CREATE INDEX idx_alerts_asset_status ON alerts (asset_id, status, time DESC);
CREATE INDEX idx_alerts_severity ON alerts (severity, time DESC);

-- =============================================================
-- TABELA: CASES (Nao e hypertable - volume baixo)
-- =============================================================

CREATE TABLE cases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    asset_id        UUID REFERENCES assets(id),
    alert_id        UUID,
    priority        VARCHAR(10) NOT NULL,   -- 'critical', 'high', 'medium', 'low'
    status          VARCHAR(20) DEFAULT 'open',  -- 'open', 'in_progress', 'resolved', 'closed'
    assigned_to     UUID,
    sop_id          UUID,
    created_by      UUID NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

-- =============================================================
-- RETENTION POLICIES
-- =============================================================

-- Dados brutos: manter 2 anos
SELECT add_retention_policy('measurements', INTERVAL '2 years');

-- Health scores: manter 5 anos
SELECT add_retention_policy('health_scores', INTERVAL '5 years');

-- Alertas: manter 3 anos
SELECT add_retention_policy('alerts', INTERVAL '3 years');

-- =============================================================
-- CONTINUOUS AGGREGATES (Data Products Silver)
-- =============================================================

-- Agregacao horaria das medicoes (silver layer)
CREATE MATERIALIZED VIEW measurements_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    asset_id,
    point_id,
    AVG(value)    AS avg_value,
    MIN(value)    AS min_value,
    MAX(value)    AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*)      AS sample_count,
    COUNT(*) FILTER (WHERE quality = 0) AS good_count
FROM measurements
GROUP BY bucket, asset_id, point_id
WITH NO DATA;

-- Refresh policy: atualizar a cada 30 minutos
SELECT add_continuous_aggregate_policy('measurements_hourly',
    start_offset    => INTERVAL '3 hours',
    end_offset      => INTERVAL '30 minutes',
    schedule_interval => INTERVAL '30 minutes'
);

-- Agregacao diaria (silver layer)
CREATE MATERIALIZED VIEW measurements_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    asset_id,
    point_id,
    AVG(value)    AS avg_value,
    MIN(value)    AS min_value,
    MAX(value)    AS max_value,
    STDDEV(value) AS stddev_value,
    COUNT(*)      AS sample_count
FROM measurements
GROUP BY bucket, asset_id, point_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy('measurements_daily',
    start_offset    => INTERVAL '3 days',
    end_offset      => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);
```

**Modelo de Dados - Diagrama ER:**

```
┌────────────┐     ┌──────────────┐     ┌───────────────────┐
│   agents   │────<│  substations │────<│      assets       │
│            │  1:N│              │  1:N│                   │
│ id (PK)    │     │ id (PK)      │     │ id (PK)          │
│ name       │     │ name         │     │ name             │
│ cnpj       │     │ agent_id(FK) │     │ asset_type       │
│ agent_type │     │ ons_code     │     │ substation_id(FK)│
│ ons_code   │     │ voltage_level│     │ rated_power      │
└────────────┘     └──────────────┘     │ status           │
                                         └────────┬──────────┘
                                                   │ 1:N
                                         ┌─────────┴──────────┐
                                         │ measurement_points │
                                         │                    │
                                         │ id (PK)            │
                                         │ asset_id (FK)      │
                                         │ signal_type        │
                                         │ unit               │
                                         └─────────┬──────────┘
                                                   │ 1:N
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                   ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐
                   │  measurements    │ │  health_scores   │ │    alerts    │
                   │  (hypertable)    │ │  (hypertable)    │ │ (hypertable) │
                   │                  │ │                  │ │              │
                   │ time (PK)        │ │ time (PK)        │ │ time (PK)   │
                   │ point_id         │ │ asset_id         │ │ asset_id    │
                   │ asset_id         │ │ overall_score    │ │ severity    │
                   │ value            │ │ components (JSON)│ │ alert_type  │
                   │ quality          │ │ model_version    │ │ status      │
                   └──────────────────┘ └──────────────────┘ └──────────────┘
```

**Interfaces:**

| Direcao | Protocolo | Origem/Destino |
|---------|-----------|----------------|
| Entrada | asyncpg (TCP 5432) | FastAPI (leitura/escrita) |
| Entrada | asyncpg (TCP 5432) | Celery workers (escrita bulk) |
| Saida | Continuous aggregates | Views materializadas internas |

**Dependencias:** PostgreSQL 16, TimescaleDB extension 2.x

---

### 2.3 Neo4j (Energy Graph)

**Responsabilidade:** Modelar a topologia eletrica e relacoes semanticas do setor como um grafo. Permite queries de impacto, dependencia, vizinhanca e navegacao topologica que seriam impraticaveis em modelo relacional.

**Tecnologia:** Neo4j 5.x, Cypher Query Language, neo4j Python driver (async)

**Modelo de Nos (Nodes):**

```
┌────────────────────────────────────────────────────────────────────┐
│                     ENERGY GRAPH - NOS (NODES)                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  (:Agent)                                                          │
│  ├── id: UUID                                                      │
│  ├── name: String                                                  │
│  ├── cnpj: String                                                  │
│  ├── type: "generator" | "transmitter" | "distributor"             │
│  └── ons_code: String                                              │
│                                                                    │
│  (:Substation)                                                     │
│  ├── id: UUID                                                      │
│  ├── name: String                                                  │
│  ├── ons_code: String                                              │
│  ├── voltage_level: Float (kV)                                     │
│  ├── latitude: Float                                               │
│  └── longitude: Float                                              │
│                                                                    │
│  (:Asset)                                                          │
│  ├── id: UUID                                                      │
│  ├── name: String                                                  │
│  ├── type: "transformer" | "generator" | "breaker" | "reactor"     │
│  ├── rated_power: Float (MVA)                                      │
│  ├── rated_voltage: Float (kV)                                     │
│  ├── status: "active" | "maintenance" | "decommissioned"           │
│  └── health_score: Float (0-100)                                   │
│                                                                    │
│  (:TransmissionLine)                                               │
│  ├── id: UUID                                                      │
│  ├── name: String                                                  │
│  ├── ons_code: String                                              │
│  ├── voltage_level: Float (kV)                                     │
│  ├── length_km: Float                                              │
│  └── capacity: Float (MW)                                          │
│                                                                    │
│  (:MeasurementPoint)                                               │
│  ├── id: UUID                                                      │
│  ├── name: String                                                  │
│  ├── signal_type: String                                           │
│  └── unit: String                                                  │
│                                                                    │
│  (:Alert)                                                          │
│  ├── id: UUID                                                      │
│  ├── severity: String                                              │
│  ├── type: String                                                  │
│  └── created_at: DateTime                                          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Modelo de Relacoes (Relationships):**

```
(:Agent)-[:OWNS]->(:Substation)
(:Substation)-[:CONTAINS]->(:Asset)
(:Asset)-[:BELONGS_TO]->(:Substation)
(:Asset)-[:CONNECTED_TO {type: "electrical"}]->(:Asset)
(:Asset)-[:MONITORED_BY]->(:MeasurementPoint)
(:Asset)-[:DEPENDS_ON {criticality: "high"}]->(:Asset)
(:TransmissionLine)-[:CONNECTS]->(:Substation)
(:Alert)-[:AFFECTS]->(:Asset)
(:Asset)-[:PART_OF]->(:TransmissionLine)
```

**Diagrama Visual do Grafo:**

```
                         ┌──────────┐
                         │  Agent   │
                         │ (CPFL)   │
                         └────┬─────┘
                              │ OWNS
                    ┌─────────┴─────────┐
                    ▼                   ▼
             ┌────────────┐      ┌────────────┐
             │ Substation │      │ Substation │
             │  (SE-001)  │      │  (SE-002)  │
             └──┬──────┬──┘      └──┬─────────┘
                │      │            │
          CONTAINS   CONTAINS    CONTAINS
                │      │            │
           ┌────▼──┐ ┌─▼────────┐ ┌▼──────────┐
           │ Asset  │ │  Asset   │ │   Asset   │
           │Transf. │ │ Breaker  │ │  Transf.  │
           │(TR-01) │ │(DJ-01)  │ │ (TR-02)   │
           └──┬──┬──┘ └────┬────┘ └─────┬─────┘
              │  │    CONNECTED_TO       │
              │  └──────────┘     DEPENDS_ON
              │                         │
         MONITORED_BY              ┌────┘
              │                    │
      ┌───────┼────────┐          │
      ▼       ▼        ▼          ▼
   ┌─────┐ ┌─────┐ ┌──────┐  ┌────────┐
   │Temp │ │Vibr.│ │Oil Lv│  │ TLine  │
   │Point│ │Point│ │Point │  │(LT-500)│
   └─────┘ └─────┘ └──────┘  └────────┘
```

**Queries Cypher Mais Comuns:**

```cypher
// 1. Obter topologia de uma subestacao com todos os ativos
MATCH (s:Substation {id: $substation_id})-[:CONTAINS]->(a:Asset)
OPTIONAL MATCH (a)-[:MONITORED_BY]->(mp:MeasurementPoint)
RETURN s, a, mp

// 2. Analise de impacto: o que e afetado se um ativo falhar?
MATCH (a:Asset {id: $asset_id})
CALL apoc.path.subgraphAll(a, {
    relationshipFilter: "CONNECTED_TO|DEPENDS_ON",
    maxLevel: 3
})
YIELD nodes, relationships
RETURN nodes, relationships

// 3. Ativos criticos com health score baixo
MATCH (a:Asset)
WHERE a.health_score < 50 AND a.status = 'active'
MATCH (a)-[:BELONGS_TO]->(s:Substation)-[:CONTAINS]->(:Asset)
WITH a, s, COUNT(*) AS assets_in_substation
RETURN a.name, a.type, a.health_score, s.name AS substation,
       assets_in_substation
ORDER BY a.health_score ASC

// 4. Caminho entre dois ativos (topologia eletrica)
MATCH path = shortestPath(
    (a1:Asset {id: $asset_id_1})-[:CONNECTED_TO*..10]-(a2:Asset {id: $asset_id_2})
)
RETURN path

// 5. Ativos que dependem de um equipamento especifico
MATCH (dependent:Asset)-[:DEPENDS_ON*1..3]->(target:Asset {id: $asset_id})
RETURN dependent.name, dependent.type, dependent.health_score

// 6. Subestacoes de um agente com contagem de alertas ativos
MATCH (ag:Agent {id: $agent_id})-[:OWNS]->(s:Substation)-[:CONTAINS]->(a:Asset)
OPTIONAL MATCH (alert:Alert)-[:AFFECTS]->(a) WHERE alert.status = 'open'
WITH s, COUNT(DISTINCT a) AS asset_count, COUNT(alert) AS open_alerts
RETURN s.name, s.voltage_level, asset_count, open_alerts
ORDER BY open_alerts DESC
```

**Indexacao:**

```cypher
-- Indices de unicidade
CREATE CONSTRAINT asset_id_unique FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT substation_id_unique FOR (s:Substation) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT agent_id_unique FOR (ag:Agent) REQUIRE ag.id IS UNIQUE;
CREATE CONSTRAINT tline_id_unique FOR (tl:TransmissionLine) REQUIRE tl.id IS UNIQUE;
CREATE CONSTRAINT mp_id_unique FOR (mp:MeasurementPoint) REQUIRE mp.id IS UNIQUE;

-- Indices de busca
CREATE INDEX asset_type_idx FOR (a:Asset) ON (a.type);
CREATE INDEX asset_status_idx FOR (a:Asset) ON (a.status);
CREATE INDEX asset_health_idx FOR (a:Asset) ON (a.health_score);
CREATE INDEX substation_ons_idx FOR (s:Substation) ON (s.ons_code);
CREATE INDEX agent_type_idx FOR (ag:Agent) ON (ag.type);

-- Full-text search
CREATE FULLTEXT INDEX asset_search FOR (a:Asset) ON EACH [a.name, a.type];
```

**Interfaces:**

| Direcao | Protocolo | Origem/Destino |
|---------|-----------|----------------|
| Entrada | Bolt (TCP 7687) | FastAPI (queries) |
| Entrada | Bolt (TCP 7687) | Celery workers (atualizacao de health score) |
| Saida | -- | Dados servidos via API |

**Dependencias:** Neo4j 5.x, APOC plugin (para queries de grafo avancadas)

---

### 2.4 Redis + Celery

**Responsabilidade:**
- **Redis:** Cache de health scores, alertas ativos e resultados de queries frequentes. Broker de mensagens para Celery. Pub/Sub para WebSocket de alertas.
- **Celery:** Execucao assincrona de tasks pesadas (ingestao, calculo de health score, deteccao de anomalias, notificacoes).

**Tecnologia:** Redis 7.x, Celery 5.x, celery-beat (scheduler)

**Estrutura de Cache (Redis):**

```
# Namespaces e TTLs

# Health scores por ativo (TTL: 5 min)
health:{asset_id}                -> JSON { score, components, updated_at }

# Alertas ativos por ativo (TTL: 1 min)
alerts:active:{asset_id}         -> JSON [ { id, severity, title, time } ]

# Dashboard KPIs consolidados (TTL: 2 min)
dashboard:summary                -> JSON { total_assets, avg_health, critical_count, ... }

# Ultima medicao por ponto (TTL: 30 sec)
measurement:latest:{point_id}    -> JSON { value, quality, time }

# Topologia do grafo (cache) (TTL: 10 min)
graph:topology:{substation_id}   -> JSON { nodes, edges }

# Sessions de usuario (TTL: conforme JWT)
session:{user_id}                -> JSON { roles, permissions, last_access }
```

**Filas Celery:**

```python
# src/backend/core/celery_app.py

from celery import Celery
from celery.schedules import crontab

celery_app = Celery("ontogrid")

celery_app.conf.task_routes = {
    # Fila de ingestao - alta throughput
    "ingestion.*": {"queue": "ingestion_queue"},

    # Fila de alertas - baixa latencia
    "alerts.*": {"queue": "alert_queue"},

    # Fila de analytics - tasks pesadas (ML)
    "analytics.*": {"queue": "analytics_queue"},
}

# Tasks periodicas (beat schedule)
celery_app.conf.beat_schedule = {
    # Recalcular health scores a cada 5 minutos
    "recalc-health-scores": {
        "task": "analytics.recalculate_health_scores",
        "schedule": 300.0,  # 5 min
        "options": {"queue": "analytics_queue"},
    },

    # Verificacao de qualidade de dados a cada 15 min
    "data-quality-check": {
        "task": "ingestion.check_data_quality",
        "schedule": 900.0,  # 15 min
        "options": {"queue": "ingestion_queue"},
    },

    # Limpar alertas expirados diariamente
    "cleanup-expired-alerts": {
        "task": "alerts.cleanup_expired",
        "schedule": crontab(hour=2, minute=0),  # 02:00
        "options": {"queue": "alert_queue"},
    },

    # Forecast de degradacao diario
    "daily-forecast": {
        "task": "analytics.run_degradation_forecast",
        "schedule": crontab(hour=3, minute=0),  # 03:00
        "options": {"queue": "analytics_queue"},
    },

    # Sincronizar health scores no Neo4j a cada 10 min
    "sync-graph-health": {
        "task": "analytics.sync_health_to_graph",
        "schedule": 600.0,  # 10 min
        "options": {"queue": "analytics_queue"},
    },
}
```

**Diagrama de Filas:**

```
                    ┌─────────────────────┐
                    │    Redis Broker      │
                    │    (DB 1)            │
                    └──┬──────┬──────┬────┘
                       │      │      │
            ┌──────────┘      │      └──────────┐
            ▼                 ▼                  ▼
   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
   │ingestion_queue │ │  alert_queue   │ │analytics_queue │
   │                │ │                │ │                │
   │ - batch_ingest │ │ - evaluate     │ │ - recalc_health│
   │ - validate     │ │ - notify       │ │ - detect_anom. │
   │ - transform    │ │ - escalate     │ │ - forecast     │
   │ - quality_check│ │ - cleanup      │ │ - sync_graph   │
   └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
           │                  │                   │
           ▼                  ▼                   ▼
   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
   │  Worker Pool   │ │  Worker Pool   │ │  Worker Pool   │
   │  (2 workers)   │ │  (2 workers)   │ │  (2 workers)   │
   │  concurrency=4 │ │  concurrency=2 │ │  concurrency=2 │
   └────────────────┘ └────────────────┘ └────────────────┘
```

**WebSocket via Redis Pub/Sub:**

```python
# src/backend/api/ws/alerts.py

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

class AlertWebSocketManager:
    """Gerencia conexoes WebSocket para alertas real-time."""

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def subscribe_alerts(self, websocket: WebSocket, user_id: str):
        """Subscreve usuario a alertas via Redis Pub/Sub."""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("alerts:new")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    alert_data = json.loads(message["data"])
                    # Filtrar por permissoes do usuario
                    if self._user_can_see(user_id, alert_data):
                        await websocket.send_json(alert_data)
        except WebSocketDisconnect:
            await pubsub.unsubscribe("alerts:new")
```

**Interfaces:**

| Direcao | Protocolo | Origem/Destino |
|---------|-----------|----------------|
| Entrada | TCP 6379 (DB 0) | FastAPI (cache reads/writes) |
| Entrada | TCP 6379 (DB 1) | Celery (broker) |
| Entrada | TCP 6379 (DB 2) | Celery (result backend) |
| Interna | Pub/Sub | WebSocket manager <-> Alert tasks |

**Dependencias:** redis, celery, celery[redis], aioredis

---

### 2.5 ML Pipeline

**Responsabilidade:** Detectar anomalias em series temporais SCADA, calcular health scores por equipamento, e prever degradacao futura. Todos os modelos devem ser explicaveis e versionados.

**Tecnologia:** scikit-learn, PyOD, Prophet, joblib (serialization)

#### 2.5.1 Anomaly Detection

```python
# src/backend/analytics/anomaly_detection.py

from dataclasses import dataclass
from enum import Enum
import numpy as np
from pyod.models.iforest import IForest
from pyod.models.ecod import ECOD
from sklearn.cluster import DBSCAN
from scipy import stats

class AnomalyMethod(str, Enum):
    ISOLATION_FOREST = "isolation_forest"
    ZSCORE = "zscore"
    DBSCAN = "dbscan"
    ECOD = "ecod"  # Empirical Cumulative Distribution

@dataclass
class AnomalyResult:
    is_anomaly: bool
    score: float          # 0.0 (normal) a 1.0 (anomalo)
    method: AnomalyMethod
    explanation: str
    contributing_features: list[str]

class AnomalyDetector:
    """
    Pipeline multi-metodo de deteccao de anomalias.
    Usa ensemble de metodos para reduzir falsos positivos.
    """

    def __init__(self, config: dict):
        self.contamination = config.get("contamination", 0.05)
        self.zscore_threshold = config.get("zscore_threshold", 3.0)
        self.ensemble_threshold = config.get("ensemble_threshold", 0.6)

        self.detectors = {
            AnomalyMethod.ISOLATION_FOREST: IForest(
                contamination=self.contamination,
                n_estimators=200,
                random_state=42
            ),
            AnomalyMethod.ECOD: ECOD(
                contamination=self.contamination
            ),
        }

    def detect(self, data: np.ndarray, feature_names: list[str]) -> list[AnomalyResult]:
        """
        Detecta anomalias usando ensemble de metodos.

        Args:
            data: Array (n_samples, n_features) com medicoes
            feature_names: Nomes das features (signal types)

        Returns:
            Lista de AnomalyResult para cada amostra
        """
        results = {}

        # Metodo 1: Isolation Forest
        self.detectors[AnomalyMethod.ISOLATION_FOREST].fit(data)
        if_scores = self.detectors[AnomalyMethod.ISOLATION_FOREST].decision_scores_

        # Metodo 2: Z-Score (por feature)
        z_scores = np.abs(stats.zscore(data, axis=0))
        z_anomalies = np.any(z_scores > self.zscore_threshold, axis=1)

        # Metodo 3: ECOD
        self.detectors[AnomalyMethod.ECOD].fit(data)
        ecod_scores = self.detectors[AnomalyMethod.ECOD].decision_scores_

        # Ensemble: media ponderada dos scores normalizados
        normalized_if = self._normalize(if_scores)
        normalized_ecod = self._normalize(ecod_scores)
        z_score_max = np.max(z_scores, axis=1) / self.zscore_threshold

        ensemble_scores = (
            0.4 * normalized_if +
            0.3 * normalized_ecod +
            0.3 * np.clip(z_score_max, 0, 1)
        )

        # Gerar resultados com explicabilidade
        anomaly_results = []
        for i in range(len(data)):
            is_anomaly = ensemble_scores[i] > self.ensemble_threshold
            contributing = self._get_contributing_features(
                data[i], z_scores[i], feature_names
            )
            anomaly_results.append(AnomalyResult(
                is_anomaly=is_anomaly,
                score=float(ensemble_scores[i]),
                method=AnomalyMethod.ISOLATION_FOREST,  # metodo principal
                explanation=self._generate_explanation(
                    is_anomaly, ensemble_scores[i], contributing
                ),
                contributing_features=contributing
            ))

        return anomaly_results

    def _get_contributing_features(
        self, sample: np.ndarray, z_scores: np.ndarray, names: list[str]
    ) -> list[str]:
        """Identifica quais features mais contribuiram para a anomalia."""
        high_z = np.where(z_scores > self.zscore_threshold * 0.7)[0]
        return [names[i] for i in high_z]

    def _generate_explanation(
        self, is_anomaly: bool, score: float, features: list[str]
    ) -> str:
        if not is_anomaly:
            return "Comportamento dentro dos padroes normais."
        feature_str = ", ".join(features) if features else "multiplas variaveis"
        return (
            f"Anomalia detectada (score: {score:.2f}). "
            f"Variaveis contribuintes: {feature_str}."
        )

    @staticmethod
    def _normalize(scores: np.ndarray) -> np.ndarray:
        min_s, max_s = scores.min(), scores.max()
        if max_s - min_s == 0:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)
```

#### 2.5.2 Health Score

```python
# src/backend/analytics/health_score.py

@dataclass
class HealthScoreConfig:
    """Configuracao de pesos para calculo de health score por tipo de ativo."""

    weights: dict[str, float]  # signal_type -> peso
    thresholds: dict[str, dict]  # signal_type -> {warning, critical}

# Configuracoes por tipo de equipamento
TRANSFORMER_CONFIG = HealthScoreConfig(
    weights={
        "temperature":  0.30,   # Temperatura do enrolamento
        "oil_level":    0.25,   # Nivel de oleo isolante
        "vibration":    0.20,   # Vibracoes
        "current":      0.15,   # Corrente
        "voltage":      0.10,   # Tensao
    },
    thresholds={
        "temperature": {"warning": 85.0, "critical": 105.0, "unit": "celsius"},
        "oil_level":   {"warning": 70.0, "critical": 50.0, "unit": "percent"},
        "vibration":   {"warning": 4.5,  "critical": 7.0,  "unit": "mm_s"},
        "current":     {"warning": 0.90, "critical": 1.05, "unit": "pu"},
        "voltage":     {"warning": 0.95, "critical": 0.90, "unit": "pu"},
    }
)

GENERATOR_CONFIG = HealthScoreConfig(
    weights={
        "temperature":  0.25,
        "vibration":    0.30,
        "current":      0.20,
        "voltage":      0.15,
        "oil_level":    0.10,
    },
    thresholds={
        "temperature": {"warning": 80.0, "critical": 100.0, "unit": "celsius"},
        "vibration":   {"warning": 3.5,  "critical": 6.0,  "unit": "mm_s"},
        "current":     {"warning": 0.92, "critical": 1.05, "unit": "pu"},
        "voltage":     {"warning": 0.95, "critical": 0.88, "unit": "pu"},
        "oil_level":   {"warning": 75.0, "critical": 55.0, "unit": "percent"},
    }
)

class HealthScoreCalculator:
    """
    Calcula health score multi-variavel para equipamentos.

    Score final: 0-100 onde:
    - 90-100: Excelente
    - 70-89:  Bom
    - 50-69:  Atencao
    - 30-49:  Alerta
    - 0-29:   Critico
    """

    CONFIG_MAP = {
        "transformer": TRANSFORMER_CONFIG,
        "generator": GENERATOR_CONFIG,
    }

    def calculate(
        self,
        asset_type: str,
        current_values: dict[str, float],
        historical_stats: dict[str, dict],
        anomaly_scores: dict[str, float],
    ) -> dict:
        config = self.CONFIG_MAP.get(asset_type, TRANSFORMER_CONFIG)
        component_scores = {}
        weighted_sum = 0.0
        total_weight = 0.0

        for signal_type, weight in config.weights.items():
            if signal_type not in current_values:
                continue

            value = current_values[signal_type]
            threshold = config.thresholds[signal_type]

            # Score baseado na distancia ao threshold
            component_score = self._signal_score(value, threshold)

            # Penalidade por anomalia
            anomaly_penalty = anomaly_scores.get(signal_type, 0.0) * 15
            component_score = max(0, component_score - anomaly_penalty)

            # Penalidade por tendencia de degradacao
            if signal_type in historical_stats:
                trend_penalty = self._trend_penalty(historical_stats[signal_type])
                component_score = max(0, component_score - trend_penalty)

            component_scores[signal_type] = round(component_score, 2)
            weighted_sum += component_score * weight
            total_weight += weight

        overall = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0

        return {
            "overall_score": overall,
            "components": component_scores,
            "severity": self._score_to_severity(overall),
            "model_version": "1.0.0",
        }

    def _signal_score(self, value: float, threshold: dict) -> float:
        """Converte valor de medicao em score 0-100."""
        warning = threshold["warning"]
        critical = threshold["critical"]

        # Para metricas onde menor = pior (ex: oil_level)
        if warning > critical:
            if value >= warning:
                return 100.0
            elif value <= critical:
                return 0.0
            else:
                return ((value - critical) / (warning - critical)) * 100.0
        # Para metricas onde maior = pior (ex: temperature)
        else:
            if value <= warning:
                return 100.0
            elif value >= critical:
                return 0.0
            else:
                return ((critical - value) / (critical - warning)) * 100.0

    @staticmethod
    def _score_to_severity(score: float) -> str:
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "attention"
        elif score >= 30:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def _trend_penalty(stats: dict) -> float:
        """Penaliza score se tendencia de degradacao for detectada."""
        trend_slope = stats.get("slope_7d", 0.0)
        if trend_slope > 0.5:  # degradacao rapida
            return 10.0
        elif trend_slope > 0.1:  # degradacao gradual
            return 5.0
        return 0.0
```

#### 2.5.3 Prophet Forecasting

```python
# src/backend/analytics/forecasting.py

from prophet import Prophet
import pandas as pd

class DegradationForecaster:
    """
    Previsao de degradacao de equipamentos usando Prophet.
    Gera previsoes de 7, 14 e 30 dias para cada variavel SCADA.
    """

    def __init__(self):
        self.forecast_horizons = [7, 14, 30]  # dias

    def forecast(
        self,
        historical_data: pd.DataFrame,
        signal_type: str,
        threshold: dict,
    ) -> dict:
        """
        Args:
            historical_data: DataFrame com colunas ['ds', 'y'] (timestamp, value)
            signal_type: Tipo de sinal para contextualizacao
            threshold: {'warning': float, 'critical': float}

        Returns:
            Dict com previsoes e estimativa de dias ate threshold
        """
        model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,  # MVP nao tem 1 ano de dados
        )

        model.fit(historical_data)

        # Forecast para 30 dias
        future = model.make_future_dataframe(periods=30, freq="H")
        forecast = model.predict(future)

        # Estimar dias ate atingir threshold critico
        days_to_critical = self._estimate_days_to_threshold(
            forecast, threshold["critical"], signal_type
        )

        # Estimar dias ate atingir threshold de warning
        days_to_warning = self._estimate_days_to_threshold(
            forecast, threshold["warning"], signal_type
        )

        return {
            "signal_type": signal_type,
            "forecast_7d": self._extract_forecast(forecast, 7),
            "forecast_14d": self._extract_forecast(forecast, 14),
            "forecast_30d": self._extract_forecast(forecast, 30),
            "days_to_warning": days_to_warning,
            "days_to_critical": days_to_critical,
            "trend_direction": self._trend_direction(forecast),
            "confidence_interval": 0.95,
        }

    def _estimate_days_to_threshold(
        self, forecast: pd.DataFrame, threshold: float, signal_type: str
    ) -> int | None:
        """Estima quantos dias ate o valor atingir o threshold."""
        future_only = forecast[forecast["ds"] > pd.Timestamp.now()]

        for _, row in future_only.iterrows():
            if signal_type in ("temperature", "vibration", "current"):
                if row["yhat"] >= threshold:
                    return (row["ds"] - pd.Timestamp.now()).days
            else:  # oil_level, voltage - menor = pior
                if row["yhat"] <= threshold:
                    return (row["ds"] - pd.Timestamp.now()).days

        return None  # Nao atinge threshold no horizonte

    @staticmethod
    def _extract_forecast(forecast: pd.DataFrame, days: int) -> dict:
        cutoff = pd.Timestamp.now() + pd.Timedelta(days=days)
        subset = forecast[forecast["ds"] <= cutoff].tail(1)
        if subset.empty:
            return {}
        row = subset.iloc[0]
        return {
            "predicted_value": round(row["yhat"], 2),
            "lower_bound": round(row["yhat_lower"], 2),
            "upper_bound": round(row["yhat_upper"], 2),
        }

    @staticmethod
    def _trend_direction(forecast: pd.DataFrame) -> str:
        recent = forecast.tail(48)  # ultimas 48h de forecast
        slope = (recent["trend"].iloc[-1] - recent["trend"].iloc[0]) / len(recent)
        if slope > 0.01:
            return "degrading"
        elif slope < -0.01:
            return "improving"
        return "stable"
```

#### 2.5.4 Model Versioning e Explicabilidade

```
┌────────────────────────────────────────────────────────────────┐
│                    ML MODEL LIFECYCLE                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. TRAINING                                                   │
│     ├── Dados: ultimos 90 dias de medicoes por tipo de ativo   │
│     ├── Frequencia: semanal (celery beat)                      │
│     └── Saida: modelo serializado (joblib) + metricas          │
│                                                                │
│  2. VERSIONING                                                 │
│     ├── Format: v{major}.{minor}.{patch}                       │
│     ├── Storage: /models/{asset_type}/{version}/model.joblib   │
│     ├── Metadata: /models/{asset_type}/{version}/metadata.json │
│     └── Rollback: manter ultimas 3 versoes                     │
│                                                                │
│  3. INFERENCE                                                  │
│     ├── Modelo carregado em memoria no worker                  │
│     ├── Cache de predicoes no Redis (TTL: 5 min)               │
│     └── Fallback: regras estaticas se modelo falhar            │
│                                                                │
│  4. EXPLICABILIDADE                                            │
│     ├── Feature importance (Isolation Forest)                  │
│     ├── Z-score por variavel contribuinte                      │
│     ├── Comparacao com baseline historico                       │
│     └── Texto explicativo em portugues no alerta               │
│                                                                │
│  metadata.json:                                                │
│  {                                                             │
│    "version": "1.2.0",                                         │
│    "asset_type": "transformer",                                │
│    "trained_at": "2026-03-01T00:00:00Z",                       │
│    "training_samples": 125000,                                 │
│    "features": ["temperature","vibration","current",           │
│                  "voltage","oil_level"],                        │
│    "metrics": {                                                │
│      "precision": 0.92,                                        │
│      "recall": 0.87,                                           │
│      "f1_score": 0.89,                                         │
│      "false_positive_rate": 0.03                               │
│    },                                                          │
│    "contamination": 0.05,                                      │
│    "ensemble_weights": { "if": 0.4, "ecod": 0.3, "z": 0.3 }  │
│  }                                                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Interfaces:**

| Direcao | Protocolo | Origem/Destino |
|---------|-----------|----------------|
| Entrada | Celery task | Dados de TimescaleDB |
| Saida | asyncpg | Health scores -> TimescaleDB |
| Saida | Bolt | Health scores -> Neo4j (propriedade do no) |
| Saida | Redis | Scores/Anomalias -> Cache |
| Saida | Redis Pub/Sub | Alertas -> WebSocket |

**Dependencias:** scikit-learn, pyod, prophet, numpy, pandas, scipy, joblib

---

### 2.6 Frontend (Next.js)

**Responsabilidade:** Interface web para operadores e gestores de manutencao. Dashboard operacional com visualizacao de health scores, alertas em tempo real, series temporais, topologia do grafo eletrico e gestao de cases.

**Tecnologia:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, React Flow

**Estrutura de Paginas:**

```
src/frontend/
├── app/
│   ├── layout.tsx                  # Layout principal (sidebar + header)
│   ├── page.tsx                    # Redirect para /dashboard
│   ├── (auth)/
│   │   ├── login/page.tsx          # Pagina de login
│   │   └── layout.tsx              # Layout sem sidebar
│   ├── dashboard/
│   │   └── page.tsx                # Dashboard principal com KPIs
│   ├── assets/
│   │   ├── page.tsx                # Lista de ativos (tabela + filtros)
│   │   └── [id]/
│   │       └── page.tsx            # Detalhe do ativo (health + charts)
│   ├── alerts/
│   │   └── page.tsx                # Central de alertas
│   ├── cases/
│   │   ├── page.tsx                # Lista de cases
│   │   └── [id]/
│   │       └── page.tsx            # Detalhe do case
│   └── graph/
│       └── page.tsx                # Graph Explorer (topologia)
│
├── components/
│   ├── ui/                         # Componentes base (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   └── ...
│   ├── charts/
│   │   ├── TimeSeriesChart.tsx     # Graficos de series temporais (Recharts)
│   │   ├── HealthGauge.tsx         # Gauge circular do health score
│   │   ├── AnomalyOverlay.tsx      # Overlay de pontos anomalos
│   │   └── ForecastChart.tsx       # Grafico com previsao Prophet
│   ├── alerts/
│   │   ├── AlertTable.tsx          # Tabela de alertas com filtros
│   │   ├── AlertBanner.tsx         # Banner de alertas criticos (topo)
│   │   └── AlertDetail.tsx         # Modal de detalhe do alerta
│   ├── assets/
│   │   ├── AssetCard.tsx           # Card resumo do ativo
│   │   ├── AssetTable.tsx          # Tabela paginada de ativos
│   │   └── HealthHistory.tsx       # Historico de health score
│   ├── graph/
│   │   ├── GraphViz.tsx            # Visualizacao do grafo (React Flow)
│   │   ├── NodeTooltip.tsx         # Tooltip com info do no
│   │   └── ImpactAnalysis.tsx      # Painel de analise de impacto
│   ├── cases/
│   │   ├── CaseTimeline.tsx        # Timeline de eventos do case
│   │   └── CaseForm.tsx            # Formulario de criacao/edicao
│   └── layout/
│       ├── Sidebar.tsx             # Menu lateral de navegacao
│       ├── Header.tsx              # Header com busca + notificacoes
│       └── NotificationBell.tsx    # Sino de notificacoes (WebSocket)
│
├── lib/
│   ├── api/
│   │   ├── client.ts               # Axios instance com interceptors
│   │   ├── assets.ts               # API calls de ativos
│   │   ├── alerts.ts               # API calls de alertas
│   │   ├── cases.ts                # API calls de cases
│   │   ├── measurements.ts         # API calls de medicoes
│   │   ├── graph.ts                # API calls do grafo
│   │   └── analytics.ts            # API calls de analytics
│   ├── hooks/
│   │   ├── useAlertWebSocket.ts    # Hook para WebSocket de alertas
│   │   ├── useHealthScore.ts       # Hook para health score com polling
│   │   └── useTimeSeriesData.ts    # Hook para dados de series temporais
│   ├── stores/
│   │   ├── authStore.ts            # Zustand: auth state
│   │   ├── alertStore.ts           # Zustand: alertas ativos
│   │   └── filterStore.ts          # Zustand: filtros globais
│   └── utils/
│       ├── formatters.ts           # Formatacao de datas, numeros
│       ├── severity.ts             # Mapeamento severidade -> cor
│       └── constants.ts            # Constantes do app
│
└── types/
    ├── asset.ts                    # Tipos de ativos
    ├── alert.ts                    # Tipos de alertas
    ├── measurement.ts              # Tipos de medicoes
    └── graph.ts                    # Tipos do grafo
```

**State Management:**

```
┌─────────────────────────────────────────────────────────────┐
│                    STATE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  React Query (TanStack Query)                               │
│  ├── Server state: dados de API (assets, alerts, etc.)      │
│  ├── Cache automatico com stale-while-revalidate            │
│  ├── Refetch automatico em window focus                     │
│  └── Polling para dados criticos (health scores: 30s)       │
│                                                             │
│  Zustand (Client State)                                     │
│  ├── authStore: token, user, permissions                    │
│  ├── alertStore: alertas real-time via WebSocket             │
│  └── filterStore: filtros de data, tipo de ativo, severidade │
│                                                             │
│  WebSocket (Real-time)                                      │
│  └── Alertas: conexao persistente, reconexao automatica     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Componentes Principais - Exemplo TimeSeriesChart:**

```tsx
// src/frontend/components/charts/TimeSeriesChart.tsx

"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine,
         ResponsiveContainer, Area } from "recharts";
import { useMemo } from "react";
import type { Measurement, AnomalyPoint } from "@/types/measurement";

interface TimeSeriesChartProps {
  data: Measurement[];
  anomalies?: AnomalyPoint[];
  warningThreshold?: number;
  criticalThreshold?: number;
  unit: string;
  title: string;
}

export function TimeSeriesChart({
  data,
  anomalies = [],
  warningThreshold,
  criticalThreshold,
  unit,
  title,
}: TimeSeriesChartProps) {
  const chartData = useMemo(() =>
    data.map((m) => ({
      time: new Date(m.time).getTime(),
      value: m.value,
      isAnomaly: anomalies.some((a) => a.time === m.time),
    })),
    [data, anomalies]
  );

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="text-sm font-medium text-muted-foreground mb-2">
        {title} ({unit})
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <XAxis dataKey="time" type="number" scale="time" domain={["auto", "auto"]}
                 tickFormatter={(t) => new Date(t).toLocaleTimeString("pt-BR")} />
          <YAxis unit={` ${unit}`} />
          <Tooltip labelFormatter={(t) => new Date(t).toLocaleString("pt-BR")} />

          {warningThreshold && (
            <ReferenceLine y={warningThreshold} stroke="#f59e0b"
                          strokeDasharray="5 5" label="Warning" />
          )}
          {criticalThreshold && (
            <ReferenceLine y={criticalThreshold} stroke="#ef4444"
                          strokeDasharray="5 5" label="Critico" />
          )}

          <Line type="monotone" dataKey="value" stroke="#3b82f6"
                dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

**Interfaces:**

| Direcao | Protocolo | Destino |
|---------|-----------|---------|
| Saida | HTTPS | FastAPI REST endpoints |
| Saida | WSS | FastAPI WebSocket (alertas) |
| Entrada | HTTP | Usuarios (navegador) |

**Dependencias:** next, react, typescript, tailwindcss, @tanstack/react-query, zustand, recharts, reactflow, axios, date-fns, zod

---

## 3. Fluxos de Dados

### 3.1 Ingestao SCADA -> Alerta

```
┌──────────────────────────────────────────────────────────────────────────┐
│                 FLUXO: INGESTAO SCADA -> ALERTA                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. SCADA/Historian                                                      │
│     │                                                                    │
│     │  POST /api/v1/measurements/ingest                                  │
│     │  Body: { asset_id, points: [{ point_id, value, time, quality }] }  │
│     ▼                                                                    │
│  2. FastAPI Gateway                                                      │
│     ├── Validacao Pydantic (schema, tipos, ranges)                       │
│     ├── Autenticacao JWT (service account)                               │
│     └── Enfileira task Celery                                            │
│     │                                                                    │
│     │  ingestion.process_batch.delay(payload)                            │
│     ▼                                                                    │
│  3. Celery Worker (ingestion_queue)                                      │
│     ├── a) Valida qualidade dos dados (quality flags)                    │
│     ├── b) Enriquece com metadata (unit, ranges do measurement_point)    │
│     ├── c) Escreve batch no TimescaleDB (COPY para performance)          │
│     └── d) Atualiza cache Redis (measurement:latest:{point_id})          │
│     │                                                                    │
│     │  Emite evento: measurement.ingested                                │
│     ▼                                                                    │
│  4. Celery Worker (analytics_queue)                                      │
│     ├── a) Busca ultimas N medicoes do ativo (janela deslizante)         │
│     ├── b) Executa AnomalyDetector.detect()                              │
│     ├── c) Se anomalia detectada:                                        │
│     │      ├── Cria registro em alerts (TimescaleDB)                     │
│     │      ├── Atualiza cache Redis (alerts:active:{asset_id})           │
│     │      └── Publica no Redis Pub/Sub (alerts:new)                     │
│     └── d) Log de auditoria                                              │
│     │                                                                    │
│     │  Redis Pub/Sub: "alerts:new"                                       │
│     ▼                                                                    │
│  5. WebSocket Manager                                                    │
│     ├── Recebe mensagem do Pub/Sub                                       │
│     ├── Filtra por permissoes do usuario                                 │
│     └── Envia para clientes WebSocket conectados                         │
│     │                                                                    │
│     ▼                                                                    │
│  6. Frontend (Next.js)                                                   │
│     ├── AlertBanner: notificacao visual (toast)                          │
│     ├── AlertTable: nova linha na tabela                                 │
│     └── NotificationBell: incrementa contador                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

Latencia alvo: < 30 segundos end-to-end (ingestao ate alerta no frontend)
```

### 3.2 Calculo de Health Score

```
┌──────────────────────────────────────────────────────────────────────────┐
│                 FLUXO: CALCULO DE HEALTH SCORE                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Celery Beat (a cada 5 minutos)                                       │
│     │                                                                    │
│     │  analytics.recalculate_health_scores.delay()                       │
│     ▼                                                                    │
│  2. Celery Worker (analytics_queue)                                      │
│     │                                                                    │
│     │  Para cada ativo ativo:                                            │
│     ▼                                                                    │
│  3. Coleta de Dados                                                      │
│     ├── a) Busca ultimas medicoes por signal_type (Redis cache ou DB)    │
│     ├── b) Busca estatisticas historicas (measurements_hourly, 7 dias)   │
│     └── c) Busca anomaly scores recentes                                 │
│     │                                                                    │
│     ▼                                                                    │
│  4. HealthScoreCalculator.calculate()                                    │
│     ├── a) Calcula score por componente (signal_type)                    │
│     ├── b) Aplica pesos configuraveis por tipo de ativo                  │
│     ├── c) Aplica penalidades (anomalias + tendencia de degradacao)      │
│     └── d) Gera score final ponderado (0-100)                            │
│     │                                                                    │
│     ▼                                                                    │
│  5. Persistencia                                                         │
│     ├── a) INSERT em health_scores (TimescaleDB hypertable)              │
│     ├── b) UPDATE no no Asset do Neo4j (propriedade health_score)        │
│     ├── c) SET no Redis (health:{asset_id}, TTL 5 min)                   │
│     └── d) Se score cruzou threshold de severidade:                      │
│            └── Gera alerta tipo "trend" ou "threshold"                   │
│     │                                                                    │
│     ▼                                                                    │
│  6. Frontend (polling React Query, 30s)                                  │
│     ├── HealthGauge: atualiza indicador visual                           │
│     ├── AssetTable: atualiza coluna de health                            │
│     └── Dashboard: atualiza KPIs consolidados                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

Duracao alvo: < 2 minutos para processar todos os ativos ativos
```

### 3.3 Criacao de Case a Partir de Alerta

```
┌──────────────────────────────────────────────────────────────────────────┐
│                 FLUXO: ALERTA -> CASE                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Operador visualiza alerta na AlertTable                              │
│     │                                                                    │
│     │  Clica em "Criar Case" no AlertDetail                              │
│     ▼                                                                    │
│  2. Frontend envia request                                               │
│     │                                                                    │
│     │  POST /api/v1/alerts/{alert_id}/case                               │
│     │  Body: { title, description, priority, assigned_to }               │
│     ▼                                                                    │
│  3. FastAPI                                                              │
│     ├── a) Valida que alerta existe e esta aberto                        │
│     ├── b) Enriquece com contexto automatico:                            │
│     │      ├── Health score atual do ativo                               │
│     │      ├── Alertas relacionados (mesmo ativo, ultimas 24h)           │
│     │      ├── Analise de impacto do Neo4j (ativos dependentes)          │
│     │      └── Historico de cases anteriores do ativo                    │
│     ├── c) Cria registro na tabela cases (TimescaleDB)                   │
│     ├── d) Atualiza status do alerta para "acknowledged"                 │
│     └── e) Registra no audit log                                         │
│     │                                                                    │
│     ▼                                                                    │
│  4. Celery Worker (alert_queue)                                          │
│     ├── a) Sugere SOP baseado no tipo de alerta + tipo de ativo          │
│     ├── b) Envia notificacao para assigned_to                            │
│     └── c) Se prioridade = "critical":                                   │
│            └── Notifica gestores (escalation)                            │
│     │                                                                    │
│     ▼                                                                    │
│  5. Frontend                                                             │
│     ├── Redireciona para CaseDetail                                      │
│     ├── Mostra timeline com contexto enriquecido                         │
│     ├── Exibe SOP sugerido                                               │
│     └── Permite adicionar comentarios e atualizar status                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Seguranca

### 4.1 Autenticacao e Autorizacao

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODELO DE SEGURANCA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AUTENTICACAO: JWT (JSON Web Tokens)                            │
│  ├── Access Token: 30 min TTL, assinado com HS256               │
│  ├── Refresh Token: 7 dias TTL, armazenado em httpOnly cookie   │
│  ├── Token payload: { sub, role, agent_id, permissions, exp }   │
│  └── Blacklist de tokens revogados (Redis, TTL = exp do token)  │
│                                                                 │
│  AUTORIZACAO: RBAC (Role-Based Access Control)                  │
│                                                                 │
│  Roles:                                                         │
│  ┌──────────────┬──────────────────────────────────────┐        │
│  │ Role         │ Permissoes                           │        │
│  ├──────────────┼──────────────────────────────────────┤        │
│  │ admin        │ Full access (CRUD all resources)     │        │
│  │ manager      │ Read all + manage cases + ack alerts │        │
│  │ operator     │ Read own agent + ack alerts          │        │
│  │ viewer       │ Read-only own agent                  │        │
│  │ service      │ Ingest data (machine-to-machine)     │        │
│  └──────────────┴──────────────────────────────────────┘        │
│                                                                 │
│  Isolamento multi-tenant por agent_id:                          │
│  - Queries filtradas automaticamente pelo agent_id do JWT       │
│  - admin pode ver todos os agentes                              │
│  - operator/viewer veem apenas ativos do seu agente             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Audit Log

```python
# src/backend/core/audit.py

class AuditLogMiddleware:
    """
    Registra todas as acoes de escrita (POST, PUT, DELETE) no audit log.
    """

    async def __call__(self, request, call_next):
        response = await call_next(request)

        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            await self.log_action(
                user_id=request.state.user_id,
                action=f"{request.method} {request.url.path}",
                resource_type=self._extract_resource(request.url.path),
                resource_id=self._extract_id(request.url.path),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                status_code=response.status_code,
                timestamp=datetime.utcnow(),
            )

        return response

# Schema da tabela audit_logs
# CREATE TABLE audit_logs (
#     id          UUID DEFAULT gen_random_uuid(),
#     time        TIMESTAMPTZ NOT NULL,
#     user_id     UUID NOT NULL,
#     action      VARCHAR(100) NOT NULL,
#     resource    VARCHAR(50),
#     resource_id UUID,
#     ip_address  INET,
#     user_agent  TEXT,
#     status_code SMALLINT,
#     details     JSONB DEFAULT '{}'
# );
# SELECT create_hypertable('audit_logs', by_range('time'));
```

### 4.3 Seguranca em Camadas

| Camada | Mecanismo | Detalhes |
|--------|-----------|----------|
| Transito | TLS 1.3 | HTTPS para API, WSS para WebSocket |
| Repouso | AES-256 | Encryption at rest (TimescaleDB, backups) |
| API | Rate Limiting | 60 req/min por usuario, 1000 req/min por service account |
| API | Input Validation | Pydantic v2 strict mode em todos os endpoints |
| API | CORS | Whitelist de origens permitidas |
| DB | Connection Pool | Pool com limite de conexoes + SSL |
| DB | Least Privilege | Usuarios de DB separados (read-only, read-write, admin) |
| Infra | Network Isolation | Databases acessiveis apenas via rede interna |
| Logs | Audit Trail | Todas as acoes de escrita registradas com timestamp e IP |

---

## 5. Decisoes Arquiteturais (ADRs)

### ADR-001: TimescaleDB vs InfluxDB

| Criterio | TimescaleDB | InfluxDB |
|----------|-------------|----------|
| **SQL Compatibilidade** | Full SQL (e PostgreSQL) | InfluxQL / Flux |
| **Ecossistema** | Todo ecossistema PostgreSQL (extensions, tooling) | Ecossistema proprio |
| **Continuous Aggregates** | Nativo, materialized views | Tasks customizadas |
| **Joins com dados dimensionais** | SQL JOINs nativos | Requer service externo |
| **Compressao** | Nativa, ate 90%+ | Nativa |
| **Aprendizado** | Time que ja conhece PostgreSQL | Curva de aprendizado nova |
| **Retention Policies** | Nativo | Nativo |
| **Hosting** | Self-hosted ou Timescale Cloud | Self-hosted ou InfluxDB Cloud |

**Decisao:** TimescaleDB

**Justificativa:** O time ja tem experiencia com PostgreSQL. TimescaleDB permite usar SQL padrao para queries complexas, JOINs com tabelas dimensionais (assets, substations) sem ETL adicional, e todo o ecossistema PostgreSQL (Alembic, SQLAlchemy, pg_stat). As continuous aggregates substituem a necessidade de um pipeline separado para Data Products (bronze -> silver).

---

### ADR-002: Neo4j vs PostgreSQL com Extensao de Grafo

| Criterio | Neo4j | PostgreSQL + Apache AGE |
|----------|-------|------------------------|
| **Query de traversal** | Cypher nativo, otimizado | SQL + openCypher, menos otimizado |
| **Performance grafo** | Index-free adjacency, O(1) | JOINs recursivos, O(n) |
| **Visualizacao** | Neo4j Browser, Bloom | Tooling limitado |
| **Complexidade ops** | Mais um banco para operar | Reusa PostgreSQL existente |
| **Analise de impacto** | Path finding nativo | CTEs recursivas, complexas |
| **Comunidade** | Matura para grafos | Extensao relativamente nova |

**Decisao:** Neo4j

**Justificativa:** O caso de uso central do Energy Graph (analise de impacto, dependencia entre ativos, topologia eletrica) requer queries de traversal profundo que sao ordens de magnitude mais rapidas em um banco de grafos nativo. A complexidade operacional adicional e justificada pelo valor da feature de analise de impacto, que e diferencial competitivo.

---

### ADR-003: FastAPI vs Django

| Criterio | FastAPI | Django + DRF |
|----------|---------|-------------|
| **Performance** | Async nativo, alta performance | Sync por padrao, WSGI |
| **Type Safety** | Pydantic v2, validacao automatica | Serializers, mais verboso |
| **API Docs** | OpenAPI automatico (Swagger/ReDoc) | drf-spectacular (adicional) |
| **WebSocket** | Nativo | Django Channels (adicional) |
| **Maturidade** | Mais recente, comunidade crescente | Muito maduro, ecossistema amplo |
| **Admin panel** | Nao incluso | Django Admin (poderoso) |
| **ORM** | SQLAlchemy (escolha) | Django ORM (incluso) |

**Decisao:** FastAPI

**Justificativa:** O MVP requer alta performance em ingestao de dados (batch de medicoes SCADA), WebSocket nativo para alertas em tempo real, e validacao rigorosa de payload com type hints. FastAPI oferece tudo isso nativamente com menos boilerplate. A ausencia de admin panel nao e relevante pois o frontend Next.js sera a interface principal.

---

### ADR-004: Monolito Modular vs Microservicos

| Criterio | Monolito Modular | Microservicos |
|----------|------------------|---------------|
| **Complexidade ops** | Baixa (1 deploy) | Alta (N deploys, service mesh) |
| **Velocidade dev** | Alta (sem overhead de rede) | Media (contratos, versionamento) |
| **Debugging** | Simples (stack trace unico) | Complexo (tracing distribuido) |
| **Escalabilidade** | Vertical + Celery workers | Horizontal independente |
| **Time necessario** | 1-3 devs | 3+ devs por servico |
| **Refactoring** | Modulos -> servicos quando necessario | Dificulta mudancas transversais |

**Decisao:** Monolito Modular

**Justificativa:** Para o MVP com time pequeno (1-3 desenvolvedores), monolito modular oferece velocidade de desenvolvimento muito superior. A separacao em modulos internos (api, services, graph, ingestion, analytics, workflows) permite futura extracao para microservicos quando necessario. Celery workers ja oferecem escalabilidade horizontal para tasks pesadas (ingestao, ML).

**Estrutura do monolito modular:**

```
src/backend/
├── main.py              # FastAPI app entrypoint
├── api/                 # Modulo: HTTP endpoints
│   ├── v1/
│   │   ├── assets.py
│   │   ├── alerts.py
│   │   ├── cases.py
│   │   ├── measurements.py
│   │   ├── graph.py
│   │   └── analytics.py
│   └── ws/
│       └── alerts.py    # WebSocket
├── core/                # Modulo: Infraestrutura
│   ├── config.py
│   ├── security.py
│   ├── database.py
│   ├── dependencies.py
│   ├── audit.py
│   └── celery_app.py
├── models/              # Modulo: Modelos de dados
│   ├── asset.py
│   ├── alert.py
│   ├── measurement.py
│   ├── case.py
│   └── user.py
├── services/            # Modulo: Logica de negocio
│   ├── asset_service.py
│   ├── alert_service.py
│   ├── case_service.py
│   └── measurement_service.py
├── graph/               # Modulo: Neo4j Energy Graph
│   ├── driver.py
│   ├── queries/
│   │   ├── topology.cypher
│   │   ├── impact.cypher
│   │   └── neighbors.cypher
│   └── graph_service.py
├── ingestion/           # Modulo: Pipeline de ingestao
│   ├── tasks.py
│   ├── validators.py
│   └── transformers.py
├── analytics/           # Modulo: Motor analitico + ML
│   ├── tasks.py
│   ├── anomaly_detection.py
│   ├── health_score.py
│   ├── forecasting.py
│   └── models/          # Modelos ML serializados
└── workflows/           # Modulo: Cases e automacoes
    ├── tasks.py
    ├── case_engine.py
    └── sop_templates.py
```

---

## 6. Escalabilidade e Performance

### 6.1 Targets de Performance do MVP

| Metrica | Target | Justificativa |
|---------|--------|---------------|
| Latencia API (P95) | < 200ms | Experiencia do operador |
| Latencia API (P99) | < 500ms | Queries complexas (grafo) |
| Ingestao SCADA | 10.000 pontos/segundo | ~100 ativos x 5 sinais x 1 amostra/3s |
| Health Score recalc | < 2 min (todos ativos) | Refresh a cada 5 min |
| Alerta end-to-end | < 30 segundos | SCADA -> notificacao no frontend |
| Dashboard load | < 2 segundos | First meaningful paint |
| WebSocket delivery | < 1 segundo | Apos publicacao no Redis |
| TimescaleDB query (24h, 1 ativo) | < 100ms | Queries mais comuns |
| TimescaleDB query (30d, 1 ativo) | < 500ms | Via continuous aggregates |
| Neo4j traversal (3 niveis) | < 50ms | Analise de impacto |

### 6.2 Dimensionamento do MVP

```
┌─────────────────────────────────────────────────────────────────┐
│                 DIMENSIONAMENTO MVP                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Ativos monitorados:     100-500                                │
│  Pontos de medicao:      500-2500 (5 sinais/ativo)              │
│  Frequencia SCADA:       1 leitura a cada 1-5 segundos          │
│  Volume diario:          ~50M-250M registros/dia                │
│  Volume mensal:          ~1.5B-7.5B registros/mes               │
│  Usuarios concorrentes:  10-50                                  │
│  Alertas/dia:            50-500                                 │
│  Cases ativos:           10-100                                 │
│                                                                 │
│  RECURSOS (Docker Compose - Desenvolvimento/MVP)                │
│  ┌──────────────────┬─────────┬───────────┐                     │
│  │ Servico          │ CPU     │ RAM       │                     │
│  ├──────────────────┼─────────┼───────────┤                     │
│  │ FastAPI (uvicorn) │ 2 cores │ 1 GB     │                     │
│  │ TimescaleDB      │ 4 cores │ 8 GB     │                     │
│  │ Neo4j            │ 2 cores │ 4 GB     │                     │
│  │ Redis            │ 1 core  │ 1 GB     │                     │
│  │ Celery Workers   │ 4 cores │ 4 GB     │                     │
│  │ Next.js          │ 1 core  │ 512 MB   │                     │
│  ├──────────────────┼─────────┼───────────┤                     │
│  │ TOTAL            │ 14 cores│ 18.5 GB  │                     │
│  └──────────────────┴─────────┴───────────┘                     │
│                                                                 │
│  STORAGE (estimativa 1 ano, 500 ativos)                         │
│  ├── TimescaleDB (bruto):       ~500 GB (com compressao: ~50GB) │
│  ├── TimescaleDB (aggregates):  ~5 GB                           │
│  ├── Neo4j:                     ~1 GB                           │
│  └── Redis:                     ~500 MB                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Estrategia de Scaling Pos-MVP

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ROADMAP DE ESCALABILIDADE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FASE 1 - MVP (atual)                                                   │
│  ├── Single instance de tudo                                            │
│  ├── Docker Compose                                                     │
│  ├── Celery workers para paralelismo                                    │
│  └── Target: 100-500 ativos, 10-50 usuarios                            │
│                                                                         │
│  FASE 2 - Escala Media (500-5000 ativos)                                │
│  ├── Kubernetes (K8s) para orquestracao                                 │
│  ├── TimescaleDB: replicas de leitura + compressao agressiva            │
│  ├── Neo4j: causal cluster (1 leader + 2 followers)                     │
│  ├── Redis: Sentinel para HA                                            │
│  ├── FastAPI: 3+ replicas com load balancer                             │
│  ├── Celery: auto-scaling de workers por tipo de fila                   │
│  └── CDN para frontend (Vercel ou CloudFront)                           │
│                                                                         │
│  FASE 3 - Escala Alta (5000+ ativos, multi-tenant)                      │
│  ├── TimescaleDB multi-node (distributed hypertables)                   │
│  ├── Sharding por agent_id                                              │
│  ├── Kafka para ingestao (substituir Redis como broker)                 │
│  ├── Extrair modulos criticos como microservicos:                       │
│  │   ├── Ingestion Service (alta throughput)                            │
│  │   ├── Analytics Service (GPU para ML)                                │
│  │   └── Notification Service (multi-canal)                             │
│  ├── Data Lake (S3/MinIO) para dados historicos cold storage            │
│  └── Observabilidade: OpenTelemetry + Grafana + Prometheus              │
│                                                                         │
│  EVOLUCAO DA ARQUITETURA:                                               │
│                                                                         │
│  MVP            Fase 2              Fase 3                              │
│  ┌──────┐      ┌──────────┐        ┌─────────────────┐                 │
│  │Monoli│ ---> │ Monolito │ --->   │  Microservicos  │                 │
│  │  to  │      │ + K8s +  │        │  + Kafka +      │                 │
│  │Modular│     │ Replicas │        │  Data Lake      │                 │
│  └──────┘      └──────────┘        └─────────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Estrategias de Otimizacao Implementadas no MVP

| Estrategia | Componente | Impacto |
|------------|-----------|---------|
| Hypertables + chunk_time_interval 1 day | TimescaleDB | Queries por range de tempo ate 100x mais rapidas |
| Continuous aggregates (hourly/daily) | TimescaleDB | Dashboards usam dados pre-agregados |
| Compressao de chunks antigos (>7 dias) | TimescaleDB | Reducao de 90%+ no storage |
| Cache de health scores (TTL 5 min) | Redis | Elimina recalculo a cada request |
| Cache de topologia do grafo (TTL 10 min) | Redis | Evita queries repetidas ao Neo4j |
| Batch insert com COPY | TimescaleDB | Ingestao 10x mais rapida que INSERT individual |
| Index-free adjacency | Neo4j | Traversal O(1) por relacao |
| Connection pooling (asyncpg) | FastAPI <-> DB | Reutiliza conexoes, menor latencia |
| React Query stale-while-revalidate | Frontend | UX instantanea com dados em cache |
| WebSocket (nao polling) | Alertas | Latencia minima + menos carga no server |

---

## Apendice A: Docker Compose (Desenvolvimento)

```yaml
# docker-compose.yml
version: "3.9"

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ontogrid
      POSTGRES_USER: ontogrid
      POSTGRES_PASSWORD: ${TIMESCALE_PASSWORD}
    volumes:
      - timescale_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ontogrid"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build:
      context: ./src/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - TIMESCALE_URL=postgresql+asyncpg://ontogrid:${TIMESCALE_PASSWORD}@timescaledb:5432/ontogrid
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      timescaledb:
        condition: service_healthy
      neo4j:
        condition: service_started
      redis:
        condition: service_started
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  celery-worker:
    build:
      context: ./src/backend
      dockerfile: Dockerfile
    environment:
      - TIMESCALE_URL=postgresql+asyncpg://ontogrid:${TIMESCALE_PASSWORD}@timescaledb:5432/ontogrid
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - redis
      - timescaledb
    command: celery -A core.celery_app worker -l info -Q ingestion_queue,alert_queue,analytics_queue

  celery-beat:
    build:
      context: ./src/backend
      dockerfile: Dockerfile
    depends_on:
      - redis
    command: celery -A core.celery_app beat -l info

  frontend:
    build:
      context: ./src/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    command: npm run dev

volumes:
  timescale_data:
  neo4j_data:
  redis_data:
```

---

## Apendice B: Mapa de Portas

| Servico | Porta | Protocolo |
|---------|-------|-----------|
| FastAPI | 8000 | HTTP |
| Next.js | 3000 | HTTP |
| TimescaleDB | 5432 | TCP (PostgreSQL) |
| Neo4j Browser | 7474 | HTTP |
| Neo4j Bolt | 7687 | TCP |
| Redis | 6379 | TCP |
