# MVP Roadmap - Asset Health

## 1. Visao Geral do MVP

### Proposta de Valor

O modulo **Asset Health** e o primeiro produto da plataforma OntoGrid. Seu objetivo e fornecer vigilancia inteligente de equipamentos criticos (transformadores de potencia, disjuntores, reatores, compensadores) para empresas geradoras e transmissoras do setor eletrico brasileiro.

A proposta central e: **transformar dados operacionais dispersos em inteligencia acionavel**, permitindo que equipes de manutencao e operacao identifiquem degradacoes antes que se tornem falhas catastroficas.

### Parametros do MVP

| Parametro | Valor |
|---|---|
| **Objetivo** | Asset Health para geradoras e transmissoras - vigilancia de equipamentos criticos |
| **Timeline** | 12 semanas (3 sprints de 4 semanas) |
| **Equipe Core** | 2 backend, 1 frontend, 1 data/ML, 1 produto |
| **Design Partners** | 2-3 empresas (ideal: 1 geradora, 1 transmissora, 1 mista) |
| **Ativos Alvo** | Transformadores de potencia (>100 MVA), disjuntores de AT/EAT |
| **ROI Primario** | Evitar falha nao planejada de transformador (R$ 1-5M por evento) |
| **ROI Secundario** | Reducao de 20-30% em intervencoes de manutencao corretiva |
| **Modelo de Dados** | Energy Graph ontologico (ativos, subestacoes, medidores, relacoes) |
| **Fontes de Dados** | SCADA, DGA (cromatografia de gases), sensores de temperatura |

### Arquitetura de Alto Nivel

```
[Fontes de Dados]          [Plataforma OntoGrid]              [Consumidores]

SCADA/OPC-UA  ----+     +---------------------------+     +--- Dashboard Web
CSV/Excel     ----|---->| Camada de Ingestao        |     |--- API REST
Sensores IoT  ----+     | (Conectores + Validacao)  |     |--- Alertas (Email/SMS)
                        +------------+--------------+     |--- Cases/SOPs
                                     |                    |
                        +------------v--------------+     |
                        | Energy Graph (Ontologia)  |-----|
                        | Neo4j + TimescaleDB       |     |
                        +------------+--------------+     |
                                     |                    |
                        +------------v--------------+     |
                        | Analytics Engine          |-----|
                        | (Anomalias + Health Score)|
                        +---------------------------+
```

---

## 2. Sprint 1 - Fundacao (Semanas 1-4)

**Objetivo:** Estabelecer a infraestrutura tecnica, o modelo ontologico minimo e a camada de ingestao simulada, garantindo que o time tenha uma base solida para construir as funcionalidades core.

### 2.1 Setup de Infraestrutura

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Dockerizar ambiente completo | Docker Compose com todos os servicos (API, DBs, workers) | 3 dias | Backend Sr | - |
| Configurar Neo4j | Instancia Neo4j para o Energy Graph com schema inicial | 2 dias | Backend Sr | Docker |
| Configurar TimescaleDB | Instancia TimescaleDB para series temporais de telemetria | 2 dias | Backend Sr | Docker |
| Configurar Redis | Cache e fila de mensagens para pipeline de ingestao | 1 dia | Backend Sr | Docker |
| Pipeline CI/CD | GitHub Actions: lint, testes, build de imagens, deploy em staging | 3 dias | Backend Jr | Docker |
| Ambiente de staging | Deploy automatizado em cloud (AWS ECS ou similar) | 2 dias | Backend Jr | CI/CD |
| Monitoramento basico | Metricas de infra com Prometheus + Grafana | 2 dias | Backend Jr | Docker |

**Entregavel:** Ambiente completo rodando localmente via `docker compose up` e pipeline CI/CD funcional.

