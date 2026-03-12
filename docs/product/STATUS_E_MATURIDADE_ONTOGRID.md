# Status e Maturidade do Produto - OntoGrid

- Status: documento de alinhamento de produto
- Escopo: visao clara de onde o projeto esta, o que significa fechar o MVP e qual e a sequencia ate o end-state
- Uso recomendado: steering de produto, priorizacao de backlog, alinhamento com parceiros, design partners e investidores

## 1. Objetivo deste documento

Este documento responde, de forma objetiva, a quatro perguntas:

1. Em que etapa a OntoGrid esta hoje.
2. O que significa dizer que o MVP esta 100% e pronto para entrega.
3. O que caracteriza a primeira versao do produto real.
4. Qual e o end-state do produto construido.

A intencao aqui nao e substituir os documentos de arquitetura, roadmap e estrategia. A funcao deste arquivo e servir como um **quadro de comando** do projeto.

## 2. Fonte de verdade e regra de leitura

Este documento deve ser lido com a seguinte hierarquia de referencia:

1. `README.md`
2. `docs/product/MVP_PUBLICO_ENERGY_DATA_HUB.md`
3. `docs/product/MVP_ROADMAP.md`
4. `docs/platform/ARQUITETURA_DE_CAMADAS.md`
5. `docs/platform/ARCHITECTURE.md`
6. `docs/platform/DATA_MODEL.md`
7. `docs/strategy/PORTFOLIO_E_ROADMAP.md`

### Regra pratica

Se houver conflito entre o recorte do MVP atual e documentos estrategicos mais antigos, prevalece o recorte **public-first do Energy Data Hub**.

Em termos simples:

- o MVP atual e **publico**;
- a fase seguinte e o **Enterprise Data Plane**;
- suites operacionais e workflows enterprise ficam **depois**;
- o end-state continua sendo uma plataforma mais ampla de dados, ontologia, analytics e IA aplicada.

## 3. Leitura executiva

**Hoje, a OntoGrid esta em:**

> **Energy Data Hub publico v1 em construcao**

Ou seja: o projeto ja passou da fase de tese e da fase de documentacao solta. O recorte do MVP esta definido e o repositorio ja aponta para um build real do hub publico.

**O proximo marco e:**

> **MVP publico 100% e pronto para ser entregue**

Este marco nao muda o produto. Ele fecha, estabiliza e torna demonstravel o que ja foi escolhido como escopo do MVP.

**A primeira versao do produto real e:**

> **Energy Data Hub SaaS v1**

Aqui o MVP deixa de ser apenas um artefato tecnico demonstravel e vira um produto repetivel, apresentavel e comercializavel.

**O end-state e:**

> **Plataforma federada de dados, ontologia, analytics, apps e IA governada para o setor eletrico brasileiro**

## 4. Mapa geral de maturidade

```text
Versao atual do MVP
        ->
MVP 100% e pronto para entrega
        ->
Primeira versao do produto real
        ->
End-state do produto construido
```

## 5. Matriz principal

| Etapa | Nome pratico | Status | Pergunta que responde |
|---|---|---|---|
| 1 | Versao atual do MVP | Em andamento | Ja existe um hub publico funcional e coerente? |
| 2 | MVP 100% | Proximo marco | O recorte escolhido esta fechado, estavel e entregavel? |
| 3 | Produto real v1 | Depois do MVP | O produto ja e repetivel, usavel e comercializavel? |
| 4 | End-state | Longo prazo | A OntoGrid ja virou a plataforma setorial completa que queremos construir? |

---

## 6. Etapa 1 - Versao atual do MVP

### Nome da etapa

**Energy Data Hub publico v1 em construcao**

### O que esta dentro do escopo

- ingestao e curadoria de dados publicos de ANEEL, ONS e CCEE;
- catalogo de fontes e datasets publicos;
- refresh e versionamento de datasets;
- harmonizacao temporal e semantica;
- Energy Graph publico com entidades, aliases e relacoes;
- APIs REST para catalogo, series, grafo e insights;
- dashboards base para exploracao;
- copilot analitico grounded em dados e metadados.

### O que ja deve existir nesta etapa

- recorte do MVP fechado e documentado;
- contratos HTTP definidos;
- arquitetura tecnica definida;
- modelo canonico de dados definido;
- stack local e runtime de desenvolvimento padronizados;
- um slice funcional do hub publico implementado no repo.

### O que ainda pode faltar nesta etapa

