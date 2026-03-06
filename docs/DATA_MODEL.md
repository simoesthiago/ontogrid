# Modelo de Dados - OntoGrid MVP

> **Versao**: 0.1.0
> **MVP**: Asset Health (Equipment Surveillance & Smart Alerting)
> **Databases**: TimescaleDB (series temporais + relacional) | Neo4j (Energy Graph)

---

## 1. Energy Graph v0.1 (Neo4j)

O Energy Graph e a ontologia do setor eletrico brasileiro implementada em Neo4j.
Unifica entidades de multiplas fontes (ONS, CCEE, ANEEL, SCADA, ERP) em um grafo
semantico que permite navegacao contextual, propagacao de impacto e resolucao de
identidade.

### 1.1 Modelo de Nos (Nodes)

#### Asset

Equipamento critico monitorado pelo sistema (transformador, gerador, disjuntor, reator).

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| external_ids      | Map        | Nao      | -                      | `{ons_id, ccee_id, aneel_id}` - IDs de orgaos      |
| name              | String     | Sim      | -                      | Nome descritivo do ativo                           |
| type              | String     | Sim      | ENUM                   | `transformer`, `generator`, `circuit_breaker`, `reactor` |
| subtype           | String     | Nao      | -                      | Subtipo especifico (ex: `autotransformer`, `hydro_generator`) |
| manufacturer      | String     | Nao      | -                      | Fabricante do equipamento                          |
| model             | String     | Nao      | -                      | Modelo do fabricante                               |
| year_installed    | Integer    | Nao      | >= 1950                | Ano de instalacao                                  |
| voltage_kv        | Float      | Sim      | > 0                    | Tensao nominal em kV                               |
| power_mva         | Float      | Nao      | > 0                    | Potencia nominal em MVA                            |
| status            | String     | Sim      | ENUM                   | `operational`, `maintenance`, `decommissioned`     |
| health_score      | Float      | Nao      | 0.0 - 100.0           | Score de saude calculado (atualizado periodicamente)|
| criticality       | String     | Sim      | ENUM                   | `A` (critico), `B` (importante), `C` (secundario) |
| lat               | Float      | Nao      | -33.75 a 5.27          | Latitude (limites Brasil)                          |
| lng               | Float      | Nao      | -73.99 a -34.79        | Longitude (limites Brasil)                         |
| metadata          | Map        | Nao      | -                      | Dados adicionais livres (peso, tipo_oleo, etc.)    |
| created_at        | DateTime   | Sim      | -                      | Data de criacao no sistema                         |
| updated_at        | DateTime   | Sim      | -                      | Data da ultima atualizacao                         |

**Indexes**: `id` (UNIQUE), `external_ids.ons_id`, `external_ids.ccee_id`, `external_ids.aneel_id`, `type`, `status`, `criticality`

```cypher
CREATE CONSTRAINT asset_id_unique IF NOT EXISTS
FOR (a:Asset) REQUIRE a.id IS UNIQUE;

CREATE INDEX asset_type_idx IF NOT EXISTS
FOR (a:Asset) ON (a.type);

CREATE INDEX asset_status_idx IF NOT EXISTS
FOR (a:Asset) ON (a.status);

CREATE INDEX asset_criticality_idx IF NOT EXISTS
FOR (a:Asset) ON (a.criticality);

CREATE INDEX asset_ons_id_idx IF NOT EXISTS
FOR (a:Asset) ON (a.`external_ids.ons_id`);
```

---

#### Substation

Subestacao eletrica que contem ativos e conecta linhas de transmissao.

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| name              | String     | Sim      | -                      | Nome da subestacao (ex: SE Adrianopolis 500kV)     |
| voltage_levels    | List[Float]| Sim      | -                      | Niveis de tensao presentes [500, 230, 138]         |
| type              | String     | Sim      | ENUM                   | `transmission`, `distribution`, `mixed`            |
| operator_id       | UUID       | Sim      | -                      | ID do agente operador                              |
| region            | String     | Sim      | ENUM                   | `N`, `NE`, `SE`, `S`, `CO` (subsistemas ONS)      |
| state             | String     | Sim      | -                      | UF (SP, RJ, MG, etc.)                             |
| lat               | Float      | Sim      | -                      | Latitude                                           |
| lng               | Float      | Sim      | -                      | Longitude                                          |
| metadata          | Map        | Nao      | -                      | Dados adicionais                                   |
| created_at        | DateTime   | Sim      | -                      | Data de criacao                                    |
| updated_at        | DateTime   | Sim      | -                      | Data da ultima atualizacao                         |

**Indexes**: `id` (UNIQUE), `name`, `region`, `state`, `type`

```cypher
CREATE CONSTRAINT substation_id_unique IF NOT EXISTS
FOR (s:Substation) REQUIRE s.id IS UNIQUE;

CREATE INDEX substation_region_idx IF NOT EXISTS
FOR (s:Substation) ON (s.region);
```

---

#### TransmissionLine

Linha de transmissao conectando subestacoes.

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| name              | String     | Sim      | -                      | Nome da LT (ex: LT 500kV Adrianopolis-Ibiuna C1)  |
| voltage_kv        | Float      | Sim      | > 0                    | Tensao nominal em kV                               |
| length_km         | Float      | Sim      | > 0                    | Extensao em km                                     |
| circuits          | Integer    | Sim      | >= 1                   | Numero de circuitos                                |
| conductor_type    | String     | Nao      | -                      | Tipo de condutor                                   |
| capacity_mw       | Float      | Nao      | > 0                    | Capacidade nominal em MW                           |
| status            | String     | Sim      | ENUM                   | `operational`, `maintenance`, `decommissioned`     |
| metadata          | Map        | Nao      | -                      | Dados adicionais                                   |
| created_at        | DateTime   | Sim      | -                      | Data de criacao                                    |
| updated_at        | DateTime   | Sim      | -                      | Data da ultima atualizacao                         |

**Indexes**: `id` (UNIQUE), `voltage_kv`, `status`

```cypher
CREATE CONSTRAINT tl_id_unique IF NOT EXISTS
FOR (t:TransmissionLine) REQUIRE t.id IS UNIQUE;
```

---

#### Agent

Agente do setor eletrico (geradora, transmissora, distribuidora, comercializadora).

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| name              | String     | Sim      | -                      | Razao social ou nome fantasia                      |
| type              | String     | Sim      | ENUM                   | `generator`, `transmitter`, `distributor`, `trader` |
| cnpj              | String     | Sim      | UNIQUE, 14 chars       | CNPJ do agente                                     |
| ons_code          | String     | Nao      | UNIQUE                 | Codigo ONS                                         |
| ccee_code         | String     | Nao      | UNIQUE                 | Codigo CCEE (perfil de agente)                     |
| aneel_code        | String     | Nao      | UNIQUE                 | Codigo ANEEL (outorga)                             |
| active            | Boolean    | Sim      | -                      | Se o agente esta ativo                             |
| metadata          | Map        | Nao      | -                      | Dados adicionais (grupo economico, etc.)           |
| created_at        | DateTime   | Sim      | -                      | Data de criacao                                    |
| updated_at        | DateTime   | Sim      | -                      | Data da ultima atualizacao                         |