### 2.2 Energy Graph v0.1 - Modelo Ontologico Minimo

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Definir ontologia core | Modelar entidades: Ativo, Subestacao, Medicao, Empresa, Regional | 3 dias | Data/ML + Produto |  - |
| Schema Neo4j | Criar constraints, indices e labels no Neo4j | 2 dias | Data/ML | Ontologia core |
| Seeds de dados | Script para popular graph com dados de referencia (tipos de ativos, parametros normais) | 2 dias | Data/ML | Schema Neo4j |
| API GraphQL do Graph | Endpoints para consultar e navegar o Energy Graph | 3 dias | Backend Sr | Schema Neo4j |
| Testes de integridade | Validar consistencia do graph (relacoes obrigatorias, tipos) | 1 dia | Data/ML | Seeds |

**Modelo Ontologico Minimo:**

```
(Empresa)-[:POSSUI]->(Regional)-[:CONTEM]->(Subestacao)
(Subestacao)-[:CONTEM]->(Ativo)
(Ativo)-[:TEM_SENSOR]->(Medidor)
(Medidor)-[:GERA]->(SerieTemporalRef)
(Ativo)-[:TIPO]->(TipoAtivo)
(TipoAtivo)-[:TEM_PARAMETRO]->(ParametroNormal)
```

**Entregavel:** Energy Graph navegavel com dados de referencia de ao menos 1 subestacao com 5-10 ativos.

### 2.3 Camada de Ingestao v1

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Conector CSV/Excel | Upload e parsing de arquivos com mapeamento de colunas | 3 dias | Backend Jr | TimescaleDB |
| Simulador SCADA | Gerador de dados realistas de telemetria (temperatura, corrente, gases) | 3 dias | Data/ML | TimescaleDB |
| Pipeline de validacao | Validacao de schema, range, duplicatas e qualidade dos dados | 2 dias | Backend Jr | Conector CSV |
| Armazenamento em TimescaleDB | Hypertables otimizadas para queries de series temporais | 2 dias | Backend Sr | TimescaleDB |
| Data Quality Score | Metrica basica de qualidade por fonte de dados (completude, consistencia) | 1 dia | Data/ML | Pipeline validacao |

**Entregavel:** Dados fluindo via CSV upload e simulador SCADA, armazenados em TimescaleDB com validacao.

### 2.4 API Base e Autenticacao

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Estrutura FastAPI | Projeto base com routers, middlewares, error handling | 2 dias | Backend Sr | - |
| Autenticacao JWT | Login, refresh token, roles (admin, operador, visualizador) | 3 dias | Backend Sr | FastAPI |
| Multi-tenancy | Isolamento de dados por empresa (tenant_id em todas as queries) | 2 dias | Backend Sr | Auth JWT |
| Rate limiting e CORS | Protecao basica da API | 1 dia | Backend Jr | FastAPI |
| Documentacao OpenAPI | Swagger auto-gerado com exemplos | 1 dia | Backend Jr | Todos endpoints |

**Entregavel:** API funcional com autenticacao, multi-tenancy e documentacao Swagger.

### 2.5 Frontend Scaffold

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Setup Next.js + TailwindCSS | Projeto base com roteamento, theme, design system | 3 dias | Frontend | - |
| Layout principal | Sidebar, header, navegacao entre modulos | 2 dias | Frontend | Setup Next.js |
| Tela de login | Autenticacao integrada com a API | 2 dias | Frontend | Auth JWT |
| Dashboard shell | Estrutura de dashboard com placeholders para widgets | 2 dias | Frontend | Layout |
| Componentes base | Tabelas, cards, modais, formularios reutilizaveis | 3 dias | Frontend | Setup Next.js |

**Entregavel:** Aplicacao web funcional com login, navegacao e dashboard vazio pronto para receber widgets.

### Resumo Sprint 1

| Metrica | Meta |
|---|---|
| Tarefas totais | ~30 |
| Esforco total estimado | ~55 dias-pessoa |
| Marco principal | Ambiente funcional end-to-end com dados simulados |
| Demo Sprint Review | Dashboard com login, Graph navegavel, dados fluindo |

---

## 3. Sprint 2 - Core Analytics (Semanas 5-8)

**Objetivo:** Implementar o nucleo analitico do produto - deteccao de anomalias, health score e alertas - transformando dados brutos em inteligencia acionavel. Ao final deste sprint, o produto deve gerar valor real para os design partners.

