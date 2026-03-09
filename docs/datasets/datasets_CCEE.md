**MAPEAMENTO DAS BASES PÚBLICAS DA CCEE**

Inventário dos conjuntos de dados públicos do portal Dados Abertos

Relatório analítico com foco em cobertura temática, organização do portal e padrões de estrutura dos datasets

| **196**               | **11**           | **194**          | **2**             |
|-----------------------|------------------|------------------|-------------------|
| **Datasets públicos** | **Organizações** | **Recursos CSV** | **Recursos GZIP** |

| Escopo do levantamento                                                                                          |
|-----------------------------------------------------------------------------------------------------------------|
| Inventário dos 196 datasets públicos visíveis no portal no momento da consulta.                                 |
| Descrição por organização e por família temática, com destaque para o que cada bloco cobre.                     |
| Leitura estrutural baseada na navegação do catálogo CKAN e na inspeção de dicionários de dados representativos. |
| Ênfase em granularidade, chaves de negócio, recortes temporais, métricas e particionamento por recurso.         |

Data da consolidação: 09/03/2026

# **1. Resumo executivo**

O portal Dados Abertos da CCEE está organizado em 11 organizações temáticas. A maior concentração está no bloco Infomercado, que sozinho responde por 137 dos 196 datasets públicos. Os demais conjuntos cobrem contas setoriais, resposta da demanda, PLD, mecanismos de comercialização, segurança prudencial, desligamento e cadastro de agentes.

Do ponto de vista técnico, o padrão dominante é CKAN com recursos particionados por ano ou por blocos históricos. A maioria dos recursos é oferecida em CSV e possui dicionário de dados no nível do recurso. Os datasets mais volumosos aparecem compactados em GZIP, em especial tabelas horárias/granulares do Infomercado.

Em termos de modelagem, há forte repetição de alguns eixos: período de referência (meses, dias, horas e processamentos), dimensão geográfica/regulatória (submercado, UF, ambiente ACL/ACR), identificação de agentes e perfis (siglas, CNPJ, classes), identificação de contratos/usinas/parcela e métricas físico-financeiras (MWh, MWm, R\$, preços, encargos, fatores e saldos).

O catálogo é adequado para três tipos de uso: transparência regulatória e financeira; acompanhamento operacional do MCP e mecanismos associados; e análises setoriais de geração/consumo/contratos, especialmente quando combinadas séries temporais mensais com visões horárias.

# **2. Metodologia de leitura**

- A inventariação foi feita a partir das páginas de organizações e de listagem do portal, garantindo cobertura nominal dos 196 datasets públicos.

- A leitura estrutural foi aprofundada em amostras representativas de cada organização, inspecionando os dicionários de dados e os metadados dos recursos.

- Quando uma família tinha muitos datasets (caso de Infomercado), a análise foi feita por família temática, não por download exaustivo de todos os arquivos.

- Sempre que o portal apresentava versões históricas e anuais em recursos separados, o relatório registrou essa característica como padrão de particionamento.

# **3. Visão geral do portal**

| **Organização**                               | **Qtd.** | **Foco analítico**                                                                 |
|-----------------------------------------------|----------|------------------------------------------------------------------------------------|
| Infomercado                                   | 137      | MCP, geração, consumo, contratos, GF/MRE, reserva, varejista e sumários do mercado |
| Contas Setoriais                              | 13       | RGR, CDE e CCC: entradas, saídas, sub-rogação e CTG                                |
| Resposta da Demanda                           | 13       | Encargos, ofertas, atendimento de produto e sandbox disponibilidade                |
| Preço de Liquidação das Diferenças            | 8        | PLD horário, médias, PLD final, sombra e PLDX                                      |
| Mecanismo de Venda de Excedentes              | 5        | Resultados do MVE em vários níveis de agregação                                    |
| Conta Bandeiras                               | 4        | CCRBT, PRH e termos de repactuação                                                 |
| Custo Variável Unitário                       | 4        | CVU térmico conjuntural, revisado, estrutural e merchant                           |
| Mecanismo de Compensação de Sobras e Déficits | 4        | Preços, cessões e liquidação do MCSD                                               |
| Segurança de Mercado                          | 4        | Monitoramento prudencial, garantias e operação balanceada                          |
| Desligamento                                  | 3        | Saídas voluntárias, compulsórias e por descumprimento                              |
| Agentes de Mercado                            | 1        | Cadastro dos agentes associados                                                    |

| Padrões transversais observados                                                                                         |
|-------------------------------------------------------------------------------------------------------------------------|
| Particionamento frequente por ano: o dataset funciona como contêiner e os recursos anuais guardam a série.              |
| Chaves temporais recorrentes: MES_REFERENCIA, PROCESSAMENTO, DIA, HORA, PERIODO_COMERCIALIZACAO, MES_CAIXA.             |
| Chaves de negócio recorrentes: SIGLA_AGENTE, CNPJ, SUBMERCADO, USINA/PARCELA, LEILAO, PRODUTO, CEDENTE/CESSIONARIO.     |
| Métricas recorrentes: montantes em MWh e MWm, valores em R\$, preços, encargos, saldos, fatores, quantidade de ofertas. |
| Amostras mostraram Data API ativa e dicionário de dados no recurso para os principais conjuntos analisados.             |

# **4. Como os datasets são organizados tecnicamente**

O catálogo usa CKAN. Cada dataset tem página própria com descrição, organização, etiquetas, autor/mantenedor, frequência de atualização, referência de publicação e um conjunto de recursos associados. Em muitos casos, o dataset tem vários recursos anuais (por exemplo, 2025, 2026 e um bloco histórico anterior).

Nos recursos, o portal expõe dicionário de dados com nome da coluna, tipo, rótulo e descrição. Em alguns datasets o próprio nível do dataset já lista todos os campos; em outros, o detalhamento aparece somente na página do recurso.

Os recursos amostrados disponibilizam exportações em CSV/TSV/JSON/XML e a Data API do CKAN. Para consumo analítico, isso significa que o portal é adequado tanto para download de arquivos quanto para integração automatizada em pipelines.

O padrão dominante é tabular e relacional: dimensões de identificação e classificação combinadas com métricas físico-financeiras. Pouco ou nada no catálogo exige tratamento semiestruturado complexo.

# **5. Agentes de Mercado**

Cadastro público de agentes associados da CCEE, com foco em identificação, classe de atuação e situação regulatória/varejista.

Quantidade de datasets nesta organização: 1.

| **Dataset**            | **O que existe no conjunto**                                                                     |
|------------------------|--------------------------------------------------------------------------------------------------|
| LISTA_AGENTE_ASSOCIADO | Listagem dos agentes associados da CCEE e suas características e atuações no mercado de energia. |

**Estrutura típica observada**

- Granularidade observada: uma linha por agente e mês de referência.

- Chaves e dimensões típicas: CNPJ, MES_REFERENCIA, SIGLA_AGENTE, RAZAO_SOCIAL, CLASSE_AGENTE.

- Atributos regulatórios: SITUACAO_COMERCIALIZADOR, SITUACAO_VAREJISTA, CATEGORIA_AGENTE, INDICADOR_VAREJISTA, ESTADO.

- Formato e acesso: CSV anual com dicionário de dados no recurso e Data API ativa.

**Campos exemplares**

| **Campo de exemplo** | **Campo de exemplo** | **Campo de exemplo**     |
|----------------------|----------------------|--------------------------|
| CNPJ                 | MES_REFERENCIA       | SIGLA_AGENTE             |
| RAZAO_SOCIAL         | CLASSE_AGENTE        | SITUACAO_COMERCIALIZADOR |
| SITUACAO_VAREJISTA   | ESTADO               | CATEGORIA_AGENTE         |
| INDICADOR_VAREJISTA  |                      |                          |

## **Conta Bandeiras**

Conjuntos ligados à Conta Centralizadora de Recursos de Bandeiras Tarifárias (CCRBT) e à repactuação do risco hidrológico.

Quantidade de datasets nesta organização: 4.