**Indexes**: `id` (UNIQUE), `cnpj` (UNIQUE), `ons_code` (UNIQUE), `ccee_code` (UNIQUE), `type`

```cypher
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (ag:Agent) REQUIRE ag.id IS UNIQUE;

CREATE CONSTRAINT agent_cnpj_unique IF NOT EXISTS
FOR (ag:Agent) REQUIRE ag.cnpj IS UNIQUE;
```

---

#### MeasurementPoint

Ponto de medicao associado a um ativo. Representa um sensor ou canal de dados SCADA.

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| asset_id          | UUID       | Sim      | -                      | ID do ativo monitorado                             |
| parameter         | String     | Sim      | ENUM                   | `temperature`, `vibration`, `current`, `voltage`, `oil_level`, `dissolved_gas`, `pressure`, `humidity`, `tap_position` |
| unit              | String     | Sim      | -                      | Unidade de medida (C, mm/s, A, kV, %, ppm, etc.)  |
| sampling_rate     | String     | Sim      | -                      | Taxa de amostragem (ex: `1s`, `5s`, `1min`, `15min`) |
| source            | String     | Sim      | -                      | Fonte de dados (ex: `scada_ons`, `historian_pi`, `iot_sensor`) |
| tag_name          | String     | Nao      | -                      | Tag original no sistema de origem                  |
| active            | Boolean    | Sim      | -                      | Se o ponto de medicao esta ativo                   |
| metadata          | Map        | Nao      | -                      | Dados adicionais (faixa esperada, limites, etc.)   |
| created_at        | DateTime   | Sim      | -                      | Data de criacao                                    |

**Indexes**: `id` (UNIQUE), `asset_id`, `parameter`

```cypher
CREATE CONSTRAINT mp_id_unique IF NOT EXISTS
FOR (mp:MeasurementPoint) REQUIRE mp.id IS UNIQUE;

CREATE INDEX mp_parameter_idx IF NOT EXISTS
FOR (mp:MeasurementPoint) ON (mp.parameter);
```

---

#### Alert

Alerta gerado pelo sistema de deteccao de anomalias ou por regras de threshold.

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| asset_id          | UUID       | Sim      | -                      | ID do ativo que gerou o alerta                     |
| severity          | String     | Sim      | ENUM                   | `critical`, `high`, `medium`, `low`                |
| alert_type        | String     | Sim      | -                      | Tipo de alerta (ex: `temperature_anomaly`, `dissolved_gas_high`, `vibration_spike`) |
| title             | String     | Sim      | -                      | Titulo descritivo                                  |
| message           | String     | Sim      | -                      | Descricao detalhada do alerta                      |
| parameters        | Map        | Nao      | -                      | Parametros que dispararam o alerta (valores, thresholds) |
| triggered_at      | DateTime   | Sim      | -                      | Data/hora do disparo                               |
| acknowledged_at   | DateTime   | Nao      | -                      | Data/hora do reconhecimento                        |
| resolved_at       | DateTime   | Nao      | -                      | Data/hora da resolucao                             |
| status            | String     | Sim      | ENUM                   | `open`, `acknowledged`, `resolved`, `dismissed`    |
| created_at        | DateTime   | Sim      | -                      | Data de criacao                                    |

**Indexes**: `id` (UNIQUE), `asset_id`, `severity`, `status`, `triggered_at`

```cypher
CREATE CONSTRAINT alert_id_unique IF NOT EXISTS
FOR (al:Alert) REQUIRE al.id IS UNIQUE;

CREATE INDEX alert_severity_idx IF NOT EXISTS
FOR (al:Alert) ON (al.severity);

CREATE INDEX alert_status_idx IF NOT EXISTS
FOR (al:Alert) ON (al.status);
```

---

#### Case

Caso de investigacao/resolucao aberto a partir de um ou mais alertas.

| Property          | Type       | Required | Constraint             | Descricao                                          |
|-------------------|------------|----------|------------------------|----------------------------------------------------|
| id                | UUID       | Sim      | UNIQUE                 | Identificador interno OntoGrid                     |
| title             | String     | Sim      | -                      | Titulo do caso                                     |
| description       | String     | Nao      | -                      | Descricao detalhada                                |
| assignee          | UUID       | Nao      | -                      | ID do usuario responsavel                          |
| status            | String     | Sim      | ENUM                   | `open`, `in_progress`, `resolved`, `closed`        |
| priority          | String     | Sim      | ENUM                   | `critical`, `high`, `medium`, `low`                |
| sop_id            | UUID       | Nao      | -                      | ID do SOP vinculado                                |
| resolution_notes  | String     | Nao      | -                      | Notas de resolucao                                 |
| created_at        | DateTime   | Sim      | -                      | Data de criacao                                    |
| updated_at        | DateTime   | Sim      | -                      | Data da ultima atualizacao                         |
| closed_at         | DateTime   | Nao      | -                      | Data de fechamento                                 |

**Indexes**: `id` (UNIQUE), `status`, `priority`, `assignee`

```cypher
CREATE CONSTRAINT case_id_unique IF NOT EXISTS
FOR (c:Case) REQUIRE c.id IS UNIQUE;

CREATE INDEX case_status_idx IF NOT EXISTS
FOR (c:Case) ON (c.status);
```

---

### 1.2 Modelo de Relacoes (Relationships)

| Relacao            | Origem           | Destino          | Properties                      | Descricao                                       |
|--------------------|------------------|------------------|---------------------------------|-------------------------------------------------|
| `BELONGS_TO`       | Asset            | Substation       | `since: DateTime`               | Ativo pertence a subestacao                     |
| `CONNECTED_TO`     | Substation       | Substation       | `via: UUID (TransmissionLine.id), voltage_kv: Float` | Subestacoes conectadas por LT |
| `OPERATED_BY`      | Asset/Substation | Agent            | `since: DateTime, role: String` | Ativo/SE operado por agente                     |
| `MONITORED_BY`     | Asset            | MeasurementPoint | `since: DateTime`               | Ativo monitorado por ponto de medicao           |
| `DEPENDS_ON`       | Asset            | Asset            | `dependency_type: String, criticality: String` | Dependencia operacional entre ativos |
| `TRIGGERED`        | Alert            | Case             | `at: DateTime`                  | Alerta que originou um caso                     |
| `IMPACTS`          | Alert            | Asset            | `impact_level: String`          | Alerta que afeta um ativo                       |
| `FEEDS`            | TransmissionLine | Substation       | `direction: String`             | LT alimenta subestacao                          |
| `ORIGINATES`       | TransmissionLine | Substation       | `direction: String`             | LT se origina de subestacao                     |
| `RAISED_ON`        | Alert            | Asset            | -                               | Alerta levantado em um ativo                    |
| `ASSIGNED_SOP`     | Case             | SOP              | -                               | Caso vinculado a um SOP                         |

