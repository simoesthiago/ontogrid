# API Spec - OntoGrid Energy Data Hub MVP

Este documento e a fonte de verdade dos contratos HTTP do MVP publico. Se outro documento divergir, este documento vence para o build atual.

## 1. Convencoes

- Prefixo base: `/api/v1`
- Formato: `application/json`
- Timezone: respostas em ISO-8601 UTC
- Leituras publicas nao dependem de `tenant_id`
- Endpoints em `/api/v1/admin` sao operacionais e exigem credencial de servico ou papel administrativo quando essa camada existir
- O runtime oficial usa PostgreSQL/Timescale, Neo4j e Redis; SQLite fica restrito a testes e ambientes efemeros

### Envelope de erro

```json
{
  "error": {
    "code": "validation_error",
    "message": "Payload invalido",
    "details": {}
  }
}
```

## 2. Sources

### `GET /api/v1/sources`

Query params:

- `q`
- `status`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "code": "aneel",
      "name": "ANEEL",
      "authority_type": "regulator",
      "refresh_strategy": "scheduled_download",
      "status": "active"
    }
  ],
  "total": 1
}
```

## 3. Datasets

Observacao operacional:

- o catalogo exposto por `/datasets` inclui o universo inventariado em `docs/datasets`, nao apenas os datasets ja ingeridos;
- o snapshot oficial do repo sobre esse universo fica em `docs/datasets/catalog_status.json` e `docs/datasets/CATALOG_STATUS.md`;
- `ingestion_status` pode ser `documented_only`, `adapter_enabled` ou `published`.

### `GET /api/v1/datasets`

Query params:

- `source`
- `domain`
- `granularity`
- `q`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "source_code": "ons",
      "code": "carga_horaria_submercado",
      "name": "Carga horaria por submercado",
      "domain": "operacao",
      "granularity": "hour",
      "latest_version": "2026-03-09",
      "latest_published_at": "2026-03-09T12:00:00Z",
      "freshness_status": "fresh",
      "adapter_enabled": true,
      "ingestion_status": "published"
    }
  ],
  "total": 1
}
```

### `GET /api/v1/datasets/{dataset_id}`

Response `200`:

```json
{
  "id": "uuid",
  "source_id": "uuid",
  "source_code": "ons",
  "code": "carga_horaria_submercado",
  "name": "Carga horaria por submercado",
  "domain": "operacao",
  "description": "Serie horaria curada a partir do portal do ONS.",
  "granularity": "hour",
  "refresh_frequency": "daily",
  "schema_summary": {
    "dimensions": ["submarket"],
    "metrics": ["load_mw"]
  },
  "adapter_enabled": true,
  "ingestion_status": "published",
  "latest_version": {
    "id": "uuid",
    "label": "2026-03-09",
    "published_at": "2026-03-09T12:00:00Z"
  }
}
```

### `GET /api/v1/datasets/{dataset_id}/versions`

Response `200`:

```json
{
  "dataset_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "label": "2026-03-09",
      "extracted_at": "2026-03-09T11:55:00Z",
      "published_at": "2026-03-09T12:00:00Z",
      "coverage_start": "2026-03-01T00:00:00Z",
      "coverage_end": "2026-03-09T23:00:00Z",
      "status": "published",
      "checksum": "sha256"
    }
  ]
}
```

### `GET /api/v1/datasets/{dataset_id}/versions/{version_id}`

Response `200`:

```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "label": "2026-03-09",
  "extracted_at": "2026-03-09T11:55:00Z",
  "published_at": "2026-03-09T12:00:00Z",
  "coverage_start": "2026-03-01T00:00:00Z",
  "coverage_end": "2026-03-09T23:00:00Z",
  "row_count": 744,
  "schema_version": "v1",
  "checksum": "sha256",
  "lineage": {
    "source_code": "ons",
    "refresh_job_id": "uuid"
  }
}
```

### `POST /api/v1/admin/datasets/{dataset_id}/refresh`