| **Dataset**              | **O que existe no conjunto**                                                               |
|--------------------------|--------------------------------------------------------------------------------------------|
| PREMIO_RISCO_HIDROLOGICO | Valores de PRH para liquidação nas contas correntes dos agentes do mercado de curto prazo. |
| CREDITO_DEBITO_CCRBT     | Créditos e débitos da Conta Centralizadora dos Recursos de Bandeiras Tarifárias.           |
| INADIMPLENCIA_CCRBT      | Valores de inadimplência na liquidação de agentes com a CCRBT.                             |
| TERMO_REPACTUACAO_PRH    | Termos de repactuação do risco hidrológico para acompanhamento e transparência.            |

**Estrutura típica observada**

- Granularidade observada: linhas por agente/usina/termo e mês de liquidação ou competência.

- Dimensões recorrentes: perfil de agente, usina, termo de repactuação, mês de liquidação, mês de apuração.

- Métricas típicas: montante repactuado, prêmio unitário, prêmio total, créditos/débitos e inadimplência.

- Série histórica particionada por ano em múltiplos recursos CSV.

**Campos exemplares**

| **Campo de exemplo**        | **Campo de exemplo** | **Campo de exemplo**       |
|-----------------------------|----------------------|----------------------------|
| SIGLA_PERFIL_AGENTE         | USINA                | DESPACHO                   |
| TERMO_DE_REPACTUACAO        | MONTANTE_RRH         | PREMIO_UNITARIO_ATUALIZADO |
| PREMIO_DE_RISCO_HIDROLOGICO | CAIXA_MES_LIQUIDACAO | COMPETENCIA_MES_APURACAO   |

## **Contas Setoriais**

Dados financeiros das contas setoriais do setor elétrico - especialmente RGR, CDE e CCC -, com foco em entradas, saídas, sub-rogações e custo total de geração.

Quantidade de datasets nesta organização: 13.

| **Dataset**               | **O que existe no conjunto**                                                         |
|---------------------------|--------------------------------------------------------------------------------------|
| RGR_DEMONSTRATIVO_SAIDA   | Recursos financeiros movimentados na RGR por agente beneficiário, rubrica e mês.     |
| RGR_DEMONSTRATIVO_ENTRADA | Entradas financeiras da RGR por agente, rubrica e mês.                               |
| CDE_DEMONSTRATIVO_ENTRADA | Entradas financeiras da CDE por agente beneficiário, rubrica e mês.                  |
| CDE_DEMONSTRATIVO_SAIDA   | Saídas financeiras da CDE por agente beneficiário, rubrica e mês.                    |
| CCC_DEMONSTRATIVO_SAIDA   | Saídas financeiras da CCC por agente beneficiário, rubrica e mês.                    |
| CCC_DEMONSTRATIVO_ENTRADA | Entradas financeiras da CCC por agente beneficiário, rubrica e mês.                  |
| CCC_SR_REA                | Valores aprovados e reembolsados pela CCC em sub-rogação por resolução autorizativa. |
| CCC_SR_OP_COM             | Sub-rogação mensal de obras em operação comercial reembolsadas pela CCC.             |
| CCC_SR_OB_AND             | Sub-rogação mensal de obras em andamento reembolsadas pela CCC.                      |
| CCC_CTG_SIGFI             | Custo total de geração para usinas SIGFI reembolsadas pela CCC.                      |
| CCC_CTG_USINA_CCESI       | Custo total de geração de usinas provenientes de leilão do sistema isolado da CCC.   |
| CCC_CTG_USINA             | Custo total de geração por usina reembolsável pela CCC.                              |
| CCC_CTG_BENEFICIARIO      | Custo total de geração e reembolso mensal de CCC por beneficiário.                   |

**Estrutura típica observada**

- Predomina o desenho financeiro por mês de caixa, mês de competência, agente, rubrica e valor.

- As famílias RGR/CDE/CCC usam identificadores de agente (CNPJ, sigla, razão social), rubricas e bases legais.

- As famílias de CTG e sub-rogação adicionam recortes por beneficiário, usina, obra e situação operacional.

- Os datasets são mensais e favorecem auditoria de fluxo financeiro, compensações, pagamentos e saldos remanescentes.

**Campos exemplares**

| **Campo de exemplo** | **Campo de exemplo** | **Campo de exemplo** |
|----------------------|----------------------|----------------------|
| MES_CAIXA            | CNPJ                 | SIGLA_AGENTE         |
| RAZAO_SOCIAL         | MES_COMPETENCIA      | RUBRICA              |
| VALOR_DEVIDO         | VALOR_COMPENSADO     | VALOR_PAGO           |
| SALDO_REMANESCENTE   | STATUS               | BASE_LEGAL           |
| RUBRICA_COMPENSACAO  |                      |                      |

## **Custo Variável Unitário**

CVU de térmicas, com recortes conjuntural, conjuntural revisado, estrutural e usinas merchant.

Quantidade de datasets nesta organização: 4.

| **Dataset**                                  | **O que existe no conjunto**                                                              |
|----------------------------------------------|-------------------------------------------------------------------------------------------|
| CUSTO_VARIAVEL_UNITARIO_CONJUNTURAL_REVISADO | Custo do combustível e CVU conjuntural revisado por usina, combustível, leilão e produto. |
| CUSTO_VARIAVEL_UNITARIO_MERCHANT             | Dados de CVU das usinas Merchant.                                                         |
| CUSTO_VARIAVEL_UNITARIO_CONJUNTURAL          | Custo do combustível e CVU conjuntural por usina, combustível, leilão e produto.          |
| CUSTO_VARIAVEL_UNITARIO_ESTRUTURAL           | CVU estrutural por usina, combustível, leilão, produto e horizonte de análise.            |

**Estrutura típica observada**

- Granularidade: mês de referência x empreendimento/parcela x combustível x leilão x produto.

- Campos típicos: agente vendedor, CNPJ, empreendimento, tipo de combustível, leilão, produto, custo do combustível e CVU.

- Alguns conjuntos adicionam metadados operacionais do modelo/preço do ONS e datas de suprimento contratual.

- Série mensal, útil para análises de custo térmico, despacho e comparação entre produtos/leilões.

**Campos exemplares**

| **Campo de exemplo** | **Campo de exemplo** | **Campo de exemplo** |
|----------------------|----------------------|----------------------|
| MES_REFERENCIA       | AGENTE_VENDEDOR      | CNPJ_AGENTE_VENDEDOR |
| SIGLA_PARCELA        | TIPO_COMBUSTIVEL     | LEILAO               |
| PRODUTO              | CUSTO_COMBUSTIVEL    | CVU_CONJUNTURAL      |
| CODIGO_MODELO_PRECO  | INICIO_SUPRIMENTO    | TERMINO_SUPRIMENTO   |

## **Desligamento**

Boletins de desligamento de agentes da CCEE, cobrindo saídas voluntárias, compulsórias e por descumprimento.

Quantidade de datasets nesta organização: 3.

| **Dataset**                 | **O que existe no conjunto**                                                 |
|-----------------------------|------------------------------------------------------------------------------|
| DESLIGAMENTO_DESCUMPRIMENTO | Procedimentos de desligamento por descumprimento de obrigação instaurados.   |
| DESLIGAMENTO_VOLUNTARIO     | Histórico de agentes que se desligaram voluntariamente, com ou sem sucessão. |
| DESLIGAMENTO_COMPULSORIO    | Histórico de agentes desligados compulsoriamente da CCEE.                    |

**Estrutura típica observada**

- Granularidade: um evento de desligamento por agente.

- Dimensões principais: agente desligado, classe, sucessão, sucessor, data de desligamento e reunião do conselho.

- Datasets separam bem o motivo/processo: voluntário, compulsório e descumprimento.

- Útil para due diligence de contrapartes e histórico regulatório de participantes.

**Campos exemplares**

| **Campo de exemplo** | **Campo de exemplo** | **Campo de exemplo** |
|----------------------|----------------------|----------------------|
| AGENTE_DESLIGADO     | CNPJ_DESLIGADO       | CLASSE_DESLIGADO     |
| TIPO_SUCESSAO        | AGENTE_SUCESSOR      | CNPJ_SUCESSOR        |
| CLASSE_SUCESSOR      | DATA_DESLIGAMENTO    | REUNIAO_CAD          |
| TIPO_DESLIGAMENTO    |                      |                      |

