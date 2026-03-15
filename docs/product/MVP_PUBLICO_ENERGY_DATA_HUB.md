# MVP Publico - Energy Data Hub

- Status: oficial para o MVP vigente
- Escopo: produto inicial, sem dependencia de dados privados do cliente

## Objetivo

Entregar um hub publico de dados do setor eletrico brasileiro que combine catalogo amplo, versionamento, entidades canonicas, visualizacao estruturada e copilot grounded. O MVP quer **catalogar os 345 datasets inventariados** de ANEEL, ONS e CCEE, mesmo que nem todos estejam ingeridos e publicados em todo ambiente.

## Fontes e cobertura alvo

- **ANEEL**: 69 datasets inventariados
- **ONS**: 80 datasets inventariados
- **CCEE**: 196 datasets inventariados
- **Total alvo do catalogo**: 345 datasets

O estado oficial de catalogacao e cobertura do repo fica em [CATALOG_STATUS.md](/C:/Users/tsimoe01/coding/ontogrid/docs/datasets/CATALOG_STATUS.md).

## Arquitetura principal da UX

O produto tem **5 paginas top-level**:

1. `Analysis`: o usuario escolhe um dataset e recebe tabelas e graficos estruturados sobre esse dataset.
2. `Entities`: eixo canonico de navegacao e agregacao cross-dataset. Nao e browser de ontologia geral.
3. `Datasets`: catalogo operacional com status, familia, fonte, cobertura e entrada para detalhe e versoes.
4. `Copilot`: IA grounded em datasets, entidades, versoes e metadados.
5. `Settings`: pagina top-level prevista, ainda nao construida.

Drill-downs secundarios continuam existindo para dataset, versao e entidade.

## Regra de produto sobre entidades e grafo

- `Entities` e a experiencia principal de identidade setorial do produto.
- Uma entidade e um substantivo recorrente em muitos datasets, com identidade resolvivel e que merece experiencia propria.
- O grafo e a infraestrutura de suporte para vizinhanca, reconciliacao e contexto relacional.
- Neo4j continua no MVP, mas nao define a IA principal do frontend.

## Capacidade minima do MVP

- catalogo completo dos 345 datasets inventariados;
- refresh e versionamento dos datasets com adapter implementado;
- camada curada para `Analysis`, `Entities` e `Copilot`;
- entidades canonicas, aliases e relacoes setoriais;
- APIs REST para catalogo, series, cobertura, entidades, grafo, insights e copilot;
- copilot analitico grounded em dados publicados e evidencia rastreavel.

## Regra de ingestao e ambiente local

- o frontend nunca carrega arquivo bruto;
- o backend serve apenas a camada curada;
- um `dataset_version` pode ser composto por multiplos arquivos de origem;
- o ambiente local deve usar `catalog` ou `sample` por padrao;
- ingestao live pesada fica para uso explicito ou ambiente centralizado.

## Valor entregue sem onboarding de cliente

- acesso rapido ao universo de datasets publicos do repositorio;
- navegacao por entidades canonicas cross-dataset;
- exploracao estruturada de datasets priorizados;
- visao clara do que esta apenas catalogado, do que ja tem adapter e do que ja foi publicado em um ambiente;
- resposta guiada por IA com citacoes de datasets, versoes e entidades.

## O que o MVP nao precisa

- SCADA, historian, ERP, OMS, CMMS ou GIS do cliente;
- upload manual de planilhas do cliente como fluxo principal;
- grafo como pagina principal da UX;
- download local completo do universo real de dados por padrao;
- workflow operacional rico, field assistant ou forecasting pesado.

## Criterio de aceite do MVP

- os **345 datasets** estao catalogados no produto;
- a documentacao deixa claro quantos datasets estao catalogados, com adapter e publicados;
- a navegacao principal do app esta organizada em `Analysis`, `Entities`, `Datasets`, `Copilot` e `Settings`;
- `Entities` esta descrita como eixo canonico cross-dataset e nao como browser de ontologia geral;
- o runtime local nao depende de baixar o universo completo de dados reais para subir o app;
- a documentacao diferencia claramente estado do repo de estado operacional do ambiente.
