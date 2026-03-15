# Pipeline de Ingestao - OntoGrid Energy Data Hub MVP

Este documento descreve a ingestao suportada no MVP publico com linguagem simples e foco em escalabilidade.

## Ideia central

O produto quer conhecer **345 datasets** no catalogo, mas isso **nao** significa baixar historico completo de tudo em todo ambiente.

O fluxo correto e:

1. manter o catalogo completo;
2. ingerir seletivamente apenas o que cada ambiente precisa;
3. servir o app a partir de uma camada curada;
4. nunca mandar arquivo bruto para o frontend.

## Tres camadas de dado

### 1. Arquivo original

E o arquivo como veio da fonte:

- CSV
- XLSX
- JSON
- ZIP
- um arquivo por ano
- varios arquivos para o mesmo dataset

Esses arquivos ficam no backend/storage.

### 2. Camada curada

E a representacao organizada que o produto realmente consulta:

- `dataset_version`
- `entity`
- `entity_alias`
- `relation`
- `metric_series`
- `observation`

### 3. Resposta do app

E o recorte enviado para o frontend:

- tabela
- grafico
- cards
- resposta do copilot

O frontend nunca baixa o bruto inteiro.

## Regras de modelagem da ingestao

- um `dataset` pode ter `N dataset_version`;
- um `dataset_version` pode ter `N dataset_artifact`;
- um dataset pode ser composto por varios arquivos de origem;
- os arquivos originais ficam preservados no backend/storage;
- a camada curada e o que abastece `Analysis`, `Entities` e `Copilot`.

## Regra de processamento

O alvo arquitetural **nao** e:

- ler arquivo inteiro em memoria;
- juntar anos inteiros em um unico arquivo gigante;
- fazer o frontend processar dataset bruto.

O alvo arquitetural e:

- processamento por lote ou streaming;
- suporte a datasets particionados por ano, mes ou recurso;
- publicacao seletiva da camada curada;
- reprocessamento rastreavel por versao e por artifact.

## Ambientes e bootstrap

### Local

- conhece os 345 datasets no catalogo;
- usa `BOOTSTRAP_MODE=catalog` ou `BOOTSTRAP_MODE=sample`;
- pode usar `BOOTSTRAP_MODE=selected_live` apenas para poucos datasets escolhidos;
- nunca deve baixar o universo completo por padrao.

### Shared/Staging/Prod

- concentra ingestao live pesada;
- publica datasets priorizados;
- preserva os arquivos originais e a camada curada em storage apropriado.

## Comandos oficiais

- `python -m app.cli bootstrap-catalog`
- `python -m app.cli bootstrap-sample-data`
- `python -m app.cli bootstrap-selected-live-data`

## Observabilidade minima

- dataset, versao e artifact precisam ser rastreaveis;
- refresh job precisa mostrar leitura, escrita e falha;
- `publicado` precisa ser lido por ambiente, nao por snapshot do git;
- coverage do ambiente precisa ser separado do snapshot do repo.