- cobertura mais ampla dos datasets prioritarios;
- reconciliacao mais forte de entidades, aliases e relacoes;
- dashboards mais completos sobre APIs reais;
- observabilidade mais madura do pipeline e do runtime;
- endurecimento operacional do copilot grounded.

### Como saber que ainda estamos nesta etapa

Ainda estamos aqui quando a pergunta principal for:

> "O MVP ja existe tecnicamente, mas ainda precisa ser fechado e endurecido para entrega?"

Se a resposta for sim, ainda estamos na etapa 1.

### Criterio de saida da etapa 1

Voce sai desta etapa quando o MVP publico puder ser considerado **completo no recorte que escolheu**, e nao apenas promissor.

---

## 7. Etapa 2 - MVP 100% e pronto para ser entregue

### Nome da etapa

**MVP publico entregavel**

### O que muda em relacao a etapa anterior

O produto continua sendo o mesmo. A diferenca e que agora ele esta:

- fechado no escopo;
- consistente de ponta a ponta;
- demonstravel sem improviso;
- operacionalmente confiavel para uso real inicial.

### O que precisa estar verdadeiro nesta etapa

#### Dados publicos

- pelo menos um conjunto prioritario de dados de ANEEL, ONS e CCEE esta catalogado e versionado;
- refresh e lineage funcionam sem quebrar a ultima versao valida;
- o usuario consegue confiar em dataset, versao e proveniencia.

#### Semantica e grafo

- entidades publicas ja aparecem de forma coerente;
- aliases e relacoes permitem navegacao util;
- o grafo responde consultas de contexto e vizinhanca.

#### Produto

- a interface permite navegar catalogo, datasets, versoes, entidades e series;
- dashboards base entregam contexto real;
- o copilot responde perguntas grounded em dados e metadados.

#### Operacao minima

- pipeline e runtime tem observabilidade minima;
- falhas de refresh nao corrompem o estado publicado;
- cache, custo e comportamento do copilot estao sob controle.

### Criterio de saida da etapa 2

Voce sai desta etapa quando puder afirmar, sem ressalva grande:

> "O MVP publico da OntoGrid esta pronto para ser apresentado, testado com usuarios reais e entregue como produto inicial."

---

## 8. Etapa 3 - Primeira versao do produto real

### Nome da etapa

**Energy Data Hub SaaS v1**

### Definicao pratica

A primeira versao do produto real nao e o end-state e tambem nao precisa incluir o Enterprise Data Plane completo.

Ela e a primeira versao em que o hub publico deixa de ser apenas um MVP tecnico e passa a ser:

- um produto usavel de forma recorrente;
- uma oferta clara para usuarios externos;
- uma porta de entrada comercial para a plataforma maior.

### O que caracteriza esta etapa

- proposta de valor muito clara para analistas, consultorias, comercializadoras, pesquisadores e energytechs;
- APIs, dashboards e copilot bons o suficiente para uso repetido;
- onboarding simples para uso do produto publico;
- narrativa comercial coerente;
- telemetria e operacao basicas para sustentar uso continuo.

### O que ainda nao precisa estar completo

- conectores privados genericos em larga escala;
- tenancy como pivô universal do produto;
- suites operacionais completas;
- automacao enterprise profunda.

### Resultado esperado desta etapa

A OntoGrid deixa de ser vista apenas como um "projeto promissor" e passa a ser percebida como um **produto real com uso e valor proprios**.

### Criterio de saida da etapa 3

Voce sai desta etapa quando o hub publico ja funcionar como **produto em si** e, ao mesmo tempo, abrir caminho natural para a camada enterprise.

---

## 9. Etapa 4 - End-state do produto construido

### Nome da etapa

**Plataforma setorial federada de dados e decisao**

### Definicao pratica

Neste estado, a OntoGrid deixa de ser apenas um hub publico excelente e passa a operar como uma plataforma completa para o setor eletrico, combinando:

- dados publicos curados;
- dados privados federados do cliente;
- ontologia e identidade setorial;
- lineage, qualidade e auditabilidade;
- analytics e exploracao semantica;
- copilots e IA governada;
- apps operacionais e regulatorios.

### Capacidades esperadas no end-state

- Enterprise Data Plane tenant-scoped;
- conectores privados para sistemas do cliente;
- fusao de contexto publico e privado no grafo;
- modulos operacionais reutilizando a mesma semantica;
- IA grounded e auditavel em toda a plataforma;
- benchmarking federado, clean room e colaboracao setorial quando fizer sentido.

### Criterio de saida da etapa 4