## **Infomercado**

Infomercado é o núcleo analítico do portal e concentra, de longe, a maior parte da oferta pública. Os datasets cobrem o resultado da contabilização do mercado brasileiro de energia, com extensões para geração, consumo, contratos, garantias físicas, MRE, energia de reserva, sumários de liquidação, varejista, permissionárias, mecanismos associados e recortes tecnológicos por fonte.

Por volume e diversidade, a melhor forma de ler o Infomercado não é dataset a dataset isoladamente, mas por famílias temáticas. Ainda assim, o inventário nominal completo aparece no anexo deste relatório.

| **Família temática**                                          | **Qtd.** | **Leitura estrutural**                                                                                                |
|---------------------------------------------------------------|----------|-----------------------------------------------------------------------------------------------------------------------|
| Cadastros, perfis, consumo e geração operacional              | 21       | Tabelas de cadastro e granularidade horária/mensal por agente, perfil, submercado e período de comercialização.       |
| Recortes por fonte/tecnologia e ambiente de comercialização   | 23       | Visões consolidadas por tecnologia (biomassa, eólica, fotovoltaica, PCH/CGH, UHE) e ambiente ACL/ACR/PROINFA/leilões. |
| Energia incentivada                                           | 3        | Montantes, geração, desconto médio e garantia física associados à energia incentivada.                                |
| Contratos, montantes e sazonalização                          | 14       | Montantes contratuais modulados e sazonalizados por tipo de contrato, leilão, submercado e perfil/agente.             |
| Garantia física, MRE e risco hidrológico                      | 17       | Datasets de GF definida/sazonalizada, MRE, repasses, RRH e fatores de ajuste.                                         |
| Energia de reserva e CONER                                    | 12       | Liquidação, saldos, encargos, inadimplência, penalidades, cessões e receitas por leilão.                              |
| Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões | 19       | Blocos regulados com balanço energético, resultado mensal, custos, receitas e liquidação.                             |
| Liquidação, encargos, exposição e consolidações do MCP        | 23       | Sumários mensais, encargos, exposição financeira, perdas, penalidades e fatores financeiros.                          |
| Resultados e montantes de MCSD no Infomercado                 | 5        | Resultados de sobras e déficits, compensações, reduções, recebimentos e cessões entre agentes.                        |

| Padrão de estrutura observado no Infomercado                                                                                               |
|--------------------------------------------------------------------------------------------------------------------------------------------|
| Predomina granularidade mensal, mas há tabelas horárias muito volumosas; duas delas são publicadas em GZIP.                                |
| Campos estruturantes recorrentes: MES_REFERENCIA, PERIODO_COMERCIALIZACAO, SUBMERCADO, SIGLA/COD_PARCELA_USINA, SIGLA_AGENTE e CNPJ.       |
| Métricas recorrentes: geração, consumo, contratos, GF, MWh, MWm, R\$, encargos, preços, exposições, saldos e fatores de ajuste.            |
| Há coexistência de séries históricas de legado e novas versões - por exemplo GERACAO_UHE e GERACAO_UHE_V2; LISTA_PERFIL e LISTA_PERFIL_V1. |

### **Cadastros, perfis, consumo e geração operacional**

Tabelas de cadastro e granularidade horária/mensal por agente, perfil, submercado e período de comercialização.

| **Datasets da família**          | **Datasets da família**                 |
|----------------------------------|-----------------------------------------|
| CONSUMO_HORARIO_PERFIL_AGENTE    | GERACAO_HORARIA_USINA                   |
| VAREJISTA_CONSUMIDOR             | PARCELA_CARGA_CONSUMO                   |
| CONSUMO_RAMO_ATIVIDADE           | PARCELA_CONSUMO_RAMO_ATIVIDADE          |
| LISTA_PERFIL_V1                  | CONSUMO_MENSAL_PERFIL_AGENTE            |
| GERACAO_FONTE_DESPACHO           | CONSUMO_MENSAL_AMBIENTE_COMERCIALIZACAO |
| GERACAO_HORARIA_FONTE_SUBMERCADO | CONSUMO_CLASSE_AGENTE                   |
| GERACAO_HORARIA                  | AGENTE_QTD_CONTABILIZACAO               |
| GERACAO_SUBMERCADO               | LISTA_PERMISSIONARIA_NAO_AGENTE         |
| GERACAO_HORARIA_SUBMERCADO       | GERACAO_CONSOLIDADA                     |
| VAREJISTA_SUBCLASSE              | CONSUMO_HORARIO_SUBMERCADO              |
| LISTA_PERFIL                     |                                         |

### **Recortes por fonte/tecnologia e ambiente de comercialização**

Visões consolidadas por tecnologia (biomassa, eólica, fotovoltaica, PCH/CGH, UHE) e ambiente ACL/ACR/PROINFA/leilões.

| **Datasets da família**             | **Datasets da família**         |
|-------------------------------------|---------------------------------|
| BIOMASSA_GERACAO_ACR_ACL_MODALIDADE | BIOMASSA_SUBMERCADO_UF          |
| FOTOVOLTAICA_GERACAO_ACR_ACL        | BIOMASSA_ACL                    |
| BIOMASSA_GF_DEFINIDA                | EOLICA_GERACAO_ACR_ACL          |
| BIOMASSA_LEILAO                     | FOTOVOLTAICA_GF_DEFINIDA        |
| BIOMASSA_FONTE_GERACAO              | EOLICA_GF_DEFINIDA              |
| LEILAO_ACR_EOL                      | FOTOVOLTAICA_ACL                |
| PCH_CGH_GF_DEFINIDA                 | PCH_PROINFA                     |
| PCH_ACL                             | BIOMASSA_PROINFA                |
| LEILAO_ACR_PCH                      | FOTOVOLTAICA_LEILAO_ACR         |
| ACL_EOL                             | GERACAO_FONTE_SUB_ESTADO_MENSAL |
| GERACAO_FONTE_PRIMARIA              | GERACAO_UHE_V2                  |
| GERACAO_UHE                         |                                 |

### **Energia incentivada**

Montantes, geração, desconto médio e garantia física associados à energia incentivada.

| **Datasets da família**      | **Datasets da família**    |
|------------------------------|----------------------------|
| ENERGIA_INCENTIVADA_MENSAL   | ENERGIA_INCENTIVADA_CLASSE |
| ENERGIA_INCENTIVADA_GF_FONTE |                            |

### **Contratos, montantes e sazonalização**

Montantes contratuais modulados e sazonalizados por tipo de contrato, leilão, submercado e perfil/agente.

| **Datasets da família**                     | **Datasets da família**                      |
|---------------------------------------------|----------------------------------------------|
| PARCELA_USINA_MONTANTE_MENSAL               | CONTRATO_MONTANTE_PERIODO                    |
| CONTRATO_MONTANTE_MENSAL_CLASSE_VENDEDOR    | ENERGIA_DISTRIB_HORARIO_SUBMERCADO           |
| CONTRATO_MONTANTE_MENSAL_LEILAO             | CONTRATO_MONTANTE_COMPRA_VENDA_PERFIL_AGENTE |
| CONTRATO_MONTANTE_SUBMERCADO_ENTREGA_CCEARQ | CONTRATO_MONTANTE_CLASSE                     |
| CONTRATO_MONTANTE_SUBMERCADO_HORARIO        | CONTRATO_MONTANTE_MENSAL_TIPO                |
| CONTRATO_MONTANTE_MENSAL_CBR                | CONTRATO_MONTANTE_MOD_PROINFA_AGENTE         |
| SAZONALIZACAO_CONTRATO_CCEARQ               | SAZONALIZACAO_CCGF                           |

### **Garantia física, MRE e risco hidrológico**

Datasets de GF definida/sazonalizada, MRE, repasses, RRH e fatores de ajuste.

