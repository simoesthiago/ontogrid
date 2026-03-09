# Tech Stack - OntoGrid MVP publico v1

Este documento registra a stack minima suportada pelo baseline atual. Onde fizer sentido, ele usa a referencia oficial mais recente disponivel em 2026-03-06.

## 1. Stack alvo

| Camada | Escolha | Status |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Implementar agora |
| Metadados e series | PostgreSQL 16 + TimescaleDB 2.x | Implementar agora |
| Grafo | Neo4j 5.x | Implementar agora |
| Cache | Redis 7.x | Implementar agora |
| Frontend | Next.js 16 + React 19 | Implementar agora |
| Testes backend | pytest | Implementar agora |
| Testes frontend | Vitest | Preparado, opcional na primeira rodada |
| Infra local | Docker Compose | Implementar agora |

## 2. Referencias oficiais usadas

- Next.js docs: [nextjs.org/docs](https://nextjs.org/docs)
- React 19 announcement: [react.dev/blog/2024/12/05/react-19](https://react.dev/blog/2024/12/05/react-19)
- FastAPI package page: [pypi.org/project/fastapi](https://pypi.org/project/fastapi/)

Observacoes:

- A documentacao oficial do Next.js expoe a serie 16 como linha atual.
- React 19 ja e estavel.
- O PyPI do FastAPI publica a linha atual do framework; o bootstrap usa uma faixa compativel com a serie vigente, sem depender de pin aspiracional espalhado em docs.

## 3. Decisoes por camada

### Backend

- Python 3.12 para manter ecossistema atual e previsivel.
- FastAPI para API REST, validacao e documentacao automatica.
- Pydantic v2 para contratos.
- SQLAlchemy e Alembic entram como base da persistencia real.

### Dados

- PostgreSQL/TimescaleDB centraliza fontes, datasets, versoes, series e observacoes.
- Neo4j projeta a ontologia e o Energy Graph publico.
- Redis entra como cache e apoio ao copilot, nao como backbone da plataforma.

### Frontend

- Next.js App Router.
- React 19.
- TypeScript em modo estrito.
- CSS simples no scaffold; um design system completo fica para a evolucao.

## 4. O que saiu da stack inicial

- GraphQL e Strawberry.
- Socket.io como contrato padrao.
- Prophet.
- PyOD.
- Kafka.
- Kubernetes no primeiro corte.
- OPC-UA e conectores privados como requisito do MVP publico.

## 5. Dependencias minimas do bootstrap

### Backend

- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `sqlalchemy`
- `alembic`
- `asyncpg`
- `redis`
- `neo4j`
- `pytest`
- `httpx`

### Frontend

- `next`
- `react`
- `react-dom`
- `typescript`
- `eslint`

## 6. Criterio para novas dependencias

Uma dependencia nova so deve entrar se:

- eliminar trabalho recorrente relevante;
- reduzir risco tecnico claro;
- ou materializar um requisito do MVP publico ja documentado.

Se a dependencia suportar apenas uma visao enterprise futura, ela deve ficar fora do bootstrap inicial.