Behavior:

- cria um `refresh_job` rastreavel;
- nao apaga a ultima versao valida quando houver falha;
- responde `409` quando o dataset esta apenas documentado no catalogo, mas ainda nao possui adapter de ingestao;
- retorna `202`.

Response `202`:

```json
{
  "refresh_job_id": "uuid",
  "dataset_id": "uuid",
  "status": "queued",
  "requested_at": "2026-03-09T12:05:00Z"
}
```

### `GET /api/v1/admin/refresh-jobs`

Query params:

- `dataset_id`
- `status`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "dataset_id": "uuid",
      "dataset_code": "carga_horaria_submercado",
      "dataset_name": "Carga horaria por submercado",
      "source_code": "ons",
      "trigger_type": "manual",
      "status": "published",
      "rows_read": 744,
      "rows_written": 744,
      "error_summary": null,
      "created_at": "2026-03-09T12:05:00Z",
      "started_at": "2026-03-09T12:05:02Z",
      "finished_at": "2026-03-09T12:05:10Z",
      "published_version_id": "uuid",
      "published_version_label": "2026-03-09"
    }
  ],
  "total": 1
}
```

### `GET /api/v1/admin/refresh-jobs/{refresh_job_id}`

Response `200`:

```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "dataset_code": "carga_horaria_submercado",
  "dataset_name": "Carga horaria por submercado",
  "source_code": "ons",
  "trigger_type": "manual",
  "status": "published",
  "rows_read": 744,
  "rows_written": 744,
  "error_summary": null,
  "created_at": "2026-03-09T12:05:00Z",
  "started_at": "2026-03-09T12:05:02Z",
  "finished_at": "2026-03-09T12:05:10Z",
  "published_version_id": "uuid",
  "published_version_label": "2026-03-09"
}
```

## 4. Coverage

Observacoes operacionais:

- este endpoint descreve o estado do ambiente em execucao, nao um snapshot estatico do git;
- o estado oficial do repo sobre os 345 datasets fica em `docs/datasets/catalog_status.json` e `docs/datasets/CATALOG_STATUS.md`;
- `published_total` depende do banco e dos refresh jobs daquele ambiente.

### `GET /api/v1/catalog/coverage`

Response `200`:

```json
{
  "inventoried_total": 345,
  "documented_only_total": 334,
  "adapter_enabled_total": 0,
  "published_total": 11,
  "sources": [
    {
      "source_code": "aneel",
      "source_name": "ANEEL",
      "source_document": "docs/datasets/datasets_ANEEL.md",
      "inventoried_total": 69,
      "documented_only_total": 65,
      "adapter_enabled_total": 0,
      "published_total": 4
    }
  ],
  "families": [
    {
      "source_code": "ons",
      "family": "Carga, balanco e programacao",
      "inventoried_total": 13,
      "documented_only_total": 11,
      "adapter_enabled_total": 0,
      "published_total": 2
    }
  ]
}
```

## 5. Series

### `GET /api/v1/series`

Query params:

- `dataset_id`
- `entity_id`
- `metric_code`
- `interval`
- `q`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "dataset_id": "uuid",
      "metric_code": "load_mw",
      "metric_name": "Carga",
      "unit": "MW",
      "temporal_granularity": "hour",
      "entity_type": "submarket",
      "latest_observation_at": "2026-03-09T23:00:00Z",
      "semantic_value_type": "observed",
      "reference_time_kind": "instant"
    }
  ],
  "total": 1
}
```

### `GET /api/v1/series/{series_id}/observations`

Query params:

- `start`
- `end`
- `bucket`
- `dataset_version_id`
- `entity_id`
- `limit`
- `offset`

Response `200`:

