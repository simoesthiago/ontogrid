# User Stories - OntoGrid MVP (Asset Health)

> **Produto:** OntoGrid - Plataforma de Dados e Decisao para o Setor Eletrico Brasileiro
> **Escopo MVP:** Asset Health - Vigilancia de equipamentos criticos para geradoras e transmissoras
> **Versao:** 1.0
> **Data:** 2026-03-06

---

## 1. Personas

### Persona 1: Carlos - Engenheiro de Manutencao

| Atributo | Descricao |
|---|---|
| **Papel** | Engenheiro de Manutencao Preditiva |
| **Empresa** | Geradora/Transmissora de energia (ex: CEMIG, Eletrobras) |
| **Experiencia** | 12 anos em manutencao de transformadores e geradores |
| **Responsabilidades** | Planejar e executar manutencao preditiva; analisar dados de monitoramento; decidir intervencoes antes de falhas |
| **Dores** | Usa planilhas e inspecoes visuais; nao tem visao integrada da saude dos ativos; descobre problemas tarde demais |
| **Objetivo** | Saber quais equipamentos estao degradando ANTES de falharem, priorizando intervencoes com base em dados |
| **Ferramentas atuais** | Excel, relatorios de inspecao em papel, sistemas SCADA isolados |

### Persona 2: Ana - Operadora de Subestacao

| Atributo | Descricao |
|---|---|
| **Papel** | Operadora de Subestacao / Centro de Operacoes |
| **Empresa** | Transmissora de energia |
| **Experiencia** | 6 anos em operacao de subestacoes |
| **Responsabilidades** | Monitorar equipamentos em tempo real; responder a alarmes; executar procedimentos operacionais |
| **Dores** | Alarmes SCADA basicos sem contexto; excesso de alarmes (alarm flooding); nao sabe a severidade real |
| **Objetivo** | Ser alertada imediatamente quando algo sai do normal, com contexto suficiente para agir corretamente |
| **Ferramentas atuais** | SCADA legado, telefone, radio, planilhas de turno |

### Persona 3: Roberto - Gerente de Operacoes

| Atributo | Descricao |
|---|---|
| **Papel** | Gerente de Operacoes e Manutencao |
| **Empresa** | Geradora/Transmissora de energia |
| **Experiencia** | 18 anos no setor eletrico, 5 em gestao |
| **Responsabilidades** | Visao executiva de ativos em risco; priorizar investimentos; reportar indicadores para diretoria e ANEEL |
| **Dores** | Consolida dados manualmente de multiplas fontes; nao tem visao unificada da frota; relatorios demoram dias |
| **Objetivo** | Dashboard executivo com KPIs de saude, risco e disponibilidade para tomada de decisao rapida |
| **Ferramentas atuais** | PowerPoint, Excel, e-mails consolidados, reunioes semanais |

### Persona 4: Marina - Analista de Confiabilidade

| Atributo | Descricao |
|---|---|
| **Papel** | Analista de Confiabilidade e Engenharia de Ativos |
| **Empresa** | Geradora/Transmissora de energia |
| **Experiencia** | 8 anos em engenharia de confiabilidade |
| **Responsabilidades** | Analisar historico de falhas e causa raiz; otimizar estrategia de manutencao; modelar vida util remanescente |
| **Dores** | Dados sujos e fragmentados; series temporais incompletas; dificuldade em correlacionar eventos |
| **Objetivo** | Dados limpos, series temporais longas e ferramentas de analise para otimizar a estrategia de manutencao |
| **Ferramentas atuais** | Python/R para analise, bancos de dados isolados, relatorios de falha em PDF |

### Persona 5: Thiago - Administrador do Sistema

| Atributo | Descricao |
|---|---|
| **Papel** | Administrador da plataforma OntoGrid |
| **Empresa** | Equipe de TI da geradora/transmissora |
| **Experiencia** | 10 anos em TI industrial |
| **Responsabilidades** | Configurar a plataforma; gerenciar usuarios e permissoes; integrar fontes de dados; manter o sistema |
| **Dores** | Multiplos sistemas desconectados; integracao manual entre SCADA, ERP e sistemas de manutencao |
| **Objetivo** | Plataforma centralizada, facil de configurar e integrar com sistemas existentes |
| **Ferramentas atuais** | Ferramentas de integracao ad hoc, scripts customizados |

---

## 2. Epicos

### Epico 1: Cadastro e Visualizacao de Ativos
Permitir o registro, classificacao e visualizacao hierarquica dos ativos criticos (transformadores, geradores, disjuntores, etc.) com seus atributos tecnicos, localizacao e relacoes.

### Epico 2: Ingestao e Monitoramento SCADA
Ingerir dados de sensores e sistemas SCADA (temperatura, pressao, gases dissolvidos, corrente, vibracoes) via CSV, API REST ou protocolo OPC-UA, normalizando e armazenando series temporais.

### Epico 3: Health Score e Anomalias
Calcular o Health Score de cada ativo com base em regras configuráveis e modelos analiticos, detectando anomalias e tendencias de degradacao automaticamente.

### Epico 4: Alertas Inteligentes
Gerar alertas contextualizados quando anomalias sao detectadas, com severidade, ativo afetado, causa provavel e acao recomendada, entregues por email, SMS ou push notification.

### Epico 5: Gestao de Casos e SOPs
Criar e gerenciar casos (tickets) a partir de alertas, associando procedimentos operacionais padrao (SOPs) e rastreando resolucao ate o encerramento.

### Epico 6: Dashboard Executivo
Fornecer dashboards executivos com KPIs de saude da frota, disponibilidade, risco e tendencias, com filtros por regiao, tipo de ativo e periodo.

### Epico 7: Energy Graph e Analise de Impacto
Utilizar o grafo ontologico (Energy Graph) para mapear relacoes entre ativos, subestacoes, linhas e consumidores, permitindo analise de impacto em cascata quando um ativo falha.

---

## 3. User Stories Detalhadas

---

### Epico 1: Cadastro e Visualizacao de Ativos

---

#### US-001: Ver lista de ativos com health score