### 3.1 Pipeline de Ingestao SCADA Real-Time

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Conector OPC-UA | Integrar com servidor OPC-UA (protocolo padrao SCADA) | 4 dias | Backend Sr | Infra Sprint 1 |
| Message broker (Redis Streams) | Fila de mensagens para desacoplar ingestao do processamento | 2 dias | Backend Sr | Redis |
| Worker de processamento | Consumidor que valida, enriquece e persiste dados | 3 dias | Backend Jr | Broker |
| Backfill historico | Mecanismo para importar dados historicos (6-12 meses) | 2 dias | Backend Jr | Worker |
| Dashboard de ingestao | Painel de status: fontes conectadas, latencia, erros | 2 dias | Frontend | Worker |

**Entregavel:** Pipeline capaz de ingerir dados SCADA em near real-time (<30s de latencia) com monitoramento.

### 3.2 Deteccao de Anomalias

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Feature engineering | Extrair features de series temporais (media movel, desvio, taxa de variacao) | 3 dias | Data/ML | TimescaleDB c/ dados |
| Isolation Forest | Modelo para detectar anomalias multivariadas em telemetria | 3 dias | Data/ML | Features |
| Z-Score adaptativo | Deteccao de desvios estatisticos com baseline ajustavel por ativo | 2 dias | Data/ML | Features |
| DBSCAN temporal | Agrupamento de anomalias relacionadas para reduzir ruido | 2 dias | Data/ML | Isolation Forest |
| Ensemble de modelos | Combinar scores dos 3 metodos com pesos configuraveis | 2 dias | Data/ML | Todos modelos |
| API de anomalias | Endpoints: listar anomalias, filtrar, detalhar, marcar como falso positivo | 2 dias | Backend Sr | Ensemble |
| Testes com dados reais | Validar modelos com dados historicos dos design partners | 3 dias | Data/ML | Ensemble |

**Entregavel:** Engine de deteccao de anomalias operacional com 3 algoritmos em ensemble, taxa de falso positivo < 20%.

### 3.3 Health Score Engine

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Definir modelo de Health Score | Score 0-100 multi-variavel por tipo de ativo | 2 dias | Data/ML + Produto | - |
| Pesos por tipo de ativo | Configuracao de pesos (temperatura, DGA, carga, idade) por tipo | 2 dias | Data/ML | Modelo definido |
| Calculo batch (diario) | Job agendado para recalcular health scores | 2 dias | Backend Sr | Pesos |
| Calculo near real-time | Atualizacao incremental quando dados novos chegam | 3 dias | Backend Sr | Calculo batch |
| Historico de Health Score | Armazenar evolucao do score para analise de tendencia | 1 dia | Backend Jr | Calculo batch |
| API de Health Score | Endpoints: score atual, historico, ranking de ativos criticos | 2 dias | Backend Sr | Calculo |

**Composicao do Health Score (exemplo transformador):**

| Variavel | Peso | Fonte |
|---|---|---|
| Temperatura do oleo | 25% | SCADA sensor |
| Gases dissolvidos (DGA) | 30% | Laboratorio / sensor online |
| Fator de potencia do isolamento | 15% | Ensaio periodico |
| Nivel de carga vs capacidade | 15% | SCADA |
| Idade e historico de manutencao | 10% | Cadastro |
| Frequencia de anomalias recentes | 5% | Engine de anomalias |

**Entregavel:** Health Score calculado para todos os ativos monitorados, com historico e ranking.

### 3.4 Sistema de Alertas

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Alert Engine | Motor de regras: condicoes, severidade (info/warning/critical/emergency) | 3 dias | Backend Sr | Anomalias + Health Score |
| Regras padrao por tipo de ativo | Templates de alertas pre-configurados (ex: DGA acima do limite IEEE) | 2 dias | Data/ML + Produto | Alert Engine |
| Regras customizaveis | Interface para criar regras personalizadas por ativo | 2 dias | Backend Sr + Frontend | Alert Engine |
| Canal de notificacao: Email | Envio de alertas por email com template rico | 2 dias | Backend Jr | Alert Engine |
| Canal de notificacao: SMS | Envio de alertas criticos por SMS (Twilio/SNS) | 1 dia | Backend Jr | Alert Engine |
| Painel de alertas | Lista de alertas com filtros, ack, snooze, escalonamento | 3 dias | Frontend | API alertas |
| Supressao e correlacao | Evitar alert fatigue: agrupar alertas relacionados, cooldown | 2 dias | Backend Sr | Alert Engine |

