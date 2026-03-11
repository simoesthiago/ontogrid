# Modelo de Dados - OntoGrid Energy Data Hub MVP

Este documento define o modelo canonico do MVP publico. Contratos HTTP pertencem a [API_SPEC.md](../contracts/API_SPEC.md).

## 1. Regras gerais

- O nucleo publico nao usa `tenant_id` como chave central.
- IDs sao `UUID`.
- Timestamps sao armazenados em UTC.
- `dataset_version` e imutavel depois de publicada.
- Toda resposta analitica precisa ser rastreavel ate `source`, `dataset` e `dataset_version`.

## 2. Entidades publicas

### source

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| code | text | unico |
| name | text | obrigatorio |
| authority_type | text | `regulator`, `system_operator`, `market_operator` |
| refresh_strategy | text | `api_pull`, `scheduled_download`, `crawler` |
| status | text | `active`, `paused`, `deprecated` |
| created_at | timestamptz | obrigatorio |
| updated_at | timestamptz | obrigatorio |

### dataset

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| source_id | UUID | FK `source.id` |
| code | text | unico por fonte |
| name | text | obrigatorio |
| domain | text | `operacao`, `mercado`, `regulatorio`, `cadastro` |
| granularity | text | `event`, `day`, `hour`, `month`, `file` |
| description | text | obrigatorio |
| schema_summary | jsonb | dimensoes e metricas principais |
| refresh_frequency | text | ex. `daily` |
| latest_version_id | UUID | opcional |
| created_at | timestamptz | obrigatorio |
| updated_at | timestamptz | obrigatorio |

### dataset_version

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| dataset_id | UUID | FK `dataset.id` |
| label | text | ex. `2026-03-09` |
| extracted_at | timestamptz | obrigatorio |
| published_at | timestamptz | obrigatorio |
| coverage_start | timestamptz | opcional |
| coverage_end | timestamptz | opcional |
| row_count | integer | obrigatorio |
| schema_version | text | obrigatorio |
| checksum | text | obrigatorio |
| status | text | `published`, `partial`, `failed` |
| lineage | jsonb | referencia minima ao refresh e ao artefato |

### refresh_job

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| dataset_id | UUID | FK `dataset.id` |
| source_type | text | `api_pull`, `scheduled_download`, `crawler` |
| trigger_type | text | `schedule`, `manual` |
| status | text | `queued`, `running`, `published`, `failed`, `partial` |
| rows_read | integer | default 0 |
| rows_written | integer | default 0 |
| error_summary | text | opcional |
| started_at | timestamptz | opcional |
| finished_at | timestamptz | opcional |
| created_at | timestamptz | obrigatorio |

### entity

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| entity_type | text | vocabulario publico: `agent`, `plant`, `generation_unit`, `distributor`, `municipality`, `subsystem`, `submarket`, `reservoir` |
| canonical_code | text | unico por tipo quando aplicavel |
| name | text | obrigatorio |
| jurisdiction | text | ex. `BR`, `SE`, `SIN` |
| attributes | jsonb | atributos canonicos minimamente tipados |
| first_seen_at | timestamptz | obrigatorio |
| last_seen_at | timestamptz | obrigatorio |

### entity_alias

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| entity_id | UUID | FK `entity.id` |
| source_id | UUID | FK `source.id` |
| external_code | text | codigo da origem |
| alias_name | text | nome alternativo |
| confidence | numeric(5,2) | opcional |
| created_at | timestamptz | obrigatorio |
| updated_at | timestamptz | obrigatorio |

### relation

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| dataset_version_id | UUID | FK `dataset_version.id` |
| relation_type | text | vocabulario minimo: `OPERATED_BY`, `OWNED_BY`, `HAS_UNIT`, `LOCATED_IN`, `BELONGS_TO_SUBSYSTEM`, `MAPPED_TO_SUBMARKET`, `HAS_TARIFF`, `HAS_QUALITY_INDICATOR` |
| source_entity_id | UUID | FK `entity.id` |
| target_entity_id | UUID | FK `entity.id` |
| valid_from | timestamptz | opcional |
| valid_to | timestamptz | opcional |
| attributes | jsonb | contexto da relacao |

