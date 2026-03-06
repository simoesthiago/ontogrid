# Infraestrutura e Deploy - OntoGrid MVP

> OntoGrid - Plataforma Ontologica de Dados e Decisao para o Setor Eletrico Brasileiro
> MVP: Asset Health - Vigilancia de equipamentos criticos com smart alerting e health score

---

## 1. Ambientes

| Ambiente | Tecnologia | Proposito | Acesso |
|----------|-----------|-----------|--------|
| **Local/Dev** | Docker Compose | Desenvolvimento e testes locais | `localhost` |
| **Staging** | Docker Compose em VM cloud | Validacao com design partners (geradoras/transmissoras) | VPN + HTTPS |
| **Producao (pos-MVP)** | Kubernetes (EKS/GKE) | Ambiente final multi-tenant | HTTPS + WAF |

### Fluxo de Promocao

```
Local/Dev  -->  Staging (merge develop)  -->  Producao (merge main, pos-MVP)
```

- **Local/Dev**: cada desenvolvedor roda a stack completa via Docker Compose. Hot-reload habilitado para backend (uvicorn `--reload`) e frontend (Next.js fast refresh).
- **Staging**: VM cloud unica com Docker Compose. Dados anonimizados de parceiros. Utilizado para demos e validacao de features com design partners do setor eletrico.
- **Producao (pos-MVP)**: migracao para Kubernetes com Helm charts. Inclui auto-scaling, alta disponibilidade e observabilidade completa.

---

## 2. Docker Compose (Desenvolvimento)

### 2.1 Servicos

| Servico | Imagem/Build | Porta | Descricao |
|---------|-------------|-------|-----------|
| **api** | Build local (`Dockerfile.api`) | 8000 | FastAPI app - REST API, WebSocket, health checks |
| **worker** | Mesma imagem do api | - | Celery worker - processamento async (ingestao, ML, alertas) |
| **beat** | Mesma imagem do api | - | Celery beat - scheduler (coleta periodica SCADA, recalculo health score) |
| **timescaledb** | `timescale/timescaledb:latest-pg16` | 5432 | PostgreSQL + TimescaleDB - series temporais SCADA e dados relacionais |
| **neo4j** | `neo4j:5-community` | 7474, 7687 | Neo4j Community - Energy Graph Brasil (ontologia do setor eletrico) |
| **redis** | `redis:7-alpine` | 6379 | Redis 7 - cache, broker Celery, rate limiting |
| **frontend** | Build local (`Dockerfile.frontend`) | 3000 | Next.js 14 - dashboard de monitoramento e alertas |

### 2.2 Volumes

| Volume | Servico | Proposito |
|--------|---------|-----------|
| `timescale_data` | timescaledb | Persistencia de dados PostgreSQL/TimescaleDB |
| `neo4j_data` | neo4j | Persistencia do grafo Neo4j |
| `redis_data` | redis | Persistencia opcional do Redis (AOF) |

### 2.3 Networks

| Network | Driver | Servicos |
|---------|--------|----------|
| `ontogrid_network` | bridge | Todos os servicos se comunicam nesta rede interna |

Isolamento: apenas `api` (8000), `frontend` (3000) e `neo4j` (7474 para browser) expoe portas para o host. Os demais servicos sao acessiveis apenas internamente.

### 2.4 Environment Variables

Arquivo `.env.example` com todas as variaveis necessarias:

```bash
# =============================================================================
# OntoGrid - Environment Variables (.env.example)
# Copie para .env e ajuste os valores
# =============================================================================

# --- Application ---
APP_ENV=development
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
APP_VERSION=0.1.0

# --- FastAPI ---
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_RELOAD=true
CORS_ORIGINS=http://localhost:3000

# --- PostgreSQL / TimescaleDB ---
POSTGRES_USER=ontogrid
POSTGRES_PASSWORD=ontogrid_dev_2024
POSTGRES_DB=ontogrid
POSTGRES_HOST=timescaledb
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# --- Neo4j ---
NEO4J_USER=neo4j
NEO4J_PASSWORD=ontogrid_graph_2024
NEO4J_HOST=neo4j
NEO4J_BOLT_PORT=7687
NEO4J_HTTP_PORT=7474
NEO4J_URI=bolt://${NEO4J_HOST}:${NEO4J_BOLT_PORT}

# --- Redis ---
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# --- Celery ---
CELERY_BROKER_URL=redis://${REDIS_HOST}:${REDIS_PORT}/1
CELERY_RESULT_BACKEND=redis://${REDIS_HOST}:${REDIS_PORT}/2
CELERY_TASK_ALWAYS_EAGER=false

# --- Security ---
JWT_SECRET=change-me-in-production-use-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
API_KEY=dev-api-key-change-in-production

# --- ML / Analytics ---
ML_ANOMALY_THRESHOLD=0.85
ML_HEALTH_SCORE_MODEL_PATH=models/health_score_v1.pkl
ML_PROPHET_CHANGEPOINT_PRIOR=0.05
ML_PYOD_CONTAMINATION=0.05
ML_BATCH_SIZE=1000

# --- Alertas ---
ALERT_CRITICAL_THRESHOLD=90
ALERT_HIGH_THRESHOLD=70
ALERT_MEDIUM_THRESHOLD=50
ALERT_NOTIFICATION_WEBHOOK=

# --- SCADA Ingestion ---
SCADA_POLL_INTERVAL_SECONDS=300
SCADA_BATCH_SIZE=5000
SCADA_RETENTION_DAYS=730

# --- Frontend (Next.js) ---
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_NEO4J_BROWSER_URL=http://localhost:7474
```

### 2.5 docker-compose.yml completo