**Entregavel:** Sistema de alertas inteligente com notificacoes multi-canal e reducao de alert fatigue.

### 3.5 Dashboard de Ativos e Visualizacoes

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Lista de ativos | Tabela com status, health score, ultimo alerta, localizacao | 2 dias | Frontend | API ativos |
| Detalhe do ativo | Pagina com ficha tecnica, health score, historico, anomalias | 3 dias | Frontend | APIs Sprint 2 |
| Graficos de series temporais | Visualizacao interativa de telemetria (Recharts/D3) | 3 dias | Frontend | API series temporais |
| Mapa de calor de ativos | Visao consolidada por subestacao com heatmap de saude | 2 dias | Frontend | Health Score API |
| Visualizacao do Energy Graph | Grafo interativo mostrando relacoes entre ativos (vis.js/d3-force) | 3 dias | Frontend | API GraphQL Graph |
| Filtros e busca global | Buscar ativos por nome, tipo, subestacao, faixa de health score | 2 dias | Frontend | APIs |

**Entregavel:** Dashboard completo com visao operacional de todos os ativos, graficos e grafo interativo.

### Resumo Sprint 2

| Metrica | Meta |
|---|---|
| Tarefas totais | ~35 |
| Esforco total estimado | ~65 dias-pessoa |
| Marco principal | Produto gerando insights reais com dados dos design partners |
| Demo Sprint Review | Alerta real disparado, Health Score de ativos, Dashboard funcional |

---

## 4. Sprint 3 - Workflows e Polish (Semanas 9-12)

**Objetivo:** Fechar o ciclo de valor (detectar -> alertar -> agir -> resolver), polir a experiencia do usuario e preparar o produto para uso real pelos design partners.

### 4.1 Case Management

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Modelo de Case | Estrutura: titulo, descricao, ativo(s), severidade, responsavel, SLA | 2 dias | Backend Sr | - |
| Criacao automatica de Cases | Alertas criticos geram cases automaticamente | 2 dias | Backend Sr | Alert Engine |
| Criacao manual de Cases | Formulario para abrir case a partir de qualquer contexto | 2 dias | Frontend + Backend Jr | Modelo Case |
| Workflow de estados | Aberto -> Em analise -> Em execucao -> Resolvido -> Fechado | 2 dias | Backend Sr | Modelo Case |
| Atribuicao e escalonamento | Atribuir responsavel, escalonar por SLA nao cumprido | 2 dias | Backend Sr | Workflow |
| Comentarios e anexos | Adicionar notas, imagens, documentos ao case | 2 dias | Backend Jr + Frontend | Modelo Case |
| Painel de Cases | Lista com filtros, kanban view, metricas de SLA | 3 dias | Frontend | API Cases |

**Entregavel:** Sistema de case management funcional com criacao automatica a partir de alertas.

### 4.2 SOPs e Base de Conhecimento

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Modelo de SOP | Estrutura: passos, checklist, tipo de ativo, condicoes de aplicacao | 2 dias | Backend Sr + Produto | - |
| CRUD de SOPs | Interface para criar, editar, versionar procedimentos | 3 dias | Frontend + Backend Jr | Modelo SOP |
| Vinculacao SOP-Alerta | Sugerir SOP relevante quando alerta/case e criado | 2 dias | Backend Sr | SOPs + Alert Engine |
| SOPs pre-configurados | 5-10 SOPs padrao para anomalias comuns em transformadores | 2 dias | Produto + Data/ML | CRUD SOPs |
| Execucao guiada de SOP | Interface step-by-step para executar SOP dentro de um case | 3 dias | Frontend | SOP + Case |