```
(:Asset)-[:BELONGS_TO {since}]->(:Substation)
(:Substation)-[:CONNECTED_TO {via, voltage_kv}]->(:Substation)
(:Asset)-[:OPERATED_BY {since, role}]->(:Agent)
(:Substation)-[:OPERATED_BY {since, role}]->(:Agent)
(:Asset)-[:MONITORED_BY {since}]->(:MeasurementPoint)
(:Asset)-[:DEPENDS_ON {dependency_type, criticality}]->(:Asset)
(:Alert)-[:TRIGGERED {at}]->(:Case)
(:Alert)-[:IMPACTS {impact_level}]->(:Asset)
(:Alert)-[:RAISED_ON]->(:Asset)
(:TransmissionLine)-[:FEEDS {direction}]->(:Substation)
(:TransmissionLine)-[:ORIGINATES {direction}]->(:Substation)
(:Case)-[:ASSIGNED_SOP]->(:SOP)
```

---

### 1.3 Queries Cypher Essenciais

#### Buscar todos os ativos de uma subestacao com health score

```cypher
MATCH (a:Asset)-[:BELONGS_TO]->(s:Substation {id: $substation_id})
RETURN a.id AS asset_id,
       a.name AS name,
       a.type AS type,
       a.health_score AS health_score,
       a.criticality AS criticality,
       a.status AS status
ORDER BY a.health_score ASC;
```

#### Propagacao de impacto: dado um ativo em falha, quais outros sao afetados

```cypher
// Nivel 1: ativos diretamente dependentes
MATCH (failed:Asset {id: $asset_id})
MATCH (affected:Asset)-[:DEPENDS_ON*1..3]->(failed)
RETURN affected.id AS affected_id,
       affected.name AS name,
       affected.type AS type,
       affected.health_score AS health_score,
       affected.criticality AS criticality,
       length((affected)-[:DEPENDS_ON*]->(failed)) AS distance
ORDER BY distance ASC, affected.criticality ASC;
```

#### Propagacao via topologia: subestacoes impactadas por falha em LT

```cypher
MATCH (s1:Substation)<-[:ORIGINATES]-(lt:TransmissionLine)-[:FEEDS]->(s2:Substation)
WHERE lt.id = $transmission_line_id
MATCH (a:Asset)-[:BELONGS_TO]->(s2)
RETURN s2.name AS substation,
       collect({id: a.id, name: a.name, type: a.type, criticality: a.criticality}) AS affected_assets;
```

#### Historico de alertas por ativo

```cypher
MATCH (al:Alert)-[:RAISED_ON]->(a:Asset {id: $asset_id})
RETURN al.id AS alert_id,
       al.severity AS severity,
       al.alert_type AS type,
       al.title AS title,
       al.status AS status,
       al.triggered_at AS triggered_at,
       al.resolved_at AS resolved_at
ORDER BY al.triggered_at DESC
LIMIT 50;
```

#### Ativos criticos com health score abaixo de threshold

```cypher
MATCH (a:Asset)
WHERE a.criticality = 'A'
  AND a.health_score < $threshold
  AND a.status = 'operational'
OPTIONAL MATCH (a)-[:BELONGS_TO]->(s:Substation)
OPTIONAL MATCH (a)-[:OPERATED_BY]->(ag:Agent)
RETURN a.id AS asset_id,
       a.name AS name,
       a.type AS type,
       a.health_score AS health_score,
       s.name AS substation,
       s.region AS region,
       ag.name AS operator
ORDER BY a.health_score ASC;
```

#### Visao completa de um ativo (contexto 360)

```cypher
MATCH (a:Asset {id: $asset_id})
OPTIONAL MATCH (a)-[:BELONGS_TO]->(s:Substation)
OPTIONAL MATCH (a)-[:OPERATED_BY]->(ag:Agent)
OPTIONAL MATCH (a)-[:MONITORED_BY]->(mp:MeasurementPoint)
OPTIONAL MATCH (a)<-[:DEPENDS_ON]-(dep:Asset)
OPTIONAL MATCH (al:Alert)-[:RAISED_ON]->(a) WHERE al.status = 'open'
RETURN a,
       s.name AS substation,
       ag.name AS operator,
       collect(DISTINCT mp) AS measurement_points,
       collect(DISTINCT dep) AS dependents,
       collect(DISTINCT al) AS open_alerts;
```

---

## 2. TimescaleDB Schema

TimescaleDB e a camada relacional e de series temporais. Armazena medicoes brutas,
agregadas, health scores, alertas, casos e todas as entidades de referencia.

### 2.1 Tabelas Principais

#### measurements (hypertable)

Tabela principal de series temporais. Particionada por tempo (chunk_interval = 1 dia).

```sql
CREATE TABLE measurements (
    time            TIMESTAMPTZ     NOT NULL,
    asset_id        UUID            NOT NULL,
    measurement_point_id UUID       NOT NULL,
    parameter       VARCHAR(50)     NOT NULL,
    value           DOUBLE PRECISION NOT NULL,
    quality_flag    SMALLINT        NOT NULL DEFAULT 0,
                    -- 0 = good, 1 = suspect, 2 = bad, 3 = substituted
    source          VARCHAR(50)     NOT NULL,
                    -- ex: scada_ons, historian_pi, iot_gateway
    ingested_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Converte para hypertable com chunk de 1 dia
SELECT create_hypertable('measurements', 'time',
    chunk_time_interval => INTERVAL '1 day');

-- Compressao apos 7 dias
ALTER TABLE measurements SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'asset_id, measurement_point_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('measurements', INTERVAL '7 days');
```

**Indexes**:
```sql
-- Index principal para queries por ativo + tempo
CREATE INDEX idx_measurements_asset_time
    ON measurements (asset_id, time DESC);

-- Index para queries por ponto de medicao + tempo
CREATE INDEX idx_measurements_mp_time
    ON measurements (measurement_point_id, time DESC);

-- Index para queries por parametro
CREATE INDEX idx_measurements_parameter
    ON measurements (parameter, time DESC);

-- Index para qualidade de dados
CREATE INDEX idx_measurements_quality
    ON measurements (quality_flag)
    WHERE quality_flag > 0;
```

---

#### health_scores (hypertable)

Scores de saude calculados periodicamente para cada ativo.

```sql
CREATE TABLE health_scores (
    time            TIMESTAMPTZ     NOT NULL,
    asset_id        UUID            NOT NULL,
    overall_score   DOUBLE PRECISION NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    component_scores JSONB          NOT NULL DEFAULT '{}',
                    -- ex: {"thermal": 85, "electrical": 92, "mechanical": 78, "oil": 90}
    anomaly_count   INTEGER         NOT NULL DEFAULT 0,
    trend           VARCHAR(20)     DEFAULT 'stable',
                    -- improving, stable, degrading
    model_version   VARCHAR(20)     NOT NULL,
                    -- ex: v1.0.0
    confidence      DOUBLE PRECISION CHECK (confidence >= 0 AND confidence <= 1),
    computed_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('health_scores', 'time',
    chunk_time_interval => INTERVAL '1 day');

ALTER TABLE health_scores SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'asset_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('health_scores', INTERVAL '30 days');
```