```yaml
# =============================================================================
# OntoGrid - Docker Compose (Desenvolvimento)
# Stack: FastAPI + TimescaleDB + Neo4j + Redis + Celery + Next.js
# =============================================================================

version: "3.9"

services:
  # ---------------------------------------------------------------------------
  # TimescaleDB - Series temporais SCADA + dados relacionais
  # ---------------------------------------------------------------------------
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: ontogrid-timescaledb
    restart: unless-stopped
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ontogrid}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ontogrid_dev_2024}
      POSTGRES_DB: ${POSTGRES_DB:-ontogrid}
    volumes:
      - timescale_data:/var/lib/postgresql/data
      - ./scripts/db/timescaledb-init.sql:/docker-entrypoint-initdb.d/001-init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ontogrid} -d ${POSTGRES_DB:-ontogrid}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - ontogrid_network

  # ---------------------------------------------------------------------------
  # Neo4j - Energy Graph Brasil (ontologia do setor eletrico)
  # ---------------------------------------------------------------------------
  neo4j:
    image: neo4j:5-community
    container_name: ontogrid-neo4j
    restart: unless-stopped
    ports:
      - "${NEO4J_HTTP_PORT:-7474}:7474"
      - "${NEO4J_BOLT_PORT:-7687}:7687"
    environment:
      NEO4J_AUTH: ${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-ontogrid_graph_2024}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_server_memory_heap_initial__size: 512m
      NEO4J_server_memory_heap_max__size: 1g
      NEO4J_server_memory_pagecache_size: 512m
    volumes:
      - neo4j_data:/data
      - ./scripts/db/neo4j-init.cypher:/var/lib/neo4j/import/init.cypher
    healthcheck:
      test: ["CMD", "neo4j", "status"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 45s
    networks:
      - ontogrid_network

  # ---------------------------------------------------------------------------
  # Redis - Cache, Celery broker, rate limiting
  # ---------------------------------------------------------------------------
  redis:
    image: redis:7-alpine
    container_name: ontogrid-redis
    restart: unless-stopped
    ports:
      - "${REDIS_PORT:-6379}:6379"
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 5s
    networks:
      - ontogrid_network

  # ---------------------------------------------------------------------------
  # API - FastAPI application
  # ---------------------------------------------------------------------------
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
      target: development
    container_name: ontogrid-api
    restart: unless-stopped
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      - APP_ENV=${APP_ENV:-development}
      - APP_DEBUG=${APP_DEBUG:-true}
      - APP_LOG_LEVEL=${APP_LOG_LEVEL:-DEBUG}
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-ontogrid}:${POSTGRES_PASSWORD:-ontogrid_dev_2024}@timescaledb:5432/${POSTGRES_DB:-ontogrid}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER:-neo4j}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD:-ontogrid_graph_2024}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - JWT_SECRET=${JWT_SECRET:-change-me-in-production-use-openssl-rand-hex-32}
      - JWT_ALGORITHM=${JWT_ALGORITHM:-HS256}
      - API_KEY=${API_KEY:-dev-api-key-change-in-production}
      - ML_ANOMALY_THRESHOLD=${ML_ANOMALY_THRESHOLD:-0.85}
      - ML_HEALTH_SCORE_MODEL_PATH=${ML_HEALTH_SCORE_MODEL_PATH:-models/health_score_v1.pkl}
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000}
    volumes:
      - ./src/backend:/app/src
      - ./models:/app/models
    depends_on:
      timescaledb:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    networks:
      - ontogrid_network

  # ---------------------------------------------------------------------------
  # Worker - Celery worker (ingestao SCADA, ML, alertas)
  # ---------------------------------------------------------------------------
  worker:
    build:
      context: .
      dockerfile: Dockerfile.api
      target: development
    container_name: ontogrid-worker
    restart: unless-stopped
    entrypoint: celery
    command: >
      -A src.core.celery_app worker
      --loglevel=${APP_LOG_LEVEL:-DEBUG}
      --concurrency=2
      --queues=default,ingestion,analytics,alerts
      -E
    environment:
      - APP_ENV=${APP_ENV:-development}
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-ontogrid}:${POSTGRES_PASSWORD:-ontogrid_dev_2024}@timescaledb:5432/${POSTGRES_DB:-ontogrid}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER:-neo4j}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD:-ontogrid_graph_2024}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - ML_ANOMALY_THRESHOLD=${ML_ANOMALY_THRESHOLD:-0.85}
      - ML_HEALTH_SCORE_MODEL_PATH=${ML_HEALTH_SCORE_MODEL_PATH:-models/health_score_v1.pkl}
      - ML_BATCH_SIZE=${ML_BATCH_SIZE:-1000}
    volumes:
      - ./src/backend:/app/src
      - ./models:/app/models
    depends_on:
      timescaledb:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ontogrid_network

  # ---------------------------------------------------------------------------
  # Beat - Celery beat scheduler (coleta periodica, recalculo health score)
  # ---------------------------------------------------------------------------
  beat:
    build:
      context: .
      dockerfile: Dockerfile.api
      target: development
    container_name: ontogrid-beat
    restart: unless-stopped
    entrypoint: celery
    command: >
      -A src.core.celery_app beat
      --loglevel=${APP_LOG_LEVEL:-INFO}
      --schedule=/tmp/celerybeat-schedule
    environment:
      - APP_ENV=${APP_ENV:-development}
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - SCADA_POLL_INTERVAL_SECONDS=${SCADA_POLL_INTERVAL_SECONDS:-300}
    volumes:
      - ./src/backend:/app/src
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - ontogrid_network

  # ---------------------------------------------------------------------------
  # Frontend - Next.js 14 dashboard
  # ---------------------------------------------------------------------------
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      target: development
    container_name: ontogrid-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
      - NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL:-ws://localhost:8000/ws}
    volumes:
      - ./src/frontend:/app/src
      - /app/node_modules
      - /app/.next
    depends_on:
      api:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    networks:
      - ontogrid_network

# =============================================================================
# Volumes
# =============================================================================
volumes:
  timescale_data:
    driver: local
  neo4j_data:
    driver: local
  redis_data:
    driver: local

# =============================================================================
# Networks
# =============================================================================
networks:
  ontogrid_network:
    driver: bridge
    name: ontogrid_network
```

---

## 3. Dockerfiles

### 3.1 Dockerfile.api (Python/FastAPI)

```dockerfile
# =============================================================================
# OntoGrid API - Multi-stage Dockerfile
# Python 3.12 + FastAPI + Celery
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Base com dependencias
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS base

# Variaveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements (cache layer)
COPY src/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Development (com hot-reload e ferramentas de debug)
# ---------------------------------------------------------------------------
FROM base AS development

# Ferramentas de desenvolvimento
COPY src/backend/requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt 2>/dev/null || true

# Copiar codigo fonte (sobrescrito por volume mount em dev)
COPY src/backend/ ./src/

# Criar usuario nao-root
RUN groupadd -r ontogrid && useradd -r -g ontogrid -d /app -s /sbin/nologin ontogrid \
    && chown -R ontogrid:ontogrid /app
USER ontogrid

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------------------------------------------------------------------------
# Stage 3: Production (imagem otimizada)
# ---------------------------------------------------------------------------
FROM base AS production

# Copiar codigo fonte
COPY src/backend/ ./src/

# Criar usuario nao-root
RUN groupadd -r ontogrid && useradd -r -g ontogrid -d /app -s /sbin/nologin ontogrid \
    && chown -R ontogrid:ontogrid /app
USER ontogrid

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3.2 Dockerfile.frontend (Next.js)

```dockerfile
# =============================================================================
# OntoGrid Frontend - Multi-stage Dockerfile
# Next.js 14 + TypeScript + Tailwind CSS
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Dependencias
# ---------------------------------------------------------------------------
FROM node:20-alpine AS deps

