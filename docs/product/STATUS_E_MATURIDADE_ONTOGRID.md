# Status e Maturidade do Produto - OntoGrid

- Status: documento de alinhamento de produto
- Escopo: fotografia clara do que o repo ja cobre e do que ainda falta para fechar o MVP publico

## Leitura executiva

Hoje a OntoGrid esta em:

> **Energy Data Hub publico v1 em construcao, com catalogo amplo e ingestao seletiva**

Isso significa:

- o recorte do produto ja esta claro;
- os **345 datasets** ja estao inventariados e catalogados no repo;
- apenas parte do universo ja possui adapter e publicacao operacional;
- a UX principal ja esta organizada em `Analysis`, `Entities`, `Datasets`, `Copilot` e `Settings`.

## Fonte de verdade

Para evitar misturar estado do repo com estado do ambiente:

- **estado do repo**: [CATALOG_STATUS.md](/C:/Users/tsimoe01/coding/ontogrid/docs/datasets/CATALOG_STATUS.md)
- **estado operacional do ambiente**: `GET /api/v1/catalog/coverage`

Regra:

- `catalogado` e compromisso do repo
- `publicado` e estado do ambiente

## Snapshot atual do repo

| Fonte | Total catalogado | Adapter pronto | Pendente de adapter |
|---|---:|---:|---:|
| ANEEL | 69 | 4 | 65 |
| ONS | 80 | 3 | 77 |
| CCEE | 196 | 4 | 192 |
| **Total** | **345** | **11** | **334** |

## O que significa fechar o MVP

Fechar o MVP nao e baixar o universo completo localmente. E:

- manter os **345 datasets** visiveis no catalogo;
- dar status claro do que esta apenas catalogado, com adapter e publicado;
- operar `Analysis`, `Entities`, `Datasets`, `Copilot` e `Settings` como IA oficial do produto;
- manter o runtime local leve por padrao;
- tratar `Entities` como experiencia de produto e o grafo como infraestrutura de suporte;
- publicar um conjunto priorizado de datasets com qualidade suficiente para demonstracao e uso inicial.

## O que ja esta resolvido conceitualmente

- o produto e public-first;
- o catalogo total ja esta definido;
- a navegacao principal do frontend esta definida;
- a separacao entre repo status e ambiente operacional esta definida;
- a arquitetura local deixou de assumir ingestao live total por padrao.

## O que ainda falta endurecer

- ampliar adapters alem dos 11 datasets atuais;
- materializar mais datasets em ambiente compartilhado;
- endurecer a reconciliacao de entidades e aliases;
- consolidar a camada curada para `Analysis`, `Entities` e `Copilot`;
- tornar coverage e bootstrap operacionais mais visiveis na UX e na automacao.

## Regra de comunicacao

Quando houver duvida de narrativa, usar esta frase:

> A OntoGrid esta construindo um Energy Data Hub publico que cataloga 345 datasets de ANEEL, ONS e CCEE, organiza a UX em Analysis, Entities, Datasets, Copilot e Settings, e usa ingestao seletiva para manter o runtime local leve e escalavel.