**Indexes**:
```sql
CREATE INDEX idx_health_scores_asset_time
    ON health_scores (asset_id, time DESC);

CREATE INDEX idx_health_scores_overall
    ON health_scores (overall_score, time DESC)
    WHERE overall_score < 70;  -- Partial index para ativos em risco
```

---

#### alerts

Alertas gerados pelo sistema de deteccao de anomalias e regras.

```sql
CREATE TABLE alerts (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID            NOT NULL REFERENCES assets(id),
    severity        VARCHAR(20)     NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    alert_type      VARCHAR(50)     NOT NULL,
                    -- ex: temperature_anomaly, dissolved_gas_high, vibration_spike,
                    --     oil_level_low, threshold_breach, pattern_detected
    title           VARCHAR(200)    NOT NULL,
    description     TEXT,
    parameters      JSONB           DEFAULT '{}',
                    -- ex: {"measured_value": 95.3, "threshold": 85.0, "parameter": "temperature"}
    context         JSONB           DEFAULT '{}',
                    -- ex: {"recent_trend": "increasing", "baseline_avg": 72.5}
    triggered_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID,
    resolved_at     TIMESTAMPTZ,
    resolved_by     UUID,
    status          VARCHAR(20)     NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'acknowledged', 'resolved', 'dismissed')),
    assigned_to     UUID,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE INDEX idx_alerts_asset_id ON alerts (asset_id);
CREATE INDEX idx_alerts_severity ON alerts (severity);
CREATE INDEX idx_alerts_status ON alerts (status);
CREATE INDEX idx_alerts_triggered_at ON alerts (triggered_at DESC);
CREATE INDEX idx_alerts_open ON alerts (asset_id, triggered_at DESC) WHERE status = 'open';
CREATE INDEX idx_alerts_type ON alerts (alert_type);
```

---

#### cases

Casos de investigacao/resolucao criados a partir de alertas.

```sql
CREATE TABLE cases (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id        UUID            REFERENCES alerts(id),
    title           VARCHAR(200)    NOT NULL,
    description     TEXT,
    status          VARCHAR(20)     NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    priority        VARCHAR(20)     NOT NULL
                    CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    assigned_to     UUID,
    sop_id          UUID            REFERENCES sops(id),
    resolution_notes TEXT,
    root_cause      VARCHAR(200),
    actions_taken   JSONB           DEFAULT '[]',
                    -- ex: [{"action": "inspecao_visual", "at": "2026-03-06T10:00:00Z", "by": "..."}]
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ
);
```

**Indexes**:
```sql
CREATE INDEX idx_cases_alert_id ON cases (alert_id);
CREATE INDEX idx_cases_status ON cases (status);
CREATE INDEX idx_cases_priority ON cases (priority);
CREATE INDEX idx_cases_assigned ON cases (assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX idx_cases_sop ON cases (sop_id) WHERE sop_id IS NOT NULL;
CREATE INDEX idx_cases_open ON cases (created_at DESC) WHERE status IN ('open', 'in_progress');
```

---

#### assets

Tabela de referencia de ativos (espelha o node Asset do Energy Graph).

```sql
CREATE TABLE assets (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    external_ids    JSONB           DEFAULT '{}',
                    -- ex: {"ons_id": "TRF-001", "ccee_id": "CCEE-5001", "aneel_id": "ANE-2001"}
    name            VARCHAR(200)    NOT NULL,
    asset_type      VARCHAR(50)     NOT NULL
                    CHECK (asset_type IN ('transformer', 'generator', 'circuit_breaker', 'reactor')),
    subtype         VARCHAR(50),
    substation_id   UUID            REFERENCES substations(id),
    manufacturer    VARCHAR(100),
    model           VARCHAR(100),
    year_installed  INTEGER         CHECK (year_installed >= 1950 AND year_installed <= 2100),
    voltage_kv      DOUBLE PRECISION NOT NULL CHECK (voltage_kv > 0),
    power_mva       DOUBLE PRECISION CHECK (power_mva > 0),
    status          VARCHAR(20)     NOT NULL DEFAULT 'operational'
                    CHECK (status IN ('operational', 'maintenance', 'decommissioned')),
    criticality     CHAR(1)         NOT NULL CHECK (criticality IN ('A', 'B', 'C')),
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    metadata        JSONB           DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE INDEX idx_assets_type ON assets (asset_type);
CREATE INDEX idx_assets_substation ON assets (substation_id);
CREATE INDEX idx_assets_status ON assets (status);
CREATE INDEX idx_assets_criticality ON assets (criticality);
CREATE INDEX idx_assets_ons_id ON assets USING gin ((external_ids->'ons_id'));
CREATE INDEX idx_assets_ccee_id ON assets USING gin ((external_ids->'ccee_id'));
CREATE INDEX idx_assets_aneel_id ON assets USING gin ((external_ids->'aneel_id'));
```

---

#### substations

```sql
CREATE TABLE substations (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200)    NOT NULL,
    voltage_levels  DOUBLE PRECISION[] NOT NULL,
                    -- ex: ARRAY[500.0, 230.0, 138.0]
    type            VARCHAR(20)     NOT NULL
                    CHECK (type IN ('transmission', 'distribution', 'mixed')),
    operator_id     UUID            REFERENCES agents(id),
    region          VARCHAR(5)      NOT NULL
                    CHECK (region IN ('N', 'NE', 'SE', 'S', 'CO')),
    state           CHAR(2)         NOT NULL,
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    metadata        JSONB           DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE INDEX idx_substations_region ON substations (region);
CREATE INDEX idx_substations_state ON substations (state);
CREATE INDEX idx_substations_operator ON substations (operator_id);
CREATE INDEX idx_substations_type ON substations (type);
```

---

#### agents

```sql
CREATE TABLE agents (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200)    NOT NULL,
    agent_type      VARCHAR(20)     NOT NULL
                    CHECK (agent_type IN ('generator', 'transmitter', 'distributor', 'trader')),
    cnpj            VARCHAR(14)     NOT NULL UNIQUE,
    ons_code        VARCHAR(50)     UNIQUE,
    ccee_code       VARCHAR(50)     UNIQUE,
    aneel_code      VARCHAR(50)     UNIQUE,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    metadata        JSONB           DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_agents_cnpj ON agents (cnpj);
CREATE INDEX idx_agents_type ON agents (agent_type);
CREATE INDEX idx_agents_ons ON agents (ons_code) WHERE ons_code IS NOT NULL;
CREATE INDEX idx_agents_ccee ON agents (ccee_code) WHERE ccee_code IS NOT NULL;
```