WORKDIR /app

# Copiar manifests de dependencias (cache layer)
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm ci --prefer-offline

# ---------------------------------------------------------------------------
# Stage 2: Development (com hot-reload)
# ---------------------------------------------------------------------------
FROM node:20-alpine AS development

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY src/frontend/ ./

EXPOSE 3000

ENV NEXT_TELEMETRY_DISABLED=1

CMD ["npm", "run", "dev"]

# ---------------------------------------------------------------------------
# Stage 3: Build (gera artefatos estaticos)
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY src/frontend/ ./

ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ---------------------------------------------------------------------------
# Stage 4: Production (imagem minima com standalone output)
# ---------------------------------------------------------------------------
FROM node:20-alpine AS production

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Criar usuario nao-root
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copiar apenas os artefatos necessarios
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

---

## 4. CI/CD (GitHub Actions)

### 4.1 Pipeline de CI

O pipeline de CI e executado em todo push e pull request. Inclui:

1. **Lint**: ruff (Python) + ESLint (TypeScript) - garante qualidade e padronizacao de codigo
2. **Testes**: pytest (backend) + Vitest (frontend) - testes unitarios e de integracao
3. **Build**: construcao das imagens Docker - valida que os Dockerfiles estao corretos
4. **Security scan**: Trivy - verifica vulnerabilidades em dependencias e imagens

### 4.2 Pipeline de CD

1. **Staging**: deploy automatico ao fazer merge para branch `develop`
2. **Producao (pos-MVP)**: deploy ao fazer merge para branch `main` com aprovacao manual

### 4.3 Workflow YAML completo

```yaml
# =============================================================================
# .github/workflows/ci.yml
# OntoGrid - Continuous Integration
# =============================================================================

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.12"
  NODE_VERSION: "20"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ---------------------------------------------------------------------------
  # Lint - Verificacao de qualidade de codigo
  # ---------------------------------------------------------------------------
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install ruff
        run: pip install ruff black

      - name: Lint Python (ruff)
        run: ruff check src/backend/

      - name: Check formatting (black)
        run: black --check src/backend/

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"
          cache-dependency-path: src/frontend/package-lock.json

      - name: Install frontend dependencies
        run: cd src/frontend && npm ci

      - name: Lint TypeScript (ESLint)
        run: cd src/frontend && npm run lint

  # ---------------------------------------------------------------------------
  # Test Backend - pytest com servicos
  # ---------------------------------------------------------------------------
  test-backend:
    name: Test Backend
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: timescale/timescaledb:latest-pg16
        env:
          POSTGRES_USER: ontogrid_test
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: ontogrid_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U ontogrid_test"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"
          cache-dependency-path: src/backend/requirements*.txt

      - name: Install dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt 2>/dev/null || true
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://ontogrid_test:test_password@localhost:5432/ontogrid_test
          REDIS_URL: redis://localhost:6379/0
          CELERY_BROKER_URL: redis://localhost:6379/1
          JWT_SECRET: test-secret-key
          APP_ENV: testing
        run: |
          cd src/backend
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing

      - name: Upload coverage
        if: github.event_name == 'pull_request'
        uses: codecov/codecov-action@v4
        with:
          files: src/backend/coverage.xml
          flags: backend

  # ---------------------------------------------------------------------------
  # Test Frontend - Vitest
  # ---------------------------------------------------------------------------
  test-frontend:
    name: Test Frontend
    runs-on: ubuntu-latest
    needs: lint

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"
          cache-dependency-path: src/frontend/package-lock.json

      - name: Install dependencies
        run: cd src/frontend && npm ci

      - name: Run tests
        run: cd src/frontend && npm run test -- --coverage

      - name: Upload coverage
        if: github.event_name == 'pull_request'
        uses: codecov/codecov-action@v4
        with:
          files: src/frontend/coverage/lcov.info
          flags: frontend

  # ---------------------------------------------------------------------------
  # Build & Push Docker Images
  # ---------------------------------------------------------------------------
  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (API)
        id: meta-api
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push API image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.api
          target: production
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta-api.outputs.tags }}
          labels: ${{ steps.meta-api.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Extract metadata (Frontend)
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push Frontend image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.frontend
          target: production
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ---------------------------------------------------------------------------
  # Security Scan - Trivy
  # ---------------------------------------------------------------------------
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name != 'pull_request'

    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy (filesystem)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: "trivy-results.sarif"
```

```yaml
# =============================================================================
# .github/workflows/cd-staging.yml
# OntoGrid - Deploy to Staging
# =============================================================================

name: CD - Staging

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/ontogrid
            git pull origin develop
            docker compose pull
            docker compose up -d --build --remove-orphans
            docker compose exec -T api alembic upgrade head
            echo "Staging deploy completed at $(date)"

      - name: Health check
        run: |
          sleep 30
          curl --fail --retry 5 --retry-delay 10 \
            https://${{ secrets.STAGING_HOST }}/health \
            || exit 1
```

---

## 5. Database Setup

### 5.1 TimescaleDB

#### Init Script (`scripts/db/timescaledb-init.sql`)

