# MVP Roadmap - OntoGrid Energy Data Hub

## 1. Meta da rodada atual

Sair de documentacao dispersa para um produto codavel com:

- escopo publico fechado;
- contratos estaveis para o hub de dados;
- arquitetura coerente com ontologia, visualizacao e copilot;
- infra local pronta;
- sequencia clara de implementacao.

## 2. Fase 0 - Consolidacao documental

- consolidar a visao publica-first;
- fechar contratos da API publica;
- fechar modelo de dados canonico;
- alinhar arquitetura tecnica com ingestao regulatoria;
- reclassificar o slice enterprise atual como fase 2.

Saida esperada: repositorio pronto para iniciar desenvolvimento sem rediscutir se o MVP depende ou nao de dados do cliente.

## 3. Fase 1 - Energy Data Hub publico

### Sprint 1 - Fontes e catalogo

- registro de fontes ANEEL, ONS e CCEE;
- catalogo de datasets publicos;
- modelo de versao e lineage;
- refresh inicial por pull agendado e download versionado.

Criterio de aceite:

- pelo menos um dataset prioritario por fonte esta catalogado;
- cada dataset expone metadados, frequencia e ultima versao;
- refresh publica rastreabilidade minima.

### Sprint 2 - Series, grafo e visualizacao

- consulta de series e observacoes;
- Energy Graph publico com entidades e relacoes iniciais;
- endpoints de insights para UI;
- telas base de catalogo, dataset e entidade.

Criterio de aceite:

- um usuario navega do catalogo ate a serie;
- uma entidade publica devolve vizinhanca e contexto;
- a UI consegue renderizar dados e insights sem onboarding de cliente.

### Sprint 3 - Copilot analitico grounded

- endpoint de copilot sobre datasets e grafo;
- citacoes de fontes, datasets e versoes;
- resumos operacionais e regulatorios baseados nos dados publicos;
- cache e observabilidade minima da experiencia.

Criterio de aceite:

- o copilot responde perguntas grounded;
- a resposta referencia datasets e versoes;
- o fluxo fim a fim funciona apenas com dados publicos.

## 4. Fase 2 - Enterprise Data Plane

- tenancy e segregacao de dados privados;
- conectores para SCADA, ERP, OMS, CMMS e GIS;
- federacao entre contexto publico e dados do cliente;
- primeiro app enterprise: Vigilancia Operacional de Ativos.

Criterio de aceite:

- um tenant conecta ao menos uma fonte privada;
- o grafo enterprise combina contexto publico e privado;
- o app de vigilancia opera sem quebrar o contrato do hub publico.

## 5. Fase 3 - Suites operacionais e copilots

- Reliability / Outage Intelligence;
- Smart Alerting Copilot;
- Technical Issue Resolution Assistant;
- Field Ops Assistant.

Criterio de aceite:

- cada modulo reutiliza ontologia, lineage e APIs da plataforma;
- a IA continua grounded e auditavel;
- os modulos nao reconstroem semantica do zero.

## 6. Fases posteriores

- federated benchmarking / clean room;
- expansao para EPE e outras fontes;
- workflows mais ricos de compliance e operacao;
- automacao mais profunda em cenarios enterprise.
