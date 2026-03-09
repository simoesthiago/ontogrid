# Arquitetura de Camadas

- Status: oficial para a arquitetura conceitual do produto
- Escopo: relacao entre plataforma, MVP publico e fase enterprise

## Camadas do produto

| Camada | Papel | Entra no MVP publico | Fica mais forte na fase enterprise |
|---|---|---|---|
| A. Data ingress | pulls agendados, downloads, crawlers e contratos de dados | sim | sim |
| B. Ontologia e Energy Graph | entidades canonicas, aliases e relacoes setoriais | sim | sim |
| C. Curadoria e lineage | versionamento, qualidade e rastreabilidade | sim | sim |
| D. APIs e visualizacao | catalogo, series, dashboards e insights | sim | sim |
| E. Copilot analitico | perguntas, explicacoes e resumos grounded | sim | sim |
| F. Enterprise Data Plane | tenancy, conectores privados e federacao | nao | sim |
| G. Apps operacionais | vigilancia, reliability, copilots de workflow | nao | sim |

## Leitura da arquitetura

O MVP atual cobre as camadas A a E com foco em dados publicos. Isso significa que a primeira entrega relevante do produto ja inclui ontologia e IA, mas dentro de um dominio controlado e demonstravel sem dependencia de cliente.

## Mapeamento para o repositorio

- `docs/contracts/API_SPEC.md` descreve os contratos do hub publico.
- `docs/platform/DATA_MODEL.md` define o nucleo canonico e a extensao enterprise futura.
- `docs/platform/ARCHITECTURE.md` detalha a arquitetura tecnica do build atual.
- `docs/strategy/PORTFOLIO_E_ROADMAP.md` mostra como novas suites consomem essas camadas.

## O que muda quando a fase enterprise comecar

- `tenant_id` passa a organizar os dados privados e os acessos enterprise.
- entram conectores privados para SCADA, ERP, OMS, CMMS e GIS.
- o Energy Graph passa a combinar grafo publico com contexto privado do cliente.
- apps como Vigilancia Operacional de Ativos deixam de ser apenas tese e viram modulo operacional.

## Regra pratica

Sempre que houver duvida de escopo, assumir o seguinte:

- dados publicos primeiro;
- ontologia e visualizacao desde o inicio;
- IA somente grounded;
- federacao e apps operacionais depois.
