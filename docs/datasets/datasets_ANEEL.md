| **ANEEL DADOS ABERTOS** |
|---|

Relatório de avaliação dos 69 conjuntos de dados públicos da ANEEL

Inventário analítico do catálogo, com foco em conteúdo, estrutura, granularidade, grupos oficiais e observações de uso.

| **69** | **1** | **13** | **7** |
|---|---|---|---|
| **Datasets públicos** | **Organização** | **Grupos oficiais** | **Famílias analíticas** |

| **Escopo** | 69 conjuntos de dados públicos visíveis no portal da ANEEL no momento da consulta. |
|---|---|
| **Base consultada** | Portal Dados Abertos da ANEEL (catálogo CKAN, página da organização, páginas de grupos, páginas de datasets e dicionários/metadados selecionados). |
| **Produto** | Relatório executivo-técnico com leitura do catálogo oficial, taxonomia analítica, padrões de modelagem e inventário completo por conjunto. |


Março de 2026


# 1. Resumo executivo

- O portal Dados Abertos da ANEEL informa **69 conjuntos de dados**, organizados sob **1 organização** e **13 grupos oficiais**. A organização única é a própria **Agência Nacional de Energia Elétrica**.

- Como os grupos do CKAN não são exclusivos, a leitura deste relatório separa duas camadas: os **13 grupos oficiais do portal** e **7 famílias analíticas** criadas para inventariar os 69 datasets uma única vez, sem duplicidade.

- O catálogo é especialmente forte em cinco frentes: **geração e expansão** (SIGA, RALIE, liberação comercial, outorgas), **distribuição e qualidade** (DEC/FEC, INDGER, BDGD, ouvidoria, reclamações), **tarifas e subsídios** (tarifas homologadas, componentes tarifárias, SAMP, SCS, CDE), **fiscalização e enforcement** (AI, TI, TN, TIPE, FSB) e **transparência institucional** (reuniões, consultas públicas, licitações, cadastro de agentes).

- Do ponto de vista estrutural, a ANEEL não publica um catálogo homogêneo de um único tipo. Há **bases tabulares simples**, **séries históricas particionadas por ano**, **pacotes multiarquivo/relacionais** e **bases geoespaciais**. SIGET, RALIE, INDGER e BDGD são os exemplos mais importantes dessa heterogeneidade.

- Em termos de uso analítico, o catálogo é adequado para: monitoramento regulatório e tarifário; acompanhamento da expansão da oferta e da rede; due diligence de fiscalização e sanções; estudos de qualidade da distribuição; e análises de programas setoriais como P&D, eficiência energética e benefícios tarifários.

- O portal preserva também um bloco relevante de **conjuntos descontinuados**, o que é positivo para séries históricas e comparações metodológicas, mas exige curadoria para não misturar datasets substituídos com seus sucessores correntes.


# 2. Critério de avaliação e leitura do catálogo

O relatório foi construído a partir do catálogo público da ANEEL, usando a página inicial do portal, a página da organização, a página de grupos, páginas individuais de datasets e dicionários/metadados representativos quando disponíveis.

A lógica de leitura seguiu quatro princípios:

- **Cobertura nominal completa dos 69 datasets**: todos os conjuntos públicos visíveis foram inventariados e classificados.
- **Separação entre organização oficial e leitura analítica**: como a ANEEL possui apenas uma organização e os grupos se sobrepõem, foi necessário criar famílias analíticas próprias para tornar o inventário utilizável.
- **Leitura estrutural por amostragem qualificada**: para os conjuntos mais densos, a caracterização foi ancorada nas descrições dos recursos, nos dicionários e nos padrões de particionamento exibidos no portal.
- **Ênfase em granularidade e função analítica**: quando um dicionário de campos explícito não estava visível no mesmo nível do dataset, a estrutura foi descrita pela sua granularidade dominante, chaves regulatórias prováveis, recortes temporais, formatos e papel analítico.

Importante: este relatório distingue **grupo oficial** de **família analítica**. Os grupos pertencem à taxonomia do portal; as famílias foram criadas aqui para permitir um inventário único e coerente.


# 3. Panorama do portal ANEEL

Em termos de desenho de catálogo, a ANEEL tem uma configuração distinta da observada na ONS e na CCEE: o portal possui **uma única organização** e distribui seus datasets em **grupos temáticos** que não funcionam como partição exclusiva. Por isso, a soma dos quantitativos por grupo supera o total de 69 conjuntos (os 13 grupos somam 74 associações dataset-grupo).

| **Métrica do catálogo** | **Leitura** |
|---|---|
| **Total informado no portal** | 69 conjuntos de dados. |
| **Organização oficial** | Agência Nacional de Energia Elétrica. |
| **Grupos oficiais** | 13 grupos temáticos publicados no CKAN. |
| **Leitura adotada neste relatório** | 69 datasets únicos inventariados por 7 famílias analíticas, preservando em seção própria os 13 grupos oficiais. |

## 3.1 Grupos publicados no portal

| **Grupo oficial publicado** | **Qtd.** | **Foco analítico** |
|---|---:|---|
| **Distribuição** | 18 | Qualidade do serviço, atendimento ao consumidor, ocorrências, indicadores operacionais e bases geográficas da rede de distribuição. |
| **Eficiência Energética** | 3 | Projetos do PEE e seus legados históricos de resultados, retornos, tipologias e investimentos. |
| **Fiscalização** | 10 | Autos, termos, segurança de barragens e séries históricas de atividades fiscalizatórias e sanções. |
| **Geração** | 12 | Cadastro do parque gerador, expansão, outorgas, liberação comercial, estatísticas e empreendimentos em estudo. |
| **Geração Distribuída** | 2 | MMGD conectada ao SCEE e acompanhamento de pedidos de conexão após a Lei 14.300. |
| **Informações Econômico-Financeiras** | 0 | Grupo oficial hoje vazio no portal, sem conjuntos associados. |
| **Leilões** | 1 | Resultado consolidado de leilões de geração e transmissão. |
| **Mercado** | 3 | Mercado de distribuição, balanço energético declarado e composição societária. |
| **Outros assuntos** | 5 | Governança, licitações, reuniões públicas, cadastro transversal e gestão de créditos. |
| **Participação Social** | 1 | Audiências, consultas e tomadas de subsídios abertas à sociedade. |
| **Pesquisa e Desenvolvimento** | 3 | Portfólio de P&D e legados regulatórios do programa. |
| **Tarifas** | 11 | Tarifas homologadas, componentes tarifárias, bandeiras, CDE, SCS, subsídios e bases de apoio. |
| **Transmissão** | 5 | Expansão da rede básica, BPR, desempenho de transmissoras e temas de infraestrutura. |