---

#### sops (Standard Operating Procedures)

```sql
CREATE TABLE sops (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(200)    NOT NULL,
    description     TEXT,
    asset_type      VARCHAR(50),
                    -- Aplica-se a qual tipo de ativo
    alert_type      VARCHAR(50),
                    -- Aplica-se a qual tipo de alerta
    severity_min    VARCHAR(20),
                    -- Severidade minima para acionar
    steps           JSONB           NOT NULL DEFAULT '[]',
                    -- ex: [{"order": 1, "action": "Verificar temperatura", "details": "..."},
                    --      {"order": 2, "action": "Inspecionar oleo", "details": "..."}]
    estimated_time  INTERVAL,
    requires_shutdown BOOLEAN       NOT NULL DEFAULT FALSE,
    version         INTEGER         NOT NULL DEFAULT 1,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_by      UUID,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE INDEX idx_sops_asset_type ON sops (asset_type);
CREATE INDEX idx_sops_alert_type ON sops (alert_type);
CREATE INDEX idx_sops_active ON sops (active) WHERE active = TRUE;
```

---

#### audit_log

```sql
CREATE TABLE audit_log (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         UUID,
    action          VARCHAR(50)     NOT NULL,
                    -- ex: create, update, delete, acknowledge, resolve, login, export
    entity_type     VARCHAR(50)     NOT NULL,
                    -- ex: asset, alert, case, sop, measurement
    entity_id       UUID,
    changes         JSONB           DEFAULT '{}',
                    -- ex: {"field": "status", "old": "open", "new": "resolved"}
    ip_address      INET,
    user_agent      VARCHAR(500),
    context         JSONB           DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Particionar por tempo para performance
SELECT create_hypertable('audit_log', 'created_at',
    chunk_time_interval => INTERVAL '1 month',
    migrate_data => TRUE);
```

**Indexes**:
```sql
CREATE INDEX idx_audit_user ON audit_log (user_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_log (entity_type, entity_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_log (action, created_at DESC);
```

---

#### measurement_points

```sql
CREATE TABLE measurement_points (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID            NOT NULL REFERENCES assets(id),
    parameter       VARCHAR(50)     NOT NULL
                    CHECK (parameter IN (
                        'temperature', 'vibration', 'current', 'voltage',
                        'oil_level', 'dissolved_gas', 'pressure', 'humidity',
                        'tap_position', 'power_factor', 'frequency'
                    )),
    unit            VARCHAR(20)     NOT NULL,
    sampling_rate   VARCHAR(20)     NOT NULL,
    source          VARCHAR(50)     NOT NULL,
    tag_name        VARCHAR(200),
    min_expected    DOUBLE PRECISION,
    max_expected    DOUBLE PRECISION,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    metadata        JSONB           DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE INDEX idx_mp_asset ON measurement_points (asset_id);
CREATE INDEX idx_mp_parameter ON measurement_points (parameter);
CREATE INDEX idx_mp_active ON measurement_points (active) WHERE active = TRUE;
```

---

### 2.2 Continuous Aggregates

#### measurements_hourly

```sql
CREATE MATERIALIZED VIEW measurements_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time)     AS bucket,
    asset_id,
    measurement_point_id,
    parameter,
    AVG(value)                      AS avg_value,
    MIN(value)                      AS min_value,
    MAX(value)                      AS max_value,
    STDDEV(value)                   AS stddev_value,
    COUNT(*)                        AS sample_count,
    COUNT(*) FILTER (WHERE quality_flag = 0) AS good_count,
    COUNT(*) FILTER (WHERE quality_flag > 0) AS bad_count
FROM measurements
GROUP BY bucket, asset_id, measurement_point_id, parameter;

-- Refresh automatico a cada hora, com lag de 30 minutos
SELECT add_continuous_aggregate_policy('measurements_hourly',
    start_offset    => INTERVAL '3 hours',
    end_offset      => INTERVAL '30 minutes',
    schedule_interval => INTERVAL '1 hour');
```

#### measurements_daily

```sql
CREATE MATERIALIZED VIEW measurements_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', bucket)    AS bucket,
    asset_id,
    measurement_point_id,
    parameter,
    AVG(avg_value)                  AS avg_value,
    MIN(min_value)                  AS min_value,
    MAX(max_value)                  AS max_value,
    AVG(stddev_value)               AS avg_stddev,
    SUM(sample_count)               AS sample_count,
    SUM(good_count)                 AS good_count,
    SUM(bad_count)                  AS bad_count
FROM measurements_hourly
GROUP BY bucket, asset_id, measurement_point_id, parameter;

SELECT add_continuous_aggregate_policy('measurements_daily',
    start_offset    => INTERVAL '3 days',
    end_offset      => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

#### health_scores_daily

```sql
CREATE MATERIALIZED VIEW health_scores_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time)      AS bucket,
    asset_id,
    AVG(overall_score)              AS avg_score,
    MIN(overall_score)              AS min_score,
    MAX(overall_score)              AS max_score,
    SUM(anomaly_count)              AS total_anomalies,
    last(overall_score, time)       AS last_score,
    last(trend, time)               AS last_trend
FROM health_scores
GROUP BY bucket, asset_id;