**Entregavel:** Base de SOPs com sugestao automatica e execucao guiada integrada ao case management.

### 4.3 Lineage e Audit Trail

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Event sourcing basico | Registrar todas as acoes relevantes (ingestao, calculo, alerta, case) | 3 dias | Backend Sr | Todas as features |
| Lineage de dados | Rastrear: dado bruto -> transformacao -> anomalia -> alerta -> case | 2 dias | Backend Sr | Event sourcing |
| Visualizacao de lineage | Timeline mostrando a cadeia de eventos de um case/alerta | 2 dias | Frontend | API lineage |
| Audit log | Registro de acoes de usuarios (quem fez o que, quando) | 2 dias | Backend Jr | Auth |
| Exportacao de audit | Download CSV/PDF do audit trail para compliance | 1 dia | Backend Jr | Audit log |

**Entregavel:** Rastreabilidade completa do ciclo dado -> insight -> acao, com audit trail exportavel.

### 4.4 Dashboard Executivo

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| KPIs principais | Widgets: ativos criticos, MTTR, alertas/semana, SLA compliance | 3 dias | Frontend | Todas APIs |
| Tendencias | Graficos de evolucao de health score medio, alertas, cases | 2 dias | Frontend | Health Score historico |
| Comparativo por subestacao | Ranking de subestacoes por saude dos ativos | 1 dia | Frontend | APIs |
| Exportacao de relatorio | PDF executivo com snapshot dos KPIs | 2 dias | Frontend + Backend Jr | KPIs |

**KPIs do Dashboard Executivo:**

| KPI | Descricao | Meta MVP |
|---|---|---|
| Ativos em estado critico | % de ativos com Health Score < 40 | Visibilidade 100% |
| MTTR (Mean Time to Resolve) | Tempo medio de resolucao de cases | < 48h para criticos |
| Taxa de deteccao precoce | Anomalias detectadas antes de virar falha | > 70% |
| SLA compliance | % de cases resolvidos dentro do SLA | > 85% |
| Alert fatigue ratio | Alertas acionaveis vs total de alertas | > 60% acionaveis |
| Cobertura de monitoramento | % de ativos criticos monitorados | 100% no escopo |

**Entregavel:** Dashboard executivo com KPIs acionaveis e exportacao de relatorio.

### 4.5 Testes, Performance e Documentacao

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Testes de carga | Simular 1000 ativos, 10k pontos/minuto de telemetria | 3 dias | Backend Sr | Toda infra |
| Testes end-to-end | Fluxo completo: ingestao -> anomalia -> alerta -> case -> resolucao | 2 dias | QA/Backend Jr | Todas features |
| Otimizacao de queries | Profiling e otimizacao de queries lentas no TimescaleDB e Neo4j | 2 dias | Backend Sr | Testes de carga |
| Documentacao da API | Guia completo com exemplos para integradores | 2 dias | Backend Jr | APIs estabilizadas |
| Guia de onboarding | Passo-a-passo para novos design partners configurarem o sistema | 2 dias | Produto | Todas features |
| Security review | Revisao de autenticacao, autorizacao, injecao, XSS | 2 dias | Backend Sr | Todas features |

**Entregavel:** Produto estavel, testado sob carga e documentado para onboarding de design partners.

### 4.6 Onboarding de Design Partners

| Tarefa | Descricao | Esforco | Responsavel | Dependencia |
|---|---|---|---|---|
| Ambiente dedicado por partner | Tenant isolado com dados do partner | 2 dias | Backend Sr | Multi-tenancy |
| Integracao de dados reais | Conectar fontes SCADA/historicas do partner | 3 dias | Data/ML + Backend | Conectores |
| Configuracao de ativos | Popular Energy Graph com ativos reais do partner | 2 dias | Data/ML | Graph API |
| Treinamento de usuarios | Sessao hands-on com equipe do partner | 1 dia | Produto | Guia onboarding |
| Coleta de feedback estruturado | Questionario + entrevista sobre valor percebido | 1 dia | Produto | 2 semanas de uso |

