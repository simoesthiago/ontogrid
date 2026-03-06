# Pipeline de Ingestao de Dados - OntoGrid MVP

## 1. Visao Geral do Pipeline

O pipeline de ingestao de dados do OntoGrid MVP (Asset Health) e responsavel por coletar, validar, transformar e armazenar dados operacionais de equipamentos criticos do setor eletrico brasileiro. O pipeline alimenta o Energy Graph (Neo4j) e o banco de series temporais (TimescaleDB) para viabilizar a vigilancia inteligente de ativos.

### 1.1 Diagrama do Fluxo de Dados

```
+-------------------+     +-------------------+     +-------------------+
|   FONTES DE DADOS |     |   CONECTORES      |     |   VALIDACAO       |
|                   |     |                   |     |                   |
| SCADA/Historian --+---->| Conector OPC-UA   +---->| Pydantic Schemas  |
| (OPC-UA, REST)    |     | (Celery Worker)   |     | Range checks      |
|                   |     |                   |     | Duplicata detect  |
| CSV/Excel --------+---->| Conector Batch    +---->| Timestamp valid   |
| (Upload API)      |     | (Celery Task)     |     | Quality flags     |
|                   |     |                   |     |                   |
| CMMS (SAP/Maximo)-+---->| Conector Batch    +---->| Schema validation |
| (API/CSV)         |     | (Celery Task)     |     | Referential check |
|                   |     |                   |     |                   |
| ONS/ANEEL --------+---->| Crawler           +---->| Version control   |
| (Dados Abertos)   |     | (Celery Beat)     |     | Retificacao detect|
+-------------------+     +-------------------+     +--------+----------+
                                                              |
                                                              v
+-------------------+     +-------------------+     +-------------------+
|   STORAGE         |     |   TRANSFORMACAO   |     |   BUFFER          |
|                   |     |                   |     |                   |
| TimescaleDB ------+<----+ Normalizacao      +<----+ Redis Streams     |
|  (Series Tempor.) |     |  temporal (UTC)   |     |  (Buffer ingestao)|
|                   |     |                   |     |                   |
| Neo4j ------------+<----+ Enriquecimento    |     | Redis Cache       |
|  (Energy Graph)   |     |  (metadata, graph)|     |  (Ultimo valor)   |
|                   |     |                   |     |                   |
| Redis Cache ------+<----+ Quality scoring   |     |                   |
|  (Ultimo valor)   |     |  (0=bom,2=ruim)   |     |                   |
+-------------------+     +-------------------+     +-------------------+
```

### 1.2 Fluxo Simplificado

```
Fonte --> Conector --> Redis Buffer --> Validacao --> Transformacao --> Storage
                          |                              |
                          v                              v
                    Metricas/Logs               Quality Flags
                    (Prometheus)                (por medicao)
```

### 1.3 Principios Arquiteturais

| Principio | Descricao | Implementacao |
|---|---|---|
| **Idempotencia** | Re-processar dados nao deve gerar duplicatas nem efeitos colaterais | Chave unica (asset_id + measurement_type + timestamp); upsert em todas as operacoes de escrita |
| **Observabilidade** | Todo ponto do pipeline emite metricas e logs estruturados | Prometheus counters/histograms em cada estagio; structured logging com correlation_id |
| **Contratos de dados** | Cada fonte tem um schema formal que define estrutura, tipos e ranges validos | Pydantic models versionados; schemas YAML para validacao; rejeicao explicita de dados invalidos |
| **Versionamento** | Mudancas em schemas e transformacoes sao rastreadas | Alembic para TimescaleDB; schema versioning em Neo4j; changelog de contratos |
| **Desacoplamento** | Cada estagio opera independentemente e se comunica via filas | Redis Streams entre conectores e processamento; Celery tasks para processamento assincrono |
| **Backpressure** | Pipeline respeita limites de capacidade sem perder dados | Redis buffer com tamanho maximo; circuit breaker em conectores; dead letter queue |

---

## 2. Fontes de Dados do MVP

### 2.1 SCADA / Historian (Prioridade 1)

O SCADA (Supervisory Control and Data Acquisition) e a fonte primaria de dados operacionais em tempo real. Os dados podem vir de historians (PI, eDNA, etc) ou diretamente de servidores OPC-UA.

#### Protocolos Suportados

| Protocolo | Caso de Uso | Latencia | Observacao |
|---|---|---|---|
| **OPC-UA** | Conexao direta com SCADA/historian | < 5s | Protocolo padrao IEC 62541; requer configuracao de endpoint e certificados |
| **CSV/Batch** | Exportacao periodica do historian | Minutos a horas | Para clientes sem acesso OPC-UA direto; parsing configuravel |
| **API REST** | Historians com API moderna (OSIsoft PI Web API, etc) | < 30s | Polling periodico com cursor de paginacao |

#### Parametros Monitorados por Tipo de Ativo

**Transformadores de Potencia (>100 MVA)**

| Parametro | Unidade | Range Normal | Frequencia | Criticidade |
|---|---|---|---|---|
| Temperatura do oleo (topo) | Celsius | 40-85 | 1 min | Alta |
| Temperatura do oleo (fundo) | Celsius | 30-65 | 1 min | Alta |
| Temperatura do enrolamento (hot spot) | Celsius | 50-110 | 1 min | Critica |
| Nivel de oleo | % | 85-100 | 5 min | Alta |
| Gases dissolvidos - Hidrogenio (H2) | ppm | 0-100 | 15 min* | Critica |
| Gases dissolvidos - Metano (CH4) | ppm | 0-120 | 15 min* | Critica |
| Gases dissolvidos - Etileno (C2H4) | ppm | 0-50 | 15 min* | Critica |
| Gases dissolvidos - Acetileno (C2H2) | ppm | 0-1 | 15 min* | Critica |
| Gases dissolvidos - CO | ppm | 0-350 | 15 min* | Alta |
| Gases dissolvidos - CO2 | ppm | 0-2500 | 15 min* | Media |
| Corrente (por fase) | A | 0-corrente_nominal | 1 s | Alta |
| Tensao (por fase) | kV | tensao_nominal +/- 5% | 1 s | Alta |
| Fator de potencia | - | 0.85-1.0 | 1 min | Media |
| Umidade do oleo | ppm | 0-25 | 15 min | Media |
| Potencia ativa | MW | 0-potencia_nominal | 1 s | Media |
| Potencia reativa | MVAr | - | 1 s | Media |

*DGA online via sensor (ex: Kelman, Serveron); se laboratorio, frequencia mensal/trimestral via CSV.

**Geradores (Hidraulicos e Termicos)**

| Parametro | Unidade | Range Normal | Frequencia | Criticidade |
|---|---|---|---|---|
| Vibracao radial do mancal guia | mm/s | 0-4.5 | 1 s | Critica |
| Vibracao axial do mancal escora | mm/s | 0-7.1 | 1 s | Critica |
| Temperatura mancal guia superior | Celsius | 40-75 | 1 min | Alta |
| Temperatura mancal guia inferior | Celsius | 40-75 | 1 min | Alta |
| Temperatura mancal escora | Celsius | 40-80 | 1 min | Critica |
| Temperatura estator (por zona) | Celsius | 50-105 | 1 min | Alta |
| Corrente de excitacao | A | Variavel | 1 s | Alta |
| Tensao de excitacao | V | Variavel | 1 s | Media |
| Velocidade | RPM | Velocidade sincrona +/- 0.5% | 1 s | Alta |
| Potencia ativa | MW | 0-potencia_nominal | 1 s | Media |
| Descargas parciais | pC | 0-500 | 5 min | Alta |

**Disjuntores de AT/EAT**

| Parametro | Unidade | Range Normal | Frequencia | Criticidade |
|---|---|---|---|---|
| Numero de operacoes acumuladas | contagem | 0-10000 | Por evento | Alta |
| Tempo de abertura | ms | Conforme fabricante | Por evento | Critica |
| Tempo de fechamento | ms | Conforme fabricante | Por evento | Critica |
| Resistencia de contato | micro-ohm | Conforme fabricante | Mensal (batch) | Alta |
| Pressao do SF6 | bar | 5.5-7.0 | 5 min | Critica |
| Corrente de interrup. acumulada | kA*ops | 0-limite_vida_util | Por evento | Alta |
| Temperatura do gabinete | Celsius | -10-55 | 15 min | Baixa |
| Nivel de oleo (disjuntores a oleo) | % | 90-100 | 15 min | Alta |

#### Volume e Throughput Estimado

| Metrica | Valor |
|---|---|
| Pontos/dia por subestacao (estimativa) | ~1.000.000 |
| Measurement points por ativo (media) | 15-25 |
| Bytes por data point (comprimido) | ~50-80 bytes |
| Volume diario por subestacao (raw) | ~50-80 MB |
| Ativos por subestacao (media) | 10-30 |
| Subestacoes no MVP | 3-10 |
| Throughput target (ingestao) | 10.000 pontos/segundo |

### 2.2 Cadastro de Ativos (Prioridade 1)

O cadastro de ativos estabelece a identidade dos equipamentos no Energy Graph e serve como referencia para todas as operacoes de enriquecimento e contextualizacao.

#### Fontes

| Fonte | Protocolo | Frequencia |
|---|---|---|
| Sistema ERP/EAM (SAP PM, Maximo, Oracle EAM) | API REST ou export CSV | Semanal ou sob demanda |
| Planilha Excel do cliente | Upload via UI | Sob demanda (onboarding) |
| Ficha tecnica do fabricante | Upload PDF/CSV | Sob demanda |

#### Dados Capturados