```sql
-- =============================================================================
-- OntoGrid - TimescaleDB Init Script
-- Executado automaticamente na primeira inicializacao do container
-- =============================================================================

-- Habilitar extensao TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Extensoes auxiliares
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Schema dedicado para dados de time-series
CREATE SCHEMA IF NOT EXISTS timeseries;

-- =============================================================================
-- Tabela principal de medicoes SCADA
-- =============================================================================
CREATE TABLE IF NOT EXISTS timeseries.measurements (
    time        TIMESTAMPTZ     NOT NULL,
    asset_id    UUID            NOT NULL,
    metric      TEXT            NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    quality     SMALLINT        DEFAULT 0,
    source      TEXT            DEFAULT 'scada'
);

-- Converter em hypertable (particao por tempo)
SELECT create_hypertable(
    'timeseries.measurements',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Indices para queries frequentes
CREATE INDEX IF NOT EXISTS idx_measurements_asset_metric
    ON timeseries.measurements (asset_id, metric, time DESC);

CREATE INDEX IF NOT EXISTS idx_measurements_metric_time
    ON timeseries.measurements (metric, time DESC);

-- =============================================================================
-- Tabela de alertas
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.alerts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id        UUID            NOT NULL,
    severity        VARCHAR(20)     NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    alert_type      VARCHAR(100)    NOT NULL,
    title           TEXT            NOT NULL,
    description     TEXT,
    metric          TEXT,
    value           DOUBLE PRECISION,
    threshold       DOUBLE PRECISION,
    status          VARCHAR(20)     DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved', 'dismissed')),
    created_at      TIMESTAMPTZ     DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_asset_status
    ON public.alerts (asset_id, status, created_at DESC);

-- =============================================================================
-- Tabela de health scores historicos
-- =============================================================================
CREATE TABLE IF NOT EXISTS timeseries.health_scores (
    time            TIMESTAMPTZ     NOT NULL,
    asset_id        UUID            NOT NULL,
    overall_score   DOUBLE PRECISION NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    thermal_score   DOUBLE PRECISION,
    electrical_score DOUBLE PRECISION,
    mechanical_score DOUBLE PRECISION,
    oil_score       DOUBLE PRECISION,
    model_version   TEXT            DEFAULT 'v1'
);

SELECT create_hypertable(
    'timeseries.health_scores',
    'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_health_scores_asset
    ON timeseries.health_scores (asset_id, time DESC);

-- =============================================================================
-- Continuous Aggregates para dashboards
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS timeseries.measurements_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    asset_id,
    metric,
    AVG(value)    AS avg_value,
    MIN(value)    AS min_value,
    MAX(value)    AS max_value,
    COUNT(*)      AS sample_count
FROM timeseries.measurements
GROUP BY bucket, asset_id, metric
WITH NO DATA;

-- Politica de refresh do continuous aggregate
SELECT add_continuous_aggregate_policy('timeseries.measurements_hourly',
    start_offset    => INTERVAL '3 hours',
    end_offset      => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists   => TRUE
);

-- =============================================================================
-- Politicas de retencao
-- =============================================================================
-- Dados brutos: 2 anos
SELECT add_retention_policy('timeseries.measurements',
    INTERVAL '730 days',
    if_not_exists => TRUE
);

-- Health scores: 5 anos
SELECT add_retention_policy('timeseries.health_scores',
    INTERVAL '1825 days',
    if_not_exists => TRUE
);

-- =============================================================================
-- Politica de compressao (dados com mais de 7 dias)
-- =============================================================================
ALTER TABLE timeseries.measurements SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'asset_id, metric',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('timeseries.measurements',
    compress_after => INTERVAL '7 days',
    if_not_exists => TRUE
);

RAISE NOTICE 'TimescaleDB initialization completed successfully';
```

#### Migrations com Alembic

```bash
# Estrutura de migrations
src/backend/
  alembic/
    env.py
    versions/
      001_initial_schema.py
      002_add_assets_table.py
      003_add_health_score_fields.py
  alembic.ini
```

Comandos:

```bash
# Criar nova migration
alembic revision --autogenerate -m "add_assets_table"

# Aplicar todas as migrations pendentes
alembic upgrade head

# Rollback uma migration
alembic downgrade -1

# Ver estado atual
alembic current

# Ver historico
alembic history
```

### 5.2 Neo4j

#### Init Script (`scripts/db/neo4j-init.cypher`)

```cypher
// =============================================================================
// OntoGrid - Neo4j Init Script
// Energy Graph Brasil: constraints, indexes e schema
// =============================================================================

// --- Constraints (unicidade e existencia) ---

CREATE CONSTRAINT asset_id IF NOT EXISTS
FOR (a:Asset) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT substation_id IF NOT EXISTS
FOR (s:Substation) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT transmission_line_id IF NOT EXISTS
FOR (tl:TransmissionLine) REQUIRE tl.id IS UNIQUE;

CREATE CONSTRAINT agent_id IF NOT EXISTS
FOR (ag:Agent) REQUIRE ag.id IS UNIQUE;

CREATE CONSTRAINT region_code IF NOT EXISTS
FOR (r:Region) REQUIRE r.code IS UNIQUE;

CREATE CONSTRAINT voltage_level_value IF NOT EXISTS
FOR (v:VoltageLevel) REQUIRE v.kv IS UNIQUE;

CREATE CONSTRAINT manufacturer_name IF NOT EXISTS
FOR (m:Manufacturer) REQUIRE m.name IS UNIQUE;

// --- Indexes para buscas frequentes ---

CREATE INDEX asset_type_idx IF NOT EXISTS
FOR (a:Asset) ON (a.type);

CREATE INDEX asset_status_idx IF NOT EXISTS
FOR (a:Asset) ON (a.status);

CREATE INDEX asset_health_score_idx IF NOT EXISTS
FOR (a:Asset) ON (a.health_score);

CREATE INDEX substation_name_idx IF NOT EXISTS
FOR (s:Substation) ON (s.name);

CREATE INDEX agent_name_idx IF NOT EXISTS
FOR (ag:Agent) ON (ag.name);

// --- Full-text search index ---

CREATE FULLTEXT INDEX asset_search IF NOT EXISTS
FOR (a:Asset) ON EACH [a.name, a.serial_number, a.description];
```

#### Seed Data (`scripts/db/neo4j-seed.cypher`)

