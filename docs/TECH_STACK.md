# Tech Stack - OntoGrid

> **OntoGrid** - Plataforma ontologica de dados e decisao para o setor eletrico brasileiro.
> **MVP**: Asset Health - Vigilancia de equipamentos criticos para geradoras e transmissoras.

---

## 1. Resumo da Stack

| Camada | Tecnologia | Versao | Justificativa |
|---|---|---|---|
| **Backend - Runtime** | Python | 3.12 | Performance melhorada (PEP 709), typing robusto, ecossistema ML maduro |
| **Backend - Framework** | FastAPI | 0.111+ | Async nativo, OpenAPI auto-gerado, integracao Pydantic v2 |
| **Backend - ORM** | SQLAlchemy | 2.0 | Async ORM, query builder maduro, suporte TimescaleDB |
| **Backend - Migrations** | Alembic | 1.13+ | Migrations automaticas, integracao nativa com SQLAlchemy |
| **Backend - Task Queue** | Celery + Redis | 5.4+ / 7.x | Processamento assincrono de ingestao SCADA e calculos ML |
| **Backend - Validacao** | Pydantic | 2.7+ | Validacao e serializacao 5-50x mais rapida que v1, integration FastAPI |
| **DB - Relacional/TS** | PostgreSQL + TimescaleDB | 16 / 2.14+ | Series temporais SCADA com compressao nativa e continuous aggregates |
| **DB - Grafo** | Neo4j | 5.x | Energy Graph - modelagem ontologica de ativos e relacoes |
| **DB - Cache/Queue** | Redis | 7.x | Cache, filas Celery, pub/sub para alertas real-time |
| **ML - Anomalias** | scikit-learn | 1.4+ | Isolation Forest, algoritmo padrao para deteccao de anomalias |
| **ML - Outliers** | PyOD | 1.1+ | Biblioteca especializada com 40+ algoritmos de outlier detection |
| **ML - Forecasting** | Prophet | 1.1+ | Forecasting de degradacao com sazonalidade e changepoints |
| **ML - Manipulacao** | NumPy + Pandas | 1.26+ / 2.2+ | Manipulacao eficiente de dados tabulares e series temporais |
| **ML - Estatistica** | SciPy | 1.12+ | Z-score, testes estatisticos, distribuicoes |
| **Frontend - Framework** | Next.js | 14 | App Router, SSR, API routes, otimizacao de bundle |
| **Frontend - Linguagem** | TypeScript | 5.x | Strict mode, type safety, DX superior |
| **Frontend - Styling** | Tailwind CSS | 3.x | Utility-first, design system rapido, bundle minimo |
| **Frontend - Graficos** | Recharts | 2.12+ | Graficos de series temporais, composable, React nativo |
| **Frontend - Grafo Visual** | React Flow | 11+ | Visualizacao interativa do Energy Graph |
| **Frontend - Data Fetching** | TanStack Query | 5.x | Cache inteligente, revalidacao, optimistic updates |
| **Frontend - State** | Zustand | 4.x | State management leve, sem boilerplate |
| **Frontend - Real-time** | Socket.io client | 4.7+ | WebSocket com fallback, reconexao automatica |
| **DevOps - Containers** | Docker + Compose | 25+ / 2.24+ | Ambiente de dev reproduzivel, multi-service |
| **DevOps - CI/CD** | GitHub Actions | N/A | Pipeline nativo GitHub, marketplace de actions |
| **Test - Backend** | pytest + pytest-asyncio | 8.x / 0.23+ | Testes async, fixtures, parametrize |
| **Test - Frontend** | Vitest + Testing Library | 1.x / 14+ | Compativel Vite, API Jest-like, testes de componente |
| **Lint - Python** | Ruff | 0.4+ | Linting ultra-rapido (10-100x mais rapido que flake8) |
| **Format - Python** | Black | 24.x | Formatacao deterministica, zero config |
| **Lint/Format - Frontend** | ESLint + Prettier | 8.x / 3.x | Padrao da industria para JS/TS |

---

## 2. Justificativas Detalhadas

### 2.1 Python 3.12

**Alternativas consideradas:**
- Python 3.11 - Estavel, mas sem otimizacoes do 3.12
- Go - Performance superior, mas ecossistema ML limitado
- Java/Kotlin - Enterprise-ready, mas overhead de desenvolvimento para MVP

