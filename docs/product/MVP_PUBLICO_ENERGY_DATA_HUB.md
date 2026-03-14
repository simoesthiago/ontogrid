# MVP Publico - Energy Data Hub

- Status: oficial para o MVP vigente
- Escopo: produto inicial, sem dependencia de dados privados do cliente

## Objetivo

Entregar um hub publico de dados do setor eletrico brasileiro que combine curadoria, versionamento, ontologia, visualizacao e IA aplicada. O MVP precisa ser util mesmo para quem ainda nao integrou nenhum dado proprietario.

## Fontes iniciais fechadas

- **ANEEL**: bases regulatarias, tarifarias e cadastrais priorizadas para navegacao e contexto.
- **ONS**: series operacionais e datasets de rede/operacao em formatos consumiveis.
- **CCEE**: datasets publicos de preco e mercado liberados para consulta publica.

EPE e outras fontes entram como expansao logo apos o nucleo inicial.

## Capacidade minima do MVP

- catalogo de fontes e datasets publicos;
- refresh e versionamento de datasets;
- harmonizacao temporal e semantica;
- Energy Graph publico com entidades, aliases e relacoes;
- APIs REST para catalogo, series, grafo e insights;
- dashboards base para exploracao do acervo;
- copilot analitico grounded em datasets, versoes e grafo.
- arquitetura principal da UI organizada em `Analysis`, `Entities`, `Datasets` e `Copilot`, com drill-down secundario para dataset, versao e entidade.

## Quem usa

- analistas de mercado e regulatorio;
- comercializadoras e consultorias;
- pesquisadores e energytechs;
- time interno de produto, estrategia e dados;
- futuros clientes enterprise que querem validar a ontologia antes de integrar dados privados.

## Valor entregue sem onboarding de cliente

- acesso rapido a dados curados e versionados;
- visao unificada de entidades e relacoes do setor;
- menos trabalho manual para reconciliar nomes, codigos e janelas temporais;
- resposta guiada por IA com citacoes de datasets e versoes;
- material demonstravel para vendas, parcerias e design partners.

## O que o MVP nao precisa

- SCADA, historian, ERP, OMS, CMMS ou GIS do cliente;
- upload manual de planilhas do cliente como fluxo principal;
- regras de health score por ativo privado;
- alertas operacionais baseados em sensor;
- workflows complexos de manutencao ou field service.

## Criterio de aceite do MVP

- pelo menos um conjunto prioritario de dados de ANEEL, ONS e CCEE esta catalogado e versionado;
- o usuario consegue navegar `Analysis`, `Entities`, `Datasets` e `Copilot`, com detalhes secundarios para dataset, versao e entidade;
- o Energy Graph publico responde consultas de vizinhanca e contexto;
- o copilot analitico responde perguntas grounded em datasets e metadados;
- a documentacao deixa claro que a fase enterprise e posterior e reutiliza essa base.
