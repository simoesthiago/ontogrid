# User Stories - OntoGrid MVP v0.1

## 1. Personas prioritárias

### Carlos - Engenheiro de manutenção

Quer priorizar ativos em risco a partir de dados operacionais.

### Ana - Operadora

Quer saber quais alertas exigem ação imediata.

### Thiago - Administrador do sistema

Quer configurar o tenant, cadastrar ativos e garantir que a ingestão funcione.

## 2. Must Have do v0.1

| ID | Story | Tela principal | Endpoint principal | Entidade |
|---|---|---|---|---|
| US-001 | Como administrador, quero autenticar no sistema para operar dentro do meu tenant | Login | `POST /api/v1/auth/login` | `user` |
| US-002 | Como administrador, quero cadastrar ativos para iniciar o monitoramento | Ativos | `POST /api/v1/assets` | `asset` |
| US-003 | Como engenheiro, quero listar ativos com contexto mínimo de saúde | Ativos | `GET /api/v1/assets` | `asset` |
| US-004 | Como engenheiro, quero abrir o detalhe de um ativo e consultar suas medições | Detalhe do ativo | `GET /api/v1/assets/{asset_id}` e `GET /api/v1/assets/{asset_id}/measurements` | `asset`, `measurement` |
| US-005 | Como administrador, quero enviar um lote de medições para alimentar o sistema | Ingestão | `POST /api/v1/ingestion/jobs` | `ingestion_job`, `measurement` |
| US-006 | Como engenheiro, quero consultar o health score atual e recente do ativo | Detalhe do ativo | `GET /api/v1/assets/{asset_id}/health` | `health_score` |
| US-007 | Como operadora, quero listar alertas abertos para saber o que exige ação | Alertas | `GET /api/v1/alerts` | `alert` |
| US-008 | Como operadora, quero reconhecer um alerta para registrar que o time assumiu a ocorrência | Alertas | `POST /api/v1/alerts/{alert_id}/ack` | `alert` |
| US-009 | Como engenheiro, quero criar um caso simples a partir de um alerta | Casos | `POST /api/v1/cases` | `case` |
| US-010 | Como engenheiro, quero ver vizinhos e impacto do ativo no Energy Graph | Detalhe do ativo | `GET /api/v1/graph/assets/{asset_id}/neighbors` e `GET /api/v1/graph/assets/{asset_id}/impact` | Grafo |

## 3. Critérios de aceite resumidos

### US-001

- token JWT retorna `tenant_id`;
- usuário nao acessa dados de outro tenant.

### US-002 e US-003

- ativo criado aparece na listagem do próprio tenant;
- listagem aceita filtro por `asset_type`, `status` e busca textual.

### US-004

- detalhe do ativo traz cadastro mínimo;
- medições retornam ordenadas por tempo.

### US-005

- job retorna identificador e status;
- registros inválidos são contabilizados sem derrubar o job inteiro.

### US-006

- resposta traz score, banda e data de cálculo;
- score reflete regras documentadas no modelo.

### US-007 e US-008

- alertas abertos podem ser filtrados por severidade e status;
- reconhecimento e idempotente.

### US-009

- caso pode ser criado com `alert_id`;
- caso inicia com status `open`.

### US-010

- vizinhança devolve nós e relações básicas;
- impacto devolve o subconjunto estimado afetado.

## 4. Stories pós-v0.1

- notificações por email e SMS;
- WebSocket para alertas;
- supressão de alarmes;
- mobile;
- mapa geográfico;
- SOPs e knowledge base ricos;
- forecasting e análises avançadas.
