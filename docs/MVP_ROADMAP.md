# MVP Roadmap - OntoGrid v0.1

## 1. Meta da rodada atual

Sair de documentação dispersa para um produto codável com:

- escopo fechado;
- contratos estáveis;
- scaffold funcional de backend e frontend;
- infra local pronta;
- sequência clara de implementação.

## 2. Fase 0 - Consolidação do repo

- consolidar docs;
- fechar contratos de API;
- fechar modelo de dados;
- criar bootstrap técnico;
- criar skill local do projeto.

Saída esperada: repositório pronto para iniciar desenvolvimento sem rediscutir stack e escopo.

## 3. Sprint 1 - Core operacional

- autenticação e contexto de tenant;
- CRUD de ativos;
- cadastro de measurement points;
- ingestão em lote;
- leitura de medições por ativo;
- tela inicial de ativos;
- persistência real em PostgreSQL/TimescaleDB.

Critério de aceite:

- um tenant consegue autenticar;
- cadastrar ativos;
- ingerir medições;
- ver a linha do tempo básica do ativo.

## 4. Sprint 2 - Score, alerta e ação

- cálculo de health score v0;
- detecção básica de anomalias;
- geração de alertas;
- reconhecimento de alerta;
- criação de caso simples;
- telas de alertas e casos.

Critério de aceite:

- medições alteram score;
- score ruim abre alerta;
- alerta pode virar caso.

## 5. Sprint 3 - Grafo básico e endurecimento

- sincronização mínima do Energy Graph;
- rotas `neighbors` e `impact`;
- integração do frontend com contexto de topologia;
- testes de fluxo principal;
- limpeza de backlog técnico do scaffold.

Critério de aceite:

- um ativo devolve vizinhança;
- um ativo crítico devolve impacto;
- o fluxo principal fica estável de ponta a ponta.

## 6. Fase 1.1 - Pós-MVP imediato

- WebSocket para alertas.
- notificações por email.
- importação em massa de ativos.
- supressão básica de alarmes.
- melhoria visual do dashboard.

## 7. Fase posterior

- GraphQL.
- forecasting.
- mobile.
- mapa geográfico.
- knowledge base e SOPs ricos.
- multi-tenant em escala alta.