| Campo | Tipo | Obrigatorio | Exemplo |
|---|---|---|---|
| asset_id | string | Sim | "TR-SE-XINGU-01" |
| asset_name | string | Sim | "Transformador de Potencia 01" |
| asset_type | enum | Sim | "power_transformer" |
| manufacturer | string | Sim | "WEG" |
| model | string | Nao | "UTL 500/230 kV - 750 MVA" |
| serial_number | string | Nao | "WEG-2015-12345" |
| year_manufactured | int | Sim | 2015 |
| year_commissioned | int | Sim | 2016 |
| rated_power_mva | float | Sim* | 750.0 |
| rated_voltage_primary_kv | float | Sim* | 500.0 |
| rated_voltage_secondary_kv | float | Sim* | 230.0 |
| substation_id | string | Sim | "SE-XINGU" |
| substation_name | string | Sim | "SE Xingu 500kV" |
| company_id | string | Sim | "ELETRONORTE" |
| region | string | Sim | "Norte" |
| latitude | float | Nao | -3.2167 |
| longitude | float | Nao | -51.9833 |
| operating_status | enum | Sim | "operational" |
| maintenance_class | enum | Nao | "A" (critico) |

*Campos especificos por tipo de ativo.

#### Mapeamento para Energy Graph (Neo4j)

```
Upload CSV/API --> Pydantic Validation --> Field Mapping --> Neo4j Merge

Nos criados/atualizados:
  (:Company {id, name})
  (:Region {id, name})
  (:Substation {id, name, lat, lon})
  (:Asset {id, name, type, manufacturer, year, ...})
  (:AssetType {id, name, parameters})

Relacoes criadas:
  (Company)-[:OWNS]->(Region)
  (Region)-[:CONTAINS]->(Substation)
  (Substation)-[:CONTAINS]->(Asset)
  (Asset)-[:IS_TYPE]->(AssetType)
```

### 2.3 Historico de Manutencao (Prioridade 2)

O historico de manutencao alimenta o calculo do Health Score (componente de idade e historico) e permite correlacionar intervencoes com mudancas nos parametros operacionais.

#### Fontes

| Fonte | Protocolo | Frequencia |
|---|---|---|
| CMMS (SAP PM, Maximo, Oracle EAM) | API REST ou export CSV | Batch diario |
| Planilha do cliente | Upload via UI | Sob demanda |

#### Dados Capturados

| Campo | Tipo | Obrigatorio | Exemplo |
|---|---|---|---|
| work_order_id | string | Sim | "OS-2024-001234" |
| asset_id | string | Sim | "TR-SE-XINGU-01" |
| work_order_type | enum | Sim | "corrective" / "preventive" / "predictive" |
| description | string | Sim | "Substituicao de buchas de AT" |
| start_date | datetime | Sim | "2024-06-15T08:00:00-03:00" |
| end_date | datetime | Nao | "2024-06-18T17:00:00-03:00" |
| failure_code | string | Nao | "BUCHA_VAZAMENTO" |
| component_replaced | string | Nao | "Bucha AT fase A" |
| cost_brl | float | Nao | 450000.00 |
| technician | string | Nao | "Joao Silva" |
| priority | enum | Sim | "high" |
| status | enum | Sim | "completed" |
| downtime_hours | float | Nao | 72.0 |
| root_cause | string | Nao | "Envelhecimento do isolamento" |

### 2.4 Dados Publicos ONS/ANEEL (Prioridade 2)

Dados abertos complementam a visao operacional com informacoes de indisponibilidade, geracao e cadastro regulatorio.

#### ONS Dados Abertos

| Dataset | URL Base | Frequencia de Atualizacao | Dados |
|---|---|---|---|
| Indisponibilidades Programadas | dados.ons.org.br | Diaria | Programacoes de desligamento de equipamentos |
| Indisponibilidades Forcadas | dados.ons.org.br | Diaria | Desligamentos nao programados (falhas) |
| Geracao por Usina | dados.ons.org.br | Horaria | Geracao em MW por usina |
| Capacidade Instalada | dados.ons.org.br | Mensal | Capacidade por empreendimento |
| Balanco de Energia | dados.ons.org.br | Diaria | Balanco de energia por subsistema |

#### ANEEL SIGA

| Dataset | URL Base | Frequencia de Atualizacao | Dados |
|---|---|---|---|
| Cadastro de Empreendimentos | sigel.aneel.gov.br | Semanal | Nome, tipo, potencia, localizacao, proprietario |
| Outorgas e Autorizacoes | aneel.gov.br | Mensal | Status regulatorio |
| Indicadores de Qualidade (DEC/FEC) | aneel.gov.br | Mensal | Indicadores de continuidade |

#### Crawler: Consideracoes

- Respeitar robots.txt e rate limits dos portais
- Controle de versao de datasets (ONS pode retificar dados de dias anteriores)
- Armazenar tanto raw (arquivo original) quanto parsed (dados estruturados)
- Alertar quando formato do dataset mudar (quebra de schema)
- Fallback para download manual com upload via UI

---

## 3. Arquitetura do Pipeline

### 3.1 Conector SCADA (Real-time)

O conector SCADA e implementado como um Celery worker de longa duracao que mantem conexao persistente com servidores OPC-UA e faz polling de APIs REST.

#### Fluxo

```
Servidor OPC-UA                    OntoGrid
+-------------------+        +----------------------------+
|                   |        |                            |
| Tags configurados +------->+ Celery Worker (OPC-UA)     |
| (subscricao)      | OPC-UA |  - Le valores por tag      |
|                   |        |  - Empacota em batch        |
+-------------------+        |  - Envia para Redis Stream  |
                             +-------------+--------------+
                                           |
                             +-------------v--------------+
                             | Redis Stream               |
                             | (scada:ingest:{tenant_id}) |
                             | Buffer temporario           |
                             | Max size: 100K mensagens    |
                             +-------------+--------------+
                                           |
                             +-------------v--------------+
                             | Celery Worker (Processor)   |
                             |  - Consome batch do Redis   |
                             |  - Valida (Pydantic)        |
                             |  - Aplica quality flags     |
                             |  - Normaliza timestamp      |
                             |  - COPY para TimescaleDB    |
                             |  - Atualiza Redis cache     |
                             +----------------------------+
```

#### Configuracao do Worker OPC-UA

```python
# Exemplo de configuracao por conexao SCADA
{
    "connection_id": "se-xingu-historian",
    "tenant_id": "eletronorte",
    "protocol": "opc-ua",
    "endpoint": "opc.tcp://historian.se-xingu.local:4840",
    "security_mode": "SignAndEncrypt",
    "certificate_path": "/certs/ontogrid-client.pem",
    "tags": [
        {
            "tag_id": "TR01.OIL_TEMP_TOP",
            "asset_id": "TR-SE-XINGU-01",
            "measurement_type": "oil_temperature_top",
            "unit": "celsius",
            "sampling_interval_ms": 60000,
            "valid_range": {"min": -10, "max": 150}
        },
        {
            "tag_id": "TR01.WINDING_TEMP",
            "asset_id": "TR-SE-XINGU-01",
            "measurement_type": "winding_temperature_hotspot",
            "unit": "celsius",
            "sampling_interval_ms": 60000,
            "valid_range": {"min": -10, "max": 200}
        }
    ],
    "batch_size": 500,
    "flush_interval_seconds": 5,
    "reconnect_interval_seconds": 30,
    "max_retries": 10
}
```

#### Otimizacao de Escrita (COPY para TimescaleDB)

```python
# Estrategia de batch insert usando COPY
# Em vez de INSERT individual, acumular pontos e fazer COPY bulk

async def flush_to_timescaledb(batch: list[DataPoint]):
    """
    Flush batch de data points para TimescaleDB via COPY.
    Throughput: ~50K pontos/segundo por worker.
    """
    buffer = StringIO()
    writer = csv.writer(buffer, delimiter='\t')
    for point in batch:
        writer.writerow([
            point.timestamp,        # timestamptz
            point.tenant_id,        # text
            point.asset_id,         # text
            point.measurement_type, # text
            point.value,            # double precision
            point.quality_flag,     # smallint
            point.source_id,        # text
        ])

    buffer.seek(0)
    async with db_pool.acquire() as conn:
        await conn.copy_to_table(
            'measurements',
            source=buffer,
            columns=['time', 'tenant_id', 'asset_id', 'measurement_type',
                     'value', 'quality_flag', 'source_id']
        )
```

#### Tolerancia a Falhas

| Cenario | Comportamento |
|---|---|
| Servidor OPC-UA indisponivel | Retry com backoff exponencial (30s, 60s, 120s, ...); alerta apos 5 min sem conexao |
| Redis indisponivel | Buffer local em memoria (max 10K pontos); alerta imediato |
| TimescaleDB indisponivel | Dados permanecem no Redis Stream; retry automatico; alerta apos 2 min |
| Dados duplicados | Upsert com ON CONFLICT (time, asset_id, measurement_type) DO NOTHING |
| Worker crash | Celery restart automatico; Redis Stream garante que mensagens nao processadas sao re-consumidas |

### 3.2 Conector Batch (CSV/API)

O conector batch processa uploads de arquivos CSV/Excel e chamadas de API de sistemas legados.

#### Fluxo

```
+-------------------+     +-------------------+     +-------------------+
| Upload API        |     | Celery Task       |     | Storage           |
| POST /api/v1/     |     |                   |     |                   |
|   ingest/upload   +---->+ parse_and_ingest  +---->+ TimescaleDB       |
|                   |     |   - Parse CSV     |     | Neo4j             |
| Headers:          |     |   - Map columns   |     | Redis             |
|   tenant_id       |     |   - Validate      |     |                   |
|   data_source     |     |   - Transform     |     | + Upload Result   |
|   file_type       |     |   - Batch insert  |     |   (status, erros) |
+-------------------+     +-------------------+     +-------------------+
```

#### API Endpoint

