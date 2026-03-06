# Modelo de Dados - OntoGrid MVP v0.1

Este documento define o modelo operacional mínimo do produto. Contratos HTTP pertencem a [API_SPEC.md](/C:/Users/tsimoe01/coding/ontogrid/docs/API_SPEC.md).

## 1. Regras gerais

- Todas as entidades operacionais carregam `tenant_id`.
- IDs são `UUID`.
- Timestamps são armazenados em UTC.
- `agent` e uma entidade de domínio do setor elétrico, nao a chave de isolamento do sistema.

## 2. Entidades operacionais

### tenant

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| slug | text | único |
| name | text | nome do cliente |
| status | text | `active` ou `inactive` |
| created_at | timestamptz | obrigatório |

### user

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | FK `tenant.id` |
| email | text | único por tenant |
| full_name | text | obrigatório |
| role | text | `admin`, `operator`, `viewer` |
| password_hash | text | obrigatório |
| created_at | timestamptz | obrigatório |

### asset

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | obrigatório |
| external_ref | text | id externo opcional |
| name | text | obrigatório |
| asset_type | text | `transformer`, `generator`, `breaker`, `reactor` |
| substation_name | text | opcional no banco relacional |
| nominal_voltage_kv | numeric | opcional |
| criticality | text | `high`, `medium`, `low` |
| status | text | `active`, `maintenance`, `retired` |
| created_at | timestamptz | obrigatório |
| updated_at | timestamptz | obrigatório |

### measurement_point

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | obrigatório |
| asset_id | UUID | FK `asset.id` |
| code | text | identificador do ponto |
| measurement_type | text | `temperature`, `vibration`, `current`, `voltage`, `pressure`, `oil_level` |
| unit | text | unidade |
| source | text | `upload`, `api`, futuro `opcua` |
| created_at | timestamptz | obrigatório |

### measurement

Tabela time-series.

| Campo | Tipo | Observação |
|---|---|---|
| time | timestamptz | chave temporal da hypertable |
| tenant_id | UUID | obrigatório |
| asset_id | UUID | obrigatório |
| measurement_point_id | UUID | opcional no primeiro corte |
| measurement_type | text | obrigatório |
| value | double precision | obrigatório |
| quality_flag | text | `good`, `bad`, `unknown` |
| source | text | `upload` ou `api` |
| ingestion_job_id | UUID | rastreabilidade |

Chave lógica de idempotência:

- `tenant_id`
- `asset_id`
- `measurement_type`
- `time`

### health_score

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | obrigatório |
| asset_id | UUID | obrigatório |
| score | numeric(5,2) | 0 a 100 |
| band | text | `critical`, `warning`, `healthy` |
| calculated_at | timestamptz | obrigatório |
| inputs | jsonb | pesos e sinais usados |

### alert

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | obrigatório |
| asset_id | UUID | obrigatório |
| health_score_id | UUID | opcional |
| severity | text | `critical`, `high`, `medium`, `low` |
| alert_type | text | threshold ou z-score |
| status | text | `open`, `acknowledged`, `closed` |
| message | text | obrigatório |
| created_at | timestamptz | obrigatório |
| acknowledged_at | timestamptz | opcional |

### case

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | obrigatório |
| asset_id | UUID | obrigatório |
| alert_id | UUID | opcional, mas esperado no fluxo principal |
| title | text | obrigatório |
| status | text | `open`, `in_progress`, `resolved` |
| priority | text | `high`, `medium`, `low` |
| created_at | timestamptz | obrigatório |

### ingestion_job

| Campo | Tipo | Observação |
|---|---|---|
| id | UUID | PK |
| tenant_id | UUID | obrigatório |
| source_type | text | `file_upload` ou `json_batch` |
| payload_format | text | `csv`, `xlsx`, `json` |
| status | text | `queued`, `processing`, `completed`, `failed` |
| records_received | integer | default 0 |
| records_accepted | integer | default 0 |
| records_rejected | integer | default 0 |
| error_summary | text | opcional |
| created_at | timestamptz | obrigatório |
| completed_at | timestamptz | opcional |

## 3. Energy Graph v0.1

O Neo4j no v0.1 nao substitui o modelo operacional. Ele guarda apenas a topologia necessária para navegação e impacto.

### Nós

- `Asset`
- `Substation`
- `Line`

### Relações

- `(:Substation)-[:CONTAINS]->(:Asset)`
- `(:Substation)-[:CONNECTS_TO]->(:Line)`
- `(:Line)-[:CONNECTS_TO]->(:Substation)`
- `(:Asset)-[:DEPENDS_ON]->(:Asset)` quando houver dependência explícita

### Propriedades mínimas

- `tenant_id`
- `id`
- `name`
- `type`

## 4. Health score v0

Regra inicial:

- score base 100;
- penalidade por threshold estourado;
- penalidade por z-score alto persistente;
- pesos por tipo de ativo;
- banda final:
  - `critical`: score < 40
  - `warning`: score >= 40 e < 70
  - `healthy`: score >= 70

## 5. Índices mínimos

- `asset(tenant_id, name)`
- `measurement(tenant_id, asset_id, measurement_type, time desc)`
- `health_score(tenant_id, asset_id, calculated_at desc)`
- `alert(tenant_id, status, created_at desc)`
- `case(tenant_id, status, created_at desc)`
- `ingestion_job(tenant_id, status, created_at desc)`

## 6. Itens adiados

- MDM completo com reconciliação multi-fonte.
- Ontologia expandida de agentes regulatórios.
- Modelos dedicados para SOP, comentario, anexo, notificacao e supressao de alarme.