Nao ha uma "saida" no sentido tradicional. Esta e a visao alvo do produto.

A pergunta aqui deixa de ser "o MVP esta pronto?" e passa a ser:

> "A OntoGrid ja e a camada comum de dados, semantica e decisao do setor eletrico para uso publico e enterprise?"

---

## 10. Heatmap de capacidades por etapa

| Capacidade | Versao atual do MVP | MVP 100% | Produto real v1 | End-state |
|---|---|---|---|---|
| Escopo publico fechado | Alto | Fechado | Fechado | Fechado |
| Catalogo de fontes e datasets | Parcial/alto | Fechado | Fechado | Fechado |
| Refresh e versionamento | Parcial | Fechado | Fechado | Avancado |
| Cobertura dos datasets prioritarios | Parcial | Boa o suficiente para entrega | Boa e orientada a uso | Ampla |
| Ontologia e Energy Graph publico | Parcial/alto | Fechado no MVP | Maduro para uso | Federado publico + privado |
| APIs REST do hub | Parcial/alto | Fechado | Estavel para consumo | Estavel e expandido |
| Dashboards base | Parcial | Fechado | Melhorado para uso recorrente | Suite ampla |
| Copilot grounded | Parcial | Operacional | Usavel de forma recorrente | Amplo e governado |
| Observabilidade e operacao | Inicial | Minimo aceitavel | Sustentavel | Avancado |
| Oferta comercial repetivel | Nao | Ainda nao | Sim | Sim |
| Dados privados federados | Nao | Nao | Inicial ou adjacente | Sim |
| Apps operacionais | Nao | Nao | Nao ou muito inicial | Sim |

---

## 11. O que fazer agora e o que nao fazer ainda

### O que fazer agora

- fechar cobertura suficiente dos datasets publicos prioritarios;
- endurecer reconciliacao semantica de entidades, aliases e relacoes;
- consolidar UX minima de catalogo, dataset, entidade, series, grafo e insights;
- endurecer observabilidade do pipeline e do runtime;
- tornar o copilot grounded mais confiavel e operacional.

### O que nao fazer ainda

- expandir o escopo para um framework generico de conectores enterprise;
- tratar tenancy como pivô central do produto antes da hora;
- abrir muitas frentes de apps operacionais em paralelo;
- reabrir a discussao de escopo do MVP para voltar a depender de dados privados;
- perseguir o end-state antes de fechar o wedge publico.

---

## 12. Checklist de saida da fase atual

Use a lista abaixo como definicao pratica de "MVP 100%":

- [ ] ha cobertura suficiente de datasets prioritarios de ANEEL, ONS e CCEE;
- [ ] datasets, versoes e lineage estao navegaveis e confiaveis;
- [ ] pelo menos um fluxo completo catalogo -> dataset -> versao -> serie -> observacao funciona sem remendo;
- [ ] entidades e relacoes do grafo entregam contexto util;
- [ ] a UI consegue navegar catalogo, dataset, entidade, series e insights;
- [ ] o copilot responde perguntas grounded com citacoes consistentes;
- [ ] refresh falha sem corromper a ultima versao valida;
- [ ] existe observabilidade minima para operacao local e demonstracao;
- [ ] a documentacao do repo deixa claro o que e MVP, o que vem depois e o que ainda esta fora de escopo.

Quando todos os itens acima estiverem resolvidos, a OntoGrid sai de **"MVP em construcao"** e entra em **"MVP 100% e pronto para ser entregue"**.

---

## 13. Regra de comunicacao do projeto

Para evitar confusao de narrativa, adote esta linguagem:

### Frase curta para o momento atual

> A OntoGrid esta construindo o MVP publico v1 de um Energy Data Hub semantico para o setor eletrico brasileiro.

### Frase curta para o proximo marco

> O objetivo imediato e fechar um MVP publico 100% entregavel, com dados curados, grafo publico, APIs e copilot grounded.

### Frase curta para a proxima camada de produto

> A camada seguinte e transformar esse MVP em um produto SaaS real e, depois, expandi-lo para um Enterprise Data Plane federado.

### Frase curta para a visao final

> O end-state e uma plataforma brasileira de dados, ontologia, analytics, apps e IA governada para o setor eletrico.

---

## 14. Resumo em uma linha

**Hoje:** MVP publico em construcao  
**Proximo marco:** MVP publico 100% entregavel  
**Depois:** Energy Data Hub SaaS v1  
**Visao final:** plataforma federada de dados, ontologia, apps e IA para o setor eletrico brasileiro