```cypher
// =============================================================================
// OntoGrid - Neo4j Seed Data
// Grafo exemplo: subestacao com transformadores e equipamentos
// Dados ficticios para desenvolvimento
// =============================================================================

// --- Regioes do SIN ---
CREATE (r1:Region {code: "SE", name: "Sudeste/Centro-Oeste"})
CREATE (r2:Region {code: "S", name: "Sul"})
CREATE (r3:Region {code: "NE", name: "Nordeste"})
CREATE (r4:Region {code: "N", name: "Norte"})

// --- Niveis de tensao ---
CREATE (v500:VoltageLevel {kv: 500, label: "500 kV"})
CREATE (v230:VoltageLevel {kv: 230, label: "230 kV"})
CREATE (v138:VoltageLevel {kv: 138, label: "138 kV"})
CREATE (v69:VoltageLevel  {kv: 69,  label: "69 kV"})

// --- Fabricantes ---
CREATE (fab1:Manufacturer {name: "WEG", country: "BR"})
CREATE (fab2:Manufacturer {name: "Siemens", country: "DE"})
CREATE (fab3:Manufacturer {name: "ABB", country: "CH"})

// --- Agente (transmissora) ---
CREATE (agent1:Agent {
    id: "agt-001",
    name: "TransNorte Energia",
    type: "transmissora",
    cnpj: "12.345.678/0001-90",
    aneel_code: "TNE"
})

// --- Subestacao ---
CREATE (se1:Substation {
    id: "se-001",
    name: "SE Ribeirao Preto 500kV",
    latitude: -21.1767,
    longitude: -47.8208,
    municipality: "Ribeirao Preto",
    state: "SP",
    status: "operational",
    commissioned_at: date("2005-03-15")
})

// --- Ativos: Transformadores ---
CREATE (t1:Asset {
    id: "ast-001",
    name: "TR-01 SE Ribeirao Preto",
    type: "transformer",
    subtype: "power_transformer",
    serial_number: "WEG-TR-2005-00142",
    rated_power_mva: 300,
    health_score: 72.5,
    status: "operational",
    commissioned_at: date("2005-06-20"),
    last_maintenance: date("2024-08-10")
})

CREATE (t2:Asset {
    id: "ast-002",
    name: "TR-02 SE Ribeirao Preto",
    type: "transformer",
    subtype: "power_transformer",
    serial_number: "SIE-TR-2010-00891",
    rated_power_mva: 300,
    health_score: 88.3,
    status: "operational",
    commissioned_at: date("2010-11-05"),
    last_maintenance: date("2025-01-15")
})

// --- Ativos: Disjuntores ---
CREATE (dj1:Asset {
    id: "ast-003",
    name: "DJ-52-1 SE Ribeirao Preto",
    type: "circuit_breaker",
    subtype: "sf6_breaker",
    serial_number: "ABB-DJ-2005-03321",
    rated_voltage_kv: 500,
    health_score: 65.0,
    status: "operational",
    commissioned_at: date("2005-06-20"),
    last_maintenance: date("2024-03-22")
})

// --- Ativos: Gerador (usina vinculada) ---
CREATE (g1:Asset {
    id: "ast-004",
    name: "UG-01 UHE Exemplo",
    type: "generator",
    subtype: "hydro_generator",
    serial_number: "WEG-GE-2000-00055",
    rated_power_mw: 150,
    health_score: 91.2,
    status: "operational",
    commissioned_at: date("2000-09-01"),
    last_maintenance: date("2025-02-01")
})

// --- Linha de transmissao ---
CREATE (lt1:TransmissionLine {
    id: "lt-001",
    name: "LT 500kV Ribeirao Preto - Araraquara",
    voltage_kv: 500,
    length_km: 85.3,
    status: "operational"
})

// --- Relacionamentos ---

// Agente opera subestacao
CREATE (agent1)-[:OPERATES]->(se1)

// Subestacao contem ativos
CREATE (se1)-[:CONTAINS]->(t1)
CREATE (se1)-[:CONTAINS]->(t2)
CREATE (se1)-[:CONTAINS]->(dj1)

// Ativos fabricados por
CREATE (t1)-[:MANUFACTURED_BY]->(fab1)
CREATE (t2)-[:MANUFACTURED_BY]->(fab2)
CREATE (dj1)-[:MANUFACTURED_BY]->(fab3)
CREATE (g1)-[:MANUFACTURED_BY]->(fab1)

// Nivel de tensao
CREATE (se1)-[:HAS_VOLTAGE]->(v500)
CREATE (se1)-[:HAS_VOLTAGE]->(v230)

// Regiao
CREATE (se1)-[:LOCATED_IN]->(r1)

// Linha de transmissao conecta subestacoes
CREATE (lt1)-[:CONNECTS]->(se1)

// Disjuntor protege transformador
CREATE (dj1)-[:PROTECTS]->(t1)

// Gerador alimenta subestacao (via LT)
CREATE (g1)-[:FEEDS]->(lt1)

RETURN "Seed data loaded: 1 agent, 1 substation, 4 assets, 1 transmission line" AS result;
```

---

## 6. Monitoramento (pos-MVP ready)

### 6.1 Health Checks

Cada servico possui health check configurado no Docker Compose (ver secao 2.5). O endpoint da API:

```python
# src/backend/api/routes/health.py

from fastapi import APIRouter, Response
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint para load balancers e monitoramento."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "checks": {
            "database": await check_timescaledb(),
            "neo4j": await check_neo4j(),
            "redis": await check_redis(),
            "celery": await check_celery(),
        }
    }

    all_healthy = all(c["status"] == "ok" for c in checks["checks"].values())

    if not all_healthy:
        checks["status"] = "degraded"
        return Response(content=json.dumps(checks), status_code=503)

    return checks
```

### 6.2 Logging Estruturado (JSON)

```python
# src/backend/core/logging.py

import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatter que emite logs em JSON para facilitar ingestao em
    ferramentas como ELK, Loki ou CloudWatch."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "asset_id"):
            log_entry["asset_id"] = record.asset_id

        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry)

def setup_logging(level: str = "INFO"):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, level.upper()))
```

### 6.3 Metricas Prometheus-ready