**Pros:**
- Inlined comprehensions (PEP 709) - melhoria de performance de 10-20% em loops
- Improved error messages para debug mais rapido
- Ecossistema ML/Data Science incomparavel (scikit-learn, pandas, prophet)
- Typing robusto com `type` keyword nativo
- Async/await maduro para I/O-bound workloads (ingestao SCADA)

**Contras:**
- GIL ainda presente (mitigado com Celery workers para CPU-bound)
- Performance inferior a Go/Rust para workloads puramente computacionais

**Por que e a melhor para o MVP:**
O MVP Asset Health e intensivo em ML (anomalias, forecasting) e ingestao de dados. Python 3.12 oferece o melhor tradeoff entre velocidade de desenvolvimento e capacidade analitica.

**Evolucao pos-MVP:**
- Python 3.13+ com free-threaded mode (PEP 703) para remover GIL
- Modulos criticos em Rust via PyO3 se performance for bottleneck
- Possivel microservico de ingestao em Go para throughput extremo

---

### 2.2 FastAPI

**Alternativas consideradas:**
- Django + DRF - Baterias incluidas, mas overhead para API-first
- Flask - Simples, mas sem async nativo e sem validacao integrada
- Litestar - Moderno, mas comunidade menor

**Pros:**
- Async nativo - essencial para I/O com SCADA, Neo4j e TimescaleDB simultaneamente
- OpenAPI auto-gerado - documentacao viva da API
- Pydantic v2 nativo - validacao e serializacao integradas
- Dependency injection elegante
- Middleware para auth, CORS, rate limiting

**Contras:**
- Sem admin panel built-in (mitigado com SQLAdmin ou painel custom)
- Menos "opinado" que Django - mais decisoes arquiteturais manuais

**Por que e a melhor para o MVP:**
API-first com async para multiplas fontes de dados. OpenAPI auto-gerado acelera integracao com frontend e futuros parceiros. Pydantic v2 garante contratos de dados rigorosos.

**Evolucao pos-MVP:**
- API Gateway (Kong/Traefik) na frente do FastAPI
- GraphQL (Strawberry) para queries complexas do Energy Graph
- gRPC para comunicacao inter-servicos se migrar para microservicos

---

### 2.3 PostgreSQL 16 + TimescaleDB

**Alternativas consideradas:**
- InfluxDB - Time-series puro, mas sem relacional
- ClickHouse - Analytics rapido, mas complexidade operacional
- PostgreSQL puro com partitioning manual - Possivel, mas sem otimizacoes TS

**Pros:**
- Continuous aggregates para dashboards pre-computados (medias horarias, diarias)
- Compressao nativa 90-95% para dados SCADA historicos
- Hypertables com particionamento automatico por tempo
- SQL padrao - sem lock-in, equipe ja conhece
- Retention policies para gerenciar lifecycle de dados
- Funciona como extensao do PostgreSQL - um unico banco para relacional + time-series

**Contras:**
- TimescaleDB Community tem limitacoes em multi-node
- Menos performante que InfluxDB para writes extremos (>1M points/sec)

**Por que e a melhor para o MVP:**
Uma unica instancia PostgreSQL para dados relacionais (usuarios, configs) e time-series (SCADA). Simplifica operacao, backup e queries cross-domain. Community edition suficiente para MVP.

**Evolucao pos-MVP:**
- TimescaleDB Enterprise para multi-node e continuous aggregates materializados
- Read replicas para separar workloads de escrita (ingestao) e leitura (dashboards)
- Citus para sharding horizontal se volume crescer alem de single-node

---

### 2.4 Neo4j 5.x

**Alternativas consideradas:**
- Amazon Neptune - Managed, mas vendor lock-in AWS
- ArangoDB - Multi-model, mas grafo menos maduro
- PostgreSQL com Apache AGE - Evita novo banco, mas Cypher limitado

**Pros:**
- Cypher - linguagem de query de grafos mais expressiva e madura
- Modelagem natural de ontologias (Ativo -> pertence_a -> Subestacao -> conecta -> Linha)
- Traversal eficiente para perguntas como "quais equipamentos sao afetados se este transformador falhar?"
- Visualizacao nativa com Neo4j Browser para debug
- APOC library para ETL e transformacoes complexas