| Campo | Descricao |
|---|---|
| **ID** | US-001 |
| **Titulo** | Ver lista de ativos com health score |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **ver uma lista de todos os ativos criticos com seu health score atual**, para que **eu possa identificar rapidamente quais equipamentos precisam de atencao prioritaria**. |
| **Prioridade** | Must Have |
| **Estimativa** | M |
| **Sprint** | 1 |
| **Dependencias** | - |

**Criterios de Aceite:**

```
Dado que Carlos esta autenticado no sistema
Quando ele acessa a pagina "Ativos"
Entao o sistema exibe uma lista paginada com todos os ativos cadastrados, mostrando: nome, tipo, localizacao, health score (0-100) e status (Critico/Alerta/Normal)

Dado que a lista de ativos esta exibida
Quando Carlos clica no cabecalho da coluna "Health Score"
Entao a lista e reordenada pelo health score (crescente ou decrescente), permitindo ver primeiro os ativos em pior estado

Dado que a lista de ativos esta exibida
Quando Carlos aplica filtros por tipo de ativo (transformador, gerador, disjuntor), regiao ou faixa de health score
Entao a lista e atualizada mostrando apenas os ativos que atendem aos filtros selecionados

Dado que existem ativos com health score abaixo de 40
Quando a lista e renderizada
Entao esses ativos sao destacados visualmente com indicador vermelho (Critico)
```

---

#### US-002: Ver detalhe de ativo com series temporais

| Campo | Descricao |
|---|---|
| **ID** | US-002 |
| **Titulo** | Ver detalhe de ativo com series temporais |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **ver a pagina de detalhe de um ativo com graficos de series temporais dos seus sensores**, para que **eu possa analisar tendencias e identificar padroes de degradacao**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 1 |
| **Dependencias** | US-001, US-007 |

**Criterios de Aceite:**

```
Dado que Carlos esta na lista de ativos
Quando ele clica em um ativo especifico
Entao o sistema exibe a pagina de detalhe com: dados cadastrais, health score atual, historico de health score (grafico de linha) e graficos de series temporais por sensor

Dado que a pagina de detalhe do ativo esta exibida
Quando Carlos seleciona um periodo (ultimas 24h, 7 dias, 30 dias, customizado)
Entao os graficos de series temporais sao atualizados para o periodo selecionado

Dado que os graficos de series temporais estao exibidos
Quando Carlos passa o mouse sobre um ponto do grafico
Entao o sistema exibe tooltip com valor exato, timestamp e unidade de medida

Dado que a pagina de detalhe esta exibida
Quando ha anomalias detectadas no periodo visualizado
Entao os pontos anomalos sao destacados no grafico com marcadores visuais e o usuario pode clicar para ver detalhes
```

---

#### US-011: Cadastrar novo ativo no sistema

| Campo | Descricao |
|---|---|
| **ID** | US-011 |
| **Titulo** | Cadastrar novo ativo no sistema |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **cadastrar um novo ativo com seus atributos tecnicos e localizacao**, para que **o ativo passe a ser monitorado pela plataforma**. |
| **Prioridade** | Must Have |
| **Estimativa** | M |
| **Sprint** | 1 |
| **Dependencias** | - |

**Criterios de Aceite:**

```
Dado que Thiago esta autenticado como administrador
Quando ele acessa "Novo Ativo" e preenche os campos obrigatorios (nome, tipo, fabricante, subestacao, tensao nominal, data de instalacao)
Entao o ativo e criado com status "Ativo" e health score inicial de 100

Dado que Thiago esta cadastrando um ativo
Quando ele informa um tipo de ativo (transformador, gerador, disjuntor, reator, etc.)
Entao o formulario exibe campos especificos daquele tipo (ex: potencia nominal para transformador, tipo de isolamento)

Dado que Thiago tenta salvar um ativo sem preencher campos obrigatorios
Quando ele clica em "Salvar"
Entao o sistema exibe mensagens de validacao indicando quais campos sao obrigatorios
```

---

#### US-012: Importar ativos em lote via CSV

| Campo | Descricao |
|---|---|
| **ID** | US-012 |
| **Titulo** | Importar ativos em lote via CSV |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **importar multiplos ativos de uma vez atraves de um arquivo CSV**, para que **a carga inicial do sistema seja rapida e eficiente**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | US-011 |

**Criterios de Aceite:**

```
Dado que Thiago esta na area de administracao
Quando ele acessa "Importar Ativos" e faz upload de um arquivo CSV
Entao o sistema valida o formato, exibe preview das primeiras 10 linhas e pede confirmacao

Dado que o CSV contem linhas com erros de validacao
Quando o sistema processa o arquivo
Entao as linhas validas sao importadas e as invalidas sao listadas com o motivo do erro para correcao

Dado que a importacao foi concluida
Quando Thiago visualiza o resultado
Entao o sistema exibe resumo: total de linhas, importadas com sucesso, erros encontrados, e permite download do log de erros
```

---

#### US-013: Visualizar hierarquia de ativos

| Campo | Descricao |
|---|---|
| **ID** | US-013 |
| **Titulo** | Visualizar hierarquia de ativos |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **visualizar a hierarquia dos ativos (empresa > regional > subestacao > bay > equipamento)**, para que **eu entenda a estrutura organizacional e localize rapidamente os equipamentos**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | US-011 |

**Criterios de Aceite:**

```
Dado que Carlos esta na pagina de ativos
Quando ele alterna para a visualizacao em arvore
Entao o sistema exibe a hierarquia completa com nos expansiveis: Empresa > Regional > Subestacao > Bay > Equipamento

Dado que a arvore esta exibida
Quando Carlos clica em um no de subestacao
Entao o sistema expande mostrando todos os bays e equipamentos daquela subestacao com indicador visual de health score

Dado que a arvore esta exibida
Quando Carlos busca por nome de ativo no campo de busca
Entao a arvore filtra e destaca o caminho completo ate o ativo encontrado
```

---

### Epico 2: Ingestao e Monitoramento SCADA

---

#### US-007: Ingerir dados SCADA via CSV/API