| **Padrões transversais observados** |
|---|
| Os grupos do CKAN não formam uma partição exclusiva dos datasets; um mesmo conjunto pode aparecer em mais de um grupo temático. |
| Há predominância de recursos tabulares em **CSV**, com **PDF** normalmente usado como dicionário de dados, manual ou documento de apoio. |
| **XML** e **JSON** aparecem em conjuntos mais estruturados, históricos ou legados; **ZIP** e **link externo** ganham importância em pacotes extensos e geoespaciais. |
| Chaves recorrentes no catálogo incluem concessionária/distribuidora, agente/CNPJ, CEG, usina/UG, conjunto elétrico, município, UF, termo/auto, data de competência e vigência regulatória. |
| Métricas recorrentes incluem MW, MWh, R$, indicadores de continuidade/qualidade, quantidades de beneficiários, reclamações, contribuições, compensações e penalidades. |


# 4. Padrões de estrutura observados no portal

Apesar da heterogeneidade temática, o catálogo da ANEEL apresenta alguns desenhos recorrentes que ajudam muito a antecipar a forma de integração analítica de cada conjunto.

| **Padrão** | **Significado prático** | **Exemplo no catálogo** |
|---|---|---|
| **PDF + CSV simples** | O PDF funciona como dicionário/manual e o CSV concentra o dado principal. | Ouvidoria, Reclamações, IASC, Subsídios Tarifários, Pautas e Atas. |
| **Série histórica particionada** | O dataset é um contêiner e os recursos são separados por ano, década ou competência. | SAMP, Ouvidoria, DEC/FEC, Beneficiários da CDE. |
| **Pacote multiarquivo / relacional** | Um mesmo conjunto traz várias tabelas com papéis diferentes, exigindo junção entre arquivos. | SIGET, RALIE, INDGER. |
| **Base geoespacial regulatória** | O dado principal não é apenas tabular; há estrutura geográfica ou arquivo técnico especializado. | BDGD. |
| **Legado descontinuado preservado** | O portal mantém bases antigas substituídas por conjuntos mais novos. | Tarifa Social – Beneficiários, autos/indicadores históricos de fiscalização, P&D e PEE legados. |

| **Tipo de modelagem** | **Como reconhecer** | **Consequência analítica** |
|---|---|---|
| **Cadastro regulatório** | Uma linha por ativo, empreendimento, agente ou registro administrativo, com pouca variação temporal. | Serve de dimensão mestre para enriquecer outras tabelas. |
| **Série temporal operacional/regulatória** | Há data/competência/vigência e medidas quantitativas recorrentes. | É o desenho dominante em tarifas, mercado, distribuição e estatísticas de geração. |
| **Evento ou processo administrativo** | Cada linha representa uma reunião, termo, auto, consulta ou ocorrência. | Adequado para trilhas de decisão, fiscalização e transparência processual. |
| **Geodado / infraestrutura** | O conjunto descreve rede, ativos físicos ou feições geográficas. | Exige ETL próprio, eventualmente com ferramentas SIG. |
| **Tabela legada de histórico** | O título ou a descrição já indicam substituição por um conjunto mais novo. | Deve ser consumida com cuidado para não sobrepor metodologias. |

# 5. Inventário completo dos 69 conjuntos de dados

A partir daqui, o relatório apresenta o inventário completo do catálogo organizado por **famílias analíticas**. Esta é a forma mais útil de ler a ANEEL porque preserva os grupos oficiais, mas evita repetição e sobreposição.

| **Família** | **Quantidade de conjuntos** |
|---|---:|
| **Transmissão, rede e ativos regulados** | 5 |
| **Geração, outorgas e expansão** | 15 |
| **Distribuição, qualidade e atendimento** | 15 |
| **Tarifas, mercado e subsídios** | 11 |
| **Fiscalização, sanções e compliance** | 10 |
| **Pesquisa, desenvolvimento e eficiência energética** | 6 |
| **Governança, cadastros e participação social** | 7 |

## 5.1 Transmissão, rede e ativos regulados

Família que concentra as bases ligadas à expansão, composição física e desempenho econômico-regulatório da transmissão. O núcleo é o SIGET, que funciona como um pacote multiarquivo para acompanhar contratos, módulos, obras, subestações, linhas e receitas associadas à expansão da rede básica.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **5** | Cadastros e fatos regulatórios por contrato/empreendimento/módulo, combinados com bases de preços de referência e indicadores de desempenho da transmissão. |

**Estrutura típica observada**

- Granularidade dominante: contrato, resolução, módulo, obra, linha, subestação ou concessionária, conforme o conjunto.
- Dimensões recorrentes: empreendimento, agente, contrato, arranjo de subestação, LT, vigência, RAP e instalações associadas.
- Métricas recorrentes: preços de referência, valores deduzidos de receita, atributos físicos e recortes de expansão da rede.
- Formato predominante: CSV + PDF, com o SIGET organizado como conjunto denso de tabelas temáticas pareadas com dicionários.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| Contrato/Resolução | Empreendimento/Módulo | Linha/Subestação |
| RAP/valor de referência | Concessionária/Vigência |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **Sistema de Gestão da Transmissão - SIGET** | Monitoramento da expansão da rede básica de transmissão e da gestão de receitas pós-reajuste; cobre contratos, empreendimentos, módulos, subestações, linhas, manobras e termos de liberação. | Conjunto multiarquivo. A página detalha várias tabelas temáticas em CSV, cada uma acompanhada de PDF de dicionário; há arquivos de contrato/resolução, módulos, reajuste RAP, novas instalações, obras concluídas e termos de liberação. |
| **GCEM - Gestão de Informações de Campos Eletromagnéticos** | Diretrizes e informações sobre campos elétricos e magnéticos associados a instalações do setor elétrico. | Estrutura simples, com PDF e CSV. |
| **BPR - Banco de Preços de Referência (linha de transmissão)** | Preços de referência para estudos de planejamento, autorização e licitação de linhas de transmissão. | PDF + CSV. |
| **BPR - Banco de Preços de Referência (subestação)** | Preços de referência para subestações em estudos, autorizações e licitações. | PDF + CSV. |
| **Desempenho das concessionárias de transmissão** | Valores deduzidos das receitas das concessionárias por indisponibilidade associada a desligamentos intempestivos. | PDF + CSV + XML + JSON. |

## 5.2 Geração, outorgas e expansão

Família que cobre o cadastro do parque gerador, o pipeline de expansão, atos de outorga, estatísticas consolidadas e recortes específicos de geração distribuída. É uma das partes mais estratégicas do catálogo porque conecta estoque instalado, projetos em implantação e novas liberações para operação comercial.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **15** | Mistura de cadastro mestre de ativos, monitoramento relacional da expansão, séries históricas anuais e recortes estatísticos por fonte, UF ou tipo de usina. |

**Estrutura típica observada**