**Contras:**
- Community Edition limitada a single instance (sem clustering)
- Curva de aprendizado para equipe nao familiarizada com grafos
- Licenciamento Enterprise pode ser caro

**Por que e a melhor para o MVP:**
O Energy Graph e o diferencial do OntoGrid. Neo4j permite modelar a ontologia do setor eletrico de forma natural e performatica. Community Edition suficiente para MVP com single-instance.

**Evolucao pos-MVP:**
- Neo4j Aura (managed) ou Enterprise para clustering e alta disponibilidade
- Graph Data Science library para algoritmos de centralidade, community detection
- Integracao com LLM para queries em linguagem natural sobre o grafo

---

### 2.5 Redis 7

**Alternativas consideradas:**
- RabbitMQ - Message broker robusto, mas nao serve como cache
- Memcached - Cache simples, mas sem pub/sub e persistencia
- Kafka - Streaming poderoso, mas over-engineering para MVP

**Pros:**
- Tripla funcao: cache + message broker (Celery) + pub/sub (alertas real-time)
- Latencia sub-milissegundo para cache de dashboards
- Redis Streams para ingestao de eventos SCADA
- Pub/sub para push de alertas para frontend via Socket.io
- Persistencia RDB/AOF para durabilidade

**Contras:**
- Memoria-bound - custo cresce com volume de cache
- Single-threaded para commands (mitigado com Redis 7 multi-threading para I/O)

**Por que e a melhor para o MVP:**
Um unico componente para tres funcoes reduz complexidade operacional. Performance adequada para volume do MVP.

**Evolucao pos-MVP:**
- Redis Cluster para HA e sharding
- Apache Kafka para event streaming de alta escala
- Redis com modulos adicionais (RedisTimeSeries, RedisGraph) se necessario

---

### 2.6 scikit-learn + PyOD + Prophet (ML Stack)

**Alternativas consideradas:**
- TensorFlow/PyTorch - Deep learning, mas over-engineering para MVP
- statsmodels - Estatistica classica, mas menos user-friendly
- Darts (time-series library) - Boa, mas menos madura que Prophet

**Pros - scikit-learn (Isolation Forest):**
- Algoritmo nao-supervisionado, nao precisa de dados rotulados (raro no setor eletrico)
- Eficiente para dados multivariados de sensores
- API consistente com fit/predict/score
- Interpretabilidade razoavel (anomaly scores)

**Pros - PyOD:**
- 40+ algoritmos de outlier detection em uma unica interface
- Combinacao de modelos (ensemble) para reduzir falsos positivos
- Benchmarks publicados para comparacao

**Pros - Prophet:**
- Decomposicao automatica de tendencia + sazonalidade + feriados
- Robusto a dados faltantes (comum em SCADA)
- Intervalos de confianca nativos para alertas graduais
- Interpretavel para engenheiros de manutencao

**Contras:**
- Prophet descontinuado pelo Meta (mantem comunidade, mas sem updates oficiais)
- Isolation Forest sensivel a hyperparametros (contamination rate)

**Por que e a melhor para o MVP:**
Abordagem classica de ML e suficiente para deteccao de anomalias em series temporais de equipamentos. Nao requer GPU, datasets massivos ou expertise em deep learning. Rapido de implementar e explicavel para stakeholders.

**Evolucao pos-MVP:**
- AutoML (FLAML, Auto-sklearn) para otimizacao de hyperparametros
- LSTM/Transformer para anomalias em sequencias longas
- MLflow para tracking de experimentos e model registry
- Feature store para reutilizacao de features entre modelos

---

### 2.7 Next.js 14

**Alternativas consideradas:**
- Vite + React - Mais simples, mas sem SSR
- Remix - SSR robusto, mas comunidade menor
- Angular - Enterprise-ready, mas curva de aprendizado e bundle maior

**Pros:**
- App Router com React Server Components para performance
- SSR para dashboards com SEO (paginas publicas futuras)
- API Routes para BFF (Backend for Frontend) - proxy de requests
- Middleware para auth e redirecionamento
- Otimizacao automatica de imagens e fonts
- Turbopack para dev server rapido

**Contras:**
- Complexidade do App Router vs Pages Router
- Vendor influence da Vercel nas decisoes de design

**Por que e a melhor para o MVP:**
Dashboard intensivo em dados precisa de SSR para performance inicial. API Routes simplificam autenticacao e proxy para backend Python. Ecossistema React garante disponibilidade de bibliotecas.