| Campo | Descricao |
|---|---|
| **ID** | US-007 |
| **Titulo** | Ingerir dados SCADA via CSV e API REST |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **configurar a ingestao de dados SCADA via upload de CSV e via API REST**, para que **os dados de sensores alimentem o sistema de monitoramento**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 1 |
| **Dependencias** | US-011 |

**Criterios de Aceite:**

```
Dado que Thiago esta na area de ingestao de dados
Quando ele faz upload de um CSV com colunas (ativo_id, sensor, timestamp, valor, unidade)
Entao o sistema valida, normaliza e armazena os dados como serie temporal associada ao ativo

Dado que um sistema externo envia dados via API REST (POST /api/v1/telemetry)
Quando o payload contem ativo_id, sensor, timestamp e valor
Entao o sistema valida, normaliza e armazena os dados com latencia menor que 5 segundos

Dado que os dados foram ingeridos
Quando Thiago acessa o log de ingestao
Entao o sistema exibe: total de pontos recebidos, aceitos, rejeitados, e motivo das rejeicoes

Dado que um registro chega com timestamp duplicado para o mesmo ativo/sensor
Quando o sistema processa
Entao o registro duplicado e descartado e logado sem gerar erro
```

---

#### US-014: Monitorar status da ingestao em tempo real

| Campo | Descricao |
|---|---|
| **ID** | US-014 |
| **Titulo** | Monitorar status da ingestao em tempo real |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **ver um painel com o status da ingestao de dados em tempo real**, para que **eu saiba se os dados estao chegando corretamente ou se ha falhas de comunicacao**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | US-007 |

**Criterios de Aceite:**

```
Dado que Thiago acessa o painel de ingestao
Quando dados estao sendo recebidos
Entao o sistema exibe: taxa de ingestao (pontos/minuto), ultimo dado recebido por fonte, e status (Online/Offline) por ativo

Dado que um ativo nao envia dados por mais de 15 minutos (timeout configuravel)
Quando o sistema detecta a ausencia
Entao o status do ativo muda para "Offline" e um alerta de comunicacao e gerado

Dado que houve falha na ingestao
Quando Thiago inspeciona o log
Entao o sistema mostra detalhes: timestamp da falha, fonte afetada, tipo de erro e sugestao de correcao
```

---

#### US-015: Configurar mapeamento de sensores por tipo de ativo

| Campo | Descricao |
|---|---|
| **ID** | US-015 |
| **Titulo** | Configurar mapeamento de sensores por tipo de ativo |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **configurar quais sensores sao esperados para cada tipo de ativo**, para que **o sistema saiba quais dados monitorar e possa detectar sensores ausentes**. |
| **Prioridade** | Must Have |
| **Estimativa** | M |
| **Sprint** | 1 |
| **Dependencias** | US-011 |

**Criterios de Aceite:**

```
Dado que Thiago esta configurando o tipo "Transformador de Potencia"
Quando ele adiciona sensores esperados (temperatura oleo, gases dissolvidos H2/CH4/C2H2, umidade, nivel oleo)
Entao o sistema registra o template de sensores para esse tipo de ativo

Dado que um ativo do tipo "Transformador" e cadastrado
Quando o sistema avalia a cobertura de sensores
Entao ele indica quais sensores estao mapeados e quais estao faltando

Dado que o template de sensores e alterado
Quando Thiago salva a configuracao
Entao os ativos existentes daquele tipo sao reavaliados quanto a cobertura de sensores
```

---

### Epico 3: Health Score e Anomalias

---

#### US-016: Calcular health score baseado em regras

| Campo | Descricao |
|---|---|
| **ID** | US-016 |
| **Titulo** | Calcular health score baseado em regras configuraveis |
| **Story** | Como **Marina (Analista de Confiabilidade)**, eu quero **que o sistema calcule automaticamente o health score de cada ativo com base em regras configuraveis por tipo de equipamento**, para que **eu tenha uma visao objetiva e consistente do estado de cada ativo**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 1 |
| **Dependencias** | US-007, US-015 |

**Criterios de Aceite:**

```
Dado que dados de sensores estao sendo recebidos para um transformador
Quando o sistema recalcula o health score (a cada 15 minutos por padrao)
Entao o health score e calculado como media ponderada dos indicadores (temperatura, gases, umidade, etc.) resultando em valor de 0 a 100

Dado que o health score foi calculado
Quando o valor muda mais de 5 pontos em relacao ao calculo anterior
Entao o sistema registra o evento de mudanca significativa no historico do ativo

Dado que Marina acessa as configuracoes de health score
Quando ela ajusta os pesos dos indicadores para transformadores (ex: gases 40%, temperatura 30%, umidade 20%, idade 10%)
Entao os health scores sao recalculados com os novos pesos na proxima execucao
```

---

#### US-017: Detectar anomalias em series temporais

| Campo | Descricao |
|---|---|
| **ID** | US-017 |
| **Titulo** | Detectar anomalias em series temporais |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **que o sistema detecte automaticamente anomalias nas series temporais dos sensores**, para que **eu seja informado de comportamentos anormais antes que se tornem falhas**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 2 |
| **Dependencias** | US-007, US-016 |

**Criterios de Aceite:**

```
Dado que o sistema esta monitorando dados de um sensor
Quando um valor ultrapassa o threshold estatistico (media + 3 desvios padrao da janela movel de 30 dias)
Entao uma anomalia e registrada com: ativo, sensor, valor observado, valor esperado, desvio e severidade

Dado que uma anomalia foi detectada
Quando Carlos acessa a pagina de detalhe do ativo
Entao a anomalia aparece destacada no grafico de series temporais com marcador visual e tooltip explicativo

Dado que multiplas anomalias ocorrem no mesmo ativo em um periodo de 24h
Quando o sistema avalia as anomalias
Entao elas sao agrupadas como um unico evento correlacionado para evitar ruido
```

---

#### US-018: Visualizar tendencia de degradacao