- Granularidade dominante: empreendimento, usina, unidade geradora, ato/outorga, data de publicação, UF e fonte de geração.
- Chaves e dimensões recorrentes: CEG, número da UG, agente/CNPJ, fonte, situação do empreendimento, etapa da outorga e data de vigência/publicação.
- Métricas recorrentes: potência outorgada, instalada ou liberada, contagens de empreendimentos/usinas, previsões de operação e acréscimos anuais.
- Formatos observados: predomínio de CSV + PDF, com XML em conjuntos mais estruturados; MMGD pós-Lei 14.300 é publicada em pacotes ZIP regionais.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| CEG | Usina/UG | Agente/CNPJ |
| Fonte/UF | Potência/situação/vigência |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **SIGA - Sistema de Informações de Geração da ANEEL** | Cadastro operacional do parque gerador nacional em várias fases, da pré-outorga à revogação. | Dicionário em PDF + CSV/XML em duas cadências: arquivo mensal e arquivo diário. Estrutura centrada no empreendimento de geração. |
| **Relação de empreendimentos de Mini e Micro Geração Distribuída** | Conexões de micro e minigeração distribuída por unidades consumidoras no SCEE/MMGD. | PDF + CSV. |
| **RALIE – Relatório de Acompanhamento da Expansão da Oferta de Geração de Energia Elétrica** | Acompanhamento da implantação de usinas em construção ou parcialmente liberadas, com histórico desde 2021. | Modelo explicitamente relacional em 3 arquivos CSV (Usina, Unidade Geradora e Leilão), cada um com dicionário em PDF; chave principal baseada em CEG e data de publicação do RALIE. |
| **Liberação para operação comercial de empreendimentos de geração** | Capacidade instalada liberada para operação comercial. | PDF + CSV + XML; a descrição do portal indica que há dois arquivos de dados dentro do conjunto. |
| **Quantidade de empreendimentos de geração de energia em operação** | Contagem de empreendimentos de geração em operação. | PDF + CSV. |
| **Atos de Outorgas de Geração** | Documentos emitidos pela ANEEL para empreendimentos de geração a partir de 2015. | PDF + CSV. |
| **Agentes de Geração de Energia Elétrica** | Lista de agentes de geração relacionando usinas, CEG, CNPJ, participação societária e tipo de agente. | PDF + CSV. |
| **Empreendimento hidrelétrico em estudo** | Possíveis empreendimentos hidrelétricos e suas fases de pré-outorga. | PDF + CSV + XML. |
| **FSB - Fiscalização de Segurança de Barragens** | Fiscalização da conformidade de barragens/usinas hidrelétricas com a legislação aplicável. | PDF + CSV. |
| **Resultado de leilões de geração e transmissão de energia elétrica** | Resultados de leilões envolvendo geração e transmissão, com atributos como investimento, RAP, preço-teto e energia vendida. | PDF + CSV. |
| **Atendimento a pedidos de conexões MMGD - Mini e Microgeração distribuída - pós Lei 14300** | Atendimentos a solicitações de conexão de MMGD entre 07/01/2022 e 07/01/2023, para acompanhamento da aplicação da Lei nº 14.300/2022. | PDF de dicionário + pacotes ZIP regionais. |
| **Quantidade de usinas termelétricas por tipo** | Contagem de usinas termelétricas por tipo/fonte. | PDF + CSV. |
| **Capacidade Instalada por Unidade da Federação** | Capacidade instalada de geração por UF. | PDF + CSV. |
| **Acréscimo anual da potência instalada** | Aumento anual da potência instalada no parque gerador. | PDF + CSV. |
| **Compensação Financeira / Royalties** | Valores apurados de compensação financeira/royalties devidos a estados, municípios e outras entidades pela utilização de recursos hídricos. | PDF + CSV + XML + JSON. |

## 5.3 Distribuição, qualidade e atendimento

Família centrada na experiência do consumidor e no desempenho da distribuição: continuidade, tensão, qualidade comercial, atendimento, ocorrências, satisfação, planejamento da rede e base geográfica regulatória. É uma das áreas mais ricas do portal em granularidade operacional e recorte territorial.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **15** | Séries mensais/anuais por distribuidora, conjunto elétrico, município ou ocorrência, complementadas por bases modulares (INDGER) e por uma base geoespacial regulatória (BDGD). |

**Estrutura típica observada**

- Granularidade dominante: distribuidora + mês/ano, conjunto de unidades consumidoras, município, ocorrência emergencial/interrupção ou ativo de distribuição.
- Dimensões recorrentes: distribuidora, município, conjunto elétrico, alimentador, subestação, classe de atendimento, tipologia de reclamação e atributo técnico.
- Métricas recorrentes: DEC/FEC, compensações, reclamações, prazos, quantidades de ocorrências, inspeções, manutenções, satisfação e atributos da rede.
- Formatos observados: amplo predomínio de CSV + PDF; INDGER combina CSV/ZIP e BDGD adiciona Geodatabase (.gdb) por distribuidora via link externo.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| Distribuidora | Conjunto/Município | Ocorrência/Interrupção |
| DEC/FEC/compensação | Alimentador/Subestação |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **Ouvidoria Setorial ANEEL** | Solicitações registradas na ouvidoria setorial da ANEEL para mediação entre consumidor e distribuidora. | Série histórica anual em arquivos CSV por ano, acompanhada de PDF de dicionário. |
| **Reclamações no 1° e 2° nível da Distribuidora** | Quantidade de reclamações por tipologia, no 1º nível e na ouvidoria da distribuidora. | PDF + CSV. |
| **Indicadores Coletivos de Continuidade (DEC e FEC)** | Limites e valores apurados de DEC e FEC para continuidade do fornecimento. | PDF + CSV. |
| **INDGER - Indicadores Gerenciais da Distribuição** | Indicadores gerenciais das distribuidoras cobrindo dados comerciais, serviços comerciais, alimentadores, linhas de distribuição e subestações. | Conjunto modular: 5 sub-bases temáticas, cada uma com PDF de metadados/dicionário; os dados são publicados em CSV/ZIP com atualização mensal. |
| **Indicadores de Conformidade do Nível de Tensão em Regime Permanente** | Conformidade do nível de tensão exigido das distribuidoras em regime permanente. | PDF + CSV. |
| **Atendimento às Ocorrências Emergenciais** | Indicadores mensais de atendimento a ocorrências emergenciais por conjuntos de unidades consumidoras. | PDF + CSV. |
| **Segurança do Trabalho e das Instalações** | Indicadores de segurança do trabalho e das instalações das distribuidoras. | PDF + CSV. |
| **Indqual Inadimplência** | Dados de inadimplência para análise de aging list, quantidade de consumidores e faturas em atraso em relação à receita faturada. | PDF + CSV. |
| **Qualidade do Atendimento Comercial** | Cumprimento de prazos dos serviços previstos nas regras de prestação do serviço público de distribuição. | PDF + CSV. |
| **IndQual Município** | Base de ligação entre indicadores de qualidade da ANEEL e municípios. | PDF + CSV. |
| **Interrupções de Energia Elétrica nas Redes de Distribuição** | Todas as interrupções de energia nas redes de distribuição do país, excluindo áreas de permissionárias. | PDF + CSV. |
| **Ocorrências Emergenciais nas Redes de Distribuição** | Todas as ocorrências emergenciais nas redes de distribuição, excluídas áreas de permissionárias. | PDF + CSV. |
| **Índice ANEEL de Satisfação do Consumidor (IASC)** | Indicador de satisfação do consumidor residencial com o serviço das distribuidoras. | PDF + CSV. |
| **PDD - Plano de Desenvolvimento da Distribuição** | Planos das distribuidoras para expansão e modernização das redes de distribuição. | PDF + CSV. |
| **Base de Dados Geográfica da Distribuidora - BDGD** | Modelo geográfico regulatório simplificado do sistema de distribuição real, incluindo ativos, topologia e informações técnicas/comerciais de interesse. | Estrutura geoespacial: repositório de arquivos Geodatabase (.gdb) por distribuidora via link externo, manuais do PRODIST/BDGD e alguns extratos CSV/ZIP. Atualização anual. |