```python
# src/backend/core/metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Metricas de negocios
health_score_gauge = Gauge(
    "ontogrid_asset_health_score",
    "Health score atual do ativo",
    ["asset_id", "asset_type"]
)

alerts_total = Counter(
    "ontogrid_alerts_total",
    "Total de alertas gerados",
    ["severity", "alert_type"]
)

ingestion_records = Counter(
    "ontogrid_ingestion_records_total",
    "Total de registros SCADA ingeridos",
    ["source"]
)

# Metricas de performance
request_duration = Histogram(
    "ontogrid_http_request_duration_seconds",
    "Duracao de requests HTTP",
    ["method", "endpoint", "status"]
)

ml_inference_duration = Histogram(
    "ontogrid_ml_inference_duration_seconds",
    "Duracao de inferencia ML",
    ["model"]
)

async def metrics_endpoint():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## 7. Seguranca

### 7.1 Secrets Management

```gitignore
# .gitignore - NUNCA commitar estes arquivos
.env
.env.local
.env.staging
.env.production
*.pem
*.key
secrets/
models/*.pkl
```

Regras:
- `.env` nunca entra no repositorio. Apenas `.env.example` com valores placeholder.
- Em staging/producao, usar secrets do Docker Swarm, Kubernetes Secrets ou servico externo (AWS Secrets Manager, HashiCorp Vault).
- JWT_SECRET deve ser gerado com `openssl rand -hex 32`.
- API_KEY deve ser unico por ambiente.

### 7.2 Network Isolation

```yaml
# Apenas servicos que precisam de acesso externo expoe portas
# No docker-compose.yml de producao, remover port mappings desnecessarios:
# - timescaledb: sem porta exposta (acesso apenas via rede interna)
# - redis: sem porta exposta
# - neo4j bolt: sem porta exposta (API faz proxy)
```

### 7.3 TLS para Producao

- Staging: Nginx reverse proxy com Let's Encrypt (certbot)
- Producao: TLS termination no ingress controller (Kubernetes) ou load balancer
- Comunicacao interna entre servicos: rede privada (sem TLS necessario dentro do cluster)

### 7.4 Backup Strategy

| Banco | Metodo | Frequencia | Retencao |
|-------|--------|------------|----------|
| TimescaleDB | `pg_dump` + WAL archiving | Diario (full) + continuo (WAL) | 30 dias (daily) + 7 dias (WAL) |
| Neo4j | `neo4j-admin database dump` | Diario | 30 dias |
| Redis | AOF + RDB snapshot | Continuo (AOF) + horario (RDB) | 7 dias |

---

## 8. Scripts Utilitarios

### 8.1 `scripts/setup.sh` - Setup inicial completo

```bash
#!/usr/bin/env bash
# =============================================================================
# OntoGrid - Setup inicial do ambiente de desenvolvimento
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo " OntoGrid - Setup do Ambiente"
echo "=========================================="

# 1. Verificar pre-requisitos
echo ""
echo "[1/6] Verificando pre-requisitos..."

command -v docker >/dev/null 2>&1 || { echo "ERRO: Docker nao encontrado. Instale em https://docs.docker.com/get-docker/"; exit 1; }
command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1 || { echo "ERRO: Docker Compose nao encontrado."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "AVISO: Python3 nao encontrado. Necessario para desenvolvimento local."; }
command -v node >/dev/null 2>&1 || { echo "AVISO: Node.js nao encontrado. Necessario para desenvolvimento local."; }

echo "  Pre-requisitos OK"

# 2. Criar .env se nao existir
echo "[2/6] Configurando variaveis de ambiente..."

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    # Gerar JWT_SECRET unico
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/change-me-in-production-use-openssl-rand-hex-32/$JWT_SECRET/" "$PROJECT_ROOT/.env"
    else
        sed -i "s/change-me-in-production-use-openssl-rand-hex-32/$JWT_SECRET/" "$PROJECT_ROOT/.env"
    fi
    echo "  .env criado com JWT_SECRET gerado automaticamente"
else
    echo "  .env ja existe, mantendo configuracao atual"
fi

# 3. Criar diretorios necessarios
echo "[3/6] Criando diretorios..."

mkdir -p "$PROJECT_ROOT/models"
mkdir -p "$PROJECT_ROOT/scripts/db"
mkdir -p "$PROJECT_ROOT/backups"

echo "  Diretorios criados"

# 4. Subir infraestrutura
echo "[4/6] Subindo containers Docker..."

cd "$PROJECT_ROOT"
docker compose up -d --build

echo "  Containers iniciados"

# 5. Aguardar servicos ficarem saudaveis
echo "[5/6] Aguardando servicos ficarem saudaveis..."

echo -n "  TimescaleDB"
for i in $(seq 1 30); do
    if docker compose exec -T timescaledb pg_isready -U ontogrid >/dev/null 2>&1; then
        echo " OK"
        break
    fi
    echo -n "."
    sleep 2
done

echo -n "  Neo4j"
for i in $(seq 1 30); do
    if docker compose exec -T neo4j neo4j status 2>/dev/null | grep -q "running"; then
        echo " OK"
        break
    fi
    echo -n "."
    sleep 3
done

echo -n "  Redis"
for i in $(seq 1 10); do
    if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        echo " OK"
        break
    fi
    echo -n "."
    sleep 1
done

# 6. Executar migrations
echo "[6/6] Executando migrations..."

docker compose exec -T api alembic upgrade head 2>/dev/null || echo "  AVISO: Alembic nao configurado ainda. Pule este passo."

echo ""
echo "=========================================="
echo " Setup completo!"
echo "=========================================="
echo ""
echo " API:      http://localhost:8000"
echo " Docs:     http://localhost:8000/docs"
echo " Frontend: http://localhost:3000"
echo " Neo4j:    http://localhost:7474"
echo ""
echo " Proximo passo: make seed (popular dados de exemplo)"
echo "=========================================="
```

### 8.2 `scripts/seed.sh` - Popular dados de exemplo

```bash
#!/usr/bin/env bash
# =============================================================================
# OntoGrid - Seed: popular bancos com dados de exemplo
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo " OntoGrid - Seed de Dados"
echo "=========================================="

# 1. Seed TimescaleDB
echo ""
echo "[1/2] Populando TimescaleDB com dados SCADA de exemplo..."

docker compose exec -T timescaledb psql -U ontogrid -d ontogrid <<'EOSQL'
-- Inserir dados SCADA simulados (ultimas 24h, a cada 5 min)
INSERT INTO timeseries.measurements (time, asset_id, metric, value, quality, source)
SELECT
    ts,
    asset_id,
    metric,
    CASE metric
        WHEN 'temperature_oil_top' THEN 55 + (random() * 30) + (EXTRACT(HOUR FROM ts) * 0.5)
        WHEN 'temperature_winding' THEN 65 + (random() * 25) + (EXTRACT(HOUR FROM ts) * 0.4)
        WHEN 'current_phase_a' THEN 280 + (random() * 40)
        WHEN 'current_phase_b' THEN 275 + (random() * 45)
        WHEN 'current_phase_c' THEN 282 + (random() * 38)
        WHEN 'voltage' THEN 500 + (random() * 10 - 5)
        WHEN 'vibration_rms' THEN 2.5 + (random() * 3)
        WHEN 'oil_moisture_ppm' THEN 15 + (random() * 10)
        ELSE random() * 100
    END,
    0,
    'seed'
FROM
    generate_series(
        NOW() - INTERVAL '24 hours',
        NOW(),
        INTERVAL '5 minutes'
    ) AS ts
CROSS JOIN (
    VALUES
        ('ast-001'::text),
        ('ast-002'::text),
        ('ast-003'::text),
        ('ast-004'::text)
) AS assets(asset_id)
CROSS JOIN (
    VALUES
        ('temperature_oil_top'),
        ('temperature_winding'),
        ('current_phase_a'),
        ('current_phase_b'),
        ('current_phase_c'),
        ('voltage'),
        ('vibration_rms'),
        ('oil_moisture_ppm')
) AS metrics(metric);

-- Inserir health scores das ultimas 24h
INSERT INTO timeseries.health_scores (time, asset_id, overall_score, thermal_score, electrical_score, mechanical_score, oil_score)
SELECT
    ts,
    asset_id::uuid,
    overall,
    overall + (random() * 10 - 5),
    overall + (random() * 8 - 4),
    overall + (random() * 12 - 6),
    overall + (random() * 6 - 3)
FROM
    generate_series(NOW() - INTERVAL '24 hours', NOW(), INTERVAL '1 hour') AS ts
CROSS JOIN (
    VALUES
        ('ast-001', 72.5),
        ('ast-002', 88.3),
        ('ast-003', 65.0),
        ('ast-004', 91.2)
) AS assets(asset_id, overall);

-- Inserir alertas de exemplo
INSERT INTO public.alerts (asset_id, severity, alert_type, title, description, metric, value, threshold, status) VALUES
    ('ast-001', 'high', 'thermal_anomaly', 'Temperatura elevada TR-01', 'Temperatura do oleo acima do limite operativo', 'temperature_oil_top', 92.3, 85.0, 'open'),
    ('ast-003', 'medium', 'vibration_anomaly', 'Vibracao acima do normal DJ-52-1', 'Nivel de vibracao RMS acima do baseline', 'vibration_rms', 5.8, 4.5, 'open'),
    ('ast-001', 'critical', 'health_score_drop', 'Queda abrupta de health score TR-01', 'Health score caiu 15 pontos nas ultimas 6 horas', 'health_score', 72.5, 80.0, 'acknowledged'),
    ('ast-002', 'low', 'scheduled_maintenance', 'Manutencao preventiva TR-02', 'Proxima manutencao programada em 30 dias', NULL, NULL, NULL, 'open');

SELECT
    'Seed TimescaleDB completo: ' ||
    (SELECT COUNT(*) FROM timeseries.measurements) || ' medicoes, ' ||
    (SELECT COUNT(*) FROM timeseries.health_scores) || ' health scores, ' ||
    (SELECT COUNT(*) FROM public.alerts) || ' alertas'
AS result;
EOSQL

echo "  TimescaleDB populado"

# 2. Seed Neo4j
echo "[2/2] Populando Neo4j com grafo de exemplo..."

docker compose exec -T neo4j cypher-shell -u neo4j -p ontogrid_graph_2024 \
    < "$PROJECT_ROOT/scripts/db/neo4j-seed.cypher"

echo "  Neo4j populado"

echo ""
echo "=========================================="
echo " Seed completo!"
echo " Dados de exemplo carregados nos dois bancos."
echo "=========================================="
```

### 8.3 `scripts/backup.sh` - Backup dos bancos

```bash
#!/usr/bin/env bash
# =============================================================================
# OntoGrid - Backup dos bancos de dados
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo " OntoGrid - Backup ($TIMESTAMP)"
echo "=========================================="

mkdir -p "$BACKUP_DIR"

# 1. Backup TimescaleDB
echo ""
echo "[1/2] Backup TimescaleDB..."

docker compose exec -T timescaledb pg_dump \
    -U ontogrid \
    -d ontogrid \
    --format=custom \
    --compress=9 \
    > "$BACKUP_DIR/timescaledb_${TIMESTAMP}.dump"

TSDB_SIZE=$(du -h "$BACKUP_DIR/timescaledb_${TIMESTAMP}.dump" | cut -f1)
echo "  TimescaleDB backup: $TSDB_SIZE -> timescaledb_${TIMESTAMP}.dump"

# 2. Backup Neo4j
echo "[2/2] Backup Neo4j..."

docker compose exec -T neo4j neo4j-admin database dump neo4j \
    --to-stdout > "$BACKUP_DIR/neo4j_${TIMESTAMP}.dump" 2>/dev/null \
    || docker compose exec -T neo4j cypher-shell -u neo4j -p ontogrid_graph_2024 \
        "CALL apoc.export.cypher.all(null, {stream:true}) YIELD cypherStatements RETURN cypherStatements" \
        > "$BACKUP_DIR/neo4j_${TIMESTAMP}.cypher"

echo "  Neo4j backup concluido"

# 3. Limpar backups antigos (manter ultimos 30 dias)
echo ""
echo "Limpando backups com mais de 30 dias..."
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.cypher" -mtime +30 -delete 2>/dev/null || true

echo ""
echo "=========================================="
echo " Backup concluido!"
echo " Arquivos em: $BACKUP_DIR/"
echo "=========================================="
```

### 8.4 `scripts/reset.sh` - Reset ambiente dev

```bash
#!/usr/bin/env bash
# =============================================================================
# OntoGrid - Reset completo do ambiente de desenvolvimento
# CUIDADO: Remove todos os dados locais!
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo " OntoGrid - Reset do Ambiente"
echo "=========================================="
echo ""
echo "ATENCAO: Isso vai remover TODOS os dados locais!"
echo ""
read -p "Tem certeza? (digite 'sim' para confirmar): " confirm

if [ "$confirm" != "sim" ]; then
    echo "Operacao cancelada."
    exit 0
fi

echo ""
echo "[1/4] Parando containers..."
cd "$PROJECT_ROOT"
docker compose down -v --remove-orphans

echo "[2/4] Removendo volumes..."
docker volume rm ontogrid_timescale_data ontogrid_neo4j_data ontogrid_redis_data 2>/dev/null || true

echo "[3/4] Limpando imagens locais..."
docker compose build --no-cache

echo "[4/4] Recriando ambiente..."
"$SCRIPT_DIR/setup.sh"

echo ""
echo "=========================================="
echo " Reset completo! Ambiente limpo e funcional."
echo "=========================================="
```

---

## 9. Requisitos de Hardware

### 9.1 Desenvolvimento (Local)

| Recurso | Minimo | Recomendado |
|---------|--------|-------------|
| **RAM** | 8 GB | 16 GB |
| **CPU** | 4 cores | 8 cores |
| **Disco** | 20 GB livre | 50 GB SSD |
| **Docker** | Docker Desktop 4.x | Docker Desktop 4.x |

Distribuicao aproximada de memoria (com todos os servicos rodando):

| Servico | RAM estimada |
|---------|-------------|
| TimescaleDB | 1-2 GB |
| Neo4j | 1-2 GB |
| Redis | 256 MB |
| API (FastAPI) | 512 MB |
| Worker (Celery) | 512 MB - 1 GB |
| Beat (Celery) | 128 MB |
| Frontend (Next.js) | 512 MB |
| **Total** | **~4-6 GB** |

### 9.2 Staging (VM Cloud)

| Recurso | Especificacao | Equivalente Cloud |
|---------|--------------|-------------------|
| **RAM** | 16 GB | AWS: `t3.xlarge` / GCP: `e2-standard-4` |
| **CPU** | 4 vCPUs | |
| **Disco** | 100 GB SSD | GP3 / SSD persistente |
| **Rede** | 1 Gbps | VPC com IP fixo |

### 9.3 Producao (pos-MVP, Kubernetes)

| Recurso | Especificacao | Notas |
|---------|--------------|-------|
| **RAM** | 32 GB+ (total do cluster) | Distribuido entre nos |
| **CPU** | 8+ vCPUs (total do cluster) | Auto-scaling habilitado |
| **Disco** | 500 GB+ SSD | IOPS provisionado para TimescaleDB |
| **Rede** | 10 Gbps intra-cluster | Load balancer externo |

Pods recomendados para Kubernetes:

| Componente | Replicas | CPU Request | Memory Request |
|-----------|----------|-------------|----------------|
| API | 2-4 (HPA) | 500m | 512Mi |
| Worker | 2-4 | 1000m | 1Gi |
| Beat | 1 | 100m | 128Mi |
| Frontend | 2 (HPA) | 250m | 256Mi |
| TimescaleDB | 1 (StatefulSet) | 2000m | 4Gi |
| Neo4j | 1 (StatefulSet) | 1000m | 2Gi |
| Redis | 1 (StatefulSet) | 250m | 512Mi |

---

## 10. Makefile

```makefile
# =============================================================================
# OntoGrid - Makefile
# Comandos uteis para desenvolvimento
# =============================================================================

.PHONY: help up down restart build logs test lint migrate seed backup reset clean status

.DEFAULT_GOAL := help

# Cores para output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RESET  := \033[0m

help: ## Mostrar esta ajuda
	@echo ""
	@echo "$(CYAN)OntoGrid - Comandos Disponiveis$(RESET)"
	@echo "================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Docker Compose
# ---------------------------------------------------------------------------

up: ## Subir todos os servicos
	docker compose up -d
	@echo ""
	@echo "$(GREEN)Servicos iniciados!$(RESET)"
	@echo "  API:      http://localhost:8000"
	@echo "  Docs:     http://localhost:8000/docs"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Neo4j:    http://localhost:7474"

down: ## Parar todos os servicos
	docker compose down

restart: ## Reiniciar todos os servicos
	docker compose restart

build: ## Rebuildar imagens Docker
	docker compose build --no-cache

logs: ## Ver logs de todos os servicos (follow)
	docker compose logs -f --tail=100

logs-api: ## Ver logs da API
	docker compose logs -f --tail=100 api

logs-worker: ## Ver logs do Celery worker
	docker compose logs -f --tail=100 worker

status: ## Ver status dos containers
	docker compose ps

# ---------------------------------------------------------------------------
# Desenvolvimento
# ---------------------------------------------------------------------------

test: ## Rodar todos os testes (backend + frontend)
	@echo "$(CYAN)=== Backend Tests ===$(RESET)"
	docker compose exec -T api pytest tests/ -v --tb=short
	@echo ""
	@echo "$(CYAN)=== Frontend Tests ===$(RESET)"
	docker compose exec -T frontend npm run test

test-backend: ## Rodar testes do backend
	docker compose exec -T api pytest tests/ -v --tb=short --cov=src

test-frontend: ## Rodar testes do frontend
	docker compose exec -T frontend npm run test

lint: ## Rodar linters (ruff + eslint)
	@echo "$(CYAN)=== Python Lint (ruff) ===$(RESET)"
	docker compose exec -T api ruff check src/
	@echo ""
	@echo "$(CYAN)=== TypeScript Lint (eslint) ===$(RESET)"
	docker compose exec -T frontend npm run lint

format: ## Formatar codigo (black + prettier)
	docker compose exec -T api black src/
	docker compose exec -T frontend npx prettier --write "src/**/*.{ts,tsx}"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate: ## Executar migrations do Alembic
	docker compose exec -T api alembic upgrade head

