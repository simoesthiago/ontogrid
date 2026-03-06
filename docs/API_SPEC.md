# API Spec - OntoGrid MVP v0.1

Este documento e a fonte de verdade dos contratos HTTP do MVP. Se outro documento divergir, este documento vence.

## 1. Convenções

- Prefixo base: `/api/v1`
- Autenticação: `Authorization: Bearer <token>`
- Formato: `application/json`, exceto upload multipart
- Timezone: respostas em ISO-8601 UTC
- Isolamento: `tenant_id` vem do JWT, nao do cliente

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

## 2. Auth

### `POST /api/v1/auth/login`

Request:

```json
{
  "email": "admin@example.com",
  "password": "secret"
}
```

Response `200`:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "tenant_id": "uuid",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

## 3. Assets

### `GET /api/v1/assets`

Query params:

- `q`
- `asset_type`
- `status`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "TR-01",
      "asset_type": "transformer",
      "status": "active",
      "criticality": "high",
      "latest_health_score": 72.5
    }
  ],
  "total": 1
}
```

### `POST /api/v1/assets`

Request:

```json
{
  "external_ref": "SAP-TR-01",
  "name": "TR-01",
  "asset_type": "transformer",
  "substation_name": "SE Centro",
  "nominal_voltage_kv": 230,
  "criticality": "high",
  "status": "active"
}
```

Response `201`: ativo criado.

### `GET /api/v1/assets/{asset_id}`

Response `200`:

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "external_ref": "SAP-TR-01",
  "name": "TR-01",
  "asset_type": "transformer",
  "substation_name": "SE Centro",
  "nominal_voltage_kv": 230,
  "criticality": "high",
  "status": "active",
  "created_at": "2026-03-06T12:00:00Z",
  "updated_at": "2026-03-06T12:00:00Z"
}
```

### `GET /api/v1/assets/{asset_id}/measurements`

Query params:

- `measurement_type`
- `start`
- `end`
- `limit`

Response `200`:

```json
{
  "asset_id": "uuid",
  "items": [
    {
      "timestamp": "2026-03-06T12:00:00Z",
      "measurement_type": "temperature",
      "value": 81.2,
      "quality_flag": "good",
      "source": "api"
    }
  ]
}
```

### `GET /api/v1/assets/{asset_id}/health`

Response `200`:

```json
{
  "asset_id": "uuid",
  "current": {
    "score": 72.5,
    "band": "healthy",
    "calculated_at": "2026-03-06T12:00:00Z"
  },
  "history": [
    {
      "score": 75.0,
      "band": "healthy",
      "calculated_at": "2026-03-06T10:00:00Z"
    }
  ]
}
```

## 4. Alerts

### `GET /api/v1/alerts`

Query params:

- `status`
- `severity`
- `asset_id`
- `limit`
- `offset`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "asset_id": "uuid",
      "severity": "high",
      "status": "open",
      "alert_type": "threshold",
      "message": "Temperatura acima do limite",
      "created_at": "2026-03-06T12:00:00Z"
    }
  ],
  "total": 1
}
```

### `POST /api/v1/alerts/{alert_id}/ack`

Behavior:

- idempotente;
- muda `status` para `acknowledged` quando aplicável.

Response `200`:

```json
{
  "id": "uuid",
  "status": "acknowledged",
  "acknowledged_at": "2026-03-06T12:05:00Z"
}
```

## 5. Cases

### `GET /api/v1/cases`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "asset_id": "uuid",
      "alert_id": "uuid",
      "title": "Investigar TR-01",
      "status": "open",
      "priority": "high",
      "created_at": "2026-03-06T12:10:00Z"
    }
  ],
  "total": 1
}
```

### `POST /api/v1/cases`

Request:

```json
{
  "asset_id": "uuid",
  "alert_id": "uuid",
  "title": "Investigar aquecimento anormal",
  "priority": "high"
}
```

Response `201`: caso criado com `status=open`.

## 6. Ingestion

### `POST /api/v1/ingestion/jobs`

Suporta dois modos.

#### JSON batch

Request:

```json
{
  "source_type": "json_batch",
  "payload_format": "json",
  "records": [
    {
      "asset_id": "uuid",
      "measurement_type": "temperature",
      "value": 81.2,
      "timestamp": "2026-03-06T12:00:00Z",
      "quality_flag": "good",
      "source": "api"
    }
  ]
}
```

#### File upload

- `Content-Type: multipart/form-data`
- campos: `source_type=file_upload`, `payload_format=csv|xlsx`, `file`, `mapping` opcional

Response `202`:

```json
{
  "id": "uuid",
  "status": "completed",
  "records_received": 1,
  "records_accepted": 1,
  "records_rejected": 0
}
```

### `GET /api/v1/ingestion/jobs/{job_id}`

Response `200`:

```json
{
  "id": "uuid",
  "status": "completed",
  "source_type": "json_batch",
  "payload_format": "json",
  "records_received": 1,
  "records_accepted": 1,
  "records_rejected": 0,
  "error_summary": null,
  "created_at": "2026-03-06T12:00:00Z",
  "completed_at": "2026-03-06T12:00:01Z"
}
```

## 7. Graph

### `GET /api/v1/graph/assets/{asset_id}/neighbors`

Response `200`:

```json
{
  "asset_id": "uuid",
  "nodes": [
    { "id": "uuid", "type": "Asset", "name": "TR-01" },
    { "id": "uuid", "type": "Substation", "name": "SE Centro" }
  ],
  "edges": [
    { "source": "uuid", "target": "uuid", "type": "CONTAINS" }
  ]
}
```

### `GET /api/v1/graph/assets/{asset_id}/impact`

Response `200`:

```json
{
  "asset_id": "uuid",
  "impacted_assets": [
    { "id": "uuid", "name": "LT-230-01", "reason": "shared_substation" }
  ],
  "impacted_substations": [
    { "id": "uuid", "name": "SE Centro" }
  ]
}
```

## 8. Endpoint interno

### `GET /healthz`

Usado para health check de serviço. Nao faz parte do contrato de produto.

## 9. Fora do contrato v0.1

- GraphQL
- WebSocket
- Socket.io
- SMS/push
- forecasting
