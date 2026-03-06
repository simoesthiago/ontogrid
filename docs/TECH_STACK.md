# Tech Stack - OntoGrid MVP v0.1

Este documento registra a stack mínima suportada pelo baseline atual. Onde fizer sentido, ele usa a referência oficial mais recente disponível em 2026-03-06.

## 1. Stack alvo

| Camada | Escolha | Status |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Implementar agora |
| Banco operacional | PostgreSQL 16 + TimescaleDB 2.x | Implementar agora |
| Grafo | Neo4j 5.x | Implementar agora |
| Cache | Redis 7.x | Implementar agora |
| Frontend | Next.js 16 + React 19 | Implementar agora |
| Testes backend | pytest | Implementar agora |
| Testes frontend | Vitest | Preparado, opcional na primeira rodada |
| Infra local | Docker Compose | Implementar agora |

## 2. Referências oficiais usadas

- Next.js docs: [nextjs.org/docs](https://nextjs.org/docs)
- React 19 announcement: [react.dev/blog/2024/12/05/react-19](https://react.dev/blog/2024/12/05/react-19)
- FastAPI package page: [pypi.org/project/fastapi](https://pypi.org/project/fastapi/)

Observações:

- A documentação oficial do Next.js expõe a série 16 como linha atual.
- React 19 já e estável.
- O PyPI do FastAPI publica a linha atual do framework; o bootstrap usa uma faixa compatível com a série vigente, sem depender de pin aspiracional espalhado em docs.

## 3. Decisões por camada

### Backend

- Python 3.12 para manter ecossistema atual e previsível.
- FastAPI para API REST, validação e documentação automática.
- Pydantic v2 para contratos.
- SQLAlchemy e Alembic entram como base da persistência real.

### Dados

- PostgreSQL/TimescaleDB centraliza dados operacionais e séries temporais.
- Neo4j fica reservado à topologia e ao impacto.
- Redis entra como componente pequeno e utilitário, nao como backbone da plataforma.

### Frontend

- Next.js App Router.
- React 19.
- TypeScript em modo estrito.
- CSS simples no scaffold; um design system completo fica para a evolução.

## 4. O que saiu da stack inicial

- GraphQL e Strawberry.
- Socket.io como contrato padrão.
- Prophet.
- PyOD.
- Kafka.
- Kubernetes no primeiro corte.

## 5. Dependências mínimas do bootstrap

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

## 6. Critério para novas dependências

Uma dependência nova só deve entrar se:

- eliminar trabalho recorrente relevante;
- reduzir risco técnico claro;
- ou materializar um requisito do v0.1 já documentado.

Se a dependência suportar apenas uma visão futura, ela deve ficar fora do bootstrap.