SELECT add_continuous_aggregate_policy('health_scores_daily',
    start_offset    => INTERVAL '3 days',
    end_offset      => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

---

### 2.3 Retention Policies

```sql
-- Medicoes brutas: 90 dias
SELECT add_retention_policy('measurements', INTERVAL '90 days');

-- Medicoes horárias: 2 anos
SELECT add_retention_policy('measurements_hourly', INTERVAL '2 years');

-- Medicoes diarias: 10 anos
SELECT add_retention_policy('measurements_daily', INTERVAL '10 years');

-- Health scores brutos: 5 anos
SELECT add_retention_policy('health_scores', INTERVAL '5 years');

-- Health scores diarios: 10 anos
SELECT add_retention_policy('health_scores_daily', INTERVAL '10 years');

-- Audit log: 7 anos (compliance regulatorio ANEEL)
SELECT add_retention_policy('audit_log', INTERVAL '7 years');
```

---

### 2.4 Indexes Adicionais de Performance

```sql
-- Index composto para dashboard principal (ativos operacionais por subestacao)
CREATE INDEX idx_assets_dashboard
    ON assets (substation_id, criticality, status)
    WHERE status = 'operational';

-- Index para busca full-text em alertas
CREATE INDEX idx_alerts_search
    ON alerts USING gin (to_tsvector('portuguese', title || ' ' || COALESCE(description, '')));

-- Index para busca full-text em cases
CREATE INDEX idx_cases_search
    ON cases USING gin (to_tsvector('portuguese', title || ' ' || COALESCE(description, '')));

-- Index GIN para queries JSONB em external_ids
CREATE INDEX idx_assets_external_ids
    ON assets USING gin (external_ids jsonb_path_ops);

-- Index GIN para queries JSONB em metadata
CREATE INDEX idx_assets_metadata
    ON assets USING gin (metadata jsonb_path_ops);

-- Index para alertas recentes por severidade (top-N query no dashboard)
CREATE INDEX idx_alerts_recent_severity
    ON alerts (severity, triggered_at DESC)
    WHERE status IN ('open', 'acknowledged');
```

---

## 3. Pydantic Schemas (API)

### 3.1 Asset Schemas

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class AssetType(str, Enum):
    TRANSFORMER = "transformer"
    GENERATOR = "generator"
    CIRCUIT_BREAKER = "circuit_breaker"
    REACTOR = "reactor"


class AssetStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class Criticality(str, Enum):
    A = "A"  # Critico
    B = "B"  # Importante
    C = "C"  # Secundario


class ExternalIds(BaseModel):
    ons_id: Optional[str] = None
    ccee_id: Optional[str] = None
    aneel_id: Optional[str] = None


# --- Request Schemas ---

class AssetCreate(BaseModel):
    name: str = Field(..., max_length=200, examples=["Transformador TR1 500/230kV"])
    asset_type: AssetType
    subtype: Optional[str] = Field(None, max_length=50)
    external_ids: Optional[ExternalIds] = None
    substation_id: Optional[UUID] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year_installed: Optional[int] = Field(None, ge=1950, le=2100)
    voltage_kv: float = Field(..., gt=0, examples=[500.0])
    power_mva: Optional[float] = Field(None, gt=0, examples=[600.0])
    status: AssetStatus = AssetStatus.OPERATIONAL
    criticality: Criticality = Field(..., examples=["A"])
    latitude: Optional[float] = Field(None, ge=-33.75, le=5.27)
    longitude: Optional[float] = Field(None, ge=-73.99, le=-34.79)
    metadata: Optional[dict] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    status: Optional[AssetStatus] = None
    criticality: Optional[Criticality] = None
    health_score: Optional[float] = Field(None, ge=0, le=100)
    metadata: Optional[dict] = None


# --- Response Schemas ---

class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    asset_type: AssetType
    subtype: Optional[str] = None
    external_ids: Optional[ExternalIds] = None
    substation_id: Optional[UUID] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_installed: Optional[int] = None
    voltage_kv: float
    power_mva: Optional[float] = None
    status: AssetStatus
    criticality: Criticality
    health_score: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int
```

**Exemplo JSON - AssetResponse**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Transformador TR1 500/230kV",
  "asset_type": "transformer",
  "subtype": "autotransformer",
  "external_ids": {
    "ons_id": "TRF-SE-ADR-001",
    "ccee_id": null,
    "aneel_id": "ANE-TRF-2001"
  },
  "substation_id": "550e8400-e29b-41d4-a716-446655440010",
  "manufacturer": "Siemens",
  "model": "SFP 500/230",
  "year_installed": 2005,
  "voltage_kv": 500.0,
  "power_mva": 600.0,
  "status": "operational",
  "criticality": "A",
  "health_score": 82.5,
  "latitude": -23.5505,
  "longitude": -46.6333,
  "metadata": {
    "oil_type": "mineral",
    "cooling": "ONAN/ONAF",
    "weight_tons": 250
  },
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-03-06T08:15:00Z"
}
```

---

### 3.2 Alert Schemas

```python
class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertCreate(BaseModel):
    asset_id: UUID
    severity: AlertSeverity
    alert_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    parameters: Optional[dict] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_id: UUID
    severity: AlertSeverity
    alert_type: str
    title: str
    description: Optional[str] = None
    parameters: Optional[dict] = None
    context: Optional[dict] = None
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    status: AlertStatus
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class AlertAcknowledge(BaseModel):
    acknowledged_by: UUID


class AlertResolve(BaseModel):
    resolved_by: UUID
    resolution_notes: Optional[str] = None
```

**Exemplo JSON - AlertResponse**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440099",
  "asset_id": "550e8400-e29b-41d4-a716-446655440001",
  "severity": "high",
  "alert_type": "temperature_anomaly",
  "title": "Temperatura acima do limiar no TR1 500/230kV",
  "description": "Temperatura do enrolamento atingiu 95.3C, acima do threshold de 85C",
  "parameters": {
    "measured_value": 95.3,
    "threshold": 85.0,
    "parameter": "temperature",
    "unit": "C"
  },
  "context": {
    "recent_trend": "increasing",
    "baseline_avg": 72.5,
    "ambient_temperature": 32.0
  },
  "triggered_at": "2026-03-06T14:22:00Z",
  "acknowledged_at": null,
  "resolved_at": null,
  "status": "open",
  "assigned_to": null,
  "created_at": "2026-03-06T14:22:00Z",
  "updated_at": "2026-03-06T14:22:00Z"
}
```

---

### 3.3 Health Score Schemas

```python
class HealthScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time: datetime
    asset_id: UUID
    overall_score: float = Field(..., ge=0, le=100)
    component_scores: dict
    anomaly_count: int
    trend: str
    model_version: str
    confidence: Optional[float] = Field(None, ge=0, le=1)


class HealthScoreHistoryResponse(BaseModel):
    asset_id: UUID
    asset_name: str
    current_score: float
    scores: list[HealthScoreResponse]
    period_start: datetime
    period_end: datetime
```

**Exemplo JSON - HealthScoreResponse**:
```json
{
  "time": "2026-03-06T12:00:00Z",
  "asset_id": "550e8400-e29b-41d4-a716-446655440001",
  "overall_score": 82.5,
  "component_scores": {
    "thermal": 78.0,
    "electrical": 92.0,
    "mechanical": 85.0,
    "oil_quality": 75.0
  },
  "anomaly_count": 2,
  "trend": "degrading",
  "model_version": "v1.2.0",
  "confidence": 0.91
}
```

---

### 3.4 Case Schemas

```python
class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CasePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseCreate(BaseModel):
    alert_id: Optional[UUID] = None
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority: CasePriority
    assigned_to: Optional[UUID] = None
    sop_id: Optional[UUID] = None


class CaseUpdate(BaseModel):
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    assigned_to: Optional[UUID] = None
    sop_id: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: CaseStatus
    priority: CasePriority
    assigned_to: Optional[UUID] = None
    sop_id: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None
    actions_taken: Optional[list[dict]] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
```

---

### 3.5 Measurement Schemas

```python
class MeasurementCreate(BaseModel):
    time: datetime
    asset_id: UUID
    measurement_point_id: UUID
    parameter: str = Field(..., max_length=50)
    value: float
    quality_flag: int = Field(0, ge=0, le=3)
    source: str = Field(..., max_length=50)


class MeasurementBatchCreate(BaseModel):
    """Para ingestao em lote de medicoes SCADA."""
    measurements: list[MeasurementCreate] = Field(..., max_length=10000)


class MeasurementResponse(BaseModel):
    time: datetime
    asset_id: UUID
    measurement_point_id: UUID
    parameter: str
    value: float
    quality_flag: int
    source: str