```
POST /api/v1/ingest/upload
Content-Type: multipart/form-data

Headers:
  Authorization: Bearer <jwt_token>

Body:
  file: <arquivo CSV/Excel>
  data_source: "scada_export" | "asset_catalog" | "maintenance_history"
  column_mapping: {
    "Timestamp": "timestamp",
    "Tag Name": "measurement_type",
    "Value": "value",
    "Quality": "quality_flag"
  }  # opcional - usa mapeamento padrao se omitido

Response (202 Accepted):
  {
    "task_id": "abc123",
    "status": "processing",
    "status_url": "/api/v1/ingest/upload/abc123/status"
  }
```

#### Validacao com Pydantic

```python
from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum

class DataSourceType(str, Enum):
    SCADA_EXPORT = "scada_export"
    ASSET_CATALOG = "asset_catalog"
    MAINTENANCE_HISTORY = "maintenance_history"

class ScadaDataPoint(BaseModel):
    timestamp: datetime
    asset_id: str
    measurement_type: str
    value: float
    quality_flag: int = 0
    source_id: str | None = None

    @field_validator('timestamp')
    @classmethod
    def timestamp_not_future(cls, v):
        if v > datetime.now(v.tzinfo):
            raise ValueError('Timestamp nao pode estar no futuro')
        return v

    @field_validator('quality_flag')
    @classmethod
    def valid_quality_flag(cls, v):
        if v not in (0, 1, 2):
            raise ValueError('Quality flag deve ser 0 (bom), 1 (suspeito), ou 2 (ruim)')
        return v

class AssetRecord(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    manufacturer: str
    year_manufactured: int
    year_commissioned: int
    substation_id: str
    substation_name: str
    company_id: str
    region: str
    operating_status: str = "operational"
    rated_power_mva: float | None = None
    rated_voltage_primary_kv: float | None = None
    latitude: float | None = None
    longitude: float | None = None

    @field_validator('year_manufactured')
    @classmethod
    def valid_year(cls, v):
        if v < 1950 or v > datetime.now().year:
            raise ValueError(f'Ano de fabricacao invalido: {v}')
        return v
```

#### Resultado do Processamento

```json
{
    "task_id": "abc123",
    "status": "completed",
    "summary": {
        "total_rows": 86400,
        "rows_accepted": 86102,
        "rows_rejected": 298,
        "processing_time_seconds": 12.5,
        "data_source": "scada_export",
        "time_range": {
            "start": "2024-06-01T00:00:00Z",
            "end": "2024-06-01T23:59:59Z"
        }
    },
    "errors": [
        {
            "row": 1523,
            "field": "value",
            "error": "Valor fora do range valido (-10 a 150): 9999.0",
            "data": {"timestamp": "2024-06-01T04:15:00Z", "value": 9999.0}
        }
    ],
    "quality_report": {
        "completeness": 0.997,
        "validity": 0.997,
        "overall_score": 0.994
    }
}
```

### 3.3 Conector ONS/ANEEL (Crawler)

O crawler e implementado como tarefas Celery Beat agendadas que baixam, parseiam e ingerem dados de portais publicos.

#### Agendamento (Celery Beat)

```python
# celery_config.py
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'crawl-ons-indisponibilidades': {
        'task': 'ontogrid.ingest.crawlers.ons.crawl_indisponibilidades',
        'schedule': crontab(hour=6, minute=0),  # Diario as 06:00 UTC
        'kwargs': {'datasets': ['programadas', 'forcadas']},
    },
    'crawl-ons-geracao': {
        'task': 'ontogrid.ingest.crawlers.ons.crawl_geracao',
        'schedule': crontab(hour='*/4', minute=30),  # A cada 4 horas
    },
    'crawl-aneel-siga': {
        'task': 'ontogrid.ingest.crawlers.aneel.crawl_siga',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Segunda as 03:00
    },
    'crawl-aneel-indicadores': {
        'task': 'ontogrid.ingest.crawlers.aneel.crawl_indicadores',
        'schedule': crontab(hour=4, minute=0, day_of_month=5),  # Dia 5 de cada mes
    },
}
```

#### Controle de Versao de Datasets

O ONS pode retificar dados de dias anteriores. O crawler detecta retificacoes comparando checksums.

```python
class DatasetVersion(BaseModel):
    """Controle de versao de datasets publicos."""
    dataset_id: str           # ex: "ons_indisponibilidades_forcadas"
    reference_date: date      # data de referencia do dataset
    version: int              # incrementado a cada retificacao detectada
    checksum_sha256: str      # hash do conteudo
    downloaded_at: datetime
    file_path: str            # caminho do arquivo raw
    record_count: int
    is_latest: bool           # True para a versao mais recente
```

#### Estrategia de Parse

```
Download (requests) --> Salvar raw (S3/local) --> Parse (pandas) -->
  Validar schema --> Detectar retificacao --> Upsert no TimescaleDB
```

---

## 4. Contratos de Dados

### 4.1 Definicao

Um contrato de dados define a interface formal entre uma fonte de dados e o pipeline de ingestao. Ele especifica:

- **Schema**: campos esperados, tipos de dados e formato
- **Regras de validacao**: ranges validos, obrigatoriedade, unicidade
- **Tratamento de erros**: como lidar com dados ausentes ou invalidos
- **SLA**: frequencia esperada, latencia maxima, volume minimo

### 4.2 Contrato: Telemetria SCADA

```yaml
# contracts/scada_telemetry_v1.yaml
contract:
  name: "SCADA Telemetry"
  version: "1.0.0"
  description: "Contrato para dados de telemetria SCADA (series temporais)"
  owner: "ontogrid-data-engineering"

schema:
  fields:
    - name: timestamp
      type: timestamptz
      required: true
      description: "Momento da medicao (UTC ou com timezone)"
      validation:
        - not_null: true
        - not_future: true
        - max_age_days: 365  # Rejeitar dados com mais de 1 ano

    - name: tenant_id
      type: string
      required: true
      description: "Identificador do tenant (empresa)"
      validation:
        - not_null: true
        - max_length: 50

    - name: asset_id
      type: string
      required: true
      description: "Identificador unico do ativo"
      validation:
        - not_null: true
        - exists_in: "neo4j:Asset.id"  # Referential integrity
        - max_length: 100

    - name: measurement_type
      type: string
      required: true
      description: "Tipo da medicao (padronizado)"
      validation:
        - not_null: true
        - one_of:
          - oil_temperature_top
          - oil_temperature_bottom
          - winding_temperature_hotspot
          - oil_level
          - dga_hydrogen
          - dga_methane
          - dga_ethylene
          - dga_acetylene
          - dga_co
          - dga_co2
          - current_phase_a
          - current_phase_b
          - current_phase_c
          - voltage_phase_a
          - voltage_phase_b
          - voltage_phase_c
          - power_factor
          - active_power
          - reactive_power
          - vibration_radial
          - vibration_axial
          - bearing_temperature
          - stator_temperature
          - excitation_current
          - speed_rpm
          - sf6_pressure
          - breaker_operations_count
          - breaker_opening_time
          - breaker_closing_time
          - contact_resistance

    - name: value
      type: float64
      required: true
      description: "Valor numerico da medicao"
      validation:
        - not_null: true
        - range_by_type:  # Range depende do measurement_type
            oil_temperature_top: { min: -40, max: 200 }
            oil_temperature_bottom: { min: -40, max: 150 }
            winding_temperature_hotspot: { min: -40, max: 300 }
            oil_level: { min: 0, max: 110 }
            dga_hydrogen: { min: 0, max: 50000 }
            dga_acetylene: { min: 0, max: 5000 }
            sf6_pressure: { min: 0, max: 15 }
            speed_rpm: { min: 0, max: 5000 }

    - name: quality_flag
      type: int
      required: false
      default: 0
      description: "Flag de qualidade: 0=bom, 1=suspeito, 2=ruim"
      validation:
        - one_of: [0, 1, 2]

    - name: source_id
      type: string
      required: false
      description: "Identificador da fonte (ex: tag OPC-UA, nome do arquivo)"
      validation:
        - max_length: 200

unique_key: [timestamp, tenant_id, asset_id, measurement_type]

sla:
  max_latency_seconds: 30       # Fonte -> Storage
  min_frequency_seconds: 1      # Frequencia minima (1 dado/segundo)
  max_gap_minutes: 15           # Alertar se gap > 15 min
  min_daily_completeness: 0.95  # 95% dos pontos esperados

error_handling:
  null_value: reject_row
  out_of_range: set_quality_flag_1  # Marcar como suspeito
  duplicate: ignore                  # Idempotencia
  invalid_type: reject_row
  unknown_asset: reject_and_alert    # Ativo nao existe no Graph
  future_timestamp: reject_row
  rejected_rows: store_in_dead_letter_queue
```

### 4.3 Contrato: Cadastro de Ativos

```yaml
# contracts/asset_catalog_v1.yaml
contract:
  name: "Asset Catalog"
  version: "1.0.0"
  description: "Contrato para cadastro de ativos"

schema:
  fields:
    - name: asset_id
      type: string
      required: true
      validation:
        - not_null: true
        - unique: true
        - pattern: "^[A-Z0-9\\-]+$"
        - max_length: 100

    - name: asset_name
      type: string
      required: true

    - name: asset_type
      type: string
      required: true
      validation:
        - one_of:
          - power_transformer
          - distribution_transformer
          - circuit_breaker
          - generator_hydro
          - generator_thermal
          - reactor
          - compensator
          - disconnect_switch
          - surge_arrester
          - current_transformer
          - voltage_transformer

    - name: manufacturer
      type: string
      required: true

    - name: year_manufactured
      type: integer
      required: true
      validation:
        - range: { min: 1950, max: 2030 }

    - name: year_commissioned
      type: integer
      required: true
      validation:
        - gte_field: year_manufactured

    - name: substation_id
      type: string
      required: true

    - name: company_id
      type: string
      required: true

    - name: operating_status
      type: string
      required: true
      validation:
        - one_of: [operational, standby, maintenance, decommissioned]

unique_key: [asset_id]

error_handling:
  duplicate_asset_id: upsert  # Atualizar se ja existir
  missing_required: reject_row
  invalid_type: reject_and_alert
```

