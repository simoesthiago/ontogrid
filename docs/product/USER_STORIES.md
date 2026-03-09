# User Stories - OntoGrid Energy Data Hub MVP

## 1. Personas prioritarias

### Julia - Analista de mercado e regulatorio

Quer consultar dados publicos harmonizados sem montar pipelines proprios.

### Caio - Consultor ou pesquisador

Quer navegar entidades, relacoes e series historicas em uma unica camada semantica.

### Marina - Operadora de dados do produto

Quer acompanhar refresh, versoes e qualidade dos datasets publicos.

## 2. Must Have do MVP publico

| ID | Story | Tela principal | Endpoint principal | Entidade |
|---|---|---|---|---|
| US-001 | Como analista, quero listar fontes e datasets para entender o que o hub cobre | Catalogo | `GET /api/v1/sources` e `GET /api/v1/datasets` | `source`, `dataset` |
| US-002 | Como analista, quero abrir um dataset e ver suas versoes para confiar no dado consultado | Detalhe do dataset | `GET /api/v1/datasets/{dataset_id}` e `GET /api/v1/datasets/{dataset_id}/versions` | `dataset`, `dataset_version` |
| US-003 | Como analista, quero consultar series e observacoes historicas para analisar tendencia e comparacao | Serie | `GET /api/v1/series` e `GET /api/v1/series/{series_id}/observations` | `metric_series`, `observation` |
| US-004 | Como consultor, quero explorar entidades e vizinhanca no Energy Graph para entender contexto setorial | Entidade / Grafo | `GET /api/v1/graph/entities` e `GET /api/v1/graph/entities/{entity_id}/neighbors` | `entity`, `relation` |
| US-005 | Como usuario, quero ver insights prontos para UI para acelerar leitura de contexto e mudancas recentes | Overview | `GET /api/v1/insights/overview` e `GET /api/v1/insights/entities/{entity_id}` | `insight_snapshot` |
| US-006 | Como usuario, quero perguntar ao copilot sobre dados publicos e receber resposta grounded | Copilot | `POST /api/v1/copilot/query` | `dataset_version`, `entity` |
| US-007 | Como operadora de dados, quero disparar refresh controlado de um dataset para manter o catalogo atualizado | Operacao interna | `POST /api/v1/admin/datasets/{dataset_id}/refresh` | `dataset_version` |

## 3. Criterios de aceite resumidos

### US-001 e US-002

- catalogo filtra por fonte, dominio e busca textual;
- detalhe do dataset mostra descricao, cobertura, frequencia e versoes;
- cada versao expone data de extracao, publicacao e checksum.

### US-003

- series retornam com unidade e granularidade explicitas;
- observacoes aceitam recorte temporal;
- a resposta identifica a versao usada no resultado.

### US-004

- entidades podem ser buscadas por nome, tipo e codigo;
- vizinhanca devolve nos, relacoes e proveniencia minima;
- o grafo usa nomenclatura canonica consistente.

### US-005

- insights resumem metricas e mudancas recentes;
- cada insight referencia datasets ou entidades de origem;
- a UI consegue montar visoes sem precisar recomputar tudo no cliente.

### US-006

- o copilot responde apenas com grounding em dados e metadados conhecidos;
- a resposta cita fontes, datasets e versoes;
- perguntas fora do escopo recebem resposta limitada e explicita.

### US-007

- refresh cria um job rastreavel;
- falhas ficam registradas sem corromper a ultima versao valida;
- o catalogo reflete o estado do refresh.

## 4. Stories pos-MVP

- conta, favoritos e historico de consultas;
- expansao para EPE e outras fontes;
- Enterprise Data Plane tenant-scoped;
- Vigilancia Operacional de Ativos;
- Reliability / Outage Intelligence;
- Smart Alerting Copilot;
- Technical Issue Resolution Assistant;
- Field Ops Assistant.