| Campo | Descricao |
|---|---|
| **ID** | US-018 |
| **Titulo** | Visualizar tendencia de degradacao do ativo |
| **Story** | Como **Marina (Analista de Confiabilidade)**, eu quero **visualizar a tendencia de degradacao do health score com projecao futura**, para que **eu possa estimar quando o ativo atingira um nivel critico e planejar intervencoes**. |
| **Prioridade** | Should Have |
| **Estimativa** | G |
| **Sprint** | 3 |
| **Dependencias** | US-016 |

**Criterios de Aceite:**

```
Dado que Marina esta na pagina de detalhe de um ativo
Quando ela ativa a visualizacao de tendencia
Entao o sistema exibe o historico de health score com linha de tendencia (regressao linear) e projecao para os proximos 90 dias

Dado que a projecao indica que o health score atingira nivel critico (<40) em menos de 30 dias
Quando a tendencia e calculada
Entao o sistema exibe alerta visual "Atencao: ativo projetado para atingir nivel critico em X dias"

Dado que Marina deseja analisar um periodo especifico
Quando ela seleciona o intervalo de analise
Entao a tendencia e recalculada com base apenas nos dados do periodo selecionado
```

---

### Epico 4: Alertas Inteligentes

---

#### US-003: Receber alerta quando anomalia detectada

| Campo | Descricao |
|---|---|
| **ID** | US-003 |
| **Titulo** | Receber alerta quando anomalia e detectada |
| **Story** | Como **Ana (Operadora de Subestacao)**, eu quero **receber alertas imediatos quando uma anomalia e detectada em um equipamento**, para que **eu possa tomar acoes corretivas rapidamente**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 2 |
| **Dependencias** | US-017 |

**Criterios de Aceite:**

```
Dado que uma anomalia de severidade Alta ou Critica e detectada
Quando o sistema gera o alerta
Entao Ana recebe notificacao em menos de 1 minuto via: push notification no app, email e badge no painel de alertas

Dado que Ana recebe o alerta
Quando ela visualiza os detalhes
Entao o alerta contem: ativo afetado, sensor, valor anomalo, severidade (Critica/Alta/Media/Baixa), timestamp, causa provavel e acao recomendada

Dado que Ana visualizou o alerta
Quando ela clica em "Reconhecer"
Entao o alerta muda de status "Novo" para "Reconhecido" e o timestamp do reconhecimento e registrado

Dado que existem multiplos alertas ativos
Quando Ana acessa o painel de alertas
Entao os alertas sao listados ordenados por severidade (Critica primeiro) e timestamp (mais recente primeiro)
```

---

#### US-008: Configurar thresholds de alerta por tipo de ativo

| Campo | Descricao |
|---|---|
| **ID** | US-008 |
| **Titulo** | Configurar thresholds de alerta por tipo de ativo |
| **Story** | Como **Marina (Analista de Confiabilidade)**, eu quero **configurar os thresholds de alerta para cada sensor por tipo de ativo**, para que **os alertas reflitam os limites operacionais reais de cada tipo de equipamento**. |
| **Prioridade** | Must Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | US-015 |

**Criterios de Aceite:**

```
Dado que Marina acessa a configuracao de thresholds para "Transformador de Potencia"
Quando ela define limites para temperatura do oleo (Normal: <80C, Alerta: 80-95C, Critico: >95C)
Entao o sistema salva os thresholds e os aplica a todos os ativos daquele tipo

Dado que Marina configura thresholds
Quando ela salva a configuracao
Entao o sistema exibe preview de quantos ativos seriam impactados (ex: "3 ativos atualmente em estado de Alerta com estes novos limites")

Dado que um ativo especifico tem caracteristicas diferentes do padrao do tipo
Quando Marina deseja customizar os thresholds para esse ativo individualmente
Entao ela pode criar um override especifico que prevalece sobre o threshold do tipo
```

---

#### US-019: Gerenciar regras de supressao de alarmes

| Campo | Descricao |
|---|---|
| **ID** | US-019 |
| **Titulo** | Gerenciar regras de supressao de alarmes |
| **Story** | Como **Ana (Operadora de Subestacao)**, eu quero **configurar regras de supressao temporaria de alarmes (ex: durante manutencao programada)**, para que **eu nao receba alertas irrelevantes durante janelas de manutencao**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 3 |
| **Dependencias** | US-003 |

**Criterios de Aceite:**

```
Dado que Ana sabe que um transformador entrara em manutencao
Quando ela cria uma regra de supressao informando: ativo, periodo (inicio/fim) e motivo
Entao alertas daquele ativo nao sao notificados durante o periodo, mas ficam registrados como "Suprimidos"

Dado que o periodo de supressao expirou
Quando novos alertas sao gerados para o ativo
Entao as notificacoes voltam ao comportamento normal automaticamente

Dado que Ana deseja ver alertas que foram suprimidos
Quando ela filtra alertas por status "Suprimido"
Entao o sistema exibe os alertas que ocorreram durante a supressao com a justificativa registrada
```

---

### Epico 5: Gestao de Casos e SOPs

---

#### US-004: Criar caso a partir de alerta

| Campo | Descricao |
|---|---|
| **ID** | US-004 |
| **Titulo** | Criar caso (ticket) a partir de alerta |
| **Story** | Como **Ana (Operadora de Subestacao)**, eu quero **criar um caso de investigacao a partir de um alerta**, para que **a situacao seja rastreada, investigada e resolvida com responsavel e prazo definidos**. |
| **Prioridade** | Must Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | US-003 |

**Criterios de Aceite:**

```
Dado que Ana esta visualizando um alerta ativo
Quando ela clica em "Criar Caso"
Entao o sistema cria um caso pre-preenchido com: ativo afetado, descricao do alerta, severidade, dados do sensor e link para o grafico de series temporais

Dado que o caso foi criado
Quando Ana atribui um responsavel (ex: Carlos) e define prioridade e prazo
Entao Carlos recebe notificacao do novo caso atribuido a ele com todos os detalhes

Dado que existem casos abertos
Quando Carlos acessa sua lista de casos
Entao ele ve todos os casos atribuidos a ele ordenados por prioridade e prazo, com indicadores de SLA

Dado que Carlos resolve o caso
Quando ele registra a resolucao (causa raiz, acao tomada, resultado)
Entao o caso muda para status "Resolvido" e o alerta original e atualizado com a resolucao
```