class MeasurementAggregateResponse(BaseModel):
    bucket: datetime
    asset_id: UUID
    parameter: str
    avg_value: float
    min_value: float
    max_value: float
    stddev_value: Optional[float] = None
    sample_count: int
```

---

## 4. Resolucao de Identidade

O setor eletrico brasileiro possui tres orgaos principais que mantem cadastros
independentes de entidades (ativos, agentes, instalacoes). O mesmo equipamento pode
ter identificadores diferentes em cada orgao.

### 4.1 O Problema

| Orgao | Escopo                          | Formato de ID          | Exemplo         |
|-------|---------------------------------|------------------------|-----------------|
| ONS   | Operacao do SIN                 | Codigo alfanumerico    | `TRF-SE-ADR-001`|
| CCEE  | Comercializacao de energia      | Codigo numerico perfil | `CCEE-5001`     |
| ANEEL | Regulacao e fiscalizacao        | Codigo outorga         | `ANE-TRF-2001`  |

**Desafios**:
- Nao existe chave unica compartilhada entre os tres sistemas
- Nomes de entidades variam entre orgaos (abreviacoes, grafias diferentes)
- Nem toda entidade existe nos tres sistemas (ex: ativo interno pode nao ter ID CCEE)
- IDs podem mudar ao longo do tempo (fusoes, cisoes, repotenciacao)

### 4.2 Estrategia de Resolucao

A resolucao de identidade usa uma abordagem em duas fases:

#### Fase 1: Matching Deterministico

Regras exatas com alta confianca:

```
1. CNPJ do agente (identificador unico federal)
   - Confianca: 100%
   - Aplica-se a: Agents

2. Codigo ONS + Tipo + Tensao + Subestacao
   - Confianca: 95%
   - Aplica-se a: Assets, Substations

3. Coordenadas geograficas (< 100m de distancia) + Tipo + Tensao
   - Confianca: 90%
   - Aplica-se a: Substations, TransmissionLines
```

#### Fase 2: Matching Probabilistico

Para entidades que nao foram resolvidas na Fase 1:

```
1. Similaridade de nome (Levenshtein / Jaro-Winkler) > 0.85
   + Mesmo tipo de entidade
   + Mesma regiao/estado
   -> Confianca: 70-85% (requer validacao humana)

2. Atributos combinados:
   - Fabricante + Modelo + Ano + Subestacao
   -> Confianca: 80% (para assets)

3. Relacoes topologicas:
   - Se LT conecta mesmas SEs nos dois sistemas
   -> Confianca: 85%
```

Matches probabilisticos com confianca < 90% sao marcados como `pending_review` e
apresentados ao usuario para validacao manual.

### 4.3 Tabela de Crosswalk

```sql
CREATE TABLE identity_crosswalk (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     VARCHAR(50)     NOT NULL,
                    -- asset, substation, transmission_line, agent
    ontogrid_id     UUID            NOT NULL,
                    -- ID interno OntoGrid (assets.id, substations.id, etc.)
    source_system   VARCHAR(20)     NOT NULL
                    CHECK (source_system IN ('ons', 'ccee', 'aneel', 'scada', 'erp', 'gis')),
    source_id       VARCHAR(200)    NOT NULL,
                    -- ID no sistema de origem
    source_name     VARCHAR(300),
                    -- Nome no sistema de origem (para auditoria)
    match_type      VARCHAR(20)     NOT NULL
                    CHECK (match_type IN ('deterministic', 'probabilistic', 'manual')),
    confidence      DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    status          VARCHAR(20)     NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'pending_review', 'rejected', 'superseded')),
    validated_by    UUID,
    validated_at    TIMESTAMPTZ,
    metadata        JSONB           DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Garante unicidade: cada source_id em cada sistema aponta para uma unica entidade
    UNIQUE (source_system, source_id, entity_type)
);
```

**Indexes**:
```sql
CREATE INDEX idx_crosswalk_ontogrid ON identity_crosswalk (ontogrid_id);
CREATE INDEX idx_crosswalk_source ON identity_crosswalk (source_system, source_id);
CREATE INDEX idx_crosswalk_pending ON identity_crosswalk (status)
    WHERE status = 'pending_review';
CREATE INDEX idx_crosswalk_entity ON identity_crosswalk (entity_type, ontogrid_id);
```

**Exemplo de dados**:
```
| entity_type | ontogrid_id | source_system | source_id       | confidence | match_type     | status  |
|-------------|-------------|---------------|-----------------|------------|----------------|---------|
| asset       | uuid-001    | ons           | TRF-SE-ADR-001  | 1.00       | deterministic  | active  |
| asset       | uuid-001    | aneel         | ANE-TRF-2001    | 0.95       | deterministic  | active  |
| asset       | uuid-001    | scada         | PI:TR1.TEMP.PV  | 1.00       | manual         | active  |
| agent       | uuid-010    | ons           | ONS-AG-042      | 1.00       | deterministic  | active  |
| agent       | uuid-010    | ccee          | CCEE-P-5001     | 1.00       | deterministic  | active  |
| agent       | uuid-010    | aneel         | ANE-OUT-7890    | 1.00       | deterministic  | active  |
| substation  | uuid-020    | ons           | SE-ADR-500      | 0.82       | probabilistic  | pending |
```

### 4.4 Fluxo de Resolucao

```
Dados de Entrada (ONS/CCEE/ANEEL/SCADA)
           |
           v
  +--------------------+
  | 1. Normalizacao     |  Padroniza nomes, remove acentos, normaliza codigos
  +--------------------+
           |
           v
  +--------------------+
  | 2. Match Determ.    |  CNPJ, codigo unico, chave composta
  +--------------------+
           |
    +------+------+
    |             |
  Match?        Nao
    |             |
    v             v
 Crosswalk    +--------------------+
 (active)     | 3. Match Probab.    |  Similaridade nome, atributos, topologia
              +--------------------+
                       |
                +------+------+
                |             |
           Conf >= 90%    Conf < 90%
                |             |
                v             v
           Crosswalk      Crosswalk
           (active)       (pending_review)
                              |
                              v
                    +--------------------+
                    | 4. Validacao Manual |  Operador confirma/rejeita
                    +--------------------+
                              |
                              v
                         Crosswalk
                    (active ou rejected)