migrate-create: ## Criar nova migration (uso: make migrate-create MSG="descricao")
	docker compose exec -T api alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Reverter ultima migration
	docker compose exec -T api alembic downgrade -1

seed: ## Popular bancos com dados de exemplo
	bash scripts/seed.sh

backup: ## Fazer backup dos bancos
	bash scripts/backup.sh

db-shell: ## Abrir shell do TimescaleDB
	docker compose exec timescaledb psql -U ontogrid -d ontogrid

neo4j-shell: ## Abrir Cypher shell do Neo4j
	docker compose exec neo4j cypher-shell -u neo4j -p ontogrid_graph_2024

redis-cli: ## Abrir CLI do Redis
	docker compose exec redis redis-cli

# ---------------------------------------------------------------------------
# Setup e Manutencao
# ---------------------------------------------------------------------------

setup: ## Setup inicial completo
	bash scripts/setup.sh

reset: ## Reset completo do ambiente (CUIDADO: remove dados!)
	bash scripts/reset.sh

clean: ## Remover containers, volumes e imagens orfas
	docker compose down -v --remove-orphans
	docker image prune -f

# ---------------------------------------------------------------------------
# Producao / Staging
# ---------------------------------------------------------------------------

build-prod: ## Build imagens de producao
	docker build -f Dockerfile.api --target production -t ontogrid-api:latest .
	docker build -f Dockerfile.frontend --target production -t ontogrid-frontend:latest .

health: ## Verificar health de todos os servicos
	@echo "API:         $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
	@echo "Frontend:    $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000)"
	@echo "TimescaleDB: $$(docker compose exec -T timescaledb pg_isready -U ontogrid && echo 'OK' || echo 'FAIL')"
	@echo "Redis:       $$(docker compose exec -T redis redis-cli ping)"
	@echo "Neo4j:       $$(docker compose exec -T neo4j neo4j status 2>/dev/null || echo 'checking...')"
```

---

## Referencia Rapida

```bash
# Primeiro uso
make setup              # Setup completo (Docker + DBs + .env)
make seed               # Popular dados de exemplo

# Dia a dia
make up                 # Subir tudo
make logs               # Ver logs
make test               # Rodar testes
make lint               # Verificar codigo
make down               # Parar tudo

# Database
make migrate            # Aplicar migrations
make db-shell           # Abrir psql
make neo4j-shell        # Abrir cypher-shell
make backup             # Backup dos bancos

# Troubleshooting
make status             # Ver containers
make health             # Health check de todos servicos
make restart            # Reiniciar tudo
make reset              # Comecar do zero
```