### metric_series

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| dataset_id | UUID | FK `dataset.id` |
| entity_type | text | tipo de entidade indexada pela serie |
| metric_code | text | obrigatorio |
| metric_name | text | obrigatorio |
| unit | text | obrigatorio |
| temporal_granularity | text | `hour`, `day`, `month`, `event` |
| semantic_value_type | text | identidade semantica denormalizada para indexacao: `observed`, `accounted`, `regulatory_effective` |
| reference_time_kind | text | identidade temporal denormalizada para indexacao: `instant`, `effective_date`, `reference_month` |
| dimensions | jsonb | eixos complementares |
| latest_observation_at | timestamptz | opcional |

### observation

Tabela time-series.

| Campo | Tipo | Observacao |
|---|---|---|
| time | timestamptz | chave temporal da hypertable |
| series_id | UUID | obrigatorio |
| entity_id | UUID | obrigatorio |
| dataset_version_id | UUID | obrigatorio |
| value_numeric | double precision | opcional |
| value_text | text | opcional |
| quality_flag | text | `published`, `estimated`, `revised` |
| dimensions | jsonb | chaves adicionais |
| published_at | timestamptz | obrigatorio |

Chave logica de idempotencia:

- `series_id`
- `entity_id`
- `time`
- `dataset_version_id`

### insight_snapshot

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| scope_type | text | `overview`, `entity`, `dataset` |
| scope_id | UUID | opcional |
| title | text | obrigatorio |
| summary | text | obrigatorio |
| payload | jsonb | cards, highlights e referencias |
| dataset_version_id | UUID | opcional |
| generated_at | timestamptz | obrigatorio |

### copilot_trace

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| question | text | obrigatorio |
| scope | jsonb | datasets, entidades e janela temporal |
| answer_payload | jsonb | resposta e citacoes |
| created_at | timestamptz | obrigatorio |

## 3. Camada semantica seletiva

Regra de modelagem:

- as tabelas abaixo complementam o kernel `entity` / `relation` / `metric_series` / `observation`;
- nenhuma substitui o kernel relacional;
- `party_master`, `agent_profile_master`, `asset_master_generation`, `geo_electric_master` e `series_registry` representam o snapshot canonico atual;
- o historico auditavel continua em `dataset_version`, `relation`, `observation`, `evidence_registry` e `harmonization_event`.

### party_master

| Campo | Tipo | Observacao |
|---|---|---|
| entity_id | UUID | PK e FK `entity.id` |
| tax_id | text | CNPJ/CPF normalizado quando houver |
| legal_name | text | obrigatorio |
| trade_name | text | opcional |
| status | text | ex. `active` |
| source_dataset_version_id | UUID | FK `dataset_version.id` |
| lineage | jsonb | proveniencia e faceta de harmonizacao |

### agent_profile_master

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| entity_id | UUID | FK `entity.id` |
| party_entity_id | UUID | FK `entity.id`, opcional |
| profile_kind | text | ex. `sector`, `market` |
| role | text | ex. `generator`, `seller`, `distributor` |
| source_code | text | `aneel`, `ons`, `ccee` |
| external_code | text | codigo externo exato da origem quando houver |
| valid_from | timestamptz | opcional |
| valid_to | timestamptz | opcional |
| source_dataset_version_id | UUID | FK `dataset_version.id` |

### asset_master_generation

| Campo | Tipo | Observacao |
|---|---|---|
| entity_id | UUID | PK e FK `entity.id` |
| ceg | text | indexado |
| ons_plant_code | text | indexado |
| source_type | text | ex. `hidreletrica`, `termica` |
| fuel_type | text | opcional |
| installed_capacity_mw | double precision | opcional |
| status | text | ex. `operating`, `granted` |
| municipality_entity_id | UUID | FK `entity.id`, opcional |
| subsystem_entity_id | UUID | FK `entity.id`, opcional |
| submarket_entity_id | UUID | FK `entity.id`, opcional |
| source_dataset_version_id | UUID | FK `dataset_version.id` |

### asset_bridge_generation

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| asset_entity_id | UUID | FK `entity.id` |
| bridge_kind | text | ex. `ceg`, `ons_plant_code`, `source_alias` |
| external_code | text | obrigatorio |
| source_code | text | `aneel`, `ons`, `ccee` |
| valid_from | timestamptz | opcional |
| valid_to | timestamptz | opcional |
| source_dataset_version_id | UUID | FK `dataset_version.id` |

