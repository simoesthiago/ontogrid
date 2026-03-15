# Catalog Status - OntoGrid

- Status: fonte oficial legivel para humanos do catalogo do repo
- Manifest machine-readable correspondente: `docs/datasets/catalog_status.json`
- Regra: `publicado` e estado operacional do ambiente e deve ser lido via `/api/v1/catalog/coverage`, nao como snapshot estatico do git

## Resumo do repo

- Inventariados: **345**
- Catalogados: **345**
- Adapters prontos: **11**
- Pendentes de adapter: **334**

## Breakdown por fonte

| Fonte | Inventariados | Catalogados | Adapter pronto | Pendente de adapter |
|---|---:|---:|---:|---:|
| ANEEL | 69 | 69 | 4 | 65 |
| ONS | 80 | 80 | 3 | 77 |
| CCEE | 196 | 196 | 4 | 192 |

## Taxonomia oficial

- `inventariado`: apareceu no levantamento da fonte.
- `catalogado`: entrou no catalogo do app/repo.
- `adapter_pronto`: ja possui adapter implementado no repo.
- `publicado`: ja possui versao publicada em um ambiente operacional e deve ser lido via `/api/v1/catalog/coverage`.

## Datasets com adapter pronto no repo

| Fonte | Dataset code | Dataset | Familia |
|---|---|---|---|
| ANEEL | `agentes_geracao_aneel` | Agentes de geracao de energia eletrica | Geracao, outorgas e expansao |
| ANEEL | `indicadores_dec_fec` | Indicadores coletivos DEC e FEC | Distribuicao, qualidade e atendimento |
| ANEEL | `siga_geracao_aneel` | SIGA - cadastro de geracao | Geracao, outorgas e expansao |
| ANEEL | `tarifas_distribuicao` | Tarifas homologadas de distribuicao | Tarifas, mercado e subsidios |
| ONS | `carga_energia_diaria` | Carga de energia diaria | Carga, balanco e programacao |
| ONS | `carga_horaria_submercado` | Carga horaria por submercado | Carga, balanco e programacao |
| ONS | `geracao_usina_horaria` | Geracao por usina em base horaria | Geracao e usinas |
| CCEE | `agentes_mercado_ccee` | Agentes de mercado da CCEE | Agentes de Mercado |
| CCEE | `infomercado_geracao_horaria_usina` | Infomercado - geracao horaria por usina | Infomercado |
| CCEE | `pld_horario_submercado` | PLD horario por submercado | Preco de liquidacao das diferencas |
| CCEE | `pld_media_diaria` | PLD medio diario por submercado | Preco de liquidacao das diferencas |

## Regra de leitura

- Os **345 datasets** ja aparecem no catalogo do produto como universo mapeado do repo.
- Nem todo dataset catalogado possui ingestao implementada hoje.
- O runtime local deve operar com `catalog` ou `sample` por padrao; ingestao live pesada fica para uso explicito ou ambiente central.
- `publicado` varia por ambiente porque depende do banco e dos refresh jobs daquele runtime.

## Como regenerar

```powershell
python scripts/generate_catalog_status.py
```