### 4.4 Contrato: Historico de Manutencao

```yaml
# contracts/maintenance_history_v1.yaml
contract:
  name: "Maintenance History"
  version: "1.0.0"
  description: "Contrato para historico de manutencao"

schema:
  fields:
    - name: work_order_id
      type: string
      required: true
      validation:
        - unique: true

    - name: asset_id
      type: string
      required: true
      validation:
        - exists_in: "neo4j:Asset.id"

    - name: work_order_type
      type: string
      required: true
      validation:
        - one_of: [corrective, preventive, predictive, emergency]

    - name: description
      type: string
      required: true
      validation:
        - max_length: 2000

    - name: start_date
      type: timestamptz
      required: true

    - name: end_date
      type: timestamptz
      required: false
      validation:
        - gte_field: start_date

    - name: priority
      type: string
      required: true
      validation:
        - one_of: [low, medium, high, critical]

    - name: status
      type: string
      required: true
      validation:
        - one_of: [open, in_progress, completed, cancelled]

    - name: cost_brl
      type: float
      required: false
      validation:
        - range: { min: 0, max: 100000000 }

unique_key: [work_order_id]

error_handling:
  duplicate_work_order: upsert
  unknown_asset: reject_and_alert
  missing_required: reject_row
```

---

## 5. Transformacoes

### 5.1 Normalizacao Temporal

#### Problema

Dados de diferentes fontes usam referencias temporais distintas:

| Fonte | Referencia Temporal | Formato Tipico |
|---|---|---|
| SCADA/OPC-UA | Hora local ou UTC | ISO 8601 com timezone |
| CSV export | Hora local sem timezone | "DD/MM/YYYY HH:MM:SS" |
| ONS | Hora operativa (00:00 = meia-noite de Brasilia) | "DD/MM/YYYY HH:00" |
| ANEEL | Data (sem hora) | "DD/MM/YYYY" |

#### Solucao

Todos os timestamps sao normalizados para **UTC** no momento da ingestao. O timezone original e preservado como metadata.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Timezone padrao do setor eletrico brasileiro
BRT = ZoneInfo("America/Sao_Paulo")

# Hora operativa ONS: dia operativo comeca as 00:00 de Brasilia
# Ex: dado com hora operativa "01/06/2024 14:00" = 2024-06-01T14:00:00-03:00
ONS_TIMEZONE = BRT

def normalize_timestamp(
    raw_timestamp: str,
    source_timezone: str | None = None,
    source_format: str | None = None
) -> datetime:
    """
    Normaliza timestamp para UTC.

    Args:
        raw_timestamp: Timestamp no formato original
        source_timezone: Timezone da fonte (ex: "America/Sao_Paulo")
        source_format: Formato strptime (ex: "%d/%m/%Y %H:%M:%S")

    Returns:
        datetime em UTC com tzinfo
    """
    if source_format:
        dt = datetime.strptime(raw_timestamp, source_format)
    else:
        dt = datetime.fromisoformat(raw_timestamp)

    if dt.tzinfo is None:
        tz = ZoneInfo(source_timezone) if source_timezone else BRT
        dt = dt.replace(tzinfo=tz)

    return dt.astimezone(timezone.utc)
```

#### Reamostragem

Dados brutos podem chegar em frequencias irregulares. O pipeline gera series reamostradas em frequencias padrao para consumo pela camada analitica.

| Frequencia Padrao | Metodo de Agregacao | Uso |
|---|---|---|
| 1 min | Media, Min, Max, Last | Dashboard em tempo real |
| 5 min | Media, Min, Max | Deteccao de anomalias |
| 15 min | Media, Min, Max | Analise de tendencia (curto prazo) |
| 1 hora | Media, Min, Max, Std | Health Score, relatorios |
| 1 dia | Media, Min, Max, Std, P5, P95 | Relatorios executivos, tendencias |

Implementacao via TimescaleDB Continuous Aggregates (ver secao 6.1).

#### Tratamento de Gaps

```python
class GapHandler:
    """Estrategias para tratamento de lacunas nos dados."""

    MAX_INTERPOLATION_GAP_MINUTES = 15  # Interpolar ate 15 min de gap
    MAX_FORWARD_FILL_MINUTES = 60       # Forward fill ate 1 hora

    def handle_gap(
        self,
        measurement_type: str,
        gap_duration_minutes: float,
        last_value: float,
        next_value: float | None
    ) -> list[dict]:
        """
        Decide como tratar um gap baseado na duracao e tipo de medicao.

        Estrategias:
        1. Gap < 15 min: interpolacao linear
        2. Gap 15-60 min: forward fill com quality_flag=1
        3. Gap > 60 min: nenhum preenchimento, registrar gap event
        """
        if gap_duration_minutes <= self.MAX_INTERPOLATION_GAP_MINUTES:
            return self._interpolate(last_value, next_value, gap_duration_minutes)
        elif gap_duration_minutes <= self.MAX_FORWARD_FILL_MINUTES:
            return self._forward_fill(last_value, gap_duration_minutes)
        else:
            self._register_gap_event(measurement_type, gap_duration_minutes)
            return []
```

### 5.2 Qualidade de Dados

#### Quality Flags

| Flag | Significado | Acao |
|---|---|---|
| 0 | Bom | Dado confiavel, usar normalmente |
| 1 | Suspeito | Dado potencialmente incorreto; incluir em analise com ressalva |
| 2 | Ruim | Dado invalido; excluir de calculos analiticos |

#### Deteccao Automatica de Problemas

```python
class DataQualityChecker:
    """Verifica qualidade de cada data point recebido."""

    def check(self, point: DataPoint, context: AssetContext) -> int:
        """
        Retorna quality_flag para o data point.

        Checks executados em ordem de severidade:
        """
        # Check 1: Valor fora de range fisicamente possivel -> flag 2 (ruim)
        if not context.physical_range.contains(point.value):
            return 2

        # Check 2: Valor fora de range operacional normal -> flag 1 (suspeito)
        if not context.operational_range.contains(point.value):
            return 1

        # Check 3: Spike detection (variacao > X% em intervalo < Y)
        if self._is_spike(point, context):
            return 1

        # Check 4: Flatline detection (mesmo valor por tempo excessivo)
        if self._is_flatline(point, context):
            return 1

        # Check 5: Rate of change (taxa de variacao anormalmente alta)
        if self._abnormal_rate_of_change(point, context):
            return 1

        return 0  # Bom

    def _is_spike(self, point: DataPoint, context: AssetContext) -> bool:
        """
        Detecta spikes: variacao > 3 sigma em relacao a media movel.
        Janela: ultimos 30 minutos.
        """
        recent_values = context.get_recent_values(minutes=30)
        if len(recent_values) < 5:
            return False
        mean = sum(recent_values) / len(recent_values)
        std = (sum((v - mean) ** 2 for v in recent_values) / len(recent_values)) ** 0.5
        if std == 0:
            return False
        z_score = abs(point.value - mean) / std
        return z_score > 3.0

    def _is_flatline(self, point: DataPoint, context: AssetContext) -> bool:
        """
        Detecta flatline: mesmo valor exato por mais de 30 minutos.
        Indicativo de sensor travado.
        """
        recent_values = context.get_recent_values(minutes=30)
        if len(recent_values) < 10:
            return False
        return all(v == recent_values[0] for v in recent_values)

    def _abnormal_rate_of_change(self, point: DataPoint, ctx: AssetContext) -> bool:
        """
        Detecta taxa de variacao anormalmente alta.
        Ex: temperatura de oleo subindo 10C/min (fisicamente improvavel).
        """
        last = ctx.get_last_value()
        if last is None:
            return False
        elapsed_minutes = (point.timestamp - last.timestamp).total_seconds() / 60
        if elapsed_minutes == 0:
            return False
        rate = abs(point.value - last.value) / elapsed_minutes
        return rate > ctx.max_rate_of_change
```

#### Data Quality Score

Cada medicao e cada ativo recebem um score de qualidade agregado.

```python
class DataQualityScore:
    """Calcula score de qualidade agregado."""

    def score_measurement_point(
        self,
        asset_id: str,
        measurement_type: str,
        period_hours: int = 24
    ) -> dict:
        """
        Score de qualidade para um measurement point em um periodo.

        Componentes:
        - Completude: % de pontos recebidos vs esperados
        - Validade: % de pontos com quality_flag = 0
        - Pontualidade: % de pontos dentro do SLA de latencia
        """
        expected_points = self._expected_points(measurement_type, period_hours)
        received_points = self._received_points(asset_id, measurement_type, period_hours)
        good_points = self._good_points(asset_id, measurement_type, period_hours)
        timely_points = self._timely_points(asset_id, measurement_type, period_hours)

        completeness = received_points / expected_points if expected_points > 0 else 0
        validity = good_points / received_points if received_points > 0 else 0
        timeliness = timely_points / received_points if received_points > 0 else 0

        overall = (completeness * 0.4 + validity * 0.4 + timeliness * 0.2)

        return {
            "asset_id": asset_id,
            "measurement_type": measurement_type,
            "period_hours": period_hours,
            "completeness": round(completeness, 4),
            "validity": round(validity, 4),
            "timeliness": round(timeliness, 4),
            "overall_score": round(overall, 4),
            "expected_points": expected_points,
            "received_points": received_points,
            "good_points": good_points,
        }

    def score_asset(self, asset_id: str, period_hours: int = 24) -> dict:
        """Score agregado por ativo (media dos measurement points)."""
        measurement_types = self._get_measurement_types(asset_id)
        scores = [
            self.score_measurement_point(asset_id, mt, period_hours)
            for mt in measurement_types
        ]
        avg_score = sum(s['overall_score'] for s in scores) / len(scores) if scores else 0
        return {
            "asset_id": asset_id,
            "period_hours": period_hours,
            "overall_score": round(avg_score, 4),
            "measurement_scores": scores,
            "worst_measurement": min(scores, key=lambda s: s['overall_score']) if scores else None
        }