```json
{
  "series_id": "uuid",
  "dataset_version_id": "uuid",
  "items": [
    {
      "entity_id": "uuid",
      "entity_name": "Sudeste/Centro-Oeste",
      "timestamp": "2026-03-09T12:00:00Z",
      "value": 81234.5,
      "unit": "MW",
      "quality_flag": "published",
      "published_at": "2026-03-09T12:00:00Z"
    }
  ]
}
```

## 6. Entities

### `GET /api/v1/entities`

Observacoes operacionais:

- este e o endpoint primario para navegacao por entidades no produto;
- nao depende de Neo4j para listar o catalogo canonico;
- `entity_type` aceita os tipos publicos canonicos do MVP, como `agent`, `distributor`, `plant`, `submarket` e `reservoir`.

Query params:

- `q`
- `entity_type`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "entity_type": "submarket",
      "canonical_code": "SE-CO",
      "name": "Sudeste/Centro-Oeste",
      "aliases": ["Sudeste/Centro-Oeste"],
      "jurisdiction": "SIN"
    }
  ],
  "total": 1
}
```

### `GET /api/v1/entities/{entity_id}/profile`

Observacoes operacionais:

- agrega identidade, aliases, facetas semanticas, series, vizinhanca e evidencia;
- funciona mesmo quando Neo4j estiver indisponivel, retornando `graph_status = "unavailable"` e `neighbors = null`.

Response `200`:

```json
{
  "identity": {
    "id": "uuid",
    "entity_type": "plant",
    "canonical_code": "PLANT-CEG-ITAIPU",
    "name": "UHE Itaipu",
    "jurisdiction": "PR",
    "attributes": {
      "source_code": "aneel",
      "ceg": "CEG-ITAIPU"
    }
  },
  "aliases": [
    {
      "source_code": "ons",
      "alias_name": "UHE Itaipu",
      "external_code": "ONS-001",
      "confidence": 1.0
    }
  ],
  "semantic_type": "plant",
  "facets": {
    "party": null,
    "agent_profile": [],
    "generation_asset": {
      "ceg": "CEG-ITAIPU",
      "ons_plant_code": "ONS-001",
      "source_type": "hidreletrica",
      "fuel_type": "agua",
      "installed_capacity_mw": 14000.0,
      "status": "operating",
      "municipality_entity_id": "uuid",
      "subsystem_entity_id": "uuid",
      "submarket_entity_id": "uuid",
      "bridge_codes": [
        {
          "bridge_kind": "ceg",
          "external_code": "CEG-ITAIPU",
          "source_code": "aneel"
        }
      ]
    },
    "geo": [],
    "regulatory": null
  },
  "series": [
    {
      "series_id": "uuid",
      "dataset_id": "uuid",
      "dataset_code": "geracao_usina_horaria",
      "metric_code": "generation_mw",
      "metric_name": "Geracao verificada",
      "unit": "MW",
      "temporal_granularity": "hour",
      "semantic_value_type": "observed",
      "reference_time_kind": "instant",
      "latest_observation_at": "2026-03-09T23:00:00Z",
      "latest_value": 13200.0
    }
  ],
  "neighbors": {
    "entity_id": "uuid",
    "nodes": [],
    "edges": [],
    "provenance": {
      "dataset_version_ids": ["uuid"]
    }
  },
  "recent_versions": [
    {
      "dataset_version_id": "uuid",
      "label": "2026-03-09",
      "published_at": "2026-03-09T23:00:00Z",
      "dataset_id": "uuid",
      "dataset_code": "geracao_usina_horaria"
    }
  ],
  "evidence": [
    {
      "id": "uuid",
      "scope_type": "harmonization",
      "scope_id": "harmonization:uuid",
      "dataset_version_id": "uuid",
      "series_id": null,
      "selector": {
        "decision": "matched_existing",
        "match_rule": "exact_ceg"
      },
      "claim_text": "UHE Itaipu foi reconciliada pela regra exact_ceg durante a harmonizacao publica da fonte ons.",
      "created_at": "2026-03-09T23:00:00Z"
    }
  ],
  "graph_status": "available"
}
```

## 7. Views

### `GET /api/v1/views`

Query params:

- `scope_type`
- `scope_id`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "demo-user",
      "scope_type": "dataset",
      "scope_id": "uuid",
      "name": "Carga por submercado",
      "description": null,
      "config_json": {
        "dataset_id": "uuid",
        "entity_id": null,
        "rows": ["entity_name"],
        "columns": [],
        "filters": [],
        "measures": [
          { "field": "load_mw", "aggregation": "sum" }
        ],
        "visualization": { "type": "table" }
      },
      "created_at": "2026-03-13T12:00:00Z",
      "updated_at": "2026-03-13T12:00:00Z"
    }
  ],
  "total": 1
}
```