| **Datasets da família**                     | **Datasets da família**           |
|---------------------------------------------|-----------------------------------|
| GARANTIA_FISICA_FONTE                       | GARANTIA_FISICA_LASTRO            |
| MRE_GF_MODULADA_USINA                       | MRE_MENSAL                        |
| GARANTIA_FISICA_SAZO_MRE_SUBMERCADO         | GARANTIA_FISICA_SAZO_LASTRO       |
| REPASSE_RISCO_HIDROLOGICO                   | RRV_MENSAL                        |
| RRH_REPASSE                                 | GARANTIA_FISICA_SAZO_SUBMERCADO   |
| RRH_GERACAO_HORARIA                         | RRH_AGENTE                        |
| MRE_HORARIO                                 | RRH_GERACAO_SUBMERCADO_HORARIA    |
| SAZONALIZACAO_MRE_GF_MOTORIZACAO_SUBMERCADO | SAZONALIZACAO_MRE_GF_FATOR_AJUSTE |
| FATOR_AJUSTE_GF                             |                                   |

### **Energia de reserva e CONER**

Liquidação, saldos, encargos, inadimplência, penalidades, cessões e receitas por leilão.

| **Datasets da família**            | **Datasets da família**        |
|------------------------------------|--------------------------------|
| ENERGIA_RESERVA_LIQUIDACAO         | RESERVA_SALDO_CONER            |
| RESERVA_INADIMPLENCIA              | RESERVA_RECEITA_LEILAO_SOL     |
| ENERGIA_RESERVA_CONSUMO_REFERENCIA | RESERVA_RECEITA_LEILAO_PCH_CGH |
| ENERGIA_RESERVA_MENSAL_LEILAO      | RESERVA_CESSAO_BIO             |
| RESERVA_ENCARGO                    | RESERVA_RECEITA_BIO_PCH_LEILAO |
| RESERVA_RECEITA_EOL_LEILAO         | RESERVA_PENALIDADE             |

### **Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões**

Blocos regulados com balanço energético, resultado mensal, custos, receitas e liquidação.

| **Datasets da família**          | **Datasets da família**                 |
|----------------------------------|-----------------------------------------|
| USINA_COTISTA_CEG_DISTRIBUIDOR   | USINA_COTISTA_NUCLEAR                   |
| USINA_COTISTA_LIQUIDACAO_PARCELA | DISPONIBILIDADE_LEILAO_RECEITA          |
| CCEN_BALANCO_ENERGETICO_MENSAL   | CCEN_CUSTO_CAFT                         |
| ITAIPU_BALANCO_ENERGETICO_MENSAL | CCGF_CONT_SAZONALIZADO                  |
| ITAIPU_RESULTADO_MENSAL          | CCEAR_BALANCO_ENERGETICO_MENSAL         |
| PROINFA_USINA                    | RECEITA_VENDA_DISTRIBUIDOR_COTA_NUCLEAR |
| CCGF_RESULTADO_MENSAL            | DISPONIBILIDADE_LEILAO_GF_GERACAO       |
| CCEAR_RESULTADO_MENSAL           | CCEN_VALOR_LIQUIDAR                     |
| PROINFA_EOL                      | CCEN_RESULTADO_MENSAL                   |
| CCGF_BALANCO_ENERGETICO_MENSAL   |                                         |

### **Liquidação, encargos, exposição e consolidações do MCP**

Sumários mensais, encargos, exposição financeira, perdas, penalidades e fatores financeiros.

| **Datasets da família**                | **Datasets da família**                |
|----------------------------------------|----------------------------------------|
| ENCARGO_RECEBIDO_PERFIL_AGENTE_USINA   | ENCARGO_PGTO_MENSAL                    |
| ENCARGO_ESS_ANCILAR                    | SUMARIO_MENSAL_AJUSTE                  |
| ENCARGO_HORARIO_SUBMERCADO             | SUMARIO_DISTRIB_MENSAL                 |
| SUMARIO_BE_HORARIO_SUBMERCADO          | PENALIDADE_CLASSE_MENSAL               |
| ALIVIO_PENALIDADE_DISTRIB_MENSAL       | PERDA_RB_HORARIO                       |
| CONTABILIZACAO_MONTANTE_PERFIL_AGENTE  | SUMARIO_MENSAL_RESULTADO               |
| PLD_HORARIO_SUBMERCADO                 | SUMARIO_MENSAL_COMPRA_VENDA_SUBMERCADO |
| QTD_HORA_MES                           | ENCARGO_IMPORTACAO_GERACAO             |
| EXPOSICAO_FINANCEIRA_MENSAL            | PERDA_RB_MES                           |
| CONTABILIZACAO_FATOR_AJUSTE_FINANCEIRO | PENALIDADE_CONSUMO_HORARIO             |
| PENALIDADE_PRECO_MENSAL                | SUMARIO_MENSAL_LIQUIDACAO              |
| MONTANTE_MENSAL_MCP_AGENTE             |                                        |

### **Resultados e montantes de MCSD no Infomercado**

Resultados de sobras e déficits, compensações, reduções, recebimentos e cessões entre agentes.

| **Datasets da família**  | **Datasets da família**            |
|--------------------------|------------------------------------|
| MCSD_RESULTADO_MENSAL    | MCSD_MONTANTE_COMPENSADO_DEVOLVIDO |
| MCSD_MONTANTE_REDUZIDO   | MCSD_MONTANTE_RECEBIDO_LEILAO      |
| MCSD_CEDENTE_CESSIONARIO |                                    |

## **Mecanismo de Compensação de Sobras e Déficits**

Dados do MCSD sobre preços, compensações e apuração/liquidação de cessões de Energia Nova e Energia Existente.

Quantidade de datasets nesta organização: 4.

| **Dataset**                                      | **O que existe no conjunto**                                                                 |
|--------------------------------------------------|----------------------------------------------------------------------------------------------|
| MCSD_ENERGIA_NOVA_PRECO                          | Preços médios dos contratos que compõem o preço médio dos CCEAR C a liquidar.                |
| MCSD_ENERGIA_NOVA_APURACAO_LIQUIDACAO            | Compensação, valores totais a liquidar e demais dados de liquidação do MCSD de Energia Nova. |
| MCSD_ENERGIA_EXISTENTE_APURACAO_LIQUIDACAO_P1_P2 | Apuração da liquidação do MCSD Energia Existente P1 e P2.                                    |
| MCSD_ENERGIA_EXISTENTE_APURACAO_LIQUIDACAO_P3    | Apuração da liquidação do MCSD Energia Existente P3.                                         |

**Estrutura típica observada**

- Granularidade observada: mês de referência/mês de processamento x cedente x cessionário x produto.

- Medidas recorrentes: valor de ajuste, preço médio, total a liquidar, total de cessão e valor da cessão.

- Dimensões específicas do mecanismo: cedente, cessionário, produto MCSD, horas do mês e processamento.

- Histórico repartido entre bloco histórico e anos correntes em recursos distintos.

**Campos exemplares**

| **Campo de exemplo** | **Campo de exemplo** | **Campo de exemplo** |
|----------------------|----------------------|----------------------|
| MES_REFERENCIA       | MES_PROCESSAMENTO    | CEDENTE              |
| CESSIONARIO          | VALOR_AJUSTE         | HORA_MES             |
| PRECO_MEDIO          | TOTAL_LIQUIDAR       | TOTAL_CESSAO         |
| VALOR_CESSAO         | PRODUTO_MCSD         |                      |

## **Mecanismo de Venda de Excedentes**

Resultados do MVE em diferentes níveis de agregação: geral, por produto, por compra/venda, por par contratual e por aporte de garantia.

Quantidade de datasets nesta organização: 5.

| **Dataset**                    | **O que existe no conjunto**                                                           |
|--------------------------------|----------------------------------------------------------------------------------------|
| MVE_RESULTADO_COMPRA_VENDA     | Resumo de compra e venda do resultado da negociação efetivamente realizada no MVE.     |
| MVE_RESULTADO_PAR_CONTRATUAL   | Detalhamento do par contratual resultante da negociação efetivamente realizada no MVE. |
| MVE_RESULTADO_GERAL            | Resultado geral da operação efetivamente realizada no âmbito do MVE.                   |
| MVE_APORTE_GARANTIA_FINANCEIRA | Aporte de garantia de participação realizado pelo agente no MVE.                       |
| MVE_RESUMO_PRODUTO             | Resumo por produto do resultado da operação efetivamente realizada no MVE.             |

**Estrutura típica observada**

- Datasets organizados por processamento do mecanismo e vigência do produto.

