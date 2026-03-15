# Modelo de Dados - OntoGrid Energy Data Hub MVP

Este documento define o modelo canonico do MVP publico com foco no produto atual: catalogo amplo, entidades canonicas, analysis e copilot grounded. Contratos HTTP pertencem a [API_SPEC.md](../contracts/API_SPEC.md).

## Regras gerais

- o nucleo publico nao usa `tenant_id` como chave central;
- IDs sao `UUID`;
- timestamps sao armazenados em UTC;
- o catalogo cobre os **345 datasets** inventariados;
- `publicado` e estado operacional do ambiente;
- o frontend nunca consome arquivo bruto diretamente.

## Nucleo do produto

### `source`

Representa a fonte publica principal, como `ANEEL`, `ONS` e `CCEE`.

### `dataset`

Representa um dataset catalogado no produto.

Campos minimos:

- `source_id`
- `code`
- `name`
- `domain`
- `granularity`
- `description`
- `schema_summary`
- `refresh_frequency`
- `latest_version_id`

### `dataset_version`

Representa uma publicacao logica de um dataset.

Campos minimos:

- `dataset_id`
- `label`
- `extracted_at`
- `published_at`
- `coverage_start`
- `coverage_end`
- `row_count`
- `schema_version`
- `checksum`
- `status`
- `lineage`

Regra importante:

- um `dataset_version` pode ser formado por **multiplos arquivos de origem**.

### `dataset_artifact` (conceito arquitetural do MVP)

Representa cada arquivo original associado a uma `dataset_version`.

Campos conceituais minimos:

- `dataset_version_id`
- `artifact_uri`
- `format`
- `checksum`
- `size_bytes`
- `partition_key`
- `schema_json`

Regra:

- o arquivo original fica no backend/storage;
- o frontend nunca consulta `dataset_artifact` diretamente.

### `refresh_job`

Representa cada tentativa de refresh/publicacao.

Campos minimos:

- `dataset_id`
- `source_type`
- `trigger_type`
- `status`
- `rows_read`
- `rows_written`
- `error_summary`
- `started_at`
- `finished_at`

## Eixo canonico de entidades

### `entity`

Entidade publica canonica reutilizada em varios datasets.

Exemplos de tipos relevantes para o MVP:

- `agent`
- `distributor`
- `plant`
- `submarket`
- `municipality`
- `subsystem`
- `reservoir`

### `entity_alias`

Liga nomes e codigos da origem a uma entidade canonica.

### `relation`

Relaciona entidades de modo rastreavel por `dataset_version`.

## Camada curada para Analysis e Copilot

### `metric_series`

Define a serie consultavel pelo produto.

### `observation`

Guarda os pontos da serie temporal ou observacional.

Regra:

- `Analysis`, `Entities` e `Copilot` consultam `metric_series` + `observation`, nao o arquivo bruto.

## Status oficiais de cobertura

Taxonomia de leitura do produto:

- `inventariado`: apareceu no levantamento da fonte;
- `catalogado`: entrou no catalogo do app/repo;
- `adapter_pronto`: ja possui adapter implementado no repo;
- `publicado`: ja possui versao publicada em um ambiente operacional.

## Regra sobre ambientes

- o repo pode catalogar 345 datasets sem exigir 345 datasets publicados localmente;
- o ambiente local deve privilegiar `catalog` ou `sample`;
- a publicacao de datasets reais pesados deve ficar em ambiente compartilhado ou em execucao explicitamente selecionada.
