# Pipeline de Ingestao - OntoGrid Energy Data Hub MVP

Este documento descreve a ingestao suportada no MVP publico.

## 1. Escopo suportado

### Entrada

- pulls agendados em APIs publicas;
- downloads versionados de arquivos publicos;
- crawlers especificos quando a fonte nao expuser API consistente.

### Formatos

- JSON
- CSV
- XLSX
- ZIP

### Fontes consideradas

- ONS Dados Abertos e distribuicoes publicas equivalentes;
- ANEEL em bases regulatorias e cadastrais priorizadas;
- CCEE em datasets publicos de mercado.

## 2. O que fica para depois

- upload manual de arquivo do cliente;
- lote JSON do cliente por API;
- OPC-UA em tempo real;
- conectores privados para SCADA, ERP, OMS, CMMS e GIS;
- reprocessamento historico massivo multi-tenant.

## 3. Fluxo do refresh

1. Scheduler ou operacao interna dispara refresh.
2. Backend registra `refresh_job`.
3. O artefato bruto e baixado ou consultado na origem.
4. O parser valida schema, checksum e cobertura temporal.
5. O dado e normalizado para `dataset_version`, `metric_series`, `observation`, `entity` e `relation`.
6. O grafo publico e os snapshots de insight sao atualizados quando aplicavel.
7. O job e marcado como `published`, `failed` ou `partial`.

## 4. Contrato interno do job

Campos esperados:

- `dataset_id`
- `source_type=api_pull|scheduled_download|crawler`
- `trigger_type=schedule|manual`
- `force` opcional

## 5. Regras de validacao

- todo refresh precisa apontar para `source`, `dataset` e `dataset_version`;
- artefato bruto e imutavel depois do download;
- timestamps externos sao normalizados para UTC;
- parser registra `schema_version` e `checksum`;
- falha nunca apaga a ultima versao valida publicada;
- lineage minimo precisa permitir rastrear dataset, versao e refresh.

## 6. Saidas do pipeline

- linhas em `dataset_version`;
- contadores e status em `refresh_job`;
- entidades e relacoes canonicas para o grafo;
- series e observacoes prontas para consulta;
- snapshots de insight prontos para UI.

## 7. Observabilidade minima

- tempo total do refresh;
- tamanho e hash do artefato bruto;
- linhas lidas, aceitas e descartadas;
- ultima versao valida por dataset;
- resumo de erros de parse e normalizacao;
- logs com `source_code`, `dataset_code`, `version_id` e `refresh_job_id`.

## 8. Regra de escopo

No MVP publico, ingestao existe para materializar o hub regulatorio. Fluxos de upload e integração do cliente entram apenas na fase enterprise.