- Dimensões típicas: tipo de energia, modalidade de preço, submercado, produto, comprador/vendedor/par contratual.

- Métricas típicas: quantidade de ofertas recebidas, montante ofertado, montante negociado em MWm, base anual e MWh.

- Publicação rápida após o processamento, com séries anuais e bloco histórico 2019-2024.

**Campos exemplares**

| **Campo de exemplo**             | **Campo de exemplo**     | **Campo de exemplo**              |
|----------------------------------|--------------------------|-----------------------------------|
| PROCESSAMENTO                    | VIGENCIA                 | TIPO_ENERGIA                      |
| MODALIDADE_PRECO                 | SUBMERCADO               | QUANTIDADE_OFERTA_RECEBIDA_COMPRA |
| QUANTIDADE_OFERTA_RECEBIDA_VENDA | MONTANTE_OFERTADO_COMPRA | MONTANTE_NEGOCIADO_MWM            |
| MONTANTE_NEGOCIADO_MWH           |                          |                                   |

## **Preço de Liquidação das Diferenças**

Conjuntos históricos do PLD em níveis horário, diário, semanal, mensal, final e sombra, incluindo PLDX anual.

Quantidade de datasets nesta organização: 8.

| **Dataset**         | **O que existe no conjunto**                                                     |
|---------------------|----------------------------------------------------------------------------------|
| PLD_HORARIO         | Valores históricos horários do PLD por submercado e período de referência.       |
| PLD_MEDIA_DIARIA    | Média diária do PLD por submercado e dia de referência.                          |
| PLD_MEDIA_SEMANAL   | Média semanal do PLD por submercado e semana de referência.                      |
| PLD_MEDIA_MENSAL    | Média mensal do PLD por submercado e mês de referência.                          |
| PLD_FINAL_MEDIO     | Média mensal do PLD Final por submercado para janelas regulatórias específicas.  |
| PLDX_VALOR_ANUAL    | Valores anuais do PLDX, associado ao custo de oportunidade de geração deslocada. |
| PLD_SOMBRA          | PLD sombra horário por submercado e tipo de metodologia sombra.                  |
| PLD_FINAL_HISTORICO | Histórico semanal do PLD Final por submercado.                                   |

**Estrutura típica observada**

- No PLD horário a chave típica é MES_REFERENCIA + DIA + HORA + SUBMERCADO + PERIODO_COMERCIALIZACAO.

- A família inteira é orientada a séries temporais e preços, sempre com forte presença da dimensão submercado.

- As métricas são valores de preço (R\$/MWh), agregados em granularidades diária, semanal, mensal e anual.

- O conjunto PLD_HORARIO combina um bloco histórico 2001-2020 e arquivos anuais desde 2021.

**Campos exemplares**

| **Campo de exemplo** | **Campo de exemplo** | **Campo de exemplo**    |
|----------------------|----------------------|-------------------------|
| MES_REFERENCIA       | SUBMERCADO           | PERIODO_COMERCIALIZACAO |
| DIA                  | HORA                 | PLD_HORA                |

## **Resposta da Demanda**

Dados da RD sobre encargos, atendimento de produto, despachos/ofertas e componentes sandbox do produto disponibilidade.

Quantidade de datasets nesta organização: 13.

| **Dataset**                               | **O que existe no conjunto**                                                                                  |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| RD_ATEND_PROD_CONTAB_MENSAL               | Sinalizadores mensais de atendimento do produto na contabilização.                                            |
| RD_ENCARGOS_CONTAB_HORARIO                | Encargo contabilizado da RD, discretizado por hora.                                                           |
| RD_ENCARGOS_CONTAB_MENSAL                 | Encargo contabilizado da RD, consolidado por mês e submercado.                                                |
| RD_ATEND_PROD_CONTAB_HORARIO              | Montantes ofertados e sinalizador de atendimento do produto, em base horária contabilizada.                   |
| RD_ATEND_PROD_PREVIO_HORARIO              | Montantes ofertados e sinalizador de atendimento do produto, em base horária prévia.                          |
| RD_ATEND_PROD_PREVIO_MENSAL               | Sinalizadores mensais de atendimento do produto em base prévia.                                               |
| RD_ENCARGOS_PREVIA_MENSAL                 | Encargo prévio da RD, consolidado por mês e submercado.                                                       |
| RD_ENCARGOS_PREVIA_HORARIO                | Encargo prévio da RD, discretizado por hora.                                                                  |
| RD_DISP_RECEITA_PENALIDADE_MENSAL_SANDBOX | Repasses e penalidades do produto Disponibilidade por perfil de agente, submercado e mês.                     |
| RD_DISP_ENCARGO_TOTAL_MENSAL_SANDBOX      | Encargo total mensal do produto Disponibilidade.                                                              |
| RD_DISP_ENCARGO_PERFIL_MENSAL_SANDBOX     | Encargo mensal do produto Disponibilidade por perfil de agente.                                               |
| RD_DISP_ENCARGO_HORARIO_SANDBOX           | Encargo horário do produto Disponibilidade por submercado e período de comercialização.                       |
| RD_DISP_DESPACHO_HORARIO_SANDBOX          | Despachos e ofertas do produto Disponibilidade por perfil de agente, submercado e período de comercialização. |

**Estrutura típica observada**

- Existem três blocos claros: dados contabilizados, dados prévios e datasets sandbox do produto Disponibilidade.

- O eixo temporal é mensal e horário; o eixo espacial/regulatório é submercado e período de comercialização.

- Os datasets alternam granularidade por submercado, por perfil de agente e por produto/oferta de redução.

- A família é bastante orientada a monitoramento operacional e repasse de encargos ESS.

**Campos exemplares**

| **Campo de exemplo**    | **Campo de exemplo** | **Campo de exemplo** |
|-------------------------|----------------------|----------------------|
| MES_REFERENCIA          | SUBMERCADO           | DATA                 |
| PERIODO_COMERCIALIZACAO | VALOR_ENCARGO_RD     |                      |

## **Segurança de Mercado**

Monitoramento prudencial e de garantias financeiras: fator de alavancagem, não aporte de garantia, operação balanceada e URL histórica do fator.

Quantidade de datasets nesta organização: 4.

| **Dataset**                    | **O que existe no conjunto**                                                      |
|--------------------------------|-----------------------------------------------------------------------------------|
| FATOR_ALAVANCAGEM              | Fator de alavancagem validado pelos agentes segundo a metodologia vigente.        |
| NAO_APORTE_GARANTIA_FINANCEIRA | Garantias financeiras calculadas, não aportadas e contratos ajustados por agente. |
| OPERACAO_BALANCEADA_PUBLICA    | Histórico de deliberações sobre operação balanceada e restrições operacionais.    |
| URL_FATOR_ALAVANCAGEM          | URL disponibilizada pelo agente para histórico do fator de alavancagem.           |

**Estrutura típica observada**

- Foco em eventos prudenciais e conformidade financeira do agente.

- O dataset de fator de alavancagem usa chaves de agente e evento (mês, código, tipo, categoria, versão de cálculo).

- Há dados de natureza cadastral (URL histórica) e dados de apuração/decisão (operação balanceada, não aporte).

- A família mostra maior variação de periodicidade: semanal/ordinária para fator de alavancagem e janelas mensais/regulatórias para outros itens.

**Campos exemplares**

| **Campo de exemplo**         | **Campo de exemplo**        | **Campo de exemplo** |
|------------------------------|-----------------------------|----------------------|
| SIGLA_AGENTE                 | NOME_RAZAO_SOCIAL           | CNPJ                 |
| NOME_CLASSE                  | MES_DO_EVENTO               | CODIGO_EVENTO        |
| DATA_INICIO_EVENTO           | TIPO_EVENTO                 | TIPO_CALCULO         |
| FATOR_ALAVANCAGEM            | FATOR_ALAVANCAGEM_INFORMADO | CATEGORIA_EVENTO     |
| DATA_ENVIO_FATOR_ALAVANCAGEM | VERSAO_CALCULO              |                      |

# **6. Avaliação crítica do catálogo público**

- Ponto forte principal: coerência temática por organização. Os blocos de PLD, RD, CVU, Segurança de Mercado, Contas Setoriais e MVE têm fronteiras de assunto muito claras, o que reduz ambiguidade para usuários externos.