---

#### US-009: Visualizar SOP recomendado para tipo de alerta

| Campo | Descricao |
|---|---|
| **ID** | US-009 |
| **Titulo** | Visualizar SOP recomendado para tipo de alerta |
| **Story** | Como **Ana (Operadora de Subestacao)**, eu quero **ver o procedimento operacional padrao (SOP) recomendado quando um alerta e gerado**, para que **eu siga o procedimento correto de resposta para cada tipo de situacao**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | US-003, US-020 |

**Criterios de Aceite:**

```
Dado que um alerta e gerado para "Alta temperatura de oleo em transformador"
Quando Ana visualiza o detalhe do alerta
Entao o sistema exibe o SOP associado com passos numerados: (1) Verificar carga atual, (2) Verificar sistema de refrigeracao, (3) Medir temperatura ambiente, etc.

Dado que o SOP contem checklist de acoes
Quando Ana executa cada passo
Entao ela pode marcar cada item como concluido, registrando timestamp e observacoes

Dado que nao existe SOP cadastrado para um tipo especifico de alerta
Quando Ana visualiza o alerta
Entao o sistema exibe mensagem "SOP nao cadastrado para este tipo de alerta" com link para solicitar cadastro
```

---

#### US-020: Cadastrar e gerenciar SOPs

| Campo | Descricao |
|---|---|
| **ID** | US-020 |
| **Titulo** | Cadastrar e gerenciar SOPs |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **cadastrar procedimentos operacionais padrao (SOPs) e associa-los a tipos de alerta**, para que **os operadores tenham orientacao padronizada ao responder alertas**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 2 |
| **Dependencias** | - |

**Criterios de Aceite:**

```
Dado que Thiago acessa a area de gestao de SOPs
Quando ele cria um novo SOP informando: titulo, tipo de alerta associado, tipo de ativo, passos (com descricao e checklist)
Entao o SOP e salvo e automaticamente vinculado aos alertas do tipo correspondente

Dado que um SOP ja existe
Quando Thiago edita o SOP e salva uma nova versao
Entao a versao anterior e mantida no historico e a nova versao passa a ser exibida nos alertas futuros

Dado que Thiago deseja desativar um SOP
Quando ele muda o status para "Inativo"
Entao o SOP nao e mais exibido em novos alertas, mas permanece visivel em casos historicos que o referenciaram
```

---

#### US-021: Acompanhar historico e timeline do caso

| Campo | Descricao |
|---|---|
| **ID** | US-021 |
| **Titulo** | Acompanhar historico e timeline do caso |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **ver a timeline completa de um caso com todos os eventos, comentarios e acoes**, para que **eu entenda o historico completo da investigacao**. |
| **Prioridade** | Should Have |
| **Estimativa** | P |
| **Sprint** | 2 |
| **Dependencias** | US-004 |

**Criterios de Aceite:**

```
Dado que Carlos acessa um caso existente
Quando ele visualiza a timeline
Entao o sistema exibe em ordem cronologica: criacao do caso, atribuicoes, comentarios, mudancas de status, checklist do SOP e resolucao

Dado que Carlos deseja adicionar informacao ao caso
Quando ele escreve um comentario
Entao o comentario e adicionado a timeline com autor, timestamp e possibilidade de anexar imagens/documentos

Dado que o caso muda de responsavel
Quando a reatribuicao e feita
Entao a timeline registra quem reatribuiu, para quem, quando e o motivo
```

---

### Epico 6: Dashboard Executivo

---

#### US-005: Ver dashboard com KPIs de saude da frota

| Campo | Descricao |
|---|---|
| **ID** | US-005 |
| **Titulo** | Ver dashboard com KPIs de saude da frota |
| **Story** | Como **Roberto (Gerente de Operacoes)**, eu quero **ver um dashboard executivo com KPIs de saude da frota de ativos**, para que **eu tenha visao rapida do estado geral e possa identificar areas que precisam de atencao**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 2 |
| **Dependencias** | US-016 |

**Criterios de Aceite:**

```
Dado que Roberto acessa o dashboard
Quando a pagina carrega
Entao o sistema exibe: (1) Health Score medio da frota, (2) Quantidade de ativos por faixa de saude (Critico/Alerta/Normal), (3) Top 10 ativos em pior estado, (4) Tendencia de saude nos ultimos 90 dias, (5) Alertas abertos por severidade

Dado que o dashboard esta exibido
Quando Roberto aplica filtro por regiao (ex: "Regional Sudeste")
Entao todos os KPIs sao recalculados apenas para os ativos daquela regiao

Dado que Roberto clica em um KPI
Quando o KPI e um grafico ou numero agregado
Entao o sistema faz drill-down mostrando os ativos individuais que compoem aquele indicador

Dado que Roberto acessa o dashboard em diferentes momentos
Quando os dados mudam
Entao os KPIs sao atualizados automaticamente a cada 5 minutos sem necessidade de refresh manual
```

---

#### US-010: Exportar relatorio de saude de ativos

| Campo | Descricao |
|---|---|
| **ID** | US-010 |
| **Titulo** | Exportar relatorio de saude de ativos |
| **Story** | Como **Roberto (Gerente de Operacoes)**, eu quero **exportar um relatorio consolidado de saude dos ativos em PDF e Excel**, para que **eu possa apresentar a situacao a diretoria e orgaos reguladores (ANEEL)**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 3 |
| **Dependencias** | US-005 |

**Criterios de Aceite:**

```
Dado que Roberto esta no dashboard
Quando ele clica em "Exportar Relatorio" e seleciona o formato (PDF ou Excel)
Entao o sistema gera o relatorio com: resumo executivo, KPIs, lista de ativos criticos, graficos de tendencia e recomendacoes

Dado que Roberto deseja customizar o relatorio
Quando ele seleciona quais secoes incluir e o periodo de analise
Entao o relatorio e gerado apenas com as secoes e periodo selecionados

Dado que o relatorio PDF e gerado
Quando Roberto abre o arquivo
Entao o relatorio tem formatacao profissional com logotipo da empresa, data de geracao, numeracao de paginas e graficos de alta qualidade
```