```

### 5.3 Enriquecimento

O enriquecimento adiciona contexto aos dados brutos antes do armazenamento final.

#### Etapas de Enriquecimento

```
Dado Bruto (asset_id, measurement_type, value, timestamp)
    |
    v
[1. Lookup no Energy Graph]
    - Resolver identidade do ativo
    - Obter metadata: subestacao, empresa, regiao, tipo
    - Validar que o ativo existe
    |
    v
[2. Adicao de Metadata]
    - tenant_id (multi-tenancy)
    - substation_id, company_id, region
    - asset_type (para regras de validacao por tipo)
    |
    v
[3. Calculo de Metricas Derivadas]
    - Taxa de variacao (delta / delta_t)
    - Media movel (janela de 1h)
    - Desvio em relacao ao baseline
    |
    v
[4. Atualizacao do Energy Graph]
    - Property last_measurement_at no no do ativo
    - Property last_value_{measurement_type}
    |
    v
Dado Enriquecido --> TimescaleDB
```

#### Cache de Enriquecimento (Redis)

Para evitar consultas repetitivas ao Neo4j, metadata de ativos e cacheada no Redis.

```python
class AssetMetadataCache:
    """Cache Redis para metadata de ativos (evitar roundtrips ao Neo4j)."""

    CACHE_TTL_SECONDS = 3600  # 1 hora
    KEY_PREFIX = "asset_meta"

    async def get_metadata(self, asset_id: str) -> dict | None:
        key = f"{self.KEY_PREFIX}:{asset_id}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Cache miss: buscar no Neo4j
        metadata = await self._fetch_from_neo4j(asset_id)
        if metadata:
            await self.redis.setex(key, self.CACHE_TTL_SECONDS, json.dumps(metadata))
        return metadata

    async def _fetch_from_neo4j(self, asset_id: str) -> dict | None:
        query = """
        MATCH (a:Asset {id: $asset_id})
        OPTIONAL MATCH (a)<-[:CONTAINS]-(s:Substation)
        OPTIONAL MATCH (s)<-[:CONTAINS]-(r:Region)
        OPTIONAL MATCH (r)<-[:OWNS]-(c:Company)
        OPTIONAL MATCH (a)-[:IS_TYPE]->(t:AssetType)
        RETURN a, s, r, c, t
        """
        result = await self.neo4j.run(query, asset_id=asset_id)
        # ... parse e retornar metadata
```

---

## 6. Storage Strategy

### 6.1 TimescaleDB

TimescaleDB e usado como banco primario de series temporais. Ele estende PostgreSQL com hypertables otimizadas para dados temporais.

#### Schema Principal

```sql
-- Hypertable principal de medicoes
CREATE TABLE measurements (
    time            TIMESTAMPTZ     NOT NULL,
    tenant_id       TEXT            NOT NULL,
    asset_id        TEXT            NOT NULL,
    measurement_type TEXT           NOT NULL,
    value           DOUBLE PRECISION NOT NULL,
    quality_flag    SMALLINT        NOT NULL DEFAULT 0,
    source_id       TEXT,
    ingested_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Criar hypertable com chunks de 1 dia
SELECT create_hypertable('measurements', 'time',
    chunk_time_interval => INTERVAL '1 day'
);

-- Indice composto para queries mais comuns
CREATE INDEX idx_measurements_asset_type_time
    ON measurements (tenant_id, asset_id, measurement_type, time DESC);

-- Constraint de unicidade para idempotencia
CREATE UNIQUE INDEX idx_measurements_unique
    ON measurements (time, tenant_id, asset_id, measurement_type);
```

#### Compression Policy

```sql
-- Habilitar compressao nativa do TimescaleDB
ALTER TABLE measurements SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id, asset_id, measurement_type',
    timescaledb.compress_orderby = 'time DESC'
);

-- Comprimir chunks com mais de 7 dias automaticamente
SELECT add_compression_policy('measurements', INTERVAL '7 days');

-- Taxa de compressao esperada: ~10-20x para dados de telemetria
-- 1 GB raw ~= 50-100 MB comprimido
```

#### Continuous Aggregates

```sql
-- Agregado de 15 minutos
CREATE MATERIALIZED VIEW measurements_15min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('15 minutes', time) AS bucket,
    tenant_id,
    asset_id,
    measurement_type,
    AVG(value)    AS avg_value,
    MIN(value)    AS min_value,
    MAX(value)    AS max_value,
    COUNT(*)      AS sample_count,
    AVG(quality_flag::float) AS avg_quality
FROM measurements
WHERE quality_flag < 2  -- Excluir dados ruins
GROUP BY bucket, tenant_id, asset_id, measurement_type;

-- Politica de refresh automatico
SELECT add_continuous_aggregate_policy('measurements_15min',
    start_offset => INTERVAL '2 hours',
    end_offset   => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '15 minutes'
);

-- Agregado de 1 hora
CREATE MATERIALIZED VIEW measurements_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    tenant_id,
    asset_id,
    measurement_type,
    AVG(value)             AS avg_value,
    MIN(value)             AS min_value,
    MAX(value)             AS max_value,
    STDDEV(value)          AS std_value,
    COUNT(*)               AS sample_count,
    AVG(quality_flag::float) AS avg_quality
FROM measurements
WHERE quality_flag < 2
GROUP BY bucket, tenant_id, asset_id, measurement_type;

SELECT add_continuous_aggregate_policy('measurements_1h',
    start_offset => INTERVAL '4 hours',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- Agregado diario
CREATE MATERIALIZED VIEW measurements_1d
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    tenant_id,
    asset_id,
    measurement_type,
    AVG(value)                 AS avg_value,
    MIN(value)                 AS min_value,
    MAX(value)                 AS max_value,
    STDDEV(value)              AS std_value,
    PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY value) AS p5_value,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value) AS p95_value,
    COUNT(*)                   AS sample_count,
    AVG(quality_flag::float)   AS avg_quality
FROM measurements
WHERE quality_flag < 2
GROUP BY bucket, tenant_id, asset_id, measurement_type;

SELECT add_continuous_aggregate_policy('measurements_1d',
    start_offset => INTERVAL '3 days',
    end_offset   => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);
```

#### Retention Policy

```sql
-- Raw data: manter 90 dias
SELECT add_retention_policy('measurements', INTERVAL '90 days');

-- Agregados 15min: manter 180 dias
SELECT add_retention_policy('measurements_15min', INTERVAL '180 days');

-- Agregados 1h: manter 2 anos
SELECT add_retention_policy('measurements_1h', INTERVAL '2 years');

-- Agregados diarios: manter 5 anos
SELECT add_retention_policy('measurements_1d', INTERVAL '5 years');
```

#### Tabelas Auxiliares

```sql
-- Historico de manutencao
CREATE TABLE maintenance_history (
    id              SERIAL PRIMARY KEY,
    tenant_id       TEXT            NOT NULL,
    work_order_id   TEXT            NOT NULL,
    asset_id        TEXT            NOT NULL,
    work_order_type TEXT            NOT NULL,
    description     TEXT,
    start_date      TIMESTAMPTZ     NOT NULL,
    end_date        TIMESTAMPTZ,
    failure_code    TEXT,
    component_replaced TEXT,
    cost_brl        NUMERIC(15, 2),
    priority        TEXT            NOT NULL,
    status          TEXT            NOT NULL,
    downtime_hours  NUMERIC(10, 2),
    root_cause      TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, work_order_id)
);

-- Dados ONS/ANEEL
CREATE TABLE public_datasets (
    time            TIMESTAMPTZ     NOT NULL,
    dataset_id      TEXT            NOT NULL,
    entity_id       TEXT            NOT NULL,  -- usina, subestacao, etc
    metric          TEXT            NOT NULL,
    value           DOUBLE PRECISION,
    text_value      TEXT,
    version         INT             NOT NULL DEFAULT 1,
    source_file     TEXT
);

SELECT create_hypertable('public_datasets', 'time',
    chunk_time_interval => INTERVAL '1 month'
);

-- Dataset version control
CREATE TABLE dataset_versions (
    id              SERIAL PRIMARY KEY,
    dataset_id      TEXT            NOT NULL,
    reference_date  DATE            NOT NULL,
    version         INT             NOT NULL,
    checksum_sha256 TEXT            NOT NULL,
    downloaded_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    file_path       TEXT,
    record_count    INT,
    is_latest       BOOLEAN         NOT NULL DEFAULT TRUE,
    UNIQUE (dataset_id, reference_date, version)
);

-- Tabela de dead letter queue (dados rejeitados)
CREATE TABLE ingest_dead_letter (
    id              SERIAL PRIMARY KEY,
    received_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    tenant_id       TEXT,
    source_id       TEXT,
    data_source     TEXT            NOT NULL,
    raw_data        JSONB           NOT NULL,
    error_message   TEXT            NOT NULL,
    error_type      TEXT            NOT NULL,
    reprocessed     BOOLEAN         NOT NULL DEFAULT FALSE,
    reprocessed_at  TIMESTAMPTZ
);
```

### 6.2 Neo4j (Energy Graph)

O Energy Graph armazena a ontologia de ativos e suas relacoes. O pipeline de ingestao interage com o Neo4j para:

1. **Validar**: Verificar que o ativo existe antes de aceitar dados
2. **Enriquecer**: Obter metadata para contextualizacao
3. **Atualizar**: Manter properties atualizados com dados mais recentes

#### Atualizacoes Realizadas pelo Pipeline

```cypher
// 1. Atualizar ultimo valor de medicao no no do ativo
MATCH (a:Asset {id: $asset_id})
SET a.last_measurement_at = $timestamp,
    a.updated_at = datetime()