### geo_electric_master

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| entity_id | UUID | FK `entity.id` |
| geo_type | text | `municipality`, `subsystem`, `submarket`, `reservoir` |
| ibge_code | text | aplicavel a municipio |
| operator_code | text | codigo eletrico canonico |
| parent_entity_id | UUID | FK `entity.id`, opcional |
| mapped_entity_id | UUID | FK `entity.id`, opcional |
| valid_from | timestamptz | opcional |
| valid_to | timestamptz | opcional |
| source_dataset_version_id | UUID | FK `dataset_version.id` |

### series_registry

| Campo | Tipo | Observacao |
|---|---|---|
| metric_series_id | UUID | PK e FK `metric_series.id` |
| semantic_value_type | text | `observed`, `accounted`, `regulatory_effective` |
| reference_time_kind | text | `instant`, `effective_date`, `reference_month` |
| target_entity_type | text | alvo semantico da serie |
| unit | text | unidade canonica |
| source_dataset_version_id | UUID | FK `dataset_version.id` |

### evidence_registry

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| scope_type | text | ex. `observation`, `relation`, `harmonization` |
| scope_id | text | seletor estavel do claim |
| dataset_version_id | UUID | FK `dataset_version.id` |
| entity_id | UUID | FK `entity.id`, opcional |
| series_id | UUID | FK `metric_series.id`, opcional |
| observation_selector | jsonb | detalhes do claim e seletor rastreavel |
| claim_text | text | frase curta grounded |
| created_at | timestamptz | obrigatorio |

### harmonization_event

| Campo | Tipo | Observacao |
|---|---|---|
| id | UUID | PK |
| dataset_version_id | UUID | FK `dataset_version.id` |
| entity_id | UUID | FK `entity.id` |
| source_code | text | `aneel`, `ons`, `ccee` |
| entity_type | text | mesmo vocabulario publico de `entity` |
| source_record_key | text | chave do registro harmonizado na rodada |
| decision | text | `created_new` ou `matched_existing` |
| match_rule | text | ex. `exact_tax_id`, `exact_ceg`, `source_external_code` |
| matched_on | jsonb | valores usados para o match |
| source_identity | jsonb | espelho minimo do registro de entrada |
| created_at | timestamptz | obrigatorio |

## 4. Energy Graph publico v1

O Neo4j no MVP publico nao substitui o modelo relacional. Ele projeta entidades e relacoes canonicamente resolvidas para navegacao e contexto.

### Nos

- `Source`
- `Dataset`
- `Entity`

### Relacoes

- `(:Dataset)-[:PUBLISHED_BY]->(:Source)`
- `(:Entity)-[:OPERATED_BY]->(:Entity)`
- `(:Entity)-[:LOCATED_IN]->(:Entity)`
- `(:Entity)-[:BELONGS_TO_SUBSYSTEM]->(:Entity)`
- `(:Entity)-[:MAPPED_TO_SUBMARKET]->(:Entity)`
- `(:Entity)-[:HAS_QUALITY_INDICATOR]->(:Entity)` quando aplicavel
- `(:Dataset)-[:REFERENCES]->(:Entity)`

### Propriedades minimas

- `id`
- `type`
- `name`
- `canonical_code`
- `dataset_version_id` quando a projecao depender de versao especifica

## 5. Extensao enterprise - Fase 2

Quando a fase enterprise comecar, entram entidades tenant-scoped como:

- `tenant`
- `user`
- `private_connection`
- `asset`
- `measurement_point`
- `measurement`
- `alert`
- `case`
- `workflow_run`

Regra: `tenant_id` passa a ser obrigatorio apenas dentro dessa camada.

## 6. Indices minimos

- `source(code)`
- `dataset(source_id, code)`
- `dataset_version(dataset_id, published_at desc)`
- `refresh_job(dataset_id, created_at desc)`
- `entity(entity_type, name)`
- `entity_alias(source_id, external_code)`
- `relation(source_entity_id, target_entity_id)`
- `metric_series(dataset_id, metric_code, entity_type, semantic_value_type, reference_time_kind)`
- `observation(series_id, entity_id, time desc)`
- `series_registry(semantic_value_type, reference_time_kind)`
- `evidence_registry(entity_id, created_at desc)`
- `harmonization_event(dataset_version_id, source_record_key)`

## 7. Itens adiados

- clean room e benchmarking multiempresa;
- controles enterprise de linha e coluna;
- modelos dedicados para SOP, comentario, anexo e notificacao;
- features private-first do slice de Vigilancia Operacional de Ativos.