### `POST /api/v1/views`

Request:

```json
{
  "scope_type": "entity",
  "scope_id": "uuid",
  "name": "PLD da entidade",
  "description": null,
  "config_json": {
    "dataset_id": "uuid",
    "entity_id": "uuid",
    "rows": ["timestamp"],
    "columns": [],
    "filters": [],
    "measures": [
      { "field": "pld_avg_rs_mwh", "aggregation": "avg" }
    ],
    "visualization": { "type": "line" }
  }
}
```

### `PATCH /api/v1/views/{view_id}`

Atualiza `name`, `description` e/ou `config_json`.

### `DELETE /api/v1/views/{view_id}`

Retorna `204`.

## 8. Analysis

### `GET /api/v1/analysis/datasets/{dataset_id}/fields`

Response `200`:

```json
{
  "dataset_id": "uuid",
  "dimensions": [
    { "id": "entity_name", "label": "Submarket", "kind": "entity" },
    { "id": "timestamp", "label": "Timestamp", "kind": "time" }
  ],
  "metrics": [
    {
      "field": "load_mw",
      "label": "Carga",
      "unit": "MW",
      "supported_aggregations": ["sum", "avg", "count", "min", "max"]
    }
  ],
  "time_fields": ["timestamp"],
  "entity_field": "entity_name",
  "default_measure": "load_mw"
}
```

### `POST /api/v1/analysis/query`

Request:

```json
{
  "config": {
    "dataset_id": "uuid",
    "entity_id": null,
    "rows": ["entity_name"],
    "columns": [],
    "filters": [],
    "measures": [
      { "field": "load_mw", "aggregation": "sum" }
    ],
    "visualization": { "type": "table" }
  }
}
```

Response `200`:

```json
{
  "dataset_id": "uuid",
  "columns": [
    { "id": "entity_name", "label": "Submarket", "kind": "dimension" },
    { "id": "load_mw__sum", "label": "Load Mw Sum", "kind": "measure" }
  ],
  "rows": [
    {
      "values": {
        "entity_name": "Sudeste/Centro-Oeste",
        "load_mw__sum": 81234.5
      }
    }
  ],
  "totals": {
    "load_mw__sum": 81234.5
  },
  "applied_filters": []
}
```

## 9. Graph

### `GET /api/v1/graph/entities`

Observacao operacional:

- retorna `503` quando o backend Neo4j nao estiver configurado ou disponivel.

Query params:

