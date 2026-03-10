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
      "freshness_status": "fresh"
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

## 4. Series

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
      "latest_observation_at": "2026-03-09T23:00:00Z"
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
      "timestamp": "2026-03-09T12:00:00Z",
      "value": 81234.5,
      "unit": "MW",
      "quality_flag": "published",
      "published_at": "2026-03-09T12:00:00Z"
    }
  ]
}
```

## 5. Graph

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
      "entity_type": "substation",
      "canonical_code": "SE-CENTRO",
      "name": "SE Centro",
      "aliases": ["Subestacao Centro"],
      "jurisdiction": "BR"
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
  "entity_type": "substation",
  "canonical_code": "SE-CENTRO",
  "name": "SE Centro",
  "attributes": {
    "owner": "ONS",
    "voltage_kv": 230
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
    { "id": "uuid", "type": "Entity", "name": "SE Centro" },
    { "id": "uuid", "type": "Entity", "name": "LT-230-01" }
  ],
  "edges": [
    { "source": "uuid", "target": "uuid", "type": "CONNECTS_TO" }
  ],
  "provenance": {
    "dataset_version_ids": ["uuid"]
  }
}
```

## 6. Insights

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

## 7. Copilot

### `POST /api/v1/copilot/query`

Observacoes operacionais:

- o copilot usa cache em Redis para respostas bem-sucedidas;
- retorna `503` quando o provider LLM nao estiver configurado;
- quando nao houver grounding suficiente, responde `200` com explicacao explicita e `citations` vazias.

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
      "version_id": "uuid",
      "entity_id": "uuid"
    }
  ],
  "follow_up_questions": [
    "Quero comparar com o Sul no mesmo periodo."
  ]
}
```

## 8. Endpoint interno

### `GET /healthz`

Usado para health check de servico. Nao faz parte do contrato de produto.

## 9. Bootstrap oficial

- `docker compose up --build` aplica migrations Alembic e executa o bootstrap live do catalogo antes de subir a API;
- o startup normal do app nao cria schema via ORM e assume banco migrado.

## 10. Fora do contrato do MVP publico

- tenancy como pivote universal;
- uploads privados e integracoes de cliente;
- `assets`, `measurements`, `health`, `alerts` e `cases` como contrato principal;
- RAG sobre documentos privados;
- copilots de workflow pesado;
- field assistant e reliability sobre OMS privado.