- Ponto forte técnico: a combinação de descrição do dataset, recursos anuais, dicionário de dados e Data API permite consumo analítico relativamente maduro para um portal de dados regulatórios.

- Ponto forte analítico: o Infomercado oferece massa crítica suficiente para análises de mercado de curto prazo, exposição, contratos, geração, consumo, GF/MRE e mecanismos associados.

- Ponto de atenção: a documentação estrutural não é uniforme no mesmo nível. Em alguns conjuntos o campo aparece detalhado na página do dataset; em outros, só ao abrir a página do recurso.

- Ponto de atenção: há sinais de versionamento e convivência entre datasets de legado e sucessores. Isso é útil para preservar histórico, mas exige do analista uma curadoria cuidadosa para evitar sobreposição de séries.

- Ponto de atenção de metadados: os contadores de licença do portal não fecham exatamente com o total de datasets, indicando pelo menos um caso de metadado incompleto no catálogo.

# **7. Fontes e amostras usadas na leitura estrutural**

- Páginas de listagem do portal e páginas de organizações para inventário nominal dos 196 datasets.

- Páginas de datasets e recursos representativos: MVE_RESULTADO_GERAL, GERACAO_UHE_V2, PLD_HORARIO, RGR_DEMONSTRATIVO_SAIDA, RD_ENCARGOS_CONTAB_HORARIO, PREMIO_RISCO_HIDROLOGICO, CUSTO_VARIAVEL_UNITARIO_CONJUNTURAL, MCSD_ENERGIA_NOVA_APURACAO_LIQUIDACAO, FATOR_ALAVANCAGEM, DESLIGAMENTO_VOLUNTARIO e LISTA_AGENTE_ASSOCIADO.

- Dicionários de dados exibidos nas páginas dos recursos, com tipos e descrições de colunas.

- Metadados de frequência, data de atualização, autor/mantenedor e referência de publicação quando relevantes para qualificar o uso analítico.

# **Anexo A - Inventário completo dos 196 datasets**

Este anexo consolida, em forma de catálogo, todos os datasets públicos identificados no portal, com a organização de origem e um rótulo temático curto.