**Entregavel:** 2-3 design partners usando o produto com dados reais e fornecendo feedback estruturado.

### Resumo Sprint 3

| Metrica | Meta |
|---|---|
| Tarefas totais | ~35 |
| Esforco total estimado | ~60 dias-pessoa |
| Marco principal | Produto em uso real por design partners |
| Demo Sprint Review | Demo end-to-end com dados reais de partner |

---

## 5. Criterios de Sucesso do MVP

### 5.1 Metricas Quantitativas

| Criterio | Meta | Como Medir |
|---|---|---|
| Ativos monitorados | >= 50 ativos criticos em produc | Contagem no sistema |
| Disponibilidade | >= 99.5% uptime | Monitoramento (Prometheus) |
| Latencia de ingestao | < 30 segundos (SCADA -> dashboard) | Metrica no pipeline |
| Deteccao de anomalias | Precisao >= 80%, Recall >= 70% | Validacao com historico |
| Falsos positivos | < 20% dos alertas disparados | Feedback dos operadores |
| Tempo de onboarding | < 1 semana por design partner | Tracking do processo |
| Adocao de usuarios | >= 3 logins/semana por usuario ativo | Analytics |
| Cases resolvidos | >= 10 cases resolvidos no periodo | Contagem no sistema |
| Performance da API | p95 < 500ms para queries principais | APM |
| Health Score coverage | 100% dos ativos no escopo com score | Contagem no sistema |

### 5.2 Feedback Qualitativo dos Design Partners

| Dimensao | Pergunta Chave | Meta |
|---|---|---|
| Valor percebido | "O produto ajudou a identificar um risco que voce nao veria sem ele?" | >= 1 caso concreto por partner |
| Facilidade de uso | "Sua equipe consegue usar o sistema sem suporte constante?" | Sim, apos treinamento inicial |
| Confiabilidade dos alertas | "Voce confia nos alertas o suficiente para agir com base neles?" | Score >= 7/10 |
| Intencao de compra | "Voce pagaria por este produto? Quanto?" | Disposicao confirmada com range |
| Completude | "O que esta faltando para voce considerar o produto completo?" | Lista priorizada de gaps |
| NPS | "De 0 a 10, quanto voce recomendaria o OntoGrid?" | >= 8 (promotor) |

---

## 6. Riscos e Mitigacoes

| # | Risco | Probabilidade | Impacto | Mitigacao |
|---|---|---|---|---|
| R1 | Dificuldade de acesso a dados SCADA dos partners (firewall, protocolos proprietarios, politicas de seguranca) | Alta | Alto | Iniciar com upload CSV/historico; ter conector OPC-UA como alternativa; oferecer deploy on-premises do coletor |
| R2 | Qualidade dos dados insuficiente (lacunas, sensores descalibrados, timestamps inconsistentes) | Alta | Alto | Data Quality Score visivel; pipeline robusto de validacao; documentar requisitos minimos de dados |
| R3 | Falsos positivos excessivos na deteccao de anomalias levando a alert fatigue | Media | Alto | Ensemble de modelos; feedback loop para marcar falso positivo; tuning por tipo de ativo; cooldown e agrupamento |
| R4 | Design partners sem disponibilidade para feedback e validacao | Media | Alto | Definir acordo formal de participacao; reunioes quinzenais agendadas; designar ponto focal no partner |
| R5 | Escopo cresce alem da capacidade do time (scope creep) | Media | Medio | Backlog rigido; product owner com poder de veto; sprint planning disciplinado; dizer nao para features fora do MVP |
| R6 | Performance insuficiente com volume real de dados | Baixa | Alto | Testes de carga desde o Sprint 2; arquitetura escalavel desde o inicio (TimescaleDB, workers assincronos) |
| R7 | Turnover de membros-chave do time | Baixa | Alto | Documentacao continua; pair programming; conhecimento distribuido (nenhum bus factor = 1) |
| R8 | Modelo ontologico muito rigido ou muito flexivel para os casos reais | Media | Medio | Validar ontologia com dados reais do partner no Sprint 1; iterar com base em feedback; manter modelo extensivel |
| R9 | Regulacao ou compliance bloqueia integracao (LGPD, politicas internas do partner) | Baixa | Medio | Levantamento juridico antecipado; dados anonimizados em staging; multi-tenancy com isolamento forte |
| R10 | Concorrentes lancam solucao similar durante o MVP | Baixa | Medio | Foco no diferencial ontologico (Energy Graph); velocidade de execucao; relacionamento proximo com partners |