---

#### US-022: Ver ranking de ativos por risco

| Campo | Descricao |
|---|---|
| **ID** | US-022 |
| **Titulo** | Ver ranking de ativos por risco |
| **Story** | Como **Roberto (Gerente de Operacoes)**, eu quero **ver um ranking dos ativos ordenados por nivel de risco combinando health score e criticidade do ativo**, para que **eu priorize investimentos e intervencoes nos ativos mais criticos**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 3 |
| **Dependencias** | US-016 |

**Criterios de Aceite:**

```
Dado que Roberto acessa o ranking de risco
Quando a pagina carrega
Entao o sistema exibe lista de ativos ordenada por indice de risco (combinacao de health score invertido x criticidade x impacto) com cores indicativas

Dado que Roberto deseja entender a composicao do risco
Quando ele clica em um ativo do ranking
Entao o sistema exibe o detalhamento: health score, criticidade, impacto na rede, historico de falhas e custo estimado de substituicao

Dado que Roberto filtra por tipo de ativo
Quando ele seleciona "Transformadores"
Entao o ranking mostra apenas transformadores com seus indicadores especificos de risco
```

---

### Epico 7: Energy Graph e Analise de Impacto

---

#### US-006: Consultar Energy Graph para analise de impacto

| Campo | Descricao |
|---|---|
| **ID** | US-006 |
| **Titulo** | Consultar Energy Graph para analise de impacto |
| **Story** | Como **Marina (Analista de Confiabilidade)**, eu quero **consultar o Energy Graph para entender as relacoes entre ativos e analisar o impacto em cascata de uma falha**, para que **eu possa avaliar o risco real de cada ativo considerando sua posicao na rede**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 3 |
| **Dependencias** | US-011, US-023 |

**Criterios de Aceite:**

```
Dado que Marina acessa o Energy Graph
Quando ela seleciona um ativo (ex: Transformador TR-01 da SE Campinas)
Entao o sistema renderiza o grafo mostrando: o ativo central, ativos conectados (disjuntores, barramentos), linhas de transmissao, subestacoes adjacentes e consumidores potencialmente afetados

Dado que o grafo esta renderizado
Quando Marina clica em "Analise de Impacto"
Entao o sistema calcula e exibe: numero de consumidores afetados, carga (MW) impactada, ativos redundantes disponiveis e tempo estimado para restauracao

Dado que Marina deseja simular a falha de um ativo
Quando ela ativa o modo "Simulacao" e remove um ativo do grafo
Entao o sistema recalcula a topologia e mostra o impacto na rede com destaque visual para areas afetadas
```

---

#### US-023: Cadastrar topologia da rede no Energy Graph

| Campo | Descricao |
|---|---|
| **ID** | US-023 |
| **Titulo** | Cadastrar topologia da rede no Energy Graph |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **cadastrar as relacoes entre ativos, subestacoes e linhas de transmissao no Energy Graph**, para que **o sistema tenha a topologia da rede para analise de impacto**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 2 |
| **Dependencias** | US-011 |

**Criterios de Aceite:**

```
Dado que Thiago acessa a area de configuracao do Energy Graph
Quando ele cria uma relacao entre dois ativos (ex: "Transformador TR-01" conectado_a "Disjuntor DJ-01")
Entao a relacao e salva no grafo com tipo de conexao, direcao e metadados

Dado que Thiago deseja importar a topologia completa
Quando ele faz upload de um arquivo de topologia (JSON/CSV com pares origem-destino)
Entao o sistema valida as referencias aos ativos e cria todas as relacoes de uma vez

Dado que a topologia foi cadastrada
Quando Thiago visualiza o grafo
Entao o sistema renderiza a topologia com nos (ativos) e arestas (conexoes) com indicadores visuais de health score por no
```

---

#### US-024: Visualizar mapa geografico dos ativos

| Campo | Descricao |
|---|---|
| **ID** | US-024 |
| **Titulo** | Visualizar mapa geografico dos ativos |
| **Story** | Como **Roberto (Gerente de Operacoes)**, eu quero **ver os ativos posicionados em um mapa geografico com indicadores de saude**, para que **eu tenha visao espacial da frota e identifique concentracoes de problemas por regiao**. |
| **Prioridade** | Could Have |
| **Estimativa** | G |
| **Sprint** | 3 |
| **Dependencias** | US-011 |

**Criterios de Aceite:**

```
Dado que Roberto acessa a visualizacao de mapa
Quando a pagina carrega
Entao o sistema exibe mapa do Brasil com marcadores nas posicoes das subestacoes, coloridos por health score medio (verde/amarelo/vermelho)

Dado que Roberto clica em um marcador de subestacao
Quando o popup abre
Entao o sistema mostra: nome da subestacao, quantidade de ativos, health score medio, piores ativos e link para detalhe

Dado que Roberto aplica zoom em uma regiao
Quando os marcadores se expandem
Entao o sistema mostra marcadores individuais de cada ativo com seu health score e status
```

---

### Stories Transversais

---

#### US-025: Autenticar no sistema com controle de acesso

| Campo | Descricao |
|---|---|
| **ID** | US-025 |
| **Titulo** | Autenticar no sistema com controle de acesso baseado em perfil |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **gerenciar usuarios com perfis de acesso diferenciados (Admin, Engenheiro, Operador, Gerente, Analista)**, para que **cada usuario acesse apenas as funcionalidades pertinentes ao seu papel**. |
| **Prioridade** | Must Have |
| **Estimativa** | G |
| **Sprint** | 1 |
| **Dependencias** | - |

**Criterios de Aceite:**

```
Dado que um usuario tenta acessar o sistema
Quando ele informa email e senha validos
Entao o sistema autentica, cria sessao e direciona para a pagina inicial do perfil do usuario

Dado que Thiago acessa a area de administracao de usuarios
Quando ele cria um novo usuario informando: nome, email, perfil e regionais de acesso
Entao o usuario recebe email de convite para definir sua senha e acessar o sistema

Dado que um usuario com perfil "Operador" tenta acessar a area de configuracao do sistema
Quando o sistema verifica permissoes
Entao o acesso e negado com mensagem "Voce nao tem permissao para acessar esta funcionalidade"
```