## 5.4 Tarifas, mercado e subsídios

Família que reúne o núcleo tarifário e econômico do portal: tarifas homologadas, componentes tarifárias, bandeiras, curvas de carga, mercado faturado/medido, subvenções, CDE e beneficiários. É a melhor entrada para análises de política tarifária, mercado de distribuição e benefícios setoriais.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **11** | Tabelas mensais ou anuais por distribuidora, vigência tarifária, subgrupo/modalidade, competência de faturamento e tipo de benefício ou programa social. |

**Estrutura típica observada**

- Granularidade dominante: distribuidora + ano/mês/competência, vigência regulatória, subgrupo tarifário, modalidade e tipo de benefício.
- Dimensões recorrentes: distribuidora/concessionária, classe/subgrupo, modalidade tarifária, resolução homologatória, mês de mercado, benefício/programa.
- Métricas recorrentes: TE, TUSD, componentes tarifárias, sinal de bandeira, volumes/mercado, DMR, quantidades de beneficiários e valores de custeio/subsídio.
- Formatos observados: CSV + PDF como padrão; XML aparece nas tarifas homologadas e ZIP ganha relevância em Beneficiários da CDE e pacotes mensais extensos.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| Distribuidora | TE/TUSD | Subgrupo/Modalidade |
| Competência/Vigência | Benefício/DMR/mercado |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **Tarifas de aplicação das distribuidoras de energia elétrica** | Valores homologados de TE e TUSD das distribuidoras. | PDF de dicionário + CSV + XML. Cobertura temporal informada: 2010 em diante; atualização semanal. |
| **Bandeiras Tarifárias** | Histórico e parâmetros do mecanismo de bandeiras tarifárias usado para sinalizar o custo conjuntural da geração. | Estrutura simples, com PDF e CSV. |
| **Componentes Tarifárias** | Componentes de TE e TUSD resultantes dos processos tarifários das distribuidoras. | PDF + CSV. |
| **CTR - Curva de Carga** | Curvas de demanda de consumidores-tipo e redes-tipo usadas em revisões tarifárias periódicas e na obtenção de custos marginais/tarifas de referência. | Dois pares de recursos: dicionário PDF + CSV para redes-tipo e dicionário PDF + CSV para consumidor-tipo. |
| **Subsídios Tarifários** | Histórico de descontos tarifários setoriais, exceto baixa renda, até mudanças trazidas pela Lei nº 12.783/2013. | PDF + CSV. |
| **Conta Desenvolvimento Energético (CDE) - Custeio dos Benefícios Tarifários** | Custeio dos benefícios tarifários suportados pela CDE. | PDF + CSV. |
| **SAMP - Sistema de Acompanhamento de Informações de Mercado para Regulação Econômica** | Informações de mercado declaradas por distribuidoras segundo a REN 1.003/2022. | Série anual em CSV por ano (2003 em diante), com granularidade mensal; inclui dicionário PDF. |
| **SCS - Sistema de Controle de Subvenções e Programas Sociais** | Relatórios mensais das distribuidoras para aprovação de Diferença Mensal de Receita referente a descontos na tarifa social e outros programas. | PDF + CSV. |
| **SAMP - Balanço** | Balanço energético com disponibilidades e requisitos do mercado de energia elétrica declarados pelas distribuidoras. | PDF + CSV. |
| **Beneficiários da Conta de Desenvolvimento Energético - CDE** | Beneficiários de descontos e repasses custeados pela CDE, conforme publicidade determinada pelo Decreto nº 9.022/2017. | Conjunto extenso: dicionário PDF, CSVs anuais e pacotes ZIP mensais por competência/segmento; a página mostra múltiplos recursos de rede básica e benefícios mensais. |
| **Tarifa Social de Energia Elétrica – Beneficiários (descontinuado)** | Histórico da quantidade de unidades consumidoras beneficiárias da tarifa social; substituído pelo conjunto de Beneficiários da CDE. | PDF + CSV + XML + JSON. |

## 5.5 Fiscalização, sanções e compliance

Família dedicada à atuação fiscalizatória da ANEEL: termos, autos, penas de edital, segurança de barragens, séries históricas de fiscalização e base relacionada à taxa setorial de fiscalização. É a camada mais útil para due diligence regulatória e acompanhamento de enforcement.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **10** | Eventos ou processos administrativo-fiscalizatórios por termo/auto/agente regulado, combinados com séries agregadas históricas e bases complementares de arrecadação ligada à fiscalização. |

**Estrutura típica observada**