- `q`
- `entity_type`
- `source`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "entity_type": "submarket",
      "canonical_code": "SE-CO",
      "name": "Sudeste/Centro-Oeste",
      "aliases": ["Sudeste/Centro-Oeste"],
      "jurisdiction": "SIN"
    }
  ],
  "total": 1
}
```

### `GET /api/v1/graph/entities/{entity_id}`

Observacao operacional:

- retorna `503` quando o backend Neo4j nao estiver configurado ou disponivel.

Response `200`:

```json
{
  "id": "uuid",
  "entity_type": "submarket",
  "canonical_code": "SE-CO",
  "name": "Sudeste/Centro-Oeste",
  "attributes": {
    "source_code": "ons",
    "operator_code": "SE-CO"
  }
}
```

### `GET /api/v1/graph/entities/{entity_id}/neighbors`

Observacao operacional:

- retorna `503` quando o backend Neo4j nao estiver configurado ou disponivel.

Response `200`:

```json
{
  "entity_id": "uuid",
  "nodes": [
    { "id": "uuid", "type": "Entity", "name": "Sudeste/Centro-Oeste" },
    { "id": "uuid", "type": "Dataset", "name": "Carga horaria por submercado" }
  ],
  "edges": [
    { "source": "uuid", "target": "uuid", "type": "REFERENCES" }
  ],
  "provenance": {
    "dataset_version_ids": ["uuid"]
  }
}
```

## 10. Insights

### `GET /api/v1/insights/overview`

Query params:

- `domain`
- `period`

Response `200`:

```json
{
  "cards": [
    {
      "id": "uuid",
      "title": "PLD medio horario",
      "value": 187.3,
      "unit": "R$/MWh",
      "trend": "up"
    }
  ],
  "highlights": [
    {
      "title": "Carga no Sudeste subiu 4.1%",
      "dataset_version_id": "uuid"
    }
  ]
}
```

### `GET /api/v1/insights/entities/{entity_id}`

Response `200`:

```json
{
  "entity_id": "uuid",
  "summary": "A entidade aparece em 3 datasets curados e 2 relacoes principais.",
  "related_series": [
    {
      "series_id": "uuid",
      "metric_code": "load_mw"
    }
  ],
  "recent_changes": [
    {
      "dataset_version_id": "uuid",
      "message": "Nova versao publicada em 2026-03-09."
    }
  ]
}
```

## 11. Copilot

### `POST /api/v1/copilot/query`

Observacoes operacionais:

- o copilot usa cache em Redis para respostas bem-sucedidas;
- retorna `503` quando o provider LLM nao estiver configurado;
- quando nao houver grounding suficiente, responde `200` com explicacao explicita e `citations` vazias;
- o grounding pode vir de observacoes publicadas ou de evidencia publicada de harmonizacao e relacao.

Request:

```json
{
  "question": "Quais mudancas recentes apareceram no PLD horario do Sudeste?",
  "dataset_ids": ["uuid"],
  "entity_ids": ["uuid"],
  "start": "2026-03-01T00:00:00Z",
  "end": "2026-03-09T23:59:59Z",
  "locale": "pt-BR"
}
```

Response `200`:

```json
{
  "answer": "O PLD horario do Sudeste mostrou alta nas ultimas publicacoes consideradas.",
  "citations": [
    {
      "source_code": "ccee",
      "dataset_id": "uuid",
      "dataset_code": "pld_horario_submercado",
      "dataset_name": "PLD horario por submercado",
      "version_id": "uuid",
      "version_label": "2026-03-09",
      "entity_id": "uuid",
      "entity_name": "Sudeste/Centro-Oeste",
      "evidence_id": "uuid"
    }
  ],
  "follow_up_questions": [
    "Quero comparar com o Sul no mesmo periodo."
  ]
}
```

## 12. Endpoint interno

### `GET /healthz`

Usado para health check de servico. Nao faz parte do contrato de produto.

## 13. Bootstrap oficial

- `docker compose up --build` executa `python -m app.cli bootstrap` antes de subir a API;
- `BOOTSTRAP_MODE=sample` e o default recomendado para desenvolvimento local;
- `BOOTSTRAP_MODE=selected_live` so deve ser usado com `BOOTSTRAP_DATASET_CODES`;
- o runtime local nao pressupoe ingestao live de todos os datasets catalogados;
- o startup normal do app nao cria schema via ORM e assume banco migrado.

## 14. Fora do contrato do MVP publico

- tenancy como pivote universal;
- uploads privados e integracoes de cliente;
- `assets`, `measurements`, `health`, `alerts` e `cases` como contrato principal;
- RAG sobre documentos privados;
- copilots de workflow pesado;
- field assistant e reliability sobre OMS privado.