---

#### US-026: Registrar log de auditoria de acoes

| Campo | Descricao |
|---|---|
| **ID** | US-026 |
| **Titulo** | Registrar log de auditoria de acoes no sistema |
| **Story** | Como **Thiago (Admin do Sistema)**, eu quero **que todas as acoes relevantes sejam registradas em log de auditoria**, para que **haja rastreabilidade completa para fins regulatorios e de seguranca**. |
| **Prioridade** | Must Have |
| **Estimativa** | M |
| **Sprint** | 1 |
| **Dependencias** | US-025 |

**Criterios de Aceite:**

```
Dado que um usuario realiza uma acao no sistema (login, criacao, edicao, exclusao, exportacao)
Quando a acao e executada
Entao o sistema registra: usuario, acao, entidade afetada, timestamp, IP e detalhes da mudanca (valor anterior/novo)

Dado que Thiago acessa o log de auditoria
Quando ele filtra por usuario, periodo ou tipo de acao
Entao o sistema exibe os registros filtrados em ordem cronologica

Dado que registros de auditoria existem
Quando qualquer usuario tenta editar ou excluir registros de auditoria
Entao o sistema bloqueia a acao (registros de auditoria sao imutaveis)
```

---

#### US-027: Configurar notificacoes por canal preferido

| Campo | Descricao |
|---|---|
| **ID** | US-027 |
| **Titulo** | Configurar preferencias de notificacao |
| **Story** | Como **Ana (Operadora de Subestacao)**, eu quero **configurar por quais canais desejo receber notificacoes e para quais severidades**, para que **eu receba apenas alertas relevantes pelos canais que monitoro**. |
| **Prioridade** | Should Have |
| **Estimativa** | P |
| **Sprint** | 2 |
| **Dependencias** | US-003, US-025 |

**Criterios de Aceite:**

```
Dado que Ana acessa suas preferencias de notificacao
Quando ela configura: email (todas severidades), push (apenas Critica e Alta), SMS (apenas Critica)
Entao o sistema respeita essas preferencias ao enviar notificacoes

Dado que Ana deseja silenciar notificacoes temporariamente
Quando ela ativa o modo "Nao Perturbe" com periodo (ex: 22h-06h)
Entao alertas desse periodo sao acumulados e entregues ao final do periodo silenciado

Dado que as configuracoes foram salvas
Quando um novo alerta e gerado
Entao Ana recebe notificacao apenas pelos canais configurados para a severidade daquele alerta
```

---

#### US-028: Buscar ativos e alertas globalmente

| Campo | Descricao |
|---|---|
| **ID** | US-028 |
| **Titulo** | Busca global de ativos, alertas e casos |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **buscar rapidamente qualquer ativo, alerta ou caso pelo nome, ID ou atributo**, para que **eu encontre informacoes rapidamente sem navegar por multiplas telas**. |
| **Prioridade** | Should Have |
| **Estimativa** | M |
| **Sprint** | 3 |
| **Dependencias** | US-001, US-003, US-004 |

**Criterios de Aceite:**

```
Dado que Carlos esta em qualquer pagina do sistema
Quando ele digita no campo de busca global (Ctrl+K ou barra de busca no topo)
Entao o sistema exibe resultados em tempo real agrupados por tipo: Ativos, Alertas, Casos, com link direto para cada resultado

Dado que Carlos busca por "TR-01"
Quando os resultados sao exibidos
Entao o sistema mostra: o ativo "Transformador TR-01", alertas recentes do TR-01 e casos abertos do TR-01

Dado que Carlos busca por um termo sem resultados
Quando nenhum resultado e encontrado
Entao o sistema exibe "Nenhum resultado encontrado" com sugestoes de termos similares
```

---

#### US-029: Comparar health score entre ativos

| Campo | Descricao |
|---|---|
| **ID** | US-029 |
| **Titulo** | Comparar health score entre ativos similares |
| **Story** | Como **Marina (Analista de Confiabilidade)**, eu quero **comparar o health score e indicadores de dois ou mais ativos do mesmo tipo lado a lado**, para que **eu identifique diferencas de desempenho e possa investigar as causas**. |
| **Prioridade** | Could Have |
| **Estimativa** | M |
| **Sprint** | 3 |
| **Dependencias** | US-002, US-016 |

**Criterios de Aceite:**

```
Dado que Marina esta na lista de ativos
Quando ela seleciona 2 a 4 ativos do mesmo tipo e clica em "Comparar"
Entao o sistema exibe pagina de comparacao com graficos sobrepostos de health score e indicadores lado a lado

Dado que a comparacao esta exibida
Quando Marina seleciona um indicador especifico (ex: temperatura do oleo)
Entao o sistema exibe graficos sobrepostos de series temporais daquele indicador para os ativos selecionados

Dado que ha diferencas significativas entre os ativos
Quando Marina analisa a comparacao
Entao o sistema destaca os indicadores onde ha divergencia maior que 20% entre os ativos comparados
```

---

#### US-030: Acessar plataforma via dispositivo movel

| Campo | Descricao |
|---|---|
| **ID** | US-030 |
| **Titulo** | Acessar plataforma via dispositivo movel (responsivo) |
| **Story** | Como **Carlos (Engenheiro de Manutencao)**, eu quero **acessar as funcionalidades essenciais da plataforma pelo celular em campo**, para que **eu consulte dados de ativos e responda a alertas mesmo quando nao estou no escritorio**. |
| **Prioridade** | Could Have |
| **Estimativa** | G |
| **Sprint** | 3 |
| **Dependencias** | US-001, US-003 |

**Criterios de Aceite:**

