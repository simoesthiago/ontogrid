# User Stories - OntoGrid Energy Data Hub MVP

## Personas prioritarias

### Julia - Analista de mercado e regulatorio

Quer consultar datasets publicos sem montar pipeline proprio.

### Caio - Consultor ou pesquisador

Quer navegar entidades canonicas e cruzar informacao entre varias fontes.

### Marina - Operadora de dados do produto

Quer saber o que esta catalogado, o que ja tem adapter e o que ja foi publicado no ambiente.

## IA principal do app

O app tem **5 paginas top-level**:

1. `Analysis`
2. `Entities`
3. `Datasets`
4. `Copilot`
5. `Settings`

`Settings` continua prevista, mas ainda nao e parte implementada do fluxo core.

## Must have do MVP publico

| ID | Story | Tela principal | Endpoint principal | Entidade |
|---|---|---|---|---|
| US-001 | Como analista, quero ver os 345 datasets catalogados para entender o que o hub cobre hoje | Datasets | `GET /api/v1/datasets` e `GET /api/v1/catalog/coverage` | `dataset` |
| US-002 | Como analista, quero abrir um dataset e ver versoes, cobertura e status para confiar no dado consultado | Datasets / detalhe secundario | `GET /api/v1/datasets/{dataset_id}` e `GET /api/v1/datasets/{dataset_id}/versions` | `dataset`, `dataset_version` |
| US-003 | Como analista, quero escolher um dataset e receber tabelas e graficos estruturados para analise | Analysis | `GET /api/v1/analysis/datasets/{dataset_id}/fields` e `POST /api/v1/analysis/query` | `metric_series`, `observation` |
| US-004 | Como consultor, quero navegar entidades canonicas cross-dataset e abrir o perfil consolidado de uma instancia | Entities / detalhe secundario | `GET /api/v1/entities` e `GET /api/v1/entities/{entity_id}/profile` | `entity`, `relation` |
| US-005 | Como usuario, quero usar o copilot sobre datasets e entidades publicadas e receber resposta grounded | Copilot | `POST /api/v1/copilot/query` | `dataset_version`, `entity` |
| US-006 | Como operadora de dados, quero acompanhar cobertura do repo vs cobertura do ambiente para saber o que falta implementar e publicar | Datasets / operacao interna | `GET /api/v1/catalog/coverage` e `docs/datasets/catalog_status.json` | `dataset`, `refresh_job` |
| US-007 | Como operadora de dados, quero disparar refresh controlado de um dataset com adapter para manter o catalogo publicado atualizado | Operacao interna | `POST /api/v1/admin/datasets/{dataset_id}/refresh` | `dataset_version` |

## Regras de leitura do produto

- `Entities` e o eixo canonico de navegacao do produto.
- Grafo continua como capacidade de backend e enriquecimento do perfil de entidade.
- O catalogo inclui datasets apenas catalogados e datasets ja ingeridos.
- `publicado` depende do ambiente; nao e metrica estatica do git.

## Criterios de aceite resumidos

### US-001 e US-002

- o catalogo mostra o universo dos 345 datasets;
- a UI diferencia `catalogado`, `adapter_pronto` e `publicado`;
- o detalhe do dataset mostra descricao, cobertura, frequencia e versoes.

### US-003

- `Analysis` opera sobre a camada curada do backend;
- o frontend nao carrega arquivo bruto;
- a resposta identifica dataset e versao quando houver dado publicado.

### US-004

- entidades podem ser buscadas por nome, tipo e codigo;
- o perfil consolida aliases, facetas, series e vizinhanca quando disponivel;
- a pagina nao e descrita como browser de ontologia geral.

### US-005

- o copilot responde apenas com grounding em dados e metadados conhecidos;
- a resposta cita fontes, datasets, versoes e, quando aplicavel, entidades;
- perguntas fora do escopo recebem resposta limitada e explicita.

### US-006 e US-007

- o repo tem manifest oficial do catalogo;
- o endpoint de coverage deixa claro o estado operacional do ambiente;
- refresh so roda para datasets com adapter e nao corrompe a ultima versao valida.