```

---

## 5. Diagrama ER Simplificado

```
+================================================================+
|                    ENERGY GRAPH (Neo4j)                         |
|                                                                |
|  +----------+    OPERATED_BY    +---------+                    |
|  |  Agent   |<------------------| Asset   |                    |
|  +----------+        +-------->+---------+                     |
|       ^              |         | id      |                     |
|       |         BELONGS_TO     | name    |                     |
|       |              |         | type    |                     |
|  OPERATED_BY         |         | health  |                     |
|       |              |         | score   |                     |
|  +----------+        |         +---------+                     |
|  |Substation|<-------+              |                          |
|  +----------+                  MONITORED_BY                    |
|  | id       |                       |                          |
|  | name     |               +-------v--------+                 |
|  | region   |               |MeasurementPoint|                 |
|  +----------+               +----------------+                 |
|       ^   ^                 | id             |                 |
|       |   |                 | parameter      |                 |
|  FEEDS|   |ORIGINATES       | unit           |                 |
|       |   |                 +----------------+                 |
|  +----+---+-----+                                              |
|  |Transmission   |    DEPENDS_ON                               |
|  |Line           |   (Asset)--------->(Asset)                  |
|  +---------------+                                             |
|                        TRIGGERED           RAISED_ON           |
|  +---------+     (Alert)-------->(Case)  (Alert)---->(Asset)   |
|  | Alert   |                                                   |
|  +---------+     IMPACTS                                       |
|  | Case    |     (Alert)--------->(Asset)                      |
|  +---------+                                                   |
+================================================================+


+================================================================+
|                   TIMESCALEDB (PostgreSQL)                      |
|                                                                |
|  +-------------------+       +-------------------+             |
|  |     agents        |       |   substations     |             |
|  +-------------------+       +-------------------+             |
|  | id (PK)           |       | id (PK)           |             |
|  | name              |  1..* | name              |             |
|  | agent_type        |<------| operator_id (FK)  |             |
|  | cnpj (UNIQUE)     |       | region            |             |
|  | ons_code          |       | state             |             |
|  | ccee_code         |       +-------------------+             |
|  +-------------------+              |                          |
|                                     | 1..*                     |
|                                     v                          |
|                              +-------------------+             |
|                              |     assets        |             |
|  +-------------------+       +-------------------+             |
|  |      sops         |       | id (PK)           |             |
|  +-------------------+       | name              |             |
|  | id (PK)           |       | asset_type        |             |
|  | title             |       | substation_id(FK) |             |
|  | asset_type        |       | voltage_kv        |             |
|  | steps (JSONB)     |       | status            |             |
|  +-------------------+       | criticality       |             |
|         ^                    | external_ids(JSON)|             |
|         |                    +-------------------+             |
|         |                       |            |                 |
|     sop_id(FK)             1..* |            | 1               |
|         |                      v            v                  |
|  +-------------------+  +-----------+  +-------------------+  |
|  |     cases         |  |measurement|  |   alerts          |  |
|  +-------------------+  |_points    |  +-------------------+  |
|  | id (PK)           |  +-----------+  | id (PK)           |  |
|  | alert_id (FK)     |  | id (PK)   |  | asset_id (FK)     |  |
|  | title             |  | asset_id  |  | severity          |  |
|  | status            |  | parameter |  | alert_type        |  |
|  | priority          |  | unit      |  | status            |  |
|  | sop_id (FK)       |  | source    |  | triggered_at      |  |
|  | assigned_to       |  +-----------+  +-------------------+  |
|  +-------------------+       |                                 |
|                              | 1..*                            |
|                              v                                 |
|  +---------------------------------------------------------+  |
|  |            measurements (hypertable)                     |  |
|  +---------------------------------------------------------+  |
|  | time | asset_id | measurement_point_id | parameter |     |  |
|  | value | quality_flag | source | ingested_at        |     |  |
|  +---------------------------------------------------------+  |
|         |                        |                             |
|         v                        v                             |
|  +------------------+   +------------------+                   |
|  |measurements_     |   |measurements_     |                   |
|  |hourly (cagg)     |   |daily (cagg)      |                   |
|  +------------------+   +------------------+                   |
|                                                                |
|  +---------------------------------------------------------+  |
|  |           health_scores (hypertable)                     |  |
|  +---------------------------------------------------------+  |
|  | time | asset_id | overall_score | component_scores |     |  |
|  | anomaly_count | trend | model_version | confidence |     |  |
|  +---------------------------------------------------------+  |
|         |                                                      |
|         v                                                      |
|  +------------------+                                          |
|  |health_scores_    |    +-------------------+                 |
|  |daily (cagg)      |    |identity_crosswalk |                 |
|  +------------------+    +-------------------+                 |
|                          | ontogrid_id       |                 |
|  +-------------------+   | source_system     |                 |
|  |   audit_log       |   | source_id         |                 |
|  +-------------------+   | confidence        |                 |
|  | user_id           |   | match_type        |                 |
|  | action            |   | status            |                 |
|  | entity_type       |   +-------------------+                 |
|  | entity_id         |                                         |
|  | changes (JSONB)   |                                         |
|  +-------------------+                                         |
+================================================================+


+================================================================+
|              SINCRONIZACAO NEO4J <-> TIMESCALEDB               |
|                                                                |
|  TimescaleDB (source of truth para dados estruturados)         |
|       |                                                        |
|       |  CDC / Event-driven sync                               |
|       v                                                        |
|  Neo4j (source of truth para relacoes e topologia)             |
|                                                                |
|  Regras:                                                       |
|  - Entidades (assets, substations, agents) sao criadas no      |
|    TimescaleDB e sincronizadas para Neo4j como nodes           |
|  - Relacoes (BELONGS_TO, CONNECTED_TO, etc.) sao gerenciadas   |
|    no Neo4j e projetadas para queries SQL quando necessario     |
|  - Health scores sao calculados a partir do TimescaleDB e       |
|    atualizados como property no node Asset do Neo4j             |
|  - Alertas existem em ambos: TimescaleDB para queries           |
|    temporais e Neo4j para propagacao de impacto                |
+================================================================+
```

---

## Apendice A: Ordem de Criacao das Tabelas (DDL)

Devido a restricoes de foreign key, a ordem de criacao das tabelas deve ser:

```
1. agents
2. substations       (FK -> agents)
3. assets            (FK -> substations)
4. measurement_points (FK -> assets)
5. measurements      (FK implicita via asset_id, measurement_point_id)
6. health_scores     (referencia asset_id)
7. sops
8. alerts            (FK -> assets)
9. cases             (FK -> alerts, sops)
10. identity_crosswalk
11. audit_log
12. Continuous aggregates (measurements_hourly, measurements_daily, health_scores_daily)
13. Retention policies
14. Compression policies
```

## Apendice B: Convencoes

| Convencao                  | Padrao                                    |
|---------------------------|-------------------------------------------|
| Naming de tabelas         | snake_case, plural (assets, measurements) |
| Naming de colunas         | snake_case (asset_id, created_at)         |
| Primary keys              | UUID v4 (gen_random_uuid())               |
| Timestamps                | TIMESTAMPTZ (sempre com timezone)         |
| Soft delete               | Nao - usamos status field                 |
| Audit                     | Via audit_log table                       |
| Versionamento de schema   | Alembic migrations                        |
| JSONB fields              | Para dados semi-estruturados e extensiveis|
| Enums                     | CHECK constraints (nao Postgres ENUM)     |
| Indexes                   | Criados junto com tabelas no migration    |
