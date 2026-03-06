# Pipeline de Ingestão - OntoGrid MVP v0.1

Este documento descreve apenas a ingestão suportada no primeiro corte.

## 1. Escopo suportado

### Entrada

- Upload de arquivo via multipart.
- Lote JSON via API.

### Formatos

- CSV
- XLSX
- JSON

### Fontes consideradas

- Export de historian/SCADA.
- Planilha operacional.
- Integração backend-to-backend simples.

## 2. O que fica para depois

- OPC-UA em tempo real.
- Crawlers ONS/ANEEL.
- Redis Streams como backbone da ingestão.
- DLQ e retry orchestration completos.
- Reprocessamento histórico massivo.

## 3. Fluxo do job

1. Cliente chama `POST /api/v1/ingestion/jobs`.
2. Backend registra `ingestion_job`.
3. Payload e validado.
4. Registros válidos são normalizados.
5. Medicoes sao persistidas em `measurement`.
6. Job e marcado como `completed` ou `failed`.

## 4. Contrato de entrada

### 4.1 Upload de arquivo

Campos esperados:

- `source_type=file_upload`
- `payload_format=csv|xlsx`
- `file`
- `mapping` opcional em JSON string

### 4.2 Lote JSON

Campos esperados:

- `source_type=json_batch`
- `payload_format=json`
- `records`

### Registro normalizado

```json
{
  "asset_id": "uuid",
  "measurement_type": "temperature",
  "value": 82.4,
  "timestamp": "2026-03-06T11:00:00Z",
  "quality_flag": "good",
  "source": "api"
}
```

## 5. Regras de validação

- `tenant_id` sempre derivado do token autenticado.
- `asset_id` precisa existir dentro do tenant.
- `timestamp` precisa conter timezone ou ser normalizado para UTC.
- `measurement_type` deve pertencer ao catálogo aceito.
- `value` deve ser numérico.
- duplicatas pela chave lógica do modelo devem ser ignoradas ou sobrescritas de forma idempotente.

## 6. Normalização mínima

- conversão para UTC;
- padronização de `measurement_type`;
- padronização de `quality_flag`;
- preenchimento de `source`;
- associação ao `ingestion_job_id`.

## 7. Saídas do pipeline

- linhas em `measurement`;
- atualização de contadores do `ingestion_job`;
- insumo para recalcular health score do ativo.

## 8. Observabilidade mínima

- contagem de registros recebidos, aceitos e rejeitados;
- tempo total do job;
- resumo de erros de validação;
- logs com `tenant_id`, `job_id` e `source_type`.