- Granularidade dominante: um processo, termo, auto ou ocorrência fiscalizatória por agente, área responsável e data de lavratura.
- Dimensões recorrentes: agente regulado, tipo de penalidade, grupo infracional, termo de notificação, natureza da fiscalização e área da ANEEL.
- Métricas recorrentes: quantidades de ações, multas/penalidades, classificações do processo e estatísticas agregadas das atividades fiscalizatórias.
- Formatos observados: CSV + PDF como padrão; XML aparece nos conjuntos correntes de fiscalização e XML/JSON nos legados explicitamente descontinuados.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| Auto/Termo | Agente regulado | Penalidade/Grupo infracional |
| Área/Natureza da fiscalização | Data/status |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **TFSEE - Taxa de Fiscalização de Serviços de Energia Elétrica** | Dados da taxa setorial instituída pela Lei nº 9.427/1996 e regulamentada pelo Decreto nº 2.410/1997. | Estrutura simples, com PDF e CSV. |
| **Auto de Infração** | Autos de infração oriundos de ações de fiscalização da ANEEL e de agências conveniadas, com imposição de penalidades. | PDF + CSV + XML. |
| **Termos de Intimação das Penas dos Editais (TIPE)** | Termos de intimação usados para multas previstas em editais de leilões de transmissão e geração. | PDF + CSV. |
| **Termo de Intimação (TI)** | Termos de intimação decorrentes de fiscalização com imposição de penalidades. | PDF + CSV. |
| **Termo de Notificação** | Notificações resultantes de ações de fiscalização. | PDF + CSV + XML. |
| **Indicadores Quantitativos da Fiscalização (descontinuado)** | Série histórica de indicadores quantitativos de fiscalizações realizadas entre 1998 e 2016; o portal direciona os dados recentes para Termo de Notificação e Auto de Infração. | CSV + XML + JSON. |
| **Fiscalização da Transmissão e Distribuição (descontinuado)** | Histórico dos totais de fiscalizações de transmissão e distribuição; substituído, para dados recentes, por TN e AI. | PDF + CSV + XML + JSON. |
| **Fiscalização da Geração (descontinuado)** | Histórico dos totais de fiscalizações de geração (2012 a 2018); substituído, para dados recentes, por TN e AI. | PDF + CSV + XML + JSON. |
| **Fiscalização Econômica e Financeira (descontinuado)** | Histórico de fiscalizações econômico-financeiras; substituído, para dados recentes, por TN e AI. | PDF + CSV + XML + JSON. |
| **Autos de infração cadastrados pelas áreas de fiscalização (descontinuado)** | Histórico de quantidades e valores de autos de infração entre 1998 e 2017; substituído pelo conjunto Auto de Infração. | CSV + XML + JSON. |

## 5.6 Pesquisa, desenvolvimento e eficiência energética

Família que reúne os programas finalísticos de inovação e de eficiência energética do setor elétrico, somando bases correntes e legados descontinuados. É uma camada importante para estudos de portfólio tecnológico, resultados acumulados e histórico regulatório dos programas.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **6** | Cadastros de projetos e séries históricas anuais por ciclo, tema, tipologia ou indicador agregado de resultados. |

**Estrutura típica observada**

- Granularidade dominante: projeto, ciclo regulatório, tema estratégico ou tipologia de ação.
- Dimensões recorrentes: empresa/beneficiário, tema, uso final, ciclo, tipologia, programa (P&D ou PEE) e situação do projeto.
- Métricas recorrentes: investimento, quantidade de projetos, economias, demanda retirada de ponta, retornos e outros indicadores quantitativos.
- Formatos observados: conjuntos correntes em CSV + PDF; os legados descontinuados preservam também XML e JSON.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| Projeto/Ciclo | Empresa/beneficiário | Tema/Tipologia |
| Investimento | Economia/demanda retirada |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **Projetos de Eficiência Energética** | Projetos do Programa de Eficiência Energética voltados à promoção do uso eficiente da energia elétrica. | PDF + CSV. |
| **Projetos de P&D em Energia Elétrica** | Projetos do programa de P&D do setor elétrico, voltados a inovação e aplicabilidade. | PDF + CSV. |
| **Projetos Res n° 316/2008, 219/2006 e anteriores (descontinuado)** | Histórico de projetos de P&D por ciclos anuais entre 1999 e 2007. | PDF + CSV + XML + JSON. |
| **Projetos de P&D – temas estratégicos (descontinuado)** | Projetos de temas estratégicos publicados sob a REN nº 316/2008; substituído por Projetos de P&D em Energia Elétrica. | PDF + CSV + XML + JSON. |
| **Projetos, Retornos e Investimentos (descontinuado)** | Série histórica de indicadores quantitativos de projetos, demanda retirada de ponta, economias e investimentos; substituído por Projetos de Eficiência Energética. | PDF + CSV + XML + JSON. |
| **Projetos por tipologia (descontinuado)** | Quantidades acumuladas, demanda de ponta evitada, economias e investimentos por tipologia; substituído por Projetos de Eficiência Energética. | PDF + CSV + XML + JSON. |

## 5.7 Governança, cadastros e participação social

Família que agrega bases institucionais e transversais: reuniões públicas, pautas e atas, audiências e consultas, licitações e contratos, cadastro de agentes, composição societária e gestão de créditos. Embora menos “operacional” que geração ou distribuição, é uma área central para transparência decisória e cadastro setorial.

| **Conjuntos** | **Modelagem predominante** |
|---|---|
| **7** | Mistura de cadastros administrativos, registros de processos participativos e séries/eventos de governança institucional. |

**Estrutura típica observada**

- Granularidade dominante: reunião, pauta/ata, processo participativo, agente cadastrado, contrato/licitação ou registro administrativo.
- Dimensões recorrentes: data, tipo de reunião, processo, contribuinte, agente/CNPJ, contrato, natureza do crédito e vínculo societário.
- Métricas recorrentes: quantidades de reuniões, contribuições, exposições orais, registros contratuais e atributos cadastrais dos agentes.
- Formatos observados: predominância de CSV + PDF; Reuniões Públicas da Diretoria expõe também XML e JSON.

| **Entidades / chaves exemplares** | **Entidades / chaves exemplares** | **Entidades / chaves exemplares** |
|---|---|---|
| Processo/Reunião | Agente/CNPJ | Contribuições/participantes |
| Contrato/Licitação | Crédito/composição societária |  |

| **Dataset** | **O que existe** | **Estrutura predominante e observações** |
|---|---|---|
| **SIGEC - Sistema de Gestão de Créditos** | Gestão dos créditos arrecadados pela ANEEL, especialmente receitas vinculadas à atuação regulatória. | Estrutura simples, com PDF e CSV. |
| **Pautas e Atas das Reuniões Publicas da Diretoria** | Pautas e atas das reuniões públicas da Diretoria, usadas para comunicar e registrar deliberações. | PDF + CSV. |
| **SLC - Sistema de Licitações e Contratos** | Contratações realizadas pela ANEEL desde 2004, incluindo contratos, credenciamento e instrumentos correlatos. | PDF + CSV. |
| **Agentes do Setor Elétrico** | Cadastro oficial de pessoas físicas e jurídicas de interesse da ANEEL. | PDF + CSV. |
| **Reuniões Públicas da Diretoria** | Quantidade de reuniões ordinárias e extraordinárias por período. | PDF + CSV + XML + JSON. |
| **Composição Societária - Polímero** | Composição societária dos empreendimentos e agentes do setor elétrico declarada à ANEEL. | PDF + CSV. |
| **Audiências e Consultas Públicas** | Processos de audiência, consulta e tomada de subsídios usados na participação social da regulação. | PDF + CSV. |



# 6. Leitura crítica do catálogo e recomendações de uso

- **Ponto forte principal: cobertura regulatória ampla.** O catálogo não se limita a indicadores superficiais. Ele cobre ativos de geração, expansão, fiscalização, mercado, qualidade da distribuição, tarifas, subsídios, P&D, eficiência energética e transparência institucional.