**Evolucao pos-MVP:**
- Edge Runtime para CDN-level rendering
- Micro-frontends se multiplos times trabalharem em paralelo
- PWA para acesso offline em campo (subestacoes remotas)

---

### 2.8 Recharts + React Flow

**Alternativas consideradas para graficos:**
- D3.js - Maximo controle, mas baixo nivel demais para MVP
- Chart.js - Simples, mas menos composable com React
- Apache ECharts - Poderoso, mas API complexa
- Plotly - Rico em features, mas bundle pesado

**Alternativas consideradas para grafo visual:**
- Cytoscape.js - Maduro, mas integracao React menos nativa
- D3-force - Baixo nivel, muito trabalho manual
- vis.js - Funcional, mas menos mantido

**Por que Recharts:**
- API declarativa React-native (composable components)
- Otimizado para series temporais (LineChart, AreaChart)
- Customizavel com tooltips e brushes para zoom temporal
- Bundle relativamente leve

**Por que React Flow:**
- Nodes e edges customizaveis para representar ativos do setor eletrico
- Zoom, pan e minimap nativos
- Layout automatico com dagre/elkjs
- Eventos para click em nodes (abrir detalhes do ativo)

**Evolucao pos-MVP:**
- Graficos 3D com Three.js para subestacoes virtuais
- Deck.gl para mapas geoespaciais de linhas de transmissao
- Grafana embedded para dashboards operacionais avancados

---

## 3. Dependencias Criticas

### 3.1 Versoes Minimas

| Componente | Versao Minima | Motivo |
|---|---|---|
| Python | 3.12.0 | PEP 709, typing improvements |
| PostgreSQL | 16.0 | Logical replication melhorado, performance |
| TimescaleDB | 2.14.0 | Continuous aggregates melhorados |
| Neo4j | 5.15.0 | Cypher improvements, performance |
| Redis | 7.2.0 | Redis Functions, multi-part AOF |
| Node.js | 20.x LTS | Next.js 14 requirement |
| npm | 10.x | Workspaces, overrides |

### 3.2 Compatibilidade entre Componentes

```
FastAPI 0.111+ --> Pydantic 2.7+ (obrigatorio, breaking change de v1 para v2)
SQLAlchemy 2.0 --> asyncpg 0.29+ (driver async para PostgreSQL)
SQLAlchemy 2.0 --> psycopg 3.1+ (driver alternativo sync/async)
Celery 5.4+ --> Redis 7.x (broker e result backend)
Celery 5.4+ --> Python 3.12 (compatibilidade confirmada)
Next.js 14 --> React 18.x (obrigatorio)
Next.js 14 --> Node.js 20+ (obrigatorio)
TanStack Query 5 --> React 18+ (obrigatorio)
React Flow 11 --> React 18+ (obrigatorio)
Prophet 1.1+ --> cmdstanpy 1.2+ (backend de sampling)
```

### 3.3 Licenciamento

| Componente | Licenca | Viabilidade Comercial |
|---|---|---|
| Python | PSF License | Livre para uso comercial |
| FastAPI | MIT | Livre para uso comercial |
| SQLAlchemy | MIT | Livre para uso comercial |
| PostgreSQL | PostgreSQL License | Livre para uso comercial |
| TimescaleDB Community | Apache 2.0 (Timescale License para features avancadas) | Community livre; features avancadas requerem licenca |
| Neo4j Community | GPL v3 | Uso em servidor permitido; distribuicao de codigo modificado requer abertura |
| Neo4j Enterprise | Licenca comercial | Requer contrato |
| Redis | BSD 3-Clause (ate v7.2) / RSALv2 + SSPLv1 (v7.4+) | Self-hosted permitido; nao pode oferecer como servico managed |
| Next.js | MIT | Livre para uso comercial |
| scikit-learn | BSD 3-Clause | Livre para uso comercial |
| Prophet | MIT | Livre para uso comercial |
| React Flow | MIT | Livre para uso comercial |
| Recharts | MIT | Livre para uso comercial |

> **Nota sobre Neo4j GPL v3:** A licenca GPL se aplica ao servidor Neo4j Community. Aplicacoes que se conectam via Bolt protocol (driver) nao sao consideradas "derivative works" e nao precisam ser open-source. O OntoGrid se conecta via driver, portanto o uso e seguro para software proprietario.