// 2. Atualizar propriedades especificas (health-related)
MATCH (a:Asset {id: $asset_id})
SET a.last_oil_temperature = $value,
    a.last_health_score = $health_score,
    a.health_status = CASE
        WHEN $health_score >= 80 THEN 'good'
        WHEN $health_score >= 60 THEN 'attention'
        WHEN $health_score >= 40 THEN 'warning'
        ELSE 'critical'
    END

// 3. Registrar evento de manutencao como relacao
MATCH (a:Asset {id: $asset_id})
CREATE (m:MaintenanceEvent {
    work_order_id: $wo_id,
    type: $wo_type,
    start_date: datetime($start_date),
    description: $description
})
CREATE (a)-[:HAD_MAINTENANCE]->(m)

// 4. Criar relacao de indisponibilidade (dados ONS)
MATCH (a:Asset {id: $asset_id})
CREATE (u:UnavailabilityEvent {
    type: $type,  // 'programada' ou 'forcada'
    start_date: datetime($start),
    end_date: datetime($end),
    reason: $reason,
    source: 'ONS'
})
CREATE (a)-[:HAD_UNAVAILABILITY]->(u)
```

#### Indices Neo4j para Performance

```cypher
CREATE INDEX asset_id_idx FOR (a:Asset) ON (a.id);
CREATE INDEX asset_type_idx FOR (a:Asset) ON (a.type);
CREATE INDEX substation_id_idx FOR (s:Substation) ON (s.id);
CREATE INDEX company_id_idx FOR (c:Company) ON (c.id);
CREATE CONSTRAINT asset_id_unique FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT substation_id_unique FOR (s:Substation) REQUIRE s.id IS UNIQUE;
```

### 6.3 Redis

Redis desempenha tres funcoes no pipeline de ingestao:

#### 6.3.1 Cache de Ultimo Valor

```
Key pattern:  last_value:{tenant_id}:{asset_id}:{measurement_type}
Value:        JSON { "value": 85.3, "timestamp": "2024-06-01T14:30:00Z", "quality": 0 }
TTL:          24 horas (renovado a cada atualizacao)
```

Usado pelo dashboard para exibir valores atuais sem consultar TimescaleDB.

#### 6.3.2 Buffer de Ingestao (Redis Streams)

```
Stream key:   scada:ingest:{tenant_id}
Max length:   100.000 mensagens
Consumer group: ingest_workers
Consumers:    worker-1, worker-2, ... (escalavel)
```

O Redis Stream garante:
- Ordering por tenant
- Acknowledgement (dados nao sao perdidos se worker cair)
- Consumer groups (multiplos workers processam em paralelo)
- Backpressure (MAXLEN limita memoria)

#### 6.3.3 Cache de Metadata

```
Key pattern:  asset_meta:{asset_id}
Value:        JSON com metadata do ativo (tipo, subestacao, empresa, ranges)
TTL:          1 hora

Key pattern:  contract:{data_source}:{version}
Value:        JSON com contrato de dados
TTL:          30 minutos
```

---

## 7. Observabilidade

### 7.1 Metricas (Prometheus)

#### Metricas do Pipeline

```python
from prometheus_client import Counter, Histogram, Gauge

# Pontos ingeridos
POINTS_INGESTED = Counter(
    'ontogrid_ingest_points_total',
    'Total de data points ingeridos',
    ['tenant_id', 'source_type', 'status']  # status: accepted, rejected
)