---

## 7. Pos-MVP: Caminho para PMF

### 7.1 Fase 2 - Asset Reliability (Meses 4-6)

Expandir de vigilancia para **gestao proativa de confiabilidade**:

- **Predicao de falhas**: Modelos de ML para prever RUL (Remaining Useful Life) de ativos criticos
- **Manutencao baseada em condicao**: Recomendacoes automaticas de intervencao com base em tendencias
- **Analise de causa raiz**: Correlacao automatica entre eventos, condicoes climaticas e degradacao
- **Benchmarking entre ativos**: Comparar performance de ativos similares em contextos diferentes
- **Integracao com sistemas de manutencao**: Conectores para SAP PM, Maximo, Oracle EAM

### 7.2 Fase 3 - Grid 360 (Meses 7-10)

Expandir o Energy Graph para uma **visao completa da rede**:

- **Topologia da rede**: Modelar linhas de transmissao, barramentos, protecao
- **Analise de contingencia**: Simular impacto de falha de um ativo na rede
- **Otimizacao de despacho**: Considerar saude dos ativos na operacao
- **Gemeo digital**: Representacao digital completa de subestacoes
- **Integracao com ONS**: Dados do operador nacional do sistema

### 7.3 Fase 4 - Energy Data Hub SaaS (Meses 11-15)

Evoluir para **plataforma de dados do setor eletrico**:

- **Marketplace de conectores**: Conectores pre-construidos para SCADA, ERP, GIS, meteorologia
- **APIs abertas**: Platform as a Service para desenvolvedores do setor eletrico
- **Analytics self-service**: Notebooks integrados e query engine para analistas
- **Data sharing regulado**: Compartilhamento seguro de dados entre empresas (com controle de acesso granular)
- **Modelos de ML pre-treinados**: Biblioteca de modelos para casos de uso comuns do setor
- **Multi-modulo**: Asset Health, Grid Reliability, Energy Trading, Regulatory Compliance como modulos independentes

### 7.4 Marcos de PMF (Product-Market Fit)

| Marco | Indicador | Meta |
|---|---|---|
| Retentor de valor | Design partners renovam apos periodo gratuito | 100% retencao |
| Referencia espontanea | Partners indicam outros potenciais clientes | >= 2 indicacoes |
| Expansao de escopo | Partners pedem monitoramento de mais ativos/subestacoes | Aumento de 3x no escopo |
| Dependencia operacional | Produto incorporado na rotina diaria da equipe | >= 5 logins/semana/usuario |
| Willingness to pay | Contrato assinado com valor definido | >= 2 contratos |
| Pipeline comercial | Empresas em negociacao alem dos design partners | >= 5 no pipeline |

---

## Apendice: Timeline Visual

```
Semana:  1    2    3    4    5    6    7    8    9   10   11   12
         |    |    |    |    |    |    |    |    |    |    |    |
Sprint 1: [=========FUNDACAO=========]
         Infra Docker    Graph v0.1
         CI/CD           Ingestao v1
         API Base        Frontend Shell

Sprint 2:                     [=======CORE ANALYTICS=======]
                              SCADA RT     Health Score
                              Anomalias    Alertas
                              Dashboard    Graficos

Sprint 3:                                          [=====WORKFLOWS/POLISH=====]
                                                   Cases       SOPs
                                                   Lineage     KPIs
                                                   Testes      Onboarding
                                                         |
                                                   Design Partners
                                                   usando produto
```

---

*Documento vivo - atualizar a cada Sprint Review com base em aprendizados e feedback dos design partners.*
