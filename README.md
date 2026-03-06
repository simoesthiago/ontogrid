# OntoGrid - Sistema Operacional de Dados e Decisao para o Setor Eletrico

## Visao Geral

OntoGrid e uma plataforma ontologica de dados e decisao para o setor eletrico brasileiro. Resolve o problema de fragmentacao semantica transformando dados dispersos (ONS, CCEE, ANEEL, SCADA, ERP, GIS) em decisoes audtaveis com semantica comum, governanca e seguranca.

## MVP: Asset Health (Equipment Surveillance & Smart Alerting)

O MVP foca em **vigilancia de equipamentos criticos** para geradoras e transmissoras:

- **Smart Alerting**: alertas inteligentes baseados em anomalias com contexto historico
- **Anomaly Detection**: deteccao de anomalias em series temporais SCADA
- **Health Score**: score de saude por equipamento critico
- **Cases/SOPs**: gestao de casos e procedimentos operacionais

### ROI Direto
Evitar **uma falha de transformador** (R$1-5M) paga a plataforma por anos.

## Arquitetura (8 Camadas)

```
H - Colaboracao Multiempresa (futuro)
G - IA Aplicada e Governada
F - Workflows e Automacao
E - Motor Analitico
D - Data Products Engine
C - Governanca e Seguranca
B - Energy Graph Brasil (Ontologia + MDM)
A - Conectores e Ingestao
```

### Escopo do MVP (Camadas ativas)
- **Camada A**: Conectores SCADA/historian + cadastro de ativos
- **Camada B**: Energy Graph v0.1 (dominio fisico + operacao)
- **Camada C**: Governanca basica (RBAC, audit log)
- **Camada D**: Data products bronze/silver para series temporais
- **Camada E**: Deteccao de anomalias + health score
- **Camada F**: Cases basicos + SOPs
- **Camada G**: Classificacao automatica de alertas

## Estrutura do Projeto

```
ontogrid/
├── docs/                    # Documentacao estrategica e tecnica
├── src/
│   ├── backend/             # API FastAPI + servicos
│   │   ├── api/             # Rotas e endpoints
│   │   ├── core/            # Config, seguranca, deps
│   │   ├── models/          # Modelos SQLAlchemy/Pydantic
│   │   ├── services/        # Logica de negocio
│   │   ├── graph/           # Energy Graph (Neo4j)
│   │   ├── ingestion/       # Pipeline de ingestao
│   │   ├── analytics/       # Motor analitico + ML
│   │   └── workflows/       # Cases e automacoes
│   └── frontend/            # Next.js dashboard
│       ├── app/             # App router pages
│       ├── components/      # Componentes React
│       └── lib/             # Utils e API client
├── config/                  # Configs de infra e deploy
├── .claude/                 # Claude Code configs
└── README.md
```

## Tech Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend API | Python 3.12 + FastAPI |
| Time-Series DB | TimescaleDB (PostgreSQL) |
| Graph DB | Neo4j (Energy Graph) |
| Cache/Queue | Redis + Celery |
| ML/Analytics | scikit-learn, Prophet, PyOD |
| Frontend | Next.js 14 + TypeScript + Tailwind |
| Visualizacao | Recharts + React Flow (grafo) |
| Infra | Docker Compose (dev) / K8s (prod) |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# Clone
git clone https://github.com/simoesthiago/ontogrid.git
cd ontogrid

# Backend
cd src/backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd src/frontend
npm install
npm run dev
```

## Documentacao

- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Arquitetura Tecnica](docs/ARCHITECTURE.md)
- [Tech Stack](docs/TECH_STACK.md)
- [Modelo de Dados](docs/DATA_MODEL.md)
- [API Spec](docs/API_SPEC.md)
- [User Stories](docs/USER_STORIES.md)
- [Infraestrutura](docs/INFRA_DEPLOY.md)
- [Pipeline de Ingestao](docs/DATA_INGESTION.md)

## Licenca

Proprietary - OntoGrid 2026