| **Organização**                               | **Dataset**                                      | **Tema / leitura resumida**                                                                                   |
|-----------------------------------------------|--------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Agentes de Mercado                            | LISTA_AGENTE_ASSOCIADO                           | Listagem dos agentes associados da CCEE e suas características e atuações no mercado de energia.              |
| Conta Bandeiras                               | PREMIO_RISCO_HIDROLOGICO                         | Valores de PRH para liquidação nas contas correntes dos agentes do mercado de curto prazo.                    |
| Conta Bandeiras                               | CREDITO_DEBITO_CCRBT                             | Créditos e débitos da Conta Centralizadora dos Recursos de Bandeiras Tarifárias.                              |
| Conta Bandeiras                               | INADIMPLENCIA_CCRBT                              | Valores de inadimplência na liquidação de agentes com a CCRBT.                                                |
| Conta Bandeiras                               | TERMO_REPACTUACAO_PRH                            | Termos de repactuação do risco hidrológico para acompanhamento e transparência.                               |
| Contas Setoriais                              | RGR_DEMONSTRATIVO_SAIDA                          | Recursos financeiros movimentados na RGR por agente beneficiário, rubrica e mês.                              |
| Contas Setoriais                              | RGR_DEMONSTRATIVO_ENTRADA                        | Entradas financeiras da RGR por agente, rubrica e mês.                                                        |
| Contas Setoriais                              | CDE_DEMONSTRATIVO_ENTRADA                        | Entradas financeiras da CDE por agente beneficiário, rubrica e mês.                                           |
| Contas Setoriais                              | CDE_DEMONSTRATIVO_SAIDA                          | Saídas financeiras da CDE por agente beneficiário, rubrica e mês.                                             |
| Contas Setoriais                              | CCC_DEMONSTRATIVO_SAIDA                          | Saídas financeiras da CCC por agente beneficiário, rubrica e mês.                                             |
| Contas Setoriais                              | CCC_DEMONSTRATIVO_ENTRADA                        | Entradas financeiras da CCC por agente beneficiário, rubrica e mês.                                           |
| Contas Setoriais                              | CCC_SR_REA                                       | Valores aprovados e reembolsados pela CCC em sub-rogação por resolução autorizativa.                          |
| Contas Setoriais                              | CCC_SR_OP_COM                                    | Sub-rogação mensal de obras em operação comercial reembolsadas pela CCC.                                      |
| Contas Setoriais                              | CCC_SR_OB_AND                                    | Sub-rogação mensal de obras em andamento reembolsadas pela CCC.                                               |
| Contas Setoriais                              | CCC_CTG_SIGFI                                    | Custo total de geração para usinas SIGFI reembolsadas pela CCC.                                               |
| Contas Setoriais                              | CCC_CTG_USINA_CCESI                              | Custo total de geração de usinas provenientes de leilão do sistema isolado da CCC.                            |
| Contas Setoriais                              | CCC_CTG_USINA                                    | Custo total de geração por usina reembolsável pela CCC.                                                       |
| Contas Setoriais                              | CCC_CTG_BENEFICIARIO                             | Custo total de geração e reembolso mensal de CCC por beneficiário.                                            |
| Custo Variável Unitário                       | CUSTO_VARIAVEL_UNITARIO_CONJUNTURAL_REVISADO     | Custo do combustível e CVU conjuntural revisado por usina, combustível, leilão e produto.                     |
| Custo Variável Unitário                       | CUSTO_VARIAVEL_UNITARIO_MERCHANT                 | Dados de CVU das usinas Merchant.                                                                             |
| Custo Variável Unitário                       | CUSTO_VARIAVEL_UNITARIO_CONJUNTURAL              | Custo do combustível e CVU conjuntural por usina, combustível, leilão e produto.                              |
| Custo Variável Unitário                       | CUSTO_VARIAVEL_UNITARIO_ESTRUTURAL               | CVU estrutural por usina, combustível, leilão, produto e horizonte de análise.                                |
| Desligamento                                  | DESLIGAMENTO_DESCUMPRIMENTO                      | Procedimentos de desligamento por descumprimento de obrigação instaurados.                                    |
| Desligamento                                  | DESLIGAMENTO_VOLUNTARIO                          | Histórico de agentes que se desligaram voluntariamente, com ou sem sucessão.                                  |
| Desligamento                                  | DESLIGAMENTO_COMPULSORIO                         | Histórico de agentes desligados compulsoriamente da CCEE.                                                     |
| Mecanismo de Compensação de Sobras e Déficits | MCSD_ENERGIA_NOVA_PRECO                          | Preços médios dos contratos que compõem o preço médio dos CCEAR C a liquidar.                                 |
| Mecanismo de Compensação de Sobras e Déficits | MCSD_ENERGIA_NOVA_APURACAO_LIQUIDACAO            | Compensação, valores totais a liquidar e demais dados de liquidação do MCSD de Energia Nova.                  |
| Mecanismo de Compensação de Sobras e Déficits | MCSD_ENERGIA_EXISTENTE_APURACAO_LIQUIDACAO_P1_P2 | Apuração da liquidação do MCSD Energia Existente P1 e P2.                                                     |
| Mecanismo de Compensação de Sobras e Déficits | MCSD_ENERGIA_EXISTENTE_APURACAO_LIQUIDACAO_P3    | Apuração da liquidação do MCSD Energia Existente P3.                                                          |
| Mecanismo de Venda de Excedentes              | MVE_RESULTADO_COMPRA_VENDA                       | Resumo de compra e venda do resultado da negociação efetivamente realizada no MVE.                            |
| Mecanismo de Venda de Excedentes              | MVE_RESULTADO_PAR_CONTRATUAL                     | Detalhamento do par contratual resultante da negociação efetivamente realizada no MVE.                        |
| Mecanismo de Venda de Excedentes              | MVE_RESULTADO_GERAL                              | Resultado geral da operação efetivamente realizada no âmbito do MVE.                                          |
| Mecanismo de Venda de Excedentes              | MVE_APORTE_GARANTIA_FINANCEIRA                   | Aporte de garantia de participação realizado pelo agente no MVE.                                              |
| Mecanismo de Venda de Excedentes              | MVE_RESUMO_PRODUTO                               | Resumo por produto do resultado da operação efetivamente realizada no MVE.                                    |
| Preço de Liquidação das Diferenças            | PLD_HORARIO                                      | Valores históricos horários do PLD por submercado e período de referência.                                    |
| Preço de Liquidação das Diferenças            | PLD_MEDIA_DIARIA                                 | Média diária do PLD por submercado e dia de referência.                                                       |
| Preço de Liquidação das Diferenças            | PLD_MEDIA_SEMANAL                                | Média semanal do PLD por submercado e semana de referência.                                                   |
| Preço de Liquidação das Diferenças            | PLD_MEDIA_MENSAL                                 | Média mensal do PLD por submercado e mês de referência.                                                       |
| Preço de Liquidação das Diferenças            | PLD_FINAL_MEDIO                                  | Média mensal do PLD Final por submercado para janelas regulatórias específicas.                               |
| Preço de Liquidação das Diferenças            | PLDX_VALOR_ANUAL                                 | Valores anuais do PLDX, associado ao custo de oportunidade de geração deslocada.                              |
| Preço de Liquidação das Diferenças            | PLD_SOMBRA                                       | PLD sombra horário por submercado e tipo de metodologia sombra.                                               |
| Preço de Liquidação das Diferenças            | PLD_FINAL_HISTORICO                              | Histórico semanal do PLD Final por submercado.                                                                |
| Resposta da Demanda                           | RD_ATEND_PROD_CONTAB_MENSAL                      | Sinalizadores mensais de atendimento do produto na contabilização.                                            |
| Resposta da Demanda                           | RD_ENCARGOS_CONTAB_HORARIO                       | Encargo contabilizado da RD, discretizado por hora.                                                           |
| Resposta da Demanda                           | RD_ENCARGOS_CONTAB_MENSAL                        | Encargo contabilizado da RD, consolidado por mês e submercado.                                                |
| Resposta da Demanda                           | RD_ATEND_PROD_CONTAB_HORARIO                     | Montantes ofertados e sinalizador de atendimento do produto, em base horária contabilizada.                   |
| Resposta da Demanda                           | RD_ATEND_PROD_PREVIO_HORARIO                     | Montantes ofertados e sinalizador de atendimento do produto, em base horária prévia.                          |
| Resposta da Demanda                           | RD_ATEND_PROD_PREVIO_MENSAL                      | Sinalizadores mensais de atendimento do produto em base prévia.                                               |
| Resposta da Demanda                           | RD_ENCARGOS_PREVIA_MENSAL                        | Encargo prévio da RD, consolidado por mês e submercado.                                                       |
| Resposta da Demanda                           | RD_ENCARGOS_PREVIA_HORARIO                       | Encargo prévio da RD, discretizado por hora.                                                                  |
| Resposta da Demanda                           | RD_DISP_RECEITA_PENALIDADE_MENSAL_SANDBOX        | Repasses e penalidades do produto Disponibilidade por perfil de agente, submercado e mês.                     |
| Resposta da Demanda                           | RD_DISP_ENCARGO_TOTAL_MENSAL_SANDBOX             | Encargo total mensal do produto Disponibilidade.                                                              |
| Resposta da Demanda                           | RD_DISP_ENCARGO_PERFIL_MENSAL_SANDBOX            | Encargo mensal do produto Disponibilidade por perfil de agente.                                               |
| Resposta da Demanda                           | RD_DISP_ENCARGO_HORARIO_SANDBOX                  | Encargo horário do produto Disponibilidade por submercado e período de comercialização.                       |
| Resposta da Demanda                           | RD_DISP_DESPACHO_HORARIO_SANDBOX                 | Despachos e ofertas do produto Disponibilidade por perfil de agente, submercado e período de comercialização. |
| Segurança de Mercado                          | FATOR_ALAVANCAGEM                                | Fator de alavancagem validado pelos agentes segundo a metodologia vigente.                                    |
| Segurança de Mercado                          | NAO_APORTE_GARANTIA_FINANCEIRA                   | Garantias financeiras calculadas, não aportadas e contratos ajustados por agente.                             |
| Segurança de Mercado                          | OPERACAO_BALANCEADA_PUBLICA                      | Histórico de deliberações sobre operação balanceada e restrições operacionais.                                |
| Segurança de Mercado                          | URL_FATOR_ALAVANCAGEM                            | URL disponibilizada pelo agente para histórico do fator de alavancagem.                                       |
| Infomercado                                   | USINA_COTISTA_CEG_DISTRIBUIDOR                   | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | USINA_COTISTA_NUCLEAR                            | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | USINA_COTISTA_LIQUIDACAO_PARCELA                 | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | ENCARGO_RECEBIDO_PERFIL_AGENTE_USINA             | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | ENCARGO_PGTO_MENSAL                              | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | ENCARGO_ESS_ANCILAR                              | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | ENERGIA_INCENTIVADA_MENSAL                       | Energia incentivada                                                                                           |
| Infomercado                                   | DISPONIBILIDADE_LEILAO_RECEITA                   | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CONSUMO_HORARIO_PERFIL_AGENTE                    | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | GERACAO_HORARIA_USINA                            | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | VAREJISTA_CONSUMIDOR                             | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | PARCELA_USINA_MONTANTE_MENSAL                    | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | ENERGIA_RESERVA_LIQUIDACAO                       | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | SUMARIO_MENSAL_AJUSTE                            | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | RESERVA_SALDO_CONER                              | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | PARCELA_CARGA_CONSUMO                            | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | CONSUMO_RAMO_ATIVIDADE                           | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | PARCELA_CONSUMO_RAMO_ATIVIDADE                   | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | CCEN_BALANCO_ENERGETICO_MENSAL                   | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | ENCARGO_HORARIO_SUBMERCADO                       | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | BIOMASSA_GERACAO_ACR_ACL_MODALIDADE              | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | RESERVA_INADIMPLENCIA                            | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | LISTA_PERFIL_V1                                  | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | GARANTIA_FISICA_FONTE                            | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | SUMARIO_DISTRIB_MENSAL                           | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | SUMARIO_BE_HORARIO_SUBMERCADO                    | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | BIOMASSA_SUBMERCADO_UF                           | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | CCEN_CUSTO_CAFT                                  | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CONTRATO_MONTANTE_PERIODO                        | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | CONTRATO_MONTANTE_MENSAL_CLASSE_VENDEDOR         | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | FOTOVOLTAICA_GERACAO_ACR_ACL                     | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | ENERGIA_INCENTIVADA_CLASSE                       | Energia incentivada                                                                                           |
| Infomercado                                   | PENALIDADE_CLASSE_MENSAL                         | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | ALIVIO_PENALIDADE_DISTRIB_MENSAL                 | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | BIOMASSA_ACL                                     | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | BIOMASSA_GF_DEFINIDA                             | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | CONSUMO_MENSAL_PERFIL_AGENTE                     | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | RESERVA_RECEITA_LEILAO_SOL                       | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | EOLICA_GERACAO_ACR_ACL                           | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | BIOMASSA_LEILAO                                  | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | GERACAO_FONTE_DESPACHO                           | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | ENERGIA_DISTRIB_HORARIO_SUBMERCADO               | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | CONTRATO_MONTANTE_MENSAL_LEILAO                  | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | ITAIPU_BALANCO_ENERGETICO_MENSAL                 | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | GARANTIA_FISICA_LASTRO                           | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | MRE_GF_MODULADA_USINA                            | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | PERDA_RB_HORARIO                                 | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | CONTRATO_MONTANTE_COMPRA_VENDA_PERFIL_AGENTE     | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | FOTOVOLTAICA_GF_DEFINIDA                         | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | CONTRATO_MONTANTE_SUBMERCADO_ENTREGA_CCEARQ      | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | ENERGIA_RESERVA_CONSUMO_REFERENCIA               | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | MRE_MENSAL                                       | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | CONTABILIZACAO_MONTANTE_PERFIL_AGENTE            | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | BIOMASSA_FONTE_GERACAO                           | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | EOLICA_GF_DEFINIDA                               | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | GARANTIA_FISICA_SAZO_MRE_SUBMERCADO              | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | LEILAO_ACR_EOL                                   | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | CONSUMO_MENSAL_AMBIENTE_COMERCIALIZACAO          | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | FOTOVOLTAICA_ACL                                 | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | PCH_CGH_GF_DEFINIDA                              | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | GERACAO_HORARIA_FONTE_SUBMERCADO                 | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | CCGF_CONT_SAZONALIZADO                           | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CONSUMO_CLASSE_AGENTE                            | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | GARANTIA_FISICA_SAZO_LASTRO                      | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | PCH_PROINFA                                      | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | GERACAO_HORARIA                                  | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | CONTRATO_MONTANTE_CLASSE                         | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | CONTRATO_MONTANTE_SUBMERCADO_HORARIO             | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | REPASSE_RISCO_HIDROLOGICO                        | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | ITAIPU_RESULTADO_MENSAL                          | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CCEAR_BALANCO_ENERGETICO_MENSAL                  | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | PCH_ACL                                          | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | AGENTE_QTD_CONTABILIZACAO                        | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | BIOMASSA_PROINFA                                 | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | GERACAO_SUBMERCADO                               | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | PROINFA_USINA                                    | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | SUMARIO_MENSAL_RESULTADO                         | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | RECEITA_VENDA_DISTRIBUIDOR_COTA_NUCLEAR          | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | LEILAO_ACR_PCH                                   | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | CONTRATO_MONTANTE_MENSAL_TIPO                    | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | PLD_HORARIO_SUBMERCADO                           | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | RRV_MENSAL                                       | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | LISTA_PERMISSIONARIA_NAO_AGENTE                  | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | GERACAO_HORARIA_SUBMERCADO                       | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | RESERVA_RECEITA_LEILAO_PCH_CGH                   | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | CCGF_RESULTADO_MENSAL                            | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | SUMARIO_MENSAL_COMPRA_VENDA_SUBMERCADO           | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | QTD_HORA_MES                                     | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | DISPONIBILIDADE_LEILAO_GF_GERACAO                | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CONTRATO_MONTANTE_MENSAL_CBR                     | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | ENCARGO_IMPORTACAO_GERACAO                       | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | EXPOSICAO_FINANCEIRA_MENSAL                      | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | RRH_REPASSE                                      | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | FOTOVOLTAICA_LEILAO_ACR                          | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | CCEAR_RESULTADO_MENSAL                           | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | GARANTIA_FISICA_SAZO_SUBMERCADO                  | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | GERACAO_CONSOLIDADA                              | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | PERDA_RB_MES                                     | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | CONTRATO_MONTANTE_MOD_PROINFA_AGENTE             | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | VAREJISTA_SUBCLASSE                              | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | RRH_GERACAO_HORARIA                              | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | RRH_AGENTE                                       | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | CCEN_VALOR_LIQUIDAR                              | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | ACL_EOL                                          | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | MRE_HORARIO                                      | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | RRH_GERACAO_SUBMERCADO_HORARIA                   | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | GERACAO_FONTE_SUB_ESTADO_MENSAL                  | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | PROINFA_EOL                                      | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CONSUMO_HORARIO_SUBMERCADO                       | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | MCSD_RESULTADO_MENSAL                            | Resultados e montantes de MCSD no Infomercado                                                                 |
| Infomercado                                   | CCEN_RESULTADO_MENSAL                            | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | CCGF_BALANCO_ENERGETICO_MENSAL                   | Cotas, contratos regulados, Itaipu, CCEN/CCGF/CCEAR e leilões                                                 |
| Infomercado                                   | GERACAO_FONTE_PRIMARIA                           | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | ENERGIA_RESERVA_MENSAL_LEILAO                    | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | CONTABILIZACAO_FATOR_AJUSTE_FINANCEIRO           | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | PENALIDADE_CONSUMO_HORARIO                       | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | PENALIDADE_PRECO_MENSAL                          | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | RESERVA_CESSAO_BIO                               | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | GERACAO_UHE_V2                                   | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | MCSD_MONTANTE_COMPENSADO_DEVOLVIDO               | Resultados e montantes de MCSD no Infomercado                                                                 |
| Infomercado                                   | MCSD_MONTANTE_REDUZIDO                           | Resultados e montantes de MCSD no Infomercado                                                                 |
| Infomercado                                   | RESERVA_ENCARGO                                  | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | SUMARIO_MENSAL_LIQUIDACAO                        | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | SAZONALIZACAO_MRE_GF_MOTORIZACAO_SUBMERCADO      | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | SAZONALIZACAO_CONTRATO_CCEARQ                    | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | SAZONALIZACAO_CCGF                               | Contratos, montantes e sazonalização                                                                          |
| Infomercado                                   | SAZONALIZACAO_MRE_GF_FATOR_AJUSTE                | Garantia física, MRE e risco hidrológico                                                                      |
| Infomercado                                   | ENERGIA_INCENTIVADA_GF_FONTE                     | Energia incentivada                                                                                           |
| Infomercado                                   | MCSD_MONTANTE_RECEBIDO_LEILAO                    | Resultados e montantes de MCSD no Infomercado                                                                 |
| Infomercado                                   | MCSD_CEDENTE_CESSIONARIO                         | Resultados e montantes de MCSD no Infomercado                                                                 |
| Infomercado                                   | RESERVA_RECEITA_BIO_PCH_LEILAO                   | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | RESERVA_RECEITA_EOL_LEILAO                       | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | LISTA_PERFIL                                     | Cadastros, perfis, consumo e geração operacional                                                              |
| Infomercado                                   | RESERVA_PENALIDADE                               | Energia de reserva e CONER                                                                                    |
| Infomercado                                   | MONTANTE_MENSAL_MCP_AGENTE                       | Liquidação, encargos, exposição e consolidações do MCP                                                        |
| Infomercado                                   | GERACAO_UHE                                      | Recortes por fonte/tecnologia e ambiente de comercialização                                                   |
| Infomercado                                   | FATOR_AJUSTE_GF                                  | Garantia física, MRE e risco hidrológico                                                                      |

