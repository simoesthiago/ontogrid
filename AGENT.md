# CLAUDE.md - OntoGrid Project Context

## Projeto
OntoGrid - Plataforma Ontologica de Dados e Decisao para o Setor Eletrico Brasileiro.

## MVP Atual: Asset Health
Vigilancia de equipamentos criticos (transformadores, geradores, disjuntores) com smart alerting, deteccao de anomalias e health score. Foco em geradoras e transmissoras.

## Contexto de Dominio
- Setor eletrico brasileiro: ONS (operador), CCEE (comercializacao), ANEEL (regulador)
- Entidades principais: ativos (transformadores, geradores), subestacoes, linhas, agentes
- Series temporais SCADA: temperatura, vibracoes, corrente, tensao, oleo isolante
- Indicadores regulatorios: DEC/FEC, disponibilidade, indisponibilidade

## Arquitetura
- 8 camadas (A-H), MVP usa A, B, C, D, E, F, G parcialmente
- Energy Graph Brasil: ontologia em Neo4j que unifica entidades do setor
- Backend: Python 3.12 + FastAPI
- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- DBs: TimescaleDB (time-series), Neo4j (grafo), Redis (cache)
- ML: scikit-learn, Prophet, PyOD para anomalias
- Queue: Celery + Redis

## Estrutura de Pastas
```
src/backend/         # FastAPI app
  api/               # Rotas REST
  core/              # Config, security, database
  models/            # SQLAlchemy + Pydantic schemas
  services/          # Business logic
  graph/             # Neo4j Energy Graph
  ingestion/         # Data pipeline connectors
  analytics/         # ML models, anomaly detection
  workflows/         # Case management, SOPs
src/frontend/        # Next.js app
  app/               # App router
  components/        # React components
  lib/               # API client, utils
```

## Convencoes de Codigo

### Backend (Python)
- Python 3.12+, type hints obrigatorios
- FastAPI com Pydantic v2 para validacao
- Async/await para I/O (database, HTTP)
- Nomenclatura: snake_case para funcoes/variaveis, PascalCase para classes
- Docstrings em portugues para logica de negocio, ingles para infra
- Testes com pytest + pytest-asyncio
- Linting: ruff
- Formatacao: black

### Frontend (TypeScript)
- Next.js 14 App Router
- TypeScript strict mode
- Componentes funcionais com hooks
- Tailwind CSS para estilos
- Nomenclatura: camelCase variaveis, PascalCase componentes
- Testes com Vitest + Testing Library
- Linting: ESLint + Prettier

### Database
- Migrations com Alembic (PostgreSQL/TimescaleDB)
- Neo4j Cypher queries em arquivos .cypher separados
- Naming: tabelas snake_case plural (assets, measurements)

### Git
- Conventional commits: feat:, fix:, docs:, refactor:, test:
- Branch naming: feature/, fix/, docs/
- PR com descricao e test plan

## Comandos Uteis
```bash
# Backend
cd src/backend && uvicorn main:app --reload --port 8000
pytest tests/ -v
ruff check .
black .

# Frontend
cd src/frontend && npm run dev
npm run test
npm run lint
npm run build

# Docker
docker-compose up -d  # Sobe TimescaleDB + Neo4j + Redis
docker-compose down

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "descricao"
```

## APIs Externas Relevantes
- ONS Dados Abertos: https://dados.ons.org.br/
- CCEE: dados de PLD e mercado
- ANEEL SIGA: cadastro de empreendimentos
- BDGD: base georreferenciada de distribuidoras

## Regras de Negocio Importantes
- Hora operativa != hora civil (ONS usa D+1 00:00 a D+1 00:00)
- PLD tem retificacoes periodicas - sempre versionar
- Resolucao de identidade: mesmo ativo tem IDs diferentes entre ONS/CCEE/ANEEL
- Health score: 0-100, baseado em multiplas variaveis SCADA + historico de manutencao
- Alertas: Critico (>90), Alto (70-90), Medio (50-70), Baixo (<50)