---

## 4. Packages Python (requirements.txt preview)

```txt
# ============================================
# OntoGrid - Python Dependencies
# ============================================

# --- Web Framework ---
fastapi==0.111.0
uvicorn[standard]==0.30.1
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# --- Database - PostgreSQL / TimescaleDB ---
sqlalchemy==2.0.30
asyncpg==0.29.0
psycopg[binary]==3.1.19
alembic==1.13.1

# --- Database - Neo4j ---
neo4j==5.20.0

# --- Database - Redis ---
redis==5.0.4

# --- Task Queue ---
celery==5.4.0

# --- Validation / Serialization ---
pydantic==2.7.4
pydantic-settings==2.3.4

# --- ML / Analytics ---
scikit-learn==1.4.2
pyod==1.1.3
prophet==1.1.5
numpy==1.26.4
pandas==2.2.2
scipy==1.13.1

# --- Real-time ---
python-socketio==5.11.2

# --- Utilities ---
httpx==0.27.0
orjson==3.10.5
python-dateutil==2.9.0
pytz==2024.1

# --- Monitoring / Logging ---
structlog==24.2.0
sentry-sdk[fastapi]==2.5.1

# --- Dev Dependencies ---
# (instalar com pip install -r requirements-dev.txt)
```

```txt
# ============================================
# requirements-dev.txt
# ============================================
-r requirements.txt

# --- Testing ---
pytest==8.2.2
pytest-asyncio==0.23.7
pytest-cov==5.0.0
pytest-mock==3.14.0
httpx==0.27.0
factory-boy==3.3.0

# --- Linting / Formatting ---
ruff==0.4.8
black==24.4.2
mypy==1.10.0

# --- Type Stubs ---
types-redis==4.6.0.20240425
pandas-stubs==2.2.2.240514

# --- Dev Tools ---
ipython==8.25.0
pre-commit==3.7.1
```

---

## 5. Packages Node (package.json preview)

```json
{
  "name": "ontogrid-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "vitest",
    "test:coverage": "vitest run --coverage",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.2.4",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "typescript": "5.5.2",

    "@tanstack/react-query": "5.45.1",
    "zustand": "4.5.2",
    "socket.io-client": "4.7.5",

    "reactflow": "11.11.3",
    "recharts": "2.12.7",

    "tailwindcss": "3.4.4",
    "@headlessui/react": "2.1.1",
    "@heroicons/react": "2.1.4",
    "clsx": "2.1.1",
    "tailwind-merge": "2.3.0",

    "date-fns": "3.6.0",
    "zod": "3.23.8",
    "axios": "1.7.2",
    "next-auth": "4.24.7"
  },
  "devDependencies": {
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "@types/node": "20.14.8",

    "vitest": "1.6.0",
    "@testing-library/react": "16.0.0",
    "@testing-library/jest-dom": "6.4.6",
    "@testing-library/user-event": "14.5.2",
    "@vitejs/plugin-react": "4.3.1",
    "jsdom": "24.1.0",

    "eslint": "8.57.0",
    "eslint-config-next": "14.2.4",
    "@typescript-eslint/eslint-plugin": "7.14.1",
    "@typescript-eslint/parser": "7.14.1",
    "prettier": "3.3.2",
    "prettier-plugin-tailwindcss": "0.6.5",

    "autoprefixer": "10.4.19",
    "postcss": "8.4.38"
  }
}
```

---

## 6. Restricoes e Limites Conhecidos

### 6.1 TimescaleDB Community vs Licensed

| Feature | Community (Gratuito) | Licensed (Pago) |
|---|---|---|
| Hypertables | Sim | Sim |
| Compressao | Sim | Sim |
| Continuous Aggregates | Sim (com limitacoes) | Sim (real-time) |
| Multi-node / Distributed | Nao | Sim |
| Data Tiering (S3) | Nao | Sim |
| Reorder policies | Nao | Sim |

**Impacto no MVP:** Community Edition e suficiente. O volume esperado no MVP (ate ~100 equipamentos, ~1000 sensores, ~1M pontos/dia) cabe em single-node. Multi-node so sera necessario com escala de milhares de equipamentos.

**Mitigacao:** Compressao agressiva (90-95%) e retention policies para manter apenas dados recentes em alta resolucao. Dados historicos agregados em continuous aggregates.