# Latencia de ingestao
INGEST_LATENCY = Histogram(
    'ontogrid_ingest_latency_seconds',
    'Latencia de ingestao (fonte -> storage)',
    ['tenant_id', 'source_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Tamanho do batch
BATCH_SIZE = Histogram(
    'ontogrid_ingest_batch_size',
    'Tamanho dos batches de ingestao',
    ['tenant_id', 'source_type'],
    buckets=[10, 50, 100, 500, 1000, 5000]
)

# Taxa de rejeicao
REJECTION_RATE = Counter(
    'ontogrid_ingest_rejections_total',
    'Total de pontos rejeitados por tipo de erro',
    ['tenant_id', 'error_type']
    # error_types: out_of_range, invalid_schema, unknown_asset,
    #              duplicate, future_timestamp, null_value
)

# Data quality score
DATA_QUALITY_SCORE = Gauge(
    'ontogrid_data_quality_score',
    'Score de qualidade de dados (0-1)',
    ['tenant_id', 'asset_id', 'measurement_type']
)

# Conectores ativos
ACTIVE_CONNECTORS = Gauge(
    'ontogrid_connectors_active',
    'Numero de conectores ativos',
    ['tenant_id', 'connector_type']
)

# Redis buffer size
REDIS_BUFFER_SIZE = Gauge(
    'ontogrid_redis_buffer_size',
    'Tamanho do buffer Redis Stream',
    ['tenant_id']
)

# TimescaleDB write throughput
TIMESCALE_WRITE_RATE = Counter(
    'ontogrid_timescaledb_writes_total',
    'Total de escritas no TimescaleDB',
    ['tenant_id', 'table']
)
```

#### Metricas de Infraestrutura

| Metrica | Fonte | Threshold de Alerta |
|---|---|---|
| CPU/memoria dos workers | Prometheus node_exporter | CPU > 80% por 5 min |
| Conexoes ativas TimescaleDB | pg_stat_activity | > 80% do max_connections |
| Tamanho do disco TimescaleDB | node_exporter | > 80% capacidade |
| Neo4j heap usage | Neo4j metrics | > 75% do max heap |
| Redis memory usage | Redis INFO | > 70% do maxmemory |
| Celery queue length | Flower / Celery events | > 10K tasks pendentes |

### 7.2 Alertas de Pipeline

```yaml
# prometheus_rules/ingest_alerts.yaml
groups:
  - name: ontogrid_ingest_alerts
    rules:

      # Pipeline parado - nenhum dado em 5 minutos
      - alert: IngestPipelineStopped
        expr: |
          rate(ontogrid_ingest_points_total[5m]) == 0
          AND ON(tenant_id) ontogrid_connectors_active > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pipeline de ingestao parado para tenant {{ $labels.tenant_id }}"
          description: "Nenhum dado ingerido nos ultimos 5 minutos apesar de conectores ativos"

      # Taxa de erros acima de 5%
      - alert: HighRejectionRate
        expr: |
          rate(ontogrid_ingest_rejections_total[15m])
          / rate(ontogrid_ingest_points_total[15m]) > 0.05
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Taxa de rejeicao alta (>5%) para tenant {{ $labels.tenant_id }}"

      # Latencia acima do SLA (30 segundos)
      - alert: HighIngestLatency
        expr: |
          histogram_quantile(0.95, rate(ontogrid_ingest_latency_seconds_bucket[5m])) > 30
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Latencia de ingestao P95 acima de 30s"

      # Redis buffer crescendo (backpressure)
      - alert: RedisBufferBackpressure
        expr: ontogrid_redis_buffer_size > 50000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis buffer acima de 50K mensagens - possivel backpressure"

      # Data quality degradado
      - alert: LowDataQuality
        expr: ontogrid_data_quality_score < 0.8
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Data quality score abaixo de 80% para {{ $labels.asset_id }}"

      # Crawler ONS/ANEEL falhou
      - alert: CrawlerFailed
        expr: |
          ontogrid_crawler_last_success_timestamp < time() - 86400
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Crawler nao obteve sucesso nas ultimas 24 horas"
```

### 7.3 Dashboard de Ingestao (Grafana)

O dashboard de ingestao fornece visibilidade operacional em tempo real do pipeline.

#### Paineis Recomendados

| Painel | Tipo | Query/Metrica |
|---|---|---|
| Throughput (pontos/s) | Time series | `rate(ontogrid_ingest_points_total[1m])` |
| Latencia P50/P95/P99 | Time series | `histogram_quantile(0.95, ...)` |
| Taxa de rejeicao (%) | Time series | `rejections / total * 100` |
| Conectores ativos | Stat | `ontogrid_connectors_active` |
| Buffer Redis | Gauge | `ontogrid_redis_buffer_size` |
| Data Quality Score por ativo | Table | `ontogrid_data_quality_score` |
| Ultimos erros | Log panel | Logs estruturados filtrados por level=error |
| Status por tenant | Status map | Um indicador por tenant (verde/amarelo/vermelho) |
| Volume diario (GB) | Bar chart | Volume de dados ingeridos por dia |
| Top 10 ativos com pior qualidade | Bar chart | Bottom 10 por quality score |

#### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Exemplo de log em cada estagio do pipeline
logger.info(
    "ingest.point.accepted",
    tenant_id=tenant_id,
    asset_id=asset_id,
    measurement_type=measurement_type,
    value=value,
    quality_flag=quality_flag,
    source_id=source_id,
    latency_ms=latency_ms,
    correlation_id=correlation_id,
)

logger.warning(
    "ingest.point.rejected",
    tenant_id=tenant_id,
    asset_id=asset_id,
    error_type="out_of_range",
    error_detail=f"Valor {value} fora do range [{min_val}, {max_val}]",
    raw_data=raw_data,
    correlation_id=correlation_id,
)
```

---

## 8. Simulador de Dados (Desenvolvimento)

O simulador gera dados SCADA realisticos para desenvolvimento, testes e demos com design partners sem necessidade de conexao com sistemas reais.

### 8.1 Arquitetura do Simulador

```python
# simulators/scada_simulator.py

class ScadaSimulator:
    """
    Gera dados de telemetria realisticos para ativos do setor eletrico.

    Uso:
        simulator = ScadaSimulator(config_path="simulator_config.yaml")
        simulator.run(duration_hours=24, speed_multiplier=60)  # 24h em 24 min
    """

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.assets = self._initialize_assets()
        self.scenarios = self._load_scenarios()

    def generate_point(
        self,
        asset: SimulatedAsset,
        measurement_type: str,
        current_time: datetime,
        scenario: str = "normal"
    ) -> DataPoint:
        """
        Gera um data point realistico baseado em:
        - Perfil do ativo (tipo, especificacoes)
        - Hora do dia (carga varia com demanda)
        - Cenario ativo (normal, degradacao, falha)
        - Ruido gaussiano
        - Correlacao entre parametros
        """
        base_value = self._get_base_value(asset, measurement_type, current_time)
        scenario_modifier = self._apply_scenario(scenario, measurement_type, current_time)
        noise = self._add_noise(measurement_type)
        correlated_adj = self._apply_correlations(asset, measurement_type, current_time)

        value = base_value + scenario_modifier + noise + correlated_adj

        return DataPoint(
            timestamp=current_time,
            tenant_id=asset.tenant_id,
            asset_id=asset.asset_id,
            measurement_type=measurement_type,
            value=round(value, 2),
            quality_flag=0,
            source_id="simulator"
        )
```

### 8.2 Cenarios Simulados

#### Operacao Normal

```yaml
scenario: normal
description: "Operacao normal com variacao diurna de carga"
duration: continuous
parameters:
  load_profile:
    type: "daily_curve"
    peak_hours: [10, 11, 14, 15, 16, 17, 18, 19]  # Pico de carga
    peak_factor: 0.85  # 85% da capacidade no pico
    offpeak_factor: 0.45  # 45% fora de ponta
  temperature:
    ambient_base: 28  # Celsius (media anual)
    daily_variation: 8  # +/- 8C ao longo do dia
    correlation_with_load: 0.7
  noise:
    type: "gaussian"
    std_percent: 0.02  # 2% de ruido
```

#### Degradacao Gradual

```yaml
scenario: gradual_degradation
description: "Degradacao termica progressiva simulando envelhecimento do isolamento"
duration_days: 30
trigger: "day_5"
parameters:
  affected_measurements:
    - measurement_type: "oil_temperature_top"
      drift_rate_celsius_per_day: 0.3  # +0.3C/dia
      max_drift: 15  # Maximo +15C acima do normal
    - measurement_type: "dga_hydrogen"
      drift_rate_ppm_per_day: 2  # +2 ppm/dia
      max_drift: 200
    - measurement_type: "dga_co"
      drift_rate_ppm_per_day: 5
      max_drift: 500
  correlation: "DGA gases correlacionados com temperatura"
```

#### Falha Subita

```yaml
scenario: sudden_failure
description: "Falha subita (ex: curto-circuito interno no transformador)"
duration_minutes: 30
trigger: "random"  # Momento aleatorio dentro da simulacao
parameters:
  pre_fault:
    duration_seconds: 120  # 2 minutos de sinais precursores
    affected:
      - measurement_type: "current_phase_a"
        spike_factor: 1.5  # Corrente sobe 50%
      - measurement_type: "vibration_radial"
        spike_factor: 3.0
  fault:
    duration_seconds: 5
    affected:
      - measurement_type: "current_phase_a"
        spike_factor: 8.0  # Corrente de curto
      - measurement_type: "winding_temperature_hotspot"
        spike_factor: 2.0
  post_fault:
    # Disjuntor abre, ativo desenergi zado
    all_measurements: "zero_or_ambient"
    breaker_operations_count: "+1"
```

#### Manutencao Programada

```yaml
scenario: scheduled_maintenance
description: "Desligamento para manutencao preventiva"
trigger: "scheduled"
schedule: "2024-06-15T08:00:00-03:00"
parameters:
  pre_maintenance:
    duration_hours: 1
    load_rampdown: true  # Reducao gradual de carga
  maintenance_window:
    duration_hours: 48
    all_measurements: "zero_or_ambient"
    maintenance_event:
      work_order_type: "preventive"
      description: "Manutencao preventiva anual"
  post_maintenance:
    duration_hours: 2
    load_rampup: true  # Retorno gradual de carga
    temperature_baseline_reset: true  # Baseline recalculado
```

### 8.3 Configuracao por Tipo de Ativo

```yaml
# simulator_config.yaml
simulation:
  tenant_id: "demo"
  speed_multiplier: 1  # 1 = tempo real, 60 = 1 min = 1 hora

assets:
  - asset_id: "TR-DEMO-01"
    asset_type: "power_transformer"
    name: "Transformador de Potencia 01"
    substation: "SE-DEMO"
    rated_power_mva: 150
    rated_voltage_primary_kv: 230
    rated_voltage_secondary_kv: 69
    year: 2010
    measurements:
      - type: oil_temperature_top
        base_value: 65
        unit: celsius
        sampling_interval_seconds: 60
      - type: winding_temperature_hotspot
        base_value: 85
        unit: celsius
        sampling_interval_seconds: 60
      - type: oil_level
        base_value: 95
        unit: percent
        sampling_interval_seconds: 300
      - type: dga_hydrogen
        base_value: 30
        unit: ppm
        sampling_interval_seconds: 900
      - type: current_phase_a
        base_value: 350
        unit: ampere
        sampling_interval_seconds: 1
    scenario: "normal"  # ou "gradual_degradation", "sudden_failure"

  - asset_id: "DJ-DEMO-01"
    asset_type: "circuit_breaker"
    name: "Disjuntor AT 01"
    substation: "SE-DEMO"
    measurements:
      - type: sf6_pressure
        base_value: 6.2
        unit: bar
        sampling_interval_seconds: 300
      - type: breaker_operations_count
        base_value: 2340
        unit: count
        sampling_interval_seconds: 0  # Apenas por evento
    scenario: "normal"
```

### 8.4 Execucao do Simulador

```bash
# Rodar simulador em modo tempo real (para desenvolvimento)
python -m ontogrid.simulators.scada_simulator \
    --config simulator_config.yaml \
    --speed 1 \
    --output redis  # Enviar para Redis Stream (pipeline completo)

# Rodar simulador acelerado (24 horas em 24 minutos)
python -m ontogrid.simulators.scada_simulator \
    --config simulator_config.yaml \
    --speed 60 \
    --duration 24h \
    --output redis

# Gerar CSV para testes offline
python -m ontogrid.simulators.scada_simulator \
    --config simulator_config.yaml \
    --speed max \
    --duration 7d \
    --output csv \
    --output-path ./test_data/

# Simular cenario especifico
python -m ontogrid.simulators.scada_simulator \
    --config simulator_config.yaml \
    --scenario gradual_degradation \
    --asset TR-DEMO-01 \
    --duration 30d \
    --output redis
```

---

## 9. Fluxo de Onboarding de Novo Cliente

O onboarding de um novo cliente (design partner ou cliente pagante) segue um processo estruturado para garantir que dados fluam corretamente e o sistema gere valor rapidamente.

### 9.1 Etapas do Onboarding

```
Etapa 1          Etapa 2          Etapa 3          Etapa 4          Etapa 5          Etapa 6
+------------+   +------------+   +------------+   +------------+   +------------+   +------------+
| Receber    |   | Mapear     |   | Importar   |   | Configurar |   | Validar    |   | Ativar     |
| catalogo   +-->| campos     +-->| para Neo4j +-->| conectores +-->| primeiros  +-->| analytics  |
| de ativos  |   | para schema|   | (Graph)    |   | SCADA      |   | dados      |   | e alertas  |
+------------+   +------------+   +------------+   +------------+   +------------+   +------------+
    1-2 dias        1 dia           1 dia           2-3 dias         1-2 dias         1 dia
```

### 9.2 Detalhamento por Etapa

#### Etapa 1: Receber Catalogo de Ativos (1-2 dias)

**Entrada esperada do cliente:**
- Planilha Excel/CSV com lista de ativos criticos
- Informacoes de subestacoes e localizacao
- Especificacoes tecnicas dos equipamentos
- Hierarquia organizacional (empresa > regional > subestacao)

**Template fornecido ao cliente:**

```
| asset_id | asset_name | asset_type | manufacturer | model | year | rated_power_mva | substation_id | substation_name |
|----------|------------|------------|--------------|-------|------|-----------------|---------------|-----------------|
| (preencher) | (preencher) | (ver lista) | (preencher) | (opcional) | (preencher) | (preencher) | (preencher) | (preencher) |
```

**Checklist:**
- [ ] Recebido catalogo de ativos
- [ ] Identificados todos os ativos criticos (transformadores, disjuntores, geradores)
- [ ] Informacoes de subestacao completas
- [ ] Tenant criado no sistema (tenant_id definido)

#### Etapa 2: Mapear Campos para Schema Padrao (1 dia)

O mapeamento converte a nomenclatura do cliente para o schema padrao do OntoGrid.

```python
# Exemplo de mapeamento
column_mapping = {
    # Campo do cliente       -> Campo OntoGrid
    "Codigo Equipamento":     "asset_id",
    "Descricao":              "asset_name",
    "Tipo":                   "asset_type",
    "Fabricante":             "manufacturer",
    "Ano Fabricacao":         "year_manufactured",
    "Ano Entrada Operacao":   "year_commissioned",
    "Potencia (MVA)":         "rated_power_mva",
    "Tensao Primaria (kV)":   "rated_voltage_primary_kv",
    "Subestacao":             "substation_name",
    "Codigo SE":              "substation_id",
    "Regional":               "region",
    "Empresa":                "company_id",
}

# Mapeamento de tipos de ativo
asset_type_mapping = {
    "Transformador de Potencia": "power_transformer",
    "Trafo de Potencia":         "power_transformer",
    "TP":                        "power_transformer",
    "Disjuntor":                 "circuit_breaker",
    "DJ":                        "circuit_breaker",
    "Gerador":                   "generator_hydro",
    "UG":                        "generator_hydro",
}
```

**Checklist:**
- [ ] Mapeamento de colunas definido
- [ ] Mapeamento de tipos de ativo validado
- [ ] Dados convertidos sem erros
- [ ] Registros rejeitados revisados e corrigidos

#### Etapa 3: Importar para Neo4j - Energy Graph (1 dia)

```python
async def import_asset_catalog(
    tenant_id: str,
    assets: list[AssetRecord],
    neo4j_driver: AsyncDriver
):
    """
    Importa catalogo de ativos para o Energy Graph.
    Usa MERGE para idempotencia (pode ser re-executado).
    """
    async with neo4j_driver.session() as session:
        for asset in assets:
            await session.run("""
                MERGE (c:Company {id: $company_id})
                SET c.name = $company_name

                MERGE (r:Region {id: $region})

                MERGE (s:Substation {id: $substation_id})
                SET s.name = $substation_name,
                    s.latitude = $latitude,
                    s.longitude = $longitude

                MERGE (a:Asset {id: $asset_id})
                SET a.name = $asset_name,
                    a.type = $asset_type,
                    a.manufacturer = $manufacturer,
                    a.year_manufactured = $year_manufactured,
                    a.year_commissioned = $year_commissioned,
                    a.rated_power_mva = $rated_power_mva,
                    a.tenant_id = $tenant_id,
                    a.operating_status = $operating_status,
                    a.imported_at = datetime()

                MERGE (t:AssetType {id: $asset_type})

                MERGE (c)-[:OWNS]->(r)
                MERGE (r)-[:CONTAINS]->(s)
                MERGE (s)-[:CONTAINS]->(a)
                MERGE (a)-[:IS_TYPE]->(t)
            """, **asset.model_dump(), tenant_id=tenant_id)
```

**Checklist:**
- [ ] Nos de Company, Region, Substation criados
- [ ] Todos os ativos importados com relacoes corretas
- [ ] Graph navegavel e consistente (sem nos orfaos)
- [ ] Validacao manual com equipe do cliente

#### Etapa 4: Configurar Conectores SCADA (2-3 dias)

**Opcoes de conexao (por ordem de preferencia):**

1. **OPC-UA direto**: Conexao com servidor OPC-UA do historian
   - Requer endpoint, credenciais e certificados
   - Mapeamento de tags OPC-UA para measurement_types do OntoGrid

2. **API REST**: Conexao com API do historian (PI Web API, etc)
   - Requer URL base, credenciais e mapeamento de endpoints

3. **CSV export agendado**: Export periodico do historian para servidor SFTP
   - Requer configuracao de export no historian do cliente
   - OntoGrid monitora diretorio e processa arquivos novos

4. **CSV manual**: Upload via interface web
   - Solucao temporaria enquanto integracao automatica nao esta pronta

**Mapeamento de tags:**

```yaml
# tag_mapping_{tenant_id}.yaml
tenant_id: "eletronorte"
connection_id: "se-xingu-historian"

tag_mappings:
  - opc_tag: "SE_XINGU.TR01.TEMP_OLEO_TOPO"
    asset_id: "TR-SE-XINGU-01"
    measurement_type: "oil_temperature_top"
    unit: "celsius"
    valid_range: { min: -10, max: 150 }
    sampling_interval_seconds: 60

  - opc_tag: "SE_XINGU.TR01.TEMP_ENROL_HS"
    asset_id: "TR-SE-XINGU-01"
    measurement_type: "winding_temperature_hotspot"
    unit: "celsius"
    valid_range: { min: -10, max: 200 }
    sampling_interval_seconds: 60

  - opc_tag: "SE_XINGU.TR01.DGA_H2"
    asset_id: "TR-SE-XINGU-01"
    measurement_type: "dga_hydrogen"
    unit: "ppm"
    valid_range: { min: 0, max: 50000 }
    sampling_interval_seconds: 900
```

**Checklist:**
- [ ] Metodo de conexao definido
- [ ] Credenciais/certificados obtidos
- [ ] Mapeamento de tags completo
- [ ] Conector configurado e testando
- [ ] Primeiros dados chegando ao pipeline

#### Etapa 5: Validar Primeiros Dados (1-2 dias)

```python
async def validate_onboarding_data(
    tenant_id: str,
    validation_window_hours: int = 24
) -> dict:
    """
    Valida que dados estao fluindo corretamente apos onboarding.
    Executar 24h apos inicio da ingestao.
    """
    return {
        "tenant_id": tenant_id,
        "validation_window_hours": validation_window_hours,
        "checks": {
            "data_flowing": {
                "status": "pass" if points_received > 0 else "fail",
                "points_received": points_received,
                "expected_minimum": expected_points * 0.8,
            },
            "all_assets_reporting": {
                "status": "pass" if missing_assets == [] else "warn",
                "assets_reporting": reporting_assets,
                "assets_missing": missing_assets,
            },
            "data_quality": {
                "status": "pass" if quality_score > 0.8 else "warn",
                "overall_score": quality_score,
                "worst_measurement": worst_measurement,
            },
            "latency": {
                "status": "pass" if p95_latency < 30 else "warn",
                "p50_seconds": p50_latency,
                "p95_seconds": p95_latency,
            },
            "no_anomalies_in_pipeline": {
                "status": "pass" if pipeline_errors == 0 else "fail",
                "errors": pipeline_errors,
                "error_types": error_types,
            }
        },
        "recommendation": "Pronto para ativar analytics" if all_pass else "Revisar items com status warn/fail"
    }
```

**Checklist:**
- [ ] Dados fluindo continuamente por pelo menos 24h
- [ ] Todos os ativos reportando
- [ ] Data quality score > 80%
- [ ] Latencia dentro do SLA (<30s)
- [ ] Nenhum erro critico no pipeline
- [ ] Valores fazem sentido fisico (validacao com equipe do cliente)

#### Etapa 6: Ativar Analytics e Alertas (1 dia)

- [ ] Ativar deteccao de anomalias para os ativos do tenant
- [ ] Configurar regras de alerta padrao por tipo de ativo
- [ ] Configurar canais de notificacao (email dos operadores)
- [ ] Gerar primeiro Health Score para todos os ativos
- [ ] Treinar equipe do cliente no dashboard
- [ ] Definir pontos focais para escalonamento

---

## 10. Limites e Consideracoes

### 10.1 Limites do MVP

| Parametro | Limite MVP | Justificativa |
|---|---|---|
| **Ativos monitorados** | Ate 100 ativos | Escopo controlado para validar modelo de dados e analytics |
| **Measurement points** | Ate 500 | ~5 measurement points por ativo em media |
| **Throughput de ingestao** | 10.000 pontos/segundo | Suficiente para 10 subestacoes em near real-time |
| **Tenants simultaneos** | Ate 5 | 2-3 design partners + ambientes de staging/demo |
| **Retencao raw** | 90 dias | Balancear custo de storage com necessidade analitica |
| **Retencao agregados** | 2 anos (1h), 5 anos (1d) | Atender requisitos de tendencia e regulatorio |
| **Latencia maxima (ingestao)** | 30 segundos | Fonte -> disponivel para query |
| **Latencia maxima (dashboard)** | 2 segundos | Query -> renderizacao no browser |
| **Tamanho maximo de upload CSV** | 100 MB | Processamento assincrono via Celery |
| **Resolucao minima** | 1 segundo | Frequencia maxima de amostragem |

### 10.2 Consideracoes de Seguranca

| Aspecto | Abordagem |
|---|---|
| **Multi-tenancy** | Isolamento logico por tenant_id em todas as queries; row-level security no TimescaleDB |
| **Transporte** | TLS 1.3 para todas as conexoes (OPC-UA, API, banco de dados) |
| **Autenticacao SCADA** | Certificados X.509 para OPC-UA; API keys rotacionadas para REST |
| **Dados em repouso** | Encryption at rest no TimescaleDB (via filesystem encryption) |
| **Auditoria** | Log de todas as operacoes de ingestao com correlation_id |
| **LGPD** | Dados de telemetria nao contem PII; dados de cadastro (nomes de tecnicos) devem ser anonimizaveis |

### 10.3 Consideracoes de Rede

| Cenario | Solucao |
|---|---|
| **Conectividade intermitente** | Buffer local no coletor; re-sync automatico quando conexao restaurada |
| **Firewall do cliente** | Coletor pode rodar on-premises (Docker) e enviar dados via HTTPS outbound |
| **Banda limitada** | Compressao de dados no transporte; amostragem adaptativa |
| **VPN obrigatoria** | Suporte a conexao via VPN site-to-site ou client VPN |

### 10.4 Escalabilidade Pos-MVP

| Componente | MVP | Pos-MVP |
|---|---|---|
| **Workers de ingestao** | 2-4 workers Celery | Kubernetes HPA com auto-scaling |
| **TimescaleDB** | Single node | TimescaleDB multi-node ou sharding por tenant |
| **Redis** | Single node | Redis Cluster |
| **Neo4j** | Single node | Neo4j Cluster (read replicas) |
| **Throughput** | 10K pts/s | 100K+ pts/s com particionamento |
| **Conectores** | OPC-UA, CSV, REST | MQTT, Kafka, Modbus, DNP3, IEC 61850 |

### 10.5 Dependencias Externas

| Dependencia | Versao Minima | Funcao |
|---|---|---|
| **Python** | 3.11+ | Runtime do pipeline |
| **FastAPI** | 0.100+ | API de ingestao |
| **Celery** | 5.3+ | Task queue e workers |
| **Redis** | 7.0+ | Buffer, cache, message broker |
| **TimescaleDB** | 2.11+ | Armazenamento de series temporais |
| **Neo4j** | 5.0+ | Energy Graph |
| **Pydantic** | 2.0+ | Validacao de dados |
| **asyncpg** | 0.28+ | Driver async PostgreSQL |
| **opcua-asyncio** | 1.0+ | Cliente OPC-UA |
| **pandas** | 2.0+ | Parsing CSV/Excel, simulador |
| **prometheus-client** | 0.17+ | Metricas |
| **structlog** | 23.0+ | Logging estruturado |

---

*Documento vivo - atualizar conforme o pipeline evolui e novas fontes de dados sao integradas.*
