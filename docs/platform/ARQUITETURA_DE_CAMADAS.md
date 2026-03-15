# Arquitetura de Camadas

- Status: oficial para a arquitetura conceitual do produto
- Escopo: relacao entre catalogo, camada curada, entidades e fase enterprise

## Camadas do produto

| Camada | Papel | Entra no MVP publico | Observacao |
|---|---|---|---|
| A. Inventario e catalogo | Conhecer os 345 datasets do repo | sim | Catalogo completo desde o inicio |
| B. Ingestao e artifacts | Baixar e guardar arquivos originais | sim | Seletiva por ambiente |
| C. Curadoria e lineage | Versionar, rastrear e publicar a camada curada | sim | `dataset_version` pode ter varios artifacts |
| D. Entidades canonicas | Resolver aliases, relacoes e perfis | sim | `Entities` e o eixo de produto |
| E. APIs e visualizacao | `Analysis`, `Datasets`, `Copilot`, detalhes secundarios e `Settings` | sim | Frontend nunca consome bruto |
| F. Grafo de suporte | Vizinhanca e contexto relacional | sim | Infra do eixo `Entities`, nao pagina principal |
| G. Enterprise Data Plane | Tenancy e dados privados | nao | Fase posterior |

## Regra pratica

Quando houver duvida de escopo, assumir o seguinte:

- dados publicos primeiro;
- catalogo completo, ingestao seletiva;
- `Entities` como experiencia principal de identidade setorial;
- grafo como mecanismo de bastidor;
- IA somente grounded;
- federacao e apps operacionais depois.