- **Ponto forte de modelagem: coexistência de camadas analíticas complementares.** A ANEEL oferece tanto bases “estreitas” e simples (por exemplo, indicadores e cadastros) quanto conjuntos mais ricos e estruturados (SIGET, RALIE, INDGER e BDGD), o que permite montar arquiteturas de dados em diferentes níveis de sofisticação.

- **Ponto forte para auditoria e regulação: preservação dos legados.** A manutenção de conjuntos descontinuados facilita reconstituição histórica, comparação metodológica e análises longitudinais.

- **Ponto de atenção: heterogeneidade do desenho técnico.** Um pipeline que funcione para SAMP ou Ouvidoria não necessariamente servirá para BDGD, INDGER ou SIGET. O catálogo exige ETLs diferenciados por família.

- **Ponto de atenção: convivência entre bases correntes e substituídas.** Em fiscalização, P&D, eficiência energética e tarifa social, a presença de conjuntos descontinuados é útil, mas aumenta o risco de o analista misturar metodologias ou duplicar séries.

- **Ponto de atenção: grupos oficiais não resolvem sozinhos a navegação analítica.** Como a ANEEL possui uma única organização e grupos sobrepostos, a taxonomia do portal é boa para descoberta, mas insuficiente para governança analítica. Por isso, uma camada de catalogação interna por família é recomendável.

- **Recomendação de uso:** monte o repositório em quatro camadas: (1) cadastros e dimensões regulatórias, (2) fatos temporais mensais/anuais, (3) eventos e processos administrativos/fiscalizatórios, e (4) conjuntos especiais geoespaciais ou multiarquivo.

- **Recomendação de curadoria:** trate separadamente os conjuntos correntes e os descontinuados, e documente explicitamente qual fonte é “de produção” para cada tema (por exemplo, TN/AI no lugar dos históricos antigos; Beneficiários da CDE no lugar da antiga base de Tarifa Social).


# 7. Fontes consultadas

- Portal Dados Abertos da ANEEL – página inicial: https://dadosabertos.aneel.gov.br/
- Organização Agência Nacional de Energia Elétrica: https://dadosabertos.aneel.gov.br/organization/
- Página de grupos do portal: https://dadosabertos.aneel.gov.br/group/
- Catálogo geral de datasets: https://dadosabertos.aneel.gov.br/dataset/

Páginas e recursos representativos usados para leitura estrutural:

- Sistema de Gestão da Transmissão - SIGET: https://dadosabertos.aneel.gov.br/dataset/sistema-de-gestao-da-transmissao-siget
- SIGA - Sistema de Informações de Geração da ANEEL: https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel
- RALIE – Relatório de Acompanhamento da Expansão da Oferta de Geração de Energia Elétrica: https://dadosabertos.aneel.gov.br/dataset/ralie-relatorio-de-acompanhamento-da-expansao-da-oferta-de-geracao-de-energia-eletrica
- Base de Dados Geográfica da Distribuidora - BDGD: https://dadosabertos.aneel.gov.br/dataset/base-de-dados-geografica-da-distribuidora-bdgd
- INDGER - Indicadores Gerenciais da Distribuição: https://dadosabertos.aneel.gov.br/dataset/indger-indicadores-gerenciais-da-distribuicao
- Tarifas de aplicação das distribuidoras de energia elétrica: https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica
- SAMP: https://dadosabertos.aneel.gov.br/dataset/samp
- SAMP - Balanço: https://dadosabertos.aneel.gov.br/dataset/samp-balanco
- Indicadores Coletivos de Continuidade (DEC e FEC): https://dadosabertos.aneel.gov.br/dataset/indicadores-coletivos-de-continuidade-dec-e-fec
- Ouvidoria Setorial ANEEL: https://dadosabertos.aneel.gov.br/dataset/ouvidoria-setorial-aneel
- Auto de Infração: https://dadosabertos.aneel.gov.br/dataset/auto-de-infracao
- Termo de Notificação: https://dadosabertos.aneel.gov.br/dataset/termo-de-notificacao
- Projetos de P&D em Energia Elétrica: https://dadosabertos.aneel.gov.br/dataset/projetos-de-p-d-em-energia-eletrica
- Projetos de Eficiência Energética: https://dadosabertos.aneel.gov.br/dataset/projetos-de-eficiencia-energetica
- Audiências e Consultas Públicas: https://dadosabertos.aneel.gov.br/dataset/audiencias-e-consultas-publicas
- Reuniões Públicas da Diretoria: https://dadosabertos.aneel.gov.br/dataset/reunioes-publicas-da-diretoria

Nota metodológica: quando o portal exibia dicionário de dados ou descrição do recurso, a leitura estrutural foi feita no nível do recurso; quando o detalhamento estava restrito à descrição catalográfica do dataset, a caracterização foi feita pela granularidade, recorte temporal, formato, particionamento e papel analítico do conjunto.

# Anexo A - Inventário completo dos 69 datasets

Este anexo consolida todos os datasets públicos identificados no portal, com a família analítica atribuída neste relatório e um rótulo curto de leitura.