```
Dado que Carlos acessa o OntoGrid pelo navegador do celular
Quando a pagina carrega
Entao o layout e responsivo, adaptado para tela pequena, com navegacao por menu hamburguer e cards otimizados

Dado que Carlos esta no celular
Quando ele visualiza a lista de ativos
Entao os cards mostram: nome, tipo, health score e status de forma legivel sem necessidade de scroll horizontal

Dado que Carlos recebe push notification de alerta
Quando ele toca na notificacao
Entao o navegador abre diretamente na pagina de detalhe do alerta com todas as informacoes relevantes
```

---

## 4. Matriz de Priorizacao (MoSCoW)

### Must Have (Sprint 1-2) - Essencial para o MVP funcionar

| ID | Story | Sprint | Esforco |
|---|---|---|---|
| US-025 | Autenticar no sistema com controle de acesso | 1 | G |
| US-026 | Registrar log de auditoria | 1 | M |
| US-011 | Cadastrar novo ativo | 1 | M |
| US-001 | Ver lista de ativos com health score | 1 | M |
| US-002 | Ver detalhe de ativo com series temporais | 1 | G |
| US-015 | Configurar mapeamento de sensores | 1 | M |
| US-007 | Ingerir dados SCADA via CSV/API | 1 | G |
| US-016 | Calcular health score baseado em regras | 1 | G |
| US-017 | Detectar anomalias em series temporais | 2 | G |
| US-003 | Receber alerta quando anomalia detectada | 2 | G |
| US-008 | Configurar thresholds de alerta | 2 | M |
| US-004 | Criar caso a partir de alerta | 2 | M |
| US-005 | Ver dashboard com KPIs de saude da frota | 2 | G |
| US-023 | Cadastrar topologia no Energy Graph | 2 | G |
| US-006 | Consultar Energy Graph para analise de impacto | 3 | G |

### Should Have (Sprint 2-3) - Importante, agrega valor significativo

| ID | Story | Sprint | Esforco |
|---|---|---|---|
| US-012 | Importar ativos em lote via CSV | 2 | M |
| US-013 | Visualizar hierarquia de ativos | 2 | M |
| US-014 | Monitorar status da ingestao em tempo real | 2 | M |
| US-009 | Visualizar SOP recomendado | 2 | M |
| US-020 | Cadastrar e gerenciar SOPs | 2 | M |
| US-021 | Acompanhar historico e timeline do caso | 2 | P |
| US-027 | Configurar notificacoes por canal | 2 | P |
| US-018 | Visualizar tendencia de degradacao | 3 | G |
| US-010 | Exportar relatorio de saude | 3 | M |
| US-022 | Ver ranking de ativos por risco | 3 | M |
| US-019 | Gerenciar regras de supressao de alarmes | 3 | M |
| US-028 | Busca global de ativos, alertas e casos | 3 | M |

### Could Have (Sprint 3) - Desejavel, pode ser movido para pos-MVP

| ID | Story | Sprint | Esforco |
|---|---|---|---|
| US-024 | Visualizar mapa geografico dos ativos | 3 | G |
| US-029 | Comparar health score entre ativos | 3 | M |
| US-030 | Acessar plataforma via dispositivo movel | 3 | G |

---

## 5. Story Map Visual (ASCII)

```
                                ONTOGRID MVP - ASSET HEALTH STORY MAP
========================================================================================

JORNADA DO      Configurar       Monitorar        Analisar          Agir            Reportar
USUARIO         Plataforma       Ativos           Saude             sobre Alertas   Resultados
                    |                |                |                 |                |
========================================================================================
SPRINT 1        US-025           US-011           US-016            (Sprint 2)      (Sprint 2)
(Fundacao)      Autenticacao     Cadastrar        Health Score
                e Controle       Ativo            por Regras
                de Acesso            |                |
                    |            US-001               |
                US-026           Lista de          US-015
                Auditoria        Ativos +          Mapeamento
                                 Health Score      de Sensores
                    |                |
                                 US-002
                US-007           Detalhe do
                Ingestao         Ativo + Series
                SCADA            Temporais
                CSV/API
========================================================================================
SPRINT 2            |                |                |                 |                |
(Core)          US-012           US-013           US-017            US-003           US-005
                Import           Hierarquia       Detectar          Receber          Dashboard
                Ativos           de Ativos        Anomalias         Alerta           KPIs
                CSV                                                     |
                    |            US-014               |             US-004           US-023
                US-020           Status           US-008            Criar            Topologia
                Gerenciar        Ingestao         Config.           Caso             Energy
                SOPs             Real-time        Thresholds            |             Graph
                                                                   US-009
                                                                   Ver SOP
                                                                       |
                                                                   US-021
                US-027                                             Timeline
                Config.                                            do Caso
                Notificacoes
========================================================================================
SPRINT 3            |                |                |                 |                |
(Avancado)                       US-024           US-018            US-019           US-010
                                 Mapa             Tendencia         Supressao        Exportar
                                 Geografico       Degradacao        de Alarmes       Relatorio
                                 [Could]              |                              PDF/Excel
                                                  US-029                |
                                 US-028           Comparar          US-006           US-022
                                 Busca            Ativos            Energy           Ranking
                                 Global           [Could]           Graph            por Risco
                                                                   Impacto
                                                  US-030
                                                  Acesso
                                                  Mobile
                                                  [Could]
========================================================================================

LEGENDA:
  [Could] = Could Have (pode ser movido para pos-MVP)
  Demais stories = Must Have ou Should Have
  Setas verticais (|) indicam dependencia dentro do mesmo sprint
  Leitura horizontal = jornada do usuario
  Leitura vertical = profundidade funcional por sprint
```

---

## Apendice: Resumo Quantitativo

| Metrica | Valor |
|---|---|
| **Total de User Stories** | 30 |
| **Must Have** | 15 (50%) |
| **Should Have** | 12 (40%) |
| **Could Have** | 3 (10%) |
| **Sprint 1** | 8 stories |
| **Sprint 2** | 13 stories |
| **Sprint 3** | 9 stories |
| **Esforco P (Pequeno)** | 2 stories |
| **Esforco M (Medio)** | 15 stories |
| **Esforco G (Grande)** | 13 stories |
| **Personas cobertas** | 5 (Carlos, Ana, Roberto, Marina, Thiago) |
| **Epicos cobertos** | 7 |