### 6.2 Neo4j Community vs Enterprise

| Feature | Community (Gratuito) | Enterprise (Pago) |
|---|---|---|
| Cypher completo | Sim | Sim |
| APOC procedures | Sim | Sim |
| Clustering / HA | Nao | Sim (Causal Clustering) |
| Role-based access control | Basico | Completo |
| Online backup | Nao (dump offline) | Sim |
| Multi-database | Nao (1 database) | Sim |
| Fabric (federated queries) | Nao | Sim |

**Impacto no MVP:** Community Edition e adequada. O Energy Graph do MVP tera ~10k-50k nodes (equipamentos, subestacoes, linhas) - bem dentro da capacidade de single-instance. A limitacao principal e backup (requer downtime de segundos para dump).

**Mitigacao:** Backup agendado em janela de baixa utilizacao. Replicacao via dump + restore em standby para DR basico.

### 6.3 Redis Licensing (v7.4+)

A partir do Redis 7.4, a licenca mudou de BSD para RSALv2 + SSPLv1. Isso significa:

- **Permitido:** Usar self-hosted como componente do OntoGrid
- **Proibido:** Oferecer Redis como servico managed para terceiros
- **Alternativa se necessario:** Valkey (fork BSD do Redis mantido pela Linux Foundation)

**Impacto no MVP:** Nenhum. OntoGrid usa Redis como componente interno, nao como servico oferecido a terceiros.

### 6.4 Consideracoes de Performance

#### Ingestao SCADA
- **Estimativa MVP:** ~1000 sensores x 1 leitura/minuto = ~1.4M pontos/dia
- **Limite pratico TimescaleDB single-node:** ~100k inserts/segundo
- **Margem:** Ampla para MVP (<<1% da capacidade)
- **Bottleneck potencial:** Network I/O se SCADA sources forem muitas conexoes simultaneas

#### Queries de Dashboard
- **Continuous aggregates:** Pre-computam medias horarias/diarias, queries em <100ms
- **Cache Redis:** Dashboards frequentes cacheados por 30-60 segundos
- **Bottleneck potencial:** Queries ad-hoc em janelas longas (>1 ano) sem agregacao

#### ML Processing
- **Isolation Forest:** Treinamento em ~10k pontos em <1 segundo (CPU)
- **Prophet:** Treinamento de um modelo em 2-10 segundos (CPU)
- **Bottleneck potencial:** Retreinamento simultaneo de muitos modelos
- **Mitigacao:** Celery workers distribuem carga; retreinamento escalonado (round-robin)

#### Neo4j Graph Queries
- **Traversal de 3-4 hops:** <50ms para grafos ate 100k nodes
- **Bottleneck potencial:** Queries de caminho mais longo (all shortest paths) em grafos densos
- **Mitigacao:** Limitar profundidade de traversal na UI; cache de resultados frequentes

#### Frontend Performance
- **SSR:** First Contentful Paint <1.5s para dashboards
- **TanStack Query:** Stale-while-revalidate para UX responsiva
- **Socket.io:** Alertas em <500ms do evento ao usuario
- **Bottleneck potencial:** Graficos com >10k pontos vissiveis simultaneamente
- **Mitigacao:** Downsampling temporal no backend antes de enviar ao frontend

---

## Apendice: Diagrama de Arquitetura (texto)

```
                    +------------------+
                    |   Next.js 14     |
                    |   (Frontend)     |
                    +--------+---------+
                             |
                    REST API + WebSocket
                             |
                    +--------+---------+
                    |    FastAPI       |
                    | (Backend API)    |
                    +--+-----+-----+--+
                       |     |     |
              +--------+  +--+--+  +--------+
              |           |     |           |
     +--------v---+ +-----v--+ +--v--------+
     | PostgreSQL | | Neo4j  | |  Redis    |
     | TimescaleDB| | (Graph)| | (Cache/   |
     | (SCADA TS) | |        | |  Queue)   |
     +------------+ +--------+ +-----+-----+
                                      |
                               +------v------+
                               |   Celery    |
                               |  Workers    |
                               | (ML / ETL)  |
                               +-------------+
```

---

> **Ultima atualizacao:** Marzo 2026
> **Autor:** Equipe OntoGrid
> **Status:** Aprovado para MVP