| **Família analítica** | **Dataset** | **Tema / leitura resumida** |
|---|---|---|
| Transmissão, rede e ativos regulados | **Sistema de Gestão da Transmissão - SIGET** | Monitoramento da expansão da rede básica de transmissão e da gestão de receitas pós-reajuste; cobre contratos, empreendimentos, módulos, subestações, linhas, manobras e termos de liberação. |
| Geração, outorgas e expansão | **SIGA - Sistema de Informações de Geração da ANEEL** | Cadastro operacional do parque gerador nacional em várias fases, da pré-outorga à revogação. |
| Distribuição, qualidade e atendimento | **Ouvidoria Setorial ANEEL** | Solicitações registradas na ouvidoria setorial da ANEEL para mediação entre consumidor e distribuidora. |
| Tarifas, mercado e subsídios | **Tarifas de aplicação das distribuidoras de energia elétrica** | Valores homologados de TE e TUSD das distribuidoras. |
| Fiscalização, sanções e compliance | **TFSEE - Taxa de Fiscalização de Serviços de Energia Elétrica** | Dados da taxa setorial instituída pela Lei nº 9.427/1996 e regulamentada pelo Decreto nº 2.410/1997. |
| Tarifas, mercado e subsídios | **Bandeiras Tarifárias** | Histórico e parâmetros do mecanismo de bandeiras tarifárias usado para sinalizar o custo conjuntural da geração. |
| Fiscalização, sanções e compliance | **Auto de Infração** | Autos de infração oriundos de ações de fiscalização da ANEEL e de agências conveniadas, com imposição de penalidades. |
| Fiscalização, sanções e compliance | **Termos de Intimação das Penas dos Editais (TIPE)** | Termos de intimação usados para multas previstas em editais de leilões de transmissão e geração. |
| Fiscalização, sanções e compliance | **Termo de Intimação (TI)** | Termos de intimação decorrentes de fiscalização com imposição de penalidades. |
| Fiscalização, sanções e compliance | **Termo de Notificação** | Notificações resultantes de ações de fiscalização. |
| Geração, outorgas e expansão | **Relação de empreendimentos de Mini e Micro Geração Distribuída** | Conexões de micro e minigeração distribuída por unidades consumidoras no SCEE/MMGD. |
| Tarifas, mercado e subsídios | **Componentes Tarifárias** | Componentes de TE e TUSD resultantes dos processos tarifários das distribuidoras. |
| Governança, cadastros e participação social | **SIGEC - Sistema de Gestão de Créditos** | Gestão dos créditos arrecadados pela ANEEL, especialmente receitas vinculadas à atuação regulatória. |
| Distribuição, qualidade e atendimento | **Reclamações no 1° e 2° nível da Distribuidora** | Quantidade de reclamações por tipologia, no 1º nível e na ouvidoria da distribuidora. |
| Governança, cadastros e participação social | **Pautas e Atas das Reuniões Publicas da Diretoria** | Pautas e atas das reuniões públicas da Diretoria, usadas para comunicar e registrar deliberações. |
| Geração, outorgas e expansão | **RALIE – Relatório de Acompanhamento da Expansão da Oferta de Geração de Energia Elétrica** | Acompanhamento da implantação de usinas em construção ou parcialmente liberadas, com histórico desde 2021. |
| Geração, outorgas e expansão | **Liberação para operação comercial de empreendimentos de geração** | Capacidade instalada liberada para operação comercial. |
| Distribuição, qualidade e atendimento | **Indicadores Coletivos de Continuidade (DEC e FEC)** | Limites e valores apurados de DEC e FEC para continuidade do fornecimento. |
| Distribuição, qualidade e atendimento | **INDGER - Indicadores Gerenciais da Distribuição** | Indicadores gerenciais das distribuidoras cobrindo dados comerciais, serviços comerciais, alimentadores, linhas de distribuição e subestações. |
| Distribuição, qualidade e atendimento | **Indicadores de Conformidade do Nível de Tensão em Regime Permanente** | Conformidade do nível de tensão exigido das distribuidoras em regime permanente. |
| Distribuição, qualidade e atendimento | **Atendimento às Ocorrências Emergenciais** | Indicadores mensais de atendimento a ocorrências emergenciais por conjuntos de unidades consumidoras. |
| Distribuição, qualidade e atendimento | **Segurança do Trabalho e das Instalações** | Indicadores de segurança do trabalho e das instalações das distribuidoras. |
| Distribuição, qualidade e atendimento | **Indqual Inadimplência** | Dados de inadimplência para análise de aging list, quantidade de consumidores e faturas em atraso em relação à receita faturada. |
| Distribuição, qualidade e atendimento | **Qualidade do Atendimento Comercial** | Cumprimento de prazos dos serviços previstos nas regras de prestação do serviço público de distribuição. |
| Distribuição, qualidade e atendimento | **IndQual Município** | Base de ligação entre indicadores de qualidade da ANEEL e municípios. |
| Geração, outorgas e expansão | **Quantidade de empreendimentos de geração de energia em operação** | Contagem de empreendimentos de geração em operação. |
| Tarifas, mercado e subsídios | **CTR - Curva de Carga** | Curvas de demanda de consumidores-tipo e redes-tipo usadas em revisões tarifárias periódicas e na obtenção de custos marginais/tarifas de referência. |
| Transmissão, rede e ativos regulados | **GCEM - Gestão de Informações de Campos Eletromagnéticos** | Diretrizes e informações sobre campos elétricos e magnéticos associados a instalações do setor elétrico. |
| Geração, outorgas e expansão | **Atos de Outorgas de Geração** | Documentos emitidos pela ANEEL para empreendimentos de geração a partir de 2015. |
| Geração, outorgas e expansão | **Agentes de Geração de Energia Elétrica** | Lista de agentes de geração relacionando usinas, CEG, CNPJ, participação societária e tipo de agente. |
| Governança, cadastros e participação social | **SLC - Sistema de Licitações e Contratos** | Contratações realizadas pela ANEEL desde 2004, incluindo contratos, credenciamento e instrumentos correlatos. |
| Transmissão, rede e ativos regulados | **BPR - Banco de Preços de Referência (linha de transmissão)** | Preços de referência para estudos de planejamento, autorização e licitação de linhas de transmissão. |
| Pesquisa, desenvolvimento e eficiência energética | **Projetos de Eficiência Energética** | Projetos do Programa de Eficiência Energética voltados à promoção do uso eficiente da energia elétrica. |
| Geração, outorgas e expansão | **Empreendimento hidrelétrico em estudo** | Possíveis empreendimentos hidrelétricos e suas fases de pré-outorga. |
| Geração, outorgas e expansão | **FSB - Fiscalização de Segurança de Barragens** | Fiscalização da conformidade de barragens/usinas hidrelétricas com a legislação aplicável. |
| Governança, cadastros e participação social | **Agentes do Setor Elétrico** | Cadastro oficial de pessoas físicas e jurídicas de interesse da ANEEL. |
| Transmissão, rede e ativos regulados | **BPR - Banco de Preços de Referência (subestação)** | Preços de referência para subestações em estudos, autorizações e licitações. |
| Governança, cadastros e participação social | **Reuniões Públicas da Diretoria** | Quantidade de reuniões ordinárias e extraordinárias por período. |
| Pesquisa, desenvolvimento e eficiência energética | **Projetos de P&D em Energia Elétrica** | Projetos do programa de P&D do setor elétrico, voltados a inovação e aplicabilidade. |
| Tarifas, mercado e subsídios | **Subsídios Tarifários** | Histórico de descontos tarifários setoriais, exceto baixa renda, até mudanças trazidas pela Lei nº 12.783/2013. |
| Tarifas, mercado e subsídios | **Conta Desenvolvimento Energético (CDE) - Custeio dos Benefícios Tarifários** | Custeio dos benefícios tarifários suportados pela CDE. |
| Geração, outorgas e expansão | **Resultado de leilões de geração e transmissão de energia elétrica** | Resultados de leilões envolvendo geração e transmissão, com atributos como investimento, RAP, preço-teto e energia vendida. |
| Tarifas, mercado e subsídios | **SAMP - Sistema de Acompanhamento de Informações de Mercado para Regulação Econômica** | Informações de mercado declaradas por distribuidoras segundo a REN 1.003/2022. |
| Distribuição, qualidade e atendimento | **Interrupções de Energia Elétrica nas Redes de Distribuição** | Todas as interrupções de energia nas redes de distribuição do país, excluindo áreas de permissionárias. |
| Tarifas, mercado e subsídios | **SCS - Sistema de Controle de Subvenções e Programas Sociais** | Relatórios mensais das distribuidoras para aprovação de Diferença Mensal de Receita referente a descontos na tarifa social e outros programas. |
| Distribuição, qualidade e atendimento | **Ocorrências Emergenciais nas Redes de Distribuição** | Todas as ocorrências emergenciais nas redes de distribuição, excluídas áreas de permissionárias. |
| Tarifas, mercado e subsídios | **SAMP - Balanço** | Balanço energético com disponibilidades e requisitos do mercado de energia elétrica declarados pelas distribuidoras. |
| Geração, outorgas e expansão | **Atendimento a pedidos de conexões MMGD - Mini e Microgeração distribuída - pós Lei 14300** | Atendimentos a solicitações de conexão de MMGD entre 07/01/2022 e 07/01/2023, para acompanhamento da aplicação da Lei nº 14.300/2022. |
| Distribuição, qualidade e atendimento | **Índice ANEEL de Satisfação do Consumidor (IASC)** | Indicador de satisfação do consumidor residencial com o serviço das distribuidoras. |
| Governança, cadastros e participação social | **Composição Societária - Polímero** | Composição societária dos empreendimentos e agentes do setor elétrico declarada à ANEEL. |
| Geração, outorgas e expansão | **Quantidade de usinas termelétricas por tipo** | Contagem de usinas termelétricas por tipo/fonte. |
| Geração, outorgas e expansão | **Capacidade Instalada por Unidade da Federação** | Capacidade instalada de geração por UF. |
| Geração, outorgas e expansão | **Acréscimo anual da potência instalada** | Aumento anual da potência instalada no parque gerador. |
| Governança, cadastros e participação social | **Audiências e Consultas Públicas** | Processos de audiência, consulta e tomada de subsídios usados na participação social da regulação. |
| Distribuição, qualidade e atendimento | **PDD - Plano de Desenvolvimento da Distribuição** | Planos das distribuidoras para expansão e modernização das redes de distribuição. |
| Distribuição, qualidade e atendimento | **Base de Dados Geográfica da Distribuidora - BDGD** | Modelo geográfico regulatório simplificado do sistema de distribuição real, incluindo ativos, topologia e informações técnicas/comerciais de interesse. |
| Tarifas, mercado e subsídios | **Beneficiários da Conta de Desenvolvimento Energético - CDE** | Beneficiários de descontos e repasses custeados pela CDE, conforme publicidade determinada pelo Decreto nº 9.022/2017. |
| Tarifas, mercado e subsídios | **Tarifa Social de Energia Elétrica – Beneficiários (descontinuado)** | Histórico da quantidade de unidades consumidoras beneficiárias da tarifa social; substituído pelo conjunto de Beneficiários da CDE. |
| Pesquisa, desenvolvimento e eficiência energética | **Projetos Res n° 316/2008, 219/2006 e anteriores (descontinuado)** | Histórico de projetos de P&D por ciclos anuais entre 1999 e 2007. |
| Fiscalização, sanções e compliance | **Indicadores Quantitativos da Fiscalização (descontinuado)** | Série histórica de indicadores quantitativos de fiscalizações realizadas entre 1998 e 2016; o portal direciona os dados recentes para Termo de Notificação e Auto de Infração. |
| Fiscalização, sanções e compliance | **Fiscalização da Transmissão e Distribuição (descontinuado)** | Histórico dos totais de fiscalizações de transmissão e distribuição; substituído, para dados recentes, por TN e AI. |
| Fiscalização, sanções e compliance | **Fiscalização da Geração (descontinuado)** | Histórico dos totais de fiscalizações de geração (2012 a 2018); substituído, para dados recentes, por TN e AI. |
| Fiscalização, sanções e compliance | **Fiscalização Econômica e Financeira (descontinuado)** | Histórico de fiscalizações econômico-financeiras; substituído, para dados recentes, por TN e AI. |
| Fiscalização, sanções e compliance | **Autos de infração cadastrados pelas áreas de fiscalização (descontinuado)** | Histórico de quantidades e valores de autos de infração entre 1998 e 2017; substituído pelo conjunto Auto de Infração. |
| Geração, outorgas e expansão | **Compensação Financeira / Royalties** | Valores apurados de compensação financeira/royalties devidos a estados, municípios e outras entidades pela utilização de recursos hídricos. |
| Pesquisa, desenvolvimento e eficiência energética | **Projetos de P&D – temas estratégicos (descontinuado)** | Projetos de temas estratégicos publicados sob a REN nº 316/2008; substituído por Projetos de P&D em Energia Elétrica. |
| Pesquisa, desenvolvimento e eficiência energética | **Projetos, Retornos e Investimentos (descontinuado)** | Série histórica de indicadores quantitativos de projetos, demanda retirada de ponta, economias e investimentos; substituído por Projetos de Eficiência Energética. |
| Pesquisa, desenvolvimento e eficiência energética | **Projetos por tipologia (descontinuado)** | Quantidades acumuladas, demanda de ponta evitada, economias e investimentos por tipologia; substituído por Projetos de Eficiência Energética. |
| Transmissão, rede e ativos regulados | **Desempenho das concessionárias de transmissão** | Valores deduzidos das receitas das concessionárias por indisponibilidade associada a desligamentos intempestivos. |