# **Anexo B - Leituras estruturais por organização (resumo rápido)**

| **Organização**                               | **Granularidade dominante**            | **Chaves / métricas recorrentes**                                                                              |
|-----------------------------------------------|----------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Agentes de Mercado                            | mensal por agente                      | CNPJ, SIGLA_AGENTE, CLASSE_AGENTE, situação regulatória/varejista, estado                                      |
| Conta Bandeiras                               | mensal por agente/usina/termo          | perfil de agente, usina, termo de repactuação, montante RRH, prêmio unitário e prêmio total                    |
| Contas Setoriais                              | mensal financeiro por agente/rubrica   | mês caixa, mês competência, rubrica, valores devido/compensado/pago, saldo, status, base legal                 |
| Custo Variável Unitário                       | mensal por usina/leilão/produto        | agente, combustível, leilão, produto, custo do combustível, CVU                                                |
| Desligamento                                  | evento por agente                      | agente desligado, sucessão, sucessor, data, reunião do conselho, tipo de desligamento                          |
| Infomercado                                   | mensal e horário; amplo espectro       | MES_REFERENCIA, SUBMERCADO, PERIODO_COMERCIALIZACAO, agente/perfil, usina/parcela, MWh, MWm, R\$, GF, encargos |
| Mecanismo de Compensação de Sobras e Déficits | mensal por cedente/cessionário         | mês referência/processamento, produto, preço médio, cessão, total a liquidar, ajuste                           |
| Mecanismo de Venda de Excedentes              | processamento/vigência/produto         | tipo de energia, submercado, modalidade de preço, ofertas e montantes negociados                               |
| Preço de Liquidação das Diferenças            | horário a anual por submercado         | dia, hora, período de comercialização, PLD em R\$/MWh                                                          |
| Resposta da Demanda                           | horário e mensal por submercado/perfil | encargos, atendimento de produto, ofertas, despachos, sandbox disponibilidade                                  |
| Segurança de Mercado                          | evento prudencial por agente           | evento, categoria, versão de cálculo, fator de alavancagem, garantias e restrições operacionais                |