# Anexo B - Leituras estruturais por família (resumo rápido)

| **Família** | **Granularidade dominante** | **Chaves / métricas recorrentes** |
|---|---|---|
| **Transmissão, rede e ativos regulados** | contrato / empreendimento / módulo / ativo de transmissão | contrato, resolução, módulo, LT, subestação, RAP, preço de referência, desempenho da concessionária |
| **Geração, outorgas e expansão** | empreendimento / usina / UG / ato / data de publicação | CEG, UG, agente/CNPJ, fonte, potência, situação, previsão de operação, vigência |
| **Distribuição, qualidade e atendimento** | distribuidora / conjunto / município / ocorrência / mês | DEC, FEC, compensações, reclamações, ocorrências, prazos, ativos de rede, satisfação |
| **Tarifas, mercado e subsídios** | distribuidora / competência / vigência / subgrupo | TE, TUSD, componentes tarifárias, DMR, mercado, beneficiários, benefício, competência |
| **Fiscalização, sanções e compliance** | processo / auto / termo / agente / data | tipo de penalidade, grupo infracional, natureza da fiscalização, agente regulado, estatísticas históricas |
| **Pesquisa, desenvolvimento e eficiência energética** | projeto / ciclo / tema / tipologia | investimento, economia, demanda retirada, quantidade de projetos, tema, beneficiário |
| **Governança, cadastros e participação social** | reunião / processo participativo / cadastro / contrato | data, tipo de reunião, contribuições, exposições orais, agente/CNPJ, crédito, composição societária |
